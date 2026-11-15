---
title: BeamNG.drive
nav_order: 2
lang: "sl"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Izvoz tečaja: BeamNG.drive {#course-export-beamngdrive}

Izvoz BeamNG prebere nivo tako, kot ga igra montira, nato zapiše isto vrsto datoteke
kot izvoz Forze: tla po kvadratih 512 m s speče teksturo, cesto in rahla tla kot
ločena dela, postavljene modele po kategorijah in vodo.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Viri: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (namestitev, datotečni sistem, prizor, teren, materiali),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (izvoz),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) in
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (oblike).
Podrobne oblike datotek: [Datoteke BeamNG](reader-beamng.md).

## Okvir lapa {#the-laps-frame}

Izvoz `course` pričakuje položaje BeamNG v **okvirju pregledovalnika**:
`(x, z, -y)` svetovnega sistema BeamNG z osjo Z navzgor, v metrih. To je rotacija, ki
jo uporabi snemalnik telemetrije 3DHeat. Izvoz lap pretvori nazaj v okvir BeamNG
(`(x, -z, y)`), tam dela in vse zapiše spet v okvirju pregledovalnika. To je rotacija, ne
zrcaljenje, zato nič ne pride zrcalno. Lap, posnet v surovem okvirju BeamNG, ne bi bil
postavljen. To ni bilo preizkušeno z drugimi snemalniki.

Igra se šteje za BeamNG, kadar datoteka `heat3d-lap` pravi `"game": "beamng"` ali
kadar podate `--game beamng`.

## Iskanje namestitve {#finding-the-install}

- `--install <folder>`: mapa, ki vsebuje `gameengine.zip` in `content`.
- Sicer se preveri `steamapps\common\BeamNG.drive` v vsaki knjižnici Steam za ti dve
  datoteki.
- Če nobeno ne uspe: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Datotečni sistem {#the-file-system}

BeamNG dostavlja navadne arhive zip in jih montira v en datotečni sistem, na katerega
se sklicujejo nivoji (`/art/shapes/...`, `/assets/materials/...`). Izvoz zgradi isto
stvar: en indeks, neobčutljiv na velike in male črke, nad

1. `gameengine.zip`,
2. vsako datoteko `*.zip` pod `content`, razen `content\vehicles\*` in arhivov, katerih
   imena se začnejo z `art_sound` ali `audio`,
3. uporabniško vsebino, z najnovejšo postavitvijo najprej: pod
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` in `%LOCALAPPDATA%\BeamNG.drive`, mapa
   `current` in mapa različice z najvišjo številko. Iz vsake: `mods\*.zip`, vsaka mapa
   v `mods\unpacked` in sama uporabniška mapa, če ima mapo `levels`.

Kasnejši dodatki zmagajo, kakor v igri, zato modifikacija nadomesti to, kar prepiše.
Modifikacije so v izvozu tečaja vedno vključene.

Poti, ki jih nivo navede, se razrešijo tako kot v igri: kot so navedene, nato glede na
datoteko, ki jih je navedla, in za vsako tudi kot `.dds`, v katerega je bila tekstura
pripravljena, `.cdae`, v katerega je bila pripravljena `.dae`, ali prek datoteke `.link`,
ki kaže v `/assets`.

## Kateri nivo {#which-level}

Brez `--level` se vsak nivo oceni po tem, koliko lapa leži na njem:

- Uporabi se do 500 vzorcev lapa, enakomerno razporejenih.
- Za `TerrainBlock` vsakega nivoja se razširitev terena prebere iz prvih pet bajtov
  njegove datoteke `.ter`, zato nivo, do katerega lap ni blizu, ne stane nič. Če je
  vsaj 30 % vzorcev znotraj razširitve, se višine preberejo. Vzorec šteje kot **na**
  terenu, kadar je med 1 m pod njim in 3 m nad njim (`ON_GROUND`), ker je referenčna
  točka avtomobila njegovo telo, ne pnevmatike.
- Če nobeden nivo ne doseže 50 %, se nivoji ocenijo tudi po njihovih **cestah**. Nekateri
  nivoji tečejo onkraj svoje višinske karte (njihovi robovi se nadaljujejo kot skalne
  plošče). Vzorec je na cesti, kadar leži znotraj polovične širine ceste plus 4 m (vsaj
  6 m) od segmenta `DecalRoad`, in med 2 m pod njo in 4 m nad njo.
- Najboljši nivo zmaga, če doseže vsaj 30 %. Sicer se izvoz ustavi in izpiše najboljše
  tri: "the lap does not lie on any installed level's terrain (best: ...). Name the
  level with --level."

Konzola izpiše `on <level>: 87% of the lap lies on its terrain` (ali `roads`).
`--level` se primerja z imeni map nivojev, brez razlikovanja velikih in malih črk.

## Branje nivoja {#reading-the-level}

Iz česa je nivo sestavljen, vsak del preverjen na objavljenih nivojih (podrobnosti v
[Datoteke BeamNG](reader-beamng.md)):

- **Prizor**: `levels\<name>\main\**\*.level.json` (en objekt JSON na vrstico ali
  polje JSON), ali datoteka `.mis` pri starejših nivojih. Orodje bere objekte `TSStatic`
  (postavljeni modeli, skrite preskoči), objekte `Prefab` (gnezdeni do 8 globoko,
  TorqueScript `.prefab` ali `.prefab.json`), objekte `DecalRoad` (narisane ceste),
  `TerrainBlock`, `WaterPlane`, `WaterBlock` in `River`.
- **Gozdni predmeti**: `levels\<name>\forest\*.forest4.json`, tipizirani prek zapisov
  `managedItemData.json`. Ograje, plotovi in skale so gozdni predmeti tako pogosto kot
  drevesa.
- **Teren**: višinski model `.ter` in njegova karta plasti.
- **Materiali**: vsaka datoteka `*.materials.json` zunaj `levels\`, plus tiste tega nivoja.

## Koridor in dekali cest {#the-corridor-and-the-road-decals}

Koridor je `--margin` metrov okoli lapa v ravnini x/y BeamNG (glejte
[Izvoz tečaja](course-export.md#the-corridor)). Koridor dosega `margin + 60 m` izbere
kandidate.

**Dekali cest** (`DecalRoad`) so tam, kjer je večina cest BeamNG: naslikani na teren,
niso modelirani. Dekali, katerih razširitev se dotika koridorja dosega, se vzamejo v
vrstnem redu risanja igre (padajoč `renderPriority`, nato vrstni red datotek) in
razporedijo kot trakovi:

- Vozlišča (x, y, z, širina) se interpolirajo s **centripetalnim Catmull-Rom zlepkom**
  približno na vsak 1 m. Enakomerna vrsta se zanka nazaj na samo sebe, kjer se vozlišča
  zgostijo v zavoju. Zaprte ceste se sklenejo.
- Vsak rob prevzame višino terena, kjer je teren znotraj 1,5 m od lastne višine ceste,
  drugje ohrani višino ceste (na mostu).
- Ime materiala odloči, kaj dekal slika:

| Vrsta | Ime materiala se ujema (prvo ujemanje velja) |
|---|---|
| sledi pnevmatik | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| prekrivni (kozmetični) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| oznake | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| rahlo | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| cesta | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| prekrivni | vse drugo |

## Tla {#the-ground}

Višinski model terena znotraj koridorja postane trikotniki:

- En četverokotnik na kvadrat terena, katerega središče je v koridorju. Kvadrati s
  plastjo 255 (luknje) se preskočijo. Vsak četverokotnik sta dva trikotnika, z diagonalo,
  ki se menja, kakor to dela teren Torque.
- Višine so `position.z + h * maxHeight / 65535`. Normale izhajajo iz višinskih razlik.
- Vsak kvadrat se razvrsti po svoji **plasti**: ime plasti z modelom tal in opombo
  materiala terena. Tlakovane besede naredijo `road`, `grass/forest/rock/moss/leaves/cliff/stone`
  naredijo `terrain`, rahle besede pa `loose` (gramoz in zemlja). Vse drugo je `terrain`.
- Nato **dekali ceste in rahlih tal prepišejo** kvadrate, ki jih pokrivajo, po vrstnem
  redu risanja, zato odloči zadnji naslikani dekal.
- Oglišča se razdelijo po kvadratih 512 m (`floor(x / 512)`, `floor(y / 512)`), tako da
  vsak del pade v natanko eno sliko: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konzola izpiše `what the ground is made of` s števili trikotnikov po vrsti.

### Modelirana vozna površina {#modelled-driving-surface}

Proge BeamNG so pogosto modeli, ne teren. Proga na dirkališču je lahko ena mreža z
lastnimi črtami, gumo in robniki kot mrežami na vrhu. Zato se postavljeni modeli v
kategorijah ceste, robniki, rob, rekviziti in mostovi preiščejo za vozno površino. Po
materialu:

| Površina | Določi (prvo ujemanje) |
|---|---|
| sledi pnevmatik | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` v imenu, vrsti tal ali opombi |
| oznake | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` v imenu materiala |
| robniki | `rumble`, `kerb`, `curb` |
| cesta | vrsta tal `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ali ime vsebuje `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| rahlo | vrsta tal `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| rob | `sidewalk` |
| (lastna kategorija modela) | za modele že razvrščene kot ceste, robniki ali rob |

Od teh materialov se **trikotniki, obrnjeni navzgor** (normala z nad 0,5) znotraj
koridorja vzamejo iz modela in postanejo tla. Naslikajo se v zapečeno teksturo ploščice
in se zapišejo kot deli, na primer `ground:road 3_-2 asphalt_light`. Oznake in sledi
pnevmatik se samo slikajo. Preostali trikotniki modela ostanejo pri modelu. Ti modeli
se nikoli ne poenostavijo ali izpustijo zaradi proračuna, ker je grob tir napačen tir.

## Zapečena tekstura tal {#the-baked-ground-texture}

Vsak kvadrat 512 m, ki ima tla, dobi eno sliko velikosti `--texture-size` pik (2048 =
25 cm na piko), narisano tako, kot igra riše svoja tla:

1. **Plasti terena.** Za vsako piko se plasti štirih okoliških kvadratov terena mešajo
   bilinearno. Vsaka plast je obarvana tako, kot jo igra barva: **osnovna karta**
   materiala se raztegne čez `diffuseSize` metrov (ali čez ves teren), nato
   **podrobnostna** in **makro** karta kot sive prekrivke
   (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 nevtralno). Njuni privzeti
   vzorci se ponavljajo na 2 m in 60 m, z močmi 0,5 in 0,3, razen če material pravi
   drugače. Plast brez materiala dobi ploska barvo svoje površine. Vrstica 0 osnovne
   karte je sever.
2. **Dekali cest**, ki so naslikani samo na terenu, po vrstnem redu risanja, vsak s
   svojo teksturo, karto neprozornosti, odtenkom in neprozornostjo, vzdolž traku.
   Nameščeni nivoji uporabljajo prednosti okoli 12-16 za asfaltne podlage, 10 za oznake
   in 4 za gumo.
3. **Modelirana vozna površina**, gledana od zgoraj: najprej podlage, nato prekrivke,
   vsaka v lastni ponavljajoči se teksturi modela na eno texel na piko pečenja.
4. **Dekali, ki se projicirajo tudi čez predmete** (`overObjects`), na koncu.

Z `--no-textures` se ne peče ničesar: deli tal dobijo ploske barve, modelirane oznake
in sledi pnevmatik pa postanejo lastni deli, dvignjeni za **3 cm**.

## Postavljeni modeli {#placed-models}

Kandidati so vsak `TSStatic`, otrok prefaba in gozdni predmet, katerega izhodišče je v
koridoru dosega. Kandidat se nariše, če se svetovna omejevalna škatla njegove oblike
dotika koridorja.

**Kategorijo** da oznaka nivoja in pot oblike. Prvo pravilo, ki se ujema, velja:

| Kategorija | Oznaka | Pot ali ime vsebuje |
|---|---|---|
| ozadje (nikoli narisano) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| robniki | | `kerb`, `curb`, `rumble` |
| cesta | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| rob | `SIDEWALK`, `COBBLESTONE` | |
| drevesa (samo z `--trees`) | `NATURE` | tree, foliage, bush, grass, plant in podobne besede |
| skale | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| ovire | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| znaki | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| mostovi | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktura | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| stavbe | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekviziti | | vse drugo |

**Oblike** se preberejo iz prevedenega `.cdae` ali iz Collada `.dae`, kjer predpomnilnik
ne obstaja (modifikacije). Oblika, ki je ni mogoče prebrati, se prešteje:
`N copies of M models could not be read`. Materiali, poimenovani ali teksturirani kot
`invisible`, `collision` ali `nodraw`, se nikoli ne narišejo.

**Teksture.** Modeli se združijo po kategoriji in materialu v dele z imenom
`structure:<category> <material>` (ali `ground:kerbs <material>`). Skupina dobi barvno
teksturo svojega materiala do največ **256 px**, samo če njene koordinate UV ostanejo
znotraj 0-1 (98 % oglišč v -0,02 do 1,02). Upodabljalnik pakira teksture v atlas in
ene ne more ponoviti. Skupina, katere tekstura se ponavlja, se nariše v povprečni barvi
teksture (utežena z alfo, v sRGB, pomnožena z barvnim odtenkom materiala), ali v barvi
kategorije, če nima teksture.

**Podrobnost** sledi skupni shemi v [Stopnje podrobnosti in proračun](detail-budget.md).
Stopnje podrobnosti BeamNG so `details` oblike (najprej največja velikost v pikah).
Čez proračun gredo najprej najbolj oddaljene kopije. Robniki in modeli, ki nosijo
vozno površino, se nikoli ne poenostavijo ali izpustijo.

`--no-placed` odstrani strukture, a ohrani modelirano vozno površino. `--trees` doda
kategorijo dreves.

## Voda {#water}

| Vir | Narisano kot |
|---|---|
| `WaterPlane` (morje) | četverokotnik 4 m na višini vode za vsako celico koridorja, kjer teren ne doseže te višine |
| `WaterBlock` | en četverokotnik, enotski kvadrat pri lokalnem z = 0 v transformaciji bloka (njegovo merilo določi velikost), če se dotika koridorja; ali je z = 0 površina bloka, ni preverjeno |
| `River` | trak skozi njegova vozlišča, če se dotika koridorja |

Vsa voda je en sam ploski del, `water:water`.

## Ni narisano {#not-drawn}

- Pokrov tal (proceduralna trava).
- Scenografija, postavljena ob robu sveta (`backdrop` in podobno).
- Ponavljajoče se teksture modelov, ki se pokažejo kot povprečna barva (glejte zgoraj).
- Skinned mreže (vozila, osebe) in mreže nalepk znotraj oblik.

## Preverjanja v ozadju {#checks-behind-it}

Kakor je navedeno v viru, izmerjeno na objavljenih nivojih:

- Vozlišča ceste ležijo na terenu do 1-2 cm (mediana) na preverjenih nivojih, z
  `h * maxHeight / 65535` in vrsticami vzdolž +y. `h / 32` ali drugi vrstni red osi
  zgrešita za desetine do stotine metrov.
- Odseki železnice, povezani vzdolž ceste, tečejo vzdolž vrstice 0 `rotationMatrix`
  (velika večina).
- Rotacijo vozlišča `.cdae` je treba transponirati. Z njo se svetovne omejitve ujemajo
  z izvornim `.dae` do milimetra. Po običajnem, učbeniškem načinu so za 38 cm narazen (mediana).
- Izvoženo na več objavljenih nivojih vsake vrste, v sekundah do minut vsak.
