
# 3DHeat GameFiles

3DHeat GameFiles reads level data out of the archives a game already ships and
writes it as a binary glTF (`.glb`) file for the 3DHeat telemetry viewer. Its
main job is the **course export**: you give it a lap you drove, and it writes the
track around that lap. That means the ground, the road told apart from verge and
grass, and kerbs, barriers, tyre walls, signs and buildings. It needs nothing
else from you.

It is one of three ways to get a level's geometry into 3DHeat:

| Route | Needs | Gives |
|---|---|---|
| 3DHeat Unreal Exporter | the Unreal project open in the editor | exact geometry |
| 3DHeat GameCapture | a screen and a capture | an estimate |
| **3DHeat GameFiles** | **the installed, shipped game** | **exact geometry, no project** |

Python package: `heat3d_gamefiles`. Repository:
[Holdi601/3DHeat-GameFiles](https://github.com/Holdi601/3DHeat-GameFiles). Licence: MIT.

## What it can do

| Game or engine | Course export (`course`) | Archive reading |
|---|---|---|
| Forza Horizon (ForzaTech) | yes: terrain, road and verge, ground texture, placed models in their own textures | `identify`, `list`, `extract` on a `.minizip`; `identify` on a `.modelbin`; models, terrain and textures through `course` and `terrain` |
| BeamNG.drive | yes: terrain, road decals, modelled circuits, placed models, water | `identify`, `list`, `extract` on level zips; `identify` on `.ter`, `.cdae`; `.dae` through `course` |
| Assetto Corsa Rally (Unreal 5.6) | yes: stage ground tiles, baked ground colour, placed models in flat colours | `identify`, `list`, `extract` on IoStore `.utoc`/`.ucas`; zen packages, static meshes, textures through `course` |
| Unreal `.pak` (versions 8-12) | no | `identify`, `list`, `extract` |
| Unity (format 22 and later) | no | `identify`, `meshes` |
| Battlefield 6 (Frostbite `.toc`/`.cas`) | no lap; a whole level with `level`: terrain, placed meshes, their colour maps with `--textures` | `identify`, `levels`; bundles, meshes, terrain, textures and placement through `level` |
| Source 2 `.vpk` | no | `identify`, `list`, `extract` |

Laps from Assetto Corsa EVO and iRacing are refused with a reason. See
[Limits and known gaps](limits-and-known-gaps).

## Install

You need Python and the packages in
[`requirements.txt`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/requirements.txt).
The tool has been run with Python 3.13. Older versions have not been checked.

```
git clone https://github.com/Holdi601/3DHeat-GameFiles.git
cd 3DHeat-GameFiles
pip install -r requirements.txt
```

Run every command from the repository folder, as `python -m heat3d_gamefiles <verb>`.

| Package | Used for |
|---|---|
| numpy | everything that decodes geometry |
| lz4 | Forza archives (mostly LZ4 blocks), some Unity bundles, IoStore LZ4 blocks |
| Pillow | decoding BC1-BC7 textures, writing the JPEG textures in the `.glb` |
| msgpack, zstandard | BeamNG's compiled shapes (`.cdae`) |
| cryptography | only for opening an encrypted `.pak` with a key you already hold |
| pytest | the tests |

Unreal content compressed with **Oodle** needs an Oodle library that is already
on your machine. One is never shipped with this tool. See [Oodle](reader-oodle).

The tool is written for Windows. It finds games through Steam's library list and
`%LOCALAPPDATA%`, and loads Oodle as a Windows DLL. Other platforms have not been
tested.

## Quick start

```
# Forza: a lap file, a lap folder, or a course name from the FH Companion library
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course path\to\lap.json -o course.glb

# BeamNG.drive or Assetto Corsa Rally: a heat3d-lap file says which game it is from
python -m heat3d_gamefiles course my_lap.json

# Every course in the FH Companion library, one .glb each
python -m heat3d_gamefiles courses -o courses

# Battlefield 6: list the levels, then export one (a large file; see Commands)
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures

# What is this file?
python -m heat3d_gamefiles identify some_archive.pak
```

Open the `.glb` in the 3DHeat viewer. The game's own world coordinates are kept
(see [Output format](output-format)), so a recorded lap lines up with the course.

## Map of this documentation

- [Commands](commands): every verb and option, with examples.
- [Course export](course-export): how a lap becomes a course, for all games.
  - [Forza Horizon](course-forza-horizon)
  - [BeamNG.drive](course-beamng)
  - [Assetto Corsa Rally](course-assetto-corsa-rally)
  - [Levels of detail and the budget](detail-budget)
- [Lap inputs](lap-inputs): every lap file shape the tool accepts.
- [Output format](output-format): what is inside the `.glb`.
- [Archive readers](archive-readers): one page per container format, covering
  what each reads, what it does not, and why.
- [Limits and known gaps](limits-and-known-gaps)
- [Troubleshooting](troubleshooting): the error messages and what to do.
- [Rules and licences](rules-and-licences): no keys, your own files, no redistribution.
- [Updates](updates): the update check and `heat3d_update`.
- [Development](development): module map and tests, including the tests that run against installed games.

## Part of 3DHeat

| Tool | What it does |
|---|---|
| [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | courses and levels out of the archives games ship, as glTF |
| [3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | lap telemetry from racing games' published interfaces; levels reconstructed from gameplay video |
| [3DHeat Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | an Unreal Editor plugin that exports a level as glTF |
| [3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demos into heatmap tables and match summaries |
| [3DHeat Watcher](https://github.com/Holdi601/3DHeat-Watcher) | records your play in the background from what games publish |
