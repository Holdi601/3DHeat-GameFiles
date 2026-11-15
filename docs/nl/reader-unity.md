---
title: Unity
nav_order: 4
lang: "nl"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, bundels, meshes {#unity-serializedfile-bundles-meshes}

**Toont objecten en decodeert meshes** van Unity `SerializedFile` formaat 22 en later (Unity 2020 tot en met 6000), en opent `UnityFS`-bundels. Er is geen Unity-baan-export.

Bronnen: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Commando's: `identify` (containers en bundels), `meshes` (alleen kale containers).

## De container {#the-container}

Unity levert een level als geserialiseerde objectgrafen: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*`, en asset-bundels. Elk bevat een tabel van objecten, gelabeld met een klasse-id.

De header is waar het lezen stilletjes misgaat. De eerste zestien bytes zijn vier big-endian `uint32`'s die om compatibiliteitsredenen bewaard worden. In formaat 22 zijn er drie nul, en de echte waarden volgen, omdat een bestand groter dan 4 GB kan zijn:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

De tweede `metadata size` is een `uint32` tussen twee `int64`'s. Als je alle drie 64-bit aanneemt, komt de versiestring vier bytes te laat. Die decodeert dan nog steeds tot iets dat op een string lijkt, en alles erna raakt verkeerd. De header is big-endian. Alles daarna volgt de endianness-byte (0, little-endian, op elke desktopbuild).

Na de header: de engineversiestring, het platform, de vlag voor de typeboom, de typetabel (klasse-id per type), de objecttabel (path id, offset, grootte, type), en de externe verwijzingen (andere bestanden waarnaar een pointer kan wijzen).

| Geval | Resultaat |
|---|---|
| formaat 22-30 | gelezen |
| formaat 9-21 (vóór Unity 2020) | geweigerd: de offsets staan in de oude header, en geen bestand dat ter beschikking stond gebruikte die |
| buiten 9-30 | geweigerd |
| typeboom ingebed (editorbuilds) | geweigerd: gewone builds bevatten er geen, en het editorpad is niet geïmplementeerd |
| een bundel waar een container verwacht wordt | geweigerd, met een verwijzing naar de bundellezer |

Er is **geen algemene deserialiser**. Gewone builds bevatten geen typeboom, omdat het schema in de speler is gecompileerd, dus elke klasse moet geparseerd worden tegen een indeling die voor zijn versie bekend is. Alleen `Mesh` wordt gedecodeerd. Andere klassen worden genoemd met naam en aantal (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`,
`Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; de rest als `class<id>`).

**Gecontroleerd** over veel geïnstalleerde spellen en miljoenen objecten: de objecttabel moet de datasectie precies vullen, zonder overlap, met niets anders tussen de objecten dan uitlijnvulling, en het laatste object eindigt op de laatste byte van het bestand. Een verkeerd gelezen header kan dat niet opleveren. De test op geïnstalleerde spellen herhaalt dat op maximaal zes `resources.assets`- / `sharedassets0.assets`-bestanden in `*_Data`-mappen.

## Bundels (`UnityFS`) {#bundles-unityfs}

Een bundel is een gecomprimeerde container van SerializedFiles. De blokkenlijst en de inhoudsopgave zijn ook gecomprimeerd. De methode zit in de laagste zes bits van een vlaggenwoord: 0 ongecomprimeerd, 1 LZMA (Unity's 5-byte header met de grootte ertussen), 2 en 3 LZ4 / LZ4HC. Formaat 7 en later lijnen de header uit op 16 bytes. Vlag `0x80` zet de inhoudsopgave aan het eind van het bestand. `UnityWeb`, `UnityRaw` en `UnityArchive` (vóór 5.3) worden herkend maar niet gelezen.

## Meshes {#meshes}

`read_mesh` decodeert een `Mesh`-object naar posities, normalen, de eerste UV-set en driehoeken, in de volgorde die Unity 2019+ schrijft: naam, submeshes, blend shapes (overgeslagen), bind poses en botdata (overgeslagen), de vlaggen voor compressie en leesbaarheid, de indexbuffer, de vertexkanalen en vertexdata, het gecomprimeerde meshblok, de lokale begrenzingsdoos, en de streaminginformatie.

- **Externe vertices.** De meeste meegeleverde geometrie zit in een `.resS`-bestand naast de container. De tool leest het uit de map van de container (alleen de bestandsnaam van het opgeslagen pad `archive:/...` wordt gebruikt). Een ontbrekende `.resS` is een fout, geen lege mesh.
- **Streams en kanalen.** Kanalen zeggen welke stream, offset, formaat en dimensie elk attribuut heeft. Streams staan na elkaar gepakt, elk opgevuld tot 16 bytes, dus het begin van een stream wordt opgeteld uit de strides ervoor. Formaten: float32, float16, unorm/snorm 8 en 16 (genormaliseerd), en gewone gehele getallen.
- **Topologie.** Alleen driehoeken (topologie 0). Strips, vierhoeken en lijnen worden geweigerd, omdat een verkeerde conversie eruitziet als echte geometrie.
- **Gecomprimeerde meshes** (gekwantiseerde delta's) worden geweigerd: `mesh '...' is stored compressed; that encoding is not implemented`.

### De zelfcontrole {#the-self-check}

Een struct in de verkeerde volgorde lezen geeft geen fout. Het levert plausibele getallen op. Daarom wordt elke gedecodeerde mesh gecontroleerd tegen de **begrenzingsdoos die Unity voor hem heeft opgeslagen**, door de editor berekend uit de echte vertices. `aabb_matches()` slaagt wanneer de hoeken van de gedecodeerde doos binnen 2% van de grootte van de opgeslagen doos liggen. `meshes` drukt op elke regel `ok` of `BOUNDS DISAGREE` af.

**Gecontroleerd:** meshes gesampled uit meerdere spellen decoderen met kloppende begrenzingen. De test op geïnstalleerde spellen herhaalt de controle op de geïnstalleerde containers.

## Niet geïmplementeerd {#not-implemented}

- Formaten van vóór 2020.
- Gecomprimeerde meshes.
- Elke klasse behalve `Mesh`: geen scènegraaf, transformaties of materialen, dus meshes staan in hun eigen lokale ruimte.
- `meshes` op een bundel. De bundellezer bestaat in Python (`UnityBundle.serialized_files()`), maar het commando neemt een kale container.
