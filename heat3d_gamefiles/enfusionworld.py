"""
An Arma Reforger world out of the installed game, as the viewer's level
contract: `ground:<World>`, `structure:<World>` and `water:<World>`.

**Terrain.** `worlds/<World>/.../<Name>.terr` is a form whose `HEAD` gives the
vertex count each way, the vertices of a block, the blocks a tile spans, the
spacing in metres and a height scale and offset. Its tiles are
`.Data/<Name>_<n>.ttile`, numbered row by row; each holds `HGHT`, the tile's
vertices as 16-bit heights, and shares its edge vertices with its neighbours.
Height in metres is `value * scale + offset`. Checked: on both shipped
terrains every shared tile edge agrees exactly (480 edges of 480 on the
smaller), and the placed objects of the world stand on the ground decoded this
way - trees a median 1 cm from it, static models 1 cm - where the transposed
grid puts them 22 m off.

**Colour.** Each tile has `<Name>_<n>_supertexture.edds`, the ground's
colour at about a metre a pixel; laid out like the tiles, it matches the
heights (the sea in it is where the terrain is below zero) and no flip of it
does as well.

**Placement.** The world file (`<World>.ent`) is the binary form of the
editor's entity text, `EBIN`: a table of names, a table of 64-bit resource
GUIDs, then entities. A value is a type byte and its payload; an entity is a
class name, an optional name, an optional `: <prefab>` and a block - `0x0e`
and a 32-bit length that counts itself - of properties, after three zero
bytes. A block with no key inside a property list holds child entities;
`$grp` holds many entities of one class and prefab. The block lengths are what
make it checkable: the whole file parses to its last byte. GUIDs name files
through each addon's `resourceDatabase.rdb`; a prefab (`.et`, text) names its
model through `MeshObject { Object ... }` or inherits it from its parent
prefab.

A position is metres, Y up, the world's own frame. Its height is above sea
level when the entity's flags (its own, or else its prefab's) have bit 51
set, and otherwise above the ground under it: buildings, which carry no flag,
sit a median 0.14 m above the terrain read that way.

**Structures are boxes.** A model (`.xob`) keeps its bounding box in its
`HEAD` chunk, and that box - placed, turned and scaled as the entity is - is
what is drawn. The models' own triangles are compressed in a layout not read
here.

**Water** is the sea: the ground grid where it lies below zero, at zero.
Lakes and rivers (generated from splines in the world file) are not drawn.

Coordinates are left as the game has them - x east, y up, z north, metres -
which is what a recording made in the game reports (`GetOrigin`), so a heat
map lies on the level with the viewer's default mapping. The game's frame is
left-handed; the viewer's *invert world axis* shows it unmirrored without
changing a coordinate.
"""

from __future__ import annotations

import math
import re
import struct
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .enfusion import EnfusionError, FileSystem, find_install, read_edds

_ABSOLUTE_Y = 1 << 51


# --------------------------------------------------------------------------
# Terrain


@dataclass
class Terrain:
    path: str
    spacing: float
    #: Metres, rows along +z, columns along +x, from the world origin.
    heights: np.ndarray
    tiles: tuple[int, int]
    tile_vertices: int
    shared: int = 0
    mismatches: int = 0

    @property
    def size(self) -> tuple[float, float]:
        return ((self.heights.shape[1] - 1) * self.spacing, (self.heights.shape[0] - 1) * self.spacing)

    def height_at(self, x: np.ndarray, z: np.ndarray) -> np.ndarray:
        """Bilinear height at world (x, z); clamped to the terrain's edge."""
        rows, cols = self.heights.shape
        gx = np.clip(np.asarray(x, dtype=np.float64) / self.spacing, 0, cols - 1.000001)
        gz = np.clip(np.asarray(z, dtype=np.float64) / self.spacing, 0, rows - 1.000001)
        i, j = np.floor(gx).astype(int), np.floor(gz).astype(int)
        fx, fz = gx - i, gz - j
        h = self.heights
        return (
            h[j, i] * (1 - fx) * (1 - fz) + h[j, i + 1] * fx * (1 - fz) + h[j + 1, i] * (1 - fx) * fz + h[j + 1, i + 1] * fx * fz
        )


def _form_chunks(data: bytes):
    at = 12
    while at + 8 <= len(data):
        tag, length = struct.unpack_from(">4sI", data, at)
        yield tag, data[at + 8 : at + 8 + length]
        at += 8 + length


def terrain_header(data: bytes) -> tuple[int, int, int, int, float, float, float]:
    if data[:4] != b"FORM" or data[8:12] != b"TERR":
        raise EnfusionError("not a terrain (FORM/TERR)")
    for tag, body in _form_chunks(data):
        if tag == b"HEAD":
            return struct.unpack_from("<4I3f", body, 0)
    raise EnfusionError("terrain without a HEAD")


def tile_heights(data: bytes, vertices: int) -> np.ndarray:
    for tag, body in _form_chunks(data):
        if tag == b"HGHT":
            if len(body) != vertices * vertices * 2:
                raise EnfusionError(f"HGHT of {len(body)} bytes for {vertices} x {vertices} vertices")
            return np.frombuffer(body, dtype="<u2").reshape(vertices, vertices)
    raise EnfusionError("tile without HGHT")


def _tile_name(terr: str, number: int, suffix: str = ".ttile") -> str:
    folder, stem = terr.rsplit("/", 1)
    return f"{folder}/.Data/{stem[:-5]}_{number}{suffix}"


def read_terrain(fs: FileSystem, terr: str) -> Terrain:
    xs, zs, block, blocks, spacing, scale, offset = terrain_header(fs.read(terr))
    vertices = (block - 1) * blocks + 1
    quads = vertices - 1
    if (xs - 1) % quads or (zs - 1) % quads:
        raise EnfusionError(f"{terr}: {xs} x {zs} vertices do not divide into tiles of {quads} quads")
    across, down = (xs - 1) // quads, (zs - 1) // quads
    heights = np.full((zs, xs), np.nan, dtype=np.float32)
    out = Terrain(terr, spacing, heights, (across, down), vertices)
    for row in range(down):
        for col in range(across):
            raw = tile_heights(fs.read(_tile_name(terr, row * across + col)), vertices)
            block_m = (raw * scale + offset).astype(np.float32)
            target = heights[row * quads : row * quads + vertices, col * quads : col * quads + vertices]
            both = np.isfinite(target)
            out.shared += int(both.sum())
            out.mismatches += int(np.count_nonzero(target[both] != block_m[both]))
            target[...] = block_m
    return out


def colour_map(fs: FileSystem, terrain: Terrain, largest: int) -> np.ndarray | None:
    """The tiles' supertextures laid out as one RGB image, row 0 at z = 0, no larger than `largest`."""
    from PIL import Image

    across, down = terrain.tiles
    pieces = {}
    for row in range(down):
        for col in range(across):
            name = _tile_name(terrain.path, row * across + col, "_supertexture.edds")
            if name not in fs:
                return None
            pieces[row, col] = read_edds(fs.read(name))[..., :3]
    side = pieces[0, 0].shape[0]
    scale = min(1.0, largest / (side * max(across, down)))
    cell = max(1, int(round(side * scale)))
    image = np.zeros((cell * down, cell * across, 3), dtype=np.uint8)
    for (row, col), pixels in pieces.items():
        if cell != side:
            pixels = np.asarray(Image.fromarray(pixels).resize((cell, cell), Image.BILINEAR))
        image[row * cell : (row + 1) * cell, col * cell : (col + 1) * cell] = pixels
    return image


def list_worlds(fs: FileSystem) -> list[tuple[str, str]]:
    """(world, terrain path) for every world with a terrain: the folder under `worlds/` that holds both."""
    out = []
    for terr in fs.find("worlds/", ".terr"):
        parts = terr.split("/")
        world = "/".join(parts[1:-2]) if parts[-2].lower() in ("terrain", parts[-1][:-5].lower()) else "/".join(parts[1:-1])
        out.append((world, terr))
    return out


def find_world(fs: FileSystem, wanted: str) -> tuple[str, str]:
    worlds = list_worlds(fs)
    for world, terr in worlds:
        if world.lower() == wanted.lower():
            return world, terr
    raise LookupError(f"no world {wanted!r}; there are: " + ", ".join(w for w, _ in worlds))


def world_file(fs: FileSystem, world: str) -> str | None:
    """`worlds/<World>/<Last>.ent`, the world itself rather than a scenario built on it."""
    stem = world.rsplit("/", 1)[-1]
    path = f"worlds/{world}/{stem}.ent"
    return path if path in fs else None


# --------------------------------------------------------------------------
# EBIN


@dataclass
class Entity:
    cls: str
    prefab: str | None
    name: str | None
    props: dict
    parent: int | None


@dataclass
class World:
    names: list[str]
    guids: list[str]
    entities: list[Entity] = field(default_factory=list)
    #: Values of a type this does not read, by key: the rest of that entity's properties are not read.
    unread: dict[str, int] = field(default_factory=dict)


class _Ebin:
    def __init__(self, data: bytes) -> None:
        if data[:4] != b"EBIN":
            raise EnfusionError("not a binary entity file (EBIN)")
        self.d = data
        count, guids = struct.unpack_from("<HH", data, 8)
        at = 12
        names = []
        for _ in range(count):
            (length,) = struct.unpack_from("<H", data, at)
            names.append(data[at + 2 : at + 2 + length].decode("utf-8", "replace"))
            at += 2 + length
        ids = [data[at + 8 * i : at + 8 * i + 8][::-1].hex().upper() for i in range(guids)]
        self.world = World(names, ids)
        self.start = at + 8 * guids

    def _u16(self, at: int) -> int:
        return struct.unpack_from("<H", self.d, at)[0]

    def _name(self, at: int) -> tuple[str, int]:
        if self.d[at] != 0x0D:
            raise EnfusionError(f"expected a name at {at}, found {self.d[at]:#04x}")
        return self.world.names[self._u16(at + 1)], at + 3

    def _label(self, at: int) -> tuple[str | None, int]:
        if self.d[at] == 0x43:
            length = self._u16(at + 1)
            return self.d[at + 3 : at + 3 + length].decode("utf-8", "replace"), at + 3 + length
        return None, at

    def _header(self, at: int):
        cls, at = self._name(at)
        name, at = self._label(at)
        prefab = None
        if self.d[at] == 0x0D and self.world.names[self._u16(at + 1)] == ":":
            if self.d[at + 3] != 0x05:
                raise EnfusionError(f"a prefab that is not a resource at {at}")
            prefab = self.world.guids[self._u16(at + 4)]
            at += 6
        return cls, name, prefab, at

    def _block(self, at: int) -> tuple[int, int]:
        if self.d[at] != 0x0E:
            raise EnfusionError(f"expected a block at {at}, found {self.d[at]:#04x}")
        (size,) = struct.unpack_from("<I", self.d, at + 1)
        end = at + 1 + size
        if end > len(self.d):
            raise EnfusionError(f"a block at {at} runs past the file")
        return at + 5, end

    def _props(self, at: int, end: int, me: int) -> dict:
        d, out = self.d, {}
        while at < end:
            if d[at] == 0x0E:
                inner, stop = self._block(at)
                self.entities(inner, stop, me)
                at = stop
                continue
            key, at = self._name(at)
            kind = d[at]
            if kind == 0x08:
                out[key] = struct.unpack_from("<3f", d, at + 1)
                at += 13
            elif kind == 0x06:
                out[key] = struct.unpack_from("<f", d, at + 1)[0]
                at += 5
            elif kind == 0x01:
                out[key] = struct.unpack_from("<i", d, at + 1)[0]
                at += 5
            elif kind == 0x02:
                out[key] = struct.unpack_from("<q", d, at + 1)[0]
                at += 9
            elif kind == 0x09:
                out[key] = struct.unpack_from("<4f", d, at + 1)
                at += 17
            elif kind == 0x0B:
                out[key] = d[at + 1]
                at += 2
            elif kind == 0x0C:
                length = self._u16(at + 1)
                out[key] = d[at + 3 : at + 3 + length].decode("utf-8", "replace")
                at += 3 + length
            elif kind == 0x05:
                out[key] = self.world.guids[self._u16(at + 1)]
                at += 3
            elif kind == 0x0E:
                _inner, at = self._block(at)
            else:
                self.world.unread[key] = self.world.unread.get(key, 0) + 1
                break
        return out

    def _one(self, at: int, cls: str, name: str | None, prefab: str | None, parent: int | None) -> int:
        inner, end = self._block(at)
        me = len(self.world.entities)
        self.world.entities.append(Entity(cls, prefab, name, {}, parent))
        self.world.entities[me].props = self._props(inner + 3, end, me)
        return end

    def entities(self, at: int, end: int, parent: int | None = None) -> int:
        while at < end:
            cls, after = self._name(at)
            if cls == "$grp":
                cls, _name, prefab, after = self._header(after)
                inner, stop = self._block(after)
                while inner < stop:
                    name, inner = self._label(inner)
                    inner = self._one(inner, cls, name, prefab, parent)
                at = stop
            else:
                cls, name, prefab, after = self._header(at)
                at = self._one(after, cls, name, prefab, parent)
        if at != end:
            raise EnfusionError(f"entities end at {at}, their block at {end}")
        return at


def read_world(data: bytes) -> World:
    reader = _Ebin(data)
    reader.entities(reader.start, len(data))
    return reader.world


# --------------------------------------------------------------------------
# Resources, prefabs and models


def resource_paths(install: Path) -> dict[str, str]:
    """Resource GUID (16 hex digits) -> path, from every addon's `resourceDatabase.rdb`."""
    out: dict[str, str] = {}
    for rdb in sorted((install / "addons").glob("*/resourceDatabase.rdb")):
        data = rdb.read_bytes()
        out.update(parse_rdb(data))
    return out


def parse_rdb(data: bytes) -> dict[str, str]:
    """
    The entries of a resource database: a 32-bit length counting the NUL, the
    path and its NUL, six bytes, then the GUID (8 bytes, little-endian).
    """
    out = {}
    for match in re.finditer(rb"([\x20-\x7e]{3,1024})\x00", data):
        start = match.start(1)
        if start < 4:
            continue
        (length,) = struct.unpack_from("<I", data, start - 4)
        if length != len(match.group(1)) + 1 or match.end() + 14 > len(data):
            continue
        guid = data[match.end() + 6 : match.end() + 14][::-1].hex().upper()
        out[guid] = match.group(1).decode("ascii")
    return out


_PARENT = re.compile(r'^\s*\w+\s*:\s*"\{[0-9A-Fa-f]{16}\}([^"]+)"')
_MODEL = re.compile(r'MeshObject\s+"\{[0-9A-Fa-f]{16}\}"\s*\{\s*Object\s+"\{[0-9A-Fa-f]{16}\}([^"]+\.xob)"', re.S)
_FLAGS = re.compile(r"^ Flags (\d+)\s*$", re.M)


@dataclass
class Prefab:
    model: str | None
    flags: int | None


class Prefabs:
    """Prefabs by path, each followed up its chain of parents for a model and flags."""

    def __init__(self, fs: FileSystem) -> None:
        self.fs = fs
        self._cache: dict[str, Prefab] = {}

    def get(self, path: str, depth: int = 0) -> Prefab:
        key = path.lower()
        if key in self._cache:
            return self._cache[key]
        self._cache[key] = Prefab(None, None)
        try:
            text = self.fs.read(path).decode("utf-8", "replace")
        except (FileNotFoundError, EnfusionError):
            return self._cache[key]
        model = _MODEL.search(text)
        flags = _FLAGS.search(text)
        found = Prefab(model.group(1) if model else None, int(flags.group(1)) if flags else None)
        parent = _PARENT.match(text)
        if parent and depth < 16 and (found.model is None or found.flags is None):
            above = self.get(parent.group(1), depth + 1)
            found = Prefab(found.model or above.model, found.flags if found.flags is not None else above.flags)
        self._cache[key] = found
        return found


def xob_bounds(data: bytes) -> tuple[np.ndarray, np.ndarray]:
    """A model's own bounding box (metres, model space) from its `HEAD`."""
    if data[:4] != b"FORM" or data[8:12] != b"XOB9":
        raise EnfusionError("not a model (FORM/XOB9)")
    for tag, body in _form_chunks(data):
        if tag == b"HEAD":
            values = np.array(struct.unpack_from("<6f", body, 4), dtype=np.float64)
            low, high = values[:3], values[3:]
            if not (np.all(np.isfinite(values)) and np.all(high >= low)):
                raise EnfusionError("a model's bounds are not a box")
            return low, high
    raise EnfusionError("a model without HEAD")


def rotation(angles) -> np.ndarray:
    """
    `angles` (degrees: about x, about y, about z) as a matrix for row vectors.
    Yaw turns +z (north) towards +x (east), as a compass does; then pitch and
    roll, applied first, about the model's own x and z.
    """
    pitch, yaw, roll = (math.radians(a) for a in angles)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    about_y = np.array([[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]])
    about_x = np.array([[1, 0, 0], [0, cp, sp], [0, -sp, cp]])
    about_z = np.array([[cr, sr, 0], [-sr, cr, 0], [0, 0, 1]])
    return about_z @ about_x @ about_y


_BOX_FACES = np.array(
    [
        [0, 2, 1], [1, 2, 3], [4, 5, 6], [5, 7, 6],
        [0, 1, 4], [1, 5, 4], [2, 6, 3], [3, 6, 7],
        [0, 4, 2], [2, 4, 6], [1, 3, 5], [3, 7, 5],
    ],
    dtype=np.int64,
)


@dataclass
class Placed:
    model: str
    corners: np.ndarray  # (8, 3) world


def place_structures(
    world: World,
    terrain: Terrain,
    fs: FileSystem,
    guids: dict[str, str],
    *,
    trees: bool = False,
    smallest: float = 1.5,
    report: dict | None = None,
) -> list[Placed]:
    """Every top-level entity with a model, as its model's box in the world."""
    report = report if report is not None else {}
    prefabs = Prefabs(fs)
    bounds: dict[str, tuple[np.ndarray, np.ndarray] | None] = {}
    out = []

    def note(reason: str) -> None:
        report[reason] = report.get(reason, 0) + 1

    for entity in world.entities:
        if entity.parent is not None:
            note("child entity (not placed)")
            continue
        coords = entity.props.get("coords")
        if coords is None or entity.prefab is None:
            continue
        if entity.cls == "Tree" and not trees:
            note("tree (--trees adds them)")
            continue
        if entity.cls in ("DecalEntity",):
            continue
        path = guids.get(entity.prefab)
        if path is None:
            note("prefab not in the resource database")
            continue
        prefab = prefabs.get(path)
        if prefab.model is None:
            continue
        model = prefab.model
        if model.lower().startswith("assets/vegetation/") and not trees:
            note("vegetation (--trees adds it)")
            continue
        if model not in bounds:
            try:
                bounds[model] = xob_bounds(fs.read(model))
            except (FileNotFoundError, EnfusionError, struct.error):
                bounds[model] = None
        box = bounds[model]
        if box is None:
            note("model without readable bounds")
            continue
        scale = float(entity.props.get("scale", 1.0))
        low, high = box[0] * scale, box[1] * scale
        if max(high - low) < smallest:
            note(f"smaller than {smallest:g} m")
            continue
        x, y, z = coords
        flags = entity.props.get("Flags", prefab.flags) or 0
        if not flags & _ABSOLUTE_Y:
            y += float(terrain.height_at(x, z))
        corners = np.array([[a, b, c] for a in (low[0], high[0]) for b in (low[1], high[1]) for c in (low[2], high[2])])
        corners = corners @ rotation(entity.props.get("angles", (0.0, 0.0, 0.0))) + np.array([x, y, z])
        out.append(Placed(model, corners))
    return out


# --------------------------------------------------------------------------
# Export


@dataclass
class WorldReport:
    name: str
    terrain: Terrain | None = None
    ground_triangles: int = 0
    texture: tuple[int, int] | None = None
    entities: int = 0
    structures: int = 0
    water_triangles: int = 0
    skipped: dict[str, int] = field(default_factory=dict)
    unread: dict[str, int] = field(default_factory=dict)


def export_world(
    install: Path,
    wanted: str,
    out: Path,
    *,
    ground_spacing: float = 2.0,
    texture: int = 4096,
    structures: bool = True,
    trees: bool = False,
    log=print,
) -> WorldReport:
    from .glb import Part, write_glb

    started = time.time()
    fs = FileSystem.of_install(install)
    world_name, terr = find_world(fs, wanted)
    name = world_name.rsplit("/", 1)[-1]
    report = WorldReport(name)
    log(f"{name}: reading the terrain")
    terrain = read_terrain(fs, terr)
    report.terrain = terrain
    step = max(1, int(round(ground_spacing / terrain.spacing)))
    h = terrain.heights[::step, ::step]
    rows, cols = h.shape
    xs = np.arange(cols) * terrain.spacing * step
    zs = np.arange(rows) * terrain.spacing * step
    grid = np.empty((rows, cols, 3), dtype=np.float32)
    grid[..., 0] = xs[None, :]
    grid[..., 1] = h
    grid[..., 2] = zs[:, None]
    index = np.arange(rows * cols).reshape(rows, cols)
    a, b, c, d = index[:-1, :-1], index[:-1, 1:], index[1:, :-1], index[1:, 1:]
    # Wound so the face normal points up (+y) in the game's frame.
    ground_faces = np.concatenate([np.stack([a, c, b], -1).reshape(-1, 3), np.stack([b, c, d], -1).reshape(-1, 3)])
    report.ground_triangles = len(ground_faces)
    width, depth = (cols - 1) * terrain.spacing * step, (rows - 1) * terrain.spacing * step
    uvs = np.stack([grid[..., 0].ravel() / width, grid[..., 2].ravel() / depth], 1).astype(np.float32)

    image = colour_map(fs, terrain, texture) if texture else None
    if image is not None:
        report.texture = image.shape[1], image.shape[0]

    positions = [grid.reshape(-1, 3)]
    all_uvs = [uvs]
    parts = [Part(f"ground:{name}", ground_faces, colour=(0.55, 0.52, 0.45), texture=image)]
    offset = len(positions[0])

    # The sea, at zero, on a grid eight times coarser than the ground: a cell
    # is sea where any ground vertex in it is below zero. Where the land
    # stands above the water the ground hides it, as in the game, so the
    # coarse edge never shows - and a flat sea needs no more triangles.
    sea_positions, water_faces = _sea(terrain.heights, terrain.spacing * step * 8, terrain.spacing)
    if len(water_faces):
        positions.append(sea_positions)
        all_uvs.append(np.zeros((len(sea_positions), 2), dtype=np.float32))
        parts.append(Part(f"water:{name}", water_faces + offset, colour=(0.22, 0.40, 0.55)))
        offset += len(sea_positions)
        report.water_triangles = len(water_faces)

    if structures:
        path = world_file(fs, world_name)
        if path is None:
            report.skipped["no world file"] = 1
        else:
            log(f"{name}: reading {path}")
            world = read_world(fs.read(path))
            report.entities = len(world.entities)
            report.unread = world.unread
            guids = resource_paths(install)
            placed = place_structures(world, terrain, fs, guids, trees=trees, report=report.skipped)
            report.structures = len(placed)
            if placed:
                corners = np.concatenate([p.corners for p in placed]).astype(np.float32)
                faces = np.concatenate([_BOX_FACES + 8 * i for i in range(len(placed))]) + offset
                positions.append(corners)
                all_uvs.append(np.zeros((len(corners), 2), dtype=np.float32))
                parts.append(Part(f"structure:{name}", faces, colour=(0.75, 0.74, 0.70)))
                offset += len(corners)

    write_glb(out, np.concatenate(positions), parts=parts, uvs=np.concatenate(all_uvs))
    log(f"{name}: written in {time.time() - started:.0f} s")
    return report


def _sea(heights: np.ndarray, cell: float, spacing: float) -> tuple[np.ndarray, np.ndarray]:
    """Square cells of `cell` metres at height zero wherever the ground in them dips below zero."""
    per = max(1, int(round(cell / spacing)))
    rows, cols = heights.shape
    nz, nx = -(-(rows - 1) // per), -(-(cols - 1) // per)
    padded = np.full((nz * per + 1, nx * per + 1), np.inf, dtype=np.float32)
    padded[:rows, :cols] = heights
    low = padded[:-1, :-1].reshape(nz, per, nx, per).min(axis=(1, 3))
    low = np.minimum(low, padded[per::per, :-1].reshape(nz, nx, per).min(axis=2))
    low = np.minimum(low, padded[:-1, per::per].reshape(nz, per, nx).min(axis=1))
    sea = low < 0
    xs = np.minimum(np.arange(nx + 1) * per, cols - 1) * spacing
    zs = np.minimum(np.arange(nz + 1) * per, rows - 1) * spacing
    grid = np.zeros((nz + 1, nx + 1, 3), dtype=np.float32)
    grid[..., 0], grid[..., 2] = xs[None, :], zs[:, None]
    index = np.arange((nz + 1) * (nx + 1)).reshape(nz + 1, nx + 1)
    a, b, c, d = index[:-1, :-1][sea], index[:-1, 1:][sea], index[1:, :-1][sea], index[1:, 1:][sea]
    faces = np.concatenate([np.stack([a, c, b], 1), np.stack([b, c, d], 1)])
    used = np.unique(faces)
    remap = np.full(len(index.ravel()), -1, dtype=np.int64)
    remap[used] = np.arange(len(used))
    return grid.reshape(-1, 3)[used], remap[faces]


# --------------------------------------------------------------------------
# Command line: `enfusion-worlds` and `enfusion-world`


def add_verbs(sub) -> None:
    p = sub.add_parser("enfusion-worlds", help="list the worlds of an installed Arma Reforger")
    p.add_argument("--install", type=Path, default=None, help="the game's folder, if not in a Steam library")
    p = sub.add_parser("enfusion-world", help="export an Arma Reforger world: terrain, its colour, the sea, building boxes")
    p.add_argument("world", help="the world's name as `enfusion-worlds` lists it")
    p.add_argument("-o", "--out", type=Path, default=None, help="the .glb (default: <world>.glb)")
    p.add_argument("--install", type=Path, default=None, help="the game's folder, if not in a Steam library")
    p.add_argument("--ground-spacing", type=float, default=2.0, metavar="METRES", help="terrain vertex spacing in the file (default 2, the terrain's own)")
    p.add_argument("--texture-size", type=int, default=4096, metavar="PIXELS", help="the ground colour image's larger side (default 4096; 0 for none)")
    p.add_argument("--no-structures", action="store_true", help="leave out the placed models")
    p.add_argument("--trees", action="store_true", help="also place trees and other vegetation (as boxes)")


def run(args) -> int:
    import sys

    install = find_install(args.install)
    if install is None:
        print("Arma Reforger not found; pass --install <game folder>", file=sys.stderr)
        return 2
    if args.verb == "enfusion-worlds":
        fs = FileSystem.of_install(install)
        for world, terr in list_worlds(fs):
            print(f"  {world:<40} {terr}")
        return 0
    out = args.out or Path(f"{args.world.replace('/', '_')}.glb")
    try:
        report = export_world(
            install,
            args.world,
            out,
            ground_spacing=args.ground_spacing,
            texture=args.texture_size,
            structures=not args.no_structures,
            trees=args.trees,
        )
    except (LookupError, EnfusionError) as exc:
        print(exc, file=sys.stderr)
        return 1
    t = report.terrain
    print(f"{report.name} -> {out}")
    print(
        f"  ground     {report.ground_triangles:>10,} triangles, {t.size[0]:,.0f} x {t.size[1]:,.0f} m; "
        f"{t.mismatches:,} of {t.shared:,} tile-edge vertices disagree"
        + (f"; colour {report.texture[0]} x {report.texture[1]}" if report.texture else "")
    )
    print(f"  structure  {report.structures:>10,} boxes from {report.entities:,} entities")
    print(f"  water      {report.water_triangles:>10,} triangles (the sea)")
    if report.skipped:
        print("  left out   " + ", ".join(f"{k}: {v:,}" for k, v in sorted(report.skipped.items())))
    if report.unread:
        print(f"  unread     {report.unread}")
    return 0
