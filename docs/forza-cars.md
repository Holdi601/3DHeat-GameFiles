---
title: Forza cars
nav_order: 6
---

# Forza cars: `cars`

Writes every car of an installed Forza at the game's own low detail into one
file for the viewer's race tab, so each recorded car is drawn in its own shape
at its true size.

![cars --help](assets/img/cars-help.svg)

## Step by step

1. **Run it** with the game installed (it is found in the Steam libraries and
   `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Or name the game's folder:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Load it in the viewer**: **Load car file...** in the view settings, or drop
   the file on the race tab; it stays in that browser. Laps whose car number is
   in the file are then drawn as that very car (see the viewer's
   [race replay docs](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Run it again** when the game gets new cars. It takes seconds and writes
   about 5 MB.

## Options

| Option | Default | Meaning |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | the file to write |
| `--game FOLDER` | the installed game found | the game's folder |

## What is in the file

For every car archive under `media/Cars`: the `ProxyLOD` model it carries
(about 900 triangles), the car's number as the telemetry states it, its make,
model tag and year from the archive's name, and its wheels and tail lights. The
shapes are in metres, 1:1 with the car. An archive without such a model (a
traffic prop) is named and left out. The layout is in
[`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

The file holds the game's content: it is for the machine it was made on, not
for passing around ([Rules and licences](rules-and-licences.md)).
