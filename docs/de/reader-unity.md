---
title: Unity
nav_order: 4
lang: de
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, Bundles, Meshes {#unity-serializedfile-bundles-meshes}

**Listet Objekte auf und dekodiert Meshes** von Unity-`SerializedFile` ab Format 22
(Unity 2020 bis 6000) und öffnet `UnityFS`-Bundles. Es gibt keinen Unity-Kursexport.

Quellen: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Befehle: `identify` (Container und Bundles), `meshes` (nur nackte Container).

## Der Container {#the-container}

Unity liefert eine Ebene als serialisierte Objektgraphen aus: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` und Asset-Bundles. Jeder enthält
eine Tabelle von Objekten, die mit einer Klassen-ID markiert sind.

Der Header ist die Stelle, an der das Lesen unbemerkt schiefgeht. Die ersten sechzehn
Byte sind vier big-endian `uint32`, die aus Kompatibilitätsgründen bleiben. Im Format 22
sind drei davon null, und die echten Werte folgen, weil eine Datei 4 GB überschreiten
kann:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Die zweite `metadata size` ist ein `uint32` zwischen zwei `int64`. Wer alle drei als
64 Bit annimmt, verschiebt die Versionszeichenkette um vier Byte. Sie ergibt dann immer
noch etwas, das wie eine Zeichenkette aussieht, und alles danach gerät auf Abwege. Der
Header ist big-endian. Alles danach folgt dem Endianness-Byte (0, little-endian, auf jedem
Desktop-Build).

Nach dem Header folgen: die Engine-Versionszeichenkette, die Plattform, das Flag für den
Typbaum, die Typtabelle (Klassen-ID je Typ), die Objekttabelle (Pfad-ID, Offset, Größe,
Typ) und die Externals (andere Dateien, auf die ein Zeiger verweisen kann).

| Fall | Ergebnis |
|---|---|
| Format 22-30 | gelesen |
| Format 9-21 (vor Unity 2020) | abgelehnt: die Offsets stehen im alten Header, und keine vorliegende Datei nutzte ihn |
| außerhalb von 9-30 | abgelehnt |
| Typbaum eingebettet (Editor-Builds) | abgelehnt: ausgelieferte Builds betten keinen ein, und der Editor-Weg ist nicht umgesetzt |
| ein Bundle, wo ein Container erwartet wird | abgelehnt, mit einem Hinweis auf den Bundle-Leser |

Es gibt **keinen allgemeinen Deserialisierer**. Ausgelieferte Builds tragen keinen
Typbaum, weil das Schema in den Player einkompiliert ist. Deshalb muss jede Klasse gegen
ein Layout geparst werden, das für ihre Version bekannt ist. Nur `Mesh` wird dekodiert.
Andere Klassen werden nach Name und Anzahl gemeldet (`GameObject`, `Transform`,
`MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`,
`MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; andere als `class<id>`).

**Geprüft** über viele installierte Spiele und Millionen Objekte: Die Objekttabelle muss
den Datenbereich lückenlos ausfüllen, ohne Überlappungen, mit nichts außer Ausrichtungs-
Auffüllung zwischen den Objekten, und das letzte Objekt endet auf dem letzten Byte der
Datei. Ein falsch gelesener Header kann das nicht erzeugen. Der Test mit installiertem
Spiel wiederholt das an bis zu sechs `resources.assets`- / `sharedassets0.assets`-Dateien,
die in `*_Data`-Ordnern gefunden werden.

## Bundles (`UnityFS`) {#bundles-unityfs}

Ein Bundle ist ein komprimierter Container aus `SerializedFile`s. Die Blockliste und das
Verzeichnis sind ebenfalls komprimiert. Das Verfahren steht in den unteren sechs Bit eines
Flag-Wortes: 0 unkomprimiert, 1 LZMA (Unitys 5-Byte-Kopf mit eingesetzter Größe), 2 und 3
LZ4 / LZ4HC. Ab Format 7 wird der Kopf auf 16 Byte ausgerichtet. Das Flag `0x80` legt das
Verzeichnis ans Dateiende. `UnityWeb`, `UnityRaw` und `UnityArchive` (vor 5.3) werden
erkannt, aber nicht gelesen.

## Meshes {#meshes}

`read_mesh` dekodiert ein `Mesh`-Objekt zu Positionen, Normalen, dem ersten UV-Satz und
Dreiecken, in der Reihenfolge, die Unity 2019+ schreibt: Name, Teilmeshes, Blend Shapes
(übersprungen), Bind Poses und Knochendaten (übersprungen), die Flags für Komprimierung
und Lesbarkeit, der Indexpuffer, die Vertex-Kanäle und Vertexdaten, der komprimierte
Mesh-Block, die lokale Begrenzungsbox und die Streaming-Information.

- **Externe Punkte.** Der größte Teil der ausgelieferten Geometrie liegt in einer
  `.resS`-Datei neben dem Container. Das Tool liest sie aus dem Ordner des Containers (nur
  der Dateiname des gespeicherten Pfads `archive:/...` wird verwendet). Eine fehlende
  `.resS` ist ein Fehler, kein leeres Mesh.
- **Streams und Kanäle.** Kanäle sagen, welcher Stream, Offset, welches Format und welche
  Dimension jedes Attribut hat. Streams liegen hintereinander, jeder auf 16 Byte
  aufgefüllt, sodass der Anfang eines Streams aus den Schrittweiten davor summiert wird.
  Formate: float32, float16, unorm/snorm 8 und 16 (normalisiert) und einfache Ganzzahlen.
- **Topologie.** Nur Dreiecke (Topologie 0). Streifen, Vierecke und Linien werden
  abgelehnt, denn eine falsche Umwandlung sieht aus wie echte Geometrie.
- **Komprimierte Meshes** (quantisierte Deltas) werden abgelehnt: "mesh '...' is stored
  compressed; that encoding is not implemented".

### Die Selbstprüfung {#the-self-check}

Ein Struct in der falschen Reihenfolge zu lesen wirft keinen Fehler. Es liefert plausible
Zahlen. Deshalb wird jedes dekodierte Mesh gegen die **Bounding Box geprüft, die Unity
dafür gespeichert hat**, vom Editor aus den echten Punkten berechnet. `aabb_matches()`
besteht, wenn die Ecken der dekodierten Box innerhalb von 2 % der Größe der gespeicherten
Box liegen. `meshes` gibt bei jeder Zeile `ok` oder `BOUNDS DISAGREE` aus.

**Geprüft:** Meshes, stichprobenartig aus mehreren Spielen, dekodieren mit übereinstimmenden
Grenzen. Der Test mit installiertem Spiel wiederholt die Prüfung an den installierten
Containern.

## Nicht umgesetzt {#not-implemented}

- Formate vor 2020.
- Komprimierte Meshes.
- Jede andere Klasse als `Mesh`: kein Szenengraph, keine Transformationen und keine
  Materialien, deshalb liegen Meshes in ihrem eigenen lokalen Raum.
- `meshes` auf einem Bundle. Der Bundle-Leser existiert in Python
  (`UnityBundle.serialized_files()`), aber der Befehl nimmt nur einen nackten Container.
