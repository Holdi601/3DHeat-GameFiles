---
title: Forza-auto's
nav_order: 6
lang: "nl"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Forza-auto's: `cars` {#forza-cars-cars}

Schrijft elke auto van een geïnstalleerde Forza op het eigen lage detailniveau van het spel in één bestand, voor het tabblad Race-analyse van de viewer (daar wordt voor elke ronde die je reed een auto getekend). Elke opgenomen auto wordt zo getekend in zijn eigen vorm en op zijn ware grootte.

![cars --help](../assets/img/cars-help.svg)

## Stap voor stap {#step-by-step}

1. **Start het** met het spel geïnstalleerd (het wordt gevonden in de Steam-bibliotheken en in `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Of geef de map van het spel op:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Laad het in de viewer**: **Autobestand laden…** in de weergave-instellingen, of zet het bestand op het tabblad Race-analyse; het blijft in die browser. Ronden waarvan het autonummer in het bestand staat, worden dan getekend als precies die auto (zie de [race-replay-documentatie van de viewer](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Draai het opnieuw** wanneer het spel nieuwe auto's krijgt. Het duurt enkele seconden en schrijft ongeveer 5 MB.

## Opties {#options}

| Optie | Standaard | Betekenis |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | het bestand dat geschreven wordt |
| `--game FOLDER` | het gevonden geïnstalleerde spel | de map van het spel |

## Wat er in het bestand zit {#what-is-in-the-file}

Voor elk autoarchief onder `media/Cars`: het `ProxyLOD`-model dat het bevat (ongeveer 900 driehoeken), het autonummer zoals de telemetrie het opgeeft, het merk, de modelaanduiding en het jaar uit de naam van het archief, en de wielen en achterlichten. De vormen staan in meters, 1:1 met de auto. Een archief zonder zo'n model (een verkeersobject) wordt benoemd en weggelaten.

Het bestand is gemaakt voor de 3DHeat-viewer. De indeling, voor wie het elders leest ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Onderdeel | Indeling |
|---|---|
| het hele bestand | gzip-gecomprimeerd |
| magic | de 8 bytes `H3DCARS1` |
| headerlengte | little-endian u32 |
| header | UTF-8-JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| opvulling | spaties tot een veelvoud van 4 bytes |
| data | per auto: hoekpunten als drie i16 elk (millimeters; x rechts, y omhoog, z vooruit), daarna driehoeken als drie u16 elk |

Elk item in `cars`: `key`, `ordinals` (de autonummers zoals de telemetrie ze opgeeft), `make`, `model`, `year`, `height` en `length` (m), `wheels` (per wiel `[x, y, z, radius]`, m), `lights` (achterlichtpunten `[x, y, z]`, m), en `vertexAt`, `vertices`, `faceAt`, `faces` (bytepositie vanaf het begin van de data, en aantallen).

Het bestand bevat de inhoud van het spel. Het is bedoeld voor de computer waarop het gemaakt is, niet om door te geven ([Regels en licenties](rules-and-licences.md)).
