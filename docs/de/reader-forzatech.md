---
title: ForzaTech
nav_order: 7
lang: de
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, Muster, Platzierungen {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon läuft auf ForzaTech, der eigenen Engine von Turn 10. Diese Leser nehmen
eine Strecke aus ihren Archiven bis hin zu positionierten, texturierten Dreiecken. Sie
werden über `course`, `courses` und `terrain` aufgerufen (siehe
[Forza Horizon](course-forza-horizon.md)). `identify` erkennt eine `.minizip` und eine
nackte `.modelbin`, und `list` und `extract` nehmen eine `.minizip`, anhand der Namen in
der `ChunkContentsMiniZip<n>.txt` daneben oder nach Eintragsnummer (`#12`).

| Format | Modul |
|---|---|
| `.minizip`-Archive und ihre Namenslisten | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin`-Modelle und Gelände | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb`-Texturmuster | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo`-Platzierungsdateien | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` und Hashes der Materialtexturen | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| Geländekacheln nach Ort | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza hält einen Teil seiner Inhalte auch in gewöhnlichen ZIP-Archiven unter `media\`.
Pythons `zipfile` öffnet diese, und `forzatech.models_in_archive()` listet ihre
`.modelbin`-Einträge auf. Die Streckengeometrie liegt in den `.minizip`-Archiven.

## `.minizip`: ein Archiv ohne Namen {#minizip-an-archive-with-no-names}

Eine Strecke liefert vier `GeoChunk<n>.minizip`-Archive aus, bei einer offenen Welt
jeweils mehrere zehn Gigabyte, mit Hunderttausenden Einträgen. **Die Archive speichern
überhaupt keine Namen**: keine Namenstabelle und keinen Kopf je Eintrag, nur eine
laufende Nummer. Die Namen stehen in `ChunkContentsMiniZip<n>.txt` neben jedem Archiv,
eine Zeile je Eintrag in Eintragsreihenfolge (`<build path>zipcache\pc\<path>|<bundle>`).
Diese Zuordnung ist der einzige Weg, eine Datei anzufordern. Alles bis einschließlich
`zipcache\pc\` wird weggelassen, und Suchen ignorieren Groß- und Kleinschreibung.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Drei Details im Index erzeugen auch dann Ausgaben, wenn man sie falsch liest. Der Leser
behandelt alle drei richtig:

| Detail | Was ein unvorsichtiger Leser tut | Wie es aussieht |
|---|---|---|
| die Segmentbasis ist **64 Bit** | liest sie als u32 plus Auffüllung | richtig für die ersten 4 GB, dann Rauschen von der richtigen Länge |
| die Basis ist **auf 8 Byte ausgerichtet** | ignoriert das Auffüllwort nach der Bundle-Tabelle | in Archiven mit gerader Bundle-Anzahl behauptet jeder Eintrag einen Codec, den es nicht gibt |
| die gespeicherte Länge eines Eintrags ist der Abstand bis zum nächsten Eintrag (oder zur Basis des nächsten Segments) **abzüglich seiner Auffüllung** (Flag-Bits 12-13) | nimmt den ganzen Abstand | LZ4 lehnt den Block sofort ab |

Codecs sind die unteren fünf Bits der Flags: `0x00` unkomprimiert, `0x08` rohes Deflate,
`0x1F` LZ4-Block. Jeder andere wird abgelehnt. Jeder Eintrag muss genau auf die Größe
entpacken, die er angibt, sonst wird er abgelehnt. Der Index (etwa 5 MB) wird einmal
gelesen, und Nutzdaten werden per Sprung gelesen.

Die Kopfzeile wird geprüft: Magic, eine 32-Byte-Kopfzeile und eine Segmentanzahl, die
`ceil(entries / per segment)` entspricht.

**Geprüft:** Einträge, stichprobenartig aus jedem Archiv einer Karte, entpacken jeweils
auf genau ihre angegebene Länge, unter allen drei Codecs.

## `.modelbin`: der Chunk-Container {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Die angegebene Dateigröße muss der tatsächlichen Größe entsprechen.
- Die **Kette**: Jeder Chunk beginnt dort, wo der vorige endete, aufgerundet auf
  4 Byte. Nichts in der Datei sagt das, deshalb ist es ein Beleg: Ein Datensatz, der mit
  falscher Schrittweite gelesen wird, ergibt diese Kette nicht. Sie galt für alle 252
  stichprobenartig geprüften Modelle.
- Eine `PGZP`-Datei, die dem Modelleser übergeben wird, wird als „ein ForzaTech-
  `.minizip`-Archiv, kein Modell" bezeichnet und auf `minizip.py` verwiesen, statt
  einfach abgelehnt zu werden.

Die Geometrie kommt aus diesen Chunks:

| Chunk | Enthält |
|---|---|
| `VLay` | ein Vertex-Layout: Attributnamen, dann Elemente (u16 Namenindex, u16 Kanal, Puffer, DXGI-Format, Offset); die Elementanzahl ist ein u16 |
| `VerB` | ein Vertex-Puffer hinter einer 16-Byte-Kopfzeile (Anzahl, Größe, u16-Schrittweite, u16-Attribute, Format) |
| `IndB` | der Indexpuffer, gleiche Kopfzeile |
| `Mesh` | ein Teilmesh: Material, Detailstufen-Maske, Indexbereich, Layout, Puffer, Schrittweite, Varianten-Tabelle und am Ende eine Positionsbox |
| `MatI` | eine Materialinstanz: ihr `.materialbin`-Pfad und Texturhashes |

### Positionen und die Box {#positions-and-the-box}

Positionen sind `R16G16B16A16_SNORM` (Format 13): vier vorzeichenbehaftete Shorts je
Punkt. `position = short / 32767 * scale + bias`, wobei Skalierung und Versatz die
letzten 32 Byte des `Mesh`-Chunks sind (zwei float4). Der Versatz liegt in **den
Weltkoordinaten des Spiels**, also landet eine Geländekachel dort, wo das Spiel sie
hinsetzt, ohne Instanztransformation. Deshalb genügt eine Telemetrie-Runde, um einen
Kartenausschnitt anzufordern. Jedes Teilmesh eines Modells trägt dieselbe Box (geprüft
an 860 davon).

### Das Vertex-Layout {#the-vertex-layout}

Ein Positionspuffer deckt jeden Punkt ab. Die übrigen Attribute sind in aufeinanderfolgende
Punktgruppen aufgeteilt, jede mit eigenem Puffer und eigenem Layout: Straße nahe einer
Kreuzung trägt drei UV-Sätze und zwei Tangenten, die Böschung daneben nur eine Normale.
Jedes Nicht-Positionsattribut ist vier Byte groß. Welches Layout welchen Puffer beschreibt,
wird aus den Teilmeshes entnommen, die aus ihm zeichnen, weil Layouts und Puffer nicht in
derselben Reihenfolge stehen (gleich, um eins verschoben oder vertauscht, je nach Modell).

| DXGI-Format | Code | Verwendet für |
|---|---|---|
| R16G16B16A16_SNORM | 13 | Position (der vierte Short ist das x der Normale) |
| R16G16_SNORM | 37 | Normale y, z |
| R16G16_UNORM | 35 | ein UV-Paar (Kanal = welcher Satz) |
| R8G8B8A8_UNORM | 28 | Farbe oder Mischgewichte |
| R10G10B10A2_UNORM | 24 | Tangente (nicht dekodiert) |
| R16_UINT | 57 | Indizes |

**Die Normale ist geteilt.** `NORMAL` enthält y und z. Das x ist der vierte Short der
Position, der wie Auffüllung aussah. Über Hunderttausende Geländepunkte korreliert er mit
+0,92 mit dem x der Dreiecksnormale und mit nichts anderem. Damit liegen 96 % der
Geländepunkte mit Hang innerhalb von 18° der berechneten Normale. Jede
Zwei-Komponenten-Kodierung ohne diesen Wert (darunter die oktaedrische in allen 48
Anordnungen) traf y und z richtig und x falsch.

Andere Positions- oder Indexformate werden **abgelehnt** ("only 13 (four shorts, scaled)
is implemented"; "only unsigned shorts are implemented").

### Teilmeshes {#submeshes}

Ein `Mesh`-Datensatz ist in der Standardform 238 Byte groß. Längere tragen vorn eine
längere Materialtabelle für **Varianten**, 238 + 8 x Anzahl - 4 Byte, und jedes Feld danach
rückt genau so weit nach hinten. Kürzere (218 Byte, bei manchem Gelände) behalten ihre
Offsets. Jeder Varianteneintrag ist `u16 0xFFFF, u16 Sommermaterial, u16 0xFFFF,
u16 Wintermaterial`. Die Detailstufen-Maske ist ein u16, ein Bit je Stufe ab Bit 1.

Nichts wird allein vertraut. Die Indexbereiche müssen den Indexpuffer genau ausfüllen,
jede `index count` muss 3 x `triangles` entsprechen, und die Schrittweite, die ein
Teilmesh nennt, muss die seines Puffers sein. Eine Tabelle, die scheitert, wird als Ganzes
abgelehnt, denn Dreiecke aus falsch gelesenen Feldern zu beschriften ist schlimmer, als
es nicht zu tun. Über Tausende stichprobenartig geprüfte Teilmeshes besteht jedes, dessen
Puffer-Index im Bereich liegt.

### Materialien und Texturhashes {#materials-and-texture-hashes}

Eine `MatI` nennt ihr Material über einen Pfad `Game:...\x.materialbin`, der durch Suche im
Chunk gefunden wird. Ihre Texturen sind `u32 slot, u32, u32 hash`-Datensätze, 33 Byte
auseinander und nicht ausgerichtet, deshalb wird der Chunk an jedem Byte-Offset nach Wörtern
durchsucht, die als Texturhashes bekannt sind. Diese stammen aus der `AssetManifest.xml`
der Strecke (`<Texture Source="...\name.swatch" SourceHash="...">`, gelesen bis
`</Textures>`). Der Slot `0x88B483AA` ist die Grundfarbe des Standardshaders. Wie dann die
Farbtextur gewählt wird, steht unter [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: Texturmuster {#pb-texture-swatches}

Ein Muster ist derselbe `burG`-Container wie ein Modell: eine 96-Byte-`HCXT`-Kopfzeile bei
Byte 44, dann ein Chunk mit Pixeln. Die Kopfzeile enthält die GUID der Textur (die im
Dateinamen steht), Breite und Höhe, die Anzahl der Mip-Stufen und den **Formatcode bei
Byte 72** (ForzaTechs eigene Nummerierung). Byte 84 enthält die Anzahl der Pixelbytes.

| Code | Format | Erkannt als |
|---|---|---|
| 0 | BC1, ein halbes Byte pro Pixel | dekodiert zu einer rot-weißen Randsteinfläche (unter BC4 Rauschen) |
| 9 | BC7, ein Byte pro Pixel | dekodiert zu einer Geländekachel, auf der die Strecke sichtbar ist |
| 13 | RGBA8, vier Byte pro Pixel | schlicht |
| andere | abgelehnt | "texture format N has not been identified; refusing to guess" |

Die Formate wurden durch Dekodieren echter Dateien auf allen Wegen bestimmt, die die
Nutzdatengröße erlaubt. Byte 47, das eine frühere Version für das Format hielt, ist bei
jeder der geprüften Texturen 4. Nur die oberste Mip-Stufe einer Datei wird dekodiert.
Jede Auflösung ist ein eigener Eintrag, `<name>_<guid>_quality<n>.pb`, Qualität 1 am
kleinsten bis 5 am größten. Bei Geländekarten liegen die zwei größten in einem anderen
Archiv als der Rest. Dekodiert wird über Pillows BCn-Dekodierer, über eine erzeugte
DDS-Kopfzeile.

## Platzierungsdateien (`.pgeo`) {#placement-files-pgeo}

Eine Datei je Kategorie und je räumlicher Zelle:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Der Pfad allein gibt das
Quadrat der Zelle und die Kategorie an, sodass Dateien gefiltert werden können, ohne sie zu
öffnen.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Wie jedes Feld entschieden wurde:

| Feld | Entschieden durch |
|---|---|
| Position ist Festkomma 16.16, kein Bruchteil der Box | aufeinanderfolgende Leitplanken liegen genau 4,000 m auseinander (die Länge des Modells) |
| Vorzeichen-Betrag, nicht Zweierkomplement | Zweierkomplement setzte negative Koordinaten zig Kilometer neben die Karte; mit Bit 31 als Vorzeichen landet jeder stichprobenartig geprüfte Datensatz jeder Kategorie innerhalb der Box seiner Datei |
| die Vektoren sind die eigenen Achsen des Modells | das Ende jeder Leitplanke liegt auf dem Anfang der nächsten: 93,5 % innerhalb von 5 cm, Median 0,000 m |
| Byte 60 ist die Variante | die fünf Kopien eines Billboards lesen 0, 2, 2, 3, 4, während jede Leitplanke 0 liest |

Nur Namen, die auf `_3D` enden, sind Modelldatensätze. Die Variantentabelle davor nennt
Namen ohne dieses Suffix, und als Datensätze gelesen landen sie im Unendlichen. Ein
Kandidatendatensatz wird nur akzeptiert, wenn seine Anzahl in die Datei passt, und
Instanzen mit nicht endlichen Zahlen werden verworfen.

## Nicht umgesetzt {#not-implemented}

- Vertex- und Indexformate außer den oben genannten (abgelehnt).
- Texturformate außer 0, 9, 13 (abgelehnt).
- Tangenten (werden überlesen, nicht verwendet).
- Die Materialschichten des Geländeshaders. Die Bodentextur ist eine Deutung der
  Kachelkarten (siehe [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
