---
title: Unreal 5 IoStore
nav_order: 2
lang: "da"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 leverer det meste indhold i **IoStore**-containere: en `.utoc`-indholdsfortegnelse og de `.ucas`-data, den indekserer. En `.pak` findes stadig, men den indeholder lidt mere end en footer. Læserne her går fra containeren ned til geometri og pixels, så langt en bane kræver. De er bygget og tjekket på Assetto Corsa Rally (Unreal 5.6.1, ændret) og nås via [Assetto Corsa Rally](course-assetto-corsa-rally.md)-course-eksporten. `identify`, `list` og `extract` tager en `.utoc` (eller `.ucas` ved siden af): filerne dens mappe navngiver, efter deres sti under monteringspunktet. En container uden mappeindeks navngiver ingen filer og listes ikke.

| Lag | Modul |
|---|---|
| containere og lageret | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| bagte "zen"-pakker | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| uversionerede egenskabsdata | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statiske meshes | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| teksturer og virtuelle teksturer | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Containere (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Indholdsfortegnelsen, version 8 (Unreal 5.6), little-endian:

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

- Versioner ældre end 5 afvises. Kun version 8 er tjekket på rigtige filer.
- **Krypterede containere afvises**: "<file> is encrypted. This tool holds no keys and recovers none." Der kan ikke sendes en nøgle ind for IoStore.
- Blok-metoder: gemt, `oodle` (via [Oodle](reader-oodle.md)), `zlib`, `lz4`. Alt andet afvises.
- Partitioner ud over den første ligger i `<name>_s<n>.ucas`.

**Lageret** åbner hver `.utoc` i spillets `Paks`-mappe og indekserer hver pakkesti uden hensyn til store og små bogstaver. Containere, der ikke kan åbnes, springes over. `global.utoc` leverer script-objekterne (C++-klasser). En pakkes bulkdata (`.ubulk`) findes som chunken med samme id og typen `BULK_DATA`, i den container, der har den.

Tjekket: hver container i det installerede spil og hver pakkesti i den.

## Zen-pakker {#zen-packages}

En bagt pakke er en header (navne, importer, eksporter, eksport-bundles, afhængighedstabeller, importerede pakkenavne) efterfulgt af hver eksports serialiserede data. Objekter henviser til hinanden med en 64-bit `FPackageObjectIndex`, hvis to øverste bit siger, hvad det er: en eksport fra denne pakke, et script-objekt, en import fra en anden pakke (hvilken pakke, og eksporten via et hash af dens sti) eller null.

- Oversigts-layoutet ændrede sig i 5.3 (afhængighedsbundles og importerede pakkenavne) og igen i 5.6 (to flere offsets). Begge layouts prøves, og det, hvis navnetabel kan parses, beholdes, så versionen ikke behøver at være kendt.
- **Versionerede** pakker (i ubagt stil) afvises.
- Importerede pakkenavne bærer et nummer. En pakke `_Terrain` nummereret 1 er filen `_Terrain_0`.
- `/Game/...`-navne afbildes på projektets `Content`-mappe i lageret.
- Henvisninger følges på tværs af pakker ved at matche eksportens offentlige hash.

Tjekket: hver celle i hver etape åbnes.

## Uversionerede egenskaber {#unversioned-properties}

Bagte Unreal 5-eksporter navngiver ikke deres egenskaber. En eksport starter med en header af løb, "spring så mange pladser over, og så så mange til stede", og en maske, der siger, hvilke tilstedeværende der er nul og ingen bytes bærer. Værdierne følger i klassens egenskabsrækkefølge. At læse det kræver hver klasses **skema**: dens egenskabsliste, i præcis den rækkefølge motoren bygger den (egne egenskaber først, derefter forældrens, én plads pr. element i et statisk array, egenskaber kun for editoren udeladt).

Skemaer er indlejret for de klasser, en bane har brug for:

| Klasse | Kæde |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM-kæderne (til stede, men ikke brugt af course-eksporten, fordi denne build omarrangerede dem) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

De dækker også de structs, disse holder (`FBodyInstance`, kollisionsrespons og andre). Værdityper læses efter kodning: tal og vektorer med fast størrelse (`FVector`, `FRotator` som doubles, `FTransform` ...), `FName`, enums (én byte), objektreferencer (`i32` pakkeindeks), bløde objektstier, arrays, indlejrede structs og multicast-delegater (springes over).

Skemaerne er **kun egenskabsnavne og typer**, udledt af Unreal Engine 5.6.1-headerne (som Epic gør tilgængelige for alle med en tilknyttet konto). Der er ingen motorkode med. Denne build har **to flere pladser i `UPrimitiveComponent`** end headerne, og **en mere i det virtuelle teksturvolumen**, fundet ud fra dataene og markeret `(unknown)`. En værdi til stede i en af de pladser er en fejl, ikke et gæt. En plads ud over slutningen af et skema eller en ukendt type rejser `PropertyError`.

Tjekket: hver statisk-mesh- og scenekomponent i hver etape afkodes, og hver slutter præcis ved sin klasses faste native hale. En spilopdatering kan flytte pladser. Læseren rejser da en fejl, og banen rapporterer, hvor mange komponenter der fejlede.

## Statiske meshes {#static-meshes}

En `UStaticMesh`-eksport er dens egenskaber efterfulgt af native data. Egenskaberne er ikke nødvendige for geometri og læses ikke. Den native del findes ud fra dens faste start: et nul-GUID-flag, to bytes strip-flag, `bCooked = 1` og indekset for meshens egen `BodySetup`-eksport. Den læses derefter i den rækkefølge, `UStaticMesh::Serialize` og `FStaticMeshRenderData::Serialize` skriver den for en **bagt, ikke-Nanite**-mesh:

- op til 16 detaljeniveauer, hver med sine sektioner (materiale, første indeks, antal trekanter), grænser, og når de er **inlinet**: positionsbufferen (float32 x 3), tangenter, UV'er (alle kanaler, halv eller fuld præcision), farver og indeksbufferen (16- eller 32-bit);
- det, der følger (omvendte og kun-dybde indeksbuffere, ray-tracing-data, areal-vægtede samplere), springes over for at nå næste niveau.

Et niveau, der ikke er gemt inline, afslutter listen. En mesh uden nogen afvises. Positioner er Unreals: centimeter, X fremad, Y til højre, Z op.

Tjekket: næsten hver stikprøvet mesh afkodes (resten er skeletmeshes), og en vejflises afkodede udstrækning passer med de grænser, den gemmer.

## Teksturer {#textures}

En `Texture2D`-eksport er dens egenskaber og derefter dens bagte platformdata: pixelformatnavnet, størrelsen og en tabel af mip-niveauer, der hver peger ind i pakkens **bulkdata-kort** (offset, størrelse, flag; inline i eksporten når flag `0x40` er sat, ellers i `.ubulk`). Platformdataene findes ud fra deres egen form, ikke ved at springe egenskaberne over, så teksturklassens egenskabs-layout betyder ikke noget. Det første mip-niveau, der ikke er større end den ønskede størrelse, afkodes.

| Unreal-format | Afkodes som |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bit RGBA |
| `PF_G8` | 8-bit gråtone |

Tjekket: et 4096 px DXT5-satellitbillede, hvis tretten niveauer præcist er størrelserne på bulk-posterne.

## Streaming-virtuelle teksturer {#streaming-virtual-textures}

En bagt `VirtualTexture2D` er kvadratiske fliser med en kant, pr. detaljeniveau, adresseret med en **Morton-kode** (x i de lige bit), gemt i chunks af pakkens bulkdata. Layoutet læses, som `FVirtualTextureBuiltData::Serialize` skriver det i Unreal 5.6: lag, flisestørrelse, kant, adressetabeller for fliser pr. mip, lagformater, og chunk *n* som bulk-post *n*. Et område af teksturen samles flise for flise, kanterne fjernet, fra det niveau, hvis opløsning er tættest på den ønskede størrelse. Kun det første lag læses, og kun i formaterne ovenfor.

Tjekket: en virtuel teksturchunks fliser er gjort op til byte.
