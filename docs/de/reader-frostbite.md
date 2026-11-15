---
title: "Frostbite: `.toc`, `.cas`, Bundles, Meshes und Level"
nav_order: 5
lang: de
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, Bundles, Meshes und Level {#frostbite-toc-cas-bundles-meshes-and-levels}

**Liest ein Battlefield-6-Level bis hinunter zu seinem Gelände, seinen platzierten Meshes und deren
Farbkarten und schreibt es als `.glb`.** Frostbite-Spiele (Battlefield, Need for Speed, Dead Space)
halten ihre Inhalte in `.cas`-Blobs, beschrieben durch `.toc`-Inhaltsverzeichnisse. Die Tabelle eines
Levels sagt, welche Bundles das Level lädt, die Bundles nennen jedes Asset, und die Assets sagen, welches
Mesh wo steht.

Quellen:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(Tabellen, Pakete, Nutzdaten),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(Bundles und ihre Manifeste),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-Partitionen),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(Höhenfeld),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(Texturen und Materialien),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(Platzierung und Export).
Befehle: `identify`, `levels`, `level` (siehe [Befehle](commands.md#levels-and-level-frostbite)).

Nichts davon ist vom Spiel dokumentiert. Jedes Layout unten wurde aus den Dateien abgelesen und dann
gegen alle Dateien geprüft, und jeder Abschnitt sagt, was die Prüfung war. Wo die Frosty-Modding-Werkzeuge
ältere Versionen einer Struktur beschreiben, folgen die Feldnamen ihren; es wurde kein Code von ihnen
übernommen (siehe [Regeln und Lizenzen](rules-and-licences.md)).

## Der Header, der verschlüsselt aussieht und es nicht ist {#the-header-that-looks-encrypted-and-is-not}

| Kennung (u32, little-endian) | Bedeutung | Behandlung |
|---|---|---|
| `0x00CED100` | plain: der Baum beginnt sofort | gelesen |
| `0x01CED100` | signed: eine 556 Byte lange Signatur, dann der Baum **im Klartext** | gelesen |
| `0x03CED100` | XOR-verschleiert, mit dem Schlüssel im eigenen Header der Datei | erkannt und abgelehnt |

Die signierte Form liefert das aktuelle Battlefield aus. Die Bytes mit hoher Entropie nach der Kennung
sind eine Signatur, kein Chiffretext.

## Der DbObject-Baum {#the-dbobject-tree}

Eine einzige rekursive Struktur. Jedes Feld ist ein Typbyte (die unteren fünf Bits der Typ, Bit 7
"anonym"), ein optionaler Name und ein Wert. Container tragen ihre Länge als variable Ganzzahl und enden
mit einem Null-Byte. `parse_toc` prüft die Länge jedes Containers, daher heißt eine Datei, die sich
parsen lässt, dass sie verstanden wurde. `layout.toc` liegt in dieser Form vor.

## Installationspakete {#installation-packages}

Jede Adresse nennt das **Installationspaket**, zu dem ihr Blob gehört. Jedes Paket nummeriert seine Blobs
ab `cas_01`, daher ist die Blobnummer allein mehrdeutig, sobald mehr als ein Paket installiert ist, und das
ist immer der Fall.

- `layout.toc` listet die Pakete unter `installManifest.installChunks`, jeweils mit einer
  `persistentIndex` und einem `installBundle` wie `Win32/installation/<package>`.
- Die Blobs des Pakets liegen in diesem Ordner, unter `Data` für das Grundspiel oder unter
  `Update/<pack>/Data` für das, was später kam.
- Ein Adresseintrag trägt die volle 32-Bit-`persistentIndex`: die untere Hälfte des ersten Wortes hält
  die obere Hälfte, die obere Hälfte des zweiten Wortes die untere Hälfte; die untere Hälfte des zweiten
  Wortes ist die Blobnummer.

Prüfung: jede Adresse in jeder binären Tabelle einer Installation löst sich in ein angekündigtes Paket
auf und liegt innerhalb des Blobs, den sie nennt. Eine frühere Version nahm die erste `cas_NN.cas` mit der
richtigen Nummer. Ein Drittel der Nutzdaten, die sie las, sah dann nach hoher Entropie aus und wurde für
Verschlüsselung gehalten. Es waren die richtigen Offsets in der falschen Datei. Nichts gefunden ist
verschlüsselt.

## Die Level-Tabelle {#the-level-table}

Die Tabelle eines Levels (`levels/<level>/<level>.toc`) ist eine Abschnittstabelle: fünfzehn
big-endian-Header-Wörter, dann Abschnitte, Ende an Ende gelegt, deren Offsets sowohl angegeben als auch aus
zwei Zählwerten ableitbar sind.

| Abschnitt | Inhalt |
|---|---|
| Bundles | eine Hash-Tabelle (je ein Wort), dann ein 16-Byte-Eintrag pro Bundle: Schlüssel, `0x40000000` \| Größe, 0, Offset |
| Chunk-Hash-Tabelle | je ein Wort pro Chunk |
| Chunks | 16-Byte-ID (die GUID des Chunks **Byte-umgekehrt**), dann ein Wort: `0x80000000` \| 4 x der Index seiner Adresse |
| Adressen | vier big-endian-Wörter: Paket (aufgeteilt), Blob, Offset, Größe |

Die Chunk-IDs und die Adressen stehen in **verschiedener Reihenfolge**. Liest man sie in Dateireihenfolge,
wird jeder Chunk mit den Bytes eines anderen Chunks gepaart, die einwandfrei dekodieren (meist als Ton)
und daher nicht falsch aussehen, bis ein Mesh als Rauschen erscheint. Prüfung: in einem Level bilden die
Indexwörter eine Permutation von 0 bis zur Chunkanzahl minus eins.

Die Bundles liegen nach der Abschnittstabelle eingebettet. Jedes hat neun big-endian-Header-Wörter, dann
seine Einträge: acht Byte Offset und Größe, davor acht weitere Byte mit Paket und Blob, wenn das Flag-Byte
des Eintrags sein oberstes Bit gesetzt hat. Prüfung: bei jedem Bundle endet der letzte Eintrag genau dort,
wo die Flag-Bytes beginnen.

### Welche Tabelle ist das Level {#which-table-is-the-level}

Ein Level kann mehrere Tabellen mit demselben Namen haben: eine im `Data` des Grundspiels, eine in jedem
Update (`Update/<pack>/Data`), das es ausliefert oder ändert, und eine in jedem hochauflösenden Paket
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Nur manche enthalten Bundles. Bei einem
Level, das ein Update ausliefert, enthält die Tabelle im Grundspiel nur Chunks und keine Bundles, und die
im Update ist das Level; die erste gefundene Tabelle zu nehmen, exportierte nichts davon.

Das Level ist daher die Tabelle mit den meisten Bundles, wobei eine spätere Schicht bei Gleichstand
gewinnt (zuerst das Grundspiel, dann die Updates in Namensreihenfolge). Die Tabellen gleichen Namens ohne
Bundles sind seine **Ergänzungen**: ihre Chunks kommen zu denen des Levels hinzu, denn sie enthalten die
größten Mipmaps seiner Texturen. Ein Texturheader nennt diesen Chunk bei +164 (siehe
[Texturen und Materialien](#textures-and-materials)). `levels` gibt aus, woher jedes Level stammt und wie
viele Ergänzungen es hat.

## Bundle-Manifeste {#bundle-manifests}

Der erste Eintrag eines Bundles ist sein Manifest, unkomprimiert gespeichert. Es ist das binäre
Bundle-Format früherer Frostbite-Spiele mit neuer Kennung `0xD68E799D`: Zähler, SHA-1s, ebx- und
res-Einträge (Namensoffset und Größe), res-Typen, Metadaten und IDs, Chunk-GUIDs, Zeichenketten. Die
übrigen Einträge des Bundles sind die ebx, die res und die Chunks, in dieser Reihenfolge. Prüfung: die
Zähler stimmen mit den Einträgen in jedem Bundle überein, und die Zeichenketten beginnen dort, wo die
Einträge enden.

Ressourcentypen sind Hashes. `0x49B156D4` ist MeshSet (jede res dieses Typs heißt `..._mesh`),
`0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` liest all dies für ein Level in wenigen Sekunden: ein Level hat dutzende Bundles und
zehntausende ebx-, res- und Chunk-Einträge.

## Nutzdaten-Blöcke {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Eine komprimierte Größe von null heißt gespeichert, solange es sich zu derselben Größe dekomprimiert.

| Methodenwort | Codec |
|---|---|
| `0x0070`, `0x0071` | keiner |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), aus der eigenen DLL `oo2core` des Spiels) |
| anderes, bei gleichen Größen | wird so kopiert, wie gespeichert |
| anderes | abgelehnt |

Aus dem richtigen Paket gelesen, dekodierte jede stichprobenartig geprüfte Nutzlast.

## EBX-Partitionen {#ebx-partitions}

EBX enthält alles, was nicht Rohdaten sind. Jede Partition ist eine RIFF-Datei: `EBXD` (die Daten, auf 16
ausgerichtet), `EFIX` (Partitions-GUID, Typ-GUIDs und Signaturen, Instanz, Zeiger-, Import- und
Typinfo-Offsets, Importe und die Offsets der Arrays, boxed values und Zeichenketten), `EBXX` (die
Array-Tabelle: Offset, Anzahl, Hash, Flags, Elementtyp). Ein Zeigerfeld ist acht Byte: null ist kein
Zeiger, ein ungerader Wert ist Import Nummer `value >> 1`, alles andere ist relativ zum Feld.

Die **Typbibliothek ist nicht lesbar**. Das Spiel liefert sie in seinem anfänglichen Dateisystem aus, das
verschlüsselt ist, und dieses Paket fasst es nicht an. Typen werden über GUID und Signatur erkannt, die
jede Partition trägt, und die wenigen Typen, die der Level-Export braucht, wurden aus den Daten abgeleitet.

## MeshSet {#meshset}

Ein Mesh ist eine MeshSet-res (die Beschreibung) und ein Chunk pro Detailstufe (die Puffer).

| Teil | Aufbau |
|---|---|
| Präfix | vier Wörter: Headergröße (176 oder 192), Größe des Stufendatensatzes (176 bis 188), Größe des Abschnittsdatensatzes (368), 0 |
| Header | Begrenzungsbox; sechs i64-Stufenoffsets; Mesh-Typ bei `0x6C` (starr, geskinnt, zusammengesetzt); Stufen- und Abschnittszahlen bei `0x9C` |
| Stufe | Abschnitte bei `+0x08`; fünf Zeichnungslisten bei `+0x14` (undurchsichtig, transparent, Decal, nur Tiefe, Schatten); Indexformat bei `+0x54` (`0x21` u16, `0x2E` u32), Index- und Vertex-Bytes; Chunk-GUID bei `+0x74` |
| Abschnitt | Materialname; Vertex-Schrittweite; Dreiecke, erster Index, Vertex-Offset (Bytes), Vertexanzahl bei `+0x20`; Vertex-Deklaration bei `+0x64`: 16 x (Verwendung, Format, Offset, Stream), 16 Stream-Schrittweiten, Zähler |
| Chunk | der Vertex-Puffer, dann der Index-Puffer. Die Streams eines Abschnitts folgen aufeinander; Indizes zählen ab dem ersten Vertex des Abschnitts |

Positionen sind Verwendung 1, Stream 0, Offset 0, als vier Halbwerte oder drei Floats.
Gezeichnet werden nur die undurchsichtigen und transparenten Abschnitte. Jeder Abschnitt mit dem Namen
`..._shadow` steht nur in der Schattenliste, und nur dort; die Listen entscheiden.

Prüfung: jedes Mesh eines Levels, dessen Stufen in Chunks liegen, dekodiert sich, und fast alle haben 99 %
oder mehr ihrer Vertices in ihrer angegebenen Box; der Rest verfehlt sie wegen Rundung bei Half-Floats. Eine
dekodierte Kiste misst etwa einen Meter, Y nach oben, mit nach außen zeigenden Normalen.

## Platzierung {#placement}

Die Content-Pipeline sammelt die statischen Objekte jeder Unterwelt in einer **statischen
Modellgruppe**: ein Array von Mitgliedern, eines pro Mesh, jedes mit seinen Instanztransformationen.

| Typ (GUID, Signatur) | Aufbau |
|---|---|
| Mitglied `ad13064e…`, `0xF861A878` | 224 Byte: `+88` Array der Transformationen, `+112` der Objekt-Blueprint (Import), `+160` das Mesh-Asset (Import) |
| Transformation `101dce06…`, `0x5E6D8C37` | 64 Byte: rechts, oben, vorne, Verschiebung, je ein vec3 mit 16 Byte aufgefüllt |

Die Partition des Mesh-Assets heißt wie seine MeshSet-res, daher gibt die Partitions-GUID des Imports das
Mesh an. Ein Punkt landet bei `x·right + y·up + z·forward + translation`. Die Transformation der Gruppe
selbst war in jeder geprüften Gruppe die Identität und wird nicht angewendet.

Prüfung: in einem Level löst sich jedes Mitglied jeder Gruppe in ein Mesh auf; die meisten Kopien haben
eine Drehung mit Determinante 1 bis auf ein Tausendstel, die übrigen sind skaliert oder gespiegelt. Die
Typ-GUIDs und Signaturen sind in anderen Leveln gleich. Ein Spiel-Update, das das Layout ändert, ändert die
Signatur, und der Leser findet dann nichts, statt falsch zu lesen.

### Einzeln platzierte Objekte {#objects-placed-one-by-one}

Was die Pipeline nicht gruppieren kann - zerstörbare Objekte, Container, Trümmer - wird durch
**Objektverweise** und **Prefab-Verweise** in den Partitionen des Levels platziert:

| Typ (GUID, Signatur) | Aufbau |
|---|---|
| Objektverweis `a9a6a6ad…`, `0xC4856BEC` | `+32` die Transformation (wie oben), `+112` der Objekt-Blueprint (Import) |
| Prefab-Verweis `117c746e…`, `0xDE3FE9B4` | dasselbe; der Blueprint ist ein Prefab, eine Partition weiterer Verweise |

Prefabs sind verschachtelt; eine Kopie landet mit ihrer eigenen Transformation mal der ihres Elternteils
(Zeilenvektoren), bis zu acht Ebenen tief. Ein Objekt-Blueprint wird als die Meshes gezeichnet, die er
importiert, ohne die zerstörten Zustände (`dc_...`). Ein gruppiertes Prefab wird als sein
`..._nongroupable_autogen`-Rest referenziert, damit nichts zweimal gezeichnet wird.

Der Durchlauf beginnt nur bei den Welten und Ebenen des Levels. Eine Partition, deren erste Instanz ein
Prefab-Blueprint ist (`134919fc…`, `0x0247807D`), ist die Definition eines Prefabs, und ein Level hält viele
davon in seinem eigenen Ordner, die von seinen Welten auf anderen Wegen als diesen Verweisen platziert
werden; als Welt behandelt, legt ein Prefab seinen Inhalt in seine lokalen Koordinaten. Das häuft
Hunderte Kopien um den Ursprung der Welt, tief unter dem Boden. Welten und Ebenen haben `a10ebe0f…`,
`0xD3D16C3C` als erstes.

Blueprints, die außerhalb des Spiels bereitgestellt werden, werden nicht verfolgt: Entwicklungs- und
Testassets (`game/dev/`, `test/`), das Set der Zwischensequenz am Rundenende (`..._gameend_...`: unter dem
Boden bereitgestellt) und der Controller der Todeskamera (`.../deathflow/...`, dessen Gadgets am Ursprung
der Welt stehen). Sie werden am Pfad ihres Assets erkannt, nicht an ihrer Ebene: dieselbe Ebene, die das
Set der Zwischensequenz enthält, kann die echten Wände und Dächer des Levels platzieren. Nach beiden Regeln
liegt in den geprüften Leveln keine Kopie mehr als 10 m unter dem Gelände, und Kopien stehen dort auf dem
Gelände, wo das Spiel sie zeigt.

**Detailstufen, die als Ersatz dienen.** Die letzte Detailstufe eines Meshes darf zu einer Ersatzansicht
in der Ferne mit eigenem Material wechseln: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Ein
Gitterturm mit zehntausenden Dreiecken kann in einer Silhouette von einigen hundert enden, die das Budget
wählen würde und die aus der Nähe ein massiver Dorn ist. Eine Detailstufe, die ein solches Material einführt,
das ihre feinste Stufe nicht hat, wird nie gewählt; die gröbste Stufe des Meshes ist die letzte echte.

## Gelände {#terrain}

Quelle: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Das Gelände ist eine TerrainStreamingTree-res (Typ `0x22FE8AC8`) und die Chunks, die sie nennt.

| Teil | Aufbau |
|---|---|
| Header | 34 Byte; die Knotenanzahl bei 25 |
| Rasterbäume | ein Typbyte und eine u32-Länge je Baum, bis zu einem Typbyte `0xFF`. Typ 0 ist das Höhenfeld: Proben pro Seite bei +5 (265), Höhenbereich bei +21 (1.280 m), das Geländequadrat im ersten Knotendatensatz bei +77 (8.192 m im geprüften Level). Es enthält Begrenzungsboxen der Knoten und eine 16 x 16 Min/Max-Pyramide je Knoten, nicht die Höhen |
| Streaming-Knoten | der Quadtree, in Tiefe zuerst: Chunk-Größe und GUID; ein optionaler zweiter Chunk; ein Flag-Byte (Bit 0: der Chunk beginnt mit einer Höhenseite); hat Kinder. Kinder in der Reihenfolge (0,0), (1,0), (1,1), (0,1) |
| Höhenseite | die ersten 265 x 265 u16 eines Chunks eines markierten Knotens, zeilenweise; Höhe = Wert x 1.280 / 65.535 m; Spalten entlang x, Zeilen entlang z, ab der niedrigen Ecke des Knotens; ein Rand von 4 Proben, also 256 Zellen je Knoten |

Jeder Schritt wurde einzeln geprüft:

- Das Parsen des Knoten-Quadtrees verbraucht die res bis zu ihrem letzten Byte, mit den angegebenen
  529 Knoten.
- Benachbarte Knoten teilen ihre neun Randspalten genau, daher ist die Schrittweite 256.
- Die Proben eines Kindes an jeder zweiten Position sind mit einem Rand von 4 genau gleich denen seines
  Elternteils und liegen bei jedem anderen Rand 90 bis 700 Einheiten daneben.
- Das niedrigste Wort im Level dekodiert auf den Zentimeter zur niedrigsten Höhe der Begrenzungsbox.
- Von den acht Arten, wie das Quadrat auf der Welt liegen könnte, bringt nur x entlang x und z entlang z
  die platzierten Objekte auf es: die Hälfte der stichprobenartig geprüften Kopien innerhalb von etwa 2 m,
  gegenüber einem Vielfachen davon bei jeder anderen Art.

Die platzierten Objekte messen dann das Ergebnis. Der tiefste Punkt jeder Kopie, gegen das Gelände darunter
(bilinear, aus dem feinsten Knoten):

| Platziert | Median des Abstands | Median mit Vorzeichen |
|---|---|---|
| Bäume und Büsche | deutlich unter einem Meter | knapp unter der Oberfläche |
| Requisiten | ein bis zwei Meter | auf der Oberfläche |
| Felsen | etwa ein Meter | um etwa einen Meter eingesunken |
| Gebäude | mehrere Meter (sie stehen auf Fundamenten) | leicht eingesunken |

Vegetation wird nur auf dem Boden platziert und nirgends sonst, daher ist sie die schärfste Prüfung: ihre
Ursprünge liegen im Median 0,07 m von der Oberfläche. Gebäude streuen weit, weil die Kategorie Wände, Böden
und Bauteile mehrgeschossiger und unterirdischer Bauwerke enthält. Verschiebt man das Gelände um 64 m seitlich,
sinkt der Anteil der Kopien innerhalb von 0,5 m von 29 % auf 10 %.

`level` zeichnet das Höhenfeld als `ground:terrain`, jeder Teil davon aus dem feinsten Knoten mit Höhen dort
und nicht feiner als `--ground-spacing` (standardmäßig 4 m: 3,7 Millionen Dreiecke für das geprüfte Level,
dessen feinste Knoten 0,5 m haben). Teile verschiedener Auflösung treffen sich mit kleinen Stufen; nichts
glättet sie.

Der Chunk eines Knotens enthält außerdem die Seiten der Layer-Masken nach seiner Höhenseite, und sein zweiter
Chunk endet mit der Farbkarte des Knotens (siehe [Gelände-Layer](#terrain-layers)).

## Gelände-Layer {#terrain-layers}

Das Spiel schattiert das Gelände nahe einem Spieler, indem es Oberflächenmaterialien über bemalte Masken
aufspleißt, mit einer Farbkarte darüber, und Decals (Straßen, Asphaltflicken, Landebahnmarkierungen)
darauf zeichnet. Frostbites eigene Darstellung des Systems (Widmark, "Terrain in Battlefield 3", GDC 2012)
nennt als Raster des Geländes das Höhenfeld, Shader-Spleiß-Masken, eine Farbkarte, "used as an overlay on top
of shader splatting", physikalische Materialien, eine Zerstörungs-Tiefenmaske, eine Albedo-Karte für das
Bounce-Licht und zusätzliche Maskenkanäle; die Kacheln eines Rasters tragen einen Rand für die
Rendering-Algorithmen. Die Streaming-Tabelle der geprüften Level hat sieben Rasterbäume, Typen 0, 1, 2, 4,
5, 7 und 8, deren Header mit ihrer Kachelgröße beginnen: 265 für das Höhenfeld (Typ 0) und Typ 2, 72 oder 66
für die Masken (Typ 1), 132 mit einem Rand von 2 für die Farbkarte (Typ 4), 260 mit einem Rand von 2 für
Typ 5.

**Die Layer-Liste.** Die `....layergraphs`-res des Geländes listet einen 32-Byte-Eintrag je Layer, in der
Reihenfolge, in der die Maskendatensätze sie nummerieren (34 Einträge, 34 Depot-Abschnitte und Layerindizes
0 bis 33 in einem Level); die ID jedes Eintrags endet mit seinem Abschnittsschlüssel im Shader-Block-Depot des
Layer-Graphen (`....layergraphs_shaderblockdepot`), dessen Block die Karten des Layers nennt: eine
`_cv`-Farbkarte, `_nhs`- und `_ao`-Karten je Oberfläche, dazu gemeinsame Detail- und Rauschkarten. Viele
Layer nennen gar keine Karten: sie sind Quellen, die der Layer-Graph liest. Die Farbe eines Layers ist der
Mittelwert seiner `_cv`-Karte; der Kachelmaßstab wird nicht gefunden. Das Geländeasset endet mit einem
fünf-Byte-Eintrag je Layer (ein Byte, dann ein u32-Layerindex oder -1).

**Die Masken.** Rasterbaum 1 ist der Quadtree der Masken. Sein Körper beginnt mit 59 Byte, die Seitenlänge
der Seite bei 0: 72, wo die Seiten BC4 sind (72 x 72, 2.592 Byte), 66, wo sie unkomprimierte Achtbit sind
(4.356 Byte). Dann folgt eine Gruppe je Knoten, in Tiefe zuerst:

| Teil | Aufbau |
|---|---|
| Gruppe | u16; u16 Datensatzanzahl; u32 Seitenanzahl; die Datensätze; ein Null-Byte. Eine Gruppe ohne Datensätze ist insgesamt 7 Byte |
| Datensatz | 33 Byte: u16 Layer, u16 Hash, die Box des Quadranten (vier Floats), zwei Flag-Bytes, eine 85-Bit-Präsenzpyramide |

Die Datensätze einer Gruppe sind die vier Quadranten ihres Knotens, Layer für Layer, wobei die Quadranten
jedes Layers in der Reihenfolge (0, 0), (1, 0), (1, 1), (0, 1) stehen. Ein Datensatz mit gesetztem zweitem
Flag deckt seinen Quadranten ganz ab und hat keine Seite; einer ohne dieses Flag hat die nächste Seite; ein
Quadrant ohne Datensatz eines Layers, den seine Gruppe nennt, ist für diesen Layer leer; das erste Flag ist
genau dann gelöscht, wenn der Layer im Quadranten in der eigenen Gruppe weiterläuft, eine Ebene tiefer, und
sie dort ersetzt. Die Seitenanzahl ist die Zahl der Datensätze mit einer Seite.

Die Seiten: die Seiten der eigenen Gruppe eines Streaming-Knotens folgen in seinem Chunk nach der Höhenseite,
einem 4.358 Byte großen 16-Bit-Abschnitt und einem 67 x 67 Achtbit-Raster (vom Anfang des Chunks an, wenn er
keine Höhenseite hat); sein zweiter Chunk hält die Seiten der Gruppen seiner vier Quadranten eine Ebene tiefer,
Quadranten in der Reihenfolge der Farbkarte, dann die Farbkarte. Eine Seite ist die Fläche von 64 x 64 Texeln
des Quadranten, Zeilen entlang z und Spalten entlang x, mit einem Rand, der von seinen Nachbarn kopiert wird:
4 Texel auf einer BC4-Seite, 1 auf einer unkomprimierten.

Die Ränder beweisen die Platzierung ohne Urteil: zwei Seiten eines Layers nebeneinander müssen die Randtexel
des anderen tragen. `read_masks` prüft das für jedes Paar, das es platziert, und lehnt ein Level ab, in dem
weniger als 99 % übereinstimmen. Etwa ein Drittel der geprüften Level wird gelesen, mit übereinstimmenden
Rändern; einige haben keine gemalten Masken; die übrigen werden abgelehnt, fast alle durch die Prüfung (ihre
Chunks enthalten mehr, als dieses Layout kennt). Der Boden eines abgelehnten Levels nimmt die mittlere Farbe
seiner Oberflächenmaterialien, und der Export sagt, warum. Die Ränder zu einem vollen Quadranten sind 255,
die zu einem leeren 0.

Der 4.358 Byte große Abschnitt und das 67 x 67 Raster vor den Seiten werden nicht gelesen: ihre Werte liegen
in einem schmalen hohen Band, ohne kleine Werte und ohne Markierung.

**Die Bodenfarbe.** Der Layer-Graph mischt die Layer in einem kompilierten Shader-Graphen aus Masken, Hang,
Höhe und Rauschen, der nicht gelesen wird. `--ground-texture` färbt den Boden nach einer eigenen Regel, hier
als solche angegeben:

- Layer, deren Farbkarte nach Entfernung benannt ist, sind die Stellvertreter der Fernsicht und bleiben
  weg;
- die texturierten Layer, die neun Zehntel des Geländes oder mehr bedecken, sind die Basis. Ihre Masken sind
  fast überall voll, daher liegt, wo jeder liegt, die Entscheidung des Shaders, nicht ihre: die nach Fels oder
  Klippe benannten färben Hänge, die steiler als 40 Grad sind, die nach Kies benannten flaches Gelände (die
  anderen Basis-Layer, wenn keiner so heißt), und zwischen 20 und 40 Grad werden sie durch die Hangneigung des
  Höhenfeldes gemischt (genommen alle 4 m und bilinear über die eingebackenen Texel verteilt: in 4-m-Blöcken
  wiederholt, zeichnete es die felsige Farbe als hart begrenzte Flecken);
- jeder andere texturierte Layer wird nach Reihenfolge der Layer über die Basis gelegt, mit seiner eigenen
  Maske;
- die Farbkarte wird über das Ergebnis gelegt, wie es die Engine tut: doppelt die Bodenfarbe mal die Karte,
  sodass Mittelgrau sie unverändert lässt; wo die Farbkarte keine Texel hat, nimmt der Boden die mittlere
  Helligkeit der Karte, in Grau.

Geprüft gegen die mittlere Bodenfarbe von Spielbildern dreier Level (Farbton als Rot und Blau über Grün): der
eingebackene Spielbereich kommt in einem auf 1,00 / 0,69 gegen die 1,19 / 0,78 der Bilder, dessen Grasschichten
grün sind, wo die Bilder trockenes Gras zeigen; in einem anderen auf 1,19 / 0,82 gegen 1,01 / 1,04, dessen
Farbkarte selbst warm ist (1,13 / 0,88); und in einem dritten ohne Farbkarte auf 1,05 / 0,91 gegen 0,93 / 0,92.
Die Bilder sind beleuchtet und abgestimmt, daher misst dies den Farbton, nicht die Helligkeit.

**Die Farbkarte.** Der zweite Chunk eines Knotens enthält nach den Maskenseiten seiner Quadrantengruppen vier
BC7-Seiten von 132 x 132 (je 17.424 Byte), eine pro Quadrant des Knotens, in der Reihenfolge (niedriges x,
hohes z), (hohes x, hohes z), (hohes x, niedriges z), (niedriges x, niedriges z). Der Maskenbaum sagt, wie viele
Byte die Maskenseiten belegen, daher wird die Farbkarte über diese Anzahl gefunden und nicht über das Ende des
Chunks: in einem Level tragen die gröberen Knoten vier weitere solche Seiten danach, ein anderes Raster in einer
einzigen Farbe, und das Lesen der letzten vier Seiten des Chunks verlor die Farbkarte über neun Zehntel des
Geländes. Ohne diese Zählung wurde die Farbkarte auch in Leveln mit unkomprimierten Maskenseiten übersehen,
deren Seiten keine ganze Zahl von BC4-Seiten ergeben; die Farbkarte eines Levels ging von 0,4 auf 0,94 seines
Geländes. Die Reihenfolge wurde angepasst: Gegen die Ränder jedes Höhenfeldes eines Quadranten passt jede Seite
der Knoten mit Merkmalen zu einem Quadranten, unverdreht, mit 0,3 bis 0,54, wo die nächstbeste Platzierung
unter 0,2 liegt. Danach zusammengesetzt, fügen sich die Seiten eines Levels nahtlos zu den Straßen, dem Wasser
und den bebauten Gebieten des Testlevels, bei 0,5 m pro Texel im Spielbereich. Wo die Layer die Arbeit tun,
ist die Farbkarte nahezu neutral (Median 110, 107, 104); anderswo kann sie volle Farbe tragen. Ein Level, dessen
zweite Chunks nur unkomprimierte Maskenseiten enthalten, hat keine Farbkarte gelesen. Eine frühere Runde dieses
Lesers nannte diese Seiten nicht geografisch: sie wurden gegen die Hintergrundkarte gehalten, die eine ganz
andere Landschaft sein kann, und jede Seite wurde auf ihren ganzen Knoten statt auf einen Quadranten gelegt.

**Die Albedo für das Bounce-Licht** wurde gesucht und nicht gefunden: die Chunks der Wurzel und der
Knoten der ersten Ebene sind ganze Maskenseiten, und die Nutzlast von Typ 5 ist nicht gefunden.

**Löcher.** Das Geländeasset eines Levels (res-Typ `0x1CA38E06`) nennt drei Shader: einen
Standard-Oberflächenshader, einen Oberflächenshader für Löcher und einen Standard-Quellshader. Welchen Layer
der Löcher-Shader liest, ist nicht gefunden, daher wird das Höhenfeld nicht ausgeschnitten. In einem Level kann
das Navigationsnetz auf Felsmeshes laufen, die zig Meter unter dem Höhenfeld liegen, wo das Spiel sie
abgeschnitten haben muss. Gesucht und nicht gefunden: die Maske eines Layers, das 67 x 67 Raster, eine
reservierte Höhe (keine Höhenseite eines Levels enthält 0 oder 65.535) und ein Knotenflag (jeder Knoten unter
der Wurzel hat Flags 1). Rasterbäume 7 und 8 sind übrig. Beide sind lauflängenkodiert: ein Byte, das dem davor
gleicht, wird von einer Anzahl weiterer Kopien gefolgt (`ff ff 84` sind 134 Byte von 255). Baum 7 (Kachel 256,
ein vollständiger Quadtree mit fünf Ebenen, vier Bit je Probe) dekodiert zu Bytepaaren mit Werten 0 bis 3;
Baum 8 (Kachel 265) zu Bytes, meist 255, mit seinen übrigen Werten in regelmäßigen Läufen. Keine der beiden
Kachelgruppen ist bisher platziert, daher ist nicht bekannt, dass eine von ihnen die Löcher enthält.

**Decals** werden gelesen und eingebacken; siehe [Gelände-Decals](#terrain-decals).

## Gelände-Decals {#terrain-decals}

Quelle: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Straßen, Landebahnen, Betonvorfelder, aufgemalte Linien und Buchstaben, Reifenspuren: die
`TerrainDecals`-res (Typ `0x15E1F32E`) hält sie als flache Geometrie, die das Spiel über das Gelände legt.

| Teil | Aufbau |
|---|---|
| Header | bei +16 eine Slot-Anzahl n, dann n 16-Byte-Slots, dann die Datensatzanzahl |
| Datensätze | einer je Zeichen-Batch, aneinandergereiht, unterschiedlich lang: 156 Byte feste Felder - erster Vertex bei +32, Dreieckszahl bei +36, Textur-Kachelung in Metern bei +44 - dann die Vertex-Bytes des Batches (Offset, Größe), dann ein Ende, das seine Texturen über die Partitions-GUIDs ihrer Assets nennt |
| Vertices | 32 Byte: x, z (f32), 8 gepackte Bytes, u, v (f32), r, g, b, a (f16); jeder Batch eine einfache Dreiecksliste |
| Indizes | u32, zählen je Batch ab 0; nicht nötig |

Prüfungen:

- Die Vertexbereiche der Datensätze folgen lückenlos aufeinander und decken alle Vertices genau ab, und der
  erste Vertex jedes Datensatzes mal 32 ist sein Offset;
- so gelesen sind die Dreiecke kompakte Decals (Buchstaben, Linienstreifen, Flächen); liest man einen Vertex
  daneben, sind sie Splitter quer über die Karte;
- fast alle Batches nennen Texturen in ihrem Ende: eine Farbkarte (`_cv`) mit einer Deckkraftkarte (`_op`,
  roter Kanal), oder bei Markierungen eine Kanalmaske (`_rgb`).

Nach den Textur-GUIDs trägt das Ende die Materialparameter des Batches, so kodiert, wie es ein Shader-Block
tut (siehe Tönungen unten). Die Farbe einer Markierung, einer Reifenspur oder einer Linie ist der Float3-Wert
mit Hash `607e`: ein sandiges 0,64, 0,56, 0,48 für Reifenspuren im Sand, nahezu Schwarz für Teer.
Deckkraftkarten sind meist Format 62, ein Kanal mit 8 Byte je Block, als BC4 gelesen.

Ein Batch bildet seine Textur entweder nach Weltposition ab (u = x, v = z, die Textur wiederholt sich alle
Kachelmeter: Asphalt, Beton, Kies) oder 0 bis 1 über das Decal (eine Linie, ein Buchstabe, eine Reifenspur).
Datensätze werden in Dateireihenfolge gezeichnet.

**Das Einbacken.** `level --ground-texture M` malt unter der Ausdehnung der Decals und in Kacheln von
höchstens 4.096 Pixeln die Hintergrund-Farbkarte (bilinear) und dann jeden Batch darüber, nach seiner
Deckkraft mal dem Alpha des Vertex. Die Farbe der Vertices wird nicht benutzt: manche Vertices von Batches sind
reines Grün oder Blau, was die Markierungen eines Levels in diesen Farben färbte. Die Höhenfeld-Dreiecke dort
werden zu `ground:terrain x<x> z<z>`-Teilen, die die Kachel tragen. Jeder Batch zeichnet mit:

| Batch-Namen | Gezeichnet als |
|---|---|
| eine Farbkarte (`_cv`) | die Karte, nach ihrer Deckkraftkarte |
| eine Multiplikationskarte (`_mult`) und eine Deckkraftkarte | die Farbe (weiß, wo das Material keine nennt) mal die Multiplikationskarte, nach der Deckkraftkarte: die abgenutzte Mittellinie einer Landebahn, die Randlinien und die Schwellenbalken |
| eine Kanalmaske (`_rgb`) | die Farbe, sonst weiß für Linien und Buchstaben, dunkel für Umrisse, eine schwache Abdunklung für Verschleiß, Reifenspuren, Flecken, Pfützen und Nässe, nach der Maske |
| eine Deckkraftkarte allein, mit einer Farbe | die Farbe nach der Deckkraftkarte: Reifenspuren |

Eine Variationsmaske der Straße ist keine Farbe, sondern verändert die Oberfläche darunter, über Hunderte
Meter, und wird nicht gezeichnet, egal welche Farbe sie hat: als Weiß gemalt, legte sie zwei blasse Rechtecke
von 150 bis 250 m Länge an die Hänge eines Levels. Die `_mult`-Karte wird als eigene Abnutzung der Farbe
genommen, nicht als Abdunklung des Bodens darunter: sie ist nahezu weiß, und die Form der Linie steht in der
Deckkraftkarte.

Fast jeder Batch wird in wenige Kacheln mit 0,5 m pro Pixel gezeichnet; der Export wächst um einige MB und
braucht einige Sekunden mehr. Von oben gesehen liegen die Vorfelder, Rollwege und das Straßennetz unter den
Zäunen und Gebäuden der Anlagen und führen zu deren Toren.

Als eigene Geometrie gezeichnet, bräuchten die Decals Alpha-Mischung, die der Schreiber nicht trägt, und ein
Versatz über einem Gelände würde mit ihm flimmern; das Einbacken hält sie in der eigenen Farbe des Bodens.

## Texturen und Materialien {#textures-and-materials}

Quelle: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Eine Texture-res (Typ `0x6BDE20BA`) ist ein 180 Byte großer Header: Typ und Pixelformat bei +8, Breite und
Höhe bei +22, Mipmap-Anzahl bei +30, die Chunk-GUID bei +40, fünfzehn Mipmap-Größen bei +56. Der Chunk ist die
Mipmap-Kette, die größte zuerst. Manche Chunks fehlen ihre größten Mipmaps, die in einem Paket mit hoher
Auflösung ausgeliefert werden, und die Länge des Chunks sagt, bei welcher Mipmap er beginnt. Der Chunk dieses
Pakets ist bei +164 benannt; er wird aus den [Ergänzungen](#which-table-is-the-level) des Levels gelesen, wenn
eine Mipmap gebraucht wird, die dem Hauptchunk fehlt, und seine Länge plus die des Hauptchunks ergibt die ganze
Kette.

| Format | Dekodiert als | Beleg |
|---|---|---|
| 67, 66 | BC7 (sRGB, linear) | eine Farbfläche eines Plastiktanks dekodiert sich so; als BC3 sind dieselben Bytes Rauschen |
| 61, 60 | BC3 | eine Kistenfläche dekodiert sauber als BC3, nicht als BC1 oder BC7 |
| 57, 56, 55 | BC1 | ein halbes Byte pro Pixel |

Das Mesh-Asset nennt keine Textur. Die Verbindung liegt in den **Shader-Block-Depots** des Levels (res-Typ
`0x73312045`, eines je Unterwelt), geschlüsselt über die acht Byte bei +0x130 im Datensatz eines Mesh-Abschnitts:

| Teil | Aufbau |
|---|---|
| Tabelle, bei 16 | (Abschnittsschlüssel u64, Deskriptor-Offset u64), bis ein Offset außerhalb der res liegt |
| Deskriptor | (Block-Offset u64, Hash u64, Blockgröße u64) |
| Block | die Shader-Parameter des Abschnitts; jede Textur ist ein 49-Byte-Datensatz: ein Byte, 16 Byte, die Partitions-GUID des Texturassets, seine Instanz-GUID |

Der Schlüssel des Kistenabschnitts taucht einmal in jedem der zehn Depots der Unterwelten auf, die ihn
platzieren, und sein Block nennt `t_mil_crate_03_cs` und `_nmt` unter den gemeinsamen Detailkarten. Ein Block
nennt jede Textur, die der Shader abtastet, und welche die Farbkarte ist, wird nicht gesagt, sondern gewählt:
eine sRGB-2D-Textur, deren Name die meisten Wörter des Materialnamens enthält (`M_ConcreteWall_01`: concrete,
wall), dann die des Meshes, dann eine, die weder Detail-, Decal- (`t_de_...`) noch Schadenskarte ist, dann die,
die die wenigsten Blöcke benutzen. Der Block eines Straßenschildes nennt seine Tafel `t_com_highwaysignage_01_cs`
und eine Decal-Bahn `t_de_com_highwaysignage_01_ca` mit einem Schild, das auf der Seite liegt; beide passen auf
die Wörter, und ohne die Decal-Regel gewann die Bahn durch Nutzung, und das Schild zeigte das Schild um ein
Viertel gedreht, über jeden Texturkoordinatensatz des Abschnitts. Signed Distance Fields (`..._sdf`), Paletten
und Kanalmasken (`_rgb`) werden nie gewählt, egal welche Wörter sie teilen (`_rgba`-Karten schon: die meisten
sind Farbe mit Alpha, und ihr Weglassen tauschte die eigenen Karten eines Strommastes und einer Treppe gegen
fremde aus): ein Vegetationsatlas des Hintergrunds `..._atlas_a_sdf`, als Farbe gezeichnet, zeigte schwarze und
weiße Sterne für Bäume, eine Palette des Hintergrundgebäudes ein Konfetti aus Farbfeldern für Wände, und
Glasbruch, durch seine Kanalmaske gezeichnet, kam cyan heraus. Ein Abschnitt, dessen einzige Kandidaten
gemeinsame Detailkarten sind, bleibt flach gefärbt.

**Paletten.** Die Hintergrundgebäude eines Levels nehmen ihre Farben aus einer Palette, 256 x 256 Texel mit
16 x 16 Farbfeldern: jeder Vertex trägt vier Byte (Verwendung `0x1E`), deren erste zwei sagen, wo in der Palette
seine Farbe liegt, x und y aus 255. `level` zeichnet einen solchen Abschnitt mit der Palette als Textur, jeder
Vertex im Mittelpunkt seines Farbfelds. So gezeichnet, kommen die Hintergrundblöcke eines Levels als Pastellwände,
Terrakotta und dunkle Fenster heraus, wo sie vorher weiß waren.

**Overlays.** Große Objekte kacheln ein Trimsheet über ihre ersten Texturkoordinaten und legen ein Overlay darüber
durch die zweiten, die zwischen 0 und 1 liegen: eine Abwicklung des ganzen Objekts. Das Overlay
(`..._overlay_cs`, mit seiner Maske `..._overlay_a`) trägt, wie das Objekt aus der Ferne aussieht, etwa die roten
Bänder und den Rost eines Öltanks; mit dem Trimsheet allein gezeichnet, kamen die Tanks eines Levels als graue
Flächen heraus. Ein Abschnitt, dessen Block ein Overlay mit seiner Maske nennt und dessen zweite Koordinaten eine
solche Abwicklung sind, wird mit dem Overlay durch sie gezeichnet (36 Abschnitte in diesem Level).

**Tönungen.** Viele Farbkarten sind grau (ihre Kanalmittel liegen innerhalb von 6 % voneinander): der Shader
bemalt sie mit Farben aus den Parametern des Blocks. Nach seinen Texturdatensätzen (je 49 Byte) listet ein Block
seine Parameter, jeder mit einem Typ-Tag (`f11af825` ein float3, `a5e1f2de` ein float4, `c1b1a014` ein float,
`4a4fc3a1` eine Ganzzahl), den Flag-Bytes `01 80` für einen Wert, einem Zwei-Byte-Hash des Parameternamens, einer
u32-Anzahl, dem Wert und einer Acht-Byte-ID. Die Namen sind nicht gespeichert. Sieben float3-Namenshashes wirken
als Tönungen: in einem Level halten drei davon in etwa 1 von 6 Blöcken eine Farbe, deren Karte grau ist, und fast
nie dort, wo die Karte eigene Farbe hat; die anderen halten die Farben, mit denen eine graue Karte bemalt wird,
wenn der Name des Materials es sagt (der `..._blue`-Streifen einer Brücke: 0,047, 0,098, 0,171 gegen ein neutrales
0,5). Eine Familie kann mehrere Werte haben, einen je Kanal einer Maske, die meisten davon neutral, und ein Wert
mit einem Kanal nahe null (reines Grün auf Backsteinfassaden) wählt einen Kanal der Maske aus, statt zu färben.
`level` multipliziert eine graue Farbkarte im linearen Licht mit dem ersten Wert jeder Familie, der weder neutral
noch ein solcher Wähler ist, über ihren neutralen Wert, und behält das Ergebnis als eigene Textur; eine Karte mit
Farbe bleibt, wie sie ist. Die Regel ist die des Exporters: welcher Kanal einer Maske welche Tönung bekommt, wird
nicht gelesen. In einem Level senkte sie den Anteil der Strukturdreiecke, die nahe Weiß gezeichnet sind, von 19,4 %
auf 3,9 %.

**Objektvarianten.** Ein Mesh wird in mehreren Erscheinungen platziert: eine Lagerhauswand mit rotem oder blauem
Streifen und einer anderen Nummer darauf, ein Container in Grün oder Grau. Jede platzierte Kopie nennt ihre
Erscheinung:

| Wo | Feld |
|---|---|
| Mitglied einer statischen Modellgruppe | +32: ein Array aus einem Zeiger je Kopie, auf eine Objektvariante oder null |
| Objektverweis | +120: ein Zeiger auf eine Objektvariante oder null |
| Objektvariante (Partition `ov_...`, Typ `235f2a9c...`) | ihre erste Instanz +32: der u32-Namenshash der Variante |

Die Erscheinung eines Abschnitts in einer Variante ist der Shader-Block, der unter dem eigenen Schlüssel des
Abschnitts steht, wobei der Variantenhash zu seinen ersten vier Byte als little-endian-u32 addiert wird
(`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); ein Abschnitt ohne Block unter diesem Schlüssel sieht
in jeder Variante gleich aus. Die Mesh-Variantendatenbanken des Levels (`meshvariationdb_win32`) listen je Mesh
und Variantenhash die Materialien, die jede Variante berührt, aber nicht die Schlüssel: die Regel wurde aus den
Schlüsseln selbst gefunden und gilt für jeden geprüften Abschnitt mit Varianten (die vier Varianten einer Wand,
je drei ihrer Abschnitte). Der Block einer Variante bringt eigene Texturen mit, nicht nur Tönungen: die gemalte
Nummer auf der Wand ist ein Buchstabenblatt, das der Block der Variante nennt. Ein großer Teil der gruppierten
Kopien wird in einer Variante platziert.

Ein Block wird einmal je Inhaltssatz gebacken, und der Eintrag des Depots für einen Schlüssel trägt einen Hash
davon (das zweite u64 des Eintrags). Hat ein Abschnitt keinen Block unter dem Schlüssel seiner Variante, erreicht
die Variante ihn trotzdem über einen *Zwilling*: einen anderen Abschnitt, dessen Standardblock denselben Inhalt
hat und einen Block unter diesem Schlüssel besitzt. Ohne Zwillinge kann eine Wand, deren Längen sich einen
Standardblock teilen, in zwei Farben erscheinen. Ein Abschnitt ohne eigene Variante nimmt die Variante, die die
meisten seiner Zwillinge haben.

**Zerstörbare Meshes.** Ein Mesh, das ein Match niederreißen kann, hat ein Zerstörungs-Asset gleichen Namens
daneben (`.../br_x.destruction` für `.../br_x_mesh`): die zerbrechlichen Gebäude und Mauern (`br_`) und viele
Requisiten. `level` behält ihre Oberflächen in eigenen Teilen, benannt mit ` (destructible)`, deren
glTF-Nodes `{"destructible": true}` tragen. Ihre zerstörten Zustände sind die Meshes `dc_..._part<N>_mesh` daneben,
jeweils um ihren eigenen Ursprung zentriert; wo ein Teil sitzt, steht im Zerstörungs-Asset, das nicht gelesen
wird, daher werden die zerstörten Zustände nicht exportiert.

**Weggelassen.** Abschnitte mit Platzhalter-Blockout-Materialien (`M_Whitebox`: wenige große, unbemalte Dreiecke,
die manche Gebäude neben ihren Flächen halten und die in einem Level als weiße Flossen herausstanden), Meshes für
Zwischensequenzen (ein Hubschrauber, der dort steht, wo seine Szene beginnt) und Beleuchtungshilfen (Ebenen, die
Licht blockieren, nie gezeichnet). Die generierten Hintergrundgebäude eines Levels
(`..._generated_blueprints_..._mesh`) werden gezeichnet, aber ihre Wandmaterialien nennen nur Rauschkarten, und
ihre Vertices tragen keine Farbe, daher bleiben sie einfach. Fast jeder gezeichnete Abschnitt bekommt eine
Farbkarte.

**Buchstabenblätter.** Eine gemalte Nummer an einer Wand oder das Plakat eines Krans ist ein eigener Abschnitt,
dessen Farbkarte ein Blatt (`_ca`) ist: das Alpha eines Buchstabens über einer festen Farbe, oder ein Druck. Seine
ersten Texturkoordinaten kacheln den Putz der Wand über die Tafel (u -0,2 bis 1,7 an einer Wand), was das Blatt
fast zweimal zeichnet; der vierte Satz (`0x24`, sonst der dritte, `0x23`) legt es genau einmal auf (u -1 bis 0,
v 1 bis 2, wenige Tausendstel darüber in den gröberen Detailstufen der größeren Level). Wo der erste Satz eine
Kopie des Bildes lässt und der vierte oder dritte innerhalb einer liegt, wird das Blatt durch diesen gezeichnet,
in 0 bis 1 verschoben. Ein Blatt mit Alpha wird 1 cm vor der Fläche gezeichnet, auf die es gemalt ist, die darunter
in der anderen Farbkarte des Blocks durch den ersten Satz gezeichnet wird: ohne das zeigten die leeren Texel des
Blattes das Innere der Wand. Der zweite Satz ist die Abwicklung eines Objekts für sein Overlay und wird hier nicht
benutzt.

**Ausschneidekarten.** Der vierte Kanal der Farbkarte bedeutet je nach Name etwas anderes. In `_cs`, bei weitem am
häufigsten (893 der gewählten Karten eines Levels), ist er Glätte: 1 % des Alphas einer mittleren Karte liegt
innerhalb von 0,1 von 0 oder 1. In `_cu` (Blätter, Gras) und `_ca` (Farbe und Alpha) ist er Deckkraft: 90 % und
87 %. Eine Farbkarte mit dem Namen `..._cu` oder `..._ca`, deren Alpha zu mindestens 75 % nahe 0 oder 1 liegt, zu
mindestens 1 % unter 0,5 und zu mindestens 5 % über 0,5, wird mit ihrem Alpha als PNG geschrieben, und ihr
Material als glTF `alphaMode` MASK, `alphaCutoff` 0,5, beidseitig; Blattkarten zeigen dann Blätter statt ihrer
schwarzen Ecken. Die Blattkarte eines Baumes hat gar kein Alpha (höchstens 4 von 255): seine Wedel werden durch
Geometrie geschnitten, und mit nur den ersten beiden Bedingungen wurde die ganze Krone weggeschnitten.

Texturkoordinaten sind die Vertex-Verwendung `0x21`, zwei Halbwerte (Format 6) oder zwei Floats (Format 2).
Abschnitte tragen bis zu drei weitere Sätze (`0x22` bis `0x24`) für Decal- und Detailschichten. Die Koordinaten
kacheln: die geriffelte Seite eines Containers läuft von -1,6 bis 1,8, die Kacheln der Hintergrund-Geländeteile
liegen ganz außerhalb von 0..1, und in einem Level liegen 23 % der texturierten Dreiecke außerhalb von 0..1. Sie
werden so geschrieben, wie sie sind, mit einem sich wiederholenden Sampler; der 3DHeat-Viewer packt jede sich
wiederholende Textur in seinen Atlas ein. Ein Renderer, der sie stattdessen klemmt, verschmiert die Rippen auf die
doppelte Breite, macht aus einem Betonboden Schlieren entlang einer Achse und gibt den Stahlträgern eines Turms
die Randfarbe ihrer Textur; für ihn schneidet `--clamped-uvs` jedes Dreieck entlang der Linien, an denen sich seine
Textur wiederholt, und verschiebt jedes Stück nach 0..1 (siehe [Ausgabeformat](output-format.md)). Danach liegen
0,03 % der texturierten Dreiecke, über die sich eine Textur mehr als 16-mal wiederholt, außerhalb, und ein Dreieck,
das das Schneiden in mehr als 4 Stücke zerlegen würde, wird in der durchschnittlichen Farbe seiner Textur gezeichnet:
Rinde wiederholt sich an jedem Ast, und geschnitten wuchsen die Bäume eines Levels von 6,4 auf 24 Millionen
Dreiecke.

Das Höhenfeld hat keine eigene Farbkarte, die sich lesen ließe. Wo eine der Farbkarten des Hintergrunds es
abdeckt, wird es daraus gefärbt: die Texturkoordinaten des Hintergrunds sind eine lineare Funktion von Welt-x und
-z (99 % seiner Vertices innerhalb von 0,001 davon; die Karte deckt ein Quadrat von 65.536 m, um ein Viertel
gedreht), und dieselbe Funktion liefert die des Höhenfeldes. Das Level liefert die Mipmaps dieser Karte ab 2.048 px
abwärts aus, daher bekommt das Höhenfeld 32 m pro Pixel. Sein dunkler Fels liegt am steilen Boden: die Korrelation
von Dunkelheit und Hang ist 0,48, und höchstens 0,34 für die sieben anderen Ausrichtungen.

Der Hintergrund eines anderen Levels sind acht nahe und acht ferne Kacheln rund um das Spielgebiet, jede wiederholt
ihre eigene Textur über die Kachel, und keine erreicht das Höhenfeld. Jede Hintergrundtextur wird für sich
angepasst, und wenn keine das Höhenfeld abdeckt, nimmt sie die durchschnittliche Farbe, die der Hintergrund innerhalb
eines Kilometers um das Geländequadrat zeigt, womit `--ground-texture` die Decals darüber einbackt. Ein
Hintergrundmaterial ist eines, dessen Name `TerrainBackdrop` enthält oder `BD_` und `Terrain` (`M_BD_<site>_Terrain..._Near`);
oder ein Hintergrundmesh (`bd_..._terrain<site>_04_far_mesh`) trägt ein schlichtes Geländematerial
(`M_<region>_Terrain<site>_04_Far`), das die ersten beiden Regeln in einem Level übersahen und daher seinen Boden
aus seinen Oberflächen färbte.

Wo aber keine Hintergrundkarte das Höhenfeld abdeckt, nimmt es die mittlere Farbe der eigenen Oberflächen des
Geländes, noch vor dem Durchschnitt des Hintergrunds: die `_cv`-Farbkarten, die die Shader-Blöcke des
Layer-Graphen nennen (27 in einem Level: Sande, Kiese, Böden, Gras, rissiger Beton), jede gemittelt, dann der
Median jedes Kanals, ohne die Standardoberfläche der Engine. Ein Hintergrund kann eine ganz andere Landschaft
sein: in einem Level ließ sein Durchschnitt (95, 99, 80 in sRGB) den Boden des Spielgebiets in einem Grau
erscheinen, das das Spiel nicht zeigt. Mit `--ground-texture` wird diese Farbe mit dem Doppelten der Farbkarte
multipliziert, was Mittelgrau unverändert lässt, und zusammen mit den Decals über die Ausdehnung der Decals und
der Farbkarte eingebacken.

Gegen das Spiel gemessen, die mittlere Bodenfarbe des eingebackenen Spielgebiets jedes Levels und von
Spielbildern (Zeilen 55 bis 72 % des Bildes neben dem HUD, je 24 Bilder; sRGB; die Bilder sind beleuchtet und
abgestimmt, daher sind die Verhältnisse r/g und b/g der faire Vergleich):

| Level | Bilder | Durchschnitt des Hintergrunds | Jetzt |
|---|---|---|---|
| erstes | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| zweites | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| drittes | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Das erste ist richtiggestellt; die anderen beiden lagen vorher im Farbton etwas näher. Eine Farbe für ein ganzes
Level kann nicht überall stimmen; die Masken würden es.

## Navigationsnetz {#navigation-mesh}

Quelle: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Ein Level liefert eine Partition je Agent aus, `<level>/dbt/<level>_navmesh_layer_<n>`: in einem Level ist Layer 0
der Soldat (1,8 m hoch, 0,18 m Stufe, 0,4 m Radius), und zwei andere sind Fahrzeuge (3,5 und 10 m hoch). Jede
Partition hält zwei Arrays:

| Array | Element |
|---|---|
| tiles | 28 Byte: u32 0, u32 Hash, u32 0, u32 Chunk-Index, u16 Kachel x, u16 Kachel z, u32 Offset, u32 Größe |
| chunks | 20 Byte: die GUID des Chunks, u32 Größe |

Eine Kachel sind `size` Byte bei `offset` im Chunk `chunk index`, little-endian, und angelegt wie Detour (Recast
Navigation) hinter einem längeren Header:

| Offset | Inhalt |
|---|---|
| 0 | `VAND`, Version 7 |
| 24 | Zähler: Polygone, Vertices, Verbindungen, Detail-Meshes, Detail-Vertices, Detail-Dreiecke, Begrenzungsvolumen-Knoten, Off-Mesh-Verbindungen, das erste Off-Mesh-Polygon |
| 188 | Agenthöhe, Stufe, Radius |
| 200 | die Begrenzungsbox der Kachel, sechs Floats |
| 232 | Vertices: x-, y-, z-Floats, Weltkoordinaten |
| nächste 8-Byte-Grenze | Polygone, 32 Byte: u32, sechs u16 Vertex-Indizes, sechs u16 Nachbarn, u16 Flags, die Vertexanzahl bei +30, bei +31 die Fläche (untere sechs Bit) und Art (obere zwei) |
| dann gepackt | Verbindungen (16 Byte), Detail-Meshes (12: erster Detail-Vertex u32, erstes Detail-Dreieck u32, Vertex- und Dreiecksanzahl u8), Detail-Vertices (drei Floats), Detail-Dreiecke (drei Indizes und Flags), Begrenzungsvolumen-Knoten (16), Off-Mesh-Verbindungen (80) |

In jeder Kachel der geprüften Level ergeben diese bis aufs Byte die Größe der Kachel, und die Detail-Meshes
nummerieren die Polygone vor dem ersten Off-Mesh-Polygon.

Ein Polygon ist zwischen seinen Ecken flach; sein **Detail-Mesh** hält die wirkliche Höhe der Fläche über Unebenheiten,
Felsen und Stufen, und das wird gezeichnet. Ein Index eines Detail-Dreiecks unterhalb der Eckenanzahl des Polygons
ist diese Ecke, sonst Detail-Vertex `first + index - corners`. Fächerförmig aus den Polygonen zu machen legt viel mehr
Dreiecke unter das Gelände und macht lange Splitter; mit den Detail-Meshes ist keines länger als die Diagonale einer
16-m-Kachel plus die Stufe einen Hang hinauf.

Art 0 ist Boden, Art 2 kleine steile Flecken (etwa 45 Grad, je einen Quadratmeter), Art 1 eine Verbindung zwischen
Flächen: ihre Ecken spannen 125 m Höhe oder mehr und liegen außerhalb der Kachel, einige am Ursprung. Verbindungen
werden weggelassen; die übrigen werden durch ihre Detail-Meshes gezeichnet oder in einer Kachel ohne sie gefächert.

Prüfungen: die Größen der Chunks ergeben genau die der Kacheln; jeder Oberflächen-Vertex liegt innerhalb der Box
seiner Kachel, bis auf etwa einen Meter; fast alle Dreiecke zeigen nach oben. Eine Kachel, die scheitert, wird
abgelehnt und gezählt, und in diesem Level wird keine abgelehnt.

Was das Netz des Soldaten im geprüften Level von oben abdeckt: der Boden, Böden, Treppen und einige Dächer, und
nicht die Oberseiten der Frachtcontainer. Es ist die KI-Karte, wo ein Soldat stehen kann, das Nächste, was die
Dateien an die Stellen herankommen, wo Spieler stehen.

## Nicht implementiert {#not-implemented}

- Der Layer-Graph des Geländes, der seine Oberflächenschichten mischt (siehe
  [Gelände-Layer](#terrain-layers)): die Bodenfarbe folgt einer eigenen Regel dieses Lesers aus den Masken der
  Layer und der Hangneigung des Höhenfeldes, und Level, deren Maskenseiten nicht zusammenpassen, erhalten eine
  Farbe.
- Farbparameter von Decal-Materialien: Markierungen durch Kanalmasken werden in neutraler Farbe gemalt.
- Objekt-Blueprints, die keine Meshes sind (Spiellogik, Effekte, Sounds).
- Zerstörte Zustände zerstörbarer Meshes: ihre Teilpositionen stehen im Zerstörungs-Asset, das nicht gelesen wird.
- Die Verbindungen des Navigationsnetzes (Sprünge, Leitern, Übersteigen) und seine Fahrzeug-Layer.
- Mesh-Stufen, die inline in der res gespeichert sind (10 Meshes in einem Level, Gadgets), Skelett- und
  zusammengesetzte Meshes mit ihren Knochen und Teilen, und Normalen (vom Schreiber berechnet).
- Normal-, Rauheits- und andere Karten; Alpha außer einem Ausschnitt (durchsichtiges Glas und Decals werden
  undurchsichtig gezeichnet).
- Terrain-Löcher: ein Oberflächenshader für Löcher ist genannt, aber was er liest, ist nicht gefunden (siehe
  [Gelände-Layer](#terrain-layers)), daher wird das Höhenfeld dort nicht ausgeschnitten, wo der begehbare Boden darunter
  verläuft.
- Welche Tönung zu welchem Kanal der Maske eines Materials gehört: eine graue Farbkarte nimmt die erste Tönung,
  die nicht neutral ist (siehe [Texturen und Materialien](#textures-and-materials)).
- Effekte (Pfade `fx/`) und die Kabel-Meshes, deren Begrenzungsboxen zig Kilometer lang sind; sie werden weggelassen
  und in der Zusammenfassung gezählt.
- Die XOR-verschleierte Form der Tabelle.
