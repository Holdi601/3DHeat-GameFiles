---
title: "Vhodi za krog"
nav_order: 7
lang: "sl"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Vhodi za krog {#lap-inputs}

**Datoteka kroga** je seznam točk x, y, z: kam je avto šel. Najhitreje ročno narejena je CSV pod [5. Tabela `.csv`](#5-a-csv-table) spodaj.

Krog izvoznemu toku proge pove, **kam je avto šel**. Nič drugega v njem se ne uporablja: hitrost, vnosi in g-sile pripadajo telemetrijskemu delu 3DHeat. Orodje bere položaje v svetovnih metrih igre, in kjer datoteka to pove, tudi igro in progo.

Vir: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Kaj sprejme `course` {#what-course-accepts}

Oblika se prepozna z gledanjem v datoteko, ne po imenu, razen da se `.npz` in `.csv` prepoznata po končnici, vse drugo pa se poskusi kot JSON.

### 1. Dokument `heat3d-lap` (katerakoli igra) {#a-heat3d-lap-document-any-game}

Zapisujejo ga snemalniki telemetrije 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y` in `channels.z` so obvezni. Vrstice, kjer kateri od treh ni končno število, se izpustijo. Drugi kanali se prezrejo.
- `game` določi izvoz (glejte [Ukazi](commands.md#which-game)).
- `track` Assetto Corsa Rally uporabi, da poskusi najprej navedeno etapo.
- Osi: y je višina. Krogi Forze in AC Rally uporabljajo vodoravni osi igre, kakor ju zapiše snemalnik. Krogi BeamNG so pričakovani v koordinatnem sistemu pregledovalnika, `(x, z, -y)` svetovnega sistema BeamNG z Z navzgor (glejte [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Datoteka poti {#a-route-file}

Zapiše jo `heat3d_capture route` in `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` je seznam `[x, y, z]`. Datoteka poti z `bounds`, a brez položajev, še vedno deluje: njena dva vogala sta degeneriran odsek, a uporabna škatla.

### 3. Datoteka kroga FH Companion {#an-fh-companion-lap-file}

Datoteke posameznih krogov iz zbirke posnetkov FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Manjkajoči `X`, `Y` ali `Z` se prebere kot 0. Datoteke so zapisane z oznako byte-order mark, zato se ves JSON bere kot `utf-8-sig`.

### 4. Posnetek `.npz` {#a-npz-recording}

Arhiv NumPy, ki hrani polje `positions` oblike (n, 3).

### 5. Tabela `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Stolpci z imeni `x`, `y`, `z` (velikost črk in presledki okoli ne štejejo) so obvezni. Drugi stolpci se prezrejo.
- Vrstice, ki se začnejo z `#`, se preskočijo. Če je **prva** vrstica `# {json}`, se prebereta njena `game` in `track`.
- Vrstice, ki se ne dajo prebrati kot številke, se preskočijo.

### 6. Mapa {#a-folder}

Mapa se preišče **rekurzivno** za datotekami `.json`, `.npz` in `.csv`, vse pa se zlepijo v eno vožnjo. Tako se shrani celotna posneta proga: zbirka FH Companion gnezdi mape razredov, avtomobilov, nastavitev in oznak.

- `course.json` se preskoči po imenu (je metapodatek, ne krog).
- Datoteka, ki je ni mogoče prebrati, se tiho preskoči. Ena slaba datoteka med stotinami ne stane ostalih.
- Konzola poroča, koliko datotek krogov je bilo vključenih (`12 laps, 18,400 samples`).
- Mapa dobi igro, ki jo navajajo njene datoteke, kadar navajajo **samo eno**. Datoteka, ki ne navaja igre (krog FH Companion, `course.json`, CSV brez vrstice z opisom), se ne šteje, zato ena takšna med posnetki igre ne stane mape njene igre. Datoteke, ki navajajo dve različni igri, so mešanica, in mapa ne dobi nobene. Mapa brez igre se izvozi kot Forza, razen če `--game` pove drugače.
- Če se nič ne da prebrati: "no readable laps under <folder>".

### 7. Ime proge {#a-course-name}

Če argument ni obstoječa datoteka ali mapa, se išče kot ime proge v zbirki FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. mapa, katere ime, brez pripone ` (course_...)`, je enako imenu (brez upoštevanja velikih črk);
2. sicer edina mapa, katere ime vsebuje ime.

Tako `"Example Circuit"` najde `Example Circuit (course_1200_3400_to_1175_3400)`, ne da bi kdo poznal koordinate. Več zadetkov je napaka, ki jih našteje. Proga, najdena po imenu, nima igre, zato se izvozi kot Forza, razen če `--game` pove drugače.

## Kaj sprejme `terrain --route` {#what-terrain---route-accepts}

`terrain` potrebuje `bounds` datoteke poti (oblika 2 zgoraj), `{"min": [x, y, z], "max": [x, y, z]}`. Brez `bounds` se ustavi z "<file> has no bounds; --route takes a route file with "bounds": {...}". Datoteka se prebere kot UTF-8 z oznako byte-order ali brez nje, kot vsak JSON krog. Če ima ista datoteka tudi vsaj 10 položajev, ki se dajo prebrati po zgornjih pravilih, zožijo rez na koridor in vodijo podrobnost.

## Kako se krog uporablja {#how-the-lap-is-used}

| Uporaba | Podrobnosti |
|---|---|
| ime | osnova imena datoteke ali ime mape, brez ` (course_...)`; postane privzeto ime izhodne datoteke |
| prevožena razdalja | vsota razmikov med zaporednimi vzorci (izpiše se kot `m driven`; pri mapi to vključuje skoke med datotekami) |
| škatla | razsežnost x in z, razširjena za `--margin`; višina ni nikoli omejena |
| koridor | x in z vsakega vzorca, glejte [Izvoz proge](course-export.md#the-corridor) |
| podrobnost | razdalja vsake postavljene kopije do najbližjega vzorca, glejte [Stopnje podrobnosti in proračun](detail-budget.md) |

Krog z manj kot dvema vzorcema je zavrnjen ("holds no driving").

## Napake {#errors}

| Sporočilo | Pomen |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | datoteka ni JSON (in ni `.npz` ali `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON druge oblike |
| `<file> has no x, y and z columns` | CSV brez teh glav |
| `<file> has no positions array` | `.npz` brez `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | ime, vendar ni knjižnice FH Companion |
| `'<name>' matches 3 courses: A, B, C` | bodi natančnejši |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | samo za iskanja po imenu in `courses` |
