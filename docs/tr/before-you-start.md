---
title: "Başlamadan önce"
nav_order: 2
lang: tr
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Başlamadan önce {#before-you-start}

Komut satırında yeni misiniz? Bu sayfa, yaklaşık on dakikada sizi hiçbir şeyden çalışan bir araca götürür. Komutları **terminal** denilen bir pencereye yazarsınız; araç metinle yanıt verir.

## 1. Python'u kurun {#install-python}

1. [python.org/downloads](https://www.python.org/downloads/) adresine gidin ve **Python 3.10 veya daha yeni** sürümünü indirin.
2. Kurulum programını çalıştırın. İlk ekranda **"Add python.exe to PATH"** (PATH'e python.exe ekle) kutusunu işaretleyin, sonra **Install Now** (Şimdi yükle) düğmesine tıklayın.

## 2. Aracı alın {#get-the-tool}

- **git ile:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **git olmadan:** [GitHub sayfasında](https://github.com/Holdi601/3DHeat-GameFiles) yeşil **Code** (Türkçe arayüzde **Kod**) düğmesine, sonra **Download ZIP** (ZIP dosyasını indir) seçeneğine tıklayın ve açın.

## 3. Aracın klasöründe bir terminal açın {#open-a-terminal-in-the-tools-folder}

- Dosya Gezgini'nde `README.md` dosyasını tutan klasörü açın. Adres çubuğuna tıklayın, `cmd` yazın ve Enter'a basın. Zaten o klasörde olan siyah bir pencere açılır.
- Ya da **Windows Terminal**'i açın ve `cd` ile oraya gidin:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Aracın ihtiyaç duyduğu şeyleri kurun {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

`Successfully installed ...` ile biten satırlar görmelisiniz.

## 5. Çalıştığını denetleyin {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

`usage: heat3d_gamefiles [-h]` ve fiillerin bir listesini görmelisiniz (`identify`, `list`, `extract`, `course`, ...). Bu başarı demektir: araç hazır.

## Örnekleri okumak {#reading-the-examples}

- `<something>` bir **yer tutucu**dur: kendi değerinizi yazın, köşeli parantezleri yazmadan. `<lap file>` örneğin `laps\my_lap.json` olur.
- Köşeli parantez içindeki `[--option]` **isteğe bağlıdır**: gerekmiyorsa bırakın.
- Boşluk içeren bir yol **çift tırnak** ister: `"C:\My Games\lap.json"`.
- Her komutu aracın klasöründe çalıştırın (3. adım).

## Bir şey ters giderse {#when-something-goes-wrong}

| Gördüğünüz | Ne yapmalı |
|---|---|
| `'python' is not recognized` | Python kurulu değil ya da "Add to PATH" işaretlenmedi. Kurulum programını yeniden çalıştırın, kutuyu işaretleyin, sonra yeni bir terminal açın. |
| `No module named heat3d_gamefiles` | Terminal yanlış klasörde. `README.md` dosyasını tutan klasöre `cd` ile gidin. |
| `No module named numpy` (ya da başka bir ad) | 4. adım atlanmış. `pip install -r requirements.txt` çalıştırın. |
| bir yolla birlikte `can't open file` / `not found` | Yolda boşluk var ve tırnak yok, ya da yazım hatası. Yolu çift tırnak içine alın. |

Daha fazla ileti ve çözümleri: [Sorun giderme](../troubleshooting.md).
