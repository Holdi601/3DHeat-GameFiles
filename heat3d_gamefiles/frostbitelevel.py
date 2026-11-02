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
from .frostbitebundle import LevelCatalogue, level_tables
from .frostbiteebx import Partition, partition_guid, read_partition
from .frostbitemesh import MESHSET, decode_sections, read_meshset

#: The static model group member, and the transform its instances are.
MEMBER = (bytes.fromhex("ad13064e92c8195914bc2c0dee33e139"), 0xF861A878)
TRANSFORM = (bytes.fromhex("101dce064e9a64fc2a9fa9d482576ffa"), 0x5E6D8C37)

MEMBER_SIZE = 224
MEMBER_TRANSFORMS = 88
MEMBER_MESH = 160
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
#: The level's distant terrain meshes, and meshes that blend into the terrain.
BACKDROP_PART = "ground:terrain backdrop"
BLEND_PART = "ground:terrain blend"
GROUND_PARTS = (BACKDROP_PART, BLEND_PART)

#: Meshes that are effects rather than surfaces — smoke plumes, scaled up
#: hundreds of times into a sheet over the whole level — by their asset path.
EFFECTS = re.compile(r"(^|/)fx/", re.I)

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
}


def find_level(root: str | Path, name: str) -> Path:
    """A level's table by its name, or by a path to the `.toc` itself."""
    if Path(name).suffix.lower() == ".toc" and Path(name).is_file():
        return Path(name)
    tables = level_tables(root)
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

    def copies(self) -> int:
        return sum(len(t) for blocks in self.meshes.values() for t in blocks)


def _members(partition: Partition, name: str) -> list[tuple[int, np.ndarray]]:
    """(import index of the mesh, transforms) for each member of each group."""
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
            out.append((index, rows.copy()))
    return out


def find_placements(
    level: LevelCatalogue, prefix: str, skip: tuple[str, ...] = (), report=print
) -> Placements:
    """
    Every grouped mesh copy the level's partitions place.

    `skip` leaves out partitions whose name contains any of the given strings —
    a game mode's layer, say, when only the common layout is wanted.
    """
    placements = Placements()
    meshes = {e.name for e in level.res.values() if e.res_type == MESHSET}
    guid_names: dict[bytes, str] = {}
    pending: list[tuple[str, bytes, np.ndarray]] = []

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
        for index, rows in found:
            pending.append((name, partition.imports[index][0], rows))

    wanted = {guid for _, guid, _ in pending}
    for mesh in sorted(meshes):
        if mesh in level.ebx and len(guid_names) < len(wanted):
            guid = partition_guid(level.read(level.ebx[mesh].location))
            if guid in wanted:
                guid_names[guid] = mesh

    for name, guid, rows in pending:
        mesh = guid_names.get(guid)
        if mesh is None:
            placements.unresolved += 1
            continue
        placements.meshes.setdefault(mesh, []).append(rows)
        short = name[len(prefix) :]
        placements.partitions[short] = placements.partitions.get(short, 0) + len(rows)
    return placements


def category(mesh: str, materials: list[str]) -> str:
    if any("terrainbackdrop" in m.lower() for m in materials):
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

    def triangles(self) -> int:
        return sum(len(f) for piece in self.parts.values() for f in piece.faces)


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
    report=print,
) -> LevelModel:
    """
    Read a level and place its meshes, at levels of detail that fit `budget`.

    `textures` is the largest texture side to write, in pixels; 0 writes flat
    colours. The terrain heightfield is drawn no finer than `ground_spacing`
    metres; 0 leaves it out.
    """
    from .forzaplacement import DEFAULT_BUDGET, auto_budget, choose_levels

    toc = find_level(root, name)
    level = LevelCatalogue(toc)
    prefix = ebx_prefix(toc)
    report(f"{toc.stem}: {level.bundle_count} bundles, {len(level.ebx):,} partitions, {len(level.res):,} resources")
    placements = find_placements(level, prefix, skip, report)
    model = LevelModel(placements=placements)
    links = None
    if textures:
        from .frostbitematerial import link_materials

        links = link_materials(level)

    sets = {}
    costs = {}
    for mesh in placements.meshes:
        if EFFECTS.search(mesh):
            model.skipped[mesh] = "an effect, not a surface"
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
        for section in sections:
            drawn += 1
            texture = None
            if links is not None and section.uvs is not None:
                key = lod.sections[section.index].key
                texture = links.colour_map(mesh, section.material, key)
            if texture is not None and texture not in model.images:
                try:
                    model.images[texture] = _image(level, links, texture, textures)
                except UnsupportedFrostbite:
                    model.images[texture] = None
            if texture is not None and model.images[texture] is None:
                texture = None
            textured += texture is not None
            world = place(section.positions, rows)
            copies = len(rows)
            tri = section.faces[None, :, :] + (np.arange(copies) * len(section.positions))[:, None, None]
            # A mirrored copy turns its triangles inside out; winding them the
            # other way round keeps the computed normals pointing outwards.
            tri[mirrored] = tri[mirrored][:, :, ::-1]
            part = kind if texture is None else f"{kind} {_short(texture)}"
            piece = model.parts.setdefault(part, Piece(texture=texture))
            uvs = np.tile(section.uvs, (copies, 1)) if texture is not None else None
            piece.add(world, tri.reshape(-1, 3), uvs)
            if kind == BACKDROP_PART and texture is not None:
                backdrop_uv.append((world, uvs, texture))
    model.textured = (textured, drawn)

    if ground_spacing:
        _add_ground(level, model, ground_spacing, backdrop_uv, links)
    return model


def _image(level, links, texture: str, largest: int) -> np.ndarray:
    from .frostbitematerial import decode_texture

    info = links.headers[texture]
    if info.chunk not in level.chunks:
        raise UnsupportedFrostbite(f"{texture}: its chunk is not in this level")
    return decode_texture(info, level.chunk(info.chunk), largest)


def _add_ground(level, model: LevelModel, spacing: float, backdrop_uv, links=None) -> None:
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
    from .frostbiteterrain import STREAMING_TREE, build_ground, read_tree

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
    texture = uvs = None
    names = {t for _, _, t in backdrop_uv}
    if len(names) == 1:
        texture = names.pop()
        xz = np.concatenate([w[:, [0, 2]] for w, _, _ in backdrop_uv]).astype(np.float64)
        uv = np.concatenate([u for _, u, _ in backdrop_uv]).astype(np.float64)
        design = np.column_stack([xz, np.ones(len(xz))])
        fit, *_ = np.linalg.lstsq(design, uv, rcond=None)
        # Vertices on a texture seam carry 0 where the fit says 1; they are a
        # handful, so the fit is refitted without them and judged by the rest.
        good = np.abs(design @ fit - uv).max(axis=1) < 0.01
        fit, *_ = np.linalg.lstsq(design[good], uv[good], rcond=None)
        residual = np.abs(design[good] @ fit - uv[good])
        if good.mean() > 0.99 and np.percentile(residual, 99) < 2e-3:
            g = ground.positions[:, [0, 2]].astype(np.float64)
            uvs = (np.column_stack([g, np.ones(len(g))]) @ fit).astype(np.float32)
        else:
            texture = None
    if texture is not None and uvs is not None and links is not None:
        # The heightfield is a small part of the map, so it gets its own crop
        # of the largest mip there is rather than the capped copy the backdrop
        # uses.
        try:
            full = _image(level, links, texture, 1 << 14)
        except UnsupportedFrostbite:
            full = None
        if full is not None:
            h, w = full.shape[:2]
            lo = np.floor(uvs.min(axis=0) * (w, h)).astype(int).clip(0, (w - 1, h - 1))
            hi = np.ceil(uvs.max(axis=0) * (w, h)).astype(int).clip(lo + 1, (w, h))
            crop = np.ascontiguousarray(full[lo[1] : hi[1], lo[0] : hi[0]])
            uvs = ((uvs * (w, h) - lo) / (hi - lo)).astype(np.float32)
            texture = texture + " (heightfield)"
            model.images[texture] = crop
    piece = Piece(texture=texture)
    piece.add(ground.positions, ground.faces, uvs)
    model.parts[TERRAIN_PART] = piece
    x0, _z0, x1, _z1 = tree.square
    model.ground = (
        f"the heightfield, {x1 - x0:,.0f} m square, drawn at {spacing:g} m or coarser"
        + (", coloured from the terrain backdrop's colour map" if texture else "")
    )


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


def write_level(model: LevelModel, out: str | Path) -> Path:
    from .glb import Part, write_glb

    positions = []
    uvs = []
    parts = []
    base = 0
    textured = any(p.texture for p in model.parts.values())
    for name in sorted(model.parts, key=lambda n: (not n.startswith("ground"), n)):
        piece = model.parts[name]
        block = np.concatenate(piece.points)
        positions.append(block)
        if textured:
            uvs.append(
                np.concatenate(piece.uvs) if piece.texture else np.zeros((len(block), 2), np.float32)
            )
        image = model.images.get(piece.texture) if piece.texture else None
        kind = name.split(" ", 1)[0] if image is not None else name
        parts.append(
            Part(
                name=name,
                faces=np.concatenate(piece.faces) + base,
                colour=None if image is not None else COLOURS.get(kind, COLOURS["structure:props"]),
                texture=image,
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
