---
title: Assetto Corsa Rally
nav_order: 3
lang: "de"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Streckenexport: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally basiert auf Unreal Engine 5 (5.6.1, eine veränderte Version)
und liefert seine Inhalte als IoStore-Container aus. Keiner davon ist
verschlüsselt. Der Export findet die Etappe und die Achsenausrichtung aus der
Runde. Er schreibt die eigenen Bodenkacheln der Etappe, aufgeteilt in Fahrbahn
und Gelände und mit der eingebackenen Bodenfarbe der Etappe als Textur, und setzt
die übrigen Modelle nach Kategorie in einfarbigen Flächen.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Quellen: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (Installation, Etappen, Platzierung),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (der Export).
Die darunterliegenden Unreal-Leser stehen unter [Unreal 5 IoStore](reader-unreal-iostore.md),
die Dekomprimierung unter [Oodle](reader-oodle.md).

**Status:** Geprüft an der installierten Version des Spiels, mit Runden, die auf
jeder Etappe an einem zufälligen Frame erzeugt wurden. Dabei wurden jedes Mal die
richtige Etappe und der richtige Frame gefunden. Eine Runde, die im Spiel selbst
aufgezeichnet wurde, ist noch nicht durch den Export gelaufen.

## Die Installation finden {#finding-the-install}

- `--install <Ordner>`: der Spielordner, sein `Content\Paks` oder ein beliebiger
  Ordner mit `.utoc`-Dateien. Das Tool prüft `<Ordner>`, dann
  `<Ordner>\acr\Content\Paks`, dann `<Ordner>\Content\Paks`.
- Sonst wird in jeder Steam-Bibliothek `steamapps\common\Assetto Corsa Rally`
  auf dieselbe Weise geprüft.
- Jede `.utoc` in diesem Ordner wird als ein Speicher geöffnet. Container, die
  sich nicht öffnen lassen, werden übersprungen. Lässt sich keiner öffnen:
  "no readable IoStore containers in ...".

Die meisten Blöcke sind mit Oodle komprimiert, und eine Bibliothek dafür wird auf
dem Rechner gesucht (jede Steam-Bibliothek wird durchsucht). Siehe [Oodle](reader-oodle.md).

Das Spiel gilt als AC Rally, wenn die Rundendatei `"game": "assetto-corsa-rally"`
(oder `acrally`) angibt oder wenn du `--game acrally` übergibst.

## Was eine Etappe ist {#what-a-stage-is}

Eine Etappe ist eine **World-Partition-Karte**:

- `Content\Levels\<Stage>.umap` platziert das ferne Gelände.
- Aufbereitete Zellen unter `Content\Levels\<Stage>\_Generated_\*.umap` platzieren
  alles Übrige.

Eine Ebene gilt als Etappe, wenn ihr Umgebungsordner `Content\Environments\<Stage>\`
einen Ordner `MeshesTrack` hat. Das Tool richtet sich nicht nach den Namen der
Kacheln, denn eine Etappe kann ihre Kacheln nach einer Stadt benennen statt nach
ihrer Karte. `--level` wird ohne Beachtung von Groß- und Kleinschreibung mit diesen
Kartennamen verglichen. Ein falscher Name listet die vorhandenen Etappen auf.

Es gibt **kein Landschaftsobjekt**. Der Boden besteht aus statischen Meshes:

| Kacheln | Pfad | Werden zu |
|---|---|---|
| Streckenkacheln, etwa 175 m, je in zwei Teile geteilt | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` und `..._Terrain_k` | `ground:road` und `ground:terrain` (eine ungeteilte Streckenkachel, etwa ein gefrorener See, ist durchweg Fahrbahn) |
| fernes Gelände, Kacheln zu 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Die Platzierungen lesen {#reading-the-placements}

Was ein Mesh platziert, ist eine `StaticMeshComponent`: ihr `StaticMesh` sowie ihre
`RelativeLocation`, `RelativeRotation` und `RelativeScale3D`, jeweils relativ zu
der Komponente, an der sie hängt (`AttachParent`), bis hinauf zur Wurzel des Akteurs,
die in der Welt liegt.

- Die Eigenschaften sind **ohne Versionsangabe**: Sie sind nach ihrer Position in
  der Eigenschaftsliste der Klasse gespeichert, nicht nach Namen. Gelesen werden
  sie mit den Schemata in
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (siehe [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Ein Wert, der dem Template der Komponente entspricht (ihrem Archetyp in einem
  Blueprint), wird nicht gespeichert. Deshalb werden zuerst die Werte des Templates
  gelesen, rekursiv, und die eigenen Werte der Komponente überschreiben sie.
- Komponenten mit `bVisible = 0` oder `bHiddenInGame = 1` werden übersprungen. Ebenso
  Meshes, deren Pfad `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/`
  oder `_hlod` enthält.
- Drehungen verwenden Unreals `FRotationMatrix` (Pitch, Yaw, Roll in Grad).
- Doppelte Platzierungen (dasselbe Mesh mit derselben Transformation, auf 0,1 cm
  genau) werden entfernt.
- Komponenten, die nicht gelesen werden können, werden nach Grund gezählt und
  gemeldet, zum Beispiel
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instanzierte Komponenten** (Wälder, fast alle) werden nur mit `--trees` gelesen.
Dieser Build hat diese Klassen über die Header der Engine hinaus umgebaut, deshalb
werden ihre Eigenschaften nicht gelesen. Stattdessen gilt:

- Das Mesh kommt aus der Abhängigkeitstabelle des Pakets. Dort listet jede solche
  Komponente genau ein statisches Mesh.
- Die Instanzen kommen aus dem nativen Block nach den Eigenschaften
  (`[1][1][128][count]`, danach `count` 4x4-Matrizen aus Doubles).
- Die Komponente gilt als an der Wurzel ihres Akteurs sitzend, so wie die
  Vegetationsakteure sie platzieren.

Die Koordinaten sind Unreals: Zentimeter, Z nach oben, X nach vorn, Y nach rechts,
ein linkshändiges System.

## Welche Etappe und welche Richtung {#which-stage-and-which-way-round}

Das Bezugssystem der Telemetrie ist nicht dokumentiert, deshalb wird es nicht
angenommen. Es wird angepasst:

- **Acht Kandidaten-Ausrichtungen.** Unreal-Z (cm) mal 0,01 wird zur Höhe der
  Runde (y). Unreal-X und -Y werden zu x und z der Runde, vertauscht oder nicht,
  jeweils mit einem der beiden Vorzeichen, alles mit 0,01 auf Meter skaliert.
- **Ein Gitter der Fahrbahnhöhen.** Für jede Etappe wird jede Fahrbahnkachel
  platziert (in ihrer gröbsten Detailstufe), und der höchste Fahrbahnpunkt wird je
  2-m-Zelle behalten.
- **Bewertung.** Bis zu 400 Punkte der Runde, gleichmäßig verteilt, werden über
  jede Ausrichtung in den Unreal-Raum übertragen. Ein Punkt liegt auf der Fahrbahn,
  wenn unter den 3 x 3 Zellen um ihn die Fahrbahnhöhe, die ihm am nächsten liegt,
  zwischen 1 m unter und 3 m über dem Punkt liegt (`ON_ROAD`). Die Wertung ist der
  Anteil der Punkte auf der Fahrbahn.
- **Sieger.** Die beste Ausrichtung auf der besten Etappe, sofern sie mindestens
  50 % erreicht. Sonst bricht der Export ab: "the lap does not lie on any stage's
  road in any frame (best: ...). Name the stage with --level."
- **Eine Runde, die ihre Strecke nennt.** Hat die Rundendatei ein Feld `track`, wird
  zuerst eine Etappe probiert, deren Name ungefähr dazu passt (nur Buchstaben und
  Ziffern, eines enthält das andere). Sie allein wird geprüft und nur akzeptiert,
  wenn sie mindestens 80 % erreicht. Sonst wird jede Etappe probiert.
- Mit `--level` wird nur diese Etappe probiert, in allen acht Ausrichtungen.

Die Konsole meldet zum Beispiel
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Danach wird alles **im Bezugssystem der Runde** geschrieben: Meter, Y nach oben. Die
Windungsrichtung eines Dreiecks wird umgekehrt, wo eine Transformation spiegelt,
damit die Flächen weiterhin in die richtige Richtung zeigen.

## Der Boden {#the-ground}

- Der Korridor ist `--margin` Meter um die Runde in deren eigener x/z-Ebene.
- Jede Bodenkachel wird in ihrer feinsten Detailstufe platziert, und nur Dreiecke,
  die in den Korridor reichen, werden behalten.
- Dreiecke werden nach Art (Fahrbahn oder Gelände) und nach 512-m-Quadraten im
  Unreal-Raum gruppiert (51.200 cm), jedes Quadrat mit eigenem Bild. Die Teile
  heißen zum Beispiel `ground:road 1_-4`. Die UVs sind
  `(unreal_xy - square_origin) / 51200`.
- Normalen werden aus den Dreiecken für die ganze Datei berechnet.

### Die Bodentextur {#the-ground-texture}

Sofern nicht `--no-textures` gesetzt ist, wird jedes Quadrat aus zwei Quellen
gemalt, mit `--texture-size` Pixeln:

1. **Die eingebackene Bodenfarbe.** Die `RuntimeVirtualTextureComponent` der
   Etappenkarte (ihre Box ist `RelativeLocation` als Ecke und `RelativeScale3D` als
   Größe, ohne Drehung) zeigt auf eine gestreamte **Virtual Textur**, die Bodenfarbe,
   die das Spiel eingebacken hat. Der Bereich des Quadrats wird daraus gelesen, auf
   der Stufe, deren Pixel der gewünschten Größe am nächsten kommen. Das sind je nach
   Etappe 13 bis 59 cm pro Pixel.
2. **Das Satellitenbild** füllt, was die Virtual Textur schwarz lässt. Es ist die
   Textur `sat*_(b|bc|c|basecolor)` der Etappe in ihrem Umgebungsordner, gelesen
   mit bis zu 4096 px. Seine Lage wird über eine Least-Squares-Anpassung der ersten
   UV-Gruppe des fernen Geländes an die Welt-x- und -y-Werte gefunden. Die Anpassung
   muss im 95. Perzentil auf 0,01 linear sein, sonst wird das Bild nicht verwendet.
   Laufen die UVs des fernen Geländes über 1 hinaus (ein Material, das sie
   wiederholt), wird die Abbildung halbiert, bis sie einmal passen.

Die Konsole sagt, was verwendet wurde, zum Beispiel
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Eine Etappe ohne beides wird in einfarbigen Flächen gezeichnet.

## Platzierte Modelle {#placed-models}

Jede Platzierung, die kein Bodenteil ist, wird nach ihrem Meshpfad eingeordnet
(der erste Treffer gilt):

| Kategorie | Der Meshname (oder bei Bäumen der Pfad) enthält |
|---|---|
| Bäume (nur mit `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| Felsen | `rock`, `cliff`, `boulder`, `stone` |
| Randsteine | `kerb`, `curb` |
| Absperrungen | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| Schilder | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| Gebäude | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| Infrastruktur | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| Requisiten | alles Übrige |

- Eine Kopie wird berücksichtigt, wenn ihr Ursprung im Reichweitenkorridor liegt
  (`margin + 60 m`), und gezeichnet, wenn ihre Ausdehnung den Korridor berührt.
- Die Detailstufen folgen [Detailstufen und Budget](detail-budget.md): Entfernungsbänder,
  dann werden die teuersten Modelle auf eine gröbere Stufe gesetzt, bis es ins Budget
  passt. Reicht selbst die gröbste Stufe nicht, werden die am weitesten entfernten
  Kopien weggelassen, wie bei BeamNG, bis es passt. Randsteine behalten volle
  Detailstufe und werden nie weggelassen. Die Zusammenfassung zeigt
  `placed on it (N triangles of a B budget)` und, wenn Kopien fehlen,
  `N copies left out to fit the budget, the furthest from the driving first`.
- Jede Kategorie ist ein Teil in einer einfarbigen Fläche: `ground:kerbs` für
  Randsteine, die wie bei Forza und BeamNG zur Fahrfläche gehören, und
  `structure:<category>` für den Rest:

| Kategorie | Farbe (lineares RGB) |
|---|---|
| Absperrungen | 0,55, 0,52, 0,48 |
| Schilder | 0,75, 0,72, 0,65 |
| Gebäude | 0,62, 0,58, 0,52 |
| Infrastruktur | 0,48, 0,48, 0,50 |
| Felsen | 0,45, 0,43, 0,40 |
| Requisiten | 0,55, 0,45, 0,35 |
| Bäume | 0,20, 0,32, 0,14 |
| Randsteine | 0,70, 0,25, 0,22 |

Statische Meshes, die nicht gelesen werden können (Skinning-Meshes, Meshes nur mit
Nanite, Level, die nicht inline gespeichert sind), werden gezählt:
`N meshes could not be read`.

## Was geprüft wurde {#checks-behind-it}

Laut Quelltext, am installierten Spiel:

- Jede Inhaltstabelle wird gelesen (Version 8).
- Jede Zelle jeder Etappe öffnet sich, und jede statische Mesh- und
  Szenenkomponente wird vollständig dekodiert und endet genau am nativen Ende ihrer
  Klasse.
- Fast jedes stichprobenweise geprüfte statische Mesh wird dekodiert (der Rest sind
  Skinning-Meshes). Die dekodierte Ausdehnung einer Fahrbahnkachel stimmt mit ihrer
  gespeicherten Box überein.
- Die Mip-Stufen eines Satellitenbildes entsprechen genau den Größen seiner
  Bulk-Einträge.
- Die Kacheln eines Virtual-Textur-Chunks sind bis aufs Byte erfasst, und die
  Fahrbahnkacheln liegen auf der Fahrbahn, die sie zeigt.

## Bekannte Lücken {#known-gaps}

- Die Eigenschaften instanzierter Komponenten werden nicht gelesen (siehe oben).
  Ihre Platzierung nimmt die Akteurwurzel an.
- Wälder, die PCG zur Laufzeit erzeugt, sind nicht in den Dateien gespeichert und
  können nicht exportiert werden.
- Spline-Meshes (unsichtbare Respawn-Wände), Decal-Komponenten und die eigenen
  Texturen platzierter Modelle werden nicht gezeichnet. Die Modelle sind einfarbig.
- `--season` hat keine Wirkung.
- Ein Patch des Spiels kann Eigenschaftsplätze verschieben. Der Leser bricht dann
  ab, statt falsch zu lesen, und die Strecke meldet, wie viele Komponenten fehlschlugen.
