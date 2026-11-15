---
title: Unreal .pak
nav_order: 1
lang: "de"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Listet und entpackt** Unreal-4.22-5.x-`.pak`-Archive: Versionen 8, 9, 10, 11 und 12,
Zlib-, Gzip- und Oodle-Komprimierung, und verschlüsselte Archive, wenn du den AES-Schlüssel
angeben. Was entpackt wird (`.uasset`, `.umap`), wird nicht interpretiert.

Quelle: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Befehle: `identify`, `list`, `extract` (siehe [Befehle](commands.md)).

## Aufbau {#layout}

Der Footer steht am Ende der Datei und wird gefunden, indem die letzten 1.024 Byte nach dem
Magic `0x5A6F12E1` durchsucht werden. Seine Feldreihenfolge ist wichtig:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Das Verschlüsselungs-Flag steht **vor** dem Magic. Liest man es nach dem Magic, landet man
auf dem „Z" von „Zlib". Dann meldet sich jedes Archiv als verschlüsselt, und jeder
Methodenname verliert den ersten Buchstaben („lib", „odle"), ein stiller und plausibler
Fehler. Die Version ist das niedrigste Byte, weil „frozen index"-Builds ein hohes Bit setzen.

Der Index enthält den Mount-Punkt, den Pfad-Hash-Index, den vollständigen Verzeichnisindex
und einen Block mit **kodierten Einträgen**: eine bitgepackte Form, in der ein Flag-Wort
angibt, welche Zahlen 32 Bit haben, die Komprimierungsmethode (6 Bit), ob der Eintrag
verschlüsselt ist, die Blockanzahl (16 Bit) und die Blockgröße in Einheiten von 2.048 (6 Bit).
Die Blockgröße aus lauter Einsen ist ein Escape: Die echte Größe folgt als u32 **vor** dem
Offset. In einem großen Archiv verschob das Lesen nach den Größen 7 % der Einträge um vier
Byte und gab ihnen Offsets in den Exabyte-Bereich.

Der vollständige Datensatz jedes Eintrags wiederholt sich direkt vor seiner Nutzlast, daher
beginnt die Nutzlast nach `8+8+8+20+4+1+4` Byte, zuzüglich `4 + 16 x blocks` bei
komprimierten Einträgen. Verschlüsselte Blöcke werden auf 16 Byte aufgefüllt.

## Was gelesen und was abgelehnt wird {#what-it-reads-and-what-it-refuses}

| Fall | Ergebnis |
|---|---|
| Versionen 8-12 | gelesen |
| jede andere Version | `pak version N; this reader handles 8-12` (ältere Versionen speichern eine flache Datensatzliste, und es gab keine Datei zum Prüfen) |
| kein Footer-Magic | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| Index außerhalb der Datei | abgelehnt: der Footer ließ sich nicht wie behauptet lesen |
| nur Pfad-Hash-Index | abgelehnt: Dateinamen wurden beim Bau gehasht und lassen sich nicht zurückgewinnen |
| Einträge in der Überlaufliste des Index (Verzeichnisoffset -1) | übersprungen, nicht erfunden |
| verschlüsselter Index, kein Schlüssel | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." In der Befehlszeile eine Zeile und Exit-Code 1 |
| verschlüsselter Eintrag, kein Schlüssel | `EncryptedPak` beim Lesen |
| Methoden Zlib, Gzip, Oodle | entpackt (Oodle braucht eine Bibliothek, siehe [Oodle](reader-oodle.md)) |
| jede andere Methode | `compression method '...' is not supported` |

## Schlüssel {#keys}

`--key` bei `list` und `extract` nimmt einen AES-256-Schlüssel, den du schon besitzt, als
64 Hexadezimalziffern, mit oder ohne `0x`. Alles andere wird abgelehnt, bevor das Archiv
geöffnet wird, mit Exit-Code 2. Entschlüsselt wird mit AES-256-ECB über das Paket
`cryptography`. Es gibt keinen Codepfad, der einen Schlüssel beschafft: keine mitgelieferten
Schlüssel, keine Suche in ausführbaren Dateien, kein Speicherauslesen. Siehe
[Regeln und Lizenzen](rules-and-licences.md).

## Geprüft {#verified}

An ausgelieferten Archiven mehrerer Spiele stimmte jeder Eintrag, auch in einem sehr großen
Archiv, mit dem SHA-1 überein, den Unreal vor jeder Nutzlast schreibt. Dieser Hash umfasst
die Bytes, wie sie gespeichert sind. Ein Treffer heißt also, dass die Dekodierung des Index,
der Offset der Nutzlast und jede Blockgrenze der Komprimierung richtig waren. Die Tests mit
installiertem Spiel (`test_pak.py`) wiederholen das an bis zu vier unverschlüsselten Paks, die
unter `steamapps\common\*\...\Content\Paks` gefunden werden. Sie prüfen, dass der Offset jedes
Eintrags innerhalb der Datei liegt, und dass der SHA-1 für eine zufällige Stichprobe von 150
Einträgen pro Archiv stimmt.
