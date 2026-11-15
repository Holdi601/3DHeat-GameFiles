---
title: "Oodle"
nav_order: 3
lang: "da"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: fundet, ikke medleveret {#oodle-found-not-bundled}

Det meste af det udleverede Unreal-indhold og nogle Frostbite-nyttelaster er komprimeret med
**Oodle** (RAD Game Tools, nu Epic). Oodle er proprietært. Der findes ingen build, der må
videregives, og ingen Python-implementering, og `oo2core_*.dll` er licenseret til det produkt, der leverer den.
Så dette værktøj **finder en kopi, der allerede ligger på din maskine, og indlæser den**. Det
medleverer aldrig en. FModel og UModel virker på samme måde.

Kilde: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Hvor den leder {#where-it-looks}

Den første fil, der findes, vinder, i denne rækkefølge:

1. En eksplicit sti, som kalderen angiver (Python-API'et).
2. `HEAT3D_OODLE`: en sti til DLL'en, eller en mappe, der indeholder en.
3. En overfladisk søgning, én mappe dyb, i
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - hver Steam-biblioteks `steamapps\common`

   For hver undermappe `<game>` kontrolleres `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` og
   `<game>\Engine\Binaries\Win64`.

Filnavne, der prøves, nyeste først: `oo2core_9_win64.dll` ned til
`oo2core_3_win64.dll`. Formatet er bagudkompatibelt, så et ældre bibliotek virker
som regel stadig.

Søgningen er med vilje **ikke** en rekursiv gennemgang af alle drev, for det ville
tage minutter. Finder den intet, så sæt `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

En mappe virker lige så godt som selve filen: DLL-navnene ovenfor bliver prøvet inde i den.

En Unreal Engine-installation har en under `Engine\Binaries\ThirdParty\Oodle`,
og det er den pæneste kilde for en udvikler. Mange spil leverer en ved siden af deres
eksekverbare fil. Unreal 5-spil linker ofte Oodle statisk og leverer ingen DLL, så
kopien, der findes, kan høre til et andet spil end det arkiv, der læses. Formatet er
det samme under alle omstændigheder.

## Sådan kaldes den {#how-it-is-called}

`OodleLZ_Decompress` kaldes via `ctypes` med den forventede outputlængde (arkivets indeks kender
altid den, og Oodle kan ikke gætte den), fuzz-sikker dekodning slået til (inputtet er
ikke pålideligt), ingen CRC-kontrol (pakkens egen SHA-1 dækker allerede bytene), og
uden tråde. Et resultat med forkert længde er en fejl. Biblioteket indlæses én gang pr. kørsel.

## Når der ikke findes nogen {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

En post, der ikke kan dekomprimeres, er en fejl, aldrig plausibelt skrald.

Indlæseren virker kun på Windows (den leder efter `*_win64.dll`). Biblioteker til Linux og macOS
bliver ikke søgt efter.
