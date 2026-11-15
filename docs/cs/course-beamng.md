---
title: "BeamNG.drive"
nav_order: 2
lang: "cs"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Export tratě: BeamNG.drive {#course-export-beamngdrive}

Export BeamNG čte úroveň tak, jak ji hra připojuje, a pak zapíše stejný druh souboru jako export Forzy: zemi po čtvercích 512 m se zapečenou texturou, silnici a volnou zem jako samostatné části, umístěné modely podle kategorií a vodu.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Zdroje: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalace, souborový systém, scéna, terén, materiály),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) a
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (tvary).
Formáty souborů podrobně: [Soubory BeamNG](reader-beamng.md).

## Rámec kola {#the-laps-frame}

Export `course` očekává pozice BeamNG v **rámci prohlížeče**: `(x, z, -y)` světa BeamNG s osou Z nahoru, v metrech. Tak to dělá otočení, které použije nahrávač telemetrie 3DHeat. Export převede kolo zpět do rámce BeamNG (`(x, -z, y)`), pracuje tam a vše zapíše zase v rámci prohlížeče. Je to otočení, ne zrcadlení, takže nic nevyjde zrcadlově. Kolo nahrané v surovém rámci BeamNG by se neumístilo. S jinými nahrávači to nebylo testováno.

Hra se bere jako BeamNG, když soubor `heat3d-lap` říká `"game": "beamng"`, nebo když zadáte `--game beamng`.

## Hledání instalace {#finding-the-install}

- `--install <folder>`: složka, která obsahuje `gameengine.zip` a `content`.
- Jinak se zkontroluje každá knihovna Steam, zda v `steamapps\common\BeamNG.drive` obsahuje oba.
- Pokud nic nenajde: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)."

## Souborový systém {#the-file-system}

BeamNG distribuuje obyčejné zip archivy a připojuje je do jednoho souborového systému, na který odkazují úrovně (`/art/shapes/...`, `/assets/materials/...`). Export postaví totéž: jeden index bez ohledu na velká a malá písmena nad

1. `gameengine.zip`,
2. každým `*.zip` pod `content`, kromě `content\vehicles\*` a archivů, jejichž názvy začínají `art_sound` nebo `audio`,
3. uživatelským obsahem, s nejnovějším rozložením jako prvním: pod `%LOCALAPPDATA%\BeamNG\BeamNG.drive` a `%LOCALAPPDATA%\BeamNG.drive` složka `current` a nejvyšší číslovaná složka verze. Z každé z nich: `mods\*.zip`, každá složka v `mods\unpacked` a uživatelská složka sama, pokud má složku `levels`.

Pozdější přídavky vyhrávají, jako ve hře, takže mod nahradí to, co přepisuje. Mody se při exportu kola vždy zahrnou.

Cesty, které úroveň uvádí, se řeší tak, jak je řeší hra: nejdřív tak, jak jsou zadány, pak relativně k souboru, který je uvedl, a u každé také jako `.dds`, do kterého byla textura zkompilována, `.cdae`, do kterého byl `.dae` zkompilován, nebo přes soubor `.link` směřující do `/assets`.

## Která úroveň {#which-level}

Bez `--level` se každá úroveň hodnotí podle toho, kolik kola na ní leží:

- Použije se až 500 vzorků kola, rovnoměrně rozložených.
- Pro `TerrainBlock` každé úrovně se rozsah terénu přečte z prvních pěti bajtů jeho souboru `.ter`, takže úroveň, u které kolo není blízko, nic nestojí. Pokud je alespoň 30 % vzorků uvnitř rozsahu, přečtou se výšky. Vzorek se počítá jako **na** terénu, když je mezi 1 m pod ním a 3 m nad ním (`ON_GROUND`), protože referenční bod auta je jeho karoserie, ne pneumatiky.
- Pokud žádná úroveň nedosáhne 50 %, hodnotí se úrovně také podle jejich **silnic**. Některé úrovně běží za svou výškovou mapu (jejich okraje pokračují jako skalní plochy). Vzorek je na silnici, když leží v polovině šířky silnice plus 4 m (nejméně 6 m) od segmentu `DecalRoad` a mezi 2 m pod a 4 m nad ním.
- Nejlepší úroveň vyhraje, pokud dosáhne alespoň 30 %. Jinak se export zastaví a vypíše nejlepší tři: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

Konzole napíše `on <level>: 87% of the lap lies on its terrain` (nebo `roads`). `--level` se porovnává bez ohledu na velká a malá písmena s názvy složek úrovní.

## Čtení úrovně {#reading-the-level}

Z čeho se úroveň skládá, každá část ověřená proti dodaným úrovním (podrobnosti v [Soubory BeamNG](reader-beamng.md)):

- **Scéna**: `levels\<name>\main\**\*.level.json` (jeden objekt JSON na řádek, nebo pole JSON), nebo soubor `.mis` u starších úrovní. Nástroj čte objekty `TSStatic` (umístěné modely, přeskočí skryté), objekty `Prefab` (vnořené nejvýš 8 úrovní hluboko, TorqueScript `.prefab` nebo `.prefab.json`), objekty `DecalRoad` (namalované silnice), `TerrainBlock`, `WaterPlane`, `WaterBlock` a `River`.
- **Lesní položky**: `levels\<name>\forest\*.forest4.json`, typované podle záznamů `managedItemData.json`. Bariéry, ploty a skály jsou lesní položky stejně často jako stromy.
- **Terén**: výšková mapa `.ter` a její mapa vrstev.
- **Materiály**: každý `*.materials.json` mimo `levels\`, plus ty této úrovně.

## Koridor a silniční dekály {#the-corridor-and-the-road-decals}

Koridor je `--margin` metrů kolem kola v rovině x/y BeamNG (viz [Export tratě](course-export.md#the-corridor)). Koridor dosahu `margin + 60 m` vybere kandidáty.

**Silniční dekály** (`DecalRoad`) tvoří většinu silnic BeamNG: jsou namalované na terénu, ne modelované. Dekály, jejichž rozsah se dotýká koridoru dosahu, se vezmou v pořadí kreslení hry (sestupně `renderPriority`, pak pořadí v souboru) a rozloží se jako pásy:

- Uzly (x, y, z, šířka) se interpolují **centripetální Catmull-Romovou** křivkou přibližně každý 1 m. Uniformní druh se na sebe uzavírá, kde se uzly shluknou v zatáčce. Uzavřené silnice se uzavřou.
- Každý okraj vezme výšku terénu tam, kde je terén do 1.5 m od výšky vlastní silnice, a jinde ponechá výšku silnice (na mostě).
- Název materiálu rozhodne, co dekál maluje:

| Druh | Název materiálu odpovídá (vyhrává první shoda) |
|---|---|
| stopy pneumatik | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| překryv (kosmetický) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| značení | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| volný povrch | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| silnice | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| překryv | cokoli jiného |

## Země {#the-ground}

Výškové pole terénu uvnitř koridoru se změní na trojúhelníky:

- Jeden čtyřúhelník na čtverec terénu, jehož střed je v koridoru. Čtverce s vrstvou 255 (díry) se přeskočí. Každý čtyřúhelník jsou dva trojúhelníky, s úhlopříčkou střídavě tak, jak to dělá terén Torque.
- Výšky jsou `position.z + h * maxHeight / 65535`. Normály vzniknou z rozdílů výšek.
- Každý čtverec se zařadí podle své **vrstvy**: název vrstvy s modelem země a poznámkou jejího materiálu terénu. Dlážděná slova ji dělají `road`, `grass/forest/rock/moss/leaves/cliff/stone` ji dělají `terrain` a volná slova ji dělají `loose` (štěrk a hlína). Cokoli jiného je `terrain`.
- Potom **silniční a volné dekály přepíší čtverce, které pokrývají**, v pořadí kreslení, takže rozhodne poslední namalovaný dekál.
- Vrcholy se dělí po čtvercích 512 m (`floor(x / 512)`, `floor(y / 512)`), takže každá část se mapuje přesně do jednoho obrázku: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konzole vypíše `what the ground is made of` s počty trojúhelníků podle druhu.

### Modelovaný povrch jízdy {#modelled-driving-surface}

Okruhy BeamNG jsou často modely stejně jako terén. Dráha závodní trati může být jeden mesh s čarami, pneumatikovými stopami a vibrujícími pásy jako vlastními meshi navrch. Umístěné modely v kategoriích silnice, obrubníky, krajnice, rekvizity a mosty se tedy prohledají na povrch jízdy. Pro každý materiál:

| Povrch | Rozhoduje (první shoda) |
|---|---|
| stopy pneumatik | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` v názvu, typu země nebo poznámce |
| značení | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` v názvu materiálu |
| obrubníky | `rumble`, `kerb`, `curb` |
| silnice | typ země `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, nebo název obsahuje `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| volný povrch | typ země `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| krajnice | `sidewalk` |
| (vlastní kategorie modelu) | pro modely už zařazené jako silnice, obrubníky nebo krajnice |

Z těchto materiálů se trojúhelníky **směřující nahoru** (normála z větší než 0.5) uvnitř koridoru vyjmou z modelu a stanou se zemí. Namalují se do zapečené textury dlaždice a zapíší se jako části jako `ground:road 3_-2 asphalt_light`. Značení a stopy pneumatik se jen malují. Zbylé trojúhelníky modelu zůstanou u modelu. Tyto modely se nikdy nezjednodušují ani nevynechávají kvůli rozpočtu, protože hrubá trať je špatná trať.

## Zapečená textura země {#the-baked-ground-texture}

Každý čtverec 512 m, který má zemi, dostane jeden obrázek o `--texture-size` pixelech (2048 = 25 cm na pixel), vykreslený tak, jak hra kreslí svou zem:

1. **Vrstvy terénu.** Pro každý pixel se vrstvy čtyř okolních čtverců terénu bilineárně smísí. Každá vrstva se obarví tak, jak ji obarvuje hra: **základní mapa** materiálu roztažená přes `diffuseSize` metrů (nebo přes celý terén), pak **detailní** a **makro** mapy jako šedé překryvy (`colour * (1 + strength * (2 * overlay - 1))`, 0.5 neutrální). Jejich výchozí hodnoty se opakují každé 2 m a 60 m, se silou 0.5 a 0.3, pokud materiál neříká jinak. Vrstva bez materiálu dostane plnou barvu svého povrchu. Řádek 0 základní mapy je sever.
2. **Silniční dekály**, které jsou namalované jen na terénu, v pořadí kreslení, každý se svou texturou, mapou průhlednosti, odstínem a průhledností, podél pásu. Úrovně distribuované s nimi používají priority kolem 12-16 pro asfaltové podklady, 10 pro značení a 4 pro gumu.
3. **Modelovaný povrch jízdy** shora: nejdřív podklady, pak překryvy, každý v opakující se textuře modelu na jeden texel na pixel zapečení.
4. **Dekály, které se promítají i přes předměty** (`overObjects`), jako poslední.

S `--no-textures` se nic nezapéká: části země dostanou plné barvy a modelované značení a stopy pneumatik se stanou vlastními částmi zvednutými o **3 cm**.

## Umístěné modely {#placed-models}

Kandidáti jsou všechny `TSStatic`, potomci prefabů a lesní položky, jejichž počátek leží v koridoru dosahu. Model se kreslí, pokud se jeho světový ohraničující kvádr tvaru dotýká koridoru.

**Kategorie** pochází z vlastní poznámky úrovně a z cesty tvaru. Vyhrává první pravidlo, které sedí:

| Kategorie | Poznámka | Cesta nebo název obsahuje |
|---|---|---|
| pozadí (nikdy nekresleno) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| obrubníky | | `kerb`, `curb`, `rumble` |
| silnice | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| krajnice | `SIDEWALK`, `COBBLESTONE` | |
| stromy (jen s `--trees`) | `NATURE` | tree, foliage, bush, grass, plant a podobná slova |
| skály | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| bariéry | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| značky | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| mosty | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktura | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| budovy | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekvizity | | cokoli jiného |

**Tvary** se čtou ze zkompilovaného `.cdae`, nebo z Collada `.dae`, pokud žádná mezipaměť neexistuje (mody). Tvar, který nejde přečíst, se počítá: `N copies of M models could not be read`. Materiály pojmenované nebo texturované `invisible`, `collision` nebo `nodraw` se nikdy nekreslí.

**Textury.** Modely se seskupují podle kategorie a materiálu do částí pojmenovaných `structure:<category> <material>` (nebo `ground:kerbs <material>`). Skupina dostane barevnou texturu svého materiálu nejvýš na **256 px**, jen pokud její UV zůstávají v 0-1 (98 % vrcholů v rozsahu -0.02 až 1.02). Prohlížeč balí textury do atlasu a jednu nemůže opakovat. Skupina, jejíž textura se opakuje, se kreslí v průměrné barvě textury (vážené alfou, v sRGB, krát odstín materiálu), nebo v barvě kategorie, pokud nemá texturu.

**Detail** se řídí sdíleným schématem v [Úrovně detailu a rozpočet](detail-budget.md). Úrovně detailu BeamNG jsou `details` tvaru (nejdřív největší velikost v pixelech). Nad rozpočtem jdou první nejvzdálenější kopie. Obrubníky a modely nesoucí povrch jízdy se nikdy nezjednodušují ani nevynechávají.

`--no-placed` zahodí konstrukce, ale ponechá modelovaný povrch jízdy. `--trees` přidá kategorii stromů.

## Voda {#water}

| Zdroj | Vykresleno jako |
|---|---|
| `WaterPlane` (moře) | čtyřúhelník 4 m na výšce vody pro každou buňku koridoru, kde terén tu výšku nedosáhne |
| `WaterBlock` | jeden čtyřúhelník, jednotkový čtverec na lokálním z = 0 v transformaci bloku (takže jeho měřítko nastaví velikost), pokud se dotýká koridoru; zda z = 0 je povrch bloku, není ověřeno |
| `River` | pás přes jeho uzly, pokud se dotýká koridoru |

Veškerá voda je jedna plochá část, `water:water`.

## Nekresleno {#not-drawn}

- Pokryv země (procedurální tráva).
- Kulisy umístěné po okraji světa (`backdrop` a podobné).
- Opakující se textury modelů, které vyjdou jako průměrná barva (viz výše).
- Skinované meshe (vozidla, postavy) a meshe dekálů uvnitř tvarů.

## Kontroly za tím {#checks-behind-it}

Jak je uvedeno ve zdrojovém kódu, změřeno na dodaných úrovních:

- Uzly silnic leží na terénu do 1-2 cm (medián) na zkontrolovaných úrovních, s `h * maxHeight / 65535` a řádky podél +y. `h / 32` nebo jiné pořadí os minou o desítky až stovky metrů.
- Železniční úseky řetězené podél silnice běží podél řádku 0 `rotationMatrix` (naprostá většina).
- Rotace uzlu `.cdae` se musí transponovat. S tím se ohraničující kvádry světa shodují se zdrojovým `.dae` na milimetr. Učebnicový postup by byl o 38 cm mimo (medián).
- Exportováno na několika dodaných úrovních všech druhů, každé za sekundy až minuty.
