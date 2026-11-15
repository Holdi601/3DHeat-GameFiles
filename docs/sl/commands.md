---
title: Ukazi
nav_order: 2
lang: "sl"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Ukazi {#commands}

Vsak ukaz teče kot `python -m heat3d_gamefiles <glagol> ...` iz mape repozitorija.
Glagoli so razvrščeni v vrstnem redu, v katerem jih običajno potrebujete: kaj je ta
datoteka, kaj je v njej, izvlecite tisto, in pretvorite lap v tečaj.

| Glagol | Vzame | Naredi |
|---|---|---|
| [`identify`](#identify) | katerokoli datoteko | ugotovi vrsto vsebnika iz njenih bajtov |
| [`list`](#list) | Unreal `.pak` ali IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` ali zip | izpiše njene vnose |
| [`extract`](#extract) | isto | zapiše en vnos na disk |
| [`meshes`](#meshes) | Unity `SerializedFile` | izpiše in preveri njene mreže |
| [`course`](#course) | lap | izvozi tečaj okoli njega (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | knjižnico posnetih lapov | zažene `course` za vsak tečaj v njej (Forza) |
| [`races`](#races) | nameščeno Forzo | našteje vsako dirko, ki jo igra določa: kaj doda, kaj skrije, prizorišča, stanje njenega izvoza |
| [`terrain`](#terrain) | mapo steze Forza | odreže območje po koordinatah sveta |
| [`levels`](#levels-and-level-frostbite) | nameščeno igro Frostbite (Battlefield 6) | izpiše njene nivoje |
| [`level`](#levels-and-level-frostbite) | ime nivoja | izvozi nivo: teren, postavljene mreže, po želji njihove barvne zemljevide (Battlefield 6) |
| [`cars`](#cars) | nameščeno Forzo | vsak avto v nizki podrobnosti, v eni datoteki za zavihek dirke v pregledovalniku |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | igro Unreal 5 | izpiše njene zemljevide World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | ime zemljevida | izvozi zemljevid: teren, strukture HLOD, vodo |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | nameščen Arma Reforger | izpiše njegove svetove |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | ime sveta | izvozi svet: teren v njegovih barvah, morje, stavbe kot kvadre |

**Kako brati primere:** `<x>` pomeni, da zamenjate to z lastno vrednostjo, brez
kotnih oklepajev; `[...]` pomeni, da je izbirno; pot s presledki zapišite med
"dvojne narekovaje", na primer `"C:\Games\My Game"`. Ste novi v tem? Glejte
[Preden začnete](before-you-start.md). Celotno pomoč `--help` vsakega glagola najdete na
[Referenci ukazov](../cli-reference.md).

Ob vsakem zagonu programa lahko najprej preveri, ali je na voljo novejša izdaja. Glejte
[Posodobitve](updates.md). `HEAT3D_NO_UPDATE=1` to preverjanje izklopi.

Vir: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Strani po korakih: [Pregled arhivov](inspecting-archives.md), [Izvoz tečaja](course-export.md),
[Celi nivoji](whole-levels.md), [Avtomobili Forza](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Kode izhoda {#exit-codes}

| Koda | Pomen |
|---|---|
| 0 | uspeh |
| 1 | delo ni uspelo (neberljiv lap, igra ni najdena, ni ničesar za izvoz, tečaj v `courses` ni uspel; pri `list` in `extract`: datoteka, ki ni nobeden od arhivov, ki ju berejo, datoteka, ki je ni mogoče odpreti ali prebrati - šifriran pak brez `--key`, šifriran IoStore vsebnik - ali vnos, ki ni v arhivu) |
| 2 | napačni argumenti (argparse), pot, ki ne obstaja, `--key`, ki ni 64 šestnajstiških številk, ali `terrain`, ki je dobil oba ali nobenega od `--box` in `--route` |

Napake pri `list` in `extract` so vsaka ena vrstica na standardnem izhodu napak,
ne Pythonov sledenje.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Ta ukaz prebere datoteko in pove, kateri vsebnik je. Ne gleda na končnico (edina
izjema je `.ucas`, spodaj). Oblike preizkuša v tem vrstnem redu in se ustavi pri
prvi, ki se razčleni:

1. **Unreal `.pak`**: noga z oznako pak v zadnjih 1.024 bajtih. Izpiše različico,
   odmik in velikost kazala, ali je kazalo šifrirano, in načine stiskanja.
2. **Unreal IoStore `.utoc`**: oznaka IoStore na začetku. Izpiše različico,
   število kosov in ali je vsebnik šifriran; če ni, število datotek, ki jih imenik
   navaja (in pod katero točko montaže), načine stiskanja in ali je ob njem `.ucas`.
   `.ucas` nima lastne glave, zato ga prepozna `.utoc` z istim imenom ob njem, in
   `identify` navede to datoteko.
3. **ForzaTech `.minizip`**: oznaka `PGZP`. Izpiše različico, število vnosov in
   segmentov ter ali je ob njej `ChunkContentsMiniZip<n>.txt`, ki imenuje vnose
   (in če je, ali jih imenuje toliko, kot jih je).
4. **zip**: glava lokalne datoteke zip na začetku. Izpiše število vnosov, šest
   najpogostejših končnic in imena nivojev, kadar vnosi ležijo pod
   `levels/<name>/`, kot v arhivu nivoja BeamNG.drive.
5. **Unity**: paket `UnityFS` (izpiše različico motorja in število vnosov) ali
   samostojen `SerializedFile` (izpiše obliko, različico motorja, število objektov
   in šest najpogostejših razredov).
6. **Frostbite `.toc`**: izpiše vrsto (`plain` ali `signed`), kje se začne drevo, in
   bodisi število sredstev (binarni razdelek s tabelo) bodisi število
   superpaketov (drevo DbObject).
7. **Source 2 `.vpk`**: izpiše različico, število vnosov in prvo mrežo navigacije
   `.nav`, če jo arhiv ima.
8. **BeamNG `.cdae`**: oblika različice 31, ki se razčleni. Izpiše število mrež,
   število prikazanih stopenj podrobnosti in prve materiale.
9. **BeamNG `.ter`**: oznake nima, zato se mora vse sešteti - stran od 2 do 16.384,
   toliko višin in bajtov plasti na kvadrat, nato od 1 do 255 natisljivih imen
   plasti. Izpiše različico, velikost in imena plasti.
10. **ForzaTech `.modelbin`**: izpiše različico, število kosov in šest najpogostejših
    oznak kosov. Vsebina kosov tu ni dekodirana.

Oblike z lastno oznako (od 2 do 4) pridejo pred Unity in Frostbite, katerih preverjanji
prebereta celo datoteko: arhiv Forza je dolg več deset gigabajtov.

Če se nobena ne ujema, izpiše `not a format this tool reads` in zadnji razlog. Ta
razlog pride iz preverjanja ForzaTech.

Primer (izmišljen):

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

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<archive>` | obvezno | Unreal `.pak`; IoStore `.utoc` (ali `.ucas` ob njem); Source 2 `.vpk` (pri razcepljenih VPK `_dir.vpk`); ForzaTech `.minizip`; zip, na primer arhivi nivojev in vsebine BeamNG |
| `--filter TEXT` | brez | samo poti, ki vsebujejo TEXT, brez razlike med velikimi in malimi črkami |
| `--limit N` | 50 | izpiše največ N vnosov (skupno število se vedno izpiše) |
| `--key HEX` | brez | ključ AES-256, ki ga že imate, 64 šestnajstiških številk, z `0x` ali brez. Uporabite ga samo šifriran `.pak`. Vse, kar ni 64 šestnajstiških številk, je zavrnjeno, še preden se arhiv odpre (koda izhoda 2) |

Format orodje določi iz bajtov: tabelo vsebine IoStore, `.minizip` in VPK po podpisu,
s katerim se začnejo, zip po lokalni glavi datoteke, `.pak` pa po noge na koncu. `.ucas`
nima glave in se odpre prek `.utoc` z istim imenom. Datoteka, ki ni nobena od teh, je
zavrnjena z `<file> is not an archive list and extract read (...)`. Datoteka, ki je
ena od teh, pa se ne da odpreti, je zavrnjena z razlogom bralnika: šifriran pak brez
`--key`, šifriran IoStore vsebnik, različica pak, ki je ne bere. V obeh primerih je
to ena vrstica in koda izhoda 1.

Vsaka vrstica prikaže nestisnjeno velikost, način stiskanja in pot:

| Arhiv | Način | Poti |
|---|---|---|
| `.pak` | `none` ali ime iz noge (`Zlib`, `Oodle`, `Gzip` ...) | z mapo montaže arhiva, na primer `../../../Game/Content/...` |
| IoStore `.utoc` | `none` ali način vsebnika (`Oodle`, `Zlib` ...), kakor je shranjen njegov prvi blok | z mapo montaže, na primer `../../../<Project>/Content/...`. Vsebnik brez imenika datotek ne imenuje in je zavrnjen |
| `.vpk` | vedno `stored` | kakor v imeniku |
| `.minizip` | `lz4`, `deflate` ali `stored` | kakor jih zapisuje `ChunkContentsMiniZip<n>.txt` ob `GeoChunk<n>.minizip`, brez predpone gradnikovega stroja (z obratnimi poševnicami, kakor jih piše igra). Arhiv ne shranjuje imen, zato brez te datoteke vnosi dobijo `#0`, `#1` ... Seznam, katerega število vrstic se ne ujema z vnosi, je zavrnjen: ne sodita skupaj |
| zip | `stored`, `deflate` ... | kakor so shranjeni; mape se ne izpisujejo |

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

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<archive>` | obvezno | kot pri `list` |
| `<entry>` | obvezno | pot točno tako, kot jo izpiše `list` (razlikuje velike in male črke); v `.minizip` deluje tudi `#<number>` |
| `--out FILE` | ime vnosa (po zadnji `/` ali `\`), v trenutni mapi | kam zapisati; nadrejene mape se ustvarijo |
| `--key HEX` | brez | kot pri `list` |

Vnos se dešifrira (pak, s ključem), razširi in zapiše. Izpiše `<bytes> bytes -> <file>`.
Če pot ni v arhivu, ukaz konča s kodo 1. Enako velja za vnos, ki ga ni mogoče prebrati
(šifriran vnos brez ključa, stisnjen z Oodle brez knjižnice Oodle), z razlogom v
eni vrstici. Vnos VPK se tu ne preverja z njegovo CRC. Bralnik ima za to metodo
`verify()` (glejte [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<path>` | obvezno | samostojen Unity `SerializedFile` (`sharedassets0.assets`, `level0` ...), ne paket |
| `--limit N` | 25 | dekodira in izpiše največ N mrež |

Izpiše število objektov `Mesh`, nato po eno vrstico za vsako mrežo: ime (prvih 40
znakov), števila oglišč in trikotnikov ter `ok` ali `BOUNDS DISAGREE`. `BOUNDS DISAGREE`
pomeni, da dekodirana oglišča ne ustrezajo omejevalnemu okvirju, ki ga je Unity shranil
za mrežo, znotraj 2 % velikosti okvirja. To je lastno preverjanje razčlenjevanja (glejte
[Unity](reader-unity.md)). Mreža, ki je ni mogoče prebrati, je prijavljena z razlogom
in šteje v omejitev. Podatki oglišč v datoteki `.resS` se berejo iz mape, v kateri
je vsebnik.

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

To izvozi tečaj okoli lapa: teren v pasu z obeh strani vožnje in to, kar stoji na
njem, kot eno datoteko `.glb`. Ostalo ugotovi samo: katera igra, katera nameščena kopija,
katera steza, nivo ali etapa in (za Assetto Corsa Rally) na kateri način so osi
obrnjene. Glejte [Izvoz tečaja](course-export.md).

`<lap>` je lahko kateri koli od naslednjih (podrobnosti v [Vhodih lapa](lap-inputs.md)):

- datoteka lapa: JSON poti, JSON lapa FH Companion, JSON `heat3d-lap`, `.npz` ali `.csv` s stolpci x, y, z
- mapa datotek lapov, iskana rekurzivno (celoten posnet tečaj)
- **ime** tečaja, poiskano v knjižnici FH Companion na `%LOCALAPPDATA%\FHCompanion\laps`

### Možnosti {#options}

| Možnost | Privzeto | Igre | Pomen |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` v trenutni mapi | vse | kam zapisati; ime se pretvori v male črke, zaporedja drugih znakov pa v `_` |
| `--game {forza,beamng,acrally}` | kar pove datoteka lapa, sicer `forza` | vse | iz katere igre je lap |
| `--margin M` | 80 | vse | metri tal, ohranjenih z vsake strani vožnje |
| `--texture-size {2048,1024,512}` | 2048 | vse | slikovne pike teksture tal na ploščico 512 m (2048 = 25 cm na piko) |
| `--no-textures` | izklopljeno | vse | samo ploske barve: bistveno manjša datoteka. Pri Forzi to izpusti tudi delitev ceste/brežine (glejte spodaj) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | zemljevidi tal in teksture modelov za katero sezono |
| `--no-placed` | izklopljeno | vse | samo teren: brez robnikov, ograj, znakov, stavb. Pri BeamNG ostanejo vozne površine, modelirane kot mreže |
| `--trees` | izklopljeno | vse | doda tudi rastlinje (Forza: drevesa, grmovje in razbijalne predmete; BeamNG: drevesa; AC Rally: drevesa in instancirano podrastje) |
| `--detail-budget N` | samodejno | vse | zgornja meja trikotnikov za vse postavljeno; glejte [Stopnje podrobnosti in proračun](detail-budget.md) |
| `--track DIR` | išče se | Forza | mapa steze (pod `media\Tracks`, ki vsebuje `GeoChunk0.minizip`), če ni treba iskati nameščene igre |
| `--level NAME` | najdeno iz lapa | BeamNG, AC Rally | nivo (ime mape BeamNG) ali etapa (ime zemljevida AC Rally), brez razlikovanja velikih in malih črk |
| `--install DIR` | išče se v knjižnicah Steam | BeamNG, AC Rally | BeamNG: mapa, ki vsebuje `gameengine.zip`. AC Rally: mapa igre ali njena `acr\Content\Paks` / `Content\Paks` |

Možnosti, ki se ne nanašajo na igro, se tiho prezrejo. Na primer,
`--season` za BeamNG in AC Rally ne naredi ničesar, prav tako `--track` zanju ne.

### Katera igra {#which-game}

Igra se vzame iz `--game`, nato iz polja `game` datoteke `heat3d-lap` (ali iz vrstice
opisa `# {...}` v CSV) in privzeto je Forza. Mapa dobi igro, ki jo imenujejo njene
datoteke, če imenujejo samo eno; datoteka, ki ne imenuje nobene (lap FH Companion,
`course.json`, CSV brez vrstice opisa), se ne šteje (glejte [Vhodi lapa](lap-inputs.md)).

| Vrednost | Izvoz |
|---|---|
| se začne z `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ali `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | zavrnjeno: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | zavrnjeno: "tracks ship in a protected format that is not a file-extraction target" |
| karkoli drugega | zavrnjeno: "there is no course reader for <game> yet" |

Zavrnitev tudi predlaga alternative: rekonstruirati tečaj iz igranja (3DHeat
GameCapture) ali analizirati lape brez tečaja, ker zavihek Analiza dirke v pregledovalniku
iz njih nariše cesto.

### Primeri {#examples}

```
# Tečaj iz knjižnice FH Companion, po imenu
python -m heat3d_gamefiles course "Example Circuit"

# Ena datoteka lapa, ožji pas, manjša datoteka
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Zimske teksture, z drevesi
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Trda meja 500.000 postavljenih trikotnikov
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Mapa steze, podana neposredno (igra nameščena zunaj Steama)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: imenujte nivo, pokažite namestitev
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, z navadnim CSV lapom, ki ne pove svoje igre
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Primer izpisa (Forza, izmišljene številke):

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

Vsak avto nameščene Forze v privzeti nizki podrobnosti igre, v eni datoteki za
zavihek dirke v pregledovalniku: model `ProxyLOD`, ki ga ima vsak arhiv avtomobila v
`media/Cars`, okoli 900 trikotnikov, s številko avtomobila, kakor jo navaja telemetrija,
njegovo znamko, oznako modela in letnico iz imena arhiva ter njegova kolesa in zadnje
luči. Traja nekaj sekund in zapiše okoli 5 MB. Ponovno zaženite, kadar igra dobi nove
avtomobile. Arhiv brez takega modela (rekvizit prometa) je imenovan in izpuščen. Oblika
je v [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Oblike so v metrih, igrine lastne: 1:1 z avtomobilom. Datoteka vsebuje vsebino
igre, zato je namenjena stroju, na katerem je nastala, ne za deljenje.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

To zažene izvoz tečaja Forza `course` na vsaki mapi tečaja v knjižnici posnetih lapov
in zapiše po eno `<name>.glb` za vsakega. Samo za Forzo. Kliče izvoz Forze neposredno
in ne bere `--game`, `--level` ali `--install`.

| Možnost | Privzeto | Pomen |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | mapa, v katero se zapisuje (ustvari se, če manjka) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | knjižnica lapov |
| `--only TEXT [TEXT ...]` | vsi | samo tečaji, katerih imena map vsebujejo enega od teh (brez razlikovanja velikih in malih črk) |
| `--force` | izklopljeno | izvozi znova, kar že ima `.glb` |
| `--track DIR` | išče se | kakor pri `course` |
| `--margin M` | 80 | kakor pri `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kakor pri `course` |

Kaj šteje za mapo tečaja: neposredna podmapa knjižnice, katere ime vsebuje ` (course_`,
kar tako poimenuje FH Companion, na primer
`Example Circuit (course_1200_3400_to_1175_3400)`. Del od ` (course_` naprej se pri imenu
izpusti.

Kako teče zagon:

- Tečaj, katerega `.glb` že obstaja, se preskoči (`kept`), razen če je dan `--force`, zato
  prekinjen zagon nadaljuje tam, kjer je ostal.
- `.glb`, ki ga je zapisala starejša različica, brez lastnega sloja dirke in prizorišč
  (njegov `asset.extras.course_format` manjka ali je nižji od trenutnega), se izvozi
  znova, kot da bi bil za ta primer dan `--force`.
- Dve mapi tečajev z istim imenom pred ` (course_` (snemalnik, ki je nov tečaj poimenoval
  po starem) se ne prepisujeta: mapa, ustvarjena prva, obdrži `<name>.glb`, druga se
  zapiše kot `<name>_<start>.glb`, kjer je `<start>` mesto začetka, minusi pa so `m`
  (na primer `example_circuit_m120_m340.glb`).
- Tečaj, ki ne uspe (neberljivi laps, zmanjkalo pomnilnika, ni terena ...), je prijavljen
  kot `FAILED`, zagon pa se nadaljuje.
- Na koncu izpiše tabelo stanja, velikosti v MB, sekund in imena, nato
  `<n> of <total> courses in <folder>`.
- Koda izhoda je 1, če je kateri koli tečaj spodletel.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Našteje vsako dirko, ki jo definira nameščena Forza, iz njenih opisov poti (glejte
[Tečaji Forza Horizon](course-forza-horizon.md#which-race)), in preveri izvoze v mapi
`courses` glede nanje. Bere igro in knjižnico lapov; zapiše samo neobvezno tabelo.

| Možnost | Privzeto | Pomen |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | mapa, v katero piše `courses` in katere datoteke se preverjajo |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | knjižnica lapov |
| `--track DIR` | išče se | mapa steze, če ni steza nameščene igre |
| `--markdown FILE` | brez | tabelo zapiše tudi tja, kot Markdown |

Ena vrstica za vsako dirko in ena za vsak posneti tečaj, na katerem je bila vožnja:

| Stolpec | Pomen |
|---|---|
| route | številka poti |
| course | posneti tečaj, ujet z njo, če obstaja |
| own assets | kopije, ki jih dirka doda svetu proste vožnje |
| drawn | od teh kopije, katerih model ima steza |
| kinds | dodane kopije po vrstah (ovire, rekviziti, nalepke, infrastruktura ...) |
| not geometry | markerji pregledovalnikov in kolizijski splajni, prešteti |
| hidden | predmeti svetu proste vožnje, ki jih dirka odstrani |
| venue | modeli tal prizorišč, ob katerih AI linija dirke gre na 10 m |
| export | `current`, `older format` (izvozi znova `courses`), `not exported` ali prazno za dirko brez posnetega tečaja |

Na koncu je štetje: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

To je rez Forze z vsem določenim ročno: podate mapo steze in območje, ne lapa. Uporabno,
kadar je želeno območje škatla, ne vožnja.

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<path>` | obvezno | mapa steze Forze pod `media\Tracks` (z `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | obvezno | `.glb`, ki se zapiše |
| `--box X0 Z0 X1 Z1` | | območje v metrih igre (x in z, kakor jih javlja telemetrija); vogali v poljubnem vrstnem redu |
| `--route FILE` | | JSON poti z `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, kakor ga zapišeta `heat3d_capture route` in `heat3d_capture laps`; prebran kot UTF-8, z ali brez oznake bajtnega reda |
| `--margin M` | **100** | metri, dodani okoli meja poti, in širina koridorja, kadar ima pot črto |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kakor pri `course` |

Podajte natanko eno od `--box` in `--route`, sicer je koda izhoda 2. Z `--route` je
rez `bounds` poti (`min`/`max`, x in z), razširjen za pas. Če datoteka vsebuje vsaj 10
položajev, se rez zoži na koridor širine `--margin` metrov okoli njih, postavljeni modeli
pa dobijo podrobnost glede na razdaljo do te črte. Z `--box` se ohrani celotna
škatla, podrobnost pa dobi to, kar stoji najbliže središču škatle.

Višina rezu nikoli ni del reza. Škatla zunaj zemljevida ali v morju da "no terrain there"
(koda izhoda 1), ne napake o koordinatah.

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

`levels` izpiše nivoje, ki jih ima nameščena igra Frostbite, po imenu njihove tabele
(`levels/<level>/<level>.toc`), z velikostjo in od kod prihajajo: `Data` za osnovno igro,
`Update/<pack>` za posodobitev, in koliko tabel visoke ločljivosti jim doda. Nivo, ki ga
dodaja posodobitev, ima majhno tabelo kosov, ki je prav tako samo v osnovni igri; tabela
s paketi nivoja je nivo (glejte [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` izvozi enega: terenski višinski model, vsako mrežo, ki jo skupine statičnih
modelov nivoja postavijo, predmete, postavljene posamično, kje stojijo, in teren
nivoja okoli zemljevida. Z `--textures` ima vsaka površina svoj barvni zemljevid; z
`--navmesh` pridejo tudi površine, po katerih hodijo vojaki. Kako se bere, je v
[Frostbite](reader-frostbite.md).

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<level>` | obvezno | ime, kakor ga izpiše `levels`, edinstven del imena ali pot do `.toc` nivoja |
| `-o`, `--out FILE` | `<level>.glb` | `.glb`, ki se zapiše |
| `--install FOLDER` | prva igra Steam, katere `Data` vsebuje `layout.toc` | mapa igre |
| `--textures [PIXELS]` | izklopljeno; 512, če je dano brez velikosti | zapiše barvni zemljevid vsake površine, največji mip, ki ni večji od PIXELS na stran, in njene koordinate tekstur, kakor jih ima igra, s ponavljajočim vzorčevalnikom (glejte [Oblika izhoda](output-format.md)). Višinski model dobi barvni zemljevid ozadja terena, kjer ga ta pokriva, sicer srednjo barvo površinskih materialov terena, sicer povprečno barvo ozadja okoli. Brez tega je vsak del ploska barva |
| `--ground-texture [METRES]` | izklopljeno; 0,5, če je dano brez velikosti | zapeče dekale terena - ceste, vzletne steze, ploščadi, barvne oznake - čez barvo tal, pomnožene z barvnim zemljevidom terena, kjer ga nivo ima, v barvo višinskega modela, METRES na piko, v ploščice največ 4.096 pik (`ground:terrain x<x> z<z>`). Deluje z `--textures` in brez njega |
| `--navmesh` | izklopljeno | doda navigacijsko mrežo nivoja za njegovega najmanjšega agenta, vojaka (1,8 m visok, 0,4 m širok), kot del `nav:walkable`: tla, tla etaž, stopnice in strehe, na katere lahko vojak pride, brez povezav (skokov, lestev, preskokov) med njimi |
| `--ground-spacing METRES` | 4 | najfinejši razmik višinskega modela; bolj fina vozlišča so vzorčena redčeje. 0 izpusti višinski model |
| `--detail-budget N` | vsaka kopija na najgrobejši stopnji, plus četrtina, vsaj 1.500.000 | zgornja meja trikotnikov. Mreže, ki stanejo največ, izgubijo eno stopnjo podrobnosti naenkrat, dokler se ne prilegajo; če tudi najgrobejše stopnje ne, se najprej izpustijo najmanjše kopije. Podlaga terena nikoli ni zgrubljena ali izpuščena |
| `--skip TEXT` | | izpusti skupine statičnih modelov, katerih ime particije vsebuje TEXT; ponovite za več. Na primer sloj določenega načina igre |
| `--by-mesh` | izklopljeno | za iskanje, kaj je del: en del na izvorno mrežo in material, imenovan `<part> \| <mesh> \| <material>`; veliko večja datoteka |
| `--clamped-uvs` | izklopljeno | za upodabljalnik, ki ne more ponoviti teksture: vsak teksturiran trikotnik razreže na kose, katerih koordinate ležijo v 0..1, trikotnik, ki bi potreboval več kot 4 kose, pa nariše v povprečni barvi njegove teksture, v delu `<part> (average colour)` |

Izpiše skupine in koliko kopij je vsaka postavila, mreže, ki jih je izpustil, in zakaj,
trikotnike na del (in z `--textures` koliko tekstur ter koliko odsekov je našlo svoj
barvni zemljevid), kaj je teren, in z `--navmesh` koliko navigacijskih ploščic je bilo
prebranih. O nivoju se razen geometrije ne zapiše nič: ne imena, ne metapodatki (glejte
[Oblika izhoda](output-format.md)).

Proračun terena je ločen: višinski model in podlaga se nikoli ne zgrubita z
`--detail-budget`; `--ground-spacing` določa višinski model.

Celoten nivo je velik: običajno več kot deset milijonov trikotnikov in več sto MB.
`--textures` doda malo k datoteki; nivo, poln dreves, lahko doseže okoli 1 GB.
`--textures 256 --detail-budget 3000000 --ground-spacing 8` spravi nivo na približno
tretjino tega.

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

`<game>` je mapa igre, njena `Content/Paks` ali ime njene mape v knjižnici Steam
(`"<Steam game folder name>"`). `ue-maps` izpiše vsak zemljevid, ki ima ob sebi
zapisane celice World Partition. `ue-map` izvozi enega kot `ground:<map>` (pokrajina),
`structure:<map>` (združene mreže HLOD zemljevida) in `water:<map>` (njegova vodna
telesa, kjer stojijo nad tlemi), v **centimetrih** Unreal, z zamenjanima Y in Z - edini
izvoz, ki ni v metrih. Kako se vsak bere in preverja: [Zemljevidi Unreal 5](level-unreal-world-partition.md).

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<map>` | obvezno | ime, kakor ga izpiše `ue-maps`, ali edinstven del imena |
| `-o`, `--out FILE` | `<map>.glb` | `.glb`, ki se zapiše |
| `--ground-spacing METRES` | 2 | razmik oglišč pokrajine v datoteki, zaokrožen na celo število njenih lastnih ploskev |
| `--no-structures`, `--no-water` | | ta del izpusti |

Izpiše trikotnike na del, koliko komponent pokrajine je bilo prebranih in koliko
oglišč, ki jih shranjujejo dvakrat, se ne ujema. Zemljevid 3 km pri 2 m je približno
4,6 milijona trikotnikov tal.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` izpiše vsak svet s terenom, po njegovi mapi pod `worlds/`.
`enfusion-world` izvozi enega: `ground:<world>` (teren, v barvah njegovih nadteksturnih
ploščic), `water:<world>` (morje, na višini nič) in `structure:<world>` (škatla vsakega
postavljenega modela), v lastnih metrih igre - x proti vzhodu, y navzgor, z proti severu.
Kako se bere in preverja: [Svetovi Arma Reforger](level-arma-reforger.md).

| Možnost | Privzeto | Pomen |
|---|---|---|
| `<world>` | obvezno | svet, kakor ga izpiše `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb`, ki se zapiše |
| `--install FOLDER` | knjižnica Steam, ki vsebuje igro | mapa igre |
| `--ground-spacing METRES` | 2 (terenov lasten) | razmik oglišč terena v datoteki |
| `--texture-size PIXELS` | 4096 | daljša stran slike barv tal; 0 za ploske barve |
| `--no-structures` | | postavljenih modelov ne vključi |
| `--trees` | izklopljeno | postavi tudi drevesa in drugo rastlinje, kot škatle |

Izpiše trikotnike na del, koliko oglišč ob robu ploščic se ne ujema, koliko entitet
ima svetovna datoteka in koliko škatel je bilo postavljenih, ter kaj je bilo izpuščeno
in zakaj.

## Environment variables {#environment-variables}

| Spremenljivka | Učinek |
|---|---|
| `HEAT3D_OODLE` | pot do `oo2core_*_win64.dll` ali mape, ki jo vsebuje; glejte [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | vsaka vrednost razen prazne, `0`, `false`, `no` izklopi preverjanje posodobitev; glejte [Posodobitve](updates.md) |
| `LOCALAPPDATA` | kje se iščejo knjižnica FH Companion, uporabniška mapa BeamNG in predpomnilnik posodobitev |
| `HEAT3D_COURSE` | samo za teste: tečaj, ki ga uporablja test robnikov na nameščeni igri; glejte [Razvoj](development.md) |
