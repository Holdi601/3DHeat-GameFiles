---
title: "BeamNG.drive"
nav_order: 2
lang: "da"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Eksport af baner: BeamNG.drive {#course-export-beamngdrive}

BeamNG-eksporten læser en bane, som spillet monterer den, og skriver samme slags fil som Forza-eksporten skriver: jord i 512 m kvadrater med en færdigbagt tekstur, vej og løs jord som egne dele, placerede modeller efter kategori, og vand.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Kilder: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (installation, filsystem, scene, terræn, materialer),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (eksporten),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) og
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (shapes).
Filformaterne i detaljer: [BeamNG-filer](reader-beamng.md).

## Omgangens koordinatsystem {#the-laps-frame}

`course`-eksporten forventer BeamNG-positioner i **viewerens koordinatsystem**:
`(x, z, -y)` af BeamNGs Z-op-verden, i meter. Det er den rotation 3DHeats telemetrioptager anvender. Eksporten drejer omgangen tilbage til BeamNGs koordinatsystem (`(x, -z, y)`), arbejder der og skriver alt ud igen i viewerens koordinatsystem. Det er en rotation, ikke en spejling, så intet bliver spejlvendt. En omgang optaget i BeamNGs rå koordinatsystem ville ikke blive placeret rigtigt. Det er ikke testet med andre optagere.

Spillet tages som BeamNG, når `heat3d-lap`-filen siger `"game": "beamng"`, eller når du giver `--game beamng`.

## Finde installationen {#finding-the-install}

- `--install <folder>`: mappen der holder `gameengine.zip` og `content`.
- Ellers tjekkes hvert Steam-biblioteks `steamapps\common\BeamNG.drive` for de to.
- Hvis ingen af delene virker: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)."

## Filsystemet {#the-file-system}

BeamNG leverer almindelige zip-arkiver og monterer dem i ét filsystem, som baner henviser til (`/art/shapes/...`, `/assets/materials/...`). Eksporten bygger det samme: ét indeks uden forskel på store og små bogstaver over

1. `gameengine.zip`,
2. hver `*.zip` under `content`, undtagen `content\vehicles\*` og arkiver hvis navne begynder med `art_sound` eller `audio`,
3. brugerens indhold, nyeste layout først: under
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` og `%LOCALAPPDATA%\BeamNG.drive`, mappen `current` og den højest nummererede versionsmappe. Fra hver: `mods\*.zip`, hver mappe i `mods\unpacked`, og selve brugermappen hvis den har en `levels`-mappe.

Senere tilføjelser vinder, som i spillet, så en mod erstatter det den overskriver. Mods er altid med i en eksport af en bane.

Stier en bane nævner, løses på samme måde som spillet løser dem: som de står, derefter i forhold til filen der nævnte dem, og for hver også som den `.dds` en tekstur blev bagt til, den `.cdae` en `.dae` blev kompileret til, eller gennem en `.link`-fil der peger ind i `/assets`.

## Hvilken bane {#which-level}

Uden `--level` scores hver bane efter, hvor meget af omgangen der ligger på den:

- Op til 500 omgangssamples, jævnt fordelt, bruges.
- For hver banes `TerrainBlock` læses terrænets udstrækning ud fra de første fem bytes i dens `.ter`-fil, så en bane omgangen er langt fra koster intet. Hvis mindst 30 % af samplene ligger inde i udstrækningen, læses højderne. Et sample tæller som **på** terrænet når det ligger mellem 1 m under og 3 m over det (`ON_GROUND`), fordi en bils referencepunkt er karrosseriet, ikke dækkene.
- Hvis ingen bane scorer 50 % eller mere, scores banerne også på deres **veje**. Nogle baner fortsætter ud over deres højdekort (deres kanter fortsætter som klippeplader). Et sample er på en vej når det ligger inden for vejens halve bredde plus 4 m (mindst 6 m) fra et `DecalRoad`-segment, og mellem 2 m under og 4 m over det.
- Den bedste bane vinder, hvis den scorer mindst 30 %. Ellers stopper eksporten og lister de bedste tre: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

Konsollen skriver `on <level>: 87% of the lap lies on its terrain` (eller `roads`). `--level` matches uden forskel på store og små bogstaver mod banemappenavnene.

## Læse banen {#reading-the-level}

Hvad en bane består af, hver del kontrolleret mod de udgivne baner (detaljer i [BeamNG-filer](reader-beamng.md)):

- **Scene**: `levels\<name>\main\**\*.level.json` (ét JSON-objekt pr. linje, eller et JSON-array), eller en `.mis`-fil til ældre baner. Værktøjet læser `TSStatic`-objekter (placerede modeller, skjulte springes over), `Prefab`-objekter (indlejret op til 8 niveauer dybt, TorqueScript `.prefab` eller `.prefab.json`), `DecalRoad`-objekter (malede veje), `TerrainBlock`, `WaterPlane`, `WaterBlock` og `River`.
- **Skovobjekter**: `levels\<name>\forest\*.forest4.json`, typet gennem posterne i `managedItemData.json`. Barrierer, hegn og klipper er lige så ofte skovobjekter som træer er.
- **Terræn**: `.ter`-højdefeltet og dets lagkort.
- **Materialer**: alle `*.materials.json` uden for `levels\`, plus dem for denne bane.

## Korridoren og vejdekalerne {#the-corridor-and-the-road-decals}

Korridoren er `--margin` meter omkring omgangen i BeamNGs x/y-plan (se [Eksport af baner](course-export.md#the-corridor)). En søgekorridor på `margin + 60 m` udvælger kandidaterne.

**Vejdekaler** (`DecalRoad`) er hvor de fleste af BeamNGs veje er: malet på terrænet, ikke modelleret. Dekaler hvis udstrækning rører søgekorridoren tages i spillets tegnerækkefølge (faldende `renderPriority`, derefter filrækkefølge) og lægges ud som bånd:

- Noderne (x, y, z, bredde) interpoleres med en **centripetal Catmull-Rom**-spline ca. hver 1 m. Den uniforme type løber tilbage på sig selv, hvor noder samler sig i en hårnålesving. Lukkede veje lukkes.
- Hver kant tager terrænets højde hvor terrænet ligger inden for 1,5 m af vejens egen højde, og beholder vejens højde ellers (på en bro).
- Materialenavnet afgør hvad en dekal maler:

| Type | Materialenavn matcher (første match vinder) |
|---|---|
| däkspor | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| overlay (kosmetisk) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| markeringer | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| løs | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| vej | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| overlay | alt andet |

## Jorden {#the-ground}

Terrænets højdefelt inden for korridoren bliver til trekanter:

- Én quad pr. terrænkvadrat hvis centrum er i korridoren. Kvadrater med lag 255 (huller) springes over. Hver quad er to trekanter, med diagonalen skiftende som Torques terræn gør det.
- Højder er `position.z + h * maxHeight / 65535`. Normaler kommer fra højdeforskellene.
- Hvert kvadrat klassificeres efter sit **lag**: lagnavnet med dets terrainmaterials jordmodel og annotation. Ord for belagt gør det til `road`, `grass/forest/rock/moss/leaves/cliff/stone` gør det til `terrain`, og løse ord gør det til `loose` (grus og jord). Alt andet er `terrain`.
- Derefter **overskriver vej- og løse dekaler** de kvadrater de dækker, i tegnerækkefølge, så den sidste dekal der males, bestemmer.
- Vertices deles pr. 512 m kvadrat (`floor(x / 512)`, `floor(y / 512)`), så hver del afbildes i præcis ét billede: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konsollen udskriver `what the ground is made of` med trekanttællinger pr. type.

### Modelleret kørselsflade {#modelled-driving-surface}

BeamNGs baner er lige så ofte modeller som terræn. En racerbanes bane kan være ét mesh med dens linjer, gummi og rumble strips som egne meshes ovenpå. Så placerede modeller i kategorierne vej, kantsten, kant og rekvisitter og broer søges for kørselsflade. Pr. materiale:

| Flade | Afgjort af (første match) |
|---|---|
| däkspor | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` i navn, jordtype eller annotation |
| markeringer | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` i materialenavnet |
| kantsten | `rumble`, `kerb`, `curb` |
| vej | jordtype `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, eller navnet indeholder `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| løs | jordtype `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| kant | `sidewalk` |
| (modellens egen kategori) | for modeller allerede klassificeret som vej, kantsten eller kant |

Af disse materialer tages de **opadvendte** trekanter (normal z over 0,5) inden for korridoren ud af modellen og bliver til jord. De males ind i flisens færdigbagte tekstur og skrives som dele som `ground:road 3_-2 asphalt_light`. Markeringer og däkspor males kun. Modellens øvrige trekanter bliver hos modellen. Disse modeller forenkles eller udelades aldrig af budgettet, for en grov bane er en forkert bane.

## Den færdigbagte jordtekstur {#the-baked-ground-texture}

Hvert 512 m kvadrat der har jord, får ét billede på `--texture-size` pixels (2048 = 25 cm pr. pixel), tegnet som spillet tegner sin jord:

1. **Terrænlag.** Pr. pixel blandes lagene for de fire omkringliggende terrænkvadrater bilinært. Hvert lag farves som spillet farver det: materialets **basismap** strakt over `diffuseSize` meter (eller hele terrænet), derefter **detalje**- og **makro**-mapperne som grå overlejringer (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutral). Deres standarder gentages hver 2 m og 60 m, med styrker på 0,5 og 0,3, medmindre materialet siger andet. Et lag uden materiale får sin overflades flade farve. Basismapets række 0 er nord.
2. **Vejdekaler** der kun males på terrænet, i tegnerækkefølge, hver med sin egen tekstur, opacitetsmap, tint og opacitet, langs båndet. Udgivne baner bruger prioriteter omkring 12-16 for asfaltbaser, 10 for markeringer og 4 for gummi.
3. **Modelleret kørselsflade set oppefra**: baser først, derefter overlays, hver i modellens egen gentagende tekstur med én texel pr. bagepixel.
4. **Dekaler der også projiceres over objekter** (`overObjects`), til sidst.

Med `--no-textures` bages intet: jorddele får flade farver, og de modellerede markeringer og däkspor bliver egne dele, løftet **3 cm**.

## Placed models {#placed-models}

Kandidater er hvert `TSStatic`, prefab-barn og skovobjekt hvis origin ligger i søgekorridoren. En kandidat tegnes, hvis dens figurs verdens-bounding-box rører korridoren.

**Kategori** kommer fra banens egen annotation og figurens sti. Den første regel der matcher, vinder:

| Kategori | Annotation | Sti eller navn indeholder |
|---|---|---|
| baggrund (tegnes aldrig) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| kantsten | | `kerb`, `curb`, `rumble` |
| vej | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| kant | `SIDEWALK`, `COBBLESTONE` | |
| træer (kun med `--trees`) | `NATURE` | tree, foliage, bush, grass, plant og lignende ord |
| klipper | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barrierer | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| skilte | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| broer | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktur | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| bygninger | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekvisitter | | alt andet |

**Shapes** læses fra den kompilerede `.cdae`, eller fra Collada-`.dae` hvor der ikke findes en cache (mods). En shape der ikke kan læses, tælles: `N copies of M models could not be read`. Materialer der hedder eller har teksturen `invisible`, `collision` eller `nodraw`, tegnes aldrig.

**Teksturer.** Modeller grupperes pr. kategori og materiale i dele med navnene `structure:<category> <material>` (eller `ground:kerbs <material>`). En gruppe får sit materiales farvetekstur i op til **256 px** kun hvis dens UV'er bliver inden for 0-1 (98 % af vertices inden for -0,02 til 1,02). Viewerens atlas pakker teksturer og kan ikke gentage en. En gruppe hvis tekstur gentages, tegnes i teksturens gennemsnitsfarve (alfavægtet, i sRGB, ganget med materialets tint), eller i kategoriens farve hvis den ikke har en tekstur.

**Detalje** følger det fælles skema i [Detaljeniveauer og budgettet](detail-budget.md). BeamNGs detaljeniveauer er shapens `details` (største pixelstørrelse først). Over budgettet går de fjerneste kopier først. Kantsten og modeller med kørselsflade forenkles eller udelades aldrig.

`--no-placed` fjerner strukturerne, men beholder stadig modelleret kørselsflade. `--trees` tilføjer kategorien træer.

## Vand {#water}

| Kilde | Tegnes som |
|---|---|
| `WaterPlane` (havet) | en 4 m quad i vandhøjde for hver korridorcelle hvor intet terræn når den højde |
| `WaterBlock` | én quad, enhedskvadratet ved lokal z = 0 i blokkens transform (så dens skala sætter størrelsen), hvis den rører korridoren; om z = 0 er blokkens overflade er ikke verificeret |
| `River` | et bånd gennem dens noder, hvis det rører korridoren |

Alt vand er én flad del, `water:water`.

## Tegnes ikke {#not-drawn}

- Jorddække (procedural græs).
- Scenografi placeret i kanten af verden (`backdrop` og lignende).
- Gentagende modeltekstureer, som bliver til en gennemsnitsfarve (se ovenfor).
- Skinnede meshes (køretøjer, figurer) og dekalmeshes inde i shapes.

## Kontroller bag det {#checks-behind-it}

Som angivet i kilden, målt på de udgivne baner:

- Vejnoder ligger på terrænet inden for 1-2 cm (median) på de kontrollerede baner, med `h * maxHeight / 65535` og rækker langs +y. `h / 32` eller den anden akserækkefølge misser med titalls til hundredvis af meter.
- Skinnesektioner kædet langs en vej løber langs `rotationMatrix` række 0 (det store flertal).
- `.cdae`-nodens rotation skal transponeres. Med det matcher verdens-boundingboksene den kilde-`.dae` til millimeteren. Den lærebogsmæssige måde er 38 cm forkert (median).
- Eksporteret på flere udgivne baner af alle slags, på sekunder til minutter hver.
