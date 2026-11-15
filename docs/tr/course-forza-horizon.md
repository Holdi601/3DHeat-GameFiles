---
title: Forza Horizon
nav_order: 1
lang: "tr"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Parkur dışa aktarma: Forza Horizon {#course-export-forza-horizon}

Forza dışa aktarması, parkuru doğrudan oyunun ForzaTech arşivlerinden okur: yol, kenar ve çimen birbirinden ayrılmış arazi; oyunun kendi zemin haritalarından pişirilmiş bir zemin dokusu; ve her yerleştirilmiş model kendi dokusuyla (kenar taşları, bariyerler, lastik duvarlar, tabelalar, süsler, binalar). Ayrıca oyunun yarışlarından hangisinde sürüldüğünü bulur ve o yarış için oyunun verdiği şeyleri ekler (olay katmanı: bariyerler, çadırlar, portallar, tribünler, bayraklar) ve sürüşün geçtiği her mekânın zemini, örneğin bir stadyumun zemini.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Kaynaklar: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Kapsayıcı biçimlerin kendisi [ForzaTech](reader-forzatech.md) sayfasında.

## Kurulu oyunu bulmak {#finding-the-installed-game}

Kimsenin `D:\Games\steamapps\common\<Forza>\media\Tracks\<map>` gibi bir yolu elle yazması gerekmez; yol kendiliğinden bulunur:

1. **Steam kitaplıkları.** Steam'in `config\libraryfolders.vdf` dosyası `C:\Program Files (x86)\Steam` ya da `C:\Program Files\Steam` içinden okunur ve içindeki her `"path"` girişi bir kitaplıktır. Her kitaplığın `steamapps\common` klasörü aranır.
2. **Microsoft Store.** Varsa `C:\XboxGames` aranır. Orada oyun bir kademe daha aşağıdadır, `<game>\Content` içinde.
3. Bir **oyun klasörü**, `media\Tracks` klasörü olan, adı ne olursa olsun, bu klasörlerin herhangi bir alt klasörüdür.
4. Bir **parkur klasörü**, `media\Tracks` altında `GeoChunk0.minizip` dosyasını tutan herhangi bir klasördür. Adına göre değil içeriğine göre sayılır; bu yüzden hiç görülmemiş bir adla olan parkur da bulunur.

Oyun başka bir yerdeyse, parkur klasörünü `--track` ile verin; bkz. [Sorun giderme](troubleshooting.md#finding-the-game) ("no installed Forza track found" - kurulu bir Forza parkuru bulunamadı).

`--track <klasör>` tüm bunları atlar.

Bir parkur klasörü, dışa aktarmanın okuduğu dosyaları tutar:

| Dosya | Ne işe yarar |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arşivler: her model, doku ve yerleşim dosyası, içinde hiç ad olmadan |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | arşiv girişi başına bir satır, giriş sırasıyla: adların tek kaynağı |
| `AssetManifest.xml` | parkurun gönderdiği her doku, malzemelerin ona başvurduğu karma ile |

## Hangi parkur {#which-track}

Bir oyun birden çok parkur klasörü gönderir (açık dünya haritası, bir iki garaj). Doğru olanı **ada göre değil koordinatlara göre** seçilir:

- Turun sınırlayıcı kutusu, `--margin` ile genişletilmiş, sorudur.
- Her parkur klasörü için dört `ChunkContentsMiniZip*.txt` manifesti bir arşiv açılmadan, metin olarak okunur. Her arazi karesinin adı (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) ızgara konumunu taşır. Araç, kutunun içine düşen ayrı arazi karelerinin sayısını sayar.
- En çok kareye sahip parkur kazanır. Hiçbirinde yoksa dışa aktarma durur: "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them." (Kurulu parkurların hiçbirinde x ..., z ... için arazi yok. Bunlar, telemetrinin bildirdiği gibi oyunun kendi metreleridir.)

Tam bir parkur bir saniyenin altında yanıt verir. Ada göre eşleşme yanlış haritayı seçebilir; yanlış bir harita, doğru olan kadar inandırıcı görünür.

Konsol `on <track>, in <game folder>` yazar.

## Which race {#which-race}

Oyun her yarışını, bir numarası olan bir rota olarak gönderir: **rota kimliği**. Her rotaya ait iki dosya vardır:

| Dosya | Ne tutar |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | yarışın YZ sürüş çizgisi: `0x60` baytından itibaren, nokta başına 56 baytlık bir düğüm; düğüm sayısı `0x24`te; her düğüm kendi konumuyla (x, y, z) oyunun metrelerinde başlar |
| `media\Stripped\gs\<map>\routedefinitions.zip` | yarış başına bir `route<id>_<map>.rtd`: yarışın dünyaya neyi eklediğini ve neyi kaldırdığını listeleyen düz XML (bkz. [Yarışın kendi katmanı](#the-races-own-layer)) |

Tur, kutusu turunkiyle örtüşen her YZ çizgisiyle karşılaştırılarak bir rotaya eşlenir:

- Her tur örneğinden, çizgideki en yakın noktaya uzaklık; ve çizginin her noktasından, en yakın tur örneğine uzaklık.
- İki ortanca değer toplanır. Toplamı **30 m**'nin (`MATCH`) altında olan ve en küçük toplamı veren rota kazanır.
- İki yön de gerekir: kısa bir sprint, aynı yolu kullanan uzun bir rotanın boyunca uzanır; uzun bir tur ise kısa bir rotayı kapsar.

Konsol `the game's route <id> (driven line within <n> m of it)` (oyunun rotası <id>, sürülen çizgi <n> m içinde) yazar ya da hiçbir rotanın eşleşmediğini. Eşleşme yoksa yalnızca serbest dolaşım dünyası yerleştirilir.

## Arazi {#terrain}

Arazi nasıl bulunur (`forzaterrain.py` içinde):

- Manifestler arazinin bir uzamsal dizin olarak adını verir:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- İki sayı, **1023 adımla** ilerleyen ızgara koordinatlarıdır ve her ızgara adımı bir **512 m**'lik karodur. `x-2046` karesi `-2046 / 1023 = -2` demektir; bu da `-2 * 512 = -1024` m'de başlar. Adları metre olarak okursanız her arama iki katı kadar ıskalar ve yine de arazi döndürür, ama haritanın yanlış bir yerinden.
- Bir kare üç kez görünebilir: düz, `_cb` ve `_ul`. Üçü de aynı zemini kaplar. Kare başına bu sırayla tercih edilen tek biri alınır; çünkü hepsini birleştirmek geometriyi üç katına çıkarır, çakışan yüzeylerle.
- Bir kare yalnızca, koridoru da kutusu da değiyorsa okunur. Koridora dokunmayan bir kare hiçbir zaman açılmaz.
- Seçilen karenin her `.modelbin` dosyası yalnızca **ayrıntı seviyesi 0**'da çözülür. Bir kare aynı zemini kaplayan dört seviye taşır; hepsini dışa aktarmak aynı metrekareyi dosyada dört kez koyardı.
- Her mesh kendi dünya ölçeğini ve sapmasını taşır; böylece her kare, oyunun koyduğu yere, örnek dönüşüm olmadan oturur. Ayak izi kutuyla örtüşen üçgenler tutulur, sonra yalnızca koridora uzananlar.
- Okuyucunun reddettiği bir biçimdeki bir mesh atlanır ve sayılır (`N meshes could not be read`), böylece zayıf bir sonucun nedeni görünür.

Arazi özeti vertex sayısını, üçgen sayısını, mesh sayısını, kare sayısını ve x/y/z aralığını yazar.

### Yol, kenar, arazi, işaretler, su {#road-verge-terrain-markings-water}

Malzeme adları yolun nerede olduğunu söyleyemez. Bir pistin çevresinde zeminin %94'ü bir yol gölgelendirici malzemesi kullanır, çünkü yolun yakınındaki arazi onunla çizilir ve gölgelendirici her pikselde asfalt mı çim mi olduğuna karar verir. Bu yüzden:

| Tür | Belirleyen |
|---|---|
| yol şeridi | **vertex düzeni**: yol şeritleri, ikinci bir UV kümesi (kanal 1) taşıyan tek zemindir; üç vertex'inin hepsinde bu olan bir üçgen yoldur |
| asfalt ile kenar | bir yol şeridinin içinde, kare başına **asfalt maskesi** üçgenin merkezinde: 0,5 ve üzeri `road`, daha az `verge` |
| işaretler | malzeme adı `whiteline`, `yellowline` ya da `decal` ile eşleşir |
| lastik izleri | malzeme adı `tyremark` ya da `skid` ile eşleşir (işaretlerden önce denetlenir, çünkü lastik izleri `tyremark_decal_*` olarak gönderilir) |
| su | malzeme adı `water`, `lake`, `river`, `paddy`, `ocean` ya da `sea` ile eşleşir |
| arazi | başka her şey |

Bir pistin kaydedilmiş turlarında ölçüldüğü gibi örneklerin neredeyse tamamı yol şeridi üçgenlerine düşer ve kenar maskeyle ayrıldıktan sonra büyük çoğunluğu asfalt kısmına.

Asfalt maskesi yalnızca zemin dokuları pişirildiğinde vardır. `--no-textures` ile ya da bir karenin haritaları eksikse, yol şeritleri bütün olarak `road` olarak kalır ve hiçbir kenar ayrılmaz. Eksik haritalar ayrıntıya mal olur, geometriye asla.

### Boyalı katmanlar kaldırılır {#painted-layers-are-lifted}

Şerit işaretleri ve lastik izleri, yolun tam içinde yatan kendi üçgenleri olarak gönderilir. Oyun onları bir derinlik sapmasıyla çizer. Oldukları gibi çizilirse yol ve boya her piksel için çatışır. Dışa aktarma her işaret ve lastik izi parçasına kendi vertex kopyasını verir ve bunu yüzey normali boyunca **5 cm** (`DECAL_LIFT`) kaldırır; böylece altındaki yol da kalkmaz.

### Normaller {#normals}

Arazi normalleri arşivden gelir. Normalin x'i, konumun dördüncü kısa sayısı olarak saklanır; y ve z ise `NORMAL` özniteliğinde (bkz. [ForzaTech](reader-forzatech.md)). Çıkarımdaki herhangi bir vertex'te normal yoksa, tüm zeminin normalleri bunun yerine üçgenlerden hesaplanır.

## Zemin dokusu {#the-ground-texture}

Her arazi karesi, 512 m'lik karesini kaplayan üç harita gönderir; beş çözünürlükte (`_quality1` ile `_quality5`, en büyüğü 2.048 px, yani piksel başına 25 cm):

| Harita | Dosya adı deseni | Ne tutar (ölçüldüğü gibi) |
|---|---|---|
| ana | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detay normali (x, z). A: asfalt üzerinde ve pürüzlü zeminde daha düşük |
| alt | `submap_x<X>_z<Z>_x<season>x_diff` | katman ağırlıkları. B: asfaltta yüksek (sürülen çizgide 239, yanında 165) |
| parlaklık | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: asfaltta düşük (147'ye karşı 215). B: ormanlıkta yükselir |

Bunların hiçbiri renkli bir fotoğraf değildir. Oyunun arazi gölgelendiricisinin malzeme katmanlarını karıştırdığı girdilerdir ve bu katmanlar çözülmez. Bu yüzden pişirilmiş doku **bir yorumdur, oyunun görünümünün kopyası değil**. Her tür zeminin *nerede* olduğunu, 25 cm'de tutar ve sabit renklerle boyar:

| Zemin | Doğrusal RGB | Ağırlık |
|---|---|---|
| çim (kısa, pistin yakınında) | 0,30, 0,44, 0,18 | temel |
| kaba (daha dışarıda) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| ormanlık | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Asfalt için iki harita da uyuşmalıdır. Biri tek başına kalırsa, blok sıkıştırmasının halka yaptığı yerlerde çimenin içinde gri benekler kalır. Sonuç, ana haritanın detay normaliyle sabit bir ışığa karşı gölgelendirilir (`0.55 + 0.6 * lambert`), böylece bordür kenarları, şevler ve tekerlek izleri kabartma gibi okunur; 8 bitlik sRGB olarak yazılır.

Yönelim: piksel satırı 0, karonun **kuzey** kenarıdır (en büyük z), sütun 0 ise **batı** kenarı (en küçük x). Bu, kaydedilmiş turların sekiz yoldan tümüyle asfalt maskesine yansıtılmasıyla bulundu: bir karenin çevrilebileceği ya da döndürülebileceği sekiz yoldan tam biri onları asfalta düşürür. Koordinatlar buradan çıkar: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Haritalar, 5. kaliteye kadar mevcut en iyi çözünürlükte okunur ve ana haritanın boyutuna yeniden örneklenir. Renk görseli `--texture-size`'tan büyükse, Lanczos filtresiyle o boyuta küçültülür. Asfalt maskesi her zaman tam çözünürlükte tutulur, çünkü geometriye karar verir. `--season`, `x<season>x` haritalarını seçer. O mevsim için haritası olmayan bir kare düz renklerle çizilir ve konsol `N without maps` yazar.

## Yerleştirilmiş modeller {#placed-models}

Arazinin kendi dünya konumu vardır. Başka hiçbir şeyin yoktur. Bir modelin her kopyasının nerede durduğu, her kategori ve uzamsal hücre için bir `.pgeo` yerleşim dosyasında kaydedilir:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Kayıt düzeni [ForzaTech](reader-forzatech.md#placement-files-pgeo) sayfasındadır.

### Ne okunur {#what-is-read}

- Yerleşim dosyaları **ada göre** süzülür: yoldaki hücre boyutu ve hücre konumu hücrenin karesini verir (`x * size` ile `(x + 1) * size` arası), ve yalnızca turun kutusuyla örtüşen, istenen bir kategorideki hücreler açılır.
- Varsayılan kategoriler: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` `trees`, `bushes` ve `smashables` ekler. Bunlar hiçbir zaman okunmaz: `grasstemplate`, `crowdtemplate` ve `cwdspline` (çim ve seyirciler: oyun bunları canlı sprite'lar olarak çizer, geometrisi yoktur).
- Her dosya bir **katmana** aittir; katman adı `c<size>_<category>_` sonrasından okunur. Bir ayrıntı seviyesi sözcüğü (`do`, `so`, `ulc`, `ulp`, `cwd`) ve isteğe bağlı bir bölüm numarası serbest dolaşım dünyasıdır. Başka her şey, oyunun açtığı bir katmandır: bir çalışma zamanı katmanı (`rt_0`), bir etkinlik (`_tag_<name>_`), bir toplanabilir, `evolving` altındaki her şey. Rota adı veren bir katman (`rt_x<id>`, örneğin `rt_x1023_x2201`) yalnızca o yarışlara aittir ve yalnızca tur o yarışlardan biriyle eşleştiyse okunur. Bkz. [Açılan katmanlar](#switched-on-layers).
- Bir kopya, konumu kutunun içindeyse ve koridorun içindeyse tutulur. Tam tekrarlar (aynı konum ve yönelim, milimetreye kadar; komşu iki hücrede de listelenen) birleştirilir.
- **Bordürler**, model adı `road_gen_rum` ile başlayan süslerdir (titreşim şeritleri). `ground:kerbs` olarak yazılırlar; hiçbir zaman sadeleştirilmezler ve dışarıda bırakılmazlar, çünkü bir tur onlara göre ölçülür.

| Kategori | Parça | Yedek renk (doku yoksa) |
|---|---|---|
| bordürler | `ground:kerbs` | 0,60, 0,12, 0,10 |
| bariyerler | `structure:barriers` | 0,50, 0,50, 0,50 |
| süsler | `structure:props` | 0,45, 0,35, 0,25 |
| tabelalar | `structure:signs` | 0,70, 0,70, 0,70 |
| binalar | `structure:buildings` | 0,55, 0,52, 0,48 |
| altyapı | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| köprüler | `structure:bridges` | 0,45, 0,45, 0,45 |
| kayalar | `structure:rocks` | 0,30, 0,28, 0,25 |
| kırılabilirler | `structure:smashables` | 0,12, 0,22, 0,06 |
| ağaçlar, çalılar | `structure:trees` | 0,10, 0,20, 0,05 |

### Modelin geometrisi {#the-models-geometry}

Yerleştirilmiş `<model>_3D` adı, `<model>_cluster###.i.modelbin` model dosyalarına başvurur (on ikiye kadar). Her üçgen, ait olduğu ayrıntı seviyelerinin bir maskesini taşır:

- Bir modelin seviyeleri, o seviye için açıkça işaretlenmiş üçgenleridir. Seviyeler 0'dan başlayarak ardışık gider, en ince önce.
- `0xFFFF` ile işaretli üçgenler (her seviye) kırılabilir parçalardır; örneğin bir bariyerin direkleri ya da bir lastik yığınının tek tek lastikleri. Model tümüyle bir parçaya ayrılınca oyun bunları onun yerine çizer. Yalnızca açıkça işaretli bir seviyesi olmayan bir model için kullanılırlar.
- Malzeme gölgelendiricisi projeksiyonlu bir **decal** olan alt mesh'ler dışarıda bırakılır.

Her kopya konumu, kaydındaki x ve y eksenleriyle (z = x çarpı y) ve ölçeğiyle yerleştirilir. Normaller ölçeğin tersiyle dönüştürülür.

### Hangi doku {#which-texture}

Bir malzeme dokularını adlandırmaz. Onları karmalar olarak listeler ve parkurun `AssetManifest.xml` dosyası her karmayı (`SourceHash`) bir doku adına eşler. Yalnızca `<Textures>` bölümü okunur; bu, on megabayt olabilen bir dosyada `</Textures>` görülene dek okumayı durdurur. Sonra:

1. `0x88B483AA` yuvası, standart çevre gölgelendiricisindeki temel renktir (örneklenen her malzeme). Malzeme orada bir doku bağlarsa o kullanılır.
2. Aksi halde dokunun kendi türü karar verir; bu, GUID'sinden önceki sözcüktür: `_bclr_`, sonra `_diff_`, sonra `_colour_`.
3. Zemin haritaları (`mainmap`, `submap`, `autogloss`) ve renk paletleri (`tint`, `worldtint`) hiçbir zaman bir modeli renklendirmez.

Yani bir model, modelin adına benzeyen bir dokuya göre değil, malzemesinin bağladığı dokuyla renklendirilir. Örneğin `bar_rur_armco_crct_02_c`, `..._02_a`'nın dokusunu kullanır.

Doku, arşivlerden, en az **256 px** genişliğindeki en küçük çözünürlükte okunur (`MODEL_TEXTURE`), büyükse 256'ya küçültülür ve `.glb` içinde RGB JPEG olarak saklanır. Dört metrelik bir bariyerin 256 pikselde rengi piksel başına 1,6 cm'dir ve görüntüleyicinin atlasına zemin karoların yanında yaklaşık 80 böyle doku sığar.

**Mevsimler.** `--season`, bir dokuyu adıyla (GUID yok sayılarak) mevsimlik ikizine değiştirir (`..._xsummerx_bclr` ile `..._xwinterx_bclr`, ya da `..._bclr` ile `..._winter_bclr`), parkurda bir ikiz varsa. `--season winter` ile, bir alt mesh'in kış materyali, varyant tablosu bir tane adlandırdığında orada da kullanılır.

**Varyantlar.** Bir alt mesh kaydı, bir kopyanın giyebileceği her görünüş için bir `(summer, winter)` materyal tablosuyla açılır: bir afiş için beş baskı, bir lastik yığını için altı boya rengi. Her yerleştirme kaydı, bu kopyanın hangi varyantı giydiğini söyler. Modelden az varyantı olan bir alt mesh kendi varyantlarını tekrarlar.

**Yer tutucu bloğu.** Ortak bina atlasları, bina gölgelendiricisinin başka dokulardan renklendirdiği yüzeyler için katı bir RGB (255, 64, 0) bloğu ayırır. Bir dokunun yirmide birinden fazlası bu renge 12 seviye içindeyse, blok dokunun kendi ortalama rengiyle yeniden boyanır. Aksi halde bir şehir turuncu çıkardı.

### Görünmez yüzeyler {#see-through-surfaces}

Zincir çit ve ağlar, dokusunun alfa kanalında deliklerle tek dörtgenlerdir. Katı çizilirse bir çit, parkurun görüş alanında bir duvar olur. `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` ya da `tree` ile eşleşen malzeme gölgelendiricisi olan yüzeyler test edilir:

- Dokunun opaklığı 32 x 32'lik bir ızgarada ortalanır.
- Yüzey başına (aynı dokuyu paylaşan her delik üçgeni), her üçgende UV uzayında dört nokta örneklenir ve üçgenin UV alanıyla ağırlıklandırılır.
- Ortalama opaklık en az 0,05 ve **0,5**'in altındaysa, tüm yüzey dışarıda bırakılır. 0,05'in altındaysa alfa, gölgelendiricisi için açıkça başka bir şey demektir (0,01 örneklenen bir uyarı işareti), ve yüzey katı tutulur.
- Her yüzeyi dışarıda bırakılan bir model bildirilir: `N models left out as see-through (mostly holes in their texture)` (N model, görünmez olarak dışarıda bırakıldı: çoğu dokusundaki delikler).

Araç, her seferinde bir üçgene değil, tüm yüzeye bakar. Üçgen üçgen yargılanınca her dörtgenin yarısı kalıyordu ve çitler diş sıraları gibi çıkıyordu.

### Bütün çizilen binalar {#buildings-drawn-whole}

Bir şehir binalarını modüler parçalardan kurar: bir sokak pistinin çevresinde yüz binlerce parça, en kabasında bile on milyonlarca üçgen. Parçaları birer birer dışarıda bırakmak, tek başına duran duvar levhaları bırakıyordu. Oyun ayrıca `scene\hlod_tier_1\` içinde bütün binalar için vekiller gönderir: bina başına bir mesh (gövde `hlod_tier_1_*`), zaten arazi gibi dünya koordinatlarında:

- Her vekilin dünya kutusu, mesh'in konum kutusundan okunur (bir başlık okuması, çözme değil). Bütün bir harita için saniyeler sürer.
- Erişim kutusuna ve koridora değen vekiller kullanılır.
- Bir vekilin taban alanı içine (0,5 m dahil) düşen her `buildings` parçası atılır ve yerine vekil çizilir. Vekilin sürüşe uzaklığı, binanın en yakın kenarına göre ölçülür.
- Özet şunu söyler: `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)` (N bina, oyunun kendi vekillerinden bütün çizildi; M modüler parçanın yerine).

### Switched-on layers {#switched-on-layers}

Açılan bir katmanın yerleştirdikleri dışa aktarılır, ama serbest dolaşım dünyasından ayrı tutulur, böylece görüntüleyici onları gösterebilir ya da gizleyebilir:

| Katman | Parça |
|---|---|
| serbest dolaşım dünyası | `structure:<category>` (öncekiyle aynı) |
| eşleşen yarışın rotasının adını taşıyan katman | `structure:event_<category>` |
| başka her açılan katman | `structure:layer_<category>` |

Özet bunları sayar: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Zaten dünya koordinatlarında olan modeller {#models-already-in-world-coordinates}

Bazı model türleri hiçbir yerleşim dosyasında yoktur. Mesh'lerinin kendi dünya konumu vardır, arazideki gibi; bu yüzden hiçbir şeyin onları yerleştirmesi gerekmez:

| `scene\models\` altındaki klasör | Nedir | Parça |
|---|---|---|
| `plots` | bir mekânın kendi zemini: bir stadyumun zemini ve iç sahası, bir festival alanı, bir meydan | `ground:venue` |
| `plinths` (ve adı `floor`, `ground` ya da `road` olan her model) | bir caddenin süslendiği zemin: saksılar, basamaklar, bir parkın döşemesi | `ground:plinths` |
| `hda_infrastructure` (köprüler) | yordamsal olarak inşa edilmiş köprüler | `structure:bridges` |

- Bir model, kutusunun orta noktası kendi orijininden **300 m** (`WORLD_REACH`) dan fazla uzaktaysa dünya koordinatlarında sayılır. Yerleşim dosyalarınca yerleştirilen modeller, orijinlerinin birkaç yüz metresi içinde durur.
- Çizilmeyenler: kapatıcılar (occluder), yollara gerilmiş kablolar, dünyanın denizdeki arka planı, modüler binaların çatıları ve kapatıcıları (vekiller o binaları çizer), çarpışma ve su hacimleri.
- Her biri, mesh'lerinin kutusundan okunur (bir başlık okuması), bütün bir harita için birkaç saniye, çalıştırma başına bir kez.
- Zemin parçaları hiçbir zaman daha kaba çizilmez ve bütçeye sığsın diye dışarıda bırakılmaz; tıpkı bordürler gibi.

**Bir mekân bütün kesilir.** Sürüş bir mekânın kendi zeminine (`ground:venue`) değdiğinde, koridor, o zeminin tüm alanına ve `--margin`e kadar genişletilir; böylece bir stadyumun çevresindeki tribünler, duvarlar ve bariyerler de gelir, yalnızca turların kullandığı şerit değil. Konsol `through a venue (<model names>): cutting all of its ground, <n> km2` yazar. Platformlar kesimi genişletmez.

### Ayrıntı ve bütçe {#detail-and-the-budget}

Mesafe bantları, bütçe ve bütçe çok küçük olduğunda hangi kopyaların gittiği, [Ayrıntı seviyeleri ve bütçe](detail-budget.md) sayfasındadır.

### Yerleştirme özeti {#placement-summary}

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## The race's own layer {#the-races-own-layer}

Birçok yarış, serbest dolaşımda orada olmayan şeyler koyar: yan yolları kapatan beton duvarlar ve çitler, lastik yığınları, çadırlar, bir başlangıç portalı, tribünler, bayraklar, afişler. Her yarış bunları rota tanımında listeler (`route<id>_<map>.rtd`, `routedefinitions.zip` içinde, düz bir zip içinde düz XML):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Eklenen.** Her örnek, bir yerleşim dosyası kopyası gibi yerleştirilir. Dönüşümün 16 sayısı dört satırdır: modelin x, y ve z eksenleri (her biri ölçekli) ve oyunun metrelerinde konumu. Üçüncü satır, ilk ikisinin çapraz çarpımıdır. `Material`, kopyanın giydiği varyanttır. Parça `structure:event_<kind>`, `<kind>` `scene\models\` altındaki klasördür (barriers, props, infrastructure, signs; başka her şey props sayılır) ve düğüm glTF extras `{"layer": "event", "route": <id>}` taşır.
- **Kaldırılan.** Bir gizli varlığın konumunun **0,1 m** içinde duran serbest dolaşım kopyası dışarıda bırakılır. Orijinde duran bir gizli varlık, dünya koordinatlarındaki bir modeldir; adını bulmak için örnek GUID'si parkurun `AssetManifest.xml` dosyasında aranır (`<Models>` listesi: bir modelin kaynağı, sonra kopyalarının GUID'leri).
- **Yarışın gizlediği zemin tutulur.** Bir venue'nun zeminini gizleyen bir yarış, oraya kendi yüzeyini serer. Bu yüzey parkurun gönderdiği modeller arasında değilse, gizlenen zemin, sürülen şeye en yakın şey olarak kalır ve özet bunu söyler (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Çizilmeyen ama sayılan.** Seyirci işaretçileri (`crowd_proxies`: oyun seyirciyi bunlardan sprite olarak çizer) ve çarpışma eğrileri (`.splinecol`). Konsol bunları listeler: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Parkurun bir model göndermediği rota varlıkları (ışık parıltıları, bazı tabelalar, oyunun akış halinde yüklediği içerik) `placed names have no model in the archives` ile adlandırılır.

Yalnızca koridor içindeki kopyalar yerleştirilir; diğer her şey gibi.

## Writing the file {#writing-the-file}

Parçalar şu sırayla yazılır: her kare için `terrain`, `verge`, `road` (her biri karenin görseliyle), sonra `water`, `tyre marks`, `markings` (düz, son ikisi kaldırılmış), sonra yerleştirilen her parça ada göre sıralı. Koordinatlar oyunun kendisininkidir (metre, Y yukarı). Bkz. [Çıktı biçimi](output-format.md).

Dosya, ne tuttuğunu glTF `asset.extras` içinde söyler:

| Alan | Anlamı |
|---|---|
| `course_format` | `2`: yarışın kendi katmanı, mekânlar ve dünya uzayındaki modeller dosyadadır. [`courses`](commands.md#courses) daha düşük bir numaralı (ya da hiç numarası olmayan) bir dosyayı yeniden dışa aktarır |
| `route` | eşleşen rota kimliği, ya da `null` |
| `event_copies`, `event_kinds` | yarışın kendi katmanından kaç kopya yerleştirildi ve türleri |
| `hidden` | yarışın kaldırdığı için dışarıda bırakılan serbest dolaşım kopyaları |
| `venue` | sürüşün geçtiği mekân zemini modelleri |
| `layers` | yerleştirilen açılan katmanlar |

## Maliyeti {#what-it-costs}

Kabaca büyüklük mertebeleri:

| Parkur | Sonuç |
|---|---|
| kısa bir kır pisti | birkaç yüz bin arazi üçgeni, bir milyonun üstünde yerleştirilmiş olanlar; saniyeler, 100 MB'ın altı |
| uzun bir noktadan noktaya sprint | koridor, etrafındaki kutunun küçük bir kısmı; yaklaşık bir dakika, birkaç yüz MB |
| bir şehir sokak pisti | binlerce bariyer, süs ve tabela ve bütün binalar; otomatik bütçeyle birkaç yüz MB'a kadar |

Açık dünya arazisinin bir kilometre karesi yaklaşık bir milyon üçgendir.

## Arkasındaki kontroller {#checks-behind-it}

Bunlar okuyucu yazılırken yapılan ölçümlerdir, kaynakta belirtildiği gibi. Oyun kuruluysa dışında testler tarafından yeniden çalıştırılmazlar.

- Test pistinde araba, çıkarılmış zeminin üstünde yaklaşık sürüş yüksekliğinde durur (ortanca 0,2 m'nin altında).
- Örneklenen her kare, adının öngördüğü 512 m'lik karenin içine düşer.
- Ardışık bariyer yerleşimleri tam olarak 4 m aralıklıdır ve çoğu bariyer ucu, bir sonrakinin başlangıcının 5 cm içine düşer.
- Bordürler, çıkarılmış zeminin birkaç santimetre üstünde, yüzleri yukarı bakar ve sürüşün 5 m içindedir (ayrıca yüklü oyun testi, bkz. [Geliştirme](development.md)).

## Çizilmeyenler {#not-drawn}

- `--trees` olmadan ağaçlar ve çalılar. Çimen ve kalabalıklar hiçbir zaman (oyun bunları sprite olarak çizer).
- Bir yarışın, parkurun göndermediği kendi modelleri (bkz. [Yarışın kendi katmanı](#the-races-own-layer)).
- Modeller üzerindeki projeksiyonlu decal malzemeleri.
- Tahtasının üzerine alfa ile karıştırılmış tabela baskıları opak olarak çıkar.
- Zemin rengi, oyunun kendi arazi malzemeleri değil; asfaltın, çimenin ve ormanlığın nerede olduğunun yeniden kurulumudur.
