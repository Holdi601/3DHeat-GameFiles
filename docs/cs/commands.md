---
title: "Příkazy"
nav_order: 2
lang: "cs"
source: commands.md
source_hash: "59996378eb40"
nav_exclude: true
search_exclude: true
---
# Příkazy {#commands}

Každý příkaz se spouští jako `python -m heat3d_gamefiles <verb> ...` ze složky repozitáře. Příkazy jsou seřazeny tak, jak je obvykle potřebujete: co je tento soubor, co je uvnitř, jak si vzít jednu položku, a jak z kola udělat trať.

| Příkaz | Bere | Dělá |
|---|---|---|
| [`identify`](#identify) | jakýkoli soubor | pojmenuje formát kontejneru podle jeho bajtů |
| [`list`](#list) | Unreal `.pak` nebo IoStore `.utoc`, Source 2 `.vpk`, ForzaTech `.minizip`, nebo zip | vypíše jeho položky |
| [`extract`](#extract) | totéž | zapíše jednu položku na disk |
| [`meshes`](#meshes) | Unity `SerializedFile` | vypíše a zkontroluje jeho meshe |
| [`course`](#course) | kolo | exportuje trať kolem něj (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | knihovnu nahraných kol | spustí `course` na každé trati v ní (Forza) |
| [`races`](#races) | nainstalovanou Forzu | vypíše každý závod, který hra definuje: co přidává, co skrývá, místa konání, stav jeho exportu |
| [`terrain`](#terrain) | složku tratě Forzy | vyřízne oblast podle světových souřadnic |
| [`levels`](#levels-and-level-frostbite) | nainstalovanou hru na Frostbite (Battlefield 6) | vypíše její úrovně |
| [`level`](#levels-and-level-frostbite) | název úrovně | exportuje úroveň: terén, umístěné meshe, volitelně jejich barevné mapy (Battlefield 6) |
| [`cars`](#cars) | nainstalovanou Forzu | každé auto v nízkém detailu, v jednom souboru pro kartu Analýza závodu v prohlížeči |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | hru na Unreal 5 | vypíše její mapy World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | název mapy | exportuje mapu: krajinu, HLOD struktury, vodu |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | nainstalovaný Arma Reforger | vypíše jeho světy |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | název světa | exportuje svět: terén v jeho barvách, moře, budovy jako krabice |

**Jak číst příklady:** `<x>` znamená nahraďte to vlastní hodnotou, bez lomených závorek; `[...]` je nepovinné; cestu s mezerami uzavřete do dvojitých uvozovek, například `"C:\Games\My Game"`. Jste v tom noví? Podívejte se na [Než začnete](before-you-start.md). Úplný `--help` každého příkazu je na [Přehledu příkazů](../cli-reference.md).

Při každém spuštění programu může nejdřív zkontrolovat, zda není k dispozici novější verze. Viz [Aktualizace](updates.md). `HEAT3D_NO_UPDATE=1` tuto kontrolu vypne.

Zdroj: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Postup krok za krokem: [Prohlížení archivů](inspecting-archives.md), [Export tratě](course-export.md), [Celé úrovně](whole-levels.md), [Auta Forzy](forza-cars.md).

![Nápověda: python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Návratové kódy {#exit-codes}

| Kód | Význam |
|---|---|
| 0 | úspěch |
| 1 | práce selhala (nečitelné kolo, nenalezena žádná hra, nic k exportu, trať v `courses` selhala; u `list` a `extract` soubor, který není žádným z archivů, které čtou, nebo který nejde otevřít nebo přečíst - zašifrovaný pak bez `--key`, zašifrovaný kontejner IoStore - nebo položka, která není v archivu) |
| 2 | špatné argumenty (argparse), cesta, která neexistuje, `--key`, které nemá 64 hexadecimálních číslic, nebo `terrain` dostal oba nebo ani jeden z `--box` a `--route` |

Selhání příkazů `list` a `extract` se vypíšou každé na jeden řádek standardního chybového výstupu, ne jako Python traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Tento příkaz soubor přečte a řekne, který kontejner to je. Nejde podle přípony (jedinou výjimkou je `.ucas`, viz níže). Zkouší formáty v tomto pořadí a zastaví se u prvního, který se dá přečíst:

1. **Unreal `.pak`**: zápatí s magickým číslem pak v posledních 1,024 bajtech. Vypíše verzi, offset a velikost indexu, zda je index zašifrovaný, a metody komprese.
2. **Unreal IoStore `.utoc`**: magické číslo IoStore na začátku. Vypíše verzi, počet chunků a zda je kontejner zašifrovaný. U nezašifrovaného vypíše počet souborů, které jeho adresář pojmenovává (a pod jakým mount pointem), metody komprese a zda je vedle něj jeho `.ucas`. `.ucas` nemá vlastní hlavičku, takže se pozná podle `.utoc` se stejným názvem vedle něj, a `identify` pojmenuje ten soubor.
3. **ForzaTech `.minizip`**: magické číslo `PGZP`. Vypíše verzi, počet položek a segmentů a zda je vedle něj `ChunkContentsMiniZip<n>.txt`, který položky pojmenovává (a pokud ano, zda jich pojmenovává tolik, kolik je).
4. **zip**: hlavička lokálního souboru zipu na začátku. Vypíše počet položek, šest nejčastějších přípon a názvy úrovní, pokud položky leží pod `levels/<name>/`, jako u archivu úrovně BeamNG.drive.
5. **Unity**: svazek `UnityFS` (vypíše verzi enginu a počet položek) nebo holý `SerializedFile` (vypíše formát, verzi enginu, počet objektů a šest nejčastějších tříd).
6. **Frostbite `.toc`**: vypíše druh (`plain` nebo `signed`), místo, kde začíná strom, a buď počet assetů (binární tabulka sekcí), nebo počet superbundlů (strom DbObject).
7. **Source 2 `.vpk`**: vypíše verzi, počet položek a první navigační mesh `.nav`, pokud ho archiv má.
8. **BeamNG `.cdae`**: verze tvaru 31, která se dá přečíst. Vypíše počet meshů, počet vykreslených úrovní detailu a první materiály.
9. **BeamNG `.ter`**: nemá magické číslo, takže musí všechno sedět - strana 2 až 16 384, tolikrát tolik výšek a bajtů vrstev, pak 1 až 255 tisknutelných názvů vrstev. Vypíše verzi, velikost a názvy vrstev.
10. **ForzaTech `.modelbin`**: vypíše verzi, počet chunků a šest nejčastějších značek chunků. Obsah chunků se tu nedekóduje.

Formáty s vlastním magickým číslem (2 až 4) jdou před Unity a Frostbite, jejichž kontroly čtou celý soubor: archiv Forzy má desítky gigabajtů.

Pokud žádný z nich nesedí, vypíše `not a format this tool reads` a poslední důvod. Ten pochází z kontroly ForzaTech.

Příklad (smyšlená data):

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

| Volba | Výchozí | Význam |
|---|---|---|
| `<archive>` | povinné | Unreal `.pak`; IoStore `.utoc` (nebo `.ucas` vedle něj); Source 2 `.vpk` (u rozdělených VPK `_dir.vpk`); ForzaTech `.minizip`; zip, například archivy úrovní a obsahu BeamNG |
| `--filter TEXT` | žádný | jen cesty obsahující TEXT, bez ohledu na velká a malá písmena |
| `--limit N` | 50 | vypíše nejvýše N položek (celkový počet se vždy vypíše) |
| `--key HEX` | žádný | AES-256 klíč, který už máte, 64 hexadecimálních číslic, s `0x` nebo bez něj. Používá ho jen zašifrovaný `.pak`. Cokoli, co není 64 hexadecimálních číslic, se odmítne dřív, než se archiv otevře (návratový kód 2) |

Nástroj pozná formát podle bajtů: tabulku obsahu IoStore, `.minizip` a VPK podle signatury, kterou začínají, zip podle lokální hlavičky a `.pak` podle zápatí na konci. `.ucas` nemá hlavičku a otevírá se přes `.utoc` se stejným názvem. Soubor, který není žádným z nich, se odmítne hláškou `<file> is not an archive list and extract read (...)`. Soubor, který jím je, ale nejde otevřít, se odmítne s důvodem od čtečky: zašifrovaný pak bez `--key`, zašifrovaný kontejner IoStore, verze pak, kterou nečteme. V obou případech je to jeden řádek a návratový kód 1.

Každý řádek ukazuje nekomprimovanou velikost, metodu komprese a cestu:

| Archiv | Metoda | Cesty |
|---|---|---|
| `.pak` | `none`, nebo název ze zápatí (`Zlib`, `Oodle`, `Gzip`...) | s mount pointem archivu, například `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, nebo metoda kontejneru (`Oodle`, `Zlib`...), podle toho, jak je uložen jeho první blok | s mount pointem, například `../../../<Project>/Content/...`. Kontejner bez adresářového indexu nepojmenuje žádné soubory a je odmítnut |
| `.vpk` | vždy `stored` | jak jsou v adresáři |
| `.minizip` | `lz4`, `deflate` nebo `stored` | jak je zapisuje `ChunkContentsMiniZip<n>.txt` vedle `GeoChunk<n>.minizip`, bez předpony počítače, na kterém se sestavovalo (zpětná lomítka, jak je hra zapisuje). Archiv názvy neukládá, takže bez tohoto souboru jsou položky `#0`, `#1`... Seznam, jehož počet řádků se neshoduje s počtem položek, je odmítnut: k sobě nepatří |
| zip | `stored`, `deflate`, ... | jak jsou uloženy; složky se nevypisují |

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

| Volba | Výchozí | Význam |
|---|---|---|
| `<archive>` | povinné | jako u `list` |
| `<entry>` | povinné | cesta přesně tak, jak ji vypíše `list` (rozlišují se velká a malá písmena); u `.minizip` funguje i `#<číslo>` |
| `--out FILE` | název položky (za posledním `/` nebo `\`) ve složce, ve které jste | kam zapsat; nadřazené složky se vytvoří |
| `--key HEX` | žádný | jako u `list` |

Položka se dešifruje (pak, s klíčem), rozbalí a zapíše. Vypíše `<bytes> bytes -> <file>`. Pokud cesty v archivu není, příkaz skončí s kódem 1. Stejně skončí položka, kterou nejde přečíst (zašifrovaná položka bez klíče, komprimovaná Oodle bez knihovny Oodle), s důvodem na jednom řádku. Položka VPK se tu nekontroluje podle CRC. Čtečka na to má metodu `verify()` (viz [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Volba | Výchozí | Význam |
|---|---|---|
| `<path>` | povinné | holý Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), ne svazek |
| `--limit N` | 25 | dekóduje a vypíše nejvýše N meshů |

Vypíše počet objektů `Mesh`, pak jeden řádek na mesh: název (prvních 40 znaků), počet vrcholů a trojúhelníků, a `ok` nebo `BOUNDS DISAGREE`. `BOUNDS DISAGREE` znamená, že dekódované vrcholy neodpovídají ohraničujícímu kvádru, který Unity uložilo pro mesh, v rámci 2 % velikosti kvádru. Je to vlastní kontrola parseru (viz [Unity](reader-unity.md)). Mesh, který nejde přečíst, se hlásí s důvodem a počítá se do limitu. Data vrcholů v souboru `.resS` se čtou ze složky, ve které je kontejner.

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

Tento příkaz exportuje trať kolem kola: zemi v pásu po obou stranách jízdy a to, co na ní stojí, jako jeden `.glb`. Zbytek zjistí sám: která hra, která nainstalovaná kopie, která trať, úroveň nebo etapa a (u Assetto Corsa Rally) jak jsou otočené osy. Viz [Export tratě](course-export.md).

`<lap>` může být kterékoli z následujících (podrobnosti v [Vstupy kola](lap-inputs.md)):

- soubor kola: trasa JSON, JSON kola FH Companion, JSON `heat3d-lap`, `.npz`, nebo `.csv` se sloupci x, y, z
- složka souborů kol, prohledaná rekurzivně (celá nahraná trať)
- **název** tratě, vyhledaný v knihovně FH Companion v `%LOCALAPPDATA%\FHCompanion\laps`

### Volby {#options}

| Volba | Výchozí | Hry | Význam |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` v aktuální složce | všechny | kam zapsat; název se převede na malá písmena a každá posloupnost jiných znaků se nahradí `_` |
| `--game {forza,beamng,acrally}` | co říká soubor kola, jinak `forza` | všechny | ze které hry je kolo |
| `--margin M` | 80 | všechny | metrů země, které se ponechají po obou stranách jízdy |
| `--texture-size {2048,1024,512}` | 2048 | všechny | pixely textury země na dlaždici 512 m (2048 = 25 cm na pixel) |
| `--no-textures` | vypnuto | všechny | jen plné barvy: výrazně menší soubor. U Forzy to také přeskočí rozdělení na silnici a krajnici (viz níže) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | mapy země a textury modelů kterého ročního období |
| `--no-placed` | vypnuto | všechny | jen terén: žádné obrubníky, svodidla, značky, budovy. U BeamNG zůstávají povrchy jízdy modelované jako meshe |
| `--trees` | vypnuto | všechny | přidá i vegetaci (Forza: stromy, keře a rozbitné objekty; BeamNG: stromy; AC Rally: stromy a instancovaná vegetace) |
| `--detail-budget N` | automaticky | všechny | horní mez trojúhelníků pro všechno umístěné; viz [Úrovně detailu a rozpočet](detail-budget.md) |
| `--track DIR` | hledá se | Forza | složka tratě (pod `media\Tracks`, obsahuje `GeoChunk0.minizip`), pokud se nainstalovaná hra nemá prohledávat |
| `--level NAME` | najde se z kola | BeamNG, AC Rally | úroveň (název složky BeamNG) nebo etapa (název mapy AC Rally), bez ohledu na velká a malá písmena |
| `--install DIR` | hledá se v knihovnách Steam | BeamNG, AC Rally | BeamNG: složka s `gameengine.zip`. AC Rally: složka hry, nebo její `acr\Content\Paks` / `Content\Paks` |

Volby, které se na hru nevztahují, se ignorují bez varování. Například `--season` nic nedělá u BeamNG a AC Rally a `--track` nic nedělá ani u nich.

### Která hra {#which-game}

Hra se vezme z `--game`, pak z pole `game` souboru `heat3d-lap` (nebo z řádku popisu `# {...}` v CSV), jinak se použije Forza. Složka dostane hru, kterou pojmenovávají její soubory, pokud pojmenovávají jen jednu. Soubor, který žádnou nepojmenovává (kolo FH Companion, `course.json`, CSV bez řádku popisu), se nepočítá (viz [Vstupy kola](lap-inputs.md)).

| Hodnota | Export |
|---|---|
| začíná na `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` nebo `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | odmítnuto: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | odmítnuto: "tracks ship in a protected format that is not a file-extraction target" |
| cokoli jiného | odmítnuto: "there is no course reader for <game> yet" |

Odmítnutí také navrhne alternativy: rekonstruovat trať z hraní (3DHeat GameCapture), nebo analyzovat kola bez tratě, protože záložka Analýza závodu v prohlížeči z nich vykreslí silnici.

### Příklady {#examples}

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

Ukázkový výstup (Forza, smyšlená čísla):

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

---

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Každé auto nainstalované Forzy v nízkém detailu, který hra sama používá, v jednom souboru pro kartu Analýza závodu v prohlížeči: model `ProxyLOD`, který nese každý archiv auta pod `media/Cars`, asi 900 trojúhelníků, s číslem auta tak, jak ho uvádí telemetrie, s jeho značkou, označením modelu a rokem z názvu archivu, a s koly a zadními světly. Trvá to sekundy a zapíše to asi 5 MB. Spusťte to znovu, až hra dostane nová auta. Archiv bez takového modelu (provozní rekvizita) se pojmenuje a vynechá. Formát je v [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Tvary jsou v metrech hry: 1:1 s autem. Soubor obsahuje obsah hry, takže je určen pro počítač, na kterém vznikl, a ne k předávání dál.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Tento příkaz spustí export Forzy `course` na každé složce tratě v knihovně nahraných kol a zapíše po jednom `<name>.glb`. Je jen pro Forzu. Volá přímo export Forzy a nečte `--game`, `--level` ani `--install`.

| Volba | Výchozí | Význam |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | složka, do které se zapisuje (vytvoří se, pokud chybí) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | knihovna kol |
| `--only TEXT [TEXT ...]` | všechny | jen tratě, jejichž názvy složek obsahují některý z těchto textů (bez ohledu na velká a malá písmena) |
| `--force` | vypnuto | exportovat znovu i to, co už má `.glb` |
| `--track DIR` | hledá se | jako u `course` |
| `--margin M` | 80 | jako u `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | jako u `course` |

Za složku tratě se počítá přímá podsložka knihovny, jejíž název obsahuje ` (course_`, jak ji FH Companion pojmenovává, například `Example Circuit (course_1200_3400_to_1175_3400)`. Část od ` (course_` dál se z názvu zahodí.

Jak běh probíhá:

- Trať, jejíž `.glb` už existuje, se přeskočí (`kept`), pokud není zadáno `--force`, takže přerušený běh pokračuje tam, kde skončil.
- `.glb` zapsaný starší verzí, bez vlastní vrstvy závodu a míst konání (jeho `asset.extras.course_format` chybí nebo je nižší než aktuální), se exportuje znovu, jako by pro něj byl zadán `--force`.
- Dvě složky tratí se stejným názvem před ` (course_` (nahrávač pojmenoval novou trať podle staré) se navzájem nepřepíší. Složka vytvořená dřív si nechá `<name>.glb`, druhá se zapíše jako `<name>_<start>.glb`, kde `<start>` je místo startu, s mínusy zapsanými jako `m` (například `example_circuit_m120_m340.glb`).
- Trať, která selže (nečitelná kola, nedostatek paměti, žádný terén...), se hlásí jako `FAILED` a běh pokračuje.
- Na konci vypíše tabulku stavu, velikosti v MB, sekund a názvu, pak `<n> of <total> courses in <folder>`.
- Návratový kód je 1, pokud některá trať selhala.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Vypíše každý závod, který nainstalovaná Forza definuje, z jeho definic tras (viz [Forza Horizon tratě](course-forza-horizon.md#which-race)), a zkontroluje exporty ve složce `courses` proti nim. Čte hru a knihovnu kol; nezapisuje nic kromě volitelné tabulky.

| Volba | Výchozí | Význam |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | složka, do které zapisuje `courses` a jejíž soubory se kontrolují |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | knihovna kol |
| `--track DIR` | hledá se | složka tratě, pokud není z nainstalované hry |
| `--markdown FILE` | žádný | tabulku zapsat i sem, jako Markdown |

Jeden řádek na závod a jeden na každou nahranou trať projetou na něm:

| Sloupec | Význam |
|---|---|
| route | id trasy |
| course | nahraná trať k ní přiřazená, pokud nějaká je |
| own assets | kopie, které závod přidává do volného světa |
| drawn | z nich ty, jejichž model trať dodává |
| kinds | přidané kopie podle druhu (bariéry, rekvizity, nálepky, infrastruktura, ...) |
| not geometry | značky diváků a kolizní splajny, spočítané |
| hidden | objekty volného světa, které závod odstraní |
| venue | modely země míst konání, kterými AI linie závodu prochází do 10 m |
| export | `current`, `older format` (exportováno znovu příkazem `courses`), `not exported`, nebo prázdné u závodu bez nahrané tratě |

Na konci je počet: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Toto je řez Forzy se vším zadaným ručně: dáte složku tratě a oblast, ne kolo. Hodí se, když je oblast, kterou chcete, spíš krabice než jízda.

| Volba | Výchozí | Význam |
|---|---|---|
| `<path>` | povinné | složka tratě Forzy pod `media\Tracks` (obsahuje `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | povinné | `.glb`, který se zapíše |
| `--box X0 Z0 X1 Z1` | | oblast v metrech hry (x a z, jak je hlásí telemetrie); rohy v libovolném pořadí |
| `--route FILE` | | trasa JSON s `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, jak ji zapisují `heat3d_capture route` a `heat3d_capture laps`; čte se jako UTF-8, s značkou pořadí bajtů i bez ní |
| `--margin M` | **100** | metrů přidaných kolem hranic trasy a šířka koridoru, pokud trasa obsahuje čáru |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | jako u `course` |

Zadejte přesně jedno z `--box` a `--route`, jinak je návratový kód 2. S `--route` je řez hranice trasy (`min`/`max`, x a z) rozšířená o okraj. Pokud soubor obsahuje také alespoň 10 pozic, řez se zúží na koridor široký `--margin` metrů kolem nich a umístěné modely dostanou detail podle vzdálenosti od té čáry. S `--box` se zachová celá krabice a detail jde tomu, co stojí nejblíž středu krabice.

Výška nikdy není součástí řezu. Krabice mimo mapu nebo na moři dá "no terrain there" (návratový kód 1), ne chybu o souřadnicích.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels a level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` vypíše úrovně, které nainstalovaná hra Frostbite obsahuje, podle názvu jejich tabulky (`levels/<level>/<level>.toc`), s velikostí a odkud pocházejí: `Data` pro základní hru, `Update/<pack>` pro aktualizaci, a kolik tabulek ve vysokém rozlišení k ní přidává. Úroveň, kterou přidává aktualizace, má malou tabulku chunků i v základní hře. Tabulka s bundly úrovně je úroveň (viz [Frostbite](reader-frostbite.md#which-table-is-the-level)).

`level` exportuje jednu: výškovou mapu terénu, každý mesh, který skupiny statických modelů úrovně umisťují, objekty umístěné jeden po druhém, kde stojí, a pozadí terénu kolem mapy. S `--textures` nese každý povrch svou barevnou mapu. S `--navmesh` přijdou i povrchy, po kterých chodí vojáci. Jak se to čte, je ve [Frostbite](reader-frostbite.md).

| Volba | Výchozí | Význam |
|---|---|---|
| `<level>` | povinné | název, jak ho vypíše `levels`, jeho jedinečná část, nebo cesta k `.toc` úrovně |
| `-o`, `--out FILE` | `<level>.glb` | `.glb`, který se zapíše |
| `--install FOLDER` | první hra Steam, jejíž `Data` obsahuje `layout.toc` | složka hry |
| `--textures [PIXELS]` | vypnuto; 512, pokud je uvedeno bez velikosti | zapsat barevnou mapu každého povrchu, největší mip nejvýš PIXELS na stranu, a jeho souřadnice textury tak, jak je hra má, s opakujícím se vzorkovačem (viz [Výstupní formát](output-format.md)). Výšková mapa dostane barevnou mapu pozadí terénu tam, kde ji pokrývá. Jinak dostane střední barvu povrchových materiálů terénu, a jinak průměrnou barvu pozadí kolem. Když je vypnuto, má každá část plnou barvu |
| `--ground-texture [METRES]` | vypnuto; 0.5 když je uvedeno bez velikosti | zapéct dekály terénu (silnice, dráhy, plochy, malované čáry) přes barvu země, vynásobené barevnou mapou terénu, pokud ji úroveň má, do barvy výškové mapy, METRES na pixel, v dlaždicích nejvýš 4,096 pixelů (`ground:terrain x<x> z<z>`). Funguje s `--textures` i bez něj |
| `--navmesh` | vypnuto | přidat navigační mesh úrovně pro nejmenšího agenta, vojáka (1.8 m vysokého, 0.4 m širokého), jako část `nav:walkable`: zem, podlahy, schody a střechy, na které voják dosáhne, bez spojů (skoky, žebříky, přelezy) mezi nimi |
| `--ground-spacing METRES` | 4 | nejjemnější rozteč výškové mapy; uzly jemnější než toto se převzorkují dolů. 0 výškovou mapu vynechá |
| `--detail-budget N` | každá kopie na nejhrubší úrovni, plus čtvrtina, nejméně 1,500,000 | horní mez trojúhelníků. Meshe, které stojí nejvíc, ztrácejí úroveň detailu po jedné, dokud se nevejdou. Pokud se nevejdou ani nejhrubší úrovně, vynechají se nejdřív nejmenší kopie. Pozadí terénu se nikdy nezhrubne ani nevynechá |
| `--skip TEXT` | | vynechat skupiny statických modelů, jejichž název oddílu obsahuje TEXT; opakujte pro více. Například vrstva jednoho herního režimu |
| `--by-mesh` | vypnuto | pro zjištění, co je která část: jedna část na zdrojový mesh a materiál, pojmenovaná `<part> \| <mesh> \| <material>`; mnohem větší soubor |
| `--clamped-uvs` | vypnuto | pro renderer, který neumí texturu opakovat: rozřezat každý texturovaný trojúhelník na kusy, jejichž souřadnice leží v 0..1, a trojúhelník, který by potřeboval víc než 4 kusy, nakreslit v průměrné barvě jeho textury, v části `<part> (average colour)` |

Vypíše skupiny a kolik kopií každá umístila, meshe, které vynechal, a proč, trojúhelníky na část (a s `--textures` kolik textur a kolik úseků našlo svou barevnou mapu), co je země, a s `--navmesh` kolik navigačních dlaždic přečetl. O úrovni se kromě geometrie nezapisuje nic: žádné názvy, žádná metadata (viz [Výstupní formát](output-format.md)).

Rozpočet terénu je oddělený. Výšková mapa a pozadí se kvůli `--detail-budget` nikdy nezhrubnou. Jemnost výškové mapy určuje `--ground-spacing`.

Celá úroveň je velká: typicky přes deset milionů trojúhelníků a několik set MB. `--textures` k souboru přidá jen trochu; úroveň plná stromů může dosáhnout asi 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8` dostane úroveň zhruba na třetinu.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps a ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` je složka hry, její `Content/Paks`, nebo název její složky v knihovně Steam (`"<Steam game folder name>"`). `ue-maps` vypíše každou mapu, která má vedle sebe zkompilované buňky World Partition. `ue-map` exportuje jednu jako `ground:<map>` (krajinu), `structure:<map>` (sloučené HLOD meshe mapy) a `water:<map>` (její vodní plochy tam, kde stojí nad zemí). Je to v **centimetrech** Unreal, s prohozenými osami Y a Z, jako jediný export, který není v metrech. Jak se každá čte a kontroluje: [Mapy Unreal 5](level-unreal-world-partition.md).

| Volba | Výchozí | Význam |
|---|---|---|
| `<map>` | povinné | název, jak ho vypíše `ue-maps`, nebo jedinečná část názvu |
| `-o`, `--out FILE` | `<map>.glb` | `.glb`, který se zapíše |
| `--ground-spacing METRES` | 2 | rozteč vrcholů krajiny v souboru, zaokrouhlená na celý počet jejích vlastních čtverců |
| `--no-structures`, `--no-water` | | tuto část vynechat |

Vypíše trojúhelníky na část, kolik komponent krajiny přečetl a kolik z vrcholů, které ukládají dvakrát, si neodpovídá. Mapa 3 km na 2 m má asi 4.6 milionu trojúhelníků země.

## enfusion-worlds a enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` vypíše každý svět s terénem, podle jeho složky pod `worlds/`. `enfusion-world` exportuje jeden: `ground:<world>` (terén v barvách jeho dlaždic supertextury), `water:<world>` (moře, na výšce nula) a `structure:<world>` (krabici každého umístěného modelu), v metrech hry: x na východ, y nahoru, z na sever. Jak se každý čte a kontroluje: [Světy Arma Reforger](level-arma-reforger.md).

| Volba | Výchozí | Význam |
|---|---|---|
| `<world>` | povinné | svět, jak ho vypíše `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` | `.glb`, který se zapíše |
| `--install FOLDER` | Steam knihovna, která hru obsahuje | složka hry |
| `--ground-spacing METRES` | 2 (vlastní hodnota terénu) | rozteč vrcholů terénu v souboru |
| `--texture-size PIXELS` | 4096 | větší strana barevného obrázku země; 0 pro plnou barvu |
| `--no-structures` | | umístěné modely vynechat |
| `--trees` | vypnuto | přidat i stromy a jinou vegetaci, jako krabice |

Vypíše trojúhelníky na část, kolik hraničních vrcholů dlaždic si neodpovídá, kolik entit obsahuje soubor světa a kolik krabic bylo umístěno, a co bylo vynecháno a proč.

## Proměnné prostředí {#environment-variables}

| Proměnná | Účinek |
|---|---|
| `HEAT3D_OODLE` | cesta k `oo2core_*_win64.dll`, nebo složka, která ho obsahuje; viz [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | jakákoli hodnota jiná než prázdná, `0`, `false` nebo `no` kontrolu aktualizací vypne; viz [Aktualizace](updates.md) |
| `LOCALAPPDATA` | kde se hledá knihovna FH Companion, uživatelská složka BeamNG a mezipaměť aktualizací |
| `HEAT3D_COURSE` | jen testy: trať, kterou používá test obrubníků na nainstalované hře; viz [Vývoj](development.md) |
