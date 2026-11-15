---
title: Archivleser
nav_order: 9
lang: de
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Archivleser {#archive-readers}

Ein **Container** (oder Archiv) ist eine große Datei, in die ein Spiel viele
Dateien packt. Eine **CRC** oder ein Hash ist ein kurzer Fingerabdruck einiger
Bytes: Wenn er stimmt, wurden die Bytes richtig gelesen. Eine **Bounding Box**
ist die kleinste Box um ein Modell.

Unter den Befehlen liegen Leser für die Container, die Spiele ausliefern. Ihre
Formate sind nicht dokumentiert, außer Valves VPK und BeamNGs `.cdae`. Deshalb
heißt „unterstützt" hier **an echten Dateien geprüft**, nicht „ist nicht
abgestürzt". Jeder Leser prüft sich selbst gegen etwas, das das Format garantiert:
einen Hash, eine CRC, eine Kette von Offsets, die sich schließen muss, eine
gespeicherte Bounding Box. Schlägt eine Prüfung fehl, verweigert der Leser die
Arbeit mit einer Meldung, statt zu raten. Ein falsches Netz sieht aus wie ein
richtiges, bis man es neben die Strecke stellt.

| Leser | Modul | Liest | Liest nicht | Wird aufgerufen von |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | Versionen 8-12: Index, Einträge, Zlib-, Gzip- und Oodle-Blöcke, AES mit einem Schlüssel, den Sie angeben | Versionen vor 8, reine Pfad-Hash-Indizes, Einträge in der Überlaufliste des Indexes, Inhalte der Assets | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (ab v5, an v8 geprüft), Zen-Pakete, Eigenschaften ohne Versionsangabe für einige Komponentenklassen, fertig aufbereitete statische Meshes, Texturen, Streaming-Virtual-Textures | verschlüsselte Container, versionierte Pakete, Meshes nur mit Nanite, Eigenschaften anderer Klassen | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle-Blöcke über eine Bibliothek, die schon auf dem Rechner liegt | alles ohne eine solche Bibliothek; sie wird nie mitgeliefert | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` ab Format 22 (Unity 2020 bis 6000), `UnityFS`-Bundles, unkomprimierte Meshes einschließlich `.resS` | Formate vor 2020, eingebettete Typbäume, komprimierte Meshes, jede Klasse außer `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc`-DbObject-Bäume und binäre Abschnittstabellen, Installationspakete, Chunk-Positionen, Inline-Bundles und ihre Manifeste, RIFF-EBX-Partitionen, MeshSet-Meshes, das Höhenfeld des Geländes, BC1/BC3/BC7-Texturen und ihre Shader-Blöcke, Platzierung statischer Modellgruppen | XOR-verschleierte Tabellen, die bodennahe Farbe des Geländes und seine Löcher, Normal Maps, Alpha außer Ausschnitten | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | Versionen 1 und 2, geteilte Archive, Preload-Daten, CRC-Prüfung | kompilierte Assets (`.vmdl_c`, `.vtex_c`), das Format des CS2-Navmeshs | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, Deflate, unkomprimiert), `.modelbin`-Geometrie, `.pb`-Muster (BC1, BC7, RGBA), `.pgeo`-Platzierungen, Hashes der Materialtexturen | andere Vertex- und Index-Formate, andere Texturformate, Materialschichten des Geländeshaders | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` und `extract` (`.minizip`) |
| [BeamNG-Dateien](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | das eingebundene Zip-Dateisystem, Szenen-JSON und TorqueScript, `.ter`, `.cdae` v31, Collada-`.dae`, Materialien | Skinning-Meshes und Decal-Meshes, animierte Sequenzen, prozedurale Bodenbedeckung | `course` (BeamNG), `identify` (Zips, `.cdae`, `.ter`), `list` und `extract` (Zips) |

## Regeln, an die sich jeder Leser hält {#rules-every-reader-follows}

- **Keine Schlüssel mitgeliefert, keine ermittelt.** Ein verschlüsseltes Archiv
  öffnet sich nur mit einem Schlüssel, den Sie übergeben (Unreal `.pak`, `--key`).
  Ein verschlüsselter IoStore-Container wird abgelehnt. Nichts durchsucht eine
  ausführbare Datei nach einem Schlüssel, und nichts liest den Speicher eines
  anderen Prozesses. Siehe [Regeln und Lizenzen](rules-and-licences.md).
- **Kein proprietärer Code mitgeliefert.** Oodle wird aus einem Spiel oder einer
  Engine geladen, die schon auf dem Rechner installiert ist.
- **Ablehnen statt raten.** Eine unbekannte Version, ein unbekannter Codec, ein
  unbekanntes Vertex- oder Texturformat löst einen bestimmten Fehler aus, zum
  Beispiel `texture format 42 has not been identified; refusing to guess`.
- **Nur lesend.** Kein Leser schreibt in einen Spielordner. Exporte landen dort,
  wo Sie es angeben.

## Was „geprüft" bedeutet {#what-verified-meant}

Die Prüfwerte, die auf diesen Seiten genannt werden, stammen aus den
Dokumentationstexten der Module (Docstrings). Sie wurden an installierten
Spielen gemessen, während jeder Leser geschrieben wurde. Die synthetischen Tests
(siehe [Entwicklung](development.md)) legen die Feldlayouts fest. Die Tests mit
installierten Spielen wiederholen einige Prüfungen, wenn das Spiel auf dem
Rechner liegt, und werden sonst übersprungen. Werte, die von keinem Test
abgedeckt sind, wurden seitdem nicht erneut geprüft.
