---
title: Geliştirme
nav_order: 14
lang: "tr"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Geliştirme {#development}

## Yerleşim {#layout}

```
heat3d_gamefiles/     paket: okuyucular, parkur dışa aktarımları, komut satırı
heat3d_update/        sürüm denetimi ve güncelleyici (bkz. Güncellemeler)
tests/                sentetik testler, örnek veriler ve kurulu oyunlara karşı testler
docs/                 bu belgeler (docs/wiki bundan üretilir)
VERSION               kurulu sürüm; GitHub sürümleriyle karşılaştırılır
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modül haritası {#module-map}

| Modül | Ne yapar |
|---|---|
| `__main__.py` | güncelleme denetimini çalıştırır, sonra `cli.main()` |
| `cli.py` | fiiller, `identify`, arşiv yönlendirmesi ve Forza parkur yazıcısı |
| `lapinput.py` | her tur biçimini konumlara çevirir; FH Companion kütüphane araması |
| `corridor.py` | sürüşün iki yanındaki bant, 4 m'lik bir raster olarak |
| `surfaces.py` | zemin türleri, parça adları ve renkleri |
| `glb.py` | `.glb` yazıcısı (parçalar, normaller, renkler, dokular, kuantizasyon) |
| `courseexport.py` | Forza: düzlemsel karo UV'leri, yol/kenar ayrımı, zemin pişirme, çıkartma kaldırma |
| `forzainstall.py` | Steam ve Xbox kütüphaneleri; bir kutunun ait olduğu Forza parkuru |
| `minizip.py` | ForzaTech `.minizip` arşivleri ve ad listeleri |
| `forzatech.py` | `.modelbin`: parçalar, tamponlar, düzenler, alt ağlar, malzemeler |
| `forzaterrain.py` | yere göre arazi karoları; yüzey sınıfları |
| `forzatexture.py` | `.pb` numuneleri; karo haritaları; zemin pişirme |
| `forzamaterial.py` | `AssetManifest.xml`; bir modeli hangi doku renkleri boyar; mevsimler |
| `forzaplacement.py` | `.pgeo` yerleşimleri, model düzeyleri, dokular, kesimler, yer tutucular, bütçe |
| `beamng.py` | BeamNG kurulumu, bağlanmış dosya sistemi, sahne, arazi, malzemeler |
| `beamngcourse.py` | BeamNG parkur dışa aktarımı |
| `beamngshape.py` | `.cdae` derlenmiş şekiller |
| `beamngcollada.py` | `.dae` yedeği |
| `acrally.py` | AC Rally kurulumu, etaplar, bileşen yerleşimi, sanal doku hacmi |
| `acrallycourse.py` | AC Rally parkur dışa aktarımı: çerçeve uydurma, zemin, yerleşim |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 işlenmiş paketleri |
| `unversioned.py` | sürümsüz özellik şemaları ve okuyucu |
| `unrealmesh.py` | işlenmiş statik ağlar |
| `unrealtexture.py` | dokular ve akışlı sanal dokular |
| `oodle.py` | kurulu bir Oodle kütüphanesini bulma ve çağırma |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity konteynerleri, paketleri, ağları |
| `frostbite.py` | Frostbite `.toc`, bölüm tabloları, kurulum paketleri, parça konumları, yükler |
| `frostbitebundle.py` | Frostbite satır içi paketleri, paket bildirimleri, bir seviyenin kataloğu, seviye listesi |
| `frostbiteebx.py` | tür kütüphanesi olmayan Frostbite RIFF EBX bölümleri |
| `frostbitemesh.py` | Frostbite MeshSet ve onun ayrıntı düzeyi parçaları |
| `frostbiteterrain.py` | Frostbite arazi akış ağacı, yükseklik sayfaları, zemin ağı |
| `frostbitematerial.py` | Frostbite dokuları (BC1/BC3/BC7 mip'leri), gölgelendirici blok depoları, renk haritası seçimi |
| `frostbitedecals.py` | Frostbite arazi çıkartmaları ve zemin pişirme |
| `frostbitenav.py` | Frostbite gezinti ağı karoları: askerlerin yürüyebileceği yüzeyler |
| `frostbitelevel.py` | Frostbite statik model grupları, yerleşim, `level` dışa aktarımı |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 arazi bileşenleri: yükseklik haritaları zemin ağına (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition haritaları: listeleme, HLOD yapıları, su, `ue-map` dışa aktarımı |
| `enfusion.py` | Enfusion `.pak`, `.edds`, arazi karoları, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger dünyaları: `.ent` dosyaları, kutular, `enfusion-world` dışa aktarımı |
| `forzacars.py` | her Forza arabası düşük ayrıntıyla `.h3dcars` içine (`cars`) |

Bütün modüller GitHub'da [`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles) altındadır.

## Testleri çalıştırmak {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini`, `testpaths = tests` ve `-q` ayarlar. Farklı nedenlerle önemli olan iki test türü vardır:

- **Sentetik testler** arşivleri bayt bayt kurar ve her yerde çalışır. Bir zamanlar yanlış olan alan düzenlerini sabitlerler: 64-bit `.minizip` segment tabanı ve hizalama dolgusu, pak blok boyutu kaçışı, Unity başlığındaki iki int64 arasındaki u32, VPK `0x7FFF` indeksi, Forza normalinin bölünmüş x'i.
- **Kurulu oyun testleri** oyun makinedeyken gerçek dosyalara karşı çalışır ve oyun yoksa **atlanır** (başarısız olmazlar). Küçük bir dosya için doğru, büyük bir dosya için yanlış olan bir düzeni yakalayabilen tek şey bunlardır.

### Örnekler {#fixtures}

| Örnek | Oluşturduğu |
|---|---|
| `tests/forza_fixtures.py` | `.minizip` arşivleri (64-bit taban, dolgu, karışık kodekler), bildirimler, `.modelbin` modelleri ve arazi, `.pb` numuneleri |
| `tests/beamng_fixtures.py` | küçük bir BeamNG kurulumu: `gameengine.zip`, `content`, 64 m arazili bir seviye zip'i, bir asfalt şeridi, bir yol çıkartması, bir ray, bir prefab, bir orman öğesi, deniz, malzemeler ve belgelenmiş düzende `.cdae` şekilleri |
| `tests/unreal_fixtures.py` | bir dizinli IoStore konteyneri, bir zen paketi, sürümsüz bir özellik bloğu |
| `tests/frostbite_fixtures.py` | Frostbite tabloları, paketler, EBX bölümleri, ağlar ve arazi sayfaları, bayt bayt |

### Test dosyaları {#test-files}

| Dosya | Kapsadığı |
|---|---|
| `test_minizip.py` | okuma, 64-bit taban, tek ve çift paket tabloları, reddetmeler, ad dosyası |
| `test_forzatech.py` | parça tablosu ve zinciri, reddetmeler; kurulu: gerçek modellerin zincirleri ve etiketleri |
| `test_forza_geometry.py` | dünya yerleşimi, tepe noktası düzeni, reddedilen biçimler, alt ağlar, normaller ve UV'ler |
| `test_forzaterrain.py` | karo ızgarası (1023 ve 512 m), kırpma, çıkarma |
| `test_forzatexture.py` | numune başlığı, çözme, doku rafı, zemin pişirme |
| `test_forzamaterial.py` | bildirim, adlar, malzeme hash'leri, renk seçimi, mevsimler |
| `test_forzaplacement.py` | `.pgeo` kaydı, kopyaları yerleştirme, düzeyler, varyantlar, saydam yüzeyler, bütün kutu, bütçe, yer tutucu rengi, otomatik bütçe; kurulu: zeminde bordürler |
| `test_forzainstall.py` | oyunu bulma, parkuru seçme |
| `test_courseexport.py` | karo UV'leri, parça planı, çıkartma kaldırma |
| `test_course_cli.py` | sentetik bir parkurda tüm `course` ve `courses` fiilleri; bayt sıra işaretli `terrain --route` ve `bounds` olmadan |
| `test_archive_cli.py` | okuyucusu olan her arşivde `identify`, `list` ve `extract` (`.pak`, IoStore, `.vpk`, adlı ya da adsız `.minizip`, zip, `.cdae`, `.ter`); tek satır hatalar ve bir çıkış kodu: şifreli bir pak, şifreli bir konteyner, bir arşiv olmayan dosya, kötü bir `--key` |
| `test_corridor.py` | bant, arazi bandla kesilir |
| `test_lapinput.py` | her tur biçimi, kutu, hatalar, parkur adı araması, bir klasörün hangi oyun olduğu |
| `test_surfaces.py` | hangi adların yüzeyi belirlediği, hangilerinin belirlemediği, parça adları |
| `test_glb.py` | dosyanın geçerliliği, düğümlerin sınıfı, reddetmeler, kuantizasyon |
| `test_beamng.py` | şekiller, seviye, kategoriler, bir turdan seviyeyi bulma, parkur, Collada yedeği; kurulu: `.cdae` ile `.dae`, her seviyenin açılması |
| `test_acrally.py` | konteynerler, paketler, özellikler, dönüşümler, çerçeve uydurma, yerleştirilmiş modellerin parçaları ve bütçesi, sanal dokular; kurulu: etaplar ve pişirilmiş zemin rengi |
| `test_pak.py` | altbilgi, girdiler, blok boyutu kaçışı, reddetmeler; kurulu: ofsetler ve SHA-1 |
| `test_unity.py` | reddetmeler; kurulu: nesne tablosunun dosyayı döşemesi, sürüm dizgileri, mesh sınırları |
| `test_frostbite.py` | imzalı ve gizlenmiş başlıklar, reddetmeler, kurulum paketleri (aynı blob numaralı iki paket); kurulu: her tablo, süper paketler, bölüm zincirleri, farklı kimlikler, doğru paketten örneklenmiş yükler |
| `test_frostbitelevel.py` | parça kimliklerinin kendi konumlarıyla eşleşmesi, satır içi paketler, bildirimler, gölge bölümü ve UV'leri olan bir MeshSet, grup üyesi, dönüşüm kuralı, iki seviyeli arazi, renk haritası seçimi, en büyük mip'leri eksik bir doku parçası, tekrarlayan örnekleyici, çıkartma kayıtları, alfasıyla birleştirilen bir çıkartma, bir yüzeyin kendi haritasına yenilen bir çıkartma sayfası, bir yüzeyin çıkartmaları, varyasyon bloğunun anahtarıyla ve bir ikiz bloğuyla erişilmesi, yüzey malzemelerinden zemin rengi, maske sayfaları (BC4 ve sıkıştırılmamış) ve renk haritası sayfaları, paletler ve kanal maskelerinin asla renk sayılmaması, gri haritaların boyanması, bitki örtüsü ve yer ağaçları; kurulu: seviyenin arazi çıkartmaları, en büyük seviyenin kataloğu, sınırları içindeki ağlar, grup üyeleri, bitki örtüsünün çözülmüş arazide durması |
| `test_vpk.py` | dizin, reddetmeler, bölünmüş arşivler; kurulu: haritalar açılır, CRC'ler eşleşir, gezinti ağı |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, arazi karoları ve dünya dosyaları; `enfusion-world` dışa aktarımı |
| `test_forzacars.py` | `cars` fiilinin yazdığı `.h3dcars` dosyası |
| `test_unreallevel.py` | Unreal 5 arazileri, HLOD yapıları, su; `ue-map` dışa aktarımı |

## Kurulu oyun testleri {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py) testler için oyunları bulur. `steam_common()` her Steam kütüphanesinin `steamapps\common` klasörünü listeler (Steam'in kendi klasörleri dahil). `installed(*globs)`, bu klasörlerin altında eşleşen yolları döndürür; bir glob `**` içeriyorsa özyinelemeli olarak. Her test neye ihtiyaç duyduğuna kendisi karar verir:

| Test | Arar | Şununla atlar |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak`, **şifrelenmemiş** bir indeksle, en çok 4 | "no shipped pak on this machine" |
| `test_unity.py` | `*/*_Data` ya da `*/*/*_Data` içinde, okuyucunun kabul ettiği `resources.assets` / `sharedassets0.assets`, en çok 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, en çok 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | FH Companion kütüphanesinin, `find_track`'in yerleştirdiği ve en çok turu olan parkurları (başlangıç ve bitiş 50 m içinde); ya da `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Yalnızca bir oyunun testlerini çalıştırın, ya da Forza bordür testini bir parkura yöneltin:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Kurulu oyun testleri yalnızca oyunlardan okur. Oyun klasörlerine hiçbir şey yazmazlar. Test çıktıları pytest'in geçici klasörlerine gider.

## Kurallar {#conventions}

- **Tahmin etmek yerine reddet.** Her okuyucu kendi istisnasını fırlatır (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) ve ne bulunduğunu ve neden okunmadığını söyleyen bir mesajla.
- **Biçimin kendisine karşı denetle.** Bir hash, bir CRC, bir ofset zinciri, saklanan bir sınır kutusu, sürüşün zeminde yatması. "Çökmedi" değil.
- **Anahtar yok, tescilli kod paketlenmez.** Bkz. [Kurallar ve lisanslar](rules-and-licences.md).
- **Gizli veriler dışarıda kalır.** Oyun dosyaları, dışa aktarımlar, turlar, kayıtlar ve ekran görüntüleri depoya asla girmez. `.gitignore` bunları klasöre ve türe göre dışarıda tutar. Testler sentetik veri ve kurulu oyunları kullanır; depoda hiçbir oyun içeriği bulunmaz.
