---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "sq"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 e dërgon pjesën më të madhe të përmbajtjes në kontejnerë **IoStore**: një tabelë
përmbajtjeje `.utoc` dhe të dhënat `.ucas` që ajo indekson. Një `.pak` është ende aty, por mban
pak më shumë se një fund. Lexuesit këtu shkojnë nga kontejneri deri te
gjeometria dhe pikselat, aq sa i duhet një kursi. U ndërtuan dhe u kontrolluan në
Assetto Corsa Rally (Unreal 5.6.1, i modifikuar) dhe arrihen përmes eksportit të kursit
[Assetto Corsa Rally](course-assetto-corsa-rally.md), dhe
`identify`, `list` dhe `extract` marrin një `.utoc` (ose `.ucas` pranë tij): skedarët
që direktoria e tij emërton, sipas shtegut të tyre nën pikën e montimit. Një kontejner
pa indeks direktorie nuk emërton skedarë dhe nuk listohet.

| Shtresa | Moduli |
|---|---|
| kontejnerët dhe depoja | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| paketat e gatuara "zen" | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| të dhënat e vetive pa version | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| rrjetat statike | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| teksturat dhe teksturat virtuale | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontejnerët (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Tabela e përmbajtjes, versioni 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Versionet më të vjetra se 5 refuzohen. Vetëm versioni 8 është kontrolluar në skedarë
  të vërtetë.
- **Kontejnerët e enkriptuar refuzohen**: "<file> is encrypted. This tool holds no
  keys and recovers none." Asnjë çelës nuk mund të jepet për IoStore.
- Metodat e blloqeve: stored, `oodle` (përmes [Oodle](reader-oodle.md)), `zlib`,
  `lz4`. Çdo tjetër refuzohet.
- Ndarjet përtej të parës jetojnë në `<name>_s<n>.ucas`.

**Depoja** hap çdo `.utoc` në dosjen `Paks` të lojës dhe indekson çdo shteg
paketë, pa dallim shkronjash të mëdha e të vogla. Kontejnerët që nuk hapen anashkalohen.
`global.utoc` jep objektet e skriptit (klasat C++). Të dhënat bulk të një pakete
(`.ubulk`) gjenden si copa me të njëjtin id dhe lloj `BULK_DATA`, në
cilindo kontejner që e mban.

Kontrolluar: çdo kontejner i lojës së instaluar dhe çdo shteg paketë në të.

## Paketat zen {#zen-packages}

Një paketë e gatuar është një kokë (emra, import-e, eksporte, paketa eksportesh, tabela
varësish, emra paketash të importuara) e ndjekur nga të dhënat e serializuara të çdo eksporti.
Objektet i referojnë njëri-tjetrin me një `FPackageObjectIndex` 64-bit dy bitet e sipërme të të cilit
thonë çfarë është: një eksport i kësaj pakete, një objekt skripti, një import nga
një paketë tjetër (cila paketë, dhe eksporti me një hash të shtegut të tij), ose null.

- Struktura e përmbledhjes ndryshoi në 5.3 (paketat e varësive dhe emrat e
  paketave të importuara) dhe përsëri në 5.6 (dy ofsete të tjera). Provohen të dyja strukturat, dhe ajo
  tabela e emrave e së cilës parsohet mbahet, prandaj versioni nuk ka nevojë të dihet.
- Paketat **me version** (në stilin e pagatuarave) refuzohen.
- Emrat e paketave të importuara mbajnë një numër. Një paketë `_Terrain` me numër 1 është
  skedari `_Terrain_0`.
- Emrat `/Game/...` hartohen mbi dosjen `Content` të projektit në depo.
- Referencat ndiqen nëpër paketa duke përputhur hash-in publik të eksportit.

Kontrolluar: çdo qelizë e çdo etape hapet.

## Vetitë pa version {#unversioned-properties}

Eksportet e gatuara të Unreal 5 nuk i emërtojnë vetitë e tyre. Një eksport fillon me një
kokë ecurish, "kapërce kaq vende, pastaj kaq të pranishme", dhe një maskë që thotë
cilat të pranishme janë zero dhe nuk mbajnë bajte. Vlerat pasojnë në rendin e vetive të klasës.
Leximi i kësaj kërkon **skemën** e çdo klase: listën e vetive të saj, në
saktësisht rendin që e ndërton motori (vetitë e veta së pari, pastaj ato të prindit,
një vend për çdo element të vargut statik, vetitë vetëm-për-editor të lëna jashtë).

Skemat janë të ngulitura për klasat që i duhen një kursi:

| Klasa | Zinxhiri |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | zinxhirët ISM (të pranishëm, por të papërdorur nga eksporti i kursit, sepse ky ndërtim i riorganizoi) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Ato mbulojnë edhe strukturat që këta mbajnë (`FBodyInstance`, përgjigjet e përplasjes dhe
të tjera). Llojet e vlerave lexohen sipas kodimit: numra dhe vektorë me madhësi fikse
(`FVector`, `FRotator` si double, `FTransform`...), `FName`, enum (një bajt),
referenca objektesh (indeks paketë `i32`), shtigje objektesh të buta, vargje, struktura
të futura, dhe delegatë multicast (kapërcehen).

Skemat janë **vetëm emra dhe lloje vetish**, nxjerrë nga titujt e Unreal
Engine 5.6.1 (që Epic i vë në dispozicion të këdo me një llogari të lidhur). Nuk përfshihet kod
motori. Ky ndërtim ka **dy vende më shumë në `UPrimitiveComponent`** se titujt, dhe **një më shumë në
vëllimin e teksturës virtuale**, të gjetura nga të dhënat dhe të shënuara `(unknown)`. Një vlerë e pranishme në një prej
atyre vendeve është gabim, jo hamendësim. Një vend përtej fundit të një skeme, ose një lloj i panjohur,
ngre `PropertyError`.

Kontrolluar: çdo komponent rrjete statike dhe skene i çdo etape dekodohet,
secili duke mbaruar saktësisht në bishtin vendas fiks të klasës së vet. Një përditësim i lojës mund t'i lëvizë vendet.
Lexuesi atëherë ngre gabim, dhe kursi raporton sa komponentë dështuan.

## Rrjetat statike {#static-meshes}

Një eksport `UStaticMesh` janë vetitë e tij të ndjekura nga të dhëna vendase. Vetitë
nuk nevojiten për gjeometrinë dhe nuk lexohen. Pjesa vendase gjendet nga fillimi i saj fiks:
një flamur GUID zero, dy bajte flamujsh heqjeje, `bCooked = 1`, dhe indeksi i eksportit
`BodySetup` të vetë rrjetës. Pastaj lexohet në rendin që e shkruajnë `UStaticMesh::Serialize` dhe
`FStaticMeshRenderData::Serialize` për një rrjetë **të gatuar, jo-Nanite**:

- deri në 16 nivele detaji, secili me seksionet e veta (materiali, indeksi i parë,
  numri i trekëndëshave), kufijtë, dhe kur është **i brendshëm**: buferi i pozicioneve (float32
  x 3), tangjentet, UV-të (të gjitha kanalet, saktësi gjysmë ose e plotë), ngjyrat, dhe
  buferi i indekseve (16- ose 32-bit);
- çfarë pason (buferat e indekseve të kundërt dhe vetëm-thellësi, të dhënat e ray-tracing,
  mostruesit e peshuar sipas sipërfaqes) kapërcehet për të arritur nivelin tjetër.

Një nivel që nuk ruhet i brendshëm e mbyll listën. Një rrjetë pa asnjë refuzohet.
Pozicionet janë të Unreal: centimetra, X përpara, Y djathtas, Z lart.

Kontrolluar: pothuajse çdo rrjetë e mostruar dekodohet (të tjerat janë me skelet), dhe shtrirja e dekoduar e një
pllake rruge përputhet me kufijtë që ruan.

## Teksturat {#textures}

Një eksport `Texture2D` janë vetitë e tij dhe pastaj të dhënat e gatuara të platformës: emri
i formatit të pikselit, madhësia, dhe një tabelë nivelesh mip, secili duke treguar në
**hartën e të dhënave bulk** të paketës (ofseti, madhësia, flamujt; i brendshëm në eksport kur flamuri
`0x40` është vendosur, përndryshe në `.ubulk`). Të dhënat e platformës gjenden nga forma e tyre,
jo duke kapërcyer vetitë, prandaj struktura e vetive të klasës së teksturës
nuk ka rëndësi. Dekodohet mip-i i parë jo më i madh se madhësia e kërkuar.

| Formati Unreal | Dekodohet si |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA 8-bit |
| `PF_G8` | gri 8-bit |

Kontrolluar: një imazh satelitor DXT5 4096 px trembëdhjetë nivelet e të cilit janë saktësisht
madhësitë e hyrjeve bulk.

## Teksturat virtuale me transmetim {#streaming-virtual-textures}

Një `VirtualTexture2D` e pjekur janë pllaka katrore me kufi, për çdo nivel detaji,
të adresuara me **kod Morton** (x në bitet çift), të ruajtura në copa të të dhënave bulk
të paketës. Struktura lexohet siç e shkruan `FVirtualTextureBuiltData::Serialize`
në Unreal 5.6: shtresat, madhësia e pllakës, kufiri, tabelat e adresave të pllakave për çdo mip,
formatet e shtresave, dhe copa *n* si hyrja bulk *n*. Një zonë e teksturës
montohet pllakë pas pllake, me kufijtë e hequr, nga niveli rezolucioni i të cilit është
më afër madhësisë së dëshiruar. Lexohet vetëm shtresa e parë, dhe vetëm në format
e mësipërme.

Kontrolluar: pllakat e një copë teksture virtuale llogariten deri në bajt.
