---
title: "Avtomobili Forza"
nav_order: 6
lang: "sl"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Avtomobili Forza: `cars` {#forza-cars-cars}

Zapiše vsak avtomobil nameščene igre Forza v eno datoteko, v nizki podrobnosti, kot jo uporablja sama igra. Datoteka je namenjena zavihku Analiza dirke v pregledovalniku, ki za vsak krog, ki ste ga vozili, nariše avtomobil. Vsak zabeleženi avtomobil je tako narisan v svoji obliki in v pravi velikosti.

![cars --help](../assets/img/cars-help.svg)

## Korak za korakom {#step-by-step}

1. **Zaženite ga**, ko je igra nameščena (najde se v knjižnicah Steam in v `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ali pa navedite mapo igre:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Naložite ga v pregledovalnik**: **Naloži datoteko z avtomobili…** v nastavitvah pogleda ali pa datoteko spustite na zavihek Analiza dirke. Ostane v tem brskalniku. Krogi, katerih številka avtomobila je v datoteki, se nato narišejo s prav tem avtomobilom (glejte [dokumentacijo o ponovitvi dirke v pregledovalniku](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Zaženite ga znova**, ko igra dobi nove avtomobile. Traja nekaj sekund in zapiše približno 5 MB.

## Možnosti {#options}

| Možnost | Privzeto | Pomen |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | datoteka, ki se zapiše |
| `--game FOLDER` | najdena nameščena igra | mapa igre |

## Kaj je v datoteki {#what-is-in-the-file}

Za vsak arhiv avtomobila v `media/Cars`: model `ProxyLOD`, ki ga vsebuje (okoli 900 trikotnikov), številka avtomobila, kot jo navaja telemetrija, njegova znamka, oznaka modela in letnik iz imena arhiva ter njegova kolesa in zadnje luči. Oblike so v metrih, v razmerju 1:1 z avtomobilom. Arhiv brez takega modela (rekvizit prometa) je poimenovan in izpuščen.

Datoteka je narejena za pregledovalnik 3DHeat. Njena postavitev, za vsakogar, ki jo bere drugje ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Del | Postavitev |
|---|---|
| cela datoteka | stisnjena z gzip |
| magic | 8 bajtov `H3DCARS1` |
| dolžina glave | u32 v little-endian |
| glava | UTF-8 JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| polnilo | presledki do večkratnika 4 bajtov |
| podatki | za vsak avtomobil: oglišča kot tri i16 vsako (milimetri; x desno, y gor, z naprej), nato trikotniki kot tri u16 vsak |

Vsak vnos v `cars` ima: `key`, `ordinals` (številke avtomobila, kot jih navaja telemetrija), `make`, `model`, `year`, `height` in `length` (m), `wheels` (za vsako kolo `[x, y, z, radius]`, m), `lights` (točke zadnjih luči `[x, y, z]`, m) ter `vertexAt`, `vertices`, `faceAt`, `faces` (zamiki v bajtih od začetka podatkov, in števila).

Datoteka vsebuje vsebino igre. Namenjena je stroju, na katerem je bila narejena, ne za posredovanje ([Pravila in licence](rules-and-licences.md)).
