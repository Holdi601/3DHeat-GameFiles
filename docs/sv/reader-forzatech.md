---
title: ForzaTech
lang: "sv"
source: reader-forzatech.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, färgprov, placeringar

Forza Horizon körs på ForzaTech, Turn 10:s egen motor. Dessa läsare tar en bana från
dess arkiv ner till positionerade, texturerade trianglar. De nås via `course`,
`courses` och `terrain` (se [Forza Horizon](course-forza-horizon.md)). `identify`
känner igen en `.minizip` och en fristående `.modelbin`, och `list` och `extract` tar
en `.minizip`, med namnen i `ChunkContentsMiniZip<n>.txt` bredvid den eller med
postnummer (`#12`).

| Format | Modul |
|---|---|
| `.minizip`-arkiv och deras namnlistor | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin`-modeller och terräng | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb`-texturfärgprov | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo`-placeringsfiler | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` och materialens texturhashar | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| terrängrutor efter plats | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza har också mycket av sitt innehåll i vanliga ZIP-arkiv under `media\`. Pythons
`zipfile` öppnar dem, och `forzatech.models_in_archive()` listar deras `.modelbin`-poster.
Banans geometri ligger i `.minizip`-arkiven.

## `.minizip`: ett arkiv utan namn

En bana levereras med fyra `GeoChunk<n>.minizip`-arkiv, tiotals gigabyte vardera för en
karta med öppen värld, med hundratusentals poster. **Arkiven lagrar inga namn alls**:
ingen namntabell och ingen huvudinformation per post, bara ett löpnummer. Namnen
finns i `ChunkContentsMiniZip<n>.txt` bredvid varje arkiv, en rad per post i postordning
(`<build path>zipcache\pc\<path>|<bundle>`). Den parningen är det enda sättet att be
om en fil. Allt upp till `zipcache\pc\` tas bort, och uppslag ignorerar versaler och gemener.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tre detaljer i indexet ger fortfarande utdata när de läses fel. Läsaren hanterar alla tre rätt:

| Detalj | Vad en slarvig läsare gör | Hur det ser ut |
|---|---|---|
| segmentbasen är **64-bitars** | läser den som u32 plus utfyllnad | rätt för de första 4 GB, sedan brus med rätt längd |
| basen är **8-bytesjusterad** | ignorerar utfyllnadsordet efter paketstabellen | i arkiv med ett jämnt antal paket påstår varje post en kodek som inte finns |
| en posts lagrade längd är avståndet till nästa post (eller nästa segments bas) **minus sin utfyllnad** (flaggbitar 12-13) | använder hela avståndet | LZ4 vägrar blocket helt |

Kodekerna är de fem lägsta bitarna i flaggorna: `0x00` lagrad, `0x08` rå deflate,
`0x1F` LZ4-block. Alla andra vägras. Varje post måste packas upp till exakt den storlek
den anger, annars vägras den. Indexet (cirka 5 MB) läses en gång, och nyttolaster läses genom att söka.

Huvudinformationen kontrolleras: magi, en 32-bytes header, och ett segmentantal som
stämmer med `ceil(entries / per segment)`.

**Verifierat:** poster samplade över varje arkiv i en karta, var och en packas upp till
exakt sin deklarerade längd under alla tre kodekerna.

## `.modelbin`: kontainern med chunkar

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Den deklarerade filstorleken måste vara lika med den verkliga.
- **Kedjan**: varje chunk börjar där den föregående slutade, avrundat uppåt till 4
  byte. Ingenting i filen anger detta, så det är belägg: en post som läses med fel
  steg ger inte det. Det höll för alla 252 samplade modeller.
- En `PGZP`-fil som ges till modellläsaren kallas "a ForzaTech .minizip archive, not a
  model" och hänvisas till `minizip.py`, i stället för att avvisas tomt.

Geometrin kommer från dessa chunkar:

| Chunk | Innehåll |
|---|---|
| `VLay` | en vertexlayout: attributnamn, sedan element (u16 namnindex, u16 kanal, buffert, DXGI-format, offset); elementantalet är en u16 |
| `VerB` | en vertexbuffert bakom en 16-bytes header (antal, storlek, u16 stride, u16 attribut, format) |
| `IndB` | indexbufferten, samma header |
| `Mesh` | en undermesh: material, detaljnivåmask, indexintervall, layout, buffert, stride, variantstabell och en positionsruta i slutet |
| `MatI` | en materialinstans: dess `.materialbin`-sökväg och texturhashar |

### Positioner och rutan

Positioner är `R16G16B16A16_SNORM` (format 13): fyra signerade shorts per vertex.
`position = short / 32767 * scale + bias`, där scale och bias är de sista 32 byten i
`Mesh`-chunken (två float4). Biasen är i **spelets världskoordinater**, så en
terrängruta hamnar där spelet placerar den utan någon instanstransform. Det är därför
ett varv med telemetri räcker för att begära en bit karta. Varje undermesh i en modell
bär samma ruta (kontrollerat för 860 av dem).

### Vertexlayouten

En positionsbuffert täcker alla vertexar. De andra attributen delas upp i följande
vertexgrupper, var och en med sin egen buffert och layout: väg nära en korsning har tre
UV-set och två tangenter, kanten bredvid bara en normal. Varje icke-position-attribut
är fyra byte. Vilken layout som beskriver vilken buffert avgörs av de undermeshar som
ritar från den, eftersom layouter och buffertar inte står i samma ordning (samma,
förskjuten ett steg, eller permuterad, beroende på modellen).

| DXGI-format | Kod | Används till |
|---|---|---|
| R16G16B16A16_SNORM | 13 | position (den fjärde short är normalens x) |
| R16G16_SNORM | 37 | normalens y, z |
| R16G16_UNORM | 35 | ett UV-par (kanal = vilket set) |
| R8G8B8A8_UNORM | 28 | färg eller blandvikter |
| R10G10B10A2_UNORM | 24 | tangent (inte avkodad) |
| R16_UINT | 57 | index |

**Normalen är delad.** `NORMAL` innehåller y och z. X är positionens fjärde short, som
såg ut som utfyllnad. Över hundratusentals markvertexar korrelerar den med +0,92 mot
x hos triangelns normal och med ingenting annat. Med den ligger 96 % av vertexarna på
sluttningar inom 18° från den beräknade normalen. Varje tvåkomponentskodning som prövats
utan den (oktaedrisk i alla 48 ordningar inbegripna) fick y och z rätt och x fel.

Andra positions- eller indexformat **vägras** ("only 13 (four shorts, scaled) is
implemented"; "only unsigned shorts are implemented").

### Undermeshar

En `Mesh`-post är 238 byte i standardformen. Längre poster bär en längre materialtabell
med **varianter** först, 238 + 8 x antal - 4 byte, och varje fält efter den flyttas
bakåt med exakt det beloppet. Kortare poster (218 byte, en del terräng) behåller
offseten. Varje variantpost är `u16 0xFFFF, u16 sommarmaterial, u16 0xFFFF, u16
vintermaterial`. Detaljnivåmasken är en u16, en bit per nivå från bit 1.

Ingenting litas på ensamt. Indexintervallen måste lägga sig exakt över indexbufferten,
varje `index count` måste vara lika med 3 x `triangles`, och stride som en undermesh
anger måste vara dess buffert. En tabell som misslyckas vägras helt, eftersom det är
värre att märka trianglar utifrån felläst data än att inte märka dem. Över tusentals
samplade undermeshar passerar varje en vars bufferindex ligger inom intervallet.

### Material och texturhashar

En `MatI` anger sitt material med en `Game:...\x.materialbin`-sökväg, som hittas genom
att söka i chunken. Dess texturer är `u32 slot, u32, u32 hash`-poster, 33 byte från
varandra och ojusterade, så chunken söks vid varje byteposition efter ord som är kända
texturhashar. De kommer från bananens `AssetManifest.xml`
(`<Texture Source="...\name.swatch" SourceHash="...">`, läst upp till `</Textures>`).
Slot `0x88B483AA` är standardshaderns basfärg. Hur färgtexturen sedan väljs finns på
[Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: texturfärgprov

Ett färgprov är samma `burG`-kontainer som en modell: en 96 byte stor `HCXT`-header vid
byte 44, sedan en chunk med pixlar. Headern innehåller texturens GUID (den i filnamnet),
bredd och höjd, antalet mipnivåer och **formatkoden vid byte 72** (ForzaTechs egen
numrering). Byte 84 innehåller pixelbyteantalet.

| Kod | Format | Identifierat som |
|---|---|---|
| 0 | BC1, en halv byte per pixel | avkodas till en röd och vit kantsten (brus under BC4) |
| 9 | BC7, en byte per pixel | avkodas till en terrängruta där banan syns |
| 13 | RGBA8, fyra byte per pixel | enkel |
| annat | vägras | "texture format N has not been identified; refusing to guess" |

Formaten identifierades genom att avkoda riktiga filer på alla sätt filens
payloadstorlek tillåter. Byte 47, som en tidigare version tog för formatet, är 4 i varje
samplad textur. Bara filens översta mip avkodas. Varje upplösning är en egen post,
`<name>_<guid>_quality<n>.pb`, kvalitet 1 minst till 5 störst. För terrängkartor ligger
de två största i ett annat arkiv än resten. Avkodningen går genom Pillows BCn-avkodare,
via en genererad DDS-header.

## Placeringsfiler (.pgeo)

En fil per kategori per rumslig cell:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Sökvägen ensam anger
cellens kvadrat och kategori, så filer kan filtreras utan att öppnas.

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

Hur varje fält avgjordes:

| Fält | Avgjort av |
|---|---|
| positionen är 16.16 fixpunkt, inte en andel av rutan | efterföljande räcken ligger exakt 4,000 m från varandra (modellens längd) |
| teckenmagnitud, inte tvåkomplement | tvåkomplement lade negativa koordinater tiotals kilometer utanför kartan; med bit 31 som tecken hamnar varje post i varje kategori som samplades inom sin fils ruta |
| vektorerna är modellens egna axlar | slutet på varje räcke ligger på början av nästa: 93,5 % inom 5 cm, median 0,000 m |
| byte 60 är varianten | en skylts fem kopior läses 0, 2, 2, 3, 4 medan varje räcke läser 0 |

Bara namn som slutar på `_3D` är modellposter. Variantstabellen före dem listar namn
utan suffixet, och läses som poster hamnar de i oändligheten. En kandidatpost godtas
bara om dess antal ryms i filen, och instanser med icke-ändliga tal släpps.

## Inte implementerat

- Vertex- och indexformat utom de ovan (vägras).
- Texturformat utom 0, 9, 13 (vägras).
- Tangenter (läses förbi, används inte).
- Terrängshaderns materiallager. Markens textur är en tolkning av rutkartorna (se [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
