---
title: Source 2 `.vpk`
nav_order: 6
lang: de
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Listet und entpackt** die VPK-Archive von Valve, Versionen 1 und 2, einschließlich geteilter Archive und Daten, die in der Verzeichnisdatei liegen. Jeder Eintrag lässt sich mit seiner eigenen CRC prüfen. Dies ist das einzige Containerformat hier, dessen Hersteller es dokumentiert. Spiele: Counter-Strike 2, Dota 2, Half-Life: Alyx und andere auf Source 2.

Quelle: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Befehle: `identify`, `list`, `extract`.

## Aufbau {#layout}

```
u32 magic 0x55AA1234, u32 version (1 or 2), u32 tree size
  (version 2: 16 more header bytes; header 12 or 28 bytes)
directory tree:
  extension        "vmdl_c", then "vtex_c", ..., then ""
    path           "maps/example_map", then ""
      file name    "world_layer0", then ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Drei ineinander liegende Schleifen, die jeweils mit einer leeren Zeichenkette enden, sodass ein Leser, der eine Anzahl erwartet, keine findet. Pfade werden je Gruppe einmal gespeichert und aus allen drei Teilen wieder zusammengesetzt. Ein einzelnes Leerzeichen bedeutet „kein Ordner“ oder „keine Endung“.
- Jeder Datensatz endet mit `0xFFFF`. Das wird geprüft, sodass ein Leser, der seine Position verloren hat, sofort anhält („the directory is not being read at the right offset“).
- **Geteilte Archive:** `pak01_dir.vpk` enthält das Verzeichnis, und die Daten liegen in `pak01_000.vpk`, `pak01_001.vpk` ... und werden über den Archivindex des Eintrags ausgewählt.
- **Archivindex `0x7FFF`** bedeutet, dass die Bytes in der Verzeichnisdatei selbst liegen, nach dem Baum. Liest ein Leser das als echten Index, sucht er `pak01_32767.vpk`.
- **Preload:** Kleine Dateien werden ganz im Verzeichnis gespeichert. Eine Länge von 0 ist dann kein Fehler.

## Befehle {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` gibt die Version, die Anzahl der Einträge und die erste `.nav`-Datei aus. `list` zeigt jeden Eintrag als `stored`, weil VPK nicht komprimiert. `extract` schreibt die Bytes ohne CRC-Prüfung. In Python vergleicht `VpkArchive(path).verify(name)` die Bytes eines Eintrags mit der CRC, die das Verzeichnis gespeichert hat.

## Das Navigationsnetz {#the-navigation-mesh}

Eine Karte liefert ihr **Navigationsnetz** (`maps/<map>.nav`) neben der kompilierten Geometrie mit. Für eine Heatmap von Spielerpositionen ist es mit großem Abstand das nützlichere der beiden, denn das Navigationsnetz *ist* der begehbare Boden, schon berechnet, und ein Tausendstel so groß. Der Test mit installiertem Spiel prüft, dass die `.nav` einer ausgelieferten Karte mit der Source-Navigationskennung `CE FA ED FE` beginnt.

## Geprüft {#verified}

Jeder Eintrag, der aus den ausgelieferten Kartenarchiven eines Spiels stichprobenartig gezogen wurde, kam Byte für Byte passend zu seiner CRC zurück, und jedes Kartenarchiv lässt sich lesen. Die Tests mit installiertem Spiel wiederholen die CRC-Prüfung an 25 zufälligen Einträgen aus jedem von bis zu vier Kartenarchiven.

## Nicht umgesetzt {#not-implemented}

- Das Decodieren der kompilierten Assets von Source 2 (`.vmdl_c`, `.vtex_c`). Es sind eigene chunk-basierte Binärdateien, dieselbe Art Aufgabe wie die Mesh-Formate von Unreal und Frostbite. Das separate CS2-Werkzeug von 3DHeat übernimmt die Geometrie der CS2-Karten.
- Das Decodieren des CS2-Navigationsnetzes. Sein Format ist Version 36 und unterscheidet sich von dem, das für Source 1 weithin dokumentiert ist. Seine Bytes sind strukturiert statt komprimiert (Entropie 6,2, 31 % Nullen), aber nur 3 % seiner Wörter lesen sich als Koordinaten. Das Layout ist also nicht das naheliegende und ist noch nicht herausgefunden.
