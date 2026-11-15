---
title: "Arkivläsare"
nav_order: 9
lang: "sv"
source: archive-readers.md
source_hash: "0f1064f05cfd"
nav_exclude: true
search_exclude: true
---
# Arkivläsare {#archive-readers}

En **behållare** (eller arkiv) är en stor fil som ett spel packar många filer i.
En **CRC** eller hash är ett kort fingeravtryck av några bytes: stämmer det, så
lästes bytesen rätt. En **omslutningsruta** (bounding box) är den minsta lådan
runt en modell.

Under kommandona finns läsare för de behållare som spel levereras i. Deras format
är odokumenterade, förutom Valves VPK och BeamNGs `.cdae`. Därför måste "stöds"
betyda **verifierat mot riktiga filer**, inte "kraschade inte". Varje läsare
kontrollerar sig mot något som formatet garanterar: en hash, en CRC, en kedja av
offset som måste gå ihop, en lagrad omslutningsruta. Om en kontroll misslyckas
vägrar läsaren med ett meddelande i stället för att gissa. En felaktig modell ser ut
som en rätt tills någon ställer den bredvid banan.

| Läsare | Modul | Läser | Läser inte | Nås från |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | version 8-12: index, poster, Zlib/Gzip/Oodle-block, AES med en nyckel du anger | version före 8, index med bara sökvägshashar, överflödesposter, innehållet i assets | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, kontrollerad på v8), zen-paket, oversionerade egenskaper för några komponentklasser, kompilerade statiska meshar, texturer, strömmade virtuella texturer | krypterade behållare, versionerade paket, meshar som bara finns i Nanite, andra klassers egenskaper | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle-block via ett bibliotek som redan finns på datorn | allt utan ett sådant bibliotek; det levereras aldrig med | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22 och senare (Unity 2020 till 6000), `UnityFS`-paket, okomprimerade meshar inklusive `.resS` | format före 2020, inbäddade typträd, komprimerade meshar, alla klasser utom `Mesh` | `identify`, `meshes` |
| [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc`-DbObject-träd och binära sektionstabeller, installationspaket, chunkplatser, inline-paket och deras manifest, RIFF EBX-partitioner, MeshSet-meshar, terrängens höjdfält, BC1/BC3/BC7-texturer och deras shaderblock, placering av statiska modellgrupper | XOR-maskerade tabeller, terrängens närmarksfärg och hål, normalkartor, alfa utom utskärningar | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | version 1 och 2, delade arkiv, förladdad data, CRC-kontroll | kompilerade assets (`.vmdl_c`, `.vtex_c`), CS2:s navmeshformat | `identify`, `list`, `extract` |
| [ForzaTech](https://holdi601.github.io/3DHeat-Ext-Forza/reader-forzatech.html) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, lagrat), `.modelbin`-geometri, `.pb`-färgprov (BC1, BC7, RGBA), `.pgeo`-placeringar, materialens texturhashar | andra vertex- och indexformat, andra texturformat, terrängshaderns materiallager | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` och `extract` (`.minizip`) |
| [BeamNG-filer](https://holdi601.github.io/3DHeat-Ext-BeamNG/reader-beamng.html) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | det monterade zip-filsystemet, scenens JSON och TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, material | skinnade meshar och dekalmeshar, animerade sekvenser, procedurell markvegetation | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` och `extract` (zip) |

## Regler som varje läsare följer {#rules-every-reader-follows}

- **Inga nycklar levereras, inga återskapas.** En krypterad arkivfil öppnas bara
  med en nyckel som du själv anger (Unreal `.pak`, `--key`). En krypterad
  IoStore-behållare vägras. Ingenting söker efter en nyckel i en körbar fil, och
  ingenting läser en annan processes minne. Se [Regler och licenser](rules-and-licences.md).
- **Ingen proprietär kod levereras.** Oodle laddas från ett spel eller en motor
  som redan är installerad på datorn.
- **Vägra hellre än gissa.** En okänd version, kodek, vertexformat eller
  texturformat ger ett särskilt felmeddelande, till exempel
  `texture format 42 has not been identified; refusing to guess`.
- **Skrivskyddat.** Ingen läsare skriver i en spelmapp. Exporter går dit du säger.

## Vad "verifierat" betyder {#what-verified-meant}

Verifieringssiffrorna på de här sidorna kommer från modulernas docstrings. De
mättes mot installerade spel medan varje läsare skrevs. De syntetiska testerna
(se [Utveckling](development.md)) låser fältlayouterna. Testerna mot installerade
spel upprepar några av kontrollerna när spelet finns på datorn, och hoppar över
dem annars. Siffror som inte täcks av något test har inte kontrollerats om sedan dess.
