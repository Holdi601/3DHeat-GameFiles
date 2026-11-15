---
title: Comenzi
nav_order: 2
lang: "ro"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Comenzi {#commands}

Fiecare comandă rulează ca `python -m heat3d_gamefiles <verb> ...` din folderul depozitului. Verbele sunt în ordinea în care le aveți de obicei nevoie: ce este acest fișier, ce se află în el, dă-mi acela și transformă un tur într-un traseu.

| Verb | Primește | Face |
|---|---|---|
| [`identify`](#identify) | orice fișier | spune ce format de container este, citind octeții lui |
| [`list`](#list) | un `.pak` Unreal sau un `.utoc` IoStore, un `.vpk` Source 2, un `.minizip` ForzaTech sau un zip | listează intrările lui |
| [`extract`](#extract) | același lucru | scrie o intrare pe disc |
| [`meshes`](#meshes) | un `SerializedFile` Unity | listează și verifică mesh-urile lui |
| [`course`](#course) | un tur | exportă traseul din jurul lui (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | o bibliotecă de ture înregistrate | rulează `course` pe fiecare traseu din ea (Forza) |
| [`races`](#races) | un Forza instalat | listează fiecare cursă pe care o definește jocul: ce adaugă, ce ascunde, locurile, starea exportului |
| [`terrain`](#terrain) | un folder de circuit Forza | taie o regiune după coordonatele lumii |
| [`levels`](#levels-and-level-frostbite) | un joc Frostbite instalat (Battlefield 6) | listează nivelurile lui |
| [`level`](#levels-and-level-frostbite) | numele unui nivel | exportă nivelul: terenul, mesh-urile plasate, opțional hărțile lor de culoare (Battlefield 6) |
| [`cars`](#cars) | un Forza instalat | fiecare mașină la detaliu redus, într-un singur fișier pentru fila de cursă a vizualizatorului |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | un joc Unreal 5 | listează hărțile lui World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | numele unei hărți | exportă harta: peisajul, structurile HLOD, apa |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | un Arma Reforger instalat | listează lumile lui |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | numele unei lumi | exportă lumea: terenul în culorile lui, marea, clădirile ca cutii |

**Cum se citesc exemplele:** `<x>` înseamnă că înlocuiți cu propria valoare, fără paranteze unghiulare; `[...]` este opțional; un drum cu spații se pune între "ghilimele duble", de exemplu `"C:\Games\My Game"`. Sunteți nou în asta? Vedeți [Înainte de a începe](before-you-start.md). Ajutorul complet (`--help`) al fiecărui verb se găsește în [Referința comenzilor](../cli-reference.md).

La fiecare pornire, programul poate verifica mai întâi dacă există o versiune nouă. Vedeți [Actualizări](updates.md). `HEAT3D_NO_UPDATE=1` oprește această verificare.

Sursa: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Pagini pas cu pas: [Inspectarea arhivelor](inspecting-archives.md), [Exportul traseului](course-export.md),
[Niveluri întregi](whole-levels.md), [Mașinile Forza](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Coduri de ieșire {#exit-codes}

| Cod | Înseamnă |
|---|---|
| 0 | succes |
| 1 | lucrul a eșuat (tur de necitit, joc negăsit, nimic de exportat, un traseu din `courses` a eșuat; pentru `list` și `extract`, un fișier care nu este niciuna dintre arhivele pe care le citesc, unul care nu poate fi deschis sau citit - un pak criptat fără `--key`, un container IoStore criptat - sau o intrare care nu există în arhivă) |
| 2 | argumente greșite (argparse), o cale care nu există, o `--key` care nu are 64 de cifre hexazecimale, sau `terrain` primit fie cu ambele, fie cu niciuna dintre `--box` și `--route` |

Erorile lui `list` și `extract` sunt fiecare o singură linie pe ieșirea de eroare standard, nu un traseu de eroare Python.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Aceasta citește fișierul și spune ce container este. Nu se ghidează după extensie (singura excepție este un `.ucas`, mai jos). Încearcă formatele în ordinea de mai jos și se oprește la primul care se poate citi:

1. **Unreal `.pak`**: un footer cu magia pak în ultimii 1.024 de octeți. Afișează versiunea, poziția și mărimea indexului, dacă indexul este criptat și metodele de compresie.
2. **Unreal IoStore `.utoc`**: magia IoStore la început. Afișează versiunea, numărul de fragmente și dacă containerul este criptat; pentru unul care nu este, numărul de fișiere pe care le numește directorul lui (și sub ce punct de montare), metodele de compresie și dacă `.ucas`-ul lui se află alături. Un `.ucas` nu are antet propriu, deci este recunoscut după `.utoc` cu același nume de lângă el, iar `identify` numește acest fișier.
3. **ForzaTech `.minizip`**: magia `PGZP`. Afișează versiunea, numărul de intrări și de segmente și dacă `ChunkContentsMiniZip<n>.txt`, care numește intrările, se află alături (și, dacă da, dacă numără câte intrări există).
4. **zip**: un antet de fișier local zip la început. Afișează numărul de intrări, cele mai frecvente șase extensii și numele nivelurilor când intrările se află sub `levels/<name>/`, ca într-o arhivă de nivel BeamNG.drive.
5. **Unity**: un pachet `UnityFS` (afișează versiunea motorului și numărul de intrări) sau un `SerializedFile` simplu (afișează formatul, versiunea motorului, numărul de obiecte și cele mai frecvente șase clase).
6. **Frostbite `.toc`**: afișează tipul (`plain` sau `signed`), unde începe arborele și fie numărul de active (tabelul binar de secțiuni), fie numărul de superpachete (arborele DbObject).
7. **Source 2 `.vpk`**: afișează versiunea, numărul de intrări și prima plasă de navigare `.nav`, dacă arhiva are una.
8. **BeamNG `.cdae`**: forma versiunea 31 care se poate citi. Afișează numărul de mesh-uri, numărul de niveluri de detaliu desenate și primele materiale.
9. **BeamNG `.ter`**: nu are magie, deci totul trebuie să se potrivească - o latură de la 2 la 16.384, atâtea înălțimi și octeți de straturi pe cât de mult este pătratul, apoi de la 1 la 255 de nume de straturi care se pot tipări. Afișează versiunea, mărimea și numele straturilor.
10. **ForzaTech `.modelbin`**: afișează versiunea, numărul de fragmente și cele mai frecvente șase etichete de fragmente. Conținutul fragmentelor nu este decodificat aici.

Formatele care au propria lor magie (2 până la 4) vin înaintea celor Unity și Frostbite, ale căror verificări citesc tot fișierul: o arhivă Forza are zeci de gigaocteți.

Dacă niciunul nu se potrivește, afișează `not a format this tool reads` și ultimul motiv. Motivul vine de la verificarea ForzaTech.

Exemplu (sintetic):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<archive>` | obligatoriu | un `.pak` Unreal; un `.utoc` IoStore (sau `.ucas`-ul de lângă el); un `.vpk` Source 2 (pentru VPK-uri împărțite, `_dir.vpk`); un `.minizip` ForzaTech; un zip, cum sunt arhivele de nivel și de conținut ale BeamNG |
| `--filter TEXT` | niciunul | doar căile care conțin TEXT, fără diferență între majuscule și minuscule |
| `--limit N` | 50 | afișează cel mult N intrări (numărul total se afișează mereu) |
| `--key HEX` | niciuna | o cheie AES-256 pe care o aveți deja, 64 de cifre hexazecimale, cu sau fără `0x`. Doar un `.pak` criptat o folosește. Orice care nu are 64 de cifre hexazecimale este refuzat înainte ca arhiva să fie deschisă (cod de ieșire 2) |

Programul decide formatul după octeți: un tabel de conținut IoStore, un `.minizip` și un VPK după semnătura cu care încep, un zip după antetul lui local, iar un `.pak` după footer-ul de la final. Un `.ucas` nu are antet și se deschide prin `.utoc` cu același nume. Un fișier care nu este niciuna dintre acestea este refuzat cu `<file> is not an archive list and extract read (...)`. Unul care este, dar nu poate fi deschis, este refuzat cu motivul cititorului: un pak criptat fără `--key`, un container IoStore criptat, o versiune de pak pe care nu o citește. În ambele cazuri este o linie și cod de ieșire 1.

Fiecare linie arată mărimea necomprimată, metoda de compresie și calea:

| Arhivă | Metodă | Căi |
|---|---|---|
| `.pak` | `none`, sau numele din footer (`Zlib`, `Oodle`, `Gzip`...) | cu punctul de montare al arhivei, de exemplu `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, sau metoda containerului (`Oodle`, `Zlib`...), așa cum este stocat primul lui bloc | cu punctul de montare, de exemplu `../../../<Project>/Content/...`. Un container fără index de director nu numește fișiere și este refuzat |
| `.vpk` | mereu `stored` | cum apar în director |
| `.minizip` | `lz4`, `deflate` sau `stored` | cum le scriu `ChunkContentsMiniZip<n>.txt` de lângă `GeoChunk<n>.minizip`, fără prefixul mașinii de build (cu backslash-uri, cum le scrie jocul). Arhiva nu stochează nume, deci fără acel fișier intrările sunt `#0`, `#1`... O listă al cărei număr de linii diferă de cel al intrărilor este refuzată: nu se potrivesc între ele |
| zip | `stored`, `deflate`, ... | cum sunt stocate; folderele nu se listează |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<archive>` | obligatoriu | ca la `list` |
| `<entry>` | obligatoriu | calea exact cum o afișează `list` (sensibilă la majuscule); într-un `.minizip`, merge și `#<număr>` |
| `--out FILE` | numele fișierului intrării (după ultimul `/` sau `\`), în folderul curent | unde se scrie; folderele părinte se creează |
| `--key HEX` | niciuna | ca la `list` |

Intrarea este decriptată (pak, cu o cheie), decomprimată și scrisă. Afișează `<bytes> bytes -> <file>`. Dacă calea nu există în arhivă, comanda iese cu codul 1. La fel se întâmplă și cu o intrare care nu poate fi citită (o intrare criptată fără cheie, sau comprimată cu Oodle fără biblioteca Oodle), cu motivul pe o linie. O intrare VPK nu este verificată aici după CRC. Cititorul are pentru asta o metodă `verify()` (vedeți [VPK Source 2](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<path>` | obligatoriu | un `SerializedFile` Unity simplu (`sharedassets0.assets`, `level0`...), nu un pachet |
| `--limit N` | 25 | decodează și afișează cel mult N mesh-uri |

Afișează numărul de obiecte `Mesh`, apoi câte o linie pentru fiecare mesh: numele (primele 40 de caractere), numărul de vârfuri și de triunghiuri și `ok` sau `BOUNDS DISAGREE`. `BOUNDS DISAGREE` înseamnă că vârfurile decodificate nu reproduc cutia de delimitare pe care Unity a stocat-o pentru mesh, în limita a 2% din mărimea cutiei. Este propria verificare a cititorului (vedeți [Unity](reader-unity.md)). Un mesh care nu poate fi citit este raportat cu motivul și se numără în limită. Datele de vârfuri dintr-un fișier `.resS` se citesc din folderul în care se află containerul.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Aceasta exportă traseul din jurul unui tur: terenul într-o bandă de fiecare parte a conducerii și ce stă pe el, ca un singur `.glb`. Restul îl află singură: ce joc, ce copie instalată, ce circuit, nivel sau etapă și (pentru Assetto Corsa Rally) în ce sens sunt axele. Vedeți [Exportul traseului](course-export.md).

`<lap>` poate fi oricare dintre următoarele (detalii în [Intrările de tur](lap-inputs.md)):

- un fișier de tur: JSON de traseu, JSON de tur FH Companion, JSON `heat3d-lap`, `.npz`, sau `.csv` cu coloanele x, y, z
- un folder cu fișiere de tur, căutat recursiv (un traseu înregistrat întreg)
- un **nume** de traseu, căutat în biblioteca FH Companion din `%LOCALAPPDATA%\FHCompanion\laps`

### Opțiuni {#options}

| Opțiune | Implicit | Jocuri | Înseamnă |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` în folderul curent | toate | unde se scrie; numele se scrie cu litere mici, iar secvențele de alte caractere se înlocuiesc cu `_` |
| `--game {forza,beamng,acrally}` | ce spune fișierul de tur, altfel `forza` | toate | din ce joc este turul |
| `--margin M` | 80 | toate | metri de teren păstrați de fiecare parte a conducerii |
| `--texture-size {2048,1024,512}` | 2048 | toate | pixeli de textură de teren pe fiecare pătrat de 512 m (2048 = 25 cm un pixel) |
| `--no-textures` | oprit | toate | doar culori plate: un fișier mult mai mic. Pentru Forza, asta sare și peste separarea drumului de bordură (vedeți mai jos) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | hărțile de teren și texturile modelelor din ce anotimp |
| `--no-placed` | oprit | toate | doar terenul: fără borduri, parapete, indicatoare, clădiri. Pentru BeamNG, suprafețele de rulare modelate ca mesh-uri rămân |
| `--trees` | oprit | toate | plasează și vegetația (Forza: copaci, tufișuri și obiecte care se sparg; BeamNG: copaci; AC Rally: copaci și vegetația instanțiată) |
| `--detail-budget N` | automat | toate | un plafon de triunghiuri pentru tot ce este plasat; vedeți [Nivelurile de detaliu și bugetul](detail-budget.md) |
| `--track DIR` | căutat | Forza | folderul circuitului (sub `media\Tracks`, cu `GeoChunk0.minizip`) dacă jocul instalat nu trebuie căutat |
| `--level NAME` | găsit din tur | BeamNG, AC Rally | nivelul (numele folderului BeamNG) sau etapa (numele hărții AC Rally), fără diferență între majuscule și minuscule |
| `--install DIR` | căutat în bibliotecile Steam | BeamNG, AC Rally | BeamNG: folderul cu `gameengine.zip`. AC Rally: folderul jocului, sau `acr\Content\Paks` / `Content\Paks` |

Opțiunile care nu se aplică unui joc sunt ignorate fără avertisment. De exemplu, `--season` nu face nimic pentru BeamNG și AC Rally, iar `--track` nu face nimic nici pentru ele.

### Ce joc {#which-game}

Jocul se ia din `--game`, apoi din câmpul `game` al unui fișier `heat3d-lap` (sau din linia de descriere `# {...}` a unui CSV), iar în lipsa lor este Forza. Un folder primește jocul pe care îl numesc fișierele lui, dacă numesc doar unul; un fișier care nu numește niciunul (un tur FH Companion, `course.json`, un CSV fără linie de descriere) nu contează (vedeți [Intrările de tur](lap-inputs.md)).

| Valoare | Export |
|---|---|
| începe cu `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` sau `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | refuzat: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | refuzat: "tracks ship in a protected format that is not a file-extraction target" |
| orice altceva | refuzat: "there is no course reader for <game> yet" |

Un refuz mai sugerează și alternativele: reconstruirea traseului din joc (3DHeat GameCapture), sau analiza tururilor fără traseu, deoarece fila Analiză de cursă a vizualizatorului desenează un drum din ele.

### Exemple {#examples}

```
# Un traseu din biblioteca FH Companion, după nume
python -m heat3d_gamefiles course "Example Circuit"

# Un fișier de tur, o bandă mai îngustă, un fișier mai mic
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Texturi de iarnă, cu copaci
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Un plafon ferm de 500.000 de triunghiuri plasate
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Un folder de circuit dat direct (jocul instalat în afara Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: numiți nivelul, arătați instalarea
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, cu un CSV simplu de tur care nu spune jocul
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Exemplu de ieșire (Forza, cifre sintetice):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Fiecare mașină a unui Forza instalat, la detaliul redus al jocului, într-un singur fișier pentru fila de cursă a vizualizatorului: modelul `ProxyLOD` pe care îl are fiecare arhivă de mașină din `media/Cars`, de aproximativ 900 de triunghiuri, cu numărul mașinii așa cum îl spune telemetria, marca, eticheta modelului și anul din numele arhivei, plus roțile și stopurile ei. Durează câteva secunde și scrie aproximativ 5 MB. Rulați-o din nou când jocul primește mașini noi. O arhivă fără un astfel de model (un obiect de trafic) este numită și lăsată afară. Formatul este în [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Formele sunt în metri, cele ale jocului: 1:1 cu mașina. Fișierul conține conținutul jocului, deci este pentru mașina pe care a fost făcut, nu pentru a fi trimis altora.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Aceasta rulează exportul de traseu Forza pe fiecare folder de traseu dintr-o bibliotecă de ture înregistrate, scriind câte un `<name>.glb` pentru fiecare. Este doar pentru Forza. Apelează direct exportul Forza și nu citește `--game`, `--level` sau `--install`.

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | folderul în care se scrie (se creează dacă lipsește) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteca de ture |
| `--only TEXT [TEXT ...]` | toate | doar traseele ale căror nume de folder conțin unul dintre acestea (fără diferență între majuscule și minuscule) |
| `--force` | oprit | exportă din nou ce are deja un `.glb` |
| `--track DIR` | căutat | ca la `course` |
| `--margin M` | 80 | ca la `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | ca la `course` |

Ce înseamnă un folder de traseu: un sub-folder direct al bibliotecii al cărui nume conține ` (course_`, cum le numește FH Companion, de exemplu `Example Circuit (course_1200_3400_to_1175_3400)`. Partea de la ` (course_` încolo se elimină din nume.

Cum se comportă o rulare:

- Un traseu al cărui `.glb` există deja este sărit (`kept`), în afară de cazul în care se dă `--force`, astfel încât o rulare întreruptă își continuă drumul de unde a rămas.
- Un `.glb` scris de o versiune mai veche, fără stratul și locurile proprii cursei (`asset.extras.course_format` lipsește sau este mai mic decât cel curent), se exportă din nou, ca și cum s-ar fi dat `--force` doar pentru el.
- Două foldere de traseu cu același nume înainte de ` (course_` (un înregistrator care a numit un traseu nou după unul vechi) nu se suprascriu: folderul creat primul păstrează `<name>.glb`, celălalt se scrie ca `<name>_<start>.glb`, `<start>` fiind locul de start, cu semnele minus scrise ca `m` (de exemplu `example_circuit_m120_m340.glb`).
- Un traseu care eșuează (ture ilizibile, memorie epuizată, fără teren...) este raportat ca `FAILED`, iar rularea continuă.
- La final afișează un tabel cu starea, mărimea în MB, secundele și numele, apoi `<n> of <total> courses in <folder>`.
- Codul de ieșire este 1 dacă vreun traseu a eșuat.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Listează fiecare cursă pe care o definește un Forza instalat, din definițiile ei de rute (vedeți [Traseele Forza Horizon](course-forza-horizon.md#which-race)), și verifică exporturile dintr-un folder `courses` față de ele. Citește jocul și biblioteca de ture; nu scrie nimic în afară de tabelul opțional.

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | folderul în care scrie `courses`, ale cărui fișiere se verifică |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteca de ture |
| `--track DIR` | căutat | folderul circuitului, dacă nu este cel al jocului instalat |
| `--markdown FILE` | niciunul | scrie și tabelul acolo, ca Markdown |

Un rând pentru fiecare cursă și unul pentru fiecare traseu înregistrat parcurs pe ea:

| Coloană | Înseamnă |
|---|---|
| route | id-ul rutei |
| course | traseul înregistrat care i se potrivește, dacă există |
| own assets | copiile pe care cursa le adaugă în lumea liberă |
| drawn | dintre acestea, copiile al căror model îl are circuitul |
| kinds | copiile adăugate, pe tipuri (parapete, recuzită, decalcuri, infrastructură, ...) |
| not geometry | markerii de spectatori și splinele de coliziune, numărate |
| hidden | obiectele din lumea liberă pe care cursa le elimină |
| venue | modelele de teren ale locurilor pe care linia de AI a cursei trece la mai puțin de 10 m |
| export | `current`, `older format` (exportat din nou de `courses`), `not exported`, sau gol pentru o cursă fără traseu înregistrat |

Se termină cu un număr: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Aceasta este tăierea Forza cu tot ce se specifică manual: dați folderul circuitului și o regiune, nu un tur. Este utilă când zona dorită este o cutie și nu o conducere.

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<path>` | obligatoriu | un folder de circuit Forza sub `media\Tracks` (cu `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | obligatoriu | `.glb`-ul de scris |
| `--box X0 Z0 X1 Z1` | | regiunea, în metrii jocului (x și z, așa cum le raportează telemetria); colțurile în orice ordine |
| `--route FILE` | | un JSON de rută cu `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, cum îl scriu `heat3d_capture route` și `heat3d_capture laps`; citit ca UTF-8, cu sau fără marcaj de ordine a octeților |
| `--margin M` | **100** | metri adăugați în jurul limitelor unei rute, și lățimea coridorului când ruta are o linie |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | ca la `course` |

Dați exact unul dintre `--box` și `--route`, altfel codul de ieșire este 2. Cu `--route`, tăierea este `bounds` (`min`/`max`, x și z) al rutei, lărgit cu marginea. Dacă fișierul mai are cel puțin 10 poziții, tăierea se îngustează la un coridor de `--margin` metri în jurul lor, iar modelele plasate își iau detaliul după distanța față de această linie. Cu `--box`, toată cutia se păstrează, iar detaliul merge către ce stă cel mai aproape de mijlocul cutiei.

Înălțimea nu face niciodată parte din tăiere. O cutie în afara hărții sau în mare dă "no terrain there" (cod de ieșire 1), nu o eroare despre coordonate.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` listează nivelurile pe care le are un joc Frostbite instalat, după numele tabelului lor (`levels/<level>/<level>.toc`), cu mărimea și de unde vin: `Data` pentru jocul de bază, `Update/<pack>` pentru o actualizare, și câte tabele de rezoluție mare adaugă la el. Un nivel pe care o actualizare îl aduce are un tabel mic de fragmente; și în jocul de bază există un tabel de fragmente al nivelului, dar tabelul cu pachetele nivelului este nivelul (vedeți [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` exportă unul: harta de înălțimi a terenului, fiecare mesh pe care îl plasează grupurile statice de modele ale nivelului, obiectele plasate una câte una, unde stau și fundalul de teren al nivelului în jurul hărții. Cu `--textures`, fiecare suprafață poartă harta ei de culoare; cu `--navmesh`, vin și suprafețele pe care merg soldații. Cum se citește este în [Frostbite](reader-frostbite.md).

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<level>` | obligatoriu | un nume cum îl afișează `levels`, o parte unică a lui sau calea unui `.toc` de nivel |
| `-o`, `--out FILE` | `<level>.glb` | `.glb`-ul de scris |
| `--install FOLDER` | primul joc Steam al cărui `Data` conține un `layout.toc` | folderul jocului |
| `--textures [PIXELS]` | oprit; 512 când se dă fără dimensiune | scrie harta de culoare a fiecărei suprafețe, cel mai mare mip nu mai mare de PIXELS pe latură, și coordonatele ei de textură așa cum le are jocul, cu un eșantionator care se repetă (vedeți [Formatul de ieșire](output-format.md)). Harta de înălțimi primește harta de culoare a fundalului de teren acolo unde acea hartă o acoperă, altfel culoarea de mijloc a materialelor de suprafață ale terenului, altfel culoarea medie a fundalului în jur. Fără opțiune, fiecare parte are o culoare plată |
| `--ground-texture [METRES]` | oprit; 0,5 când se dă fără dimensiune | coace decalcurile de teren - drumuri, piste, platforme, marcaje pictate - peste culoarea solului, înmulțite cu harta de culoare a terenului acolo unde nivelul o are, în culoarea hărții de înălțimi, METRES un pixel, în plăci de cel mult 4.096 pixeli (`ground:terrain x<x> z<z>`). Merge cu sau fără `--textures` |
| `--navmesh` | oprit | adaugă plasa de navigare a nivelului pentru cel mai mic agent, soldatul (1,8 m înălțime, 0,4 m lățime), ca partea `nav:walkable`: solul, podelele, scările și acoperișurile pe care le poate atinge un soldat, fără legăturile (sărituri, scări, escaladări) dintre ele |
| `--ground-spacing METRES` | 4 | cea mai fină distanță a hărții de înălțimi; nodurile mai fine decât atât se eșantionează mai rar. 0 lasă harta de înălțimi afară |
| `--detail-budget N` | fiecare copie la cel mai grosier nivel, plus un sfert, cel puțin 1.500.000 | un plafon de triunghiuri. Mesh-urile care costă cel mai mult coboară câte un nivel de detaliu pe rând până se încadrează; dacă nici cele mai grosiere nu se încadrează, cele mai mici copii se lasă afară primele. Fundalul de teren nu se simplifică și nu se lasă afară niciodată |
| `--skip TEXT` | | lasă afară grupurile statice de modele al căror nume de partiție conține TEXT; repetați pentru mai multe. Stratul unui mod de joc, de exemplu |
| `--by-mesh` | oprit | pentru a afla ce este o parte: o parte pentru fiecare mesh și material sursă, numită `<part> \| <mesh> \| <material>`; un fișier mult mai mare |
| `--clamped-uvs` | oprit | pentru un renderer care nu poate repeta o textură: taie fiecare triunghi texturat în bucăți ale căror coordonate stau între 0..1, și desenează un triunghi care ar avea nevoie de mai mult de 4 bucăți în culoarea medie a texturii lui, într-o parte `<part> (average colour)` |

Afișează grupurile și câte copii a plasat fiecare, mesh-urile lăsate afară și motivul, triunghiurile pe parte (și, cu `--textures`, câte texturi și câte secțiuni și-au găsit harta de culoare), ce este solul și, cu `--navmesh`, câte plăci de navigare s-au citit. Nu se scrie nimic despre nivel în afară de geometrie: fără nume, fără metadate (vedeți [Formatul de ieșire](output-format.md)).

Bugetul terenului este separat: harta de înălțimi și fundalul nu se simplifică niciodată prin `--detail-budget`; `--ground-spacing` dimensionează harta de înălțimi.

Un nivel întreg este mare: de obicei peste zece milioane de triunghiuri și câteva sute de MB. `--textures` adaugă puțin la fișier; un nivel plin de copaci poate ajunge la aproximativ 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` aduce un nivel la aproximativ o treime din asta.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` este folderul jocului, `Content/Paks` al lui, sau numele folderului său dintr-o bibliotecă Steam (`"<Steam game folder name>"`). `ue-maps` listează fiecare hartă care are alături celule World Partition compilate. `ue-map` exportă una ca `ground:<map>` (peisajul), `structure:<map>` (mesh-urile HLOD unite ale hărții) și `water:<map>` (corpurile ei de apă acolo unde stau deasupra solului), în **centimetri** Unreal, cu Y și Z schimbate - singurul export care nu este în metri. Cum se citește și se verifică fiecare: [Hărțile Unreal 5](level-unreal-world-partition.md).

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<map>` | obligatoriu | un nume cum îl afișează `ue-maps`, sau o parte unică a lui |
| `-o`, `--out FILE` | `<map>.glb` | `.glb`-ul de scris |
| `--ground-spacing METRES` | 2 | distanța dintre vârfurile peisajului în fișier, rotunjită la un număr întreg de pătrate proprii |
| `--no-structures`, `--no-water` | | lasă partea respectivă afară |

Afișează triunghiurile pe parte, câte componente de peisaj s-au citit și câte dintre vârfurile lor, stocate de două ori, nu se potrivesc. O hartă de 3 km la 2 m are aproximativ 4,6 milioane de triunghiuri de sol.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` listează fiecare lume cu un teren, după folderul ei din `worlds/`. `enfusion-world` exportă una: `ground:<world>` (terenul, în culorile plăcilor lui de supratextură), `water:<world>` (marea, la înălțimea zero) și `structure:<world>` (cutia fiecărui model plasat), în metrii jocului - x spre est, y în sus, z spre nord. Cum se citește și se verifică: [Lumile Arma Reforger](level-arma-reforger.md).

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `<world>` | obligatoriu | o lume cum o afișează `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb`-ul de scris |
| `--install FOLDER` | biblioteca Steam care conține jocul | folderul jocului |
| `--ground-spacing METRES` | 2 (al terenului) | distanța dintre vârfurile terenului în fișier |
| `--texture-size PIXELS` | 4096 | latura mai mare a imaginii de culoare a solului; 0 pentru culoare plată |
| `--no-structures` | | lasă modelele plasate afară |
| `--trees` | oprit | plasează și copacii și alte vegetații, ca cutii |

Afișează triunghiurile pe parte, câte vârfuri de margine de placă nu se potrivesc, câte entități are fișierul lumii și câte cutii s-au plasat, și ce s-a lăsat afară și de ce.

## Variabile de mediu {#environment-variables}

| Variabilă | Efect |
|---|---|
| `HEAT3D_OODLE` | calea către un `oo2core_*_win64.dll`, sau un folder care îl conține; vedeți [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | orice valoare în afară de goală, `0`, `false`, `no` oprește verificarea actualizărilor; vedeți [Actualizări](updates.md) |
| `LOCALAPPDATA` | unde se caută biblioteca FH Companion, folderul de utilizator al BeamNG și memoria cache a actualizărilor |
| `HEAT3D_COURSE` | doar pentru teste: traseul pe care îl folosește testul de bordură al jocului instalat; vedeți [Dezvoltarea](development.md) |
