---
title: Assetto Corsa Rally
parent: Course export
nav_order: 3
---

# Course export: Assetto Corsa Rally

Assetto Corsa Rally is built on Unreal Engine 5 (5.6.1, a modified build) and
ships its content as IoStore containers. None of them is encrypted. The export
finds the stage and the axis orientation from the lap. It writes the stage's own
ground tiles, split into road and terrain and textured from the stage's baked
ground colour, and places the other models in flat colours by category.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Sources: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (install, stages, placement),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (the export).
The Unreal readers underneath are on [Unreal 5 IoStore](reader-unreal-iostore.md),
and decompression on [Oodle](reader-oodle.md).

**Status:** checked on the installed game with laps generated in a random frame
on every stage, and it found the right stage and frame every time. No lap recorded
in the game itself has been through it yet.

## Finding the install

- `--install <folder>`: the game folder, or its `Content\Paks`, or any folder
  holding `.utoc` files. The tool checks `<folder>`, then
  `<folder>\acr\Content\Paks`, then `<folder>\Content\Paks`.
- Otherwise every Steam library's `steamapps\common\Assetto Corsa Rally` is
  checked in the same way.
- Every `.utoc` in that folder is opened as one store. Containers that fail to
  open are skipped. If none opens: "no readable IoStore containers in ...".

Most blocks are Oodle-compressed, and a library is looked for on the machine
(every Steam library is searched). See [Oodle](reader-oodle.md).

The game is taken as AC Rally when the lap file says `"game": "assetto-corsa-rally"`
(or `acrally`), or when you pass `--game acrally`.

## What a stage is

A stage is a **World Partition** map:

- `Content\Levels\<Stage>.umap` places the far terrain.
- Cooked cells under `Content\Levels\<Stage>\_Generated_\*.umap` place everything else.

A level counts as a stage if its environment folder,
`Content\Environments\<Stage>\`, has a `MeshesTrack` folder. The tool does not go
by the tiles' names, because one stage names them after its town rather than its
map. `--level` is matched case-insensitively against these map names. A wrong
name lists the stages there are.

There is **no landscape**. The ground is static meshes:

| Tiles | Path | Become |
|---|---|---|
| track tiles, about 175 m, split in two | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` and `..._Terrain_k` | `ground:road` and `ground:terrain` (an unsplit track tile, such as a frozen lake, is all road) |
| far terrain, 2 km tiles | `.../MeshesTerrain/...` | `ground:terrain` |

## Reading the placements

What places a mesh is a `StaticMeshComponent`: its `StaticMesh`, and its
`RelativeLocation`, `RelativeRotation` and `RelativeScale3D`, each relative to the
component it is attached to (`AttachParent`), up to the actor's root, which is in
the world.

- The properties are **unversioned**: stored by position in the class's property
  list, not by name. They are read with the schemas in
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (see [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- A value equal to the component's template (its archetype in a Blueprint) is not
  stored, so the template's values are read first, recursively, and the
  component's own values override them.
- Components with `bVisible = 0` or `bHiddenInGame = 1` are skipped. So are meshes
  whose path matches `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/`
  or `_hlod`.
- Rotations use Unreal's `FRotationMatrix` (pitch, yaw, roll in degrees).
- Duplicates (the same mesh at the same transform, to 0.1 cm) are dropped.
- Components that cannot be read are counted by reason and reported, for example
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instanced components** (forests, nearly all of them) are read only with
`--trees`. This build has rearranged those classes beyond the engine's headers,
so their properties are not read. Instead:

- the mesh comes from the package's dependency table, where each such component
  lists exactly one static mesh,
- the instances come from the native block after the properties
  (`[1][1][128][count]` then `count` 4x4 double matrices),
- the component is taken to sit at its actor's root, which is how the foliage
  actors place them.

Coordinates are Unreal's: centimetres, Z up, X forward, Y right, a left-handed
frame.

## Which stage, and which way round

The telemetry's frame is not documented, so it is not assumed. It is fitted:

- **Eight candidate frames.** Unreal Z (cm) times 0.01 becomes the lap's height
  (y). Unreal X and Y become the lap's x and z, swapped or not, each with either
  sign, all scaled by 0.01 to metres.
- **A road-height grid.** For each stage, every road tile is placed (at its
  coarsest level of detail) and the highest road vertex is kept per 2 m cell.
- **Scoring.** Up to 400 lap samples, evenly spaced, are taken into Unreal space
  through each frame. A sample is on the road when, among the 3 x 3 cells around
  it, the road height closest to it is between 1 m below and 3 m above the sample
  (`ON_ROAD`). The score is the share of samples on the road.
- **Winner.** The best frame on the best stage, if it scores at least 50%.
  Otherwise the export stops: "the lap does not lie on any stage's road in any
  frame (best: ...). Name the stage with --level."
- **A lap that names its track.** If the lap file has a `track` field, a stage
  whose name loosely matches it (letters and digits only, either containing the
  other) is tried first, alone, and accepted only if it scores at least 80%.
  Otherwise every stage is tried.
- With `--level`, only that stage is tried, in all eight frames.

The console says, for example,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Everything is then written **in the lap's frame**: metres, Y up. A triangle's
winding is flipped wherever a transform mirrors, so faces still point the right
way.

## The ground

- The corridor is `--margin` metres around the lap in its own x/z plane.
- Each ground tile is placed at its finest level of detail, and only triangles
  reaching into the corridor are kept.
- Triangles are grouped by kind (road or terrain) and by 512 m square in Unreal
  space (51,200 cm), each square with its own image. Parts are named like
  `ground:road 1_-4`. UVs are `(unreal_xy - square_origin) / 51200`.
- Normals are computed from the triangles for the whole file.

### The ground texture

Unless `--no-textures`, each square is painted from two sources, at
`--texture-size` pixels:

1. **The baked ground colour.** The stage map's `RuntimeVirtualTextureComponent`
   (its box is `RelativeLocation` as the corner and `RelativeScale3D` as the size,
   with no rotation) points at a streaming **virtual texture**, the ground colour
   the game baked. The region of the square is read from it, at the level whose
   pixels are nearest the wanted size. That is 13 to 59 cm a pixel, depending on
   the stage.
2. **The satellite image** fills whatever the virtual texture leaves black. It is
   the stage's `sat*_(b|bc|c|basecolor)` texture in its environment folder, read
   at up to 4096 px. Its placement is found by a least-squares fit of the far
   terrain's first UV channel against world x and y. The fit must be linear to
   within 0.01 at the 95th percentile, or the image is not used. If the far
   terrain's UVs run past 1 (a material that repeats them), the mapping is halved
   until they fit once.

The console says which it used, for example
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
One stage has neither and is drawn in flat colours.

## Placed models

Every placement that is not a ground tile is classed by its mesh path (first
match wins):

| Category | Mesh name (or path, for trees) contains |
|---|---|
| trees (only with `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| rocks | `rock`, `cliff`, `boulder`, `stone` |
| kerbs | `kerb`, `curb` |
| barriers | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| signs | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| buildings | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastructure | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| props | anything else |

- A copy is considered if its origin is in the reach corridor (`margin + 60 m`)
  and drawn if its bounds touch the corridor.
- Levels of detail follow [Levels of detail and the budget](detail-budget.md):
  distance bands, then the costliest models step down to fit the budget. Where
  even the coarsest levels exceed it, the furthest copies are left out, as in
  BeamNG, until it fits. Kerbs keep full detail and are never left out. The
  summary prints `placed on it (N triangles of a B budget)` and, when copies
  went, `N copies left out to fit the budget, the furthest from the driving first`.
- Every category is one part in a flat colour: `ground:kerbs` for kerbs, which
  are driving surface, as in Forza and BeamNG, and `structure:<category>` for the
  rest:

| Category | Colour (linear RGB) |
|---|---|
| barriers | 0.55, 0.52, 0.48 |
| signs | 0.75, 0.72, 0.65 |
| buildings | 0.62, 0.58, 0.52 |
| infrastructure | 0.48, 0.48, 0.50 |
| rocks | 0.45, 0.43, 0.40 |
| props | 0.55, 0.45, 0.35 |
| trees | 0.20, 0.32, 0.14 |
| kerbs | 0.70, 0.25, 0.22 |

Static meshes that cannot be read (skeletal meshes, Nanite-only meshes, levels
not stored inline) are counted: `N meshes could not be read`.

## Checks behind it

As stated in the source, on the installed game:

- 54 containers, 47,246 package paths in the tables of contents (version 8).
- Every cell of every stage opens. 32,310 static-mesh and 10,906 scene components across 16 levels decode, each ending exactly at its class's native tail.
- 296 of 300 random static meshes decode (the other four are skeletal). A road tile's decoded extent matches its stored bounds.
- A 4096 px DXT5 satellite image's 13 mip levels are exactly the sizes of their bulk entries.
- The first virtual texture chunk is 4 + 4,096 x 34,848 bytes, its tiles accounted for to the byte, and the road tiles land on the road it shows.

## Known gaps

- Instanced components' own properties are not read (see above). Their placement assumes the actor root.
- Forests generated by PCG at run time are not stored in the files and cannot be exported.
- Spline meshes (invisible respawn walls), decal components and placed models' own textures are not drawn. Models are flat-coloured.
- `--season` has no effect.
- A game patch can move property slots. The reader raises rather than mis-reading, and the course reports how many components failed.
