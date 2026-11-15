---
title: Komutlar
nav_order: 2
lang: "tr"
source: commands.md
source_hash: "db876ce4e110"
nav_exclude: true
search_exclude: true
---
# Komutlar {#commands}

Her komut, depo klasöründen `python -m heat3d_gamefiles <verb> ...` olarak çalışır. Komutlar, genellikle ihtiyaç duyulan sırayla dizilmiştir: bu dosya nedir, içinde ne var, bana şunu ver, ve bir turu bir parkura çevir.

| Komut | Alır | Ne yapar |
|---|---|---|
| [`identify`](#identify) | herhangi bir dosya | baytlarını okuyarak kapsayıcı biçimini adlandırır |
| [`list`](#list) | bir Unreal `.pak` veya IoStore `.utoc`, bir Source 2 `.vpk`, bir ForzaTech `.minizip` ya da bir zip | girişlerini listeler |
| [`extract`](#extract) | aynısı | bir girişi diske yazar |
| [`meshes`](#meshes) | bir Unity `SerializedFile` | mesh'lerini listeler ve denetler |
| [`course`](#course) | bir tur | onun etrafındaki parkuru dışa aktarır (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | kaydedilmiş bir tur kitaplığı | içindeki her parkur için `course` çalıştırır (Forza) |
| [`races`](#races) | kurulu bir Forza | oyunun tanımladığı her yarışı listeler: neyi eklediği, neyi gizlediği, mekânlar, dışa aktarımının durumu |
| [`terrain`](#terrain) | bir Forza parkur klasörü | dünya koordinatlarıyla bir bölgeyi keser |
| [`levels`](#levels-and-level-frostbite) | kurulu bir Frostbite oyunu (Battlefield 6) | bölümlerini listeler |
| [`level`](#levels-and-level-frostbite) | bir bölümün adı | bölümü dışa aktarır: arazi, yerleştirilmiş mesh'ler, isteğe bağlı olarak renk haritaları (Battlefield 6) |
| [`cars`](#cars) | kurulu bir Forza | her araba düşük ayrıntıda, görüntüleyicinin yarış sekmesi için tek bir dosyada |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | bir Unreal 5 oyunu | World Partition haritalarını listeler |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | bir haritanın adı | haritayı dışa aktarır: arazi, HLOD yapıları, su |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | kurulu bir Arma Reforger | dünyalarını listeler |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | bir dünyanın adı | dünyayı dışa aktarır: renkleriyle arazi, deniz, binalar kutu olarak |

**Örnekleri okumak:** `<x>`, kendi değerinizle değiştirin anlamına gelir; açılı parantezleri yazmayın. `[...]` isteğe bağlıdır. Boşluk içeren bir yolu "çift tırnak" içine alın, örneğin `"C:\Games\My Game"`. Yeni misiniz? Bkz. [Başlamadan önce](before-you-start.md). Her komutun tam `--help` çıktısı [Komut başvurusu](../cli-reference.md) sayfasındadır.

Program her başladığında, önce daha yeni bir sürüm olup olmadığına bakabilir. Bkz. [Güncellemeler](updates.md). `HEAT3D_NO_UPDATE=1` bu denetimi kapatır.

Kaynak: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Adım adım sayfalar: [Arşivleri incelemek](inspecting-archives.md), [Parkur dışa aktarma](course-export.md),
[Tam bölümler](whole-levels.md), [Forza arabaları](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Çıkış kodları {#exit-codes}

| Kod | Anlamı |
|---|---|
| 0 | başarılı |
| 1 | iş başarısız oldu (okunamayan tur, oyun bulunamadı, dışa aktarılacak bir şey yok, `courses` içindeki bir parkur başarısız oldu; `list` ve `extract` için, okudukları arşivlerden hiçbiri olmayan bir dosya, açılamayan ya da okunamayan bir dosya (`--key` olmadan şifreli bir pak, şifreli bir IoStore kapsayıcısı) ya da arşivde olmayan bir giriş) |
| 2 | hatalı argümanlar (argparse), var olmayan bir yol, 64 onaltılık basamak olmayan bir `--key`, ya da `terrain`'in `--box` ve `--route`'tan ikisini birden ya da hiçbirini almaması |

`list` ve `extract` hataları, standart hata çıktısında her biri tek bir satırdır; bir Python izlemesi değildir.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Bu, dosyayı okur ve hangi kapsayıcı olduğunu söyler. Uzantıya bakmaz (tek istisna, aşağıdaki `.ucas`tır). Biçimleri şu sırayla dener ve ilk ayrıştırılanda durur:

1. **Unreal `.pak`**: dosyanın son 1.024 baytında pak sihirli değeri olan bir altbilgi. Sürümü, dizin ofsetini ve boyutunu, dizinin şifreli olup olmadığını ve sıkıştırma yöntemlerini yazar.
2. **Unreal IoStore `.utoc`**: başında IoStore sihirli değeri. Sürümü, parça sayısını ve kapsayıcının şifreli olup olmadığını yazar; şifreli değilse, dizininin adlandırdığı dosya sayısını (ve hangi bağlama noktası altında), sıkıştırma yöntemlerini ve `.ucas` dosyasının yanında olup olmadığını. Bir `.ucas`'ın kendi başlığı yoktur; yanında aynı adlı `.utoc` tarafından tanınır ve `identify` bu dosyayı adlandırır.
3. **ForzaTech `.minizip`**: `PGZP` sihirli değeri. Sürümü, giriş ve segment sayılarını ve girişleri adlandıran `ChunkContentsMiniZip<n>.txt` dosyasının yanında olup olmadığını yazar (ve varsa, girişler kadar satır içerip içermediğini).
4. **zip**: başta bir zip yerel dosya başlığı. Giriş sayısını, en yaygın altı uzantıyı ve girişler `levels/<name>/` altındaysa bölüm adlarını yazar, BeamNG.drive bölüm arşivlerinde olduğu gibi.
5. **Unity**: bir `UnityFS` paketi (motor sürümünü ve giriş sayısını yazar) ya da çıplak bir `SerializedFile` (biçimi, motor sürümünü, nesne sayısını ve en yaygın altı sınıfı yazar).
6. **Frostbite `.toc`**: türünü (`plain` ya da `signed`), ağacın nerede başladığını ve ya parça sayısını (ikili bölüm tablosu) ya da süper paket sayısını (DbObject ağacı) yazar.
7. **Source 2 `.vpk`**: sürümü, giriş sayısını ve varsa ilk `.nav` gezinme mesh'ini yazar.
8. **BeamNG `.cdae`**: ayrıştırılan şekil sürümü 31. Mesh sayısını, çizilen ayrıntı seviyelerinin sayısını ve ilk malzemeleri yazar.
9. **BeamNG `.ter`**: sihirli değer yok, bu yüzden hepsinin tutması gerekir: 2 ile 16.384 arası bir kenar, o sayının karesi kadar yükseklik ve katman baytı, sonra 1 ile 255 arası yazdırılabilir katman adı. Sürümü, boyutu ve katman adlarını yazar.
10. **ForzaTech `.modelbin`**: sürümü, parça sayısını ve en yaygın altı parça etiketini yazar. Parça içerikleri burada çözülmez.

Kendi sihirli değeri olan biçimler (2 ile 4) Unity ve Frostbite'tan önce gelir; bu ikisinin denetimleri dosyanın tamamını okur ve bir Forza arşivi on gigabaytlarca olabilir.

Hiçbiri eşleşmezse `not a format this tool reads` (bu aracın okumadığı bir biçim) ve son nedeni yazar. Bu neden ForzaTech denetiminden gelir.

Örnek (sahte):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<archive>` | zorunlu | bir Unreal `.pak`; bir IoStore `.utoc` (ya da yanındaki `.ucas`); bir Source 2 `.vpk` (bölünmüş VPK'lar için `_dir.vpk`); bir ForzaTech `.minizip`; BeamNG'nin bölüm ve içerik arşivleri gibi bir zip |
| `--filter TEXT` | yok | yalnızca TEXT'i içeren yollar, büyük/küçük harf duyarsız |
| `--limit N` | 50 | en fazla N girişi yazdırır (toplam sayı her zaman yazılır) |
| `--key HEX` | yok | zaten sahip olduğunuz bir AES-256 anahtarı, 64 onaltılık basamak, `0x` ile ya da onsuz. Yalnızca şifreli bir `.pak` bunu kullanır. 64 onaltılık basamak olmayan her şey, arşiv açılmadan reddedilir (çıkış kodu 2) |

Araç biçimi baytlardan belirler: bir IoStore içindekiler tablosu, bir `.minizip` ve bir VPK, başladıkları imzaya göre; bir zip, yerel dosya başlığına göre; bir `.pak` de sonundaki altbilgiye göre. `.ucas`'ın başlığı yoktur ve aynı adlı `.utoc` üzerinden açılır. Bunların hiçbiri olmayan bir dosya `<file> is not an archive list and extract read (...)` ile reddedilir. Olup da açılamayan bir dosya, okuyucunun nedeniyle reddedilir: `--key` olmadan şifreli bir pak, şifreli bir IoStore kapsayıcısı, okumadığı bir pak sürümü. Her iki durumda da tek satır ve çıkış kodu 1'dir.

Her satır, sıkıştırılmamış boyutu, sıkıştırma yöntemini ve yolu gösterir:

| Arşiv | Yöntem | Yollar |
|---|---|---|
| `.pak` | `none`, ya da altbilgiden gelen ad (`Zlib`, `Oodle`, `Gzip`...) | arşivin bağlama noktasıyla, örneğin `../../../Game/Content/...` |
| IoStore `.utoc` | `none`, ya da kapsayıcının yöntemi (`Oodle`, `Zlib`...), ilk bloğu nasıl saklandığına göre | bağlama noktasıyla, örneğin `../../../<Project>/Content/...`. Dizin indeksi olmayan bir kapsayıcı hiçbir dosya adlandırmaz ve reddedilir |
| `.vpk` | her zaman `stored` | dizinde olduğu gibi |
| `.minizip` | `lz4`, `deflate` ya da `stored` | `GeoChunk<n>.minizip` yanındaki `ChunkContentsMiniZip<n>.txt` nasıl yazıyorsa öyle, derleme makinesinin ön eki çıkarılmış (oyunun yazdığı gibi ters eğik çizgilerle). Arşiv hiçbir ad saklamaz; o dosya olmadan girişler `#0`, `#1`... olur. Satır sayısı girişlerden farklı bir liste reddedilir: ikisi birbirine ait değildir |
| zip | `stored`, `deflate`, ... | saklandığı gibi; klasörler listelenmez |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<archive>` | zorunlu | `list` ile aynı |
| `<entry>` | zorunlu | `list`'in yazdığı yol aynen (büyük/küçük harf duyarlı); bir `.minizip`'te `#<number>` de çalışır |
| `--out FILE` | girişin dosya adı (son `/` ya da `\` sonrası), geçerli klasörde | nereye yazılacağı; üst klasörler oluşturulur |
| `--key HEX` | yok | `list` ile aynı |

Giriş çözülür (pak, anahtarla), açılır ve yazılır. `<bytes> bytes -> <file>` yazdırır. Yol arşivde yoksa komut çıkış kodu 1 ile biter. Okunamayan bir girişte de öyle (anahtarsız şifreli bir giriş, Oodle ile sıkıştırılmış ama Oodle kitaplığı olmayan), nedeni tek satırda yazılarak. Bir VPK girişinin CRC'si burada denetlenmez. Okuyucunun bunun için bir `verify()` yöntemi vardır (bkz. [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<path>` | zorunlu | çıplak bir Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), bir paket değil |
| `--limit N` | 25 | en fazla N mesh'i çözer ve yazdırır |

Bu, `Mesh` nesnelerinin sayısını, sonra mesh başına bir satır yazdırır: adı (ilk 40 karakter), vertex ve üçgen sayıları, ve `ok` ya da `BOUNDS DISAGREE`. `BOUNDS DISAGREE`, çözülmüş vertex'lerin Unity'nin mesh için sakladığı sınır kutusunu, kutu boyutunun %2'si içinde yeniden üretmediği anlamına gelir. Bu, ayrıştırmanın kendi denetimidir (bkz. [Unity](reader-unity.md)). Okunamayan bir mesh nedeniyle birlikte bildirilir ve sınıra dahil edilir. Bir `.resS` dosyasındaki vertex verisi, kapsayıcının bulunduğu klasörden okunur.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Bu, bir turun etrafındaki parkuru dışa aktarır: sürüşün iki yanındaki bir şeritteki zemin ve üstündekiler, tek bir `.glb` olarak. Gerisini kendisi çözer: hangi oyun, hangi kurulu kopya, hangi parkur, bölüm ya da etap, ve (Assetto Corsa Rally için) eksenlerin hangi yönde olduğu. Bkz. [Parkur dışa aktarma](course-export.md).

`<lap>`, şunlardan biri olabilir (ayrıntılar [Tur girdileri](lap-inputs.md) sayfasında):

- bir tur dosyası: rota JSON'u, FH Companion tur JSON'u, `heat3d-lap` JSON'u, `.npz`, ya da x, y, z sütunlu bir `.csv`
- bir tur dosyaları klasörü, özyinelemeli aranır (kaydedilmiş bir parkurun tamamı)
- bir parkur **adı**, `%LOCALAPPDATA%\FHCompanion\laps` içindeki FH Companion kitaplığında aranır

### Seçenekler {#options}

| Seçenek | Varsayılan | Oyunlar | Anlamı |
|---|---|---|---|
| `-o`, `--out FILE` | geçerli klasörde `<course name>.glb`, ya da o ayarlıysa `$HEAT3D_LEVELS/<game>/courses/` içinde | hepsi | nereye yazılacağı; ad küçük harfe çevrilir, diğer karakter dizileri `_` olur |
| `--game {forza,beamng,acrally}` | tur dosyasının dediği, yoksa `forza` | hepsi | turun hangi oyundan olduğu |
| `--margin M` | 80 | hepsi | sürüşün iki yanında tutulan zemin, metre |
| `--texture-size {2048,1024,512}` | 2048 | hepsi | 512 m'lik parkur karesi başına zemin dokusu pikseli (2048 = piksel başına 25 cm) |
| `--no-textures` | kapalı | hepsi | yalnızca düz renkler: çok daha küçük bir dosya. Forza için bu, yol/kenar ayrımını da atlar (aşağıya bakın) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | hangi mevsimin zemin haritaları ve model dokuları |
| `--no-placed` | kapalı | hepsi | yalnızca arazi: bordür, bariyer, tabela, bina yok. BeamNG için, mesh olarak modellenmiş sürüş yüzeyi yine tutulur |
| `--trees` | kapalı | hepsi | bitki örtüsünü de yerleştirir (Forza: ağaçlar, çalılar ve kırılabilirler; BeamNG: ağaçlar; AC Rally: ağaçlar ve örneklenmiş yapraklık) |
| `--detail-budget N` | otomatik | hepsi | yerleştirilen her şey için bir üçgen tavanı; bkz. [Ayrıntı seviyeleri ve bütçe](detail-budget.md) |
| `--track DIR` | aranır | Forza | kurulu oyun aranmayacaksa parkur klasörü (`media\Tracks` altında, `GeoChunk0.minizip` tutan) |
| `--level NAME` | turdan bulunur | BeamNG, AC Rally | bölüm (BeamNG klasör adı) ya da etap (AC Rally harita adı), büyük/küçük harf duyarsız |
| `--install DIR` | Steam kitaplıklarında aranır | BeamNG, AC Rally | BeamNG: `gameengine.zip` tutan klasör. AC Rally: oyun klasörü, ya da onun `acr\Content\Paks` / `Content\Paks` klasörü |

Bir oyun için geçerli olmayan seçenekler, uyarı olmadan yok sayılır. Örneğin `--season` BeamNG ve AC Rally için bir şey yapmaz; `--track` de onlar için bir şey yapmaz.

### Hangi oyun {#which-game}

Oyun, önce `--game`'den, sonra bir `heat3d-lap` dosyasının `game` alanından (ya da bir CSV'nin `# {...}` açıklama satırından) alınır; yoksa Forza varsayılır. Bir klasör, dosyaları yalnızca birini adlandırıyorsa o oyunu alır; hiçbiri adlandırmayan bir dosya (bir FH Companion turu, `course.json`, açıklama satırı olmayan bir CSV) sayılmaz (bkz. [Tur girdileri](lap-inputs.md)).

| Değer | Dışa aktarma |
|---|---|
| `forza` ile başlar | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` ya da `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | reddedilir: "keeps all its content in one package obfuscated with a key, and this tool recovers none" (tüm içeriğini anahtarla karıştırılmış tek bir pakette tutar ve bu araç hiçbirini kurtarmaz) |
| `iracing` | reddedilir: "tracks ship in a protected format that is not a file-extraction target" (parkurlar, dosya çıkarma hedefi olmayan korumalı bir biçimde gönderilir) |
| başka her şey | reddedilir: "there is no course reader for <game> yet" (<game> için henüz bir parkur okuyucusu yok) |

Bir ret, alternatifleri de önerir: parkuru oynanıştan yeniden kurmak (3DHeat GameCapture), ya da parkursuz turları analiz etmek, çünkü görüntüleyicinin Yarış analizi sekmesi onlardan bir yol çizer.

### Örnekler {#examples}

```
# A course from the FH Companion library, by name
python -m heat3d_gamefiles course "Example Circuit"

# One lap file, a narrower band, a smaller file
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter textures, trees included
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# A hard ceiling of 500,000 placed triangles
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# A track folder given directly (game installed outside Steam)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: name the level, point at the install
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, with a plain CSV lap that does not say its game
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Örnek çıktı (Forza, sahte sayılar):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Kurulu bir Forza'nın her arabası, oyunun kendi düşük ayrıntısında, görüntüleyicinin yarış sekmesi için tek bir dosyada: `media/Cars` altındaki her araba arşivinin taşıdığı `ProxyLOD` modeli, yaklaşık 900 üçgen; arabanın numarası telemetrinin söylediği gibi, markası, model etiketi ve yılı arşivin adından, ve tekerlekleri ve arka lambaları. Saniyeler sürer ve yaklaşık 5 MB yazar. Oyun yeni arabalar aldığında yeniden çalıştırın. Böyle bir modeli olmayan bir arşiv (bir trafik nesnesi) adlandırılır ve dışarıda bırakılır. Biçim [`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py) içindedir.

Şekiller metredir, oyunun kendi ölçeğinde: arabayla 1:1. Dosya oyunun içeriğini taşır; bu yüzden yapıldığı makine içindir, dolaştırmak için değil.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Bu, kaydedilmiş bir tur kitaplığındaki her parkur klasörü için Forza `course` dışa aktarmasını çalıştırır ve her biri için bir `<name>.glb` yazar. Yalnızca Forza içindir. Forza dışa aktarmasını doğrudan çağırır; `--game`, `--level` ya da `--install` okumaz.

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `-o`, `--out FOLDER` | `courses`, ya da `$HEAT3D_LEVELS/forza/courses` ayarlıysa o | yazılacak klasör (yoksa oluşturulur) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | tur kitaplığı |
| `--only TEXT [TEXT ...]` | hepsi | yalnızca klasör adlarında bunlardan biri geçen parkurlar (büyük/küçük harf duyarsız) |
| `--force` | kapalı | zaten `.glb`'si olanları yeniden dışa aktarır |
| `--track DIR` | aranır | `course` ile aynı |
| `--margin M` | 80 | `course` ile aynı |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | `course` ile aynı |

Bir parkur klasörü nedir: kitaplığın doğrudan bir alt klasörü, adı ` (course_` içeren; FH Companion onları böyle adlandırır, örneğin `Example Circuit (course_1200_3400_to_1175_3400)`. Adın ` (course_`'tan sonraki kısmı atılır.

Bir çalıştırma şöyle davranır:

- Zaten `.glb`'si olan bir parkur atlanır (`kept`), `--force` verilmedikçe; böylece kesintiye uğrayan bir çalıştırma kaldığı yerden devam eder.
- Eski bir sürümün yazdığı, yarışın kendi katmanı ve mekânları olmayan bir `.glb` (`asset.extras.course_format` yok ya da mevcut sürümden düşük) yalnızca onun için `--force` verilmiş gibi yeniden dışa aktarılır.
- Ad öncesi ` (course_` aynı olan iki parkur klasörü (eski bir parkurun adını yeni bir parkura veren bir kaydedici) birbirinin üstüne yazmaz: önce oluşturulan klasör `<name>.glb`'yi tutar, diğeri `<name>_<start>.glb` olarak yazılır, `<start>` nerede başladığıdır, eksi işaretleri `m` ile (örneğin `example_circuit_m120_m340.glb`).
- Başarısız olan bir parkur (okunamayan turlar, bellek yetersizliği, arazi yok...) `FAILED` olarak bildirilir ve çalıştırma devam eder.
- Sonunda durum, MB cinsinden boyut, geçen saniye ve ad içeren bir tablo yazdırır, ardından `<n> of <total> courses in <folder>`.
- Herhangi bir parkur başarısız olursa çıkış kodu 1'dir.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races {#races}

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Kurulu bir Forza'nın tanımladığı her yarışı, rota tanımlarından listeler (bkz. [Forza Horizon parkurları](course-forza-horizon.md#which-race)) ve bir `courses` klasöründeki dışa aktarımları onlara karşı denetler. Oyunu ve tur kitaplığını okur; isteğe bağlı tablo dışında hiçbir şey yazmaz.

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` ile aynı | `courses`'un yazdığı klasör, denetlenen dosyaları |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | tur kitaplığı |
| `--track DIR` | aranır | parkur klasörü, kurulu oyununki değilse |
| `--markdown FILE` | yok | tabloyu ayrıca orada Markdown olarak da yazar |

Yarış başına bir satır, ve üzerinde sürülen kaydedilmiş parkur başına bir satır:

| Sütun | Anlamı |
|---|---|
| route | rota kimliği |
| course | ona eşleşen kaydedilmiş parkur, varsa |
| own assets | yarışın serbest dolaşım dünyasına eklediği kopyalar |
| drawn | bunların, parkurun gönderdiği modeli olanları |
| kinds | eklenen kopyalar türe göre (barriers, props, decals, infrastructure, ...) |
| not geometry | seyirci işaretçileri ve çarpışma eğrileri, sayılmış |
| hidden | yarışın kaldırdığı serbest dolaşım nesneleri |
| venue | yarışın YZ çizgisinin 10 m içinden geçtiği mekân zemini modelleri |
| export | `current` (güncel), `older format` (`courses` tarafından yeniden dışa aktarılacak), `not exported` (dışa aktarılmamış), ya da kaydedilmiş parkuru olmayan bir yarış için boş |

Bir sayımla biter: `<n> races: <a> with assets of their own, <v> through a venue, <d> driven in the lap library, <s> recorded courses to export again` (<n> yarış: <a> tanesinin kendi varlıkları var, <v> tanesi bir mekândan geçiyor, <d> tanesi tur kitaplığında sürüldü, <s> kaydedilmiş parkur yeniden dışa aktarılacak).

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Bu, her şeyi elle belirttiğiniz Forza kesimidir: bir tur değil, bir parkur klasörü ve bir bölge verirsiniz. Alan bir sürüş yerine bir kutu olduğunda işe yarar.

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<path>` | zorunlu | bir Forza parkur klasörü, `media\Tracks` altında (`GeoChunk*.minizip` tutan) |
| `-o`, `--out FILE` | zorunlu | yazılacak `.glb` |
| `--box X0 Z0 X1 Z1` | | bölge, oyunun metrelerinde (x ve z, telemetrinin bildirdiği gibi); köşeler herhangi bir sırada |
| `--route FILE` | | `"bounds": {"min": [x, y, z], "max": [x, y, z]}` içeren bir rota JSON'u, `heat3d_capture route` ve `heat3d_capture laps`'in yazdığı gibi; UTF-8 olarak okunur, bayt sıra işaretiyle ya da onsuz |
| `--margin M` | **100** | bir rotanın sınırlarına eklenen metre, ve rotanın bir çizgisi varsa koridor genişliği |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | `course` ile aynı |

`--box` ile `--route`tan tam olarak birini verin; aksi halde çıkış kodu 2 olur. `--route` ile kesim, rotanın `bounds` alanının (`min`/`max`, x ve z) margin ile genişletilmiş hali olur. Dosya ayrıca en az 10 konum içeriyorsa, kesim onların etrafında `--margin` metrelik bir koridora daralır ve yerleştirilmiş modeller ayrıntılarını bu çizgiye uzaklıklarına göre alır. `--box` ile bütün kutu tutulur ve ayrıntı, kutunun ortasına en yakın olanlara gider.

Yükseklik kesimin hiçbir zaman parçası değildir. Haritanın dışında ya da denizdeki bir kutu, bir koordinat hatası değil, "no terrain there" (orada arazi yok) verir (çıkış kodu 1).

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels`, kurulu bir Frostbite oyununun gönderdiği bölümleri, tablolarının adıyla (`levels/<level>/<level>.toc`) listeler; boyutu ve nereden geldiğiyle: temel oyun için `Data`, bir güncelleme için `Update/<pack>`, ve ona kaç yüksek çözünürlüklü tablonun eklendiği. Bir güncellemenin gönderdiği bir bölümün, temel oyunda da yalnızca parçaların küçük bir tablosu vardır; bölümün bağlantılarını taşıyan tablo bölümdür (bkz. [Frostbite](reader-frostbite.md#which-table-is-the-level)). `level` birini dışa aktarır: arazi yükseklik alanını, bölümün statik model gruplarının yerleştirdiği her mesh'i, tek tek yerleştirilen nesneleri ve nerede durduklarını ve bölümün haritanın etrafındaki arazi arka planını. `--textures` ile her yüzey kendi renk haritasını taşır; `--navmesh` ile askerlerin üstünde yürüdüğü yüzeyler de gelir. Nasıl okunduğu [Frostbite](reader-frostbite.md) sayfasındadır.

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<level>` | zorunlu | `levels`'in yazdığı bir ad, bir adın benzersiz bir parçası, ya da bir bölümün `.toc` yolu |
| `-o`, `--out FILE` | `<level>.glb` (`$HEAT3D_LEVELS/<game>/` içinde, o ayarlıysa) | yazılacak `.glb` |
| `--install FOLDER` | `layout.toc` içeren `Data` klasörüne sahip ilk Steam oyunu | oyunun klasörü |
| `--textures [PIXELS]` | kapalı; boyut verilmeden verilirse 512 | her yüzeyin renk haritasını, bir kenarı PIXELS'i geçmeyen en büyük mip ile, ve doku koordinatlarını oyunun sahip olduğu gibi, tekrarlayan bir örnekleyiciyle yazar (bkz. [Çıktı biçimi](output-format.md)). Yükseklik alanı, arka plan arazisinin renk haritası onu kapsıyorsa ondan renk alır; değilse arazinin yüzey malzemelerinin orta rengi; o da yoksa arka planın ortalama rengi. Kapalıyken her parça düz bir renktir |
| `--ground-texture [METRES]` | kapalı; boyut verilmeden verilirse 0,5 | arazi decal'lerini (yollar, pistler, apronlar, boyalı işaretler) zemin rengi üzerine pişirir; bölümün renk haritası varsa onunla çarpılarak yükseklik alanının rengine, piksel başına METRES ve en fazla 4.096 piksellik karolar halinde (`ground:terrain x<x> z<z>`). `--textures` ile ya da olmadan çalışır |
| `--navmesh` | kapalı | en küçük ajanın, askerin (1,8 m boy, 0,4 m genişlik), gezinme mesh'ini `nav:walkable` parçası olarak ekler: asker'in ulaşabildiği zemin, döşemeler, merdivenler ve çatılar, bunları birbirine bağlayan bağlantılar (atlamalar, merdivenler, aşmalar) olmadan |
| `--ground-spacing METRES` | 4 | yükseklik alanının en ince aralığı; bundan daha ince düğümler seyreltilir. 0, yükseklik alanını dışarıda bırakır |
| `--detail-budget N` | her kopya kendi en kaba seviyesinde, artı dörtte bir, en az 1.500.000 | bir üçgen tavanı. En çok maliyeti olan mesh'ler bir ayrıntı seviyesini aynı anda düşürür, sığana dek; en kaba seviyeler de sığmazsa en küçük kopyalar önce dışarıda bırakılır. Arazi arka planı hiçbir zaman kabalaştırılmaz ya da dışarıda bırakılmaz |
| `--skip TEXT` | | adı TEXT içeren statik model gruplarını dışarıda bırakır; birkaç kez verilebilir. Bir oyun modunun katmanı, örneğin |
| `--by-mesh` | kapalı | bir parçanın ne olduğunu bulmak için: kaynak mesh ve malzeme başına bir parça, `<part> \| <mesh> \| <material>` adıyla; çok daha büyük bir dosya |
| `--clamped-uvs` | kapalı | bir dokuyu tekrarlayamayan bir çizici için: her dokulu üçgeni, koordinatları 0..1 içinde kalan parçalara keser ve 4'ten fazla parçaya ihtiyaç duyan bir üçgeni dokusunun ortalama renginde çizer, `<part> (average colour)` parçasında |

Gruplar ve her birinin kaç kopya yerleştirdiğini, dışarıda bırakılan mesh'leri ve nedenlerini, parça başına üçgenleri (ve `--textures` ile kaç dokunun ve kaç bölümün renk haritasını bulduğunu), zeminin ne olduğunu ve `--navmesh` ile kaç gezinme karosu okunduğunu yazdırır. Geometrinin dışında bölüm hakkında hiçbir şey yazılmaz: ad yok, meta veri yok (bkz. [Çıktı biçimi](output-format.md)).

Arazi bütçesi ayrıdır: yükseklik alanı ve arka plan `--detail-budget` tarafından hiçbir zaman kabalaştırılmaz; `--ground-spacing` yükseklik alanının boyutunu belirler.

Bütün bir bölüm büyüktür: tipik olarak on milyonun üstünde üçgen ve birkaç yüz MB. `--textures` dosyaya biraz ekler; ağaçlarla dolu bir bölüm yaklaşık 1 GB'a ulaşabilir. `--textures 256 --detail-budget 3000000 --ground-spacing 8` bunu kabaca üçte birine indirir.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>`, oyunun klasörü, `Content/Paks` klasörü ya da bir Steam kitaplığındaki klasör adıdır (`"<Steam game folder name>"`). `ue-maps`, yanlarında pişmiş World Partition hücreleri olan her haritayı listeler. `ue-map` birini `ground:<map>` (arazi), `structure:<map>` (haritanın birleştirilmiş HLOD mesh'leri) ve `water:<map>` (zeminin üstünde durdukları yerlerdeki su gövdeleri) olarak dışa aktarır; Unreal **santimetre** biriminde, Y ve Z yer değiştirmiş halde: metre olmayan tek dışa aktarma budur. Her birinin nasıl okunduğu ve denetlendiği: [Unreal 5 haritaları](level-unreal-world-partition.md).

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<map>` | zorunlu | `ue-maps`'in yazdığı bir ad, ya da bir adın benzersiz parçası |
| `-o`, `--out FILE` | `<map>.glb` (`$HEAT3D_LEVELS/<game>/` içinde, o ayarlıysa) | yazılacak `.glb` |
| `--ground-spacing METRES` | 2 | arazinin dosyadaki vertex aralığı, kendi karelerinin tam bir sayısına yuvarlanmış |
| `--no-structures`, `--no-water` | | o parçayı dışarıda bırakır |

Parça başına üçgenleri, kaç arazi bileşeninin okunduğunu ve bunların iki kez sakladığı vertex'lerin kaçının birbirini tutmadığını yazdırır. 2 m'de 3 km'lik bir harita yaklaşık 4,6 milyon zemin üçgenidir.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds`, bir araziye sahip her dünyayı `worlds/` altındaki klasörüyle listeler. `enfusion-world` birini dışa aktarır: `ground:<world>` (arazi, süper doku karelerinin renkleriyle), `water:<world>` (deniz, sıfır yükseklikte) ve `structure:<world>` (yerleştirilmiş her modelin kutusu), oyunun kendi metrelerinde: x doğu, y yukarı, z kuzey. Her birinin nasıl okunduğu ve denetlendiği: [Arma Reforger dünyaları](level-arma-reforger.md).

| Seçenek | Varsayılan | Anlamı |
|---|---|---|
| `<world>` | zorunlu | `enfusion-worlds`'in yazdığı gibi bir dünya |
| `-o`, `--out FILE` | `<world>.glb` (`$HEAT3D_LEVELS/<game>/` içinde, o ayarlıysa) | yazılacak `.glb` |
| `--install FOLDER` | oyunu tutan Steam kitaplığı | oyunun klasörü |
| `--ground-spacing METRES` | 2 (arazinin kendisi) | arazinin dosyadaki vertex aralığı |
| `--texture-size PIXELS` | 4096 | zemin renk görselinin büyük kenarı; düz renk için 0 |
| `--no-structures` | | yerleştirilmiş modelleri dışarıda bırakır |
| `--trees` | kapalı | ağaçları ve diğer bitki örtüsünü de yerleştirir, kutular olarak |

Parça başına üçgenleri, kaç karo kenarı vertex'inin birbirini tutmadığını, dünya dosyasının kaç varlık tuttuğunu ve kaç kutu yerleştirildiğini, ve neyin neden dışarıda bırakıldığını yazdırır.

## Ortam değişkenleri {#environment-variables}

| Değişken | Etkisi |
|---|---|
| `HEAT3D_OODLE` | bir `oo2core_*_win64.dll` yolu, ya da onu tutan klasör; bkz. [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | `-o` olmadan yapılan her dışa aktarma için tek bir klasör: her oyunun çıktısı `<HEAT3D_LEVELS>/<game>/` içine gider (parkurlar `<game>/courses/` içinde, araba paketi `forza/` içinde). Ayarlı değilse geçerli klasöre gider |
| `HEAT3D_NO_UPDATE` | boş, `0`, `false`, `no` dışındaki herhangi bir değer güncelleme denetimini kapatır; bkz. [Güncellemeler](updates.md) |
| `LOCALAPPDATA` | FH Companion kitaplığının, BeamNG'nin kullanıcı klasörünün ve güncelleme önbelleğinin aranacağı yer |
| `HEAT3D_COURSE` | yalnızca testler: kurulu oyun üzerindeki bordür testinin kullandığı parkur; bkz. [Geliştirme](development.md) |
