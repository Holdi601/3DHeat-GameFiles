---
title: "Oodle: пронађен, није испоручен"
nav_order: 3
lang: "sr"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: пронађен, није испоручен {#oodle-found-not-bundled}

Већина испоручене Unreal садржине и неки Frostbite садржаји компресовани су помоћу **Oodle** (RAD Game Tools, сада Epic). Oodle је власнички. Не постоји дистрибутивна верзија и нема Python имплементације, а `oo2core_*.dll` је лиценциран производу који га испоручује. Зато овај алат **проналази примерак који је већ на вашем рачунару и учитава га**. Никад га не носи са собом. FModel и UModel раде на исти начин.

Извор: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Где тражи {#where-it-looks}

Први фајл који постоји побеђује, тим редом:

1. Изричита путања коју прослеђује позивалац (Python API).
2. `HEAT3D_OODLE`: путања до DLL-а, или фолдер који га садржи.
3. Плитка претрага, један ниво дубине, у:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` сваке Steam библиотеке

   За сваки подфолдер `<game>` проверава `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` и `<game>\Engine\Binaries\Win64`.

Имена фајлова која проба, од најновијег: `oo2core_9_win64.dll` до `oo2core_3_win64.dll`. Формат је уназадно компатибилан, па старија библиотека обично и даље ради.

Претрага намерно **није** рекурзивно скенирање свих дискова, које би трајало минутима. Ако ништа не нађе, поставите `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Фолдер ради једнако добро као и сам фајл: имена DLL-ова горе се пробају унутар њега.

Инсталација Unreal Engine-а садржи један под `Engine\Binaries\ThirdParty\Oodle`, што је најуредније место за програмера. Многе игре испоручују један поред свог извршног фајла. Unreal 5 игре често повезују Oodle статички и не испоручују DLL, па пронађени примерак може припадати другој игри од оне чији архив се чита. Формат је исти у сваком случају.

## Како се позива {#how-it-is-called}

`OodleLZ_Decompress` се позива преко `ctypes` с очекиваном дужином излаза (индекс архива то увек зна, а Oodle то не може закључити), декодирање отпорно на грешке укључено (улаз је непоуздан), без CRC провере (SHA-1 самог pak-а већ покрива бајтове), и без нити. Резултат погрешне дужине је грешка. Библиотека се учитава једном по покретању.

## Кад га нема {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Унос који се не може декомпресовати је грешка, никад веродостојно смеће.

Учитавач је само за Windows (тражи `*_win64.dll`). Linux и macOS библиотеке се не траже.
