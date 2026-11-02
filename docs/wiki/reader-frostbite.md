
# Frostbite: `.toc`, `.cas`, bundles, meshes and levels

**Reads a Battlefield 6 level down to its terrain, its placed meshes and their
colour maps, and writes it as a `.glb`.** Frostbite games (Battlefield, Need for Speed, Dead Space) keep their
content in `.cas` blobs, described by `.toc` tables of contents. A level's table
says which bundles the level loads, the bundles name every asset, and the
assets say which mesh stands where.

Sources:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tables, packages, payloads),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundles and their manifests),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX partitions),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(heightfield),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(textures and materials),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(placement and export).
Commands: `identify`, `levels`, `level` (see [Commands](commands#levels-and-level-frostbite)).

Nothing here is documented by the game. Every layout below was read off the
files and then held against all of them, and each section says what the check
was. Where the Frosty modding tools describe older versions of a structure, the
field names follow theirs; no code was taken from them (see
[Rules and licences](rules-and-licences)).

## The header that looks encrypted and is not

| Magic (u32, little-endian) | Meaning | Handled |
|---|---|---|
| `0x00CED100` | plain: the tree starts immediately | read |
| `0x01CED100` | signed: a 556-byte signature, then the tree **in the clear** | read |
| `0x03CED100` | XOR-obfuscated, with the key in the file's own header | detected and declined |

The signed form is what current Battlefield ships. The high-entropy bytes after
the magic are a signature, not ciphertext.

## The DbObject tree

One recursive structure. Each field is a type byte (low five bits the type, bit 7
"anonymous"), an optional name, and a value. Containers carry their length as a
variable-length integer and end with a zero byte. `parse_toc` checks every
container's length, so a file that parses was understood. `layout.toc` is in
this form.

## Installation packages

Every location names the **installation package** its blob belongs to. Each
package numbers its blobs from `cas_01`, so the blob number alone is ambiguous as
soon as more than one package is installed, which is always.

- `layout.toc` lists the packages under `installManifest.installChunks`, each
  with a `persistentIndex` and an `installBundle` such as
  `Win32/installation/<package>`.
- The package's blobs are in that folder, under `Data` for the base game or
  under `Update/<pack>/Data` for what came later.
- A location record carries the full 32-bit `persistentIndex`: the low half of
  its first word holds the high half, the high half of its second word the low
  half; the low half of the second word is the blob number.

Check: all 3,328,654 locations in the 144 binary tables of an installation
resolve to a declared package and land inside the blob they name. An earlier
version took the first `cas_NN.cas` of the right number. A third of the
payloads it read then looked high-entropy and were taken for encryption. They
were the right offsets in the wrong file. Nothing found is encrypted.

## The level table

A level's table (`levels/<level>/<level>.toc`) is a section table: fifteen
big-endian header words, then sections laid end to end, whose offsets are both
stated and derivable from two counts.

| Section | Contents |
|---|---|
| bundles | a hash table (one word each), then a 16-byte record per bundle: key, `0x40000000` \| size, 0, offset |
| chunk hash table | one word per chunk |
| chunks | 16-byte id (the chunk's GUID **byte-reversed**), then a word: `0x80000000` \| 4 x the index of its location |
| locations | four big-endian words: package (split), blob, offset, size |

The chunk ids and the locations are **in different orders**. Reading them in
file order pairs each chunk with another chunk's bytes, which decode perfectly
well (mostly as sound) and so do not look wrong until a mesh comes out as noise.
Check: in a level of 73,875 chunks, the index words are a permutation of 0 to
73,874.

The bundles are stored inline after the section table. Each is nine big-endian
header words, then its entries: eight bytes of offset and size, preceded by
eight more naming package and blob when the entry's flag byte has its top bit
set. Check: on every bundle, the last entry ends exactly where the flag bytes
begin.

## Bundle manifests

A bundle's first entry is its manifest, stored uncompressed. It is the binary
bundle format of earlier Frostbite games with a new magic, `0xD68E799D`: counts,
SHA-1s, ebx and res records (name offset and size), res types, metadata and
ids, chunk GUIDs, strings. The rest of the bundle's entries are the ebx, the res
and the chunks in that order. Check: the counts match the entries on every
bundle, and the strings start where the records end.

Resource types are hashes. `0x49B156D4` is MeshSet (every res of that type is
named `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` reads all of this for one level, in about two seconds: one
level has 43 bundles, 123,752 ebx, 40,179 res and 79,789 chunks.

## Payload blocks

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

A zero compressed size means stored, as long as it decompresses to.

| Method word | Codec |
|---|---|
| `0x0070`, `0x0071` | none |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle), from the game's own `oo2core` DLL) |
| other, with equal sizes | copied as stored |
| other | refused |

Read from the right package, every payload sampled decodes.

## EBX partitions

EBX holds everything that is not raw data. Each partition is a RIFF file:
`EBXD` (the data, aligned to 16), `EFIX` (partition GUID, type GUIDs and
signatures, instance, pointer, import and type-info offsets, imports, and the
array, boxed-value and string offsets), `EBXX` (the array table: offset, count,
hash, flags, element type). A pointer field is eight bytes: zero is null, an odd
value is import number `value >> 1`, anything else is relative to the field.

The **type library is not readable**. The game ships it in its initial file
system, which is encrypted, and this package does not touch it. Types are known
by GUID and signature, which every partition carries, and the few types the
level export needs were laid out from the data.

## MeshSet

A mesh is a MeshSet res (the description) and one chunk per level of detail (the
buffers).

| Part | Layout |
|---|---|
| prefix | four words: header size (176 or 192), level record size (176 to 188), section record size (368), 0 |
| header | bounding box; six i64 level offsets; mesh type at `0x6C` (rigid, skinned, composite); level and section counts at `0x9C` |
| level | sections at `+0x08`; five draw lists at `+0x14` (opaque, transparent, decal, depth only, shadow); index format `+0x54` (`0x21` u16, `0x2E` u32), index and vertex bytes; chunk GUID at `+0x74` |
| section | material name; vertex stride; triangles, first index, vertex offset (bytes), vertex count at `+0x20`; vertex declaration at `+0x64`: 16 x (usage, format, offset, stream), 16 stream strides, counts |
| chunk | the vertex buffer, then the index buffer. A section's streams follow one another; indices count from the section's first vertex |

Positions are usage 1, stream 0, offset 0, as four halves or three floats.
Only the opaque and transparent sections are drawn. Every section named
`..._shadow` is in the shadow list and only there, so the lists decide.

Check: of a level's 4,090 meshes, all 4,080 whose levels are stored in chunks
decode, 14,043 levels and 43,130 sections. 4,027 of them have 99% or more of
their vertices inside their declared box; the rest miss it by half-float
rounding. The first mesh decoded,
a crate, measures 1.08 by 0.75 by 0.87 metres, Y up, with its normals pointing
outwards.

## Placement

The content pipeline gathers the static objects of each sub-world into a
**static model group**: an array of members, one per mesh, each with its
instance transforms.

| Type (GUID, signature) | Layout |
|---|---|
| member `ad13064e…`, `0xF861A878` | 224 bytes: `+88` array of transforms, `+112` the object blueprint (import), `+160` the mesh asset (import) |
| transform `101dce06…`, `0x5E6D8C37` | 64 bytes: right, up, forward, translation, each a vec3 padded to 16 |

The mesh asset's partition is named like its MeshSet res, so the import's
partition GUID gives the mesh. A point lands at
`x·right + y·up + z·forward + translation`. The group's own transform was the
identity in all 41 groups of the two levels checked, and is not applied.

Check: in one level, 41,277 copies of 1,753 meshes in 19 groups, every member
resolving to a mesh; two copies in three have a rotation of determinant 1 to a
thousandth, the rest are scaled or mirrored. The type GUIDs and signatures are
the same in a second level. A game update that changes the layout changes the
signature, and the reader then finds nothing rather than misreading.

## Terrain

Source: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

The terrain is a TerrainStreamingTree res (type `0x22FE8AC8`) and the chunks it
names.

| Part | Layout |
|---|---|
| header | 34 bytes; the node count at 25 |
| raster trees | a type byte and a u32 length each, until a type byte `0xFF`. Type 0 is the heightfield: samples a side at +5 (265), height range at +21 (1,280 m), the terrain square in its first node record at +77 (8,192 m in the level checked). It holds node bounding boxes and a 16 x 16 min/max pyramid per node, not the heights |
| streaming nodes | the quadtree, depth first: chunk size and GUID; an optional second chunk; a flag byte (bit 0: the chunk starts with a height page); has-children. Children in the order (0,0), (1,0), (1,1), (0,1) |
| height page | the first 265 x 265 u16 of a flagged node's chunk, row by row; height = value x 1,280 / 65,535 m; columns along x, rows along z, from the node's low corner; a border of 4 samples, so 256 cells a node |

Each step was checked on its own:

- The node quadtree parse consumes the res to its last byte, with the declared
  529 nodes.
- Neighbouring nodes share their nine edge columns exactly, so the stride is 256.
- A child's samples at every other position equal its parent's exactly with a
  border of 4, and are 90 to 700 units off with any other border.
- The lowest word in the level decodes to the bounding box's lowest height to
  the centimetre (41.95 m).
- Of the eight ways the square could lie on the world, only x along x and z
  along z puts the placed objects on it: half of 3,000 copies within 2.2 m,
  against 11 m and more for every other way.

The placed objects then measure the result. The lowest point of each copy,
against the terrain under it (bilinear, from the finest node):

| Placed | Copies | Median distance | 90% within | Signed median |
|---|---|---|---|---|
| trees and bushes | 2,319 | 0.30 m | 0.81 m | -0.27 m |
| props | 20,227 | 1.54 m | 21 m | 0.00 m |
| rocks | 3,725 | 1.24 m | 17 m | -1.19 m |
| buildings | 9,198 | 6.72 m | 21 m | -0.74 m |
| all | 39,214 | 2.11 m | 19 m | -0.09 m |

Vegetation is placed on the ground and nowhere else, which makes it the
sharpest check: its origins sit a median 0.07 m from the surface. Buildings
spread widely because the category holds walls, floors and kit pieces of
multi-storey and underground structures. Shifting the terrain 64 m sideways
drops the share of copies within 0.5 m from 29% to 10%.

`level` draws the heightfield as `ground:terrain`, each part of it from the
finest node with heights there and no finer than `--ground-spacing` (4 m by
default: 3.7 million triangles for the level checked, whose finest nodes are
0.5 m). Pieces of different resolution meet with small steps; nothing stitches
them.

A node's chunk also holds 72 x 72 BC4 pages (masks and detail rasters,
continuous across nodes) and, in its second chunk, 136 x 136 or 68 x 68 BC7
colour pages. Those colour pages are not geographic: neighbouring pages do not
continue one another in any of the eight orientations (edge difference 29 grey
levels in all of them), so they are not used.

## Terrain layers and decals: what is known, not yet used

The game shades the terrain near a player by splatting tiling surface materials
and drawing decals (roads, asphalt patches, runway markings) over them. Neither
is in the export yet, which is why the ground colour is the backdrop map's. What
was established, so the next step starts from it:

**The layer list.** The terrain's `....layergraphs` res and its shader block
depot (`....layergraphs_shaderblockdepot`) describe a layer graph of 56 nodes.
The res lists them in order (each with a 16-byte id whose second half is the
depot's section key), and the depot's blocks name each node's textures: one
`_cv` colour map, `_nhs` and `_ao` maps per surface (sand, gravel, dirt road,
cracked concrete, rock, cliff, soil and a default), plus shared detail and noise
maps. The tiling scale of each surface was not found.

**The masks.** Raster tree 1 (pages of 72 x 72) holds, per layer, a quadtree of
33-byte records down to 64 m cells: the layer's id and hash, then the cell's box,
two bytes, and an 85-bit presence pyramid (1 + 4 + 16 + 64 bits, row-major; 98%
of records close as parent = OR of children). Up to 20 layers are present at a
node. A node's chunk holds BC4 pages of 72 x 72 after its height page, but they
do not map onto those layers one to one:

- besides one BC7 colour page and a small remainder, a node with 19 layers
  present has 38 or 39 pages, one with 20 has 40 to 43;
- the pages come in groups of four with related content;
- they are not weights: summed per pixel they range from 0 to over 1,000;
- a layer present in 18 of its node's 64 cells matches no page's occupancy
  better than 77%.

The surfaces are mixed by the layer graph itself — a shader graph of masks,
slope, height and noise — and reproducing that from the files is the open part.

**The colour pages.** The BC7 pages in nodes' second chunks (136 x 136) and in
the 4,624-byte chunks (68 x 68) are not geographic: matched against the backdrop
colour map at their node's footprint they correlate at 0.14 to 0.47 with their
best position anywhere, and in none of 12 checked is that position their own.

**Decals** are read and baked; see [Terrain decals](#terrain-decals).

## Terrain decals

Source: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Roads, runways, concrete aprons, painted lines and letters, tyre marks: the
`TerrainDecals` res (type `0x15E1F32E`, 10 MB in the level checked) holds them
as flat geometry the game drapes over the terrain.

| Part | Layout |
|---|---|
| header | at +16 a slot count n, then n 16-byte slots, then the record count |
| records | one per draw batch, back to back, of varying length: 156 bytes of fixed fields — first vertex at +32, triangle count at +36, texture tiling in metres at +44 — then the batch's vertex bytes (offset, size), then a tail naming its textures by their assets' partition GUIDs |
| vertices | 32 bytes: x, z (f32), 8 packed bytes, u, v (f32), r, g, b, a (f16); every batch a plain triangle list |
| indices | u32, counting from 0 in each batch; not needed |

Checks:

- the 926 records' vertex ranges follow each other without gap and cover the
  265,794 vertices exactly, and each record's first vertex × 32 is its offset;
- read so, the triangles are compact decals (letters, strips of line, patches);
  read one vertex off, they are slivers across the map;
- 912 of 926 batches name textures in their tail: a colour map (`_cv`) with an
  opacity map (`_op`, red channel), or for markings a channel mask (`_rgb`).

A batch maps its texture either by world position (u = x, v = z, the texture
repeating every tiling-metres: asphalt, concrete, gravel) or 0 to 1 across the
decal (a line, a letter, a tyre track). Records are drawn in file order.

**The bake.** `level --ground-texture M` paints, under the decals' extent and
tiles of at most 4,096 pixels, the backdrop colour map (bilinear) and then every
batch over it by its opacity × the vertex alpha. The heightfield's triangles
there become `ground:terrain x<x> z<z>` parts carrying the tile. A material's
own colour parameters are not read, so a marking drawn through a channel mask is
painted white, an outline dark, wear and tyre marks a faint darkening.

In the level checked, 909 of 926 batches draw, into four tiles at 0.5 m a
pixel; the export grows by 3 MB and takes a few seconds more. Seen from above,
the aprons, taxiways and road network lie under the compounds' fences and
buildings and lead into their gates.

Drawn as geometry of their own instead, decals would need alpha blending, which
the writer does not carry, and an offset above a terrain they would z-fight
with; baking keeps them in the ground's own colour.

## Textures and materials

Source: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

A Texture res (type `0x6BDE20BA`) is a 180-byte header: type and pixel format
at +8, width and height at +22, mip count at +30, the chunk GUID at +40, fifteen
mip sizes at +56. The chunk is the mip chain, largest first. Some chunks lack
their largest mips, which ship in another package, and the chunk's length says
which mip it starts at.

| Format | Decoded as | Evidence |
|---|---|---|
| 67, 66 | BC7 (sRGB, linear) | a plastic tank's colour sheet decodes as one; as BC3 the same bytes are noise |
| 61, 60 | BC3 | a crate sheet decodes cleanly as BC3, not as BC1 or BC7 |
| 57, 56, 55 | BC1 | half a byte a pixel |

The mesh asset names no texture. The link is in the level's **shader block
depots** (res type `0x73312045`, one per sub-world), keyed by the eight bytes at
+0x130 of a mesh section's record:

| Part | Layout |
|---|---|
| table, at 16 | (section key u64, descriptor offset u64), until an offset falls outside the res |
| descriptor | (block offset u64, hash u64, block size u64) |
| block | the section's shader parameters; each texture is a 49-byte record: a byte, 16 bytes, the texture asset's partition GUID, its instance GUID |

The crate's section key appears once in each of the ten depots of the
sub-worlds that place it, and its block names `t_mil_crate_03_cs` and `_nmt`
among the shared detail maps. A block names every texture the shader samples,
and which one is the colour map is not stated, so it is chosen: an sRGB 2D
texture whose name holds most words of the material's name
(`M_ConcreteWall_01`: concrete, wall), then of the mesh's, then one that is not
a detail, decal or damage map, then the one fewest blocks use. A section whose
only candidates are shared detail maps stays flat-coloured. In the level
checked, 2,214 of 2,375 drawn sections get a colour map.

Texture coordinates are vertex usage `0x21`, two halves (format 6) or two
floats (format 2). They tile, so a textured export writes them as floats with a
repeating sampler (see [Output format](output-format)).

The heightfield has no colour map of its own that could be read. It is coloured
from the terrain backdrop's: the backdrop's texture coordinates are a linear
function of world x and z (99% of its vertices within 0.001 of it; the map
covers a 65,536 m square, turned a quarter), and the same function gives the
heightfield's. The level ships that map's mips from 2,048 px down, so the
heightfield gets 32 m a pixel. Its dark rock lies on the steep ground: the
correlation of darkness with slope is 0.48, and at most 0.34 for the seven other
orientations.

## Not implemented

- The terrain's surface splatting through its layer graph (see
  [Terrain layers and decals](#terrain-layers-and-decals-what-is-known-not-yet-used)):
  away from decals the ground is the backdrop colour map, 32 m a pixel.
- Decal materials' colour parameters: markings through channel masks are
  painted in a neutral colour.
- Objects placed one by one rather than grouped: destructible prefabs and
  gameplay objects. Each kind has its own layout to pin down.
- Mesh levels stored inline in the res (10 meshes in a level, gadgets), skinned
  and composite meshes' bones and parts, and normals (computed by the writer).
- Normal, roughness and other maps; alpha (cut-out leaves and fences are drawn
  solid); texture variations a placed copy may carry.
- Effects (`fx/` paths) and the cable meshes, whose bounding boxes are tens of
  kilometres long; they are left out and counted in the summary.
- The XOR-obfuscated table form.
