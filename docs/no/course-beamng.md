---
title: BeamNG.drive
lang: "no"
source: course-beamng.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Banueksport: BeamNG.drive

BeamNG-eksporten leser et nivå slik spillet monterer det, og skriver deretter samme
slags fil som Forza-eksporten skriver: bakke per 512 m firkant med en innbakt tekstur,
vei og løs bakke som egne deler, plasserte modeller etter kategori, og vann.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Kilder: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (installasjon, filsystem, scene, terreng, materialer),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (eksporten),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) og
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (former).
Filformatene i detalj: [BeamNG-filer](reader-beamng.md).

## Lapets koordinatsystem

`course`-eksporten forventer at BeamNG-posisjonene er i **visningens koordinatsystem**:
`(x, z, -y)` av BeamNGs Z-opp-verden, i meter. Det er rotasjonen opptakeren for 3DHeat-
telemetrien bruker. Eksporten snur lapet tilbake til BeamNGs koordinatsystem
(`(x, -z, y)`), arbeider der, og skriver alt ut i visningens koordinatsystem igjen.
Dette er en rotasjon, ikke en speiling, så ingenting kommer ut speilvendt. Et lap som er
tatt opp i BeamNGs rå koordinatsystem ville ikke blitt plassert riktig. Dette er ikke
testet med andre opptakere.

Spillet regnes som BeamNG når `heat3d-lap`-filen sier `"game": "beamng"`, eller når du
gir `--game beamng`.

## Finne installasjonen

- `--install <folder>`: mappen som har `gameengine.zip` og `content`.
- Ellers sjekkes hvert Steam-biblioteks `steamapps\common\BeamNG.drive` for de to.
- Hvis ingenting av dette fungerer: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Filsystemet

BeamNG leverer vanlige zip-arkiver og monterer dem i ett filsystem som nivåene peker
inn i (`/art/shapes/...`, `/assets/materials/...`). Eksporten bygger det samme: ett
store- og småbokstav-uavhengig register over

1. `gameengine.zip`,
2. hver `*.zip` under `content`, unntatt `content\vehicles\*` og arkiver hvis navn
   begynner med `art_sound` eller `audio`,
3. brukerens innhold, nyeste oppsett først: under
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` og `%LOCALAPPDATA%\BeamNG.drive`, mappen
   `current` og den høyest nummererte versjonsmappen. Fra hver: `mods\*.zip`, hver
   mappe i `mods\unpacked`, og selve brukermappen hvis den har en `levels`-mappe.

Senere tillegg vinner, som i spillet, så en mod erstatter det den overstyrer. Mods tas
alltid med i en banueksport.

Stier et nivå nevner, løses slik spillet løser dem: slik de står, deretter i forhold til
filen som nevnte dem, og for hver også som `.dds` teksturen ble komprimert til, `.cdae`
en `.dae` ble kompilert til, eller via en `.link`-fil som peker inn i `/assets`.

## Hvilket nivå

Uten `--level` får hvert nivå poeng etter hvor mye av lapet som ligger på det:

- Opptil 500 lap-punkter, jevnt fordelt, brukes.
- For hvert nivås `TerrainBlock` leses terrengets utstrekning fra de fem første bytene i
  `.ter`-filen, så et nivå lapet ikke er i nærheten av koster ingenting. Hvis minst 30 %
  av punktene ligger innenfor utstrekningen, leses høydene. Et punkt regnes som **på**
  terrenget når det er mellom 1 m under og 3 m over det (`ON_GROUND`), fordi et bils
  referansepunkt er karosseriet, ikke dekkene.
- Hvis intet nivå får 50 % eller mer, får nivåene også poeng for sine **veier**. Noen
  nivåer går videre enn høydekartet sitt (kantene fortsetter som fjellplater). Et punkt
  er på en vei når det ligger innenfor veiens halve bredde pluss 4 m (minst 6 m) fra et
  `DecalRoad`-segment, og mellom 2 m under og 4 m over det.
- Det beste nivået vinner hvis det får minst 30 %. Ellers stopper eksporten og lister de
  beste tre: "the lap does not lie on any installed level's terrain (best: ...). Name the
  level with --level."

Konsollen skriver `on <level>: 87% of the lap lies on its terrain` (eller `roads`).
`--level` sammenlignes uten forskjell på store og små bokstaver med nivåmappenavnene.

## Lese nivået

Hva et nivå består av, hver del sjekket mot de leverte nivåene (detaljer i
[BeamNG-filer](reader-beamng.md)):

- **Scene**: `levels\<name>\main\**\*.level.json` (ett JSON-objekt per linje, eller en
  JSON-matrise), eller en `.mis`-fil for eldre nivåer. Verktøyet leser `TSStatic`-objekter
  (plasserte modeller, hopper over skjulte), `Prefab`-objekter (nestet opptil 8 nivåer
  dypt, TorqueScript `.prefab` eller `.prefab.json`), `DecalRoad`-objekter (malte veier),
  `TerrainBlock`, `WaterPlane`, `WaterBlock` og `River`.
- **Skogsobjekter**: `levels\<name>\forest\*.forest4.json`, typet gjennom
  `managedItemData.json`-postene. Barrierer, gjerder og steiner er skogsobjekter like ofte
  som trær er det.
- **Terreng**: `.ter`-høyde­feltet og dets lagkart.
- **Materialer**: hver `*.materials.json` utenfor `levels\`, pluss de til dette nivået.

## Korridoren og veidekalene

Korridoren er `--margin` meter rundt lapet i BeamNGs x/y-plan (se
[Banueksport](course-export.md#the-corridor)). En rekkeviddekorridor på `margin + 60 m`
velger kandidatene.

**Veidekaler** (`DecalRoad`) er der de fleste av BeamNGs veier er: malt på terrenget,
ikke modellert. Dekaler hvis utstrekning rører rekkeviddekorridoren tas i spillets
tegnerekkefølge (synkende `renderPriority`, deretter filrekkefølge), og legges ut som
bånd:

- Nodene (x, y, z, bredde) interpoleres med en **sentripetal Catmull-Rom**-spline omtrent
  hver 1 m. Den uniforme typen går i ring der nodene samler seg i en hårnål. Lukkede veier
  lukkes.
- Hver kant tar terrengets høyde der terrenget er innenfor 1,5 m av veiens egen høyde, og
  beholder veiens høyde ellers (på en bro).
- Materialnavnet avgjør hva et dekal maler:

| Type | Materialnavnet inneholder (første treff vinner) |
|---|---|
| dekkmerker | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| overlegg (kosmetisk) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| merkinger | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| løs | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| vei | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| overlegg | alt annet |

## Bakken

Terrengets høyde­felt innenfor korridoren blir til trekanter:

- Én firkant per terrengfirkant hvis senter er i korridoren. Firkanter med lag 255 (hull)
  hoppes over. Hver firkant er to trekanter, med diagonalen vekslende slik Torques terreng
  gjør.
- Høydene er `position.z + h * maxHeight / 65535`. Normalene kommer fra høydeforskjellene.
- Hver firkant klassifiseres etter sitt **lag**: lagnavnet med terrengmaterialets
  bakkemodell og merknad. Asfalt-ord gjør den til `road`,
  `grass/forest/rock/moss/leaves/cliff/stone` gjør den til `terrain`, og løse ord gjør den
  til `loose` (grus og jord). Alt annet er `terrain`.
- Deretter **overstyrer vei- og løsedekaler** firkantene de dekker, i tegnerekkefølge, så
  det siste dekalet som ble malt, bestemmer.
- Hjørnepunktene deles per 512 m firkant (`floor(x / 512)`, `floor(y / 512)`), så hver del
  havner i nøyaktig ett bilde: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konsollen skriver `what the ground is made of` med antall trekanter per type.

### Modellert kjørebane

BeamNGs baner er like ofte modeller som terreng. En racerbane kan ha banen som ett mesh,
med linjene, dekkmerkene og rumble strips som egne meshes oppå. Derfor søkes plasserte
modeller i kategoriene vei, kanter, skulder, rekvisitter og broer etter kjørebane. Per
materiale:

| Overflate | Avgjort av (første treff) |
|---|---|
| dekkmerker | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` i navn, bakkemodell eller merknad |
| merkinger | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` i materialnavnet |
| kanter | `rumble`, `kerb`, `curb` |
| vei | bakkemodell `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, eller navnet inneholder `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| løs | bakkemodell `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| skulder | `sidewalk` |
| (modellens egen kategori) | for modeller som allerede er klassifisert som vei, kanter eller skulder |

Av disse materialene tas **oppoverrettede** trekanter (normal z over 0,5) innenfor
korridoren ut av modellen og blir til bakke. De males inn i flisens innbakte tekstur og
skrives som deler, for eksempel `ground:road 3_-2 asphalt_light`. Merkinger og dekkmerker
males bare. Modellens øvrige trekanter blir værende i modellen. Disse modellene blir
aldri forenklet eller utelatt av budsjettet, fordi en grov bane er en feil bane.

## Den innbakte bakketeksturen

Hver 512 m firkant som har bakke får ett bilde på `--texture-size` piksler (2048 =
25 cm per piksel), tegnet slik spillet tegner sin bakke:

1. **Terrenglag.** Per piksel blandes lagene til de fire omkringliggende terrengfirkantene
   bilineært. Hvert lag farges slik spillet farger det: materialets **grunnkart** strukket
   over `diffuseSize` meter (eller hele terrenget), deretter **detalj**- og
   **makrokartene** som gråtoneoverlegg (`colour * (1 + strength * (2 * overlay - 1))`,
   0,5 nøytral). Standardene gjentar hver 2 m og 60 m, med styrke 0,5 og 0,3, med mindre
   materialet sier noe annet. Et lag uten materiale får overflatens flate farge. Rad 0 i
   grunnkartet er nord.
2. **Veidekaler som bare males på terrenget**, i tegnerekkefølge, hver med sin egen tekstur,
   deknings­kart, toning og opasitet, langs båndet. Leverte nivåer bruker prioriteringer
   rundt 12-16 for asfaltbaser, 10 for merkinger og 4 for dekkmerker.
3. **Modellert kjørebane sett ovenfra**: baser først, deretter overlegg, hver i modellens
   egen gjentakende tekstur med én texel per bake-piksel.
4. **Dekaler som også projiseres over objekter** (`overObjects`), sist.

Med `--no-textures` bakes ingenting: bakkedeler får flate farger, og de modellerte
merkingene og dekkmerkene blir egne deler, løftet **3 cm**.

## Plasserte modeller

Kandidater er hver `TSStatic`, prefab-barn og skogsobjekt hvis origo ligger i
rekkeviddekorridoren. En kandidat tegnes hvis formens verdensboks berører korridoren.

**Kategori** kommer fra nivåets egen merknad og fra formens sti. Den første regelen som
passer, vinner:

| Kategori | Merknad | Sti eller navn inneholder |
|---|---|---|
| bakgrunn (tegnes aldri) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| kanter | | `kerb`, `curb`, `rumble` |
| vei | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| skulder | `SIDEWALK`, `COBBLESTONE` | |
| trær (bare med `--trees`) | `NATURE` | tree, foliage, bush, grass, plant og lignende ord |
| steiner | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barrierer | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| skilt | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| broer | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktur | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| bygninger | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekvisitter | | alt annet |

**Former** leses fra den kompilerte `.cdae`, eller fra Collada-`.dae` der ingen cache finnes
(mods). En form som ikke kan leses, telles: `N copies of M models could not be read`.
Materialer som heter eller har tekstur `invisible`, `collision` eller `nodraw`, tegnes aldri.

**Teksturer.** Modeller grupperes per kategori og materiale i deler som heter
`structure:<category> <material>` (eller `ground:kerbs <material>`). En gruppe får sin
materialets fargetekstur på opptil **256 piksler** bare hvis UV-koordinatene blir innenfor
0-1 (98 % av hjørnepunktene innenfor -0,02 til 1,02). Visningen pakker teksturer i et atlas
og kan ikke gjenta en. En gruppe hvis tekstur gjentas, tegnes i teksturens gjennomsnittsfarge
(alfavektet, i sRGB, ganget med materialets toning), eller i kategoriens farge hvis den
ikke har tekstur.

**Detalj** følger den felles ordningen i [Detaljnivåer og budsjett](detail-budget.md).
BeamNGs detaljnivåer er formens `details` (største pikselstørrelse først). Over budsjett
går de fjerneste kopiene først. Kanter og modeller som bærer kjørebane blir aldri
forenklet eller utelatt.

`--no-placed` dropper strukturene, men beholder fortsatt modellert kjørebane. `--trees`
legger til trærkategorien.

## Vann

| Kilde | Tegnes som |
|---|---|
| `WaterPlane` (havet) | en 4 m firkant på vannhøyden for hver banecelle der ingenting av terrenget når den høyden |
| `WaterBlock` | én firkant, enhetskvadraten ved lokal z = 0 i blokkens transformasjon (så skalaen bestemmer størrelsen), hvis den berører korridoren; om z = 0 er blokkens overflate er ikke verifisert |
| `River` | et bånd gjennom nodene, hvis det berører korridoren |

Alt vann er én flat del, `water:water`.

## Tegnes ikke

- Bakkedekke (prosedyrisk gress).
- Scenerier plassert i kanten av verden (`backdrop` og lignende).
- Gjentakende modellteksturer, som blir til en gjennomsnittsfarge (se over).
- Skinnede meshes (kjøretøy, figurer) og dekal-meshes inne i former.

## Kontroller bak dette

Slik kildekoden sier, målt på de leverte nivåene:

- Veinoder ligger på terrenget innen 1-2 cm (median) på de nivåene som ble sjekket, med
  `h * maxHeight / 65535` og rader langs +y. `h / 32` eller den andre aksen bommer med titalls til
  hundrevis av meter.
- Skinnseksjoner som er kjedet sammen langs en vei, går langs `rotationMatrix`-rad 0 (det
  store flertallet).
- Rotasjonen for `.cdae`-noden må transponeres. Med det stemmer verdensgrensene med kilde-
  `.dae` til millimeteren. Den lærebokaktige metoden er 38 cm feil (median).
- Eksportert på flere leverte nivåer av alle slag, på sekunder til minutter hver.
