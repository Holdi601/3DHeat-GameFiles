---
title: "Autá z Forzy: `cars`"
nav_order: 6
lang: "sk"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Autá z Forzy: `cars` {#forza-cars-cars}

Zapíše každé auto nainštalovanej Forzy vo východzom nízkom detaile hry do jedného súboru pre kartu Analýza pretekov v prehliadači 3DHeat (kreslí auto za každé kolo, ktoré ste odjazdili), takže každé zaznamenané auto sa kreslí vo svojom vlastnom tvare a v skutočnej veľkosti.

![cars --help](../assets/img/cars-help.svg)

## Postup krok za krokom {#step-by-step}

1. **Spustite ho**, keď je hra nainštalovaná (nájde sa v knižniciach Steamu a v `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Alebo uveďte priečinok hry:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Načítajte ho v prehliadači**: **Načítať súbor s autami…** v nastaveniach zobrazenia alebo pustite súbor na kartu Analýza pretekov; ostane v tomto prehliadači. Jazdy, ktorých číslo auta je v súbore, sa potom kreslia ako presne toto auto (pozri [dokumentáciu prehrávania pretekov v prehliadači](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Spustite ho znova**, keď hra dostane nové autá. Trvá to sekundy a zapíše asi 5 MB.

## Možnosti {#options}

| Možnosť | Predvolené | Význam |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | súbor, ktorý sa zapíše |
| `--game FOLDER` | nájdená nainštalovaná hra | priečinok hry |

## Čo je v súbore {#what-is-in-the-file}

Pre každý archív auta pod `media/Cars`: model `ProxyLOD`, ktorý nesie (asi 900 trojuholníkov), číslo auta tak, ako ho uvádza telemetria, jeho značku, označenie modelu a rok z názvu archívu, a jeho kolesá a zadné svetlá. Tvary sú v metroch, 1:1 s autom. Archív bez takéhoto modelu (rekvizita premávky) sa pomenuje a vynechá.

Súbor je vytvorený pre prehliadač 3DHeat; jeho rozloženie pre každého, kto ho číta inde ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Časť | Rozloženie |
|---|---|
| celý súbor | komprimovaný gzipom |
| magické číslo | 8 bajtov `H3DCARS1` |
| dĺžka hlavičky | little-endian u32 |
| hlavička | JSON v kódovaní UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| výplň | medzery až do násobku 4 bajtov |
| údaje | pre každé auto: vrcholy ako tri i16 každý (milimetre; x doprava, y hore, z dopredu), potom trojuholníky ako tri u16 každý |

Každá položka `cars`: `key`, `ordinals` (čísla auta tak, ako ich uvádza telemetria), `make`, `model`, `year`, `height` a `length` (m), `wheels` (pre každé koleso `[x, y, z, radius]`, m), `lights` (body zadných svetiel `[x, y, z]`, m) a `vertexAt`, `vertices`, `faceAt`, `faces` (posuny v bajtoch od začiatku údajov, a počty).

Súbor obsahuje obsah hry: je určený pre počítač, na ktorom vznikol, nie na posielanie ďalej ([Pravidlá a licencie](rules-and-licences.md)).
