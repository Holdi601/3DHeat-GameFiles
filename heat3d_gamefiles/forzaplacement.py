"""
Everything placed on the terrain: kerbs, barriers, tyre walls, signs, buildings.

Terrain carries its own world position; nothing else does. A guardrail is a
four-metre model in its own space, and where each copy of it stands is recorded
separately, in `.pgeo` placement files - one per category per spatial cell, under
`scene\\proc\\cellsize\\<size>\\<x>_<z>\\c<size>_<category>_….pgeo`. This reads
those, finds each placed model's geometry and textures, and puts the copies where
the game puts them.

The record
----------
::

    u32 name length, name            the cell and section, for humans
    u32 0, u32 13, u32 15
    f32 x 8                          a box: min xyz, pad, max xyz, pad
    u32 length, CATEGORY
    ... a table of variant names ...
    then per model:
        u32 length, <model name>_3D
        u32 count
        count x 80 bytes:
            u32 x 3   position, sign-magnitude 16.16 fixed point
            f32 x 3   the model's x axis in the world
            f32 x 3   its y axis
            f32 x 3   scale
            u32 x 3   unknown
            u32       which material variant this copy wears
            ...       16 bytes not needed to place it

Three things about that were wrong before they were right, and each was found
by a check rather than by reading:

- **The position is fixed point, not a fraction of the box.** Both readings put
  every guardrail inside its file's box, so the box alone could not decide it.
  Consecutive guardrail segments did: read as 16.16 they are exactly 4.000 metres
  apart, which is the model's length; read as a fraction of the box they are
  1.4 millimetres apart.
- **The sign is a sign bit, not two's complement.** Two's complement put negative
  coordinates tens of kilometres off the map. With bit 31 as the sign, every
  `_3D` record of every category sampled lands inside its own file's box.
- **The two vectors are the model's own axes, as columns.** With the x axis taken
  as the first vector, the end of every guardrail segment lands on the start of
  the next: 93.5% within 5 cm, median 0.000 m. Every other reading tried puts the
  next segment several metres away.

The third axis is their cross product, x cross y.

Only names ending in `_3D` are model records. The table before them lists
variants by bare name (`PRP_GBL_CRCT_TYRES_02_D`), and read as records those
put a tenth of their "instances" at infinity and the rest outside the file's box.

Which level of detail
---------------------
A model is up to a dozen `_cluster###.i.modelbin` files. Each triangle carries a
mask of the detail levels it belongs to (bit `level + 1`); 0xFFFF marks the
breakable pieces - a guardrail's posts, a tyre stack's single tyres - which
overlap the whole model (95% of one such cluster lies within 2 cm of the level-0
surface) and are drawn instead of it once it is knocked apart. So a model's
levels are its explicitly marked triangles, and the 0xFFFF ones are used only by
a model that has no marked level at all.

The finest level of everything around a circuit is several million triangles:
950 guardrail segments at 960 each, 820 tyre stacks at 1,400. So the export is
given a triangle budget. Copies far from the driving start coarse (`NEAR`,
`FAR`), the models that cost most - count times triangles - step down a level
at a time until it fits, and where even the coarsest levels will not, copies
are left out, furthest and smallest-looking first (`_fit`). Kerbs never step
down or go: they are 84 triangles, and they are the one thing on the list a lap
is measured against. City buildings are handled whole, through the game's own
stand-ins (`HLOD`).
"""

from __future__ import annotations

import heapq
import re
import struct
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .detail import DEFAULT_BUDGET, FAR, HEADROOM, NEAR, auto_budget, choose_levels, route_distance  # noqa: F401
from .forzamaterial import Manifest, colour_texture, in_season, strip_guid
from .forzatech import (
    UnsupportedForza,
    _chunks_by_tag,
    material_paths,
    material_textures,
    position_box,
    read_geometry,
    read_model,
)
from .minizip import open_chunk

#: Bytes per placed instance.
INSTANCE = 80
#: Where in an instance its material variant is: which of a billboard's five
#: prints, or a tyre stack's six paint colours, this copy wears. It indexes the
#: variant table each `Mesh` record opens with (see `forzatech.MESH_STANDARD`).
#: Found by reading copies of one circuit's billboard, whose five variants
#: this field ran through 0, 2, 2, 3, 4 while every guardrail's stayed 0.
VARIANT_AT = 60

#: `u32 length` then that many name characters, ending in the model suffix.
_RECORD = re.compile(rb"[\x05-\x7f]\x00\x00\x00([A-Za-z0-9_\-]{2,120}_3[Dd])")

#: Categories and the part each is exported as. Kerbs are pulled out of props
#: below. Left out by default: `trees` and `bushes` (hundreds of thousands of
#: leaf cards, and they hide the road), and `grasstemplate`, `crowdtemplate` and
#: `cwdspline` (grass and spectators: animated sprites, no geometry). `evolving`
#: (sites that change with progression) is read, but only ever as a layer of
#: its own (see `layer_of`).
CATEGORIES = {
    "barriers": "structure:barriers",
    "props": "structure:props",
    "signs": "structure:signs",
    "buildings": "structure:buildings",
    "infrastructure": "structure:infrastructure",
    "bridges": "structure:bridges",
    "rocks": "structure:rocks",
    "smashables": "structure:smashables",
    "trees": "structure:trees",
    "bushes": "structure:trees",
    "evolving": "structure:props",
}
DEFAULT_CATEGORIES = (
    "barriers", "props", "signs", "buildings", "infrastructure", "bridges", "rocks", "evolving",
)
VEGETATION = ("trees", "bushes", "smashables")

#: What a placement file's name says after `c<size>_<category>_` when it is part
#: of the free-roam world: a level-of-detail set and perhaps a section number.
#: Everything else names a layer the game switches on - a race's own layer
#: (`rt_x<route>`), a runtime layer (`rt_<n>`), an activity
#: (`_tag_drift_zone_04_`), a collectible - and is exported apart, labelled.
#: The level-of-detail token is a short word (`do`, `so`, `ulc`, `ulp`, `cwd`;
#: whatever a later game calls it, it has stayed under four letters); `rt`
#: never is one - it opens a runtime layer.
_BASE_LAYER = re.compile(r"^(?!rt(?:_|$))[a-z]{0,3}(?:_\d+)?$")
_LOD_TOKEN = re.compile(r"^(?:do|so|ulc|ulp|cwd)_|_(?:do|so|ulc|ulp|cwd)$")
#: The race a layer belongs to: `x<route id>`, one or more.
_ROUTE_TOKEN = re.compile(r"(?:^|_)x(\d+)(?=_|$)")

#: Parts for what is switched on with something: the race being exported's own
#: layer, and every other layer that is not the free-roam world.
EVENT_PART = "structure:event_{}"
LAYER_PART = "structure:layer_{}"


def layer_of(name: str) -> str:
    """
    A placement file's layer: "" for the free-roam world, else its tag.

    `c200_props_do.pgeo` and `c50_buildings_do_119.pgeo` are the world;
    `c200_props_do_rt_0_discount_board_xp_a_054.pgeo` is layer
    `rt_0_discount_board_xp_a`, `c300_crowdtemplate_cwd_rt_x2292.pgeo` layer
    `rt_x2292`, and anything filed under `evolving` is a layer whatever it says.
    """
    leaf = name.replace("/", "\\").rsplit("\\", 1)[-1].lower()
    leaf = leaf.removesuffix(".pgeo")
    pieces = leaf.split("_", 2)
    if len(pieces) < 2:
        return ""
    rest = pieces[2] if len(pieces) > 2 else ""
    if pieces[1] == "evolving":
        return "evolving_" + (_LOD_TOKEN.sub("", rest).strip("_") or "world")
    if _BASE_LAYER.match(rest):
        return ""
    tag = _LOD_TOKEN.sub("", rest)
    # A trailing number is the file's section, except the one after `rt`,
    # which is the layer's own.
    tag = re.sub(r"(?<!rt)_\d+$", "", tag) if not _ROUTE_TOKEN.search(tag) else tag
    return tag.strip("_") or rest.strip("_")


def routes_of(layer: str) -> set[int]:
    """The route ids a layer is placed for: `rt_x1023_x2201` -> {1023, 2201}."""
    return {int(found) for found in _ROUTE_TOKEN.findall(layer)}

#: Kerbs ship as props - `road_gen_rum_…`, rumble strips - but they are part of
#: the racing surface, and they are the one prop a lap analysis cannot do
#: without. So they get their own part, and it is ground: solid, and read as
#: part of the track rather than as something standing on it.
KERB = re.compile(r"^road_gen_rum", re.I)
KERB_PART = "ground:kerbs"

#: Linear RGB for what has no texture, by part.
FALLBACK_COLOURS = {
    KERB_PART: (0.60, 0.12, 0.10),
    "ground:venue": (0.33, 0.33, 0.34),
    "ground:plinths": (0.42, 0.41, 0.39),
    "structure:barriers": (0.50, 0.50, 0.50),
    "structure:props": (0.45, 0.35, 0.25),
    "structure:signs": (0.70, 0.70, 0.70),
    "structure:buildings": (0.55, 0.52, 0.48),
    "structure:infrastructure": (0.45, 0.45, 0.47),
    "structure:bridges": (0.45, 0.45, 0.45),
    "structure:rocks": (0.30, 0.28, 0.25),
    "structure:smashables": (0.12, 0.22, 0.06),
    "structure:trees": (0.10, 0.20, 0.05),
}

#: Material shaders whose surfaces are cut out by the texture's alpha: a chain
#: link fence is one quad with holes painted into it. Drawn solid, it is a wall.
_CUTOUT = re.compile(r"alphatest|alphablend|transmissive|anim_flag|impostor|branch|bush|tree", re.I)
#: Material shaders that draw nothing solid of their own: projected decals.
_SKIP = re.compile(r"decal", re.I)
#: A cut-out surface less opaque than this, on average, is left out: it is
#: mostly holes, like a chain-link fence (measured 0.44 to 0.47 around the test circuit),
#: and drawn solid it would be a wall across the view of the track.
CUTOUT_COVERAGE = 0.5
#: ...unless it is nearly all holes, which no real surface is: a warning sign
#: that samples 0.01 is reading a texture whose alpha means something else to
#: its shader, and it is kept as the solid thing it is.
NOT_A_MASK = 0.05

#: How big a model's texture is kept. A guardrail's colour at 256 pixels for
#: four metres is 1.6 cm a pixel, finer than anyone looks at a barrier, and
#: eighty of them pack into the viewer's one atlas beside two 2048-pixel ground
#: tiles with room to spare. At 512 they took four times the room and the
#: ground's own detail was what gave way.
MODEL_TEXTURE = 256

#: The game's own stand-ins for whole buildings: `scene\hlod_tier_1\`, one mesh
#: per building or block, already in world coordinates like terrain. A city
#: builds its buildings out of modular pieces - 380,000 of them around one
#: city street circuit, forty million triangles even at their coarsest - so
#: they cannot all be kept, and leaving pieces out one at a time leaves lone wall
#: slabs standing. Where a stand-in covers a building, it is used instead of the
#: pieces, and is kept or left out whole.
HLOD = "hlod_tier_1_"

#: Models already in world coordinates, outside the placement files: a venue's
#: own ground (a stadium's floor and infield, a plaza, the plinth a site
#: stands on - `scene\models\plots\`, `scene\models\plinths\`), procedurally
#: built bridges (`scene\models\hda_infrastructure\`) and a few one-off pieces.
#: Nothing places them; their meshes carry their own world position, as
#: terrain does. A stadium circuit is driven on its floor, and without it the
#: export is the open-world ground the game hides under it.
#:
#: Told from models in their own space by where their box lies: a model's own
#: space has it within a couple of hundred metres of its origin (a stadium's
#: roof hangs far off its own), a world-space one sits wherever it is on the map.
WORLD_REACH = 300.0
#: World-space models that are not drawn: occluders, cables strung along the
#: roads, the sea's backdrop, building roofs and occluders the stand-ins
#: already draw, collision and water volumes.
_NOT_DRAWN = re.compile(r"occ|vista|cable|collision|boundary|trigger", re.I)
_NOT_DRAWN_FOLDERS = {
    "hda_buildings", "hda_cables", "collision", "building_shells", "water", "vista",
    "whitebox", "development", "decals", "road_decals", "terrain_decals", "groundcover",
}
#: World-space models that are ground. A plot is a venue's own ground - a
#: stadium's floor, a festival site, a plaza - and a venue the driving touches
#: is cut whole. A plinth is the ground a street is dressed with (planters,
#: steps, a park's paving): drawn where the driving is, like the rest.
_VENUE_FOLDERS = {"plots"}
_GROUND_FOLDERS = {"plinths"}
_GROUNDLIKE = re.compile(r"floor|ground|road", re.I)
VENUE_PART = "ground:venue"
PLINTH_PART = "ground:plinths"
WORLD_GROUND = (VENUE_PART, PLINTH_PART)
#: Track folder -> its world-space models, read once a process.
_WORLD_CACHE: dict[str, list] = {}


def world_part(folder: str, stem: str) -> str | None:
    """The part a world-space model is exported as, or None if it is not drawn."""
    if folder in _NOT_DRAWN_FOLDERS or _NOT_DRAWN.search(stem):
        return None
    if folder in _VENUE_FOLDERS:
        return VENUE_PART
    if folder in _GROUND_FOLDERS or _GROUNDLIKE.search(stem):
        return PLINTH_PART
    if "bridge" in stem:
        return CATEGORIES["bridges"]
    return CATEGORIES.get(folder, CATEGORIES["infrastructure"])

def fixed(value: int) -> float:
    """Sign-magnitude 16.16: bit 31 the sign, the rest the magnitude."""
    magnitude = (value & 0x7FFFFFFF) / 65536.0
    return -magnitude if value & 0x80000000 else magnitude


@dataclass
class Placements:
    """One `.pgeo`: which models it places, and where."""

    title: str
    low: np.ndarray
    high: np.ndarray
    #: model name -> (n, 13): position, x axis, y axis, scale, variant.
    models: dict[str, np.ndarray] = field(default_factory=dict)


def parse_pgeo(data: bytes) -> Placements:
    """
    Read one placement file.

    Model records are found by their `_3D` name rather than walked from a
    known offset: the variant table between the header and the first model
    varies in length and is not needed. A candidate is accepted only if its
    count of instances fits in the file, so a stray match inside a record cannot
    start a phantom model, and instances whose numbers are not finite are
    dropped.
    """
    if len(data) < 8:
        raise UnsupportedForza("too short to be a placement file")
    (length,) = struct.unpack_from("<I", data, 0)
    if length > 256 or 4 + length + 44 > len(data):
        raise UnsupportedForza("the placement header does not parse")
    title = data[4 : 4 + length].decode("ascii", "replace")
    at = 4 + length + 12
    box = struct.unpack_from("<8f", data, at)
    out = Placements(title=title, low=np.array(box[0:3]), high=np.array(box[4:7]))

    position = at + 32
    while True:
        found = _RECORD.search(data, position)
        if not found:
            break
        start = found.start()
        (length,) = struct.unpack_from("<I", data, start)
        name = found.group(1).decode("ascii")
        after = start + 4 + length
        if length != len(name) or after + 4 > len(data):
            position = start + 1
            continue
        (count,) = struct.unpack_from("<I", data, after)
        body = after + 4
        if not 1 <= count <= 200_000 or body + count * INSTANCE > len(data):
            position = start + 1
            continue
        raw = np.frombuffer(data, dtype=np.uint8, count=count * INSTANCE, offset=body)
        raw = raw.reshape(count, INSTANCE)
        words = raw[:, 0:12].copy().view("<u4")
        sign = np.where(words & 0x80000000, -1.0, 1.0)
        positions = sign * (words & 0x7FFFFFFF).astype(np.float64) / 65536.0
        with np.errstate(invalid="ignore", over="ignore"):
            axes = raw[:, 12:48].copy().view("<f4").astype(np.float64)
        variant = raw[:, VARIANT_AT : VARIANT_AT + 4].copy().view("<u4").astype(np.float64)
        instances = np.concatenate([positions, axes, variant], axis=1)
        instances = instances[np.isfinite(instances).all(axis=1)]
        if len(instances):
            previous = out.models.get(name)
            out.models[name] = (
                instances if previous is None else np.concatenate([previous, instances])
            )
        position = body + count * INSTANCE
    return out


def cell_of(name: str) -> tuple[int, int, int, str] | None:
    """(size, x, z, category) from a placement file's path, or None."""
    parts = name.split("\\")
    if "cellsize" not in parts:
        return None
    where = parts.index("cellsize")
    try:
        size = int(parts[where + 1])
        cx, cz = (int(v) for v in parts[where + 2].split("_"))
    except (ValueError, IndexError):
        return None
    leaf = parts[-1].split("_")
    return size, cx, cz, leaf[1].lower() if len(leaf) > 1 else ""


class Track:
    """
    A track's archives, opened once, with its placements and models indexed.

    Found from names alone - `cellsize\\<size>\\<x>_<z>` names the cell a
    placement file covers - so a whole map's worth of files is filtered without
    opening one.
    """

    def __init__(self, folder: str | Path, chunks=(0, 1, 2, 3)):
        self.folder = Path(folder)
        self.archives = {}
        self.placements: list[tuple[int, int, tuple[int, int, int, str]]] = []
        #: (chunk, entry) -> the placement file's layer, "" for the free-roam world.
        self.layers: dict[tuple[int, int], str] = {}
        self.clusters: dict[str, list[tuple[int, int, str]]] = defaultdict(list)
        for number in chunks:
            if not (self.folder / f"GeoChunk{number}.minizip").exists():
                continue
            archive, contents = open_chunk(self.folder, number)
            self.archives[number] = archive
            for entry, name in enumerate(contents.names):
                lower = name.lower()
                if lower.endswith(".pgeo"):
                    cell = cell_of(lower)
                    if cell:
                        self.placements.append((number, entry, cell))
                        layer = layer_of(lower)
                        if layer:
                            self.layers[(number, entry)] = layer
                elif lower.endswith(".modelbin") and "_cluster" in lower:
                    stem = lower.rsplit("\\", 1)[-1].split("_cluster")[0]
                    self.clusters[stem].append((number, entry, name))
        self._stand_ins: list | None = None
        self._world: list | None = None

    def layer(self, number: int, entry: int) -> str:
        return self.layers.get((number, entry), "")

    def world_models(self) -> list[tuple[str, str, np.ndarray, np.ndarray]]:
        """
        Every drawn model already in world coordinates, as (stem, part, low,
        high): a venue's ground, procedural bridges (see `WORLD_REACH`). Header
        reads only, a few seconds for a whole map.
        """
        key = str(self.folder.resolve()) if isinstance(self.folder, Path) else str(self.folder)
        if self._world is None and key in _WORLD_CACHE:
            self._world = _WORLD_CACHE[key]
        if self._world is None:
            found = []
            for stem, clusters in self.clusters.items():
                if stem.startswith((HLOD, "autoterrain", "autouberlod")):
                    continue
                number, entry, name = min(clusters, key=lambda c: c[2])
                path = name.lower().replace("/", "\\")
                if "\\scene\\models\\" not in path:
                    continue
                folder = path.split("\\scene\\models\\", 1)[1].split("\\", 1)[0]
                part = world_part(folder, stem)
                if part is None:
                    continue
                try:
                    model = read_model(name, self.read(number, entry))
                    meshes = _chunks_by_tag(model).get("Mesh") or []
                    boxes = [position_box(model.raw(mesh)) for mesh in meshes]
                except (UnsupportedForza, struct.error, ValueError, AttributeError, TypeError):
                    continue
                if not boxes:
                    continue
                low = np.min([bias - np.abs(scale) for scale, bias in boxes], axis=0)
                high = np.max([bias + np.abs(scale) for scale, bias in boxes], axis=0)
                middle = (low + high) / 2
                if np.hypot(middle[0], middle[2]) > WORLD_REACH and np.isfinite(low).all():
                    found.append((stem, part, low, high))
            self._world = _WORLD_CACHE[key] = found
        return self._world

    def venues(self, low, high, corridor=None) -> list[tuple[str, np.ndarray, np.ndarray]]:
        """A venue's own ground the driving passes over, as (stem, low, high)."""
        return [
            (stem, lo, hi)
            for stem, part, lo, hi in self.world_models()
            if part == VENUE_PART
            and hi[0] >= low[0] and lo[0] <= high[0] and hi[2] >= low[1] and lo[2] <= high[1]
            and (corridor is None or corridor.touches((lo[0], lo[2]), (hi[0], hi[2])))
        ]

    def stand_ins(self) -> list[tuple[str, np.ndarray, np.ndarray]]:
        """
        Every whole-building stand-in, as (stem, low, high) world bounds.

        Read from each mesh's own position box, so finding the ones in a box
        costs a header per mesh rather than a decode: two seconds for all of an
        open-world map's.
        """
        if self._stand_ins is None:
            found = []
            for stem, clusters in self.clusters.items():
                if not stem.startswith(HLOD):
                    continue
                low = np.full(3, np.inf)
                high = np.full(3, -np.inf)
                for number, entry, name in clusters:
                    try:
                        model = read_model(name, self.read(number, entry))
                        meshes = _chunks_by_tag(model).get("Mesh")
                        if not meshes:
                            continue
                        scale, bias = position_box(model.raw(meshes[0]))
                    except (UnsupportedForza, struct.error):
                        continue
                    low = np.minimum(low, bias - np.abs(scale))
                    high = np.maximum(high, bias + np.abs(scale))
                if np.isfinite(low).all():
                    found.append((stem, low, high))
            self._stand_ins = found
        return self._stand_ins

    def read(self, number: int, entry: int) -> bytes:
        return self.archives[number].read(entry)

    def close(self) -> None:
        for archive in self.archives.values():
            archive.close()

    def __enter__(self):
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def placement_files(self, low, high, categories) -> list[tuple[int, int, str]]:
        out = []
        for number, entry, (size, cx, cz, category) in self.placements:
            if category not in categories:
                continue
            x0, z0 = cx * size, cz * size
            if x0 > high[0] or x0 + size < low[0] or z0 > high[1] or z0 + size < low[1]:
                continue
            out.append((number, entry, category))
        return out


@dataclass
class Level:
    """One level of detail of one model, compacted to the vertices it uses."""

    positions: np.ndarray
    normals: np.ndarray
    uvs: np.ndarray | None
    faces: np.ndarray
    #: Index into `Model.textures` per triangle and variant, -1 for none:
    #: (triangles, variants).
    texture: np.ndarray

    @property
    def triangles(self) -> int:
        return len(self.faces)


@dataclass
class Model:
    name: str
    levels: list[Level]
    textures: list[str]

    @property
    def size(self) -> float:
        """The diagonal of its finest level's bounding box, in its own metres."""
        points = self.levels[0].positions
        return float(np.linalg.norm(points.max(axis=0) - points.min(axis=0))) if len(points) else 0.0


#: A colour no surface is painted: the solid block a shared building atlas
#: reserves for surfaces its shader tints from other textures. The stand-ins map
#: roofs and blank walls into it, and drawn as it is, a city comes out orange.
PLACEHOLDER = np.array([255, 64, 0])


def unmark(image: np.ndarray) -> np.ndarray:
    """
    The texture with any large placeholder block painted over in the texture's
    own average colour. Only a block - over a twentieth of the image, all within
    a few levels of the placeholder - counts; an orange traffic cone does not.
    """
    rgb = image[:, :, :3].astype(np.int16)
    marked = (np.abs(rgb - PLACEHOLDER).max(axis=2) <= 12)
    if marked.mean() < 0.05 or marked.all():
        return image
    out = image.copy()
    out[marked, :3] = np.round(image[~marked, :3].mean(axis=0)).astype(np.uint8)
    return out


class Textures:
    """Model textures by name, decoded once, at most `largest` pixels across."""

    def __init__(self, shelf, largest: int = MODEL_TEXTURE):
        self.shelf = shelf
        self.largest = largest
        self._images: dict[str, np.ndarray | None] = {}
        self._coverage: dict[str, np.ndarray | None] = {}

    def image(self, name: str) -> np.ndarray | None:
        if name not in self._images:
            try:
                image = self.shelf.best(name, largest=self.largest)
            except UnsupportedForza:
                image = None
            self._images[name] = unmark(image) if image is not None else None
        return self._images[name]

    def coverage(self, name: str) -> np.ndarray | None:
        """Opacity averaged over 1/32 of the texture each way, 0..1."""
        if name not in self._coverage:
            image = self.image(name)
            if image is None or image.shape[2] < 4:
                self._coverage[name] = None
            else:
                from PIL import Image

                alpha = Image.fromarray(image[:, :, 3]).resize((32, 32), Image.BOX)
                self._coverage[name] = np.asarray(alpha, dtype=np.float32) / 255.0
        return self._coverage[name]


class ModelShelf:
    """Placed models by name, read once each."""

    def __init__(self, track: Track, manifest: Manifest | None, textures: Textures | None, season: str = "summer"):
        self.track = track
        self.manifest = manifest
        self.hashes = manifest.hashes() if manifest else None
        self.textures = textures
        self.season = season
        self._cache: dict[str, Model | None] = {}
        #: Models left out whole because every surface was see-through.
        self.see_through: set[str] = set()
        self.cut_away = False

    @staticmethod
    def stem(placed: str) -> str:
        return placed.lower().removesuffix("_3d")

    def _texture_for(self, slots) -> str | None:
        if not self.manifest or not self.textures:
            return None
        name = colour_texture(slots, self.manifest)
        if name is None:
            return None
        return in_season(name, self.season, self.textures.shelf.resolve)

    def load(self, placed: str) -> Model | None:
        stem = self.stem(placed)
        if stem not in self._cache:
            self._cache[stem] = self._load(stem)
        return self._cache[stem]

    def _load(self, stem: str) -> Model | None:
        self.cut_away = False
        pieces = []
        textures: list[str] = []
        for number, entry, name in sorted(self.track.clusters.get(stem, []), key=lambda c: c[2]):
            try:
                model = read_model(name, self.track.read(number, entry))
                geometry = read_geometry(model, lod=None)
            except (UnsupportedForza, ValueError, struct.error):
                continue
            if not len(geometry.faces) or geometry.lods is None:
                continue
            shaders = material_paths(model)
            slots = material_textures(model, self.hashes) if self.hashes is not None else []
            per_material = []
            for index, shader in enumerate(shaders):
                texture = self._texture_for(slots[index]) if index < len(slots) else None
                if texture is not None and texture not in textures:
                    textures.append(texture)
                per_material.append(
                    (
                        textures.index(texture) if texture is not None else -1,
                        bool(_CUTOUT.search(shader)),
                        bool(_SKIP.search(shader)),
                    )
                )
            # A submesh whose material is not readable takes the model's first
            # material, which is the default-season one.
            fallback = next((m for m in per_material if not m[2]), (-1, False, False))
            materials = self._materials(geometry, len(per_material))
            # Shifted by one so that -1, unknown, looks up the fallback.
            lookup = [fallback, *per_material]
            textures_of = np.array([entry[0] for entry in lookup], dtype=np.int32)
            cutout_of = np.array([entry[1] for entry in lookup], dtype=bool)
            skip_of = np.array([entry[2] for entry in lookup], dtype=bool)
            face_texture = textures_of[materials + 1]
            cutout = cutout_of[materials[:, 0] + 1]
            skip = skip_of[materials[:, 0] + 1]
            pieces.append((geometry, face_texture, cutout, skip))
        if not pieces:
            return None
        # Every level answers for the same number of variants, so a copy's
        # variant means the same thing whichever level it is drawn at.
        width = max(piece[1].shape[1] for piece in pieces)
        pieces = [
            (g, t[:, np.arange(width) % t.shape[1]], c, k) for g, t, c, k in pieces
        ]

        explicit = any(((g.lods != 0xFFFF) & (g.lods != 0)).any() for g, *_ in pieces)
        levels = []
        for level in range(15):
            bit = 1 << (level + 1)
            parts = []
            for geometry, face_texture, cutout, skip in pieces:
                if explicit:
                    keep = ((geometry.lods & bit) != 0) & (geometry.lods != 0xFFFF)
                else:
                    keep = np.ones(len(geometry.faces), dtype=bool) if level == 0 else np.zeros(len(geometry.faces), dtype=bool)
                keep &= ~skip
                if keep.any():
                    parts.append((geometry, keep, face_texture, cutout))
            if not parts:
                if level and not explicit:
                    break
                if levels:
                    # Levels are contiguous from 0; the first empty one ends them.
                    break
                continue
            built = self._level(parts, textures)
            if built is not None and built.triangles:
                levels.append(built)
        if not levels:
            if self.cut_away:
                self.see_through.add(stem)
            return None
        return Model(name=stem, levels=levels, textures=textures)

    def _materials(self, geometry, count: int) -> np.ndarray:
        """
        The `MatI` each triangle uses for every variant a copy can wear: a
        (triangles, variants) array, -1 where it is not known.

        A submesh with fewer variants than the model's widest repeats its own,
        so a copy asking for variant 4 of a tyre stack whose frame has one
        material still gets the frame.
        """
        faces = len(geometry.faces)
        if geometry.submesh is None or not geometry.variants:
            single = (
                geometry.material_index.astype(np.int64)
                if geometry.material_index is not None
                else np.full(faces, -1, dtype=np.int64)
            )
            single[(single >= count) | (single < 0)] = -1
            return single.reshape(faces, 1)
        width = max(len(table) for table in geometry.variants) or 1
        out = np.full((faces, width), -1, dtype=np.int64)
        winter = self.season == "winter"
        for number, table in enumerate(geometry.variants):
            chosen = geometry.submesh == number
            if not chosen.any() or not table:
                continue
            for variant in range(width):
                summer, cold = table[variant % len(table)]
                material = cold if winter and cold != 0xFFFF else summer
                out[chosen, variant] = material if material < count else -1
        return out

    def _level(self, parts, textures) -> Level | None:
        from .glb import compute_normals

        positions, normals, uvs, faces, texture = [], [], [], [], []
        offset = 0
        any_uvs = False
        for geometry, keep, face_texture, cutout in parts:
            chosen = geometry.faces[keep]
            tex = face_texture[keep].copy()  # (triangles, variants)
            cut = cutout[keep]
            uv = geometry.uvs.get(0)
            if uv is not None:
                # Vertices in a buffer group whose layout has no first UV set
                # come back as NaN; their triangles are drawn in flat colour.
                missing = ~np.isfinite(uv).all(axis=1)
                if missing.any():
                    tex[missing[chosen].any(axis=1)] = -1
                    uv = np.where(missing[:, None], 0.0, uv)
            if uv is not None and self.textures is not None and cut.any():
                kept = self._cut(chosen, tex[:, 0], cut, uv, textures)
                chosen, tex = chosen[kept], tex[kept]
            if not len(chosen):
                continue
            used, inverse = np.unique(chosen, return_inverse=True)
            local = geometry.positions[used].astype(np.float32)
            n = geometry.normals[used] if geometry.normals is not None else None
            compact = inverse.reshape(-1, 3).astype(np.int32)
            if n is None or not np.isfinite(n).all():
                n = compute_normals(local, compact)
            positions.append(local)
            normals.append(n.astype(np.float32))
            if uv is not None:
                uvs.append(uv[used].astype(np.float32))
                any_uvs = True
            else:
                uvs.append(np.zeros((len(used), 2), dtype=np.float32))
                tex = np.full(tex.shape, -1, dtype=np.int32)
            faces.append(compact + offset)
            texture.append(tex)
            offset += len(used)
        if not faces:
            return None
        return Level(
            positions=np.concatenate(positions),
            normals=np.concatenate(normals),
            uvs=np.concatenate(uvs) if any_uvs else None,
            faces=np.concatenate(faces),
            texture=np.concatenate(texture),
        )

    def _cut(self, faces, texture, cutout, uv, textures):
        """
        Drop cut-out surfaces whose texture is mostly holes.

        Decided per surface - every cut-out triangle sharing one texture - and
        not per triangle. A chain-link panel is a quad; judged a triangle at a
        time, the half whose samples happen to land on a post survives and the
        other does not, and a fence becomes a row of grey teeth. So the texture's
        opacity is averaged over the whole surface, four samples a triangle
        weighted by its area in the texture, and the surface is kept or left out
        entire.
        """
        keep = np.ones(len(faces), dtype=bool)
        corners = uv[faces]  # (n, 3, 2)
        weights = np.array(
            [[1 / 3, 1 / 3, 1 / 3], [2 / 3, 1 / 6, 1 / 6], [1 / 6, 2 / 3, 1 / 6], [1 / 6, 1 / 6, 2 / 3]]
        )
        points = np.einsum("sk,nkd->nsd", weights, corners)  # (n, 4, 2)
        edge1 = corners[:, 1] - corners[:, 0]
        edge2 = corners[:, 2] - corners[:, 0]
        area = np.abs(edge1[:, 0] * edge2[:, 1] - edge1[:, 1] * edge2[:, 0]) + 1e-9
        for index in np.unique(texture[cutout]):
            if index < 0:
                continue
            coverage = self.textures.coverage(textures[index])
            if coverage is None:
                continue
            these = cutout & (texture == index)
            size = coverage.shape[0]
            u = np.clip((points[these, :, 0] % 1.0) * size, 0, size - 1).astype(int)
            v = np.clip((points[these, :, 1] % 1.0) * size, 0, size - 1).astype(int)
            opacity = coverage[v, u].mean(axis=1)
            mean = np.average(opacity, weights=area[these])
            if NOT_A_MASK <= mean < CUTOUT_COVERAGE:
                keep[these] = False
                self.cut_away = True
        return keep


def place(level: Level, instances: np.ndarray):
    """
    Every copy of one model level, in world space.

    Returns positions, normals and faces for all copies at once. The model's
    local x maps to the first axis, y to the second and z to their cross
    product, each scaled first.
    """
    count = len(instances)
    local = level.positions.astype(np.float64)
    origin = instances[:, 0:3]
    ax = instances[:, 3:6]
    ay = instances[:, 6:9]
    az = np.cross(ax, ay)
    scale = instances[:, 9:12]
    scale = np.where(np.abs(scale) < 1e-6, 1.0, scale)

    scaled = local[None, :, :] * scale[:, None, :]
    world = (
        origin[:, None, :]
        + scaled[:, :, 0:1] * ax[:, None, :]
        + scaled[:, :, 1:2] * ay[:, None, :]
        + scaled[:, :, 2:3] * az[:, None, :]
    )
    n = level.normals.astype(np.float64)[None, :, :] / scale[:, None, :]
    rotated = n[:, :, 0:1] * ax[:, None, :] + n[:, :, 1:2] * ay[:, None, :] + n[:, :, 2:3] * az[:, None, :]
    normals = rotated / np.maximum(np.linalg.norm(rotated, axis=2, keepdims=True), 1e-9)
    faces = level.faces[None, :, :] + (np.arange(count) * len(local))[:, None, None]
    return (
        world.reshape(-1, 3).astype(np.float32),
        normals.reshape(-1, 3).astype(np.float32),
        faces.reshape(-1, 3).astype(np.int32),
    )


@dataclass
class Mesh:
    """One export part: its own vertices, and at most one texture."""

    positions: np.ndarray
    normals: np.ndarray
    uvs: np.ndarray | None
    faces: np.ndarray
    texture: str | None
    colour: tuple[float, float, float]


@dataclass
class Placed:
    """What was placed in a box, by the part it will be exported as."""

    parts: dict[str, Mesh] = field(default_factory=dict)
    textures: dict[str, np.ndarray] = field(default_factory=dict)
    #: category part -> model -> copies.
    counts: dict[str, dict[str, int]] = field(default_factory=dict)
    #: model -> (finest level used, levels available).
    levels: dict[str, tuple[int, int]] = field(default_factory=dict)
    #: Copies left out because even at their coarsest the budget would not
    #: hold them, of how many there were.
    dropped: int = 0
    considered: int = 0
    #: The triangle budget this was fitted to.
    budget: int = 0
    #: Buildings drawn as the game's own whole-building stand-ins, and the
    #: modular pieces they replaced.
    stand_ins: int = 0
    replaced: int = 0
    missing: set[str] = field(default_factory=set)
    #: Models that are nothing but see-through surfaces - chain-link fences,
    #: nets - and so were left out.
    see_through: set[str] = field(default_factory=set)
    #: The game's route this was placed for, if the driving matched one.
    route_id: int | None = None
    #: Layer -> copies: the race's own layers, and every other switched-on layer.
    event: dict[str, int] = field(default_factory=dict)
    layers: dict[str, int] = field(default_factory=dict)
    #: World-space ground of a venue the driving passes through, and how many
    #: other world-space models (bridges) were drawn.
    venue: list[str] = field(default_factory=list)
    world: int = 0
    #: Free-roam copies left out because the race hides them, and a venue's
    #: ground it hides but that is kept, its replacement not being shipped.
    hidden: int = 0
    kept_ground: list[str] = field(default_factory=list)

    def triangles(self) -> int:
        return sum(len(m.faces) for m in self.parts.values())

    def summary(self) -> str:
        lines = []
        for part in sorted(self.counts):
            models = self.counts[part]
            copies = sum(models.values())
            triangles = sum(len(m.faces) for name, m in self.parts.items() if name.split(" ")[0] == part)
            lines.append(
                f"    {copies:7,} placed  {len(models):4} models  {triangles:10,} triangles  {part}"
            )
        if self.venue:
            lines.append(
                f"    venue: the driving passes through {len(self.venue)} pieces of a site's own ground "
                f"({', '.join(sorted(self.venue)[:3])}{'...' if len(self.venue) > 3 else ''})"
            )
        if self.world:
            lines.append(f"    {self.world} models drawn where the game builds them in place (plinths, bridges)")
        race = f"route {self.route_id}" if self.route_id is not None else "no matched route"
        if self.event:
            lines.append(
                f"    event layer ({race}): {sum(self.event.values()):,} copies in "
                + ", ".join(sorted(self.event))
            )
        else:
            lines.append(f"    event layer ({race}): nothing placed for this race alone")
        if self.hidden:
            lines.append(f"    {self.hidden:,} free-roam objects left out: the race takes them away")
        if self.kept_ground:
            lines.append(
                f"    kept {', '.join(self.kept_ground)}: the race hides it for a surface of its own "
                "that the track does not ship"
            )
        if self.layers:
            lines.append(
                f"    switched-on layers: {sum(self.layers.values()):,} copies in {len(self.layers)} "
                f"({', '.join(sorted(self.layers)[:4])}{'...' if len(self.layers) > 4 else ''})"
            )
        coarser = sum(1 for level, _n in self.levels.values() if level)
        if coarser:
            lines.append(f"    {coarser} of {len(self.levels)} models drawn at a coarser level to fit the budget")
        if self.stand_ins:
            lines.append(
                f"    {self.stand_ins:,} buildings drawn whole from the game's own stand-ins "
                f"(which replace {self.replaced:,} modular pieces)"
            )
        if self.dropped:
            lines.append(
                f"    {self.dropped:,} of {self.considered:,} copies left out to fit the budget, the "
                "smallest and furthest from the driving first (--detail-budget raises it)"
            )
        if self.see_through:
            lines.append(
                f"    {len(self.see_through)} models left out as see-through (mostly holes in their texture): "
                + ", ".join(sorted(self.see_through)[:3])
                + ("..." if len(self.see_through) > 3 else "")
            )
        if self.missing:
            lines.append(
                f"    {len(self.missing)} placed names have no model in the archives: "
                + ", ".join(sorted(self.missing)[:3])
                + ("..." if len(self.missing) > 3 else "")
            )
        return "\n".join(lines)


class _Hidden:
    """
    Where the free-roam objects a race hides stand, for finding them among the
    placements: a copy within `REACH` of one is the one hidden. Hashed on a grid
    of that size, so a city race's six thousand hidden objects cost nothing.
    """

    REACH = 0.1

    def __init__(self, positions: np.ndarray):
        self.positions = np.asarray(positions, dtype=np.float64).reshape(-1, 3)
        self.keys = np.unique(self._key(np.floor(self.positions / self.REACH).astype(np.int64)))

    @staticmethod
    def _key(cells: np.ndarray) -> np.ndarray:
        # 21 bits a coordinate: a tenth of a metre over two hundred kilometres.
        shifted = cells + (1 << 20)
        return (shifted[:, 0] << 42) | (shifted[:, 1] << 21) | shifted[:, 2]

    def __len__(self) -> int:
        return len(self.positions)

    def near(self, points: np.ndarray) -> np.ndarray:
        cells = np.floor(np.asarray(points, dtype=np.float64) / self.REACH).astype(np.int64)
        out = np.zeros(len(cells), dtype=bool)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    out |= np.isin(self._key(cells + np.array([dx, dy, dz])), self.keys)
        return out


def _unique(instances: np.ndarray) -> np.ndarray:
    """
    Drop exact repeats of one placement.

    A model near a cell boundary can be listed by both cells. Two copies at the
    same millimetre with the same orientation are one object.
    """
    key = np.round(instances[:, 0:9], 3)
    _, first = np.unique(key, axis=0, return_index=True)
    return instances[np.sort(first)]


def place_in_box(
    track: Track,
    low: tuple[float, float],
    high: tuple[float, float],
    *,
    categories=DEFAULT_CATEGORIES,
    budget: int | None = None,
    season: str = "summer",
    textures: bool = True,
    texture_size: int = MODEL_TEXTURE,
    route: np.ndarray | None = None,
    corridor=None,
    route_id: int | None = None,
    route_assets=None,
) -> Placed:
    """
    Every placed model standing inside a box, grouped into export parts.

    `route` is where the car drove, world positions (x, y, z) or (x, z). Detail
    goes to what stands near it; without one, to what stands near the middle
    of the box. With a `corridor`, nothing outside it is placed - the terrain
    under it has been cut away. `route_id`, the game's route the driving was
    matched to, decides which races' own layers are placed: that race's, and no
    other's. `route_assets` (`forzaroute.RouteAssets`) is that race's own layer
    from the game's route definitions: placed as the event parts, and what it
    hides of the free-roam world taken away.
    """
    from .forzatexture import TextureShelf

    manifest = Manifest.read(track.folder) if textures else None
    shelf = TextureShelf(track.folder) if manifest else None
    try:
        library = Textures(shelf, texture_size) if shelf else None
        models = ModelShelf(track, manifest, library, season)
        hidden_world = set()
        if route_assets is not None and len(route_assets.hidden):
            # A hidden copy standing at the origin is a model in world
            # coordinates (a stadium's lawn), known by its instance id only.
            from .forzaroute import instance_models

            at_origin = np.abs(route_assets.hidden).max(axis=1) < 0.01
            ids = [i for i, o in zip(route_assets.hidden_ids, at_origin) if o]
            hidden_world = set(instance_models(track.folder, ids).values())
        return _place(
            track, low, high, categories, budget, models, _plane(route, low, high), corridor,
            route_id if route_id is not None else getattr(route_assets, "id", None),
            route_assets, hidden_world,
        )
    finally:
        if shelf is not None:
            shelf.close()


def _plane(route, low, high) -> np.ndarray:
    """The route as (x, z) points, or the box's middle when there is none."""
    if route is None or not len(route):
        return np.array([[(low[0] + high[0]) / 2, (low[1] + high[1]) / 2]])
    route = np.asarray(route, dtype=np.float64)
    return route[:, [0, 2]] if route.shape[1] >= 3 else route[:, :2]


def _covered(points: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Which (x, z) points fall inside any of the (x0, z0, x1, z1) boxes."""
    out = np.zeros(len(points), dtype=bool)
    if not len(boxes) or not len(points):
        return out
    for start in range(0, len(points), 8192):
        block = points[start : start + 8192]
        inside = (
            (block[:, None, 0] >= boxes[None, :, 0])
            & (block[:, None, 0] <= boxes[None, :, 2])
            & (block[:, None, 1] >= boxes[None, :, 1])
            & (block[:, None, 1] <= boxes[None, :, 3])
        )
        out[start : start + 8192] = inside.any(axis=1)
    return out


def _place(
    track, low, high, categories, budget, models: ModelShelf, route: np.ndarray, corridor=None, route_id=None,
    route_assets=None, hidden_world=frozenset(),
) -> Placed:
    out = Placed(route_id=route_id)
    hidden = _Hidden(route_assets.hidden if route_assets is not None else np.zeros((0, 3)))
    stand_ins = []
    if "buildings" in categories and hasattr(track, "stand_ins"):
        stand_ins = [
            (stem, lo, hi)
            for stem, lo, hi in track.stand_ins()
            if hi[0] >= low[0] and lo[0] <= high[0] and hi[2] >= low[1] and lo[2] <= high[1]
            and (corridor is None or corridor.touches((lo[0], lo[2]), (hi[0], hi[2])))
        ]
    # A stand-in's footprint, a little generous: a piece standing on the edge
    # of the building it belongs to is still part of it.
    boxes = np.array([[lo[0] - 0.5, lo[2] - 0.5, hi[0] + 0.5, hi[2] + 0.5] for _s, lo, hi in stand_ins])

    found: dict[str, list[np.ndarray]] = defaultdict(list)
    part_of: dict[str, str] = {}
    layer_of_file = getattr(track, "layer", lambda number, entry: "")
    for number, entry, category in track.placement_files(low, high, categories):
        layer = layer_of_file(number, entry)
        races = routes_of(layer)
        if races and route_id not in races:
            # Another race's own layer: not there when this one is driven.
            continue
        try:
            placements = parse_pgeo(track.read(number, entry))
        except (UnsupportedForza, struct.error):
            continue
        for name, instances in placements.models.items():
            x, z = instances[:, 0], instances[:, 2]
            inside = (x >= low[0]) & (x <= high[0]) & (z >= low[1]) & (z <= high[1])
            if corridor is not None and inside.any():
                inside &= corridor.contains(instances[:, [0, 2]])
            if len(hidden):
                gone = inside & hidden.near(instances[:, 0:3])
                out.hidden += int(gone.sum())
                inside &= ~gone
            if category == "buildings" and not layer and len(boxes):
                covered = inside & _covered(instances[:, [0, 2]], boxes)
                out.replaced += int(covered.sum())
                inside &= ~covered
            if not inside.any():
                continue
            stem = models.stem(name)
            if KERB.match(stem):
                part = KERB_PART
            elif races:
                part = EVENT_PART.format(category)
            elif layer:
                part = LAYER_PART.format(category)
            else:
                part = CATEGORIES[category]
            # One model can stand in the world and in a layer; each is its own
            # entry, so the layer can be told apart and switched off.
            key = stem if part == CATEGORIES.get(category) or part == KERB_PART else f"{stem}@{part}"
            found[key].append(instances[inside])
            part_of[key] = part
            if layer:
                tally = out.event if races else out.layers
                tally[layer] = tally.get(layer, 0) + int(inside.sum())

    # Models already in world coordinates: a venue's ground, procedural bridges.
    world = []
    if hasattr(track, "world_models"):
        world = [
            (stem, part, lo, hi)
            for stem, part, lo, hi in track.world_models()
            if hi[0] >= low[0] and lo[0] <= high[0] and hi[2] >= low[1] and lo[2] <= high[1]
            and (corridor is None or corridor.touches((lo[0], lo[2]), (hi[0], hi[2])))
        ]
        # A race that hides a venue's ground lays its own surface there, and
        # that surface is not among the models the track ships (measured on a
        # stadium circuit: its laps ride on the hidden lawn's height). The
        # ground stays, as the nearest thing to what is driven on; anything
        # else the race hides goes.
        out.kept_ground = sorted(w[0] for w in world if w[0] in hidden_world and w[1] in WORLD_GROUND)
        out.hidden += sum(1 for w in world if w[0] in hidden_world and w[1] not in WORLD_GROUND)
        world = [w for w in world if w[0] not in hidden_world or w[1] in WORLD_GROUND]

    # The race's own layer: everything the game adds to the world for it.
    if route_assets is not None:
        for stem, instances in route_assets.models.items():
            x, z = instances[:, 0], instances[:, 2]
            inside = (x >= low[0]) & (x <= high[0]) & (z >= low[1]) & (z <= high[1])
            if corridor is not None and inside.any():
                inside &= corridor.contains(instances[:, [0, 2]])
            if not inside.any():
                continue
            kind = route_assets.kinds.get(stem, "props")
            category = kind if kind in CATEGORIES else "props"
            part = KERB_PART if KERB.match(stem) else EVENT_PART.format(category)
            key = f"{stem}@{part}"
            found[key].append(instances[inside])
            part_of[key] = part
            out.event[kind] = out.event.get(kind, 0) + int(inside.sum())

    loaded: dict[str, tuple[Model, np.ndarray]] = {}
    for key, chunks in found.items():
        stem = key.split("@")[0]
        model = models.load(stem)
        if model is None:
            (out.see_through if stem in models.see_through else out.missing).add(stem)
            continue
        loaded[key] = (model, _unique(np.concatenate(chunks)))

    # Each model's copies in three bands by distance from the driving, each band
    # its own entry in the budget: near copies start at the finest level, the
    # middle band one coarser, the far band at the coarsest.
    entries: dict[tuple[str, int], tuple[Model, np.ndarray, np.ndarray]] = {}
    for key, (model, instances) in loaded.items():
        distance = route_distance(instances[:, [0, 2]], route)
        band = np.digitize(distance, (NEAR, FAR))
        for number in np.unique(band):
            chosen = band == number
            entries[(key, int(number))] = (model, instances[chosen], distance[chosen])
    # The stand-ins: one copy each, in place already, at a distance measured to
    # the nearest edge of the building rather than to its middle.
    identity = np.array([[0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0]], dtype=np.float64)
    for stem, lo, hi in stand_ins:
        model = models.load(stem)
        if model is None:
            continue
        centre = np.array([[(lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2]])
        reach = np.hypot(hi[0] - lo[0], hi[2] - lo[2]) / 2
        distance = np.maximum(route_distance(centre, route) - reach, 0.0)
        entries[(stem, 0)] = (model, identity, distance)
        part_of[stem] = CATEGORIES["buildings"]
    for stem, part, lo, hi in world:
        model = models.load(stem)
        if model is None:
            continue
        centre = np.array([[(lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2]])
        reach = np.hypot(hi[0] - lo[0], hi[2] - lo[2]) / 2
        distance = np.maximum(route_distance(centre, route) - reach, 0.0)
        entries[(stem, 0)] = (model, identity, distance)
        part_of[stem] = part
        if part == VENUE_PART:
            out.venue.append(stem)
        else:
            out.world += 1

    costs = {name: (len(inst), [lv.triangles for lv in m.levels]) for name, (m, inst, _d) in entries.items()}
    # Kerbs and a venue's ground are what a lap is driven on and measured
    # against: never coarser, never left out.
    pinned = {name for name in entries if part_of[name[0]] in (KERB_PART, *WORLD_GROUND)}
    start = {name: (0, 1, 99)[name[1]] for name in entries}
    if budget is None:
        budget = auto_budget(costs, pinned)
    out.budget = budget
    chosen = choose_levels(costs, budget, pinned, start)
    keep = _fit(entries, costs, chosen, pinned, budget, out)

    blocks: dict[str, list] = defaultdict(list)
    for name, (model, instances, _distance) in sorted(entries.items()):
        key = name[0]
        instances = instances[keep[name]]
        if not len(instances):
            continue
        if key.startswith(HLOD):
            out.stand_ins += 1
        part = part_of[key]
        level = model.levels[chosen[name]]
        finest = out.levels.get(key, (len(model.levels), 0))[0]
        out.levels[key] = (min(finest, chosen[name]), len(model.levels))
        counts = out.counts.setdefault(part, {})
        counts[key] = counts.get(key, 0) + len(instances)
        variants = level.texture.shape[1]
        wearing = instances[:, 12].astype(np.int64) % variants
        for variant in np.unique(wearing):
            copies = instances[wearing == variant]
            positions, normals, faces = place(level, copies)
            uvs = np.tile(level.uvs, (len(copies), 1)) if level.uvs is not None else None
            face_texture = np.tile(level.texture[:, variant], len(copies))
            for index in np.unique(face_texture):
                texture = model.textures[index] if index >= 0 else None
                image = models.textures.image(texture) if (texture and models.textures) else None
                if image is None:
                    texture = None
                name = f"{part} {strip_guid(texture)}" if texture else part
                blocks[name].append(
                    (positions, normals, uvs if texture else None, faces[face_texture == index], texture, part)
                )
                if texture:
                    out.textures[texture] = image[:, :, :3]

    for name, pieces in blocks.items():
        out.parts[name] = _merge_blocks(pieces)
    return out


def _fit(entries, costs, chosen, pinned, budget, out: Placed) -> dict:
    """
    Which copies to keep: all of them, unless even their coarsest levels will
    not fit the budget - then the ones that look smallest from the road go
    first, until it does. Kerbs are never left out.

    "Look smallest" is distance over size. A city block is hundreds of
    thousands of pieces, most of them the size of an air conditioner; ordered by
    distance alone, a unit on a wall nine metres away outlives the twenty-metre
    facade it hangs on, twelve metres away.
    """
    keep = {name: np.ones(len(entries[name][1]), dtype=bool) for name in entries}
    out.considered = sum(len(entries[name][1]) for name in entries)
    total = sum(costs[name][0] * costs[name][1][chosen[name]] for name in entries)
    if total <= budget:
        return keep
    names = [name for name in entries if name not in pinned]
    if not names:
        return keep

    def visible(name):
        model, instances, distance = entries[name]
        scale = np.abs(instances[:, 9:12]).max(axis=1) if instances.shape[1] >= 12 else 1.0
        size = np.maximum(getattr(model, "size", 1.0) * np.where(scale > 0, scale, 1.0), 0.25)
        return distance / size

    ratio = np.concatenate([visible(name) for name in names])
    # What stands beside the road goes last, whatever its size: a three-metre
    # barrier five metres from the line is the edge of the track, and a
    # fifty-metre building sixty metres back is scenery - by distance over size
    # alone the building would win.
    beside = np.concatenate([entries[name][2] < NEAR for name in names])
    cost = np.concatenate(
        [np.full(len(entries[name][2]), costs[name][1][chosen[name]]) for name in names]
    )
    owner = np.concatenate([np.full(len(entries[name][2]), i) for i, name in enumerate(names)])
    index = np.concatenate([np.arange(len(entries[name][2])) for name in names])
    order = np.lexsort((-ratio, beside))
    shed = np.cumsum(cost[order])
    count = int(np.searchsorted(shed, total - budget)) + 1
    count = min(count, len(order))
    gone = order[:count]
    for i in gone:
        keep[names[owner[i]]][index[i]] = False
    out.dropped = count
    return keep


def _merge_blocks(pieces) -> Mesh:
    """Concatenate several models' copies into one part, keeping only used vertices."""
    positions, normals, uvs, faces = [], [], [], []
    offset = 0
    textured = pieces[0][4] is not None
    for p, n, uv, f, _texture, _part in pieces:
        used, inverse = np.unique(f, return_inverse=True)
        positions.append(p[used])
        normals.append(n[used])
        if textured:
            uvs.append(uv[used])
        faces.append(inverse.reshape(-1, 3).astype(np.int32) + offset)
        offset += len(used)
    part = pieces[0][5]
    return Mesh(
        positions=np.concatenate(positions),
        normals=np.concatenate(normals),
        uvs=np.concatenate(uvs) if textured else None,
        faces=np.concatenate(faces),
        texture=pieces[0][4],
        colour=fallback_colour(part),
    )


def fallback_colour(part: str) -> tuple[float, float, float]:
    """A part's flat colour; a layer's parts take their category's."""
    if part in FALLBACK_COLOURS:
        return FALLBACK_COLOURS[part]
    for template in (EVENT_PART, LAYER_PART):
        prefix = template.format("")
        if part.startswith(prefix):
            return FALLBACK_COLOURS.get(CATEGORIES.get(part[len(prefix):], ""), (0.5, 0.5, 0.5))
    return (0.5, 0.5, 0.5)


def place_in_track(folder: str | Path, low, high, **options) -> Placed:
    """The same, opening the track's archives for the call."""
    with Track(folder) as track:
        return place_in_box(track, low, high, **options)
