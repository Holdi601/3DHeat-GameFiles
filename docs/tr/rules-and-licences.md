---
title: Kurallar ve lisanslar
nav_order: 12
lang: "tr"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Kurallar ve lisanslar {#rules-and-licences}

Aracın bütününü üç kural şekillendirir. Tam metin: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Anahtar yok: paketlenmiş yok, kurtarılmış yok {#no-keys-none-shipped-none-recovered}

**Konteynerleri okur.** Bir arşiv biçimini ayrıştırmak sıradan dosya işlemedir; FModel, UModel ve AssetRipper bunu yıllardır açıkça yapıyor.

**Önemli olan çizgi şifrelemedir ve araç içinde çizilmiştir.**

- **Paketlenmiş anahtar yok.** Kodda ya da veride hiçbir anahtar bulunmaz.
- **Anahtar kurtarma yok.** Hiçbir şey bir çalıştırılabilir dosyada anahtar aramaz ve hiçbir şey başka bir sürecin belleğini okumaz.
- **Elinizdeki bir anahtar, ya da hiçbir şey.** Şifreli bir Unreal `.pak`, yalnızca `--key <hex>` ile açılır (Python'da, `PakArchive(path, aes_key=...)`). `pak.py`'nin anahtar elde edebileceği hiçbir kod yolu yoktur. Şifreli bir IoStore konteyneri doğrudan reddedilir.
- **Gizleme de uygulanmaz.** Frostbite'ın XOR ile gizlenmiş tabloları, anahtarlarını dosyanın kendisinde tutar; bu yüzden bir erişim kontrolü değil, gizlemedir. Yine de tespit edilirler ve reddedilirler, çünkü hiçbir elindeki dosya bu biçimi kullanmaz ve bir uygulamayı karşılaştıracak bir şey olmaz. Assetto Corsa EVO'nun anahtarlı paketi de aynı nedenle, anahtar kuralının nedeniyle reddedilir.
- **Şifreli dosyalar kapalı kalır.** Battlefield 6'nın, oyunun tür kütüphanesini tutan ilk dosya sistemi şifrelidir ve okunmaz. Seviye dışa aktarımı şifrelenmemiş dosyalardan çalışır ve ihtiyaç duyduğu iki türü verilerden kurar.
- **Hiçbir şey bir oyun sürecine enjekte edilmez.** Telemetri, oyunların kendi yayınladığı akışlardan gelir; kayıt, genel ekran kaydı API'leri kullanır (diğer 3DHeat araçlarında). Anti-hile korumalı bir oyuna enjeksiyon, bunu çalıştıran kişinin hesabını riske atar.

Şimdiye kadar test edilen her arşiv şifrelenmemiştir.

## 2. Kendi dosyalarınız {#your-own-files}

Araç, **makinenize kurulu oyun dosyalarını** okur. Asla oyun içeriği indirmez.

Bir oyundan hiçbir şey onunla birlikte dağıtılmaz: oyun içeriği yok, oyun kodu yok, DLL yok. Dışa aktardığı her şey sizin diskinize yazılır, başka hiçbir yere değil.

3DHeat GameFiles hiçbir oyun yayıncısıyla bağlantılı değildir ve hiçbiri tarafından onaylanmamıştır. Oyunlar ve ilgili adlar ve ticari markalar sahiplerine aittir. Hak sahipleri: [github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) adresinde bir issue açın - hızlı yanıt veririz ve istek üzerine her şeyi kaldırırız.

## 3. Çıktı yeniden dağıtım için değildir {#output-is-not-for-redistribution}

Çıkan şey **mekânsal bağlam** için geometridir: zemin, yol ve yanındaki şeyler; bir bütçeye indirgenmiş, böylece turlar yerinde analiz edilebilir. Bir arşivin tuttuğu en az şeydir ve yine de oyun yayıncısının içeriğidir.

- Dışa aktarılmış `.glb` dosyalarını ve içindeki dokuları kendi analiziniz için saklayın.
- Dışa aktarılmış parkurları, seviyeleri, modelleri ya da dokuları yayınlamayın, paylaşmayın ya da satmayın.
- Deponun `.gitignore` dosyası, oyun dosyalarını, dışa aktarımları, turları ve kayıtları klasöre ve dosya türüne göre (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` ve diğerleri) sürüm kontrolünün dışında tutar.

## Oodle bulunur, paketlenmez {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, şimdi Epic), tescillidir ve yeniden dağıtılabilir bir yapısı yoktur. `oo2core_*.dll`, onu gönderen ürüne lisanslıdır. Bu yüzden `oodle.py`, bir kütüphaneyi paketlemek yerine makinede zaten olan bir kütüphaneyi yükler. Bu, lisansın öngördüğü düzenlemedir ve FModel ile UModel'in kullandığı aynı düzendir. Bkz. [Oodle](reader-oodle.md).

## Biçimlerin kendileri {#the-formats-themselves}

- `.pak`, IoStore, Unity'nin `SerializedFile`'ı, Frostbite'ın `.toc`'u ve ForzaTech'in biçimleri belgelenmemiştir. Buradaki okuyucuların hiçbiri başka bir projenin kaynak kodundan türetilmemiştir. Frostbite için, eski sürümlerin genel açıklamaları (Frosty modding araçları, bir Need for Speed Heat biçim notu, bir GDC konuşması) alan adlarını ve neye bakılacağının bir haritasını sağladı. Hiçbir kod alınmadı; her ofset dosyalar üzerinde ölçüldü (bkz. [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Çıkarılmış seviyeler yalnızca sizin kullanımınız içindir. Araç onları yalnızca sizin diskinize yazar; yayınlamayın.
- BeamNG `.cdae` düzenini yayınlar ve okuyucu ona uyar.
- Valve, VPK'yi belgeler.
- Unreal 5'in pişirilmiş özellik verisi, her sınıfın özellik listesini gerektirir. `unversioned.py`'deki listeler **yalnızca adlar ve tiplerdir**; bir arayüz eşleme dosyasının tuttuğu türden biçim gerçekleridir. Epic'in bağlı bir hesabı olan herkese sunduğu Unreal Engine başlıklarından türetilmiş ve paylaşılan verilere karşı denetlenmiştir. Hiçbir motor kaynağı dahil değildir ya da gerekli değildir.

## Bu aracın lisansı {#this-tools-licence}

Bu depo için yazılan her şey **MIT lisansı** altındadır ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): kullanın, değiştirin, dağıtın; ticari olsun ya da olmasın.

Üçüncü taraf paketler, hepsi izin verici olduğu için dışa aktarıcının kendi kısıtlaması yoktur:

| Paket | Lisans | Kullanım amacı |
|---|---|---|
| numpy | BSD-3-Clause | mesh çözme |
| cryptography | Apache-2.0 / BSD-3-Clause | yalnızca anahtarını sahip olduğunuz arşivler |
| lz4 | BSD-3-Clause | Forza arşivleri, bazı Unity paketleri, IoStore LZ4 blokları |
| Pillow | MIT-CMU (HPND) | blok sıkıştırmalı dokular, JPEG çıktısı |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | birkaç zstd sıkıştırılmış `.cdae`, Frostbite zstd blokları |
| pytest | MIT | yalnızca geliştirme |

Lisanslar, Eylül 2026'da paket meta verilerinden okundu. Bir bileşenin koşulları o tarihten sonra değiştiyse, kaynak geçerlidir.
