---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "bs"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 većinu sadržaja isporučuje u **IoStore** kontejnerima: tablica sadržaja
`.utoc` i podaci `.ucas` koje ona indeksira. `.pak` je i dalje tu, ali sadrži
tek nešto više od podnožja. Čitači ovdje idu od kontejnera do geometrije i
piksela, koliko staza treba. Izgrađeni su i provjereni na Assetto Corsa Rally
(Unreal 5.6.1, izmijenjen) i dostupni su kroz izvoz staze
[Assetto Corsa Rally](course-assetto-corsa-rally.md), a `identify`, `list` i
`extract` uzimaju `.utoc` (ili `.ucas` pored njega): datoteke koje njegov
direktorij imenuje, po njihovoj putanji ispod tačke montiranja. Kontejner bez
indeksa direktorija ne imenuje datoteke i ne navodi se.

| Sloj | Modul |
|---|---|
| kontejneri i pohrana | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| pečeni "zen" paketi | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| neverzionirani podaci svojstava | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statičke mreže | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| teksture i virtualne teksture | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontejneri (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Tablica sadržaja, verzija 8 (Unreal 5.6), little-endian:

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

- Verzije starije od 5 se odbijaju. Samo je verzija 8 provjerena na stvarnim
  datotekama.
- **Šifrirani kontejneri se odbijaju**: "<file> is encrypted. This tool holds no
  keys and recovers none." Za IoStore se ne može predati nikakav ključ.
- Metode blokova: pohranjeno, `oodle` (kroz [Oodle](reader-oodle.md)), `zlib`,
  `lz4`. Sve ostalo se odbija.
- Particije nakon prve žive u `<name>_s<n>.ucas`.

**Pohrana** otvara svaki `.utoc` u folderu `Paks` igre i indeksira svaku putanju
paketa, bez obzira na velika i mala slova. Kontejneri koji se ne otvore
preskaču se. `global.utoc` daje skriptne objekte (C++ klase). Bulk podaci paketa
(`.ubulk`) pronalaze se kao chunk s istim id-om i tipom `BULK_DATA`, u bilo kojem
kontejneru koji ga drži.

Provjereno: svaki kontejner instalirane igre i svaka putanja paketa u njemu.

## Zen paketi {#zen-packages}

Pečeni paket je zaglavlje (imena, importi, exporti, export bundlovi, tablice
zavisnosti, imena importiranih paketa) nakon kojeg slijede serijalizirani podaci
svakog exporta. Objekti se jedni na druge pozivaju 64-bitnim
`FPackageObjectIndex` čija gornja dva bita kažu šta je: export ovog paketa,
skriptni objekat, import iz drugog paketa (koji paket, i export po hashu njegove
putanje) ili null.

- Raspored sažetka promijenjen je u 5.3 (bundlovi zavisnosti i imena
  importiranih paketa) i ponovo u 5.6 (još dva pomaka). Oba rasporeda se
  isprobavaju, a zadržava se onaj čija se tablica imena parsira, pa verzija ne
  mora biti poznata.
- **Verzionirani** paketi (u stilu nepečenih) se odbijaju.
- Imena importiranih paketa nose broj. Paket `_Terrain` s brojem 1 je datoteka
  `_Terrain_0`.
- Imena `/Game/...` mapiraju se na folder `Content` projekta u pohrani.
- Reference se prate preko paketa podudaranjem javnog hasha exporta.

Provjereno: otvara se svaka ćelija svake etape.

## Neverzionirana svojstva {#unversioned-properties}

Pečeni Unreal 5 exporti ne imenuju svoja svojstva. Export počinje zaglavljem
nizova, "preskoči toliko slotova, zatim toliko prisutnih", i maskom koja kaže
koja prisutna su nula i ne nose bajte. Vrijednosti slijede redoslijedom
svojstava klase. Za čitanje je potrebna **shema** svake klase: njena lista
svojstava, tačno onim redoslijedom kojim je engine gradi (prvo vlastita svojstva,
zatim roditeljska, jedan slot po elementu statičkog niza, svojstva samo za editor
izostavljena).

Sheme su ugrađene za klase koje staza treba:

| Klasa | Lanac |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM lanci (prisutni, ali ih izvoz staze ne koristi, jer ih je ova verzija preuredila) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

One pokrivaju i strukture koje ove drže (`FBodyInstance`, odgovore kolizije i
druge). Tipovi vrijednosti čitaju se po kodiranju: brojevi i vektori fiksne
veličine (`FVector`, `FRotator` kao double, `FTransform`...), `FName`, enumi
(jedan bajt), reference na objekte (`i32` indeks paketa), meke putanje objekata,
nizovi, ugniježđene strukture i multicast delegati (preskaču se).

Sheme su **samo imena i tipovi svojstava**, izvedeni iz zaglavlja Unreal Engine
5.6.1 (koja Epic daje na raspolaganje svakome s povezanim računom). Nikakav kod
enginea nije uključen. Ova verzija ima **dva slota više u `UPrimitiveComponent`**
nego zaglavlja i **jedan više u volumenu virtualne teksture**, pronađene iz
podataka i označene `(unknown)`. Vrijednost prisutna u jednom od tih slotova je
greška, a ne nagađanje. Slot iza kraja sheme ili nepoznat tip izaziva
`PropertyError`.

Provjereno: dekodira se svaka komponenta statičke mreže i scene svake etape,
svaka završava tačno na fiksnom nativnom repu svoje klase. Zakrpa igre može
pomjeriti slotove. Čitač tada izaziva grešku, a `course` prijavljuje koliko
komponenti nije uspjelo.

## Statičke mreže {#static-meshes}

Export `UStaticMesh` su njegova svojstva nakon kojih slijede nativni podaci.
Svojstva nisu potrebna za geometriju i ne čitaju se. Nativni dio se pronalazi po
fiksnom početku: zastavica nultog GUID-a, dva bajta zastavica uklanjanja,
`bCooked = 1` i indeks exporta `BodySetup` same mreže. Zatim se čita redoslijedom
kojim ga pišu `UStaticMesh::Serialize` i `FStaticMeshRenderData::Serialize` za
**pečenu mrežu bez Nanite**:

- do 16 nivoa detalja, svaki sa svojim sekcijama (materijal, prvi indeks, broj
  trouglova), granicama, i kad je **ugrađen**: bafer pozicija (float32 x 3),
  tangente, UV-ovi (svi kanali, polovična ili puna preciznost), boje i bafer
  indeksa (16- ili 32-bitni);
- ono što slijedi (obrnuti i bafer indeksa samo za dubinu, podaci za ray tracing,
  uzorkivači ponderisani površinom) preskače se do sljedećeg nivoa.

Nivo koji nije pohranjen ugrađeno završava listu. Mreža bez ijednog se odbija.
Pozicije su Unrealove: centimetri, X naprijed, Y desno, Z gore.

Provjereno: gotovo svaka uzorkovana mreža se dekodira (ostale su skeletalne), a
dekodirani opseg pločice ceste podudara se s granicama koje pohranjuje.

## Teksture {#textures}

Export `Texture2D` su njegova svojstva, a zatim njegovi pečeni podaci platforme:
ime formata piksela, veličina i tablica mip nivoa, svaki koji pokazuje u **mapu
bulk podataka** paketa (pomak, veličina, zastavice; ugrađeno u export kad je
postavljena zastavica `0x40`, inače u `.ubulk`). Podaci platforme pronalaze se
po vlastitom obliku, a ne preskakanjem svojstava, pa raspored svojstava klase
teksture nije bitan. Dekodira se prvi mip koji nije veći od tražene veličine.

| Unreal format | Dekodira se kao |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bitni RGBA |
| `PF_G8` | 8-bitna siva |

Provjereno: DXT5 satelitska slika od 4096 px čijih je trinaest nivoa tačno
veličine unosa bulka.

## Streaming virtualne teksture {#streaming-virtual-textures}

Pečeni `VirtualTexture2D` su kvadratne pločice s okvirom, po nivou detalja,
adresirane **Mortonovim kodom** (x u parnim bitima), pohranjene u chunkovima
bulk podataka paketa. Raspored se čita onako kako ga piše
`FVirtualTextureBuiltData::Serialize` u Unreal 5.6: slojevi, veličina pločice,
okvir, tablice adresa pločica po mipu, formati slojeva i chunk *n* kao bulk
unos *n*. Područje teksture sastavlja se pločicu po pločicu, s uklonjenim
okvirima, iz nivoa čija je rezolucija najbliža željenoj veličini. Čita se samo
prvi sloj, i to samo u gore navedenim formatima.

Provjereno: pločice chunka virtualne teksture obračunate su do bajta.
