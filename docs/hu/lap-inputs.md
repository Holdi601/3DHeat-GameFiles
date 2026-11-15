---
title: Körfájl-bemenetek
nav_order: 7
lang: "hu"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Körfájl-bemenetek {#lap-inputs}

A **körfájl** x, y, z pontok listája: hogy hová ment az autó. A leggyorsabban kézzel
elkészíthető a [5. Egy `.csv` táblázat](#5-a-csv-table) alatti CSV.

A kör megmondja a pályaexportnak, **hová ment az autó**. Benne más nem kerül felhasználásra:
a sebesség, a bemenetek és a g-erők a 3DHeat telemetriai oldalához tartoznak. Az eszköz a játék
saját világméterben adott pozíciókat olvassa, és ahol a fájl megadja, a játékot és a pályát is.

Forrás: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Amit a `course` elfogad {#what-course-accepts}

A formátumot a fájl tartalma alapján ismeri fel, nem a neve alapján, kivéve hogy a `.npz` és a
`.csv` a kiterjesztésük alapján. Minden másat JSON-ként próbál.

### 1. Egy `heat3d-lap` dokumentum (bármely játék) {#a-heat3d-lap-document-any-game}

A 3DHeat telemetria-rögzítői írják (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- A `channels.x`, `channels.y` és `channels.z` kötelező. Azok a sorok, ahol bármelyik nem véges
  szám, kimaradnak. A többi csatornát figyelmen kívül hagyjuk.
- A `game` dönti el az exportot (lásd: [Parancsok](commands.md#which-game)).
- A `track`-et az Assetto Corsa Rally arra használja, hogy a megnevezett szakaszt próbálja meg
  először.
- Tengelyek: az y a magasság. A Forza és az AC Rally körei a játék vízszintes tengelyeit használják,
  ahogy a rögzítő írja. A BeamNG körei a nézegető keretében várhatók, a BeamNG Z-felfelé
  világának `(x, z, -y)` értékeiben (lásd: [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Egy útvonalfájl {#a-route-file}

A `heat3d_capture route` és `heat3d_capture laps` írja:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

A `positions` `[x, y, z]` értékek listája. Egy útvonalfájl, amely `bounds`-t tartalmaz pozíciók
nélkül is működik: a két sarka egy elfajult vonal, de használható doboz.

### 3. Egy FH Companion köri fájl {#an-fh-companion-lap-file}

Az FH Companion rögzített könyvtárának köri fájljai:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Hiányzó `X`, `Y` vagy `Z` 0-nak számít. A fájlokat bájtsorrend-jelzővel írják, ezért minden JSON
`utf-8-sig` kódolással olvasódik.

### 4. Egy `.npz` felvétel {#a-npz-recording}

Egy NumPy-archívum, amely `positions` tömböt tartalmaz, alakja (n, 3).

### 5. Egy `.csv` táblázat {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Az `x`, `y`, `z` nevű oszlopok kötelezők (a nagybetű-kisbetű és a szóközök nem számítanak).
  A többi oszlopot figyelmen kívül hagyjuk.
- A `#`-tel kezdődő sorokat kihagyjuk. Ha az **első** sor `# {json}`, abból olvassuk a `game`
  és a `track` értékeket.
- A számként nem értelmezhető sorokat kihagyjuk.

### 6. Egy mappa {#a-folder}

A mappát **rekurzívan** átnézzük `.json`, `.npz` és `.csv` fájlokért, és mindet egy vezetett
vonallá fűzzük össze. Így tárolódik egy teljes rögzített pálya: az FH Companion osztály-, autó-,
hangolás- és címkemappákba rendezi.

- A `course.json` névről kihagyjuk (metaadat, nem kör).
- A nem olvasható fájlt csendben kihagyjuk. Egy rossz fájl a több száz közül nem viszi el a többit.
- A konzol jelenti, hány köri fájl került be (`12 laps, 18,400 samples`).
- A mappa azt a játékot kapja, amelyet a fájljai **egyedül** megneveznek. Egy fájl, amely nem
  nevez meg játékot (egy FH Companion kör, a `course.json`, egy leíró sor nélküli CSV), nem számít,
  így egy ilyen egy játék felvételei között nem vonja meg tőle a játékot. Ha a fájlok két különböző
  játékot neveznek meg, az keveredés, és a mappa egyiket sem kapja. Játék nélküli mappát Forzaként
  exportálunk, hacsak a `--game` másképp nem mondja.
- Ha semmi nem olvasható: „no readable laps under <folder>".

### 7. Egy pályanév {#a-course-name}

Ha az argumentum nem létező fájl vagy mappa, akkor pályanévként keressük az FH Companion
könyvtárában, `%LOCALAPPDATA%\FHCompanion\laps`:

1. egy mappa, amelynek neve, a ` (course_...)` végződés nélkül, megegyezik a névvel (kis- és
   nagybetű nem számít);
2. különben az egyetlen mappa, amelynek neve tartalmazza.

Így a `"Example Circuit"` megtalálja a
`Example Circuit (course_1200_3400_to_1175_3400)`-t anélkül, hogy bárki ismerné a koordinátákat.
Több találat hiba, amely felsorolja őket. Névvel talált pálya nem hordoz játékot, ezért Forzaként
exportáljuk, hacsak a `--game` másképp nem mondja.

## Amit a `terrain --route` elfogad {#what-terrain---route-accepts}

A `terrain`-nek az útvonalfájl `bounds`-ja kell (a fenti 2. alak),
`{"min": [x, y, z], "max": [x, y, z]}`. `bounds` nélkül megáll ezzel: „<file> has no bounds;
--route takes a route file with "bounds": {...}". A fájlt UTF-8-ként olvassuk, bájtsorrend-jelzővel
vagy anélkül, mint minden JSON-kört. Ha ugyanebben a fájlban legalább 10 pozíció is van, amelyet a
fenti szabályok szerint lehet olvasni, azok a vágást sávra szűkítik és a részletességet irányítják.

## Hogyan használjuk a kört {#how-the-lap-is-used}

| Használat | Részletek |
|---|---|
| név | a fájl törzsneve, vagy a mappa neve, a ` (course_...)` végződés nélkül; ez lesz az alapértelmezett kimeneti fájlnév |
| megtett távolság | a szomszédos minták közötti távolságok összege (`m driven` formában kiírva; mappánál ide tartoznak a fájlok közötti ugrások is) |
| doboz | az x és z kiterjedés, `--margin`-nal szélesítve; a magasság soha nincs korlátozva |
| sáv | minden minta x és z értéke, lásd: [Pályaexport](course-export.md#the-corridor) |
| részletesség | minden elhelyezett példány távolsága a legközelebbi mintától, lásd: [Részletességi szintek és a keret](detail-budget.md) |

Egy kör, amelynek két mintánál kevesebb van, elutasított („holds no driving").

## Hibák {#errors}

| Üzenet | Jelentés |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | a fájl nem JSON (és nem `.npz` vagy `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | más alakú JSON |
| `<file> has no x, y and z columns` | CSV, amelyben nincsenek ezek a fejlécek |
| `<file> has no positions array` | `.npz`, amelyben nincs `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | egy név, de nincs FH Companion könyvtár |
| `'<name>' matches 3 courses: A, B, C` | legyél pontosabb |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | csak névkeresésnél és a `courses`-nál |
