---
title: Oodle
parent: Archive readers
nav_order: 3
---

# Oodle: found, not bundled

Most shipped Unreal content, and some Frostbite payloads, are compressed with
**Oodle** (RAD Game Tools, now Epic). Oodle is proprietary. There is no
redistributable build and no Python implementation, and `oo2core_*.dll` is
licensed to the product that ships it. So this tool **finds a copy already on your
machine and loads it**. It never carries one. FModel and UModel work the same
way.

Source: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Where it looks

The first file that exists wins, in this order:

1. An explicit path passed by the caller (Python API).
2. `HEAT3D_OODLE`: a path to the DLL, or a folder that holds one.
3. A shallow search, one level deep, of
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - every Steam library's `steamapps\common`

   For each child folder `<game>`, it checks `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` and
   `<game>\Engine\Binaries\Win64`.

File names tried, newest first: `oo2core_9_win64.dll` down to
`oo2core_3_win64.dll`. The format is backward compatible, so an older library
usually still works.

The search is deliberately **not** a recursive scan of every drive, which would
take minutes. If it finds nothing, set `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

A folder works as well as the file itself: the DLL names above are tried inside it.

An Unreal Engine install carries one under `Engine\Binaries\ThirdParty\Oodle`,
which is the tidiest source for a developer. Many games ship one beside their
executable. Unreal 5 games often link Oodle statically and ship no DLL, so the
copy found may belong to a different game than the archive being read. The
format is the same either way.

## How it is called

`OodleLZ_Decompress` is called through `ctypes` with the expected output length
(the archive index always knows it, and Oodle cannot infer it), fuzz-safe
decoding on (the input is untrusted), no CRC check (the pak's own SHA-1 already
covers the bytes), and unthreaded. A result of the wrong length is an error. The
library is loaded once per run.

## When there is none

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

An entry that cannot be decompressed is an error, never plausible rubbish.

The loader is Windows-only (it looks for `*_win64.dll`). Linux and macOS
libraries are not searched for.
