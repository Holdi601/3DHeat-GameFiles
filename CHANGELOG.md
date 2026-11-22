# Changelog

Releases are tagged `v<VERSION>`. Each entry names what changed; the **Docs**
section below says which documentation page explains each feature.

## 1.3.0

- Its own icon: the 3DHeat cube with a text badge for its game (letters in 3DHeat's colours), as the
  program, window, taskbar and docs icon.
- A new window: the 3DHeat look in dark and light (follows the system, switchable), the logo and
  icon, sharp at any display scaling. Four steps: find the game (each requirement with its fix),
  choose (maps ticked when there is something to do, filters, search; jobs with their fields
  inline), work (progress, time left, cancel), done (open in 3DHeat, open the output folder, and
  for a failure what went wrong and what to do, copy details, report a problem).
- No console window on Windows: the program is a window program. From a terminal it still prints
  as before; `heat3d-gamefiles-cli.cmd` beside it waits for it in a terminal and passes its exit code.
- The update offer in the same look: Update now / Later / Skip this version, and "Update
  automatically" from the dialog.
- CI draws every page and dialog of the window (on Linux under a virtual display) and checks the
  Windows build is a window program.

## 1.2.0

- A standalone program for Windows, Linux and macOS (no Python needed), built by CI with a `SHA256SUMS` file.
  Without arguments it opens a window: what is missing (Oodle library, disk space), the levels folder, an
  Unreal 5 game's maps and the export of one of them, what a file is and what an archive holds, and updates.
  `--check --json` and `status --json` for scripts. `heat3d_gamefiles.__version__` is set.
- Updates ask first (update now / later / skip this version) unless automatic updates were chosen
  (`--auto-update`, the window's checkbox, or `HEAT3D_AUTO_UPDATE=1`); `heat3d_update.startup` asks through the
  same code.

## 1.1.0

- Each game's reader is its own project now, so it can be installed, updated,
  maintained or withdrawn on its own: Forza (3DHeat-Ext-Forza, `heat3d-forza-maps`),
  Battlefield/Frostbite (3DHeat-Ext-Battlefield), BeamNG.drive
  (3DHeat-Ext-BeamNG), Assetto Corsa Rally (3DHeat-Ext-ACRally) and Arma
  Reforger/Enfusion (3DHeat-Ext-Reforger), moved with their history, tests and
  pages. GameFiles keeps the engine-format readers and the shared plumbing as a
  library (`pyproject.toml`, `heat3d-gamefiles`; new core modules `steam`,
  `detail`, `unrealmath`), and its game verbs run the game's tool with the same
  arguments (`external.py`), or say where to get it and exit 2.
- Documentation: a "Before you start" page, plain-words openers, a generated
  command reference, diagrams drawn from `tools/docs_diagrams.py`, a release
  checklist. `identify` prints `2 x .json` instead of `2x.json`.
- Forza `course`: the lap is matched to the game's own route (its AI line),
  and that race's own layer from the game's route definitions is placed as
  `structure:event_*` parts (barriers, tents, gantries, stands, flags); what
  the race takes away from the free-roam world is left out. A venue's own
  ground (stadium floors, festival sites), plinths and procedurally built
  bridges, which nothing places, are drawn; a venue the driving passes
  through is cut whole. Switched-on placement layers are their own `structure:layer_*`
  parts. Files say what they hold in `asset.extras`; `courses` re-exports
  older ones and keeps two courses of one name apart.
- `races`: every race an installed Forza defines, what it adds and hides,
  which venues it passes through, and whether its export is current.

## 1.0.3

- Whole maps from Unreal 5 World Partition games (`ue-maps`, `ue-map`) and
  Arma Reforger worlds (`enfusion-worlds`, `enfusion-world`).
- `cars`: every car of an installed Forza at low detail, for the viewer.
- Battlefield 6 levels (`levels`, `level`): meshes, placement, terrain,
  textures, terrain decals, navigation mesh, object variations, destructible
  parts, letter sheets.

## 1.0.0 - 1.0.2

- Course export from Forza Horizon, BeamNG.drive and Assetto Corsa Rally laps;
  archive readers for Unreal, Unity, Source 2, ForzaTech, BeamNG; update check.

## Docs

| Feature | Page |
|---|---|
| Installing, first run | [Before you start](https://holdi601.github.io/3DHeat-GameFiles/before-you-start.html) |
| Every verb and option | [Commands](https://holdi601.github.io/3DHeat-GameFiles/commands.html), [Command reference](https://holdi601.github.io/3DHeat-GameFiles/cli-reference.html) |
| `identify`, `list`, `extract`, `meshes` | [Inspecting archives](https://holdi601.github.io/3DHeat-GameFiles/inspecting-archives.html) |
| `course`, `courses`, `terrain` | [Course export](https://holdi601.github.io/3DHeat-GameFiles/course-export.html) and its Forza, BeamNG and AC Rally pages |
| `races`, a race's own layer, venues | [Commands](https://holdi601.github.io/3DHeat-GameFiles/commands.html#races), [Forza Horizon courses](https://holdi601.github.io/3DHeat-GameFiles/course-forza-horizon.html#which-race) |
| `--detail-budget` | [Levels of detail and the budget](https://holdi601.github.io/3DHeat-GameFiles/detail-budget.html) |
| `levels`, `level` (Battlefield 6) | [Battlefield 6 levels](https://holdi601.github.io/3DHeat-GameFiles/level-battlefield.html) |
| `ue-maps`, `ue-map` | [Unreal 5 maps](https://holdi601.github.io/3DHeat-GameFiles/level-unreal-world-partition.html) |
| `enfusion-worlds`, `enfusion-world` | [Arma Reforger worlds](https://holdi601.github.io/3DHeat-GameFiles/level-arma-reforger.html) |
| `cars` | [Forza cars](https://holdi601.github.io/3DHeat-GameFiles/forza-cars.html) |
| Lap files accepted | [Lap inputs](https://holdi601.github.io/3DHeat-GameFiles/lap-inputs.html) |
| The `.glb` written | [Output format](https://holdi601.github.io/3DHeat-GameFiles/output-format.html) |
| Archive formats | [Archive readers](https://holdi601.github.io/3DHeat-GameFiles/archive-readers.html) |
| Update check | [Updates](https://holdi601.github.io/3DHeat-GameFiles/updates.html) |
| Releasing, keeping the docs right | [Maintaining](https://holdi601.github.io/3DHeat-GameFiles/maintaining.html) |
