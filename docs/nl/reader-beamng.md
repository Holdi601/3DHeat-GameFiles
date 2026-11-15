---
title: BeamNG-bestanden
nav_order: 8
lang: "nl"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG-bestanden: levelarchieven, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive levert gewone zip-archieven, dus er is geen container om te reverse-engineeren. Het werk zit in het lezen van een level **zoals het spel dat doet**: de archieven in één bestandssysteem koppelen, de scènebestanden volgen, en het terrein en de gecompileerde vormen decoderen. Deze lezers worden bereikt via de baan-export van [BeamNG.drive](course-beamng.md). `identify` herkent ook een levelzip, een `.cdae` en een `.ter`, en `list` en `extract` nemen elke zip.

Bronnen: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Het gekoppelde bestandssysteem {#the-mounted-file-system}

`Files.of_install(game)` bouwt één index, zonder onderscheid tussen hoofdletters, over
`gameengine.zip`, de `content`-zips (behalve voertuigen en geluiden), en de mods van de gebruiker (`mods\*.zip`, `mods\unpacked\*`, en een map `levels` van de gebruiker). Latere toevoegingen overschrijven eerdere, zoals in het spel. Lookups negeren hoofdletters, omdat de verwijzingen van de levels zelf niet met de archieven overeenkomen (`.DAE` voor een `.dae`). Details staan op [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` vindt een pad zoals het spel dat doet: zoals opgegeven, relatief aan het bestand dat ernaar verwees, `x.png` als `x.dds`, `x.dae` als `x.cdae` (voorkeur), en via een `x.png.link`-JSON-bestand waarvan `path` naar `/assets` wijst.

## Scènebestanden {#scene-files}

| Bron | Formaat | Gelezen |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | één JSON-object per regel, of een enkele JSON-array of -map | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | dezelfde klassen, voor oudere levels zonder `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript of JSON | kinderen geplaatst ten opzichte van de prefab, tot 8 niveaus diep |
| `levels\<name>\forest\*.forest4.json` | één instantie per regel | getypeerd door `TSForestItemData`-records in `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | de titel van het level (vertaalsleutels worden genegeerd) |

**Transformaties.** `rotationMatrix` is negen getallen waarvan de **rijen** de eigen assen van het object in de wereld zijn. Vangrailsegmenten die langs een weg zijn geketend, lopen langs rij 0 (92%), en de opwaartse rij kantelt mee met de helling van de weg. Oudere prefabs geven `rotation = "x y z degrees"`, een rechtshandige draai over die hoek (92% van de railketens sluit erop aan, 19% in de tegengestelde zin). Schaal vermenigvuldigt de rijen, en `position` (of `pos`) is de laatste rij. De transformatie van een prefabkind wordt samengesteld met die van de prefab. Het `groupPosition` van de prefab is een draaipunt uit de editor en wordt **niet** afgetrokken: een karretjesprefab staat alleen op de grond zonder het.

TorqueScript-getallen worden met een tolerant patroon gelezen, omdat sommige meegeleverde prefabs waarden schrijven zoals `-0.99563-0.0` zonder spatie.

## Terrein: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Hoogte in meters: `position.z + h * maxHeight / 65535`, met `position`, `squareSize` en `maxHeight` uit de `TerrainBlock` (standaard 0, 1 en 2048).
- Rijen lopen langs +y. Rasterpunt (i, j) staat op `(position.x + i * squareSize, position.y + j * squareSize)`.
- Laag 255 is een gat.

Gecontroleerd: wegknooppunten liggen op het terrein tot 1-2 cm (mediaan) op drie levels. `h / 32`, of de andere asvolgorde, mist met tientallen tot honderden meters.

## Materialen {#materials}

Elk `*.materials.json` buiten `levels\`, plus dat van het huidige level, geïndexeerd op `mapTo`, `name` en sleutel:

| Klasse | Gebruikte velden |
|---|---|
| `Material`, `CustomMaterial` | kleurkaart (`baseColorMap`, `colorMap` of `diffuseMap`, eerste stadium), kleurfactor, dekkingskaart en -factor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | basiskaart en `diffuseSize`, detailkaart en grootte en sterkte, macrokaart en grootte en sterkte, `groundmodelName`, `annotation` |

Afbeeldingen worden gedecodeerd met Pillow (DDS, PNG enzovoort), waar mogelijk met een verkleinde draft, en per grootte in de cache gezet. Een onleesbare textuur valt terug op een vlakke kleur.

## Gecompileerde vormen: `.cdae` {#compiled-shapes-cdae}

`.cdae` is de eigen cache van het spel van elk Collada-bestand, geschreven als MessagePack. De indeling wordt **door BeamNG gedocumenteerd** (documentation.beamng.com/modding/file_formats/cdae/), en de lezer volgt die:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Wat gelezen wordt: begrenzingen, knooppunten, objecten, `details` (detailniveaus), standaardrotaties van knooppunten (`Quat16`) en translaties, elke mesh's vertices, UV's, normalen, kleuren, primitieven en indices, en de materiaalnamen. Materiaalnamen worden aan het eind van de stroom gevonden, omdat de reeksen van een geanimeerd rekwisiet ervoor staan in een vorm die niet gedocumenteerd is.

Twee dingen die de documentatie niet uitschrijft, uitgezocht aan de hand van de `.dae`-bestanden waaruit de vormen gebouwd zijn:

- **Rotaties van knooppunten zijn die van Torque.** Een `Quat16` die op de leerboekmanier gelezen wordt, draait de verkeerde kant op. Zijn matrix moet **getransponeerd** worden. Daarmee komt elke begrenzing van elk knooppunt tot op de millimeter overeen met de Collada. Zonder dat zit het in de mediaan 38 cm ernaast.
- **Eenheden en assen zijn al toegepast.** Een Collada-bestand dat in centimeters of Y-omhoog is gemaakt, komt uit de cache in meters, Z-omhoog.

Detailniveaus zijn de `details` met een niet-negatieve grootte, grootste eerst. Negatieve groottes zijn botsings- en zichtlijnmeshes, die nooit getekend worden. Objecten met de naam `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` of `imposter` worden nooit getekend. Alleen standaard- en gesorteerde meshes worden getekend. Geskinde meshes (personages, voertuigen) en decal-meshes niet. Triangle-strips en -waaiers worden uitgerold, en vlakken worden opnieuw gedraaid om te kloppen met de opgeslagen normalen, omdat de eigen draairichting van Torque dat niet belooft.

Gecontroleerd: bijna elke meegeleverde vorm wordt gelezen. De twee andere zijn van een oudere versie.

## Terugval op Collada: `.dae` {#collada-fallback-dae}

Voor vormen zonder `.cdae` (mods, en de enkele vorm waarvan de cache ouder is), wordt het Collada-bestand gelezen zoals de importeur van Torque het leest, in dezelfde structuur:

- Detailniveaus volgens de naamgeving van Torque: het getal aan het eind van een mesh-knoopnaam is de pixelgrootte waarop hij getekend wordt (`barrier75`, `barrier40`). Een negatief getal, of een naam `collision`/`Colmesh`/`LOS`/`nulldetail`, wordt nooit getekend. Een vorm zonder die conventie heeft één niveau.
- Eenheden uit `<unit meter>`, en omzetting van Y-omhoog naar Z-omhoog.
- UV's omgedraaid naar de conventie van de cache (v loopt omlaag door de afbeelding).

Gecontroleerd tegen de `.cdae` van het spel van dezelfde bestanden: bijna alle gesamplede begrenzingen binnen 1 cm, 583 met hetzelfde aantal driehoeken, 94% van de UV's van de materialen identiek. De test op geïnstalleerde spellen eist dat 90% van maximaal 60 vormparen uit het gedeelde kunstarchief binnen 1 cm overeenkomt.

## Niet gelezen {#not-read}

- Grondbedekking (procedureel gras), en alles wat tijdens het draaien wordt gegenereerd.
- Geanimeerde reeksen en skinning.
- Voertuigen en geluiden (worden nooit gekoppeld).
