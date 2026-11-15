---
title: BeamNG.drive
nav_order: 2
lang: "hu"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Pályaexportálás: BeamNG.drive {#course-export-beamngdrive}

A BeamNG-export úgy olvassa a pályát, ahogy a játék csatolja, majd ugyanolyan
fájlt ír, mint a Forza-export: talajt 512 m-es négyzetenként, sütött
textúrával, az úttestet és a laza talajt külön részként, az elhelyezett
modelleket kategóriánként, és a vizet.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Források: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (telepítés, fájlrendszer, jelenet, terep, anyagok),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (az export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) és
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (alakzatok).
A fájlformátumok részletesen: [BeamNG-fájlok](reader-beamng.md).

## A kör koordinátarendszere {#the-laps-frame}

A `course` export a BeamNG-pozíciókat a **megjelenítő koordinátarendszerében**
várja: a BeamNG Z-felfelé világának `(x, z, -y)` értékei, méterben. Ezt a
rotációt alkalmazza a 3DHeat telemetria-rögzítője. Az export visszaforgatja a
kört a BeamNG koordinátarendszerébe (`(x, -z, y)`), ott dolgozik, majd mindent
újra a megjelenítő koordinátarendszerében ír ki. Ez forgatás, nem tükrözés, így
semmi sem lesz tükrözött. A BeamNG nyers koordinátarendszerében rögzített kör
nem kerülne a helyére. Más rögzítőkkel nem tesztelték.

A játék BeamNG-ként értelmeződik, ha a `heat3d-lap` fájl `"game": "beamng"`
mezőt tartalmaz, vagy ha a `--game beamng` kapcsolót adod meg.

## A telepítés megtalálása {#finding-the-install}

- `--install <folder>`: a mappa, amelyben a `gameengine.zip` és a `content` van.
- Egyébként minden Steam-könyvtár `steamapps\common\BeamNG.drive` mappáját
  ellenőrzi ezekre a két elemre.
- Ha egyik sem működik: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## A fájlrendszer {#the-file-system}

A BeamNG sima zip-archívumokat szállít, és ezeket egyetlen fájlrendszerbe csatolja,
amelyre a pályák hivatkoznak (`/art/shapes/...`, `/assets/materials/...`). Az export
ugyanezt építi meg: egyetlen kis- és nagybetűre nem érzékeny indexet a következőkből:

1. `gameengine.zip`,
2. minden `*.zip` a `content` alatt, kivéve a `content\vehicles\*` mappát és azokat
   az archívumokat, amelyek neve `art_sound` vagy `audio` kezdetű,
3. a felhasználó tartalma, az legújabb elrendezés először: a
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` és a `%LOCALAPPDATA%\BeamNG.drive` alatt a
   `current` mappa és a legmagasabb számú verziómappa. Mindegyikből: `mods\*.zip`,
   a `mods\unpacked` minden mappája, és maga a felhasználói mappa, ha van benne
   `levels` mappa.

A későbbi hozzáadások nyernek, ahogy a játékban is, így egy mod felülírja azt,
amit felülír. A modok mindig benne vannak a kör exportjában.

A pálya által megnevezett elérési utakat úgy oldja fel, ahogy a játék: először
ahogy meg van adva, majd a fájl szerint, amely megnevezte őket, és mindegyiknél
azt a `.dds`-t is, amelyre a textúrát sütötték, azt a `.cdae`-t, amelyre a `.dae`-t
fordították, vagy egy `/assets`-re mutató `.link` fájlon keresztül.

## Melyik pálya {#which-level}

A `--level` nélkül minden pályát pontoz aszerint, hogy a körnek mekkora része
fekszik rajta:

- Legfeljebb 500 körpont, egyenletes közökben, kerül felhasználásra.
- Minden pálya `TerrainBlock`-jának kiterjedését a `.ter` fájl első öt bájtjából
  olvassa, így a kör által nem érintett pálya nem kerül költségbe. Ha a pontok
  legalább 30%-a a kiterjedésen belül van, a magasságok beolvasásra kerülnek. Egy
  pont akkor számít a terepen lévőnek, ha 1 m-rel a terep alatt és 3 m-rel fölötte
  van között (`ON_GROUND`), mert az autó referenciapontja a karosszéria, nem a
  kerék.
- Ha egyik pálya sem éri el az 50%-ot, a pályákat az **útjaik** alapján is
  pontozza. Néhány pálya a magasságtérképén túl fut (szélei sziklalemezként
  folytatódnak). Egy pont akkor út, ha a út félszélességének és 4 m-nek a
  összege (legalább 6 m) belül van egy `DecalRoad` szakaszától, és 2 m-rel a
  felület alatt és 4 m-rel fölötte van.
- A legjobb pálya nyer, ha legalább 30%-ot ér el. Különben az export megáll, és
  a három legjobbat listázza: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

A konzol kiírja: `on <level>: 87% of the lap lies on its terrain` (vagy `roads`).
A `--level` a pályamappák nevéhez kis- és nagybetűtől függetlenül illeszkedik.

## A pálya olvasása {#reading-the-level}

Egy pálya a következőkből áll, mindegyik a shipped pályákhoz ellenőrizve
(részletek: [BeamNG-fájlok](reader-beamng.md)):

- **Jelenet**: `levels\<name>\main\**\*.level.json` (soronként egy JSON-objektum,
  vagy JSON-tömb), vagy régebbi pályáknál egy `.mis` fájl. Az eszköz olvassa a
  `TSStatic` objektumokat (elhelyezett modellek, a rejtetteket kihagyva), a
  `Prefab` objektumokat (legfeljebb 8 mélyen egymásba ágyazva, TorqueScript
  `.prefab` vagy `.prefab.json`), a `DecalRoad` objektumokat (festett utak), a
  `TerrainBlock`, `WaterPlane`, `WaterBlock` és `River` objektumokat.
- **Erdei elemek**: `levels\<name>\forest\*.forest4.json`, a
  `managedItemData.json` bejegyzéseivel típusozva. Korlátok, kerítések és sziklák
  ugyanannyiszor erdei elemek, mint a fák.
- **Terep**: a `.ter` magassági mező és a rétegtérképe.
- **Anyagok**: minden `*.materials.json` a `levels\` mappán kívül, valamint ennek a
  pályának a saját anyagai.

## A folyosó és az úttest-matricák {#the-corridor-and-the-road-decals}

A folyosó `--margin` méter a kör körül a BeamNG x/y síkjában (lásd:
[Pályaexportálás](course-export.md#the-corridor)). A `margin + 60 m`-es
elérési folyosó választja ki a jelölteket.

**Úttest-matricák** (`DecalRoad`): a BeamNG útjainak nagy része ezek: a terepre
festve, nem modellezve. A kiterjedésük érinti az elérési folyosót, azok a játék
rajzolási sorrendjében kerülnek figyelembe (`renderPriority` szerint csökkenően,
majd fájlsorrendben), szalagokként elrendezve:

- A csomópontok (x, y, z, szélesség) körülbelül 1 m-enként **centripetális
  Catmull-Rom** spline-nal interpolálódnak. Az egyenletes típus visszahurkolódik
  ott, ahol a csomópontok egy kanyarban összesűrűsödnek. A hurkolt utak lezáródnak.
- Minden él a terep magasságát veszi, ahol a terep az út saját magasságától 1,5
  m-en belül van, máshol megtartja az út magasságát (hídon).
- Az anyag neve dönti el, mit fest a matrica:

| Típus | Az anyagnév egyezik (az első egyezés nyer) |
|---|---|
| gumiabroncs-nyomok | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| átfedés (csak díszítő) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| jelölések | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| laza | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| út | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| átfedés | minden más |

## A talaj {#the-ground}

A folyosón belüli terep-magassági mező háromszögekké válik:

- Egy négyszög minden olyan terepnégyzetre, amelynek középpontja a folyosóban
  van. A 255-ös rétegű négyzetek (lyukak) kimaradnak. Minden négyszög két
  háromszög, az átló váltakozva, ahogy a Torque terepe csinálja.
- A magasságok `position.z + h * maxHeight / 65535`. A normálok a
  magasságkülönbségekből jönnek.
- Minden négyzet a **rétegével** kerül osztályba: a rétegnév a terepanyagának
  talajmodelljével és megjegyzésével együtt. A burkolt szavak `road`-dá teszik, a
  `grass/forest/rock/moss/leaves/cliff/stone` `terrain`-né, a laza szavak pedig
  `loose`-szá (kavics és föld). Minden más `terrain`.
- Ezután az **úttest- és laza matricák felülírják** azokat a négyzeteket, amelyeket
  lefednek, a rajzolási sorrendben, így az utolsó matrica dönt.
- A csúcsok 512 m-es négyzetenként oszlanak el (`floor(x / 512)`, `floor(y / 512)`),
  így minden rész pontosan egy képbe képeződik le: `u = (x - x0) / 512`,
  `v = 1 - (y - y0) / 512`.

A konzol kiírja a `what the ground is made of` részt, típusonként a háromszögek
számával.

### Modellezett vezetőfelület {#modelled-driving-surface}

A BeamNG versenypályái gyakran modellek, nem terep. Egy versenypálya pályája lehet
egyetlen háló, a vonalaival, gumiabroncs-nyomaival és rezgősávjaival külön
hálóként a tetején. Ezért az út, a szegély, a széle és a híd kategóriájú elhelyezett
modelleket vezetőfelületre keresi. Anyagonként:

| Felület | Ez dönti el (az első egyezés) |
|---|---|
| gumiabroncs-nyomok | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` a névben, a talajtípusban vagy a megjegyzésben |
| jelölések | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` az anyagnévben |
| szegélyek | `rumble`, `kerb`, `curb` |
| út | talajtípus `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, vagy a név tartalmazza: `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| laza | talajtípus `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| széle | `sidewalk` |
| (a modell saját kategóriája) | azoknak a modelleknek, amelyek már úton, szegélyen vagy szélen vannak |

Ezekből az anyagokból a **felfelé néző** háromszögek (normál z-je 0,5 felett) a
folyosón belül kikerülnek a modellből, és talaj lesz belőlük. A sütött textúrába
festik, és olyan részekként íródnak ki, mint például `ground:road 3_-2 asphalt_light`.
A jelölések és a gumiabroncs-nyomok csak festettek. A modell többi háromszöge a
modellnél marad. Ezeket a modelleket a keret soha nem egyszerűsíti vagy hagyja
ki, mert egy pontatlan pálya hibás pálya.

## A sütött talajtextúra {#the-baked-ground-texture}

Minden olyan 512 m-es négyzet, amelynek van talaja, egy `--texture-size`
pixeles képet kap (2048 = 25 cm pixelenként), úgy rajzolva, ahogy a játék rajzolja
a talajt:

1. **Terepi rétegek.** Pixelenként a négy környező terepnégyzet rétegei
   bilineárisan keverednek. Minden réteg úgy színeződik, ahogy a játék színezi:
   az anyag **alaptérképe** `diffuseSize` méterre kinyújtva (vagy az egész
   terepen), majd a **részletes** és **makro** térképek szürke átfedésként
   (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 a semleges). Alapértelmezésük
   2 m-enként és 60 m-enként ismétlődik, 0,5-ös és 0,3-as erősséggel, hacsak az
   anyag másképp nem mondja. Anyag nélküli réteg a felületének lapos színét kapja.
   Az alaptérkép 0. sora észak.
2. **Úttest-matricák**, amelyek csak a terepre vannak festve, a rajzolási
   sorrendben, mindegyik a saját textúrájával, átlátszóság-térképével, színezésével
   és átlátszóságával, a szalag mentén. A megjelenített pályák 12-16 körüli
   prioritásokat használnak az aszfalt alapokhoz, 10-et a jelölésekhez és 4-et a
   gumihoz.
3. **Modellezett vezetőfelület** felülről nézve: először az alapok, majd az
   átfedések, mindegyik a modell saját ismétlődő textúrájában, sütési
   pixelenként egy texelben.
4. **Matricák, amelyek tárgyakra is vetülnek** (`overObjects`), utoljára.

A `--no-textures` kapcsolóval semmi sincs sütve: a talajrészek lapos színt
kapnak, a modellezett jelölések és gumiabroncs-nyomok pedig külön részekké
válnak, **3 cm**-rel megemelve.

## Elhelyezett modellek {#placed-models}

A jelöltek minden olyan `TSStatic`, prefab-gyermek és erdei elem, amelynek
origója az elérési folyosóban van. Egy jelölt akkor rajzolódik ki, ha alakzatának
világbeli határolódoboza érinti a folyosót.

A **kategóriát** a pálya saját megjegyzése és az alakzat útvonala adja. Az első
szabály, amely illeszkedik, nyer:

| Kategória | Megjegyzés | Útvonal vagy név tartalmazza |
|---|---|---|
| háttér (soha nem rajzolódik) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| szegélyek | | `kerb`, `curb`, `rumble` |
| út | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| széle | `SIDEWALK`, `COBBLESTONE` | |
| fák (csak `--trees`-szel) | `NATURE` | tree, foliage, bush, grass, plant és hasonló szavak |
| sziklák | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| korlátok | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| táblák | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| hidak | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktúra | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| épületek | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| díszletek | | minden más |

Az **alakzatok** a fordított `.cdae`-ből olvasódnak, vagy ahol nincs gyorsítótár
(modok), a Collada `.dae`-ből. Az olvashatatlan alakzat számolódik: `N copies of M
models could not be read`. Az `invisible`, `collision` vagy `nodraw` nevű vagy
ilyen textúrájú anyagok soha nem rajzolódnak.

**Textúrák.** A modellek kategóriánként és anyagonként `structure:<category>
<material>` (vagy `ground:kerbs <material>`) nevű részekbe kerülnek. Egy csoport
megkapja az anyagának színtextúráját legfeljebb **256 px**-ben, de csak akkor, ha
az UV-koordinátái 0-1 közé esnek (a csúcsok 98%-a -0,02 és 1,02 között). A
megjelenítő atlaszba csomagolja a textúrákat, és nem tud ismételni. Egy olyan
csoport, amelynek textúrája ismétlődik, a textúra átlagszínével rajzolódik
(alfa-súlyozva, sRGB-ben, az anyag színezésével szorozva), vagy a kategória
színével, ha nincs textúrája.

**Részletesség.** A közös séma szerint (lásd: [Részletességi szintek és a keret](detail-budget.md)).
A BeamNG részletességi szintjei az alakzat `details` mezői (a legnagyobb
pixelmérettel kezdve). A keret túllépésekor a legtávolabbi másolatok mennek
először. A szegélyek és a vezetőfelületet hordozó modellek soha nem egyszerűsödnek
és nem maradnak ki.

A `--no-placed` eltávolítja a szerkezeteket, de a modellezett vezetőfelületet
megtartja. A `--trees` hozzáadja a fák kategóriáját.

## Víz {#water}

| Forrás | Hogyan rajzolódik |
|---|---|
| `WaterPlane` (a tenger) | 4 m-es négyszög a víz magasságában minden olyan folyosó-cellára, ahol a terep nem éri el azt a magasságot |
| `WaterBlock` | egy négyszög, az egységnégyzet a blokk transzformációjában a helyi z = 0-nál (így a skálája adja a méretet), ha érinti a folyosót; hogy a z = 0 a blokk felszíne-e, az nincs ellenőrizve |
| `River` | szalag a csomópontjain át, ha érinti a folyosót |

Az összes víz egyetlen lapos rész: `water:water`.

## Nem rajzolódik {#not-drawn}

- Talajtakaró (procedurális fű).
- A világ szélén elhelyezett díszlet (`backdrop` és hasonlók).
- Ismétlődő modell-textúrák, amelyek átlagszínként jönnek ki (lásd fent).
- Modelleken belüli csontozott meshek (járművek, karakterek) és dekor-meshek.

## Az ellenőrzések háttere {#checks-behind-it}

Ahogy a forrásban állítják, a betöltött pályákon mérve:

- Az úttest csomópontjai 1-2 cm-en belül fekszenek a terepen (medián) a vizsgált
  pályákon, `h * maxHeight / 65535` értékkel és a +y mentén sorokkal. A `h / 32`
  vagy más tengelysorrend tíz-száz méterrel téved.
- Az úthoz láncolt sínszakaszok a `rotationMatrix` 0. sora mentén futnak (a
  túlnyomó többség).
- A `.cdae` csomópont-forgatását transzponálni kell. Ezzel a világi határok
  milliméterre egyeznek a forrás `.dae`-vel. A tankönyvi módszer 38 cm-rel téved
  (medián).
- Több betöltött pályán, minden fajtából, exportálva, másodpercek és percek alatt.
