---
title: Rundeinput
nav_order: 7
lang: "da"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Rundeinput {#lap-inputs}

En **rundefil** er en liste over x-, y- og z-punkter: hvor din bil kørte. Den hurtigste håndlavede er CSV-filen under [5. En `.csv`-tabel](#a-csv-table) nedenfor.

En runde fortæller course-eksporten **hvor bilen kørte**. Intet andet i den bruges: hastighed, input og g-kræfter hører til telemetri-siden af 3DHeat. Værktøjet læser positioner i spillets egne verdensmeter, og hvor filen siger det, også spillet og banen.

Kilde: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Hvad `course` accepterer {#what-course-accepts}

Formatet genkendes ud fra filens indhold, ikke navnet, undtagen at `.npz` og `.csv` går efter filendelsen, og alt andet prøves som JSON.

### 1. Et `heat3d-lap`-dokument (ethvert spil) {#a-heat3d-lap-document-any-game}

Skrevet af 3DHeat-telemetri-optagerne (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y`, `channels.z` er påkrævet. Rækker, hvor en af de tre ikke er et endeligt tal, droppes. Andre kanaler ignoreres.
- `game` bestemmer eksporten (se [Kommandoer](commands.md#which-game)).
- `track` bruges af Assetto Corsa Rally til først at prøve den navngivne etape.
- Akser: y er højde. Forza- og AC Rally-runder bruger spillets vandrette akser, som optageren skriver dem. BeamNG-runder forventes i viewer-koordinatsystemet, `(x, z, -y)` i BeamNGs Z-op-verden (se [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. En rutefil {#a-route-file}

Skrevet af `heat3d_capture route` og `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` er en liste af `[x, y, z]`. En ruetfil med `bounds` men uden positioner virker stadig: dens to hjørner er en degenereret linje, men en brugbar boks.

### 3. En FH Companion-rundefil {#an-fh-companion-lap-file}

Den enkelte rundefil i FH Companions optagede bibliotek:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Et manglende `X`, `Y` eller `Z` læses som 0. Filerne skrives med en byte-order mark, så al JSON læses som `utf-8-sig`.

### 4. En `.npz`-optagelse {#a-npz-recording}

Et NumPy-arkiv, der indeholder et `positions`-array med formen (n, 3).

### 5. En `.csv`-tabel {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolonner med navnene `x`, `y`, `z` (store/små bogstaver og mellemrum omkring ignoreres) er påkrævet. Andre kolonner ignoreres.
- Linjer, der starter med `#`, springes over. Hvis den **første** linje er `# {json}`, læses dens `game` og `track`.
- Rækker, der ikke kan læses som tal, springes over.

### 6. En mappe {#a-folder}

En mappe gennemsøges **rekursivt** for `.json`-, `.npz`- og `.csv`-filer, og alle sammenkædes til én kørt linje. Sådan gemmes en hel optaget bane: FH Companion indlejrer klasse-, bil-, tuning- og tag-mapper.

- `course.json` springes over efter navn (det er metadata, ikke en runde).
- En fil, der ikke kan læses, springes stille over. Én dårlig fil blandt hundredvis koster ikke resten.
- Konsollen rapporterer, hvor mange rundefiler der blev læst (`12 laps, 18,400 samples`).
- Mappen får det spil, dens filer navngiver, når de navngiver **kun ét**. En fil, der ikke navngiver et spil (en FH Companion-runde, `course.json`, en CSV uden sin beskrivelseslinje), tæller ikke, så en af dem blandt et spils optagelser koster ikke mappen dens spil. Filer, der navngiver to forskellige spil, er en blanding, og mappen får ingen. En mappe uden spil eksporteres som Forza, medmindre `--game` siger andet.
- Hvis intet kan læses: "no readable laps under <folder>".

### 7. Et banenavn {#a-course-name}

Hvis argumentet hverken er en eksisterende fil eller mappe, slås det op som et banenavn i FH Companion-biblioteket, `%LOCALAPPDATA%\FHCompanion\laps`:

1. en mappe, hvis navn, med ` (course_...)`-endelsen fjernet, er lig navnet (uden hensyn til store og små bogstaver);
2. ellers den ene mappe, hvis navn indeholder det.

Så finder `"Example Circuit"` `Example Circuit (course_1200_3400_to_1175_3400)`, uden at nogen kender koordinaterne. Flere match er en fejl, der lister dem. En bane fundet via navn bærer intet spil og eksporteres som Forza, medmindre `--game` siger andet.

## Hvad `terrain --route` accepterer {#what-terrain---route-accepts}

`terrain` har brug for ruefilens `bounds` (form 2 ovenfor), `{"min": [x, y, z], "max": [x, y, z]}`. Uden `bounds` stopper den med "<file> has no bounds; --route takes a route file with "bounds": {...}". Filen læses som UTF-8 med eller uden byte-order mark, ligesom al JSON-runde. Hvis den samme fil også har mindst 10 positioner, der kan læses efter reglerne ovenfor, bruges de til at snævre udskæringen ind til en korridor og styre detaljen.

## Hvordan runden bruges {#how-the-lap-is-used}

| Brug | Detalje |
|---|---|
| navn | filens stamme, eller mappens navn, med ` (course_...)` fjernet; det bliver standard-outputfilnavnet |
| kørt afstand | summen af afstandene mellem på hinanden følgende punkter (udskrevet som `m driven`; på tværs af en mappe tæller spring mellem filerne med) |
| boks | x- og z-udstrækningen udvidet med `--margin`; højden begrænses aldrig |
| korridor | x og z for hvert punkt, se [Course-eksport](course-export.md#the-corridor) |
| detalje | hver placeret kopis afstand til det nærmeste punkt, se [Detaljeniveauer og budgettet](detail-budget.md) |

En runde med færre end to punkter afvises ("holds no driving").

## Fejl {#errors}

| Besked | Betydning |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | filen er ikke JSON (og ikke `.npz` eller `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON af en anden form |
| `<file> has no x, y and z columns` | en CSV uden de headers |
| `<file> has no positions array` | en `.npz` uden `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | et navn, men intet FH Companion-bibliotek |
| `'<name>' matches 3 courses: A, B, C` | vær mere præcis |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | kun for navneopslag og `courses` |
