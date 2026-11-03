
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

### Which table is the level

A level can have several tables of the same name: one in the base game's
`Data`, one in each update (`Update/<pack>/Data`) that ships or changes it, and
one in each high-resolution pack
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Only some hold
bundles. For a level an update ships, the table in the base game is 64 KB of
chunks and no bundles, and the 4.4 MB one in the update is the level; taking the
first table found exported nothing of it.

So the level is the table with the most bundles, a later layer winning a tie
(base game first, then updates in name order), and the tables of the same name
without bundles are its **supplements**: their chunks are added to the level's,
for they hold the largest mips of its textures. A texture header names that
chunk at +164 (see [Textures and materials](#textures-and-materials)). `levels`
prints where each level comes from and how many supplements it has.

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

### Objects placed one by one

What the pipeline cannot group — destructible objects, containers, debris — is
placed by **object references** and **prefab references** in the
level's partitions:

| Type (GUID, signature) | Layout |
|---|---|
| object reference `a9a6a6ad…`, `0xC4856BEC` | `+32` the transform (as above), `+112` the object blueprint (import) |
| prefab reference `117c746e…`, `0xDE3FE9B4` | the same; the blueprint is a prefab, a partition of further references |

Prefabs nest; a copy lands at its own transform times its parent's (row
vectors), down to eight levels. An object blueprint is drawn as the meshes it
imports, leaving out the destroyed states (`dc_...`). A grouped prefab is
referenced as its `..._nongroupable_autogen` remainder, so nothing is drawn
twice.

The walk starts only from the level's worlds and layers. A partition whose
first instance is a prefab blueprint (`134919fc…`, `0x0247807D`) is a prefab's
definition, and a level keeps many under its own folder, placed by its worlds
in ways other than these references; walked from as if it were a world, a
prefab puts its contents at its local coordinates. In one level that piled
1,742 copies of barriers, sandbags and chairs round the world's origin, 120 m
under the ground. Worlds and layers have `a10ebe0f…`, `0xD3D16C3C` first.

Blueprints staged out of play are not followed: development and test assets
(`game/dev/`, `test/`), the round-end cinematic's set (`..._gameend_...`: a
helicopter and light blockers 47 m under the ground, in each of three levels)
and the death camera's controller (`.../deathflow/...`, whose gadgets stand at
the world's origin). They are recognised by their asset path, not their layer:
the same lighting layer that holds the cinematic set places a level's real
warehouse walls and roofs. After both rules no copy in three levels lies more
than 10 m under the terrain, where 1,759 did. Check: in one level,
1,574 copies, each standing on the terrain where the game shows it.

**Levels of detail that stand in.** A mesh's last level of detail may switch
to a distant-view stand-in with a material of its own: `M_LastLod`,
`M_Billboard`, `M_Vista`, `M_ProjectionLod` (215 meshes in one level). A
power pylon's lattice of 32,080 triangles ends in a 164-triangle `M_Vista`
silhouette, which the budget chose and which up close is a solid spike 64 m
tall. A level of detail that brings in such a material, one its finest level
does not have, is never chosen; the mesh's coarsest is the last real one.

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

A node's chunk also holds the pages of the layer masks after its height page,
and its second chunk ends with the node's colormap (see
[Terrain layers](#terrain-layers)).

## Terrain layers

The game shades the terrain near a player by splatting tiling surface materials
by painted masks, with a colormap over them, and drawing decals (roads,
asphalt patches, runway markings) on top. Frostbite's own account of the system
(Widmark, "Terrain in Battlefield 3", GDC 2012) lists the terrain's rasters as
the heightfield, shader splatting masks, a colormap "used as an overlay on top
of shader splatting", physics materials, a destruction depth mask, an albedo
map for bounce light and additional mask channels; a raster's tiles carry a
border for the rendering algorithms. The streaming tree of the levels checked
has seven raster trees, typed 0, 1, 2, 4, 5, 7 and 8, whose headers begin with
their tile size: 265 for the heightfield (type 0) and type 2, 72 or 66 for the
masks (type 1), 132 with a border of 2 for the colormap (type 4), 260 with a
border of 2 for type 5.

**The layer list.** The terrain's `....layergraphs` res lists one 32-byte entry
per layer, in the order the mask records number them (34 entries, 34 depot
sections and layer indices 0 to 33 in one level); each entry's id ends with
its section key in the layer graph's shader block depot
(`....layergraphs_shaderblockdepot`), whose block names the layer's maps: one
`_cv` colour map, `_nhs` and `_ao` maps per surface, plus shared detail and
noise maps. Many layers name no maps at all: they are sources the layer graph
reads. A layer's colour is its `_cv` map's mean; the tiling scale is not found.
The terrain asset ends with one five-byte entry per layer (a byte, then a u32
layer index or -1).

**The masks.** Raster tree 1 is the masks' quadtree. Its body starts with 59
bytes, the page's side at 0: 72 where the pages are BC4 (72 x 72, 2,592
bytes), 66 where they are uncompressed eight-bit (4,356 bytes). Then comes one
group per node, depth first:

| Part | Layout |
|---|---|
| group | u16; u16 record count; u32 page count; the records; a zero byte. A group without records is 7 bytes in all |
| record | 33 bytes: u16 layer, u16 hash, the quadrant's box (four floats), two flag bytes, an 85-bit presence pyramid |

A group's records are its node's four quadrants, layer by layer, each layer's
quadrants in the order (0, 0), (1, 0), (1, 1), (0, 1). A record with the
second flag set covers its quadrant whole and has no page; one without it has
the next page; a quadrant without a record of a layer its group names is empty
of that layer; the first flag is clear exactly when the layer goes on in the
quadrant's own group, one level down, which replaces it there. The page count
is the number of records with a page.

The pages: a streaming node's own group's pages follow, in its chunk, the
height page, a 4,358-byte 16-bit section and a 67 x 67 eight-bit raster (from
the chunk's start when it has no height page); its second chunk holds the
pages of its four quadrants' groups one level down, quadrants in the
colormap's order, then the colormap. A page is the quadrant's 64 x 64 texels,
rows along z and columns along x, with a border copied from its neighbours: 4
texels on a BC4 page, 1 on an uncompressed one.

The borders prove the placing without judgement: two pages of one layer side by
side must carry each other's edge texels. `read_masks` checks that for every
pair it places and refuses a level where fewer than 99% agree. Of 33 levels,
13 are read, with all but one of 192,808 borders agreeing (every one in 12 of
them); 2 have no painted masks; 18 are refused, 17 by the check (0% to 94% of
their borders agree: their nodes' chunks hold more than this layout knows) and
one because two of its groups describe the same node. A refused level's ground
takes the middle colour of its surface materials, and the export says why.
In one level the borders facing a full quadrant are exactly 255 and those
facing an empty one exactly 0 (2,042 of 2,050).

The 4,358-byte section and the 67 x 67 raster before the pages are not read:
the section's 2,179 values run from 27,042 to 30,929, with no small values and
no sentinel.

**The ground's colour.** The layer graph mixes the layers in a compiled shader
graph of masks, slope, height and noise, which is not read. `--ground-texture`
colours the ground by a rule of its own, said here as such:

- layers whose colour map is named for distance are the far view's stand-ins
  and are left out;
- the textured layers covering nine tenths of the terrain or more are the
  base. Their masks are full nearly everywhere, so where each lies is the
  shader's choice, not theirs: those named for rock or cliff colour slopes
  steeper than 40 degrees, those named for gravel flat ground (the other base
  layers when none is), blended between 20 and 40 degrees by the
  heightfield's slope (taken every 4 m and spread bilinearly over the baked
  texels: repeated in 4 m blocks it drew the rocky colour as hard-edged
  patches);
- every other textured layer is laid over the base by its own mask, in layer
  order;
- the colormap is laid over the result as the engine does it, twice the
  ground's colour times the map's, so that mid-grey leaves it as it is; where
  the colormap has no texels the ground takes the map's median brightness, in
  grey.

Checked against the median ground colour of gameplay frames of three levels
(chroma as red and blue over green): the baked play area comes to 1.00 / 0.69
against the frames' 1.19 / 0.78 in one, whose grass layers are green where the
frames show dry grass, 1.19 / 0.82 against 1.01 / 1.04 in another, whose
colormap itself is warm (1.13 / 0.88), and 1.05 / 0.91 against 0.93 / 0.92 in
a third without a colormap. The frames are lit and graded, so
this measures the tint, not the brightness.

**The colormap.** A node's second chunk holds, after the mask pages of its
quadrants' groups, four BC7 pages of 132 x 132 (17,424 bytes each), one per
quadrant of the node, in the order (low x, high z), (high x, high z), (high x,
low z), (low x, low z). The mask tree says how many bytes the mask pages take,
so the colormap is found by count, not by the chunk's end: in one level the
coarser nodes carry four more such pages after it, another raster in one flat
colour, and reading the chunk's last four pages lost the colormap over nine
tenths of the terrain. Without that count the colormap was also missed in
levels with uncompressed mask pages, whose pages are not a whole number of
BC4 ones; one level's colormap went from 0.4 to 0.94 of its terrain. The order was fitted: against the edges of
each quadrant's heightfield, every page of the nodes with features matches one
quadrant, unflipped, at 0.3 to 0.54 where the next best placement is below
0.2. Stitched by it, a level's pages join without a seam into the roads, water
and built-up areas of the test level, at 0.5 m a texel in the play area. Where
the layers do the work the colormap is near-neutral (median 110, 107, 104);
elsewhere it can carry full colour. A level whose second chunks hold only
uncompressed mask pages has no colormap read. An earlier round of this reader
called these pages not geographic: it matched them against the backdrop map,
which can be another landscape altogether, and placed each page on its whole
node instead of a quadrant.

**The bounce-light albedo** was looked for and not found: the root and
first-level nodes' chunks are whole mask pages, and type 5's payload is not
located.

**Holes.** A level's terrain asset (res type `0x1CA38E06`) names three shaders:
a default surface shader, a holes surface shader and a default source shader.
Which layer the holes shader reads is not found, so the heightfield is not cut.
In one level the navigation mesh runs on rock meshes 20 to 50 m under the
heightfield, where the game must have cut it away (12,120 of its triangles
more than 5 m under it). Looked for and not found there: a layer's mask (the
closest averages 0.69 over those triangles against 0.51 elsewhere), the
67 x 67 raster, a reserved height (no height page of the level holds 0 or
65,535) and a node flag (every node below the root has flags 1). Raster trees
7 and 8 are what is left. Both are run-length coded: a byte equal to the one
before it is followed by a count of further copies (`ff ff 84` is 134 bytes
of 255). Tree 7 (tile 256, 341 nodes: a full quadtree of five levels, four
bits a sample) decodes to 9.8 MB of byte pairs of values 0 to 3; tree 8 (tile
265) to 2.95 MB, nine in ten bytes 255, with its other values in runs that
start every 36,170 bytes. Neither's tiles are placed yet, so neither is
known to hold the holes.

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
batch over it by its opacity × the vertex alpha. The vertices' colour is not
used: some batches' vertices are pure green or blue, which tinted a level's
markings those colours. The heightfield's triangles there become
`ground:terrain x<x> z<z>` parts carrying the tile. A decal batch names no
shader block, so its material's colour parameters are not read: a marking drawn
through a channel mask is painted white, an outline dark, wear, tyre marks,
stains, puddles and wetness a faint darkening (stains painted white laid pale
strips across a level's lawns). A road variation mask is not paint but varies the surface
under it, hundreds of metres across, and is not drawn: painted white it laid
two pale rectangles 150 to 250 m long on a level's slopes. Decals that draw a
multiply texture (`..._mult`) with no colour map, such as a runway's
markings, are not drawn.

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
their largest mips, which ship in a high-resolution pack, and the chunk's length
says which mip it starts at. That pack's chunk is named at +164; it is read
from the level's [supplements](#which-table-is-the-level) when a mip the main
chunk lacks is wanted, and its length plus the main chunk's is the whole chain.

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
a detail, decal (`t_de_...`) or damage map, then the one fewest blocks use. A
road sign's block names its panel `t_com_highwaysignage_01_cs` and a decal
sheet `t_de_com_highwaysignage_01_ca` with a shield laid on its side; both match
the words, and without the decal rule the sheet won on use and the sign showed
the shield turned a quarter, through every texture coordinate set the section
has. Signed distance fields (`..._sdf`), palettes and channel masks (`_rgb`)
are never chosen, whatever words they share (`_rgba` maps are: most are colour
with an alpha, and leaving them out swapped a power line's and a staircase's
own maps for unrelated ones): a backdrop's vegetation
atlas `..._atlas_a_sdf` drawn as colour showed black and white stars for
trees, a backdrop's building palette a confetti of swatches for walls, and
glass debris drawn through its channel mask came out cyan. A section whose
only candidates are shared detail maps stays flat-coloured.

**Palettes.** A backdrop's buildings take their colours from a palette, 256 x
256 texels of 16 x 16 swatches: each vertex carries four bytes (usage `0x1E`)
whose first two say where in the palette its colour is, x and y out of 255.
`level` draws such a section with the palette as its texture, each vertex at
the centre of its swatch. Drawn so, a level's backdrop blocks come out in
pastel walls, terracotta and dark windows where they were plain white.

**Overlays.** Large objects tile a trim sheet through their first texture
coordinates and lay an overlay over it through the second, which lie within
0 to 1: an unwrap of the whole object. The overlay (`..._overlay_cs`, with its
mask `..._overlay_a`) carries what the object looks like from afar, an oil
tank's red bands and rust; drawn with the trim sheet alone, the tanks of one
level came out as grey panels. A section whose block names an overlay with its
mask, and whose second coordinates are such an unwrap, is drawn with the
overlay through them (36 sections in that level).

**Tints.** Many colour maps are grey (their channels' means within 6% of each
other): the shader paints them with colours from the block's parameters. After
its texture entries (49 bytes each) a block lists its parameters, each a type
tag (`f11af825` a float3, `a5e1f2de` a float4, `c1b1a014` a float,
`4a4fc3a1` an integer), the flag bytes `01 80` for one value, a two-byte hash
of the parameter's name, a u32 count, the value and an eight-byte id. The
names are not stored. Seven float3 name hashes act as tints: in one level
three of them hold a colour in about 1 block in 6 whose map is grey and almost
never where the map has colour of its own, and the others hold the colours a
grey map is painted in where the material's name says so (a bridge's
`..._blue` trim: 0.047, 0.098, 0.171 against a neutral 0.5). A family can hold
several values, one per channel of a mask, most of them neutral, and a value
with a channel near nothing (pure green on brick facades) selects a mask's
channel rather than paints. `level` multiplies a grey colour map, in linear
light, by each family's first value that is neither neutral nor such a
selector, over its neutral one, and keeps the result as a texture of
its own; a map with colour is left as it is. The rule is the exporter's own:
which channel of a mask takes which tint is not read. In one level it took
the share of structure triangles drawn near white from 19.4% to 3.9%.

**Object variations.** One mesh is placed in several looks: a warehouse
wall with a red or a blue stripe and a different number painted on it, a
container in green or grey. Each placed copy names its look:

| Where | Field |
|---|---|
| static model group member | +32: an array of one pointer a copy, to an object variation or null |
| object reference | +120: a pointer to an object variation or null |
| object variation (`ov_...` partition, type `235f2a9c...`) | its first instance +32: the variation's u32 name hash |

A section's look in a variation is the shader block keyed by the section's
own key with the variation's hash added to its first four bytes, as a
little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`);
a section with no block under that key looks the same in every variation.
The level's mesh variation databases (`meshvariationdb_win32`) list, per mesh
and variation hash, the materials each variation touches, but not the keys:
the rule was found from the keys themselves and holds for every section with
variants checked (the four variations of one wall, three of its sections each).
A variation's block brings its own textures as well as its tints: the
painted number on the wall is a letter sheet the variation's block names.
In one level 11,211 of 27,501 grouped copies are placed in a variation.

**Destructible meshes.** A mesh a match can knock down has a destruction
asset of its own name beside it (`.../br_x.destruction` for
`.../br_x_mesh`): the breakable buildings and walls (`br_`) and many props.
`level` keeps their surfaces in parts of their own, named with
` (destructible)`, whose glTF nodes carry `{"destructible": true}`. Their
destroyed states are the `dc_..._part<N>_mesh` meshes beside them, each
centred on its own origin; where a part sits is in the destruction asset,
which is not read, so the destroyed states are not exported.

**Left out.** Sections of placeholder blockout materials (`M_Whitebox`: a few
large untextured triangles some buildings keep beside their surfaces, which
stood out of a level as white fins), meshes made for cinematics (a helicopter
placed where its scene starts) and lighting helpers (planes that block light,
never drawn). A level's generated backdrop buildings
(`..._generated_blueprints_..._mesh`) are drawn, but their walls' material
names only noise maps and its vertices carry no colour, so they stay plain. In the level
checked, 2,214 of 2,375 drawn sections get a colour map.

**Cut-out maps.** The colour map's fourth channel means different things by
the map's name. In `_cs`, by far the most common (893 of one level's chosen
maps), it is smoothness: 1% of a median map's alpha lies within 0.1 of 0 or 1.
In `_cu` (leaves, grass) and `_ca` (colour and alpha) it is opacity: 90% and
87%. A colour map named `..._cu` or `..._ca` whose alpha is at least 75% near
0 or 1, at least 1% below 0.5 and at least 5% above is written with its alpha,
as PNG, and its
material as glTF `alphaMode` MASK, `alphaCutoff` 0.5, double-sided; leaf cards
then show leaves, not their black corners. One tree's leaf map has no alpha at
all (4 of 255 at most): its fronds are cut by geometry, and with only the first
two conditions the whole crown was cut away.

Texture coordinates are vertex usage `0x21`, two halves (format 6) or two
floats (format 2). Sections carry up to three more sets (`0x22` to `0x24`) for
decal and detail layers. The coordinates tile: a container's ribbed side runs
from -1.6 to 1.8, the terrain backdrop's tiles lie wholly outside 0..1, and in
one level 23% of the textured triangles reach outside 0..1. A renderer that
clamps them — the 3DHeat viewer does, packing all textures into one atlas —
smears the ribs to twice their width, turns a concrete floor into streaks along
one axis, and gives a tower's steel beams their texture's edge colour. So the
export cuts each triangle along the lines where its texture repeats and moves
each piece into 0..1 (see [Output format](output-format)); afterwards 0.03%
of the textured triangles, across which a texture repeats more than 16 times,
reach outside. A triangle the cutting would make more than 4 pieces of is
drawn in its texture's average colour instead: bark repeats down every branch,
and cut, a level's trees went from 6.4 to 24 million triangles.

The heightfield has no colour map of its own that could be read. Where one of
the terrain backdrop's maps covers it, it is coloured from that: the backdrop's texture coordinates are a linear
function of world x and z (99% of its vertices within 0.001 of it; the map
covers a 65,536 m square, turned a quarter), and the same function gives the
heightfield's. The level ships that map's mips from 2,048 px down, so the
heightfield gets 32 m a pixel. Its dark rock lies on the steep ground: the
correlation of darkness with slope is 0.48, and at most 0.34 for the seven other
orientations.

Another level's backdrop is eight near and eight far tiles round the play area,
each repeating its own texture across the tile, and none reaches the
heightfield. Each backdrop texture is fitted on its own, and when none covers
the heightfield it takes the average colour the backdrop shows within a
kilometre of the terrain square, which `--ground-texture` bakes the decals over.
A backdrop material is one whose name holds `TerrainBackdrop`, or `BD_` and
`Terrain` (`M_BD_<site>_Terrain..._Near`); or a backdrop mesh
(`bd_..._terrain<site>_04_far_mesh`) carries a plain terrain material
(`M_<region>_Terrain<site>_04_Far`), which the first two rules missed in one
level and so coloured its ground from its surfaces instead.

Where no backdrop map covers the heightfield, though, it takes the middle
colour of the terrain's own surfaces before the backdrop's average: the `_cv`
colour maps its layer graph's shader blocks name (27 in one level: sands,
gravels, soils, grass, cracked concrete), each averaged, then the median of
each channel, leaving out the engine's default surface. A backdrop can be
another landscape altogether: in one level its average (95, 99, 80 in sRGB)
turned the play area's ground a grey the game does not show. With `--ground-texture`, that colour is
multiplied by twice the colormap, which mid-grey leaves as it is, and baked
with the decals over both the decals' and the colormap's extent.

Against the game, the median ground colour of each level's baked play area
and of gameplay frames (rows 55 to 72% of the picture beside the HUD, 24
frames each; sRGB; frames are lit and graded, so the ratios r/g and b/g are
the fair comparison):

| Level | Frames | Backdrop's average | Now |
|---|---|---|---|
| first | 167, 140, 109 (1.19, 0.78) | 95, 99, 80 (0.96, 0.81) | 117, 108, 86 (1.08, 0.80) |
| second | 72, 71, 74 (1.01, 1.04) | 117, 110, 104 (1.06, 0.95) | 146, 135, 117 (1.08, 0.87) |
| third | 83, 89, 82 (0.93, 0.92) | 160, 148, 136 (1.08, 0.92) | 148, 137, 117 (1.08, 0.85) |

The first is put right; the other two were a little nearer in hue before. One
colour for a whole level cannot be right everywhere; the masks would be.

## Navigation mesh

Source: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

A level ships one partition per agent, `<level>/dbt/<level>_navmesh_layer_<n>`:
in one level layer 0 is the soldier (1.8 m tall, 0.18 m step, 0.4 m radius) and
two others are vehicles (3.5 and 10 m tall). Each partition holds two arrays:

| Array | Element |
|---|---|
| tiles | 28 bytes: u32 0, u32 hash, u32 0, u32 chunk index, u16 tile x, u16 tile z, u32 offset, u32 size |
| chunks | 20 bytes: the chunk's GUID, u32 size |

A tile is `size` bytes at `offset` in chunk `chunk index`, little-endian, and
laid out as Detour's (Recast Navigation) behind a longer header:

| Offset | Contents |
|---|---|
| 0 | `VAND`, version 7 |
| 24 | counts: polygons, vertices, links, detail meshes, detail vertices, detail triangles, bounding-volume nodes, off-mesh links, the first off-mesh polygon |
| 188 | agent height, step, radius |
| 200 | the tile's bounding box, six floats |
| 232 | vertices: x, y, z floats, world coordinates |
| next 8-byte boundary | polygons, 32 bytes: u32, six u16 vertex indices, six u16 neighbours, u16 flags, the vertex count at +30, at +31 the area (low six bits) and kind (top two) |
| then, packed | links (16 bytes), detail meshes (12: first detail vertex u32, first detail triangle u32, vertex and triangle count u8), detail vertices (three floats), detail triangles (three indices and flags), bounding-volume nodes (16), off-mesh links (80) |

In every tile of three levels (17,702) these add up to the tile's size to the
byte, and the detail meshes number the polygons before the first off-mesh one.

A polygon is flat between its corners; its **detail mesh** holds the
surface's real height over bumps, rocks and steps, and is what is drawn. A
detail triangle's index below the polygon's corner count is that corner,
otherwise detail vertex `first + index - corners`. Fanning the polygons
instead put 9.3% of one level's triangles more than half a metre under the
terrain and 5.6% with the detail meshes, and 15,544 triangles had an edge over
20 m against 8,915; none is longer than a 16 m tile's diagonal plus the step
up a slope.

Kind 0 is ground, kind 2 small steep patches (about 45 degrees, a square metre
each), kind 1 a link between surfaces: its corners span 125 m of height or more
and lie outside the tile, some at the origin. Links are left out; the rest are
drawn by their detail meshes, or fanned in a tile without any.

Checks: the chunks' sizes add up to the tiles' exactly (20,677,772 bytes in 305
chunks for 9,744 tiles of 16 m); every surface vertex lies within its tile's box
give or take 1.2 m; 99.87% of the triangles face up. A tile that fails is
refused and counted, and in that level none is.

What the soldier's mesh covers, seen from above in the test level: the ground,
floors, stairs and some roofs, and not the tops of freight containers. It is the AI's map of where a soldier can stand,
the closest the files come to where players stand.

## Not implemented

- The terrain's layer graph, which mixes its surface layers (see
  [Terrain layers](#terrain-layers)): the ground's colour follows a rule of
  this reader's own from the layers' masks and the heightfield's slope, and
  levels whose mask pages do not fit together get one colour.
- Decal materials' colour parameters: markings through channel masks are
  painted in a neutral colour.
- Object blueprints that are not meshes (gameplay logic, effects, sounds).
- Destroyed states of destructible meshes: their parts' places are in the
  destruction asset, which is not read.
- The navigation mesh's links (jumps, ladders, vaults) and its vehicle layers.
- Mesh levels stored inline in the res (10 meshes in a level, gadgets), skinned
  and composite meshes' bones and parts, and normals (computed by the writer).
- Normal, roughness and other maps; alpha other than a cut-out (translucent
  glass and decals are drawn opaque).
- Terrain holes: a holes surface shader is named, but what it reads is not
  found (see [Terrain layers](#terrain-layers)), so the heightfield is not cut
  where the walkable ground runs under it.
- Which tint goes with which channel of a material's mask: a grey colour map
  takes the first tint that is not neutral (see
  [Textures and materials](#textures-and-materials)).
- Effects (`fx/` paths) and the cable meshes, whose bounding boxes are tens of
  kilometres long; they are left out and counted in the summary.
- The XOR-obfuscated table form.
