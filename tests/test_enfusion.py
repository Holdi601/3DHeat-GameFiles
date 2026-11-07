"""
Arma Reforger (Enfusion): archives, textures, terrain, the binary world file,
resources and prefabs - and a whole world exported from an install built in
the test.

Written to the layouts settled on against the shipped game (see `enfusion.py`
and `enfusionworld.py`); where the game is installed, checked on it too.
"""

from __future__ import annotations

import json
import math
import struct
import zlib
from pathlib import Path

import lz4.block
import numpy as np
import pytest

from heat3d_gamefiles.enfusion import EnfusionError, FileSystem, find_install, parse_tree, read_directory, read_edds, unlz4
from heat3d_gamefiles.enfusionworld import (
    Prefabs,
    export_world,
    list_worlds,
    parse_rdb,
    place_structures,
    read_terrain,
    read_world,
    resource_paths,
    rotation,
    world_file,
    xob_bounds,
)

# --------------------------------------------------------------------------
# Builders


def chunk(tag: bytes, body: bytes) -> bytes:
    return tag + struct.pack(">I", len(body)) + body


def form(kind: bytes, *chunks: bytes) -> bytes:
    body = kind + b"".join(chunks)
    return b"FORM" + struct.pack(">I", len(body)) + body


def pak(files: dict[str, bytes], compressed: set[str] = frozenset()) -> bytes:
    """A FORM/PAC1 archive: HEAD, DATA, FILE (a tree of directories and files)."""
    head = chunk(b"HEAD", bytes(28))
    data_start = 12 + len(head) + 8
    blob, where = bytearray(), {}
    for path, content in files.items():
        stored = zlib.compress(content) if path in compressed else content
        where[path] = (data_start + len(blob), len(stored), len(content), 1 if path in compressed else 0)
        blob += stored
    tree: dict = {}
    for path in files:
        node = tree
        *folders, name = path.split("/")
        for folder in folders:
            node = node.setdefault(folder, {})
        node[name] = path

    def encode(name: str, node) -> bytes:
        raw = name.encode()
        if isinstance(node, dict):
            out = bytes([0, len(raw)]) + raw + struct.pack("<I", len(node))
            return out + b"".join(encode(k, v) for k, v in node.items())
        offset, stored, size, method = where[node]
        return bytes([1, len(raw)]) + raw + struct.pack("<IIIIHBBI", offset, stored, size, 0, 0, method, 6 if method else 0, 0)

    return form(b"PAC1", head, chunk(b"DATA", bytes(blob)), chunk(b"FILE", encode("", tree)))


def edds(width: int, height: int, dxgi: int, levels: list[tuple[bytes, bytes]]) -> bytes:
    """An .edds: DDS + DX10 header, then (tag, size) per level smallest first, then the levels."""
    head = b"DDS " + struct.pack("<I", 124) + struct.pack("<IIIII", 0x1007, height, width, 0, 0)
    head += struct.pack("<I", len(levels)) + bytes(44)
    head += struct.pack("<II4s", 32, 4, b"DX10") + bytes(20) + bytes(20)
    head += struct.pack("<IIIII", dxgi, 3, 0, 1, 0)
    assert len(head) == 148
    return head + b"".join(struct.pack("<4sI", tag, len(body)) for tag, body in levels) + b"".join(body for _t, body in levels)


def lz4_level(raw: bytes, piece: int = 1 << 16) -> bytes:
    """Chunked LZ4 as a level stores it: total size, then (size | last bit, block) chunks chained by dictionary."""
    out = struct.pack("<I", len(raw))
    for at in range(0, len(raw), piece):
        block = lz4.block.compress(raw[at : at + piece], store_size=False, dict=raw[max(0, at - (1 << 16)) : at])
        last = at + piece >= len(raw)
        out += struct.pack("<I", len(block) | (1 << 31 if last else 0)) + block
    return out


BC1_RED = struct.pack("<HHI", 0xF800, 0xF800, 0)  # a 4x4 block, every pixel pure red


class EBIN:
    """A binary entity file, written token by token."""

    def __init__(self, names: list[str], guids: list[str]) -> None:
        self.names, self.guids, self.body = names, guids, bytearray()

    def n(self, name: str) -> bytes:
        return b"\x0d" + struct.pack("<H", self.names.index(name))

    def guid(self, guid: str) -> bytes:
        return b"\x05" + struct.pack("<H", self.guids.index(guid))

    @staticmethod
    def block(content: bytes) -> bytes:
        return b"\x0e" + struct.pack("<I", 4 + len(content)) + content

    def entity(self, cls: str, prefab: str | None, props: bytes, name: str | None = None) -> bytes:
        out = self.n(cls)
        if name:
            out += b"\x43" + struct.pack("<H", len(name)) + name.encode()
        if prefab:
            out += self.n(":") + self.guid(prefab)
        return out + self.block(bytes(3) + props)

    def vec(self, key: str, *v: float) -> bytes:
        return self.n(key) + b"\x08" + struct.pack("<3f", *v)

    def bytes(self, entities: bytes) -> bytes:
        out = b"EBIN" + struct.pack("<I", 1) + struct.pack("<HH", len(self.names), len(self.guids))
        out += b"".join(struct.pack("<H", len(s)) + s.encode() for s in self.names)
        out += b"".join(bytes.fromhex(g)[::-1] for g in self.guids)
        return out + entities


def rdb(entries: dict[str, str]) -> bytes:
    out = bytearray(b"FORM\0\0\0\0RDBC")
    for path, guid in entries.items():
        raw = path.encode() + b"\0"
        out += struct.pack("<I", len(raw)) + raw + struct.pack("<H", 6) + bytes(4) + bytes.fromhex(guid)[::-1] + bytes(8)
    return bytes(out)


def xob(low, high) -> bytes:
    return form(b"XOB9", chunk(b"HEAD", bytes(4) + struct.pack("<6f", *low, *high) + bytes(40)))


# Terrain: 2 x 2 tiles of 2 blocks of 2 quads, 1 m apart.
BLOCK, BLOCKS, SPACING, SCALE, OFFSET = 3, 2, 1.0, 0.5, -10.0
TILE = (BLOCK - 1) * BLOCKS + 1
SIDE = 2 * (TILE - 1) + 1


def ground(x, z):
    return 20.0 + 0.5 * x - 1.0 * z  # metres; whole steps of SCALE store exactly


def terrain_files(prefix: str = "worlds/Isle/Terrain", *, corrupt: bool = False) -> dict[str, bytes]:
    head = struct.pack("<4I3fI", SIDE, SIDE, BLOCK, BLOCKS, SPACING, SCALE, OFFSET, 9)
    files = {f"{prefix}/Terrain.terr": form(b"TERR", chunk(b"VERS", struct.pack("<I", 9)), chunk(b"HEAD", head))}
    for row in range(2):
        for col in range(2):
            z = (row * (TILE - 1) + np.arange(TILE))[:, None] * SPACING
            x = (col * (TILE - 1) + np.arange(TILE))[None, :] * SPACING
            raw = np.round((ground(x, z) - OFFSET) / SCALE).astype("<u2")
            if corrupt and (row, col) == (0, 1):
                raw[0, 0] += 1  # a vertex its left neighbour also stores
            files[f"{prefix}/.Data/Terrain_{row * 2 + col}.ttile"] = form(b"TERR", chunk(b"HGHT", raw.tobytes()))
            files[f"{prefix}/.Data/Terrain_{row * 2 + col}_supertexture.edds"] = edds(4, 4, 71, [(b"COPY", BC1_RED)])
    return files


class _Files:
    """Just enough of a file system for the prefab and terrain readers."""

    def __init__(self, files: dict[str, bytes]) -> None:
        self.files = {k.lower(): (k, v) for k, v in files.items()}

    def read(self, path: str) -> bytes:
        if path.lower() not in self.files:
            raise FileNotFoundError(path)
        return self.files[path.lower()][1]

    def __contains__(self, path: str) -> bool:
        return path.lower() in self.files

    def find(self, contains: str, suffix: str = "") -> list[str]:
        return sorted(n for p, (n, _v) in self.files.items() if contains.lower() in p and p.endswith(suffix.lower()))


# --------------------------------------------------------------------------
# Archives


class TestArchives:
    def test_files_are_listed_by_path_and_read_back(self, tmp_path):
        files = {"a/b/plain.txt": b"hello", "a/c.bin": b"x" * 1000, "top.conf": b"{}"}
        (tmp_path / "data.pak").write_bytes(pak(files, compressed={"a/c.bin"}))
        listing = read_directory(tmp_path / "data.pak")
        assert sorted(listing) == sorted(files)
        assert listing["a/c.bin"].method == 1 and listing["a/c.bin"].stored < 1000
        fs = FileSystem([tmp_path])
        assert fs.read("A/B/PLAIN.TXT") == b"hello" and fs.read("a/c.bin") == b"x" * 1000

    def test_odd_chunk_lengths_are_not_padded(self, tmp_path):
        # DATA of odd length: an IFF reader that pads would miss the directory.
        (tmp_path / "data.pak").write_bytes(pak({"f": b"abc"}))
        assert read_directory(tmp_path / "data.pak")["f"].size == 3

    def test_a_later_addon_replaces_an_earlier_one(self, tmp_path):
        for addon, text in (("core", b"core"), ("data", b"data")):
            (tmp_path / "addons" / addon).mkdir(parents=True)
            (tmp_path / "addons" / addon / "data.pak").write_bytes(pak({"same.txt": text}))
        assert FileSystem.of_install(tmp_path).read("same.txt") == b"data"

    def test_a_directory_with_bytes_left_over_is_refused(self):
        with pytest.raises(EnfusionError):
            parse_tree(bytes([0, 0]) + struct.pack("<I", 0) + b"junk", Path("x.pak"), 100)

    def test_something_else_is_refused(self, tmp_path):
        (tmp_path / "data.pak").write_bytes(b"PK\x03\x04" + bytes(20))
        with pytest.raises(EnfusionError):
            read_directory(tmp_path / "data.pak")


class TestTextures:
    def test_a_copied_level(self):
        image = read_edds(edds(4, 4, 71, [(b"COPY", BC1_RED)]))
        assert image.shape == (4, 4, 4) and tuple(image[0, 0, :3]) == (255, 0, 0)

    def test_the_largest_level_is_the_last(self):
        green = struct.pack("<HHI", 0x07E0, 0x07E0, 0)
        image = read_edds(edds(4, 4, 71, [(b"COPY", BC1_RED), (b"COPY", green)]))
        assert tuple(image[0, 0, :3]) == (0, 255, 0)

    def test_an_lz4_level(self):
        image = read_edds(edds(4, 4, 71, [(b"LZ4 ", lz4_level(BC1_RED))]))
        assert tuple(image[3, 3, :3]) == (255, 0, 0)

    def test_lz4_chunks_refer_back_into_the_one_before(self):
        rng = np.random.default_rng(1)
        pattern = rng.integers(0, 256, 40_000, dtype=np.uint8).tobytes()
        raw = (pattern * 4)[:150_000]
        level = lz4_level(raw)
        assert unlz4(level) == raw
        # Three chunks, the later ones far smaller than their data: they copy from the dictionary.
        assert len(level) < len(raw) // 2

    def test_a_short_lz4_level_is_refused(self):
        level = lz4_level(b"abcdefgh" * 100)
        with pytest.raises(EnfusionError):
            unlz4(level[:-3])


class TestTerrain:
    def test_tiles_join_row_by_row_and_heights_are_scaled(self):
        terrain = read_terrain(_Files(terrain_files()), "worlds/Isle/Terrain/Terrain.terr")
        assert terrain.heights.shape == (SIDE, SIDE) and terrain.tiles == (2, 2)
        x = np.arange(SIDE)[None, :] * SPACING
        z = np.arange(SIDE)[:, None] * SPACING
        assert np.array_equal(terrain.heights, ground(x, z).astype(np.float32))
        assert terrain.mismatches == 0 and terrain.shared > 0
        assert terrain.height_at(np.array(2.5), np.array(1.0)) == pytest.approx(ground(2.5, 1.0))

    def test_a_disagreeing_tile_edge_is_counted(self):
        terrain = read_terrain(_Files(terrain_files(corrupt=True)), "worlds/Isle/Terrain/Terrain.terr")
        assert terrain.mismatches == 1

    def test_worlds_are_named_by_their_folder(self):
        files = {**terrain_files(), **terrain_files("worlds/Other/Other")}
        files["worlds/Other/Other/Other.terr"] = files.pop("worlds/Other/Other/Terrain.terr")
        fs = _Files(files)
        assert sorted(w for w, _ in list_worlds(fs)) == ["Isle", "Other"]


# --------------------------------------------------------------------------
# The world file

GUIDS = ["0123456789ABCDEF", "1111111111111111", "2222222222222222"]
NAMES = ["$grp", "Tree", ":", "coords", "angles", "scale", "SCR_DestructibleBuildingEntity", "Flags", "ID", "Enabled", "Priority", "LineColor", "GenericEntity"]


def world_bytes() -> bytes:
    w = EBIN(NAMES, GUIDS)
    trees = w.block(
        w.block(bytes(3) + w.vec("coords", 1, 2, 3) + w.n("scale") + b"\x06" + struct.pack("<f", 1.5))
        + b"\x43" + struct.pack("<H", 4) + b"tall"
        + w.block(bytes(3) + w.vec("coords", 4, 5, 6))
    )
    group = w.n("$grp") + w.n("Tree") + w.n(":") + w.guid(GUIDS[1]) + trees
    child = w.entity("GenericEntity", GUIDS[2], w.vec("coords", 0, 1, 0))
    building = w.entity(
        "SCR_DestructibleBuildingEntity",
        GUIDS[0],
        w.vec("coords", 3.0, 0.5, 4.0)
        + w.vec("angles", 0.0, 90.0, 0.0)
        + w.n("ID") + b"\x0c" + struct.pack("<H", 2) + b"ab"
        + w.n("Enabled") + b"\x0b\x01"
        + w.n("Priority") + b"\x01" + struct.pack("<i", 7)
        + w.n("Flags") + b"\x02" + struct.pack("<q", 0)
        + w.n("LineColor") + b"\x09" + struct.pack("<4f", 1, 0, 0, 1)
        + w.block(child),
        name="house",
    )
    return w.bytes(group + building)


class TestWorldFile:
    def test_entities_groups_and_children(self):
        world = read_world(world_bytes())
        assert [e.cls for e in world.entities] == ["Tree", "Tree", "SCR_DestructibleBuildingEntity", "GenericEntity"]
        first, second, house, door = world.entities
        assert first.prefab == GUIDS[1] and first.props == {"coords": (1, 2, 3), "scale": 1.5}
        assert second.name == "tall" and second.props["coords"] == (4, 5, 6)
        assert house.name == "house" and house.prefab == GUIDS[0]
        assert house.props["ID"] == "ab" and house.props["Enabled"] == 1 and house.props["Priority"] == 7
        assert house.props["LineColor"] == (1, 0, 0, 1)
        assert door.parent == 2 and house.parent is None
        assert not world.unread

    def test_a_block_length_that_does_not_close_is_refused(self):
        data = bytearray(world_bytes())
        data += b"\x00"
        with pytest.raises(EnfusionError):
            read_world(bytes(data))


class TestResources:
    def test_the_database_maps_guids_to_paths(self):
        found = parse_rdb(rdb({"Prefabs/A.et": GUIDS[0], "Assets/B.xob": GUIDS[1]}))
        assert found == {GUIDS[0]: "Prefabs/A.et", GUIDS[1]: "Assets/B.xob"}

    def test_a_prefab_inherits_its_model_and_flags(self):
        fs = _Files(
            {
                "Prefabs/Base.et": b'GenericEntity {\n Flags 2251799813685248\n components {\n  MeshObject "{AAAAAAAAAAAAAAAA}" {\n   Object "{BBBBBBBBBBBBBBBB}Assets/M.xob"\n  }\n }\n}\n',
                "Prefabs/Child.et": b'GenericEntity : "{CCCCCCCCCCCCCCCC}Prefabs/Base.et" {\n ID "1"\n}\n',
            }
        )
        prefab = Prefabs(fs).get("Prefabs/Child.et")
        assert prefab.model == "Assets/M.xob" and prefab.flags == 1 << 51

    def test_a_model_keeps_its_box(self):
        low, high = xob_bounds(xob((-1, 0, -2), (1, 3, 2)))
        assert low.tolist() == [-1, 0, -2] and high.tolist() == [1, 3, 2]

    def test_yaw_turns_north_towards_east(self):
        turned = np.array([0.0, 0.0, 1.0]) @ rotation((0.0, 90.0, 0.0))
        assert np.allclose(turned, (1.0, 0.0, 0.0))
        assert np.allclose(np.array([1.0, 0.0, 0.0]) @ rotation((0.0, 90.0, 0.0)), (0.0, 0.0, -1.0))


# --------------------------------------------------------------------------
# A whole world


def install(tmp_path: Path) -> Path:
    files = terrain_files()
    files["worlds/Isle/Isle.ent"] = world_bytes()
    files["Prefabs/House.et"] = b'SCR_DestructibleBuildingEntity {\n Flags 0\n components {\n  MeshObject "{AAAAAAAAAAAAAAAA}" {\n   Object "{BBBBBBBBBBBBBBBB}Assets/House.xob"\n  }\n }\n}\n'
    files["Prefabs/Tree.et"] = b'Tree {\n components {\n  MeshObject "{AAAAAAAAAAAAAAAA}" {\n   Object "{BBBBBBBBBBBBBBBB}Assets/Vegetation/T.xob"\n  }\n }\n}\n'
    files["Assets/House.xob"] = xob((-2.0, 0.0, -1.0), (2.0, 3.0, 1.0))
    files["Assets/Vegetation/T.xob"] = xob((-1.0, 0.0, -1.0), (1.0, 8.0, 1.0))
    addon = tmp_path / "addons" / "data"
    addon.mkdir(parents=True)
    (addon / "data.pak").write_bytes(pak(files))
    (addon / "resourceDatabase.rdb").write_bytes(rdb({"Prefabs/House.et": GUIDS[0], "Prefabs/Tree.et": GUIDS[1]}))
    return tmp_path


def glb_json(path: Path) -> dict:
    data = path.read_bytes()
    (length,) = struct.unpack_from("<I", data, 12)
    return json.loads(data[20 : 20 + length])


class TestExport:
    def test_ground_water_and_a_house_on_the_ground(self, tmp_path):
        root = install(tmp_path)
        out = tmp_path / "isle.glb"
        report = export_world(root, "Isle", out, ground_spacing=1.0, texture=64, log=lambda *_: None)
        nodes = [n["name"] for n in glb_json(out)["nodes"]]
        assert "ground:Isle" in nodes and "structure:Isle" in nodes
        assert report.terrain.mismatches == 0 and report.texture is not None
        # Two trees left out by default, one house placed; its door is a child and is not.
        assert report.structures == 1
        assert report.skipped.get("tree (--trees adds them)") == 2

    def test_a_relative_height_is_measured_from_the_ground(self, tmp_path):
        root = install(tmp_path)
        fs = FileSystem.of_install(root)
        terrain = read_terrain(fs, "worlds/Isle/Terrain/Terrain.terr")
        world = read_world(fs.read(world_file(fs, "Isle")))
        placed = place_structures(world, terrain, fs, resource_paths(root))
        (house,) = placed
        # No absolute flag: y 0.5 is above the ground at (3, 4); the box's floor is there.
        assert house.corners[:, 1].min() == pytest.approx(ground(3.0, 4.0) + 0.5, abs=1e-4)
        # Turned a quarter: its 4 m length now runs north-south.
        extent = house.corners.max(0) - house.corners.min(0)
        assert extent[2] == pytest.approx(4.0) and extent[0] == pytest.approx(2.0)


# --------------------------------------------------------------------------
# On the installed game

INSTALL = find_install()


@pytest.fixture(scope="module")
def smallest():
    """The installed game's smallest world that has a world file, by its number of terrain tiles."""
    fs = FileSystem.of_install(INSTALL)
    worlds = [(w, t) for w, t in list_worlds(fs) if world_file(fs, w)]
    sizes = {w: len(fs.find(t.rsplit("/", 1)[0] + "/.data/", ".ttile")) for w, t in worlds}
    world = min((w for w in sizes if sizes[w] > 16), key=lambda w: sizes[w])
    return fs, world, dict(worlds)[world]


@pytest.mark.skipif(INSTALL is None, reason="Arma Reforger is not installed")
class TestTheInstalledGame:
    def test_every_shared_tile_edge_agrees(self, smallest):
        fs, _world, terr = smallest
        terrain = read_terrain(fs, terr)
        assert terrain.mismatches == 0 and terrain.shared > 10_000

    def test_the_world_file_parses_and_its_objects_stand_on_the_ground(self, smallest):
        fs, world, terr = smallest
        terrain = read_terrain(fs, terr)
        parsed = read_world(fs.read(world_file(fs, world)))
        assert len(parsed.entities) > 10_000
        absolute = [
            e.props["coords"]
            for e in parsed.entities
            if e.parent is None and "coords" in e.props and (e.props.get("Flags") or 0) & (1 << 51)
        ]
        p = np.array(absolute)
        off = p[:, 1] - terrain.height_at(p[:, 0], p[:, 2])
        assert np.median(np.abs(off)) < 0.1
