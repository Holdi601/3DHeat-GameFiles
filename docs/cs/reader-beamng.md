---
title: Soubory BeamNG
nav_order: 8
lang: "cs"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Soubory BeamNG: archivy úrovní, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive dodává obyčejné zip archivy, takže není žádný kontejner, který by se
musel reverzně inženýrovat. Práce spočívá v čtení úrovně **tak, jak to dělá hra**:
připojení archivů do jednoho souborového systému, sledování scénových souborů a
dekódování terénu a zkompilovaných tvarů. Tyto čtečky se volají přes export tratě
[BeamNG.drive](course-beamng.md). `identify` pojmenuje také zip úrovně, `.cdae` a
`.ter`, a `list` a `extract` berou kterýkoli ze zipů.

Zdroje: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Připojený souborový systém {#the-mounted-file-system}

`Files.of_install(game)` vytvoří jeden index bez ohledu na velikost písmen nad
`gameengine.zip`, zip soubory `content` (kromě vozidel a zvuků) a uživatelskými
mody (`mods\*.zip`, `mods\unpacked\*` a uživatelská složka `levels`). Pozdější
přídavky přepisují dřívější, jako ve hře. Vyhledávání nerozlišuje velikost písmen,
protože odkazy úrovní se neshodují s archivy (`.DAE` pro `.dae`). Podrobnosti jsou
na [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` najde cestu tak, jako to dělá hra: tak, jak je zadána, relativně k
souboru, který ji jmenoval, `x.png` jako `x.dds`, `x.dae` jako `x.cdae` (přednostně),
a přes soubor `x.png.link` v JSONu, jehož `path` ukazuje do `/assets`.

## Scénové soubory {#scene-files}

| Zdroj | Formát | Čte se |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | jeden objekt JSON na řádek, nebo jediné pole či mapa JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | stejné třídy, pro starší úrovně bez `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript nebo JSON | potomci umístění vzhledem k prefabu, až 8 úrovní hluboko |
| `levels\<name>\forest\*.forest4.json` | jedna instance na řádek | typované záznamy `TSForestItemData` v `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | název úrovně (klíče překladu se ignorují) |

**Transformace.** `rotationMatrix` je devět čísel, jejichž **řádky** jsou vlastními
osami objektu ve světě. Svodidlové sekce řazené podél silnice běží po řádku 0 (92 %)
a řádek nahoru se nakloní se sklonem silnice. Starší prefaby dávají
`rotation = "x y z degrees"`, pravotočivé otočení o daný úhel (92 % řetězů
svodidel souhlasí, 19 % s opačným smyslem). Měřítko násobí řádky a `position` (nebo
`pos`) je poslední řádek. Transformace potomka prefabu se skládá s transformací
prefabu. `groupPosition` prefabu je pivot z editoru a **neodečítá se**: prefab
vozíku stojí na zemi jen bez něj.

Čísla v TorqueScriptu se čtou tolerantním vzorem, protože některé dodané prefaby
píší hodnoty jako `-0.99563-0.0` bez mezery.

## Terén: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Výška v metrech: `position.z + h * maxHeight / 65535`, s `position`,
  `squareSize` a `maxHeight` z `TerrainBlock` (výchozí 0, 1 a 2048).
- Řádky běží podél +y. Bod mřížky (i, j) je na
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Vrstva 255 je díra.

Ověřeno: uzly silnice leží na terénu s odchylkou 1-2 cm (medián) na třech úrovních.
`h / 32`, nebo jiné pořadí os, minou o desítky až stovky metrů.

## Materiály {#materials}

Každý `*.materials.json` mimo `levels\`, plus ten aktuální úrovně, indexovaný podle
`mapTo`, `name` a klíče:

| Třída | Použitá pole |
|---|---|
| `Material`, `CustomMaterial` | barevná mapa (`baseColorMap`, `colorMap` nebo `diffuseMap`, první stupeň), faktor barvy, mapa a faktor průhlednosti, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | základní mapa a `diffuseSize`, detailní mapa, velikost a síla, makro mapa, velikost a síla, `groundmodelName`, `annotation` |

Obrázky se dekódují Pillow (DDS, PNG a tak dále), kde to jde se zmenšeným náhledem,
a ukládají se do mezipaměti podle velikosti. Textura, kterou nejde přečíst, spadne
na plochou barvu.

## Zkompilované tvary: `.cdae` {#compiled-shapes-cdae}

`.cdae` je vlastní mezipaměť hry pro každý soubor Collada, zapsaná jako MessagePack.
Jeho rozložení **dokumentuje BeamNG** (documentation.beamng.com/modding/file_formats/cdae/)
a čtečka se jím řídí:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Čte se: hranice, uzly, objekty, `details` (úrovně detailu), výchozí rotace uzlů
(`Quat16`) a posuny, každé vrcholy, UV, normály, barvy, primitiva a indexy každé
sítě a názvy materiálů. Názvy materiálů se najdou na konci proudu, protože
sekvence animovaného rekvizity přicházejí před nimi v podobě, která není
zdokumentovaná.

Dvě věci, které dokumentace nerozvádí, se ověřily proti souborům `.dae`, z nichž
tvary vznikly:

- **Rotace uzlů jsou Torquovy.** `Quat16` přečtený učebnicovým způsobem se otočí
  špatně. Jeho matice se musí **transponovat**. S tím každé světové hranice uzlu
  sedí na Collada s přesností na milimetr. Bez toho jsou mediánem o 38 cm mimo.
- **Jednotky a osy jsou už aplikované.** Soubor Collada psaný v centimetrech nebo s Y
  nahoru přijde z mezipaměti v metrech, Z nahoru.

Úrovně detailu jsou `details` s nezápornou velikostí, od největší. Záporné velikosti
jsou kolizní a mezi-viditelnostní sítě, které se nikdy nekreslí. Objekty
pojmenované `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` nebo
`imposter` se nikdy nekreslí. Kreslí se jen standardní a seřazené sítě. Kožované
sítě (postavy, vozidla) a dekorační sítě ne. Pásy a vějíře trojúhelníků se rozbalí
a plochy se přetočí tak, aby souhlasily s uloženými normálami, což Torquovo vlastní
točení nezaručuje.

Ověřeno: téměř každý dodaný tvar se čte. Ostatní dva jsou starší verze.

## Záložní čtení Collada: `.dae` {#collada-fallback-dae}

U tvarů bez `.cdae` (mody a občasný tvar se starší mezipamětí) se soubor Collada
čte tak, jak ho čte importér Torque, do stejné struktury:

- Úrovně detailu podle Torquova pojmenování: koncové číslo v názvu sítě uzlu je
  pixelová velikost, ze které se kreslí (`barrier75`, `barrier40`). Záporné číslo
  nebo název `collision`/`Colmesh`/`LOS`/`nulldetail` se nikdy nekreslí. Tvar bez
  této konvence má jednu úroveň.
- Jednotky z `<unit meter>`, a osa Y nahoru převedená na Z nahoru.
- UV převrácená do konvence mezipaměti (v běží dolů po obrázku).

Ověřeno proti hrou vlastním `.cdae` týchž souborů: téměř všechny vzorkované hranice
v rozmezí 1 cm, 583 se stejným počtem trojúhelníků, 94 % UV materiálů totožných.
Test na nainstalované hře vyžaduje, aby se 90 % z až 60 dvojic tvarů ze sdíleného
archivu uměleckých děl shodovalo do 1 cm.

## Nečte se {#not-read}

- Porost země (procedurální tráva) a cokoli, co vznikne za běhu.
- Animované sekvence a kožování.
- Vozidla a zvuky (nikdy se nepřipojí).
