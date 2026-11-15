---
title: Begrænsninger og kendte huller
nav_order: 10
lang: "da"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Begrænsninger og kendte huller {#limits-and-known-gaps}

Hvad værktøjet ikke gør, hvad det kun gør delvist, og hvor dets adfærd er ujævn. De fleste huller er bevidste afvisninger. At afkode uden en fil at tjekke mod giver et output, der ser rigtigt ud, men ikke er det.

## Spil {#games}

| Spil | Course-eksport | Hvorfor ikke, eller hvor langt |
|---|---|---|
| Forza Horizon | ja | jordfarven er en fortolkning (se nedenfor) |
| BeamNG.drive | ja | ingen jordbevoksning, gentagne modelteksturer udjævnet |
| Assetto Corsa Rally | ja | modeller i flade farver; endnu ikke kørt på en runde optaget i spillet |
| Assetto Corsa EVO | **nej** | alt indhold ligger i én pakke sløret med en nøgle, og dette værktøj finder ingen nøgler |
| Battlefield 6 (niveau-eksport, `level`) | ja, et helt niveau | terræn, grupperede og enkeltvis placerede meshes og deres farvekort, soldaternes navigationsmesh, udklippet bevoksning; spilområdets jordfarve er grov (32 m pr. pixel, eller én gennemsnitsfarve); ingen transparens eller normalmaps; ødelæggelige meshes markeret, deres ødelagte tilstande eksporteres ikke |
| Unreal 5 World Partition-spil (kort-eksport, `ue-map`) | ja, et helt kort | landskabet præcist; bygninger som kortets forenklede HLOD-meshes, ikke modellerne i fuld detalje; vandområder; ingen bevoksning, decals eller jordfarve |
| Arma Reforger (verdens-eksport, `enfusion-world`) | ja, en hel verden | terræn i sine egne farver og havet; bygninger, rekvisitter og klipper som deres modellers bokse, ikke deres trekanter; træer efter ønske (`--trees`), som bokse; ingen søer, floder eller underentiteter |
| iRacing | **nej** | baner leveres i et beskyttet format, der ikke er et mål for filudtræk |
| alt andet | **nej** | der findes ingen banelæser; rekonstruér ud fra spilning med 3DHeat GameCapture, eller analysér runderne i viewer'ens Løbsanalyse-fane uden en bane |

## Motorer og formater {#engines-and-formats}

| Format | Ikke implementeret |
|---|---|
| Unreal `.pak` | versioner før 8; indeks med kun stihash (navne kan ikke gendannes); poster i indeksets overløbsliste (springes over); afkodning af `.uasset`-/`.umap`-indhold fra en pak |
| Unreal IoStore | krypterede containere (afvist, ingen nøglemulighed); oplistning af en container uden mappeindeks (den navngiver ingen filer); versionerede pakker; meshes kun med Nanite og meshes, der ikke er inline; skeletmeshes; egenskaber for klasser uden skema; instancerede komponenters egenskaber (layoutet ændret i spillets build); spline-meshes og decal-komponenter |
| Unity | formater før 22 (Unity 2019 og ældre); filer med indlejrede typetræer; komprimerede meshes; alle klasser undtagen `Mesh`, så ingen transformationer, materialer eller scener; `meshes` på en bundle; `list`/`extract` (brug `meshes`) |
| Frostbite | XOR-slørede tabeller; terrænets laggraf (masker læses i omkring en tredjedel af de kontrollerede niveauer); objektblueprints ud over meshes (spillogik, effekter, lyde); mesh-niveauer gemt inline; normal- og andre kort, alfa ud over udklip; terrænhuller; typebiblioteket (krypteret i det oprindelige filsystem, ikke rørt); en kommando til at liste eller udtrække enkelte assets |
| Source 2 | kompilerede assets (`.vmdl_c`, `.vtex_c`); CS2's navmesh (version 36) |
| ForzaTech | positionsformater ud over fire skalerede shorts; indeksformater ud over u16; teksturkoder ud over 0, 9, 13; terrænshaderens materiallag; tangenter |
| BeamNG | skinnede og decal-meshes; animation; procedural jordbevoksning; kulisser i verdenens kant |
| Unreal-landskaber og World Partition-kort | landskaber, hvis højdekort ligger i de bagte celler; redigeringslag og huller; Nanite-landskabsmeshes; modeller i fuld detalje placeret i cellerne; bevoksning; landskabsmaterialer |
| Enfusion | modeltrekanter (`.xob`-geometri er komprimeret i et layout, der ikke læses); `.edds` med DX10-forud headers; indlejrede objektværdier i verdensfiler (springes over, tælles); underentiteter; genererede søer og floder; `list`/`extract` på en `.pak` |

## Adfærd, det er godt at kende {#behaviour-worth-knowing}

- **Forza-jordfarven er ikke spillets.** Den indbagte tekstur tegnes ud fra flisekortene, der siger *hvor* asfalt, kort græs, ru jord og skov er. Den bruger faste farver og skygge, fordi terrænshaderens egne materiallag ikke afkodes.
- **`--no-textures` fjerner også Forzas kant.** Asfalt/kant-delingen bruger asfaltmasken, der følger med de indbagte kort. Uden teksturer forbliver vejstrimler hele som vej.
- **Et budget du angiver, kan kun overskrides af kantsten.** Kantsten (og BeamNGs kørselsflade-modeller) forenkles eller udelades aldrig, i noget spil, så et `--detail-budget`, der er mindre end det, de koster, overskrides af dem alene; alt andet udelades først. Se [Detaljeniveauer og budgettet](detail-budget.md).
- **Valgmuligheder, der ikke gælder, ignoreres stille**: `--season` for BeamNG og AC Rally, `--track` for BeamNG og AC Rally, `--level`/`--install` for Forza.
- **En Battlefield 6-niveaus jordfarve er grov væk fra dets decals.** Højdefeltet farves ud fra terrænbaggrundens farvekort, 32 m pr. pixel ved det største mip-niveau niveauet leverer, eller, hvor intet baggrundskort dækker, ud fra midterfarven i terrænets fladematerialer. `--ground-texture` ganger det med terrænets farvekort (ved 0,5 m pr. pixel, hvor niveauet har et) og indbager veje, pladser, banelinjer, dækspor og markeringer ovenpå, i deres materialers malingfarve hvor en er sat, og en neutral en hvor ikke; vejens variationsmasker udelades. Spillet blander sine fladelag i en shadergraf, der ikke læses; eksporten lægger lagenes farver ud efter deres masker og højdefeltets hældning, efter en regel eget til den, og et niveau, hvis maskesider ikke passer sammen, får én farve. Hvert lag er dets farvekorts gennemsnit, ikke dets tekstur. Se [Frostbite](reader-frostbite.md#terrain-layers). Stykker af højdefeltet i forskellig opløsning mødes med små trin.
- **En Battlefield 6-farvekort vælges, den læses ikke.** En shaderblok navngiver hver tekstur, den sampler, uden at sige hvilken der er farven; valget sker efter navn (se [Frostbite](reader-frostbite.md#textures-and-materials)) og kan vælge et trim- eller detaljeark for en flade. Decal-ark (`t_de_...`) taber til fladens eget kort; et skilts decal, tegnet som dets panel, viste sit skjold drejet en kvart omgang. Distance-felter, paletter og kanalmasker tages aldrig. Bygninger i baggrunden tegnes i deres paletts farver; gråtoneskort tager materialets tint efter en regel fra eksportøren selv, da parameternes navne er hashede, og et materiale, der maler et gråtoneskort gennem en maske med flere tints, får én af dem.
- **Battlefield 6-terrænhuller skæres ikke.** Hvor et niveaus gangbare jord løber under højdefeltet, må spillet have skåret terrænet, og eksporten gør ikke det. Udelukket som hvor hullerne er: terrænets lagmasker (ingen er koncentreret der), dets 67 x 67 noderaster, en reserveret højdeværdi (ingen højdeside holder 0 eller 65.535), nodernes flag (alle ens), og meshes eller assets, der skærer jorden: det, der er placeret under jorden der, er klippe- og klippemeshes, og intet asset i niveauet er navngivet for huller, tunneler eller huler. To rastertræer er run-length-afkodet, men ikke placeret, og er det, der er tilbage (se [Frostbite](reader-frostbite.md#terrain-layers)).
- **En Battlefield 6-objektvariation når en sektion via dens tvillinger.** En placeret kopis variation vælger sine sektioners shaderblokke efter nøgle; hvor en mesh ikke har en blok for en variation, tages variantet af en anden meshes sektion med en identisk standardblok (se [Frostbite](reader-frostbite.md#textures-and-materials)). Det er eksportørens regel; en sektion uden tvilling, der varierer, beholder sit standardudseende.
- **Battlefield 6-lagdelte materialer tegnes som deres base og ét ark.** En vægplade med skrift tegnes som sin puds med bogstavarket over; materialets andre lag (overlejret smuds gennem sin maske, detalje- og mosskort) blandes ikke ind.
- **Navigationsmeshen er AI'ens, ikke spillernes.** Den dækker det, en soldat kan gå hen til: jorden, gulve og trapper og nogle tage, men ikke alle høje punkter. Forbindelserne mellem flader (spring, stiger, spring over) udelades.
- **Et Battlefield 6-niveau inkluderer hvert spilles lag.** Objekter, som kun ét spil placerer, kan overlappe et andet. `--skip` udelader lag efter navn.
- **`courses` gælder kun Forza**, og plukker kun bibliotekmapper op, der hedder `... (course_...)`.
- **BeamNG-rundens koordinatsystem antages** at være viewer-systemet `(x, z, -y)`, som 3DHeat-optageren skriver. Runder fra en anden optager i BeamNGs rå koordinatsystem ville ikke blive placeret.
- **`list` og `extract` tager arkiverne, ikke alle formater.** De åbner en `.pak`, en IoStore-`.utoc`, en `.vpk`, en `.minizip` og en zip. En Unity-container læses med `meshes`, et Frostbite-niveau med `level`, og en `.cdae` eller `.ter` er en fil frem for et arkiv (`identify` navngiver den). En `.minizip` uden sin `ChunkContentsMiniZip<n>.txt` ved siden af listes efter postnummer.
- **BeamNG-modeller med gentagne teksturer bruger gennemsnitsfarver**, fordi `.glb`-samplet klemmer, og viewer'en pakker teksturer ind i et atlas.
- **Windows, i praksis.** Steam-stier under `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames`, og en `*_win64.dll` for Oodle. Andre platforme er ikke testet.

## Ikke verificeret {#unverified}

- Ældre Python-versioner (værktøjet er kørt med 3.13).
- Assetto Corsa Rally med en runde optaget i spillet. Det er kun testet med syntetiske runder i tilfældige frames.
- glTF-viewere ud over 3DHeat-viewer'en.
- Om hvert spils koordinatsystem er venstre- eller højrehåndet. Eksporten beholder hvert spils telemetri-koordinatsystem, så runder og baner passer sammen uanset.
- Betydningen af `WaterBlock`'s lokale z = 0 som dens overflade (BeamNG).
- Frostbite-placering på andre spil end Battlefield 6, og på Battlefield 6 efter en opdatering, der ændrer gruppemedlemmets layout. Læseren finder da ingen grupper og siger det.
- Om en Battlefield 6-eksport passer med positioner, spillet rapporterer. Koordinaterne er spillets egne, som for de andre spil, men ingen optagelse er endnu lagt over en.
