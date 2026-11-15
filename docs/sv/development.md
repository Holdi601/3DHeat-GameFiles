---
title: Utveckling
nav_order: 14
lang: "sv"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Utveckling {#development}

## Struktur {#layout}

```
heat3d_gamefiles/     paketet: läsarna, banexporterna, kommandoraden
heat3d_update/        kontrollen av nya versioner och uppdateraren (se Uppdateringar)
tests/                syntetiska tester, testfiler och tester mot installerade spel
docs/                 den här dokumentationen (docs/wiki genereras från den)
VERSION               den installerade versionen, jämförd med GitHubs utgåvor
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modulkarta {#module-map}

| Modul | Vad den gör |
|---|---|
| `__main__.py` | kör kontrollen av uppdateringar, sedan `cli.main()` |
| `cli.py` | kommandona, `identify`, arkivval, Forza-banskrivaren |
| `lapinput.py` | varje varvformat till positioner; uppslagning i FH Companion-biblioteket |
| `corridor.py` | bandet på båda sidor om körningen, som en 4 m-raster |
| `surfaces.py` | markslagen, deras delnamn och färger |
| `glb.py` | `.glb`-skrivaren (delar, normaler, färger, texturer, kvantisering) |
| `courseexport.py` | Forza: plana rut-UV, väg/kant-delning, markinbakning, dekal-lyftning |
| `forzainstall.py` | Steam- och Xbox-bibliotek; vilken Forza-bana en låda hör till |
| `minizip.py` | ForzaTech `.minizip`-arkiv och deras namnlistor |
| `forzatech.py` | `.modelbin`: chunkar, buffertar, layouter, undermeshar, material |
| `forzaterrain.py` | terrängrutor efter plats; ytklasser |
| `forzatexture.py` | `.pb`-färgprov; rutkartor; markinbakningen |
| `forzamaterial.py` | `AssetManifest.xml`; vilka texturfärger en modell har; säsonger |
| `forzaplacement.py` | `.pgeo`-placeringar, modellnivåer, texturer, utskärningar, stand-ins, budgeten |
| `beamng.py` | BeamNG-installation, monterat filsystem, scen, terräng, material |
| `beamngcourse.py` | BeamNG-banexporten |
| `beamngshape.py` | `.cdae`-kompilerade former |
| `beamngcollada.py` | `.dae`-reserv |
| `acrally.py` | AC Rally-installation, etapper, komponentplacering, virtuell texturvolym |
| `acrallycourse.py` | AC Rally-banexporten: riktningsanpassning, mark, placering |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 cachade paket |
| `unversioned.py` | scheman för oversionerade egenskaper och läsaren |
| `unrealmesh.py` | cachade statiska meshar |
| `unrealtexture.py` | texturer och strömmade virtuella texturer |
| `oodle.py` | hitta och anropa ett installerat Oodle-bibliotek |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-behållare, paket, meshar |
| `frostbite.py` | Frostbite `.toc`, sektionstabeller, installationspaket, chunkplatser, nyttolaster |
| `frostbitebundle.py` | Frostbite inline-paket, paketmanifest, en nivås katalog, nivålistan |
| `frostbiteebx.py` | Frostbite RIFF EBX-partitioner utan typbibliotek |
| `frostbitemesh.py` | Frostbite MeshSet och dess chunkar för detaljnivåer |
| `frostbiteterrain.py` | Frostbites terrängströmningsträd, höjdsidor, markmeshen |
| `frostbitematerial.py` | Frostbite-texturer (BC1/BC3/BC7-mipnivåer), skuggblockens depåer, val av färgkarta |
| `frostbitedecals.py` | Frostbites terrängdekaler och markinbakningen |
| `frostbitenav.py` | Frostbites navigeringsmeshrutor: de walkable ytor soldaterna går på |
| `frostbitelevel.py` | Frostbites statiska modellgrupper, placering, `level`-exporten |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5-landskapskomponenter: höjdkartor till markmeshen (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition-kartor: listning, HLOD-strukturer, vatten, `ue-map`-exporten |
| `enfusion.py` | Enfusion `.pak`, `.edds`, terrängrutor, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger-världar: `.ent`-filer, lådor, `enfusion-world`-exporten |
| `forzacars.py` | varje Forza-bil i låg detalj till `.h3dcars` (`cars`) |

Alla moduler finns på GitHub under
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Köra testerna {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` sätter `testpaths = tests` och `-q`. Två slag av tester spelar roll,
av olika skäl:

- **Syntetiska tester** bygger arkiv byte för byte och körs var som helst. De låser
  fältlayouter som vid något tillfälle var fel: `.minizip`-segmentbasen på 64 bitar
  och dess justeringsutfyllnad, pak-blockstorlekens escape, Unity-headerns u32 mellan
  två int64, VPK:ns `0x7FFF`-index, Forza-normalens delade x.
- **Tester mot installerade spel** körs mot de riktiga filerna när spelet finns på
  datorn, och **hoppar över** (de misslyckas inte) när det inte gör det. De är det enda
  som fångar en layout som är rätt för en liten fil men fel för en stor.

### Testfiler {#fixtures}

| Testfiler | Bygger |
|---|---|
| `tests/forza_fixtures.py` | `.minizip`-arkiv (med 64-bitarsbas, utfyllnad, blandade kodekar), manifest, `.modelbin`-modeller och terräng, `.pb`-färgprov |
| `tests/beamng_fixtures.py` | en liten BeamNG-installation: `gameengine.zip`, `content`, en nivå-zip med 64 m terräng, en asfaltremsa, en vägdekal, ett räcke, en prefab, ett skogsobjekt, havet, material och `.cdae`-former i den dokumenterade layouten |
| `tests/unreal_fixtures.py` | en IoStore-behållare med en katalog, ett zen-paket, ett oversionerat egenskapsblock |
| `tests/frostbite_fixtures.py` | Frostbite-tabeller, paket, EBX-partitioner, meshar och terrängsidor, byte för byte |

### Testfiler {#test-files}

| Fil | Täcker |
|---|---|
| `test_minizip.py` | läsning tillbaka, 64-bitarsbasen, jämna och udda paketstabeller, avvisningar, namnfilen |
| `test_forzatech.py` | chunktabellen och kedjan, avvisningar; installerat: riktiga modellers kedjor och taggar |
| `test_forza_geometry.py` | världsplacering, vertexlayout, avvisade format, undermeshar, normaler och UV |
| `test_forzaterrain.py` | rutnätet (1023 mot 512 m), klippning, extrahering |
| `test_forzatexture.py` | färgprovets header, avkodning, texturhyllan, markinbakningen |
| `test_forzamaterial.py` | manifestet, namn, materialhashar, färgvalet, säsonger |
| `test_forzaplacement.py` | `.pgeo`-posten, placering av kopior, nivåer, varianter, genomskinliga ytor, en hel låda, budgeten, platshållarfärgen, den automatiska budgeten; installerat: kantstenar på marken |
| `test_forzainstall.py` | hitta spelet, välja banan |
| `test_courseexport.py` | rut-UV, delplanen, dekallyftningen |
| `test_course_cli.py` | hela verben `course` och `courses` på en syntetisk bana; `terrain --route` med en byte-ordningsmarkering, och utan `bounds` |
| `test_archive_cli.py` | `identify`, `list` och `extract` på varje arkiv med en läsare (`.pak`, IoStore, `.vpk`, `.minizip` med och utan namn, zip, `.cdae`, `.ter`); fel som en rad och en avslutningskod: ett krypterat pak, en krypterad behållare, en fil som inte är ett arkiv, en felaktig `--key` |
| `test_corridor.py` | bandet, att klippa terräng med det |
| `test_lapinput.py` | varje varvformat, lådan, fel, uppslag av banans namn, vilket spel en mapp är |
| `test_surfaces.py` | vilka namn som avgör en yta, vilka som inte gör det, delnamn |
| `test_glb.py` | filen är giltig, noder bär klassen, avvisningar, kvantisering |
| `test_beamng.py` | former, nivån, kategorier, att hitta nivån från ett varv, banan, Collada-reserven; installerat: `.cdae` mot `.dae`, varje nivå öppnas |
| `test_acrally.py` | behållare, paket, egenskaper, transformer, riktningsanpassningen, placerade modellers delar och budgeten, virtuella texturer; installerat: etapper och den inbakade markfärgen |
| `test_pak.py` | footer, poster, blockstorlekens escape, avvisningar; installerat: offset och SHA-1 |
| `test_unity.py` | avvisningar; installerat: objekttabellen täcker filen, versionssträngar, meshgränser |
| `test_frostbite.py` | signerade mot maskerade headers, avvisningar, installationspaket (två paket med samma bloblnummer); installerat: varje tabell, superbundles, sektionskedjor, unika id, samplade nyttolaster från rätt paket |
| `test_frostbitelevel.py` | chunk-id parade med sina egna platser, inline-paket, manifest, en MeshSet med en skuggsektion och UV, en gruppmedlem, transformkonventionen, en terräng med två nivåer, val av färgkarta, en texturchunk som saknar sina största mipnivåer, den upprepande samplaren, dekalposter, en dekal sammansatt via sin alfa, ett dekalark som förlorar mot ytans egen karta, nivåns tabell vald bland grundspelet och dess uppdateringar, navigeringsrutor (ytor behålls, länkar utelämnas, avvisningar, detaljmeshar), upprepande texturer skrivna med egna koordinater, trianglar klippta där deras textur upprepas för klämd utdata, markens färg från dess ytmaterial, maskssidor (BC4 och okomprimerade) placerade på sina kvadranter och avvisade när deras kanter inte stämmer, färgkartssidor placerade på kvadranter och hittade efter maskssidorna som maskträdet räknar, distansfält, paletter och kanalmasker tas aldrig som färg, ett blocks tonning och en grå karta målad med den, en palettvertex i sin swatchs mitt, rutnätet för lutningen spridet tillbaka bilinjärt, ett objekts överlägg ritat genom dess uppvikning, en variants block nycklat med sin hash och nått via ett tvillingblock, ett bokstavsark lagt på av sina fjärde texturkoordinater över ytan det målas på, en dekals färg läst från sitt material och bankande linjer och däckspår ritade, enkanalskartor avkodade, förstörbara meshar taggade i sina delar och extras, blockout-, cinematiska och belysningsmeshar utelämnade och ett kartlayout som inte läses, utklippskartor och deras maskerade, tvåsidiga PNG-material, bakgrundsrutor namngivna efter sin mesh; installerat: nivåns terrängdekaler, den största nivåns katalog, meshar inom sina gränser, gruppmedlemmar, vegetation som står på den avkodade terrängen |
| `test_vpk.py` | katalogen, avvisningar, delade arkiv; installerat: kartor öppnas, CRC stämmer, navmeshen |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, terrängrutor och världsfiler; `enfusion-world`-exporten |
| `test_forzacars.py` | `.h3dcars`-filen som `cars`-verbet skriver |
| `test_unreallevel.py` | Unreal 5-landskap, HLOD-strukturer, vatten; `ue-map`-exporten |

## Tester mot installerade spel {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
hittar spel för testerna. `steam_common()` listar varje Steam-bibliotek
`steamapps\common` (Steams egna mappar inräknade), och `installed(*globs)`
returnerar de sökvägar under dem som matchar någon glob, rekursivt där en glob har
`**`. Varje test avgör vad det behöver:

| Test | Letar efter | Hoppar över med |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` med ett **okrypterat** index, upp till 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` i `*/*_Data` eller `*/*/*_Data` som läsaren godtar, upp till 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, upp till 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | FH Companion-bibliotekets banor (start och mål inom 50 m), med flest varv, som `find_track` placerar; eller `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Kör bara ett spels tester, eller peka Forza-kantstenstestet mot en bana:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Tester mot installerade spel läser bara från spelen. De skriver ingenting i
spelmapparna. Testens utdata går till pytests tillfälliga mappar.

## Konventioner {#conventions}

- **Vägra hellre än gissa.** Varje läsare kastar sitt eget undantag
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) med
  ett meddelande som säger vad som hittades och varför det inte lästes.
- **Kontrollera mot formatet självt.** En hash, en CRC, en kedja av offset, en lagrad
  omslutningsruta, att körningen ligger på marken. Inte "den kraschade inte".
- **Inga nycklar, ingen medlevererad proprietär kod.** Se [Regler och licenser](rules-and-licences.md).
- **Konfidentiell data stannar utanför.** Spelfiler, exporter, varv, inspelningar och
  skärmbilder hamnar aldrig i förrådet. `.gitignore` utesluter dem efter mapp och
  efter filtyp. Testerna använder syntetisk data och installerade spel, aldrig
  incheckat spelinnehåll.
