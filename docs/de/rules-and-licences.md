---
title: Regeln und Lizenzen
nav_order: 12
lang: "de"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Regeln und Lizenzen {#rules-and-licences}

Drei Regeln prägen das ganze Tool. Volltext:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Keine Schlüssel: keine mitgeliefert, keine ermittelt {#no-keys-none-shipped-none-recovered}

**Es liest Container.** Ein Archivformat zu parsen ist gewöhnliche Dateiverarbeitung, und
FModel, UModel und AssetRipper tun das seit Jahren offen.

**Die entscheidende Grenze ist die Verschlüsselung, und sie ist im Tool selbst gezogen.**

- **Keine mitgelieferten Schlüssel.** Im Code und in den Daten steht kein Schlüssel.
- **Keine Schlüsselermittlung.** Nichts durchsucht eine ausführbare Datei nach einem
  Schlüssel, und nichts liest den Speicher eines anderen Prozesses.
- **Ein Schlüssel, den du besitzt, oder keiner.** Ein verschlüsseltes Unreal-`.pak` öffnet
  sich nur mit `--key <hex>` (in Python `PakArchive(path, aes_key=...)`). `pak.py` hat keinen
  Codepfad, der einen Schlüssel beschafft. Ein verschlüsselter IoStore-Container wird
  kategorisch abgelehnt.
- **Verschleierung ist ebenfalls nicht umgesetzt.** Die XOR-verschleierten Tabellen von
  Frostbite halten ihren Schlüssel in der Datei selbst, deshalb sind sie Verschleierung und
  keine Zugangskontrolle. Sie werden trotzdem erkannt und abgelehnt, weil keine vorliegende
  Datei diese Form nutzt und es nichts gäbe, woran man eine Umsetzung prüfen könnte.
  Der verschlüsselte Schlüsselpaket-Stand von Assetto Corsa EVO wird aus demselben Grund
  abgelehnt, aus dem die Schlüsselregel gilt.
- **Verschlüsselte Dateien bleiben verschlossen.** Das initiale Dateisystem von Battlefield 6,
  das die Typbibliothek des Spiels enthält, ist verschlüsselt und wird nicht gelesen. Der
  Level-Export arbeitet mit den Dateien, die nicht verschlüsselt sind, und legt die zwei Typen,
  die er braucht, aus den Daten selbst an.
- **Nichts wird in einen Spielprozess eingeschleust.** Telemetrie kommt aus Datenquellen, die
  die Spiele selbst veröffentlichen, und die Aufnahme nutzt öffentliche Bildschirm-
  aufnahme-APIs (in den anderen 3DHeat-Tools). Einschleusen in einen Titel mit Anti-Cheat
  gefährdet das Konto dessen, der es ausführt.

Jedes bisher getestete Archiv war unverschlüsselt.

## 2. Ihre eigenen Dateien {#your-own-files}

Das Tool liest die Spieldateien, die **auf deinem Rechner installiert** sind. Es lädt nie
Spielinhalte herunter.

Nichts aus einem Spiel wird mitgeliefert: keine Spielinhalte, kein Spielcode, keine DLLs. Was
es exportiert, wird auf deine Festplatte geschrieben und sonst nirgendwohin.

3DHeat GameFiles ist mit keinem Spieleherausgeber verbunden und wird von keinem unterstützt.
Die Spiele und die zugehörigen Namen und Marken gehören ihren Inhabern. Rechteinhaber: Bitte
eröffnet ein Issue unter
[github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) -
wir antworten schnell und entfernen auf Anfrage alles.

## 3. Die Ausgabe ist nicht zur Weitergabe bestimmt {#output-is-not-for-redistribution}

Was herauskommt, ist Geometrie für **räumlichen Kontext**: der Boden, die Straße und was
daneben steht, auf ein Budget reduziert, damit Runden an Ort und Stelle analysiert werden
können. Es ist das Geringste, was ein Archiv enthält, und es ist trotzdem der Inhalt des
Spielherausgebers.

- Behalte exportierte `.glb`-Dateien und die Texturen darin für deine eigene Analyse.
- Veröffentlichen, teilen oder verkaufe exportierte Strecken, Level, Modelle oder Texturen
  nicht.
- Die `.gitignore` des Repositorys hält Spieldateien, Exporte, Runden und Aufnahmen nach Ordner
  und Dateityp aus der Versionskontrolle heraus (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`,
  `*.png`, `*.lap.json` und mehr).

## Oodle wird gefunden, nicht mitgeliefert {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, heute Epic) ist proprietär und hat keinen weitergabefähigen Build.
`oo2core_*.dll` ist an das Produkt lizenziert, das sie ausliefert. `oodle.py` lädt deshalb
eine Bibliothek, die schon auf dem Rechner liegt, statt eine mitzuführen. Das ist die
Anordnung, die die Lizenz vorsieht, dieselbe, die FModel und UModel verwenden. Siehe
[Oodle](reader-oodle.md).

## Die Formate selbst {#the-formats-themselves}

- `.pak`, IoStore, Unitys `SerializedFile`, Frostbites `.toc` und ForzaTechs Formate sind
  nicht dokumentiert. Keiner der
  Leser hier ist aus dem Quelltext eines anderen Projekts abgeleitet. Für Frostbite lieferten
  öffentliche Beschreibungen älterer Versionen (die Frosty-Modding-Werkzeuge, eine
  Formatnotiz zu Need for Speed Heat, ein GDC-Vortrag) Feldnamen und eine Liste dessen, wonach
  zu suchen ist. Kein Code wurde übernommen; jeder Offset wurde an den Dateien gemessen (siehe
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Extrahierte Level sind für deinen eigenen Gebrauch bestimmt. Das Tool schreibt sie auf deine
  Festplatte und sonst nirgendwohin; veröffentliche sie nicht.
- BeamNG veröffentlicht sein `.cdae`-Layout, und der Leser folgt ihm.
- Valve dokumentiert VPK.
- Die aufbereiteten Eigenschaftsdaten von Unreal 5 brauchen die Eigenschaftsliste jeder Klasse.
  Die Listen in `unversioned.py` enthalten **nur Namen und Typen**, Tatsachen über das Format,
  wie eine Interoperabilitäts-Zuordnungsdatei sie enthält. Sie wurden aus den Unreal-Engine-
  Headern abgeleitet, die Epic jedem mit verknüpftem Konto zur Verfügung stellt, und an den
  ausgelieferten Daten geprüft. Kein Engine-Quelltext ist enthalten oder nötig.

## Die Lizenz dieses Tools {#this-tools-licence}

Alles, was für dieses Repository geschrieben wurde, steht unter der **MIT-Lizenz**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): nutzen,
ändern, ausliefern, kommerziell oder nicht.

Fremdpakete, alle freizügig, sodass der Exporter selbst keine eigene Einschränkung trägt:

| Paket | Lizenz | Verwendet für |
|---|---|---|
| numpy | BSD-3-Clause | Dekodierung von Meshes |
| cryptography | Apache-2.0 / BSD-3-Clause | nur Archive, für die du einen Schlüssel besitzt |
| lz4 | BSD-3-Clause | Forza-Archive, einige Unity-Bundles, IoStore-LZ4-Blöcke |
| Pillow | MIT-CMU (HPND) | blockkomprimierte Texturen, JPEG-Ausgabe |
| msgpack | Apache-2.0 | BeamNG-`.cdae` |
| zstandard | BSD-3-Clause | die wenigen zstd-komprimierten `.cdae`, Frostbite-zstd-Blöcke |
| pytest | MIT | nur für die Entwicklung |

Die Lizenzen wurden im September 2026 aus den Paketmetadaten gelesen. Wo sich die
Bedingungen einer Komponente danach geändert haben, zählt die Quelle.
