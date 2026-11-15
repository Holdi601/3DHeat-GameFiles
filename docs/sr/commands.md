---
title: Команде
nav_order: 2
lang: "sr"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Команде {#commands}

Свака команда се покреће као `python -m heat3d_gamefiles <команда> ...` из фолдера репозиторијума.
Команде су поређане оним редом којим их обично треба: шта је ова датотека, шта је унутра, дај ми то,
и претвори круг у стазу.

| Команда | Узима | Ради |
|---|---|---|
| [`identify`](#identify) | било коју датотеку | именује формат контејнера тако што чита његове бајтове |
| [`list`](#list) | Unreal `.pak` или IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip` или zip | исписује његове ставке |
| [`extract`](#extract) | исто | уписује једну ставку на диск |
| [`meshes`](#meshes) | Unity `SerializedFile` | исписује и проверава његове мреже |
| [`course`](#course) | круг | извози стазу око њега (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | библиотеку снимљених кругова | покреће `course` за сваку стазу у њој (Forza) |
| [`races`](#races) | инсталирану Forza | исписује сваку трку коју игра дефинише: шта додаје, шта скрива, места одржавања и стање њеног извоза |
| [`terrain`](#terrain) | фолдер Forza стазе | исече област по координатама у свету |
| [`levels`](#levels-and-level-frostbite) | инсталирану Frostbite игру (Battlefield 6) | исписује њене нивое |
| [`level`](#levels-and-level-frostbite) | име нивоа | извози ниво: терен, постављене мреже, по потреби њихове мапе боја (Battlefield 6) |
| [`cars`](#cars) | инсталирану Forza | сваки аутомобил у ниском детаљу, у једној датотеци за картицу трке у приказивачу |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | Unreal 5 игру | исписује њене мапе World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | име мапе | извози мапу: терен, HLOD структуре, воду |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | инсталирани Arma Reforger | исписује његове светове |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | име света | извози свет: терен у његовим бојама, море, зграде као кутије |

**Како читати примере:** `<x>` значи замени то својом вредношћу, без угаоних заграда; `[...]` је
опционално; путању са размацима стави у "двоструке наводнике", на пример `"C:\Games\My Game"`.
Први пут? Погледај [Пре почетка](before-you-start.md). Потпун `--help` сваке команде је на
[Референци команди](../cli-reference.md).

Кад се програм покрене, може прво да провери да ли постоји новије издање. Погледај
[Ажурирања](updates.md). `HEAT3D_NO_UPDATE=1` искључује ту проверу.

Извор: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Корак по корак: [Преглед архива](inspecting-archives.md), [Извоз стазе](course-export.md),
[Цели нивои](whole-levels.md), [Forza аутомобили](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Излазни кодови {#exit-codes}

| Код | Значење |
|---|---|
| 0 | успех |
| 1 | посао није успео (круг се не може прочитати, игра није нађена, нема шта да се извезе, стаза у `courses` није успела; за `list` и `extract`, фајл који није ниједан од архива које читају, фајл који не може да се отвори или прочита - шифровани pak без `--key`, шифровани IoStore контејнер - или ставка којој нема места у архиви) |
| 2 | лоши аргументи (argparse), путања која не постоји, `--key` који није 64 хекадецимална броја, или `terrain` добијен и са `--box` и са `--route`, или ни са једним од њих |

Грешке команди `list` и `extract` су сваки пут једна линија на стандардној грешци, а не
Python трагање за грешком.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Ова команда чита фајл и каже који је то контејнер. Не гледа екстензију (једини изузетак је
`.ucas`, испод). Пробава формате овим редом и staje на првом који се може прочитати:

1. **Unreal `.pak`**: заглавље на крају са pak магичним бројем у последњих 1.024 бајта. Исписује
   верзију, почетак и величину индекса, да ли је индекс шифрован и методе компресије.
2. **Unreal IoStore `.utoc`**: IoStore магични број на почетку. Исписује верзију, број блокова и
   да ли је контејнер шифрован; за нешифрован, број фајлова које његов директоријум именује (и под
   којом тачком монтирања), методе компресије и да ли је његов `.ucas` поред њега. `.ucas` нема
   сопствено заглавље, па се препознаје по `.utoc` истог имена поред себе, а `identify` именује
   тај фајл.
3. **ForzaTech `.minizip`**: магични број `PGZP`. Исписује верзију, број ставки и сегмената, и
   да ли је поред њега `ChunkContentsMiniZip<n>.txt` који именује ставке (и, ако јесте, да ли их
   именује онолико колико их има).
4. **zip**: локално заглавље zip фајла на почетку. Исписује број ставки, шест најчешћих
   екстензија и називе нивоа кад су ставке у `levels/<name>/`, као у архиви нивоа BeamNG.drive.
5. **Unity**: `UnityFS` свежањ (исписује верзију мотора и број ставки) или голи `SerializedFile`
   (исписује формат, верзију мотора, број објеката и шест најчешћих класа).
6. **Frostbite `.toc`**: исписује врсту (`plain` или `signed`), где почиње стабло и или број
   ресурса (табела бинарних секција) или број superbundle-ова (DbObject стабло).
7. **Source 2 `.vpk`**: исписује верзију, број ставки и први `.nav` мрежу за навигацију ако је има у архиви.
8. **BeamNG `.cdae`**: верзија облика 31 која се може прочитати. Исписује број мрежа, број
   нацртаних нивоа детаља и прве материјале.
9. **BeamNG `.ter`**: нема магичног броја, па све мора да се сложи - страница од 2 до 16.384,
   толико висина и бајтова слојева на квадрат, па онда 1 до 255 штампаних имена слојева. Исписује
   верзију, величину и имена слојева.
10. **ForzaTech `.modelbin`**: исписује верзију, број блокова и шест најчешћих ознака блокова.
    Садржај блокова се овде не декодира.

Формати који имају сопствени магични број (2 до 4) долазе пре Unity и Frostbite провере, јер те
провере читају цео фајл: Forza архива је десетине гигабајта.

Ако ниједан не одговара, исписује `not a format this tool reads` и последњи разлог. Тај разлог
долази из ForzaTech провере.

Пример (измишљени подаци):

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

| Опција | Подразумевано | Значење |
|---|---|---|
| `<archive>` | обавезно | Unreal `.pak`; IoStore `.utoc` (или `.ucas` поред њега); Source 2 `.vpk` (за подељене VPK, `_dir.vpk`); ForzaTech `.minizip`; zip, као BeamNG-ове архиве нивоа и садржаја |
| `--filter TEXT` | нема | само путање које садрже TEXT, без обзира на велика и мала слова |
| `--limit N` | 50 | исписује највише N ставки (укупан број се увек исписује) |
| `--key HEX` | нема | AES-256 кључ који већ имате, 64 хекадецимална броја, са или без `0x`. Користи га само шифрован `.pak`. Све што није 64 хекадецимална броја се одбија пре отварања архиве (излазни код 2) |

Алат одређује формат по бајтовима: IoStore табелу садржаја, `.minizip` и VPK по потпису са којим
почињу, zip по његовом локалном заглављу, а `.pak` по крају на дну. `.ucas` нема заглавље и
отвара се преко `.utoc` истог имена. Фајл који није ниједан од ових одбија се са `<file> is not an
archive list and extract read (...)`. Фајл који јесте, али не може да се отвори, одбија се са
разлогом читача: шифрован pak без `--key`, шифрован IoStore контејнер, верзија pak-а коју не
чита. У сваком случају је једна линија и излазни код 1.

Свака линија приказује величину без компресије, методу компресије и путању:

| Архива | Метода | Путање |
|---|---|---|
| `.pak` | `none`, или назив из заглавља (`Zlib`, `Oodle`, `Gzip`...) | са тачком монтирања архиве, на пример `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, или метода контејнера (`Oodle`, `Zlib`...), како је прва блок ускладиштен | са тачком монтирања, на пример `../../../<Project>/Content/...`. Контејнер без индекса директоријума не именује ниједан фајл и одбија се |
| `.vpk` | увек `stored` | као у директоријуму |
| `.minizip` | `lz4`, `deflate` или `stored` | као што их пише `ChunkContentsMiniZip<n>.txt` поред `GeoChunk<n>.minizip`, без префикса машине на којој је направљен (с косим цртама уназад, како их игра записује). Архива не чува имена, па без тог фајла ставке су `#0`, `#1`... Списак чији се број редова не слаже са бројем ставки се одбија: та два не припадају једно другом |
| zip | `stored`, `deflate`, ... | као што су ускладиштени; фолдери се не исписују |

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

| Опција | Подразумевано | Значење |
|---|---|---|
| `<archive>` | обавезно | као за `list` |
| `<entry>` | обавезно | путања тачно онаква као што је исписује `list` (осетљиво на велика и мала слова); у `.minizip`-у ради и `#<број>` |
| `--out FILE` | име ставке (после последње `/` или `\`), у тренутном фолдеру | куда да се запише; родитељски фолдери се праве |
| `--key HEX` | нема | као за `list` |

Ставка се дешифрује (pak, уз кључ), декомпресује и запише. Исписује се
`<bytes> bytes -> <file>`. Ако путање нема у архиви, команда излази са кодом 1. Исто важи и за
ставку која не може да се прочита (шифрована ставка без кључа, Oodle компресија без Oodle
библиотеке), са разлогом у једној линији. VPK ставка се овде не проверава CRC-ом. Читач за то има
метод `verify()` (видите [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Опција | Подразумевано | Значење |
|---|---|---|
| `<path>` | обавезно | голи Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), а не свежањ |
| `--limit N` | 25 | декодира и исписује највише N мрежа |

Исписује број објеката `Mesh`, па по једну линију за сваку мрежу: име (првих 40 знакова), број
темена и троуглова, и `ok` или `BOUNDS DISAGREE`. `BOUNDS DISAGREE` значи да декодирана темена не
дају оквир који је Unity сачувао за мрежу, у границама од 2% величине оквира. То је сопствена
провера читања (видите [Unity](reader-unity.md)). Мрежа која не може да се прочита приказује се са
разлогом и рачуна се према граници. Подаци темена у `.resS` фајлу се читају из фолдера у којем је
контејнер.

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

Ова команда извози стазу око круга: тло у појасу са обе стране вожње и оно што стоји на њему, као
један `.glb`. Остало сама одређује: коју игру, који инсталирани примерак, коју стазу, ниво или
деоницу, и (за Assetto Corsa Rally) којим редом су осе окренуте. Погледај
[Извоз стазе](course-export.md).

`<lap>` може бити било шта од следећег (детаље у [Улазима за круг](lap-inputs.md)):

- фајл круга: route JSON, FH Companion lap JSON, `heat3d-lap` JSON, `.npz` или `.csv` са колонама x, y, z
- фолдер фајлова кругова, претражен рекурзивно (цела снимљена стаза)
- **име** стазе, потражено у библиотеци FH Companion на `%LOCALAPPDATA%\FHCompanion\laps`

### Опције {#options}

| Опција | Подразумевано | Игре | Значење |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` у тренутном фолдеру | све | куда да се запише; име се претвара у мала слова, а низови других знакова у `_` |
| `--game {forza,beamng,acrally}` | оно што каже фајл круга, иначе `forza` | све | из које игре је круг |
| `--margin M` | 80 | све | метара тла задржано са обе стране вожње |
| `--texture-size {2048,1024,512}` | 2048 | све | пиксели текстуре тла по плочици од 512 м (2048 = 25 cm по пикселу) |
| `--no-textures` | искључено | све | само равне боје: знатно мањи фајл. За Forza ово такође прескаче поделу на коловоз и банкину (видите испод) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | мапе тла и текстуре модела за које годишње доба |
| `--no-placed` | искључено | све | само терен: без ивичњака, баријера, знакова, зграда. За BeamNG, površine вожње направљене као мреже се и даље задржавају |
| `--trees` | искључено | све | поставља и вегетацију (Forza: дрвеће, грмље и ствари које се разбијају; BeamNG: дрвеће; AC Rally: дрвеће и инстанцирано растиње) |
| `--detail-budget N` | аутоматски | све | горња граница троуглова за све постављено; видите [Нивои детаља и буџет](detail-budget.md) |
| `--track DIR` | тражи се | Forza | фолдер стазе (у `media\Tracks`, у којем је `GeoChunk0.minizip`) ако инсталирана игра не сме да се претражује |
| `--level NAME` | нађено из круга | BeamNG, AC Rally | ниво (име фолдера у BeamNG-у) или деоница (име мапе у AC Rally), без обзира на велика и мала слова |
| `--install DIR` | тражи се у Steam библиотекама | BeamNG, AC Rally | BeamNG: фолдер који садржи `gameengine.zip`. AC Rally: фолдер игре, или његово `acr\Content\Paks` / `Content\Paks` |

Опције које се не односе на неку игру се игноришу без упозорења. На пример, `--season` не ради
ништа за BeamNG и AC Rally, а `--track` не ради ништа ни за њих.

### Која игра {#which-game}

Игра се узима из `--game`, па из поља `game` у фајлу `heat3d-lap` (или из реда описа `# {...}` у
CSV-у), па се подразумева Forza. Фолдер добија игру коју именују његови фајлови, ако именују само
једну; фајл који не именује ниједну (FH Companion круг, `course.json`, CSV без реда описа) се не
рачуна (видите [Улази за круг](lap-inputs.md)).

| Вредност | Извоз |
|---|---|
| почиње са `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` или `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | одбијено: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | одбијено: "tracks ship in a protected format that is not a file-extraction target" |
| било шта друго | одбијено: "there is no course reader for <game> yet" |

Одбијање такође предлаже алтернативе: реконструкцију стазе из игре (3DHeat GameCapture), или анализу
кругова без стазе, јер картица Анализа трке у приказивачу из њих црта пут.

### Примери {#examples}

```
# Стаза из библиотеке FH Companion, по имену
python -m heat3d_gamefiles course "Example Circuit"

# Један фајл круга, ужи појас, мањи фајл
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Зимске текстуре, са дрвећем
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Тврда граница од 500.000 постављених троуглова
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Фолдер стазе дат директно (игра инсталирана ван Steam-а)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: назови ниво, покажи инсталацију
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, са обичним CSV кругом који не каже за коју је игру
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Пример исписа (Forza, измишљени бројеви):

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

Сваки аутомобил инсталиране Forza игре на ниском детаљу који је предвидела сама игра, у једној датотеци за
картицу трке у приказивачу: модел `ProxyLOD` који носи сваки архив аутомобила у `media/Cars`, око
900 троуглова, са бројем аутомобила какав га телеметрија наводи, његовом марком, ознаком модела и
годином из имена архива, и његовим точковима и задњим светлима. Траје секунде и пише око 5 MB.
Покрените га поново кад игра добије нове аутомобиле. Архив без таквог модела (рекавизит за саобраћај)
се именује и изоставља. Формат је у [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Облици су у метрима, игрини сопствени: 1:1 са аутомобилом. Датотека садржи садржај игре, па је
намењена машини на којој је направљена, а не за слање даље.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Ова команда покреће Forza извоз `course` на сваком фолдеру стазе у снимљеној библиотеци кругова, и
за сваку пише по један `<name>.glb`. Само је за Forza. Директно позива Forza извоз и не чита
`--game`, `--level` или `--install`.

| Опција | Подразумевано | Значење |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | фолдер у који се пише (прави се ако не постоји) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | библиотека кругова |
| `--only TEXT [TEXT ...]` | све | само стазе чија имена фолдера садрже неки од ових (без обзира на велика и мала слова) |
| `--force` | искључено | поново извози оно што већ има `.glb` |
| `--track DIR` | тражи се | као за `course` |
| `--margin M` | 80 | као за `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | као за `course` |

Шта се рачуна као фолдер стазе: непосредни подфолдер библиотеке чије име садржи ` (course_`, како их
FH Companion именује, на пример `Example Circuit (course_1200_3400_to_1175_3400)`. Део имена од
` (course_` надаље се одбацује.

Како се покретање понаша:

- Стаза чији `.glb` већ постоји се прескаче (`kept`), осим ако није дат `--force`, па се прекинуто
  покретање наставља тамо где је стало.
- `.glb` који је написала старија верзија, без слоја трке и места одржавања (његово
  `asset.extras.course_format` недостаје или је мањи од тренутног), извози се поново, као да је за
  њега дат `--force`.
- Две фолдера стаза са истим именом пре ` (course_` (снимач који је нову стазу назвао по старој) не
  преписују једна другу: фолдер направљен раније задржава `<name>.glb`, а други се пише као
  `<name>_<start>.glb`, где је `<start>` место почетка, са знаком минус као `m` (на пример
  `example_circuit_m120_m340.glb`).
- Стаза која не успе (нечитљиви кругови, нестанак меморије, нема терена...) се јавља као `FAILED`, а
  покретање се наставља.
- На крају исписује табелу статуса, величине у MB, секунди и имена, па `<n> of <total> courses in <folder>`.
- Излазни код је 1 ако је нека стаза пропала.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Исписује сваку трку коју инсталирана Forza дефинише, из њених дефиниција рута (видите
[Forza Horizon стазе](course-forza-horizon.md#which-race)), и проверава извезене фајлове у фолдеру
`courses` према њима. Чита игру и библиотеку кругова; ништа не пише осим необавезне табеле.

| Опција | Подразумевано | Значење |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | фолдер у који пише `courses`, чији се фајлови проверавају |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | библиотека кругова |
| `--track DIR` | тражи се | фолдер стазе, ако није инсталирана игра |
| `--markdown FILE` | нема | таблицу пише и тамо, као Markdown |

Један ред по трци, и један за сваку снимљену стазу на којој се вози:

| Колона | Значење |
|---|---|
| route | идентификатор руте |
| course | снимљена стаза упарена са њом, ако постоји |
| own assets | копије које трка додаје у слободан свет |
| drawn | од њих, копије чији модел стаза садржи |
| kinds | додате копије по врсти (баријере, реквизити, декали, инфраструктура, ...) |
| not geometry | маркери публике и колизионе криве, избројани |
| hidden | објекти слободне вожње које трка уклања |
| venue | модели тла места које AI линија трке пролази на 10 m или ближе |
| export | `current`, `older format` (поново извезено командом `courses`), `not exported`, или празно за трку без снимљене стазе |

Завршава бројем: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Ово је Forza сечење са свиме наведеним ручно: дајете фолдер стазе и област, а не круг. Корисно је
кад је подручје које желите кутија, а не вожња.

| Опција | Подразумевано | Значење |
|---|---|---|
| `<path>` | обавезно | Forza фолдер стазе у `media\Tracks` (у којем су `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | обавезно | `.glb` који се пише |
| `--box X0 Z0 X1 Z1` | | област, у метрима игре (x и z, како их телеметрија исписује); углови у било ком реду |
| `--route FILE` | | route JSON са `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, како их пишу `heat3d_capture route` и `heat3d_capture laps`; чита се као UTF-8, са или без byte-order марке |
| `--margin M` | **100** | метара додатих око граница руте, и ширина коридора кад рута има линију |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | као за `course` |

Дајте тачно једно од `--box` и `--route`, иначе је излазни код 2. Са `--route`, сечење су границе
руте (`min`/`max`, x и z) проширене маргином. Ако фајл садржи и најмање 10 позиција, сечење се сужава
на коридор ширине `--margin` метара око њих, а постављени модели добијају детаљ према удаљености од
те линије. Са `--box`, задржава се цела кутија, а детаљ иде ономе што стоји најближе средини кутије.

Висина никад није део сечења. Кутија ван мапе, или у мору, даје "no terrain there" (излазни код 1),
а не грешку о координатама.

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

`levels` исписује нивое које инсталирана Frostbite игра садржи, по имену њихове табеле
(`levels/<level>/<level>.toc`), са величином и одакле долазе: `Data` за основну игру,
`Update/<pack>` за ажурирање, и колико табела у високој резолуцији се додаје. Ниво који ажурирање
доноси има малу табелу чанкова и у основној игри; табела са блоковима тог нивоа је сам ниво (видите
[Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` извози један: висинско поље
терена, сваку мрежу коју групе статичких модела постављају, објекте постављене један по један, где
стоје, и позадину терена нивоа око мапе. Са `--textures`, свака површина носи своју мапу боја; са
`--navmesh` долазе и површине по којима војници ходају. Како се то чита, написано је у
[Frostbite](reader-frostbite.md).

| Опција | Подразумевано | Значење |
|---|---|---|
| `<level>` | обавезно | име као што га исписује `levels`, јединствен део имена, или путања `.toc` нивоа |
| `-o`, `--out FILE` | `<level>.glb` | `.glb` који се пише |
| `--install FOLDER` | први Steam примерак чији `Data` садржи `layout.toc` | фолдер игре |
| `--textures [PIXELS]` | искључено; 512 кад је дато без величине | пише мапу боја сваке површине, највећи мип не већи од PIXELS по страни, и њене координате текстуре онакве какве их игра има, са понављајућим узорковањем (видите [Формат излаза](output-format.md)). Висинско поље добија мапу боја позадине терена где је та мапа покрива, иначе средњу боју површинских материјала терена, иначе просечну боју позадине око њега. Искључено, сваки део је равна боја |
| `--ground-texture [METRES]` | искључено; 0,5 кад је дато без величине | запече декале терена (путеве, писте, перона, обележавања) преко боје тла, помножене мапом боја терена где је ниво има, у боју висинског поља, METRES по пикселу, у плочицама од највише 4.096 пиксела (`ground:terrain x<x> z<z>`). Ради са или без `--textures` |
| `--navmesh` | искључено | додаје мрежу за навигацију нивоа за његов најмањи агент, војника (1,8 m висине, 0,4 m ширине), као део `nav:walkable`: тло, подови, степенице и кровови до којих војник може да дође, без веза (скокова, лествица, прескакања) између њих |
| `--ground-spacing METRES` | 4 | најфинији размак висинског поља; чворови финији од тога се узоркују грубље. 0 изоставља висинско поље |
| `--detail-budget N` | свака копија на најгрубљем нивоу, плус четвртина, најмање 1.500.000 | горња граница троуглова. Мреже које највише коштају спуштају по један ниво детаља у исто време док не стану; ако ни најгрубљи нивои не стану, најмање копије се прво изостављају. Позадина терена се никад не грубе и не изоставља |
| `--skip TEXT` | | изоставља групе статичких модела чије име партиције садржи TEXT; понавља се за више. На пример слој једног режима игре |
| `--by-mesh` | искључено | за налажење шта је део: по један део по изворној мрежи и материјалу, именован `<part> \| <mesh> \| <material>`; много већа датотека |
| `--clamped-uvs` | искључено | за рендерер који не може да понавља текстуру: сече сваки троугао са текстуром на комаде чије координате леже у 0..1, а троугао који би требао више од 4 комада црта у просечној боји његове текстуре, у делу `<part> (average colour)` |

Исписује групе и колико копија је свака поставила, мреже које је изоставио и зашто, троуглове по
делу (и са `--textures` колико текстура, и колико делова је нашло своју мапу боја), шта је тло, а са
`--navmesh` колико плочица навигације је прочитано. Ништа се не пише о нивоу осим геометрије: без
имена, без метаподатака (видите [Формат излаза](output-format.md)).

Буџет терена је посебан: висинско поље и позадина се никад не грубе са `--detail-budget`;
`--ground-spacing` одређује висинско поље.

Цео ниво је велик: обично преко десет милиона троуглова и неколико стотина MB. `--textures` додаје
мало фајлу; ниво пун дрвећа може достићи око 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
доводи ниво на отприлике трећину тога.

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

`<game>` је фолдер игре, њен `Content/Paks`, или име њеног фолдера у Steam библиотеци
(`"<Steam game folder name>"`). `ue-maps` исписује сваку мапу која има готове World Partition
ћелије поред себе. `ue-map` извози једну као `ground:<map>` (пејзаж), `structure:<map>` (спојене HLOD
мреже мапе) и `water:<map>` (њена водена тела тамо где стоје изнад тла), у Unreal **центиметрима**
са заменом Y и Z - једини извоз који није у метрима. Како се сваки чита и провери:
[Unreal 5 мапе](level-unreal-world-partition.md).

| Опција | Подразумевано | Значење |
|---|---|---|
| `<map>` | обавезно | име као што га исписује `ue-maps`, или јединствен део имена |
| `-o`, `--out FILE` | `<map>.glb` | `.glb` који се пише |
| `--ground-spacing METRES` | 2 | размак темена пејзажа у фајлу, заокружен на цео број његових сопствених квадрата |
| `--no-structures`, `--no-water` | | изоставља тај део |

Исписује троуглове по делу, колико компонената пејзажа је прочитано и колико од темена које оне
чувају два пута се не слаже. Мапа од 3 km на 2 m има око 4,6 милиона троуглова тла.

## enfusion-worlds и enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` исписује сваки свет са тереном, по његовом фолдеру у `worlds/`. `enfusion-world`
извози један: `ground:<world>` (терен, у бојама његових супертекстурних плочица), `water:<world>`
(море, на висини нула) и `structure:<world>` (кутија сваког постављеног модела), у игриним сопственим
метрима - x исток, y горе, z север. Како се сваки чита и провери:
[Arma Reforger светови](level-arma-reforger.md).

| Опција | Подразумевано | Значење |
|---|---|---|
| `<world>` | обавезно | свет као што га исписује `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb` који се пише |
| `--install FOLDER` | Steam библиотека која садржи игру | фолдер игре |
| `--ground-spacing METRES` | 2 (терена сопствени) | размак темена терена у фајлу |
| `--texture-size PIXELS` | 4096 | већа страна слике боја тла; 0 за равну боју |
| `--no-structures` | | изоставља постављене моделе |
| `--trees` | искључено | поставља и дрвеће и другу вегетацију, као кутије |

Исписује троуглове по делу, колико ивичних темена плочица се не слаже, колико ентитета
садржи фајл света и колико кутија је постављено, и шта је изостављено и зашто.

## Променљиве окружења {#environment-variables}

| Променљива | Дејство |
|---|---|
| `HEAT3D_OODLE` | путања до `oo2core_*_win64.dll`, или фолдера који га садржи; видите [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | свака вредност осим празне, `0`, `false`, `no` искључује проверу ажурирања; видите [Ажурирања](updates.md) |
| `LOCALAPPDATA` | где се траже библиотека FH Companion, кориснички фолдер BeamNG-а и кеш ажурирања |
| `HEAT3D_COURSE` | само за тестове: стаза коју тест за ивичњаке инсталиране игре користи; видите [Развој](development.md) |
