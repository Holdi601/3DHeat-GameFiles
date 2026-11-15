---
title: Kierrosten syötteet
nav_order: 7
lang: "fi"
source: lap-inputs.md
source_hash: "3f335d2fc454"
nav_exclude: true
search_exclude: true
---
# Kierrosten syötteet {#lap-inputs}

**Kierrostiedosto** on lista x-, y- ja z-pisteitä: missä auto kulki. Nopein
käsin tehty on CSV kohdassa [5. `.csv`-taulukko](#5-a-csv-table) alla.

Kierros kertoo radan viennille **missä auto kulki**. Muuta siinä ei käytetä:
nopeus, syötteet ja g-voimat kuuluvat 3DHeatin telemetriapuolelle. Työkalu lukee
sijainnit pelin omina maailmametreinä, ja lisäksi pelin ja radan, jos tiedosto
niin kertoo.

Lähde: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Mitä `course` hyväksyy {#what-course-accepts}

Muoto tunnistetaan tiedoston sisällöstä, ei nimestä. Poikkeuksena `.npz` ja `.csv`,
jotka tunnistetaan tiedostopäätteestä, ja kaikki muu yritetään JSON:ina.

### 1. `heat3d-lap`-asiakirja (mikä tahansa peli) {#a-heat3d-lap-document-any-game}

Kirjoittavat 3DHeatin telemetriatallentimet (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y` ja `channels.z` vaaditaan. Rivit, joissa jokin näistä
  ei ole äärellinen luku, pudotetaan. Muut kanavat ohitetaan.
- `game` päättää viennin (katso [Komennot](commands.md#which-game)).
- `track`-kenttää Assetto Corsa Rally käyttää kokeillakseen nimettyä vaihetta ensin.
- Akselit: y on korkeus. Forza- ja AC Rally -kierrokset käyttävät pelin vaakasuuntaisia
  akseleita sellaisinaan kuin tallennin ne kirjoittaa. BeamNG-kierrosten odotetaan
  olevan katseluohjelman koordinaatistossa, `(x, z, -y)` BeamNG:n Z-ylös-maailmasta
  (katso [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Reittitiedosto {#a-route-file}

Kirjoittavat `heat3d_capture route` ja `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` on lista `[x, y, z]`-pisteitä. Reittitiedosto, jossa on `bounds` mutta
ei positions-kenttää, toimii yhä: sen kaksi kulmaa ovat rappeutunut viiva, mutta
käyttökelpoinen laatikko.

### 3. FH Companionin kierrostiedosto {#an-fh-companion-lap-file}

FH Companionin tallennetun kirjaston kierrostiedostot:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Puuttuva `X`, `Y` tai `Z` luetaan nollaksi. Tiedostot kirjoitetaan tavujärjestysmerkin
kanssa, joten kaikki JSON luetaan `utf-8-sig`-koodauksella.

### 4. `.npz`-tallenne {#a-npz-recording}

NumPy-arkisto, joka sisältää `positions`-taulukon, jonka muoto on (n, 3).

### 5. `.csv`-taulukko {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- `x`-, `y`- ja `z`-nimiset sarakkeet (kirjainkoko ja ympäröivät välilyönnit eivät
  merkitse) vaaditaan. Muut sarakkeet ohitetaan.
- Rivit, jotka alkavat `#`-merkillä, ohitetaan. Jos **ensimmäinen** rivi on `# {json}`,
  sen `game` ja `track` luetaan.
- Rivit, joita ei voi jäsentää luvuiksi, ohitetaan.

### 6. Kansio {#a-folder}

Kansiosta haetaan **rekursiivisesti** `.json`-, `.npz`- ja `.csv`-tiedostot, ja
kaikki yhdistetään yhdeksi ajetuksi viivaksi. Näin koko tallennettu rata säilytetään:
FH Companion sisäkkää luokka-, auto-, säätö- ja tunnistekansiot.

- `course.json` ohitetaan nimellä (se on metadataa, ei kierros).
- Tiedosto, jota ei voi lukea, ohitetaan hiljaa. Yksi huono tiedosto sadoista ei
  maksa muita.
- Konsoli ilmoittaa, kuinka monta kierrostiedostoa otettiin (`12 laps, 18,400 samples`).
- Kansio saa pelin, jonka sen tiedostot nimeävät, kun ne nimeävät **vain yhden**.
  Tiedosto, joka ei nimeä peliä (FH Companionin kierros, `course.json`, CSV ilman
  kuvausriviä), ei lasketa, joten yksi niistä pelin tallenteiden joukossa ei vie
  kansiolta sen peliä. Tiedostot, jotka nimeävät kaksi eri peliä, ovat sekoitus, ja
  kansio ei saa yhtään. Kansio ilman peliä viedään Forzana, ellei `--game` sano muuta.
- Jos mikään ei lue: "no readable laps under <folder>".

### 7. Radan nimi {#a-course-name}

Jos argumentti ei ole olemassa oleva tiedosto tai kansio, se haetaan radan nimenä
FH Companionin kirjastosta, `%LOCALAPPDATA%\FHCompanion\laps`:

1. kansio, jonka nimi (ilman ` (course_...)`-päätettä) on sama kuin nimi
   (kirjainkoosta riippumatta);
2. muuten ainoa kansio, jonka nimi sisältää sen.

Joten `"Example Circuit"` löytää kansion
`Example Circuit (course_1200_3400_to_1175_3400)` kenenkään tietämättä koordinaatteja.
Useat osumat ovat virhe, joka listaa ne. Nimen perusteella löydetty rata ei kanna
peliä, joten se viedään Forzana, ellei `--game` sano muuta.

## Mitä `terrain --route` hyväksyy {#what-terrain---route-accepts}

`terrain` tarvitsee reittitiedoston `bounds`-kentän (muoto 2 yllä),
`{"min": [x, y, z], "max": [x, y, z]}`. Ilman `bounds`-kenttää se pysähtyy viestiin
"<file> has no bounds; --route takes a route file with "bounds": {...}". Tiedosto
luetaan UTF-8:na tavujärjestysmerkin kanssa tai ilman, kuten jokainen JSON-kierros.
Jos sama tiedosto sisältää myös vähintään 10 sijaintia, jotka voidaan lukea yllä
olevien sääntöjen mukaan, ne kaventavat leikkauksen käytäväksi ja ohjaavat
yksityiskohtia.

## Miten kierrosta käytetään {#how-the-lap-is-used}

| Käyttö | Yksityiskohta |
|---|---|
| nimi | tiedoston kantanimi tai kansion nimi ilman ` (course_...)`-päätettä; siitä tulee oletustiedostonimi |
| ajettu matka | peräkkäisten näytteiden välien summa (tulostuu `m driven`; kansiossa mukana ovat myös tiedostojen väliset hypyt) |
| laatikko | x- ja z-ulottuvuus, levennettynä `--margin`-arvolla; korkeutta ei rajata koskaan |
| käytävä | jokaisen näytteen x ja z, katso [Radan vienti](course-export.md#the-corridor) |
| yksityiskohdat | jokaisen sijoitetun kopion etäisyys lähimpään näytteeseen, katso [Yksityiskohtatasot ja budjetti](detail-budget.md) |

Kierros, jossa on alle kaksi näytettä, hylätään ("holds no driving").

## Virheet {#errors}

| Viesti | Merkitys |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | tiedosto ei ole JSON (eikä `.npz` tai `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON jonkin muun muotoista |
| `<file> has no x, y and z columns` | CSV ilman näitä otsikoita |
| `<file> has no positions array` | `.npz` ilman `positions`-taulukkoa |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | nimi, mutta ei FH Companionin kirjastoa |
| `'<name>' matches 3 courses: A, B, C` | ole tarkempi |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | vain nimihaussa ja `courses`-komennossa |
