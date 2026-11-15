---
title: Súbory BeamNG
nav_order: 8
lang: "sk"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Súbory BeamNG: archívy levelov, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive dodáva obyčajné zip archívy, takže tu nie je žiadny kontajner na
spätné inžinierstvo. Práca spočíva v čítaní levelu **tak, ako ho číta hra**: pripojiť
archívy do jedného súborového systému, sledovať scénové súbory a dekódovať terén
a skompilované tvary. K týmto čítačkám sa dostanete cez export trate
[BeamNG.drive](course-beamng.md). `identify` pomenuje aj zip levelu, `.cdae` a `.ter`,
a `list` a `extract` berú ktorýkoľvek zo zipov.

Zdroje: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Pripojený súborový systém {#the-mounted-file-system}

`Files.of_install(game)` vytvorí jeden index bez rozlíšenia veľkosti písmen nad
`gameengine.zip`, zipmi `content` (okrem vozidiel a zvukov) a modmi používateľa
(`mods\*.zip`, `mods\unpacked\*` a priečinok `levels` používateľa). Neskoršie doplnky
prepíšu skoršie, ako v hre. Hľadanie ignoruje veľkosť písmen, lebo odkazy samotných
levelov sa so zipmi nezhodujú (`.DAE` pre `.dae`). Podrobnosti sú na stránke
[BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` nájde cestu tak, ako ju nájde hra: ako je zadaná, relatívne k súboru,
ktorý ju pomenoval, `x.png` ako `x.dds`, `x.dae` ako `x.cdae` (uprednostnený) a cez
súbor JSON `x.png.link`, ktorého `path` ukazuje do `/assets`.

## Scénové súbory {#scene-files}

| Zdroj | Formát | Číta sa |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | jeden objekt JSON na riadok, alebo jedno pole či mapa JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | tie isté triedy, pre staršie levely bez `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript alebo JSON | deti umiestnené relatívne k prefabu, až 8 úrovní do hĺbky |
| `levels\<name>\forest\*.forest4.json` | jedna inštancia na riadok | typované záznamami `TSForestItemData` v `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | názov levelu (kľúče prekladu sa ignorujú) |

**Transformácie.** `rotationMatrix` je deväť čísel, ktorých **riadky** sú vlastné osi
objektu vo svete. Segmenty zvodidiel reťazené pozdĺž cesty bežia pozdĺž riadku 0
(92 %) a horný riadok sa nakláňa so sklonom cesty. Staršie prefaby dávajú
`rotation = "x y z degrees"`, pravotočivé otočenie o ten uhol (92 % reťazí zvodidiel
sedí s ním, 19 % s opačným smerom). Mierka násobí riadky a `position` (alebo `pos`) je
posledný riadok. Transformácia potomka prefabu sa skladá s transformáciou prefabu.
`groupPosition` prefabu je pivot editora a **neodpočítava sa**: vozík prefabu stojí na
zemi len bez neho.

Čísla TorqueScript sa čítajú tolerantným vzorom, lebo niektoré dodávané prefaby píšu
hodnoty ako `-0.99563-0.0` bez medzery.

## Terén: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Výška v metroch: `position.z + h * maxHeight / 65535`, s `position`,
  `squareSize` a `maxHeight` z `TerrainBlock` (predvolené 0, 1 a 2048).
- Riadky bežia pozdĺž +y. Bod mriežky (i, j) je na
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Vrstva 255 je diera.

Overené: uzly cesty ležia na terréne s odchýlkou 1-2 cm (medián) na troch leveloch.
`h / 32` alebo iné poradie osí sa minie o desiatky až stovky metrov.

## Materiály {#materials}

Každý `*.materials.json` mimo `levels\`, plus ten aktuálneho levelu, indexovaný podľa
`mapTo`, `name` a kľúča:

| Trieda | Použité polia |
|---|---|
| `Material`, `CustomMaterial` | farebná mapa (`baseColorMap`, `colorMap` alebo `diffuseMap`, prvá fáza), faktor farby, mapa priehľadnosti a faktor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | základná mapa a `diffuseSize`, detailná mapa, veľkosť a sila, makro mapa, veľkosť a sila, `groundmodelName`, `annotation` |

Obrázky sa dekódujú cez Pillow (DDS, PNG a ďalšie), kde sa dá, s použitím zmenšenej
veľkosti, a ukladajú sa do vyrovnávacej pamäte podľa veľkosti. Textúra, ktorú nevie
prečítať, sa vráti na plošnú farbu.

## Skompilované tvary: `.cdae` {#compiled-shapes-cdae}

`.cdae` je vlastná vyrovnávacia pamäť hry pre každý súbor Collada, zapísaná ako
MessagePack. Jej rozloženie **zdokumentovala BeamNG**
(documentation.beamng.com/modding/file_formats/cdae/) a čítačka ho nasleduje:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Čítajú sa: hranice, uzly, objekty, `details` (úrovne detailu), predvolené rotácie uzlov
(`Quat16`) a posuny, každý vrchol, UV, normála, farba, primitíva a indexy každej siete
a názvy materiálov. Názvy materiálov sa nachádzajú na konci streamu, lebo sekvencie
animovaného rekvizitu sú pred nimi v nedokumentovanej forme.

Dve veci, ktoré dokumentácia nevysvetľuje, boli overené voči súborom `.dae`, z ktorých
tvary vznikli:

- **Rotácie uzlov sú Torquove.** `Quat16` čítané učebnicovým spôsobom sa otáča opačne.
  Jeho matica sa musí **transponovať**. S tým každé svetové hranice uzla sedia s Collada
  na milimeter. Bez toho sú mediánovo o 38 cm mimo.
- **Jednotky a osi sú už aplikované.** Súbor Collada v centimetroch alebo s Y hore sa
  z vyrovnávacej pamäte dostane v metroch, s Z hore.

Úrovne detailu sú `details` s nezápornou veľkosťou, od najväčšej. Záporné veľkosti sú
siete kolízie a zorného poľa, nikdy sa nekreslia. Objekty pomenované `colmesh`,
`collision`, `los`, `bb_`, `billboard`, `autobillboard` alebo `imposter` sa nikdy
nekreslia. Kreslia sa len štandardné a zoradené siete. Skinované siete (postavy,
vozidlá) a dekálové siete nie. Pásy a vejáre trojuholníkov sa rozbalia a steny sa
otočia tak, aby súhlasili s uloženými normálami, čo Torquovo vlastné otáčanie nesľubuje.

Overené: takmer každý dodávaný tvar sa prečíta. Dva ostatné sú staršia verzia.

## Záložné čítanie Collada: `.dae` {#collada-fallback-dae}

Pre tvary bez `.cdae` (mody a občas tvar, ktorého vyrovnávacia pamäť je staršia) sa
súbor Collada číta tak, ako ho číta Torquov importér, do tej istej štruktúry:

- Úrovne detailu z Torquovej konvencie názvov: koncové číslo názvu siete uzla je
  pixelová veľkosť, z ktorej sa kreslí (`barrier75`, `barrier40`). Záporné číslo alebo
  názov `collision`/`Colmesh`/`LOS`/`nulldetail` sa nikdy nekreslí. Tvar bez tejto
  konvencie má jednu úroveň.
- Jednotky z `<unit meter>` a Y hore sa prevedie na Z hore.
- UV sa prevrátia na konvenciu vyrovnávacej pamäte (v beží nadol cez obrázok).

Overené voči vlastným `.cdae` hry pre tie isté súbory: takmer všetky vzorkované
hranice sa zhodujú do 1 cm, 583 s rovnakým počtom trojuholníkov, 94 % UV materiálov
je identických. Test na nainštalovanej hre vyžaduje, aby 90 % z až 60 párov tvarov
zo spoločného archívu umení sedelo do 1 cm.

## Nečíta sa {#not-read}

- Porast povrchu (procedurálna tráva) a všetko, čo sa generuje za behu.
- Animované sekvencie a skinning.
- Vozidlá a zvuky (nikdy sa nepripájajú).
