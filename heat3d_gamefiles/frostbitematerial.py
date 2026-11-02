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
_AVOID = re.compile(
    r"dest|detail|decal|overlay|dirt|noise|grunge|lookup|fracture|damage|burn|blood|snow|puddle|wet|test",
    re.I,
)


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


def read_texture_header(res: bytes, name: str = "texture") -> TextureInfo:
    if len(res) < 120:
        raise UnsupportedFrostbite(f"{name}: too short for a texture header")
    kind, fmt = struct.unpack_from("<II", res, 8)
    width, height = struct.unpack_from("<HH", res, 22)
    mips = res[30]
    sizes = struct.unpack_from("<15I", res, 56)[: max(1, min(mips, 15))]
    return TextureInfo(name, kind, fmt, width, height, mips, res[40:56], sizes)


def decode_texture(info: TextureInfo, chunk: bytes, largest: int) -> np.ndarray:
    """
    The largest mip the chunk holds that is no wider or taller than `largest`,
    as 8-bit RGB.
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
            return np.asarray(image.convert("RGB"))
        at += info.sizes[level]
    raise UnsupportedFrostbite(f"{info.name}: no mip to decode")


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
    usage: Counter = field(default_factory=Counter)
    headers: dict[str, TextureInfo] = field(default_factory=dict)

    def colour_map(self, mesh: str, material: str, key: bytes) -> str | None:
        names = self.blocks.get(key)
        if not names:
            return None
        candidates = [
            n for n in set(names)
            if n in self.headers
            and self.headers[n].kind == 0
            and self.headers[n].format in COLOUR_FORMATS
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
    by_guid: dict[bytes, str] = {}
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
            links.blocks.setdefault(key, seen[ident])
    return links
