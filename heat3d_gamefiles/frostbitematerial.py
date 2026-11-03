"""
Which texture a Frostbite mesh section shows, and the texture itself.

Textures
--------
A Texture res is a 180-byte header; the pixels are in a chunk::

    +8   type (0 a 2D texture), pixel format
    +22  width, height, depth, slices (u16)
    +30  mip count, first mip (u8)
    +40  the chunk's GUID
    +56  fifteen mip sizes (u32)
    +116 the size of the whole chain
    +164 the GUID of the chunk with the largest mips, when the main chunk
         lacks them

The chunk is the mip chain, largest first — for some textures without its
largest levels, which ship in another package; the chunk's length says where it
starts, since it is always the sum of the sizes from some mip down. The pixel
formats were identified by decoding them and looking: 67 and 66 are BC7 (sRGB
and linear, 1 byte a pixel), 61 and 60 BC3, 57, 56 and 55 BC1. A BC7 colour map
of a plastic tank decodes to the tank's texture sheet; read as BC3 the same
bytes are noise.

Materials
---------
The mesh asset says nothing about textures. The link is in the level's shader
block depots (res type 0x73312045, one per sub-world), which the mesh section
keys by the eight bytes at +0x130 of its record::

    +16      table: (section key u64, descriptor offset u64), until an offset
             falls outside the res
    descriptor  (block offset u64, hash u64, block size u64)
    block    the section's shader parameters; a texture parameter is a
             49-byte record — a byte, sixteen bytes, then the texture asset's
             partition GUID and instance GUID

Evidence: the crate's section key appears once in each of the ten depots of
the sub-worlds that place it; its block names `t_mil_crate_03_cs` and
`t_mil_crate_03_nmt` among the shared detail maps. Across a level, 2,641 of
2,724 drawn sections of the placed meshes find a block with a colour texture.

A block lists every texture the shader samples — the colour map, normal maps,
shared detail and destruction maps — and which parameter is the colour map is
not named. It is chosen: among the block's sRGB 2D textures, the one whose name
contains most words of the material's name (`M_ConcreteWall_01`: concrete,
wall), then most of the mesh's, then one that is not a detail, decal or damage
map, then the one fewest blocks use. A section whose only
candidates are shared detail maps is left flat-coloured.
"""

from __future__ import annotations

import re
import struct
from collections import Counter
from dataclasses import dataclass, field

import numpy as np

from .frostbite import UnsupportedFrostbite

TEXTURE = 0x6BDE20BA
SHADER_BLOCK_DEPOT = 0x73312045

#: Pixel formats, as Pillow's BCn decoder numbers them.
BC_FORMATS = {67: 7, 66: 7, 61: 3, 60: 3, 57: 1, 56: 1, 55: 1}
#: The sRGB ones: colour maps.
COLOUR_FORMATS = {67, 61, 57}
_BLOCK_BYTES = {7: 16, 3: 16, 1: 8}

_GENERIC = {"t", "vst", "mesh", "cs", "c", "ca", "cu", "d", "a", "b", "m", "com", "mil", "ind"}
#: Names of maps that are not a surface's own colour. `t_de_` is a decal sheet:
#: a road sign's block names its plain panel `t_com_highwaysignage_01_cs` and
#: `t_de_com_highwaysignage_01_ca`, a sheet with a shield laid on its side,
#: which drawn as the panel's colour shows the shield turned a quarter.
_AVOID = re.compile(
    r"^(t_)?de_|dest|detail|decal|overlay|dirt|noise|grunge|lookup|fracture|damage|burn|blood|snow|puddle|wet|test",
    re.I,
)
#: Maps that are never a surface's colour, whatever their name shares with
#: the material: signed distance fields (`_sdf`, shapes for cut-outs, drawn as
#: colour black and white stars), palettes a shader looks colours up in
#: (drawn as colour, a confetti of swatches) and channel masks (`_rgb`: glass
#: debris drawn through one came out cyan). `_rgba` maps are not among them:
#: most are colour with an alpha (a power line's sheet, stairs, a fence), and
#: taking them out replaced those with unrelated maps.
_NEVER = re.compile(r"_sdf$|palette|_rgb$", re.I)


#: A shader block's parameters follow its texture entries, each a type tag,
#: two flag bytes (01 80 for one value), a two-byte hash of the parameter's
#: name, a u32 count, the value and an eight-byte id. A float3 tag:
_FLOAT3 = re.compile(rb"\xf1\x1a\xf8\x25\x01\x80(..)\x01\x00\x00\x00(.{12})", re.S)
#: Float3 parameters that tint a surface's colour map, by name hash, with the
#: value that leaves it as it is. Found by what they hold: in one level they
#: carry a colour in 1 block in 6 whose colour map is grey and almost never
#: where the map has colour of its own (`4141`, `a37b`, `05dd`); the others
#: hold the colours a grey map is painted in where the material's name says
#: so (a bridge's `..._blue` trim, a window's dark frame). Their names are
#: hashed and not known.
TINTS = {b"\x41\x41": 1.0, b"\xa3\x7b": 1.0, b"\xbe\xad": 1.0, b"\x05\xdd": 1.0, b"\x6a\x68": 0.5, b"\x8a\x88": 0.5, b"\xec\x64": 0.5}


def block_tint(block: bytes) -> tuple[float, float, float] | None:
    """
    The product of a block's tints, each family's first value that is not
    neutral over the neutral one (a family can hold several, one per channel
    of a mask, most of them neutral); None when all are neutral. A value with
    a channel near nothing, such as pure green, selects a mask's channel and
    is passed over: taken as paint it turned brick facades green.
    """
    tint = np.ones(3)
    seen = set()
    for m in _FLOAT3.finditer(block):
        family = m.group(1)
        if family not in TINTS or family in seen:
            continue
        value = np.frombuffer(m.group(2), "<f4").astype(np.float64) / TINTS[family]
        if not np.isfinite(value).all() or (value < 0).any() or value.max() > 8 or np.allclose(value, 1.0, atol=0.01):
            continue
        if value.min() < 0.02 * value.max():
            continue  # a pure primary selects a channel of a mask; it is not a paint
        seen.add(family)
        tint *= value
    tint = np.clip(tint, 0.0, 2.0)
    return None if np.allclose(tint, 1.0, atol=0.01) else tuple(float(v) for v in tint)


@dataclass
class TextureInfo:
    name: str
    kind: int
    format: int
    width: int
    height: int
    mips: int
    chunk: bytes
    sizes: tuple[int, ...]
    #: The chunk holding the largest mips when `chunk` lacks them: they ship in
    #: a high-resolution pack, in a table of their own (+164 in the header).
    detail: bytes = b""


def read_texture_header(res: bytes, name: str = "texture") -> TextureInfo:
    if len(res) < 120:
        raise UnsupportedFrostbite(f"{name}: too short for a texture header")
    kind, fmt = struct.unpack_from("<II", res, 8)
    width, height = struct.unpack_from("<HH", res, 22)
    mips = res[30]
    sizes = struct.unpack_from("<15I", res, 56)[: max(1, min(mips, 15))]
    detail = res[164:180] if len(res) >= 180 and any(res[164:180]) else b""
    return TextureInfo(name, kind, fmt, width, height, mips, res[40:56], sizes, detail)


def decode_texture(info: TextureInfo, chunk: bytes, largest: int, alpha: bool = False) -> np.ndarray:
    """
    The largest mip the chunk holds that is no wider or taller than `largest`,
    as 8-bit RGB, or RGBA with `alpha`.
    """
    from PIL import Image

    n = BC_FORMATS.get(info.format)
    if n is None:
        raise UnsupportedFrostbite(f"{info.name}: pixel format {info.format} is not decoded")
    first = next(
        (k for k in range(len(info.sizes)) if sum(info.sizes[k:]) == len(chunk)), None
    )
    if first is None:
        raise UnsupportedFrostbite(f"{info.name}: the chunk is no tail of the mip chain")
    at = 0
    for level in range(first, len(info.sizes)):
        w, h = max(1, info.width >> level), max(1, info.height >> level)
        if (w <= largest and h <= largest) or level == len(info.sizes) - 1:
            expected = max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * _BLOCK_BYTES[n]
            if expected != info.sizes[level]:
                raise UnsupportedFrostbite(
                    f"{info.name}: mip {level} holds {info.sizes[level]} bytes, not {expected}"
                )
            image = Image.frombytes("RGBA", (w, h), chunk[at : at + expected], "bcn", n)
            return np.asarray(image.convert("RGBA" if alpha else "RGB"))
        at += info.sizes[level]
    raise UnsupportedFrostbite(f"{info.name}: no mip to decode")


#: Colour maps whose fourth channel is opacity: `_cu` (leaves, grass, cut-out
#: foliage) and `_ca` (colour and alpha). In `_cs`, by far the most common, it
#: is smoothness. Across one level's chosen colour maps, the median `_cu` has
#: 90% of its alpha within 0.1 of 0 or 1 and the median `_cs` 1%.
CUTOUT_NAME = re.compile(r"_c[ua](_\d+)?$", re.I)
#: Below this alpha a texel of a cut-out map is not drawn.
ALPHA_CUTOFF = 0.5


def is_cutout(name: str, rgba: np.ndarray) -> bool:
    """
    Whether a colour map's alpha cuts its surface out: named for it, and the
    alpha mostly near 0 or 1, some of it below the cutoff and some above - an
    opacity mask, not a gradient. One tree's leaf map carries no alpha at all
    (none above 4 in 255, at every size): its fronds are cut by their geometry
    and are drawn whole.
    """
    if not CUTOUT_NAME.search(name.rsplit("/", 1)[-1]) or rgba.ndim != 3 or rgba.shape[2] != 4:
        return False
    a = rgba[:, :, 3].astype(np.float32) / 255.0
    return bool(
        ((a < 0.1) | (a > 0.9)).mean() >= 0.75
        and (a < ALPHA_CUTOFF).mean() >= 0.01
        and (a >= ALPHA_CUTOFF).mean() >= 0.05
    )


def _words(name: str) -> set[str]:
    """The words of an asset or material name: split at underscores and at
    lower-to-upper case changes, lower-cased, without numbers and filler."""
    tail = name.rsplit("/", 1)[-1]
    tail = re.sub(r"([a-z])([A-Z])", r"\1_\2", tail)
    return {
        w for w in re.split(r"[_\W]+", tail.lower())
        if len(w) >= 3 and w not in _GENERIC and not w.isdigit()
    }


@dataclass
class MaterialLinks:
    """Section key -> the textures its shader block names, for one level."""

    blocks: dict[bytes, list[str]] = field(default_factory=dict)
    #: Texture asset partition GUID -> texture name, for whatever else names
    #: textures that way (terrain decals do).
    by_guid: dict[bytes, str] = field(default_factory=dict)
    usage: Counter = field(default_factory=Counter)
    headers: dict[str, TextureInfo] = field(default_factory=dict)
    #: Section key -> its block's tint (see `block_tint`), where not neutral.
    tints: dict[bytes, tuple[float, float, float]] = field(default_factory=dict)

    def variant_colour_map(self, mesh: str, material: str, key: bytes, default: bytes) -> str | None:
        """
        A section's colour map in an object variation keyed `key`, its own
        block keyed `default`. A variation swaps textures: where the map the
        section shows by default is not in the variation's block, the
        variation's map of the same kind (`_ca`, `_cs`, ...) that the default
        block does not name takes its place - the number a wall is painted
        with in place of the default lettering.
        """
        mine = self.colour_map(mesh, material, default)
        names = self.blocks.get(key, [])
        if mine is None or mine in names:
            return self.colour_map(mesh, material, key)
        kind = mine.rsplit("_", 1)[-1].lower()
        swapped = [
            n for n in names
            if n not in self.blocks.get(default, []) and n.rsplit("_", 1)[-1].lower() == kind and n in self.headers
        ]
        return swapped[0] if len(swapped) == 1 else self.colour_map(mesh, material, key)

    def overlay(self, key: bytes) -> str | None:
        """The `..._overlay_cs` a block names, if it names one and its mask (`..._overlay_a`)."""
        names = self.blocks.get(key, ())
        tails = {n.rsplit("/", 1)[-1].lower() for n in names}
        for n in names:
            tail = n.rsplit("/", 1)[-1].lower()
            if (
                tail.endswith("_overlay_cs")
                and tail[: -len("_cs")] + "_a" in tails
                and n in self.headers
                and self.headers[n].kind == 0
            ):
                return n
        return None

    def palette(self, key: bytes) -> str | None:
        """The palette a block names, if it names one."""
        for n in self.blocks.get(key, ()):
            if "palette" in n.rsplit("/", 1)[-1].lower() and n in self.headers and self.headers[n].kind == 0:
                return n
        return None

    def colour_map(self, mesh: str, material: str, key: bytes) -> str | None:
        names = self.blocks.get(key)
        if not names:
            return None
        candidates = [
            n for n in set(names)
            if n in self.headers
            and self.headers[n].kind == 0
            and self.headers[n].format in COLOUR_FORMATS
            and not _NEVER.search(n.rsplit("/", 1)[-1])
        ]
        if not candidates:
            return None
        material_words = _words(material)
        mesh_words = _words(mesh)

        def score(n):
            tail = n.rsplit("/", 1)[-1].lower()
            return (
                -sum(w in tail for w in material_words),
                -sum(w in tail for w in mesh_words),
                bool(_AVOID.search(tail)),
                self.usage[n],
                n,
            )

        best = min(candidates, key=score)
        tail = best.rsplit("/", 1)[-1].lower()
        if score(best)[:2] == (0, 0) and _AVOID.search(tail):
            return None
        return best


def link_materials(level) -> MaterialLinks:
    """Read every texture header and shader block depot of a level."""
    from .frostbiteebx import partition_guid

    links = MaterialLinks()
    by_guid = links.by_guid
    for entry in level.res.values():
        if entry.res_type != TEXTURE:
            continue
        try:
            links.headers[entry.name] = read_texture_header(level.read(entry.location), entry.name)
        except UnsupportedFrostbite:
            continue
        if entry.name in level.ebx:
            by_guid[partition_guid(level.read(level.ebx[entry.name].location))] = entry.name

    seen: dict[tuple[str, int], list[str]] = {}
    tints: dict[tuple[str, int], tuple[float, float, float] | None] = {}
    for entry in level.res.values():
        if entry.res_type != SHADER_BLOCK_DEPOT:
            continue
        data = level.read(entry.location)
        at = 16
        while at + 16 <= len(data):
            key = data[at : at + 8]
            (where,) = struct.unpack_from("<Q", data, at + 8)
            if not 0 < where <= len(data) - 24:
                break
            at += 16
            block_at, _hash, size = struct.unpack_from("<QQQ", data, where)
            if block_at + size > len(data):
                continue
            ident = (entry.name, block_at)
            if ident not in seen:
                block = data[block_at : block_at + size]
                names = [
                    by_guid[block[p : p + 16]]
                    for p in range(0, max(0, len(block) - 15))
                    if block[p : p + 16] in by_guid
                ]
                seen[ident] = names
                links.usage.update(set(names))
                tints[ident] = block_tint(block)
            links.blocks.setdefault(key, seen[ident])
            if tints[ident] is not None:
                links.tints.setdefault(key, tints[ident])
    return links
