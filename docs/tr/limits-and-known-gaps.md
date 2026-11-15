---
title: Sınırlar ve bilinen eksikler
nav_order: 10
lang: "tr"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Sınırlar ve bilinen eksikler {#limits-and-known-gaps}

Aracın yapmadıkları, kısmen yaptıkları ve davranışının tutarsız olduğu yerler. Çoğu eksik bilinçli bir reddetmedir. Denetlenecek dosya olmadan çözmek, doğru görünen ama olmayan bir çıktı üretir.

## Oyunlar {#games}

| Oyun | Parkur dışa aktarımı | Neden değil ya da ne kadar |
|---|---|---|
| Forza Horizon | evet | zemin rengi bir yorumdur (aşağıya bakın) |
| BeamNG.drive | evet | zemin örtüsü yok, tekrarlayan model dokuları düzleştirilir |
| Assetto Corsa Rally | evet | modeller düz renkli; oyunda kaydedilmiş bir tur ile henüz çalıştırılmadı |
| Assetto Corsa EVO | **hayır** | tüm içerik, bir anahtarla gizlenmiş tek bir pakette; bu araç anahtar kurtarmaz |
| Battlefield 6 (seviye dışa aktarımı, `level`) | evet, bütün bir seviye | arazi, gruplanmış ve tek tek yerleştirilmiş mesh'ler ve renk haritaları, askerlerin gezinti ağı, kesilmiş bitki örtüsü; oyun alanının zemin rengi kaba (metre başına 32 m, ya da tek bir ortalama renk); saydamlık ve normal haritalar yok; yok edilebilir mesh'ler etiketlenir, yok edilmiş halleri dışa aktarılmaz |
| Unreal 5 World Partition oyunları (harita dışa aktarımı, `ue-map`) | evet, bütün bir harita | arazi tam; binalar haritanın basitleştirilmiş HLOD mesh'leri, tam ayrıntılı modeller değil; su gövdeleri; bitki örtüsü, çıkartma ve zemin rengi yok |
| Arma Reforger (dünya dışa aktarımı, `enfusion-world`) | evet, bütün bir dünya | arazi kendi renklerinde ve deniz; binalar, donatılar ve kayalar modellerinin üçgenleri değil, kutuları olarak; ağaçlar istek üzerine (`--trees`), kutu olarak; göller, nehirler ya da alt varlıklar yok |
| iRacing | **hayır** | parkurlar, dosya çıkarma hedefi olmayan korumalı bir biçimde gelir |
| başka her şey | **hayır** | parkur okuyucusu yok; 3DHeat GameCapture ile oyundan yeniden kurun, ya da görüntüleyicinin Yarış analizi sekmesinde parkursuz turları analiz edin |

## Motorlar ve biçimler {#engines-and-formats}

| Biçim | Uygulanmayan |
|---|---|
| Unreal `.pak` | sürüm 8'den önceki sürümler; yalnızca yol karması içeren dizinler (adlar kurtarılamaz); indeksin taşma listesindeki girdiler (atlanır); bir pak'tan `.uasset`/`.umap` içeriklerinin çözülmesi |
| Unreal IoStore | şifreli konteynerler (reddedilir, anahtar seçeneği yok); bir dizin indeksi olmadan konteynerleri listelemek (dosya adı içermez); sürümlü paketler; yalnızca Nanite ve satır içi olmayan mesh'ler; iskelet mesh'leri; şeması olmayan sınıfların özellikleri; bileşenlerin özellikleri (bu sürümde düzeni değişti); spline mesh'leri ve çıkartma bileşenleri |
| Unity | 22'den önceki biçimler (Unity 2019 ve daha eski); gömülü tip ağaçları olan dosyalar; sıkıştırılmış mesh'ler; `Mesh` dışındaki her sınıf, yani dönüşüm, malzeme ve sahne yok; bir pakette `meshes`; `list`/`extract` (bunun yerine `meshes` kullanın) |
| Frostbite | XOR ile gizlenmiş tablolar; arazinin katman grafiği (kontrol edilen seviyelerin yaklaşık üçte birinde maskeler okunur); `Mesh` dışındaki nesne taslakları (oyun mantığı, efektler, sesler); satır içi saklanmayan mesh seviyeleri; normal ve diğer haritalar, kesim maskeleri dışındaki alfa; arazi delikleri; tür kütüphanesi (ilk dosya sisteminde şifreli, dokunulmadı); tek tek varlıkları listeleyen ya da çıkaran bir komut |
| Source 2 | derlenmiş varlıklar (`.vmdl_c`, `.vtex_c`); CS2 gezinti ağı (sürüm 36) |
| ForzaTech | dört ölçekli kısa tamsayı dışındaki konum biçimleri; u16 dışındaki indeks biçimleri; 0, 9, 13 dışındaki doku kodları; arazi gölgelendiricisinin malzeme katmanları; tanjantlar |
| BeamNG | yüzey ve çıkartma mesh'leri; animasyon; yordamsal zemin örtüsü; dünyanın kenarındaki manzara |
| Unreal arazileri ve World Partition haritaları | yükseklik haritaları işlenmiş hücrelerde olan araziler; düzenleme katmanları ve delikler; Nanite arazi mesh'leri; hücrelere yerleştirilmiş tam ayrıntılı modeller; bitki örtüsü; arazi malzemeleri |
| Enfusion | model üçgenleri (`.xob` geometrisi, okunmayan bir düzende sıkıştırılmış); DX10 öncesi başlıklı `.edds`; dünya dosyalarındaki iç içe nesne değerleri (atlanır, sayılır); alt varlıklar; üretilmiş göller ve nehirler; bir `.pak` üzerinde `list`/`extract` |

## Bilmeye değer davranışlar {#behaviour-worth-knowing}

- **Forza'nın zemin rengi oyunun kendisi değildir.** Pişirilmiş doku, asfaltın, kısa çimin, pürüzlü zeminin ve ormanlığın *nerede* olduğunu söyleyen karo haritalarından çizilir. Sabit renkler ve gölgelendirme kullanır, çünkü terrain gölgelendiricisinin kendi malzeme katmanları çözülmez.
- **`--no-textures`, Forza'nın kenarını da kaldırır.** Asfalt/kenar ayrımı, pişirilmiş haritalarla gelen asfalt maskesini kullanır. Dokusuz yol şeritleri bütün kalır ve yol olarak kalır.
- **Verdiğiniz bir bütçe yalnızca bordürler tarafından aşılabilir.** Bordürler (ve BeamNG'nin sürüş yüzeyi modelleri) hiçbir oyunda sadeleştirilmez ya da bırakılmaz; bu yüzden onların maliyetinden küçük bir `--detail-budget` yalnızca onlar tarafından aşılır; diğer her şey önce bırakılır. Bkz. [Ayrıntı düzeyleri ve bütçe](detail-budget.md).
- **Uygulanmayan seçenekler sessizce yok sayılır**: BeamNG ve AC Rally için `--season`, BeamNG ve AC Rally için `--track`, Forza için `--level`/`--install`.
- **Bir Battlefield 6 seviyesinin zemin rengi, çıkartmalarından uzakta kabadır.** Yükseklik alanı, arka plan dokusunun renk haritasından renklendirilir: seviyenin sunduğu en büyük mip'te metre başına 32 m; ya da hiçbir arka plan haritası kapsamıyorsa, arazinin yüzey malzemelerinin orta rengiyle. `--ground-texture`, bunu arazinin renk haritasıyla (seviyede varsa 0,5 m piksel başına) çarpar ve yolları, pistleri, çizgileri ve lastik izlerini, malzemelerinde bir boya rengi ayarlanmışsa o renkle, değilse nötr bir renkle üstüne pişirir; yol değişim maskeleri dışarıda bırakılır. Oyun yüzey katmanlarını okunmayan bir gölgelendirici grafiğinde karıştırır; dışa aktarım katmanların renklerini maskeleriyle ve yükseklik alanının eğimiyle, kendi kuralıyla yerleştirir; maske sayfaları birbirine uymayan bir seviye tek bir renk alır. Her katman, dokusu değil, renk haritasının ortalamasıdır. Bkz. [Frostbite](reader-frostbite.md#terrain-layers). Yükseklik alanının farklı çözünürlükteki parçaları küçük basamaklarla birleşir.
- **Bir Battlefield 6 renk haritası seçilir, okunmaz.** Bir gölgelendirici bloğu örneklediği her dokuyu adlandırır, ama hangisinin renk olduğunu söylemez; seçim adla yapılır (bkz. [Frostbite](reader-frostbite.md#textures-and-materials)) ve bir yüzey için bir süsleme ya da ayrıntı sayfası seçebilir. Çıkartma sayfaları (`t_de_...`) yüzeyin kendi haritasına yenilir; bir tabelanın çıkartması, kalkanı bir çeyrek dönmüş olarak çizilirse ona bakılır. Mesafe alanları, paletler ve kanal maskeleri asla alınmaz. Arka plan binaları paletlerinin renkleriyle çizilir; gri haritalar, parametrelerin adları karmaşık olduğu için malzemenin rengini, dışa aktarıcının kendi kuralıyla alır; birden çok renkle bir maske üzerinden gri bir harita boyayan bir malzeme, bunlardan birini alır.
- **Battlefield 6 arazi delikleri kesilmez.** Bir seviyenin yürünebilir zemini yükseklik alanının altında kaldığında, oyunun araziyi kesmiş olması gerekir; dışa aktarım bunu yapmaz. Deliklerin yeri olarak elenenler: arazinin katman maskeleri (hiçbiri orada yoğunlaşmaz), 67 x 67'lik düğüm rasteri, ayrılmış bir yükseklik değeri (hiçbir yükseklik sayfası 0 ya da 65.535 tutmaz), düğümlerin bayrakları (hepsi aynı) ve zemini kesen mesh'ler ya da varlıklar: oradaki zeminin altına yerleştirilmiş olan şey kaya ve uçurum mesh'leridir ve seviyenin hiçbir varlığı delikler, tüneller ya da mağaralar için adlandırılmamıştır. İki raster ağacı çalıştırma uzunluğuyla çözülür ama yerleştirilmez; geriye kalan onlardır (bkz. [Frostbite](reader-frostbite.md#terrain-layers)).
- **Bir Battlefield 6 nesne varyasyonu, bir bölüme ikizleri üzerinden ulaşır.** Yerleştirilmiş bir kopyanın varyasyonu, bölümlerinin gölgelendirici bloklarını anahtarla seçer; bir mesh'in bir varyasyon için bloğu yoksa, aynı varsayılan bloğa sahip başka bir mesh'in bölümünün varyantı alınır (bkz. [Frostbite](reader-frostbite.md#textures-and-materials)). Bu dışa aktarıcının kuralıdır; ikizi olmayan ve değişen bir bölüm varsayılan görünümünü korur.
- **Battlefield 6 katmanlı malzemeleri, temelleri ve bir sayfa olarak çizilir.** Harflemesi olan bir duvar paneli, harfleri üstündeki bir sayfayla birlikte sıvası olarak çizilir; malzemenin diğer katmanları (maskesi üzerinden kir kaplaması, ayrıntı ve yosun haritaları) karıştırılmaz.
- **Gezinti ağı, yapay zekânın ağıdır, oyuncuların değil.** Bir askerin gidebileceği yerleri kapsar: zemin, döşemeler ve merdivenler, bazı çatılar, ama her yüksek nokta değil. Yüzeyler arasındaki bağlantılar (atlama, merdiven, aşma) dışarıda bırakılır.
- **Bir Battlefield 6 seviyesi her oyun modunun katmanını içerir.** Yalnızca bir modun yerleştirdiği nesneler, başka bir modun nesneleriyle üst üste gelebilir. `--skip` katmanları adlarına göre dışarıda bırakır.
- **`courses` yalnızca Forza içindir** ve yalnızca `... (course_...)` adlı kütüphane klasörlerini alır.
- **BeamNG tur çerçevesi varsayılır**: 3DHeat kaydedicisinin yazdığı görüntüleyici çerçevesi `(x, z, -y)`. BeamNG'nin ham çerçevesinde, başka bir kaydediciden gelen turlar yerleştirilmez.
- **`list` ve `extract`, her biçimi değil arşivleri alır.** Bir `.pak`, bir IoStore `.utoc`, bir `.vpk`, bir `.minizip` ve bir zip'i açarlar. Bir Unity konteyneri `meshes` ile, bir Frostbite seviyesi `level` ile okunur; bir `.cdae` ya da `.ter` bir arşiv değil bir dosyadır (`identify` adını söyler). Yanında `ChunkContentsMiniZip<n>.txt` olmayan bir `.minizip`, girdi numarasıyla listelenir.
- **BeamNG'de yinelenen dokulu yerleştirilmiş modeller ortalama renk olarak kullanılır**, çünkü `.glb` örnekleyicisi kenetler ve görüntüleyici dokuları bir atlasa paketler.
- **Pratikte yalnızca Windows.** Steam yolları `C:\Program Files` altında, `%LOCALAPPDATA%`, `C:\XboxGames`, ve Oodle için bir `*_win64.dll`. Diğer platformlar test edilmedi.

## Doğrulanmamış {#unverified}

- Eski Python sürümleri (araç 3.13 ile çalıştırıldı).
- Oyunda kaydedilmiş bir turla Assetto Corsa Rally. Yalnızca sentetik turlarla, rastgele çerçevelerde test edildi.
- 3DHeat görüntüleyicisi dışındaki glTF görüntüleyicileri.
- Her oyunun çerçevesinin sol mu sağ elli mi olduğu. Dışa aktarım her oyunun telemetri çerçevesini korur, bu yüzden turlar ve parkurlar her durumda hizalanır.
- BeamNG'de `WaterBlock`'un yerel z = 0'ının yüzeyi olarak anlamı.
- Battlefield 6 dışındaki oyunlarda Frostbite yerleşimi ve grup üyesi düzenini değiştiren bir güncellemeden sonra Battlefield 6'da Frostbite yerleşimi. Okuyucu o zaman grup bulamaz ve bunu söyler.
- Bir Battlefield 6 dışa aktarımının, oyunun bildirdiği konumlarla hizalanıp hizalanmadığı. Koordinatlar diğer oyunlardaki gibi oyunun kendisine aittir, ama henüz hiçbir kayıt bir dışa aktarımın üstüne konmadı.
