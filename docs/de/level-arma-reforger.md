---
title: Arma-Reforger-Welten
nav_order: 3
lang: "de"
source: level-arma-reforger.md
source_hash: "83746901e212"
nav_exclude: true
search_exclude: true
---
# Arma-Reforger-Welten: `enfusion-worlds` und `enfusion-world` {#arma-reforger-worlds-enfusion-worlds-and-enfusion-world}

**Was ist das?** Eine ganze Arma-Reforger-Welt als eine 3D-Datei. **Warum?** Damit
die Hitze aus dem Spiel das Gelände und die Gebäude darunter hat. (*Enfusion* ist die
Engine, mit der Arma Reforger gemacht ist; eine *Welt* ist das, was das Spiel eine
Karte nennt.)

Exportiert eine ganze Enfusion-Welt des installierten Arma Reforger: das Gelände in
den Farben seiner eigenen Supertexture-Kacheln, das Meer und jedes platzierte Modell
als Box, in den eigenen Metern des Spiels.

![Die Schritte eines enfusion-world-Exports](../assets/img/de/enfusion-steps.svg)

## Schritt für Schritt {#step-by-step}

1. **Die Welten auflisten**, die ein Gelände haben:

   ```
   python -m heat3d_gamefiles enfusion-worlds
   python -m heat3d_gamefiles enfusion-worlds --install "D:\Games\Arma Reforger"
   ```

2. **Eine exportieren**, unter ihrem Ordnernamen in `worlds/`, wie aufgelistet:

   ```
   python -m heat3d_gamefiles enfusion-world <world> -o world.glb
   ```

3. **Varianten:**

   ```
   python -m heat3d_gamefiles enfusion-world <world> --trees               # vegetation too, as boxes
   python -m heat3d_gamefiles enfusion-world <world> --texture-size 0      # flat colour, small file
   python -m heat3d_gamefiles enfusion-world <world> --ground-spacing 4 --no-structures
   ```

4. **`world.glb` öffnen** im Bereich Hintergrund / Level des 3DHeat-Viewers
   ([Level laden](https://holdi601.github.io/3DHeat/levels.html)).

## Optionen {#options}

| Option | Vorgabe | Bedeutung |
|---|---|---|
| `<world>` | Pflicht | eine Welt, so wie `enfusion-worlds` sie ausgibt |
| `-o`, `--out FILE` | `<world>.glb` | die zu schreibende Datei |
| `--install FOLDER` | die Steam-Bibliothek, die das Spiel enthält | der Spielordner |
| `--ground-spacing METRES` | 2 (das eigene des Geländes) | der Abstand der Geländepunkte in der Datei |
| `--texture-size PIXELS` | 4096 | die größere Seite des Bildes der Bodenfarbe; 0 für einfarbige Flächen |
| `--no-structures` | | die platzierten Modelle weglassen |
| `--trees` | aus | auch Bäume und andere Vegetation platzieren, als Boxen |

## Beispielausgabe {#example-output}

```text
<world> -> world.glb
  ground      <n> triangles, <w> x <h> m; <n> of <n> tile-edge vertices disagree; colour <w> x <h>
  structure   <n> boxes from <n> entities
  water       <n> triangles (the sea)
  left out    <what>: <n>, ...
```

## Die Teile {#the-parts}

`ground:<world>` (das Gelände), `water:<world>` (das Meer, auf Höhe null) und
`structure:<world>` (die Boxen). Die Koordinaten sind die eigenen des Spiels: x nach
Osten, y nach oben, z nach Norden, in Metern, also das, was eine Aufnahme aus dem
Spiel meldet. Das Bezugssystem des Spiels ist linkshändig. *Weltachse invertieren* im
Viewer zeigt es ungespiegelt.

## Wie es gelesen und geprüft wird {#how-it-is-read-and-checked}

Kein Workbench nötig, und nichts ist verschlüsselt.

| Format | Was es ist | Geprüft gegen |
|---|---|---|
| `.pak` | ein Datenchunk und ein Verzeichnisbaum, Einträge gespeichert oder zlib | der Baum verbraucht seinen Chunk genau; stichprobenartig geprüfte zlib-Einträge entpacken auf genau ihre angegebene Größe |
| `.edds` | eine DDS-Kopfzeile, dann pro Mip-Stufe `COPY`- oder `LZ4 `-Chunks | aufgeteilte Stufen dekodieren auf genau ihre Größe und verwenden genau ihre Bytes |
| `.terr` / `.ttile` | eine Kopfzeile und Kacheln mit 16-Bit-Höhen | jede gemeinsame Kachelkante stimmt genau überein |
| Supertexture | die Bodenfarbe jeder Kachel, etwa ein Meter pro Pixel | sie passt zum Meer in den Höhen; keine Spiegelung oder Transposition passt besser |
| `.ent` | Namen, Ressourcen-GUIDs, dann Entitäten als typisierte Werte | eine Weltdatei parst bis zu ihrem letzten Byte |
| `resourceDatabase.rdb` | GUID zu Pfad | fast jede GUID, die eine Welt verwendet, nennt eine Datei, die existiert |

Objekte, die als auf absoluter Höhe stehend markiert sind, sitzen auf wenige
Zentimeter genau auf dem dekodierten Gelände (mit vertauschtem Raster lägen sie um
Meter daneben). Nicht gezeichnet: die eigenen Dreiecke der Modelle, Bäume standardmäßig
(`--trees` fügt sie als Boxen hinzu), untergeordnete Entitäten, Seen und Flüsse,
Texturen mit Kopfzeilen vor DX10.

**Begriffe:** Die Lizenz des Spiels erlaubt nichtkommerzielle Nutzung und verbietet
das Reverse Engineering der Spieldateien. Das Lesen deiner eigenen Installation ist
Deine Entscheidung unter dieser Lizenz; die Ausgabe ist für deinen eigenen Gebrauch
bestimmt und wird nicht weitergegeben.
