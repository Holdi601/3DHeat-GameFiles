---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "sv"
source: reader-unreal-iostore.md
source_hash: "a71af3169c83"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 levererar det mesta av innehållet i **IoStore**-behållare: en `.utoc`-
innehållsförteckning och `.ucas`-datan den indexerar. En `.pak` finns fortfarande
kvar, men den innehåller lite mer än en footer. Läsarna här går från behållaren ner
till geometri och pixlar, så långt en bana behöver. De byggdes och kontrollerades på
Assetto Corsa Rally (Unreal 5.6.1, modifierad) och nås via banexporten
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html), och
`identify`, `list` och `extract` tar en `.utoc` (eller `.ucas` bredvid den): filerna dess katalog anger, med
deras sökväg under monteringspunkten. En behållare utan katalogindex anger inga filer och
listas inte.

| Lager | Modul |
|---|---|
| behållare och lagret | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| kylda "zen"-paket | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| oversionerad egenskapsdata | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statiska meshar | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| texturer och virtuella texturer | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Behållare (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Innehållsförteckningen, version 8 (Unreal 5.6), little-endian:

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

- Versioner äldre än 5 vägras. Bara version 8 har kontrollerats mot riktiga filer.
- **Krypterade behållare vägras**: "<file> is encrypted. This tool holds no keys and
  recovers none." Ingen nyckel kan anges för IoStore.
- Blockmetoder: lagrad, `oodle` (genom [Oodle](reader-oodle.md)), `zlib`,
  `lz4`. Allt annat vägras.
- Partitioner efter den första ligger i `<name>_s<n>.ucas`.

**Lagret** öppnar varje `.utoc` i spelets `Paks`-mapp och indexerar varje paketsökväg,
utan hänsyn till versaler och gemener. Behållare som inte går att öppna hoppas över.
`global.utoc` levererar skriptobjekten (C++-klasserna). Ett pakets bulkdata (`.ubulk`)
hittas som chunken med samma id och typen `BULK_DATA`, i vilken behållare den än ligger.

Kontrollerat: varje behållare i det installerade spelet och varje paketsökväg i den.

## Zen-paket {#zen-packages}

Ett cachat paket är en header (namn, importer, exporter, exportbuntar, beroendetabeller,
importerade paketnamn) följd av varje exports serialiserade data. Objekt pekar på
varandra med ett 64-bitars `FPackageObjectIndex` vars två översta bitar anger vad det
är: en export från detta paket, ett skriptobjekt, en import från ett annat paket (vilket
paket, och exporten via en hash av dess sökväg), eller null.

- Sammanfattningens layout ändrades i 5.3 (beroendebuntar och importerade paketnamn)
  och igen i 5.6 (två ytterligare offset). Båda layouterna prövas, och den vars
  namntabell går att parsa behålls, så versionen behöver inte vara känd.
- **Versionerade** (icke-cachade-liknande) paket vägras.
- Importerade paketnamn bär ett nummer. Ett paket `_Terrain` med nummer 1 är filen `_Terrain_0`.
- `/Game/...`-namn mappas till projektets `Content`-mapp i lagret.
- Referenser följs mellan paket genom att matcha exportens publika hash.

Kontrollerat: varje cell i varje etapp öppnas.

## Oversionerade egenskaper {#unversioned-properties}

Cachad Unreal 5-egenskapsdata namnger inte sina egenskaper. En export börjar med en
header av serier, "hoppa över så många platser, sedan så många som finns", och en mask
som anger vilka närvarande som är noll och inte bär några byte. Värdena följer i
klassens egenskapsordning. Att läsa det kräver varje klass **schema**: dess egenskapslista,
i exakt den ordning motorn bygger den (egna egenskaper först, sedan förälderns, en plats
per statisk arrayelement, egenskaper som bara finns i redigeraren utelämnade).

Scheman är inbäddade för de klasser en bana behöver:

| Klass | Kedja |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM-kedjorna (finns, men används inte av banexporten, eftersom den här versionen flyttat om dem) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

De täcker också strukturerna dessa innehåller (`FBodyInstance`, kollisionssvar och
andra). Värdetyper läses efter kodning: fasta tal och vektorer (`FVector`,
`FRotator` som double, `FTransform` ...), `FName`, enumerationer (en byte), objektreferenser
(`i32` paketindex), mjuka objektsökvägar, arrayer, kapslade strukturer och multicast-delegater (hoppas över).

Scheman är **bara egenskapsnamn och typer**, härledda från Unreal Engine 5.6.1:s headers
(som Epic gör tillgängliga för alla med ett länkat konto). Ingen motorkod ingår. Den här
versionen har **två fler platser i `UPrimitiveComponent`** än headers, och **en fler i den
virtuella texturvolymen**, funna ur datan och markerade `(unknown)`. Ett värde i en av
de platserna är ett fel, inte en gissning. En plats förbi slutet av ett schema, eller en
okänd typ, ger `PropertyError`.

Kontrollerat: varje statisk mesh- och scenkomponent i varje etapp avkodas, och slutar
exakt vid sin klass fasta svans. En spelpatch kan flytta platser. Läsaren avbryter då,
och banan redovisar hur många komponenter som misslyckades.

## Statiska meshar {#static-meshes}

Ett `UStaticMesh`-objekt är sina egenskaper följda av native-data. Egenskaperna behövs
inte för geometrin och läses inte. Den native-delen hittas via sin fasta start: en
nollställd GUID-flagga, två byte stripflaggor, `bCooked = 1` och indexet för meshens egna
`BodySetup`-objekt. Den läses sedan i den ordning `UStaticMesh::Serialize` och
`FStaticMeshRenderData::Serialize` skriver den för en **cachad, icke-Nanite**-mesh:

- upp till 16 detaljnivåer, var och en med sina sektioner (material, första index,
  antal trianglar), gränser, och när den är **inlinad**: positionsbufferten (float32
  x 3), tangenter, UV (alla kanaler, halv eller full precision), färger och indexbufferten
  (16- eller 32-bitars);
- det som följer (omvända och bara-djup-indexbuffertar, strålspårningsdata, områdesviktade
  samplare) hoppas över för att komma till nästa nivå.

En nivå som inte är lagrad inline avslutar listan. En mesh utan någon vägras.
Positionerna är Unreals: centimeter, X framåt, Y åt höger, Z uppåt.

Kontrollerat: nästan varje samplad mesh avkodas (resten är skelett), och en vägrutas
avkodade utsträckning stämmer med gränserna den lagrar.

## Texturer {#textures}

Ett `Texture2D`-objekt är sina egenskaper och sedan dess cachade plattformsdata: namnet
på pixelformatet, storleken och en tabell med mipnivåer, var och en pekande in i paketets
**bulkdatakarta** (offset, storlek, flaggor; inline i exporten när flagga `0x40` är satt,
annars i `.ubulk`). Plattformsdatan hittas via sin egen form, inte genom att hoppa över
egenskaperna, så texturklassens egenskapslayout spelar ingen roll. Den första mipnivån
som inte är större än den begärda storleken avkodas.

| Unreal-format | Avkodas som |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bitars RGBA |
| `PF_G8` | 8-bitars gråskala |

Kontrollerat: en 4096 px DXT5-satellitbild vars tretton nivåer är exakt
bulkpostens storlekar.

## Strömmade virtuella texturer {#streaming-virtual-textures}

En inbakad `VirtualTexture2D` är kvadratiska rutor med kant, per detaljnivå, adresserade
med en **Morton-kod** (x i de jämna bitarna), lagrade i chunkar i paketets bulkdata.
Layouten läses så som `FVirtualTextureBuiltData::Serialize` skriver den i Unreal 5.6:
lager, rutstorlek, kant, adresstabeller per mip för rutor, lagerformat, och chunk *n* som
bulkpost *n*. En region av texturen sätts ihop ruta för ruta, med kanterna borttagna,
från den nivå vars upplösning ligger närmast den önskade storleken. Bara det första lagret
läses, och bara i formaten ovan.

Kontrollerat: en virtuell texturchunks rutor är alla redovisade till byten.
