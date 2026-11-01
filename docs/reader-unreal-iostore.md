---
title: Unreal 5 IoStore
parent: Archive readers
nav_order: 2
---

# Unreal 5 IoStore

Unreal 5 ships most content in **IoStore** containers: a `.utoc` table of
contents and the `.ucas` data it indexes. A `.pak` is still there, but it holds
little more than a footer. The readers here go from the container down to
geometry and pixels, as far as a course needs. They were built and checked on
Assetto Corsa Rally (Unreal 5.6.1, modified) and are reached through the
[Assetto Corsa Rally](course-assetto-corsa-rally.md) course export, and
`identify`, `list` and `extract` take a `.utoc` (or the `.ucas` beside it): the
files its directory names, by their path under the mount point. A container
without a directory index names no files and is not listed.

| Layer | Module |
|---|---|
| containers and the store | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| cooked "zen" packages | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| unversioned property data | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| static meshes | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| textures and virtual textures | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Containers (`.utoc`, `.ucas`)

The table of contents, version 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Versions older than 5 are refused. Only version 8 has been checked on real
  files.
- **Encrypted containers are refused**: "<file> is encrypted. This tool holds no
  keys and recovers none." No key can be passed in for IoStore.
- Block methods: stored, `oodle` (through [Oodle](reader-oodle.md)), `zlib`,
  `lz4`. Anything else is refused.
- Partitions beyond the first live in `<name>_s<n>.ucas`.

The **store** opens every `.utoc` in the game's `Paks` folder and indexes every
package path, case-insensitively. Containers that fail to open are skipped.
`global.utoc` provides the script objects (C++ classes). A package's bulk data
(`.ubulk`) is found as the chunk with the same id and type `BULK_DATA`, in
whichever container holds it.

Checked: 54 containers, 47,246 package paths.

## Zen packages

A cooked package is a header (names, imports, exports, export bundles, dependency
tables, imported package names) followed by each export's serialised data.
Objects refer to one another by a 64-bit `FPackageObjectIndex` whose top two bits
say what it is: an export of this package, a script object, an import from
another package (which package, and the export by a hash of its path), or null.

- The summary layout changed in 5.3 (dependency bundles and imported package
  names) and again in 5.6 (two more offsets). Both layouts are tried, and the one
  whose name table parses is kept, so the version does not need to be known.
- **Versioned** (uncooked-style) packages are refused.
- Imported package names carry a number. A package `_Terrain` numbered 1 is the
  file `_Terrain_0`.
- `/Game/...` names map onto the project's `Content` folder in the store.
- References are followed across packages by matching the export's public hash.

Checked: every cell of every stage opens.

## Unversioned properties

Cooked Unreal 5 exports do not name their properties. An export starts with a
header of runs, "skip so many slots, then so many present", and a mask saying
which present ones are zero and carry no bytes. The values follow in the class's
property order. Reading that needs each class's **schema**: its property list, in
exactly the order the engine builds it (own properties first, then the parent's,
one slot per static-array element, editor-only properties left out).

Schemas are embedded for the classes a course needs:

| Class | Chain |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | the ISM chains (present, but not used by the course export, because this build rearranged them) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

They also cover the structs these hold (`FBodyInstance`, collision responses and
others). Value types are read by encoding: fixed-size numbers and vectors
(`FVector`, `FRotator` as doubles, `FTransform`...), `FName`, enums (one byte),
object references (`i32` package index), soft object paths, arrays, nested
structs, and multicast delegates (skipped).

The schemas are **property names and types only**, derived from the Unreal
Engine 5.6.1 headers (which Epic makes available to anyone with a linked
account). No engine code is included. This build has **two more slots in
`UPrimitiveComponent`** than the headers, and **one more in the virtual texture
volume**, found from the data and marked `(unknown)`. A value present in one of
those slots is an error, not a guess. A slot past the end of a schema, or an
unknown type, raises `PropertyError`.

Checked: 32,310 static-mesh and 10,906 scene components across 16 levels decode,
each ending exactly at its class's fixed native tail. A game patch can move slots.
The reader then raises, and the course reports how many components failed.

## Static meshes

A `UStaticMesh` export is its properties followed by native data. The properties
are not needed for geometry and are not read. The native part is found by its
fixed start: a zero GUID flag, two bytes of strip flags, `bCooked = 1`, and the
index of the mesh's own `BodySetup` export. It is then read in the order
`UStaticMesh::Serialize` and `FStaticMeshRenderData::Serialize` write it for a
**cooked, non-Nanite** mesh:

- up to 16 levels of detail, each with its sections (material, first index,
  triangle count), bounds, and when **inlined**: the position buffer (float32
  x 3), tangents, UVs (all channels, half or full precision), colours, and the
  index buffer (16- or 32-bit);
- what follows (reversed and depth-only index buffers, ray-tracing data,
  area-weighted samplers) is stepped over to reach the next level.

A level that is not stored inline ends the list. A mesh with none is refused.
Positions are Unreal's: centimetres, X forward, Y right, Z up.

Checked: 296 of 300 random meshes decode (the other four are skeletal), and a road
tile's decoded extent matches the bounds it stores.

## Textures

A `Texture2D` export is its properties and then its cooked platform data: the
pixel format name, the size, and a table of mip levels, each pointing into the
package's **bulk data map** (offset, size, flags; inline in the export when flag
`0x40` is set, else in the `.ubulk`). The platform data is found by its own shape,
not by skipping the properties, so the texture class's property layout does not
matter. The first mip no larger than the requested size is decoded.

| Unreal format | Decoded as |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bit RGBA |
| `PF_G8` | 8-bit grey |

Checked: a 4096 px DXT5 satellite image whose thirteen levels are exactly the
bulk entries' sizes.

## Streaming virtual textures

A baked `VirtualTexture2D` is square tiles with a border, per level of detail,
addressed by **Morton code** (x in the even bits), stored in chunks of the
package's bulk data. The layout is read as `FVirtualTextureBuiltData::Serialize`
writes it in Unreal 5.6: layers, tile size, border, per-mip tile address tables,
layer formats, and chunk *n* as bulk entry *n*. A region of the texture is
assembled tile by tile, borders removed, from the level whose resolution is
nearest the wanted size. Only the first layer is read, and only in the formats
above.

Checked: the first chunk of a stage's 16,384 px base colour is
4 + 4,096 x 34,848 bytes, its 64 x 64 tiles of 256 px accounted for to the byte.
