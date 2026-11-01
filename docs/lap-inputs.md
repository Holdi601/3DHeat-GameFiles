---
title: Lap inputs
nav_order: 4
---

# Lap inputs

A lap tells the course export **where the car went**. Nothing else in it is used:
speed, inputs and g-forces belong to the telemetry side of 3DHeat. The tool reads
positions in the game's own world metres, plus, where the file says so, the game
and the track.

Source: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## What `course` accepts

The format is recognised by looking at the file, not its name, except that
`.npz` and `.csv` go by extension and everything else is tried as JSON.

### 1. A `heat3d-lap` document (any game)

Written by the 3DHeat telemetry recorders (`heat3d_capture telemetry`):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y`, `channels.z` are required. Rows where any of the
  three is not a finite number are dropped. Other channels are ignored.
- `game` decides the export (see [Commands](commands.md#which-game)).
- `track` is used by Assetto Corsa Rally to try the named stage first.
- Axes: y is height. Forza and AC Rally laps use the game's horizontal axes as the
  recorder writes them. BeamNG laps are expected in the viewer's frame,
  `(x, z, -y)` of BeamNG's Z-up world (see [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. A route file

Written by `heat3d_capture route` and `heat3d_capture laps`:

```json
{
  "bounds": {"min": [-4100.0, 80.0, 6600.0], "max": [-3000.0, 140.0, 7400.0]},
  "positions": [[-4096.0, 101.2, 6610.5], [-4095.1, 101.2, 6612.0]]
}
```

`positions` is a list of `[x, y, z]`. A route file with `bounds` but no
positions still works: its two corners are a degenerate line but a usable box.

### 3. An FH Companion lap file

The per-lap files of FH Companion's recorded library:

```json
{"Lap": {"samples": [{"X": -4096.0, "Y": 101.2, "Z": 6610.5}, {"X": -4095.1, "Y": 101.2, "Z": 6612.0}]}}
```

A missing `X`, `Y` or `Z` reads as 0. The files are written with a byte-order
mark, so all JSON is read as `utf-8-sig`.

### 4. A `.npz` recording

A NumPy archive holding a `positions` array of shape (n, 3).

### 5. A `.csv` table

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Columns named `x`, `y`, `z` (case and surrounding spaces ignored) are required.
  Other columns are ignored.
- Lines starting with `#` are skipped. If the **first** line is `# {json}`, its
  `game` and `track` are read.
- Rows that do not parse as numbers are skipped.

### 6. A folder

A folder is searched **recursively** for `.json`, `.npz` and `.csv` files, and
all of them are concatenated into one driven line. That is how a whole recorded
course is stored: FH Companion nests class, car, tune and tag folders.

- `course.json` is skipped by name (it is metadata, not a lap).
- A file that will not read is skipped quietly. One bad file among hundreds does
  not cost the rest.
- The console reports how many lap files went in (`12 laps, 18,400 samples`).
- The folder gets the game its files name, when they name **only one**. A file
  that names no game (an FH Companion lap, `course.json`, a CSV without its
  description line) does not count, so one of them among a game's recordings
  does not cost the folder its game. Files naming two different games are a mix,
  and the folder gets none. A folder without a game is exported as Forza unless
  `--game` says otherwise.
- If nothing reads: "no readable laps under <folder>".

### 7. A course name

If the argument is not an existing file or folder, it is looked up as a course
name in the FH Companion library, `%LOCALAPPDATA%\FHCompanion\laps`:

1. a folder whose name, with the ` (course_...)` suffix removed, equals the name
   (case-insensitive);
2. otherwise the single folder whose name contains it.

So `"Example Circuit"` finds
`Example Circuit (course_1200_3400_to_1175_3400)` without anyone knowing the
coordinates. Several matches are an error that lists them. A course found by
name carries no game, so it is exported as Forza unless `--game` says otherwise.

## What `terrain --route` accepts

`terrain` needs the route file's `bounds` (shape 2 above),
`{"min": [x, y, z], "max": [x, y, z]}`. Without `bounds`, it stops with
"<file> has no bounds; --route takes a route file with "bounds": {...}". The file
is read as UTF-8 with or without a byte-order mark, like every JSON lap. If the same file
also has at least 10 positions readable by the rules above, they narrow the cut
to a corridor and steer the detail.

## How the lap is used

| Use | Detail |
|---|---|
| name | the file's stem, or the folder's name, with ` (course_...)` removed; it becomes the default output file name |
| distance driven | the sum of the gaps between consecutive samples (printed as `m driven`; across a folder this includes the jumps between files) |
| box | the x and z extent widened by `--margin`; height is never bounded |
| corridor | the x and z of every sample, see [Course export](course-export.md#the-corridor) |
| detail | each placed copy's distance to the nearest sample, see [Levels of detail and the budget](detail-budget.md) |

A lap with fewer than two samples is refused ("holds no driving").

## Errors

| Message | Meaning |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | the file is not JSON (and not `.npz` or `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON of another shape |
| `<file> has no x, y and z columns` | a CSV without those headers |
| `<file> has no positions array` | an `.npz` without `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | a name, but no FH Companion library |
| `'<name>' matches 3 courses: A, B, C` | be more specific |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | only for name lookups and `courses` |
