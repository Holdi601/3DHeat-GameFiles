---
title: "Forza Horizon"
nav_order: 1
lang: "cs"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Export tratě: Forza Horizon {#course-export-forza-horizon}

Export Forzy čte trať přímo z archivů ForzaTech ve hře: terén, kde jsou silnice, krajnice a tráva odlišeny, zemi zapečenou z mapy země samotné hry a každý umístěný model ve vlastní textuře (obrubníky, svodidla, zábrany z pneumatik, značky, rekvizity, budovy). Také zjistí, na kterém ze závodů hry bylo kolo najeto, a přidá to, co hra pro ten závod vykresluje sama (jeho vrstvu událostí: bariéry, stany, portály, tribuny, vlajky), a zemi každého místa konání, přes které jízda vede, například podlahu stadionu.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Zdroje: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Samotné formáty kontejnerů jsou na [ForzaTech](reader-forzatech.md).

## Hledání nainstalované hry {#finding-the-installed-game}

Nikdo by neměl psát cestu jako
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, takže se cesta zjistí sama:

1. **Knihovny Steam.** Čte se `config\libraryfolders.vdf` ze složky `C:\Program Files (x86)\Steam` nebo `C:\Program Files\Steam`. Každý záznam `"path"` v něm je knihovna. Prohledá se `steamapps\common` každé knihovny.
2. **Microsoft Store.** Prohledá se `C:\XboxGames`, pokud existuje. Tam je hra o jednu úroveň hlouběji, v `<game>\Content`.
3. **Složka hry** je každý podřízený prvek těchto složek, který má složku `media\Tracks`, ať se jmenuje jakkoli.
4. **Složka tratě** je každá složka pod `media\Tracks`, která obsahuje `GeoChunk0.minizip`. Počítá se podle obsahu, ne podle názvu, takže se najde i trať pod názvem, který nikdo neviděl.

Pokud je hra jinde, předejte složku tratě přes `--track`. Viz [Řešení potíží](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` všechno to přeskočí.

Složka tratě obsahuje, co export čte:

| Soubor | Co to je |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | archivy: každý model, textura a soubor umístění, bez názvů uvnitř |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | jeden řádek na položku archivu, v pořadí položek: jediný zdroj názvů |
| `AssetManifest.xml` | každá textura, kterou trať obsahuje, s hashem, kterým na ni materiály odkazují |

## Která trať {#which-track}

Hra obsahuje víc složek tratí (otevřený svět, garáž nebo dvě). Správná se vybírá **podle souřadnic, ne podle názvu**:

- Otázkou je ohraničující kvádr kola, rozšířený o `--margin`.
- Pro každou složku tratě se čtou čtyři manifesty `ChunkContentsMiniZip*.txt` jako text, bez otevírání archivu. Každý název terénní dlaždice (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) nese svou pozici v mřížce. Nástroj spočítá, kolik různých dlaždic leží uvnitř kvádru.
- Vyhrává trať s nejvíce dlaždicemi. Pokud žádná nemá žádnou, export se zastaví s hláškou "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Celá trať se vyřídí za necelou sekundu. Shoda podle názvu by mohla vybrat špatnou mapu, a špatná mapa vypadá stejně věrohodně jako správná.

Konzole napíše `on <track>, in <game folder>`.

## Který závod {#which-race}

Hra vydává každý ze svých závodů jako trasu s číslem, svým **id trasy**. Ke každé trase patří dva soubory:

| Soubor | Co obsahuje |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | AI jízdní linie závodu: uzel o 56 bajtech od bajtu `0x60`, počet uzlů na `0x24`, každý uzel začíná svou pozicí (x, y, z) v metrech hry |
| `media\Stripped\gs\<map>\routedefinitions.zip` | jeden `route<id>_<map>.rtd` na závod: prostý XML, který vypisuje, co závod do světa přidává a co z něj odebírá (viz [Vlastní vrstva závodu](#the-races-own-layer)) |

Kolo se páruje s trasou porovnáním s každou AI linií, jejíž kvádr se překrývá s kvádrem kola:

- Od každého vzorku kola vzdálenost k nejbližšímu bodu linie; a od každého bodu linie vzdálenost k nejbližšímu vzorku kola.
- Oba mediány se sečtou. Trasa s nejmenším součtem vyhrává, pokud je součet menší než **30 m** (`MATCH`).
- Potřebné jsou oba směry: krátký sprint leží podél dlouhého závodu, který používá stejnou silnici, a dlouhé kolo pokrývá krátkou trasu.

Konzole napíše `the game's route <id> (driven line within <n> m of it)`, nebo že žádná trasa neodpovídá. Bez shody se umístí jen volný svět.

## Terén {#terrain}

Jak se terén nachází (v `forzaterrain.py`):

- Manifesty pojmenovávají terén jako prostorový index: `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Obě čísla jsou souřadnice mřížky, které se posouvají po **1023**, a každý krok mřížky je dlaždice **512 m**. Dlaždice `x-2046` je `-2046 / 1023 = -2`, která začíná na `-2 * 512 = -1024` m. Kdyby se názvy četly jako metry, každé hledání by minulo o faktor dva a přesto by vrátilo terén, z jiné části mapy.
- Dlaždice se může objevit třikrát: obyčejná, `_cb` a `_ul`. Všechny tři pokrývají tutéž zem. Bere se jedna na dlaždici, v tomto pořadí přednosti, protože sloučení by ztrojnásobilo geometrii do splývajících ploch.
- Dlaždice se čte jen tehdy, když se dotýká kvádru kola **a** koridoru. Dlaždice, které se koridor nedotýká, se nikdy nedekomprimuje.
- Každý `.modelbin` vybrané dlaždice se dekóduje jen na **úrovni detailu 0**. Dlaždice nese čtyři úrovně nad stejnou zemí, a kdyby se exportovaly všechny, stejný čtvereční metr by byl v souboru čtyřikrát.
- Každý mesh nese vlastní měřítko a posun ve světových souřadnicích, takže dlaždice přistane tam, kam ji hra klade, bez transformace instance. Trojúhelníky, jejichž otisk se překrývá s kvádrem, se zachovají, a pak jen ty, které zasahují do koridoru.
- Mesh ve formátu, který čtečka odmítne, se přeskočí a počítá se (`N meshes could not be read`), takže slabý výsledek říká proč.

Souhrn terénu vypíše počet vrcholů, počet trojúhelníků, počet meshů, počet dlaždic a rozsah x/y/z.

### Silnice, krajnice, země, značení, voda {#road-verge-terrain-markings-water}

Názvy materiálů neřeknou, kde je silnice. Kolem okruhu 94 % země používá materiál s shaderem silnice, protože terén blízko silnice se kreslí jím a shader rozhodne po pixelech asfalt nebo trávu. Proto:

| Druh | Rozhoduje |
|---|---|
| pás silnice | **rozložení vrcholů**: pásy silnice jsou jediná země s druhou sadou UV (kanál 1); trojúhelník, jehož tři vrcholy ji všechny mají, je silnice |
| asfalt vs. krajnice | uvnitř pásu silnice **maska asfaltu** dlaždice v těžišti trojúhelníku: 0.5 nebo víc je `road`, méně je `verge` |
| značení | shoda názvu materiálu s `whiteline`, `yellowline` nebo `decal` |
| stopy pneumatik | shoda názvu materiálu s `tyremark` nebo `skid` (kontroluje se před značením, protože stopy pneumatik se dodávají jako `tyremark_decal_*`) |
| voda | shoda názvu materiálu s `water`, `lake`, `river`, `paddy`, `ocean` nebo `sea` |
| terén | vše ostatní |

Naměřeno na zaznamenaných kolech testovacího okruhu přistane skoro každý vzorek na trojúhelnících pásu silnice a velká většina na asfaltové části, jakmile maska oddělí krajnici.

Maska asfaltu existuje jen tehdy, když se zapékají textury země. S `--no-textures`, nebo u dlaždice, jejíž mapy chybí, zůstanou pásy silnice celé jako `road` a žádná krajnice se neoddělí. Chybějící mapy stojí detail, nikdy geometrii.

### Malované vrstvy jsou zvednuty {#painted-layers-are-lifted}

Značení jízdních pruhů a stopy pneumatik se dodávají jako vlastní trojúhelníky ležící přesně na silnici. Hra je kreslí s hloubkovým posunem. Kdyby se kreslily tak, jak jsou, silnice a barva by se přetahovaly o každý pixel. Export dá každé části značení a stop pneumatik vlastní kopii jejích vrcholů, zvednutou o **5 cm** (`DECAL_LIFT`) podél normály povrchu, takže silnice pod ní není zvednutá také.

### Normály {#normals}

Normály terénu pocházejí z archivu. X normály je uloženo jako čtvrtý short pozice, Y a Z v atributu `NORMAL` (viz [ForzaTech](reader-forzatech.md)). Pokud nějaký vrchol v extrakci nemá normálu, počítají se normály pro celou zem z trojúhelníků.

## Zemní textura {#the-ground-texture}

Každá dlaždice terénu nese tři mapy pokrývající její čtverec 512 m, v pěti rozlišeních (`_quality1` až `_quality5`, největší 2048 px, což je 25 cm na pixel):

| Mapa | Vzor názvu souboru | Co obsahuje (naměřeno) |
|---|---|---|
| hlavní | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detailní normála (x, z). A: nižší na asfaltu a na drsném povrchu |
| podřízená | `submap_x<X>_z<Z>_x<season>x_diff` | váhy vrstev. B: vysoké na asfaltu (239 na jízdní linii, 165 vedle ní) |
| lesk | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: nízké na asfaltu (147 proti 215). B: roste v lese |

Žádná z těchto map není barevná fotografie. Jsou to vstupy, kterými shader terénu hry míchá své materiálové vrstvy, a tyto vrstvy se nedekódují. Zapečená textura je proto **interpretace, ne kopie vzhledu hry**. Drží *kde* je který druh země, na 25 cm, a maluje ji pevnými barvami:

| Země | Lineární RGB | Váha |
|---|---|---|
| tráva (krátká, u trati) | 0.30, 0.44, 0.18 | základ |
| drsná (dál) | 0.40, 0.42, 0.22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| les | 0.13, 0.23, 0.10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0.20, 0.20, 0.21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Pro asfalt musí souhlasit obě mapy. Jedna sama o sobě nechá šedé skvrny v trávě všude, kde komprese bloků dělá kruhy. Výsledek se stíní detailní normálou hlavní mapy proti pevnému světlu (`0.55 + 0.6 * lambert`), takže hrany obrubníků, svahy a koleje se čtou jako reliéf, a zapíše se jako 8bitové sRGB.

Orientace: řádek 0 obrázku je **severní** okraj dlaždice (největší z), sloupec 0 její **západní** okraj (nejmenší x). Zjistilo se to tak, že se zaznamenaná kola promítla na masku asfaltu všemi osmi způsoby, jak lze čtverec převrátit nebo otočit. Právě jeden způsob je položí na asfalt. Z toho plynou UV: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Mapy se čtou v nejlepším dostupném rozlišení až do kvality 5 a převzorkují se na velikost hlavní mapy. Je-li barevný obrázek větší než `--texture-size`, pak se zmenší na tuto velikost Lanczosovým filtrem. Maska asfaltu se vždy drží v plném rozlišení, protože rozhoduje o geometrii. `--season` vybírá mapy `x<season>x`. Dlaždice bez map pro dané období se kreslí v plných barvách a konzole hlásí `N without maps`.

## Umístěné modely {#placed-models}

Terén nese svou vlastní světovou pozici. Nic jiného ne. Kde stojí každá kopie modelu, je zapsáno v souborech umístění `.pgeo`, jeden na kategorii na prostorovou buňku:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Rozložení záznamu je na [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Co se čte {#what-is-read}

- Soubory umístění se filtrují **podle názvu**: velikost buňky a pozice buňky v cestě dávají čtverec buňky (`x * size` až `(x + 1) * size`), a otevřou se jen buňky, které se překrývají s kvádrem kola, v požadované kategorii.
- Kategorie výchozí: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` přidá `trees`, `bushes` a `smashables`. Tyto se nikdy nečtou: `grasstemplate`, `crowdtemplate` a `cwdspline` (tráva a diváci: hra je kreslí jako animované sprity, nemají geometrii).
- Každý soubor patří do **vrstvy**, přečtené z názvu za `c<size>_<category>_`. Slovo úrovně detailu (`do`, `so`, `ulc`, `ulp`, `cwd`) a volitelné číslo sekce je volný svět. Cokoli jiného je vrstva, kterou hra zapíná: běhová vrstva (`rt_0`), aktivita (`_tag_<name>_`), sběratelský předmět, cokoli zařazeného pod `evolving`. Vrstva, která pojmenovává trasy (`rt_x<id>`, například `rt_x1023_x2201`), patří jen těm závodům a čte se jen tehdy, když kolo odpovídalo jednomu z nich. Viz [Zapnuté vrstvy](#switched-on-layers).
- Kopie se ponechá, pokud je její pozice uvnitř kvádru a uvnitř koridoru. Přesné opakování (stejná pozice a orientace na milimetr, zapsané dvěma sousedními buňkami) se sloučí.
- **Obrubníky** jsou rekvizity, jejichž název modelu začíná `road_gen_rum` (vibrační pásy). Zapisují se jako `ground:kerbs`, nikdy se nezjednodušují ani nevynechávají, protože podle nich se měří kolo.

| Kategorie | Část | Záložní barva (bez textury) |
|---|---|---|
| obrubníky | `ground:kerbs` | 0.60, 0.12, 0.10 |
| bariéry | `structure:barriers` | 0.50, 0.50, 0.50 |
| rekvizity | `structure:props` | 0.45, 0.35, 0.25 |
| značky | `structure:signs` | 0.70, 0.70, 0.70 |
| budovy | `structure:buildings` | 0.55, 0.52, 0.48 |
| infrastruktura | `structure:infrastructure` | 0.45, 0.45, 0.47 |
| mosty | `structure:bridges` | 0.45, 0.45, 0.45 |
| skály | `structure:rocks` | 0.30, 0.28, 0.25 |
| rozbitné | `structure:smashables` | 0.12, 0.22, 0.06 |
| stromy, keře | `structure:trees` | 0.10, 0.20, 0.05 |

### Geometrie modelu {#the-models-geometry}

Umístěný název `<model>_3D` odkazuje na soubory modelu `<model>_cluster###.i.modelbin` (až tucet). Každý trojúhelník nese masku úrovní detailu, do kterých patří:

- Úrovně modelu jsou jeho trojúhelníky výslovně označené pro danou úroveň. Úrovně jdou souvisle od 0, nejjemnější první.
- Trojúhelníky označené `0xFFFF` (všechny úrovně) jsou rozbitné kusy, například sloupky svodidla nebo jednotlivé pneumatiky věže z pneumatik. Překrývají celý model a hra je kreslí místo něj, jakmile je model rozbit. Používají se jen u modelu, který nemá žádnou výslovně označenou úroveň.
- Podsítě, jejichž materiálový shader je promítaný **dekál**, se vynechají.

Každá kopie se umístí svou pozicí, svými osami x a y ze záznamu (z = x krát y) a svým měřítkem. Normály se transformují inverzí měřítka.

### Která textura {#which-texture}

Materiál nepojmenovává své textury. Vypíše je jako hashe a `AssetManifest.xml` trati mapuje každý hash (`SourceHash`) na název textury. Čte se jen sekce `<Textures>`, čtení se zastaví u `</Textures>` v souboru, který může mít desítky megabajtů. Pak:

1. Slot `0x88B483AA` je základní barva ve standardním environment shaderu (každý vzorkovaný materiál). Pokud na něj materiál váže texturu, použije se ta.
2. Jinak rozhoduje druh textury samotné, což je slovo před jejím GUID: `_bclr_`, pak `_diff_`, pak `_colour_`.
3. Terénní mapy (`mainmap`, `submap`, `autogloss`) a palety odstínů (`tint`, `worldtint`) nikdy neobarvují model.

Model se tedy barví podle toho, co jeho materiál váže, ne podle textury pojmenované jako model. Například `bar_rur_armco_crct_02_c` používá texturu `..._02_a`.

Textura se čte z archivů v nejmenším rozlišení, které má alespoň **256 px** na šířku (`MODEL_TEXTURE`), zmenšená na 256, je-li větší, a uložená jako RGB JPEG v `.glb`. Barva zábradlí na 256 px na čtyři metry má 1.6 cm na pixel, a kolem 80 takových textur se vejde do atlasu prohlížeče vedle dlaždic země.

**Roční období.** `--season` vymění texturu za její sezónní dvojče podle názvu, GUID se ignoruje (`..._xsummerx_bclr` na `..._xwinterx_bclr`, nebo `..._bclr` na `..._winter_bclr`), pokud ji trať má. S `--season winter` se zimní materiál podsítě použije také tam, kde ho uvádí její tabulka variant.

**Varianty.** Záznam podsítě začíná tabulkou dvojic `(summer, winter)` materiálů, jeden pro každý vzhled, v jakém se kopie může objevit: pět potisků pro billboard, šest barev nátěru pro věž z pneumatik. Každý záznam umístění říká, jakou variantu kopie nosí. Podsíť s méně variantami, než má model, si svoje varianty opakuje.

**Blok zástupce.** Sdílené atlasy budov vyhrazují plný blok RGB (255, 64, 0) pro povrchy, které shader budovy obarví z jiných textur. Pokud více než dvacetina textury leží do 12 úrovní od této barvy, blok se přemaluje průměrnou barvou textury. Jinak by město vyšlo oranžové.

### Průhledné povrchy {#see-through-surfaces}

Plotové sítě a sítě jsou jednoduché čtyřúhelníky s dírami v alfě textury. Vykreslené plně, je plot zeď přes výhled na trať. Povrchy, jejichž materiálový shader odpovídá `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` nebo `tree`, se testují:

- Průhlednost textury se zprůměruje přes mřížku 32 x 32.
- Pro každý povrch (každý trojúhelník s výřezem sdílející jednu texturu) se čtyři body na trojúhelník vzorkují v prostoru UV a váží se plochou UV trojúhelníku.
- Pokud je průměrná průhlednost alespoň 0.05 a menší než **0.5**, celý povrch se vynechá. Pod 0.05 alfa znamená pro jeho shader něco jiného (varovná značka, která vzorkuje 0.01), a povrch se ponechá plný.
- Model, jehož všechny povrchy byly vynechány, se nahlásí: `N models left out as see-through (mostly holes in their texture)`.

Nástroj posuzuje celý povrch, ne jednotlivé trojúhelníky. Posuzováno po trojúhelnících by polovina každého čtyřúhelníku přežila a ploty by vyšly jako řady zubů.

### Budovy vykreslené celé {#buildings-drawn-whole}

Město staví budovy z modulárních dílů: stovky tisíc kolem jednoho pouličního okruhu, desítky milionů trojúhelníků i v nejhrubší úrovni. Vynechávat díly po jednom nechávalo osamělé stěnové desky stát. Hra také dodává celé náhrady budov v `scene\hlod_tier_1\`, jeden mesh na budovu (kmen `hlod_tier_1_*`), už ve světových souřadnicích jako terén:

- Světový kvádr každé náhrady se přečte z pozičního kvádru jejího meshe (čtení hlavičky, ne dekódování). To trvá sekundy pro celou mapu.
- Náhrady, které se dotýkají kvádru kola a koridoru, se použijí.
- Každý díl `buildings`, jehož pozice padne do půdorysu náhrady (plus 0.5 m), se zahodí a místo něj se nakreslí náhrada. Její vzdálenost od jízdy se měří k nejbližší hraně budovy.
- Souhrn říká `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Zapnuté vrstvy {#switched-on-layers}

Co umisťuje zapnutá vrstva, se exportuje, ale odděleně od volného světa, aby ji prohlížeč mohl ukázat nebo skrýt:

| Vrstva | Část |
|---|---|
| volný svět | `structure:<category>` (jako dřív) |
| vrstva pojmenovávající trasu odpovídajícího závodu | `structure:event_<category>` |
| jakákoli jiná zapnutá vrstva | `structure:layer_<category>` |

Souhrn je počítá: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modely už ve světových souřadnicích {#models-already-in-world-coordinates}

Některé druhy modelů nejsou v žádném souboru umístění. Jejich meshe nesou vlastní světovou pozici, jako terén, takže je nic nemusí umisťovat:

| Složka pod `scene\models\` | Co to je | Část |
|---|---|---|
| `plots` | vlastní země místa konání: podlaha a střed stadionu, festivalový areál, náměstí | `ground:venue` |
| `plinths` (a jakýkoli model pojmenovaný `floor`, `ground` nebo `road`) | země, kterou je ulice ozdobena: květináče, schody, dlažba parku | `ground:plinths` |
| `hda_infrastructure` (mosty) | procedurálně postavené mosty | `structure:bridges` |

- Model se počítá jako ve světových souřadnicích, když střed jeho kvádru leží více než **300 m** (`WORLD_REACH`) od jeho vlastního počátku. Modely umístěné soubory umístění leží do pár set metrů od svých počátků.
- Nekreslí se: okluzory, kabely napnuté podél silnic, pozadí moře, střechy a okluzory modulárních budov (náhrady ty budovy kreslí), kolize a objemy vody.
- Každý se čte z kvádru svých meshů (čtení hlavičky), několik sekund pro celou mapu, jednou za běh.
- Části země se nikdy nekreslí hrubší a nikdy se kvůli rozpočtu nevynechají, stejně jako obrubníky.

**Místo konání se řeže celé.** Když jízda zasahuje do vlastní země místa konání (`ground:venue`), koridor se rozšíří na celou plochu té země plus `--margin`, takže tribuny, zdi a zábrany kolem stadionu přijdou s ním, ne jen pás, který kola použila. Konzole napíše `through a venue (<model names>): cutting all of its ground, <n> km2`. Plinthy koridor nerozšiřují.

### Podrobnosti a rozpočet {#detail-and-the-budget}

Pásy vzdálenosti, rozpočet a které kopie odejdou, když je rozpočet příliš malý, jsou na [Úrovně detailu a rozpočet](detail-budget.md).

### Souhrn umístění {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## Vlastní vrstva závodu {#the-races-own-layer}

Mnohé závody vydávají věci, které ve volném světě nejsou: betonové zdi a ploty, které uzavírají vedlejší silnice, věže z pneumatik, stany, startovní portál, tribuny, vlajky, transparenty. Každý závod je uvádí ve své definici trasy (`route<id>_<map>.rtd` v `routedefinitions.zip`, prostý XML v prostém zipu):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Co se přidá.** Každá instance se umístí jako kopie ze souboru umístění. Šestnáct čísel transformace jsou čtyři řádky: osy x, y a z modelu (každá vynásobená měřítkem) a jeho pozice v metrech hry. Třetí řádek je vektorový součin prvních dvou. `Material` je varianta, kterou kopie nosí. Část je `structure:event_<kind>`, kde `<kind>` je složka pod `scene\models\` (barriers, props, infrastructure, signs; cokoli jiného se počítá jako props), a uzel nese extras glTF `{"layer": "event", "route": <id>}`.
- **Co se odebere.** Volná kopie stojící do **0.1 m** od pozice skryté položky se vynechá. Skrytá položka stojící v počátku je model ve světových souřadnicích; její GUID instance se vyhledá v `AssetManifest.xml` trati (seznam `<Models>`: zdroj modelu, pak GUID jeho kopií), aby se pojmenovala.
- **Země, kterou závod skrývá, se zachová.** Závod, který skrývá zemi místa konání, na tom místě položí vlastní povrch. Když tento povrch není mezi modely, které trať dodává, skrytá země zůstane jako nejbližší věc k tomu, po čem se jede, a souhrn to říká (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Nekreslí se, ale počítají se.** Značky diváků (`crowd_proxies`: hra z nich kreslí dav jako sprity) a kolizní splajny (`.splinecol`). Konzole je vypíše: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Modely, které trať pro trasové prvky nedodává (světelné záře, některé značky, obsah, který hra streamuje), se pojmenují v `placed names have no model in the archives`.

Umísťují se jen kopie uvnitř koridoru, jako u všeho ostatního.

## Zápis souboru {#writing-the-file}

Části se zapisují v tomto pořadí: pro každou dlaždici `terrain`, `verge`, `road` (každá s obrázkem dlaždice), pak `water`, `tyre marks`, `markings` (naplocho, poslední dvě zvednuté), pak každá umístěná část seřazená podle názvu. Souřadnice jsou hry vlastní (metry, Y nahoru). Viz [Výstupní formát](output-format.md).

Soubor říká, co obsahuje, ve svém `asset.extras` glTF:

| Pole | Význam |
|---|---|
| `course_format` | `2`: vlastní vrstva závodu, místa konání a modely ve světových souřadnicích jsou v něm. [`courses`](commands.md#courses) exportuje soubor s nižším číslem (nebo bez něj) znovu |
| `route` | id odpovídající trasy, nebo `null` |
| `event_copies`, `event_kinds` | kolik kopií vlastní vrstvy závodu se umístilo, a jejich druhy |
| `hidden` | volné kopie, které se vynechají, protože je závod odebírá |
| `venue` | modely země míst konání, přes která jízda prochází |
| `layers` | umístěné zapnuté vrstvy |

## Co to stojí {#what-it-costs}

Hrubé řády velikosti:

| Trať | Výsledek |
|---|---|
| krátký okruh na venkově | několik set tisíc trojúhelníků terénu, přes milion umístěných; sekundy, pod 100 MB |
| dlouhý bodový sprint | koridor je malý zlomek kvadru kolem něj; asi minuta, několik set MB |
| městský okruh v ulicích | tisíce bariér, rekvizit a značek a celé budovy; s automatickým rozpočtem až několik stovek MB |

Čtvereční kilometr terénu otevřeného světa je asi milion trojúhelníků.

## Kontroly za tím {#checks-behind-it}

Toto jsou měření provedená při psaní čtečky, jak je uvedeno ve zdrojovém kódu. Testy je nespouštějí, pokud hra není nainstalovaná.

- Na testovacím okruhu sedí auto asi na své jízdní výšce nad extrahovanou zemí (medián pod 0.2 m).
- Každá vzorkovaná dlaždice přistane uvnitř čtverce 512 m, který předpovídá její název.
- Po sobě jdoucí umístění svodidel jsou přesně 4 m od sebe a většina konců svodidel leží do 5 cm od začátku dalšího.
- Obrubníky sedí několik centimetrů nad extrahovanou zemí, čelem nahoru, do 5 m od jízdy (také test na nainstalované hře, viz [Vývoj](development.md)).

## Nekresleno {#not-drawn}

- Stromy a keře, pokud není `--trees`. Tráva a davy nikdy (hra je kreslí jako sprity).
- Modely závodu, které trať nedodává (viz [Vlastní vrstva závodu](#the-races-own-layer)).
- Promítané materiály dekálů na modelech.
- Potisky značek, které jsou alfa-smíšené přes svou desku, vyjdou neprůhledné.
- Barva země je rekonstrukce toho, kde je asfalt, tráva a les, ne vlastní terénní materiály hry.
