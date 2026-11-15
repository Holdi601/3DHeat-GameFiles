---
title: File di BeamNG
nav_order: 8
lang: "it"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# File di BeamNG: archivi di livello, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive distribuisce semplici archivi zip, quindi non c'è un contenitore da decodificare. Il lavoro sta nel
leggere un livello **nel modo in cui lo fa il gioco**: montare gli archivi in un unico file system, seguire i file
di scena, e decodificare il terreno e le forme compilate. Questi lettori vengono raggiunti dall'esportazione del
percorso di [BeamNG.drive](course-beamng.md). `identify` riconosce anche uno zip di livello, un `.cdae` e un
`.ter`, e `list` ed `extract` prendono qualsiasi zip.

Sorgenti: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Il file system montato {#the-mounted-file-system}

`Files.of_install(game)` costruisce un unico indice senza distinzione tra maiuscole e minuscole su
`gameengine.zip`, gli zip `content` (tranne veicoli e suoni) e le mod dell'utente (`mods\*.zip`,
`mods\unpacked\*` e una cartella `levels` dell'utente). Le aggiunte successive sovrascrivono le precedenti, come nel
gioco. Le ricerche ignorano le maiuscole perché i riferimenti dei livelli non concordano con gli archivi
(`.DAE` per un `.dae`). Dettagli su [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` trova un percorso come lo fa il gioco: così com'è, relativo al file che lo ha nominato, `x.png` come
`x.dds`, `x.dae` come `x.cdae` (preferito), e tramite un file JSON `x.png.link` il cui `path` punta dentro `/assets`.

## File di scena {#scene-files}

| Sorgente | Formato | Letto |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | un oggetto JSON per riga, oppure un unico array o mappa JSON | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | le stesse classi, per livelli più vecchi senza `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript o JSON | figli posizionati relativamente al prefab, fino a 8 livelli di profondità |
| `levels\<name>\forest\*.forest4.json` | un'istanza per riga | tipizzate dai record `TSForestItemData` in `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | il titolo del livello (le chiavi di traduzione vengono ignorate) |

**Trasformazioni.** `rotationMatrix` sono nove numeri le cui **righe** sono gli assi propri dell'oggetto nel mondo.
I segmenti di guardrail concatenati lungo una strada corrono lungo la riga 0 (92%), e la riga verso l'alto si inclina
con la pendenza della strada. I prefab più vecchi danno `rotation = "x y z degrees"`, una rotazione destrorsa di quel
angolo (il 92% delle catene di rotaia si allinea così, il 19% nel senso opposto). La scala moltiplica le righe, e
`position` (o `pos`) è l'ultima riga. La trasformazione di un figlio di prefab è composta con quella del prefab. Il
`groupPosition` del prefab è un perno dell'editor e **non** viene sottratto: un prefab di carrello poggia sul suolo solo
senza di esso.

I numeri di TorqueScript vengono letti con uno schema tollerante, perché alcuni prefab distribuiti scrivono valori come
`-0.99563-0.0` senza spazio.

## Terreno: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Altezza in metri: `position.z + h * maxHeight / 65535`, con `position`, `squareSize` e `maxHeight` dal `TerrainBlock`
  (predefiniti 0, 1 e 2048).
- Le righe corrono lungo +y. Il punto di griglia (i, j) è in
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Il livello 255 è un buco.

Verificato: i nodi stradali giacciono sul terreno entro 1-2 cm (mediana) su tre livelli. `h / 32`, o l'altro ordine
degli assi, sbaglia di decine o centinaia di metri.

## Materiali {#materials}

Ogni `*.materials.json` fuori da `levels\`, più quello del livello attuale, indicizzato per `mapTo`, `name` e chiave:

| Classe | Campi usati |
|---|---|
| `Material`, `CustomMaterial` | mappa colore (`baseColorMap`, `colorMap` o `diffuseMap`, primo stadio), fattore colore, mappa e fattore di opacità, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | mappa base e `diffuseSize`, mappa di dettaglio, dimensione e intensità, mappa macro, dimensione e intensità, `groundmodelName`, `annotation` |

Le immagini vengono decodificate con Pillow (DDS, PNG e così via), usando una bozza a dimensione ridotta dove possibile,
e memorizzate nella cache per dimensione. Una texture illeggibile ricade su un colore piatto.

## Forme compilate: `.cdae` {#compiled-shapes-cdae}

`.cdae` è la cache propria del gioco di ogni file Collada, scritta come MessagePack. Il suo layout è **documentato da
BeamNG** (documentation.beamng.com/modding/file_formats/cdae/) e il lettore lo segue:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Viene letto: limiti, nodi, oggetti, `details` (livelli di dettaglio), rotazioni predefinite dei nodi (`Quat16`) e
traslazioni, i vertici, le UV, le normali, i colori, le primitive e gli indici di ogni mesh, e i nomi dei materiali.
I nomi dei materiali si trovano alla fine del flusso, perché le sequenze di un oggetto animato vengono prima di essi in
una forma non documentata.

Due cose che la documentazione non spiega, stabilite confrontandole con i file `.dae` da cui le forme sono state
costruite:

- **Le rotazioni dei nodi sono quelle di Torque.** Un `Quat16` letto nel modo canonico ruota nel verso sbagliato. La sua
  matrice va **trasposta**. Con questo, i limiti mondiali di ogni nodo corrispondono al Collada fino al millimetro. Senza,
  sono fuori di 38 cm nella mediana.
- **Unità e assi sono già applicati.** Un file Collada creato in centimetri o con Y in alto esce dalla cache in metri, con
  Z in alto.

I livelli di dettaglio sono i `details` con una dimensione non negativa, il più grande per primo. Le dimensioni negative
sono mesh di collisione e di linea di vista, mai disegnate. Gli oggetti chiamati `colmesh`, `collision`, `los`, `bb_`,
`billboard`, `autobillboard` o `imposter` non vengono mai disegnati. Vengono disegnate solo le mesh standard e ordinate.
Le mesh con skinning (personaggi, veicoli) e le mesh decalcomania non vengono disegnate. Le strisce e i ventagli di triangoli
vengono srotolati, e le facce vengono riavvolte per concordare con le normali memorizzate, cosa che l'avvolgimento
proprio di Torque non garantisce.

Verificato: quasi ogni forma distribuita si legge. Le altre due sono di una versione più vecchia.

## Ripiego su Collada: `.dae` {#collada-fallback-dae}

Per le forme senza `.cdae` (mod, e qualche forma la cui cache è più vecchia), il file Collada viene letto nel modo in cui
l'importatore di Torque lo legge, nella stessa struttura:

- Livelli di dettaglio dalla convenzione di denominazione di Torque: il numero finale del nome di un nodo mesh è la
  dimensione in pixel da cui viene disegnato (`barrier75`, `barrier40`). Un numero negativo, o un nome `collision`/`Colmesh`/`LOS`/`nulldetail`,
  non viene mai disegnato. Una forma senza la convenzione ha un solo livello.
- Unità da `<unit meter>`, e Y in alto convertito in Z in alto.
- UV capovolte nella convenzione della cache (v scende nell'immagine).

Verificato contro il `.cdae` del gioco degli stessi file: quasi tutti i limiti campionati entro 1 cm, 583 con lo stesso
numero di triangoli, il 94% delle UV dei materiali identico. Il test sui giochi installati richiede che il 90% di fino a
60 coppie di forme dall'archivio di arte condiviso concordi entro 1 cm.

## Non letto {#not-read}

- Copertura del suolo (erba procedurale), e tutto ciò che viene generato a runtime.
- Sequenze animate e skinning.
- Veicoli e suoni (mai montati).
