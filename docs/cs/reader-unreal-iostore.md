---
title: Unreal 5 IoStore
nav_order: 2
lang: "cs"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 dodává většinu obsahu v kontejnerech **IoStore**: tabulka obsahu `.utoc` a
data `.ucas`, která indexuje. `.pak` tam pořád je, ale drží málo víc než patku.
Čtečky zde jdou od kontejneru dolů ke geometrii a pixelům, jen tak daleko, jak to
trať potřebuje. Byly postaveny a ověřeny na Assetto Corsa Rally (Unreal 5.6.1,
upravená verze) a volají se přes export tratě [Assetto Corsa Rally](course-assetto-corsa-rally.md).
`identify`, `list` a `extract` berou `.utoc` (nebo `.ucas` vedle něj): soubory, které
jeho adresář jmenuje, podle jejich cesty pod bodem připojení. Kontejner bez indexu
adresáře nejmenuje žádné soubory a neobjeví se ve výpisu.

| Vrstva | Modul |
|---|---|
| kontejnery a úložiště | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| zkompilované balíčky "zen" | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| neverzovaná data vlastností | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statické sítě | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| textury a virtuální textury | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Kontejnery (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Tabulka obsahu, verze 8 (Unreal 5.6), little-endian:

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

- Verze starší než 5 se odmítnou. Jen verze 8 byla ověřena na skutečných
  souborech.
- **Šifrované kontejnery se odmítnou**: "<file> is encrypted. This tool holds no
  keys and recovers none." Pro IoStore nelze předat žádný klíč.
- Metody bloků: uloženo, `oodle` (přes [Oodle](reader-oodle.md)), `zlib`, `lz4`.
  Cokoli jiného se odmítne.
- Oddíly za prvním žijí v `<name>_s<n>.ucas`.

**Úložiště** otevře každý `.utoc` ve složce `Paks` hry a indexuje každou cestu
balíčku bez ohledu na velikost písmen. Kontejnery, které se nepodaří otevřít, se
přeskočí. `global.utoc` poskytuje skriptové objekty (třídy C++). Hromadná data
balíčku (`.ubulk`) se najdou jako chunk se stejným ID a typem `BULK_DATA`, v
kterémkoli kontejneru, který ho drží.

Ověřeno: každý kontejner nainstalované hry a každá cesta balíčku v něm.

## Zen balíčky {#zen-packages}

Zkompilovaný balíček je hlavička (názvy, importy, exporty, svazky exportů, tabulky
závislostí, jména importovaných balíčků) následovaná serializovanými daty každého
exportu. Objekty na sebe odkazují 64bitovým `FPackageObjectIndex`, jehož dva nejvyšší
bity říkají, co je: export tohoto balíčku, skriptový objekt, import z jiného balíčku
(který balíček a export podle hashe jeho cesty), nebo null.

- Shrnutí se změnilo ve 5.3 (svazky závislostí a jména importovaných balíčků) a znovu
  ve 5.6 (dva další posuny). Zkoušejí se oba tvary a ponechá se ten, jehož tabulka
  názvů se naparsuje, takže verze se nemusí znát.
- **Verzované** (nezkompilované) balíčky se odmítnou.
- Jména importovaných balíčků nesou číslo. Balíček `_Terrain` s číslem 1 je soubor
  `_Terrain_0`.
- Názvy `/Game/...` se mapují na složku `Content` projektu v úložišti.
- Odkazy přes balíčky se sledují párováním veřejného hashe exportu.

Ověřeno: každá buňka každé etapy se otevře.

## Neverzované vlastnosti {#unversioned-properties}

Zkompilované exporty Unreal 5 nejmenují své vlastnosti. Export začíná hlavičkou
běhů "přeskoč tolik slotů, pak tolik přítomných", a maskou, která říká, které
přítomné jsou nulové a nenesou žádné bajty. Hodnoty následují v pořadí vlastností
třídy. Pro to je potřeba každé třídy **schéma**: její seznam vlastností, přesně v
pořadí, v jakém ho engine sestaví (vlastní vlastnosti nejdřív, potom rodičovské,
jeden slot na prvek statického pole, vlastnosti jen pro editor vynechané).

Schémata jsou vložená pro třídy, které trať potřebuje:

| Třída | Řetěz |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | řetězy ISM (přítomné, ale exportem tratě nepoužité, protože tento build je upravil) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Pokrývají také struktury, které tyto třídy drží (`FBodyInstance`, odezvy kolizí a
další). Hodnotové typy se čtou podle kódování: čísla a vektory pevné velikosti
(`FVector`, `FRotator` jako double, `FTransform`...), `FName`, výčty (jeden bajt),
odkazy na objekty (`i32` index balíčku), měkké cesty objektů, pole, vnořené
struktury a multicast delegáty (přeskočí se).

Schémata jsou **jen názvy vlastností a typy**, odvozené z hlaviček Unreal Engine
5.6.1 (které Epic zpřístupňuje každému s propojeným účtem). Nejsou v nich žádný kód
enginu. Tento build má **dva další sloty v `UPrimitiveComponent`** oproti hlavičkám
a **jeden další ve virtuálním objemu textury**, nalezené z dat a označené
`(unknown)`. Hodnota přítomná v jednom z těchto slotů je chyba, ne odhad. Slot za
koncem schématu nebo neznámý typ vyvolá `PropertyError`.

Ověřeno: každá statická a scénová komponenta každé etapy se dekóduje, přičemž každá
končí přesně na pevném nativním konci své třídy. Oprava hry může posunout sloty. Čtečka
pak vyvolá chybu a trať nahlásí, kolik komponent selhalo.

## Statické sítě {#static-meshes}

Export `UStaticMesh` je jeho vlastnosti následované nativními daty. Vlastnosti
k geometrii nejsou potřeba a nečtou se. Nativní část se najde podle svého pevného
začátku: nulový příznak GUID, dva bajty příznaků pásů, `bCooked = 1` a index vlastního
exportu `BodySetup` sítě. Pak se čte v pořadí, v jakém ho zapisují
`UStaticMesh::Serialize` a `FStaticMeshRenderData::Serialize` pro **zkompilovanou,
ne-Nanite** síť:

- až 16 úrovní detailu, každá se svými sekcemi (materiál, první index, počet
  trojúhelníků), hranicemi a, když je **vložená**: buffer pozic (float32 x 3),
  tangenty, UV (všechny kanály, poloviční nebo plná přesnost), barvy a buffer indexů
  (16- nebo 32bitový);
- co následuje (obrácené a hloubkové buffery indexů, data ray tracingu, samplery
  založené na ploše) se přeskočí, aby se došlo k další úrovni.

Úroveň, která není uložená vložené, ukončí seznam. Síť bez žádné se odmítne.
Pozice jsou Unreal: centimetry, X dopředu, Y doprava, Z nahoru.

Ověřeno: téměř každá vzorkovaná síť se dekóduje (zbytek jsou skeletální), a zjištěný
rozměr dlaždice silnice odpovídá hranicím, které uchovává.

## Textury {#textures}

Export `Texture2D` je jeho vlastnosti a potom jeho zkompilovaná data pro platformu:
název formátu pixelů, velikost a tabulka mipových úrovní, každá ukazuje do **mapy
hromadných dat** balíčku (posun, velikost, příznaky; vložená v exportu, když je
nastaven příznak `0x40`, jinak v `.ubulk`). Data platformy se najdou podle vlastního
tvaru, ne přeskakováním vlastností, takže rozložení vlastností třídy textury nevadí.
Dekóduje se první mip, který není větší než požadovaná velikost.

| Formát Unreal | Dekódováno jako |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8bitové RGBA |
| `PF_G8` | 8bitová šedá |

Ověřeno: satelitní snímek DXT5 4096 px, jehož třinácť úrovní je přesně velikostí
hromadných položek.

## Streamované virtuální textury {#streaming-virtual-textures}

Zapečený `VirtualTexture2D` tvoří čtvercové dlaždice s okrajem, pro každou úroveň
detailu, adresované **Mortonovým kódem** (x v sudých bitech), uložené v chuncích
hromadných dat balíčku. Rozložení se čte tak, jak ho zapisuje
`FVirtualTextureBuiltData::Serialize` v Unreal 5.6: vrstvy, velikost dlaždice, okraj,
tabulky adres dlaždic pro každý mip, formáty vrstev a chunk *n* jako položka hromadných
dat *n*. Oblast textury se skládá dlaždici po dlaždici, okraje se odstraní, z úrovně,
jejíž rozlišení je nejblíž požadované velikosti. Čte se jen první vrstva a jen ve výše
uvedených formátech.

Ověřeno: dlaždice chunku virtuální textury jsou přesně započítané až po bajt.
