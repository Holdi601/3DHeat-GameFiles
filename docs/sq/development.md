---
title: "Zhvillimi"
nav_order: 14
lang: "sq"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Zhvillimi {#development}

## Struktura {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Harta e moduleve {#module-map}

| Moduli | Çfarë bën |
|---|---|
| `__main__.py` | kryen kontrollin e përditësimit, pastaj `cli.main()` |
| `cli.py` | veprat (verbs), `identify`, shpërndarjen e arkivave, shkruesin e kursit Forza |
| `lapinput.py` | çdo formë xhiroje në pozicione; kërkimin në bibliotekën e FH Companion |
| `corridor.py` | brezi nga të dyja anët e vozitjes, si raster 4 m |
| `surfaces.py` | llojet e tokës, emrat e pjesëve dhe ngjyrat e tyre |
| `glb.py` | shkruesin e `.glb` (pjesë, normale, ngjyra, tekstura, kuantizim) |
| `courseexport.py` | Forza: UV-të planare të pllakave, ndarjen rrugë/buzë, pjekjen e tokës, ngritjen e decal-eve |
| `forzainstall.py` | bibliotekat Steam dhe Xbox; pistën Forza ku bën pjesë një kuti |
| `minizip.py` | arkivat `.minizip` të ForzaTech dhe listat e emrave të tyre |
| `forzatech.py` | `.modelbin`: copat, buferat, strukturat, nën-rrjetat, materialet |
| `forzaterrain.py` | pllakat e terrenit sipas vendit; klasat e sipërfaqes |
| `forzatexture.py` | mostrat `.pb`; hartat e pllakave; pjekjen e tokës |
| `forzamaterial.py` | `AssetManifest.xml`; cila teksturë e ngjyros një model; stinët |
| `forzaplacement.py` | vendosjet `.pgeo`, nivelet e modelit, teksturat, prerjet, zëvendësuesit, buxhetin |
| `beamng.py` | instalimin e BeamNG, sistemin e montuar të skedarëve, skenën, terrenin, materialet |
| `beamngcourse.py` | eksportin e kursit BeamNG |
| `beamngshape.py` | format e përpiluara `.cdae` |
| `beamngcollada.py` | alternativën `.dae` |
| `acrally.py` | instalimin e AC Rally, etapat, vendosjen e komponentëve, vëllimin e teksturës virtuale |
| `acrallycourse.py` | eksportin e kursit AC Rally: përshtatjen e kornizës, tokën, vendosjen |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | paketat e gatuara të Unreal 5 |
| `unversioned.py` | skemat dhe lexuesin e vetive pa version |
| `unrealmesh.py` | rrjetat statike të gatuara |
| `unrealtexture.py` | teksturat dhe teksturat virtuale me transmetim |
| `oodle.py` | gjetjen dhe thirrjen e një biblioteke Oodle të instaluar |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | kontejnerët, paketat dhe rrjetat e Unity |
| `frostbite.py` | Frostbite `.toc`, tabelat e seksioneve, paketat e instalimit, vendndodhjet e copave, ngarkesat |
| `frostbitebundle.py` | paketat e brendshme të Frostbite, manifestet e paketave, katalogun e një niveli, listën e niveleve |
| `frostbiteebx.py` | ndarjet RIFF EBX të Frostbite pa bibliotekë llojesh |
| `frostbitemesh.py` | Frostbite MeshSet dhe copat e tij të niveleve të detajit |
| `frostbiteterrain.py` | pemën e transmetimit të terrenit të Frostbite, faqet e lartësive, rrjetën e tokës |
| `frostbitematerial.py` | teksturat e Frostbite (mip BC1/BC3/BC7), depot e blloqeve të shaderave, zgjedhjen e hartës së ngjyrave |
| `frostbitedecals.py` | decal-et e terrenit të Frostbite dhe pjekjen e tokës |
| `frostbitenav.py` | pllakat e rrjetës së navigimit të Frostbite: sipërfaqet e ecshme të ushtarëve |
| `frostbitelevel.py` | grupet e modeleve statike të Frostbite, vendosjen, eksportin `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | komponentët e peizazhit të Unreal 5: hartat e lartësive në rrjetën e tokës (`ue-map`) |
| `unreallevel.py` | hartat World Partition të Unreal 5: listimin, strukturat HLOD, ujin, eksportin `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, pllakat e terrenit, `resourceDatabase.rdb` |
| `enfusionworld.py` | botët e Arma Reforger: skedarët `.ent`, kutitë, eksportin `enfusion-world` |
| `forzacars.py` | çdo makinë Forza me detaj të ulët në `.h3dcars` (`cars`) |

Të gjitha modulet janë në GitHub nën
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Ekzekutimi i testeve {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` cakton `testpaths = tests` dhe `-q`. Dy lloje testesh kanë rëndësi, për
arsye të ndryshme:

- **Testet sintetike** i ndërtojnë arkivat bajt pas bajti dhe ekzekutohen kudo. Ato fiksojnë
  strukturat e fushave që në një kohë ishin gabim: baza 64-bit e segmentit `.minizip`
  dhe mbushja e saj për përafrim, ikja e madhësisë së bllokut në pak, u32-ja e kokës së Unity
  midis dy int64-ve, indeksi `0x7FFF` i VPK, x-i i ndarë i normales së Forza.
- **Testet me lojë të instaluar** ekzekutohen me skedarët e vërtetë kur loja është në
  kompjuter, dhe **anashkalohen** (nuk dështojnë) kur nuk është. Janë e vetmja gjë
  që kap një strukturë që është e saktë për një skedar të vogël e e gabuar për një të madh.

### Fixtures {#fixtures}

| Fixture | Ndërton |
|---|---|
| `tests/forza_fixtures.py` | arkiva `.minizip` (me bazën 64-bit, mbushjen, kodekët e përzier), manifeste, modele `.modelbin` dhe terren, mostra `.pb` |
| `tests/beamng_fixtures.py` | një instalim të vogël BeamNG: `gameengine.zip`, `content`, një zip niveli me terren 64 m, një shirit asfalti, një decal rruge, një parmak, një prefab, një send pylli, detin, materialet dhe forma `.cdae` në strukturën e dokumentuar |
| `tests/unreal_fixtures.py` | një kontejner IoStore me një direktori, një paketë zen, një bllok vetish pa version |
| `tests/frostbite_fixtures.py` | tabela Frostbite, pako, ndarje EBX, rrjeta dhe faqe terreni, bajt pas bajti |

### Skedarët e testeve {#test-files}

| Skedari | Mbulon |
|---|---|
| `test_minizip.py` | leximin mbrapsht, bazën 64-bit, tabelat e paketave tek e çift, refuzimet, skedarin e emrave |
| `test_forzatech.py` | tabelën e copave dhe zinxhirin, refuzimet; të instaluar: zinxhirët dhe etiketat e modeleve të vërteta |
| `test_forza_geometry.py` | vendosjen në botë, strukturën e kulmeve, formatet e refuzuara, nën-rrjetat, normalet dhe UV-të |
| `test_forzaterrain.py` | rrjetën e pllakave (1023 kundrejt 512 m), prerjen, nxjerrjen |
| `test_forzatexture.py` | kokën e mostrës, dekodimin, raftin e teksturave, pjekjen e tokës |
| `test_forzamaterial.py` | manifestin, emrat, hash-et e materialeve, zgjedhjen e ngjyrës, stinët |
| `test_forzaplacement.py` | regjistrin `.pgeo`, vendosjen e kopjeve, nivelet, variantet, sipërfaqet transparente, një kuti të plotë, buxhetin, ngjyrën zëvendësuese, buxhetin automatik; të instaluar: bordurat në tokë |
| `test_forzainstall.py` | gjetjen e lojës, zgjedhjen e pistës |
| `test_courseexport.py` | UV-të e pllakave, planin e pjesëve, ngritjen e decal-eve |
| `test_course_cli.py` | veprat e plota `course` dhe `courses` në një pistë sintetike; `terrain --route` me shenjë të renditjes së bajteve (byte-order mark), dhe pa `bounds` |
| `test_archive_cli.py` | `identify`, `list` dhe `extract` në çdo arkiv me lexues (`.pak`, IoStore, `.vpk`, `.minizip` me dhe pa emrat e tij, zip, `.cdae`, `.ter`); dështimet si një rresht dhe kod daljeje: një pak i enkriptuar, një kontejner i enkriptuar, një skedar që nuk është arkiv, një `--key` i keq |
| `test_corridor.py` | brezin, prerjen e terrenit me të |
| `test_lapinput.py` | çdo formë xhiroje, kutinë, dështimet, kërkimin e emrit të kursit, cila lojë është një dosje |
| `test_surfaces.py` | cilët emra vendosin një sipërfaqe, cilët jo, emrat e pjesëve |
| `test_glb.py` | skedari është i vlefshëm, nyjet mbartin klasën, refuzimet, kuantizimin |
| `test_beamng.py` | format, nivelin, kategoritë, gjetjen e nivelit nga një xhiro, kursin, alternativën Collada; të instaluar: `.cdae` kundrejt `.dae`, çdo nivel hapet |
| `test_acrally.py` | kontejnerët, paketat, vetitë, transformimet, përshtatjen e kornizës, pjesët e modeleve të vendosura dhe buxhetin, teksturat virtuale; të instaluar: etapat dhe ngjyra e pjekur e tokës |
| `test_pak.py` | fundin, hyrjet, ikjen e madhësisë së bllokut, refuzimet; të instaluar: ofsetet dhe SHA-1 |
| `test_unity.py` | refuzimet; të instaluar: tabela e objekteve e mbulon skedarin, vargjet e versionit, kufijtë e rrjetave |
| `test_frostbite.py` | kokat e nënshkruara kundrejt të turbulluarave, refuzimet, paketat e instalimit (dy paketa me të njëjtin numër blobi); të instaluar: çdo tabelë, superpaketat, zinxhirët e seksioneve, id-të e dallueshme, ngarkesat e mostruara nga paketa e duhur |
| `test_frostbitelevel.py` | id-të e copave të çiftuara me vendndodhjet e tyre, paketat e brendshme, manifestet, një MeshSet me seksion hijeje dhe UV, një anëtar grupi, konventën e transformimit, një terren me dy nivele, zgjedhjen e hartës së ngjyrave, një copë teksture që i mungojnë mip-et më të mëdha, mostruesin që përsërit, regjistrat e decal-eve, një decal të kompozuar nga alfa e tij, një fletë decal-esh që humbet përballë hartës së vetë sipërfaqes, tabelën e nivelit të zgjedhur mes lojës bazë dhe përditësimeve të saj, pllakat e navigimit (sipërfaqet e mbajtura, lidhjet e lëna jashtë, refuzimet, rrjetat e detajit), teksturat që përsëriten të shkruara me koordinatat e tyre, trekëndëshat e prerë ku përsëritet teksturat e tyre për daljen e kapur (clamped), ngjyrën e tokës nga materialet e sipërfaqes së saj, faqet e maskave (BC4 dhe të pakompresuara) të vendosura në kuadrantet e tyre dhe të refuzuara kur kufijtë e tyre nuk përputhen, faqet e colormap të vendosura në kuadrantet e tyre dhe të gjetura pas faqeve të maskave që i numëron pema e maskave, fushat e largësisë, paletat dhe maskat e kanaleve që nuk merren kurrë si ngjyrë, ngjyrimin e një blloku dhe një hartë gri të lyer me të, një kulm palete në qendër të mostrës së vet, rrjetën e pjerrësisë të përhapur mbrapsht në mënyrë bilineare, mbivendosjen e një objekti të vizatuar përmes shpalosjes së tij, bllokun e një variacioni me çelës hash-in e tij dhe të arritur përmes një blloku binjak, një fletë shkronjash të vendosur nga koordinatat e katërta të teksturës mbi sipërfaqen ku lyhet, bojën e një decal-i të lexuar nga materiali i tij dhe vijat e pistës e gjurmët e gomave të vizatuara, hartat njëkanalëshe të dekoduara, rrjetat e shkatërrueshme të etiketuara në pjesët dhe extras e tyre, rrjetat blockout, kinematike dhe ndriçimi të lëna jashtë dhe një strukturë colormap që nuk lexohet, hartat cut-out dhe materialet e tyre PNG të maskuara me dy anë, pllakat e sfondit të emërtuara nga rrjeta e tyre; të instaluar: decal-et e terrenit të nivelit, katalogun e nivelit më të madh, rrjetat brenda kufijve të tyre, anëtarët e grupeve, bimësinë që qëndron mbi terrenin e dekoduar |
| `test_vpk.py` | direktorinë, refuzimet, arkivat e ndara; të instaluar: hartat hapen, CRC-të përputhen, rrjeta e navigimit |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, pllakat e terrenit dhe skedarët e botës; eksportin `enfusion-world` |
| `test_forzacars.py` | skedarin `.h3dcars` që e shkruan vepra `cars` |
| `test_unreallevel.py` | peizazhet e Unreal 5, strukturat HLOD, ujin; eksportin `ue-map` |

## Testet me lojë të instaluar {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
gjen lojërat për testet. `steam_common()` liston `steamapps\common` të çdo biblioteke
Steam (përfshirë dosjet e vetë Steam), dhe `installed(*globs)`
kthen shtigjet që përputhen me ndonjë glob nën to, në mënyrë rekursive ku një glob ka
`**`. Çdo test vendos çfarë i duhet:

| Testi | Kërkon | Anashkalohet me |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` me indeks **të paenkriptuar**, deri në 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` në `*/*_Data` ose `*/*/*_Data` që lexuesi i pranon, deri në 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, deri në 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | qarqet e bibliotekës FH Companion (fillimi dhe fundi brenda 50 m), me më shumë xhiro, që `find_track` i vendos; ose `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Ekzekuto vetëm testet e një loje, ose drejto testin e bordurave të Forza te një kurs:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testet me lojë të instaluar lexojnë vetëm nga lojërat. Nuk shkruajnë asgjë në dosjet e
lojërave. Daljet e testeve shkojnë në dosjet e përkohshme të pytest.

## Konventat {#conventions}

- **Refuzo në vend që të hamendësosh.** Çdo lexues ngre përjashtimin e vet
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) me
  një mesazh që thotë çfarë u gjet dhe pse nuk u lexua.
- **Kontrollo kundrejt vetë formatit.** Një hash, një CRC, një zinxhir ofsetesh, një kuti
  kufizuese e ruajtur, vozitja që shtrihet mbi tokë. Jo "nuk u rrëzua".
- **Pa çelësa, pa kod pronësor të përfshirë.** Shih [Rregullat dhe licencat](rules-and-licences.md).
- **Të dhënat konfidenciale mbeten jashtë.** Skedarët e lojërave, eksportet, xhirot, regjistrimet dhe
  pamjet e ekranit nuk hyjnë kurrë në repozitor. `.gitignore` i përjashton sipas dosjes
  dhe sipas llojit. Testet përdorin të dhëna sintetike dhe lojëra të instaluara, kurrë përmbajtje loje
  të futur në repozitor.
