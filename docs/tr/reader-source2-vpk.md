---
title: Source 2 `.vpk`
nav_order: 6
lang: "tr"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

Valve'ın VPK arşivlerini (sürüm 1 ve 2) **listeler ve çıkarır**. Bölünmüş arşivleri ve dizin dosyasının içinde saklanan verileri de kapsar. Her girdi kendi CRC değerine karşı denetlenebilir. Burada bu, satıcısının kendisinin belgelediği tek kapsayıcı biçimidir. Oyunlar: Counter-Strike 2, Dota 2, Half-Life: Alyx ve Source 2 üzerindeki diğerleri.

Kaynak: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Komutlar: `identify`, `list`, `extract`.

## Düzen {#layout}

```
u32 magic 0x55AA1234, u32 version (1 or 2), u32 tree size
  (version 2: 16 more header bytes; header 12 or 28 bytes)
directory tree:
  extension        "vmdl_c", then "vtex_c", ..., then ""
    path           "maps/example_map", then ""
      file name    "world_layer0", then ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Her biri boş bir dizgiyle biten üç iç içe döngü vardır. Sayı bekleyen bir okuyucu hiçbirini bulamaz. Yollar grup başına bir kez saklanır ve üç parçasından yeniden birleştirilir. Tek bir boşluk "klasör yok" ya da "uzantı yok" anlamına gelir.
- Her kayıt `0xFFFF` ile biter. Bu denetlenir. Yerini kaybetmiş bir okuyucu hemen durur ("the directory is not being read at the right offset": dizin doğru konumdan okunmuyor).
- **Bölünmüş arşivler:** `pak01_dir.vpk` dizini tutar. Veri ise `pak01_000.vpk`, `pak01_001.vpk`... içindedir ve girdinin arşiv numarasıyla seçilir.
- **Arşiv numarası `0x7FFF`** baytların, ağaçtan sonra dizin dosyasının içinde olduğu anlamına gelir. Bunu gerçek bir numara gibi okuyan bir okuyucu `pak01_32767.vpk` arar.
- **Ön yükleme:** küçük dosyalar dizinde bütün olarak saklanır. Bu durumda uzunluk 0 bir hata değildir.

## Komutlar {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` sürümü, girdi sayısını ve ilk `.nav` dosyasını yazar. `list` her girdiyi `stored` olarak gösterir, çünkü VPK sıkıştırma yapmaz. `extract` baytları CRC denetimi yapmadan yazar. Python'da `VpkArchive(path).verify(name)`, bir girdinin baytlarını dizinin kaydettiği CRC ile karşılaştırır.

## Gezinme ağı {#the-navigation-mesh}

Bir harita, derlenmiş geometrisinin yanında **gezinme ağını** (`maps/<map>.nav`) da taşır. Oyuncu konumlarının ısı haritası için bu ikisinden çok daha kullanışlıdır. Gezinme ağı yürünebilir zemindir, zaten hesaplanmıştır ve boyutu bunun binde biridir. Kurulu oyun testi, dağıtılan bir haritanın `.nav` dosyasının Source gezinme sihirli değeri `CE FA ED FE` ile başladığını denetler.

## Doğrulandı {#verified}

Bir oyunun dağıtılan harita arşivlerindeki örneklenen her girdi, CRC değerine karşı bayt bayt doğru çıktı ve her harita arşivi ayrıştırılıyor. Kurulu oyun testleri, en çok dört harita arşivinin her birinden rastgele 25 girdide CRC denetimini tekrarlar.

## Henüz uygulanmadı {#not-implemented}

- Source 2'nin derlenmiş varlıklarının (`.vmdl_c`, `.vtex_c`) çözülmesi. Bunlar kendi parçalı ikili dosyalarıdır. Unreal ve Frostbite ağ biçimleriyle aynı türden bir iş. Ayrı 3DHeat CS2 aracı CS2 harita geometrisini işler.
- CS2 gezinme ağının çözülmesi. Biçimi 36. sürümdür ve yaygın olarak belgelenmiş Source 1 biçiminden farklıdır. Baytları sıkıştırılmış değil, yapılıdır (entropi 6.2, %31'i sıfır). Ancak sözcüklerin yalnızca %3'ü koordinat olarak okunur. Yani düzen açık olan değildir ve henüz çözülmemiştir.
