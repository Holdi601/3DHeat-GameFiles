---
title: "Auta z Forzy: `cars`"
nav_order: 6
lang: "cs"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Auta z Forzy: `cars` {#forza-cars-cars}

Zapíše každé auto nainstalované Forzy v nízkém detailu, jaký používá sama hra, do jednoho souboru pro kartu Analýza závodu v prohlížeči (nakreslí auto pro každé kolo, které jste odjeli). Každé zaznamenané auto se tak vykreslí vlastním tvarem ve své skutečné velikosti.

![nápověda příkazu cars --help](../assets/img/cars-help.svg)

## Postup krok za krokem {#step-by-step}

1. **Spusťte ho**, když je hra nainstalovaná (najde se v knihovnách Steamu a v `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Nebo zadejte složku hry:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Načtěte ho v prohlížeči**: **Načíst soubor s auty…** v nastavení zobrazení, nebo přetáhněte soubor na kartu Analýza závodu. Zůstane v tomto prohlížeči. Kola, jejichž číslo auta je v souboru, se potom vykreslí jako právě to auto (viz [dokumentace přehrávání závodu ve vieweru](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Spusťte ho znovu**, až hra dostane nová auta. Trvá to jen pár sekund a zapíše asi 5 MB.

## Možnosti {#options}

| Možnost | Výchozí | Význam |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | soubor, který se zapíše |
| `--game FOLDER` | nalezená nainstalovaná hra | složka hry |

## Co je v souboru {#what-is-in-the-file}

Pro každý archiv auta v `media/Cars`: model `ProxyLOD`, který nese (asi 900 trojúhelníků), číslo auta podle telemetrie, značku, označení modelu a rok z názvu archivu a jeho kola a zadní světla. Tvary jsou v metrech, 1:1 s autem. Archiv bez takového modelu (dopravní rekvizita) se pojmenuje a vynechá.

Soubor je určen pro prohlížeč 3DHeat. Jeho rozložení pro každého, kdo ho čte jinde ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Část | Rozložení |
|---|---|
| celý soubor | komprimovaný gzipem |
| magic | 8 bajtů `H3DCARS1` |
| délka hlavičky | u32 little-endian |
| hlavička | JSON v UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| výplň | mezery až do násobku 4 bajtů |
| data | pro každé auto: vrcholy jako tři i16 (milimetry; x vpravo, y nahoru, z dopředu), pak trojúhelníky jako tři u16 |

Každá položka `cars` obsahuje: `key`, `ordinals` (čísla auta tak, jak je uvádí telemetrie), `make`, `model`, `year`, `height` a `length` (m), `wheels` (pro každé kolo `[x, y, z, radius]`, m), `lights` (body zadních světel `[x, y, z]`, m) a `vertexAt`, `vertices`, `faceAt`, `faces` (posuny v bajtech od začátku dat a počty).

Soubor obsahuje obsah hry: je určen pro počítač, na kterém vznikl, a ne k předávání dál ([Pravidla a licence](rules-and-licences.md)).
