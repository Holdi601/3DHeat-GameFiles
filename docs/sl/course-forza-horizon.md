---
title: Forza Horizon
nav_order: 1
lang: "sl"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Izvoz tečaja: Forza Horizon {#course-export-forza-horizon}

Izvoz Forze prebere stezo naravnost iz arhivov ForzaTech igre: teren, kjer sta cesta,
rob in trava ločeni, teksturo tal, zapečeno iz lastnih zemljevidov tal igre, in vsak
postavljen model v lastni teksturi (robniki, varnostne ograje, zidovi iz gum, znaki,
rekviziti, stavbe). Najde tudi, na kateri dirki igre je bil lap odpeljan, in doda, kar
igra izpusti samo za to dirko (njen dogodkovni sloj: ovire, šotore, portale, tribune,
zastave), ter tla vsakega prizorišča, skozi katero vožnja gre, na primer tla stadiona.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Viri: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Sami formati vsebnikov so na [ForzaTech](reader-forzatech.md).

## Iskanje nameščene igre {#finding-the-installed-game}

Nihče ne bi smel vpisovati poti, kot je
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, zato se pot izračuna sama:

1. **Knjižnice Steam.** Datoteka `config\libraryfolders.vdf` Steama se prebere iz
   `C:\Program Files (x86)\Steam` ali `C:\Program Files\Steam`, vsak vnos `"path"` v njej
   pa je knjižnica. Pregleda se `steamapps\common` vsake knjižnice.
2. **Microsoft Store.** Pregleda se `C:\XboxGames`, če obstaja. Tam je igra eno raven
   globlje, v `<game>\Content`.
3. **Mapa igre** je vsak otrok teh map, ki ima mapo `media\Tracks`, ne glede na ime.
4. **Mapa steze** je vsaka mapa pod `media\Tracks`, ki vsebuje `GeoChunk0.minizip`.
   Šteje se po vsebini, ne po imenu, zato se najde tudi steza pod imenom, ki ga še
   nihče ni videl.

Če je igra drugje, podajte mapo steze z `--track`; glejte
[Odpravljanje težav](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` preskoči vse to.

Mapa steze vsebuje to, kar izvoz bere:

| Datoteka | Kaj je |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arhivi: vsak model, tekstura in datoteka postavitev, brez imen v njih |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | ena vrstica za vnos arhiva, po vrstnem redu vnosov: edini vir imen |
| `AssetManifest.xml` | vsaka tekstura, ki jo steza dostavlja, z zgoščeno vrednostjo, s katero se nanjo sklicujejo materiali |

## Katera steza {#which-track}

Igra dostavlja več map stez (odprti svet, garažo ali dve). Prava se izbere po
**koordinatah, ne po imenu**:

- Omejevalna škatla lapa, razširjena z `--margin`, je vprašanje.
- Za vsako mapo steze se štirje manifesti `ChunkContentsMiniZip*.txt` preberejo kot
  besedilo, brez odpiranja arhiva. Vsako ime ploščice terena
  (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) nosi svoj položaj v mreži. Orodje
  prešteje, koliko različnih ploščic leži v škatli.
- Steza z največ ploščicami zmaga. Če nobena nima nobene, se izvoz ustavi z napako
  "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's
  own metres, as its telemetry reports them."

Cela steza odgovori v manj kot sekundi. Ujemanje po imenu bi lahko izbralo napačen
zemljevid, napačen pa je videti prav tako verjetno kot pravi.

Konzola izpiše `on <track>, in <game folder>`.

## Katera dirka {#which-race}

Igra vsako svojo dirko dostavlja kot pot s številko, njenim **ID poti**. Vsaka pot ima
dve datoteki:

| Datoteka | Kaj vsebuje |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | AI vožnjina linija dirke: vozlišče dolžine 56 bajtov od bajta `0x60`, število vozlišč pri `0x24`, vsako vozlišče se začne s svojim položajem (x, y, z) v metrih igre |
| `media\Stripped\gs\<map>\routedefinitions.zip` | ena datoteka `route<id>_<map>.rtd` za vsako dirko: navaden XML, ki našteje, kaj dirka doda svetu in kaj mu vzame (glejte [Lastni sloj dirke](#the-races-own-layer)) |

Lap se ujema s potjo tako, da se primerja z vsako AI linijo, katere škatla se prekriva z
lapovo.

- Od vsakega vzorca lapa razdalja do najbližje točke linije; in od vsake točke linije
  razdalja do najbližjega vzorca lapa.
- Obe mediani se seštejeta. Pot z najmanjšo vsoto zmaga, če je vsota manjša od
  **30 m** (`MATCH`).
- Potrebni sta obe smeri: kratek sprint leži vzdolž dolge poti, ki uporablja isto cesto,
  dolg lap pa pokrije kratko pot.

Konzola izpiše `the game's route <id> (driven line within <n> m of it)` ali da se nobena
pot ne ujema. Brez ujemanja se postavi samo svet proste vožnje.

## Teren {#terrain}

Kako je teren najden (v `forzaterrain.py`):

- Manifesti imenujejo teren kot prostorski indeks:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Obe številki sta mrežni koordinati, ki **korakata po 1023**, vsak korak mreže pa je
  ploščica **512 m**. Ploščica `x-2046` je `-2046 / 1023 = -2`, ki se začne pri
  `-2 * 512 = -1024` m. Če imena beremo kot metre, vsako iskanje zgreši za faktor dve
  in še vedno vrne teren, iz napačnega dela zemljevida.
- Ploščica se lahko pojavi trikrat: navadna, `_cb` in `_ul`. Vse tri pokrivajo isto
  zemljo. Za ploščico se vzame ena, v tem vrstnem redu prednosti, ker bi združevanje
  potrojilo geometrijo v sovpadajoče ploskve.
- Ploščica se prebere samo, če se dotika lapove škatle **in** koridorja. Ploščica, ki se je
  koridorja ne dotika, se nikoli ne dekompresira.
- Vsak `.modelbin` izbrane ploščice se dekodira samo na **stopnji podrobnosti 0**.
  Ploščica nosi štiri stopnje nad isto zemljo, in če bi jih izvozili vse, bi isti
  kvadratni meter bil v datoteki štirikrat.
- Vsaka mreža nosi svoje merilo in premik v svetovnem prostoru, zato pristane tam, kjer jo
  igra postavi, brez transformacije primerka. Trikotniki, katerih odtis se prekriva s
  škatlo, se ohranijo, nato samo tisti, ki segajo v koridor.
- Mreža v obliki, ki jo bralnik zavrne, se preskoči in prešteje
  (`N meshes could not be read`), zato tanek rezultat pove, zakaj.

Povzetek terena izpiše število oglišč, trikotnikov, mrež, ploščic in razpon x/y/z.

### Cesta, rob, teren, oznake, voda {#road-verge-terrain-markings-water}

Imena materialov ne morejo povedati, kje je cesta. Okoli dirkališča 94 % tal uporablja
material cestne senčilnike, ker se teren blizu ceste riše z njim, senčilnik pa na vsaki
piki odloči, asfalt ali trava. Zato:

| Vrsta | Določi |
|---|---|
| pas ceste | **postavitev oglišč**: pasovi ceste so edina tla z drugim nizom UV (kanal 1); trikotnik, katerega vsa tri oglišča ga imajo, je cesta |
| asfalt proti robu | znotraj pasu ceste maska asfalta ploščice v težišču trikotnika: 0,5 ali več je `road`, manj je `verge` |
| oznake | ujemanje imena materiala z `whiteline`, `yellowline` ali `decal` |
| sledi pnevmatik | ujemanje imena materiala z `tyremark` ali `skid` (preverjeno pred oznakami, ker se sledi pnevmatik pošiljajo kot `tyremark_decal_*`) |
| voda | ujemanje imena materiala z `water`, `lake`, `river`, `paddy`, `ocean` ali `sea` |
| teren | vse drugo |

Na laps testne steze je skoraj vsak vzorec pristal na trikotnikih pasu ceste, velika
večina pa na asfaltnem delu, ko je maska odcepila rob.

Maska asfalta obstaja samo, kadar se pečejo teksture tal. Z `--no-textures` ali za
ploščico, katere zemljevidi manjkajo, ostanejo pasovi ceste celi kot `road` in rob se ne
odcepi. Manjkajoči zemljevidi stanejo podrobnost, nikoli geometrije.

### Naslikane plasti so dvignjene {#painted-layers-are-lifted}

Oznake pasov in sledi pnevmatik se pošiljajo kot lastni trikotniki, ki ležijo točno na
cesti. Igra jih riše z odmikom globine. Če bi jih narisali takšne, bi se cesta in barva
prepirali za vsak piksel. Izvoz da vsaki oznaki in vsakemu delu sledi pnevmatik lastno
kopijo njenih oglišč, dvignjeno za **5 cm** (`DECAL_LIFT`) vzdolž normale ploskve, da
cesta pod njo ni dvignjena tudi.

### Normale {#normals}

Normale terena pridejo iz arhiva. X normale je shranjen kot četrti kratki element
položaja, njen y in z pa v atributu `NORMAL` (glejte [ForzaTech](reader-forzatech.md)).
Če kateremu oglišču v izvlečku manjka normala, se normale za vsa tla izračunajo iz
trikotnikov.

## Teksture tal {#the-ground-texture}

Vsaka ploščica terena dostavlja tri zemljevide, ki pokrivajo njen kvadrat 512 m, v
petih ločljivostih (`_quality1` do `_quality5`, največja 2048 px, to je 25 cm na piko):

| Zemljevid | Vzorec imena datoteke | Kaj vsebuje (kakor izmerjeno) |
|---|---|---|
| glavni | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: podrobna normala (x, z). A: nizko na asfaltu in na grobih tleh |
| podrejeni | `submap_x<X>_z<Z>_x<season>x_diff` | uteži plasti. B: visoko na asfaltu (239 na vozni črti, 165 ob njej) |
| sijaj | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: nizko na asfaltu (147 proti 215). B: narašča v gozdu |

Nobeden od teh ni barvna fotografija. So vhodi, s katerimi senčilnik teren igre meša
svoje materialne plasti, teh plasti pa ni dekodirano. Zato je zapečena tekstura **razlaga,
ne kopija videza igre**. Ohrani *kje* je vsaka vrsta tal, pri 25 cm, in jo naslika v
fiksnih barvah:

| Tla | Linearni RGB | Utež |
|---|---|---|
| trava (kratka, blizu steze) | 0,30, 0,44, 0,18 | osnova |
| grobo (dlje) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| gozd | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Za asfalt se morata oba zemljevida strinjati. Če bi se držal samo eden, bi v travi
ostal sivi pikčasti vzorec tam, kjer stiskanje blokov zvoni. Rezultat je osvetljen z
podrobno normalo glavnega zemljevida proti fiksni svetlobi (`0.55 + 0.6 * lambert`), zato
robovi kamnov, bregovi in kolesnice berejo kot reliefi, in zapisan kot 8-bitni sRGB.

Usmerjenost: vrstica 0 piksla je **severni** rob ploščice (največji z), stolpec 0 pa
**zahodni** rob (najmanjši x). To je bilo ugotovljeno tako, da so bili posneti lapi
projicirani na masko asfalta na vseh osem načinov, na katere se kvadrat lahko obrne ali
zavrti. Natanko en način jih postavi na asfalt. Koordinate UV iz tega sledijo:
`u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Zemljevidi se preberejo v najboljši razpoložljivi ločljivosti do kakovosti 5 in
prevzorčijo na velikost glavnega zemljevida. Če je barvna slika večja od
`--texture-size`, se nato z Lanczosovim filtrom zmanjša na to velikost. Maska asfalta
je vedno v polni ločljivosti, ker odloča o geometriji. `--season` izbere zemljevide
`x<season>x`. Ploščica brez zemljevidov za to sezono je narisana v ploskih barvah, konzola
pa to sporoči kot `N without maps`.

## Postavljeni modeli {#placed-models}

Teren nosi svoj svetovni položaj. Nič drugega ga ne. Kje stoji vsaka kopija modela, je
zapisano v datotekah postavitev `.pgeo`, po ena za vsako kategorijo na prostorsko celico:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Postavitev zapisov je v
[ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Kaj se bere {#what-is-read}

- Datoteke postavitev se filtrirajo **po imenu**: velikost celice in položaj celice v poti
  dasta kvadrat celice (`x * size` do `(x + 1) * size`), odpirajo pa se samo celice, ki
  se prekrivajo z lapovo škatlo, v želeni kategoriji.
- Kategorije privzeto: `barriers`, `props`, `signs`, `buildings`, `infrastructure`,
  `bridges`, `rocks`, `evolving`. `--trees` doda `trees`, `bushes` in `smashables`. Tiste
  se nikoli ne berejo: `grasstemplate`, `crowdtemplate` in `cwdspline` (trava in
  gledalci: igra jih riše kot animirane sprite, geometrije ni).
- Vsaka datoteka pripada **plasti**, prebrani iz njenega imena po `c<size>_<category>_`.
  Stopenjska beseda (`do`, `so`, `ulc`, `ulp`, `cwd`) in neobvezna številka oddelka je
  svet proste vožnje. Vse drugo je plast, ki jo igra vklopi: izvajalna plast (`rt_0`),
  dejavnost (`_tag_<name>_`), zbiralni predmet, vse, kar je uvrščeno pod `evolving`. Plast,
  ki imenuje poti (`rt_x<id>`, na primer `rt_x1023_x2201`), pripada samo tem dirkam in se
  prebere samo, če se je lap ujel z eno od njih. Glejte [Vklopljeni sloji](#switched-on-layers).
- Kopija se ohrani, če je njen položaj znotraj škatle in znotraj koridorja. Natančne
  ponovitve (isti položaj in usmerjenost do milimetra, ki jih naštejeta dve sosednji celici)
  se združijo.
- **Robniki** so rekviziti, katerih ime modela se začne z `road_gen_rum` (vibracijski pasovi).
  Zapišejo se kot `ground:kerbs`, nikoli se ne poenostavijo in nikoli ne izpustijo, ker se
  lap meri glede nanje.

| Kategorija | Del | Rezervna barva (brez teksture) |
|---|---|---|
| robniki | `ground:kerbs` | 0,60, 0,12, 0,10 |
| ovire | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekviziti | `structure:props` | 0,45, 0,35, 0,25 |
| znaki | `structure:signs` | 0,70, 0,70, 0,70 |
| stavbe | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktura | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| mostovi | `structure:bridges` | 0,45, 0,45, 0,45 |
| skale | `structure:rocks` | 0,30, 0,28, 0,25 |
| razbijalni predmeti | `structure:smashables` | 0,12, 0,22, 0,06 |
| drevesa, grmovje | `structure:trees` | 0,10, 0,20, 0,05 |

### Geometrija modela {#the-models-geometry}

Postavljeno ime `<model>_3D` se nanaša na datoteke modela `<model>_cluster###.i.modelbin`
(do ducat). Vsak trikotnik nosi masko stopenj podrobnosti, katerim pripada:

- Stopnje modela so njegovi trikotniki, izrecno označeni za to stopnjo. Stopnje tečejo
  zvezno od 0, najbolj natančna najprej.
- Trikotniki, označeni z `0xFFFF` (vse stopnje), so lomljivi kosi, na primer stebrički
  ograje ali posamezne gume v kupu gum. Prekrivajo ves model, igra pa jih riše namesto
  njega, ko je razbit na koščke. Uporabljajo se samo pri modelu brez izrecno označene
  stopnje.
- Podmreže, katerih senčilnik materiala je projicirani **dekal**, se izpustijo.

Vsaka kopija se postavi s svojim položajem, svojima osema x in y iz zapisa (z = x krat y)
in svojim merilom. Normale se transformirajo z inverznim merilom.

### Katera tekstura {#which-texture}

Material ne imenuje svojih tekstur. Našteje jih kot zgoščene vrednosti, zemljevid
`AssetManifest.xml` steze pa vsako vrednost (`SourceHash`) preslika v ime teksture. Bere se
samo oddelek `<Textures>`, branje se ustavi pri `</Textures>` v datoteki, ki je lahko
dolga več deset megabajtov. Nato:

1. Reža `0x88B483AA` je osnovna barva v standardnem okoljskem senčilniku (vsak vzorčen
   material). Če material tam veže teksturo, se ta uporabi.
2. Sicer odloči vrsta same teksture, beseda pred njenim GUID: `_bclr_`, nato `_diff_`, nato
   `_colour_`.
3. Zemljevidi terena (`mainmap`, `submap`, `autogloss`) in paleti odtenkov (`tint`,
   `worldtint`) nikoli ne obarvajo modela.

Model je torej obarvan s tem, kar veže njegov material, ne z teksturo, poimenovano po
modelu. Na primer, `bar_rur_armco_crct_02_c` uporablja teksturo iz `..._02_a`.

Tekstura se prebere iz arhivov pri najmanjši ločljivosti, ki je vsaj **256 px** čez
(`MODEL_TEXTURE`), pomanjša na 256, če je večja, in shrani kot RGB JPEG v `.glb`. Barva
varovalne ograje pri 256 px za štiri metre je 1,6 cm na piko, približno 80 takih tekstur
pa se prilega atlasu pregledovalnika poleg ploščic tal.

**Sezone.** `--season` zamenja teksturo z njenim sezonskim dvojčkom po imenu, GUID se
ignorira (`..._xsummerx_bclr` v `..._xwinterx_bclr`, ali `..._bclr` v `..._winter_bclr`),
kadar ga steza ima. Z `--season winter` se zimski material podmreže uporabi tudi tam,
kjer ga njena tabela variant imenuje.

**Variante.** Zapis podmreže se začne s tabelo parov `(summer, winter)` materialov, po
enega za vsak videz, ki ga lahko kopija nosi: pet tiskov za reklamni pano, šest barv za
kup gum. Vsak zapis postavitve pove, katero varianto nosi kopija. Podmreža z manj
variantami, kot jih ima model, ponovi svoje.

**Blok za zamenjavo.** Skupni atlasi stavb rezervirajo trdni blok RGB (255, 64, 0) za
površine, ki jih senčilnik stavb obarva z drugih tekstur. Če je več kot dvajseti del
teksture v 12 stopnjah te barve, se blok prebarva v povprečno barvo teksture. Sicer bi
mesto prišlo ven oranžno.

### Prosojne površine {#see-through-surfaces}

Mrežice iz verig in mreže so posamezni četverokotniki z luknjami v alfa teksture. Če bi
bili narisani polni, bi bila ograja zid čez pogled na stezo. Površine, katerih senčilnik
materiala ustreza `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`,
`branch`, `bush` ali `tree`, se preizkusijo:

- Neprosojnost teksture se povpreči po mreži 32 x 32.
- Za vsako površino (vsak trikotnik z izrezom, ki deli isto teksturo) se štiri točke na
  trikotnik vzorčijo v prostoru UV in uteži z območjem UV trikotnika.
- Če je povprečna neprosojnost vsaj 0,05 in pod **0,5**, se celotna površina izpusti. Pod
  0,05 alfa za njen senčilnik jasno pomeni nekaj drugega (opozorilni znak, ki vzorči
  0,01), zato se površina ohrani polna.
- Model, katerega vse površine so bile izpuščene, se prijavi:
  `N models left out as see-through (mostly holes in their texture)`.

Orodje sodi celotno površino in ne posameznega trikotnika. Če bi sodilo vsak trikotnik
posebej, bi polovica vsakega četverokotnika preživela in ograje bi prišle ven kot vrste
zob.

### Stavbe v celoti {#buildings-drawn-whole}

Mesto gradi stavbe iz modularnih kosov: na enem ulični dirkalnici jih je na stotine tisoč,
desetine milijonov trikotnikov tudi pri njihovi najgrobejši stopnji. Če bi kose izpuščali
enega za drugim, bi ostale stati posamezne stene. Igra dostavlja tudi cele stavbe kot
nadomestke v `scene\hlod_tier_1\`, po eno mrežo na stavbo (osnova `hlod_tier_1_*`), že v
svetovnih koordinatah kakor teren:

- Svetovna škatla vsakega nadomestka se prebere iz omejitvene škatle njegove mreže (samo
  glava, ne dekodiranje). To traja sekunde za cel zemljevid.
- Uporabijo se nadomestki, ki se dotikajo lapove škatle in koridorja.
- Vsak kos `buildings`, čigar položaj pade znotraj tlorisa nadomestka (plus 0,5 m), se
  izpusti, namesto njega se nariše nadomestek. Njegova razdalja do vožnje se meri do
  najbližjega roba stavbe.
- Povzetek pravi `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Vklopljeni sloji {#switched-on-layers}

Kar postavi vklopljen sloj, se izvozi, a ločeno od sveta proste vožnje, da ga pregledovalnik
lahko pokaže ali skrije:

| Sloj | Del |
|---|---|
| svet proste vožnje | `structure:<category>` (kot prej) |
| sloj, ki imenuje pot ujete dirke | `structure:event_<category>` |
| vsak drug vklopljen sloj | `structure:layer_<category>` |

Povzetek jih šteje: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modeli že v svetovnih koordinatah {#models-already-in-world-coordinates}

Nekatere vrste modelov niso v nobeni datoteki postavitev. Njihove mreže nosijo lasten
svetovni položaj, kakor teren, zato jih nič ni treba postaviti:

| Mapa pod `scene\models\` | Kaj je | Del |
|---|---|---|
| `plots` | lastna tla prizorišča: tla in notranjost stadiona, festivalsko območje, trg | `ground:venue` |
| `plinths` (in vsak model z imenom `floor`, `ground` ali `road`) | tla, s katerimi je okrašena ulica: korita, stopnice, tlakovanje parka | `ground:plinths` |
| `hda_infrastructure` (mostovi) | proceduralno zgrajeni mostovi | `structure:bridges` |

- Model šteje za del svetovnih koordinat, kadar je sredina njegove škatle več kot **300 m**
  (`WORLD_REACH`) od njegovega izhodišča. Modeli, postavljeni z datotekami postavitev, so
  nekaj sto metrov od svojih.
- Ne narišejo se: zakrivala, kabli, napeti vzdolž cest, ozadje morja, strehe in zakrivala
  modularnih stavb (nadomestki te stavbe že risejo), kolizijske površine in prostornine
  vode.
- Vsak se prebere iz škatle svojih mrež (samo glava), nekaj sekund za cel zemljevid, enkrat
  na zagon.
- Deli tal se nikoli ne rišejo grobo in nikoli ne izpuščajo zaradi proračuna, kakor
  robniki.

**Prizorišče se izreže v celoti.** Kadar se vožnja dotakne lastnih tal prizorišča
(`ground:venue`), se koridor razširi na celoten odtis tistih tal plus `--margin`, zato
tribune, zidovi in ovire okoli stadiona pridejo z njim, ne samo pas, ki so ga uporabili
laps. Konzola izpiše `through a venue (<model names>): cutting all of its ground, <n> km2`.
Ploščadi ne razširijo reza.

### Podrobnost in proračun {#detail-and-the-budget}

Pasovi razdalje, proračun in kopije, ki odidejo, če je proračun premajhen, so v
[Stopnje podrobnosti in proračun](detail-budget.md).

### Povzetek postavitve {#placement-summary}

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

## Lastni sloj dirke {#the-races-own-layer}

Mnoge dirke v vožnjo dodajo stvari, ki v svetu proste vožnje ne obstajajo: betonske
zidove in ograje, ki zapirajo stranske ceste, kupe gum, šotore, startni portal, tribune,
zastave, transparente. Vsaka dirka jih našteje v svoji opisu poti (`route<id>_<map>.rtd`
v `routedefinitions.zip`, navaden XML v navadnem zip):

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

- **Kaj se doda.** Vsak primerek se postavi kot kopija iz datoteke postavitve. Šestnajst
  števil transformacije je štiri vrstice: osi modela x, y in z (vsaka pomnožena z merilom)
  in njegov položaj v metrih igre. Tretja vrstica je vektorski produkt prvih dveh.
  `Material` je varianta, ki jo kopija nosi. Del je `structure:event_<kind>`, pri čemer je
  `<kind>` mapa pod `scene\models\` (barriers, props, infrastructure, signs; vse drugo šteje
  kot props), vozlišče pa nosi dodatne podatke glTF `{"layer": "event", "route": <id>}`.
- **Kaj se vzame.** Kopija svetovne proste vožnje, ki stoji znotraj **0,1 m** od položaja
  skritega sredstva, se izpusti. Skrito sredstvo, ki stoji v izhodišču, je model v
  svetovnih koordinatah; njegov GUID primerka se poišče v `AssetManifest.xml` steze (seznam
  `<Models>`: vir modela, nato GUID-ji njegovih kopij), da se poimenuje.
- **Tla, ki jih dirka skrije, se ohranijo.** Dirka, ki skrije tla prizorišča, na njih položi
  lastno površino. Kadar te površine steza ne dostavlja med svojimi modeli, skrita tla
  ostanejo kot najbližje temu, po čemer se vozi, povzetek pa to pove
  (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Ni narisano, a šteto.** Markerji pregledovalnikov (`crowd_proxies`: igra iz njih riše množico
  kot sprite) in kolizijski splajni (`.splinecol`). Konzola jih našteje:
  `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Dirkine lastne modele, ki jih steza ne dostavlja (svetlobni sijaji, nekateri znaki, vsebina,
  ki jo igra pretaka), navede `placed names have no model in the archives`.

Postavljene so samo kopije znotraj koridorja, kakor pri vsem drugem.

## Pisanje datoteke {#writing-the-file}

Deli se zapisujejo v tem vrstnem redu: za vsako ploščico `terrain`, `verge`, `road` (vsak s
sliko ploščice), nato `water`, `tyre marks`, `markings` (ploski, zadnja dva dvignjena), nato
vsak postavljen del, razvrščen po imenu. Koordinate so igrine lastne (metri, y navzgor).
Glejte [Oblika izhoda](output-format.md).

Datoteka pove, kaj vsebuje, v svojih podatkih glTF `asset.extras`:

| Polje | Pomen |
|---|---|
| `course_format` | `2`: lastni sloj dirke, prizorišča in modeli v svetovnih koordinatah so v njej. [`courses`](commands.md#courses) izvozi datoteko z nižjo številko (ali brez nje) znova |
| `route` | ujemajoči se ID poti ali `null` |
| `event_copies`, `event_kinds` | koliko kopij lastnega sloja dirke je bilo postavljenih in njihove vrste |
| `hidden` | kopije svetovne proste vožnje, ki so izpuščene, ker jih dirka odstrani |
| `venue` | modeli tal prizorišč, skozi katera gre vožnja |
| `layers` | postavljeni vklopljeni sloji |

## Koliko stane {#what-it-costs}

Grobi redi velikosti:

| Tečaj | Rezultat |
|---|---|
| kratek podeželski krog | nekaj sto tisoč trikotnikov terena, nad milijon postavljenih; sekunde, pod 100 MB |
| dolg sprint od točke do točke | koridor je majhen delček škatle okoli njega; okoli minute, nekaj sto MB |
| krog po mestni ulici | na tisoče ovir, rekvizitov in znakov ter celih stavb; s samodejnim proračunom do nekaj sto MB |

Kvadratni kilometer odprtega sveta terena je približno milijon trikotnikov.

## Preverjanja v ozadju {#checks-behind-it}

To so meritve, narejene med pisanjem bralnika, kakor je navedeno v viru. Testi jih ne
ponovijo, razen če je igra nameščena.

- Na testni stezi avto sedi približno na svoji višini vožnje nad izvlečenimi tlemi (mediana
  pod 0,2 m).
- Vsaka vzorčena ploščica pristane znotraj kvadrata 512 m, ki ga napove njeno ime.
- Zaporedne postavitve varovalnih ograj so točno 4 m narazen, in večina koncev ograje pristane
  znotraj 5 cm od začetka naslednje.
- Robniki sedijo nekaj centimetrov nad izvlečenimi tlemi, obrazi navzgor, znotraj 5 m od
  vožnje (tudi test nameščene igre, glejte [Razvoj](development.md)).

## Ni narisano {#not-drawn}

- Drevesa in grmovje, razen z `--trees`. Trava in množice nikoli (igra jih riše kot sprite).
- Lastni modeli dirke, ki jih steza ne dostavlja (glejte [Lastni sloj dirke](#the-races-own-layer)).
- Materiali projiciranih dekalov na modelih.
- Tiskane površine znakov, ki so prosojno pomešane čez svojo ploščo, pridejo neprosojne.
- Barva tal je rekonstrukcija, kje so asfalt, trava in gozd, ne lastni materiali terena igre.
