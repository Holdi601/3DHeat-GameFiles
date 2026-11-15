---
title: "Hyrjet e xhiros"
nav_order: 7
lang: "sq"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Hyrjet e xhiros {#lap-inputs}

Një **skedar xhiroje** është një listë pikash x, y, z: ku shkoi makina jote. Më e shpejta e bërë
me dorë është CSV-ja te [5. Një tabelë `.csv`](#5-a-csv-table) më poshtë.

Një xhiro i tregon eksportit të kursit **ku shkoi makina**. Asgjë tjetër në të nuk përdoret:
shpejtësia, komandat dhe g-forcat i përkasin anës së telemetrisë të 3DHeat. Mjeti lexon
pozicionet në metra të botës së vetë lojës, plus, kur skedari e thotë, lojën
dhe pistën.

Burimi: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Çfarë pranon `course` {#what-course-accepts}

Formati njihet duke parë skedarin, jo emrin e tij, përveçse `.npz` dhe `.csv`
shkojnë sipas shtesës dhe çdo gjë tjetër provohet si JSON.

### 1. Një dokument `heat3d-lap` (çdo lojë) {#a-heat3d-lap-document-any-game}

Shkruhet nga regjistruesit e telemetrisë të 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y`, `channels.z` janë të detyrueshme. Rreshtat ku cilado nga
  të tria nuk është numër i fundëm hiqen. Kanalet e tjera injorohen.
- `game` vendos eksportin (shih [Komandat](commands.md#which-game)).
- `track` përdoret nga Assetto Corsa Rally për të provuar së pari etapën e emërtuar.
- Akset: y është lartësia. Xhirot e Forza dhe AC Rally përdorin akset horizontale të lojës ashtu
  siç i shkruan regjistruesi. Xhirot e BeamNG pritet të jenë në kornizën e shikuesit,
  `(x, z, -y)` i botës Z-lart të BeamNG (shih [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Një skedar rruge {#a-route-file}

Shkruhet nga `heat3d_capture route` dhe `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` është një listë `[x, y, z]`. Një skedar rruge me `bounds` por pa
pozicione prapë punon: dy cepat e tij janë një vijë e degjeneruar por një kuti e përdorshme.

### 3. Një skedar xhiroje FH Companion {#an-fh-companion-lap-file}

Skedarët për çdo xhiro të bibliotekës së regjistruar të FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Një `X`, `Y` ose `Z` që mungon lexohet si 0. Skedarët shkruhen me një shenjë të renditjes së bajteve
(byte-order mark), prandaj i gjithë JSON lexohet si `utf-8-sig`.

### 4. Një regjistrim `.npz` {#a-npz-recording}

Një arkiv NumPy që mban një varg `positions` me formë (n, 3).

### 5. Një tabelë `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolonat me emrat `x`, `y`, `z` (shkronjat e mëdha e të vogla dhe hapësirat përreth injorohen) janë të detyrueshme.
  Kolonat e tjera injorohen.
- Rreshtat që fillojnë me `#` anashkalohen. Nëse rreshti i **parë** është `# {json}`, lexohen
  `game` dhe `track` e tij.
- Rreshtat që nuk lexohen si numra anashkalohen.

### 6. Një dosje {#a-folder}

Një dosje kërkohet **në mënyrë rekursive** për skedarë `.json`, `.npz` dhe `.csv`, dhe
të gjithë bashkohen në një vijë të vetme vozitjeje. Kështu ruhet një kurs i tërë i regjistruar:
FH Companion fut brenda njëra-tjetrës dosje klase, makine, akordimi dhe etiketash.

- `course.json` anashkalohet sipas emrit (është metadata, jo xhiro).
- Një skedar që nuk lexohet anashkalohet në heshtje. Një skedar i keq mes qindrash
  nuk kushton të tjerët.
- Konsola raporton sa skedarë xhiroje hynë (`12 laps, 18,400 samples`).
- Dosja merr lojën që e emërtojnë skedarët e saj, kur emërtojnë **vetëm një**. Një skedar
  që nuk emërton lojë (një xhiro e FH Companion, `course.json`, një CSV pa rreshtin e
  përshkrimit) nuk llogaritet, prandaj një i tillë mes regjistrimeve të një loje
  nuk i kushton dosjes lojën. Skedarët që emërtojnë dy lojëra të ndryshme janë një përzierje,
  dhe dosja nuk merr asnjë. Një dosje pa lojë eksportohet si Forza përveç nëse
  `--game` thotë ndryshe.
- Nëse nuk lexohet asgjë: "no readable laps under <folder>".

### 7. Një emër kursi {#a-course-name}

Nëse argumenti nuk është skedar ose dosje ekzistuese, kërkohet si emër kursi
në bibliotekën e FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. një dosje emri i së cilës, pa prapashtesën ` (course_...)`, është i barabartë me emrin
   (pa dallim shkronjash të mëdha e të vogla);
2. përndryshe dosja e vetme emri i së cilës e përmban.

Kështu `"Example Circuit"` gjen
`Example Circuit (course_1200_3400_to_1175_3400)` pa e ditur kush koordinatat.
Disa përputhje janë një gabim që i liston. Një kurs i gjetur sipas emrit nuk mban lojë, prandaj
eksportohet si Forza përveç nëse `--game` thotë ndryshe.

## Çfarë pranon `terrain --route` {#what-terrain---route-accepts}

`terrain` ka nevojë për `bounds` të skedarit të rrugës (forma 2 më sipër),
`{"min": [x, y, z], "max": [x, y, z]}`. Pa `bounds`, ndalon me
"<file> has no bounds; --route takes a route file with "bounds": {...}". Skedari
lexohet si UTF-8 me ose pa shenjë renditjeje bajtesh, si çdo xhiro JSON. Nëse i njëjti skedar
ka edhe të paktën 10 pozicione të lexueshme sipas rregullave më sipër, ato e ngushtojnë prerjen
në një korridor dhe drejtojnë detajin.

## Si përdoret xhiroja {#how-the-lap-is-used}

| Përdorimi | Detaji |
|---|---|
| emri | trungu i skedarit, ose emri i dosjes, pa ` (course_...)`; bëhet emri i parazgjedhur i skedarit të daljes |
| largësia e vozitur | shuma e hapësirave mes mostrave të njëpasnjëshme (printohet si `m driven`; në një dosje kjo përfshin kërcimet mes skedarëve) |
| kutia | shtrirja x dhe z e zgjeruar me `--margin`; lartësia nuk kufizohet kurrë |
| korridori | x dhe z e çdo mostre, shih [Eksporti i kursit](course-export.md#the-corridor) |
| detaji | largësia e çdo kopjeje të vendosur nga mostra më e afërt, shih [Nivelet e detajit dhe buxheti](detail-budget.md) |

Një xhiro me më pak se dy mostra refuzohet ("holds no driving").

## Gabimet {#errors}

| Mesazhi | Kuptimi |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | skedari nuk është JSON (dhe jo `.npz` ose `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON me formë tjetër |
| `<file> has no x, y and z columns` | një CSV pa ato tituj |
| `<file> has no positions array` | një `.npz` pa `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | një emër, por pa bibliotekë FH Companion |
| `'<name>' matches 3 courses: A, B, C` | bëhu më specifik |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | vetëm për kërkimin e emrave dhe `courses` |
