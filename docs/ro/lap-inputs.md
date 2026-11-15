---
title: "Intrările de tur"
nav_order: 7
lang: "ro"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Intrările de tur {#lap-inputs}

Un **fișier de tur** este o listă de puncte x, y, z: unde a mers mașina. Cel mai simplu fișier făcut de mână este CSV-ul de la [5. Un tabel `.csv`](#5-un-tabel-csv) de mai jos.

Turul îi spune exportului de circuit **unde a mers mașina**. Nimic altceva din el nu se folosește: viteza, comenzile și forțele g aparțin părții de telemetrie a 3DHeat. Instrumentul citește pozițiile în metrii lumii jocului, plus, acolo unde fișierul o spune, jocul și traseul.

Sursa: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Ce acceptă `course` {#what-course-accepts}

Formatul se recunoaște după conținutul fișierului, nu după nume, cu excepția faptului că `.npz` și `.csv` se recunosc după extensie, iar orice altceva se încearcă ca JSON.

### 1. Un document `heat3d-lap` (orice joc) {#a-heat3d-lap-document-any-game}

Scris de înregistratoarele de telemetrie 3DHeat (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

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

- `channels.x`, `channels.y`, `channels.z` sunt obligatorii. Rândurile în care oricare dintre cele trei nu este un număr finit sunt eliminate. Celelalte canale sunt ignorate.
- `game` hotărăște exportul (vezi [Comenzi](commands.md#which-game)).
- `track` este folosit de Assetto Corsa Rally ca să încerce mai întâi etapa numită.
- Axele: y este înălțimea. Tururile Forza și AC Rally folosesc axele orizontale ale jocului, așa cum le scrie înregistratorul. Tururile BeamNG sunt așteptate în cadrul vizualizatorului, `(x, z, -y)` din lumea BeamNG cu Z în sus (vezi [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Un fișier de traseu {#a-route-file}

Scris de `heat3d_capture route` și `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` este o listă de `[x, y, z]`. Un fișier de traseu cu `bounds` și fără poziții funcționează în continuare: cele două colțuri ale lui sunt o linie degenerată, dar o casetă utilizabilă.

### 3. Un fișier de tur FH Companion {#an-fh-companion-lap-file}

Fișierele pe tur ale bibliotecii înregistrate de FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Un `X`, `Y` sau `Z` lipsă se citește ca 0. Fișierele sunt scrise cu un marcaj de ordine a octeților, deci tot JSON-ul se citește ca `utf-8-sig`.

### 4. O înregistrare `.npz` {#a-npz-recording}

O arhivă NumPy care conține un tablou `positions` de forma (n, 3).

### 5. Un tabel `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Coloanele numite `x`, `y`, `z` (fără a ține cont de majuscule și de spațiile din jur) sunt obligatorii. Celelalte coloane sunt ignorate.
- Liniile care încep cu `#` sunt sărite. Dacă **prima** linie este `# {json}`, `game` și `track` din ea sunt citite.
- Rândurile care nu se citesc ca numere sunt sărite.

### 6. Un folder {#a-folder}

Un folder este căutat **recursiv** după fișiere `.json`, `.npz` și `.csv`, iar toate sunt concatenate într-o singură linie parcursă. Așa se stochează un circuit înregistrat întreg: FH Companion își pune folderele pe clasă, mașină, reglaj și etichetă.

- `course.json` este sărit după nume (sunt metadate, nu un tur).
- Un fișier care nu se poate citi este sărit discret. Un fișier stricat printre sute nu strică restul.
- Consola raportează câte fișiere de tur au intrat (`12 laps, 18,400 samples`).
- Folderul primește jocul pe care îl numesc fișierele, când numesc **un singur** joc. Un fișier care nu numește niciun joc (un tur FH Companion, `course.json`, un CSV fără linia de descriere) nu contează, deci unul dintre acestea printre înregistrările unui joc nu îi ia folderului jocul. Fișierele care numesc două jocuri diferite sunt un amestec, iar folderul nu primește niciunul. Un folder fără joc se exportă ca Forza, dacă `--game` nu spune altceva.
- Dacă nimic nu se citește: "no readable laps under <folder>".

### 7. Un nume de circuit {#a-course-name}

Dacă argumentul nu este un fișier sau un folder existent, este căutat ca nume de circuit în biblioteca FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. un folder al cărui nume, fără sufixul ` (course_...)`, este egal cu numele (fără a ține cont de majuscule);
2. altfel, singurul folder al cărui nume îl conține.

Așadar, `"Example Circuit"` găsește `Example Circuit (course_1200_3400_to_1175_3400)` fără ca cineva să cunoască coordonatele. Mai multe potriviri sunt o eroare care le listează. Un circuit găsit după nume nu poartă joc, deci se exportă ca Forza, dacă `--game` nu spune altceva.

## Ce acceptă `terrain --route` {#what-terrain---route-accepts}

`terrain` are nevoie de `bounds` din fișierul de traseu (forma 2 de mai sus), `{"min": [x, y, z], "max": [x, y, z]}`. Fără `bounds`, se oprește cu "<file> has no bounds; --route takes a route file with "bounds": {...}". Fișierul se citește ca UTF-8 cu sau fără marcaj de ordine a octeților, ca orice tur JSON. Dacă același fișier are și cel puțin 10 poziții citibile după regulile de mai sus, acestea restrâng tăietura la un coridor și ghidează detaliul.

## Cum este folosit turul {#how-the-lap-is-used}

| Folosire | Detalii |
|---|---|
| nume | numele fișierului, sau numele folderului, fără ` (course_...)`; devine numele implicit al fișierului de ieșire |
| distanța parcursă | suma intervalelor dintre eșantioane consecutive (afișată ca `m driven`; pe un folder, include și săriturile dintre fișiere) |
| casetă | intervalul x și z lărgit cu `--margin`; înălțimea nu este niciodată limitată |
| coridor | x și z ale fiecărui eșantion, vezi [Export de circuit](course-export.md#the-corridor) |
| detaliu | distanța fiecărei copii plasate până la cel mai apropiat eșantion, vezi [Niveluri de detaliu și buget](detail-budget.md) |

Un tur cu mai puțin de două eșantioane este refuzat ("holds no driving").

## Erori {#errors}

| Mesaj | Înseamnă |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | fișierul nu este JSON (și nici `.npz` sau `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON de altă formă |
| `<file> has no x, y and z columns` | un CSV fără acele antete |
| `<file> has no positions array` | un `.npz` fără `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | un nume, dar nicio bibliotecă FH Companion |
| `'<name>' matches 3 courses: A, B, C` | fiți mai precis |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | doar pentru căutările după nume și pentru `courses` |
