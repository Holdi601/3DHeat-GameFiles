
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
| iRacing | **no** | tracks ship in a protected format that is not a file-extraction target |
| anything else | **no** | there is no course reader; reconstruct from gameplay with 3DHeat GameCapture, or analyse the laps in the viewer's Race tab without a course |

## Engines and formats

| Format | Not implemented |
|---|---|
| Unreal `.pak` | versions before 8; path-hash-only indexes (names cannot be recovered); entries in the index's overflow list (skipped); decoding `.uasset`/`.umap` contents from a pak |
| Unreal IoStore | encrypted containers (refused, no key option); listing a container without a directory index (it names no files); versioned packages; Nanite-only and non-inline meshes; skeletal meshes; properties of classes without a schema; instanced components' properties (layout changed in the game's build); spline meshes and decal components |
| Unity | formats before 22 (Unity 2019 and older); files with embedded type trees; compressed meshes; every class except `Mesh`, so no transforms, materials or scenes; `meshes` on a bundle; `list`/`extract` (use `meshes`) |
| Frostbite | XOR-obfuscated tables; payloads that are not block chains (about a quarter of a sample); the mesh format; a command to list or extract |
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
  else is left out first. See [Levels of detail and the budget](detail-budget).
- **Options that do not apply are ignored silently**: `--season` for BeamNG and
  AC Rally, `--track` for BeamNG and AC Rally, `--level`/`--install` for Forza.
- **`courses` is Forza only**, and only picks up library folders named
  `... (course_...)`.
- **The BeamNG lap frame is assumed** to be the viewer frame `(x, z, -y)` that the
  3DHeat recorder writes. Laps from another recorder in BeamNG's raw frame would
  not be placed.
- **`list` and `extract` take the archives, not every format.** They open a
  `.pak`, an IoStore `.utoc`, a `.vpk`, a `.minizip` and a zip. A Unity container
  is read with `meshes`, a Frostbite table only from Python, and a `.cdae` or
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
- Frostbite packages with more than one installation package. The first
  `cas_NN.cas` large enough to hold the record is used.
