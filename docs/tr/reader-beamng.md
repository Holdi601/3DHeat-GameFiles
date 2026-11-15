---
title: BeamNG dosyaları
nav_order: 8
lang: "tr"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG dosyaları: seviye arşivleri, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive, düz zip arşivleri dağıtır; bu yüzden tersine mühendislik yapılacak bir konteyner yoktur. İş, bir seviyeyi oyunun yaptığı **gibi** okumaktadır: arşivleri tek bir dosya sistemine bağlamak, sahne dosyalarını izlemek ve arazi ile derlenmiş şekilleri çözmek. Bu okuyuculara [BeamNG.drive](course-beamng.md) parkur dışa aktarımı üzerinden ulaşılır. `identify` bir seviye zip'ini, bir `.cdae`'yi ve bir `.ter`'i de adlandırır; `list` ve `extract` her zip'i alır.

Kaynaklar: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Bağlanmış dosya sistemi {#the-mounted-file-system}

`Files.of_install(game)`, `gameengine.zip`, `content` zip'leri (araçlar ve sesler hariç) ve kullanıcının modları (`mods\*.zip`, `mods\unpacked\*` ve bir kullanıcı `levels` klasörü) üzerinde tek bir büyük/küçük harf duyarsız dizin oluşturur. Sonraki eklemeler, oyunun yaptığı gibi öncekileri geçersiz kılar. Aramalar büyük/küçük harfe bakmaz, çünkü seviyelerin kendi başvuruları arşivlerle bu konuda uyuşmaz (bir `.dae` için `.DAE`). Ayrıntılar [BeamNG.drive](course-beamng.md#the-file-system) sayfasındadır.

`resolve()`, bir yolu oyunun yaptığı gibi bulur: verildiği gibi, onu adlandıran dosyaya göre göreli, `x.png` için `x.dds`, `x.dae` için `x.cdae` (tercih edilen) ve `/assets` içine işaret eden bir `path` değeri olan `x.png.link` JSON dosyası üzerinden.

## Sahne dosyaları {#scene-files}

| Kaynak | Biçim | Okunan |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | satır başına bir JSON nesnesi ya da tek bir JSON dizisi ya da haritası | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | aynı sınıflar; `main\` olmayan eski seviyeler için |
| `*.prefab` / `*.prefab.json` | TorqueScript ya da JSON | çocuklar prefab'a göre yerleştirilir, 8 düzey derine kadar |
| `levels\<name>\forest\*.forest4.json` | satır başına bir örnek | `managedItemData.json` içindeki `TSForestItemData` kayıtlarıyla türlenir (`shapeFile`) |
| `info.json` | JSON | seviyenin başlığı (çeviri anahtarları yok sayılır) |

**Dönüşümler.** `rotationMatrix`, **satırları** nesnenin dünyadaki kendi eksenleri olan dokuz sayıdır. Bir yol boyunca zincirlenmiş bariyer bölümleri satır 0 boyunca koşar (%92), ve yukarı satırı yolun eğimiyle eğilir. Eski prefab'lar `rotation = "x y z degrees"` verir: bu, o açıyla sağ elli bir dönüş (raylı zincirlerin %92'si bununla, %19'u ters yönle hizalanır). Ölçek satırları çarpar ve `position` (ya da `pos`) son satırdır. Bir prefab çocuğunun dönüşümü prefab'ınkiyle birleştirilir. Prefab'ın `groupPosition` değeri bir editör pivotudur ve **çıkarılmaz**: bir vagon prefab'ı, ancak onsuz zemine oturur.

TorqueScript sayıları, bazı paketlenmiş prefab'ların `-0.99563-0.0` gibi, aralık olmadan yazdığı değerler yüzünden esnek bir örüntüyle okunur.

## Arazi: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Metre cinsinden yükseklik: `position.z + h * maxHeight / 65535`; `position`, `squareSize` ve `maxHeight`, `TerrainBlock`'tan (varsayılanlar 0, 1 ve 2048).
- Satırlar +y boyunca koşar. Izgara noktası (i, j), `(position.x + i * squareSize, position.y + j * squareSize)` konumundadır.
- Katman 255 bir delik.

Denetim: üç seviyede yol düğümleri araziye 1-2 cm (medyan) içinde oturur. `h / 32` ya da diğer eksen sırası, onlarca ila yüzlerce metre kayar.

## Malzemeler {#materials}

`levels\` dışındaki her `*.materials.json` ile mevcut seviyenin kendisi, `mapTo`, `name` ve anahtara göre dizinlenir:

| Sınıf | Kullanılan alanlar |
|---|---|
| `Material`, `CustomMaterial` | renk haritası (`baseColorMap`, `colorMap` ya da `diffuseMap`, ilk aşama), renk faktörü, opaklık haritası ve faktörü, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | taban haritası ve `diffuseSize`, ayrıntı haritası ve boyutu ile gücü, makro harita ve boyutu ile gücü, `groundmodelName`, `annotation` |

Görüntüler Pillow ile çözülür (DDS, PNG ve benzerleri), mümkün olduğunda küçültülmüş bir taslakla ve boyuta göre önbelleğe alınarak. Okunamayan bir doku düz renge döner.

## Derlenmiş şekiller: `.cdae` {#compiled-shapes-cdae}

`.cdae`, her Collada dosyasının oyunun kendi önbelleğidir ve MessagePack olarak yazılır. Düzeni **BeamNG tarafından belgelenmiştir** (documentation.beamng.com/modding/file_formats/cdae/) ve okuyucu ona uyar:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Okunanlar: sınırlar, düğümler, nesneler, ayrıntılar (ayrıntı düzeyleri), varsayılan düğüm dönüşleri (`Quat16`) ve öteleme, her mesh'in tepe noktaları, UV'leri, normalleri, renkleri, ilkelleri ve indeksleri ve malzeme adları. Malzeme adları akışın sonunda bulunur, çünkü canlandırılmış bir nesnenin dizileri, belgelenmemiş bir biçimde, onlardan önce gelir.

Belgelenmemiş iki şey, şekillerin inşa edildiği `.dae` dosyalarına karşı çözüldü:

- **Düğüm dönüşleri Torque'undur.** Ders kitabı yöntemiyle okunan bir `Quat16` ters yöne döner. Matrisinin **devrik** alınması gerekir. Bununla, her düğümün dünya sınırları Collada'ya milimetreye kadar uyar. Olmadan, medyanda 38 cm kayar.
- **Birimler ve eksenler zaten uygulanmıştır.** Santimetre ya da Y-yukarı yazılmış bir Collada dosyası, önbellekten metre ve Z-yukarı olarak çıkar.

Ayrıntı düzeyleri, negatif olmayan boyutlu `details` değerleridir, en büyükten başlayarak. Negatif boyutlar çarpışma ve görüş hattı mesh'leridir, asla çizilmez. `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` ya da `imposter` adlı nesneler asla çizilmez. Yalnızca standart ve sıralanmış mesh'ler çizilir. İskelet mesh'leri (karakterler, araçlar) ve çıkartma mesh'leri çizilmez. Üçgen şeritler ve yelpazeler açılır; yüzler, Torque'un kendi sarımının garanti etmediği, saklanan normallerle uyumlu olacak şekilde yeniden sarılır.

Denetim: gösterilen neredeyse her şekil okunur. Diğer ikisi eski bir sürümdür.

## Collada yedeği: `.dae` {#collada-fallback-dae}

`.cdae`'si olmayan şekiller için (modlar ve önbelleği daha eski olan birkaç şekil), Collada dosyası Torque'un içe aktarıcısının okuduğu gibi okunur, aynı yapıya:

- Torque'un adlandırmasından ayrıntı düzeyleri: bir mesh düğümünün sondaki sayısı, onun çizildiği piksel boyutudur (`barrier75`, `barrier40`). Negatif bir sayı ya da `collision`/`Colmesh`/`LOS`/`nulldetail` adı asla çizilmez. Bu kurala uymayan bir şekil tek düzeydir.
- `<unit meter>`'dan birimler; Y-yukarı, Z-yukarıya çevrilir.
- UV'ler önbelleğin kuralına çevrilir (v, görüntüde aşağı doğru koşar).

Aynı dosyaların oyunun kendi `.cdae` dosyalarına karşı denetimi: neredeyse örneklenen tüm sınırlar 1 cm içinde, 583 aynı üçgen sayısıyla, malzemelerin UV'lerinin %94'ü aynı. Kurulu oyun testi, paylaşılan sanat arşivinden en çok 60 şekil çiftinin %90'ının 1 cm içinde uyuşmasını ister.

## Okunmayanlar {#not-read}

- Zemin örtüsü (yordamsal çimen) ve çalışma zamanında üretilen her şey.
- Canlandırılmış diziler ve iskelet bağlama.
- Araçlar ve sesler (asla bağlanmaz).
