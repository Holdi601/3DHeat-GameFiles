---
title: "Baan-export: Assetto Corsa Rally"
nav_order: 3
lang: "nl"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Baan-export: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally is gebouwd op Unreal Engine 5 (5.6.1, een aangepaste build) en levert zijn inhoud in IoStore-containers. Geen daarvan is versleuteld. De export vindt de etappe en de richting van de assen uit de ronde. Hij schrijft de eigen grondtegels van de etappe, gesplitst in weg en terrein en getextureerd met de gebakken grondkleur van de etappe. De overige modellen krijgen vlakke kleuren per categorie.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Bronnen: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (installatie, etappes, plaatsing),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (de export).
De Unreal-lezers eronder staan op [Unreal 5 IoStore](reader-unreal-iostore.md),
en decompressie op [Oodle](reader-oodle.md).

**Status:** gecontroleerd op het geïnstalleerde spel, met ronden die op elke etappe in een willekeurig frame gegenereerd zijn. Elke keer vond hij de juiste etappe en het juiste frame. Een ronde die in het spel zelf is gereden, heeft hij nog niet doorlopen.

## De installatie vinden {#finding-the-install}

- `--install <map>`: de spelmap, of zijn `Content\Paks`, of elke map met `.utoc`-bestanden. De tool kijkt in `<map>`, dan in `<map>\acr\Content\Paks`, dan in `<map>\Content\Paks`.
- Anders wordt in elke Steam-bibliotheek `steamapps\common\Assetto Corsa Rally` op dezelfde manier gecontroleerd.
- Elke `.utoc` in die map wordt als één opslag geopend. Containers die niet openen, worden overgeslagen. Als er geen enkele opent: `no readable IoStore containers in ...`.

De meeste blokken zijn met Oodle gecomprimeerd, en er wordt op de pc naar een bibliotheek gezocht (elke Steam-bibliotheek wordt doorzocht). Zie [Oodle](reader-oodle.md).

Het spel wordt als AC Rally herkend wanneer het lapbestand `"game": "assetto-corsa-rally"` (of `acrally`) zegt, of wanneer je `--game acrally` meegeeft.

## Wat een etappe is {#what-a-stage-is}

Een etappe is een **World Partition**-kaart:

- `Content\Levels\<Stage>.umap` plaatst het verre terrein.
- Gegenereerde cellen onder `Content\Levels\<Stage>\_Generated_\*.umap` plaatsen al het andere.

Een level telt als etappe wanneer zijn omgevingsmap, `Content\Environments\<Stage>\`, een map `MeshesTrack` heeft. De tool kijkt niet naar de namen van de tegels, omdat een etappe ze kan noemen naar een stad in plaats van naar zijn kaart. `--level` wordt hoofdletterongevoelig vergeleken met deze kaartnamen. Een verkeerde naam geeft de lijst met etappes die er zijn.

Er is **geen landschap**. De grond bestaat uit statische meshes:

| Tegels | Pad | Worden |
|---|---|---|
| baantegels, ongeveer 175 m, in tweeën gesplitst | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` en `..._Terrain_k` | `ground:road` en `ground:terrain` (een ongesplitste baantegel, zoals een bevroren meer, is helemaal weg) |
| verre terrein, tegels van 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Plaatsingen lezen {#reading-the-placements}

Wat een mesh plaatst, is een `StaticMeshComponent`: zijn `StaticMesh`, en zijn `RelativeLocation`, `RelativeRotation` en `RelativeScale3D`, elk ten opzichte van het component waaraan het vastzit (`AttachParent`), tot aan de root van de actor, die in de wereld staat.

- De eigenschappen zijn **unversioned**: ze staan opgeslagen op hun plek in de eigenschappenlijst van de klasse, niet op naam. Ze worden gelezen met de schema's in
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (zie [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Een waarde die gelijk is aan de sjabloon van het component (zijn archetype in een Blueprint) wordt niet opgeslagen. De waarden van de sjabloon worden dus eerst gelezen, recursief, en de eigen waarden van het component overschrijven ze.
- Componenten met `bVisible = 0` of `bHiddenInGame = 1` worden overgeslagen. Dat geldt ook voor meshes waarvan het pad `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` of `_hlod` bevat.
- Rotaties gebruiken Unreals `FRotationMatrix` (pitch, yaw, roll in graden).
- Dubbelen (dezelfde mesh op dezelfde transformatie, tot op 0,1 cm) vallen weg.
- Componenten die niet gelezen kunnen worden, worden per reden geteld en gemeld, bijvoorbeeld `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Geïnstanceerde componenten** (bossen, bijna allemaal) worden alleen gelezen met `--trees`. Deze build heeft die klassen herschikt buiten wat de headers van de engine zeggen, dus hun eigenschappen worden niet gelezen. In plaats daarvan:

- komt de mesh uit de afhankelijkhedentabel van het pakket, waar elk zo'n component precies één statische mesh noemt,
- komen de instanties uit het native blok na de eigenschappen (`[1][1][128][count]`, daarna `count` 4x4 double-matrices),
- wordt het component geacht op de root van zijn actor te staan, zoals de bosactoren ze plaatsen.

Coördinaten zijn die van Unreal: centimeters, Z omhoog, X vooruit, Y rechts, een linkshandig stelsel.

## Welke etappe, en welke kant op {#which-stage-and-which-way-round}

Het assenstelsel van de telemetrie is niet gedocumenteerd, dus het wordt niet aangenomen. Het wordt bepaald:

- **Acht kandidaat-stelsels.** Unreal Z (cm) keer 0,01 wordt de hoogte (y) van de ronde. Unreal X en Y worden de x en z van de ronde, al dan niet omgewisseld, elk met een van beide tekens, alles geschaald met 0,01 naar meters.
- **Een raster met wegshoogtes.** Voor elke etappe wordt elke wegtegel geplaatst (op zijn grofste detailniveau), en per cel van 2 m wordt de hoogste wegvertex bewaard.
- **Scoren.** Tot 400 rondepunten, gelijkmatig verdeeld, worden via elk stelsel naar de Unreal-ruimte omgezet. Een punt ligt op de weg wanneer de wegshoogte die het dichtst bij het punt ligt, in de 3 x 3 cellen eromheen, tussen 1 m onder en 3 m boven het punt ligt (`ON_ROAD`). De score is het aandeel punten op de weg.
- **Winnaar.** Het beste stelsel op de beste etappe, mits het minstens 50% haalt. Anders stopt de export met de melding: `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.`
- **Een ronde die zijn baan noemt.** Heeft het lapbestand een veld `track`, dan wordt eerst alleen de etappe geprobeerd waarvan de naam losjes past (alleen letters en cijfers, het ene bevat het andere). Die wordt alleen geaccepteerd bij minstens 80%. Anders worden alle etappes geprobeerd.
- Met `--level` wordt alleen die etappe geprobeerd, in alle acht stelsels.

De console zegt bijvoorbeeld: `on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Daarna wordt alles **in het stelsel van de ronde** geschreven: meters, Y omhoog. De draairichting van een driehoek wordt omgedraaid waar een transformatie spiegelt, zodat de vlakken nog steeds de goede kant op wijzen.

## De grond {#the-ground}

- De corridor is `--margin` meter rond de ronde, in zijn eigen x/z-vlak.
- Elke grondtegel wordt op zijn fijnste detailniveau geplaatst, en alleen driehoeken die de corridor raken, blijven over.
- Driehoeken worden gegroepeerd per soort (weg of terrein) en per vierkant van 512 m in Unreal-ruimte (51.200 cm), elk vierkant met zijn eigen afbeelding. Delen krijgen namen als `ground:road 1_-4`. UV's zijn `(unreal_xy - square_origin) / 51200`.
- Normalen worden voor het hele bestand uit de driehoeken berekend.

### De grondtextuur {#the-ground-texture}

Tenzij `--no-textures` is opgegeven, wordt elk vierkant beschilderd vanuit twee bronnen, op `--texture-size` pixels:

1. **De gebakken grondkleur.** De `RuntimeVirtualTextureComponent` van de kaart van de etappe (zijn box is `RelativeLocation` als hoek en `RelativeScale3D` als grootte, zonder rotatie) wijst naar een streaming **virtual texture**: de grondkleur die het spel heeft gebakken. Het gebied van het vierkant wordt eruit gelezen, op het niveau waarvan de pixels het dichtst bij de gewenste grootte liggen. Dat is 13 tot 59 cm per pixel, afhankelijk van de etappe.
2. **De satellietafbeelding** vult wat de virtual texture zwart laat. Het is de textuur `sat*_(b|bc|c|basecolor)` van de etappe in zijn omgevingsmap, gelezen op maximaal 4096 px. Zijn plaatsing wordt gevonden met een kleinste-kwadratenfit van het eerste UV-kanaal van het verre terrein tegen de wereld-x en -y. De fit moet lineair zijn tot binnen 0,01 op het 95e percentiel, anders wordt de afbeelding niet gebruikt. Lopen de UV's van het verre terrein voorbij 1 (een materiaal dat ze herhaalt), dan wordt de afbeelding eenmaal gehalveerd, tot ze passen.

De console zegt welke bron is gebruikt, bijvoorbeeld `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. Een etappe met geen van beide wordt in vlakke kleuren getekend.

## Geplaatste modellen {#placed-models}

Elke plaatsing die geen grondtegel is, wordt ingedeeld op zijn meshpad (de eerste overeenkomst wint):

| Categorie | Mesh-naam (of pad, voor bomen) bevat |
|---|---|
| bomen (alleen met `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| rotsen | `rock`, `cliff`, `boulder`, `stone` |
| kantstenen | `kerb`, `curb` |
| barrières | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| borden | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| gebouwen | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastructuur | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekwisieten | alles wat overblijft |

- Een kopie telt mee wanneer zijn oorsprong in de bereikcorridor ligt (`margin + 60 m`), en wordt getekend wanneer zijn begrenzing de corridor raakt.
- Detailniveaus volgen [Detailniveaus en het budget](detail-budget.md): eerst afstandsbanden, daarna stappen de duurste modellen omlaag om in het driehoeksbudget te passen. Waar zelfs de grofste niveaus het budget overschrijden, worden de verste kopieën weggelaten, zoals bij BeamNG, tot het past. Kantstenen houden volledig detail en worden nooit weggelaten. De samenvatting drukt `placed on it (N triangles of a B budget)` af en, als er kopieën zijn weggelaten, `N copies left out to fit the budget, the furthest from the driving first`.
- Elke categorie is één deel in een vlakke kleur: `ground:kerbs` voor kantstenen, die rijoppervlak zijn, zoals bij Forza en BeamNG, en `structure:<categorie>` voor de rest:

| Categorie | Kleur (lineaire RGB) |
|---|---|
| barrières | 0.55, 0.52, 0.48 |
| borden | 0.75, 0.72, 0.65 |
| gebouwen | 0.62, 0.58, 0.52 |
| infrastructuur | 0.48, 0.48, 0.50 |
| rotsen | 0.45, 0.43, 0.40 |
| rekwisieten | 0.55, 0.45, 0.35 |
| bomen | 0.20, 0.32, 0.14 |
| kantstenen | 0.70, 0.25, 0.22 |

Statische meshes die niet gelezen kunnen worden (skeletmeshes, meshes die alleen Nanite zijn, niveaus die niet inline zijn opgeslagen), worden geteld: `N meshes could not be read`.

## Gecontroleerd {#checks-behind-it}

Zoals de broncode het zegt, op het geïnstalleerde spel:

- Elke inhoudsopgave leest (versie 8).
- Elke cel van elke etappe opent, en elk statisch-mesh- en scènecomponent decodeert precies tot aan de native staart van zijn klasse.
- Bijna elke gesamplede statische mesh decodeert (de rest zijn skeletmeshes). De omvang van een wegtegel na decoderen komt overeen met de begrenzing die hij opslaat.
- De mip-niveaus van een satellietafbeelding hebben precies de groottes van hun bulk-items.
- De tegels van een virtual texture-chunk kloppen tot op de byte, en de wegtegels vallen op de weg die die toont.

## Bekende lacunes {#known-gaps}

- De eigen eigenschappen van geïnstanceerde componenten worden niet gelezen (zie hierboven). Hun plaatsing gaat uit van de actorroot.
- Bossen die tijdens het spelen door PCG worden gegenereerd, staan niet in de bestanden en kunnen niet worden geëxporteerd.
- Spline-meshes (onzichtbare respawnmuren), decalcomponenten en de eigen texturen van geplaatste modellen worden niet getekend. Modellen krijgen vlakke kleuren.
- `--season` heeft geen effect.
- Een patch van het spel kan de plekken van eigenschappen verschuiven. De lezer geeft dan een fout in plaats van verkeerd te lezen, en de export meldt hoeveel componenten zijn mislukt.
