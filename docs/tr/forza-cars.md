---
title: Forza araçları
nav_order: 6
lang: "tr"
source: forza-cars.md
source_hash: "e1b48f2525db"
nav_exclude: true
search_exclude: true
---
# Forza araçları: `cars` {#forza-cars-cars}

Kurulu bir Forza'daki her aracı, oyunun kendi düşük ayrıntısıyla tek bir dosyaya yazar. Bu dosya görüntüleyicinin Yarış analizi sekmesi içindir: sürdüğünüz her tur için bir araç çizer. Böylece kaydedilen her araç kendi biçiminde ve gerçek boyutunda çizilir.

![cars --help çıktısı](../assets/img/cars-help.svg)

## Adım adım {#step-by-step}

1. **Çalıştırın.** Oyun kuruluyken (Steam kitaplıklarında ve `C:\XboxGames` içinde bulunur):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ya da oyunun klasörünü adıyla verin:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Görüntüleyicide yükleyin:** görünüm ayarlarındaki **Araç dosyasını yükle…** düğmesiyle, ya da dosyayı yarış sekmesine sürükleyip bırakarak. Dosya o tarayıcıda kalır. Araç numarası dosyadaki bir numarayla eşleşen turlar artık tam o aracın kendisiyle çizilir (bkz. görüntüleyicinin [yarış tekrarı belgeleri](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Oyuna yeni araçlar geldiğinde yeniden çalıştırın.** Birkaç saniye sürer ve yaklaşık 5 MB yazar.

## Seçenekler {#options}

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars`, ya da `HEAT3D_LEVELS` ayarlıysa `$HEAT3D_LEVELS/forza/forza.h3dcars` | yazılacak dosya |
| `--game FOLDER` | bulunan kurulu oyun | oyunun klasörü |

## Dosyada ne var {#what-is-in-the-file}

`media/Cars` altındaki her araç arşivi için: içindeki `ProxyLOD` modeli (yaklaşık 900 üçgen), telemetrinin belirttiği araç numarası, arşiv adından gelen marka, model etiketi ve yıl, tekerlekler ve arka stop ışıkları. Biçimler metre cinsindendir ve araçla 1:1 eşleşir. Böyle bir modeli olmayan bir arşiv (bir trafik nesnesi) adıyla anılır ve dışarıda bırakılır.

Dosya 3DHeat görüntüleyicisi için yapılmıştır. Başka yerde okumak isterseniz düzeni şöyledir ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Bölüm | Düzen |
|---|---|
| bütün dosya | gzip ile sıkıştırılmış |
| sihirli değer | 8 bayt `H3DCARS1` |
| başlık uzunluğu | küçük-uçlu (little-endian) u32 |
| başlık | UTF-8 JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| dolgu | veri 4 baytın katı olana kadar boşluk |
| veri | araç başına: köşeler üçer i16 olarak (milimetre; x sağa, y yukarı, z ileri), sonra üçgenler üçer u16 olarak |

Her `cars` girdisi şunlardır: `key`, `ordinals` (telemetrinin belirttiği araç numaraları), `make` (marka), `model`, `year` (yıl), `height` (yükseklik) ve `length` (uzunluk) (m), `wheels` (tekerlek başına `[x, y, z, radius]`, m), `lights` (stop ışığı noktaları `[x, y, z]`, m) ve `vertexAt`, `vertices`, `faceAt`, `faces` (verinin başından itibaren bayt konumları ve sayıları).

Dosya oyunun içeriğini taşır. Yalnızca üzerinde yapıldığı makinede kullanılmak içindir, başkalarına dağıtmak için değildir ([Kurallar ve lisanslar](rules-and-licences.md)).
