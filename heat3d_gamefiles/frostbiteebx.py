"""
Frostbite EBX partitions in their RIFF form, read without the game's type library.

EBX is how Frostbite stores everything that is not raw data: a level's layout,
a prefab, the asset that says which mesh a prop uses. Each partition is a RIFF
file of three chunks::

    RIFF <size> EBX\\0 (or EBXS)
      EBXD   the instances and arrays, aligned to 16 inside the chunk
      EFIX   what the data needs fixing up with
      EBXX   the array and boxed-value tables

EFIX, all little-endian, in order::

    partition GUID
    type GUIDs        count, then 16 bytes each
    type signatures   count, then a word each
    exported instance count
    instance offsets  count, then a word each
    pointer offsets, resource-reference offsets      count + words, each
    imports           count, then (partition GUID, instance GUID) each
    import offsets, type-info offsets                count + words, each
    array offset, boxed-value offset, string offset
    one more table    count + words; usually empty

EBXX is two counts, then sixteen bytes per array — offset, element count, a
hash, type flags, and the index of its element type among the type GUIDs.

Every offset counts from the start of the aligned data. The instance's first
sixteen bits index its type; an exported instance has its GUID in the sixteen
bytes before it. A pointer field is eight bytes: zero is null, an odd value is
import number `value >> 1`, and anything else is relative to the field. An array
field is a relative offset to the array's first element; its count is the word
before it.

The chunk layout is public — the Frosty modding tools read the same form for
earlier Frostbite games — and it closes here on all 4,439 partitions tried, a
level's own and 3,000 more at random: the EFIX fields consume the chunk to the
word. Signatures are one per type, except that a few partitions list one or
more last types without one.

What is not in the files
------------------------
The type library: which fields a type has and where. The game ships it encrypted
in its initial file system, which this package does not touch, and does not
need to: a type is known by its GUID and signature, both in every partition, and
the few this package reads were laid out from the data — see `frostbitelevel`.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

from .frostbite import UnsupportedFrostbite


@dataclass(frozen=True)
class Array:
    offset: int
    count: int
    hash: int
    flags: int
    #: Index into `Partition.types` of the element type, or 0xFFFF for a
    #: primitive.
    type: int


@dataclass
class Partition:
    guid: bytes
    #: The aligned data every offset counts from.
    data: bytes
    types: list[bytes]
    signatures: list[int]
    exported: int
    instances: list[int]
    pointers: set[int]
    imports: list[tuple[bytes, bytes]]
    import_offsets: set[int]
    arrays: list[Array]
    #: Arrays by the offset of their first element.
    by_offset: dict[int, Array] = field(default_factory=dict)

    def type_index(self, guid: bytes, signature: int | None = None) -> list[int]:
        """Indices of a type in this partition's type list."""
        return [
            i
            for i, g in enumerate(self.types)
            if g == guid
            and (signature is None or (i < len(self.signatures) and self.signatures[i] == signature))
        ]

    def pointer(self, at: int) -> tuple[str, int]:
        """
        What the pointer field at `at` holds: ("null", 0), ("import", index) or
        ("local", target offset).
        """
        (value,) = struct.unpack_from("<q", self.data, at)
        if value == 0:
            return "null", 0
        if value & 1:
            index = value >> 1
            if index >= len(self.imports):
                raise UnsupportedFrostbite(f"import {index} of {len(self.imports)}")
            return "import", index
        return "local", at + value

    def array_at(self, at: int) -> Array | None:
        """The array an array field at `at` refers to, if it is one."""
        (relative,) = struct.unpack_from("<i", self.data, at)
        return self.by_offset.get(at + relative)


def _chunks(raw: bytes) -> dict[bytes, tuple[int, int]]:
    if raw[:4] != b"RIFF" or raw[8:12] not in (b"EBX\x00", b"EBXS"):
        raise UnsupportedFrostbite("not a RIFF EBX partition")
    out: dict[bytes, tuple[int, int]] = {}
    at = 12
    while at + 8 <= len(raw):
        tag = raw[at : at + 4]
        (size,) = struct.unpack_from("<I", raw, at + 4)
        out[tag] = (at + 8, size)
        at += 8 + size
        at += at & 1
    for tag in (b"EBXD", b"EFIX", b"EBXX"):
        if tag not in out:
            raise UnsupportedFrostbite(f"partition has no {tag.decode()} chunk")
    return out


def read_partition(raw: bytes, name: str = "partition") -> Partition:
    chunks = _chunks(raw)
    data_at, data_size = chunks[b"EBXD"]
    base = data_at + (-data_at) % 16
    data = raw[base : data_at + data_size]

    at, size = chunks[b"EFIX"]
    end = at + size

    def word() -> int:
        nonlocal at
        if at + 4 > end:
            raise UnsupportedFrostbite(f"{name}: EFIX ended early")
        (value,) = struct.unpack_from("<I", raw, at)
        at += 4
        return value

    def words() -> list[int]:
        nonlocal at
        count = word()
        if at + 4 * count > end:
            raise UnsupportedFrostbite(f"{name}: an EFIX table runs past the chunk")
        out = list(struct.unpack_from(f"<{count}I", raw, at))
        at += 4 * count
        return out

    guid = raw[at : at + 16]
    at += 16
    count = word()
    types = [raw[at + 16 * i : at + 16 * i + 16] for i in range(count)]
    at += 16 * count
    signatures = words()
    exported = word()
    instances = words()
    pointers = words()
    _resource_refs = words()
    count = word()
    imports = [(raw[at + 32 * i : at + 32 * i + 16], raw[at + 32 * i + 16 : at + 32 * i + 32]) for i in range(count)]
    at += 32 * count
    import_offsets = words()
    _type_info = words()
    for _ in range(3):
        word()
    _trailing = words()
    if at != end:
        raise UnsupportedFrostbite(f"{name}: EFIX has {end - at} bytes left over")
    # Usually one signature per type; some partitions list a last type with
    # none, so the signatures are a prefix of the types, never more.
    if len(signatures) > len(types):
        raise UnsupportedFrostbite(f"{name}: {len(types)} types and {len(signatures)} signatures")

    at, size = chunks[b"EBXX"]
    n_arrays, _n_boxed = struct.unpack_from("<2I", raw, at)
    if 8 + 16 * n_arrays > size:
        raise UnsupportedFrostbite(f"{name}: the array table runs past EBXX")
    arrays = [Array(*struct.unpack_from("<IiIHH", raw, at + 8 + 16 * i)) for i in range(n_arrays)]

    partition = Partition(
        guid=guid,
        data=data,
        types=types,
        signatures=signatures,
        exported=exported,
        instances=instances,
        pointers=set(pointers),
        imports=imports,
        import_offsets=set(import_offsets),
        arrays=arrays,
    )
    partition.by_offset = {a.offset: a for a in arrays}
    return partition


def partition_guid(raw: bytes) -> bytes:
    """Only the partition's own GUID: the first sixteen bytes of EFIX."""
    at, _size = _chunks(raw)[b"EFIX"]
    return raw[at : at + 16]
