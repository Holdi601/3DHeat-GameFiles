---
title: "Oodle: намерен, не е включен"
nav_order: 3
lang: "bg"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: намира се на компютъра, не се включва {#oodle-found-not-bundled}

Повечето Unreal съдържания в игрите и някои Frostbite полезни товари са компресирани с **Oodle** (RAD Game Tools, сега Epic). Oodle е собствен софтуер. Няма версия за разпространение и няма имплементация на Python, а `oo2core_*.dll` е лицензиран за продукта, който го включва. Затова този инструмент **намира копие, вече налично на вашия компютър, и го зарежда**. Никога не носи такова. FModel и UModel работят по същия начин.

Източник: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Къде търси {#where-it-looks}

Печели първият файл, който съществува, в този ред:

1. Изричен път, подаден от извикващия (Python API).
2. `HEAT3D_OODLE`: път до DLL файла или до папка, която го съдържа.
3. Плитко търсене, на едно ниво навътре, в:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` на всяка Steam библиотека

   За всяка дъщерна папка `<game>` проверява `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` и `<game>\Engine\Binaries\Win64`.

Имената на файловете се пробват от най-новия: от `oo2core_9_win64.dll` до `oo2core_3_win64.dll`. Форматът е обратно съвместим, така че по-стара библиотека обикновено пак работи.

Търсенето умишлено **не** е рекурсивно сканиране на всеки диск, което би отнело минути. Ако не намери нищо, задайте `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Папката работи също толкова добре, колкото и самият файл: DLL имената по-горе се пробват вътре в нея.

Инсталация на Unreal Engine носи такава под `Engine\Binaries\ThirdParty\Oodle`, което е най-подреденият източник за разработчик. Много игри я слагат до своя изпълним файл. Игрите на Unreal 5 често свързват Oodle статично и не носят DLL, затова намереното копие може да принадлежи на друга игра, а не на архива, който се чете. Форматът е един и същ във всеки случай.

## Как се извиква {#how-it-is-called}

`OodleLZ_Decompress` се извиква през `ctypes` с очакваната дължина на изхода (индексът на архива винаги я знае, а Oodle не може да я отгатне), с включено безопасно декодиране при грешни данни (входните данни не са надеждни), без CRC проверка (SHA-1 на pak файла вече покрива байтовете) и без нишки. Резултат с грешна дължина е грешка. Библиотеката се зарежда веднъж за всяко стартиране.

## Когато няма {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Запис, който не може да се декомпресира, е грешка, никога правдоподобни боклуци.

Зареждачът работи само под Windows (търси `*_win64.dll`). Библиотеки за Linux и macOS не се търсят.
