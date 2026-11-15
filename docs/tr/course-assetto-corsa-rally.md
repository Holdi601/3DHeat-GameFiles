---
title: Assetto Corsa Rally
nav_order: 3
lang: "tr"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Parkur dışa aktarma: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally, Unreal Engine 5 üzerine kuruludur (5.6.1, değiştirilmiş bir sürüm) ve içeriğini IoStore konteynerleri olarak dağıtır. Bunların hiçbiri şifreli değildir. Dışa aktarım, etabı ve eksen yönünü turdan bulur. Etabın kendi zemin karolarını yazar; bunlar yol ve arazi olarak ayrılır ve etabın pişirilmiş zemin renginden dokulanır. Diğer modelleri kategorilerine göre düz renklerle yerleştirir.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Kaynaklar: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (kurulum, etaplar, yerleşim),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (dışa aktarım).
Altındaki Unreal okuyucuları [Unreal 5 IoStore](reader-unreal-iostore.md) sayfasında,
sıkıştırma açma ise [Oodle](reader-oodle.md) sayfasında anlatılır.

**Durum:** kurulu oyunda, her etapta rastgele bir karede üretilen turlarla denendi; doğru etabı ve kareyi her seferinde buldu. Oyunun kendi kaydettiği hiçbir tur henüz bu süreçten geçmedi.

## Kurulumu bulmak {#finding-the-install}

- `--install <klasör>`: oyun klasörü, ya da `Content\Paks`, ya da `.utoc` dosyaları içeren herhangi bir klasör. Araç sırayla `<klasör>`, `<klasör>\acr\Content\Paks`, `<klasör>\Content\Paks` klasörlerine bakar.
- Aksi halde her Steam kütüphanesindeki `steamapps\common\Assetto Corsa Rally` aynı biçimde denetlenir.
- Bu klasördeki her `.utoc` tek bir depo olarak açılır. Açılamayan konteynerler atlanır. Hiçbiri açılmazsa şu mesaj çıkar: "no readable IoStore containers in ...".

Blokların çoğu Oodle ile sıkıştırılmıştır ve makinede bir kütüphane aranır (her Steam kütüphanesi taranır). Bkz. [Oodle](reader-oodle.md).

Tur dosyası `"game": "assetto-corsa-rally"` (ya da `acrally`) dediğinde ya da `--game acrally` verdiğinizde oyun AC Rally sayılır.

## Etap nedir {#what-a-stage-is}

Bir etap bir **World Partition** haritasıdır:

- `Content\Levels\<Stage>.umap` uzak araziyi yerleştirir.
- `Content\Levels\<Stage>\_Generated_\*.umap` altındaki işlenmiş hücreler geri kalan her şeyi yerleştirir.

Bir seviye, ortam klasörü `Content\Environments\<Stage>\` içinde bir `MeshesTrack` klasörü varsa etap sayılır. Araç karoların adlarına bakmaz; bir etap karolarını harita adı yerine bir kasabanın adıyla adlandırmış olabilir. `--level`, bu harita adlarıyla büyük/küçük harf duyarsız eşleştirilir. Yanlış bir ad, var olan etapların listesini verir.

Bir **arazi yoktur**. Zemin statik modellerden oluşur:

| Karolar | Yol | Olur |
|---|---|---|
| parkur karoları, yaklaşık 175 m, ikiye bölünmüş | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` ve `..._Terrain_k` | `ground:road` ve `ground:terrain` (bölünmemiş bir parkur karosu, örneğin donmuş bir göl, tamamen yoldur) |
| uzak arazi, 2 km'lik karolar | `.../MeshesTerrain/...` | `ground:terrain` |

## Yerleşimleri okumak {#reading-the-placements}

Bir mesh'i yerleştiren şey bir `StaticMeshComponent`'tir: onun `StaticMesh`'i ve `RelativeLocation`, `RelativeRotation`, `RelativeScale3D` değerleri. Bunların her biri bağlı olduğu bileşene (`AttachParent`) göredir; zincir aktörün köküne, yani dünyaya kadar uzanır.

- Özellikler **sürümsüzdür**: adlarıyla değil, sınıfın özellik listesindeki konumlarıyla saklanırlar. [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) içindeki şemalarla okunurlar (bkz. [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Bileşenin şablonuna (bir Blueprint'teki arketipine) eşit bir değer saklanmaz. Bu yüzden şablonun değerleri önce, özyinelemeli olarak okunur ve bileşenin kendi değerleri onların üzerine yazılır.
- `bVisible = 0` ya da `bHiddenInGame = 1` olan bileşenler atlanır. Yolu `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` ya da `_hlod` içeren meshler de atlanır.
- Dönüşler Unreal'in `FRotationMatrix` yöntemiyle yapılır (pitch, yaw, roll, derece cinsinden).
- Yinelenenler (aynı mesh, aynı dönüşüm, 0,1 cm hassasiyetle) bırakılır.
- Okunamayan bileşenler nedenlerine göre sayılır ve bildirilir, örneğin:
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`

**Örnekleme bileşenleri** (ormanların neredeyse hepsi) yalnızca `--trees` ile okunur. Bu sürüm bu sınıfları motorun başlık dosyalarının ötesinde yeniden düzenlemiştir; bu yüzden özellikleri okunmaz. Bunun yerine:

- mesh, paketin bağımlılık tablosundan alınır; burada her böyle bileşen tam olarak bir statik mesh listeler,
- örnekler, özelliklerden sonraki yerel bloktan alınır (`[1][1][128][count]`, ardından `count` adet 4x4 çift duyarlıklı matris),
- bileşenin aktörünün kökünde durduğu varsayılır; orman aktörleri bitkileri bu şekilde yerleştirir.

Koordinatlar Unreal'in koordinatlarıdır: santimetre, Z yukarı, X ileri, Y sağ, sol elli bir çerçeve.

## Hangi etap, hangi yönde {#which-stage-and-which-way-round}

Telemetrinin çerçevesi belgelenmemiştir, bu yüzden varsayılmaz. Uydurulur:

- **Sekiz aday çerçeve.** Unreal Z (cm) çarpı 0,01, turun yüksekliği (y) olur. Unreal X ve Y, turun x ve z'si olur; yer değiştirmiş ya da değiştirilmemiş, her biri iki işaretten biriyle, hepsi metre için 0,01 ile ölçeklenmiş.
- **Yol yüksekliği ızgarası.** Her etap için her yol karosu (en kaba ayrıntı düzeyinde) yerleştirilir ve her 2 m'lik hücre için en yüksek yol köşesi tutulur.
- **Puanlama.** En fazla 400 tur örneği eşit aralıklarla alınır ve her çerçeveyle Unreal uzayına taşınır. Bir örnek, çevresindeki 3 x 3 hücrede, örneğe en yakın yol yüksekliği örnekten 1 m aşağı ile 3 m yukarı arasındaysa yolda sayılır (`ON_ROAD`). Puan, yolda olan örneklerin oranıdır.
- **Kazanan.** En iyi etapta en iyi çerçeve, en az %50 puan alırsa. Aksi halde dışa aktarım durur: "the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level."
- **Adını taşıyan tur.** Tur dosyasında `track` alanı varsa, adı kabaca eşleşen bir etap (yalnızca harf ve rakamlar, biri diğerini içerir) önce ve tek başına denenir; yalnızca en az %80 puan alırsa kabul edilir. Aksi halde her etap denenir.
- `--level` verildiğinde yalnızca o etap, sekiz çerçevenin hepsinde denenir.

Konsol şuna benzer bir şey yazar: `on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Her şey sonra **turun çerçevesinde** yazılır: metre, Y yukarı. Bir dönüşüm aynalıyorsa üçgenin sarım yönü ters çevrilir, böylece yüzler hâlâ doğru yöne bakar.

## Zemin {#the-ground}

- Koridor, turun kendi x/z düzleminde, etrafındaki `--margin` metredir.
- Her zemin karosu en ince ayrıntı düzeyinde yerleştirilir; yalnızca koridora uzanan üçgenler tutulur.
- Üçgenler türe (yol ya da arazi) ve Unreal uzayında 512 m'lik kareye göre (51.200 cm) gruplanır; her karenin kendi görüntüsü vardır. Parçalar `ground:road 1_-4` gibi adlandırılır. UV'ler `(unreal_xy - square_origin) / 51200`.
- Normaller, tüm dosya için üçgenlerden hesaplanır.

### Zemin dokusu {#the-ground-texture}

`--no-textures` verilmezse her kare iki kaynaktan, `--texture-size` pikselde boyanır:

1. **Pişirilmiş zemin rengi.** Etap haritasındaki `RuntimeVirtualTextureComponent` (kutusunun köşesi `RelativeLocation`, boyutu `RelativeScale3D`, dönüşsüz) oyunun pişirdiği zemin rengi olan akışlı bir **sanal doku**ya işaret eder. Karenin bölgesi, istenen boyuta en yakın piksel düzeyinde okunur. Bu, etaba göre piksel başına 13 ila 59 cm'dir.
2. **Uydu görüntüsü**, sanal dokunun siyah bıraktığı her yeri doldurur. Etabın ortam klasöründeki `sat*_(b|bc|c|basecolor)` dokusudur ve en çok 4096 px okunur. Yerleşimi, uzak arazinin ilk UV kanalının dünya x ve y'sine karşı en küçük kareler yöntemiyle bulunur. Uyum, %95'lik dilimde 0,01'e kadar doğrusal olmalıdır; aksi halde görüntü kullanılmaz. Uzak arazinin UV'leri 1'i aşarsa (malzemenin onları tekrarlaması durumunda), eşleme bir kez sığana kadar yarıya indirilir.

Konsol hangisinin kullanıldığını söyler, örneğin `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. İkisi de olmayan bir etap düz renklerle çizilir.

## Yerleştirilmiş modeller {#placed-models}

Zemin karosu olmayan her yerleşim, mesh yoluna göre sınıflandırılır (ilk eşleşme kazanır):

| Kategori | Mesh adı (ağaçlarda yol) şunu içerir |
|---|---|
| ağaçlar (yalnızca `--trees` ile) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| kayalar | `rock`, `cliff`, `boulder`, `stone` |
| bordürler | `kerb`, `curb` |
| bariyerler | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| tabelalar | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| binalar | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| altyapı | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| donatılar | bunlar dışında her şey |

- Bir kopya, orijini ulaşım koridorundaysa (`margin + 60 m`) ele alınır ve sınır kutusu gerçek koridora değiyorsa çizilir.
- Ayrıntı düzeyleri [Ayrıntı düzeyleri ve bütçe](detail-budget.md) sayfasını izler: önce mesafe bantları, sonra en pahalı modeller bütçeye sığana kadar bir kademe düşer. En kaba düzeyler bile bütçeyi aşarsa, en uzak kopyalar BeamNG'de olduğu gibi, sığana kadar bırakılır. Bordürler tam ayrıntıda kalır ve asla bırakılmaz. Özet şunu yazar: `placed on it (N triangles of a B budget)`, kopyalar bırakıldıysa da `N copies left out to fit the budget, the furthest from the driving first`.
- Her kategori, düz renkte tek bir parçadır: bordürler için `ground:kerbs` (Forza ve BeamNG'de olduğu gibi sürüş yüzeyi sayılır), geri kalanlar için `structure:<category>`:

| Kategori | Renk (doğrusal RGB) |
|---|---|
| bariyerler | 0.55, 0.52, 0.48 |
| tabelalar | 0.75, 0.72, 0.65 |
| binalar | 0.62, 0.58, 0.52 |
| altyapı | 0.48, 0.48, 0.50 |
| kayalar | 0.45, 0.43, 0.40 |
| donatılar | 0.55, 0.45, 0.35 |
| ağaçlar | 0.20, 0.32, 0.14 |
| bordürler | 0.70, 0.25, 0.22 |

Okunamayan statik meshler (iskelet meshleri, yalnızca Nanite meshleri, satır içi saklanmayan seviyeler) sayılır: `N meshes could not be read`.

## Yapılan denetimler {#checks-behind-it}

Kaynakta belirtildiği gibi, kurulu oyunda:

- Her içindekiler tablosu okunur (sürüm 8).
- Her etabın her hücresi açılır; her statik mesh ve sahne bileşeni, tam olarak sınıfının sabit yerel kuyruğunda biten şekilde çözülür.
- Neredeyse her örneklenen statik mesh çözülür (kalanlar iskelettir). Bir yol karosunun çözülen kapsamı, sakladığı sınırlarla eşleşir.
- Bir uydu görüntüsünün mip düzeyleri, toplu girdilerinin boyutlarının tam olarak aynısıdır.
- Bir sanal doku parçasının karoları bayta kadar hesaba katılır; yol karoları, gösterdiği yolun üzerine düşer.

## Bilinen eksikler {#known-gaps}

- Örneklenmiş bileşenlerin kendi özellikleri okunmaz (yukarıya bakın). Yerleşimleri aktör kökünü varsayar.
- Çalışma zamanında PCG ile üretilen ormanlar dosyalarda saklanmaz ve dışa aktarılamaz.
- Spline meshleri (görünmez yeniden doğma duvarları), çıkartma bileşenleri ve yerleştirilmiş modellerin kendi dokuları çizilmez. Modeller düz renklidir.
- `--season` etkisizdir.
- Bir oyun yaması özellik yuvalarını kaydırabilir. Okuyucu yanlış okumak yerine hata verir ve parkur kaç bileşenin başarısız olduğunu bildirir.
