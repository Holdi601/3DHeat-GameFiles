---
title: BeamNG.drive
nav_order: 2
lang: "hr"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Izvoz staze: BeamNG.drive {#course-export-beamngdrive}

Izvoz BeamNG-a čita razinu onako kako je igra montira, a zatim piše istu vrstu datoteke koju piše izvoz Forze: tlo po kvadratu od 512 m s pečenom teksturom, cesta i rubno tlo kao vlastiti dijelovi, postavljeni modeli po kategoriji, te voda.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Izvori: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalacija, datotečni sustav, scena, teren, materijali),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (izvoz),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) i
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (oblici).
Formati datoteka u detalju: [BeamNG datoteke](reader-beamng.md).

## Okvir kruga {#the-laps-frame}

Izvoz `course` očekuje BeamNG pozicije u **okviru preglednika**: `(x, z, -y)` svjetskog prostora BeamNG-a s Z prema gore, u metrima. To je rotacija koju primjenjuje 3DHeat snimač telemetrije. Izvoz vraća krug u BeamNG-ov okvir (`(x, -z, y)`), radi tamo i sve ponovno zapisuje u okviru preglednika. Riječ je o rotaciji, a ne o zrcaljenju, pa ništa ne izlazi zrcaljeno. Krug snimljen u sirovom BeamNG okviru ne bi bio postavljen na pravo mjesto. Ovo nije testirano s drugim snimačima.

Igra se uzima kao BeamNG kada datoteka `heat3d-lap` kaže `"game": "beamng"`, ili kada zadate `--game beamng`.

## Pronalaženje instalacije {#finding-the-install}

- `--install <folder>`: mapa koja sadrži `gameengine.zip` i `content`.
- Inače se provjerava `steamapps\common\BeamNG.drive` u svakoj Steam biblioteci, traže se ta dva.
- Ako ni to ne uspije, ispisuje se: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)."

## Datotečni sustav {#the-file-system}

BeamNG isporučuje obične zip arhive i montira ih u jedan datotečni sustav na koji se razine pozivaju (`/art/shapes/...`, `/assets/materials/...`). Izvoz gradi isto: jedan indeks bez razlike između velikih i malih slova nad:

1. `gameengine.zip`,
2. svakim `*.zip` pod `content`, osim `content\vehicles\*` i arhiva čija imena počinju s `art_sound` ili `audio`,
3. korisnikovim sadržajem, najnoviji raspored prvi: pod `%LOCALAPPDATA%\BeamNG\BeamNG.drive` i `%LOCALAPPDATA%\BeamNG.drive`, mapa `current` i mapa najviše numerirane verzije. Iz svake: `mods\*.zip`, svaka mapa u `mods\unpacked`, i sama korisnička mapa ako ima mapu `levels`.

Kasnija dodavanja pobjeđuju, kao u igri, pa mod zamjenjuje ono što nadjača. Modovi su uvijek uključeni u izvoz staze.

Putevi koje razina navodi razrješavaju se kako ih razrješava igra: kako su zadani, zatim relativno u odnosu na datoteku koja ih navodi, a za svaki također kao `.dds` u koji je tekstura pripremljena za igru, kao `.cdae` u koji je `.dae` preveden, ili preko `.link` datoteke koja pokazuje u `/assets`.

## Koja razina {#which-level}

Bez `--level`, svaka se razina boduje prema tome koliko kruga leži na njoj:

- Koristi se do 500 uzoraka kruga, ravnomjerno raspoređenih.
- Za `TerrainBlock` svake razine, raspon terena čita se iz prvih pet bajtova njezine datoteke `.ter`, pa razina na kojoj krug nigdje nije ne košta ništa. Ako je barem 30% uzoraka unutar raspona, čitaju se visine. Uzorak se broji kao **na** terenu kada je između 1 m ispod i 3 m iznad njega (`ON_GROUND`), jer je referentna točka automobila njegovo tijelo, a ne gume.
- Ako nijedna razina ne postigne 50% ili više, razine se boduju i po svojim **cestama**. Neke razine se nastavljaju preko svoje visinske karte (njihovi rubovi se nastavljaju kao stijenski slojevi). Uzorak je na cesti kada leži unutar poluširine ceste plus 4 m (najmanje 6 m) od segmenta `DecalRoad`, i između 2 m ispod i 4 m iznad njega.
- Najbolja razina pobjeđuje ako postigne barem 30%. Inače izvoz staje i navodi tri najbolje: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

Konzola ispisuje `on <level>: 87% of the lap lies on its terrain` (ili `roads`). `--level` se uspoređuje s imenima mapa razina bez obzira na velika i mala slova.

## Čitanje razine {#reading-the-level}

Od čega se razina sastoji, svaki dio provjeren prema isporučenim razinama (pojedinosti u [BeamNG datotekama](reader-beamng.md)):

- **Scena**: `levels\<name>\main\**\*.level.json` (jedan JSON objekt po retku, ili JSON niz), ili datoteka `.mis` za starije razine. Alat čita objekte `TSStatic` (postavljeni modeli, preskačući skrivene), objekte `Prefab` (ugniježđene do 8 razina dubine, TorqueScript `.prefab` ili `.prefab.json`), objekte `DecalRoad` (naslikane ceste), `TerrainBlock`, `WaterPlane`, `WaterBlock` i `River`.
- **Šumske stavke**: `levels\<name>\forest\*.forest4.json`, tipizirane kroz zapise `managedItemData.json`. Barijere, ograde i stijene su šumske stavke jednako često kao što su drveće.
- **Teren**: `.ter` visinsko polje i njegova karta slojeva.
- **Materijali**: svaki `*.materials.json` izvan `levels\`, plus oni ove razine.

## Koridor i dekali cesta {#the-corridor-and-the-road-decals}

Koridor je `--margin` metara oko kruga u BeamNG-ovoj ravnini x/y (vidi [Izvoz staze](course-export.md#the-corridor)). Koridor dosega od `margin + 60 m` bira kandidate.

**Dekali cesta** (`DecalRoad`) su mjesto gdje je većina BeamNG-ovih cesta: naslikani na terenu, ne modelirani. Dekali čiji opseg dodiruje koridor dosega uzimaju se redom crtanja igre (opadajući `renderPriority`, zatim redoslijed datoteke) i slažu se kao vrpce:

- Čvorovi (x, y, z, širina) interpoliraju se **centripetalnom Catmull-Rom** krivuljom otprilike svakih 1 m. Uniformna vrsta se vraća na sebe tamo gdje se čvorovi gomilaju u zavoju. Zatvorene ceste se zatvaraju.
- Svaki rub uzima visinu terena tamo gdje je teren unutar 1.5 m od vlastite visine ceste, a inače zadržava visinu ceste (na mostu).
- Ime materijala određuje što dekal crta:

| Vrsta | Ime materijala se podudara (prvo podudaranje pobjeđuje) |
|---|---|
| tragovi guma | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| preklop (kozmetički) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| oznake | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| rastresito | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| cesta | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| preklop | sve ostalo |

## Tlo {#the-ground}

Visinsko polje terena unutar koridora pretvara se u trokute:

- Jedan četverokut po kvadratu terena čije je središte u koridoru. Kvadrati sa slojem 255 (rupe) preskaču se. Svaki četverokut su dva trokuta, a dijagonala se izmjenjuje kao kod Torqueova terena.
- Visine su `position.z + h * maxHeight / 65535`. Normale dolaze iz razlika visina.
- Svaki kvadrat se razvrstava po svom **sloju**: ime sloja s modelom tla i oznakom materijala terena. Riječi za popločeno čine ga `road`, `grass/forest/rock/moss/leaves/cliff/stone` čine ga `terrain`, a riječi za rastresito čine ga `loose` (šljunak i zemlja). Sve drugo je `terrain`.
- Zatim **dekali cesta i rastresitog** preko-pisuju kvadrate koje pokrivaju, redom crtanja, pa odlučuje posljednji naslikani dekal.
- Vrhovi se dijele po kvadratu od 512 m (`floor(x / 512)`, `floor(y / 512)`), pa se svaki dio preslikava u točno jednu sliku: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konzola ispisuje `what the ground is made of` s brojem trokuta po vrsti.

### Modelirana površina vožnje {#modelled-driving-surface}

BeamNG-ove staze su često modeli, a ne teren. Staza može biti jedna mreža, a njezine linije, gume i rubne trake vlastite mreže iznad nje. Zato se postavljeni modeli u kategorijama road, kerbs, verge, props i bridges pretražuju za površinom vožnje. Po materijalu:

| Površina | Određuje (prvo podudaranje) |
|---|---|
| tragovi guma | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` u imenu, vrsti tla ili oznaci |
| oznake | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` u imenu materijala |
| rubnjaci | `rumble`, `kerb`, `curb` |
| cesta | vrsta tla `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ili ime sadrži `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| rastresito | vrsta tla `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| rub | `sidewalk` |
| (vlastita kategorija modela) | za modele već razvrstane kao road, kerbs ili verge |

Od tih materijala, **gornji** trokuti (normala z iznad 0.5) unutar koridora uzimaju se iz modela i postaju tlo. Boje se u pečenu teksturu pločice i zapisuju kao dijelovi poput `ground:road 3_-2 asphalt_light`. Oznake i tragovi guma se samo naslikaju. Preostali trokuti modela ostaju kod modela. Ti modeli se nikad ne pojednostavljuju niti izostavljaju proračunom, jer je gruba staza pogrešna staza.

## Pečena tekstura tla {#the-baked-ground-texture}

Svaki kvadrat od 512 m koji ima tlo dobiva jednu sliku od `--texture-size` piksela (2048 = 25 cm po pikselu), nacrtanu kako igra crta svoje tlo:

1. **Slojevi terena.** Po pikselu se slojevi četiri okolna kvadrata terena miješaju bilinearno. Svaki sloj je obojen kako ga igra boji: **osnovna karta** materijala razvučena preko `diffuseSize` metara (ili cijelog terena), zatim **detaljne** i **makro** karte kao sivi preklopi (`boja * (1 + jačina * (2 * preklop - 1))`, 0.5 neutralno). Njihove zadane vrijednosti ponavljaju se svakih 2 m i 60 m, s jačinama 0.5 i 0.3, osim ako materijal kaže drugačije. Sloj bez materijala dobiva ravnu boju svoje površine. Redak 0 osnovne karte je sjever.
2. **Dekali cesta** naslikani samo na terenu, redom crtanja, svaki sa svojom teksturom, mapom neprozirnosti, nijansom i neprozirnošću, duž vrpce. Isporučene razine koriste prioritete oko 12-16 za asfaltne podloge, 10 za oznake i 4 za gumu.
3. **Modelirana površina vožnje** gledana odozgo: prvo podloge, zatim preklopi, svaki u vlastitoj ponavljajućoj teksturi modela, s jednim texelom po pikselu pečenja.
4. **Dekali koji se projiciraju i preko predmeta** (`overObjects`), zadnji.

Uz `--no-textures` ništa se ne peče: dijelovi tla dobivaju ravne boje, a modelirane oznake i tragovi guma postaju vlastiti dijelovi, podignuti za **3 cm**.

## Postavljeni modeli {#placed-models}

Kandidati su svaki `TSStatic`, dijete prefaba i šumska stavka čija je ishodišna točka u koridoru dosega. Kandidat se crta ako svjetski ograničavajući okvir njegova oblika dodiruje koridor.

**Kategorija** dolazi iz vlastite oznake razine i iz putanje oblika. Prvo pravilo koje se podudara pobjeđuje:

| Kategorija | Oznaka | Putanja ili ime sadrži |
|---|---|---|
| backdrop (nikad se ne crta) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| kerbs | | `kerb`, `curb`, `rumble` |
| road | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| verge | `SIDEWALK`, `COBBLESTONE` | |
| trees (samo uz `--trees`) | `NATURE` | tree, foliage, bush, grass, plant i slične riječi |
| rocks | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barriers | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| signs | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| bridges | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastructure | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| buildings | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| props | | sve ostalo |

**Oblici** se čitaju iz prevedenog `.cdae`, ili iz Collada `.dae` gdje predmemorija ne postoji (modovi). Oblik koji se ne može pročitati prebroji se: `N copies of M models could not be read`. Materijali imenovani ili teksturirani kao `invisible`, `collision` ili `nodraw` nikad se ne crtaju.

**Teksture.** Modeli se grupiraju po kategoriji i materijalu u dijelove imenovane `structure:<category> <material>` (ili `ground:kerbs <material>`). Grupa dobiva boja teksturu svog materijala do **256 px** samo ako njezine UV koordinate ostaju unutar 0-1 (98% vrhova unutar -0.02 do 1.02). Preglednik slaže teksture u atlas i ne može ponavljati jednu. Grupa čija se tekstura ponavlja crta se prosječnom bojom teksture (ponderiranom alfom, u sRGB, pomnoženom nijansom materijala), ili bojom kategorije ako nema teksture.

**Detalj** slijedi zajedničku shemu na [Razine detalja i proračun](detail-budget.md). BeamNG-ove razine detalja su `details` oblika (najveća veličina piksela prva). Kad je proračun premašen, najdalje kopije odlaze prve. Rubnjaci i modeli koji nose površinu vožnje nikad se ne pojednostavljuju niti izostavljaju.

`--no-placed` izbacuje konstrukcije, ali zadržava modeliranu površinu vožnje. `--trees` dodaje kategoriju drveća.

## Voda {#water}

| Izvor | Crta se kao |
|---|---|
| `WaterPlane` (more) | četverokut od 4 m na visini vode za svaku ćeliju koridora gdje nijedan teren ne dosiže tu visinu |
| `WaterBlock` | jedan četverokut, jedinični kvadrat na lokalnom z = 0 u transformaciji bloka (pa njegova skala određuje veličinu), ako dodiruje koridor; je li z = 0 površina bloka nije provjereno |
| `River` | vrpca kroz njegove čvorove ako dodiruje koridor |

Sva voda je jedan ravni dio, `water:water`.

## Ne crta se {#not-drawn}

- Pokrov tla (proceduralna trava).
- Scenografija postavljena oko ruba svijeta (`backdrop` i slično).
- Ponavljajuće teksture modela, koje ispadaju kao prosječna boja (vidi gore).
- Skinned mreže (vozila, likovi) i mreže dekala unutar oblika.

## Provjere iza toga {#checks-behind-it}

Kako piše u izvoru, izmjereno na isporučenim razinama:

- Čvorovi ceste leže na terenu do 1-2 cm (medijan) na provjerenim razinama, s `h * maxHeight / 65535` i redovima duž +y. `h / 32` ili drugi redoslijed osi promašuju za desetke do stotine metara.
- Dijelovi ograde nanizani uz cestu idu duž retka 0 matrice `rotationMatrix` (velika većina).
- Rotaciju čvora `.cdae` treba transponirati. Tada se svjetski okviri poklapaju s izvornim `.dae` do milimetra. Naivnim pristupom bili bi 38 cm izvan (medijan).
- Izvezeno na više isporučenih razina svake vrste, u sekundama do minuta po razini.
