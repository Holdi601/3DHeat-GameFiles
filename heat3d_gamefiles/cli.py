"""
Command line for the game-file exporter.

Verbs in the order the questions come up: what engine is this, what is inside,
and give me that. Everything else — which mesh is the level, how to decimate it
— belongs to the viewer's own import, not here.

    python -m heat3d_gamefiles identify <path>
    python -m heat3d_gamefiles list     <archive> [--filter text] [--limit n]
    python -m heat3d_gamefiles extract  <archive> <path inside> [--out file]
    python -m heat3d_gamefiles meshes   <unity .assets> [--limit n]
    python -m heat3d_gamefiles course   <lap> [--out map.glb]
    python -m heat3d_gamefiles courses  [--out folder] [--only name ...]
    python -m heat3d_gamefiles terrain  <forza track folder> --out map.glb
                                        (--box x0 z0 x1 z1 | --route route.json)
    python -m heat3d_gamefiles levels   [--install folder]
    python -m heat3d_gamefiles level    <frostbite level> [-o map.glb]
                                        [--detail-budget n] [--skip text ...]

The file is whatever the game ships, and `identify` does not require knowing
which: an Unreal `.pak` or IoStore `.utoc`, a Unity `.assets` or bundle, a
Frostbite `.toc`, a Source 2 `.vpk`, a ForzaTech `.minizip` or `.modelbin`, a
BeamNG zip, `.cdae` or `.ter`. `list` and `extract` take the archives among
them - a `.pak`, a `.utoc`, a `.vpk`, a `.minizip` and a zip; Unity has
`meshes`, and Frostbite has `levels` and `level`, which read a whole level
from its table of contents.

The last three are the odd ones out, and deliberately. They do not take an
archive but a lap, a library of laps, or a whole Forza track folder, because a
piece of map is spread across four archives and their manifests, and it is asked
for by *place* rather than by name.

`course` is the one to reach for: give it a lap and it exports the ground around
it. It works out which game is installed, which of its tracks the lap was driven
on, and where to cut, so the only thing anyone has to know is which lap they
mean. `courses` does that for every course in a recorded library. `terrain` is
the same cut with all of that spelled out by hand, for when the answer is a box
rather than a drive.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _identify(path: Path) -> str:
    """Name the container format, by reading it rather than by extension."""
    from .frostbite import (
        UnsupportedFrostbite,
        parse_toc,
        read_header,
        read_sections,
        superbundles,
    )
    from .pak import UnsupportedPak, read_footer
    from .unity import UnsupportedUnity, read_serialized

    lines = [f"{path.name}  ({path.stat().st_size:,} bytes)"]

    try:
        info = read_footer(path)
        lines.append(f"  Unreal pak, version {info.version}")
        lines.append(f"    index      {info.index_size:,} bytes at {info.index_offset:,}")
        lines.append(f"    encrypted  {'yes' if info.encrypted_index else 'no'}")
        lines.append(f"    methods    {', '.join(info.methods) or 'none'}")
        return "\n".join(lines)
    except UnsupportedPak:
        pass

    # The containers with a magic of their own, before anything that reads the
    # whole file to find out: a Forza archive is tens of gigabytes, and an
    # IoStore partition or a level's zip not much less.
    found = _identify_by_magic(path)
    if found is not None:
        return "\n".join(lines + found)

    try:
        head = path.open("rb").read(8)
        if head.startswith(b"UnityFS"):
            from .unity import UnityBundle

            bundle = UnityBundle(path)
            lines.append(f"  Unity bundle, engine {bundle.engine_version}")
            lines.append(f"    {len(bundle)} entries")
            return "\n".join(lines)
        container = read_serialized(path)
        lines.append(f"  Unity SerializedFile, format {container.version}")
        lines.append(f"    engine     {container.unity_version}")
        lines.append(f"    objects    {len(container):,}")
        top = list(container.counts().items())[:6]
        lines.append("    holds      " + ", ".join(f"{n}x{k}" for k, n in top))
        return "\n".join(lines)
    except UnsupportedUnity:
        pass

    try:
        data = path.read_bytes()[:64]
        info = read_header(data, path.name)
        lines.append(f"  Frostbite table of contents, {info.kind}")
        lines.append(f"    tree begins at {info.payload_offset}")
        whole = path.read_bytes()
        try:
            sections = read_sections(whole, info, path.name)
            lines.append(f"    assets     {sections.asset_count:,}")
        except UnsupportedFrostbite:
            names = superbundles(parse_toc(path)[1])
            lines.append(f"    superbundles {len(names)}")
        return "\n".join(lines)
    except UnsupportedFrostbite:
        pass

    try:
        from .vpk import UnsupportedVpk, VpkArchive

        archive = VpkArchive(path)
        lines.append(f"  Source 2 VPK, version {archive.version}")
        lines.append(f"    entries    {len(archive):,}")
        navs = [n for n in archive.list() if n.endswith(".nav")]
        if navs:
            lines.append(f"    navmesh    {navs[0]}")
        return "\n".join(lines)
    except UnsupportedVpk:
        pass

    found = _identify_beamng(path)
    if found is not None:
        return "\n".join(lines + found)

    try:
        from .forzatech import UnsupportedForza, read_model

        model = read_model(path)
        lines.append(f"  ForzaTech model, version {model.version}")
        lines.append(f"    chunks     {len(model)}")
        lines.append(
            "    holds      "
            + ", ".join(f"{n}x{t}" for t, n in list(model.counts().items())[:6])
        )
        lines.append("    note       chunk contents are not decoded")
        return "\n".join(lines)
    except UnsupportedForza as exc:
        lines.append("  not a format this tool reads")
        lines.append(f"    {exc}")
    return "\n".join(lines)


def _head(path: Path, size: int) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def _identify_by_magic(path: Path) -> list[str] | None:
    """An IoStore table of contents or partition, a `.minizip`, a zip; else None."""
    from .iostore import MAGIC as IOSTORE_MAGIC
    from .minizip import MAGIC as MINIZIP_MAGIC

    head = _head(path, 16)
    if head == IOSTORE_MAGIC:
        return _identify_iostore(path)
    # A partition has no header at all, so this one goes by its name: a
    # `.ucas` is only ever read through the `.utoc` of the same name.
    if path.suffix.lower() == ".ucas" and path.with_suffix(".utoc").exists():
        return [
            "  Unreal IoStore data (a .ucas carries no header of its own)",
            f"    contents   {path.with_suffix('.utoc').name}, which is what identify, list and extract take",
        ]
    if head[:4] == MINIZIP_MAGIC:
        return _identify_minizip(path)
    if head[:4] in _ZIP_MAGIC:
        return _identify_zip(path)
    return None


def _identify_iostore(path: Path) -> list[str]:
    import struct

    from .iostore import Container, IoStoreError, read_header

    try:
        header = read_header(_head(path, 144))
    except (IoStoreError, struct.error) as exc:
        return ["  Unreal IoStore table of contents, but not one this reads", f"    {exc}"]
    lines = [
        f"  Unreal IoStore table of contents, version {header.version}",
        f"    chunks     {header.entries:,}",
        f"    encrypted  {'yes' if header.encrypted else 'no'}",
    ]
    if header.encrypted:
        lines.append("    note       this tool holds no keys, so it cannot be listed")
        return lines
    try:
        container = Container.open(path)
    except (IoStoreError, OSError, struct.error) as exc:
        lines.append(f"    unreadable {exc}")
        return lines
    lines.append(f"    files      {len(container.files):,}" + (f" under {container.mount}" if container.mount else ""))
    lines.append(f"    methods    {', '.join(container.methods) or 'none'}")
    data = path.with_suffix(".ucas")
    lines.append(f"    data       {data.name}" + ("" if data.exists() else " - missing"))
    return lines


def _identify_minizip(path: Path) -> list[str]:
    from .minizip import Contents, MiniZip, UnsupportedMiniZip, manifest_of

    try:
        archive = MiniZip(path)
    except UnsupportedMiniZip as exc:
        return ["  ForzaTech .minizip archive, but not one this reads", f"    {exc}"]
    with archive:
        lines = [
            f"  ForzaTech .minizip archive, version {archive.version}",
            f"    entries    {archive.count:,} in {archive.segments:,} segments",
        ]
    manifest = manifest_of(path)
    if manifest is not None and manifest.exists():
        names = len(Contents(manifest))
        disagree = (
            f" - {names:,} names for {archive.count:,} entries, so they do not belong together"
            if names != archive.count
            else ""
        )
        lines.append(f"    names      {manifest.name}{disagree}")
    else:
        # The archive stores no names; without the manifest an entry is a number.
        lines.append("    names      no manifest beside it, so entries go by number (#0, #1, ...)")
    return lines


def _identify_zip(path: Path) -> list[str]:
    import zipfile
    from collections import Counter

    try:
        with zipfile.ZipFile(path) as bundle:
            names = [n for n in bundle.namelist() if not n.endswith("/")]
    except (zipfile.BadZipFile, OSError) as exc:
        return ["  zip archive, but not one this reads", f"    {exc}"]
    lines = [f"  zip archive, {len(names):,} entries"]
    kinds = Counter(
        "." + n.rsplit(".", 1)[-1].lower() if "." in n.rsplit("/", 1)[-1] else "(no extension)"
        for n in names
    )
    if kinds:
        lines.append("    holds      " + ", ".join(f"{n}x{k}" for k, n in kinds.most_common(6)))
    # BeamNG ships one zip per level, everything in it under `levels/<name>/`.
    levels = sorted({n.split("/")[1] for n in names if n.lower().startswith("levels/") and n.count("/") >= 2})
    if levels:
        lines.append(f"    levels     {', '.join(levels[:6])} (laid out as a BeamNG.drive level)")
    return lines


def _identify_beamng(path: Path) -> list[str] | None:
    """A BeamNG `.cdae` shape or `.ter` terrain, by their contents; else None."""
    import struct

    from .beamngshape import SHAPE_VERSION

    head = _head(path, 8)
    if len(head) == 8 and struct.unpack_from("<I", head)[0] & 0xFF == SHAPE_VERSION:
        from .beamngshape import read_shape

        try:
            shape = read_shape(path.read_bytes())
        except Exception:  # noqa: BLE001 - whatever does not parse is not a shape
            shape = None
        if shape is not None:
            return [
                f"  BeamNG.drive shape (.cdae), version {SHAPE_VERSION}",
                f"    meshes     {len(shape.meshes):,}",
                f"    detail     {len(shape.levels())} drawn levels",
                f"    materials  {', '.join(shape.materials[:6]) or 'none'}",
            ]
    if len(head) < 5:
        return None
    # A `.ter`: a version byte, the side, side x side heights and as many layer
    # bytes, then the layer names. No magic, so all of it has to add up.
    side = int.from_bytes(head[1:5], "little")
    if not 2 <= side <= 16384:
        return None
    at = 5 + side * side * 3
    with path.open("rb") as handle:
        handle.seek(at)
        tail = handle.read(4 + 256 * 256)
    if len(tail) < 4:
        return None
    count = int.from_bytes(tail[:4], "little")
    if not 0 < count <= 255:
        return None
    names, at = [], 4
    for _ in range(count):
        if at >= len(tail) or at + 1 + tail[at] > len(tail):
            return None
        name = tail[at + 1 : at + 1 + tail[at]]
        if not name or not all(32 <= c < 127 for c in name):
            return None
        names.append(name.decode("ascii"))
        at += 1 + tail[at]
    return [
        f"  BeamNG.drive terrain (.ter), version {head[0]}",
        f"    heights    {side:,} x {side:,}",
        f"    layers     {', '.join(names[:6])}" + (f" and {len(names) - 6} more" if len(names) > 6 else ""),
    ]


#: What a zip begins with: a local file header, or the end record of an empty one.
_ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06")

#: What `list` and `extract` open, for the message when a file is none of them.
_ARCHIVES = "an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip"


class ArchiveError(Exception):
    """An archive `list` or `extract` cannot open or read, said in one line."""


class BadKey(ValueError):
    """A `--key` that is not an AES-256 key written in hex."""


def _aes_key(key: str | None) -> bytes | None:
    if not key:
        return None
    text = key[2:] if key.lower().startswith("0x") else key
    try:
        aes = bytes.fromhex(text)
    except ValueError:
        raise BadKey(f"--key is not hexadecimal: {key!r}") from None
    if len(aes) != 32:
        raise BadKey(f"--key takes an AES-256 key, 64 hex digits; this one has {len(text)}")
    return aes


class _Listing:
    """
    What `list` and `extract` need of an archive, whichever kind it is: its
    entry names, and for each its size, how it is stored, and its bytes.
    """

    def __init__(self, names) -> None:
        self.names = sorted(names)
        self._known = set(self.names)

    def list(self, pattern: str | None = None) -> list[str]:
        if not pattern:
            return list(self.names)
        needle = pattern.lower()
        return [n for n in self.names if needle in n.lower()]

    def __contains__(self, name: str) -> bool:
        return name in self._known

    def describe(self, name: str) -> tuple[int, str]:
        raise NotImplementedError

    def read(self, name: str) -> bytes:
        raise NotImplementedError

    def close(self) -> None:
        pass


class _PakListing(_Listing):
    def __init__(self, archive) -> None:
        super().__init__(archive.entries)
        self.archive = archive

    def describe(self, name):
        entry = self.archive.entries[name]
        return entry.uncompressed_size, self.archive.info.method_name(entry.method)

    def read(self, name):
        return self.archive.read(name)


class _VpkListing(_Listing):
    def __init__(self, archive) -> None:
        super().__init__(archive.entries)
        self.archive = archive

    def describe(self, name):
        # A VPK entry is never compressed.
        return self.archive.entries[name].size, "stored"

    def read(self, name):
        return self.archive.read(name)


class _IoStoreListing(_Listing):
    """One `.utoc` and its partitions, by the package paths its directory names."""

    def __init__(self, utoc: Path) -> None:
        from .iostore import Container, IoStoreError

        self.container = Container.open(utoc)
        if not self.container.files:
            raise IoStoreError(f"{utoc.name} has no directory index, so its chunks carry no names to list")
        super().__init__(self.container.files)

    def describe(self, name):
        entry = self.container.files[name]
        offset, size = self.container.spans[entry]
        # The method of the chunk's first block. A block that would not shrink
        # is stored even in a compressed container, so this is the usual one
        # rather than a promise about every block.
        method = self.container.blocks[offset // self.container.header.block_size][3] if size else 0
        if method == 0:
            return size, "none"
        methods = self.container.methods
        return size, methods[method - 1] if method <= len(methods) else f"unknown({method})"

    def read(self, name):
        return self.container.read(self.container.files[name])


class _MiniZipListing(_Listing):
    """
    A `.minizip`, by the names in the manifest beside it, or by entry number
    (`#12`) where there is none. The number works either way.
    """

    CODECS = {0x00: "stored", 0x08: "deflate", 0x1F: "lz4"}

    def __init__(self, path: Path) -> None:
        from .minizip import Contents, MiniZip, UnsupportedMiniZip, manifest_of

        self.archive = MiniZip(path)
        manifest = manifest_of(path)
        if manifest is not None and manifest.exists():
            names = Contents(manifest).names
            if len(names) != self.archive.count:
                self.archive.close()
                raise UnsupportedMiniZip(
                    f"{manifest.name} names {len(names):,} entries but {path.name} holds "
                    f"{self.archive.count:,}; the two do not belong together"
                )
        else:
            names = [f"#{i}" for i in range(self.archive.count)]
        self._index: dict[str, int] = {}
        for number, name in enumerate(names):
            self._index.setdefault(name, number)
        super().__init__(self._index)

    def _number(self, name: str) -> int | None:
        if name in self._index:
            return self._index[name]
        if name.startswith("#") and name[1:].isdigit() and int(name[1:]) < self.archive.count:
            return int(name[1:])
        return None

    def __contains__(self, name: str) -> bool:
        return self._number(name) is not None

    def describe(self, name):
        entry = self.archive.entry(self._number(name))
        return entry.size, self.CODECS.get(entry.codec, f"unknown({entry.codec})")

    def read(self, name):
        return self.archive.read(self._number(name))

    def close(self) -> None:
        self.archive.close()


class _ZipListing(_Listing):
    """A plain zip: BeamNG's level and content archives, Forza's model zips."""

    METHODS = {0: "stored", 8: "deflate", 9: "deflate64", 12: "bzip2", 14: "lzma", 93: "zstd"}

    def __init__(self, path: Path) -> None:
        import zipfile

        self.bundle = zipfile.ZipFile(path)
        self.infos = {i.filename: i for i in self.bundle.infolist() if not i.is_dir()}
        super().__init__(self.infos)

    def describe(self, name):
        info = self.infos[name]
        return info.file_size, self.METHODS.get(info.compress_type, f"method {info.compress_type}")

    def read(self, name):
        return self.bundle.read(name)

    def close(self) -> None:
        self.bundle.close()


def _reader_errors() -> tuple[type[BaseException], ...]:
    """Everything the archive readers raise to say a file cannot be read."""
    import struct
    import zipfile

    from .iostore import IoStoreError
    from .minizip import UnsupportedMiniZip
    from .oodle import OodleUnavailable
    from .pak import EncryptedPak, UnsupportedPak
    from .vpk import UnsupportedVpk

    return (
        ArchiveError,
        UnsupportedPak,
        EncryptedPak,
        UnsupportedVpk,
        IoStoreError,
        UnsupportedMiniZip,
        OodleUnavailable,
        zipfile.BadZipFile,
        # What zipfile raises for a method it has no codec for, and for an
        # entry that wants a password.
        NotImplementedError,
        RuntimeError,
        struct.error,
        OSError,
    )


def _open_archive(path: Path, key: str | None) -> _Listing:
    """
    Open whichever kind of archive this is.

    Dispatching on the bytes rather than on the extension, and rather than on a
    flag the user has to pass: `list` and `extract` mean the same thing for an
    Unreal pak, an IoStore container, a Source 2 VPK, a Forza `.minizip` and a
    BeamNG zip, and making someone say which they have is asking them to know
    something the tool can see. Raises `BadKey` for a `--key` that is not one,
    and one of `_reader_errors()` for a file that does not open.
    """
    import struct

    from .iostore import MAGIC as IOSTORE_MAGIC
    from .minizip import MAGIC as MINIZIP_MAGIC
    from .pak import PAK_MAGIC, PakArchive
    from .vpk import VPK_MAGIC, VpkArchive

    aes = _aes_key(key)
    head = _head(path, 16)
    if head == IOSTORE_MAGIC:
        return _IoStoreListing(path)
    if path.suffix.lower() == ".ucas" and path.with_suffix(".utoc").exists():
        # A partition has no header; its table of contents is what opens it.
        return _IoStoreListing(path.with_suffix(".utoc"))
    if head[:4] == MINIZIP_MAGIC:
        return _MiniZipListing(path)
    if head[:4] == struct.pack("<I", VPK_MAGIC):
        return _VpkListing(VpkArchive(path))
    if head[:4] in _ZIP_MAGIC:
        return _ZipListing(path)
    # Last, because a pak is the one recognised by its end rather than its start.
    size = path.stat().st_size
    with path.open("rb") as handle:
        handle.seek(max(0, size - 1024))
        tail = handle.read()
    if struct.pack("<I", PAK_MAGIC) not in tail:
        raise ArchiveError(f"{path.name} is not an archive list and extract read ({_ARCHIVES})")
    return _PakListing(PakArchive(path, aes_key=aes))


def _write_course(out, track, target, args, low, high, route=None, corridor=None) -> Path:
    """
    Bake, place, plan and write: the part of an export both verbs share.

    Textures are baked per tile from the track's own maps unless turned off,
    and a tile whose maps are missing falls back to flat colour rather than
    failing the export - detail is optional, geometry is not. The same goes for
    placed models: kerbs, barriers and the rest are added from the track's
    placement files, each with its own texture where the game gives it one,
    and with the detail going to what stands nearest `route`, the driving.
    """
    import numpy as np

    from .courseexport import bake_tiles, lift_decals, plan_parts, planar_uvs
    from .glb import Part, compute_normals, write_glb

    images = {}
    if not args.no_textures and out.tile_keys:
        images = bake_tiles(
            track, out.tile_keys, size=args.texture_size, season=args.season
        )
        missing = len(out.tile_keys) - len(images)
        note = f", {missing} without maps" if missing else ""
        print(
            f"\n  baked {len(images)} ground textures at {args.texture_size} px "
            f"({512 / args.texture_size * 100:.0f} cm a pixel){note}"
        )

    plan = plan_parts(out, images)
    total = sum(plan.counts.values())
    print("\n  what the ground is made of:")
    for label, many in sorted(plan.counts.items(), key=lambda kv: -kv[1]):
        print(f"    {many:9,} triangles  {many / total:5.1%}  {label}")

    ground_normals = out.normals if out.normals is not None else compute_normals(out.positions, out.faces)
    parts, decal_positions, decal_normals = lift_decals(plan.parts, out.positions, ground_normals)
    positions = [out.positions, decal_positions]
    normals = [ground_normals, decal_normals]
    uvs = [
        planar_uvs(out) if plan.textured else np.zeros((len(out.positions), 2), np.float32),
        np.zeros((len(decal_positions), 2), np.float32),
    ]
    textured = plan.textured
    if not args.no_placed:
        from .forzaplacement import DEFAULT_CATEGORIES, VEGETATION, place_in_track

        categories = DEFAULT_CATEGORIES + (VEGETATION if args.trees else ())
        placed = place_in_track(
            track,
            low,
            high,
            categories=categories,
            budget=args.detail_budget,
            season=args.season,
            textures=not args.no_textures,
            route=route,
            corridor=corridor,
        )
        if placed.parts:
            print(
                f"\n  placed on it ({placed.triangles():,} triangles of a "
                f"{placed.budget:,} budget, {len(placed.textures)} textures):"
            )
            print(placed.summary())
        offset = len(out.positions) + len(decal_positions)
        for name, mesh in sorted(placed.parts.items()):
            positions.append(mesh.positions)
            normals.append(mesh.normals)
            uvs.append(mesh.uvs if mesh.uvs is not None else np.zeros((len(mesh.positions), 2), np.float32))
            texture = placed.textures.get(mesh.texture) if mesh.texture else None
            textured = textured or texture is not None
            parts.append(
                Part(name=name, faces=mesh.faces + offset, colour=None if texture is not None else mesh.colour, texture=texture)
            )
            offset += len(mesh.positions)

    written = write_glb(
        target,
        np.concatenate(positions),
        parts=parts,
        normals=np.concatenate(normals),
        uvs=np.concatenate(uvs).astype(np.float32) if textured else None,
    )
    print(f"\nwrote {written} ({written.stat().st_size:,} bytes)")
    return written


def _course(args) -> int:
    """
    A lap in, the ground around it out.

    Everything between those two is derivable and so is derived: which game is
    installed, which of its tracks these coordinates belong to, and what to
    cut. The alternative is a command line carrying a forty-character path to a
    folder inside a game someone already has installed, which nobody should have
    to look up to export a corner of a racetrack.
    """
    from .lapinput import UnreadableLap, read

    try:
        driven = read(args.lap)
    except UnreadableLap as exc:
        print(exc, file=sys.stderr)
        return 1
    target = args.out or Path(_slug(driven.name) + ".glb")
    game = (getattr(args, "game", None) or driven.game or "forza").lower()
    if game == "beamng":
        from .beamngcourse import export

        if len(driven) < 2:
            print(f"{driven.name} holds no driving", file=sys.stderr)
            return 1
        print(f"{driven.name}: {len(driven):,} samples, {driven.metres:,.0f} m driven (BeamNG.drive)")
        return export(driven, target, args, install=getattr(args, "install", None))
    if game in ("assetto-corsa-rally", "acrally"):
        from .acrallycourse import export as export_rally

        if len(driven) < 2:
            print(f"{driven.name} holds no driving", file=sys.stderr)
            return 1
        print(f"{driven.name}: {len(driven):,} samples, {driven.metres:,.0f} m driven (Assetto Corsa Rally)")
        return export_rally(driven, target, args, paks=getattr(args, "install", None))
    if not game.startswith("forza"):
        print(_no_course(game), file=sys.stderr)
        return 1
    return export_course(driven, target, args)


#: Why a game's lap cannot be turned into a course from its files yet. Said
#: plainly, with the route that does work for every game.
_WHY_NOT = {
    "assetto-corsa-evo": (
        "Assetto Corsa EVO keeps all its content in one package obfuscated "
        "with a key, and this tool recovers none"
    ),
    "iracing": "iRacing's tracks ship in a protected format that is not a file-extraction target",
}


def _no_course(game: str) -> str:
    reason = _WHY_NOT.get(game, f"there is no course reader for {game} yet")
    return (
        f"no course export for this lap: {reason}.\n"
        "  Courses can be exported from Forza, BeamNG.drive and Assetto Corsa Rally laps. For the "
        "rest, reconstruct the course from gameplay\n"
        "  (gamecapture), or analyse the laps without one - the "
        "Race tab draws a road from them."
    )


def _slug(name: str) -> str:
    """A course name as a file name: `Mapletree Test Loop` -> `mapletree_test_loop`."""
    import re

    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "course"


def export_course(driven, target: Path, args) -> int:
    """
    Export the ground and everything on it along one course's driving.

    The cut is a corridor `args.margin` metres either side of the driven line,
    not the driving's bounding box: the same thing for a circuit, and a tenth
    of it for a point-to-point sprint, whose box is mostly hillside nobody
    drives past.
    """
    from .corridor import Corridor
    from .forzainstall import find_track
    from .forzaterrain import extract_from_track

    if len(driven) < 2:
        print(f"{driven.name} holds no driving", file=sys.stderr)
        return 1

    corridor = Corridor(driven.positions, args.margin)
    low, high = driven.box(args.margin)
    laps = f"{driven.laps} laps, " if driven.laps > 1 else ""
    print(
        f"{driven.name}: {laps}{len(driven):,} samples, {driven.metres:,.0f} m driven"
    )

    track = args.track
    if track is None:
        try:
            track = find_track(low, high)
        except FileNotFoundError as exc:
            print(exc, file=sys.stderr)
            return 1
        print(f"  on {track.name}, in {track.parents[2].name}")

    print(
        f"  cutting {args.margin:,.0f} m either side of the driving: "
        f"{corridor.area / 1e6:,.2f} km2 of a {high[0] - low[0]:,.0f} by "
        f"{high[1] - low[1]:,.0f} m box"
    )
    out = extract_from_track(track, low, high, corridor=corridor)
    if not len(out.faces):
        print(
            f"\nno terrain there. {track.name} has tiles nearby but none that "
            "cover the driving, which usually means the lap and the track are "
            "from different games.",
            file=sys.stderr,
        )
        return 1

    print()
    print(out.summary())
    _write_course(out, track, target, args, low, high, route=driven.positions, corridor=corridor)
    return 0


def _courses(args) -> int:
    """
    Every course in a recorded lap library, one file each.

    Carries on past a course that fails, and says at the end which did; a
    course already exported is skipped unless `--force`, so a run that was
    interrupted picks up where it stopped.
    """
    import time

    from .lapinput import UnreadableLap, default_library, read

    try:
        library = Path(args.library) if args.library else default_library()
    except UnreadableLap as exc:
        print(exc, file=sys.stderr)
        return 1
    if not library.is_dir():
        print("no recorded lap library found; name one with --library", file=sys.stderr)
        return 1
    folder = Path(args.out)
    folder.mkdir(parents=True, exist_ok=True)
    courses = sorted(
        p for p in Path(library).iterdir() if p.is_dir() and " (course_" in p.name
    )
    if args.only:
        wanted = [w.lower() for w in args.only]
        courses = [p for p in courses if any(w in p.name.lower() for w in wanted)]
    results = []
    for number, course in enumerate(courses, 1):
        name = course.name.split(" (course_")[0]
        target = folder / (_slug(name) + ".glb")
        if target.exists() and not args.force:
            results.append((name, "kept", target.stat().st_size, 0.0))
            continue
        print(f"\n=== {number}/{len(courses)}: {name} ===")
        started = time.time()
        try:
            driven = read(course)
            status = export_course(driven, target, args)
        except (UnreadableLap, OSError, ValueError, MemoryError) as exc:
            print(f"  failed: {exc}", file=sys.stderr)
            status = 1
        took = time.time() - started
        size = target.stat().st_size if target.exists() and status == 0 else 0
        results.append((name, "written" if status == 0 else "FAILED", size, took))

    print("\n" + "-" * 72)
    for name, status, size, took in results:
        extra = f"{size / 1e6:8.1f} MB" if size else " " * 11
        timing = f"{took:6.0f} s" if took else ""
        print(f"  {status:8} {extra}  {timing:>8}  {name}")
    failed = [r for r in results if r[1] == "FAILED"]
    print(f"\n{len(results) - len(failed)} of {len(results)} courses in {folder}")
    return 1 if failed else 0


def _route_box(path: Path, margin: float) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    The ground a recorded lap covers, widened a little.

    The margin is not cosmetic. A lap is a line, and a line's bounding box in the
    plane is the road and nothing either side of it — no verge, no barrier, no
    hill the road runs along. A hundred metres is enough to see what the driver
    saw.
    """
    import json

    # utf-8-sig, as `lapinput` reads JSON: a file written by a .NET tool, or
    # saved by Notepad, starts with a byte-order mark that plain utf-8 refuses.
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    box = data.get("bounds") if isinstance(data, dict) else None
    if not box:
        raise SystemExit(
            f"{path} has no bounds; --route takes a route file with "
            '"bounds": {"min": [x, y, z], "max": [x, y, z]}'
        )
    low, high = box["min"], box["max"]
    return (
        (low[0] - margin, low[2] - margin),
        (high[0] + margin, high[2] + margin),
    )


def _terrain(args) -> int:
    from .forzaterrain import extract_from_track
    from .glb import write_glb

    if bool(args.box) == bool(args.route):
        print("give exactly one of --box and --route", file=sys.stderr)
        return 2
    route = corridor = None
    if args.route:
        from .corridor import Corridor
        from .lapinput import UnreadableLap, read_file

        low, high = _route_box(args.route, args.margin)
        try:
            route = read_file(args.route)
        except UnreadableLap:
            route = None
        # A route file that only carries its bounds is a box, not a line.
        if route is not None and len(route) >= 10:
            corridor = Corridor(route, args.margin)
    else:
        x0, z0, x1, z1 = args.box
        low, high = (min(x0, x1), min(z0, z1)), (max(x0, x1), max(z0, z1))

    span = (high[0] - low[0], high[1] - low[1])
    print(
        f"cutting {span[0]:,.0f} by {span[1]:,.0f} metres "
        f"at x {low[0]:,.0f}..{high[0]:,.0f}, z {low[1]:,.0f}..{high[1]:,.0f}"
    )
    out = extract_from_track(args.path, low, high, corridor=corridor)
    if not len(out.faces):
        print(
            "no terrain there.\n"
            "  The coordinates are the game's own metres, as its telemetry reports\n"
            "  them. A box outside the map, or in the sea, is empty rather than an\n"
            "  error.",
            file=sys.stderr,
        )
        return 1

    print(out.summary())
    _write_course(out, args.path, args.out, args, low, high, route=route, corridor=corridor)
    return 0


def _frostbite_install(given: Path | None) -> Path | None:
    """
    A Frostbite game's folder: the one given, or the first Steam game whose
    `Data` holds a `layout.toc`.
    """
    from .forzainstall import STEAM_DEFAULTS, steam_libraries

    if given is not None:
        return given
    for library in [Path(p) for p in STEAM_DEFAULTS] + steam_libraries():
        common = library / "steamapps" / "common"
        if not common.is_dir():
            continue
        for game in sorted(common.iterdir()):
            if (game / "Data" / "layout.toc").is_file():
                return game
    return None


def _levels(args) -> int:
    from .frostbite import UnsupportedFrostbite
    from .frostbitebundle import level_sources

    install = _frostbite_install(args.install)
    if install is None:
        print("no Frostbite game found in a Steam library; give --install", file=sys.stderr)
        return 2
    try:
        tables = level_sources(install)
    except UnsupportedFrostbite as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"{len(tables)} levels in {install}")
    for name, table in sorted(tables.items()):
        extra = f" (+{len(table.supplements)} high-resolution)" if table.supplements else ""
        print(f"  {name:<40} {table.toc.stat().st_size:>12,}  {table.source}{extra}")
    return 0


def _level(args) -> int:
    from .frostbite import UnsupportedFrostbite
    from .frostbitelevel import build_level, write_level

    install = _frostbite_install(args.install)
    if install is None:
        print("no Frostbite game found in a Steam library; give --install", file=sys.stderr)
        return 2
    out = args.out or Path(f"{Path(args.level).stem}.glb")
    try:
        model = build_level(
            install,
            args.level,
            budget=args.detail_budget,
            skip=tuple(args.skip or ()),
            textures=args.textures,
            ground_spacing=args.ground_spacing,
            ground_texture=args.ground_texture,
            navmesh=args.navmesh,
            by_mesh=args.by_mesh,
        )
    except UnsupportedFrostbite as exc:
        print(exc, file=sys.stderr)
        return 1

    placed = model.placements
    print(
        f"{placed.copies():,} copies of {len(placed.meshes):,} meshes, from "
        f"{len(placed.partitions)} static model groups"
    )
    for name, copies in sorted(placed.partitions.items(), key=lambda kv: -kv[1]):
        print(f"  {copies:>8,}  {name}")
    if placed.objects:
        print(f"  {placed.objects:>8,}  placed one by one (object and prefab references)")
    if placed.unresolved:
        print(f"{placed.unresolved:,} members name a mesh this level does not carry; left out")
    reasons: dict[str, int] = {}
    for why in model.skipped.values():
        reasons[why] = reasons.get(why, 0) + 1
    for why, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"{count:,} meshes left out: {why}")
    print(
        f"{model.triangles():,} triangles, budget {model.budget:,}; "
        f"{model.coarser:,} meshes drawn at a coarser level to fit"
    )
    if model.dropped:
        print(
            f"{model.dropped:,} copies left out to fit the budget, the smallest first "
            "(--detail-budget raises it)"
        )
    kinds: dict[str, list[int]] = {}
    for part, piece in model.parts.items():
        part = part.replace(" (destructible)", "")
        short = (piece.texture or "").rsplit("/", 1)[-1]
        kind = part[: -len(short) - 1] if piece.texture and part.endswith(" " + short) else part
        entry = kinds.setdefault(kind, [0, 0])
        entry[0] += sum(len(f) for f in piece.faces)
        entry[1] += 1 if piece.texture else 0
    for kind, (triangles, textures) in sorted(kinds.items()):
        print(f"  {triangles:>12,}  {kind}" + (f", {textures:,} texture{'s' if textures > 1 else ''}" if textures else ""))
    if args.textures:
        done, drawn = model.textured
        print(f"{done:,} of {drawn:,} drawn sections carry their colour map; the rest are flat colours")
    print(f"Ground: {model.ground}.")
    if args.navmesh:
        print(f"Navigation mesh: {model.navmesh}.")
    if model.blockout:
        print(f"{model.blockout:,} triangles of placeholder blockout sections left out.")
    if placed.variations:
        print(
            f"{placed.variations:,} grouped copies placed in an object variation; "
            f"{model.varied:,} section copies drawn with their variation's own shader block."
        )
    if model.destructible:
        print(f"{model.destructible:,} triangles of destructible meshes, in parts named '... (destructible)'.")
    if model.overlaid:
        print(f"{model.overlaid:,} sections drawn with their object's overlay through its second texture coordinates.")
    try:
        write_level(model, out)
    except (UnsupportedFrostbite, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    if model.flattened:
        print(
            f"{model.flattened:,} triangle{'s' if model.flattened > 1 else ''} repeat their texture too "
            "densely to cut and are drawn in its average colour."
        )
    print(f"-> {out} ({out.stat().st_size / 1e6:,.0f} MB)")
    return 0


def _export_options(p) -> None:
    """The options `course` and `terrain` share: what goes into the file."""
    from .forzaplacement import DEFAULT_BUDGET

    p.add_argument(
        "--texture-size",
        type=int,
        choices=(2048, 1024, 512),
        default=2048,
        help="ground texture per 512 m tile, in pixels (2048 = 25 cm a pixel)",
    )
    p.add_argument(
        "--no-textures",
        action="store_true",
        help="flat colours only: a far smaller file, and no ground detail",
    )
    p.add_argument(
        "--season",
        choices=("summer", "autumn", "winter", "spring"),
        default="summer",
        help="which season's ground maps and model textures to use",
    )
    p.add_argument(
        "--no-placed",
        action="store_true",
        help="terrain only: leave out kerbs, barriers, tyre walls, signs and buildings",
    )
    p.add_argument(
        "--trees",
        action="store_true",
        help="also place trees and bushes (many triangles, and they hide the road)",
    )
    p.add_argument(
        "--detail-budget",
        type=int,
        default=None,
        help=(
            "a ceiling on triangles for everything placed; the costliest models drop "
            "to coarser levels of detail until it fits, and past that the furthest "
            "copies are left out (default: enough to keep every copy, and at least "
            f"{DEFAULT_BUDGET:,}; kerbs always stay at full detail)"
        ),
    )


def _list(archive: _Listing, args) -> int:
    names = archive.list(args.filter)
    print(f"{len(names):,} entries" + (f" matching {args.filter!r}" if args.filter else ""))
    for name in names[: args.limit]:
        size, how = archive.describe(name)
        print(f"  {size:>12,}  {how:<6} {name}")
    if len(names) > args.limit:
        print(f"  ... {len(names) - args.limit:,} more")
    return 0


def _extract(archive: _Listing, args) -> int:
    import re

    if args.entry not in archive:
        print(f"not in the archive: {args.entry}", file=sys.stderr)
        return 1
    data = archive.read(args.entry)
    # A Forza manifest names entries with backslashes, and an archive without
    # one by number (`#12`, written as `12`).
    out = args.out or Path(re.split(r"[/\\]", args.entry)[-1].lstrip("#") or "entry")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"{len(data):,} bytes -> {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="heat3d_gamefiles",
        description="Read level data out of shipped game archives.",
        epilog=(
            "Encrypted archives need a key you already hold; this tool has none "
            "and recovers none. What you point it at is subject to that game's "
            "own licence."
        ),
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    p = sub.add_parser("identify", help="say what a file is")
    p.add_argument("path", type=Path)

    archives = "an Unreal .pak or IoStore .utoc, a Source 2 .vpk (the _dir.vpk), a ForzaTech .minizip, or a zip"
    key_help = "an AES-256 key in hex (64 digits), if you hold one; only an encrypted .pak needs it"

    p = sub.add_parser("list", help="list what is inside an archive")
    p.add_argument("path", type=Path, help=archives)
    p.add_argument("--filter", default=None, help="only paths containing this text")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--key", default=None, help=key_help)

    p = sub.add_parser("extract", help="write one entry to disk")
    p.add_argument("path", type=Path, help=archives)
    p.add_argument("entry", help="the path as list prints it (a .minizip without its manifest: #number)")
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--key", default=None, help=key_help)

    p = sub.add_parser("meshes", help="list the meshes in a Unity container")
    p.add_argument("path", type=Path)
    p.add_argument("--limit", type=int, default=25)

    p = sub.add_parser(
        "course", help="export the ground around a lap, working out the rest"
    )
    _export_options(p)
    p.add_argument(
        "lap",
        help=(
            "a lap or course: a file written by heat3d_capture, a lap or course "
            "folder from a recorded library, or just a course's name"
        ),
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="where to write the .glb (default: the course's name)",
    )
    p.add_argument(
        "--track",
        type=Path,
        default=None,
        help="the track folder, if the installed game should not be searched for",
    )
    p.add_argument(
        "--margin",
        type=float,
        default=80.0,
        help="metres of ground to keep either side of the driving (default 80)",
    )
    p.add_argument(
        "--game",
        choices=("forza", "beamng", "acrally"),
        default=None,
        help="which game the lap is from (default: what the lap file says, else Forza)",
    )
    p.add_argument(
        "--level",
        default=None,
        help="BeamNG, AC Rally: the level or stage, if it should not be found from the lap",
    )
    p.add_argument(
        "--install",
        type=Path,
        default=None,
        help="BeamNG, AC Rally: the game's folder, if it is not in a Steam library",
    )
    p.set_defaults(run=_course)

    p = sub.add_parser(
        "courses", help="export every course in a recorded lap library, one file each"
    )
    _export_options(p)
    p.add_argument("-o", "--out", default="courses", help="folder to write into (default ./courses)")
    p.add_argument(
        "--library",
        default=None,
        help="the lap library (default: FH Companion's, under %%LOCALAPPDATA%%)",
    )
    p.add_argument("--only", nargs="+", default=None, help="just the courses whose names contain these")
    p.add_argument("--force", action="store_true", help="export again what is already there")
    p.add_argument("--track", type=Path, default=None, help="the track folder, if not the installed game's")
    p.add_argument("--margin", type=float, default=80.0, help="metres either side of the driving (default 80)")
    p.set_defaults(run=_courses)

    p = sub.add_parser(
        "terrain", help="cut a piece of Forza terrain out, by world coordinates"
    )
    _export_options(p)
    p.add_argument("path", type=Path, help="a track folder under media/Tracks")
    p.add_argument("-o", "--out", type=Path, required=True)
    p.add_argument(
        "--box",
        type=float,
        nargs=4,
        metavar=("X0", "Z0", "X1", "Z1"),
        default=None,
        help="the region to cut, in the game's metres",
    )
    p.add_argument(
        "--route",
        type=Path,
        default=None,
        help=(
            'a route JSON with "bounds" {"min": [x, y, z], "max": [x, y, z]}, as '
            "heat3d_capture route and laps write it; its x and z extent is the region, "
            "and its positions, if it has at least 10, narrow it to a corridor"
        ),
    )
    p.add_argument(
        "--margin",
        type=float,
        default=100.0,
        help="metres to add around a route, so the verge comes with the road",
    )

    p = sub.add_parser("levels", help="list the levels of an installed Frostbite game")
    p.add_argument("--install", type=Path, default=None, help="the game's folder, if not in a Steam library")

    p = sub.add_parser(
        "level", help="export a Frostbite level: its terrain backdrop and placed meshes"
    )
    p.add_argument("level", help="the level's name as `levels` lists it, or its .toc")
    p.add_argument("-o", "--out", type=Path, default=None, help="the .glb (default: <level>.glb)")
    p.add_argument("--install", type=Path, default=None, help="the game's folder, if not in a Steam library")
    p.add_argument(
        "--detail-budget",
        type=int,
        default=None,
        help=(
            "a ceiling on triangles; the costliest meshes drop to coarser levels of "
            "detail until it fits (default: every copy at its coarsest, plus a "
            "quarter, at least 1,500,000; the terrain stays at full detail)"
        ),
    )
    p.add_argument(
        "--textures",
        type=int,
        nargs="?",
        const=512,
        default=0,
        metavar="PIXELS",
        help=(
            "write each surface's colour map, no larger than PIXELS a side "
            "(default 512 when given without a size); without it, flat colours"
        ),
    )
    p.add_argument(
        "--ground-texture",
        type=float,
        nargs="?",
        const=0.5,
        default=0.0,
        metavar="METRES",
        help=(
            "bake the terrain decals (roads, aprons, markings) into the ground's "
            "colour, METRES a pixel (default 0.5 when given without a size), in "
            "tiles of at most 4096 pixels"
        ),
    )
    p.add_argument(
        "--navmesh",
        action="store_true",
        help=(
            "add the soldiers' walkable surfaces from the level's navigation mesh "
            "as the part nav:walkable"
        ),
    )
    p.add_argument(
        "--by-mesh",
        action="store_true",
        help=(
            "for finding what a part is: one part per source mesh and material, "
            "named '<part> | <mesh> | <material>' (a much larger file)"
        ),
    )
    p.add_argument(
        "--ground-spacing",
        type=float,
        default=4.0,
        metavar="METRES",
        help="the terrain heightfield's finest spacing (default 4; 0 leaves it out)",
    )
    p.add_argument(
        "--skip",
        action="append",
        default=None,
        metavar="TEXT",
        help="leave out static model groups whose partition name contains TEXT (repeatable)",
    )

    args = parser.parse_args(argv)

    if args.verb == "course":
        return _course(args)
    if args.verb == "courses":
        return _courses(args)
    if args.verb == "levels":
        return _levels(args)
    if args.verb == "level":
        return _level(args)

    if not args.path.exists():
        print(f"no such file: {args.path}", file=sys.stderr)
        return 2

    if args.verb == "identify":
        print(_identify(args.path))
        return 0

    if args.verb in ("list", "extract"):
        try:
            archive = _open_archive(args.path, args.key)
        except BadKey as exc:
            print(exc, file=sys.stderr)
            return 2
        except _reader_errors() as exc:
            print(exc, file=sys.stderr)
            return 1
        try:
            return _list(archive, args) if args.verb == "list" else _extract(archive, args)
        except _reader_errors() as exc:
            print(exc, file=sys.stderr)
            return 1
        finally:
            archive.close()

    if args.verb == "terrain":
        return _terrain(args)

    if args.verb == "meshes":
        from .unity import read_serialized
        from .unity_mesh import read_mesh

        container = read_serialized(args.path)
        meshes = container.of_class("Mesh")
        print(f"{len(meshes)} meshes in {args.path.name}")
        shown = 0
        for obj in meshes:
            if shown >= args.limit:
                break
            try:
                mesh = read_mesh(container, obj)
            except Exception as exc:  # noqa: BLE001 - reported, not swallowed
                print(f"  [{obj.path_id}] could not be read: {exc}")
                shown += 1
                continue
            check = "ok" if mesh.aabb_matches() else "BOUNDS DISAGREE"
            print(
                f"  {mesh.name[:40]:<40} {len(mesh.vertices):>8,} verts "
                f"{len(mesh.triangles):>8,} tris  {check}"
            )
            shown += 1
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
