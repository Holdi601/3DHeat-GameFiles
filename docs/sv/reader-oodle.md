---
title: Oodle
nav_order: 3
lang: "sv"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: hittas, inte medlevererad {#oodle-found-not-bundled}

Det mesta av det Unreal-innehåll som levereras, och en del Frostbite-data, är komprimerat med **Oodle** (RAD Game Tools, nu Epic). Oodle är proprietär programvara. Det finns ingen version som får spridas fritt och ingen Python-implementation, och `oo2core_*.dll` är licensierad till den produkt som levererar den. Därför **letar detta verktyg efter en kopia som redan finns på din dator och läser in den**. Det bär aldrig med sig en egen. FModel och UModel fungerar på samma sätt.

Källa: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Var den letar {#where-it-looks}

Den första fil som finns vinner, i den här ordningen:

1. En uttrycklig sökväg som anroparen skickar in (Python-API:et).
2. `HEAT3D_OODLE`: en sökväg till DLL-filen, eller till en mapp som innehåller en.
3. En grund sökning, en nivå djup, i
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - varje Steam-biblioteks `steamapps\common`

   För varje undermapp `<game>` kontrollerar den `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` och `<game>\Engine\Binaries\Win64`.

Filnamnen som testas, nyast först: från `oo2core_9_win64.dll` ned till `oo2core_3_win64.dll`. Formatet är bakåtkompatibelt, så ett äldre bibliotek fungerar oftast ändå.

Sökningen är med flit **inte** en rekursiv genomsökning av varje enhet, eftersom det skulle ta minuter. Hittar den ingenting, ange `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

En mapp fungerar lika bra som filen själv: DLL-namnen ovan testas inuti den.

En installation av Unreal Engine har en under `Engine\Binaries\ThirdParty\Oodle`, vilket är den renaste källan för en utvecklare. Många spel levererar en bredvid sin körbara fil. Unreal 5-spel länkar ofta Oodle statiskt och levererar ingen DLL, så kopian som hittas kan höra till ett annat spel än arkivet som läses. Formatet är detsamma i båda fallen.

## Hur den anropas {#how-it-is-called}

`OodleLZ_Decompress` anropas via `ctypes` med den förväntade utdatalängden (arkivindexet vet alltid den, och Oodle kan inte räkna ut den), med fuzz-säker avkodning på (indata är inte betrodd), utan CRC-kontroll (pak-filens egen SHA-1 täcker redan byten) och utan trådar. Ett resultat med fel längd är ett fel. Biblioteket läses in en gång per körning.

## När det inte finns någon {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

En post som inte går att packa upp är ett fel, aldrig trovärdigt skräp.

Inläsaren fungerar bara på Windows (den letar efter `*_win64.dll`). Bibliotek för Linux och macOS letas inte efter.
