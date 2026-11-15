---
title: Vstupy kola
nav_order: 7
lang: "sk"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Vstupy kola {#lap-inputs}

**Súbor kola** je zoznam bodov x, y, z: kam išlo auto. Najrýchlejší ručne vytvorený
je CSV v časti [5. Tabuľka `.csv`](#5-a-csv-table) nižšie.

Kolo hovorí exportu trate **kam auto išlo**. Nič iné v ňom sa nepoužíva: rýchlosť,
vstupy a g-sily patria telemetrickej časti 3DHeat. Nástroj číta pozície v svetových
metroch hry a tam, kde to súbor uvádza, aj hru a trať.

Zdroj: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Čo prijíma `course` {#what-course-accepts}

Formát sa rozpoznáva podľa obsahu súboru, nie podľa názvu, až na to, že `.npz` a `.csv`
sa rozpoznávajú podľa prípony; všetko ostatné sa skúša ako JSON.

### 1. Dokument `heat3d-lap` (ľubovoľná hra) {#a-heat3d-lap-document-any-game}

Zapisujú ho telemetrické zapisovače 3DHeat (`heat3d_capture telemetry`
([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y` a `channels.z` sú povinné. Riadky, kde niektorý z nich nie
  je konečné číslo, sa zahodia. Ostatné kanály sa ignorujú.
- `game` rozhoduje o exporte (pozri [Príkazy](commands.md#which-game)).
- `track` používa Assetto Corsa Rally na to, aby najprv vyskúšala pomenovanú etapu.
- Osi: y je výška. Kolá Forza a AC Rally používajú vodorovné osi hry tak, ako ich
  zapisovač zapisuje. Kolá BeamNG sa očakávajú v rámci prehliadača,
  `(x, z, -y)` svetа BeamNG so Z hore (pozri [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Súbor trasy {#a-route-file}

Zapisuje ho `heat3d_capture route` a `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` je zoznam `[x, y, z]`. Súbor trasy s `bounds` a bez pozícií stále funguje:
jeho dva rohy sú degenerovaná čiara, ale použiteľný box.

### 3. Súbor kola FH Companion {#an-fh-companion-lap-file}

Súbory jednotlivých kôl z nahranej knižnice FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Chýbajúce `X`, `Y` alebo `Z` sa čítajú ako 0. Súbory sa zapisujú s bajtovou značkou
poradia, takže všetok JSON sa číta ako `utf-8-sig`.

### 4. Nahrávka `.npz` {#a-npz-recording}

Archív NumPy, ktorý obsahuje pole `positions` s tvarom (n, 3).

### 5. Tabuľka `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Stĺpce pomenované `x`, `y`, `z` (bez ohľadu na veľkosť písmen a medzery okolo) sú
  povinné. Ostatné stĺpce sa ignorujú.
- Riadky začínajúce `#` sa preskočia. Ak **prvý** riadok je `# {json}`, čítajú sa z neho
  polia `game` a `track`.
- Riadky, ktoré sa nedajú prečítať ako čísla, sa preskočia.

### 6. Priečinok {#a-folder}

Priečinok sa prehľadáva **rekurzívne** za súbormi `.json`, `.npz` a `.csv` a všetky
sa spoja do jednej jazdnej čiary. Takto sa ukladá celý nahraný kurz: knižnica FH
Companion vnára priečinky podľa triedy, auta, ladenia a značky.

- `course.json` sa preskočí podľa názvu (sú to metadáta, nie kolo).
- Súbor, ktorý sa nedá prečítať, sa potichu preskočí. Jeden zlý súbor medzi stovkami
  nezruší zvyšok.
- Konzola hlási, koľko súborov kôl vošlo (`12 laps, 18,400 samples`).
- Priečinok dostane hru, ktorú pomenúvajú jeho súbory, ak pomenúvajú **len jednu**.
  Súbor, ktorý žiadnu hru nepomenúva (kolo FH Companion, `course.json`, CSV bez riadku
  s popisom), sa nepočíta, takže jeden z nich medzi nahrávkami hry nezoberie priečinku
  jeho hru. Súbory pomenúvajúce dve rôzne hry sú zmes a priečinok nedostane žiadnu.
  Priečinok bez hry sa exportuje ako Forza, pokiaľ `--game` nerozhodne inak.
- Ak sa nič neprečíta: „no readable laps under <folder>“.

### 7. Názov trate {#a-course-name}

Ak argument nie je existujúci súbor alebo priečinok, hľadá sa ako názov trate v knižnici
FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. priečinok, ktorého názov bez prípony ` (course_...)` sa rovná názvu (bez ohľadu na
   veľkosť písmen);
2. inak jediný priečinok, ktorého názov názov obsahuje.

Takže `"Example Circuit"` nájde
`Example Circuit (course_1200_3400_to_1175_3400)` bez toho, aby niekto poznal súradnice.
Viac zhôd je chyba, ktorá ich vypíše. Trať nájdená podľa názvu nenesie hru, takže sa
exportuje ako Forza, pokiaľ `--game` nerozhodne inak.

## Čo prijíma `terrain --route` {#what-terrain---route-accepts}

`terrain` potrebuje `bounds` súboru trasy (tvar 2 vyššie),
`{"min": [x, y, z], "max": [x, y, z]}`. Bez `bounds` sa zastaví s hláškou
„<file> has no bounds; --route takes a route file with "bounds": {...}“. Súbor sa číta
ako UTF-8 s bajtovou značkou alebo bez nej, ako každé JSON kolo. Ak má ten istý súbor
aspoň 10 pozícií čitateľných podľa pravidiel vyššie, zúžia rez na koridor a usmernia
detail.

## Ako sa kolo používa {#how-the-lap-is-used}

| Použitie | Podrobnosti |
|---|---|
| názov | základný názov súboru alebo názov priečinka bez ` (course_...)`; stane sa predvoleným názvom výstupného súboru |
| prejdená vzdialenosť | súčet medzier medzi po sebe idúcimi vzorkami (vypíše sa ako `m driven`; pri priečinku sú v tom aj skoky medzi súbormi) |
| box | rozsah x a z rozšírený o `--margin`; výška sa nikdy neohraničuje |
| koridor | x a z každej vzorky, pozri [Export trate](course-export.md#the-corridor) |
| detail | vzdialenosť každej umiestnenej kópie k najbližšej vzorke, pozri [Úrovne detailu a rozpočet](detail-budget.md) |

Kolo s menej ako dvoma vzorkami sa odmietne („holds no driving“).

## Chyby {#errors}

| Hláška | Význam |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | súbor nie je JSON (ani `.npz`, ani `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON iného tvaru |
| `<file> has no x, y and z columns` | CSV bez týchto hlavičiek |
| `<file> has no positions array` | `.npz` bez `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | názov, ale žiadna knižnica FH Companion |
| `'<name>' matches 3 courses: A, B, C` | buďte konkrétnejší |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | len pri hľadaní názvu a pri `courses` |
