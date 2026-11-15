---
title: BeamNG.drive
nav_order: 2
lang: "tr"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Parkur dışa aktarma: BeamNG.drive {#course-export-beamngdrive}

BeamNG dışa aktarması, bir bölümü oyunun onu bağladığı biçimde okur ve Forza dışa aktarmasıyla aynı türde bir dosya yazar: her 512 m'lik kare için pişirilmiş dokulu zemin, yol ve gevşek zemin kendi parçalarında, yerleştirilmiş modeller kategoriye göre ve su.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Kaynaklar: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (kurulum, dosya sistemi, sahne, arazi, materyaller),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (dışa aktarma),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) ve
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (şekiller).
Dosya biçimleri ayrıntılı olarak: [BeamNG dosyaları](reader-beamng.md).

## Turun çerçevesi {#the-laps-frame}

`course` dışa aktarması BeamNG konumlarını **görüntüleyicinin çerçevesinde** bekler:
BeamNG'nin Z-yukarı dünyasında metre cinsinden `(x, z, -y)`. Bu, 3DHeat telemetri kaydedicisinin uyguladığı dönüşümdür. Dışa aktarma turu BeamNG'nin çerçevesine geri çevirir (`(x, -z, y)`), orada çalışır ve her şeyi yeniden görüntüleyicinin çerçevesinde yazar. Bu bir döndürmedir, ayna değil; bu yüzden hiçbir şey ters çıkmaz. BeamNG'nin ham çerçevesinde kaydedilmiş bir tur yerine oturmaz. Bu, başka kaydediciler için denenmedi.

Oyun, `heat3d-lap` dosyası `"game": "beamng"` dediğinde ya da `--game beamng` verdiğinizde BeamNG olarak alınır.

## Kurulumu bulmak {#finding-the-install}

- `--install <klasör>`: `gameengine.zip` ve `content` dosyalarını tutan klasör.
- Aksi halde her Steam kitaplığındaki `steamapps\common\BeamNG.drive` bu iki dosya için kontrol edilir.
- İkisi de işe yaramazsa: "no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip)." (Steam kitaplıklarında BeamNG.drive kurulumu bulunamadı. Klasörünü --install ile belirtin: gameengine.zip dosyasını tutan klasörü.)

## Dosya sistemi {#the-file-system}

BeamNG düz zip arşivleri gönderir ve bunları, bölümlerin başvurduğu tek bir dosya sistemine bağlar (`/art/shapes/...`, `/assets/materials/...`). Dışa aktarma aynı şeyi kurar: şu kaynaklar üzerinde tek bir büyük/küçük harf duyarsız dizin:

1. `gameengine.zip`,
2. `content` altındaki her `*.zip`, `content\vehicles\*` ve adı `art_sound` ya da `audio` ile başlayan arşivler hariç,
3. kullanıcının içeriği, en yeni düzen önce: `%LOCALAPPDATA%\BeamNG\BeamNG.drive` ve `%LOCALAPPDATA%\BeamNG.drive` altında `current` klasörü ve en yüksek numaralı sürüm klasörü. Her birinden: `mods\*.zip`, `mods\unpacked` içindeki her klasör ve kullanıcı klasörünün kendisi, eğer `levels` klasörü varsa.

Sonraki eklemeler kazanır, oyundaki gibi; yani bir mod, geçersiz kıldığı şeyin yerine geçer. Modlar her dışa aktarmada her zaman dahil edilir.

Bir bölümün adlandırdığı yollar oyunun çözdüğü gibi çözülür: olduğu gibi, sonra bir yolu adlandıran dosyaya göre göreli, ve her ikisi için de bir dokunun pişirildiği `.dds`, bir `.dae`'nin derlendiği `.cdae`, ya da `/assets`'e işaret eden bir `.link` dosyası üzerinden.

## Hangi bölüm {#which-level}

`--level` yoksa her bölüm, turun ne kadarının onun üzerinde olduğuna göre puanlanır:

- En fazla 500 tur örneği, eşit aralıklarla kullanılır.
- Her bölümün `TerrainBlock`'u için arazinin kapsamı `.ter` dosyasının ilk beş baytından okunur; böylece tur yakınından bile geçmeyen bir bölüm hiçbir şeye mal olmaz. Örneklerin en az %30'u kapsamın içindeyse yükseklikler okunur. Bir örnek, 1 m aşağıdan 3 m yukarıya kadar olan aralıktaysa arazinin **üstünde** sayılır (`ON_GROUND`), çünkü bir arabanın referans noktası tekerlekleri değil gövdesidir.
- Hiçbir bölüm %50 veya daha fazla puan almazsa, bölümler **yollarına** göre de puanlanır. Bazı bölümler yükseklik haritalarının ötesine geçer (kenarları kaya levhaları olarak devam eder). Bir örnek, bir `DecalRoad` parçasına, yolun yarı genişliği artı 4 m (en az 6 m) içindeyse ve onun 2 m altı ile 4 m üstü arasındaysa yol üzerindedir.
- En iyi bölüm, en az %30 alırsa kazanır. Aksi halde dışa aktarma durur ve en iyi üç bölümü listeler: "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level." (Tur hiçbir kurulu bölümün arazisinin üstünde değil (en iyisi: ...). Bölümü --level ile adlandırın.)

Konsol `on <level>: 87% of the lap lies on its terrain` (ya da `roads`) yazar. `--level`, bölüm klasörü adlarıyla büyük/küçük harf duyarsız eşleşir.

## Bölümü okumak {#reading-the-level}

Bir bölümün neyden yapıldığı, her parça gerçek bölümlerle karşılaştırılarak (ayrıntılar [BeamNG dosyaları](reader-beamng.md) sayfasında):

- **Sahne**: `levels\<name>\main\**\*.level.json` (satır başına bir JSON nesnesi ya da bir JSON dizisi) veya eski bölümler için bir `.mis` dosyası. Araç `TSStatic` nesnelerini (yerleştirilmiş modeller, gizli olanlar atlanarak), `Prefab` nesnelerini (8 seviyeye kadar iç içe, TorqueScript `.prefab` ya da `.prefab.json`), `DecalRoad` nesnelerini (boyanmış yollar), `TerrainBlock`, `WaterPlane`, `WaterBlock` ve `River` okur.
- **Orman öğeleri**: `levels\<name>\forest\*.forest4.json`, `managedItemData.json` kayıtları üzerinden türlendirilmiş. Bariyerler, çitler ve kayalar, ağaçlar kadar sık orman öğesidir.
- **Arazi**: `.ter` yükseklik alanı ve katman haritası.
- **Materyaller**: `levels\` dışındaki her `*.materials.json` ve bu bölüme ait olanlar.

## Koridor ve yol decal'leri {#the-corridor-and-the-road-decals}

Koridor, BeamNG'nin x/y düzleminde turun etrafındaki `--margin` metredir (bkz. [Course export](course-export.md#the-corridor)). Adayları seçmek için `margin + 60 m`lik bir erişim koridoru kullanılır.

**Yol decal'leri** (`DecalRoad`), BeamNG yollarının çoğunun bulunduğu yerdir: arazinin üstüne boyanmış, modellenmemiş. Genişliği erişim koridoruna değen decal'ler, oyunun çizim sırasıyla (azalan `renderPriority`, sonra dosya sırası) alınır ve şeritler olarak yerleştirilir:

- Düğümler (x, y, z, genişlik), yaklaşık her 1 m'de bir **centripetal Catmull-Rom** eğrisiyle ara değerlenir. Düzgün tür, düğümlerin üst üste yığıldığı bir viraj noktasında kendi üstüne döner. Döngü yapan yollar kapanır.
- Her kenar, arazinin yolun kendi yüksekliğinin 1,5 m içinde olduğu yerde arazinin yüksekliğini alır; başka yerde yolun yüksekliğini korur (bir köprüde).
- Malzeme adı bir decal'in neyi boyadığına karar verir:

| Tür | Malzeme adı eşleşir (ilk eşleşme kazanır) |
|---|---|
| lastik izleri | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| kaplama (yalnızca görünüm) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| işaretler | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| gevşek | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| yol | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| kaplama | başka her şey |

## Zemin {#the-ground}

Koridorun içindeki arazi yükseklik alanı üçgenlere dönüşür:

- Merkezi koridorda olan her arazi karesi için bir dörtgen. Katman 255 olan kareler (delikler) atlanır. Her dörtgen iki üçgendir; köşegen, Torque'un arazisinin yaptığı gibi değişir.
- Yükseklikler `position.z + h * maxHeight / 65535`. Normaller yükseklik farklarından gelir.
- Her kare **katmanına** göre sınıflanır: katman adı, arazi malzemesinin zemin modeli ve açıklamasıyla. Döşeli sözcükler onu `road` yapar, `grass/forest/rock/moss/leaves/cliff/stone` `terrain` yapar, gevşek sözcükler `loose` (çakıl ve toprak) yapar. Diğer her şey `terrain`dir.
- Sonra **yol ve gevşek decal'ler**, kapladıkları kareleri çizim sırasıyla geçersiz kılar; yani son çizilen decal karar verir.
- Köşeler her 512 m'lik kareye göre bölünür (`floor(x / 512)`, `floor(y / 512)`), böylece her parça tam olarak bir görsele düşer: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konsol `what the ground is made of` (zemin neyden yapılmış) başlığını, tür başına üçgen sayılarıyla yazar.

### Modellenmiş sürüş yüzeyi {#modelled-driving-surface}

BeamNG'nin pistleri, arazi olduğu kadar modeldir. Bir yarış pisti tek bir mesh olabilir, üstünde çizgileri, lastikleri ve titreşim şeritleri ayrı mesh'ler olarak bulunur. Bu yüzden yol, bordür, kenar, süs ve köprü kategorisindeki yerleştirilmiş modeller sürüş yüzeyi için taranır. Malzeme başına:

| Yüzey | Belirleyen (ilk eşleşme) |
|---|---|
| lastik izleri | adında, zemin türünde ya da açıklamasında `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` |
| işaretler | malzeme adında `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` |
| bordürler | `rumble`, `kerb`, `curb` |
| yol | zemin türü `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, ya da adı `asphalt`, `tarmac`, `track_edge`, `road_surface` içeriyor |
| gevşek | zemin türü `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| kenar | `sidewalk` |
| (modelin kendi kategorisi) | zaten yol, bordür ya da kenar sınıfında olan modeller için |

Bu malzemelerin, koridor içindeki **yukarı bakan** üçgenleri (normal z'si 0,5'in üstünde) modelden çıkarılır ve zemin olur. Pişmiş dokunun içine boyanır ve `ground:road 3_-2 asphalt_light` gibi parçalar olarak yazılır. İşaretler ve lastik izleri yalnızca boyanır. Modelin kalan üçgenleri modelde kalır. Bu modeller hiçbir zaman sadeleştirilmez ya da bütçe yüzünden dışarıda bırakılmaz, çünkü kaba bir pist yanlış bir pisttir.

## Pişirilmiş zemin dokusu {#the-baked-ground-texture}

Zemini olan her 512 m'lik kare, `--texture-size` pikselde (2048 = piksel başına 25 cm) tek bir görsel alır ve oyunun zemini çizdiği gibi çizilir:

1. **Arazi katmanları.** Her piksel için, çevreleyen dört arazi karesinin katmanları çift doğrusal olarak karıştırılır. Her katman, oyunun renklendirdiği gibi renklendirilir: malzemenin **temel haritası**, `diffuseSize` metre boyunca gerilmiş (ya da tüm arazi boyunca), sonra **detay** ve **makro** haritalar gri katmanlar olarak (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 nötr). Varsayılanları sırasıyla her 2 m ve 60 m'de tekrar eder, güçleri 0,5 ve 0,3'tür; malzeme başka bir şey söylemedikçe. Malzemesi olmayan bir katman, yüzeyinin düz rengini alır. Temel harita satır 0 kuzeydir.
2. **Yalnızca arazi üstüne boyanmış yol decal'leri**, çizim sırasıyla, her birinin kendi dokusu, opaklık haritası, tonu ve opaklığıyla, şerit boyunca. Yerleşik oyunlarda asfalt tabanlar için öncelikler 12-16 civarında, işaretler için 10 ve lastikler için 4.
3. **Üstten görülen modellenmiş sürüş yüzeyi**: önce tabanlar, sonra kaplamalar; her biri modelin kendi tekrar eden dokusuyla, bir piksel başına bir texel.
4. **Nesnelerin üzerine de yansıtılan decal'ler** (`overObjects`), en sonda.

`--no-textures` ile hiçbir şey pişirilmez: zemin parçaları düz renkler alır ve modellenmiş işaretler ile lastik izleri **3 cm** kaldırılmış kendi parçaları olur.

## Placed models {#placed-models}

Adaylar, orijini erişim koridorunda olan her `TSStatic`, prefab çocuğu ve orman öğesidir. Bir aday, şeklinin dünya sınırlayıcı kutusu koridora değiyorsa çizilir.

**Kategori**, bölümün kendi açıklamasından ve şeklin yolundan gelir. İlk eşleşen kural kazanır:

| Kategori | Açıklama | Yolu ya da adı içerir |
|---|---|---|
| arka plan (asla çizilmez) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| bordürler | | `kerb`, `curb`, `rumble` |
| yol | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| kenar | `SIDEWALK`, `COBBLESTONE` | |
| ağaçlar (yalnızca `--trees` ile) | `NATURE` | tree, foliage, bush, grass, plant ve benzeri sözcükler |
| kayalar | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| bariyerler | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| tabelalar | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| köprüler | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| altyapı | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| binalar | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| süs | | başka her şey |

**Şekiller** derlenmiş `.cdae` dosyasından okunur ya da bir önbelleğin olmadığı yerde (modlar) Collada `.dae` dosyasından. Okunamayan bir şekil sayılır: `N copies of M models could not be read` (M modelden N kopya okunamadı). `invisible`, `collision` ya da `nodraw` adlı ya da dokulu materyaller hiçbir zaman çizilmez.

**Dokular.** Modeller kategoriye ve materyale göre gruplanır ve `structure:<category> <material>` (ya da `ground:kerbs <material>`) adlı parçalar olur. Bir grup, malzemesinin renk dokusunu en fazla **256 px** olarak alır; ancak UV'leri 0-1 içinde kalıyorsa (köşelerin %98'i -0,02 ile 1,02 arasında). Görüntüleyici dokuları bir atlasa paketler ve bir dokuyu tekrarlayamaz. Dokusu tekrar eden bir grup, dokunun ortalama rengiyle (alfa ağırlıklı, sRGB'de, malzeme tonuyla çarpılmış) çizilir; dokusu yoksa kategori rengiyle.

**Ayrıntı** ortak düzen için [Ayrıntı seviyeleri ve bütçe](detail-budget.md) sayfasında. BeamNG'nin ayrıntı seviyeleri, şeklin `details` alanıdır (en büyük piksel boyutu önce). Bütçe aşılırsa en uzaktaki kopyalar önce gider. Bordürler ve sürüş yüzeyi taşıyan modeller hiçbir zaman sadeleştirilmez ya da dışarıda bırakılmaz.

`--no-placed` yapıları atar ama modellenmiş sürüş yüzeyini tutar. `--trees` ağaç kategorisini ekler.

## Su {#water}

| Kaynak | Şöyle çizilir |
|---|---|
| `WaterPlane` (deniz) | su yüksekliğinde 4 m'lik bir dörtgen, arazinin o yüksekliğe ulaşmadığı her koridor hücresi için |
| `WaterBlock` | tek bir dörtgen, bloğun dönüşümünde yerel z = 0'daki birim kare (yani ölçeği boyutunu belirler), koridora değiyorsa; z = 0'ın bloğun yüzeyi olup olmadığı doğrulanmadı |
| `River` | düğümlerinden geçen bir şerit, koridora değiyorsa |

Tüm su, `water:water` adlı tek bir düz parçadır.

## Çizilmeyenler {#not-drawn}

- Zemin örtüsü (yordamsal çimen).
- Dünyanın kenarına yerleştirilmiş manzara (`backdrop` ve benzerleri).
- Tekrar eden model dokuları; bunlar bir ortalama renk olarak çıkar (yukarıya bakın).
- Skinli mesh'ler (araçlar, karakterler) ve şekiller içindeki decal mesh'leri.

## Kontroller {#checks-behind-it}

Kaynakta belirtildiği gibi, yüklü oyunlarda ölçülmüştür:

- Yol düğümleri, `h * maxHeight / 65535` ile ve satırlar +y boyunca alındığında, incelenen bölümlerde arazinin üstünde 1-2 cm (ortanca) içindedir. `h / 32` ya da diğer eksen sırası onları on ila yüzlerce metre ıskalar.
- Bir yol boyunca zincirlenmiş raylı bölümler `rotationMatrix` satır 0 boyunca uzanır (büyük çoğunluk).
- `.cdae` düğüm döndürmesinin devriği alınmalıdır. Bununla dünya sınırları kaynak `.dae` ile milimetre tam olarak eşleşir. Bilinen, kitaptaki yöntemle ise 38 cm kayar (ortanca).
- Her türden birkaç yüklü bölümde dışa aktarıldı; her biri saniyeler ile dakikalar arasında.
