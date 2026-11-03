"""
Frostbite meshes: a `MeshSet` resource and the chunk its levels of detail point at.

A mesh in current Battlefield is two pieces. The **MeshSet** res is the
description — bounding box, levels of detail, and for each level its sections
(one per material) with their vertex layout — and each level names a **chunk**
by GUID that holds the vertex and index buffers. The res is found by name in a
level's bundles (`frostbitebundle`); the chunk by GUID in the level's table.

The layout
----------
Nothing here is documented by the game. It was read off the bytes of one mesh,
a crate, and then held against every one of the 4,090 meshes a level ships —
14,043 levels of detail, 43,130 sections — before any of it was trusted. The
Frosty modding tools describe older versions of the same structure, which is
where the field names come from; the offsets are this game's own.

The res opens with four little-endian words — the size of the header, of one
level-of-detail record and of one section record — and everything after those
sixteen bytes is addressed from there::

    header      bounding box (two vec4), six i64 offsets of the levels of
                detail, names; at 0x6C the mesh type (0 rigid, 1 skinned,
                2 composite); at 0x9C the level and section counts
    level       at +0x08 its section count and the i64 offset of its sections;
                +0x54 index format, +0x58 index bytes, +0x5C vertex bytes,
                +0x74 the chunk's GUID
    section     +0x08 material name; +0x1E vertex stride; +0x1F primitive
                type (3, a triangle list, in every section); +0x20 triangles,
                first index, vertex offset (bytes), vertex count; +0x64 the
                vertex declaration — sixteen (usage, format, offset, stream)
                elements, then sixteen (stride, classification) streams, then
                the two counts

The record sizes are 176 or 192 for the header, 176 to 188 for a level and 368
for a section. The fields this reads sit at the same offsets in all of them; the
extra bytes are bones and parts for skinned and composite meshes, which a level
export has no use for.

The chunk is the vertex buffer then the index buffer. Within a section the
streams follow each other — stream *k* starts `vertex count x` the strides of the
streams before it into the section's vertices — and indices count from the
section's first vertex. Positions are always element usage 1 in stream 0 at
offset 0, as four halves (format 8) or three floats (format 3); indices are 16
bits under format 0x21 and 32 under 0x2E. The decoded crate measures 1.08 by
0.75 by 0.87 metres, Y up, and looks like a crate.

What is left out
----------------
- Levels of detail stored inline in the res instead of in a chunk: 35 of 14,078
  in a level, on gadgets rather than scenery. Refused with a message.
- Normals. They are recomputed by the writer as everywhere else in this
  package. Texture coordinates are read (`decode_sections`); which texture a
  section shows is `frostbitematerial`'s business.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

import numpy as np

from .frostbite import UnsupportedFrostbite

#: The MeshSet res type, as bundle manifests give it.
MESHSET = 0x49B156D4

#: Vertex element formats a position comes in, with their numpy reading.
POSITION_FORMATS = {
    3: ("<f4", 3),  # Float3
    4: ("<f4", 4),  # Float4
    7: ("<f2", 3),  # Half3
    8: ("<f2", 4),  # Half4
}

#: Texture coordinate formats: two halves, or two floats.
UV_FORMATS = {
    2: ("<f4", 2),  # Float2
    6: ("<f2", 2),  # Half2
}

#: Index buffer formats: the RenderFormat values seen, and their widths.
INDEX_FORMATS = {0x21: "<u2", 0x2E: "<u4"}

MESH_TYPES = {0: "rigid", 1: "skinned", 2: "composite"}

#: A level of detail lists its sections in five draw categories, each an i32
#: count and an i64 offset to that many section-index bytes: opaque,
#: transparent, transparent decal, depth only, shadow. In a level's meshes the
#: lists are clean — every section named `..._shadow` is in the last two and
#: only there — so they decide what is drawn, not the names.
OPAQUE, TRANSPARENT = 0, 1

_PREFIX = 16
_TRIANGLE_LIST = 3
_USAGE_POSITION = 1
_USAGE_TEXCOORD0 = 0x21
_USAGE_TEXCOORD1 = 0x22
#: The third and fourth texture coordinate sets. On a wall's lettering they
#: lay the letter sheet over the panel exactly once, where the first set
#: tiles the wall's plaster across it (see `frostbitelevel._sheet_uvs`).
_USAGE_TEXCOORD2 = 0x23
_USAGE_TEXCOORD3 = 0x24
#: Four unsigned bytes a vertex. In the backdrops' palette materials the first
#: two are where in the palette the vertex's colour is, x and y out of 255.
_USAGE_PALETTE = 0x1E
_UBYTE4 = 13


@dataclass
class Section:
    material: str
    stride: int
    triangles: int
    first_index: int
    vertex_offset: int
    vertex_count: int
    #: (usage, format, offset, stream) for each element.
    elements: list[tuple[int, int, int, int]]
    #: Byte stride of each stream.
    streams: list[int]
    #: Eight bytes at +0x130 that key the section's material in the level's
    #: shader block depots (see `frostbitematerial`).
    key: bytes = b""


@dataclass
class Lod:
    chunk: bytes
    index_format: int
    index_bytes: int
    vertex_bytes: int
    sections: list[Section] = field(default_factory=list)
    #: Indices of the sections drawn as surfaces: the level's opaque and
    #: transparent lists. The others are depth-only, shadow-only or decals.
    drawn: set[int] = field(default_factory=set)

    @property
    def triangles(self) -> int:
        """Triangles drawn: the shadow and depth-only copies are not counted."""
        return sum(s.triangles for i, s in enumerate(self.sections) if i in self.drawn)


@dataclass
class MeshSet:
    name: str
    kind: str
    low: np.ndarray
    high: np.ndarray
    lods: list[Lod]


def _cstring(data: bytes, at: int) -> str:
    if not 0 <= at < len(data):
        return ""
    end = data.find(b"\x00", at)
    return data[at : end if end >= 0 else len(data)].decode("utf-8", "replace")


def read_meshset(res: bytes, name: str = "mesh") -> MeshSet:
    """
    The description of one mesh, from its MeshSet res.

    Raises rather than guessing when a record size or a level's section table
    does not fit the res — those are the cheap checks that the layout above
    applies.
    """
    if len(res) < _PREFIX + 0xA0:
        raise UnsupportedFrostbite(f"{name}: too short for a MeshSet")
    header_size, lod_size, section_size, _zero = struct.unpack_from("<4I", res, 0)
    if section_size != 368 or not 0xA0 <= header_size <= 0x100 or not 0xA8 <= lod_size <= 0x100:
        raise UnsupportedFrostbite(
            f"{name}: record sizes {header_size}/{lod_size}/{section_size} are not "
            "the ones this reader knows"
        )
    data = res[_PREFIX:]
    box = np.frombuffer(data, dtype="<f4", count=8, offset=0).reshape(2, 4)[:, :3]
    offsets = [v for v in struct.unpack_from("<6q", data, 0x20) if v]
    kind = MESH_TYPES.get(data[0x6C], f"type {data[0x6C]}")
    count, _sections = struct.unpack_from("<HH", data, 0x9C)
    if count != len(offsets):
        raise UnsupportedFrostbite(
            f"{name}: {count} levels of detail declared and {len(offsets)} offsets given"
        )

    lods: list[Lod] = []
    for at in offsets:
        if at + lod_size > len(data):
            raise UnsupportedFrostbite(f"{name}: a level of detail runs past the res")
        n_sections, sections_at = struct.unpack_from("<Iq", data, at + 0x08)
        index_format, index_bytes, vertex_bytes = struct.unpack_from("<iII", data, at + 0x54)
        lod = Lod(data[at + 0x74 : at + 0x84], index_format, index_bytes, vertex_bytes)
        for category in (OPAQUE, TRANSPARENT):
            listed, where = struct.unpack_from("<iq", data, at + 0x14 + 12 * category)
            if listed > 0 and 0 <= where and where + listed <= len(data):
                lod.drawn.update(data[where : where + listed])
        if sections_at + n_sections * section_size > len(data):
            raise UnsupportedFrostbite(f"{name}: a section table runs past the res")
        for k in range(n_sections):
            s = sections_at + k * section_size
            stride, primitive = data[s + 0x1E], data[s + 0x1F]
            if primitive != _TRIANGLE_LIST:
                raise UnsupportedFrostbite(f"{name}: primitive type {primitive} is not a triangle list")
            triangles, first, vertex_offset, vertices = struct.unpack_from("<4I", data, s + 0x20)
            n_elements, n_streams = data[s + 0xC4], data[s + 0xC5]
            elements = [
                tuple(data[s + 0x64 + 4 * i : s + 0x68 + 4 * i]) for i in range(min(n_elements, 16))
            ]
            streams = [data[s + 0xA4 + 2 * i] for i in range(min(n_streams, 16))]
            if sum(streams) != stride:
                raise UnsupportedFrostbite(
                    f"{name}: section streams add up to {sum(streams)}, not its stride {stride}"
                )
            (material_at,) = struct.unpack_from("<q", data, s + 0x08)
            lod.sections.append(
                Section(
                    material=_cstring(data, material_at),
                    stride=stride,
                    triangles=triangles,
                    first_index=first,
                    vertex_offset=vertex_offset,
                    vertex_count=vertices,
                    elements=elements,
                    streams=streams,
                    key=bytes(data[s + 0x130 : s + 0x138]),
                )
            )
        lods.append(lod)
    return MeshSet(name=name, kind=kind, low=box[0].copy(), high=box[1].copy(), lods=lods)


@dataclass
class SectionGeometry:
    """One drawn section: its own vertices, triangles and texture coordinates."""

    index: int
    material: str
    positions: np.ndarray
    faces: np.ndarray
    #: The first texture coordinate set, (N, 2), or None if the section has
    #: none. Not wrapped into 0..1: Frostbite materials tile.
    uvs: np.ndarray | None
    #: The four-byte element `_USAGE_PALETTE`, (N, 4) uint8, if the section has it.
    palette: np.ndarray | None = None
    #: The second texture coordinate set, (N, 2), if the section has one.
    uvs2: np.ndarray | None = None
    #: The third and fourth sets, (N, 2), if the section has them.
    uvs3: np.ndarray | None = None
    uvs4: np.ndarray | None = None


def _element(buffers: bytes, section: Section, element, formats, name: str) -> np.ndarray:
    _usage, fmt, offset, stream = element
    if fmt not in formats:
        raise UnsupportedFrostbite(f"{name}: vertex element format {fmt} is not known")
    dtype, components = formats[fmt]
    stream_at = section.vertex_offset + section.vertex_count * sum(section.streams[:stream])
    stride = section.streams[stream]
    raw = np.frombuffer(buffers, dtype=np.uint8, count=section.vertex_count * stride, offset=stream_at)
    raw = raw.reshape(section.vertex_count, stride)[:, offset : offset + components * np.dtype(dtype).itemsize]
    return np.ascontiguousarray(raw).view(dtype).reshape(section.vertex_count, components).astype(np.float32)


def decode_sections(lod: Lod, buffers: bytes, name: str = "mesh") -> list[SectionGeometry]:
    """
    Every drawn section of one level of detail, separately.

    `buffers` is the level's chunk: the vertex buffer, then the index buffer.
    The sections drawn are the level's opaque and transparent ones; a
    shadow-only section repeats the same surface coarser, and a decal floats a
    hair above another. Texture coordinates are usage 0x21 — two halves (format
    6) in every drawn section of a level but a handful, which have two floats
    (format 2).
    """
    if lod.chunk == bytes(16):
        raise UnsupportedFrostbite(f"{name}: this level of detail is stored inline, which is not read")
    if len(buffers) < lod.vertex_bytes + lod.index_bytes:
        raise UnsupportedFrostbite(
            f"{name}: the chunk holds {len(buffers)} bytes, not the "
            f"{lod.vertex_bytes} + {lod.index_bytes} the mesh declares"
        )
    width = INDEX_FORMATS.get(lod.index_format)
    if width is None:
        raise UnsupportedFrostbite(f"{name}: index format 0x{lod.index_format:X} is not known")
    item = np.dtype(width).itemsize

    out: list[SectionGeometry] = []
    for index, section in enumerate(lod.sections):
        if index not in lod.drawn or not section.triangles:
            continue
        position = [e for e in section.elements if e[0] == _USAGE_POSITION]
        if not position:
            continue
        stream = position[0][3]
        stream_at = section.vertex_offset + section.vertex_count * sum(section.streams[:stream])
        if stream_at + section.vertex_count * section.streams[stream] > lod.vertex_bytes:
            raise UnsupportedFrostbite(f"{name}: a section's vertices run past the vertex buffer")
        xyz = _element(buffers, section, position[0], POSITION_FORMATS, name)[:, :3]

        start = lod.vertex_bytes + section.first_index * item
        count = section.triangles * 3
        if start + count * item > lod.vertex_bytes + lod.index_bytes:
            raise UnsupportedFrostbite(f"{name}: a section's indices run past the index buffer")
        tri = np.frombuffer(buffers, dtype=width, count=count, offset=start).reshape(-1, 3).astype(np.int64)
        if len(tri) and tri.max() >= section.vertex_count:
            raise UnsupportedFrostbite(
                f"{name}: an index reaches vertex {tri.max()} of {section.vertex_count}"
            )
        if not np.isfinite(xyz).all():
            raise UnsupportedFrostbite(f"{name}: positions that are not finite")
        uv = [e for e in section.elements if e[0] == _USAGE_TEXCOORD0]
        uvs = None
        if uv and uv[0][1] in UV_FORMATS:
            uvs = _element(buffers, section, uv[0], UV_FORMATS, name)[:, :2]
            if not np.isfinite(uvs).all():
                uvs = None
        bytes4 = [e for e in section.elements if e[0] == _USAGE_PALETTE and e[1] == _UBYTE4]
        palette = _element(buffers, section, bytes4[0], {_UBYTE4: ("<u1", 4)}, name) if bytes4 else None
        more = []
        for usage in (_USAGE_TEXCOORD1, _USAGE_TEXCOORD2, _USAGE_TEXCOORD3):
            found = [e for e in section.elements if e[0] == usage and e[1] in UV_FORMATS]
            extra = _element(buffers, section, found[0], UV_FORMATS, name)[:, :2] if found else None
            more.append(extra if extra is not None and np.isfinite(extra).all() else None)
        out.append(SectionGeometry(index, section.material, xyz, tri, uvs, palette, *more))
    return out


def decode_lod(lod: Lod, buffers: bytes, name: str = "mesh") -> tuple[np.ndarray, np.ndarray]:
    """Positions (N x 3, float32) and triangles (M x 3) of a level's drawn sections."""
    parts = decode_sections(lod, buffers, name)
    if not parts:
        return np.zeros((0, 3), np.float32), np.zeros((0, 3), np.int64)
    faces = []
    base = 0
    for part in parts:
        faces.append(part.faces + base)
        base += len(part.positions)
    return np.concatenate([p.positions for p in parts]), np.concatenate(faces)
