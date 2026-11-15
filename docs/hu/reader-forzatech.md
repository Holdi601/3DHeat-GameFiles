---
title: ForzaTech
nav_order: 7
lang: "hu"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, mintakártyák, elhelyezések {#forzatech-minizip-modelbin-swatches-placements}

A Forza Horizon a ForzaTech-en fut, a Turn 10 saját motorján. Ezek az olvasók egy pályát az
archívumaiból egészen a pozícionált, textúrázott háromszögekig visznek. A `course`, `courses` és
`terrain` parancsokon keresztül érik el (lásd: [Forza Horizon](course-forza-horizon.md)). Az `identify`
felismer egy `.minizip`-et és egy önálló `.modelbin`-t, a `list` és az `extract` pedig egy `.minizip`-et
fogad, a mellette lévő `ChunkContentsMiniZip<n>.txt` nevei alapján vagy bejegyzésszám szerint (`#12`).

| Formátum | Modul |
|---|---|
| `.minizip` archívumok és nevlistáik | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin` modellek és terep | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb` textúra-mintakártyák | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo` elhelyezési fájlok | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` és anyag-textúra hashek | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| terepcsempék helyük szerint | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

A Forza a tartalma nagy részét a `media\` alatti közönséges ZIP-archívumokban is tartja. A Python
`zipfile`-ja ezeket megnyitja, a `forzatech.models_in_archive()` pedig felsorolja a `.modelbin`
bejegyzéseiket. A pálya geometriája a `.minizip` archívumokban van.

## `.minizip`: archívum névtelen tartalommal {#minizip-an-archive-with-no-names}

Egy pálya négy `GeoChunk<n>.minizip` archívumot szállít, nyílt világú térképnél tíz gigabájtnyiakat,
több százezer bejegyzéssel. **Az archívumok semmilyen nevet nem tárolnak**: nincs névtábla, és nincs
bejegyzésenkénti fejléc, csak egy sorszám. A nevek a mellette lévő `ChunkContentsMiniZip<n>.txt`
fájlban vannak, soronként egy bejegyzés, bejegyzési sorrendben (`<build path>zipcache\pc\<path>|<bundle>`).
Ez a párosítás az egyetlen mód egy fájl lekérésére. A `zipcache\pc\`-ig tartó rész el van dobva, és a
keresés nem érzékeny a kis- és nagybetűre.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Az indexben három részlet van, amely rosszul olvasva is ad kimenetet. Az olvasó mindhármat helyesen
kezeli:

| Részlet | Amit egy gondatlan olvasó csinál | Hogy néz ki |
|---|---|---|
| a szegmensbázis **64 bites** | u32-nek és kitöltésnek olvassa | az első 4 GB-ig helyes, utána a megfelelő hosszúságú zaj |
| a bázis **8 bájtra igazított** | figyelmen kívül hagyja a csomagtábla utáni kitöltő szót | páros csomagszámú archívumokban minden bejegyzés olyan kodeket állít, amely nem létezik |
| egy bejegyzés tárolt hossza a következő bejegyzésig (vagy a következő szegmens bázisáig) tartó rés **a kitöltés nélkül** (a 12–13-as jelzőbitek) | az egész rést használja | az LZ4 azonnal megtagadja a blokkot |

A kodekek a jelzők alsó öt bitje: `0x00` tárolt, `0x08` nyers deflate, `0x1F` LZ4-blokk. Minden más
megtagadva. Minden bejegyzésnek pontosan a deklarált méretére kell kicsomagolódnia, különben
megtagadjuk. Az index (mintegy 5 MB) egyszer olvasódik, a tartalmakat keresésssel olvassuk.

A fejléc ellenőrzött: a mágikus szó, egy 32 bájtos fejléc, és a szegmensszám egyezik a
`ceil(entries / per segment)` értékkel.

**Ellenőrizve:** minden térkép minden archívumából mintavett bejegyzések, mindhárom kodekkel pontosan a
deklarált hosszukra kicsomagolva.

## `.modelbin`: a darabos konténer {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- A deklarált fájlméretnek egyeznie kell a valódi mérettel.
- **A lánc:** minden darab ott kezdődik, ahol az előző véget ért, 4 bájtra felfelé kerekítve. Ezt semmi
  a fájl nem mondja ki, ezért bizonyíték: egy rekord, amelyet rossz lépéssel olvasnak, nem adja ki. Az
  összes mintavett, 252 modellen teljesült.
- A `PGZP` fájl, amelyet a modellolvasónak adnak, „a ForzaTech .minizip archívumként" van megnevezve,
  és a `minizip.py`-ra mutat, ahelyett, hogy üresen elutasítanánk.

A geometriát ezek a darabok adják:

| Darab | Tartalma |
|---|---|
| `VLay` | egy csúcselrendezés: attribútumnevek, majd elemek (u16 névindex, u16 csatorna, puffer, DXGI-formátum, eltolás); az elemszám egy u16 |
| `VerB` | egy csúcspuffer 16 bájtos fejléccel (szám, méret, u16 lépés, u16 attribútumok, formátum) |
| `IndB` | az indexpuffer, azonos fejléccel |
| `Mesh` | egy részháló: anyag, részletességi szint-maszk, indextartomány, elrendezés, puffer, lépés, változattábla, és egy pozíciódoboz a végén |
| `MatI` | egy anyagpéldány: a `.materialbin` útvonala és textúra-hashei |

### Pozíciók és a doboz {#positions-and-the-box}

A pozíciók `R16G16B16A16_SNORM` (13-as formátum): csúcsonként négy előjeles rövid int.
`position = short / 32767 * scale + bias`, ahol a scale és a bias a `Mesh` darab utolsó 32 bájtja (két
float4). A bias **a játék világkoordinátáiban** van, így egy terepcsempe ott landol, ahol a játék
teszi, példányátalakítás nélkül. Ezért elég egy telemetriakör ahhoz, hogy egy térképrészletet kérjünk.
Egy modell minden részhálója ugyanazt a dobozt hordozza (860-on ellenőrizve).

### A csúcselrendezés {#the-vertex-layout}

Egy pozíciópuffer fedi az összes csúcsot. A többi attribútum egymást követő csúcscsoportokra oszlik,
mindegyiknek saját pufferével és elrendezésével: egy csomópont közeli út három UV-készletet és két
tangenst hordoz, a mellette lévő rézsű csak normált. Minden nem pozíciós attribútum négy bájt. Hogy
melyik elrendezés melyik puffert írja le, azt a belőle rajzoló részhálókból vesszük, mert az elrendezések
és a pufferek nem azonos sorrendben vannak (azonos, eggyel elforgatott vagy átrendezett, a modelltől
függően).

| DXGI-formátum | Kód | Mire való |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozíció (a negyedik rövid a normál x-e) |
| R16G16_SNORM | 37 | normál y, z |
| R16G16_UNORM | 35 | egy UV-pár (a csatorna = melyik készlet) |
| R8G8B8A8_UNORM | 28 | szín vagy csontsúly |
| R10G10B10A2_UNORM | 24 | tangens (nincs dekódolva) |
| R16_UINT | 57 | indexek |

**A normál felosztva van.** A `NORMAL` y-t és z-t tartalmaz. Az x a pozíció negyedik rövidje, amely
kitöltésnek látszott. Több százezer terepcsúcson át a +0,92-es korrelációt mutatja a háromszög-normál
x-ével, mást nem. Ezzel a csúcsok 96%-a lejtős talajon 18°-on belül van a számított normálhoz képest.
Minden két komponensű kódolás, amelyet ez nélkül próbáltunk (köztük az oktaéderes mind a 48 elrendezésben),
y-t és z-t jól, x-et rosszul adta.

Más pozíció- vagy indexformátumokat **megtagadunk** („only 13 (four shorts, scaled) is implemented";
„only unsigned shorts are implemented").

### Részhálók {#submeshes}

Egy `Mesh` rekord szabványos formában 238 bájt. A hosszabbak egy hosszabb anyag-**változattáblát** hordoznak
az elején, 238 + 8 x count - 4 bájt, és minden utána következő mező pontosan ennyivel tolódik vissza.
A rövidebbek (218 bájt, néhány terep) megtartják az eltolásokat. Minden változatbejegyzés
`u16 0xFFFF, u16 nyári anyag, u16 0xFFFF, u16 téli anyag`. A részletességi szint-maszk egy u16, bitenként
egy szint, az 1-es bittől.

Semmi nem bízik egyedül egy adatban. Az indextartományoknak pontosan le kell fedniük az indexpuffert,
minden `index count`-nak 3 x `triangles`-nek kell lennie, és a részhálónak megnevezett lépésnek a pufferéé
kell lennie. Az a tábla, amely nem felel meg, egészben megtagadódik, mert a rosszul olvasott mezőkből
címkézett háromszögek rosszabbak, mint a hiányzó címkék. A mintavett több ezer részhálón minden, amelynek
pufferindexe tartományon belül van, átment.

### Anyagok és textúra-hashek {#materials-and-texture-hashes}

Egy `MatI` az anyagát egy `Game:...\x.materialbin` útvonallal nevezi meg, a darab keresésével. Textúrái
`u32 slot, u32, u32 hash` rekordok, egymástól 33 bájtra, igazítatlanul, ezért a darabot minden bájtoffszetnél
átkeressük olyan szavakra, amelyek ismert textúra-hashek. Ezek a pálya `AssetManifest.xml`-jéből jönnek
(`<Texture Source="...\name.swatch" SourceHash="...">`, a `</Textures>`-ig olvasva). A `0x88B483AA` slot a
szabványos árnyaló alapszíne. Hogyan választják ki utána a színtextúrát, az a [Forza Horizon](course-forza-horizon.md#which-texture)
oldalon van.

## `.pb`: textúra-mintakártyák {#pb-texture-swatches}

Egy mintakártya ugyanaz a `burG` konténer, mint egy modell: egy 96 bájtos `HCXT` fejléc a 44. bájtnál, majd
egy pixeldarab. A fejléc tartalmazza a textúra GUID-ját (a fájlnévben), a szélességet és magasságot, a mip-számot
és a **formátumkódot a 72. bájton** (a ForzaTech saját számozása). A 84. bájt a pixelbájtok számát adja.

| Kód | Formátum | Azonosítva mint |
|---|---|---|
| 0 | BC1, pixelenként fél bájt | piros-fehér szegély-textúrára dekódolódik (zaj BC4 alatt) |
| 9 | BC7, pixelenként egy bájt | egy terepcsempére dekódolódik, amelyen a pálya látszik |
| 13 | RGBA8, pixelenként négy bájt | sima |
| egyéb | megtagadva | „texture format N has not been identified; refusing to guess" |

A formátumokat valódi fájlok dekódolásával azonosítottuk, minden módon, ahogy a payload mérete engedi.
A 47. bájt, amelyet egy korábbi verzió formátumnak vett, a mintavett textúrák mindegyikében 4. Csak egy
fájl legfelső mipjét dekódoljuk. Minden felbontás külön bejegyzés, `<name>_<guid>_quality<n>.pb`, az 1-es
minőség a legkisebb, az 5-ös a legnagyobb. A terképekhez a két legnagyobb egy másik archívumban van, mint
a többi. A dekódolás a Pillow BCn-dekódolóján át megy, generált DDS-fejléccel.

## Elhelyezési fájlok (.pgeo) {#placement-files-pgeo}

Kategóriánként és térbeli cellánként egy fájl:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Maga az útvonal megadja a cella
négyzetét és a kategóriát, így a fájlokat meg lehet szűrni megnyitásuk nélkül.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Hogyan döntöttük el az egyes mezőket:

| Mező | Ezt döntötte el |
|---|---|
| a pozíció 16.16 fixpontos, nem a doboz törtrésze | az egymást követő korlátok pontosan 4,000 m-re vannak egymástól (a modell hossza) |
| előjel-nagyság, nem kettes komplemens | a kettes komplemens a negatív koordinátákat tízezer kilométerrel a térkép mellé tette; a 31. bit előjelként, minden mintavett kategória minden rekordja a fájl dobozán belül esik |
| a vektorok a modell saját tengelyei | minden korlát vége az következő kezdetére esik: 93,5% 5 cm-en belül, medián 0,000 m |
| a 60. bájt a változat | egy reklámtábla öt példánya 0, 2, 2, 3, 4-et olvas, miközben minden korlát 0-t |

Csak a `_3D` végződésű nevek modelrekordok. Az előttük lévő változattábla végződés nélküli neveket sorol, és
rekordként olvasva azok a végtelenbe kerülnek. Egy jelölt rekord csak akkor fogadható el, ha a darabszáma
belefér a fájlba, és a nem véges számokat tartalmazó példányok el vannak dobva.

## Nincs megvalósítva {#not-implemented}

- A fent nem említett csúcs- és indexformátumok (megtagadva).
- A 0, 9, 13-on kívüli textúraformátumok (megtagadva).
- Tangensek (átugorva, nem használva).
- A terepárnyaló anyagrétegei. A talajtextúra a csempe-térképek értelmezése (lásd: [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
