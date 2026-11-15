---
title: Arkivlæsere
nav_order: 9
lang: "da"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Arkivlæsere {#archive-readers}

En **container** (eller arkiv) er én stor fil, som et spil pakker mange filer ind i. En **CRC** eller hash er et kort fingeraftryk af nogle bytes: passer det, er bytes læst rigtigt. En **bounding box** (afgrænsningsboks) er den mindste boks omkring en model.

Under kommandoerne ligger læsere til de containere, spil leverer. Deres formater er udokumenterede, bortset fra Valves VPK og BeamNGs `.cdae`, så "understøttet" skal betyde **verificeret mod rigtige filer**, ikke "gik ikke ned". Hver læser tjekker sig selv mod noget, formatet garanterer: en hash, en CRC, en kæde af offsets der skal lukke sig, eller en gemt bounding box. Hvor et tjek fejler, afviser læseren med en besked i stedet for at gætte. En forkert mesh ser ud som en rigtig, indtil nogen stiller den ved siden af banen.

| Læser | Modul | Kan læse | Kan ikke læse | Nås fra |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versionerne 8-12: indeks, poster, Zlib-, Gzip- og Oodle-blokke, AES med en nøgle du selv angiver | versioner før 8, indeks med kun stihash, overløbsposter, asset-indhold | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, kontrolleret på v8), zen-pakker, uversionerede egenskaber for nogle få komponentklasser, bagte statiske meshes, teksturer, streaming-virtuelle teksturer | krypterede containere, versionerede pakker, meshes kun med Nanite, andre klassers egenskaber | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle-blokke via et bibliotek, der allerede er på maskinen | alt uden et sådant bibliotek; det medleveres aldrig | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22+ (Unity 2020 til 6000), `UnityFS`-bundles, ukomprimerede meshes inkl. `.resS` | formater før 2020, indlejrede typetræer, komprimerede meshes, enhver klasse undtagen `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc`-DbObject-træer og binære sektionstabeller, installationspakker, chunk-placeringer, inline-bundles og deres manifester, RIFF EBX-partitioner, MeshSet-meshes, terrænets højdefelt, BC1/BC3/BC7-teksturer og deres shaderblokke, placering af statiske modelgrupper | XOR-slørede tabeller, terrænets farve tæt på jorden og huller, normalmaps, alfa ud over udklip | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | version 1 og 2, delte arkiver, preload-data, CRC-tjek | kompilerede assets (`.vmdl_c`, `.vtex_c`), CS2's navmesh-format | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, gemt), `.modelbin`-geometri, `.pb`-farveprøver (BC1, BC7, RGBA), `.pgeo`-placeringer, materialeteksturhashes | andre vertex- og indeksformater, andre teksturformater, terrænshaderens materiallag | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` og `extract` (`.minizip`) |
| [BeamNG-filer](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | det monterede zip-filsystem, scene-JSON og TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materialer | skinnede og decal-meshes, animerede sekvenser, procedural jordbevoksning | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` og `extract` (zip) |

## Regler alle læsere følger {#rules-every-reader-follows}

- **Ingen nøgler medleveret, ingen fundet.** En krypteret arkiv åbnes kun med en nøgle, du selv sender ind (Unreal `.pak`, `--key`). En krypteret IoStore-container afvises. Intet søger i en eksekverbar fil efter en nøgle, og intet læser en anden proces' hukommelse. Se [Regler og licenser](rules-and-licences.md).
- **Ingen proprietær kode medleveret.** Oodle indlæses fra et spil eller en motor, der allerede er installeret på maskinen.
- **Afvis hellere end at gætte.** En ukendt version, codec, vertexformat eller teksturformat rejser en specifik fejl, fx `texture format 42 has not been identified; refusing to guess`.
- **Kun læsning.** Ingen læser skriver ind i en spilmappe. Eksporter går derhen, du angiver.

## Hvad "verificeret" betød {#what-verified-meant}

De verifikationstal, der citeres på disse sider, stammer fra modulernes docstrings. De blev målt mod installerede spil, mens hver læser blev skrevet. De syntetiske tests (se [Udvikling](development.md)) fastlåser feltlayouterne. Testene mod installerede spil gentager nogle af tjekkene, når spillet er på maskinen, og springes ellers over. Tal, som ingen test dækker, er ikke tjekket igen siden.
