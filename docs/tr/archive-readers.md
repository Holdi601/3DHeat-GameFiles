---
title: Arşiv okuyucuları
nav_order: 9
lang: "tr"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Arşiv okuyucuları {#archive-readers}

Bir **konteyner** (ya da arşiv), bir oyunun birçok dosyayı içine koyduğu tek ve büyük bir dosyadır. Bir **CRC** ya da hash, bazı baytların kısa bir parmak izidir: eşleşirse baytlar doğru okunmuş demektir. Bir **sınır kutusu**, bir modelin etrafındaki en küçük kutudur.

Komutların altında, oyunların kullandığı konteynerleri okuyan okuyucular vardır. Biçimleri belgelenmemiştir; Valve'ın VPK'si ve BeamNG'nin `.cdae` dosyası bunun dışındadır. Bu yüzden "desteklenen" demek **gerçek dosyalarla doğrulanmış** demektir, "çökmedi" demek değil. Her okuyucu kendini, biçimin garanti ettiği bir şeye karşı denetler: bir hash, bir CRC, sonunda kapanması gereken bir ofset zinciri ya da saklanmış bir sınır kutusu. Bir denetim başarısız olursa okuyucu tahmin yürütmek yerine bir mesajla reddeder. Yanlış bir ağ, doğru bir ağ gibi görünür; ta ki onu parkurun yanına koyana kadar.

| Okuyucu | Modül | Okuduğu | Okumadığı | Nereden çağrılır |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | sürüm 8-12: dizin, girdiler, Zlib/Gzip/Oodle blokları, sizin verdiğiniz bir anahtarla AES | sürüm 8'den önceki sürümler, yalnızca yol karması içeren dizinler, taşan girdiler, varlık içerikleri | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, v8 üzerinde denetlendi), zen paketleri, birkaç bileşen sınıfı için sürümsüz özellikler, işlenmiş statik ağlar, dokular, akışlı sanal dokular | şifreli konteynerler, sürümlü paketler, yalnızca Nanite ağları, diğer sınıfların özellikleri | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | makinede zaten bulunan bir kütüphane üzerinden Oodle blokları | Oodle kütüphanesi olmayan hiçbir şey; asla paketlenmez | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` biçimi 22 ve üzeri (Unity 2020 - 6000), `UnityFS` paketleri, `.resS` dahil sıkıştırılmamış ağlar | 2020 öncesi biçimler, gömülü tip ağaçları, sıkıştırılmış ağlar, `Mesh` dışında hiçbir sınıf | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc` DbObject ağaçları ve ikili bölüm tabloları, kurulum paketleri, parça konumları, satır içi paketler ve bildirimleri, RIFF EBX bölümleri, MeshSet ağları, arazi yükseklik alanı, BC1/BC3/BC7 dokuları ve gölgelendirici blokları, statik model grubu yerleşimi | XOR ile gizlenmiş tablolar, arazinin yere yakın rengi ve delikleri, normal haritalar, kesim maskeleri dışındaki alfa | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | sürüm 1 ve 2, bölünmüş arşivler, ön yükleme verisi, CRC denetimi | derlenmiş varlıklar (`.vmdl_c`, `.vtex_c`), CS2 gezinti ağı biçimi | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, saklı), `.modelbin` geometrisi, `.pb` numuneleri (BC1, BC7, RGBA), `.pgeo` yerleşimleri, malzeme doku hash'leri | diğer tepe noktası ve indeks biçimleri, diğer doku biçimleri, arazi gölgelendirici katmanları | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` ve `extract` (`.minizip`) |
| [BeamNG dosyaları](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | bağlanmış zip dosya sistemi, sahne JSON'u ve TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, malzemeler | yüzey ve çıkartma ağları, canlandırılmış diziler, yordamsal zemin örtüsü | `course` (BeamNG), `identify` (zip'ler, `.cdae`, `.ter`), `list` ve `extract` (zip'ler) |

## Her okuyucunun uyduğu kurallar {#rules-every-reader-follows}

- **Anahtar yok, hiçbiri kurtarılmaz.** Şifreli bir Unreal `.pak` yalnızca sizin verdiğiniz bir anahtarla (`--key`) açılır. Şifreli bir IoStore konteyneri reddedilir. Hiçbir şey bir çalıştırılabilir dosyada anahtar aramaz ya da başka bir sürecin belleğini okumaz. Bkz. [Kurallar ve lisanslar](rules-and-licences.md).
- **Tescilli kod paketlenmez.** Oodle, makinede zaten kurulu bir oyundan ya da motordan yüklenir.
- **Tahmin etmek yerine reddet.** Bilinmeyen bir sürüm, sıkıştırma, tepe noktası biçimi ya da doku biçimi belirli bir hata verir, örneğin `texture format 42 has not been identified; refusing to guess`.
- **Salt okunur.** Hiçbir okuyucu bir oyun klasörüne yazmaz. Dışa aktarımlar sizin belirttiğiniz yere gider.

## "Doğrulanmış" ne anlama geliyordu {#what-verified-meant}

Bu sayfalardaki doğrulama rakamları modül açıklamalarından (docstring) alınmıştır. Her okuyucu yazılırken kurulu oyunlara karşı ölçülmüştür. [Geliştirme](development.md) sayfasında anlatılan sentetik testler alan düzenlerini sabitler. Kurulu oyun testleri, oyun makinedeyse bazı denetimleri yineler, değilse atlar. Bir testle kapsanmayan rakamlar o zamandan beri yeniden denetlenmemiştir.
