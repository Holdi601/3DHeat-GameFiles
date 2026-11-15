---
title: Assetto Corsa Rally
nav_order: 3
lang: "hu"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Pályaexport: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Az Assetto Corsa Rally az Unreal Engine 5-re épül (5.6.1, módosított változat), és a
tartalmát IoStore-konténerekben szállítja. Egyik sincs titkosítva. Az export megtalálja a
szakaszt és a tengelyek irányát a körből. Felírja a szakasz saját talajcsempéit, úton és
terepen szétbontva, és a szakasz sütött talajszínéből textúrázza őket. A többi modellt
kategória szerint, egyszínűen helyezi el.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Forrás: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py)
(telepítés, szakaszok, elhelyezés),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py)
(az export). Az alatta lévő Unreal-olvasók az [Unreal 5 IoStore](reader-unreal-iostore.md)
oldalon vannak, a kicsomagolás az [Oodle](reader-oodle.md) oldalon.

**Állapot:** a telepített játékon ellenőrizve, minden szakaszon véletlenszerű keretben
generált körökkel, és minden alkalommal megtalálta a helyes szakaszt és keretet. A játékban
rögzített kör még nem ment át rajta.

## A telepítés megtalálása {#finding-the-install}

- `--install <mappa>`: a játék mappája, vagy annak `Content\Paks` mappája, vagy bármely mappa,
  amely `.utoc` fájlokat tartalmaz. Az eszköz ellenőrzi a `<mappa>`-t, aztán a
  `<mappa>\acr\Content\Paks`-ot, végül a `<mappa>\Content\Paks`-ot.
- Egyébként minden Steam-könyvtár `steamapps\common\Assetto Corsa Rally` mappáját ugyanígy
  ellenőrzi.
- A mappában lévő minden `.utoc` egy konténerként nyílik meg. A meg nem nyíló konténereket
  kihagyja. Ha egy sem nyílik meg: „no readable IoStore containers in ...".

A blokkok többsége Oodle-lel van tömörítve, a könyvtárat a gépen keresi (minden Steam-könyvtárat
átnéz). Lásd: [Oodle](reader-oodle.md).

A játékot AC Rally-ként ismeri fel, ha a körfájl `"game": "assetto-corsa-rally"` (vagy
`acrally`) értéket ad meg, vagy ha `--game acrally`-t adsz meg.

## Mi a szakasz {#what-a-stage-is}

A szakasz egy **World Partition** térkép:

- `Content\Levels\<Stage>.umap` helyezi el a távoli terepet.
- A `Content\Levels\<Stage>\_Generated_\*.umap` alatti cookolt cellák helyezik el a többit.

Egy pálya akkor számít szakasznak, ha a környezeti mappájában, `Content\Environments\<Stage>\`,
van `MeshesTrack` mappa. Az eszköz nem a csempék nevéből dönt, mert egy szakasz a csempéit
a térkép neve helyett egy városról nevezheti el. A `--level` nagy- és kisbetű-függetlenül
egyezik ezekkel a térképnevekkel. Hibás név esetén felsorolja a meglévő szakaszokat.

Nincs **talajréteg (landscape)**. A talaj statikus modellekből áll:

| Csempék | Útvonal | Ebből lesz |
|---|---|---|
| pályacsempék, kb. 175 m, kettéosztva | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` és `..._Terrain_k` | `ground:road` és `ground:terrain` (a fel nem osztott pályacsempe, például egy befagyott tó, csupa út) |
| távoli terep, 2 km-es csempék | `.../MeshesTerrain/...` | `ground:terrain` |

## Az elhelyezések olvasása {#reading-the-placements}

Egy modellt `StaticMeshComponent` helyez el: a `StaticMesh`-e, és a `RelativeLocation`,
`RelativeRotation` és `RelativeScale3D` értékei, mindegyik ahhoz a komponenshez képest,
amelyhez csatolva van (`AttachParent`), egészen az aktor gyökeréig, amely a világban van.

- A tulajdonságok **nem verziózottak**: az osztály tulajdonságlistájában elfoglalt helyük
  alapján vannak tárolva, nem névvel. A beolvasásuk az
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  sémáival történik (lásd: [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Ha az érték megegyezik a komponens sablonjával (egy Blueprint archetípusával), nincs tárolva.
  Ezért a sablon értékeit előbb, rekurzívan olvassuk be, és a komponens saját értékei
  felülírják őket.
- A `bVisible = 0` vagy `bHiddenInGame = 1` komponenseket kihagyjuk. Ugyanígy azokat a
  modelleket, amelyek elérési útja illeszkedik ezekre: `respawnwall`, `collision`, `blocker`,
  `invisible`, `/hlod/` vagy `_hlod`.
- A forgatások az Unreal `FRotationMatrix`-ét használják (pitch, yaw, roll fokban).
- A duplikátumokat (ugyanaz a háló, ugyanazzal a transzformációval, 0,1 cm pontossággal)
  eldobjuk.
- A beolvashatatlan komponenseket ok szerint számoljuk és jelentjük, például
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Példányosított komponensek** (erdők, szinte mind) csak a `--trees` kapcsolóval olvashatók.
Ennek a buildnek a motor fejléceihez képest átrendezte ezeket az osztályokat, ezért a
tulajdonságaikat nem olvassuk. Helyette:

- a hálót a csomag függőségi táblázata adja, ahol minden ilyen komponens pontosan egy statikus
  hálót sorol fel,
- a példányokat a tulajdonságok utáni natív blokk adja (`[1][1][128][count]`, majd `count`
  darab 4x4-es dupla mátrix),
- a komponenst úgy vesszük, hogy az aktor gyökerén ül, ahogy az erdei aktorok elhelyezik.

A koordináták Unreal-koordináták: centiméter, Z felfelé, X előre, Y jobbra, balkezes
rendszer.

## Melyik szakasz, és melyik irányban {#which-stage-and-which-way-round}

A telemetria keretét nem dokumentálták, ezért nem feltételezzük. Illesztjük:

- **Nyolc jelölt keret.** Az Unreal Z (cm) szorozva 0,01-del lesz a kör magassága (y). Az Unreal
  X és Y lesz a kör x és z értéke, felcserélve vagy nem, mindkét előjellel, mindet 0,01-del
  szorozva méterre.
- **Úttengely-rács.** Minden szakaszra minden úttcsempét elhelyezünk (a legdurvább
  részletességi szintjén), és cellánként 2 m-enként megtartjuk a legmagasabb úti csúcsot.
- **Pontozás.** Legfeljebb 400 egyenletesen elosztott köri mintát visszük át minden keretben
  az Unreal-térbe. Egy minta akkor van úton, ha a körülötte lévő 3 x 3 cella közül a hozzá
  legközelebbi úti magasság 1 m-rel a minta alatt és 3 m-rel fölötte van (`ON_ROAD`). A
  pontszám az úton lévő minták aránya.
- **Győztes.** A legjobb keret a legjobb szakaszon, ha legalább 50%-os. Különben az export
  megáll: „the lap does not lie on any stage's road in any frame (best: ...). Name the stage
  with --level."
- **Egy kör, amely megnevezi a pályáját.** Ha a körfájlnak van `track` mezője, akkor egy
  olyan szakaszt próbálunk először, egyedül, amelynek neve lazán egyezik vele (csak betűk és
  számjegyek, és az egyik tartalmazza a másikat). Ezt csak akkor fogadjuk el, ha legalább 80%-os.
  Különben minden szakaszt megpróbálunk.
- A `--level` megadásakor csak az a szakasz próbálódik, mind a nyolc keretben.

A konzol például ezt írja:
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Ezután minden **a kör keretében** íródik: méterben, Y felfelé. Egy háromszög körülfordítását
megfordítjuk minden olyan transzformációnál, amely tükrözi, így a lapok továbbra is a helyes
irányba néznek.

## A talaj {#the-ground}

- A sáv a kör körül `--margin` méter, a saját x/z síkjában.
- Minden talajcsempe a legfinomabb részletességi szintjén kerül elhelyezésre, és csak a sávba
  nyúló háromszögeket tartjuk meg.
- A háromszögeket fajta szerint (út vagy terep) és az Unreal-térben 512 m-es négyzet szerint
  csoportosítjuk (51 200 cm), minden négyzetnek saját képpel. A részek nevei például
  `ground:road 1_-4`. Az UV-k: `(unreal_xy - square_origin) / 51200`.
- A normálok a háromszögekből készülnek, az egész fájlra.

### A talajtextúra {#the-ground-texture}

A `--no-textures` kapcsoló nélkül minden négyzet két forrásból készül, `--texture-size`
pixelben:

1. **A sütött talajszín.** A szakasztérkép `RuntimeVirtualTextureComponent`-je (a doboza
   `RelativeLocation` a sarok, `RelativeScale3D` a méret, forgatás nélkül) egy
   streamelt **virtuális textúrára** mutat, a játék által sütött talajszínre. A négyzet
   területét ebből olvassuk ki, azon a szinten, amelynek pixelei a kért mérethez a
   legközelebb esnek. Ez szakasztól függően 13–59 cm pixelenként.
2. **A műholdkép** kitölti, amit a virtuális textúra feketén hagy. Ez a szakasz
   környezeti mappájában lévő `sat*_(b|bc|c|basecolor)` textúra, legfeljebb 4096 px-en
   olvasva. Az elhelyezését a távoli terep első UV-csatornájának legkisebb négyzetek szerinti
   illesztése adja a világ x és y értékéhez képest. Az illesztésnek 0,01-en belül lineárisnak
   kell lennie a 95. percentilisben, különben a képet nem használjuk. Ha a távoli terep UV-i
   1 fölé mennek (egy anyag ismétli őket), a leképezést felezzük, míg egyszer illeszkednek.

A konzol megmondja, melyiket használta, például
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Ahol egyik sincs, ott egyszínű talaj lesz.

## Elhelyezett modellek {#placed-models}

Minden elhelyezés, amely nem talajcsempe, a hálója útvonala szerint kerül kategóriába (az
első találat nyer):

| Kategória | A háló neve (vagy fáknál az útvonal) tartalmazza |
|---|---|
| fák (csak `--trees`-szel) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| sziklák | `rock`, `cliff`, `boulder`, `stone` |
| szegélykövek | `kerb`, `curb` |
| korlátok | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| táblák | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| épületek | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktúra | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| kellékek | minden más |

- Egy példányt akkor veszünk figyelembe, ha az origója a sáv-kiterjesztésben van
  (`margin + 60 m`), és akkor rajzoljuk, ha a határoló doboza érinti a sávot.
- A részletességi szintek a [Részletességi szintek és a keret](detail-budget.md) szerint
  követik egymást: távolsági sávok, majd a legköltségesebb modellek egy szinttel lejjebb lépnek,
  hogy a keretbe férjenek. Ahol még a legdurvább szintek is túllépik, a legtávolabbi
  példányokat kihagyjuk, ahogy a BeamNG-nél, amíg bele nem férnek. A szegélykövek megtartják a
  teljes részletességet, és soha nincsenek kihagyva. Az összefoglaló kiírja a
  `placed on it (N triangles of a B budget)` sort, és ha példányok kimaradtak,
  a `N copies left out to fit the budget, the furthest from the driving first` sort.
- Minden kategória egy rész, egyszínű színnel: a szegélykövek `ground:kerbs` néven, mert
  vezetési felületnek számítanak, ahogy a Forzában és a BeamNG-ben, a többi `structure:<category>`
  néven:

| Kategória | Szín (lineáris RGB) |
|---|---|
| korlátok | 0.55, 0.52, 0.48 |
| táblák | 0.75, 0.72, 0.65 |
| épületek | 0.62, 0.58, 0.52 |
| infrastruktúra | 0.48, 0.48, 0.50 |
| sziklák | 0.45, 0.43, 0.40 |
| kellékek | 0.55, 0.45, 0.35 |
| fák | 0.20, 0.32, 0.14 |
| szegélykövek | 0.70, 0.25, 0.22 |

A statikus hálók, amelyek nem olvashatók (csontozott hálók, csak Nanite hálók, a fájlon belül
nem tárolt szintek), meg vannak számolva: `N meshes could not be read`.

## Ellenőrzések {#checks-behind-it}

A forráskód szerint, a telepített játékon:

- Minden tartalomjegyzék beolvasódik (8-as verzió).
- Minden szakasz minden cellája megnyílik, és minden statikus háló- és jelenetkomponens pontosan
  az osztályának natív záróbájtjánál ér véget.
- Szinte minden mintavett statikus háló beolvasódik (a többi csontozott). Egy úti csempe
  dekódolt kiterjedése egyezik a tárolt határoló doboza méretével.
- Egy műholdkép mip-szintjei pontosan megegyeznek a bulk bejegyzéseik méreteivel.
- Egy virtuális textúra-darab csempéi bájtra pontosan el vannak számolva, és az úti csempék az
  általa mutatott útra esnek.

## Ismert hiányosságok {#known-gaps}

- A példányosított komponensek saját tulajdonságait nem olvassuk (lásd fent). Az elhelyezésük
  az aktor gyökerére támaszkodik.
- A PCG által futásidőben generált erdők nincsenek a fájlokban tárolva, nem exportálhatók.
- A spline-hálók (láthatatlan újraélesztési falak), a matricakomponensek és az elhelyezett
  modellek saját textúrái nem rajzolódnak ki. A modellek egyszínűek.
- A `--season` nincs hatással.
- Egy játékfrissítés elmozdíthatja a tulajdonságrések helyét. Az olvasó ilyenkor hibát dob
  ahelyett, hogy rosszul olvasna, a pálya pedig jelenti, hány komponens nem sikerült.
