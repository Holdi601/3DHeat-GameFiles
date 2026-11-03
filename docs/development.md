---
title: Development
nav_order: 11
---

# Development

## Layout

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Module map

| Module | What it does |
|---|---|
| `__main__.py` | runs the update check, then `cli.main()` |
| `cli.py` | the verbs, `identify`, archive dispatch, the Forza course writer |
| `lapinput.py` | every lap shape into positions; FH Companion library lookup |
| `corridor.py` | the band either side of the driving, as a 4 m raster |
| `surfaces.py` | the ground kinds, their part names and colours |
| `glb.py` | the `.glb` writer (parts, normals, colours, textures, quantisation) |
| `courseexport.py` | Forza: planar tile UVs, road/verge split, ground bake, decal lift |
| `forzainstall.py` | Steam and Xbox libraries; the Forza track a box belongs to |
| `minizip.py` | ForzaTech `.minizip` archives and their name lists |
| `forzatech.py` | `.modelbin`: chunks, buffers, layouts, submeshes, materials |
| `forzaterrain.py` | terrain tiles by place; surface classes |
| `forzatexture.py` | `.pb` swatches; tile maps; the ground bake |
| `forzamaterial.py` | `AssetManifest.xml`; which texture colours a model; seasons |
| `forzaplacement.py` | `.pgeo` placements, model levels, textures, cut-outs, stand-ins, the budget |
| `beamng.py` | BeamNG install, mounted file system, scene, terrain, materials |
| `beamngcourse.py` | the BeamNG course export |
| `beamngshape.py` | `.cdae` compiled shapes |
| `beamngcollada.py` | `.dae` fallback |
| `acrally.py` | AC Rally install, stages, component placement, virtual texture volume |
| `acrallycourse.py` | the AC Rally course export: frame fit, ground, placement |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 cooked packages |
| `unversioned.py` | unversioned property schemas and reader |
| `unrealmesh.py` | cooked static meshes |
| `unrealtexture.py` | textures and streaming virtual textures |
| `oodle.py` | finding and calling an installed Oodle library |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity containers, bundles, meshes |
| `frostbite.py` | Frostbite `.toc`, section tables, installation packages, chunk locations, payloads |
| `frostbitebundle.py` | Frostbite inline bundles, bundle manifests, a level's catalogue, the level list |
| `frostbiteebx.py` | Frostbite RIFF EBX partitions without a type library |
| `frostbitemesh.py` | Frostbite MeshSet and its level-of-detail chunks |
| `frostbiteterrain.py` | Frostbite terrain streaming tree, height pages, the ground mesh |
| `frostbitematerial.py` | Frostbite textures (BC1/BC3/BC7 mips), shader block depots, colour-map choice |
| `frostbitedecals.py` | Frostbite terrain decals and the ground bake |
| `frostbitenav.py` | Frostbite navigation mesh tiles: the soldiers' walkable surfaces |
| `frostbitelevel.py` | Frostbite static model groups, placement, the `level` export |
| `vpk.py` | Source 2 VPK |

All modules are on GitHub under
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Running the tests

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` sets `testpaths = tests` and `-q`. Two kinds of test matter, for
different reasons:

- **Synthetic tests** build archives byte by byte and run anywhere. They pin
  the field layouts that were wrong at some point: the 64-bit `.minizip` segment
  base and its alignment padding, the pak block-size escape, the Unity header's
  u32 between two int64s, the VPK `0x7FFF` index, the Forza normal's split x.
- **Installed-game tests** run against the real files when the game is on the
  machine, and **skip** (they do not fail) when it is not. They are the only thing
  that catches a layout that is right for a small file and wrong for a large one.

### Fixtures

| Fixture | Builds |
|---|---|
| `tests/forza_fixtures.py` | `.minizip` archives (with the 64-bit base, padding, mixed codecs), manifests, `.modelbin` models and terrain, `.pb` swatches |
| `tests/beamng_fixtures.py` | a small BeamNG install: `gameengine.zip`, `content`, one level zip with a 64 m terrain, an asphalt strip, a road decal, a rail, a prefab, a forest item, the sea, materials, and `.cdae` shapes in the documented layout |
| `tests/unreal_fixtures.py` | an IoStore container with a directory, a zen package, an unversioned property block |

### Test files

| File | Covers |
|---|---|
| `test_minizip.py` | read-back, the 64-bit base, odd and even bundle tables, refusals, the names file |
| `test_forzatech.py` | the chunk table and chain, refusals; installed: real models' chains and tags |
| `test_forza_geometry.py` | world placement, vertex layout, refused formats, submeshes, normals and UVs |
| `test_forzaterrain.py` | the tile grid (1023 vs 512 m), clipping, extraction |
| `test_forzatexture.py` | swatch header, decoding, the texture shelf, the ground bake |
| `test_forzamaterial.py` | the manifest, names, material hashes, the colour choice, seasons |
| `test_forzaplacement.py` | the `.pgeo` record, placing copies, levels, variants, see-through surfaces, a whole box, the budget, the placeholder colour, the automatic budget; installed: kerbs on the ground |
| `test_forzainstall.py` | finding the game, choosing the track |
| `test_courseexport.py` | tile UVs, the part plan, decal lift |
| `test_course_cli.py` | the whole `course` and `courses` verbs on a synthetic track; `terrain --route` with a byte-order mark, and without `bounds` |
| `test_archive_cli.py` | `identify`, `list` and `extract` on every archive with a reader (`.pak`, IoStore, `.vpk`, `.minizip` with and without its names, zip, `.cdae`, `.ter`); failures as one line and an exit code: an encrypted pak, an encrypted container, a file that is no archive, a bad `--key` |
| `test_corridor.py` | the band, cutting terrain with it |
| `test_lapinput.py` | every lap shape, the box, failures, course-name lookup, which game a folder is |
| `test_surfaces.py` | which names decide a surface, which do not, part names |
| `test_glb.py` | the file is valid, nodes carry the class, refusals, quantisation |
| `test_beamng.py` | shapes, the level, categories, finding the level from a lap, the course, the Collada fallback; installed: `.cdae` vs `.dae`, every level opens |
| `test_acrally.py` | containers, packages, properties, transforms, the frame fit, placed models' parts and the budget, virtual textures; installed: stages and the baked ground colour |
| `test_pak.py` | footer, entries, the block-size escape, refusals; installed: offsets and SHA-1 |
| `test_unity.py` | refusals; installed: the object table tiles the file, version strings, mesh bounds |
| `test_frostbite.py` | signed vs obfuscated headers, refusals, installation packages (two packages with the same blob number); installed: every table, superbundles, section chains, distinct ids, sampled payloads from the right package |
| `test_frostbitelevel.py` | chunk ids paired with their own locations, inline bundles, manifests, a MeshSet with a shadow section and UVs, a group member, the transform convention, a two-level terrain, colour-map choice, a texture chunk missing its largest mips, the repeating sampler, decal records, a decal composited by its alpha, a decal sheet losing to a surface's own map, the level's table chosen across the base game and its updates, navigation tiles (surfaces kept, links left out, refusals, detail meshes), triangles cut where their texture repeats, the ground's colour from its surface materials, mask pages (BC4 and uncompressed) placed on their quadrants and refused when their borders disagree, colormap pages placed on their quadrants and found after the mask pages the mask tree counts, distance fields, palettes and channel masks never taken as colour, a block's tint and a grey map painted with it, a palette vertex at its swatch's centre, the slope grid spread back bilinearly, an object's overlay drawn through its unwrap, blockout, cinematic and lighting meshes left out and a colormap layout that is not read, cut-out maps and their masked, two-sided PNG materials, backdrop tiles named by their mesh; installed: the level's terrain decals, the largest level's catalogue, meshes inside their bounds, group members, vegetation standing on the decoded terrain |
| `test_vpk.py` | the directory, refusals, split archives; installed: maps open, CRCs match, the nav mesh |

## Installed-game tests

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
finds games for the tests. `steam_common()` lists every Steam library's
`steamapps\common` (Steam's own folders included), and `installed(*globs)`
returns the paths matching any glob under them, recursively where a glob has
`**`. Each test decides what it needs:

| Test | Looks for | Skips with |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` with an **unencrypted** index, up to 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` in `*/*_Data` or `*/*/*_Data` that the reader accepts, up to 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, up to 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | the FH Companion library's circuits (start and finish within 50 m), with the most laps, that `find_track` places; or `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Run only one game's tests, or point the Forza kerb test at a course:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Installed-game tests read from the games only. They write nothing into game
folders. Test outputs go to pytest's temporary folders.

## Conventions

- **Refuse rather than guess.** Every reader raises its own exception
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) with
  a message saying what was found and why it was not read.
- **Check against the format itself.** A hash, a CRC, a chain of offsets, a stored
  bounding box, the driving lying on the ground. Not "it did not crash".
- **No keys, no bundled proprietary code.** See [Rules and licences](rules-and-licences.md).
- **Confidential data stays out.** Game files, exports, laps, recordings and
  screenshots never go into the repository. `.gitignore` excludes them by folder
  and by type. Tests use synthetic data and installed games, never checked-in game
  content.
