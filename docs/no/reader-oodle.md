---
title: "Oodle: funnet, ikke med"
nav_order: 3
lang: "no"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: funnet, ikke med {#oodle-found-not-bundled}

Det meste delte Unreal-innhold, og noen Frostbite-nyttelaster, er komprimert med
**Oodle** (RAD Game Tools, nå Epic). Oodle er proprietær. Det finnes ingen
videredistribuerbar utgave og ingen Python-implementasjon, og `oo2core_*.dll` er
lisensiert til produktet som leverer den. Så dette verktøyet **finner en kopi som
allerede er på maskinen din og laster den**. Det leverer aldri en egen. FModel og
UModel fungerer på samme måte.

Kilde: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Hvor det leter {#where-it-looks}

Den første filen som finnes, vinner, i denne rekkefølgen:

1. En eksplisitt sti sendt av kalleren (Python-API).
2. `HEAT3D_OODLE`: en sti til DLL-en, eller en mappe som har en.
3. Et grunt søk, én mappe dypt, i
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - hvert Steam-biblioteks `steamapps\common`

   For hver undermappe `<game>` sjekkes `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` og
   `<game>\Engine\Binaries\Win64`.

Filnavnene som prøves, nyeste først: `oo2core_9_win64.dll` ned til
`oo2core_3_win64.dll`. Formatet er bakoverkompatibelt, så et eldre bibliotek fungerer
som regel også.

Søket er bevisst **ikke** et rekursivt søk over alle diskene, som ville tatt minutter.
Finner det ingenting, sett `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

En mappe fungerer like godt som selve filen: DLL-navnene over prøves inni den.

En installasjon av Unreal Engine har en under `Engine\Binaries\ThirdParty\Oodle`, som er
den ryddigste kilden for en utvikler. Mange spill har en ved siden av den kjørbare filen.
Unreal 5-spill lenker ofte Oodle statisk og leverer ingen DLL, så kopien som finnes, kan
tilhøre et annet spill enn arkivet som leses. Formatet er det samme uansett.

## Hvordan det kalles {#how-it-is-called}

`OodleLZ_Decompress` kalles gjennom `ctypes` med den forventede utdatalengden (arkivets
indeks vet alltid den, og Oodle kan ikke utlede den), feilsikker dekoding på (inndataene er
ikke pålitelige), ingen CRC-sjekk (pakens egen SHA-1 dekker bytene allerede), og
ikke-trådet. En resultatlengde som er feil, er en feil. Biblioteket lastes én gang per kjøring.

## Når det ikke finnes noen {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

En oppføring som ikke kan dekomprimeres, er en feil, aldri plausibel søppel.

Lasteren er bare for Windows (den leter etter `*_win64.dll`). Linux- og macOS-biblioteker
søkes ikke etter.
