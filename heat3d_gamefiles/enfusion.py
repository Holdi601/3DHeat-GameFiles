"""
Enfusion (Arma Reforger) archives: `.pak` files, the file system they make
together, and `.edds` textures.

A `.pak` is an IFF-style form, big-endian chunk sizes: `FORM` <size> `PAC1`,
then `HEAD` (28 bytes), `DATA` (every file's bytes, back to back) and `FILE`,
the directory as a tree. A tree node is a byte saying directory (0) or file
(1), a byte of name length and the name; a directory then has a 32-bit count
of children, a file 24 bytes: offset from the start of the archive, stored
size, original size, eight bytes of zero, a compression byte (0 stored, 1
zlib), the zlib level, and a timestamp. Little-endian, unlike the chunk
headers. Nothing is encrypted.

Checked on the installed game: the tree consumes every `FILE` chunk exactly
(18 archives, 218,728 files), every stored size ends inside `DATA`, and every
zlib entry sampled inflates to exactly its original size.

An addon is a folder of archives; the game mounts its addons into one file
system, a later addon's file replacing an earlier one's of the same path.

An `.edds` is a DDS header (with the DX10 extension where the format needs
it), then one 8-byte record per mip level - `COPY` or `LZ4 ` and a size -
smallest level first, then the levels' bytes in the same order. `COPY` levels
are the block data as DDS would hold it. An `LZ4 ` level is its original
size (32 bits), then chunks, each a 32-bit header - the compressed size, the
top bit set on the last chunk - and a plain LZ4 block that may refer back into
the 64 KB decoded before it. Checked: every LZ4 level of a world's terrain
textures decodes to exactly its original size and uses exactly its bytes.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

STEAM_FOLDER = "Arma Reforger"


class EnfusionError(Exception):
    """An archive or file this cannot read, and why."""


@dataclass(frozen=True)
class Entry:
    archive: Path
    offset: int
    stored: int
    size: int
    method: int


def _chunks(handle, start: int, end: int):
    at = start
    while at + 8 <= end:
        handle.seek(at)
        tag, length = struct.unpack(">4sI", handle.read(8))
        yield tag, at + 8, length
        at += 8 + length  # no pad byte after an odd length, unlike IFF


def read_directory(path: str | Path) -> dict[str, Entry]:
    """Every file in one `.pak`, by its path inside it."""
    path = Path(path)
    with open(path, "rb") as handle:
        head = handle.read(12)
        if len(head) < 12 or head[:4] != b"FORM" or head[8:12] != b"PAC1":
            raise EnfusionError(f"{path.name}: not an Enfusion pak (FORM/PAC1)")
        size = path.stat().st_size
        blob = data_end = None
        for tag, at, length in _chunks(handle, 12, size):
            if tag == b"DATA":
                data_end = at + length
            elif tag == b"FILE":
                handle.seek(at)
                blob = handle.read(length)
        if blob is None:
            raise EnfusionError(f"{path.name}: no FILE chunk")
    return parse_tree(blob, path, data_end if data_end is not None else size)


def parse_tree(blob: bytes, archive: Path, data_end: int) -> dict[str, Entry]:
    out: dict[str, Entry] = {}
    at = 0

    def node(prefix: str) -> None:
        nonlocal at
        kind, length = blob[at], blob[at + 1]
        name = blob[at + 2 : at + 2 + length].decode("utf-8")
        at += 2 + length
        if kind == 0:
            (count,) = struct.unpack_from("<I", blob, at)
            at += 4
            for _ in range(count):
                node(f"{prefix}{name}/" if name else prefix)
        elif kind == 1:
            offset, stored, original, _zero, _zero2, method, _level, _time = struct.unpack_from("<IIIIHBBI", blob, at)
            at += 24
            if offset + stored > data_end or method > 1:
                raise EnfusionError(f"{archive.name}: {prefix}{name} does not fit the archive")
            out[f"{prefix}{name}"] = Entry(archive, offset, stored, original, method)
        else:
            raise EnfusionError(f"{archive.name}: directory node of kind {kind}")

    try:
        node("")
    except (IndexError, struct.error) as exc:
        raise EnfusionError(f"{archive.name}: the directory runs short") from exc
    if at != len(blob):
        raise EnfusionError(f"{archive.name}: {len(blob) - at} bytes after the directory")
    return out


def read_entry(entry: Entry) -> bytes:
    with open(entry.archive, "rb") as handle:
        handle.seek(entry.offset)
        raw = handle.read(entry.stored)
    data = zlib.decompress(raw) if entry.method == 1 else raw
    if len(data) != entry.size:
        raise EnfusionError(f"{entry.archive.name}: an entry inflates to {len(data)} bytes, not {entry.size}")
    return data


class FileSystem:
    """The game's addons mounted as one tree; paths are case-insensitive, as the engine's are."""

    def __init__(self, addons: list[Path]) -> None:
        self.files: dict[str, Entry] = {}
        self.names: dict[str, str] = {}
        for folder in addons:
            for pak in sorted(Path(folder).glob("*.pak")):
                for name, entry in read_directory(pak).items():
                    self.files[name.lower()] = entry
                    self.names[name.lower()] = name
        if not self.files:
            raise EnfusionError("no readable .pak archives in " + ", ".join(str(a) for a in addons))

    @classmethod
    def of_install(cls, install: Path) -> "FileSystem":
        addons = install / "addons"
        if not addons.is_dir():
            raise EnfusionError(f"{install}: no addons folder")
        # The engine's own `core` first, then the game data, then the rest.
        folders = sorted((p for p in addons.iterdir() if p.is_dir()), key=lambda p: ({"core": 0, "data": 1}.get(p.name.lower(), 2), p.name.lower()))
        return cls(folders)

    def __contains__(self, path: str) -> bool:
        return path.lower() in self.files

    def read(self, path: str) -> bytes:
        entry = self.files.get(path.lower())
        if entry is None:
            raise FileNotFoundError(path)
        return read_entry(entry)

    def find(self, contains: str, suffix: str = "") -> list[str]:
        contains, suffix = contains.lower(), suffix.lower()
        return sorted(self.names[p] for p in self.files if contains in p and p.endswith(suffix))


def find_install(where: str | Path | None = None) -> Path | None:
    """The game's folder: given, or in any Steam library."""
    candidates = [Path(where)] if where else []
    if not where:
        from .forzainstall import STEAM_DEFAULTS, steam_libraries

        for library in [Path(p) for p in STEAM_DEFAULTS] + [Path(p) for p in steam_libraries()]:
            candidates.append(library / "steamapps" / "common" / STEAM_FOLDER)
    for folder in candidates:
        if (folder / "addons").is_dir():
            return folder
    return None


# --------------------------------------------------------------------------
# .edds


def unlz4(data: bytes) -> bytes:
    """An `LZ4 ` mip level: chunked LZ4 blocks, each able to refer to the 64 KB before it."""
    import lz4.block

    (total,) = struct.unpack_from("<I", data, 0)
    at, out = 4, bytearray()
    while True:
        if at + 4 > len(data):
            raise EnfusionError("an LZ4 level runs short of its chunks")
        (head,) = struct.unpack_from("<I", data, at)
        at += 4
        size, last = head & 0x7FFFFFFF, head >> 31
        try:
            out += lz4.block.decompress(
                data[at : at + size], uncompressed_size=min(1 << 16, total - len(out)), dict=bytes(out[-(1 << 16) :])
            )
        except lz4.block.LZ4BlockError as exc:
            raise EnfusionError(f"an LZ4 chunk does not decode: {exc}") from exc
        at += size
        if last:
            break
    if at != len(data) or len(out) != total:
        raise EnfusionError(f"an LZ4 level decodes to {len(out)} bytes of {total}, using {at} of {len(data)}")
    return bytes(out)


#: DXGI formats this decodes from a `COPY` level: bytes per 4x4 block.
_BLOCKS = {71: 8, 72: 8, 77: 16, 78: 16, 80: 8, 83: 16, 98: 16, 99: 16}


def read_edds(data: bytes) -> np.ndarray:
    """The largest level of an `.edds` as (height, width, 4) uint8 RGBA."""
    import io

    from PIL import Image

    from .unrealtexture import _dds

    if data[:4] != b"DDS ":
        raise EnfusionError("not an .edds (no DDS header)")
    height, width = struct.unpack_from("<II", data, 12)
    (mips,) = struct.unpack_from("<I", data, 28)
    fourcc = data[84:88]
    if fourcc != b"DX10":
        raise EnfusionError(f"DDS format {fourcc!r} is not read")
    (dxgi,) = struct.unpack_from("<I", data, 128)
    at = 148
    mips = max(1, mips)
    records = [struct.unpack_from("<4sI", data, at + 8 * i) for i in range(mips)]
    at += 8 * mips
    sizes = [size for _tag, size in records]
    if at + sum(sizes) != len(data):
        raise EnfusionError(f"level records add up to {at + sum(sizes)} bytes, the file is {len(data)}")
    tag, size = records[-1]
    payload = data[len(data) - size :]
    if tag == b"LZ4 ":
        payload = unlz4(payload)
    elif tag != b"COPY":
        raise EnfusionError(f"the largest level is stored as {tag!r}, which is not read")
    per = _BLOCKS.get(dxgi)
    if per is None:
        raise EnfusionError(f"DXGI format {dxgi} is not read")
    if len(payload) != -(-width // 4) * -(-height // 4) * per:
        raise EnfusionError(f"the largest level is {len(payload)} bytes, not {width} x {height} of format {dxgi}")
    # PIL decodes the linear and sRGB variants alike; the bytes are the same.
    plain = {72: 71, 78: 77, 99: 98}.get(dxgi, dxgi)
    with Image.open(io.BytesIO(_dds(width, height, plain, payload))) as image:
        return np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
