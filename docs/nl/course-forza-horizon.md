---
title: "Forza Horizon"
nav_order: 1
lang: "nl"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Baanexport: Forza Horizon {#course-export-forza-horizon}

De Forza-export leest de baan rechtstreeks uit de ForzaTech-archieven van het spel: terrein waarbij
weg, berm en gras uit elkaar worden gehouden, een grondtextuur die is ingebakken uit de eigen
grondkaarten van het spel, en elk geplaatst model in zijn eigen textuur (stoepranden, vangrails,
bandenmuren, borden, rekwisieten, gebouwen). Ook zoekt het welke van de races van het spel de ronde
is gereden, en voegt het toe wat het spel voor die race alleen neerzet (de eigen laag: vangrails,
tenten, portalen, tribunes, vlaggen), en de grond van elke locatie waar de rit doorheen gaat, zoals
de vloer van een stadion.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Bronnen: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
De containerformaten zelf staan op [ForzaTech](reader-forzatech.md).

## Het geïnstalleerde spel vinden {#finding-the-installed-game}

Niemand hoeft een pad als `D:\Games\steamapps\common\<Forza>\media\Tracks\<map>` te typen, dus het
pad wordt zelf uitgezocht:

1. **Steam-bibliotheken.** Het bestand `config\libraryfolders.vdf` van Steam wordt gelezen uit
   `C:\Program Files (x86)\Steam` of `C:\Program Files\Steam`, en elk `"path"`-item erin is een
   bibliotheek. In de `steamapps\common` van elke bibliotheek wordt gezocht.
2. **Microsoft Store.** `C:\XboxGames` wordt doorzocht als die bestaat. Daar staat het spel één
   map dieper, in `<game>\Content`.
3. Een **spelmap** is elk kind van die mappen dat een map `media\Tracks` heeft, welke naam het ook
   heeft.
4. Een **banenmap** is elke map onder `media\Tracks` die een `GeoChunk0.minizip` bevat. Die telt op
   zijn inhoud, niet op zijn naam, dus een baan onder een naam die niemand heeft gezien, wordt toch
   gevonden.

Staat het spel ergens anders, geef dan de banenmap op met `--track`; zie
[Problemen oplossen](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` slaat dit allemaal over.

Een banenmap bevat wat de export leest:

| Bestand | Wat het is |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | de archieven: elk model, elke textuur en elk plaatsingsbestand, zonder namen erin |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | één regel per archiefitem, in itemvolgorde: de enige bron van namen |
| `AssetManifest.xml` | elke textuur die de baan meelevert, met de hash waarmee materialen ernaar verwijzen |

## Welke baan {#which-track}

Een spel levert meer dan één banenmap (de open wereld, een garage of twee). De juiste wordt gekozen
op **coördinaten, niet op naam**:

- De bounding box van de ronde, vergroot met `--margin`, is de vraag.
- Voor elke banenmap worden de vier `ChunkContentsMiniZip*.txt`-manifesten als tekst gelezen, zonder
  een archief te openen. Elke terreintegelnaam (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`)
  draagt zijn positie in het raster. De tool telt hoeveel verschillende tegels binnen de box vallen.
- De baan met de meeste tegels daar wint. Heeft geen enkele baan er, dan stopt de export met
  "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres,
  as its telemetry reports them."

Een hele baan wordt in ruim een seconde gevonden. Een naamovereenkomst zou de verkeerde kaart kunnen
kiezen, en een verkeerde kaart ziet er even geloofwaardig uit als de juiste.

De console zegt `on <track>, in <game folder>`.

## Welke race {#which-race}

Het spel levert elke race als een route met een nummer, het **route-id**. Bij elke route horen twee
bestanden:

| Bestand | Wat het bevat |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | de AI-rijlijn van de race: een knoop van 56 bytes vanaf byte `0x60`, het aantal knopen op `0x24`, elke knoop begint met zijn positie (x, y, z) in de meters van het spel |
| `media\Stripped\gs\<map>\routedefinitions.zip` | één `route<id>_<map>.rtd` per race: gewone XML met wat de race aan de wereld toevoegt en wat ze eruit haalt (zie [De eigen laag van de race](#the-races-own-layer)) |

De ronde wordt aan een route gekoppeld door hem te vergelijken met elke AI-lijn waarvan de box de
box van de ronde overlapt:

- Van elk rondemonster de afstand tot het dichtstbijzijnde punt van de lijn; en van elk punt van de
  lijn de afstand tot het dichtstbijzijnde rondemonster.
- De twee medianen worden opgeteld. De route met de kleinste som wint als de som onder **30 m**
  (`MATCH`) ligt.
- Beide richtingen zijn nodig: een korte sprint ligt langs een lange route die dezelfde weg gebruikt,
  en een lange ronde bedekt een korte route.

De console zegt `the game's route <id> (driven line within <n> m of it)`, of dat geen route past. Bij
geen overeenkomst wordt alleen de wereld van de vrije rijmodus geplaatst.

## Terrein {#terrain}

Zo wordt het terrein gevonden (in `forzaterrain.py`):

- De manifesten noemen het terrein als een ruimtelijke index:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- De twee getallen zijn rastercoördinaten die **in stappen van 1023** lopen, en elke rasterstap is
  een tegel van **512 m**. Tegel `x-2046` is `-2046 / 1023 = -2`, die begint op `-2 * 512 = -1024` m.
  Als je de namen als meters leest, mist elke opzoeking met een factor twee en levert toch terrein op,
  uit het verkeerde deel van de kaart.
- Een tegel kan drie keer voorkomen: gewoon, `_cb` en `_ul`. Alle drie dekken dezelfde grond. Per
  tegel wordt er één genomen, in die volgorde van voorkeur, omdat samenvoegen de geometrie drie keer
  zou maken in samenvallende vlakken.
- Een tegel wordt alleen gelezen als hij de box van de ronde **en** de corridor raakt. Een tegel die
  de corridor niet raakt, wordt nooit gedecomprimeerd.
- Elke `.modelbin` van een gekozen tegel wordt alleen op **detailniveau 0** gedecodeerd. Een tegel
  heeft vier niveaus over dezelfde grond, en alle exporteren zou dezelfde vierkante meter vier keer in
  het bestand zetten.
- Elk mesh draagt zijn eigen schaal en bias in wereldruimte, dus een tegel komt precies waar het spel
  hem zet, zonder instantietransformatie. Driehoeken waarvan de voetafdruk de box overlapt, worden
  bewaard, daarna alleen die die de corridor bereiken.
- Een mesh in een formaat dat de lezer weigert, wordt overgeslagen en geteld
  (`N meshes could not be read`), zodat een schraal resultaat zegt waarom.

De terreinsamenvatting toont het aantal vertices, driehoeken, meshes en tegels, en de x/y/z-omvang.

### Weg, berm, terrein, markeringen, water {#road-verge-terrain-markings-water}

Materiaalnamen kunnen niet zeggen waar de weg is. Rond een circuit gebruikt 94% van de grond een
wegshader-materiaal, omdat terrein nabij een weg met die shader wordt getekend en de shader per pixel
beslist asfalt of gras. Dus:

| Soort | Bepaald door |
|---|---|
| wegstrook | de **vertexindeling**: wegstroken zijn de enige grond met een tweede UV-set (kanaal 1); een driehoek waarvan alle drie vertices die hebben, is weg |
| asfalt tegen berm | binnen een wegstrook, het asfaltmasker van de tegel op het zwaartepunt van de driehoek: 0,5 of meer is `road`, minder is `verge` |
| markeringen | materiaalnaam die `whiteline`, `yellowline` of `decal` bevat |
| bandensporen | materiaalnaam die `tyremark` of `skid` bevat (eerder gecontroleerd dan markeringen, omdat bandensporen als `tyremark_decal_*` worden geleverd) |
| water | materiaalnaam die `water`, `lake`, `river`, `paddy`, `ocean` of `sea` bevat |
| terrein | al het andere |

Gemeten op de opgenomen ronden van het testcircuit landt bijna elk monster op driehoeken van
wegstroken, en het grootste deel op het asfaltdeel zodra het masker de berm heeft afgesplitst.

Het asfaltmasker bestaat alleen als grondtexturen worden ingebakken. Met `--no-textures`, of voor een
tegel waarvan de kaarten ontbreken, blijven wegstroken heel als `road` en wordt geen berm afgesplitst.
Ontbrekende kaarten kosten detail, nooit geometrie.

### Geschilderde lagen worden opgetild {#painted-layers-are-lifted}

Rijstrooklijnen en bandensporen worden geleverd als eigen driehoeken die precies in de weg liggen. Het
spel tekent ze met een dieptebias. Getekend zoals ze zijn, vechten weg en verf om elke pixel. De export
geeft elk markerings- en bandenspoordeel een eigen kopie van zijn vertices, opgetild **5 cm**
(`DECAL_LIFT`) langs de oppervlaktenormaal, zodat de weg eronder niet mee wordt opgetild.

### Normalen {#normals}

Terreinnormalen komen uit het archief. De x van de normaal staat als het vierde short van de positie,
en y en z in het `NORMAL`-attribuut (zie [ForzaTech](reader-forzatech.md)). Heeft één vertex in de
extractie geen normaal, dan worden de normalen voor de hele grond berekend uit de driehoeken.

## De grondtextuur {#the-ground-texture}

Elke terreintegel levert drie kaarten voor zijn vierkant van 512 m, in vijf resoluties (`_quality1` tot
`_quality5`, de grootste 2048 px, dat is 25 cm per pixel):

| Kaart | Bestandsnaampatroon | Wat ze bevat (zoals gemeten) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detailnormaal (x, z). A: lager op asfalt en op ruw terrein |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | laaggewichten. B: hoog op asfalt (239 op de gereden lijn, 165 ernaast) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: laag op asfalt (147 tegen 215). B: stijgt in bosgebied |

Geen van deze is een kleurenfoto. Het zijn de invoer waarmee de terreinshader van het spel zijn
materiaallagen mengt, en die lagen worden niet gedecodeerd. De ingebakken textuur is dus **een
interpretatie, geen kopie van de look van het spel**. Ze houdt *waar* elke soort grond ligt, op 25 cm,
en schildert die in vaste kleuren:

| Grond | Lineair RGB | Gewicht |
|---|---|---|
| gras (kort, dicht bij de baan) | 0,30, 0,44, 0,18 | de basis |
| ruw (verder weg) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| bosgebied | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Beide kaarten moeten het eens zijn voor asfalt. Eén alleen laat grijze vlekken in het gras achter waar
de blokcompressie ringen maakt. Het resultaat wordt belicht door de detailnormaal van de main-kaart
tegen een vast licht (`0.55 + 0.6 * lambert`), zodat stoeprandlippen, taluds en sporen als reliëf
lezen, en geschreven als 8-bit sRGB.

Oriëntatie: pixelrij 0 is de **noord**rand van de tegel (grootste z), kolom 0 de **west**rand (kleinste
x). Dat is gevonden door gereden ronden te projecteren op het asfaltmasker in alle acht manieren waarop
een vierkant kan worden gespiegeld of gedraaid. Precies één manier zet ze op asfalt. De UV's volgen
daaruit: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

De kaarten worden gelezen op de beste resolutie tot quality 5 en teruggeschaald naar de grootte van de
main-kaart. Is de kleurafbeelding groter dan `--texture-size`, dan wordt ze verkleind met Lanczos-filter.
Het asfaltmasker blijft altijd op volle resolutie, omdat het de geometrie bepaalt. `--season` kiest de
`x<season>x`-kaarten. Een tegel zonder kaarten voor dat seizoen wordt in vlakke kleuren getekend, en de
console meldt `N without maps`.

## Geplaatste modellen {#placed-models}

Het terrein draagt zijn eigen wereldpositie. Niets anders doet dat. Waar elke kopie van een model staat,
staat in `.pgeo`-plaatsingsbestanden, één per categorie per ruimtelijke cel:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. De indeling van de records staat op
[ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Wat wordt gelezen {#what-is-read}

- Plaatsingsbestanden worden **op naam** gefilterd: de celgrootte en de celpositie in het pad geven het
  vierkant van de cel (`x * size` tot `(x + 1) * size`), en alleen cellen die de box van de ronde
  overlappen, in een gewenste categorie, worden geopend.
- Standaard categorieën: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`,
  `rocks`, `evolving`. `--trees` voegt `trees`, `bushes` en `smashables` toe. Deze worden nooit gelezen:
  `grasstemplate`, `crowdtemplate` en `cwdspline` (gras en toeschouwers: het spel tekent ze als geanimeerde
  sprites, er is geen geometrie).
- Elk bestand hoort bij een **laag**, gelezen uit zijn naam na `c<size>_<category>_`. Een detailniveau-woord
  (`do`, `so`, `ulc`, `ulp`, `cwd`) en een optioneel sectienummer is de wereld van de vrije rijmodus. Al het
  andere is een laag die het spel aanzet: een runtime-laag (`rt_0`), een activiteit (`_tag_<name>_`), een
  verzamelobject, alles wat onder `evolving` valt. Een laag die routes noemt (`rt_x<id>`, bijvoorbeeld
  `rt_x1023_x2201`) hoort alleen bij die races, en wordt alleen gelezen als de ronde op een ervan paste. Zie
  [Aangezette lagen](#switched-on-layers).
- Een kopie wordt bewaard als haar positie binnen de box en binnen de corridor ligt. Exacte herhalingen
  (dezelfde positie en oriëntatie tot de millimeter, door twee naburige cellen opgesomd) worden samengevoegd.
- **Stoepranden** zijn rekwisieten waarvan de modelnaam begint met `road_gen_rum` (rumblestrips). Ze worden
  geschreven als `ground:kerbs`, nooit vereenvoudigd en nooit weggelaten, omdat een ronde ertegen wordt
  gemeten.

| Categorie | Deel | Terugvalkleur (zonder textuur) |
|---|---|---|
| stoepranden | `ground:kerbs` | 0,60, 0,12, 0,10 |
| vangrails | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekwisieten | `structure:props` | 0,45, 0,35, 0,25 |
| borden | `structure:signs` | 0,70, 0,70, 0,70 |
| gebouwen | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastructuur | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| bruggen | `structure:bridges` | 0,45, 0,45, 0,45 |
| rotsen | `structure:rocks` | 0,30, 0,28, 0,25 |
| breekbare objecten | `structure:smashables` | 0,12, 0,22, 0,06 |
| bomen, struiken | `structure:trees` | 0,10, 0,20, 0,05 |

### De geometrie van het model {#the-model-s-geometry}

Een geplaatste naam `<model>_3D` verwijst naar de modelbestanden `<model>_cluster###.i.modelbin` (tot
ongeveer twaalf). Elke driehoek draagt een masker van de detailniveaus waartoe hij behoort:

- De detailniveaus van een model zijn de driehoeken die expliciet voor dat niveau zijn gemarkeerd. Niveaus
  lopen aaneengesloten vanaf 0, het fijnste eerst.
- Driehoeken gemarkeerd met `0xFFFF` (elk niveau) zijn de breekbare stukken, zoals de palen van een
  vangrail of de losse banden van een bandenstapel. Ze overlappen het hele model, en het spel tekent ze
  in plaats van het model zodra het uiteen is geslagen. Ze worden alleen gebruikt door een model zonder
  expliciet gemarkeerd niveau.
- Submeshes waarvan het materiaal een geprojecteerde **decal**-shader heeft, worden weggelaten.

Elke kopie wordt geplaatst met zijn positie, zijn x- en y-assen uit het record (z = x kruis y), en zijn
schaal. Normalen worden getransformeerd met de inverse schaal.

### Welke textuur {#which-texture}

Een materiaal noemt zijn texturen niet. Het geeft ze als hashes, en het `AssetManifest.xml` van de baan
koppelt elke hash (`SourceHash`) aan een texturnaam. Alleen de sectie `<Textures>` wordt gelezen, en het
lezen stopt bij `</Textures>` in een bestand dat tientallen megabytes groot kan zijn. Daarna:

1. Slot `0x88B483AA` is de basiskleur in de standaard omgevingsshader (elk bemonsterd materiaal). Bindt het
   materiaal daar een textuur, dan wordt die gebruikt.
2. Anders beslist de soort van de textuur, het woord vóór zijn GUID: `_bclr_`, dan `_diff_`, dan `_colour_`.
3. Terreinkaarten (`mainmap`, `submap`, `autogloss`) en tintpaletten (`tint`, `worldtint`) kleuren nooit een
   model.

Een model krijgt dus de kleur van wat zijn materiaal bindt, niet van een textuur met de naam van het model.
Bijvoorbeeld: `bar_rur_armco_crct_02_c` gebruikt de textuur van `..._02_a`.

De textuur wordt uit de archieven gelezen op de kleinste resolutie die minstens **256 px** breed is
(`MODEL_TEXTURE`), verkleind tot 256 als ze groter is, en opgeslagen als RGB-JPEG in de `.glb`. De kleur van
een vangrail op 256 px voor vier meter is 1,6 cm per pixel, en ongeveer tachtig van zulke texturen passen
naast de grondtegels in de atlas van de viewer.

**Seizoenen.** `--season` ruilt een textuur op naam om voor zijn seizoenstweeling, met de GUID genegeerd
(`..._xsummerx_bclr` naar `..._xwinterx_bclr`, of `..._bclr` naar `..._winter_bclr`), als de baan er een
heeft. Met `--season winter` wordt het winterlas van een submesh ook gebruikt waar zijn variantentabel dat
noemt.

**Varianten.** Een submeshrecord begint met een tabel van `(summer, winter)`-materialen, één per uiterlijk dat
een kopie kan dragen: vijf prints voor een billboard, zes verfkleuren voor een bandenstapel. Elk
plaatsingsrecord zegt welke variant die kopie draagt. Een submesh met minder varianten dan het model herhaalt
er zijn eigen.

**Het plaatsblok.** Gedeelde gebouwatlassen reserveren een effen RGB-blok (255, 64, 0) voor oppervlakken die de
gebouwshader uit andere texturen kleurt. Als meer dan een twintigste van een textuur binnen 12 niveaus van die
kleur ligt, wordt het blok overgeschilderd in de gemiddelde kleur van de textuur zelf. Anders wordt een stad
oranje.

### Doorzichtige oppervlakken {#see-through-surfaces}

Kettingvrijheden en netten zijn enkele vierhoeken met gaten in het alfakanaal van de textuur. Solide getekend
is een hek een muur dwars over het zicht op de baan. Oppervlakken waarvan de materiaalshader overeenkomt met
`alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` of `tree` worden getest:

- De ondoorzichtigheid van de textuur wordt gemiddeld over een raster van 32 x 32.
- Per oppervlak (elke uitgeknipte driehoek die één textuur deelt) worden vier punten per driehoek in UV-ruimte
  bemonsterd en gewogen naar het UV-oppervlak van de driehoek.
- Ligt de gemiddelde ondoorzichtigheid op minstens 0,05 en onder **0,5**, dan wordt het hele oppervlak
  weggelaten. Onder 0,05 betekent het alfa voor zijn shader duidelijk iets anders (een waarschuwingsbord dat
  0,01 bemonstert), en blijft het oppervlak solide.
- Een model waarvan elk oppervlak is weggelaten, wordt gemeld:
  `N models left out as see-through (mostly holes in their texture)`.

De tool beoordeelt het hele oppervlak in plaats van één driehoek tegelijk. Per driehoek beoordeeld, bleef de
helft van elke vierhoek over en kwamen hekken eruit als rijen tanden.

### Gebouwen als geheel {#buildings-drawn-whole}

Een stad bouwt zijn gebouwen uit modulaire stukken: honderdduizenden rond één stratencircuit, tientallen
miljoenen driehoeken zelfs op hun grofste niveau. Stukken één voor één weglaten liet losse wandplaten
overeind staan. Het spel levert ook stand-ins van hele gebouwen in `scene\hlod_tier_1\`, één mesh per gebouw
(stam `hlod_tier_1_*`), al in wereldcoördinaten zoals het terrein:

- De wereldbox van elke stand-in wordt gelezen uit de positiebox van zijn mesh (alleen een koplezing, geen
  decodering). Dat duurt seconden voor een hele kaart.
- Stand-ins die de box en de corridor van de ronde raken, worden gebruikt.
- Elk stuk `buildings` waarvan de positie binnen de voetafdruk van een stand-in valt (plus 0,5 m), wordt weggelaten
  en de stand-in wordt getekend. De afstand tot de rijlijn wordt gemeten tot de dichtstbijzijnde rand van het
  gebouw.
- De samenvatting zegt `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Aangezette lagen {#switched-on-layers}

Wat een aangezette laag plaatst, wordt geëxporteerd, maar los van de wereld van de vrije rijmodus, zodat de
viewer het kan tonen of verbergen:

| Laag | Deel |
|---|---|
| de wereld van de vrije rijmodus | `structure:<category>` (zoals voorheen) |
| een laag die de route van de gekoppelde race noemt | `structure:event_<category>` |
| elke andere aangezette laag | `structure:layer_<category>` |

De samenvatting telt ze: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modellen die al in wereldcoördinaten staan {#models-already-in-world-coordinates}

Een paar soorten modellen staan in geen enkel plaatsingsbestand. Hun meshes dragen hun eigen wereldpositie,
zoals het terrein, dus niets hoeft ze te plaatsen:

| Map onder `scene\models\` | Wat het is | Deel |
|---|---|---|
| `plots` | de eigen grond van een locatie: de vloer en het binnenveld van een stadion, een festivalterrein, een plein | `ground:venue` |
| `plinths` (en elk model met de naam `floor`, `ground` of `road`) | grond waarmee een straat wordt aangekleed: plantenbakken, trappen, een parkbestrating | `ground:plinths` |
| `hda_infrastructure` (bruggen) | procedureel gebouwde bruggen | `structure:bridges` |

- Een model telt als staand in wereldcoördinaten als het midden van zijn box meer dan **300 m**
  (`WORLD_REACH`) van zijn eigen oorsprong ligt. Modellen die door de plaatsingsbestanden worden geplaatst,
  liggen binnen een paar honderd meter van hun oorsprong.
- Niet getekend: occluders, kabels langs de wegen, de achtergrond van de zee, de daken en occluders van
  modulaire gebouwen (de stand-ins tekenen die gebouwen), botsings- en watervolumes.
- Elk wordt gelezen uit de box van zijn meshes (een koplezing), enkele seconden voor een hele kaart, één keer
  per run.
- Grondonderdelen worden nooit grover getekend en nooit weggelaten om in het budget te passen, net als
  stoepranden.

**Een locatie wordt als geheel gesneden.** Raakt de rit de eigen grond van een locatie (`ground:venue`), dan
wordt de corridor verbreed tot de hele voetafdruk van die grond plus `--margin`, zodat de tribunes, muren en
vangrails rond een stadion meekomen, niet alleen de strook die de ronden gebruikten. De console zegt
`through a venue (<model names>): cutting all of its ground, <n> km2`. Plinten verbreden de snede niet.

### Detail en het budget {#detail-and-the-budget}

Afstandsbanden, het budget, en welke kopieën weggaan als het budget te klein is, staan op
[Detailniveaus en het budget](detail-budget.md).

### Plaatsingssamenvatting {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## De eigen laag van de race {#the-race-s-own-layer}

Veel races zetten dingen neer die er in de vrije rijmodus niet zijn: betonnen muren en hekken die zijwegen
afsluiten, bandenstapels, tenten, een startportaal, tribunes, vlaggen, spandoeken. Elke race somt ze op in
haar routedefinitie (`route<id>_<map>.rtd` in `routedefinitions.zip`, gewone XML in een gewoon zip-archief):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Wat wordt toegevoegd.** Elke instantie wordt geplaatst zoals een kopie uit een plaatsingsbestand. De 16
  getallen van de transformatie zijn vier rijen: de x-, y- en z-assen van het model (elk geschaald) en zijn
  positie in de meters van het spel. De derde rij is het kruisproduct van de eerste twee. `Material` is de
  variant die de kopie draagt. Het deel is `structure:event_<kind>`, waarbij `<kind>` de map onder
  `scene\models\` is (barriers, props, infrastructure, signs; al het andere telt als props), en de node draagt
  de glTF-extras `{"layer": "event", "route": <id>}`.
- **Wat wordt weggehaald.** Een kopie van de vrije rijmodus die binnen **0,1 m** van de positie van een
  verborgen asset staat, wordt weggelaten. Een verborgen asset dat in de oorsprong staat, is een model in
  wereldcoördinaten; zijn instantie-GUID wordt opgezocht in het `AssetManifest.xml` van de baan (de lijst
  `<Models>`: de bron van een model, dan de GUID's van zijn kopieën) om het te benoemen.
- **Grond die de race verbergt, blijft behouden.** Een race die de grond van een locatie verbergt, legt er
  zelf een eigen oppervlak neer. Staat dat oppervlak niet bij de modellen die de baan levert, dan blijft de
  verborgen grond, als het dichtste bij wat er wordt gereden, en de samenvatting zegt dat
  (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Niet getekend, wel geteld.** Toeschouwermarkeringen (`crowd_proxies`: het spel tekent de menigte als
  sprites ervanaf) en botssplines (`.splinecol`). De console somt ze op:
  `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Routeassets waarvoor de baan geen model levert (lichtgloed, sommige borden, inhoud die het spel streamt),
  worden genoemd onder `placed names have no model in the archives`.

Alleen kopieën binnen de corridor worden geplaatst, zoals bij al het andere.

## Het bestand schrijven {#writing-the-file}

De delen worden in deze volgorde geschreven: per tegel `terrain`, `verge`, `road` (elk met de afbeelding van de
tegel), dan `water`, `tyre marks`, `markings` (vlak, de laatste twee opgetild), dan elk geplaatst deel
gesorteerd op naam. De coördinaten zijn die van het spel zelf (meters, Y omhoog). Zie
[Uitvoerformaat](output-format.md).

Het bestand zegt wat het bevat in zijn glTF-`asset.extras`:

| Veld | Betekenis |
|---|---|
| `course_format` | `2`: de eigen laag van de race, locaties en modellen in wereldcoördinaten zitten erin. [`courses`](commands.md#courses) exporteert een bestand met een lager nummer (of geen) opnieuw |
| `route` | het gekoppelde route-id, of `null` |
| `event_copies`, `event_kinds` | hoeveel kopieën van de eigen laag van de race zijn geplaatst, en hun soorten |
| `hidden` | kopieën van de vrije rijmodus die zijn weggelaten omdat de race ze verwijdert |
| `venue` | de terreinmodellen van locaties waar de rit doorheen gaat |
| `layers` | de geplaatste aangezette lagen |

## Wat het kost {#what-it-costs}

Grove ordes van grootte:

| Baan | Resultaat |
|---|---|
| een kort circuit op het platteland | enkele honderdduizenden terreindriehoeken, meer dan een miljoen geplaatste; seconden, onder 100 MB |
| een lange point-to-point-sprint | de corridor is een klein deel van de box eromheen; ongeveer een minuut, enkele honderden MB |
| een stadscircuit | duizenden vangrails, rekwisieten en borden, en hele gebouwen; met het automatische budget tot enkele honderden MB |

Een vierkante kilometer open-wereldterrein is ongeveer een miljoen driehoeken.

## Controles hierachter {#checks-behind-it}

Dit zijn metingen die zijn gedaan toen de lezer werd geschreven, zoals in de bron staat. Ze worden niet
opnieuw uitgevoerd door de tests, tenzij het spel is geïnstalleerd.

- Op het testcircuit zit de auto ongeveer zijn rijhoogte boven de geëxtraheerde grond (mediaan onder 0,2 m).
- Elke gemonsterde tegel ligt binnen het vierkant van 512 m dat zijn naam voorspelt.
- Opeenvolgende plaatsingen van vangrails liggen precies 4 m uit elkaar, en de meeste uiteinden van vangrails
  liggen binnen 5 cm van het begin van de volgende.
- Stoepranden zitten een paar centimeter boven de geëxtraheerde grond, met de voorkant omhoog, binnen 5 m van
  de rit (ook een test met het geïnstalleerde spel, zie [Ontwikkeling](development.md)).

## Niet getekend {#not-drawn}

- Bomen en struiken, tenzij `--trees`. Gras en menigten nooit (het spel tekent ze als sprites).
- Modellen van de race zelf die de baan niet levert (zie [De eigen laag van de race](#the-race-s-own-layer)).
- Geprojecteerde decalmaterialen op modellen.
- Printen van borden die over hun paneel alfa-gemengd zijn, komen ondoorzichtig uit.
- De grondkleur is een reconstructie van waar asfalt, gras en bosgebied liggen, niet de eigen terreinmaterialen van het spel.
