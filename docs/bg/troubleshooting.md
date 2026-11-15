---
title: "Отстраняване на проблеми"
nav_order: 11
lang: "bg"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Отстраняване на проблеми {#troubleshooting}

Съобщенията, които инструментът извежда, когато нещо го спре, какво значи всяко и какво да направиш. Съобщенията са цитирани от кода, с местодържатели в ъглови скоби.

## Преди инструментът изобщо да стартира {#before-the-tool-even-starts}

| Виждате | Направете |
|---|---|
| `'python' is not recognized` | инсталирайте Python 3.10 или по-нов и отметнете „Add python.exe to PATH“; отворете нов терминал ([Преди да започнете](before-you-start.md)) |
| `No module named heat3d_gamefiles` | терминалът е в грешната папка: `cd` до папката с `README.md` |
| `No module named numpy` (или друг пакет) | пуснете `pip install -r requirements.txt` |
| път с интервали е отрязан или `unrecognized arguments` | сложете пътя в двойни кавички: `"C:\My Games\lap.json"` |

## Намиране на играта {#finding-the-game}

| Съобщение | Значение | Направете |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | нито една библиотека на Steam или `C:\XboxGames` не държи игра с `media\Tracks` | `--track "<игра>\media\Tracks\<карта>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | координатите на обиколката не са на нито едно инсталирано трасе | проверете дали обиколката е от тази игра; дайте `--track`, ако трасето е другаде |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | има плочки близо до кутията, но нито една, която да покрива шофирането в коридора | както по-горе |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<папка с gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<папка на играта>"` |
| `no readable IoStore containers in <folder>` | папката няма `.utoc`, който да се отваря | насочи `--install` към папката с файловете `.utoc` |

## Намиране на мястото {#finding-the-place}

| Съобщение | Значение | Направете |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: нито едно ниво не е събрало 30% | `--level <име>`; проверете дали обиколката е във рамката на визуализатора |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` не съвпадна | използвайте едно от изброените имена на папки |
| `<level> has no scene (no main/*.level.json and no .mis)` | папката на нивото няма файлове на сцената | счупено или непълно ниво или модификация |
| `no terrain of <level> lies along the driving.` | BeamNG: коридорът няма квадрати от терен | грешно ниво или ниво без терен там, където е обиколката |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: никой етап и рамка не са събрали 50% | `--level <етап>`; проверете дали позициите на обиколката са в метри с Y нагоре |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` не съвпадна | използвайте едно от изброените имена |
| `no ground of <stage> lies along the driving.` | AC Rally: няма плочка от земята в коридора | грешен етап |

## Обиколката {#the-lap}

| Съобщение | Направете |
|---|---|
| `<file> is not a lap this can read. ...` | дайте поддържана форма, вижте [Входни данни за обиколка](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON файлът не е обиколка |
| `<file> has no x, y and z columns` | назовете колоните в CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | проверете името или дайте файл |
| `'<name>' matches 3 courses: ...` | използвайте по-дълга част от името |
| `<name> holds no driving` | обиколката има по-малко от две точки |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` иска JSON маршрут с `bounds`, както го записват `heat3d_capture route` и `laps`; файлът с обиколка е за `course` |
| `give exactly one of --box and --route` | `terrain` иска един регион |
| `no course export for this lap: <reason>.` | играта не се поддържа, вижте [Ограничения и известни пропуски](limits-and-known-gaps.md) |

## Архивите {#archives}

| Съобщение | Значение |
|---|---|
| `no Oodle library found. ...` | задайте `HEAT3D_OODLE`, вижте [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | криптиран pak: `--key <hex>`, ако държите ключа. Друг начин няма |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | ключът е 32 байта, записани като 64 шестнадесетични цифри, `0x` по избор (код за изход 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | файлът не е нито един от тях; `identify` казва какво е. Контейнер на Unity се подава на `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | криптиран контейнер IoStore. Не може да се чете |
| `pak version <n>; this reader handles 8-12` | по-стар или по-нов формат на pak |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | от Python: пробвайте `.utoc`, който също приемат `list` и `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | контейнер IoStore, който не назовава файлове; до чанковете му се стига само през други пакети |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | `ChunkContentsMiniZip<n>.txt` до архива е от друг билд или друг архив; без него записите се изброяват по номер |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | имената са хеширани при билдване |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | таблица на Frostbite в обфусцираната форма |
| `no Frostbite game found in a Steam library; give --install` | `levels` или `level` не намериха игра в Steam, чиято `Data` съдържа `layout.toc`; дайте папката на играта |
| `no level called '<name>'; did you mean one of ...?` | името не съвпадна с таблица на ниво или съвпадна с няколко; `levels` ги изброява |
| `nothing was placed: no static model group was recognised` | членовете на групите на нивото имат различна сигнатура на типа, след обновление на играта или в друга игра на Frostbite; оформлението трябва да се измери отново |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | компресирана мрежа на Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | дръжте `.resS` до `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | по-стар билд на Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` приема гол контейнер |
| `texture format <n> has not been identified; refusing to guess` | формат на образец от Forza, който още не е виждан |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | дръжте частите на разделен VPK заедно |

## Експорти, които излизат грешни {#exports-that-come-out-wrong}

| Симптом | Вероятна причина |
|---|---|
| трасето е изместено спрямо обиколката във визуализатора | обиколката и експортът ползват различни рамки: проверете `--game` (например обиколка на BeamNG, прочетена като Forza) |
| няма банкет на трасе на Forza | `--no-textures` или плочката няма карти за този `--season` (конзолата казва `N without maps`) |
| плочка на Forza в плоски цветове | картите на земята ѝ липсват за сезона |
| много по-малко разположени обекти, отколкото се очаква | зададен изрично `--detail-budget` е твърде малък; обобщението казва колко копия са пропуснати |
| файлът е много голям (стотици MB) | градски коридор при автоматичния бюджет; използвайте `--detail-budget`, `--texture-size 1024` или `--margin 40` |
| липсват огради | прозрачните повърхности се пропускат нарочно (обобщението ги назовава) |
| `N meshes could not be read` | някои модели ползват формат, който четецът отхвърля; останалото се експортира |
| `N of M components could not be read` (AC Rally) | кръпка на играта може да е преместила слотовете на свойствата; моля, докладвай го |
