---
title: "Hringinntök"
nav_order: 7
lang: "is"
source: lap-inputs.md
source_hash: "3f335d2fc454"
nav_exclude: true
search_exclude: true
---
# Hringinntök {#lap-inputs}

**Hringskrá** (lap file) er listi af x, y, z punktum: hvert bíllinn þinn fór. Fljótlegasta
handgerða skráin er CSV-skráin undir [5. `.csv` tafla](#5-a-csv-table) hér að neðan.

Hringur segir brautarútflutningnum **hvert bíllinn fór**. Ekkert annað í honum er notað:
hraði, inntök og g-kraftar tilheyra mælingahlið 3DHeat. Verkfærið les
staðsetningar í eigin heimsmetrum leiksins, auk, þar sem skráin segir til um það, leiksins
og brautarinnar.

Frumkóði: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Hvað `course` tekur við {#what-course-accepts}

Sniðið er þekkt með því að skoða skrána, ekki nafn hennar, nema að
`.npz` og `.csv` fara eftir endingu og allt annað er reynt sem JSON.

### 1. `heat3d-lap` skjal (hvaða leikur sem er) {#1-a-heat3d-lap-document-any-game}

Skrifað af mælingaupptökuforritum 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y`, `channels.z` eru nauðsynleg. Raðir þar sem eitthvert
  af þremur er ekki endanleg tala eru felldar niður. Aðrar rásir eru hunsaðar.
- `game` ræður útflutningnum (sjá [Skipanir](commands.md#which-game)).
- `track` er notað af Assetto Corsa Rally til að reyna nefndu sérleiðina fyrst.
- Ásar: y er hæð. Hringir í Forza og AC Rally nota láréttu ása leiksins eins og
  upptökuforritið skrifar þá. Búist er við að BeamNG hringir séu í ásakerfi skoðarans,
  `(x, z, -y)` úr Z-upp heimi BeamNG (sjá [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Leiðarskrá {#2-a-route-file}

Skrifuð af `heat3d_capture route` og `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` er listi af `[x, y, z]`. Leiðarskrá með `bounds` en án
staðsetninga virkar samt: hornin tvö eru úrkynjuð lína en nothæfur kassi.

### 3. FH Companion hringskrá {#3-an-fh-companion-lap-file}

Skrárnar fyrir hvern hring úr upptökusafni FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Vantandi `X`, `Y` eða `Z` les sem 0. Skrárnar eru skrifaðar með bætaröðunarmerki
(byte-order mark), svo allt JSON er lesið sem `utf-8-sig`.

### 4. `.npz` upptaka {#4-a-npz-recording}

NumPy skjalasafn sem geymir `positions` fylki af lögun (n, 3).

### 5. `.csv` tafla {#5-a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Dálkar sem heita `x`, `y`, `z` (hástafir og lágstafir og bil í kring hunsuð) eru nauðsynlegir.
  Aðrir dálkar eru hunsaðir.
- Línum sem byrja á `#` er sleppt. Ef **fyrsta** línan er `# {json}` eru `game`
  og `track` úr henni lesin.
- Raðir sem ekki þáttast sem tölur er sleppt.

### 6. Mappa {#6-a-folder}

Mappa er leituð **endurkvæmt** að `.json`, `.npz` og `.csv` skrám, og
þær allar eru settar saman í eina ekna línu. Þannig er heil upptekin
braut geymd: FH Companion hreiðrar flokka-, bíla-, stillinga- og merkjamöppur.

- `course.json` er sleppt eftir nafni (það eru lýsigögn, ekki hringur).
- Skrá sem les ekki er sleppt hljóðlega. Ein slæm skrá meðal hundraða
  kostar ekki restina.
- Skjárinn segir hve margar hringskrár fóru inn (`12 laps, 18,400 samples`).
- Mappan fær leikinn sem skrárnar nefna, þegar þær nefna **aðeins einn**. Skrá
  sem nefnir engan leik (FH Companion hringur, `course.json`, CSV án
  lýsingarlínunnar) telst ekki með, svo ein slík meðal upptaka leiks
  kostar ekki möppuna leikinn. Skrár sem nefna tvo ólíka leiki eru blanda,
  og mappan fær engan. Mappa án leiks er flutt út sem Forza nema
  `--game` segi annað.
- Ef ekkert les: „no readable laps under <folder>“.

### 7. Heiti brautar {#7-a-course-name}

Ef röksemdin er ekki til sem skrá eða mappa er hún flett upp sem heiti brautar
í FH Companion safninu, `%LOCALAPPDATA%\FHCompanion\laps`:

1. mappa þar sem heitið, með ` (course_...)` viðskeytið fjarlægt, er jafnt
   heitinu (án tillits til há- og lágstafa);
2. annars eina mappan þar sem heiti hennar inniheldur það.

Svo `"Example Circuit"` finnur
`Example Circuit (course_1200_3400_to_1175_3400)` án þess að nokkur þurfi að vita
hnitin. Mörg samsvörun er villa sem listar þær. Braut sem fannst með
heiti ber engan leik, svo hún er flutt út sem Forza nema `--game` segi annað.

## Hvað `terrain --route` tekur við {#what-terrain-route-accepts}

`terrain` þarf `bounds` leiðarskrárinnar (form 2 hér að ofan),
`{"min": [x, y, z], "max": [x, y, z]}`. Án `bounds` stöðvast það með
„<file> has no bounds; --route takes a route file with "bounds": {...}“. Skráin
er lesin sem UTF-8 með eða án bætaröðunarmerkis, eins og hvert JSON-hring. Ef sama skrá
hefur líka að minnsta kosti 10 staðsetningar sem lesast samkvæmt reglunum hér að ofan, þrengja þær skurðinn
í gang og stýra smáatriðum.

## Hvernig hringurinn er notaður {#how-the-lap-is-used}

| Notkun | Smáatriði |
|---|---|
| heiti | stofn skráarnafnsins, eða heiti möppunnar, með ` (course_...)` fjarlægt; það verður sjálfgefið heiti úttaksskrár |
| ekin vegalengd | summa bilanna milli samliggjandi sýna (prentuð sem `m driven`; yfir möppu telst með stökkin milli skráa) |
| kassi | umfang x og z víkkað með `--margin`; hæð er aldrei afmörkuð |
| gangur | x og z hvers sýnis, sjá [Brautarútflutningur](course-export.md#the-corridor) |
| smáatriði | fjarlægð hvers staðsetts eintaks að næsta sýni, sjá [Smáatriðastig og kostnaðarhámarkið](detail-budget.md) |

Hring með færri en tveimur sýnum er hafnað („holds no driving“).

## Villur {#errors}

| Skilaboð | Merking |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | skráin er ekki JSON (og ekki `.npz` eða `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON af annarri lögun |
| `<file> has no x, y and z columns` | CSV án þessara fyrirsagna |
| `<file> has no positions array` | `.npz` án `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | heiti, en ekkert FH Companion safn |
| `'<name>' matches 3 courses: A, B, C` | vertu nákvæmari |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | aðeins fyrir uppflettingu heita og `courses` |
