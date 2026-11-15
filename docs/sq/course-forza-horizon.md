---
title: "Forza Horizon"
nav_order: 1
lang: "sq"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Eksporti i kursit: Forza Horizon {#course-export-forza-horizon}

Eksporti për Forza e lexon pistën drejtpërdrejt nga arkivat ForzaTech të lojës:
terren me rrugën, buzën dhe barin të ndara, një teksturë toke e pjekur nga
hartat e vetë lojës të tokës, dhe çdo model i vendosur me teksturën e vet (bordura,
parmakë, mure gomash, tabela, objekte, ndërtesa). Gjen gjithashtu në cilën nga garat e
lojës u drejtua xhiroja dhe shton atë që loja nxjerr vetëm për atë garë
(shtresa e saj e ngjarjes: barriera, tenda, portale, tribuna, flamuj), dhe
tokën e çdo vendi nëpër të cilin kalon drejtimi, si dyshemeja e një stadiumi.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Burimet: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Vetë formatet e kontejnerëve janë te [ForzaTech](reader-forzatech.md).

## Gjetja e lojës së instaluar {#finding-the-installed-game}

Askush nuk duhet të shkruajë një shteg si
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, ndaj shtegu zbulohet vetë:

1. **Bibliotekat Steam.** `config\libraryfolders.vdf` i Steam lexohet nga
   `C:\Program Files (x86)\Steam` ose `C:\Program Files\Steam`, dhe çdo hyrje `"path"`
   në të është një bibliotekë. `steamapps\common` i secilës bibliotekë kërkohet.
2. **Microsoft Store.** `C:\XboxGames` kërkohet nëse ekziston. Aty loja
   qëndron një nivel më poshtë, te `<game>\Content`.
3. Një **dosje loje** është çdo fëmijë i atyre dosjeve që ka një dosje
   `media\Tracks`, pavarësisht emrit.
4. Një **dosje pistë** është çdo dosje nën `media\Tracks` që mban një
   `GeoChunk0.minizip`. Llogaritet nga përmbajtja, jo nga emri, ndaj një pistë me një
   emër që askush nuk e ka parë gjendet prapë.

Nëse loja është gjetkë, jep dosjen e pistës me `--track`; shih
[Zgjidhja e problemeve](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` i kalon të gjitha këto.

Një dosje pistë mban atë që lexon eksporti:

| Skedari | Çfarë është |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arkivat: çdo model, teksturë dhe skedar vendosjeje, pa emra brenda |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | një rresht për çdo hyrje arkivi, sipas radhës së hyrjeve: burimi i vetëm i emrave |
| `AssetManifest.xml` | çdo teksturë që jep pista, me hash-in me të cilin materialet i referohen |

## Cila pistë {#which-track}

Një lojë jep më shumë se një dosje pistë (harta e botës së hapur, një garazh ose dy).
E duhura zgjidhet nga **koordinatat, jo nga emri**:

- Pyetja është kutia kufizuese e xhiros, e zgjeruar me `--margin`.
- Për çdo dosje pistë, katër manifestet `ChunkContentsMiniZip*.txt` lexohen
  si tekst, pa hapur arkiv. Çdo emër pllake terreni
  (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) mban pozicionin e saj në rrjetë.
  Mjeti numëron sa pllaka të dallueshme bien brenda kutisë.
- Fiton pista me më shumë pllaka aty. Nëse asnjë pistë nuk ka asnjë, eksporti ndalet
  me "none of the installed tracks (...) has terrain at x ..., z .... Those are
  the game's own metres, as its telemetry reports them."

Një pistë e tërë përgjigjet shumë nën një sekondë. Një përputhje emri mund të zgjedhë
hartën e gabuar, dhe një hartë e gabuar duket po aq bindëse sa e duhura.

Konsola thotë `on <track>, in <game folder>`.

## Cila garë {#which-race}

Loja jep secilën nga garat e saj si një rrugë me një numër, **route id**. Dy
skedarë i përkasin çdo rruge:

| Skedari | Çfarë mban |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | vija e drejtimit e AI-së së garës: një nyje 56 bajtëshe për çdo pikë nga bajti `0x60`, numri i nyjeve te `0x24`, çdo nyje duke filluar me pozicionin e saj (x, y, z) në metrat e lojës |
| `media\Stripped\gs\<map>\routedefinitions.zip` | një `route<id>_<map>.rtd` për garë: XML i thjeshtë që liston çfarë i shton gara botës dhe çfarë i heq (shih [Shtresa e vetë garës](#the-races-own-layer)) |

Xhiroja i përputhet një rruge duke u krahasuar me çdo vijë AI kutia e së cilës
mbivendoset me atë të xhiros:

- Nga çdo mostër xhiroje, largësia te pika më e afërt e vijës; dhe nga
  çdo pikë e vijës, largësia te mostra më e afërt e xhiros.
- Dy medianat mblidhen. Fiton rruga me shumën më të vogël nëse shuma
  është nën **30 m** (`MATCH`).
- Duhen të dyja drejtimet: një sprint i shkurtër shtrihet përgjatë një rruge të gjatë që përdor
  të njëjtën rrugë, dhe një xhiro e gjatë mbulon një rrugë të shkurtër.

Konsola thotë `the game's route <id> (driven line within <n> m of it)`, ose që
asnjë rrugë nuk përputhet. Pa përputhje, vendoset vetëm bota e lirë.

## Terreni {#terrain}

Si gjendet terreni (te `forzaterrain.py`):

- Manifestet e emërtojnë terrenin si një indeks hapësinor:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Dy numrat janë koordinata rrjete që **hapin nga 1023**, dhe çdo hap rrjete
  është një pllakë **512 m**. Pllaka `x-2046` është `-2046 / 1023 = -2`, që fillon te
  `-2 * 512 = -1024` m. Nëse i lexon emrat si metra, çdo kërkim gabon me një
  faktor dy dhe prapë kthen terren, nga pjesa e gabuar e hartës.
- Një pllakë mund të shfaqet tri herë: e thjeshtë, `_cb` dhe `_ul`. Të tria mbulojnë të njëjtën
  tokë. Merret një për pllakë, sipas kësaj radhe preference, sepse bashkimi i
  tyre do të trefishonte gjeometrinë në sipërfaqe që përputhen.
- Një pllakë lexohet vetëm nëse prek kutinë e xhiros **dhe** korridorin. Një pllakë
  që korridori nuk e prek nuk dekompresohet kurrë.
- Çdo `.modelbin` i një pllake të zgjedhur dekodohet **vetëm në nivelin e detajit 0**. Një
  pllakë mban katër nivele mbi të njëjtën tokë, dhe eksportimi i të gjithave e vë
  të njëjtin metër katror në skedar katër herë.
- Çdo rrjetë mban shkallën dhe zhvendosjen e vet në hapësirën botërore, ndaj një pllakë ulet aty ku e vë
  loja pa transformim instance. Trekëndëshat gjurma e të cilëve mbivendoset me
  kutinë mbahen, pastaj vetëm ata që arrijnë në korridor.
- Një rrjetë në një format që lexuesi e refuzon kalohet dhe numërohet
  (`N meshes could not be read`), ndaj një rezultat i hollë tregon pse.

Përmbledhja e terrenit printon numrin e kulmeve, trekëndëshave, rrjetave, pllakave
dhe shtrirjen x/y/z.

### Rrugë, buzë, terren, shenja, ujë {#road-verge-terrain-markings-water}

Emrat e materialeve nuk mund të thonë ku është rruga. Rreth një qarku, 94% e tokës
përdor material me shader rruge, sepse terreni pranë një rruge vizatohet me të dhe
shader-i vendos asfalt ose bar për piksel. Ndaj:

| Lloji | Vendoset nga |
|---|---|
| shirit rruge | **struktura e kulmeve**: shiritat e rrugës janë e vetmja tokë me një set të dytë UV (kanali 1); një trekëndësh të tre kulmet e të cilit e kanë është rrugë |
| asfalt kundrejt buze | brenda një shiriti rruge, **maska e asfaltit** e pllakës në qendrën e trekëndëshit: 0.5 ose më shumë është `road`, më pak është `verge` |
| shenja rruge | emri i materialit përputhet me `whiteline`, `yellowline` ose `decal` |
| shenja gomash | emri i materialit përputhet me `tyremark` ose `skid` (kontrollohet para shenjave të rrugës, sepse shenjat e gomave vijnë si `tyremark_decal_*`) |
| ujë | emri i materialit përputhet me `water`, `lake`, `river`, `paddy`, `ocean` ose `sea` |
| terren | çdo gjë tjetër |

Të matura në xhirot e regjistruara të qarkut të testit, pothuajse të gjitha mostrat bien mbi
trekëndëshat e shiritave të rrugës, dhe shumica dërrmuese në pjesën e asfaltit pasi maska
e ka ndarë buzën.

Maska e asfaltit ekziston vetëm kur teksturat e tokës piqen. Me
`--no-textures`, ose për një pllakë që i mungojnë hartat, shiritat e rrugës mbeten të plotë si
`road` dhe nuk ndahet asnjë buzë. Hartat që mungojnë kushtojnë detaj, kurrë gjeometri.

### Shtresat e lyera ngrihen {#painted-layers-are-lifted}

Shenjat e korsive dhe shenjat e gomave vijnë si trekëndësha më vete që shtrihen saktësisht në
rrugë. Loja i vizaton me një zhvendosje thellësie. Të vizatuara siç janë, rruga dhe boja
luftojnë për çdo piksel. Eksporti i jep çdo pjese shenje rruge dhe shenje gome kopjen e vet
të kulmeve, të ngritura **5 cm** (`DECAL_LIFT`) përgjatë normales së sipërfaqes, kështu
rruga poshtë saj nuk ngrihet gjithashtu.

### Normalet {#normals}

Normalet e terrenit vijnë nga arkivi. X-i i normales ruhet si
shorti i katërt i pozicionit, dhe y e z në atributin `NORMAL` (shih
[ForzaTech](reader-forzatech.md)). Nëse ndonjë kulm në nxjerrje i mungon
një normale, normalet e gjithë tokës llogariten nga trekëndëshat në vend të kësaj.

## Teksturat e tokës {#the-ground-texture}

Çdo pllakë terreni jep tri harta që mbulojnë katrorin e saj 512 m, në pesë rezolucione
(`_quality1` deri `_quality5`, më e madhja 2048 px, që është 25 cm për piksel):

| Harta | Modeli i emrit të skedarit | Çfarë mban (siç u mat) |
|---|---|---|
| main | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: normalja e detajit (x, z). A: më e ulët në asfalt dhe në tokë të ashpër |
| sub | `submap_x<X>_z<Z>_x<season>x_diff` | peshat e shtresave. B: e lartë në asfalt (239 në vijën e drejtuar, 165 pranë saj) |
| gloss | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: e ulët në asfalt (147 kundrejt 215). B: ngrihet në pyll |

Asnjë nga këto nuk është fotografi me ngjyra. Janë hyrjet me të cilat shader-i i terrenit të lojës
përzien shtresat e materialeve të veta, dhe ato shtresa nuk dekodohen. Ndaj
teksturat e pjekura janë **një interpretim, jo një kopje e pamjes së lojës**. Mban
*ku* është çdo lloj toke, në 25 cm, dhe e lyen me ngjyra fikse:

| Toka | RGB lineare | Pesha |
|---|---|---|
| bar (i shkurtër, afër pistës) | 0.30, 0.44, 0.18 | baza |
| e ashpër (më larg) | 0.40, 0.42, 0.22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| pyll | 0.13, 0.23, 0.10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0.20, 0.20, 0.21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Të dyja hartat duhet të bien dakord për asfaltin. Secila vetëm lë njolla gri në
bar kudo që kompresimi me blloqe tingëllon. Rezultati hijëzohet nga normalja e detajit e hartës main
kundrejt një drite fikse (`0.55 + 0.6 * lambert`), ndaj buzët e bordurave, brigjet
dhe gropat lexohen si reliev, dhe shkruhet si sRGB 8-bitësh.

Orientimi: rreshti i pikselit 0 është skaji **verior** i pllakës (z më i madh), kolona 0 skaji i saj
**perëndimor** (x më i vogël). Kjo u gjet duke projektuar xhirot e regjistruara mbi
maskën e asfaltit në të tetë mënyrat që mund të përmbyset ose rrotullohet një katror. Saktësisht një mënyrë
i vë ato në asfalt. UV-të rrjedhin nga kjo: `u = (x - x0) / 512`,
`v = 1 - (z - z0) / 512`.

Hartat lexohen në rezolucionin më të mirë të disponueshëm deri në cilësinë 5 dhe rimostrohen
në madhësinë e hartës main. Nëse imazhi i ngjyrave është më i madh se `--texture-size`, ai
zvogëlohet në atë madhësi me filtrim Lanczos. Maska e asfaltit mbahet gjithmonë në rezolucion të plotë, sepse ajo
vendos gjeometrinë. `--season` zgjedh hartat `x<season>x`. Një pllakë pa harta për
atë stinë vizatohet me ngjyra të sheshta, dhe konsola raporton
`N without maps`.

## Modelet e vendosura {#placed-models}

Terreni mban pozicionin e vet botëror. Asgjë tjetër jo. Ku qëndron çdo kopje e një
modeli regjistrohet në skedarë vendosjeje `.pgeo`, një për kategori për çdo qelizë
hapësinore:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Struktura e regjistrimit
është te [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Çfarë lexohet {#what-is-read}

- Skedarët e vendosjes filtrohen **sipas emrit**: madhësia e qelizës dhe pozicioni i qelizës në
  shteg japin katrorin e qelizës (`x * size` deri `(x + 1) * size`), dhe hapen vetëm qelizat
  që mbivendosen me kutinë e xhiros, në një kategori të dëshiruar.
- Kategoritë parazgjedhur: `barriers`, `props`, `signs`, `buildings`,
  `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` shton `trees`,
  `bushes` dhe `smashables`. Këto nuk lexohen kurrë: `grasstemplate`,
  `crowdtemplate` dhe `cwdspline` (bar dhe spektatorë: loja i vizaton si
  sprite të animuara, nuk ka gjeometri).
- Çdo skedar i përket një **shtrese**, e lexuar nga emri i tij pas
  `c<size>_<category>_`. Një fjalë niveli detaji (`do`, `so`, `ulc`, `ulp`, `cwd`)
  dhe një numër seksioni opsional është bota e lirë. Çdo gjë tjetër është një
  shtresë që loja e ndez: një shtresë kohe-ekzekutimi (`rt_0`), një aktivitet
  (`_tag_<name>_`), një objekt koleksioni, çdo gjë e arkivuar nën `evolving`. Një shtresë
  që emërton rrugë (`rt_x<id>`, për shembull `rt_x1023_x2201`) u përket atyre
  garave vetëm, dhe lexohet vetëm kur xhiroja i përputhet njërës prej tyre. Shih
  [Shtresat e ndezura](#switched-on-layers).
- Një kopje mbahet nëse pozicioni i saj është brenda kutisë dhe brenda korridorit.
  Përsëritjet e sakta (i njëjti pozicion dhe orientim deri në milimetër, të listuara nga
  dy qeliza fqinje) bashkohen.
- **Bordurat** janë objekte emri i modelit të të cilave fillon me `road_gen_rum` (shirita
  dridhjeje). Shkruhen si `ground:kerbs`, nuk thjeshtohen kurrë dhe nuk lihen kurrë
  jashtë, sepse një xhiro matet kundrejt tyre.

| Kategoria | Pjesa | Ngjyra rezervë (pa teksturë) |
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

### Gjeometria e modelit {#the-models-geometry}

Një emër i vendosur `<model>_3D` i referohet skedarëve të modelit `<model>_cluster###.i.modelbin`
(deri në një duzinë). Çdo trekëndësh mban një maskë të niveleve të detajit ku i përket:

- Nivelet e një modeli janë trekëndëshat e tij të shënuar shprehimisht për atë nivel. Nivelet shkojnë
  vazhdimisht nga 0, më i imti së pari.
- Trekëndëshat e shënuar `0xFFFF` (çdo nivel) janë pjesët e thyeshme, si
  shtyllat e një parmaku ose gomat e vetme të një grumbulli gomash. Mbivendosen me të gjithë modelin,
  dhe loja i vizaton në vend të tij sapo ai goditet e shpërndahet. Përdoren
  vetëm nga një model pa nivel të shënuar shprehimisht.
- Nënrrjetat shader-i i materialit të të cilave është një **decal** i projektuar lihen jashtë.

Çdo kopje vendoset me pozicionin e saj, boshtet x dhe y nga regjistrimi
(z = x kryq y), dhe shkallën. Normalet transformohen me shkallën e anasjellë.

### Cila teksturë {#which-texture}

Një material nuk emërton teksturat e veta. I liston si hash-e, dhe
`AssetManifest.xml` i pistës e hartëzon çdo hash (`SourceHash`) te një emër teksture. Lexohet vetëm
seksioni `<Textures>`, i cili ndalon leximin te `</Textures>` në një skedar që
mund të jetë dhjetëra megabajte. Pastaj:

1. Foleja `0x88B483AA` është ngjyra bazë në shader-in standard të mjedisit (çdo
   material i mostruar). Nëse materiali lidh një teksturë aty, përdoret ajo.
2. Përndryshe vendos lloji i vetë teksturës, që është fjala para GUID-it të saj:
   `_bclr_`, pastaj `_diff_`, pastaj `_colour_`.
3. Hartat e terrenit (`mainmap`, `submap`, `autogloss`) dhe paletat e tonit (`tint`,
   `worldtint`) nuk e ngjyrosin kurrë një model.

Ndaj një model ngjyroset nga ajo që lidh materiali i tij, jo nga një teksturë me emër si
modeli. Për shembull, `bar_rur_armco_crct_02_c` përdor teksturën e `..._02_a`.

Teksturat lexohen nga arkivat në rezolucionin më të vogël me të paktën
**256 px** gjerësi (`MODEL_TEXTURE`), zvogëlohet në 256 nëse është më e madhe, dhe ruhet si JPEG
RGB në `.glb`. Ngjyra e një parmaku në 256 px për katër metra është 1.6 cm për
piksel, dhe rreth 80 tekstura të tilla ngjasojnë në atlasin e shikuesit pranë pllakave
të tokës.

**Stinët.** `--season` ndërron një teksturë me binjaken e saj sezonale sipas emrit, me
GUID-in të injoruar (`..._xsummerx_bclr` në `..._xwinterx_bclr`, ose `..._bclr` në
`..._winter_bclr`), kur pista ka një. Me `--season winter`, përdoret edhe materiali
dimëror i një nënrrjete aty ku e emërton tabela e saj e varianteve.

**Variantet.** Një regjistrim nënrrjete hapet me një tabelë materialesh `(summer, winter)`,
një për çdo pamje që mund të veshë një kopje: pesë printime për një billboard, gjashtë ngjyra boje për një
grumbull gomash. Çdo regjistrim vendosjeje thotë cilin variant e vesh ajo kopje. Një nënrrjetë
me më pak variante se modeli përsërit të vetat.

**Blloku zëvendësues.** Atlasat e përbashkët të ndërtesave rezervojnë një bllok të plotë
RGB (255, 64, 0) për sipërfaqe që shader-i i ndërtesës i ngjyros nga tekstura të tjera.
Nëse më shumë se një e njëzeta e një teksture është brenda 12 nivelesh nga ajo ngjyrë, blloku
rilyhet me ngjyrën mesatare të teksturës vetë. Përndryshe një qytet del
portokalli.

### Sipërfaqet e tejdukshme {#see-through-surfaces}

Rrjetat me lidhje zinxhir dhe rrjetat janë katërkëndësha të vetëm me vrima në alfa të teksturës.
Të vizatuara të ngurta, një gardh është mur përmes pamjes së pistës. Sipërfaqet shader-i i
materialit të të cilave përputhet me `alphatest`, `alphablend`, `transmissive`, `anim_flag`,
`impostor`, `branch`, `bush` ose `tree` testohen:

- Opaciteti i teksturës mesatarizohet mbi një rrjetë 32 x 32.
- Për sipërfaqe (çdo trekëndësh i prerë që ndan një teksturë), katër pika për
  trekëndësh mostrohen në hapësirën UV dhe peshohen nga sipërfaqja UV e trekëndëshit.
- Nëse opaciteti mesatar është të paktën 0.05 dhe nën **0.5**, e gjithë sipërfaqja
  lihet jashtë. Nën 0.05 alfa qartë do të thotë diçka tjetër për shader-in e saj (një
  tabelë paralajmërimi që mostron 0.01), dhe sipërfaqja mbahet e ngurtë.
- Një model çdo sipërfaqe e të cilit u la jashtë raportohet:
  `N models left out as see-through (mostly holes in their texture)`.

Mjeti gjykon gjithë sipërfaqen dhe jo një trekëndësh në herë. Gjykuar
për trekëndësh, gjysma e çdo katërkëndëshi mbijetoi dhe gardhet dolën si rreshta dhëmbësh.

### Ndërtesat e vizatuara të plota {#buildings-drawn-whole}

Një qytet i ndërton ndërtesat nga pjesë modulare: qindra mijëra prej tyre
rreth një qarku rrugësh, dhjetëra miliona trekëndësha edhe në nivelin e tyre më të ashpër.
Lënia jashtë e pjesëve një nga një la pllaka muresh të vetmuara në këmbë. Loja jep gjithashtu
zëvendësues të ndërtesave të plota te `scene\hlod_tier_1\`, një rrjetë për ndërtesë
(rrënja `hlod_tier_1_*`), tashmë në koordinata botërore si terreni:

- Kutia botërore e çdo zëvendësuesi lexohet nga kutia e pozicionit të rrjetës së tij (një lexim kryeje,
  jo dekodim). Kjo zgjat sekonda për një hartë të tërë.
- Përdoren zëvendësuesit që prekin kutinë e xhiros dhe korridorin.
- Çdo pjesë `buildings` pozicioni i së cilës bie brenda gjurmës së një zëvendësuesi
  (plus 0.5 m) hiqet, dhe vizatohet zëvendësuesi. Largësia e tij nga
  drejtimi matet te skaji më i afërt i ndërtesës.
- Përmbledhja thotë `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Shtresat e ndezura {#switched-on-layers}

Çfarë vendos një shtresë e ndezur eksportohet, por veç botës së lirë,
që shikuesi ta shfaqë ose ta fshehë:

| Shtresa | Pjesa |
|---|---|
| bota e lirë | `structure:<category>` (si më parë) |
| një shtresë që emërton rrugën e garës së përputhur | `structure:event_<category>` |
| çdo shtresë tjetër e ndezur | `structure:layer_<category>` |

Përmbledhja i numëron: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modelet tashmë në koordinata botërore {#models-already-in-world-coordinates}

Disa lloje modelesh nuk janë në asnjë skedar vendosjeje. Rrjetat e tyre mbajnë pozicionin
e vet botëror, si terreni, ndaj asgjë nuk duhet t'i vendosë:

| Dosja nën `scene\models\` | Çfarë është | Pjesa |
|---|---|---|
| `plots` | toka e vetë një vendi: dyshemeja dhe fusha e një stadiumi, një vend festivali, një shesh | `ground:venue` |
| `plinths` (dhe çdo model me emrin `floor`, `ground` ose `road`) | toka me të cilën vishet një rrugë: vazo, shkallë, shtrimi i një parku | `ground:plinths` |
| `hda_infrastructure` (ura) | ura të ndërtuara procedurale | `structure:bridges` |

- Një model llogaritet në koordinata botërore kur mesi i kutisë së tij qëndron
  më shumë se **300 m** (`WORLD_REACH`) nga origjina e tij. Modelet e vendosura nga
  skedarët e vendosjes qëndrojnë brenda disa qindra metrash nga e tyra.
- Nuk vizatohen: bllokuesit e pamjes (occluders), kabllot e shtrira përgjatë rrugëve, sfondi i detit,
  çatitë dhe bllokuesit e ndërtesave modulare (zëvendësuesit i vizatojnë ato
  ndërtesa), vëllimet e përplasjes dhe të ujit.
- Secili lexohet nga kutia e rrjetave të tij (një lexim kryeje), disa sekonda për një
  hartë të tërë, një herë për ekzekutim.
- Pjesët e tokës nuk vizatohen kurrë më të ashpra dhe nuk lihen kurrë jashtë për t'u përshtatur me buxhetin,
  si bordurat.

**Një vend priten i plotë.** Kur drejtimi prek tokën e vetë një vendi
(`ground:venue`), korridori zgjerohet në gjithë gjurmën e asaj toke plus
`--margin`, kështu tribunat, muret dhe barrierat rreth një stadiumi vijnë me të, jo
vetëm shiriti që përdorën xhirot. Konsola thotë
`through a venue (<model names>): cutting all of its ground, <n> km2`. Bazamentet (plinths)
nuk e zgjerojnë prerjen.

### Detaji dhe buxheti {#detail-and-the-budget}

Brezat e largësisë, buxheti dhe cilat kopje shkojnë kur buxheti është shumë i vogël janë te
[Nivelet e detajit dhe buxheti](detail-budget.md).

### Përmbledhja e vendosjes {#placement-summary}

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

## Shtresa e vetë garës {#the-races-own-layer}

Shumë gara nxjerrin gjëra që nuk ekzistojnë në botën e lirë: mure betoni dhe
gardhe që mbyllin rrugët anësore, grumbuj gomash, tenda, një portal nisjeje,
tribuna, flamuj, banderola. Çdo garë i liston në përkufizimin e rrugës së saj
(`route<id>_<map>.rtd` në `routedefinitions.zip`, XML i thjeshtë në një zip të thjeshtë):

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

- **Çfarë shtohet.** Çdo instance vendoset si një kopje skedari vendosjeje. 16 numrat e
  transformimit janë katër rreshta: boshtet x, y dhe z të modelit (secili i shkallëzuar)
  dhe pozicioni i tij në metrat e lojës. Rreshti i tretë është prodhimi kryq i
  dy të parëve. `Material` është varianti që vesh kopja. Pjesa është
  `structure:event_<kind>`, ku `<kind>` është dosja nën `scene\models\`
  (barriers, props, infrastructure, signs; çdo gjë tjetër llogaritet props), dhe
  nyja mban ekstrat glTF `{"layer": "event", "route": <id>}`.
- **Çfarë hiqet.** Një kopje e botës së lirë që qëndron brenda **0.1 m** nga pozicioni i një
  aseti të fshehur lihet jashtë. Një aset i fshehur që qëndron në origjinë është një model
  në koordinata botërore; GUID-i i instance-it të tij kërkohet në
  `AssetManifest.xml` të pistës (lista `<Models>`: burimi i një modeli, pastaj GUID-et e
  kopjeve të tij) për ta emërtuar.
- **Toka që gara e fsheh mbahet.** Një garë që fsheh tokën e një vendi vendos
  sipërfaqen e vet aty. Kur ajo sipërfaqe nuk është mes modeleve që jep pista,
  toka e fshehur mbetet, si gjëja më e afërt me atë ku drejtohet, dhe
  përmbledhja e thotë (`kept <model>: the race hides it for a surface of its own
  that the track does not ship`).
- **Nuk vizatohen, por numërohen.** Shënuesit e spektatorëve (`crowd_proxies`: loja vizaton
  turmën si sprite prej tyre) dhe spline-et e përplasjes (`.splinecol`). Konsola i liston:
  `its own layer: <n> copies of <m> models, <k> free-roam
  objects hidden; not drawn: ...`.
- Asetet e rrugës për të cilat pista nuk jep model (shkëlqime dritash, disa tabela,
  përmbajtje që loja e transmeton) emërtohen te `placed names have no model in the
  archives`.

Vendosen vetëm kopjet brenda korridorit, si për çdo gjë tjetër.

## Shkrimi i skedarit {#writing-the-file}

Pjesët shkruhen në këtë radhë: për pllakë `terrain`, `verge`, `road` (secila me
imazhin e pllakës), pastaj `water`, `tyre marks`, `markings` (të sheshta, dy të fundit
të ngritura), pastaj çdo pjesë e vendosur e renditur sipas emrit. Koordinatat janë të vetë lojës
(metra, Y lart). Shih [Formati i daljes](output-format.md).

Skedari thotë çfarë mban në `asset.extras` të glTF:

| Fusha | Kuptimi |
|---|---|
| `course_format` | `2`: brenda ka shtresën e vetë garës, vendet dhe modelet në hapësirë botërore. [`courses`](commands.md#courses) e eksporton përsëri një skedar me numër më të ulët (ose pa numër) |
| `route` | id-ja e rrugës së përputhur, ose `null` |
| `event_copies`, `event_kinds` | sa kopje të shtresës së vetë garës u vendosën, dhe llojet e tyre |
| `hidden` | kopjet e botës së lirë të lëna jashtë sepse gara i heq |
| `venue` | modelet e tokës së vendit nëpër të cilat kalon drejtimi |
| `layers` | shtresat e ndezura të vendosura |

## Sa kushton {#what-it-costs}

Rendet e përafërta të madhësisë:

| Kursi | Rezultati |
|---|---|
| një qark i shkurtër fshati | disa qindra mijëra trekëndësha terreni, mbi një milion të vendosur; sekonda, nën 100 MB |
| një sprint i gjatë pikë-në-pikë | korridori është një pjesë e vogël e kutisë rreth tij; rreth një minutë, disa qindra MB |
| një qark rrugësh qyteti | mijëra barriera, objekte e tabela dhe ndërtesa të plota; me buxhetin automatik deri në disa qindra MB |

Një kilometër katror terren bote të hapur është rreth një milion trekëndësha.

## Kontrollet pas tij {#checks-behind-it}

Këto janë matje të bëra kur u shkrua lexuesi, siç thuhet në
burim. Testet nuk i ekzekutojnë përsëri përveç nëse loja është e instaluar.

- Në qarkun e testit, makina qëndron rreth lartësisë së saj të udhëtimit mbi tokën e nxjerrë (mediana nën 0.2 m).
- Çdo pllakë e mostruar bie brenda katrorit 512 m që parashikon emri i saj.
- Vendosjet e njëpasnjëshme të parmakëve janë saktësisht 4 m larg, dhe shumica e skajeve të parmakëve bien brenda 5 cm nga fillimi i tjetrit.
- Bordurat qëndrojnë disa centimetra mbi tokën e nxjerrë, me fytyrë lart, brenda 5 m nga drejtimi (gjithashtu test me lojë të instaluar, shih [Zhvillimi](development.md)).

## Çfarë nuk vizatohet {#not-drawn}

- Pemët dhe shkurret përveç me `--trees`. Bari dhe turmat kurrë (loja i vizaton si sprite).
- Modelet e vetë garës që pista nuk i jep (shih [Shtresa e vetë garës](#the-races-own-layer)).
- Materialet decal të projektuara në modele.
- Printimet e tabelave të përziera me alfa mbi bordin e tyre dalin të errëta (opake).
- Ngjyra e tokës është një rindërtim i vendit ku janë asfalti, bari dhe pylli, jo materialet e vetë terrenit të lojës.
