---
title: Rondebestanden
nav_order: 7
lang: "nl"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Rondebestanden {#lap-inputs}

Een **rondebestand** is een lijst van x-, y-, z-punten: waar je auto heen ging. Het snelst zelf te maken is de CSV onder [5. Een `.csv`-tabel](#5-a-csv-table) hieronder.

Een ronde vertelt de baan-export **waar de auto reed**. Al het andere erin wordt niet gebruikt: snelheid, bediening en g-krachten horen bij de telemetriekant van 3DHeat. De tool leest posities in de eigen wereldmeters van het spel, plus, waar het bestand dat zegt, het spel en het circuit.

Bron: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Wat `course` accepteert {#what-course-accepts}

Het formaat wordt herkend aan de inhoud van het bestand, niet aan de naam. Alleen `.npz` en `.csv` gaan op de extensie. Al het andere wordt als JSON geprobeerd.

### 1. Een `heat3d-lap`-document (elk spel) {#a-heat3d-lap-document-any-game}

Geschreven door de telemetrie-opnemers van 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y`, `channels.z` zijn verplicht. Rijen waarin een van de drie geen eindig getal is, vallen weg. Andere kanalen worden genegeerd.
- `game` bepaalt de export (zie [Commando's](commands.md#which-game)).
- `track` wordt door Assetto Corsa Rally gebruikt om eerst de genoemde etappe te proberen.
- Assen: y is de hoogte. Forza- en AC Rally-ronden gebruiken de horizontale assen van het spel, zoals de opnemer ze schrijft. BeamNG-ronden worden verwacht in het stelsel van de viewer, `(x, z, -y)` van de Z-omhoog-wereld van BeamNG (zie [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Een routebestand {#a-route-file}

Geschreven door `heat3d_capture route` en `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` is een lijst van `[x, y, z]`. Een routebestand met `bounds` maar zonder posities werkt ook: de twee hoeken vormen dan een ontaarde lijn, maar wel een bruikbare doos.

### 3. Een FH Companion-rondebestand {#an-fh-companion-lap-file}

De losse rondebestanden uit de opgenomen bibliotheek van FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Een ontbrekende `X`, `Y` of `Z` wordt als 0 gelezen. De bestanden worden geschreven met een byte-ordermarkering, dus alle JSON wordt als `utf-8-sig` gelezen.

### 4. Een `.npz`-opname {#a-npz-recording}

Een NumPy-archief met een array `positions` van vorm (n, 3).

### 5. Een `.csv`-tabel {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolommen met de namen `x`, `y`, `z` (hoofdletters en spaties eromheen worden genegeerd) zijn verplicht. Andere kolommen worden genegeerd.
- Regels die met `#` beginnen, worden overgeslagen. Staat op de **eerste** regel `# {json}`, dan worden de `game` en `track` daaruit gelezen.
- Rijen die niet als getallen lezen, worden overgeslagen.

### 6. Een map {#a-folder}

Een map wordt **recursief** doorzocht op `.json`-, `.npz`- en `.csv`-bestanden, en alle gevonden bestanden worden achter elkaar gezet tot één gereden lijn. Zo wordt een hele opgenomen baan bewaard: FH Companion zet klasse-, auto-, afstelling- en labelmappen onder elkaar.

- `course.json` wordt op naam overgeslagen (het is metadata, geen ronde).
- Een bestand dat niet gelezen kan worden, wordt stilletjes overgeslagen. Eén slecht bestand tussen honderden kost de rest niets.
- De console meldt hoeveel rondebestanden zijn meegenomen (`12 laps, 18,400 samples`).
- De map krijgt het spel dat zijn bestanden noemen, als ze **maar één** spel noemen. Een bestand dat geen spel noemt (een FH Companion-ronde, `course.json`, een CSV zonder de beschrijvingsregel) telt niet mee, dus één zo'n bestand tussen de opnames van één spel kost de map zijn spel niet. Bestanden die twee verschillende spellen noemen, zijn een mix, en dan krijgt de map geen spel.
  Een map zonder spel wordt als Forza geëxporteerd, tenzij `--game` iets anders zegt.
- Als niets gelezen kan worden: `no readable laps under <folder>`.

### 7. Een baannaam {#a-course-name}

Als het argument geen bestaand bestand of map is, wordt het opgezocht als baannaam in de FH Companion-bibliotheek, `%LOCALAPPDATA%\FHCompanion\laps`:

1. een map waarvan de naam, zonder het achtervoegsel ` (course_...)`, gelijk is aan de naam (hoofdletterongevoelig);
2. anders de enige map waarvan de naam de gezochte tekst bevat.

Zo vindt `"Example Circuit"` de map `Example Circuit (course_1200_3400_to_1175_3400)`, zonder dat je de coördinaten hoeft te weten. Meerdere overeenkomsten zijn een fout die ze allemaal opsomt. Een baan die via de naam is gevonden, heeft geen spel, dus wordt hij als Forza geëxporteerd, tenzij `--game` iets anders zegt.

## Wat `terrain --route` accepteert {#what-terrain---route-accepts}

`terrain` heeft de `bounds` van het routebestand nodig (vorm 2 hierboven), `{"min": [x, y, z], "max": [x, y, z]}`. Zonder `bounds` stopt het met `<file> has no bounds; --route takes a route file with "bounds": {...}`. Het bestand wordt als UTF-8 gelezen, met of zonder byte-ordermarkering, zoals elke JSON-ronde. Als hetzelfde bestand ook minstens 10 posities heeft die volgens de regels hierboven lezen, dan versmallen die de snede tot een corridor en sturen ze het detail.

## Hoe de ronde wordt gebruikt {#how-the-lap-is-used}

| Gebruik | Detail |
|---|---|
| naam | de bestandsnaam zonder extensie, of de mapnaam zonder ` (course_...)`; dit wordt de standaard uitvoernaam |
| afgelegde afstand | de som van de afstanden tussen opeenvolgende punten (afgedrukt als `m driven`; bij een map zijn de sprongen tussen de bestanden meegerekend) |
| doos | het x- en z-bereik, verbreed met `--margin`; de hoogte wordt nooit begrensd |
| corridor | de x en z van elk punt, zie [Baan-export](course-export.md#the-corridor) |
| detail | de afstand van elke geplaatste kopie tot het dichtstbijzijnde punt, zie [Detailniveaus en het budget](detail-budget.md) |

Een ronde met minder dan twee punten wordt geweigerd (`holds no driving`).

## Fouten {#errors}

| Melding | Betekenis |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | het bestand is geen JSON (en geen `.npz` of `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON van een andere vorm |
| `<file> has no x, y and z columns` | een CSV zonder die kopteksten |
| `<file> has no positions array` | een `.npz` zonder `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | een naam, maar geen FH Companion-bibliotheek |
| `'<name>' matches 3 courses: A, B, C` | wees specifieker |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | alleen bij naamzoekopdrachten en `courses` |
