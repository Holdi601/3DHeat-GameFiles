---
title: Unreal 5 IoStore
nav_order: 2
lang: "sk"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 dodáva väčšinu obsahu v kontajneroch **IoStore**: tabuľka obsahu `.utoc`
a dáta `.ucas`, ktoré indexuje. `.pak` tam ešte je, ale obsahuje len o málo viac než
pätku. Čítačky tu idú od kontajnera až ku geometrii a pixelom, až dokedy to trať
potrebuje. Vytvorené a overené na Assetto Corsa Rally (Unreal 5.6.1, upravená verzia)
a dostanete sa k nim cez export trate [Assetto Corsa Rally](course-assetto-corsa-rally.md).
`identify`, `list` a `extract` berú `.utoc` (alebo `.ucas` vedľa neho): súbory, ktoré
jeho adresár pomenúva, podľa ich cesty pod bodom pripojenia. Kontajner bez indexu
adresárov nepomenúva súbory a nevypíše sa.

| Vrstva | Modul |
|---|---|
| kontajnery a úložný priestor | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| cooked balíky „zen“ | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| neverzované dáta vlastností | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statické siete | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| textúry a virtuálne textúry | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontajnery (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Tabuľka obsahu, verzia 8 (Unreal 5.6), little-endian:

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

- Verzie staršie než 5 sa odmietnu. Len verzia 8 bola overená na skutočných súboroch.
- **Šifrované kontajnery sa odmietnu**: „<file> is encrypted. This tool holds no
  keys and recovers none.“ Pre IoStore sa nedá zadať žiadny kľúč.
- Metódy blokov: uložené, `oodle` (cez [Oodle](reader-oodle.md)), `zlib`, `lz4`.
  Čokoľvek iné sa odmietne.
- Partície za prvou sú v `<name>_s<n>.ucas`.

**Úložný priestor** otvorí každý `.utoc` v priečinku `Paks` hry a indexuje každú cestu
balíka bez ohľadu na veľkosť písmen. Kontajnery, ktoré sa nedajú otvoriť, sa preskočia.
`global.utoc` dodáva skriptové objekty (triedy C++). Dátový blok balíka (`.ubulk`) sa
nájde ako chunk s rovnakým ID a typom `BULK_DATA`, v tom kontajneri, ktorý ho drží.

Overené: každý kontajner nainštalovanej hry a každá cesta balíka v ňom.

## Balíky zen {#zen-packages}

Cooked balík je hlavička (názvy, importy, exporty, zväzky exportov, tabuľky závislostí,
názvy importovaných balíkov), za ktorou nasleduje serializované dáta každého exportu.
Objekty na seba odkazujú 64-bitovým `FPackageObjectIndex`, ktorého horné dva bity
hovoria, čo to je: export tohto balíka, skriptový objekt, import z iného balíka (ktorý
balík a export podľa hashu jeho cesty), alebo null.

- Zhrnutie sa v 5.3 zmenilo (zväzky závislostí a názvy importovaných balíkov) a znova
  v 5.6 (dva ďalšie offsety). Vyskúšajú sa obe rozloženia a ponechá sa to, ktorého
  tabuľka názvov sa zparsuje, takže verzia sa nemusí poznať.
- **Verzované** (uncooked štýl) balíky sa odmietnu.
- Názvy importovaných balíkov nesú číslo. Balík `_Terrain` s číslom 1 je súbor
  `_Terrain_0`.
- Názvy `/Game/...` sa mapujú na priečinok projektu `Content` v úložnom priestore.
- Odkazy sa sledujú cez balíky zhodou verejného hashu exportu.

Overené: každá bunka každej etapy sa otvorí.

## Neverzované vlastnosti {#unversioned-properties}

Cooked exporty Unreal 5 nepomenúvajú svoje vlastnosti. Export začína hlavičkou behov:
„preskoč toľko slotov, potom toľko prítomných“, a maskou, ktorá hovorí, ktoré prítomné
sú nula a nenesú bajty. Hodnoty nasledujú v poradí vlastností triedy. Na čítanie je
treba **schému** každej triedy: jej zoznam vlastností presne v poradí, v akom ho engine
zostaví (vlastné vlastnosti ako prvé, potom vlastnosti rodiča, jeden slot na prvok
statického poľa, vlastnosti len pre editor vynechané).

Schémy sú zabudované pre triedy, ktoré trať potrebuje:

| Trieda | Reťaz |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | reťazce ISM (prítomné, ale export trate ich nepoužíva, lebo tento build ich preusporiadal) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Pokrývajú aj štruktúry, ktoré obsahujú (`FBodyInstance`, odozvy kolízií a ďalšie).
Typy hodnôt sa čítajú podľa kódovania: čísla a vektory pevnej veľkosti (`FVector`,
`FRotator` ako double, `FTransform`...), `FName`, enumy (jeden bajt), referencie na
objekty (`i32` index balíka), mäkké cesty objektov, polia, vnorené štruktúry
a multicast delegáty (preskočené).

Schémy obsahujú **len názvy a typy vlastností**, odvodené z hlavičiek Unreal Engine 5.6.1
(ktoré Epic sprístupňuje každému s prepojeným účtom). Nie je v nich žiadny kód enginu.
Tento build má **o dva sloty viac v `UPrimitiveComponent`** ako hlavičky a **o jeden
viac vo virtuálnom objeme textúry**, zistené z dát a označené `(unknown)`. Hodnota
prítomná v jednom z týchto slotov je chyba, nie odhad. Slot za koncom schémy alebo
neznámy typ vyvolá `PropertyError`.

Overené: každý komponent statickej siete a scény každej etapy sa dekóduje a každý
končí presne na pevnom natívnom konci svojej triedy. Záplata hry môže posunúť sloty.
Čítačka potom vyhodí chybu a trať nahlási, koľko komponentov zlyhalo.

## Statické siete {#static-meshes}

Export `UStaticMesh` je jeho vlastnosti nasledované natívnymi dátami. Vlastnosti sa na
geometriu nepotrebujú a nečítajú sa. Natívna časť sa nájde podľa svojho pevného
začiatku: nulový príznak GUID, dva bajty príznakov pásov, `bCooked = 1` a index
vlastného exportu `BodySetup` siete. Potom sa číta v poradí, v akom ho
`UStaticMesh::Serialize` a `FStaticMeshRenderData::Serialize` zapisujú pre **cooked,
nie-Nanite** sieť:

- až 16 úrovní detailu, každá so svojimi sekciami (materiál, prvý index, počet
  trojuholníkov), hranicami a keď je **vložená**: buffer pozícií (float32 x 3),
  tangenty, UV (všetky kanály, polovičná alebo plná presnosť), farby a buffer indexov
  (16- alebo 32-bitový);
- čo nasleduje (obrátené a hĺbkové buffery indexov, dáta ray-tracingu, vzorkovače
  podľa plochy) sa preskočí, aby sa dosiahla ďalšia úroveň.

Úroveň, ktorá nie je uložená vnútri, ukončí zoznam. Sieť bez ani jednej sa odmietne.
Pozície sú Unreal: centimetre, X dopredu, Y doprava, Z hore.

Overené: takmer každá vzorkovaná sieť sa dekóduje (zvyšok sú kostrové) a dekódovaný
rozmer dlaždice cesty sa zhoduje s hranicami, ktoré uchováva.

## Textúry {#textures}

Export `Texture2D` je jeho vlastnosti a potom jeho cooked dáta platformy: názov
pixelového formátu, veľkosť a tabuľka mipových úrovní, z ktorých každá ukazuje do
**mapy bulk dát** balíka (offset, veľkosť, príznaky; vnútri exportu, keď je nastavený
príznak `0x40`, inak v `.ubulk`). Dáta platformy sa nachádzajú podľa vlastného tvaru,
nie preskakovaním vlastností, takže rozloženie vlastností triedy textúry nezáleží. Dekóduje
sa prvý mip nie väčší než požadovaná veľkosť.

| Formát Unreal | Dekódované ako |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-bitové RGBA |
| `PF_G8` | 8-bitová šedá |

Overené: satelitný obrázok DXT5 4096 px, ktorého trinásť úrovní je presne veľkosťou
bulk položiek.

## Streamované virtuálne textúry {#streaming-virtual-textures}

Zapečený `VirtualTexture2D` je štvorcové dlaždice s okrajom, pre každú úroveň detailu,
adresované **Morton kódom** (x v párnych bitoch), uložené v chunkoch bulk dát balíka.
Rozloženie sa číta tak, ako ho zapisuje `FVirtualTextureBuiltData::Serialize` v Unreal
5.6: vrstvy, veľkosť dlaždice, okraj, tabuľky adries dlaždíc pre každý mip, formáty
vrstiev a chunk *n* ako bulk položka *n*. Oblasť textúry sa zloží dlaždica po dlaždici,
okraje sa odstránia, z úrovne, ktorej rozlíšenie je najbližšie požadovanej veľkosti.
Číta sa len prvá vrstva a len v formátoch vyššie.

Overené: dlaždice chunku virtuálnej textúry sa účtujú až na bajt.
