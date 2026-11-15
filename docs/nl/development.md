---
title: Ontwikkeling
nav_order: 14
lang: "nl"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Ontwikkeling {#development}

## Indeling {#layout}

```
heat3d_gamefiles/     het pakket: lezers, baan-exports, de opdrachtregel
heat3d_update/        de controle op nieuwe versies en de updater (zie Updates)
tests/                synthetische tests, fixtures, en tests tegen geïnstalleerde spellen
docs/                 deze documentatie (docs/wiki wordt hieruit gegenereerd)
VERSION               de geïnstalleerde versie, vergeleken met de GitHub-releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modulenoverzicht {#module-map}

| Module | Wat het doet |
|---|---|
| `__main__.py` | draait de controle op updates, daarna `cli.main()` |
| `cli.py` | de commando's, `identify`, archiefdoorverwijzing, de Forza-baanschrijver |
| `lapinput.py` | elke vorm van ronde naar posities; opzoeken in de FH Companion-bibliotheek |
| `corridor.py` | de strook aan beide kanten van de rijlijn, als raster van 4 m |
| `surfaces.py` | de soorten grond, hun delnamen en kleuren |
| `glb.py` | de `.glb`-schrijver (delen, normalen, kleuren, texturen, kwantisatie) |
| `courseexport.py` | Forza: vlakke tegel-UV's, weg/berm-splitsing, grondbake, decal-optilling |
| `forzainstall.py` | Steam- en Xbox-bibliotheken; de Forza-baan waartoe een doos behoort |
| `minizip.py` | ForzaTech `.minizip`-archieven en hun naamlijsten |
| `forzatech.py` | `.modelbin`: chunks, buffers, indelingen, submeshes, materialen |
| `forzaterrain.py` | terreintegels op plaats; oppervlakteklassen |
| `forzatexture.py` | `.pb`-swatches; tegelkaarten; de grondbake |
| `forzamaterial.py` | `AssetManifest.xml`; welke texturkleuren een model heeft; seizoenen |
| `forzaplacement.py` | `.pgeo`-plaatsingen, modelniveaus, texturen, uitsnijdingen, stand-ins, het budget |
| `beamng.py` | BeamNG-installatie, gekoppeld bestandssysteem, scène, terrein, materialen |
| `beamngcourse.py` | de BeamNG-baan-export |
| `beamngshape.py` | `.cdae`-gecompileerde vormen |
| `beamngcollada.py` | `.dae`-terugvaloptie |
| `acrally.py` | AC Rally-installatie, etappes, componentplaatsing, virtual texture-volume |
| `acrallycourse.py` | de AC Rally-baan-export: fit van het stelsel, grond, plaatsing |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 gecookte pakketten |
| `unversioned.py` | schema's en lezer voor unversioned eigenschappen |
| `unrealmesh.py` | gecookte statische meshes |
| `unrealtexture.py` | texturen en streaming virtual textures |
| `oodle.py` | een geïnstalleerde Oodle-bibliotheek vinden en aanroepen |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-containers, bundels, meshes |
| `frostbite.py` | Frostbite `.toc`, sectietabellen, installatiepakketten, chunklocaties, payloads |
| `frostbitebundle.py` | Frostbite inline bundels, bundelmanifesten, de catalogus van een level, de levellijst |
| `frostbiteebx.py` | Frostbite RIFF EBX-partities zonder typebibliotheek |
| `frostbitemesh.py` | Frostbite MeshSet en zijn detailniveau-chunks |
| `frostbiteterrain.py` | Frostbite terreinstreamingboom, hoogtepagina's, de grondmesh |
| `frostbitematerial.py` | Frostbite-texturen (BC1/BC3/BC7-mips), shaderblokdepots, keuze van de kleurkaart |
| `frostbitedecals.py` | Frostbite-terreindecals en de grondbake |
| `frostbitenav.py` | Frostbite navigatiemesh-tegels: de loopbare oppervlakken van de soldaten |
| `frostbitelevel.py` | Frostbite statische modelgroepen, plaatsing, de `level`-export |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 landschapscomponenten: hoogtekaarten naar de grondmesh (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition-kaarten: lijsten, HLOD-structuren, water, de `ue-map`-export |
| `enfusion.py` | Enfusion `.pak`, `.edds`, terreintegels, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger-werelden: `.ent`-bestanden, dozen, de `enfusion-world`-export |
| `forzacars.py` | elke Forza-auto op laag detail naar `.h3dcars` (`cars`) |

Alle modules staan op GitHub in
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## De tests draaien {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` zet `testpaths = tests` en `-q`. Er zijn twee soorten tests, om verschillende redenen belangrijk:

- **Synthetische tests** bouwen archieven byte voor byte en draaien overal. Ze leggen de veldindelingen vast die ooit fout waren: de 64-bit segmentbasis van `.minizip` en zijn uitlijningsvulling, de blokgrootte-escape van pak, de u32 tussen twee int64's in de Unity-header, de `0x7FFF`-index van VPK, de gesplitste x van de Forza-normaal.
- **Tests op geïnstalleerde spellen** draaien tegen de echte bestanden wanneer het spel op de pc staat, en **slaan over** (ze falen niet) wanneer dat niet zo is. Alleen zij vangen een indeling die klopt voor een klein bestand en fout is voor een groot bestand.

### Fixtures {#fixtures}

| Fixture | Bouwt |
|---|---|
| `tests/forza_fixtures.py` | `.minizip`-archieven (met de 64-bit basis, vulling, gemengde codecs), manifesten, `.modelbin`-modellen en terrein, `.pb`-swatches |
| `tests/beamng_fixtures.py` | een kleine BeamNG-installatie: `gameengine.zip`, `content`, één levelzip met een terrein van 64 m, een asfaltstrook, een wegdecal, een vangrail, een prefab, een bositem, de zee, materialen, en `.cdae`-vormen in de gedocumenteerde indeling |
| `tests/unreal_fixtures.py` | een IoStore-container met een map, een zen-pakket, een unversioned eigenschappenblok |
| `tests/frostbite_fixtures.py` | Frostbite-tabellen, bundels, EBX-partities, meshes en terreinpagina's, byte voor byte |

### Testbestanden {#test-files}

| Bestand | Dekt |
|---|---|
| `test_minizip.py` | teruglezen, de 64-bit basis, even en oneven bundeltabellen, weigeringen, het naambestand |
| `test_forzatech.py` | de chunktabel en -keten, weigeringen; geïnstalleerd: de ketens en tags van echte modellen |
| `test_forza_geometry.py` | wereldplaatsing, vertexindeling, geweigerde formaten, submeshes, normalen en UV's |
| `test_forzaterrain.py` | het tegelraster (1023 vs 512 m), knippen, extractie |
| `test_forzatexture.py` | swatch-header, decoderen, de texturenplank, de grondbake |
| `test_forzamaterial.py` | het manifest, namen, materiaalhashes, de kleurkeuze, seizoenen |
| `test_forzaplacement.py` | het `.pgeo`-record, kopieën plaatsen, niveaus, varianten, doorzichtige oppervlakken, een hele doos, het budget, de plaatsingskleur, het automatische budget; geïnstalleerd: kantstenen op de grond |
| `test_forzainstall.py` | het spel vinden, de baan kiezen |
| `test_courseexport.py` | tegel-UV's, het onderdelenplan, decal-optilling |
| `test_course_cli.py` | de hele `course`- en `courses`-commando's op een nagebootste baan; `terrain --route` met een byte-ordermarkering, en zonder `bounds` |
| `test_archive_cli.py` | `identify`, `list` en `extract` op elk archief met een lezer (`.pak`, IoStore, `.vpk`, `.minizip` met en zonder namen, zip, `.cdae`, `.ter`); fouten als één regel en een exitcode: een versleuteld pak, een versleutelde container, een bestand dat geen archief is, een slechte `--key` |
| `test_corridor.py` | de strook, het knippen van terrein ermee |
| `test_lapinput.py` | elke vorm van ronde, de doos, fouten, het opzoeken van baannamen, welk spel een map is |
| `test_surfaces.py` | welke namen de soort bepalen, welke niet, onderdelennamen |
| `test_glb.py` | het bestand is geldig, knooppunten dragen de klasse, weigeringen, kwantisatie |
| `test_beamng.py` | vormen, het level, categorieën, het level vinden uit een ronde, de baan, de Collada-terugval; geïnstalleerd: `.cdae` vs `.dae`, elk level opent |
| `test_acrally.py` | containers, pakketten, eigenschappen, transformaties, de fit van het stelsel, onderdelen en het budget van geplaatste modellen, virtual textures; geïnstalleerd: etappes en de gebakken grondkleur |
| `test_pak.py` | footer, items, de blokgrootte-escape, weigeringen; geïnstalleerd: offsets en SHA-1 |
| `test_unity.py` | weigeringen; geïnstalleerd: de objecttabel vult het bestand, versiestrings, meshbegrenzingen |
| `test_frostbite.py` | ondertekende vs verhulde headers, weigeringen, installatiepakketten (twee pakketten met hetzelfde bundelnummer); geïnstalleerd: elke tabel, superbundels, sectieketens, duidelijke id's, gesamplede payloads uit het juiste pakket |
| `test_frostbitelevel.py` | chunk-id's gekoppeld aan hun eigen locaties, inline bundels, manifesten, een MeshSet met een schaduwsectie en UV's, een groepslid, de transformatieconventie, een terrein met twee levels, keuze van de kleurkaart, een texturchunk zonder de grootste mips, de herhalende sampler, decalrecords, een decal gecomponeerd via zijn alfa, een decalblad dat verliest van de eigen kaart van een oppervlak, een blokkleurtint en een grijze kaart die ermee geverfd wordt, een paletvertex in het midden van zijn swatch, het hellingsraster terug bilineair uitgespreid, de overlay van een object getekend via zijn ontvouwing, het blok van een variant gesleuteld op zijn hash en bereikt via een tweelingblok, een letterblad dat wordt aangebracht via zijn vierde texturcoördinaten over het oppervlak waarop het geschilderd is, de verf van een decal gelezen uit zijn materiaal en baanlijnen en bandensporen getekend, enkelkanaalskaarten gedecodeerd, vernietigbare meshes gelabeld in hun delen en extra's, blockout-, cinematic- en lichtmeshes weggelaten en een kleurkaartlayout die niet gelezen wordt, uitsnijdkaarten en hun gemaskeerde, tweezijdige PNG-materialen, achtergrondtegels genoemd naar hun mesh; geïnstalleerd: de terreindecals van het level, de catalogus van het grootste level, meshes binnen hun grenzen, groepsleden, vegetatie die op het gedecodeerde terrein staat |
| `test_vpk.py` | de map, weigeringen, gesplitste archieven; geïnstalleerd: kaarten openen, CRC's kloppen, de navigatiemesh |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, terreintegels en wereldbestanden; de `enfusion-world`-export |
| `test_forzacars.py` | het `.h3dcars`-bestand dat het `cars`-commando schrijft |
| `test_unreallevel.py` | Unreal 5-landschappen, HLOD-structuren, water; de `ue-map`-export |

## Tests op geïnstalleerde spellen {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
zoekt spellen voor de tests. `steam_common()` geeft de `steamapps\common` van elke Steam-bibliotheek (ook Steams eigen mappen), en `installed(*globs)`
geeft de paden die overeenkomen met een van de globs eronder, recursief waar een glob `**` heeft. Elke test bepaalt zelf wat hij nodig heeft:

| Test | Zoekt naar | Slaat over met |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` met een **niet-versleutelde** index, tot 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` in `*/*_Data` of `*/*/*_Data` die de lezer aanvaardt, tot 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, tot 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | de circuits uit de FH Companion-bibliotheek (start en finish binnen 50 m), met de meeste ronden, die `find_track` plaatst; of `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Draai alleen de tests van één spel, of richt de Forza-kantsteentest op een baan:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Tests op geïnstalleerde spellen lezen alleen uit de spellen. Ze schrijven niets in spelmappen. De uitvoer van de tests gaat naar de tijdelijke mappen van pytest.

## Conventies {#conventions}

- **Weigeren in plaats van raden.** Elke lezer geeft zijn eigen uitzondering (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) met een melding die zegt wat er gevonden is en waarom het niet is gelezen.
- **Controleer tegen het formaat zelf.** Een hash, een CRC, een keten van offsets, een opgeslagen begrenzingsdoos, het rijden dat op de grond ligt. Niet "het crashte niet".
- **Geen sleutels, geen meegeleverde code van derden.** Zie [Regels en licenties](rules-and-licences.md).
- **Vertrouwelijke gegevens blijven buiten de repository.** Spelbestanden, exports, ronden, opnames en screenshots gaan nooit in de repository. `.gitignore` sluit ze uit per map en per type. Tests gebruiken synthetische gegevens en geïnstalleerde spellen, nooit spelinhoud die in de repository staat.
