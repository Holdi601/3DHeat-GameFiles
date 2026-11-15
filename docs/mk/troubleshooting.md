---
title: "Отстранување проблеми"
nav_order: 11
lang: "mk"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Отстранување проблеми {#troubleshooting}

Пораките што ги печати алатката кога нешто ќе ја запре, што значи секоја, и што да
направите. Пораките се цитирани од кодот, со местозаменувачи во аглести загради.

## Пред алатката воопшто да почне {#before-the-tool-even-starts}

| Гледате | Направете |
|---|---|
| `'python' is not recognized` | инсталирајте Python 3.10 или понов и штиклирајте „Add python.exe to PATH“; отворете нов терминал ([Пред да започнете](before-you-start.md)) |
| `No module named heat3d_gamefiles` | терминалот е во погрешна папка: `cd` до папката со `README.md` |
| `No module named numpy` (или друг пакет) | извршете `pip install -r requirements.txt` |
| патека со празни места е пресечена, или `unrecognized arguments` | ставете ја патеката во двојни наводници: `"C:\My Games\lap.json"` |

## Наоѓање на играта {#finding-the-game}

| Порака | Значење | Направете |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | ниту една Steam библиотека или `C:\XboxGames` не држи игра со `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | координатите на кругот не се на ниту една инсталирана патека | проверете дали кругот е од оваа игра; зададете `--track` ако патеката е на друго место |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | има плочки близу кутијата но ниту една во коридорот | како погоре |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | папката нема `.utoc` што се отвора | упатете `--install` на папката со датотеките `.utoc` |

## Наоѓање на местото {#finding-the-place}

| Порака | Значење | Направете |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: ниту едно ниво не добило 30% | `--level <name>`; проверете дали кругот е во рамката на прегледувачот |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` не се совпадна | користете едно од наведените имиња на папки |
| `<level> has no scene (no main/*.level.json and no .mis)` | папката на нивото нема датотеки на сцена | расипано или делумно ниво или мод |
| `no terrain of <level> lies along the driving.` | BeamNG: коридорот нема квадрати на терен | погрешно ниво, или ниво без терен таму каде што е кругот |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: ниту една етапа и рамка не добила 50% | `--level <stage>`; проверете дали позициите на кругот се метри со y нагоре |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` не се совпадна | користете едно од наведените имиња |
| `no ground of <stage> lies along the driving.` | AC Rally: нема плочка на земја во коридорот | погрешна етапа |

## Кругот {#the-lap}

| Порака | Направете |
|---|---|
| `<file> is not a lap this can read. ...` | дајте му поддржан облик, видете [Влезови за круг](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON-от не е круг |
| `<file> has no x, y and z columns` | именувајте ги колоните на CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | проверете го името, или дајте датотека |
| `'<name>' matches 3 courses: ...` | користете подолг дел од името |
| `<name> holds no driving` | кругот има помалку од два примероци |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` бара JSON на рута со `bounds`, како што го пишуваат `heat3d_capture route` и `laps`; датотеката на круг е за `course` |
| `give exactly one of --box and --route` | `terrain` бара еден регион |
| `no course export for this lap: <reason>.` | играта не е поддржана, видете [Ограничувања и познати празнини](limits-and-known-gaps.md) |

## Архиви {#archives}

| Порака | Значење |
|---|---|
| `no Oodle library found. ...` | поставете `HEAT3D_OODLE`, видете [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | шифриран pak: `--key <hex>` ако го имате клучот. Нема друг начин |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | клучот е 32 бајти запишани како 64 хекс цифри, `0x` по избор (излезен код 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | не е ништо од тоа; `identify` кажува што е. Контејнер на Unity зема `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | шифриран IoStore контејнер. Не може да се прочита |
| `pak version <n>; this reader handles 8-12` | постар или понов формат на pak |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | од Python: пробајте `.utoc`, кој го земаат и `list` и `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | IoStore контејнер што не именува датотеки; до неговите делови се стига само преку други пакети |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` до архивата е од друга градба или друга архива; без него записите се наведуваат по број |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | имињата биле хеширани при градењето |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | табела на Frostbite во замаглена форма |
| `no Frostbite game found in a Steam library; give --install` | `levels` или `level` не нашле Steam игра чиј `Data` држи `layout.toc`; зададете ја папката на играта |
| `no level called '<name>'; did you mean one of ...?` | името не се совпадна со табелата на ниту едно ниво, или се совпадна со неколку; `levels` ги наведува |
| `nothing was placed: no static model group was recognised` | членовите на групите на нивото имаат друг потпис на тип, по ажурирање на играта или во друга игра на Frostbite; распоредот мора повторно да се измери |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | компресирана мрежа на Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | чувајте ја `.resS` до `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | постара градба на Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` зема гол контејнер |
| `texture format <n> has not been identified; refusing to guess` | формат на примерок на Forza што сè уште не е виден |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | чувајте ги деловите на поделен VPK заедно |

## Извози што излегуваат погрешни {#exports-that-come-out-wrong}

| Симптом | Веројатна причина |
|---|---|
| патеката е поместена од кругот во прегледувачот | кругот и извозот користат различни рамки: проверете `--game` (на пример круг на BeamNG прочитан како Forza) |
| нема банкина во патека од Forza | `--no-textures`, или плочката немала мапи за тој `--season` (конзолата вели `N without maps`) |
| плочка на Forza во рамни бои | недостасуваат нејзините мапи на земја за сезоната |
| многу помалку поставени објекти од очекуваното | експлицитен `--detail-budget` премал; резимето кажува колку копии се изоставени |
| датотеката е многу голема (стотици MB) | градски коридор под автоматскиот буџет; користете `--detail-budget`, `--texture-size 1024`, или `--margin 40` |
| недостасуваат огради | површините низ кои се гледа се изоставени намерно (резимето ги именува) |
| `N meshes could not be read` | некои модели користат формат што читачот го одбива; остатокот сепак се извезува |
| `N of M components could not be read` (AC Rally) | закрпа на играта можеби ги поместила слотовите на својствата; пријавете го |
