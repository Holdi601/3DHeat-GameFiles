---
title: "Frostbite: `.toc`, `.cas`, kötegek, hálók és pályák"
nav_order: 5
lang: "hu"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, kötegek, hálók és pályák {#frostbite-toc-cas-bundles-meshes-and-levels}

**Egy Battlefield 6 pályát olvas a terepéig, az elhelyezett hálóiig és azok
színtérképeiig, és `.glb`-ként írja ki.** A Frostbite-játékok (Battlefield, Need for
Speed, Dead Space) tartalmukat `.cas` blobokban tárolják, amelyeket `.toc`
tartalomjegyzékek írnak le. Egy pálya táblázata megmondja, mely köteget tölti be a
pálya, a kötegek minden eszközt megneveznek, az eszközök pedig megmondják, melyik
mesh hol áll.

Források:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(táblázatok, csomagok, adatblokkok),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(kötegek és manifesztjeik),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-partíciók),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(magassági mező),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(textúrák és anyagok),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(elhelyezés és export).
Parancsok: `identify`, `levels`, `level` (lásd: [Parancsok](commands.md#levels-and-level-frostbite)).

A játék egyik részt sem dokumentálja. Minden alábbi elrendezést a fájlokról
olvasták le, majd az összes fájlon ellenőrizték, és minden szakasz leírja, mi
volt az ellenőrzés. Ahol a Frosty modding-eszközök egy régebbi verzió szerkezetét
írják le, a mezőnevek az ő neveiket követik; kódot nem vettek át tőlük (lásd:
[Jogi kérdések és licencek](rules-and-licences.md)).

## Az a fejléc, amely titkosítottnak látszik, de nem az {#the-header-that-looks-encrypted-and-is-not}

| Azonosító (u32, kis-endián) | Jelentés | Kezelés |
|---|---|---|
| `0x00CED100` | sima: a fa azonnal kezdődik | olvasva |
| `0x01CED100` | aláírt: 556 bájtos aláírás, utána a fa **nyíltan** | olvasva |
| `0x03CED100` | XOR-obfuszkált, a kulcs a fájl saját fejlécében | felismerve és elutasítva |

Az aláírt forma az, amit a mai Battlefield szállít. Az azonosító utáni nagy
entrópiájú bájtok aláírás, nem titkosított szöveg.

## A DbObject-fa {#the-dbobject-tree}

Egy rekurzív szerkezet. Minden mező egy típusbájt (az alsó öt bit a típus, a 7.
bit az "anonymous" jelző), egy opcionális név és egy érték. A tárolók hosszukat
változó hosszúságú egészként hordozzák, és egy nulla bájttal zárulnak. A
`parse_toc` minden tároló hosszát ellenőrzi, így ami feldolgozódik, az értelmezett.
A `layout.toc` ebben a formában van.

## Telepítési csomagok {#installation-packages}

Minden hely megnevezi azt a **telepítési csomagot**, amelyhez a blobja tartozik.
Minden csomag `cas_01`-től számozza a blobjait, így a blobszám önmagában
kétértelmű, amint egynél több csomag van telepítve, ami mindig így van.

- A `layout.toc` a `installManifest.installChunks` alatt sorolja fel a csomagokat,
  mindegyikhez egy `persistentIndex`-szel és egy `installBundle`-lel, például
  `Win32/installation/<package>`.
- A csomag blobjai abban a mappában vannak: az alapjátéknál a `Data` alatt, a
  későbbi tartalomnál az `Update/<pack>/Data` alatt.
- Egy helyrekord a teljes 32 bites `persistentIndex`-et hordozza: az első szó
  alsó fele tartja a felső felet, a második szó felső fele az alsó felet; a második
  szó alsó fele a blobszám.

Ellenőrzés: egy telepítés minden binális táblázatának minden helye egy deklarált
csomagra oldódik fel, és a megnevezett blob határain belül esik. Egy korábbi
verzió az első, megfelelő számú `cas_NN.cas`-t vette. Az általa olvasott
adatblokkok harmada ekkor magas entrópiájúnak látszott, és titkosításnak
vették. A helyes eltolások voltak, csak rossz fájlban. Semmi, amit találtak, nincs
titkosítva.

## A pálya táblázata {#the-level-table}

Egy pálya táblázata (`levels/<level>/<level>.toc`) egy szakasztábla: tizenöt
nagy-endián fejlécszó, majd egymás után következő szakaszok, amelyek eltolásai
egyszerre vannak megadva és két számból levezethetők.

| Szakasz | Tartalom |
|---|---|
| kötegek | egy hash-tábla (szavanként egy), majd kötegenként egy 16 bájtos rekord: kulcs, `0x40000000` \| méret, 0, eltolás |
| darab-hash-tábla | darabonként egy szó |
| darabok | 16 bájtos azonosító (a darab GUID-ja **bájtsorrendben megfordítva**), majd egy szó: `0x80000000` \| 4 x a helyének indexe |
| helyek | négy nagy-endián szó: csomag (felosztva), blob, eltolás, méret |

A darab-azonosítók és a helyek **különböző sorrendben vannak**. Ha fájlsorrendben
olvassuk őket, minden darab egy másik darab bájtjaival párosul, amelyek szépen
dekódolódnak (többnyire hangként), és ezért nem tűnnek hibásnak, amíg egy mesh zajként
nem jelenik meg. Ellenőrzés: egy pályában az indexszavak 0-tól a darabszám mínusz
egyig terjedő permutációt alkotnak.

A kötegek a szakasztábla után, beágyazva vannak tárolva. Mindegyik kilenc nagy-endián
fejlécszó, majd a bejegyzései: nyolc bájt eltolás és méret, amelyet nyolc további
bájt előz meg, amelyek a csomagot és a blobot nevezik meg, ha a bejegyzés jelzőbájtja
felső bitje be van állítva. Ellenőrzés: minden kötegen az utolsó bejegyzés pontosan
ott ér véget, ahol a jelzőbájtok kezdődnek.

### Melyik táblázat a pálya {#which-table-is-the-level}

Egy pályának több azonos nevű táblázata lehet: egy az alapjáték `Data` mappájában,
egy-egy minden frissítésben (`Update/<pack>/Data`), amely szállítja vagy módosítja,
és egy-egy minden nagy felbontású csomagban
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Csak némelyikük
tartalmaz köteget. Egy olyan pályánál, amelyet egy frissítés szállít, az alapjáték
táblázata csak darabokat tartalmaz köteg nélkül, és a frissítésben lévő a pálya:
az első megtalált táblázat exportált volna valamit, de nem a pályát.

Ezért a pálya az a táblázat, amelyben a legtöbb köteg van, döntetlennél a későbbi
réteg nyer (először az alapjáték, majd a frissítések névsorban). Az azonos nevű,
köteg nélküli táblázatok a pálya **kiegészítői**: darabjaikat hozzáadják a pályáéhoz,
mert ezekben vannak a textúrák legnagyobb mipjei. A textúra-fejléc a +164-nél
nevezi meg ezt a darabot (lásd: [Textúrák és anyagok](#textures-and-materials)). A
`levels` kiírja, honnan jön minden pálya, és hány kiegészítője van.

## Kötegmanifesztek {#bundle-manifests}

Egy köteg első bejegyzése a manifesztje, tömörítés nélkül tárolva. Ez a korábbi
Frostbite-játékok bináris kötegformátuma, új azonosítóval, `0xD68E799D`: számlálók,
SHA-1-ek, ebx- és res-rekordok (névpozíció és méret), res-típusok, metaadat és
azonosítók, darab-GUID-ek, karakterláncok. A köteg többi bejegyzése az ebx, a res és
a darabok ebben a sorrendben. Ellenőrzés: a számlálók minden köteg bejegyzéseinek
számával egyeznek, és a karakterláncok ott kezdődnek, ahol a rekordok véget érnek.

A res-típusok hash-ek. A `0x49B156D4` a MeshSet (minden ilyen típusú res
`..._mesh` nevű), a `0x6BDE20BA` Texture, a `0x22FE8AC8` TerrainStreamingTree.

A `LevelCatalogue` ezt az egészet egy pályára néhány másodperc alatt beolvassa: egy
pályának tucatnyi köteg, tízezreknyi ebx, res és darab van.

## Adatblokkok {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Nulla tömörített méret azt jelenti, hogy tárolva van, feltéve, hogy kicsomagolva
ugyanakkora.

| Módszerszó | Kodek |
|---|---|
| `0x0070`, `0x0071` | nincs |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), a játék saját `oo2core` DLL-jéből) |
| más, azonos méretekkel | ahogy tárolva van, másolva |
| más | elutasítva |

A megfelelő csomagból olvasva minden mintavételezett adatblokk dekódolódik.

## EBX-partíciók {#ebx-partitions}

Az EBX mindent tartalmaz, ami nem nyers adat. Minden partíció egy RIFF-fájl:
`EBXD` (az adat, 16-ra igazítva), `EFIX` (partíció-GUID, típus-GUID-ek és
aláírások, példány, mutató-, import- és típusinformáció-eltolások, importok, valamint
a tömb-, dobozolt-érték- és karakterlánc-eltolások), `EBXX` (a tömbtábla: eltolás,
darabszám, hash, jelzők, elemtípus). Egy mutatómező nyolc bájt: a nulla null, a
páratlan érték az `value >> 1` számú import, minden más a mezőhöz képest relatív.

A **típuskönyvtár nem olvasható**. A játék a kezdeti fájlrendszerében szállítja, ami
titkosított, és ez a csomag nem nyúl hozzá. A típusok GUID és aláírás alapján
ismertek, amelyet minden partíció hordoz, és a pálya-exporthoz szükséges néhány
típust az adatokból rajzolták meg.

## MeshSet {#meshset}

Egy mesh egy MeshSet res (a leírás) és minden részletességi szinthez egy darab (a
pufferek).

| Rész | Elrendezés |
|---|---|
| előtag | négy szó: fejlécméret (176 vagy 192), szintrekord-méret (176-188), szakaszrekord-méret (368), 0 |
| fejléc | határolódoboz; hat i64 szinteltolás; a mesh típusa a `0x6C`-nél (merev, csontozott, összetett); szint- és szakaszszám a `0x9C`-nél |
| szint | szakaszok a `+0x08`-nál; öt rajzolási lista a `+0x14`-nél (átlátszatlan, átlátszó, dekál, csak mélység, árnyék); indexformátum a `+0x54`-nél (`0x21` u16, `0x2E` u32), index- és csúcsbájtok; darab-GUID a `+0x74`-nél |
| szakasz | anyagnév; csúcslépés; háromszögek, első index, csúcseltolás (bájtban), csúcsszám a `+0x20`-nál; csúcsdeklaráció a `+0x64`-nél: 16 x (használat, formátum, eltolás, adatfolyam), 16 adatfolyam-lépés, számlálók |
| darab | a csúcspuffer, majd az indexpuffer. Egy szakasz adatfolyamai egymás után következnek, az indexek a szakasz első csúcsától számítanak |

A pozíciók használat 1, adatfolyam 0, eltolás 0, mint négy félszó vagy három lebegőpontos
érték. Csak az átlátszatlan és átlátszó szakaszok rajzolódnak. Minden `..._shadow`
nevű szakasz az árnyéklistában van, és csak ott, így a listák döntenek.

Ellenőrzés: egy pálya minden meshe, amelynek szintjei darabokban vannak tárolva,
dekódolódik, és szinte mindnek a csúcsainak 99% vagy több része a deklarált
dobozán belül van; a többi félszó-kerekítésből marad ki. Egy dekódolt láda nagyjából
egy méter, Y felfelé, normáljai kifelé mutatnak.

## Elhelyezés {#placement}

A tartalomfeldolgozás egy részpálya statikus objektumait egy **statikus modellcsoportba**
gyűjti: tagok tömbje, egy minden meshre, mindegyiknek a példány-transzformációival.

| Típus (GUID, aláírás) | Elrendezés |
|---|---|
| tag `ad13064e…`, `0xF861A878` | 224 bájt: `+88` transzformációk tömbje, `+112` az objektumtervrajz (import), `+160` a mesh-eszköz (import) |
| transzformáció `101dce06…`, `0x5E6D8C37` | 64 bájt: jobb, fel, előre, eltolás, mindegyik 16-ra kitöltött vec3 |

A mesh-eszköz partíciója a hozzá tartozó MeshSet res nevét viseli, így az import
partíció-GUID-je adja meg a meshet. Egy pont ide kerül:
`x·right + y·up + z·forward + translation`. A csoport saját transzformációja az
ellenőrzött pályák minden csoportjában az identitás volt, és nincs alkalmazva.

Ellenőrzés: egy pályában minden csoport minden tagja meshre oldódik fel; a legtöbb
példánynak ezredpontossággal 1 determinánsú forgatása van, a többi skálázott vagy
tükrözött. A típus-GUID-ek és aláírások más pályákon is ugyanazok. Egy játékfrissítés,
amely megváltoztatja az elrendezést, megváltoztatja az aláírást, és az olvasó ekkor
semmit nem talál, ahelyett hogy félreolvasna.

### Egyenként elhelyezett objektumok {#objects-placed-one-by-one}

Amit a feldolgozás nem tud csoportosítani - rombolható tárgyak, konténerek, törmelék
-, azt a pálya partícióiban lévő **objektumhivatkozások** és **prefab-hivatkozások**
helyezik el:

| Típus (GUID, aláírás) | Elrendezés |
|---|---|
| objektumhivatkozás `a9a6a6ad…`, `0xC4856BEC` | `+32` a transzformáció (mint fent), `+112` az objektumtervrajz (import) |
| prefab-hivatkozás `117c746e…`, `0xDE3FE9B4` | ugyanaz; a tervrajz egy prefab, amely további hivatkozások partíciója |

A prefabok egymásba ágyazódnak; egy példány a saját transzformációjának és a szülőjének
szorzatán (sor-vektorokkal) landol, nyolc szintig. Egy objektum-tervrajz a
importált meshei szerint rajzolódik, kihagyva a romboló állapotokat (`dc_...`). Egy
csoportosított prefabra `..._nongroupable_autogen` maradékaként hivatkozunk, így semmi
sem rajzolódik kétszer.

A bejárás csak a pálya világaiból és rétegeiből indul. Egy olyan partíció, amelynek
első példánya egy prefab-tervrajz (`134919fc…`, `0x0247807D`), egy prefab
definíciója, és a pálya sok ilyet tart a saját mappájában, amelyeket a világai más
módon helyeznek el, mint ezek a hivatkozások; ha világként járnánk be, a prefab a
tartalmát a helyi koordinátáira tenné. Ez száz másolatot torlaszolna a világ
origója körül, messze a talaj alatt. A világoknak és rétegeknek a `a10ebe0f…`,
`0xD3D16C3C` az első azonosítójuk.

A játékból kiemelt tervrajzokat nem követjük: a fejlesztési és teszteszközöket
(`game/dev/`, `test/`), a körvégi jelenet készletét (`..._gameend_...`: a talaj
alá rakva), és a halál utáni kamera vezérlőjét (`.../deathflow/...`, amelynek
kellékei a világ origójában állnak). Az eszköz-útvonaluk alapján ismerjük fel őket,
nem a rétegük alapján: ugyanaz a réteg, amely a jelenetkészletet tartalmazza, a
pálya valódi falait és tetőit is elhelyezheti. Mindkét szabály után az ellenőrzött
pályák egyetlen másolata sem fekszik 10 m-nél mélyebben a terep alatt, és a
másolatok ott állnak a terepen, ahol a játék mutatja őket.

**Részletességi szintek, amelyek helyettesítenek.** Egy mesh utolsó részletességi
szintje átválthat egy távoli nézet helyettesítő modelljére saját anyaggal:
`M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Egy rácsos torony több tízezer
háromszögét egy néhány száz háromszögű sziluett zárhatja, amelyet a keret kiválasztana,
és közelről egy tömör tüske lenne. Egy olyan részletességi szint, amely ilyen
anyagot hoz be - amelyet a legfinomabb szintje nem tartalmaz -, soha nem kerül
kiválasztásra; a mesh legdurvább szintje az utolsó valódi.

## Terep {#terrain}

Forrás: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

A terep egy TerrainStreamingTree res (típus `0x22FE8AC8`), és az általa megnevezett
darabok.

| Rész | Elrendezés |
|---|---|
| fejléc | 34 bájt; a csomópontszám a 25-nél |
| raszterfák | egy típusbájt és egy u32 hossz mindegyikhez, amíg a `0xFF` típusbájt nem jön. A 0-s típus a magassági mező: a mintavételek oldalanként a +5-nél (265), a magasságtartomány a +21-nél (1280 m), a terepnégyzet az első csomóponti rekord +77-nél (8192 m az ellenőrzött pályán). Csomópont-határolódobozokat és csomópontonkénti 16 x 16-os min/max piramist tartalmaz, nem a magasságokat |
| streaming-csomópontok | a négyfa, mélységben először: darab mérete és GUID-ja; egy opcionális második darab; egy jelzőbájt (0. bit: a darab magassági oldallal kezdődik); van-e gyermek. A gyermekek sorrendje (0,0), (1,0), (1,1), (0,1) |
| magassági oldal | egy jelzett csomópont darabjának első 265 x 265 u16-ja, sorról sorra; magasság = érték x 1280 / 65535 m; az oszlopok x mentén, a sorok z mentén, a csomópont alsó sarkától; 4 mintás szegély, így csomópontonként 256 cella |

Minden lépést külön ellenőriztek:

- A csomópont-négyfa feldolgozása a res utolsó bájtjáig fogyaszt, a deklarált 529
  csomóponttal.
- A szomszédos csomópontok kilenc szélső oszlopukat pontosan megosztják, így a lépés 256.
- Egy gyermek mintái a szülő minden második pozíciójában pontosan egyeznek a szülőével,
  4-es szegéllyel, és 90-700 egységgel térnek el, bármely más szegéllyel.
- A pályán a legalacsonyabb szó a határolódoboz legalacsonyabb magasságát adja
  vissza a centiméterig.
- A nyolc lehetséges módból, ahogyan a négyzet a világra eshet, csak az x x mentén és
  a z z mentén illeszti a elhelyezett tárgyakat: a mintavett példányok fele 2 m-en
  belül, minden más módnál ennek többszöröse.

Az elhelyezett tárgyak ezután mérik az eredményt. Minden példány legalacsonyabb
pontját a fölötte lévő terephez mérve (bilineáris, a legfinomabb csomópontból):

| Elhelyezett | Medián távolság | Előjeles medián |
|---|---|---|
| fák és bokrok | jóval egy méter alatt | a felszín alatt, kicsivel |
| díszletek | egy-két méter | a felszínen |
| sziklák | körülbelül egy méter | kb. egy méterrel belesüllyedve |
| épületek | több méter (alapzaton állnak) | kicsit belesüllyedve |

A növényzet a talajra kerül, és sehová máshová, ezért ez a legélesebb ellenőrzés:
tövei medián 0,07 m-re vannak a felszíntől. Az épületek széles eloszlása azért van,
mert a kategória falakat, padlókat és többszintes, valamint földalatti szerkezetek
készletdarabjait tartalmazza. A terep 64 m-rel oldalra tolása 29%-ról 10%-ra csökkenti
a 0,5 m-en belüli példányok arányát.

A `level` a magassági mezőt `ground:terrain`-ként rajzolja, minden részét a
legfinomabb csomóponttal, amelynek ott vannak magasságai, és nem finomabban, mint a
`--ground-spacing` (alapértelmezésben 4 m: 3,7 millió háromszög az ellenőrzött
pályán, ahol a legfinomabb csomópontok 0,5 m-esek). Különböző felbontású darabok
kis lépcsőkkel találkoznak; semmi nem varrja össze őket.

A csomópont darabja a magassági oldal után tartalmazza a maszkrétegek oldalait is,
a második darabja pedig a csomópont színtérképével végződik (lásd: [Terepi rétegek](#terrain-layers)).

## Terepi rétegek {#terrain-layers}

A játék egy játékos közelében a terepet úgy árnyalja, hogy felületi anyagokat
keverget festett maszkokkal, egy színtérképpel a tetején, és dekálokat (utakat,
aszfaltfoltokat, kifutójelöléseket) rajzol rá. A Frostbite saját leírása a rendszerről
(Widmark, "Terrain in Battlefield 3", GDC 2012) a terep rasztereit a
magassági mezőként, a shader-keverő maszkokként, egy színtérképként, "amelyet a
shader-keverés fölötti rétegként használnak", fizikai anyagokként, egy rombolási
mélységmaszkként, egy visszaverődő fényhez használt albedó-térképként és további
maszkcsatornákként sorolja fel; egy raszter csempéi szegélyt hordoznak a
renderelési algoritmusok számára. Az ellenőrzött pályák streaming-fájának hét
raszterfája van, 0, 1, 2, 4, 5, 7 és 8 típussal, amelyek fejlécük elején a
csempeméretet hordozzák: 265 a magassági mezőnél (0-s típus) és a 2-es típusnál,
72 vagy 66 a maszkoknál (1-es típus), 132, 2-es szegéllyel a színtérképnél (4-es típus),
260, 2-es szegéllyel az 5-ös típusnál.

**A rétegek listája.** A terep `....layergraphs` res-e rétegenként egy 32 bájtos
bejegyzést sorol fel abban a sorrendben, ahogy a maszkrekordok számozzák (34
bejegyzés, 34 darabszekció és 0-33 közötti rétegindex egy pályán); minden bejegyzés
azonosítója a rétegrajz shader-blokk-depójában (`....layergraphs_shaderblockdepot`)
lévő szekciókulccsal végződik, amelynek blokkja megnevezi a réteg térképeit: egy
`_cv` színtérképet, és felületenként `_nhs` és `_ao` térképeket, plusz megosztott
részlet- és zajtérképeket. Sok rétegnek nincs megnevezett térképe: forrásai, amelyeket
a rétegrajz olvas. Egy réteg színe a `_cv` térképének átlaga; a csempézési méretet
nem találják. A terepi asset tetején rétegenként egy öt bájtos bejegyzés van (egy
bájt, majd egy u32 rétegindex vagy -1).

**A maszkok.** Az 1-es típusú raszterfa a maszkok négyfája. Törzse 59 bájttal kezdődik,
amelynek 0-nál lévő bájtja a lap oldalhossza: 72, ha a lapok BC4-esek (72 x 72,
2592 bájt), 66, ha a nyers nyolcbites (4356 bájt). Ezután csomópontonként egy csoport
jön, mélységben először:

| Rész | Elrendezés |
|---|---|
| csoport | u16; u16 rekordszám; u32 lapszám; a rekordok; egy nulla bájt. A rekord nélküli csoport összesen 7 bájt |
| rekord | 33 bájt: u16 réteg, u16 hash, a negyed doboza (négy float), két jelzőbájt, egy 85 bites jelenléti piramis |

Egy csoport rekordjai a csomópontjának négy negyedét fedik le, rétegenként, minden
réteg negyedei a (0,0), (1,0), (1,1), (0,1) sorrendben. Egy rekord, amelynek a második
jelzője be van állítva, a negyedet egészben fedi, és nincs lapja; amelyiknek nincs,
annak a következő lapja van; a csoport által megnevezett réteg rekord nélküli negyede
üres az adott rétegből; az első jelző pontosan akkor nincs beállítva, ha a réteg a
negyed saját csoportjában folytatódik, egy szinttel lejjebb, amely ott helyettesíti
azt. A lapszám a lapot hordozó rekordok száma.

A lapok: egy streaming-csomópont saját csoportjának lapjai a darabjában következnek a
magassági lap után, egy 4358 bájtos, 16 bites szekció és egy 67 x 67-es, nyolcbites
raszter (ha nincs magassági lapja, a darab elejétől); a második darabja a négy
negyedének csoportjainak lapjait tartalmazza egy szinttel lejjebb, a negyedek a
színtérkép sorrendjében, majd a színtérkép. Egy lap a negyed 64 x 64 texelje, a
sorok z mentén, az oszlopok x mentén, a szomszédoktól másolt szegéllyel: 4 texel BC4
lapon, 1 a nyers lapon. 

A szegélyek bizonyítják az elhelyezést ítélet nélkül: egy réteg két egymás melletti
lapjának egymás szélső texeljeit kell hordoznia. A `read_masks` ezt minden párra
ellenőrzi, amelyet elhelyez, és elutasít egy pályát, ahol kevesebb mint 99% egyezik.
Az ellenőrzött pályák körülbelül egyharmada olvasható, szegélyeik egyezésével; néhánynak
nincs festett maszkja; a többi elutasításra kerül, szinte mindet az ellenőrzés miatt
(a csomópontjaik darabjai többet tartalmaznak, mint amit ez az elrendezés ismer).
Egy elutasított pálya talaja a felületi anyagai középső színét kapja, és az export
megmondja, miért. A teljes negyedet lefedő szegélyek 255-öt, a teljesen üres negyedek
felé nézők 0-t hordoznak.

A lapok előtti 4358 bájtos szekciót és 67 x 67-es rasztert nem olvassák: értékeik
keskeny magas sávban vannak, kis értékek és őrszem nélkül.

**A talaj színe.** A rétegrajz a rétegeket maszkok, lejtő, magasság és zaj
összeállított shader-gráfjában keveri, amelyet nem olvasnak. A `--ground-texture` a
talajt egy saját szabállyal színezi, amelyet itt mint olyat írunk le:

- a távolsági nézet helyettesítőinek színtérképeit megnevező rétegek kimaradnak;
- a terep kilenc tized részét vagy többet lefedő, textúrázott rétegek az alap. Maszkjaik
  szinte mindenhol teltek, így az, hogy hol fekszik mindegyik, a shader választása,
  nem az övék: a szikla vagy szirt nevűek 40 foknál meredekebb lejtőket színeznek,
  a kavics nevűek a sík talajt, a többi alap réteg, ha nincs más, 20 és 40 fok
  között a magassági mező lejtője szerint keveredve (4 m-enként véve és bilineárisan
  szétterítve a sütött texeleken: 4 m-es blokkokban ismételve a sziklás szín
  kemény szélű foltokat rajzolt);
- minden más textúrázott réteg a saját maszkja szerint kerül az alapra, a réteg
  sorrendjében;
- a színtérkép az eredményre kerül úgy, ahogy a motor használja: a talaj színének
  kétszerese a térkép színével szorozva, így a középszürke nem változtat rajta; ahol a
  színtérképnek nincs texele, a talaj a térkép medián fényességét veszi, szürkében.

A játék képkockáinak mediánjához képest ellenőrizve három pályán (a kromaticitás
vörös és kék, zöldhöz képest): a sütött játéktér 1,00 / 0,69, a képkockáké 1,19 / 0,78
az egyiken, amelynek fűrétegei zöldek ott, ahol a képek száraz füvet mutatnak;
1,19 / 0,82 a képkockák 1,01 / 1,04 ellenében egy másikon, amelynek színtérképe
maga meleg (1,13 / 0,88); és 1,05 / 0,91 a 0,93 / 0,92 ellenében egy harmadikon,
színtérkép nélkül. A képkockák megvilágítottak és színezettek, így ez a
árnyalatot méri, nem a fényerőt.

**A színtérkép.** Egy csomópont második darabja a negyedei csoportjainak maszklapjai
után négy BC7 lapot tartalmaz, 132 x 132-est (egyenként 17 424 bájt), a csomópont
minden negyedére egyet, a (alacsony x, magas z), (magas x, magas z), (magas x,
alacsony z), (alacsony x, alacsony z) sorrendben. A maszkfa megmondja, hány bájtot
foglalnak el a maszklapok, így a színtérképet a számlálással találják meg, nem a
darab végével: egy pályán a durvább csomópontok négy ilyen további lapot hordoznak
utána, egy másik raszter egyetlen színnel, és a darab utolsó négy lapjának olvasása
elvesztette a színtérképet a terep kilenc tized részén. E számlálás nélkül a
színtérkép olyan pályákon is hiányzott, ahol a maszklapok nyers nyolcbitesek, és
nem teljes számú BC4 lap; egy pálya színtérképe 0,4-ről 0,94-re javult a terepén.
A sorrend illesztéssel készült: minden negyed magassági mezőjének szélei ellen minden
olyan csomópont lapja, amelynek vannak jellemzői, egy negyedhez illeszkedik,
tükrözés nélkül, 0,3-0,54 értékkel, ahol a következő legjobb elhelyezés 0,2 alatt van.
Ezzel összerakva egy pálya lapjai varrás nélkül illeszkednek az utakba, vízbe és
beépített területekbe az ellenőrzött pályán, 0,5 m-es texelenként a játéktérben. Ahol a
rétegek végzik a munkát, a színtérkép közel semleges (medián 110, 107, 104); máshol
teljes színt is hordozhat. Egy pálya, amelynek második darabjai csak nyers maszklapokat
tartalmaznak, nem olvas színtérképet. Ennek az olvasónak egy korábbi köre ezeket a
lapokat nem földrajzinak nevezte: a háttértérképhez illesztette, amely egészen más
tájat is mutathat, és minden lapot a teljes csomópontjára helyezett a negyed helyett.

**A visszaverődő fény albedója** keresésre került, de nem találták meg: a gyökér- és
első szintű csomópontok darabjai teljes maszklapok, az 5-ös típus adatfolyama pedig
nincs megtalálva.

**Lyukak.** Egy pálya terepi asset-je (res típusa `0x1CA38E06`) három shadert nevez meg:
egy alapértelmezett felületi shadert, egy lyukas felületi shadert és egy alapértelmezett
forrásshadert. Hogy a lyukas shader melyik réteget olvassa, nincs megtalálva, így a
magassági mező nincs kivágva. Egy pályán a navigációs háló futhat több tíz méterrel a
magassági mező alatt lévő sziklamesheken, ahol a játéknak ki kellett volna vágnia
azokat. Ezt keresték, és nem találták: egy réteg maszkját, a 67 x 67-es rasztert, egy
fenntartott magasságot (a pálya egyik magassági lapja sem tartalmaz 0-t vagy 65 535-öt)
és egy csomóponti jelzőt (minden gyökér alatti csomópont 1-es jelzőt visel). A 7-es és
8-as rasztert maradt. Mindkettő futáshossz-kódolt: egy bájt, amely megegyezik az
előzőjével, egy további másolatszámot követ (`ff ff 84` 134 bájt 255-ből). A 7-es
fa (csempe 256, öt szintű teljes négyfa, mintánként négy bit) bájtpárokra dekódolódik,
0-3 értékekkel; a 8-as fa (csempe 265) többnyire 255 bájtokra, más értékei szabályos
sorozatokban. Egyiknek a csempéi sincsenek még elhelyezve, így egyikről sem tudjuk,
hogy a lyukakat tartalmazza-e.

**A dekálokat** beolvassák és sütik; lásd: [Terepi dekálok](#terrain-decals).

## Terepi dekálok {#terrain-decals}

Forrás: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Utak, kifutók, betonfelületek, festett vonalak és betűk, gumiabroncs-nyomok: a
`TerrainDecals` res (típus `0x15E1F32E`) tartalmazza őket, mint lapos geometriát, amelyet
a játék ráterít a terepre.

| Rész | Elrendezés |
|---|---|
| fejléc | a +16-nál egy n darabszám, utána n darab 16 bájtos hely, majd a rekordszám |
| rekordok | rajzolási kötegenként egy, egymás után, változó hosszal: 156 bájt rögzített mező - az első csúcs a +32-nél, a háromszögek száma a +36-nál, a textúra csempézése méterben a +44-nél - majd a köteg csúcsbájtjai (eltolás, méret), majd egy farok, amely a textúráit az eszközük partíció-GUID-jával nevezi meg |
| csúcsok | 32 bájt: x, z (f32), 8 csomagolt bájt, u, v (f32), r, g, b, a (f16); minden köteg sima háromszöglista |
| indexek | u32, kötegenként 0-tól számolva; nem kell |

Ellenőrzések:

- a rekordok csúcstartományai rés nélkül követik egymást, és pontosan lefedik az
  összes csúcsot, és minden rekord első csúcsa x 32 a saját eltolása;
- így olvasva a háromszögek tömör dekálok (betűk, vonalcsíkok, foltok); egy csúcsot
  mellé olvasva a térkép túloldalára nyúló szálak;
- szinte minden köteg megnevez textúrákat a farkában: színtérképet (`_cv`) egy
  átlátszatlanság-térképpel (`_op`, vörös csatorna), vagy jelöléseknél csatornamaszkot
  (`_rgb`).

A textúra-GUID-ek után a farok a köteg anyagparamétereit hordozza, úgy kódolva, ahogy
egy shader-blokké van (lásd lent: Árnyalatok). Egy jelölés, egy gumiabroncs-nyom vagy
egy vonal festékszíne a `607e` hash-ű float3: homokban a gumiabroncs-nyomoknál
homokszínű 0,64, 0,56, 0,48; a kátránynál szinte fekete. Az átlátszatlanság-térképek
többnyire 62-es formátumúak, egy csatorna 8 bájton blokkonként, BC4-ként olvasva.

Egy köteg úgy képezi le a textúráját, hogy vagy a világi pozíció alapján (u = x, v = z,
a textúra minden csempézési méterenként ismétlődik: aszfalt, beton, kavics), vagy 0-tól
1-ig a dekálon át (vonal, betű, gumiabroncs-nyom). A rekordok fájlsorrendben rajzolódnak.

**A sütés.** A `level --ground-texture M` a dekálok kiterjedése alatt, legfeljebb 4096
pixeles csempékben, megfesti a háttér színtérképét (bilineáris), majd minden köteget
ráfest az átlátszatlansága × a csúcs alfája szerint. A csúcsok színét nem használják:
néhány köteg csúcsai tiszta zöldek vagy kékek, amelyek egy pálya jelöléseit ezekre a
színekre festették. A dekálok alatti magassági mező háromszögei `ground:terrain x<x> z<z>`
részekké válnak, a csempét hordozva. Minden köteg így rajzolódik:

| A köteg nevez | Így rajzolódik |
|---|---|
| színtérképet (`_cv`) | a térkép, az átlátszatlansági térképe szerint |
| szorzó-térképet (`_mult`) és átlátszatlansági térképet | a festék (fehér, ha az anyag nem nevez meg egyet) szorozva a szorzó-térképpel, az átlátszatlansági térkép szerint: egy kifutó kopott középvonala, szélvonalai és küszöbsávjai |
| csatornamaszkot (`_rgb`) | a festék, különben fehér vonalaknál és betűknél, sötét körvonalaknál, enyhe elsötétítés a kopásnál, gumiabroncs-nyomoknál, foltoknál, pocsolyáknál és nedvességnél, a maszk szerint |
| csak átlátszatlansági térképet, festékkel | a festék az átlátszatlansági térkép szerint: gumiabroncs-nyomok |

Az úttáblázatos variációs maszk nem festék: a alatta lévő felületet változtatja,
száz méterekre kiterjedően, és nem rajzolódik ki, bármilyen festéke is van. Fehéren
festve két halvány téglalapot rajzolt egy pálya lejtőire, 150-250 m hosszan. A `_mult`
térképet a festék saját kopásának veszik, nem az alatta lévő talaj sötétítésének: közel
fehér, és a vonal alakja az átlátszatlansági térképben van.

Szinte minden köteg rajzolódik, néhány csempébe 0,5 m pixelenként; az export néhány
MB-tal nő, és néhány másodperccel tovább tart. Felülről nézve az kifutók, gurulóutak és
az úthálózat a vegyületek kerítései és épületei alatt fekszenek, és azok kapuiba
vezetnek.

Ha ehelyett geometriaként rajzolnánk őket, az alfakeverést kellene támogatni, amelyet
az író nem visz, és egy terep fölött eltolva összeküzdenének vele; a sütés a
talaj saját színében tartja őket.

## Textúrák és anyagok {#textures-and-materials}

Forrás: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Egy Texture res (típus `0x6BDE20BA`) 180 bájtos fejléc: típus és pixelformátum a +8-nál,
szélesség és magasság a +22-nél, mip-szám a +30-nál, a darab GUID-ja a +40-nél,
tizenöt mip-méret a +56-nál. A darab a mip-lánc, legnagyobbal kezdve. Néhány darabból
hiányzik a legnagyobb mip, amelyek egy nagy felbontású csomagban vannak; a darab
hossza megmondja, melyik mipnél kezdődik. Annak a csomagnak a darabja a +164-nél van
megnevezve; a pálya [kiegészítőiből](#which-table-is-the-level) olvassák, amikor a fő
darabból hiányzó mipre van szükség, és hossza plusz a fő darab hossza adja a teljes
láncot.

| Formátum | Dekódolva mint | Bizonyíték |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineáris) | egy műanyag tartály színlapja így dekódolódik; BC3-ként ugyanazok a bájtok zaj |
| 61, 60 | BC3 | egy láda lapja tisztán dekódolódik BC3-ként, nem BC1-ként vagy BC7-ként |
| 57, 56, 55 | BC1 | fél bájt pixelenként |

A mesh-eszköz nem nevez meg textúrát. A kapcsolat a pálya **shader-blokk-depóiban**
van (res típus `0x73312045`, egy alvilágonként), amelyeket egy mesh-szekció
rekordjának +0x130-nál lévő nyolc bájtja kulcsol:

| Rész | Elrendezés |
|---|---|
| tábla, a 16-nál | (szekciókulcs u64, leíró-eltolás u64), amíg egy eltolás ki nem esik a res-ből |
| leíró | (blokk-eltolás u64, hash u64, blokkméret u64) |
| blokk | a szekció shader-paraméterei; minden textúra egy 49 bájtos rekord: egy bájt, 16 bájt, a textúra-eszköz partíció-GUID-je, és a példány-GUID-je |

A láda szekciókulcsa minden olyan alvilág tíz depójában egyszer megjelenik, amely
elhelyezi, és blokkja megnevezi a `t_mil_crate_03_cs`-t és a `_nmt`-t a megosztott
részlettérképek között. Egy blokk minden textúrát megnevez, amelyet a shader
mintavételez, és hogy melyik a színtérkép, nincs megmondva, ezért kiválasztják: egy
sRGB 2D textúra, amelynek neve az anyag nevének szavai közül a legtöbbet tartalmazza
(`M_ConcreteWall_01`: concrete, wall), majd a mesh nevének szavai közül, majd egy, amely
nem részlet, dekál (`t_de_...`) vagy sérülés-térkép, végül az, amelyet a legkevesebb
blokk használ. Egy közlekedési tábla blokkja megnevezi a panelját
(`t_com_highwaysignage_01_cs`) és egy dekálos lapját (`t_de_com_highwaysignage_01_ca`) egy
oldalára fektetett pajzzsal; mindkettő illeszkedik a szavakra, és a dekálszabály nélkül
a lap nyert használat miatt, és a tábla a pajzsot negyed fordulattal mutatta, a szekció
összes textúrakoordináta-készletén át. Az előjeles távolságmezők (`..._sdf`), palettták
és csatornamaszkok (`_rgb`) soha nem kerülnek kiválasztásra, bármilyen szavakat
osztanak is meg (az `_rgba` térképek viszont kiválasztódnak: többségük szín alfával,
és kihagyásuk egy villanyvezeték és egy lépcső saját térképét más, nem hozzájuk tartozó
térképekre cserélte); egy háttér növényzeti atlasz `..._atlas_a_sdf` színesen rajzolva
fekete-fehér csillagokat mutatott a fákon, egy háttér épületpalettája konfettiként
falakat, és az üvegtörmelék csatornamaszkján át rajzolva ciánná vált. Egy szekció, amelynek
egyetlen jelöltje megosztott részlettérkép, lapos színű marad.

**Palettták.** Egy háttér épületei színüket egy palettából kapják, 256 x 256 texel 16 x 16-os
mintákból: minden csúcs négy bájtot hordoz (használat `0x1E`), amelynek első kettője
megmondja, hol van a palettában a színe, x és y 255-ből. A `level` egy ilyen szekciót a
palettával textúraként rajzol, minden csúcs a mintájának közepén. Így rajzolva egy pálya
háttérépületei pasztell falakká, téglavörös és sötét ablakokká válnak, ahol eredetileg
sima fehérek voltak.

**Átfedések.** A nagy tárgyak egy díszítőlapot csempéznek az első textúrakoordinátáikon
át, és a másodikon át ráterítenek egy átfedést, amelyek a 0 és 1 közt vannak: a tárgy
teljes kiterítése. Az átfedés (`..._overlay_cs`, a maszkjával `..._overlay_a`) azt
hordozza, milyen a tárgy távolról: egy olajtartály piros sávjait és rozsdáját;
a díszítőlappal önmagában rajzolva egy pálya tartályai szürke paneleknek látszottak. Egy
szekció, amelynek blokkja átfedést nevez meg a maszkjával, és amelynek második
koordinátái ilyen kiterítést alkotnak, az átfedéssel rajzolódik rajtuk keresztül (36
szekció azon a pályán).

**Árnyalatok.** Sok színtérkép szürke (csatornáik átlaga 6%-on belül egyforma): a shader
a blokk paramétereiből származó színekkel festi őket. A textúra-bejegyzések (49 bájtosak)
után a blokk felsorolja a paramétereit, mindegyik egy típuscímke (`f11af825` float3,
`a5e1f2de` float4, `c1b1a014` float, `4a4fc3a1` egész szám), a `01 80` jelzőbájtok egy
értékhez, egy kétbájtos hash a paraméter nevéről, egy u32 darabszám, az érték és egy
nyolcbájtos azonosító. A nevek nincsenek tárolva. Hét float3 név-hash árnyalatként
viselkedik: egy pályán hármuk az egyik blokk 6-ból körülbelül egyben tart színt, amelynek
térképe szürke, és szinte soha nincs ott, ahol a térképnek saját színe van; a többiek
azokat a színeket tartják, amelyekkel egy szürke térkép festve van, ha az anyag neve
ezt mondja (egy híd `..._blue` díszcsíkja: 0,047, 0,098, 0,171 a semleges 0,5 ellenében).
Egy család több értéket is tartalmazhat, egy-egy csatornát egy maszkon, a legtöbb
semleges, és egy érték, amelynek egy csatornája szinte semmi (tiszta zöld
téglafrontokon), egy maszk csatornáját választja ki, nem festi. A `level` a szürke
színtérképet lineáris fényben szorozza minden család első értékével, amely sem semleges,
sem ilyen kiválasztó, a semleges értéke fölött, és az eredményt saját textúraként
tartja meg; a színes térkép érintetlen marad. A szabály az exportőré: hogy egy maszk
melyik csatornája melyik árnyalatot kapja, nincs megállapítva. Egy pályán az arányt, amelyet
a szerkezeti háromszögek közeli fehérrel rajzolódtak, 19,4%-ról 3,9%-ra csökkentette.

**Tárgyváltozatok.** Egy mesh több megjelenésben kerül elhelyezésre: egy raktárfal piros
vagy kék csíkkal és más számmal festve, egy konténer zöldben vagy szürkében. Minden
elhelyezett példány megnevezi a megjelenését:

| Hol | Mező |
|---|---|
| statikus modellcsoport-tag | +32: egy egy-mutatós tömb példányonként, tárgyváltozatra vagy nullra |
| objektumhivatkozás | +120: egy mutató egy tárgyváltozatra vagy nullra |
| tárgyváltozat (`ov_...` partíció, típus `235f2a9c...`) | az első példány +32-nél: a változat u32 név-hash-e |

Egy szekció megjelenése egy változatban az a shader-blokk, amelyet a szekció saját
kulcsa határoz meg, a változat hash-ével megnövelt első négy bájttal, kis-endián u32-ként
(`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); az a szekció, amelynek nincs
blokkja e kulcs alatt, minden változatban ugyanúgy néz ki. A pálya mesh-változat-adatbázisai
(`meshvariationdb_win32`) mesh és változat-hash szerint sorolják fel, hogy melyik
anyagokat érinti az egyes változat, de nem a kulcsokat. A szabályt magukból a kulcsokból
találták meg, és minden ellenőrzött változatos szekciónál igaz (egy fal négy változata,
mindegyiknek három szekciója). Egy változat blokkja saját textúráit is hozza, mint a
színeket: a falra festett szám egy betűlap, amelyet a változat blokkja nevez meg.
A megosztott csoportosított példányok nagy része változatban van elhelyezve.

Egy blokkot egyszer sütnek minden tartalmi halmazra, és a kulcs bejegyzése hash-t hordoz
róluk (a bejegyzés második u64-je). Ahol egy szekciónak nincs blokkja a változatának
kulcsa alatt, a változat ettől még eléri egy *ikerpárján* keresztül: egy másik szekción,
amelynek alapértelmezett blokkja ugyanazt a tartalmat hordozza, és van blokkja. Ikerpárok
nélkül egy fal, amelynek hosszai egy alapértelmezett blokkot osztanak, két színben
jelenhetne meg. Egy változat nélküli szekció azt a változatot veszi, amelyet a legtöbb
ikerpárja visel.

**Rombolható meshek.** Egy mesh, amelyet egy meccs le tud dönteni, a saját nevével
rombolási eszközzel rendelkezik mellette (`.../br_x.destruction` a `.../br_x_mesh`-hez):
a rombolható épületek és falak (`br_`) és sok tárgy. A `level` felületeiket saját
részekben tartja, ` (destructible)` névvel, amelyek glTF-csomópontjai hordozzák a
`{"destructible": true}` jelölést. Romboló állapotaik a mellettük lévő
`dc_..._part<N>_mesh` meshek, mindegyik a saját origója körül; hogy hol ülnek, az a
rombolási eszközben van, amelyet nem olvasnak, így a romboló állapotok nem exportálódnak.

**Kimarad.** Helyőrző tömbölő anyagok szakaszai (`M_Whitebox`: néhány nagy, textúrátlan
háromszög, amelyet egyes épületek a felületeik mellett tartanak, és amelyek uszonyként
álltak ki egy pályából), kinematikának készült meshek (egy helikopter, ahol a jelenete
kezdődik) és fényvilágítási segédek (fényt blokkoló síkok, soha nem rajzolódnak).
Egy pálya generált háttérépületei (`..._generated_blueprints_..._mesh`) rajzolódnak, de
falaik anyagnevei csak zajtérképeket neveznek meg, és csúcsaik nem hordoznak színt, így
simák maradnak. Szinte minden rajzolt szekció kap színtérképet.

**Betűlapok.** Egy fal festett száma vagy egy daru reklámtáblájának nyomata külön szekció,
amelynek színtérképe egy lap (`_ca`): egy betű alfája tömör festék fölött, vagy egy nyomat.
Első textúrakoordinátái csempézik a fal vakolatát a panel felett (u -0,2-től 1,7-ig egy
falon), ami majdnem kétszer rajzolja a lapot; a negyedik készlet (`0x24`, különben a harmadik,
`0x23`) egyszer, pontosan rárakja (u -1-től 0-ig, v 1-től 2-ig, néhány ezredrésszel
túl a durvább részletességi szinteken). Ahol az első készlet a kép egy példányát hagyja,
a negyedik vagy harmadik pedig egyen belül van, a lap azon keresztül rajzolódik, 0 és 1
közé mozgatva. Egy alfás lap 1 cm-rel a felület előtt rajzolódik, amelyre festették, és
ez a felület a blokk másik színtérképével, az első készleten át rajzolódik alatta: enélkül
a lap üres texelei a fal belsejét mutatták.
A második készlet egy tárgy kiterítése az átfedéséhez, és itt nem használják.

**Kivágási térképek.** A színtérkép negyedik csatornája a térkép neve szerint mást jelent.
A `_cs` névnél, messze a leggyakoribb (893 kiválasztott térkép egy pályán), ez a simaság:
egy medián térkép alfájának 1%-a 0,1-en belül van 0-hoz vagy 1-hez. A `_cu` (levelek, fű)
és `_ca` (szín és alfa) esetén az átlátszatlanság: 90%, illetve 87%. Egy `..._cu` vagy
`..._ca` nevű színtérkép, amelynek alfája legalább 75%-ban 0 vagy 1 közelében van, legalább
1%-ban 0,5 alatt, és legalább 5%-ban felette, alfájával együtt íródik, PNG-ként, az
anyagát pedig glTF `alphaMode` MASK, `alphaCutoff` 0,5, kétoldalú jelöléssel; így a
lombkorona-kártyák leveleket mutatnak, nem a sarkaik fekete részeit. Egy fa levéltérképének
nincs alfája egyáltalán (legfeljebb 4 a 255-ből): a levelei geometriával vannak
kivágva, és csak az első két feltétellel az egész lombkorona eltűnt volna.

A textúrakoordináták a `0x21` használatú csúcsok, két félszó (6-os formátum) vagy két lebegőpontos
érték (2-es formátum). A szekciók további három készletet hordoznak (`0x22`-től `0x24`-ig) dekál-
és részletrétegekhez. A koordináták csempéznek: egy konténer bordázott oldala -1,6-tól 1,8-ig
fut, a háttérterep csempéi teljesen a 0..1-en kívül esnek, és egy pályán a texturált
háromszögek 23%-a 0..1 közé kívül esik. Úgy íródnak, ahogy vannak, ismétlődő mintavételezővel;
a 3DHeat megjelenítő minden ismétlődő textúrát az atlaszán belül csomagol. Egy megjelenítő,
amely helyette szorítja őket, a bordákat kétszeres szélességűre nyújtja, egy betonpadlót
csíkossá tesz egy tengely mentén, és egy torony acélgerendáinak textúrája szélének színét
kapja; ennek `--clamped-uvs` vágja szét minden háromszöget ott, ahol a textúra ismétlődik,
és 0..1 közé mozgatja a darabokat (lásd: [Kimeneti formátum](output-format.md)). Ezután a
texturált háromszögek 0,03%-a, amelyeken a textúra 16-nál többször ismétlődik, kívül esik, és
az a háromszög, amelyet a vágás 4-nél több darabra bontana, a textúra átlagszínével rajzolódik:
a kéreg minden ágon ismétlődik, és vágva egy pálya fái 6,4-ről 24 millió háromszögre nőttek.

A magassági mezőnek nincs saját színtérképe, amelyet ki lehetne olvasni. Ahol a háttérterep
egyik térképe lefedi, az innen színeződik: a háttér textúrakoordinátái a világ x és z
lineáris függvényei (a csúcsok 99%-a 0,001-en belül ettől), a térkép egy 65 536 m-es
négyzetet fed, negyedfordulattal. Ugyanez a függvény adja a magassági mezőét. A szint
a térkép mipjeit 2048 px-től lefelé szállítja, így a magassági mező 32 m pixelenként
kap. A sziklás, sötét része a meredek talajon van: a sötétség és a lejtő korrelációja 0,48,
a másik hét tájolásnál legfeljebb 0,34.

Egy másik pálya háttere nyolc közeli és nyolc távoli csempe a játéktér körül, mindegyik
a saját textúráját ismétli a csempe teljes felületén, és egyik sem éri el a magassági
mezőt. Minden háttértextúrát külön illesztenek, és ha egyik sem fedi a magassági mezőt,
az átlagszínt veszi, amelyet a háttér mutat a terepnégyzettől egy kilométeren belül;
ezzel sül a `--ground-texture` a dekálokat. Háttéranyag az, amelynek nevében `TerrainBackdrop`,
vagy `BD_` és `Terrain` szerepel (`M_BD_<site>_Terrain..._Near`); vagy egy háttér-mesh
(`bd_..._terrain<site>_04_far_mesh`) egy sima terepanyagot hordoz (`M_<region>_Terrain<site>_04_Far`),
amelyet az első két szabály egy pályán elszalasztott, így a talaját a felületeiből színezte volna.

Ahol nincs háttértérkép, amely lefedné a magassági mezőt, az a terep saját felületeinek
középső színét veszi, a háttér átlaga előtt: a színtérkép-kiválasztásokat, amelyeket a
rétegrajz shader-blokkjai neveznek meg (27 egy pályán: homokok, kavicsok, talajok, fű,
repedezett beton), mindegyiket átlagolva, majd csatornánként a mediánt véve, a motor
alapértelmezett felületét kihagyva. Egy háttér lehet egészen másik táj: egy pályán az
átlaga (sRGB-ben 95, 99, 80) a játéktér talaját olyan szürkévé tette, amelyet a játék nem
mutat. A `--ground-texture` esetén ez a szín a színtérkép kétszeresével szorzódik, amit
a középszürke nem változtat, és a dekálokkal együtt sül, mindkettő kiterjedésén át.

A játékhoz mérve a játéktérként sütött talaj és a játék képkockáinak mediánja pályánként
(a képkocka a HUD melletti kép 55-72%-os sorai, képkockánként 24; sRGB; a képkockák
megvilágítottak és színezettek, így az arányok r/g és b/g a méltányos összehasonlítás):

| Pálya | Képkockák | A háttér átlaga | Most |
|---|---|---|---|
| első | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| második | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| harmadik | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Az elsőt helyreállították; a másik kettő korábban kicsit közelebb volt az árnyalatban. Egy
színt egy egész pályára nem lehet mindenhol helyesen alkalmazni; a maszkok lehetnének.

## Navigációs háló {#navigation-mesh}

Forrás: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Egy pálya ágensenként egy partíciót szállít, `<level>/dbt/<level>_navmesh_layer_<n>` néven:
egy pályán a 0. réteg a katona (1,8 m magas, 0,18 m lépcsőmagasság, 0,4 m sugár), két másik
pedig járművek (3,5 és 10 m magasak). Minden partíció két tömböt tartalmaz:

| Tömb | Elem |
|---|---|
| csempék | 28 bájt: u32 0, u32 hash, u32 0, u32 darabindex, u16 csempe x, u16 csempe z, u32 eltolás, u32 méret |
| darabok | 20 bájt: a darab GUID-ja, u32 méret |

Egy csempe `size` bájt a `offset`-nél a `chunk index` darabban, kis-endián, és a Detour
(Recast Navigation) szerint van elrendezve egy hosszabb fejléc mögött:

| Eltolás | Tartalom |
|---|---|
| 0 | `VAND`, 7-es verzió |
| 24 | számlálók: poligonok, csúcsok, linkek, részleges hálók, részleges csúcsok, részleges háromszögek, térfogati csomópontok, lekapcsolt linkek, az első lekapcsolt poligon |
| 188 | az ágens magassága, lépcsője, sugara |
| 200 | a csempe határolódoboza, hat float |
| 232 | csúcsok: x, y, z floatok, világi koordinátákban |
| következő 8 bájtos határ | poligonok, 32 bájt: u32, hat u16 csúcsindex, hat u16 szomszéd, u16 jelzők, a csúcsszám a +30-nál, a +31-nél a terület (alsó hat bit) és a típus (felső kettő) |
| utána, tömörítve | linkek (16 bájt), részleges hálók (12: első részleges csúcs u32, első részleges háromszög u32, csúcs- és háromszögszám u8), részleges csúcsok (három float), részleges háromszögek (három index és jelzők), térfogati csomópontok (16), lekapcsolt linkek (80) |

Minden ellenőrzött pálya minden csempéjében ezek bájtra pontosan kiadják a csempe méretét,
és a részleges hálók az első lekapcsolt poligon előtt számozzák a poligonokat.

Egy poligon sík a sarkai között; a **részleges hálója** tartja a felület valódi magasságát
a dudorok, sziklák és lépcsők felett, és ez az, ami rajzolódik. Egy részleges háromszög
indexe, amely a poligon sarokszámánál kisebb, azt a sarkot jelöli, különben a részleges
csúcs `first + index - corners`. A poligonok legyezése helyett ez sokkal több háromszöget
tesz a terep alá, és hosszú csíkokat hoz létre; a részleges hálókkal egyik sem hosszabb egy
16 m-es csempe átlójánál, plusz a lejtő lépcsőmagasságánál.

A 0-s típus a talaj, a 2-es típus kis meredek foltok (körülbelül 45 fok, egy négyzetméterenként),
az 1-es típus egy kapcsolat két felület között: sarkai 125 m vagy több magasságot ölelnek át,
és a csempén kívül esnek, néhány az origóban. A linkek kimaradnak; a többit a részleges
hálóik rajzolják, vagy legyezve egy csempében, amelynek nincs ilyenje.

Ellenőrzések: a darabok méretei pontosan összeadódnak a csempékével; minden felületi csúcs
a csempéje dobozán belül van, egy méter erejéig; szinte minden háromszög felfelé néz.
Egy sikertelen csempe elutasításra kerül és számolódik, és abban a pályában egy sem sikertelen.

Ami a katona hálójával lefedett, az a teszt pályán felülről nézve: a talaj, padlók, lépcsők és
néhány tető, és nem a konténerek tetői. Ez a katonák számára a helyek térképe, ahol egy
katona állhat, a fájlok legközelebbi megfelelője ahhoz, ahol a játékosok állnak.

## Nincs megvalósítva {#not-implemented}

- A terep rétegrajza, amely összekeveri felületi rétegeit (lásd: [Terepi rétegek](#terrain-layers)):
  a talaj színe ennek az olvasónak a saját szabályát követi a rétegek maszkjaiból és a
  magassági mező lejtőjéből, és azok a pályák, amelyeknek maszklapjai nem illenek össze,
  egy színt kapnak.
- Dekálanyagok színparaméterei: a csatornamaszkon át festett jelölések semleges színnel
  festettek.
- Nem mesh objektum-tervrajzok (játéklogika, effektek, hangok).
- Rombolható meshek romboló állapotai: helyük a rombolási eszközben van, amelyet nem olvasnak.
- A navigációs háló linkjei (ugrások, létrák, átmászások) és járműrétegei.
- A res-ben beágyazott mesh-szintek (10 mesh egy pályán, kellékek), csontozott és összetett
  meshek csontjai és részei, és a normálok (az író számolja).
- Normál-, érdesség- és más térképek; az átlátszóság a kivágási térképen kívül (az üveg és
  az átlátszó dekálok átlátszatlanul rajzolódnak).
- Terepi lyukak: egy lyukas felületi shader van megnevezve, de az általa olvasottat nem találták
  meg (lásd: [Terepi rétegek](#terrain-layers)), így a magassági mező nincs kivágva ott, ahol a
  járható talaj alatta fut.
- Az anyag színmaszkjának melyik csatornája melyik árnyalatot kapja: egy szürke színtérkép az
  első nem semleges árnyalatot kapja (lásd: [Textúrák és anyagok](#textures-and-materials)).
- Effektek (`fx/` útvonalak) és a kábel-meshek, amelyek határolódobozai tíz kilométer hosszúak;
  kimaradnak, és az összesítésben meg vannak számolva.
- A XOR-obfuszkált táblázatforma.
