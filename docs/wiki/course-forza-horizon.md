
# Course export: Forza Horizon

The Forza export reads the track straight out of the game's ForzaTech archives:
terrain with road, verge and grass told apart, a ground texture baked from the
game's own ground maps, and every placed model in its own texture (kerbs,
guardrails, tyre walls, signs, props, buildings).

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
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py).
The container formats themselves are on [ForzaTech](reader-forzatech).

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

## Terrain

How terrain is found (in `forzaterrain.py`):

- The manifests name terrain as a spatial index:
  `scene\tbheightfield\autoterrain_x-8184_z13299_cluster012.i.modelbin`.
- The two numbers are grid coordinates that **step by 1023**, and each grid step
  is a **512 m** tile. Tile `x-8184` is `-8184 / 1023 = -8`, which begins at
  `-8 * 512 = -4096` m. If you read the names as metres, every lookup misses by a
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

Measured on a test circuit's recorded laps, 99.2% of the samples land on
road-strip triangles, and 94.3% on the asphalt part once the mask has split off
the verge.

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
[ForzaTech](reader-forzatech)). If any vertex in the extraction lacks a
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
layout is on [ForzaTech](reader-forzatech#placement-files-pgeo).

### What is read

- Placement files are filtered **by name**: the cell size and cell position in the
  path give the cell's square (`x * size` to `(x + 1) * size`), and only cells
  overlapping the lap's box, in a wanted category, are opened.
- Categories by default: `barriers`, `props`, `signs`, `buildings`,
  `infrastructure`, `bridges`, `rocks`. `--trees` adds `trees`, `bushes` and
  `smashables`. These are never read: `grasstemplate`, `crowdtemplate` and
  `cwdspline` (grass and spectators), and `evolving` (festival sites that change
  with progression).
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

1. Slot `0x88B483AA` is the base colour in the standard environment shader (1,054
   of 1,054 sampled materials). If the material binds a texture there, that one is
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

### Detail and the budget

Distance bands, budget, and which copies go when the budget is too small are on
[Levels of detail and the budget](detail-budget).

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
```

## Writing the file

Parts are written in this order: per tile `terrain`, `verge`, `road` (each with
the tile's image), then `water`, `tyre marks`, `markings` (flat, the last two
lifted), then every placed part sorted by name. Coordinates are the game's own
(metres, Y up). See [Output format](output-format).

## What it costs

Approximate figures from the author's own runs:

| Course | Result |
|---|---|
| a country circuit (46 recorded laps) | about 225,000 terrain triangles on two tiles, 1.5 million placed triangles, about 10 s and 79 MB |
| a 14.7 km point-to-point sprint | a 1.53 km² corridor instead of a 22 km² box; 1.3 million terrain triangles, about a minute, 160 MB |
| a city street circuit, one lap | 3,400 barriers, 1,500 props, 700 signs, 174 whole buildings, 193 MB with a given budget; with the automatic budget a city corridor can reach 15 million placed triangles and about 660 MB |

A square kilometre of open-world terrain is about 1.16 million triangles.

## Checks behind it

These are measurements made while the reader was written, as stated in the
source. They are not re-run by the tests unless the game is installed.

- Across the recorded laps of a test circuit, the car sits a median 0.19 m above the extracted ground (sd 0.14 m, worst 0.58 m), which is the car's ride height.
- 600 of 600 sampled tiles land inside the 512 m square their name predicts.
- Consecutive guardrail placements are exactly 4.000 m apart, and 93.5% of guardrail ends land within 5 cm of the next one's start.
- Kerbs sit a median 3 cm above the extracted ground, faces up, within 5 m of the driving (also an installed-game test, see [Development](development)).

## Not drawn

- Trees and bushes unless `--trees`. Grass, crowds and festival sites never.
- Projected decal materials on models.
- Sign prints that are alpha-blended over their board come out opaque.
- The ground colour is a reconstruction of where asphalt, grass and woodland are, not the game's own terrain materials.
