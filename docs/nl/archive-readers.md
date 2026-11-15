---
title: Archieflezers
nav_order: 9
lang: "nl"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Archieflezers {#archive-readers}

Een **container** (of archief) is een groot bestand waarin een spel veel andere bestanden samenpakt. Een **CRC** of hash is een korte vingerafdruk van een aantal bytes: als die klopt, zijn de bytes goed gelezen. Een **begrenzingsdoos** (bounding box) is de kleinst mogelijke doos rond een model.

Onder de commando's liggen lezers voor de containers die spellen meeleveren. Hun formaten zijn niet gedocumenteerd, op Valve's VPK en BeamNG's `.cdae` na. "Ondersteund" betekent dus **gecontroleerd met echte bestanden**, niet "is niet gecrasht". Elke lezer controleert zichzelf aan iets wat het formaat garandeert: een hash, een CRC, een keten van offsets die moet kloppen, of een opgeslagen begrenzingsdoos. Als zo'n controle faalt, weigert de lezer met een melding in plaats van te gokken. Een verkeerd mesh lijkt op een goed mesh, totdat iemand het naast het parcours zet.

| Lezer | Module | Leest | Leest niet | Wordt aangeroepen vanuit |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versies 8-12: index, items, Zlib/Gzip/Oodle-blokken, AES met een sleutel die je zelf opgeeft | versies vóór 8, indexen met alleen path-hashes, overloopitems, inhoud van assets | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, gecontroleerd op v8), zen-pakketten, unversioned eigenschappen voor enkele componentklassen, gebakken statische meshes, texturen, streaming virtual textures | versleutelde containers, versioned pakketten, meshes die alleen Nanite zijn, eigenschappen van andere klassen | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle-blokken via een bibliotheek die al op de pc staat | alles zonder zo'n bibliotheek; die wordt nooit meegeleverd | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` formaat 22+ (Unity 2020 tot 6000), `UnityFS`-bundels, niet-gecomprimeerde meshes incl. `.resS` | formaten van vóór 2020, ingebedde typebomen, gecomprimeerde meshes, elke klasse behalve `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` DbObject-bomen en binaire sectietabellen, installatiepakketten, chunklocaties, inline bundels en hun manifesten, RIFF EBX-partities, MeshSet-meshes, het terrein-hoogteveld, BC1/BC3/BC7-texturen en hun shaderblokken, plaatsing van statische modelgroepen | XOR-verhulde tabellen, de nabije grondkleur en gaten in het terrein, normal maps, alfa behalve uitsnijdingen | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versies 1 en 2, gesplitste archieven, vooraf geladen data, CRC-controle | gecompileerde assets (`.vmdl_c`, `.vtex_c`), het CS2 nav mesh-formaat | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, ongecomprimeerd), `.modelbin`-geometrie, `.pb`-swatches (BC1, BC7, RGBA), `.pgeo`-plaatsingen, hashes van materiaaltexturen | andere vertex- en indexformaten, andere texturformaten, lagen van de terreinshader | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` en `extract` (`.minizip`) |
| [BeamNG-bestanden](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | het gekoppelde zip-bestandssysteem, scène-JSON en TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materialen | vervormbare en decal-meshes, animaties, procedurele grondbedekking | `course` (BeamNG), `identify` (zips, `.cdae`, `.ter`), `list` en `extract` (zips) |

## Regels die elke lezer volgt {#rules-every-reader-follows}

- **Geen sleutels meegeleverd, en er worden er geen gevonden.** Een versleuteld Unreal `.pak` opent alleen met `--key <hex>` (in Python `PakArchive(path, aes_key=...)`). Een versleutelde IoStore-container wordt helemaal geweigerd. Niets zoekt in een programma naar een sleutel, en niets leest het geheugen van een ander proces. Zie [Regels en licenties](rules-and-licences.md).
- **Geen code van derden meegeleverd.** Oodle wordt geladen uit een spel of engine die al op de pc is geïnstalleerd.
- **Weigeren in plaats van raden.** Een onbekende versie, codec, vertexformaat of texturformaat geeft een eigen foutmelding, zoals `texture format 42 has not been identified; refusing to guess`.
- **Alleen lezen.** Geen enkele lezer schrijft in een spelmap. Exports gaan naar de plek die je opgeeft.

## Wat "gecontroleerd" betekende {#what-verified-meant}

De controlegetallen op deze pagina's komen uit de modulebeschrijvingen in de code. Ze zijn gemeten op geïnstalleerde spellen, terwijl elke lezer werd geschreven. De synthetische tests (zie [Ontwikkeling](development.md)) leggen de veldindelingen vast. De tests op geïnstalleerde spellen herhalen sommige controles wanneer het spel op de pc staat, en slaan ze over wanneer dat niet zo is. Cijfers die door geen test gedekt worden, zijn sindsdien niet opnieuw gecontroleerd.
