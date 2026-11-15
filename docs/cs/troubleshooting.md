---
title: Řešení potíží
nav_order: 11
lang: "cs"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Řešení potíží {#troubleshooting}

Zprávy, které nástroj vypíše, když ho něco zastaví, co každá znamená a co dělat.
Zprávy jsou citovány z kódu, s zástupnými údaji v lomených závorkách.

## Dříve, než nástroj vůbec začne {#before-the-tool-even-starts}

| Vidíte | Udělejte |
|---|---|
| `'python' is not recognized` | nainstalujte Python 3.10 nebo novější a zaškrtněte "Add python.exe to PATH"; otevřete nový terminál ([Než začnete](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminál je ve špatné složce: `cd` do složky s `README.md` |
| `No module named numpy` (nebo jiný balíček) | spusťte `pip install -r requirements.txt` |
| cesta s mezerami je useknutá, nebo `unrecognized arguments` | dejte cestu do uvozovek: `"C:\My Games\lap.json"` |

## Hledání hry {#finding-the-game}

| Zpráva | Význam | Udělejte |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | žádná knihovna Steamu ani `C:\XboxGames` nedrží hru s `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | souřadnice kola nejsou na žádné nainstalované trati | ověřte, že kolo je z této hry; pokud je trať jinde, zadejte `--track` |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | dlaždice jsou blízko boxu, ale žádná nepokrývá koridor | jako výše |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | složka nemá žádný `.utoc`, který by se otevřel | nasměrujte `--install` na složku s soubory `.utoc` |

## Hledání místa {#finding-the-place}

| Zpráva | Význam | Udělejte |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: žádná úroveň nedosáhla 30 % | `--level <name>`; ověřte, že kolo je v soustavě prohlížeče |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` se neshodl | použijte jeden z vypsaných názvů složek |
| `<level> has no scene (no main/*.level.json and no .mis)` | složka úrovně nemá scénové soubory | rozbitá nebo neúplná úroveň, nebo mod |
| `no terrain of <level> lies along the driving.` | BeamNG: koridor nemá žádné čtverce terénu | špatná úroveň, nebo úroveň bez terénu tam, kde je kolo |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: žádná etapa a rámec nedosáhly 50 % | `--level <stage>`; ověřte, že pozice kola jsou metry s y nahoru |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` se neshodl | použijte jeden z vypsaných názvů |
| `no ground of <stage> lies along the driving.` | AC Rally: v koridoru není žádná dlaždice země | špatná etapa |

## Kolo {#the-lap}

| Zpráva | Udělejte |
|---|---|
| `<file> is not a lap this can read. ...` | dejte podporovaný tvar, viz [Vstupy kola](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON není kolo |
| `<file> has no x, y and z columns` | pojmenujte sloupce CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | zkontrolujte název, nebo dejte soubor |
| `'<name>' matches 3 courses: ...` | použijte delší část názvu |
| `<name> holds no driving` | kolo má méně než dva vzorky |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` potřebuje soubor trasy JSON s `bounds`, jaký zapisují `heat3d_capture route` a `laps`; soubor kola je pro `course` |
| `give exactly one of --box and --route` | `terrain` potřebuje jednu oblast |
| `no course export for this lap: <reason>.` | hra není podporovaná, viz [Omezení a známé mezery](limits-and-known-gaps.md) |

## Archivy {#archives}

| Zpráva | Význam |
|---|---|
| `no Oodle library found. ...` | nastavte `HEAT3D_OODLE`, viz [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | šifrovaný pak: `--key <hex>`, pokud klíč máte. Jiná cesta není |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | klíč má 32 bajtů zapsaných jako 64 šestnáctkových číslic, `0x` volitelné (návratový kód 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | není to nic z toho; `identify` řekne, co to je. Kontejner Unity bere `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | šifrovaný kontejner IoStore. Nelze ho přečíst |
| `pak version <n>; this reader handles 8-12` | starší nebo novější formát pak |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | z Pythonu: zkuste `.utoc`, který berou i `list` a `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | kontejner IoStore, který nejmenuje soubory; jeho chunky se dosáhnou jen přes jiné balíčky |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` vedle archivu je z jiného buildu nebo jiného archivu; bez něj se položky vypíšou podle čísla |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | názvy byly při sestavení zahashované |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | tabulka Frostbite v obfuskované formě |
| `no Frostbite game found in a Steam library; give --install` | `levels` nebo `level` nenašly hru Steam, jejíž `Data` drží `layout.toc`; zadejte složku hry |
| `no level called '<name>'; did you mean one of ...?` | název neodpovídá žádné tabulce úrovně, nebo odpovídá více; `levels` je vypíše |
| `nothing was placed: no static model group was recognised` | členové skupin úrovně mají jiný podpis typu, po aktualizaci hry nebo v jiné hře Frostbite; rozložení se musí znovu změřit |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | komprimovaná síť Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | nechte `.resS` vedle `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | starší build Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` bere holý kontejner |
| `texture format <n> has not been identified; refusing to guess` | formát vzorníku Forzy, který ještě nebyl vidět |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | držte části rozděleného VPK pohromadě |

## Exporty, které vyjdou špatně {#exports-that-come-out-wrong}

| Příznak | Pravděpodobná příčina |
|---|---|
| trať je od kola v prohlížeči posunutá | kolo a export používají jiné soustavy: zkontrolujte `--game` (například kolo BeamNG čtené jako Forza) |
| žádná krajnice ve trati Forzy | `--no-textures`, nebo dlaždice neměla mapy pro dané `--season` (konzole napíše `N without maps`) |
| dlaždice Forzy v plochých barvách | její mapy země chybí pro dané roční období |
| výrazně méně umístěných objektů, než se čeká | zadaný `--detail-budget` je příliš malý; shrnutí řekne, kolik kopií se vynechalo |
| soubor je velmi velký (stovky MB) | městský koridor s automatickým rozpočtem; použijte `--detail-budget`, `--texture-size 1024`, nebo `--margin 40` |
| chybí ploty | průhledné povrchy se záměrně vynechávají (shrnutí je pojmenuje) |
| `N meshes could not be read` | některé modely používají formát, který čtečka odmítá; zbytek se exportuje |
| `N of M components could not be read` (AC Rally) | oprava hry mohla posunout sloty vlastností; nahlaste to, prosím |
