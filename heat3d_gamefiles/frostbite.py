"""
Reading Frostbite `.toc` tables of contents.

Frostbite — Battlefield, Need for Speed, Dead Space — keeps its content in a few
dozen `.cas` blobs and describes them in `.toc` files. The `.toc` is the map: it
names the superbundles, the bundles inside them, and for each piece of content
the blob index, offset and length where its bytes actually live.

The header that looks encrypted and is not
------------------------------------------
A `.toc` opens with a 32-bit magic that decides what follows::

    0x00CED100   plain; the tree starts immediately
    0x01CED100   signed; a 556-byte header, then the tree in the clear
    0x03CED100   obfuscated; the payload is XORed

The middle one is what current Battlefield ships, and the high-entropy bytes
after the magic are a signature, not ciphertext — the tree begins in plain sight
at offset 556. Treating the whole file as encrypted because its first kilobyte
looks random is the easy mistake here, and it is wrong.

The third is XOR obfuscation with the key carried in the file's own header. That
is not an access control and no key is needed from anyone, but it is also not
something any file on hand uses, so it is detected and reported rather than
implemented against nothing.

The tree
--------
Everything after the header is one recursive structure. Each field is a type
byte, an optional name, and a value; containers carry their length as a
variable-length integer and end with a zero byte::

    82              anonymous object, length follows
      84 e1 0c        209028 bytes of contents
      01 "superBundles\0"   a named list
        af 1e             3887 bytes
        82 19             anonymous object, 25 bytes
          07 "name\0"       a named string
            11 "Win32/characters\0"
          00              end of object
        ...
      00              end of list

Whether the type table below is right is not a matter of opinion: every
container declares its own length, so a wrong type desynchronises the cursor and
the length no longer matches. `parse_toc` checks that on every container, which
is why it can be trusted on files nobody has seen.

Getting to the bytes
--------------------
Current Battlefield ships a second form: a binary section table rather than a
tree. It is undocumented, and every step of reading it was checked against the
files rather than assumed.

    the section chain   each section starts where the last ends — closes on all
                        136 tables Battlefield 6 ships
    asset identifiers   all 74,175 in one level table come back distinct, which
                        a wrong record stride does not produce
    asset locations     all 74,175 land inside an installed .cas blob, none past
                        the end of its file, none naming a blob that is absent
    packages            each location names the installation package its blob
                        belongs to, and `layout.toc` says which folder that is —
                        all 3.3 million locations of the 144 tables resolve, and
                        land inside the blob they name
    payloads            chains of eight-byte-headed blocks; a chain consumes the
                        payload exactly or it is not a chain

Every one of 300 payloads sampled from a level decodes that way. An earlier
version of this reader ignored the package and took the first `cas_NN.cas` it
found with the right number, and a third of the payloads it read then looked
high-entropy from their first byte — they were the right offsets in the wrong
blob, not encryption. Nothing found so far is encrypted.

Turning a decoded payload into geometry is the Frostbite mesh format on top; see
`frostbitebundle` for what the bundles name and `frostbitemesh` for the meshes.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

#: Magic values, and what each says about the payload.
MAGIC_PLAIN = 0x00CED100
MAGIC_SIGNED = 0x01CED100
MAGIC_OBFUSCATED = 0x03CED100

#: A signed header is this long; the tree begins after it.
SIGNED_HEADER = 556

#: DbObject field types. The low five bits of a type byte select one of these;
#: bit 7 means the field is anonymous and carries no name.
T_EOF = 0x00
T_LIST = 0x01
T_OBJECT = 0x02
T_BOOL = 0x06
T_STRING = 0x07
T_INT = 0x08
T_LONG = 0x09
T_FLOAT = 0x0A
T_DOUBLE = 0x0B
T_GUID = 0x0F
T_SHA1 = 0x10
T_MATRIX = 0x11
T_VECTOR4 = 0x12
T_BLOB = 0x13

#: Fixed-width types and their sizes, so the reader needs no branch for each.
#:
#: `T_LONG` is eight bytes, which is the one worth stating outright: reading it
#: as four desynchronises the cursor by four bytes, and because most integers in
#: a toc are small and little-endian, the next field still often lands on
#: something that decodes. The damage surfaces far from its cause.
_FIXED = {
    T_BOOL: 1,
    T_INT: 4,
    T_LONG: 8,
    T_FLOAT: 4,
    T_DOUBLE: 8,
    T_GUID: 16,
    T_SHA1: 20,
    T_MATRIX: 64,
    T_VECTOR4: 16,
}


class UnsupportedFrostbite(Exception):
    """Not a Frostbite table of contents this reader can read."""


@dataclass(frozen=True)
class TocInfo:
    """What the magic said."""

    magic: int
    payload_offset: int

    @property
    def kind(self) -> str:
        return {
            MAGIC_PLAIN: "plain",
            MAGIC_SIGNED: "signed",
            MAGIC_OBFUSCATED: "obfuscated",
        }.get(self.magic, f"unknown(0x{self.magic:08X})")


class _Cursor:
    """A little-endian cursor over the tree."""

    def __init__(self, data: bytes, at: int = 0):
        self.data = data
        self.at = at

    def u8(self) -> int:
        if self.at >= len(self.data):
            raise UnsupportedFrostbite("tree ended mid-field")
        value = self.data[self.at]
        self.at += 1
        return value

    def varint(self) -> int:
        """
        A little-endian base-128 integer: seven bits per byte, high bit to continue.

        Used for every container length and string length, so a misread here
        throws the whole rest of the file out rather than one field.
        """
        value = 0
        shift = 0
        while True:
            byte = self.u8()
            value |= (byte & 0x7F) << shift
            if not byte & 0x80:
                return value
            shift += 7
            if shift > 63:
                raise UnsupportedFrostbite("variable-length integer did not terminate")

    def cstring(self) -> str:
        end = self.data.find(b"\x00", self.at)
        if end < 0:
            raise UnsupportedFrostbite("unterminated name")
        out = self.data[self.at : end].decode("utf-8", "replace")
        self.at = end + 1
        return out

    def take(self, count: int) -> bytes:
        if self.at + count > len(self.data):
            raise UnsupportedFrostbite("field ran past the end of the file")
        out = self.data[self.at : self.at + count]
        self.at += count
        return out


def read_header(data: bytes, name: str = "toc") -> TocInfo:
    """Decide where the tree starts, or say why it cannot be read."""
    if len(data) < 8:
        raise UnsupportedFrostbite(f"{name} is too small to be a table of contents")
    (magic,) = struct.unpack_from("<I", data, 0)

    if magic == MAGIC_PLAIN:
        return TocInfo(magic, 0)
    if magic == MAGIC_SIGNED:
        return TocInfo(magic, SIGNED_HEADER)
    if magic == MAGIC_OBFUSCATED:
        raise UnsupportedFrostbite(
            f"{name} is XOR-obfuscated. That form is not implemented, because no "
            "file here uses it and guessing at a layout with nothing to check it "
            "against is worse than declining."
        )
    raise UnsupportedFrostbite(
        f"{name} has magic 0x{magic:08X}, which is not a Frostbite table of contents"
    )


def _read_value(cursor: _Cursor, type_id: int):
    """One value, given its type. Containers recurse; everything else is flat."""
    if type_id in (T_OBJECT, T_LIST):
        length = cursor.varint()
        end = cursor.at + length
        contents = _read_fields(cursor, end)
        if cursor.at != end:
            raise UnsupportedFrostbite(
                f"container declared {length} bytes but the reader consumed "
                f"{length + cursor.at - end}; a field type is being misread"
            )
        return contents
    if type_id == T_STRING:
        length = cursor.varint()
        return cursor.take(length).split(b"\x00")[0].decode("utf-8", "replace")
    if type_id == T_BLOB:
        return cursor.take(cursor.varint())
    width = _FIXED.get(type_id)
    if width is None:
        raise UnsupportedFrostbite(f"field type 0x{type_id:02X} is not known")
    raw = cursor.take(width)
    if type_id == T_BOOL:
        return bool(raw[0])
    if type_id in (T_INT, T_LONG):
        return int.from_bytes(raw, "little", signed=True)
    if type_id == T_FLOAT:
        return struct.unpack("<f", raw)[0]
    if type_id == T_DOUBLE:
        return struct.unpack("<d", raw)[0]
    return raw


def _read_fields(cursor: _Cursor, end: int):
    """
    The fields of one container, until its terminating zero byte.

    A named container yields a dict and an anonymous one a list, which is how
    Frostbite distinguishes an object's members from a list's elements.
    """
    named: dict[str, object] = {}
    anonymous: list[object] = []
    while cursor.at < end:
        type_byte = cursor.u8()
        if type_byte == T_EOF:
            break
        type_id = type_byte & 0x1F
        if type_byte & 0x80:
            anonymous.append(_read_value(cursor, type_id))
        else:
            name = cursor.cstring()
            named[name] = _read_value(cursor, type_id)
    if named and anonymous:
        named["_items"] = anonymous
        return named
    return named if named or not anonymous else anonymous


def parse_toc(path: str | Path) -> tuple[TocInfo, object]:
    """
    Parse a `.toc` into plain Python containers.

    Returns the header and the tree. Every container's declared length is checked
    against what was actually consumed, so a file that parses is a file that was
    understood — not one that merely did not crash.
    """
    path = Path(path)
    data = path.read_bytes()
    info = read_header(data, path.name)
    cursor = _Cursor(data, info.payload_offset)

    type_byte = cursor.u8()
    if type_byte & 0x1F != T_OBJECT:
        raise UnsupportedFrostbite(
            f"{path.name}: the tree starts with type 0x{type_byte:02X}, not an object"
        )
    tree = _read_value(cursor, T_OBJECT)
    return info, tree


# ---------------------------------------------------------------------------
# The binary table, which is what current Battlefield actually ships.


#: A superbundle toc whose tree is a binary section table rather than a DbObject
#: opens with this as the first big-endian word: the length of its own header.
BINARY_HEADER = 60

#: Records in the asset table: a 16-byte identifier and one 32-bit word.
ASSET_RECORD = 20


@dataclass(frozen=True)
class Sections:
    """
    Where each section of a binary toc begins, and how big it is.

    Offsets are relative to the end of the signed header, so add
    `TocInfo.payload_offset` to reach a file position.
    """

    #: The bundles: a hash table of one word per bundle, then a 16-byte record
    #: per bundle (`frostbitebundle.toc_bundles` reads them) — 20 bytes each.
    lookup: tuple[int, int]
    #: One 32-bit word per asset: the hash table over the identifiers.
    asset_index: tuple[int, int]
    #: The chunks themselves: a 16-byte identifier, then a word giving the
    #: index of its location record (see `chunk_locations`).
    assets: tuple[int, int]
    #: Four words per asset — where its bytes live in the cas blobs.
    locations: tuple[int, int]
    #: A trailing word table.
    extra: tuple[int, int]
    asset_count: int

    @property
    def end(self) -> int:
        return self.extra[0] + self.extra[1]


def read_sections(data: bytes, info: TocInfo, name: str = "toc") -> Sections:
    """
    Parse the section table of a binary toc.

    The header is fifteen big-endian words, and the sections are laid end to end
    in a fixed chain — each one's start is the previous one's start plus its
    length, with the lengths derived from two counts. That redundancy is what
    makes this checkable without documentation: the arithmetic either closes on
    the declared offsets or it does not, and a wrong record size will not close.
    It closes on all 136 tables shipped with Battlefield 6.

    This only finds the sections. `chunk_locations` pairs the chunks with their
    locations, and `frostbitebundle.toc_bundles` reads the bundles stored after
    the table.
    """
    at = info.payload_offset
    if len(data) < at + BINARY_HEADER:
        raise UnsupportedFrostbite(f"{name} is too short to hold a section table")
    fields = struct.unpack_from(">15I", data, at)

    if fields[0] != BINARY_HEADER:
        raise UnsupportedFrostbite(
            f"{name} declares a {fields[0]}-byte header, not {BINARY_HEADER}; it is "
            "probably the DbObject form — use parse_toc()"
        )

    lookup_count = fields[2]
    asset_count = fields[5]

    lookup = (fields[0], ASSET_RECORD * lookup_count)
    asset_index = (fields[3], 4 * asset_count)
    assets = (fields[4], ASSET_RECORD * asset_count)
    locations = (fields[6], 16 * asset_count)
    extra = (fields[8], 4 * fields[12])

    expected = {
        "asset index start": (fields[3], _align(fields[0] + ASSET_RECORD * lookup_count)),
        "asset start": (fields[4], fields[3] + 4 * asset_count),
        "location start": (fields[6], fields[4] + ASSET_RECORD * asset_count),
        "extra start": (fields[8], fields[6] + 16 * asset_count),
        "table end": (fields[14], fields[8] + 4 * fields[12]),
    }
    for label, (declared, derived) in expected.items():
        if declared != derived:
            raise UnsupportedFrostbite(
                f"{name}: {label} is {declared} but the section chain puts it at "
                f"{derived}; this table is not laid out as expected"
            )
    if at + fields[14] > len(data):
        raise UnsupportedFrostbite(
            f"{name}: the table claims to end at {at + fields[14]} of {len(data)} bytes"
        )

    return Sections(
        lookup=lookup,
        asset_index=asset_index,
        assets=assets,
        locations=locations,
        extra=extra,
        asset_count=asset_count,
    )


def _align(value: int, to: int = 8) -> int:
    return -(-value // to) * to


def asset_ids(data: bytes, info: TocInfo, sections: Sections) -> list[bytes]:
    """
    The 16-byte identifier of every asset the table lists, as stored.

    Stored byte-reversed: the GUID a mesh or a bundle manifest names its chunk by
    is these sixteen bytes back to front. `chunk_locations` turns them round.
    """
    start = info.payload_offset + sections.assets[0]
    return [
        data[start + i * ASSET_RECORD : start + i * ASSET_RECORD + 16]
        for i in range(sections.asset_count)
    ]


def chunk_locations(data: bytes, info: TocInfo, sections: Sections) -> dict[bytes, "Location"]:
    """
    Where each chunk's bytes are, by the GUID the rest of the game uses for it.

    The identifiers and the locations are two tables in different orders. The
    word after each identifier joins them: its top bit is set, and the rest is
    four times the index of the identifier's location record. Reading them in
    file order instead pairs every chunk with somebody else's bytes — which
    decode perfectly well, mostly as sound, and so do not look wrong until a
    mesh comes out as noise. In a level of 73,875 chunks the words are all
    distinct and run 0, 4, ... 4 × 73,874: a permutation, which is what an
    index is and a coincidence is not.
    """
    start = info.payload_offset + sections.assets[0]
    table = info.payload_offset + sections.locations[0]
    out: dict[bytes, Location] = {}
    for i in range(sections.asset_count):
        at = start + i * ASSET_RECORD
        (word,) = struct.unpack_from(">I", data, at + 16)
        index = (word & 0x00FFFFFF) >> 2
        if index >= sections.asset_count:
            raise UnsupportedFrostbite(
                f"chunk {i} points at location {index} of {sections.asset_count}"
            )
        out[data[at : at + 16][::-1]] = location_at(data, table + index * 16)
    return out


@dataclass(frozen=True)
class Location:
    """Where one asset's bytes sit in the `.cas` blobs."""

    #: Which `cas_NN.cas`, as the files are numbered.
    cas: int
    offset: int
    size: int
    #: The installation package the blob belongs to: the `persistentIndex` of
    #: one of the install chunks `layout.toc` lists, which also names the folder
    #: the package is installed in. `install_packages` resolves it.
    package: int

    @property
    def end(self) -> int:
        return self.offset + self.size


def locations(data: bytes, info: TocInfo, sections: Sections) -> list[Location]:
    """
    Where every asset's bytes are, in the order of the location table.

    That is not the order of `asset_ids`; `chunk_locations` pairs the two.

    Four big-endian words per asset. The layout was not documented anywhere; it
    was read off the numbers and then checked against the files themselves —
    every one of the 74,175 records in a Battlefield 6 level table lands inside
    an installed `.cas` blob, with no record running past the end of its file and
    no record naming a blob that is not there. A wrong field order does not
    produce that.

    The package is split across the first two words: the low half of the first
    holds the high half of the package's `persistentIndex`, the high half of the
    second its low half, and the low half of the second is the blob number::

        00 00 14 FB   60 ED 00 03   ...
              ^^^^^   ^^^^^ ^^^^^
              package 0x14FB60ED, cas_03

    The top half of the first word is zero in every record shipped.
    """
    start = info.payload_offset + sections.locations[0]
    out = []
    for i in range(sections.asset_count):
        out.append(location_at(data, start + i * 16))
    return out


def location_at(data: bytes, at: int) -> Location:
    """One sixteen-byte location record; see `locations` for the layout."""
    first, second, offset, size = struct.unpack_from(">4I", data, at)
    return Location(
        cas=second & 0xFFFF,
        offset=offset,
        size=size,
        package=((first & 0xFFFF) << 16) | (second >> 16),
    )


#: Frostbite payloads are a chain of blocks, each with an eight-byte header::
#:
#:     [decompressed size : 4]  [method : 2]  [compressed size : 2]
#:
#: all big-endian. Verified against a shipped level: a record of 855 bytes holds
#: one block declaring 847 compressed, and 847 + 8 is 855; one of 27,728 holds a
#: stored block of 27,720. The arithmetic closing on every block of a payload is
#: what makes this readable without documentation.
BLOCK_HEADER = 8

#: Compression methods, by the header's method word.
BLOCK_METHODS = {
    0x0070: "none",
    0x0270: "zlib",
    0x0970: "lz4",
    0x0F70: "zstd",
    0x1170: "oodle",
    0x1570: "oodle",
}


@dataclass(frozen=True)
class Block:
    """One compressed block within a payload."""

    decompressed: int
    method: int
    compressed: int
    #: Offset of the block's data, from the start of the payload.
    at: int

    @property
    def method_name(self) -> str:
        return BLOCK_METHODS.get(self.method, f"unknown(0x{self.method:04X})")


def split_blocks(payload: bytes) -> list[Block]:
    """
    Walk a payload's block chain, or raise if it does not walk.

    A stored block's header repeats its size in both fields, which is the cheap
    check that the chain is being read at the right offsets; a chain that reaches
    the end of the payload exactly is the stronger one.
    """
    blocks: list[Block] = []
    at = 0
    while at + BLOCK_HEADER <= len(payload):
        decompressed, method, compressed = struct.unpack_from(">IHH", payload, at)
        at += BLOCK_HEADER
        # A zero in the compressed field means the block is stored and is as long
        # as it decompresses to. Reading it as a zero-length block instead
        # rejects the payload outright: honouring it took the share of a level's
        # payloads that parse as a clean chain from 159 of 299 to 218.
        if compressed == 0:
            compressed = decompressed
        if compressed == 0 or at + compressed > len(payload):
            raise UnsupportedFrostbite(
                f"block at {at - BLOCK_HEADER} declares {compressed} bytes, which "
                f"does not fit the remaining {len(payload) - at}"
            )
        blocks.append(Block(decompressed, method, compressed, at))
        at += compressed
    if at != len(payload):
        raise UnsupportedFrostbite(
            f"the block chain ended at {at} of {len(payload)} bytes; this payload "
            "is not a chain of blocks, or is encrypted"
        )
    return blocks


def decompress_payload(payload: bytes) -> bytes:
    """Every block of a payload, decompressed and joined."""
    out = bytearray()
    for block in split_blocks(payload):
        raw = payload[block.at : block.at + block.compressed]
        name = block.method_name
        if name == "none":
            out += raw[: block.decompressed]
        elif block.compressed == block.decompressed:
            # Stored under a method code this table does not name. The lengths
            # agreeing is the evidence: nothing compressed comes out exactly its
            # own size, so copying is right and guessing a codec would not be.
            out += raw[: block.decompressed]
        elif name == "zlib":
            import zlib

            out += zlib.decompress(raw)
        elif name == "zstd":
            try:
                import zstandard
            except ImportError as exc:
                raise UnsupportedFrostbite(
                    "this payload is Zstandard-compressed, which needs the "
                    "`zstandard` package"
                ) from exc
            out += zstandard.ZstdDecompressor().decompress(
                raw, max_output_size=block.decompressed
            )
        elif name == "lz4":
            try:
                import lz4.block
            except ImportError as exc:
                raise UnsupportedFrostbite(
                    "this payload is LZ4-compressed, which needs the `lz4` package"
                ) from exc
            out += lz4.block.decompress(raw, uncompressed_size=block.decompressed)
        elif name == "oodle":
            from .oodle import decompress_oodle

            out += decompress_oodle(raw, block.decompressed)
        else:
            raise UnsupportedFrostbite(f"block compression {name} is not supported")
    return bytes(out)


def game_root(path: str | Path) -> Path:
    """
    The installation folder: the one whose `Data` holds `layout.toc`.

    Accepts the folder itself, its `Data`, or anything inside it — a level's
    table, typically — so a caller holding any one file can find the rest.
    """
    path = Path(path).resolve()
    for folder in [path, *path.parents]:
        if (folder / "Data" / "layout.toc").is_file():
            return folder
        if folder.name.lower() == "data" and (folder / "layout.toc").is_file():
            return folder.parent
    raise UnsupportedFrostbite(f"no Data\\layout.toc at or above {path}")


#: Package maps already read, by installation folder. `layout.toc` is 200 KB
#: and a level export resolves tens of thousands of locations against it.
_PACKAGES: dict[str, dict[int, list[Path]]] = {}


def install_packages(root: str | Path) -> dict[int, list[Path]]:
    """
    Every installation package `layout.toc` declares, by `persistentIndex`, with
    the folders it is installed in.

    `layout.toc` lists the install chunks under `installManifest.installChunks`,
    each with a `persistentIndex` — the number a location record carries — and
    an `installBundle` such as `Win32/installation/commonbase`, which is the
    folder its `cas_NN.cas` blobs sit in. That folder is under `Data` for the
    base game and under `Update/<pack>/Data` for what came later, so both are
    searched; a package may be split across several.

    A package with no folder on disk is still listed, with no folders: it is
    declared but not installed, which is worth saying differently from a number
    nobody declared.
    """
    root = game_root(root)
    key = str(root).lower()
    if key in _PACKAGES:
        return _PACKAGES[key]

    _, tree = parse_toc(root / "Data" / "layout.toc")
    manifest = tree.get("installManifest", {}) if isinstance(tree, dict) else {}
    chunks = manifest.get("installChunks", []) if isinstance(manifest, dict) else []
    bases = [root / "Data"]
    if (root / "Update").is_dir():
        bases += sorted(p / "Data" for p in (root / "Update").iterdir() if (p / "Data").is_dir())

    found: dict[int, list[Path]] = {}
    for chunk in chunks:
        if not isinstance(chunk, dict) or "persistentIndex" not in chunk:
            continue
        bundle = str(chunk.get("installBundle", "") or "")
        folders = [base / bundle for base in bases if bundle and (base / bundle).is_dir()]
        found[int(chunk["persistentIndex"]) & 0xFFFFFFFF] = folders
    _PACKAGES[key] = found
    return found


def cas_path(root: str | Path, location: Location) -> Path:
    """The `cas_NN.cas` a location points into, or why there is none."""
    packages = install_packages(root)
    if location.package not in packages:
        raise UnsupportedFrostbite(
            f"package 0x{location.package:08X} is not declared in layout.toc"
        )
    name = f"cas_{location.cas:02d}.cas"
    for folder in packages[location.package]:
        if (folder / name).is_file():
            return folder / name
    raise UnsupportedFrostbite(
        f"package 0x{location.package:08X} has no {name} installed"
    )


def read_asset(root: str | Path, location: Location) -> bytes:
    """
    The raw bytes of one asset, from the installation package that holds them.

    Raw: Frostbite stores content in compressed blocks, and unpacking those is a
    separate matter from finding them — `decompress_payload` does that.

    The package matters. Every package numbers its blobs from `cas_01`, so a
    blob number alone names one file per package; taking the first match reads
    the right offsets out of the wrong file, which is what an earlier version
    did, and the bytes that came back looked encrypted.
    """
    path = cas_path(root, location)
    with open(path, "rb") as handle:
        handle.seek(location.offset)
        data = handle.read(location.size)
    if len(data) != location.size:
        raise UnsupportedFrostbite(
            f"{path.name} ends before bytes {location.offset}–{location.end}"
        )
    return data


def describe(path: str | Path) -> str:
    """One paragraph saying what a toc holds, whichever form it is in."""
    path = Path(path)
    data = path.read_bytes()
    info = read_header(data, path.name)

    try:
        sections = read_sections(data, info, path.name)
    except UnsupportedFrostbite:
        _, tree = parse_toc(path)
        names = superbundles(tree)
        return (
            f"{path.name}: {info.kind} DbObject tree, "
            f"{len(names)} superbundles"
        )
    return (
        f"{path.name}: {info.kind} binary table, {sections.asset_count:,} assets, "
        f"table ends at {sections.end:,}"
    )


@dataclass(frozen=True)
class CasReference:
    """Where one piece of content actually lives."""

    #: Which `cas_NN.cas` blob, 1-based as the files are named.
    cas: int
    offset: int
    size: int
    #: The installation package the blob belongs to, when the toc names one.
    installation: str = ""


def cas_references(tree: object) -> list[CasReference]:
    """
    Every (cas, offset, size) triple in a parsed toc.

    Frostbite spells these the same way wherever they appear, so walking the tree
    for the trio is more robust across game versions than following one expected
    path down to them.
    """
    found: list[CasReference] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if {"cas", "offset", "size"} <= node.keys():
                found.append(
                    CasReference(
                        cas=int(node["cas"]),
                        offset=int(node["offset"]),
                        size=int(node["size"]),
                        installation=str(node.get("installationPackage", "")),
                    )
                )
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(tree)
    return found


def superbundles(tree: object) -> list[str]:
    """The superbundle names a toc declares, for reporting what a game holds."""
    if not isinstance(tree, dict):
        return []
    out = []
    for entry in tree.get("superBundles", []) or []:
        if isinstance(entry, dict) and "name" in entry:
            out.append(str(entry["name"]))
    return out
