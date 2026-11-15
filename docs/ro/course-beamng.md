---
title: BeamNG.drive
nav_order: 2
lang: "ro"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Exportul traseului: BeamNG.drive {#course-export-beamngdrive}

Exportul BeamNG citește un nivel în felul în care îl montează jocul, apoi scrie același fel de fișier ca exportul Forza: terenul pe pătrate de 512 m, cu o textură coaptă, drumul și solul liber ca părți proprii, modelele plasate pe categorii și apa.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Surse: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalare, sistem de fișiere, scenă, teren, materiale),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (exportul),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) și
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (forme).
Formatele de fișiere în detaliu: [Fișierele BeamNG](reader-beamng.md).

## Cadrul turului {#the-laps-frame}

Exportul `course` se așteaptă ca pozițiile BeamNG să fie în **cadrul vizualizatorului**:
`(x, z, -y)` din lumea cu Z în sus a BeamNG, în metri. Aceasta este rotația pe care o aplică înregistratorul de telemetrie 3DHeat. Exportul întoarce turul înapoi în cadrul BeamNG (`(x, -z, y)`), lucrează acolo și scrie totul din nou în cadrul vizualizatorului. Este o rotație, nu o oglindire, deci nimic nu iese oglindit. Un tur înregistrat în cadrul brut al BeamNG nu s-ar plasa. Nu s-a testat cu alți înregistratori.

Jocul este luat ca BeamNG când fișierul `heat3d-lap` spune `"game": "beamng"`, sau când dați `--game beamng`.

## Găsirea instalării {#finding-the-install}

- `--install <folder>`: folderul care conține `gameengine.zip` și `content`.
- Altfel, se verifică `steamapps\common\BeamNG.drive` din fiecare bibliotecă Steam pentru cele două.
- Dacă nimic nu merge: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)."

## Sistemul de fișiere {#the-file-system}

BeamNG livrează arhive zip simple și le montează într-un singur sistem de fișiere la care se referă nivelurile (`/art/shapes/...`, `/assets/materials/...`). Exportul construiește același lucru: un singur index care nu ține cont de majuscule și minuscule peste

1. `gameengine.zip`,
2. fiecare `*.zip` din `content`, cu excepția `content\vehicles\*` și a arhivelor al căror nume începe cu `art_sound` sau `audio`,
3. conținutul utilizatorului, cu cel mai nou aspect primul: sub `%LOCALAPPDATA%\BeamNG\BeamNG.drive` și `%LOCALAPPDATA%\BeamNG.drive`, folderul `current` și folderul de versiune cu cel mai mare număr. Din fiecare: `mods\*.zip`, fiecare folder din `mods\unpacked`, și chiar folderul utilizatorului dacă are un folder `levels`.

Adăugirile de mai târziu câștigă, ca în joc, astfel încât un mod înlocuiește ce suprascrie. Modurile sunt mereu incluse într-un export de traseu.

Căile pe care le numește un nivel se rezolvă ca în joc: așa cum sunt scrise, apoi relativ la fișierul care le-a numit, iar pentru fiecare și ca `.dds` în care a fost compilată o textură, `.cdae` în care a fost compilat un `.dae`, sau printr-un fișier `.link` care duce în `/assets`.

## Care nivel {#which-level}

Fără `--level`, fiecare nivel este notat după cât din tur se află pe el:

- Până la 500 de eșantioane ale turului, distribuite uniform, sunt folosite.
- Pentru `TerrainBlock`-ul fiecărui nivel, extinderea terenului se citește din primii cinci octeți ai fișierului lui `.ter`, astfel că un nivel pe care turul nu se află deloc nu costă nimic. Dacă cel puțin 30% din eșantioane sunt în interiorul extinderii, se citesc înălțimile. Un eșantion se numără ca **pe** teren când se află între 1 m sub și 3 m deasupra lui (`ON_GROUND`), pentru că punctul de referință al unei mașini este caroseria, nu roțile.
- Dacă niciun nivel nu obține 50% sau mai mult, nivelurile se notează și după **drumurile** lor. Unele nivele merg dincolo de harta lor de înălțimi (marginile lor continuă ca foi de stâncă). Un eșantion este pe drum când se află în limita semi-lățimii drumului plus 4 m (cel puțin 6 m) de un segment `DecalRoad`, și între 2 m sub și 4 m deasupra lui.
- Cel mai bun nivel câștigă dacă obține cel puțin 30%. Altfel exportul se oprește și listează primele trei cele mai bune: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

Consola spune `on <level>: 87% of the lap lies on its terrain` (sau `roads`). `--level` se potrivește fără diferență între majuscule și minuscule cu numele folderelor de nivel.

## Citirea nivelului {#reading-the-level}

Din ce este făcut un nivel, fiecare parte verificată pe nivelurile livrate (detalii în [Fișierele BeamNG](reader-beamng.md)):

- **Scena**: `levels\<name>\main\**\*.level.json` (un obiect JSON pe linie, sau un tablou JSON), sau un fișier `.mis` pentru nivelurile mai vechi. Instrumentul citește obiectele `TSStatic` (modele plasate, sărind peste cele ascunse), obiectele `Prefab` (cuibărite până la 8 niveluri, `.prefab` TorqueScript sau `.prefab.json`), obiectele `DecalRoad` (drumuri pictate), `TerrainBlock`, `WaterPlane`, `WaterBlock` și `River`.
- **Elemente de pădure**: `levels\<name>\forest\*.forest4.json`, tipizate prin înregistrările `managedItemData.json`. Barierele, gardurile și stâncile sunt elemente de pădure la fel de des ca și copacii.
- **Terenul**: harta de înălțimi `.ter` și harta lui de straturi.
- **Materialele**: fiecare `*.materials.json` din afara `levels\`, plus cele ale acestui nivel.

## Coridorul și decalcurile de drum {#the-corridor-and-the-road-decals}

Coridorul este `--margin` metri în jurul turului, în planul x/y al BeamNG (vedeți [Exportul traseului](course-export.md#the-corridor)). Un coridor de atingere de `margin + 60 m` alege candidații.

**Decalcurile de drum** (`DecalRoad`) sunt unde se află cea mai mare parte a drumurilor BeamNG: pictate pe teren, nu modelate. Decalcurile a căror extindere atinge coridorul de atingere se iau în ordinea de desenare a jocului (`renderPriority` descrescător, apoi ordinea din fișier), și se așază ca panglici:

- Nodurile (x, y, z, lățime) se interpolează printr-un **spline Catmull-Rom centripet** la aproximativ fiecare 1 m. Tipul uniform se întoarce asupra lui însuși acolo unde nodurile se îngrămădesc într-un ac de păr. Drumurile în buclă se închid.
- Fiecare margine ia înălțimea terenului acolo unde terenul este la cel mult 1,5 m de propria înălțime a drumului, și păstrează înălțimea drumului în rest (pe un pod).
- Numele materialului decide ce pictează un decal:

| Tip | Numele materialului se potrivește (prima potrivire câștigă) |
|---|---|
| urme de cauciucuri | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| suprapunere (cosmetic) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| marcaje | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| sol afânat | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| drum | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| suprapunere | orice altceva |

## Solul {#the-ground}

Heightfield-ul terenului din interiorul coridorului devine triunghiuri:

- Un pătrat de patru laturi pe pătratul terenului al cărui centru este în coridor. Pătratele cu stratul 255 (găuri) se sar. Fiecare pătrat este două triunghiuri, cu diagonala alternând cum face terenul Torque.
- Înălțimile sunt `position.z + h * maxHeight / 65535`. Normalele vin din diferențele de înălțime.
- Fiecare pătrat se clasează după **stratul** lui: numele stratului cu modelul de sol și adnotarea materialului terenului. Cuvintele pavate fac `road`, `grass/forest/rock/moss/leaves/cliff/stone` fac `terrain`, iar cuvintele afânate fac `loose` (pietriș și pământ). Orice altceva este `terrain`.
- Apoi **decalcurile de drum și cele afânate suprascriu** pătratele pe care le acoperă, în ordinea desenării, astfel încât ultimul decal pictat decide.
- Vârfurile se împart pe pătrate de 512 m (`floor(x / 512)`, `floor(y / 512)`), astfel încât fiecare parte se mapează într-o singură imagine: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Consola afișează `what the ground is made of` cu numărul de triunghiuri pe fiecare tip.

### Suprafața de rulare modelată {#modelled-driving-surface}

Circuitele BeamNG sunt la fel de des modele ca fiind teren. Pista unui circuit poate fi un singur mesh, cu liniile, cauciucurile și benzile de rulare ca mesh-uri proprii deasupra. Deci modelele plasate din categoriile drum, borduri, margine, recuzită și poduri se caută pentru suprafață de rulare. Pe material:

| Suprafață | Decisă de (prima potrivire) |
|---|---|
| urme de cauciucuri | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` în nume, tipul solului sau adnotare |
| marcaje | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` în numele materialului |
| borduri | `rumble`, `kerb`, `curb` |
| drum | tipul solului `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, sau numele conține `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| sol afânat | tipul solului `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| margine | `sidewalk` |
| (categoria proprie a modelului) | pentru modelele deja clasate drum, borduri sau margine |

Din aceste materiale, triunghiurile **cu fața în sus** (normala z peste 0,5) din interiorul coridorului se scot din model și devin sol. Sunt pictate în textura coaptă a pătratului și scrise ca părți precum `ground:road 3_-2 asphalt_light`. Marcajele și urmele de cauciucuri sunt doar pictate. Triunghiurile rămase ale modelului rămân cu modelul. Aceste modele nu se simplifică și nu se lasă afară de buget, pentru că o pistă grosolană ar fi o pistă greșită.

## Textura coaptă a solului {#the-baked-ground-texture}

Fiecare pătrat de 512 m care are sol primește o imagine de `--texture-size` pixeli (2048 = 25 cm un pixel), desenată cum desenează jocul solul:

1. **Straturile terenului.** Pe pixel, straturile celor patru pătrate de teren din jur se amestecă biliniar. Fiecare strat este colorat cum îl colorează jocul: harta **de bază** a materialului întinsă pe `diffuseSize` metri (sau pe tot terenul), apoi hărțile de **detaliu** și **macro** ca suprapuneri gri (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutru). Repetarea lor implicită este la fiecare 2 m și 60 m, cu puteri de 0,5 și 0,3, dacă materialul nu spune altfel. Un strat fără material primește culoarea plată a suprafeței lui. Rândul 0 al hărții de bază este nordul.
2. **Decalcurile de drum** pictate doar pe teren, în ordinea desenării, fiecare cu propria textură, hartă de opacitate, nuanță și opacitate, de-a lungul panglicii. Nivelurile livrate folosesc priorități în jur de 12-16 pentru bazele de asfalt, 10 pentru marcaje și 4 pentru cauciuc.
3. **Suprafața de rulare modelată** văzută de sus: întâi bazele, apoi suprapunerile, fiecare în propria textură repetitivă a modelului, la un texel pe pixelul de coacere.
4. **Decalcurile care se proiectează și peste obiecte** (`overObjects`), la urmă.

Cu `--no-textures`, nu se coace nimic: piesele de sol primesc culori plate, iar marcajele și urmele de cauciucuri modelate devin piese proprii, ridicate cu **3 cm**.

## Modele plasate {#placed-models}

Candidații sunt fiecare `TSStatic`, copil de prefab și element de pădure a cărui origine se află în coridorul de atingere. Un candidat se desenează dacă cutia lui de delimitare mondială atinge coridorul.

**Categoria** vine din adnotarea nivelului și din calea formei. Prima regulă care se potrivește câștigă:

| Categorie | Adnotare | Calea sau numele conține |
|---|---|---|
| fundal (nu se desenează niciodată) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| borduri | | `kerb`, `curb`, `rumble` |
| drum | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| margine | `SIDEWALK`, `COBBLESTONE` | |
| copaci (doar cu `--trees`) | `NATURE` | tree, foliage, bush, grass, plant și cuvinte asemănătoare |
| stânci | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| bariere | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| indicatoare | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| poduri | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastructură | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| clădiri | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| recuzită | | orice altceva |

**Formele** se citesc din `.cdae` compilat, sau din `.dae` Collada acolo unde nu există memorie cache (moduri). O formă care nu poate fi citită se numără: `N copies of M models could not be read`. Materialele numite sau texturate `invisible`, `collision` sau `nodraw` nu se desenează niciodată.

**Texturi.** Modelele se grupează pe categorie și material în părți numite `structure:<category> <material>` (sau `ground:kerbs <material>`). Un grup primește textura de culoare a materialului său, de până la **256 px**, doar dacă coordonatele lui UV rămân între 0 și 1 (98% din vârfuri între -0,02 și 1,02). Vizualizatorul împachetează texturile într-un atlas și nu poate repeta una. Un grup a cărui textură se repetă se desenează în culoarea medie a texturii (ponderată cu alfa, în sRGB, înmulțită cu nuanța materialului), sau în culoarea categoriei dacă nu are textură.

**Detaliul** urmează schema comună din [Nivelurile de detaliu și bugetul](detail-budget.md). Nivelurile de detaliu ale BeamNG sunt `details` ale formei (cel mai mare pixel-size primul). Peste buget, copiile cele mai îndepărtate pleacă primele. Bordurile și modelele care poartă suprafață de rulare nu se simplifică și nu se lasă afară niciodată.

`--no-placed` scoate structurile, dar păstrează suprafața de rulare modelată. `--trees` adaugă categoria copacilor.

## Apa {#water}

| Sursă | Desenată ca |
|---|---|
| `WaterPlane` (marea) | un patrulater de 4 m la înălțimea apei pentru fiecare celulă a coridorului unde niciun teren nu ajunge la acea înălțime |
| `WaterBlock` | un patrulater, pătratul unitate la z local = 0 în transformarea blocului (deci scara lui îi dă mărimea), dacă atinge coridorul; dacă z = 0 este suprafața blocului nu este verificat |
| `River` | o panglică prin nodurile lui, dacă atinge coridorul |

Toată apa este o singură parte plană, `water:water`.

## Ce nu se desenează {#not-drawn}

- Acoperirea solului (iarba procedurală).
- Decorul plasat la marginea lumii (`backdrop` și asemenea).
- Texturile repetitive ale modelelor, care ies ca o culoare medie (vedeți mai sus).
- Modelele scheletice (vehicule, personaje) și mesh-urile decalurilor din interiorul formelor.

## Verificările din spatele lui {#checks-behind-it}

Cum spune sursa, măsurate pe nivelurile livrate:

- Nodurile de drum se află pe teren la 1-2 cm (mediană) pe nivelurile verificate, cu `h * maxHeight / 65535` și rânduri pe +y. `h / 32` sau cealaltă ordine a axelor greșesc cu zeci până la sute de metri.
- Secțiunile de șine înlănțuite de-a lungul unui drum merg pe rândul 0 al `rotationMatrix` (marea majoritate).
- Rotația nodului `.cdae` trebuie transpusă. Cu asta, cutiile lumii se potrivesc cu `.dae` sursă până la milimetru. Modul clasic ar fi 38 cm greșit (mediană).
- Exportat pe mai multe niveluri livrate din fiecare fel, în secunde până la minute fiecare.
