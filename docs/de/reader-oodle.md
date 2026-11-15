---
title: Oodle
nav_order: 3
lang: de
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: gefunden, nicht mitgeliefert {#oodle-found-not-bundled}

Die meisten ausgelieferten Unreal-Inhalte und einige Frostbite-Nutzdaten sind mit **Oodle** komprimiert (RAD Game Tools, heute Epic). Oodle ist proprietär. Es gibt kein frei weitergebbares Build und keine Python-Umsetzung, und `oo2core_*.dll` gehört dem Produkt, das sie ausliefert. Deshalb **findet dieses Werkzeug eine Kopie, die schon auf deinem Rechner liegt, und lädt sie**. Es liefert nie eine eigene mit. FModel und UModel arbeiten genauso.

Quelle: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Wo gesucht wird {#where-it-looks}

Die erste Datei, die existiert, gewinnt, in dieser Reihenfolge:

1. Ein ausdrücklicher Pfad, den der Aufrufer übergibt (Python-API).
2. `HEAT3D_OODLE`: ein Pfad zur DLL oder zu einem Ordner, der eine enthält.
3. Eine flache Suche, eine Ebene tief, in
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - dem Ordner `steamapps\common` jeder Steam-Bibliothek

   Für jeden Unterordner `<game>` prüft es `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` und `<game>\Engine\Binaries\Win64`.

Versuchte Dateinamen, neueste zuerst: `oo2core_9_win64.dll` bis `oo2core_3_win64.dll`. Das Format ist abwärtskompatibel, deshalb funktioniert eine ältere Bibliothek meist noch.

Die Suche ist bewusst **kein** rekursives Durchsuchen aller Laufwerke, das Minuten dauern würde. Wenn sie nichts findet, setze `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Ein Ordner funktioniert genauso gut wie die Datei selbst: Die DLL-Namen von oben werden darin versucht.

Eine Installation der Unreal Engine enthält eine unter `Engine\Binaries\ThirdParty\Oodle`, das ist für Entwickler die sauberste Quelle. Viele Spiele legen eine neben ihre ausführbare Datei. Unreal-5-Spiele binden Oodle oft statisch ein und liefern keine DLL aus, daher kann die gefundene Kopie zu einem anderen Spiel gehören als das Archiv, das gelesen wird. Das Format ist in beiden Fällen dasselbe.

## Wie es aufgerufen wird {#how-it-is-called}

`OodleLZ_Decompress` wird über `ctypes` aufgerufen, mit der erwarteten Ausgabelänge (der Archivindex kennt sie immer, Oodle kann sie nicht erraten), mit fehlertoleranter Dekodierung an (die Eingabe ist nicht vertrauenswürdig), ohne CRC-Prüfung (die SHA-1 des Pak deckt die Bytes bereits ab) und ohne Threads. Ein Ergebnis mit falscher Länge ist ein Fehler. Die Bibliothek wird einmal je Lauf geladen.

## Wenn keine vorhanden ist {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Ein Eintrag, der sich nicht dekomprimieren lässt, ist ein Fehler, nie ein glaubwürdiger Müll.

Der Lader funktioniert nur unter Windows (er sucht nach `*_win64.dll`). Bibliotheken für Linux und macOS werden nicht gesucht.
