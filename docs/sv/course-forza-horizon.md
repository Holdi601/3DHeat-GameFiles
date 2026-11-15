---
title: Forza Horizon
lang: "sv"
source: course-forza-horizon.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Exportera en bana: Forza Horizon

Forza-exporten läser banan direkt ur spelets ForzaTech-arkiv: terräng där väg, vall
och gräs skiljs åt, en markstruktur inbakad från spelets egna markkartor, och varje
placerad modell i sin egen textur (kantstenar, räcken, däckväggar, skyltar, rekvisita,
byggnader). Den hittar också vilket av spelets lopp varvet kördes på, och lägger till
det spelet levererar för just det loppet (dess händelselager: barriärer, tält, portaler,
läktare, flaggor), och marken på varje venue som körningen passerar, till exempel ett
stadions golv.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Källor: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Containerformaten själva finns på [ForzaTech](reader-forzatech.md).

## Hitta det installerade spelet

Ingen ska behöva skriva en sökväg som
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, så sökvägen räknas ut:

1. **Steam-bibliotek.** Steams `config\libraryfolders.vdf` läses från
   `C:\Program Files (x86)\Steam` eller `C:\Program Files\Steam`, och varje `"path"`-post
   i den är ett bibliotek. Varje biblioteks `steamapps\common` söks.
2. **Microsoft Store.** `C:\XboxGames` söks om den finns. Där ligger spelet ett steg
   längre ner, i `<game>\Content`.
3. En **spelmapp** är varje underordnad till dessa mappar som har en mapp
   `media\Tracks`, oavsett namn.
4. En **banmapp** är varje mapp under `media\Tracks` som innehåller en
   `GeoChunk0.minizip`. Den räknas efter innehållet, inte namnet, så en bana under ett
   namn ingen har sett ännu hittas ändå.

Om spelet ligger någon annanstans, ange banmappen med `--track`; se
[Felsökning](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` hoppar över allt detta.

En banmapp innehåller det exporten läser:

| Fil | Vad den är |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arkiven: varje modell, textur och placeringsfil, utan namn inuti |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | en rad per arkivpost, i postordning: den enda källan till namn |
| `AssetManifest.xml` | varje textur banan levererar, med den hash som material refererar till den med |

## Vilken bana

Ett spel levererar fler än en banmapp (den öppna världen, ett garage eller två). Rätt
väljs efter **koordinater, inte namn**:

- Varvets begränsningslåda, vidgad med `--margin`, är frågan.
- För varje banmapp läses de fyra `ChunkContentsMiniZip*.txt`-manifesten som text, utan
  att något arkiv öppnas. Varje terrängkakelnamn
  (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) bär sin rutnätsposition. Verktyget
  räknar hur många olika kakel som ligger inom lådan.
- Banan med flest kakel där vinner. Om ingen bana har några avbryts exporten med
  "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's
  own metres, as its telemetry reports them."

En hel bana svarar på väl under en sekund. En namnmatchning kan välja fel karta, och en
fel karta ser lika trovärdig ut som den rätta.

Konsolen skriver `on <track>, in <game folder>`.

## Vilket lopp

Spelet levererar varje lopp som en rutt med ett nummer, dess **ruttid**. Två filer hör
till varje rutt:

| Fil | Vad den innehåller |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | loppets AI-körlinje: en nod på 56 byte från byte `0x60`, nodantalet vid `0x24`, där varje nod börjar med sin position (x, y, z) i spelets meter |
| `media\Stripped\gs\<map>\routedefinitions.zip` | en `route<id>_<map>.rtd` per lopp: vanlig XML som listar vad loppet lägger till i världen och vad det tar bort (se [Loppets eget lager](#the-races-own-layer)) |

Varvet matchas mot en rutt genom att jämföra det med varje AI-linje vars låda överlappar
varvets:

- Från varje varvsprov, avståndet till linjens närmaste punkt; och från varje punkt på
  linjen, avståndet till närmaste varvsprov.
- De två medianerna adderas. Rutten med minst summa vinner om summan är under **30 m**
  (`MATCH`).
- Båda riktningarna behövs: en kort sprint ligger längs en lång rutt som använder samma
  väg, och ett långt varv täcker en kort rutt.

Konsolen skriver `the game's route <id> (driven line within <n> m of it)`, eller att ingen
rutt matchar. Utan matchning placeras bara den fria världen.

## Terräng

Så hittas terrängen (i `forzaterrain.py`):

- Manifesten anger terrängen som ett rumsligt index:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- De två talen är rutnätskoordinater som **steg om 1023**, och varje rutnätssteg är ett
  **512 m**-kakel. Kakel `x-2046` är `-2046 / 1023 = -2`, vilket börjar vid
  `-2 * 512 = -1024` m. Läser man namnen som meter missar varje uppslag med en faktor två
  och ger ändå terräng, från fel del av kartan.
- Ett kakel kan förekomma tre gånger: vanligt, `_cb` och `_ul`. Alla tre täcker samma
  mark. Ett tas per kakel, i den ordningen, eftersom sammanslagning skulle tredubbla
  geometrin till sammanfallande ytor.
- Ett kakel läses bara om det rör varvets låda **och** korridoren. Ett kakel som
  korridoren inte rör packas aldrig upp.
- Varje `.modelbin` i ett valt kakel avkodas på **detaljnivå 0 bara**. Ett kakel bär fyra
  nivåer över samma mark, och om man exporterade alla skulle samma kvadratmeter hamna
  fyra gånger i filen.
- Varje mesh bär sin egen världsskala och förskjutning, så ett kakel landar där spelet
  lägger det utan någon instanstransform. Trianglar vars fotavtryck överlappar lådan
  behålls, sedan bara de som når in i korridoren.
- En mesh i ett format läsaren vägrar skippas och räknas (`N meshes could not be read`),
  så ett tunt resultat säger varför.

Terrängsammanfattningen skriver antalet hörn, trianglar, meshar och kakel samt
x/y/z-utsträckningen.

### Väg, vall, terräng, markeringar, vatten

Materialnamn säger inte var vägen är. Runt en bana använder 94 % av marken ett
vägshader-material, eftersom terräng nära en väg ritas med det, och shadern avgör asfalt
eller gräs per pixel. Så:

| Slag | Avgörs av |
|---|---|
| vägremsa | **hörnlayouten**: vägremsor är den enda marken med en andra UV-uppsättning (kanal 1); en triangel vars tre hörn alla har den är väg |
| asfalt kontra vall | inom en vägremsa, kakelns **asfaltsmask** i triangelns tyngdpunkt: 0,5 eller mer är `road`, mindre är `verge` |
| markeringar | materialnamn som matchar `whiteline`, `yellowline` eller `decal` |
| däckspår | materialnamn som matchar `tyremark` eller `skid` (kontrolleras före markeringar, eftersom däckspår levereras som `tyremark_decal_*`) |
| vatten | materialnamn som matchar `water`, `lake`, `river`, `paddy`, `ocean` eller `sea` |
| terräng | allt annat |

Mätt på testbanans inspelade varv hamnar nästan alla prov på vägremsetrianglar, och den
stora majoriteten på asfaltdelen när masken har skilt av vallen.

Asfaltmasken finns bara när markens texturer bakas. Med `--no-textures`, eller för ett
kakel vars kartor saknas, förblir vägremsorna hela som `road` och ingen vall skiljs av.
Saknade kartor kostar detaljer, aldrig geometri.

### Målade lager lyfts

Filmarkeringar och däckspår levereras som egna trianglar som ligger exakt i vägen. Spelet
ritar dem med ett djupbias. Ritas de som de är slåss väg och färg om varje pixel.
Exporten ger varje markerings- och däckspårsdel en egen kopia av sina hörn, lyft **5 cm**
(`DECAL_LIFT`) längs ytnormalen, så att vägen under den inte lyfts också.

### Normaler

Terrängnormaler kommer från arkivet. Normalens x lagras som positionens fjärde short, och
y och z i attributet `NORMAL` (se [ForzaTech](reader-forzatech.md)). Om något hörn i
uttaget saknar normal, räknas normaler för hela marken ut från trianglarna i stället.

## Markens textur

Varje terrängkakel levererar tre kartor som täcker dess 512 m-kvadrat, i fem upplösningar
(`_quality1` till `_quality5`, den största 2048 px, vilket är 25 cm per pixel):

| Karta | Filnamnsmönster | Vad den innehåller (uppmätt) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detaljnormal (x, z). A: lägre på asfalt och på ojämn mark |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | skiktvikter. B: hög på asfalt (239 på den körda linjen, 165 bredvid den) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: låg på asfalt (147 mot 215). B: stiger i skog |

Ingen av dem är en färgfotografi. De är indata som spelets terrängshader blandar sina
materiallager med, och de lagren läses inte. Så den inbakade texturen är **en tolkning,
inte en kopia av spelets utseende**. Den behåller *var* varje slags mark finns, på 25 cm,
och målar den i fasta färger:

| Mark | Linjärt RGB | Vikt |
|---|---|---|
| gräs (kort, nära banan) | 0,30, 0,44, 0,18 | basen |
| ojämnt (längre ut) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| skog | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Båda kartorna måste vara överens för asfalt. Endera ensam lämnar grå fläckighet i gräset
där blockkompressionen ringar. Resultatet skuggas av huvudkartans detaljnormal mot ett
fast ljus (`0.55 + 0.6 * lambert`), så kantstensläppar, slänter och hjulspår läses som
relief, och skrivs som 8-bitars sRGB.

Orientering: pixelrad 0 är kakelns **norra** kant (största z), kolumn 0 dess **västra**
kant (minsta x). Det fanns genom att projicera inspelade varv på asfaltmasken på alla
åtta sätt en kvadrat kan vändas eller roteras. Exakt ett sätt lägger dem på asfalt.
UV:erna följer av det: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Kartorna läses i bästa tillgängliga upplösning upp till kvalitet 5 och skalas till
huvudkartans storlek. Om färgbilden är större än `--texture-size` krymps den sedan till
den storleken med Lanczos-filtrering. Asfaltmasken behålls alltid i full upplösning,
eftersom den avgör geometrin. `--season` väljer kartorna `x<season>x`. Ett kakel utan
kartor för den säsongen ritas i platta färger, och konsolen rapporterar
`N without maps`.

## Placerade modeller

Terrängen bär sin egen världsposition. Ingenting annat gör det. Var varje kopia av en modell
står registreras i `.pgeo`-placeringsfiler, en per kategori per rumslig cell:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Postlayouten finns på
[ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Vad läses

- Placeringsfiler filtreras **efter namn**: cellstorleken och cellpositionen i sökvägen
  ger cellens kvadrat (`x * size` till `(x + 1) * size`), och bara celler som överlappar
  varvets låda, i en önskad kategori, öppnas.
- Kategorier som standard: `barriers`, `props`, `signs`, `buildings`, `infrastructure`,
  `bridges`, `rocks`, `evolving`. `--trees` lägger till `trees`, `bushes` och
  `smashables`. Dessa läses aldrig: `grasstemplate`, `crowdtemplate` och `cwdspline`
  (gräs och åskådare: spelet ritar dem som animerade sprites, det finns ingen geometri).
- Varje fil hör till ett **lager**, läst från dess namn efter `c<size>_<category>_`. Ett
  detaljnivåord (`do`, `so`, `ulc`, `ulp`, `cwd`) och ett valfritt sektionsnummer är den
  fria världen. Allt annat är ett lager spelet slår på: ett runtime-lager (`rt_0`), en
  aktivitet (`_tag_<name>_`), ett samlarföremål, allt som ligger under `evolving`. Ett lager
  som namnger rutter (`rt_x<id>`, till exempel `rt_x1023_x2201`) hör bara till de loppen,
  och läses bara när varvet matchade ett av dem. Se [Påslagna lager](#switched-on-layers).
- En kopia behålls om dess position ligger inom lådan och inom korridoren. Exakta
  upprepningar (samma position och orientering till millimetern, listade av två
  grannceller) slås ihop.
- **Kantstenar** är rekvisita vars modellnamn börjar med `road_gen_rum` (vibrationsremsor).
  De skrivs som `ground:kerbs`, förenklas aldrig och utelämnas aldrig, eftersom ett varv
  mäts mot dem.

| Kategori | Del | Reservfärg (utan textur) |
|---|---|---|
| kantstenar | `ground:kerbs` | 0,60, 0,12, 0,10 |
| räcken | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekvisita | `structure:props` | 0,45, 0,35, 0,25 |
| skyltar | `structure:signs` | 0,70, 0,70, 0,70 |
| byggnader | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktur | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| broar | `structure:bridges` | 0,45, 0,45, 0,45 |
| stenar | `structure:rocks` | 0,30, 0,28, 0,25 |
| sönderslagbara | `structure:smashables` | 0,12, 0,22, 0,06 |
| träd, buskar | `structure:trees` | 0,10, 0,20, 0,05 |

### Modellens geometri

En placerad `<model>_3D` refererar till modellfilerna `<model>_cluster###.i.modelbin`
(upp till ett dussin). Varje triangel bär en mask över de detaljnivåer den hör till:

- En modells nivåer är dess trianglar som uttryckligen är markerade för den nivån. Nivåerna
  löper i följd från 0, finast först.
- Trianglar markerade `0xFFFF` (varje nivå) är de brytbara bitarna, till exempel en
  räckespelares stolpar eller en däckstapels enskilda däck. De överlappar hela modellen,
  och spelet ritar dem i stället för den när den slagits sönder. De används bara av en
  modell utan någon uttryckligen markerad nivå.
- Undermeshar vars materialshader är en projicerad **dekal** utelämnas.

Varje kopia placeras med sin position, sina x- och y-axlar från posten (z = x korsat med y),
och sin skala. Normaler transformeras med skalans inverterade.

### Vilken textur

Ett material anger inte sina texturer. Det listar dem som hashar, och banans
`AssetManifest.xml` kopplar varje hash (`SourceHash`) till ett texturnamn. Bara
`<Textures>`-sektionen läses, som slutar vid `</Textures>` i en fil som kan vara tiotals
megabyte. Sedan:

1. Platsen `0x88B483AA` är basfärgen i den standardmiljöshadern (varje samplat material).
   Om materialet binder en textur där, används den.
2. Annars avgör texturens egen typ, vilket är ordet före dess GUID:
   `_bclr_`, sedan `_diff_`, sedan `_colour_`.
3. Terrängkartor (`mainmap`, `submap`, `autogloss`) och tintpaletter (`tint`,
   `worldtint`) färgar aldrig en modell.

En modell färgas alltså av vad dess material binder, inte av en textur som heter som
modellen. Till exempel använder `bar_rur_armco_crct_02_c` `..._02_a`:s textur.

Texturen läses från arkiven i den minsta upplösningen som är minst **256 px** över
(`MODEL_TEXTURE`), krymps till 256 om den är större, och lagras som RGB-JPEG i `.glb`-filen.
En räckes färg på 256 px för fyra meter är 1,6 cm per pixel, och runt 80 sådana texturer
får plats i visarens atlas bredvid markkakelen.

**Säsonger.** `--season` byter en textur mot sin säsongstvilling med namnet, utan att GUID:n
räknas (`..._xsummerx_bclr` till `..._xwinterx_bclr`, eller `..._bclr` till
`..._winter_bclr`), när banan har en sådan. Med `--season winter` används också en
undermeshs vintermaterial där dess variantTabell anger ett.

**Varianter.** En undermeshpost börjar med en tabell över `(summer, winter)`-material,
ett per utseende en kopia kan bära: fem tryck för en reklamskylt, sex färger för en däckstapel.
Varje placeringspost anger vilken variant kopian bär. En undermesh med färre varianter
än modellen upprepar sina egna.

**Platshållarblocket.** Delade byggnadsatlaser reserverar ett fast RGB-block (255, 64, 0)
för ytor som byggnadsshadern färgar från andra texturer. Om mer än en tjugondel av en
textur ligger inom 12 nivåer från den färgen, målas blocket om i texturens egen
medelfärg. Annars blir en stad orange.

### Genomskinliga ytor

Kedjestängsel och nät är enkla fyrhörningar med hål i texturens alfa. Ritade fasta blir ett
staket en vägg över banans utsikt. Ytor vars materialshader matchar `alphatest`,
`alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` eller `tree` testas:

- Texturens opacitet medelvärdesbildas över ett rutnät på 32 x 32.
- Per yta (alla utskurna trianglar som delar en textur) samplas fyra punkter per triangel
  i UV-rymden och vägs efter triangelns UV-area.
- Om medelopaciteten är minst 0,05 och under **0,5** utelämnas hela ytan. Under 0,05 betyder
  alfan tydligt något annat för dess shader (en varningsskylt som samplar 0,01), och ytan
  behålls fast.
- En modell vars alla ytor utelämnades rapporteras:
  `N models left out as see-through (mostly holes in their texture)`.

Verktyget bedömer hela ytan i stället för en triangel i taget. Bedömd per triangel
överlevde hälften av varje fyrhörning och stängslen blev rader av tänder.

### Byggnader ritade hela

En stad bygger sina byggnader av modulära delar: hundratusentals kring en gatbana, tiotals
miljoner trianglar även på grövsta nivå. Att utelämna delar en i taget lämnade ensamma
väggplattor stående. Spelet levererar också hela-byggnads-ersättare i `scene\hlod_tier_1\`,
en mesh per byggnad (stammen `hlod_tier_1_*`), redan i världskoordinater som terrängen:

- Varje ersättares världslåda läses från dess meshs positionslåda (en huvudläsning, ingen
  avkodning). Det tar sekunder för en hel karta.
- Ersättare som rör varvets låda och korridoren används.
- Varje `buildings`-del vars position ligger inom en ersättares fotavtryck (plus 0,5 m) tas
  bort, och ersättaren ritas i stället. Dess avstånd till körningen mäts till byggnadens
  närmaste kant.
- Sammanfattningen säger `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Påslagna lager

Det en påslagen lager placerar exporteras, men skilt från den fria världen, så att visaren
kan visa eller dölja det:

| Lager | Del |
|---|---|
| den fria världen | `structure:<category>` (som förut) |
| ett lager som namnger det matchade loppets rutt | `structure:event_<category>` |
| något annat påslaget lager | `structure:layer_<category>` |

Sammanfattningen räknar dem: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modeller redan i världskoordinater

Några slag av modeller finns inte i någon placeringsfil. Deras meshar bär sin egen världs-
position, precis som terrängen, så ingenting behöver placera dem:

| Mapp under `scene\models\` | Vad den är | Del |
|---|---|---|
| `plots` | ett venues egen mark: ett stadions golv och innerplan, ett festivalområde, ett torg | `ground:venue` |
| `plinths` (och varje modell med namnet `floor`, `ground` eller `road`) | mark en gata är dekorerad med: planteringar, trappsteg, en parks plattor | `ground:plinths` |
| `hda_infrastructure` (broar) | procedurellt byggda broar | `structure:bridges` |

- En modell räknas som i världskoordinater när mitten av dess låda ligger mer än **300 m**
  (`WORLD_REACH`) från sin egen origo. Modeller som placeras av placeringsfilerna ligger
  inom ett par hundra meter från sina.
- Ritas inte: ockluderare, kablar spända längs vägarna, havets bakgrund, taken och
  ockluderarna på modulära byggnader (ersättarna ritar dem), kollisions- och vattenvolymer.
- Varje läses från lådan för dess meshar (en huvudläsning), några sekunder för en hel karta,
  en gång per körning.
- Markdelar grövs aldrig och utelämnas aldrig för att passa budgeten, precis som kantstenar.

**Ett venue skärs i sin helhet.** När körningen rör ett venues egen mark (`ground:venue`)
vidgas korridoren till hela den markens fotavtryck plus `--margin`, så att läktarna,
väggarna och räckena runt ett stadion kommer med, inte bara den remsa varven använde.
Konsolen skriver `through a venue (<model names>): cutting all of its ground, <n> km2`.
Plinths vidgar inte klippet.

### Detalj och budgeten

Avståndsband, budget och vilka kopior som går när budgeten är för liten finns på
[Detaljnivåer och budgeten](detail-budget.md).

### Placeringssammanfattning

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

## Loppets eget lager

Många lopp levererar saker som inte finns i den fria världen: betongväggar och staket som
stänger av sidovägar, däckstaplar, tält, en startportal, läktare, flaggor, banderoller.
Varje lopp listar dem i sin ruttdefinition (`route<id>_<map>.rtd` i `routedefinitions.zip`,
vanlig XML i ett vanligt zip-arkiv):

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

- **Vad som läggs till.** Varje instans placeras som en kopia från en placeringsfil. Transformens
  16 tal är fyra rader: modellens x-, y- och z-axlar (var och en skalad) och dess position i
  spelets meter. Den tredje raden är korsprodukten av de två första. `Material` är varianten
  kopian bär. Delen är `structure:event_<kind>`, där `<kind>` är mappen under
  `scene\models\` (barriers, props, infrastructure, signs; allt annat räknas som props), och
  noden bär glTF-extrat `{"layer": "event", "route": <id>}`.
- **Vad som tas bort.** En kopia i den fria världen som står inom **0,1 m** från en dold
  tillgångs position utelämnas. En dold tillgång som står i origo är en modell i världs-
  koordinater; dess instans-GUID slås upp i banans `AssetManifest.xml` (listan `<Models>`:
  en modells källa, sedan GUID:erna för dess kopior) för att namnge den.
- **Mark som loppet döljer behålls.** Ett lopp som döljer ett venues mark lägger en egen yta
  där. När den ytan inte finns bland modellerna som banan levererar, behålls den dolda marken
  som det närmaste till det man kör på, och sammanfattningen säger det
  (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Ritas inte, men räknas.** Publikmarkörer (`crowd_proxies`: spelet ritar publiken som
  sprites utifrån dem) och kollisionssplines (`.splinecol`). Konsolen listar dem:
  `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Ruttillgångar som banan inte levererar en modell för (ljusglöd, vissa skyltar, innehåll som
  spelet strömmar in) namnges i `placed names have no model in the archives`.

Bara kopior inom korridoren placeras, som för allt annat.

## Skriva filen

Delarna skrivs i den här ordningen: per kakel `terrain`, `verge`, `road` (var och en med kakelns
bild), sedan `water`, `tyre marks`, `markings` (platta, de två sista lyfta), och sedan varje
placerad del sorterad efter namn. Koordinaterna är spelets egna (meter, Y uppåt). Se
[Utdataformat](output-format.md).

Filen anger vad den innehåller i sin glTF-`asset.extras`:

| Fält | Betydelse |
|---|---|
| `course_format` | `2`: loppets eget lager, venues och världskoordinatsmodeller finns i den. [`courses`](commands.md#courses) exporterar en fil med lägre nummer (eller ingen) på nytt |
| `route` | ruttens id som matchades, eller `null` |
| `event_copies`, `event_kinds` | hur många kopior av loppets egna lager som placerades, och deras slag |
| `hidden` | kopior i den fria världen som utelämnades för att loppet tar bort dem |
| `venue` | venue-markmodellerna som körningen passerar |
| `layers` | de påslagna lager som placerades |

## Vad det kostar

Grova storleksordningar:

| Bana | Resultat |
|---|---|
| en kort landsvägsbana | några hundratusen markettrianglar, över en miljon placerade; sekunder, under 100 MB |
| en lång punkt-till-punkt-sprint | korridoren är en liten del av lådan runt den; ungefär en minut, några hundra MB |
| en stadsgatbana | tusentals räcken, rekvisita och skyltar, och hela byggnader; med den automatiska budgeten upp till flera hundra MB |

En kvadratkilometer öppen världsterräng är ungefär en miljon trianglar.

## Kontroller bakom det

Det här är mätningar gjorda när läsaren skrevs, så som sagt i källkoden. De körs inte om av
testerna om inte spelet är installerat.

- På testbanan ligger bilen ungefär sin körhöjd över den uttagna marken (median under 0,2 m).
- Varje provtaget kakel ligger inom den 512 m-kvadrat dess namn förutsäger.
- Efter varandra följande räckesplaceringar ligger exakt 4 m från varandra, och de flesta
  räckesändar ligger inom 5 cm från nästa starts.
- Kantstenar ligger några centimeter över den uttagna marken, med framsidan uppåt, inom 5 m från
  körningen (även ett test mot installerat spel, se [Utveckling](development.md)).

## Ritas inte

- Träd och buskar om inte `--trees`. Gräs och publik aldrig (spelet ritar dem som sprites).
- Ett lopps egna modeller som banan inte levererar (se [Loppets eget lager](#the-races-own-layer)).
- Projicerade dekalmaterial på modeller.
- Skyltkopior som är alfablandade över sin skylt blir ogenomskinliga.
- Markfärgen är en rekonstruktion av var asfalt, gräs och skog ligger, inte spelets egna terrängmaterial.
