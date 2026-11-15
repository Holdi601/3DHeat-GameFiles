---
title: ForzaTech
nav_order: 7
lang: "tr"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, numuneler, yerleşimler {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon, Turn 10'un kendi motoru olan ForzaTech üzerinde çalışır. Bu okuyucular bir parkuru arşivlerinden alıp konumlandırılmış, dokulanmış üçgenlere kadar götürür. Bunlara `course`, `courses` ve `terrain` üzerinden ulaşılır (bkz. [Forza Horizon](course-forza-horizon.md)). `identify` bir `.minizip`'i ve tek başına bir `.modelbin`'i tanır; `list` ve `extract` bir `.minizip`'i, yanındaki `ChunkContentsMiniZip<n>.txt` içindeki adlarla ya da girdi numarasıyla (`#12`) alır.

| Biçim | Modül |
|---|---|
| `.minizip` arşivleri ve ad listeleri | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin` modelleri ve arazi | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb` doku numuneleri | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo` yerleşim dosyaları | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` ve malzeme doku hash'leri | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| yere göre arazi karoları | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza içeriğinin bir kısmını `media\` altındaki sıradan ZIP arşivlerinde de tutar. Python'un `zipfile` modülü bunları açar ve `forzatech.models_in_archive()` onların `.modelbin` girdilerini listeler. Parkur geometrisi `.minizip` arşivlerindedir.

## `.minizip`: adsız bir arşiv {#minizip-an-archive-with-no-names}

Bir parkur dört `GeoChunk<n>.minizip` arşivi gönderir; açık dünya bir harita için her biri onlarca gigabayt, yüz binlerce girdiyle. **Arşivler hiçbir ad saklamaz**: ad tablosu yok, girdi başına başlık yok, yalnızca bir sıra numarası. Adlar, her arşivin yanındaki `ChunkContentsMiniZip<n>.txt` dosyasındadır; girdi sırasına göre her satırda bir (`<build path>zipcache\pc\<path>|<bundle>`). Bir dosyayı istemenin tek yolu bu eşleşmedir. `zipcache\pc\` öncesindeki her şey atılır ve aramalar büyük/küçük harf duyarsızdır.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Dizinde yanlış okunduğunda yine de çıktı üreten üç ayrıntı vardır. Okuyucu üçünü de doğru yapar:

| Ayrıntı | Dikkatsiz bir okuyucunun yaptığı | Nasıl görünür |
|---|---|---|
| segment tabanı **64-bit** | u32 artı dolgu olarak okur | ilk 4 GB için doğrudur, sonra doğru uzunlukta gürültü |
| taban **8 bayta hizalı** | paket tablosundan sonraki dolgu sözcüğünü yok sayar | çift paket sayılı arşivlerde her girdi, var olmayan bir kodeği iddia eder |
| bir girdinin saklı uzunluğu, sonraki girdiye (ya da sonraki segmentin tabanına) olan boşluk **eksi dolgusu** (bayrak bitleri 12-13) | tüm boşluğu kullanır | LZ4 bloğu tamamen reddeder |

Kodekler, bayrakların düşük beş biti: `0x00` saklı, `0x08` ham deflate, `0x1F` LZ4 bloğu. Başka her şey reddedilir. Her girdi, bildirdiği boyuta tam olarak açılmalıdır, yoksa reddedilir. Dizin (yaklaşık 5 MB) bir kez okunur ve yükler, konum aranarak okunur.

Başlık denetlenir: sihirli sayı, 32 baytlık bir başlık ve `ceil(entries / per segment)` ile eşleşen bir segment sayısı.

**Doğrulandı:** bir haritanın her arşivinde örneklenen girdiler, üç kodekle de bildirdikleri uzunluğa tam olarak açılır.

## `.modelbin`: parça konteyneri {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Bildirilen dosya boyutu gerçek boyuta eşit olmalıdır.
- **Zincir**: her parça, önceki parçanın bittiği yerden başlar ve 4 bayta yuvarlanır. Dosyada bunu söyleyen hiçbir şey yoktur, bu yüzden bir kanıttır: yanlış adımla okunan bir kayıt bunu üretmez. Örneklenen 252 modelin tamamında tuttu.
- Modele verilen bir `PGZP` dosyası, reddedilmek yerine "a ForzaTech .minizip archive, not a model" olarak adlandırılır ve `minizip.py`'ye yönlendirilir.

Geometri şu parçalardan gelir:

| Parça | İçerdiği |
|---|---|
| `VLay` | bir tepe noktası düzeni: öznitelik adları, sonra öğeler (u16 ad indeksi, u16 kanal, tampon, DXGI biçimi, ofset); öğe sayısı bir u16 |
| `VerB` | 16 baytlık bir başlığın ardında bir tepe noktası tamponu (sayı, boyut, u16 adım, u16 öznitelikler, biçim) |
| `IndB` | indeks tamponu, aynı başlık |
| `Mesh` | bir alt ağ: malzeme, ayrıntı düzeyi maskesi, indeks aralığı, düzen, tampon, adım, varyant tablosu ve sonda bir konum kutusu |
| `MatI` | bir malzeme örneği: `.materialbin` yolu ve doku hash'leri |

### Konumlar ve kutu {#positions-and-the-box}

Konumlar `R16G16B16A16_SNORM` (biçim 13): tepe noktası başına dört işaretli kısa. `position = short / 32767 * scale + bias`; ölçek ve sapma, `Mesh` parçasının son 32 baytıdır (iki float4). Sapma **oyunun dünya koordinatlarındadır**, bu yüzden bir arazi karosu, oyunun onu koyduğu yere hiçbir örnek dönüşümü olmadan iner. Bu yüzden bir haritanın bir parçasını istemek için bir telemetri turu yeterlidir.
Bir modelin her alt ağı aynı kutuyu taşır (860 tanesinde denetlendi).

### Tepe noktası düzeni {#the-vertex-layout}

Tek bir konum tamponu bütün tepe noktalarını kapsar. Konum dışındaki öznitelikler, art arda gelen tepe noktası gruplarına bölünür; her birinin kendi tamponu ve kendi düzeni vardır: bir kavşağın yakınındaki yol üç UV kümesi ve iki tanjant taşır, yanındaki şev yalnızca bir normal. Konum dışındaki her öznitelik dört bayttır. Hangi düzenin hangi tamponu tanımladığı, ona çizen alt ağlardan alınır, çünkü düzenler ve tamponlar aynı sırada değildir (modele göre aynı, bir atlamalı ya da karışık).

| DXGI biçimi | Kod | Kullanımı |
|---|---|---|
| R16G16B16A16_SNORM | 13 | konum (dördüncü kısa normalin x'idir) |
| R16G16_SNORM | 37 | normal y, z |
| R16G16_UNORM | 35 | bir UV çifti (kanal = hangi küme) |
| R8G8B8A8_UNORM | 28 | renk ya da karışım ağırlıkları |
| R10G10B10A2_UNORM | 24 | tanjant (çözülmez) |
| R16_UINT | 57 | indeksler |

**Normal bölünmüştür.** `NORMAL` y ve z'yi tutar. x, dolgu sanılan konum'un dördüncü kısasıdır. Yüz binlerce arazi tepe noktası üzerinde, yalnızca üçgen normalinin x'iyle +0,92 korelasyon gösterir ve başka hiçbiriyle göstermez. Onunla, eğimli zeminin %96'sı hesaplanmış normalden 18° içindedir. Onsuz denenen her iki bileşenli kodlama (48 düzenin tamamındaki oktahedral dahil) y ve z'yi doğru, x'i yanlış aldı.

Başka konum ya da indeks biçimleri **reddedilir** ("only 13 (four shorts, scaled) is implemented"; "only unsigned shorts are implemented").

### Alt ağlar {#submeshes}

Bir `Mesh` kaydı standart biçimde 238 bayttır. Daha uzun olanlar, önde daha uzun bir malzeme **varyant** tablosu taşır: 238 + 8 x sayı - 4 bayt; ondan sonraki her alan tam olarak o kadar geri kayar. Daha kısa olanlar (218 bayt, bazı arazi) ofsetlerini korur. Her varyant girdisi `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. Ayrıntı düzeyi maskesi bir u16'dır, 1. bitten başlayarak her düzey için bir bit.

Hiçbir şey tek başına güvenilmez. İndeks aralıkları indeks tamponunu tam olarak döşemelidir, her `index count` 3 x `triangles` eşit olmalıdır ve bir alt ağın adlandırdığı adım, kendi tamponunun adımı olmalıdır. Bir tablo başarısız olursa bütünüyle reddedilir, çünkü yanlış okunmuş alanlardan üçgenlere etiket vermek, hiç etiket vermemekten kötüdür. Tamponu aralık içinde olan her örneklenmiş alt ağ (binlercesi) geçer.

### Malzemeler ve doku hash'leri {#materials-and-texture-hashes}

Bir `MatI`, malzemesini parçada arayarak bulunan bir `Game:...\x.materialbin` yoluyla adlandırır. Dokuları, aralarında 33 bayt olan, hizasız `u32 slot, u32, u32 hash` kayıtlarıdır; bu yüzden parça her bayt ofsetinde, bilinen doku hash'leri olan sözcükler için taranır. Bunlar parkurun `AssetManifest.xml` dosyasından gelir (`<Texture Source="...\name.swatch" SourceHash="...">`, `</Textures>` kadar okunur). `0x88B483AA` yuvası standart gölgelendiricinin taban rengidir. Renk dokusunun nasıl seçildiği [Forza Horizon](course-forza-horizon.md#which-texture) sayfasındadır.

## `.pb`: doku numuneleri {#pb-texture-swatches}

Bir numune, bir modelle aynı `burG` konteynerdir: bayt 44'te 96 baytlık bir `HCXT` başlık ve bir piksel parçası. Başlık, texture'ın GUID'ini (dosya adındaki), genişliğini ve yüksekliğini, mip sayısını ve **bayt 72'deki biçim kodunu** (ForzaTech'in kendi numaralandırması) tutar. Bayt 84, piksel bayt sayısını tutar.

| Kod | Biçim | Olarak tanındı |
|---|---|---|
| 0 | BC1, pikselin yarım baytı | kırmızı ve beyaz bir bordüre çözülür (BC4 altında gürültü) |
| 9 | BC7, pikselin bir baytı | parkurun görünür olduğu bir arazi karosuna çözülür |
| 13 | RGBA8, pikselin dört baytı | düz |
| diğer | reddedilir | "texture format N has not been identified; refusing to guess" |

Biçimler, yük boyutunun izin verdiği her yolla gerçek dosyaların çözülmesiyle tanımlandı. Önceki bir sürümün biçim saydığı bayt 47, örneklenen tüm dokularda 4'tür. Bir dosyanın yalnızca en üst mip'i çözülür. Her çözünürlük kendi girdisidir: `<name>_<guid>_quality<n>.pb`, kalite 1 en küçük, 5 en büyük. Arazi haritaları için en büyük iki tanesi, diğerlerinden farklı bir arşivdedir. Çözme, üretilen bir DDS başlığı üzerinden Pillow'un BCn çözücüsüne gider.

## Yerleşim dosyaları (.pgeo) {#placement-files-pgeo}

Her kategori ve uzamsal hücre için bir dosya: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Yol tek başına hücrenin karesini ve kategorisini verir, böylece dosyalar açılmadan süzülebilir.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Her alan nasıl kararlaştırıldı:

| Alan | Karar veren |
|---|---|
| konum, kutunun oranı değil 16.16 sabit noktalıdır | ardışık bariyerler tam olarak 4,000 m arayla durur (modelin uzunluğu) |
| işaret-büyüklük, iki tümleyen değil | iki tümleyen negatif koordinatları on kilometrelerce uzağa koydu; bit 31 işaret olunca, örneklenen her kategorinin her kaydı dosyasının kutusunun içine düşer |
| vektörler modelin kendi eksenleridir | her bariyerin ucu, bir sonrakinin başlangıcına düşer: %93,5'i 5 cm içinde, medyan 0,000 m |
| bayt 60 varyanttır | bir billboard'un beş kopyası 0, 2, 2, 3, 4 okurken her bariyer 0 okur |

Yalnızca `_3D` ile biten adlar model kayıtlarıdır. Onlardan önceki varyant tablosu sonek olmadan adları listeler; kayıt olarak okunurlarsa sonsuza düşerler. Bir aday kayıt yalnızca sayısı dosyaya sığarsa kabul edilir; sonlu olmayan sayılar içeren örnekler atılır.

## Uygulanmayanlar {#not-implemented}

- Yukarıdakilerin dışındaki tepe noktası ve indeks biçimleri (reddedilir).
- 0, 9, 13 dışındaki doku biçimleri (reddedilir).
- Tanjantlar (okunur geçilir, kullanılmaz).
- Arazi gölgelendiricisinin malzeme katmanları. Zemin dokusu, karo haritalarının bir yorumudur (bkz. [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
