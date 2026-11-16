---
title: "Kommandon"
nav_order: 2
lang: "sv"
source: commands.md
source_hash: "8ae04c37b1a4"
nav_exclude: true
search_exclude: true
---
# Kommandon {#commands}

Varje kommando körs som `python -m heat3d_gamefiles <verb> ...` från mappen med
förrådet. Verben står i den ordning du oftast behöver dem: vad är den här filen,
vad finns i den, ge mig den där, och gör om ett varv till en bana.

| Verb | Tar | Gör |
|---|---|---|
| [`identify`](#identify) | valfri fil | anger containerformatet genom att läsa filens bytes |
| [`list`](#list) | en Unreal `.pak` eller IoStore `.utoc`, en Source 2 `.vpk`, eller en zip (en ForzaTech `.minizip` genom Forza-verktyget) | listar dess poster |
| [`extract`](#extract) | samma | skriver en post till disk |
| [`meshes`](#meshes) | en Unity-`SerializedFile` | listar och kontrollerar dess meshar |
| [`course`](#course) | ett varv | exporterar banan runt det (Forza, BeamNG.drive, Assetto Corsa Rally) (körs av Forza-, BeamNG.drive- eller AC Rally-verktyget) |
| [`courses`](#courses) | ett inspelat varvbibliotek | kör `course` på varje bana i det (Forza) (körs av Forza-verktyget) |
| [`races`](#races) | en installerad Forza | listar varje lopp spelet definierar: vad det lägger till, vad det döljer, platser och läget för dess export (körs av Forza-verktyget) |
| [`terrain`](#terrain) | en Forza-banmapp | klipper ut ett område efter världskoordinater (körs av Forza-verktyget) |
| [`levels`](#levels-and-level-frostbite) | ett installerat Frostbite-spel (Battlefield 6) | listar dess nivåer (körs av Battlefield-verktyget) |
| [`level`](#levels-and-level-frostbite) | en nivås namn | exporterar nivån: terräng, placerade meshar, vid behov deras färgkartor (Battlefield 6) (körs av Battlefield-verktyget) |
| [`cars`](#cars) | en installerad Forza | varje bil i låg detaljnivå, i en fil för visarens flik Racinganalys (körs av Forza-verktyget) |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | ett Unreal 5-spel | listar dess World Partition-kartor |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | en kartas namn | exporterar kartan: landskap, HLOD-strukturer, vatten |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | ett installerat Arma Reforger | listar dess världar (körs av Reforger-verktyget) |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | en världs namn | exporterar världen: terräng i dess färger, havet, byggnader som lådor (körs av Reforger-verktyget) |

**Så läser du exemplen:** `<x>` betyder att du ersätter det med ditt eget värde,
utan vinkelparenteserna; `[...]` är valfritt; sätt en sökväg med mellanslag inom
"dubbla citattecken", till exempel `"C:\Games\My Game"`. Är det nytt för dig? Se
[Innan du börjar](before-you-start.md). Det fullständiga `--help` för varje verb
finns på [Kommandoreferensen](../cli-reference.md).

Varje gång programmet startar kan det först leta efter en nyare version. Se
[Uppdateringar](updates.md). `HEAT3D_NO_UPDATE=1` stänger av den kontrollen.

Källa: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Steg-för-steg-sidor: [Undersöka arkiv](inspecting-archives.md), [Exportera en bana](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html),
[Hela nivåer](whole-levels.md), [Forza-bilar](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Slutkoder {#exit-codes}

| Kod | Betydelse |
|---|---|
| 0 | klart |
| 1 | arbetet misslyckades (ett oläsbart varv, inget spel hittades, inget att exportera, en bana i `courses` misslyckades; för `list` och `extract`, en fil som inte är något av de arkiv de läser, en som inte kan öppnas eller läsas - en krypterad pak utan `--key`, en krypterad IoStore-container - eller en post som inte finns i arkivet) |
| 2 | felaktiga argument (argparse), en sökväg som inte finns, en `--key` som inte är 64 hexadecimala siffror, eller `terrain` som fick både eller ingen av `--box` och `--route` |

Felen från `list` och `extract` skrivs var och en som en rad på standardfelutdata,
inte som en Python-spårutskrift.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Det här läser filen och säger vilken container det är. Det går inte efter
filändelsen (undantaget är en `.ucas`, nedan). Det prövar formaten i den här
ordningen och stannar vid det första som går att tolka:

1. **Unreal `.pak`**: en fotnot med pak-magin i de sista 1 024 byten. Skriver ut
   versionen, indexets position och storlek, om indexet är krypterat och
   komprimeringsmetoderna.
2. **Unreal IoStore `.utoc`**: IoStore-magin i början. Skriver ut versionen, antalet
   chunkar och om containern är krypterad; för en som inte är det, antalet filer
   dess katalog anger (och under vilken mountpunkt), komprimeringsmetoderna och om
   dess `.ucas` ligger bredvid. En `.ucas` har ingen egen header, så den känns igen
   på den `.utoc` med samma namn som ligger bredvid den, och `identify` anger den filen.
3. **ForzaTech `.minizip`**: `PGZP`-magin. Skriver ut versionen, antalet poster och
   segment, och om `ChunkContentsMiniZip<n>.txt` som anger posterna ligger bredvid
   (och, om den finns, om den anger lika många som det finns).
4. **zip**: en lokal zip-filhuvud i början. Skriver ut antalet poster, de sex vanligaste
   filändelserna, och nivånamnen när posterna ligger under `levels/<name>/`, som i ett
   BeamNG.drive-nivåarkiv.
5. **Unity**: ett `UnityFS`-paket (skriver ut motorversionen och antalet poster) eller
   en naken `SerializedFile` (skriver ut formatet, motorversionen, antalet objekt och
   de sex vanligaste klasserna).
6. **Frostbite `.toc`**: skriver ut typen (`plain` eller `signed`), var trädet börjar,
   och antingen antalet tillgångar (binär sektionstabell) eller antalet superbundles
   (DbObject-träd).
7. **Source 2 `.vpk`**: skriver ut versionen, antalet poster och den första
   navigeringsmeshen `.nav` om arkivet har en.
8. **BeamNG `.cdae`**: form-version 31 som går att tolka. Skriver ut antalet meshar,
   antalet ritade detaljnivåer och de första materialen.
9. **BeamNG `.ter`**: det finns ingen magi, så allt måste gå ihop - en sida på 2 till
   16 384, så många höjder och lagerbyte i kvadrat, sedan 1 till 255 utskrivbara
   lagernamn. Skriver ut versionen, storleken och lagernamnen.
10. **ForzaTech `.modelbin`**: skriver ut versionen, antalet chunkar och de sex
    vanligaste chunk-taggarna. Chunkinnehållet avkodas inte här.

Formaten med en egen magi (2 till 4) kommer före Unity och Frostbite, vars kontroller
läser hela filen: ett Forza-arkiv är tiotals gigabyte.

Om ingen av dem passar skriver den ut `not a format this tool reads` och den sista
orsaken. Den orsaken kommer från ForzaTech-kontrollen.

Exempel (syntetiskt):

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

| Alternativ | Standard | Betydelse |
|---|---|---|
| `<archive>` | krävs | en Unreal `.pak`; en IoStore `.utoc` (eller `.ucas` bredvid den); en Source 2 `.vpk` (för delade VPK:er, `_dir.vpk`); en ForzaTech `.minizip`; en zip, till exempel BeamNG:s nivå- och innehållsarkiv |
| `--filter TEXT` | ingen | bara sökvägar som innehåller TEXT, gemener och versaler spelar ingen roll |
| `--limit N` | 50 | skriv ut högst N poster (det totala antalet skrivs alltid ut) |
| `--key HEX` | ingen | en AES-256-nyckel du redan har, 64 hexadecimala siffror, med eller utan `0x`. Bara en krypterad `.pak` använder den. Allt som inte är 64 hexadecimala siffror avvisas innan arkivet öppnas (slutkod 2) |

Verktyget avgör formatet från bytes: en IoStore-innehållsförteckning, en `.minizip`
och en VPK på signaturen de börjar med, en zip på dess lokala filhuvud, och en `.pak`
på fotnoten i slutet. En `.ucas` har inget huvud och öppnas via `.utoc` med samma namn.
En fil som ingen av dem är avvisas med `<file> is not an archive list and extract read (...)`.
En som är ett arkiv men inte kan öppnas avvisas med läsarens orsak: en krypterad pak
utan `--key`, en krypterad IoStore-container, en pak-version den inte läser. Hur som
helst är det en rad och slutkod 1.

Varje rad visar den okomprimerade storleken, komprimeringsmetoden och sökvägen:

| Arkiv | Metod | Sökvägar |
|---|---|---|
| `.pak` | `none`, eller namnet från fotnoten (`Zlib`, `Oodle`, `Gzip`...) | med arkivets mountpunkt, till exempel `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, eller containerns metod (`Oodle`, `Zlib`...), så som dess första block är lagrat | med mountpunkten, till exempel `../../../<Project>/Content/...`. En container utan katalogindex anger inga filer och avvisas |
| `.vpk` | alltid `stored` | som i katalogen |
| `.minizip` | `lz4`, `deflate` eller `stored` | som `ChunkContentsMiniZip<n>.txt` bredvid `GeoChunk<n>.minizip` skriver dem, med byggmaskinens prefix borttaget (bakstreck, så som spelet skriver dem). Arkivet lagrar inga namn, så utan den filen heter posterna `#0`, `#1`... En lista vars radantal skiljer sig från antalet poster avvisas: de hör inte ihop |
| zip | `stored`, `deflate`, ... | som lagrat; mappar listas inte |

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

| Alternativ | Standard | Betydelse |
|---|---|---|
| `<archive>` | krävs | som för `list` |
| `<entry>` | krävs | sökvägen exakt så som `list` skriver ut den (skiftlägeskänslig); i en `.minizip` fungerar också `#<nummer>` |
| `--out FILE` | postens filnamn (efter sista `/` eller `\`), i den aktuella mappen | var den ska skrivas; överordnade mappar skapas |
| `--key HEX` | ingen | som för `list` |

Posten dekrypteras (pak, med en nyckel), packas upp och skrivs ut. Den skriver
`<bytes> bytes -> <file>`. Finns sökvägen inte i arkivet avslutas kommandot med
kod 1. Det gör också en post som inte kan läsas (en krypterad post utan nyckel, en
Oodle-komprimerad post utan Oodle-biblioteket), med orsaken på en rad. En VPK-post
kontrolleras inte mot sin CRC här. Läsaren har en metod `verify()` för det (se
[Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Alternativ | Standard | Betydelse |
|---|---|---|
| `<path>` | krävs | en naken Unity-`SerializedFile` (`sharedassets0.assets`, `level0`...), inte ett paket |
| `--limit N` | 25 | avkoda och skriv ut högst N meshar |

Det skriver ut antalet `Mesh`-objekt, sedan en rad per mesh: namnet (de första 40
tecknen), antalet hörn och trianglar, och `ok` eller `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` betyder att de avkodade hörnen inte återger den inbäddade box som
Unity lagrat för meshen, inom 2 % av boxens storlek. Det är tolkningens egen kontroll
(se [Unity](reader-unity.md)). En mesh som inte kan läsas rapporteras med orsaken och
räknas mot gränsen. Hörndata i en `.resS`-fil läses från mappen som containern ligger i.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## Spelens egna verb {#the-games-own-verbs}

Varje spelläsare är ett eget litet projekt med egen licensfil, egna releaser och eget
ärendesystem, så att den kan installeras, uppdateras, underhållas - eller dras
tillbaka på en rättighetshavares begäran - för sig, utan att påverka visaren eller de
andra verktygen. Installera det för ditt spel (dess sida säger hur), så fungerar både
dess egna kommando och verben här. GameFiles kör spelets verktyg med de argument du
gav det; ingenting av verktyget importeras. Det hittas som dess kommando på `PATH`,
som dess installerade paket, eller som dess mapp i `HEAT3D_<GAME>_MAPS` eller bredvid
GameFiles (`exporters/ext/<game>-maps` i en 3DHeat-utcheckning, eller
`3DHeat-Ext-<Game>` bredvid den här mappen). När det inte är installerat säger verbet
var det får tag i det och avslutar med kod 2.

| Spel | Dess egna verktyg | Verb här som kör det |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (Forza-varv), `courses`, `races`, `cars`, `terrain`; `identify`, `list`, `extract` av en `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level`; `identify` av en Frostbite-`.toc` |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (BeamNG-varv); `identify` av en `.cdae` eller `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (AC Rally-varv) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verb> --help` visar spelverktygets egna alternativ.

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Banan runt ett varv - marken i ett band på vardera sidan av körningen, och det som
står på den, som en enda `.glb` - gjord av varvets spels egna verktyg, körd med
samma argument: [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html),
[BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html),
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). Vad ett varv
kan vara: [Varvindata](lap-inputs.md); hur mycket detalj som behålls:
[Detaljnivåer och budgeten](detail-budget.md).

### Vilket spel {#which-game}

Spelet tas från `--game`, sedan från fältet `game` i en `heat3d-lap`-fil (eller i en
CSV:s `# {...}`-beskrivningsrad), och annars är det Forza. En mapp får spelet dess
filer anger, om de anger bara ett; en fil som inte anger något (ett FH Companion-varv,
`course.json`, en CSV utan beskrivningsrad) räknas inte (se [Varvindata](lap-inputs.md)).

| Värde | Körs av |
|---|---|
| börjar med `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` eller `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | nekas: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | nekas: "tracks ship in a protected format that is not a file-extraction target" |
| något annat | nekas: "there is no course reader for <game> yet" |

Ett nekande föreslår också alternativen: rekonstruera banan från spelandet (3DHeat
GameCapture), eller analysera varven utan bana, eftersom visarens flik Racinganalys
ritar en väg utifrån dem.

## courses, races, cars, terrain (Forza) {#courses-races-cars-terrain-forza}

Körs av `heat3d-forza-maps` med samma argument: [dess kommandon](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels and level (Frostbite) {#levels-and-level-frostbite}

Körs av `heat3d-battlefield-maps` med samma argument: [Battlefield-nivåer](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` är spelets mapp, dess `Content/Paks`, eller namnet på dess mapp i ett
Steam-bibliotek (`"<Steam game folder name>"`). `ue-maps` listar varje karta som har
färdiga World Partition-celler bredvid sig. `ue-map` exporterar en som `ground:<map>`
(landskapet), `structure:<map>` (kartans sammanslagna HLOD-meshar) och `water:<map>`
(dess vattenområden där de står över marken), i Unreals **centimeter** med Y och Z
bytta - den enda exporten som inte är i meter. Hur varje läses och kontrolleras:
[Unreal 5-kartor](level-unreal-world-partition.md).

| Alternativ | Standard | Betydelse |
|---|---|---|
| `<map>` | krävs | ett namn så som `ue-maps` skriver ut det, eller en unik del av ett |
| `-o`, `--out FILE` | `<map>.glb` (i `$HEAT3D_LEVELS/<game>/` när den är satt) | `.glb`-filen att skriva |
| `--ground-spacing METRES` | 2 | landskapets hörnavstånd i filen, avrundat till ett helt antal av dess egna rutor |
| `--no-structures`, `--no-water` | | lämna den delen utanför |

Den skriver ut trianglarna per del, hur många landskapskomponenter som lästes, och
hur många av hörnen de lagrar två gånger som inte stämmer överens. En 3 km karta på
2 m är ungefär 4,6 miljoner markettrianglar.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

Körs av `heat3d-reforger-maps` med samma argument (dess `worlds` och `world`):
[Arma Reforger-världar](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Environment variables {#environment-variables}

| Variabel | Effekt |
|---|---|
| `HEAT3D_OODLE` | sökväg till en `oo2core_*_win64.dll`, eller en mapp som innehåller en; se [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | en mapp för varje export gjord utan `-o`: varje spels hamnar i `<HEAT3D_LEVELS>/<game>/` (banor i `<game>/courses/`, bilpaketet i `forza/`). Om den inte är satt hamnar de i den aktuella mappen |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | ett spelverktygs mapp, när det varken är installerat eller bredvid GameFiles |
| `HEAT3D_NO_UPDATE` | valfritt värde utom tomt, `0`, `false`, `no` stänger av kontrollen av uppdateringar; se [Uppdateringar](updates.md) |
| `LOCALAPPDATA` | där FH Companion-biblioteket, BeamNG:s användarmapp och uppdateringscachen letas |
| `HEAT3D_COURSE` | endast tester: banan som den installerade spelets kantstenstest använder; se [Utveckling](development.md) |
