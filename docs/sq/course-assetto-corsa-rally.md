---
title: "Assetto Corsa Rally"
nav_order: 3
lang: "sq"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Eksporti i kursit: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally është ndërtuar mbi Unreal Engine 5 (5.6.1, një ndërtim i modifikuar) dhe
e dërgon përmbajtjen si kontejnerë IoStore. Asnjë nuk është i enkriptuar. Eksporti
gjen etapën dhe orientimin e akseve nga xhiro. Shkruan pllakat e veta të tokës së etapës,
të ndara në rrugë dhe terren dhe të teksturuara nga ngjyra e pjekur e tokës së etapës,
dhe vendos modelet e tjera me ngjyra të sheshta sipas kategorisë.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Burimet: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalimi, etapat, vendosja),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (eksporti).
Lexuesit e Unreal nën to janë te [Unreal 5 IoStore](reader-unreal-iostore.md),
dhe dekompresimi te [Oodle](reader-oodle.md).

**Statusi:** kontrolluar në lojën e instaluar me xhiro të gjeneruara në një kornizë të rastësishme
në çdo etapë, dhe gjeti çdo herë etapën dhe kornizën e duhur. Asnjë xhiro e regjistruar
në vetë lojën nuk ka kaluar ende nëpër të.

## Gjetja e instalimit {#finding-the-install}

- `--install <folder>`: dosja e lojës, ose `Content\Paks` e saj, ose çdo dosje
  që ka skedarë `.utoc`. Mjeti kontrollon `<folder>`, pastaj
  `<folder>\acr\Content\Paks`, pastaj `<folder>\Content\Paks`.
- Përndryshe kontrollohet në të njëjtën mënyrë `steamapps\common\Assetto Corsa Rally`
  i çdo biblioteke Steam.
- Çdo `.utoc` në atë dosje hapet si një depo e vetme. Kontejnerët që nuk hapen
  anashkalohen. Nëse nuk hapet asnjë: "no readable IoStore containers in ...".

Shumica e blloqeve janë të kompresuara me Oodle dhe një bibliotekë kërkohet në kompjuter
(kërkohet në çdo bibliotekë Steam). Shih [Oodle](reader-oodle.md).

Loja merret si AC Rally kur skedari i xhiros thotë `"game": "assetto-corsa-rally"`
(ose `acrally`), ose kur jep `--game acrally`.

## Çfarë është një etapë {#what-a-stage-is}

Një etapë është një hartë **World Partition**:

- `Content\Levels\<Stage>.umap` vendos terrenin e largët.
- Qelizat e gatuara nën `Content\Levels\<Stage>\_Generated_\*.umap` vendosin gjithçka tjetër.

Një nivel llogaritet si etapë nëse dosja e tij e mjedisit,
`Content\Environments\<Stage>\`, ka një dosje `MeshesTrack`. Mjeti nuk shkon
sipas emrave të pllakave, sepse një etapë mund t'i quajë sipas një qyteti në vend të
hartës së saj. `--level` krahasohet pa dallim shkronjash të mëdha e të vogla me këta emra hartash.
Një emër i gabuar liston etapat që ka.

**Nuk ka peizazh (landscape).** Toka janë rrjeta statike:

| Pllakat | Shtegu | Bëhen |
|---|---|---|
| pllakat e pistës, rreth 175 m, të ndara në dysh | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` dhe `..._Terrain_k` | `ground:road` dhe `ground:terrain` (një pllakë pistë e pandarë, si një liqen i ngrirë, është krejt rrugë) |
| terreni i largët, pllaka 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Leximi i vendosjeve {#reading-the-placements}

Ajo që vendos një rrjetë është një `StaticMeshComponent`: `StaticMesh` e tij, dhe
`RelativeLocation`, `RelativeRotation` e `RelativeScale3D`, secila relative me
komponentin ku është ngjitur (`AttachParent`), deri te rrënja e aktorit, që është
në botë.

- Vetitë janë **pa version**: ruhen sipas pozicionit në listën e vetive të klasës,
  jo sipas emrit. Lexohen me skemat në
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (shih [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Një vlerë e barabartë me shabllonin e komponentit (arketipi i tij në një Blueprint) nuk
  ruhet, prandaj vlerat e shabllonit lexohen së pari, në mënyrë rekursive, dhe
  vlerat e vetë komponentit i mbivendosin.
- Komponentët me `bVisible = 0` ose `bHiddenInGame = 1` anashkalohen. Po ashtu rrjetat
  që shtegu i tyre përputhet me `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/`
  ose `_hlod`.
- Rrotullimet përdorin `FRotationMatrix` të Unreal (pitch, yaw, roll në gradë).
- Dublikatat (e njëjta rrjetë në të njëjtën transformim, deri në 0.1 cm) hiqen.
- Komponentët që nuk mund të lexohen numërohen sipas arsyes dhe raportohen, për shembull
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Komponentët me instanca** (pyjet, pothuajse të gjithë) lexohen vetëm me
`--trees`. Ky ndërtim i ka riorganizuar ato klasa përtej titujve të motorit,
prandaj vetitë e tyre nuk lexohen. Në vend të kësaj:

- rrjeta vjen nga tabela e varësive e paketës, ku çdo komponent i tillë
  liston saktësisht një rrjetë statike,
- instancat vijnë nga blloku vendas pas vetive
  (`[1][1][128][count]` pastaj `count` matrica 4x4 double),
- komponenti merret se qëndron te rrënja e aktorit të vet, që është mënyra si i vendosin
  aktorët e gjetheve.

Koordinatat janë ato të Unreal: centimetra, Z lart, X përpara, Y djathtas, një kornizë
e dorës së majtë.

## Cila etapë dhe në cilën anë {#which-stage-and-which-way-round}

Korniza e telemetrisë nuk është e dokumentuar, prandaj nuk supozohet. Ajo përshtatet:

- **Tetë korniza kandidate.** Z i Unreal (cm) shumëzuar me 0.01 bëhet lartësia e xhiros
  (y). X dhe Y i Unreal bëhen x dhe z e xhiros, të këmbyera ose jo, secila me cilindo
  shenjë, të gjitha të shkallëzuara me 0.01 në metra.
- **Një rrjetë lartësish rruge.** Për çdo etapë vendoset çdo pllakë rruge (në
  nivelin e saj më të trashë të detajit) dhe mbahet kulmi më i lartë i rrugës për çdo qelizë 2 m.
- **Vlerësimi.** Deri në 400 mostra të xhiros, të shpërndara njëtrajtësisht, merren në hapësirën Unreal
  nëpër çdo kornizë. Një mostër është në rrugë kur, midis 3 x 3 qelizave rreth saj,
  lartësia e rrugës më e afërt me të është midis 1 m poshtë dhe 3 m mbi mostrën
  (`ON_ROAD`). Vlerësimi është pjesa e mostrave në rrugë.
- **Fituesi.** Korniza më e mirë në etapën më të mirë, nëse ka të paktën 50%.
  Përndryshe eksporti ndalon: "the lap does not lie on any stage's road in any
  frame (best: ...). Name the stage with --level."
- **Një xhiro që emërton pistën e saj.** Nëse skedari i xhiros ka fushën `track`, një etapë
  emri i së cilës përputhet lirshëm me të (vetëm shkronja dhe shifra, njëra përmban
  tjetrën) provohet e para, e vetme, dhe pranohet vetëm nëse ka të paktën 80%.
  Përndryshe provohet çdo etapë.
- Me `--level`, provohet vetëm ajo etapë, në të tetë kornizat.

Konsola thotë, për shembull,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Pastaj gjithçka shkruhet **në kornizën e xhiros**: metra, Y lart. Mbështjellja
e një trekëndëshi përmbyset kudo ku një transformim pasqyron, që faqet të shohin prapë
nga ana e duhur.

## Toka {#the-ground}

- Korridori është `--margin` metra rreth xhiros në planin e vet x/z.
- Çdo pllakë toke vendoset në nivelin e saj më të imët të detajit, dhe mbahen vetëm
  trekëndëshat që arrijnë në korridor.
- Trekëndëshat grupohen sipas llojit (rrugë ose terren) dhe sipas katrorëve 512 m në hapësirën
  Unreal (51,200 cm), secili katror me imazhin e vet. Pjesët emërtohen si
  `ground:road 1_-4`. UV-të janë `(unreal_xy - square_origin) / 51200`.
- Normalet llogariten nga trekëndëshat për të gjithë skedarin.

### Teksturat e tokës {#the-ground-texture}

Nëse nuk ka `--no-textures`, çdo katror lyhet nga dy burime, me `--texture-size` pikselë:

1. **Ngjyra e pjekur e tokës.** `RuntimeVirtualTextureComponent` i hartës së etapës
   (kutia e tij është `RelativeLocation` si cep dhe `RelativeScale3D` si madhësi,
   pa rrotullim) tregon një **teksturë virtuale** me transmetim, ngjyrën e tokës
   që e piu loja. Zona e katrorit lexohet prej saj, në nivelin pikselat e të cilit
   janë më afër madhësisë së dëshiruar. Kjo është 13 deri 59 cm për piksel, sipas
   etapës.
2. **Imazhi satelitor** mbush çfarëdo që teksturë virtuale e lë të zezë. Është
   teksturë `sat*_(b|bc|c|basecolor)` e etapës në dosjen e saj të mjedisit, e lexuar
   deri në 4096 px. Vendosja e saj gjendet me përshtatje të katrorëve më të vegjël të
   kanalit të parë UV të terrenit të largët kundrejt x dhe y të botës.
   Përshtatja duhet të jetë lineare brenda 0.01 në përqindjen e 95-të, përndryshe imazhi nuk përdoret.
   Nëse UV-të e terrenit të largët kalojnë 1 (një material që i përsërit), harta
   përgjysmohet derisa të futen një herë.

Konsola thotë cilën përdori, për shembull
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Një etapë pa asnjërën vizatohet me ngjyra të sheshta.

## Modelet e vendosura {#placed-models}

Çdo vendosje që nuk është pllakë toke klasifikohet sipas shtegut të rrjetës (fiton
përputhja e parë):

| Kategoria | Emri i rrjetës (ose shtegu, për pemët) përmban |
|---|---|
| pemë (vetëm me `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| shkëmbinj | `rock`, `cliff`, `boulder`, `stone` |
| bordura | `kerb`, `curb` |
| barriera | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| tabela | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| ndërtesa | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastrukturë | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| objekte (props) | çdo gjë tjetër |

- Një kopje merret parasysh nëse origjina e saj është në korridorin e arritjes
  (`margin + 60 m`) dhe vizatohet nëse kufijtë e saj prekin korridorin.
- Nivelet e detajit ndjekin [Nivelet e detajit dhe buxheti](detail-budget.md):
  breza largësie, pastaj modelet më të kushtueshme zbresin për t'u futur në buxhet. Kur
  edhe nivelet më të trasha e tejkalojnë, kopjet më të largëta lihen jashtë, si në
  BeamNG, derisa të futet. Bordurat mbajnë detajin e plotë dhe nuk lihen kurrë jashtë. Përmbledhja
  printon `placed on it (N triangles of a B budget)` dhe, kur u larguan kopje,
  `N copies left out to fit the budget, the furthest from the driving first`.
- Çdo kategori është një pjesë me ngjyrë të sheshtë: `ground:kerbs` për bordurat,
  që janë sipërfaqe vozitjeje, si në Forza dhe BeamNG, dhe `structure:<category>` për
  të tjerat:

| Kategoria | Ngjyra (RGB lineare) |
|---|---|
| barriera | 0.55, 0.52, 0.48 |
| tabela | 0.75, 0.72, 0.65 |
| ndërtesa | 0.62, 0.58, 0.52 |
| infrastrukturë | 0.48, 0.48, 0.50 |
| shkëmbinj | 0.45, 0.43, 0.40 |
| objekte (props) | 0.55, 0.45, 0.35 |
| pemë | 0.20, 0.32, 0.14 |
| bordura | 0.70, 0.25, 0.22 |

Rrjetat statike që nuk mund të lexohen (rrjetat me skelet, rrjetat vetëm Nanite, nivelet
që nuk ruhen brenda) numërohen: `N meshes could not be read`.

## Kontrollet pas tij {#checks-behind-it}

Siç thuhet në burim, në lojën e instaluar:

- Çdo tabelë përmbajtjeje lexohet (versioni 8).
- Çdo qelizë e çdo etape hapet, dhe çdo rrjetë statike dhe komponent skene dekodohet duke u mbyllur saktësisht në bishtin vendas të klasës së vet.
- Pothuajse çdo rrjetë statike e mostruar dekodohet (të tjerat janë me skelet). Shtrirja e dekoduar e një pllake rruge përputhet me kufijtë e saj të ruajtur.
- Nivelet mip të një imazhi satelitor janë saktësisht madhësitë e hyrjeve të tyre bulk.
- Pllakat e një copë teksture virtuale llogariten deri në bajt, dhe pllakat e rrugës bien mbi rrugën që ajo tregon.

## Boshllëqe të njohura {#known-gaps}

- Vetitë e vetë komponentëve me instanca nuk lexohen (shih më sipër). Vendosja e tyre supozon rrënjën e aktorit.
- Pyjet e gjeneruara nga PCG gjatë ekzekutimit nuk ruhen në skedarë dhe nuk mund të eksportohen.
- Rrjetat spline (muret e padukshme të rilindjes), komponentët decal dhe teksturat e vetë modeleve të vendosura nuk vizatohen. Modelet janë me ngjyra të sheshta.
- `--season` nuk ka efekt.
- Një përditësim i lojës mund t'i lëvizë vendet e vetive. Lexuesi ngre gabim në vend që të lexojë keq, dhe kursi raporton sa komponentë dështuan.
