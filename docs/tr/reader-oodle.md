---
title: "Oodle: bulunur, dahil edilmez"
nav_order: 3
lang: "tr"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: bulunur, dahil edilmez {#oodle-found-not-bundled}

Çoğu paketlenmiş Unreal içeriği ve bazı Frostbite yükleri **Oodle** ile sıkıştırılır (RAD Game Tools, şimdi Epic). Oodle özel bir yazılımdır. Yeniden dağıtılabilir bir sürümü ve bir Python uygulaması yoktur. `oo2core_*.dll` dosyası, onu dağıtan ürüne lisanslıdır. Bu yüzden bu araç **makinenizde zaten bulunan bir kopyayı bulur ve yükler**. Hiçbir zaman bir kopya taşımaz. FModel ve UModel de aynı şekilde çalışır.

Kaynak: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Nerede arar {#where-it-looks}

İlk var olan dosya kazanır. Sıra şöyledir:

1. Çağıran tarafından verilen açık bir yol (Python API).
2. `HEAT3D_OODLE`: DLL'in yolu ya da bir tane içeren bir klasör.
3. Şu klasörlerde, yalnızca bir düzey derinliğinde bir arama:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - her Steam kitaplığının `steamapps\common` klasörü

   Her alt `<game>` klasörü için `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` ve `<game>\Engine\Binaries\Win64` denetlenir.

Denenen dosya adları en yenisinden başlar: `oo2core_9_win64.dll`'den `oo2core_3_win64.dll`'e kadar. Biçim geriye uyumludur, bu yüzden eski bir kitaplık genellikle yine çalışır.

Arama bilerek her sürücüyü özyinelemeli olarak taramaz. Bu dakikalar sürerdi. Hiçbir şey bulunamazsa `HEAT3D_OODLE` ayarlayın:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Bir klasör de dosyanın kendisi kadar işe yarar. Yukarıdaki DLL adları o klasörün içinde denenir.

Bir Unreal Engine kurulumu, DLL'i `Engine\Binaries\ThirdParty\Oodle` altında taşır. Bir geliştirici için en düzenli kaynak budur. Birçok oyun, DLL'i çalıştırılabilir dosyasının yanında dağıtır. Unreal 5 oyunları Oodle'ı çoğu zaman statik olarak bağlar ve hiç DLL dağıtmaz. Bu yüzden bulunan kopya, okunan arşivin oyunundan başka bir oyuna ait olabilir. Biçim her iki durumda da aynıdır.

## Nasıl çağrılır {#how-it-is-called}

`OodleLZ_Decompress`, `ctypes` üzerinden çağrılır. Beklenen çıktı uzunluğu verilir (arşiv dizini bunu her zaman bilir, Oodle ise bunu kendisi çıkaramaz). Hataya dayanıklı çözme açıktır, çünkü girdi güvenilmez. CRC denetimi yoktur, çünkü pak dosyasının kendi SHA-1 değeri baytları zaten kapsar. Çözme tek iş parçacıklıdır. Yanlış uzunlukta bir sonuç hatadır. Kitaplık her çalıştırmada bir kez yüklenir.

## Hiç bulunamazsa {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Çözülemeyen bir girdi bir hatadır. Asla inandırıcı görünen çöp veri değildir.

Yükleyici yalnızca Windows içindir (`*_win64.dll` arar). Linux ve macOS kitaplıkları aranmaz.
