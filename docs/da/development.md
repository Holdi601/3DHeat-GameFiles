---
title: Udvikling
nav_order: 14
lang: "da"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Udvikling {#development}

## Layout {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modulkort {#module-map}

| Modul | Hvad den gør |
|---|---|
| `__main__.py` | kører opdateringstjekket og derefter `cli.main()` |
| `cli.py` | kommandoerne, `identify`, arkivfordelingen, Forza-course-skriveren |
| `lapinput.py` | hver rundeform til positioner; opslag i FH Companion-biblioteket |
| `corridor.py` | bæltet på hver side af kørslen, som et 4 m raster |
| `surfaces.py` | jordtyperne, deres delnavne og farver |
| `glb.py` | `.glb`-skriveren (dele, normaler, farver, teksturer, kvantisering) |
| `courseexport.py` | Forza: plane flise-UV'er, vej/kant-deling, jordbagning, decal-løft |
| `forzainstall.py` | Steam- og Xbox-biblioteker; den Forza-bane en boks hører til |
| `minizip.py` | ForzaTech `.minizip`-arkiver og deres navnelister |
| `forzatech.py` | `.modelbin`: chunks, buffere, layouts, undermeshes, materialer |
| `forzaterrain.py` | terrænfliser efter sted; overfladeklasser |
| `forzatexture.py` | `.pb`-farveprøver; flisekort; jordbagningen |
| `forzamaterial.py` | `AssetManifest.xml`; hvilke tekstur-farver en model bruger; årstider |
| `forzaplacement.py` | `.pgeo`-placeringer, modelniveauer, teksturer, udklip, stand-ins, budgettet |
| `beamng.py` | BeamNG-installation, monteret filsystem, scene, terræn, materialer |
| `beamngcourse.py` | BeamNG-course-eksporten |
| `beamngshape.py` | `.cdae`-kompilerede former |
| `beamngcollada.py` | `.dae`-reserve |
| `acrally.py` | AC Rally-installation, etaper, komponentplacering, virtuelt teksturvolumen |
| `acrallycourse.py` | AC Rally-course-eksporten: koordinatsystem-tilpasning, jord, placering |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 bagte pakker |
| `unversioned.py` | skemaer og læser for uversionerede egenskaber |
| `unrealmesh.py` | bagte statiske meshes |
| `unrealtexture.py` | teksturer og virtuelle teksturer |
| `oodle.py` | finder og kalder et installeret Oodle-bibliotek |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-containere, bundles, meshes |
| `frostbite.py` | Frostbite `.toc`, sektionstabeller, installationspakker, chunk-placeringer, nyttelast |
| `frostbitebundle.py` | Frostbite inline-bundles, bundle-manifester, et niveaus katalog, niveaulisten |
| `frostbiteebx.py` | Frostbite RIFF EBX-partitioner uden typebibliotek |
| `frostbitemesh.py` | Frostbite MeshSet og dets detaljeniveau-chunks |
| `frostbiteterrain.py` | Frostbite terræn-streamingtræ, højdesider, jordmeshen |
| `frostbitematerial.py` | Frostbite-teksturer (BC1/BC3/BC7-mips), shaderblokdepoter, valg af farvekort |
| `frostbitedecals.py` | Frostbite terræn-decals og jordbagningen |
| `frostbitenav.py` | Frostbite navigationsmesh-fliser: soldaternes gangbare flader |
| `frostbitelevel.py` | Frostbite statiske modelgrupper, placering, `level`-eksporten |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 landskabskomponenter: højdekort ind i jordmeshen (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition-kort: oversigt, HLOD-strukturer, vand, `ue-map`-eksporten |
| `enfusion.py` | Enfusion `.pak`, `.edds`, terrænfliser, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger-verdener: `.ent`-filer, bokse, `enfusion-world`-eksporten |
| `forzacars.py` | alle Forza-biler i lav detalje til `.h3dcars` (`cars`) |

Alle moduler findes på GitHub under [`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Kør testene {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` sætter `testpaths = tests` og `-q`. To slags tests har betydning, af forskellige grunde:

- **Syntetiske tests** bygger arkiver byte for byte og kan køre overalt. De fastlåser feltlayouts, der engang var forkerte: den 64-bit `.minizip`-segmentbase og dens alignment-padding, pak-blokstørrelses-escape, Unity-headerens u32 mellem to int64, VPK'ens `0x7FFF`-indeks, Forza-normalens delte x.
- **Tests mod installerede spil** kører mod de rigtige filer, når spillet er på maskinen, og **springes over** (de fejler ikke), når det ikke er. De er det eneste, der fanger et layout, der er rigtigt for en lille fil og forkert for en stor.

### Fixtures {#fixtures}

| Fixture | Bygger |
|---|---|
| `tests/forza_fixtures.py` | `.minizip`-arkiver (med 64-bit-basen, padding, blandede codecs), manifester, `.modelbin`-modeller og terræn, `.pb`-farveprøver |
| `tests/beamng_fixtures.py` | en lille BeamNG-installation: `gameengine.zip`, `content`, én niveau-zip med et 64 m terræn, en asfaltstrimmel, en vejdecal, en skinne, en prefab, en skovgenstand, havet, materialer og `.cdae`-former i det dokumenterede layout |
| `tests/unreal_fixtures.py` | en IoStore-container med en mappe, en zen-pakke og en uversioneret egenskabsblok |
| `tests/frostbite_fixtures.py` | Frostbite-tabeller, bundles, EBX-partitioner, meshes og terrænsider, byte for byte |

### Testfiler {#test-files}

| Fil | Dækker |
|---|---|
| `test_minizip.py` | læsning tilbage, 64-bit-basen, ulige og lige bundle-tabeller, afvisninger, navnefilen |
| `test_forzatech.py` | chunk-tabellen og kæden, afvisninger; installeret: rigtige modellers kæder og tags |
| `test_forza_geometry.py` | placering i verden, vertexlayout, afviste formater, undermeshes, normaler og UV'er |
| `test_forzaterrain.py` | flisegitteret (1023 mod 512 m), klipning, udtræk |
| `test_forzatexture.py` | farveprøvens header, afkodning, teksturhylden, jordbagningen |
| `test_forzamaterial.py` | manifestet, navne, materialehashes, farvevalget, årstider |
| `test_forzaplacement.py` | `.pgeo`-posten, placering af kopier, niveauer, varianter, gennemsigtige flader, en hel boks, budgettet, pladsholderfarven, det automatiske budget; installeret: kantsten på jorden |
| `test_forzainstall.py` | at finde spillet, vælge banen |
| `test_courseexport.py` | flise-UV'er, delplanen, decal-løft |
| `test_course_cli.py` | hele kommandoerne `course` og `courses` på en syntetisk bane; `terrain --route` med en byte-order mark og uden `bounds` |
| `test_archive_cli.py` | `identify`, `list` og `extract` på hvert arkiv med en læser (`.pak`, IoStore, `.vpk`, `.minizip` med og uden sine navne, zip, `.cdae`, `.ter`); fejl som én linje og en exit-kode: en krypteret pak, en krypteret container, en fil der ikke er et arkiv, en forkert `--key` |
| `test_corridor.py` | bæltet, udskæring af terræn med det |
| `test_lapinput.py` | hver rundeform, boksen, fejl, opslag af banenavn, hvilket spil en mappe er |
| `test_surfaces.py` | hvilke navne der afgør en flade, og hvilke der ikke gør, delnavne |
| `test_glb.py` | filen er gyldig, noder bærer klassen, afvisninger, kvantisering |
| `test_beamng.py` | former, niveauet, kategorier, at finde niveauet ud fra en runde, banen, Collada-reserven; installeret: `.cdae` mod `.dae`, hvert niveau åbnes |
| `test_acrally.py` | containere, pakker, egenskaber, transformationer, koordinatsystem-tilpasningen, placerede modellers dele og budgettet, virtuelle teksturer; installeret: etaper og den indbagte jordfarve |
| `test_pak.py` | footer, poster, blokstørrelses-escape, afvisninger; installeret: offsets og SHA-1 |
| `test_unity.py` | afvisninger; installeret: objekttabellen dækker filen, versionsstrenge, mesh-grænser |
| `test_frostbite.py` | signerede mod slørede headers, afvisninger, installationspakker (to pakker med samme blob-nummer); installeret: hver tabel, superbundles, sektionskæder, særskilte id'er, stikprøvede nyttelaster fra den rigtige pakke |
| `test_frostbitelevel.py` | chunk-id'er parret med deres egne placeringer, inline-bundles, manifester, en MeshSet med en skyggesektion og UV'er, et gruppemedlem, transformationskonventionen, et terræn med to niveauer, valg af farvekort, en teksturchunk der mangler sine største mips, den gentagne sampler, decal-poster, en decal sammensat via sin alfa, et decal-ark der taber til en flades eget kort, niveauets tabel valgt på tværs af grundspillet og dets opdateringer, navigationsfliser (flader beholdt, led udeladt, afvisninger, detaljemeshes), gentagne teksturer skrevet med deres egne koordinater, trekanter skåret der hvor deres tekstur gentages for klemt output, jordens farve fra dens fladematerialer, maskesider (BC4 og ukomprimeret) placeret på deres kvadranter og afvist, når deres kanter ikke passer sammen, farvekortsider placeret på deres kvadranter og fundet efter de maskesider, maske-træet tæller, afstandsfelter, paletter og kanalmasker aldrig taget som farve, en blok's tint og et gråt kort malet med den, en palet-vertex i prøvens midte, hældningsgitteret spredt tilbage bilinært, et objekts overlay tegnet gennem dets udfoldning, en variations blok nøglet af dens hash og nået via en tvillingblok, et bogstavark lagt på via dets fjerde teksturkoordinater over fladen, det males på, en decals maling læst fra dets materiale og landingsbane-linjer og dækspor tegnet, enkeltkanalskort afkodet, ødelæggelige meshes markeret i deres dele og extras, blockout-, filmiske og lysmeshes udeladt og en farvekort-layout der ikke læses, udklipskort og deres maskerede, tosidede PNG-materialer, baggrundsfliser navngivet efter deres mesh; installeret: niveauets terræn-decals, det største niveaus katalog, meshes inden for deres grænser, gruppemedlemmer, vegetation stående på det afkodede terræn |
| `test_vpk.py` | mappen, afvisninger, delte arkiver; installeret: kort åbnes, CRC'er passer, navmeshen |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, terrænfliser og verdensfiler; `enfusion-world`-eksporten |
| `test_forzacars.py` | `.h3dcars`-filen, som kommandoen `cars` skriver |
| `test_unreallevel.py` | Unreal 5-landskaber, HLOD-strukturer, vand; `ue-map`-eksporten |

## Tests mod installerede spil {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
finder spil til testene. `steam_common()` lister hvert Steam-biblioteks `steamapps\common` (Steams egne mapper inklusive), og `installed(*globs)`
returnerer stierne, der matcher et glob under dem, rekursivt hvor et glob har `**`. Hver test afgør selv, hvad den har brug for:

| Test | Leder efter | Springer over med |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` med et **ukrypteret** indeks, op til 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` i `*/*_Data` eller `*/*/*_Data`, som læseren accepterer, op til 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, op til 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | FH Companion-bibliotekets baner (start og mål inden for 50 m) med flest runder, som `find_track` placerer; eller `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Kør kun ét spils tests, eller peg Forza-kantstens-testen på en bane:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Tests mod installerede spil læser kun fra spillene. De skriver intet ind i spilmapper. Testresultater går til pytests midlertidige mapper.

## Konventioner {#conventions}

- **Afvis hellere end at gætte.** Hver læser rejser sin egen undtagelse (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError` ...) med en besked, der siger, hvad der blev fundet, og hvorfor det ikke blev læst.
- **Tjek mod selve formatet.** En hash, en CRC, en kæde af offsets, en gemt bounding box, at kørslen ligger på jorden. Ikke "den gik ikke ned".
- **Ingen nøgler, ingen medleveret proprietær kode.** Se [Regler og licenser](rules-and-licences.md).
- **Fortrolige data holdes ude.** Spilfiler, eksporter, runder, optagelser og skærmbilleder kommer aldrig i repositoriet. `.gitignore` udelukker dem efter mappe og type. Tests bruger syntetiske data og installerede spil, aldrig indhold fra spil, der er checket ind.
