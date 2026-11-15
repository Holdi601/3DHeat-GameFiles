---
title: Forza Horizon
parent: Course export
nav_order: 1
---

# Course export: Forza Horizon

The Forza export reads the track straight out of the game's ForzaTech archives:
terrain with road, verge and grass told apart, a ground texture baked from the
game's own ground maps, and every placed model in its own texture (kerbs,
guardrails, tyre walls, signs, props, buildings). It also finds which of the
game's races the lap was driven on and adds what the game puts out for that race
alone (its event layer: barriers, tents, gantries, stands, flags), and the
ground of any venue the driving passes through, such as a stadium's floor.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Sources: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
The container formats themselves are on [ForzaTech](reader-forzatech.md).

## Finding the installed game

Nobody should have to type a path like
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, so the path is worked out:

1. **Steam libraries.** Steam's `config\libraryfolders.vdf` is read from
   `C:\Program Files (x86)\Steam` or `C:\Program Files\Steam`, and every `"path"`
   entry in it is a library. Each library's `steamapps\common` is searched.
2. **Microsoft Store.** `C:\XboxGames` is searched if it exists. There the game
   sits one level further down, in `<game>\Content`.
3. A **game folder** is any child of those folders that has a `media\Tracks`
   folder, whatever its name.
4. A **track folder** is any folder under `media\Tracks` that holds a
   `GeoChunk0.minizip`. It counts by its contents, not its name, so a track under a
   name nobody has seen is still found.

If the game is somewhere else, pass the track folder with `--track`; see
[Troubleshooting](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` skips all of this.

A track folder holds what the export reads:

| File | What it is |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | the archives: every model, texture and placement file, with no names inside |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | one line per archive entry, in entry order: the only source of names |
| `AssetManifest.xml` | every texture the track ships, with the hash materials refer to it by |

## Which track

A game ships more than one track folder (the open-world map, a garage or two).
The right one is chosen by **coordinates, not by name**:

- The lap's bounding box, widened by `--margin`, is the question.
- For each track folder, the four `ChunkContentsMiniZip*.txt` manifests are read
  as text, without opening an archive. Every terrain tile name
  (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) carries its grid position.
  The tool counts how many distinct tiles fall inside the box.
- The track with the most tiles there wins. If no track has any, the export stops
  with "none of the installed tracks (...) has terrain at x ..., z .... Those are
  the game's own metres, as its telemetry reports them."

A whole track answers in well under a second. A name match could pick the wrong
map, and a wrong map looks as plausible as the right one.

The console says `on <track>, in <game folder>`.

## Which race

The game ships each of its races as a route with a number, its **route id**. Two
files belong to each route:

| File | What it holds |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | the race's AI driving line: a 56-byte node per point from byte `0x60`, the node count at `0x24`, each node starting with its position (x, y, z) in the game's metres |
| `media\Stripped\gs\<map>\routedefinitions.zip` | one `route<id>_<map>.rtd` per race: plain XML listing what the race adds to the world and what it takes away (see [The race's own layer](#the-races-own-layer)) |

The lap is matched to a route by comparing it with every AI line whose box
overlaps the lap's:

- From each lap sample, the distance to the nearest point of the line; and from
  each point of the line, the distance to the nearest lap sample.
- The two medians are added. The route with the smallest sum wins if the sum is
  under **30 m** (`MATCH`).
- Both directions are needed: a short sprint lies along a long route that uses
  the same road, and a long lap covers a short route.

The console says `the game's route <id> (driven line within <n> m of it)`, or that
no route matches. With no match, only the free-roam world is placed.

## Terrain

How terrain is found (in `forzaterrain.py`):

- The manifests name terrain as a spatial index:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- The two numbers are grid coordinates that **step by 1023**, and each grid step
  is a **512 m** tile. Tile `x-2046` is `-2046 / 1023 = -2`, which begins at
  `-2 * 512 = -1024` m. If you read the names as metres, every lookup misses by a
  factor of two and still returns terrain, from the wrong part of the map.
- A tile may appear three times: plain, `_cb` and `_ul`. All three cover the same
  ground. One is taken per tile, in that order of preference, because merging
  them would triple the geometry into coincident surfaces.
- A tile is read only if it touches the lap's box **and** the corridor. A tile
  the corridor does not touch is never decompressed.
- Every `.modelbin` of a chosen tile is decoded at **level of detail 0 only**. A
  tile carries four levels over the same ground, and exporting them all puts the
  same square metre in the file four times.
- Each mesh carries its own world-space scale and bias, so a tile lands where the
  game puts it with no instance transform. Triangles whose footprint overlaps the
  box are kept, then only those reaching into the corridor.
- A mesh in a format the reader refuses is skipped and counted
  (`N meshes could not be read`), so a thin result says why.

The terrain summary prints the vertex count, triangle count, mesh count, tile
count and the x/y/z extent.

### Road, verge, terrain, markings, water

Material names cannot say where the road is. Around a circuit, 94% of the ground
uses a road-shader material, because terrain near a road is drawn with it and the
shader decides asphalt or grass per pixel. So:

| Kind | Decided by |
|---|---|
| road strip | the **vertex layout**: road strips are the only ground with a second UV set (channel 1); a triangle whose three vertices all have it is road |
| asphalt vs verge | within a road strip, the tile's **asphalt mask** at the triangle's centroid: 0.5 or more is `road`, less is `verge` |
| markings | material name matching `whiteline`, `yellowline` or `decal` |
| tyre marks | material name matching `tyremark` or `skid` (checked before markings, because tyre marks ship as `tyremark_decal_*`) |
| water | material name matching `water`, `lake`, `river`, `paddy`, `ocean` or `sea` |
| terrain | everything else |

Measured on the test circuit's recorded laps, nearly all samples land on
road-strip triangles, and the large majority on the asphalt part once the mask
has split off the verge.

The asphalt mask only exists when ground textures are baked. With
`--no-textures`, or for a tile whose maps are missing, road strips stay whole as
`road` and no verge is split off. Missing maps cost detail, never geometry.

### Painted layers are lifted

Lane markings and tyre marks ship as their own triangles lying exactly in the
road. The game draws them with a depth bias. Drawn as they are, road and paint
fight over every pixel. The export gives each marking and tyre-mark part its own
copy of its vertices, lifted **5 cm** (`DECAL_LIFT`) along the surface normal, so
the road under it is not lifted too.

### Normals

Terrain normals come from the archive. The normal's x is stored as the
position's fourth short, and its y and z in the `NORMAL` attribute (see
[ForzaTech](reader-forzatech.md)). If any vertex in the extraction lacks a
normal, normals for the whole ground are computed from the triangles instead.

## The ground texture

Each terrain tile ships three maps covering its 512 m square, in five resolutions
(`_quality1` to `_quality5`, the largest 2048 px, which is 25 cm a pixel):

| Map | File name pattern | What it holds (as measured) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detail normal (x, z). A: lower on asphalt and on rough ground |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | layer weights. B: high on asphalt (239 on the driven line, 165 beside it) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: low on asphalt (147 vs 215). B: rises in woodland |

None of these is a colour photograph. They are the inputs the game's terrain
shader blends its material layers with, and those layers are not decoded. So the
baked texture is **an interpretation, not a copy of the game's look**. It keeps
*where* each kind of ground is, at 25 cm, and paints it in fixed colours:

| Ground | Linear RGB | Weight |
|---|---|---|
| grass (short, near the track) | 0.30, 0.44, 0.18 | the base |
| rough (further out) | 0.40, 0.42, 0.22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| woodland | 0.13, 0.23, 0.10 | `smoothstep(4 -> 24, gloss.B)` |
| asphalt | 0.20, 0.20, 0.21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Both maps have to agree for asphalt. Either one alone leaves grey speckle in the
grass wherever block compression rings. The result is shaded by the main map's
detail normal against a fixed light (`0.55 + 0.6 * lambert`), so kerb lips, banks
and ruts read as relief, and written as 8-bit sRGB.

Orientation: pixel row 0 is the tile's **north** edge (largest z), column 0 its
**west** edge (smallest x). This was found by projecting recorded laps onto the
asphalt mask in all eight ways a square can be flipped or turned. Exactly one way
puts them on asphalt. The UVs follow from that: `u = (x - x0) / 512`,
`v = 1 - (z - z0) / 512`.

The maps are read at the best resolution available up to quality 5 and resampled
to the main map's size. If the colour image is larger than `--texture-size`, it is
then shrunk to that size with Lanczos filtering. The asphalt mask is always kept at full resolution, because it
decides geometry. `--season` picks the `x<season>x` maps. A tile with no maps for
that season is drawn in flat colours, and the console reports
`N without maps`.

## Placed models

Terrain carries its own world position. Nothing else does. Where each copy of a
model stands is recorded in `.pgeo` placement files, one per category per spatial
cell:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. The record
layout is on [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### What is read

- Placement files are filtered **by name**: the cell size and cell position in the
  path give the cell's square (`x * size` to `(x + 1) * size`), and only cells
  overlapping the lap's box, in a wanted category, are opened.
- Categories by default: `barriers`, `props`, `signs`, `buildings`,
  `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` adds `trees`,
  `bushes` and `smashables`. These are never read: `grasstemplate`,
  `crowdtemplate` and `cwdspline` (grass and spectators: the game draws them as
  animated sprites, there is no geometry).
- Each file belongs to a **layer**, read from its name after
  `c<size>_<category>_`. A level-of-detail word (`do`, `so`, `ulc`, `ulp`, `cwd`)
  and an optional section number is the free-roam world. Anything else is a
  layer the game switches on: a runtime layer (`rt_0`), an activity
  (`_tag_<name>_`), a collectible, anything filed under `evolving`. A layer
  that names routes (`rt_x<id>`, for example `rt_x1023_x2201`) belongs to those
  races only, and is read only when the lap matched one of them. See
  [Switched-on layers](#switched-on-layers).
- A copy is kept if its position is inside the box and inside the corridor.
  Exact repeats (the same position and orientation to the millimetre, listed by
  two neighbouring cells) are merged.
- **Kerbs** are props whose model name starts with `road_gen_rum` (rumble
  strips). They are written as `ground:kerbs`, never simplified and never left
  out, because a lap is measured against them.

| Category | Part | Fallback colour (no texture) |
|---|---|---|
| kerbs | `ground:kerbs` | 0.60, 0.12, 0.10 |
| barriers | `structure:barriers` | 0.50, 0.50, 0.50 |
| props | `structure:props` | 0.45, 0.35, 0.25 |
| signs | `structure:signs` | 0.70, 0.70, 0.70 |
| buildings | `structure:buildings` | 0.55, 0.52, 0.48 |
| infrastructure | `structure:infrastructure` | 0.45, 0.45, 0.47 |
| bridges | `structure:bridges` | 0.45, 0.45, 0.45 |
| rocks | `structure:rocks` | 0.30, 0.28, 0.25 |
| smashables | `structure:smashables` | 0.12, 0.22, 0.06 |
| trees, bushes | `structure:trees` | 0.10, 0.20, 0.05 |

### The model's geometry

A placed name `<model>_3D` refers to the model files `<model>_cluster###.i.modelbin`
(up to a dozen). Each triangle carries a mask of the detail levels it belongs to:

- A model's levels are its triangles explicitly marked for that level. Levels run
  contiguously from 0, finest first.
- Triangles marked `0xFFFF` (every level) are the breakable pieces, such as a
  guardrail's posts or a tyre stack's single tyres. They overlap the whole model,
  and the game draws them instead of it once it is knocked apart. They are used
  only by a model with no explicitly marked level.
- Submeshes whose material shader is a projected **decal** are left out.

Each copy is placed with its position, its x and y axes from the record
(z = x cross y), and its scale. Normals are transformed with the inverse scale.

### Which texture

A material does not name its textures. It lists them as hashes, and the track's
`AssetManifest.xml` maps each hash (`SourceHash`) to a texture name. Only the
`<Textures>` section is read, which stops reading at `</Textures>` in a file that
can be tens of megabytes. Then:

1. Slot `0x88B483AA` is the base colour in the standard environment shader (every
   sampled material). If the material binds a texture there, that one is
   used.
2. Otherwise the texture's own kind decides, which is the word before its GUID:
   `_bclr_`, then `_diff_`, then `_colour_`.
3. Terrain maps (`mainmap`, `submap`, `autogloss`) and tint palettes (`tint`,
   `worldtint`) never colour a model.

So a model is coloured by what its material binds, not by a texture named like
the model. For example, `bar_rur_armco_crct_02_c` uses `..._02_a`'s texture.

The texture is read from the archives at the smallest resolution at least
**256 px** across (`MODEL_TEXTURE`), shrunk to 256 if larger, and stored as RGB
JPEG in the `.glb`. A guardrail's colour at 256 px for four metres is 1.6 cm a
pixel, and around 80 such textures fit in the viewer's atlas beside the ground
tiles.

**Seasons.** `--season` swaps a texture for its seasonal twin by name, with the
GUID ignored (`..._xsummerx_bclr` to `..._xwinterx_bclr`, or `..._bclr` to
`..._winter_bclr`), when the track has one. With `--season winter`, a submesh's
winter material is also used where its variant table names one.

**Variants.** A submesh record opens with a table of `(summer, winter)` materials,
one per look a copy can wear: five prints for a billboard, six paint colours for a
tyre stack. Each placement record says which variant that copy wears. A submesh
with fewer variants than the model repeats its own.

**The placeholder block.** Shared building atlases reserve a solid
RGB (255, 64, 0) block for surfaces the building shader tints from other textures.
If more than a twentieth of a texture is within 12 levels of that colour, the
block is repainted in the texture's own average colour. Otherwise a city comes
out orange.

### See-through surfaces

Chain-link fences and nets are single quads with holes in the texture's alpha.
Drawn solid, a fence is a wall across the view of the track. Surfaces whose
material shader matches `alphatest`, `alphablend`, `transmissive`, `anim_flag`,
`impostor`, `branch`, `bush` or `tree` are tested:

- The texture's opacity is averaged over a 32 x 32 grid.
- Per surface (every cut-out triangle sharing one texture), four points per
  triangle are sampled in UV space and weighted by the triangle's UV area.
- If the average opacity is at least 0.05 and below **0.5**, the whole surface is
  left out. Below 0.05 the alpha clearly means something else to its shader (a
  warning sign that samples 0.01), and the surface is kept solid.
- A model whose every surface was left out is reported:
  `N models left out as see-through (mostly holes in their texture)`.

The tool judges the whole surface rather than one triangle at a time. Judged
per triangle, half of every quad survived and fences came out as rows of teeth.

### Buildings drawn whole

A city builds its buildings from modular pieces: hundreds of thousands of them
around one street circuit, tens of millions of triangles even at their coarsest.
Leaving pieces out one at a time left lone wall slabs standing. The game also
ships whole-building stand-ins in `scene\hlod_tier_1\`, one mesh per building
(stem `hlod_tier_1_*`), already in world coordinates like the terrain:

- Each stand-in's world box is read from its mesh's position box (a header read,
  not a decode). This takes seconds for a whole map.
- Stand-ins touching the lap's box and the corridor are used.
- Every `buildings` piece whose position falls inside a stand-in's footprint
  (plus 0.5 m) is dropped, and the stand-in is drawn instead. Its distance to the
  driving is measured to the building's nearest edge.
- The summary says `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Switched-on layers

What a switched-on layer places is exported, but apart from the free-roam world,
so the viewer can show it or hide it:

| Layer | Part |
|---|---|
| the free-roam world | `structure:<category>` (as before) |
| a layer naming the matched race's route | `structure:event_<category>` |
| any other switched-on layer | `structure:layer_<category>` |

The summary counts them: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Models already in world coordinates

A few kinds of model are not in any placement file. Their meshes carry their own
world position, as terrain does, so nothing has to place them:

| Folder under `scene\models\` | What it is | Part |
|---|---|---|
| `plots` | a venue's own ground: a stadium's floor and infield, a festival site, a plaza | `ground:venue` |
| `plinths` (and any model named `floor`, `ground` or `road`) | ground a street is dressed with: planters, steps, a park's paving | `ground:plinths` |
| `hda_infrastructure` (bridges) | procedurally built bridges | `structure:bridges` |

- A model counts as being in world coordinates when the middle of its box lies
  more than **300 m** (`WORLD_REACH`) from its own origin. Models placed by the
  placement files sit within a couple of hundred metres of theirs.
- Not drawn: occluders, cables strung along the roads, the sea's backdrop,
  the roofs and occluders of modular buildings (the stand-ins draw those
  buildings), collision and water volumes.
- Each is read from the box of its meshes (a header read), a few seconds for a
  whole map, once per run.
- Ground parts are never drawn coarser and never left out to fit the budget,
  like kerbs.

**A venue is cut whole.** When the driving touches a venue's own ground
(`ground:venue`), the corridor is widened to that ground's whole footprint plus
`--margin`, so the stands, walls and barriers around a stadium come with it, not
only the strip the laps used. The console says
`through a venue (<model names>): cutting all of its ground, <n> km2`. Plinths
do not widen the cut.

### Detail and the budget

Distance bands, budget, and which copies go when the budget is too small are on
[Levels of detail and the budget](detail-budget.md).

### Placement summary

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## The race's own layer

Many races put out things that are not there in free roam: concrete walls and
fences that close off side roads, tyre stacks, tents, a start gantry,
grandstands, flags, banners. Each race lists them in its route definition
(`route<id>_<map>.rtd` in `routedefinitions.zip`, plain XML in a plain zip):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **What is added.** Each instance is placed like a placement-file copy. The
  transform's 16 numbers are four rows: the model's x, y and z axes (each scaled)
  and its position in the game's metres. The third row is the cross product of the
  first two. `Material` is the variant the copy wears. The part is
  `structure:event_<kind>`, `<kind>` being the folder under `scene\models\`
  (barriers, props, infrastructure, signs; anything else counts as props), and the
  node carries the glTF extras `{"layer": "event", "route": <id>}`.
- **What is taken away.** A free-roam copy standing within **0.1 m** of a hidden
  asset's position is left out. A hidden asset standing at the origin is a model
  in world coordinates; its instance GUID is looked up in the track's
  `AssetManifest.xml` (the `<Models>` list: a model's source, then the GUIDs of
  its copies) to name it.
- **Ground the race hides is kept.** A race that hides a venue's ground lays its
  own surface there. When that surface is not among the models the track ships,
  the hidden ground stays, as the nearest thing to what is driven on, and the
  summary says so (`kept <model>: the race hides it for a surface of its own
  that the track does not ship`).
- **Not drawn, but counted.** Spectator markers (`crowd_proxies`: the game draws
  the crowd as sprites from them) and collision splines (`.splinecol`). The
  console lists them: `its own layer: <n> copies of <m> models, <k> free-roam
  objects hidden; not drawn: ...`.
- Route assets the track does not ship a model for (light glows, some signs,
  content the game streams in) are named in `placed names have no model in the
  archives`.

Only copies inside the corridor are placed, as for everything else.

## Writing the file

Parts are written in this order: per tile `terrain`, `verge`, `road` (each with
the tile's image), then `water`, `tyre marks`, `markings` (flat, the last two
lifted), then every placed part sorted by name. Coordinates are the game's own
(metres, Y up). See [Output format](output-format.md).

The file says what it holds in its glTF `asset.extras`:

| Field | Meaning |
|---|---|
| `course_format` | `2`: the race's own layer, venues and world-space models are in it. [`courses`](commands.md#courses) exports a file with a lower number (or none) again |
| `route` | the matched route id, or `null` |
| `event_copies`, `event_kinds` | how many copies of the race's own layer were placed, and their kinds |
| `hidden` | free-roam copies left out because the race removes them |
| `venue` | the venue ground models the driving passes through |
| `layers` | the switched-on layers placed |

## What it costs

Rough orders of magnitude:

| Course | Result |
|---|---|
| a short country circuit | a few hundred thousand terrain triangles, over a million placed ones; seconds, under 100 MB |
| a long point-to-point sprint | the corridor is a small fraction of the box around it; about a minute, a few hundred MB |
| a city street circuit | thousands of barriers, props and signs and whole buildings; with the automatic budget up to several hundred MB |

A square kilometre of open-world terrain is about a million triangles.

## Checks behind it

These are measurements made while the reader was written, as stated in the
source. They are not re-run by the tests unless the game is installed.

- On the test circuit, the car sits about its ride height above the extracted ground (median under 0.2 m).
- Every sampled tile lands inside the 512 m square its name predicts.
- Consecutive guardrail placements are exactly 4 m apart, and most guardrail ends land within 5 cm of the next one's start.
- Kerbs sit a few centimetres above the extracted ground, faces up, within 5 m of the driving (also an installed-game test, see [Development](development.md)).

## Not drawn

- Trees and bushes unless `--trees`. Grass and crowds never (the game draws them as sprites).
- A race's own models that the track does not ship (see [The race's own layer](#the-races-own-layer)).
- Projected decal materials on models.
- Sign prints that are alpha-blended over their board come out opaque.
- The ground colour is a reconstruction of where asphalt, grass and woodland are, not the game's own terrain materials.
