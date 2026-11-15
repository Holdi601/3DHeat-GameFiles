---
title: Tur girdileri
nav_order: 7
lang: "tr"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Tur girdileri {#lap-inputs}

Bir **tur dosyası**, x, y, z noktalarından oluşan bir listedir: arabanın nereye gittiği. Elle yazılabilen en hızlı tur dosyası, aşağıdaki [5. Bir `.csv` tablosu](#5-a-csv-table) başlığındaki CSV'dir.

Bir tur, parkur dışa aktarımına **arabanın nereye gittiğini** söyler. Dosyadaki başka hiçbir şey kullanılmaz: hız, girdiler ve g kuvvetleri 3DHeat'in telemetri tarafına aittir. Araç, oyunun kendi dünya metrelerindeki konumları okur; dosyanın bunu söylediği yerde oyunu ve parkuru da okur.

Kaynak: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## `course` neyi kabul eder {#what-course-accepts}

Biçim, dosyaya bakılarak tanınır; yalnızca `.npz` ve `.csv` uzantıya göre tanınır, diğer her şey JSON olarak denenir.

### 1. Bir `heat3d-lap` belgesi (her oyun) {#a-heat3d-lap-document-any-game}

3DHeat telemetri kaydedicileri (`heat3d_capture telemetry` ([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))) tarafından yazılır:

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y`, `channels.z` zorunludur. Üçünden herhangi biri sonlu bir sayı olmayan satırlar atılır. Diğer kanallar yok sayılır.
- `game` dışa aktarımı belirler (bkz. [Komutlar](commands.md#which-game)).
- `track`, Assetto Corsa Rally'nin adı geçen etabı önce denemesi için kullanılır.
- Eksenler: y yüksekliktir. Forza ve AC Rally turları, kaydedicinin yazdığı gibi oyunun yatay eksenlerini kullanır. BeamNG turları, görüntüleyici çerçevesinde, yani BeamNG'nin Z-yukarı dünyasının `(x, z, -y)` halinde beklenir (bkz. [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Bir rota dosyası {#a-route-file}

`heat3d_capture route` ve `heat3d_capture laps` tarafından yazılır:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions`, `[x, y, z]` değerlerinin bir listesidir. `bounds` içeren ama konumları olmayan bir rota dosyası da çalışır: iki köşesi dejenere bir çizgi olsa da kullanılabilir bir kutudur.

### 3. Bir FH Companion tur dosyası {#an-fh-companion-lap-file}

FH Companion'ın kayıtlı kütüphanesinin tur başına dosyaları:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Eksik bir `X`, `Y` ya da `Z` 0 olarak okunur. Dosyalar bayt sıra işaretiyle (byte-order mark) yazılır; bu yüzden tüm JSON'lar `utf-8-sig` olarak okunur.

### 4. Bir `.npz` kaydı {#a-npz-recording}

`positions` adlı, (n, 3) şeklinde bir dizi içeren bir NumPy arşivi.

### 5. Bir `.csv` tablosu {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- `x`, `y`, `z` adlı sütunlar zorunludur (büyük/küçük harf ve çevredeki boşluklar yok sayılır). Diğer sütunlar yok sayılır.
- `#` ile başlayan satırlar atlanır. **İlk** satır `# {json}` ise, onun `game` ve `track` değerleri okunur.
- Sayı olarak ayrıştırılamayan satırlar atlanır.

### 6. Bir klasör {#a-folder}

Bir klasör `.json`, `.npz` ve `.csv` dosyaları için **özyinelemeli** olarak aranır ve hepsi tek bir sürülen çizgide birleştirilir. Kayıtlı bir parkur böyle saklanır: FH Companion sınıf, araba, ayar ve etiket klasörleri iç içe koyar.

- `course.json` adıyla atlanır (o bir tur değil, üst veridir).
- Okunamayan bir dosya sessizce atlanır. Yüzlerce dosyadan biri bozuksa diğerleri etkilenmez.
- Konsol kaç tur dosyasının alındığını bildirir (`12 laps, 18,400 samples`).
- Klasör, dosyalarının adını verdiği oyunu alır; ama yalnızca **bir** oyun adı veriyorlarsa. Oyun adı vermeyen bir dosya (bir FH Companion turu, `course.json`, açıklama satırı olmayan bir CSV) saymaz; bu yüzden bir oyunun kayıtları arasındaki böyle bir dosya, klasörün oyununu kaybettirmez. İki farklı oyun adı veren dosyalar bir karışımdır ve klasör hiçbir oyunu almaz. Oyunu olmayan bir klasör, `--game` başka bir şey demedikçe Forza olarak dışa aktarılır.
- Hiçbir şey okunamazsa: "no readable laps under <folder>".

### 7. Bir parkur adı {#a-course-name}

Argüman mevcut bir dosya ya da klasör değilse, FH Companion kütüphanesinde bir parkur adı olarak aranır: `%LOCALAPPDATA%\FHCompanion\laps`.

1. adı (` (course_...)` eki çıkarılmış hali) eşit olan bir klasör (büyük/küçük harf duyarsız);
2. aksi halde adını içeren tek klasör.

Yani `"Example Circuit"`, koordinatları kimse bilmeden `Example Circuit (course_1200_3400_to_1175_3400)` klasörünü bulur. Birden çok eşleşme, hepsini listeleyen bir hatadır. Adla bulunan bir parkurun oyunu yoktur; `--game` başka bir şey demedikçe Forza olarak dışa aktarılır.

## `terrain --route` neyi kabul eder {#what-terrain---route-accepts}

`terrain`, rota dosyasının `bounds` değerini ister (yukarıdaki 2. şekil), `{"min": [x, y, z], "max": [x, y, z]}`. `bounds` olmadan şu mesajla durur: "<file> has no bounds; --route takes a route file with "bounds": {...}". Dosya bayt sıra işaretiyle ya da onsuz UTF-8 olarak okunur, tüm JSON turları gibi. Aynı dosyada yukarıdaki kurallarla okunabilen en az 10 konum varsa, bunlar kesimi bir koridora daraltır ve ayrıntıyı yönlendirir.

## Tur nasıl kullanılır {#how-the-lap-is-used}

| Kullanım | Ayrıntı |
|---|---|
| ad | dosyanın adı ya da klasörün adı (` (course_...)` çıkarılmış); varsayılan çıktı dosya adı olur |
| sürülen mesafe | ardışık örnekler arasındaki boşlukların toplamı (`m driven` olarak yazılır; bir klasörde dosyalar arasındaki atlamalar da dahildir) |
| kutu | x ve z aralığı `--margin` kadar genişletilmiş; yükseklik asla sınırlanmaz |
| koridor | turdaki her örneğin x ve z'si, bkz. [Parkur dışa aktarma](course-export.md#the-corridor) |
| ayrıntı | yerleştirilmiş her kopyanın en yakın örneğe mesafesi, bkz. [Ayrıntı düzeyleri ve bütçe](detail-budget.md) |

İkiden az örneği olan bir tur reddedilir ("holds no driving").

## Hatalar {#errors}

| Mesaj | Anlamı |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | dosya JSON değil (ve `.npz` ya da `.csv` değil) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | başka bir biçimde JSON |
| `<file> has no x, y and z columns` | bu başlıkları olmayan bir CSV |
| `<file> has no positions array` | `positions` içermeyen bir `.npz` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | bir ad, ama FH Companion kütüphanesi yok |
| `'<name>' matches 3 courses: A, B, C` | daha belirgin olun |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | yalnızca ad aramalarında ve `courses` için |
