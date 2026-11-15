---
title: Feilsøking
nav_order: 11
lang: "no"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Feilsøking {#troubleshooting}

Meldingene verktøyet skriver når noe stopper det, hva hver betyr, og hva du gjør. Meldinger er sitert fra koden, med plassholdere i vinkelparenteser.

## Før verktøyet i det hele tatt starter {#before-the-tool-even-starts}

| Du ser | Gjør |
|---|---|
| `'python' is not recognized` | installer Python 3.10 eller nyere og kryss av for «Add python.exe to PATH»; åpne en ny terminal ([Før du begynner](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminalen står i feil mappe: `cd` til mappen med `README.md` |
| `No module named numpy` (eller en annen pakke) | kjør `pip install -r requirements.txt` |
| en sti med mellomrom blir kuttet, eller `unrecognized arguments` | sett stien i doble anførselstegn: `"C:\My Games\lap.json"` |

## Finne spillet {#finding-the-game}

| Melding | Betydning | Gjør |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | ingen Steam-bibliotek eller `C:\XboxGames` har et spill med `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | runden sine koordinater finnes ikke på noen installerte bane | kontroller at runden er fra dette spillet; gi `--track` hvis banen er et annet sted |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | det finnes fliser nær boksen, men ingen i korridoren | samme som over |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | mappen har ingen `.utoc` som åpnes | pek `--install` på mappen med `.utoc`-filene |

## Finne stedet {#finding-the-place}

| Melding | Betydning | Gjør |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: ingen nivå fikk 30 % | `--level <name>`; kontroller at runden er i visningsrammen |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` traff ikke | bruk ett av de oppførte mappenavnene |
| `<level> has no scene (no main/*.level.json and no .mis)` | nivåmappen har ingen scenefiler | et ødelagt eller ufullstendig nivå eller mod |
| `no terrain of <level> lies along the driving.` | BeamNG: korridoren har ingen terrengruter | feil nivå, eller et nivå uten terreng der runden er |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: ingen etappe og ramme fikk 50 % | `--level <stage>`; kontroller at rundens posisjoner er meter med y opp |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` traff ikke | bruk ett av de oppførte navnene |
| `no ground of <stage> lies along the driving.` | AC Rally: ingen bakkeflis i korridoren | feil etappe |

## Runden {#the-lap}

| Melding | Gjør |
|---|---|
| `<file> is not a lap this can read. ...` | gi en støttet form, se [Rundeinndata](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON-filen er ikke en runde |
| `<file> has no x, y and z columns` | gi CSV-kolonnene navnene `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | kontroller navnet, eller gi en fil |
| `'<name>' matches 3 courses: ...` | bruk en lengre del av navnet |
| `<name> holds no driving` | runden har færre enn to prøver |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` trenger en rute-JSON med `bounds`, slik `heat3d_capture route` og `laps` skriver den; en rundefil er for `course` |
| `give exactly one of --box and --route` | `terrain` trenger ett område |
| `no course export for this lap: <reason>.` | spillet støttes ikke, se [Begrensninger og kjente mangler](limits-and-known-gaps.md) |

## Arkiver {#archives}

| Melding | Betydning |
|---|---|
| `no Oodle library found. ...` | sett `HEAT3D_OODLE`, se [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | en kryptert pak: `--key <hex>` hvis du har nøkkelen. Det finnes ingen annen vei |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | nøkkelen er 32 byte skrevet som 64 heksadesimale siffer, `0x` valgfritt (avslutningskode 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | den er ingen av disse; `identify` sier hva den er. En Unity-beholder tar `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | en kryptert IoStore-beholder. Den kan ikke leses |
| `pak version <n>; this reader handles 8-12` | en eldre eller nyere pak-versjon |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | fra Python: prøv `.utoc`, som `list` og `extract` også tar |
| `<file> has no directory index, so its chunks carry no names to list` | en IoStore-beholder som ikke nevner noen filer; dens chunker nås bare gjennom andre pakker |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` ved siden av arkivet er fra et annet bygg eller et annet arkiv; uten den listes oppføringene etter nummer |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | navnene ble hashet bort ved bygging |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | en Frostbite-tabell i den forvrengede formen |
| `no Frostbite game found in a Steam library; give --install` | `levels` eller `level` fant ikke et Steam-spill der `Data` har en `layout.toc`; gi spillets mappe |
| `no level called '<name>'; did you mean one of ...?` | navnet traff ingen nivåtabell, eller flere; `levels` lister dem |
| `nothing was placed: no static model group was recognised` | nivåets gruppemedlemmer har en annen typesignatur, etter en spilloppdatering eller i et annet Frostbite-spill; oppsettet må måles på nytt |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | en komprimert Unity-mesh |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | behold `.resS` ved siden av `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | et eldre Unity-bygg |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` tar en ren beholder |
| `texture format <n> has not been identified; refusing to guess` | et Forza-fargeprøveformat som ikke er sett før |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | behold delene av en delt VPK sammen |

## Eksporter som blir feil {#exports-that-come-out-wrong}

| Symptom | Sannsynlig årsak |
|---|---|
| løypen er forskjøvet fra runden i visningen | runden og eksporten bruker ulike rammer: sjekk `--game` (en BeamNG-runde lest som Forza, for eksempel) |
| ingen skulder i en Forza-løype | `--no-textures`, eller flisen hadde ingen kart for den `--season`-en (konsollen sier `N without maps`) |
| en Forza-flis i flate farger | bakkekartene mangler for årstiden |
| langt færre plasserte objekter enn forventet | et eksplisitt `--detail-budget` er for lite; oppsummeringen sier hvor mange kopier som ble utelatt |
| filen er svært stor (hundrevis av MB) | en bykorridor under det automatiske budsjettet; bruk `--detail-budget`, `--texture-size 1024` eller `--margin 40` |
| gjerder mangler | gjennomsiktige flater er utelatt med vilje (oppsummeringen navngir dem) |
| `N meshes could not be read` | noen modeller bruker et format leseren avviser; resten eksporteres |
| `N of M components could not be read` (AC Rally) | en spilloppdatering kan ha flyttet egenskapsplasser; gi gjerne beskjed |
