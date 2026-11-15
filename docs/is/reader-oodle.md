---
title: "Oodle"
nav_order: 3
lang: "is"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: fundið, ekki fylgir með {#oodle-found-not-bundled}

Mest af útgefnu Unreal-efni, og sumt af Frostbite-gögnum, er þjappað með
**Oodle** (RAD Game Tools, nú Epic). Oodle er séreign. Það er engin
endurdreifanleg útgáfa og engin Python-útfærsla, og `oo2core_*.dll` er
með leyfi fyrir vörunni sem sendir það með. Þess vegna **finnur þetta verkfæri eintak sem er þegar til á
vélinni þinni og hleður því**. Það ber aldrei neitt með sér. FModel og UModel virka
á sama hátt.

Frumkóði: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Hvar það leitar {#where-it-looks}

Fyrsta skráin sem er til sigrar, í þessari röð:

1. Slóð sem kallandinn gefur beint (Python API).
2. `HEAT3D_OODLE`: slóð að DLL-skránni, eða mappa sem geymir eina.
3. Grunn leit, eitt stig niður, í
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` hvers Steam-safns

   Fyrir hverja undirmöppu `<game>` athugar það `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` og
   `<game>\Engine\Binaries\Win64`.

Skráarnöfn sem reynd eru, nýjasta fyrst: `oo2core_9_win64.dll` niður í
`oo2core_3_win64.dll`. Sniðið er afturábak samhæft, svo eldra safn
virkar yfirleitt enn.

Leitin er af ásettu ráði **ekki** endurkvæm skönnun á hverjum diski, sem myndi
taka mínútur. Ef það finnur ekkert skaltu setja `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Mappa virkar jafnt og skráin sjálf: DLL-nöfnin hér að ofan eru reynd inni í henni.

Uppsetning á Unreal Engine hefur eitt undir `Engine\Binaries\ThirdParty\Oodle`,
sem er snyrtilegasta uppsprettan fyrir forritara. Margir leikir senda eitt með við hlið
keyrsluskrár sinnar. Unreal 5 leikir tengja Oodle oft kyrrstætt og senda enga DLL, svo
eintakið sem finnst getur tilheyrt öðrum leik en skjalasafninu sem er lesið. Sniðið
er það sama hvort sem er.

## Hvernig það er kallað {#how-it-is-called}

`OodleLZ_Decompress` er kallað gegnum `ctypes` með væntanlegri úttakslengd
(skjalasafnsskráin veit hana alltaf, og Oodle getur ekki ályktað hana), öruggri
afkóðun gegn fuzz (fuzz-safe) á (inntakið er ótraust), án CRC-athugunar (SHA-1 pak-skrárinnar
nær þegar yfir bætin) og án þráða. Niðurstaða af rangri lengd er villa. Safnið
er hlaðið einu sinni í hverri keyrslu.

## Þegar ekkert er til {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Færsla sem ekki er hægt að afþjappa er villa, aldrei sennilegt rusl.

Hleðslan er aðeins fyrir Windows (hún leitar að `*_win64.dll`). Linux- og macOS-söfn
eru ekki leituð uppi.
