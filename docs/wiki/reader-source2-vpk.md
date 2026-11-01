
# Source 2 `.vpk`

**Lists and extracts** Valve's VPK archives, versions 1 and 2, including split
archives and data stored inside the directory file. Every entry can be checked
against its own CRC. This is the one container format here whose vendor documents
it. Games: Counter-Strike 2, Dota 2, Half-Life: Alyx, and others on Source 2.

Source: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Commands: `identify`, `list`, `extract`.

## Layout

```
u32 magic 0x55AA1234, u32 version (1 or 2), u32 tree size
  (version 2: 16 more header bytes; header 12 or 28 bytes)
directory tree:
  extension        "vmdl_c", then "vtex_c", ..., then ""
    path           "maps/example_map", then ""
      file name    "world_layer0", then ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Three nested loops, each ending on an empty string, so a reader that expects
  a count finds none. Paths are stored once per group and reassembled from all
  three parts. A single space means "no folder" or "no extension".
- Every record ends with `0xFFFF`. That is checked, so a reader that has lost its
  place stops at once ("the directory is not being read at the right offset").
- **Split archives:** `pak01_dir.vpk` holds the directory, and the data sits in
  `pak01_000.vpk`, `pak01_001.vpk`... selected by the entry's archive index.
- **Archive index `0x7FFF`** means the bytes are in the directory file itself,
  after the tree. Reading it as a real index sends a reader looking for
  `pak01_32767.vpk`.
- **Preload:** small files are stored whole in the directory. A length of 0 is
  then not an error.

## Commands

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` prints the version, the entry count and the first `.nav` file. `list`
shows every entry as `stored`, because VPK does not compress. `extract` writes
the bytes without checking the CRC. In Python, `VpkArchive(path).verify(name)`
compares an entry's bytes with the CRC the directory recorded.

## The navigation mesh

A map ships its **navigation mesh** (`maps/<map>.nav`) beside the compiled
geometry. For a heatmap of player positions it is the more useful of the two by a
wide margin, because the nav mesh *is* the walkable floor, already computed and a
thousandth of the size. The installed-game test checks that a shipped map's
`.nav` starts with the Source navigation magic `CE FA ED FE`.

## Verified

200 of 200 entries sampled across Counter-Strike 2's shipped maps came back
byte-exact against their CRC. All 43 map archives parse, 22,637 entries in total.
The installed-game tests repeat the CRC check on 25 random entries from each of
up to four map archives.

## Not implemented

- Decoding Source 2's compiled assets (`.vmdl_c`, `.vtex_c`). They are chunked
  binaries of their own, the same kind of job as the Unreal and Frostbite mesh
  formats. The separate 3DHeat CS2 tool handles CS2 map geometry.
- Decoding the CS2 nav mesh. Its format is version 36 and differs from the widely
  documented Source 1 one. Its bytes are structured rather than compressed
  (entropy 6.2, 31% zeroes), but only 3% of its words read as coordinates, so the
  layout is not the obvious one and has not been worked out yet.
