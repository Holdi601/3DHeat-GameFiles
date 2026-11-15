---
title: "ForzaTech"
nav_order: 7
lang: "bs"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, uzorci, postavljanja {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon radi na ForzaTechu, vlastitom engineu studija Turn 10. Ovi čitači
vode stazu iz njenih arhiva do pozicioniranih, teksturiranih trouglova. Do njih
se dolazi kroz `course`, `courses` i `terrain` (pogledajte
[Forza Horizon](course-forza-horizon.md)). `identify` prepoznaje `.minizip`
i goli `.modelbin`, a `list` i `extract` uzimaju `.minizip`, po imenima iz
`ChunkContentsMiniZip<n>.txt` pored njega ili po broju unosa (`#12`).

| Format | Modul |
|---|---|
| `.minizip` arhive i njihove liste imena | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin` modeli i teren | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb` uzorci tekstura | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo` datoteke postavljanja | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` i hashevi tekstura materijala | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| pločice terena po mjestu | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza također drži velik dio sadržaja u običnim ZIP arhivama pod `media\`.
Pythonov `zipfile` ih otvara, a `forzatech.models_in_archive()` navodi njihove
`.modelbin` unose. Geometrija staze je u `.minizip` arhivama.

## `.minizip`: arhiva bez imena {#minizip-an-archive-with-no-names}

Staza isporučuje četiri arhive `GeoChunk<n>.minizip`, svaka desetine gigabajta za
mapu otvorenog svijeta, sa stotinama hiljada unosa. **Arhive uopće ne pohranjuju
imena**: nema tablice imena ni zaglavlja po unosu, samo redni broj. Imena su u
`ChunkContentsMiniZip<n>.txt` pored svake arhive, jedan red po unosu redom unosa
(`<build path>zipcache\pc\<path>|<bundle>`). To sparivanje je jedini način da se
zatraži datoteka. Sve do `zipcache\pc\` se odbacuje, a pretraživanje ignorira
velika i mala slova.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tri detalja u indeksu i dalje daju izlaz kad se pročitaju pogrešno. Čitač sva tri
čita ispravno:

| Detalj | Šta radi nepažljiv čitač | Kako to izgleda |
|---|---|---|
| baza segmenta je **64-bitna** | čita je kao u32 plus padding | ispravno za prva 4 GB, zatim šum prave dužine |
| baza je **poravnata na 8 bajtova** | ignorira riječ paddinga nakon tablice bundlova | u arhivama s parnim brojem bundlova svaki unos tvrdi da ima kodek koji ne postoji |
| pohranjena dužina unosa je razmak do sljedećeg unosa (ili baze sljedećeg segmenta) **minus njegov padding** (bitovi zastavica 12-13) | koristi cijeli razmak | LZ4 potpuno odbija blok |

Kodeci su niža pet bitova zastavica: `0x00` pohranjeno, `0x08` sirovi deflate,
`0x1F` LZ4 blok. Svaki drugi se odbija. Svaki unos se mora raspakovati na tačno
onu veličinu koju navodi, inače se odbija. Indeks (oko 5 MB) čita se jednom, a
payloadi se čitaju premotavanjem.

Zaglavlje se provjerava: magic, zaglavlje od 32 bajta i broj segmenata koji se
podudara s `ceil(entries / per segment)`.

**Provjereno:** unosi uzorkovani iz svake arhive mape, svaki se
raspakuje na tačno svoju navedenu dužinu pod sva tri kodeka.

## `.modelbin`: kontejner chunkova {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Navedena veličina datoteke mora biti jednaka stvarnoj.
- **Lanac**: svaki chunk počinje tamo gdje je prethodni završio, zaokruženo na
  4 bajta. Ništa u datoteci ovo ne navodi, pa je to dokaz: zapis pročitan s
  pogrešnim korakom ga ne daje. Vrijedilo je za svih 252 uzorkovana modela.
- `PGZP` datoteka data čitaču modela imenuje se kao "a ForzaTech .minizip
  archive, not a model" i upućuje na `minizip.py`, umjesto da se prazno odbije.

Geometrija dolazi iz ovih chunkova:

| Chunk | Sadrži |
|---|---|
| `VLay` | raspored vrhova: imena atributa, zatim elementi (u16 indeks imena, u16 kanal, bafer, DXGI format, pomak); broj elemenata je u16 |
| `VerB` | bafer vrhova iza zaglavlja od 16 bajtova (broj, veličina, u16 stride, u16 atributi, format) |
| `IndB` | bafer indeksa, isto zaglavlje |
| `Mesh` | jedna podmreža: materijal, maska nivoa detalja, raspon indeksa, raspored, bafer, stride, tablica varijanti i kutija pozicije na kraju |
| `MatI` | instanca materijala: njegova putanja `.materialbin` i hashevi tekstura |

### Pozicije i kutija {#positions-and-the-box}

Pozicije su `R16G16B16A16_SNORM` (format 13): četiri označena shorta po vrhu.
`position = short / 32767 * scale + bias`, gdje su scale i bias posljednjih 32
bajta chunka `Mesh` (dva float4). Bias je u **svjetskim koordinatama igre**, pa
pločica terena sleti tamo gdje je igra stavlja bez transformacije instance. Zato
je krug telemetrije dovoljan da se zatraži dio mape. Svaka podmreža modela nosi
istu kutiju (provjereno na 860 njih).

### Raspored vrhova {#the-vertex-layout}

Jedan bafer pozicija pokriva svaki vrh. Ostali atributi podijeljeni su u
uzastopne grupe vrhova, svaka sa svojim baferom i svojim rasporedom: cesta blizu
raskrsnice nosi tri UV skupa i dvije tangente, nasip pored nje samo normalu.
Svaki atribut osim pozicije je četiri bajta. Koji raspored opisuje koji bafer
uzima se iz podmreža koje iz njega crtaju, jer rasporedi i baferi nisu istim
redoslijedom (isto, rotirano za jedan, ili permutirano, ovisno o modelu).

| DXGI format | Kod | Koristi se za |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozicija (četvrti short je x normale) |
| R16G16_SNORM | 37 | normala y, z |
| R16G16_UNORM | 35 | UV par (kanal = koji skup) |
| R8G8B8A8_UNORM | 28 | boja ili težine miješanja |
| R10G10B10A2_UNORM | 24 | tangenta (ne dekodira se) |
| R16_UINT | 57 | indeksi |

**Normala je podijeljena.** `NORMAL` drži y i z. X je četvrti short pozicije,
koji je izgledao kao padding. Preko stotina hiljada vrhova terena korelira
+0,92 s x normale trougla i ni s čim drugim. S njim je 96% vrhova nagnutog
tla unutar 18° od izračunate normale. Svako dvokomponentno kodiranje isprobano
bez njega (uključujući oktaedarsko u svih 48 rasporeda) imalo je y i z ispravne,
a x pogrešan.

Drugi formati pozicija ili indeksa se **odbijaju** ("only 13 (four shorts, scaled) is
implemented"; "only unsigned shorts are implemented").

### Podmreže {#submeshes}

Zapis `Mesh` je 238 bajta u standardnom obliku. Duži nose dužu tablicu
**varijanti** materijala na početku, 238 + 8 x count - 4 bajta, i svako polje
nakon nje pomjera se unazad za tačno toliko. Kraći (218 bajta, neki teren)
zadržavaju pomake. Svaki unos varijante je
`u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`.
Maska nivoa detalja je u16, jedan bit po nivou od bita 1.

Ništa se ne vjeruje samo. Rasponi indeksa moraju tačno popločati bafer indeksa,
svaki `index count` mora biti jednak 3 x `triangles`, a stride koji podmreža
navodi mora biti stride njenog bafera. Tablica koja ne prođe odbija se cijela,
jer je označavanje trouglova iz pogrešno pročitanih polja gore nego ih ne
označiti. Preko hiljada uzorkovanih podmreža prolazi svaka čiji je indeks bafera
u opsegu.

### Materijali i hashevi tekstura {#materials-and-texture-hashes}

`MatI` imenuje svoj materijal putanjom `Game:...\x.materialbin`, pronađenom
pretragom chunka. Njegove teksture su zapisi `u32 slot, u32, u32 hash`, razmaknuti
33 bajta i neporavnati, pa se chunk pretražuje na svakom bajtnom pomaku za riječi
koje su poznati hashevi tekstura. Oni dolaze iz `AssetManifest.xml` staze
(`<Texture Source="...\name.swatch" SourceHash="...">`, čita se do
`</Textures>`). Slot `0x88B483AA` je osnovna boja standardnog shadera. Kako se
zatim bira tekstura boje opisano je na stranici
[Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: uzorci tekstura {#pb-texture-swatches}

Uzorak (swatch) je isti `burG` kontejner kao model: zaglavlje `HCXT` od 96 bajta
na bajtu 44, zatim jedan chunk piksela. Zaglavlje drži GUID teksture (onaj u
njenom imenu datoteke), širinu i visinu, broj mipova i **kod formata na bajtu 72**
(vlastito numerisanje ForzaTecha). Bajt 84 drži broj bajta piksela.

| Kod | Format | Identificirano kao |
|---|---|---|
| 0 | BC1, pola bajta po pikselu | dekodira se u crveno-bijeli ivičnjak (šum pod BC4) |
| 9 | BC7, jedan bajt po pikselu | dekodira se u pločicu terena s vidljivom stazom |
| 13 | RGBA8, četiri bajta po pikselu | običan |
| drugi | odbija se | "texture format N has not been identified; refusing to guess" |

Formati su identificirani dekodiranjem stvarnih datoteka na svaki način koji
veličina payloada dopušta. Bajt 47, koji je ranija verzija uzimala za format, je 4
u svakoj od uzorkovanih tekstura. Dekodira se samo gornji mip datoteke. Svaka
rezolucija je vlastiti unos, `<name>_<guid>_quality<n>.pb`, kvalitet 1 najmanji
do 5 najveći. Za mape terena dvije najveće su u drugoj arhivi od ostalih.
Dekodiranje ide kroz Pillowov BCn dekoder, preko generiranog DDS zaglavlja.

## Datoteke postavljanja (.pgeo) {#placement-files-pgeo}

Jedna datoteka po kategoriji po prostornoj ćeliji:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Sama putanja
daje kvadrat i kategoriju ćelije, pa se datoteke mogu filtrirati bez otvaranja.

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

Kako je svako polje određeno:

| Polje | Određeno pomoću |
|---|---|
| pozicija je 16.16 fiksni zarez, a ne razlomak kutije | uzastopne zaštitne ograde udaljene su tačno 4,000 m (dužina modela) |
| predznak-i-veličina, a ne dvojni komplement | dvojni komplement je stavljao negativne koordinate desetinama kilometara van mape; s bitom 31 kao predznakom, svaki zapis svake uzorkovane kategorije slijeće unutar kutije svoje datoteke |
| vektori su vlastite ose modela | kraj svake zaštitne ograde slijeće na početak sljedeće: 93,5% unutar 5 cm, medijan 0,000 m |
| bajt 60 je varijanta | pet kopija bilborda čita 0, 2, 2, 3, 4 dok svaka zaštitna ograda čita 0 |

Samo imena koja završavaju na `_3D` su zapisi modela. Tablica varijanti prije
njih navodi imena bez sufiksa, i čitana kao zapisi ona slijeću u beskonačnost.
Kandidatski zapis prihvata se samo ako njegov broj stane u datoteku, a instance
s nekonačnim brojevima se odbacuju.

## Nije implementirano {#not-implemented}

- Formati vrhova i indeksa osim gore navedenih (odbijaju se).
- Formati tekstura osim 0, 9, 13 (odbijaju se).
- Tangente (pročitane mimo, ne koriste se).
- Slojevi materijala shadera terena. Tekstura tla je interpretacija mapa pločica (pogledajte [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
