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

        ((index, found),) = _members(partition, "group")

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
        rows = np.concatenate([r for _, r in members])
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
