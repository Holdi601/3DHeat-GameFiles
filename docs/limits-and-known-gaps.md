---
title: Limits and known gaps
nav_order: 7
---

# Limits and known gaps

What the tool does not do, what it does only partly, and where its behaviour is
uneven. Most gaps are deliberate refusals. Decoding with no file to check against
produces output that looks right and is not.

## Games

| Game | Course export | Why not, or how far |
|---|---|---|
| Forza Horizon | yes | ground colour is an interpretation (see below) |
| BeamNG.drive | yes | no ground cover, repeating model textures flattened |
| Assetto Corsa Rally | yes | models flat-coloured; not yet run on a lap recorded in the game |
| Assetto Corsa EVO | **no** | all content is in one package obfuscated with a key, and this tool recovers no keys |
| Battlefield 6 (level export, `level`) | yes, a whole level | terrain, grouped and individually placed meshes and their colour maps, the soldiers' navigation mesh, cut-out foliage; the play area's ground colour is coarse (32 m a pixel, or one average colour); no translucency, normal maps or per-copy texture variations |
| iRacing | **no** | tracks ship in a protected format that is not a file-extraction target |
| anything else | **no** | there is no course reader; reconstruct from gameplay with 3DHeat GameCapture, or analyse the laps in the viewer's Race tab without a course |

## Engines and formats

| Format | Not implemented |
|---|---|
| Unreal `.pak` | versions before 8; path-hash-only indexes (names cannot be recovered); entries in the index's overflow list (skipped); decoding `.uasset`/`.umap` contents from a pak |
| Unreal IoStore | encrypted containers (refused, no key option); listing a container without a directory index (it names no files); versioned packages; Nanite-only and non-inline meshes; skeletal meshes; properties of classes without a schema; instanced components' properties (layout changed in the game's build); spline meshes and decal components |
| Unity | formats before 22 (Unity 2019 and older); files with embedded type trees; compressed meshes; every class except `Mesh`, so no transforms, materials or scenes; `meshes` on a bundle; `list`/`extract` (use `meshes`) |
| Frostbite | XOR-obfuscated tables; the terrain's layer graph (masks read in 13 of 33 levels); object blueprints other than meshes (gameplay logic, effects, sounds); mesh levels stored inline; normal and other maps, alpha other than cut-outs; terrain holes; the type library (encrypted in the initial file system, not touched); a command to list or extract single assets |
| Source 2 | compiled assets (`.vmdl_c`, `.vtex_c`); the CS2 nav mesh (version 36) |
| ForzaTech | position formats other than four scaled shorts; index formats other than u16; texture codes other than 0, 9, 13; the terrain shader's material layers; tangents |
| BeamNG | skinned and decal meshes; animation; procedural ground cover; scenery round the edge of the world |

## Behaviour worth knowing

- **Forza ground colour is not the game's.** The baked texture is drawn from the
  tile maps that say *where* asphalt, short grass, rough ground and woodland are.
  It uses fixed colours and shading, because the terrain shader's own material
  layers are not decoded.
- **`--no-textures` also removes Forza's verge.** The asphalt/verge split uses the
  asphalt mask that comes with the baked maps. Without textures, road strips stay
  whole as road.
- **A budget you give can only be exceeded by kerbs.** Kerbs (and BeamNG's
  driving-surface models) are never simplified or left out, in any game, so a
  `--detail-budget` smaller than they cost is exceeded by them alone; everything
  else is left out first. See [Levels of detail and the budget](detail-budget.md).
- **Options that do not apply are ignored silently**: `--season` for BeamNG and
  AC Rally, `--track` for BeamNG and AC Rally, `--level`/`--install` for Forza.
- **A Battlefield 6 level's ground colour is coarse away from its decals.** The
  heightfield is coloured from the terrain backdrop's colour map, 32 m a pixel at
  the largest mip the level ships — or, where no backdrop map covers it, in the
  middle colour of the terrain's surface materials; `--ground-texture`
  multiplies that by the terrain's colormap (at 0.5 m a pixel where the level
  has one) and bakes the roads, aprons and
  markings over it, with markings drawn through channel
  masks in a neutral paint colour. The game mixes its surface layers in a
  shader graph that is not read; the export lays the layers' colours by their
  masks and the heightfield's slope, by a rule of its own, and a level whose
  mask pages do not fit together (18 of 33) gets one colour. Each layer is
  its colour map's mean, not its texture. See
  [Frostbite](reader-frostbite.md#terrain-layers). Pieces of the
  heightfield at different resolutions meet with small steps.
- **A Battlefield 6 colour map is chosen, not read.** A shader block names
  every texture it samples without saying which is the colour; the choice goes
  by name (see [Frostbite](reader-frostbite.md#textures-and-materials)) and can
  pick a trim or detail sheet for a surface. Decal sheets (`t_de_...`) lose to
  the surface's own map; a sign's decal drawn as its panel showed its shield
  turned a quarter. Distance fields, palettes and channel masks are never
  taken. Backdrop buildings are drawn in their palette's colours; grey maps
  take the material's tint by a rule of the exporter's own, as the
  parameters' names are hashed, and a material that paints a grey map
  through a mask with several tints gets one of them.
- **The navigation mesh is the AI's, not the players'.** It covers what a
  soldier can walk to: in the level checked the ground, floors and stairs, and
  some roofs, but not the tops of freight containers. The links between surfaces (jumps, ladders, vaults) are left out.
- **A Battlefield 6 level includes every game mode's layer.** Objects that only
  one mode places can overlap another's. `--skip` leaves layers out by name.
- **`courses` is Forza only**, and only picks up library folders named
  `... (course_...)`.
- **The BeamNG lap frame is assumed** to be the viewer frame `(x, z, -y)` that the
  3DHeat recorder writes. Laps from another recorder in BeamNG's raw frame would
  not be placed.
- **`list` and `extract` take the archives, not every format.** They open a
  `.pak`, an IoStore `.utoc`, a `.vpk`, a `.minizip` and a zip. A Unity container
  is read with `meshes`, a Frostbite level with `level`, and a `.cdae` or
  `.ter` is a file rather than an archive (`identify` names it). A `.minizip`
  without its `ChunkContentsMiniZip<n>.txt` beside it lists by entry number.
- **Placed models in BeamNG use repeating textures as average colours**, because
  the `.glb` sampler clamps and the viewer packs textures into an atlas.
- **Windows only, in practice.** Steam paths under `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames`, and a `*_win64.dll` for Oodle. Other platforms
  are untested.

## Unverified

- Older Python versions (the tool has been run with 3.13).
- Assetto Corsa Rally with a lap recorded in the game. It has been tested only
  with synthetic laps in random frames.
- glTF viewers other than the 3DHeat viewer.
- Whether each game's frame is left- or right-handed. The export keeps each
  game's telemetry frame, so laps and courses line up regardless.
- The meaning of `WaterBlock`'s local z = 0 as its surface (BeamNG).
- Frostbite placement on games other than Battlefield 6, and on Battlefield 6
  after an update that changes the group member's layout. The reader then finds
  no groups and says so.
- Whether a Battlefield 6 export lines up with positions the game reports. The
  coordinates are the game's own, as for the other games, but no recording has
  been laid over one yet.
