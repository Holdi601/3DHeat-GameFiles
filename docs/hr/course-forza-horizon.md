---
title: Forza Horizon
nav_order: 1
lang: "hr"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Izvoz staze: Forza Horizon {#course-export-forza-horizon}

Izvoz Forze čita stazu izravno iz ForzaTech arhiva igre: teren s razdvojenom cestom, rubom i travom, teksturu tla pečenu iz igrinih vlastitih karata tla, i svaki postavljeni model u vlastitoj teksturi (rubnjaci, zaštitne ograde, zidovi od guma, znakovi, rekviziti, zgrade). Također pronalazi koju je od igrinih utrka krug vožen i dodaje ono što igra stavlja za tu utrku sama (njezin sloj događaja: barijere, šatore, portale, tribine, zastave), te tlo svakog mjesta održavanja kroz koje vožnja prolazi, poput poda stadiona.

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
Sami formati spremnika opisani su na [ForzaTech](reader-forzatech.md).

## Pronalaženje instalirane igre {#finding-the-installed-game}

Nitko ne bi trebao upisivati put poput `D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, pa se put sam određuje:

1. **Steam biblioteke.** Steamova `config\libraryfolders.vdf` čita se iz `C:\Program Files (x86)\Steam` ili `C:\Program Files\Steam`, a svaki unos `"path"` u njoj je biblioteka. Pretražuje se `steamapps\common` svake biblioteke.
2. **Microsoft Store.** Pretražuje se `C:\XboxGames`, ako postoji. Tamo je igra jednu razinu dublje, u `<game>\Content`.
3. **Mapa igre** je svaka podmapa tih mapa koja ima mapu `media\Tracks`, bez obzira na ime.
4. **Mapa staze** je svaka mapa pod `media\Tracks` koja ima `GeoChunk0.minizip`. Broji se po sadržaju, a ne po imenu, pa se staza pod imenom koje nitko nije vidio ipak nađe.

Ako je igra negdje drugdje, zadajte mapu staze s `--track`; vidi [Rješavanje problema](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <mapa>` preskače sve ovo.

Mapa staze sadrži ono što izvoz čita:

| Datoteka | Što je |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arhivi: svaki model, tekstura i datoteka postavljanja, bez imena unutra |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | jedan redak po stavci arhiva, po redoslijedu stavki: jedini izvor imena |
| `AssetManifest.xml` | svaka tekstura koju staza isporučuje, s heš-vrijednošću kojom je materijali navode |

## Koja staza {#which-track}

Igra isporučuje više mapa staza (otvoreni svijet, jedna ili dvije garaže). Ispravna se bira po **koordinatama, a ne po imenu**:

- Pitanje je okvir kruga, proširen za `--margin`.
- Za svaku mapu staze četiri manifesta `ChunkContentsMiniZip*.txt` čitaju se kao tekst, bez otvaranja arhiva. Svako ime pločice terena (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) nosi svoj položaj u mreži. Alat broji koliko različitih pločica pada unutar okvira.
- Pobjeđuje staza s najviše pločica. Ako nijedna nema nijednu, izvoz staje s porukom `"none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."`

Cijela staza odgovara za manje od sekunde. Podudaranje imena moglo bi odabrati pogrešnu kartu, a pogrešna karta izgleda jednako uvjerljivo kao i ispravna.

Konzola ispisuje `on <track>, in <game folder>`.

## Koja utrka {#which-race}

Igra isporučuje svaku svoju utrku kao rutu s brojem, njezinim **id-om rute**. Svaka ruta ima dvije datoteke:

| Datoteka | Što sadrži |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | AI vožnja utrke: čvor od 56 bajtova počevši od bajta `0x60`, broj čvorova na `0x24`, svaki čvor počinje svojom pozicijom (x, y, z) u metrima igre |
| `media\Stripped\gs\<map>\routedefinitions.zip` | jedan `route<id>_<map>.rtd` po utrci: običan XML koji navodi što utrka dodaje svijetu i što iz njega uklanja (vidi [Sloj vlastite utrke](#the-races-own-layer)) |

Krug se uparuje s rutom uspoređujući ga sa svakom AI linijom čiji se okvir preklapa s krugom:

- Od svakog uzorka kruga, udaljenost do najbliže točke linije; i od svake točke linije, udaljenost do najbližeg uzorka kruga.
- Dva medijana se zbrajaju. Ruta s najmanjim zbrojem pobjeđuje ako je zbroj manji od **30 m** (`MATCH`).
- Potrebna su oba smjera: kratki sprint leži uz dugu rutu koja koristi istu cestu, a dugi krug pokriva kratku rutu.

Konzola ispisuje `the game's route <id> (driven line within <n> m of it)`, ili da nijedna ruta ne odgovara. Bez podudaranja postavlja se samo svijet slobodne vožnje.

## Teren {#terrain}

Kako se teren pronalazi (u `forzaterrain.py`):

- Manifesti navode teren kao prostorni indeks: `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Dva broja su koordinate mreže koje **rastu za 1023**, a svaki korak mreže je pločica od **512 m**. Pločica `x-2046` je `-2046 / 1023 = -2`, što počinje na `-2 * 512 = -1024` m. Ako imena čitate kao metre, svako traženje promaši za faktor dva i ipak vrati teren, iz krivog dijela karte.
- Pločica se može pojaviti tri puta: obična, `_cb` i `_ul`. Sve tri pokrivaju isto tlo. Uzima se jedna po pločici, tim redoslijedom prednosti, jer bi ih spajanje utrostručilo geometriju u površinama koje se podudaraju.
- Pločica se čita samo ako dodiruje okvir kruga **i** koridor. Pločica koju koridor ne dodiruje nikad se ne dekomprimira.
- Svaki `.modelbin` odabrane pločice dekodira se samo na **razini detalja 0**. Pločica nosi četiri razine nad istim tlom, a izvoz svih stavlja isti kvadratni metar u datoteku četiri puta.
- Svaka mreža nosi vlastitu skalu i pomak u prostoru svijeta, pa pločica sjeda tamo gdje je igra stavlja, bez transformacije instance. Zadržavaju se trokuti čiji otisak preklapa okvir, zatim samo oni koji sežu u koridor.
- Mreža u formatu koji čitač odbija preskače se i broji (`N meshes could not be read`), pa tanak rezultat kaže zašto.

Sažetak terena ispisuje broj vrhova, trokuta, mreža, pločica i raspon x/y/z.

### Cesta, rub, teren, oznake, voda {#road-verge-terrain-markings-water}

Imena materijala ne mogu reći gdje je cesta. Oko staze 94% tla koristi materijal sjenčara ceste, jer se teren uz cestu crta njime, a sjenčar po pikselu odlučuje o asfaltu ili travi. Zato:

| Vrsta | Određuje |
|---|---|
| traka ceste | **raspored vrhova**: trake ceste su jedino tlo s drugim skupom UV-a (kanal 1); trokut kojem sva tri vrha to imaju je cesta |
| asfalt ili rub | unutar trake ceste, **maska asfalta** pločice u težištu trokuta: 0.5 ili više je `road`, manje je `verge` |
| oznake | ime materijala podudara se s `whiteline`, `yellowline` ili `decal` |
| tragovi guma | ime materijala podudara se s `tyremark` ili `skid` (provjerava se prije oznaka, jer se tragovi guma isporučuju kao `tyremark_decal_*`) |
| voda | ime materijala podudara se s `water`, `lake`, `river`, `paddy`, `ocean` ili `sea` |
| teren | sve ostalo |

Izmjereno na snimljenim krugovima probne staze, gotovo svi uzorci padaju na trokute trake ceste, a velika većina na dio asfalta nakon što je maska odvojila rub.

Maska asfalta postoji samo kad se teksture tla peku. Uz `--no-textures`, ili za pločicu kojoj karte nedostaju, trake ceste ostaju cjelovite kao `road` i nijedan rub se ne odvaja. Nedostajuće karte koštaju detalj, nikad geometriju.

### Naslikani slojevi se podižu {#painted-layers-are-lifted}

Oznake traka i tragovi guma isporučuju se kao vlastiti trokuti koji leže točno na cesti. Igra ih crta s pomakom dubine. Nacrtani kakvi jesu, cesta i boja bore se oko svakog piksela. Izvoz svakom dijelu oznake i tragova guma daje vlastitu kopiju njegovih vrhova, podignutu za **5 cm** (`DECAL_LIFT`) duž normale površine, pa se cesta ispod ne podiže.

### Normale {#normals}

Normale terena dolaze iz arhiva. Normalin x sprema se kao četvrti short pozicije, a y i z u atributu `NORMAL` (vidi [ForzaTech](reader-forzatech.md)). Ako nekom vrhu izvlačenja nedostaje normala, normale cijelog tla računaju se iz trokuta.

## Tekstura tla {#the-ground-texture}

Svaka pločica terena isporučuje tri karte koje pokrivaju njezin kvadrat od 512 m, u pet razlučivosti (`_quality1` do `_quality5`, najveća 2048 px, što je 25 cm po pikselu):

| Karta | Obrazac imena datoteke | Što sadrži (izmjereno) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detaljna normala (x, z). A: niže na asfaltu i na grubom tlu |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | težine slojeva. B: visoko na asfaltu (239 na vožnoj liniji, 165 pored nje) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: nisko na asfaltu (147 naspram 215). B: raste u šumi |

Nijedna od ovih nije fotografija u boji. To su ulazi kojima sjenčar terena igre miješa svoje slojeve materijala, a ti slojevi se ne dekodiraju. Zato je pečena tekstura **tumačenje, a ne kopija izgleda igre**. Čuva *gdje* je koja vrsta tla, na 25 cm, i boji je fiksnim bojama:

| Tlo | Linearni RGB | Težina |
|---|---|---|
| trava (kratka, uz stazu) | 0.30, 0.44, 0.18 | osnova |
| grubo tlo (dalje) | 0.40, 0.42, 0.22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| šuma | 0.13, 0.23, 0.10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0.20, 0.20, 0.21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Za asfalt se moraju slagati obje karte. Svaka sama ostavlja sivo šarenilo u travi gdje god kompresija blokova zvoni. Rezultat se sjenča detaljnom normalom glavne karte prema fiksnom svjetlu (`0.55 + 0.6 * lambert`), pa rubovi kolnika, nasipi i koloseci djeluju kao reljef, i zapisuje se kao 8-bitni sRGB.

Orijentacija: redak 0 piksela je **sjeverni** rub pločice (najveći z), stupac 0 njezin **zapadni** rub (najmanji x). To je nađeno projiciranjem snimljenih krugova na masku asfalta na svih osam načina na koje se kvadrat može okrenuti ili prevrnuti. Točno jedan način ih stavlja na asfalt. UV koordinate slijede iz toga: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Karte se čitaju u najboljoj razlučivosti do kvalitete 5 i preuzorkuju na veličinu glavne karte. Ako je slika boja veća od `--texture-size`, zatim se smanjuje na tu veličinu Lanczos filtrom. Maska asfalta uvijek se čuva u punoj razlučivosti, jer odlučuje o geometriji. `--season` bira karte `x<season>x`. Pločica bez karata za to godišnje doba crta se ravnim bojama, a konzola prijavljuje `N without maps`.

## Postavljeni modeli {#placed-models}

Teren nosi vlastiti položaj u svijetu. Ništa drugo ne nosi. Gdje stoji svaka kopija modela zapisano je u datotekama postavljanja `.pgeo`, jedna po kategoriji po prostornoj ćeliji: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Raspored zapisa je na [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Što se čita {#what-is-read}

- Datoteke postavljanja filtriraju se **po imenu**: veličina ćelije i položaj ćelije u putanji daju kvadrat ćelije (`x * size` do `(x + 1) * size`), i otvaraju se samo ćelije koje se preklapaju s okvirom kruga, u traženoj kategoriji.
- Kategorije po zadanom: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` dodaje `trees`, `bushes` i `smashables`. Ovo se nikad ne čita: `grasstemplate`, `crowdtemplate` i `cwdspline` (trava i gledatelji: igra ih crta kao animirane sprajtove, nema geometrije).
- Svaka datoteka pripada **sloju**, koji se čita iz imena nakon `c<size>_<category>_`. Riječ razine detalja (`do`, `so`, `ulc`, `ulp`, `cwd`) i izborni broj odjeljka je svijet slobodne vožnje. Sve drugo je sloj koji igra uključuje: sloj za vrijeme izvođenja (`rt_0`), aktivnost (`_tag_<name>_`), skupljalo, sve što je spremljeno pod `evolving`. Sloj koji imenuje rute (`rt_x<id>`, na primjer `rt_x1023_x2201`) pripada samo tim utrkama i čita se samo ako se krug podudario s jednom od njih. Vidi [Uključeni slojevi](#switched-on-layers).
- Kopija se zadržava ako je njezin položaj unutar okvira i unutar koridora. Točni ponovci (isti položaj i orijentacija do milimetra, a navedeni u dvije susjedne ćelije) spajaju se.
- **Rubnjaci** su rekviziti čije ime modela počinje s `road_gen_rum` (rubne trake). Zapisuju se kao `ground:kerbs`, nikad se ne pojednostavljuju i nikad ne izostavljaju, jer se krug mjeri prema njima.

| Kategorija | Dio | Rezervna boja (bez teksture) |
|---|---|---|
| kerbs | `ground:kerbs` | 0.60, 0.12, 0.10 |
| barriers | `structure:barriers` | 0.50, 0.50, 0.50 |
| props | `structure:props` | 0.45, 0.35, 0.25 |
| signs | `structure:signs` | 0.70, 0.70, 0.70 |
| buildings | `structure:buildings` | 0.55, 0.52, 0.48 |
| infrastructure | `structure:infrastructure` | 0.45, 0.45, 0.47 |
| bridges | `structure:bridges` | 0.45, 0.45, 0.45 |
| rocks | `structure:rocks` | 0.30, 0.28, 0.25 |
| smashables | `structure:smashables` | 0.12, 0.22, 0.06 |
| trees, bushes | `structure:trees` | 0.10, 0.20, 0.05 |

### Geometrija modela {#the-models-geometry}

Ime postavljenog modela `<model>_3D` upućuje na datoteke modela `<model>_cluster###.i.modelbin` (do desetak). Svaki trokut nosi masku razina detalja kojima pripada:

- Razine modela su njegovi trokuti izričito označeni za tu razinu. Razine teku bez prekida od 0, najfinija prva.
- Trokuti označeni `0xFFFF` (svaka razina) su dijelovi koji se mogu slomiti, poput stupova zaštitne ograde ili pojedinih guma u slogu guma. Preklapaju cijeli model, a igra ih crta umjesto njega kada se on raspadne. Koriste ih samo modeli bez izričito označene razine.
- Podmreže čiji je sjenčar materijala projicirani **dekal** izostavljaju se.

Svaka kopija se postavlja svojim položajem, svojim x i y osima iz zapisa (z = x križ y) i svojom skalom. Normale se transformiraju inverznom skalom.

### Koja tekstura {#which-texture}

Materijal ne imenuje svoje teksture. Navodi ih kao heš-vrijednosti, a `AssetManifest.xml` staze preslikava svaku heš-vrijednost (`SourceHash`) u ime teksture. Čita se samo odjeljak `<Textures>`, koji prestaje na `</Textures>` u datoteci koja može imati desetke megabajta. Zatim:

1. Slot `0x88B483AA` je osnovna boja u standardnom sjenčaru okoline (svaki uzorkovani materijal). Ako tamo materijal veže teksturu, ona se koristi.
2. Inače odlučuje vlastita vrsta teksture, riječ prije njezina GUID-a: `_bclr_`, zatim `_diff_`, zatim `_colour_`.
3. Karte terena (`mainmap`, `submap`, `autogloss`) i palete nijansi (`tint`, `worldtint`) nikad ne boje model.

Model je dakle obojen onim što mu materijal veže, a ne teksturom imenovanom kao model. Na primjer, `bar_rur_armco_crct_02_c` koristi teksturu od `..._02_a`.

Tekstura se čita iz arhiva u najmanjoj razlučivosti koja je barem **256 px** preko (`MODEL_TEXTURE`), smanjuje se na 256 ako je veća, i sprema se kao RGB JPEG u `.glb`. Boja zaštitne ograde na 256 px za četiri metra je 1.6 cm po pikselu, a oko 80 takvih tekstura stane u atlas preglednika uz pločice tla.

**Godišnja doba.** `--season` zamjenjuje teksturu njezinim sezonskim parom po imenu, uz zanemarivanje GUID-a (`..._xsummerx_bclr` u `..._xwinterx_bclr`, ili `..._bclr` u `..._winter_bclr`), kada staza ima par. Uz `--season winter`, zimski materijal podmreže također se koristi tamo gdje njezina tablica varijanti ga imenuje.

**Varijante.** Zapis podmreže počinje tablicom materijala `(summer, winter)`, po jedan za svaki izgled koji kopija može nositi: pet otisaka za reklamni pano, šest boja za slog guma. Svaki zapis postavljanja kaže koju varijantu ta kopija nosi. Podmreža s manje varijanti nego model ponavlja svoje.

**Blok rezerviranog mjesta.** Zajednički atlasi zgrada rezerviraju čvrsti RGB (255, 64, 0) blok za površine koje sjenčar zgrade boji iz drugih tekstura. Ako je više od dvadesetine teksture unutar 12 razina od te boje, blok se preslikava prosječnom bojom same teksture. Inače bi grad ispao narančast.

### Prozirne površine {#see-through-surfaces}

Žičane ograde i mreže su pojedinačni četverokuti s rupama u alfa kanalu teksture. Nacrtane čvrsto, ograda je zid preko pogleda na stazu. Površine čiji sjenčar materijala odgovara `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` ili `tree` provjeravaju se:

- Neprozirnost teksture usrednjava se po mreži 32 x 32.
- Po površini (svaki izrezani trokut koji dijeli jednu teksturu), četiri točke po trokutu uzorkuju se u UV prostoru i važu se UV površinom trokuta.
- Ako je prosječna neprozirnost barem 0.05 i ispod **0.5**, cijela površina se izostavlja. Ispod 0.05 alfa za njegov sjenčar jasno znači nešto drugo (znak upozorenja koji uzorkuje 0.01), pa se površina zadržava čvrsta.
- Model kojem su sve površine izostavljene prijavljuje se: `N models left out as see-through (mostly holes in their texture)`.

Alat ocjenjuje cijelu površinu, a ne jedan trokut po jedan. Ocijenjeno po trokutu, pola svakog četverokuta bi preživjelo i ograde bi ispale kao redovi zubaca.

### Zgrade nacrtane cjelovito {#buildings-drawn-whole}

Grad gradi zgrade od modularnih dijelova: stotine tisuća oko jedne ulične staze, desetke milijuna trokuta čak i u najgrubljoj razini. Izostavljanje dijelova jednog po jednog ostavljalo je samotne zidne ploče kako stoje. Igra isporučuje i zamjene za cijele zgrade u `scene\hlod_tier_1\`, jednu mrežu po zgradi (osnova `hlod_tier_1_*`), već u svjetskim koordinatama kao teren:

- Svjetski okvir svake zamjene čita se iz okvira položaja njezine mreže (čitanje zaglavlja, ne dekodiranje). Za cijelu kartu to traje sekunde.
- Koriste se zamjene koje dodiruju okvir kruga i koridor.
- Svaki dio `buildings` čiji položaj pada unutar otiska zamjene (plus 0.5 m) se izbacuje, a umjesto njega se crta zamjena. Njezina udaljenost od vožnje mjeri se do najbližeg ruba zgrade.
- Sažetak kaže `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Uključeni slojevi {#switched-on-layers}

Ono što uključeni sloj postavlja izvozi se, ali odvojeno od svijeta slobodne vožnje, da ga preglednik može prikazati ili sakriti:

| Sloj | Dio |
|---|---|
| svijet slobodne vožnje | `structure:<category>` (kao prije) |
| sloj koji imenuje rutu podudarene utrke | `structure:event_<category>` |
| bilo koji drugi uključeni sloj | `structure:layer_<category>` |

Sažetak ih broji: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modeli koji su već u svjetskim koordinatama {#models-already-in-world-coordinates}

Nekoliko vrsta modela nije ni u jednoj datoteci postavljanja. Njihove mreže nose vlastiti položaj u svijetu, kao teren, pa ih ništa ne mora postaviti:

| Mapa pod `scene\models\` | Što je | Dio |
|---|---|---|
| `plots` | vlastito tlo mjesta održavanja: pod stadiona i unutrašnjost staze, mjesto festivala, trg | `ground:venue` |
| `plinths` (i svaki model imenovan `floor`, `ground` ili `road`) | tlo kojim je ulica uređena: sadilice, stepenice, popločenje parka | `ground:plinths` |
| `hda_infrastructure` (mostovi) | proceduralno izgrađeni mostovi | `structure:bridges` |

- Model se smatra u svjetskim koordinatama kada je središte njegova okvira dalje od **300 m** (`WORLD_REACH`) od vlastitog ishodišta. Modeli koje postavljaju datoteke postavljanja nalaze se unutar nekoliko stotina metara od svog.
- Ne crta se: zaklanjači, kablovi razapeti uz ceste, pozadina mora, krovovi i zaklanjači modularnih zgrada (zamjene crtaju te zgrade), kolizijski i vodeni volumeni.
- Svaki se čita iz okvira svojih mreža (čitanje zaglavlja), nekoliko sekundi za cijelu kartu, jednom po pokretanju.
- Dijelovi tla se nikad ne crtaju grublje i nikad se ne izostavljaju da bi stali u proračun, kao rubnjaci.

**Mjesto održavanja se reže cijelo.** Kada vožnja dodiruje vlastito tlo mjesta (`ground:venue`), koridor se proširuje na cijeli otisak tog tla plus `--margin`, pa tribine, zidovi i barijere oko stadiona dolaze s njim, a ne samo traka koju su krugovi koristili. Konzola ispisuje `through a venue (<model names>): cutting all of its ground, <n> km2`. Sokli ne proširuju izrez.

### Detalj i proračun {#detail-and-the-budget}

Pojasevi udaljenosti, proračun i koje kopije odlaze kada je proračun premali nalaze se na [Razine detalja i proračun](detail-budget.md).

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

## Sloj vlastite utrke {#the-races-own-layer}

Mnoge utrke postavljaju stvari koje ne postoje u slobodnoj vožnji: betonske zidove i ograde koje zatvaraju sporedne ceste, slogove guma, šatore, startni portal, tribine, zastave, transparente. Svaka utrka ih navodi u svojoj definiciji rute (`route<id>_<map>.rtd` u `routedefinitions.zip`, običan XML u običnom zip-u):

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

- **Što se dodaje.** Svaka instanca postavlja se kao kopija iz datoteke postavljanja. 16 brojeva transformacije su četiri retka: x, y i z osi modela (svaka skalirana) i njegov položaj u metrima igre. Treći redak je vektorski produkt prva dva. `Material` je varijanta koju kopija nosi. Dio je `structure:event_<kind>`, gdje je `<kind>` mapa pod `scene\models\` (barriers, props, infrastructure, signs; sve drugo se računa kao props), a čvor nosi glTF dodatke `{"layer": "event", "route": <id>}`.
- **Što se oduzima.** Kopija slobodne vožnje koja stoji unutar **0.1 m** od položaja skrivenog sredstva izostavlja se. Skriveno sredstvo na ishodištu je model u svjetskim koordinatama; njegov GUID instance traži se u `AssetManifest.xml` staze (popis `<Models>`: izvor modela, zatim GUID-ovi njegovih kopija) da bi se imenovao.
- **Tlo koje utrka skriva ostaje.** Utrka koja skriva tlo mjesta tamo postavlja vlastitu površinu. Kada ta površina nije među modelima koje staza isporučuje, skriveno tlo ostaje kao najbliže onome po čemu se vozi, a sažetak to kaže (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Ne crta se, ali se broji.** Markeri gledatelja (`crowd_proxies`: igra mnoštvo crta kao sprajtove iz njih) i kolizijski splajnovi (`.splinecol`). Konzola ih navodi: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Imovina rute za koju staza ne isporučuje model (svjetlosni sjajevi, neki znakovi, sadržaj koji igra strimuje) imenuje se u `placed names have no model in the archives`.

Postavljaju se samo kopije unutar koridora, kao i za sve drugo.

## Pisanje datoteke {#writing-the-file}

Dijelovi se pišu ovim redom: po pločici `terrain`, `verge`, `road` (svaki sa slikom pločice), zatim `water`, `tyre marks`, `markings` (ravni, zadnja dva podignuta), zatim svaki postavljeni dio sortiran po imenu. Koordinate su igrine vlastite (metri, Y gore). Vidi [Format izlaza](output-format.md).

Datoteka u svojim `asset.extras` glTF-a kaže što sadrži:

| Polje | Značenje |
|---|---|
| `course_format` | `2`: sloj vlastite utrke, mjesta i modeli u svjetskim koordinatama su u njoj. [`courses`](commands.md#courses) izvozi datoteku s nižim brojem (ili bez njega) ponovno |
| `route` | id podudarene rute, ili `null` |
| `event_copies`, `event_kinds` | koliko kopija sloja vlastite utrke je postavljeno, i njihove vrste |
| `hidden` | kopije slobodne vožnje izostavljene jer ih utrka uklanja |
| `venue` | modeli tla mjesta održavanja kroz koja vožnja prolazi |
| `layers` | uključeni slojevi koji su postavljeni |

## Što košta {#what-it-costs}

Grubi redovi veličine:

| Staza | Rezultat |
|---|---|
| kratka seoska staza | nekoliko stotina tisuća trokuta terena, preko milijun postavljenih; sekunde, ispod 100 MB |
| dugi sprint od točke do točke | koridor je mali dio okvira oko njega; oko minute, nekoliko stotina MB |
| ulična staza u gradu | tisuće barijera, rekvizita i znakova te cijele zgrade; uz automatski proračun do nekoliko stotina MB |

Kvadratni kilometar terena otvorenog svijeta je oko milijun trokuta.

## Provjere iza toga {#checks-behind-it}

Ovo su mjerenja napravljena dok je čitač pisan, kako piše u izvoru. Testovi ih ne ponavljaju osim ako je igra instalirana.

- Na probnoj stazi automobil stoji otprilike na svojoj visini vožnje iznad izvučenog tla (medijan ispod 0.2 m).
- Svaka uzorkovana pločica pada unutar kvadrata od 512 m koji njezino ime predviđa.
- Uzastopna postavljanja zaštitnih ograda su točno 4 m razmaka, a većina krajeva ograde pada unutar 5 cm od početka sljedeće.
- Rubnjaci stoje nekoliko centimetara iznad izvučenog tla, lica prema gore, unutar 5 m od vožnje (također test instalirane igre, vidi [Razvoj](development.md)).

## Ne crta se {#not-drawn}

- Drveće i grmlje osim uz `--trees`. Trava i mnoštvo nikad (igra ih crta kao sprajtove).
- Modeli vlastite utrke koje staza ne isporučuje (vidi [Sloj vlastite utrke](#the-races-own-layer)).
- Projicirani materijali dekala na modelima.
- Otisci znakova koji su alfa-stopljeni preko svoje ploče ispadaju neprozirni.
- Boja tla je rekonstrukcija gdje su asfalt, trava i šuma, a ne materijali terena same igre.
