"""
Unreal 5 World Partition maps: the landscape read from its components'
heightmaps, static meshes in the 5.3-5.5 layout and inside a map package,
and the water laid on the ground.

Built to the layouts the readers were settled on against a shipped game (see
`unreallandscape.py`, `unreallevel.py`); where that game is installed, also
checked on its archives.
"""

from __future__ import annotations

import struct

import numpy as np
import pytest

from heat3d_gamefiles.unreallandscape import LandscapeError, read_landscape
from heat3d_gamefiles.unreallevel import _bounds_hold, find_paks, ground_mesh, list_maps, map_name, to_viewer, water_surface
from heat3d_gamefiles.unrealmesh import read_static_mesh
from heat3d_gamefiles.zen import Package

from .unreal_fixtures import fstring, unversioned, zen_package

SCRIPT = 1 << 62
CLASSES = {
    1: "/Script/Landscape.Landscape",
    2: "/Script/Engine.SceneComponent",
    3: "/Script/Landscape.LandscapeComponent",
    4: "/Script/Engine.Texture2D",
    5: "/Script/Engine.StaticMesh",
    6: "/Script/Engine.BodySetup",
}


class _Scripts:
    def path(self, index: int) -> str:
        return CLASSES[index & ((1 << 62) - 1)]


def _package(names, exports, bulk=()) -> Package:
    return Package(zen_package(names, exports, bulk=bulk), "map", _Scripts())


# --------------------------------------------------------------------------
# Landscape

SIZE, SUB, COUNT = 4, 2, 2  # a component of two 2-quad subsections
SPAN = COUNT * (SUB + 1)  # its texels each way


def _height(gx: int, gy: int) -> float:
    """Landscape units at a vertex of the landscape's own grid; multiples of 1/128 store exactly."""
    return gx * 1.5 - gy * 0.25 + 3.0


def _texel_vertex(t: int) -> int:
    part, within = t // (SUB + 1), t % (SUB + 1)
    return part * SUB + within


def _heightmap(sections: list[tuple[int, int]], width: int) -> bytes:
    """One BGRA heightmap holding the components side by side, red the high byte, green the low."""
    pixels = np.zeros((SPAN, width, 4), dtype=np.uint8)
    for n, (sx, sy) in enumerate(sections):
        for ty in range(SPAN):
            for tx in range(SPAN):
                value = int(round(32768 + 128 * _height(sx + _texel_vertex(tx), sy + _texel_vertex(ty))))
                pixels[ty, n * SPAN + tx] = (0, value & 0xFF, value >> 8, 0)
    return pixels.tobytes()


def _landscape_package(sections, *, corrupt: bool = False, decoy: bool = True) -> Package:
    names = ["None", "Landscape", "RootComponent0", "LandscapeComponent", "Heightmap_0", "PF_B8G8R8A8"]
    width = SPAN * len(sections)
    pixels = bytearray(_heightmap(sections, width))
    if corrupt:  # one texel of the second component's shared left edge
        at = (1 * width + SPAN) * 4
        pixels[at + 1] ^= 0x7F
    head = bytes(8) + struct.pack("<iii", width, SPAN, 0) + fstring("PF_B8G8R8A8")
    head += struct.pack("<ii", 0, 1) + struct.pack("<iiii", 0, width, SPAN, 1)
    texture = head + bytes(pixels)
    root = unversioned([5, 7]) + struct.pack("<3d", 1000.0, 2000.0, 300.0) + struct.pack("<3d", 50.0, 50.0, 100.0)
    exports = [
        {"name": 1, "cls": SCRIPT | 1, "data": b""},
        {"name": 2, "cls": SCRIPT | 2, "data": root, "outer": 0},
        {"name": 4, "cls": SCRIPT | 4, "data": texture},
    ]
    for n, (sx, sy) in enumerate(sections):
        body = unversioned([0, 1, 2, 3, 4, 11, 13, 19]) + struct.pack("<5i", sx, sy, SIZE, SUB, COUNT)
        if decoy:  # the weightmap's scale and bias: half a texel off, never taken for the heightmap's
            body += struct.pack("<4d", 1 / width, 1 / SPAN, 0.5 / width, 0.5 / SPAN)
        body += struct.pack("<4d", 1 / width, 1 / SPAN, n * SPAN / width, 0.0)
        body += struct.pack("<i", 3)  # the heightmap: export 3, counted from one
        exports.append({"name": 3, "cls": SCRIPT | 3, "data": body, "outer": 0})
    return _package(names, exports, bulk=[(len(head), len(pixels), 0x40)])


class TestLandscape:
    def test_components_are_assembled_into_one_grid(self):
        land = read_landscape(None, _landscape_package([(0, 0), (SIZE, 0)]))
        assert land.components == 2 and land.mismatches == 0 and not land.unread
        assert land.heights.shape == (SIZE + 1, 2 * SIZE + 1)
        expected = np.array([[_height(x, y) for x in range(2 * SIZE + 1)] for y in range(SIZE + 1)])
        assert np.array_equal(land.heights, expected.astype(np.float32))
        # The repeated subsection edges and the shared component edge were all compared.
        assert land.shared > 0

    def test_world_positions_follow_the_landscape_actor(self):
        land = read_landscape(None, _landscape_package([(0, 0), (SIZE, 0)]))
        grid, mask = land.world(1)
        assert mask.all()
        assert np.allclose(grid[0, 0], (1000.0, 2000.0, 300.0 + 100.0 * _height(0, 0)))
        assert np.allclose(grid[2, 3], (1000.0 + 3 * 50.0, 2000.0 + 2 * 50.0, 300.0 + 100.0 * _height(3, 2)))

    def test_a_disagreeing_shared_vertex_is_counted_not_hidden(self):
        land = read_landscape(None, _landscape_package([(0, 0), (SIZE, 0)], corrupt=True))
        assert land.mismatches == 1

    def test_a_map_without_a_landscape_actor_is_refused(self):
        with pytest.raises(LandscapeError):
            read_landscape(None, _package(["None", "X"], [{"name": 1, "cls": SCRIPT | 2, "data": b""}]))

    def test_the_ground_is_two_triangles_a_cell(self):
        land = read_landscape(None, _landscape_package([(0, 0), (SIZE, 0)]))
        positions, faces = ground_mesh(*land.world(1))
        assert len(positions) == (SIZE + 1) * (2 * SIZE + 1) and len(faces) == 2 * SIZE * 2 * SIZE


# --------------------------------------------------------------------------
# Static meshes


def _mesh_native(body: int, *, bounds: bool) -> bytes:
    """A cooked, non-Nanite mesh with one level of one triangle."""
    out = bytes(4) + struct.pack("<H", 0) + struct.pack("<Iii", 1, body, 0) + bytes(16) + struct.pack("<ii", 0, 1)
    out += struct.pack("<H", 0x0C00) + struct.pack("<i", 1)  # strip flags: no reversed or depth-only buffers
    out += struct.pack("<iIIII", 0, 0, 1, 0, 2) + bytes(20)
    if bounds:
        out += struct.pack("<7d", 0.5, 0.5, 0.0, 0.5, 0.5, 0.0, 0.8)
    out += struct.pack("<f", 0.0) + struct.pack("<III", 0, 1, 0) + struct.pack("<H", 0)
    positions = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    out += struct.pack("<II", 12, 3) + struct.pack("<ii", 12, 3) + positions
    out += struct.pack("<H", 0) + struct.pack("<IIII", 1, 3, 1, 0)
    out += struct.pack("<ii", 8, 3) + bytes(24)  # tangents
    out += struct.pack("<ii", 8, 3) + struct.pack("<6f", 0, 0, 1, 0, 0, 1)  # UVs
    out += struct.pack("<H", 0) + struct.pack("<II", 0, 0)  # no colours
    out += struct.pack("<I", 0) + struct.pack("<ii", 2, 3) + struct.pack("<3H", 0, 1, 2) + struct.pack("<I", 0)
    out += struct.pack("<I", 0) + struct.pack("<ii", 2, 0) + struct.pack("<I", 0)  # one more index buffer
    out += (struct.pack("<ii", 0, 0) + struct.pack("<f", 0.0)) * 2 + bytes(12)
    return out


class TestStaticMeshes:
    @pytest.mark.parametrize("bounds", [True, False], ids=["5.6 layout", "5.3-5.5 layout"])
    def test_a_level_reads_with_or_without_its_bounds(self, bounds):
        names = ["None", "StaticMesh_0", "BodySetup_0", "Other"]
        exports = [
            {"name": 3, "cls": SCRIPT | 6, "data": b""},  # a body setup of something else, listed first
            {"name": 1, "cls": SCRIPT | 5, "data": _mesh_native(3, bounds=bounds)},
            {"name": 2, "cls": SCRIPT | 6, "data": b"", "outer": 1},
        ]
        package = _package(names, exports)
        mesh = read_static_mesh(package, export=package.exports[1])
        lod = mesh.lods[0]
        assert lod.faces.tolist() == [[0, 1, 2]]
        assert np.allclose(lod.positions[1], (1, 0, 0))


# --------------------------------------------------------------------------
# Water and HLOD


class TestWaterAndHlod:
    def _grid(self, n=11, spacing=100.0, height=0.0):
        grid = np.zeros((n, n, 3))
        grid[..., 0] = np.arange(n)[None, :] * spacing
        grid[..., 1] = np.arange(n)[:, None] * spacing
        grid[..., 2] = height
        return grid, np.ones((n, n), dtype=bool)

    def test_water_is_kept_only_where_it_stands_above_the_ground(self):
        grid, mask = self._grid()
        grid[:, 5:, 2] = 500.0  # a bank across the east half
        tri = np.array([[-1, -1, 200], [2001, -1, 200], [-1, 2001, 200]], dtype=np.float32)
        p, f = water_surface(grid, mask, [("lake", tri, np.array([[0, 1, 2]]))])
        assert len(f) and np.allclose(p[:, 2], 200.0)
        # Nothing reaches past the first cell that climbs the bank.
        assert p[:, 0].max() <= 500.0

    def test_no_water_under_the_ground(self):
        grid, mask = self._grid(height=1000.0)
        tri = np.array([[0, 0, 200], [1000, 0, 200], [0, 1000, 200]], dtype=np.float32)
        p, f = water_surface(grid, mask, [("lake", tri, np.array([[0, 1, 2]]))])
        assert len(f) == 0

    def test_a_mesh_is_kept_when_the_component_s_bounds_describe_it(self):
        positions = np.array([[0, 0, 0], [10, 20, 4]], dtype=np.float32)
        record = bytes(5) + struct.pack("<7d", 5.0, 10.0, 2.0, 5.0, 10.0, 2.0, 11.4) + bytes(3)
        assert _bounds_hold(record, positions)
        assert not _bounds_hold(record, positions + 500.0)

    def test_the_viewer_frame_swaps_y_and_z(self):
        assert to_viewer(np.array([[1.0, 2.0, 3.0]])).tolist() == [[1.0, 3.0, 2.0]]

    def test_map_names_drop_the_world_partition_suffix(self):
        assert map_name("../../../G/Content/Maps/A/A_Persistent_WP.umap") == "A"
        assert map_name("../../../G/Content/Maps/B.umap") == "B"


# --------------------------------------------------------------------------
# On the installed game

PAKS = find_paks("Hell Let Loose - Vietnam")


@pytest.mark.skipif(PAKS is None, reason="Hell Let Loose: Vietnam is not installed")
class TestTheInstalledGame:
    def test_a_map_s_landscape_reads_whole_and_its_shared_vertices_agree(self):
        from heat3d_gamefiles.iostore import Store
        from heat3d_gamefiles.zen import Packages

        store = Store(PAKS)
        packages = Packages(store)
        maps = [m for m in list_maps(store) if "persistent" in m.lower()]
        assert maps
        land = read_landscape(packages, packages.open(maps[0]))
        assert land.components > 100 and not land.unread
        assert land.mismatches < 0.01 * land.shared
