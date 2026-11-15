---
title: "Forza Horizon"
nav_order: 1
lang: "bs"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Izvoz staze: Forza Horizon {#course-export-forza-horizon}

Forza izvoz čita stazu direktno iz ForzaTech arhiva igre:
teren s razlikovanjem ceste, ruba i trave, teksturu tla pečenu iz
vlastitih mapa tla igre, i svaki postavljeni model u njegovoj vlastitoj teksturi (ivičnjaci,
zaštitne ograde, zidovi od guma, znakovi, rekviziti, zgrade). Također pronalazi na kojoj je od
utrka igre krug vožen i dodaje ono što igra postavlja samo za tu utrku
(njen sloj događaja: ograde, šatori, portali, tribine, zastave), te
tlo svake lokacije kroz koju vožnja prolazi, kao što je pod stadiona.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Izvori: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Sami formati kontejnera nalaze se na [ForzaTech](reader-forzatech.md).

## Pronalaženje instalirane igre {#finding-the-installed-game}

Niko ne bi trebao ukucavati putanju poput
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, pa se putanja određuje sama:

1. **Steam biblioteke.** Steamov `config\libraryfolders.vdf` čita se iz
   `C:\Program Files (x86)\Steam` ili `C:\Program Files\Steam`, a svaki unos `"path"`
   u njemu je biblioteka. Pretražuje se `steamapps\common` svake biblioteke.
2. **Microsoft Store.** Pretražuje se `C:\XboxGames` ako postoji. Tamo se igra
   nalazi jedan nivo dublje, u `<game>\Content`.
3. **Folder igre** je svako dijete tih foldera koje ima folder
   `media\Tracks`, bez obzira na ime.
4. **Folder staze** je svaki folder pod `media\Tracks` koji sadrži
   `GeoChunk0.minizip`. Računa se po sadržaju, a ne po imenu, pa se staza pod
   imenom koje niko nije vidio i dalje pronalazi.

Ako je igra negdje drugdje, navedite folder staze preko `--track`; pogledajte
[Rješavanje problema](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` preskače sve ovo.

Folder staze sadrži ono što izvoz čita:

| Datoteka | Šta je |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arhive: svaki model, tekstura i datoteka postavljanja, bez imena unutra |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | jedan red po unosu arhive, redoslijedom unosa: jedini izvor imena |
| `AssetManifest.xml` | svaka tekstura koju staza isporučuje, s hashom po kojem se materijali na nju pozivaju |

## Koja staza {#which-track}

Igra isporučuje više od jednog foldera staze (mapa otvorenog svijeta, garaža ili dvije).
Prava se bira po **koordinatama, a ne po imenu**:

- Pitanje je granični okvir kruga, proširen za `--margin`.
- Za svaki folder staze čitaju se četiri manifesta `ChunkContentsMiniZip*.txt`
  kao tekst, bez otvaranja arhive. Ime svake pločice terena
  (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) nosi njenu poziciju u mreži.
  Alat broji koliko različitih pločica pada unutar okvira.
- Staza s najviše pločica tamo pobjeđuje. Ako nijedna staza nema nijednu, izvoz se zaustavlja
  s "none of the installed tracks (...) has terrain at x ..., z .... Those are
  the game's own metres, as its telemetry reports them."

Cijela staza odgovara za znatno manje od sekunde. Poklapanje po imenu moglo bi izabrati pogrešnu
mapu, a pogrešna mapa izgleda jednako uvjerljivo kao prava.

Konzola kaže `on <track>, in <game folder>`.

## Koja utrka {#which-race}

Igra isporučuje svaku od svojih utrka kao rutu s brojem, njenim **route id**. Dvije
datoteke pripadaju svakoj ruti:

| Datoteka | Šta sadrži |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | AI linija vožnje utrke: čvor od 56 bajta po tački od bajta `0x60`, broj čvorova na `0x24`, svaki čvor počinje svojom pozicijom (x, y, z) u metrima igre |
| `media\Stripped\gs\<map>\routedefinitions.zip` | jedan `route<id>_<map>.rtd` po utrci: običan XML koji navodi šta utrka dodaje svijetu i šta oduzima (pogledajte [Vlastiti sloj utrke](#the-races-own-layer)) |

Krug se povezuje s rutom poređenjem sa svakom AI linijom čiji se okvir
preklapa s okvirom kruga:

- Od svakog uzorka kruga, udaljenost do najbliže tačke linije; i od
  svake tačke linije, udaljenost do najbližeg uzorka kruga.
- Dva medijana se zbrajaju. Ruta s najmanjim zbirom pobjeđuje ako je zbir
  ispod **30 m** (`MATCH`).
- Trebaju oba smjera: kratki sprint leži duž duge rute koja koristi
  istu cestu, a dug krug pokriva kratku rutu.

Konzola kaže `the game's route <id> (driven line within <n> m of it)`, ili da
se nijedna ruta ne poklapa. Bez poklapanja postavlja se samo svijet slobodnog vožnjenja.

## Teren {#terrain}

Kako se teren pronalazi (u `forzaterrain.py`):

- Manifesti imenuju teren kao prostorni indeks:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Ta dva broja su koordinate mreže koje **koračaju po 1023**, a svaki korak
  mreže je pločica od **512 m**. Pločica `x-2046` je `-2046 / 1023 = -2`, koja počinje na
  `-2 * 512 = -1024` m. Ako imena pročitate kao metre, svako traženje promašuje za
  faktor dva i ipak vraća teren, iz pogrešnog dijela mape.
- Pločica se može pojaviti triput: obična, `_cb` i `_ul`. Sve tri pokrivaju isto
  tlo. Po pločici se uzima jedna, tim redom prednosti, jer bi njihovo spajanje
  utrostručilo geometriju u koincidentne površine.
- Pločica se čita samo ako dodiruje okvir kruga **i** koridor. Pločica
  koju koridor ne dodiruje nikad se ne dekomprimira.
- Svaki `.modelbin` izabrane pločice dekodira se **samo na nivou detalja 0**. Pločica
  nosi četiri nivoa nad istim tlom, a izvoz svih stavlja
  isti kvadratni metar u datoteku četiri puta.
- Svaka mreža nosi vlastitu skalu i pomak u svjetskom prostoru, pa pločica sjedne tamo gdje je
  igra stavlja bez transformacije instance. Zadržavaju se trouglovi čiji otisak preklapa
  okvir, a zatim samo oni koji sežu u koridor.
- Mreža u formatu koji čitač odbija preskače se i broji
  (`N meshes could not be read`), pa tanak rezultat kaže zašto.

Sažetak terena ispisuje broj vrhova, broj trouglova, broj mreža, broj pločica
i x/y/z opseg.

### Cesta, rub, teren, oznake, voda {#road-verge-terrain-markings-water}

Imena materijala ne mogu reći gdje je cesta. Oko staze, 94% tla
koristi materijal cestovnog shadera, jer se teren blizu ceste crta njime, a
shader po pikselu odlučuje asfalt ili trava. Zato:

| Vrsta | Odlučuje |
|---|---|
| traka ceste | **raspored vrhova**: trake ceste su jedino tlo s drugim UV skupom (kanal 1); trougao čija ga sva tri vrha imaju je cesta |
| asfalt prema rubu | unutar trake ceste, **maska asfalta** pločice u težištu trougla: 0,5 ili više je `road`, manje je `verge` |
| oznake | ime materijala se poklapa s `whiteline`, `yellowline` ili `decal` |
| tragovi guma | ime materijala se poklapa s `tyremark` ili `skid` (provjerava se prije oznaka, jer tragovi guma dolaze kao `tyremark_decal_*`) |
| voda | ime materijala se poklapa s `water`, `lake`, `river`, `paddy`, `ocean` ili `sea` |
| teren | sve ostalo |

Izmjereno na snimljenim krugovima probne staze, gotovo svi uzorci padaju na
trouglove trake ceste, a velika većina na asfaltni dio kad je maska
odvojila rub.

Maska asfalta postoji samo kad se peku teksture tla. Uz
`--no-textures`, ili za pločicu čije mape nedostaju, trake ceste ostaju cijele kao
`road` i rub se ne odvaja. Nedostajuće mape koštaju detalj, nikad geometriju.

### Oslikani slojevi su podignuti {#painted-layers-are-lifted}

Oznake traka i tragovi guma dolaze kao vlastiti trouglovi koji leže tačno u
cesti. Igra ih crta s pomakom dubine. Nacrtani takvi kakvi jesu, cesta i boja
bore se za svaki piksel. Izvoz daje svakom dijelu oznaka i tragova guma vlastitu
kopiju njegovih vrhova, podignutu **5 cm** (`DECAL_LIFT`) duž normale površine, pa
cesta ispod nije podignuta zajedno s njima.

### Normale {#normals}

Normale terena dolaze iz arhive. X normale pohranjen je kao
četvrti short pozicije, a njen y i z u atributu `NORMAL` (pogledajte
[ForzaTech](reader-forzatech.md)). Ako ijedan vrh u izdvajanju nema
normalu, normale cijelog tla računaju se umjesto toga iz trouglova.

## Tekstura tla {#the-ground-texture}

Svaka pločica terena isporučuje tri mape koje pokrivaju njen kvadrat od 512 m, u pet rezolucija
(`_quality1` do `_quality5`, najveća 2048 px, što je 25 cm po pikselu):

| Mapa | Obrazac imena datoteke | Šta sadrži (kako je izmjereno) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detaljna normala (x, z). A: niže na asfaltu i na hrapavom tlu |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | težine slojeva. B: visoko na asfaltu (239 na vozenoj liniji, 165 pored nje) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: nisko na asfaltu (147 prema 215). B: raste u šumi |

Nijedna od ovih nije fotografija u boji. To su ulazi kojima shader terena igre
miješa svoje slojeve materijala, a ti slojevi nisu dekodirani. Zato je
pečena tekstura **interpretacija, a ne kopija izgleda igre**. Zadržava
*gdje* je svaka vrsta tla, na 25 cm, i boji je fiksnim bojama:

| Tlo | Linearni RGB | Težina |
|---|---|---|
| trava (kratka, blizu staze) | 0,30, 0,44, 0,18 | osnova |
| hrapavo (dalje) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| šuma | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Obje mape se moraju složiti za asfalt. Svaka sama ostavlja sivi šum u
travi gdje god blokovska kompresija zvoni. Rezultat se zasjenjuje detaljnom normalom glavne mape
prema fiksnom svjetlu (`0.55 + 0.6 * lambert`), pa ivice ivičnjaka, nasipi
i kolotrazi izgledaju kao reljef, i upisuje se kao 8-bitni sRGB.

Orijentacija: red piksela 0 je **sjeverna** ivica pločice (najveći z), kolona 0 njena
**zapadna** ivica (najmanji x). Ovo je pronađeno projiciranjem snimljenih krugova na
masku asfalta na svih osam načina na koje se kvadrat može okrenuti ili obrnuti. Tačno jedan način
ih stavlja na asfalt. UV-ovi slijede iz toga: `u = (x - x0) / 512`,
`v = 1 - (z - z0) / 512`.

Mape se čitaju u najboljoj dostupnoj rezoluciji do kvaliteta 5 i prouzorkuju
na veličinu glavne mape. Ako je slika boje veća od `--texture-size`, tada se
smanjuje na tu veličinu Lanczos filtriranjem. Maska asfalta uvijek se zadržava u punoj rezoluciji, jer
odlučuje geometriju. `--season` bira mape `x<season>x`. Pločica bez mapa za
to godišnje doba crta se ravnim bojama, a konzola prijavljuje
`N without maps`.

## Postavljeni modeli {#placed-models}

Teren nosi vlastitu svjetsku poziciju. Ništa drugo ne nosi. Gdje stoji svaka kopija
modela zapisano je u `.pgeo` datotekama postavljanja, po jedan po kategoriji po prostornoj
ćeliji:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Raspored zapisa
je na [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Šta se čita {#what-is-read}

- Datoteke postavljanja filtriraju se **po imenu**: veličina ćelije i pozicija ćelije u
  putanji daju kvadrat ćelije (`x * size` do `(x + 1) * size`), a otvaraju se samo ćelije koje
  preklapaju okvir kruga, u traženoj kategoriji.
- Zadane kategorije: `barriers`, `props`, `signs`, `buildings`,
  `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` dodaje `trees`,
  `bushes` i `smashables`. Ovo se nikad ne čita: `grasstemplate`,
  `crowdtemplate` i `cwdspline` (trava i gledaoci: igra ih crta kao
  animirane sprajtove, nema geometrije).
- Svaka datoteka pripada **sloju**, koji se čita iz njegovog imena poslije
  `c<size>_<category>_`. Riječ nivoa detalja (`do`, `so`, `ulc`, `ulp`, `cwd`)
  i neobavezan broj sekcije je svijet slobodnog vožnjenja. Sve ostalo je
  sloj koji igra uključuje: runtime sloj (`rt_0`), aktivnost
  (`_tag_<name>_`), kolekcionarski predmet, sve što je upisano pod `evolving`. Sloj
  koji imenuje rute (`rt_x<id>`, na primjer `rt_x1023_x2201`) pripada samo tim
  utrkama i čita se samo kad se krug poklopio s jednom od njih. Pogledajte
  [Uključeni slojevi](#switched-on-layers).
- Kopija se zadržava ako je njena pozicija unutar okvira i unutar koridora.
  Tačni duplikati (ista pozicija i orijentacija do milimetra, navedeni u
  dvije susjedne ćelije) se spajaju.
- **Ivičnjaci** su rekviziti čije ime modela počinje s `road_gen_rum` (rumble
  trake). Upisuju se kao `ground:kerbs`, nikad se ne pojednostavljuju i nikad se ne izostavljaju,
  jer se krug mjeri prema njima.

| Kategorija | Dio | Rezervna boja (bez teksture) |
|---|---|---|
| ivičnjaci | `ground:kerbs` | 0,60, 0,12, 0,10 |
| ograde | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekviziti | `structure:props` | 0,45, 0,35, 0,25 |
| znakovi | `structure:signs` | 0,70, 0,70, 0,70 |
| zgrade | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktura | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| mostovi | `structure:bridges` | 0,45, 0,45, 0,45 |
| stijene | `structure:rocks` | 0,30, 0,28, 0,25 |
| smashables | `structure:smashables` | 0,12, 0,22, 0,06 |
| drveće, grmlje | `structure:trees` | 0,10, 0,20, 0,05 |

### Geometrija modela {#the-models-geometry}

Postavljeno ime `<model>_3D` odnosi se na datoteke modela `<model>_cluster###.i.modelbin`
(do desetak). Svaki trougao nosi masku nivoa detalja kojima pripada:

- Nivoi modela su njegovi trouglovi izričito označeni za taj nivo. Nivoi idu
  neprekidno od 0, prvo najfiniji.
- Trouglovi označeni s `0xFFFF` (svaki nivo) su dijelovi koji se mogu slomiti, kao
  stupovi zaštitne ograde ili pojedinačne gume u zidu od guma. Preklapaju cijeli model,
  a igra ih crta umjesto njega kad se raspadne. Koriste se
  samo za model bez izričito označenog nivoa.
- Podmreže čiji je shader materijala projicirani **decal** izostavljaju se.

Svaka kopija se postavlja sa svojom pozicijom, svojim x i y osama iz zapisa
(z = x puta y) i svojom skalom. Normale se transformiraju inverznom skalom.

### Koja tekstura {#which-texture}

Materijal ne imenuje svoje teksture. Navodi ih kao hasheve, a `AssetManifest.xml` staze
mapira svaki hash (`SourceHash`) na ime teksture. Čita se samo
odjeljak `<Textures>`, pri čemu se čitanje zaustavlja na `</Textures>` u datoteci koji
može imati desetke megabajta. Zatim:

1. Slot `0x88B483AA` je osnovna boja u standardnom shaderu okruženja (svaki
   uzorkovani materijal). Ako materijal tamo veže teksturu, koristi se ta.
2. Inače odlučuje vlastita vrsta teksture, a to je riječ prije njenog GUID-a:
   `_bclr_`, zatim `_diff_`, zatim `_colour_`.
3. Mape terena (`mainmap`, `submap`, `autogloss`) i palete nijansi (`tint`,
   `worldtint`) nikad ne boje model.

Dakle model se boji onim što njegov materijal veže, a ne teksturom imenovanom kao
model. Na primjer, `bar_rur_armco_crct_02_c` koristi teksturu od `..._02_a`.

Tekstura se čita iz arhiva u najmanjoj rezoluciji od najmanje
**256 px** u širinu (`MODEL_TEXTURE`), smanjuje na 256 ako je veća, i pohranjuje kao RGB
JPEG u `.glb`. Boja zaštitne ograde na 256 px za četiri metra je 1,6 cm po
pikselu, a oko 80 takvih tekstura stane u atlas preglednika pored pločica
tla.

**Godišnja doba.** `--season` mijenja teksturu njenim sezonskim blizancem po imenu, uz
ignoriranje GUID-a (`..._xsummerx_bclr` u `..._xwinterx_bclr`, ili `..._bclr` u
`..._winter_bclr`), kad ga staza ima. Uz `--season winter`, zimski materijal podmreže
također se koristi gdje ga imenuje njena tablica varijanti.

**Varijante.** Zapis podmreže počinje tablicom materijala `(summer, winter)`,
po jedan za svaki izgled koji kopija može nositi: pet printova za bilbord, šest boja
za zid od guma. Svaki zapis postavljanja kaže koju varijantu ta kopija nosi. Podmreža
s manje varijanti od modela ponavlja svoje.

**Blok rezervirane boje.** Zajednički atlasi zgrada rezerviraju puni
RGB (255, 64, 0) blok za površine koje shader zgrade boji iz drugih tekstura.
Ako je više od dvadesetine teksture unutar 12 nivoa te boje, blok se
ponovo boji prosječnom bojom same teksture. Inače grad ispadne narandžast.

### Prozirne površine {#see-through-surfaces}

Ograde od pletene žice i mreže su pojedinačni kvadovi s rupama u alfi teksture.
Nacrtana puna, ograda je zid preko pogleda na stazu. Površine čiji
shader materijala odgovara `alphatest`, `alphablend`, `transmissive`, `anim_flag`,
`impostor`, `branch`, `bush` ili `tree` se testiraju:

- Neprozirnost teksture usrednjava se preko mreže 32 x 32.
- Po površini (svaki izrezani trougao koji dijeli jednu teksturu), uzimaju se četiri tačke po
  trouglu u UV prostoru, otežane UV površinom trougla.
- Ako je prosječna neprozirnost najmanje 0,05 i ispod **0,5**, cijela površina se
  izostavlja. Ispod 0,05 alfa očito znači nešto drugo njenom shaderu (znak
  upozorenja koji daje 0,01), a površina ostaje puna.
- Model čija je svaka površina izostavljena prijavljuje se:
  `N models left out as see-through (mostly holes in their texture)`.

Alat sudi cijeloj površini, a ne jednom po jednom trouglu. Suđeno
po trouglu, preživjela je polovina svakog kvada, a ograde su ispale kao nizovi zuba.

### Zgrade crtane cijele {#buildings-drawn-whole}

Grad gradi svoje zgrade od modularnih dijelova: stotine hiljada njih
oko jedne gradske staze, desetine miliona trouglova čak i u najgrubljem. Izostavljanje
dijelova jedan po jedan ostavljalo je usamljene zidne ploče. Igra također
isporučuje zamjene za cijele zgrade u `scene\hlod_tier_1\`, jednu mrežu po zgradi
(korijen `hlod_tier_1_*`), već u svjetskim koordinatama kao teren:

- Svjetski okvir svake zamjene čita se iz okvira pozicije njene mreže (čitanje
  zaglavlja, ne dekodiranje). Za cijelu mapu to traje sekunde.
- Koriste se zamjene koje dodiruju okvir kruga i koridor.
- Svaki komad `buildings` čija pozicija pada unutar otiska zamjene
  (plus 0,5 m) odbacuje se, a umjesto njega se crta zamjena. Njena udaljenost od
  vožnje mjeri se do najbliže ivice zgrade.
- Sažetak kaže `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Uključeni slojevi {#switched-on-layers}

Ono što uključeni sloj postavlja izvozi se, ali odvojeno od svijeta slobodnog vožnjenja,
pa ga preglednik može prikazati ili sakriti:

| Sloj | Dio |
|---|---|
| svijet slobodnog vožnjenja | `structure:<category>` (kao prije) |
| sloj koji imenuje rutu povezane utrke | `structure:event_<category>` |
| bilo koji drugi uključeni sloj | `structure:layer_<category>` |

Sažetak ih broji: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modeli već u svjetskim koordinatama {#models-already-in-world-coordinates}

Nekoliko vrsta modela nije ni u jednoj datoteci postavljanja. Njihove mreže nose vlastitu
svjetsku poziciju, kao teren, pa ih ništa ne treba postavljati:

| Folder pod `scene\models\` | Šta je | Dio |
|---|---|---|
| `plots` | vlastito tlo lokacije: pod i unutrašnjost stadiona, mjesto festivala, trg | `ground:venue` |
| `plinths` (i svaki model nazvan `floor`, `ground` ili `road`) | tlo kojim je ulica uređena: žardinjere, stepenice, popločenje parka | `ground:plinths` |
| `hda_infrastructure` (mostovi) | proceduralno građeni mostovi | `structure:bridges` |

- Model se računa kao da je u svjetskim koordinatama kad sredina njegovog okvira leži
  dalje od **300 m** (`WORLD_REACH`) od vlastitog ishodišta. Modeli postavljeni
  datotekama postavljanja stoje unutar nekoliko stotina metara od svog.
- Ne crtaju se: okluderi, kablovi razapeti duž cesta, pozadina mora,
  krovovi i okluderi modularnih zgrada (zamjene crtaju te
  zgrade), volumeni sudara i vode.
- Svaki se čita iz okvira svojih mreža (čitanje zaglavlja), nekoliko sekundi za
  cijelu mapu, jednom po pokretanju.
- Dijelovi tla se nikad ne crtaju grublje i nikad se ne izostavljaju da stanu u budžet,
  kao ivičnjaci.

**Lokacija se siječe cijela.** Kad vožnja dodirne vlastito tlo lokacije
(`ground:venue`), koridor se proširuje na cijeli otisak tog tla plus
`--margin`, pa tribine, zidovi i ograde oko stadiona dolaze s njim, a ne
samo traka koju su krugovi koristili. Konzola kaže
`through a venue (<model names>): cutting all of its ground, <n> km2`. Postolja (plinths)
ne proširuju izrez.

### Detalj i budžet {#detail-and-the-budget}

Pojasevi udaljenosti, budžet i koje kopije odlaze kad je budžet premalen nalaze se na
[Nivoi detalja i budžet](detail-budget.md).

### Sažetak postavljanja {#placement-summary}

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

## Vlastiti sloj utrke {#the-races-own-layer}

Mnoge utrke postavljaju stvari kojih nema u slobodnom vožnjenju: betonske zidove i
ograde koje zatvaraju sporedne ceste, zidove od guma, šatore, startni portal,
tribine, zastave, transparente. Svaka utrka ih navodi u svojoj definiciji rute
(`route<id>_<map>.rtd` u `routedefinitions.zip`, običan XML u običnom zipu):

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

- **Šta se dodaje.** Svaka instanca se postavlja kao kopija iz datoteke postavljanja.
  16 brojeva transformacije su četiri reda: x, y i z ose modela (svaka skalirana)
  i njegova pozicija u metrima igre. Treći red je vektorski produkt prva
  dva. `Material` je varijanta koju kopija nosi. Dio je
  `structure:event_<kind>`, gdje je `<kind>` folder pod `scene\models\`
  (barriers, props, infrastructure, signs; sve ostalo računa se kao props), a
  čvor nosi glTF extras `{"layer": "event", "route": <id>}`.
- **Šta se oduzima.** Kopija slobodnog vožnjenja koja stoji unutar **0,1 m** od pozicije
  skrivenog asseta izostavlja se. Skriveni asset koji stoji u ishodištu je model
  u svjetskim koordinatama; njegov GUID instance traži se u `AssetManifest.xml`
  staze (lista `<Models>`: izvor modela, zatim GUID-ovi njegovih
  kopija) da bi se imenovao.
- **Tlo koje utrka skriva se zadržava.** Utrka koja skriva tlo lokacije polaže
  tamo vlastitu površinu. Kad ta površina nije među modelima koje staza isporučuje,
  skriveno tlo ostaje, kao najbliže onome po čemu se vozi, a
  sažetak to kaže (`kept <model>: the race hides it for a surface of its own
  that the track does not ship`).
- **Ne crta se, ali se broji.** Markeri gledalaca (`crowd_proxies`: igra crta
  publiku kao sprajtove iz njih) i splineovi sudara (`.splinecol`). Konzola
  ih navodi: `its own layer: <n> copies of <m> models, <k> free-roam
  objects hidden; not drawn: ...`.
- Assete rute za koje staza ne isporučuje model (odsjaji svjetala, neki znakovi,
  sadržaj koji igra učitava u hodu) navode se u `placed names have no model in the
  archives`.

Postavljaju se samo kopije unutar koridora, kao i za sve ostalo.

## Upisivanje datoteke {#writing-the-file}

Dijelovi se upisuju ovim redom: po pločici `terrain`, `verge`, `road` (svaki sa
slikom pločice), zatim `water`, `tyre marks`, `markings` (ravni, zadnja dva
podignuta), zatim svaki postavljeni dio sortiran po imenu. Koordinate su vlastite
koordinate igre (metri, Y gore). Pogledajte [Format izlaza](output-format.md).

Datoteka u svom glTF `asset.extras` kaže šta sadrži:

| Polje | Značenje |
|---|---|
| `course_format` | `2`: u njemu su vlastiti sloj utrke, lokacije i modeli u svjetskom prostoru. [`courses`](commands.md#courses) ponovo izvozi datoteku s nižim brojem (ili bez njega) |
| `route` | id povezane rute, ili `null` |
| `event_copies`, `event_kinds` | koliko je kopija vlastitog sloja utrke postavljeno, i njihove vrste |
| `hidden` | kopije slobodnog vožnjenja izostavljene jer ih utrka uklanja |
| `venue` | modeli tla lokacije kroz koje vožnja prolazi |
| `layers` | postavljeni uključeni slojevi |

## Šta košta {#what-it-costs}

Grubi redovi veličine:

| Staza | Rezultat |
|---|---|
| kratka seoska staza | nekoliko stotina hiljada trouglova terena, preko milion postavljenih; sekunde, ispod 100 MB |
| dug sprint od tačke do tačke | koridor je mali dio okvira oko njega; oko minute, nekoliko stotina MB |
| gradska ulična staza | hiljade ograda, rekvizita i znakova i cijele zgrade; s automatskim budžetom do nekoliko stotina MB |

Kvadratni kilometar terena otvorenog svijeta je oko milion trouglova.

## Provjere iza toga {#checks-behind-it}

Ovo su mjerenja napravljena dok je čitač pisan, kako stoji u
izvoru. Testovi ih ne ponavljaju osim ako je igra instalirana.

- Na probnoj stazi, automobil sjedi otprilike na visini svoje vožnje iznad izdvojenog tla (medijan ispod 0,2 m).
- Svaka uzorkovana pločica pada unutar kvadrata od 512 m koji njeno ime predviđa.
- Uzastopna postavljanja zaštitnih ograda su tačno 4 m razmaknuta, a većina krajeva ograda pada unutar 5 cm od početka sljedeće.
- Ivičnjaci sjede nekoliko centimetara iznad izdvojenog tla, licem prema gore, unutar 5 m od vožnje (također test instalirane igre, pogledajte [Razvoj](development.md)).

## Ne crta se {#not-drawn}

- Drveće i grmlje osim uz `--trees`. Trava i publika nikad (igra ih crta kao sprajtove).
- Vlastiti modeli utrke koje staza ne isporučuje (pogledajte [Vlastiti sloj utrke](#the-races-own-layer)).
- Projicirani decal materijali na modelima.
- Printovi znakova alfa-miješani preko svoje ploče ispadnu neprozirni.
- Boja tla je rekonstrukcija gdje su asfalt, trava i šuma, a ne vlastiti materijali terena igre.
