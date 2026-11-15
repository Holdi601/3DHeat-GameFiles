---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "sl"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 večino vsebine shranjuje v kontejnerjih **IoStore**: tabela vsebine `.utoc` in podatki `.ucas`, ki jih kaže. `.pak` je še vedno tu, vendar hrani malo več kot nogo. Bralniki tukaj gredo od kontejnerja do geometrije in slikovnih pik, kolikor jih proga potrebuje. Zgrajeni in preverjeni so bili na Assetto Corsa Rally (Unreal 5.6.1, prirejen), do njih pa pridemo prek izvoza proge [Assetto Corsa Rally](course-assetto-corsa-rally.md). `identify`, `list` in `extract` vzamejo `.utoc` (ali `.ucas` ob njem): datoteke, ki jih imenik imenuje, po njihovi poti pod točko montaže. Kontejner brez indeksa imenika ne imenuje datotek in ni izpisan.

| Plast | Modul |
|---|---|
| kontejnerji in shramba | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| prevedeni paketi "zen" | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| podatki o lastnostih brez različic | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statični meshi | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| teksture in virtualne teksture | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontejnerji (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Tabela vsebine, različica 8 (Unreal 5.6), little-endian:

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

- Različice, starejše od 5, so zavrnjene. Samo različica 8 je bila preverjena na pravih datotekah.
- **Šifrirani kontejnerji so zavrnjeni**: "<file> is encrypted. This tool holds no keys and recovers none." Za IoStore ni možnosti vnosa ključa.
- Metode blokov: shranjeno, `oodle` (prek [Oodle](reader-oodle.md)), `zlib`, `lz4`. Vse drugo je zavrnjeno.
- Particije za prvo so v `<name>_s<n>.ucas`.

**Shramba** odpre vsako `.utoc` v mapi `Paks` igre in indeksira vsako pot paketa, neodvisno od velikosti črk. Kontejnerji, ki se ne odprejo, se preskočijo. `global.utoc` daje skripte predmetov (razrede C++). Podatki `.ubulk` paketa se najdejo kot chunk z istim ID-jem in tipom `BULK_DATA`, v katerem koli kontejnerju je.

Preverjeno: vsak kontejner nameščene igre in vsaka pot paketa v njej.

## Paketi Zen {#zen-packages}

Prevedeni paket je glava (imena, uvozi, izvozi, paketi izvozov, tabele odvisnosti, uvoženi imeni paketov) in za njo serializirani podatki vsakega izvoza. Predmeti se sklicujejo drug na drugega s 64-bitnim `FPackageObjectIndex`, katerega zgornja dva bita povesta, kaj je: izvoz tega paketa, skriptni predmet, uvoz iz drugega paketa (kateri paket in izvoz po zgoščeni vrednosti njegove poti) ali nič.

- Postavitev povzetka se je spremenila v 5.3 (paketi odvisnosti in imena uvoženih paketov) in znova v 5.6 (dva nova odmika). Poskusijo se obe postavitvi, ohrani pa se tista, katere tabela imen se razčleni, zato različica ni treba biti znana.
- **Različični** (v slogu neprevedeni) paketi so zavrnjeni.
- Imena uvoženih paketov nosijo število. Paket `_Terrain` s številko 1 je datoteka `_Terrain_0`.
- Imena `/Game/...` se preslikajo na mapo `Content` projekta v shrambi.
- Reference se sledijo čez pakete z ujemanjem javne zgoščene vrednosti izvoza.

Preverjeno: vsaka celica vsake etape se odpre.

## Lastnosti brez različic {#unversioned-properties}

Prevedeni izvozi Unreal 5 ne imenujejo svojih lastnosti. Izvoz se začne z glavo nizov, "preskoči toliko mest, nato toliko prisotnih", in masko, ki pove, kateri prisotni so ničle in ne nosijo bajtov. Vrednosti sledijo po vrstnem redu lastnosti razreda. Za branje je potrebna **shema** vsakega razreda: njegov seznam lastnosti, v točno tistem vrstnem redu, kot ga gradi motor (najprej lastne lastnosti, nato lastnosti starša, eno mesto za vsak element statičnega polja, lastnosti samo za urejevalnik izpuščene).

Sheme so vgrajene za razrede, ki jih proga potrebuje:

| Razred | Veriga |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | verige ISM (prisotne, vendar jih izvoz proge ne uporablja, ker je ta gradnja preuredila) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Pokrivajo tudi strukture, ki jih držijo (`FBodyInstance`, odzivi trkov in drugi). Vrednosti tipov se berejo po kodiranju: števila fiksne velikosti in vektorji (`FVector`, `FRotator` kot double, `FTransform` ...), `FName`, nabori (en bajt), kazalci na predmete (`i32` indeks paketa), mehke poti predmetov, polja, ugnezdene strukture in večkratni delegati (preskočeni).

Sheme so **samo imena in tipi lastnosti**, izpeljani iz glav Unreal Engine 5.6.1 (ki jih Epic da na voljo vsakomur z registriranim računom). Ni vključena nobena koda motorja. Ta gradnja ima **dve dodatni reži v `UPrimitiveComponent`** glede na glave in **eno dodatno v volumnu virtualne teksture**, najdeni iz podatkov in označeni z `(unknown)`. Vrednost, prisotna v eni od teh rež, je napaka, ne ugibanje. Reža za koncem sheme ali neznan tip sproži `PropertyError`.

Preverjeno: vsaka statična komponenta mesha in scene vsake etape se dekodira, vsaka se konča natanko na svojem fiksnem nativnem repu. Popravek igre lahko premakne reže. Bralnik potem sproži napako, izvoz proge pa pove, koliko komponent je odpovedalo.

## Statični meshi {#static-meshes}

Izvoz `UStaticMesh` je njegove lastnosti, za njimi nativni podatki. Lastnosti niso potrebne za geometrijo in se ne berejo. Nativni del se najde po svojem fiksnem začetku: nično GUID zastavico, dva bajta zastavic trakov, `bCooked = 1` in indeks lastnega izvoza `BodySetup` mesha. Nato se prebere v vrstnem redu, v katerem ga za **prevedeni, ne-Nanite** mesh zapisujeta `UStaticMesh::Serialize` in `FStaticMeshRenderData::Serialize`:

- do 16 stopenj podrobnosti, vsaka s svojimi odseki (material, prvi indeks, število trikotnikov), mejami in kadar je **vgrajena**: medpomnilnik položajev (float32 x 3), tangente, UV (vsi kanali, polovična ali polna natančnost), barve in medpomnilnik indeksov (16- ali 32-bitni);
- kar sledi (obrnjeni in globinski medpomnilniki indeksov, podatki sledenja žarkov, vzorčevalniki po površini), se preskoči, da pridemo do naslednje stopnje.

Stopnja, ki ni vgrajena shranjena v vrstici, konča seznam. Mesh brez nobene je zavrnjen. Položaji so Unrealovi: centimetri, X naprej, Y desno, Z navzgor.

Preverjeno: skoraj vsak vzorčen mesh se dekodira (ostali so skeletni), razsežnost cestne ploščice pa se ujema z mejami, ki jih shrani.

## Teksture {#textures}

Izvoz `Texture2D` so njegove lastnosti in nato njegovi prevedeni podatki platforme: ime formata pikslov, velikost in tabela mipov nivojev, od katerih vsak kaže v **zemljevid podatkov v bulku** paketa (odmik, velikost, zastavice; vgrajen v izvozu, ko je bit `0x40` nastavljen, sicer v `.ubulk`). Podatki platforme se najdejo po lastni obliki, ne s preskakovanjem lastnosti, zato razporeditev lastnosti razreda teksture ni pomembna. Dekodira se prvi mip, ki ni večji od zahtevane velikosti.

| Format Unreal | Dekodiran kot |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bitni RGBA |
| `PF_G8` | 8-bitna siva |

Preverjeno: satelitska slika DXT5 4096 px, katere trinajst stopenj je natanko velikosti zbirnih vnosov.

## Tokovne virtualne teksture {#streaming-virtual-textures}

Zapečena `VirtualTexture2D` je kvadratne ploščice z obrobo, po stopnji podrobnosti, naslovljene z **Mortonovo kodo** (x v sodih bitih), shranjene v kosih podatkov v bulku paketa. Postavitev se bere, kot jo `FVirtualTextureBuiltData::Serialize` zapiše v Unreal 5.6: plasti, velikost ploščice, obroba, tabele naslovov ploščic za vsak mip, formati plasti in kos *n* kot zbirni vnos *n*. Območje teksture se sestavi ploščico za ploščico, z odstranjeno obrobo, iz stopnje, katere ločljivost je najbližja želeni velikosti. Prebrana je samo prva plast in samo v zgoraj navedenih formatih.

Preverjeno: ploščice kosa virtualne teksture so obračunane do bajta.
