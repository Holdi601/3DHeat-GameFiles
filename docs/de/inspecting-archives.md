---
title: Archive untersuchen
nav_order: 3
lang: "de"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Archive untersuchen: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Ein Spiel packt seine Dateien in große Kisten, die **Archive** heißen. Diese Befehle lesen das Etikett einer Kiste, listen auf, was darin liegt, und holen eine Sache heraus.

Bevor du etwas aus einem unbekannten Spiel exportierst, schau dir an, was es mitliefert. Diese vier Befehle lesen eine Datei und sagen dir, was sie ist und was sie enthält. Sie schreiben nichts außer dem einen Eintrag, den du mit `extract` anforderst.

![identify, list and extract run on a small zip](../assets/img/inspect-archives.svg)

*Ein Lauf auf einer künstlichen ZIP-Datei, aufgebaut wie ein Level von BeamNG.drive.*

## Schritt für Schritt {#step-by-step}

1. **Frage, was die Datei ist.** `identify` liest die Bytes, nicht die Dateiendung:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Es nennt das Format (Unreal-`.pak`, IoStore-`.utoc`/`.ucas`, Unity-Bundle oder `SerializedFile`, Frostbite-`.toc`, Source-2-`.vpk`, ForzaTech-`.minizip` oder `.modelbin`, BeamNG-`.cdae`/`.ter`, ZIP), seine Version, wie viele Einträge es enthält und ob es verschlüsselt ist.

2. **Liste den Inhalt auf.** `list` gibt eine Zeile je Eintrag aus: Größe, Komprimierung, Pfad. Grenze es mit `--filter` ein und begrenze die Anzahl mit `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Hole einen Eintrag heraus.** `extract` schreibt einen Eintrag (in den Ordner, in dem du gerade bist, sofern `--out` nichts anderes sagt), und zwar über den Pfad, den `list` ausgegeben hat (oder über `#12`, die Nummer, bei einem `.minizip` ohne Namen):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` listet die Meshes in einem `SerializedFile` auf und prüft sie:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Optionen {#options}

| Befehl | Option | Bedeutung |
|---|---|---|
| `identify` | `<file>` | jede Datei |
| `list` | `<archive>` | `.pak`, `.utoc` (oder die `.ucas` daneben), `.vpk`, `.minizip`, ZIP |
| | `--filter TEXT` | nur Pfade, die TEXT enthalten |
| | `--limit N` | höchstens N Zeilen |
| | `--key HEX` | ein AES-256-Schlüssel (64 Hex-Ziffern), den du schon hast; nur eine verschlüsselte `.pak` braucht ihn |
| `extract` | `<archive> <path>` | das Archiv und der Pfad des Eintrags, so wie `list` ihn ausgibt |
| | `--out FILE` | wohin er geschrieben wird (Standard: der Dateiname des Eintrags) |
| | `--key HEX` | wie bei `list` |
| `meshes` | `<file>`, `--limit N` | ein Unity-`SerializedFile`; höchstens N Meshes |

Das Werkzeug liefert keine Schlüssel mit und findet keine. Ein verschlüsseltes Archiv öffnet sich nur mit einem Schlüssel, den du angibst. Eine Datei, die es nicht lesen kann, wird in einer Zeile mit Exit-Code 1 abgelehnt. Jeder Befehl und jeder Exit-Code steht auf [Befehle](commands.md). Wie jedes Format gelesen wird, steht unter [Archiv-Leser](archive-readers.md).
