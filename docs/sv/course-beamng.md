---
title: BeamNG.drive
lang: "sv"
source: course-beamng.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Exportera en bana: BeamNG.drive

BeamNG-exporten läser en nivå så som spelet monterar den, och skriver sedan samma
slags fil som Forza-exporten skriver: mark per 512 m-kvadrat med en inbakad
textur, väg och lös mark som egna delar, placerade modeller efter kategori, och vatten.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Källor: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (installation, filsystem, scen, terräng, material),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (exporten),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) och
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (former).
Filformaten i detalj: [BeamNG-filer](reader-beamng.md).

## Varvets koordinatsystem

Exporten `course` förväntar sig BeamNG-positioner i **visarens koordinatsystem**:
`(x, z, -y)` i BeamNG:s Z-uppåt-värld, i meter. Det är den rotation som
3DHeat-telemetriinspelaren använder. Exporten vrider varvet tillbaka till BeamNG:s
koordinatsystem (`(x, -z, y)`), arbetar där, och skriver sedan ut allt i visarens
koordinatsystem igen. Det här är en rotation, inte en spegling, så ingenting blir
spegelvänt. Ett varv inspelat i BeamNG:s råa koordinatsystem skulle inte placeras
rätt. Detta har inte testats med andra inspelare.

Spelet tas som BeamNG när `heat3d-lap`-filen säger `"game": "beamng"`, eller när du
anger `--game beamng`.

## Att hitta installationen

- `--install <folder>`: mappen som innehåller `gameengine.zip` och `content`.
- Annars kontrolleras varje Steam-bibliotek `steamapps\common\BeamNG.drive` efter
  just dessa två.
- Om ingen av dem fungerar: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Filsystemet

BeamNG levererar vanliga zip-arkiv och monterar dem i ett enda filsystem som nivåer
refererar in i (`/art/shapes/...`, `/assets/materials/...`). Exporten bygger samma sak:
ett skiftlägesokänsligt index över

1. `gameengine.zip`,
2. varje `*.zip` under `content`, utom `content\vehicles\*` och arkiv vars namn
   börjar med `art_sound` eller `audio`,
3. användarens innehåll, nyaste layouten först: under
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` och `%LOCALAPPDATA%\BeamNG.drive`, mappen
   `current` och den högst numrerade versionsmappen. Från var och en: `mods\*.zip`,
   varje mapp i `mods\unpacked`, och användarmappen själv om den har en `levels`-mapp.

Senare tillägg vinner, som i spelet, så en mod ersätter det den åsidosätter. Mods
tas alltid med i en bansexport.

Sökvägar som en nivå anger löses som spelet löser dem: så som de står, sedan i förhål-
lande till filen som angav dem, och för var och en också som den `.dds` en textur
kompilerades till, den `.cdae` en `.dae` kompilerades till, eller via en `.link`-fil
som pekar in i `/assets`.

## Vilken nivå

Utan `--level` poängsätts varje nivå efter hur stor del av varvet som ligger på den:

- Upp till 500 varvsprov, jämnt fördelade, används.
- För varje nivås `TerrainBlock` läses terrängens utsträckning från de första fem
  byten i dess `.ter`-fil, så en nivå som varvet inte är i närheten av kostar ingenting.
  Om minst 30 % av proven ligger inom utsträckningen läses höjderna. Ett prov räknas
  som **på** terrängen när det ligger mellan 1 m under och 3 m över den (`ON_GROUND`),
  eftersom en bils referenspunkt är dess kaross, inte däcken.
- Om ingen nivå når 50 % poängsätts nivåerna också efter sina **vägar**. Vissa nivåer
  går längre än sin höjdkarta (deras kanter fortsätter som bergskivor). Ett prov ligger
  på en väg när det ligger inom vägens halva bredd plus 4 m (minst 6 m) från ett
  `DecalRoad`-segment, och mellan 2 m under och 4 m över den.
- Den bästa nivån vinner om den får minst 30 %. Annars avbryts exporten och listar de
  tre bästa: "the lap does not lie on any installed level's terrain (best: ...). Name
  the level with --level."

Konsolen skriver `on <level>: 87% of the lap lies on its terrain` (eller `roads`).
`--level` matchas utan hänsyn till skiftläge mot nivåmapparnas namn.

## Att läsa nivån

Vad en nivå består av, var del kontrollerad mot de levererade nivåerna (detaljer i
[BeamNG-filer](reader-beamng.md)):

- **Scen**: `levels\<name>\main\**\*.level.json` (ett JSON-objekt per rad, eller en
  JSON-array), eller en `.mis`-fil för äldre nivåer. Verktyget läser `TSStatic`-objekt
  (placerade modeller, de dolda hoppas över), `Prefab`-objekt (kapslade upp till 8
  nivåer djupt, TorqueScript `.prefab` eller `.prefab.json`), `DecalRoad`-objekt
  (målade vägar), `TerrainBlock`, `WaterPlane`, `WaterBlock` och `River`.
- **Skogsobjekt**: `levels\<name>\forest\*.forest4.json`, typade via posterna i
  `managedItemData.json`. Räcken, staket och stenar är skogsobjekt lika ofta som träd är det.
- **Terräng**: höjdfältet i `.ter` och dess lagerkarta.
- **Material**: varje `*.materials.json` utanför `levels\`, plus de för den här nivån.

## Korridoren och vägdekalerna

Korridoren är `--margin` meter runt varvet i BeamNG:s x/y-plan (se
[Exportera en bana](course-export.md#the-corridor)). En räckviddskorridor på
`margin + 60 m` väljer kandidaterna.

**Vägdekaler** (`DecalRoad`) är där de flesta av BeamNG:s vägar finns: målade på
terrängen, inte modellerade. Dekaler vars utsträckning rör räckviddskorridoren tas i
spelets ritordning (fallande `renderPriority`, sedan filordning), och läggs ut som
band:

- Noderna (x, y, z, bredd) interpoleras med en **centripetal Catmull-Rom**-spline ungefär
  var 1 m. Den likformiga varianten viker tillbaka på sig själv där noderna hopar sig
  i en hårnålskurva. Slingade vägar sluts.
- Varje kant tar terrängens höjd där terrängen ligger inom 1,5 m från vägens egen höjd,
  och behåller vägens höjd annars (på en bro).
- Materialnamnet avgör vad en dekal målar:

| Slag | Materialnamnet matchar (första träff gäller) |
|---|---|
| däckspår | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| överlägg (kosmetiskt) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| markeringar | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| lös | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| väg | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| överlägg | allt annat |

## Marken

Terrängens höjdfält inom korridoren blir trianglar:

- En fyrhörning per terrängruta vars mittpunkt ligger i korridoren. Rutor med lager 255
  (hål) hoppas över. Varje fyrhörning är två trianglar, med diagonalen växlande som
  Torques terräng gör.
- Höjderna är `position.z + h * maxHeight / 65535`. Normalerna kommer från höjdskillnaderna.
- Varje ruta klassas efter sitt **lager**: lagernamnet med dess terrängmaterials
  markmodell och anteckning. Ord för stenlagt gör den till `road`, `grass/forest/rock/moss/leaves/cliff/stone`
  gör den till `terrain`, och lösa ord gör den till `loose` (grus och jord). Annat blir
  `terrain`.
- Sedan **överskriver väg- och lösa dekaler** de rutor de täcker, i ritordning, så den
  sista målade dekalen avgör.
- Hörn delas per 512 m-kvadrat (`floor(x / 512)`, `floor(y / 512)`), så varje del
  avbildas i exakt en bild: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konsolen skriver `what the ground is made of` med antal trianglar per slag.

### Modellerad körbana

BeamNG:s banor är lika ofta modeller som terräng. En bana kan vara en mesh med sina
linjer, däck och vibrationsremsor som egna meshar ovanpå. Därför letas det i placerade
modeller i kategorierna road, kerbs, verge, props och bridges efter körbana. Per material:

| Yta | Avgörs av (första träff) |
|---|---|
| däckspår | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` i namn, markslag eller anteckning |
| markeringar | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` i materialnamnet |
| kantstenar | `rumble`, `kerb`, `curb` |
| väg | markslag `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, eller namnet innehåller `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| lös | markslag `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| vall | `sidewalk` |
| (modellens egen kategori) | för modeller som redan är klassade som väg, kantstenar eller vall |

Av de materialen tas de **uppåtvända** trianglarna (normal z över 0,5) inom korridoren
ut ur modellen och blir mark. De målas in i kakelns inbakade textur och skrivs som delar
som `ground:road 3_-2 asphalt_light`. Markeringar och däckspår målas bara. Modellens
återstående trianglar stannar hos modellen. Dessa modeller förenklas eller utelämnas
aldrig av budgeten, för en grov bana är en fel bana.

## Den inbakade marktexturen

Varje 512 m-kvadrat som har mark får en bild på `--texture-size` pixlar (2048 = 25 cm per
pixel), ritad så som spelet ritar sin mark:

1. **Terränglager.** Per pixel blandas de fyra omgivande terrängrutornas lager
   bilinjärt. Varje lager färgas så som spelet färgar det: materialets **basbild** sträckt
   över `diffuseSize` meter (eller hela terrängen), sedan **detalj-** och **makrobilderna**
   som grå överlägg (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutralt). Deras
   standardvärden upprepas var 2 m och var 60 m, med styrkor 0,5 och 0,3, om inte
   materialet säger annat. Ett lager utan material får sin ytas platta färg. Basbildens
   rad 0 är norr.
2. **Vägdekaler** som bara är målade på terrängen, i ritordning, var och en med sin egen
   textur, opacitetskarta, nyans och opacitet, längs bandet. Levererade nivåer använder
   prioriteter kring 12-16 för asfaltsbaser, 10 för markeringar och 4 för gummi.
3. **Modellerad körbana sedd uppifrån**: baser först, sedan överlägg, var och en i modellens
   egen upprepande textur med en texel per bakpixel.
4. **Dekaler som projiceras över objekt också** (`overObjects`), sist.

Med `--no-textures` bakas inget: markdelar får platta färger, och de modellerade
markeringarna och däckspåren blir egna delar, lyfta **3 cm**.

## Placerade modeller

Kandidater är varje `TSStatic`, prefab-barn och skogsobjekt vars ursprung ligger i
räckviddskorridoren. En kandidat ritas om dess modells världsbegränsningslåda rör korridoren.

**Kategorin** kommer från nivåns egen annotation och modellens sökväg. Första regel som
matchar gäller:

| Kategori | Annotation | Sökväg eller namn innehåller |
|---|---|---|
| bakgrund (ritas aldrig) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| kantstenar | | `kerb`, `curb`, `rumble` |
| väg | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| vall | `SIDEWALK`, `COBBLESTONE` | |
| träd (bara med `--trees`) | `NATURE` | tree, foliage, bush, grass, plant och liknande ord |
| stenar | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| räcken | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| skyltar | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| broar | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktur | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| byggnader | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekvisita | | allt annat |

**Former** läses från den kompilerade `.cdae`, eller från Collada-filen `.dae` där ingen
cache finns (mods). En form som inte kan läsas räknas: `N copies of M models could not be
read`. Material som heter eller har en textur `invisible`, `collision` eller `nodraw` ritas aldrig.

**Texturer.** Modeller grupperas per kategori och material i delar som heter
`structure:<category> <material>` (eller `ground:kerbs <material>`). En grupp får sitt
materials färgtextur i högst **256 px** bara om dess UV:er ligger inom 0-1 (98 % av
hörnen inom -0,02 till 1,02). Visaren packar texturer i en atlas och kan inte upprepa
en textur. En grupp vars textur upprepas ritas i texturens medelfärg (alfaviktad, i sRGB,
gånger materialets nyans), eller i kategorins färg om den saknar textur.

**Detalj** följer det gemensamma schemat i [Detaljnivåer och budgeten](detail-budget.md).
BeamNG:s detaljnivåer är formens `details` (största pixelstorlek först). Över budgeten
går de avlägsnaste kopiorna först. Kantstenar och modeller som bär körbana förenklas
eller utelämnas aldrig.

`--no-placed` tar bort strukturerna men behåller modellerad körbana. `--trees` lägger till
kategorin träd.

## Vatten

| Källa | Ritas som |
|---|---|
| `WaterPlane` (havet) | en fyrhörning på 4 m på vattenhöjden för varje korridorruta där ingen terräng når upp till den höjden |
| `WaterBlock` | en fyrhörning, enhetskvadraten vid lokal z = 0 i blockets transform (så dess skala sätter storleken), om den rör korridoren; om z = 0 är blockets yta är ännu inte verifierat |
| `River` | ett band genom dess noder om det rör korridoren |

Allt vatten är en platt del, `water:water`.

## Ritas inte

- Markbeväxning (procedurellt gräs).
- Scenerier placerade runt världens kant (`backdrop` och liknande).
- Upprepande modelltexturer, som blir en medelfärg (se ovan).
- Skinnade meshar (fordon, figurer) och dekalmeshar inuti former.

## Kontroller bakom det

Så som sagt i källkoden, uppmätt på de levererade nivåerna:

- Vägnoder ligger på terrängen inom 1-2 cm (median) på de nivåer som kontrollerats, med
  `h * maxHeight / 65535` och rader längs +y. `h / 32` eller den andra axelordningen
  missar med tiotals till hundratals meter.
- Skenlängder som kedjas längs en väg löper längs `rotationMatrix` rad 0 (den stora majoriteten).
- `.cdae`-nodens rotation måste transponeras. Med det stämmer världsbegränsningarna mot
  källans `.dae` till millimetern. Den läroboksmässiga metoden hamnar 38 cm fel (median).
- Exporterat på flera levererade nivåer av alla slag, på sekunder till minuter var.
