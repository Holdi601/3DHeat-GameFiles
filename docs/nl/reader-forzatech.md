---
title: ForzaTech
nav_order: 7
lang: "nl"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, swatches, plaatsingen {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon draait op ForzaTech, de eigen engine van Turn 10. Deze lezers nemen een baan uit zijn archieven en brengen die terug tot geplaatste, getextureerde driehoeken. Ze worden bereikt via `course`, `courses` en `terrain` (zie [Forza Horizon](course-forza-horizon.md)). `identify` herkent een `.minizip` en een kale `.modelbin`, en `list` en `extract` nemen een `.minizip`, op de namen in de `ChunkContentsMiniZip<n>.txt` ernaast of op itemnummer (`#12`).

| Formaat | Module |
|---|---|
| `.minizip`-archieven en hun naamlijsten | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin`-modellen en terrein | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb`-texturswatches | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo`-plaatsingsbestanden | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` en hashes van materiaaltexturen | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| terreintegels op plaats | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza bewaart ook veel inhoud in gewone ZIP-archieven onder `media\`. Pythons `zipfile` opent die, en `forzatech.models_in_archive()` somt hun `.modelbin`-items op. De geometrie van de baan zit in de `.minizip`-archieven.

## `.minizip`: een archief zonder namen {#minizip-an-archive-with-no-names}

Een baan levert vier `GeoChunk<n>.minizip`-archieven, elk tientallen gigabytes voor een open-wereldkaart, met honderdduizenden items. **De archieven slaan helemaal geen namen op**: geen naamtabel en geen header per item, alleen een volgnummer. De namen staan in `ChunkContentsMiniZip<n>.txt` naast elk archief, één regel per item in itemvolgorde (`<build path>zipcache\pc\<path>|<bundle>`). Die koppeling is de enige manier om een bestand op te vragen. Alles tot en met `zipcache\pc\` wordt weggelaten, en opzoeken negeert hoofdletters.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Drie details in de index leveren nog uitvoer op als ze verkeerd gelezen worden. De lezer heeft alle drie goed:

| Detail | Wat een onzorgvuldige lezer doet | Hoe het eruitziet |
|---|---|---|
| de segmentbasis is **64-bit** | leest hem als u32 plus vulling | correct voor de eerste 4 GB, daarna ruis van de juiste lengte |
| de basis is **8-byte uitgelijnd** | negeert het vulwoord na de bundeltabel | in archieven met een even aantal bundels claimt elk item een codec die niet bestaat |
| de opgeslagen lengte van een item is de afstand tot het volgende item (of de basis van het volgende segment) **min zijn vulling** (vlagbits 12-13) | gebruikt de hele afstand | LZ4 weigert het blok helemaal |

Codecs zijn de laagste vijf bits van de vlaggen: `0x00` ongecomprimeerd, `0x08` ruwe deflate, `0x1F` LZ4-blok. Elke andere wordt geweigerd. Elk item moet precies de grootte uitpakken die het opgeeft, anders wordt het geweigerd. De index (ongeveer 5 MB) wordt eenmaal gelezen, en payloads worden gelezen door te zoeken.

De header wordt gecontroleerd: magic, een header van 32 bytes, en een aantal segmenten dat overeenkomt met `ceil(entries / per segment)`.

**Gecontroleerd:** items uit elk archief van een kaart gesampled, die elk onder alle drie codecs precies hun opgegeven lengte uitpakken.

## `.modelbin`: de chunkcontainer {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- De opgegeven bestandsgrootte moet gelijk zijn aan de echte grootte.
- De **keten**: elke chunk begint waar de vorige eindigde, afgerond op 4 bytes. Niets in het bestand zegt dit, dus het is bewijs: een record dat met de verkeerde stap gelezen wordt, levert dit niet op. Het hield voor alle 252 gesamplede modellen.
- Een `PGZP`-bestand dat aan de modellezer wordt gegeven, wordt aangeduid als "a ForzaTech .minizip archive, not a model" en naar `minizip.py` verwezen, in plaats van zonder meer geweigerd.

Geometrie komt uit deze chunks:

| Chunk | Bevat |
|---|---|
| `VLay` | een vertexindeling: attribuutnamen, dan elementen (u16 naamindex, u16 kanaal, buffer, DXGI-formaat, offset); het aantal elementen is een u16 |
| `VerB` | een vertexbuffer achter een header van 16 bytes (aantal, grootte, u16 stride, u16 attributen, formaat) |
| `IndB` | de indexbuffer, zelfde header |
| `Mesh` | één submesh: materiaal, detailniveaumasker, indexbereik, indeling, buffer, stride, variantentabel, en een positiedoos aan het eind |
| `MatI` | een materiaalinstantie: zijn `.materialbin`-pad en texturhashes |

### Posities en de doos {#positions-and-the-box}

Posities zijn `R16G16B16A16_SNORM` (formaat 13): vier ondertekende shorts per vertex. `position = short / 32767 * scale + bias`, waarbij scale en bias de laatste 32 bytes van de `Mesh`-chunk zijn (twee float4's). De bias staat in **de wereldcoördinaten van het spel**, dus een terreintegel komt precies waar het spel hem zet, zonder instantie-transformatie. Daarom is één telemetrieronde genoeg om om een stuk kaart te vragen. Elke submesh van een model draagt dezelfde doos (gecontroleerd op 860 ervan).

### De vertexindeling {#the-vertex-layout}

Eén positiebuffer dekt elke vertex. De andere attributen zijn verdeeld in opeenvolgende vertexgroepen, elk met een eigen buffer en eigen indeling: weg bij een kruispunt heeft drie UV-sets en twee tangenten, de berm ernaast alleen een normaal. Elk niet-positie-attribuut is vier bytes. Welke indeling bij welke buffer hoort, wordt bepaald uit de submeshes die uit die buffer tekenen, omdat indelingen en buffers niet in dezelfde volgorde staan (gelijk, één verschoven, of door elkaar, afhankelijk van het model).

| DXGI-formaat | Code | Gebruikt voor |
|---|---|---|
| R16G16B16A16_SNORM | 13 | positie (de vierde short is de x van de normaal) |
| R16G16_SNORM | 37 | normaal y, z |
| R16G16_UNORM | 35 | een UV-paar (kanaal = welke set) |
| R8G8B8A8_UNORM | 28 | kleur of gewichten van blends |
| R10G10B10A2_UNORM | 24 | tangent (niet gedecodeerd) |
| R16_UINT | 57 | indices |

**De normaal is gesplitst.** `NORMAL` bevat y en z. De x is de vierde short van de positie, die eruitzag als opvulling. Over honderdduizenden terreinvertices correleert hij +0,92 met de x van de driehoeksnormaal en met niets anders. Daarmee valt 96% van de vertices op hellende grond binnen 18° van de berekende normaal. Elke codering van twee componenten die zonder hem is geprobeerd (octaëder in alle 48 rangschikkingen inbegrepen) kreeg y en z goed en x fout.

Andere positie- of indexformaten worden **geweigerd** (`only 13 (four shorts, scaled) is implemented`; `only unsigned shorts are implemented`).

### Submeshes {#submeshes}

Een `Mesh`-record is 238 bytes in de standaardvorm. Langere records hebben vooraan een langere materiaal-**variant**tabel, 238 + 8 x aantal - 4 bytes, en elk veld daarna schuift precies zoveel terug. Kortere (218 bytes, sommig terrein) houden de offsets. Elk variantitem is `u16 0xFFFF, u16 zomermateriaal, u16 0xFFFF, u16 wintermateriaal`. Het detailniveaumasker is een u16, één bit per niveau vanaf bit 1.

Niets wordt alleen vertrouwd. De indexbereiken moeten de indexbuffer precies vullen, elk `index count` moet gelijk zijn aan 3 x `triangles`, en de stride die een submesh noemt, moet die van zijn buffer zijn. Een tabel die faalt, wordt in zijn geheel geweigerd, omdat driehoeken labelen met verkeerd gelezen velden erger is dan ze niet labelen. Over duizenden gesamplede submeshes slaagde elke submesh waarvan het bufferindex in bereik ligt.

### Materialen en texturhashes {#materials-and-texture-hashes}

Een `MatI` noemt zijn materiaal met een pad `Game:...\x.materialbin`, gevonden door de chunk te doorzoeken. Zijn texturen zijn `u32 slot, u32, u32 hash`-records, 33 bytes uit elkaar en niet uitgelijnd, dus de chunk wordt op elke byte-offset doorzocht naar woorden die bekende texturhashes zijn. Die komen uit het `AssetManifest.xml` van de baan (`<Texture Source="...\name.swatch" SourceHash="...">`, gelezen tot `</Textures>`). Slot `0x88B483AA` is de basiskleur van de standaardshader. Hoe de kleurtextuur daarna wordt gekozen, staat op [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: texturswatches {#pb-texture-swatches}

Een swatch is dezelfde `burG`-container als een model: een header `HCXT` van 96 bytes op byte 44, daarna één chunk met pixels. De header bevat de GUID van de textuur (die in zijn bestandsnaam staat), breedte en hoogte, het aantal mips, en de **formatcode op byte 72** (de eigen nummering van ForzaTech). Byte 84 bevat het aantal pixelbytes.

| Code | Formaat | Herkend als |
|---|---|---|
| 0 | BC1, een halve byte per pixel | decodeert tot een rood-witte kantsteen (ruis onder BC4) |
| 9 | BC7, één byte per pixel | decodeert tot een terreintegel waarop het circuit te zien is |
| 13 | RGBA8, vier bytes per pixel | gewoon |
| overig | geweigerd | `texture format N has not been identified; refusing to guess` |

Formaten zijn herkend door echte bestanden te decoderen op alle manieren die de payloadgrootte toelaat. Byte 47, dat een eerdere versie voor het formaat hield, is in elke gesamplede textuur 4. Alleen het bovenste mip-niveau van een bestand wordt gedecodeerd. Elke resolutie is een eigen item, `<name>_<guid>_quality<n>.pb`, kwaliteit 1 het kleinst tot 5 het grootst. Voor terreinkaarten staan de twee grootste in een ander archief dan de rest. Decoderen gaat via de BCn-decoder van Pillow, via een gegenereerde DDS-header.

## Plaatsingsbestanden (.pgeo) {#placement-files-pgeo}

Eén bestand per categorie per ruimtelijke cel: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Het pad alleen geeft het vierkant en de categorie van de cel, zodat bestanden gefilterd kunnen worden zonder ze te openen.

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

Hoe elk veld is bepaald:

| Veld | Bepaald door |
|---|---|
| positie is 16.16 vaste komma, geen breuk van de doos | opeenvolgende vangrails liggen precies 4,000 m uit elkaar (de lengte van het model) |
| tekengebit met teken, niet twee-complement | twee-complement zette negatieve coördinaten tientallen kilometers naast de kaart; met bit 31 als teken valt elk record van elke categorie gesampled binnen de doos van zijn bestand |
| de vectoren zijn de eigen assen van het model | het eind van elke vangrail valt op het begin van de volgende: 93,5% binnen 5 cm, mediaan 0,000 m |
| byte 60 is de variant | de vijf kopieën van een billboard lezen 0, 2, 2, 3, 4, terwijl elke vangrail 0 leest |

Alleen namen die op `_3D` eindigen zijn modelrecords. De variantentabel ervoor noemt namen zonder het achtervoegsel, en als die als records gelezen worden, komen ze in oneindig terecht. Een kandidaatrecord wordt alleen aanvaard als zijn aantal in het bestand past, en instanties met niet-eindige getallen worden weggelaten.

## Niet geïmplementeerd {#not-implemented}

- Vertex- en indexformaten anders dan hierboven (geweigerd).
- Texturformaten anders dan 0, 9, 13 (geweigerd).
- Tangenten (gelezen en overgeslagen, niet gebruikt).
- De materiaallagen van de terreinshader. De grondtextuur is een interpretatie van de tegelkaarten (zie [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
