---
title: BeamNG.drive
parent: Course export
nav_order: 2
---

# Course export: BeamNG.drive

The BeamNG export reads a level the way the game mounts it, then writes the same
kind of file the Forza export writes: ground per 512 m square with a baked
texture, road and loose ground as their own parts, placed models by category, and
water.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Sources: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (install, file system, scene, terrain, materials),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (the export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) and
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (shapes).
File formats in detail: [BeamNG files](reader-beamng.md).

## The lap's frame

The `course` export expects BeamNG positions in the **viewer's frame**:
`(x, z, -y)` of BeamNG's Z-up world, metres. That is the rotation the 3DHeat
telemetry recorder applies. The export turns the lap back into BeamNG's frame
(`(x, -z, y)`), works there, and writes everything out in the viewer's frame
again. This is a rotation, not a mirror, so nothing comes out mirrored. A lap
recorded in BeamNG's raw frame would not be placed. This has not been tested with
other recorders.

The game is taken as BeamNG when the `heat3d-lap` file says `"game": "beamng"`,
or when you pass `--game beamng`.

## Finding the install

- `--install <folder>`: the folder holding `gameengine.zip` and `content`.
- Otherwise every Steam library's `steamapps\common\BeamNG.drive` is checked
  for those two.
- If neither works: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## The file system

BeamNG ships plain zip archives and mounts them into one file system that levels
refer into (`/art/shapes/...`, `/assets/materials/...`). The export builds the
same thing: one case-insensitive index over

1. `gameengine.zip`,
2. every `*.zip` under `content`, except `content\vehicles\*` and archives whose
   names start with `art_sound` or `audio`,
3. the user's content, newest layout first: under
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` and `%LOCALAPPDATA%\BeamNG.drive`, the
   `current` folder and the highest numbered version folder. From each:
   `mods\*.zip`, every folder in `mods\unpacked`, and the user folder itself if it
   has a `levels` folder.

Later additions win, as in the game, so a mod replaces what it overrides. Mods are
always included in a course export.

Paths a level names are resolved the way the game resolves them: as given, then
relative to the file that named them, and for each also as the `.dds` a texture
was cooked to, the `.cdae` a `.dae` was compiled to, or through a `.link` file
pointing into `/assets`.

## Which level

Without `--level`, every level is scored on how much of the lap lies on it:

- Up to 500 lap samples, evenly spaced, are used.
- For each level's `TerrainBlock`, the terrain's extent is read from the first
  five bytes of its `.ter` file, so a level the lap is nowhere near costs nothing.
  If at least 30% of the samples are inside the extent, the heights are read. A
  sample counts as **on** the terrain when it is between 1 m below and 3 m above
  it (`ON_GROUND`), because a car's reference point is its body, not its tyres.
- If no level scores 50% or more, levels are also scored on their **roads**. Some
  levels run on past their heightmap (one shipped desert continues as rock
  sheets). A sample is on a road when it lies within the road's half-width plus
  4 m (at least 6 m) of a `DecalRoad` segment, and between 2 m below and 4 m above
  it.
- The best level wins if it scores at least 30%. Otherwise the export stops and
  lists the best three: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

The console says `on <level>: 87% of the lap lies on its terrain` (or `roads`).
`--level` is matched case-insensitively against the level folder names.

## Reading the level

What a level is made of, each part checked against the shipped levels
(details on [BeamNG files](reader-beamng.md)):

- **Scene**: `levels\<name>\main\**\*.level.json` (one JSON object per line, or a
  JSON array), or a `.mis` file for older levels. The tool reads `TSStatic`
  objects (placed models, skipping hidden ones), `Prefab` objects (nested up to 8
  deep, TorqueScript `.prefab` or `.prefab.json`), `DecalRoad` objects (painted
  roads), `TerrainBlock`, `WaterPlane`, `WaterBlock` and `River`.
- **Forest items**: `levels\<name>\forest\*.forest4.json`, typed through the
  `managedItemData.json` records. Barriers, fences and rocks are forest items as
  often as trees are.
- **Terrain**: the `.ter` heightfield and its layer map.
- **Materials**: every `*.materials.json` outside `levels\`, plus those of this
  level.

## The corridor and the road decals

The corridor is `--margin` metres around the lap in BeamNG's x/y plane (see
[Course export](course-export.md#the-corridor)). A reach corridor of
`margin + 60 m` selects the candidates.

**Road decals** (`DecalRoad`) are where most of BeamNG's roads are: painted on
the terrain, not modelled. Decals whose extent touches the reach corridor are
taken in the game's drawing order (descending `renderPriority`, then file order),
laid out as ribbons:

- The nodes (x, y, z, width) are interpolated by a **centripetal Catmull-Rom**
  spline about every 1 m. The uniform kind loops back on itself where nodes bunch
  up at a hairpin. Looped roads close.
- Each edge takes the terrain's height where the terrain is within 1.5 m of the
  road's own height, and keeps the road's height elsewhere (on a bridge).
- The material name decides what a decal paints:

| Kind | Material name matches (first match wins) |
|---|---|
| tyre marks | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| overlay (cosmetic) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| markings | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| loose | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| road | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| overlay | anything else |

## The ground

The terrain heightfield inside the corridor becomes triangles:

- One quad per terrain square whose centre is in the corridor. Squares with layer
  255 (holes) are skipped. Each quad is two triangles, with the diagonal
  alternating the way Torque's terrain does.
- Heights are `position.z + h * maxHeight / 65535`. Normals come from the height
  differences.
- Each square is classed by its **layer**: the layer name with its terrain
  material's ground model and annotation. Paved words make it `road`,
  `grass/forest/rock/moss/leaves/cliff/stone` make it `terrain`, and loose words
  make it `loose` (gravel and dirt). Anything else is `terrain`.
- Then **road and loose decals override** the squares they cover, in drawing
  order, so the last decal painted decides.
- Vertices are split per 512 m square (`floor(x / 512)`, `floor(y / 512)`), so
  each part maps into exactly one image: `u = (x - x0) / 512`,
  `v = 1 - (y - y0) / 512`.

The console prints `what the ground is made of` with triangle counts per kind.

### Modelled driving surface

BeamNG's circuits are models as often as they are terrain. A raceway's track can
be one mesh with its lines, rubber and rumble strips as meshes of their own on
top. So placed models in the categories road, kerbs, verge, props and bridges are
searched for driving surface. Per material:

| Surface | Decided by (first match) |
|---|---|
| tyre marks | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` in name, ground type or annotation |
| markings | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` in the material name |
| kerbs | `rumble`, `kerb`, `curb` |
| road | ground type `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, or the name contains `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| loose | ground type `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| verge | `sidewalk` |
| (the model's own category) | for models already classed road, kerbs or verge |

Of those materials, the **up-facing** triangles (normal z above 0.5) inside the
corridor are taken out of the model and become ground. They are painted into the
tile's baked texture and written as parts such as
`ground:road 3_-2 asphalt_light`. Markings and tyre marks are painted only. The
model's remaining triangles stay with the model. These models are never
simplified or left out by the budget, because a coarse track is a wrong track.

## The baked ground texture

Each 512 m square that has ground gets one image of `--texture-size` pixels
(2048 = 25 cm a pixel), drawn the way the game draws its ground:

1. **Terrain layers.** Per pixel, the four surrounding terrain squares' layers are
   blended bilinearly. Each layer is coloured as the game colours it: the
   material's **base map** stretched over `diffuseSize` metres (or the whole
   terrain), then the **detail** and **macro** maps as grey overlays
   (`colour * (1 + strength * (2 * overlay - 1))`, 0.5 neutral). Their defaults
   repeat every 2 m and 60 m, with strengths 0.5 and 0.3, unless the material says
   otherwise. A layer with no material gets its surface's flat colour. Base map
   row 0 is north.
2. **Road decals** that are painted on the terrain only, in drawing order, each
   with its own texture, opacity map, tint and opacity, along the ribbon.
   Shipped levels use priorities around 12-16 for asphalt bases, 10 for markings
   and 4 for rubber.
3. **Modelled driving surface** seen from above: bases first, then overlays, each
   in the model's own repeating texture at one texel per bake pixel.
4. **Decals that project over objects too** (`overObjects`), last.

With `--no-textures`, nothing is baked: ground parts get flat colours, and the
modelled markings and tyre marks become parts of their own, lifted **3 cm**.

## Placed models

Candidates are every `TSStatic`, prefab child and forest item whose origin lies in
the reach corridor. A candidate is drawn if its shape's world bounding box touches
the corridor.

**Category** comes from the level's own annotation and the shape's path. The
first rule that matches wins:

| Category | Annotation | Path or name contains |
|---|---|---|
| backdrop (never drawn) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| kerbs | | `kerb`, `curb`, `rumble` |
| road | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| verge | `SIDEWALK`, `COBBLESTONE` | |
| trees (only with `--trees`) | `NATURE` | tree, foliage, bush, grass, plant and similar words |
| rocks | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barriers | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| signs | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| bridges | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastructure | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| buildings | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| props | | anything else |

**Shapes** are read from the compiled `.cdae`, or from the Collada `.dae` where no
cache exists (mods). A shape that cannot be read is counted:
`N copies of M models could not be read`. Materials named or textured
`invisible`, `collision` or `nodraw` are never drawn.

**Textures.** Models are grouped per category and material into parts named
`structure:<category> <material>` (or `ground:kerbs <material>`). A group gets its
material's colour texture at up to **256 px** only if its UVs stay within 0-1
(98% of vertices within -0.02 to 1.02). The viewer packs textures into an atlas
and cannot repeat one. A group whose texture repeats is drawn in the texture's
average colour (alpha-weighted, in sRGB, times the material tint), or in the
category colour if it has no texture.

**Detail** follows the shared scheme on
[Levels of detail and the budget](detail-budget.md). BeamNG's levels of detail are
the shape's `details` (largest pixel size first). Over budget, the furthest
copies go first. Kerbs and models carrying driving surface are never simplified
or left out.

`--no-placed` drops the structures but still keeps modelled driving surface.
`--trees` adds the trees category.

## Water

| Source | Drawn as |
|---|---|
| `WaterPlane` (the sea) | a 4 m quad at the water height for each corridor cell where no terrain reaches that height |
| `WaterBlock` | one quad, the unit square at local z = 0 in the block's transform (so its scale sets the size), if it touches the corridor; whether z = 0 is the block's surface is unverified |
| `River` | a ribbon through its nodes if it touches the corridor |

All water is one flat part, `water:water`.

## Not drawn

- Ground cover (procedural grass).
- Scenery placed round the edge of the world (`backdrop` and the like).
- Repeating model textures, which come out as an average colour (see above).
- Skinned meshes (vehicles, characters) and decal meshes inside shapes.

## Checks behind it

As stated in the source, measured on the shipped levels:

- Road nodes lie on the terrain to 1-2 cm (median) on three levels with `h * maxHeight / 65535` and rows along +y. `h / 32` or the other axis order miss by tens to hundreds of metres.
- Rail sections chained along a road run along `rotationMatrix` row 0 (92%).
- The `.cdae` node rotation has to be transposed. With that, world bounds match the source `.dae` to the millimetre. The textbook way they are 38 cm out (median).
- Exported on six shipped levels of every kind, 20 seconds to 2 minutes each.
