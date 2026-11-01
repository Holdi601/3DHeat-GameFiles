---
title: Unity
parent: Archive readers
nav_order: 4
---

# Unity: `SerializedFile`, bundles, meshes

**Lists objects and decodes meshes** of Unity `SerializedFile` format 22 and
later (Unity 2020 through 6000), and opens `UnityFS` bundles. There is no Unity
course export.

Sources: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Commands: `identify` (containers and bundles), `meshes` (bare containers only).

## The container

Unity ships a level as serialised object graphs: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*`, and asset bundles. Each
holds a table of objects tagged with a class id.

The header is where reading goes wrong quietly. The first sixteen bytes are four
big-endian `uint32`s kept for compatibility. In format 22, three of them are zero,
and the real values follow because a file may exceed 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

The second `metadata size` is a `uint32` between two `int64`s. Assuming all three
are 64-bit puts the version string four bytes late. It still decodes to something
string-shaped and sends everything after it astray. The header is big-endian.
Everything after it follows the endianness byte (0, little-endian, on every
desktop build).

After the header: the engine version string, the platform, the type-tree flag, the
type table (class id per type), the object table (path id, offset, size, type),
and the externals (other files a pointer can refer to).

| Case | Result |
|---|---|
| format 22-30 | read |
| format 9-21 (before Unity 2020) | refused: the offsets are in the legacy header, and no file at hand used it |
| outside 9-30 | refused |
| type tree embedded (editor builds) | refused: shipped builds do not embed one, and the editor path is not implemented |
| a bundle passed where a container is expected | refused, with a pointer to the bundle reader |

There is **no general deserialiser**. Shipped builds carry no type tree, because
the schema is compiled into the player, so each class has to be parsed against a
layout known for its version. Only `Mesh` is decoded. Other classes are reported
by name and count (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`,
`Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; others as `class<id>`).

**Verified** across 12 installed games and 12 million objects: the object table
has to tile the data section exactly, with no overlaps, nothing but alignment
padding between objects, and the last object ending on the final byte of the
file. A header misread cannot produce that. The installed-game test repeats it on
up to six `resources.assets` / `sharedassets0.assets` files found in
`*_Data` folders.

## Bundles (`UnityFS`)

A bundle is a compressed container of SerializedFiles. The block list and
directory are compressed too. The method is in the low six bits of a flags word:
0 stored, 1 LZMA (Unity's 5-byte header with the size spliced in), 2 and 3 LZ4 /
LZ4HC. Format 7 and later align the header to 16 bytes. Flag `0x80` puts the
directory at the end of the file. `UnityWeb`, `UnityRaw` and `UnityArchive`
(pre-5.3) are recognised but not read.

## Meshes

`read_mesh` decodes a `Mesh` object to positions, normals, the first UV set and
triangles, in the order Unity 2019+ writes them: name, submeshes, blend shapes
(skipped), bind poses and bone data (skipped), the compression and readability
flags, the index buffer, the vertex channels and vertex data, the compressed mesh
block, the local bounding box, and the streaming info.

- **External vertices.** Most shipped geometry lives in a `.resS` file beside the
  container. The tool reads it from the container's folder (only the file name of
  the stored `archive:/...` path is used). A missing `.resS` is an error, not an
  empty mesh.
- **Streams and channels.** Channels say which stream, offset, format and
  dimension each attribute has. Streams are packed one after another, each padded
  to 16 bytes, so a stream's start is accumulated from the strides before it.
  Formats: float32, float16, unorm/snorm 8 and 16 (normalised), and plain
  integers.
- **Topology.** Only triangles (topology 0). Strips, quads and lines are refused,
  because a wrong conversion looks like real geometry.
- **Compressed meshes** (quantised deltas) are refused: "mesh '...' is stored
  compressed; that encoding is not implemented".

### The self-check

Reading a struct in the wrong order does not raise. It yields plausible numbers.
So every decoded mesh is checked against the **bounding box Unity stored for it**,
computed by the editor from the real vertices. `aabb_matches()` passes when the
decoded box's corners are within 2% of the stored box's size. `meshes` prints `ok`
or `BOUNDS DISAGREE` on every line.

**Verified:** 820 meshes across four games decode with their bounds agreeing. The
installed-game test repeats the check on the installed containers.

## Not implemented

- Pre-2020 formats.
- Compressed meshes.
- Any class other than `Mesh`: no scene graph, transforms or materials, so
  meshes are in their own local space.
- `meshes` on a bundle. The bundle reader exists in Python
  (`UnityBundle.serialized_files()`), but the command takes a bare container.
