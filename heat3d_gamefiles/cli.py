"""
Command line for the game-file readers.

Verbs in the order the questions come up: what engine is this, what is inside,
and give me that. Everything else - which mesh is the level, how to decimate it
- belongs to the viewer's own import, not here.

    python -m heat3d_gamefiles identify <path>
    python -m heat3d_gamefiles list     <archive> [--filter text] [--limit n]
    python -m heat3d_gamefiles extract  <archive> <path inside> [--out file]
    python -m heat3d_gamefiles meshes   <unity .assets> [--limit n]
    python -m heat3d_gamefiles ue-maps / ue-map   (Unreal World Partition levels)

The file is whatever the game ships, and `identify` does not require knowing
which: an Unreal `.pak` or IoStore `.utoc`, a Unity `.assets` or bundle, a
Source 2 `.vpk`, a zip. `list` and `extract` take the archives among them.

Each game's own reader lives in its own repository and is run as a command
(external.py): `course` (Forza, BeamNG.drive and Assetto Corsa Rally laps),
`courses`, `races`, `cars` and `terrain` (heat3d-forza-maps), `levels` and
`level` (heat3d-battlefield-maps), `enfusion-worlds` and `enfusion-world`
(heat3d-reforger-maps) keep working here by running that tool with the same
arguments; `identify`, `list` and `extract` ask it for the files that are its
game's own (a ForzaTech `.minizip` or model, a Frostbite `.toc`, a BeamNG
`.cdae` or `.ter`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import levelshome


def _identify(path: Path) -> str:
    """Name the container format, by reading it rather than by extension."""
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
        lines.append("    holds      " + ", ".join(f"{n} x {k}" for k, n in top))
        return "\n".join(lines)
    except UnsupportedUnity:
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

    # The games' own formats are read by their own tools (external.py).
    from .external import identify as identify_elsewhere

    told = identify_elsewhere(path)
    if told is not None:
        return told
    lines.append("  not a format this tool reads (nor an installed game tool)")
    return "\n".join(lines)

def _head(path: Path, size: int) -> bytes:
    with path.open("rb") as handle:
        return handle.read(size)


def _identify_by_magic(path: Path) -> list[str] | None:
    """An IoStore table of contents or partition, a `.minizip`, a zip; else None."""
    from .iostore import MAGIC as IOSTORE_MAGIC

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
        # Forza's archive: its tool says what is in it.
        from .external import TOOLS

        done = TOOLS["forza"].run(["identify", str(path.resolve())], capture=True)
        if done is not None and done.returncode == 0:
            return done.stdout.rstrip().splitlines()[1:] or ["  ForzaTech .minizip archive"]
        return ["  ForzaTech .minizip archive", "    " + (TOOLS["forza"].missing() if done is None else done.stderr.strip())]
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
        lines.append("    holds      " + ", ".join(f"{n} x {k}" for k, n in kinds.most_common(6)))
    # BeamNG ships one zip per level, everything in it under `levels/<name>/`.
    levels = sorted({n.split("/")[1] for n in names if n.lower().startswith("levels/") and n.count("/") >= 2})
    if levels:
        lines.append(f"    levels     {', '.join(levels[:6])} (laid out as a BeamNG.drive level)")
    return lines


#: What a zip begins with: a local file header, or the end record of an empty one.
_ZIP_MAGIC = (b"PK\x03\x04", b"PK\x05\x06")
#: A ForzaTech `.minizip`, which the Forza tool reads.
MINIZIP_MAGIC = b"PGZP"

#: What `list` and `extract` open, for the message when a file is none of them.
_ARCHIVES = "an Unreal .pak or IoStore .utoc, a Source 2 .vpk, or a zip (a ForzaTech .minizip through heat3d-forza-maps)"


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
    from .oodle import OodleUnavailable
    from .pak import EncryptedPak, UnsupportedPak
    from .vpk import UnsupportedVpk

    return (
        ArchiveError,
        UnsupportedPak,
        EncryptedPak,
        UnsupportedVpk,
        IoStoreError,
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
    from .pak import PAK_MAGIC, PakArchive
    from .vpk import VPK_MAGIC, VpkArchive

    aes = _aes_key(key)
    head = _head(path, 16)
    if head == IOSTORE_MAGIC:
        return _IoStoreListing(path)
    if path.suffix.lower() == ".ucas" and path.with_suffix(".utoc").exists():
        # A partition has no header; its table of contents is what opens it.
        return _IoStoreListing(path.with_suffix(".utoc"))
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


#: A lap's game -> the tool that exports its course (Forza's is the default).
_COURSE_TOOLS = {"beamng": "beamng", "acrally": "acrally", "assetto-corsa-rally": "acrally"}

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


def _course(argv: list[str]) -> int:
    """
    A lap in, the ground around it out - by the lap's game's own tool, run with
    the same arguments. The lap says which game it is from; `--game` overrides.
    """
    from .external import delegate
    from .lapinput import UnreadableLap, read

    pick = argparse.ArgumentParser(add_help=False)
    pick.add_argument("lap", nargs="?")
    pick.add_argument("--game", default=None)
    known, _rest = pick.parse_known_args(argv[1:])
    game = known.game
    if known.lap and not game and not {"-h", "--help"} & set(argv):
        try:
            game = read(known.lap).game
        except UnreadableLap as exc:
            print(exc, file=sys.stderr)
            return 1
    game = (game or "forza").lower()
    if game.startswith("forza"):
        return delegate("forza", argv)
    if game in _COURSE_TOOLS:
        return delegate(_COURSE_TOOLS[game], argv)
    print(_no_course(game), file=sys.stderr)
    return 1


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
    from .external import VERBS, delegate

    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in VERBS:
        return delegate(VERBS[argv[0]], argv)
    if argv and argv[0] == "course":
        return _course(argv)

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

    # Run by the game's own tool with the same arguments (external.py); `<verb> --help` shows its options.
    for verb, help_text in (
        ("course", "export the ground around a lap (by the Forza, BeamNG.drive or AC Rally tool)"),
        ("courses", "every course in a recorded lap library (heat3d-forza-maps)"),
        ("races", "every race an installed Forza defines (heat3d-forza-maps)"),
        ("cars", "every car of an installed Forza at low detail (heat3d-forza-maps)"),
        ("terrain", "a piece of Forza terrain by world coordinates (heat3d-forza-maps)"),
        ("levels", "the levels of an installed Frostbite game (heat3d-battlefield-maps)"),
        ("level", "a Frostbite level as one .glb (heat3d-battlefield-maps)"),
        ("enfusion-worlds", "the worlds of an installed Arma Reforger (heat3d-reforger-maps)"),
        ("enfusion-world", "an Arma Reforger world as one .glb (heat3d-reforger-maps)"),
    ):
        sub.add_parser(verb, help=help_text, add_help=False)

    from . import unreallevel

    unreallevel.add_verbs(sub)

    args = parser.parse_args(argv)

    if args.verb in ("ue-maps", "ue-map"):
        return unreallevel.run(args)

    if not args.path.exists():
        print(f"no such file: {args.path}", file=sys.stderr)
        return 2

    if args.verb == "identify":
        print(_identify(args.path))
        return 0

    if args.verb in ("list", "extract"):
        if _head(args.path, 4) == MINIZIP_MAGIC:
            return delegate("forza", argv)
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
