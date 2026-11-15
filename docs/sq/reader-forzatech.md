---
title: "ForzaTech"
nav_order: 7
lang: "sq"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, mostra, vendosje {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon punon mbi ForzaTech, motorin e vetë të Turn 10. Këta lexues e çojnë një pistë
nga arkivat e saj deri te trekëndëshat e pozicionuar dhe të teksturuar. Arrihen
përmes `course`, `courses` dhe `terrain` (shih
[Forza Horizon](course-forza-horizon.md)). `identify` njeh një `.minizip`
dhe një `.modelbin` të vetëm, dhe `list` e `extract` marrin një `.minizip`, sipas emrave
në `ChunkContentsMiniZip<n>.txt` pranë tij ose sipas numrit të hyrjes (`#12`).

| Formati | Moduli |
|---|---|
| arkivat `.minizip` dhe listat e emrave të tyre | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modelet dhe terreni `.modelbin` | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| mostrat e teksturave `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| skedarët e vendosjes `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` dhe hash-et e teksturave të materialeve | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| pllakat e terrenit sipas vendit | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza e mban një pjesë të madhe të përmbajtjes edhe në arkiva ZIP të zakonshme nën `media\`.
`zipfile` i Python i hap ato, dhe `forzatech.models_in_archive()` liston hyrjet e tyre
`.modelbin`. Gjeometria e pistës është në arkivat `.minizip`.

## `.minizip`: një arkiv pa emra {#minizip-an-archive-with-no-names}

Një pistë dërgon katër arkiva `GeoChunk<n>.minizip`, dhjetëra gigabajt secili për një
hartë me botë të hapur, me qindra mijëra hyrje. **Arkivat nuk ruajnë asnjë
emër**: pa tabelë emrash dhe pa kokë për çdo hyrje, vetëm një numër rendor. Emrat
janë në `ChunkContentsMiniZip<n>.txt` pranë çdo arkivi, një rresht për çdo hyrje sipas
rendit të hyrjeve (`<build path>zipcache\pc\<path>|<bundle>`). Kjo çiftëzim është e vetmja
mënyrë për të kërkuar një skedar. Gjithçka deri te `zipcache\pc\` hiqet, dhe kërkimet
injorojnë shkronjat e mëdha e të vogla.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tri detaje në indeks prodhojnë prapë dalje kur lexohen gabim. Lexuesi i bën
të tria saktë:

| Detaji | Çfarë bën një lexues i pakujdesshëm | Si duket |
|---|---|---|
| baza e segmentit është **64-bit** | e lexon si u32 plus mbushje | e saktë për 4 GB e para, pastaj zhurmë me gjatësinë e duhur |
| baza është **e përafruar në 8 bajte** | injoron fjalën e mbushjes pas tabelës së paketave | në arkivat me numër çift paketash, çdo hyrje pretendon një kodek që nuk ekziston |
| gjatësia e ruajtur e një hyrjeje është hapësira deri te hyrja tjetër (ose baza e segmentit tjetër) **minus mbushjen e saj** (bitet e flamurit 12-13) | përdor të gjithë hapësirën | LZ4 e refuzon bllokun krejt |

Kodekët janë pesë bitet e ulët të flamurëve: `0x00` stored, `0x08` raw deflate,
`0x1F` bllok LZ4. Çdo tjetër refuzohet. Çdo hyrje duhet të zbërthehet saktësisht në
madhësinë që deklaron, përndryshe refuzohet. Indeksi (rreth 5 MB) lexohet një herë, dhe
ngarkesat lexohen duke kërkuar (seek).

Koka kontrollohet: magjia, një kokë 32-bajtëshe, dhe një numër segmentesh që përputhet me
`ceil(entries / per segment)`.

**Verifikuar:** hyrje të mostruara nëpër çdo arkiv të një harte, secila
e zbërthyer saktësisht në gjatësinë e vet të deklaruar nën të tre kodekët.

## `.modelbin`: kontejneri i copave {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Madhësia e deklaruar e skedarit duhet të jetë e barabartë me madhësinë e vërtetë.
- **Zinxhiri**: çdo copë fillon aty ku mbaroi e mëparshmja, e rrumbullakuar lart në 4
  bajte. Asgjë në skedar nuk e thotë këtë, prandaj është provë: një regjistër i lexuar
  me hap të gabuar nuk e prodhon. Vlente për të 252 modelet e mostruara.
- Një skedar `PGZP` që i jepet lexuesit të modeleve emërtohet "a ForzaTech .minizip
  archive, not a model" dhe drejtohet te `minizip.py`, në vend që të refuzohet thatë.

Gjeometria vjen nga këto copa:

| Copa | Mban |
|---|---|
| `VLay` | një strukturë kulmesh: emrat e atributeve, pastaj elementet (indeksi i emrit u16, kanali u16, buferi, formati DXGI, ofseti); numri i elementeve është u16 |
| `VerB` | një bufer kulmesh pas një koke 16-bajtëshe (numri, madhësia, hapi u16, atributet u16, formati) |
| `IndB` | buferi i indekseve, e njëjta kokë |
| `Mesh` | një nën-rrjetë: materiali, maska e nivelit të detajit, diapazoni i indekseve, struktura, buferi, hapi, tabela e varianteve, dhe një kuti pozicioni në fund |
| `MatI` | një instancë materiali: shtegu i tij `.materialbin` dhe hash-et e teksturave |

### Pozicionet dhe kutia {#positions-and-the-box}

Pozicionet janë `R16G16B16A16_SNORM` (formati 13): katër short me shenjë për kulm.
`position = short / 32767 * scale + bias`, ku scale dhe bias janë 32 bajtet e fundit
të copës `Mesh` (dy float4). Bias është në **koordinatat e botës së lojës**, prandaj një
pllakë terreni bie aty ku e vë loja pa transformim instance. Prandaj një xhiro telemetrie
mjafton për të kërkuar një copë harte.
Çdo nën-rrjetë e një modeli mban të njëjtën kuti (kontrolluar nëpër 860 prej tyre).

### Struktura e kulmeve {#the-vertex-layout}

Një bufer pozicionesh mbulon çdo kulm. Atributet e tjera ndahen në
grupe kulmesh të njëpasnjëshme, secili me buferin e vet dhe strukturën e vet: rruga pranë
një kryqëzimi mban tre grupe UV dhe dy tangjente, bregu pranë saj vetëm një
normale. Çdo atribut jo-pozicion është katër bajte. Cila strukturë përshkruan cilin
bufer merret nga nën-rrjetat që vizatojnë prej tij, sepse strukturat dhe buferat
nuk janë në të njëjtin rend (i njëjti, i rrotulluar me një, ose i permutuar, sipas
modelit).

| Formati DXGI | Kodi | Përdoret për |
|---|---|---|
| R16G16B16A16_SNORM | 13 | pozicion (short i katërt është x i normales) |
| R16G16_SNORM | 37 | normale y, z |
| R16G16_UNORM | 35 | një çift UV (kanali = cili grup) |
| R8G8B8A8_UNORM | 28 | ngjyrë ose pesha përzierjeje |
| R10G10B10A2_UNORM | 24 | tangjente (nuk dekodohet) |
| R16_UINT | 57 | indekse |

**Normalja është e ndarë.** `NORMAL` mban y dhe z. X është short i katërt i
pozicionit, që dukej si mbushje. Mbi qindra mijëra kulme terreni korrelon
+0.92 me x të normales së trekëndëshit dhe me asgjë tjetër. Me të, 96% e
kulmeve të tokës së pjerrët janë brenda 18° nga normalja e llogaritur. Çdo kodim me dy përbërës
i provuar pa të (oktaedral në të 48 renditjet mes tyre) e kishte y
dhe z të saktë dhe x të gabuar.

Formatet e tjera të pozicionit ose indekseve **refuzohen** ("only 13 (four shorts, scaled) is
implemented"; "only unsigned shorts are implemented").

### Nën-rrjetat {#submeshes}

Një regjistër `Mesh` është 238 bajte në formën standarde. Ata më të gjatë mbajnë një tabelë
**variantesh** materiali më të gjatë në fillim, 238 + 8 x count - 4 bajte, dhe çdo
fushë pas saj lëviz mbrapsht saktësisht aq. Ata më të shkurtër (218 bajte, disa
terrene) i mbajnë ofsetet. Çdo hyrje varianti është
`u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Maska e
nivelit të detajit është u16, një bit për çdo nivel duke filluar nga biti 1.

Asgjë nuk besohet vetëm. Diapazonet e indekseve duhet ta mbulojnë buferin e indekseve saktësisht,
çdo `index count` duhet të jetë i barabartë me 3 x `triangles`, dhe hapi që emërton një nën-rrjetë
duhet të jetë ai i buferit të saj. Një tabelë që dështon refuzohet e tëra, sepse
etiketimi i trekëndëshave nga fusha të lexuara gabim është më keq se mosetiketimi. Nëpër mijëra
nën-rrjeta të mostruara, secila që ka indeksin e buferit në diapazon e kalon.

### Materialet dhe hash-et e teksturave {#materials-and-texture-hashes}

Një `MatI` e emërton materialin e vet me një shteg `Game:...\x.materialbin`, të gjetur duke
kërkuar në copë. Teksturat e tij janë regjistra `u32 slot, u32, u32 hash`, 33 bajte
larg njëri-tjetrit dhe të papërafruar, prandaj copa kërkohet në çdo ofset bajti për fjalë që
janë hash-e të njohura teksturash. Ato vijnë nga `AssetManifest.xml` e pistës
(`<Texture Source="...\name.swatch" SourceHash="...">`, i lexuar deri te
`</Textures>`). Vendi `0x88B483AA` është ngjyra bazë e shaderit standard. Si zgjidhet
pastaj tekstura e ngjyrës është te
[Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: mostrat e teksturave {#pb-texture-swatches}

Një mostër është i njëjti kontejner `burG` si një model: një kokë `HCXT` 96-bajtëshe në bajtin
44, pastaj një copë pikselësh. Koka mban GUID-in e teksturës (atë në emrin e
skedarit të saj), gjerësinë dhe lartësinë, numrin e mip-eve, dhe **kodin e formatit në bajtin 72**
(numërimi i vetë ForzaTech). Bajti 84 mban numrin e bajteve të pikselave.

| Kodi | Formati | Identifikuar si |
|---|---|---|
| 0 | BC1, gjysmë bajti për piksel | dekodohet në një bordurë të kuqe e të bardhë (zhurmë nën BC4) |
| 9 | BC7, një bajt për piksel | dekodohet në një pllakë terreni ku duket qarku |
| 13 | RGBA8, katër bajte për piksel | e thjeshtë |
| tjetër | refuzohet | "texture format N has not been identified; refusing to guess" |

Formatet u identifikuan duke dekoduar skedarë të vërtetë në çdo mënyrë që e lejon madhësia e ngarkesës.
Bajti 47, që një version i mëparshëm e mori për format, është 4 në çdo një nga teksturat
e mostruara. Dekodohet vetëm mip-i i sipërm i një skedari. Çdo rezolucion është
hyrja e vet, `<name>_<guid>_quality<n>.pb`, cilësia 1 më e vogla deri 5 më e madhja. Për
hartat e terrenit dy më të mëdhatë janë në një arkiv tjetër nga të tjerat. Dekodimi
kalon përmes dekoduesit BCn të Pillow, nëpërmjet një koke DDS të gjeneruar.

## Skedarët e vendosjes (.pgeo) {#placement-files-pgeo}

Një skedar për çdo kategori për çdo qelizë hapësinore:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Vetëm shtegu
jep katrorin dhe kategorinë e qelizës, prandaj skedarët mund të filtrohen pa i hapur.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Si u vendos çdo fushë:

| Fusha | Vendosur nga |
|---|---|
| pozicioni është pikë fikse 16.16, jo një pjesë e kutisë | parmakët e njëpasnjëshëm janë saktësisht 4.000 m larg njëri-tjetrit (gjatësia e modelit) |
| shenjë-madhësi, jo plotësim i dyshit | plotësimi i dyshit i vuri koordinatat negative dhjetëra kilometra jashtë hartës; me bitin 31 si shenjë, çdo regjistër i çdo kategorie të mostruar bie brenda kutisë së skedarit të vet |
| vektorët janë akset e vetë modelit | fundi i çdo parmaku bie mbi fillimin e tjetrit: 93.5% brenda 5 cm, mediana 0.000 m |
| bajti 60 është varianti | pesë kopjet e një billboard lexojnë 0, 2, 2, 3, 4 ndërsa çdo parmak lexon 0 |

Vetëm emrat që mbarojnë me `_3D` janë regjistra modelesh. Tabela e varianteve para tyre liston
emra pa prapashtesën, dhe të lexuara si regjistra ato bien në pafundësi. Një regjistër
kandidat pranohet vetëm nëse numri i tij futet në skedar, dhe instancat me
numra jo të fundëm hidhen.

## Nuk është zbatuar {#not-implemented}

- Formatet e kulmeve dhe indekseve përveç atyre më sipër (refuzohen).
- Formatet e teksturave përveç 0, 9, 13 (refuzohen).
- Tangjentet (kapërcehen, nuk përdoren).
- Shtresat e materialeve të shaderit të terrenit. Teksturë e tokës është një interpretim i hartave të pllakave (shih [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
