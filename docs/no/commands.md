---
title: Kommandoer
nav_order: 2
lang: "no"
source: commands.md
source_hash: "8ae04c37b1a4"
nav_exclude: true
search_exclude: true
---
# Kommandoer {#commands}

Hver kommando kjøres som `python -m heat3d_gamefiles <verb> ...` fra
repomappen. Verbene står i den rekkefølgen du vanligvis trenger dem: hva er
denne filen, hva ligger inni, gi meg den, og gjør en runde om til en bane.

| Verb | Tar | Gjør |
|---|---|---|
| [`identify`](#identify) | en hvilken som helst fil | navngir beholderformatet ved å lese bytene |
| [`list`](#list) | en Unreal `.pak` eller IoStore `.utoc`, en Source 2 `.vpk`, eller et zip (en ForzaTech `.minizip` via Forza-verktøyet) | lister oppføringene |
| [`extract`](#extract) | det samme | skriver én oppføring til disk |
| [`meshes`](#meshes) | en Unity `SerializedFile` | lister og sjekker modellene |
| [`course`](#course) | en runde | eksporterer banen rundt den (Forza, BeamNG.drive og Assetto Corsa Rally) (kjøres av Forza-, BeamNG.drive- eller AC Rally-verktøyet) |
| [`courses`](#courses) | et bibliotek med innspilte runder | kjører `course` på hver bane i det (Forza) (kjøres av Forza-verktøyet) |
| [`races`](#races) | et installert Forza | lister hvert løp spillet definerer: hva det legger til, hva det skjuler, steder, og status for eksporten (kjøres av Forza-verktøyet) |
| [`terrain`](#terrain) | en Forza-banemappe | klipper ut et område etter verdenskoordinater (kjøres av Forza-verktøyet) |
| [`levels`](#levels-and-level-frostbite) | et installert Frostbite-spill (Battlefield 6) | lister nivåene |
| [`level`](#levels-and-level-frostbite) | et nivås navn | eksporterer nivået: terreng, plasserte modeller, eventuelt fargekartene deres (Battlefield 6) (kjøres av Battlefield-verktøyet) |
| [`cars`](#cars) | et installert Forza | hver bil i lav detalj, i én fil for visningens løpsfane (kjøres av Forza-verktøyet) |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | et Unreal 5-spill | lister kartene med World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | et kartnavn | eksporterer kartet: terreng, HLOD-strukturer, vann |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | en installert Arma Reforger | lister verdenene |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | en verdens navn | eksporterer verdenen: terreng i sine farger, havet, bygninger som bokser (kjøres av Reforger-verktøyet) |

**Slik leser du eksemplene:** `<x>` betyr at du skal erstatte det med din egen
verdi, uten vinkelparentesene; `[...]` er valgfritt; sett en sti med mellomrom i
"doble anførselstegn", for eksempel `"C:\Games\My Game"`. Er dette nytt for deg?
Se [Før du begynner](before-you-start.md). Full `--help` for hvert verb står på
[Kommandoreferansen](../cli-reference.md).

Hver gang programmet starter, kan det sjekke etter en nyere utgave først. Se
[Oppdateringer](updates.md). `HEAT3D_NO_UPDATE=1` slår av den sjekken.

Kilde: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Trinn for trinn: [Undersøke arkiver](inspecting-archives.md), [Baneeksport](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html),
[Hele nivåer](whole-levels.md), [Forza-biler](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Avslutningskoder {#exit-codes}

| Kode | Betydning |
|---|---|
| 0 | fullført |
| 1 | arbeidet mislyktes (uleselig runde, ingen spill funnet, ingenting å eksportere, en bane i `courses` mislyktes; for `list` og `extract`, en fil som ingen av arkivtypene leser, en som ikke kan åpnes eller leses - en kryptert pak uten `--key`, en kryptert IoStore-beholder - eller en oppføring som ikke finnes i arkivet) |
| 2 | feil argumenter (argparse), en sti som ikke finnes, en `--key` som ikke er 64 heksadesimale siffer, eller `terrain` gitt både eller ingen av `--box` og `--route` |

Feilene til `list` og `extract` skrives som én linje på standardfeil, ikke som en
Python-sporing.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Dette leser filen og sier hvilken beholder det er. Det går ikke på filendelsen
(unntaket er en `.ucas`, under). Den prøver formatene i denne rekkefølgen og
stopper ved det første som parser:

1. **Unreal `.pak`**: en fotdel med pak-magien i de siste 1 024 bytene. Skriver
   ut versjonen, indeksens forskyvning og størrelse, om indeksen er kryptert, og
   komprimeringsmetodene.
2. **Unreal IoStore `.utoc`**: IoStore-magien i starten. Skriver ut versjonen,
   antall deler og om beholderen er kryptert; for en som ikke er det, antall
   filer katalogen dens nevner (og under hvilket monteringspunkt), komprimerings-
   metodene, og om dens `.ucas` ligger ved siden av. En `.ucas` har ingen egen
   topptekst, så den kjennes igjen på `.utoc` med samme navn ved siden av, og
   `identify` navngir den filen.
3. **ForzaTech `.minizip`**: `PGZP`-magien. Skriver ut versjonen, antall
   oppføringer og segmenter, og om `ChunkContentsMiniZip<n>.txt` som navngir
   oppføringene ligger ved siden av (og, hvis den gjør det, om den nevner like
   mange som det finnes).
4. **zip**: en zip-topptekst for lokal fil i starten. Skriver ut antall
   oppføringer, de seks vanligste filendelsene, og nivånavnene når oppføringene
   ligger under `levels/<name>/`, som i et BeamNG.drive-nivåarkiv.
5. **Unity**: en `UnityFS`-pakke (skriver ut motorversjonen og antall
   oppføringer) eller en naken `SerializedFile` (skriver ut formatet,
   motorversjonen, antall objekter og de seks vanligste klassene).
6. **Frostbite `.toc`**: skriver ut typen (`plain` eller `signed`), hvor treet
   begynner, og enten antall ressurser (binær seksjonstabell) eller antall
   superpakker (DbObject-tre).
7. **Source 2 `.vpk`**: skriver ut versjonen, antall oppføringer, og den første
   `.nav`-navigasjonsmodellen hvis arkivet har en.
8. **BeamNG `.cdae`**: shape-versjon 31 som parser. Skriver ut antall modeller,
   antall tegnede detaljnivåer og de første materialene.
9. **BeamNG `.ter`**: det finnes ingen magi, så alt må gå opp - en side på 2 til
   16 384, så mange kvadrerte høyder og lagbytes, deretter 1 til 255 utskrivbare
   lagnavn. Skriver ut versjonen, størrelsen og lagnavnene.
10. **ForzaTech `.modelbin`**: skriver ut versjonen, antall deler og de seks
    vanligste deltaggene. Innholdet i delene dekodes ikke her.

Formatene med en egen magi (2 til 4) kommer før Unity og Frostbite, hvis
sjekker leser hele filen: et Forza-arkiv er titalls gigabyte.

Hvis ingen av dem passer, skriver den `not a format this tool reads` og den siste
grunnen. Den grunnen kommer fra ForzaTech-sjekken.

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

| Alternativ | Standard | Betydning |
|---|---|---|
| `<archive>` | påkrevd | en Unreal `.pak`; en IoStore `.utoc` (eller `.ucas` ved siden av); en Source 2 `.vpk` (for delte VPK-er, `_dir.vpk`); en ForzaTech `.minizip`; et zip, for eksempel BeamNGs nivå- og innholdsarkiver |
| `--filter TEXT` | ingen | bare stier som inneholder TEXT, uten store/små-bokstavforskjell |
| `--limit N` | 50 | skriv ut høyst N oppføringer (totalen skrives alltid ut) |
| `--key HEX` | ingen | en AES-256-nøkkel du allerede har, 64 heksadesimale siffer, med eller uten `0x`. Bare en kryptert `.pak` bruker den. Alt som ikke er 64 heksadesimale siffer avvises før arkivet åpnes (avslutningskode 2) |

Verktøyet bestemmer formatet ut fra bytene: en IoStore-innholdsfortegnelse, en
`.minizip` og en VPK etter signaturen de starter med, et zip etter den lokale
filoverskriften, og en `.pak` etter fotdelen på slutten. En `.ucas` har ingen
topptekst og åpnes gjennom `.utoc` med samme navn. En fil som ingen av disse er,
avvises med `<file> is not an archive list and extract read (...)`. En fil som
er det, men ikke kan åpnes, avvises med leserens grunn: en kryptert pak uten
`--key`, en kryptert IoStore-beholder, en pak-versjon den ikke leser. Uansett
blir det én linje og avslutningskode 1.

Hver linje viser den ukomprimerte størrelsen, komprimeringsmetoden og stien:

| Arkiv | Metode | Stier |
|---|---|---|
| `.pak` | `none`, eller navnet fra fotdelen (`Zlib`, `Oodle`, `Gzip` ...) | med arkivets monteringspunkt, for eksempel `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, eller beholderens metode (`Oodle`, `Zlib` ...), slik den første blokken er lagret | med monteringspunktet, for eksempel `../../../<Project>/Content/...`. En beholder uten katalogindeks nevner ingen filer og avvises |
| `.vpk` | alltid `stored` | slik de står i katalogen |
| `.minizip` | `lz4`, `deflate` eller `stored` | slik `ChunkContentsMiniZip<n>.txt` ved siden av `GeoChunk<n>.minizip` skriver dem, uten byggemaskinens prefiks (bakoverskråstreker, slik spillet skriver dem). Arkivet lagrer ingen navn, så uten den filen er oppføringene `#0`, `#1` ... En liste der antall linjer ikke stemmer med antall oppføringer avvises: de hører ikke sammen |
| zip | `stored`, `deflate` ... | som lagret; mapper listes ikke |

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

| Alternativ | Standard | Betydning |
|---|---|---|
| `<archive>` | påkrevd | som for `list` |
| `<entry>` | påkrevd | stien nøyaktig slik `list` skriver den (store/små bokstaver har betydning); i en `.minizip` virker også `#<nummer>` |
| `--out FILE` | oppføringens filnavn (etter siste `/` eller `\`), i gjeldende mappe | hvor den skal skrives; overordnede mapper opprettes |
| `--key HEX` | ingen | som for `list` |

Oppføringen dekrypteres (pak, med nøkkel), pakkes ut og skrives. Den skriver
`<bytes> bytes -> <file>`. Hvis stien ikke finnes i arkivet, avslutter
kommandoen med kode 1. Det samme gjelder en oppføring som ikke kan leses (en
kryptert oppføring uten nøkkel, eller Oodle-komprimert uten Oodle-bibliotek),
med grunnen på én linje. En VPK-oppføring sjekkes ikke mot CRC-en her. Leseren
har en `verify()`-metode for det (se [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Alternativ | Standard | Betydning |
|---|---|---|
| `<path>` | påkrevd | en naken Unity `SerializedFile` (`sharedassets0.assets`, `level0` ...), ikke en pakke |
| `--limit N` | 25 | dekod og skriv ut høyst N modeller |

Dette skriver antall `Mesh`-objekter, deretter én linje per modell: navnet
(de første 40 tegnene), antall vertekser og trekanter, og `ok` eller
`BOUNDS DISAGREE`. `BOUNDS DISAGREE` betyr at de dekodede vertekste ikke gir
den omsluttende boksen Unity lagret for modellen, innen 2 % av boksens størrelse.
Det er parserens egen sjekk (se [Unity](reader-unity.md)). En modell som ikke
kan leses, rapporteres med grunnen og teller mot grensen. Vertdata i en
`.resS`-fil leses fra mappen beholderen ligger i.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## Spillenes egne verb {#the-games-own-verbs}

Hver spilleser er sitt eget lille prosjekt med egen lisensfil, egne utgivelser og
egen sakssporing, slik at den kan installeres, oppdateres, vedlikeholdes - eller
trekkes tilbake på forespørsel fra en rettighetshaver - for seg selv, uten å
påvirke visningsprogrammet eller de andre verktøyene. Installer den for ditt spill
(siden for det sier hvordan), så fungerer både dets egen kommando og verbene her.
GameFiles kjører spillets verktøy med argumentene du ga det; ingenting av verktøyet
importeres. Det finnes som kommandoen på `PATH`, som den installerte pakken, eller
som mappen i `HEAT3D_<GAME>_MAPS` eller ved siden av GameFiles
(`exporters/ext/<game>-maps` i en 3DHeat-kopi, eller `3DHeat-Ext-<Game>` ved siden
av denne mappen). Når det ikke er installert, sier verbet hvor det fås og avslutter
med kode 2.

| Spill | Dets eget verktøy | Verb her som kjører det |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (Forza-runder), `courses`, `races`, `cars`, `terrain`; `identify`, `list`, `extract` av en `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level`; `identify` av en Frostbite `.toc` |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (BeamNG-runder); `identify` av en `.cdae` eller `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (AC Rally-runder) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verb> --help` viser spillverktøyets egne alternativer.

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Banen rundt en runde - bakken i et bånd på hver side av kjøringen, og det som står
på den, som én `.glb` - laget av rundens spills eget verktøy, kjørt med de samme
argumentene: [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html),
[BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html),
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). Hva en runde
kan være: [Rundeinndata](lap-inputs.md); hvor mye detalj som beholdes:
[Detaljnivåer og budsjettet](detail-budget.md).

### Hvilket spill {#which-game}

Spillet hentes fra `--game`, deretter fra feltet `game` i en `heat3d-lap`-fil
(eller CSV-ens `# {...}`-beskrivelseslinje), og er som standard Forza. En mappe
får spillet filene navngir, når de bare navngir ett; en fil som ikke navngir noe
(en FH Companion-runde, `course.json`, en CSV uten beskrivelseslinje) teller ikke
(se [Rundeinndata](lap-inputs.md)).

| Verdi | Kjøres av |
|---|---|
| begynner med `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` eller `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | avvist: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | avvist: "tracks ship in a protected format that is not a file-extraction target" |
| alt annet | avvist: "there is no course reader for <game> yet" |

En avvisning foreslår også alternativene: rekonstruer banen fra spilling
(3DHeat GameCapture), eller analyser rundene uten bane, fordi visningens
fane for løpsanalyse tegner en vei fra dem.

## courses, races, cars, terrain (Forza) {#courses-races-cars-terrain-forza}

Kjøres av `heat3d-forza-maps` med de samme argumentene:
[kommandoene dens](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels and level (Frostbite) {#levels-and-level-frostbite}

Kjøres av `heat3d-battlefield-maps` med de samme argumentene:
[Battlefield-nivåer](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` er spillets mappe, dens `Content/Paks`, eller navnet på mappen i et
Steam-bibliotek (`"<Steam game folder name>"`). `ue-maps` lister hvert kart som
har innbakte World Partition-celler ved siden av seg. `ue-map` eksporterer ett av
dem som `ground:<map>` (terrenget), `structure:<map>` (kartets sammenslåtte HLOD-
modeller) og `water:<map>` (vannmassene der de står over bakken), i Unreal
**centimeter** med Y og Z byttet om - den ene eksporten som ikke er i meter. Hvordan
hver leses og sjekkes: [Unreal 5-kart](level-unreal-world-partition.md).

| Alternativ | Standard | Betydning |
|---|---|---|
| `<map>` | påkrevd | et navn slik `ue-maps` skriver det, eller en unik del av et navn |
| `-o`, `--out FILE` | `<map>.glb` (i `$HEAT3D_LEVELS/<game>/` når den er satt) | `.glb`-filen som skal skrives |
| `--ground-spacing METRES` | 2 | avstanden mellom terrengets vertekser i filen, avrundet til et helt antall av sine egne firkanter |
| `--no-structures`, `--no-water` | | utelat den delen |

Den skriver ut trekanter per del, hvor mange terrengkomponenter som ble lest, og
hvor mange av verteksene de lagrer to ganger som ikke stemmer. Et 3 km kart på
2 m er rundt 4,6 millioner bakketrekanter.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

Kjøres av `heat3d-reforger-maps` med de samme argumentene (dets `worlds` og
`world`): [Arma Reforger-verdener](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Miljøvariabler {#environment-variables}

| Variabel | Virkning |
|---|---|
| `HEAT3D_OODLE` | sti til en `oo2core_*_win64.dll`, eller en mappe som har en; se [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | én mappe for alle eksporter laget uten `-o`: hvert spills havner i `<HEAT3D_LEVELS>/<game>/` (baner i `<game>/courses/`, bilpakken i `forza/`). Uten den havner de i gjeldende mappe |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | mappen til et spills verktøy, når det verken er installert eller ved siden av GameFiles |
| `HEAT3D_NO_UPDATE` | en verdi annen enn tom, `0`, `false` eller `no` slår av oppdateringssjekken; se [Oppdateringer](updates.md) |
| `LOCALAPPDATA` | der FH Companion-biblioteket, BeamNGs brukermappe og oppdateringsbufferen letes etter |
| `HEAT3D_COURSE` | kun for tester: banen som den installerte-spill-testen for kantstein bruker; se [Utvikling](development.md) |
