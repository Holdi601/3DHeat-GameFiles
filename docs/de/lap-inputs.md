---
title: Rundeneingaben
nav_order: 7
lang: de
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Rundeneingaben {#lap-inputs}

Eine **Rundendatei** ist eine Liste von x-, y-, z-Punkten: wohin das Auto gefahren
ist. Die schnellste selbst gemachte ist die CSV unter [5. Eine `.csv`-Tabelle](#5-a-csv-table) unten.

Eine Runde sagt dem Streckenexport **wohin das Auto gefahren ist**. Alles andere darin
wird nicht verwendet: Geschwindigkeit, Eingaben und g-Kräfte gehören zur
Telemetrie-Seite von 3DHeat. Das Tool liest Positionen in den Weltmetern des Spiels,
dazu, wenn die Datei es angibt, das Spiel und die Strecke.

Quelle: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Was `course` annimmt {#what-course-accepts}

Das Format wird am Inhalt der Datei erkannt, nicht am Namen. Nur `.npz` und `.csv`
werden an der Endung erkannt. Alles andere wird als JSON versucht.

### 1. Ein `heat3d-lap`-Dokument (jedes Spiel) {#a-heat3d-lap-document-any-game}

Geschrieben von den Telemetrie-Recordern von 3DHeat (`heat3d_capture telemetry`
([3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture))):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y` und `channels.z` sind Pflicht. Zeilen, bei denen einer
  dieser Werte keine endliche Zahl ist, werden verworfen. Andere Kanäle werden ignoriert.
- `game` bestimmt den Export (siehe [Befehle](commands.md#which-game)).
- `track` verwendet Assetto Corsa Rally, um die genannte Etappe zuerst zu probieren.
- Achsen: y ist die Höhe. Forza- und AC-Rally-Runden verwenden die horizontalen
  Achsen des Spiels, so wie der Recorder sie schreibt. BeamNG-Runden werden im
  Bezugssystem des Viewers erwartet, `(x, z, -y)` des Z-nach-oben-Weltsystems von
  BeamNG (siehe [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Eine Routendatei {#a-route-file}

Geschrieben von `heat3d_capture route` und `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` ist eine Liste von `[x, y, z]`. Eine Routendatei mit `bounds`, aber ohne
Positionen funktioniert trotzdem: Ihre beiden Ecken ergeben eine entartete Linie, aber
eine brauchbare Box.

### 3. Eine FH-Companion-Rundendatei {#an-fh-companion-lap-file}

Die einzelnen Rundendateien der aufgezeichneten Bibliothek von FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Fehlt `X`, `Y` oder `Z`, gilt der Wert als 0. Die Dateien werden mit einer
Byte-Order-Mark geschrieben, deshalb wird alles JSON als `utf-8-sig` gelesen.

### 4. Eine `.npz`-Aufnahme {#a-npz-recording}

Ein NumPy-Archiv, das ein Array `positions` mit der Form (n, 3) enthält.

### 5. Eine `.csv`-Tabelle {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Spalten mit den Namen `x`, `y`, `z` (Groß- und Kleinschreibung sowie umgebende
  Leerzeichen werden ignoriert) sind Pflicht. Andere Spalten werden ignoriert.
- Zeilen, die mit `#` beginnen, werden übersprungen. Steht in der **ersten** Zeile
  `# {json}`, werden daraus `game` und `track` gelesen.
- Zeilen, die sich nicht als Zahlen lesen lassen, werden übersprungen.

### 6. Ein Ordner {#a-folder}

Ein Ordner wird **rekursiv** nach `.json`-, `.npz`- und `.csv`-Dateien durchsucht,
und alle werden zu einer gefahrenen Linie zusammengefügt. So wird eine ganze
aufgezeichnete Strecke gespeichert: FH Companion legt Ordner nach Klasse, Auto, Tuning
und Schlagwort an.

- `course.json` wird am Namen erkannt und übersprungen (es sind Metadaten, keine Runde).
- Eine Datei, die sich nicht lesen lässt, wird still übersprungen. Eine kaputte Datei
  unter Hunderten kostet nicht die übrigen.
- Die Konsole meldet, wie viele Rundendateien eingegangen sind (`12 laps, 18,400 samples`).
- Der Ordner bekommt das Spiel, das seine Dateien nennen, wenn sie **nur eines**
  nennen. Eine Datei, die kein Spiel nennt (eine FH-Companion-Runde, `course.json`, eine
  CSV ohne ihre Beschreibungszeile), zählt nicht, deshalb kostet eine davon unter den
  Aufnahmen eines Spiels dem Ordner nicht sein Spiel. Dateien, die zwei verschiedene
  Spiele nennen, sind gemischt, und der Ordner bekommt keines. Ein Ordner ohne Spiel
  wird als Forza exportiert, sofern `--game` nichts anderes sagt.
- Wird nichts gelesen: "no readable laps under <folder>".

### 7. Ein Kursname {#a-course-name}

Ist das Argument weder eine vorhandene Datei noch ein Ordner, wird es als Kursname in
der FH-Companion-Bibliothek gesucht, `%LOCALAPPDATA%\FHCompanion\laps`:

1. ein Ordner, dessen Name, ohne den Zusatz ` (course_...)`, dem Namen entspricht
   (ohne Unterscheidung von Groß- und Kleinschreibung);
2. andernfalls der einzige Ordner, dessen Name ihn enthält.

So findet `"Example Circuit"` den Ordner
`Example Circuit (course_1200_3400_to_1175_3400)`, ohne dass jemand die Koordinaten
kennt. Mehrere Treffer sind ein Fehler, der sie auflistet. Ein über den Namen
gefundener Kurs trägt kein Spiel, deshalb wird er als Forza exportiert, sofern
`--game` nichts anderes sagt.

## Was `terrain --route` annimmt {#what-terrain---route-accepts}

`terrain` braucht das Feld `bounds` der Routendatei (Form 2 oben),
`{"min": [x, y, z], "max": [x, y, z]}`. Ohne `bounds` stoppt es mit
"<file> has no bounds; --route takes a route file with "bounds": {...}". Die Datei
wird als UTF-8 gelesen, mit oder ohne Byte-Order-Mark, wie jede JSON-Runde. Hat
dieselbe Datei außerdem mindestens 10 Positionen, die nach den obigen Regeln lesbar
sind, grenzen sie den Ausschnitt auf einen Korridor ein und steuern die Detailtiefe.

## Wie die Runde verwendet wird {#how-the-lap-is-used}

| Verwendung | Einzelheiten |
|---|---|
| Name | der Dateiname ohne Endung oder der Ordnername ohne ` (course_...)`; er wird zum Standardnamen der Ausgabedatei |
| zurückgelegte Strecke | die Summe der Abstände zwischen aufeinanderfolgenden Punkten (ausgegeben als `m driven`; bei einem Ordner zählen die Sprünge zwischen den Dateien mit) |
| Box | die Ausdehnung in x und z, um `--margin` erweitert; die Höhe wird nie begrenzt |
| Korridor | die x- und z-Werte jedes Punktes, siehe [Streckenexport](course-export.md#the-corridor) |
| Detailtiefe | die Entfernung jeder platzierten Kopie zum nächsten Punkt, siehe [Detailstufen und Budget](detail-budget.md) |

Eine Runde mit weniger als zwei Punkten wird abgelehnt ("holds no driving").

## Fehler {#errors}

| Meldung | Bedeutung |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | die Datei ist kein JSON (und weder `.npz` noch `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON einer anderen Form |
| `<file> has no x, y and z columns` | eine CSV ohne diese Spaltenköpfe |
| `<file> has no positions array` | eine `.npz` ohne `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | ein Name, aber keine FH-Companion-Bibliothek |
| `'<name>' matches 3 courses: A, B, C` | genauer angeben |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | nur bei Namenssuchen und `courses` |
