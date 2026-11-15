---
title: "BeamNG.drive"
nav_order: 2
lang: de
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Streckenexport: BeamNG.drive {#course-export-beamngdrive}

Der BeamNG-Export liest ein Level so, wie das Spiel es einbindet, und schreibt danach dieselbe Art
Datei wie der Forza-Export: Boden je 512-m-Quadrat mit einer eingebackenen Textur, Straße und loser
Boden als eigene Teile, platzierte Modelle nach Kategorie und Wasser.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Quellen: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (Installation, Dateisystem, Szene, Gelände, Materialien),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (der Export),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) und
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (Shapes).
Dateiformate im Detail: [BeamNG-Dateien](reader-beamng.md).

## Das Koordinatensystem der Runde {#the-laps-frame}

Der `course`-Export erwartet BeamNG-Positionen im **Koordinatensystem des Viewers**:
`(x, z, -y)` des Z-up-Welt von BeamNG, in Metern. Das ist die Drehung, die der Telemetrie-Recorder
von 3DHeat anwendet. Der Export dreht die Runde zurück in das System von BeamNG
(`(x, -z, y)`), arbeitet dort und schreibt alles wieder im System des Viewers aus. Das ist eine
Drehung, keine Spiegelung, daher kommt nichts seitenverkehrt heraus. Eine Runde, die im rohen
System von BeamNG aufgezeichnet wurde, würde nicht richtig platziert. Das ist mit anderen Recordern
nicht getestet.

Das Spiel gilt als BeamNG, wenn die `heat3d-lap`-Datei `"game": "beamng"` sagt oder du
`--game beamng` angibst.

## Die Installation finden {#finding-the-install}

- `--install <folder>`: der Ordner, der `gameengine.zip` und `content` enthält.
- Sonst wird in jeder Steam-Bibliothek `steamapps\common\BeamNG.drive` nach diesen beiden gesucht.
- Wenn keines davon klappt: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)." (keine BeamNG.drive-Installation in den
  Steam-Bibliotheken gefunden. Nenne den Ordner mit --install, den mit gameengine.zip.)

## Das Dateisystem {#the-file-system}

BeamNG liefert einfache Zip-Archive aus und bindet sie in ein gemeinsames Dateisystem ein, auf das
Level verweisen (`/art/shapes/...`, `/assets/materials/...`). Der Export baut dasselbe: einen
Index ohne Unterschied von Groß- und Kleinschreibung über

1. `gameengine.zip`,
2. jede `*.zip` unter `content`, außer `content\vehicles\*` und Archiven, deren Namen mit
   `art_sound` oder `audio` beginnen,
3. die Inhalte des Benutzers, neueste Ebene zuerst: unter
   `%LOCALAPPDATA%\BeamNG\BeamNG.drive` und `%LOCALAPPDATA%\BeamNG.drive` der Ordner `current` und der
   höchstnummerierte Versionsordner. Aus jedem: `mods\*.zip`, jeder Ordner in `mods\unpacked` und der
   Benutzerordner selbst, wenn er einen Ordner `levels` hat.

Spätere Ergänzungen gewinnen, wie im Spiel, so ersetzt ein Mod, was er überschreibt. Mods sind bei
einem Streckenexport immer dabei.

Pfade, die ein Level nennt, werden so aufgelöst, wie das Spiel sie auflöst: zuerst wie angegeben,
dann relativ zu der Datei, die sie nannte, und für jeden auch als die `.dds`, in die eine Textur
gebacken wurde, die `.cdae`, in die eine `.dae` kompiliert wurde, oder über eine `.link`-Datei, die
auf `/assets` zeigt.

## Welches Level {#which-level}

Ohne `--level` wird jedes Level danach bewertet, wie viel der Runde auf ihm liegt:

- Bis zu 500 Rundenpunkte, gleichmäßig verteilt, werden benutzt.
- Für das `TerrainBlock` jedes Levels wird die Ausdehnung des Geländes aus den ersten fünf Bytes
  seiner `.ter`-Datei gelesen, sodass ein Level, bei dem die Runde weit weg liegt, nichts kostet.
  Liegen mindestens 30 % der Punkte innerhalb der Ausdehnung, werden die Höhen gelesen. Ein Punkt
  zählt als **auf** dem Gelände, wenn er zwischen 1 m unter und 3 m über ihm liegt (`ON_GROUND`),
  weil der Bezugspunkt eines Autos sein Karosserie ist, nicht seine Reifen.
- Erreicht kein Level 50 % oder mehr, werden die Level auch nach ihren **Straßen** bewertet. Manche
  Level laufen über ihre Höhenkarte hinaus (ihre Ränder setzen sich als Felsflächen fort). Ein Punkt
  liegt auf einer Straße, wenn er innerhalb der halben Breite der Straße plus 4 m (mindestens 6 m) von
  einem `DecalRoad`-Segment liegt und zwischen 2 m unter und 4 m über ihm.
- Das beste Level gewinnt, wenn es mindestens 30 % erreicht. Sonst hält der Export an und listet die
  besten drei: "the lap does not lie on any installed level's terrain (best: ...). Name the level
  with --level." (die Runde liegt auf keinem Gelände eines installierten Levels (am besten: ...). Nenne
  das Level mit --level.)

Die Konsole zeigt `on <level>: 87% of the lap lies on its terrain` (oder `roads`). `--level` wird ohne
Unterschied von Groß- und Kleinschreibung mit den Ordnernamen der Level verglichen.

## Das Level lesen {#reading-the-level}

Woraus ein Level besteht, jeder Teil gegen die mitgelieferten Level geprüft
(Details auf [BeamNG-Dateien](reader-beamng.md)):

- **Szene**: `levels\<name>\main\**\*.level.json` (ein JSON-Objekt pro Zeile oder ein JSON-Array) oder
  eine `.mis`-Datei für ältere Level. Das Werkzeug liest `TSStatic`-Objekte (platzierte Modelle,
  versteckte werden übersprungen), `Prefab`-Objekte (bis zu 8 Ebenen tief verschachtelt, TorqueScript
  `.prefab` oder `.prefab.json`), `DecalRoad`-Objekte (aufgemalte Straßen), `TerrainBlock`,
  `WaterPlane`, `WaterBlock` und `River`.
- **Forst-Objekte**: `levels\<name>\forest\*.forest4.json`, mit den Typen aus den Datensätzen
  `managedItemData.json`. Barrieren, Zäune und Felsen sind genauso oft Forst-Objekte wie Bäume.
- **Gelände**: das `.ter`-Höhenfeld und seine Layer-Karte.
- **Materialien**: jede `*.materials.json` außerhalb von `levels\` sowie die dieses Levels.

## Der Korridor und die Straßen-Decals {#the-corridor-and-the-road-decals}

Der Korridor ist `--margin` Meter um die Runde in der x/y-Ebene von BeamNG (siehe
[Strecken-Export](course-export.md#the-corridor)). Ein Reichweiten-Korridor von `margin + 60 m` wählt
die Kandidaten aus.

**Straßen-Decals** (`DecalRoad`) sind der Großteil der Straßen von BeamNG: auf das Gelände gemalt,
nicht modelliert. Decals, deren Ausdehnung den Reichweiten-Korridor berührt, werden in der
Zeichenreihenfolge des Spiels übernommen (absteigend `renderPriority`, dann Dateireihenfolge) und als
Bänder angelegt:

- Die Knoten (x, y, z, Breite) werden etwa alle 1 m durch einen **zentripetalen Catmull-Rom-Spline**
  interpoliert. Die uniforme Variante schleift sich an einer Haarnadelkurve zurück, wo Knoten sich
  drängen. Geschlossene Straßen werden geschlossen.
- Jede Kante nimmt die Höhe des Geländes, wo das Gelände innerhalb von 1,5 m der eigenen Höhe der
  Straße liegt, und behält sonst die Höhe der Straße (auf einer Brücke).
- Der Materialname entscheidet, was ein Decal malt:

| Art | Materialname enthält (erster Treffer gilt) |
|---|---|
| Reifenspuren | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| Auflage (nur Optik) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| Markierungen | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| lose | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| Straße | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| Auflage | alles andere |

## Der Boden {#the-ground}

Das Höhenfeld des Geländes innerhalb des Korridors wird zu Dreiecken:

- Ein Viereck pro Geländequadrat, dessen Mittelpunkt im Korridor liegt. Quadrate mit Layer 255
  (Löcher) werden übersprungen. Jedes Viereck besteht aus zwei Dreiecken, deren Diagonale so wechselt,
  wie es das Gelände von Torque tut.
- Die Höhen sind `position.z + h * maxHeight / 65535`. Die Normalen kommen aus den Höhenunterschieden.
- Jedes Quadrat wird nach seinem **Layer** eingeordnet: dem Layernamen mit seinem Geländematerial,
  dem Bodenmodell und der Annotation. Wörter für Pflaster machen es `road`,
  `grass/forest/rock/moss/leaves/cliff/stone` machen es `terrain`, lose Wörter machen es `loose`
  (Kies und Erde). Alles andere ist `terrain`.
- Dann **überschreiben Straßen- und lose Decals** die Quadrate, die sie abdecken, in der
  Zeichenreihenfolge, sodass das zuletzt gemalte Decal entscheidet.
- Die Vertices werden je 512-m-Quadrat aufgeteilt (`floor(x / 512)`, `floor(y / 512)`), damit jeder
  Teil in genau ein Bild abgebildet wird: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Die Konsole gibt bei `what the ground is made of` die Dreiecksanzahl pro Art aus.

### Gemodellte Fahrfläche {#modelled-driving-surface}

Die Rennstrecken von BeamNG sind oft ebenso Modelle wie Gelände. Die Strecke einer Rennbahn kann ein
einziges Mesh sein, mit ihren Linien, Gummispuren und Rüttelstreifen als eigenen Meshes darüber. Daher
werden platzierte Modelle der Kategorien road, kerbs, verge, props und bridges nach Fahrfläche
durchsucht. Pro Material:

| Fläche | Entschieden durch (erster Treffer) |
|---|---|
| Reifenspuren | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` im Namen, Bodentyp oder Annotation |
| Markierungen | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` im Materialnamen |
| Bordsteine | `rumble`, `kerb`, `curb` |
| Straße | Bodentyp `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, oder der Name enthält `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| lose | Bodentyp `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| Randstreifen | `sidewalk` |
| (die eigene Kategorie des Modells) | für Modelle, die schon als road, kerbs oder verge eingeordnet sind |

Von diesen Materialien werden die **nach oben zeigenden** Dreiecke (Normale z über 0,5) innerhalb des
Korridors aus dem Modell herausgenommen und werden Boden. Sie werden in die eingebackene Textur der
Kachel gemalt und als Teile geschrieben, etwa `ground:road 3_-2 asphalt_light`. Markierungen und
Reifenspuren werden nur gemalt. Die übrigen Dreiecke des Modells bleiben beim Modell. Diese Modelle
werden nie vereinfacht oder vom Budget weggelassen, denn eine grobe Strecke ist eine falsche Strecke.

## Die eingebackene Bodentextur {#the-baked-ground-texture}

Jedes 512-m-Quadrat mit Boden bekommt ein Bild mit `--texture-size` Pixeln (2048 = 25 cm pro
Pixel), so gezeichnet, wie das Spiel seinen Boden zeichnet:

1. **Gelände-Layer.** Pro Pixel werden die Layer der vier umliegenden Geländequadrate bilinear
   gemischt. Jeder Layer wird so gefärbt, wie das Spiel es tut: die **Basis-Map** des Materials, auf
   `diffuseSize` Meter gestreckt (oder über das ganze Gelände), dann die **Detail**- und
   **Makro**-Maps als graue Überlagerungen (`colour * (1 + strength * (2 * overlay - 1))`, 0,5
   neutral). Ihre Standardwerte wiederholen sich alle 2 m und 60 m, mit Stärken 0,5 und 0,3, sofern das
   Material nichts anderes sagt. Ein Layer ohne Material bekommt die flache Farbe seiner Fläche.
   Zeile 0 der Basis-Map ist Norden.
2. **Straßen-Decals**, die nur auf das Gelände gemalt sind, in Zeichenreihenfolge, jedes mit eigener
   Textur, Deckkraft-Map, Tönung und Deckkraft, entlang des Bandes. Ausgelieferte Level nutzen
   Prioritäten um 12 bis 16 für Asphaltbasen, 10 für Markierungen und 4 für Gummi.
3. **Gemodellte Fahrfläche** von oben gesehen: zuerst die Basen, dann die Auflagen, jeweils in der
   eigenen wiederholenden Textur des Modells, ein Texel pro Bake-Pixel.
4. **Decals, die auch über Objekte projiziert werden** (`overObjects`), zuletzt.

Mit `--no-textures` wird nichts eingebacken: Bodenteile bekommen flache Farben, und die gemodellten
Markierungen und Reifenspuren werden eigene Teile, um **3 cm** angehoben.

## Platzierte Modelle {#placed-models}

Kandidaten sind jedes `TSStatic`, jedes Prefab-Kind und jedes Forst-Objekt, dessen Ursprung im
Reichweiten-Korridor liegt. Ein Kandidat wird gezeichnet, wenn seine Welt-Begrenzungsbox der Form den
Korridor berührt.

**Kategorie** kommt aus der Annotation des Levels und dem Pfad der Form. Die erste Regel, die passt,
gewinnt:

| Kategorie | Annotation | Pfad oder Name enthält |
|---|---|---|
| Kulisse (wird nie gezeichnet) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| Bordsteine | | `kerb`, `curb`, `rumble` |
| Straße | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| Randstreifen | `SIDEWALK`, `COBBLESTONE` | |
| Bäume (nur mit `--trees`) | `NATURE` | tree, foliage, bush, grass, plant und ähnliche Wörter |
| Felsen | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| Barrieren | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| Schilder | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| Brücken | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| Infrastruktur | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| Gebäude | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| Requisiten | | alles andere |

**Formen** werden aus der kompilierten `.cdae` gelesen, oder aus der Collada-`.dae`, wo kein Cache
existiert (Mods). Eine Form, die sich nicht lesen lässt, wird gezählt:
`N copies of M models could not be read` (N Kopien von M Modellen konnten nicht gelesen werden).
Materialien mit dem Namen oder der Textur `invisible`, `collision` oder `nodraw` werden nie gezeichnet.

**Texturen.** Modelle werden je Kategorie und Material in Teile gruppiert, benannt
`structure:<category> <material>` (oder `ground:kerbs <material>`). Eine Gruppe bekommt die
Farbtextur ihres Materials mit höchstens **256 px**, aber nur, wenn ihre UVs innerhalb von 0 bis 1
bleiben (98 % der Vertices innerhalb von -0,02 bis 1,02). Der Viewer packt Texturen in einen Atlas und
kann keine wiederholen. Eine Gruppe, deren Textur sich wiederholt, wird in der durchschnittlichen Farbe
der Textur gezeichnet (alphagewichtet, in sRGB, multipliziert mit der Tönung des Materials), oder in
der Kategoriefarbe, wenn sie keine Textur hat.

**Detail** folgt dem gemeinsamen Schema unter
[Detailstufen und Budget](detail-budget.md). Die Detailstufen von BeamNG sind die `details` der Form
(größte Pixelgröße zuerst). Über dem Budget gehen die entferntesten Kopien zuerst. Bordsteine und
Modelle mit Fahrfläche werden nie vereinfacht oder weggelassen.

`--no-placed` lässt die Strukturen weg, behält aber die gemodellte Fahrfläche. `--trees` fügt die
Kategorie Bäume hinzu.

## Wasser {#water}

| Quelle | Gezeichnet als |
|---|---|
| `WaterPlane` (das Meer) | ein 4-m-Viereck auf Wasserhöhe für jede Korridorzelle, in der kein Gelände diese Höhe erreicht |
| `WaterBlock` | ein Viereck, das Einheitsquadrat bei lokalem z = 0 im Transformations der Box (ihre Skalierung bestimmt also die Größe), wenn es den Korridor berührt; ob z = 0 die Oberfläche der Box ist, ist nicht geprüft |
| `River` | ein Band durch seine Knoten, wenn es den Korridor berührt |

Alles Wasser ist ein flacher Teil, `water:water`.

## Nicht gezeichnet {#not-drawn}

- Bodenbewuchs (prozedurales Gras).
- Szenerie am Rand der Welt (`backdrop` und Ähnliches).
- Wiederholende Modelltexturen, die als durchschnittliche Farbe erscheinen (siehe oben).
- Skelettmeshes (Fahrzeuge, Figuren) und Decal-Meshes innerhalb von Formen.

## Prüfungen dahinter {#checks-behind-it}

Wie im Quelltext angegeben, an den ausgelieferten Leveln gemessen:

- Straßenknoten liegen mit 1 bis 2 cm (Median) auf dem Gelände, auf den geprüften Leveln, mit
  `h * maxHeight / 65535` und Zeilen entlang +y. `h / 32` oder die andere Achsenreihenfolge liegen um
  Zehner bis Hunderte Meter daneben.
- Schienenabschnitte, die entlang einer Straße verkettet sind, laufen entlang der Zeile 0 der
  `rotationMatrix` (die große Mehrheit).
- Die Knotendrehung der `.cdae` muss transponiert werden. Damit stimmen die Welt-Begrenzungen auf den
  Millimeter mit der Quell-`.dae` überein. Ohne das liegen sie im Median 38 cm daneben.
- Auf mehreren ausgelieferten Leveln aller Arten exportiert, in Sekunden bis Minuten je Level.
