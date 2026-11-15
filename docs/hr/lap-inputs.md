---
title: Ulazni podaci kruga
nav_order: 7
lang: "hr"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Ulazni podaci kruga {#lap-inputs}

**Datoteka kruga** je popis točaka x, y, z: kamo je auto išao. Najbrža ručno napravljena
je CSV tablica pod [5. `.csv` tablica](#5-a-csv-table) ispod.

Krug govori izvozu staze **kamo je auto išao**. Ništa drugo u njoj se ne koristi:
brzina, upravljanje i G-sile pripadaju telemetrijskoj strani 3DHeata. Alat čita pozicije
u svjetskim metrima igre, a, gdje to datoteka kaže, i igru i stazu.

Izvor: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Što prima `course` {#what-course-accepts}

Oblik se prepoznaje po sadržaju datoteke, a ne po imenu, osim što se `.npz` i `.csv`
prepoznaju po nastavku. Sve ostalo se proba kao JSON.

### 1. Dokument `heat3d-lap` (bilo koja igra) {#a-heat3d-lap-document-any-game}

Piše ga snimač telemetrije 3DHeata (`heat3d_capture telemetry`
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

- `channels.x`, `channels.y` i `channels.z` su obavezni. Reci u kojima bilo koja od
  te tri vrijednosti nije konačan broj se odbacuju. Ostali kanali se ignoriraju.
- `game` određuje izvoz (vidi [Naredbe](commands.md#which-game)).
- `track` koristi Assetto Corsa Rally da prvo isproba imenovanu etapu.
- Osi: y je visina. Krugovi Forze i AC Rallyja koriste vodoravne osi igre onako kako ih
  snimač zapisuje. Krugovi BeamNG-a očekuju se u okviru preglednika,
  `(x, z, -y)` BeamNG svijeta s Z prema gore (vidi [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Datoteka rute {#a-route-file}

Piše je `heat3d_capture route` i `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` je popis `[x, y, z]`. Datoteka rute s `bounds` ali bez pozicija i dalje
radi: njezina dva kuta čine degeneriranu liniju, ali upotrebljiv okvir.

### 3. Datoteka kruga FH Companiona {#an-fh-companion-lap-file}

Datoteke pojedinačnih krugova iz snimljene biblioteke FH Companiona:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Nedostajući `X`, `Y` ili `Z` čita se kao 0. Datoteke su pisane s oznakom redoslijeda
bajtova, pa se sav JSON čita kao `utf-8-sig`.

### 4. Snimka `.npz` {#a-npz-recording}

Arhiva NumPyja koja sadrži niz `positions` oblika (n, 3).

### 5. `.csv` tablica {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Stupci imenovani `x`, `y`, `z` (velika i mala slova te razmaci oko imena se
  ignoriraju) su obavezni. Ostali stupci se ignoriraju.
- Retci koji počinju s `#` preskaču se. Ako je **prvi** redak `# {json}`, čitaju se
  njegovi `game` i `track`.
- Reci koji se ne mogu pročitati kao brojevi preskaču se.

### 6. Mapa {#a-folder}

Mapa se pretražuje **rekurzivno** za datotekama `.json`, `.npz` i `.csv`, a sve se
spaja u jednu vožnju. Tako se sprema cijela snimljena staza: FH Companion slaže mape
po klasi, automobilu, podešavanju i oznaci.

- `course.json` se preskače po imenu (to su metapodaci, a ne krug).
- Datoteka koja se ne može pročitati preskače se tiho. Jedna loša datoteka među
  stotinama ne košta ostale.
- Konzola prijavljuje koliko je datoteka krugova ušlo (`12 laps, 18,400 samples`).
- Mapa dobiva igru koju njezine datoteke navode, ako navode **samo jednu**. Datoteka
  koja ne navodi igru (krug FH Companiona, `course.json`, CSV bez opisnog retka) se
  ne računa, pa jedna takva među snimkama jedne igre ne oduzima mapi njezinu igru.
  Datoteke koje navode dvije različite igre čine miješanje, i mapa ne dobiva nijednu.
  Mapa bez igre izvozi se kao Forza, osim ako `--game` kaže drugačije.
- Ako se ništa ne može pročitati: "no readable laps under <folder>".

### 7. Ime staze {#a-course-name}

Ako argument nije postojeća datoteka ili mapa, traži se kao ime staze u biblioteci
FH Companiona, `%LOCALAPPDATA%\FHCompanion\laps`:

1. mapa čije ime, bez nastavka ` (course_...)`, je jednako zadanom imenu (bez obzira na
   velika i mala slova);
2. inače jedina mapa čije ime sadrži zadani tekst.

Tako `"Example Circuit"` nalazi
`Example Circuit (course_1200_3400_to_1175_3400)` bez da itko zna koordinate.
Više podudaranja je greška koja ih navodi. Staza pronađena po imenu nema igru, pa se
izvozi kao Forza, osim ako `--game` kaže drugačije.

## Što prima `terrain --route` {#what-terrain---route-accepts}

`terrain` treba `bounds` datoteke rute (oblik 2 iznad),
`{"min": [x, y, z], "max": [x, y, z]}`. Bez `bounds` zaustavlja se s porukom
"<file> has no bounds; --route takes a route file with "bounds": {...}". Datoteka se čita
kao UTF-8 s oznakom redoslijeda bajtova ili bez nje, kao svaki JSON krug. Ako ista
datoteka ima i barem 10 pozicija čitljivih prema gore navedenim pravilima, one sužavaju
rez na koridor i usmjeravaju detalj.

## Kako se krug koristi {#how-the-lap-is-used}

| Upotreba | Pojedinosti |
|---|---|
| ime | osnova imena datoteke ili ime mape, bez ` (course_...)`; postaje zadano ime izlazne datoteke |
| prijeđena udaljenost | zbroj razmaka između uzastopnih uzoraka (ispisuje se kao `m driven`; kod mape uključuje skokove između datoteka) |
| okvir | raspon x i z proširen za `--margin`; visina se nikad ne ograničava |
| koridor | x i z svakog uzorka, vidi [Izvoz staze](course-export.md#the-corridor) |
| detalj | udaljenost svakog postavljenog primjerka do najbližeg uzorka, vidi [Razine detalja i proračun](detail-budget.md) |

Krug s manje od dva uzorka se odbija ("holds no driving", krug ne sadrži vožnju).

## Greške {#errors}

| Poruka | Značenje |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | datoteka nije JSON (ni `.npz` ni `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON drugog oblika |
| `<file> has no x, y and z columns` | CSV bez tih zaglavlja |
| `<file> has no positions array` | `.npz` bez `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | ime, ali nema biblioteke FH Companiona |
| `'<name>' matches 3 courses: A, B, C` | budite određeniji |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | samo za pretragu po imenu i za `courses` |
