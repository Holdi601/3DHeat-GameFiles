"""
Miniature Frostbite files, built the way the readers expect them.

Every structure here is the inverse of what a reader in `heat3d_gamefiles`
parses, kept as small as it can be while still exercising the parts that go
wrong: a level table whose chunk identifiers and locations are in different
orders, a bundle whose entries continue a blob named earlier, a mesh with a
shadow section that must not be drawn, a partition with a group member.
"""

from __future__ import annotations

import struct

import numpy as np

from heat3d_gamefiles.frostbite import MAGIC_SIGNED, SIGNED_HEADER


def location(package: int, cas: int, offset: int, size: int) -> bytes:
    """A sixteen-byte location record."""
    return struct.pack(">4I", package >> 16, ((package & 0xFFFF) << 16) | cas, offset, size)


def bundle_blob(entries: list[tuple[int, int, int, int]]) -> bytes:
    """An inline bundle: (package, cas, offset, size) per entry."""
    body = b""
    flags = b""
    last = None
    for package, cas, offset, size in entries:
        if (package, cas) != last:
            body += struct.pack(">2I", package >> 16, ((package & 0xFFFF) << 16) | cas)
            flags += b"\x80"
            last = (package, cas)
        else:
            flags += b"\x00"
        body += struct.pack(">2I", offset, size)
    count = len(entries)
    header = struct.pack(">9I", 0, 0, 36 + len(body), count, 36, 36, 36, 0, count)
    return header + body + flags


def level_table(chunks: list[tuple[bytes, bytes]], bundles: list[bytes]) -> bytes:
    """
    A signed binary level table: `chunks` are (GUID, location record), and
    the location records are written in reverse order so that pairing by file
    order is wrong.
    """
    n, nb = len(chunks), len(bundles)
    lookup = 60
    table = lookup + 4 * nb
    index = -(-(60 + 20 * nb) // 8) * 8
    assets = index + 4 * n
    where = assets + 20 * n
    extra = where + 16 * n
    end = extra
    fields = (60, table, nb, index, assets, n, where, where, extra, where, 4 * n, 0, 0, 0, end)
    body = bytearray(struct.pack(">15I", *fields))
    body += b"\xff" * (4 * nb)
    blobs_at = end
    records = b""
    for blob in bundles:
        records += struct.pack(">4I", 0, 0x40000000 | len(blob), 0, blobs_at)
        blobs_at += len(blob)
    body += records
    body += b"\x00" * (index - len(body))
    body += b"\xff" * (4 * n)
    order = list(reversed(range(n)))
    for i, (guid, _record) in enumerate(chunks):
        body += guid[::-1] + struct.pack(">I", 0x80000000 | 4 * order.index(i))
    for k in order:
        body += chunks[k][1]
    for blob in bundles:
        body += blob
    signed = struct.pack("<I", MAGIC_SIGNED).ljust(SIGNED_HEADER, b"\x00")
    return signed + bytes(body)


def manifest(ebx: list[tuple[str, int]], res: list[tuple[str, int, int]], chunks: list[bytes]) -> bytes:
    """A binary bundle manifest: ebx (name, size), res (name, size, type), chunk GUIDs."""
    total = len(ebx) + len(res) + len(chunks)
    names = b""
    offsets = []
    for name in [e[0] for e in ebx] + [r[0] for r in res]:
        offsets.append(len(names))
        names += name.encode() + b"\x00"
    records = b"\x00" * (20 * total)
    for (_, size), at in zip(ebx, offsets):
        records += struct.pack("<2I", at, size)
    for (_, size, _), at in zip(res, offsets[len(ebx) :]):
        records += struct.pack("<2I", at, size)
    records += b"".join(struct.pack("<I", r[2]) for r in res)
    records += b"\x00" * (16 * len(res))
    records += b"".join(struct.pack("<Q", 1000 + i) for i in range(len(res)))
    records += b"".join(g + struct.pack("<2I", 0, 64) for g in chunks)
    strings = 32 + len(records)
    head = struct.pack("<7I", total, len(ebx), len(res), len(chunks), strings, strings + len(names), 0)
    body = struct.pack(">I", 0xD68E799D) + head + records + names
    return struct.pack(">I", len(body)) + body


def meshset(
    triangles: int, vertices: int, shadow: bool = True, chunk: bytes = b"C" * 16, uv: bool = False
) -> bytes:
    """
    A rigid MeshSet with one level of detail: an opaque section, and optionally
    a shadow section after it that only the shadow list names. With `uv`, each
    section has a second stream of half-float texture coordinates.
    """
    header, lod_size, section_size = 176, 176, 368
    sections = 2 if shadow else 1
    lod_at = header
    sections_at = lod_at + lod_size
    lists_at = sections_at + sections * section_size
    names_at = lists_at + 8
    data = bytearray(names_at + 64)

    struct.pack_into("<8f", data, 0, -1, -1, -1, 0, 1, 1, 1, 0)
    struct.pack_into("<6q", data, 0x20, lod_at, 0, 0, 0, 0, 0)
    data[0x6C] = 0
    struct.pack_into("<HH", data, 0x9C, 1, sections)

    stride = 12 if uv else 8
    vertex_bytes = vertices * stride * sections
    index_bytes = triangles * 3 * 2 * sections
    struct.pack_into("<IIIq", data, lod_at, 0, 0xFFFF, sections, sections_at)
    struct.pack_into("<iq", data, lod_at + 0x14, 1, lists_at)  # opaque: section 0
    if shadow:
        struct.pack_into("<iq", data, lod_at + 0x14 + 12 * 4, 1, lists_at + 1)
    data[lists_at] = 0
    data[lists_at + 1] = 1
    struct.pack_into("<iII", data, lod_at + 0x54, 0x21, index_bytes, vertex_bytes)
    data[lod_at + 0x74 : lod_at + 0x84] = chunk

    data[names_at : names_at + 9] = b"M_Thing\x00\x00"
    data[names_at + 16 : names_at + 32] = b"M_Thing_Shadow\x00\x00"
    for k in range(sections):
        s = sections_at + k * section_size
        struct.pack_into("<q", data, s + 0x08, names_at + 16 * k)
        data[s + 0x1E] = stride
        data[s + 0x1F] = 3
        struct.pack_into("<4I", data, s + 0x20, triangles, k * triangles * 3, k * vertices * stride, vertices)
        data[s + 0x64 : s + 0x68] = bytes((1, 8, 0, 0))  # position, half4, offset 0, stream 0
        data[s + 0xA4] = 8
        data[s + 0xC4], data[s + 0xC5] = 1, 1
        if uv:
            data[s + 0x68 : s + 0x6C] = bytes((0x21, 6, 0, 1))  # texcoord 0, half2, stream 1
            data[s + 0xA6] = 4
            data[s + 0xC4], data[s + 0xC5] = 2, 2
        data[s + 0x130 : s + 0x138] = bytes([k + 1]) * 8
    return struct.pack("<4I", header, lod_size, section_size, 0) + bytes(data)


def buffers(positions: np.ndarray, faces: np.ndarray, sections: int = 2, uvs=None) -> bytes:
    """The chunk for `meshset`: every section's half4 positions (and half2 UVs), then indices."""
    half = np.zeros((len(positions), 4), dtype="<f2")
    half[:, :3] = positions
    half[:, 3] = 1
    one = half.tobytes()
    if uvs is not None:
        one += np.asarray(uvs, dtype="<f2").tobytes()
    vertex = one * sections
    index = faces.astype("<u2").tobytes() * sections
    return vertex + index


def partition(
    types: list[tuple[bytes, int]],
    data: bytes,
    instances: list[int],
    pointers: list[int],
    imports: list[tuple[bytes, bytes]],
    import_offsets: list[int],
    arrays: list[tuple[int, int, int]],
    guid: bytes = b"P" * 16,
) -> bytes:
    """
    A RIFF EBX partition. `data` is the aligned data; `arrays` are
    (offset, count, element type index).
    """

    def table(values: list[int]) -> bytes:
        return struct.pack("<I", len(values)) + b"".join(struct.pack("<I", v) for v in values)

    efix = guid
    efix += struct.pack("<I", len(types)) + b"".join(g for g, _ in types)
    efix += table([s for _, s in types])
    efix += struct.pack("<I", len(instances))
    efix += table(instances) + table(pointers) + table([])
    efix += struct.pack("<I", len(imports)) + b"".join(p + i for p, i in imports)
    efix += table(import_offsets) + table([])
    efix += struct.pack("<3I", len(data), len(data), len(data)) + table([])
    ebxx = struct.pack("<2I", len(arrays), 0) + b"".join(
        struct.pack("<IiIHH", offset, count, 0, 0x48, kind) for offset, count, kind in arrays
    )
    # EBXD's data starts at file offset 20; pad it to 32 so it is aligned.
    ebxd = b"\x00" * 12 + data
    body = b"EBX\x00"
    for tag, chunk in ((b"EBXD", ebxd), (b"EFIX", efix), (b"EBXX", ebxx)):
        body += tag + struct.pack("<I", len(chunk)) + chunk
        if len(chunk) & 1:
            body += b"\x00"
    return b"RIFF" + struct.pack("<I", len(body)) + body


def terrain_tree(samples: int, height_range: float, square: float, nodes) -> bytes:
    """
    A terrain streaming tree: a heightfield raster tree, then the node quadtree.
    `nodes` is a nested tuple: (chunk GUID, flags, [children...]).
    """
    header = bytearray(34)
    count = 0

    def walk(node):
        nonlocal count
        guid, flags, children = node
        count += 1
        out = struct.pack("<I", 1000) + guid + b"\x00" + bytes([flags, 1 if children else 0])
        for child in children:
            out += walk(child)
        return out

    body = walk(nodes)
    struct.pack_into("<I", header, 25, count)
    tree = bytearray(71)
    struct.pack_into("<I", tree, 0, samples)
    struct.pack_into("<f", tree, 16, height_range)
    record = b"\x00" + struct.pack("<6f", -square / 2, 0, -square / 2, square / 2, height_range, square / 2)
    tree += record
    return bytes(header) + b"\x00" + struct.pack("<I", len(tree)) + bytes(tree) + b"\xff" + body
