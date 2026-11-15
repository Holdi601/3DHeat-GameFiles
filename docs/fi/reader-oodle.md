---
title: "Oodle"
nav_order: 3
lang: "fi"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: löytyy, ei mukana {#oodle-found-not-bundled}

Useimmat Unreal-pelien mukana tulevat sisällöt ja osa Frostbite-hyötykuormista on pakattu **Oodlella** (RAD Game Tools, nykyään Epic). Oodle on omistusoikeudellinen. Siitä ei ole jaettavaa versiota eikä Python-toteutusta, ja `oo2core_*.dll` on lisensoitu sille tuotteelle, joka sen mukana toimittaa. Tämä työkalu siis **etsii koneeltasi jo olevan kopion ja lataa sen**. Se ei koskaan toimita kopiota mukana. FModel ja UModel toimivat samalla tavalla.

Lähde: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Mistä se etsii {#where-it-looks}

Ensimmäinen olemassa oleva tiedosto voittaa, tässä järjestyksessä:

1. Kutsujan antama polku (Python-rajapinta).
2. `HEAT3D_OODLE`: polku DLL-tiedostoon tai kansioon, joka sen sisältää.
3. Matala haku, yhden tason syvyydeltä, kohteista
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - jokaisen Steam-kirjaston `steamapps\common`

   Jokaisesta alikansiosta `<game>` se tarkistaa kansiot `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` ja `<game>\Engine\Binaries\Win64`.

Kokeiltavat tiedostonimet, uusin ensin: `oo2core_9_win64.dll` alas `oo2core_3_win64.dll`:ään. Muoto on taaksepäin yhteensopiva, joten vanhempi kirjasto toimii yleensä edelleen.

Haku ei ole tarkoituksella rekursiivinen koko levyn läpi, koska se kestäisi minuutteja. Jos mitään ei löydy, aseta `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Kansio käy yhtä hyvin kuin tiedosto itse: yllä mainitut DLL-nimet kokeillaan kansion sisältä.

Unreal Engine -asennuksessa on sellainen kohdassa `Engine\Binaries\ThirdParty\Oodle`, mikä on kehittäjälle siistein lähde. Monet pelit toimittavat sellaisen suoritettavan tiedoston viereen. Unreal 5 -pelit linkittävät Oodlen usein staattisesti eivätkä toimita DLL-tiedostoa, joten löydetty kopio voi kuulua eri pelille kuin luettava arkisto. Muoto on kuitenkin sama.

## Miten sitä kutsutaan {#how-it-is-called}

`OodleLZ_Decompress` kutsutaan `ctypes`-kirjaston kautta odotetulla tulospituudella (arkistohakemisto tietää sen aina, eikä Oodle voi päätellä sitä). Vikasietoinen purku on päällä (syöte on epäluotettava), CRC-tarkistus on pois päältä (pakin oma SHA-1 kattaa jo tavut) ja purku on yksisäikeinen. Väärän pituinen tulos on virhe. Kirjasto ladataan kerran per ajo.

## Kun sitä ei ole {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Merkintä, jota ei voi purkaa, on virhe, ei uskottavaa roskaa.

Lataaja toimii vain Windowsissa (se etsii `*_win64.dll`-tiedostoja). Linux- ja macOS-kirjastoja ei etsitä.
