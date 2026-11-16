---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "de"
source: reader-unreal-iostore.md
source_hash: "a71af3169c83"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 liefert den größten Teil seiner Inhalte in **IoStore**-Containern aus: einer
`.utoc`-Inhaltstabelle und den `.ucas`-Daten, die sie indiziert. Eine `.pak` gibt es
weiterhin, aber sie enthält kaum mehr als einen Footer. Die Leser hier gehen vom Container
bis hinunter zu Geometrie und Pixeln, soweit eine Strecke es braucht. Sie wurden an
Assetto Corsa Rally (Unreal 5.6.1, verändert) gebaut und geprüft und werden über den
Streckenexport von [Assetto Corsa Rally](https://holdi601.github.io/3DHeat-Ext-ACRally/course-assetto-corsa-rally.html) aufgerufen. `identify`,
`list` und `extract` nehmen eine `.utoc` (oder die `.ucas` daneben): die Dateien, die ihr
Verzeichnis nennt, unter ihrem Pfad unterhalb des Einhängepunkts. Ein Container ohne
Verzeichnisindex nennt keine Dateien und wird nicht aufgelistet.

| Schicht | Modul |
|---|---|
| Container und Speicher | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| aufbereitete „Zen"-Pakete | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| Eigenschaften ohne Versionsangabe | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| statische Meshes | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| Texturen und Virtual Textures | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Container (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Die Inhaltstabelle, Version 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Versionen vor 5 werden abgelehnt. Nur Version 8 wurde an echten Dateien geprüft.
- **Verschlüsselte Container werden abgelehnt**: "<file> is encrypted. This tool holds no
  keys and recovers none." Für IoStore gibt es keine Schlüsseloption.
- Blockmethoden: stored, `oodle` (über [Oodle](reader-oodle.md)), `zlib`, `lz4`. Alles
  andere wird abgelehnt.
- Partitionen ab der zweiten liegen in `<name>_s<n>.ucas`.

Der **Speicher** öffnet jede `.utoc` im `Paks`-Ordner des Spiels und indiziert jeden
Paketpfad, ohne Beachtung von Groß- und Kleinschreibung. Container, die sich nicht öffnen
lassen, werden übersprungen. `global.utoc` liefert die Skriptobjekte (C++-Klassen). Die
Bulk-Daten (`.ubulk`) eines Pakets werden als der Chunk mit derselben ID und dem Typ
`BULK_DATA` gefunden, in welchem Container er auch liegt.

**Geprüft:** jeder Container des installierten Spiels und jeder Paketpfad darin.

## Zen-Pakete {#zen-packages}

Ein aufbereitetes Paket ist ein Kopf (Namen, Importe, Exporte, Exportbündel,
Abhängigkeitstabellen, importierte Paketnamen), gefolgt von den serialisierten Daten jedes
Exports. Objekte verweisen aufeinander über einen 64-Bit-`FPackageObjectIndex`, dessen
oberste zwei Bit angeben, was er ist: ein Export dieses Pakets, ein Skriptobjekt, ein Import
aus einem anderen Paket (welches Paket, und der Export über einen Hash seines Pfads) oder null.

- Das Layout der Zusammenfassung änderte sich in 5.3 (Abhängigkeitsbündel und importierte
  Paketnamen) und erneut in 5.6 (zwei weitere Offsets). Beide Layouts werden versucht, und
  das, dessen Namentabelle sich parsen lässt, wird behalten, sodass die Version nicht
  bekannt sein muss.
- **Versionierte** (unaufbereitete) Pakete werden abgelehnt.
- Importierte Paketnamen tragen eine Nummer. Ein Paket `_Terrain` mit Nummer 1 ist die
  Datei `_Terrain_0`.
- `/Game/...`-Namen werden im Speicher auf den `Content`-Ordner des Projekts abgebildet.
- Verweise über Pakete hinweg werden durch Abgleich des öffentlichen Hashes des Exports
  verfolgt.

**Geprüft:** jede Zelle jeder Etappe öffnet sich.

## Eigenschaften ohne Versionsangabe {#unversioned-properties}

Aufbereitete Unreal-5-Exporte benennen ihre Eigenschaften nicht. Ein Export beginnt mit
einem Kopf aus Läufen, „überspringe so viele Plätze, dann so viele vorhandene", und einer
Maske, die angibt, welche vorhandenen Werte null sind und keine Bytes tragen. Die Werte
folgen in der Eigenschaftsreihenfolge der Klasse. Dafür braucht man das **Schema** jeder
Klasse: ihre Eigenschaftsliste, in genau der Reihenfolge, die die Engine aufbaut (zuerst die
eigenen Eigenschaften, dann die des Elternteils, ein Platz je Element eines statischen
Arrays, Eigenschaften nur für den Editor weggelassen).

Schemata sind für die Klassen eingebettet, die eine Strecke braucht:

| Klasse | Kette |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | die ISM-Ketten (vorhanden, aber vom Streckenexport nicht verwendet, weil dieser Build sie umgebaut hat) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Sie decken auch die Strukturen ab, die diese halten (`FBodyInstance`, Kollisionsantworten
und andere). Wertetypen werden nach ihrer Kodierung gelesen: feste Zahlen und Vektoren
(`FVector`, `FRotator` als Doubles, `FTransform` ...), `FName`, Aufzählungen (ein Byte),
Objektverweise (`i32`-Paketindex), Soft-Objektpfade, Arrays, verschachtelte Strukturen und
Multicast-Delegates (übersprungen).

Die Schemata enthalten **nur Eigenschaftsnamen und -typen**, abgeleitet aus den Headern von
Unreal Engine 5.6.1, die Epic jedem mit einem verknüpften Konto zur Verfügung stellt. Kein
Engine-Code ist enthalten. Dieser Build hat **zwei Plätze mehr in `UPrimitiveComponent`** als
die Header, und **einen mehr im Virtual-Textur-Volumen**, aus den Daten ermittelt und als
`(unknown)` markiert. Ein Wert, der in einem dieser Plätze steht, ist ein Fehler, keine
Vermutung. Ein Platz hinter dem Ende eines Schemas oder ein unbekannter Typ löst
`PropertyError` aus.

**Geprüft:** jede statische Mesh- und Szenenkomponente jeder Etappe wird dekodiert, und jede
endet genau am festen nativen Ende ihrer Klasse. Ein Patch des Spiels kann Plätze
verschieben. Der Leser bricht dann ab, und die Strecke meldet, wie viele Komponenten
fehlschlugen.

## Statische Meshes {#static-meshes}

Ein `UStaticMesh`-Export besteht aus seinen Eigenschaften, gefolgt von nativen Daten. Die
Eigenschaften braucht man für die Geometrie nicht, und sie werden nicht gelesen. Der native
Teil wird über seinen festen Anfang gefunden: ein Null-GUID-Flag, zwei Byte Streifen-Flags,
`bCooked = 1` und der Index des eigenen `BodySetup`-Exports des Meshes. Gelesen wird er in
der Reihenfolge, in der `UStaticMesh::Serialize` und `FStaticMeshRenderData::Serialize` ihn
für ein **aufbereitetes, nicht-Nanite** Mesh schreiben:

- bis zu 16 Detailstufen, jede mit ihren Abschnitten (Material, erster Index, Anzahl der
  Dreiecke), Grenzen und, wenn **inline**: der Positionspuffer (float32 x 3), Tangenten,
  UVs (alle Kanäle, halbe oder volle Genauigkeit), Farben und der Indexpuffer (16 oder
  32 Bit);
- was folgt (umgekehrte und reine Tiefen-Indexpuffer, Daten für Raytracing,
  flächengewichtete Sampler), wird überschritten, um die nächste Stufe zu erreichen.

Eine Stufe, die nicht inline gespeichert ist, beendet die Liste. Ein Mesh ohne solche Stufe
wird abgelehnt. Positionen sind Unreals: Zentimeter, X nach vorn, Y nach rechts, Z nach oben.

**Geprüft:** fast jedes stichprobenartig geprüfte Mesh wird dekodiert (der Rest sind
Skinning-Meshes), und die dekodierte Ausdehnung einer Fahrbahnkachel stimmt mit den
gespeicherten Grenzen überein.

## Texturen {#textures}

Ein `Texture2D`-Export besteht aus seinen Eigenschaften und dann seinen aufbereiteten
Plattformdaten: dem Namen des Pixelformats, der Größe und einer Tabelle von Mip-Stufen, die
jeweils auf die **Bulk-Datenkarte** des Pakets zeigen (Offset, Größe, Flags; im Export selbst,
wenn das Flag `0x40` gesetzt ist, sonst in der `.ubulk`). Die Plattformdaten werden über ihre
eigene Form gefunden, nicht durch Überspringen der Eigenschaften, sodass das Eigenschafts-
Layout der Texturklasse keine Rolle spielt. Die erste Mip-Stufe, die nicht größer als die
gewünschte Größe ist, wird dekodiert.

| Unreal-Format | Dekodiert als |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | 8-Bit-RGBA |
| `PF_G8` | 8-Bit-Graustufen |

**Geprüft:** ein Satellitenbild, 4096 px, DXT5, dessen dreizehn Stufen genau den Größen der
Bulk-Einträge entsprechen.

## Gestreamte Virtual Textures {#streaming-virtual-textures}

Eine eingebackene `VirtualTexture2D` besteht aus quadratischen Kacheln mit Rand, je
Detailstufe, adressiert über einen **Morton-Code** (x in den geraden Bits), gespeichert in
Chunks der Bulk-Daten des Pakets. Das Layout wird so gelesen, wie
`FVirtualTextureBuiltData::Serialize` es in Unreal 5.6 schreibt: Schichten, Kachelgröße, Rand,
Adresstabellen je Mip-Stufe, Formate der Schichten, und Chunk *n* ist Bulk-Eintrag *n*. Ein
Bereich der Textur wird Kachel für Kachel zusammengesetzt, Ränder entfernt, aus der Stufe, deren
Auflösung der gewünschten Größe am nächsten ist. Nur die erste Schicht wird gelesen, und nur
in den oben genannten Formaten.

**Geprüft:** Die Kacheln eines Virtual-Textur-Chunks sind bis aufs Byte erfasst.
