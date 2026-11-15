---
title: Frostbite
nav_order: 5
lang: "tr"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paketler, mesh'ler ve bölümler {#frostbite-toc-cas-bundles-meshes-and-levels}

**Bir Battlefield 6 bölümünü arazisine, yerleştirilmiş mesh'lerine ve onların renk haritalarına kadar okur ve bir `.glb` olarak yazar.** Frostbite oyunları (Battlefield, Need for Speed, Dead Space) içeriklerini `.toc` içindekiler tabloları ile tanımlanan `.cas` bloblarında tutar. Bir bölümün tablosu, bölümün hangi paketleri yüklediğini söyler; paketler her varlığı adlandırır; ve varlıklar hangi mesh'in nerede durduğunu söyler.

Kaynaklar:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tablolar, paketler, yükler),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paketler ve manifestleri),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX bölümleri),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(yükseklik alanı),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(dokular ve materyaller),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(yerleşim ve dışa aktarma).
Komutlar: `identify`, `levels`, `level` (bkz. [Komutlar](commands.md#levels-and-level-frostbite)).

Bunların hiçbiri oyun tarafından belgelenmemiştir. Aşağıdaki her düzen dosyalardan okunmuş ve sonra hepsine karşı sınanmıştır; her bölüm, sınamanın ne olduğunu söyler. Frosty modding araçlarının bir yapının eski sürümlerini anlattığı yerlerde, alan adları onlarınkini izler; ama hiçbir kod onlardan alınmamıştır (bkz. [Haklar ve lisanslar](rules-and-licences.md)).

## Şifreli görünen ama olmayan başlık {#the-header-that-looks-encrypted-and-is-not}

| Sihirli değer (u32, little-endian) | Anlamı | Nasıl ele alınır |
|---|---|---|
| `0x00CED100` | düz: ağaç hemen başlar | okunur |
| `0x01CED100` | imzalı: 556 baytlık bir imza, sonra ağaç **açık metin olarak** | okunur |
| `0x03CED100` | başlığındaki anahtarla XOR ile karıştırılmış | algılanır ve reddedilir |

İmzalı biçim, güncel Battlefield'ın gönderdiği biçimdir. Sihirli değerden sonraki yüksek entropili baytlar bir imzadır, şifreli metin değil.

## DbObject ağacı {#the-dbobject-tree}

Tek bir özyinelemeli yapı. Her alan bir tür baytı (düşük beş bit tür, bit 7 "anonim"), isteğe bağlı bir ad ve bir değer taşır. Kapsayıcılar uzunluklarını değişken uzunluklu bir tamsayı olarak taşır ve sıfır baytla biter. `parse_toc` her kapsayıcının uzunluğunu denetler; yani ayrıştırılan bir dosya anlaşılmıştır. `layout.toc` bu biçimdedir.

## Kurulum paketleri {#installation-packages}

Her konum, blobunun ait olduğu **kurulum paketini** adlandırır. Her paket blobları `cas_01`'den numaralandırır; bu yüzden, birden çok paket kurulu olduğunda (ki bu her zaman böyledir), tek başına blob numarası belirsizdir.

- `layout.toc`, paketleri `installManifest.installChunks` altında listeler; her biri bir `persistentIndex` ve `Win32/installation/<package>` gibi bir `installBundle` ile.
- Paketin blobları bu klasördedir: temel oyun için `Data` altında, sonradan gelenler için `Update/<pack>/Data` altında.
- Bir konum kaydı tam 32 bitlik `persistentIndex`'i taşır: ilk sözcüğün düşük yarısı yüksek yarıyı tutar, ikinci sözcüğün yüksek yarısı düşük yarıyı; ikinci sözcüğün düşük yarısı blob numarasıdır.

Denetim: bir kurulumun her ikili tablosundaki her konum, bildirilmiş bir pakete çözülür ve adlandırdığı bloğun içine düşer. Önceki bir sürüm, doğru numaralı ilk `cas_NN.cas`'ı alıyordu. Okuduğu yüklerin üçte biri o zaman yüksek entropili görünüyordu ve şifreleme sanılıyordu. Doğru ofsetlerdi, yanlış dosyada. Bulunan hiçbir şey şifreli değil.

## Bölüm tablosu {#the-level-table}

Bir bölümün tablosu (`levels/<level>/<level>.toc`) bir bölüm tablosudur: büyük-endian on beş başlık sözcüğü, sonra uçtan uca dizilmiş bölümler; ofsetleri hem belirtilmiş hem de iki sayıdan türetilebilir.

| Bölüm | İçerik |
|---|---|
| bloblar | bir karma tablosu (her biri bir sözcük), sonra blob başına 16 baytlık bir kayıt: anahtar, `0x40000000` \| boyut, 0, ofset |
| parça karma tablosu | parça başına bir sözcük |
| parçalar | 16 baytlık kimlik (parçanın GUID'si **baytları ters çevrilmiş**), sonra bir sözcük: `0x80000000` \| konumunun dizininin 4 katı |
| konumlar | dört büyük-endian sözcük: paket (bölünmüş), blob, ofset, boyut |

Parça kimlikleri ve konumlar **farklı sıralardadır**. Dosya sırasıyla okumak, her parçayı başka bir parçanın baytlarıyla eşler; bunlar güzelce çözülür (çoğunlukla ses olarak) ve bu yüzden bir mesh gürültü olarak çıkana kadar yanlış görünmez. Denetim: bir bölümde indeks sözcükleri, 0'dan parça sayısının bir eksiğine kadar bir permütasyondur.

Bloblar bölüm tablosundan sonra satır içinde saklanır. Her biri dokuz büyük-endian başlık sözcüğü ve sonra girdileri: sekiz bayt ofset ve boyut, girdinin bayrak baytının en üst biti ayarlıysa önüne paketi ve bloğu adlandıran sekiz bayt daha. Denetim: her blobta son girdi, bayrak baytlarının başladığı yerde biter.

### Hangi tablo bölüm {#which-table-is-the-level}

Bir bölümün aynı adlı birden çok tablosu olabilir: temel oyunun `Data`sında bir tane, bölümü gönderen ya da değiştiren her güncellemede (`Update/<pack>/Data`) bir tane, ve her yüksek çözünürlüklü pakette bir tane (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Yalnızca bazıları blob taşır. Bir güncellemenin gönderdiği bir bölüm için, temel oyundaki tablo yalnızca parça taşır ve blob taşımaz; asıl bölüm güncellemedeki tablodur. Bulunan ilk tabloyu almak, bölümün hiçbirini dışa aktarmazdı.

Bu yüzden bölüm, en çok blobu olan tablodur; eşitlikte sonraki katman kazanır (önce temel oyun, sonra güncellemeler ad sırasıyla). Blobu olmayan aynı adlı tablolar ise onun **ek tablolarıdır** (supplements): parçaları bölümün parçalarına eklenir, çünkü en büyük doku mip'lerini tutarlar. Bir doku başlığı bu parçayı +164'te adlandırır (bkz. [Dokular ve materyaller](#textures-and-materials)). `levels`, her bölümün nereden geldiğini ve kaç ek tablosu olduğunu yazdırır.

## Paket manifestleri {#bundle-manifests}

Bir paketin ilk girdisi, sıkıştırılmamış olarak saklanan manifestidir. Daha eski Frostbite oyunlarının ikili paket biçimidir, yeni bir sihirli değerle, `0xD68E799D`: sayılar, SHA-1'ler, ebx ve res kayıtları (ad ofseti ve boyutu), res türleri, meta veri ve kimlikler, parça GUID'leri, dizeler. Paketin kalan girdileri sırasıyla ebx, res ve parçalardır. Denetim: sayılar her pakette girdilerle eşleşir ve dizeler kayıtların bittiği yerde başlar.

Kaynak türleri karmadır. `0x49B156D4` MeshSet'tir (bu türdeki her res `..._mesh` olarak adlandırılır), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` bunların hepsini bir bölüm için birkaç saniyede okur: bir bölümün onlarca paketi ve on binlerce ebx, res ve parçası olur.

## Yük blokları {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Sıkıştırılmış boyut sıfırsa, açıldığı boyuta eşit olduğu sürece saklanmış sayılır.

| Yöntem sözcüğü | Kodlama |
|---|---|
| `0x0070`, `0x0071` | yok |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), oyunun kendi `oo2core` DLL'inden) |
| diğer, boyutlar eşitse | saklandığı gibi kopyalanır |
| diğer | reddedilir |

Doğru paketten okunduğunda, örneklenen her yük çözülür.

## EBX bölümleri {#ebx-partitions}

EBX, ham veri olmayan her şeyi tutar. Her bölüm bir RIFF dosyasıdır: `EBXD` (veri, 16'ya hizalı), `EFIX` (bölüm GUID'si, tür GUID'leri ve imzaları, örnek, işaretçi, içe aktarma ve tür bilgisi ofsetleri, içe aktarmalar ve dizi, kutulu değer ve dize ofsetleri), `EBXX` (dizi tablosu: ofset, sayı, karma, bayraklar, öğe türü). Bir işaretçi alanı sekiz bayttır: sıfır boştur, tek bir değer `değer >> 1` numaralı içe aktarmadır, diğer her şey alanın göreli konumuna göredir.

**Tür kütüphanesi okunamaz.** Oyun onu, şifrelenmiş olan ilk dosya sisteminde gönderir ve bu paket ona dokunmaz. Türler GUID ve imzalarıyla bilinir; her bölüm bunları taşır ve bölüm dışa aktarmasının ihtiyaç duyduğu birkaç tür verilerden çıkarılarak düzenlenmiştir.

## MeshSet {#meshset}

Bir mesh, bir MeshSet res'idir (tanım) ve her ayrıntı seviyesi için bir parça (tampon).

| Kısım | Düzen |
|---|---|
| önek | dört sözcük: başlık boyutu (176 ya da 192), seviye kaydı boyutu (176 ile 188 arası), bölüm kaydı boyutu (368), 0 |
| başlık | sınır kutusu; altı i64 seviye ofseti; mesh türü `0x6C`'de (rigid, skinned, composite); seviye ve bölüm sayıları `0x9C`'de |
| seviye | bölümler `+0x08`'de; beş çizim listesi `+0x14`'te (opak, saydam, decal, yalnızca derinlik, gölge); indeks biçimi `+0x54`'te (`0x21` u16, `0x2E` u32), indeks ve vertex baytları; parça GUID'si `+0x74`'te |
| bölüm | materyal adı; vertex adımı; üçgenler, ilk indeks, vertex ofseti (bayt), vertex sayısı `+0x20`'de; vertex bildirimi `+0x64`'te: 16 x (kullanım, biçim, ofset, akış), 16 akış adımı, sayılar |
| parça | vertex tamponu, sonra indeks tamponu. Bir bölümün akışları birbirini izler; indeksler bölümün ilk vertex'inden sayar |

Konumlar kullanım 1, akış 0, ofset 0'dadır; dört yarım ya da üç float olarak.
Yalnızca opak ve saydam bölümler çizilir. Adı `..._shadow` olan her bölüm yalnızca gölge listesindedir; yani listeler kararı verir.

Denetim: seviyeleri parçalarda saklanan bir bölümün her mesh'i çözülür ve neredeyse hepsinin vertex'lerinin %99 veya daha fazlası bildirilen kutunun içindedir; kalanlar yarım-float yuvarlamasıyla ıskalar. Çözülmüş bir sandık yaklaşık bir metre, Y yukarı, normalleri dışarı bakar.

## Yerleşim {#placement}

İçerik hattı, bir alt dünyanın statik nesnelerini bir **statik model grubunda** toplar: her mesh için bir üye, her biri örnek dönüşümleriyle birlikte.

| Tür (GUID, imza) | Düzen |
|---|---|
| üye `ad13064e…`, `0xF861A878` | 224 bayt: `+88` dönüşümlerin dizisi, `+112` nesne taslağı (içe aktarma), `+160` mesh varlığı (içe aktarma) |
| dönüşüm `101dce06…`, `0x5E6D8C37` | 64 bayt: sağ, yukarı, ileri, öteleme; her biri 16'ya dolgulu bir vec3 |

Mesh varlığının bölümü, MeshSet res'i gibi adlandırılır; yani içe aktarmanın bölüm GUID'si mesh'i verir. Bir nokta `x·right + y·up + z·forward + translation` konumuna düşer. Grubun kendi dönüşümü, incelenen bölümlerin her grubunda birim matristi ve uygulanmaz.

Denetim: bir bölümde her grubun her üyesi bir mesh'e çözülür; kopyaların çoğunun determinantı binde birine kadar 1 olan bir dönüşü vardır, kalanları ölçeklenmiş ya da aynalanmıştır. Tür GUID'leri ve imzaları diğer bölümlerde aynıdır. Düzeni değiştiren bir oyun güncellemesi imzayı değiştirir; o zaman okuyucu yanlış okumak yerine hiçbir şey bulmaz.

### Tek tek yerleştirilen nesneler {#objects-placed-one-by-one}

Hattın gruplayamadığı şeyler (yıkılabilir nesneler, konteynerler, enkaz) bölümün **nesne referansları** ve **prefab referansları** ile yerleştirilir:

| Tür (GUID, imza) | Düzen |
|---|---|
| nesne referansı `a9a6a6ad…`, `0xC4856BEC` | `+32` dönüşüm (yukarıdaki gibi), `+112` nesne taslağı (içe aktarma) |
| prefab referansı `117c746e…`, `0xDE3FE9B4` | aynısı; taslak bir prefab'dır, daha fazla referanstan oluşan bir bölüm |

Prefab'lar iç içe geçer; bir kopya, kendi dönüşümünün çarpı üst öğesinin dönüşümünde (satır vektörleri) yerleşir, sekiz seviyeye kadar. Bir nesne taslağı, içe aktardığı mesh'ler olarak çizilir, yok edilmiş durumlar (`dc_...`) dışarıda bırakılarak. Gruplanmış bir prefab, `..._nongroupable_autogen` kalanıyla referans verilir; böylece hiçbir şey iki kez çizilmez.

Yürüyüş yalnızca bölümün dünyalarından ve katmanlarından başlar. İlk örneği bir prefab taslağı (`134919fc…`, `0x0247807D`) olan bir bölüm, bir prefab'ın tanımıdır; bölüm bunları kendi klasörü altında çok tutar ve onları bu referanslardan farklı yollarla dünyaları yerleştirir. Bir dünya gibi yürünürse, bir prefab içeriğini yerel koordinatlarında koyar. Bu, dünyanın orijini etrafında yüzlerce kopyayı, zeminin çok altında biriktirir. Dünyalar ve katmanlar ilk olarak `a10ebe0f…`, `0xD3D16C3C` ile başlar.

Oyunun dışında tutulan taslaklar takip edilmez: geliştirme ve test varlıkları (`game/dev/`, `test/`), tur sonu sinematiğinin sahnesi (`..._gameend_...`: zeminin altına sahnelenmiş) ve ölüm kamerasının kontrolcüsü (`.../deathflow/...`, bileşenleri dünyanın orijininde durur). Bunlar katmanlarıyla değil, varlık yollarıyla tanınır: sinematik sahneyi tutan aynı katman, bir bölümün gerçek duvarlarını ve çatılarını da yerleştirebilir. İki kuraldan sonra incelenen bölümlerin hiçbir kopyası arazinin 10 m altından fazla derinde değildir ve kopyalar oyunun gösterdiği yerde arazinin üstünde durur.

**Yer tutan ayrıntı seviyeleri.** Bir mesh'in son ayrıntı seviyesi, kendi materyali olan uzak görünüm yer tutucusuna geçebilir: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. On binlerce üçgenli bir kafes kule, birkaç yüz üçgenlik bir siluetle bitebilir; bütçe bunu seçer ve yakından bakıldığında katı bir dikene dönüşür. En ince seviyesinde olmayan böyle bir malzemeyi getiren bir ayrıntı seviyesi hiçbir zaman seçilmez; mesh'in en kabası, son gerçek seviyedir.

## Arazi {#terrain}

Kaynak: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Arazi, bir TerrainStreamingTree res'idir (tür `0x22FE8AC8`) ve adlandırdığı parçalar.

| Kısım | Düzen |
|---|---|
| başlık | 34 bayt; düğüm sayısı 25'te |
| raster ağaçları | her biri bir tür baytı ve bir u32 uzunluk, tür baytı `0xFF` olana dek. Tür 0 yükseklik alanıdır: +5'te (265) bir kenardaki örnek sayısı, +21'de (1.280 m) yükseklik aralığı, ilk düğüm kaydının +77'sinde arazi karesi (incelenen bölümde 8.192 m). Yükseklikleri değil, düğüm sınır kutularını ve düğüm başına 16 x 16 min/max piramidini tutar |
| akış düğümleri | dörtlü ağaç, derinlik öncelikli: parça boyutu ve GUID; isteğe bağlı ikinci bir parça; bir bayrak baytı (bit 0: parça bir yükseklik sayfasıyla başlar); çocuğu var mı. Çocuklar (0,0), (1,0), (1,1), (0,1) sırasıyla |
| yükseklik sayfası | bayraklı bir düğümün parçasının ilk 265 x 265 u16'sı, satır satır; yükseklik = değer x 1.280 / 65.535 m; sütunlar x boyunca, satırlar z boyunca, düğümün alt köşesinden; 4 örneklik bir kenar, yani düğüm başına 256 hücre |

Her adım kendi başına denetlendi:

- Düğüm dörtlü ağacının ayrıştırılması res'in son baytına kadar tüketilir ve bildirilen 529 düğümü verir.
- Komşu düğümler dokuz kenar sütunlarını tam olarak paylaşır; bu yüzden adım 256'dır.
- Bir çocuğun örnekleri, her iki konumda bir, kendi ebeveyninin örnekleriyle tam olarak eşittir (4'lük bir kenarla); başka bir kenarla 90 ile 700 birim arasında sapar.
- Bir bölümdeki en düşük sözcük, sınır kutusunun en düşük yüksekliğini santimetreye kadar çözer.
- Karenin dünyaya yerleşebileceği sekiz yoldan yalnızca x'in x boyunca ve z'nin z boyunca gittiği yol, yerleştirilmiş nesneleri zemine oturtur: örneklenen kopyaların yarısı yaklaşık 2 m içinde; diğer her yol bunun birkaç katı.

Yerleştirilmiş nesneler sonra sonucu ölçer. Her kopyanın en alt noktası, altındaki araziye karşı (çift doğrusal, en ince düğümden):

| Yerleştirilen | Ortanca uzaklık | İşaretli ortanca |
|---|---|---|
| ağaçlar ve çalılar | bir metrenin çok altında | yüzeyin hemen altında |
| süsler | bir ya da iki metre | yüzeyde |
| kayalar | yaklaşık bir metre | yaklaşık bir metre gömülü |
| binalar | birkaç metre (temel üzerinde dururlar) | hafifçe gömülü |

Bitkiler yalnızca zemine yerleştirilir ve başka hiçbir yere; bu, en keskin denetimdir: kökenleri yüzeyden ortanca 0,07 m uzaktadır. Binalar geniş yayılır, çünkü bu kategori çok katlı ve yeraltı yapılarının duvarlarını, döşemelerini ve kit parçalarını tutar. Arazinin 64 m yana kaydırılması, yarım metre içindeki kopyaların oranını %29'dan %10'a düşürür.

`level` yükseklik alanını `ground:terrain` olarak çizer; her parçası, yükseklikleri olan en ince düğümden ve `--ground-spacing`'den (varsayılan 4 m: incelenen bölüm için 3,7 milyon üçgen, en ince düğümleri 0,5 m) daha ince olmayan düğümlerden alınır. Farklı çözünürlükteki parçalar küçük basamaklarla buluşur; hiçbir şey onları birleştirmez.

Bir düğümün parçası, yükseklik sayfasından sonra, o düğümün grupları için maske sayfalarını da tutar ve ikinci parçası, düğümün renk haritasıyla biter (bkz. [Arazi katmanları](#terrain-layers)).

## Terrain layers {#terrain-layers}

Oyun, bir oyuncunun yakınındaki arazi, boyalı maskelerle karıştırılmış döşenebilir yüzey malzemeleriyle, üstüne bir renk haritası bindirilerek ve üstüne decal'ler (yollar, asfalt yamaları, pist işaretleri) çizilerek gölgelendirilir. Frostbite'ın bu sistem hakkındaki kendi anlatımı (Widmark, "Terrain in Battlefield 3", GDC 2012) arazinin rasterlerini şöyle listeler: yükseklik alanı, gölgelendirici karıştırma maskeleri, "shader splatting" üstüne bir bindirme olarak kullanılan bir renk haritası, fizik malzemeleri, bir yıkım derinlik maskesi, sıçrayan ışık için bir albedo haritası ve ek maske kanalları; bir rasterin parçaları, işleme algoritmaları için bir kenar taşır. İncelenen bölümlerin akış ağacında yedi raster ağacı vardır, türleri 0, 1, 2, 4, 5, 7 ve 8; başlıkları parça boyutlarıyla başlar: yükseklik alanı (tür 0) ve tür 2 için 265, maskeler (tür 1) için 72 ya da 66, renk haritası (tür 4) için 2 kenarlı 132, tür 5 için 2 kenarlı 260.

**Katman listesi.** Arazinin `....layergraphs` res'i, maske kayıtlarının numaralandırdığı sırayla, katman başına 32 baytlık bir girdi listeler (bir bölümde 34 girdi, 34 depo bölümü ve 0'dan 33'e katman indeksleri); her girdinin kimliği, katman grafiğinin gölgelendirici blok deposundaki (`....layergraphs_shaderblockdepot`) bölüm anahtarıyla biter; bu bloğun adları katmanın haritalarını verir: katman başına bir `_cv` renk haritası, yüzey başına `_nhs` ve `_ao` haritaları, artı paylaşılan detay ve gürültü haritaları. Birçok katman hiçbir harita adlandırmaz: bunlar katman grafiğinin okuduğu kaynaklardır. Bir katmanın rengi, `_cv` haritasının ortalamasıdır; döşeme ölçeği bulunamaz. Arazi varlığı, katman başına beş baytlık bir girdiyle biter (bir bayt, sonra bir u32 katman indeksi ya da -1).

**Maskeler.** Raster ağacı 1, maskelerin dörtlü ağacıdır. Gövdesi 59 baytla başlar, sayfanın kenarı 0'dadır: sayfalar BC4 ise 72 (72 x 72, 2.592 bayt), sıkıştırılmamış sekiz bitlikse 66 (4.356 bayt). Sonra düğüm başına, derinlik öncelikli bir grup gelir:

| Kısım | Düzen |
|---|---|
| grup | u16; u16 kayıt sayısı; u32 sayfa sayısı; kayıtlar; bir sıfır baytı. Kaydı olmayan bir grup toplam 7 bayttır |
| kayıt | 33 bayt: u16 katman, u16 karma, çeyreğin kutusu (dört float), iki bayrak baytı, 85 bitlik bir varlık piramidi |

Bir grubun kayıtları, düğümünün dört çeyreği, katman katman, her katmanın çeyrekleri (0,0), (1,0), (1,1), (0,1) sırasıyla. İkinci bayrağı ayarlı bir kayıt çeyreği bütün kapsar ve sayfası yoktur; bu bayrağı olmayanın bir sonraki sayfası vardır; grubun adlandırdığı bir katmanın kaydı olmayan bir çeyrek, o katman için boştur; ilk bayrak yalnızca katman çeyreğin kendi grubunda bir seviye aşağıda devam ettiğinde temizdir, ve bu, oradaki kaydın yerini alır. Sayfa sayısı, bir sayfası olan kayıtların sayısıdır.

Sayfalar: bir akış düğümünün kendi grubunun sayfaları, parçasında, yükseklik sayfasından sonra gelir: 4.358 baytlık bir 16 bitlik bölüm ve 67 x 67 sekiz bitlik bir raster (parçanın başından, yükseklik sayfası yoksa); ikinci parçası dört çeyreğinin, bir seviye aşağıdaki grupların sayfalarını, renk haritasının sırasıyla çeyreklerin ardından ve sonra renk haritasını tutar. Bir sayfa, çeyreğin 64 x 64 texel'idir, satırlar z boyunca ve sütunlar x boyunca, komşularından kopyalanmış bir kenarla: BC4 sayfasında 4 texel, sıkıştırılmamış birinde 1.

Kenarlar yargıya gerek bırakmadan yerleştirmeyi kanıtlar: bir katmanın yan yana iki sayfası birbirinin kenar texel'lerini taşımalıdır. `read_masks` yerleştirdiği her çift için bunu denetler ve %99'dan az uyuşan bir bölümü reddeder. İncelenen bölümlerin yaklaşık üçte biri, kenarları uyuşarak okunur; birkaçında boyalı maske yoktur; kalanı reddedilir, neredeyse hepsi denetimle (düğümlerinin parçaları bu düzenin bildiğinden fazlasını tutar). Reddedilen bir bölümün zemini, yüzey malzemelerinin orta rengini alır ve dışa aktarma nedenini söyler. Tam bir çeyreğe yüzen kenarlar 255, boş birine bakanlar 0'dır.

Ayrıca: 4.358 baytlık bölüm ve sayfalardan önceki 67 x 67 raster okunmaz: değerleri dar bir yüksek bantta durur, küçük değer yok ve bekçi değer de yok.

**Zeminin rengi.** Katman grafiği katmanları, maskelerden, eğimden, yükseklikten ve gürültüden oluşan derlenmiş bir gölgelendirici grafiği içinde karıştırır; bu okunmaz. `--ground-texture` zemini, kendi kuralıyla renklendirir ve bunu burada böyle söyler:

- Renk haritası uzaklık için adlandırılmış katmanlar, uzak görünümün yer tutucularıdır ve dışarıda bırakılır;
- arazinin dokulu katmanlarından onda dokuzdan fazlasını kaplayanlar temeldir. Maskeleri hemen hemen her yerde dolu olduğundan, her birinin nerede durduğu onların değil gölgelendiricinin seçimidir: kaya ya da uçurum için adlandırılanlar 40 dereceden dik yamaçları renklendirir, çakıl için adlandırılanlar düz zemini (temel katmanların diğerleri, hiçbiri yoksa), ve 20 ile 40 derece arasında yükseklik alanının eğimine göre karışır (her 4 m'de örneklenip pişirilen texel'lere çift doğrusal yayılır: 4 m bloklarla tekrarlanınca kayalık renk sert kenarlı yamalar çizdi);
- başka her dokulu katman, kendi maskesiyle, katman sırasına göre temelin üstüne serilir;
- renk haritası sonuca, motorun yaptığı gibi bindirilir: zeminin renginin iki katı çarpı haritanın değeri, böylece orta gri hiçbir şeyi değiştirmez; renk haritasının texel'i olmadığı yerde zemin, haritanın ortanca parlaklığını gri olarak alır.

Oyun karelerine karşı, üç bölümün (yarı yolda HUD'a kadar satırların %55 ile 72'si), ortanca zemin rengi (kroma, kırmızı ve mavi olarak yeşile göre): bir bölümde pişmiş oynanış alanı 1,00 / 0,69 iken kareler 1,19 / 0,78; orada çimen katmanları kuru çimin olduğu yerde yeşil. Başka bir bölümde 1,19 / 0,82, kareler 1,01 / 1,04; onun renk haritası kendisi sıcak (1,13 / 0,88). Üçüncüsünde, renk haritası olmadan, 1,05 / 0,91, kareler 0,93 / 0,92. Kareler ışıklı ve derecelendirilmiştir, bu yüzden bu ölçüm tonu, parlaklığı değil, ölçer.

**Renk haritası.** Bir düğümün ikinci parçası, çeyreklerinin grupları için maske sayfalarından sonra, dört BC7 sayfası içerir; her biri 132 x 132 (her biri 17.424 bayt), düğümün çeyrek başına bir tane, sırasıyla (düşük x, yüksek z), (yüksek x, yüksek z), (yüksek x, düşük z), (düşük x, düşük z). Maske ağacı, maske sayfalarının kaç bayt tuttuğunu söyler; bu yüzden renk haritası parçanın sonuna göre değil, sayıyla bulunur: bir bölümde daha kaba düğümler bundan sonra dört sayfa daha taşır, bir başkası düz renkte başka bir raster; parçanın son dört sayfasını okumak, arazinin onda dokuzundan fazlası üzerindeki renk haritasını kaybetti. Bu sayım olmadan, renk haritası sıkıştırılmamış maske sayfaları olan bölümlerde de kaçıyordu; bu sayfalar tam sayıda BC4 değildir; bir bölümün renk haritası, arazisinin 0,4'ünden 0,94'üne çıktı. Sıra uyumlandı: her çeyreğin yükseklik alanının kenarlarına karşı, özellikleri olan düğümlerin her sayfası, çevrilmeden tek bir çeyreğe 0,3 ile 0,54 arası uyar; bir sonraki en iyi yerleşim 0,2'nin altındadır. Bununla dikilen bir bölümün sayfaları, test bölgesinin yollarına, sularına ve yerleşim alanlarına, oynanış alanında 0,5 m texel başına dikişsiz birleşir. Katmanlar işi yaptığı yerde renk haritası neredeyse nötrdür (ortanca 110, 107, 104); başka yerlerde tam renk taşıyabilir. Yalnızca sıkıştırılmamış maske sayfaları içeren ikinci parçalara sahip bir bölümün renk haritası okunmaz. Bu okuyucunun önceki bir turu bu sayfaları coğrafi olmayan sayıyordu: onları arka plan haritasıyla eşleştirmişti; bu harita başka bir arazi bile olabilir, ve her sayfayı tüm düğümüne, çeyreğine değil, koymuştu.

**Sıçrayan ışığın albedosu** aranmış ve bulunamamıştır: kök ve birinci seviye düğümlerinin parçaları bütün maske sayfalarıdır ve tür 5'in yükü bulunamamıştır.

**Delikler.** Bir bölümün arazi varlığı (res türü `0x1CA38E06`) üç gölgelendiriciyi adlandırır: varsayılan yüzey gölgelendiricisi, delik yüzey gölgelendiricisi ve varsayılan kaynak gölgelendiricisi. Delik gölgelendiricisinin hangi katmanı okuduğu bulunamadı; bu yüzden yükseklik alanı kesilmez. Bir bölümde gezinme mesh'i, altındaki yükseklik alanının onlarca metre aşağısında kaya mesh'lerinde çalışabilir; oyunun onları kesmiş olması gerekirdi. Orada aranmış ve bulunamamıştır: bir katmanın maskesi, 67 x 67 raster, ayrılmış bir yükseklik (bölümün hiçbir yükseklik sayfası 0 ya da 65.535 tutmaz) ve bir düğüm bayrağı (kökün altındaki her düğümün bayrağı 1). Raster ağaçları 7 ve 8 geriye kalanlardır. İkisi de çalışma-uzunluğu kodludur: önceki baytla eşit bir bayt, ardından daha fazla kopya sayısı gelir (`ff ff 84`, 255'in 134 baytıdır). Ağaç 7 (karo 256, beş seviyeli tam bir dörtlü ağaç, örnek başına dört bit) 0 ile 3 arası değerlerin bayt çiftlerine çözülür; ağaç 8 (karo 265), çoğunlukla 255 olan baytlara, diğer değerleri düzenli çalışmalarda. İkisinin karoları henüz yerleştirilmediğinden, hangisinin delikleri tuttuğu bilinmez.

**Decal'ler** okunur ve pişirilir; bkz. [Arazi decal'leri](#terrain-decals).

## Terrain decals {#terrain-decals}

Kaynak: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Yollar, pistler, beton apronlar, boyalı çizgiler ve harfler, lastik izleri: `TerrainDecals` res'i (tür `0x15E1F32E`) bunları, oyunun arazinin üstüne serdiği düz geometri olarak tutar.

| Kısım | Düzen |
|---|---|
| başlık | +16'da bir yuva sayısı n, sonra n tane 16 baytlık yuva, sonra kayıt sayısı |
| kayıtlar | çizim grubu başına bir tane, art arda, değişken uzunlukta: 156 baytlık sabit alanlar: ilk vertex +32'de, üçgen sayısı +36'da, metre cinsinden doku döşemesi +44'te; sonra grubun vertex baytları (ofset, boyut); sonra dokularını varlıklarının bölüm GUID'leriyle adlandıran bir kuyruk |
| vertex'ler | 32 bayt: x, z (f32), 8 paketlenmiş bayt, u, v (f32), r, g, b, a (f16); her grup düz bir üçgen listesi |
| indeksler | u32, her grupta 0'dan sayarak; gerekli değil |

Denetimler:

- kayıtların vertex aralıkları boşluksuz birbirini izler ve tüm vertex'leri tam olarak kapsar; her kaydın ilk vertex'i x 32, kendi ofsetidir;
- bu şekilde okununca üçgenler kompakt decal'lerdir (harfler, şerit çizgiler, yamalar); bir vertex atlanarak okununca haritanın üstünde şeritlerdir;
- neredeyse her grup, kuyruğunda doku adlandırır: bir renk haritası (`_cv`) ve bir opaklık haritası (`_op`, kırmızı kanal), ya da işaretler için bir kanal maskesi (`_rgb`).

Doku GUID'lerinden sonra kuyruk, grubun materyal parametrelerini taşır; gölgelendirici bloğununkiler gibi kodlanmış (bkz. aşağıda Tints). Bir işaretin, bir lastik izinin ya da bir çizginin boya rengi, `607e` karmalı float3'tür: kumdaki lastik izleri için kumsu 0,64, 0,56, 0,48; katran için neredeyse siyah. Opaklık haritaları çoğunlukla biçim 62'dir, blok başına sekiz bayt, tek kanal, BC4 olarak okunur.

Bir grup dokusunu ya dünya konumuyla eşler (u = x, v = z, doku her döşeme-metrede tekrar eder: asfalt, beton, çakıl) ya da decal boyunca 0'dan 1'e (bir çizgi, bir harf, bir lastik izi). Kayıtlar dosya sırasıyla çizilir.

**Pişirme.** `level --ground-texture M`, decal'lerin alanı altında ve en fazla 4.096 piksellik karolarda, arka plan renk haritasını (çift doğrusal) boyar, sonra her grubu opaklığı x vertex alfası ile üstüne çizer. Vertex'lerin rengi kullanılmaz: bazı grupların vertex'leri saf yeşil ya da mavidir ve bu bir bölümün işaretlerini o renklere boyadı. Oradaki arazi üçgenleri `ground:terrain x<x> z<z>` parçaları olur ve karoyu taşır. Her grup şöyle çizilir:

| Grup adları | Şöyle çizilir |
|---|---|
| bir renk haritası (`_cv`) | harita, opaklık haritasıyla |
| bir çarpım haritası (`_mult`) ve bir opaklık haritası | boya (malzeme bir tane adlandırmıyorsa beyaz) çarpı çarpım haritası, opaklık haritasıyla: bir pistin aşınmış orta çizgisi, kenar çizgileri ve eşik çubukları |
| bir kanal maskesi (`_rgb`) | boya, yoksa çizgiler ve harfler için beyaz, ana hatlar için koyu, aşınma, lastik izleri, lekeler, su birikintileri ve ıslaklık için hafif bir karartma, maskeyle |
| yalnızca bir opaklık haritası, bir boyayla | opaklık haritasıyla boya: lastik izleri |

Bir yol varyasyon maskesi boya değildir, altındaki yüzeyi değiştirir, yüzlerce metre boyunca; çizilmez, boyası ne olursa olsun: beyaza boyanınca bir bölümün yamaçlarına 150 ila 250 m uzunluğunda iki soluk dikdörtgen serdi. `_mult` haritası, altındaki zeminin koyulaştırılması değil, boyanın kendi aşınması olarak alınır: neredeyse beyazdır ve çizginin şekli opaklık haritasındadır.

Decal'lerin neredeyse hepsi, birkaç karoya piksel başına 0,5 m olarak çizilir; dışa aktarma birkaç MB büyür ve birkaç saniye daha sürer. Yukarıdan bakıldığında apronlar, taksi yolları ve yol ağı, bileşiklerin çitlerinin ve binalarının altında kalır ve kapılarına doğru uzanır.

Bunun yerine geometri olarak çizilse, decal'lerin alfa karıştırması gerekirdi; yazıcı bunu taşımaz; ve bir arazinin üstünde bir ofset z-fight yapardı. Pişirme, onları zeminin kendi renginde tutar.

## Dokular ve materyaller {#textures-and-materials}

Kaynak: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Bir Texture res'i (tür `0x6BDE20BA`) 180 baytlık bir başlıktır: +8'de tür ve piksel biçimi, +22'de genişlik ve yükseklik, +30'da mip sayısı, +40'ta parça GUID'si, +56'da on beş mip boyutu. Parça, mip zinciridir, en büyüğü önce. Bazı parçalar en büyük mip'lerinden yoksundur; bunlar yüksek çözünürlüklü bir pakette gönderilir ve parçanın uzunluğu hangi mip'ten başladığını söyler. O paketin parçası +164'te adlandırılır; ana parçada eksik bir mip istendiğinde bölümün [ek tablolarından](#which-table-is-the-level) okunur ve uzunluğu, ana parçanın uzunluğuna eklendiğinde tam zincir olur.

| Biçim | Şöyle çözülür |
|---|---|
| 67, 66 | BC7 (sRGB, doğrusal) | bir plastik tankın renk levhası BC7 olarak çözülür; BC3 olarak aynı baytlar gürültüdür |
| 61, 60 | BC3 | bir sandık levhası BC3 olarak temiz çözülür, BC1 ya da BC7 olarak değil |
| 57, 56, 55 | BC1 | piksel başına yarım bayt |

Mesh varlığı hiçbir doku adlandırmaz. Bağlantı, **gölgelendirici blok depolarındadır** (res türü `0x73312045`, alt dünya başına bir tane), bir mesh bölümünün kaydının +0x130'undaki sekiz baytla anahtarlanmış:

| Kısım | Düzen |
|---|---|
| tablo, 16'da | (bölüm anahtarı u64, tanımlayıcı ofseti u64), bir ofset res'in dışına düşene dek |
| tanımlayıcı | (blok ofseti u64, karma u64, blok boyutu u64) |
| blok | bölümün gölgelendirici parametreleri; her doku 49 baytlık bir kayıttır: bir bayt, 16 bayt, doku varlığının bölüm GUID'si, örnek GUID'si |

Sandığın bölüm anahtarı, onu yerleştiren alt dünyaların on depolarının her birinde bir kez görünür ve bloğu, `t_mil_crate_03_cs` ile `_nmt`'yi paylaşılan detay haritaları arasında adlandırır. Bir blok, gölgelendiricinin örneklediği her dokuyu adlandırır; hangisinin renk haritası olduğu belirtilmez, bu yüzden seçilir: adında malzemenin adındaki sözcüklerin çoğunu taşıyan (`M_ConcreteWall_01`: concrete, wall) sRGB 2D doku, sonra mesh'in adındakinden, sonra bir detay, decal (`t_de_...`) ya da hasar haritası olmayanı, ve sonra en az blok tarafından kullanılan. Bir yol tabelasının bloğu panelini `t_com_highwaysignage_01_cs` ve yanına yatırılmış bir kalkanlı decal sayfasını `t_de_com_highwaysignage_01_ca` olarak adlandırır; ikisi de sözcükleri eşler, ve decal kuralı olmadan sayfa kullanım sayısını kazandı ve tabela, bölümün sahip olduğu her doku koordinat kümesinde kalkanı dörtte bir döndürmüş gösterdi. İşaretli mesafe alanları (`..._sdf`), paletler ve kanal maskeleri (`_rgb`) hiçbir zaman seçilmez, hangi sözcükleri paylaşırlarsa paylaşsınlar (`_rgba` haritaları seçilebilir: çoğu renk artı alfadır ve onları dışarıda bırakmak bir elektrik hattının ve bir merdivenin kendi haritalarının yerine ilgisiz haritalar koydu): bir arka planın bitki atlası `..._atlas_a_sdf`, renk olarak çizildiğinde ağaçlar için siyah ve beyaz yıldızlar gösterdi; bir arka planın bina paleti duvarlar için renkli lekeler verdi; ve kanal maskesiyle çizilen cam enkazı camgöbeği çıktı. Adayları yalnızca paylaşılan detay haritaları olan bir bölüm, düz renkte kalır.

**Paletler.** Bir arka planın binaları, 16 x 16'lık renk karelerinden oluşan 256 x 256 texel'lik bir paletten renk alır: her vertex, ilk ikisi paletteki renginin yerini söyleyen dört bayt taşır (x ve y, 255'te). `level` böyle bir bölümü, paleti dokusu olarak, her vertex kendi karesinin merkezinde olacak şekilde çizer. Böyle çizilince bir bölümün arka plan blokları, beyazken düz olan yerde pastel duvarlar, tuğla rengi ve koyu pencereler olur.

**Overlay'ler.** Büyük nesneler, ilk doku koordinatlarıyla bir kırpma levhasını döşer ve ikinciyle üstüne bir overlay bindirir; bunlar 0 ile 1 arasında kalır: nesnenin tüm bir açılımı. Overlay (`..._overlay_cs`, maskesi `..._overlay_a`), nesnenin uzaktan nasıl göründüğünü tutar: bir yağ tankının kırmızı bantları ve pası; kırpma levhası tek başına çizildiğinde, bir bölümün tankları gri paneller olarak çıktı. Bloğu bir overlay'i maskesiyle adlandıran ve ikinci doku koordinatları böyle bir açılım olan bir bölüm, overlay ile, onlardan çizilir (o bölümde 36 bölüm).

**Tint'ler.** Birçok renk haritası gridir (üç kanalının ortalamaları birbirinin %6'sı içinde): gölgelendirici onları bloğun parametrelerinden renklerle boyar. Doku girdilerinden (49 bayt her biri) sonra bir blok parametrelerini listeler; her biri bir tür etiketi (`f11af825` bir float3, `a5e1f2de` bir float4, `c1b1a014` bir float, `4a4fc3a1` bir tamsayı), tek değer için `01 80` bayrak baytları, parametre adının iki baytlık karması, bir u32 sayı, değer ve sekiz baytlık bir kimlik. Adlar saklanmaz. Yedi float3 ad karması tint olarak davranır: bir bölümde üçü, haritası gri olan blokların yaklaşık altıda birinde bir renk tutar ve kendi renginin bulunduğu yerde neredeyse hiç; diğerleri, malzemenin adı öyle söylediğinde gri bir haritanın boyandığı renkleri tutar (bir köprünün `..._blue` süsü: nötr 0,5'e karşı 0,047, 0,098, 0,171). Bir aile, bir maskenin kanalı başına birkaç değer tutabilir, çoğu nötr; ve neredeyse hiçbir şeyi olmayan bir kanal (tuğla cephelerde saf yeşil) boyamaz, bir maskenin kanalını seçer. `level`, gri bir renk haritasını, doğrusal ışıkta, her ailenin nötr olmayan ve böyle bir seçici olmayan ilk değeriyle, nötr değerinin üstüne çarpar ve sonucu kendi dokusu olarak tutar; renkli bir harita olduğu gibi bırakılır. Kural dışa aktarıcının kendi kuralıdır: bir maskenin hangi kanalının hangi tint'i aldığı okunmaz. Bir bölümde yapı üçgenlerinin, neredeyse beyaz çizilenlerin payı %19,4'ten %3,9'a düştü.

**Nesne varyasyonları.** Bir mesh birkaç görünüşte yerleştirilir: kırmızı ya da mavi şeritli ve üstünde farklı bir numara boyalı bir depo duvarı, yeşil ya da gri bir konteyner. Yerleştirilen her kopya görünüşünü adlandırır:

| Nerede | Alan |
|---|---|
| statik model grubu üyesi | +32: kopya başına bir işaretçi dizisi, bir nesne varyasyonuna ya da null'a |
| nesne referansı | +120: bir nesne varyasyonuna ya da null'a işaretçi |
| nesne varyasyonu (`ov_...` bölümü, tür `235f2a9c...`) | ilk örneğinin +32'si: varyasyonun u32 ad karması |

Bir bölümün bir varyasyondaki görünümü, bölümün kendi anahtarıyla anahtarlanmış gölgelendirici bloğudur; varyasyonun karması ilk dört baytına küçük-endian bir u32 olarak eklenmiştir (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); bu anahtarla bloğu olmayan bir bölüm her varyasyonda aynı görünür. Bölümün meshvariationdb_win32 varyasyon veritabanları, mesh ve varyasyon karması başına, her varyasyonun dokunduğu materyalleri listeler, ama anahtarları listelemez: kuralı anahtarların kendisinden bulunmuş ve denetlenen varyantlı her bölümde tutmuştur (bir duvarın dört varyasyonu, her birinde üç bölüm). Bir varyasyonun bloğu hem tint'lerini hem de kendi dokularını taşır: duvardaki boyalı numara, varyasyonun bloğunun adlandırdığı bir harf levhasıdır. Gruplanmış kopyaların büyük bir payı bir varyasyonda yerleştirilir.

Bir blok, içeriğinin her kümesi için bir kez pişirilir ve depo girdisi bir içerik karması taşır (girdinin ikinci u64'ü). Bir bölümün varyasyonunun anahtarında bloğu olmadığında, varyasyon yine de bir **ikize** (twin) ulaşır: varsayılan bloğu aynı içeriğe sahip ve bir bloğu olan başka bir bölüm. İkizler olmadan, varsayılan blokları aynı uzunlukları paylaşan bir duvar iki renkte çıkabilir. Kendi varyantı olmayan bir bölüm, ikizlerinin çoğunun aldığı varyantı alır.

**Yıkılabilir mesh'ler.** Bir maçın yıkabileceği bir mesh, kendi adıyla yanında bir yıkım varlığı taşır (`.../br_x.destruction`, `.../br_x_mesh` için): yıkılabilir binalar ve duvarlar (`br_`) ve birçok süs. `level` onların yüzeylerini, `{"destructible": true}` glTF düğümleri taşıyan ` (destructible)` adlı kendi parçalarında tutar. Yok edilmiş halleri, yanlarındaki `dc_..._part<N>_mesh` mesh'leridir, her biri kendi orijininde ortalanmış; parçalarının nerede durduğu, okunmayan yıkım varlığındadır, bu yüzden yok edilmiş haller dışa aktarılmaz.

**Dışarıda bırakılanlar.** Yer tutucu blockout malzemelerinin (`M_Whitebox`: bazı binaların yüzeylerinin yanında tuttuğu birkaç büyük, dokusuz üçgen; bir bölümde beyaz yüzgeçler olarak çıkıyorlardı) bölümleri, sinematikler için yapılmış mesh'ler (sahnesi başladığında yerleştirilmiş bir helikopter) ve aydınlatma yardımcıları (ışığı engelleyen, hiç çizilmeyen düzlemler). Bir bölümün üretilmiş arka plan binaları (`..._generated_blueprints_..._mesh`) çizilir, ama duvarlarının materyal adları yalnızca gürültü haritalarını taşır ve vertex'leri renk taşımaz, bu yüzden düz kalırlar. Çizilen neredeyse her bölüm bir renk haritası alır.

**Harf levhaları.** Bir duvarın boyalı numarası ya da bir vincin afişi, kendi renk haritası bir levha (`_ca`) olan ayrı bir bölümdür: bir harfin alfası, düz boyanın üstünde, ya da bir baskı. İlk doku koordinatları, levhayı duvarın sıvasının üzerine döşer (bir duvarda u -0,2 ile 1,7), bu da levhayı neredeyse iki kez çizer; dördüncü küme (`0x24`, yoksa üçüncü, `0x23`) onu tam bir kez yerleştirir (u -1 ile 0, v 1 ile 2, daha kaba ayrıntı seviyelerinde birkaç binde birkaç taşar). İlk küme görüntünün bir kopyasını bıraktığında ve dördüncü ya da üçüncü bir kopyanın içinde kaldığında, levha onun üzerinden çizilir, 0 ile 1 aralığına taşınmış olarak. Alfalı bir levha, üzerine boyandığı yüzeyin 1 cm önünde çizilir; bu yüzey, bloğun diğer renk haritasıyla ilk küme üzerinden altta çizilir: bu olmadan levhanın boş texel'leri duvarın içini gösterirdi. İkinci küme, bir nesnenin overlay'i için açılımdır ve burada kullanılmaz.

**Kesme haritaları.** Renk haritasının dördüncü kanalı, haritanın adına göre farklı şeyler anlamına gelir. `_cs`'te, en yaygın olanı (bir bölümün seçilen 893 haritasında), pürüzsüzlüktür: ortanca bir haritanın alfasının %1'i 0 ya da 1'e 0,1 içindedir. `_cu` (yapraklar, çimen) ve `_ca` (renk ve alfa)'da ise opaklıktır: %90 ve %87. Adı `..._cu` ya da `..._ca` olan ve alfası en az %75'i 0 ya da 1'e yakın, en az %1'i 0,5'in altında ve en az %5'i üstünde olan bir renk haritası, alfasıyla, PNG olarak yazılır ve materyali glTF `alphaMode` MASK, `alphaCutoff` 0,5, çift taraflı olarak; yaprak kartları böylece yaprakları gösterir, siyah köşelerini değil. Bir ağacın yaprak haritasının hiç alfası yoktur (en fazla 255'te 4): yaprakları geometriyle kesilir ve yalnızca ilk iki koşulla bütün tepe kesilip atılıyordu.

Doku koordinatları vertex kullanımı `0x21`, iki yarım (biçim 6) ya da iki float (biçim 2). Bölümler, decal ve detay katmanları için üç küme daha taşır (`0x22` ile `0x24`). Koordinatlar döşenir: bir konteynerin kaburgalı yanı -1,6 ile 1,8 arasında gider, arka plan arazisinin döşemeleri tamamen 0..1 dışında kalır ve bir bölümde dokulu üçgenlerin %23'ü 0..1 dışına taşar. Oldukları gibi, tekrarlayan bir örnekleyiciyle yazılırlar; 3DHeat görüntüleyicisi her tekrarlayan dokuyu kendi atlasında sarar. Bunları kıstıran bir çizici, kaburgaları genişliklerinin iki katına çeker, bir beton zemini bir eksen boyunca çizgilere çevirir ve bir kulenin çelik kirişlerine dokusunun kenar rengini verir; bunun için `--clamped-uvs` her üçgeni dokusunun tekrar ettiği çizgiler boyunca keser ve her parçayı 0..1 aralığına taşır (bkz. [Çıktı biçimi](output-format.md)). Bundan sonra dokulu üçgenlerin %0,03'ü, dokusunun 16 kezden fazla tekrar ettiği üçgenler, dışarı taşar; ve kesim 4'ten fazla parça yapacak bir üçgen, bunun yerine dokusunun ortalama renginde çizilir: kabuk her dalda tekrar eder, ve kesilince bir bölümün ağaçları 6,4 milyondan 24 milyon üçgene çıktı.

Arazinin kendi okunabilir bir renk haritası yoktur. Arka planın doku haritalarından biri onu kapsıyorsa, renk oradan alınır: arka planın doku koordinatları dünya x ve z'nin doğrusal bir fonksiyonudur (tepe noktalarının %99'u bundan 0,001 içinde; harita 65.536 m'lik bir kareyi kapsar, çeyrek dönmüş); aynı fonksiyon arazininkini verir. Bölüm bu haritanın 2.048 px'den aşağıya mip'lerini sunar, bu yüzden arazi piksel başına 32 m alır. Karanlık kayası dik yamaçlarda durur: karanlığın eğimle korelasyonu 0,48'dir, diğer yedi yönelimde en fazla 0,34.

Başka bir bölümün arka planı, oynanış alanı etrafında sekiz yakın ve sekiz uzak karodur, her biri kendi dokusunu karonun üzerine tekrarlar ve hiçbiri arazinin üstüne gelmez. Her arka plan dokusu ayrı ayrı uydurulur; hiçbiri arazinin üstünü kaplamazsa, arka planın arazi karesinin bir kilometre içinde gösterdiği ortalama renk alınır; `--ground-texture` decal'leri onun üstüne pişirir. Bir arka plan malzemesi, adında `TerrainBackdrop` ya da `BD_` ve `Terrain` geçenidir (`M_BD_<site>_Terrain..._Near`); ya da bir arka plan mesh'i (`bd_..._terrain<site>_04_far_mesh`), düz bir arazi malzemesi taşır (`M_<region>_Terrain<site>_04_Far`); bu, ilk iki kuralın bir bölümde kaçırdığı ve zemini yüzeylerinden renklendirdiği bir durumdu.

Ancak hiçbir arka plan haritası arazinin üstünü kaplamıyorsa, arazinin kendi yüzeylerinin orta rengini alır, arka planın ortalamasından önce: katman grafiğinin gölgelendirici bloklarının adlandırdığı `_cv` renk haritaları (bir bölümde 27: kumlar, çakıllar, topraklar, çimen, çatlamış beton), her biri ortalanmış, sonra her kanalın ortancası, motorun varsayılan yüzeyi dışarıda bırakılarak. Bir arka plan, başka bir arazi bile olabilir: bir bölümde ortalaması (sRGB'de 95, 99, 80), oynanış alanının zeminini oyunun göstermediği bir griye çevirdi. `--ground-texture` ile, o renk renk haritasının iki katıyla çarpılır (orta gri değişmez bırakılır) ve decal'lerle birlikte, hem decal'lerin hem renk haritasının kapsamı üzerine pişirilir.

Her bölümün pişmiş oynanış alanının ve oyun karelerinin ortanca zemin rengine karşı (aynı 24 kare; sRGB; kareler ışıklı ve derecelendirilmiş olduğundan, r/g ve b/g oranları adil karşılaştırmadır):

| Bölüm | Kareler | Arka planın ortalaması | Şimdi |
|---|---|---|---|
| birinci | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| ikinci | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| üçüncü | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Birincisi düzeltildi; diğer ikisi öncesinde biraz daha tona yakındı. Bütün bir bölüm için tek bir renk her yerde doğru olamaz; maskeler olabilirdi.

## Gezinme mesh'i {#navigation-mesh}

Kaynak: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Bir bölüm, ajan başına bir bölüm gönderir: `<level>/dbt/<level>_navmesh_layer_<n>`. Bir bölümde 0. katman askerdir (1,8 m boy, 0,18 m basamak, 0,4 m yarıçap), ve iki diğeri araçlardır (3,5 ve 10 m yükseklikte). Her bölüm iki dizi tutar:

| Dizi | Öğe |
|---|---|
| karolar | 28 bayt: u32 0, u32 karma, u32 0, u32 parça indeksi, u16 karo x, u16 karo z, u32 ofset, u32 boyut |
| parçalar | 20 bayt: parçanın GUID'si, u32 boyut |

Bir karo, `parça indeksi` parçasında `ofset` konumunda `boyut` bayttır, little-endian, ve Detour'un (Recast Navigation) düzeninde, daha uzun bir başlığın ardında:

| Ofset | İçerik |
|---|---|
| 0 | `VAND`, sürüm 7 |
| 24 | sayılar: çokgenler, vertex'ler, bağlantılar, detay mesh'leri, detay vertex'leri, detay üçgenleri, sınır hacmi düğümleri, off-mesh bağlantıları, ilk off-mesh çokgeni |
| 188 | ajan yüksekliği, basamak, yarıçap |
| 200 | karonun sınır kutusu, altı float |
| 232 | vertex'ler: x, y, z floatları, dünya koordinatları |
| sonraki 8 baytlık sınır | çokgenler, 32 bayt: u32, altı u16 vertex indeksi, altı u16 komşu, u16 bayraklar, +30'da vertex sayısı, +31'de alan (düşük altı bit) ve tür (en üst iki) |
| sonra, paketli | bağlantılar (16 bayt), detay mesh'leri (12: ilk detay vertex'i u32, ilk detay üçgeni u32, vertex ve üçgen sayısı u8), detay vertex'leri (üç float), detay üçgenleri (üç indeks ve bayraklar), sınır hacmi düğümleri (16), off-mesh bağlantıları (80) |

Okunan her karoda bunlar karonun boyutuna bayta kadar tutar ve detay mesh'leri, ilk off-mesh çokgeninden önceki çokgenleri numaralandırır.

Bir çokgen, köşeleri arasında düzdür; **detay mesh'i** yüzeyin gerçek yüksekliğini, tümsekler, kayalar ve basamaklar üstünden tutar ve çizilen odur. Bir detay üçgeninin indeksi çokgenin köşe sayısının altındaysa o köşedir; aksi halde detay vertex'i `first + index - corners`. Çokgenleri yelpazeleyerek yapmak arazinin altında çok daha fazla üçgen bırakır ve uzun şeritler üretir; detay mesh'leriyle hiçbiri 16 m'lik bir karonun köşegeninden ve bir yamaçtaki basamak yükselişinden uzun değildir.

Tür 0 zemindir, tür 2 küçük dik yamaçlar (yaklaşık 45 derece, metrekare başına bir tane), tür 1 yüzeyler arası bir bağlantıdır: köşeleri 125 m veya daha fazla yükseklik kapsar ve karonun dışındadır, bazıları orijinde. Bağlantılar dışarıda bırakılır; kalanlar detay mesh'leriyle çizilir ya da detaysız bir karonun içinde yelpazelenir.

Denetimler: parçaların boyutları, karoların boyutlarının toplamını tam olarak verir; her yüzey vertex'i kendi karosunun kutusu içindedir, yaklaşık bir metre payla; neredeyse tüm üçgenler yukarı bakar. Başarısız olan bir karo reddedilir ve sayılır; ve o bölümde hiçbiri başarısız olmaz.

Test bölümünde yukarıdan görüldüğü gibi, askerin mesh'i: zemin, döşemeler, merdivenler ve bazı çatılar, ama serbest yük konteynerlerinin üst yüzleri değil. Bu, YZ'nin bir askerin durabileceği yerlerin haritasıdır; dosyaların oyuncuların durduğu yerlere en yakın bilgisi.

## Uygulanmayanlar {#not-implemented}

- Arazinin, yüzey katmanlarını karıştıran katman grafiği (bkz. [Terrain layers](#terrain-layers)): zeminin rengi, katmanların maskelerinden ve yükseklik alanının eğiminden bu okuyucunun kendi kuralını izler; maske sayfaları birbirine uymayan bölümler tek bir renk alır.
- Decal malzemelerinin renk parametreleri: kanal maskeleriyle işaretler nötr bir renkle boyanır.
- Mesh olmayan nesne taslakları (oynanış mantığı, efektler, sesler).
- Yıkılabilir mesh'lerin yok edilmiş halleri: parçalarının yerleri, okunmayan yıkım varlığındadır.
- Gezinme mesh'inin bağlantıları (atlamalar, merdivenler, aşmalar) ve araç katmanları.
- Res'in içine satır içi saklanan ayrıntı seviyeleri (bir bölümde 10 mesh, aletler), skinli ve bileşik mesh'lerin kemikleri ve parçaları ve normaller (yazıcı tarafından hesaplanır).
- Normal, pürüzlülük ve diğer haritalar; bir kesme dışındaki alfa (yarı saydam cam ve decal'ler opak çizilir).
- Arazi delikleri: bir delik yüzey gölgelendiricisi adlandırılmıştır, ama ne okuduğu bulunamamıştır (bkz. [Terrain layers](#terrain-layers)), bu yüzden yükseklik alanı, yürünebilir zeminin altında kaldığı yerde kesilmez.
- Bir malzemenin maskesindeki hangi kanalın hangi tint'i aldığı: gri bir renk haritası, nötr olmayan ilk tint'i alır (bkz. [Dokular ve materyaller](#textures-and-materials)).
- Efektler (`fx/` yolları) ve kablo mesh'leri, sınır kutuları on kilometrelerce uzun; dışarıda bırakılır ve özette sayılır.
- Karartılmış, XOR ile karıştırılmış tablo biçimi.
