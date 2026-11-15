---
title: Güncellemeler
nav_order: 13
lang: "tr"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Güncellemeler {#updates}

3DHeat GameFiles başladığında bu deponun GitHub sürümlerini denetler, yeni bir sürüm çıktığını söyler ve güncellemeyi önerir. Sizin kendi dosyalarınıza (turlar, dışa aktarmalar) hiçbir zaman dokunulmaz.

Kaynak: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Kurulu sürüm, depodaki [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) dosyasındaki sürümdür.

## Başlangıçtaki denetim {#the-check-at-start-up}

Her `python -m heat3d_gamefiles ...` çalıştırması, argümanlarını ayrıştırmadan önce denetimi çağırır:

- Denetim, **5 saniye** zaman aşımıyla `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` adresini sorar.
- Yanıt, `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` içinde **6 saat** önbelleğe alınır (`LOCALAPPDATA` yoksa `~/.cache/3DHeat/...`). Bu süre içinde istek yapılmaz. "Henüz sürüm yok" (HTTP 404) yanıtı da önbelleğe alınır.
- Çevrimdışıysanız, istek sınırına takıldıysanız ya da bir vekil sunucunun arkasındaysanız denetim sessizce döner ve araç sahip olduğu sürümle çalışır.
- En son sürümün etiketi (`v1.2.3` ya da `1.2.3`; `-` ya da `+` sonrasındaki her şey yok sayılır) `VERSION`'dan yeniyse stderr'e şunu yazar:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Bir terminalde** (stdin ve stderr ikisi de TTY) `Update now? [Y/n]` diye sorar. Enter, `y`, `yes`, `j` ya da `ja` güncellemeyi yapar. Başarılı bir güncellemeden sonra **aynı komut** yeni kodla yeniden başlatılır ve çıkış kodu geçirilir.
- **Terminal olmadan** (zamanlanmış bir çalıştırma, bir boru) yalnızca ``Run `python -m heat3d_update` in <folder> to update.`` yazar ve devam eder.

## İstek üzerine güncelleme {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Bu her zaman GitHub'a sorar (önbellek kullanılmaz). `Up to date: 1.0.1.`, `No release found (...)` ya da ne yaptığını yazar. Güncelleme uygulanamazsa çıkış kodu 1 olur.

## Güncelleme nasıl uygulanır {#how-an-update-is-applied}

| Şöyle kurulmuşsa | Güncelleme |
|---|---|
| bir **git klonu** (bir `.git` klasörü ve PATH üzerinde `git`) | `git pull --ff-only`. İzlenen dosyalarda yerel değişiklik varken **reddedilir**: "this checkout has local changes; commit or stash them, then run `git pull`". İzlenmeyen dosyalar buna engel olmaz |
| bir **indirilmiş kopya** | sürümün kaynak arşivi (`zipball_url`) indirilir ve geçici bir klasöre açılır. Dışarı çıkmaya çalışan her yol yok sayılır. Arşivin `VERSION` değeri sürümün sürümüne eşit olmalıdır, değilse hiçbir şey kopyalanmaz. Sonra dosyalar bu klasörün üzerine kopyalanır |

Bir arşivden kopyalanırken sürümün parçası olmayan dosyalar (turlar, dışa aktarmalar, sanal ortamlar, sizin yaptığınız her şey) olduğu gibi bırakılır. Güncelleyici ayrıca, bir sürümün paketlerinden kaldırdığı `.py` modüllerini silmeyi dener. Böylece eski bir modül, yerini alacak olanı gölgelemez. Arşivin kök dizininde ve bir alt klasöründe `heat3d_*` paketlerine bakar; sürümün artık sahip olmadığı `.py` dosyalarını siler.

## Kapatmak {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Boş olmayan, `0`, `false` ya da `no` dışındaki her değer hem başlangıçtaki denetimi hem de teklifi kapatır. `python -m heat3d_update` elle çalıştırıldığında yine çalışır.
