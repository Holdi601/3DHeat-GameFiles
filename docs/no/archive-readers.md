---
title: Arkivlesere
nav_order: 9
lang: "no"
source: archive-readers.md
source_hash: "0f1064f05cfd"
nav_exclude: true
search_exclude: true
---
# Arkivlesere {#archive-readers}

Et **arkiv** (eller container) er én stor fil som et spill pakker mange filer
inn i. En **CRC** eller hash er et kort fingeravtrykk av noen bytes: hvis det
stemmer, er bytes lest riktig. En **omsluttende boks** er den minste boksen
rundt en modell.

Under kommandoene ligger lesere for de arkivene spill leverer. Formatene deres
er udokumenterte, bortsett fra Valves VPK og BeamNGs `.cdae`. Derfor må
«støttet» bety **verifisert mot ekte filer**, ikke «krasjet ikke». Hver leser
sjekker seg selv mot noe formatet garanterer: en hash, en CRC, en kjede av
forskyvninger som må gå opp, eller en lagret omsluttende boks. Når en sjekk
feiler, nekter leseren med en melding i stedet for å gjette. En feil modell ser
ut som en riktig en, helt til noen setter den ved siden av banen.

| Leser | Modul | Leser | Leser ikke | Brukes av |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versjon 8-12: indeks, oppføringer, Zlib/Gzip/Oodle-blokker, AES med en nøkkel du oppgir | versjoner før 8, indekser med bare stihash, overløpsoppføringer, innholdet i ressursfiler | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, sjekket på v8), zen-pakker, uversjonerte egenskaper for noen få komponentklasser, innbakte statiske modeller, teksturer, strømmede virtuelle teksturer | krypterte beholdere, versjonerte pakker, modeller som bare finnes som Nanite, egenskaper for andre klasser | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle-blokker gjennom et bibliotek som allerede finnes på maskinen | alt uten slikt bibliotek; det leveres aldri med | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22+ (Unity 2020 til 6000), `UnityFS`-pakker, ukomprimerte modeller inkl. `.resS` | formater før 2020, innebygde typetrær, komprimerte modeller, andre klasser enn `Mesh` | `identify`, `meshes` |
| [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc`-DbObject-trær og binære seksjonstabeller, installasjonspakker, plasseringer av biter, innebygde pakker og deres manifester, RIFF EBX-partisjoner, MeshSet-modeller, terrengets høydefelt, BC1/BC3/BC7-teksturer og deres shaderblokker, plassering av statiske modellgrupper | XOR-forhårdede tabeller, terrengets fargenær bakke og hull, normalkart, alfa annet enn utskjæringer | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versjon 1 og 2, delte arkiver, forhåndslastede data, CRC-sjekk | kompilerte ressurser (`.vmdl_c`, `.vtex_c`), formatet for CS2-navigasjonsnettet | `identify`, `list`, `extract` |
| [ForzaTech](https://holdi601.github.io/3DHeat-Ext-Forza/reader-forzatech.html) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, lagret), `.modelbin`-geometri, `.pb`-fargeprøver (BC1, BC7, RGBA), `.pgeo`-plasseringer, teksturhasher for materialer | andre vertex- og indeksformater, andre teksturformater, terrengets shaderlag | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` og `extract` (`.minizip`) |
| [BeamNG-filer](https://holdi601.github.io/3DHeat-Ext-BeamNG/reader-beamng.html) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | det monterte zip-filsystemet, scene-JSON og TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materialer | skinnede modeller og dekalmodeller, animerte sekvenser, prosedyremessig bakkedekke | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` og `extract` (zip) |

## Regler alle lesere følger {#rules-every-reader-follows}

- **Ingen nøkler leveres, og ingen hentes ut.** Et kryptert arkiv åpnes bare
  med en nøkkel du selv oppgir (Unreal `.pak`, `--key`). En kryptert IoStore-
  beholder blir avvist. Ingenting søker i en kjørbar fil etter en nøkkel, og
  ingenting leser en annen prosess sitt minne. Se
  [Regler og lisenser](rules-and-licences.md).
- **Ingen proprietær kode følger med.** Oodle lastes fra et spill eller en
  motor som allerede er installert på maskinen.
- **Nekt heller enn gjett.** En ukjent versjon, kodek, vertexformat eller
  teksturformat gir en spesifikk feil, for eksempel
  `texture format 42 has not been identified; refusing to guess`.
- **Bare lesing.** Ingen leser skriver inn i en spillmappe. Eksporter går dit du
  sier.

## Hva «verifisert» betyr {#what-verified-meant}

Verifiseringstallene på disse sidene kommer fra modul-docstringene. De ble målt
mot installerte spill mens hver leser ble skrevet. De syntetiske testene (se
[Utvikling](development.md)) låser feltoppsettene. Testene mot installerte spill
gjentar noen av sjekkene når spillet er på maskinen, og hopper over dem ellers.
Tall som ingen test dekker, er ikke kontrollert på nytt siden.
