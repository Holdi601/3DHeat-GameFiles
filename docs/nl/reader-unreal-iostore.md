---
title: Unreal 5 IoStore
nav_order: 2
lang: "nl"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 levert het grootste deel van de inhoud in **IoStore**-containers: een `.utoc`-inhoudsopgave en de `.ucas`-data waarnaar die verwijst. Een `.pak` is er ook nog, maar die bevat weinig meer dan een footer. De lezers hier gaan van de container naar geometrie en pixels, voor zover een baan dat nodig heeft. Ze zijn gebouwd en gecontroleerd op Assetto Corsa Rally (Unreal 5.6.1, aangepast) en worden bereikt via de baan-export van [Assetto Corsa Rally](course-assetto-corsa-rally.md). `identify`, `list` en `extract` nemen een `.utoc` (of de `.ucas` ernaast): de bestanden die de map noemt, op hun pad onder het mountpunt. Een container zonder mapindex noemt geen bestanden en wordt niet getoond.

| Laag | Module |
|---|---|
| containers en de opslag | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| gecookte "zen"-pakketten | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| unversioned eigenschapsdata | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statische meshes | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| texturen en virtual textures | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Containers (`.utoc`, `.ucas`) {#containers-utoc-ucas}

De inhoudsopgave, versie 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Versies ouder dan 5 worden geweigerd. Alleen versie 8 is op echte bestanden gecontroleerd.
- **Versleutelde containers worden geweigerd**: `<file> is encrypted. This tool holds no keys and recovers none.` Voor IoStore kan geen sleutel worden meegegeven.
- Blokmethoden: ongecomprimeerd, `oodle` (via [Oodle](reader-oodle.md)), `zlib`, `lz4`. Al het andere wordt geweigerd.
- Partities na de eerste staan in `<name>_s<n>.ucas`.

De **opslag** opent elke `.utoc` in de `Paks`-map van het spel en indexeert elk pakketpad, zonder onderscheid tussen hoofdletters. Containers die niet openen, worden overgeslagen. `global.utoc` levert de scriptobjecten (C++-klassen). De bulkdata van een pakket (`.ubulk`) wordt gevonden als de chunk met dezelfde id en het type `BULK_DATA`, in welke container die ook zit.

Gecontroleerd: elke container van het geïnstalleerde spel en elk pakketpad erin.

## Zen-pakketten {#zen-packages}

Een gecookt pakket is een header (namen, imports, exports, exportbundels, afhankelijkheidstabellen, geïmporteerde pakketnamen), gevolgd door de geserialiseerde data van elke export. Objecten verwijzen naar elkaar via een 64-bit `FPackageObjectIndex` waarvan de bovenste twee bits zeggen wat het is: een export van dit pakket, een scriptobject, een import uit een ander pakket (welk pakket, en de export via een hash van zijn pad), of null.

- De samenvatting veranderde in 5.3 (afhankelijkheidsbundels en geïmporteerde pakketnamen) en opnieuw in 5.6 (twee extra offsets). Beide indelingen worden geprobeerd, en de indeling waarvan de naamtabel parseert, wordt bewaard, zodat de versie niet bekend hoeft te zijn.
- **Versioned** (ongecookte-achtige) pakketten worden geweigerd.
- Geïmporteerde pakketnamen dragen een nummer. Een pakket `_Terrain` met nummer 1 is het bestand `_Terrain_0`.
- `/Game/...`-namen worden in de opslag gekoppeld aan de map `Content` van het project.
- Verwijzingen worden over pakketten heen gevolgd door te zoeken op de publieke hash van de export.

Gecontroleerd: elke cel van elke etappe opent.

## Unversioned eigenschappen {#unversioned-properties}

Gecookte Unreal 5-exports noemen hun eigenschappen niet. Een export begint met een header van reeksen, "sla zoveel slots over, dan zoveel aanwezige", en een masker dat zegt welke aanwezige nul zijn en geen bytes dragen. De waarden volgen in de eigenschapsvolgorde van de klasse. Om dat te lezen is het **schema** van elke klasse nodig: zijn eigenschappenlijst, precies in de volgorde die de engine opbouwt (eigen eigenschappen eerst, dan die van de ouder, één slot per element van een statische array, editor-eigenschappen weggelaten).

Schema's zijn ingebed voor de klassen die een baan nodig heeft:

| Klasse | Keten |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | de ISM-ketens (aanwezig, maar niet gebruikt door de baan-export, omdat deze build ze herschikt heeft) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Ze dekken ook de structs die deze bevatten (`FBodyInstance`, botsingsreacties en andere). Waardetypen worden per codering gelezen: vaste getallen en vectoren (`FVector`, `FRotator` als doubles, `FTransform`...), `FName`, enums (één byte), objectverwijzingen (`i32`-pakketindex), zachte objectpaden, arrays, geneste structs, en multicast-delegates (overgeslagen).

De schema's bevatten **alleen eigenschapsnamen en -typen**, afgeleid van de headers van Unreal Engine 5.6.1 (die Epic beschikbaar stelt aan iedereen met een gekoppeld account). Er is geen engine-code bijgevoegd. Deze build heeft **twee extra slots in `UPrimitiveComponent`** ten opzichte van de headers, en **één extra in het virtual texture-volume**, gevonden uit de data en gemarkeerd als `(unknown)`. Een waarde in een van die slots is een fout, geen gok. Een slot voorbij het eind van een schema, of een onbekend type, geeft een `PropertyError`.

Gecontroleerd: elk statisch-mesh- en scènecomponent van elke etappe decodeert, en eindigt precies bij de vaste native staart van zijn klasse. Een patch van het spel kan slots verschuiven. De lezer geeft dan een fout, en de baan meldt hoeveel componenten mislukten.

## Statische meshes {#static-meshes}

Een `UStaticMesh`-export bestaat uit zijn eigenschappen gevolgd door native data. De eigenschappen zijn niet nodig voor de geometrie en worden niet gelezen. Het native deel wordt gevonden via zijn vaste begin: een nul-GUID-vlag, twee bytes stripvlaggen, `bCooked = 1`, en de index van het `BodySetup`-export van de mesh zelf. Daarna wordt het gelezen in de volgorde waarin `UStaticMesh::Serialize` en `FStaticMeshRenderData::Serialize` die schrijven voor een **gecookt, niet-Nanite** mesh:

- tot 16 detailniveaus, elk met zijn secties (materiaal, eerste index, aantal driehoeken), begrenzingen, en wanneer **inline**: de positiebuffer (float32 x 3), tangenten, UV's (alle kanalen, halve of volledige precisie), kleuren, en de indexbuffer (16- of 32-bit);
- wat daarna komt (omgekeerde en alleen-diepte-indexbuffers, ray-tracingdata, samplers met oppervlaktegewicht) wordt overgeslagen om bij het volgende niveau te komen.

Een niveau dat niet inline is opgeslagen, beëindigt de lijst. Een mesh zonder niveaus wordt geweigerd. Posities zijn die van Unreal: centimeters, X vooruit, Y rechts, Z omhoog.

Gecontroleerd: bijna elke gesamplede mesh decodeert (de rest zijn skeletmeshes), en de omvang van een wegtegel na decoderen komt overeen met de begrenzing die hij opslaat.

## Texturen {#textures}

Een `Texture2D`-export bestaat uit zijn eigenschappen en daarna zijn gecookte platformdata: de naam van het pixelformaat, de grootte, en een tabel van mip-niveaus, elk wijzend naar de **bulkdatakaart** van het pakket (offset, grootte, vlaggen; inline in de export als vlag `0x40` is gezet, anders in de `.ubulk`). De platformdata wordt gevonden op haar eigen vorm, niet door de eigenschappen over te slaan, dus de eigenschapsindeling van de textuurklasse doet er niet toe. Het eerste mip-niveau dat niet groter is dan de gevraagde grootte, wordt gedecodeerd.

| Unreal-formaat | Gedecodeerd als |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bit RGBA |
| `PF_G8` | 8-bit grijs |

Gecontroleerd: een satellietafbeelding van 4096 px in DXT5 waarvan de dertien niveaus precies de groottes van de bulk-items zijn.

## Streaming virtual textures {#streaming-virtual-textures}

Een gebakken `VirtualTexture2D` bestaat uit vierkante tegels met een rand, per detailniveau, geadresseerd met een **Morton-code** (x in de even bits), opgeslagen in chunks van de bulkdata van het pakket. De indeling wordt gelezen zoals `FVirtualTextureBuiltData::Serialize` die in Unreal 5.6 schrijft: lagen, tegelgrootte, rand, adrestabellen per mip-niveau, formaten per laag, en chunk *n* als bulk-item *n*. Een gebied van de textuur wordt tegel voor tegel samengesteld, randen verwijderd, uit het niveau waarvan de resolutie het dichtst bij de gewenste grootte ligt. Alleen de eerste laag wordt gelezen, en alleen in de formaten hierboven.

Gecontroleerd: de tegels van een virtual texture-chunk zijn tot op de byte verantwoord.
