---
title: "Forza Horizon"
nav_order: 1
lang: "da"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Eksport af baner: Forza Horizon {#course-export-forza-horizon}

Forza-eksporten læser banen direkte ud af spillets ForzaTech-arkiver: terræn, hvor vej, kant og græs er adskilt, en jordtekstur bagt ud fra spillets egne jordkort, og hver placeret model i sin egen tekstur (kantsten, autoværn, dækvægge, skilte, rekvisitter, bygninger). Den finder også hvilket af spillets løb omgangen blev kørt på, og tilføjer det spillet sender ud for netop det løb (dets event-lag: barrierer, telte, portaler, tribuner, flag), og jorden på et venue som kørslen passerer igennem, for eksempel et stadions gulv.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Kilder: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Containerformaterne selv står på [ForzaTech](reader-forzatech.md).

## Finde det installerede spil {#finding-the-installed-game}

Ingen bør skulle skrive en sti som
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, så stien findes automatisk:

1. **Steam-biblioteker.** Steams `config\libraryfolders.vdf` læses fra
   `C:\Program Files (x86)\Steam` eller `C:\Program Files\Steam`, og hver `"path"`-post i den er et bibliotek. Hvert biblioteks `steamapps\common` søges.
2. **Microsoft Store.** `C:\XboxGames` søges, hvis den findes. Der ligger spillet et niveau dybere, i `<game>\Content`.
3. En **spilmappe** er enhver underordnet mappe til disse, der har en `media\Tracks`-mappe, uanset navn.
4. En **banemappe** er enhver mappe under `media\Tracks` der holder en `GeoChunk0.minizip`. Den tæller på sit indhold, ikke sit navn, så en bane under et navn ingen har set endnu, bliver stadig fundet.

Hvis spillet ligger et andet sted, giv banemappen med `--track`; se [Fejlfinding](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` springer alt dette over.

En banemappe holder det eksporten læser:

| Fil | Hvad den er |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arkiverne: hver model, tekstur og placeringsfil, uden navne indeni |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | én linje pr. arkivpost, i postrækkefølge: den eneste kilde til navne |
| `AssetManifest.xml` | hver tekstur banen leverer, med den hash materialerne henviser til den med |

## Hvilken bane {#which-track}

Et spil leverer mere end én banemappe (den åbne verden, et garage eller to). Den rigtige vælges efter **koordinater, ikke navn**:

- Omgangens bounding box, udvidet med `--margin`, er spørgsmålet.
- For hver banemappe læses de fire `ChunkContentsMiniZip*.txt`-manifester som tekst, uden at åbne et arkiv. Hvert terrænflisenavn (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) bærer sin gitterposition. Værktøjet tæller hvor mange forskellige fliser der ligger inden for boksen.
- Banen med flest fliser dér vinder. Hvis ingen bane har nogen, stopper eksporten med "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Et helt spor svarer på godt under et sekund. Et navnematch kunne vælge det forkerte kort, og et forkert kort ser lige så plausibelt ud som det rigtige.

Konsollen skriver `on <track>, in <game folder>`.

## Which race {#which-race}

Spillet leverer hvert af sine løb som en rute med et nummer, sit **rute-id**. To filer hører til hver rute:

| Fil | Hvad den holder |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | løbets AI-kørselslinje: en 56-byte node fra byte `0x60`, nodeantallet ved `0x24`, og hver node begynder med sin position (x, y, z) i spillets meter |
| `media\Stripped\gs\<map>\routedefinitions.zip` | én `route<id>_<map>.rtd` pr. løb: almindelig XML der lister hvad løbet tilføjer til verden og hvad det fjerner (se [Løbets eget lag](#the-races-own-layer)) |

Omgangen matches til en rute ved at sammenligne den med hver AI-linje hvis boks overlapper omgangens:

- Fra hvert omgangssample afstanden til linjens nærmeste punkt; og fra hvert punkt på linjen afstanden til det nærmeste omgangssample.
- De to medianer lægges sammen. Ruten med den mindste sum vinder, hvis summen er under **30 m** (`MATCH`).
- Begge retninger er nødvendige: en kort sprint ligger langs en lang rute der bruger samme vej, og en lang omgang dækker en kort rute.

Konsollen skriver `the game's route <id> (driven line within <n> m of it)`, eller at ingen rute matcher. Uden match placeres kun den frie verden.

## Terræn {#terrain}

Sådan findes terrænet (i `forzaterrain.py`):

- Manifesterne navngiver terræn som et rumligt indeks:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- De to tal er gitterkoordinater der **går i trin af 1023**, og hvert gittertrin er en **512 m** flise. Flise `x-2046` er `-2046 / 1023 = -2`, som begynder ved `-2 * 512 = -1024` m. Læser man navnene som meter, misser hvert opslag med en faktor to og returnerer alligevel terræn, fra den forkerte del af kortet.
- En flise kan optræde tre gange: almindelig, `_cb` og `_ul`. Alle tre dækker den samme jord. Én tages pr. flise, i den rækkefølge, for at samle dem ville tredoble geometrien til sammenfaldende flader.
- En flise læses kun hvis den rører omgangens boks **og** korridoren. En flise korridoren ikke rører, dekomprimeres aldrig.
- Hver `.modelbin` i en valgt flise afkodes kun ved **detaljeniveau 0**. En flise bærer fire niveauer over den samme jord, og at eksportere dem alle ville lægge den samme kvadratmeter i filen fire gange.
- Hvert mesh har sin egen verdensskala og bias, så en flise lander der spillet placerer den, uden en instanstransform. Trekanter hvis fodaftryk overlapper boksen beholdes, derefter kun dem der rækker ind i korridoren.
- Et mesh i et format læseren afviser springes over og tælles (`N meshes could not be read`), så et tyndt resultat siger hvorfor.

Terrænopsummeringen udskriver antallet af vertices, trekanter, meshes og fliser samt udstrækningen i x/y/z.

### Vej, kant, terræn, markeringer, vand {#road-verge-terrain-markings-water}

Materialenavne kan ikke sige hvor vejen er. Omkring en bane bruger 94 % af jorden et vejshader-materiale, fordi terræn nær en vej tegnes med det, og shaderen afgør asfalt eller græs pixel for pixel. Så:

| Type | Afgjort af |
|---|---|
| vejstrimmel | **vertexlayoutet**: vejstrimler er den eneste jord med et andet UV-sæt (kanal 1); en trekant hvis tre vertices alle har det, er vej |
| asfalt kontra kant | inden for en vejstrimmel, flisens **asfaltmaske** i trekantens centroide: 0,5 eller mere er `road`, mindre er `verge` |
| markeringer | materialenavn der matcher `whiteline`, `yellowline` eller `decal` |
| däkspor | materialenavn der matcher `tyremark` eller `skid` (tjekket før markeringer, fordi däkspor leveres som `tyremark_decal_*`) |
| vand | materialenavn der matcher `water`, `lake`, `river`, `paddy`, `ocean` eller `sea` |
| terræn | alt andet |

Målt på testbanens optagede omgange, lander næsten alle samples på vejstrimmeltrekanter, og det store flertal på asfaltdelen når masken har skilt kanten fra.

Asfaltmasken findes kun når jordteksturer bages. Med `--no-textures`, eller for en flise hvis kort mangler, bliver vejstrimler hele som `road`, og ingen kant skilles fra. Manglende kort koster detalje, aldrig geometri.

### Malede lag løftes {#painted-layers-are-lifted}

Baneafmærkninger og däkspor leveres som egne trekanter, der ligger præcis i vejen. Spillet tegner dem med en dybdeforskydning. Tegnes de som de er, kæmper vej og maling om hver pixel. Eksporten giver hver markerings- og däksporsdel sin egen kopi af vertices, løftet **5 cm** (`DECAL_LIFT`) langs overfladenormalen, så vejen under den ikke løftes med.

### Normaler {#normals}

Terrænnormaler kommer fra arkivet. Normalens x gemmes som positionens fjerde short, og y og z i `NORMAL`-attributten (se [ForzaTech](reader-forzatech.md)). Hvis en vertex i udtrækningen mangler en normal, beregnes normaler for hele jorden ud fra trekanterne i stedet.

## Jordteksturen {#the-ground-texture}

Hver terrainflise leverer tre kort der dækker dens 512 m kvadrat, i fem opløsninger (`_quality1` til `_quality5`, den største 2048 px, som er 25 cm pr. pixel):

| Kort | Filnavnsmønster | Hvad det holder (målt) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detaljenormal (x, z). A: lavt på asfalt og på ru jord |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | lagvægte. B: højt på asfalt (239 på den kørte linje, 165 ved siden af) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: lavt på asfalt (147 mod 215). B: stiger i skov |

Intet af dette er et farvefotografi. Det er de input spillets terrainshader blander sine materialelag med, og de lag er ikke afkodet. Så den bagte tekstur er **en fortolkning, ikke en kopi af spillets udseende**. Den bevarer *hvor* hver slags jord er, ved 25 cm, og maler den i faste farver:

| Jord | Lineær RGB | Vægt |
|---|---|---|
| græs (kort, nær banen) | 0,30, 0,44, 0,18 | grundlaget |
| ru (længere ude) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| skov | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Begge kort skal være enige om asfalt. Det ene alene efterlader gråt korn i græsset hvor blokkompressionen ringer. Resultatet skygges af hovedkortets detaljenormal mod et fast lys (`0.55 + 0.6 * lambert`), så kantlæber, skråninger og hjulspor læses som relief, og skrives som 8-bit sRGB.

Orientering: pixelrække 0 er flisens **nord**-kant (størst z), kolonne 0 dens **vest**-kant (mindst x). Det blev fundet ved at projicere optagede omgange på asfaltmasken på alle otte måder et kvadrat kan vendes eller drejes. Præcis én måde lægger dem på asfalt. UV'erne følger deraf: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Kortene læses i den bedste tilgængelige opløsning op til kvalitet 5 og omsamples til hovedkortets størrelse. Er farvebilledet større end `--texture-size`, formindskes det derefter til den størrelse med Lanczos-filtrering. Asfaltmasken beholdes altid i fuld opløsning, fordi den afgør geometrien. `--season` vælger `x<season>x`-kortene. En flise uden kort for den sæson tegnes i flade farver, og konsollen rapporterer `N without maps`.

## Placerede modeller {#placed-models}

Terrænet bærer sin egen verdensposition. Intet andet gør. Hvor hver kopi af en model står, er optaget i `.pgeo`-placeringsfiler, én pr. kategori pr. rumlig celle: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Postlayoutet står på [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Hvad læses {#what-is-read}

- Placeringsfiler filtreres **efter navn**: cellestørrelsen og cellepositionen i stien giver cellens kvadrat (`x * size` til `(x + 1) * size`), og kun celler der overlapper omgangens boks, i en ønsket kategori, åbnes.
- Kategorier som standard: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` tilføjer `trees`, `bushes` og `smashables`. Disse læses aldrig: `grasstemplate`, `crowdtemplate` og `cwdspline` (græs og tilskuere: spillet tegner dem som animerede sprites, der er ingen geometri).
- Hver fil hører til et **lag**, læst fra dens navn efter `c<size>_<category>_`. Et detaljeniveau-ord (`do`, `so`, `ulc`, `ulp`, `cwd`) og et valgfrit sektionsnummer er den frie verden. Alt andet er et lag spillet tænder: et runtime-lag (`rt_0`), en aktivitet (`_tag_<name>_`), et samleobjekt, alt der er gemt under `evolving`. Et lag der navngiver ruter (`rt_x<id>`, for eksempel `rt_x1023_x2201`) hører kun til de løb, og læses kun når omgangen matchede dem. Se [Tændte lag](#switched-on-layers).
- En kopi beholdes hvis dens position er inden for boksen og korridoren. Præcise gentagelser (samme position og orientering til millimeteren, opført af to nabo-celler) slås sammen.
- **Kantsten** er props hvis modelnavn begynder med `road_gen_rum` (rumble strips). De skrives som `ground:kerbs`, forenkles aldrig og udelades aldrig, fordi en omgang måles mod dem.

| Kategori | Del | Reservefarve (ingen tekstur) |
|---|---|---|
| kantsten | `ground:kerbs` | 0,60, 0,12, 0,10 |
| barrierer | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekvisitter | `structure:props` | 0,45, 0,35, 0,25 |
| skilte | `structure:signs` | 0,70, 0,70, 0,70 |
| bygninger | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktur | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| broer | `structure:bridges` | 0,45, 0,45, 0,45 |
| klipper | `structure:rocks` | 0,30, 0,28, 0,25 |
| knusbare ting | `structure:smashables` | 0,12, 0,22, 0,06 |
| træer, buske | `structure:trees` | 0,10, 0,20, 0,05 |

### Modellens geometri {#the-models-geometry}

Et placeret navn `<model>_3D` henviser til modelfilerne `<model>_cluster###.i.modelbin` (op til et dusin). Hver trekant bærer en maske over de detaljeniveauer den hører til:

- En models niveauer er dens trekanter der udtrykkeligt er markeret for det niveau. Niveauerne løber sammenhængende fra 0, fineste først.
- Trekanter markeret `0xFFFF` (alle niveauer) er de brydelige stykker, for eksempel et autoværns stolper eller en dækstabels enkelte dæk. De overlapper hele modellen, og spillet tegner dem i stedet for den når den er slået i stykker. De bruges kun af en model uden noget udtrykkeligt markeret niveau.
- Submeshes hvis materialeshader er en projiceret **dekal**, udelades.

Hver kopi placeres med sin position, sine x- og y-akser fra posten (z = x krydset y) og sin skala. Normaler transformeres med den inverse skala.

### Hvilken tekstur {#which-texture}

Et materiale navngiver ikke sine teksturer. Det lister dem som hashes, og banens `AssetManifest.xml` afbilder hver hash (`SourceHash`) til et teksturnavn. Kun `<Textures>`-sektionen læses, og læsningen stopper ved `</Textures>` i en fil der kan være titalls megabytes. Så:

1. Slot `0x88B483AA` er grundfarven i standard-miljøshaderen (næsten alle samplede materialer). Binder materialet en tekstur dér, bruges den.
2. Ellers afgør teksturens egen type, som er ordet før dens GUID: `_bclr_`, så `_diff_`, så `_colour_`.
3. Terrænkort (`mainmap`, `submap`, `autogloss`) og tintpaletter (`tint`, `worldtint`) farver aldrig en model.

En model farves altså af hvad dens materiale binder, ikke af en tekstur der navngiver sig efter modellen. For eksempel bruger `bar_rur_armco_crct_02_c` teksturen fra `..._02_a`.

Teksturen læses fra arkiverne i den mindste opløsning på mindst **256 px** over (`MODEL_TEXTURE`), formindskes til 256 hvis den er større, og gemmes som RGB-JPEG i `.glb`. Et autoværns farve ved 256 px for fire meter er 1,6 cm pr. pixel, og omkring 80 sådanne teksturer passer i viewerens atlas ved siden af jordfliserne.

**Sæsoner.** `--season` bytter en tekstur ud med sin sæsontvilling efter navn, med GUID'en ignoreret (`..._xsummerx_bclr` til `..._xwinterx_bclr`, eller `..._bclr` til `..._winter_bclr`), når banen har en. Med `--season winter` bruges en submeshes vintermateriale også hvor dens variantTabel navngiver et.

**Varianter.** En submesh-post åbner med en tabel over `(summer, winter)`-materialer, ét for hvert udseende en kopi kan have: fem tryk på et billboard, seks malingsfarver på en dækstabel. Hver placeringspost siger hvilken variant den kopi bærer. En submesh med færre varianter end modellen gentager sine egne.

**Pladsholderblokken.** Delte bygningsatlasser reserverer en fast RGB-blok (255, 64, 0) til flader bygningsshaderen farver med andre teksturer. Hvis mere end en tyvendedel af en tekstur ligger inden for 12 niveauer af den farve, males blokken om i teksturens egen gennemsnitsfarve. Ellers bliver en by orange.

### Gennemsigtige flader {#see-through-surfaces}

Kædehegn og net er enkelte quads med huller i teksturens alfa. Tegnet ugennemsigtigt er et hegn en væg hen over banens udsyn. Flader hvis materialeshader matcher `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` eller `tree`, testes:

- Teksturens opacitet midles over et 32 x 32 gitter.
- Pr. flade (hver udskåret trekant der deler en tekstur) samples fire punkter pr. trekant i UV-rummet og vejes efter trekantens UV-areal.
- Hvis den gennemsnitlige opacitet er mindst 0,05 og under **0,5**, udelades hele fladen. Under 0,05 betyder alfaen klart noget andet for dens shader (et advarselsskilt der samples til 0,01), og fladen beholdes massiv.
- En model hvis hver flade blev udeladt, rapporteres: `N models left out as see-through (mostly holes in their texture)`.

Værktøjet vurderer hele fladen i stedet for én trekant ad gangen. Vurderet pr. trekant overlevede halvdelen af hver quad, og hegn kom ud som rækker af tænder.

### Bygninger tegnet som helhed {#buildings-drawn-whole}

En by bygger sine bygninger af modulære stykker: hundredtusinder af dem omkring ét gadebane, titalls millioner trekanter selv i deres groveste niveau. At udelade stykker ét ad gangen efterlod stående enkelte vægplader. Spillet leverer også helhedsstandin i `scene\hlod_tier_1\`, ét mesh pr. bygning (stamme `hlod_tier_1_*`), allerede i verdenskoordinater ligesom terrænet:

- Hver standins verdensboks læses fra dens mesh' positionsboks (en header-læsning, ikke en afkodning). Det tager sekunder for et helt kort.
- Standins der rører omgangens boks og korridoren, bruges.
- Hver `buildings`-stykke hvis position falder inden for en standins fodaftryk (plus 0,5 m) droppes, og standin tegnes i stedet. Dens afstand til kørslen måles til bygningens nærmeste kant.
- Opsummeringen siger `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Switched-on layers {#switched-on-layers}

Det et tændt lag placerer, eksporteres, men adskilt fra den frie verden, så vieweren kan vise eller skjule det:

| Lag | Del |
|---|---|
| den frie verden | `structure:<category>` (som før) |
| et lag der navngiver det matchede løbs rute | `structure:event_<category>` |
| et andet tændt lag | `structure:layer_<category>` |

Opsummeringen tæller dem: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modeller der allerede er i verdenskoordinater {#models-already-in-world-coordinates}

Nogle typer modeller står ikke i nogen placeringsfil. Deres meshes bærer deres egen verdensposition, ligesom terrænet, så intet skal placere dem:

| Mappe under `scene\models\` | Hvad den er | Del |
|---|---|---|
| `plots` | et venues egen jord: et stadions gulv og midtbane, et festivalområde, en plads | `ground:venue` |
| `plinths` (og enhver model der hedder `floor`, `ground` eller `road`) | jord en gade er pyntet med: plantekasser, trapper, en parks belægning | `ground:plinths` |
| `hda_infrastructure` (broer) | proceduralt byggede broer | `structure:bridges` |

- En model tæller som værende i verdenskoordinater når midten af dens boks ligger mere end **300 m** (`WORLD_REACH`) fra sit eget origin. Modeller placeret af placeringsfilerne ligger inden for et par hundrede meter fra deres.
- Tegnes ikke: occludere, kabler spændt langs vejene, havets baggrund, tagene og occludere på modulære bygninger (standins tegner dem), kollisions- og vandvolumener.
- Hver læses fra boksen af dens meshes (en header-læsning), nogle få sekunder for et helt kort, én gang pr. kørsel.
- Jorddele tegnes aldrig grovere og udelades aldrig for at passe budgettet, ligesom kantsten.

**Et venue skæres helt.** Når kørslen rører et venues egen jord (`ground:venue`), udvides korridoren til hele den jords fodaftryk plus `--margin`, så tribunerne, murene og barriererne omkring et stadion følger med, ikke kun stripen omgangene brugte. Konsollen skriver `through a venue (<model names>): cutting all of its ground, <n> km2`. Plinths udvider ikke udskæringen.

### Detalje og budgettet {#detail-and-the-budget}

Afstandsbånd, budget og hvilke kopier der går først når budgettet er for lille, står på [Detaljeniveauer og budgettet](detail-budget.md).

### Placeringsopsummering {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## The race's own layer {#the-races-own-layer}

Mange løb sender ting ud, der ikke findes i den frie verden: betonvægge og hegn der lukker sidegader, dækstabler, telte, en startportal, tribuner, flag, bannere. Hvert løb lister dem i sin rutedefinition (`route<id>_<map>.rtd` i `routedefinitions.zip`, almindelig XML i et almindeligt zip):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Hvad der tilføjes.** Hver instans placeres som en placeringsfil-kopi. Transformens 16 tal er fire rækker: modellens x-, y- og z-akser (hver skaleret) og dens position i spillets meter. Den tredje række er krydsproduktet af de to første. `Material` er den variant kopien bærer. Delen er `structure:event_<kind>`, hvor `<kind>` er mappen under `scene\models\` (barriers, props, infrastructure, signs; alt andet tæller som props), og noden bærer glTF-extras `{"layer": "event", "route": <id>}`.
- **Hvad der fjernes.** En kopi i den frie verden der står inden for **0,1 m** af et skjult aktivs position udelades. Et skjult aktiv der står i origin, er en model i verdenskoordinater; dens instans-GUID slås op i banens `AssetManifest.xml` (`<Models>`-listen: en models kilde, derefter GUID'erne for dens kopier) for at navngive den.
- **Jord løbet skjuler, beholdes.** Et løb der skjuler et venues jord, lægger sin egen overflade der. Når den overflade ikke er blandt de modeller banen leverer, bliver den skjulte jord stående, som det nærmeste til det man kører på, og opsummeringen siger det (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Ikke tegnet, men talt.** Tilskuermarkører (`crowd_proxies`: spillet tegner publikum som sprites ud fra dem) og kollisionssplines (`.splinecol`). Konsollen lister dem: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Rute-aktiver banen ikke leverer en model til (lysglimt, nogle skilte, indhold spillet streamer ind), nævnes under `placed names have no model in the archives`.

Kun kopier inden for korridoren placeres, som for alt andet.

## Writing the file {#writing-the-file}

Dele skrives i denne rækkefølge: pr. flise `terrain`, `verge`, `road` (hver med flisens billede), derefter `water`, `tyre marks`, `markings` (flade, de to sidste løftet), og så hver placeret del sorteret efter navn. Koordinaterne er spillets egne (meter, Y op). Se [Outputformat](output-format.md).

Filen siger hvad den holder i sin glTF `asset.extras`:

| Felt | Betydning |
|---|---|
| `course_format` | `2`: løbets eget lag, venues og verdensmodeller er i den. [`courses`](commands.md#courses) eksporterer en fil med et lavere nummer (eller ingen) igen |
| `route` | det matchede rute-id, eller `null` |
| `event_copies`, `event_kinds` | hvor mange kopier af løbets eget lag der blev placeret, og deres typer |
| `hidden` | kopier i den frie verden der er udeladt fordi løbet fjerner dem |
| `venue` | de venue-jordmodeller kørslen passerer |
| `layers` | de tændte lag der blev placeret |

## Hvad det koster {#what-it-costs}

Grove størrelsesordener:

| Bane | Resultat |
|---|---|
| en kort landevejsbane | nogle hundrede tusinde terræntrekanter, over en million placerede; sekunder, under 100 MB |
| en lang punkt-til-punkt-sprint | korridoren er en lille brøkdel af boksen omkring den; omkring et minut, nogle hundrede MB |
| en bybane | tusindvis af barrierer, rekvisitter og skilte, og hele bygninger; med det automatiske budget op til flere hundrede MB |

Et kvadratkilometer åbent verdensterræn er omkring en million trekanter.

## Kontroller bag det {#checks-behind-it}

Disse er målinger lavet da læseren blev skrevet, som angivet i kilden. De køres ikke igen af testene, medmindre spillet er installeret.

- På testbanen ligger bilen omkring sin kørehøjde over den udtrukne jord (median under 0,2 m).
- Hver samplet flise ligger inden for det 512 m kvadrat dens navn forudsiger.
- Autoværnsplaceringer lige efter hinanden er præcis 4 m fra hinanden, og de fleste autoværnsender ligger inden for 5 cm af den næste start.
- Kantsten ligger et par centimeter over den udtrukne jord, med siderne opad, inden for 5 m af kørslen (også en test mod det installerede spil, se [Udvikling](development.md)).

## Tegnes ikke {#not-drawn}

- Træer og buske, medmindre `--trees`. Græs og publikum aldrig (spillet tegner dem som sprites).
- Et løbs egne modeller som banen ikke leverer (se [Løbets eget lag](#the-races-own-layer)).
- Projicerede dekalmaterialer på modeller.
- Skiltetryk der er alfa-blandet over deres tavle, kommer ud ugennemsigtige.
- Jordfarven er en rekonstruktion af hvor asfalt, græs og skov ligger, ikke spillets egne terrainmaterialer.
