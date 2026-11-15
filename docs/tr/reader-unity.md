---
title: Unity
nav_order: 4
lang: "tr"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paketler, mesh'ler {#unity-serializedfile-bundles-meshes}

Unity `SerializedFile` biçimi 22 ve sonrasının (Unity 2020'den 6000'e) **nesnelerini listeler ve mesh'lerini çözer**; `UnityFS` paketlerini açar. Bir Unity parkur dışa aktarımı yoktur.

Kaynaklar: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Komutlar: `identify` (konteynerler ve paketler), `meshes` (yalnızca düz konteynerler).

## Konteyner {#the-container}

Unity bir seviyeyi serileştirilmiş nesne grafikleri olarak dağıtır: `globalgamemanagers`, `sharedassets*.assets`, `resources.assets`, `level*` ve varlık paketleri. Her biri, bir sınıf kimliğiyle etiketlenmiş bir nesne tablosu tutar.

Başlıkta okuma sessizce yanlış gider. İlk on altı bayt, uyumluluk için tutulan dört büyük-endian `uint32`'dir. Biçim 22'de üçü sıfırdır ve gerçek değerler, bir dosya 4 GB'ı aşabileceği için onları izler:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

İkinci `metadata size`, iki `int64` arasındaki bir `uint32`'dir. Üçünün de 64-bit olduğunu varsaymak, sürüm dizgisini dört bayt geç koyar. Yine de dizge benzeri bir şey çözülür ve sonrasındaki her şeyi yanlış yere gönderir. Başlık büyük-endian'dır. Ondan sonraki her şey endianness baytını izler (0, küçük-endian, her masaüstü yapıda).

Başlıktan sonra: motor sürüm dizgisi, platform, tip ağacı bayrağı, tip tablosu (tip başına sınıf kimliği), nesne tablosu (yol kimliği, ofset, boyut, tip) ve harici öğeler (bir işaretçinin başvurabileceği diğer dosyalar).

| Durum | Sonuç |
|---|---|
| biçim 22-30 | okunur |
| biçim 9-21 (Unity 2020 öncesi) | reddedilir: ofsetler eski başlıktadır ve elindeki hiçbir dosya bunu kullanmadı |
| 9-30 dışında | reddedilir |
| gömülü tip ağacı (editör yapıları) | reddedilir: kurulu yapılar bir tane gömmez ve editör yolu uygulanmamıştır |
| konteyner beklenen yere bir paket verilirse | paket okuyucusuna yönlendirmeyle reddedilir |

**Genel bir seri çözücü yoktur.** Kurulu yapılar tip ağacı taşımaz, çünkü şema oyuncunun içine derlenmiştir; bu yüzden her sınıf, o sürüm için bilinen bir düzene karşı ayrıştırılmalıdır. Yalnızca `Mesh` çözülür. Diğer sınıflar adı ve sayısıyla bildirilir (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; diğerleri `class<id>`).

**Doğrulandı:** birçok kurulu oyunda ve milyonlarca nesnede: nesne tablosu veri bölümünü döşemelidir, örtüşme olmadan, nesneler arasında hizalama dolgusu dışında hiçbir şey olmadan ve son nesne dosyanın son baytında bitmelidir. Yanlış okunmuş bir başlık bunu üretemez. Kurulu oyun testi, `*_Data` klasörlerinde bulunan en çok altı `resources.assets` / `sharedassets0.assets` dosyasında bunu yineler.

## Paketler (`UnityFS`) {#bundles-unityfs}

Bir paket, `SerializedFile`'ların sıkıştırılmış bir konteynerdir. Blok listesi ve dizin de sıkıştırılmıştır. Yöntem, bir bayrak sözcüğünün düşük altı bitinde: 0 saklı, 1 LZMA (Unity'nin 5 baytlık başlığı, boyut araya eklenmiş), 2 ve 3 LZ4 / LZ4HC. Biçim 7 ve sonrası başlığı 16 bayta hizalar. `0x80` bayrağı dizini dosyanın sonuna koyar. `UnityWeb`, `UnityRaw` ve `UnityArchive` (5.3 öncesi) tanınır ama okunmaz.

## Mesh'ler {#meshes}

`read_mesh`, bir `Mesh` nesnesini konumlara, normallere, ilk UV kümesine ve üçgenlere çözer; Unity 2019+'ın yazdığı sırayla: ad, alt ağlar, karıştırma şekilleri (atlanır), bağlama pozları ve kemik verisi (atlanır), sıkıştırma ve okunabilirlik bayrakları, indeks tamponu, tepe noktası kanalları ve tepe noktası verisi, sıkıştırılmış mesh bloğu, yerel sınır kutusu ve akış bilgisi.

- **Harici tepe noktaları.** Kodun çoğu geometri, konteynerin yanındaki bir `.resS` dosyasında yaşar. Araç bunu konteynerin klasöründen okur (saklanan `archive:/...` yolunun yalnızca dosya adı kullanılır). Eksik bir `.resS` bir hatadır, boş bir mesh değil.
- **Akışlar ve kanallar.** Kanallar, her özniteliğin hangi akış, ofset, biçim ve boyuta sahip olduğunu söyler. Akışlar art arda paketlenir, her biri 16 bayta dolgulu; bir akışın başlangıcı, önündeki adımlardan biriktirilerek bulunur. Biçimler: float32, float16, unorm/snorm 8 ve 16 (normalleştirilmiş) ve düz tamsayılar.
- **Topoloji.** Yalnızca üçgenler (topoloji 0). Şeritler, dörtgenler ve çizgiler reddedilir, çünkü yanlış bir dönüşüm gerçek geometri gibi görünür.
- **Sıkıştırılmış mesh'ler** (kuantize edilmiş farklar) reddedilir: "mesh '...' is stored compressed; that encoding is not implemented".

### Öz denetim {#the-self-check}

Bir yapıyı yanlış sırada okumak hata vermez. Makul görünen sayılar üretir. Bu yüzden çözülen her mesh, Unity'nin **sakladığı sınır kutusuna** karşı denetlenir; bu kutu editör tarafından gerçek tepe noktalarından hesaplanmıştır. `aabb_matches()`, çözülen kutunun köşeleri, saklanan kutunun boyutunun %2'si içindeyse geçer. `meshes` her satırda `ok` ya da `BOUNDS DISAGREE` yazar.

**Doğrulandı:** birkaç oyundan örneklenen mesh'ler, sınırları uyuşarak çözülür. Kurulu oyun testi denetimi kurulu konteynerlerde yineler.

## Uygulanmayanlar {#not-implemented}

- 2020 öncesi biçimler.
- Sıkıştırılmış mesh'ler.
- `Mesh` dışındaki her sınıf: sahne grafiği, dönüşüm ya da malzeme yok, bu yüzden mesh'ler kendi yerel uzaylarındadır.
- Bir pakette `meshes`. Paket okuyucusu Python'da vardır (`UnityBundle.serialized_files()`), ama komut düz bir konteyner alır.
