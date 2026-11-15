---
title: Forza Horizon
nav_order: 1
lang: "ro"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Exportul traseului: Forza Horizon {#course-export-forza-horizon}

Exportul Forza citește traseul direct din arhivele ForzaTech ale jocului: terenul cu drumul, bordura și iarba deosebite una de alta, o textură de sol coaptă din hărțile de sol ale jocului, și fiecare model plasat în propria lui textură (borduri, parapete, ziduri de cauciucuri, indicatoare, recuzită, clădiri). Găsește și care dintre cursele jocului a fost parcursă în turul dat și adaugă ce scoate jocul pentru acea cursă singură (stratul ei de evenimente: bariere, corturi, portaluri, tribune, steaguri), plus solul oricărui loc prin care trece conducerea, precum podeaua unui stadion.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Surse: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Formatele de containere în sine sunt descrise în [ForzaTech](reader-forzatech.md).

## Găsirea jocului instalat {#finding-the-installed-game}

Nimeni nu ar trebui să tasteze o cale ca
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, deci calea se află singură:

1. **Bibliotecile Steam.** Fișierul `config\libraryfolders.vdf` al Steam se citește din `C:\Program Files (x86)\Steam` sau `C:\Program Files\Steam`, iar fiecare intrare `"path"` din el este o bibliotecă. Se caută `steamapps\common` al fiecărei biblioteci.
2. **Microsoft Store.** Se caută `C:\XboxGames`, dacă există. Acolo jocul se află cu un nivel mai jos, în `<game>\Content`.
3. Un **folder de joc** este orice copil al acestor foldere care are un folder `media\Tracks`, indiferent de nume.
4. Un **folder de circuit** este orice folder sub `media\Tracks` care conține un `GeoChunk0.minizip`. Se recunoaște după conținut, nu după nume, deci un circuit sub un nume pe care nimeni nu l-a văzut încă tot se găsește.

Dacă jocul se află în altă parte, dați folderul circuitului cu `--track`; vedeți [Depanarea](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` sare peste toate acestea.

Un folder de circuit conține ce citește exportul:

| Fișier | Ce este |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arhivele: fiecare model, textură și fișier de plasare, fără nume în interior |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | o linie pentru fiecare intrare a arhivei, în ordinea intrărilor: singura sursă de nume |
| `AssetManifest.xml` | fiecare textură pe care o livrează circuitul, cu hash-ul prin care materialele se referă la ea |

## Care circuit {#which-track}

Un joc livrează mai multe foldere de circuit (harta lumii deschise, un garaj sau două). Circuitul corect se alege după **coordonate, nu după nume**:

- Cutia de delimitare a turului, lărgită cu `--margin`, este întrebarea.
- Pentru fiecare folder de circuit, cele patru manifeste `ChunkContentsMiniZip*.txt` se citesc ca text, fără să se deschidă vreo arhivă. Fiecare nume de placă de teren (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) poartă poziția lui în grilă. Instrumentul numără câte plăci distincte cad în cutie.
- Circuitul cu cele mai multe plăci acolo câștigă. Dacă niciun circuit nu are vreuna, exportul se oprește cu "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Un circuit întreg răspunde în mai puțin de o secundă. O potrivire după nume ar putea alege harta greșită, iar o hartă greșită arată la fel de plauzibil ca cea corectă.

Consola spune `on <track>, in <game folder>`.

## Care cursă {#which-race}

Jocul livrează fiecare dintre curselele lui ca o rută cu un număr, **id-ul rutei**. Două fișiere aparțin fiecărei rute:

| Fișier | Ce conține |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | linia de conducere a AI-ului pentru cursă: un nod de 56 de octeți din octetul `0x60`, numărul de noduri la `0x24`, fiecare nod începând cu poziția lui (x, y, z) în metrii jocului |
| `media\Stripped\gs\<map>\routedefinitions.zip` | un `route<id>_<map>.rtd` pentru fiecare cursă: XML simplu care listează ce adaugă cursa în lume și ce scoate din ea (vedeți [Stratul propriu al cursei](#the-races-own-layer)) |

Turul se potrivește cu o rută comparându-l cu fiecare linie AI a cărei cutie se suprapune cu a lui:

- Din fiecare eșantion al turului, distanța până la cel mai apropiat punct al liniei; și din fiecare punct al liniei, distanța până la cel mai apropiat eșantion al turului.
- Cele două mediane se adună. Ruta cu cea mai mică sumă câștigă dacă suma este sub **30 m** (`MATCH`).
- Sunt necesare ambele direcții: un sprint scurt se află de-a lungul unei rute lungi care folosește același drum, iar un tur lung acoperă o rută scurtă.

Consola spune `the game's route <id> (driven line within <n> m of it)`, sau că nicio rută nu se potrivește. Fără potrivire, se plasează doar lumea liberă.

## Terenul {#terrain}

Cum se găsește terenul (în `forzaterrain.py`):

- Manifestele numesc terenul ca un index spațial:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Cele două numere sunt coordonate de grilă care **cresc din 1023 în 1023**, iar fiecare pas de grilă este un **circuit de 512 m**. Placa `x-2046` este `-2046 / 1023 = -2`, care începe la `-2 * 512 = -1024` m. Dacă citiți numele ca metri, fiecare căutare greșește cu un factor de doi și totuși returnează teren, din altă parte a hărții.
- O placă poate apărea de trei ori: simplă, `_cb` și `_ul`. Toate trei acoperă același sol. Se ia una pe placă, în ordinea aceasta de preferință, pentru că a le îmbina ar tripla geometria în suprafețe care coincid.
- O placă se citește doar dacă atinge cutia turului **și** coridorul. O placă pe care coridorul nu o atinge nu se decomprimă niciodată.
- Fiecare `.modelbin` al unei plăci alese se decodează doar la **nivelul de detaliu 0**. O placă are patru niveluri peste același sol, iar exportarea tuturor ar pune același metru pătrat de patru ori în fișier.
- Fiecare mesh poartă propria lui scară și deplasare în spațiul lumii, astfel încât o placă ajunge unde o pune jocul fără nicio transformare a instanței. Triunghiurile a căror amprentă se suprapune cu cutia se păstrează, apoi doar cele care ajung în coridor.
- Un mesh într-un format pe care cititorul îl refuză este sărit și numărat (`N meshes could not be read`), ca un rezultat slab să spună de ce.

Rezumatul terenului afișează numărul de vârfuri, de triunghiuri, de mesh-uri și de plăci, și extinderea pe x/y/z.

### Drum, margine, teren, marcaje, apă {#road-verge-terrain-markings-water}

Numele materialelor nu pot spune unde este drumul. În jurul unui circuit, 94% din sol folosește un material cu shader de drum, pentru că terenul de lângă un drum este desenat cu el, iar shader-ul decide asfalt sau iarbă pe pixel. Deci:

| Tip | Decis de |
|---|---|
| fâșia de drum | **layout-ul vârfurilor**: fâșiile de drum sunt singurul sol cu un al doilea set UV (canalul 1); un triunghi ale cărui trei vârfuri îl au este drum |
| asfalt sau margine | în interiorul unei fâșii de drum, **masca de asfalt** a plăcii în centrul triunghiului: 0,5 sau mai mult este `road`, mai puțin este `verge` |
| marcaje | numele materialului se potrivește cu `whiteline`, `yellowline` sau `decal` |
| urme de cauciucuri | numele materialului se potrivește cu `tyremark` sau `skid` (verificat înaintea marcajelor, pentru că urmele de cauciucuri vin ca `tyremark_decal_*`) |
| apă | numele materialului se potrivește cu `water`, `lake`, `river`, `paddy`, `ocean` sau `sea` |
| teren | orice altceva |

Măsurat pe tururile înregistrate pe circuitul de test, aproape toate eșantioanele cad pe triunghiuri de fâșie de drum, iar marea majoritate pe partea de asfalt după ce masca a separat marginea.

Masca de asfalt există doar când se coc texturile de sol. Cu `--no-textures`, sau pentru o placă ale cărei hărți lipsesc, fâșiile de drum rămân întregi ca `road` și nu se separă nicio margine. Hărțile lipsă costă detaliu, niciodată geometrie.

### Straturile pictate sunt ridicate {#painted-layers-are-lifted}

Marcajele de bandă și urmele de cauciucuri vin ca triunghiuri proprii, așezate exact în drum. Jocul le desenează cu o deplasare de adâncime. Desenate așa cum sunt, drumul și vopseaua se bat la fiecare pixel. Exportul dă fiecărei piese de marcaj și de urme de cauciucuri propria copie a vârfurilor, ridicată cu **5 cm** (`DECAL_LIFT`) de-a lungul normalei suprafeței, astfel încât drumul de sub ea să nu fie ridicat și el.

### Normale {#normals}

Normalele terenului vin din arhivă. Componenta x a normalei este stocată ca al patrulea short al poziției, iar y și z în atributul `NORMAL` (vedeți [ForzaTech](reader-forzatech.md)). Dacă vreun vârf din extragere nu are normală, normalele pentru tot solul se calculează din triunghiuri.

## Textura solului {#the-ground-texture}

Fiecare placă de teren livrează trei hărți care acoperă pătratul ei de 512 m, în cinci rezoluții (`_quality1` până la `_quality5`, cea mai mare de 2048 px, adică 25 cm un pixel):

| Hartă | Model de nume de fișier | Ce conține (măsurat) |
|---|---|---|
| principală | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: normala de detaliu (x, z). A: mai jos pe asfalt și pe terenul accidentat |
| secundară | `submap_x<X>_z<Z>_x<season>x_diff` | greutățile straturilor. B: ridicat pe asfalt (239 pe linia condusă, 165 alături) |
| luciu | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: scăzut pe asfalt (147 față de 215). B: crește în pădure |

Niciuna dintre acestea nu este o fotografie în culori. Sunt intrările pe care le amestecă shader-ul de teren al jocului cu straturile lui de material, iar straturile acelea nu sunt decodate. Deci textura coaptă este **o interpretare, nu o copie a aspectului jocului**. Păstrează *unde* este fiecare fel de sol, la 25 cm, și îl pictează în culori fixe:

| Sol | RGB liniar | Pondere |
|---|---|---|
| iarbă (scurtă, lângă traseu) | 0,30, 0,44, 0,18 | baza |
| aspru (mai departe) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| pădure | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Ambele hărți trebuie să fie de acord pentru asfalt. Oricare dintre ele singură lasă pete gri în iarbă acolo unde inelează compresia pe blocuri. Rezultatul este umbrit de normala de detaliu a hărții principale față de o lumină fixă (`0.55 + 0.6 * lambert`), astfel încât buzele bordurilor, malurile și făgașele se citesc ca relief, și este scris ca sRGB pe 8 biți.

Orientarea: rândul 0 al pixelilor este marginea de **nord** a plăcii (z cel mai mare), coloana 0 marginea de **vest** (x cel mai mic). S-a aflat proiectând tururile înregistrate pe masca de asfalt în toate cele opt moduri în care se poate răsuci sau oglindi un pătrat. Exact un mod le pune pe asfalt. UV-urile urmează din asta: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Hărțile se citesc la cea mai bună rezoluție disponibilă până la calitatea 5 și se reeșantionează la mărimea hărții principale. Dacă imaginea de culoare este mai mare decât `--texture-size`, se micșorează apoi la acea mărime cu filtrul Lanczos. Masca de asfalt se păstrează mereu la rezoluție completă, pentru că decide geometria. `--season` alege hărțile `x<season>x`. O placă fără hărți pentru acel anotimp se desenează în culori plate, iar consola raportează `N without maps`.

## Modele plasate {#placed-models}

Terenul poartă propria poziție în lume. Nimic altceva nu. Unde stă fiecare copie a unui model este înregistrat în fișiere de plasare `.pgeo`, câte unul pe categorie și pe celulă spațială:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Layout-ul înregistrărilor este în [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Ce se citește {#what-is-read}

- Fișierele de plasare se filtrează **după nume**: dimensiunea celulei și poziția celulei din cale dau pătratul celulei (`x * size` până la `(x + 1) * size`), iar doar celulele care se suprapun cu cutia turului, dintr-o categorie dorită, se deschid.
- Categoriile implicite: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` adaugă `trees`, `bushes` și `smashables`. Acestea nu se citesc niciodată: `grasstemplate`, `crowdtemplate` și `cwdspline` (iarbă și spectatori: jocul le desenează ca sprite-uri animate, nu există geometrie).
- Fiecare fișier aparține unui **strat**, citit din numele lui după `c<size>_<category>_`. Un cuvânt de nivel de detaliu (`do`, `so`, `ulc`, `ulp`, `cwd`) și un număr de secțiune opțional este lumea liberă. Orice altceva este un strat pe care jocul îl pornește: un strat de rulare (`rt_0`), o activitate (`_tag_<name>_`), un obiect de colectare, orice trecut la `evolving`. Un strat care numește rute (`rt_x<id>`, de exemplu `rt_x1023_x2201`) aparține doar acelor curse și se citește doar dacă turul s-a potrivit cu una dintre ele. Vedeți [Straturile pornite](#switched-on-layers).
- O copie se păstrează dacă poziția ei este în interiorul cutiei și al coridorului. Repetările exacte (aceeași poziție și orientare până la milimetru, listate de două celule vecine) se îmbină.
- **Bordurile** sunt recuzită al cărei nume de model începe cu `road_gen_rum` (benzi de zgomot). Se scriu ca `ground:kerbs`, nu se simplifică și nu se lasă afară niciodată, pentru că un tur se măsoară față de ele.

| Categorie | Parte | Culoare de rezervă (fără textură) |
|---|---|---|
| borduri | `ground:kerbs` | 0,60, 0,12, 0,10 |
| bariere | `structure:barriers` | 0,50, 0,50, 0,50 |
| recuzită | `structure:props` | 0,45, 0,35, 0,25 |
| indicatoare | `structure:signs` | 0,70, 0,70, 0,70 |
| clădiri | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastructură | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| poduri | `structure:bridges` | 0,45, 0,45, 0,45 |
| stânci | `structure:rocks` | 0,30, 0,28, 0,25 |
| obiecte care se sparg | `structure:smashables` | 0,12, 0,22, 0,06 |
| copaci, tufișuri | `structure:trees` | 0,10, 0,20, 0,05 |

### Geometria modelului {#the-models-geometry}

Un nume plasat `<model>_3D` se referă la fișierele modelului `<model>_cluster###.i.modelbin` (până la o duzină). Fiecare triunghi poartă o mască a nivelurilor de detaliu la care aparține:

- Nivelurile unui model sunt triunghiurile lui marcate explicit pentru acel nivel. Nivelurile merg continuu de la 0, cel mai fin primul.
- Triunghiurile marcate `0xFFFF` (fiecare nivel) sunt bucățile care se sparg, precum stâlpii unei parapet sau roțile separate ale unui zid de cauciucuri. Acoperă tot modelul, iar jocul le desenează în locul lui odată ce a fost făcut bucăți. Se folosesc doar la un model fără niciun nivel marcat explicit.
- Submeshurile al căror shader de material este un **decal** proiectat se lasă afară.

Fiecare copie se plasează cu poziția ei, cu axele x și y din înregistrare (z = x cross y), și cu scara ei. Normalele se transformă cu inversa scării.

### Care textură {#which-texture}

Un material nu își numește texturile. Le listează ca hash-uri, iar `AssetManifest.xml` al circuitului mapează fiecare hash (`SourceHash`) la un nume de textură. Se citește doar secțiunea `<Textures>`, care se oprește la `</Textures>` într-un fișier care poate avea zeci de megaocteți. Apoi:

1. Slotul `0x88B483AA` este culoarea de bază în shader-ul standard de mediu (fiecare material eșantionat). Dacă materialul leagă acolo o textură, aceea se folosește.
2. Altfel, tipul propriu al texturii decide, care este cuvântul dinaintea GUID-ului său: `_bclr_`, apoi `_diff_`, apoi `_colour_`.
3. Hărțile de teren (`mainmap`, `submap`, `autogloss`) și paletele de nuanțe (`tint`, `worldtint`) nu colorează niciodată un model.

Deci un model este colorat de ce leagă materialul lui, nu de o textură numită ca modelul. De exemplu, `bar_rur_armco_crct_02_c` folosește textura lui `..._02_a`.

Textura se citește din arhive la cea mai mică rezoluție de cel puțin **256 px** pe latură (`MODEL_TEXTURE`), micșorată la 256 dacă este mai mare, și se stochează ca JPEG RGB în `.glb`. Culoarea unei parapete la 256 px pe patru metri este 1,6 cm un pixel, iar în jur de 80 de astfel de texturi încap în atlasul vizualizatorului alături de plăcile de sol.

**Anotimpuri.** `--season` schimbă o textură cu geamănul ei de anotimp după nume, cu GUID-ul ignorat (`..._xsummerx_bclr` cu `..._xwinterx_bclr`, sau `..._bclr` cu `..._winter_bclr`), dacă circuitul are unul. Cu `--season winter`, materialul de iarnă al unui submesh se folosește și acolo unde tabelul lui de variante numește unul.

**Variante.** Un record de submesh începe cu un tabel de materiale `(vară, iarnă)`, unul pentru fiecare înfățișare pe care o poate purta o copie: cinci tipare pentru un panou publicitar, șase culori de vopsea pentru un zid de cauciucuri. Fiecare record de plasare spune ce variantă poartă acea copie. Un submesh cu mai puține variante decât modelul își repetă propriile.

**Blocul de rezervă.** Atlasele comune de clădiri rezervă un bloc RGB plin (255, 64, 0) pentru suprafețele pe care shader-ul clădirii le colorează din alte texturi. Dacă mai mult de o douăzecime dintr-o textură se află la cel mult 12 niveluri de culoarea aceea, blocul se repictează în culoarea medie a texturii. Altfel un oraș iese portocaliu.

### Suprafețe transparente {#see-through-surfaces}

Gardurile din plasă de sârmă și plasele sunt patrulatere simple cu găuri în canalul alfa al texturii. Desenate pline, un gard devine un zid peste vederea circuitului. Suprafețele al căror shader de material se potrivește cu `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` sau `tree` sunt testate:

- Opacitatea texturii se mediază pe o grilă de 32 x 32.
- Pe suprafață (fiecare triunghi decupat care împarte o textură), patru puncte pe triunghi se eșantionează în spațiul UV și se ponderează cu aria UV a triunghiului.
- Dacă opacitatea medie este cel puțin 0,05 și sub **0,5**, întreaga suprafață se lasă afară. Sub 0,05 canalul alfa înseamnă altceva pentru shader-ul lui (un semn de avertizare care eșantionează 0,01), iar suprafața se păstrează plină.
- Un model a cărui fiecare suprafață a fost lăsată afară este raportat: `N models left out as see-through (mostly holes in their texture)`.

Instrumentul judecă întreaga suprafață, nu un triunghi pe rând. Judecată pe triunghi, jumătate din fiecare patrulater supraviețuia, iar gardurile ieșeau ca rânduri de dinți.

### Clădiri desenate întregi {#buildings-drawn-whole}

Un oraș își construiește clădirile din piese modulare: sute de mii în jurul unui circuit urban, zeci de milioane de triunghiuri chiar la cel mai grosier nivel. Lăsarea pieselor afară una câte una lăsa în picioare pereți singuri. Jocul livrează și reprezentări întregi ale clădirilor în `scene\hlod_tier_1\`, câte un mesh pentru fiecare clădire (rădăcina `hlod_tier_1_*`), deja în coordonate lume, ca terenul:

- Cutia lumii fiecărei reprezentări se citește din cutia de poziție a mesh-ului ei (o citire de antet, nu o decodare). Durează secunde pentru o hartă întreagă.
- Reprezentările care ating cutia turului și coridorul se folosesc.
- Fiecare piesă `buildings` a cărei poziție cade în interiorul amprentei unei reprezentări (plus 0,5 m) se elimină, iar reprezentarea se desenează în locul ei. Distanța ei până la conducere se măsoară până la marginea cea mai apropiată a clădirii.
- Rezumatul spune `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Straturile pornite {#switched-on-layers}

Ce plasează un strat pornit se exportă, dar separat de lumea liberă, ca vizualizatorul să îl poată arăta sau ascunde:

| Strat | Parte |
|---|---|
| lumea liberă | `structure:<category>` (ca înainte) |
| un strat care numește ruta cursei potrivite | `structure:event_<category>` |
| orice alt strat pornit | `structure:layer_<category>` |

Rezumatul le numără: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modele deja în coordonate lume {#models-already-in-world-coordinates}

Câteva feluri de modele nu sunt în niciun fișier de plasare. Meshurile lor poartă propria poziție în lume, ca terenul, deci nimic nu trebuie să le plaseze:

| Folder sub `scene\models\` | Ce este | Parte |
|---|---|---|
| `plots` | solul propriu al unui loc: podeaua și interiorul unui stadion, un sit de festival, o piață | `ground:venue` |
| `plinths` (și orice model numit `floor`, `ground` sau `road`) | sol cu care este împodobit un stradă: jardiniere, trepte, pavajul unui parc | `ground:plinths` |
| `hda_infrastructure` (poduri) | poduri construite procedural | `structure:bridges` |

- Un model se consideră în coordonate lume când mijlocul cutiei lui se află la mai mult de **300 m** (`WORLD_REACH`) de originea lui. Modelele plasate de fișierele de plasare stau la câteva sute de metri de a lor.
- Nu se desenează: obturatoarele, cablurile întinse de-a lungul drumurilor, fundalul mării, acoperișurile și obturatoarele clădirilor modulare (reprezentările desenează acele clădiri), volumele de coliziune și de apă.
- Fiecare se citește din cutia meshurilor lui (o citire de antet), câteva secunde pentru o hartă întreagă, o dată pe rulare.
- Piesele de sol nu se desenează niciodată mai grosier și nu se lasă afară pentru a încăpea în buget, ca bordurile.

**Un loc se taie întreg.** Când conducerea atinge solul propriu al unui loc (`ground:venue`), coridorul se lărgește la întreaga amprentă a acelui sol plus `--margin`, astfel încât tribunele, zidurile și barierele din jurul unui stadion vin odată cu el, nu doar fâșia pe care au parcurs-o tururile. Consola spune `through a venue (<model names>): cutting all of its ground, <n> km2`. Soclurile nu lărgesc tăierea.

### Detaliul și bugetul {#detail-and-the-budget}

Benzile de distanță, bugetul și care copii pleacă atunci când bugetul e prea mic sunt în [Nivelurile de detaliu și bugetul](detail-budget.md).

### Rezumatul plasării {#placement-summary}

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

## Stratul propriu al cursei {#the-races-own-layer}

Multe curse scot lucruri care nu există în lumea liberă: pereți și garduri din beton care închid drumuri laterale, stive de cauciucuri, corturi, un portal de start, tribune, steaguri, bannere. Fiecare cursă le listează în definiția ei de rută (`route<id>_<map>.rtd` în `routedefinitions.zip`, XML simplu într-un zip simplu):

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

- **Ce se adaugă.** Fiecare instanță se plasează ca o copie dintr-un fișier de plasare. Cele 16 numere ale transformării sunt patru rânduri: axele x, y și z ale modelului (fiecare scalată) și poziția lui în metrii jocului. Al treilea rând este produsul vectorial al primelor două. `Material` este varianta pe care o poartă copia. Partea este `structure:event_<kind>`, `<kind>` fiind folderul de sub `scene\models\` (barriers, props, infrastructure, signs; orice altceva contează ca props), iar nodul poartă extras-urile glTF `{"layer": "event", "route": <id>}`.
- **Ce se scoate.** O copie din lumea liberă care stă la cel mult **0,1 m** de poziția unui obiect ascuns este lăsată afară. Un obiect ascuns care stă în origine este un model în coordonate lume; GUID-ul instanței lui se caută în `AssetManifest.xml` al circuitului (lista `<Models>`: sursa unui model, apoi GUID-urile copiilor lui) ca să i se dea numele.
- **Solul ascuns de cursă se păstrează.** O cursă care ascunde solul unui loc își așază propria suprafață acolo. Când acea suprafață nu se află printre modelele pe care le livrează circuitul, solul ascuns rămâne, ca cel mai apropiat lucru de ceea ce se conduce pe el, iar rezumatul o spune (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Nu se desenează, dar se numără.** Markerii de spectatori (`crowd_proxies`: jocul desenează mulțimea ca sprite-uri din ei) și splinele de coliziune (`.splinecol`). Consola le listează: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Modelele pe care le adaugă cursa și pe care circuitul nu livrează un model pentru ele (strălucirile de lumină, unele indicatoare, conținut pe care jocul îl transmite în flux) sunt numite în `placed names have no model in the archives`.

Doar copiile din interiorul coridorului se plasează, ca pentru orice altceva.

## Scrierea fișierului {#writing-the-file}

Părțile se scriu în ordinea aceasta: pe placă `terrain`, `verge`, `road` (fiecare cu imaginea plăcii), apoi `water`, `tyre marks`, `markings` (plate, ultimele două ridicate), apoi fiecare parte plasată, sortată după nume. Coordonatele sunt ale jocului (metri, Y în sus). Vedeți [Formatul de ieșire](output-format.md).

Fișierul spune ce conține în `asset.extras` al glTF:

| Câmp | Înseamnă |
|---|---|
| `course_format` | `2`: stratul propriu al cursei, locurile și modelele în coordonate lume sunt în el. [`courses`](commands.md#courses) exportă din nou un fișier cu un număr mai mic (sau fără) |
| `route` | id-ul rutei potrivite, sau `null` |
| `event_copies`, `event_kinds` | câte copii ale stratului propriu al cursei s-au plasat și tipurile lor |
| `hidden` | copii din lumea liberă lăsate afară pentru că cursa le elimină |
| `venue` | modelele de sol ale locurilor prin care trece conducerea |
| `layers` | straturile pornite plasate |

## Cât costă {#what-it-costs}

Ordine de mărime:

| Traseu | Rezultat |
|---|---|
| un circuit scurt de țară | câteva sute de mii de triunghiuri de teren, peste un milion plasate; secunde, sub 100 MB |
| un sprint lung de la punct la punct | coridorul este o mică fracțiune din cutia din jurul lui; un minut, câteva sute de MB |
| un circuit de stradă urbană | mii de bariere, recuzită și indicatoare și clădiri întregi; cu bugetul automat până la câteva sute de MB |

Un kilometru pătrat de teren de lume deschisă este aproximativ un milion de triunghiuri.

## Verificările din spatele lui {#checks-behind-it}

Acestea sunt măsurători făcute când a fost scris cititorul, cum spune sursa. Nu sunt refăcute de teste decât dacă jocul este instalat.

- Pe circuitul de test, mașina stă aproximativ la înălțimea ei de mers deasupra solului extras (mediană sub 0,2 m).
- Fiecare placă eșantionată cade în pătratul de 512 m prezis de numele ei.
- Plasările consecutive de parapete sunt exact la 4 m distanță, iar majoritatea capetelor de parapet se află la 5 cm de începutul următoarei.
- Bordurile stau cu câțiva centimetri deasupra solului extras, cu fețele în sus, la cel mult 5 m de conducere (și un test pe jocul instalat, vedeți [Dezvoltarea](development.md)).

## Ce nu se desenează {#not-drawn}

- Copacii și tufișurile, dacă nu este `--trees`. Iarba și mulțimile niciodată (jocul le desenează ca sprite-uri).
- Modelele proprii ale unei curse pe care circuitul nu le livrează (vedeți [Stratul propriu al cursei](#the-races-own-layer)).
- Materialele de decal proiectate pe modele.
- Imprimările de indicatoare care sunt amestecate alfa peste placa lor apar opace.
- Culoarea solului este o reconstrucție a locului unde sunt asfaltul, iarba și pădurea, nu materialele de teren ale jocului.
