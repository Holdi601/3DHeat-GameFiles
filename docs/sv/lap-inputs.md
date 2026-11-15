---
title: "Varvindata"
nav_order: 7
lang: "sv"
source: lap-inputs.md
source_hash: "3f335d2fc454"
nav_exclude: true
search_exclude: true
---
# Varvindata {#lap-inputs}

En **varvfil** är en lista med x-, y- och z-punkter: var bilen körde. Det snabbaste
handgjorda exemplet är CSV-filen under [5. En `.csv`-tabell](#5-a-csv-table) nedan.

Ett varv berättar för banexporten **var bilen körde**. Inget annat i det används:
hastighet, inmatning och g-krafter hör till 3DHeats telemetrisida. Verktyget läser
positioner i spelets egna världsmeter, och, där filen säger det, spelet och banan.

Källa: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Vad `course` tar emot {#what-course-accepts}

Formatet känns igen genom att titta på filen, inte på dess namn, förutom att `.npz`
och `.csv` går på filändelsen. Allt annat provas som JSON.

### 1. Ett `heat3d-lap`-dokument (alla spel) {#a-heat3d-lap-document-any-game}

Skrivs av 3DHeats telemetriinspelare (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y` och `channels.z` krävs. Rader där något av de tre inte är
  ett ändligt tal släpps. Andra kanaler ignoreras.
- `game` avgör exporten (se [Kommandon](commands.md#which-game)).
- `track` används av Assetto Corsa Rally för att pröva den namngivna etappen först.
- Axlar: y är höjd. Forza- och AC Rally-varv använder spelets horisontella axlar så
  som inspelaren skriver dem. BeamNG-varv förväntas i visarens ram,
  `(x, z, -y)` i BeamNG:s Z-uppåt-värld (se [BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html#the-laps-frame)).

### 2. En ruttfil {#a-route-file}

Skrivs av `heat3d_capture route` och `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` är en lista med `[x, y, z]`. En ruttfil med `bounds` men utan
positioner fungerar fortfarande: dess två hörn är en degenererad linje men en användbar låda.

### 3. En FH Companion-varvfil {#an-fh-companion-lap-file}

De enskilda varvfilerna i FH Companions inspelade bibliotek:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Saknas `X`, `Y` eller `Z` läses det som 0. Filerna skrivs med en byte-ordningsmarkering,
så all JSON läses som `utf-8-sig`.

### 4. En `.npz`-inspelning {#a-npz-recording}

Ett NumPy-arkiv som innehåller en matris `positions` med formen (n, 3).

### 5. En `.csv`-tabell {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolumner som heter `x`, `y`, `z` (versaler och gemener och omgivande blanksteg
  spelar ingen roll) krävs. Andra kolumner ignoreras.
- Rader som börjar med `#` hoppas över. Om **första** raden är `# {json}` läses
  dess `game` och `track`.
- Rader som inte går att läsa som tal hoppas över.

### 6. En mapp {#a-folder}

En mapp söks **rekursivt** efter `.json`-, `.npz`- och `.csv`-filer, och alla slås
ihop till en enda körd linje. Så lagras en hel inspelad bana: FH Companion lägger
in klass-, bil-, inställnings- och taggmappar.

- `course.json` hoppas över på namnet (det är metadata, inte ett varv).
- En fil som inte går att läsa hoppas tyst över. En trasig fil bland hundratals kostar
  inte resten.
- Konsolen redovisar hur många varvfiler som togs med (`12 laps, 18,400 samples`).
- Mappen får det spel dess filer nämner, när de nämner **bara ett**. En fil som inte
  nämner något spel (ett FH Companion-varv, `course.json`, en CSV utan beskrivningsraden)
  räknas inte, så en sådan fil bland ett spels inspelningar kostar inte mappen dess spel.
  Filer som nämner två olika spel är en blandning, och mappen får inget spel. En mapp
  utan spel exporteras som Forza, om inte `--game` anger något annat.
- Om inget kan läsas: "no readable laps under <mapp>".

### 7. Ett banans namn {#a-course-name}

Om argumentet inte är en befintlig fil eller mapp slås det upp som ett banans namn i
FH Companion-biblioteket, `%LOCALAPPDATA%\FHCompanion\laps`:

1. en mapp vars namn, med suffixet ` (course_...)` borttaget, är lika med namnet
   (utan hänsyn till stora och små bokstäver);
2. annars den enda mapp vars namn innehåller det.

Så `"Example Circuit"` hittar `Example Circuit (course_1200_3400_to_1175_3400)` utan
att någon behöver känna till koordinaterna. Flera träffar är ett fel som listar dem.
En bana som hittas med namn bär inget spel, så den exporteras som Forza om inte
`--game` anger något annat.

## Vad `terrain --route` tar emot {#what-terrain---route-accepts}

`terrain` behöver ruttfilens `bounds` (form 2 ovan),
`{"min": [x, y, z], "max": [x, y, z]}`. Utan `bounds` stannar det med
"<fil> has no bounds; --route takes a route file with "bounds": {...}". Filen läses
som UTF-8 med eller utan byte-ordningsmarkering, precis som all JSON-varvdata. Om
samma fil också har minst 10 positioner som går att läsa enligt reglerna ovan, begränsar
de utskärningen till en korridor och styr detaljen.

## Hur varvet används {#how-the-lap-is-used}

| Användning | Detalj |
|---|---|
| namn | filens stam, eller mappens namn, med ` (course_...)` borttaget; det blir standardnamnet på utdatafilen |
| körd sträcka | summan av avstånden mellan efterföljande punkter (skrivs som `m driven`; över en mapp räknas även hoppen mellan filerna) |
| låda | x- och z-utsträckningen breddad med `--margin`; höjden begränsas aldrig |
| korridor | x och z för varje punkt, se [Banexport](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html#the-corridor) |
| detalj | varje placerad kopias avstånd till närmaste punkt, se [Detaljnivåer och budgeten](detail-budget.md) |

Ett varv med färre än två punkter avvisas ("holds no driving").

## Fel {#errors}

| Meddelande | Betydelse |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | filen är inte JSON (och inte `.npz` eller `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON av annan form |
| `<file> has no x, y and z columns` | en CSV utan de rubrikerna |
| `<file> has no positions array` | en `.npz` utan `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | ett namn, men inget FH Companion-bibliotek |
| `'<name>' matches 3 courses: A, B, C` | var mer specifik |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | bara för namnuppslag och `courses` |
