
# Course export

`course` turns a lap into a course: the ground in a band either side of where the
car went, and what stands on that ground, as one `.glb` for the viewer. This page
covers what all three supported games share. The pages under it cover what
differs:

- [Forza Horizon](course-forza-horizon): ForzaTech `.minizip` archives
- [BeamNG.drive](course-beamng): zip archives, a terrain heightfield, compiled shapes
- [Assetto Corsa Rally](course-assetto-corsa-rally): Unreal 5 IoStore, a World Partition stage
- [Levels of detail and the budget](detail-budget): how many triangles the placed models get, and which copies stay

## The steps

1. **Read the lap.** Positions only, from any of the shapes in
   [Lap inputs](lap-inputs). Speed and inputs are not used. A lap with fewer
   than two samples is refused ("holds no driving").
2. **Decide the game.** `--game`, then the lap file's own `game`, then Forza (see
   [Commands](commands#which-game)).
3. **Find the installed game.** All three search every Steam library listed in
   Steam's `config\libraryfolders.vdf`. Forza also searches `C:\XboxGames`.
   `--track` (Forza) or `--install` (BeamNG, AC Rally) skips the search.
4. **Find where the lap was driven.** This is never decided by a name match
   alone. Forza picks the track whose terrain tiles cover the lap. BeamNG picks the
   level whose terrain (or roads) the lap's samples lie on. AC Rally tries every
   stage in eight axis orientations and picks the one that puts the most of the
   lap on road.
5. **Cut a corridor** `--margin` metres either side of the driving (below).
6. **Build the ground** inside the corridor, classed as road, verge, gravel and
   dirt, terrain, markings, tyre marks or water, and bake a ground texture for
   each 512 m square.
7. **Place the models** standing in the corridor, by category, at a level of
   detail chosen by distance and a triangle budget.
8. **Write the `.glb`**: one named node per part. See [Output format](output-format).

## The corridor

The cut is a band around the driven line, not the lap's bounding box. For a
circuit the two are nearly the same. For a point-to-point sprint the box is mostly
hillside nobody drives past, and the band can be a tenth of its area. Source:
[`corridor.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/corridor.py).

How it is built:

- The driving is projected to the ground plane: x and z of the lap
  (BeamNG: x and y of the game's own frame).
- It is rasterised on a grid of **4 m** cells (`CELL`). Each cell the driving
  touches is widened by a disc of radius `margin + 4 m` in every direction.
- Consecutive samples less than **50 m** apart (`JOIN`) are joined by points every
  4 m, so the band has no gaps. Samples further apart are treated as separate
  stretches of driving and are not joined. A library course is many lap files end
  to end, and the finish of one sprint and the start of the next must not draw a
  band across the map.
- A triangle is kept if any corner, the middle of any edge, or its centroid lies
  in the band. The middle points catch a large triangle that lies across a narrow
  band with all its corners outside.
- Height is never part of the cut. A box that bounded altitude would cut the
  ground out from under a hill the road climbs.

The console reports the corridor's area, for example
`cutting 80 m either side of the driving: 1.53 km2 of a 6,000 by 3,600 m box`.

BeamNG and AC Rally also build a wider **reach** corridor of `margin + 60 m`. A
placed model is considered if its origin lies in the reach corridor, and drawn
only if its footprint touches the real corridor. That way a long object whose
origin is just outside the band is not lost. BeamNG also uses the reach corridor
to choose which road decals to paint.

## What the ground is made of

Every export classes its ground triangles into the same kinds, and each kind is
written as its own part so the viewer can show or hide it:

| Kind | Part name | Flat colour (linear RGB) | Forza | BeamNG | AC Rally |
|---|---|---|---|---|---|
| road | `ground:road` | 0.22, 0.22, 0.23 | road strips: asphalt part | `ASPHALT`-type layers, road decals, modelled road | track tiles (`/MeshesTrack/`) |
| verge | `ground:verge` | 0.52, 0.47, 0.30 | road strips: the shoulder | sidewalks and verge models | - |
| gravel and dirt | `ground:gravel and dirt` | 0.50, 0.42, 0.30 | - | dirt, gravel, sand, mud layers and decals | - |
| terrain | `ground:terrain` | 0.30, 0.44, 0.18 | everything else | everything else | `_Terrain` tiles and far terrain |
| kerbs | `ground:kerbs` | 0.60, 0.12, 0.10 (Forza) | `road_gen_rum*` props | kerb, curb and rumble models | kerb and curb models |
| markings | `ground:markings` | 0.90, 0.90, 0.88 | decal submeshes, lifted 5 cm | painted into the texture | - |
| tyre marks | `ground:tyre marks` | 0.20, 0.17, 0.16 | decal submeshes, lifted 5 cm | painted into the texture | - |
| water | `water:water` | 0.16, 0.34, 0.48 | water materials | sea plane, water blocks, rivers | - |

The flat colours are chosen to read at a glance, not to match the game. They are
used for parts without a texture and by viewers that ignore textures. Source:
[`surfaces.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/surfaces.py).

Ground parts are split per 512 m square, and each square carries its own baked
image, so the part names carry the square:

| Game | Ground part name | Square key |
|---|---|---|
| Forza | `ground:road x-8184 z13299` | the terrain tile's grid name (steps of 1023, see [Forza Horizon](course-forza-horizon)) |
| BeamNG | `ground:road 3_-2` | `floor(x / 512)`, `floor(y / 512)` in BeamNG metres |
| AC Rally | `ground:road 1_-4` | `floor(x / 51200)`, `floor(y / 51200)` in Unreal centimetres |

## What stands on it

Placed models are written in parts named `structure:<category>`, or
`ground:kerbs` for kerbs (in all three games). When a part has its own texture, the
texture or material name follows the category, for example
`structure:barriers bar_armco_bclr`.

| Category | Forza | BeamNG | AC Rally |
|---|---|---|---|
| barriers | yes | yes | yes |
| props | yes | yes | yes |
| signs | yes | yes | yes |
| buildings | yes (whole-building stand-ins where the game has them) | yes | yes |
| infrastructure | yes | yes | yes |
| bridges | yes | yes | (classed as infrastructure) |
| rocks | yes | yes | yes |
| kerbs | yes, as ground | yes, as ground | yes, as ground |
| trees | with `--trees` | with `--trees` | with `--trees` |
| smashables | with `--trees` | - | - |

How detail is shared out is the same in all three. Copies within 25 m of the
driving start at full detail, copies 25-60 m away one level coarser, and copies
further out at the coarsest level. Then the costliest models step down until a
triangle budget fits, and where even the coarsest levels do not fit a budget you
give, copies are left out. Kerbs are never simplified or left out. See
[Levels of detail and the budget](detail-budget).

## Options that shape the result

| Want | Use |
|---|---|
| a smaller file | `--no-textures` (flat colours), `--texture-size 1024` or `512`, `--detail-budget N`, `--margin 40` |
| just the ground | `--no-placed` |
| the scenery too | `--trees` |
| a different season (Forza) | `--season winter` |
| a game outside Steam | `--track` (Forza) or `--install` (BeamNG, AC Rally) |
| a lap the search does not place | `--level` (BeamNG, AC Rally), `--track` (Forza) |

## Coordinates

Each export writes metres with Y up, in a frame a recorded lap of the same game
lines up with:

| Game | Frame written |
|---|---|
| Forza | the game's own world coordinates, unchanged |
| BeamNG | `(x, z, -y)` of BeamNG's Z-up world, which is the rotation the telemetry recorder applies |
| AC Rally | the lap's frame, found by fitting: Unreal centimetres become metres, and Unreal X and Y become the lap's x and z in whichever of eight orientations fits |

See [Output format](output-format).
