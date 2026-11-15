---
title: Utvikling
nav_order: 14
lang: "no"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Utvikling {#development}

## Oppsett {#layout}

```
heat3d_gamefiles/     pakken: lesere, løypeeksporter, kommandolinjen
heat3d_update/        sjekken for nye utgivelser og oppdateringen (se Oppdateringer)
tests/                syntetiske tester, testfiler, og tester mot installerte spill
docs/                 denne dokumentasjonen (docs/wiki genereres fra den)
VERSION               den installerte versjonen, sammenlignet med GitHub-utgivelsene
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modulkart {#module-map}

| Modul | Hva den gjør |
|---|---|
| `__main__.py` | kjører oppdateringssjekken, deretter `cli.main()` |
| `cli.py` | kommandoene, `identify`, arkivfordeling, Forza-løypeskriveren |
| `lapinput.py` | alle rundeformer til posisjoner; FH Companion-biblioteksoppslag |
| `corridor.py` | båndet på hver side av kjøringen, som et 4 m-raster |
| `surfaces.py` | bakkeslagene, deres delnavn og farger |
| `glb.py` | `.glb`-skriveren (deler, normaler, farger, teksturer, kvantisering) |
| `courseexport.py` | Forza: planare flis-UV-er, vei-/skulderdeling, bakkebaking, dekalløfting |
| `forzainstall.py` | Steam- og Xbox-biblioteker; hvilken Forza-bane en boks tilhører |
| `minizip.py` | ForzaTech `.minizip`-arkiver og deres navnelister |
| `forzatech.py` | `.modelbin`: chunks, buffere, oppsett, undermasker, materialer |
| `forzaterrain.py` | terrengfliser etter sted; overflateklasser |
| `forzatexture.py` | `.pb`-fargeprøver; flisekart; bakkebaking |
| `forzamaterial.py` | `AssetManifest.xml`; hvilke teksturfarger en modell har; årstider |
| `forzaplacement.py` | `.pgeo`-plasseringer, modellnivåer, teksturer, utklipp, stand-ins, budsjettet |
| `beamng.py` | BeamNG-installasjon, monterte filsystem, scene, terreng, materialer |
| `beamngcourse.py` | BeamNG-løypeeksporten |
| `beamngshape.py` | `.cdae`-kompilerte former |
| `beamngcollada.py` | `.dae`-reserveløsning |
| `acrally.py` | AC Rally-installasjon, etapper, komponentplassering, virtuell teksturvolum |
| `acrallycourse.py` | AC Rally-løypeeksporten: rammetilpasning, bakke, plassering |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 innbakte pakker |
| `unversioned.py` | skjemaer og leser for uversjonerte egenskaper |
| `unrealmesh.py` | innbakte statiske modeller |
| `unrealtexture.py` | teksturer og strømmede virtuelle teksturer |
| `oodle.py` | finne og kalle et installert Oodle-bibliotek |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-beholdere, pakker, modeller |
| `frostbite.py` | Frostbite `.toc`, seksjonstabeller, installasjonspakker, plasseringer av biter, nyttelaster |
| `frostbitebundle.py` | Frostbite innebygde pakker, pakkemanifester, et nivås katalog, nivålisten |
| `frostbiteebx.py` | Frostbite RIFF EBX-partisjoner uten typebibliotek |
| `frostbitemesh.py` | Frostbite MeshSet og dets detaljnivå-deler |
| `frostbiteterrain.py` | Frostbite terrengstrømmingstre, høydesider, bakkemodellen |
| `frostbitematerial.py` | Frostbite-teksturer (BC1/BC3/BC7-mips), shaderblokk-depoter, valg av fargekart |
| `frostbitedecals.py` | Frostbite-terrengdekaler og bakkebaking |
| `frostbitenav.py` | Frostbite navigasjonsmesh-fliser: soldatenes gangbare flater |
| `frostbitelevel.py` | Frostbite statiske modellgrupper, plassering, `level`-eksporten |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 landskapskomponenter: høydekart inn i bakkemodellen (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition-kart: opplisting, HLOD-strukturer, vann, `ue-map`-eksporten |
| `enfusion.py` | Enfusion `.pak`, `.edds`, terrengfliser, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger-verdener: `.ent`-filer, bokser, `enfusion-world`-eksporten |
| `forzacars.py` | hver Forza-bil på lav detalj til `.h3dcars` (`cars`) |

Alle modulene ligger på GitHub under
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Kjøre testene {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` setter `testpaths = tests` og `-q`. To slags tester betyr noe, av ulike grunner:

- **Syntetiske tester** bygger arkiver byte for byte og kjører hvor som helst. De låser
  feltoppsettene som var feil på et tidspunkt: `.minizip`s 64-bits segmentbase og dens
  justeringsfylling, blokkstørrelse-escape i pak, Unity-hodets u32 mellom to int64, VPK-indeksen
  `0x7FFF`, Forza-normalens delte x.
- **Tester mot installerte spill** kjører mot de ekte filene når spillet finnes på maskinen, og
  **hopper over** (de feiler ikke) når det ikke gjør det. De er det eneste som fanger et oppsett
  som er riktig for en liten fil og feil for en stor.

### Testfiler {#fixtures}

| Testfiler | Bygger |
|---|---|
| `tests/forza_fixtures.py` | `.minizip`-arkiver (med 64-bits base, fylling, blandede kodeker), manifester, `.modelbin`-modeller og terreng, `.pb`-fargeprøver |
| `tests/beamng_fixtures.py` | en liten BeamNG-installasjon: `gameengine.zip`, `content`, ett nivå-zip med et 64 m terreng, en asfaltstripe, en veidekal, et rekkverk, et prefab, et skogelement, havet, materialer og `.cdae`-former i den dokumenterte layouten |
| `tests/unreal_fixtures.py` | en IoStore-beholder med en mappe, en zen-pakke, en uversjonert egenskapsblokk |
| `tests/frostbite_fixtures.py` | Frostbite-tabeller, pakker, EBX-partisjoner, modeller og terrengsider, byte for byte |

### Testfiler {#test-files}

| Fil | Dekker |
|---|---|
| `test_minizip.py` | lesing tilbake, 64-bits base, odde og like pakketabeller, avvisninger, navnefilen |
| `test_forzatech.py` | chunk-tabellen og kjeden, avvisninger; installert: ekte modellers kjeder og merker |
| `test_forza_geometry.py` | verdensplassering, hjørnepunktoppsett, avviste formater, undermasker, normaler og UV-er |
| `test_forzaterrain.py` | rutenettet for fliser (1023 mot 512 m), klipping, uttrekk |
| `test_forzatexture.py` | fargeprøvens hode, dekoding, teksturhyllen, bakkebakingen |
| `test_forzamaterial.py` | manifestet, navn, materialhash-er, fargevalget, årstider |
| `test_forzaplacement.py` | `.pgeo`-posten, plassering av kopier, nivåer, varianter, gjennomsiktige flater, en hel boks, budsjettet, plassholderfargen, det automatiske budsjettet; installert: kantstein på bakken |
| `test_forzainstall.py` | finne spillet, velge banen |
| `test_courseexport.py` | flis-UV-er, delplanen, dekalløfting |
| `test_course_cli.py` | hele `course`- og `courses`-kommandoen på en syntetisk bane; `terrain --route` med en byte-order mark, og uten `bounds` |
| `test_archive_cli.py` | `identify`, `list` og `extract` på hvert arkiv med en leser (`.pak`, IoStore, `.vpk`, `.minizip` med og uten navn, zip, `.cdae`, `.ter`); feil som én linje og en avslutningskode: en kryptert pak, en kryptert beholder, en fil som ikke er et arkiv, en feil `--key` |
| `test_corridor.py` | båndet, utskjæring av terreng med det |
| `test_lapinput.py` | alle rundeformer, boksen, feil, løypenavnsoppslag, hvilket spill en mappe er |
| `test_surfaces.py` | hvilke navn som avgjør en flate, og hvilke som ikke gjør det; delnavn |
| `test_glb.py` | filen er gyldig, noder bærer klassen, avvisninger, kvantisering |
| `test_beamng.py` | former, nivået, kategorier, finne nivået fra en runde, løypen, Collada-reserveløsningen; installert: `.cdae` mot `.dae`, hvert nivå åpnes |
| `test_acrally.py` | beholdere, pakker, egenskaper, transformasjoner, rammetilpasningen, plasserte modellers deler og budsjettet, virtuelle teksturer; installert: etapper og den innbakte bakkefargen |
| `test_pak.py` | fot, oppføringer, blokkstørrelse-escape, avvisninger; installert: forskyvinger og SHA-1 |
| `test_unity.py` | avvisninger; installert: objekttabellen dekker filen, versjonsstrenger, modellgrenser |
| `test_frostbite.py` | signerte mot forvirrede hoder, avvisninger, installasjonspakker (to pakker med samme blobnummer); installert: hver tabell, superpakker, seksjonskjeder, distinkte id-er, utvalgte nyttelaster fra riktig pakke |
| `test_frostbitelevel.py` | chunk-id-er paret med sine egne plasseringer, innebygde pakker, manifester, en MeshSet med en skyggeseksjon og UV-er, et gruppemedlem, transformasjonskonvensjonen, et tonenivå-terreng, valg av fargekart, en teksturchunk som mangler sine største mips, den gjentatte samplingen, dekalposter, en dekal komponert etter alfaen, et dekalark som taper mot en flates eget kart, nivåtabellen valgt mellom grunnspillet og dets oppdateringer, navigasjonsfliser (flater beholdt, koblinger utelatt, avvisninger, detaljmesh), gjentatte teksturer skrevet med sine egne koordinater, trekanter klippet der teksturen gjentas for klemt utdata, bakkens farge fra overflatenes materialer, maskesider (BC4 og ukomprimert) plassert på sine kvadranter og avvist når kantene ikke passer, fargekartsider plassert på kvadranter og funnet etter maskesidene masketreet teller, avstandsfelt, paletter og kanalmasker aldri tatt som farge, en blokks farge og et grått kart malt med den, et palettehjørne i sentrum av sin fargeprøve, skråningsrutenettet spredt tilbake bilineært, et objekts overlegg tegnet gjennom sin utfolding, en variasjons blokk nøklet av sin hash og nådd gjennom en tvillingblokk, et bokstavark lagt på av sine fjerde teksturkoordinater over flaten det males på, en dekals maling lest fra sitt materiale og kjørebaneslinjer og dekkspor tegnet, enkeltkanalkart dekodet, ødeleggbare modeller merket i sine deler og ekstradata, blockout-, kinematiske og lysmodeller utelatt og et fargekartoppsett som ikke leses, utklippskart og deres maskerte, toseidede PNG-materialer, kulissefliser navngitt etter sin mesh; installert: nivåets terrengdekaler, største nivås katalog, meshes innenfor sine grenser, gruppemedlemmer, vegetasjon som står på det dekodede terrenget |
| `test_vpk.py` | katalogen, avvisninger, delte arkiver; installert: kart åpnes, CRC-er stemmer, navmeshen |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, terrengfliser og verdensfiler; `enfusion-world`-eksporten |
| `test_forzacars.py` | `.h3dcars`-filen `cars`-kommandoen skriver |
| `test_unreallevel.py` | Unreal 5-landskap, HLOD-strukturer, vann; `ue-map`-eksporten |

## Tester mot installerte spill {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
finner spill for testene. `steam_common()` lister hvert Steam-biblioteks `steamapps\common`
(Steams egne mapper medregnet), og `installed(*globs)` returnerer stiene som matcher et av
mønstrene under dem, rekursivt der et mønster har `**`. Hver test avgjør selv hva den trenger:

| Test | Leter etter | Hopper over med |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` med en **ukryptert** indeks, opptil 4 | «no shipped pak on this machine» |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` i `*/*_Data` eller `*/*/*_Data` som leseren godtar, opptil 6 | «no Unity game on this machine» |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | «no Frostbite game on this machine» |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | «no Frostbite level on this machine» |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, opptil 6 | «Counter-Strike 2 is not installed» |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | «no Forza install on this machine» |
| `test_forzaplacement.py` | FH Companion-bibliotekets baner (start og mål innen 50 m), med flest runder, som `find_track` plasserer; eller `HEAT3D_COURSE` | «no Forza install with a recorded lap library here» |
| `test_beamng.py` | `find_install()` | «BeamNG.drive is not installed» |
| `test_acrally.py` | `find_paks()` | «Assetto Corsa Rally is not installed» |

Kjør bare ett spills tester, eller pek Forza-kantsteinstesten mot en løype:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Tester mot installerte spill leser bare fra spillene. De skriver ingenting inn i spillmapper.
Testresultatene går til pytests midlertidige mapper.

## Konvensjoner {#conventions}

- **Avvis heller enn å gjette.** Hver leser kaster sitt eget unntak (`UnsupportedPak`,
  `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`,
  `BeamNGError`, `PropertyError` ...) med en melding som sier hva som ble funnet og hvorfor det ikke
  ble lest.
- **Kontroller mot formatet selv.** En hash, en CRC, en kjede av forskyvinger, en lagret
  avgrensningsboks, at kjøringen ligger på bakken. Ikke «den krasjet ikke».
- **Ingen nøkler, ingen medfølgende proprietær kode.** Se [Regler og lisenser](rules-and-licences.md).
- **Konfidensielle data holdes utenfor.** Spillfiler, eksporter, runder, opptak og skjermbilder havner
  aldri i depotet. `.gitignore` utelukker dem etter mappe og type. Testene bruker syntetiske data og
  installerte spill, aldri innsjekket spillinnhold.
