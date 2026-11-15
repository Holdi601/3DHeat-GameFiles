---
title: Fehlerbehebung
nav_order: 11
lang: de
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Fehlerbehebung {#troubleshooting}

Die Meldungen, die das Tool ausgibt, wenn etwas es anhält, was jede bedeutet und was zu tun
ist. Meldungen sind aus dem Code zitiert, Platzhalter stehen in spitzen Klammern.

## Bevor das Tool überhaupt startet {#before-the-tool-even-starts}

| Sie sehen | Tun Sie |
|---|---|
| `'python' is not recognized` | Python 3.10 oder neuer installieren und „Add python.exe to PATH" ankreuzen; ein neues Terminal öffnen ([Bevor Sie anfangen](before-you-start.md)) |
| `No module named heat3d_gamefiles` | das Terminal steht im falschen Ordner: `cd` in den Ordner mit `README.md` |
| `No module named numpy` (oder ein anderes Paket) | `pip install -r requirements.txt` ausführen |
| ein Pfad mit Leerzeichen wird abgeschnitten, oder `unrecognized arguments` | den Pfad in doppelte Anführungszeichen setzen: `"C:\My Games\lap.json"` |

## Das Spiel finden {#finding-the-game}

| Meldung | Bedeutung | Tun |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | keine Steam-Bibliothek und kein `C:\XboxGames` enthält ein Spiel mit `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | die Koordinaten der Runde liegen auf keiner installierten Strecke | prüfen, ob die Runde aus diesem Spiel stammt; `--track` übergeben, wenn die Strecke woanders liegt |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | Kacheln gibt es in der Nähe der Box, aber keine im Korridor | wie oben |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | der Ordner hat keine `.utoc`, die sich öffnen lässt | `--install` auf den Ordner mit den `.utoc`-Dateien richten |

## Den Ort finden {#finding-the-place}

| Meldung | Bedeutung | Tun |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: kein Level erreichte 30 % | `--level <name>`; prüfen, ob die Runde im Bezugssystem des Viewers ist |
| `no level called '<name>'; installed: ...` | BeamNG: `--level` passte nicht | einen der aufgelisteten Ordnernamen verwenden |
| `<level> has no scene (no main/*.level.json and no .mis)` | der Levelordner hat keine Szenendateien | ein beschädigtes oder unvollständiges Level oder Mod |
| `no terrain of <level> lies along the driving.` | BeamNG: der Korridor hat keine Geländefelder | falsches Level, oder ein Level ohne Gelände dort, wo die Runde liegt |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: keine Etappe und Ausrichtung erreichte 50 % | `--level <stage>`; prüfen, ob die Positionen der Runde Meter mit Y nach oben sind |
| `no stage called '<name>'; there are: ...` | AC Rally: `--level` passte nicht | einen der aufgelisteten Namen verwenden |
| `no ground of <stage> lies along the driving.` | AC Rally: keine Bodenkachel im Korridor | falsche Etappe |

## Die Runde {#the-lap}

| Meldung | Tun |
|---|---|
| `<file> is not a lap this can read. ...` | eine unterstützte Form angeben, siehe [Rundeneingaben](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | das JSON ist keine Runde |
| `<file> has no x, y and z columns` | die CSV-Spalten `x`, `y`, `z` nennen |
| `'<name>' is not a file, and no course in <library> matches it` | den Namen prüfen, oder eine Datei übergeben |
| `'<name>' matches 3 courses: ...` | einen längeren Teil des Namens verwenden |
| `<name> holds no driving` | die Runde hat weniger als zwei Punkte |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` braucht eine Route-JSON mit `bounds`, so wie `heat3d_capture route` und `laps` sie schreiben; eine Rundendatei gehört zu `course` |
| `give exactly one of --box and --route` | `terrain` braucht genau eine Region |
| `no course export for this lap: <reason>.` | das Spiel wird nicht unterstützt, siehe [Grenzen und bekannte Lücken](limits-and-known-gaps.md) |

## Archive {#archives}

| Meldung | Bedeutung |
|---|---|
| `no Oodle library found. ...` | `HEAT3D_OODLE` setzen, siehe [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | ein verschlüsseltes Pak: `--key <hex>`, wenn Sie den Schlüssel besitzen. Einen anderen Weg gibt es nicht |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | der Schlüssel sind 32 Byte, als 64 Hexadezimalziffern geschrieben, `0x` optional (Exit-Code 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | es ist keines davon; `identify` sagt, was es ist. Ein Unity-Container nimmt `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | ein verschlüsselter IoStore-Container. Er kann nicht gelesen werden |
| `pak version <n>; this reader handles 8-12` | ein älteres oder neueres Pak-Format |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | aus Python: die `.utoc` versuchen, die `list` und `extract` ebenfalls nehmen |
| `<file> has no directory index, so its chunks carry no names to list` | ein IoStore-Container, der keine Dateien nennt; seine Chunks sind nur über andere Pakete erreichbar |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | die `ChunkContentsMiniZip<n>.txt` neben dem Archiv stammt von einem anderen Build oder einem anderen Archiv; ohne sie werden die Einträge nach Nummer aufgelistet |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | die Namen wurden beim Bau gehasht |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | eine Frostbite-Tabelle in der verschleierten Form |
| `no Frostbite game found in a Steam library; give --install` | `levels` oder `level` fand kein Steam-Spiel, dessen `Data` ein `layout.toc` hat; den Spielordner übergeben |
| `no level called '<name>'; did you mean one of ...?` | der Name passte auf keine Level-Tabelle, oder auf mehrere; `levels` listet sie auf |
| `nothing was placed: no static model group was recognised` | die Gruppenmitglieder des Levels haben eine andere Typsignatur, nach einem Spielupdate oder in einem anderen Frostbite-Spiel; das Layout muss neu gemessen werden |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | ein komprimiertes Unity-Mesh |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | die `.resS` neben der `.assets` behalten |
| `<file>: format <n> predates Unity 2020 ...` | ein älterer Unity-Build |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` nimmt einen nackten Container |
| `texture format <n> has not been identified; refusing to guess` | ein Forza-Musterformat, das noch nicht gesehen wurde |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | die Teile einer geteilten VPK zusammenhalten |

## Exporte, die falsch herauskommen {#exports-that-come-out-wrong}

| Symptom | Wahrscheinliche Ursache |
|---|---|
| der Kurs ist im Viewer gegenüber der Runde verschoben | Runde und Export nutzen verschiedene Bezugssysteme: `--game` prüfen (zum Beispiel eine BeamNG-Runde, als Forza gelesen) |
| kein Seitenstreifen bei einem Forza-Kurs | `--no-textures`, oder die Kachel hatte für diese `--season` keine Karten (die Konsole sagt `N without maps`) |
| eine Forza-Kachel in einfarbigen Flächen | ihre Bodenkarten fehlen für die Jahreszeit |
| weit weniger platzierte Objekte als erwartet | ein ausdrücklich angegebenes `--detail-budget` ist zu klein; die Zusammenfassung sagt, wie viele Kopien fehlen |
| die Datei ist sehr groß (hunderte MB) | ein Stadtkorridor unter dem automatischen Budget; `--detail-budget`, `--texture-size 1024` oder `--margin 40` verwenden |
| Zäune fehlen | durchsichtige Flächen werden absichtlich weggelassen (die Zusammenfassung nennt sie) |
| `N meshes could not be read` | einige Modelle verwenden ein Format, das der Leser ablehnt; der Rest wird trotzdem exportiert |
| `N of M components could not be read` (AC Rally) | ein Spielpatch hat die Eigenschaftsplätze möglicherweise verschoben; bitte melden |
