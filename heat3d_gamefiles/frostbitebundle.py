"""
What a Frostbite level's bundles hold, by name.

`frostbite` reads a level's table of contents down to chunk locations. Those are
anonymous: sixteen-byte identifiers and where their bytes are. The names — which
asset is a mesh, which a texture, which the level's own layout — live one step
further in, in the level's bundles, and this module reads them.

Where the bundles are
---------------------
Current Battlefield keeps them inside the level's `.toc`, after the section
table. Header word 1 is where the bundle records start and word 2 how many there
are; each record is four big-endian words::

    [key] [0x40000000 | size] [0] [offset from the end of the signature]

The flag in the second word says the bundle is inline, which is all this reader
has met; a bundle without it is refused rather than looked for elsewhere.

Each inline bundle is a short list of locations. Nine big-endian words of header
— word 2 is where a flag byte per entry starts, word 3 how many entries there
are, word 4 where they start — then the entries: eight bytes of offset and size,
preceded by eight more naming the package and blob whenever the entry's flag has
its top bit set. Entries without it continue in the blob the last one named. The
arithmetic closes on every bundle of a level: the last entry ends exactly where
the flag bytes begin.

The manifest
------------
The first entry is the bundle's manifest, stored uncompressed. It is the binary
bundle format Frostbite has used since Battlefield 4, under a newer magic::

    [size : 4 BE] [magic 0xD68E799D : 4 BE]
    total, ebx count, res count, chunk count, strings offset,
    meta offset, meta size                          seven LE words
    SHA-1 x total
    ebx    (name offset, size) x ebx count
    res    (name offset, size) x res count
           type x res count, meta (16 bytes) x res count, id (8) x res count
    chunks (GUID, logical offset, logical size) x chunk count
    strings, then a DbObject of chunk metadata

Offsets count from the magic. The strings offset is stated and also follows from
the counts, so a wrong record size is caught on the first bundle. The remaining
entries of the bundle are then the ebx, the res and the chunks, in that order —
which is the check that the manifest was read right: the count matches on every
bundle of every level.

Resource types are hashes. The ones this package uses were matched to their
names in the manifests — every resource of type 0x49B156D4 is called `..._mesh`,
every one of 0x22FE8AC8 `....streamingtree_win32` — and agree with the values
the Frosty modding tools publish for older Frostbite games.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

from .frostbite import (
    Location,
    UnsupportedFrostbite,
    chunk_locations,
    decompress_payload,
    game_root,
    read_asset,
    read_header,
    read_sections,
)

#: The second word of a bundle record carries this when the bundle is inline.
BUNDLE_INLINE = 0x40000000

#: A binary bundle manifest's magic, big-endian, after its size.
MANIFEST_MAGIC = 0xD68E799D

#: Resource types by hash, for the ones this package reads or reports.
RES_TYPES = {
    0x49B156D4: "MeshSet",
    0x6BDE20BA: "Texture",
    0x22FE8AC8: "TerrainStreamingTree",
    0x1CA38E06: "VisualTerrain",
    0x15E1F32E: "TerrainDecals",
    0x70C5CB3E: "EnlightenDatabase",
}


@dataclass(frozen=True)
class Entry:
    """One named ebx or res in a bundle."""

    name: str
    #: "ebx" or "res".
    kind: str
    #: The size the manifest declares: decompressed, for both kinds.
    size: int
    location: Location
    #: A res only: its type hash (see `RES_TYPES`), 16 bytes of type-specific
    #: metadata, and its 64-bit resource id.
    res_type: int = 0
    meta: bytes = b""
    rid: int = 0

    @property
    def type_name(self) -> str:
        return RES_TYPES.get(self.res_type, f"0x{self.res_type:08X}")


@dataclass(frozen=True)
class ChunkRef:
    """A chunk a bundle names, with where its bytes are."""

    id: bytes
    logical_offset: int
    logical_size: int
    location: Location


@dataclass
class Manifest:
    ebx: list[Entry] = field(default_factory=list)
    res: list[Entry] = field(default_factory=list)
    chunks: list[ChunkRef] = field(default_factory=list)


def toc_bundles(data: bytes, name: str = "toc") -> list[list[Location]]:
    """
    Every bundle a binary toc carries inline, as its list of entry locations.

    The first location of each is the bundle's manifest; `read_manifest` says
    what the rest are.
    """
    info = read_header(data, name)
    base = info.payload_offset
    read_sections(data, info, name)  # raises unless it is the binary form
    table, count = struct.unpack_from(">2I", data, base + 4)

    bundles: list[list[Location]] = []
    for i in range(count):
        _key, sized, _zero, offset = struct.unpack_from(">4I", data, base + table + 16 * i)
        if not sized & BUNDLE_INLINE:
            raise UnsupportedFrostbite(
                f"{name}: bundle {i} is not stored inline, and nothing else has been seen"
            )
        size = sized & ~BUNDLE_INLINE
        start = base + offset
        if start + size > len(data):
            raise UnsupportedFrostbite(f"{name}: bundle {i} runs past the end of the file")
        bundles.append(_bundle_entries(data[start : start + size], f"{name} bundle {i}"))
    return bundles


def _bundle_entries(blob: bytes, name: str) -> list[Location]:
    words = struct.unpack_from(">9I", blob, 0)
    flags_at, count, at = words[2], words[3], words[4]
    if flags_at + count > len(blob):
        raise UnsupportedFrostbite(f"{name}: its flag bytes run past its end")
    flags = blob[flags_at : flags_at + count]
    out: list[Location] = []
    package = cas = None
    for flag in flags:
        if flag & 0x80:
            first, second = struct.unpack_from(">2I", blob, at)
            package = ((first & 0xFFFF) << 16) | (second >> 16)
            cas = second & 0xFFFF
            at += 8
        if package is None:
            raise UnsupportedFrostbite(f"{name}: an entry continues a blob nobody named")
        offset, size = struct.unpack_from(">2I", blob, at)
        at += 8
        out.append(Location(cas=cas, offset=offset, size=size, package=package))
    if at != flags_at:
        raise UnsupportedFrostbite(
            f"{name}: the entries end at {at} but the flags start at {flags_at}"
        )
    return out


def _cstring(data: bytes, at: int) -> str:
    end = data.find(b"\x00", at)
    if end < 0:
        raise UnsupportedFrostbite("a manifest name is not terminated")
    return data[at:end].decode("utf-8", "replace")


def read_manifest(raw: bytes, entries: list[Location], name: str = "bundle") -> Manifest:
    """
    A bundle's manifest, with each ebx, res and chunk paired with its location.

    `entries` are the bundle's locations after the manifest's own.
    """
    if len(raw) < 36:
        raise UnsupportedFrostbite(f"{name}: too short for a manifest")
    size, magic = struct.unpack_from(">2I", raw, 0)
    if magic != MANIFEST_MAGIC:
        raise UnsupportedFrostbite(f"{name}: manifest magic 0x{magic:08X} is not known")
    if size + 4 > len(raw):
        raise UnsupportedFrostbite(f"{name}: manifest declares {size} bytes of {len(raw) - 4}")
    total, n_ebx, n_res, n_chunks, strings, _meta_at, _meta_size = struct.unpack_from(
        "<7I", raw, 8
    )
    if total != n_ebx + n_res + n_chunks:
        raise UnsupportedFrostbite(f"{name}: {total} entries is not {n_ebx}+{n_res}+{n_chunks}")
    if len(entries) != total:
        raise UnsupportedFrostbite(
            f"{name}: the manifest lists {total} entries and the bundle holds {len(entries)}"
        )

    at = 36 + 20 * total  # past the SHA-1s
    ebx = [struct.unpack_from("<2I", raw, at + 8 * i) for i in range(n_ebx)]
    at += 8 * n_ebx
    res = [struct.unpack_from("<2I", raw, at + 8 * i) for i in range(n_res)]
    at += 8 * n_res
    types = struct.unpack_from(f"<{n_res}I", raw, at)
    at += 4 * n_res
    metas = [raw[at + 16 * i : at + 16 * i + 16] for i in range(n_res)]
    at += 16 * n_res
    rids = struct.unpack_from(f"<{n_res}Q", raw, at)
    at += 8 * n_res
    chunks = [
        (raw[at + 24 * i : at + 24 * i + 16],) + struct.unpack_from("<2I", raw, at + 24 * i + 16)
        for i in range(n_chunks)
    ]
    at += 24 * n_chunks
    if at != 4 + strings:
        raise UnsupportedFrostbite(
            f"{name}: the records end at {at} but the strings start at {4 + strings}"
        )

    text = 4 + strings
    out = Manifest()
    for (offset, length), where in zip(ebx, entries[:n_ebx]):
        out.ebx.append(Entry(_cstring(raw, text + offset), "ebx", length, where))
    for (offset, length), kind, meta, rid, where in zip(
        res, types, metas, rids, entries[n_ebx : n_ebx + n_res]
    ):
        out.res.append(
            Entry(_cstring(raw, text + offset), "res", length, where, kind, meta, rid)
        )
    for (guid, logical_offset, logical_size), where in zip(chunks, entries[n_ebx + n_res :]):
        out.chunks.append(ChunkRef(guid, logical_offset, logical_size, where))
    return out


class LevelCatalogue:
    """
    Everything one level's table names: ebx and res by name, chunks by GUID.

    A name can appear in several bundles of a level — shared props are listed in
    each bundle that uses them — and the first one seen is kept; they point at
    the same bytes.
    """

    def __init__(self, toc: str | Path, supplements=()):
        self.toc = Path(toc)
        self.root = game_root(self.toc)
        data = self.toc.read_bytes()
        info = read_header(data, self.toc.name)
        self.chunks: dict[bytes, Location] = chunk_locations(
            data, info, read_sections(data, info, self.toc.name)
        )
        # High-resolution packs ship further chunks of the level — a texture's
        # largest mips — in tables of their own.
        for extra in supplements:
            more = Path(extra).read_bytes()
            extra_info = read_header(more, Path(extra).name)
            for guid, where in chunk_locations(
                more, extra_info, read_sections(more, extra_info, Path(extra).name)
            ).items():
                self.chunks.setdefault(guid, where)
        self.ebx: dict[str, Entry] = {}
        self.res: dict[str, Entry] = {}
        self.bundle_count = 0
        for i, locations in enumerate(toc_bundles(data, self.toc.name)):
            raw = read_asset(self.root, locations[0])
            manifest = read_manifest(raw, locations[1:], f"{self.toc.name} bundle {i}")
            self.bundle_count += 1
            for entry in manifest.ebx:
                self.ebx.setdefault(entry.name, entry)
            for entry in manifest.res:
                self.res.setdefault(entry.name, entry)
            for chunk in manifest.chunks:
                self.chunks.setdefault(chunk.id, chunk.location)

    def read(self, location: Location) -> bytes:
        """One entry's bytes, decompressed."""
        return decompress_payload(read_asset(self.root, location))

    def chunk(self, guid: bytes) -> bytes:
        if guid not in self.chunks:
            raise UnsupportedFrostbite(f"chunk {guid.hex()} is not in {self.toc.name}")
        return self.read(self.chunks[guid])

    def of_type(self, res_type: int) -> list[Entry]:
        return [e for e in self.res.values() if e.res_type == res_type]


@dataclass(frozen=True)
class LevelTable:
    """Where one level's tables are, across the installation's layers."""

    name: str
    #: The table with the level's bundles.
    toc: Path
    #: `Data`, or `Update/<pack>`: which layer that table comes from.
    source: str
    #: Tables of the same level that carry chunks and no bundles: the
    #: high-resolution packs' extra texture and mesh data.
    supplements: tuple[Path, ...] = ()


def _layer(root: Path, toc: Path) -> str:
    parts = toc.relative_to(root).parts
    return "Data" if parts[0] == "Data" else f"{parts[0]}/{parts[1]}"


def _bundle_count(toc: Path) -> int:
    try:
        data = toc.read_bytes()
        info = read_header(data, toc.name)
        read_sections(data, info, toc.name)
        return struct.unpack_from(">I", data, info.payload_offset + 8)[0]
    except (UnsupportedFrostbite, OSError, struct.error):
        return -1


def level_sources(root: str | Path) -> dict[str, LevelTable]:
    """
    Every level the installation ships, by the name its table carries, with
    the layer it comes from.

    A level's table sits in a folder of its own name under `levels`
    (`levels/<level>/<level>.toc`), in the base game's `Data` or in an
    update's `Update/<pack>/Data`, and a level can have several: the update
    that ships it, and high-resolution packs that add a table of chunks only.
    The one with the level's bundles — the most of them, a later layer winning
    a tie — is the level; tables without bundles are its supplements. Taking
    the first found instead picks, for a level an update ships, a 64 KB table
    of high-resolution chunks with no content of its own.
    """
    root = game_root(root)
    bases = [root / "Data"]
    if (root / "Update").is_dir():
        bases += sorted(p / "Data" for p in (root / "Update").iterdir() if (p / "Data").is_dir())
    candidates: dict[str, list[tuple[int, int, Path]]] = {}
    for layer, base in enumerate(bases):
        for toc in sorted(base.glob("**/levels/**/*.toc")):
            if toc.parent.name.lower() == toc.stem.lower():
                candidates.setdefault(toc.stem.lower(), []).append((_bundle_count(toc), layer, toc))
    found: dict[str, LevelTable] = {}
    for name, items in candidates.items():
        bundles, _layer_index, toc = max(items, key=lambda item: (item[0], item[1]))
        if bundles <= 0:
            continue
        extra = tuple(p for b, _l, p in items if b == 0)
        found[name] = LevelTable(name, toc, _layer(root, toc), extra)
    return found


def level_tables(root: str | Path) -> dict[str, Path]:
    """Every level's main table, by name; see `level_sources`."""
    return {name: table.toc for name, table in level_sources(root).items()}
