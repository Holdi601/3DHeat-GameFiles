---
title: Unreal .pak
nav_order: 1
lang: "tr"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

Unreal 4.22-5.x `.pak` arşivlerini **listeler ve çıkarır**: sürüm 8, 9, 10, 11 ve 12; Zlib, Gzip ve Oodle sıkıştırması; ve AES anahtarını siz verdiğinizde şifreli arşivler. Çıkardığı şeyi (`.uasset`, `.umap`) yorumlamaz.

Kaynak: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Komutlar: `identify`, `list`, `extract` (bkz. [Komutlar](commands.md)).

## Düzen {#layout}

Altbilgi dosyanın sonundadır ve son 1.024 baytta `0x5A6F12E1` sihirli sayısı aranarak bulunur. Alan sırası önemlidir:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Şifreleme bayrağı, sihirli sayıdan **önce** gelir. Sihirli sayıdan sonra okunursa "Z"den (Zlib'in) denk gelir. O zaman her arşiv kendini şifreli olarak bildirir ve her sıkıştırma yöntemi adı ilk harfini kaybeder ("lib", "odle"): sessiz ve inandırıcı bir hata. Sürüm düşük bayttır, çünkü "frozen index" yapıları yüksek biti ayarlar.

İndeks, bağlama noktasını, yol-karma indeksini, tam dizin indeksini ve **kodlanmış girdiler** bloğunu tutar: bir bayrak sözcüğünün hangi sayıların 32 bit olduğunu söylediği, bit paketlenmiş bir biçim; sıkıştırma yöntemi (6 bit), girdinin şifreli olup olmadığı, blok sayısı (16 bit) ve 2.048'in katları cinsinden blok boyutu (6 bit). Tümü bir olan blok boyutu bir kaçıştır: gerçek boyut, ofsetten **önce** bir u32 olarak gelir. Büyük bir arşivde, bunu boyutlardan sonra okumak girdilerin %7'sini dört bayt kaydırdı ve onlara exabayt mertebesinde ofsetler verdi.

Her girdinin tam kaydı, yükünden hemen önce tekrarlanır; bu yüzden yük `8+8+8+20+4+1+4` bayttan sonra başlar; sıkıştırılmışsa ek olarak `4 + 16 x blocks`. Şifreli bloklar 16 bayta dolgulanır.

## Ne okur, ne reddeder {#what-it-reads-and-what-it-refuses}

| Durum | Sonuç |
|---|---|
| sürüm 8-12 | okunur |
| başka her sürüm | `pak version N; this reader handles 8-12` (eski sürümler düz bir kayıt listesi saklar ve test edilecek bir dosya yoktu) |
| sihirli sayı yok | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks dosyanın dışında | reddedilir: altbilgi iddia edildiği gibi ayrıştırılmadı |
| yalnızca yol-karma indeksi | reddedilir: dosya adları yapım sırasında karmalandı ve kurtarılamaz |
| indeksin taşma listesindeki girdiler (dizin ofseti -1) | atlanır, uydurulmaz |
| şifreli indeks, anahtar yok | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Komut satırında tek satır ve 1 çıkış kodu |
| şifreli girdi, anahtar yok | okurken `EncryptedPak` |
| Zlib, Gzip, Oodle yöntemleri | açılır (Oodle bir kütüphane ister, bkz. [Oodle](reader-oodle.md)) |
| başka her yöntem | `compression method '...' is not supported` |

## Anahtarlar {#keys}

`list` ve `extract` üzerindeki `--key`, zaten sahip olduğunuz bir AES-256 anahtarını alır: 64 onaltılık basamak olarak, `0x` ile ya da onsuz. Başka her şey, arşiv açılmadan önce reddedilir ve çıkış kodu 2 olur. Şifre çözme AES-256-ECB ile `cryptography` paketi üzerinden yapılır. Bir anahtarı elde eden hiçbir kod yolu yoktur: paketlenmiş anahtar yok, çalıştırılabilir dosya araması yok, bellek okuma yok. Bkz. [Kurallar ve lisanslar](rules-and-licences.md).

## Doğrulandı {#verified}

Birden çok oyunun paketlenmiş arşivlerine karşı, her girdi, çok büyük bir arşivdekiler dahil, her yükün önünde Unreal'in yazdığı SHA-1 ile eşleşti. Bu hash saklandığı gibi baytları kapsar, yani bir eşleşme; indeks çözümünün, yük ofsetinin ve her sıkıştırılmış blok sınırının doğru olduğu anlamına gelir. Kurulu oyun testleri (`test_pak.py`), `steamapps\common\*\...\Content\Paks` altında bulunan en çok dört şifrelenmemiş pak üzerinde bunu yineler. Her girdinin ofsetinin dosyanın içinde olduğunu ve her arşiv için rastgele 150 girdilik bir örneklemde SHA-1'in eşleştiğini denetlerler.
