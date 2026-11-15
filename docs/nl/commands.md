---
title: "Commando's"
nav_order: 2
lang: "nl"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Commando's {#commands}

Elk commando draait als `python -m heat3d_gamefiles <verb> ...` vanuit de map van de
repository. De verbs staan in de volgorde waarin je ze meestal nodig hebt: wat is dit
bestand, wat zit erin, geef mij dat, en maak van een ronde een baan.

| Verb | Neemt | Doet |
|---|---|---|
| [`identify`](#identify) | elk bestand | benoemt het containerformaat door de bytes te lezen |
| [`list`](#list) | een Unreal `.pak` of IoStore `.utoc`, een Source 2 `.vpk`, een ForzaTech `.minizip`, of een zip | toont de items erin |
| [`extract`](#extract) | hetzelfde | schrijft één item naar schijf |
| [`meshes`](#meshes) | een Unity `SerializedFile` | toont en controleert de meshes |
| [`course`](#course) | een ronde | exporteert de baan rond die ronde (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | een opgeslagen rondebibliotheek | draait `course` op elke baan erin (Forza) |
| [`races`](#races) | een geïnstalleerde Forza | toont elke race die het spel definieert: wat ze toevoegt, wat ze verbergt, locaties, de stand van de export |
| [`terrain`](#terrain) | een Forza-banenmap | snijdt een gebied uit op wereldcoördinaten |
| [`levels`](#levels-and-level-frostbite) | een geïnstalleerd Frostbite-spel (Battlefield 6) | toont de levels |
| [`level`](#levels-and-level-frostbite) | de naam van een level | exporteert het level: terrein, geplaatste meshes, optioneel hun kleurkaarten (Battlefield 6) |
| [`cars`](#cars) | een geïnstalleerde Forza | elke auto op lage detail, in één bestand voor het tabblad Race-analyse van de viewer |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | een Unreal 5-spel | toont de World Partition-kaarten |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | de naam van een kaart | exporteert de kaart: landschap, HLOD-structuren, water |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | een geïnstalleerde Arma Reforger | toont de werelden |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | de naam van een wereld | exporteert de wereld: terrein in zijn kleuren, de zee, gebouwen als blokken |

**De voorbeelden lezen:** `<x>` betekent dat je het vervangt door je eigen waarde, zonder
de punthaakjes; `[...]` is optioneel; zet een pad met spaties tussen "dubbele
aanhalingstekens", bijvoorbeeld `"C:\Games\Mijn Spel"`. Nieuw hiermee? Zie
[Voordat je begint](before-you-start.md). De volledige `--help` van elk verb staat op de
[Commandoreferentie](../cli-reference.md).

Elke keer dat het programma start, kan het eerst controleren of er een nieuwere versie
is. Zie [Updates](updates.md). `HEAT3D_NO_UPDATE=1` zet die controle uit.

Bron: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Stap-voor-stap-pagina's: [Archieven inspecteren](inspecting-archives.md), [Baanexport](course-export.md),
[Hele levels](whole-levels.md), [Forza-auto's](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Afsluitcodes {#exit-codes}

| Code | Betekenis |
|---|---|
| 0 | gelukt |
| 1 | het werk is mislukt (een ronde die niet te lezen is, geen spel gevonden, niets om te exporteren, een baan in `courses` is mislukt; voor `list` en `extract`: een bestand dat geen van de archieven is die ze lezen, een bestand dat niet geopend of gelezen kan worden - een versleutelde pak zonder `--key`, een versleutelde IoStore-container - of een item dat niet in het archief staat) |
| 2 | verkeerde argumenten (argparse), een pad dat niet bestaat, een `--key` dat geen 64 hexadecimale cijfers is, of `terrain` die zowel `--box` als `--route` krijgt of geen van beide |

De fouten van `list` en `extract` staan elk op één regel op de standaardfout, niet als
een Python-traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Dit leest het bestand en zegt welke container het is. Het kijkt niet naar de
extensie (de enige uitzondering is een `.ucas`, hieronder). Het probeert de formaten in
deze volgorde en stopt bij het eerste dat past:

1. **Unreal `.pak`**: een footer met de pak-magie in de laatste 1.024 bytes. Toont de
   versie, de offset en grootte van de index, of de index versleuteld is, en de
   compressiemethoden.
2. **Unreal IoStore `.utoc`**: de IoStore-magie aan het begin. Toont de versie, het
   aantal chunks en of de container versleuteld is; voor een container die dat niet is,
   het aantal bestanden dat de map erin noemt (en onder welk mountpunt), de
   compressiemethoden, en of de bijbehorende `.ucas` ernaast staat. Een `.ucas` heeft
   geen eigen kop, dus die wordt herkend aan de `.utoc` met dezelfde naam ernaast, en
   `identify` noemt dat bestand.
3. **ForzaTech `.minizip`**: de `PGZP`-magie. Toont de versie, het aantal items en
   segmenten, en of de `ChunkContentsMiniZip<n>.txt` die de items noemt ernaast staat
   (en zo ja, of die evenveel noemt als er zijn).
4. **zip**: een lokale zip-bestandskop aan het begin. Toont het aantal items, de zes
   meest voorkomende extensies, en de levelnamen als items onder `levels/<naam>/` liggen,
   zoals in een BeamNG.drive-levelarchief.
5. **Unity**: een `UnityFS`-bundel (toont de engineversie en het aantal items) of een
   kale `SerializedFile` (toont het formaat, de engineversie, het aantal objecten en de
   zes meest voorkomende klassen).
6. **Frostbite `.toc`**: toont de soort (`plain` of `signed`), waar de boom begint, en
   óf het aantal assets (binaire sectietabel) óf het aantal superbundels (DbObject-boom).
7. **Source 2 `.vpk`**: toont de versie, het aantal items, en het eerste `.nav`-navigatiemesh
   als het archief er een heeft.
8. **BeamNG `.cdae`**: shapeversie 31 die te lezen is. Toont het aantal meshes, het aantal
   getekende detailniveaus en de eerste materialen.
9. **BeamNG `.ter`**: er is geen magie, dus alles moet kloppen - een zijde van 2 tot
   16.384, zoveel hoogtes en laagbytes in het kwadraat, dan 1 tot 255 afdrukbare
   laagnamen. Toont de versie, de grootte en de laagnamen.
10. **ForzaTech `.modelbin`**: toont de versie, het aantal chunks en de zes meest
    voorkomende chunk-tags. De inhoud van de chunks wordt hier niet gedecodeerd.

De formaten met een eigen magie (2 tot en met 4) komen vóór Unity en Frostbite, omdat
de controles daarvan het hele bestand lezen: een Forza-archief is tientallen gigabytes.

Als geen van de formaten past, staat er `not a format this tool reads` met de laatste
reden. Die reden komt van de ForzaTech-controle.

Voorbeeld (fictieve gegevens):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Optie | Standaard | Betekenis |
|---|---|---|
| `<archive>` | verplicht | een Unreal `.pak`; een IoStore `.utoc` (of de `.ucas` ernaast); een Source 2 `.vpk` (voor gesplitste VPK's, de `_dir.vpk`); een ForzaTech `.minizip`; een zip, zoals de level- en contentarchieven van BeamNG |
| `--filter TEXT` | geen | alleen paden die TEXT bevatten, hoofdletterongevoelig |
| `--limit N` | 50 | toont hoogstens N items (het totaal wordt altijd getoond) |
| `--key HEX` | geen | een AES-256-sleutel die je al hebt, 64 hexadecimale cijfers, met of zonder `0x`. Alleen een versleutelde `.pak` gebruikt die. Alles wat geen 64 hexadecimale cijfers is, wordt geweigerd voordat het archief wordt geopend (afsluitcode 2) |

Het hulpmiddel bepaalt het formaat aan de hand van de bytes: een IoStore-inhoudsopgave,
een `.minizip` en een VPK aan de handtekening waarmee ze beginnen, een zip aan zijn lokale
bestandskop, en een `.pak` aan de footer aan het eind. Een `.ucas` heeft geen kop en wordt
geopend via de `.utoc` met dezelfde naam. Een bestand dat geen van deze is, wordt
geweigerd met `<file> is not an archive list and extract read (...)`. Een bestand dat dat
wel is maar niet geopend kan worden, wordt geweigerd met de reden van de lezer: een
versleutelde pak zonder `--key`, een versleutelde IoStore-container, een pakversie die het
niet leest. In beide gevallen is het één regel en afsluitcode 1.

Elke regel toont de ongecomprimeerde grootte, de compressiemethode en het pad:

| Archief | Methode | Paden |
|---|---|---|
| `.pak` | `none`, of de naam uit de footer (`Zlib`, `Oodle`, `Gzip`...) | met het mountpunt van het archief, bijvoorbeeld `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, of de methode van de container (`Oodle`, `Zlib`...), zoals het eerste blok is opgeslagen | met het mountpunt, bijvoorbeeld `../../../<Project>/Content/...`. Een container zonder mapindex noemt geen bestanden en wordt geweigerd |
| `.vpk` | altijd `stored` | zoals in de map |
| `.minizip` | `lz4`, `deflate` of `stored` | zoals het `ChunkContentsMiniZip<n>.txt` ernaast `GeoChunk<n>.minizip` ze schrijft, zonder het voorvoegsel van de buildmachine (backslashes, zoals het spel ze schrijft). Het archief bewaart geen namen, dus zonder dat bestand zijn de items `#0`, `#1`... Een lijst waarvan het aantal regels niet gelijk is aan het aantal items wordt geweigerd: die horen niet bij elkaar |
| zip | `stored`, `deflate`, ... | zoals opgeslagen; mappen worden niet getoond |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Optie | Standaard | Betekenis |
|---|---|---|
| `<archive>` | verplicht | zoals bij `list` |
| `<entry>` | verplicht | het pad precies zoals `list` het toont (hoofdlettergevoelig); in een `.minizip` werkt ook `#<nummer>` |
| `--out FILE` | de bestandsnaam van het item (na de laatste `/` of `\`), in de huidige map | waarnaar wordt geschreven; bovenliggende mappen worden aangemaakt |
| `--key HEX` | geen | zoals bij `list` |

Het item wordt ontsleuteld (pak, met een sleutel), uitgepakt en weggeschreven. Het toont
`<bytes> bytes -> <file>`. Staat het pad niet in het archief, dan eindigt het commando met
afsluitcode 1. Dat geldt ook voor een item dat niet te lezen is (een versleuteld item zonder
sleutel, Oodle-gecomprimeerd zonder Oodle-bibliotheek), met de reden in één regel. Een
VPK-item wordt hier niet gecontroleerd op zijn CRC. De lezer heeft daarvoor een methode
`verify()` (zie [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Optie | Standaard | Betekenis |
|---|---|---|
| `<path>` | verplicht | een kale Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), geen bundel |
| `--limit N` | 25 | decodeert en toont hoogstens N meshes |

Dit toont het aantal `Mesh`-objecten, en daarna één regel per mesh: de naam (de eerste
40 tekens), het aantal vertices en driehoeken, en `ok` of `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` betekent dat de gedecodeerde vertices niet de bounding box reproduceren
die Unity voor de mesh heeft opgeslagen, binnen 2% van de grootte van de box. Dat is de
eigen controle van de parser (zie [Unity](reader-unity.md)). Een mesh die niet te lezen is,
wordt gemeld met de reden en telt mee voor de limiet. Vertexdata in een `.resS`-bestand
wordt gelezen uit de map waarin de container staat.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Dit exporteert de baan rond een ronde: de grond in een strook aan weerszijden van de
rijlijn, en wat erop staat, als één `.glb`. Het zoekt de rest zelf uit: welk spel, welke
geïnstalleerde kopie, welke baan, level of etappe, en (voor Assetto Corsa Rally) welke kant
de assen op staan. Zie [Baanexport](course-export.md).

`<lap>` kan een van de volgende zijn (details in [Rondeinvoer](lap-inputs.md)):

- een rondebestand: route-JSON, FH Companion-ronde-JSON, `heat3d-lap`-JSON, `.npz`, of `.csv` met x-, y- en z-kolommen
- een map met rondebestanden, doorzocht met submappen (een hele opgenomen baan)
- een baan**naam**, opgezocht in de FH Companion-bibliotheek op `%LOCALAPPDATA%\FHCompanion\laps`

### Opties {#course-options}

| Optie | Standaard | Spellen | Betekenis |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` in de huidige map | alle | waarnaar wordt geschreven; de naam wordt in kleine letters gezet, met reeksen andere tekens omgezet in `_` |
| `--game {forza,beamng,acrally}` | wat het rondebestand zegt, anders `forza` | alle | van welk spel de ronde is |
| `--margin M` | 80 | alle | meters grond die aan weerszijden van de rijlijn wordt bewaard |
| `--texture-size {2048,1024,512}` | 2048 | alle | grondtexturepixels per 512 m-tegel (2048 = 25 cm per pixel) |
| `--no-textures` | uit | alle | alleen vlakke kleuren: een veel kleiner bestand. Voor Forza slaat dit ook de weg/berm-splitsing over (zie hieronder) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | de grondkaarten en modeltexturen van welk seizoen |
| `--no-placed` | uit | alle | alleen terrein: geen stoepranden, vangrails, borden, gebouwen. Voor BeamNG blijft het rijoppervlak dat als mesh is gemodelleerd wel bewaard |
| `--trees` | uit | alle | plaats ook begroeiing (Forza: bomen, struiken en breekbare objecten; BeamNG: bomen; AC Rally: bomen en het geïnstantieerde bladerwerk) |
| `--detail-budget N` | automatisch | alle | een plafond op driehoeken voor alles wat geplaatst wordt; zie [Detailniveaus en het budget](detail-budget.md) |
| `--track DIR` | gezocht | Forza | de banenmap (onder `media\Tracks`, met `GeoChunk0.minizip`) als de geïnstalleerde game niet gezocht moet worden |
| `--level NAME` | uit de ronde gehaald | BeamNG, AC Rally | het level (mapnaam van BeamNG) of de etappe (kaartnaam van AC Rally), hoofdletterongevoelig |
| `--install DIR` | gezocht in Steam-bibliotheken | BeamNG, AC Rally | BeamNG: de map met `gameengine.zip`. AC Rally: de spelmap, of de `acr\Content\Paks` / `Content\Paks` daarin |

Opties die niet op een spel van toepassing zijn, worden stilzwijgend genegeerd. Zo doet
`--season` niets voor BeamNG en AC Rally, en `--track` doet niets voor hen.

### Welk spel {#which-game}

Het spel wordt bepaald door `--game`, dan door het veld `game` van een `heat3d-lap`-bestand
(of van de `# {...}`-beschrijvingsregel van een CSV), en valt anders terug op Forza. Een map
krijgt het spel dat de bestanden erin noemen, als ze er maar één noemen; een bestand dat er
geen noemt (een FH Companion-ronde, `course.json`, een CSV zonder beschrijvingsregel) telt
niet mee (zie [Rondeinvoer](lap-inputs.md)).

| Waarde | Export |
|---|---|
| begint met `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` of `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | geweigerd: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | geweigerd: "tracks ship in a protected format that is not a file-extraction target" |
| al het andere | geweigerd: "there is no course reader for <game> yet" |

Een weigering geeft ook de alternatieven aan: de baan reconstrueren uit gameplay (3DHeat
GameCapture), of de ronden analyseren zonder baan, omdat het tabblad Race-analyse van de
viewer er een weg uit tekent.

### Voorbeelden {#course-examples}

```
# Een baan uit de FH Companion-bibliotheek, op naam
python -m heat3d_gamefiles course "Example Circuit"

# Eén rondebestand, een smallere strook, een kleiner bestand
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Wintertexturen, met bomen
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Een harde grens van 500.000 geplaatste driehoeken
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Een banenmap rechtstreeks opgegeven (spel buiten Steam geïnstalleerd)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: het level noemen, naar de installatie wijzen
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, met een gewone CSV-ronde die zijn spel niet noemt
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Voorbeelduitvoer (Forza, fictieve getallen):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Elke auto van een geïnstalleerde Forza op de eigen lage detail van het spel, in één bestand
voor het tabblad Race-analyse van de viewer: het `ProxyLOD`-model dat elk autoarchief onder
`media/Cars` bevat, ongeveer 900 driehoeken, met het autonummer zoals de telemetrie het
opgeeft, zijn merk, modelaanduiding en bouwjaar uit de naam van het archief, en zijn wielen
en achterlichten. Het duurt seconden en schrijft ongeveer 5 MB. Draai het opnieuw als het
spel nieuwe auto's krijgt. Een archief zonder zo'n model (een verkeersrekwisiet) wordt
genoemd en weggelaten. Het formaat staat in
[`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

De vormen zijn in meters, de eigen maat van het spel: 1:1 met de auto. Het bestand bevat de
inhoud van het spel, dus het is bedoeld voor de machine waarop het is gemaakt, niet om rond
te sturen.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Dit draait de Forza-export `course` op elke banenmap in een opgenomen rondebibliotheek, en
schrijft per baan één `<name>.glb`. Het werkt alleen voor Forza. Het roept de Forza-export
rechtstreeks aan en leest `--game`, `--level` noch `--install`.

| Optie | Standaard | Betekenis |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | de map waarin wordt geschreven (wordt aangemaakt als die ontbreekt) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | de rondebibliotheek |
| `--only TEXT [TEXT ...]` | alle | alleen de banen waarvan de mapnaam een van deze bevat (hoofdletterongevoelig) |
| `--force` | uit | opnieuw exporteren wat al een `.glb` heeft |
| `--track DIR` | gezocht | zoals bij `course` |
| `--margin M` | 80 | zoals bij `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | zoals bij `course` |

Wat als banenmap telt: een directe submap van de bibliotheek waarvan de naam ` (course_`
bevat, zoals FH Companion ze noemt, bijvoorbeeld
`Example Circuit (course_1200_3400_to_1175_3400)`. Het deel vanaf ` (course_` wordt uit de
naam weggelaten.

Zo gedraagt een run zich:

- Een baan waarvan de `.glb` al bestaat, wordt overgeslagen (`kept`), tenzij `--force` is
  opgegeven, zodat een onderbroken run verdergaat waar hij stopte.
- Een `.glb` die door een oudere versie is geschreven, zonder de eigen laag en locaties van de
  race (zijn `asset.extras.course_format` ontbreekt of is lager dan de huidige), wordt opnieuw
  geëxporteerd, alsof `--force` alleen voor die baan was opgegeven.
- Twee banenmappen met dezelfde naam voor ` (course_` (een opnemer die een nieuwe baan naar een
  oude noemde) overschrijven elkaar niet: de map die eerst is aangemaakt houdt `<name>.glb`, de
  andere wordt geschreven als `<name>_<start>.glb`, waarbij `<start>` het beginpunt is, met
  minustekens als `m` (bijvoorbeeld `example_circuit_m120_m340.glb`).
- Een baan die mislukt (onleesbare ronden, geheugen op, geen terrein...) wordt als `FAILED`
  gemeld, en de run gaat door.
- Aan het eind toont hij een tabel met status, grootte in MB, geschatte seconden en naam, en
  daarna `<n> of <total> courses in <folder>`.
- De afsluitcode is 1 als een baan is mislukt.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Toont elke race die een geïnstalleerde Forza definieert, uit de routedefinities (zie
[Forza Horizon-banen](course-forza-horizon.md#which-race)), en controleert de exports in een
`courses`-map daartegen. Het leest het spel en de rondebibliotheek; het schrijft niets dan de
optionele tabel.

| Optie | Standaard | Betekenis |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | de map waarnaar `courses` schrijft, waarvan de bestanden worden gecontroleerd |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | de rondebibliotheek |
| `--track DIR` | gezocht | de banenmap, als die niet van het geïnstalleerde spel is |
| `--markdown FILE` | geen | schrijf de tabel ook daarheen, als Markdown |

Eén rij per race, en één per opgenomen baan die erop is gereden:

| Kolom | Betekenis |
|---|---|
| route | het route-id |
| course | de opgenomen baan die erbij hoort, indien aanwezig |
| own assets | kopieën die de race aan de vrije-rijwereld toevoegt |
| drawn | daarvan, de kopieën waarvan de baan het model meelevert |
| kinds | de toegevoegde kopieën per soort (vangrails, rekwisieten, decals, infrastructuur, ...) |
| not geometry | toeschouwermarkeringen en botssplines, geteld |
| hidden | objecten van de vrije rijwereld die de race verwijdert |
| venue | de terreinmodellen van de locatie waarbinnen de AI-lijn van de race binnen 10 m komt |
| export | `current`, `older format` (opnieuw geëxporteerd door `courses`), `not exported`, of leeg voor een race zonder opgenomen baan |

Het eindigt met een telling: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Dit is de Forza-uitsnede met alles met de hand opgegeven: je geeft de banenmap en een gebied,
geen ronde. Het is handig als het gebied dat je wilt een vak is in plaats van een rit.

| Optie | Standaard | Betekenis |
|---|---|---|
| `<path>` | verplicht | een Forza-banenmap onder `media\Tracks` (met `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | verplicht | de `.glb` om te schrijven |
| `--box X0 Z0 X1 Z1` | | het gebied, in de meters van het spel (x en z, zoals de telemetrie ze opgeeft); hoeken in willekeurige volgorde |
| `--route FILE` | | een route-JSON met `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, zoals `heat3d_capture route` en `heat3d_capture laps` die schrijven; gelezen als UTF-8, met of zonder byte-order mark |
| `--margin M` | **100** | meters die rond de grenzen van een route worden toegevoegd, en de breedte van de corridor als de route een lijn heeft |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | zoals bij `course` |

Geef precies één van `--box` en `--route`, anders is de afsluitcode 2. Met `--route` is de
uitsnede de `bounds` van de route (`min`/`max`, x en z) vergroot met de marge. Als het bestand
ook minstens 10 posities bevat, wordt de uitsnede versmald tot een corridor van `--margin`
meter rond die posities, en krijgen geplaatste modellen hun detail op basis van de afstand tot
die lijn. Met `--box` wordt het hele vak bewaard, en gaat het detail naar wat het dichtst bij
het midden van het vak staat.

Hoogte maakt nooit deel uit van de uitsnede. Een vak buiten de kaart, of in de zee, geeft
"no terrain there" (afsluitcode 1), geen fout over coördinaten.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` toont de levels die een geïnstalleerd Frostbite-spel bevat, op de naam van hun
inhoudsopgave (`levels/<level>/<level>.toc`), met hun grootte en waar ze vandaan komen: `Data`
voor het basisspel, `Update/<pack>` voor een update, en hoeveel tabellen van hoge resolutie
erbij komen. Een level dat een update meelevert, heeft een kleine tabel met chunks die ook in
het basisspel staat; de tabel met de bundels van het level is het level (zie
[Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` exporteert er één: het
hoogteveld van het terrein, elk mesh dat de statische modelgroepen van het level plaatsen, de
objecten die één voor één zijn geplaatst, waar ze staan, en het terreinachtergrond van het
level rond de kaart. Met `--textures` krijgt elk oppervlak zijn kleurkaart; met `--navmesh`
komen ook de oppervlakken waarop soldaten lopen erbij. Hoe het wordt gelezen staat in
[Frostbite](reader-frostbite.md).

| Optie | Standaard | Betekenis |
|---|---|---|
| `<level>` | verplicht | een naam zoals `levels` die toont, een unieke deel ervan, of het pad van het `.toc` van een level |
| `-o`, `--out FILE` | `<level>.glb` | de te schrijven `.glb` |
| `--install FOLDER` | de eerste Steam-game waarvan `Data` een `layout.toc` bevat | de map van het spel |
| `--textures [PIXELS]` | uit; 512 als het zonder grootte wordt gegeven | schrijf de kleurkaart van elk oppervlak, de grootste mip niet groter dan PIXELS aan een zijde, en de texturecoördinaten zoals het spel ze heeft, met een herhalende sampler (zie [Uitvoerformaat](output-format.md)). Het hoogteveld krijgt de kleurkaart van de terreinachtergrond waar die kaart het bedekt, anders de middelste kleur van de oppervlaktematerialen van het terrein, anders de gemiddelde kleur van de achtergrond eromheen. Uit, dan is elk deel een vlakke kleur |
| `--ground-texture [METRES]` | uit; 0,5 als het zonder grootte wordt gegeven | bak de terreindecals — wegen, landingsbanen, platforms, geschilderde markeringen — over de grondkleur, vermenigvuldigd met de kleurkaart van het terrein waar het level er een heeft, in de kleur van het hoogteveld, METRES per pixel, in tegels van hoogstens 4.096 pixels (`ground:terrain x<x> z<z>`). Werkt met of zonder `--textures` |
| `--navmesh` | uit | voeg het navigatiemesh van het level toe voor zijn kleinste agent, de soldaat (1,8 m hoog, 0,4 m breed), als het deel `nav:walkable`: de grond, vloeren, trappen en de daken die een soldaat kan bereiken, zonder de verbindingen (sprongen, ladders, overstappen) ertussen |
| `--ground-spacing METRES` | 4 | de fijnste afstand van het hoogteveld; knopen die fijner zijn, worden verkleind. 0 laat het hoogteveld weg |
| `--detail-budget N` | elke kopie op het grofste niveau, plus een kwart, minstens 1.500.000 | een plafond op driehoeken. De meshes die het meest kosten, zakken één detailniveau tegelijk tot het past; past het dan nog niet, dan vallen eerst de kleinste kopieën weg. De terreinachtergrond wordt nooit grover gemaakt of weggelaten |
| `--skip TEXT` | | laat statische modelgroepen weg waarvan de partitienaam TEXT bevat; herhaal het voor meer. De laag van een spelmodus, bijvoorbeeld |
| `--by-mesh` | uit | om te vinden wat een deel is: één deel per bronmesh en materiaal, genoemd `<part> \| <mesh> \| <material>`; een veel groter bestand |
| `--clamped-uvs` | uit | voor een renderer die een textuur niet kan herhalen: knip elke getextureerde driehoek in stukken waarvan de coördinaten binnen 0..1 liggen, en teken een driehoek die meer dan 4 stukken nodig heeft in de gemiddelde kleur van zijn textuur, in een deel `<part> (average colour)` |

Het toont de groepen en hoeveel kopieën elk is geplaatst, de meshes die het heeft weggelaten en
waarom, de driehoeken per deel (en met `--textures` hoeveel texturen, en hoeveel secties hun
kleurkaart vonden), wat de grond is, en met `--navmesh` hoeveel navigatietegels zijn gelezen.
Over het level wordt niets anders geschreven dan de geometrie: geen namen, geen metadata (zie
[Uitvoerformaat](output-format.md)).

Het terreinbudget staat los: het hoogteveld en de achtergrond worden nooit grover gemaakt door
`--detail-budget`; `--ground-spacing` bepaalt het hoogteveld.

Een heel level is groot: meestal meer dan tien miljoen driehoeken en enkele honderden MB.
`--textures` voegt weinig toe aan het bestand; een level vol bomen kan ongeveer 1 GB bereiken.
`--textures 256 --detail-budget 3000000 --ground-spacing 8` brengt een level tot ongeveer een
derde daarvan.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` is de map van het spel, zijn `Content/Paks`, of de naam van zijn map in een
Steam-bibliotheek (`"<Steam game folder name>"`). `ue-maps` toont elke kaart die naast zich
gebakken World Partition-cellen heeft. `ue-map` exporteert er één als `ground:<map>` (het
landschap), `structure:<map>` (de samengevoegde HLOD-meshes van de kaart) en `water:<map>` (de
waterlichamen waar ze boven de grond staan), in Unreal-**centimeters** met Y en Z omgewisseld -
de enige export die niet in meters is. Hoe elk wordt gelezen en gecontroleerd:
[Unreal 5-kaarten](level-unreal-world-partition.md).

| Optie | Standaard | Betekenis |
|---|---|---|
| `<map>` | verplicht | een naam zoals `ue-maps` die toont, of een unieke deel ervan |
| `-o`, `--out FILE` | `<map>.glb` | de te schrijven `.glb` |
| `--ground-spacing METRES` | 2 | de vertexafstand van het landschap in het bestand, afgerond op een heel aantal van zijn eigen vierkanten |
| `--no-structures`, `--no-water` | | laat dat deel weg |

Het toont de driehoeken per deel, hoeveel landschapscomponenten zijn gelezen, en hoeveel van de
vertices die ze twee keer opslaan niet overeenkomen. Een kaart van 3 km op 2 m is ongeveer 4,6
miljoen grondriehoeken.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` toont elke wereld met een terrein, op zijn map onder `worlds/`.
`enfusion-world` exporteert er één: `ground:<world>` (het terrein, in de kleuren van zijn
supertexture-tegels), `water:<world>` (de zee, op hoogte nul) en `structure:<world>` (de box van
elk geplaatst model), in de eigen meters van het spel - x oost, y omhoog, z noord. Hoe elk wordt
gelezen en gecontroleerd: [Arma Reforger-werelden](level-arma-reforger.md).

| Optie | Standaard | Betekenis |
|---|---|---|
| `<world>` | verplicht | een wereld zoals `enfusion-worlds` die toont |
| `-o`, `--out FILE` | `<world>.glb` | de te schrijven `.glb` |
| `--install FOLDER` | de Steam-bibliotheek die het spel bevat | de map van het spel |
| `--ground-spacing METRES` | 2 (dat van het terrein zelf) | de vertexafstand van het terrein in het bestand |
| `--texture-size PIXELS` | 4096 | de grootste zijde van de grondkleurafbeelding; 0 voor een vlakke kleur |
| `--no-structures` | | laat de geplaatste modellen weg |
| `--trees` | uit | plaats ook bomen en andere begroeiing, als blokken |

Het toont de driehoeken per deel, hoeveel tegelrandvertices niet overeenkomen, hoeveel entiteiten
het wereldbestand bevat en hoeveel blokken zijn geplaatst, en wat er is weggelaten en waarom.

## Omgevingsvariabelen {#environment-variables}

| Variabele | Effect |
|---|---|
| `HEAT3D_OODLE` | pad naar een `oo2core_*_win64.dll`, of een map die er een bevat; zie [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | elke waarde behalve leeg, `0`, `false`, `no` zet de updatecontrole uit; zie [Updates](updates.md) |
| `LOCALAPPDATA` | waar de FH Companion-bibliotheek, de gebruikersmap van BeamNG en de updatecache worden gezocht |
| `HEAT3D_COURSE` | alleen voor tests: de baan die de test van de geïnstalleerde-spel-stoepranden gebruikt; zie [Ontwikkeling](development.md) |
