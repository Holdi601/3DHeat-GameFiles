---
title: "BeamNG datoteke"
nav_order: 8
lang: "bs"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG datoteke: arhive nivoa, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive isporučuje obične zip arhive, pa nema kontejnera koji bi trebalo
reverzno inženjerirati. Posao je u čitanju nivoa **onako kako to radi igra**:
montiranje arhiva u jedan datotečni sistem, praćenje datoteka scene i
dekodiranje terena i kompiliranih oblika. Do ovih čitača dolazi se kroz izvoz
staze [BeamNG.drive](course-beamng.md). `identify` imenuje i zip nivoa, `.cdae` i
`.ter`, a `list` i `extract` uzimaju bilo koji od zipova.

Izvori: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Montirani datotečni sistem {#the-mounted-file-system}

`Files.of_install(game)` gradi jedan indeks neosjetljiv na velika i mala slova
preko `gameengine.zip`, `content` zipova (osim vozila i zvukova) i korisnikovih
modova (`mods\*.zip`, `mods\unpacked\*` i korisnički folder `levels`). Kasnija
dodavanja nadjačavaju ranija, kao u igri. Pretraživanje ignorira velika i mala
slova jer se vlastite reference nivoa ne slažu s arhivama u tome (`.DAE` za
`.dae`). Detalji su na stranici [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` pronalazi putanju onako kako to radi igra: kako je data, relativno
prema datoteci koja ju je imenovala, `x.png` kao `x.dds`, `x.dae` kao `x.cdae`
(preferirano), i kroz JSON datoteku `x.png.link` čiji `path` pokazuje u `/assets`.

## Datoteke scene {#scene-files}

| Izvor | Format | Čita se |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | jedan JSON objekt po redu, ili jedan JSON niz ili mapa | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | iste klase, za starije nivoe bez `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript ili JSON | djeca postavljena relativno prema prefabu, do 8 nivoa dubine |
| `levels\<name>\forest\*.forest4.json` | jedna instanca po redu | tipizirano zapisima `TSForestItemData` u `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | naslov nivoa (ključevi prevoda se ignoriraju) |

**Transformacije.** `rotationMatrix` je devet brojeva čiji su **redovi** vlastite
ose objekta u svijetu. Sekcije zaštitne ograde povezane duž ceste idu duž reda 0
(92%), a red "gore" naginje se s nagibom ceste. Stariji prefabi daju
`rotation = "x y z degrees"`, desnu rotaciju za taj ugao (92% lanaca ograda
poravnava se s njom, 19% sa suprotnim smislom). Skala množi redove, a
`position` (ili `pos`) je posljednji red. Transformacija djeteta prefaba
slaže se s transformacijom prefaba. `groupPosition` prefaba je pivot editora i
**ne** oduzima se: prefab trolejbusa stoji na tlu samo bez toga.

TorqueScript brojevi čitaju se tolerantnim obrascem, jer neki isporučeni
prefabi pišu vrijednosti poput `-0.99563-0.0` bez razmaka.

## Teren: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Visina u metrima: `position.z + h * maxHeight / 65535`, s `position`,
  `squareSize` i `maxHeight` iz `TerrainBlock` (zadano 0, 1 i 2048).
- Redovi idu duž +y. Tačka mreže (i, j) je na
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Sloj 255 je rupa.

Provjereno: čvorovi ceste leže na terenu na 1-2 cm (medijan) na tri nivoa.
`h / 32`, ili drugi redoslijed osa, promašuje za desetine do stotine metara.

## Materijali {#materials}

Svaki `*.materials.json` izvan `levels\`, plus onaj trenutnog nivoa, indeksiran
po `mapTo`, `name` i ključu:

| Klasa | Korištena polja |
|---|---|
| `Material`, `CustomMaterial` | mapa boje (`baseColorMap`, `colorMap` ili `diffuseMap`, prva faza), faktor boje, mapa i faktor neprozirnosti, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | osnovna mapa i `diffuseSize`, detaljna mapa, veličina i jačina, makro mapa, veličina i jačina, `groundmodelName`, `annotation` |

Slike se dekodiraju Pillowom (DDS, PNG i tako dalje), koristeći nacrt smanjene
veličine gdje je moguće, i keširaju se po veličini. Nečitljiva tekstura vraća se
na ravnu boju.

## Kompilirani oblici: `.cdae` {#compiled-shapes-cdae}

`.cdae` je vlastiti keš igre za svaku Collada datoteku, pisan kao MessagePack.
Njegov raspored je **dokumentirao BeamNG**
(documentation.beamng.com/modding/file_formats/cdae/) i čitač ga slijedi:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Šta se čita: granice, čvorovi, objekti, details (nivoi detalja), zadane rotacije
čvorova (`Quat16`) i translacije, vrhovi, UV-ovi, normale, boje, primitivi i
indeksi svake mreže, te imena materijala. Imena materijala pronalaze se na kraju
toka, jer sekvence animiranog rekvizita dolaze prije njih u obliku koji nije
dokumentiran.

Dvije stvari koje dokumentacija ne navodi, riješene naspram `.dae` datoteka iz
kojih su oblici građeni:

- **Rotacije čvorova su Torqueove.** `Quat16` pročitan udžbenički rotira u
  pogrešnom smjeru. Njegova matrica se mora **transponirati**. Tako svaka svjetska
  granica čvora podudara se s Colladom do milimetra. Bez toga, u medijanu su 38 cm
  pogrešne.
- **Jedinice i ose su već primijenjene.** Collada datoteka autorirana u
  centimetrima ili s Y gore izlazi iz keša u metrima, sa Z gore.

Nivoi detalja su `details` s nenegativnom veličinom, najveći prvi. Negativne
veličine su mreže kolizije i linije vidljivosti, nikad se ne crtaju. Objekti
nazvani `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` ili
`imposter` nikad se ne crtaju. Crtaju se samo standardne i sortirane mreže.
Skinirane mreže (likovi, vozila) i mreže decala ne crtaju se. Trakasti i lepezasti
trouglovi se razmotavaju, a lica se ponovo namotavaju da se slažu s pohranjenim
normalama, što Torqueovo vlastito namotavanje ne obećava.

Provjereno: gotovo svaki isporučeni oblik se čita. Preostala dva su starije
verzije.

## Collada rezerva: `.dae` {#collada-fallback-dae}

Za oblike bez `.cdae` (modovi i poneki oblik čiji je keš stariji), Collada
datoteka se čita onako kako je čita Torqueov importer, u istu strukturu:

- Nivoi detalja iz Torqueovog imenovanja: završni broj čvora mreže je veličina
  u pikselima od koje se crta (`barrier75`, `barrier40`). Negativan broj, ili ime
  `collision`/`Colmesh`/`LOS`/`nulldetail`, nikad se ne crta. Oblik bez te
  konvencije je jedan nivo.
- Jedinice iz `<unit meter>`, a Y-gore pretvoreno u Z-gore.
- UV-ovi okrenuti u konvenciju keša (v ide niz sliku).

Provjereno naspram vlastitog `.cdae` igre za iste datoteke: gotovo sve uzorkovane granice unutar
1 cm, 583 s istim brojem trouglova, 94% UV-ova materijala identično. Test na
instaliranoj igri zahtijeva da se 90% od do 60 parova oblika iz zajedničke arhive
umjetnosti slaže unutar 1 cm.

## Ne čita se {#not-read}

- Raslinje po tlu (proceduralna trava) i sve što se generira u toku izvođenja.
- Animirane sekvence i skinning.
- Vozila i zvukovi (nikad se ne montiraju).
