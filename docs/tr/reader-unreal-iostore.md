---
title: Unreal 5 IoStore
nav_order: 2
lang: "tr"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5, içeriğin çoğunu **IoStore** konteynerlerinde dağıtır: bir `.utoc` içindekiler tablosu ve onun indekslediği `.ucas` verisi. Bir `.pak` hâlâ oradadır, ama neredeyse yalnızca bir altbilgi tutar. Buradaki okuyucular, bir parkurun ihtiyaç duyduğu kadarıyla konteynerden geometriye ve piksellere kadar gider. Assetto Corsa Rally (Unreal 5.6.1, değiştirilmiş) üzerinde yazılıp denetlendiler ve [Assetto Corsa Rally](course-assetto-corsa-rally.md) parkur dışa aktarımı üzerinden çağrılırlar. `identify`, `list` ve `extract` bir `.utoc`'u (ya da yanındaki `.ucas`'ı) alır: dizininin adlandırdığı dosyalar, bağlama noktası altındaki yollarıyla. Dizin indeksi olmayan bir konteyner hiçbir dosya adlandırmaz ve listelenmez.

| Katman | Modül |
|---|---|
| konteynerler ve depo | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| işlenmiş "zen" paketleri | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| sürümsüz özellik verisi | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statik mesh'ler | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| dokular ve sanal dokular | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Konteynerler (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Sürüm 8 (Unreal 5.6) içindekiler tablosu, küçük-endian:

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

- Sürüm 5'ten eski olanlar reddedilir. Gerçek dosyalarda yalnızca sürüm 8 denetlendi.
- **Şifreli konteynerler reddedilir**: "<file> is encrypted. This tool holds no keys and recovers none." IoStore için hiçbir anahtar verilemez.
- Blok yöntemleri: saklı, `oodle` ([Oodle](reader-oodle.md) üzerinden), `zlib`, `lz4`. Başka her şey reddedilir.
- İlk bölümden sonraki bölümler `<name>_s<n>.ucas` içinde yaşar.

**Depo**, oyunun `Paks` klasöründeki her `.utoc`'u açar ve her paket yolunu büyük/küçük harf duyarsız dizinler. Açılamayan konteynerler atlanır. `global.utoc`, betik nesnelerini (C++ sınıfları) sağlar. Bir paketin toplu verisi (`.ubulk`), aynı kimliğe ve `BULK_DATA` tipine sahip parça olarak bulunur; hangi konteynerde olursa olsun.

Denetim: oyunun her konteyneri ve her paket yolu.

## Zen paketleri {#zen-packages}

İşlenmiş bir paket, bir başlık (adlar, içe aktarımlar, dışa aktarımlar, dışa aktarım paketleri, bağımlılık tabloları, içe aktarılan paket adları) ve ardından her dışa aktarımın serileştirilmiş verisinden oluşur. Nesneler birbirine 64-bit bir `FPackageObjectIndex` ile başvurur; bunun en üstteki iki biti ne olduğunu söyler: bu paketin bir dışa aktarımı, bir betik nesnesi, başka bir paketten bir içe aktarım (hangi paket, ve dışa aktarım yolunun bir karmasıyla), ya da boş.

- Özet düzeni 5.3'te (bağımlılık paketleri ve içe aktarılan paket adları) ve 5.6'da (iki ofset daha) değişti. İki düzen de denenir ve adlar tablosu ayrışan tutulur; bu yüzden sürümün bilinmesi gerekmez.
- **Sürümlü** (düzenlenmemiş tarzda) paketler reddedilir.
- Numaralı içe aktarılan paket adları taşır. `1` numaralı `_Terrain` paketi `_Terrain_0` dosyasıdır.
- `/Game/...` adları, depodaki projenin `Content` klasörüne eşlenir.
- Başvurular paketler arasında, dışa aktarımın genel karmasının eşleştirilmesiyle izlenir.

Denetim: her etabın her hücresi açılır.

## Sürümsüz özellikler {#unversioned-properties}

İşlenmiş Unreal 5 dışa aktarımları özelliklerini adlandırmaz. Bir dışa aktarım, "şu kadar yuvayı atla, sonra şu kadar tanesi mevcut" çalışmalarından oluşan bir başlıkla başlar ve mevcut olanlardan hangilerinin sıfır olup bayt taşımadığını söyleyen bir maske. Değerler, sınıfın özellik sırasıyla izler. Bunu okumak, her sınıfın **şemasını** gerektirir: özellik listesini, motorun inşa ettiği tam sırada (önce kendi özellikleri, sonra ebeveynin, her statik dizi öğesi için bir yuva, yalnızca editörde olan özellikler dışarıda). 

Şemalar, bir parkurun ihtiyaç duyduğu sınıflar için gömülüdür:

| Sınıf | Zincir |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | ISM zincirleri (mevcut, ama parkur dışa aktarımı kullanmaz, çünkü bu sürüm bunları yeniden düzenledi) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Bunların taşıdığı yapıları da kapsarlar (`FBodyInstance`, çarpışma tepkileri ve diğerleri). Değer tipleri kodlamalarıyla okunur: sabit boyutlu sayılar ve vektörler (`FVector`, çift duyarlıklı `FRotator`, `FTransform`...), `FName`, enum'lar (bir bayt), nesne başvuruları (`i32` paket indeksi), yumuşak nesne yolları, diziler, iç içe yapılar ve çok yayınlı temsilciler (atlanır).

Şemalar **yalnızca özellik adları ve tipleridir**; Unreal Engine 5.6.1 başlıklarından türetilmiştir (Epic bunları bağlı bir hesabı olan herkese sunar). Hiçbir motor kodu dahil değildir. Bu sürümün `UPrimitiveComponent`'inde başlıklardan **iki fazla yuva** ve sanal doku hacminde **bir fazla** vardır; bunlar veriden bulunmuş ve `(unknown)` olarak işaretlenmiştir. Bu yuvalardan birinde bulunan bir değer bir hatadır, bir tahmin değil. Bir şemanın sonunun ötesindeki bir yuva ya da bilinmeyen bir tip, `PropertyError` fırlatır.

Denetim: her etabın her statik mesh ve sahne bileşeni çözülür, her biri sınıfının sabit yerel kuyruğunda tam olarak biter. Bir oyun yaması yuvaları kaydırabilir. Okuyucu o zaman hata verir ve parkur kaç bileşenin başarısız olduğunu bildirir.

## Statik mesh'ler {#static-meshes}

Bir `UStaticMesh` dışa aktarımı, özelliklerinin ardından yerel verisidir. Özellikler geometri için gerekmez ve okunmaz. Yerel kısım sabit başlangıcıyla bulunur: sıfır bir GUID bayrağı, iki bayt şerit bayrakları, `bCooked = 1` ve mesh'in kendi `BodySetup` dışa aktarımının indeksi. Sonra, **işlenmiş, Nanite olmayan** bir mesh için `UStaticMesh::Serialize` ve `FStaticMeshRenderData::Serialize`'ın yazdığı sırayla okunur:

- 16 düzeye kadar, her biri bölümleriyle (malzeme, ilk indeks, üçgen sayısı), sınırlarla ve **satır içi** olduğunda: konum tamponu (float32 x 3), tanjantlar, UV'ler (tüm kanallar, yarım ya da tam hassasiyet), renkler ve indeks tamponu (16 ya da 32 bit);
- bunların ardından gelen (ters ve yalnızca derinlik indeks tamponları, ışın izleme verisi, alan ağırlıklı örnekleyiciler) sonraki düzeye ulaşmak için atlanır.

Satır içi saklanmayan bir düzey listeyi bitirir. Hiçbiri olmayan bir mesh reddedilir. Konumlar Unreal'in koordinatlarıdır: santimetre, X ileri, Y sağ, Z yukarı.

Denetim: neredeyse örneklenen her mesh çözülür (kalanlar iskelettir), ve bir yol karosunun çözülen kapsamı, sakladığı sınırlarla eşleşir.

## Dokular {#textures}

Bir `Texture2D` dışa aktarımı, özellikleri ve ardından işlenmiş platform verisidir: piksel biçim adı, boyut ve paketin **toplu veri eşlemine** işaret eden mip düzeylerinin bir tablosu (ofset, boyut, bayraklar; bayrak `0x40` ayarlıysa dışa aktarımın içinde, aksi halde `.ubulk`'ta). Platform verisi kendi şekline göre bulunur, özellikleri atlayarak değil; bu yüzden doku sınıfının özellik düzeni önemli değildir. İstenen boyuttan büyük olmayan ilk mip çözülür.

| Unreal biçimi | Olarak çözülür |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8 bit RGBA |
| `PF_G8` | 8 bit gri |

Denetim: 4096 px'lik bir DXT5 uydu görüntüsü, on üç düzeyi toplu girdilerin boyutlarıyla tam olarak eşleşir.

## Akışlı sanal dokular {#streaming-virtual-textures}

Pişirilmiş bir `VirtualTexture2D`, düzey başına, bir kenarlığı olan kare karolardır; Morton kodu (x çift bitlerde) ile adreslenir ve paketin toplu verisinin parçalarında saklanır. Düzen, Unreal 5.6'da `FVirtualTextureBuiltData::Serialize`'ın yazdığı gibi okunur: katmanlar, karo boyutu, kenarlık, mip başına karo adres tabloları, katman biçimleri ve *n*. parça *n*. toplu girdi. Dokunun bir bölgesi, istenen boyuta en yakın çözünürlüğe sahip düzeyden, karo karo, kenarlıklar kaldırılarak birleştirilir. Yalnızca ilk katman okunur ve yalnızca yukarıdaki biçimlerde.

Denetim: bir sanal doku parçasının karoları bayta kadar hesaba katılır.
