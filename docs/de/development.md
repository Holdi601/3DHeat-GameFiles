---
title: Entwicklung
nav_order: 14
lang: "de"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Entwicklung {#development}

## Aufbau {#layout}

```
heat3d_gamefiles/     das Paket: Leser, Streckenexporte, die Befehlszeile
heat3d_update/        die Prüfung auf Releases und der Updater (siehe Updates)
tests/                synthetische Tests, Testdaten und Tests gegen installierte Spiele
docs/                 diese Dokumentation (docs/wiki wird daraus erzeugt)
VERSION               die installierte Version, verglichen mit den GitHub-Releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Modulübersicht {#module-map}

| Modul | Was es tut |
|---|---|
| `__main__.py` | führt die Update-Prüfung aus, dann `cli.main()` |
| `cli.py` | die Befehle, `identify`, die Weiterleitung nach Archiv, der Forza-Streckenschreiber |
| `lapinput.py` | jede Form einer Runde in Positionen; Suche in der FH-Companion-Bibliothek |
| `corridor.py` | das Band links und rechts der Fahrt, als 4-m-Raster |
| `surfaces.py` | die Bodenarten, ihre Teilnamen und Farben |
| `glb.py` | der `.glb`-Schreiber (Teile, Normalen, Farben, Texturen, Quantisierung) |
| `courseexport.py` | Forza: ebene Kachel-UVs, Trennung von Straße und Seitenstreifen, Bodenbacken, Anheben der Decals |
| `forzainstall.py` | Steam- und Xbox-Bibliotheken; zu welcher Forza-Strecke eine Box gehört |
| `minizip.py` | ForzaTech-`.minizip`-Archive und ihre Namenslisten |
| `forzatech.py` | `.modelbin`: Chunks, Puffer, Layouts, Teilmeshes, Materialien |
| `forzaterrain.py` | Geländekacheln nach Ort; Oberflächenklassen |
| `forzatexture.py` | `.pb`-Muster; Kachelkarten; das Bodenbacken |
| `forzamaterial.py` | `AssetManifest.xml`; welche Texturfarben ein Modell hat; Jahreszeiten |
| `forzaplacement.py` | `.pgeo`-Platzierungen, Modellstufen, Texturen, Ausschnitte, Stellvertreter, das Budget |
| `beamng.py` | BeamNG-Installation, eingebundenes Dateisystem, Szene, Gelände, Materialien |
| `beamngcourse.py` | der BeamNG-Streckenexport |
| `beamngshape.py` | `.cdae`-kompilierte Formen |
| `beamngcollada.py` | `.dae`-Ersatz |
| `acrally.py` | AC-Rally-Installation, Etappen, Platzierung von Komponenten, Virtual-Textur-Volumen |
| `acrallycourse.py` | der AC-Rally-Streckenexport: Anpassung der Ausrichtung, Boden, Platzierung |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 aufbereitete Pakete |
| `unversioned.py` | Schemata und Leser für Eigenschaften ohne Versionsangabe |
| `unrealmesh.py` | aufbereitete statische Meshes |
| `unrealtexture.py` | Texturen und gestreamte Virtual Textures |
| `oodle.py` | Suche und Aufruf einer Oodle-Bibliothek auf dem Rechner |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-Container, Bundles, Meshes |
| `frostbite.py` | Frostbite-`.toc`, Abschnittstabellen, Installationspakete, Chunk-Positionen, Nutzdaten |
| `frostbitebundle.py` | Frostbite-Inline-Bundles, Bundle-Manifeste, der Katalog einer Ebene, die Ebenenliste |
| `frostbiteebx.py` | Frostbite-RIFF-EBX-Partitionen ohne Typbibliothek |
| `frostbitemesh.py` | Frostbite-MeshSet und seine Chunks der Detailstufen |
| `frostbiteterrain.py` | Frostbite-Streaming-Baum des Geländes, Höhenseiten, das Bodenmesh |
| `frostbitematerial.py` | Frostbite-Texturen (BC1/BC3/BC7-Mips), Shader-Block-Depots, Wahl der Farbkarte |
| `frostbitedecals.py` | Frostbite-Gelände-Decals und das Bodenbacken |
| `frostbitenav.py` | Frostbite-Navigationsmesh-Kacheln: die begehbaren Flächen der Soldaten |
| `frostbitelevel.py` | Frostbite-statische Modellgruppen, Platzierung, der `level`-Export |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal-5-Landschaftskomponenten: Höhenkarten im Bodenmesh (`ue-map`) |
| `unreallevel.py` | Unreal-5-World-Partition-Karten: Auflistung, HLOD-Strukturen, Wasser, der `ue-map`-Export |
| `enfusion.py` | Enfusion-`.pak`, `.edds`, Geländekacheln, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma-Reforger-Welten: `.ent`-Dateien, Boxen, der `enfusion-world`-Export |
| `forzacars.py` | jedes Forza-Auto in niedriger Detailstufe nach `.h3dcars` (`cars`) |

Alle Module stehen auf GitHub unter
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Die Tests ausführen {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` setzt `testpaths = tests` und `-q`. Zwei Arten von Tests sind wichtig,
aus verschiedenen Gründen:

- **Synthetische Tests** bauen Archive Byte für Byte und laufen überall. Sie legen
  die Feldlayouts fest, die zu irgendeinem Zeitpunkt falsch waren: die 64-Bit-Basis
  des `.minizip`-Segments und ihr Auffüllen auf die Ausrichtung, der Block-Größen-Escape
  des Pak, das u32 im Unity-Header zwischen zwei int64, der `0x7FFF`-Index des VPK,
  die geteilte x-Komponente der Forza-Normale.
- **Tests mit installierten Spielen** laufen gegen die echten Dateien, wenn das Spiel
  auf dem Rechner liegt, und **werden übersprungen** (sie schlagen nicht fehl), wenn
  es nicht da ist. Nur sie fangen ein Layout ab, das für eine kleine Datei richtig und
  für eine große falsch ist.

### Testdaten {#fixtures}

| Testdaten | Erzeugt |
|---|---|
| `tests/forza_fixtures.py` | `.minizip`-Archive (mit der 64-Bit-Basis, Auffüllung, gemischten Codecs), Manifeste, `.modelbin`-Modelle und Gelände, `.pb`-Muster |
| `tests/beamng_fixtures.py` | eine kleine BeamNG-Installation: `gameengine.zip`, `content`, eine Ebenen-Zip mit einem 64-m-Gelände, ein Asphaltstreifen, ein Straßen-Decal, eine Schiene, ein Prefab, ein Waldelement, das Meer, Materialien und `.cdae`-Formen im dokumentierten Layout |
| `tests/unreal_fixtures.py` | ein IoStore-Container mit einem Verzeichnis, ein Zen-Paket, ein Block mit Eigenschaften ohne Versionsangabe |
| `tests/frostbite_fixtures.py` | Frostbite-Tabellen, Bundles, EBX-Partitionen, Meshes und Geländeseiten, Byte für Byte |

### Testdateien {#test-files}

| Datei | Prüft |
|---|---|
| `test_minizip.py` | Rücklesen, die 64-Bit-Basis, gerade und ungerade Bundle-Tabellen, Ablehnungen, die Namensdatei |
| `test_forzatech.py` | die Chunk-Tabelle und -Kette, Ablehnungen; installiert: die Ketten und Tags echter Modelle |
| `test_forza_geometry.py` | Weltplatzierung, Vertex-Layout, abgelehnte Formate, Teilmeshes, Normalen und UVs |
| `test_forzaterrain.py` | das Kachelraster (1023 gegen 512 m), Beschneiden, Extraktion |
| `test_forzatexture.py` | Kopfzeile der Muster, Dekodierung, das Texturregal, das Bodenbacken |
| `test_forzamaterial.py` | das Manifest, Namen, Materialhashes, die Farbwahl, Jahreszeiten |
| `test_forzaplacement.py` | der `.pgeo`-Datensatz, Platzieren von Kopien, Stufen, Varianten, durchsichtige Flächen, eine ganze Box, das Budget, die Platzhalterfarbe, das automatische Budget; installiert: Randsteine auf dem Boden |
| `test_forzainstall.py` | Suche des Spiels, Wahl der Strecke |
| `test_courseexport.py` | Kachel-UVs, der Teilplan, das Anheben von Decals |
| `test_course_cli.py` | die ganzen Befehle `course` und `courses` auf einer synthetischen Strecke; `terrain --route` mit Byte-Order-Mark und ohne `bounds` |
| `test_archive_cli.py` | `identify`, `list` und `extract` auf jedem Archiv mit Leser (`.pak`, IoStore, `.vpk`, `.minizip` mit und ohne Namen, Zip, `.cdae`, `.ter`); Fehler als eine Zeile und ein Exit-Code: ein verschlüsseltes Pak, ein verschlüsselter Container, eine Datei, die kein Archiv ist, ein falscher `--key` |
| `test_corridor.py` | das Band, Schneiden von Gelände mit dem Band |
| `test_lapinput.py` | jede Form einer Runde, die Box, Fehler, die Suche nach dem Streckennamen, welches Spiel ein Ordner ist |
| `test_surfaces.py` | welche Namen über die Oberfläche entscheiden und welche nicht, Teilnamen |
| `test_glb.py` | die Datei ist gültig, Knoten tragen die Klasse, Ablehnungen, Quantisierung |
| `test_beamng.py` | Formen, die Ebene, Kategorien, das Finden der Ebene aus einer Runde, die Strecke, der Collada-Ersatz; installiert: `.cdae` gegen `.dae`, jede Ebene öffnet sich |
| `test_acrally.py` | Container, Pakete, Eigenschaften, Transformationen, die Anpassung der Ausrichtung, Teile platzierter Modelle und das Budget, Virtual Textures; installiert: Etappen und die eingebackene Bodenfarbe |
| `test_pak.py` | Footer, Einträge, der Block-Größen-Escape, Ablehnungen; installiert: Offsets und SHA-1 |
| `test_unity.py` | Ablehnungen; installiert: die Objekttabelle füllt die Datei, Versionszeichenketten, Mesh-Grenzen |
| `test_frostbite.py` | signierte gegen verschleierte Header, Ablehnungen, Installationspakete (zwei Pakete mit derselben Blobnummer); installiert: jede Tabelle, Superbundles, Abschnittsketten, eindeutige IDs, Stichproben der Nutzdaten aus dem richtigen Paket |
| `test_frostbitelevel.py` | Chunk-IDs mit ihren eigenen Positionen gepaart, Inline-Bundles, Manifeste, ein MeshSet mit Schattenabschnitt und UVs, ein Gruppenmitglied, die Transformationskonvention, ein zweistufiges Gelände, Wahl der Farbkarte, ein Texturchunk ohne die größten Mips, der wiederholende Sampler, Decal-Datensätze, ein Decal, das über seinen Alphakanal zusammengesetzt wird, ein Decal-Blatt, das gegen die eigene Karte einer Oberfläche verliert, Materialien mit Decals, Fahrbahnlinien und Reifenspuren gezeichnet, einkanalige Karten dekodiert, zerstörbare Meshes in ihren Teilen und Extras markiert, Blockout-, Zwischensequenz- und Lichtmeshes weggelassen und ein Farbkarten-Layout, das nicht gelesen wird, ausgeschnittene Karten und ihre Masken, zweiseitige PNG-Materialien, Hintergrundkacheln nach ihrem Mesh benannt; installiert: die Gelände-Decals der Ebene, der Katalog der größten Ebene, Meshes innerhalb ihrer Grenzen, Gruppenmitglieder, Vegetation auf dem dekodierten Gelände |
| `test_vpk.py` | das Verzeichnis, Ablehnungen, geteilte Archive; installiert: Karten öffnen sich, CRCs stimmen, das Navmesh |
| `test_enfusion.py` | Enfusion-`.pak`, `.edds`, Geländekacheln und Weltdateien; der `enfusion-world`-Export |
| `test_forzacars.py` | die `.h3dcars`-Datei, die der Befehl `cars` schreibt |
| `test_unreallevel.py` | Unreal-5-Landschaften, HLOD-Strukturen, Wasser; der `ue-map`-Export |

## Tests mit installierten Spielen {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
findet Spiele für die Tests. `steam_common()` listet das Verzeichnis
`steamapps\common` jeder Steam-Bibliothek (einschließlich der Ordner von Steam selbst),
und `installed(*globs)` gibt die Pfade zurück, die einem der Muster darunter
entsprechen, rekursiv, wo ein Muster `**` hat. Jeder Test entscheidet selbst, was er
braucht:

| Test | Sucht nach | Wird übersprungen mit |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` mit einem **unverschlüsselten** Index, bis zu 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` in `*/*_Data` oder `*/*/*_Data`, die der Leser annimmt, bis zu 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, bis zu 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | die Rundenbibliothek der FH Companion für Rundstrecken (Start und Ziel innerhalb von 50 m), mit den meisten Runden, die `find_track` platziert; oder `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Nur die Tests eines Spiels ausführen, oder den Forza-Randstein-Test auf eine Strecke richten:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Tests mit installierten Spielen lesen nur aus den Spielen. Sie schreiben nichts in
Spielordner. Testausgaben landen in den temporären Ordnern von pytest.

## Konventionen {#conventions}

- **Ablehnen statt raten.** Jeder Leser löst seine eigene Ausnahme aus
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError` ...) mit
  einer Meldung, die sagt, was gefunden wurde und warum es nicht gelesen wurde.
- **Gegen das Format selbst prüfen.** Ein Hash, eine CRC, eine Kette von Offsets, eine
  gespeicherte Bounding Box, die Fahrt, die auf dem Boden liegt. Nicht „es ist nicht
  abgestürzt".
- **Keine Schlüssel, kein mitgelieferter proprietärer Code.** Siehe
  [Regeln und Lizenzen](rules-and-licences.md).
- **Vertrauliche Daten bleiben draußen.** Spieldateien, Exporte, Runden, Aufnahmen und
  Screenshots gelangen nie ins Repository. `.gitignore` schließt sie nach Ordner und
  nach Dateityp aus. Tests verwenden synthetische Daten und installierte Spiele, nie
  eingecheckte Spielinhalte.
