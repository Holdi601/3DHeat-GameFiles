---
title: BeamNG-fájlok
nav_order: 8
lang: "hu"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG-fájlok: pályaarchívumok, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

A BeamNG.drive sima zip-archívumokban szállít, így nincs olyan konténer, amelyet vissza kellene
fejteni. A munka abban van, hogy a pályát **úgy olvassuk, ahogy a játék**: az archívumokat egyetlen
fájlrendszerbe csatoljuk, követjük a jelenetfájlokat, és dekódoljuk a terepet és a fordított
alakzatokat. Ezeket az olvasókat a [BeamNG.drive](course-beamng.md) pályaexport hívja. Az `identify`
egy pályazipet, egy `.cdae`-t és egy `.ter`-t is felismer, a `list` és az `extract` pedig bármelyik zipet
elfogadja.

Forrás: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## A csatolt fájlrendszer {#the-mounted-file-system}

A `Files.of_install(game)` egyetlen, kis- és nagybetű-érzéketlen indexet épít a `gameengine.zip`, a
`content` zipek (a járművek és hangok kivételével) és a felhasználó modjai (`mods\*.zip`,
`mods\unpacked\*`, és a felhasználói `levels` mappa) fölé. A későbbi hozzáadások felülírják a
korábbiakat, ahogy a játékban. A keresés nem érzékeny a kis- és nagybetűre, mert a pályák saját
hivatkozásai nem egyeznek az archívumokkal (`.DAE` egy `.dae` helyett). A részletek a
[BeamNG.drive](course-beamng.md#the-file-system) oldalon vannak.

A `resolve()` úgy találja meg az útvonalat, ahogy a játék: ahogy megadják, a hivatkozó fájlhoz képest,
az `x.png`-t mint `x.dds`, az `x.dae`-t mint `x.cdae` (előnyben), és egy `x.png.link` JSON-fájlon át,
amelynek `path` mezője a `/assets`-be mutat.

## Jelenetfájlok {#scene-files}

| Forrás | Formátum | Ebből olvasva |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | soronként egy JSON-objektum, vagy egyetlen JSON-tömb vagy -leképezés | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | ugyanezek az osztályok, a régebbi pályákhoz, amelyeknek nincs `main\` mappájuk |
| `*.prefab` / `*.prefab.json` | TorqueScript vagy JSON | a prefabhoz képest elhelyezett gyermekek, legfeljebb 8 szinttel mélyen |
| `levels\<name>\forest\*.forest4.json` | soronként egy példány | a `managedItemData.json` `TSForestItemData` rekordjai szerint típusozva (`shapeFile`) |
| `info.json` | JSON | a pálya címe (a fordítási kulcsokat figyelmen kívül hagyjuk) |

**Transzformációk.** A `rotationMatrix` kilenc szám, amelynek **sorai** a tárgy saját tengelyei a
világban. Az úton összefűzött korlátszakaszok a 0. sor mentén futnak (92%), a felfelé sor pedig az út
lejtésével dől. A régebbi prefabok `rotation = "x y z degrees"` értéket adnak, egy jobbkezes fordulat
az adott szöggel (a korlátláncok 92%-a ennek megfelelően illeszkedik, 19%-a az ellenkező irányban).
A skála szorozza a sorokat, a `position` (vagy `pos`) pedig az utolsó sor. Egy prefab gyermekének
transzformációja a prefabbal együtt áll össze. A prefab `groupPosition`-jét egy szerkesztői
forgáspont, és **nem** vonjuk le: egy kocsi-prefab csak nélküle áll a talajon.

A TorqueScript-számokat toleráns mintával olvassuk, mert néhány szállított prefab olyan értékeket ír,
mint a `-0.99563-0.0`, szóköz nélkül.

## Terep: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- A magasság méterben: `position.z + h * maxHeight / 65535`, ahol a `position`, `squareSize` és
  `maxHeight` a `TerrainBlock`-ból jön (alapértelmezés 0, 1 és 2048).
- A sorok a +y irányába futnak. A (i, j) rácspont a
  `(position.x + i * squareSize, position.y + j * squareSize)` pontban van.
- A 255-ös réteg lyuk.

Ellenőrizve: az úti csomópontok három pályán 1–2 cm-en belül (medián) a terepen fekszenek. A `h / 32`,
vagy a másik tengelysorrend tíz-száz méterrel téved.

## Anyagok {#materials}

Minden `levels\`-en kívüli `*.materials.json`, plusz az aktuális pálya fájlja, indexelve a `mapTo`, a
`name` és a kulcs szerint:

| Osztály | Felhasznált mezők |
|---|---|
| `Material`, `CustomMaterial` | színtérkép (`baseColorMap`, `colorMap` vagy `diffuseMap`, az első szakasz), színtényező, átlátszatlansági térkép és tényező, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | alaptérkép és `diffuseSize`, részlettérkép, méret és erősség, makrotérkép, méret és erősség, `groundmodelName`, `annotation` |

A képeket Pillow-val dekódoljuk (DDS, PNG és így tovább), ahol lehet, csökkentett méretű draft-tal,
méretenként gyorsítótárazva. Egy olvashatatlan textúra egyszínűre esik vissza.

## Fordított alakzatok: `.cdae` {#compiled-shapes-cdae}

A `.cdae` a játék saját gyorsítótára minden Collada-fájlról, MessagePack formátumban. Az elrendezését a
**BeamNG dokumentálja** (documentation.beamng.com/modding/file_formats/cdae/), és az olvasó ezt követi:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Ezeket olvassuk: határolók, csomópontok, objektumok, részletességi szintek (`details`), az alapértelmezett
csomóponti forgatások (`Quat16`) és eltolások, minden háló csúcsai, UV-i, normáljai, színei, primitívjei
és indexei, valamint az anyagnevek. Az anyagneveket a folyam végén találjuk meg, mert egy animált kellék
sorozatai egy nem dokumentált formában előbb jönnek.

Két dolog, amelyet a dokumentáció nem fejt ki, a `.dae` fájlokhoz igazítva, amelyekből az alakzatok
készültek:

- **A csomóponti forgatások Torque-félék.** Egy `Quat16`, ahogy a tankönyv szerint olvassuk, rosszul
  forog. A mátrixát **transzponálni** kell. Így minden csomópont világbeli határolója a Collada-val
  milliméterre egyezik. Enélkül a medián 38 cm-t téved.
- **Az egységek és a tengelyek már alkalmazva vannak.** A centiméterben vagy Y-felfelé készült Collada
  fájl a gyorsítótárból métert, Z-felfelé értékben jön ki.

A részletességi szintek a nem negatív méretű `details` elemek, a legnagyobbal kezdve. A negatív méretűek
ütközési és látóvonal-hálók, sosem rajzoljuk őket. A `colmesh`, `collision`, `los`, `bb_`, `billboard`,
`autobillboard` vagy `imposter` nevű objektumok sosem rajzolódnak. Csak a standard és rendezett hálók
rajzolódnak. A csontozott hálók (karakterek, járművek) és a matrica-hálók nem. A háromszögcsíkokat és
-legyezőket kibontjuk, és a faceket úgy fordítjuk meg, hogy egyezzenek a tárolt normálokkal, amit a Torque
saját körüljárása nem garantál.

Ellenőrizve: szinte minden szállított alakzat beolvasódik. A másik kettő régebbi verzió.

## Collada-tartalék: `.dae` {#collada-fallback-dae}

Azoknál az alakzatoknál, amelyekhez nincs `.cdae` (modok, és néhány alakzat, amelynek gyorsítótára régebbi),
a Collada-fájlt úgy olvassuk, ahogy a Torque importőre olvassa, ugyanabba a szerkezetbe:

- A részletességi szintek a Torque elnevezéséből: egy hálócsomópont végi száma az a pixelméret, amelyből
  rajzolódik (`barrier75`, `barrier40`). Egy negatív szám, vagy egy `collision`/`Colmesh`/`LOS`/`nulldetail`
  név sosem rajzolódik. Az egyezmény nélküli alakzat egy szint.
- Az egységek a `<unit meter>`-ből, a Y-felfelé pedig Z-felfelé fordítva.
- Az UV-k a gyorsítótár konvenciójára fordítva (a v lefelé fut a képen).

Ellenőrizve a játék saját `.cdae`-jával ugyanazokra a fájlokra: szinte minden mintavett határoló 1 cm-en
belül, 583 azonos háromszögszámmal, az anyagok UV-inek 94%-a azonos. A telepített játékon futó teszt
megköveteli, hogy a közös művészeti archívum legfeljebb 60 alakzatpárjának 90%-a 1 cm-en belül egyezzen.

## Nincs beolvasva {#not-read}

- Talajborítás (procedurális fű), és bármi, ami futásidőben generálódik.
- Animált sorozatok és csontozás.
- Járművek és hangok (soha nincsenek csatolva).
