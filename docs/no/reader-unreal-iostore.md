---
title: Unreal 5 IoStore
nav_order: 2
lang: "no"
source: reader-unreal-iostore.md
source_hash: "a71af3169c83"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 leverer mesteparten av innholdet i **IoStore**-beholdere: en `.utoc`-innholdsfortegnelse
og `.ucas`-dataene den indekserer. En `.pak` finnes fortsatt, men den inneholder lite mer enn en
fotdel. Leserne her går fra beholderen ned til geometri og piksler, så langt en bane trenger. De
ble bygget og kontrollert på Assetto Corsa Rally (Unreal 5.6.1, modifisert), og nås gjennom
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html)-
baneeksporten, og `identify`, `list` og `extract` tar en `.utoc` (eller `.ucas` ved siden av): filene
katalogen dens nevner, etter stien under monteringspunktet. En beholder uten katalogindeks nevner
ingen filer og listes ikke.

| Lag | Modul |
|---|---|
| beholdere og lageret | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| kokte "zen"-pakker | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| uversjonerte egenskapsdata | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statiske modeller | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| teksturer og virtuelle teksturer | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Beholderne (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Innholdsfortegnelsen, version 8 (Unreal 5.6), little-endian:

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

- Versjoner eldre enn 5 avvises. Bare versjon 8 er kontrollert på ekte filer.
- **Krypterte beholdere avvises**: "<file> is encrypted. This tool holds no keys and recovers none."
  Ingen nøkkel kan sendes inn for IoStore.
- Blokkmetoder: lagret, `oodle` (gjennom [Oodle](reader-oodle.md)), `zlib`, `lz4`. Alt annet avvises.
- Partisjoner utover den første ligger i `<name>_s<n>.ucas`.

**Lageret** åpner hver `.utoc` i spillets `Paks`-mappe og indekserer hver pakkesti, uten
store/små-bokstavforskjell. Beholdere som ikke kan åpnes, hoppes over. `global.utoc` gir
skriptobjektene (C++-klassene). En pakkes bulkdata (`.ubulk`) finnes som chunken med samme id og
typen `BULK_DATA`, i den beholderen som har den.

Kontrollert: hver beholder i det installerte spillet og hver pakkesti i den.

## Zen-pakker {#zen-packages}

En kokt pakke er en topptekst (navn, importer, eksporter, eksportbunter, avhengighetstabeller,
importerte pakkenavn) etterfulgt av hver eksports serialiserte data. Objekter refererer til
hverandre med en 64-bit `FPackageObjectIndex` der de to øverste bitene sier hva det er: en
eksport av denne pakken, et skriptobjekt, en import fra en annen pakke (hvilken pakke, og eksporten
etter en hash av stien dens), eller null.

- Oppsettet av sammendraget endret seg i 5.3 (avhengighetsbunter og importerte pakkenavn) og igjen i
  5.6 (to nye forskyvninger). Begge oppsettene prøves, og det som gir en parsbar navnetabell, beholdes,
  så versjonen trenger ikke å være kjent.
- **Versjonerte** (ukokte, uncooked-lignende) pakker avvises.
- Importerte pakkenavn har et nummer. En pakke `_Terrain` med nummer 1 er filen `_Terrain_0`.
- `/Game/...`-navn avbildes på prosjektets `Content`-mappe i lageret.
- Referanser følges på tvers av pakker ved å matche eksportens offentlige hash.

Kontrollert: hver celle av hvert trinn åpner.

## Uversjonerte egenskaper {#unversioned-properties}

Kokte Unreal 5-eksporter navngir ikke egenskapene sine. En eksport starter med en topptekst av
løp, "hopp over så mange plasser, deretter så mange til stede", og en maske som sier hvilke av de
tilstedeværende som er null og ikke har bytes. Verdiene følger i klassens egenskapsrekkefølge.
Å lese det krever hver klasses **skjema**: dens egenskapsliste, i nøyaktig den rekkefølgen motoren
bygger den (egne egenskaper først, deretter forelderens, én plass per element i en statisk matrise,
redigeringsegenskaper utelatt).

Skjemaer er innebygd for klassene en bane trenger:

| Klasse | Kjede |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM-kjedene (til stede, men ikke brukt av baneeksporten, fordi dette bygget omorganiserte dem) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

De dekker også strukturene disse holder (`FBodyInstance`, kollisjonsresponser og andre). Verditypene
leses etter koding: faste tall og vektorer (`FVector`, `FRotator` som doubles, `FTransform` ...),
`FName`, enums (én byte), objektreferanser (`i32`-pakkeindeks), myke objektstier, matriser, nøstede
strukturer og multicast-delegater (hoppes over).

Skjemaene er **bare egenskapsnavn og -typer**, avledet fra Unreal Engine 5.6.1-headerne (som Epic
gjør tilgjengelige for alle med en koblet konto). Ingen motorkode er med. Dette bygget har **to flere
plasser i `UPrimitiveComponent`** enn headerne, og **én flere i volumet for virtuell tekstur**, funnet
fra dataene og merket `(unknown)`. En verdi til stede i en av disse plassene er en feil, ikke en
gjetning. En plass forbi enden av et skjema, eller en ukjent type, gir `PropertyError`.

Kontrollert: hver statisk modell- og scenekomponent i hvert trinn dekoderer, og hver avslutter nøyaktig
ved sin klasses faste innebygde hale. En spillpatch kan flytte plasser. Leseren hever da en feil, og
banen rapporterer hvor mange komponenter som mislyktes.

## Statiske modeller {#static-meshes}

En `UStaticMesh`-eksport er sine egenskaper etterfulgt av innebygde data. Egenskapene trengs ikke for
geometrien og leses ikke. Den innebygde delen finnes ved sin faste start: et null-GUID-flagg, to byte
stripflagg, `bCooked = 1`, og indeksen til meshens egen `BodySetup`-eksport. Den leses så i
rekkefølgen `UStaticMesh::Serialize` og `FStaticMeshRenderData::Serialize` skriver den for en **kokt,
ikke-Nanite** modell:

- opptil 16 detaljnivåer, hver med sine seksjoner (materiale, første indeks, antall trekanter), grenser,
  og når de er **innebygd**: posisjonsbufferen (float32 x 3), tangenter, UV-er (alle kanaler, halv eller
  full presisjon), farger, og indeksbufferen (16- eller 32-bit);
- det som følger (reverserte og bare-dybde-indeksbuffere, strålesporingsdata, områdevektede
  samplere) hoppes over for å nå neste nivå.

Et nivå som ikke er lagret innebygd, avslutter listen. En modell uten noen avvises. Posisjoner er
Unreals: centimeter, X fremover, Y høyre, Z opp.

Kontrollert: nesten hver stikkprøvet modell dekoderer (resten er skjelettmodeller), og et veiflis' dekodede
utstrekning stemmer med grensene det lagrer.

## Teksturer {#textures}

En `Texture2D`-eksport er sine egenskaper og deretter sine kokte plattformdata: navnet på pikselformatet,
størrelsen, og en tabell med mipnivåer, der hvert peker inn i pakkens **bulkdata-kart** (forskyvning,
størrelse, flagg; innebygd i eksporten når flagg `0x40` er satt, ellers i `.ubulk`). Plattformdataene
finnes etter sin egen form, ikke ved å hoppe over egenskapene, så teksturklassens egenskapsoppsett
spiller ingen rolle. Det første mipnivået som ikke er større enn den forespurte størrelsen, dekodes.

| Unreal-format | Dekodet som |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bit RGBA |
| `PF_G8` | 8-bit gråtone |

Kontrollert: et 4096 px DXT5-satellittbilde der tretten nivåer er nøyaktig størrelsene til bulk-oppføringene.

## Strømmede virtuelle teksturer {#streaming-virtual-textures}

En innbakt `VirtualTexture2D` er kvadratiske fliser med en kant, per detaljnivå, adressert med en
**Morton-kode** (x i de partall-bitene), lagret i chunker i pakkens bulkdata. Oppsettet leses slik
`FVirtualTextureBuiltData::Serialize` skriver det i Unreal 5.6: lag, flisstørrelse, kant, adressetabeller
per mip for flisene, lagformater, og chunk *n* som bulk-oppføring *n*. En region av teksturen settes
sammen flis for flis, med kantene fjernet, fra nivået hvis oppløsning er nærmest den ønskede størrelsen.
Bare det første laget leses, og bare i formatene over.

Kontrollert: en virtuell teksturchunks fliser er regnskapsført til byten.
