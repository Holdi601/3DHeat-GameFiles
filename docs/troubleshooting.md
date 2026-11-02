---
title: Troubleshooting
nav_order: 8
---

# Troubleshooting

The messages the tool prints when something stops it, what each means, and what
to do. Messages are quoted from the code, with placeholders in angle brackets.

## Finding the game

| Message | Meaning | Do |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | no Steam library or `C:\XboxGames` holds a game with `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | the lap's coordinates are not on any installed track | check the lap is from this game; pass `--track` if the track is elsewhere |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | tiles exist near the box but none in the corridor | as above |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | the folder has no `.utoc` that opens | point `--install` at the folder with the `.utoc` files |

## Finding the place

| Message | Meaning | Do |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: no level scored 30% | `--level <name>`; check the lap is in the viewer frame |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` did not match | use one of the listed folder names |
| `<level> has no scene (no main/*.level.json and no .mis)` | the level folder has no scene files | a broken or partial level or mod |
| `no terrain of <level> lies along the driving.` | BeamNG: the corridor has no terrain squares | wrong level, or a level without terrain where the lap is |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: no stage and frame scored 50% | `--level <stage>`; check the lap's positions are metres with y up |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` did not match | use one of the listed names |
| `no ground of <stage> lies along the driving.` | AC Rally: no ground tile in the corridor | wrong stage |

## The lap

| Message | Do |
|---|---|
| `<file> is not a lap this can read. ...` | give it a supported shape, see [Lap inputs](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | the JSON is not a lap |
| `<file> has no x, y and z columns` | name the CSV columns `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | check the name, or pass a file |
| `'<name>' matches 3 courses: ...` | use a longer part of the name |
| `<name> holds no driving` | the lap has fewer than two samples |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` needs a route JSON with `bounds`, as `heat3d_capture route` and `laps` write it; a lap file is for `course` |
| `give exactly one of --box and --route` | `terrain` needs one region |
| `no course export for this lap: <reason>.` | the game is not supported, see [Limits and known gaps](limits-and-known-gaps.md) |

## Archives

| Message | Meaning |
|---|---|
| `no Oodle library found. ...` | set `HEAT3D_OODLE`, see [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | an encrypted pak: `--key <hex>` if you hold the key. There is no other way |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | the key is 32 bytes written as 64 hex digits, `0x` optional (exit code 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | it is none of those; `identify` says what it is. A Unity container takes `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | an encrypted IoStore container. It cannot be read |
| `pak version <n>; this reader handles 8-12` | an older or newer pak format |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | from Python: try the `.utoc`, which `list` and `extract` also take |
| `<file> has no directory index, so its chunks carry no names to list` | an IoStore container that names no files; its chunks are reached only through other packages |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | the `ChunkContentsMiniZip<n>.txt` beside the archive is from another build or another archive; without it the entries list by number |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | names were hashed away at build time |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | a Frostbite table in the obfuscated form |
| `no Frostbite game found in a Steam library; give --install` | `levels` or `level` found no Steam game whose `Data` holds a `layout.toc`; pass the game's folder |
| `no level called '<name>'; did you mean one of ...?` | the name matched no level's table, or several; `levels` lists them |
| `nothing was placed: no static model group was recognised` | the level's group members have a different type signature, after a game update or in another Frostbite game; the layout has to be measured again |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | a compressed Unity mesh |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | keep the `.resS` beside the `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | an older Unity build |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` takes a bare container |
| `texture format <n> has not been identified; refusing to guess` | a Forza swatch format not yet seen |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | keep a split VPK's parts together |

## Exports that come out wrong

| Symptom | Likely cause |
|---|---|
| the course is offset from the lap in the viewer | the lap and the export use different frames: check `--game` (a BeamNG lap read as Forza, say) |
| no verge in a Forza course | `--no-textures`, or the tile had no maps for that `--season` (the console says `N without maps`) |
| a Forza tile in flat colours | its ground maps are missing for the season |
| far fewer placed objects than expected | an explicit `--detail-budget` too small; the summary says how many copies were left out |
| the file is very large (hundreds of MB) | a city corridor under the automatic budget; use `--detail-budget`, `--texture-size 1024`, or `--margin 40` |
| fences missing | see-through surfaces are left out on purpose (the summary names them) |
| `N meshes could not be read` | some models use a format the reader refuses; the rest is still exported |
| `N of M components could not be read` (AC Rally) | a game patch may have moved property slots; please report it |
