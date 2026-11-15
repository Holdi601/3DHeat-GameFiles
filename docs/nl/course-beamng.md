---
title: "BeamNG.drive"
nav_order: 2
lang: "nl"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Baanexport: BeamNG.drive {#course-export-beamng-drive}

De BeamNG-export leest een level zoals het spel het koppelt, en schrijft daarna hetzelfde soort
bestand als de Forza-export: grond per vierkant van 512 m met een ingebakken textuur, weg en
losse grond als eigen delen, geplaatste modellen per categorie, en water.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Bronnen: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (installatie, bestandssysteem, scène, terrein, materialen),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (de export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) en
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (vormen).
Bestandsformaten in detail: [BeamNG-bestanden](reader-beamng.md).

## Het kader van de ronde {#the-lap-s-frame}

De export `course` verwacht BeamNG-posities in het **kader van de viewer**:
`(x, z, -y)` van de Z-omhoog-wereld van BeamNG, in meters. Dat is de rotatie die de
telemetrie-opnemer van 3DHeat toepast. De export zet de ronde terug naar het kader van BeamNG
(`(x, -z, y)`), werkt daar, en schrijft alles weer uit in het kader van de viewer. Dit is een
rotatie, geen spiegeling, dus er komt niets gespiegeld uit. Een ronde die in het ruwe kader van
BeamNG is opgenomen, zou niet goed worden geplaatst. Dit is niet getest met andere opnemers.

Het spel wordt als BeamNG herkend als het `heat3d-lap`-bestand `"game": "beamng"` zegt, of als
je `--game beamng` opgeeft.

## De installatie vinden {#finding-the-install}

- `--install <folder>`: de map met `gameengine.zip` en `content`.
- Anders wordt in elke Steam-bibliotheek `steamapps\common\BeamNG.drive` gecontroleerd op die twee.
- Werkt geen van beide: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Het bestandssysteem {#the-file-system}

BeamNG levert gewone zip-archieven en koppelt ze in één bestandssysteem waarnaar levels verwijzen
(`/art/shapes/...`, `/assets/materials/...`). De export bouwt hetzelfde: één index zonder
hoofdlettergevoeligheid over

1. `gameengine.zip`,
2. elk `*.zip` onder `content`, behalve `content\vehicles\*` en archieven waarvan de naam begint
   met `art_sound` of `audio`,
3. de inhoud van de gebruiker, nieuwste indeling eerst: onder
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` en `%LOCALAPPDATA%\BeamNG.drive`, de map `current` en de
   hoogst genummerde versiemap. Uit elk daarvan: `mods\*.zip`, elke map in `mods\unpacked`, en de
   gebruikersmap zelf als die een map `levels` heeft.

Latere toevoegingen winnen, zoals in het spel, dus een mod vervangt wat hij overschrijft. Mods
worden altijd meegenomen in een baanexport.

Paden die een level noemt, worden opgelost zoals het spel ze oplost: zoals gegeven, daarna ten
opzichte van het bestand dat ze noemde, en voor elk ook als de `.dds` waarnaar een textuur is
omgezet, de `.cdae` waarnaar een `.dae` is gecompileerd, of via een `.link`-bestand dat naar
`/assets` wijst.

## Welk level {#which-level}

Zonder `--level` wordt elk level gescoord op hoeveel van de ronde erop ligt:

- Tot 500 rondemonsters, gelijkmatig verdeeld, worden gebruikt.
- Voor het `TerrainBlock` van elk level wordt de omvang van het terrein gelezen uit de eerste vijf
  bytes van zijn `.ter`-bestand, zodat een level waar de ronde nergens bij in de buurt komt niets
  kost. Liggen minstens 30% van de monsters binnen de omvang, dan worden de hoogtes gelezen. Een
  monster telt als **op** het terrein als het tussen 1 m onder en 3 m boven het terrein ligt
  (`ON_GROUND`), omdat het referentiepunt van een auto zijn carrosserie is, niet zijn banden.
- Haalt geen enkel level 50% of meer, dan worden levels ook gescoord op hun **wegen**. Sommige
  levels lopen door voorbij hun hoogtekaart (hun randen gaan verder als rotsplaten). Een monster
  ligt op een weg als het binnen de halve breedte van de weg plus 4 m (minstens 6 m) van een
  segment `DecalRoad` ligt, en tussen 2 m onder en 4 m boven het terrein.
- Het beste level wint als het minstens 30% scoort. Anders stopt de export en noemt de beste drie:
  "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

De console zegt `on <level>: 87% of the lap lies on its terrain` (of `roads`). `--level` wordt
hoofdletterongevoelig vergeleken met de namen van de levelmappen.

## Het level lezen {#reading-the-level}

Waaruit een level bestaat, elk onderdeel gecontroleerd tegen de meegeleverde levels (details in
[BeamNG-bestanden](reader-beamng.md)):

- **Scène**: `levels\<name>\main\**\*.level.json` (één JSON-object per regel, of een JSON-array), of
  een `.mis`-bestand voor oudere levels. De tool leest `TSStatic`-objecten (geplaatste modellen,
  verborgen overgeslagen), `Prefab`-objecten (tot 8 niveaus diep, TorqueScript `.prefab` of
  `.prefab.json`), `DecalRoad`-objecten (geschilderde wegen), `TerrainBlock`, `WaterPlane`,
  `WaterBlock` en `River`.
- **Bosobjecten**: `levels\<name>\forest\*.forest4.json`, getypt via de records van
  `managedItemData.json`. Vangrails, hekken en rotsen zijn even vaak bosobjecten als bomen.
- **Terrein**: het `.ter`-hoogteveld en zijn laagkaart.
- **Materialen**: elk `*.materials.json` buiten `levels\`, plus die van dit level.

## De corridor en de wegdecals {#the-corridor-and-the-road-decals}

De corridor is `--margin` meter rond de ronde in het x/y-vlak van BeamNG (zie
[Baanexport](course-export.md#the-corridor)). Een bereikcorridor van `margin + 60 m` kiest de
kandidaten.

**Wegdecals** (`DecalRoad`) vormen het grootste deel van de wegen van BeamNG: ze zijn op het
terrein geschilderd, niet gemodelleerd. Decals waarvan de omvang de bereikcorridor raakt, worden
in de tekenvolgorde van het spel genomen (aflopend `renderPriority`, dan bestandsvolgorde) en als
linten uitgelegd:

- De knopen (x, y, z, breedte) worden elke ongeveer 1 m geïnterpoleerd met een **centripetale
  Catmull-Rom-spline**. De uniforme soort maakt een lus waar knopen zich bij een haarspeldbocht
  opstapelen. Lussen van wegen worden gesloten.
- Elke rand neemt de hoogte van het terrein waar het terrein binnen 1,5 m van de eigen hoogte van
  de weg ligt, en houdt elders de hoogte van de weg aan (op een brug).
- De materiaalnaam bepaalt wat een decal schildert:

| Soort | Materiaalnaam bevat (de eerste overeenkomst wint) |
|---|---|
| bandensporen | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| overlay (cosmetisch) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| markeringen | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| los | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| weg | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| overlay | al het andere |

## De grond {#the-ground}

Het hoogteveld van het terrein binnen de corridor wordt driehoeken:

- Één vierkant per terreinvierkant waarvan het midden in de corridor ligt. Vierkanten met laag 255
  (gaten) worden overgeslagen. Elk vierkant is twee driehoeken, met de diagonaal die wisselt zoals
  het terrein van Torque dat doet.
- Hoogtes zijn `position.z + h * maxHeight / 65535`. Normalen komen uit de hoogteverschillen.
- Elk vierkant wordt ingedeeld naar zijn **laag**: de laagnaam met het grondmodel en de annotatie
  van het terreinmateriaal. Woorden voor verharding maken er `road` van,
  `grass/forest/rock/moss/leaves/cliff/stone` maken er `terrain` van, en losse woorden maken er
  `loose` van (grind en zand). Al het andere is `terrain`.
- Daarna **overschrijven wegdecals en losse decals** de vierkanten die ze bedekken, in tekenvolgorde,
  dus het laatste decal dat is geschilderd, beslist.
- De vertices worden gesplitst per vierkant van 512 m (`floor(x / 512)`, `floor(y / 512)`), zodat
  elk deel in precies één afbeelding past: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

De console toont `what the ground is made of` met het aantal driehoeken per soort.

### Gemodelleerd rijoppervlak {#modelled-driving-surface}

De circuits van BeamNG zijn even vaak modellen als terrein. Een racebaan kan één mesh zijn met de
lijnen, rubber en rumblestrips als eigen meshes erbovenop. Daarom worden geplaatste modellen in de
categorieën weg, stoepranden, berm, rekwisieten en bruggen doorzocht op rijoppervlak. Per materiaal:

| Oppervlak | Bepaald door (de eerste overeenkomst) |
|---|---|
| bandensporen | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` in de naam, het grondtype of de annotatie |
| markeringen | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` in de materiaalnaam |
| stoepranden | `rumble`, `kerb`, `curb` |
| weg | grondtype `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, of de naam bevat `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| los | grondtype `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| berm | `sidewalk` |
| (de eigen categorie van het model) | voor modellen die al als weg, stoepranden of berm zijn ingedeeld |

Van die materialen worden de **naar boven gerichte** driehoeken (normaal z boven 0,5) binnen de
corridor uit het model gehaald en worden grond. Ze worden in de ingebakken textuur van de tegel
geschilderd en als delen geschreven, zoals `ground:road 3_-2 asphalt_light`. Markeringen en
bandensporen worden alleen geschilderd. De overige driehoeken van het model blijven bij het model.
Deze modellen worden nooit vereenvoudigd of door het budget weggelaten, omdat een grove baan een
verkeerde baan is.

## De ingebakken grondtextuur {#the-baked-ground-texture}

Elk vierkant van 512 m met grond krijgt één afbeelding van `--texture-size` pixels (2048 = 25 cm per
pixel), getekend zoals het spel zijn grond tekent:

1. **Terreinlagen.** Per pixel worden de lagen van de vier omliggende terreinvierkanten bilineair
   gemengd. Elke laag krijgt de kleur zoals het spel die geeft: de **basiskaart** van het materiaal
   uitgerekt over `diffuseSize` meter (of het hele terrein), dan de **detail-** en **macrokaarten**
   als grijze overlays (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 is neutraal). Hun
   standaarden herhalen zich elke 2 m en 60 m, met sterkte 0,5 en 0,3, tenzij het materiaal anders
   zegt. Een laag zonder materiaal krijgt de vlakke kleur van zijn oppervlak. Rij 0 van de
   basiskaart is het noorden.
2. **Wegdecals** die alleen op het terrein zijn geschilderd, in tekenvolgorde, elk met zijn eigen
   textuur, dekkingskaart, tint en dekking, langs het lint. Geleverde levels gebruiken prioriteiten
   rond 12-16 voor asfaltbases, 10 voor markeringen en 4 voor rubber.
3. **Gemodelleerd rijoppervlak** van bovenaf gezien: eerst de basis, dan de overlays, elk in de
   eigen herhalende textuur van het model op één texel per bakpixel.
4. **Decals die ook over objecten heen projecteren** (`overObjects`), als laatste.

Met `--no-textures` wordt niets ingebakken: grondonderdelen krijgen vlakke kleuren, en de
gemodelleerde markeringen en bandensporen worden eigen delen die **3 cm** worden opgetild.

## Geplaatste modellen {#placed-models}

Kandidaten zijn elke `TSStatic`, elk prefabkind en elk bosobject waarvan het oorsprongspunt in de
bereikcorridor ligt. Een kandidaat wordt getekend als de wereldbox van zijn vorm de corridor raakt.

De **categorie** komt uit de eigen annotatie van het level en het pad van de vorm. De eerste regel
die past, wint:

| Categorie | Annotatie | Pad of naam bevat |
|---|---|---|
| achtergrond (wordt nooit getekend) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| stoepranden | | `kerb`, `curb`, `rumble` |
| weg | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| berm | `SIDEWALK`, `COBBLESTONE` | |
| bomen (alleen met `--trees`) | `NATURE` | tree, foliage, bush, grass, plant en vergelijkbare woorden |
| rotsen | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| vangrails | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| borden | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| bruggen | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastructuur | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| gebouwen | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekwisieten | | al het andere |

**Vormen** worden gelezen uit de gecompileerde `.cdae`, of uit de Collada-`.dae` waar geen cache
bestaat (mods). Een vorm die niet te lezen is, wordt geteld:
`N copies of M models could not be read`. Materialen met de naam of textuur `invisible`,
`collision` of `nodraw` worden nooit getekend.

**Texturen.** Modellen worden per categorie en materiaal gegroepeerd in delen met de naam
`structure:<category> <material>` (of `ground:kerbs <material>`). Een groep krijgt de kleurtextuur
van zijn materiaal op maximaal **256 px**, alleen als zijn UV's binnen 0-1 blijven (98% van de
vertices binnen -0,02 tot 1,02). De viewer pakt texturen in een atlas en kan er geen herhalen. Een
groep waarvan de textuur zich herhaalt, wordt getekend in de gemiddelde kleur van de textuur
(alfagewogen, in sRGB, maal de materiaaltint), of in de categoriekleur als er geen textuur is.

**Detail** volgt het gedeelde schema op [Detailniveaus en het budget](detail-budget.md). De
detailniveaus van BeamNG zijn de `details` van de vorm (eerst de grootste pixelgrootte). Boven het
budget gaan de verste kopieën eerst. Stoepranden en modellen die rijoppervlak dragen, worden nooit
vereenvoudigd of weggelaten.

`--no-placed` laat de structuren weg maar houdt het gemodelleerde rijoppervlak. `--trees` voegt de
categorie bomen toe.

## Water {#water}

| Bron | Getekend als |
|---|---|
| `WaterPlane` (de zee) | een vierkant van 4 m op de waterhoogte voor elke corridorcel waar geen terrein tot die hoogte reikt |
| `WaterBlock` | één vierkant, het eenheidsvierkant op lokale z = 0 in de transformatie van het blok (de schaal bepaalt dus de grootte), als het de corridor raakt; of z = 0 het oppervlak van het blok is, is niet geverifieerd |
| `River` | een lint door zijn knopen als het de corridor raakt |

Alle water is één vlak deel, `water:water`.

## Niet getekend {#not-drawn}

- Grondbedekking (procedureel gras).
- Decor langs de rand van de wereld (`backdrop` en dergelijke).
- Herhalende modeltexturen, die als gemiddelde kleur uitkomen (zie hierboven).
- Skinned meshes (voertuigen, personages) en decalmeshes binnen vormen.

## Controles hierachter {#checks-behind-it}

Zoals in de bron staat, gemeten op de meegeleverde levels:

- Wegknopen liggen op het terrein tot 1-2 cm (mediaan) op de gecontroleerde levels, met
  `h * maxHeight / 65535` en rijen langs +y. `h / 32` of de andere asvolgorde missen met tientallen
  tot honderden meters.
- Railsecties die langs een weg aan elkaar hangen, lopen langs rij 0 van `rotationMatrix` (de
  grote meerderheid).
- De knoprotatie van de `.cdae` moet worden getransponeerd. Daarmee komen de wereldboxen tot op de
  millimeter overeen met de bron-`.dae`. De leerboekmanier zit 38 cm ernaast (mediaan).
- Geëxporteerd op meerdere meegeleverde levels van elke soort, in seconden tot minuten per stuk.
