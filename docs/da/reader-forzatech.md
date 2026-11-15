---
title: "ForzaTech: `.minizip`, `.modelbin`, farveprøver, placeringer"
nav_order: 7
lang: "da"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, farveprøver, placeringer {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon kører på ForzaTech, Turn 10's egen motor. Disse læsere tager en bane fra dens arkiver ned til placerede, teksturerede trekanter. De nås via `course`, `courses` og `terrain` (se [Forza Horizon](course-forza-horizon.md)). `identify` genkender en `.minizip` og en nøgen `.modelbin`, og `list` og `extract` tager en `.minizip`, efter navnene i `ChunkContentsMiniZip<n>.txt` ved siden af den eller efter postnummer (`#12`).

| Format | Modul |
|---|---|
| `.minizip`-arkiver og deres navnelister | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin`-modeller og terræn | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb`-teksturfarveprøver | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo`-placeringsfiler | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` og materialeteksturhashes | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| terrænfliser efter sted | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza gemmer også meget af sit indhold i almindelige ZIP-arkiver under `media\`. Pythons `zipfile` åbner dem, og `forzatech.models_in_archive()` lister deres `.modelbin`-poster. Banens geometri ligger i `.minizip`-arkiverne.

## `.minizip`: et arkiv uden navne {#minizip-an-archive-with-no-names}

En bane leveres med fire `GeoChunk<n>.minizip`-arkiver, titalls gigabyte hver for et åbent kort, med hundredtusindvis af poster. **Arkiverne gemmer slet ingen navne**: ingen navnetabel og ingen header pr. post, kun et løbenummer. Navnene findes i `ChunkContentsMiniZip<n>.txt` ved siden af hvert arkiv, én linje pr. post i postrækkefølge (`<build path>zipcache\pc\<path>|<bundle>`). Den parring er den eneste måde at bede om en fil. Alt op til `zipcache\pc\` droppes, og opslag ser bort fra store og små bogstaver.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tre detaljer i indekset giver stadig output, når de læses forkert. Læseren får alle tre rigtige:

| Detalje | Hvad en skødesløs læser gør | Hvordan det ser ud |
|---|---|---|
| segmentbasen er **64-bit** | læser den som u32 plus padding | rigtig for de første 4 GB, derefter støj af den rigtige længde |
| basen er **8-byte-justeret** | ignorerer padding-ordet efter bundle-tabellen | i arkiver med et lige antal bundles påstår hver post en codec, der ikke findes |
| en posts gemte længde er mellemrummet til næste post (eller næste segments base) **minus dens padding** (flagbit 12-13) | bruger hele mellemrummet | LZ4 afviser blokken helt |

Codecs er de laveste fem bit i flagene: `0x00` gemt, `0x08` rå deflate, `0x1F` LZ4-blok. Alle andre afvises. Hver post skal pakkes ud til præcis den størrelse, den angiver, ellers afvises den. Indekset (ca. 5 MB) læses én gang, og nyttelaster læses ved at søge.

Headeren tjekkes: magic, en 32-byte header og et segmenttal, der passer med `ceil(entries / per segment)`.

**Verificeret:** poster stikprøvet på tværs af hvert arkiv i et kort, hver pakket ud til præcis sin angivne længde under alle tre codecs.

## `.modelbin`: chunk-containeren {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Den angivne filstørrelse skal være lig den rigtige størrelse.
- **Kæden**: hver chunk starter, hvor den forrige sluttede, afrundet op til 4 bytes. Intet i filen angiver dette, så det er et bevis: en post læst med forkert skridtlængde giver det ikke. Det holdt for alle 252 stikprøvede modeller.
- En `PGZP`-fil givet til modellæseren navngives som "a ForzaTech .minizip archive, not a model" og henvises til `minizip.py`, frem for at blive afvist tomt.

Geometrien kommer fra disse chunks:

| Chunk | Indeholder |
|---|---|
| `VLay` | en vertexlayout: attributnavne, derefter elementer (u16 navneindeks, u16 kanal, buffer, DXGI-format, offset); elementantallet er en u16 |
| `VerB` | en vertexbuffer bag en 16-byte header (antal, størrelse, u16 skridt, u16 attributter, format) |
| `IndB` | indeksbufferen, samme header |
| `Mesh` | én undermesh: materiale, detaljeniveau-maske, indeksinterval, layout, buffer, skridt, variantetabel og en positionsboks til sidst |
| `MatI` | en materialeinstans: dens `.materialbin`-sti og teksturhashes |

### Positioner og boksen {#positions-and-the-box}

Positioner er `R16G16B16A16_SNORM` (format 13): fire signerede shorts pr. vertex. `position = short / 32767 * scale + bias`, hvor scale og bias er de sidste 32 bytes af `Mesh`-chunken (to float4'er). Bias er i **spillets verdenskoordinater**, så en terrænflise lander, hvor spillet placerer den, uden nogen instanstransformation. Derfor er en runde telemetri nok til at bede om et stykke kort. Hver undermesh i en model bærer den samme boks (tjekket på 860 af dem).

### Vertexlayoutet {#the-vertex-layout}

Én positionsbuffer dækker hver vertex. De andre attributter er delt op i sammenhængende vertexgrupper, hver med sin egen buffer og sin egen layout: vej nær et kryds bærer tre UV-sæt og to tangenter, skrænten ved siden kun en normal. Hver ikke-position-attribut er fire bytes. Hvilken layout der beskriver hvilken buffer, tages fra de undermeshes, der tegner fra den, fordi layouts og buffere ikke er i samme rækkefølge (ens, roteret med én, eller ombyttet, afhængigt af modellen).

| DXGI-format | Kode | Bruges til |
|---|---|---|
| R16G16B16A16_SNORM | 13 | position (den fjerde short er normalens x) |
| R16G16_SNORM | 37 | normal y, z |
| R16G16_UNORM | 35 | et UV-par (kanal = hvilket sæt) |
| R8G8B8A8_UNORM | 28 | farve eller blandevægte |
| R10G10B10A2_UNORM | 24 | tangent (ikke afkodet) |
| R16_UINT | 57 | indekser |

**Normalen er delt.** `NORMAL` indeholder y og z. X'et er positionens fjerde short, som lignede padding. Over hundredtusindvis af terrænvertices korrelerer den +0,92 med x'et i trekantnormalen og med intet andet. Med den ligger 96 % af skråningsvertices inden for 18° af den beregnede normal. Hver to-komponent-kodning, der blev prøvet uden den (oktaedrisk i alle 48 arrangementer blandt dem), fik y og z rigtige og x forkert.

Andre positions- eller indeksformater **afvises** ("only 13 (four shorts, scaled) is implemented"; "only unsigned shorts are implemented").

### Undermeshes {#submeshes}

En `Mesh`-post er 238 bytes i standardformen. Længere poster bærer en længere materiale-**variant**tabel forrest, 238 + 8 x antal - 4 bytes, og hvert felt efter den flyttes præcis så meget tilbage. Kortere (218 bytes, noget terræn) beholder offsets. Hver variantpost er `u16 0xFFFF, u16 sommermateriale, u16 0xFFFF, u16 vintermateriale`. Detaljeniveau-masken er en u16, én bit pr. niveau fra bit 1.

Intet stoles på alene. Indeksintervallerne skal dække indeksbufferen præcist, hvert `index count` skal være lig 3 x `triangles`, og det skridt, en undermesh angiver, skal være dens buffers. En tabel, der fejler, afvises helt, for det er værre at mærke trekanter ud fra fejllæste felter end ikke at mærke dem. På tværs af tusinder af stikprøvede undermeshes består hver, hvis bufferindeks er i området.

### Materialer og teksturhashes {#materials-and-texture-hashes}

En `MatI` navngiver sit materiale med en `Game:...\x.materialbin`-sti, fundet ved at søge i chunken. Dens teksturer er `u32 slot, u32, u32 hash`-poster, 33 bytes fra hinanden og uden justering, så chunken søges ved hvert byte-offset efter ord, der er kendte teksturhashes. Disse kommer fra banens `AssetManifest.xml` (`<Texture Source="...\name.swatch" SourceHash="...">`, læst op til `</Textures>`). Slot `0x88B483AA` er standard-shaderens grundfarve. Hvordan farveteksturen så vælges, står under [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: teksturfarveprøver {#pb-texture-swatches}

En farveprøve er den samme `burG`-container som en model: en 96-byte `HCXT`-header ved byte 44, derefter én chunk med pixels. Headeren indeholder teksturens GUID (den i dens filnavn), bredde og højde, antallet af mip-niveauer og **formatkoden ved byte 72** (ForzaTechs egen nummerering). Byte 84 indeholder antallet af pixel-bytes.

| Kode | Format | Identificeret som |
|---|---|---|
| 0 | BC1, en halv byte pr. pixel | afkodes til en rød og hvid kantsten (støj under BC4) |
| 9 | BC7, én byte pr. pixel | afkodes til en terrænflise med banen synlig |
| 13 | RGBA8, fire bytes pr. pixel | almindelig |
| andet | afvist | "texture format N has not been identified; refusing to guess" |

Formaterne blev identificeret ved at afkode rigtige filer på alle måder, nyttelastens størrelse tillader. Byte 47, som en tidligere version tog for formatet, er 4 i alle de stikprøvede teksturer. Kun filens øverste mip-niveau afkodes. Hver opløsning er sin egen post, `<name>_<guid>_quality<n>.pb`, kvalitet 1 mindst til 5 størst. For terrænkort ligger de to største i et andet arkiv end resten. Afkodning går via Pillows BCn-afkoder, via en genereret DDS-header.

## Placeringsfiler (.pgeo) {#placement-files-pgeo}

Én fil pr. kategori pr. rumlig celle: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Stien alene giver cellens kvadrat og kategori, så filer kan filtreres uden at åbne dem.

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

Sådan blev hvert felt afgjort:

| Felt | Afgjort af |
|---|---|
| position er 16.16 fastkomma, ikke en brøkdel af boksen | på hinanden følgende autoværnssektioner er præcis 4,000 m fra hinanden (modellens længde) |
| fortegn-og-størrelse, ikke tokomplement | tokomplement satte negative koordinater titalls kilometer ved siden af kortet; med bit 31 som fortegn lander hver post i hver stikprøvet kategori inden for sin fils boks |
| vektorerne er modellens egne akser | enden af hver autoværnssektion lander på starten af den næste: 93,5 % inden for 5 cm, median 0,000 m |
| byte 60 er varianten | en billboards fem kopier læses 0, 2, 2, 3, 4, mens hver autoværnssektion læses 0 |

Kun navne, der ender på `_3D`, er modelposter. Variantabellen før dem lister navne uden suffikset, og læst som poster lander de i uendeligheden. En kandidatpost accepteres kun, hvis dens antal passer i filen, og forekomster med ikke-endelige tal udelades.

## Ikke implementeret {#not-implemented}

- Vertex- og indeksformater ud over dem ovenfor (afvist).
- Teksturformater ud over 0, 9, 13 (afvist).
- Tangenter (læses forbi, bruges ikke).
- Terrænshaderens materiallag. Jordteksturen er en fortolkning af flisekortene (se [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
