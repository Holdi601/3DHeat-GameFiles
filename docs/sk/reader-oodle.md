---
title: "Oodle: nájdený, nie priložený"
nav_order: 3
lang: "sk"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: nájdený, nie priložený {#oodle-found-not-bundled}

Väčšina zverejneného obsahu Unreal a niektoré obsahy Frostbite sú komprimované pomocou **Oodle** (RAD Game Tools, teraz Epic). Oodle je proprietárny. Neexistuje voľne šíriteľná verzia ani implementácia v Pythone a `oo2core_*.dll` je licencovaná produktu, ktorý ju dodáva. Preto tento nástroj **nájde kópiu, ktorá už je na vašom počítači, a načíta ju**. Nikdy žiadnu neprikladá. FModel a UModel fungujú rovnako.

Zdroj: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Kde hľadá {#where-it-looks}

Vyhrá prvý súbor, ktorý existuje, v tomto poradí:

1. Výslovne zadaná cesta od volajúceho (Python API).
2. `HEAT3D_OODLE`: cesta k DLL alebo priečinok, ktorý ju obsahuje.
3. Plytké hľadanie, do jednej úrovne, v
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` každej knižnice Steamu

   Pri každom podpriečinku `<game>` skontroluje `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` a `<game>\Engine\Binaries\Win64`.

Mená súborov, ktoré skúša, od najnovšieho: `oo2core_9_win64.dll` až po `oo2core_3_win64.dll`. Formát je spätne kompatibilný, takže staršia knižnica zvyčajne stále funguje.

Hľadanie je zámerne **nie** rekurzívne prehľadávanie všetkých diskov, lebo by trvalo minúty. Ak nič nenájde, nastavte `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Priečinok funguje rovnako ako samotný súbor: názvy DLL vyššie sa v ňom skúšajú.

Inštalácia Unreal Engine obsahuje jednu pod `Engine\Binaries\ThirdParty\Oodle`, čo je pre vývojára najčistejší zdroj. Mnohé hry ju majú vedľa svojho spustiteľného súboru. Hry Unreal 5 často linkujú Oodle staticky a nedodajú žiadnu DLL, takže nájdená kópia môže patriť inej hre, než je archív, ktorý sa číta. Formát je v oboch prípadoch rovnaký.

## Ako sa volá {#how-it-is-called}

`OodleLZ_Decompress` sa volá cez `ctypes` s očakávanou dĺžkou výstupu (index archívu ju vždy pozná a Oodle ju nevie odvodiť), s dekódovaním odolným voči fuzzingu (vstup nie je dôveryhodný), bez kontroly CRC (SHA-1 samotného pak už pokrýva bajty) a bez vlákien. Výsledok zlej dĺžky je chyba. Knižnica sa načíta raz pri každom behu.

## Keď žiadna nie je {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Položka, ktorú nie je možné dekomprimovať, je chyba, nikdy nie uveriteľný odpad.

Čítačka je len pre Windows (hľadá `*_win64.dll`). Knižnice pre Linux a macOS sa nehľadajú.
