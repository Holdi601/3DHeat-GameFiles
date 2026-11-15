---
title: Parancsok
nav_order: 2
lang: "hu"
source: commands.md
source_hash: "db876ce4e110"
nav_exclude: true
search_exclude: true
---
# Parancsok {#commands}

Minden parancs a `python -m heat3d_gamefiles <parancs> ...` alakban fut a tároló
mappájából. A parancsok abban a sorrendben követik egymást, ahogy általában
szükséged van rájuk: mi ez a fájl, mi van benne, add ide azt, és alakíts egy kört
pályává.

| Parancs | Bemenet | Mit csinál |
|---|---|---|
| [`identify`](#identify) | bármilyen fájl | a bájtjai alapján megnevezi a tárolóformátumot |
| [`list`](#list) | Unreal `.pak` vagy IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` vagy zip | kilistázza a bejegyzéseit |
| [`extract`](#extract) | ugyanaz | kiír egy bejegyzést a lemezre |
| [`meshes`](#meshes) | Unity `SerializedFile` | listázza és ellenőrzi a meshjeit |
| [`course`](#course) | egy kör | exportálja a körülötte lévő pályát (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | egy rögzített körkönyvtár | lefuttatja a `course`-t a benne lévő minden pályán (Forza) |
| [`races`](#races) | egy telepített Forza | kilistázza a játékban definiált összes versenyt: mit ad hozzá, mit rejt el, a helyszíneket, és az exportjuk állapotát |
| [`terrain`](#terrain) | egy Forza pályamappa | kivág egy területet világkoordináták szerint |
| [`levels`](#levels-and-level-frostbite) | egy telepített Frostbite-játék (Battlefield 6) | kilistázza a pályáit |
| [`level`](#levels-and-level-frostbite) | egy pálya neve | exportálja a pályát: terep, elhelyezett meshek, opcionálisan azok színtérképei (Battlefield 6) |
| [`cars`](#cars) | egy telepített Forza | minden autó alacsony részletességgel, egyetlen fájlban a megjelenítő versenyfülének |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | egy Unreal 5 játék | kilistázza a World Partition térképeit |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | egy térkép neve | exportálja a térképet: tájkép, HLOD-szerkezetek, víz |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | egy telepített Arma Reforger | kilistázza a világait |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | egy világ neve | exportálja a világot: a terepet a saját színeiben, a tengert, az épületeket dobozokként |

**A példák olvasása:** a `<x>` azt jelenti, hogy a saját értékeddel kell
helyettesíteni, a szögletes zárójelek nélkül; a `[...]` opcionális; a szóközt
tartalmazó elérési utat "dupla idézőjelbe" tedd, például `"C:\Games\My Game"`.
Ez újdonság neked? Lásd: [Mielőtt elkezdenéd](before-you-start.md). Minden
parancs teljes `--help` szövege a [Parancsreferencia](../cli-reference.md) oldalon
van.

A program minden indításkor ellenőrizheti, hogy van-e újabb kiadás. Lásd:
[Frissítések](updates.md). A `HEAT3D_NO_UPDATE=1` kikapcsolja ezt az ellenőrzést.

Forrás: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Lépésről lépésre leírt oldalak: [Archívumok vizsgálata](inspecting-archives.md), [Pályaexportálás](course-export.md),
[Teljes pályák](whole-levels.md), [Forza autók](forza-cars.md).

![A `python -m heat3d_gamefiles --help` kimenete](../assets/img/help.svg)

## Kilépési kódok {#exit-codes}

| Kód | Jelentés |
|---|---|
| 0 | sikeres |
| 1 | a munka sikertelen volt (olvashatatlan kör, nincs játék találva, nincs mit exportálni, a `courses` egyik pályája sikertelen; a `list` és az `extract` esetén olyan fájl, ami egyik olvasott archívum sem, vagy amit nem lehet megnyitni vagy beolvasni - titkosított pak `--key` nélkül, titkosított IoStore-tároló - vagy a bejegyzés nincs az archívumban) |
| 2 | hibás argumentumok (argparse), olyan elérési út, ami nem létezik, `--key`, ami nem 64 hexadecimális számjegy, vagy a `terrain` a `--box` és a `--route` közül egyiket sem vagy mindkettőt kapta |

A `list` és az `extract` hibái mindegyike egy sor a szabványos hibakimenetre,
nem Python-hibakövetés.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Ez beolvassa a fájlt, és megmondja, milyen tároló. Nem a kiterjesztés alapján
dönt (az egyetlen kivétel a `.ucas`, lent). A formátumokat ebben a sorrendben
próbálja ki, és az első, amelyik sikeresen értelmezhető, megáll:

1. **Unreal `.pak`**: a végén, az utolsó 1024 bájtban pak-azonosító. Kiírja a
   verziót, az indexe kezdő helyét és méretét, hogy titkosított-e az index, és a
   tömörítési módokat.
2. **Unreal IoStore `.utoc`**: az elején IoStore-azonosító. Kiírja a verziót, a
   darabok számát, és hogy titkosított-e a tároló; ha nem, a könyvtárában
   nevezett fájlok számát (és alatta a csatlakozási pontot), a tömörítési
   módokat, és hogy mellette van-e a `.ucas`. A `.ucas`-nak nincs saját
   fejléce, ezért az azonos nevű, mellette lévő `.utoc` alapján ismeri fel, és az
   `identify` azt a fájlt nevezi meg.
3. **ForzaTech `.minizip`**: a `PGZP` azonosító. Kiírja a verziót, a bejegyzések
   és szegmensek számát, és hogy mellette van-e a `ChunkContentsMiniZip<n>.txt`,
   ami a bejegyzéseket nevezi meg (és ha igen, hogy annyit nevez-e meg, ahány
   bejegyzés van).
4. **zip**: zip helyi fájlfejléc az elején. Kiírja a bejegyzések számát, a hat
   leggyakoribb kiterjesztést, és a pályaneveket, ha a bejegyzések
   `levels/<name>/` alatt vannak, mint a BeamNG.drive pályaarchívumában.
5. **Unity**: `UnityFS` köteg (kiírja a motor verzióját és a bejegyzések számát)
   vagy önálló `SerializedFile` (kiírja a formátumot, a motor verzióját, az
   objektumok számát és a hat leggyakoribb osztályt).
6. **Frostbite `.toc`**: kiírja a típust (`plain` vagy `signed`), hogy hol
   kezdődik a fa, és vagy az eszközök számát (bináris szakasztáblázat), vagy a
   superbundle-ök számát (DbObject-fa).
7. **Source 2 `.vpk`**: kiírja a verziót, a bejegyzések számát, és az első `.nav`
   navigációs hálót, ha az archívumban van.
8. **BeamNG `.cdae`**: 31-es alakverzió, ami sikeresen értelmezhető. Kiírja a
   meshek számát, a rajzolt részletességi szintek számát és az első anyagokat.
9. **BeamNG `.ter`**: nincs azonosítója, ezért mindennek össze kell állnia - 2 és
   16 384 közötti oldalhossz, annyi négyzetre magasságok és rétegbájtok, majd 1
   és 255 közötti nyomtatható rétegnév. Kiírja a verziót, a méretet és a
   rétegneveket.
10. **ForzaTech `.modelbin`**: kiírja a verziót, a darabok számát és a hat
    leggyakoribb darabcímkét. A darabok tartalmát itt nem dekódolja.

A saját azonosítóval rendelkező formátumok (2-4) a Unity- és Frostbite-ellenőrzés
előtt jönnek, mert azok a teljes fájlt beolvassák: egy Forza-archívum tíz
gigabájtos is lehet.

Ha egyik sem illeszkedik, a program kiírja: `not a format this tool reads`, és
az utolsó okot. Ez az ok a ForzaTech-ellenőrzésből származik.

Példa (kitalált adatokkal):

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

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<archive>` | kötelező | Unreal `.pak`; IoStore `.utoc` (vagy a mellette lévő `.ucas`); Source 2 `.vpk` (osztott VPK-nál a `_dir.vpk`); ForzaTech `.minizip`; zip, például a BeamNG pálya- és tartalomarchívumai |
| `--filter TEXT` | nincs | csak a TEXT-et tartalmazó elérési utak, kis- és nagybetűtől függetlenül |
| `--limit N` | 50 | legfeljebb N bejegyzés kiírása (az össz-szám mindig kiíródik) |
| `--key HEX` | nincs | egy AES-256 kulcs, amivel már rendelkezel, 64 hexadecimális számjegy, `0x`-szel vagy anélkül. Csak titkosított `.pak` használja. Ami nem 64 hexadecimális számjegy, azt az archívum megnyitása előtt elutasítja (2-es kilépési kód) |

A program a bájtok alapján dönt a formátumról: az IoStore-tartalomjegyzéket, a
`.minizip`-et és a VPK-t a kezdő azonosítójuk alapján, a zip-et a helyi
fájlfejléce alapján, a `.pak`-ot a végén lévő lábléc alapján ismeri fel. A `.ucas`-nak
nincs fejléce, ezért az azonos nevű `.utoc`-on keresztül nyitja meg. Az olyan
fájlt, ami egyik sem, ezzel az üzenettel utasítja el: `<file> is not an archive
list and extract read (...)`. Ami ilyen, de nem nyitható meg, azt a olvasó
okával utasítja el: titkosított pak `--key` nélkül, titkosított IoStore-tároló,
vagy olyan pak-verzió, amit nem olvas. Mindkét esetben egy sor és 1-es
kilépési kód.

Minden sor kiírja a kicsomagolt méretet, a tömörítési módot és az elérési utat:

| Archívum | Mód | Elérési utak |
|---|---|---|
| `.pak` | `none`, vagy a lábléc neve (`Zlib`, `Oodle`, `Gzip`...) | az archívum csatlakozási pontjával, például `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, vagy a tároló módja (`Oodle`, `Zlib`...), az első blokkja szerint tárolva | a csatlakozási ponttal, például `../../../<Project>/Content/...`. A könyvtárindex nélküli tároló nem nevez meg fájlokat, és elutasításra kerül |
| `.vpk` | mindig `stored` | ahogy a könyvtárban áll |
| `.minizip` | `lz4`, `deflate` vagy `stored` | ahogy a `GeoChunk<n>.minizip` melletti `ChunkContentsMiniZip<n>.txt` írja, a fordítógép előtagjával együtt eltávolítva (visszaperjelekkel, ahogy a játék írja). Az archívum nem tárol neveket, így e fájl nélkül a bejegyzések `#0`, `#1`... lesznek. Az a lista, amelynek sorainak száma nem egyezik a bejegyzésekkel, elutasításra kerül: a kettő nem tartozik össze |
| zip | `stored`, `deflate`, ... | ahogy tárolva van; a mappák nincsenek listázva |

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

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<archive>` | kötelező | mint a `list`-nél |
| `<entry>` | kötelező | az elérési út pontosan úgy, ahogy a `list` kiírja (kis- és nagybetűre érzékeny); `.minizip`-ben a `#<szám>` is működik |
| `--out FILE` | a bejegyzés fájlneve (az utolsó `/` vagy `\` után), az aktuális mappában | hova írjon; a szülőmappákat létrehozza |
| `--key HEX` | nincs | mint a `list`-nél |

A bejegyzés visszafejtésre kerül (pak esetén kulccsal), kicsomagolódik, és kiíródik.
Kiírja: `<bytes> bytes -> <file>`. Ha az elérési út nincs az archívumban, a
parancs 1-es kilépési kóddal fejeződik be. Ugyanígy jár, ha a bejegyzés nem
olvasható (titkosított bejegyzés kulcs nélkül, Oodle-tömörítés Oodle-könyvtár
nélkül), az okot egy sorban kiírja. A VPK-bejegyzés CRC-jét itt nem ellenőrzi. Erre
az olvasónak van `verify()` metódusa (lásd: [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<path>` | kötelező | egy önálló Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), nem köteg |
| `--limit N` | 25 | legfeljebb N mesh dekódolása és kiírása |

Kiírja a `Mesh` objektumok számát, majd soronként egy meshet: a nevét (első 40
karakter), a csúcsok és háromszögek számát, és `ok` vagy `BOUNDS DISAGREE`.
A `BOUNDS DISAGREE` azt jelenti, hogy a dekódolt csúcsok nem adják vissza a
Unity által a meshnek tárolt határolódobozt, a doboz méretének 2%-án belül. Ez
az elemzés saját ellenőrzése (lásd: [Unity](reader-unity.md)). Az olyan mesh,
amit nem lehet beolvasni, az okával együtt jelenik meg, és beleszámít a
korlátba. A `.resS` fájl csúcsadatait a tároló mappájából olvassa.

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

Ez exportálja a kör körüli pályát: a vezetés két oldalán egy sávnyi talajt és az
azon álló tárgyakat, egyetlen `.glb` fájlba. A többit maga találja ki: melyik
játék, melyik telepített példány, melyik pálya, szint vagy szakasz, és (Assetto
Corsa Rallynál) melyik irányban állnak a tengelyek. Lásd: [Pályaexportálás](course-export.md).

A `<lap>` a következők bármelyike lehet (részletek: [Körbemenetek](lap-inputs.md)):

- körfájl: route JSON, FH Companion kör JSON, `heat3d-lap` JSON, `.npz`, vagy `.csv` x, y, z oszlopokkal
- körfájlokat tartalmazó mappa, rekurzívan bejárva (egy egész rögzített pálya)
- egy pálya **neve**, amit az FH Companion könyvtárban keres a `%LOCALAPPDATA%\FHCompanion\laps` helyen

### Kapcsolók {#options}

| Kapcsoló | Alapérték | Játékok | Jelentés |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` az aktuális mappában, vagy a `$HEAT3D_LEVELS/<game>/courses/` mappában, ha az be van állítva | mind | hova írjon; a név kisbetűs lesz, a más karakterek sorozatai `_` jellel helyettesítve |
| `--game {forza,beamng,acrally}` | amit a körfájl mond, különben `forza` | mind | melyik játékból való a kör |
| `--margin M` | 80 | mind | méter talaj, amit a vezetés két oldalán megtart |
| `--texture-size {2048,1024,512}` | 2048 | mind | talajtextúra-pixel 512 m-es csempénként (2048 = 25 cm pixelenként) |
| `--no-textures` | ki | mind | csak lapos színek: sokkal kisebb fájl. Forzánál ez az úttest/szegély szétválasztást is kihagyja (lásd lent) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | melyik évszak talajtérképei és modelltextúrái |
| `--no-placed` | ki | mind | csak a terep: nincsenek szegélyek, korlátok, táblák, épületek. BeamNG-nél a modellezett vezetőfelületek megmaradnak |
| `--trees` | ki | mind | a növényzetet is elhelyezi (Forza: fák, bokrok és összetörhető tárgyak; BeamNG: fák; AC Rally: fák és a példányosított aljnövényzet) |
| `--detail-budget N` | automatikus | mind | háromszögplafon mindenre, ami el van helyezve; lásd: [Részletességi szintek és a keret](detail-budget.md) |
| `--track DIR` | keresi | Forza | a pályamappa (a `media\Tracks` alatt, benne a `GeoChunk0.minizip`), ha a telepített játékban nem keresni kell |
| `--level NAME` | a körből derül ki | BeamNG, AC Rally | a pálya (BeamNG mappanév) vagy szakasz (AC Rally térképnév), kis- és nagybetűtől függetlenül |
| `--install DIR` | keresi a Steam-könyvtárakban | BeamNG, AC Rally | BeamNG: a `gameengine.zip`-et tartalmazó mappa. AC Rally: a játékmappa, vagy annak `acr\Content\Paks` / `Content\Paks` mappája |

Az a kapcsoló, ami egy játékra nem vonatkozik, figyelmeztetés nélkül figyelmen
kívül marad. Például a `--season` a BeamNG-nél és az AC Rallynál nem tesz semmit,
a `--track` pedig ezekben sem.

### Melyik játék {#which-game}

A játékot a `--game` adja meg, utána a `heat3d-lap` fájl `game` mezője (vagy egy
CSV `# {...}` leíró sora), és ha ez sincs, alapértelmezés szerint a Forza. Egy
mappa azt a játékot kapja, amit a fájljai megneveznek, ha csak egy van; amelyik
fájl egyet sem nevez meg (FH Companion kör, `course.json`, leíró sor nélküli CSV),
az nem számít (lásd: [Körbemenetek](lap-inputs.md)).

| Érték | Export |
|---|---|
| `forza` kezdetű | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` vagy `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | elutasítva: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | elutasítva: "tracks ship in a protected format that is not a file-extraction target" |
| bármi más | elutasítva: "there is no course reader for <game> yet" |

Az elutasítás a lehetőségeket is felsorolja: rekonstruálni a pályát a játékmenetből
(3DHeat GameCapture), vagy a köröket pálya nélkül elemezni, mert a megjelenítő
Versenyelemzés fülén ezekből rajzolódik ki egy út.

### Példák {#examples}

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Példa a kimenetre (Forza, kitalált számokkal):

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

Minden telepített Forza-autó a játék saját alacsony részletességével, egyetlen
fájlban a megjelenítő versenyfülének: minden, a `media/Cars` alatti autóarchívum
`ProxyLOD` modellje, nagyjából 900 háromszöggel, az autó számával, ahogy a
telemetria megnevezi, a márkájával, modelljelölésével és évjáratával az
archívum nevéből, valamint a kerekeivel és hátsó lámpáival. Másodpercek alatt
készül, és körülbelül 5 MB-os fájlt ír. Ha a játék új autókat kap, futtasd újra.
Az olyan archívum, amelynek nincs ilyen modellje (forgalmi díszlet), név szerint
jelenik meg és kimarad. A formátum leírása: [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Az alakzatok méterben vannak, a játék saját méretei szerint: 1:1 az autóval. A
fájl a játék tartalmát tartalmazza, ezért arra a gépre való, amelyen készült, és
nem arra, hogy továbbadd.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Ez a Forza `course` exportját futtatja egy rögzített körkönyvtár minden
pályamappájára, és pályánként egy `<name>.glb` fájlt ír. Csak Forzához való. Közvetlenül
a Forza exportot hívja, és nem olvassa a `--game`, `--level` vagy `--install`
kapcsolókat.

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `-o`, `--out FOLDER` | `courses`, vagy a `$HEAT3D_LEVELS/forza/courses`, ha az be van állítva | a mappa, amibe ír (ha hiányzik, létrehozza) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | a körkönyvtár |
| `--only TEXT [TEXT ...]` | mind | csak azok a pályák, amelyek mappanevében szerepel valamelyik (kis- és nagybetűtől függetlenül) |
| `--force` | ki | újra exportálja, ami már van `.glb`-vel |
| `--track DIR` | keresi | mint a `course`-nál |
| `--margin M` | 80 | mint a `course`-nál |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | mint a `course`-nál |

Mi számít pályamappának: a körkönyvtár közvetlen almappája, amelynek neve
tartalmazza a ` (course_` részt, ahogy az FH Companion nevezi őket, például
`Example Circuit (course_1200_3400_to_1175_3400)`. A névből a ` (course_` utáni
rész elhagyásra kerül.

Egy futás így viselkedik:

- Ha egy pálya `.glb` fájlja már létezik, kimarad (`kept`), hacsak nincs `--force`,
  így a megszakadt futás ott folytatódik, ahol abbamaradt.
- Egy régebbi verzió által írt `.glb`, amelynek nincs meg a verseny saját rétege
  és helyszínei (az `asset.extras.course_format` hiányzik, vagy kisebb a jelenleginél),
  újra exportálódik, mintha csak arra a fájlra `--force` lenne megadva.
- Két azonos nevű pályamappa (a ` (course_` előtti rész) nem írja felül egymást: az
  előbb létrehozott mappa a `<name>.glb` nevet kapja, a másik `<name>_<start>.glb`
  lesz, ahol `<start>` a kezdőpont, a mínuszjelek `m` betűvel (például
  `example_circuit_m120_m340.glb`).
- Ami sikertelen (olvashatatlan körök, elfogyott memória, nincs terep...), `FAILED`
  jelzéssel szerepel, és a futás folytatódik.
- A végén egy táblázatot ír: állapot, méret MB-ban, eltelt másodpercek és név,
  utána: `<n> of <total> courses in <folder>`.
- A kilépési kód 1, ha bármelyik pálya sikertelen volt.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Kilistázza a telepített Forza minden versenyét, az útvonal-definícióikból (lásd:
[Forza Horizon pályák](course-forza-horizon.md#which-race)), és ellenőrzi a
`courses` mappa exportjait ezekhez képest. Olvassa a játékot és a körkönyvtárat;
a választható táblázaton kívül semmit nem ír.

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | a mappa, amibe a `courses` ír, és amelynek fájljait ellenőrzi |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | a körkönyvtár |
| `--track DIR` | keresi | a pályamappa, ha nem a telepített játékbeli |
| `--markdown FILE` | nincs | a táblázatot Markdownként is ide írja |

Egy sor minden versenyhez, és egy minden olyan rögzített pályához, amelyet azon
hajtottak:

| Oszlop | Jelentés |
|---|---|
| route | az útvonal azonosítója |
| course | az ahhoz illesztett rögzített pálya, ha van |
| own assets | a szabad mozgású világhoz a verseny által hozzáadott másolatok |
| drawn | ezek közül azoknak a másolatoknak a száma, amelyek modelljét a pálya szállítja |
| kinds | a hozzáadott másolatok típus szerint (korlátok, díszletek, matricák, infrastruktúra, ...) |
| not geometry | nézői jelölők és ütközési görbék, megszámolva |
| hidden | a szabad mozgású tárgyak, amelyeket a verseny eltávolít |
| venue | a helyszín talajmodelljei, amelyeket a verseny AI-vonala 10 m-en belül elhalad |
| export | `current`, `older format` (a `courses` újra exportálja), `not exported`, vagy üres, ha a versenyhez nincs rögzített pálya |

A végén egy összesítés áll: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Ez a Forza-kivágás minden részletében kézzel megadva: nem kört adsz meg, hanem a
pályamappát és egy területet. Akkor hasznos, ha a kívánt terület inkább doboz,
mint egy út.

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<path>` | kötelező | egy Forza pályamappa a `media\Tracks` alatt (benne `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | kötelező | a kiírandó `.glb` |
| `--box X0 Z0 X1 Z1` | | a terület, a játék méterében (x és z, ahogy a telemetria jelenti); a sarkok bármilyen sorrendben |
| `--route FILE` | | route JSON `"bounds": {"min": [x, y, z], "max": [x, y, z]}` mezővel, ahogy a `heat3d_capture route` és `heat3d_capture laps` írja; UTF-8-ként olvassa, byte-sorrendi jellel vagy anélkül |
| `--margin M` | **100** | méter, amit az útvonal határolódobozához ad, és a folyosó szélessége, ha az útvonalnak van vonala |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | mint a `course`-nál |

Pontosan egyet adj meg a `--box` és a `--route` közül, különben a kilépési kód 2.
A `--route` esetén a kivágás az útvonal `bounds` (`min`/`max`, x és z) értéke,
kiterjesztve a margóval. Ha a fájl legalább 10 pozíciót is tartalmaz, a kivágás
egy `--margin` méteres folyosóra szűkül körülöttük, az elhelyezett modelleket
pedig a távolságuk szerint kapják részletességüket. A `--box` esetén az egész doboz
megmarad, és a részletesség arra megy, ami a doboz közepe közelében áll.

A magasság soha nem része a kivágásnak. A térképen kívüli vagy tengeri doboz
"no terrain there" üzenetet kap (1-es kilépési kód), nem koordinátahibát.

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

A `levels` kilistázza a pályákat, amelyeket a telepített Frostbite-játék tartalmaz,
a táblázatuk (`levels/<level>/<level>.toc`) neve szerint, a méretükkel és azzal,
honnan származnak: `Data` az alapjátéknál, `Update/<pack>` egy frissítésnél, és
hogy hány nagy felbontású táblázat egészíti ki. Az a pálya, amelyet egy frissítés
szállít, az alapjátékban is tartalmaz egy kis darabtáblázatot; a pálya
köteginek táblázata a pálya (lásd: [Frostbite](reader-frostbite.md#which-table-is-the-level)).
A `level` egyet exportál: a terep magassági mezőjét, minden meshet, amelyet a
pálya statikus modellcsoportjai elhelyeznek, a tárgyakat egyenként, ahol állnak,
és a pálya terepi háttérét a térkép körül. A `--textures` kapcsolóval minden
felület hordozza a színtérképét; a `--navmesh` kapcsolóval a felületek, amelyeken
a katonák járnak, is bekerülnek. Hogyan olvassa: [Frostbite](reader-frostbite.md).

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<level>` | kötelező | név, ahogy a `levels` kiírja, annak egyedi része, vagy egy pálya `.toc`-jának elérési útja |
| `-o`, `--out FILE` | `<level>.glb` (a `$HEAT3D_LEVELS/<game>/` mappában, ha az be van állítva) | a kiírandó `.glb` |
| `--install FOLDER` | az első Steam-játék, amelynek `Data` mappájában van `layout.toc` | a játék mappája |
| `--textures [PIXELS]` | ki; méret nélkül 512 | minden felület színtérképe, a legnagyobb mip, ami legfeljebb PIXELS oldalhosszú, és a textúrakoordinátái, ahogy a játék használja, ismétlődő mintavételezővel (lásd: [Kimeneti formátum](output-format.md)). A magassági mező megkapja a terepi háttér színtérképét, ahol az lefedi, különben a terep felületi anyagainak középső színét, különben a háttér átlagszínét. Kikapcsolva minden rész lapos szín |
| `--ground-texture [METRES]` | ki; méret nélkül 0,5 | a terep matricái - utak, kifutók, betonfelületek, festett jelölések - rárajzolása a talajszínre, a terep színtérképével megszorozva, ahol van neki, a magassági mező színébe, METRES méter pixelenként, legfeljebb 4096 pixeles csempékben (`ground:terrain x<x> z<z>`). Működik `--textures`-szel és anélkül is |
| `--navmesh` | ki | a pálya navigációs hálójának hozzáadása a legkisebb ágensre, a katonára (1,8 m magas, 0,4 m széles), mint `nav:walkable` rész: a talaj, a padlók, lépcsők és a tetők, amelyekre egy katona eljut, az őket összekötő linkek nélkül (ugrások, létrák, átlendülések) |
| `--ground-spacing METRES` | 4 | a magassági mező legfinomabb osztása; a finomabb csomópontok ritkítva lesznek. 0 esetén a magassági mező kimarad |
| `--detail-budget N` | minden másolat a legdurvább szintjén, plusz negyed, legalább 1 500 000 | háromszögplafon. A legtöbbet költő meshek egy részletességi szintet vesztenek egyszerre, amíg be nem férnek; ha a legdurvább szintek sem férnek be, először a legkisebb másolatok maradnak ki. A terep háttere soha nem durvul és nem marad ki |
| `--skip TEXT` | | a statikus modellcsoportok kihagyása, amelyek partíciónevében előfordul a TEXT; többször is megadható. Például egy játékmód rétege |
| `--by-mesh` | ki | egy rész megtalálásához: forrásmeshenként és anyagonként egy rész, `<part> \| <mesh> \| <material>` névvel; sokkal nagyobb fájl |
| `--clamped-uvs` | ki | olyan megjelenítőhöz, amely nem tud textúrát ismételni: minden textúrázott háromszöget olyan darabokra vág, amelyek koordinátái 0..1 közé esnek, és amely háromszöget 4-nél több darabra kellene vágni, azt a textúrája átlagszínével rajzolja, a `<part> (average colour)` nevű részben |

Kiírja a csoportokat és azt, hány másolatot helyeztek el mindegyikből, a kihagyott
meshéket és az okukat, a háromszögeket részenként (és `--textures` esetén hány
textúra van, és hány szakasznak találta meg a színtérképét), hogy mi a talaj, és
`--navmesh` esetén hány navigációs csempét olvasott. A geometrián kívül a pályáról
nem ír semmit: se nevet, se metaadatot (lásd: [Kimeneti formátum](output-format.md)).

A terepköltségvetés külön van: a magassági mezőt és a hátteret a `--detail-budget`
soha nem durvítja, a magassági mező méretét a `--ground-spacing` adja.

Egy egész pálya nagy: jellemzően tízmillió háromszög fölötti, és több száz MB.
A `--textures` kevés pluszt ad a fájlhoz; egy fákkal teli pálya körülbelül 1 GB-ig
is nőhet. A `--textures 256 --detail-budget 3000000 --ground-spacing 8` nagyjából
a harmadára csökkenti.

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

A `<game>` a játék mappája, a `Content/Paks` mappája, vagy a játék mappanevének
neve egy Steam-könyvtárban (`"<Steam game folder name>"`). A `ue-maps` minden
olyan térképet kilistáz, amelynek mellette megépített World Partition cellái
vannak. A `ue-map` egyet exportál: `ground:<map>` (a tájkép), `structure:<map>`
(a térkép összevont HLOD-meshei) és `water:<map>` (a vízterületei, ahol a talaj
fölé emelkednek), Unreal **centiméterben**, az Y és Z tengellyel felcserélve - ez az
egyetlen export, ami nem méterben van. Hogyan olvassa és ellenőrzi: [Unreal 5 térképek](level-unreal-world-partition.md).

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<map>` | kötelező | név, ahogy a `ue-maps` kiírja, vagy annak egyedi része |
| `-o`, `--out FILE` | `<map>.glb` (a `$HEAT3D_LEVELS/<game>/` mappában, ha az be van állítva) | a kiírandó `.glb` |
| `--ground-spacing METRES` | 2 | a tájkép csúcsainak távolsága a fájlban, a saját négyzeteinek egész számára kerekítve |
| `--no-structures`, `--no-water` | | az adott részt kihagyja |

Kiírja a részenkénti háromszögeket, hány tájkép-komponenst olvasott, és hogy
ezek közül a kétszer tárolt csúcsok hány esetben nem egyeznek. Egy 3 km-es
térkép 2 m-en nagyjából 4,6 millió talaj-háromszög.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

Az `enfusion-worlds` minden olyan világot kilistáz, amelynek van terepe, a `worlds/`
alatti mappája szerint. Az `enfusion-world` egyet exportál: `ground:<world>` (a
terep, a szupertextúra-csempék színeiben), `water:<world>` (a tenger, nulla
magasságon) és `structure:<world>` (minden elhelyezett modell dobozai), a játék
saját méterében - x kelet, y fel, z észak. Hogyan olvassa és ellenőrzi:
[Arma Reforger világok](level-arma-reforger.md).

| Kapcsoló | Alapérték | Jelentés |
|---|---|---|
| `<world>` | kötelező | egy világ, ahogy az `enfusion-worlds` kiírja |
| `-o`, `--out FILE` | `<world>.glb` (a `$HEAT3D_LEVELS/<game>/` mappában, ha az be van állítva) | a kiírandó `.glb` |
| `--install FOLDER` | az a Steam-könyvtár, amelyik a játékot tartalmazza | a játék mappája |
| `--ground-spacing METRES` | 2 (a terepé) | a terep csúcsainak távolsága a fájlban |
| `--texture-size PIXELS` | 4096 | a talajszín-kép nagyobbik oldala; 0 lapos színhez |
| `--no-structures` | | az elhelyezett modelleket kihagyja |
| `--trees` | ki | fákat és más növényzetet is elhelyez, dobozként |

Kiírja a részenkénti háromszögeket, hány csúcs nem egyezik a csempék szélein, hány
entitást tartalmaz a világfájl, hány doboz lett elhelyezve, és mi maradt ki és miért.

## Environment variables {#environment-variables}

| Változó | Hatás |
|---|---|
| `HEAT3D_OODLE` | egy `oo2core_*_win64.dll` elérési útja, vagy a mappa, amelyben van; lásd: [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | egy mappa minden `-o` nélküli exporthoz: mindegyik játéké a `<HEAT3D_LEVELS>/<game>/` mappába kerül (a pályaexport-kurzusok a `<game>/courses/` alá, az autócsomag a `forza/` alá). Ha nincs beállítva, az aktuális mappába kerülnek |
| `HEAT3D_NO_UPDATE` | bármilyen érték, az üres, `0`, `false`, `no` kivételével, kikapcsolja a frissítés-ellenőrzést; lásd: [Frissítések](updates.md) |
| `LOCALAPPDATA` | ezen belül keresi az FH Companion könyvtárat, a BeamNG felhasználói mappáját és a frissítés-gyorsítótárat |
| `HEAT3D_COURSE` | csak tesztekhez: a kurzus, amelyet a telepített játék szegély-tesztje használ; lásd: [Fejlesztés](development.md) |
