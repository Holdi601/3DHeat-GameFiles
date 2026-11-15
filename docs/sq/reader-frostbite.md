---
title: "Frostbite"
nav_order: 5
lang: "sq"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paketa, rrjeta dhe nivele {#frostbite-toc-cas-bundles-meshes-and-levels}

**Lexon një nivel të Battlefield 6 deri te terreni i tij, rrjetat e vendosura dhe
hartat e tyre të ngjyrave, dhe e shkruan si `.glb`.** Lojërat Frostbite (Battlefield, Need for Speed, Dead Space) e mbajnë
përmbajtjen e tyre në blloqe `.cas`, të përshkruara nga tabela përmbajtjeje `.toc`. Tabela e një niveli
thotë cilat paketa (bundles) ngarkon niveli, paketat emërtojnë çdo aset,
dhe asetet thonë cila rrjetë qëndron ku.

Burimet:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabelat, paketat e instalimit, ngarkesat),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paketat dhe manifestet e tyre),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(ndarjet EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(heightfield),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(tekstura dhe materiale),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(vendosja dhe eksporti).
Komandat: `identify`, `levels`, `level` (shih [Komandat](commands.md#levels-and-level-frostbite)).

Asgjë këtu nuk është dokumentuar nga loja. Çdo strukturë më poshtë u lexua nga
skedarët dhe pastaj u krahasua me të gjithë, dhe çdo seksion thotë cili ishte
kontrolli. Aty ku mjetet e modifikimit Frosty përshkruajnë versione më të vjetra të një strukture,
emrat e fushave ndjekin të tyret; nuk u mor asnjë kod prej tyre (shih
[Rregullat dhe licencat](rules-and-licences.md)).

## Kryet që duket i enkriptuar dhe nuk është {#the-header-that-looks-encrypted-and-is-not}

| Magjia (u32, little-endian) | Kuptimi | Trajtimi |
|---|---|---|
| `0x00CED100` | e thjeshtë: pema fillon menjëherë | lexohet |
| `0x01CED100` | e nënshkruar: një nënshkrim 556 bajtësh, pastaj pema **në të qartë** | lexohet |
| `0x03CED100` | e turbulluar me XOR, me çelësin në kryet e vetë skedarit | zbulohet dhe refuzohet |

Forma e nënshkruar është ajo që jep Battlefield aktual. Bajtet me entropi të lartë pas
magjisë janë një nënshkrim, jo tekst i enkriptuar.

## Pema DbObject {#the-dbobject-tree}

Një strukturë rekursive. Çdo fushë është një bajt tipi (pesë bitet e ulët janë tipi, biti 7
"anonim"), një emër opsional, dhe një vlerë. Kontejnerët mbajnë gjatësinë e tyre si
numër të plotë me gjatësi të ndryshueshme dhe mbarojnë me një bajt zero. `parse_toc` kontrollon gjatësinë
e çdo kontejneri, ndaj një skedar që lexohet është kuptuar. `layout.toc` është në
këtë formë.

## Paketat e instalimit {#installation-packages}

Çdo vendndodhje emërton **paketën e instalimit** së cilës i përket blloku i saj. Çdo
paketë i numëron blloqet e veta nga `cas_01`, ndaj numri i bllokut vetëm është i paqartë
sapo instalohet më shumë se një paketë, çka ndodh gjithmonë.

- `layout.toc` liston paketat nën `installManifest.installChunks`, secila
  me një `persistentIndex` dhe një `installBundle` si
  `Win32/installation/<package>`.
- Blloqet e paketës janë në atë dosje, nën `Data` për lojën bazë ose
  nën `Update/<pack>/Data` për atë që erdhi më vonë.
- Një regjistrim vendndodhjeje mban `persistentIndex` të plotë 32-bitësh: gjysma e ulët e
  fjalës së tij të parë mban gjysmën e lartë, gjysma e lartë e fjalës së dytë gjysmën e ulët;
  gjysma e ulët e fjalës së dytë është numri i bllokut.

Kontroll: çdo vendndodhje në çdo tabelë binare të një instalimi
zgjidhet te një paketë e deklaruar dhe bie brenda bllokut që emërton. Një version
më i hershëm merrte `cas_NN.cas` e parë me numrin e duhur. Një e treta e
ngarkesave që lexonte atëherë dukeshin me entropi të lartë dhe u morën për enkriptim.
Ishin zhvendosjet e duhura në skedarin e gabuar. Asgjë e gjetur nuk është e enkriptuar.

## Tabela e nivelit {#the-level-table}

Tabela e një niveli (`levels/<level>/<level>.toc`) është një tabelë seksionesh: pesëmbëdhjetë
fjalë kryeje big-endian, pastaj seksione të vendosura njëri pas tjetrit, zhvendosjet e të cilëve janë
si të deklaruara ashtu edhe të nxjerrshme nga dy numërues.

| Seksioni | Përmbajtja |
|---|---|
| bundles | një tabelë hash (një fjalë secila), pastaj një regjistrim 16 bajtësh për paketë: çelësi, `0x40000000` \| madhësia, 0, zhvendosja |
| tabela hash e copave | një fjalë për copë (chunk) |
| chunks | id 16 bajtëshe (GUID i copës **me bajtet e kthyera**), pastaj një fjalë: `0x80000000` \| 4 x indeksi i vendndodhjes së saj |
| locations | katër fjalë big-endian: paketa (e ndarë), blloku, zhvendosja, madhësia |

Id-të e copave dhe vendndodhjet janë **në radhë të ndryshme**. Leximi i tyre sipas
radhës së skedarit çifton çdo copë me bajtet e një copeje tjetër, të cilat dekodohen
shkëlqyeshëm (kryesisht si tingull) dhe ndaj nuk duken gabim derisa një rrjetë del si zhurmë.
Kontroll: në një nivel, fjalët e indeksit janë një permutacion i 0 deri te numri i copave
minus një.

Paketat ruhen në vazhdim pas tabelës së seksioneve. Secila është nëntë fjalë kryeje
big-endian, pastaj hyrjet e saj: tetë bajte zhvendosje e madhësi, të paraprira nga
tetë të tjera që emërtojnë paketën dhe bllokun kur bajti i flamurit të hyrjes ka bitin e lartë
të vendosur. Kontroll: në çdo paketë, hyrja e fundit mbaron saktësisht aty ku fillojnë
bajtet e flamujve.

### Cila tabelë është niveli {#which-table-is-the-level}

Një nivel mund të ketë disa tabela me të njëjtin emër: një në `Data` të lojës bazë,
një në çdo përditësim (`Update/<pack>/Data`) që e jep ose e ndryshon, dhe
një në çdo paketë me rezolucion të lartë
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Vetëm disa mbajnë
paketa. Për një nivel që e jep një përditësim, tabela në lojën bazë mban vetëm
copa dhe asnjë paketë, dhe ajo në përditësim është niveli; marrja e tabelës së
parë të gjetur nuk eksportonte asgjë prej tij.

Ndaj niveli është tabela me më shumë paketa, me një shtresë të mëvonshme që fiton në barazim
(loja bazë së pari, pastaj përditësimet sipas emrit), dhe tabelat e të njëjtit emër
pa paketa janë **suplementet** e tij: copat e tyre i shtohen atyre të nivelit,
sepse mbajnë mip-et më të mëdha të teksturave të tij. Një kokë teksture e emërton atë
copë te +164 (shih [Teksturat dhe materialet](#textures-and-materials)). `levels`
printon nga vjen çdo nivel dhe sa suplemente ka.

## Manifestet e paketave {#bundle-manifests}

Hyrja e parë e një pakete është manifesti i saj, i ruajtur i pakompresuar. Është formati
binar i paketave të lojërave më të hershme Frostbite me një magji të re, `0xD68E799D`: numërues,
SHA-1, regjistrime ebx dhe res (zhvendosja e emrit dhe madhësia), tipe res, metadata dhe
id, GUID-e copash, vargje teksti. Hyrjet e tjera të paketës janë ebx, res
dhe copat sipas asaj radhe. Kontroll: numëruesit përputhen me hyrjet në çdo
paketë, dhe vargjet e tekstit fillojnë aty ku mbarojnë regjistrimet.

Tipet e burimeve janë hash-e. `0x49B156D4` është MeshSet (çdo res i atij tipi
emërtohet `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` i lexon të gjitha këto për një nivel, në pak sekonda: një nivel
ka dhjetëra paketa dhe dhjetëra mijëra ebx, res dhe copa.

## Blloqet e ngarkesës {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Një madhësi e kompresuar zero do të thotë e ruajtur, sa gjatësia në të cilën dekompresohet.

| Fjala e metodës | Kodeku |
|---|---|
| `0x0070`, `0x0071` | asnjë |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), nga DLL-ja `oo2core` e vetë lojës) |
| tjetër, me madhësi të barabarta | kopjohet siç është ruajtur |
| tjetër | refuzohet |

Të lexuar nga paketa e duhur, çdo ngarkesë e mostruar dekodohet.

## Ndarjet EBX {#ebx-partitions}

EBX mban gjithçka që nuk është të dhëna të papërpunuara. Çdo ndarje (partition) është një skedar RIFF:
`EBXD` (të dhënat, të rreshtuara në 16), `EFIX` (GUID i ndarjes, GUID-e tipesh dhe
nënshkrime, zhvendosje instance, treguesish, importesh dhe informacioni tipesh, importet, dhe
zhvendosjet e vargjeve, vlerave të kutizuara dhe vargjeve të tekstit), `EBXX` (tabela e vargjeve: zhvendosja, numri,
hash, flamujt, tipi i elementit). Një fushë treguesi është tetë bajte: zero është null, një vlerë
tek është importi numër `value >> 1`, çdo gjë tjetër është relative me fushën.

**Biblioteka e tipeve nuk lexohet**. Loja e jep në sistemin e saj fillestar
të skedarëve, që është i enkriptuar, dhe ky paketë nuk e prek. Tipet njihen
nga GUID dhe nënshkrimi, që e mbart çdo ndarje, dhe ato pak tipe që i duhen eksportit të nivelit
u ngritën nga të dhënat.

## MeshSet {#meshset}

Një rrjetë është një res MeshSet (përshkrimi) dhe një copë për çdo nivel detaji (buferat).

| Pjesa | Struktura |
|---|---|
| prefix | katër fjalë: madhësia e kryeje (176 ose 192), madhësia e regjistrimit të nivelit (176 deri 188), madhësia e regjistrimit të seksionit (368), 0 |
| header | kutia kufizuese; gjashtë zhvendosje nivelesh i64; tipi i rrjetës te `0x6C` (e ngurtë, me skelet, e përbërë); numrat e niveleve dhe seksioneve te `0x9C` |
| level | seksionet te `+0x08`; pesë lista vizatimi te `+0x14` (opake, e tejdukshme, decal, vetëm thellësi, hijezim); formati i indeksit `+0x54` (`0x21` u16, `0x2E` u32), bajtet e indeksit dhe kulmeve; GUID i copës te `+0x74` |
| section | emri i materialit; hapi (stride) i kulmeve; trekëndëshat, indeksi i parë, zhvendosja e kulmeve (bajte), numri i kulmeve te `+0x20`; deklarata e kulmeve te `+0x64`: 16 x (përdorimi, formati, zhvendosja, rrjedha), 16 hapa rrjedhash, numërues |
| chunk | buferi i kulmeve, pastaj buferi i indekseve. Rrjedhat e një seksioni vijnë njëra pas tjetrës; indekset numërohen nga kulmi i parë i seksionit |

Pozicionet janë përdorimi 1, rrjedha 0, zhvendosja 0, si katër gjysma (half) ose tre float.
Vizatohen vetëm seksionet opake dhe të tejdukshme. Çdo seksion me emrin
`..._shadow` është në listën e hijeve dhe vetëm aty, ndaj listat vendosin.

Kontroll: çdo rrjetë e një niveli, nivelet e së cilës ruhen në copa, dekodohet, dhe
pothuajse të gjitha kanë 99% ose më shumë të kulmeve brenda kutisë së tyre të deklaruar; pjesa
tjetër e humbet për shkak të rrumbullakimit të gjysmë-float. Një arkë e dekoduar mat rreth një metër, Y lart, me normalet e saj që shohin
nga jashtë.

## Vendosja {#placement}

Tubacioni i përmbajtjes mbledh objektet statike të secilës nënbotë në një
**grup modelesh statike**: një varg anëtarësh, një për rrjetë, secili me
transformimet e instance-ve të tij.

| Tipi (GUID, nënshkrimi) | Struktura |
|---|---|
| anëtar `ad13064e…`, `0xF861A878` | 224 bajte: `+88` varg transformimesh, `+112` plani i objektit (import), `+160` aseti i rrjetës (import) |
| transformim `101dce06…`, `0x5E6D8C37` | 64 bajte: right, up, forward, translation, secili një vec3 i plotësuar në 16 |

Ndarja e asetit të rrjetës emërtohet si res-i i saj MeshSet, ndaj GUID-i i ndarjes së importit
jep rrjetën. Një pikë ulet te
`x·right + y·up + z·forward + translation`. Transformimi i vetë grupit ishte
identiteti në çdo grup të niveleve të kontrolluara, dhe nuk aplikohet.

Kontroll: në një nivel, çdo anëtar i çdo grupi zgjidhet te një rrjetë; shumica e kopjeve kanë një rrotullim me determinant 1 deri në një
të mijtën, pjesa tjetër janë të shkallëzuara ose të pasqyruara. GUID-et dhe nënshkrimet e tipeve janë
të njëjta në nivele të tjera. Një përditësim loje që ndryshon strukturën ndryshon
nënshkrimin, dhe lexuesi atëherë nuk gjen asgjë në vend që të lexojë gabim.

### Objektet e vendosura një nga një {#objects-placed-one-by-one}

Ç'nuk mund të grupojë tubacioni — objekte të shkatërrueshme, kontejnerë, mbeturina — vendoset
nga **referencat e objekteve** dhe **referencat e prefab-eve** në ndarjet e
nivelit:

| Tipi (GUID, nënshkrimi) | Struktura |
|---|---|
| referencë objekti `a9a6a6ad…`, `0xC4856BEC` | `+32` transformimi (si më sipër), `+112` plani i objektit (import) |
| referencë prefab `117c746e…`, `0xDE3FE9B4` | e njëjta; plani është një prefab, një ndarje referencash të tjera |

Prefab-et folen; një kopje ulet te transformimi i saj herë ai i prindit (vektorë rreshtash),
deri në tetë nivele. Një plan objekti vizatohet si rrjetat që importon,
duke lënë jashtë gjendjet e shkatërruara (`dc_...`). Një prefab i grupuar
referohet si mbetja e tij `..._nongroupable_autogen`, ndaj asgjë nuk vizatohet dy herë.

Ecja fillon vetëm nga botët dhe shtresat e nivelit. Një ndarje instanca e parë e së cilës
është një plan prefab-i (`134919fc…`, `0x0247807D`) është përkufizimi i një prefab-i,
dhe një nivel mban shumë nën dosjen e vet, të vendosur nga botët e tij
në mënyra të tjera nga këto referenca; e ecur sikur të ishte një botë, një
prefab i vë përmbajtjen në koordinatat e tij lokale. Kjo grumbullon
qindra kopje rreth origjinës së botës, shumë poshtë tokës. Botët dhe shtresat kanë `a10ebe0f…`, `0xD3D16C3C` të parën.

Planet e inskenuara jashtë lojës nuk ndiqen: asetet e zhvillimit dhe testimit
(`game/dev/`, `test/`), set-i i kinematikës së fundit të raundit (`..._gameend_...`: inskenuar
nën tokë)
dhe kontrolluesi i kamerës së vdekjes (`.../deathflow/...`, ku pajisjet e saj qëndrojnë
në origjinën e botës). Njihen nga shtegu i asetit të tyre, jo nga shtresa e tyre:
e njëjta shtresë që mban set-in e kinematikës mund të vendosë muret dhe çatitë e vërteta të një niveli.
Pas të dy rregullave asnjë kopje në nivelet e kontrolluara nuk qëndron
më shumë se 10 m nën terren, dhe kopjet qëndrojnë në terren aty ku i tregon loja.

**Nivele detaji që zëvendësojnë.** Niveli i fundit i detajit i një rrjete mund të kalojë
te një zëvendësues pamjeje të largët me një material të vetin: `M_LastLod`,
`M_Billboard`, `M_Vista`, `M_ProjectionLod`. Një kullë grilë me dhjetëra
mijëra trekëndësha mund të mbarojë në një silueta me disa qindra, të cilën
buxheti do ta zgjidhte dhe që nga afër është një gjemb i ngurtë. Një nivel detaji që sjell një material të tillë, që niveli
më i imët i tij nuk e ka, nuk zgjidhet kurrë; niveli më i ashpër i rrjetës është i fundit i vërtetë.

## Terreni {#terrain}

Burimi: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terreni është një res TerrainStreamingTree (tipi `0x22FE8AC8`) dhe copat që emërton.

| Pjesa | Struktura |
|---|---|
| header | 34 bajte; numri i nyjeve te 25 |
| pemët raster | një bajt tipi dhe një gjatësi u32 secila, deri te një bajt tipi `0xFF`. Tipi 0 është heightfield-i: mostra për anë te +5 (265), diapazoni i lartësisë te +21 (1,280 m), katrori i terrenit në regjistrimin e nyjes së parë te +77 (8,192 m në nivelin e kontrolluar). Mban kutitë kufizuese të nyjeve dhe një piramidë min/max 16 x 16 për nyje, jo lartësitë |
| nyjet e transmetimit | quadtree, thellësi së pari: madhësia e copës dhe GUID; një copë e dytë opsionale; një bajt flamuri (biti 0: copa fillon me një faqe lartësie); ka-fëmijë. Fëmijët në radhën (0,0), (1,0), (1,1), (0,1) |
| faqja e lartësisë | u16 e parë 265 x 265 e copës së një nyjeje me flamur, rresht pas rreshti; lartësia = vlera x 1,280 / 65,535 m; kolonat përgjatë x, rreshtat përgjatë z, nga këndi i ulët i nyjes; një kufi prej 4 mostrash, kështu 256 qeliza për nyje |

Çdo hap u kontrollua më vete:

- Leximi i quadtree-t të nyjeve e konsumon res-in deri në bajtin e fundit, me
  529 nyjet e deklaruara.
- Nyjet fqinje ndajnë nëntë kolonat e skajit saktësisht, ndaj hapi është 256.
- Mostrat e një fëmije në çdo pozicion të dytë barazojnë saktësisht ato të prindit
  me një kufi 4, dhe janë 90 deri 700 njësi larg me çdo kufi tjetër.
- Fjala më e ulët në nivel dekodohet te lartësia më e ulët e kutisë kufizuese deri
  në centimetër.
- Nga tetë mënyrat se si mund të shtrihej katrori në botë, vetëm x përgjatë x dhe z
  përgjatë z i vë objektet e vendosura mbi të: gjysma e kopjeve të mostruara brenda
  rreth 2 m, kundrejt disa herë më shumë për çdo mënyrë tjetër.

Objektet e vendosura e masin pastaj rezultatin. Pika më e ulët e çdo kopjeje,
kundrejt terrenit poshtë saj (bilinear, nga nyja më e imët):

| E vendosur | Largësia mediane | Mediana me shenjë |
|---|---|---|
| pemë dhe shkurre | shumë nën një metër | pak nën sipërfaqe |
| objekte | një a dy metra | në sipërfaqe |
| shkëmbinj | rreth një metër | të ngulur rreth një metër |
| ndërtesa | disa metra (qëndrojnë mbi themele) | pak të ngulura |

Bimësia vendoset në tokë dhe askund tjetër, çka e bën kontrollin më të mprehtë:
origjinat e saj qëndrojnë një mediane 0.07 m nga sipërfaqja. Ndërtesat
përhapen gjerësisht sepse kategoria mban mure, dysheme dhe pjesë kit të
strukturave shumëkatëshe dhe nëntokësore. Zhvendosja e terrenit 64 m anash
ul pjesën e kopjeve brenda 0.5 m nga 29% në 10%.

`level` e vizaton heightfield-in si `ground:terrain`, secilën pjesë të tij nga
nyja më e imët me lartësi aty dhe jo më e imët se `--ground-spacing` (4 m si
parazgjedhje: 3.7 milionë trekëndësha për nivelin e kontrolluar, nyjet më të imta të të cilit janë
0.5 m). Pjesët me rezolucion të ndryshëm takohen me hapa të vegjël; asgjë nuk i qep.

Copa e një nyjeje mban edhe faqet e maskave të shtresave pas faqes së lartësisë,
dhe copa e saj e dytë mbaron me hartën e ngjyrave të nyjes (shih
[Shtresat e terrenit](#terrain-layers)).

## Shtresat e terrenit {#terrain-layers}

Loja e hijëzon terrenin pranë një lojtari duke shtrirë materiale sipërfaqesh që përsëriten
sipas maskave të lyera, me një hartë ngjyrash sipër, dhe duke vizatuar decal-e (rrugë,
copa asfalti, shenja pistash) në krye. Përshkrimi i vetë Frostbite për sistemin
(Widmark, "Terrain in Battlefield 3", GDC 2012) i liston rasterat e terrenit si
heightfield, maskat e shtrirjes së shader-it, një hartë ngjyrash "e përdorur si mbivendosje mbi
shtrirjen e shader-it", materiale fizike, një maskë thellësie shkatërrimi, një hartë albedo
për dritën e kthyer dhe kanale shtesë maskash; pllakat e një rasteri mbajnë një
kufi për algoritmet e vizatimit. Pema e transmetimit e niveleve të kontrolluara
ka shtatë pemë raster, të tipuara 0, 1, 2, 4, 5, 7 dhe 8, kryet e të cilave fillojnë me
madhësinë e pllakës: 265 për heightfield-in (tipi 0) dhe tipin 2, 72 ose 66 për
maskat (tipi 1), 132 me një kufi 2 për hartën e ngjyrave (tipi 4), 260 me një
kufi 2 për tipin 5.

**Lista e shtresave.** Res-i `....layergraphs` i terrenit liston një hyrje 32 bajtëshe
për shtresë, sipas radhës që i numërojnë regjistrimet e maskave (34 hyrje, 34 seksione depoje
dhe indekse shtresash 0 deri 33 në një nivel); id-ja e secilës hyrje mbaron me
çelësin e seksionit në depon e blloqeve shader të grafit të shtresave
(`....layergraphs_shaderblockdepot`), blloku i së cilës emërton hartat e shtresës: një
hartë ngjyrash `_cv`, harta `_nhs` dhe `_ao` për sipërfaqe, plus harta të përbashkëta detaji dhe
zhurme. Shumë shtresa nuk emërtojnë asnjë hartë: janë burime që i lexon grafi i shtresave. Ngjyra e një shtrese është mesatarja e hartës së saj `_cv`; shkalla e përsëritjes nuk gjendet.
Aseti i terrenit mbaron me një hyrje pesë bajtëshe për shtresë (një bajt, pastaj një u32
indeks shtrese ose -1).

**Maskat.** Pema raster 1 është quadtree i maskave. Trupi i saj fillon me 59
bajte, ana e faqes te 0: 72 aty ku faqet janë BC4 (72 x 72, 2,592
bajte), 66 aty ku janë tetë-bitëshe të pakompresuara (4,356 bajte). Pastaj vjen një
grup për nyje, thellësi së pari:

| Pjesa | Struktura |
|---|---|
| group | u16; u16 numri i regjistrimeve; u32 numri i faqeve; regjistrimet; një bajt zero. Një grup pa regjistrime është 7 bajte gjithsej |
| record | 33 bajte: u16 shtresa, u16 hash, kutia e kuadrantit (katër float), dy bajte flamuri, një piramidë prania 85-bitëshe |

Regjistrimet e një grupi janë katër kuadrantet e nyjes së tij, shtresë pas shtrese, kuadrantet
e çdo shtrese në radhën (0, 0), (1, 0), (1, 1), (0, 1). Një regjistrim me
flamurin e dytë të vendosur e mbulon kuadrantin e tij tërësisht dhe nuk ka faqe; ai pa të ka
faqen tjetër; një kuadrant pa regjistrim të një shtrese që e emërton grupi i tij është bosh
nga ajo shtresë; flamuri i parë është i pastruar saktësisht kur shtresa vazhdon në
grupin e vetë kuadrantit, një nivel më poshtë, që e zëvendëson aty. Numri i faqeve
është numri i regjistrimeve me faqe.

Faqet: faqet e grupit të vetë nyjes së transmetimit vijnë në copën e saj pas
faqes së lartësisë, një seksion 16-bitësh 4,358 bajtësh dhe një raster tetë-bitësh 67 x 67 (nga
fillimi i copës kur nuk ka faqe lartësie); copa e saj e dytë mban
faqet e grupeve të katër kuadranteve të saj një nivel më poshtë, kuadrantet sipas radhës së
hartës së ngjyrave, pastaj hartën e ngjyrave. Një faqe është 64 x 64 teksetë e kuadrantit,
rreshta përgjatë z dhe kolona përgjatë x, me një kufi të kopjuar nga fqinjët: 4
teksele në një faqe BC4, 1 në një të pakompresuar.

Kufijtë e provojnë vendosjen pa gjykim: dy faqe të një shtrese anash njëra
tjetrës duhet të mbajnë tekselet e skajit të njëra-tjetrës. `read_masks` e kontrollon këtë për çdo
çift që vendos dhe refuzon një nivel ku më pak se 99% bien dakord. Rreth një
e treta e niveleve të kontrolluara lexohen, me kufijtë që bien dakord; disa nuk kanë
maska të lyera; pjesa tjetër refuzohen, pothuajse të gjitha nga kontrolli (copat e nyjeve të tyre
mbajnë më shumë se di kjo strukturë). Toka e një niveli të refuzuar
merr ngjyrën e mesit të materialeve të sipërfaqes së saj, dhe eksporti thotë pse.
Kufijtë përballë një kuadranti të plotë janë 255 dhe ato përballë një të zbrazëti 0.

Seksioni 4,358 bajtësh dhe rasteri 67 x 67 para faqeve nuk lexohen:
vlerat e tij qëndrojnë në një brez të ngushtë të lartë, pa vlera të vogla dhe pa sentinelë.

**Ngjyra e tokës.** Grafi i shtresave i përzien shtresat në një graf shader-i të
përpiluar me maska, pjerrësi, lartësi dhe zhurmë, i cili nuk lexohet. `--ground-texture`
e ngjyros tokën me një rregull të vetin, i thënë këtu si i tillë:

- shtresat hartat e ngjyrave të të cilave emërtohen për largësi janë zëvendësuesit e
  pamjes së largët dhe lihen jashtë;
- shtresat e teksturuara që mbulojnë nëntë të dhjetat e terrenit ose më shumë janë
  baza. Maskat e tyre janë të plota pothuajse kudo, ndaj ku shtrihet secila është
  zgjedhje e shader-it, jo e tyre: ato të emërtuara për shkëmb ose shkëmb të lartë ngjyrosin pjerrësi
  mbi 40 gradë, ato të emërtuara për zhavorr tokën e sheshtë (shtresat e tjera bazë
  kur nuk ka asnjë), të përzierat mes 20 dhe 40 gradë sipas
  pjerrësisë së heightfield-it (marrë çdo 4 m dhe shpërndarë në mënyrë bilineare mbi
  tekselet e pjekura: e përsëritur në blloqe 4 m e vizatonte ngjyrën shkëmbore si
  njolla me skaje të forta);
- çdo shtresë tjetër e teksturuar vendoset mbi bazë nga maska e vet, sipas radhës së
  shtresave;
- harta e ngjyrave vendoset mbi rezultatin siç e bën motori, dyfishi i
  ngjyrës së tokës herë atë të hartës, që gri e mesme e lë siç është; aty ku
  harta e ngjyrave nuk ka teksele toka merr shkëlqimin mesatar të hartës, në
  gri.

Kontrolluar kundrejt ngjyrës mediane të tokës së kuadrove të lojës së tre niveleve
(kroma si e kuqe dhe blu mbi jeshile): zona e lojës e pjekur del 1.00 / 0.69
kundrejt 1.19 / 0.78 të kuadrove në njërin, shtresat e barit të të cilit janë jeshile aty ku
kuadrot tregojnë bar të thatë, 1.19 / 0.82 kundrejt 1.01 / 1.04 në tjetrin, harta e ngjyrave e të cilit
është vetë e ngrohtë (1.13 / 0.88), dhe 1.05 / 0.91 kundrejt 0.93 / 0.92 në
një të tretin pa hartë ngjyrash. Kuadrot janë të ndriçuara dhe të gradeuara, ndaj
kjo mat tonin, jo shkëlqimin.

**Harta e ngjyrave.** Copa e dytë e një nyjeje mban, pas faqeve të maskave të
grupeve të kuadranteve të saj, katër faqe BC7 132 x 132 (17,424 bajte secila), një për
kuadrant të nyjes, sipas radhës (x e ulët, z e lartë), (x e lartë, z e lartë), (x e lartë,
z e ulët), (x e ulët, z e ulët). Pema e maskave thotë sa bajte zënë faqet e maskave,
ndaj harta e ngjyrave gjendet me numërim, jo nga fundi i copës: në një nivel
nyjet më të ashpra mbajnë katër faqe të tilla të tjera pas saj, një raster tjetër në një
ngjyrë të sheshtë, dhe leximi i katër faqeve të fundit të copës humbi hartën e ngjyrave mbi nëntë
të dhjetat e terrenit. Pa atë numërim harta e ngjyrave humbi edhe në
nivele me faqe maskash të pakompresuara, faqet e të cilave nuk janë një numër i plotë
faqesh BC4; harta e ngjyrave e një niveli shkoi nga 0.4 në 0.94 të terrenit të tij. Radha u përshtat: kundrejt skajeve të
heightfield-it të çdo kuadranti, çdo faqe e nyjeve me veçori përputhet me një
kuadrant, jo të përmbysur, në 0.3 deri 0.54 ku vendosja e dytë më e mirë është nën
0.2. Të qepura me të, faqet e një niveli bashkohen pa tegel në rrugët, ujin
dhe zonat e ndërtuara të nivelit të testit, në 0.5 m për teksel në zonën e lojës. Aty ku
shtresat bëjnë punën harta e ngjyrave është pothuajse neutrale (mediana 110, 107, 104);
gjetkë mund të mbajë ngjyrë të plotë. Një nivel kopat e dyta të të cilit mbajnë vetëm
faqe maskash të pakompresuara nuk ka hartë ngjyrash të lexuar. Një rund më i hershëm i këtij lexuesi
i quajti këto faqe jo-gjeografike: i krahasoi me hartën e sfondit,
që mund të jetë një peizazh krejt tjetër, dhe e vendosi çdo faqe mbi gjithë
nyjen e saj në vend të një kuadranti.

**Albedo e dritës së kthyer** u kërkua dhe nuk u gjet: copat e nyjeve rrënjë dhe
të nivelit të parë janë faqe maskash të plota, dhe ngarkesa e tipit 5 nuk
lokalizohet.

**Vrimat.** Aseti i terrenit të një niveli (tipi res `0x1CA38E06`) emërton tre shader-a:
një shader sipërfaqe parazgjedhje, një shader sipërfaqe vrimash dhe një shader burimi parazgjedhje.
Cilën shtresë e lexon shader-i i vrimave nuk gjendet, ndaj heightfield-i nuk pritet.
Në një nivel rrjeta e navigimit mund të shkojë mbi rrjeta shkëmbinjsh dhjetëra metra nën
heightfield, aty ku loja duhet ta ketë prerë. Të kërkuara dhe të pagjetura aty: maska e një shtrese, rasteri
67 x 67, një lartësi e rezervuar (asnjë faqe lartësie e nivelit nuk mban 0 ose
65,535) dhe një flamur nyjeje (çdo nyje nën rrënjë ka flamuj 1). Pemët raster
7 dhe 8 janë ç'mbetet. Të dyja janë të koduara me gjatësi vrapimi: një bajt i barabartë me atë
para tij ndiqet nga një numër kopjesh të tjera (`ff ff 84` është 134 bajte
255). Pema 7 (pllaka 256, quadtree i plotë me pesë nivele, katër bit për mostër)
dekodohet në çifte bajtesh me vlera 0 deri 3; pema 8 (pllaka 265) në bajte kryesisht 255,
me vlerat e tjera në vrapime të rregullta. Pllakat e asnjërës nuk janë vendosur ende, ndaj asnjëra nuk
dihet se mban vrimat.

**Decal-et** lexohen dhe piqen; shih [Decal-et e terrenit](#terrain-decals).

## Decal-et e terrenit {#terrain-decals}

Burimi: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Rrugë, pista aeroplanësh, platforma betoni, vija dhe shkronja të lyera, shenja gomash: res-i
`TerrainDecals` (tipi `0x15E1F32E`) i mban
si gjeometri të sheshtë që loja e mbështjell mbi terren.

| Pjesa | Struktura |
|---|---|
| header | te +16 një numër folesh n, pastaj n foletë 16 bajtëshe, pastaj numri i regjistrimeve |
| records | një për grup vizatimi, njëri pas tjetrit, me gjatësi të ndryshme: 156 bajte fushash fikse — kulmi i parë te +32, numri i trekëndëshave te +36, përsëritja e teksturës në metra te +44 — pastaj bajtet e kulmeve të grupit (zhvendosja, madhësia), pastaj një bishtalec që emërton teksturat e tij me GUID-et e ndarjeve të asetave të tyre |
| vertices | 32 bajte: x, z (f32), 8 bajte të paketuar, u, v (f32), r, g, b, a (f16); çdo grup një listë trekëndëshash e thjeshtë |
| indices | u32, duke numëruar nga 0 në çdo grup; nuk duhen |

Kontrolle:

- diapazonet e kulmeve të regjistrimeve ndjekin njëri-tjetrin pa boshllëk dhe i mbulojnë të gjitha
  kulmet saktësisht, dhe kulmi i parë × 32 i çdo regjistrimi është zhvendosja e tij;
- të lexuar kështu, trekëndëshat janë decal-e kompakte (shkronja, shirita vije, copa);
  të lexuar një kulm më tutje, janë shtylla të holla nëpër hartë;
- pothuajse të gjitha grupet emërtojnë tekstura në bishtalecin e tyre: një hartë ngjyrash (`_cv`) me
  një hartë opaciteti (`_op`, kanali i kuq), ose për shenja një maskë kanalesh (`_rgb`).

Pas GUID-eve të teksturave bishtaleci mban parametrat e materialit të grupit,
të koduar siç janë ato të një blloku shader-i (shih Tonet më poshtë). Ngjyra e bojës e një
shenje, një gjurme gome ose një vije është float3 i hash-uar `607e`: një 0.64,
0.56, 0.48 ranor për gjurmë gomash në rërë, pothuajse e zezë për katran. Hartat e opacitetit janë
kryesisht formati 62, një kanal me 8 bajte për bllok, të lexuara si BC4.

Një grup e hartëzon teksturën e tij ose sipas pozicionit botëror (u = x, v = z, teksturat
që përsëriten çdo tiling-metra: asfalt, beton, zhavorr) ose 0 në 1 përgjatë
decal-it (një vijë, një shkronjë, një gjurmë gome). Regjistrimet vizatohen sipas radhës së skedarit.

**Pjekja.** `level --ground-texture M` lyen, nën shtrirjen e decal-eve dhe
pllaka deri 4,096 pikselë, hartën e ngjyrave të sfondit (bilinear) dhe pastaj çdo
grup mbi të sipas opacitetit të tij × alfa e kulmeve. Ngjyra e kulmeve nuk
përdoret: kulmet e disa grupeve janë jeshile ose blu të pastra, çka i ngjyrosi shenjat e një niveli
me ato ngjyra. Trekëndëshat e heightfield-it aty bëhen
pjesë `ground:terrain x<x> z<z>` që mbajnë pllakën. Çdo grup vizatohet me:

| Grupi emërton | Vizatohet si |
|---|---|
| një hartë ngjyrash (`_cv`) | harta, sipas hartës së saj të opacitetit |
| një hartë shumëzimi (`_mult`) dhe një hartë opaciteti | boja (e bardhë aty ku materiali nuk emërton asnjë) herë harta e shumëzimit, sipas hartës së opacitetit: vija qendrore e konsumuar e një pista, vijat e skajeve dhe shiritat e pragut |
| një maskë kanalesh (`_rgb`) | boja, ndryshe e bardhë për vija e shkronja, e errët për kontura, një errësim i lehtë për konsumim, gjurmë gomash, njolla, pellgje dhe lagështi, sipas maskës |
| një hartë opaciteti vetëm, me bojë | boja sipas hartës së opacitetit: gjurmët e gomave |

Një maskë ndryshimi rruge nuk është bojë por ndryshon sipërfaqen poshtë saj, qindra
metra e gjerë, dhe nuk vizatohet, çfarëdo boje të ketë: e lyer e bardhë vendosi
dy drejtkëndësha të zbehtë 150 deri 250 m të gjatë në shpatet e një niveli. Harta `_mult`
merret si konsumimi i vetë bojës, jo si errësim i tokës poshtë saj:
është pothuajse e bardhë, dhe forma e vijës është në hartën e opacitetit.

Pothuajse çdo grup vizatohet, në pak pllaka në 0.5 m për piksel; eksporti
rritet me disa MB dhe zgjat disa sekonda më shumë. Parë nga lart,
platformat, rrugët e taksimit dhe rrjeti rrugor shtrihen nën gardhet dhe
ndërtesat e kompleksit dhe të çojnë te portat e tyre.

Të vizatuara si gjeometri më vete, decal-et do të kërkonin përzierje alfa, të cilën
shkruesi nuk e mban, dhe një zhvendosje mbi terren me të cilin do të luftonin
në thellësi (z-fight); pjekja i mban në ngjyrën e vetë tokës.

## Teksturat dhe materialet {#textures-and-materials}

Burimi: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Një res Texture (tipi `0x6BDE20BA`) është një krye 180 bajtëshe: tipi dhe formati i pikselit
te +8, gjerësia dhe lartësia te +22, numri i mip-eve te +30, GUID-i i copës te +40, pesëmbëdhjetë
madhësi mip-esh te +56. Copa është zinxhiri i mip-eve, më i madhi së pari. Disa copa nuk i kanë
mip-et e tyre më të mëdha, që vijnë në një paketë me rezolucion të lartë, dhe gjatësia e copës
thotë nga cili mip fillon. Copa e asaj pakete emërtohet te +164; lexohet
nga [suplementet](#which-table-is-the-level) e nivelit kur dëshirohet një mip që copa
kryesore nuk e ka, dhe gjatësia e saj plus ajo e copës kryesore është zinxhiri i plotë.

| Formati | Dekodohet si | Provë |
|---|---|---|
| 67, 66 | BC7 (sRGB, linear) | fleta e ngjyrave e një tanku plastik dekodohet si e tillë; si BC3 të njëjtat bajte janë zhurmë |
| 61, 60 | BC3 | fleta e një arke dekodohet pastër si BC3, jo si BC1 ose BC7 |
| 57, 56, 55 | BC1 | gjysmë bajti për piksel |

Aseti i rrjetës nuk emërton asnjë teksturë. Lidhja është në **depot e blloqeve shader**
të nivelit (tipi res `0x73312045`, një për nënbotë), me çelës tetë bajtet te
+0x130 të regjistrimit të seksionit të një rrjete:

| Pjesa | Struktura |
|---|---|
| table, te 16 | (çelësi i seksionit u64, zhvendosja e përshkruesit u64), derisa një zhvendosje bie jashtë res-it |
| descriptor | (zhvendosja e bllokut u64, hash u64, madhësia e bllokut u64) |
| block | parametrat shader të seksionit; çdo teksturë është një regjistrim 49 bajtësh: një bajt, 16 bajte, GUID-i i ndarjes së asetit të teksturës, GUID-i i instance-it të saj |

Çelësi i seksionit të arkës shfaqet një herë në secilën nga dhjetë depot e
nënbotëve që e vendosin, dhe blloku i saj emërton `t_mil_crate_03_cs` dhe `_nmt`
mes hartave të përbashkëta të detajit. Një bllok emërton çdo teksturë që mostron shader-i,
dhe cila është harta e ngjyrave nuk thuhet, ndaj zgjidhet: një teksturë 2D sRGB
emri i së cilës mban më shumë fjalë të emrit të materialit
(`M_ConcreteWall_01`: concrete, wall), pastaj të rrjetës, pastaj një që nuk është
hartë detaji, decal (`t_de_...`) ose dëmi, pastaj ajo që përdoret nga më pak blloqe. Blloku i një
tabele rruge emërton panelin e saj `t_com_highwaysignage_01_cs` dhe një fletë decal
`t_de_com_highwaysignage_01_ca` me një mburojë të shtrirë anash; të dyja përputhen me
fjalët, dhe pa rregullin e decal-it fletën e fitonte përdorimi dhe tabela shfaqte
mburojën të kthyer një çerek, përmes çdo seti koordinatash teksture që ka seksioni.
Fushat e largësisë së nënshkruar (`..._sdf`), paletat dhe maskat e kanaleve (`_rgb`)
nuk zgjidhen kurrë, çfarëdo fjalësh të ndajnë (hartat `_rgba` zgjidhen: shumica janë ngjyrë
me alfa, dhe lënia e tyre jashtë këmbeu hartat e vetë të një linje elektrike dhe të një shkalle
me të tjera të palidhura): atlasi i bimësisë së një sfondi
`..._atlas_a_sdf` i vizatuar si ngjyrë shfaqte yje bardh e zi për
pemë, paleta e ndërtesave e një sfondi një konfeti mostrash për mure, dhe mbeturinat
e xhamit të vizatuara përmes maskës së kanaleve dolën cian. Një seksion kandidatët e vetëm të të cilit
janë harta të përbashkëta detaji mbetet me ngjyrë të sheshtë.

**Paletat.** Ndërtesat e një sfondi i marrin ngjyrat nga një paletë, 256 x
256 teksele me mostra 16 x 16: çdo kulm mban katër bajte (përdorimi `0x1E`)
dy të parët e të cilëve thonë ku është ngjyra e tij në paletë, x dhe y nga 255.
`level` e vizaton një seksion të tillë me paletën si teksturë, çdo kulm në
qendër të mostrës së tij. Vizatuar kështu, blloqet e sfondit të një niveli dalin
me mure pastel, terrakotë dhe dritare të errëta aty ku ishin të bardha të thjeshta.

**Mbivendosjet.** Objektet e mëdha përsërisin një fletë trim përmes koordinatave të para
të teksturës dhe vendosin një mbivendosje mbi të përmes të dytave, që qëndrojnë brenda
0 deri 1: një shpalosje e gjithë objektit. Mbivendosja (`..._overlay_cs`, me
maskën e saj `..._overlay_a`) mban pamjen e objektit nga larg, shiritat e kuq
dhe ndryshkun e një tanku nafte; vizatuar vetëm me fletën trim, tankat e një
niveli dolën si panele gri. Një seksion blloku i të cilit emërton një mbivendosje me
maskën e saj, dhe koordinatat e dyta të të cilit janë një shpalosje e tillë, vizatohet me
mbivendosjen përmes tyre (36 seksione në atë nivel).

**Tonet.** Shumë harta ngjyrash janë gri (mesataret e kanaleve të tyre brenda 6% njëra
tjetrës): shader-i i lyen me ngjyra nga parametrat e bllokut. Pas
hyrjeve të teksturave (49 bajte secila) një bllok liston parametrat e tij, secili një etiketë
tipi (`f11af825` një float3, `a5e1f2de` një float4, `c1b1a014` një float,
`4a4fc3a1` një numër i plotë), bajtet e flamurit `01 80` për një vlerë, një hash dy bajtësh
i emrit të parametrit, një numër u32, vlera dhe një id tetë bajtëshe. Emrat
nuk ruhen. Shtatë hash-e emrash float3 veprojnë si tone: në një nivel
tri prej tyre mbajnë një ngjyrë në rreth 1 bllok nga 6 harta e të cilit është gri dhe pothuajse
kurrë aty ku harta ka ngjyrë të vetën, dhe të tjerat mbajnë ngjyrat me të cilat lyhet
një hartë gri aty ku e thotë emri i materialit (trim `..._blue` i një ure:
0.047, 0.098, 0.171 kundrejt një 0.5 neutrale). Një familje mund të mbajë
disa vlera, një për kanal të një maske, shumica neutrale, dhe një vlerë
me një kanal afër zeros (jeshile e pastër në fasadat me tulla) zgjedh një kanal
maske në vend që të lyejë. `level` e shumëzon një hartë ngjyrash gri, në dritë
lineare, me vlerën e parë të çdo familjeje që nuk është as neutrale as një zgjedhës i tillë,
mbi atë neutrale të saj, dhe e mban rezultatin si teksturë të vetë;
një hartë me ngjyrë lihet siç është. Rregulli është i vetë eksportuesit:
cili kanal i një maske merr cilin ton nuk lexohet. Në një nivel ai e uli
pjesën e trekëndëshave të strukturave të vizatuar pothuajse të bardhë nga 19.4% në 3.9%.

**Variacionet e objekteve.** Një rrjetë vendoset në disa pamje: një mur depoje
me vijë të kuqe ose blu dhe një numër tjetër të lyer mbi të, një
kontejner jeshil ose gri. Çdo kopje e vendosur emërton pamjen e saj:

| Ku | Fusha |
|---|---|
| anëtar i grupit të modeleve statike | +32: një varg me një tregues për kopje, te një variacion objekti ose null |
| referencë objekti | +120: një tregues te një variacion objekti ose null |
| variacion objekti (ndarja `ov_...`, tipi `235f2a9c...`) | instanca e tij e parë +32: hash-i u32 i emrit të variacionit |

Pamja e një seksioni në një variacion është blloku shader me çelës çelësin e vetë
seksionit me hash-in e variacionit të shtuar në katër bajtet e tij të parë, si një
u32 little-endian (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`);
një seksion pa bllok nën atë çelës duket njësoj në çdo variacion.
Bazat e të dhënave të variacioneve të rrjetave të nivelit (`meshvariationdb_win32`) listojnë, për rrjetë
dhe hash variacioni, materialet që prek çdo variacion, por jo çelësat:
rregulli u gjet nga vetë çelësat dhe vlen për çdo seksion me
variante të kontrolluar (katër variacionet e një muri, tri seksionet e tij secili).
Blloku i një variacioni sjell teksturat e veta si dhe tonet e veta:
numri i lyer mbi mur është një fletë shkronjash që e emërton blloku i variacionit.
Një pjesë e madhe e kopjeve të grupuara vendosen në një variacion.

Një bllok piqet një herë për çdo set përmbajtjesh, dhe hyrja e depos për një
çelës mban një hash të tyre (u64 e dytë e hyrjes). Aty ku një seksion nuk ka
bllok nën çelësin e variacionit të tij, variacioni prapë e arrin përmes një
*binjaku*: një seksion tjetër blloku parazgjedhje i të cilit ka të njëjtën përmbajtje
dhe ka një. Pa binjakë, një mur gjatësitë e të cilit ndajnë një bllok parazgjedhje mund të dalë me
dy ngjyra. Një seksion pa variantin e vet merr variantin që e kanë shumica e
binjakëve të tij.

**Rrjetat e shkatërrueshme.** Një rrjetë që një ndeshje mund ta rrëzojë ka një aset
shkatërrimi me emrin e vet pranë (`.../br_x.destruction` për
`.../br_x_mesh`): ndërtesat dhe muret e thyeshme (`br_`) dhe shumë objekte.
`level` i mban sipërfaqet e tyre në pjesë më vete, të emërtuara me
` (destructible)`, nyjet glTF të të cilave mbajnë `{"destructible": true}`. Gjendjet e tyre
të shkatërruara janë rrjetat `dc_..._part<N>_mesh` pranë tyre, secila
e përqendruar në origjinën e vet; ku qëndron një pjesë është në asetin e shkatërrimit,
i cili nuk lexohet, ndaj gjendjet e shkatërruara nuk eksportohen.

**Lënë jashtë.** Seksionet e materialeve zëvendësuese blockout (`M_Whitebox`: disa
trekëndësha të mëdhenj pa teksturë që disa ndërtesa i mbajnë pranë sipërfaqeve të tyre,
që dilnin nga një nivel si pendë të bardha), rrjetat e bëra për kinematika (një helikopter
i vendosur aty ku fillon skena e tij) dhe ndihmësit e ndriçimit (rrafshe që bllokojnë dritën,
të pavizatuara kurrë). Ndërtesat e gjeneruara të sfondit të një niveli
(`..._generated_blueprints_..._mesh`) vizatohen, por materiali i mureve të tyre
emërton vetëm harta zhurme dhe kulmet e tyre nuk mbajnë ngjyrë, ndaj mbeten të thjeshta. Pothuajse çdo
seksion i vizatuar merr një hartë ngjyrash.

**Fletët e shkronjave.** Numri i lyer i një muri ose printimi i billboard-it të një vinçi është
një seksion më vete harta e ngjyrave e të cilit është një fletë (`_ca`): alfa e një shkronje
mbi bojë të plotë, ose një printim. Koordinatat e para të teksturës e përsërisin
suvanë e murit nëpër panel (u -0.2 deri 1.7 në një mur), çka e vizaton fletën
gati dy herë; seti i katërt (`0x24`, ndryshe i treti, `0x23`) e vë saktësisht
një herë (u -1 deri 0, v 1 deri 2, disa të mijtat tejkalim në nivelet më të ashpra
të detajit). Aty ku seti i parë lë një kopje të imazhit dhe i katërti ose i treti qëndron brenda një, fleta vizatohet përmes tij, e zhvendosur në
0 deri 1. Një fletë me alfa vizatohet 1 cm para sipërfaqes ku është lyer, e
cila vizatohet nën të në hartën tjetër të ngjyrave të bllokut përmes setit
të parë: pa këtë, tekselet bosh të fletës shfaqnin brendinë e murit.
Seti i dytë është shpalosja e objektit për mbivendosjen e tij dhe nuk përdoret këtu.

**Hartat cut-out.** Kanali i katërt i hartës së ngjyrave do të thotë gjëra të ndryshme sipas
emrit të hartës. Në `_cs`, më e shpeshta (893 nga hartat e zgjedhura të një niveli),
është qetësia (smoothness): 1% e alfa-s së një harte mediane qëndron brenda 0.1 nga 0 ose 1.
Në `_cu` (gjethe, bar) dhe `_ca` (ngjyrë dhe alfa) është opacitet: 90% dhe
87%. Një hartë ngjyrash me emër `..._cu` ose `..._ca` alfa e së cilës është të paktën 75% afër
0 ose 1, të paktën 1% nën 0.5 dhe të paktën 5% mbi shkruhet me alfa-n e saj,
si PNG, dhe materiali i saj
si glTF `alphaMode` MASK, `alphaCutoff` 0.5, double-sided; kartat e gjetheve
shfaqin atëherë gjethe, jo qoshet e tyre të zeza. Harta e gjetheve e një peme nuk ka alfa
fare (4 nga 255 maksimumi): gjethet e saj priten nga gjeometria, dhe me vetëm dy
kushtet e para i gjithë kurora u pre.

Koordinatat e teksturës janë përdorimi i kulmit `0x21`, dy gjysma (formati 6) ose dy
float (formati 2). Seksionet mbajnë deri në tre sete të tjera (`0x22` deri `0x24`) për
shtresat decal dhe detaji. Koordinatat përsëriten: ana me brinjë e një kontejneri shkon
nga -1.6 në 1.8, pllakat e sfondit të terrenit qëndrojnë tërësisht jashtë 0..1, dhe në
një nivel 23% e trekëndëshave të teksturuar dalin jashtë 0..1. Shkruhen
siç janë, me një mostrues përsëritës; shikuesi 3DHeat e mbështjell çdo teksturë
përsëritëse brenda atlasit të tij. Një renderues që i kufizon në vend të kësaj i njollos brinjët
në dyfishin e gjerësisë së tyre, e kthen një dysheme betoni në vija përgjatë një boshti, dhe
u jep traversave të çelikut të një kulle ngjyrën e skajit të teksturës së tyre; për të,
`--clamped-uvs` e pret çdo trekëndësh përgjatë vijave ku teksturat e tij përsëriten
dhe e zhvendos çdo copë në 0..1 (shih [Formati i daljes](output-format.md)).
Pas kësaj 0.03% e trekëndëshave të teksturuar, mbi të cilët një teksturë përsëritet më shumë
se 16 herë, dalin jashtë, dhe një trekëndësh që prerja do ta bënte më shumë se
4 copa vizatohet në ngjyrën mesatare të teksturës së tij: lëvorja përsëritet
poshtë çdo dege, dhe e prerë, pemët e një niveli shkuan nga 6.4 në 24 milionë
trekëndësha.

Heightfield-i nuk ka hartë ngjyrash të vetën që mund të lexohet. Aty ku një nga hartat e
sfondit të terrenit e mbulon, ngjyroset nga ajo: koordinatat e teksturës së sfondit janë një funksion linear i
x dhe z botërore (99% e kulmeve të tij brenda 0.001 prej tij; harta
mbulon një katror 65,536 m, e kthyer një çerek), dhe i njëjti funksion jep
koordinatat e heightfield-it. Niveli e jep mip-et e asaj harte nga 2,048 px e poshtë,
ndaj heightfield-i merr 32 m për piksel. Shkëmbi i tij i errët shtrihet në tokën e pjerrët: korrelacioni i errësirës me pjerrësinë është 0.48, dhe më së shumti 0.34 për shtatë
orientimet e tjera.

Sfondi i një niveli tjetër është tetë pllaka afër dhe tetë larg rreth zonës së lojës,
secila duke përsëritur teksturën e vet nëpër pllakë, dhe asnjëra nuk arrin
heightfield-in. Çdo teksturë sfondi përshtatet më vete, dhe kur asnjëra nuk e mbulon
heightfield-in ai merr ngjyrën mesatare që shfaq sfondi brenda një
kilometri nga katrori i terrenit, mbi të cilën `--ground-texture` pjek decal-et.
Një material sfondi është ai emri i të cilit mban `TerrainBackdrop`, ose `BD_` dhe
`Terrain` (`M_BD_<site>_Terrain..._Near`); ose një rrjetë sfondi
(`bd_..._terrain<site>_04_far_mesh`) mban një material të thjeshtë terreni
(`M_<region>_Terrain<site>_04_Far`), të cilin dy rregullat e para e humbën në një
nivel dhe kështu e ngjyrosën tokën e tij nga sipërfaqet e veta.

Aty ku asnjë hartë sfondi nuk e mbulon heightfield-in, megjithatë, ai merr ngjyrën e
mesit të sipërfaqeve të vetë terrenit para mesatares së sfondit: hartat e ngjyrave `_cv`
që emërtojnë blloqet shader të grafit të shtresave të tij (27 në një nivel: rëra, zhavorre,
dhera, bar, beton i çarë), secila e mesatarizuar, pastaj mediana e secilit kanal,
duke lënë jashtë sipërfaqen parazgjedhje të motorit. Një sfond mund të jetë një
peizazh krejt tjetër: në një nivel mesatarja e tij (95, 99, 80 në sRGB)
e ktheu tokën e zonës së lojës në një gri që loja nuk e shfaq. Me `--ground-texture`, ajo ngjyrë
shumëzohet me dyfishin e hartës së ngjyrave, që gri e mesme e lë siç është, dhe piqet
me decal-et mbi shtrirjen e të dyve, decal-eve dhe hartës së ngjyrave.

Kundrejt lojës, ngjyra mediane e tokës së zonës së lojës së pjekur të çdo niveli
dhe e kuadrove të lojës (rreshtat 55 deri 72% të figurës pranë HUD, 24
kuadro secila; sRGB; kuadrot janë të ndriçuara dhe të gradeuara, ndaj raportet r/g dhe b/g janë
krahasimi i drejtë):

| Niveli | Kuadrot | Mesatarja e sfondit | Tani |
|---|---|---|---|
| i pari | 167, 140, 109 (1.19, 0.78) | 95, 99, 80 (0.96, 0.81) | 117, 108, 86 (1.08, 0.80) |
| i dyti | 72, 71, 74 (1.01, 1.04) | 117, 110, 104 (1.06, 0.95) | 146, 135, 117 (1.08, 0.87) |
| i treti | 83, 89, 82 (0.93, 0.92) | 160, 148, 136 (1.08, 0.92) | 148, 137, 117 (1.08, 0.85) |

I pari u ndreq; dy të tjerët ishin pak më afër në ton më parë. Një
ngjyrë për një nivel të tërë nuk mund të jetë e saktë kudo; maskat do të ishin.

## Rrjeta e navigimit {#navigation-mesh}

Burimi: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Një nivel jep një ndarje për agjent, `<level>/dbt/<level>_navmesh_layer_<n>`:
në një nivel shtresa 0 është ushtari (1.8 m i gjatë, hap 0.18 m, rreze 0.4 m) dhe
dy të tjerat janë automjete (3.5 dhe 10 m të gjata). Çdo ndarje mban dy vargje:

| Vargu | Elementi |
|---|---|
| tiles | 28 bajte: u32 0, u32 hash, u32 0, u32 indeksi i copës, u16 pllaka x, u16 pllaka z, u32 zhvendosja, u32 madhësia |
| chunks | 20 bajte: GUID i copës, u32 madhësia |

Një pllakë është `size` bajte te `offset` në copën `chunk index`, little-endian, dhe
e ngritur si ajo e Detour (Recast Navigation) pas një kryeje më të gjatë:

| Zhvendosja | Përmbajtja |
|---|---|
| 0 | `VAND`, versioni 7 |
| 24 | numëruesit: poligonet, kulmet, lidhjet, rrjetat e detajit, kulmet e detajit, trekëndëshat e detajit, nyjet e vëllimit kufizues, lidhjet off-mesh, poligoni i parë off-mesh |
| 188 | lartësia e agjentit, hapi, rrezja |
| 200 | kutia kufizuese e pllakës, gjashtë float |
| 232 | kulmet: x, y, z float, koordinata botërore |
| kufiri tjetër 8-bajtësh | poligonet, 32 bajte: u32, gjashtë indekse kulmesh u16, gjashtë fqinjë u16, flamuj u16, numri i kulmeve te +30, te +31 zona (gjashtë bitet e ulët) dhe lloji (dy të lartët) |
| pastaj, të paketuara | lidhjet (16 bajte), rrjetat e detajit (12: kulmi i parë i detajit u32, trekëndëshi i parë i detajit u32, numri i kulmeve dhe trekëndëshave u8), kulmet e detajit (tre float), trekëndëshat e detajit (tre indekse dhe flamuj), nyjet e vëllimit kufizues (16), lidhjet off-mesh (80) |

Në çdo pllakë të niveleve të kontrolluara këto mblidhen në madhësinë e pllakës deri
në bajt, dhe rrjetat e detajit numërojnë poligonet para të parit off-mesh.

Një poligon është i sheshtë mes qosheve të tij; **rrjeta e detajit** e tij mban
lartësinë e vërtetë të sipërfaqes mbi gunga, shkëmbinj dhe shkallë, dhe është ajo që
vizatohet. Indeksi i një trekëndëshi detaji nën numrin e qosheve të poligonit është ai kënd,
përndryshe kulmi i detajit `first + index - corners`. Hapja në erë e poligoneve
në vend të kësaj vë shumë më tepër trekëndësha nën terren dhe bën shtylla të gjata të holla;
me rrjetat e detajit asnjë nuk është më i gjatë se diagonalja e një pllake 16 m plus ngjitja
e një shpati.

Lloji 0 është tokë, lloji 2 copa të vogla të pjerrëta (rreth 45 gradë, një metër katror
secila), lloji 1 një lidhje mes sipërfaqesh: qoshet e saj përfshijnë 125 m lartësi ose më shumë
dhe qëndrojnë jashtë pllakës, disa në origjinë. Lidhjet lihen jashtë; pjesa tjetër
vizatohet nga rrjetat e detajit të tyre, ose hapet në erë në një pllakë pa to.

Kontrolle: madhësitë e copave mblidhen në ato të pllakave saktësisht; çdo kulm sipërfaqeje
qëndron brenda kutisë së pllakës së tij plus minus rreth një metër; pothuajse të gjithë trekëndëshat
shohin lart. Një pllakë që dështon
refuzohet dhe numërohet, dhe në atë nivel asnjë nuk dështon.

Çfarë mbulon rrjeta e ushtarit, parë nga lart në nivelin e testit: toka,
dyshemetë, shkallët dhe disa çati, dhe jo majat e kontejnerëve të mallrave. Është harta e AI-së për ku mund të qëndrojë një ushtar,
gjëja më e afërt që japin skedarët me ku qëndrojnë lojtarët.

## Çfarë nuk është implementuar {#not-implemented}

- Grafi i shtresave të terrenit, që përzien shtresat e sipërfaqes së tij (shih
  [Shtresat e terrenit](#terrain-layers)): ngjyra e tokës ndjek një rregull të
  vetë këtij lexuesi nga maskat e shtresave dhe pjerrësia e heightfield-it, dhe
  nivelet faqet e maskave të të cilëve nuk përshtaten marrin një ngjyrë.
- Parametrat e ngjyrave të materialeve decal: shenjat përmes maskave të kanaleve
  lyhen me një ngjyrë neutrale.
- Planet e objekteve që nuk janë rrjeta (logjika e lojës, efekte, tinguj).
- Gjendjet e shkatërruara të rrjetave të shkatërrueshme: vendet e pjesëve të tyre janë në
  asetin e shkatërrimit, i cili nuk lexohet.
- Lidhjet e rrjetës së navigimit (kërcime, shkallë, kapërcime) dhe shtresat e saj për automjete.
- Nivelet e rrjetave të ruajtura brenda res-it (10 rrjeta në një nivel, pajisje), kockat
  dhe pjesët e rrjetave me skelet dhe të përbëra, dhe normalet (llogariten nga shkruesi).
- Hartat normale, të vrazhdësisë dhe të tjera; alfa përveç një cut-out (xhami i tejdukshëm
  dhe decal-et vizatohen opake).
- Vrimat e terrenit: një shader sipërfaqe vrimash emërtohet, por ç'lexon nuk
  gjendet (shih [Shtresat e terrenit](#terrain-layers)), ndaj heightfield-i nuk pritet
  aty ku toka e kalueshme shkon nën të.
- Cili ton shkon me cilin kanal të maskës së një materiali: një hartë ngjyrash gri
  merr tonin e parë që nuk është neutral (shih
  [Teksturat dhe materialet](#textures-and-materials)).
- Efektet (shtigjet `fx/`) dhe rrjetat e kabllove, kutitë kufizuese të të cilave janë dhjetëra
  kilometra të gjata; lihen jashtë dhe numërohen në përmbledhje.
- Forma e tabelës e turbulluar me XOR.
