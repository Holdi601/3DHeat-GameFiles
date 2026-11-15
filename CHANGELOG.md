# Changelog

Releases are tagged `v<VERSION>`. Each entry names what changed; the **Docs**
section below says which documentation page explains each feature.

## Unreleased

- Each game's reader is its own project now, so a problem with one game's terms
  touches only that game: Forza (3DHeat-Ext-Forza, `heat3d-forza-maps`),
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
