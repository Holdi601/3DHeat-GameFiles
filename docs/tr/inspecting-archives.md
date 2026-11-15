---
title: Arşivleri inceleme
nav_order: 3
lang: "tr"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Arşivleri inceleme: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Oyunlar dosyalarını **arşiv** denen büyük kutulara koyar. Bu komutlar bir kutunun etiketine bakar, içindekileri listeler ve bir şeyi dışarı çıkarır.

Bilmediğiniz bir oyundan bir şey dışa aktarmadan önce neler içerdiğine bakın. Bu dört komut bir dosyayı okur, ne olduğunu ve ne tuttuğunu söyler. İstediğiniz `extract` girdisi dışında hiçbir şey yazmaz.

![identify, list ve extract küçük bir zip üzerinde çalıştırıldı](../assets/img/inspect-archives.svg)

*BeamNG.drive seviyesi gibi düzenlenmiş yapay bir zip üzerinde bir çalıştırma.*

## Adım adım {#step-by-step}

1. **Dosyanın ne olduğunu sorun.** `identify` uzantıya değil, baytlara bakar:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Biçimin adını (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity paketi ya da `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ya da `.modelbin`, BeamNG `.cdae`/`.ter`, zip), sürümünü, kaç girdi tuttuğunu ve şifreli olup olmadığını söyler.

2. **İçindekileri listeleyin.** `list` her girdi için bir satır yazar: boyut, sıkıştırma, yol. `--filter` ile daraltın, `--limit` ile sınırlayın:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Bir girdiyi dışarı çıkarın.** `extract` tek bir girdiyi yazar (`--out` ile başka bir yer belirtmezseniz bulunduğunuz klasöre). Yolu `list`'in yazdığı gibi verin ya da adı olmayan bir `.minizip` içinde numarasıyla (`#12` gibi) belirtin:

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes`, bir `SerializedFile` içindeki ağları listeler ve denetler:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Seçenekler {#options}

| Komut | Seçenek | Anlamı |
|---|---|---|
| `identify` | `<file>` | herhangi bir dosya |
| `list` | `<archive>` | `.pak`, `.utoc` (ya da yanındaki `.ucas`), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | yalnızca içinde TEXT geçen yollar |
| | `--limit N` | en fazla N satır |
| | `--key HEX` | elinizde olan bir AES-256 anahtarı (64 onaltılık basamak); yalnızca şifreli bir `.pak` bunu ister |
| `extract` | `<archive> <path>` | arşiv ve girdinin `list`'in yazdığı yolu |
| | `--out FILE` | nereye yazılacağı (varsayılan: girdinin dosya adı) |
| | `--key HEX` | `list` ile aynı |
| `meshes` | `<file>`, `--limit N` | bir Unity `SerializedFile`; en fazla N ağ |

Araç hiçbir anahtar içermez ve bir anahtarı geri kazanmaz. Şifreli bir arşiv yalnızca sizin verdiğiniz bir anahtarla açılır. Okuyamadığı bir dosya tek satırla reddedilir ve çıkış kodu 1 olur. Her komut ve çıkış kodu [Komutlar](commands.md) sayfasında, her biçimin nasıl okunduğu ise [Arşiv okuyucuları](archive-readers.md) altındadır.
