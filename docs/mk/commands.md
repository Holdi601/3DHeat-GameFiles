---
title: "Команди"
nav_order: 2
lang: "mk"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Команди {#commands}

Секоја команда се извршува како `python -m heat3d_gamefiles <verb> ...` од папката на
складиштето. Глаголите се по редот по кој обично ви требаат: што е оваа датотека, што има
во неа, дај ми го тоа и претвори круг во патека.

| Глагол | Прима | Прави |
|---|---|---|
| [`identify`](#identify) | која било датотека | го именува форматот на контејнерот со читање на нејзините бајти |
| [`list`](#list) | Unreal `.pak` или IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` или zip | ги наведува неговите ставки |
| [`extract`](#extract) | истото | запишува една ставка на диск |
| [`meshes`](#meshes) | Unity `SerializedFile` | ги наведува и проверува неговите мрежи (mesh) |
| [`course`](#course) | круг | ја извезува патеката околу него (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | снимена библиотека на кругови | го извршува `course` на секоја патека во неа (Forza) |
| [`races`](#races) | инсталиран Forza | ги наведува сите трки што ги дефинира играта: што додаваат, што кријат, местата, состојбата на нивниот извоз |
| [`terrain`](#terrain) | папка на патека од Forza | сече област по светски координати |
| [`levels`](#levels-and-level-frostbite) | инсталирана игра со Frostbite (Battlefield 6) | ги наведува нејзините нивоа |
| [`level`](#levels-and-level-frostbite) | име на ниво | го извезува нивото: терен, поставени мрежи, по избор и нивните мапи на бои (Battlefield 6) |
| [`cars`](#cars) | инсталиран Forza | секој автомобил со ниска детаљност, во една датотека за табот Анализа на трка на прегледувачот |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | игра со Unreal 5 | ги наведува нејзините мапи со World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | име на мапа | ја извезува мапата: пејзаж, HLOD структури, вода |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | инсталиран Arma Reforger | ги наведува неговите светови |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | име на свет | го извезува светот: терен во своите бои, морето, зградите како кутии |

**Читање на примерите:** `<x>` значи заменете го со ваша вредност, без аглестите
загради; `[...]` е по избор; патека со празни места ставете ја во „двојни наводници“,
на пример `"C:\Games\My Game"`. Нови сте во ова? Видете [Пред да започнете](before-you-start.md).
Целиот `--help` на секој глагол е на [Упатството за команди](../cli-reference.md).

Секој пат кога програмата ќе се стартува, може прво да провери за понова верзија. Видете
[Ажурирања](updates.md). `HEAT3D_NO_UPDATE=1` ја исклучува таа проверка.

Извор: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Страници чекор по чекор: [Преглед на архиви](inspecting-archives.md), [Извоз на патека](course-export.md),
[Цели нивоа](whole-levels.md), [Автомобили од Forza](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Излезни кодови {#exit-codes}

| Код | Значење |
|---|---|
| 0 | успех |
| 1 | работата не успеа (нечитлив круг, не е пронајдена игра, нема што да се извезе, патека во `courses` не успеа; за `list` и `extract`: датотека што не е ниту една од архивите што ги читаат, една што не може да се отвори или прочита - шифриран pak без `--key`, шифриран IoStore контејнер - или ставка што ја нема во архивата) |
| 2 | лоши аргументи (argparse), патека што не постои, `--key` што не е 64 хексадецимални цифри, или `terrain` добил и двете или ниту една од `--box` и `--route` |

Неуспесите на `list` и `extract` се по една линија на стандардниот излез за грешки, а не
Python traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Ја чита датотеката и вели кој контејнер е. Не се потпира на
наставката (единствен исклучок е `.ucas`, подолу). Ги пробува форматите по овој
редослед и запира на првиот што се чита:

1. **Unreal `.pak`**: подножје со pak магијата во последните 1.024 бајти. Печати
   верзија, поместување и големина на индексот, дали индексот е шифриран и
   методите на компресија.
2. **Unreal IoStore `.utoc`**: IoStore магијата на почетокот. Печати верзија,
   бројот на делови (chunk) и дали контејнерот е шифриран; за оној што не е,
   бројот на датотеки што ги именува неговиот директориум (и под која точка на монтирање),
   методите на компресија и дали неговиот `.ucas` е покрај него. `.ucas` нема
   сопствено заглавие, па се препознава по `.utoc` со исто име покрај него,
   а `identify` ја именува таа датотека.
3. **ForzaTech `.minizip`**: магијата `PGZP`. Печати верзија, бројот на ставки и
   сегменти и дали `ChunkContentsMiniZip<n>.txt` што ги именува ставките
   е покрај него (и ако е, дали именува толку колку што има).
4. **zip**: локално заглавие на zip датотека на почетокот. Печати бројот на ставки,
   шесте најчести наставки и имињата на нивоата кога ставки лежат под
   `levels/<name>/`, како во архива на ниво на BeamNG.drive.
5. **Unity**: пакет `UnityFS` (печати верзија на engine-от и број на ставки) или
   гол `SerializedFile` (печати форматот, верзијата на engine-от, бројот на објекти и
   шесте најчести класи).
6. **Frostbite `.toc`**: печати видот (`plain` или `signed`), каде започнува
   дрвото и или бројот на средства (бинарна табела на секции) или бројот
   на суперпакети (DbObject дрво).
7. **Source 2 `.vpk`**: печати верзија, бројот на ставки и првата `.nav`
   навигациска мрежа ако ја има архивата.
8. **BeamNG `.cdae`**: верзија на облик 31 што се чита. Печати бројот на мрежи,
   бројот на цртани нивоа на детаљност и првите материјали.
9. **BeamNG `.ter`**: нема магија, па сè мора да се совпадне - страна од 2
   до 16.384, толку на квадрат височини и бајти за слоеви, па 1 до 255 печатливи
   имиња на слоеви. Печати верзија, големина и имињата на слоевите.
10. **ForzaTech `.modelbin`**: печати верзија, бројот на делови и шесте
    најчести ознаки на делови. Содржината на деловите овде не се декодира.

Форматите со своја магија (2 до 4) доаѓаат пред Unity и Frostbite,
чии проверки ја читаат целата датотека: архива на Forza е десетици гигабајти.

Ако ниту еден не се совпадне, печати `not a format this tool reads` и последната
причина. Таа причина доаѓа од проверката за ForzaTech.

Пример (синтетички):

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

| Опција | Основно | Значење |
|---|---|---|
| `<archive>` | задолжително | Unreal `.pak`; IoStore `.utoc` (или `.ucas` покрај него); Source 2 `.vpk` (за поделени VPK, `_dir.vpk`); ForzaTech `.minizip`; zip, како архивите на нивоа и содржина на BeamNG |
| `--filter TEXT` | нема | само патеки што го содржат TEXT, без разлика на големи и мали букви |
| `--limit N` | 50 | печати најмногу N ставки (вкупниот број секогаш се печати) |
| `--key HEX` | нема | AES-256 клуч што веќе го имате, 64 хексадецимални цифри, со или без `0x`. Само шифриран `.pak` го користи. Сè што не е 64 хексадецимални цифри се одбива пред да се отвори архивата (излезен код 2) |

Алатката го одредува форматот од бајтите: IoStore табела на содржини, `.minizip` и VPK
по потписот со кој започнуваат, zip по неговото локално заглавие, а `.pak` по
подножјето на својот крај. `.ucas` нема заглавие и се отвора преку `.utoc` со исто име.
Датотека што не е ништо од ова се одбива со
`<file> is not an archive list and extract read (...)`. Онаа што е, но
не може да се отвори, се одбива со причината на читачот: шифриран pak без
`--key`, шифриран IoStore контејнер, верзија на pak што не ја чита. Во секој случај
тоа е една линија и излезен код 1.

Секоја линија ја прикажува некомпресираната големина, методот на компресија и патеката:

| Архива | Метод | Патеки |
|---|---|---|
| `.pak` | `none`, или името од подножјето (`Zlib`, `Oodle`, `Gzip`...) | со точката на монтирање на архивата, на пример `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, или методот на контејнерот (`Oodle`, `Zlib`...), онака како е зачуван неговиот прв блок | со точката на монтирање, на пример `../../../<Project>/Content/...`. Контејнер без индекс на директориум не именува датотеки и се одбива |
| `.vpk` | секогаш `stored` | како во директориумот |
| `.minizip` | `lz4`, `deflate` или `stored` | како што ги пишува `ChunkContentsMiniZip<n>.txt` покрај `GeoChunk<n>.minizip`, со отстранет префикс на машината за градење (обратни коси црти, како што ги пишува играта). Архивата не чува имиња, па без таа датотека ставките се `#0`, `#1`... Список чиј број на линии се разликува од ставките се одбива: двете не си припаѓаат |
| zip | `stored`, `deflate`, ... | како што се зачувани; папките не се наведуваат |

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

| Опција | Основно | Значење |
|---|---|---|
| `<archive>` | задолжително | како за `list` |
| `<entry>` | задолжително | патеката точно како што ја печати `list` (разликува големи и мали букви); во `.minizip` работи и `#<number>` |
| `--out FILE` | името на датотеката на ставката (по последното `/` или `\`), во тековната папка | каде да се запише; родителските папки се создаваат |
| `--key HEX` | нема | како за `list` |

Ставката се дешифрира (pak, со клуч), се декомпресира и се запишува. Печати
`<bytes> bytes -> <file>`. Ако патеката ја нема во архивата, командата излегува
со код 1. Истото важи за ставка што не може да се прочита (шифрирана ставка без
клуч, компресирана со Oodle без Oodle библиотека), со причината во една линија. Ставка од VPK овде не се проверува со неговиот CRC. Читачот има
метод `verify()` за тоа (видете [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Опција | Основно | Значење |
|---|---|---|
| `<path>` | задолжително | гол Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), не пакет |
| `--limit N` | 25 | декодира и печати најмногу N мрежи |

Ова го печати бројот на објекти `Mesh`, па една линија по мрежа: името (првите
40 знаци), бројот на темиња и триаголници, и `ok` или `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` значи дека декодираните темиња не ја репродуцираат граничната кутија
што Unity ја зачувал за мрежата, во рамки на 2% од големината на кутијата. Тоа е
сопствената проверка на парсирањето (видете [Unity](reader-unity.md)). Мрежа што не може да се прочита се пријавува
со причината и се брои кон ограничувањето. Податоците за темињата во `.resS` датотека се читаат
од папката во која е контејнерот.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Ја извезува патеката околу еден круг: теренот во појас од двете страни на
возењето и она што стои на него, како еден `.glb`. Остатокот го одредува сама: која
игра, која инсталирана копија, која патека, ниво или етапа и (за Assetto Corsa
Rally) на која страна се оските. Видете [Извоз на патека](course-export.md).

`<lap>` може да биде кое било од следново (детали во [Влезови за круг](lap-inputs.md)):

- датотека со круг: route JSON, FH Companion lap JSON, `heat3d-lap` JSON, `.npz` или `.csv` со колони x, y, z
- папка со датотеки со кругови, пребарувана рекурзивно (цела снимена патека)
- **име** на патека, пронајдено во библиотеката на FH Companion на `%LOCALAPPDATA%\FHCompanion\laps`

### Опции {#options}

| Опција | Основно | Игри | Значење |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` во тековната папка | сите | каде да се запише; името е со мали букви, а низите од други знаци се претвораат во `_` |
| `--game {forza,beamng,acrally}` | што вели датотеката со круг, инаку `forza` | сите | од која игра е кругот |
| `--margin M` | 80 | сите | метри терен што се задржуваат од двете страни на возењето |
| `--texture-size {2048,1024,512}` | 2048 | сите | пиксели на текстурата на теренот по плочка од 512 m (2048 = 25 cm по пиксел) |
| `--no-textures` | исклучено | сите | само рамни бои: многу помала датотека. За Forza ова го прескокнува и поделувањето на пат/банкина (видете подолу) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | мапите на земјата и текстурите на моделите од кој сезона |
| `--no-placed` | исклучено | сите | само терен: без рабници, огради, знаци, згради. За BeamNG, површините за возење моделирани како мрежи сепак се задржуваат |
| `--trees` | исклучено | сите | постави и вегетација (Forza: дрвја, грмушки и предмети што се кршат; BeamNG: дрвја; AC Rally: дрвја и инстанцираната зеленина) |
| `--detail-budget N` | автоматски | сите | таван на триаголници за сè поставено; видете [Нивоа на детали и буџетот](detail-budget.md) |
| `--track DIR` | се бара | Forza | папката на патеката (под `media\Tracks`, со `GeoChunk0.minizip`) ако инсталираната игра не треба да се бара |
| `--level NAME` | најдено од кругот | BeamNG, AC Rally | нивото (име на папка кај BeamNG) или етапата (име на мапа кај AC Rally), без разлика на големи и мали букви |
| `--install DIR` | се бара во библиотеките на Steam | BeamNG, AC Rally | BeamNG: папката со `gameengine.zip`. AC Rally: папката на играта или нејзината `acr\Content\Paks` / `Content\Paks` |

Опциите што не важат за некоја игра се игнорираат без предупредување. На пример,
`--season` не прави ништо за BeamNG и AC Rally, а ниту `--track`.

### Која игра {#which-game}

Играта се зема од `--game`, па од полето `game` на датотека `heat3d-lap`
(или од описната линија `# {...}` на CSV), а инаку е Forza. Папката
ја добива играта што ја именуваат нејзините датотеки, кога именуваат само една; датотека што не именува
ниедна (круг на FH Companion, `course.json`, CSV без описна линија) не се
брои (видете [Влезови за круг](lap-inputs.md)).

| Вредност | Извоз |
|---|---|
| почнува со `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` или `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | се одбива: „keeps all its content in one package obfuscated with a key, and this tool recovers none“ |
| `iracing` | се одбива: „tracks ship in a protected format that is not a file-extraction target“ |
| сè друго | се одбива: „there is no course reader for <game> yet“ |

Одбивањето предлага и алтернативи: реконструирање на патеката од играње
(3DHeat GameCapture) или анализа на круговите без патека, бидејќи табот Анализа на трка
на прегледувачот црта пат од нив.

### Примери {#examples}

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Пример на излез (Forza, синтетички бројки):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Секој автомобил од инсталиран Forza со сопствената ниска детаљност на играта, во една датотека за
табот Анализа на трка на прегледувачот: моделот `ProxyLOD` што го носи секоја архива на автомобил под
`media/Cars`, околу 900 триаголници, со бројот на автомобилот како што го наведува
телеметријата, неговата марка, ознака на моделот и година од името на архивата, и неговите тркала и задни
светла. Трае секунди и пишува околу 5 MB. Извршете ја повторно кога играта добива нови
автомобили. Архива без таков модел (реквизит од сообраќај) се именува и се изоставува. Форматот
е во [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Обликите се во метри, на самата игра: 1:1 со автомобилот. Датотеката ја содржи
содржината на играта, па е за машината на која е направена, а не за препраќање.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Го извршува извозот `course` на Forza на секоја папка на патека во снимена библиотека
на кругови, и пишува по еден `<name>.glb`. Само за Forza. Го повикува извозот на Forza
директно и не ги чита `--game`, `--level` или `--install`.

| Опција | Основно | Значење |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | папката во која се пишува (се создава ако ја нема) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | библиотеката со кругови |
| `--only TEXT [TEXT ...]` | сите | само патеките чии имиња на папки содржат еден од овие (без разлика на големи и мали букви) |
| `--force` | исклучено | извези повторно што веќе има `.glb` |
| `--track DIR` | се бара | како за `course` |
| `--margin M` | 80 | како за `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | како за `course` |

Што се смета за папка на патека: директна подпапка на библиотеката чие име
содржи ` (course_`, така ги именува FH Companion, на пример
`Example Circuit (course_1200_3400_to_1175_3400)`. Делот од ` (course_` натаму
се отфрла од името.

Како се однесува извршувањето:

- Патека чиј `.glb` веќе постои се прескокнува (`kept`) освен ако е дадено `--force`, па прекинато извршување продолжува од каде запрело.
- `.glb` напишан од постара верзија, без сопствениот слој и местата на трката (неговиот `asset.extras.course_format` недостасува или е понизок од тековниот), се извезува повторно, како да е дадено `--force` само за него.
- Две папки на патеки со исто име пред ` (course_` (снимач што нова патека ја именувал по стара) не се пребришуваат: папката создадена прва го задржува `<name>.glb`, другата се пишува како `<name>_<start>.glb`, каде `<start>` е местото каде започнува, со знаци минус како `m` (на пример `example_circuit_m120_m340.glb`).
- Патека што не успева (нечитливи кругови, снемување меморија, нема терен...) се пријавува како `FAILED`, а извршувањето продолжува.
- На крајот печати табела со состојба, големина во MB, поминати секунди и име, па `<n> of <total> courses in <folder>`.
- Излезниот код е 1 ако некоја патека не успеала.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Ги наведува сите трки што ги дефинира инсталиран Forza, од неговите дефиниции на рути (видете
[Патеки од Forza Horizon](course-forza-horizon.md#which-race)), и ги проверува
извозите во папка `courses` спрема нив. Ги чита играта и библиотеката со кругови;
не пишува ништо освен изборната табела.

| Опција | Основно | Значење |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | папката во која пишува `courses`, чии датотеки се проверуваат |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | библиотеката со кругови |
| `--track DIR` | се бара | папката на патеката, ако не е онаа на инсталираната игра |
| `--markdown FILE` | нема | запиши ја табелата и таму, како Markdown |

Еден ред по трка и еден по снимена патека возена на неа:

| Колона | Значење |
|---|---|
| route | идентификаторот на рутата |
| course | снимената патека совпадната со неа, ако има |
| own assets | копии што трката ги додава на светот за слободно возење |
| drawn | од нив, копии чиј модел го испорачува патеката |
| kinds | додадените копии по вид (огради, реквизити, налепници, инфраструктура, ...) |
| not geometry | маркери за гледачи и сплајнови за судири, избројани |
| hidden | објекти од слободното возење што ги отстранува трката |
| venue | моделите на земјата на местото покрај кои линијата на AI на трката поминува на помалку од 10 m |
| export | `current`, `older format` (повторно извезена од `courses`), `not exported`, или празно за трка без снимена патека |

Завршува со број: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Ова е сечење на Forza со сè наведено рачно: давате папка на патека
и област, а не круг. Корисно е кога областа што ја сакате е кутија,
а не возење.

| Опција | Основно | Значење |
|---|---|---|
| `<path>` | задолжително | папка на патека од Forza под `media\Tracks` (со `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | задолжително | `.glb` што се пишува |
| `--box X0 Z0 X1 Z1` | | областа, во метри на играта (x и z, како што ги пријавува телеметријата); аглите по кој било редослед |
| `--route FILE` | | route JSON со `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, како што го пишуваат `heat3d_capture route` и `heat3d_capture laps`; се чита како UTF-8, со или без ознака за редослед на бајти |
| `--margin M` | **100** | метри додадени околу границите на рута, и ширина на коридорот кога рутата има линија |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | како за `course` |

Дајте точно една од `--box` и `--route`, инаку излезниот код е 2. Со
`--route`, сечењето се `bounds` на рутата (`min`/`max`, x и z) проширени за
маргината. Ако датотеката содржи и најмалку 10 позиции, сечењето се стеснува на
коридор од `--margin` метри околу нив, а поставените модели добиваат детаљ
според растојанието до таа линија. Со `--box` се задржува целата кутија, а детаљот оди на
она што стои најблиску до средината на кутијата.

Височината никогаш не е дел од сечењето. Кутија надвор од мапата или во море дава
„no terrain there“ (излезен код 1), а не грешка за координатите.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels и level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` ги наведува нивоата што ги испорачува инсталирана игра со Frostbite, по името на
нивната табела (`levels/<level>/<level>.toc`), со нејзината големина и од каде
доаѓа: `Data` за основната игра, `Update/<pack>` за ажурирање, и колку
табели со висока резолуција ѝ додаваат. Ниво што го испорачува ажурирање има мала табела
само со делови и во основната игра; табелата со пакетите на нивото е
нивото (видете [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` извезува едно: висинското поле на теренот, секоја мрежа што ја поставуваат статичните
групи модели на нивото, објектите поставени еден по еден, каде стојат и
позадината на теренот на нивото околу мапата. Со `--textures`, секоја површина носи
своја мапа на бои; со `--navmesh` доаѓаат и површините по кои одат војниците. Како
се чита е во [Frostbite](reader-frostbite.md).

| Опција | Основно | Значење |
|---|---|---|
| `<level>` | задолжително | име како што го печати `levels`, единствен дел од него или патеката на `.toc` на нивото |
| `-o`, `--out FILE` | `<level>.glb` | `.glb` што се пишува |
| `--install FOLDER` | првата игра од Steam чиј `Data` содржи `layout.toc` | папката на играта |
| `--textures [PIXELS]` | исклучено; 512 кога е дадено без големина | запиши ја мапата на бои на секоја површина, најголемиот mip не поголем од PIXELS по страна, и нејзините координати на текстура како што ги има играта, со повторувачки семплер (видете [Формат на излезот](output-format.md)). Висинското поле ја добива мапата на бои на позадината на теренот каде таа мапа го покрива, инаку средната боја на материјалите на површината на теренот, инаку просечната боја на позадината околу него. Исклучено, секој дел е рамна боја |
| `--ground-texture [METRES]` | исклучено; 0.5 кога е дадено без големина | испечи ги налепниците на теренот — патишта, писти, платформи, насликани ознаки — врз бојата на земјата, помножени со мапата на бои на теренот каде нивото има таква, во бојата на висинското поле, METRES по пиксел, во плочки од најмногу 4.096 пиксели (`ground:terrain x<x> z<z>`). Работи со или без `--textures` |
| `--navmesh` | исклучено | додај ја навигациската мрежа на нивото за неговиот најмал агент, војникот (висок 1,8 m, широк 0,4 m), како делот `nav:walkable`: земјата, подовите, скалите и покривите до кои може да стигне војник, без врските (скокови, скали, прескокнувања) меѓу нив |
| `--ground-spacing METRES` | 4 | најфиното растојание на висинското поле; јазлите пофини од ова се семплираат надолу. 0 го изоставува висинското поле |
| `--detail-budget N` | секоја копија на нејзиното најгрубо ниво, плус четвртина, најмалку 1.500.000 | таван на триаголници. Мрежите што чинат најмногу паѓаат по едно ниво на детаљност додека не се собере; ако ни најгрубите нивоа не се собираат, најпрво се изоставуваат најмалите копии. Позадината на теренот никогаш не се огрубува ниту се изоставува |
| `--skip TEXT` | | изостави статични групи модели чие име на партиција го содржи TEXT; повторете за повеќе. На пример, слој на режим на игра |
| `--by-mesh` | исклучено | за наоѓање што е еден дел: еден дел по изворна мрежа и материјал, именуван `<part> \| <mesh> \| <material>`; многу поголема датотека |
| `--clamped-uvs` | исклучено | за рендерер што не може да повторува текстура: исечи го секој текстуриран триаголник на парчиња чии координати лежат во 0..1, и нацртај триаголник што би барал повеќе од 4 парчиња во просечната боја на неговата текстура, во делот `<part> (average colour)` |

Печати кои групи и колку копии поставила секоја, мрежите што ги изоставила и
зошто, триаголниците по дел (а со `--textures` колку текстури, и
колку секции ја нашле својата мапа на бои), што е земјата, а со
`--navmesh` колку навигациски плочки се прочитани. Не се пишува ништо за нивото освен
геометријата: без имиња, без метаподатоци (видете [Формат на излезот](output-format.md)).

Буџетот на теренот е одделен: висинското поле и позадината никогаш не се
огрубуваат со `--detail-budget`; `--ground-spacing` ја одредува големината на висинското поле.

Цело ниво е големо: обично над десет милиони триаголници и неколку
стотини MB. `--textures` додава малку на датотеката; ниво густо со дрвја
може да стигне до околу 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
го доведува нивото на отприлика третина од тоа.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps и ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` е папката на играта, нејзината `Content/Paks` или името на нејзината папка
во библиотека на Steam (`"<Steam game folder name>"`). `ue-maps` ги наведува сите мапи
што имаат испечени ќелии на World Partition покрај себе. `ue-map` извезува една како
`ground:<map>` (пејзажот), `structure:<map>` (споените HLOD
мрежи на мапата) и `water:<map>` (нејзините водни тела таму каде стојат над
земјата), во Unreal **сантиметри** со заменети Y и Z - единствениот извоз што не е
во метри. Како се чита и проверува секој: [Мапи на Unreal 5](level-unreal-world-partition.md).

| Опција | Основно | Значење |
|---|---|---|
| `<map>` | задолжително | име како што го печати `ue-maps`, или единствен дел од него |
| `-o`, `--out FILE` | `<map>.glb` | `.glb` што се пишува |
| `--ground-spacing METRES` | 2 | растојанието на темињата на пејзажот во датотеката, заокружено на цел број од неговите четириаголници |
| `--no-structures`, `--no-water` | | изостави го тој дел |

Печати триаголници по дел, колку компоненти на пејзажот се прочитани и
колку од темињата што ги чуваат двапати не се совпаѓаат. Мапа од 3 km на 2 m е околу
4,6 милиони триаголници на земјата.

## enfusion-worlds и enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` ги наведува сите светови со терен, по нивната папка под
`worlds/`. `enfusion-world` извезува еден: `ground:<world>` (теренот, во
боите на неговите плочки од супертекстура), `water:<world>` (морето, на височина нула)
и `structure:<world>` (кутијата на секој поставен модел), во метри на самата игра -
x исток, y горе, z север. Како се чита и проверува секој:
[Светови на Arma Reforger](level-arma-reforger.md).

| Опција | Основно | Значење |
|---|---|---|
| `<world>` | задолжително | свет како што го печати `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb` што се пишува |
| `--install FOLDER` | библиотеката на Steam што ја држи играта | папката на играта |
| `--ground-spacing METRES` | 2 (сопственото на теренот) | растојанието на темињата на теренот во датотеката |
| `--texture-size PIXELS` | 4096 | поголемата страна на сликата со боја на земјата; 0 за рамна боја |
| `--no-structures` | | изостави ги поставените модели |
| `--trees` | исклучено | постави и дрвја и друга вегетација, како кутии |

Печати триаголници по дел, колку темиња на рабовите на плочките не се совпаѓаат, колку
ентитети содржи датотеката на светот и колку кутии се поставени, и што е
изоставено и зошто.

## Променливи на околината {#environment-variables}

| Променлива | Ефект |
|---|---|
| `HEAT3D_OODLE` | патека до `oo2core_*_win64.dll`, или папка што содржи една; видете [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | секоја вредност освен празно, `0`, `false`, `no` ја исклучува проверката за ажурирања; видете [Ажурирања](updates.md) |
| `LOCALAPPDATA` | каде се бараат библиотеката на FH Companion, корисничката папка на BeamNG и кешот за ажурирања |
| `HEAT3D_COURSE` | само за тестови: патеката што ја користи тестот за рабници на инсталирана игра; видете [Развој](development.md) |
