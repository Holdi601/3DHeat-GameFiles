---
title: "BeamNG.drive"
nav_order: 2
lang: "sk"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Export trate: BeamNG.drive {#course-export-beamng-drive}

Export BeamNG číta level tak, ako ho hra pripája, a potom zapíše rovnaký druh
súboru ako export Forzy: zem po štvorcoch 512 m s pečenou textúrou, cesta a
voľná zem ako samostatné časti, umiestnené modely podľa kategórií a voda.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Zdroje: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (inštalácia, súborový systém, scéna, terén, materiály),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) a
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (tvary).
Formáty súborov podrobne: [Súbory BeamNG](reader-beamng.md).

## Rámec kola {#the-lap-s-frame}

Export `course` očakáva pozície BeamNG v **rámci prehliadača**:
`(x, z, -y)` svetu BeamNG so Z hore, v metroch. To je rotácia, ktorú
telemetrický nahrávač 3DHeat použije. Export previede kolo späť do rámca BeamNG
(`(x, -z, y)`), pracuje v ňom a všetko zapíše zase v rámci prehliadača. Je to
rotácia, nie zrkadlenie, takže nič nevychádza zrkadlovo. Kolo nahrané v surovom
rámci BeamNG by sa nezarovnalo. Nebolo testované s inými nahrávačmi.

Hra sa berie ako BeamNG, keď súbor `heat3d-lap` hovorí `"game": "beamng"`, alebo
keď zadáte `--game beamng`.

## Hľadanie inštalácie {#finding-the-install}

- `--install <folder>`: priečinok, ktorý obsahuje `gameengine.zip` a `content`.
- Inak sa skontroluje `steamapps\common\BeamNG.drive` v každej knižnici Steamu na tieto dve veci.
- Ak nič nepomôže: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Súborový systém {#the-file-system}

BeamNG distribuuje obyčajné zip archívy a pripája ich do jedného súborového
systému, na ktorý sa odvolávajú levely (`/art/shapes/...`, `/assets/materials/...`).
Export vytvorí to isté: jeden indexovaný bez ohľadu na veľkosť písmen cez

1. `gameengine.zip`,
2. každý `*.zip` pod `content`, okrem `content\vehicles\*` a archívov, ktorých názvy začínajú na `art_sound` alebo `audio`,
3. obsah používateľa, najprv najnovšie rozloženie: pod `%LOCALAPPDATA%\BeamNG\BeamNG.drive` a `%LOCALAPPDATA%\BeamNG.drive`, priečinok `current` a priečinok verzie s najvyšším číslom. Z každého: `mods\*.zip`, každý priečinok v `mods\unpacked` a samotný priečinok používateľa, ak má priečinok `levels`.

Neskoršie prírastky vyhrávajú, ako v hre, takže mod nahradí to, čo prepisuje.
Mody sa pri exporte trate vždy zahrnú.

Cesty, ktoré level pomenúva, sa rozlišujú tak, ako ich hra: ako sú uvedené, potom
relatívne k súboru, ktorý ich pomenoval, a pre každú aj ako `.dds`, do ktorého sa
textúra skompilovala, `.cdae`, do ktorého sa skompiloval `.dae`, alebo cez súbor
`.link` smerujúci do `/assets`.

## Ktorý level {#which-level}

Ak nie je zadané `--level`, každý level sa ohodnotí podľa toho, koľko kola na ňom
leží:

- Použije sa až 500 vzoriek kola, rovnomerne rozložených.
- Pre `TerrainBlock` každého levelu sa rozsah terénu prečíta z prvých piatich bajtov jeho súboru `.ter`, takže level, pri ktorom kolo vôbec nie je, nič nestojí. Ak je aspoň 30 % vzoriek v tomto rozsahu, prečítajú sa výšky. Vzorka sa počíta ako **na** terén, ak je medzi 1 m pod ním a 3 m nad ním (`ON_GROUND`), lebo referenčný bod auta je jeho karoséria, nie pneumatiky.
- Ak žiadny level nedosiahne 50 % alebo viac, levely sa ohodnotia aj podľa ich **ciest**. Niektoré levely pokračujú za svoju výškovú mapu (ich okraje pokračujú ako skalné plochy). Vzorka je na ceste, ak leží do polovice šírky cesty plus 4 m (aspoň 6 m) od segmentu `DecalRoad` a medzi 2 m pod a 4 m nad ním.
- Najlepší level vyhrá, ak dosiahne aspoň 30 %. Inak sa export zastaví a vypíše najlepšie tri: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

Konzola vypíše `on <level>: 87% of the lap lies on its terrain` (alebo `roads`).
`--level` sa porovnáva bez ohľadu na veľkosť písmen s názvami priečinkov levelov.

## Čítanie levelu {#reading-the-level}

Z čoho sa level skladá, každá časť overená voči dodaným levelom
(podrobnosti v [Súboroch BeamNG](reader-beamng.md)):

- **Scéna**: `levels\<name>\main\**\*.level.json` (jeden objekt JSON na riadok, alebo pole JSON), alebo súbor `.mis` pre staršie levely. Nástroj číta objekty `TSStatic` (umiestnené modely, preskakuje skryté), objekty `Prefab` (vnorené až 8 úrovní hlboko, skript TorqueScript `.prefab` alebo `.prefab.json`), objekty `DecalRoad` (namaľované cesty), `TerrainBlock`, `WaterPlane`, `WaterBlock` a `River`.
- **Lesné položky**: `levels\<name>\forest\*.forest4.json`, typované cez záznamy `managedItemData.json`. Bariéry, ploty a skaly sú lesné položky tak často ako stromy.
- **Terén**: výškové pole `.ter` a jeho mapa vrstiev.
- **Materiály**: každý `*.materials.json` mimo `levels\`, plus tie tohto levelu.

## Koridor a cestné nálepky {#the-corridor-and-the-road-decals}

Koridor je `--margin` metrov okolo kola v rovine x/y BeamNG (pozri [Export trate](course-export.md#the-corridor)). Koridor dosahu `margin + 60 m` vyberie kandidátov.

**Cestné nálepky** (`DecalRoad`) sú väčšina ciest BeamNG: namaľované na
terén, nie modelované. Nálepky, ktorých rozsah sa dotýka koridora dosahu, sa
zoberú v poradí kreslenia hry (klesajúci `renderPriority`, potom poradie v
súbore) a rozložia sa ako pásy:

- Uzly (x, y, z, šírka) sa interpolujú **centripetálnym Catmull-Rom** splajnom približne každý 1 m. Uniformný druh sa uzavrie sám na seba tam, kde sa uzly zhromažďujú v ostrej zákrute. Uzavreté cesty sa uzavrú.
- Každý okraj dostane výšku terénu tam, kde je terén do 1,5 m od vlastnej výšky cesty, a inde si ponechá výšku cesty (na moste).
- Názov materiálu určí, čo nálepka maľuje:

| Druh | Názov materiálu sa zhoduje (prvá zhoda vyhráva) |
|---|---|
| stopy pneumatík | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| prekrytie (kozmetické) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| vyznačenia | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| sypké | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| cesta | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| prekrytie | čokoľvek iné |

## Zem {#the-ground}

Výškové pole terénu vnútri koridora sa zmení na trojuholníky:

- Jeden štvoruholník na štvorec terénu, ktorého stred je v koridore. Štvorce s vrstvou 255 (diery) sa preskočia. Každý štvoruholník sú dva trojuholníky, s uhlopriečkou, ktorá sa strieda tak, ako to robí terén Torque.
- Výšky sú `position.z + h * maxHeight / 65535`. Normály sa odvodia z rozdielov výšok.
- Každý štvorec sa zaradí podľa svojej **vrstvy**: názov vrstvy s jej modelom zeme a poznámkou materiálu terénu. Slová o dlažbe z neho urobia `road`, `grass/forest/rock/moss/leaves/cliff/stone` z neho urobia `terrain` a sypké slová `loose` (štrk a hlina). Všetko ostatné je `terrain`.
- Potom **cestné a sypké nálepky** prepíšu štvorce, ktoré pokrývajú, v poradí kreslenia, takže posledná nálepka rozhodne.
- Vrcholy sa rozdelia na každý štvorec 512 m (`floor(x / 512)`, `floor(y / 512)`), takže každá časť sa mapuje presne do jedného obrázka: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konzola vypíše `what the ground is made of` s počtami trojuholníkov podľa druhu.

### Modelovaný povrch jazdy {#modelled-driving-surface}

Okruhy BeamNG sú rovnako často modely ako terén. Trať na okruhu môže byť jedna
sieť s čiarami, gumou a vibračnými pásmi ako samostatnými sieťami navrchu. Preto
sa umiestnené modely v kategóriách cesta, obruby, lem, rekvizity a mosty
prehľadávajú na povrch jazdy. Pre každý materiál:

| Povrch | Určený podľa (prvá zhoda) |
|---|---|
| stopy pneumatík | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` v názve, type zeme alebo poznámke |
| vyznačenia | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` v názve materiálu |
| obruby | `rumble`, `kerb`, `curb` |
| cesta | typ zeme `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, alebo názov obsahuje `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| sypké | typ zeme `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| lem | `sidewalk` |
| (vlastná kategória modelu) | pre modely už zaradené medzi cesty, obruby alebo lem |

Z týchto materiálov sa trojuholníky **smerujúce nahor** (normála z väčšia ako
0,5) vnútri koridora vyberú z modelu a stanú sa zemou. Namaľujú sa do pečenej
textúry dlaždice a zapíšu sa ako časti, napríklad
`ground:road 3_-2 asphalt_light`. Vyznačenia a stopy pneumatík sa len maľujú.
Zvyšné trojuholníky modelu zostanú pri modeli. Tieto modely nikdy nezjednodušuje
ani nevynecháva rozpočet, lebo hrubá trať je zlá trať.

## Pečená textúra zeme {#the-baked-ground-texture}

Každý štvorec 512 m, ktorý má zem, dostane jeden obrázok o `--texture-size`
pixeloch (2048 = 25 cm na pixel), nakreslený tak, ako hra kreslí svoju zem:

1. **Vrstvy terénu.** Pre každý pixel sa vrstvy štyroch okolitých štvorcov terénu bilineárne miešajú. Každá vrstva je zafarbená tak, ako ju hra zafarbuje: **základná mapa** materiálu roztiahnutá cez `diffuseSize` metrov (alebo celý terén), potom mapy **detailu** a **makra** ako šedé prekrytia (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutrálne). Ich predvolené hodnoty sa opakujú každé 2 m a 60 m, so silou 0,5 a 0,3, pokiaľ materiál nehovorí inak. Vrstva bez materiálu dostane plochú farbu svojho povrchu. Riadok 0 základnej mapy je sever.
2. **Cestné nálepky**, ktoré sa maľujú len na terén, v poradí kreslenia, každá so svojou textúrou, mapou nepriehľadnosti, odtieňom a nepriehľadnosťou, pozdĺž pásu. Dodávané úrovne používajú priority okolo 12–16 pre asfaltové podklady, 10 pre vyznačenia a 4 pre gumu.
3. **Modelovaný povrch jazdy** zhora: najprv podklady, potom prekrytia, každé vo vlastnej opakujúcej sa textúre modelu s jedným texelom na pixel pečenia.
4. **Nálepky, ktoré sa premietajú aj cez objekty** (`overObjects`), naposledy.

S `--no-textures` sa nič nepečie: časti zeme dostanú ploché farby a modelované
vyznačenia a stopy pneumatík sa stanú vlastnými časťami, zdvihnutými o **3 cm**.

## Umiestnené modely {#placed-models}

Kandidáti sú všetky `TSStatic`, deti prefabov a lesné položky, ktorých počiatok
leží v koridore dosahu. Model sa vykreslí, ak sa jeho svetový ohraničujúci kváder
tvaru dotýka koridora.

**Kategória** pochádza z vlastnej poznámky levelu a z cesty tvaru. Prvé pravidlo,
ktoré sa zhoduje, vyhrá:

| Kategória | Poznámka | Cesta alebo názov obsahuje |
|---|---|---|
| pozadie (nikdy sa nekreslí) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| obruby | | `kerb`, `curb`, `rumble` |
| cesta | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| lem | `SIDEWALK`, `COBBLESTONE` | |
| stromy (len s `--trees`) | `NATURE` | tree, foliage, bush, grass, plant a podobné slová |
| skaly | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| bariéry | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| značky | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| mosty | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infraštruktúra | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| budovy | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekvizity | | čokoľvek iné |

**Tvary** sa čítajú zo skompilovaného `.cdae`, alebo z Collada `.dae`, ak
vyrovnávacia pamäť neexistuje (mody). Tvar, ktorý sa nedá prečítať, sa počíta:
`N copies of M models could not be read`. Materiály pomenované alebo s textúrou
`invisible`, `collision` alebo `nodraw` sa nikdy nekreslia.

**Textúry.** Modely sa zoskupujú podľa kategórie a materiálu do častí pomenovaných
`structure:<category> <material>` (alebo `ground:kerbs <material>`). Skupina dostane
farebnú textúru svojho materiálu až do **256 px** len vtedy, ak jej UV zostávajú v
rozsahu 0–1 (98 % vrcholov v rozsahu -0,02 až 1,02). Prehliadač balí textúry do atlasu
a nevie jednu opakovať. Skupina, ktorej textúra sa opakuje, sa kreslí v priemernej
farbe textúry (alfou vážená, v sRGB, vynásobená farbou materiálu), alebo v
farbe kategórie, ak nemá textúru.

**Detail** sa riadi spoločnou schémou v [Úrovne detailu a rozpočet](detail-budget.md).
Úrovne detailu BeamNG sú `details` tvaru (najväčšia pixelová veľkosť ako prvá).
Keď je rozpočet prekročený, najvzdialenejšie kópie idú prvé. Obruby a modely
nesúce povrch jazdy sa nikdy nezjednodušujú ani nevynechávajú.

`--no-placed` zruší konštrukcie, ale modelovaný povrch jazdy ponechá. `--trees`
pridá kategóriu stromov.

## Voda {#water}

| Zdroj | Vykreslené ako |
|---|---|
| `WaterPlane` (more) | štvoruholník 4 m na výške vody pre každú bunku koridora, kam terén nedosahuje na túto výšku |
| `WaterBlock` | jeden štvoruholník, jednotkový štvorec pri lokálnom z = 0 v transformácii bloku (takže jeho mierka určuje veľkosť), ak sa dotýka koridora; či z = 0 je povrch bloku, nie je overené |
| `River` | pás pozdĺž jeho uzlov, ak sa dotýka koridora |

Všetka voda je jedna plochá časť, `water:water`.

## Nevykresľuje sa {#not-drawn}

- Pokryvová zem (procedurálna tráva).
- Scenéria umiestnená okolo okraja sveta (`backdrop` a podobné).
- Opakujúce sa textúry modelov, ktoré vyjdú ako priemerná farba (pozri vyššie).
- Kostrové siete (vozidlá, postavy) a sieťe nálepiek vnútri tvarov.

## Kontroly v pozadí {#checks-behind-it}

Ako je uvedené v zdrojovom kóde, namerané na dodávaných leveloch:

- Uzly ciest ležia na teréne s presnosťou 1–2 cm (medián) na skontrolovaných leveloch, s `h * maxHeight / 65535` a riadkami pozdĺž +y. `h / 32` alebo iné poradie osí minie o desiatky až stovky metrov.
- Železničné úseky zreťazené pozdĺž cesty bežia pozdĺž riadku 0 `rotationMatrix` (naprevažujúca väčšina).
- Rotáciu uzla `.cdae` treba transponovať. Potom sa ohraničenia sveta zhodujú so zdrojovým `.dae` na milimeter. Bez toho sú o 38 cm mimo (medián), čo je bežná chyba.
- Exportované na niekoľkých dodávaných leveloch každého druhu, za sekundy až minúty každý.
