---
title: "Fișiere BeamNG: arhive de nivel, `.ter`, `.cdae`, `.dae`"
nav_order: 8
lang: "ro"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Fișiere BeamNG: arhive de nivel, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive livrează arhive zip obișnuite, deci nu există un container de analizat prin inginerie inversă. Munca constă în citirea unui nivel **așa cum o face jocul**: montarea arhivelor într-un singur sistem de fișiere, urmarea fișierelor de scenă și decodarea terenului și a formelor compilate. Aceste cititoare se ating prin exportul de circuit [BeamNG.drive](course-beamng.md). `identify` recunoaște și un zip de nivel, un `.cdae` și un `.ter`, iar `list` și `extract` iau oricare dintre zip-uri.

Surse: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Sistemul de fișiere montat {#the-mounted-file-system}

`Files.of_install(game)` construiește un singur index, fără a ține cont de majuscule, peste `gameengine.zip`, zip-urile `content` (fără vehicule și sunete) și modurile utilizatorului (`mods\*.zip`, `mods\unpacked\*` și un folder `levels` al utilizatorului). Adăugirile ulterioare le înlocuiesc pe cele anterioare, ca în joc. Căutările ignoră majusculele, pentru că referințele nivelurilor nu se potrivesc cu arhivele în privința lor (`.DAE` pentru un `.dae`). Detalii la [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` găsește o cale cum o face jocul: așa cum este dată, relativ la fișierul care a numit-o, `x.png` ca `x.dds`, `x.dae` ca `x.cdae` (preferat), și printr-un fișier JSON `x.png.link` a cărui `path` indică spre `/assets`.

## Fișiere de scenă {#scene-files}

| Sursă | Format | Citit |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | un obiect JSON pe linie, sau un singur tablou sau dicționar JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | aceleași clase, pentru nivelurile mai vechi fără `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript sau JSON | copiii plasați relativ la prefab, până la 8 niveluri adânc |
| `levels\<name>\forest\*.forest4.json` | o instanță pe linie | tipizate prin înregistrările `TSForestItemData` din `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | titlul nivelului (cheile de traducere sunt ignorate) |

**Transformări.** `rotationMatrix` are nouă numere ale căror **rânduri** sunt axele proprii ale obiectului în lume. Secțiunile de parapet înlănțuite de-a lungul unui drum merg pe rândul 0 (92%), iar rândul de sus se înclină odată cu panta drumului. Prefabricatele mai vechi dau `rotation = "x y z degrees"`, o rotire dreptă cu acel unghi (92% dintre lanțurile de parapet se aliniază cu ea, 19% cu sensul opus). Scala înmulțește rândurile, iar `position` (sau `pos`) este ultimul rând. Transformarea unui copil de prefab se compune cu a prefabului. `groupPosition` al prefabului este un pivot de editor și **nu** se scade: un prefab de cărucior stă pe sol doar fără el.

Numerele TorqueScript se citesc cu un șablon tolerant, pentru că unele prefabricate livrate scriu valori precum `-0.99563-0.0` fără spațiu.

## Teren: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Înălțimea în metri: `position.z + h * maxHeight / 65535`, cu `position`, `squareSize` și `maxHeight` din `TerrainBlock` (implicit 0, 1 și 2048).
- Rândurile merg pe +y. Punctul de grilă (i, j) se află la `(position.x + i * squareSize, position.y + j * squareSize)`.
- Stratul 255 este o gaură.

Verificat: nodurile de drum stau pe teren cu 1-2 cm (mediană) pe trei niveluri. `h / 32`, sau cealaltă ordine a axelor, greșește cu zeci până la sute de metri.

## Materiale {#materials}

Fiecare `*.materials.json` din afara `levels\`, plus cel al nivelului curent, indexat după `mapTo`, `name` și cheie:

| Clasă | Câmpuri folosite |
|---|---|
| `Material`, `CustomMaterial` | harta de culoare (`baseColorMap`, `colorMap` sau `diffuseMap`, primul stadiu), factorul de culoare, harta de opacitate și factorul ei, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | harta de bază și `diffuseSize`, harta de detaliu, dimensiunea și intensitatea ei, harta macro, dimensiunea și intensitatea ei, `groundmodelName`, `annotation` |

Imaginile sunt decodate cu Pillow (DDS, PNG și altele), folosind un draft redus acolo unde este posibil, și sunt memorate în cache după dimensiune. O textură care nu poate fi citită revine la culoare uniformă.

## Forme compilate: `.cdae` {#compiled-shapes-cdae}

`.cdae` este memoria cache a jocului pentru fiecare fișier Collada, scrisă ca MessagePack. Structura lui este **documentată de BeamNG** (documentation.beamng.com/modding/file_formats/cdae/), iar cititorul o urmează:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Ce se citește: limitele, nodurile, obiectele, `details` (nivelurile de detaliu), rotațiile implicite ale nodurilor (`Quat16`) și translațiile, fiecare vertex, UV, normală, culoare, primitivă și index al fiecărui mesh, și numele materialelor. Numele materialelor se găsesc la sfârșitul fluxului, pentru că secvențele unui obiect animat vin înaintea lor, într-o formă care nu este documentată.

Două lucruri pe care documentația nu le spune explicit, stabilite față de fișierele `.dae` din care au fost construite formele:

- **Rotațiile nodurilor sunt ale lui Torque.** Un `Quat16` citit în felul din manual se rotește pe dos. Matricea lui trebuie **transpusă**. Cu asta, limitele în lume ale fiecărui nod se potrivesc cu Collada până la milimetru. Fără ea, sunt în afara cu 38 cm în mediană.
- **Unitățile și axele sunt deja aplicate.** Un fișier Collada făcut în centimetri sau cu Y în sus iese din memoria cache în metri, cu Z în sus.

Nivelurile de detaliu sunt `details` cu dimensiune nenegativă, cel mai mare întâi. Dimensiunile negative sunt mesh-uri de coliziune și de linie de vedere, care nu se desenează niciodată. Obiectele numite `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` sau `imposter` nu se desenează niciodată. Se desenează doar mesh-urile standard și cele sortate. Mesh-urile cu schelet (personaje, vehicule) și mesh-urile de decalcomanii nu. Benzile și evantaiele de triunghiuri sunt desfăcute, iar fețele sunt re-înfășurate ca să se potrivească cu normalele stocate, ceea ce înfășurarea lui Torque nu garantează.

Verificat: aproape fiecare formă livrată se citește. Celelalte două sunt dintr-o versiune mai veche.

## Rezerva Collada: `.dae` {#collada-fallback-dae}

Pentru forme fără `.cdae` (mods, și formele rare a căror memorie cache este mai veche), fișierul Collada este citit cum îl citește importatorul Torque, în aceeași structură:

- Nivelurile de detaliu din convenția de nume a lui Torque: numărul de la sfârșitul numelui unui nod de mesh este dimensiunea în pixeli din care este desenat (`barrier75`, `barrier40`). Un număr negativ, sau un nume `collision`/`Colmesh`/`LOS`/`nulldetail`, nu se desenează niciodată. O formă fără convenție are un singur nivel.
- Unități din `<unit meter>`, iar Y în sus devine Z în sus.
- UV-urile întoarse după convenția memoriei cache (v merge în jos pe imagine).

Verificat față de `.cdae` al jocului pentru aceleași fișiere: aproape toate limitele eșantionate la 1 cm, 583 cu același număr de triunghiuri, 94% din UV-urile materialelor identice. Testul pe jocul instalat cere ca 90% din până la 60 de perechi de forme din arhiva comună de artă să se potrivească la 1 cm.

## Ce nu se citește {#not-read}

- Vegetația de sol (iarba procedurală) și tot ce este generat în timpul rulării.
- Secvențele animate și scheletul.
- Vehiculele și sunetele (nu sunt niciodată montate).
