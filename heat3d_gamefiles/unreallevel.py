"""
A whole Unreal 5 World Partition map out of a shipped build, as the viewer's
level contract: `ground:<Map>`, `structure:<Map>` and `water:<Map>`.

A World Partition map is a persistent package (`<Map>.umap`) and cooked cells
under `<Map>/_Generated_/`. What this reads is all in the persistent package:

- **ground** - the landscape, from its components' heightmaps
  (`unreallandscape.py`), exact to the landscape's own vertex spacing and
  drawn at `ground_spacing`;
- **structure** - the map's merged HLOD meshes: what the engine draws for a
  whole cell of buildings and props at a distance, built in world space and
  stored in the persistent package. They are simplified stand-ins, not the
  full-detail models the cells place, and are kept only when the mesh lies
  where the component that draws it says it does;
- **water** - each water body's water-info mesh, the outline of its surface
  that the water plugin renders from. Built in world space too.

Coordinates are Unreal's centimetres with Y and Z swapped, the same frame the
editor exporter (`exporters/unreal`) writes, so telemetry from the same game
in Unreal units lies on it with the viewer's default mapping.

Not read: the cells' full-detail placed models (their components' property
layout is the build's own and is not calibrated here), foliage, decals, and
landscape materials. The ground is drawn untextured; the viewer shades it.
"""

from __future__ import annotations

import re
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .iostore import Store
from .unrealmesh import MeshError, read_static_mesh
from .unreallandscape import Landscape, LandscapeError, read_landscape
from .unversioned import read_header
from .zen import Package, Packages

_HLOD_ACTOR = "/Script/Engine.WorldPartitionHLOD"
_SMC = "/Script/Engine.StaticMeshComponent"
_WATER_MESH = re.compile(r"^WaterInfoMesh(_\d+)?$")


def find_paks(where: str | Path | None) -> Path | None:
    """
    A game's `Content/Paks` folder holding IoStore containers: the folder
    itself, anywhere under a game folder, or a game folder of that name in a
    Steam library.
    """
    candidates: list[Path] = []
    if where:
        path = Path(where)
        if path.exists():
            candidates.append(path)
        else:
            from .forzainstall import STEAM_DEFAULTS, steam_libraries

            for library in [Path(p) for p in STEAM_DEFAULTS] + [Path(p) for p in steam_libraries()]:
                candidates.append(library / "steamapps" / "common" / str(where))
    for folder in candidates:
        if not folder.is_dir():
            continue
        if any(folder.glob("*.utoc")):
            return folder
        for paks in sorted(folder.glob("*/Content/Paks")) + sorted(folder.glob("Content/Paks")):
            if any(paks.glob("*.utoc")):
                return paks
    return None


def list_maps(store: Store) -> list[str]:
    """Every World Partition map: a `.umap` with cooked cells beside it, by its file path."""
    with_cells = {p.split("/_generated_/")[0] for p in store.files if "/_generated_/" in p}
    return sorted(
        (store.names.get(p, p) for p in store.files if p.endswith(".umap") and p[:-5] in with_cells),
        key=str.lower,
    )


def map_name(path: str) -> str:
    """`.../Maps/X/X_Persistent_WP.umap` -> `X`: the map's file name without World Partition suffixes."""
    stem = path.rsplit("/", 1)[-1][:-5]
    return re.sub(r"(_persistent)?(_wp)?$", "", stem, flags=re.I) or stem


def find_map(store: Store, wanted: str) -> str:
    maps = list_maps(store)
    exact = [m for m in maps if map_name(m).lower() == wanted.lower() or m.rsplit("/", 1)[-1][:-5].lower() == wanted.lower()]
    if len(exact) == 1:
        return exact[0]
    partial = [m for m in maps if wanted.lower() in m.lower()]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise LookupError(f"no World Partition map matches {wanted!r}; there are: " + ", ".join(map_name(m) for m in maps))
    raise LookupError(f"{wanted!r} matches several maps: " + ", ".join(map_name(m) for m in partial))


@dataclass
class MapReport:
    name: str
    ground_triangles: int = 0
    structure_meshes: int = 0
    structure_triangles: int = 0
    water_bodies: int = 0
    water_triangles: int = 0
    landscape: Landscape | None = None
    skipped: dict[str, int] = field(default_factory=dict)

    def skip(self, reason: str) -> None:
        self.skipped[reason] = self.skipped.get(reason, 0) + 1


def ground_grid(landscape: Landscape, spacing_cm: float) -> tuple[np.ndarray, np.ndarray]:
    """The landscape's vertices at the step nearest `spacing_cm`, Unreal world cm, and where there is ground."""
    step = max(1, int(round(spacing_cm / max(abs(landscape.scale[0]), 1e-6))))
    return landscape.world(step)


def ground_mesh(grid: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """A grid of vertices as triangles, two per cell whose four corners are ground."""
    ny, nx = mask.shape
    index = np.arange(ny * nx).reshape(ny, nx)
    a, b = index[:-1, :-1], index[:-1, 1:]
    c, d = index[1:, :-1], index[1:, 1:]
    keep = mask[:-1, :-1] & mask[:-1, 1:] & mask[1:, :-1] & mask[1:, 1:]
    faces = np.concatenate(
        [np.stack([a[keep], c[keep], b[keep]], 1), np.stack([b[keep], c[keep], d[keep]], 1)]
    )
    return grid.reshape(-1, 3).astype(np.float32), faces.astype(np.int64)


def _first_reference(data: bytes) -> int | None:
    """The first value of a property block, when it is the only object reference wanted: slot 4 of a static-mesh component."""
    present, at = read_header(data, 0)
    if not present or present[0][1]:
        return None
    return struct.unpack_from("<i", data, at)[0]


def hlod_meshes(package: Package, report: MapReport) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """
    Every merged HLOD mesh the map stores, in world cm. The mesh a component
    draws is its static-mesh slot, the first value of its block. A mesh is
    kept only if the world bounds the component caches for itself describe
    the mesh's own vertices, so a component that moves its mesh is never
    drawn in the wrong place.
    """
    out = []
    seen: set[int] = set()
    for export in package.exports:
        if package.class_name(export) != _SMC:
            continue
        actor = package.outer_export(export)
        if actor is None or package.class_name(actor) != _HLOD_ACTOR:
            continue
        data = package.export_data(export)
        try:
            reference = _first_reference(data)
        except (struct.error, IndexError):
            reference = None
        if not reference or reference <= 0 or reference > len(package.exports):
            report.skip("HLOD component without a mesh of its own package")
            continue
        mesh_export = package.exports[reference - 1]
        if not package.class_name(mesh_export).endswith(".StaticMesh"):
            report.skip("HLOD component's first value is not a mesh")
            continue
        if mesh_export.index in seen:
            continue
        try:
            mesh = read_static_mesh(package, export=mesh_export)
        except (MeshError, struct.error, ValueError):
            report.skip("HLOD mesh does not read")
            continue
        lod = mesh.lods[0]
        if not _bounds_hold(data, lod.positions):
            report.skip("HLOD mesh not where its component's bounds say")
            continue
        seen.add(mesh_export.index)
        out.append((mesh_export.name, lod.positions.astype(np.float32), lod.faces))
    return out


def _bounds_hold(data: bytes, positions: np.ndarray) -> bool:
    """
    Whether the component's cached world bounds (origin, extent, radius as
    doubles, somewhere in its block) describe these vertices: the vertices'
    own box centre and half-size match one such record to a centimetre.
    """
    low, high = positions.min(0).astype(np.float64), positions.max(0).astype(np.float64)
    centre, half = (low + high) / 2, (high - low) / 2
    for at in range(0, len(data) - 55):
        values = struct.unpack_from("<7d", data, at)
        if all(abs(values[i] - centre[i]) < 2.0 for i in range(3)) and all(abs(values[3 + i] - half[i]) < 2.0 for i in range(3)):
            return True
    return False


def water_meshes(package: Package, report: MapReport) -> list[tuple[str, np.ndarray, np.ndarray]]:
    """Each water body's water-info mesh (not the dilated copy beside it), world cm."""
    out = []
    for export in package.exports:
        if not _WATER_MESH.match(export.name) or not package.class_name(export).endswith(".StaticMesh"):
            continue
        try:
            mesh = read_static_mesh(package, export=export)
        except (MeshError, struct.error, ValueError):
            report.skip("water mesh does not read")
            continue
        lod = mesh.lods[0]
        out.append((export.name, lod.positions.astype(np.float32), lod.faces))
    return out


def water_surface(
    grid: np.ndarray, mask: np.ndarray, bodies: list[tuple[str, np.ndarray, np.ndarray]]
) -> tuple[np.ndarray, np.ndarray]:
    """
    The water bodies laid on the ground grid, kept where the water is above
    the ground. A water body's mesh is its footprint, flat or following its
    river, and reaches under the banks - one lake's runs kilometres past the
    map at its own level - so drawn as stored it would cover hillsides. Each
    grid vertex inside a water triangle takes the water's height there (the
    highest body wins); a cell is water when all four corners are and the
    water stands above the ground at one of them.
    """
    ny, nx = mask.shape
    x0, y0 = grid[0, 0, 0], grid[0, 0, 1]
    dx, dy = grid[0, 1, 0] - x0, grid[1, 0, 1] - y0
    level = np.full((ny, nx), -np.inf)
    for _name, p, faces in bodies:
        tri = p[faces].astype(np.float64)
        for a, b, c in tri:
            lo = np.minimum(np.minimum(a, b), c)
            hi = np.maximum(np.maximum(a, b), c)
            j0, j1 = max(0, int(np.ceil((lo[0] - x0) / dx))), min(nx - 1, int(np.floor((hi[0] - x0) / dx)))
            i0, i1 = max(0, int(np.ceil((lo[1] - y0) / dy))), min(ny - 1, int(np.floor((hi[1] - y0) / dy)))
            if j1 < j0 or i1 < i0:
                continue
            px = x0 + np.arange(j0, j1 + 1) * dx
            py = y0 + np.arange(i0, i1 + 1) * dy
            X, Y = np.meshgrid(px, py)
            det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(det) < 1e-9:
                continue
            u = ((b[1] - c[1]) * (X - c[0]) + (c[0] - b[0]) * (Y - c[1])) / det
            v = ((c[1] - a[1]) * (X - c[0]) + (a[0] - c[0]) * (Y - c[1])) / det
            w = 1.0 - u - v
            inside = (u >= -1e-9) & (v >= -1e-9) & (w >= -1e-9)
            z = u * a[2] + v * b[2] + w * c[2]
            block = level[i0 : i1 + 1, j0 : j1 + 1]
            np.maximum(block, np.where(inside, z, -np.inf), out=block)
    wet = np.isfinite(level)
    above = wet & mask & (level > grid[..., 2])
    keep = wet[:-1, :-1] & wet[:-1, 1:] & wet[1:, :-1] & wet[1:, 1:]
    keep &= above[:-1, :-1] | above[:-1, 1:] | above[1:, :-1] | above[1:, 1:]
    positions = grid.copy()
    positions[..., 2] = np.where(wet, level, grid[..., 2])
    index = np.arange(ny * nx).reshape(ny, nx)
    a, b = index[:-1, :-1], index[:-1, 1:]
    c, d = index[1:, :-1], index[1:, 1:]
    faces = np.concatenate([np.stack([a[keep], c[keep], b[keep]], 1), np.stack([b[keep], c[keep], d[keep]], 1)])
    used = np.unique(faces)
    remap = np.full(ny * nx, -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return positions.reshape(-1, 3)[used].astype(np.float32), remap[faces]


def to_viewer(positions: np.ndarray) -> np.ndarray:
    """Unreal (x, y, z up) cm -> the viewer's Y-up frame, the editor exporter's swap."""
    return np.ascontiguousarray(positions[:, [0, 2, 1]], dtype=np.float32)


def export_map(
    paks: Path,
    wanted: str,
    out: Path,
    *,
    ground_spacing: float = 2.0,
    structures: bool = True,
    water: bool = True,
    log=print,
) -> MapReport:
    from .glb import Part, write_glb

    started = time.time()
    store = Store(paks)
    packages = Packages(store)
    path = find_map(store, wanted)
    name = map_name(path)
    report = MapReport(name)
    package = packages.open(path)
    if package is None:
        raise LandscapeError(f"{path}: the map package does not read")
    log(f"{name}: reading the landscape")
    landscape = read_landscape(packages, package)
    report.landscape = landscape
    grid, mask = ground_grid(landscape, ground_spacing * 100.0)
    ground, ground_faces = ground_mesh(grid, mask)
    report.ground_triangles = len(ground_faces)

    pieces: list[tuple[str, np.ndarray, np.ndarray, tuple[float, float, float]]] = [
        (f"ground:{name}", ground, ground_faces, (0.55, 0.52, 0.45))
    ]
    if structures:
        meshes = hlod_meshes(package, report)
        report.structure_meshes = len(meshes)
        report.structure_triangles = sum(len(f) for _n, _p, f in meshes)
        if meshes:
            pieces.append((f"structure:{name}", *_merge(meshes), (0.75, 0.74, 0.70)))
    if water:
        bodies = water_meshes(package, report)
        report.water_bodies = len(bodies)
        if bodies:
            surface, surface_faces = water_surface(grid, mask, bodies)
            report.water_triangles = len(surface_faces)
            if len(surface_faces):
                pieces.append((f"water:{name}", surface, surface_faces, (0.22, 0.40, 0.55)))

    positions, parts, offset = [], [], 0
    for part_name, p, f, colour in pieces:
        positions.append(to_viewer(p))
        parts.append(Part(part_name, f + offset, colour=colour))
        offset += len(p)
    write_glb(out, np.concatenate(positions), parts=parts)
    log(f"{name}: written in {time.time() - started:.0f} s")
    return report


def _merge(meshes) -> tuple[np.ndarray, np.ndarray]:
    positions, faces, offset = [], [], 0
    for _name, p, f in meshes:
        positions.append(p)
        faces.append(f + offset)
        offset += len(p)
    return np.concatenate(positions), np.concatenate(faces)


# --------------------------------------------------------------------------
# Command line: `ue-maps` and `ue-map`


def add_verbs(sub) -> None:
    where = "the game's folder, its Content/Paks, or a Steam game folder name (e.g. \"Hell Let Loose - Vietnam\")"
    p = sub.add_parser("ue-maps", help="list the World Partition maps of an Unreal 5 game")
    p.add_argument("game", help=where)
    p = sub.add_parser("ue-map", help="export an Unreal 5 World Partition map: landscape, HLOD structures, water")
    p.add_argument("game", help=where)
    p.add_argument("map", help="the map's name as `ue-maps` lists it")
    p.add_argument("-o", "--out", type=Path, default=None, help="the .glb (default: <map>.glb)")
    p.add_argument(
        "--ground-spacing",
        type=float,
        default=2.0,
        metavar="METRES",
        help="the landscape's vertex spacing in the file, rounded to its own grid (default 2)",
    )
    p.add_argument("--no-structures", action="store_true", help="leave out the HLOD buildings and props")
    p.add_argument("--no-water", action="store_true", help="leave out the water bodies")


def run(args) -> int:
    import sys

    paks = find_paks(args.game)
    if paks is None:
        print(f"no Unreal IoStore containers found for {args.game!r}", file=sys.stderr)
        return 2
    if args.verb == "ue-maps":
        store = Store(paks)
        for path in list_maps(store):
            print(f"  {map_name(path):<32} {path}")
        return 0
    out = args.out or Path(f"{_safe(args.map)}.glb")
    try:
        report = export_map(
            paks,
            args.map,
            out,
            ground_spacing=args.ground_spacing,
            structures=not args.no_structures,
            water=not args.no_water,
        )
    except (LookupError, LandscapeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    land = report.landscape
    print(f"{report.name} -> {out}")
    print(
        f"  ground     {report.ground_triangles:>10,} triangles from {land.components} landscape components; "
        f"{land.mismatches:,} of {land.shared:,} vertices stored twice disagree"
    )
    if land.unread:
        print(f"  unread     {land.unread}")
    print(f"  structure  {report.structure_triangles:>10,} triangles in {report.structure_meshes} HLOD meshes")
    print(f"  water      {report.water_triangles:>10,} triangles from {report.water_bodies} water bodies")
    if report.skipped:
        print(f"  skipped    {report.skipped}")
    return 0


def _safe(name: str) -> str:
    return re.sub(r"[^\w.-]+", "_", name).strip("_") or "map"
