---
title: Forza Horizon
nav_order: 1
lang: "hu"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Pályaexportálás: Forza Horizon {#course-export-forza-horizon}

A Forza-export a pályát közvetlenül a játék ForzaTech-archívumaiból olvassa ki:
terepet, ahol az úttest, a szegély és a fű külön van választva, talajtextúrát,
amelyet a játék saját talajtérképeiből sütnek, és minden elhelyezett modellt a
saját textúrájával (szegélyek, korlátok, gumifalak, táblák, díszletek, épületek).
Megkeresi azt is, hogy a játék melyik versenyén hajtották a kört, és hozzáadja,
amit a játék azért a versenyért ad ki (eseményrétegét: korlátok, sátrak,
portálok, lelátók, zászlók), valamint annak a helyszínnek a talaját, amelyen a
verseny áthalad, például egy stadion padlóját.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Források: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
A tárolóformátumok maguk a [ForzaTech](reader-forzatech.md) oldalon vannak.

## A telepített játék megtalálása {#finding-the-installed-game}

Senkinek sem kell beírnia egy ilyen elérési utat, mint
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, ezért az utat a program
kitalálja:

1. **Steam-könyvtárak.** A Steam `config\libraryfolders.vdf` fájlját olvassa a
   `C:\Program Files (x86)\Steam` vagy a `C:\Program Files\Steam` helyről, és a
   benne lévő minden `"path"` bejegyzés egy könyvtár. Minden könyvtár
   `steamapps\common` mappáját átkutatja.
2. **Microsoft Store.** A `C:\XboxGames` mappát kutatja, ha létezik. Ott a játék
   eggyel lejjebb van, a `<game>\Content` mappában.
3. **Játékmappa** bármelyik ilyen mappa gyermeke, amelynek van `media\Tracks`
   mappája, bármilyen nevű is.
4. **Pályamappa** minden olyan mappa a `media\Tracks` alatt, amelyben van
   `GeoChunk0.minizip`. A tartalma alapján ismeri fel, nem a neve alapján, így egy
   olyan pálya is megtalálható, amelynek neve még senki nem látott.

Ha a játék máshol van, add meg a pályamappát a `--track` kapcsolóval; lásd:
[Hibaelhárítás](troubleshooting.md#finding-the-game) ("no installed Forza track found").

A `--track <folder>` mindezt kihagyja.

Egy pályamappában az van, amit az export olvas:

| Fájl | Mi ez |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | az archívumok: minden modell-, textúra- és elhelyezési fájl, név nélkül |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | soronként egy archívum-bejegyzés, a bejegyzések sorrendjében: az egyetlen forrás a nevekhez |
| `AssetManifest.xml` | minden textúra, amelyet a pálya szállít, azzal a hash-sel, amellyel az anyagok hivatkoznak rá |

## Melyik pálya {#which-track}

A játék egynél több pályamappát szállít (a nyílt világú térkép, egy-két garázs).
A megfelelő pályát **koordináták alapján, nem név alapján** választja ki:

- A kör határolódoboza, a `--margin` értékkel kiterjesztve, a kérdés.
- Minden pályamappához a négy `ChunkContentsMiniZip*.txt` jegyzék szövegként
  olvasódik, archívum megnyitása nélkül. Minden terepcsempe-név
  (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) hordozza a rácspozícióját.
  Az eszköz megszámolja, hány különböző csempe esik a dobozba.
- Az a pálya nyer, amelyiknek ott a legtöbb csempéje van. Ha egyiknek sincs, az
  export megáll ezzel: "none of the installed tracks (...) has terrain at x ..., z ....
  Those are the game's own metres, as its telemetry reports them."

Egy egész pálya kevesebb mint egy másodperc alatt válaszol. Egy névegyezés rossz
térképet is választhatna, és a rossz térkép ugyanolyan hihetőnek látszik, mint a
helyes.

A konzol kiírja: `on <track>, in <game folder>`.

## Melyik verseny {#which-race}

A játék minden versenyét egy számmal ellátott útvonalként szállítja, az
**útvonal-azonosítójával**. Két fájl tartozik minden útvonalhoz:

| Fájl | Mit tartalmaz |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | a verseny AI-vezetési vonala: egy 56 bájtos csomópont a `0x60` bájttól, a csomópontok száma a `0x24`-nél, minden csomópont a pozíciójával kezdődik (x, y, z) a játék méterében |
| `media\Stripped\gs\<map>\routedefinitions.zip` | versenyenként egy `route<id>_<map>.rtd`: sima XML, amely felsorolja, mit ad hozzá a verseny a világhoz, és mit vesz el tőle (lásd: [A verseny saját rétege](#the-races-own-layer)) |

A kört egy útvonalhoz úgy illesztik, hogy összehasonlítják minden AI-vonallal,
amelynek dobozai átfedik a kör dobozát:

- Minden körpontból a vonal legközelebbi pontjának távolsága; és a vonal
  minden pontjából a legközelebbi körpont távolsága.
- A két medián összeadódik. Az az útvonal nyer, amelynek az összege a **30 m**
  alatt van (`MATCH`).
- Mindkét irány szükséges: egy rövid sprint egy hosszú verseny mentén fekszik,
  ha ugyanazon az úton halad, és egy hosszú kör lefedi a rövid útvonalat.

A konzol kiírja: `the game's route <id> (driven line within <n> m of it)`, vagy
azt, hogy nincs illeszkedő útvonal. Illeszkedés nélkül csak a szabad mozgású világ
kerül elhelyezésre.

## Terep {#terrain}

Hogyan találja meg a terepet (a `forzaterrain.py`-ban):

- A jegyzékek a terepet térbeli indexként nevezik meg:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- A két szám rácskoordináta, amely **1023-asával lép**, és minden rácslépés egy
  **512 m-es** csempe. Az `x-2046` csempe `-2046 / 1023 = -2`, ami `-2 * 512 = -1024` m-nél
  kezdődik. Ha a neveket méterként olvassuk, minden keresés kétszeres tévedéssel
  tér vissza, és továbbra is ad terepet, csak a térkép rossz részéről.
- Egy csempe háromszor is megjelenhet: sima, `_cb` és `_ul` alakban. Mindhárom
  ugyanazt a földet fedi le. Csempénként egyet vesz, ebben a preferencia-sorrendben,
  mert az összevonásuk háromszorozná a geometriát egymásra eső felületekké.
- Egy csempét csak akkor olvas, ha érinti a kör dobozát **és** a folyosót. Amelyiket
  a folyosó nem érinti, azt soha nem tömörítik ki.
- Egy kiválasztott csempe minden `.modelbin`-je csak a **0. részletességi szinten**
  dekódolódik. Egy csempében négy szint van ugyanarra a talajra, és mindet
  exportálni ugyanazt a négyzetmétert négyszer tenné a fájlba.
- Minden mesh a saját világi skáláját és eltolását hordozza, így a csempe a játék
  által adott helyén landol, példány-transzformáció nélkül. A háromszögek, amelyek
  lábnyoma átfedi a dobozt, megmaradnak, majd csak azok, amelyek a folyosóig érnek.
- Az olvasó által nem értett formátumú mesh kimarad és megszámolódik
  (`N meshes could not be read`), így egy gyér eredmény megmagyarázza magát.

A terepösszesítő kiírja a csúcsok számát, a háromszögek számát, a meshek számát, a
csempék számát és az x/y/z kiterjedést.

### Út, szegély, terep, jelölések, víz {#road-verge-terrain-markings-water}

Az anyagnevek nem mondják meg, hol van az út. Egy pálya körül a talajnak 94%-a
úttest-shader anyagot használ, mert az úthoz közeli terepet azzal rajzolják, és a
shader pixelenként dönti el az aszfaltot vagy a füvet. Így:

| Típus | Ez dönti el |
|---|---|
| úttest-csík | a **csúcs-elrendezés**: az úttest-csíkok az egyetlen talaj, amelynek van második UV-készlete (1-es csatorna); az a háromszög, amelynek mindhárom csúcsán van, út |
| aszfalt vs. szegély | egy úttest-csíkon belül a csempe **aszfaltmaszkja** a háromszög súlypontjánál: 0,5 vagy több az `road`, kevesebb a `verge` |
| jelölések | anyagnév egyezése: `whiteline`, `yellowline` vagy `decal` |
| gumiabroncs-nyomok | anyagnév egyezése: `tyremark` vagy `skid` (a jelölések előtt ellenőrizve, mert a gumiabroncs-nyomok `tyremark_decal_*` néven szállítódnak) |
| víz | anyagnév egyezése: `water`, `lake`, `river`, `paddy`, `ocean` vagy `sea` |
| terep | minden más |

A pálya rögzített köreinek mérésével a minták szinte mind úttest-csík
háromszögekre esnek, és a nagy többség az aszfalt részre, miután a maszk
leválasztotta a szegélyt.

Az aszfaltmaszk csak akkor létezik, ha a talajtextúrák sütve vannak. A
`--no-textures` kapcsolóval, vagy egy olyan csempénél, amelynek a térképei
hiányoznak, az úttest-csíkok egészben maradnak `road` néven, és nincs leválasztott
szegély. A hiányzó térképek részletességet, soha nem geometriát veszítenek el.

### A festett rétegek felemelése {#painted-layers-are-lifted}

A sávjelölések és a gumiabroncs-nyomok saját háromszögként szállítódnak, amelyek
pontosan az úttesten fekszenek. A játék mélységi eltolással rajzolja őket. Ha
úgy rajzolnánk ki őket, ahogy vannak, az út és a festék minden pixelért
versengene. Az export minden jelölés- és gumiabroncs-nyom-résznek a saját
másolatot adja a csúcsaiból, **5 cm**-rel (`DECAL_LIFT`) megemelve a felületi
normál mentén, így az alatta lévő út nem emelkedik fel vele.

### Normálok {#normals}

A terep normáljait az archívumból kapja. A normál x-e a pozíció negyedik rövid
egésze, az y és z a `NORMAL` attribútumban (lásd: [ForzaTech](reader-forzatech.md)).
Ha a kinyerésben bármelyik csúcsnak nincs normálja, az egész talaj normáljait a
háromszögekből számolja.

## A talajtextúra {#the-ground-texture}

Minden terepcsempe három térképet szállít, amelyek lefedik az 512 m-es négyzetét,
öt felbontásban (`_quality1` - `_quality5`, a legnagyobb 2048 px, ami 25 cm
pixelenként):

| Térkép | Fájlnév-minta | Mit tartalmaz (mérés szerint) |
|---|---|---|
| fő | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: részletes normál (x, z). A: alacsonyabb az aszfalton és a durva talajon |
| al | `submap_x<X>_z<Z>_x<season>x_diff` | réteg-súlyok. B: magas az aszfalton (239 a vezetett vonalon, 165 mellette) |
| fény | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: alacsony az aszfalton (147 vs. 215). B: emelkedik az erdőben |

Egyik sem színes fénykép. A játék terepshaderének bemenetei, amelyekkel az
anyagrétegeit keveri, és ezek a rétegek nincsenek visszafejtve. Így a sütött
textúra **értelmezés, nem a játék képének másolata**. Megőrzi, *hol* van minden
fajta talaj, 25 cm-en, és rögzített színekkel festi ki:

| Talaj | Lineáris RGB | Súly |
|---|---|---|
| fű (rövid, a pálya közelében) | 0,30; 0,44; 0,18 | az alap |
| durva (távolabb) | 0,40; 0,42; 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| erdő | 0,13; 0,23; 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| aszfalt | 0,20; 0,20; 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Az aszfalthoz mindkét térképnek egyeznie kell. Ha csak az egyik van, a fűben
szürke szemcsézés marad ott, ahol a blokktömörítés gyűrűket húz. Az eredmény a
fő térkép részletes normáljával árnyalódik egy rögzített fényhez képest
(`0.55 + 0.6 * lambert`), így a szegélyek, a partok és a kerékvágások
domborzatként hatnak, és 8 bites sRGB-ben íródik ki.

Tájolás: a képpont 0. sora a csempe **északi** széle (a legnagyobb z), 0. oszlopa
a **nyugati** széle (a legkisebb x). Ezt úgy találták meg, hogy a rögzített köröket
rávetítették az aszfaltmaszkra mind a nyolc módon, ahogyan egy négyzet tükrözhető
vagy foroghat. Pontosan egy mód helyezi őket aszfaltra. Az UV-k ebből következnek:
`u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

A térképeket a legjobb rendelkezésre álló felbontásban olvassa, az 5-ös minőségig,
és a fő térkép méretére mintavételezi újra. Ha a színkép nagyobb, mint a
`--texture-size`, akkor Lanczos-szűréssel arra a méretre kicsinyíti. Az aszfaltmaszk
mindig teljes felbontásban marad, mert a geometriáról dönt. A `--season` az
`x<season>x` térképeket választja ki. Ha egy csempének nincs térképe az adott
évszakra, lapos színnel rajzolódik ki, és a konzol kiírja: `N without maps`.

## Elhelyezett modellek {#placed-models}

A terep saját világi pozícióval rendelkezik. Más nem. Hogy egy modell minden
példánya hol áll, azt a `.pgeo` elhelyezési fájlok rögzítik, kategóriánként és
térbeli cellánként egy: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`.
A rekordok elrendezése a [ForzaTech](reader-forzatech.md#placement-files-pgeo) oldalon van.

### Mi olvasódik {#what-is-read}

- Az elhelyezési fájlokat **név szerint** szűri: az útvonal cellamérete és
  cellapozíciója adja a cella négyzetét (`x * size` - `(x + 1) * size`), és csak
  azok a cellák nyílnak meg, amelyek átfedik a kör dobozát, és kívánt kategóriába
  tartoznak.
- Alapértelmezésben a kategóriák: `barriers`, `props`, `signs`, `buildings`,
  `infrastructure`, `bridges`, `rocks`, `evolving`. A `--trees` hozzáadja a
  `trees`, `bushes` és `smashables` kategóriákat. Ezeket soha nem olvassa:
  `grasstemplate`, `crowdtemplate` és `cwdspline` (fű és nézők: a játék animált
  spriteként rajzolja őket, nincs geometriájuk).
- Minden fájl egy **rétegbe** tartozik, amelyet a nevéből olvas a
  `c<size>_<category>_` után. Egy részletességi szintet jelölő szó (`do`, `so`,
  `ulc`, `ulp`, `cwd`) és egy opcionális szakaszszám a szabad mozgású világ.
  Minden más egy réteg, amelyet a játék bekapcsol: futásidejű réteg (`rt_0`), tevékenység
  (`_tag_<name>_`), gyűjthető, vagy bármi, ami az `evolving` alatt van. Az a réteg,
  amely útvonalakat nevez meg (`rt_x<id>`, például `rt_x1023_x2201`), csak azokra a
  versenyekre tartozik, és csak akkor olvasódik, ha a kör illeszkedett egyikükre.
  Lásd: [Bekapcsolt rétegek](#switched-on-layers).
- Egy másolat megmarad, ha a pozíciója a dobozon és a folyosón belül van. A pontos
  ismétlések (ugyanaz a pozíció és irány a milliméterig, két szomszédos cella is
  felsorolja) összevonódnak.
- A **szegélyek** azok a díszletek, amelyek modellneve `road_gen_rum` (rezgősáv)
  kezdetű. Úgy íródnak, mint `ground:kerbs`, soha nem egyszerűsödnek és soha nem
  maradnak ki, mert a kört hozzájuk mérik.

| Kategória | Rész | Tartalék szín (nincs textúra) |
|---|---|---|
| szegélyek | `ground:kerbs` | 0,60; 0,12; 0,10 |
| korlátok | `structure:barriers` | 0,50; 0,50; 0,50 |
| díszletek | `structure:props` | 0,45; 0,35; 0,25 |
| táblák | `structure:signs` | 0,70; 0,70; 0,70 |
| épületek | `structure:buildings` | 0,55; 0,52; 0,48 |
| infrastruktúra | `structure:infrastructure` | 0,45; 0,45; 0,47 |
| hidak | `structure:bridges` | 0,45; 0,45; 0,45 |
| sziklák | `structure:rocks` | 0,30; 0,28; 0,25 |
| összetörhető tárgyak | `structure:smashables` | 0,12; 0,22; 0,06 |
| fák, bokrok | `structure:trees` | 0,10; 0,20; 0,05 |

### A modell geometriája {#the-models-geometry}

Egy elhelyezett `<model>_3D` név a `<model>_cluster###.i.modelbin` modellfájlokra
utal (legfeljebb tucat). Minden háromszög hordoz egy maszkot azokról a
részletességi szintekről, amelyekhez tartozik:

- Egy modell szintjei a háromszögei, amelyek kifejezetten az adott szinthez vannak
  jelölve. A szintek 0-tól folytonosan futnak, a legfinomabbal kezdve.
- A `0xFFFF`-del jelölt háromszögek (minden szint) a törhető darabok, például egy
  korlát oszlopai vagy egy gumiabroncs-torony egyes gumijai. Az egész modell fölött
  átfedik egymást, és a játék ezeket rajzolja a modell helyett, amint az szétesett.
  Csak olyan modell használja őket, amelynek nincs kifejezetten jelölt szintje.
- A **dekal**-árnyékoló anyaggal rendelkező részmeshek kimaradnak.

Minden példány a pozíciójával, az x és y tengelyével a rekordból (z = x kereszt y)
és a skálájával kerül elhelyezésre. A normálok az inverz skálával transzformálódnak.

### Melyik textúra {#which-texture}

Egy anyag nem nevezi meg a textúráit. Hash-ekként sorolja fel őket, a pálya
`AssetManifest.xml` fájlja pedig minden hash-t (`SourceHash`) egy textúranévhez
rendel. Csak a `<Textures>` szakasz olvasódik, és a `</Textures>`-nél áll meg, egy
olyan fájlban, amely tíz megabájtos is lehet. Ezután:

1. A `0x88B483AA` foglalat az alap színe a szabványos környezeti shaderben (minden
   mintavételezett anyag). Ha az anyag ide köt textúrát, azt használja.
2. Különben a textúra saját típusa dönt, az a szó, amely a GUID előtt áll:
   `_bclr_`, majd `_diff_`, majd `_colour_`.
3. A terep-térképek (`mainmap`, `submap`, `autogloss`) és a színpalettták (`tint`,
   `worldtint`) soha nem színezik a modellt.

Tehát egy modell azt kapja, amit az anyaga köt, nem azt a textúrát, amelynek neve
hasonlít a modellére. Például a `bar_rur_armco_crct_02_c` a `..._02_a` textúráját
használja.

A textúra az archívumokból olvasódik a legkisebb olyan felbontásban, amely legalább
**256 px** széles (`MODEL_TEXTURE`), és 256-ra kicsinyítve, ha nagyobb, és `.glb`-ben
RGB JPEG-ként tárolódik. Egy korlát színe 256 px-en négy méterre 1,6 cm pixelenként,
és nagjából 80 ilyen textúra fér el a megjelenítő atlaszában a talajcsempék mellett.

**Évszakok.** A `--season` a textúrát annak évszakos párjára cseréli a neve alapján,
a GUID figyelmen kívül hagyásával (`..._xsummerx_bclr` - `..._xwinterx_bclr`, vagy
`..._bclr` - `..._winter_bclr`), ha a pályának van ilyen. `--season winter` esetén
egy részmesh téli anyagát is használja, ahol a variánstáblája megnevez egyet.

**Variánsok.** Egy részmesh-rekord egy `(summer, winter)` anyagpárokból álló
táblával kezdődik, minden megjelenéshez egy: öt nyomat egy reklámtáblához, hat
festékszín egy gumiabroncs-toronyhoz. Minden elhelyezési rekord megmondja, melyik
variánst viseli az adott példány. Ha egy részmeshnek kevesebb variánsa van, mint
ahány a modellnek van, az a saját variánsait ismétli.

**A helyőrző blokk.** A közös épületatlaszok egy tömör RGB (255, 64, 0) blokkot
tartanak fenn olyan felületekre, amelyeket az épület shader más textúrákból színez.
Ha a textúra egy huszadánál több pixele van 12 szinten belül ettől a színtől, a blokkot
a textúra saját átlagszínével festik át. Különben egy város
narancssárgán jönne ki.

### Átlátszó felületek {#see-through-surfaces}

A láncszem-kerítések és hálók egyetlen négyszögek, amelyek lyukai a textúra
alfájában vannak. Telten rajzolva a kerítés a pálya előtt álló fal lenne. Azok a
felületek, amelyeknek az anyagshader-e `alphatest`, `alphablend`, `transmissive`,
`anim_flag`, `impostor`, `branch`, `bush` vagy `tree`, tesztelve vannak:

- A textúra átlátszatlansága egy 32 x 32-es rácson átlagolódik.
- Felületenként (minden lyukas háromszög, amely ugyanazt a textúrát használja)
  háromszögenként négy pont mintavételezódik az UV-térben, és a háromszög UV-területével
  súlyozódik.
- Ha az átlagos átlátszatlanság legalább 0,05 és **0,5** alatti, a teljes felület kimarad.
  0,05 alatt az alfa a shader számára mást jelent (figyelmeztető jel, amely 0,01-et
  mintavételez), és a felület tömörként marad.
- Egy modell, amelynek minden felülete kimaradt, jelentést kap:
  `N models left out as see-through (mostly holes in their texture)`.

Az eszköz a teljes felületet ítéli meg, nem háromszögenként. Háromszögenként ítélve
minden négyszög fele megmaradt volna, és a kerítések fogsorokként jöttek volna ki.

### Épületek egészben rajzolva {#buildings-drawn-whole}

Egy város moduláris darabokból építi az épületeit: több százezer darab egy utcai
pálya körül, tíz- vagy százmillió háromszög akkor is, ha a legdurvább szinten
vannak. Ha darabonként hagytuk volna ki őket, magányos falpanelek maradtak volna
állni. A játék szállít egész épületeket helyettesítő modelleket is a
`scene\hlod_tier_1\` mappában, épületenként egy mesh-sel (törzs `hlod_tier_1_*`),
amelyek már világi koordinátákban vannak, mint a terep:

- Minden helyettesítő világi doboza a mesh pozíció-dobozából olvasódik (csak
  fejléc, nem dekódolás). Ez egy egész térképre másodpercek alatt megvan.
- A kör dobozát és folyosóját érintő helyettesítők kerülnek felhasználásra.
- Minden `buildings` darab, amelynek pozíciója egy helyettesítő lábnyomán belül van
  (plusz 0,5 m), kimarad, és a helyettesítő rajzolódik helyette. A távolsága a
  vezetéstől az épület legközelebbi éléig mérődik.
- Az összesítés ezt írja: `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Bekapcsolt rétegek {#switched-on-layers}

Ami egy bekapcsolt réteg elhelyez, az exportálódik, de a szabad mozgású világtól
külön, hogy a megjelenítő meg tudja mutatni vagy el tudja rejteni:

| Réteg | Rész |
|---|---|
| a szabad mozgású világ | `structure:<category>` (mint eddig) |
| egy réteg, amely az egyeztetett verseny útvonalát nevezi meg | `structure:event_<category>` |
| bármely más bekapcsolt réteg | `structure:layer_<category>` |

Az összesítés számolja őket: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Világi koordinátákban lévő modellek {#models-already-in-world-coordinates}

Néhány modelltípus nincs semmilyen elhelyezési fájlban. Meshük saját világi
pozícióval rendelkezik, mint a terep, így semmit nem kell elhelyezni:

| A `scene\models\` alatti mappa | Mi ez | Rész |
|---|---|---|
| `plots` | egy helyszín saját talaja: egy stadion padlója és belső területe, egy fesztiválterület, egy tér | `ground:venue` |
| `plinths` (és bármely `floor`, `ground` vagy `road` nevű modell) | talaj, amelyet egy utca díszít: ültetőládák, lépcsők, egy park burkolata | `ground:plinths` |
| `hda_infrastructure` (hidak) | procedurálisan épített hidak | `structure:bridges` |

- Egy modell akkor számít világi koordinátájúnak, ha a dobozának középpontja
  **300 m** (`WORLD_REACH`) távolabb van a saját origójától. Az elhelyezési
  fájlok által elhelyezett modellek a sajátjuk néhány száz méterén belül állnak.
- Nem rajzolódik: takarók, az utak mentén kifeszített kábelek, a tenger háttere,
  a moduláris épületek tetői és takarói (a helyettesítők rajzolják azokat az
  épületeket), ütközési és víz-térfogatok.
- Mindegyik a mesh-ei dobozából olvasódik (csak fejléc), másodpercek egy egész
  térképre, futásonként egyszer.
- A talajrészeket soha nem rajzolják durvábban, és soha nem hagyják ki a keret
  miatt, akárcsak a szegélyeket.

**A helyszín egészben vágódik ki.** Ha a vezetés egy helyszín saját talajához ér
(`ground:venue`), a folyosó kiszélesedik ennek a talajnak a teljes lábnyomára plusz
`--margin`-re, így a stadion körüli lelátók, falak és korlátok is bekerülnek, nem
csak az a sáv, amelyen a körök haladtak. A konzol ezt írja:
`through a venue (<model names>): cutting all of its ground, <n> km2`. A járdák nem
szélesítik a kivágást.

### Részletesség és a keret {#detail-and-the-budget}

A távolsági sávok, a keret és az, hogy a keret túl kicsi esetén melyik példány megy
el először, a [Részletességi szintek és a keret](detail-budget.md) oldalon van.

### Elhelyezési összesítés {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## A verseny saját rétege {#the-races-own-layer}

Sok verseny olyasmit ad ki, ami a szabad mozgásban nincs ott: betonfalakat és
kerítéseket, amelyek mellékutcákat zárnak el, gumiabroncs-tornyokat, sátrakat, egy
rajtportált, lelátókat, zászlókat, transzparenseket. Minden verseny felsorolja
ezeket az útvonal-definíciójában (`route<id>_<map>.rtd` a `routedefinitions.zip`-ben,
sima XML egy sima zipben):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Mi kerül hozzá.** Minden példány úgy helyeződik el, mint egy elhelyezési fájlbeli
  másolat. A transzformáció 16 száma négy sor: a modell x, y és z tengelye (mind
  skálázva), és a pozíciója a játék méterében. A harmadik sor az első kettő
  kereszt-szorzata. A `Material` az a variáns, amelyet a másolat visel. A rész a
  `structure:event_<kind>`, ahol a `<kind>` a `scene\models\` alatti mappa (barriers,
  props, infrastructure, signs; minden más díszletként számít), és a csomópont
  hordozza a glTF-extrákat: `{"layer": "event", "route": <id>}`.
- **Mi kerül el.** Egy szabad mozgású másolat, amely egy elrejtett eszköz pozíciójának
  **0,1 m**-én belül áll, kimarad. Egy az origóban álló elrejtett eszköz egy világi
  koordinátájú modell; az példány-GUID-ját a pálya `AssetManifest.xml`-ében keresi
  (a `<Models>` lista: egy modell forrása, majd a másolatai GUID-jai), hogy
  megnevezze.
- **A verseny által elrejtett talaj megmarad.** Az a verseny, amely egy helyszín
  talaját elrejti, a saját felületét rakja oda. Ha ez a felület nincs a pálya által
  szállított modellek között, az elrejtett talaj megmarad, mint a legközelebbi dolog
  ahhoz, amin vezetnek, és az összesítés ezt mondja: `kept <model>: the race hides it
  for a surface of its own that the track does not ship`.
- **Nem rajzolódik, de számolódik.** Nézői jelölők (`crowd_proxies`: a játék ezekből
  rajzolja a tömeget spriteokkal) és ütközési görbék (`.splinecol`). A konzol
  felsorolja: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Az útvonal-eszközök, amelyekhez a pálya nem szállít modellt (fénylő foltok, néhány
  tábla, a játék által streamelt tartalom), a `placed names have no model in the
  archives` alatt vannak megnevezve.

Csak a folyosón belüli másolatok kerülnek elhelyezésre, akárcsak mindennek.

## A fájl kiírása {#writing-the-file}

A részek ebben a sorrendben íródnak: csempénként `terrain`, `verge`, `road` (mind
a csempe képével), majd `water`, `tyre marks`, `markings` (lapos, az utolsó kettő
megemelve), majd minden elhelyezett rész név szerint rendezve. A koordináták a
játéké (méter, Y felfelé). Lásd: [Kimeneti formátum](output-format.md).

A fájl a glTF `asset.extras` mezőjében mondja meg, mit tartalmaz:

| Mező | Jelentés |
|---|---|
| `course_format` | `2`: benne van a verseny saját rétege, a helyszínek és a világi koordinátájú modellek. A [`courses`](commands.md#courses) egy kisebb (vagy hiányzó) számú fájlt újra exportál |
| `route` | az illesztett útvonal azonosítója, vagy `null` |
| `event_copies`, `event_kinds` | hány másolat került a verseny saját rétegéből elhelyezésre, és azok típusai |
| `hidden` | a szabad mozgású másolatok, amelyek kimaradtak, mert a verseny eltávolítja őket |
| `venue` | a helyszín-talajmodellek, amelyeken a vezetés áthalad |
| `layers` | az elhelyezett bekapcsolt rétegek |

## Mibe kerül {#what-it-costs}

Nagyságrendek:

| Pálya | Eredmény |
|---|---|
| rövid vidéki pálya | néhány százezer terep-háromszög, több mint egymillió elhelyezett; másodpercek, 100 MB alatt |
| hosszú pont-pont sprint | a folyosó a körülötte lévő doboz kis töredéke; körülbelül egy perc, néhány száz MB |
| városi utcai pálya | több ezer korlát, díszlet és tábla, és egész épületek; az automatikus kerettel akár több száz MB |

Egy négyzetkilométer nyílt világú terep körülbelül egymillió háromszög.

## Az ellenőrzések háttere {#checks-behind-it}

Ezek az olvasó megírása közben végzett mérések, ahogy a forrásban állítják. A tesztek
nem futtatják újra, hacsak a játék nincs telepítve.

- A tesztpályán az autó kb. a futómagasságán van a kinyert talaj felett (medián 0,2 m alatt).
- Minden mintavételezett csempe az 512 m-es négyzeten belül landol, amelyet a neve megjósol.
- A szomszédos korlát-elhelyezések pontosan 4 m-re vannak egymástól, és a legtöbb
  korlátvég 5 cm-en belül van a következő kezdetétől.
- A szegélyek néhány centiméterrel a kinyert talaj fölött ülnek, a lapjukkal felfelé,
  a vezetéstől 5 m-en belül (ez egy telepített játékon végzett teszt is, lásd: [Fejlesztés](development.md)).

## Nem rajzolódik {#not-drawn}

- Fák és bokrok, hacsak nincs `--trees`. A fű és a tömeg soha (a játék spriteként rajzolja őket).
- A verseny saját modelljei, amelyeket a pálya nem szállít (lásd: [A verseny saját rétege](#the-races-own-layer)).
- Vetített dekál-anyagok modelleken.
- Az alfa-keverten a táblára festett táblanyomatok átlátszatlanul jönnek ki.
- A talajszín az aszfalt, a fű és az erdő helyének rekonstrukciója, nem a játék saját terepanyagai.
