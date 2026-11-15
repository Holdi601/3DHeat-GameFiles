---
title: BeamNG-Dateien
nav_order: 8
lang: de
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# BeamNG-Dateien: Leveldateien, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive liefert einfache Zip-Archive aus, also gibt es keinen Container, den man
zurückentwickeln müsste. Die Arbeit liegt darin, ein Level **so zu lesen, wie das
Spiel es tut**: die Archive in ein Dateisystem einhängen, den Szenendateien folgen und
das Gelände und die kompilierten Formen dekodieren. Diese Leser werden über den
[BeamNG.drive](course-beamng.md)-Kursexport aufgerufen. `identify` erkennt außerdem
ein Level-Zip, eine `.cdae` und eine `.ter`, und `list` und `extract` nehmen jedes der Zips.

Quellen: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Das eingehängte Dateisystem {#the-mounted-file-system}

`Files.of_install(game)` baut einen Index über `gameengine.zip`, die `content`-Zips
(außer Fahrzeuge und Töne) und die Mods des Nutzers (`mods\*.zip`, `mods\unpacked\*`
und ein Ordner `levels` des Nutzers). Spätere Ergänzungen überschreiben frühere, wie im
Spiel. Die Suche ignoriert Groß- und Kleinschreibung, weil die Verweise der Level nicht
mit den Archiven übereinstimmen (`.DAE` für eine `.dae`). Einzelheiten stehen unter
[BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` findet einen Pfad so, wie das Spiel es tut: wie angegeben, relativ zu der
Datei, die ihn nennt, `x.png` als `x.dds`, `x.dae` als `x.cdae` (bevorzugt), und über
eine JSON-Datei `x.png.link`, deren `path` in `/assets` zeigt.

## Szenendateien {#scene-files}

| Quelle | Format | Gelesen |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | ein JSON-Objekt je Zeile, oder ein einzelnes JSON-Array oder eine Map | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | dieselben Klassen, für ältere Level ohne `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript oder JSON | Kinder relativ zum Prefab platziert, bis 8 Ebenen tief |
| `levels\<name>\forest\*.forest4.json` | eine Instanz je Zeile | typisiert durch `TSForestItemData`-Datensätze in `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | der Titel des Levels (Übersetzungsschlüssel werden ignoriert) |

**Transformationen.** `rotationMatrix` sind neun Zahlen, deren **Zeilen** die eigenen
Achsen des Objekts in der Welt sind. Leitplankenabschnitte, die entlang einer Straße
aneinandergereiht sind, laufen entlang Zeile 0 (92 %), und die Zeile „oben" neigt sich
mit der Steigung der Straße. Ältere Prefabs geben `rotation = "x y z degrees"`, eine
rechtshändige Drehung um diesen Winkel (92 % der Schienenketten stimmen damit überein,
19 % mit dem entgegengesetzten Sinn). Die Skalierung multipliziert die Zeilen, und
`position` (oder `pos`) ist die letzte Zeile. Die Transformation eines Prefab-Kindes wird
mit der des Prefabs zusammengesetzt. Das `groupPosition` des Prefabs ist ein Drehpunkt
des Editors und wird **nicht** abgezogen: Ein Wagen-Prefab steht nur ohne diesen Abzug
auf dem Boden.

TorqueScript-Zahlen werden mit einem toleranten Muster gelesen, weil einige ausgelieferte
Prefabs Werte wie `-0.99563-0.0` ohne Leerzeichen schreiben.

## Gelände: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Höhe in Metern: `position.z + h * maxHeight / 65535`, mit `position`,
  `squareSize` und `maxHeight` aus dem `TerrainBlock` (Vorgaben 0, 1 und 2048).
- Die Zeilen laufen entlang +y. Rasterpunkt (i, j) liegt bei
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Schicht 255 ist ein Loch.

Geprüft: Straßenknoten liegen auf drei Ebenen auf dem Gelände, auf 1-2 cm genau (Median).
`h / 32` oder die andere Achsenreihenfolge verfehlt um Zehner bis Hunderte Meter.

## Materialien {#materials}

Jede `*.materials.json` außerhalb von `levels\` sowie die des aktuellen Levels, indiziert
nach `mapTo`, `name` und Schlüssel:

| Klasse | Verwendete Felder |
|---|---|
| `Material`, `CustomMaterial` | Farbkarte (`baseColorMap`, `colorMap` oder `diffuseMap`, erste Stufe), Farbfaktor, Deckkraftkarte und -faktor, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | Basiskarte und `diffuseSize`, Detailkarte, Größe und Stärke, Makrokarte, Größe und Stärke, `groundmodelName`, `annotation` |

Bilder werden mit Pillow dekodiert (DDS, PNG und so weiter), wo möglich mit einer
verkleinerten Vorstufe, und je Größe zwischengespeichert. Eine unlesbare Textur fällt
auf eine einfarbige Fläche zurück.

## Kompilierte Formen: `.cdae` {#compiled-shapes-cdae}

`.cdae` ist der eigene Zwischenspeicher des Spiels für jede Collada-Datei, als
MessagePack geschrieben. Sein Layout ist **von BeamNG dokumentiert**
(documentation.beamng.com/modding/file_formats/cdae/), und der Leser folgt ihm:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Gelesen werden: Begrenzungen, Knoten, Objekte, `details` (Detailstufen), die
Standarddrehungen (`Quat16`) und Verschiebungen der Knoten, jedes Mesh mit Punkten,
UVs, Normalen, Farben, Primitiven und Indizes sowie die Materialnamen. Die Materialnamen
stehen am Ende des Stroms, weil die Sequenzen eines animierten Requisits davor kommen,
in einer Form, die nicht dokumentiert ist.

Zwei Dinge, die die Dokumentation nicht ausführt, wurden an den `.dae`-Dateien geprüft,
aus denen die Formen gebaut wurden:

- **Die Drehungen der Knoten sind die von Torque.** Ein `Quat16`, auf die übliche Weise
  gelesen, dreht falsch herum. Seine Matrix muss **transponiert** werden. Dann stimmen
  die Weltgrenzen jedes Knotens auf den Millimeter mit der Collada überein. Ohne das
  liegen sie im Median 38 cm daneben.
- **Einheiten und Achsen sind schon angewendet.** Eine Collada-Datei, die in Zentimetern
  oder mit Y nach oben erstellt wurde, kommt aus dem Zwischenspeicher in Metern, mit Z
  nach oben.

Detailstufen sind die `details` mit nicht negativer Größe, größte zuerst. Negative
Größen sind Kollisions- und Sichtlinien-Meshes, die nie gezeichnet werden. Objekte mit
den Namen `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` oder
`imposter` werden nie gezeichnet. Gezeichnet werden nur Standard- und sortierte Meshes.
Skinning-Meshes (Charaktere, Fahrzeuge) und Decal-Meshes nicht. Dreiecksstreifen und
-fächer werden aufgelöst, und Flächen werden so gedreht, dass sie zu den gespeicherten
Normalen passen, was die eigene Windungsrichtung von Torque nicht garantiert.

Geprüft: Fast jede ausgelieferte Form wird gelesen. Die zwei anderen gehören zu einer
älteren Version.

## Collada-Ersatz: `.dae` {#collada-fallback-dae}

Für Formen ohne `.cdae` (Mods und die wenigen Formen, deren Zwischenspeicher älter ist)
wird die Collada-Datei so gelesen, wie der Importer von Torque sie liest, in dieselbe
Struktur:

- Detailstufen nach Torques Namensregel: Die Zahl am Ende eines Meshknotens ist die
  Pixelgröße, aus der es gezeichnet wird (`barrier75`, `barrier40`). Eine negative Zahl
  oder ein Name `collision`/`Colmesh`/`LOS`/`nulldetail` wird nie gezeichnet. Eine Form
  ohne diese Regel hat eine Stufe.
- Einheiten aus `<unit meter>`, und Y-nach-oben wird zu Z-nach-oben gedreht.
- UVs werden auf die Konvention des Zwischenspeichers umgedreht (v läuft nach unten im Bild).

Geprüft gegen die eigene `.cdae` des Spiels derselben Dateien: fast alle stichprobenartig
geprüften Grenzen auf 1 cm genau, 583 mit derselben Dreieckszahl, 94 % der UVs der
Materialien identisch. Der Test mit installiertem Spiel verlangt, dass 90 % von bis zu
60 Formpaaren aus dem gemeinsamen Kunstarchiv auf 1 cm übereinstimmen.

## Nicht gelesen {#not-read}

- Bodenbedeckung (prozedurales Gras) und alles, was zur Laufzeit entsteht.
- Animierte Sequenzen und Skinning.
- Fahrzeuge und Töne (werden nie eingehängt).
