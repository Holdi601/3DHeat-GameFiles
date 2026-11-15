---
title: BeamNG datoteke
nav_order: 8
lang: "hr"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG datoteke: arhive razina, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive isporučuje obične zip arhive, pa ne postoji spremnik za obrnuto
inženjerstvo. Posao je u čitanju razine **na način na koji je igra čita**: montiranje
arhiva u jedan datotečni sustav, praćenje datoteka scene i dekodiranje terena i
sastavljenih oblika. Do ovih čitača se dolazi kroz izvoz staze za
[BeamNG.drive](course-beamng.md). `identify` također prepoznaje zip razine, `.cdae` i
`.ter`, a `list` i `extract` uzimaju bilo koji od zipova.

Izvori: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Montirani datotečni sustav {#the-mounted-file-system}

`Files.of_install(game)` gradi jedan indeks bez razlikovanja velikih i malih slova nad
`gameengine.zip`, `content` zipovima (osim vozila i zvukova) i korisnikovim modovima
(`mods\*.zip`, `mods\unpacked\*` i korisnička mapa `levels`). Kasniji dodaci nadjačavaju
ranije, kao u igri. Pretraga ne razlikuje velika i mala slova, jer se reference u
razinama ne slažu s arhivama (`.DAE` za `.dae`). Pojedinosti su na
[BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` pronalazi putanju kao što je to radi igra: kako je dana, relativno u odnosu na
datoteku koja ju je navela, `x.png` kao `x.dds`, `x.dae` kao `x.cdae` (preferirano), i
kroz `x.png.link` JSON datoteku čiji `path` pokazuje u `/assets`.

## Datoteke scene {#scene-files}

| Izvor | Format | Čita se |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | jedan JSON objekt po retku, ili jedan JSON niz ili mapa | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | iste klase, za starije razine bez `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript ili JSON | djeca postavljena relativno u odnosu na prefab, do 8 razina duboko |
| `levels\<name>\forest\*.forest4.json` | jedna instanca po retku | tipizirane zapisima `TSForestItemData` u `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | naslov razine (ključevi prijevoda se ignoriraju) |

**Transformacije.** `rotationMatrix` su devet brojeva čiji su **redovi** vlastite osi
objekta u svijetu. Dijelovi ograde nanizani uz cestu idu duž reda 0 (92%), a gornji red
se nagne s nagibom ceste. Stariji prefabi daju `rotation = "x y z degrees"`, desnostrani
okret za taj kut (92% lanaca tračnica se slaže s njim, 19% s suprotnim smjerom). Skala
množi redove, a `position` (ili `pos`) je zadnji red. Transformacija djeteta prefaba
sastavlja se s prefabom. `groupPosition` prefaba je pivot uređivača i **ne** oduzima se:
kolica-prefab stoje na tlu samo bez njega.

Brojevi u TorqueScriptu čitaju se tolerantnim uzorkom, jer neki isporučeni prefabi pišu
vrijednosti poput `-0.99563-0.0` bez razmaka.

## Teren: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Visina u metrima: `position.z + h * maxHeight / 65535`, s `position`, `squareSize` i
  `maxHeight` iz `TerrainBlock` (zadano 0, 1 i 2048).
- Redovi idu u smjeru +y. Točka mreže (i, j) je na
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Sloj 255 je rupa.

Provjereno: čvorovi ceste leže na terenu unutar 1-2 cm (medijan) na tri razine.
`h / 32`, ili drugi redoslijed osi, promaši za desetke do stotine metara.

## Materijali {#materials}

Svaki `*.materials.json` izvan `levels\`, plus onaj trenutne razine, indeksiran po
`mapTo`, `name` i ključu:

| Klasa | Korištena polja |
|---|---|
| `Material`, `CustomMaterial` | mapa boja (`baseColorMap`, `colorMap` ili `diffuseMap`, prva faza), faktor boje, mapa neprozirnosti i faktor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | osnovna mapa i `diffuseSize`, detaljna mapa, veličina i jačina, makro mapa, veličina i jačina, `groundmodelName`, `annotation` |

Slike se dekodiraju s Pillowom (DDS, PNG i ostali), koristeći smanjeni nacrt gdje je
moguće, i predmemoriraju se po veličini. Teksture koja se ne može pročitati vraća se na
jednoliku boju.

## Sastavljeni oblici: `.cdae` {#compiled-shapes-cdae}

`.cdae` je igrina vlastita predmemorija svakog Collada datoteke, zapisana kao MessagePack.
Njezin raspored **dokumentira BeamNG**
(documentation.beamng.com/modding/file_formats/cdae/), a čitač ga slijedi:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Što se čita: granice, čvorovi, objekti, `details` (razine detalja), zadane rotacije čvorova
(`Quat16`) i translacije, svi vrhovi, UV-ovi, normale, boje, primitivi i indeksi svake
mreže te nazivi materijala. Nazivi materijala nalaze se na kraju toka, jer sekvence
animiranog rekvizita dolaze prije njih u obliku koji nije dokumentiran.

Dvije stvari koje dokumentacija ne navodi, riješene prema `.dae` datotekama od kojih su
oblici napravljeni:

- **Rotacije čvorova su Torqueove.** `Quat16` pročitan na uobičajeni način rotira na krivu
  stranu. Njegovu matricu treba **transponirati**. S tim, svaka granica svijeta čvora
  odgovara Collada datoteci do milimetra. Bez toga, medijan je 38 cm izvan.
- **Jedinice i osi su već primijenjene.** Collada datoteka napisana u centimetrima ili s Y
  prema gore izlazi iz predmemorije u metrima, Z prema gore.

Razine detalja su `details` s nenegativnom veličinom, najveće prve. Negativne veličine
su mreže sudara i linije vida, nikad se ne crtaju. Objekti imenovani `colmesh`, `collision`,
`los`, `bb_`, `billboard`, `autobillboard` ili `imposter` nikad se ne crtaju. Crtaju se samo
standardne i sortirane mreže. Skinned mreže (likovi, vozila) i decal mreže se ne crtaju.
Trake i lepeze trokuta se razmotavaju, a lica se ponovno usmjeravaju da se slože s
pohranjenim normalama, što Torqueov vlastiti poredak ne obećava.

Provjereno: gotovo svaki isporučeni oblik se čita. Druga dva su starija verzija.

## Collada rezerva: `.dae` {#collada-fallback-dae}

Za oblike bez `.cdae` (modovi, i poneki oblik čija je predmemorija starija), Collada
datoteka čita se onako kako je Torqueov uvoznik čita, u istu strukturu:

- Razine detalja iz Torqueova imenovanja: broj na kraju imena mreže čvora je veličina u
  pikselima s koje se crta (`barrier75`, `barrier40`). Negativan broj, ili ime
  `collision`/`Colmesh`/`LOS`/`nulldetail`, nikad se ne crta. Oblik bez te konvencije je
  jedna razina.
- Jedinice iz `<unit meter>`, a Y prema gore pretvoren u Z prema gore.
- UV-ovi okrenuti prema konvenciji predmemorije (v ide niz sliku).

Provjereno naspram vlastitog `.cdae` igre za iste datoteke: gotovo sve uzorkovane granice u
1 cm, 583 s istim brojem trokuta, 94% UV-ova materijala identično. Test na instaliranoj igri
traži da 90% od do 60 parova oblika iz zajedničke arhive umjetnine bude u 1 cm.

## Nije čitano {#not-read}

- Pokrov tla (proceduralna trava), i sve što nastaje u vrijeme rada.
- Animirane sekvence i skinning.
- Vozila i zvukovi (nikad se ne montiraju).
