---
title: "BeamNG.drive"
nav_order: 2
lang: "bs"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Izvoz staze: BeamNG.drive {#course-export-beamngdrive}

BeamNG izvoz čita nivo onako kako ga igra montira, a zatim piše istu vrstu
datoteke kao i Forza izvoz: tlo po kvadratu od 512 m s pečenom teksturom, cestu i
rastresito tlo kao zasebne dijelove, postavljene modele po kategorijama i
vodu.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Izvori: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalacija, datotečni sistem, scena, teren, materijali),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (izvoz),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) i
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (oblici).
Formati datoteka detaljno: [BeamNG datoteke](reader-beamng.md).

## Koordinatni okvir kruga {#the-laps-frame}

Izvoz `course` očekuje BeamNG pozicije u **okviru preglednika**:
`(x, z, -y)` BeamNG-ovog svijeta s Z prema gore, u metrima. To je rotacija koju primjenjuje
3DHeat snimač telemetrije. Izvoz vraća krug u BeamNG-ov okvir
(`(x, -z, y)`), radi tamo, i sve ponovo upisuje u okviru preglednika. Ovo je rotacija, a ne zrcaljenje, pa ništa ne ispadne zrcaljeno. Krug
snimljen u BeamNG-ovom sirovom okviru ne bi bio postavljen. Ovo nije testirano s
drugim snimačima.

Igra se uzima kao BeamNG kad datoteka `heat3d-lap` kaže `"game": "beamng"`,
ili kad date `--game beamng`.

## Pronalaženje instalacije {#finding-the-install}

- `--install <folder>`: folder koji sadrži `gameengine.zip` i `content`.
- Inače se u svakoj Steam biblioteci provjerava `steamapps\common\BeamNG.drive`
  za ta dva.
- Ako ništa ne uspije: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Datotečni sistem {#the-file-system}

BeamNG isporučuje obične zip arhive i montira ih u jedan datotečni sistem na koji se
nivoi pozivaju (`/art/shapes/...`, `/assets/materials/...`). Izvoz gradi
istu stvar: jedan indeks bez razlike velikih i malih slova nad

1. `gameengine.zip`,
2. svakim `*.zip` pod `content`, osim `content\vehicles\*` i arhiva čija
   imena počinju s `art_sound` ili `audio`,
3. korisničkim sadržajem, prvo najnoviji raspored: pod
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` i `%LOCALAPPDATA%\BeamNG.drive`,
   folder `current` i folder verzije s najvećim brojem. Iz svakog:
   `mods\*.zip`, svaki folder u `mods\unpacked`, i sam korisnički folder ako
   ima folder `levels`.

Kasnija dodavanja pobjeđuju, kao u igri, pa mod zamjenjuje ono što nadjačava. Modovi se
uvijek uključuju u izvoz staze.

Putanje koje nivo imenuje rješavaju se onako kako ih igra rješava: kako su mu, zatim
relativno prema datoteci koja ih je imenovala, a za svaku i kao `.dds` u koji je tekstura
skuhana, `.cdae` u koji je `.dae` kompajliran, ili preko `.link` datoteke
koja pokazuje u `/assets`.

## Koji nivo {#which-level}

Bez `--level`, svaki nivo se ocjenjuje po tome koliko kruga leži na njemu:

- Koristi se do 500 uzoraka kruga, ravnomjerno raspoređenih.
- Za `TerrainBlock` svakog nivoa, opseg terena čita se iz prvih
  pet bajtova njene `.ter` datoteke, pa nivo kojem krug nije ni blizu ne košta ništa.
  Ako je najmanje 30% uzoraka unutar opsega, čitaju se visine. Uzorak
  se računa kao **na** terenu kad je između 1 m ispod i 3 m iznad
  njega (`ON_GROUND`), jer je referentna tačka automobila njegova karoserija, a ne gume.
- Ako nijedan nivo ne postigne 50% ili više, nivoi se ocjenjuju i po svojim **cestama**. Neki
  nivoi nastavljaju poslije svoje mape visina (njihove ivice se nastavljaju kao stijene u listovima). Uzorak je na cesti kad leži unutar polovine širine ceste plus
  4 m (najmanje 6 m) od segmenta `DecalRoad`, i između 2 m ispod i 4 m iznad
  njega.
- Najbolji nivo pobjeđuje ako postigne najmanje 30%. Inače se izvoz zaustavlja i
  ispisuje tri najbolja: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

Konzola kaže `on <level>: 87% of the lap lies on its terrain` (ili `roads`).
`--level` se poredi bez razlike velikih i malih slova s imenima foldera nivoa.

## Čitanje nivoa {#reading-the-level}

Od čega se nivo sastoji, svaki dio provjeren prema isporučenim nivoima
(detalji na [BeamNG datoteke](reader-beamng.md)):

- **Scena**: `levels\<name>\main\**\*.level.json` (jedan JSON objekat po redu, ili
  JSON niz), ili `.mis` datoteka za starije nivoe. Alat čita `TSStatic`
  objekte (postavljeni modeli, preskačući skrivene), `Prefab` objekte (ugniježđene do 8
  nivoa, TorqueScript `.prefab` ili `.prefab.json`), `DecalRoad` objekte (oslikane
  ceste), `TerrainBlock`, `WaterPlane`, `WaterBlock` i `River`.
- **Šumski objekti**: `levels\<name>\forest\*.forest4.json`, tipizirani preko zapisa
  `managedItemData.json`. Ograde, plotovi i stijene su šumski objekti jednako
  često kao i drveće.
- **Teren**: heightfield `.ter` i njegova mapa slojeva.
- **Materijali**: svaki `*.materials.json` izvan `levels\`, plus oni ovog
  nivoa.

## Koridor i dekali cesta {#the-corridor-and-the-road-decals}

Koridor je `--margin` metara oko kruga u BeamNG-ovoj x/y ravni (pogledajte
[Izvoz staze](course-export.md#the-corridor)). Koridor dosega od
`margin + 60 m` bira kandidate.

**Dekali cesta** (`DecalRoad`) su mjesto gdje je većina BeamNG-ovih cesta: oslikani na
terenu, a ne modelirani. Dekali čiji opseg dodiruje koridor dosega
uzimaju se redoslijedom crtanja igre (opadajući `renderPriority`, zatim redoslijed u datoteci),
razloženi kao trake:

- Čvorovi (x, y, z, širina) interpoliraju se **centripetalnim Catmull-Rom**
  splajnom otprilike svaki 1 m. Uniformna vrsta se vrti u petlji kad se čvorovi
  zbiju na ukosnici. Cestovne petlje se zatvaraju.
- Svaka ivica uzima visinu terena gdje je teren unutar 1,5 m od
  visine same ceste, a drugdje zadržava visinu ceste (na mostu).
- Ime materijala odlučuje šta dekal slika:

| Vrsta | Ime materijala se poklapa s (pobjeđuje prvo poklapanje) |
|---|---|
| tragovi guma | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| preklop (kozmetički) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| oznake | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| rastresito | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| cesta | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| preklop | sve ostalo |

## Tlo {#the-ground}

Heightfield terena unutar koridora postaje trouglovi:

- Jedan kvad po kvadratu terena čije je središte u koridoru. Kvadrati sa slojem
  255 (rupe) se preskaču. Svaki kvad su dva trougla, s dijagonalom koja
  se smjenjuje onako kako to radi Torqueov teren.
- Visine su `position.z + h * maxHeight / 65535`. Normale dolaze iz razlika
  visina.
- Svaki kvadrat se razvrstava po svom **sloju**: ime sloja s modelom tla
  i anotacijom njegovog materijala terena. Riječi za asfalt daju `road`,
  `grass/forest/rock/moss/leaves/cliff/stone` daju `terrain`, a riječi za rastresito tlo daju
  `loose` (šljunak i zemlja). Sve ostalo je `terrain`.
- Zatim **dekali ceste i rastresitog tla poništavaju** kvadrate koje pokrivaju, redoslijedom
  crtanja, pa odlučuje zadnji naslikani dekal.
- Vrhovi se dijele po kvadratu od 512 m (`floor(x / 512)`, `floor(y / 512)`), pa
  se svaki dio mapira u tačno jednu sliku: `u = (x - x0) / 512`,
  `v = 1 - (y - y0) / 512`.

Konzola ispisuje `what the ground is made of` s brojem trouglova po vrsti.

### Modelirana površina za vožnju {#modelled-driving-surface}

BeamNG-ovi krugovi su modeli jednako često kao i teren. Staza trkališta može
biti jedna mreža, s linijama, gumom i rumble trakama kao zasebnim mrežama
na njoj. Zato se postavljeni modeli u kategorijama cesta, ivičnjaci, rub, rekviziti i mostovi
pretražuju za površinu za vožnju. Po materijalu:

| Površina | Odlučuje (pobjeđuje prvo poklapanje) |
|---|---|
| tragovi guma | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` u imenu, vrsti tla ili anotaciji |
| oznake | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` u imenu materijala |
| ivičnjaci | `rumble`, `kerb`, `curb` |
| cesta | vrsta tla `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ili ime sadrži `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| rastresito | vrsta tla `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| rub | `sidewalk` |
| (vlastita kategorija modela) | za modele već razvrstane kao cesta, ivičnjaci ili rub |

Od tih materijala, trouglovi **okrenuti prema gore** (normala z iznad 0,5) unutar
koridora vade se iz modela i postaju tlo. Slikaju se u pečenu teksturu
pločice i upisuju kao dijelovi poput
`ground:road 3_-2 asphalt_light`. Oznake i tragovi guma samo se slikaju. Preostali
trouglovi modela ostaju uz model. Ovi modeli se nikad
ne pojednostavljuju niti izostavljaju zbog budžeta, jer je gruba staza pogrešna staza.

## Pečena tekstura tla {#the-baked-ground-texture}

Svaki kvadrat od 512 m koji ima tlo dobiva jednu sliku od `--texture-size` piksela
(2048 = 25 cm po pikselu), nacrtanu onako kako igra crta svoje tlo:

1. **Slojevi terena.** Po pikselu, slojevi četiri okolna kvadrata terena miješaju se
   bilinearno. Svaki sloj se boji kako ga igra boji: **osnovna mapa**
   materijala razvučena preko `diffuseSize` metara (ili cijelog
   terena), zatim **detail** i **macro** mape kao sivi preklopi
   (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutralno). Njihove zadane vrijednosti
   ponavljaju se svakih 2 m i 60 m, s jačinama 0,5 i 0,3, osim ako materijal ne kaže
   drugačije. Sloj bez materijala dobiva ravnu boju svoje površine. Red 0
   osnovne mape je sjever.
2. **Dekali ceste** koji su naslikani samo na terenu, redoslijedom crtanja, svaki
   sa svojom teksturom, mapom prozirnosti, nijansom i prozirnošću, duž trake.
   Isporučeni nivoi koriste prioritete oko 12-16 za asfaltne osnove, 10 za oznake
   i 4 za gumu.
3. **Modelirana površina za vožnju** viđena odozgo: prvo osnove, zatim preklopi, svaki
   u vlastitoj ponavljajućoj teksturi modela s jednim teksel po pikselu pečenja.
4. **Dekali koji se projiciraju i preko objekata** (`overObjects`), zadnji.

Uz `--no-textures` ništa se ne peče: dijelovi tla dobivaju ravne boje, a
modelirane oznake i tragovi guma postaju zasebni dijelovi, podignuti **3 cm**.

## Postavljeni modeli {#placed-models}

Kandidati su svaki `TSStatic`, dijete prefaba i šumski objekat čije ishodište leži u
koridoru dosega. Kandidat se crta ako granična kutija njegovog oblika u svijetu dodiruje
koridor.

**Kategorija** dolazi iz vlastite anotacije nivoa i putanje oblika. Pobjeđuje
prvo pravilo koje se poklopi:

| Kategorija | Anotacija | Putanja ili ime sadrži |
|---|---|---|
| pozadina (nikad se ne crta) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| ivičnjaci | | `kerb`, `curb`, `rumble` |
| cesta | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| rub | `SIDEWALK`, `COBBLESTONE` | |
| drveće (samo uz `--trees`) | `NATURE` | tree, foliage, bush, grass, plant i slične riječi |
| stijene | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| ograde | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| znakovi | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| mostovi | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktura | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| zgrade | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekviziti | | sve ostalo |

**Oblici** se čitaju iz kompajliranog `.cdae`, ili iz Collada `.dae` gdje nema
keša (modovi). Oblik koji se ne može pročitati se broji:
`N copies of M models could not be read`. Materijali nazvani ili teksturirani
`invisible`, `collision` ili `nodraw` nikad se ne crtaju.

**Teksture.** Modeli se grupiraju po kategoriji i materijalu u dijelove nazvane
`structure:<category> <material>` (ili `ground:kerbs <material>`). Grupa dobiva
teksturu boje svog materijala do **256 px** samo ako njeni UV-ovi ostaju unutar 0-1
(98% vrhova unutar -0,02 do 1,02). Preglednik pakira teksture u atlas
i ne može ponavljati nijednu. Grupa čija se tekstura ponavlja crta se u prosječnoj
boji teksture (otežanoj alfom, u sRGB, puta nijansa materijala), ili u
boji kategorije ako nema teksturu.

**Detalj** slijedi zajedničku šemu na
[Nivoi detalja i budžet](detail-budget.md). BeamNG-ovi nivoi detalja su
`details` oblika (prvo najveća veličina u pikselima). Preko budžeta, najudaljenije
kopije idu prve. Ivičnjaci i modeli koji nose površinu za vožnju nikad se ne pojednostavljuju
niti izostavljaju.

`--no-placed` izbacuje strukture ali i dalje zadržava modeliranu površinu za vožnju.
`--trees` dodaje kategoriju drveća.

## Voda {#water}

| Izvor | Crta se kao |
|---|---|
| `WaterPlane` (more) | kvad od 4 m na visini vode za svaku ćeliju koridora gdje nijedan teren ne dosegne tu visinu |
| `WaterBlock` | jedan kvad, jedinični kvadrat na lokalnom z = 0 u transformaciji bloka (pa njegova skala određuje veličinu), ako dodiruje koridor; je li z = 0 površina bloka nije provjereno |
| `River` | traka kroz njegove čvorove ako dodiruje koridor |

Sva voda je jedan ravan dio, `water:water`.

## Ne crta se {#not-drawn}

- Pokrivač tla (procedurana trava).
- Scenografija postavljena oko ruba svijeta (`backdrop` i slično).
- Ponavljajuće teksture modela, koje ispadnu kao prosječna boja (pogledajte gore).
- Skinned mreže (vozila, likovi) i dekal mreže unutar oblika.

## Provjere iza toga {#checks-behind-it}

Kako stoji u izvoru, izmjereno na isporučenim nivoima:

- Čvorovi ceste leže na terenu na 1-2 cm (medijan) na provjerenim nivoima, s `h * maxHeight / 65535` i redovima duž +y. `h / 32` ili drugi redoslijed osa promašuju za desetke do stotine metara.
- Dijelovi ograde nanizani duž ceste idu duž reda 0 matrice `rotationMatrix` (velika većina).
- Rotacija čvora `.cdae` mora se transponirati. S tim se granice u svijetu poklapaju s izvornim `.dae` do milimetra. Udžbenički način je 38 cm pogrešan (medijan).
- Izvezeno na nekoliko isporučenih nivoa svake vrste, svaki za sekunde do minute.
