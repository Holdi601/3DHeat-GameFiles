"""
A Frostbite level as one model: its static meshes where the level puts them.

What places a mesh
------------------
A level is a tree of partitions — the level, its sub-worlds, their layers — and
the content pipeline gathers everything static in each of them into a static
model group: an array of members, one per mesh, each with an array of instance
transforms. That array is where nearly all of a level's buildings, props and
scenery are. Battlefield 6 ships no type library in readable form (see
`frostbiteebx`), so the member's layout was read off the data and is pinned here
by its type GUID and signature, which are in every partition that uses it::

    member (224 bytes)       +88   array of instance transforms
                             +112  the object blueprint, an import
                             +160  the mesh asset, an import
    instance transform (64)  right, up, forward, translation: four vec3,
                             each padded to sixteen bytes

The evidence for the reading: in the member arrays of a level, the field at +160
imports a partition named like a MeshSet in every member, and every one of the
41,277 copies of a level resolved to one; the array at +88 is always of the
64-byte type; its first three rows are a rotation, scaled — two in three copies
have a determinant of 1 to a thousandth, the rest are scaled or mirrored props —
and the translations draw the level's buildings where its sub-world names say
they are, on the terrain backdrop's hole for the play area. A mirrored copy
(negative determinant) has its triangles re-wound. The type GUIDs and signatures are the same in every
level, so a game update that changes the layout changes the signature, and the
reader then finds nothing and says so rather than misreading.

A point of a mesh lands at ``x·right + y·up + z·forward + translation``, in the
game's own frame: metres, Y up. The group's own transform is the identity in
every group of the levels checked, and is not applied.

The partition a member imports its mesh from is named after the mesh, so the
MeshSet res of the same name is the geometry.

What is not here
----------------
- Objects placed one by one rather than grouped: destructible prefabs and
  gameplay objects. They are a small part of what is drawn, and each kind has
  its own layout to pin down.
- The terrain's own colour at the resolution the game draws it near a player.
  The play area's heightfield (`frostbiteterrain`) is coloured from the terrain
  backdrop's colour map, 32 m a pixel.

The ground
----------
Two parts: `ground:terrain`, the heightfield of the terrain square, and
`ground:terrain backdrop`, the coarse terrain meshes the game draws for the
distance — tens of kilometres round the map, with a hole where the heightfield
is — which the level places in its own static model group. Meshes whose
material blends into the terrain are `ground:terrain blend`.

Textures
--------
With a texture size, each drawn section's colour map is found through the
level's shader block depots (`frostbitematerial`) and written with the
section's texture coordinates, which tile; the parts are then one per
category and texture, `structure:buildings t_<texture>`.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .frostbite import UnsupportedFrostbite
from .frostbitebundle import LevelCatalogue
from .frostbiteebx import Partition, partition_guid, read_partition
from .frostbitematerial import CUTOUT_NAME
from .frostbitemesh import MESHSET, decode_sections, read_meshset

#: The static model group member, and the transform its instances are.
MEMBER = (bytes.fromhex("ad13064e92c8195914bc2c0dee33e139"), 0xF861A878)
TRANSFORM = (bytes.fromhex("101dce064e9a64fc2a9fa9d482576ffa"), 0x5E6D8C37)

MEMBER_SIZE = 224
MEMBER_TRANSFORMS = 88
MEMBER_MESH = 160
#: An array of one pointer a copy: the object variation it is drawn in, or null.
MEMBER_VARIATIONS = 32
#: An object variation's type; its name hash is a u32 32 bytes into its instance.
OBJECT_VARIATION = bytes.fromhex("235f2a9c2c2819d359772c072bc47082")
VARIATION_HASH = 32
TRANSFORM_SIZE = 64

#: Part names by what a mesh's asset path says it is. The first match wins;
#: anything else is a prop. The patterns are Frostbite's own folder names.
CATEGORIES = (
    ("water:water", re.compile(r"water", re.I)),
    ("structure:trees", re.compile(r"/(vegetation|foliage|trees?)/|tree|bush|grass", re.I)),
    ("structure:rocks", re.compile(r"/rocks?/|rock|cliff|boulder", re.I)),
    ("structure:buildings", re.compile(r"/architecture/|building|house|wall", re.I)),
    ("structure:infrastructure", re.compile(r"road|bridge|pylon|pipeline|fence|rail", re.I)),
)
TERRAIN_PART = "ground:terrain"
#: The soldiers' walkable surfaces, from the level's navigation mesh.
NAV_PART = "nav:walkable"
#: The level's distant terrain meshes, and meshes that blend into the terrain.
BACKDROP_PART = "ground:terrain backdrop"
BLEND_PART = "ground:terrain blend"
GROUND_PARTS = (BACKDROP_PART, BLEND_PART)

#: Meshes that are effects rather than surfaces — smoke plumes, scaled up
#: hundreds of times into a sheet over the whole level — by their asset path.
EFFECTS = re.compile(r"(^|/)fx/", re.I)
#: Meshes made for cinematics: a helicopter flying through a scene, placed
#: where the scene starts and drawn there in cyan through its channel mask.
CINEMATIC = re.compile(r"/cinematics?/|_cin_mesh$", re.I)
#: Lighting helpers: planes that block light, never drawn in the game, which
#: stood out of a level as flat cards.
LIGHTING = re.compile(r"(^|/)lighting/meshes/|light_?blocker", re.I)

#: A mesh whose own bounding box is longer than this is not geometry this
#: reader decodes right: the level's cable sets declare boxes of 70 to 300
#: kilometres and are placed at zero scale. The terrain backdrop is exempt.
LARGEST = 20_000.0

#: Flat colours, as the other games' exports use for untextured parts.
COLOURS = {
    "ground:terrain": (0.42, 0.38, 0.30),
    "ground:terrain backdrop": (0.42, 0.38, 0.30),
    "ground:terrain blend": (0.45, 0.40, 0.32),
    "structure:buildings": (0.62, 0.60, 0.56),
    "structure:props": (0.55, 0.50, 0.42),
    "structure:trees": (0.25, 0.38, 0.20),
    "structure:rocks": (0.48, 0.45, 0.40),
    "structure:infrastructure": (0.45, 0.45, 0.47),
    "water:water": (0.20, 0.35, 0.50),
    "nav:walkable": (0.10, 0.80, 0.30),
}


def find_level(root: str | Path, name: str):
    """
    A level's tables (a `frostbitebundle.LevelTable`) by its name, or by a path
    to the `.toc` itself.
    """
    from .frostbitebundle import LevelTable, level_sources

    tables = level_sources(root)
    if Path(name).suffix.lower() == ".toc" and Path(name).is_file():
        toc = Path(name)
        known = tables.get(toc.stem.lower())
        supplements = known.supplements if known and known.toc.resolve() == toc.resolve() else ()
        return LevelTable(toc.stem.lower(), toc, "given", supplements)
    key = name.lower()
    if key in tables:
        return tables[key]
    near = sorted(t for t in tables if key in t)
    if len(near) == 1:
        return tables[near[0]]
    raise UnsupportedFrostbite(
        f"no level called {name!r}"
        + (f"; did you mean one of {', '.join(near)}?" if near else "; `levels` lists them")
    )


def ebx_prefix(toc: Path) -> str:
    """
    The path a level's own partitions are named under.

    A level's table sits at `Data/Win32/<path>/<level>.toc`, and its partitions
    are named `<path>/...` — lower case, forward slashes.
    """
    parts = [p.lower() for p in toc.parent.parts]
    if "win32" not in parts:
        raise UnsupportedFrostbite(f"{toc} is not under a Win32 folder")
    return "/".join(parts[parts.index("win32") + 1 :]) + "/"


@dataclass
class Placements:
    #: Mesh name -> instance transforms, (N, 4, 4) float32 rows as stored.
    meshes: dict[str, list[np.ndarray]] = field(default_factory=dict)
    #: Partition name -> copies placed from it.
    partitions: dict[str, int] = field(default_factory=dict)
    #: Members whose mesh import names no MeshSet the level has.
    unresolved: int = 0
    #: Copies placed one by one, by object and prefab references.
    objects: int = 0
    #: Grouped copies drawn in an object variation rather than as the mesh is.
    variations: int = 0

    def copies(self) -> int:
        return sum(len(t) for blocks in self.meshes.values() for t in blocks)


def _members(partition: Partition, name: str) -> list[tuple[int, np.ndarray, list[int | None]]]:
    """
    (import index of the mesh, transforms, import index of each copy's object
    variation or None) for each member of each group.
    """
    member = partition.type_index(*MEMBER)
    transform = partition.type_index(*TRANSFORM)
    if not member:
        return []
    data = partition.data
    out = []
    for array in partition.arrays:
        if array.type not in member:
            continue
        for i in range(array.count):
            at = array.offset + i * MEMBER_SIZE
            if at + MEMBER_SIZE > len(data):
                raise UnsupportedFrostbite(f"{name}: a group member runs past the data")
            kind, index = partition.pointer(at + MEMBER_MESH)
            if kind != "import":
                continue
            block = partition.array_at(at + MEMBER_TRANSFORMS)
            if block is None or block.type not in transform:
                raise UnsupportedFrostbite(
                    f"{name}: member {i} has no transform array where one should be; "
                    "the member layout is not the one this reader knows"
                )
            if not block.count:
                continue
            rows = np.frombuffer(
                data, dtype="<f4", count=16 * block.count, offset=block.offset
            ).reshape(block.count, 4, 4)
            variations: list[int | None] = [None] * block.count
            chosen = partition.array_at(at + MEMBER_VARIATIONS)
            if chosen is not None and chosen.count == block.count:
                for k in range(chosen.count):
                    what, which = partition.pointer(chosen.offset + 8 * k)
                    variations[k] = which if what == "import" else None
            out.append((index, rows.copy(), variations))
    return out


def variation_hash(level: LevelCatalogue, name: str) -> int:
    """An object variation partition's name hash, 0 when it is not one."""
    entry = level.ebx.get(name)
    if entry is None:
        return 0
    try:
        part = read_partition(level.read(entry.location), name)
    except UnsupportedFrostbite:
        return 0
    if not part.instances:
        return 0
    at = part.instances[0]
    (kind,) = struct.unpack_from("<H", part.data, at)
    if kind not in part.type_index(OBJECT_VARIATION) or at + VARIATION_HASH + 4 > len(part.data):
        return 0
    return struct.unpack_from("<I", part.data, at + VARIATION_HASH)[0]


def find_placements(
    level: LevelCatalogue,
    prefix: str,
    skip: tuple[str, ...] = (),
    report=print,
    partitions: dict[bytes, str] | None = None,
) -> Placements:
    """
    Every grouped mesh copy the level's partitions place, each carrying its
    object variation's hash (see `with_variations`) when `partitions`
    (partition GUID -> name) is given to find the variations by.

    `skip` leaves out partitions whose name contains any of the given strings —
    a game mode's layer, say, when only the common layout is wanted.
    """
    placements = Placements()
    meshes = {e.name for e in level.res.values() if e.res_type == MESHSET}
    guid_names: dict[bytes, str] = {}
    pending: list[tuple[str, bytes, np.ndarray, np.ndarray]] = []
    hashes: dict[bytes, int] = {}

    names = sorted(n for n in level.ebx if n.startswith(prefix))
    if not names:
        raise UnsupportedFrostbite(f"no partition of {level.toc.name} is named under {prefix}")
    for name in names:
        if any(s and s.lower() in name for s in skip):
            continue
        raw = level.read(level.ebx[name].location)
        if MEMBER[0] not in raw:
            continue
        partition = read_partition(raw, name)
        found = _members(partition, name)
        for index, rows, variations in found:
            chosen = np.zeros(len(rows), dtype=np.uint32)
            for k, which in enumerate(variations):
                if which is None or partitions is None:
                    continue
                guid = partition.imports[which][0]
                if guid not in hashes:
                    hashes[guid] = variation_hash(level, partitions[guid]) if guid in partitions else 0
                chosen[k] = hashes[guid]
            pending.append((name, partition.imports[index][0], with_variations(rows, chosen), chosen))

    wanted = {guid for _, guid, _, _ in pending}
    for mesh in sorted(meshes):
        if mesh in level.ebx and len(guid_names) < len(wanted):
            guid = partition_guid(level.read(level.ebx[mesh].location))
            if guid in wanted:
                guid_names[guid] = mesh

    for name, guid, rows, chosen in pending:
        mesh = guid_names.get(guid)
        if mesh is None:
            placements.unresolved += 1
            continue
        placements.meshes.setdefault(mesh, []).append(rows)
        placements.variations += int(np.count_nonzero(chosen))
        short = name[len(prefix) :]
        placements.partitions[short] = placements.partitions.get(short, 0) + len(rows)
    return placements


#: Objects placed one by one: an object reference places an object blueprint,
#: a prefab reference a prefab of further references. Both carry a
#: LinearTransform at +32 (right, up, forward, translation, each a vec3 padded
#: to 16) and the blueprint as an import at +112.
OBJECT_REFERENCE = (bytes.fromhex("a9a6a6ad0d73a898e77c534f52b03d78"), 0xC4856BEC)
PREFAB_REFERENCE = (bytes.fromhex("117c746e0f2b24f790846b609eb8dd3e"), 0xDE3FE9B4)
#: What a partition is, by its first instance: a prefab's definition, or a
#: world or layer that places things. Only the latter are walked from.
PREFAB_BLUEPRINT = (bytes.fromhex("134919fc829d1166507c3345a01b1a05"), 0x0247807D)
#: Blueprints staged out of play, which no player sees: development and test
#: assets, the round-end cinematic's set (a helicopter and light blockers
#: 47 m under the ground in three levels) and the death camera's controller,
#: whose gadgets stand at the world's origin.
STAGED = re.compile(r"^(game/dev/|test/)|/deathflow/|_gameend_")
REFERENCE_TRANSFORM = 32
REFERENCE_BLUEPRINT = 112
#: The object variation an object reference draws its blueprint in, or null.
REFERENCE_VARIATION = 120

#: Prefabs nest; deeper than this is a loop or a mistake.
PREFAB_DEPTH = 8


def partition_names(level: LevelCatalogue) -> dict[bytes, str]:
    """Every partition's GUID -> its name: what an import's GUID refers to."""
    names: dict[bytes, str] = {}
    for name, entry in level.ebx.items():
        try:
            names[partition_guid(level.read(entry.location))] = name
        except UnsupportedFrostbite:
            continue
    return names


def _matrix(rows: np.ndarray) -> np.ndarray:
    """A LinearTransform's four rows as a 4 x 4 matrix acting on row vectors."""
    out = np.zeros((4, 4), dtype=np.float64)
    out[:, :3] = rows[:, :3]
    out[3, 3] = 1.0
    return out


def find_objects(
    level: LevelCatalogue, prefix: str, names: dict[bytes, str], skip: tuple[str, ...] = ()
) -> Placements:
    """
    Every mesh that object and prefab references place, through nested
    prefabs, in world space.

    These are what the content pipeline could not group: destructible
    objects, containers, debris piles. A grouped prefab is referenced as its
    `..._nongroupable_autogen` remainder, so nothing here is also in a static
    model group. An object blueprint is drawn as the meshes it imports — the
    intact ones, not the destroyed (`dc_`) states.

    The walk starts only from worlds and layers: not from a prefab's
    definition (its first instance a prefab blueprint), nor from a partition a
    reference names. A level keeps many of its prefabs under its own folder,
    placed by its worlds in ways other than these references, and a prefab
    walked from as if it were the world puts its contents at its local
    coordinates: in the test level 1,742 copies of barriers, sandbags and
    chairs piled round the world's origin, 120 m under the ground.
    """
    meshes = {e.name for e in level.res.values() if e.res_type == MESHSET}
    found = Placements()
    cache: dict[str, Partition | None] = {}
    hashes: dict[bytes, int] = {}

    def partition(name: str) -> Partition | None:
        if name not in cache:
            entry = level.ebx.get(name)
            cache[name] = None
            if entry is not None:
                try:
                    cache[name] = read_partition(level.read(entry.location), name)
                except UnsupportedFrostbite:
                    pass
        return cache[name]

    def references(part: Partition):
        """(transform rows, target partition, variation hash) of each reference in a partition."""
        kinds = set(part.type_index(*OBJECT_REFERENCE)) | set(part.type_index(*PREFAB_REFERENCE))
        for at in part.instances:
            (kind,) = struct.unpack_from("<H", part.data, at)
            if kind not in kinds:
                continue
            what, index = part.pointer(at + REFERENCE_BLUEPRINT)
            if what != "import":
                continue
            target = names.get(part.imports[index][0])
            if target is None or STAGED.search(target):
                continue
            chosen = 0
            if at + REFERENCE_VARIATION + 8 <= len(part.data):
                what, which = part.pointer(at + REFERENCE_VARIATION)
                if what == "import":
                    guid = part.imports[which][0]
                    if guid not in hashes:
                        hashes[guid] = variation_hash(level, names[guid]) if guid in names else 0
                    chosen = hashes[guid]
            yield np.frombuffer(part.data, dtype="<f4", count=16, offset=at + REFERENCE_TRANSFORM), target, chosen

    def visit(name: str, parent: np.ndarray, depth: int, origin: str, variation: int = 0) -> None:
        part = partition(name)
        if part is None or depth > PREFAB_DEPTH:
            return
        kinds = set(part.type_index(*OBJECT_REFERENCE)) | set(part.type_index(*PREFAB_REFERENCE))
        drawn = [
            names.get(guid) for guid, _ in part.imports
            if names.get(guid) in meshes and not names.get(guid).rsplit("/", 1)[-1].startswith("dc_")
        ]
        if depth > 0 and not kinds:
            for mesh in dict.fromkeys(drawn):
                rows = np.zeros((1, 4, 4), dtype=np.float32)
                rows[0, :, :3] = parent[:, :3]
                found.meshes.setdefault(mesh, []).append(with_variations(rows, [variation]))
                found.variations += bool(variation)
                found.partitions[origin] = found.partitions.get(origin, 0) + 1
            return
        for rows, target, chosen in references(part):
            local = _matrix(rows.reshape(4, 4).astype(np.float64))
            visit(target, local @ parent, depth + 1, origin, chosen or variation)

    holders = []
    targets: set[str] = set()
    for name in sorted(n for n in level.ebx if n.startswith(prefix)):
        raw = level.read(level.ebx[name].location)
        if OBJECT_REFERENCE[0] not in raw and PREFAB_REFERENCE[0] not in raw:
            continue
        part = partition(name)
        if part is None:
            continue
        targets.update(target for _rows, target, _chosen in references(part))
        (first,) = struct.unpack_from("<H", part.data, part.instances[0]) if part.instances else (-1,)
        if first not in part.type_index(*PREFAB_BLUEPRINT):
            holders.append(name)
    for name in holders:
        if name in targets or any(s and s.lower() in name for s in skip):
            continue
        visit(name, np.eye(4), 0, name[len(prefix):])
    return found


#: Materials of a stand-in for distant views, which a mesh's last level of
#: detail may switch to: a flat card or silhouette (`M_LastLod`, `M_Billboard`,
#: `M_Vista`, `M_ProjectionLod`). A power pylon's lattice of 32,080 triangles
#: ends in a 164-triangle `M_Vista` silhouette, which drawn up close is a
#: solid dark spike 64 m tall.
PROXY_MATERIAL = re.compile(r"last_?lod|billboard|vista|projection|project_?lod|(^|_)lod(_?\d+)?$", re.I)


#: What a destructible mesh's parts are named with: a mesh is destructible
#: when the level has a destruction asset of its own name
#: (`.../br_x.destruction` beside `.../br_x_mesh`), the breakable buildings,
#: walls and props a match can knock down. Its parts carry
#: `{"destructible": true}` as glTF extras.
DESTRUCTIBLE = " (destructible)"
DESTRUCTION_SUFFIX = ".destruction"


def destructible(level, mesh: str) -> bool:
    """Whether the level has a destruction asset named after the mesh."""
    stem = mesh[: -len("_mesh")] if mesh.endswith("_mesh") else mesh
    return stem + DESTRUCTION_SUFFIX in level.res or stem + DESTRUCTION_SUFFIX in level.ebx


#: Placeholder blockout materials: a few large untextured triangles some
#: buildings keep beside their real surfaces, which stand out of the level as
#: white fins.
BLOCKOUT = re.compile(r"whitebox|blockout", re.I)


def with_variations(rows: np.ndarray, hashes: np.ndarray) -> np.ndarray:
    """
    Rows that carry each copy's object variation hash in their fourth column,
    which a LinearTransform does not use (0: the mesh as it is).
    """
    rows = rows.copy()
    rows[:, :, 3] = 0.0
    rows[:, 0, 3] = np.asarray(hashes, dtype=np.uint32).view(np.float32)
    return rows


def variation_hashes(rows: np.ndarray) -> np.ndarray:
    """The object variation hash each copy carries (see `with_variations`)."""
    return np.ascontiguousarray(rows[:, 0, 3]).view(np.uint32)


def variant_keys(key: bytes, hashes: np.ndarray, links) -> list[bytes]:
    """
    The shader block key each copy of a section draws with: its variation's
    (see `MaterialLinks.variant`), or its own where the variation leaves the
    section as it is.
    """
    if links is None:
        return [key] * len(hashes)
    out = []
    cache: dict[int, bytes] = {}
    for h in hashes.tolist():
        if h not in cache:
            cache[h] = links.variant(key, h) or key
        out.append(cache[h])
    return out


def _proxy(lod, finest) -> bool:
    """Whether a level of detail is a distant-view stand-in rather than the mesh."""
    own = {s.material.lower() for i, s in enumerate(finest.sections) if i in finest.drawn}
    return any(
        PROXY_MATERIAL.search(s.material) and s.material.lower() not in own
        for i, s in enumerate(lod.sections)
        if i in lod.drawn
    )


def category(mesh: str, materials: list[str]) -> str:
    lowered = [m.lower() for m in materials]
    # Backdrop terrain is named one of three ways: `M_TerrainBackdrop`, a
    # backdrop-prefixed terrain material such as `M_BD_<site>_Terrain..._Near`,
    # or a plain terrain material (`M_<region>_Terrain<site>_04_Far`) on a
    # backdrop mesh, `bd_..._terrain<site>_04_far_mesh`.
    tail = mesh.rsplit("/", 1)[-1].lower()
    if any("terrainbackdrop" in m or ("bd_" in m and "terrain" in m) for m in lowered) or (
        tail.startswith("bd_") and "terrain" in tail and any("terrain" in m for m in lowered)
    ):
        return BACKDROP_PART
    if any("terrain" in m.lower() for m in materials):
        return BLEND_PART
    path = "/" + mesh
    for part, pattern in CATEGORIES:
        if pattern.search(path):
            return part
    return "structure:props"


def place(positions: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Every copy of a mesh in world space: (copies x vertices, 3)."""
    rotation = rows[:, :3, :3].astype(np.float64)
    translation = rows[:, 3, :3].astype(np.float64)
    world = np.einsum("vi,cij->cvj", positions.astype(np.float64), rotation) + translation[:, None, :]
    return world.reshape(-1, 3)


@dataclass
class Piece:
    """One export part: its points, triangles, and texture coordinates if textured."""

    points: list[np.ndarray] = field(default_factory=list)
    faces: list[np.ndarray] = field(default_factory=list)
    uvs: list[np.ndarray] = field(default_factory=list)
    texture: str | None = None
    count: int = 0

    def add(self, points: np.ndarray, faces: np.ndarray, uvs: np.ndarray | None = None) -> None:
        self.faces.append(faces + self.count)
        self.points.append(points.astype(np.float32))
        if self.texture is not None:
            self.uvs.append(uvs.astype(np.float32))
        self.count += len(points)


@dataclass
class LevelModel:
    parts: dict[str, Piece] = field(default_factory=dict)
    placements: Placements = field(default_factory=Placements)
    budget: int = 0
    coarser: int = 0
    #: Copies left out because even at their coarsest the budget would not
    #: hold them, of how many there were.
    dropped: int = 0
    skipped: dict[str, str] = field(default_factory=dict)
    #: Texture name -> decoded image (None when it could not be decoded).
    images: dict[str, np.ndarray | None] = field(default_factory=dict)
    #: Drawn sections given a colour map, of all drawn sections placed.
    textured: tuple[int, int] = (0, 0)
    #: What the ground is, for the summary.
    ground: str = ""
    #: Triangles drawn in their texture's average colour: see `UNTILE_PIECES`.
    flattened: int = 0
    #: What the navigation mesh part holds, for the summary.
    navmesh: str = ""
    #: Triangles of placeholder blockout sections left out: see `BLOCKOUT`.
    blockout: int = 0
    #: Drawn copies of sections given their object variation's own shader block.
    varied: int = 0
    #: Triangles of destructible meshes: see `DESTRUCTIBLE`.
    destructible: int = 0
    #: Drawn sections given their object's overlay through its second texture
    #: coordinates rather than their colour map.
    overlaid: int = 0
    #: Section copies whose cut-out sheet is laid on by a later texture
    #: coordinate set (see `_sheet_uvs`).
    sheets: int = 0
    #: The heightfield's flat colour when no colour map covers it.
    ground_colour: tuple[float, float, float] | None = None

    def triangles(self) -> int:
        return sum(len(f) for piece in self.parts.values() for f in piece.faces)


#: Swatches a palette side has: 16 x 16 cells of 16 texels in the 256 x 256
#: palettes of the levels checked.
PALETTE_CELLS = 16


def _sheet_uvs(section) -> np.ndarray | None:
    """
    The texture coordinates a cut-out sheet is laid over its section with,
    where they are not the first set.

    A warehouse's painted number is a section of the wall whose first set
    tiles the wall's plaster across the panel - u -0.2 to 1.7 - while the
    number sheet, a single "01" in its alpha over solid paint, is laid over
    the panel exactly once by the fourth set (u -1 to 0, v 1 to 2). Drawn
    through the first, the panel shows the number almost twice. So where the
    first set leaves one copy of the image and the fourth (else the third)
    lies within one copy, spanning a real part of it, that set is used,
    moved by whole copies into 0..1. The second set is an object's unwrap
    for its overlay (see the overlay rule) and is not taken here.
    """
    if section.uvs is None or not len(section.uvs):
        return None
    lo, hi = section.uvs.min(axis=0), section.uvs.max(axis=0)
    if (np.floor(lo + 0.01) == np.floor(hi - 0.01)).all():
        return None
    for uvs in (section.uvs4, section.uvs3):
        if uvs is None or not len(uvs):
            continue
        # Stored as halves, a corner meant to sit on a whole number lands a
        # few thousandths past it in the coarser levels of detail.
        lo, hi = uvs.min(axis=0), uvs.max(axis=0)
        cell = np.floor(lo + 0.01)
        if (cell == np.floor(hi - 0.01)).all() and ((hi - lo) > 0.05).all():
            return np.clip(uvs - cell, 0.0, 1.0).astype(np.float32)
    return None


#: How far a sheet is drawn in front of the surface it is painted on, in
#: metres: enough that the two do not fight over which is nearer at a
#: distance, too little to see.
SHEET_LIFT = 0.01


def _lifted(points: np.ndarray, faces: np.ndarray, distance: float) -> np.ndarray:
    """Points moved `distance` along the normals of the triangles they make, outwards by their winding."""
    p = points.astype(np.float64)
    face = np.cross(p[faces[:, 1]] - p[faces[:, 0]], p[faces[:, 2]] - p[faces[:, 0]])
    normal = np.zeros_like(p)
    for corner in range(3):
        np.add.at(normal, faces[:, corner], face)
    length = np.linalg.norm(normal, axis=1, keepdims=True)
    return p + np.where(length > 0, normal / np.maximum(length, 1e-12), 0.0) * distance


def _unwrapped(uvs: np.ndarray) -> bool:
    """Texture coordinates that lie within one copy of the image: an unwrap, not a tiling."""
    return bool(len(uvs)) and float(uvs.min()) >= -0.05 and float(uvs.max()) <= 1.05


def _palette_uvs(palette: np.ndarray) -> np.ndarray:
    """Texture coordinates at the centre of the swatch each vertex names (x, y out of 255)."""
    cell = np.floor(palette[:, :2].astype(np.float32) / 256 * PALETTE_CELLS)
    return ((cell + 0.5) / PALETTE_CELLS).astype(np.float32)


#: A colour map whose channels' means differ by less than this share of the
#: brightest is grey: the shader paints it with the material's tint.
GREY_MAP = 0.06


def _tinted(model, texture: str, tint) -> str:
    """
    The texture a section is drawn with once its block's tint is laid on: a
    grey map times the tint, in linear light, kept under a name of its own;
    a map with colour of its own, or a neutral tint, unchanged.
    """
    if tint is None:
        return texture
    image = model.images[texture]
    means = image[..., :3].reshape(-1, 3).mean(0)
    if means.max() - means.min() > GREY_MAP * max(means.max(), 1.0):
        return texture
    name = f"{texture} tinted {tint[0]:.3f} {tint[1]:.3f} {tint[2]:.3f}"
    if name not in model.images:
        linear = (image[..., :3].astype(np.float32) / 255.0) ** 2.2 * np.asarray(tint, np.float32)
        rgb = (np.clip(linear, 0.0, 1.0) ** (1 / 2.2) * 255.0 + 0.5).astype(np.uint8)
        model.images[name] = np.concatenate([rgb, image[..., 3:]], axis=-1) if image.shape[-1] == 4 else rgb
    return name


def _short(texture: str) -> str:
    return texture.rsplit("/", 1)[-1]


def build_level(
    root: str | Path,
    name: str,
    *,
    budget: int | None = None,
    skip: tuple[str, ...] = (),
    textures: int = 0,
    ground_spacing: float = 4.0,
    ground_texture: float = 0.0,
    navmesh: bool = False,
    by_mesh: bool = False,
    report=print,
) -> LevelModel:
    """
    Read a level and place its meshes, at levels of detail that fit `budget`.

    `textures` is the largest texture side to write, in pixels; 0 writes flat
    colours. The terrain heightfield is drawn no finer than `ground_spacing`
    metres; 0 leaves it out. `ground_texture`, in metres a pixel, bakes the
    terrain decals into the heightfield's colour where they are; 0 does not.
    """
    from .forzaplacement import DEFAULT_BUDGET, auto_budget, choose_levels

    table = find_level(root, name)
    toc = table.toc
    level = LevelCatalogue(toc, table.supplements)
    prefix = ebx_prefix(toc)
    report(f"{toc.stem}: {level.bundle_count} bundles, {len(level.ebx):,} partitions, {len(level.res):,} resources")
    names = partition_names(level)
    placements = find_placements(level, prefix, skip, report, names)
    objects = find_objects(level, prefix, names, skip)
    for mesh, blocks in objects.meshes.items():
        placements.meshes.setdefault(mesh, []).extend(blocks)
    placements.objects = sum(objects.partitions.values())
    placements.variations += objects.variations
    model = LevelModel(placements=placements)
    links = None
    if textures or ground_texture:
        from .frostbitematerial import link_materials

        links = link_materials(level)

    sets = {}
    costs = {}
    for mesh in placements.meshes:
        if EFFECTS.search(mesh):
            model.skipped[mesh] = "an effect, not a surface"
            continue
        if CINEMATIC.search(mesh):
            model.skipped[mesh] = "made for a cinematic"
            continue
        if LIGHTING.search(mesh):
            model.skipped[mesh] = "a lighting helper, not drawn"
            continue
        entry = level.res[mesh]
        try:
            meshset = read_meshset(level.read(entry.location), mesh)
        except UnsupportedFrostbite as exc:
            model.skipped[mesh] = str(exc)
            continue
        rows = np.concatenate(placements.meshes[mesh])
        # A copy scaled to nothing draws nothing.
        rows = rows[np.abs(np.linalg.det(rows[:, :3, :3].astype(np.float64))) > 1e-9]
        if not len(rows):
            model.skipped[mesh] = "every copy is scaled to nothing"
            continue
        placements.meshes[mesh] = [rows]
        lods = [lod for lod in meshset.lods if lod.chunk != bytes(16) and lod.chunk in level.chunks]
        lods = lods[:1] + [lod for lod in lods[1:] if not _proxy(lod, lods[0])]
        if not lods:
            model.skipped[mesh] = "no level of detail stored in a chunk"
            continue
        terrain_like = category(mesh, [x.material for x in lods[0].sections]) in GROUND_PARTS
        if not terrain_like and np.linalg.norm(meshset.high - meshset.low) > LARGEST:
            model.skipped[mesh] = "a bounding box tens of kilometres long"
            continue
        sets[mesh] = (meshset, lods)
        copies = sum(len(r) for r in placements.meshes[mesh])
        costs[mesh] = (copies, [lod.triangles for lod in lods])

    terrain = {
        m for m, (s, lods) in sets.items()
        if category(m, [x.material for x in lods[0].sections]) in GROUND_PARTS
    }
    model.budget = budget if budget else max(DEFAULT_BUDGET, auto_budget(costs, pinned=terrain))
    chosen = choose_levels(costs, model.budget, pinned=terrain)
    model.coarser = sum(1 for m, level_ in chosen.items() if level_ > 0)
    keep = _fit(sets, placements, chosen, terrain, model)

    textured = drawn = 0
    backdrop_uv: list[tuple[np.ndarray, np.ndarray, str]] = []
    for mesh, (meshset, lods) in sets.items():
        lod = lods[chosen[mesh]]
        try:
            sections = decode_sections(lod, level.chunk(lod.chunk), mesh)
        except UnsupportedFrostbite as exc:
            model.skipped[mesh] = str(exc)
            continue
        rows = np.concatenate(placements.meshes[mesh])[keep[mesh]]
        if not len(rows) or not sections:
            continue
        kind = category(mesh, [s.material for s in lod.sections])
        mirrored = np.linalg.det(rows[:, :3, :3].astype(np.float64)) < 0
        variations = variation_hashes(rows)
        breakable = destructible(level, mesh)
        for section in sections:
            if BLOCKOUT.search(section.material):
                model.blockout += len(section.faces) * len(rows)
                continue
            drawn += 1
            keys = variant_keys(lod.sections[section.index].key, variations, links)
            for key in dict.fromkeys(keys):
                chosen_rows = np.array([k == key for k in keys])
                group, flipped = rows[chosen_rows], mirrored[chosen_rows]
                if key != lod.sections[section.index].key:
                    model.varied += len(group)
                texture = None
                if textures and links is not None and section.uvs is not None:
                    texture = links.variant_colour_map(mesh, section.material, key, lod.sections[section.index].key)
                if texture is not None and texture not in model.images:
                    try:
                        model.images[texture] = _colour_map(level, links, texture, textures)
                    except UnsupportedFrostbite:
                        model.images[texture] = None
                if texture is not None and model.images[texture] is None:
                    texture = None
                uvs_of = section.uvs
                image = model.images.get(texture) if texture is not None else None
                sheet = None
                if image is not None and CUTOUT_NAME.search(texture.rsplit("/", 1)[-1]):
                    sheet = _sheet_uvs(section)
                    if sheet is not None:
                        uvs_of = sheet
                        model.sheets += len(group)
                        if image.ndim != 3 or image.shape[2] != 4:
                            # Opaque - a billboard's print: it covers its
                            # panel and needs nothing under it.
                            sheet = None
                overlay = links.overlay(key) if textures and links is not None else None
                if overlay is not None and section.uvs2 is not None and _unwrapped(section.uvs2):
                    # An object's overlay (its painted bands, rust and panels) is
                    # an unwrap of the whole object in the second coordinate set,
                    # where the colour map tiles a trim sheet through the first;
                    # the overlay is what the object looks like from afar.
                    if overlay not in model.images:
                        try:
                            model.images[overlay] = _colour_map(level, links, overlay, textures)
                        except UnsupportedFrostbite:
                            model.images[overlay] = None
                    if model.images[overlay] is not None:
                        texture, uvs_of = overlay, section.uvs2
                        model.overlaid += 1
                if texture is not None and links is not None:
                    texture = _tinted(model, texture, links.tints.get(key))
                if texture is None and textures and links is not None and section.palette is not None:
                    # A backdrop that looks its colours up in a palette: each
                    # vertex says which swatch, so the palette is drawn through
                    # those, each at its swatch's centre.
                    palette = links.palette(key)
                    if palette is not None and palette not in model.images:
                        try:
                            model.images[palette] = _colour_map(level, links, palette, textures)
                        except UnsupportedFrostbite:
                            model.images[palette] = None
                    if palette is not None and model.images[palette] is not None:
                        texture, uvs_of = palette, _palette_uvs(section.palette)
                textured += texture is not None
                world = place(section.positions, group)
                copies = len(group)
                tri = section.faces[None, :, :] + (np.arange(copies) * len(section.positions))[:, None, None]
                # A mirrored copy turns its triangles inside out; winding them the
                # other way round keeps the computed normals pointing outwards.
                tri[flipped] = tri[flipped][:, :, ::-1]
                part = kind if texture is None else f"{kind} {_short(texture)}"
                if breakable:
                    part += DESTRUCTIBLE
                    model.destructible += len(section.faces) * len(group)
                if by_mesh:
                    part = f"{part} | {mesh} | {section.material}"
                if sheet is not None:
                    # The surface the sheet is painted on, under it: the block's
                    # colour map other than the sheet, through the first set.
                    # Without it the sheet's empty texels show whatever is
                    # behind the panel - the inside of the wall.
                    base = links.colour_map(mesh, section.material, key, skip=CUTOUT_NAME)
                    if base is not None and base not in model.images:
                        try:
                            model.images[base] = _colour_map(level, links, base, textures)
                        except UnsupportedFrostbite:
                            model.images[base] = None
                    if base is not None and model.images[base] is not None:
                        base = _tinted(model, base, links.tints.get(key))
                        under = f"{kind} {_short(base)}" + (DESTRUCTIBLE if breakable else "")
                        if by_mesh:
                            under = f"{under} | {mesh} | {section.material}"
                        model.parts.setdefault(under, Piece(texture=base)).add(
                            world, tri.reshape(-1, 3), np.tile(section.uvs, (copies, 1))
                        )
                        world = _lifted(world, tri.reshape(-1, 3), SHEET_LIFT)
                piece = model.parts.setdefault(part, Piece(texture=texture))
                uvs = np.tile(uvs_of, (copies, 1)) if texture is not None else None
                piece.add(world, tri.reshape(-1, 3), uvs)
                if kind == BACKDROP_PART and links is not None and section.uvs is not None:
                    # The backdrop's colour map colours the heightfield, textured
                    # export or not.
                    colour = links.colour_map(mesh, section.material, key)
                    if colour is not None:
                        backdrop_uv.append((world, np.tile(section.uvs, (copies, 1)), colour))
    model.textured = (textured, drawn)

    if ground_spacing:
        _add_ground(level, model, ground_spacing, backdrop_uv, links, ground_texture, report)
    if navmesh:
        from .frostbitenav import soldier_layer

        walkable = soldier_layer(level, prefix)
        if walkable is None:
            model.navmesh = "no navigation mesh could be read"
        else:
            piece = Piece()
            piece.add(walkable.positions, walkable.faces)
            model.parts[NAV_PART] = piece
            model.navmesh = (
                f"{len(walkable.faces):,} triangles of {walkable.name.rsplit('/', 1)[-1]} "
                f"(agent {walkable.agent[0]:.1f} m tall, {walkable.agent[2]:.1f} m wide); "
                f"{walkable.refused} of {walkable.tiles:,} tiles refused"
            )
    return model


def _colour_map(level, links, texture: str, largest: int) -> np.ndarray:
    """
    A surface's colour map: RGBA when its alpha cuts the surface out (leaves,
    fences, decals; see `is_cutout`), else RGB.
    """
    from .frostbitematerial import CUTOUT_NAME, is_cutout

    if CUTOUT_NAME.search(texture.rsplit("/", 1)[-1]):
        rgba = _image(level, links, texture, largest, alpha=True)
        return rgba if is_cutout(texture, rgba) else np.ascontiguousarray(rgba[:, :, :3])
    return _image(level, links, texture, largest)


def _image(level, links, texture: str, largest: int, alpha: bool = False) -> np.ndarray:
    from .frostbitematerial import decode_texture

    info = links.headers[texture]
    if info.chunk not in level.chunks:
        raise UnsupportedFrostbite(f"{texture}: its chunk is not in this level")
    chunk = level.chunk(info.chunk)
    # The largest mips sit in a high-resolution pack's chunk; they are worth
    # reading only when a mip the main chunk lacks is wanted.
    if info.detail and info.detail in level.chunks and len(chunk) < sum(info.sizes):
        first = next((k for k in range(len(info.sizes)) if sum(info.sizes[k:]) == len(chunk)), 0)
        if first and min(info.width >> (first - 1), info.height >> (first - 1)) <= largest:
            detail = level.chunk(info.detail)
            if len(detail) + len(chunk) == sum(info.sizes):
                chunk = detail + chunk
    return decode_texture(info, chunk, largest, alpha)


def _add_ground(
    level, model: LevelModel, spacing: float, backdrop_uv, links=None, metres: float = 0.0, report=print
) -> None:
    """
    The heightfield as `ground:terrain`, coloured from the terrain backdrop's
    colour map where the backdrop has one: the backdrop's texture coordinates
    are a linear function of world x and z, fitted on its vertices, and the
    same function gives the heightfield's. In the level checked the map covers
    a 65,536 m square, turned a quarter (u follows z, v follows -x), and 99% of
    the backdrop's vertices sit within 0.001 of the fit, which is half-float
    rounding; the fit is used only if that holds. That is 32 m a pixel at the
    largest mip the level ships — the colour of the land, not of a path.
    """
    from .frostbiteterrain import STREAMING_TREE, build_ground, read_colormap, read_tree

    trees = [e for e in level.res.values() if e.res_type == STREAMING_TREE]
    if not trees:
        model.ground = "no terrain streaming tree; only the backdrop"
        return
    try:
        tree = read_tree(level.read(trees[0].location), trees[0].name)
        ground = build_ground(tree, level.chunk, spacing)
    except UnsupportedFrostbite as exc:
        model.ground = f"the heightfield could not be read ({exc}); only the backdrop"
        return
    colour = _backdrop_colour(level, links, backdrop_uv, ground, tree.square)
    # Where no backdrop map covers the heightfield, the ground is coloured from
    # the terrain's own surface materials before the backdrop round it: what a
    # backdrop shows can be another landscape altogether, and in one level its
    # average turned the play area's ground a grey the game does not show.
    surfaces = None
    layered = refused = None
    if (colour is None or colour[0] == "flat") and links is not None:
        try:
            layered = _layered_ground(level, links, tree)
        except UnsupportedFrostbite as exc:
            layered, refused = None, str(exc)
        surfaces = layered[1] if layered else _surface_colour(level, links)
        if surfaces is not None:
            colour = ("flat", surfaces)
    texture = uvs = base = None
    x0, _z0, x1, _z1 = tree.square
    model.ground = f"the heightfield, {x1 - x0:,.0f} m square, drawn at {spacing:g} m or coarser"
    if colour is not None and colour[0] == "map":
        _kind, name, fit, full = colour
        g = ground.positions[:, [0, 2]].astype(np.float64)
        uvs = (np.column_stack([g, np.ones(len(g))]) @ fit).astype(np.float32)
        # The heightfield is a small part of the map, so it gets its own crop
        # of the largest mip there is rather than the capped copy the backdrop
        # uses.
        h, w = full.shape[:2]
        lo = np.floor(uvs.min(axis=0) * (w, h)).astype(int).clip(0, (w - 1, h - 1))
        hi = np.ceil(uvs.max(axis=0) * (w, h)).astype(int).clip(lo + 1, (w, h))
        texture = name + " (heightfield)"
        model.images[texture] = np.ascontiguousarray(full[lo[1] : hi[1], lo[0] : hi[0]])
        uvs = ((uvs * (w, h) - lo) / (hi - lo)).astype(np.float32)
        model.ground += ", coloured from the terrain backdrop's colour map"
        base = _map_sampler(fit, full)
    elif colour is not None:
        flat = colour[1]
        model.ground += (
            f", {layered[2]}"
            if layered is not None
            else ", in the middle colour of the terrain's surface materials"
            + (f" ({refused})" if refused else "")
            if surfaces is not None
            else ", in the average colour of the terrain backdrop round it (no colour map "
            "of the level covers the heightfield)"
        )
        base = (
            layered[0]
            if layered is not None
            else lambda gx, gz: np.broadcast_to(np.array(flat, np.float32), gx.shape + (3,)).copy()
        )
        model.ground_colour = flat
    colormap = None
    if metres and base is not None:
        colormap = read_colormap(tree, level.chunk, lambda guid: guid in level.chunks)
    if colormap is not None:
        # The engine draws the colormap as an overlay on its splatted surface
        # layers: twice the layers' colour times the map's, so that mid-grey
        # leaves them as they are. Where the map has no texels the ground
        # takes its median brightness, grey, so that its edge does not show
        # as a step in brightness and its tint is not spread beyond it.
        plain = base
        known = colormap.image[colormap.image[..., 3] > 0, :3]
        grey = float(2.0 * np.median(known, axis=0).mean() / 255.0) if len(known) else 1.0
        tint = np.full(3, grey, np.float32)

        def base(gx, gz):
            overlay = 2.0 * colormap.sample(gx, gz)
            return plain(gx, gz) * np.where(np.isnan(overlay), tint, overlay)

        model.ground += ", under the terrain's colormap"
    keep = np.ones(len(ground.faces), dtype=bool)
    if metres and base is not None:
        keep = _bake_ground(level, links, model, ground, base, metres, report, colormap)
    elif metres:
        model.ground += "; no terrain backdrop colour to bake on"
    faces = ground.faces[keep]
    if len(faces):
        used, local = np.unique(faces, return_inverse=True)
        piece = Piece(texture=texture)
        piece.add(ground.positions[used], local.reshape(-1, 3), None if uvs is None else uvs[used])
        model.parts[TERRAIN_PART] = piece


@dataclass
class TerrainLayer:
    index: int
    colour_map: str | None
    colour: tuple[float, float, float] | None


def terrain_layers(level, links) -> list[TerrainLayer]:
    """
    The terrain's surface layers, by the index the mask records use: the
    layer-graph res lists one 32-byte entry per layer, in index order, each
    naming its section key in the layer graph's shader block depot; the block
    names the layer's maps, and its `_cv` map is the layer's colour. In one
    level the res has 34 entries, the depot 34 sections, and the records'
    layer indices run 0 to 33. A layer's colour is its map's mean: the tiling
    scale is not found, so the map is not drawn tiled.
    """
    from .frostbitematerial import SHADER_BLOCK_DEPOT

    graphs = [e for e in level.res.values() if "layergraph" in e.name and e.res_type != SHADER_BLOCK_DEPOT]
    depots = [e for e in level.res.values() if "layergraph" in e.name and e.res_type == SHADER_BLOCK_DEPOT]
    if not graphs or not depots:
        return []
    graph = level.read(graphs[0].location)
    depot = level.read(depots[0].location)
    blocks: dict[bytes, bytes] = {}
    at = 16
    while at + 16 <= len(depot):
        key = depot[at : at + 8]
        (where,) = struct.unpack_from("<Q", depot, at + 8)
        if not 0 < where <= len(depot) - 24:
            break
        block_at, _hash, size = struct.unpack_from("<QQQ", depot, where)
        blocks[key] = depot[block_at : block_at + size]
        at += 16
    layers = []
    for p in range(len(graph) - 7):
        key = graph[p : p + 8]
        if key not in blocks:
            continue
        block = blocks[key]
        names = [
            links.by_guid[block[q : q + 16]] for q in range(len(block) - 15) if block[q : q + 16] in links.by_guid
        ]
        colour_map = next(
            (n for n in names if n.rsplit("/", 1)[-1].endswith("_cv") and "default" not in n), None
        )
        colour = None
        if colour_map is not None and colour_map in links.headers:
            try:
                colour = tuple(float(v) for v in _image(level, links, colour_map, 64).reshape(-1, 3).mean(axis=0) / 255.0)
            except UnsupportedFrostbite:
                colour = None
        layers.append(TerrainLayer(len(layers), colour_map, colour))
    return layers


def _upsample(coarse: np.ndarray, step: int, h: int, w: int) -> np.ndarray:
    """A grid sampled every `step` texels, bilinearly back to h x w texels."""
    rows = np.minimum(np.arange(h) / step, coarse.shape[0] - 1)
    cols = np.minimum(np.arange(w) / step, coarse.shape[1] - 1)
    r0 = np.floor(rows).astype(int)
    c0 = np.floor(cols).astype(int)
    r1 = np.minimum(r0 + 1, coarse.shape[0] - 1)
    c1 = np.minimum(c0 + 1, coarse.shape[1] - 1)
    fr = (rows - r0)[:, None]
    fc = (cols - c0)[None, :]
    top = coarse[np.ix_(r0, c0)] * (1 - fc) + coarse[np.ix_(r0, c1)] * fc
    bottom = coarse[np.ix_(r1, c0)] * (1 - fc) + coarse[np.ix_(r1, c1)] * fc
    return (top * (1 - fr) + bottom * fr).astype(np.float32)


#: Slopes, in degrees, between which the ground goes from its flat surfaces
#: to its rocky ones.
ROCK_SLOPE = (20.0, 40.0)


def _layered_ground(level, links, tree):
    """
    The ground's colour from its surface layers and their masks, by a rule
    of this exporter's own: the engine mixes them in a compiled shader graph
    of masks, slope, height and noise, which is not read.

    - Layers named for distance are the far view's stand-ins and are left
      out.
    - The textured layers that cover nine tenths of the terrain or more are
      the base: their masks are full nearly everywhere, so where each lies is
      decided by the shader, not by them. Those named for rock or cliff
      colour slopes steeper than 40 degrees, those named for gravel flat
      ground (the other base layers when none is), blended between 20 and 40
      degrees by the heightfield's slope.
    - Every other textured layer is laid over the base by its own mask, in
      layer order.

    A layer's colour is its `_cv` map's mean; the tiling scale is not found.
    Returns (sampler, flat colour, description) or None.
    """
    from .frostbiteterrain import read_masks, sample_heights

    layers = terrain_layers(level, links)
    masks = read_masks(tree, level.chunk, lambda guid: guid in level.chunks) if layers else None
    if masks is None:
        return None
    textured = {
        l.index: l
        for l in layers
        if l.colour is not None and l.index in masks.tiles and "distance" not in (l.colour_map or "").lower()
    }
    if not textured:
        return None
    x0, z0, x1, z1 = tree.square
    coarse = 16.0
    side = int(round((x1 - x0) / coarse))
    cover = {i: float(np.nanmean(np.nan_to_num(masks.raster(i, (x0, z0), coarse, (side, side)), nan=0.0))) for i in textured}
    base = [textured[i] for i in textured if cover[i] >= 0.9]
    painted = [textured[i] for i in sorted(textured) if cover[i] < 0.9]
    if not base:
        return None
    rocky = [l for l in base if any(w in (l.colour_map or "").lower() for w in ("rock", "cliff"))]
    others = [l for l in base if l not in rocky]
    flat_layers = [l for l in others if "gravel" in (l.colour_map or "").lower()] or others or base
    flat = np.median([l.colour for l in flat_layers], axis=0).astype(np.float32)
    steep = np.median([l.colour for l in rocky], axis=0).astype(np.float32) if rocky else flat

    def sample(gx, gz):
        h, w = gx.shape
        metres = float(gx[0, 1] - gx[0, 0]) if w > 1 else 1.0
        origin = (float(gx[0, 0]) - metres / 2, float(gz[0, 0]) - metres / 2)
        # Slope from the heightfield, every eighth texel.
        step = 8
        sx, sz = gx[::step, ::step], gz[::step, ::step]
        heights = sample_heights(tree, level.chunk, sx.ravel(), sz.ravel()).reshape(sx.shape)
        dz, dx = np.gradient(heights, metres * step)
        slope = np.degrees(np.arctan(np.hypot(dx, dz)))
        # Spread back over every texel bilinearly: repeated in blocks, the
        # 20 to 40 degree ramp drew the rocky colour as hard-edged patches.
        slope = _upsample(slope, step, h, w)
        t = np.clip((slope - ROCK_SLOPE[0]) / (ROCK_SLOPE[1] - ROCK_SLOPE[0]), 0.0, 1.0)[..., None]
        out = flat * (1 - t) + steep * t
        for layer in painted:
            m = np.nan_to_num(masks.raster(layer.index, origin, metres, (h, w)), nan=0.0)[..., None]
            out = out * (1 - m) + np.array(layer.colour, np.float32) * m
        return out.astype(np.float32)

    description = (
        f"in its surface layers: {len(base)} covering the terrain as the base"
        + (f" ({len(rocky)} rocky on steep ground)" if rocky else "")
        + f", {len(painted)} laid over it by their masks"
    )
    return sample, tuple(float(v) for v in flat), description


def _surface_colour(level, links) -> tuple[float, float, float] | None:
    """
    The middle colour of the terrain's surface materials: the colour maps
    (`..._cv`) its layer graph's shader blocks name, each averaged, then the
    median of each channel. For a level without a terrain backdrop. One such
    level names 27 surfaces - sand, gravels, soils, grass, cracked concrete -
    The engine's default surface is left out.
    """
    from .frostbitematerial import SHADER_BLOCK_DEPOT

    names = set()
    for entry in level.res.values():
        if entry.res_type != SHADER_BLOCK_DEPOT or "layergraph" not in entry.name:
            continue
        data = level.read(entry.location)
        names.update(
            links.by_guid[data[p : p + 16]] for p in range(len(data) - 15) if data[p : p + 16] in links.by_guid
        )
    colours = []
    for name in sorted(names):
        tail = name.rsplit("/", 1)[-1]
        if not tail.endswith("_cv") or "default" in tail or name not in links.headers:
            continue
        try:
            colours.append(_image(level, links, name, 64).reshape(-1, 3).mean(axis=0) / 255.0)
        except UnsupportedFrostbite:
            continue
    if not colours:
        return None
    return tuple(float(v) for v in np.median(colours, axis=0))


def _map_sampler(fit, full):
    """World (x, z) grids -> colours 0..1, bilinear from a colour map by a UV fit."""
    fh, fw = full.shape[:2]
    image = full.astype(np.float32) / 255.0

    def sample(gx, gz):
        uv = np.stack([gx, gz, np.ones_like(gx)], -1) @ fit
        pu, pv = uv[..., 0] * fw - 0.5, uv[..., 1] * fh - 0.5
        c0, r0 = np.floor(pu).astype(int), np.floor(pv).astype(int)
        fu, fv = (pu - c0)[..., None], (pv - r0)[..., None]

        def at(r, c):
            return image[r.clip(0, fh - 1), c.clip(0, fw - 1)]

        return (
            at(r0, c0) * (1 - fu) * (1 - fv) + at(r0, c0 + 1) * fu * (1 - fv)
            + at(r0 + 1, c0) * (1 - fu) * fv + at(r0 + 1, c0 + 1) * fu * fv
        )

    return sample


def _backdrop_colour(level, links, backdrop_uv, ground, square):
    """
    What colours the heightfield: ("map", texture, fit, image) when a terrain
    backdrop's colour map covers it, else ("flat", rgb) — the average colour of
    the backdrop within a kilometre round the terrain square — or None.

    Each backdrop texture is fitted on its own: its texture coordinates are a
    linear function of world x and z (99% of vertices within 0.001, half-float
    rounding; seam vertices refitted away). One level maps a single 65 km
    texture over everything and so over the heightfield too; another gives
    each of eight tiles round the play area its own texture, and none of them
    reaches the heightfield.
    """
    if links is None or not backdrop_uv:
        return None
    groups: dict[str, list] = {}
    for world, uv, name in backdrop_uv:
        groups.setdefault(name, []).append((world, uv))
    g = ground.positions[:, [0, 2]].astype(np.float64)
    gd = np.column_stack([g, np.ones(len(g))])
    x0, z0, x1, z1 = square
    samples = []
    for name, items in sorted(groups.items()):
        xz = np.concatenate([w[:, [0, 2]] for w, _ in items]).astype(np.float64)
        uv = np.concatenate([u for _, u in items]).astype(np.float64)
        design = np.column_stack([xz, np.ones(len(xz))])
        fit, *_ = np.linalg.lstsq(design, uv, rcond=None)
        good = np.abs(design @ fit - uv).max(axis=1) < 0.01
        if good.mean() < 0.99:
            continue
        fit, *_ = np.linalg.lstsq(design[good], uv[good], rcond=None)
        if np.percentile(np.abs(design[good] @ fit - uv[good]), 99) >= 2e-3:
            continue
        try:
            full = _image(level, links, name, 1 << 14)
        except UnsupportedFrostbite:
            continue
        mapped = gd @ fit
        lo, hi = uv[good].min(axis=0) - 1e-3, uv[good].max(axis=0) + 1e-3
        if (mapped >= lo).all() and (mapped <= hi).all():
            return ("map", name, fit, np.ascontiguousarray(full))
        # Not covering: what it shows right round the square is the colour.
        near = (
            (xz[:, 0] > x0 - 1000) & (xz[:, 0] < x1 + 1000)
            & (xz[:, 1] > z0 - 1000) & (xz[:, 1] < z1 + 1000)
        )
        if near.any():
            h, w = full.shape[:2]
            frac = uv[near] % 1.0
            px = full[(frac[:, 1] * h).astype(int).clip(0, h - 1), (frac[:, 0] * w).astype(int).clip(0, w - 1)]
            samples.append(px.reshape(-1, 3).astype(np.float64) / 255.0)
    if samples:
        return ("flat", tuple(float(v) for v in np.concatenate(samples).mean(axis=0)))
    return None


def _fit(sets, placements, chosen, terrain, model) -> dict[str, np.ndarray]:
    """
    Which copies to keep: all of them, unless even the coarsest levels exceed
    the budget. Then the smallest copies go first — size being the mesh's
    bounding-box diagonal times the copy's scale — because a level has no lap to
    measure distance from, and a crate is missed less than a hangar. The
    terrain backdrop is never left out.
    """
    keep = {
        mesh: np.ones(sum(len(r) for r in placements.meshes[mesh]), dtype=bool) for mesh in sets
    }
    cost = {mesh: lods[chosen[mesh]].triangles for mesh, (_s, lods) in sets.items()}
    total = sum(cost[mesh] * len(k) for mesh, k in keep.items())
    if total <= model.budget:
        return keep

    sizes, owners, index = [], [], []
    for mesh, (meshset, _lods) in sets.items():
        if mesh in terrain:
            continue
        rows = np.concatenate(placements.meshes[mesh])
        scale = np.abs(np.linalg.det(rows[:, :3, :3].astype(np.float64))) ** (1 / 3)
        sizes.append(scale * float(np.linalg.norm(meshset.high - meshset.low)))
        owners += [mesh] * len(rows)
        index.append(np.arange(len(rows)))
    if not sizes:
        return keep
    order = np.argsort(np.concatenate(sizes), kind="stable")
    index = np.concatenate(index)
    for at in order:
        if total <= model.budget:
            break
        mesh = owners[at]
        keep[mesh][index[at]] = False
        total -= cost[mesh]
        model.dropped += 1
    return keep


#: The paint of a decal whose material names none: a runway's white lines.
DECAL_WHITE = (0.92, 0.92, 0.90)

#: The largest side of one baked ground tile, in pixels.
GROUND_TILE = 4096


def _decal_layers(level, links, decals, largest: int = 512):
    """What each decal batch draws with: its colour map and opacity, decoded."""
    from .frostbitedecals import MASK_PAINT, Layer

    cache: dict[str, np.ndarray | None] = {}

    def image(name):
        if name not in cache:
            try:
                cache[name] = _image(level, links, name, largest).astype(np.float32) / 255.0
            except UnsupportedFrostbite:
                cache[name] = None
        return cache[name]

    v = decals.vertices
    layers = []
    for batch in decals.batches:
        tri = v[batch.first : batch.first + 3 * batch.triangles]
        world = bool(len(tri)) and bool(np.all(tri["u"] == tri["x"]) and np.all(tri["v"] == tri["z"]))
        colour_name, opacity_name, mask_name, mult_name = (
            batch.texture("_cv"), batch.texture("_op"), batch.texture("_rgb"), batch.texture("_mult")
        )
        colour = image(colour_name) if colour_name else None
        opacity = image(opacity_name) if opacity_name else None
        mult = image(mult_name) if mult_name else None
        paint = batch.paint
        if colour is not None:
            layers.append(Layer(colour, None, None if opacity is None else opacity[:, :, 0], world, batch.tiling))
        elif mult is not None and opacity is not None:
            # A runway's worn white line: the line is the opacity map, its
            # wear the multiply map over the paint.
            layers.append(
                Layer(mult[:, :, :3] * np.asarray(paint or DECAL_WHITE, np.float32), None, opacity[:, :, 0], world, batch.tiling)
            )
        elif mask_name and image(mask_name) is not None:
            fallback, strength = next(
                (c, k) for pattern, c, k in MASK_PAINT if pattern.search(mask_name.rsplit("/", 1)[-1])
            )
            layers.append(
                Layer(None, paint or fallback, image(mask_name).max(axis=2) * strength, world, batch.tiling)
                if strength
                else None
            )
        elif opacity is not None and paint is not None:
            # A tyre track: paint in the material's colour, shaped by the opacity map.
            layers.append(Layer(None, paint, opacity[:, :, 0], world, batch.tiling))
        else:
            layers.append(None)
    return layers


def _bake_ground(level, links, model, ground, base_colour, metres: float, report, colormap=None) -> np.ndarray:
    """
    Bake tiles of ground colour under the terrain decals and cut the
    heightfield's triangles there into parts that carry them. Returns the mask
    of triangles left to the plain backdrop colour.
    """
    from .frostbitedecals import TERRAIN_DECALS, bake, read_decals

    keep = np.ones(len(ground.faces), dtype=bool)
    entries = [e for e in level.res.values() if e.res_type == TERRAIN_DECALS]
    if not entries:
        model.ground += "; no terrain decals to bake"
        return keep
    try:
        decals = read_decals(level.read(entries[0].location), links.by_guid, entries[0].name)
    except UnsupportedFrostbite as exc:
        model.ground += f"; the terrain decals could not be read ({exc})"
        return keep
    layers = _decal_layers(level, links, decals)

    v = decals.vertices
    margin = 32.0
    lo = np.floor((np.array([v["x"].min(), v["z"].min()]) - margin) / metres) * metres
    hi = np.ceil((np.array([v["x"].max(), v["z"].max()]) + margin) / metres) * metres
    if colormap is not None:
        # The colormap's own extent is baked too: it is the ground's look where
        # no decal lies.
        h, w = colormap.image.shape[:2]
        lo = np.minimum(lo, np.floor(np.array(colormap.origin) / metres) * metres)
        hi = np.maximum(hi, np.ceil((np.array(colormap.origin) + (w * colormap.metres, h * colormap.metres)) / metres) * metres)
    g_lo = ground.positions[:, [0, 2]].min(axis=0)
    g_hi = ground.positions[:, [0, 2]].max(axis=0)
    lo, hi = np.maximum(lo, g_lo), np.minimum(hi, g_hi)
    if (hi <= lo).any():
        return keep
    span = GROUND_TILE * metres
    tiles_x = int(np.ceil((hi[0] - lo[0]) / span))
    tiles_z = int(np.ceil((hi[1] - lo[1]) / span))

    centres = ground.positions[ground.faces].mean(axis=1)[:, [0, 2]]
    baked = 0
    for j in range(tiles_z):
        for i in range(tiles_x):
            x0 = lo[0] + i * span
            z0 = lo[1] + j * span
            w = int(round(min(span, hi[0] - x0) / metres))
            h = int(round(min(span, hi[1] - z0) / metres))
            if w < 2 or h < 2:
                continue
            inside = (
                keep
                & (centres[:, 0] >= x0) & (centres[:, 0] < x0 + w * metres)
                & (centres[:, 1] >= z0) & (centres[:, 1] < z0 + h * metres)
            )
            if not inside.any():
                continue
            xs = x0 + (np.arange(w) + 0.5) * metres
            zs = z0 + (np.arange(h) + 0.5) * metres
            gx, gz = np.meshgrid(xs, zs)
            base = base_colour(gx, gz)
            image = bake(decals, layers, base, (x0, z0), metres)
            name = f"{TERRAIN_PART} x{int(x0)} z{int(z0)}"
            texture = f"{name} (baked)"
            model.images[texture] = (np.clip(image, 0, 1) * 255).astype(np.uint8)

            faces = ground.faces[inside]
            used, local = np.unique(faces, return_inverse=True)
            points = ground.positions[used]
            uvs = np.stack(
                [(points[:, 0] - x0) / (w * metres), (points[:, 2] - z0) / (h * metres)], 1
            ).astype(np.float32)
            piece = Piece(texture=texture)
            piece.add(points, local.reshape(-1, 3), uvs)
            model.parts[name] = piece
            keep &= ~inside
            baked += 1
    drawn = sum(1 for layer in layers if layer is not None)
    model.ground += (
        f"; {baked} tile{'s' if baked != 1 else ''} baked at {metres:g} m a pixel "
        f"with {drawn:,} of {len(layers):,} decal batches"
    )
    return keep


#: Only for clamped output (`write_level(..., clamped=True)`): triangles whose
#: texture repeats more often than this across them are left as they are rather
#: than cut into that many pieces a side.
UNTILE_MOST = 16
#: Only for clamped output: a triangle its texture would cut into more pieces
#: than this is drawn in the texture's average colour, in a part of its own.
#: Bark repeats down every branch of a tree: cut, one tree's 1,099 triangles
#: became 51,735, and a level's trees 6.4 million became 24 million. Cut-out
#: maps (leaves) are never flattened.
UNTILE_PIECES = 4


def untile(
    points: np.ndarray, faces: np.ndarray, uvs: np.ndarray, most: int = UNTILE_MOST
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    The same surface with every triangle's texture coordinates inside 0..1.

    Frostbite repeats textures: a container's ribbed side runs from -1.6 to
    1.8, and a fifth of a level's textured triangles reach outside 0..1. A
    renderer that packs textures into an atlas and clamps them, rather than
    wrapping each in its own cell as the 3DHeat viewer does, draws such a
    texture smeared, stretched along one axis or reversed, differently for
    every texture. For that renderer - `write_level(..., clamped=True)` - each
    triangle is cut along the whole-number lines it crosses, and each piece
    moved by whole repeats into 0..1: the same pixels on the same surface.
    Triangles already inside keep their shared vertices.
    """
    eps = 1e-4
    tri_uv = uvs[faces].astype(np.float64)
    inside = ((tri_uv >= -eps) & (tri_uv <= 1 + eps)).all(axis=(1, 2))
    span = tri_uv.max(axis=1) - np.floor(tri_uv.min(axis=1) + eps)
    huge = (span > most + eps).any(axis=1)
    loose = ~inside & ~huge
    if not loose.any():
        return points, faces, uvs
    xyz = points[faces[loose]].astype(np.float64)
    tex = tri_uv[loose]
    for axis in (0, 1):
        done_xyz, done_tex = [], []
        while len(tex):
            lo = np.floor(tex[:, :, axis].min(axis=1) + eps)
            cut = lo + 1
            crossing = tex[:, :, axis].max(axis=1) > cut + eps
            done_xyz.append(xyz[~crossing])
            done_tex.append(tex[~crossing])
            xyz, tex = _split(xyz[crossing], tex[crossing], axis, cut[crossing])
        xyz, tex = np.concatenate(done_xyz), np.concatenate(done_tex)
    # Each piece now lies within one repeat: move it there.
    tex = tex - np.floor(tex.mean(axis=1, keepdims=True))
    tex = tex.clip(0.0, 1.0)
    # The pieces' corners, each once: pieces of one repeat share their edges.
    corners = np.concatenate([xyz.reshape(-1, 3), tex.reshape(-1, 2)], axis=1).astype(np.float32)
    corners, cut_faces = np.unique(corners, axis=0, return_inverse=True)
    keep_faces = faces[~loose]
    used, local = np.unique(keep_faces, return_inverse=True)
    n = len(used)
    out_points = np.concatenate([points[used], corners[:, :3]])
    out_uvs = np.concatenate([uvs[used], corners[:, 3:]])
    out_faces = np.concatenate([local.reshape(-1, 3), n + cut_faces.reshape(-1, 3)])
    return out_points, out_faces, out_uvs


def _pieces(faces: np.ndarray, uvs: np.ndarray) -> np.ndarray:
    """Per triangle, how many repeats of its texture it spans: the pieces
    `untile` would cut it into, at most."""
    tri = uvs[faces].astype(np.float64)
    span = np.ceil(tri.max(axis=1) - np.floor(tri.min(axis=1) + 1e-4) - 1e-4).clip(1, None)
    return span[:, 0] * span[:, 1]


def _split(xyz: np.ndarray, tex: np.ndarray, axis: int, cut: np.ndarray):
    """
    Triangles that cross the line `tex[axis] == cut`, each cut into the
    triangle on one side and the two that fill the other, winding kept.
    """
    if not len(xyz):
        return xyz, tex
    above = tex[:, :, axis] > cut[:, None]
    # The corner alone on its side, then the other two in their order.
    alone = np.where(above.sum(axis=1) == 1, above.argmax(axis=1), (~above).argmax(axis=1))
    order = (alone[:, None] + np.arange(3)) % 3
    rows = np.arange(len(xyz))[:, None]
    p, t = xyz[rows, order], tex[rows, order]

    def meet(i, j):
        f = (cut - t[:, i, axis]) / (t[:, j, axis] - t[:, i, axis])
        return p[:, i] + f[:, None] * (p[:, j] - p[:, i]), t[:, i] + f[:, None] * (t[:, j] - t[:, i])

    pab, tab = meet(0, 1)
    pac, tac = meet(0, 2)
    out_p = np.concatenate([
        np.stack([p[:, 0], pab, pac], 1),
        np.stack([pab, p[:, 1], p[:, 2]], 1),
        np.stack([pab, p[:, 2], pac], 1),
    ])
    out_t = np.concatenate([
        np.stack([t[:, 0], tab, tac], 1),
        np.stack([tab, t[:, 1], t[:, 2]], 1),
        np.stack([tab, t[:, 2], tac], 1),
    ])
    return out_p, out_t


def write_level(model: LevelModel, out: str | Path, clamped: bool = False) -> Path:
    """
    The level as a binary glTF.

    Textures repeat as the game repeats them: UVs are written as they are,
    unclamped, with a REPEAT sampler, and a brick wall is one triangle pair
    whose UV runs 0 to 40. `clamped` is for a consumer that cannot repeat a
    texture - an atlas that clamps each image into its cell: every textured
    triangle is cut into pieces inside 0..1 (`untile`), and one its texture
    would cut into more than `UNTILE_PIECES` is drawn in the texture's average
    colour instead, in a part named '... (average colour)'.
    """
    from .frostbitematerial import ALPHA_CUTOFF
    from .glb import Part, write_glb

    positions = []
    uvs = []
    parts = []
    base = 0
    textured = any(p.texture for p in model.parts.values())
    for name in sorted(model.parts, key=lambda n: (not n.startswith("ground"), n)):
        piece = model.parts[name]
        block = np.concatenate(piece.points)
        faces = np.concatenate(piece.faces)
        image = model.images.get(piece.texture) if piece.texture else None
        if piece.texture:
            coords = np.concatenate(piece.uvs)
        if piece.texture and clamped:
            dense = _pieces(faces, coords) > UNTILE_PIECES
            if image is not None and image.shape[2] == 3 and dense.any():
                # Repeating too densely to cut: its average colour instead.
                average = tuple(float(v) for v in image.reshape(-1, 3).mean(axis=0) / 255.0)
                used, local = np.unique(faces[dense], return_inverse=True)
                positions.append(block[used])
                if textured:
                    uvs.append(np.zeros((len(used), 2), np.float32))
                parts.append(
                    Part(
                        name=f"{name} (average colour)",
                        faces=local.reshape(-1, 3) + base,
                        colour=average,
                        extras={"destructible": True} if DESTRUCTIBLE in name else None,
                    )
                )
                base += len(used)
                model.flattened += int(dense.sum())
                faces = faces[~dense]
            if not len(faces):
                continue
            block, faces, coords = untile(block, faces, coords)
        positions.append(block)
        if textured:
            uvs.append(coords if image is not None else np.zeros((len(block), 2), np.float32))
        kind = name.split(" ", 1)[0] if image is not None else name.replace(DESTRUCTIBLE, "")
        parts.append(
            Part(
                name=name,
                faces=faces + base,
                colour=None if image is not None else (
                    model.ground_colour
                    if name == TERRAIN_PART and model.ground_colour
                    else COLOURS.get(kind, COLOURS["structure:props"])
                ),
                texture=image,
                alpha_cutoff=ALPHA_CUTOFF if image is not None and image.shape[2] == 4 else None,
                extras={"destructible": True} if DESTRUCTIBLE in name else None,
            )
        )
        base += len(block)
    if not parts:
        raise UnsupportedFrostbite("nothing was placed: no static model group was recognised")
    return write_glb(
        out,
        np.concatenate(positions),
        parts=parts,
        uvs=np.concatenate(uvs) if textured else None,
        repeat=textured,
    )
