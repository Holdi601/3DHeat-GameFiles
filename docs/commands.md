---
title: Commands
nav_order: 2
---

# Commands

Every command runs as `python -m heat3d_gamefiles <verb> ...` from the repository
folder. The verbs come in the order you usually need them: what is this file, what
is inside it, give me that, and turn a lap into a course.

| Verb | Takes | Does |
|---|---|---|
| [`identify`](#identify) | any file | names the container format by reading its bytes |
| [`list`](#list) | an Unreal `.pak` or IoStore `.utoc`, a Source 2 `.vpk`, a ForzaTech `.minizip`, or a zip | lists its entries |
| [`extract`](#extract) | the same | writes one entry to disk |
| [`meshes`](#meshes) | a Unity `SerializedFile` | lists and checks its meshes |
| [`course`](#course) | a lap | exports the course around it (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | a recorded lap library | runs `course` on every course in it (Forza) |
| [`terrain`](#terrain) | a Forza track folder | cuts a region by world coordinates |
| [`levels`](#levels-and-level-frostbite) | an installed Frostbite game | lists its levels |
| [`level`](#levels-and-level-frostbite) | a level's name | exports the level: terrain, placed meshes, optionally their colour maps (Battlefield 6) |

Each time the program starts, it may check for a newer release first. See
[Updates](updates.md). `HEAT3D_NO_UPDATE=1` turns that check off.

Source: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | the work failed (unreadable lap, no game found, nothing to export, a course in `courses` failed; for `list` and `extract`, a file that is none of the archives they read, one that cannot be opened or read - an encrypted pak without `--key`, an encrypted IoStore container - or an entry not in the archive) |
| 2 | bad arguments (argparse), a path that does not exist, a `--key` that is not 64 hex digits, or `terrain` given both or neither of `--box` and `--route` |

The failures of `list` and `extract` are each one line on standard error, not a
Python traceback.

---

## identify

```
python -m heat3d_gamefiles identify <path>
```

This reads the file and says which container it is. It does not go by the
extension (the one exception is a `.ucas`, below). It tries the formats in this
order and stops at the first that parses:

1. **Unreal `.pak`**: a footer with the pak magic in the last 1,024 bytes. Prints
   the version, the index offset and size, whether the index is encrypted, and the
   compression methods.
2. **Unreal IoStore `.utoc`**: the IoStore magic at its start. Prints the version,
   the chunk count and whether the container is encrypted; for one that is not,
   the number of files its directory names (and under which mount point), the
   compression methods, and whether its `.ucas` is beside it. A `.ucas` carries no
   header of its own, so it is recognised by the `.utoc` of the same name beside
   it, and `identify` names that file.
3. **ForzaTech `.minizip`**: the `PGZP` magic. Prints the version, the entry and
   segment counts, and whether the `ChunkContentsMiniZip<n>.txt` that names the
   entries is beside it (and, if so, whether it names as many as there are).
4. **zip**: a zip local file header at the start. Prints the entry count, the six
   most common extensions, and the level names when entries lie under
   `levels/<name>/`, as in a BeamNG.drive level archive.
5. **Unity**: a `UnityFS` bundle (prints the engine version and entry count) or a
   bare `SerializedFile` (prints the format, engine version, object count and the
   six most common classes).
6. **Frostbite `.toc`**: prints the kind (`plain` or `signed`), where the tree
   begins, and either the asset count (binary section table) or the superbundle
   count (DbObject tree).
7. **Source 2 `.vpk`**: prints the version, the entry count, and the first `.nav`
   navigation mesh if the archive has one.
8. **BeamNG `.cdae`**: shape version 31 that parses. Prints the mesh count, the
   number of drawn levels of detail and the first materials.
9. **BeamNG `.ter`**: there is no magic, so all of it has to add up - a side of 2
   to 16,384, that many squared heights and layer bytes, then 1 to 255 printable
   layer names. Prints the version, the size and the layer names.
10. **ForzaTech `.modelbin`**: prints the version, the chunk count and the six
    most common chunk tags. Chunk contents are not decoded here.

The formats with a magic of their own (2 to 4) come before Unity and Frostbite,
whose checks read the whole file: a Forza archive is tens of gigabytes.

If none of them matches, it prints `not a format this tool reads` and the last
reason. That reason comes from the ForzaTech check.

Example (synthetic):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Option | Default | Meaning |
|---|---|---|
| `<archive>` | required | an Unreal `.pak`; an IoStore `.utoc` (or the `.ucas` beside it); a Source 2 `.vpk` (for split VPKs, the `_dir.vpk`); a ForzaTech `.minizip`; a zip, such as BeamNG's level and content archives |
| `--filter TEXT` | none | only paths containing TEXT, case-insensitive |
| `--limit N` | 50 | print at most N entries (the total count is always printed) |
| `--key HEX` | none | an AES-256 key you already hold, 64 hex digits, with or without `0x`. Only an encrypted `.pak` uses it. Anything that is not 64 hex digits is refused before the archive is opened (exit code 2) |

The tool decides the format from the bytes: an IoStore table of contents, a
`.minizip` and a VPK by the signature they start with, a zip by its local file
header, and a `.pak` by the footer at its end. A `.ucas` has no header and is
opened through the `.utoc` of the same name. A file that is none of these is
refused with `<file> is not an archive list and extract read (...)`. One that is
but cannot be opened is refused with the reader's reason: an encrypted pak without
`--key`, an encrypted IoStore container, a pak version it does not read. Either
way it is one line and exit code 1.

Each line shows the uncompressed size, the compression method, and the path:

| Archive | Method | Paths |
|---|---|---|
| `.pak` | `none`, or the name from the footer (`Zlib`, `Oodle`, `Gzip`...) | with the archive's mount point, for example `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, or the container's method (`Oodle`, `Zlib`...), as its first block is stored | with the mount point, for example `../../../<Project>/Content/...`. A container without a directory index names no files and is refused |
| `.vpk` | always `stored` | as in the directory |
| `.minizip` | `lz4`, `deflate` or `stored` | as the `ChunkContentsMiniZip<n>.txt` beside `GeoChunk<n>.minizip` spells them, build-machine prefix removed (backslashes, as the game writes them). The archive stores no names, so without that file entries are `#0`, `#1`... A list whose line count differs from the entries is refused: the two do not belong together |
| zip | `stored`, `deflate`, ... | as stored; folders are not listed |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Option | Default | Meaning |
|---|---|---|
| `<archive>` | required | as for `list` |
| `<entry>` | required | the path exactly as `list` prints it (case-sensitive); in a `.minizip`, `#<number>` works too |
| `--out FILE` | the entry's file name (after the last `/` or `\`), in the current folder | where to write; parent folders are created |
| `--key HEX` | none | as for `list` |

The entry is decrypted (pak, with a key), decompressed, and written out. It prints
`<bytes> bytes -> <file>`. If the path is not in the archive, the command exits
with code 1. So does an entry that cannot be read (an encrypted entry without a
key, Oodle-compressed with no Oodle library), with the reason in one line. A VPK entry is not checked against its CRC here. The reader has a
`verify()` method for that (see [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Option | Default | Meaning |
|---|---|---|
| `<path>` | required | a bare Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), not a bundle |
| `--limit N` | 25 | decode and print at most N meshes |

This prints the number of `Mesh` objects, then one line per mesh: the name (first
40 characters), the vertex and triangle counts, and `ok` or `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` means the decoded vertices do not reproduce the bounding box
Unity stored for the mesh, within 2% of the box size. That is the parse's own
check (see [Unity](reader-unity.md)). A mesh that cannot be read is reported with
the reason and counts towards the limit. Vertex data in a `.resS` file is read
from the folder the container is in.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

This exports the course around a lap: the ground in a band either side of the
driving, and what stands on it, as one `.glb`. It works out the rest itself: which
game, which installed copy, which track, level or stage, and (for Assetto Corsa
Rally) which way round the axes are. See [Course export](course-export.md).

`<lap>` can be any of the following (details in [Lap inputs](lap-inputs.md)):

- a lap file: route JSON, FH Companion lap JSON, `heat3d-lap` JSON, `.npz`, or `.csv` with x, y, z columns
- a folder of lap files, searched recursively (a whole recorded course)
- a course **name**, looked up in the FH Companion library at `%LOCALAPPDATA%\FHCompanion\laps`

### Options

| Option | Default | Games | Meaning |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` in the current folder | all | where to write; the name is lower-cased, with runs of other characters turned into `_` |
| `--game {forza,beamng,acrally}` | what the lap file says, else `forza` | all | which game the lap is from |
| `--margin M` | 80 | all | metres of ground kept either side of the driving |
| `--texture-size {2048,1024,512}` | 2048 | all | ground texture pixels per 512 m tile (2048 = 25 cm a pixel) |
| `--no-textures` | off | all | flat colours only: a far smaller file. For Forza this also skips the road/verge split (see below) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | which season's ground maps and model textures |
| `--no-placed` | off | all | terrain only: no kerbs, barriers, signs, buildings. For BeamNG, driving surfaces modelled as meshes are still kept |
| `--trees` | off | all | also place vegetation (Forza: trees, bushes and smashables; BeamNG: trees; AC Rally: trees and the instanced foliage) |
| `--detail-budget N` | automatic | all | a ceiling on triangles for everything placed; see [Levels of detail and the budget](detail-budget.md) |
| `--track DIR` | searched | Forza | the track folder (under `media\Tracks`, holding `GeoChunk0.minizip`) if the installed game should not be searched |
| `--level NAME` | found from the lap | BeamNG, AC Rally | the level (BeamNG folder name) or stage (AC Rally map name), case-insensitive |
| `--install DIR` | searched in Steam libraries | BeamNG, AC Rally | BeamNG: the folder holding `gameengine.zip`. AC Rally: the game folder, or its `acr\Content\Paks` / `Content\Paks` |

Options that do not apply to a game are ignored without a warning. For example,
`--season` does nothing for BeamNG and AC Rally, and `--track` does nothing for
them either.

### Which game

The game is taken from `--game`, then from the `game` field of a `heat3d-lap`
file (or of a CSV's `# {...}` description line), then defaults to Forza. A folder
gets the game its files name, when they name only one; a file that names none
(an FH Companion lap, `course.json`, a CSV without a description line) does not
count (see [Lap inputs](lap-inputs.md)).

| Value | Export |
|---|---|
| starts with `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` or `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | refused: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | refused: "tracks ship in a protected format that is not a file-extraction target" |
| anything else | refused: "there is no course reader for <game> yet" |

A refusal also suggests the alternatives: reconstruct the course from gameplay
(3DHeat GameCapture), or analyse the laps without a course, because the viewer's
Race tab draws a road from them.

### Examples

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Example output (Forza, synthetic numbers):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x   -4096.0 ..   -2950.0
  y      88.4 ..     131.9
  z    6600.0 ..    7420.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Every car of an installed Forza at the game's own low detail, in one file for
the viewer's race tab: the `ProxyLOD` model each car archive under `media/Cars`
carries, about 900 triangles, with the car's number as the telemetry states it,
its make, model tag and year from the archive's name, and its wheels and tail
lights. Takes seconds and writes about 5 MB. Run it again when the game gets new
cars. An archive with no such model (a traffic prop) is named and left out. The
format is in [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

The shapes are in metres, the game's own: 1:1 with the car. The file holds the
game's content, so it is for the machine it was made on, not for passing around.

## courses

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

This runs the Forza `course` export on every course folder in a recorded lap
library, writing one `<name>.glb` each. It is Forza only. It calls the Forza
export directly and does not read `--game`, `--level` or `--install`.

| Option | Default | Meaning |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | the folder to write into (created if missing) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | the lap library |
| `--only TEXT [TEXT ...]` | all | only the courses whose folder names contain one of these (case-insensitive) |
| `--force` | off | export again what already has a `.glb` |
| `--track DIR` | searched | as for `course` |
| `--margin M` | 80 | as for `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | as for `course` |

What counts as a course folder: a direct sub-folder of the library whose name
contains ` (course_`, which is how FH Companion names them, for example
`Example Circuit (course_1200_3400_to_1175_3400)`. The part from ` (course_` on is
dropped from the name.

How a run behaves:

- A course whose `.glb` already exists is skipped (`kept`) unless `--force` is given, so an interrupted run carries on where it stopped.
- A course that fails (unreadable laps, out of memory, no terrain...) is reported as `FAILED`, and the run continues.
- At the end it prints a table of status, size in MB, seconds taken and name, then `<n> of <total> courses in <folder>`.
- The exit code is 1 if any course failed.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## terrain

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

This is the Forza cut with everything spelled out by hand: you give the track
folder and a region, not a lap. It is useful when the area you want is a box
rather than a drive.

| Option | Default | Meaning |
|---|---|---|
| `<path>` | required | a Forza track folder under `media\Tracks` (holding `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | required | the `.glb` to write |
| `--box X0 Z0 X1 Z1` | | the region, in the game's metres (x and z, as the telemetry reports them); corners in any order |
| `--route FILE` | | a route JSON with `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, as `heat3d_capture route` and `heat3d_capture laps` write it; read as UTF-8, with or without a byte-order mark |
| `--margin M` | **100** | metres added around a route's bounds, and the corridor width when the route has a line |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | as for `course` |

Give exactly one of `--box` and `--route`, otherwise the exit code is 2. With
`--route`, the cut is the route's `bounds` (`min`/`max`, x and z) widened by the
margin. If the file also holds at least 10 positions, the cut narrows to a
corridor of `--margin` metres around them, and placed models get their detail by
distance to that line. With `--box`, the whole box is kept, and detail goes to
what stands nearest the middle of the box.

Height is never part of the cut. A box outside the map, or in the sea, gives
"no terrain there" (exit code 1), not an error about coordinates.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box -4096 6600 -3584 7100 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite)

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` lists the levels an installed Frostbite game ships, by the name of
their table (`levels/<level>/<level>.toc`), with its size and where it comes
from: `Data` for the base game, `Update/<pack>` for an update, and how many
high-resolution tables add to it. A level an update ships has a small table of
chunks only in the base game as well; the table with the level's bundles is the
level (see [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` exports one: the terrain heightfield, every mesh the level's static
model groups place, the objects placed one by one, where they stand, and the
level's terrain backdrop round the map. With `--textures`, every surface carries
its colour map; with `--navmesh`, the surfaces soldiers walk on come too. How it
is read is in [Frostbite](reader-frostbite.md).

| Option | Default | Meaning |
|---|---|---|
| `<level>` | required | a name as `levels` prints it, a unique part of one, or the path of a level's `.toc` |
| `-o`, `--out FILE` | `<level>.glb` | the `.glb` to write |
| `--install FOLDER` | the first Steam game whose `Data` holds a `layout.toc` | the game's folder |
| `--textures [PIXELS]` | off; 512 when given without a size | write each surface's colour map, the largest mip no bigger than PIXELS a side, and its texture coordinates as the game has them, with a repeating sampler (see [Output format](output-format.md)). The heightfield gets the terrain backdrop's colour map where that map covers it, else the middle colour of the terrain's surface materials, else the backdrop's average colour round it. Off, every part is a flat colour |
| `--ground-texture [METRES]` | off; 0.5 when given without a size | bake the terrain decals — roads, runways, aprons, painted markings — over the ground colour, multiplied by the terrain's colormap where the level has one, into the heightfield's colour, METRES a pixel, in tiles of at most 4,096 pixels (`ground:terrain x<x> z<z>`). Works with or without `--textures` |
| `--navmesh` | off | add the level's navigation mesh for its smallest agent, the soldier (1.8 m tall, 0.4 m wide), as the part `nav:walkable`: the ground, floors, stairs and the roofs a soldier can reach, without the links (jumps, ladders, vaults) between them |
| `--ground-spacing METRES` | 4 | the heightfield's finest spacing; nodes finer than this are sampled down. 0 leaves the heightfield out |
| `--detail-budget N` | every copy at its coarsest level, plus a quarter, at least 1,500,000 | a ceiling on triangles. The meshes costing most drop a level of detail at a time until it fits; if even the coarsest levels do not, the smallest copies are left out first. The terrain backdrop is never coarsened or left out |
| `--skip TEXT` | | leave out static model groups whose partition name contains TEXT; repeat it for several. A game mode's layer, for instance |
| `--by-mesh` | off | for finding what a part is: one part per source mesh and material, named `<part> \| <mesh> \| <material>`; a much larger file |
| `--clamped-uvs` | off | for a renderer that cannot repeat a texture: cut every textured triangle into pieces whose coordinates lie within 0..1, and draw a triangle that would need more than 4 pieces in its texture's average colour, in a part `<part> (average colour)` |

It prints the groups and how many copies each placed, the meshes it left out and
why, the triangles per part (and with `--textures` how many textures, and how
many sections found their colour map), what the ground is, and with
`--navmesh` how many navigation tiles were read. Nothing is written about the level beyond the
geometry: no names, no metadata (see [Output format](output-format.md)).

The terrain budget is separate: the heightfield and the backdrop are never
coarsened by `--detail-budget`; `--ground-spacing` sizes the heightfield.

A whole level is large. For the level checked:

| Options | Triangles | File |
|---|---|---|
| none | 13.5 million | 450 MB |
| `--textures 512` | 13.5 million | 530 MB |
| `--textures 512 --ground-texture 0.5` | 13.5 million | 533 MB |
| `--textures 256 --detail-budget 3000000 --ground-spacing 8` | 5.1 million | 175 MB |

A second level, shipped by an update, with `--textures 512 --ground-texture 0.5
--navmesh`: 12.4 million triangles, 235,000 of them walkable, 460 MB. A level
thick with trees comes to 24 million and about 1 GB; `--detail-budget` brings
it down.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## Environment variables

| Variable | Effect |
|---|---|
| `HEAT3D_OODLE` | path to an `oo2core_*_win64.dll`, or a folder holding one; see [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | any value other than empty, `0`, `false`, `no` turns the update check off; see [Updates](updates.md) |
| `LOCALAPPDATA` | where the FH Companion library, BeamNG's user folder and the update cache are looked for |
| `HEAT3D_COURSE` | tests only: the course the installed-game kerb test uses; see [Development](development.md) |
