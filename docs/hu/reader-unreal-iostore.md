---
title: Unreal 5 IoStore
nav_order: 2
lang: "hu"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Az Unreal 5 a legtöbb tartalmát **IoStore** konténerekben szállítja: egy `.utoc` tartalomjegyzék és a
`.ucas` adat, amelyet indexel. A `.pak` is megvan, de alig több benne a lábléc. Az itteni olvasók a
konténertől a geometriáig és a képpontokig mennek, amennyire egy pályához szükséges. Az Assetto Corsa
Rally (Unreal 5.6.1, módosított) fájljain építettük és ellenőriztük őket, és az
[Assetto Corsa Rally](course-assetto-corsa-rally.md) pályaexport éri el őket, valamint az `identify`,
`list` és `extract` parancsok fogadnak `.utoc`-ot (vagy mellette lévő `.ucas`-t): a fájlokat, amelyeket
a könyvtára nevez meg, a csatolási pontja alatti útvonalukon. A könyvtárindex nélküli konténer nem nevez
meg fájlokat, ezért nem listázódik.

| Réteg | Modul |
|---|---|
| konténerek és a tároló | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| cookolt „zen" csomagok | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| nem verziózott tulajdonságadatok | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statikus hálók | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| textúrák és virtuális textúrák | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Konténerek (`.utoc`, `.ucas`) {#containers-utoc-ucas}

A tartalomjegyzék, 8-as verzió (Unreal 5.6), little-endian:

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

- Az ötnél régebbi verziók megtagadva. Csak a 8-as verziót ellenőriztük valódi fájlokon.
- **A titkosított konténerek megtagadva**: „<file> is encrypted. This tool holds no keys and recovers none."
  IoStore-hoz nem adható meg kulcs.
- Blokkmódszerek: tárolt, `oodle` (az [Oodle](reader-oodle.md)-on át), `zlib`, `lz4`. Minden más megtagadva.
- Az első utáni partíciók a `<name>_s<n>.ucas` fájlokban vannak.

A **tároló** megnyitja a játék `Paks` mappájának minden `.utoc`-ját, és minden csomagútvonalat indexel,
kis- és nagybetű-érzéketlenül. A meg nem nyíló konténereket kihagyja. A `global.utoc` adja a szkriptobjektumokat
(C++ osztályok). Egy csomag nagy adatát (`.ubulk`) az azonos azonosítójú és `BULK_DATA` típusú darab adja, abban
a konténerben, amelyben van.

Ellenőrizve: a telepített játék minden konténere és minden benne lévő csomagútvonal.

## Zen csomagok {#zen-packages}

Egy cookolt csomag fejlécből (nevek, importok, exportok, exportcsomagok, függőségi táblák, importált csomagnevek)
áll, amelyet minden export szerializált adata követ. Az objektumok egy 64 bites `FPackageObjectIndex`-en át
hivatkoznak egymásra, amelynek felső két bitje megmondja, mi: ennek a csomagnak egy exportja, egy szkriptobjektum,
egy import egy másik csomagból (melyik csomag, és az export az útvonala hash-e szerint), vagy null.

- Az összefoglaló elrendezése az 5.3-ban változott (függőségi csomagok és importált csomagnevek), majd az 5.6-ban
  (két további eltolás). Mindkét elrendezést megpróbáljuk, és azt tartjuk meg, amelynek a névtáblája feldolgozható,
  így a verziót nem kell előre ismerni.
- **A verziózott** (nem cookolt jellegű) csomagok megtagadva.
- Az importált csomagnevek számmal érkeznek. Egy `_Terrain` nevű, 1-es számú csomag a `_Terrain_0` fájl.
- A `/Game/...` nevek a projekt `Content` mappájára képződnek le a tárolóban.
- A hivatkozásokat csomagok között úgy követjük, hogy az exportok nyilvános hash-ét egyeztetjük.

Ellenőrizve: minden stage minden cellája megnyílik.

## Nem verziózott tulajdonságok {#unversioned-properties}

A cookolt Unreal 5 exportok nem nevezik meg a tulajdonságaikat. Egy export fejléce futásokból áll, „ugorj át ennyi
rekeszt, majd ennyi jelenlévőt", és egy maszkból, amely megmondja, mely jelenlévők nullák és nem hordoznak bájtokat.
Az értékek az osztály tulajdonsági sorrendjében követik. Ehhez minden osztály **sémája** kell: a tulajdonságlistája
pontosan abban a sorrendben, ahogy a motor felépíti (először a saját tulajdonságok, aztán a szülőé, egy rekesz
minden statikus tömbelemhez, a szerkesztői tulajdonságok nélkül).

A sémák be vannak ágyazva a pályához szükséges osztályokhoz:

| Osztály | Lánc |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | az ISM-láncok (megvannak, de a pályaexport nem használja, mert ez a build átrendezte őket) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Lefedik a bennük lévő struktúrákat is (`FBodyInstance`, ütközési válaszok és mások). Az értéktípusokat kódolás
szerint olvassuk: fix méretű számok és vektorok (`FVector`, `FRotator` dupla pontossággal, `FTransform`...), `FName`,
enumok (egy bájt), objektumhivatkozások (`i32` csomagindex), szoft objektumútvonalak, tömbök, egymásba ágyazott
struktúrák, és többszörös delegáltak (kihagyva).

A sémák **csak tulajdonságnevek és típusok**, az Unreal Engine 5.6.1 fejlécei alapján (amelyeket az Epic minden
összekapcsolt fiókkal rendelkezőnek elérhetővé tesz). Nincs bennük motorkód. Ez a build **két további rekesszel
rendelkezik a `UPrimitiveComponent`-ben** a fejlécekhez képest, és **eggyel a virtuális textúra-kötetben**, ezeket az
adatokból találtuk, és `(unknown)` jelöléssel látjuk el. Egy ilyen rekeszben lévő érték hiba, nem tipp. Egy séma
végén túli rekesz vagy ismeretlen típus `PropertyError`-t dob.

Ellenőrizve: minden stage minden statikus háló- és jelenetkomponense dekódolódik, mindegyik pontosan az osztálya
fix natív záróbájtjánál végződik. Egy játékfoltozás elmozdíthatja a rekeszeket. Az olvasó ekkor hibát dob, a pálya
pedig jelenti, hány komponens nem sikerült.

## Statikus hálók {#static-meshes}

Egy `UStaticMesh` export a tulajdonságai, majd a natív adat. A tulajdonságokra a geometriához nincs szükség, nem
olvassuk őket. A natív részt a fix kezdete alapján találjuk meg: egy nulla GUID-jelző, két bájt sávjelző, `bCooked = 1`,
és a háló saját `BodySetup` exportjának indexe. Ezután abban a sorrendben olvassuk, ahogy a
`UStaticMesh::Serialize` és az `FStaticMeshRenderData::Serialize` írja egy **cookolt, nem Nanite** hálóhoz:

- legfeljebb 16 részletességi szint, mindegyik a részeivel (anyag, első index, háromszögszám), határolókkal, és ha
  **beágyazott**: a pozíciópuffer (float32 x 3), tangensek, UV-k (minden csatorna, félpontos vagy teljes pontosságú),
  színek, és az indexpuffer (16 vagy 32 bites);
- ami követi (a fordított és mélységi indexpufferek, a sugárkövetési adatok, a területsúlyozott mintavevők) át van
  lépve, hogy elérjük a következő szintet.

Egy nem a fájlban beágyazott szint lezárja a listát. Egy háló, amelynek nincs ilyen szintje, megtagadva. A pozíciók
Unreal-féleek: centiméter, X előre, Y jobbra, Z fel.

Ellenőrizve: szinte minden mintavett háló dekódolódik (a többi csontozott), és egy úti csempe dekódolt kiterjedése
egyezik a tárolt határolóval.

## Textúrák {#textures}

Egy `Texture2D` export a tulajdonságai, majd a cookolt platformadatai: a pixelformátum neve, a méret, és egy mip-szintek
táblázata, amelyek mindegyike a csomag **bulk data térképére** mutat (eltolás, méret, jelzők; az exportban beágyazva, ha
a `0x40` jelző be van állítva, különben a `.ubulk`-ban). A platformadatokat a saját alakjuk alapján találjuk meg, nem a
tulajdonságok átugrásával, így a textúraosztály tulajdonságelrendezése nem számít. Az első mip, amely nem nagyobb a kért
méretnél, dekódolódik.

| Unreal-formátum | Dekódolva mint |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8 bites RGBA |
| `PF_G8` | 8 bites szürke |

Ellenőrizve: egy 4096 px-es DXT5 műholdkép, amelynek tizenhárom szintje pontosan megegyezik a bulk bejegyzések
méreteivel.

## Streamelt virtuális textúrák {#streaming-virtual-textures}

Egy sütött `VirtualTexture2D` szegéllyel ellátott négyzet alakú csempék, részletességi szintenként, Morton-kóddal
(x a páros biteken) címezve, a csomag bulk adatának darabjaiban tárolva. Az elrendezést úgy olvassuk, ahogy a
`FVirtualTextureBuiltData::Serialize` írja az Unreal 5.6-ban: rétegek, csempeméret, szegély, mipenkénti csempecímtáblák,
rétegformátumok, és a *n*-edik darab a *n*-edik bulk bejegyzés. A textúra egy részét csempénként állítjuk össze, a
szegélyeket eltávolítva, abból a szintből, amelynek felbontása a kért mérethez a legközelebb van. Csak az első réteget
olvassuk, és csak a fenti formátumokban.

Ellenőrizve: egy virtuális textúra-darab csempéi bájtra pontosan el vannak számolva.
