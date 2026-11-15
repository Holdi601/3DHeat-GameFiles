---
title: Forza-Autos
nav_order: 6
lang: de
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Forza-Autos: `cars` {#forza-cars-cars}

Schreibt jedes Auto eines installierten Forza in einer Datei, in der niedrigen Detailstufe des Spiels, für den Tab Rennanalyse des Viewers (er zeichnet für jede Runde, die du gefahren bist, ein Auto). So wird jedes aufgenommene Auto in seiner eigenen Form und in seiner echten Größe gezeichnet.

![cars --help](../assets/img/cars-help.svg)

## Schritt für Schritt {#step-by-step}

1. **Starte es**, wenn das Spiel installiert ist (es wird in den Steam-Bibliotheken und in `C:\XboxGames` gefunden):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Oder nenne den Ordner des Spiels:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza-Ordner>" -o forza.h3dcars
   ```

2. **Lade die Datei im Viewer**: **Autodatei laden…** in den Ansichtseinstellungen, oder ziehe die Datei auf den Tab Rennanalyse. Sie bleibt in diesem Browser gespeichert. Runden, deren Startnummer in der Datei steht, werden dann genau als dieses Auto gezeichnet (siehe die [Doku zur Rennwiedergabe im Viewer](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Starte es erneut**, wenn das Spiel neue Autos bekommt. Es dauert Sekunden und schreibt etwa 5 MB.

## Optionen {#options}

| Option | Standard | Bedeutung |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | die Datei, die geschrieben wird |
| `--game FOLDER` | das gefundene installierte Spiel | der Ordner des Spiels |

## Was in der Datei steht {#what-is-in-the-file}

Für jedes Autoarchiv unter `media/Cars`: das `ProxyLOD`-Modell, das es enthält (etwa 900 Dreiecke), die Startnummer des Autos, so wie die Telemetrie sie angibt, seine Marke, sein Modellkürzel und sein Baujahr aus dem Namen des Archivs sowie seine Räder und Rücklichter. Die Formen sind in Metern, 1:1 mit dem Auto. Ein Archiv ohne ein solches Modell (ein Verkehrsrequisit) wird benannt und ausgelassen.

Die Datei ist für den 3DHeat-Viewer gemacht. Ihr Aufbau für alle, die sie anderswo lesen ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Teil | Aufbau |
|---|---|
| ganze Datei | gzip-komprimiert |
| Kennung | die 8 Bytes `H3DCARS1` |
| Länge des Kopfs | little-endian u32 |
| Kopf | UTF-8-JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| Auffüllung | Leerzeichen bis zu einem Vielfachen von 4 Bytes |
| Daten | je Auto: die Eckpunkte als drei i16 je Punkt (Millimeter; x nach rechts, y nach oben, z nach vorn), danach die Dreiecke als drei u16 je Dreieck |

Jeder Eintrag in `cars` hat: `key`, `ordinals` (die Startnummern des Autos, so wie die Telemetrie sie angibt), `make`, `model`, `year`, `height` und `length` (m), `wheels` (je Rad `[x, y, z, radius]`, m), `lights` (Punkte der Rücklichter `[x, y, z]`, m) sowie `vertexAt`, `vertices`, `faceAt`, `faces` (Byte-Versatz ab dem Anfang der Daten und Anzahlen).

Die Datei enthält Inhalte des Spiels. Sie ist für den Rechner gedacht, auf dem sie erstellt wurde, nicht zum Weitergeben ([Regeln und Lizenzen](rules-and-licences.md)).
