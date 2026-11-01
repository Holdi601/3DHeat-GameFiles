---
title: Unreal .pak
parent: Archive readers
nav_order: 1
---

# Unreal `.pak`

**Lists and extracts** Unreal 4.22-5.x `.pak` archives: versions 8, 9, 10, 11
and 12, Zlib, Gzip and Oodle compression, and encrypted archives when you supply
the AES key. It does not interpret what it extracts (`.uasset`, `.umap`).

Source: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Commands: `identify`, `list`, `extract` (see [Commands](commands.md)).

## Layout

The footer is at the end of the file and is found by searching the last 1,024
bytes for the magic `0x5A6F12E1`. Its field order matters:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

The encryption flag sits **before** the magic. Taking it from after the magic
lands on the "Z" of "Zlib". Then every archive reports itself encrypted and every
method name loses its first letter ("lib", "odle"), a quiet and plausible
failure. The version is the low byte, because "frozen index" builds set a high
bit.

The index holds the mount point, the path-hash index, the full directory index,
and a block of **encoded entries**: a bit-packed form where a flags word says
which numbers are 32-bit, the compression method (6 bits), whether the entry is
encrypted, the block count (16 bits) and the block size in units of 2,048
(6 bits). The all-ones block size is an escape: the real size follows as a u32
**before** the offset. In a 27 GB archive, reading it after the sizes shifted 7%
of entries by four bytes and gave them offsets in the exabytes.

Each entry's full record is repeated just before its payload, so the payload
begins after `8+8+8+20+4+1+4` bytes, plus `4 + 16 x blocks` when compressed.
Encrypted blocks are padded to 16 bytes.

## What it reads, and what it refuses

| Case | Result |
|---|---|
| versions 8-12 | read |
| any other version | `pak version N; this reader handles 8-12` (older versions store a flat record list, and there was no file to test against) |
| no footer magic | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index outside the file | refused: the footer did not parse as claimed |
| path-hash index only | refused: file names were hashed away at build time and cannot be recovered |
| entries in the index's overflow list (directory offset -1) | skipped, not faked |
| encrypted index, no key | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." On the command line, one line and exit code 1 |
| encrypted entry, no key | `EncryptedPak` on read |
| methods Zlib, Gzip, Oodle | decompressed (Oodle needs a library, see [Oodle](reader-oodle.md)) |
| any other method | `compression method '...' is not supported` |

## Keys

`--key` on `list` and `extract` takes an AES-256 key you already hold, as 64 hex
digits, with or without `0x`. Anything else is refused before the archive is
opened, with exit code 2. Decryption is AES-256-ECB through the
`cryptography` package. There is no code path that obtains a key: no bundled
keys, no search of executables, no memory reading. See
[Rules and licences](rules-and-licences.md).

## Verified

Against three shipped archives across two games: 178,809 entries, including one
archive of 27 GB holding 167,412 of them, matched by the SHA-1 Unreal writes
ahead of every payload. That hash covers the bytes as stored, so a match means
the index decode, the payload offset and every compressed block boundary were
right. The installed-game tests (`test_pak.py`) repeat this on up to four
unencrypted paks found under `steamapps\common\*\...\Content\Paks`. They check
that every entry's offset lies inside the file, and that the SHA-1 matches for a
random sample of 150 entries per archive.
