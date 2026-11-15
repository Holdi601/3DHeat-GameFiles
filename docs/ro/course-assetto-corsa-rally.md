---
title: "Assetto Corsa Rally"
nav_order: 3
lang: "ro"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Export de circuit: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally este construit pe Unreal Engine 5 (5.6.1, o versiune modificată) și își livrează conținutul ca containere IoStore. Niciunul nu este criptat. Exportul găsește etapa și orientarea axelor din tur. Scrie solul propriu al etapei, împărțit în drum și teren și texturat după culoarea de sol coaptă a etapei, iar celelalte modele le plasează în culori uniforme, pe categorii.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Surse: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalarea, etapele, plasarea),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (exportul).
Cititoarele Unreal de sub ele sunt descrise la [Unreal 5 IoStore](reader-unreal-iostore.md),
iar decompresia la [Oodle](reader-oodle.md).

**Stare:** verificat pe jocul instalat, cu tururi generate într-un cadru aleatoriu pe fiecare etapă, și a găsit de fiecare dată etapa și cadrul corecte. Niciun tur înregistrat în chiar joc nu a trecut prin el încă.

## Găsirea instalării {#finding-the-install}

- `--install <folder>`: folderul jocului, sau `Content\Paks` al lui, sau orice folder care conține fișiere `.utoc`. Instrumentul verifică `<folder>`, apoi `<folder>\acr\Content\Paks`, apoi `<folder>\Content\Paks`.
- Altfel, se verifică în același fel `steamapps\common\Assetto Corsa Rally` din fiecare bibliotecă Steam.
- Fiecare `.utoc` din acel folder este deschis ca un singur depozit. Containerele care nu se deschid sunt sărite. Dacă niciunul nu se deschide: "no readable IoStore containers in ...".

Majoritatea blocurilor sunt comprimate cu Oodle, iar o bibliotecă este căutată pe calculator (se caută în fiecare bibliotecă Steam). Vezi [Oodle](reader-oodle.md).

Jocul este considerat AC Rally când fișierul de tur spune `"game": "assetto-corsa-rally"` (sau `acrally`), sau când dați `--game acrally`.

## Ce este o etapă {#what-a-stage-is}

O etapă este o hartă **World Partition**:

- `Content\Levels\<Stage>.umap` plasează terenul îndepărtat.
- Celulele compilate din `Content\Levels\<Stage>\_Generated_\*.umap` plasează tot restul.

Un nivel contează drept etapă dacă folderul lui de mediu, `Content\Environments\<Stage>\`, are un folder `MeshesTrack`. Instrumentul nu se ghidează după numele dalelor, pentru că o etapă le poate numi după un oraș, nu după harta ei. `--level` se potrivește fără a ține cont de majuscule cu aceste nume de hărți. Un nume greșit listează etapele care există.

**Nu există teren de tip landscape.** Solul este format din mesh-uri statice:

| Dale | Cale | Devin |
|---|---|---|
| dale de traseu, circa 175 m, împărțite în două | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` și `..._Terrain_k` | `ground:road` și `ground:terrain` (o dală de traseu nedivizată, precum un lac înghețat, este tot drum) |
| teren îndepărtat, dale de 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Citirea plasărilor {#reading-the-placements}

Ceea ce plasează un mesh este o `StaticMeshComponent`: `StaticMesh`-ul ei și `RelativeLocation`, `RelativeRotation` și `RelativeScale3D`, fiecare relativ la componenta de care este atașată (`AttachParent`), până la rădăcina actorului, care se află în lume.

- Proprietățile sunt **neversionate**: stocate după poziția lor în lista de proprietăți a clasei, nu după nume. Sunt citite cu schemele din [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) (vezi [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- O valoare egală cu șablonul componentei (arhetipul ei dintr-un Blueprint) nu este stocată, deci valorile șablonului se citesc întâi, recursiv, iar valorile proprii ale componentei le suprascriu.
- Componentele cu `bVisible = 0` sau `bHiddenInGame = 1` sunt sărite. La fel și mesh-urile a căror cale se potrivește cu `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` sau `_hlod`.
- Rotațiile folosesc `FRotationMatrix` al Unreal (pitch, yaw, roll, în grade).
- Duplicatele (același mesh la aceeași transformare, până la 0,1 cm) sunt eliminate.
- Componentele care nu pot fi citite sunt numărate pe motive și raportate, de exemplu `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Componentele instanțiate** (păduri, aproape toate) sunt citite doar cu `--trees`. Această versiune a rearanjat acele clase dincolo de anteturile motorului, deci proprietățile lor nu sunt citite. În schimb:

- mesh-ul vine din tabela de dependențe a pachetului, unde fiecare astfel de componentă listează exact un mesh static,
- instanțele vin din blocul nativ de după proprietăți (`[1][1][128][count]`, apoi `count` matrice 4x4 de double),
- componenta se consideră că stă în rădăcina actorului, cum plasează actorii de vegetație.

Coordonatele sunt cele ale Unreal: centimetri, Z în sus, X înainte, Y la dreapta, un cadru stângaci.

## Care etapă și în ce sens {#which-stage-and-which-way-round}

Cadrul de referință al telemetriei nu este documentat, deci nu se presupune nimic: se ajustează.

- **Opt cadre candidate.** Unreal Z (cm) înmulțit cu 0,01 devine înălțimea turului (y). Unreal X și Y devin x și z ale turului, schimbate sau nu, fiecare cu un semn oarecare, toate scalate cu 0,01 la metri.
- **O grilă a înălțimii drumului.** Pentru fiecare etapă, fiecare dală de drum este plasată (la cel mai grosier nivel de detaliu), iar cel mai înalt vertex de drum este păstrat pentru fiecare celulă de 2 m.
- **Punctare.** Până la 400 de eșantioane ale turului, distribuite uniform, sunt duse în spațiul Unreal prin fiecare cadru. Un eșantion este pe drum când, dintre cele 3 x 3 celule din jurul lui, înălțimea drumului cea mai apropiată de el este între 1 m sub și 3 m peste eșantion (`ON_ROAD`). Scorul este proporția eșantioanelor pe drum.
- **Câștigătorul.** Cel mai bun cadru de pe cea mai bună etapă, dacă are cel puțin 50%. Altfel exportul se oprește: "the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level."
- **Un tur care își numește traseul.** Dacă fișierul de tur are un câmp `track`, o etapă al cărei nume se potrivește vag (doar litere și cifre, unul conținând pe celălalt) este încercată prima, singură, și este acceptată doar dacă are cel puțin 80%. Altfel sunt încercate toate etapele.
- Cu `--level`, se încearcă doar acea etapă, în toate cele opt cadre.

Consola afișează, de exemplu,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Apoi totul se scrie **în cadrul turului**: metri, Y în sus. Înfășurarea unui triunghi este inversată oriunde o transformare oglindește, deci fețele privesc tot în direcția corectă.

## Solul {#the-ground}

- Coridorul este `--margin` metri în jurul turului, în planul x/z al acestuia.
- Fiecare dală de sol este plasată la cel mai fin nivel de detaliu, iar doar triunghiurile care ating coridorul sunt păstrate.
- Triunghiurile sunt grupate pe tip (drum sau teren) și pe pătrate de 512 m în spațiul Unreal (51.200 cm), fiecare pătrat cu propria imagine. Piesele se numesc ca `ground:road 1_-4`. UV-urile sunt `(unreal_xy - square_origin) / 51200`.
- Normalele se calculează din triunghiuri pentru tot fișierul.

### Textura solului {#the-ground-texture}

Dacă nu este `--no-textures`, fiecare pătrat este pictat din două surse, la `--texture-size` pixeli:

1. **Culoarea de sol coaptă.** `RuntimeVirtualTextureComponent` al hărții etapei (caseta lui are `RelativeLocation` ca un colț și `RelativeScale3D` ca dimensiune, fără rotație) indică o **textură virtuală** de streaming, culoarea solului pe care jocul a copt-o. Zona pătratului este citită din ea, la nivelul ai cărui pixeli sunt cei mai apropiați de dimensiunea dorită. Asta înseamnă 13 până la 59 cm pe pixel, în funcție de etapă.
2. **Imaginea din satelit** umple ce lasă negru textura virtuală. Este textura `sat*_(b|bc|c|basecolor)` a etapei din folderul ei de mediu, citită la cel mult 4096 px. Plasarea ei se află printr-o potrivire prin cele mai mici pătrate a primului canal UV al terenului îndepărtat față de x și y ai lumii. Potrivirea trebuie să fie liniară până la 0,01 la percentila 95, altfel imaginea nu se folosește. Dacă UV-urile terenului îndepărtat trec de 1 (un material care le repetă), maparea se înjumătățește până se potrivesc o singură dată.

Consola spune ce s-a folosit, de exemplu `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. O etapă fără niciuna dintre ele se desenează în culori uniforme.

## Modele plasate {#placed-models}

Fiecare plasare care nu este o dală de sol este clasată după calea mesh-ului (prima potrivire câștigă):

| Categorie | Numele mesh-ului (sau calea, pentru copaci) conține |
|---|---|
| copaci (doar cu `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| stânci | `rock`, `cliff`, `boulder`, `stone` |
| borduri | `kerb`, `curb` |
| bariere | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| semne | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| clădiri | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastructură | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| recuzită | orice altceva |

- O copie este luată în calcul dacă originea ei se află în coridorul de acces (`margin + 60 m`), și este desenată dacă limitele ei ating coridorul.
- Nivelurile de detaliu urmează [Niveluri de detaliu și buget](detail-budget.md): benzi de distanță, apoi cele mai costisitoare modele coboară un nivel până încap în buget. Acolo unde nici cele mai grosiere niveluri nu încap, cele mai îndepărtate copii sunt lăsate afară, ca în BeamNG, până când se potrivește. Bordurile păstrează detaliul complet și nu sunt lăsate afară niciodată. Sumarul afișează `placed on it (N triangles of a B budget)` și, când au fost lăsate copii afară, `N copies left out to fit the budget, the furthest from the driving first`.
- Fiecare categorie este o singură piesă, într-o culoare uniformă: `ground:kerbs` pentru borduri, care sunt suprafață de rulare, ca în Forza și BeamNG, și `structure:<category>` pentru restul:

| Categorie | Culoare (RGB liniar) |
|---|---|
| bariere | 0.55, 0.52, 0.48 |
| semne | 0.75, 0.72, 0.65 |
| clădiri | 0.62, 0.58, 0.52 |
| infrastructură | 0.48, 0.48, 0.50 |
| stânci | 0.45, 0.43, 0.40 |
| recuzită | 0.55, 0.45, 0.35 |
| copaci | 0.20, 0.32, 0.14 |
| borduri | 0.70, 0.25, 0.22 |

Mesh-urile statice care nu pot fi citite (mesh-uri cu schelet, mesh-uri doar Nanite, niveluri care nu sunt stocate inline) sunt numărate: `N meshes could not be read`.

## Verificări din spatele lor {#checks-behind-it}

După cum spune sursa, pe jocul instalat:

- Fiecare tabel de conținut se citește (versiunea 8).
- Fiecare celulă a fiecărei etape se deschide, iar fiecare componentă de mesh static sau de scenă se decodează terminând exact la coada nativă a clasei ei.
- Aproape orice mesh static eșantionat se decodează (restul sunt cu schelet). Extinderea decodată a unei dale de drum se potrivește cu limitele pe care le stochează.
- Nivelurile de mip ale unei imagini din satelit au exact dimensiunile intrărilor lor în bulk.
- Dalele unui fragment de textură virtuală sunt contabilizate până la octet, iar dalele de drum cad pe drumul pe care îl arată.

## Lacune cunoscute {#known-gaps}

- Proprietățile componentelor instanțiate nu sunt citite (vezi mai sus). Plasarea lor presupune rădăcina actorului.
- Pădurile generate de PCG în timpul rulării nu sunt stocate în fișiere și nu pot fi exportate.
- Mesh-urile spline (zidurile invizibile de respawn), componentele de decalcomanie și propriile texturi ale modelelor plasate nu sunt desenate. Modelele sunt în culori uniforme.
- `--season` nu are efect.
- O actualizare a jocului poate muta sloturile proprietăților. Cititorul ridică o eroare în loc să citească greșit, iar exportul raportează câte componente au eșuat.
