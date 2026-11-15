# Commands

Every command runs as `python -m heat3d_gamefiles <verb> ...` from the repository
folder. The verbs come in the order you usually need them: what is this file, what
is inside it, give me that, and turn a lap into a course.

| Verb | Takes | Does |
|---|---|---|
| [`identify`](#identify) | any file | names the container format by reading its bytes |
| [`list`](#list) | an Unreal `.pak` or IoStore `.utoc`, a Source 2 `.vpk`, or a zip (a ForzaTech `.minizip` through the Forza tool) | lists its entries |
| [`extract`](#extract) | the same | writes one entry to disk |
| [`meshes`](#meshes) | a Unity `SerializedFile` | lists and checks its meshes |
| [`course`](#course) | a lap | exports the course around it (Forza, BeamNG.drive, Assetto Corsa Rally) (run by the the Forza, BeamNG.drive or AC Rally tool) |
| [`courses`](#courses) | a recorded lap library | runs `course` on every course in it (Forza) (run by the Forza tool) |
| [`races`](#races) | an installed Forza | lists every race the game defines: what it adds, what it hides, venues, the state of its export (run by the Forza tool) |
| [`terrain`](#terrain) | a Forza track folder | cuts a region by world coordinates (run by the Forza tool) |
| [`levels`](#levels-and-level-frostbite) | an installed Frostbite game (Battlefield 6) | lists its levels (run by the Battlefield tool) |
| [`level`](#levels-and-level-frostbite) | a level's name | exports the level: terrain, placed meshes, optionally their colour maps (Battlefield 6) (run by the Battlefield tool) |
| [`cars`](#cars) | an installed Forza | every car at low detail, in one file for the viewer's race tab (run by the Forza tool) |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | an Unreal 5 game | lists its World Partition maps |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | a map's name | exports the map: landscape, HLOD structures, water |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | an installed Arma Reforger | lists its worlds (run by the Reforger tool) |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | a world's name | exports the world: terrain in its colours, the sea, buildings as boxes (run by the Reforger tool) |

**Reading the examples:** `<x>` means replace it with your own value, without the
angle brackets; `[...]` is optional; wrap a path with spaces in "double quotes",
for example `"C:\Games\My Game"`. New to this? See [Before you start](before-you-start).
The full `--help` of every verb is on the [Command reference](cli-reference).

Each time the program starts, it may check for a newer release first. See
[Updates](updates). `HEAT3D_NO_UPDATE=1` turns that check off.

Source: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Step-by-step pages: [Inspecting archives](inspecting-archives), [Course export](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html),
[Whole levels](whole-levels), [Forza cars](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

![python -m heat3d_gamefiles --help](https://raw.githubusercontent.com/Holdi601/3DHeat-GameFiles/main/docs/assets/img/help.svg)

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
`verify()` method for that (see [Source 2 VPK](reader-source2-vpk)).

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
check (see [Unity](reader-unity)). A mesh that cannot be read is reported with
the reason and counts towards the limit. Vertex data in a `.resS` file is read
from the folder the container is in.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## The games' own verbs

Each game's reader is its own project, so a problem with one game's terms
touches only that game: install the one for your game (its page says how), and
both its own command and the verbs here work. GameFiles runs the game's tool
with the arguments you gave it; nothing of the tool is imported. It is found as
its command on `PATH`, as its installed package, or as its folder in
`HEAT3D_<GAME>_MAPS` or beside GameFiles (`exporters/ext/<game>-maps` in a 3DHeat
checkout, or `3DHeat-Ext-<Game>` next to this folder). When it is not
installed, the verb says where to get it and exits with code 2.

| Game | Its own tool | Verbs here that run it |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (Forza laps), `courses`, `races`, `cars`, `terrain`; `identify`, `list`, `extract` of a `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level`; `identify` of a Frostbite `.toc` |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (BeamNG laps); `identify` of a `.cdae` or `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (AC Rally laps) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verb> --help` shows the game tool's own options.

## course

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

The course around a lap - the ground in a band either side of the driving, and
what stands on it, as one `.glb` - made by the lap's game's own tool, run with
the same arguments: [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html),
[BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html),
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). What a lap
can be: [Lap inputs](lap-inputs); how much detail is kept:
[Levels of detail and the budget](detail-budget).

### Which game

The game is taken from `--game`, then from the `game` field of a `heat3d-lap`
file (or of a CSV's `# {...}` description line), then defaults to Forza. A folder
gets the game its files name, when they name only one; a file that names none
(an FH Companion lap, `course.json`, a CSV without a description line) does not
count (see [Lap inputs](lap-inputs)).

| Value | Run by |
|---|---|
| starts with `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` or `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | refused: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | refused: "tracks ship in a protected format that is not a file-extraction target" |
| anything else | refused: "there is no course reader for <game> yet" |

A refusal also suggests the alternatives: reconstruct the course from gameplay
(3DHeat GameCapture), or analyse the laps without a course, because the viewer's
Race analysis tab draws a road from them.

## courses, races, cars, terrain (Forza)

Run by `heat3d-forza-maps` with the same arguments:
[its commands](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels and level (Frostbite)

Run by `heat3d-battlefield-maps` with the same arguments:
[Battlefield levels](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

## ue-maps and ue-map (Unreal 5 World Partition)

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` is the game's folder, its `Content/Paks`, or the name of its folder
in a Steam library (`"<Steam game folder name>"`). `ue-maps` lists every map
that has cooked World Partition cells beside it. `ue-map` exports one as
`ground:<map>` (the landscape), `structure:<map>` (the map's merged HLOD
meshes) and `water:<map>` (its water bodies where they stand above the
ground), in Unreal **centimetres** with Y and Z swapped - the one export not
in metres. How each is read and checked: [Unreal 5 maps](level-unreal-world-partition).

| Option | Default | Meaning |
|---|---|---|
| `<map>` | required | a name as `ue-maps` prints it, or a unique part of one |
| `-o`, `--out FILE` | `<map>.glb` (in `$HEAT3D_LEVELS/<game>/` when that is set) | the `.glb` to write |
| `--ground-spacing METRES` | 2 | the landscape's vertex spacing in the file, rounded to a whole number of its own quads |
| `--no-structures`, `--no-water` | | leave that part out |

It prints the triangles per part, how many landscape components were read and
how many of the vertices they store twice disagree. A 3 km map at 2 m is about
4.6 million ground triangles.

## enfusion-worlds and enfusion-world (Arma Reforger)

Run by `heat3d-reforger-maps` with the same arguments (its `worlds` and
`world`): [Arma Reforger worlds](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Environment variables

| Variable | Effect |
|---|---|
| `HEAT3D_OODLE` | path to an `oo2core_*_win64.dll`, or a folder holding one; see [Oodle](reader-oodle) |
| `HEAT3D_LEVELS` | one folder for every export made without `-o`: each game's go in `<HEAT3D_LEVELS>/<game>/` (courses in `<game>/courses/`, the car pack in `forza/`). Unset, they go in the current folder |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | a game tool's folder, when it is neither installed nor beside GameFiles |
| `HEAT3D_NO_UPDATE` | any value other than empty, `0`, `false`, `no` turns the update check off; see [Updates](updates) |
| `LOCALAPPDATA` | where the FH Companion library, BeamNG's user folder and the update cache are looked for |
| `HEAT3D_COURSE` | tests only: the course the installed-game kerb test uses; see [Development](development) |
