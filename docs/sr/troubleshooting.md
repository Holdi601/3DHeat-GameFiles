---
title: Решавање проблема
nav_order: 11
lang: "sr"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Решавање проблема {#troubleshooting}

Поруке које алат исписује кад нешто заустави, шта свака значи и шта да урадите. Поруке су наведене из кода, са местима у угластим заградама.

## Пре него што алат уопште почне {#before-the-tool-even-starts}

| Видите | Урадите |
|---|---|
| `'python' is not recognized` | инсталирајте Python 3.10 или новији и штиклирајте „Add python.exe to PATH“; отворите нови терминал ([Пре почетка](before-you-start.md)) |
| `No module named heat3d_gamefiles` | терминал је у погрешној фасцикли: `cd` до фасцикле са `README.md` |
| `No module named numpy` (или други пакет) | покрените `pip install -r requirements.txt` |
| путања са размацима је пресечена, или `unrecognized arguments` | ставите путању под двоструке наводнике: `"C:\My Games\lap.json"` |

## Налажење игре {#finding-the-game}

| Порука | Значење | Урадите |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | ниједна Steam библиотека или `C:\XboxGames` не садржи игру са `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | координате круга нису ни на једној инсталираној стази | проверите да је круг из ове игре; проследите `--track` ако је стаза негде другде |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | плочице постоје у близини кутије, али ниједна не покрива вожњу у коридору | као горе |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | фасцикла нема `.utoc` који се отвара | усмерите `--install` на фасциклу са `.utoc` фајловима |

## Налажење места {#finding-the-place}

| Порука | Значење | Урадите |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: ниједан ниво није постигао 30% | `--level <name>`; проверите да је круг у оквиру приказивача |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` се није поклопио | користите један од набројаних назива фасцикли |
| `<level> has no scene (no main/*.level.json and no .mis)` | фасцикла нивоа нема фајлове сцене | покварен или непотпун ниво, или модификација |
| `no terrain of <level> lies along the driving.` | BeamNG: коридор нема квадрате терена | погрешан ниво, или ниво без терена тамо где је круг |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: ниједна деоница и кадар није постигла 50% | `--level <stage>`; проверите да су положаји круга метри са y нагоре |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` се није поклопио | користите један од набројаних назива |
| `no ground of <stage> lies along the driving.` | AC Rally: ниједна плочица тла у коридору | погрешна деоница |

## Круг {#the-lap}

| Порука | Урадите |
|---|---|
| `<file> is not a lap this can read. ...` | дајте подржан облик, видите [Улазни подаци круга](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | тај JSON није круг |
| `<file> has no x, y and z columns` | назовите CSV колоне `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | проверите назив, или дајте фајл |
| `'<name>' matches 3 courses: ...` | користите дужи део назива |
| `<name> holds no driving` | круг има мање од два узорка |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` треба JSON руте са `bounds`, као што га пишу `heat3d_capture route` и `laps`; фајл круга је за `course` |
| `give exactly one of --box and --route` | `terrain` треба један регион |
| `no course export for this lap: <reason>.` | игра није подржана, видите [Ограничења и познати недостаци](limits-and-known-gaps.md) |

## Архиве {#archives}

| Порука | Значење |
|---|---|
| `no Oodle library found. ...` | поставите `HEAT3D_OODLE`, видите [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | шифровани pak: `--key <hex>` ако имате кључ. Другог начина нема |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | кључ је 32 бајта, записан као 64 хекс цифре, `0x` опционо (излазни код 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | није ниједан од њих; `identify` каже шта јесте. Unity контејнер узима `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | шифрован IoStore контејнер. Не може да се прочита |
| `pak version <n>; this reader handles 8-12` | старији или новији pak формат |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | из Python-а: пробајте `.utoc`, који узимају и `list` и `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | IoStore контејнер који не именује фајлове; до његових блокова се долази само кроз друге пакете |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` поред архиве је из друге градње или друге архиве; без њега се уноси исписују по броју |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | називи су хеширани при градњи |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | Frostbite табела у обфусцираном облику |
| `no Frostbite game found in a Steam library; give --install` | `levels` или `level` нису нашли Steam игру чији `Data` има `layout.toc`; дајте фасциклу игре |
| `no level called '<name>'; did you mean one of ...?` | назив се није поклопио ни са једном табелом нивоа, или се поклопио са више њих; `levels` их исписује |
| `nothing was placed: no static model group was recognised` | чланови групе нивоа имају другачији потпис типова, после ажурирања игре или у другој Frostbite игри; распоред треба поново измерити |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | компресована Unity мрежа |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | држите `.resS` поред `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | старија Unity верзија |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` узима голи контејнер |
| `texture format <n> has not been identified; refusing to guess` | Forza формат узорка који још није виђен |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | држите делове раздељеног VPK-а заједно |

## Извози који испадну погрешно {#exports-that-come-out-wrong}

| Симптом | Вероватни узрок |
|---|---|
| стаза је померена у односу на круг у приказивачу | круг и извоз користе различите оквире: проверите `--game` (BeamNG круг прочитан као Forza, на пример) |
| нема банкине у Forza стази | `--no-textures`, или плочица нема мапе за тај `--season` (конзола исписује `N without maps`) |
| Forza плочица у равним бојама | њене мапе тла недостају за то доба године |
| далеко мање постављених објеката него што очекујете | експлицитан `--detail-budget` премали; резиме каже колико копија је изостављено |
| датотека је веома велика (стотине MB) | градски коридор под аутоматским буџетом; користите `--detail-budget`, `--texture-size 1024` или `--margin 40` |
| недостају ограде | провидне површине се намерно изостављају (резиме их именује) |
| `N meshes could not be read` | неки модели користе формат који читач одбија; остатак се ипак извози |
| `N of M components could not be read` (AC Rally) | закрпа игре можда је померила слотове особина; јавите то |
