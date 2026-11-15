---
title: Grenzen en bekende lacunes
nav_order: 10
lang: "nl"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Grenzen en bekende lacunes {#limits-and-known-gaps}

Wat de tool niet doet, wat hij maar gedeeltelijk doet, en waar zijn gedrag ongelijk is. De meeste lacunes zijn bewuste weigeringen. Decoderen zonder een bestand om tegen te controleren levert uitvoer op die goed lijkt en het niet is.

## Spellen {#games}

| Spel | Baan-export | Waarom niet, of hoe ver het gaat |
|---|---|---|
| Forza Horizon | ja | de grondkleur is een interpretatie (zie hieronder) |
| BeamNG.drive | ja | geen grondbedekking, herhalende modeltexturen worden afgevlakt |
| Assetto Corsa Rally | ja | modellen in vlakke kleuren; nog niet getest op een ronde die in het spel zelf is opgenomen |
| Assetto Corsa EVO | **nee** | alle inhoud zit in één pakket dat met een sleutel is verhuld, en deze tool herstelt geen sleutels |
| Battlefield 6 (levelexport, `level`) | ja, een compleet level | terrein, gegroepeerde en afzonderlijk geplaatste meshes en hun kleurkaarten, het navigatiemesh van de soldaten, uitgesneden gebladerte; de grondkleur van het speelgebied is grof (32 m per pixel, of één gemiddelde kleur); geen transparantie of normal maps; vernietigbare meshes zijn gelabeld, hun vernielde toestanden niet geëxporteerd |
| Unreal 5 World Partition-spellen (kaartexport, `ue-map`) | ja, een complete kaart | het landschap exact; gebouwen als de vereenvoudigde HLOD-meshes van de kaart, niet de modellen op volledig detail; waterlichamen; geen gebladerte, decals of grondkleur |
| Arma Reforger (wereldexport, `enfusion-world`) | ja, een complete wereld | terrein in zijn eigen kleuren en de zee; gebouwen, rekwisieten en rotsen als de dozen van hun modellen, niet hun driehoeken; bomen op verzoek (`--trees`), als dozen; geen meren, rivieren of kindentiteiten |
| iRacing | **nee** | banen zitten in een beschermd formaat dat geen doel voor bestandsextractie is |
| al het andere | **nee** | er is geen baanlezer; reconstrueer uit gameplay met 3DHeat GameCapture, of analyseer de ronden in het tabblad Race-analyse van de viewer zonder baan |

## Engines en formaten {#engines-and-formats}

| Formaat | Niet geïmplementeerd |
|---|---|
| Unreal `.pak` | versies vóór 8; indexen met alleen path-hashes (namen kunnen niet worden hersteld); items in de overloopslijst van de index (overgeslagen); het decoderen van `.uasset`/`.umap`-inhoud uit een pak |
| Unreal IoStore | versleutelde containers (geweigerd, geen sleuteloptie); een container zonder mapindex tonen (die noemt geen bestanden); versioned pakketten; meshes die alleen Nanite zijn en niet-inline meshes; skeletmeshes; eigenschappen van klassen zonder schema; eigenschappen van geïnstantieerde componenten (de indeling is in de build van het spel veranderd); spline-meshes en decalcomponenten |
| Unity | formaten vóór 22 (Unity 2019 en ouder); bestanden met ingebedde typebomen; gecomprimeerde meshes; elke klasse behalve `Mesh`, dus geen transformaties, materialen of scènes; `meshes` op een bundel; `list`/`extract` (gebruik `meshes`) |
| Frostbite | XOR-verhulde tabellen; de laaggrafiek van het terrein (maskers gelezen in ongeveer een derde van de gecontroleerde levels); objectblauwdrukken anders dan meshes (spellogica, effecten, geluiden); meshniveaus die inline zijn opgeslagen; normal- en andere kaarten, alfa anders dan uitsnijdingen; gaten in het terrein; de typebibliotheek (versleuteld in het initiële bestandssysteem, niet aangeraakt); een commando om losse assets te tonen of extraheren |
| Source 2 | gecompileerde assets (`.vmdl_c`, `.vtex_c`); het CS2 navigatiemesh (versie 36) |
| ForzaTech | positieformaten anders dan vier geschaalde shorts; indexformaten anders dan u16; textuurcodes anders dan 0, 9, 13; de materiaallagen van de terreinshader; tangenten |
| BeamNG | skinned- en decal-meshes; animatie; procedurele grondbedekking; scenery rond de rand van de wereld |
| Unreal-landschappen en World Partition-kaarten | landschappen waarvan de hoogtekaarten in de gebakken cellen staan; bewerkingslagen en gaten; Nanite-landschapsmeshes; modellen op volledig detail die in de cellen geplaatst zijn; gebladerte; landschapsmaterialen |
| Enfusion | modeldriehoeken (de geometrie van `.xob` is in een indeling gecomprimeerd die niet gelezen wordt); `.edds` met pre-DX10-headers; waarden van geneste objecten in wereldbestanden (overgeslagen en geteld); kindentiteiten; gegenereerde meren en rivieren; `list`/`extract` op een `.pak` |

## Gedrag dat je moet kennen {#behaviour-worth-knowing}

- **De grondkleur van Forza is niet die van het spel.** De gebakken textuur komt uit de tegelkaarten die zeggen *waar* asfalt, kort gras, ruw terrein en bosgrond liggen. Ze gebruikt vaste kleuren en schaduw, omdat de materiaallagen van de terreinshader niet worden gedecodeerd.
- **`--no-textures` verwijdert ook Forza's berm.** De splitsing asfalt/berm gebruikt het asfaltmasker dat bij de gebakken kaarten hoort. Zonder texturen blijven wegstroken als één geheel weg.
- **Een budget dat je opgeeft, kan alleen door kantstenen worden overschreden.** Kantstenen (en voor BeamNG de modellen van het rijoppervlak) worden in geen enkel spel vereenvoudigd of weggelaten, dus een `--detail-budget` dat kleiner is dan wat zij kosten, wordt door hen alleen overschreden; al het andere wordt eerst weggelaten. Zie [Detailniveaus en het budget](detail-budget.md).
- **Opties die niet van toepassing zijn, worden stilletjes genegeerd**: `--season` voor BeamNG en AC Rally, `--track` voor BeamNG en AC Rally, `--level`/`--install` voor Forza.
- **De grondkleur van een Battlefield 6-level is grof buiten zijn decals.** Het hoogteveld wordt gekleurd vanuit de kleurkaart van het achtergrondstuk van het terrein, 32 m per pixel op het grootste mip-niveau dat het level levert, of, waar geen achtergrondkaart het dekt, in de middenkleur van de oppervlaktematerialen van het terrein. `--ground-texture` vermenigvuldigt dat met de kleurkaart van het terrein (op 0,5 m per pixel waar het level er een heeft) en bakt de wegen, opstelplaatsen, landingsbaanlijnen, bandensporen en markeringen erover, in de verfkleur van hun materiaal waar die is ingesteld en een neutrale kleur waar niet; variatiemaskers van wegen worden weggelaten. Het spel mengt zijn oppervlaktelagen in een shader-graph die niet gelezen wordt; de export legt de kleuren van de lagen neer op basis van hun maskers en de helling van het hoogteveld, volgens een eigen regel, en een level waarvan de maskerpagina's niet op elkaar passen, krijgt één kleur. Elke laag is het gemiddelde van zijn kleurkaart, niet zijn textuur. Zie [Frostbite](reader-frostbite.md#terrain-layers). Stukken van het hoogteveld met verschillende resoluties komen met kleine treden samen.
- **Een kleurkaart van een Battlefield 6-object wordt gekozen, niet gelezen.** Een shaderblok noemt elke textuur die het bemonstert, zonder te zeggen welke de kleur is; de keuze gebeurt op naam (zie [Frostbite](reader-frostbite.md#textures-and-materials)) en kan een trim- of detailblad voor een oppervlak kiezen. Decalbladen (`t_de_...`) verliezen van de eigen kaart van het oppervlak; een decal van een bord dat als zijn paneel werd getekend, met zijn schild een kwart gedraaid. Afstandsvelden, paletten en kanaalmaskers worden nooit als kleur gebruikt. Achtergrondgebouwen worden getekend in hun palet-kleuren; grijze kaarten krijgen de tint van het materiaal volgens een regel van de exporter zelf, omdat de namen van de parameters gehasht zijn, en een materiaal dat een grijze kaart door een masker met meerdere tinten verft, krijgt er een van die tinten.
- **Gaten in het terrein van Battlefield 6 worden niet uitgesneden.** Waar het loopbare grondoppervlak van een level onder het hoogteveld loopt, moet het spel het terrein hebben uitgesneden, en de export doet dat niet. Uitgesloten als plaats van de gaten: de laagmaskers van het terrein (geen enkele is daar geconcentreerd), zijn rooster van 67 x 67 knooppunten, een gereserveerde hoogtewaarde (geen hoogtepagina bevat 0 of 65.535), de vlaggen van de knooppunten (allemaal gelijk), en meshes of assets die de grond uitsnijden: wat daar onder het terrein staat, zijn rots- en kliffmeshes, en geen asset van het level is genoemd naar gaten, tunnels of grotten. Twee rasterbomen worden run-length gedecodeerd maar niet geplaatst, en zij vormen wat er overblijft (zie [Frostbite](reader-frostbite.md#terrain-layers)).
- **Een objectvariatie van Battlefield 6 bereikt een sectie via zijn tweelingen.** De variatie van een geplaatste kopie kiest de shaderblokken van zijn secties op sleutel; waar een mesh geen blok voor een variatie heeft, wordt de variant van een sectie van een andere mesh met een identiek standaardblok genomen (zie [Frostbite](reader-frostbite.md#textures-and-materials)). Dat is de regel van de exporter; een sectie zonder tweeling die varieert, behoudt zijn standaardlook.
- **Gelaagde Battlefield 6-materialen worden getekend als hun basis en één blad.** Een wandpaneel met letters wordt getekend als zijn pleisterwerk met het letterblad erover; de andere lagen van het materiaal (overlay-vuil via zijn masker, detail- en mosskaarten) worden niet ingemengd.
- **Het navigatiemesh is dat van de AI, niet dat van de spelers.** Het dekt wat een soldaat kan bereiken: de grond, vloeren en trappen, en
  sommige daken, maar niet elke hoge plek. De verbindingen tussen oppervlakken (sprongen, ladders, overstappen) worden weggelaten.
- **Een Battlefield 6-level bevat de laag van elke speelmodus.** Objecten die alleen in één modus geplaatst worden, kunnen overlappen met die van een andere. `--skip` laat lagen weg op naam.
- **`courses` is alleen voor Forza**, en pakt alleen bibliotheekmappen op die `... (course_...)` heten.
- **Het assenstelsel van de BeamNG-ronde wordt aangenomen** als het viewerstelsel `(x, z, -y)` dat de 3DHeat-opnemer schrijft. Ronden van een andere opnemer in het ruwe stelsel van BeamNG worden niet geplaatst.
- **`list` en `extract` nemen de archieven, niet elk formaat.** Ze openen een `.pak`, een IoStore `.utoc`, een `.vpk`, een `.minizip` en een zip. Een Unity-container wordt met `meshes` gelezen, een Frostbite-level met `level`, en een `.cdae` of `.ter` is een bestand en geen archief (`identify` noemt het). Een `.minizip` zonder zijn `ChunkContentsMiniZip<n>.txt` ernaast wordt op itemnummer weergegeven.
- **Geplaatste modellen in BeamNG gebruiken herhalende texturen als gemiddelde kleuren**, omdat de sampler van de `.glb` vastklemt en de viewer texturen in een atlas pakt.
- **In de praktijk alleen Windows.** Steam-paden onder `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames`, en een `*_win64.dll` voor Oodle. Andere platforms zijn niet getest.

## Niet geverifieerd {#unverified}

- Oudere Python-versies (de tool is gedraaid met 3.13).
- Assetto Corsa Rally met een ronde die in het spel is opgenomen. Het is alleen getest met synthetische ronden in willekeurige frames.
- glTF-viewers anders dan de 3DHeat-viewer.
- Of het assenstelsel van elk spel links- of rechtshandig is. De export behoudt het telemetriestelsel van elk spel, zodat ronden en banen hoe dan ook op elkaar liggen.
- De betekenis van `WaterBlock`'s lokale z = 0 als wateroppervlak (BeamNG).
- Frostbite-plaatsing op andere spellen dan Battlefield 6, en op Battlefield 6 na een update die de indeling van een groepslid verandert. De lezer vindt dan geen groepen en zegt dat.
- Of een Battlefield 6-export past op posities die het spel meldt. De coördinaten zijn die van het spel zelf, zoals bij de andere spellen, maar er is nog geen opname over een export gelegd.
