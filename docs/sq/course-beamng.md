---
title: "BeamNG.drive"
nav_order: 2
lang: "sq"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Eksporti i kursit: BeamNG.drive {#course-export-beamngdrive}

Eksporti për BeamNG e lexon një nivel ashtu siç e montion loja, pastaj shkruan të njëjtin
lloj skedari që shkruan eksporti i Forza: toka për çdo katror 512 m me një
teksturë të pjekur, rruga dhe toka e lirshme si pjesë më vete, modelet e vendosura sipas kategorisë, dhe
uji.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Burimet: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalimi, sistemi i skedarëve, skena, terreni, materialet),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (eksporti),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) dhe
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (format e rrjetave).
Formatet e skedarëve në hollësi: [Skedarët e BeamNG](reader-beamng.md).

## Kuadri i xhiros {#the-laps-frame}

Eksporti `course` pret pozicionet e BeamNG në **kuadrin e shikuesit**:
`(x, z, -y)` e botës së BeamNG me Z lart, në metra. Kjo është rrotullimi që aplikon
regjistruesi i telemetrisë 3DHeat. Eksporti e kthen xhiron në kuadrin e BeamNG
(`(x, -z, y)`), punon aty, dhe i shkruan të gjitha përsëri në kuadrin e shikuesit.
Ky është një rrotullim, jo një pasqyrim, ndaj asgjë nuk del e pasqyruar. Një xhiro
e regjistruar në kuadrin e papërpunuar të BeamNG nuk do të vendosej. Kjo nuk është testuar me
regjistrues të tjerë.

Loja merret si BeamNG kur skedari `heat3d-lap` thotë `"game": "beamng"`,
ose kur jep `--game beamng`.

## Gjetja e instalimit {#finding-the-install}

- `--install <folder>`: dosja që mban `gameengine.zip` dhe `content`.
- Përndryshe kontrollohet `steamapps\common\BeamNG.drive` i çdo biblioteke Steam
  për ato të dyja.
- Nëse nuk funksionon asnjëra: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Sistemi i skedarëve {#the-file-system}

BeamNG jep arkiva zip të thjeshta dhe i montion në një sistem skedarësh ku
referohen nivelet (`/art/shapes/...`, `/assets/materials/...`). Eksporti ndërton
të njëjtën gjë: një indeks pa dallim shkronjash mbi

1. `gameengine.zip`,
2. çdo `*.zip` nën `content`, përveç `content\vehicles\*` dhe arkivave emrat e të cilave
   fillojnë me `art_sound` ose `audio`,
3. përmbajtjen e përdoruesit, me strukturën më të re së pari: nën
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` dhe `%LOCALAPPDATA%\BeamNG.drive`, dosja
   `current` dhe dosja e versionit me numrin më të lartë. Nga secila:
   `mods\*.zip`, çdo dosje në `mods\unpacked`, dhe vetë dosja e përdoruesit nëse
   ka një dosje `levels`.

Shtesat e mëvonshme fitojnë, si në lojë, ndaj një mod zëvendëson ç'e mbishkruan. Modet
përfshihen gjithmonë në një eksport kursi.

Shtigjet që emërton një nivel zgjidhen ashtu siç i zgjidh loja: siç janë dhënë, pastaj
në lidhje me skedarin që i emërtoi, dhe për secilin edhe si `.dds` në të cilin u gatua
një teksturë, `.cdae` në të cilin u përpilua një `.dae`, ose përmes një skedari `.link`
që tregon te `/assets`.

## Cili nivel {#which-level}

Pa `--level`, çdo nivel vlerësohet sipas sa nga xhiroja shtrihet mbi të:

- Përdoren deri në 500 mostra xhiroje, të shpërndara njëlloj.
- Për `TerrainBlock` të çdo niveli, shtrirja e terrenit lexohet nga pesë
  bajtet e para të skedarit të tij `.ter`, ndaj një nivel afër të cilit xhiroja nuk kalon fare nuk kushton asgjë.
  Nëse të paktën 30% e mostrave janë brenda shtrirjes, lexohen lartësitë. Një
  mostër llogaritet **mbi** terrenin kur është mes 1 m poshtë dhe 3 m mbi
  të (`ON_GROUND`), sepse pika e referencës e një makine është trupi i saj, jo gomat.
- Nëse asnjë nivel nuk merr 50% ose më shumë, nivelet vlerësohen edhe sipas **rrugëve** të tyre. Disa
  nivele vazhdojnë përtej hartës së lartësisë (skajet e tyre vazhdojnë si fletë shkëmbi). Një mostër është mbi një rrugë kur qëndron brenda gjysmë-gjerësisë së rrugës plus
  4 m (të paktën 6 m) nga një segment `DecalRoad`, dhe mes 2 m poshtë dhe 4 m mbi
  të.
- Niveli më i mirë fiton nëse merr të paktën 30%. Përndryshe eksporti ndalet dhe
  liston tre më të mirët: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

Konsola thotë `on <level>: 87% of the lap lies on its terrain` (ose `roads`).
`--level` krahasohet pa dallim shkronjash me emrat e dosjeve të niveleve.

## Leximi i nivelit {#reading-the-level}

Nga çfarë përbëhet një nivel, secila pjesë e kontrolluar kundrejt niveleve të dhëna
(hollësitë te [Skedarët e BeamNG](reader-beamng.md)):

- **Skena**: `levels\<name>\main\**\*.level.json` (një objekt JSON për rresht, ose një
  varg JSON), ose një skedar `.mis` për nivele më të vjetra. Mjeti lexon objektet `TSStatic`
  (modele të vendosura, duke kaluar ato të fshehura), objektet `Prefab` (të foleuara deri 8
  thellë, `.prefab` TorqueScript ose `.prefab.json`), objektet `DecalRoad` (rrugë
  të lyera), `TerrainBlock`, `WaterPlane`, `WaterBlock` dhe `River`.
- **Objektet e pyllit**: `levels\<name>\forest\*.forest4.json`, të tipizuara përmes
  regjistrimeve `managedItemData.json`. Barrierat, gardhet dhe shkëmbinjtë janë objekte pylli po aq
  shpesh sa pemët.
- **Terreni**: heightfield-i `.ter` dhe harta e shtresave të tij.
- **Materialet**: çdo `*.materials.json` jashtë `levels\`, plus ato të këtij
  niveli.

## Korridori dhe decal-et e rrugës {#the-corridor-and-the-road-decals}

Korridori është `--margin` metra rreth xhiros në planin x/y të BeamNG (shih
[Eksporti i kursit](course-export.md#the-corridor)). Një korridor arritjeje prej
`margin + 60 m` përzgjedh kandidatët.

**Decal-et e rrugës** (`DecalRoad`) janë aty ku është pjesa më e madhe e rrugëve të BeamNG: të lyera
mbi terren, jo të modeluara. Decal-et shtrirja e të cilëve prek korridorin e arritjes
merren sipas radhës së vizatimit të lojës (`renderPriority` zbritës, pastaj radha e skedarit),
dhe shtrohen si shirita:

- Nyjet (x, y, z, gjerësia) interpolohen nga një spline **centripetal Catmull-Rom**
  rreth çdo 1 m. Lloji uniform bën lak mbi vete aty ku nyjet grumbullohen
  në një kthesë të mprehtë. Rrugët me lak mbyllen.
- Çdo skaj merr lartësinë e terrenit aty ku terreni është brenda 1.5 m nga
  lartësia e vetë rrugës, dhe mban lartësinë e rrugës gjetkë (në një urë).
- Emri i materialit vendos çfarë lyen një decal:

| Lloji | Emri i materialit përputhet (fiton i pari) |
|---|---|
| shenja gomash | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| mbivendosje (kozmetike) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| shenja rruge | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| e lirshme | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| rrugë | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| mbivendosje | çdo gjë tjetër |

## Toka {#the-ground}

Heightfield-i i terrenit brenda korridorit bëhet trekëndësha:

- Një katërkëndësh për çdo katror terreni qendra e të cilit është në korridor. Katrorët me shtresë
  255 (vrima) kalohen. Çdo katërkëndësh është dy trekëndësha, me diagonalen që
  alternon ashtu siç bën terreni i Torque.
- Lartësitë janë `position.z + h * maxHeight / 65535`. Normalet vijnë nga
  diferencat e lartësive.
- Çdo katror klasifikohet sipas **shtresës** së tij: emri i shtresës me modelin e tokës
  dhe shënimin e materialit të terrenit. Fjalët e shtruara e bëjnë `road`,
  `grass/forest/rock/moss/leaves/cliff/stone` e bëjnë `terrain`, dhe fjalët e lirshme
  e bëjnë `loose` (zhavorr dhe dhe). Çdo gjë tjetër është `terrain`.
- Pastaj **decal-et e rrugës dhe të tokës së lirshme mbishkruajnë** katrorët që mbulojnë, sipas
  radhës së vizatimit, ndaj decal-i i fundit i lyer vendos.
- Kulmet ndahen për çdo katror 512 m (`floor(x / 512)`, `floor(y / 512)`), kështu
  çdo pjesë hartëzohet në saktësisht një imazh: `u = (x - x0) / 512`,
  `v = 1 - (y - y0) / 512`.

Konsola printon `what the ground is made of` me numrat e trekëndëshave sipas llojit.

### Sipërfaqja e drejtimit e modeluar {#modelled-driving-surface}

Qarqet e BeamNG janë modele po aq shpesh sa janë terren. Pista e një qarku mund
të jetë një rrjetë me vijat, gomat dhe shiritat e dridhjes si rrjeta më vete sipër saj. Ndaj modelet e vendosura në kategoritë rrugë, bordura, buzë, objekte dhe ura
kërkohen për sipërfaqe drejtimi. Sipas materialit:

| Sipërfaqja | Vendoset nga (fiton i pari) |
|---|---|
| shenja gomash | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` në emër, llojin e tokës ose shënim |
| shenja rruge | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` në emrin e materialit |
| bordura | `rumble`, `kerb`, `curb` |
| rrugë | lloji i tokës `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ose emri përmban `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| e lirshme | lloji i tokës `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| buzë | `sidewalk` |
| (kategoria e vetë modelit) | për modelet e klasifikuara tashmë rrugë, bordura ose buzë |

Nga ata materiale, trekëndëshat **që shohin lart** (normalja z mbi 0.5) brenda
korridorit nxirren nga modeli dhe bëhen tokë. Lyhen në teksturën e pjekur të pllakës
dhe shkruhen si pjesë të tilla si
`ground:road 3_-2 asphalt_light`. Shenjat e rrugës dhe të gomave vetëm lyhen. Trekëndëshat e mbetur
të modelit mbeten me modelin. Këto modele nuk thjeshtohen kurrë
dhe nuk lihen jashtë nga buxheti, sepse një pistë e ashpër është një pistë e gabuar.

## Teksturat e pjekura të tokës {#the-baked-ground-texture}

Çdo katror 512 m që ka tokë merr një imazh me `--texture-size` pikselë
(2048 = 25 cm për piksel), të vizatuar ashtu siç e vizaton loja tokën e saj:

1. **Shtresat e terrenit.** Për piksel, shtresat e katër katrorëve përreth të terrenit përzihen
   në mënyrë bilineare. Çdo shtresë ngjyroset ashtu siç e ngjyros loja: **harta bazë**
   e materialit e shtrirë mbi `diffuseSize` metra (ose gjithë
   terrenin), pastaj hartat **detail** dhe **macro** si mbivendosje gri
   (`colour * (1 + strength * (2 * overlay - 1))`, 0.5 neutrale). Parazgjedhjet e tyre
   përsëriten çdo 2 m dhe 60 m, me forca 0.5 dhe 0.3, përveç nëse materiali thotë
   ndryshe. Një shtresë pa material merr ngjyrën e sheshtë të sipërfaqes së saj. Rreshti 0
   i hartës bazë është veriu.
2. **Decal-et e rrugës** që lyhen vetëm mbi terren, sipas radhës së vizatimit, secili
   me teksturën e vet, hartën e opacitetit, tonin dhe opacitetin, përgjatë shiritit.
   Nivelet e dhëna përdorin prioritete rreth 12-16 për bazat e asfaltit, 10 për shenjat
   dhe 4 për gomën.
3. **Sipërfaqja e drejtimit e modeluar** e parë nga lart: bazat së pari, pastaj mbivendosjet, secila
   në teksturën përsëritëse të vetë modelit me një teksel për piksel të pjekjes.
4. **Decal-et që projektohen edhe mbi objekte** (`overObjects`), të fundit.

Me `--no-textures`, nuk piqet asgjë: pjesët e tokës marrin ngjyra të sheshta, dhe
shenjat e modeluara të rrugës dhe të gomave bëhen pjesë më vete, të ngritura **3 cm**.

## Modelet e vendosura {#placed-models}

Kandidatët janë çdo `TSStatic`, fëmijë prefab dhe objekt pylli origjina e të cilit qëndron në
korridorin e arritjes. Një kandidat vizatohet nëse kutia kufizuese botërore e formës së tij prek
korridorin.

**Kategoria** vjen nga shënimi i vetë nivelit dhe shtegu i formës. Rregulli i
parë që përputhet fiton:

| Kategoria | Shënimi | Shtegu ose emri përmban |
|---|---|---|
| sfond (nuk vizatohet kurrë) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| bordura | | `kerb`, `curb`, `rumble` |
| rrugë | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| buzë | `SIDEWALK`, `COBBLESTONE` | |
| pemë (vetëm me `--trees`) | `NATURE` | tree, foliage, bush, grass, plant dhe fjalë të ngjashme |
| shkëmbinj | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| barriera | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| tabela | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| ura | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastrukturë | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| ndërtesa | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| objekte | | çdo gjë tjetër |

**Format** lexohen nga `.cdae` i përpiluar, ose nga `.dae` Collada aty ku nuk ka
cache (modet). Një formë që nuk lexohet numërohet:
`N copies of M models could not be read`. Materialet e emërtuar ose të teksturuar
`invisible`, `collision` ose `nodraw` nuk vizatohen kurrë.

**Teksturat.** Modelet grupohen sipas kategorisë dhe materialit në pjesë me emër
`structure:<category> <material>` (ose `ground:kerbs <material>`). Një grup merr
teksturën e ngjyrës së materialit të tij deri në **256 px** vetëm nëse UV-të e tij qëndrojnë brenda 0-1
(98% e kulmeve brenda -0.02 deri 1.02). Shikuesi i paketon teksturat në një atlas
dhe nuk mund të përsërisë asnjë. Një grup tekstura e të cilit përsëritet vizatohet në
ngjyrën mesatare të teksturës (e peshuar me alfa, në sRGB, shumëzuar me tonin e materialit),
ose në ngjyrën e kategorisë nëse nuk ka teksturë.

**Detaji** ndjek skemën e përbashkët te
[Nivelet e detajit dhe buxheti](detail-budget.md). Nivelet e detajit të BeamNG janë
`details` e formës (madhësia më e madhe në piksel së pari). Mbi buxhet, kopjet
më të largëta largohen të parat. Bordurat dhe modelet që mbajnë sipërfaqe drejtimi nuk thjeshtohen
dhe nuk lihen jashtë kurrë.

`--no-placed` heq strukturat por mban prapë sipërfaqen e drejtimit të modeluar.
`--trees` shton kategorinë e pemëve.

## Uji {#water}

| Burimi | Vizatohet si |
|---|---|
| `WaterPlane` (deti) | një katërkëndësh 4 m në lartësinë e ujit për çdo qelizë korridori ku asnjë terren nuk arrin atë lartësi |
| `WaterBlock` | një katërkëndësh, katrori njësi në z lokale = 0 në transformimin e bllokut (ndaj shkalla e tij vendos madhësinë), nëse prek korridorin; nëse z = 0 është sipërfaqja e bllokut nuk është verifikuar |
| `River` | një shirit nëpër nyjet e tij nëse prek korridorin |

I gjithë uji është një pjesë e sheshtë, `water:water`.

## Çfarë nuk vizatohet {#not-drawn}

- Mbulesa e tokës (bar procedural).
- Dekori i vendosur rreth skajit të botës (`backdrop` dhe të ngjashme).
- Teksturat përsëritëse të modeleve, që dalin si ngjyrë mesatare (shih më sipër).
- Rrjetat me skelet (automjete, personazhe) dhe rrjetat e decal-eve brenda formave.

## Kontrollet pas tij {#checks-behind-it}

Siç thuhet në burim, të matura mbi nivelet e dhëna:

- Nyjet e rrugës qëndrojnë mbi terren deri në 1-2 cm (mediana) në nivelet e kontrolluara, me `h * maxHeight / 65535` dhe rreshta përgjatë +y. `h / 32` ose radha tjetër e boshteve gabon me dhjetëra deri qindra metra.
- Seksionet e shinave të zinxhiruara përgjatë një rruge shkojnë përgjatë rreshtit 0 të `rotationMatrix` (shumica dërrmuese).
- Rrotullimi i nyjes `.cdae` duhet transpozuar. Me këtë, kufijtë botërorë përputhen me `.dae` burimore deri në milimetër. Mënyra e librit shkollor gabon me 38 cm (mediana).
- Eksportuar në disa nivele të dhëna të çdo lloji, në sekonda deri minuta secili.
