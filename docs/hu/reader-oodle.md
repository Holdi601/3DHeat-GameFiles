---
title: "Oodle: megtalálva, nem csomagolva"
nav_order: 3
lang: "hu"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: megtalálva, nem csomagolva {#oodle-found-not-bundled}

A legtöbb szállított Unreal-tartalmat, és néhány Frostbite-adatcsomagot **Oodle** tömörít (RAD Game
Tools, ma Epic). Az Oodle szabadalmazott. Nincs újraterjeszthető változata és nincs Python-megvalósítása,
az `oo2core_*.dll` pedig annak a terméknek a licencéhez tartozik, amely szállítja. Ezért ez az eszköz
**megkeres egy már a gépeden lévő példányt, és betölti**. Soha nem szállít egyet sem. Az FModel és
az UModel ugyanígy működik.

Forrás: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Hol keres {#where-it-looks}

Az első létező fájl nyer, ebben a sorrendben:

1. A hívó által megadott útvonal (Python API).
2. `HEAT3D_OODLE`: a DLL útvonala, vagy egy mappa, amely tartalmazza.
3. Sekély keresés, egy szinttel mélyen, a következő helyeken:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - minden Steam-könyvtár `steamapps\common` mappája

   Minden `<game>` almappánál ellenőrzi a `<game>`, a
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` és a `<game>\Engine\Binaries\Win64` mappát.

A kipróbált fájlnevek, a legújabbtól: `oo2core_9_win64.dll`-tól `oo2core_3_win64.dll`-ig. A formátum
visszafelé kompatibilis, így egy régebbi könyvtár általában még működik.

A keresés szándékosan **nem** végigmegy minden meghajtón rekurzívan, mert az percekig tartana. Ha nem
talál semmit, állítsd be a `HEAT3D_OODLE` változót:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Egy mappa éppúgy jó, mint maga a fájl: a fent felsorolt DLL-neveket benne próbálja ki.

Egy Unreal Engine telepítés az `Engine\Binaries\ThirdParty\Oodle` alatt tartalmaz egyet, ez a
fejlesztőnek a legkényelmesebb forrás. Sok játék a futtatható fájlja mellett szállít egyet. Az Unreal 5
játékok gyakran statikusan kapcsolják az Oodle-t, és nem szállítanak DLL-t, így a megtalált példány más
játékhoz tartozhat, mint az olvasott archívum. A formátum mindkét esetben ugyanaz.

## Hogyan hívódik {#how-it-is-called}

Az `OodleLZ_Decompress` `ctypes`-on keresztül hívódik, a várt kimeneti hosszal (az archívum indexe
mindig ismeri, az Oodle nem tudja kitalálni), hibatűrő dekódolással bekapcsolva (a bemenet nem
megbízható), CRC-ellenőrzés nélkül (a pak saját SHA-1 értéke már lefedi a bájtokat), és szálak nélkül.
Rossz hosszúságú eredmény hiba. A könyvtár futásonként egyszer töltődik be.

## Ha nincs {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Egy ki nem tömöríthető bejegyzés hiba, sosem valószínűtlen szemét.

A betöltő csak Windowson működik (a `*_win64.dll` fájlokat keresi). Linux- és macOS-könyvtárakat nem
keres.
