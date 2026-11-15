---
title: Rundeinndata
nav_order: 7
lang: "no"
source: lap-inputs.md
source_hash: "3f335d2fc454"
nav_exclude: true
search_exclude: true
---
# Rundeinndata {#lap-inputs}

En **rundefil** er en liste med x-, y- og z-punkter: hvor bilen kjørte. Den raskeste
håndlagde er CSV-en under [5. En `.csv`-tabell](#5-a-csv-table) nedenfor.

En runde forteller baneeksporten **hvor bilen kjørte**. Ingenting annet i den
brukes: fart, styring og g-krefter hører til telemetridelen av 3DHeat. Verktøyet
leser posisjoner i spillets egne verdensmeter, pluss, der filen sier det, spillet
og banen.

Kilde: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Hva `course` tar imot {#what-course-accepts}

Formatet gjenkjennes ved å se på filen, ikke navnet, bortsett fra at `.npz` og `.csv`
går etter filendelse, og alt annet prøves som JSON.

### 1. Et `heat3d-lap`-dokument (alle spill) {#a-heat3d-lap-document-any-game}

Skrevet av 3DHeat-telemetriopptakerne (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y` og `channels.z` er påkrevd. Rader der en av de tre ikke
  er et endelig tall, fjernes. Andre kanaler ignoreres.
- `game` avgjør eksporten (se [Kommandoer](commands.md#which-game)).
- `track` brukes av Assetto Corsa Rally til å prøve den navngitte etappen først.
- Akser: y er høyde. Forza- og AC Rally-runder bruker spillets horisontale akser slik
  opptakeren skriver dem. BeamNG-runder forventes i visningens koordinatsystem,
  `(x, z, -y)` i BeamNGs Z-opp-verden (se [BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html#the-laps-frame)).

### 2. En rutefil {#a-route-file}

Skrevet av `heat3d_capture route` og `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` er en liste med `[x, y, z]`. En rutefil med `bounds` men uten
posisjoner fungerer fortsatt: de to hjørnene er en degenerert linje, men en brukbar
boks.

### 3. En FH Companion-rundefil {#an-fh-companion-lap-file}

Rundefilene i FH Companions innspilte bibliotek:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

En manglende `X`, `Y` eller `Z` leses som 0. Filene skrives med en byte-
rekkefølgemarkering, så all JSON leses som `utf-8-sig`.

### 4. En `.npz`-innspilling {#a-npz-recording}

Et NumPy-arkiv som har en `positions`-matrise med form (n, 3).

### 5. En `.csv`-tabell {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolonner som heter `x`, `y`, `z` (store/små bokstaver og omkringliggende mellomrom
  ignoreres) er påkrevd. Andre kolonner ignoreres.
- Linjer som begynner med `#` hoppes over. Hvis **første** linje er `# {json}`, leses
  `game` og `track` fra den.
- Rader som ikke leses som tall, hoppes over.

### 6. En mappe {#a-folder}

En mappe søkes **rekursivt** etter `.json`-, `.npz`- og `.csv`-filer, og alle slås
sammen til én kjørt linje. Slik lagres en hel innspilt bane: FH Companion legger
klasse-, bil-, innstillings- og merkemapper inn i hverandre.

- `course.json` hoppes over etter navn (den er metadata, ikke en runde).
- En fil som ikke kan leses, hoppes stille over. Én dårlig fil blant hundrevis
  koster ikke resten.
- Konsollen rapporterer hvor mange rundefiler som ble med (`12 laps, 18,400 samples`).
- Mappen får spillet filene navngir, når de navngir **bare ett**. En fil som ikke
  navngir noe spill (en FH Companion-runde, `course.json`, en CSV uten
  beskrivelseslinje) teller ikke, så én av dem blant et spills innspillinger tar
  ikke spillet fra mappen. Filer som navngir to ulike spill er en blanding, og
  mappen får ingen. En mappe uten spill eksporteres som Forza med mindre `--game`
  sier noe annet.
- Hvis ingenting kan leses: "no readable laps under <folder>".

### 7. Et banenavn {#a-course-name}

Hvis argumentet ikke er en eksisterende fil eller mappe, slås det opp som et banenavn
i FH Companion-biblioteket, `%LOCALAPPDATA%\FHCompanion\laps`:

1. en mappe der navnet, uten ` (course_...)`-endelsen, er lik navnet (uten store/små-
   bokstavforskjell);
2. ellers den ene mappen der navnet inngår.

Så `"Example Circuit"` finner `Example Circuit (course_1200_3400_to_1175_3400)` uten
at noen må kjenne koordinatene. Flere treff er en feil som lister dem opp. En bane
funnet med navn har ikke noe spill, så den eksporteres som Forza med mindre `--game`
sier noe annet.

## Hva `terrain --route` tar imot {#what-terrain---route-accepts}

`terrain` trenger rutefilens `bounds` (form 2 over),
`{"min": [x, y, z], "max": [x, y, z]}`. Uten `bounds` stopper den med
"<file> has no bounds; --route takes a route file with "bounds": {...}". Filen leses
som UTF-8 med eller uten byte-rekkefølgemarkering, som all JSON-runde. Hvis samme fil
også har minst 10 posisjoner som kan leses etter reglene over, avgrenser de snittet
til en korridor og styrer detaljen.

## Hvordan runden brukes {#how-the-lap-is-used}

| Bruk | Detalj |
|---|---|
| navn | filens stamme, eller mappens navn, uten ` (course_...)`; det blir standard utdatafilnavn |
| kjørt distanse | summen av avstandene mellom etterfølgende punkter (skrives ut som `m driven`; over en mappe inkluderer det hoppene mellom filene) |
| boks | x- og z-utstrekningen utvidet med `--margin`; høyden begrenses aldri |
| korridor | x og z for hvert punkt, se [Baneeksport](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html#the-corridor) |
| detalj | hver plassert kopis avstand til nærmeste punkt, se [Detaljnivåer og budsjettet](detail-budget.md) |

En runde med færre enn to punkter avvises ("holds no driving").

## Feil {#errors}

| Melding | Betydning |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | filen er ikke JSON (og ikke `.npz` eller `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON av en annen form |
| `<file> has no x, y and z columns` | en CSV uten disse overskriftene |
| `<file> has no positions array` | en `.npz` uten `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | et navn, men intet FH Companion-bibliotek |
| `'<name>' matches 3 courses: A, B, C` | vær mer presis |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | bare for navneoppslag og `courses` |
