
# Output format

Every export (`course`, `courses`, `terrain`, `level`) writes one **binary glTF 2.0**
file (`.glb`). It is deliberately small and flat, and laid out the way the 3DHeat
viewer reads a level. Source:
[`glb.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/glb.py).

## Structure

```
scene 0
 ├─ node "ground:terrain x-8184 z13299"  -> mesh 0 -> 1 primitive, material 0
 ├─ node "ground:road x-8184 z13299"     -> mesh 1 -> 1 primitive, material 1
 ├─ node "ground:markings"               -> mesh 2 -> ...
 ├─ node "ground:kerbs road_gen_rum_..." -> ...
 ├─ node "structure:barriers bar_armco_bclr"
 └─ ...
```

- **One node per part**, all at the scene root, with **no transforms**. All
  geometry is already in world space.
- Each node has its own mesh with **one primitive** and its own material. The
  node, the mesh and the material all carry the part's name.
- Each primitive has **its own compact vertex arrays**, only the vertices that
  part uses. A shared vertex array is legal glTF, but a reader that expands each
  primitive's accessors would then hold every vertex once per part.
- `asset.generator` is `heat3d_gamefiles`.
- **No `extras`** are written: no custom metadata, no lap, no game or track name.
  Everything the viewer needs is in the node names.

## Node names: the classification

The viewer takes a part's class from the **node** name (falling back to the mesh
name), and only when it matches

```
^(ground|structure|water)\s*[:|]
```

Anything else is classified by a heuristic written for Unreal landscapes. So
every part the exporter writes starts with one of these prefixes:

| Prefix | Meaning | Parts written |
|---|---|---|
| `ground:` | the driving surface and the land | `ground:road`, `ground:verge`, `ground:terrain`, `ground:gravel and dirt`, `ground:kerbs`, `ground:markings`, `ground:tyre marks` |
| `structure:` | what stands on it | `structure:barriers`, `structure:props`, `structure:signs`, `structure:buildings`, `structure:infrastructure`, `structure:bridges`, `structure:rocks`, `structure:smashables`, `structure:trees` |
| `water:` | water | `water:water` |

After the kind comes, depending on the game:

| Example | Meaning |
|---|---|
| `ground:road x-8184 z13299` | Forza ground in the terrain tile named `x-8184 z13299` (grid units, 1023 per 512 m) |
| `ground:road 3_-2` | BeamNG ground in 512 m square (3, -2) |
| `ground:road 3_-2 asphalt_light` | BeamNG modelled driving surface of material `asphalt_light` in that square |
| `ground:road 1_-4` | AC Rally ground in 512 m square (1, -4) of Unreal space |
| `structure:barriers bar_armco_bclr` | Forza placed models sharing one texture (its name without the GUID) |
| `structure:barriers` | placed models without a texture (Forza, AC Rally) |
| `structure:barriers armco_metal` | BeamNG placed models of one material |
| `ground:markings`, `water:water` | flat parts, one for the whole file |
| `ground:terrain` (Battlefield 6) | the heightfield; `ground:terrain backdrop` the distant terrain meshes, `ground:terrain blend` meshes that blend into the terrain |
| `ground:terrain x-634 z-552` (Battlefield 6, `--ground-texture`) | the heightfield under one baked decal tile, named by the tile's low corner in metres |
| `structure:buildings t_concreteclean_01_cs` (Battlefield 6, `--textures`) | every surface of that kind showing that colour map; without `--textures`, one part per kind, no suffix |

The viewer can filter by these names. For example, "only the racing surface" is
`ground:road` together with `ground:kerbs`, in all three games. The prefix is also
how the viewer draws a part: ground as the surface the heat lies on, structure as
what stands on it.

## Units, axes and frame

- **Metres, Y up**, glTF's convention. Nothing is rescaled or recentred: the
  numbers are the game's world coordinates, which is the point of reading the
  archive instead of reconstructing.
- **Forza:** the game's own world coordinates (x, y up, z), unchanged. The same as
  its telemetry, so a recorded lap lies on the course.
- **BeamNG.drive:** `(x, z, -y)` of BeamNG's Z-up world, which is the rotation the
  telemetry recorder applies. A rotation, not a mirror.
- **Battlefield 6:** the game's own world coordinates (x, y up, z), unchanged:
  the level's instance transforms applied to each mesh as stored. Mirrored
  copies are re-wound so their normals point outwards.
- **Assetto Corsa Rally:** the lap's frame. Unreal centimetres become metres,
  Unreal Z becomes y, and Unreal X and Y become x and z in whichever of the eight
  orientations the lap fitted (see
  [Assetto Corsa Rally](course-assetto-corsa-rally#which-stage-and-which-way-round)).
  Triangles are re-wound where that mapping mirrors.

Each export keeps the axes its telemetry uses, so in all three games the lap and
the course share a frame. Whether that frame is left- or right-handed in each game
has not been checked.

## Vertex data

The default is the **quantised** form (`quantize=True`). It needs the
`KHR_mesh_quantization` extension, which is listed in both `extensionsUsed` and
`extensionsRequired`.

| Attribute | Quantised (default) | Full precision (`quantize=False`) |
|---|---|---|
| `POSITION` | float32 VEC3, with min/max | float32 VEC3 |
| `NORMAL` | int8 VEC3 normalised, padded to 4 bytes (stride 4) | float32 VEC3 |
| `TEXCOORD_0` (textured parts only) | uint16 VEC2 normalised, clamped to 0-1 | float32 VEC2 |
| `COLOR_0` (untextured parts, when any part has a colour) | uint8 VEC3 normalised, padded to 4 bytes | float32 VEC3 |
| indices | uint16 when the part has at most 65,535 vertices, else uint32 | uint32 |

A vertex is 20 bytes instead of 32 (24 instead of 44 with colour). That takes a
third off every file, and it is the difference between a city course loading in a
browser tab and not. The cost is under half a degree of normal and 1/65,535 of a
UV (a fifteenth of a texel at 4,096 px). The command line always writes the
quantised form. `write_glb(..., quantize=False)` in Python writes the other.

Normals come from the game where it stores them (Forza terrain and models, BeamNG
shapes and terrain). Otherwise they are computed as area-weighted smooth normals
from the triangles. AC Rally normals are always computed.

## Materials, colours and textures

- Every material is `metallicFactor 0`, `roughnessFactor 1`.
- **Textured part:** `baseColorTexture` with the part's image, UVs, and no vertex
  colour. glTF multiplies the two, so a surface would come out darkened twice.
- **Untextured part:** vertex colour `COLOR_0` with the part's flat colour, and a
  white `baseColorFactor`. If no part in the file has a colour, there is no
  `COLOR_0`. Where parts share vertices, the later part's colour wins, so flat
  parts are written in order of increasing importance.
- **Images** are embedded in the binary chunk as **JPEG**, quality 90, no chroma
  subsampling, RGB only (alpha is dropped). A 2048 px ground of grass and tree
  crowns is noise to a lossless coder: several megabytes a tile as PNG, under one
  as JPEG. An image shared by several parts is stored once.
- One sampler for all textures: linear magnification, linear-mipmap-linear
  minification, **clamp to edge** on both axes. Textures never repeat — except
  in a Battlefield 6 export with `--textures`, whose materials tile: there the
  sampler repeats and `TEXCOORD_0` is float32, unclamped
  (`write_glb(..., repeat=True)`). That is why
  BeamNG draws repeating model textures as flat colours (see
  [BeamNG.drive](course-beamng#placed-models)).

| Texture | Size | Covers |
|---|---|---|
| ground (all games but Battlefield 6) | `--texture-size`: 2048, 1024 or 512 px | one 512 m square: 25, 50 or 100 cm a pixel |
| Battlefield 6 heightfield | the backdrop colour map's largest mip in the level, cropped | the terrain square: 32 m a pixel in the level checked |
| Battlefield 6 surfaces | `--textures`: at most that many px a side | the surface's own texture, **tiling** |
| Battlefield 6 baked ground | `--ground-texture`: metres a pixel, tiles of at most 4,096 px | one tile of the decals' extent: 2,048 m at 0.5 m a pixel |
| Forza placed model | at most 256 px | the model's own UV layout |
| BeamNG placed model | at most 256 px | the model's own UV layout, only where it does not repeat |
| AC Rally placed model | none | flat colours |

## What the writer refuses

`write_glb` raises an error rather than write a file a viewer would open and show
wrongly:

| Refused | Because |
|---|---|
| positions not N x 3, or not finite | a broken mesh |
| an index past the end of the vertex list | renders as noise |
| a textured part when the file has no UVs | renders as one smeared pixel |
| no triangles at all | renders as nothing |
| a normal, colour or UV array of the wrong length, or not finite | one per vertex is needed |

## Reading it elsewhere

Any glTF 2.0 viewer that supports `KHR_mesh_quantization` should open these
files. Only the 3DHeat viewer has been checked; other viewers are unverified. A
reader without the extension refuses the file, because it is marked required. The files can be large: about 80 MB for a
country circuit, up to several hundred MB for a city course with the automatic
budget.
