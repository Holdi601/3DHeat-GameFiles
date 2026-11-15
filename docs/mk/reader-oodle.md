---
title: "Oodle"
nav_order: 3
lang: "mk"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: се наоѓа, не се пакува {#oodle-found-not-bundled}

Најголемиот дел од испорачаната содржина на Unreal, и некои податоци на Frostbite, се компресирани со
**Oodle** (RAD Game Tools, сега Epic). Oodle е сопственички. Нема
верзија што смее да се дистрибуира, ниту имплементација во Python, а `oo2core_*.dll` е
лиценциран за производот што го испорачува. Затоа оваа алатка **наоѓа копија што веќе е на вашата
машина и ја вчитува**. Никогаш не носи своја. FModel и UModel работат на ист
начин.

Извор: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Каде бара {#where-it-looks}

Победува првата датотека што постои, по овој редослед:

1. Изрична патека дадена од повикувачот (Python API).
2. `HEAT3D_OODLE`: патека до DLL, или папка што содржи еден.
3. Плитко пребарување, едно ниво длабоко, во
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` на секоја библиотека на Steam

   За секоја подпапка `<game>` проверува `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` и
   `<game>\Engine\Binaries\Win64`.

Имиња на датотеки што се пробуваат, најновото прво: од `oo2core_9_win64.dll` надолу до
`oo2core_3_win64.dll`. Форматот е наназад компатибилен, па постара библиотека
обично сè уште работи.

Пребарувањето намерно **не** е рекурзивно скенирање на секој диск, што би
траело минути. Ако не најде ништо, поставете `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Папка работи исто како и самата датотека: во неа се пробуваат горенаведените имиња на DLL.

Инсталација на Unreal Engine носи една под `Engine\Binaries\ThirdParty\Oodle`,
што е најуредниот извор за програмер. Многу игри испорачуваат една покрај својата
извршна датотека. Игрите на Unreal 5 често го врзуваат Oodle статички и не испорачуваат DLL, па
пронајдената копија може да припаѓа на друга игра од архивата што се чита. Форматот
е ист во секој случај.

## Како се повикува {#how-it-is-called}

`OodleLZ_Decompress` се повикува преку `ctypes` со очекуваната излезна должина
(индексот на архивата секогаш ја знае, а Oodle не може да ја заклучи), безбедно за fuzz
декодирање вклучено (влезот не е доверлив), без проверка на CRC (SHA-1 на самиот pak
веќе ги покрива бајтите), и без нишки. Резултат со погрешна должина е грешка.
Библиотеката се вчитува еднаш по извршување.

## Кога нема ниедна {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Запис што не може да се декомпресира е грешка, никогаш веродостојно ѓубре.

Вчитувачот е само за Windows (бара `*_win64.dll`). Библиотеки за Linux и macOS
не се бараат.
