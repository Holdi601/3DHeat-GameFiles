---
title: Forza Horizon
lang: "no"
source: course-forza-horizon.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Banueksport: Forza Horizon

Forza-eksporten leser banen rett ut av spillets ForzaTech-arkiver: terreng med vei, kant
og gress skilt fra hverandre, en bakketekstur innbakt fra spillets egne bakkekart, og hver
plasserte modell i sin egen tekstur (kanter, barrierer, dekkmurer, skilt, rekvisitter,
bygninger). Den finner også hvilket av spillets løp lapet ble kjørt på, og legger til det
spillet sender ut for akkurat det løpet (dets hendelseslag: barrierer, telt, portaler,
tribuner, flagg), og bakken til ethvert venue kjøringen går gjennom, for eksempel et
stadions gulv.

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
Selve containerformatene står på [ForzaTech](reader-forzatech.md).

## Finne det installerte spillet

Ingen skal måtte skrive en sti som
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, så stien finnes av seg selv:

1. **Steam-biblioteker.** Steams `config\libraryfolders.vdf` leses fra
   `C:\Program Files (x86)\Steam` eller `C:\Program Files\Steam`, og hver `"path"`-oppføring
   i den er et bibliotek. `steamapps\common` i hvert bibliotek søkes.
2. **Microsoft Store.** `C:\XboxGames` søkes hvis den finnes. Der ligger spillet ett nivå
   dypere, i `<game>\Content`.
3. En **spillmappe** er hvilken som helst undermappe i disse mappene som har en
   `media\Tracks`-mappe, uansett navn.
4. En **banemappe** er hvilken som helst mappe under `media\Tracks` som har en
   `GeoChunk0.minizip`. Den regnes etter innholdet, ikke navnet, så en bane under et navn
   ingen har sett, blir likevel funnet.

Hvis spillet ligger et annet sted, gi banemappen med `--track`; se
[Feilsøking](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` hopper over alt dette.

En banemappe har det eksporten leser:

| Fil | Hva den er |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arkivene: alle modeller, teksturer og plasseringsfiler, uten navn inni |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | én linje per arkivinnslag, i innslagsrekkefølge: den eneste kilden til navn |
| `AssetManifest.xml` | hver tekstur banen leverer, med hashen materialene refererer den med |

## Hvilken bane

Et spill leverer mer enn én banemappe (det åpne kartet, et garasje eller to). Den rette
velges etter **koordinater, ikke navn**:

- Lapets omsluttende boks, utvidet med `--margin`, er spørsmålet.
- For hver banemappe leses de fire `ChunkContentsMiniZip*.txt`-manifestene som tekst, uten å
  åpne et arkiv. Hvert terrengflis-navn (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`)
  bærer sin plassering i rutenettet. Verktøyet teller hvor mange ulike fliser som ligger
  innenfor boksen.
- Banen med flest fliser der vinner. Hvis ingen bane har noen, stopper eksporten med
  "none of the installed tracks (...) has terrain at x ..., z ....  Those are the game's own
  metres, as its telemetry reports them."

Et helt banesvar tar godt under et sekund. Et navnetreff kunne velge feil kart, og et feil
kart ser like troverdig ut som det rette.

Konsollen skriver `on <track>, in <game folder>`.

## Hvilket løp

Spillet leverer hvert av sine løp som en rute med et nummer, sin **rute-id**. To filer hører
til hver rute:

| Fil | Hva den inneholder |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | løpets AI-kjørelinje: en 56 byte stor node fra byte `0x60`, antallet noder ved `0x24`, og hver node starter med sin posisjon (x, y, z) i spillets meter |
| `media\Stripped\gs\<map>\routedefinitions.zip` | én `route<id>_<map>.rtd` per løp: ren XML som lister hva løpet legger til i verden og hva det tar bort (se [Løpets eget lag](#the-races-own-layer)) |

Lapet kobles til en rute ved å sammenligne det med hver AI-linje som har en boks som
overlapper lapets:

- Fra hvert lap-punkt, avstanden til nærmeste punkt på linjen; og fra hvert punkt på linjen,
  avstanden til nærmeste lap-punkt.
- De to medianene legges sammen. Ruten med minst sum vinner hvis summen er under **30 m**
  (`MATCH`).
- Begge veier trengs: en kort sprint ligger langs en lang rute som bruker samme vei, og et
  langt lap dekker en kort rute.

Konsollen skriver `the game's route <id> (driven line within <n> m of it)`, eller at ingen
rute passer. Uten treff plasseres bare den frie verdenen.

## Terreng

Slik finnes terrenget (i `forzaterrain.py`):

- Manifestene nevner terreng som et romlig indeks:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- De to tallene er rutenettkoordinater som **går i steg på 1023**, og hvert rutenettsteg er en
  **512 m** flis. Flis `x-2046` er `-2046 / 1023 = -2`, som begynner på `-2 * 512 = -1024` m.
  Leser du navnene som meter, bommer hvert oppslag med en faktor to, og fortsatt får du
  terreng - fra feil del av kartet.
- En flis kan dukke opp tre ganger: vanlig, `_cb` og `_ul`. Alle tre dekker samme bakke. Én tas
  per flis, i den rekkefølgen, fordi å slå dem sammen ville tredoblet geometrien til
  sammenfallende flater.
- En flis leses bare hvis den berører lapets boks **og** korridoren. En flis korridoren ikke
  berører, blir aldri dekomprimert.
- Hver `.modelbin` i en valgt flis dekodes på **detaljnivå 0 bare**. En flis har fire nivåer
  over samme bakke, og å eksportere dem alle legger samme kvadratmeter inn i filen fire ganger.
- Hvert mesh har sin egen skala og forskyvning i verdenskoordinater, så det havner der spillet
  plasserer det uten noen instanstransformasjon. Trekanter der fotavtrykket overlapper boksen
  beholdes, og deretter bare de som når inn i korridoren.
- Et mesh i et format leseren nekter, hoppes over og telles (`N meshes could not be read`),
  så et tynt resultat forklarer seg selv.

Terrengsammendraget skriver antall hjørnepunkter, trekanter, meshes, fliser og
x/y/z-utstrekningen.

### Vei, kant, terreng, merkinger, vann

Materialnavn kan ikke si hvor veien er. Rundt en bane bruker 94 % av bakken et
veiskyggematerial, fordi terreng nær en vei tegnes med det, og skyggeren avgjør asfalt eller
gress per piksel. Så:

| Type | Avgjort av |
|---|---|
| veistrimmel | **hjørnelayouten**: veistrimler er den eneste bakken med et andre UV-sett (kanal 1); en trekant der alle tre hjørnene har det, er vei |
| asfalt kontra kant | innenfor en veistrimmel, flisens **asfaltmaske** i trekantens midtpunkt: 0,5 eller mer er `road`, mindre er `verge` |
| merkinger | materialnavn som passer `whiteline`, `yellowline` eller `decal` |
| dekkmerker | materialnavn som passer `tyremark` eller `skid` (sjekkes før merkinger, fordi dekkmerker leveres som `tyremark_decal_*`) |
| vann | materialnavn som passer `water`, `lake`, `river`, `paddy`, `ocean` eller `sea` |
| terreng | alt annet |

Målt på testbanens innspilte lap, havner nesten alle punkter på veistrimmel-trekanter, og
det store flertallet på asfaltdelen når masken har skilt av kanten.

Asfaltmasken finnes bare når bakketeksturer bakes. Med `--no-textures`, eller for en flis
der kartene mangler, forblir veistrimlene hele som `road`, og ingen kant skilles av. Manglende
kart koster detalj, aldri geometri.

### Malte lag løftes

Linjemarkeringer og dekkmerker leveres som egne trekanter som ligger nøyaktig i veien. Spillet
tegner dem med en dybdeforskyvning. Tegnes de slik de er, kjemper vei og maling om hver piksel.
Eksporten gir hver merknads- og dekkmerkedel sin egen kopi av hjørnepunktene, løftet **5 cm**
(`DECAL_LIFT`) langs flatens normal, så veien under ikke løftes med.

### Normaler

Terrengnormaler kommer fra arkivet. Normalens x lagres som posisjonens fjerde short, og y og z
i `NORMAL`-attributtet (se [ForzaTech](reader-forzatech.md)). Hvis et hjørnepunkt i uttrekket
mangler en normal, beregnes normalene for hele bakken fra trekantene i stedet.

## Bakketeksturen

Hver terrengflis leverer tre kart som dekker sin 512 m firkant, i fem oppløsninger
(`_quality1` til `_quality5`, den største 2048 piksler, altså 25 cm per piksel):

| Kart | Filnavnmønster | Hva det inneholder (målt) |
|---|---|---|
| hoved | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detaljnormal (x, z). A: lavere på asfalt og på ujevn grunn |
| under | `submap_x<X>_z<Z>_x<season>x_diff` | lagvekter. B: høy på asfalt (239 på den kjørte linjen, 165 ved siden av) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: lav på asfalt (147 mot 215). B: stiger i skog |

Ingen av disse er et fargefotografi. De er inngangene spillets terrengskygger blander sine
materiallag med, og de lagene er ikke dekodet. Så den innbakte teksturen er **en tolkning, ikke
en kopi av spillets utseende**. Den beholder *hvor* hver type bakke er, i 25 cm, og maler den i
faste farger:

| Bakke | Lineær RGB | Vekt |
|---|---|---|
| gress (kort, nær banen) | 0,30, 0,44, 0,18 | grunnlaget |
| ru (lenger ut) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| skog | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Begge kartene må stemme for asfalt. Ett alene etterlater grått sprenkel i gresset der
blokkkomprimeringen ringer. Resultatet skygges av hovedkartets detaljnormal mot et fast lys
(`0.55 + 0.6 * lambert`), så kantlepper, skråninger og hjulspor leses som relieff, og skrives
som 8-bit sRGB.

Orientering: pikselrad 0 er flisens **nord**-kant (størst z), kolonne 0 dens **vest**-kant (minst
x). Dette ble funnet ved å projisere innspilte lap på asfaltmasken på alle de åtte måtene en
firkant kan speiles eller snus. Nøyaktig én måte legger dem på asfalt. UV-ene følger av det:
`u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Kartene leses i den beste oppløsningen som finnes opp til kvalitet 5, og resamples til
hovedkartets størrelse. Hvis fargebildet er større enn `--texture-size`, krympes det deretter
til den størrelsen med Lanczos-filtrering. Asfaltmasken beholdes alltid i full oppløsning, fordi
den avgjør geometrien. `--season` velger `x<season>x`-kartene. En flis uten kart for den sesongen
tegnes i flate farger, og konsollen skriver `N without maps`.

## Plasserte modeller

Terrenget bærer sin egen verdensposisjon. Ingenting annet gjør det. Hvor hver kopi av en modell
står, er registrert i `.pgeo`-plasseringsfiler, én per kategori per romlig celle:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Postoppsettet står på
[ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Hva leses

- Plasseringsfiler filtreres **etter navn**: celle­størrelsen og cellens posisjon i stien gir cellens
  firkant (`x * size` til `(x + 1) * size`), og bare celler som overlapper lapets boks, i en ønsket
  kategori, åpnes.
- Kategorier som standard: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`,
  `rocks`, `evolving`. `--trees` legger til `trees`, `bushes` og `smashables`. Disse leses aldri:
  `grasstemplate`, `crowdtemplate` og `cwdspline` (gress og tilskuere: spillet tegner dem som
  animerte sprites, det finnes ingen geometri).
- Hver fil tilhører et **lag**, lest fra navnet etter `c<size>_<category>_`. Et detaljnivåord
  (`do`, `so`, `ulc`, `ulp`, `cwd`) og et valgfritt seksjonsnummer er den frie verdenen. Alt annet er
  et lag spillet slår på: et kjøretidslag (`rt_0`), en aktivitet (`_tag_<name>_`), et samleobjekt,
  alt under `evolving`. Et lag som nevner ruter (`rt_x<id>`, for eksempel `rt_x1023_x2201`) hører
  bare til disse løpene, og leses bare når lapet passet til en av dem. Se
  [Påslåtte lag](#switched-on-layers).
- En kopi beholdes hvis posisjonen er inne i boksen og inne i korridoren. Nøyaktige gjentakelser
  (samme posisjon og retning til millimeteren, oppført av to nabeceller) slås sammen.
- **Kanter** er rekvisitter hvis modellnavn begynner med `road_gen_rum` (rumble strips). De skrives
  som `ground:kerbs`, aldri forenklet og aldri utelatt, fordi et lap måles mot dem.

| Kategori | Del | Reservefarge (uten tekstur) |
|---|---|---|
| kanter | `ground:kerbs` | 0,60, 0,12, 0,10 |
| barrierer | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekvisitter | `structure:props` | 0,45, 0,35, 0,25 |
| skilt | `structure:signs` | 0,70, 0,70, 0,70 |
| bygninger | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktur | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| broer | `structure:bridges` | 0,45, 0,45, 0,45 |
| steiner | `structure:rocks` | 0,30, 0,28, 0,25 |
| knuselementer | `structure:smashables` | 0,12, 0,22, 0,06 |
| trær, busker | `structure:trees` | 0,10, 0,20, 0,05 |

### Modellens geometri

Et plassert navn `<model>_3D` peker til modellfilene `<model>_cluster###.i.modelbin` (opptil et dusin).
Hver trekant bærer en maske over hvilke detaljnivåer den hører til:

- En modells nivåer er trekantene som er eksplisitt merket for det nivået. Nivåene går sammenhengende
  fra 0, fineste først.
- Trekanter merket `0xFFFF` (alle nivåer) er de knusbare bitene, for eksempel en barrieres stolper eller
  de enkelte dekkene i en dekkstabel. De overlapper hele modellen, og spillet tegner dem i stedet for den
  når den er slått i stykker. De brukes bare av en modell uten noe eksplisitt merket nivå.
- Undermeshes der materialskyggeren er en projisert **dekal**, utelates.

Hver kopi plasseres med sin posisjon, sine x- og y-akser fra posten (z = x kryss y), og sin skala.
Normaler transformeres med den inverse skalaen.

### Hvilken tekstur

Et materiale nevner ikke sine teksturer. Det lister dem som hasher, og banens `AssetManifest.xml`
kobler hver hash (`SourceHash`) til et teksturnavn. Bare `<Textures>`-seksjonen leses, og lesingen
stopper ved `</Textures>` i en fil som kan være titalls megabyte. Deretter:

1. Plass `0x88B483AA` er grunnfargen i standardmiljøskyggeren (alle samplede materialer). Hvis
   materialet binder en tekstur der, brukes den.
2. Ellers avgjør teksturens egen type, som er ordet før dens GUID: `_bclr_`, deretter `_diff_`,
   deretter `_colour_`.
3. Terrengkart (`mainmap`, `submap`, `autogloss`) og toningspaletter (`tint`, `worldtint`) farger
   aldri en modell.

En modell farges altså av det materialet binder, ikke av en tekstur som heter som modellen. For
eksempel bruker `bar_rur_armco_crct_02_c` teksturen til `..._02_a`.

Teksturen leses fra arkivene i den minste oppløsningen som er minst **256 px** på tvers
(`MODEL_TEXTURE`), krympes til 256 hvis den er større, og lagres som RGB-JPEG i `.glb`-filen. En
rekkes farge ved 256 px for fire meter er 1,6 cm per piksel, og rundt 80 slike teksturer får plass i
visningens atlas ved siden av bakkeflisene.

**Sesonger.** `--season` bytter en tekstur med sin sesongtvilling etter navn, med GUID-en ignorert
(`..._xsummerx_bclr` til `..._xwinterx_bclr`, eller `..._bclr` til `..._winter_bclr`), når banen har en.
Med `--season winter` brukes også en undermesh sitt vintermateriale der variantstabellen nevner ett.

**Varianter.** En undermesh-post starter med en tabell over `(summer, winter)`-materialer, én for hvert
utseende en kopi kan ha: fem trykk for en reklameplakat, seks malingsfarger for en dekkstabel. Hver
plasseringspost sier hvilken variant den kopien har. En undermesh med færre varianter enn modellen
gjentar sine egne.

**Plassholderblokken.** Felles bygningsatlaser reserverer en solid RGB-blokk (255, 64, 0) for flater
bygningsskyggeren farger med andre teksturer. Hvis mer enn en tjuendedel av en tekstur er innenfor 12
nivåer av den fargen, males blokken om i teksturens egen gjennomsnittsfarge. Ellers blir en by oransje.

### Gjennomsiktige flater

Kjededreide gjerder og nett er enkle firkanter med hull i teksturens alfa. Tegnes de faste, blir et
gjerde en vegg over synsfeltet mot banen. Flater der materialskyggeren passer `alphatest`,
`alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` eller `tree` prøves:

- Teksturens opasitet snittes over et 32 x 32-rutenett.
- Per flate (hver utskåret trekant som deler én tekstur) samples fire punkter per trekant i UV-rommet,
  og vektes etter trekantens UV-areal.
- Hvis gjennomsnittlig opasitet er minst 0,05 og under **0,5**, utelates hele flaten. Under 0,05 betyr
  alfaen tydelig noe annet for skyggeren sin (et varselsskilt som samples til 0,01), og flaten beholdes
  solid.
- En modell der hver flate ble utelatt, meldes: `N models left out as see-through (mostly holes in their texture)`.

Verktøyet vurderer hele flaten og ikke én trekant om gangen. Vurdert per trekant ble halvparten av hver
firkant beholdt, og gjerdene kom ut som rader av tenner.

### Bygninger tegnet hele

En by bygger sine bygninger av modulære biter: hundretusenvis rundt én gatebane, titalls millioner
trekanter selv på det groveste. Å utelate biter én for én etterlot enkeltstående veggplater stående. Spillet
leverer også hele-bygning-stedfortredere i `scene\hlod_tier_1\`, ett mesh per bygning (stammen
`hlod_tier_1_*`), allerede i verdenskoordinater som terrenget:

- Hver stedfortreders verdensboks leses fra meshets posisjonsboks (en headerlesing, ikke en dekoding).
  Dette tar sekunder for et helt kart.
- Stedfortredere som berører lapets boks og korridoren brukes.
- Hver `buildings`-bit hvis posisjon er innenfor en stedfortreders fotavtrykk (pluss 0,5 m) fjernes, og
  stedfortrederen tegnes i stedet. Avstanden til kjøringen måles til bygningens nærmeste kant.
- Sammendraget sier `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Påslåtte lag

Det en påslått layer plasserer, eksporteres, men adskilt fra den frie verdenen, slik at visningen kan vise
eller skjule det:

| Lag | Del |
|---|---|
| den frie verdenen | `structure:<category>` (som før) |
| et lag som nevner det matchede løpets rute | `structure:event_<category>` |
| et annet påslått lag | `structure:layer_<category>` |

Sammendraget teller dem: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modeller som allerede er i verdenskoordinater

Noen typer modeller finnes ikke i noen plasseringsfil. Deres meshes bærer sin egen verdensposisjon, slik
terrenget gjør, så ingen må plassere dem:

| Mappe under `scene\models\` | Hva den er | Del |
|---|---|---|
| `plots` | et venues egen bakke: et stadions gulv og midtbane, en festivalplass, et torg | `ground:venue` |
| `plinths` (og enhver modell kalt `floor`, `ground` eller `road`) | bakke en gate er pyntet med: plantekasser, trapper, en parks belegg | `ground:plinths` |
| `hda_infrastructure` (broer) | prosedyrisk bygde broer | `structure:bridges` |

- En modell regnes som å være i verdenskoordinater når midten av boksen ligger mer enn **300 m**
  (`WORLD_REACH`) fra sitt eget origo. Modeller plassert av plasseringsfilene ligger innen et par hundre
  meter fra sitt origo.
- Tegnes ikke: okkludere, kabler strukket langs veiene, havets bakgrunn, takene og okkluderne til
  modulære bygninger (stedfortrederne tegner de bygningene), kollisjons- og vannvolum.
- Hver leses fra boksen til meshene (en headerlesing), noen sekunder for et helt kart, én gang per kjøring.
- Bakkedeler blir aldri tegnet grovere og aldri utelatt for å passe budsjettet, på samme måte som kanter.

**Et venue kuttes helt.** Når kjøringen berører et venues egen bakke (`ground:venue`), utvides korridoren
til hele bakkens fotavtrykk pluss `--margin`, så tribunene, veggene og barrierene rundt et stadion kommer
med, ikke bare stripen lapene brukte. Konsollen skriver
`through a venue (<model names>): cutting all of its ground, <n> km2`. Sokler utvider ikke kuttet.

### Detalj og budsjett

Avstandsbånd, budsjett og hvilke kopier som går når budsjettet er for lite, står på
[Detaljnivåer og budsjett](detail-budget.md).

### Plasseringssammendrag

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

## Løpets eget lag

Mange løp sender ut ting som ikke finnes i den frie verdenen: betongvegger og gjerder som stenger sidegater,
dekkstabler, telt, en startportal, tribuner, flagg, bannere. Hvert løp lister dem i sin rutedefinisjon
(`route<id>_<map>.rtd` i `routedefinitions.zip`, ren XML i et vanlig zip):

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

- **Hva som legges til.** Hver instans plasseres som en kopi fra en plasseringsfil. Transformasjonens 16
  tall er fire rader: modellens x-, y- og z-akser (hver skalert) og dens posisjon i spillets meter. Den
  tredje raden er kryssproduktet av de to første. `Material` er varianten kopien bærer. Delen er
  `structure:event_<kind>`, der `<kind>` er mappen under `scene\models\` (barriers, props, infrastructure,
  signs; alt annet regnes som props), og noden bærer glTF-extras `{"layer": "event", "route": <id>}`.
- **Hva som tas bort.** En kopi i den frie verdenen som står innen **0,1 m** fra en skjult instans' posisjon,
  utelates. En skjult instans som står i origo er en modell i verdenskoordinater; dens instans-GUID slås opp
  i banens `AssetManifest.xml` (listen `<Models>`: en modells kilde, deretter GUID-ene til dens kopier) for
  å navngi den.
- **Bakke løpet skjuler, beholdes.** Et løp som skjuler et venues bakke legger sin egen overflate der. Når
  den overflaten ikke er blant modellene banen leverer, beholdes den skjulte bakken som det nærmeste til det
  som kjøres på, og sammendraget sier det (`kept <model>: the race hides it for a surface of its own
  that the track does not ship`).
- **Ikke tegnet, men telt.** Tilskuermarkører (`crowd_proxies`: spillet tegner publikum som sprites fra dem)
  og kollisjonsspliner (`.splinecol`). Konsollen lister dem: `its own layer: <n> copies of <m> models, <k>
  free-roam objects hidden; not drawn: ...`.
- Rute-eiendeler banen ikke har en modell for (lysglimt, noen skilt, innhold spillet strømmer inn) nevnes
  i `placed names have no model in the archives`.

Bare kopier innenfor korridoren plasseres, som for alt annet.

## Skrive filen

Delene skrives i denne rekkefølgen: per flis `terrain`, `verge`, `road` (hver med flisens bilde), deretter
`water`, `tyre marks`, `markings` (flate, de to siste løftet), og så hver plassert del sortert etter navn.
Koordinatene er spillets egne (meter, Y opp). Se [Utdataformat](output-format.md).

Filen sier hva den inneholder i sin glTF-`asset.extras`:

| Felt | Betydning |
|---|---|
| `course_format` | `2`: løpets eget lag, venues og modeller i verdenskoordinater er med. [`courses`](commands.md#courses) eksporterer en fil med lavere nummer (eller ingen) på nytt |
| `route` | den matchede rute-id-en, eller `null` |
| `event_copies`, `event_kinds` | hvor mange kopier av løpets eget lag som ble plassert, og deres typer |
| `hidden` | kopier i den frie verdenen som ble utelatt fordi løpet fjerner dem |
| `venue` | venue-bakkemodellene kjøringen går gjennom |
| `layers` | de påslåtte lagene som ble plassert |

## Hva det koster

Grove størrelsesorden:

| Bane | Resultat |
|---|---|
| en kort landeveisbane | noen hundre tusen terrengtrekanter, over en million plasserte; sekunder, under 100 MB |
| en lang punkt-til-punkt-sprint | korridoren er en liten del av boksen rundt den; omtrent et minutt, noen hundre MB |
| en bybane | tusenvis av barrierer, rekvisitter og skilt, og hele bygninger; med det automatiske budsjettet opptil flere hundre MB |

En kvadratkilometer åpen terreng i det åpne kartet er omtrent en million trekanter.

## Kontroller bak dette

Dette er målinger gjort mens leseren ble skrevet, slik kildekoden sier. De kjøres ikke på nytt av
testene med mindre spillet er installert.

- På testbanen ligger bilen omtrent på sin kjørehøyde over den uttrukne bakken (median under 0,2 m).
- Hver samplede flis ligger innenfor den 512 m store firkanten navnet forutsier.
- Påfølgende plasseringer av barrierer ligger nøyaktig 4 m fra hverandre, og de fleste barriereender
  ligger innen 5 cm fra neste starts.
- Kanter ligger noen centimeter over den uttrukne bakken, med kanten opp, innen 5 m av kjøringen (også en
  test mot installert spill, se [Utvikling](development.md)).

## Tegnes ikke

- Trær og busker med mindre `--trees`. Gress og publikum aldri (spillet tegner dem som sprites).
- Et løps egne modeller som banen ikke leverer (se [Løpets eget lag](#the-races-own-layer)).
- Projiserte dekalmaterialer på modeller.
- Skiltkopier som er alfa-blandet over sin tavle, blir ugjennomsiktige.
- Bakkefargen er en rekonstruksjon av hvor asfalt, gress og skog er, ikke spillets egne terrengmaterialer.
