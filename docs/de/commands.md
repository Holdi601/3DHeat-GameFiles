---
title: Befehle
nav_order: 2
lang: de
source: commands.md
source_hash: "6c8d37db40e5"
nav_exclude: true
search_exclude: true
---
# Befehle {#commands}

Jeder Befehl läuft als `python -m heat3d_gamefiles <verb> ...` aus dem Ordner des Projekts.
Die Verben stehen in der Reihenfolge, in der du sie meist brauchst: was ist diese Datei,
was steckt darin, gib mir jenes, und mach aus einer Runde eine Strecke.

| Verb | Nimmt | Macht |
|---|---|---|
| [`identify`](#identify) | jede Datei | nennt das Containerformat, indem es die Bytes liest |
| [`list`](#list) | ein Unreal-`.pak` oder IoStore-`.utoc`, ein Source-2-`.vpk`, ein ForzaTech-`.minizip` oder ein Zip | listet seine Einträge auf |
| [`extract`](#extract) | dasselbe | schreibt einen Eintrag auf die Platte |
| [`meshes`](#meshes) | eine Unity-`SerializedFile` | listet seine Meshes auf und prüft sie |
| [`course`](#course) | eine Runde | exportiert die Strecke um die Runde (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | eine gespeicherte Rundenbibliothek | führt `course` für jede Strecke darin aus (Forza) |
| [`terrain`](#terrain) | einen Forza-Streckenordner | schneidet einen Bereich anhand von Weltkoordinaten aus |
| [`levels`](#levels-and-level-frostbite) | ein installiertes Frostbite-Spiel (Battlefield 6) | listet seine Level auf |
| [`level`](#levels-and-level-frostbite) | den Namen eines Levels | exportiert das Level: Gelände, platzierte Meshes, optional ihre Farbkarten (Battlefield 6) |
| [`cars`](#cars) | ein installiertes Forza | jedes Auto in niedriger Detailstufe, in einer Datei für den Rennen-Tab des Viewers |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | ein Unreal-5-Spiel | listet seine World-Partition-Karten auf |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | den Namen einer Karte | exportiert die Karte: Landschaft, HLOD-Strukturen, Wasser |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | ein installiertes Arma Reforger | listet seine Welten auf |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | den Namen einer Welt | exportiert die Welt: Gelände in seinen Farben, das Meer, Gebäude als Quader |

**So liest du die Beispiele:** `<x>` heißt, dass du es durch deinen eigenen Wert ersetzt, ohne die
spitzen Klammern. `[...]` ist optional. Einen Pfad mit Leerzeichen setzt du in "doppelte
Anführungszeichen", zum Beispiel `"C:\Games\Mein Spiel"`. Neu damit? Siehe [Bevor du anfängst](before-you-start.md).
Die vollständige `--help`-Ausgabe jedes Verbs steht in der [Befehlsreferenz](../cli-reference.md).

Bei jedem Start prüft das Programm unter Umständen zuerst, ob es eine neuere Version gibt. Siehe
[Updates](updates.md). `HEAT3D_NO_UPDATE=1` schaltet diese Prüfung ab.

Quelle: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Schritt-für-Schritt-Seiten: [Archive untersuchen](inspecting-archives.md), [Strecken-Export](course-export.md),
[Ganze Level](whole-levels.md), [Forza-Autos](forza-cars.md).

![Ausgabe von python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Exit-Codes {#exit-codes}

| Code | Bedeutung |
|---|---|
| 0 | erfolgreich |
| 1 | die Arbeit ist fehlgeschlagen (eine nicht lesbare Runde, kein Spiel gefunden, nichts zu exportieren, eine Strecke in `courses` ist fehlgeschlagen; bei `list` und `extract` eine Datei, die keines der Archive ist, die sie lesen, eine, die sich nicht öffnen oder lesen lässt - eine verschlüsselte pak ohne `--key`, ein verschlüsselter IoStore-Container - oder ein Eintrag, der nicht im Archiv steht) |
| 2 | falsche Argumente (argparse), ein Pfad, der nicht existiert, ein `--key`, das nicht aus 64 Hex-Ziffern besteht, oder `terrain` mit beiden oder keinem von `--box` und `--route` |

Die Fehler von `list` und `extract` stehen jeweils in einer Zeile auf der Standardfehlerausgabe,
nicht als Python-Traceback.

---

## identify {#identify}

```
python -m heat3d_gamefiles identify <path>
```

Dieser Befehl liest die Datei und sagt, welcher Container es ist. Er geht nicht nach der
Dateiendung (die einzige Ausnahme ist eine `.ucas`, siehe unten). Er probiert die Formate in
dieser Reihenfolge und hört beim ersten auf, das sich parsen lässt:

1. **Unreal-`.pak`**: ein Footer mit der pak-Kennung in den letzten 1.024 Bytes. Gibt die Version,
   den Offset und die Größe des Index, ob der Index verschlüsselt ist, und die Kompressionsmethoden aus.
2. **Unreal-IoStore-`.utoc`**: die IoStore-Kennung am Anfang. Gibt die Version, die Anzahl der Chunks
   und an, ob der Container verschlüsselt ist; bei einem unverschlüsselten die Anzahl der Dateien, die
   sein Verzeichnis nennt (und unter welchem Mount-Punkt), die Kompressionsmethoden und ob seine
   `.ucas` daneben liegt. Eine `.ucas` hat keinen eigenen Header, daher wird sie an der gleichnamigen
   `.utoc` daneben erkannt, und `identify` nennt diese Datei.
3. **ForzaTech-`.minizip`**: die Kennung `PGZP`. Gibt die Version, die Anzahl der Einträge und Segmente
   und an, ob die `ChunkContentsMiniZip<n>.txt` daneben liegt, die die Einträge nennt (und, falls ja,
   ob sie so viele nennt, wie es gibt).
4. **Zip**: ein Zip-Dateikopf am Anfang. Gibt die Anzahl der Einträge, die sechs häufigsten Endungen
   und die Levelnamen aus, wenn Einträge unter `levels/<name>/` liegen, wie in einem BeamNG.drive-Level-Archiv.
5. **Unity**: ein `UnityFS`-Bundle (gibt die Engine-Version und die Anzahl der Einträge aus) oder eine
   nackte `SerializedFile` (gibt das Format, die Engine-Version, die Anzahl der Objekte und die sechs
   häufigsten Klassen aus).
6. **Frostbite-`.toc`**: gibt die Art (`plain` oder `signed`), wo der Baum beginnt, und entweder die
   Anzahl der Assets (binäre Abschnittstabelle) oder die Anzahl der Superbundles (DbObject-Baum) aus.
7. **Source-2-`.vpk`**: gibt die Version, die Anzahl der Einträge und das erste `.nav`-Navigationsmesh
   aus, falls das Archiv eines hat.
8. **BeamNG-`.cdae`**: Shape-Version 31, die sich parsen lässt. Gibt die Anzahl der Meshes, die Anzahl
   der gezeichneten Detailstufen und die ersten Materialien aus.
9. **BeamNG-`.ter`**: hat keine Kennung, deshalb muss alles zusammenpassen - eine Seitenlänge von 2
   bis 16.384, so viele quadratische Höhen- und Layer-Bytes, dann 1 bis 255 druckbare Layernamen.
   Gibt die Version, die Größe und die Layernamen aus.
10. **ForzaTech-`.modelbin`**: gibt die Version, die Anzahl der Chunks und die sechs häufigsten
    Chunk-Tags aus. Der Inhalt der Chunks wird hier nicht dekodiert.

Die Formate mit eigener Kennung (2 bis 4) kommen vor Unity und Frostbite, deren Prüfungen die ganze
Datei lesen: ein Forza-Archiv ist zig Gigabyte groß.

Passt keines, gibt er `not a format this tool reads` (kein Format, das dieses Werkzeug liest) und den
letzten Grund aus. Dieser Grund kommt von der ForzaTech-Prüfung.

Beispiel (synthetisch):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list {#list}

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Option | Standard | Bedeutung |
|---|---|---|
| `<archive>` | erforderlich | eine Unreal-`.pak`; eine IoStore-`.utoc` (oder die `.ucas` daneben); eine Source-2-`.vpk` (bei geteilten VPKs die `_dir.vpk`); eine ForzaTech-`.minizip`; ein Zip, etwa BeamNGs Level- und Inhalts-Archive |
| `--filter TEXT` | keiner | nur Pfade, die TEXT enthalten, ohne Groß-/Kleinschreibung |
| `--limit N` | 50 | gibt höchstens N Einträge aus (die Gesamtzahl wird immer ausgegeben) |
| `--key HEX` | keiner | ein AES-256-Schlüssel, den du schon hast, 64 Hex-Ziffern, mit oder ohne `0x`. Nur eine verschlüsselte `.pak` benutzt ihn. Alles, was nicht aus 64 Hex-Ziffern besteht, wird abgelehnt, bevor das Archiv geöffnet wird (Exit-Code 2) |

Das Werkzeug erkennt das Format an den Bytes: eine IoStore-Inhaltstabelle, eine `.minizip` und ein VPK
an ihrer Signatur am Anfang, ein Zip an seinem lokalen Dateikopf und eine `.pak` am Footer am Ende.
Eine `.ucas` hat keinen Kopf und wird über die gleichnamige `.utoc` geöffnet. Eine Datei, die keines
davon ist, wird mit `<file> is not an archive list and extract read (...)` (Datei ist kein Archiv, das
list und extract lesen) abgelehnt. Eine, die eines davon ist, aber sich nicht öffnen lässt, wird mit
dem Grund des Lesers abgelehnt: eine verschlüsselte pak ohne `--key`, ein verschlüsselter
IoStore-Container oder eine pak-Version, die es nicht liest. In beiden Fällen ist es eine Zeile und
Exit-Code 1.

Jede Zeile zeigt die unkomprimierte Größe, die Kompressionsmethode und den Pfad:

| Archiv | Methode | Pfade |
|---|---|---|
| `.pak` | `none`, oder der Name aus dem Footer (`Zlib`, `Oodle`, `Gzip`...) | mit dem Mount-Punkt des Archivs, zum Beispiel `../../../Game/Content/...` |
| IoStore-`.utoc` | `none`, oder die Methode des Containers (`Oodle`, `Zlib`...), so wie ihr erster Block gespeichert ist | mit dem Mount-Punkt, zum Beispiel `../../../<Project>/Content/...`. Ein Container ohne Verzeichnisindex nennt keine Dateien und wird abgelehnt |
| `.vpk` | immer `stored` | wie im Verzeichnis |
| `.minizip` | `lz4`, `deflate` oder `stored` | wie die `ChunkContentsMiniZip<n>.txt` daneben sie schreibt, ohne den Präfix des Build-Rechners (Backslashes, so wie das Spiel sie schreibt). Das Archiv speichert keine Namen, daher heißen die Einträge ohne diese Datei `#0`, `#1`... Eine Liste, deren Zeilenzahl von den Einträgen abweicht, wird abgelehnt: die beiden gehören nicht zusammen |
| Zip | `stored`, `deflate`, ... | wie gespeichert; Ordner werden nicht aufgelistet |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract {#extract}

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Option | Standard | Bedeutung |
|---|---|---|
| `<archive>` | erforderlich | wie bei `list` |
| `<entry>` | erforderlich | der Pfad genau so, wie `list` ihn ausgibt (Groß-/Kleinschreibung zählt); in einer `.minizip` funktioniert auch `#<Nummer>` |
| `--out FILE` | der Dateiname des Eintrags (nach dem letzten `/` oder `\`), im aktuellen Ordner | wohin geschrieben wird; übergeordnete Ordner werden angelegt |
| `--key HEX` | keiner | wie bei `list` |

Der Eintrag wird entschlüsselt (pak, mit Schlüssel), dekomprimiert und geschrieben. Es gibt
`<bytes> bytes -> <file>` aus. Steht der Pfad nicht im Archiv, endet der Befehl mit Exit-Code 1.
Ebenso bei einem Eintrag, der sich nicht lesen lässt (ein verschlüsselter Eintrag ohne Schlüssel,
Oodle-komprimiert ohne Oodle-Bibliothek), mit dem Grund in einer Zeile. Ein VPK-Eintrag wird hier
nicht gegen seine CRC geprüft. Dafür hat der Leser eine Methode `verify()` (siehe
[Source-2-VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes {#meshes}

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Option | Standard | Bedeutung |
|---|---|---|
| `<path>` | erforderlich | eine nackte Unity-`SerializedFile` (`sharedassets0.assets`, `level0`...), kein Bundle |
| `--limit N` | 25 | dekodiert und gibt höchstens N Meshes aus |

Das gibt die Anzahl der `Mesh`-Objekte aus, dann eine Zeile pro Mesh: den Namen (die ersten 40
Zeichen), die Anzahl der Vertices und Dreiecke und `ok` oder `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` heißt, dass die dekodierten Vertices die Begrenzungsbox, die Unity für das Mesh
gespeichert hat, nicht innerhalb von 2 % der Boxgröße treffen. Das ist die eigene Prüfung des
Parsers (siehe [Unity](reader-unity.md)). Ein Mesh, das sich nicht lesen lässt, wird mit dem Grund
gemeldet und zählt zum Limit. Vertex-Daten in einer `.resS`-Datei werden aus dem Ordner gelesen, in
dem der Container liegt.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Dieser Befehl exportiert die Strecke um eine Runde: den Boden in einem Streifen links und rechts
der Fahrlinie und was darauf steht, als eine `.glb`. Den Rest findet er selbst heraus: welches
Spiel, welche installierte Kopie, welche Strecke, welches Level oder welche Etappe und (bei Assetto
Corsa Rally) wie herum die Achsen liegen. Siehe [Strecken-Export](course-export.md).

`<lap>` kann eines der folgenden sein (Details in [Rundeneingaben](lap-inputs.md)):

- eine Rundendatei: Route-JSON, FH-Companion-Runden-JSON, `heat3d-lap`-JSON, `.npz` oder `.csv` mit den Spalten x, y, z
- ein Ordner mit Rundendateien, rekursiv durchsucht (eine ganze aufgezeichnete Strecke)
- ein Streckenname, nachgeschlagen in der FH-Companion-Bibliothek unter `%LOCALAPPDATA%\FHCompanion\laps`

### Optionen {#options}

| Option | Standard | Spiele | Bedeutung |
|---|---|---|---|
| `-o`, `--out FILE` | `<Streckenname>.glb` im aktuellen Ordner | alle | wohin geschrieben wird; der Name wird in Kleinbuchstaben umgewandelt, Folgen anderer Zeichen werden zu `_` |
| `--game {forza,beamng,acrally}` | was die Rundendatei sagt, sonst `forza` | alle | aus welchem Spiel die Runde stammt |
| `--margin M` | 80 | alle | Meter Boden, die links und rechts der Fahrlinie bleiben |
| `--texture-size {2048,1024,512}` | 2048 | alle | Bodentexturpixel pro 512-m-Kachel (2048 = 25 cm pro Pixel) |
| `--no-textures` | aus | alle | nur flache Farben: eine weit kleinere Datei. Bei Forza entfällt damit auch die Trennung von Straße und Randstreifen (siehe unten) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | die Bodenkarten und Modelltexturen welcher Jahreszeit |
| `--no-placed` | aus | alle | nur Gelände: keine Bordsteine, Leitplanken, Schilder, Gebäude. Bei BeamNG bleiben als Meshes modellierte Fahrflächen erhalten |
| `--trees` | aus | alle | platziert auch Vegetation (Forza: Bäume, Büsche und zerstörbare Objekte; BeamNG: Bäume; AC Rally: Bäume und das instanzierte Grün) |
| `--detail-budget N` | automatisch | alle | eine Obergrenze für Dreiecke für alles Platzierte; siehe [Detailstufen und Budget](detail-budget.md) |
| `--track DIR` | wird gesucht | Forza | der Streckenordner (unter `media\Tracks`, mit `GeoChunk0.minizip`), falls das installierte Spiel nicht gesucht werden soll |
| `--level NAME` | aus der Runde gefunden | BeamNG, AC Rally | das Level (Ordnername bei BeamNG) oder die Etappe (Kartenname bei AC Rally), ohne Groß-/Kleinschreibung |
| `--install DIR` | in den Steam-Bibliotheken gesucht | BeamNG, AC Rally | BeamNG: der Ordner mit `gameengine.zip`. AC Rally: der Spielordner oder sein `acr\Content\Paks` / `Content\Paks` |

Optionen, die für ein Spiel nicht gelten, werden ohne Warnung ignoriert. Zum Beispiel tut `--season`
bei BeamNG und AC Rally nichts, und `--track` tut bei ihnen ebenfalls nichts.

### Welches Spiel {#which-game}

Das Spiel wird aus `--game` genommen, dann aus dem Feld `game` einer `heat3d-lap`-Datei (oder aus
der `# {...}`-Beschreibungszeile einer CSV), und fällt sonst auf Forza zurück. Ein Ordner bekommt das
Spiel, das seine Dateien nennen, wenn sie nur eines nennen. Eine Datei, die keines nennt (eine
FH-Companion-Runde, `course.json`, eine CSV ohne Beschreibungszeile), zählt nicht (siehe
[Rundeneingaben](lap-inputs.md)).

| Wert | Export |
|---|---|
| beginnt mit `forza` | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` oder `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | abgelehnt: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | abgelehnt: "tracks ship in a protected format that is not a file-extraction target" |
| alles andere | abgelehnt: "there is no course reader for <game> yet" |

Eine Ablehnung nennt auch die Alternativen: die Strecke aus dem Spiel rekonstruieren (3DHeat
GameCapture) oder die Runden ohne Strecke analysieren, denn der Tab Rennanalyse des Viewers zeichnet
aus ihnen eine Straße.

### Beispiele {#examples}

```
# Eine Strecke aus der FH-Companion-Bibliothek, nach Namen
python -m heat3d_gamefiles course "Example Circuit"

# Eine Rundendatei, ein schmalerer Streifen, eine kleinere Datei
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Winter-Texturen, mit Bäumen
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# Eine harte Obergrenze von 500.000 platzierten Dreiecken
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Ein Streckenordner direkt angegeben (Spiel außerhalb von Steam installiert)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: das Level nennen, auf die Installation zeigen
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, mit einer einfachen CSV-Runde, die ihr Spiel nicht nennt
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Beispielausgabe (Forza, synthetische Zahlen):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars {#cars}

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Jedes Auto eines installierten Forza in der niedrigen Detailstufe des Spiels, in einer Datei für den
Rennen-Tab des Viewers: das `ProxyLOD`-Modell, das jedes Auto-Archiv unter `media/Cars` mitbringt,
etwa 900 Dreiecke, mit der Startnummer des Autos, wie die Telemetrie sie angibt, seiner Marke,
dem Modellkürzel und dem Baujahr aus dem Archivnamen sowie seinen Rädern und Rücklichtern. Das
dauert Sekunden und schreibt etwa 5 MB. Führe es erneut aus, wenn das Spiel neue Autos bekommt. Ein
Archiv ohne solches Modell (ein Verkehrsobjekt) wird benannt und ausgelassen. Das Format steht in
[`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Die Formen sind in Metern, wie es das Spiel selbst hat: 1:1 mit dem Auto. Die Datei enthält Inhalte
des Spiels, sie ist daher für den Rechner gedacht, auf dem sie entstanden ist, und nicht zum Weitergeben.

## courses {#courses}

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Das führt den Forza-`course`-Export für jeden Streckenordner in einer aufgezeichneten
Rundenbibliothek aus und schreibt je eine `<name>.glb`. Es gilt nur für Forza. Es ruft den
Forza-Export direkt auf und liest `--game`, `--level` oder `--install` nicht.

| Option | Standard | Bedeutung |
|---|---|---|
| `-o`, `--out FOLDER` | `courses` | der Ordner, in den geschrieben wird (wird angelegt, falls er fehlt) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | die Rundenbibliothek |
| `--only TEXT [TEXT ...]` | alle | nur die Strecken, deren Ordnernamen eines dieser Wörter enthalten (ohne Groß-/Kleinschreibung) |
| `--force` | aus | exportiert erneut, was schon eine `.glb` hat |
| `--track DIR` | wird gesucht | wie bei `course` |
| `--margin M` | 80 | wie bei `course` |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | wie bei `course` |

Was als Streckenordner zählt: ein direkter Unterordner der Bibliothek, dessen Name ` (course_`
enthält, so benennt FH Companion sie, zum Beispiel
`Example Circuit (course_1200_3400_to_1175_3400)`. Der Teil ab ` (course_` wird aus dem Namen entfernt.

So verhält sich ein Lauf:

- Eine Strecke, deren `.glb` schon existiert, wird übersprungen (`kept`), außer mit `--force`. So
  macht ein unterbrochener Lauf dort weiter, wo er aufgehört hat.
- Eine Strecke, die fehlschlägt (nicht lesbare Runden, zu wenig Speicher, kein Gelände ...), wird als
  `FAILED` gemeldet, und der Lauf geht weiter.
- Am Ende gibt er eine Tabelle aus mit Status, Größe in MB, benötigten Sekunden und Name, danach
  `<n> of <total> courses in <folder>`.
- Der Exit-Code ist 1, wenn eine Strecke fehlgeschlagen ist.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## terrain {#terrain}

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Das ist der Forza-Ausschnitt, bei dem du alles von Hand angibst: den Streckenordner und einen
Bereich, nicht eine Runde. Es ist nützlich, wenn der gewünschte Bereich eher ein Kasten als eine
Fahrt ist.

| Option | Standard | Bedeutung |
|---|---|---|
| `<path>` | erforderlich | ein Forza-Streckenordner unter `media\Tracks` (mit `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | erforderlich | die zu schreibende `.glb` |
| `--box X0 Z0 X1 Z1` | | der Bereich, in Metern des Spiels (x und z, so wie die Telemetrie sie angibt); Ecken in beliebiger Reihenfolge |
| `--route FILE` | | eine Route-JSON mit `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, so wie `heat3d_capture route` und `heat3d_capture laps` sie schreiben; als UTF-8 gelesen, mit oder ohne Byte-Order-Mark |
| `--margin M` | **100** | Meter, die um die Grenzen einer Route gelegt werden, und die Breite des Korridors, wenn die Route eine Linie hat |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | wie bei `course` |

Gib genau eines von `--box` und `--route` an, sonst ist der Exit-Code 2. Bei `--route` ist der
Ausschnitt die `bounds` der Route (`min`/`max`, x und z), erweitert um den Rand. Enthält die Datei
außerdem mindestens 10 Positionen, wird der Ausschnitt auf einen Korridor von `--margin` Metern um
diese Positionen verengt, und platzierte Modelle bekommen ihre Detailstufe nach dem Abstand zu dieser
Linie. Bei `--box` bleibt der ganze Kasten erhalten, und die Detailstufe geht an das, was der Mitte
des Kastens am nächsten steht.

Die Höhe gehört nie zum Ausschnitt. Ein Kasten außerhalb der Karte oder im Meer ergibt
"no terrain there" (kein Gelände dort, Exit-Code 1), kein Fehler über Koordinaten.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite) {#levels-and-level-frostbite}

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` listet die Level auf, die ein installiertes Frostbite-Spiel mitbringt, nach dem Namen ihrer
Tabelle (`levels/<level>/<level>.toc`), mit Größe und Herkunft: `Data` für das Grundspiel,
`Update/<pack>` für ein Update und wie viele hochauflösende Tabellen dazukommen. Ein Level, das ein
Update mitbringt, hat im Grundspiel nur eine kleine Tabelle mit Chunks; die Tabelle mit den Bundles
des Levels ist das Level (siehe [Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` exportiert eines: das Höhenfeld des Geländes, jedes Mesh, das die statischen Modellgruppen des
Levels platzieren, die Objekte einzeln mit ihrer Position und die Gelände-Kulisse des Levels rund um
die Karte. Mit `--textures` trägt jede Oberfläche ihre Farbkarte; mit `--navmesh` kommen die
Oberflächen dazu, auf denen Soldaten laufen. Wie es gelesen wird, steht in [Frostbite](reader-frostbite.md).

| Option | Standard | Bedeutung |
|---|---|---|
| `<level>` | erforderlich | ein Name, wie `levels` ihn ausgibt, ein eindeutiger Teil davon oder der Pfad zur `.toc` eines Levels |
| `-o`, `--out FILE` | `<level>.glb` | die zu schreibende `.glb` |
| `--install FOLDER` | die erste Steam-Installation, deren `Data` eine `layout.toc` hat | der Spielordner |
| `--textures [PIXELS]` | aus; 512, wenn ohne Größe angegeben | schreibt die Farbkarte jeder Oberfläche, die größte Mipmap, die höchstens PIXELS an einer Seite hat, und ihre Texturkoordinaten, so wie das Spiel sie hat, mit einem wiederholenden Sampler (siehe [Ausgabeformat](output-format.md)). Das Höhenfeld bekommt die Farbkarte der Gelände-Kulisse, wo diese Karte es abdeckt, sonst die mittlere Farbe der Oberflächenmaterialien des Geländes, sonst die Durchschnittsfarbe der Kulisse drum herum. Ohne den Schalter ist jeder Teil eine flache Farbe |
| `--ground-texture [METRES]` | aus; 0,5, wenn ohne Größe angegeben | bäckt die Gelände-Decals - Straßen, Landebahnen, Vorfelder, aufgemalte Markierungen - über die Bodenfarbe, multipliziert mit der Farbkarte des Geländes, wo das Level eine hat, in die Farbe des Höhenfeldes, METRES pro Pixel, in Kacheln von höchstens 4.096 Pixeln (`ground:terrain x<x> z<z>`). Funktioniert mit oder ohne `--textures` |
| `--navmesh` | aus | fügt das Navigationsnetz des Levels für seinen kleinsten Agenten hinzu, den Soldaten (1,8 m hoch, 0,4 m breit), als Teil `nav:walkable`: der Boden, Böden, Treppen und die Dächer, auf die ein Soldat kommt, ohne die Verbindungen (Sprünge, Leitern, Übersteigen) zwischen ihnen |
| `--ground-spacing METRES` | 4 | der feinste Abstand des Höhenfeldes; feinere Knoten werden auf diesen Abstand herabgerechnet. 0 lässt das Höhenfeld weg |
| `--detail-budget N` | jede Kopie in ihrer gröbsten Stufe, plus ein Viertel, mindestens 1.500.000 | eine Obergrenze für Dreiecke. Die Meshes mit den höchsten Kosten verlieren jeweils eine Detailstufe, bis es passt; reichen auch die gröbsten Stufen nicht, werden zuerst die kleinsten Kopien weggelassen. Die Gelände-Kulisse wird nie gröber gemacht oder weggelassen |
| `--skip TEXT` | | lässt statische Modellgruppen weg, deren Partitionsname TEXT enthält; mehrfach angeben für mehrere. Zum Beispiel die Ebene eines Spielmodus |
| `--by-mesh` | aus | um zu finden, was ein Teil ist: ein Teil pro Quell-Mesh und Material, benannt `<part> \| <mesh> \| <material>`; eine viel größere Datei |
| `--clamped-uvs` | aus | für einen Renderer, der eine Textur nicht wiederholen kann: jedes texturierte Dreieck wird in Stücke geschnitten, deren Koordinaten innerhalb von 0..1 liegen, und ein Dreieck, das mehr als 4 Stücke bräuchte, wird in der Durchschnittsfarbe seiner Textur gezeichnet, in einem Teil `<part> (average colour)` |

Es gibt aus, welche Gruppen es gibt und wie viele Kopien jede platziert hat, welche Meshes es
ausgelassen hat und warum, die Dreiecke pro Teil (und mit `--textures`, wie viele Texturen und wie
viele Abschnitte ihre Farbkarte gefunden haben), was der Boden ist, und mit `--navmesh`, wie viele
Navigationskacheln gelesen wurden. Über das Level wird außer der Geometrie nichts geschrieben: keine
Namen, keine Metadaten (siehe [Ausgabeformat](output-format.md)).

Das Gelände-Budget ist getrennt: das Höhenfeld und die Kulisse werden durch `--detail-budget` nie
gröber gemacht; `--ground-spacing` bestimmt die Größe des Höhenfeldes.

Ein ganzes Level ist groß: typisch über zehn Millionen Dreiecke und mehrere hundert MB. `--textures`
fügt der Datei etwas hinzu; ein Level, das dicht mit Bäumen bewachsen ist, kann etwa 1 GB erreichen.
`--textures 256 --detail-budget 3000000 --ground-spacing 8` bringt ein Level auf etwa ein Drittel
davon.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition) {#ue-maps-and-ue-map-unreal-5-world-partition}

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` ist der Ordner des Spiels, sein `Content/Paks` oder der Name seines Ordners in einer
Steam-Bibliothek (`"<Steam game folder name>"`). `ue-maps` listet jede Karte auf, die fertige
World-Partition-Zellen daneben hat. `ue-map` exportiert eine davon als `ground:<map>` (die
Landschaft), `structure:<map>` (die zusammengeführten HLOD-Meshes der Karte) und `water:<map>`
(ihre Wasserflächen, wo sie über dem Boden stehen), in Unreal-**Zentimetern** mit vertauschten Y- und
Z-Achsen - der einzige Export, der nicht in Metern ist. Wie jedes gelesen und geprüft wird:
[Unreal-5-Karten](level-unreal-world-partition.md).

| Option | Standard | Bedeutung |
|---|---|---|
| `<map>` | erforderlich | ein Name, wie `ue-maps` ihn ausgibt, oder ein eindeutiger Teil davon |
| `-o`, `--out FILE` | `<map>.glb` | die zu schreibende `.glb` |
| `--ground-spacing METRES` | 2 | der Abstand der Landschafts-Vertices in der Datei, auf eine ganze Zahl eigener Quads gerundet |
| `--no-structures`, `--no-water` | | lässt diesen Teil weg |

Es gibt die Dreiecke pro Teil aus, wie viele Landschafts-Komponenten gelesen wurden und wie viele der
doppelt gespeicherten Vertices nicht übereinstimmen. Eine 3-km-Karte mit 2 m ergibt etwa 4,6 Millionen
Boden-Dreiecke.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` listet jede Welt mit einem Gelände auf, nach ihrem Ordner unter `worlds/`.
`enfusion-world` exportiert eine: `ground:<world>` (das Gelände, in den Farben seiner
Supertexture-Kacheln), `water:<world>` (das Meer, auf Höhe null) und `structure:<world>` (die Box
jedes platzierten Modells), in den eigenen Metern des Spiels - x nach Osten, y nach oben, z nach
Norden. Wie jede gelesen und geprüft wird: [Arma-Reforger-Welten](level-arma-reforger.md).

| Option | Standard | Bedeutung |
|---|---|---|
| `<world>` | erforderlich | eine Welt, wie `enfusion-worlds` sie ausgibt |
| `-o`, `--out FILE` | `<world>.glb` | die zu schreibende `.glb` |
| `--install FOLDER` | die Steam-Bibliothek, die das Spiel enthält | der Spielordner |
| `--ground-spacing METRES` | 2 (das des Geländes) | der Vertex-Abstand des Geländes in der Datei |
| `--texture-size PIXELS` | 4096 | die größere Seite des Bodenfarbbildes; 0 für flache Farbe |
| `--no-structures` | | lässt die platzierten Modelle weg |
| `--trees` | aus | platziert auch Bäume und andere Vegetation, als Boxen |

Es gibt die Dreiecke pro Teil aus, wie viele Kachelrand-Vertices nicht übereinstimmen, wie viele
Entitäten die Weltdatei enthält und wie viele Boxen platziert wurden, und was wegfiel und warum.

## Umgebungsvariablen {#environment-variables}

| Variable | Wirkung |
|---|---|
| `HEAT3D_OODLE` | Pfad zu einer `oo2core_*_win64.dll` oder zu einem Ordner, der eine enthält; siehe [Oodle](reader-oodle.md) |
| `HEAT3D_NO_UPDATE` | jeder Wert außer leer, `0`, `false`, `no` schaltet die Update-Prüfung ab; siehe [Updates](updates.md) |
| `LOCALAPPDATA` | wo die FH-Companion-Bibliothek, BeamNGs Benutzerordner und der Update-Cache gesucht werden |
| `HEAT3D_COURSE` | nur für Tests: die Strecke, die der Test der installierten Bordsteine benutzt; siehe [Entwicklung](development.md) |
