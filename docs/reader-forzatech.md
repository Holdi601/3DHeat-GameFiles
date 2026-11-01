---
title: ForzaTech
parent: Archive readers
nav_order: 7
---

# ForzaTech: `.minizip`, `.modelbin`, swatches, placements

Forza Horizon runs on ForzaTech, Turn 10's own engine. These readers take a track
from its archives down to positioned, textured triangles. They are reached
through `course`, `courses` and `terrain` (see
[Forza Horizon](course-forza-horizon.md)). `identify` recognises a `.minizip`
and a bare `.modelbin`, and `list` and `extract` take a `.minizip`, by the names
in the `ChunkContentsMiniZip<n>.txt` beside it or by entry number (`#12`).

| Format | Module |
|---|---|
| `.minizip` archives and their name lists | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin` models and terrain | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb` texture swatches | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo` placement files | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` and material texture hashes | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| terrain tiles by place | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza also keeps much of its content in ordinary ZIP archives under `media\`.
Python's `zipfile` opens those, and `forzatech.models_in_archive()` lists their
`.modelbin` entries. The track geometry is in the `.minizip` archives.

## `.minizip`: an archive with no names

A track ships four `GeoChunk<n>.minizip` archives, tens of gigabytes each for an
open-world map, with hundreds of thousands of entries. **The archives store no
names at all**: no name table and no per-entry header, only an ordinal. The names
are in `ChunkContentsMiniZip<n>.txt` beside each archive, one line per entry in
entry order (`<build path>zipcache\pc\<path>|<bundle>`). That pairing is the only
way to ask for a file. Everything up to `zipcache\pc\` is dropped, and lookups
ignore case.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Three details in the index still produce output when read wrong. The reader gets
all three right:

| Detail | What a careless reader does | What it looks like |
|---|---|---|
| the segment base is **64-bit** | reads it as u32 plus padding | correct for the first 4 GB, then noise of the right length |
| the base is **8-byte aligned** | ignores the padding word after the bundle table | in archives with an even bundle count, every entry claims a codec that does not exist |
| an entry's stored length is the gap to the next entry (or the next segment's base) **minus its padding** (flag bits 12-13) | uses the whole gap | LZ4 refuses the block outright |

Codecs are the low five bits of the flags: `0x00` stored, `0x08` raw deflate,
`0x1F` LZ4 block. Any other is refused. Every entry must unpack to exactly the
size it declares, or it is refused. The index (about 5 MB) is read once, and
payloads are read by seeking.

The header is checked: magic, a 32-byte header, and a segment count that matches
`ceil(entries / per segment)`.

**Verified:** 14,541 entries sampled across all four archives of a map, each
unpacking to exactly its declared length under all three codecs.

## `.modelbin`: the chunk container

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- The declared file size must equal the real size.
- The **chain**: each chunk starts where the previous one ended, rounded up to 4
  bytes. Nothing in the file states this, so it is evidence: a record read at the
  wrong stride does not produce it. It held for all 252 models sampled.
- A `PGZP` file given to the model reader is named as "a ForzaTech .minizip
  archive, not a model" and pointed at `minizip.py`, rather than rejected blankly.

Geometry comes from these chunks:

| Chunk | Holds |
|---|---|
| `VLay` | a vertex layout: attribute names, then elements (u16 name index, u16 channel, buffer, DXGI format, offset); the element count is a u16 |
| `VerB` | a vertex buffer behind a 16-byte header (count, size, u16 stride, u16 attributes, format) |
| `IndB` | the index buffer, same header |
| `Mesh` | one submesh: material, level-of-detail mask, index range, layout, buffer, stride, variant table, and a position box at the end |
| `MatI` | a material instance: its `.materialbin` path and texture hashes |

### Positions and the box

Positions are `R16G16B16A16_SNORM` (format 13): four signed shorts per vertex.
`position = short / 32767 * scale + bias`, where scale and bias are the last 32
bytes of the `Mesh` chunk (two float4s). The bias is in **the game's world
coordinates**, so a terrain tile lands where the game puts it with no instance
transform. That is why a lap of telemetry is enough to ask for a piece of map.
Every submesh of a model carries the same box (checked across 860 of them).

### The vertex layout

One position buffer covers every vertex. The other attributes are split into
consecutive vertex groups, each with its own buffer and its own layout: road near
a junction carries three UV sets and two tangents, the bank beside it only a
normal. Every non-position attribute is four bytes. Which layout describes which
buffer is taken from the submeshes that draw from it, because layouts and buffers
are not in the same order (same, rotated by one, or permuted, depending on the
model).

| DXGI format | Code | Used for |
|---|---|---|
| R16G16B16A16_SNORM | 13 | position (the fourth short is the normal's x) |
| R16G16_SNORM | 37 | normal y, z |
| R16G16_UNORM | 35 | a UV pair (channel = which set) |
| R8G8B8A8_UNORM | 28 | colour or blend weights |
| R10G10B10A2_UNORM | 24 | tangent (not decoded) |
| R16_UINT | 57 | indices |

**The normal is split.** `NORMAL` holds y and z. The x is the position's fourth
short, which looked like padding. Over 690,000 terrain vertices it correlates
+0.92 with the x of the triangle normal and with nothing else. With it, 96% of
sloped-ground vertices are within 18° of the computed normal. Every two-component
encoding tried without it (octahedral in all 48 arrangements among them) got y
and z right and x wrong.

Other position or index formats are **refused** ("only 13 (four shorts, scaled) is
implemented"; "only unsigned shorts are implemented").

### Submeshes

A `Mesh` record is 238 bytes in the standard form. Longer ones carry a longer
material **variant** table at the front, 238 + 8 x count - 4 bytes, and every
field after it moves back by exactly that much. Shorter ones (218 bytes, some
terrain) keep the offsets. Each variant entry is
`u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. The
level-of-detail mask is a u16, one bit per level from bit 1.

Nothing is trusted alone. The index ranges must tile the index buffer exactly,
each `index count` must equal 3 x `triangles`, and the stride a submesh names
must be its buffer's. A table that fails is refused whole, because labelling
triangles from misread fields is worse than not labelling them. Across 5,350
sampled submeshes, every one whose buffer index is in range passes.

### Materials and texture hashes

A `MatI` names its material by a `Game:...\x.materialbin` path, found by
searching the chunk. Its textures are `u32 slot, u32, u32 hash` records, 33 bytes
apart and unaligned, so the chunk is searched at every byte offset for words that
are known texture hashes. Those come from the track's `AssetManifest.xml`
(`<Texture Source="...\name.swatch" SourceHash="...">`, read up to
`</Textures>`). Slot `0x88B483AA` is the standard shader's base colour. How the
colour texture is then chosen is on
[Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: texture swatches

A swatch is the same `burG` container as a model: a 96-byte `HCXT` header at byte
44, then one chunk of pixels. The header holds the texture's GUID (the one in its
file name), width and height, the mip count, and the **format code at byte 72**
(ForzaTech's own numbering). Byte 84 holds the pixel byte count.

| Code | Format | Identified as |
|---|---|---|
| 0 | BC1, half a byte a pixel | decodes to a red and white kerb (noise under BC4) |
| 9 | BC7, one byte a pixel | decodes to a terrain tile with the circuit visible |
| 13 | RGBA8, four bytes a pixel | plain |
| other | refused | "texture format N has not been identified; refusing to guess" |

Formats were identified by decoding real files every way the payload size
allows. Byte 47, which an earlier version took for the format, is 4 in all 3,000
textures sampled. Only the top mip of a file is decoded. Each resolution is its
own entry, `<name>_<guid>_quality<n>.pb`, quality 1 smallest to 5 largest. For
terrain maps the two largest are in a different archive from the rest. Decoding
goes through Pillow's BCn decoder, via a generated DDS header.

## Placement files (.pgeo)

One file per category per spatial cell:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. The path alone
gives the cell's square and category, so files can be filtered without opening
them.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

How each field was decided:

| Field | Decided by |
|---|---|
| position is 16.16 fixed point, not a fraction of the box | consecutive guardrails are exactly 4.000 m apart (the model's length) |
| sign-magnitude, not two's complement | two's complement put negative coordinates tens of kilometres off the map; with bit 31 as the sign, every record of every category sampled lands inside its file's box |
| the vectors are the model's own axes | the end of every guardrail lands on the start of the next: 93.5% within 5 cm, median 0.000 m |
| byte 60 is the variant | a billboard's five copies read 0, 2, 2, 3, 4 while every guardrail reads 0 |

Only names ending in `_3D` are model records. The variant table before them lists
names without the suffix, and read as records those land at infinity. A candidate
record is accepted only if its count fits in the file, and instances with
non-finite numbers are dropped.

## Not implemented

- Vertex and index formats other than those above (refused).
- Texture formats other than 0, 9, 13 (refused).
- Tangents (read past, not used).
- The terrain shader's material layers. The ground texture is an interpretation of the tile maps (see [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
