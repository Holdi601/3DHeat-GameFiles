---
title: "Ulazi kruga"
nav_order: 7
lang: "bs"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Ulazi kruga {#lap-inputs}

**Datoteka kruga** je lista x, y, z tačaka: gdje je išao vaš auto. Najbrža ručno
napravljena je CSV ispod, u [5. `.csv` tablica](#a-csv-table).

Krug kaže izvozu staze **gdje je auto išao**. Ništa drugo u njemu se ne koristi:
brzina, komande i g-sile pripadaju telemetrijskoj strani 3DHeata. Alat čita
pozicije u vlastitim svjetskim metrima igre, plus, gdje datoteka to kaže, igru i
stazu.

Izvor: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Šta `course` prihvata {#what-course-accepts}

Format se prepoznaje gledanjem u datoteku, a ne u njeno ime, osim što se `.npz` i
`.csv` određuju po ekstenziji, a sve ostalo se pokušava kao JSON.

### 1. Dokument `heat3d-lap` (bilo koja igra) {#a-heat3d-lap-document-any-game}

Pišu ga 3DHeat telemetrijski snimači (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y`, `channels.z` su obavezni. Redovi u kojima bilo koji
  od ta tri nije konačan broj odbacuju se. Ostali kanali se ignoriraju.
- `game` određuje izvoz (pogledajte [Komande](commands.md#which-game)).
- `track` koristi Assetto Corsa Rally da prvo isproba imenovanu etapu.
- Ose: y je visina. Krugovi za Forzu i AC Rally koriste horizontalne ose igre
  onako kako ih snimač piše. Krugovi za BeamNG očekuju se u okviru preglednika,
  `(x, z, -y)` BeamNG-ovog svijeta sa Z prema gore (pogledajte [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Datoteka rute {#a-route-file}

Pišu je `heat3d_capture route` i `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` je lista `[x, y, z]`. Datoteka rute s `bounds` a bez pozicija i dalje
radi: njena dva ugla su degenerirana linija, ali upotrebljiva kutija.

### 3. Datoteka kruga FH Companion {#an-fh-companion-lap-file}

Datoteke po krugu iz snimljene biblioteke FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Nedostajući `X`, `Y` ili `Z` čita se kao 0. Datoteke se pišu s oznakom redoslijeda
bajtova (BOM), pa se sav JSON čita kao `utf-8-sig`.

### 4. Snimak `.npz` {#a-npz-recording}

NumPy arhiva koja sadrži niz `positions` oblika (n, 3).

### 5. `.csv` tablica {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolone nazvane `x`, `y`, `z` (velika/mala slova i okolni razmaci se ignoriraju)
  su obavezne. Ostale kolone se ignoriraju.
- Redovi koji počinju sa `#` se preskaču. Ako je **prvi** red `# {json}`, čitaju
  se njegovi `game` i `track`.
- Redovi koji se ne parsiraju kao brojevi se preskaču.

### 6. Folder {#a-folder}

Folder se pretražuje **rekurzivno** za `.json`, `.npz` i `.csv` datoteke, a sve
se spajaju u jednu vožnu liniju. Tako se pohranjuje cijela snimljena staza: FH
Companion ugnježđuje foldere klase, auta, podešavanja i oznake.

- `course.json` se preskače po imenu (to su metapodaci, a ne krug).
- Datoteka koja se ne može pročitati preskače se tiho. Jedna loša datoteka među
  stotinama ne košta ostale.
- Konzola prijavljuje koliko je datoteka krugova ušlo (`12 laps, 18,400 samples`).
- Folder dobija igru koju njegove datoteke navode, kad navode **samo jednu**.
  Datoteka koja ne navodi igru (krug FH Companion, `course.json`, CSV bez reda
  opisa) ne računa se, pa jedna takva među snimcima jedne igre folder ne košta
  njegove igre. Datoteke koje navode dvije različite igre su mješavina i folder
  ne dobija nijednu. Folder bez igre izvozi se kao Forza osim ako `--game` ne
  kaže drugačije.
- Ako se ništa ne pročita: "no readable laps under <folder>".

### 7. Ime staze {#a-course-name}

Ako argument nije postojeća datoteka ili folder, traži se kao ime staze u
biblioteci FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. folder čije ime, s uklonjenim sufiksom ` (course_...)`, jednako je imenu
   (bez obzira na velika i mala slova);
2. inače jedini folder čije ime ga sadrži.

Tako `"Example Circuit"` pronalazi
`Example Circuit (course_1200_3400_to_1175_3400)` a da niko ne zna koordinate.
Više poklapanja je greška koja ih navodi. Staza pronađena po imenu ne nosi igru,
pa se izvozi kao Forza osim ako `--game` ne kaže drugačije.

## Šta `terrain --route` prihvata {#what-terrain---route-accepts}

`terrain` treba `bounds` datoteke rute (oblik 2 gore),
`{"min": [x, y, z], "max": [x, y, z]}`. Bez `bounds` staje s porukom
"<file> has no bounds; --route takes a route file with "bounds": {...}". Datoteka
se čita kao UTF-8 sa ili bez oznake redoslijeda bajtova, kao svaki JSON krug. Ako ista datoteka
ima i barem 10 pozicija čitljivih po gornjim pravilima, one sužavaju rez na
koridor i usmjeravaju detalj.

## Kako se krug koristi {#how-the-lap-is-used}

| Upotreba | Detalj |
|---|---|
| ime | ime datoteke (stem) ili ime foldera, s uklonjenim ` (course_...)`; postaje zadano ime izlazne datoteke |
| pređena udaljenost | zbir razmaka između uzastopnih uzoraka (ispisuje se kao `m driven`; preko foldera to uključuje skokove između datoteka) |
| kutija | x i z opseg proširen za `--margin`; visina nikad nije ograničena |
| koridor | x i z svakog uzorka, pogledajte [Izvoz staze](course-export.md#the-corridor) |
| detalj | udaljenost svake postavljene kopije do najbližeg uzorka, pogledajte [Nivoi detalja i budžet](detail-budget.md) |

Krug s manje od dva uzorka se odbija ("holds no driving").

## Greške {#errors}

| Poruka | Značenje |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | datoteka nije JSON (a nije ni `.npz` ni `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON drugog oblika |
| `<file> has no x, y and z columns` | CSV bez tih zaglavlja |
| `<file> has no positions array` | `.npz` bez `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | ime, ali nema biblioteke FH Companion |
| `'<name>' matches 3 courses: A, B, C` | budite precizniji |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | samo za traženje imena i `courses` |
