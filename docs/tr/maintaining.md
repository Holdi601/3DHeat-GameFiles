---
title: Bakım
nav_order: 99
lang: "tr"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Bakım: sürüm kontrol listesi {#maintaining-the-release-checklist}

Bir sürümü etiketlemeden önce (`v` + `VERSION` içindeki sayı), bu listeyi sırayla gözden geçirin. Sayfaların, resimlerin ve çevirilerin koda uygun kalmasını sağlar.

1. **Üretilen sayfaları yeniden üretin.**
   - `python tools/gen_docs_reference.py`, [Komut başvurusunu](../cli-reference.md) programın kendi `--help` çıktısından yeniden yazar. `python tools/gen_docs_reference.py --check` ise commit edilmiş sayfa eskiyse 1 koduyla çıkar.
   - `python tools/docs_diagrams.py --strings`, `docs/assets/img/` içindeki şemaları yeniden çizer ve `docs/assets/i18n/en.json` dosyasını yeniden yazar. Bu dosya çevrilecek her şema etiketinin listesidir.
2. **Son sürümden bu yana neyin değiştiğini listeleyin:** `git log --oneline v<last VERSION>..HEAD`. Her yeni komut, seçenek, çıktı alanı ya da davranış `CHANGELOG.md` dosyasında bir satır ve **Belgeler** tablosunda, onu açıklayan sayfayı adlandıran bir satır gerektirir. O sayfayı güncelleyin.
3. **Değişen sayfaları ve resimleri bağımsız biriyle gözden geçirin.** Bunları yazmamış biri (ya da bir ajan) üç kişi gibi okusun: hiç terminal kullanmamış bir yeni başlayan, 8 yaşında bir çocuk ve bir profesyonel. Şemalar da denetlenir: sayfa genişliğinde okunabilir olmalı, etiketler doğru olmalı ve renkler açıklanmış olmalı.
4. **Gözden geçirmenin bulduklarını düzeltin.** Sonra gerçek oyun verisinin sızmadığını denetleyin: harita, seviye ya da oyuncu adı yok; gerçek kayıtlardan ya da kurulumlardan hiçbir rakam yok. `<map>` gibi yer tutucular ya da "test seviyesi" kullanın.
5. **Değişen sayfaları yeniden çevirin.** Her çevrilmiş sayfa, üzerinden yapıldığı İngilizce sayfanın karmasını kaydeder. İngilizce kaynağı değişen sayfalar yeniden çevrilir, şema etiketleri de onlarla birlikte. Sonra her dili gözden geçirin: aynı üç okuyucu için açık olmalı, etiketler doğru olmalı ve sözcükler o dildeki görüntüleyici arayüzüyle uyumlu olmalı.
6. **Yalnızca kullanıcının onayından sonra gönderin.** Sahip onay vermeden hiçbir şey gönderilmez ya da etiketlenmez.

## Çeviriler: komutlar {#translations-the-commands}

Site, 3DHeat görüntüleyicisinin 40 diline çevrilmiştir. İngilizce `docs/` içindedir, diğer her dil aynı dosya adlarıyla `docs/<lang>/` içindedir. `tools/docs_i18n.py` kayıt işlerini yapar:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Yalnızca `todo`'nun listelediklerini çevirin. Markdown'ı, bağlantıları, kodu, dosya ve sütun adlarını olduğu gibi tutun. Başlıkları ve resim açıklamalarını çevirin. Görüntüleyicinin düğme ve panelleri için görüntüleyicinin kendi sözcüklerini kullanın (`src/i18n/locales/<lang>/`). Üretilmiş başvuru sayfaları ve terminal resimleri İngilizce kalır. Sitede eskimiş bir çeviri bunu söyler ve İngilizce sayfaya bağlanır. Eksik bir çeviri ise İngilizceye döner. Üstbilgideki dil menüsü ve ana sayfadaki tarayıcı diline göre yönlendirme `docs/_includes/` dizininden gelir.
