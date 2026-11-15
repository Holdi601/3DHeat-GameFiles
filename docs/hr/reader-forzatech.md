---
title: ForzaTech
nav_order: 7
lang: "hr"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, uzorci, postavljanja {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon radi na ForzaTechu, Turn 10-ovom vlastitom pogonu. Ovi čitači vode stazu
od njezinih arhiva do pozicioniranih, teksturiranih trokuta. Do njih se dolazi kroz
`course`, `courses` i `terrain` (vidi [Forza Horizon](course-forza-horizon.md)).
`identify` prepoznaje `.minizip` i goli `.modelbin`, a `list` i `extract` uzimaju
`.minizip`, po imenima u `ChunkContentsMiniZip<n>.txt` pored njega ili po rednom broju
unosa (`#12`).

| Format | Modul |
|---|---|
| `.minizip` arhive i njihovi popisi imena | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin` modeli i teren | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb` uzorci tekstura | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo` datoteke postavljanja | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` i hashevi tekstura materijala | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| pločice terena po mjestu | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza također čuva velik dio sadržaja u običnim ZIP arhivama pod `media\`. Pythonov
`zipfile` ih otvara, a `forzatech.models_in_archive()` popisuje njihove `.modelbin`
unose. Geometrija staza je u `.minizip` arhivama.

## `.minizip`: arhiva bez imena {#minizip-an-archive-with-no-names}

Staza isporučuje četiri arhive `GeoChunk<n>.minizip`, po desetke gigabajta za
otvoreni svijet, sa stotinama tisuća unosa. **Arhive uopće ne spremaju imena**: nema
tablice imena ni zaglavlja po unosu, samo redni broj. Imena su u
`ChunkContentsMiniZip<n>.txt` pored svake arhive, jedan redak po unosu, redom unosa
(`<build path>zipcache\pc\<path>|<bundle>`). To uparivanje je jedini način da se zatraži
datoteka. Sve do `zipcache\pc\` se odbacuje, a traženja ne razlikuju velika i mala slova.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tri pojedinosti u indeksu i dalje daju izlaz kad se pročitaju krivo. Čitač ih sve tri
ispravno čita:

| Pojedinost | Što radi nepažljiv čitač | Kako to izgleda |
|---|---|---|
| baza segmenta je **64-bitna** | čita je kao u32 plus popunjavanje | ispravna za prva 4 GB, zatim šum prave duljine |
| baza je **poravnata na 8 bajtova** | ignorira riječ popunjavanja iza tablice paketa | u arhivama s parnim brojem paketa svaki unos tvrdi da koristi kodek koji ne postoji |
| spremljena duljina unosa je razmak do sljedećeg unosa (ili baze sljedećeg segmenta) **minus njegovo popunjavanje** (bitovi zastavica 12-13) | uzima cijeli razmak | LZ4 odbija blok bez iznimke |

Kodeci su donjih pet bitova zastavica: `0x00` pohranjeno, `0x08` sirovi deflate,
`0x1F` LZ4 blok. Svaki drugi se odbija. Svaki unos mora se raspakirati u točno veličinu
koju deklarira, ili se odbija. Indeks (oko 5 MB) čita se jednom, a podaci se čitaju
pozicioniranjem.

Zaglavlje se provjerava: magični broj, zaglavlje od 32 bajta, i broj segmenata koji se
podudara s `ceil(entries / per segment)`.

**Provjereno:** unosi uzorkovani kroz svaku arhivu karte, svaki se raspakira u točno svoju
deklariranu duljinu pod sva tri kodeka.

## `.modelbin`: spremnik segmenata {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Deklarirana veličina datoteke mora biti jednaka stvarnoj.
- **Lanac**: svaki segment počinje tamo gdje je završio prethodni, zaokružen na 4 bajta.
  Ništa u datoteci to ne kaže, pa je to dokaz: zapis pročitan krivim korakom to ne proizvodi.
  Držalo je za svih 252 uzorkovana modela.
- `PGZP` datoteka predana čitaču modela imenuje se kao "a ForzaTech .minizip archive, not a
  model" i upućuje na `minizip.py`, umjesto da se odbije bez objašnjenja.

Geometriju daju ovi segmenti:

| Segment | Sadrži |
|---|---|
| `VLay` | raspored vrhova: imena atributa, pa elementi (u16 indeks imena, u16 kanal, međuspremnik, DXGI format, pomak); broj elemenata je u16 |
| `VerB` | međuspremnik vrhova iza zaglavlja od 16 bajtova (broj, veličina, u16 korak, u16 atributi, format) |
| `IndB` | međuspremnik indeksa, isto zaglavlje |
| `Mesh` | jedna podmreža: materijal, maska razine detalja, raspon indeksa, raspored, međuspremnik, korak, tablica varijanti, i kutija pozicija na kraju |
| `MatI` | instanca materijala: njezina `.materialbin` putanja i hashevi tekstura |

### Pozicije i kutija {#positions-and-the-box}

Pozicije su `R16G16B16A16_SNORM` (format 13): četiri označena kratka broja po vrhu.
`position = short / 32767 * scale + bias`, gdje su scale i bias zadnjih 32 bajta
segmenta `Mesh` (dva float4). Bias je u **svjetskim koordinatama igre**, pa pločica terena
sleti tamo gdje je igra stavlja bez transformacije instance. Zato je dovoljan jedan krug
telemetrije da se zatraži dio karte.
Svaka podmreža modela nosi istu kutiju (provjereno na 860 njih).

### Raspored vrhova {#the-vertex-layout}

Jedan međuspremnik pozicija pokriva svaki vrh. Ostali atributi podijeljeni su u uzastopne
grupe vrhova, svaka sa svojim međuspremnikom i svojim rasporedom: cesta blizu raskrižja
nosi tri skupa UV-ova i dvije tangente, a obala pored nje samo normalu. Svaki ne-pozicijski
atribut je četiri bajta. Koji raspored opisuje koji međuspremnik određuje se iz podmreža
koje crtaju iz njega, jer rasporedi i međuspremnici nisu u istom redoslijedu (isti, pomaknut
za jedan, ili permutiran, ovisno o modelu).

| DXGI format | Kod | Za što |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozicija (četvrti kratki broj je x normale) |
| R16G16_SNORM | 37 | normala y, z |
| R16G16_UNORM | 35 | par UV-ova (kanal = koji skup) |
| R8G8B8A8_UNORM | 28 | boja ili težine miješanja |
| R10G10B10A2_UNORM | 24 | tangenta (nije dekodirana) |
| R16_UINT | 57 | indeksi |

**Normala je podijeljena.** `NORMAL` drži y i z. x je četvrti kratki broj pozicije, koji je
izgledao kao popunjavanje. Preko stotina tisuća vrhova terena korelira s +0,92 s x
normale trokuta i ni s čim drugim. S njime, 96% vrhova nagnutog tla je unutar 18° od
izračunate normale. Svaka kodiranja s dvije komponente isprobana bez nje (oktaedarska u
svih 48 rasporeda među njima) ispravno su dobila y i z, a krivo x.

Drugi formati pozicija ili indeksa se **odbijaju** ("only 13 (four shorts, scaled) is
implemented"; "only unsigned shorts are implemented").

### Podmreže {#submeshes}

Zapis `Mesh` je 238 bajtova u standardnom obliku. Duži nose duže tablicu materijalnih
**varijanti** na početku, 238 + 8 x broj - 4 bajta, a svako polje iza nje pomiče se unatrag
za točno tu vrijednost. Kratki (218 bajtova, neki teren) zadržavaju pomake. Svaki unos
varijante je `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Maska
razine detalja je u16, jedan bit po razini od bita 1.

Ništa se ne vjeruje samo. Rasponi indeksa moraju točno prekrivati međuspremnik indeksa,
svaki `index count` mora biti jednak 3 x `triangles`, a korak koji podmreža navodi mora biti
korak njezina međuspremnika. Tablica koja ne prođe odbija se u cijelosti, jer je
označavanje trokuta iz krivo pročitanih polja gore od toga da se ne označava. Kroz tisuće
uzorkovanih podmreža, svaka čiji je indeks međuspremnika u rasponu prolazi.

### Materijali i hashevi tekstura {#materials-and-texture-hashes}

`MatI` imenuje svoj materijal putanjom `Game:...\x.materialbin`, pronađenom pretragom
segmenta. Njegove teksture su zapisi `u32 slot, u32, u32 hash` udaljeni 33 bajta, bez
poravnanja, pa se segment pretražuje na svakom bajtovnom pomaku za riječima koje su poznati
hashevi tekstura. Oni dolaze iz `AssetManifest.xml` staze
(`<Texture Source="...\name.swatch" SourceHash="...">`, čitano do `</Textures>`). Utor
`0x88B483AA` je osnovna boja standardnog sjenčala. Kako se tada bira tekstura boje, opisano
je na [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: uzorci tekstura {#pb-texture-swatches}

Uzorak je isti `burG` spremnik kao model: zaglavlje `HCXT` od 96 bajtova na bajtu 44, zatim
jedan segment piksela. Zaglavlje sadrži GUID teksture (onaj u njenom imenu datoteke),
širinu i visinu, broj mipova i **kod formata na bajtu 72** (ForzaTechovo vlastito
numeriranje). Bajt 84 drži broj bajtova piksela.

| Kod | Format | Prepoznat kao |
|---|---|---|
| 0 | BC1, pola bajta po pikselu | dekodira se u crveno-bijeli rub (šum pod BC4) |
| 9 | BC7, jedan bajt po pikselu | dekodira se u pločicu terena s vidljivom stazom |
| 13 | RGBA8, četiri bajta po pikselu | običan |
| ostalo | odbijeno | "texture format N has not been identified; refusing to guess" |

Formati su prepoznati dekodiranjem stvarnih datoteka na svaki način koji veličina podataka
dopušta. Bajt 47, koji je ranija verzija uzela za format, je 4 u svakoj uzorkovanoj
teksturi. Dekodira se samo gornji mip datoteke. Svaka rezolucija je zaseban unos,
`<name>_<guid>_quality<n>.pb`, kvaliteta 1 najmanja do 5 najveća. Za karte terena dvije
najveće su u drugoj arhivi nego ostale. Dekodiranje ide kroz Pillowov BCn dekoder, preko
generiranog DDS zaglavlja.

## Datoteke postavljanja (.pgeo) {#placement-files-pgeo}

Jedna datoteka po kategoriji po prostornoj ćeliji:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Sama putanja daje kvadrat
ćelije i kategoriju, pa se datoteke mogu filtrirati bez njihova otvaranja.

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

Kako je odlučeno svako polje:

| Polje | Odlučeno prema |
|---|---|
| pozicija je 16.16 fiksna točka, a ne udio kutije | uzastopne tračnice su točno 4,000 m udaljene (duljina modela) |
| znak-veličina, a ne dvojni komplement | dvojni komplement je stavljao negativne koordinate desetke kilometara izvan karte; s bitom 31 kao predznakom, svaki zapis svake sampling kategorije pada unutar kutije svoje datoteke |
| vektori su vlastite osi modela | kraj svake tračnice pada na početak sljedeće: 93,5% unutar 5 cm, medijan 0,000 m |
| bajt 60 je varijanta | pet primjeraka billboarda čita 0, 2, 2, 3, 4, dok svaka tračnica čita 0 |

Samo imena koja završavaju na `_3D` su zapisi modela. Tablica varijanti prije njih navodi
imena bez nastavka, i pročitana kao zapisi ona završe u beskonačnosti. Kandidatski zapis se
prihvaća samo ako njegov broj stane u datoteku, a instance s nekonačnim brojevima se
odbacuju.

## Nije implementirano {#not-implemented}

- Formati vrhova i indeksa osim gore navedenih (odbijeni).
- Formati tekstura osim 0, 9, 13 (odbijeni).
- Tangente (preskočene, ne koriste se).
- Slojevi materijala sjenčala terena. Tekstura tla je tumačenje karti pločica (vidi
  [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
