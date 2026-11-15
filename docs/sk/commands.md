---
title: "Príkazy"
nav_order: 2
lang: "sk"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Príkazy {#commands}

Každý príkaz sa spúšťa ako `python -m heat3d_gamefiles <verb> ...` z priečinka
repozitára. Slovesá sú v poradí, v akom ich zvyčajne potrebujete: čo je to za
súbor, čo je vo vnútri, ako z neho vybrať jednu položku a ako premeniť kolo na trať.

| Sloveso | Berie | Robí |
|---|---|---|
| [`identify`](#identify) | ľubovoľný súbor | podľa bajtov zistí formát kontajnera |
| [`list`](#list) | Unreal `.pak` alebo IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` alebo zip | vypíše jeho položky |
| [`extract`](#extract) | to isté | zapíše jednu položku na disk |
| [`meshes`](#meshes) | Unity `SerializedFile` | vypíše a skontroluje jeho siete |
| [`course`](#course) | kolo | exportuje trať okolo neho (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | knižnicu zaznamenaných kôl | spustí `course` na každej trati v nej (Forza) |
| [`races`](#races) | nainštalovanú Forzu | vypíše každé preteky, ktoré hra definuje: čo pridávajú, čo skrývajú, miesta konania a stav ich exportu |
| [`terrain`](#terrain) | priečinok trate Forzy | vyreže oblasť podľa svetových súradníc |
| [`levels`](#levels-and-level-frostbite) | nainštalovanú hru Frostbite (Battlefield 6) | vypíše jej úrovne |
| [`level`](#levels-and-level-frostbite) | názov úrovne | exportuje úroveň: terén, umiestnené siete, voliteľne ich farebné mapy (Battlefield 6) |
| [`cars`](#cars) | nainštalovanú Forzu | každé auto v nízkom detaile, v jednom súbore pre kartu Analýza pretekov v prehliadači |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | hru Unreal 5 | vypíše jej mapy World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | názov mapy | exportuje mapu: krajinu, zlúčené štruktúry HLOD, vodu |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | nainštalovaný Arma Reforger | vypíše jeho svety |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | názov sveta | exportuje svet: terén vo farbách, more, budovy ako krabice |

**Ako čítať príklady:** `<x>` znamená, že to nahradíte vlastnou hodnotou, bez
lomených zátvoriek; `[...]` je voliteľné; cestu s medzerami uzavrite do
"dvojitých úvodzoviek", napríklad `"C:\Games\My Game"`. Ste tu noví? Pozrite si
[Ako začať](before-you-start.md). Úplný `--help` každého slovesa je na
[Referencii príkazov](../cli-reference.md).

Pri každom spustení program môže najprv skontrolovať, či nie je novšia verzia.
Pozrite si [Aktualizácie](updates.md). `HEAT3D_NO_UPDATE=1` túto kontrolu vypne.

Zdroj: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Podrobné návody: [Prezeranie archívov](inspecting-archives.md), [Export trate](course-export.md),
[Celé úrovne](whole-levels.md), [Autá Forzy](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Návratové kódy {#exit-codes}

| Kód | Význam |
|---|---|
| 0 | úspech |
| 1 | práca zlyhala (nečitateľné kolo, nenájdená hra, nič na export, trať v `courses` zlyhala; pri `list` a `extract` súbor, ktorý nie je žiadnym z archívov, ktoré čítajú, alebo sa nedá otvoriť či prečítať - zašifrovaný pak bez `--key`, zašifrovaný kontajner IoStore - alebo položka v archíve chýba) |
| 2 | zlé argumenty (argparse), cesta, ktorá neexistuje, `--key`, ktorý nemá 64 hexadecimálnych číslic, alebo `terrain` dostal naraz oba alebo ani jeden z `--box` a `--route` |

Chyby `list` a `extract` sú každá jeden riadok na štandardnom chybovom výstupe,
nie výpis Python traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Tento príkaz prečíta súbor a povie, o aký kontajner ide. Nerozhoduje podľa
prípony (jedinou výnimkou je `.ucas`, pozri nižšie). Formáty skúša v tomto
poradí a zastaví sa pri prvom, ktorý sa dá prečítať:

1. **Unreal `.pak`**: pätička s magickou hodnotou pak v posledných 1 024 bajtoch.
   Vypíše verziu, offset a veľkosť indexu, či je index zašifrovaný, a metódy
   kompresie.
2. **Unreal IoStore `.utoc`**: magická hodnota IoStore na začiatku. Vypíše
   verziu, počet blokov a či je kontajner zašifrovaný; ak nie je, počet súborov,
   ktoré pomenúva jeho adresár (a pod akým mount bodom), metódy kompresie a či je
   vedľa neho jeho `.ucas`. `.ucas` nemá vlastnú hlavičku, takže sa spoznáva podľa
   `.utoc` rovnakého mena vedľa neho, a `identify` pomenuje tento súbor.
3. **ForzaTech `.minizip`**: magická hodnota `PGZP`. Vypíše verziu, počet položiek
   a segmentov a či je vedľa neho `ChunkContentsMiniZip<n>.txt`, ktorý pomenúva
   položky (a ak áno, či ich pomenúva rovnako veľa).
4. **zip**: hlavička lokálneho súboru zip na začiatku. Vypíše počet položiek, šesť
   najčastejších prípon a názvy úrovní, ak položky ležia pod `levels/<name>/`, ako
   v archíve úrovne BeamNG.drive.
5. **Unity**: zväzok `UnityFS` (vypíše verziu enginu a počet položiek) alebo
   samostatný `SerializedFile` (vypíše formát, verziu enginu, počet objektov a šesť
   najčastejších tried).
6. **Frostbite `.toc`**: vypíše druh (`plain` alebo `signed`), kde sa začína strom,
   a buď počet aktív (binárna tabuľka sekcií), alebo počet superbalíkov (strom
   DbObject).
7. **Source 2 `.vpk`**: vypíše verziu, počet položiek a prvú sieť navigácie `.nav`,
   ak ju archív má.
8. **BeamNG `.cdae`**: verzia tvaru 31, ktorá sa dá prečítať. Vypíše počet sietí,
   počet vykreslených úrovní detailu a prvé materiály.
9. **BeamNG `.ter`**: nemá magickú hodnotu, takže všetko musí sedieť - strana 2 až
   16 384, toľko výšok a bajtov vrstiev na druhú, potom 1 až 255 tlačiteľných
   názvov vrstiev. Vypíše verziu, veľkosť a názvy vrstiev.
10. **ForzaTech `.modelbin`**: vypíše verziu, počet blokov a šesť najčastejších
    značiek blokov. Obsah blokov sa tu nedekóduje.

Formáty s vlastnou magickou hodnotou (2 až 4) prichádzajú pred Unity a Frostbite,
pretože ich kontroly čítajú celý súbor: archív Forzy má desiatky gigabajtov.

Ak sa žiaden nezhoduje, vypíše `not a format this tool reads` a posledný dôvod.
Ten pochádza z kontroly ForzaTech.

Príklad (syntetický):

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

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<archive>` | povinné | Unreal `.pak`; IoStore `.utoc` (alebo `.ucas` vedľa neho); Source 2 `.vpk` (pri rozdelených VPK súbor `_dir.vpk`); ForzaTech `.minizip`; zip, ako archívy úrovní a obsahu BeamNG |
| `--filter TEXT` | žiadne | len cesty, ktoré obsahujú TEXT, bez ohľadu na veľkosť písmen |
| `--limit N` | 50 | vypíše najviac N položiek (celkový počet sa vždy vypíše) |
| `--key HEX` | žiadne | kľúč AES-256, ktorý už máte, 64 hexadecimálnych číslic, s `0x` alebo bez neho. Používa ho iba zašifrovaný `.pak`. Čokoľvek, čo nemá 64 hexadecimálnych číslic, sa odmietne skôr, ako sa archív otvorí (návratový kód 2) |

Nástroj určí formát podľa bajtov: obsah IoStore, `.minizip` a VPK podľa
podpisu, s ktorým začínajú, zip podľa jeho lokálnej hlavičky a `.pak` podľa
pätičky na konci. `.ucas` nemá hlavičku a otvára sa cez `.utoc` s rovnakým
menom. Súbor, ktorý nie je žiadnym z nich, sa odmietne hlásením
`<file> is not an archive list and extract read (...)`. Súbor, ktorý je
archívom, ale nedá sa otvoriť, sa odmietne s dôvodom čitateľa: zašifrovaný pak
bez `--key`, zašifrovaný kontajner IoStore, verzia paku, ktorú nečíta. V oboch
prípadoch je to jeden riadok a návratový kód 1.

Každý riadok ukazuje nekomprimovanú veľkosť, metódu kompresie a cestu:

| Archív | Metóda | Cesty |
|---|---|---|
| `.pak` | `none`, alebo názov z pätičky (`Zlib`, `Oodle`, `Gzip`...) | s mount bodom archívu, napríklad `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, alebo metóda kontajnera (`Oodle`, `Zlib`...), ako je uložený jeho prvý blok | s mount bodom, napríklad `../../../<Project>/Content/...`. Kontajner bez indexu adresára nepomenúva žiadne súbory a odmietne sa |
| `.vpk` | vždy `stored` | ako v adresári |
| `.minizip` | `lz4`, `deflate` alebo `stored` | ako ich zapisuje `ChunkContentsMiniZip<n>.txt` vedľa `GeoChunk<n>.minizip`, bez predpony stavacieho počítača (spätné lomky, ako ich hra zapisuje). Archív názvy neukladá, takže bez tohto súboru sú položky `#0`, `#1`... Ak sa počet riadkov zoznamu líši od počtu položiek, odmietne sa: nepatria k sebe |
| zip | `stored`, `deflate`, ... | ako je uložené; priečinky sa nevypisujú |

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

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<archive>` | povinné | ako pri `list` |
| `<entry>` | povinné | cesta presne tak, ako ju vypíše `list` (rozlišujú sa veľké a malé písmená); v `.minizip` funguje aj `#<číslo>` |
| `--out FILE` | názov súboru položky (za posledným `/` alebo `\`), v aktuálnom priečinku | kam zapísať; nadradené priečinky sa vytvoria |
| `--key HEX` | žiadne | ako pri `list` |

Položka sa dešifruje (pak, s kľúčom), dekomprimuje a zapíše. Vypíše
`<bytes> bytes -> <file>`. Ak cesta nie je v archíve, príkaz skončí s kódom 1.
Rovnako aj položka, ktorú sa nedá prečítať (zašifrovaná položka bez kľúča,
komprimovaná Oodle bez knižnice Oodle), s dôvodom na jednom riadku. Položka VPK sa
tu nekontroluje cez CRC. Na to má čitateľ metódu `verify()` (pozri
[Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<path>` | povinné | samostatný Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), nie zväzok |
| `--limit N` | 25 | dekódovať a vypísať najviac N sietí |

Vypíše počet objektov `Mesh` a potom jeden riadok na sieť: názov (prvých 40
znakov), počet vrcholov a trojuholníkov a `ok` alebo `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` znamená, že dekódované vrcholy nereprodukujú ohraničujúci
kváder, ktorý Unity uložilo pre sieť, v rámci 2 % veľkosti kvádra. Je to vlastná
kontrola čítania (pozri [Unity](reader-unity.md)). Sieť, ktorú sa nedá prečítať,
sa hlási s dôvodom a počíta sa do limitu. Dáta vrcholov v súbore `.resS` sa
čítajú z priečinka, v ktorom je kontajner.

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

Tento príkaz exportuje trať okolo kola: terén v pásme po oboch stranách jazdy a
to, čo na ňom stojí, ako jeden `.glb`. Zvyšok zistí sám: akú hru, ktorú
nainštalovanú kópiu, ktorú trať, úroveň alebo etapu a (pri Assetto Corsa Rally)
akým smerom sú osi otočené. Pozri [Export trate](course-export.md).

`<lap>` môže byť ktorýkoľvek z týchto (podrobnosti v [Vstupy kola](lap-inputs.md)):

- súbor kola: JSON trasy, JSON kola FH Companion, JSON `heat3d-lap`, `.npz` alebo `.csv` so stĺpcami x, y, z
- priečinok súborov kôl, hľadaný rekurzívne (celá zaznamenaná trať)
- **názov** trate, hľadaný v knižnici kôl FH Companion v `%LOCALAPPDATA%\FHCompanion\laps`

### Možnosti {#options}

| Možnosť | Predvolené | Hry | Význam |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` v aktuálnom priečinku | všetky | kam zapísať; názov sa prevedie na malé písmená a sekvencie iných znakov sa nahradia za `_` |
| `--game {forza,beamng,acrally}` | čo hovorí súbor kola, inak `forza` | všetky | z ktorej hry je kolo |
| `--margin M` | 80 | všetky | metrov zeme ponechaných po oboch stranách jazdy |
| `--texture-size {2048,1024,512}` | 2048 | všetky | pixely textúry zeme na 512 m dlaždicu (2048 = 25 cm na pixel) |
| `--no-textures` | vypnuté | všetky | len ploché farby: výrazne menší súbor. Pri Forze to tiež preskočí rozdelenie cesta/lem (pozri nižšie) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | mapy zeme a textúry modelov ktorého ročného obdobia |
| `--no-placed` | vypnuté | všetky | len terén: žiadne obruby, bariéry, značky, budovy. Pri BeamNG zostanú vodiace plochy modelované ako siete |
| `--trees` | vypnuté | všetky | umiestni aj vegetáciu (Forza: stromy, kry a rozbitné objekty; BeamNG: stromy; AC Rally: stromy a inštancovaná vegetácia) |
| `--detail-budget N` | automaticky | všetky | strop trojuholníkov pre všetko umiestnené; pozri [Úrovne detailu a rozpočet](detail-budget.md) |
| `--track DIR` | hľadá sa | Forza | priečinok trate (pod `media\Tracks`, s `GeoChunk0.minizip`), ak sa nemá hľadať v nainštalovanej hre |
| `--level NAME` | nájde sa z kola | BeamNG, AC Rally | úroveň (názov priečinka BeamNG) alebo etapa (názov mapy AC Rally), bez ohľadu na veľkosť písmen |
| `--install DIR` | hľadá sa v knižniciach Steamu | BeamNG, AC Rally | BeamNG: priečinok, v ktorom je `gameengine.zip`. AC Rally: priečinok hry alebo jeho `acr\Content\Paks` / `Content\Paks` |

Možnosti, ktoré sa na hru nevzťahujú, sa ticho ignorujú. Napríklad `--season`
pri BeamNG a AC Rally nič nerobí a `--track` pri nich tiež nič nerobí.

### Ktorá hra {#which-game}

Hra sa určí z `--game`, potom z poľa `game` súboru `heat3d-lap` (alebo z riadku
popisu `# {...}` v CSV), a ak ani to, tak sa predvolí Forza. Priečinok dostane
hru, ktorú pomenúvajú jeho súbory, ak pomenúvajú len jednu; súbor, ktorý žiadnu
nepomenúva (kolo FH Companion, `course.json`, CSV bez riadku popisu), sa
nepočíta (pozri [Vstupy kola](lap-inputs.md)).

| Hodnota | Export |
|---|---|
| začína na `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` alebo `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | odmietnuté: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | odmietnuté: "tracks ship in a protected format that is not a file-extraction target" |
| čokoľvek iné | odmietnuté: "there is no course reader for <game> yet" |

Odmietnutie tiež navrhuje alternatívy: zrekonštruovať trať z hrania (3DHeat
GameCapture), alebo analyzovať kolá bez trate, lebo karta Analýza pretekov v
prehliadači z nich kreslí cestu.

### Príklady {#examples}

```
# Trať z knižnice FH Companion, podľa názvu
python -m heat3d_gamefiles course "Example Circuit"

# Jeden súbor kola, užší pás, menší súbor
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Zimné textúry, so stromami
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Pevný strop 500 000 umiestnených trojuholníkov
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Priečinok trate zadaný priamo (hra nainštalovaná mimo Steamu)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: pomenujte úroveň, ukážte na inštaláciu
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, s jednoduchým CSV kolom, ktoré nehovorí svoju hru
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Príklad výstupu (Forza, syntetické čísla):

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

Každé auto nainštalovanej Forzy v nízkom detaile, ktorý hra sama používa, v
jednom súbore pre kartu Analýza pretekov v prehliadači: model `ProxyLOD`, ktorý nesie každý
archív auta v `media/Cars`, asi 900 trojuholníkov, s číslom auta podľa telemetrie,
jeho značkou, modelom a rokom z názvu archívu, a jeho kolesami a zadnými svetlami.
Trvá sekundy a zapíše asi 5 MB. Spustite znova, keď hra dostane nové autá. Archív
bez takéhoto modelu (dopravný rekvizit) sa pomenuje a vynechá. Formát je v
[`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Tvary sú v metroch, herné: 1:1 s autom. Súbor obsahuje obsah hry, preto je určený
pre počítač, na ktorom vznikol, a nie na posielanie ďalej.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Tento príkaz spustí export trate Forzy `course` na každom priečinku trate v
zaznamenanej knižnici kôl a zapíše jeden `<name>.glb` pre každý. Je len pre
Forzu. Volá priamo export Forzy a nečíta `--game`, `--level` ani `--install`.

| Možnosť | Predvolené | Význam |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | priečinok, do ktorého zapisovať (ak chýba, vytvorí sa) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | knižnica kôl |
| `--only TEXT [TEXT ...]` | všetky | len trate, ktorých názvy priečinkov obsahujú niektorý z týchto textov (bez ohľadu na veľkosť písmen) |
| `--force` | vypnuté | exportovať znova to, čo už má `.glb` |
| `--track DIR` | hľadá sa | ako pri `course` |
| `--margin M` | 80 | ako pri `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | ako pri `course` |

Čo sa počíta ako priečinok trate: priamy podpriečinok knižnice, ktorého názov
obsahuje ` (course_`, tak ako ich pomenúva FH Companion, napríklad
`Example Circuit (course_1200_3400_to_1175_3400)`. Časť od ` (course_` vyššie sa
z názvu vynechá.

Ako beží:

- Trať, ktorej `.glb` už existuje, sa preskočí (`kept`), pokiaľ nie je zadané `--force`, takže prerušený beh pokračuje tam, kde skončil.
- `.glb` zapísané staršou verziou, bez vlastnej vrstvy preteku a miest konania (jeho `asset.extras.course_format` chýba alebo je nižší ako aktuálny), sa exportuje znova, ako keby bolo zadané `--force` len pre ňu.
- Dva priečinky tratí s rovnakým názvom pred ` (course_` (nahrávač pomenoval novú trať podľa starej) si neprepisujú súbory: priečinok vytvorený ako prvý si ponechá `<name>.glb`, druhý sa zapíše ako `<name>_<start>.glb`, kde `<start>` je miesto začiatku, mínusy ako `m` (napríklad `example_circuit_m120_m340.glb`).
- Trať, ktorá zlyhá (nečitateľné kolá, málo pamäte, žiadny terén...), sa hlási ako `FAILED` a beh pokračuje.
- Na konci vypíše tabuľku stavu, veľkosti v MB, sekúnd a názvu, potom `<n> of <total> courses in <folder>`.
- Návratový kód je 1, ak zlyhala aspoň jedna trať.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Vypíše každé preteky, ktoré definuje nainštalovaná Forza, z ich definícií trás
(pozri [Trate Forza Horizon](course-forza-horizon.md#which-race)), a skontroluje
exporty v priečinku `courses` voči nim. Číta hru a knižnicu kôl; zapisuje len
voliteľnú tabuľku.

| Možnosť | Predvolené | Význam |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | priečinok, do ktorého zapisuje `courses` a ktorého súbory sa kontrolujú |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | knižnica kôl |
| `--track DIR` | hľadá sa | priečinok trate, ak nie je to z nainštalovanej hry |
| `--markdown FILE` | žiadne | zapísať tabuľku aj tam, ako Markdown |

Jeden riadok na preteky a jeden na každú zaznamenanú trať odjazdenú na nich:

| Stĺpec | Význam |
|---|---|
| route | id trasy |
| course | zaznamenaná trať k nej priradená, ak nejaká je |
| own assets | kópie, ktoré preteky pridávajú do voľnej jazdy sveta |
| drawn | z nich kópie, ktorých model dodáva trať |
| kinds | pridané kópie podľa druhu (bariéry, rekvizity, nálepky, infraštruktúra, ...) |
| not geometry | značky divákov a kolízne splajny, spočítané |
| hidden | objekty voľnej jazdy, ktoré preteky odstraňujú |
| venue | pozemné modely miest konania, ku ktorým sa AI línia pretekov priblíži do 10 m |
| export | `current`, `older format` (exportované znova cez `courses`), `not exported`, alebo prázdne pri pretekoch bez zaznamenanej trate |

Na konci je počet: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Toto je výrez Forzy, pri ktorom všetko zadávate ručne: dáte priečinok trate a
oblasť, nie kolo. Hodí sa, keď chcete oblasť ako obdĺžnik, nie ako jazdu.

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<path>` | povinné | priečinok trate Forzy pod `media\Tracks` (s `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | povinné | `.glb`, ktorý sa zapíše |
| `--box X0 Z0 X1 Z1` | | oblasť, v metroch hry (x a z, ako ich hlási telemetria); rohy v ľubovoľnom poradí |
| `--route FILE` | | JSON trasy s `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, ako ho zapisujú `heat3d_capture route` a `heat3d_capture laps`; číta sa ako UTF-8, s alebo bez značky poradia bajtov |
| `--margin M` | **100** | metrov pridaných okolo hraníc trasy, a šírka koridora, ak má trasa čiaru |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | ako pri `course` |

Zadajte presne jedno z `--box` a `--route`, inak je návratový kód 2. Pri
`--route` je výrez hranica trasy (`min`/`max`, x a z) rozšírená o okraj. Ak súbor
obsahuje aspoň 10 pozícií, výrez sa zúži na koridor o šírke `--margin` metrov
okolo nich a umiestnené modely dostanú detail podľa vzdialenosti od tejto čiary.
Pri `--box` sa zachová celý obdĺžnik a detail ide k tomu, čo stojí najbližšie
stredu obdĺžnika.

Výška sa do výrezu nikdy nepočíta. Obdĺžnik mimo mapy alebo na mori dá "no
terrain there" (návratový kód 1), nie chybu o súradniciach.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels a level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` vypíše úrovne, ktoré nainštalovaná hra Frostbite obsahuje, podľa názvu
ich tabuľky (`levels/<level>/<level>.toc`), s veľkosťou a odkiaľ pochádzajú:
`Data` pre základnú hru, `Update/<pack>` pre aktualizáciu, a koľko tabuliek s
vysokým rozlíšením k nej pridáva. Úroveň, ktorú prináša aktualizácia, má v základnej
hre aj malú tabuľku blokov; tabuľka s balíkmi úrovne je samotná úroveň (pozri
[Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` exportuje
jeden: výškové pole terénu, každú sieť, ktorú skupiny statických modelov úrovne
umiestňujú, objekty umiestnené jednotlivo, kde stoja, a pozadie terénu okolo mapy.
S `--textures` každý povrch nesie svoju farebnú mapu; s `--navmesh` sa pridajú
aj povrchy, po ktorých chodia vojaci. Ako sa to číta, je vo [Frostbite](reader-frostbite.md).

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<level>` | povinné | názov, ako ho vypíše `levels`, jeho jedinečná časť, alebo cesta k `.toc` úrovne |
| `-o`, `--out FILE` | `<level>.glb` | `.glb`, ktorý sa zapíše |
| `--install FOLDER` | prvá hra Steamu, ktorej `Data` obsahuje `layout.toc` | priečinok hry |
| `--textures [PIXELS]` | vypnuté; 512, ak je zadané bez veľkosti | zapísať farebnú mapu každého povrchu, najväčší mip nie väčší ako PIXELS na stranu, a jeho súradnice textúry tak, ako ich hra má, s opakujúcim sa vzorkovačom (pozri [Výstupný formát](output-format.md)). Výškové pole dostane farebnú mapu pozadia terénu, kde ju pokrýva, inak stredovú farbu materiálov povrchu terénu, inak priemernú farbu pozadia okolo. Bez toho má každá časť plochú farbu |
| `--ground-texture [METRES]` | vypnuté; 0.5, ak je zadané bez veľkosti | zapiecť dekaly terénu — cesty, ranveje, plochy, vyznačenia — do farby zeme, vynásobené farebnou mapou terénu tam, kde ju úroveň má, do farby výškového poľa, METRES na pixel, v dlaždiciach najviac 4 096 pixelov (`ground:terrain x<x> z<z>`). Funguje s `--textures` aj bez neho |
| `--navmesh` | vypnuté | pridať navigačnú sieť úrovne pre jeho najmenšieho agenta, vojaka (1,8 m vysoký, 0,4 m široký), ako časť `nav:walkable`: zem, podlahy, schody a strechy, na ktoré vojak dosiahne, bez spojov (skokov, rebríkov, prekážok) medzi nimi |
| `--ground-spacing METRES` | 4 | najjemnejší rozostup výškového poľa; uzly jemnejšie než toto sa prevzorkujú nadol. 0 nechá výškové pole von |
| `--detail-budget N` | každá kópia na najhrubšej úrovni, plus štvrtina, aspoň 1 500 000 | strop trojuholníkov. Siete, ktoré stoja najviac, stratia úroveň detailu naraz, kým sa to nezmestí; ak sa to nezmestí ani na najhrubších úrovniach, najmenšie kópie sa vynechajú ako prvé. Pozadie terénu sa nikdy nezhrubne ani nevynechá |
| `--skip TEXT` | | vynechať skupiny statických modelov, ktorých názov oddielu obsahuje TEXT; opakujte to pre viac. Napríklad vrstva herného režimu |
| `--by-mesh` | vypnuté | na hľadanie, čo časť je: jedna časť na zdrojovú sieť a materiál, pomenovaná `<part> \| <mesh> \| <material>`; oveľa väčší súbor |
| `--clamped-uvs` | vypnuté | pre renderer, ktorý nevie textúru opakovať: rozrezať každý texturovaný trojuholník na kusy, ktorých súradnice ležia v rozsahu 0..1, a trojuholník, ktorý by potreboval viac ako 4 kusy, nakresliť v priemernej farbe jeho textúry, v časti `<part> (average colour)` |

Vypíše skupiny a koľko kópií každá umiestnila, siete, ktoré vynechal, a prečo,
trojuholníky na časť (a pri `--textures` koľko textúr a koľko úsekov našlo svoju
farebnú mapu), čo je zem, a pri `--navmesh` koľko navigačných dlaždíc sa
prečítalo. O úrovni sa okrem geometrie nezapisuje nič: žiadne názvy, žiadne
metadáta (pozri [Výstupný formát](output-format.md)).

Rozpočet terénu je oddelený: výškové pole a pozadie sa `--detail-budget`
nikdy nezhrubnú; veľkosť výškového poľa určuje `--ground-spacing`.

Celá úroveň je veľká: typicky viac ako desať miliónov trojuholníkov a niekoľko
stoviek MB. `--textures` pridá k súboru trochu; úroveň plná stromov môže mať okolo
1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` privedie úroveň
na zhruba tretinu toho.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps a ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` je priečinok hry, jej `Content/Paks`, alebo názov jej priečinka v
knižnici Steamu (`"<Steam game folder name>"`). `ue-maps` vypíše každú mapu,
ktorá má vedľa seba skompilované bunky World Partition. `ue-map` exportuje jednu
ako `ground:<map>` (krajinu), `structure:<map>` (zlúčené siete HLOD mapy) a
`water:<map>` (jej vodné plochy tam, kde stoja nad zemou), v **centimetroch** Unreal
s prehodenými osami Y a Z - jediný export, ktorý nie je v metroch. Ako sa každá
číta a kontroluje: [Mapy Unreal 5](level-unreal-world-partition.md).

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<map>` | povinné | názov, ako ho vypíše `ue-maps`, alebo jedinečná časť názvu |
| `-o`, `--out FILE` | `<map>.glb` | `.glb`, ktorý sa zapíše |
| `--ground-spacing METRES` | 2 | rozostup vrcholov krajiny v súbore, zaokrúhlený na celé číslo vlastných štvorcov |
| `--no-structures`, `--no-water` | | túto časť vynechať |

Vypíše trojuholníky na časť, koľko komponentov krajiny sa prečítalo a koľko
vrcholov, ktoré ukladajú dvakrát, sa nezhoduje. Mapa 3 km pri 2 m má asi 4,6
milióna trojuholníkov zeme.

## enfusion-worlds a enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` vypíše každý svet s terénom podľa jeho priečinka pod
`worlds/`. `enfusion-world` exportuje jeden: `ground:<world>` (terén vo farbách
jeho supertextúrnych dlaždíc), `water:<world>` (more, na výške nula) a
`structure:<world>` (krabica každého umiestneného modelu), v metroch hry - x na
východ, y hore, z na sever. Ako sa každý číta a kontroluje:
[Svety Arma Reforger](level-arma-reforger.md).

| Možnosť | Predvolené | Význam |
|---|---|---|
| `<world>` | povinné | svet, ako ho vypíše `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb`, ktorý sa zapíše |
| `--install FOLDER` | knižnica Steamu, ktorá hru obsahuje | priečinok hry |
| `--ground-spacing METRES` | 2 (vlastná hodnota terénu) | rozostup vrcholov terénu v súbore |
| `--texture-size PIXELS` | 4096 | väčšia strana farebného obrazu zeme; 0 pre plochú farbu |
| `--no-structures` | | umiestnené modely vynechať |
| `--trees` | vypnuté | umiestniť aj stromy a inú vegetáciu, ako krabice |

Vypíše trojuholníky na časť, koľko okrajových vrcholov dlaždíc sa nezhoduje,
koľko entít obsahuje súbor sveta a koľko krabíc sa umiestnilo, a čo sa vynechalo
a prečo.

## Premenné prostredia {#environment-variables}

| Premenná | Účinok |
|---|---|
| `HEAT3D_OODLE` | cesta k `oo2core_*_win64.dll`, alebo priečinok, ktorý ho obsahuje; pozri [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | akákoľvek hodnota okrem prázdnej, `0`, `false`, `no` vypne kontrolu aktualizácií; pozri [Aktualizácie](updates.md) |
| `LOCALAPPDATA` | kde sa hľadajú knižnica FH Companion, používateľský priečinok BeamNG a vyrovnávacia pamäť aktualizácií |
| `HEAT3D_COURSE` | len pre testy: trať, ktorú používa test kraja s nainštalovanou hrou; pozri [Vývoj](development.md) |
