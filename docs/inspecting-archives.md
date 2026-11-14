---
title: Inspecting archives
nav_order: 3
---

# Inspecting archives: `identify`, `list`, `extract`, `meshes`

Before exporting anything from an unfamiliar game, look at what it ships.
These four verbs read a file and tell you what it is and what it holds; they
write nothing except the one entry you ask `extract` for.

![identify, list and extract run on a small zip](assets/img/inspect-archives.svg)

*A run on a synthetic zip laid out like a BeamNG.drive level.*

## Step by step

1. **Ask what the file is.** `identify` reads the bytes, not the extension:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   It names the format (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle or
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` or
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), its version, how many entries it
   holds, and whether it is encrypted.

2. **List what is inside.** `list` prints one line per entry: size, compression,
   path. Narrow it with `--filter`, cap it with `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Take one entry out.** `extract` writes one entry, by the path `list`
   printed (or `#12`, by number, in a `.minizip` without names):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` lists and checks the meshes in a `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Options

| Verb | Option | Meaning |
|---|---|---|
| `identify` | `<file>` | any file |
| `list` | `<archive>` | `.pak`, `.utoc` (or the `.ucas` beside it), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | only paths containing TEXT |
| | `--limit N` | at most N lines |
| | `--key HEX` | an AES-256 key (64 hex digits) you already hold; only an encrypted `.pak` needs it |
| `extract` | `<archive> <path>` | the archive and the entry's path as `list` prints it |
| | `--out FILE` | where to write it (default: the entry's file name) |
| | `--key HEX` | as for `list` |
| `meshes` | `<file>`, `--limit N` | a Unity `SerializedFile`; at most N meshes |

The tool ships no keys and recovers none: an encrypted archive opens only with
a key you pass. A file it cannot read is refused in one line with exit code 1.
Every verb and exit code is on [Commands](commands.md); how each format is
read is under [Archive readers](archive-readers.md).
