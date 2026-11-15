---
title: "Komandat"
nav_order: 2
lang: "sq"
source: commands.md
source_hash: "db876ce4e110"
nav_exclude: true
search_exclude: true
---
# Komandat {#commands}

Çdo komandë niset si `python -m heat3d_gamefiles <verb> ...` nga dosja e
repozitorit. Foljet vijnë sipas radhës që të duhen zakonisht: çfarë është ky skedar,
çfarë ka brenda, më jep atë, dhe ktheje një xhiro në një kurs.

| Folja | Merr | Bën |
|---|---|---|
| [`identify`](#identify) | çdo skedar | emërton formatin e kontejnerit duke lexuar bajtet e tij |
| [`list`](#list) | një `.pak` ose IoStore `.utoc` të Unreal, një `.vpk` të Source 2, një `.minizip` të ForzaTech, ose një zip | liston hyrjet e tij |
| [`extract`](#extract) | të njëjtat | shkruan një hyrje në disk |
| [`meshes`](#meshes) | një `SerializedFile` të Unity | liston dhe kontrollon rrjetat e tij (meshes) |
| [`course`](#course) | një xhiro | eksporton kursin rreth saj (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | një bibliotekë xhirosh të regjistruara | ekzekuton `course` për çdo kurs në të (Forza) |
| [`races`](#races) | një Forza të instaluar | liston çdo garë që e përcakton loja: çfarë shton, çfarë fsheh, vendet, gjendjen e eksportit të saj |
| [`terrain`](#terrain) | një dosje pisti të Forza | pret një rajon sipas koordinatave të botës |
| [`levels`](#levels-and-level-frostbite) | një lojë Frostbite të instaluar (Battlefield 6) | liston nivelet e saj |
| [`level`](#levels-and-level-frostbite) | emrin e një niveli | eksporton nivelin: terrenin, rrjetat e vendosura, opsionalisht hartat e tyre të ngjyrave (Battlefield 6) |
| [`cars`](#cars) | një Forza të instaluar | çdo makinë me detaje të ulëta, në një skedar për skedën e garës të shikuesit |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | një lojë Unreal 5 | liston hartat e saj World Partition |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | emrin e një harte | eksporton hartën: peizazhin, strukturat HLOD, ujin |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | një Arma Reforger të instaluar | liston botët e saj |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | emrin e një bote | eksporton botën: terrenin në ngjyrat e tij, detin, ndërtesat si kuti |

**Si t'i lexosh shembujt:** `<x>` do të thotë ta zëvendësosh me vlerën tënde, pa
kllapat këndore; `[...]` është opsionale; një shteg me hapësira vëre në "thonjëza të dyfishta",
për shembull `"C:\Games\My Game"`. Je i ri? Shih [Para se të fillosh](before-you-start.md).
`--help` i plotë i çdo foljeje është te [Referenca e komandave](../cli-reference.md).

Çdo herë që programi niset, mund të kontrollojë së pari për një version më të ri. Shih
[Përditësimet](updates.md). `HEAT3D_NO_UPDATE=1` e çaktivizon këtë kontroll.

Burimi: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Faqe hap pas hapi: [Inspektimi i arkivave](inspecting-archives.md), [Eksporti i kursit](course-export.md),
[Nivele të plota](whole-levels.md), [Makinat e Forza](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Kodet e daljes {#exit-codes}

| Kodi | Kuptimi |
|---|---|
| 0 | sukses |
| 1 | puna dështoi (xhiro e palexueshme, asnjë lojë e gjetur, asgjë për të eksportuar, një kurs në `courses` dështoi; për `list` dhe `extract`, një skedar që nuk është asnjë nga arkivat që lexojnë, një që nuk hapet ose nuk lexohet - një pak i enkriptuar pa `--key`, një kontejner IoStore i enkriptuar - ose një hyrje që nuk është në arkiv) |
| 2 | argumente të gabuara (argparse), një shteg që nuk ekziston, një `--key` që nuk është 64 shifra hex, ose `terrain` që merr të dyja ose asnjërën nga `--box` dhe `--route` |

Dështimet e `list` dhe `extract` janë nga një rresht në daljen standarde të gabimeve, jo një
gjurmë (traceback) e Python.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Kjo lexon skedarin dhe thotë se cili kontejner është. Nuk shkon sipas
shtesës (përjashtimi i vetëm është një `.ucas`, më poshtë). I provon formatet sipas kësaj
radhe dhe ndalet te i pari që e lexon:

1. **Unreal `.pak`**: një fund (footer) me magjinë e pak në 1,024 bajtet e fundit. Printon
   versionin, ku fillon indeksi dhe madhësinë e tij, nëse indeksi është i enkriptuar, dhe
   metodat e kompresimit.
2. **Unreal IoStore `.utoc`**: magjia e IoStore në fillim. Printon versionin,
   numrin e copave (chunks) dhe nëse kontejneri është i enkriptuar; për një që nuk është,
   numrin e skedarëve që emërton drejtoria e tij (dhe nën cilën pikë montimi), metodat
   e kompresimit, dhe nëse `.ucas` i tij është pranë tij. Një `.ucas` nuk ka
   krye të vetin, ndaj njihet nga `.utoc` me të njëjtin emër pranë tij,
   dhe `identify` e emërton atë skedar.
3. **ForzaTech `.minizip`**: magjia `PGZP`. Printon versionin, numrin e hyrjeve dhe
   segmenteve, dhe nëse `ChunkContentsMiniZip<n>.txt` që i emërton
   hyrjet është pranë tij (dhe, nëse po, nëse emërton aq sa ka).
4. **zip**: një krye lokal skedari zip në fillim. Printon numrin e hyrjeve, gjashtë
   shtesat më të shpeshta, dhe emrat e niveleve kur hyrjet qëndrojnë nën
   `levels/<name>/`, si në një arkiv niveli të BeamNG.drive.
5. **Unity**: një paketë `UnityFS` (printon versionin e motorit dhe numrin e hyrjeve) ose një
   `SerializedFile` i zhveshur (printon formatin, versionin e motorit, numrin e objekteve dhe
   gjashtë klasat më të shpeshta).
6. **Frostbite `.toc`**: printon llojin (`plain` ose `signed`), ku fillon pema,
   dhe ose numrin e asetëve (tabela binare e seksioneve) ose numrin e superpaketave
   (pema DbObject).
7. **Source 2 `.vpk`**: printon versionin, numrin e hyrjeve, dhe rrjetën e parë
   të navigimit `.nav` nëse arkivi ka një.
8. **BeamNG `.cdae`**: version forme 31 që lexohet. Printon numrin e rrjetave (meshes),
   numrin e niveleve të vizatuara të detajit dhe materialet e para.
9. **BeamNG `.ter`**: nuk ka magji, ndaj gjithçka duhet të përputhet - një anë nga 2
   deri në 16,384, aq lartësi në katror dhe bajte shtresash, pastaj 1 deri 255 emra
   shtresash të printueshëm. Printon versionin, madhësinë dhe emrat e shtresave.
10. **ForzaTech `.modelbin`**: printon versionin, numrin e copave dhe gjashtë
    etiketat më të shpeshta të copave. Përmbajtja e copave nuk dekodohet këtu.

Formatet me magji të vetën (2 deri 4) vijnë para Unity dhe Frostbite,
kontrollet e të cilave lexojnë të gjithë skedarin: një arkiv i Forza është dhjetëra gigabajte.

Nëse asnjëri nuk përputhet, printon `not a format this tool reads` dhe arsyen e fundit.
Ajo arsye vjen nga kontrolli i ForzaTech.

Shembull (sintetik):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<archive>` | i detyrueshëm | një `.pak` i Unreal; një IoStore `.utoc` (ose `.ucas` pranë tij); një `.vpk` i Source 2 (për VPK të ndara, `_dir.vpk`); një `.minizip` i ForzaTech; një zip, si arkivat e niveleve dhe përmbajtjes të BeamNG |
| `--filter TEXT` | asnjë | vetëm shtigjet që përmbajnë TEXT, pa dallim shkronjash të mëdha e të vogla |
| `--limit N` | 50 | printo më së shumti N hyrje (numri total printohet gjithmonë) |
| `--key HEX` | asnjë | një çelës AES-256 që e ke tashmë, 64 shifra hex, me ose pa `0x`. Vetëm një `.pak` i enkriptuar e përdor. Çdo gjë që nuk është 64 shifra hex refuzohet para se të hapet arkivi (kodi i daljes 2) |

Mjeti e vendos formatin nga bajtet: një tabelë përmbajtjeje IoStore, një
`.minizip` dhe një VPK nga nënshkrimi me të cilin fillojnë, një zip nga kryet e tij lokal
të skedarit, dhe një `.pak` nga fundi (footer) në fund të tij. Një `.ucas` nuk ka krye dhe
hapet përmes `.utoc` me të njëjtin emër. Një skedar që nuk është asnjë nga këto
refuzohet me `<file> is not an archive list and extract read (...)`. Një që është
por nuk hapet refuzohet me arsyen e lexuesit: një pak i enkriptuar pa
`--key`, një kontejner IoStore i enkriptuar, një version pak që nuk e lexon. Në të dyja
rastet është një rresht dhe kodi i daljes 1.

Çdo rresht tregon madhësinë e pakompresuar, metodën e kompresimit dhe shtegun:

| Arkivi | Metoda | Shtigjet |
|---|---|---|
| `.pak` | `none`, ose emri nga fundi (`Zlib`, `Oodle`, `Gzip`...) | me pikën e montimit të arkivit, për shembull `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, ose metoda e kontejnerit (`Oodle`, `Zlib`...), siç ruhet blloku i tij i parë | me pikën e montimit, për shembull `../../../<Project>/Content/...`. Një kontejner pa indeks drejtorie nuk emërton asnjë skedar dhe refuzohet |
| `.vpk` | gjithmonë `stored` | si në drejtori |
| `.minizip` | `lz4`, `deflate` ose `stored` | siç i shkruan `ChunkContentsMiniZip<n>.txt` pranë `GeoChunk<n>.minizip`, me parashtesën e makinës së ndërtimit të hequr (backslash, siç i shkruan loja). Arkivi nuk ruan emra, ndaj pa atë skedar hyrjet janë `#0`, `#1`... Një listë me numër rreshtash të ndryshëm nga hyrjet refuzohet: të dyja nuk i përkasin njëra-tjetrës |
| zip | `stored`, `deflate`, ... | siç është ruajtur; dosjet nuk listohen |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<archive>` | i detyrueshëm | si për `list` |
| `<entry>` | i detyrueshëm | shtegu saktësisht siç e printon `list` (me dallim shkronjash); në një `.minizip`, funksionon edhe `#<number>` |
| `--out FILE` | emri i skedarit të hyrjes (pas `/` ose `\` të fundit), në dosjen aktuale | ku të shkruhet; dosjet prind krijohen |
| `--key HEX` | asnjë | si për `list` |

Hyrja dekriptohet (pak, me çelës), dekompresohet dhe shkruhet. Printon
`<bytes> bytes -> <file>`. Nëse shtegu nuk është në arkiv, komanda del
me kodin 1. Kështu bën edhe një hyrje që nuk lexohet (një hyrje e enkriptuar pa
çelës, e kompresuar me Oodle pa bibliotekë Oodle), me arsyen në një rresht. Një hyrje VPK nuk kontrollohet kundrejt CRC-së së saj këtu. Lexuesi ka një
metodë `verify()` për këtë (shih [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<path>` | i detyrueshëm | një `SerializedFile` i zhveshur i Unity (`sharedassets0.assets`, `level0`...), jo një paketë |
| `--limit N` | 25 | dekodo dhe printo më së shumti N rrjeta |

Kjo printon numrin e objekteve `Mesh`, pastaj një rresht për rrjetë: emrin (40 shkronjat
e para), numrin e kulmeve dhe të trekëndëshave, dhe `ok` ose `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` do të thotë se kulmet e dekoduara nuk e riprodhojnë kutinë kufizuese
që Unity ruajti për rrjetën, brenda 2% të madhësisë së kutisë. Ky është kontrolli i vetë
leximit (shih [Unity](reader-unity.md)). Një rrjetë që nuk lexohet raportohet me
arsyen dhe numërohet në kufi. Të dhënat e kulmeve në një skedar `.resS` lexohen
nga dosja ku është kontejneri.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Kjo eksporton kursin rreth një xhiroje: tokën në një brez nga të dyja anët e
drejtimit, dhe çfarë qëndron mbi të, si një `.glb`. Pjesën tjetër e zbulon vetë: cila
lojë, cila kopje e instaluar, cila pistë, nivel ose etapë, dhe (për Assetto Corsa
Rally) në cilën anë janë boshtet. Shih [Eksporti i kursit](course-export.md).

`<lap>` mund të jetë çdo nga këto (hollësitë te [Të dhënat e xhiros](lap-inputs.md)):

- një skedar xhiroje: JSON rruge, JSON xhiroje e FH Companion, JSON `heat3d-lap`, `.npz`, ose `.csv` me kolona x, y, z
- një dosje skedarësh xhiroje, e kërkuar rekursivisht (një kurs i plotë i regjistruar)
- një **emër** kursi, i kërkuar në bibliotekën e FH Companion te `%LOCALAPPDATA%\FHCompanion\laps`

### Opsionet {#options}

| Opsioni | Parazgjedhja | Lojërat | Kuptimi |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` në dosjen aktuale, ose në `$HEAT3D_LEVELS/<game>/courses/` kur ajo është vendosur | të gjitha | ku të shkruhet; emri bëhet me shkronja të vogla, me vargje shkronjash të tjera të kthyera në `_` |
| `--game {forza,beamng,acrally}` | ç'thotë skedari i xhiros, ndryshe `forza` | të gjitha | nga cila lojë është xhiroja |
| `--margin M` | 80 | të gjitha | metra tokë të mbajtur nga të dyja anët e drejtimit |
| `--texture-size {2048,1024,512}` | 2048 | të gjitha | piksele teksture toke për pllakë 512 m (2048 = 25 cm për piksel) |
| `--no-textures` | joaktiv | të gjitha | vetëm ngjyra të sheshta: një skedar shumë më i vogël. Për Forza kjo kalon edhe ndarjen rrugë/buzë (shih më poshtë) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | hartat e tokës dhe teksturat e modeleve të cilës stinë |
| `--no-placed` | joaktiv | të gjitha | vetëm terreni: pa bordura, barriera, tabela, ndërtesa. Për BeamNG, sipërfaqet e drejtimit të modeluara si rrjeta mbahen prapë |
| `--trees` | joaktiv | të gjitha | vendos edhe bimësi (Forza: pemë, shkurre dhe objekte të thyeshme; BeamNG: pemë; AC Rally: pemë dhe gjethnaja e instancuar) |
| `--detail-budget N` | automatik | të gjitha | një tavan trekëndëshash për gjithçka të vendosur; shih [Nivelet e detajit dhe buxheti](detail-budget.md) |
| `--track DIR` | kërkohet | Forza | dosja e pistës (nën `media\Tracks`, që mban `GeoChunk0.minizip`) nëse loja e instaluar nuk duhet kërkuar |
| `--level NAME` | gjendet nga xhiroja | BeamNG, AC Rally | niveli (emri i dosjes në BeamNG) ose etapa (emri i hartës në AC Rally), pa dallim shkronjash |
| `--install DIR` | kërkohet në bibliotekat Steam | BeamNG, AC Rally | BeamNG: dosja që mban `gameengine.zip`. AC Rally: dosja e lojës, ose `acr\Content\Paks` / `Content\Paks` e saj |

Opsionet që nuk vlejnë për një lojë injorohen pa paralajmërim. Për shembull,
`--season` nuk bën asgjë për BeamNG dhe AC Rally, dhe `--track` nuk bën asgjë
as për to.

### Cila lojë {#which-game}

Loja merret nga `--game`, pastaj nga fusha `game` e një skedari `heat3d-lap`
(ose e rreshtit përshkrues `# {...}` të një CSV), pastaj parazgjedhja është Forza. Një dosje
merr lojën që e emërtojnë skedarët e saj, kur emërtojnë vetëm një; një skedar që nuk
emërton asnjë (një xhiro e FH Companion, `course.json`, një CSV pa rresht përshkrimi) nuk
llogaritet (shih [Të dhënat e xhiros](lap-inputs.md)).

| Vlera | Eksporti |
|---|---|
| fillon me `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ose `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | refuzohet: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | refuzohet: "tracks ship in a protected format that is not a file-extraction target" |
| çdo gjë tjetër | refuzohet: "there is no course reader for <game> yet" |

Një refuzim sugjeron edhe alternativat: rindërtoje kursin nga loja e luajtur
(3DHeat GameCapture), ose analizo xhirot pa kurs, sepse skeda Race analysis e
shikuesit vizaton një rrugë prej tyre.

### Shembuj {#examples}

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Shembull dalje (Forza, numra sintetikë):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Çdo makinë e një Forza të instaluar me detajet e ulëta të vetë lojës, në një skedar për
skedën e garës të shikuesit: modeli `ProxyLOD` që mban çdo arkiv makine nën `media/Cars`,
rreth 900 trekëndësha, me numrin e makinës siç e thotë telemetria,
markën, etiketën e modelit dhe vitin nga emri i arkivit, dhe rrotat e dritat e pasme.
Zgjat sekonda dhe shkruan rreth 5 MB. Ekzekutoje përsëri kur loja merr
makina të reja. Një arkiv pa një model të tillë (një objekt trafiku) emërtohet dhe lihet jashtë. Formati
është te [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Format janë në metra, të vetë lojës: 1:1 me makinën. Skedari mban
përmbajtjen e lojës, ndaj është për makinën ku u krijua, jo për t'u ndarë me të tjerë.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Kjo ekzekuton eksportin Forza `course` për çdo dosje kursi në një bibliotekë
xhirosh të regjistruara, duke shkruar nga një `<name>.glb` për secilin. Është vetëm për Forza. Thërret
eksportin e Forza drejtpërdrejt dhe nuk i lexon `--game`, `--level` ose `--install`.

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `-o`, `--out FOLDER` | `courses`, ose `$HEAT3D_LEVELS/forza/courses` kur ajo është vendosur | dosja ku të shkruhet (krijohet nëse mungon) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteka e xhirove |
| `--only TEXT [TEXT ...]` | të gjitha | vetëm kurset emrat e dosjeve të të cilave përmbajnë një nga këta (pa dallim shkronjash) |
| `--force` | joaktiv | eksporto përsëri ç'ka tashmë një `.glb` |
| `--track DIR` | kërkohet | si për `course` |
| `--margin M` | 80 | si për `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | si për `course` |

Çfarë llogaritet dosje kursi: një nëndosje e drejtpërdrejtë e bibliotekës emri i së cilës
përmban ` (course_`, ashtu siç i emërton FH Companion, për shembull
`Example Circuit (course_1200_3400_to_1175_3400)`. Pjesa nga ` (course_` e tutje
hiqet nga emri.

Si sillet një ekzekutim:

- Një kurs që ka tashmë `.glb` anashkalohet (`kept`) përveç nëse jepet `--force`, ndaj një ekzekutim i ndërprerë vazhdon aty ku ndaloi.
- Një `.glb` i shkruar nga një version më i vjetër, pa shtresën dhe vendet e vetë garës (`asset.extras.course_format` mungon ose është më i ulët se aktuali), eksportohet përsëri, sikur `--force` të ishte dhënë vetëm për të.
- Dy dosje kursesh me të njëjtin emër para ` (course_` (një regjistrues që e emëroi një kurs të ri si një të vjetër) nuk e mbishkruajnë njëra-tjetrën: dosja e krijuar e para mban `<name>.glb`, tjetra shkruhet si `<name>_<start>.glb`, ku `<start>` është ku fillon, me shenjat minus si `m` (për shembull `example_circuit_m120_m340.glb`).
- Një kurs që dështon (xhiro të palexueshme, pa kujtesë, pa terren...) raportohet si `FAILED`, dhe ekzekutimi vazhdon.
- Në fund printon një tabelë me gjendjen, madhësinë në MB, sekondat e harxhuara dhe emrin, pastaj `<n> of <total> courses in <folder>`.
- Kodi i daljes është 1 nëse ndonjë kurs dështoi.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Liston çdo garë që e përcakton një Forza e instaluar, nga përkufizimet e rrugëve të saj (shih
[Kurset e Forza Horizon](course-forza-horizon.md#which-race)), dhe kontrollon
eksportet në një dosje `courses` kundrejt tyre. Lexon lojën dhe bibliotekën e xhirove;
nuk shkruan asgjë përveç tabelës opsionale.

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `-o`, `--out FOLDER` | si për `courses` | dosja ku shkruan `courses`, skedarët e së cilës kontrollohen |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | biblioteka e xhirove |
| `--track DIR` | kërkohet | dosja e pistës, nëse nuk është ajo e lojës së instaluar |
| `--markdown FILE` | asnjë | shkruaj edhe tabelën atje, si Markdown |

Një rresht për garë, dhe një për çdo kurs të regjistruar të drejtuar mbi të:

| Kolona | Kuptimi |
|---|---|
| route | id-ja e rrugës |
| course | kursi i regjistruar që i përputhet, nëse ka |
| own assets | kopjet që gara shton në botën e lirë |
| drawn | prej tyre, kopjet modeli i të cilave e jep pista |
| kinds | kopjet e shtuara sipas llojit (barriera, objekte, decal-e, infrastrukturë, ...) |
| not geometry | shënues spektatorësh dhe spline-e përplasjeje, të numëruara |
| hidden | objektet e botës së lirë që gara i heq |
| venue | modelet e tokës së vendit që vija e AI-së së garës kalon brenda 10 m prej tyre |
| export | `current`, `older format` (eksportohet përsëri nga `courses`), `not exported`, ose bosh për një garë pa kurs të regjistruar |

Mbaron me një numërim: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Ky është prerja e Forza me çdo gjë të shkruar me dorë: jep dosjen e pistës dhe
një rajon, jo një xhiro. Është e dobishme kur zona që do është një kuti
dhe jo një drejtim.

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<path>` | i detyrueshëm | një dosje pistë e Forza nën `media\Tracks` (që mban `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | i detyrueshëm | `.glb` që do shkruhet |
| `--box X0 Z0 X1 Z1` | | rajoni, në metrat e lojës (x dhe z, siç i raporton telemetria); këndet në çdo radhë |
| `--route FILE` | | një JSON rruge me `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, siç e shkruajnë `heat3d_capture route` dhe `heat3d_capture laps`; lexohet si UTF-8, me ose pa shenjë renditjeje bajtesh |
| `--margin M` | **100** | metra të shtuara rreth kufijve të një rruge, dhe gjerësia e korridorit kur rruga ka vijë |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | si për `course` |

Jep saktësisht një nga `--box` dhe `--route`, përndryshe kodi i daljes është 2. Me
`--route`, prerja është `bounds` e rrugës (`min`/`max`, x dhe z) e zgjeruar me
marzhin. Nëse skedari mban edhe të paktën 10 pozicione, prerja ngushtohet në një
korridor `--margin` metrash rreth tyre, dhe modelet e vendosura marrin detajin sipas
largësisë nga ajo vijë. Me `--box`, mbahet e gjithë kutia, dhe detaji shkon te
ç'qëndron më afër mesit të kutisë.

Lartësia nuk është kurrë pjesë e prerjes. Një kuti jashtë hartës, ose në det, jep
"no terrain there" (kodi i daljes 1), jo një gabim për koordinatat.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` liston nivelet që jep një lojë Frostbite e instaluar, sipas emrit të
tabelës së tyre (`levels/<level>/<level>.toc`), me madhësinë e saj dhe nga vjen:
`Data` për lojën bazë, `Update/<pack>` për një përditësim, dhe sa tabela me
rezolucion të lartë i shtohen. Një nivel që e jep një përditësim ka një tabelë të vogël
vetëm copash edhe në lojën bazë; tabela me paketat e nivelit është
niveli (shih [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` eksporton një: heightfield-in e terrenit, çdo rrjetë që vendosin grupet
statike të modeleve të nivelit, objektet e vendosura një nga një, ku qëndrojnë, dhe
sfondin e terrenit të nivelit rreth hartës. Me `--textures`, çdo sipërfaqe mban
hartën e saj të ngjyrave; me `--navmesh`, vijnë edhe sipërfaqet ku ecin ushtarët. Si
lexohet është te [Frostbite](reader-frostbite.md).

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<level>` | i detyrueshëm | një emër siç e printon `levels`, një pjesë unike e tij, ose shtegu i `.toc` të një niveli |
| `-o`, `--out FILE` | `<level>.glb` (në `$HEAT3D_LEVELS/<game>/` kur ajo është vendosur) | `.glb` që do shkruhet |
| `--install FOLDER` | loja e parë Steam `Data` e së cilës mban një `layout.toc` | dosja e lojës |
| `--textures [PIXELS]` | joaktiv; 512 kur jepet pa madhësi | shkruaj hartën e ngjyrave të çdo sipërfaqeje, mip-in më të madh jo më të madh se PIXELS për anë, dhe koordinatat e teksturës siç i ka loja, me një mostrues përsëritës (shih [Formati i daljes](output-format.md)). Heightfield-i merr hartën e ngjyrave të sfondit të terrenit aty ku ajo hartë e mbulon, ndryshe ngjyrën e mesit të materialeve të sipërfaqes së terrenit, ndryshe ngjyrën mesatare të sfondit rreth tij. Joaktiv, çdo pjesë është një ngjyrë e sheshtë |
| `--ground-texture [METRES]` | joaktiv; 0.5 kur jepet pa madhësi | piq decal-et e terrenit - rrugë, pista, platforma, shenja të lyera - mbi ngjyrën e tokës, të shumëzuara me hartën e ngjyrave të terrenit kur niveli ka një, në ngjyrën e heightfield-it, METRES për piksel, në pllaka deri 4,096 pikselë (`ground:terrain x<x> z<z>`). Funksionon me ose pa `--textures` |
| `--navmesh` | joaktiv | shto rrjetën e navigimit të nivelit për agjentin e tij më të vogël, ushtarin (1.8 m i gjatë, 0.4 m i gjerë), si pjesën `nav:walkable`: toka, dyshemetë, shkallët dhe çatitë që arrin një ushtar, pa lidhjet (kërcime, shkallë, kapërcime) mes tyre |
| `--ground-spacing METRES` | 4 | hapësira më e imët e heightfield-it; nyjet më të imta mostrohen më rrallë. 0 e lë heightfield-in jashtë |
| `--detail-budget N` | çdo kopje në nivelin e saj më të ashpër, plus një çerek, të paktën 1,500,000 | një tavan trekëndëshash. Rrjetat që kushtojnë më shumë ulin një nivel detaji një herë, derisa të përshtaten; nëse as nivelet më të ashpra nuk përshtaten, kopjet më të vogla lihen jashtë të parat. Sfondi i terrenit nuk ashpërsohet dhe nuk lihet kurrë jashtë |
| `--skip TEXT` | | lër jashtë grupet statike të modeleve emri i ndarjes (partition) i të cilave përmban TEXT; përsërite për disa. Shtresa e një mënyre loje, për shembull |
| `--by-mesh` | joaktiv | për të gjetur çfarë është një pjesë: një pjesë për çdo rrjetë burimi dhe material, e emërtuar `<part> \| <mesh> \| <material>`; një skedar shumë më i madh |
| `--clamped-uvs` | joaktiv | për një renderues që nuk përsërit dot një teksturë: pret çdo trekëndësh të teksturuar në copa koordinatat e të cilave bien brenda 0..1, dhe vizaton një trekëndësh që do kërkonte më shumë se 4 copa në ngjyrën mesatare të teksturës së tij, në një pjesë `<part> (average colour)` |

Printon grupet dhe sa kopje vendosi secili, rrjetat që la jashtë dhe
pse, trekëndëshat për pjesë (dhe me `--textures` sa tekstura, dhe sa
seksione gjetën hartën e tyre të ngjyrave), çfarë është toka, dhe me
`--navmesh` sa pllaka navigimi u lexuan. Asgjë nuk shkruhet për nivelin përtej
gjeometrisë: pa emra, pa metadata (shih [Formati i daljes](output-format.md)).

Buxheti i terrenit është i veçantë: heightfield-i dhe sfondi nuk ashpërsohen
kurrë nga `--detail-budget`; `--ground-spacing` përcakton madhësinë e heightfield-it.

Një nivel i plotë është i madh: zakonisht mbi dhjetë milionë trekëndësha dhe disa
qindra MB. `--textures` i shton pak skedarit; një nivel plot pemë
mund të arrijë rreth 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
e sjell një nivel në afërsisht një të tretën e kësaj.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` është dosja e lojës, `Content/Paks` e saj, ose emri i dosjes së saj
në një bibliotekë Steam (`"<Steam game folder name>"`). `ue-maps` liston çdo hartë
që ka qeliza të gatuara World Partition pranë saj. `ue-map` eksporton një si
`ground:<map>` (peizazhi), `structure:<map>` (rrjetat e bashkuara HLOD të hartës)
dhe `water:<map>` (trupat e ujit ku qëndrojnë mbi tokë), në **centimetra** të Unreal
me Y dhe Z të këmbyera - i vetmi eksport që nuk është
në metra. Si lexohet dhe kontrollohet secili: [Hartat Unreal 5](level-unreal-world-partition.md).

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<map>` | i detyrueshëm | një emër siç e printon `ue-maps`, ose një pjesë unike e tij |
| `-o`, `--out FILE` | `<map>.glb` (në `$HEAT3D_LEVELS/<game>/` kur ajo është vendosur) | `.glb` që do shkruhet |
| `--ground-spacing METRES` | 2 | hapësira e kulmeve të peizazhit në skedar, e rrumbullakuar në një numër të plotë katrorësh të vetë atij |
| `--no-structures`, `--no-water` | | lër atë pjesë jashtë |

Printon trekëndëshat për pjesë, sa komponentë peizazhi u lexuan dhe
sa nga kulmet që ruajnë dy herë nuk përputhen. Një hartë 3 km me 2 m është rreth
4.6 milionë trekëndësha toke.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` liston çdo botë me terren, sipas dosjes së saj nën
`worlds/`. `enfusion-world` eksporton një: `ground:<world>` (terreni, në
ngjyrat e pllakave të supertekturës së tij), `water:<world>` (deti, në lartësi zero)
dhe `structure:<world>` (kutia e çdo modeli të vendosur), në metrat e vetë lojës -
x lindje, y lart, z veri. Si lexohet dhe kontrollohet secili:
[Botët e Arma Reforger](level-arma-reforger.md).

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `<world>` | i detyrueshëm | një botë siç e printon `enfusion-worlds` |
| `-o`, `--out FILE` | `<world>.glb` (në `$HEAT3D_LEVELS/<game>/` kur ajo është vendosur) | `.glb` që do shkruhet |
| `--install FOLDER` | biblioteka Steam që mban lojën | dosja e lojës |
| `--ground-spacing METRES` | 2 (ajo e vetë terrenit) | hapësira e kulmeve të terrenit në skedar |
| `--texture-size PIXELS` | 4096 | ana më e madhe e imazhit të ngjyrës së tokës; 0 për ngjyrë të sheshtë |
| `--no-structures` | | lër jashtë modelet e vendosura |
| `--trees` | joaktiv | vendos edhe pemë dhe bimësi tjetër, si kuti |

Printon trekëndëshat për pjesë, sa kulme të skajeve të pllakave nuk përputhen, sa
entitete mban skedari i botës dhe sa kuti u vendosën, dhe çfarë u la
jashtë dhe pse.

## Ndryshoret e mjedisit {#environment-variables}

| Ndryshorja | Efekti |
|---|---|
| `HEAT3D_OODLE` | shtegu i një `oo2core_*_win64.dll`, ose i një dosjeje që mban një; shih [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | një dosje për çdo eksport të bërë pa `-o`: ato të çdo loje shkojnë te `<HEAT3D_LEVELS>/<game>/` (kurset te `<game>/courses/`, paketa e makinave te `forza/`). Pa e vendosur, shkojnë në dosjen aktuale |
| `HEAT3D_NO_UPDATE` | çdo vlerë tjetër përveç bosh, `0`, `false`, `no` e çaktivizon kontrollin e përditësimit; shih [Përditësimet](updates.md) |
| `LOCALAPPDATA` | ku kërkohen biblioteka e FH Companion, dosja e përdoruesit të BeamNG dhe cache e përditësimeve |
| `HEAT3D_COURSE` | vetëm për teste: kursi që përdor testi i bordurave të lojës së instaluar; shih [Zhvillimi](development.md) |
