---
title: Felsökning
nav_order: 11
lang: "sv"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Felsökning {#troubleshooting}

Meddelandena verktyget skriver när något stoppar det, vad varje betyder, och vad du gör.
Meddelanden citeras från koden, med platshållare inom vinkelparenteser.

## Innan verktyget ens startar {#before-the-tool-even-starts}

| Du ser | Gör så här |
|---|---|
| `'python' is not recognized` | installera Python 3.10 eller senare och bocka i "Add python.exe to PATH"; öppna en ny terminal ([Innan du börjar](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminalen står i fel mapp: `cd` till mappen med `README.md` |
| `No module named numpy` (eller ett annat paket) | kör `pip install -r requirements.txt` |
| en sökväg med mellanslag klipps av, eller `unrecognized arguments` | sätt sökvägen inom dubbla citattecken: `"C:\My Games\lap.json"` |

## Hitta spelet {#finding-the-game}

| Meddelande | Betydelse | Gör så här |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | inget Steam-bibliotek eller `C:\XboxGames` har ett spel med `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | varvets koordinater ligger inte på någon installerad bana | kontrollera att varvet är från det här spelet; ange `--track` om banan ligger någon annanstans |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | det finns rutor nära lådan men ingen som täcker körningen i korridoren | som ovan |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<mapp med gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<spelmapp>"` |
| `no readable IoStore containers in <folder>` | mappen har ingen `.utoc` som öppnas | peka `--install` på mappen med `.utoc`-filerna |

## Hitta platsen {#finding-the-place}

| Meddelande | Betydelse | Gör så här |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: ingen nivå fick 30 % | `--level <name>`; kontrollera att varvet är i visarens ram |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` matchade inte | använd ett av de listade mappnamnen |
| `<level> has no scene (no main/*.level.json and no .mis)` | nivåmappen saknar scenfiler | en trasig eller ofullständig nivå eller mod |
| `no terrain of <level> lies along the driving.` | BeamNG: korridoren har inga terrängrutor | fel nivå, eller en nivå utan terräng där varvet är |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: ingen etapp och riktning fick 50 % | `--level <stage>`; kontrollera att varvets positioner är meter med y uppåt |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` matchade inte | använd ett av de listade namnen |
| `no ground of <stage> lies along the driving.` | AC Rally: ingen markruta i korridoren | fel etapp |

## Varvet {#the-lap}

| Meddelande | Gör så här |
|---|---|
| `<file> is not a lap this can read. ...` | ge den en form som stöds, se [Varvindata](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON:en är inte ett varv |
| `<file> has no x, y and z columns` | namnge CSV-kolumnerna `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | kontrollera namnet, eller ange en fil |
| `'<name>' matches 3 courses: ...` | använd en längre del av namnet |
| `<name> holds no driving` | varvet har färre än två punkter |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` behöver en rutt-JSON med `bounds`, som `heat3d_capture route` och `laps` skriver den; en varvfil är för `course` |
| `give exactly one of --box and --route` | `terrain` behöver en region |
| `no course export for this lap: <reason>.` | spelet stöds inte, se [Begränsningar och kända brister](limits-and-known-gaps.md) |

## Arkiv {#archives}

| Meddelande | Betydelse |
|---|---|
| `no Oodle library found. ...` | ange `HEAT3D_OODLE`, se [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | ett krypterat pak: `--key <hex>` om du har nyckeln. Det finns inget annat sätt |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | nyckeln är 32 byte skrivna som 64 hexadecimala siffror, `0x` valfritt (avslutningskod 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | det är inget av dessa; `identify` säger vad det är. En Unity-behållare tar `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | en krypterad IoStore-behållare. Den kan inte läsas |
| `pak version <n>; this reader handles 8-12` | ett äldre eller nyare pakformat |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | från Python: prova `.utoc`, som `list` och `extract` också tar |
| `<file> has no directory index, so its chunks carry no names to list` | en IoStore-behållare som inte namnger några filer; dess chunkar nås bara via andra paket |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` bredvid arkivet är från en annan build eller ett annat arkiv; utan den listas posterna efter nummer |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | namnen hashades bort vid bygget |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | en Frostbite-tabell i den obfuskerade formen |
| `no Frostbite game found in a Steam library; give --install` | `levels` eller `level` hittade inget Steam-spel vars `Data` har en `layout.toc`; ange spelets mapp |
| `no level called '<name>'; did you mean one of ...?` | namnet matchade ingen nivåtabell, eller flera; `levels` listar dem |
| `nothing was placed: no static model group was recognised` | nivåns gruppmedlemmar har en annan typsignatur, efter en speluppdatering eller i ett annat Frostbite-spel; layouten måste mätas om |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | en komprimerad Unity-mesh |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | behåll `.resS` bredvid `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | ett äldre Unity-bygge |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` tar en naken behållare |
| `texture format <n> has not been identified; refusing to guess` | ett Forza-färgprovsformat som inte setts tidigare |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | behåll en delad VPK:s delar tillsammans |

## Exporter som blir fel {#exports-that-come-out-wrong}

| Symptom | Troligen orsak |
|---|---|
| banan är förskjuten från varvet i visaren | varvet och exporten använder olika ramar: kontrollera `--game` (ett BeamNG-varv läst som Forza, till exempel) |
| ingen kant i en Forza-bana | `--no-textures`, eller rutan hade inga kartor för den `--season` (konsolen skriver `N without maps`) |
| en Forza-ruta i platta färger | dess markkartor saknas för säsongen |
| betydligt färre placerade objekt än väntat | en uttryckligen angiven `--detail-budget` är för liten; sammanfattningen säger hur många kopior som utelämnades |
| filen är mycket stor (hundratals MB) | en stadskorridor under den automatiska budgeten; använd `--detail-budget`, `--texture-size 1024` eller `--margin 40` |
| staket saknas | genomskinliga ytor utelämnas med avsikt (sammanfattningen namnger dem) |
| `N meshes could not be read` | en del modeller använder ett format som läsaren vägrar; resten exporteras |
| `N of M components could not be read` (AC Rally) | en spelpatch kan ha flyttat egenskapsplatser; anmäl gärna det |
