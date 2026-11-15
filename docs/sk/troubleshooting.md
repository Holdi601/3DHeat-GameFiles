---
title: Riešenie problémov
nav_order: 11
lang: "sk"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Riešenie problémov {#troubleshooting}

Hlásenia, ktoré nástroj vypíše, keď sa niečo zastaví, čo každé znamená a čo robiť.
Hlásenia sú citované z kódu, s miestami v lomených zátvorkách pre premenné.

## Ešte predtým, ako nástroj začne {#before-the-tool-even-starts}

| Vidíte | Urobte |
|---|---|
| `'python' is not recognized` | nainštalujte Python 3.10 alebo novší a zaškrtnite „Add python.exe to PATH“; otvorte nový terminál ([Pred začiatkom](before-you-start.md)) |
| `No module named heat3d_gamefiles` | terminál je v zlom priečinku: `cd` do priečinka s `README.md` |
| `No module named numpy` (alebo iný balík) | spustite `pip install -r requirements.txt` |
| cesta s medzerami je useknutá, alebo `unrecognized arguments` | dajte cestu do dvojitých úvodzoviek: `"C:\My Games\lap.json"` |

## Hľadanie hry {#finding-the-game}

| Hlásenie | Význam | Čo urobiť |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | žiadna knižnica Steam ani `C:\XboxGames` neobsahuje hru s `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | súradnice kola nie sú na žiadnej nainštalovanej trati | skontrolujte, že kolo je z tejto hry; ak je trať inde, zadajte `--track` |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | dlaždice existujú blízko boxu, ale žiadna nepokrýva koridor | ako vyššie |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | priečinok nemá žiadny `.utoc`, ktorý sa dá otvoriť | nasmerujte `--install` na priečinok so súbormi `.utoc` |

## Hľadanie miesta {#finding-the-place}

| Hlásenie | Význam | Čo urobiť |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: žiadny level nedosiahol 30 % | `--level <name>`; skontrolujte, že kolo je v rámci prehliadača |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` sa nezhodoval | použite jeden z vypísaných názvov priečinkov |
| `<level> has no scene (no main/*.level.json and no .mis)` | priečinok levelu nemá scénové súbory | poškodený alebo neúplný level, alebo mod |
| `no terrain of <level> lies along the driving.` | BeamNG: koridor nemá žiadne štvorce terénu | zlý level, alebo level bez terénu tam, kde je kolo |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: žiadna etapa a rámec nedosiahli 50 % | `--level <stage>`; skontrolujte, že pozície kola sú v metroch s Y hore |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` sa nezhodoval | použite jeden z vypísaných názvov |
| `no ground of <stage> lies along the driving.` | AC Rally: v koridore nie je žiadna dlaždica povrchu | zlá etapa |

## Kolo {#the-lap}

| Hlásenie | Čo urobiť |
|---|---|
| `<file> is not a lap this can read. ...` | dajte podporovaný tvar, pozri [Vstupy kola](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON nie je kolo |
| `<file> has no x, y and z columns` | pomenujte stĺpce CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | skontrolujte názov, alebo dajte súbor |
| `'<name>' matches 3 courses: ...` | použite dlhšiu časť názvu |
| `<name> holds no driving` | kolo má menej ako dve vzorky |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` potrebuje JSON trasy s `bounds`, ako ho zapisujú `heat3d_capture route` a `laps`; súbor kola patrí do `course` |
| `give exactly one of --box and --route` | `terrain` potrebuje jednu oblasť |
| `no course export for this lap: <reason>.` | hra nie je podporovaná, pozri [Obmedzenia a známe medzery](limits-and-known-gaps.md) |

## Archívy {#archives}

| Hlásenie | Význam |
|---|---|
| `no Oodle library found. ...` | nastavte `HEAT3D_OODLE`, pozri [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | šifrovaný pak: `--key <hex>`, ak máte kľúč. Iná cesta neexistuje |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | kľúč sú 32 bajty zapísané ako 64 hexadecimálnych číslic, `0x` voliteľné (návratový kód 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | nie je to žiadny z nich; `identify` povie, čo to je. Kontajner Unity berie `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | šifrovaný kontajner IoStore. Nedá sa prečítať |
| `pak version <n>; this reader handles 8-12` | starší alebo novší formát pak |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | z Pythonu: skúste `.utoc`, ktorý berú aj `list` a `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | kontajner IoStore, ktorý nepomenúva súbory; jeho chunky sa dosiahnu len cez iné balíky |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` vedľa archívu je z iného buildu alebo iného archívu; bez neho sa položky vypíšu podľa čísla |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | názvy boli pri zostavovaní zahashované |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | tabuľka Frostbite v obfuskovanej forme |
| `no Frostbite game found in a Steam library; give --install` | `levels` alebo `level` nenašli hru Steam, ktorej `Data` obsahuje `layout.toc`; zadajte priečinok hry |
| `no level called '<name>'; did you mean one of ...?` | názov sa nezhodoval so žiadnou tabuľkou levelu, alebo sa zhodoval s viacerými; `levels` ich vypíše |
| `nothing was placed: no static model group was recognised` | podpis typu členov skupiny levelu sa líši, po aktualizácii hry alebo v inej hre Frostbite; rozloženie sa musí zmerať znova |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | komprimovaná sieť Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | nechajte `.resS` vedľa `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | staršia verzia Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` berie holý kontajner |
| `texture format <n> has not been identified; refusing to guess` | formát vzorníka Forza, ktorý ešte nebol videný |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | ponechajte časti rozdeleného VPK pohromade |

## Exporty, ktoré vyjdu zle {#exports-that-come-out-wrong}

| Príznak | Pravdepodobná príčina |
|---|---|
| trať je v prehliadači posunutá oproti kolu | kolo a export používajú iné rámce: skontrolujte `--game` (napríklad kolo BeamNG čítané ako Forza) |
| v trati Forza nie je krajnica | `--no-textures`, alebo dlaždica nemala mapy pre dané `--season` (konzola hlási `N without maps`) |
| dlaždica Forza v plošných farbách | jej mapy povrchu chýbajú pre ročné obdobie |
| výrazne menej umiestnených objektov, než sa čakalo | zadaný `--detail-budget` je príliš malý; súhrn povie, koľko kópií sa vynechalo |
| súbor je veľmi veľký (stovky MB) | mestský koridor pri automatickom rozpočte; použite `--detail-budget`, `--texture-size 1024` alebo `--margin 40` |
| chýbajú ploty | priehľadné plochy sa vynechávajú zámerne (súhrn ich pomenuje) |
| `N meshes could not be read` | niektoré modely používajú formát, ktorý čítačka odmieta; zvyšok sa exportuje |
| `N of M components could not be read` (AC Rally) | záplata hry mohla posunúť sloty vlastností; prosím nahláste to |
