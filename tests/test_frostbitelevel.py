"""
Tests for reading a Frostbite level: bundles, meshes, partitions, placement.

Each reader is checked twice. Built files (`frostbite_fixtures`) pin the layout
the reader assumes, including the parts that went wrong while working it out:
chunk identifiers and locations are in different orders; a bundle entry can
continue the blob the last one named; a mesh's shadow section repeats its
surface and must not be drawn; a mirrored copy must be re-wound.

Then, where Battlefield 6 is installed, the same readers run on a shipped level
— the largest one, whichever that is — and are held to what the layout predicts
rather than to counts taken from one installation.
"""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import pytest

from heat3d_gamefiles.frostbite import (
    UnsupportedFrostbite,
    chunk_locations,
    read_header,
    read_sections,
)
from heat3d_gamefiles.frostbitebundle import (
    MANIFEST_MAGIC,
    read_manifest,
    toc_bundles,
)
from heat3d_gamefiles.frostbiteebx import read_partition
from heat3d_gamefiles.frostbitelevel import (
    MEMBER,
    MEMBER_MESH,
    MEMBER_SIZE,
    MEMBER_TRANSFORMS,
    TRANSFORM,
    _members,
    category,
    ebx_prefix,
    place,
)
from heat3d_gamefiles.frostbitemesh import decode_lod, read_meshset

from . import frostbite_fixtures as fx
from .installed import installed


class TestTable:
    def test_chunks_pair_with_their_own_locations_not_the_next_in_file(self):
        chunks = [(bytes([i]) * 16, fx.location(0x14FB60ED, i + 1, 100 * i, 10 + i)) for i in range(3)]
        data = fx.level_table(chunks, [])
        info = read_header(data)

        found = chunk_locations(data, info, read_sections(data, info))

        assert set(found) == {g for g, _ in chunks}
        for i, (guid, _) in enumerate(chunks):
            spot = found[guid]
            assert (spot.package, spot.cas, spot.offset, spot.size) == (0x14FB60ED, i + 1, 100 * i, 10 + i)

    def test_inline_bundles_continue_the_blob_last_named(self):
        blob = fx.bundle_blob([(0x663A3E8E, 13, 0, 5), (0x663A3E8E, 13, 5, 7), (0x14FB60ED, 2, 9, 3)])
        data = fx.level_table([(b"G" * 16, fx.location(1, 1, 0, 1))], [blob])

        (entries,) = toc_bundles(data)

        assert [(e.package, e.cas, e.offset, e.size) for e in entries] == [
            (0x663A3E8E, 13, 0, 5),
            (0x663A3E8E, 13, 5, 7),
            (0x14FB60ED, 2, 9, 3),
        ]


class TestManifest:
    def test_names_types_and_chunks_line_up_with_the_entries(self):
        raw = fx.manifest(
            [("level/layout", 64)],
            [("props/crate_mesh", 128, 0x49B156D4)],
            [b"K" * 16],
        )
        entries = [fx.location(1, 1, 10 * i, 4) for i in range(3)]
        from heat3d_gamefiles.frostbite import location_at

        spots = [location_at(e, 0) for e in entries]

        out = read_manifest(raw, spots)

        assert [e.name for e in out.ebx] == ["level/layout"]
        assert out.res[0].name == "props/crate_mesh" and out.res[0].type_name == "MeshSet"
        assert out.res[0].location.offset == 10
        assert out.chunks[0].id == b"K" * 16 and out.chunks[0].location.offset == 20

    def test_a_count_that_does_not_match_the_bundle_is_refused(self):
        raw = fx.manifest([("a", 1)], [], [])
        with pytest.raises(UnsupportedFrostbite, match="holds"):
            read_manifest(raw, [])

    def test_an_unknown_magic_is_refused(self):
        raw = bytearray(fx.manifest([("a", 1)], [], []))
        struct.pack_into(">I", raw, 4, MANIFEST_MAGIC ^ 1)
        with pytest.raises(UnsupportedFrostbite, match="magic"):
            read_manifest(bytes(raw), [None])


class TestMesh:
    positions = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
    faces = np.array([[0, 1, 2], [0, 2, 3]])

    def test_the_opaque_section_is_decoded_and_the_shadow_one_is_not(self):
        mesh = read_meshset(fx.meshset(len(self.faces), len(self.positions)))
        (lod,) = mesh.lods

        points, tri = decode_lod(lod, fx.buffers(self.positions, self.faces))

        assert lod.drawn == {0}
        assert lod.triangles == 2  # the shadow copy is not counted either
        assert np.allclose(points, self.positions)
        assert tri.tolist() == self.faces.tolist()

    def test_a_chunk_shorter_than_the_mesh_declares_is_refused(self):
        mesh = read_meshset(fx.meshset(2, 4))
        with pytest.raises(UnsupportedFrostbite, match="declares"):
            decode_lod(mesh.lods[0], b"\x00" * 16)

    def test_unknown_record_sizes_are_refused(self):
        raw = bytearray(fx.meshset(2, 4))
        struct.pack_into("<I", raw, 8, 400)
        with pytest.raises(UnsupportedFrostbite, match="record sizes"):
            read_meshset(bytes(raw))


def _group(transforms: np.ndarray) -> bytes:
    """A partition holding one group member that places `transforms`."""
    member_at = 64
    rows_at = member_at + MEMBER_SIZE + 16
    data = bytearray(rows_at + 64 * len(transforms))
    struct.pack_into("<H", data, 0, 0)
    struct.pack_into("<i", data, member_at + MEMBER_TRANSFORMS, rows_at - (member_at + MEMBER_TRANSFORMS))
    struct.pack_into("<q", data, member_at + MEMBER_MESH, (0 << 1) | 1)
    struct.pack_into("<I", data, rows_at - 4, len(transforms))
    data[rows_at:] = transforms.astype("<f4").tobytes()
    return fx.partition(
        types=[(b"I" * 16, 1), MEMBER, TRANSFORM],
        data=bytes(data),
        instances=[0],
        pointers=[member_at + MEMBER_TRANSFORMS, member_at + MEMBER_MESH],
        imports=[(b"M" * 16, b"i" * 16)],
        import_offsets=[member_at + MEMBER_MESH],
        arrays=[(member_at, 1, 1), (rows_at, len(transforms), 2)],
    )


class TestPlacement:
    def test_a_group_member_gives_its_mesh_and_transforms(self):
        rows = np.zeros((2, 4, 4), dtype=np.float32)
        rows[:, :3, :3] = np.eye(3)
        rows[0, 3, :3] = (10, 0, 5)
        rows[1, 3, :3] = (-3, 2, 1)
        partition = read_partition(_group(rows))

        ((index, found, variations),) = _members(partition, "group")

        assert partition.imports[index][0] == b"M" * 16
        assert np.allclose(found, rows)

    def test_a_point_lands_at_right_up_forward_plus_translation(self):
        rows = np.zeros((1, 4, 4), dtype=np.float32)
        rows[0, 0, :3] = (0, 0, -1)  # right
        rows[0, 1, :3] = (0, 1, 0)  # up
        rows[0, 2, :3] = (1, 0, 0)  # forward
        rows[0, 3, :3] = (100, 0, 0)

        world = place(np.array([[1.0, 2.0, 3.0]]), rows)

        assert np.allclose(world, [[103, 2, -1]])

    def test_categories_come_from_the_asset_path_and_terrain_materials(self):
        assert category("common/env/architecture/hangar_mesh", ["M_Wall"]) == "structure:buildings"
        assert category("level/generated/backdrop_mesh", ["M_TerrainBackdrop"]) == "ground:terrain backdrop"
        assert category("common/env/props/crate_mesh", ["M_Crate"]) == "structure:props"
        # A backdrop tile with a plain terrain material, and terrain that is not backdrop.
        assert category("lv/bd_x_terrainlv_04_far_mesh", ["M_X_TerrainLv_04_Far"]) == "ground:terrain backdrop"
        assert category("lv/rock_blend_mesh", ["M_RockTerrainBlend"]) == "ground:terrain blend"

    def test_the_partition_prefix_comes_from_the_table_path(self):
        toc = Path("X:/Game/Data/Win32/game/a/levels/lv/lv.toc")
        assert ebx_prefix(toc) == "game/a/levels/lv/"


# ---------------------------------------------------------------------------
# A shipped level, where one is installed.


def _largest_level() -> Path | None:
    tables = [
        p for p in installed("Battlefield*/**/levels/**/*.toc")
        if p.parent.name.lower() == p.stem.lower()
    ]
    return max(tables, key=lambda p: p.stat().st_size) if tables else None


LEVEL = _largest_level()
needs_level = pytest.mark.skipif(LEVEL is None, reason="no Frostbite level on this machine")


@pytest.fixture(scope="module")
def catalogue():
    from heat3d_gamefiles.frostbitebundle import LevelCatalogue

    return LevelCatalogue(LEVEL)


@needs_level
def test_a_shipped_level_names_its_content(catalogue):
    """Every bundle's manifest matched its entry count, or this would have raised."""
    assert catalogue.bundle_count > 0
    assert catalogue.ebx and catalogue.res and catalogue.chunks
    assert any(e.type_name == "MeshSet" for e in catalogue.res.values())


@needs_level
def test_shipped_meshes_decode_inside_their_own_bounds(catalogue):
    """
    Half floats round, so a vertex may sit a hair outside the declared box;
    a misread layout scatters them everywhere.
    """
    from heat3d_gamefiles.frostbitemesh import MESHSET

    meshes = [e for e in catalogue.res.values() if e.res_type == MESHSET]
    checked = 0
    for entry in meshes[:: max(1, len(meshes) // 40)]:
        mesh = read_meshset(catalogue.read(entry.location), entry.name)
        lod = mesh.lods[0]
        if lod.chunk == bytes(16) or lod.chunk not in catalogue.chunks:
            continue
        points, tri = decode_lod(lod, catalogue.chunk(lod.chunk), entry.name)
        if not len(points):
            continue
        slack = 0.01 * max(1.0, float(np.abs(mesh.high - mesh.low).max()))
        inside = ((points >= mesh.low - slack) & (points <= mesh.high + slack)).all(axis=1)
        assert inside.mean() > 0.95, entry.name
        assert tri.max() < len(points)
        checked += 1
    assert checked >= 10


@needs_level
def test_shipped_group_members_have_the_layout_this_reader_pins(catalogue):
    """Some partition of the level holds group members, and they read cleanly."""
    prefix = ebx_prefix(LEVEL)
    for name in sorted(n for n in catalogue.ebx if n.startswith(prefix)):
        raw = catalogue.read(catalogue.ebx[name].location)
        if MEMBER[0] not in raw:
            continue
        members = _members(read_partition(raw, name), name)
        if not members:
            continue
        rows = np.concatenate([r for _, r, _ in members])
        determinants = np.linalg.det(rows[:, :3, :3].astype(np.float64))
        assert np.isfinite(rows).all()
        assert (np.abs(np.abs(determinants) - 1) < 1e-3).mean() > 0.3
        return
    pytest.fail("no partition of the level holds a static model group member")


class TestTerrain:
    """
    A two-level terrain: a root with heights, and one child of four with its
    own. The child's quadrant must come from the child, the other three from
    the root, and a height page's border must not be drawn.
    """

    SAMPLES = 17  # 8 cells a side, a border of four, and the closing sample

    def build(self):
        from heat3d_gamefiles.frostbiteterrain import read_tree

        n = self.SAMPLES
        root = np.full((n, n), 1000, dtype="<u2")
        child = np.full((n, n), 3000, dtype="<u2")
        chunks = {b"R" * 16: root.tobytes(), b"C" * 16: child.tobytes()}
        res = fx.terrain_tree(
            n, 655.35, 160.0,
            (b"R" * 16, 1, [(b"C" * 16, 1, []), (b"x" * 16, 0, []), (b"y" * 16, 0, []), (b"z" * 16, 0, [])]),
        )
        return read_tree(res), chunks.__getitem__

    def test_the_quadtree_and_heightfield_parameters_are_read(self):
        tree, _ = self.build()
        assert (tree.samples, tree.stride, tree.square) == (17, 8, (-80.0, -80.0, 80.0, 80.0))
        assert len(tree.nodes) == 5
        assert set(tree.height_nodes()) == {(0, 0, 0), (1, 0, 0)}

    def test_the_finest_node_supplies_each_quadrant(self):
        from heat3d_gamefiles.frostbiteterrain import build_ground, sample_heights

        tree, read = self.build()
        ground = build_ground(tree, read, spacing=1.0)

        # 1000 and 3000 words of a 655.35 m range: 10 m and 30 m.
        heights = sample_heights(tree, read, np.array([-40.0, 40.0]), np.array([-40.0, 40.0]))
        assert np.allclose(heights, [30.0, 10.0])
        assert ground.positions[:, [0, 2]].min() == -80 and ground.positions[:, [0, 2]].max() == 80
        low = ground.positions[(ground.positions[:, 0] < -1) & (ground.positions[:, 2] < -1)]
        assert np.allclose(low[:, 1], 30.0)
        # Every triangle faces up.
        t = ground.positions[ground.faces]
        assert (np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])[:, 1] > 0).all()

    def test_a_tree_that_does_not_end_where_the_res_ends_is_refused(self):
        from heat3d_gamefiles.frostbiteterrain import read_tree

        res = fx.terrain_tree(17, 1.0, 16.0, (b"R" * 16, 1, []))
        with pytest.raises(UnsupportedFrostbite, match="quadtree"):
            read_tree(res + b"\x00")


class TestMaterials:
    def links(self):
        from heat3d_gamefiles.frostbitematerial import MaterialLinks, TextureInfo

        def info(name, fmt):
            return TextureInfo(name, 0, fmt, 64, 64, 1, b"", (4096,))

        names = {
            "t_shared_mossdetail_01_cs": 67,
            "t_ind_hut_01_trim_cs": 67,
            "t_concreteclean_01_cs": 67,
            "t_ind_hut_01_nmt": 66,
        }
        links = MaterialLinks()
        links.headers = {n: info(n, f) for n, f in names.items()}
        links.blocks[b"K" * 8] = list(names)
        links.blocks[b"D" * 8] = ["t_shared_mossdetail_01_cs", "t_ind_hut_01_nmt"]
        links.usage.update({"t_shared_mossdetail_01_cs": 900, "t_ind_hut_01_trim_cs": 3, "t_concreteclean_01_cs": 40})
        return links

    def test_the_material_s_words_pick_the_colour_map(self):
        links = self.links()
        assert links.colour_map("x/ind_hut_01_mesh", "M_ConcreteWall_01", b"K" * 8) == "t_concreteclean_01_cs"
        assert links.colour_map("x/ind_hut_01_mesh", "M_Trim", b"K" * 8) == "t_ind_hut_01_trim_cs"

    def test_a_decal_sheet_loses_to_the_surface_s_own_map(self):
        from heat3d_gamefiles.frostbitematerial import MaterialLinks, TextureInfo

        names = ["t_de_com_sign_01_ca", "t_com_sign_01_cs"]
        links = MaterialLinks()
        links.headers = {n: TextureInfo(n, 0, 67, 64, 64, 1, b"", (4096,)) for n in names}
        links.blocks[b"S" * 8] = names
        links.usage.update({"t_de_com_sign_01_ca": 1, "t_com_sign_01_cs": 5})
        # Both match the material and the mesh; the sheet is used less, and
        # used to win on that.
        assert links.colour_map("x/com_sign_01_mesh", "M_Sign", b"S" * 8) == "t_com_sign_01_cs"

    def test_distance_fields_and_palettes_are_never_the_colour(self):
        from heat3d_gamefiles.frostbitematerial import MaterialLinks, TextureInfo

        names = ["t_bd_vegetationtown_atlas_a_sdf", "bd_seu_buildingstown_palette", "t_com_oak_01_leaves_cu"]
        links = MaterialLinks()
        links.headers = {n: TextureInfo(n, 0, 67, 64, 64, 1, b"", (4096,)) for n in names}
        links.blocks[b"V" * 8] = names
        links.blocks[b"P" * 8] = names[1:2]
        # The atlas and the palette share the material's words; the leaves do not.
        assert links.colour_map("x/vegetationtown_mesh", "M_VegetationTown", b"V" * 8) == "t_com_oak_01_leaves_cu"
        assert links.colour_map("x/buildingstown_mesh", "M_BuildingsTown", b"P" * 8) is None

    def test_a_block_with_only_shared_detail_maps_stays_flat(self):
        links = self.links()
        assert links.colour_map("x/ind_hut_01_mesh", "M_Glass", b"D" * 8) is None
        assert links.colour_map("x/ind_hut_01_mesh", "M_Glass", b"?" * 8) is None

    def test_a_texture_chunk_missing_its_largest_mips_decodes_from_what_it_has(self):
        from heat3d_gamefiles.frostbitematerial import TextureInfo, decode_texture

        red = struct.pack("<HHI", 0xF800, 0xF800, 0)  # BC1: both endpoints pure red
        sizes = (4 * 8, 8, 8, 8)  # 8x8, 4x4, 2x2, 1x1
        info = TextureInfo("t", 0, 57, 8, 8, 4, b"", sizes)

        whole = decode_texture(info, red * 4 + red * 3, largest=8)
        tail = decode_texture(info, red * 3, largest=8)

        assert whole.shape == (8, 8, 3) and tail.shape == (4, 4, 3)
        assert (whole[..., 0] > 240).all() and (whole[..., 1:] < 10).all()
        with pytest.raises(UnsupportedFrostbite, match="tail"):
            decode_texture(info, red * 2 + b"\x00", largest=8)


def test_sections_carry_their_texture_coordinates():
    from heat3d_gamefiles.frostbitemesh import decode_sections

    positions = TestMesh.positions
    uvs = np.array([[0, 0], [2, 0], [0, 3], [1, 1]], dtype=np.float32)
    mesh = read_meshset(fx.meshset(2, 4, uv=True))

    (section,) = decode_sections(mesh.lods[0], fx.buffers(positions, TestMesh.faces, uvs=uvs))

    assert np.allclose(section.positions, positions)
    assert np.allclose(section.uvs, uvs)  # tiling coordinates are kept, not clamped
    assert mesh.lods[0].sections[0].key == b"\x01" * 8


def test_a_repeating_texture_keeps_float_coordinates(tmp_path):
    import json

    from heat3d_gamefiles.glb import Part, write_glb

    positions = np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1]], dtype=np.float32)
    image = np.full((4, 4, 3), 200, dtype=np.uint8)
    out = write_glb(
        tmp_path / "t.glb", positions,
        parts=[Part("structure:buildings t", np.array([[0, 2, 1]]), texture=image)],
        uvs=np.array([[0, 0], [3, 0], [0, 2]], dtype=np.float32), repeat=True,
    )
    raw = out.read_bytes()
    (length,) = struct.unpack_from("<I", raw, 12)
    doc = json.loads(raw[20 : 20 + length])
    assert doc["samplers"][0]["wrapS"] == 10497
    uv = doc["meshes"][0]["primitives"][0]["attributes"]["TEXCOORD_0"]
    assert doc["accessors"][uv]["componentType"] == 5126


@needs_level
def test_vegetation_stands_on_the_decoded_terrain(catalogue):
    """
    Trees and bushes are placed on the ground and nowhere else, so their
    origins are the sharpest check of the heightfield: within half a metre
    in the median, where any misreading puts them metres off.
    """
    from heat3d_gamefiles.frostbitelevel import CATEGORIES, find_placements
    from heat3d_gamefiles.frostbiteterrain import STREAMING_TREE, read_tree, sample_heights

    trees = [e for e in catalogue.res.values() if e.res_type == STREAMING_TREE]
    if not trees:
        pytest.skip("the level has no terrain")
    tree = read_tree(catalogue.read(trees[0].location), trees[0].name)
    placed = find_placements(catalogue, ebx_prefix(LEVEL), report=lambda *a: None)
    vegetation = dict(CATEGORIES)["structure:trees"]
    origins = [
        np.concatenate(blocks)[:, 3, :3]
        for mesh, blocks in placed.meshes.items()
        if vegetation.search("/" + mesh)
    ]
    if not origins:
        pytest.skip("the level places no vegetation")
    points = np.concatenate(origins)
    heights = sample_heights(tree, catalogue.chunk, points[:, 0], points[:, 2])
    off = np.abs(points[:, 1] - heights)
    assert np.nanmedian(off) < 0.5


def _decal_res(guid: bytes) -> bytes:
    """
    Two decal batches of one triangle each, the first mapped by world
    position, the second naming a texture in its tail.
    """
    records = b""
    for k in range(2):
        core = bytearray(156)
        struct.pack_into("<II", core, 32, 3 * k, 1)
        struct.pack_into("<f", core, 44, 10.0)
        tail = struct.pack("<II", 96 * k, 96) + (guid if k == 1 else b"\x00" * 16) + b"\x00" * 7
        records += bytes(core) + tail
    head = bytearray(20 + 16 + 4)
    struct.pack_into("<I", head, 16, 1)
    struct.pack_into("<I", head, 36, 2)
    from heat3d_gamefiles.frostbitedecals import VERTEX

    vertices = np.zeros(6, dtype=VERTEX)
    vertices["x"] = [0, 8, 0, 10, 12, 10]
    vertices["z"] = [0, 0, 8, 0, 0, 2]
    vertices["u"] = [0, 8, 0, 0, 1, 0]
    vertices["v"] = [0, 0, 8, 0, 0, 1]
    vertices["rgba"] = 1.0
    vertices["u"][:3], vertices["v"][:3] = vertices["x"][:3], vertices["z"][:3]
    # One u32 index per vertex, then sixteen bytes, end the res.
    return bytes(head) + records + vertices.tobytes() + bytes(4 * len(vertices) + 16)


class TestDecals:
    def test_batches_vertices_and_textures_are_read(self):
        from heat3d_gamefiles.frostbitedecals import read_decals

        decals = read_decals(_decal_res(b"T" * 16), {b"T" * 16: "x/t_line_op"})

        assert [(b.first, b.triangles, b.tiling) for b in decals.batches] == [(0, 1, 10.0), (3, 1, 10.0)]
        assert decals.batches[1].texture("_op") == "x/t_line_op"
        assert decals.vertices["x"].tolist() == [0, 8, 0, 10, 12, 10]

    def test_a_record_out_of_sequence_is_refused(self):
        from heat3d_gamefiles.frostbitedecals import read_decals

        res = bytearray(_decal_res(b"T" * 16))
        struct.pack_into("<I", res, 40 + 187 + 156, 999)  # second record's byte offset
        with pytest.raises(UnsupportedFrostbite, match="record 1"):
            read_decals(bytes(res), {})

    def test_a_decal_is_composited_by_its_alpha(self):
        from heat3d_gamefiles.frostbitedecals import Layer, bake, read_decals

        decals = read_decals(_decal_res(b"T" * 16), {})
        decals.vertices["rgba"][:3, 3] = 0.5
        base = np.zeros((16, 16, 3), dtype=np.float32)
        layers = [Layer(None, (1.0, 1.0, 1.0), None, True, 10.0), None]

        out = bake(decals, layers, base, (0.0, 0.0), 1.0)

        assert np.allclose(out[1, 1], 0.5)  # inside the first triangle, half covered
        assert np.allclose(out[10, 10], 0.0)  # outside it
        assert np.allclose(out[0, 12], 0.0)  # the second batch has no layer


@needs_level
def test_shipped_terrain_decals_are_read(catalogue):
    """Every record's vertex range follows the last; most batches name their textures."""
    from heat3d_gamefiles.frostbitedecals import TERRAIN_DECALS, read_decals
    from heat3d_gamefiles.frostbitematerial import link_materials

    entries = [e for e in catalogue.res.values() if e.res_type == TERRAIN_DECALS]
    if not entries:
        pytest.skip("the level has no terrain decals")
    links = link_materials(catalogue)
    decals = read_decals(catalogue.read(entries[0].location), links.by_guid, entries[0].name)

    assert sum(3 * b.triangles for b in decals.batches) == len(decals.vertices)
    assert np.mean([bool(b.textures) for b in decals.batches]) > 0.8
    # Decals are small: read at the wrong vertex, triangles reach across the map.
    v = decals.vertices
    p = np.stack([v["x"], v["z"]], 1).reshape(-1, 3, 2)
    edge = np.linalg.norm(p - np.roll(p, 1, axis=1), axis=2).max(axis=1)
    assert np.median(edge) < 50


class TestLevelLayers:
    """Which table is a level, when the base game and its updates each ship one."""

    @staticmethod
    def table(root: Path, base: str, name: str, bundles: int) -> Path:
        path = root / base / "Win32" / "game" / "levels" / name / f"{name}.toc"
        path.parent.mkdir(parents=True, exist_ok=True)
        blobs = [fx.bundle_blob([(1, 1, 0, 4)])] * bundles
        path.write_bytes(fx.level_table([(b"G" * 16, fx.location(1, 1, 0, 4))], blobs))
        return path

    @staticmethod
    def install(tmp_path: Path) -> Path:
        (tmp_path / "Data").mkdir()
        (tmp_path / "Data" / "layout.toc").write_bytes(b"")
        return tmp_path

    def test_an_update_s_complete_table_wins_over_a_stub_in_data(self, tmp_path):
        from heat3d_gamefiles.frostbitebundle import level_sources

        root = self.install(tmp_path)
        stub = self.table(root, "Data", "lv_a", 0)
        real = self.table(root, "Update/Pack/Data", "lv_a", 2)
        extra = self.table(root, "Update/Hres/Data/Win32/installation/detail/pkg", "lv_a", 0)

        (table,) = level_sources(root).values()

        assert table.toc == real and table.source == "Update/Pack"
        assert set(table.supplements) == {stub, extra}

    def test_a_level_only_in_data_comes_from_data(self, tmp_path):
        from heat3d_gamefiles.frostbitebundle import level_sources

        root = self.install(tmp_path)
        own = self.table(root, "Data", "lv_b", 1)
        self.table(root, "Update/Hres/Data", "lv_c", 0)  # chunks only: not a level

        found = level_sources(root)

        assert set(found) == {"lv_b"}
        assert found["lv_b"].toc == own and found["lv_b"].source == "Data"

    def test_of_two_complete_tables_the_later_layer_wins(self, tmp_path):
        from heat3d_gamefiles.frostbitebundle import level_sources

        root = self.install(tmp_path)
        self.table(root, "Data", "lv_d", 1)
        newer = self.table(root, "Update/Patch/Data", "lv_d", 1)

        assert level_sources(root)["lv_d"].toc == newer


def _nav_tile(points, polygons, box=((0, 0, 0), (16, 10, 16)), detail=None) -> bytes:
    """
    A navigation tile: `polygons` are (vertex indices, kind); `detail`, if
    given, is (detail vertices, [(first vertex, first triangle, vertex count,
    triangle count) per polygon], triangles of three indices).
    """
    from heat3d_gamefiles.frostbitenav import MAGIC, POLYGON, VERTICES

    extra, meshes, triangles = detail if detail else ([], [], [])
    head = bytearray(VERTICES)
    head[:4] = MAGIC
    struct.pack_into("<I", head, 4, 7)
    struct.pack_into(
        "<9I", head, 24, len(polygons), len(points), 0, len(meshes), len(extra), len(triangles), 0, 0, len(meshes)
    )
    struct.pack_into("<3f", head, 188, 1.8, 0.18, 0.4)
    struct.pack_into("<6f", head, 200, *box[0], *box[1])
    body = bytes(head) + np.asarray(points, dtype="<f4").tobytes()
    body += bytes(-len(body) % 8)
    for indices, kind in polygons:
        record = bytearray(POLYGON)
        struct.pack_into("<6H", record, 4, *(list(indices) + [0xFFFF] * 6)[:6])
        record[30] = len(indices)
        record[31] = (kind << 6) | 63
        body += bytes(record)
    for mesh in meshes:
        body += struct.pack("<IIBB2x", *mesh)
    body += np.asarray(extra, dtype="<f4").tobytes()
    for tri in triangles:
        body += bytes(list(tri) + [0])
    return body


class TestNavigation:
    points = [(1, 0, 1), (9, 0, 1), (9, 0, 9), (1, 0, 9), (4, 1, 4), (300, 120, -500), (0, 0, 0)]

    def test_surfaces_are_read_and_links_left_out(self):
        from heat3d_gamefiles.frostbitenav import read_tile

        blob = _nav_tile(self.points, [((0, 1, 2, 3), 0), ((0, 4, 1), 2), ((5, 6, 2, 3), 1)])

        agent, vertices, polygons = read_tile(blob)

        assert np.allclose(agent, (1.8, 0.18, 0.4))
        assert np.allclose(vertices[:5], self.points[:5])
        # The link reaches 500 m out of its 16 m tile and is no surface; with
        # no detail meshes, the polygons are fanned.
        assert polygons == [(0, 1, 2), (0, 2, 3), (0, 4, 1)]

    def test_a_polygon_s_detail_mesh_gives_its_surface(self):
        from heat3d_gamefiles.frostbitenav import read_tile

        # A flat square whose detail mesh raises its middle by a metre: four
        # triangles round one detail vertex, index 4 (after the 4 corners).
        detail = ([(5, 1, 5)], [(0, 0, 1, 4)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)])
        blob = _nav_tile(self.points[:4], [((0, 1, 2, 3), 0)], detail=detail)

        _agent, vertices, triangles = read_tile(blob)

        assert triangles == [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        assert np.allclose(vertices[4], (5, 1, 5))

    def test_a_surface_outside_its_tile_is_refused(self):
        from heat3d_gamefiles.frostbitenav import read_tile

        with pytest.raises(UnsupportedFrostbite, match="outside"):
            read_tile(_nav_tile(self.points, [((0, 5, 2), 0)]))

    def test_an_index_past_the_vertices_is_refused(self):
        from heat3d_gamefiles.frostbitenav import read_tile

        with pytest.raises(UnsupportedFrostbite, match="vertex"):
            read_tile(_nav_tile(self.points, [((0, 1, 9), 0)]))


class TestUntile:
    """Repeating textures cut into pieces that each sit inside 0..1."""

    @staticmethod
    def signed_area(points, faces):
        t = points[faces].astype(np.float64)
        return (np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])[:, 2] / 2).sum()

    def test_every_piece_shows_the_same_pixels_inside_0_to_1(self):
        from heat3d_gamefiles.frostbitelevel import untile

        # Texture coordinates equal to x and y: however a triangle is cut, a
        # point's coordinates must stay its position less whole repeats.
        rng = np.random.default_rng(3)
        uv = (rng.random((40, 2)) * 7 - 3).astype(np.float32)
        points = np.column_stack([uv, np.zeros(len(uv))]).astype(np.float32)
        faces = rng.integers(0, len(uv), (60, 3))
        faces = faces[np.ptp(faces, axis=1) > 0]

        out_points, out_faces, out_uv = untile(points, faces, uv)

        assert len(out_faces) > len(faces)
        assert out_uv.min() >= 0 and out_uv.max() <= 1
        offset = out_uv - out_points[:, :2]
        assert np.allclose(offset, np.round(offset), atol=1e-4)
        # Flat, so the signed areas add up only if every piece is wound as
        # its triangle was.
        assert np.isclose(self.signed_area(out_points, out_faces), self.signed_area(points, faces), rtol=1e-5)

    def test_triangles_inside_keep_their_shared_vertices(self):
        from heat3d_gamefiles.frostbitelevel import untile

        points = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32)
        uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
        faces = np.array([[0, 1, 2], [0, 2, 3]])

        out = untile(points, faces, uv)

        assert out[0] is points and out[1] is faces and out[2] is uv

    def test_a_texture_repeating_too_often_is_left_as_it_is(self):
        from heat3d_gamefiles.frostbitelevel import untile

        points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        uv = np.array([[0, 0], [40, 0], [0, 1]], dtype=np.float32)

        _points, out_faces, out_uv = untile(points, np.array([[0, 1, 2]]), uv)

        assert len(out_faces) == 1 and np.allclose(out_uv, uv)


def test_a_level_without_backdrop_takes_its_surfaces_middle_colour(monkeypatch):
    from types import SimpleNamespace

    from heat3d_gamefiles import frostbitelevel
    from heat3d_gamefiles.frostbitematerial import SHADER_BLOCK_DEPOT, MaterialLinks

    shades = {"t_sand_cv": 200, "t_gravel_cv": 150, "t_soil_cv": 100, "t_ter_defaulttexture_cv": 255, "t_sand_nhs": 0}
    links = MaterialLinks()
    links.by_guid = {bytes([i]) * 16: name for i, name in enumerate(shades, 1)}
    links.headers = {name: None for name in shades}
    depot = SimpleNamespace(res_type=SHADER_BLOCK_DEPOT, name="x/terrain.layergraphs_shaderblockdepot", location=0)
    other = SimpleNamespace(res_type=SHADER_BLOCK_DEPOT, name="x/sub_world_shaderblockdepot", location=1)
    blobs = [b"\0" * 7 + b"".join(links.by_guid) + b"\0" * 5, b"\x01" * 16]
    level = SimpleNamespace(res={"a": depot, "b": other}, read=lambda at: blobs[at])
    monkeypatch.setattr(
        frostbitelevel, "_image", lambda _level, _links, name, _largest: np.full((4, 4, 3), shades[name], np.uint8)
    )

    colour = frostbitelevel._surface_colour(level, links)

    # The median of sand, gravel and soil; the default surface and the
    # non-colour map are left out.
    assert np.allclose(colour, 150 / 255)


def test_only_a_named_mask_of_alpha_cuts_a_surface_out():
    from heat3d_gamefiles.frostbitematerial import is_cutout

    leaves = np.full((8, 8, 4), 255, np.uint8)
    leaves[:4, :, 3] = 0  # half the card is empty
    smooth = leaves.copy()
    smooth[:, :, 3] = np.linspace(20, 230, 64).reshape(8, 8)  # a gradient: smoothness

    assert is_cutout("x/t_tree_01_leaves_cu", leaves)
    assert is_cutout("x/t_seaweed_01_ca_1", leaves)
    assert not is_cutout("x/t_tree_01_bark_cs", leaves)  # in `_cs` alpha is smoothness
    assert not is_cutout("x/t_tree_01_leaves_cu", smooth)
    assert not is_cutout("x/t_tree_01_leaves_cu", np.full((8, 8, 4), 255, np.uint8))  # nothing cut
    empty = leaves.copy()
    empty[:, :, 3] = 0  # no alpha at all: fronds cut by geometry, drawn whole
    assert not is_cutout("x/t_tree_02_leaves_cu", empty)


def test_a_cut_out_texture_is_a_masked_two_sided_png(tmp_path):
    import io
    import json

    from PIL import Image

    from heat3d_gamefiles.glb import Part, write_glb

    positions = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [5, 0, 0], [6, 0, 0], [5, 1, 0]], dtype=np.float32)
    leaves = np.zeros((4, 4, 4), dtype=np.uint8)
    leaves[:, :2] = (40, 120, 40, 255)
    wall = np.full((4, 4, 3), 180, dtype=np.uint8)
    out = write_glb(
        tmp_path / "t.glb", positions,
        parts=[
            Part("structure:trees leaves", np.array([[0, 1, 2]]), texture=leaves, alpha_cutoff=0.5),
            Part("structure:buildings wall", np.array([[3, 4, 5]]), texture=wall),
        ],
        uvs=np.zeros((6, 2), dtype=np.float32),
    )
    raw = out.read_bytes()
    (length,) = struct.unpack_from("<I", raw, 12)
    doc = json.loads(raw[20 : 20 + length])
    masked, opaque = doc["materials"]

    assert masked["alphaMode"] == "MASK" and masked["alphaCutoff"] == 0.5 and masked["doubleSided"]
    assert "alphaMode" not in opaque and "doubleSided" not in opaque
    assert [i["mimeType"] for i in doc["images"]] == ["image/png", "image/jpeg"]
    view = doc["bufferViews"][doc["images"][0]["bufferView"]]
    binary = raw[20 + length + 8 :]
    png = Image.open(io.BytesIO(binary[view["byteOffset"] : view["byteOffset"] + view["byteLength"]]))
    assert png.mode == "RGBA" and np.asarray(png)[0, 3, 3] == 0


def _repeating_model():
    from heat3d_gamefiles.frostbitelevel import LevelModel, Piece

    model = LevelModel()
    bark = Piece(texture="t_bark_cs")
    # A long thin branch whose bark repeats twelve times along it.
    bark.add(
        np.array([[0, 0, 0], [0.1, 0, 0], [0, 5, 0]], dtype=np.float32), np.array([[0, 1, 2]]),
        np.array([[0, 0], [1, 0], [0, 12]], dtype=np.float32),
    )
    wall = Piece(texture="t_wall_cs")
    wall.add(
        np.array([[5, 0, 0], [6, 0, 0], [5, 1, 0]], dtype=np.float32), np.array([[0, 1, 2]]),
        np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32),
    )
    model.parts = {"structure:trees t_bark_cs": bark, "structure:buildings t_wall_cs": wall}
    model.images = {
        "t_bark_cs": np.full((4, 4, 3), (100, 60, 20), np.uint8),
        "t_wall_cs": np.full((4, 4, 3), 200, np.uint8),
    }
    return model


def test_a_repeating_texture_keeps_its_uvs_and_repeats(tmp_path):
    import json

    from heat3d_gamefiles.frostbitelevel import write_level

    model = _repeating_model()
    out = write_level(model, tmp_path / "t.glb")

    raw = out.read_bytes()
    (length,) = struct.unpack_from("<I", raw, 12)
    doc = json.loads(raw[20 : 20 + length])
    # Nothing cut and nothing flattened: two triangles, as placed.
    assert model.flattened == 0
    assert [m["name"] for m in doc["materials"]] == ["structure:buildings t_wall_cs", "structure:trees t_bark_cs"]
    assert sum(doc["accessors"][p["indices"]]["count"] for m in doc["meshes"] for p in m["primitives"]) == 6
    # The bark's UVs run to 12 down the branch, and the sampler repeats them.
    binary = raw[20 + length + 8 :]
    highest = 0.0
    for a in (p["attributes"]["TEXCOORD_0"] for m in doc["meshes"] for p in m["primitives"]):
        accessor = doc["accessors"][a]
        view = doc["bufferViews"][accessor["bufferView"]]
        start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        assert accessor["componentType"] == 5126
        uv = np.frombuffer(binary, np.float32, accessor["count"] * 2, start)
        highest = max(highest, float(uv.max()))
    assert highest == 12
    assert all(s["wrapS"] == 10497 and s["wrapT"] == 10497 for s in doc["samplers"])


def test_clamped_output_draws_a_texture_too_dense_to_cut_in_its_average_colour(tmp_path):
    import json

    from heat3d_gamefiles.frostbitelevel import write_level

    model = _repeating_model()
    out = write_level(model, tmp_path / "t.glb", clamped=True)

    raw = out.read_bytes()
    (length,) = struct.unpack_from("<I", raw, 12)
    doc = json.loads(raw[20 : 20 + length])
    by_name = {m["name"]: m["pbrMetallicRoughness"] for m in doc["materials"]}
    assert model.flattened == 1
    assert "baseColorTexture" in by_name["structure:buildings t_wall_cs"]
    # The branch has a part of its own, in the bark's average colour, and is not
    # cut into twelve or more; the textured part it came from is left empty.
    assert "baseColorTexture" not in by_name["structure:trees t_bark_cs (average colour)"]
    assert "structure:trees t_bark_cs" not in by_name
    assert sum(doc["accessors"][p["indices"]]["count"] for m in doc["meshes"] for p in m["primitives"]) == 6


def _bc7_solid(rgb) -> bytes:
    """One BC7 block (mode 6) of a single opaque colour."""
    bits, at = 1 << 6, 7  # mode 6
    for channel in (*rgb, 255):
        for _endpoint in range(2):
            bits |= (channel >> 1) << at
            at += 7
    for channel in (rgb[0] & 1, rgb[0] & 1):  # p-bits: the low bit
        bits |= channel << at
        at += 1
    return bits.to_bytes(16, "little")  # indices all 0: endpoint 0


def test_the_colormap_pages_lie_on_their_quadrants():
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbiteterrain import COLOUR_QUADRANTS, MASK_PAGE, TerrainTree, read_colormap

    colours = [(200, 40, 40), (40, 200, 40), (40, 40, 200), (200, 200, 40)]
    pages = b"".join(_bc7_solid(c) * (33 * 33) for c in colours)
    node = SimpleNamespace(depth=1, ix=1, iz=0, second=b"C" * 16)
    tree = TerrainTree(265, 1280.0, (0.0, 0.0, 512.0, 512.0), [node])
    chunks = {b"C" * 16: bytes(MASK_PAGE) + pages}  # one mask page before the colormap

    cm = read_colormap(tree, chunks.__getitem__, chunks.__contains__)

    assert cm.metres == 1.0 and cm.origin == (256.0, 0.0)
    for colour, (qx, qz) in zip(colours, COLOUR_QUADRANTS):
        x, z = 256 + 64 + 128 * qx, 64 + 128 * qz
        got = cm.sample(np.array([x], float), np.array([z], float))[0] * 255
        assert np.allclose(got, colour, atol=2), (colour, got)
    assert np.isnan(cm.sample(np.array([10.0]), np.array([10.0]))).all()  # outside the node


def test_the_colormap_follows_the_mask_pages_the_mask_tree_counts():
    import struct
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbiteterrain import MASK_HEADER, MASKS, TerrainTree, read_colormap

    # One uncompressed mask page (the group of quadrant (1, 0) has one), the
    # colormap, then four pages of another raster in a flat colour.
    record = struct.pack("<HH4f", 3, 0, 256.0, 0.0, 384.0, 128.0) + bytes([1, 0]) + bytes(11)
    group = struct.pack("<HHI", 0, 1, 1) + record + bytes(1)
    body = struct.pack("<I", 66) + bytes(MASK_HEADER - 4) + group
    node = SimpleNamespace(depth=0, ix=0, iz=0, second=b"C" * 16)
    tree = TerrainTree(265, 1280.0, (0.0, 0.0, 512.0, 512.0), [node], rasters={MASKS: body})
    colormap = _bc7_solid((200, 120, 40)) * (33 * 33) * 4
    other = _bc7_solid((0, 190, 190)) * (33 * 33) * 4
    chunks = {b"C" * 16: bytes(66 * 66) + colormap + other}

    cm = read_colormap(tree, chunks.__getitem__, chunks.__contains__)

    got = cm.sample(np.array([100.0, 400.0]), np.array([100.0, 400.0])) * 255
    assert np.allclose(got, (200, 120, 40), atol=2), got


def test_a_chunk_of_many_colormaps_lengths_is_another_layout():
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbiteterrain import COLOUR_PAGES, TerrainTree, read_colormap

    node = SimpleNamespace(depth=0, ix=0, iz=0, second=b"C" * 16)
    tree = TerrainTree(265, 1280.0, (0.0, 0.0, 512.0, 512.0), [node])
    chunks = {b"C" * 16: bytes(10 * COLOUR_PAGES)}

    assert read_colormap(tree, chunks.__getitem__, chunks.__contains__) is None


@pytest.mark.parametrize("tile", [66, 72])
def test_mask_pages_land_on_their_quadrants(tile):
    import struct
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbiteterrain import MASK_HEADER, MASKS, TerrainTree, read_masks

    border = (tile - 64) // 2

    def page(low, high):
        # Rows along z: the core's lower half `low`, its upper half `high`; the border 1.
        image = np.ones((tile, tile), np.uint8)
        image[border : border + 32, border : border + 64] = low
        image[border + 32 : border + 64, border : border + 64] = high
        if tile == 66:
            return image.tobytes()
        # BC4, one solid block per 4 x 4 texels.
        return b"".join(
            bytes([image[by * 4, bx * 4]] * 2) + bytes(6) for by in range(18) for bx in range(18)
        )

    def record(layer, box, full=False, deeper=False):
        return struct.pack("<HH4f", layer, 0, *box) + bytes([0 if deeper else 1, 1 if full else 0]) + bytes(11)

    def group(records, pages):
        return struct.pack("<HHI", 0, len(records), pages) + b"".join(records) + bytes(1)

    q = lambda x, z, side=256.0, at=(0.0, 0.0): (at[0] + x * side, at[1] + z * side, at[0] + (x + 1) * side, at[1] + (z + 1) * side)
    # The root: layer 5 paged in (0, 0) and (1, 1), full in (1, 0), absent in
    # (0, 1); layer 6 paged in (0, 1) only. Layer 5 goes on in (1, 1)'s group.
    root = group(
        [record(5, q(0, 0)), record(5, q(1, 0), full=True), record(5, q(1, 1), deeper=True), record(6, q(0, 1))], 3
    )
    child = group([record(5, q(0, 0, 128.0, (256.0, 256.0)))], 1)
    empty = struct.pack("<HHH", 1, 0, 0) + bytes(1)  # a group without records: 7 bytes
    body = struct.pack("<I", tile) + bytes(MASK_HEADER - 4) + root + empty + child
    node = SimpleNamespace(depth=0, ix=0, iz=0, chunk=b"N" * 16, flags=0, second=b"S" * 16)
    tree = TerrainTree(265, 1280.0, (0.0, 0.0, 512.0, 512.0), [node], rasters={MASKS: body})
    chunks = {b"N" * 16: page(40, 50) + page(80, 80) + page(120, 120), b"S" * 16: page(200, 200)}

    masks = read_masks(tree, chunks.__getitem__, chunks.__contains__)
    five = masks.raster(5, (0.0, 0.0), 8.0, (64, 64)) * 255
    six = masks.raster(6, (0.0, 0.0), 8.0, (64, 64)) * 255

    at = lambda image, x, z: round(float(image[int(z // 8), int(x // 8)]))
    assert (at(five, 100, 60), at(five, 100, 200)) == (40, 50)  # rows along z, border cut
    assert at(five, 300, 100) == 255  # full
    assert at(five, 100, 300) == 0  # named by the group, absent in the quadrant
    # The child group replaces its node: its one quadrant paged, the others empty.
    assert at(five, 300, 300) == 200 and at(five, 450, 450) == 0
    assert at(six, 100, 300) == 120 and at(six, 300, 100) == 0


def test_mask_pages_whose_borders_disagree_are_refused():
    import struct
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbite import UnsupportedFrostbite
    from heat3d_gamefiles.frostbiteterrain import MASK_HEADER, MASKS, TerrainTree, read_masks

    # Two pages of one layer side by side along x, a ramp across both: the
    # left page's right border holds the right page's first core columns.
    ramp = np.arange(130, dtype=np.uint8)  # texel x of the two cores and their borders
    left = np.tile(ramp[0:66], (66, 1))
    right = np.tile(ramp[64:130], (66, 1))

    def record(box):
        return struct.pack("<HH4f", 2, 0, *box) + bytes([1, 0]) + bytes(11)

    group = struct.pack("<HHI", 0, 2, 2) + record((0.0, 0.0, 256.0, 256.0)) + record((256.0, 0.0, 512.0, 256.0)) + bytes(1)
    body = struct.pack("<I", 66) + bytes(MASK_HEADER - 4) + group
    node = SimpleNamespace(depth=0, ix=0, iz=0, chunk=b"N" * 16, flags=0, second=None)
    tree = TerrainTree(265, 1280.0, (0.0, 0.0, 512.0, 512.0), [node], rasters={MASKS: body})

    chunks = {b"N" * 16: left.tobytes() + right.tobytes()}
    assert read_masks(tree, chunks.__getitem__, chunks.__contains__) is not None

    chunks = {b"N" * 16: right.tobytes() + left.tobytes()}  # the pages swapped
    with pytest.raises(UnsupportedFrostbite, match="0 of 1 borders agree"):
        read_masks(tree, chunks.__getitem__, chunks.__contains__)


def _float3(family: bytes, value) -> bytes:
    """One float3 parameter of a shader block: tag, flags, name hash, count, value, id."""
    return bytes.fromhex("f11af8250180") + family + struct.pack("<I3f", 1, *value) + bytes(8)


def test_a_block_s_tint_is_each_family_s_first_value_that_is_not_neutral():
    from heat3d_gamefiles.frostbitematerial import block_tint

    # The first of a family is neutral (0.5 where 0.5 leaves the map as it is),
    # the second blue; another family halves the brightness.
    block = (
        bytes(40)
        + _float3(bytes.fromhex("8a88"), (0.5, 0.5, 0.5))
        + _float3(bytes.fromhex("8a88"), (0.0, 0.5, 0.002))  # a channel selector, not a paint
        + _float3(bytes.fromhex("8a88"), (0.05, 0.1, 0.2))
        + _float3(bytes.fromhex("8a88"), (0.2, 0.2, 0.2))
        + _float3(bytes.fromhex("4141"), (0.5, 0.5, 0.5))
        + _float3(bytes.fromhex("1234"), (0.0, 1.0, 0.0))  # not a tint
    )
    assert np.allclose(block_tint(block), (0.05, 0.1, 0.2))
    assert block_tint(bytes(40) + _float3(bytes.fromhex("8a88"), (0.5, 0.5, 0.5))) is None


def test_a_grey_map_takes_its_tint_and_a_coloured_one_keeps_its_colour():
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbitelevel import _tinted

    model = SimpleNamespace(images={"grey": np.full((4, 4, 3), 200, np.uint8), "red": np.zeros((4, 4, 3), np.uint8)})
    model.images["red"][..., 0] = 200
    name = _tinted(model, "grey", (1.0, 0.5, 0.25))
    assert name != "grey" and model.images[name][0, 0, 0] == 200 > model.images[name][0, 0, 1] > model.images[name][0, 0, 2]
    assert _tinted(model, "red", (1.0, 0.5, 0.25)) == "red"
    assert _tinted(model, "grey", None) == "grey"


def test_a_palette_vertex_draws_its_swatch_s_centre():
    from heat3d_gamefiles.frostbitelevel import _palette_uvs

    palette = np.array([[0, 0, 0, 255], [153, 32, 0, 255], [255, 255, 219, 64]], np.float32)
    assert np.allclose(_palette_uvs(palette), [[1 / 32, 1 / 32], [9.5 / 16, 2.5 / 16], [15.5 / 16, 15.5 / 16]])


def test_blockout_cinematic_lighting_and_channel_mask_names_are_left_out():
    from heat3d_gamefiles.frostbitedecals import MASK_PAINT
    from heat3d_gamefiles.frostbitelevel import BLOCKOUT, CINEMATIC, LIGHTING
    from heat3d_gamefiles.frostbitematerial import MaterialLinks, TextureInfo

    assert BLOCKOUT.search("M_Whitebox") and not BLOCKOUT.search("M_WhiteBrick")
    assert CINEMATIC.search("common/hardware/vehicles/heli/art/cinematics/ob_heli_cin_mesh")
    assert LIGHTING.search("common/lighting/meshes/plane_light_blocker_01_mesh")
    paint = next(k for pattern, _c, k in MASK_PAINT if pattern.search("t_road_variationmask_01_rgb"))
    assert paint == 0.0  # a variation mask is not drawn
    stain = next((c, k) for pattern, c, k in MASK_PAINT if pattern.search("t_town_stains_01_a_rgb"))
    assert stain[1] < 1 and max(stain[0]) < 0.5  # a stain darkens
    names = ["t_com_glassdebris_01_rgb", "t_com_glass_01_cs"]
    links = MaterialLinks()
    links.headers = {n: TextureInfo(n, 0, 67, 64, 64, 1, b"", (4096,)) for n in names}
    links.blocks[b"G" * 8] = names
    assert links.colour_map("x/glassdebris_01_mesh", "M_GlassDebris", b"G" * 8) == "t_com_glass_01_cs"
    names = ["t_town_stairs_01_b_rgba", "t_com_detail_01_cs"]
    links.headers.update({n: TextureInfo(n, 0, 67, 64, 64, 1, b"", (4096,)) for n in names})
    links.blocks[b"S" * 8] = names
    assert links.colour_map("x/town_stairs_01_mesh", "M_Stairs", b"S" * 8) == "t_town_stairs_01_b_rgba"  # colour and alpha


def test_a_coarse_slope_grid_is_spread_back_bilinearly():
    from heat3d_gamefiles.frostbitelevel import _upsample

    coarse = np.array([[0.0, 8.0], [16.0, 24.0]], np.float32)
    fine = _upsample(coarse, 8, 16, 16)
    assert fine.shape == (16, 16)
    assert fine[0, 0] == 0 and fine[0, 4] == 4 and fine[4, 0] == 8 and fine[8, 8] == 24
    assert len(np.unique(fine)) > 4  # a ramp, not four blocks


def test_an_object_s_overlay_is_drawn_through_its_unwrap():
    from heat3d_gamefiles.frostbitelevel import _unwrapped
    from heat3d_gamefiles.frostbitematerial import MaterialLinks, TextureInfo

    names = ["t_tank_02_trim_cs", "t_tank_02_overlay_cs", "t_tank_02_overlay_a"]
    links = MaterialLinks()
    links.headers = {n: TextureInfo(n, 0, 67, 64, 64, 1, b"", (4096,)) for n in names}
    links.blocks[b"T" * 8] = names
    links.blocks[b"N" * 8] = names[:2]  # an overlay without its mask is not taken
    assert links.overlay(b"T" * 8) == "t_tank_02_overlay_cs"
    assert links.overlay(b"N" * 8) is None
    assert _unwrapped(np.array([[0.0, 0.0], [0.92, 1.0]])) and not _unwrapped(np.array([[-8.0, 0.0], [9.0, 4.0]]))


def test_a_variation_draws_with_the_block_its_hash_keys():
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbitelevel import variant_keys, variation_hashes, with_variations

    rows = np.zeros((3, 4, 4), np.float32)
    rows[:, 0, 0] = rows[:, 1, 1] = rows[:, 2, 2] = 1.0
    rows[:, 0, 3] = 7.0  # padding as a file may leave it: not a hash
    placed = with_variations(rows, [0, 0x88AF2290, 0x88AF2292])
    hashes = variation_hashes(placed)
    assert hashes.tolist() == [0, 0x88AF2290, 0x88AF2292]
    assert np.allclose(placed[:, :3, :3], rows[:, :3, :3])
    # A section keyed 05177857 76ddd22e: the first variation has a block under
    # the key with the hash added to its first four bytes, the second has not.
    default = bytes.fromhex("0517785776ddd22e")
    blue = bytes.fromhex("953927e076ddd22e")  # 0x57781705 + 0x88af2290 = 0xe0273995
    links = SimpleNamespace(blocks={default: [], blue: []})
    assert variant_keys(default, hashes, links) == [default, blue, default]
    assert variant_keys(default, hashes, None) == [default] * 3


def test_a_mesh_with_a_destruction_asset_of_its_name_is_destructible(tmp_path):
    import json
    from types import SimpleNamespace

    from heat3d_gamefiles.frostbitelevel import DESTRUCTIBLE, LevelModel, Piece, destructible, write_level

    level = SimpleNamespace(res={"env/br_wall_01.destruction": 0, "env/br_wall_01_mesh": 0}, ebx={})
    assert destructible(level, "env/br_wall_01_mesh")
    assert not destructible(level, "env/crate_01_mesh")

    model = LevelModel()
    for name in ("structure:buildings", "structure:buildings" + DESTRUCTIBLE):
        piece = Piece()
        piece.add(np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], np.float32), np.array([[0, 1, 2]]))
        model.parts[name] = piece
    out = write_level(model, tmp_path / "level.glb")
    data = out.read_bytes()
    (length,) = struct.unpack_from("<I", data, 12)
    nodes = {n["name"]: n for n in json.loads(data[20 : 20 + length])["nodes"]}
    assert nodes["structure:buildings" + DESTRUCTIBLE]["extras"] == {"destructible": True}
    assert "extras" not in nodes["structure:buildings"]


def test_a_variation_swaps_the_texture_its_block_replaces():
    from heat3d_gamefiles.frostbitematerial import MaterialLinks, TextureInfo

    names = ["t_de_hall_letter_a_01_ca", "t_de_hall_number_01_ca", "t_com_plaster_cs"]
    links = MaterialLinks()
    links.headers = {n: TextureInfo(n, 0, 67, 64, 64, 1, b"", (4096,)) for n in names}
    links.blocks[b"D" * 8] = [names[0], names[2]]  # the default: lettering
    links.blocks[b"V" * 8] = [names[1], names[2]]  # the variation: a number in its place
    assert links.colour_map("x/hall_mesh", "M_Letter", b"D" * 8) == names[0]
    assert links.variant_colour_map("x/hall_mesh", "M_Letter", b"V" * 8, b"D" * 8) == names[1]
    assert links.variant_colour_map("x/hall_mesh", "M_Letter", b"D" * 8, b"D" * 8) == names[0]
