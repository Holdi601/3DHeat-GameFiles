---
title: "Kommandoer"
nav_order: 2
lang: "da"
source: commands.md
source_hash: "db876ce4e110"
nav_exclude: true
search_exclude: true
---
# Kommandoer {#commands}

Hver kommando kører som `python -m heat3d_gamefiles <verb> ...` fra mappen med repositoryet. Verberne står i den rækkefølge, du typisk har brug for dem: hvad er denne fil, hvad ligger inde i den, giv mig den, og lav en omgang om til en bane.

| Verbum | Tager | Gør |
|---|---|---|
| [`identify`](#identify) | en vilkårlig fil | navngiver containerformatet ved at læse filens bytes |
| [`list`](#list) | en Unreal `.pak` eller IoStore `.utoc`, en Source 2 `.vpk`, en ForzaTech `.minizip` eller en zip | lister dens poster |
| [`extract`](#extract) | det samme | skriver én post ud til disken |
| [`meshes`](#meshes) | en Unity `SerializedFile` | lister og kontrollerer dens meshes |
| [`course`](#course) | en omgang | eksporterer banen omkring den (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | et bibliotek med optagede omgange | kører `course` på hver bane i det (Forza) |
| [`races`](#races) | et installeret Forza | lister alle løb spillet definerer: hvad det tilføjer, hvad det skjuler, steder og status for eksporten |
| [`terrain`](#terrain) | en Forza-banemappe | skærer et område ud efter verdenskoordinater |
| [`levels`](#levels-and-level-frostbite) | et installeret Frostbite-spil (Battlefield 6) | lister dets baner |
| [`level`](#levels-and-level-frostbite) | en banes navn | eksporterer banen: terræn, placerede meshes og eventuelt deres farvekort (Battlefield 6) |
| [`cars`](#cars) | et installeret Forza | alle biler i lav detaljegrad, i én fil til viewerens løbsfane |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | et Unreal 5-spil | lister dets World Partition-kort |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | et kortnavn | eksporterer kortet: landskab, HLOD-strukturer, vand |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | et installeret Arma Reforger | lister dets verdener |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | en verdens navn | eksporterer verdenen: terræn i dens farver, havet, bygninger som kasser |

**Sådan læses eksemplerne:** `<x>` betyder, at du erstatter det med din egen værdi, uden vinkelparenteserne; `[...]` er valgfri; en sti med mellemrum skal stå i "dobbelte anførselstegn", for eksempel `"C:\Games\My Game"`. Er det nyt for dig? Se [Før du går i gang](before-you-start.md). Den fulde `--help` for hvert verbum findes på [Kommandoreferencen](../cli-reference.md).

Hver gang programmet starter, kan det først tjekke for en nyere udgave. Se [Opdateringer](updates.md). `HEAT3D_NO_UPDATE=1` slår den kontrol fra.

Kilde: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Trin-for-trin-sider: [Undersøg arkiver](inspecting-archives.md), [Eksport af baner](course-export.md),
[Hele baner](whole-levels.md), [Forza-biler](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Afslutningskoder {#exit-codes}

| Kode | Betydning |
|---|---|
| 0 | lykkedes |
| 1 | arbejdet mislykkedes (en omgang der ikke kan læses, intet spil fundet, intet at eksportere, en bane i `courses` fejlede; for `list` og `extract`: en fil der ikke er nogen af de arkiver de læser, en fil der ikke kan åbnes eller læses - en krypteret pak uden `--key`, en krypteret IoStore-container - eller en post der ikke findes i arkivet) |
| 2 | ugyldige argumenter (argparse), en sti der ikke findes, en `--key` der ikke er 64 hex-cifre, eller `terrain` givet både `--box` og `--route` eller ingen af dem |

Fejlene i `list` og `extract` vises hver som én linje på standardfejl, ikke som en Python-traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Den læser filen og siger, hvilken container det er. Den går ikke efter filendelsen (undtagen en `.ucas`, se nedenfor). Den prøver formaterne i denne rækkefølge og stopper ved det første, der kan læses:

1. **Unreal `.pak`**: en footer med pak-magien i de sidste 1.024 bytes. Udskriver versionen, indeksets forskydning og størrelse, om indekset er krypteret, og komprimeringsmetoderne.
2. **Unreal IoStore `.utoc`**: IoStore-magien i starten. Udskriver versionen, antallet af chunks og om containeren er krypteret; for en der ikke er det, antallet af filer dens mappe nævner (og under hvilket mount point), komprimeringsmetoderne, og om dens `.ucas` ligger ved siden af. En `.ucas` har ingen egen header, så den genkendes på `.utoc`-filen med samme navn ved siden af den, og `identify` nævner den fil.
3. **ForzaTech `.minizip`**: `PGZP`-magien. Udskriver versionen, antallet af poster og segmenter, og om `ChunkContentsMiniZip<n>.txt`, der navngiver posterne, ligger ved siden af (og hvis den gør, om den nævner lige så mange, som der er).
4. **zip**: en zip-lokal filheader i starten. Udskriver antallet af poster, de seks mest almindelige filendelser, og banenavnene når posterne ligger under `levels/<name>/`, som i et BeamNG.drive-banearkiv.
5. **Unity**: en `UnityFS`-bundle (udskriver motorversionen og antallet af poster) eller en nøgen `SerializedFile` (udskriver formatet, motorversionen, antallet af objekter og de seks mest almindelige klasser).
6. **Frostbite `.toc`**: udskriver typen (`plain` eller `signed`), hvor træet begynder, og enten antallet af assets (binær sektionstabel) eller antallet af superbundles (DbObject-træ).
7. **Source 2 `.vpk`**: udskriver versionen, antallet af poster og den første `.nav`-navigationsmesh, hvis arkivet har en.
8. **BeamNG `.cdae`**: shape-version 31, der kan læses. Udskriver antallet af meshes, antallet af tegnede detaljeniveauer og de første materialer.
9. **BeamNG `.ter`**: der er ingen magi, så alt skal gå op - en side på 2 til 16.384, så mange højder og lagbytes i kvadrat, derefter 1 til 255 udskrivbare lagnavne. Udskriver versionen, størrelsen og lagnavnene.
10. **ForzaTech `.modelbin`**: udskriver versionen, antallet af chunks og de seks mest almindelige chunk-tags. Chunk-indholdet afkodes ikke her.

Formaterne med en egen magi (2 til 4) kommer før Unity og Frostbite, hvis checks læser hele filen: et Forza-arkiv er titusinder af gigabytes.

Hvis ingen af dem passer, udskrives `not a format this tool reads` og den sidste grund. Den grund kommer fra ForzaTech-checket.

Eksempel (syntetisk):

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

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<archive>` | påkrævet | en Unreal `.pak`; en IoStore `.utoc` (eller `.ucas` ved siden af den); en Source 2 `.vpk` (for delte VPK'er er det `_dir.vpk`); en ForzaTech `.minizip`; en zip, som BeamNGs bane- og indholdsarkiver |
| `--filter TEXT` | ingen | kun stier der indeholder TEXT, uden forskel på store og små bogstaver |
| `--limit N` | 50 | udskriv højst N poster (det samlede antal udskrives altid) |
| `--key HEX` | ingen | en AES-256-nøgle du allerede har, 64 hex-cifre, med eller uden `0x`. Kun en krypteret `.pak` bruger den. Alt der ikke er 64 hex-cifre afvises, før arkivet åbnes (afslutningskode 2) |

Værktøjet afgør formatet ud fra bytene: en IoStore-indholdsfortegnelse, en `.minizip` og en VPK ud fra signaturen de starter med, en zip ud fra dens lokale filheader, og en `.pak` ud fra footeren til sidst. En `.ucas` har ingen header og åbnes gennem `.utoc` med samme navn. En fil der ikke er nogen af disse, afvises med `<file> is not an archive list and extract read (...)`. En fil der er et af dem, men ikke kan åbnes, afvises med læserens grund: en krypteret pak uden `--key`, en krypteret IoStore-container, en pak-version den ikke læser. Uanset hvad er det én linje og afslutningskode 1.

Hver linje viser den ukomprimerede størrelse, komprimeringsmetoden og stien:

| Arkiv | Metode | Stier |
|---|---|---|
| `.pak` | `none`, eller navnet fra footeren (`Zlib`, `Oodle`, `Gzip` ...) | med arkivets mount point, for eksempel `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, eller containerens metode (`Oodle`, `Zlib` ...), som den er gemt i sin første blok | med mount point, for eksempel `../../../<Project>/Content/...`. En container uden mappeindeks nævner ingen filer og afvises |
| `.vpk` | altid `stored` | som i mappen |
| `.minizip` | `lz4`, `deflate` eller `stored` | som `ChunkContentsMiniZip<n>.txt` ved siden af `GeoChunk<n>.minizip` skriver dem, med byggemaskinens præfiks fjernet (backslashes, som spillet skriver dem). Arkivet gemmer ingen navne, så uden den fil er posterne `#0`, `#1` ... En liste hvis antal linjer ikke passer med antallet af poster, afvises: de hører ikke sammen |
| zip | `stored`, `deflate` ... | som gemt; mapper vises ikke |

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

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<archive>` | påkrævet | som for `list` |
| `<entry>` | påkrævet | stien præcis som `list` udskriver den (der skelnes mellem store og små bogstaver); i en `.minizip` virker `#<nummer>` også |
| `--out FILE` | indgangens filnavn (efter sidste `/` eller `\`), i den aktuelle mappe | hvor den skrives; overordnede mapper oprettes |
| `--key HEX` | ingen | som for `list` |

Posten dekrypteres (pak, med en nøgle), dekomprimeres og skrives ud. Den udskriver `<bytes> bytes -> <file>`. Hvis stien ikke findes i arkivet, afsluttes kommandoen med kode 1. Det samme sker, hvis en post ikke kan læses (en krypteret post uden nøgle, en Oodle-komprimeret post uden Oodle-biblioteket), med grunden på én linje. En VPK-post kontrolleres ikke mod sin CRC her. Læseren har en metode `verify()` til det (se [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<path>` | påkrævet | en nøgen Unity `SerializedFile` (`sharedassets0.assets`, `level0` ...), ikke en bundle |
| `--limit N` | 25 | afkod og udskriv højst N meshes |

Den udskriver antallet af `Mesh`-objekter og derefter én linje pr. mesh: navnet (de første 40 tegn), antallet af vertices og trekanter, og `ok` eller `BOUNDS DISAGREE`. `BOUNDS DISAGREE` betyder, at de afkodede vertices ikke giver den bounding box, Unity har gemt for meshen, inden for 2 % af boksens størrelse. Det er parserens egen kontrol (se [Unity](reader-unity.md)). En mesh der ikke kan læses, vises med grunden og tæller med i grænsen. Vertexdata i en `.resS`-fil læses fra mappen containeren ligger i.

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

Den eksporterer banen omkring en omgang: jorden i et bånd på hver side af kørslen og det, der står på den, som én `.glb`. Resten finder den selv: hvilket spil, hvilken installeret kopi, hvilken bane, bane eller etape, og (for Assetto Corsa Rally) hvordan akserne er vendt. Se [Eksport af baner](course-export.md).

`<lap>` kan være et af følgende (detaljer i [Omgangsinput](lap-inputs.md)):

- en omgangsfil: route-JSON, FH Companion-omgangs-JSON, `heat3d-lap`-JSON, `.npz`, eller `.csv` med kolonnerne x, y, z
- en mappe med omgangsfiler, søgt rekursivt (et helt optaget banespor)
- et banenavn **(course name)**, slået op i FH Companion-biblioteket i `%LOCALAPPDATA%\FHCompanion\laps`

### Valgmuligheder {#options}

| Valgmulighed | Standard | Spil | Betydning |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` i den aktuelle mappe, eller i `$HEAT3D_LEVELS/<game>/courses/` når den er sat | alle | hvor den skrives; navnet skrives med små bogstaver, og rækker af andre tegn erstattes med `_` |
| `--game {forza,beamng,acrally}` | det omgangsfilen siger, ellers `forza` | alle | hvilket spil omgangen er fra |
| `--margin M` | 80 | alle | meter jord der bevares på hver side af kørslen |
| `--texture-size {2048,1024,512}` | 2048 | alle | jordteksturpixels pr. 512 m-flise (2048 = 25 cm pr. pixel) |
| `--no-textures` | fra | alle | kun flade farver: en langt mindre fil. For Forza springer det også over opdelingen i vej og kant (se nedenfor) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | hvilken sæsons jordkort og modeltekstureer |
| `--no-placed` | fra | alle | kun terræn: ingen kantsten, rækværk, skilte, bygninger. For BeamNG bevares kørefladerne, der er modelleret som meshes, stadig |
| `--trees` | fra | alle | placerer også vegetation (Forza: træer, buske og knusbare ting; BeamNG: træer; AC Rally: træer og den instanserede bevoksning) |
| `--detail-budget N` | automatisk | alle | et loft for trekanter for alt der placeres; se [Detaljeniveauer og budgettet](detail-budget.md) |
| `--track DIR` | søges | Forza | banemappen (under `media\Tracks`, med `GeoChunk0.minizip`), hvis det installerede spil ikke skal søges |
| `--level NAME` | findes ud fra omgangen | BeamNG, AC Rally | banen (BeamNG-mappenavnet) eller etapen (AC Rally-kortnavnet), uden forskel på store og små bogstaver |
| `--install DIR` | søges i Steam-biblioteker | BeamNG, AC Rally | BeamNG: mappen med `gameengine.zip`. AC Rally: spilmappen, eller dens `acr\Content\Paks` / `Content\Paks` |

Valgmuligheder der ikke gælder for et spil, ignoreres uden advarsel. For eksempel gør `--season` ingenting for BeamNG og AC Rally, og `--track` gør heller ingenting for dem.

### Hvilket spil {#which-game}

Spillet tages fra `--game`, derefter fra feltet `game` i en `heat3d-lap`-fil (eller i en CSV's `# {...}`-beskrivelseslinje), og er ellers Forza. En mappe får det spil dens filer nævner, når de kun nævner ét; en fil der ikke nævner noget (en FH Companion-omgang, `course.json`, en CSV uden beskrivelseslinje) tæller ikke med (se [Omgangsinput](lap-inputs.md)).

| Værdi | Eksport |
|---|---|
| begynder med `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` eller `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | afvist: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | afvist: "tracks ship in a protected format that is not a file-extraction target" |
| alt andet | afvist: "there is no course reader for <game> yet" |

En afvisning nævner også alternativerne: rekonstruer banen ud fra spilning (3DHeat GameCapture), eller analysér omgangene uden en bane, fordi viewerens fane Løbsanalyse tegner en vej ud fra dem.

### Eksempler {#examples}

```
# En bane fra FH Companion-biblioteket, med navn
python -m heat3d_gamefiles course "Example Circuit"

# Én omgangsfil, et smallere bånd, en mindre fil
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Vinterteksturer, med træer
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Et hårdt loft på 500.000 placerede trekanter
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# En banemappe givet direkte (spillet installeret uden for Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: navngiv banen, peg på installationen
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, med en almindelig CSV-omgang der ikke siger hvilket spil
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Eksempel på output (Forza, syntetiske tal):

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

Hver bil i et installeret Forza i spillets egen lave detaljegrad, i én fil til viewerens løbsfane: `ProxyLOD`-modellen, som hvert bilarkiv under `media/Cars` har, omkring 900 trekanter, med bilens nummer som telemetrien angiver det, dens mærke, modelmærke og årgang fra arkivets navn, og dens hjul og baglygter. Det tager få sekunder og skriver omkring 5 MB. Kør den igen, når spillet får nye biler. Et arkiv uden en sådan model (en trafikprop) nævnes og udelades. Formatet findes i [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Formerne er i meter, spillets egne: 1:1 med bilen. Filen indeholder spillets indhold, så den er til den maskine den blev lavet på, ikke til at sende rundt.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Den kører Forza-eksporten `course` på hver banemappe i et optaget omgangsbibliotek og skriver én `<name>.glb` for hver. Den er kun til Forza. Den kalder Forza-eksporten direkte og læser ikke `--game`, `--level` eller `--install`.

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `-o`, `--out FOLDER` | `courses`, eller `$HEAT3D_LEVELS/forza/courses` når den er sat | mappen der skrives til (oprettes hvis den mangler) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | omgangsbiblioteket |
| `--only TEXT [TEXT ...]` | alle | kun de baner, hvis mappenavne indeholder mindst én af disse (uden forskel på store og små bogstaver) |
| `--force` | fra | eksportér igen det der allerede har en `.glb` |
| `--track DIR` | søges | som for `course` |
| `--margin M` | 80 | som for `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | som for `course` |

Hvad der tæller som en banemappe: en direkte undermappe i biblioteket, hvis navn indeholder ` (course_`, sådan som FH Companion navngiver dem, for eksempel `Example Circuit (course_1200_3400_to_1175_3400)`. Delen fra ` (course_` og frem fjernes fra navnet.

Sådan opfører en kørsel sig:

- En bane, hvis `.glb` allerede findes, springes over (`kept`), medmindre `--force` er givet, så en afbrudt kørsel fortsætter, hvor den stoppede.
- En `.glb` skrevet af en ældre version, uden løbets eget lag og venues (dens `asset.extras.course_format` mangler eller er lavere end den nuværende), eksporteres igen, som om `--force` var givet for den alene.
- To banemappe med samme navn før ` (course_` (en optager der har navngivet en ny bane efter en gammel) overskriver ikke hinanden: mappen der blev oprettet først beholder `<name>.glb`, den anden skrives som `<name>_<start>.glb`, hvor `<start>` er hvor den starter, med minustegn som `m` (for eksempel `example_circuit_m120_m340.glb`).
- En bane der fejler (omgange der ikke kan læses, løbet tør for hukommelse, intet terræn ...) rapporteres som `FAILED`, og kørslen fortsætter.
- Til sidst udskrives en tabel med status, størrelse i MB, sekunder brugt og navn, og derefter `<n> of <total> courses in <folder>`.
- Afslutningskoden er 1, hvis en bane fejlede.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Lister alle løb et installeret Forza definerer, ud fra dets rutedefinitioner (se [Forza Horizon-baner](course-forza-horizon.md#which-race)), og kontrollerer eksporterne i en `courses`-mappe mod dem. Den læser spillet og omgangsbiblioteket; den skriver intet andet end den valgfri tabel.

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `-o`, `--out FOLDER` | som for `courses` | mappen `courses` skriver til, hvis filer kontrolleres |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | omgangsbiblioteket |
| `--track DIR` | søges | banemappen, hvis den ikke er det installerede spils |
| `--markdown FILE` | ingen | skriv også tabellen dertil, som Markdown |

Én række pr. løb, og én pr. optaget bane kørt på det:

| Kolonne | Betydning |
|---|---|
| route | rute-id'et |
| course | den optagede bane der er matchet til det, hvis nogen |
| own assets | kopier løbet tilføjer til den frie verden |
| drawn | af dem, de kopier hvis model banen leverer |
| kinds | de tilføjede kopier efter type (barrierer, rekvisitter, dekaler, infrastruktur ...) |
| not geometry | tilskuermarkører og kollisionssplines, talt op |
| hidden | objekter i den frie verden som løbet fjerner |
| venue | de venue-jordmodeller løbets AI-linje passerer inden for 10 m af |
| export | `current`, `older format` (eksporteret igen af `courses`), `not exported`, eller tom for et løb uden optaget bane |

Den slutter med en optælling: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Det er Forza-udskæringen med alt skrevet ud i hånden: du giver banemappen og et område, ikke en omgang. Det er nyttigt, når det område du vil have, er en boks og ikke en kørsel.

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<path>` | påkrævet | en Forza-banemappe under `media\Tracks` (med `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | påkrævet | `.glb`-filen der skrives |
| `--box X0 Z0 X1 Z1` | | området, i spillets meter (x og z, som telemetrien angiver dem); hjørnerne i vilkårlig rækkefølge |
| `--route FILE` | | en route-JSON med `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, som `heat3d_capture route` og `heat3d_capture laps` skriver den; læses som UTF-8, med eller uden byte-order-mark |
| `--margin M` | **100** | meter lagt til omkring en rutes bounds, og korridorens bredde når ruten har en linje |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | som for `course` |

Giv præcis én af `--box` og `--route`, ellers er afslutningskoden 2. Med `--route` er udskæringen rutens `bounds` (`min`/`max`, x og z) udvidet med marginen. Indeholder filen også mindst 10 positioner, indsnævres udskæringen til en korridor på `--margin` meter omkring dem, og placerede modeller får deres detaljeniveau efter afstand til linjen. Med `--box` bevares hele boksen, og detaljen går til det der står tættest på boksens midte.

Højden indgår aldrig i udskæringen. En boks uden for kortet, eller i havet, giver "no terrain there" (afslutningskode 1), ikke en fejl om koordinater.

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

`levels` lister de baner et installeret Frostbite-spil indeholder, efter navnet på deres tabel (`levels/<level>/<level>.toc`), med størrelse og hvor de kommer fra: `Data` for basisspillet, `Update/<pack>` for en opdatering, og hvor mange tabeller i høj opløsning der tilføjer til den. En bane en opdatering leverer har en lille tabel med chunks, og også en i basisspillet; tabellen med banens bundles er banen (se [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` eksporterer en: højdefeltet for terrænet, hvert mesh banens statiske modelgrupper placerer, objekterne placeret enkeltvis, hvor de står, og banens terrænbaggrund rundt om kortet. Med `--textures` har hver overflade sit farvekort; med `--navmesh` kommer de overflader soldater går på også med. Hvordan det læses, står i [Frostbite](reader-frostbite.md).

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<level>` | påkrævet | et navn som `levels` udskriver det, en unik del af et, eller stien til en banes `.toc` |
| `-o`, `--out FILE` | `<level>.glb` (i `$HEAT3D_LEVELS/<game>/` når den er sat) | den `.glb` der skrives |
| `--install FOLDER` | den første Steam-udgave hvis `Data` har en `layout.toc` | spillets mappe |
| `--textures [PIXELS]` | fra; 512 når den gives uden størrelse | skriv hver overflades farvekort, den største mip der ikke er større end PIXELS på en side, og dens teksturkoordinater som spillet har dem, med en gentagende sampler (se [Outputformat](output-format.md)). Højdefeltet får terrænbaggrundens farvekort hvor det dækker, ellers middelfarven af terrænets overfladematerialer, ellers baggrundens gennemsnitsfarve rundt om det. Slået fra får hver del en flad farve |
| `--ground-texture [METRES]` | fra; 0,5 når den gives uden størrelse | bag terrændekalerne — veje, startbaner, perroner, malede markeringer — ind over jordfarven, ganget med terrænets farvekort hvor banen har et, ind i højdefeltets farve, METRES pr. pixel, i fliser på højst 4.096 pixels (`ground:terrain x<x> z<z>`). Virker med eller uden `--textures` |
| `--navmesh` | fra | tilføj banens navigationsmesh for dens mindste agent, soldaten (1,8 m høj, 0,4 m bred), som delen `nav:walkable`: jorden, gulve, trapper og de tage en soldat kan nå, uden forbindelserne (spring, stiger, spring over) imellem dem |
| `--ground-spacing METRES` | 4 | højdefeltets fineste afstand; noder finere end det nedsamples. 0 udelader højdefeltet |
| `--detail-budget N` | hver kopi på sit groveste niveau, plus en fjerdedel, mindst 1.500.000 | et loft for trekanter. De meshes der koster mest, mister et detaljeniveau ad gangen, til det passer; passer det stadig ikke med de groveste niveauer, udelades de mindste kopier først. Terrænbaggrunden grovgøres aldrig og udelades aldrig |
| `--skip TEXT` | | udelad statiske modelgrupper hvis partitionsnavn indeholder TEXT; gentag for flere. En spiltilstands lag, for eksempel |
| `--by-mesh` | fra | til at finde ud af hvad en del er: én del pr. kildemesh og materiale, navngivet `<part> \| <mesh> \| <material>`; en langt større fil |
| `--clamped-uvs` | fra | til en renderer der ikke kan gentage en tekstur: skær hver teksturerede trekant i stykker hvis koordinater ligger inden for 0..1, og tegn en trekant der ville have brug for mere end 4 stykker i sin teksturs gennemsnitsfarve, i en del `<part> (average colour)` |

Den udskriver grupperne og hvor mange kopier hver fik placeret, de meshes den udelod og hvorfor, trekanterne pr. del (og med `--textures` hvor mange teksturer, og hvor mange sektioner der fandt deres farvekort), hvad jorden består af, og med `--navmesh` hvor mange navigationsfliser der blev læst. Der skrives intet om banen ud over geometrien: ingen navne, ingen metadata (se [Outputformat](output-format.md)).

Terrænbudgettet er adskilt: højdefeltet og baggrunden grovgøres aldrig af `--detail-budget`; `--ground-spacing` bestemmer højdefeltets størrelse.

En hel bane er stor: typisk over ti millioner trekanter og flere hundrede MB. `--textures` lægger lidt til filen; en bane tyk med træer kan nå omkring 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` bringer en bane ned på omkring en tredjedel af det.

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

`<game>` er spillets mappe, dens `Content/Paks`, eller navnet på dens mappe i et Steam-bibliotek (`"<Steam game folder name>"`). `ue-maps` lister hvert kort der har færdigbagte World Partition-celler ved siden af sig. `ue-map` eksporterer et som `ground:<map>` (landskabet), `structure:<map>` (kortets sammenflettede HLOD-meshes) og `water:<map>` (dets vandområder hvor de står over jorden), i Unreal-**centimeter** med Y og Z byttet om - den eneste eksport der ikke er i meter. Hvordan hver læses og kontrolleres: [Unreal 5-kort](level-unreal-world-partition.md).

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<map>` | påkrævet | et navn som `ue-maps` udskriver det, eller en unik del af et |
| `-o`, `--out FILE` | `<map>.glb` (i `$HEAT3D_LEVELS/<game>/` når den er sat) | den `.glb` der skrives |
| `--ground-spacing METRES` | 2 | landskabets vertex-afstand i filen, rundet til et helt antal af dets egne quads |
| `--no-structures`, `--no-water` | | udelad den del |

Den udskriver trekanterne pr. del, hvor mange landskabskomponenter der blev læst, og hvor mange af de vertices de gemmer to gange, der ikke stemmer overens. Et 3 km kort ved 2 m er omkring 4,6 millioner jordtrekanter.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` lister hver verden med et terræn, efter sin mappe under `worlds/`. `enfusion-world` eksporterer en: `ground:<world>` (terrænet, i farverne fra dets supertekstur-fliser), `water:<world>` (havet, ved højde nul) og `structure:<world>` (hver placeret models boks), i spillets egne meter - x mod øst, y op, z mod nord. Hvordan hver læses og kontrolleres: [Arma Reforger-verdener](level-arma-reforger.md).

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `<world>` | påkrævet | en verden som `enfusion-worlds` udskriver den |
| `-o`, `--out FILE` | `<world>.glb` (i `$HEAT3D_LEVELS/<game>/` når den er sat) | den `.glb` der skrives |
| `--install FOLDER` | Steam-biblioteket der holder spillet | spillets mappe |
| `--ground-spacing METRES` | 2 (terrænets egen) | terrænets vertex-afstand i filen |
| `--texture-size PIXELS` | 4096 | den største side af jordens farvebillede; 0 for flad farve |
| `--no-structures` | | udelad de placerede modeller |
| `--trees` | fra | placer også træer og anden vegetation, som kasser |

Den udskriver trekanterne pr. del, hvor mange tile-kant-vertices der ikke stemmer overens, hvor mange entiteter verdensfilen indeholder og hvor mange kasser der blev placeret, og hvad der blev udeladt og hvorfor.

## Miljøvariabler {#environment-variables}

| Variabel | Virkning |
|---|---|
| `HEAT3D_OODLE` | sti til en `oo2core_*_win64.dll`, eller en mappe der holder en; se [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | én mappe for hver eksport lavet uden `-o`: hvert spils ligger i `<HEAT3D_LEVELS>/<game>/` (baner i `<game>/courses/`, bilpakken i `forza/`). Når den ikke er sat, ligger de i den aktuelle mappe |
| `HEAT3D_NO_UPDATE` | enhver værdi andet end tom, `0`, `false`, `no` slår opdateringstjekket fra; se [Opdateringer](updates.md) |
| `LOCALAPPDATA` | hvor FH Companion-biblioteket, BeamNGs brugermappe og opdateringens cache søges |
| `HEAT3D_COURSE` | kun til tests: den bane den installerede spil-kantstens-test bruger; se [Udvikling](development.md) |
