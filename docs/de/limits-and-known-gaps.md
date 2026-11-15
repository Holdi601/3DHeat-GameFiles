---
title: Grenzen und bekannte Lücken
nav_order: 10
lang: de
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Grenzen und bekannte Lücken {#limits-and-known-gaps}

Was das Tool nicht tut, was es nur teilweise tut und wo sein Verhalten ungleichmäßig
ist. Die meisten Lücken sind bewusste Ablehnungen. Dekodieren ohne eine Datei zum
Prüfen erzeugt Ausgaben, die richtig aussehen und es nicht sind.

## Spiele {#games}

| Spiel | Kursexport | Warum nicht, oder wie weit |
|---|---|---|
| Forza Horizon | ja | die Bodenfarbe ist eine Deutung (siehe unten) |
| BeamNG.drive | ja | keine Bodenbedeckung, wiederholende Modelltexturen werden geglättet |
| Assetto Corsa Rally | ja | Modelle einfarbig; noch nicht an einer im Spiel aufgezeichneten Runde getestet |
| Assetto Corsa EVO | **nein** | alle Inhalte stehen in einem einzigen Paket, das mit einem Schlüssel verschleiert ist, und dieses Tool gewinnt keine Schlüssel |
| Battlefield 6 (Level-Export, `level`) | ja, ein ganzes Level | Gelände, gruppierte und einzeln platzierte Meshes und ihre Farbkarten, das Navigationsmesh der Soldaten, ausgeschnittene Vegetation; die Bodenfarbe des Spielbereichs ist grob (32 m pro Pixel oder eine Durchschnittsfarbe); keine Transparenz und keine Normal Maps; zerstörbare Meshes markiert, ihre zerstörten Zustände nicht exportiert |
| Unreal-5-Spiele mit World Partition (Kartenexport, `ue-map`) | ja, eine ganze Karte | die Landschaft genau; Gebäude als vereinfachte HLOD-Meshes der Karte, nicht als Modelle in voller Detailtiefe; Wasserkörper; kein Laub, keine Decals, keine Bodenfarbe |
| Arma Reforger (Welt-Export, `enfusion-world`) | ja, eine ganze Welt | Gelände in den eigenen Farben und das Meer; Gebäude, Requisiten und Felsen als Boxen ihrer Modelle, nicht als Dreiecke; Bäume auf Wunsch (`--trees`), als Boxen; keine Seen, Flüsse oder untergeordneten Entitäten |
| iRacing | **nein** | Strecken liegen in einem geschützten Format, das kein Ziel für das Extrahieren von Dateien ist |
| alles andere | **nein** | es gibt keinen Streckenleser; mit 3DHeat GameCapture aus dem Spiel rekonstruieren oder die Runden im Viewer im Tab Rennanalyse ohne Strecke auswerten |

## Engines und Formate {#engines-and-formats}

| Format | Nicht umgesetzt |
|---|---|
| Unreal `.pak` | Versionen vor 8; reine Pfad-Hash-Indizes (Namen können nicht zurückgewonnen werden); Einträge in der Überlaufliste des Indexes (übersprungen); das Dekodieren von `.uasset`/`.umap`-Inhalten aus einem Pak |
| Unreal IoStore | verschlüsselte Container (abgelehnt, keine Schlüsseloption); das Auflisten eines Containers ohne Verzeichnisindex (er nennt keine Dateien); versionierte Pakete; Meshes nur mit Nanite und nicht inline gespeicherte; Skinning-Meshes; Eigenschaften von Klassen ohne Schema; Eigenschaften instanzierter Komponenten (Layout in diesem Spielbuild geändert); Spline-Meshes und Decal-Komponenten |
| Unity | Formate vor 22 (Unity 2019 und älter); Dateien mit eingebetteten Typbäumen; komprimierte Meshes; jede Klasse außer `Mesh`, also keine Transformationen, Materialien oder Szenen; `meshes` auf einem Bundle; `list`/`extract` (stattdessen `meshes` verwenden) |
| Frostbite | XOR-verschleierte Tabellen; der Ebenengraph des Geländes (Masken werden nur in etwa einem Drittel der geprüften Level gelesen); Objektvorlagen außer Meshes (Spiellogik, Effekte, Töne); Mesh-Ebenen, die inline gespeichert sind; Normal Maps und andere Karten, Alpha außer Ausschnitten; Löcher im Gelände; die Typbibliothek (verschlüsselt im initialen Dateisystem, nicht angefasst); ein Befehl, um einzelne Assets aufzulisten oder zu extrahieren |
| Source 2 | kompilierte Assets (`.vmdl_c`, `.vtex_c`); das Navmesh von CS2 (Version 36) |
| ForzaTech | Positionsformate außer vier skalierten Shorts; Indexformate außer u16; Texturcodes außer 0, 9, 13; die Materialschichten des Geländeshaders; Tangenten |
| BeamNG | Skinning- und Decal-Meshes; Animation; prozedurale Bodenbedeckung; Szenerie am Rand der Welt |
| Unreal-Landschaften und World-Partition-Karten | Landschaften, deren Höhenkarten in den aufbereiteten Zellen liegen; Bearbeitungsebenen und Löcher; Landschafts-Meshes nur mit Nanite; Modelle in voller Detailtiefe in den Zellen; Laub; Landschaftsmaterialien |
| Enfusion | Modell-Dreiecke (die Geometrie von `.xob` ist in einem nicht gelesenen Layout komprimiert); `.edds` mit Kopfzeilen vor DX10; Werte verschachtelter Objekte in Weltdateien (übersprungen und gezählt); untergeordnete Entitäten; erzeugte Seen und Flüsse; `list`/`extract` auf einer `.pak` |

## Verhalten, das man kennen sollte {#behaviour-worth-knowing}

- **Die Bodenfarbe von Forza ist nicht die des Spiels.** Die eingebackene Textur wird
  aus den Kachelkarten gezeichnet, die sagen, *wo* Asphalt, kurzes Gras, rauher Boden
  und Wald liegen. Sie verwendet feste Farben und Schattierung, weil die
  Materialschichten des Geländeshaders nicht dekodiert werden.
- **`--no-textures` entfernt auch Forzas Seitenstreifen.** Die Trennung von Asphalt und
  Seitenstreifen verwendet die Asphaltmaske, die mit den gebackenen Karten kommt. Ohne
  Texturen bleiben Straßenstreifen als Fahrbahn ganz.
- **Ein Budget, das du vorgibst, kann nur durch Randsteine überschritten werden.**
  Randsteine (und die Modelle der Fahrfläche bei BeamNG) werden in keinem Spiel
  vereinfacht oder weggelassen. Ein `--detail-budget`, das kleiner ist als ihre Kosten,
  wird also allein durch sie überschritten; alles andere wird zuerst weggelassen. Siehe
  [Detailstufen und Budget](detail-budget.md).
- **Optionen, die nicht zutreffen, werden stillschweigend ignoriert:** `--season` bei
  BeamNG und AC Rally, `--track` bei BeamNG und AC Rally, `--level`/`--install` bei Forza.
- **Die Bodenfarbe eines Battlefield-6-Levels ist abseits seiner Decals grob.** Das
  Höhenfeld wird aus der Farbkarte des Geländehintergrunds gefärbt, mit 32 m pro Pixel
  auf der größten Mip-Stufe, die das Level mitbringt; oder, wo keine Hintergrundkarte
  es abdeckt, in der mittleren Farbe der Oberflächenmaterialien des Geländes.
  `--ground-texture` multipliziert das mit der Farbkarte des Geländes (bei 0,5 m pro
  Pixel, wo das Level eine hat) und backt Straßen, Vorfelder, Landebahnlinien,
  Reifenspuren und Markierungen darüber, in der Farbe ihrer Materialien, sofern eine
  gesetzt ist, und in einer neutralen Farbe, wo nicht; Straßen-Variationsmasken werden
  weggelassen. Das Spiel mischt seine Oberflächenschichten in einem Shader-Graphen, der
  nicht gelesen wird; der Export legt die Farben der Schichten nach ihren Masken und
  der Hangneigung des Höhenfeldes, nach einer eigenen Regel, und ein Level, dessen
  Maskenseiten nicht zusammenpassen, bekommt eine einzige Farbe. Jede Schicht ist der
  Mittelwert ihrer Farbkarte, nicht ihre Textur. Siehe
  [Frostbite](reader-frostbite.md#terrain-layers). Stücke des Höhenfeldes mit
  verschiedener Auflösung treffen sich mit kleinen Stufen.
- **Eine Farbkarte von Battlefield 6 wird ausgewählt, nicht gelesen.** Ein
  Shader-Block benennt jede Textur, die er abtastet, ohne zu sagen, welche die Farbe
  ist; die Wahl erfolgt nach dem Namen (siehe [Frostbite](reader-frostbite.md#textures-and-materials))
  und kann für eine Oberfläche ein Detail- oder Verzierungsblatt wählen. Decal-Blätter
  (`t_de_...`) verlieren gegen die eigene Karte der Oberfläche; das Decal eines Schildes,
  als seine Tafel gezeichnet, zeigte sein Wappen um ein Viertel gedreht. Distanzfelder,
  Paletten und Kanalmasken werden nie genommen. Hintergrundgebäude werden in den Farben
  ihrer Palette gezeichnet; graue Karten übernehmen die Tönung des Materials nach einer
  eigenen Regel des Exporters, da die Namen der Parameter gehasht sind; und ein Material,
  das eine graue Karte durch eine Maske mit mehreren Tönungen malt, bekommt eine davon.
- **Löcher im Gelände von Battlefield 6 werden nicht ausgeschnitten.** Wo der begehbare
  Boden eines Levels unter dem Höhenfeld liegt, muss das Spiel das Gelände
  ausgeschnitten haben, und der Export tut es nicht. Als Ort der Löcher ausgeschlossen
  sind: die Maskenschichten des Geländes (keine ist dort konzentriert), sein Raster aus
  67 x 67 Knoten, ein reservierter Höhenwert (keine Höhenseite enthält 0 oder 65.535),
  die Flags der Knoten (alle gleich) und Meshes oder Assets, die den Boden durchbrechen:
  Dort platziert sind Fels- und Klippenmeshes, und kein Asset des Levels ist für Löcher,
  Tunnel oder Höhlen benannt. Zwei Rastersbäume werden lauflängenkodiert gelesen, aber
  nicht platziert, und sie sind das, was übrig bleibt (siehe
  [Frostbite](reader-frostbite.md#terrain-layers)).
- **Eine Objektvariation von Battlefield 6 erreicht einen Abschnitt über seine
  Zwillinge.** Die Variation einer platzierten Kopie wählt die Shader-Blöcke ihrer
  Abschnitte über den Schlüssel; hat ein Mesh für eine Variation keinen Block, wird die
  Variante eines Abschnitts eines anderen Meshes mit einem identischen Standardblock
  genommen (siehe [Frostbite](reader-frostbite.md#textures-and-materials)). Das ist die
  Regel des Exporters; ein Abschnitt ohne variierenden Zwilling behält sein
  Standardaussehen.
- **Geschichtete Materialien von Battlefield 6 werden als ihre Basis und ein Blatt
  gezeichnet.** Eine Wandplatte mit Beschriftung wird als ihr Putz mit dem Buchstabenblatt
  darüber gezeichnet; die übrigen Schichten des Materials (Schmutz als Überlagerung über
  seine Maske, Detail- und Moosskarten) werden nicht eingemischt.
- **Das Navigationsmesh gehört den KI-Soldaten, nicht den Spielern.** Es deckt ab, wohin
  ein Soldat gehen kann: den Boden, Etagen und Treppen und einige Dächer, aber nicht jede
  hohe Stelle. Die Verbindungen zwischen Flächen (Sprünge, Leitern, Übersteigen) sind
  weggelassen.
- **Ein Battlefield-6-Level enthält die Ebene jedes Spielmodus.** Objekte, die nur ein
  Modus platziert, können sich mit denen eines anderen überschneiden. `--skip` lässt
  Ebenen nach Namen weg.
- **`courses` gibt es nur für Forza**, und es nimmt nur Bibliotheksordner auf, die
  `... (course_...)` heißen.
- **Das Bezugssystem der BeamNG-Runde wird angenommen**, nämlich das Bezugssystem des
  Viewers `(x, z, -y)`, das der 3DHeat-Recorder schreibt. Runden eines anderen
  Recorders im rohen Bezugssystem von BeamNG werden nicht platziert.
- **`list` und `extract` nehmen die Archive, nicht jedes Format.** Sie öffnen eine
  `.pak`, eine IoStore-`.utoc`, eine `.vpk`, eine `.minizip` und ein Zip. Ein
  Unity-Container wird mit `meshes` gelesen, ein Frostbite-Level mit `level`, und eine
  `.cdae` oder `.ter` ist eine Datei statt eines Archivs (`identify` benennt sie). Eine
  `.minizip` ohne `ChunkContentsMiniZip<n>.txt` daneben wird nach Eintragsnummer
  aufgelistet.
- **Platzierte Modelle in BeamNG verwenden wiederholende Texturen als Durchschnittsfarben**,
  weil der Sampler der `.glb` klemmt und der Viewer Texturen in einen Atlas packt.
- **In der Praxis nur Windows.** Steam-Pfade unter `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames` und eine `*_win64.dll` für Oodle. Andere
  Plattformen sind ungetestet.

## Ungeprüft {#unverified}

- Ältere Python-Versionen (das Tool wurde mit 3.13 ausgeführt).
- Assetto Corsa Rally mit einer im Spiel aufgezeichneten Runde. Es wurde nur mit
  synthetischen Runden in zufälligen Frames getestet.
- glTF-Viewer außer dem 3DHeat-Viewer.
- Ob das Bezugssystem jedes Spiels links- oder rechtshändig ist. Der Export behält das
  Telemetrie-Bezugssystem jedes Spiels bei, deshalb liegen Runden und Kurse in jedem
  Fall passend.
- Die Bedeutung von `WaterBlock`s lokalem z = 0 als seine Oberfläche (BeamNG).
- Frostbite-Platzierung in anderen Spielen als Battlefield 6, und in Battlefield 6 nach
  einem Update, das das Layout der Gruppenmitglieder ändert. Der Leser findet dann keine
  Gruppen und sagt es.
- Ob ein Battlefield-6-Export mit Positionen übereinstimmt, die das Spiel meldet. Die
  Koordinaten sind die eigenen des Spiels, wie bei den anderen Spielen, aber noch wurde
  keine Aufnahme darübergelegt.
