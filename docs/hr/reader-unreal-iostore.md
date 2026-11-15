---
title: Unreal 5 IoStore
nav_order: 2
lang: "hr"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 isporučuje većinu sadržaja u **IoStore** spremnicima: tablicu sadržaja `.utoc` i
podatke `.ucas` koje ona indeksira. `.pak` je i dalje tu, ali sadrži malo više od podnožja.
Čitači ovdje idu od spremnika do geometrije i piksela, koliko staza treba. Izrađeni su i
provjereni na Assetto Corsa Rallyju (Unreal 5.6.1, izmijenjen) i do njih se dolazi kroz izvoz
staze [Assetto Corsa Rally](course-assetto-corsa-rally.md), a `identify`, `list` i `extract`
uzimaju `.utoc` (ili `.ucas` pored njega): datoteke koje njegov direktorij imenuje, po njihovoj
putanji pod točkom montiranja. Spremnik bez indeksa direktorija ne imenuje datoteke i ne
popisuje se.

| Sloj | Modul |
|---|---|
| spremnici i skladište | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| kompajlirani "zen" paketi | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| neverzionirani podaci o svojstvima | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statičke mreže | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| teksture i virtualne teksture | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Spremnici (`.utoc`, `.ucas`) {#containers-utoc-ucas}

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

- Verzije starije od 5 se odbijaju. Samo verzija 8 je provjerena na stvarnim datotekama.
- **Šifrirani spremnici se odbijaju**: "<file> is encrypted. This tool holds no keys and
  recovers none." Za IoStore se ne može predati nijedan ključ.
- Metode blokova: pohranjeno, `oodle` (kroz [Oodle](reader-oodle.md)), `zlib`, `lz4`. Svaka
  druga se odbija.
- Particije iza prve žive u `<name>_s<n>.ucas`.

**Skladište** otvara svaki `.utoc` u mapi `Paks` igre i indeksira svaku putanju paketa, bez
razlikovanja velikih i malih slova. Spremnici koji se ne mogu otvoriti preskaču se.
`global.utoc` daje objekte skripti (C++ klase). Bulk podaci paketa (`.ubulk`) nalaze se kao
dio s istim ID-jem i tipom `BULK_DATA`, u kojem god spremniku se nalazi.

Provjereno: svaki spremnik instalirane igre i svaka putanja paketa u njemu.

## Zen paketi {#zen-packages}

Kompajlirani paket je zaglavlje (imena, uvoz, izvoz, paketi izvoza, tablice ovisnosti,
imena uvezenih paketa), a iza njega podaci serijalizirani za svaki izvoz. Objekti se referiraju
jedan na drugi 64-bitnim `FPackageObjectIndex`-om čija dva najviša bita govore što je: izvoz ovog
paketa, objekt skripte, uvoz iz drugog paketa (koji paket, i izvoz po hashu njegove putanje), ili
null.

- Raspored sažetka promijenio se u 5.3 (paketi ovisnosti i imena uvezenih paketa) i opet u 5.6
  (dva pomaka više). Probaju se oba rasporeda, a zadržava se onaj čija se tablica imena parsira,
  pa verziju ne treba unaprijed znati.
- **Verzionirani** (paketi u stilu neobrađenih) se odbijaju.
- Imena uvezenih paketa nose broj. Paket `_Terrain` s brojem 1 je datoteka `_Terrain_0`.
- Imena `/Game/...` preslikavaju se na mapu `Content` projekta u skladištu.
- Reference se prate preko paketa podudaranjem javnog hasha izvoza.

Provjereno: svaka ćelija svake etape se otvara.

## Neverzionirana svojstva {#unversioned-properties}

Pečeni Unreal 5 izvozi ne imenuju svoja svojstva. Izvoz počinje zaglavljem serija, "preskoči toliko
mjesta, zatim toliko prisutnih", i maskom koja kaže koja prisutna mjesta su nula i ne nose bajtove.
Vrijednosti slijede redoslijedom svojstava klase. Za čitanje je potrebna **shema** svake klase:
njezin popis svojstava, točno redom kojim ga motor gradi (vlastita svojstva prvo, pa roditeljeva,
jedno mjesto po elementu statičkog niza, uređivačka svojstva izostavljena).

Sheme su ugrađene za klase koje izvozu staze trebaju:

| Klasa | Lanac |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | lanci ISM-a (prisutni, ali izvoz staze ih ne koristi, jer je ova verzija to preuredila) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Pokrivaju i strukture koje drže (`FBodyInstance`, odgovori sudara i ostale). Vrijednosti tipova
čitaju se po kodiranju: brojevi fiksne veličine i vektori (`FVector`, `FRotator` kao double,
`FTransform`...), `FName`, enumi (jedan bajt), reference na objekte (`i32` indeks paketa), meke
putanje objekata, nizovi, ugniježđene strukture i višestruki delegati (preskočeni).

Sheme su **samo imena i tipovi svojstava**, izvedeni iz zaglavlja Unreal Enginea 5.6.1 (koja Epic
stavlja na raspolaganje svakome s povezanim računom). Nema koda motora. Ova verzija ima **dva
dodatna mjesta u `UPrimitiveComponent`** u odnosu na zaglavlja i **jedno dodatno u volumenu
virtualne teksture**, pronađena iz podataka i označena kao `(unknown)`. Vrijednost prisutna u
jednom od tih mjesta je greška, a ne pretpostavka. Mjesto iza kraja sheme ili nepoznat tip
podiže `PropertyError`.

Provjereno: svaka statička mreža i komponenta scene svake etape se dekodira, svaka završava točno
na nativnom repu svoje klase. Zakrpa igre može pomaknuti mjesta. Čitač tada podiže grešku, a
staza prijavljuje koliko je komponenti otkazalo.

## Statičke mreže {#static-meshes}

Izvoz `UStaticMesh` je njegova svojstva, a zatim nativni podaci. Svojstva nisu potrebna za
geometriju i ne čitaju se. Nativni dio se nalazi po fiksnom početku: nulta GUID zastavica, dva
bajta zastavica traka, `bCooked = 1` i indeks vlastitog `BodySetup` izvoza mreže. Zatim se čita
redoslijedom kojim ga `UStaticMesh::Serialize` i `FStaticMeshRenderData::Serialize` pišu za
**pečenu, ne-Nanite** mrežu:

- do 16 razina detalja, svaka sa svojim podmrežama (materijal, prvi indeks, broj trokuta),
  granicama i, kad je **inlineano**: međuspremnik pozicija (float32 x 3), tangente, UV-ovi (svi
  kanali, polu ili puna preciznost), boje i međuspremnik indeksa (16 ili 32 bita);
- što slijedi (obrnuti i dubinski međuspremnici indeksa, podaci za ray tracing, uzorkivači
  s težinom površine) preskače se da se dođe do sljedeće razine.

Razina koja nije spremljena unutra završava popis. Mreža bez ijedne se odbija. Pozicije su
Unrealove: centimetri, X naprijed, Y desno, Z gore.

Provjereno: gotovo svaka uzorkovana mreža se dekodira (ostale su skeletne), a dekodirani
obuhvat pločice ceste odgovara granicama koje ona sprema.

## Teksture {#textures}

Izvoz `Texture2D` su njegova svojstva, a zatim njegovi pečeni podaci platforme: naziv formata
piksela, veličina i tablica mip razina, od kojih svaka pokazuje u **mapu bulk podataka** paketa
(pomak, veličina, zastavice; unutar izvoza kad je postavljena zastavica `0x40`, inače u
`.ubulk`). Podaci platforme nalaze se po vlastitom obliku, a ne preskakanjem svojstava, pa raspored
svojstava klase teksture nije važan. Prvi mip koji nije veći od tražene veličine se dekodira.

| Unreal format | Dekodira se kao |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bitni RGBA |
| `PF_G8` | 8-bitni sivi |

Provjereno: satelitska slika DXT5 od 4096 px čijih trinaest razina točno odgovara veličinama
bulk unosa.

## Streaming virtualne teksture {#streaming-virtual-textures}

Pečena `VirtualTexture2D` su kvadratne pločice s rubom, po razini detalja, adresirane **Mortonovim
kodom** (x u parnim bitovima), spremljene u dijelovima bulk podataka paketa. Raspored se čita kao
što ga `FVirtualTextureBuiltData::Serialize` piše u Unreal 5.6: slojevi, veličina pločice, rub,
tablice adresa pločica po mipu, formati slojeva, i dio *n* kao bulk unos *n*. Područje teksture
sastavlja se pločica po pločica, uz uklonjene rubove, s razine čija je rezolucija najbliža
traženoj veličini. Čita se samo prvi sloj, i to samo u formatima iznad.

Provjereno: pločice jednog dijela virtualne teksture obračunate su do bajta.
