---
title: Rješavanje problema
nav_order: 11
lang: "hr"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Rješavanje problema {#troubleshooting}

Poruke koje alat ispisuje kad nešto zaustavi, što znače i što učiniti. Poruke su citirane iz
koda, a mjesta u kutastim zagradama su zamjene.

## Prije nego što alat uopće krene {#before-the-tool-even-starts}

| Vidite | Učinite |
|---|---|
| `'python' is not recognized` | instalirajte Python 3.10 ili noviji i označite "Add python.exe to PATH"; otvorite novi terminal ([Prije nego što počnete](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminal je u krivoj mapi: `cd` u mapu s `README.md` |
| `No module named numpy` (ili drugi paket) | pokrenite `pip install -r requirements.txt` |
| putanja s razmacima je odsječena, ili `unrecognized arguments` | stavite putanju u dvostruke navodnike: `"C:\My Games\lap.json"` |

## Pronalaženje igre {#finding-the-game}

| Poruka | Značenje | Učinite |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | nijedna Steam biblioteka ni `C:\XboxGames` nema igru s `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | koordinate kruga nisu ni na jednoj instaliranoj stazi | provjerite je li krug iz ove igre; predajte `--track` ako je staza drugdje |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | pločice postoje blizu okvira, ali nijedna ne pokriva vožnju u koridoru | kao gore |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | mapa nema `.utoc` koji se otvara | usmjerite `--install` na mapu s `.utoc` datotekama |

## Pronalaženje mjesta {#finding-the-place}

| Poruka | Značenje | Učinite |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: nijedna razina nije postigla 30% | `--level <name>`; provjerite je li krug u okviru preglednika |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` se nije podudarao | koristite jedno od ispisanih imena mapa |
| `<level> has no scene (no main/*.level.json and no .mis)` | mapa razine nema datoteke scene | pokvarena ili nepotpuna razina ili mod |
| `no terrain of <level> lies along the driving.` | BeamNG: koridor nema kvadrata terena | kriva razina, ili razina bez terena tamo gdje je krug |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: nijedna etapa i okvir nisu postigli 50% | `--level <stage>`; provjerite jesu li pozicije kruga metri s Y prema gore |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` se nije podudarao | koristite jedno od ispisanih imena |
| `no ground of <stage> lies along the driving.` | AC Rally: nijedna pločica tla u koridoru | kriva etapa |

## Krug {#the-lap}

| Poruka | Učinite |
|---|---|
| `<file> is not a lap this can read. ...` | dajte podržan oblik, vidi [Ulazni podaci kruga](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON nije krug |
| `<file> has no x, y and z columns` | nazovite CSV stupce `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | provjerite ime ili predajte datoteku |
| `'<name>' matches 3 courses: ...` | koristite dulji dio imena |
| `<name> holds no driving` | krug ima manje od dva uzorka |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` treba JSON rute s `bounds`, kakav pišu `heat3d_capture route` i `laps`; datoteka kruga je za `course` |
| `give exactly one of --box and --route` | `terrain` treba jedno područje |
| `no course export for this lap: <reason>.` | igra nije podržana, vidi [Ograničenja i poznati nedostaci](limits-and-known-gaps.md) |

## Arhive {#archives}

| Poruka | Značenje |
|---|---|
| `no Oodle library found. ...` | postavite `HEAT3D_OODLE`, vidi [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | šifrirani pak: `--key <hex>` ako imate ključ. Drugog načina nema |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | ključ su 32 bajta, zapisana kao 64 heksadecimalne znamenke, `0x` opcionalno (izlazni kod 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | nije nijedno od tih; `identify` kaže što jest. Unity spremnik ide kroz `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | šifrirani IoStore spremnik. Ne može se čitati |
| `pak version <n>; this reader handles 8-12` | starija ili novija pak verzija |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | iz Pythona: probajte `.utoc`, koji uzimaju i `list` i `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | IoStore spremnik koji ne imenuje datoteke; do njegovih segmenata se dolazi samo kroz druge pakete |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` pored arhive je iz druge verzije ili druge arhive; bez njega se unosi popisuju po broju |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | imena su hashirana pri izradi |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | Frostbite tablica u zamaskiranom obliku |
| `no Frostbite game found in a Steam library; give --install` | `levels` ili `level` nisu našli Steam igru čiji `Data` sadrži `layout.toc`; predajte mapu igre |
| `no level called '<name>'; did you mean one of ...?` | ime se nije podudaralo ni s jednom tablicom razine, ili se podudaralo s više; `levels` ih popisuje |
| `nothing was placed: no static model group was recognised` | članovi grupa razine imaju drugačiji potpis tipa, nakon nadogradnje igre ili u drugoj Frostbite igri; raspored treba ponovno izmjeriti |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | komprimirana Unity mreža |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | držite `.resS` pored `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | starija Unity verzija |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` uzima goli spremnik |
| `texture format <n> has not been identified; refusing to guess` | Forza format uzorka još nije viđen |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | držite dijelove podijeljenog VPK-a zajedno |

## Izvozi koji ispadnu krivo {#exports-that-come-out-wrong}

| Simptom | Vjerojatni uzrok |
|---|---|
| staza je pomaknuta u odnosu na krug u pregledniku | krug i izvoz koriste različite okvire: provjerite `--game` (na primjer BeamNG krug čitan kao Forza) |
| nema ruba u Forza stazi | `--no-textures`, ili pločica nije imala karte za taj `--season` (konzola ispisuje `N without maps`) |
| Forza pločica u jednolikim bojama | njezine karte tla nedostaju za to godišnje doba |
| znatno manje postavljenih objekata nego što se očekuje | eksplicitan `--detail-budget` premalen; sažetak kaže koliko je primjeraka izostavljeno |
| datoteka je vrlo velika (stotine MB) | gradski koridor pod automatskim proračunom; upotrijebite `--detail-budget`, `--texture-size 1024` ili `--margin 40` |
| nedostaju ograde | prozirne površine se namjerno izostavljaju (sažetak ih imenuje) |
| `N meshes could not be read` | neki modeli koriste format koji čitač odbija; ostatak se izvozi |
| `N of M components could not be read` (AC Rally) | zakrpa igre je možda pomaknula mjesta svojstava; javite to |
