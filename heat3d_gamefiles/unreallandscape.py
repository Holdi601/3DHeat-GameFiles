"""
Cooked Unreal 5 landscapes: the heightfield of a map's `Landscape`, read from
its components' heightmap textures.

A landscape is a grid of components. Each knows where it sits in the
landscape's own grid of quads (`SectionBaseX`, `SectionBaseY`), how many quads
it spans (`ComponentSizeQuads`, split into `NumSubsections` subsections of
`SubsectionSizeQuads`), and which texture holds its heights, with a scale and
bias (`HeightmapScaleBias`) saying where in that texture it starts. A height is
16 bits, red the high byte and green the low (blue and alpha hold the normal);
32768 is zero and a step is 1/128 of a landscape unit. The landscape actor's
transform turns the grid into the world: a quad is `scale.x` by `scale.y`
centimetres, a height unit `scale.z / 128` centimetres.

Subsections each carry their own edge: a component of two 63-quad subsections
is 2 x 64 texels wide, and texels 63 and 64 are the same vertex. Neighbouring
components share their edge vertices too. Both repeats are where the decode is
checked: every vertex stored twice must agree, and `Landscape.mismatches`
counts the ones that do not.

The properties are read without a schema of the build's slot numbers, which
move between engine versions and games. The first five slots are the five
integers above in every version (absent means zero, as an unversioned block
leaves out defaults). The heightmap is the one object reference in the block
that names a texture called `Heightmap...`; its scale and bias are the four
doubles whose first two are one over that texture's size and whose last two
fall on whole texels. The weightmap's scale and bias, the only other four
doubles of that shape, sit half a texel off and so never match.

Not read: landscapes whose heightmaps live in other packages (each component
in its own cell), edit layers, holes (the visibility layer), and Nanite
landscape meshes; the heightmap they are built from is read instead.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

import numpy as np

from .iostore import BULK_DATA, Store
from .unrealtexture import TextureError, _platform, bulk_map
from .unversioned import PropertyError, read_header, read_properties
from .zen import Export, Package, Packages

LANDSCAPE = "/Script/Landscape.Landscape"
PROXIES = ("/Script/Landscape.LandscapeStreamingProxy", "/Script/Landscape.LandscapeProxy")
COMPONENT = "/Script/Landscape.LandscapeComponent"
_SCENE = "/Script/Engine.SceneComponent"


class LandscapeError(Exception):
    """A landscape this cannot read, and why."""


@dataclass
class Component:
    name: str
    section: tuple[int, int]
    size_quads: int
    subsection_quads: int
    subsections: int
    heightmap: Export
    #: Where the component starts in its heightmap, in texels.
    texel: tuple[int, int]
    texture_size: tuple[int, int]


@dataclass
class Landscape:
    #: The landscape actor's location (cm), scale, and yaw/pitch/roll.
    location: tuple[float, float, float]
    scale: tuple[float, float, float]
    rotation: tuple[float, float, float]
    #: The grid's first vertex, in quads of the landscape's own grid.
    origin: tuple[int, int]
    #: Height per vertex in landscape units (stored value minus 32768, over
    #: 128), rows along Y; NaN where no component lies.
    heights: np.ndarray
    components: int = 0
    #: Vertices stored twice - on a subsection or component edge - that disagree.
    mismatches: int = 0
    shared: int = 0
    unread: dict[str, int] = field(default_factory=dict)

    def world(self, step: int = 1) -> tuple[np.ndarray, np.ndarray]:
        """
        Every `step`th vertex in Unreal world coordinates (cm, Z up), as an
        (ny, nx, 3) grid, and a mask of where there is ground.
        """
        h = self.heights[::step, ::step]
        ny, nx = h.shape
        gx = self.origin[0] + np.arange(nx) * step
        gy = self.origin[1] + np.arange(ny) * step
        local = np.empty((ny, nx, 3), dtype=np.float64)
        local[..., 0] = gx[None, :] * self.scale[0]
        local[..., 1] = gy[:, None] * self.scale[1]
        local[..., 2] = np.nan_to_num(h) * self.scale[2]
        if any(self.rotation):
            from .acrally import rotator_matrix

            local = local @ rotator_matrix(*self.rotation)
        local += np.asarray(self.location)
        return local, np.isfinite(h)


def _ints(data: bytes) -> tuple[list[int], int]:
    """Slots 0-4 as integers (absent or zero is 0), and where the values start."""
    present, at = read_header(data, 0)
    values = [0] * 5
    for slot, is_zero in present:
        if slot > 4:
            break
        if not is_zero:
            (values[slot],) = struct.unpack_from("<i", data, at)
            at += 4
    return values, at


def _heightmap_reference(package: Package, data: bytes, at: int) -> Export | None:
    found = []
    for offset in range(at, len(data) - 3):
        (value,) = struct.unpack_from("<i", data, offset)
        if 0 < value <= len(package.exports):
            export = package.exports[value - 1]
            if export.name.lower().startswith("heightmap") and package.class_name(export).endswith(".Texture2D"):
                found.append(export)
    return found[0] if len({e.index for e in found}) == 1 else None


def _scale_bias(data: bytes, at: int, width: int, height: int) -> tuple[int, int] | None:
    want = (1.0 / width, 1.0 / height)
    for offset in range(at, len(data) - 31):
        sx, sy, bx, by = struct.unpack_from("<4d", data, offset)
        if (sx, sy) != want or not (0.0 <= bx < 1.0 and 0.0 <= by < 1.0):
            continue
        tx, ty = bx * width, by * height
        if abs(tx - round(tx)) < 1e-6 and abs(ty - round(ty)) < 1e-6:
            return int(round(tx)), int(round(ty))
    return None


def read_component(package: Package, export: Export, sizes: dict[int, tuple[int, int]]) -> Component:
    data = package.export_data(export)
    (sx, sy, size, sub, count), at = _ints(data)
    if size <= 0 or sub <= 0 or count <= 0 or sub * count != size:
        raise LandscapeError(f"{export.name}: sizes {size} = {count} x {sub} do not add up")
    texture = _heightmap_reference(package, data, at)
    if texture is None:
        raise LandscapeError(f"{export.name}: no single heightmap texture in its properties")
    if texture.index not in sizes:
        found = _platform(package.export_data(texture), package.names)
        if found is None or found[0] != "PF_B8G8R8A8":
            raise LandscapeError(f"{texture.name}: not an 8-bit BGRA heightmap")
        sizes[texture.index] = (found[1][0].width, found[1][0].height)
    width, height = sizes[texture.index]
    texel = _scale_bias(data, at, width, height)
    if texel is None:
        raise LandscapeError(f"{export.name}: no heightmap scale and bias for a {width} x {height} texture")
    span = count * (sub + 1)
    if texel[0] + span > width or texel[1] + span > height:
        raise LandscapeError(f"{export.name}: runs off its heightmap")
    return Component(export.name, (sx, sy), size, sub, count, texture, texel, (width, height))


def bulk_range(store: Store, path: str, offset: int, size: int) -> bytes | None:
    """Part of a package's `.ubulk`, without reading the rest of it."""
    found = store.chunk_of(path)
    if found is None:
        return None
    _container, chunk_id = found
    for container in store.containers:
        entry = container.chunk(chunk_id, BULK_DATA)
        if entry is not None:
            start, length = container.spans[entry]
            if offset + size > length:
                return None
            return container.read_range(start + offset, size)
    return None


def texture_pixels(packages: Packages, package: Package, export: Export) -> np.ndarray:
    """The largest level of one texture export as (height, width, 4) bytes in its stored order."""
    data = package.export_data(export)
    found = _platform(data, package.names)
    if found is None:
        raise TextureError(f"{export.name}: no cooked pixels in a known format")
    name, mips = found
    if name not in ("PF_B8G8R8A8", "PF_R8G8B8A8"):
        raise TextureError(f"{export.name}: {name} is not an 8-bit four-channel format")
    mip = mips[0]
    entries = bulk_map(package)
    if not 0 <= mip.index < len(entries):
        raise TextureError(f"{export.name}: its first level has no bulk entry")
    offset, length, flags = entries[mip.index]
    want = mip.width * mip.height * 4
    if length < want:
        raise TextureError(f"{export.name}: level {mip.width}x{mip.height} is cut short")
    if flags & 0x40:
        payload = data[offset : offset + want]
    else:
        payload = bulk_range(packages.store, package.path, offset, want)
        if payload is None:
            raise TextureError(f"{export.name}: its bulk data is not in any container")
    return np.frombuffer(payload, dtype=np.uint8).reshape(mip.height, mip.width, 4)


def _actor_root(package: Package, actor: Export) -> dict | None:
    for export in package.exports:
        if package.outer_export(export) is actor and package.class_name(export) == _SCENE:
            try:
                values, _end = read_properties(package.export_data(export), _SCENE, package.names)
            except (PropertyError, struct.error, IndexError):
                return None
            if not values.get("AttachParent"):
                return values
    return None


def read_landscape(packages: Packages, package: Package) -> Landscape:
    """The landscape a map package holds, its heights assembled into one grid."""
    actor = next((e for e in package.exports if package.class_name(e) == LANDSCAPE), None)
    if actor is None:
        raise LandscapeError(f"{package.path}: no Landscape actor")
    root = _actor_root(package, actor)
    if root is None:
        raise LandscapeError(f"{package.path}: the Landscape actor's transform does not read")
    location = tuple(root.get("RelativeLocation") or (0.0, 0.0, 0.0))
    rotation = tuple(root.get("RelativeRotation") or (0.0, 0.0, 0.0))
    scale = tuple(root.get("RelativeScale3D") or (1.0, 1.0, 1.0))

    unread: dict[str, int] = {}
    sizes: dict[int, tuple[int, int]] = {}
    components: list[Component] = []
    for export in package.exports:
        if package.class_name(export) != COMPONENT:
            continue
        try:
            components.append(read_component(package, export, sizes))
        except (LandscapeError, TextureError, struct.error, IndexError) as exc:
            reason = str(exc).split(": ", 1)[-1]
            unread[reason] = unread.get(reason, 0) + 1
    if not components:
        raise LandscapeError(f"{package.path}: no landscape component reads ({unread})")

    x0 = min(c.section[0] for c in components)
    y0 = min(c.section[1] for c in components)
    x1 = max(c.section[0] + c.size_quads for c in components)
    y1 = max(c.section[1] + c.size_quads for c in components)
    heights = np.full((y1 - y0 + 1, x1 - x0 + 1), np.nan, dtype=np.float32)
    out = Landscape(location, scale, rotation, (x0, y0), heights, len(components), unread=unread)

    pixels: dict[int, np.ndarray] = {}
    for c in components:
        if c.heightmap.index not in pixels:
            try:
                raw = texture_pixels(packages, package, c.heightmap)
            except TextureError as exc:
                unread[str(exc)] = unread.get(str(exc), 0) + 1
                continue
            # Stored B, G, R, A: red is the high byte, green the low.
            value = raw[..., 2].astype(np.int32) * 256 + raw[..., 1]
            pixels[c.heightmap.index] = ((value - 32768) / 128.0).astype(np.float32)
        image = pixels[c.heightmap.index]
        # Each vertex of the component: which subsection, and its texel.
        v = np.arange(c.size_quads + 1)
        part = np.minimum(v // c.subsection_quads, c.subsections - 1)
        texel = part * (c.subsection_quads + 1) + (v - part * c.subsection_quads)
        block = image[np.ix_(c.texel[1] + texel, c.texel[0] + texel)]
        # The repeated subsection edge, read from both sides.
        for k in range(1, c.subsections):
            left = image[c.texel[1] :, c.texel[0] + k * (c.subsection_quads + 1) - 1][: c.subsections * (c.subsection_quads + 1)]
            right = image[c.texel[1] :, c.texel[0] + k * (c.subsection_quads + 1)][: c.subsections * (c.subsection_quads + 1)]
            out.shared += len(left)
            out.mismatches += int(np.count_nonzero(left != right))
        gx, gy = c.section[0] - x0, c.section[1] - y0
        target = heights[gy : gy + c.size_quads + 1, gx : gx + c.size_quads + 1]
        both = np.isfinite(target)
        out.shared += int(both.sum())
        out.mismatches += int(np.count_nonzero(target[both] != block[both]))
        target[...] = block
    return out
