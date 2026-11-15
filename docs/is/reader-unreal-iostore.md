---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "is"
source: reader-unreal-iostore.md
source_hash: "a71af3169c83"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 sendir mest af efninu í **IoStore** ílátum: `.utoc` efnisskrá og
`.ucas` gögnin sem hún vísar í. `.pak` er enn til staðar, en það geymir
lítið meira en fót. Lesararnir hér fara frá ílátinu niður í
rúmfræði og dikla, eins langt og braut þarf. Þeir voru smíðaðir og prófaðir á
Assetto Corsa Rally (Unreal 5.6.1, breytt) og nást í gegnum
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html) brautarútflutninginn, og
`identify`, `list` og `extract` taka `.utoc` (eða `.ucas` við hlið hennar): skrárnar
sem mappa hennar nefnir, eftir slóð þeirra undir tengipunktinum. Ílát
án möppuvísis nefnir engar skrár og er ekki listað.

| Lag | Eining |
|---|---|
| ílát og safnið | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| bakaðir „zen“ pakkar | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| óútgefin eigindagögn | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| kyrrstæð net | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| áferðir og sýndaráferðir | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Ílát (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Efnisskráin, útgáfa 8 (Unreal 5.6), little-endian:

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

- Útgáfum eldri en 5 er hafnað. Aðeins útgáfa 8 hefur verið prófuð á raunverulegum
  skrám.
- **Dulkóðuðum ílátum er hafnað**: „<file> is encrypted. This tool holds no
  keys and recovers none.“ Ekki er hægt að gefa upp lykil fyrir IoStore.
- Blokkaaðferðir: geymt, `oodle` (í gegnum [Oodle](reader-oodle.md)), `zlib`,
  `lz4`. Öllu öðru er hafnað.
- Skiptingar umfram þá fyrstu búa í `<name>_s<n>.ucas`.

**Safnið** opnar hverja `.utoc` í `Paks` möppu leiksins og skráir hverja
pakkaslóð, án tillits til há- og lágstafa. Ílát sem opnast ekki eru sleppt.
`global.utoc` útvegar skriftuhlutina (C++ flokka). Magngögn pakka
(`.ubulk`) finnast sem bitinn með sama auðkenni og gerð `BULK_DATA`, í
hvaða íláti sem geymir hann.

Prófað: hvert ílát uppsetta leiksins og hver pakkaslóð í því.

## Zen pakkar {#zen-packages}

Bakaður pakki er haus (nöfn, innflutningar, útflutningar, útflutningsbúnt, ósjálfstæðistöflur,
nöfn innfluttra pakka) og á eftir honum raðað gagnasafn hvers útflutnings.
Hlutir vísa hver í annan með 64 bita `FPackageObjectIndex` þar sem efstu tveir bitarnir
segja hvað það er: útflutningur þessa pakka, skriftuhlutur, innflutningur úr
öðrum pakka (hvaða pakki, og útflutningurinn með tætigildi slóðar hans), eða núll.

- Samantektaruppröðunin breyttist í 5.3 (ósjálfstæðisbúnt og nöfn innfluttra
  pakka) og aftur í 5.6 (tvær hliðranir til viðbótar). Báðar uppraðanir eru reyndar, og sú
  þar sem nafnataflan þáttast er geymd, svo útgáfan þarf ekki að vera þekkt.
- **Útgáfumerktum** (eins og óbökuðum) pökkum er hafnað.
- Nöfn innfluttra pakka bera tölu. Pakki `_Terrain` með númerið 1 er
  skráin `_Terrain_0`.
- `/Game/...` nöfn varpast á `Content` möppu verkefnisins í safninu.
- Tilvísunum er fylgt milli pakka með því að para saman opinbert tætigildi útflutningsins.

Prófað: hver reitur hverrar sérleiðar opnast.

## Óútgefnar eigindir {#unversioned-properties}

Bakaðir Unreal 5 útflutningar nefna ekki eigindir sínar. Útflutningur byrjar á
haus af röðum, „slepptu svo mörgum raufum, síðan svo mörgum sem eru til staðar“, og grímu sem segir
hverjar af þeim sem eru til staðar eru núll og bera engin bæti. Gildin fylgja í röð
eigindalista flokksins. Til að lesa það þarf **skema** hvers flokks: eigindalista hans, í
nákvæmlega þeirri röð sem vélin smíðar hann (eigin eigindir fyrst, síðan foreldrisins,
ein rauf fyrir hvert stakstætt fylkisstak, eigindir sem eru aðeins í ritli sleppt).

Skemu eru innbyggð fyrir flokkana sem braut þarf:

| Flokkur | Keðja |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM keðjurnar (til staðar, en ekki notaðar af brautarútflutningnum, því þessi útgáfa endurraðaði þeim) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Þau ná líka yfir gagnabyggingarnar sem þessir halda (`FBodyInstance`, árekstrarsvör og
fleiri). Gildagerðir eru lesnar eftir kóðun: tölur og vigrar af fastri stærð
(`FVector`, `FRotator` sem tvöfaldar tölur, `FTransform`...), `FName`, upptalningar (eitt bæti),
hlutatilvísanir (`i32` pakkavísir), mjúkar hlutaslóðir, fylki, hreiðraðar
gagnabyggingar, og fjölvarpsfulltrúar (sleppt).

Skemun eru **aðeins eigindanöfn og gerðir**, leidd af Unreal
Engine 5.6.1 hausunum (sem Epic gerir aðgengilega hverjum sem hefur tengdan
reikning). Enginn kóði vélarinnar er innifalinn. Þessi útgáfa hefur **tvær raufar til viðbótar í
`UPrimitiveComponent`** miðað við hausana, og **eina til viðbótar í sýndaráferðar-
rúmmálinu**, fundnar út frá gögnunum og merktar `(unknown)`. Gildi í einni af
þeim raufum er villa, ekki ágiskun. Rauf handan enda skemu, eða
óþekkt gerð, kastar `PropertyError`.

Prófað: hver kyrrstæður netíhlutur og senuíhlutur hverrar sérleiðar afkóðast,
hver endar nákvæmlega við fastan innfæddan hala flokks síns. Leikjauppfærsla getur fært raufar.
Lesarinn kastar þá villu, og brautin segir hve marga íhluti brást.

## Kyrrstæð net {#static-meshes}

`UStaticMesh` útflutningur er eigindir hans og á eftir innfædd gögn. Eigindirnar
þarf ekki fyrir rúmfræði og þær eru ekki lesnar. Innfæddi hlutinn finnst á
föstu upphafi sínu: núll GUID fáni, tvö bæti af strip fánum, `bCooked = 1`, og
vísir á `BodySetup` útflutning netsins sjálfs. Hann er svo lesinn í þeirri röð sem
`UStaticMesh::Serialize` og `FStaticMeshRenderData::Serialize` skrifa hann fyrir
**bakað net án Nanite**:

- allt að 16 smáatriðastig, hvert með köflum sínum (efni, fyrsti vísir,
  þríhyrningafjöldi), mörkum, og þegar það er **innbyggt** (inlined): staðsetningabiðminnið (float32
  x 3), snertla, UV (allar rásir, hálf eða full nákvæmni), liti, og
  vísabiðminnið (16 eða 32 bita);
- það sem á eftir fylgir (umsnúin vísabiðminni og eingöngu dýpt, geislarekjunargögn,
  flatarmálsvegin sýnatökutæki) er stigið yfir til að ná næsta stigi.

Stig sem er ekki geymt innbyggt endar listann. Neti án neins er hafnað.
Staðsetningar eru Unreal: sentímetrar, X fram, Y til hægri, Z upp.

Prófað: nær öll sýnatökunet afkóðast (hin eru með beinagrind), og afkóðað umfang
vegarflísar passar við mörkin sem hún geymir.

## Áferðir {#textures}

`Texture2D` útflutningur er eigindir hans og svo bökuðu vettvangsgögn hans: heiti
dikilsniðsins, stærðin, og tafla af mip stigum, hvert vísandi í **magngagnakort**
pakkans (hliðrun, stærð, fánar; innbyggt í útflutningnum þegar fáni
`0x40` er settur, annars í `.ubulk`). Vettvangsgögnin finnast eftir eigin lögun,
ekki með því að sleppa eigindunum, svo eigindauppröðun áferðarflokksins skiptir
ekki máli. Fyrsta mip sem er ekki stærra en umbeðin stærð er afkóðað.

| Unreal snið | Afkóðað sem |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8 bita RGBA |
| `PF_G8` | 8 bita grátt |

Prófað: 4096 dikla DXT5 gervihnattamynd þar sem stigin þrettán eru nákvæmlega
stærðir magnfærslnanna.

## Streymandi sýndaráferðir {#streaming-virtual-textures}

Bökuð `VirtualTexture2D` eru ferningslaga flísar með jaðri, fyrir hvert smáatriðastig,
vistfangaðar með **Morton kóða** (x í sléttu bitunum), geymdar í bitum
magngagna pakkans. Uppröðunin er lesin eins og `FVirtualTextureBuiltData::Serialize`
skrifar hana í Unreal 5.6: lög, flísastærð, jaðar, vistfangatöflur flísa fyrir hvert mip,
snið laga, og biti *n* sem magnfærsla *n*. Svæði áferðarinnar er
sett saman flís fyrir flís, jaðrar fjarlægðir, frá því stigi þar sem upplausnin er
næst umbeðinni stærð. Aðeins fyrsta lagið er lesið, og aðeins á sniðunum
hér að ofan.

Prófað: flísar í bita sýndaráferðar standast upp á bæti.
