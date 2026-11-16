---
title: "Befehle"
nav_order: 2
lang: "de"
source: commands.md
source_hash: "8ae04c37b1a4"
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
| [`list`](#list) | ein Unreal-`.pak` oder IoStore-`.utoc`, ein Source-2-`.vpk` oder ein Zip (ein ForzaTech-`.minizip` über das Forza-Werkzeug) | listet seine Einträge auf |
| [`extract`](#extract) | dasselbe | schreibt einen Eintrag auf die Platte |
| [`meshes`](#meshes) | eine Unity-`SerializedFile` | listet seine Meshes auf und prüft sie |
| [`course`](#course) | eine Runde | exportiert die Strecke um die Runde (Forza, BeamNG.drive, Assetto Corsa Rally) (vom Forza-, BeamNG.drive- oder AC-Rally-Werkzeug ausgeführt) |
| [`courses`](#courses) | eine aufgezeichnete Rundenbibliothek | führt `course` für jede Strecke darin aus (Forza) (vom Forza-Werkzeug ausgeführt) |
| [`races`](#races) | ein installiertes Forza | listet jedes Rennen auf, das das Spiel definiert: was es hinzufügt, was es verbirgt, Veranstaltungsorte, den Stand seines Exports (vom Forza-Werkzeug ausgeführt) |
| [`terrain`](#terrain) | einen Forza-Streckenordner | schneidet einen Bereich anhand von Weltkoordinaten aus (vom Forza-Werkzeug ausgeführt) |
| [`levels`](#levels-and-level-frostbite) | ein installiertes Frostbite-Spiel (Battlefield 6) | listet seine Levels auf (vom Battlefield-Werkzeug ausgeführt) |
| [`level`](#levels-and-level-frostbite) | den Namen eines Levels | exportiert das Level: Gelände, platzierte Meshes, optional ihre Farbkarten (Battlefield 6) (vom Battlefield-Werkzeug ausgeführt) |
| [`cars`](#cars) | ein installiertes Forza | jedes Auto in niedriger Detailstufe, in einer Datei für den Rennanalyse-Tab des Viewers (vom Forza-Werkzeug ausgeführt) |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | ein Unreal-5-Spiel | listet seine World-Partition-Karten auf |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | den Namen einer Karte | exportiert die Karte: Landschaft, HLOD-Strukturen, Wasser |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | ein installiertes Arma Reforger | listet seine Welten auf (vom Reforger-Werkzeug ausgeführt) |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | den Namen einer Welt | exportiert die Welt: Gelände in seinen Farben, das Meer, Gebäude als Quader (vom Reforger-Werkzeug ausgeführt) |

**So liest du die Beispiele:** `<x>` heißt, dass du es durch deinen eigenen Wert ersetzt, ohne die
spitzen Klammern. `[...]` ist optional. Einen Pfad mit Leerzeichen setzt du in "doppelte
Anführungszeichen", zum Beispiel `"C:\Games\Mein Spiel"`. Neu damit? Siehe [Bevor du anfängst](before-you-start.md).
Die vollständige `--help`-Ausgabe jedes Verbs steht in der [Befehlsreferenz](../cli-reference.md).

Bei jedem Start prüft das Programm unter Umständen zuerst, ob es eine neuere Version gibt. Siehe
[Updates](updates.md). `HEAT3D_NO_UPDATE=1` schaltet diese Prüfung ab.

Quelle: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Schritt-für-Schritt-Seiten: [Archive untersuchen](inspecting-archives.md), [Streckenexport](https://holdi601.github.io/3DHeat-Ext-Forza/course-export.html),
[Ganze Levels](whole-levels.md), [Forza-Autos](https://holdi601.github.io/3DHeat-Ext-Forza/forza-cars.html).

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

## Die Verben der Spiele {#the-games-own-verbs}

Jeder Spiel-Leser ist ein eigenes kleines Projekt mit eigener Lizenzdatei, eigenen Releases und eigenem
Issue-Tracker. So kann er für sich installiert, aktualisiert, gepflegt - oder auf Wunsch eines Rechteinhabers
zurückgezogen - werden, ohne den Viewer oder die anderen Tools zu berühren. Installiere den Leser für dein Spiel
(seine Seite sagt, wie), dann funktionieren sein eigener Befehl und die Befehle hier. GameFiles startet das
Werkzeug des Spiels mit den Argumenten, die du angegeben hast; nichts davon wird importiert. Es wird gefunden als
sein Befehl im `PATH`, als sein installiertes Paket oder als sein Ordner in `HEAT3D_<GAME>_MAPS` oder neben
GameFiles (`exporters/ext/<game>-maps` in einem 3DHeat-Checkout oder `3DHeat-Ext-<Game>` neben diesem Ordner). Ist
es nicht installiert, sagt der Befehl, wo du es bekommst, und beendet sich mit Code 2.

| Spiel | Sein eigenes Werkzeug | Befehle hier, die es ausführen |
|---|---|---|
| Forza Horizon / Motorsport | [3DHeat-Ext-Forza](https://holdi601.github.io/3DHeat-Ext-Forza/) (`heat3d-forza-maps`) | `course` (Forza-Runden), `courses`, `races`, `cars`, `terrain`; `identify`, `list`, `extract` eines `.minizip` |
| Battlefield (Frostbite) | [3DHeat-Ext-Battlefield](https://holdi601.github.io/3DHeat-Ext-Battlefield/) (`heat3d-battlefield-maps`) | `levels`, `level`; `identify` eines Frostbite-`.toc` |
| BeamNG.drive | [3DHeat-Ext-BeamNG](https://holdi601.github.io/3DHeat-Ext-BeamNG/) (`heat3d-beamng-maps`) | `course` (BeamNG-Runden); `identify` einer `.cdae` oder `.ter` |
| Assetto Corsa Rally | [3DHeat-Ext-ACRally](https://holdi601.github.io/3DHeat-Ext-ACRally/) (`heat3d-acrally-maps`) | `course` (AC-Rally-Runden) |
| Arma Reforger (Enfusion) | [3DHeat-Ext-Reforger](https://holdi601.github.io/3DHeat-Ext-Reforger/) (`heat3d-reforger-maps`) | `enfusion-worlds`, `enfusion-world` |

`python -m heat3d_gamefiles <verb> --help` zeigt die eigenen Optionen des Spielwerkzeugs.

## course {#course}

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Die Strecke um eine Runde – der Boden in einem Streifen links und rechts der Fahrlinie und was darauf
steht, als eine `.glb` – entsteht mit dem eigenen Werkzeug des Spiels, zu dem die Runde gehört, mit
denselben Argumenten: [Forza](https://holdi601.github.io/3DHeat-Ext-Forza/course-forza-horizon.html),
[BeamNG.drive](https://holdi601.github.io/3DHeat-Ext-BeamNG/course-beamng.html),
[Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html). Was eine Runde
sein kann: [Rundeneingaben](lap-inputs.md); wie viel Detail behalten wird:
[Detailstufen und Budget](detail-budget.md).

### Welches Spiel {#which-game}

Das Spiel wird aus `--game` genommen, dann aus dem Feld `game` einer `heat3d-lap`-Datei (oder aus
der `# {...}`-Beschreibungszeile einer CSV), und fällt sonst auf Forza zurück. Ein Ordner bekommt das
Spiel, das seine Dateien nennen, wenn sie nur eines nennen. Eine Datei, die keines nennt (eine
FH-Companion-Runde, `course.json`, eine CSV ohne Beschreibungszeile), zählt nicht (siehe
[Rundeneingaben](lap-inputs.md)).

| Wert | Ausgeführt von |
|---|---|
| beginnt mit `forza` | `heat3d-forza-maps course` |
| `beamng` | `heat3d-beamng-maps course` |
| `assetto-corsa-rally` oder `acrally` | `heat3d-acrally-maps course` |
| `assetto-corsa-evo` | abgelehnt: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | abgelehnt: "tracks ship in a protected format that is not a file-extraction target" |
| alles andere | abgelehnt: "there is no course reader for <game> yet" |

Eine Ablehnung nennt auch die Alternativen: die Strecke aus dem Spiel rekonstruieren (3DHeat
GameCapture) oder die Runden ohne Strecke analysieren, denn der Tab Rennanalyse des Viewers zeichnet
aus ihnen eine Straße.

## courses, races, cars, terrain (Forza) {#courses-races-cars-terrain-forza}

Ausgeführt von `heat3d-forza-maps` mit denselben Argumenten:
[seine Befehle](https://holdi601.github.io/3DHeat-Ext-Forza/commands.html).

## levels and level (Frostbite) {#levels-and-level-frostbite}

Ausgeführt von `heat3d-battlefield-maps` mit denselben Argumenten:
[Battlefield-Levels](https://holdi601.github.io/3DHeat-Ext-Battlefield/level-battlefield.html).

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
| `-o`, `--out FILE` | `<map>.glb` (in `$HEAT3D_LEVELS/<game>/`, wenn das gesetzt ist) | die zu schreibende `.glb` |
| `--ground-spacing METRES` | 2 | der Abstand der Landschafts-Vertices in der Datei, auf eine ganze Zahl eigener Quads gerundet |
| `--no-structures`, `--no-water` | | lässt diesen Teil weg |

Es gibt die Dreiecke pro Teil aus, wie viele Landschafts-Komponenten gelesen wurden und wie viele der
doppelt gespeicherten Vertices nicht übereinstimmen. Eine 3-km-Karte mit 2 m ergibt etwa 4,6 Millionen
Boden-Dreiecke.

## enfusion-worlds and enfusion-world (Arma Reforger) {#enfusion-worlds-and-enfusion-world-arma-reforger}

Ausgeführt von `heat3d-reforger-maps` mit denselben Argumenten (seine Befehle `worlds` und `world`):
[Arma-Reforger-Welten](https://holdi601.github.io/3DHeat-Ext-Reforger/level-arma-reforger.html).

## Umgebungsvariablen {#environment-variables}

| Variable | Wirkung |
|---|---|
| `HEAT3D_OODLE` | Pfad zu einer `oo2core_*_win64.dll` oder zu einem Ordner, der eine enthält; siehe [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | ein Ordner für jeden Export ohne `-o`: Die Exporte jedes Spiels landen in `<HEAT3D_LEVELS>/<game>/` (Strecken in `<game>/courses/`, das Autopaket in `forza/`). Ist sie nicht gesetzt, landen sie im aktuellen Ordner |
| `HEAT3D_FORZA_MAPS`, `HEAT3D_BATTLEFIELD_MAPS`, `HEAT3D_BEAMNG_MAPS`, `HEAT3D_ACRALLY_MAPS`, `HEAT3D_REFORGER_MAPS` | der Ordner eines Spielwerkzeugs, wenn es weder installiert noch neben GameFiles ist |
| `HEAT3D_NO_UPDATE` | jeder Wert außer leer, `0`, `false`, `no` schaltet die Update-Prüfung ab; siehe [Updates](updates.md) |
| `LOCALAPPDATA` | wo die FH-Companion-Bibliothek, BeamNGs Benutzerordner und der Update-Cache gesucht werden |
| `HEAT3D_COURSE` | nur für Tests: die Strecke, die der Test der installierten Bordsteine benutzt; siehe [Entwicklung](development.md) |
