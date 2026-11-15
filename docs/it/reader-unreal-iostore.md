---
title: Unreal 5 IoStore
nav_order: 2
lang: "it"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Unreal 5 distribuisce la maggior parte dei contenuti in contenitori **IoStore**: un indice dei contenuti `.utoc` e i dati
`.ucas` che esso indicizza. Un `.pak` c'è ancora, ma contiene poco più di un footer. I lettori qui vanno dal contenitore
fino a geometria e pixel, nella misura in cui serve a un percorso. Sono stati costruiti e verificati su Assetto Corsa Rally
(Unreal 5.6.1, modificato) e vengono raggiunti tramite l'esportazione del percorso di
[Assetto Corsa Rally](course-assetto-corsa-rally.md). `identify`, `list` ed `extract` prendono un `.utoc` (o il `.ucas` accanto
ad esso): i file che la sua directory nomina, con il loro percorso sotto il punto di montaggio. Un contenitore senza indice di
directory non nomina file e non viene elencato.

| Livello | Modulo |
|---|---|
| contenitori e archivio | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| pacchetti cotti "zen" | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| dati di proprietà non versionati | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| mesh statiche | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| texture e texture virtuali | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Contenitori (`.utoc`, `.ucas`) {#containers-utoc-ucas}

L'indice dei contenuti, versione 8 (Unreal 5.6), little-endian:

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

- Le versioni precedenti alla 5 vengono rifiutate. Solo la versione 8 è stata verificata su file reali.
- **I contenitori cifrati vengono rifiutati**: "<file> is encrypted. This tool holds no keys and recovers none." Per IoStore
  non si può passare nessuna chiave.
- Metodi dei blocchi: memorizzato, `oodle` (tramite [Oodle](reader-oodle.md)), `zlib`, `lz4`. Qualsiasi altro viene rifiutato.
- Le partizioni oltre la prima vivono in `<name>_s<n>.ucas`.

Lo **store** apre ogni `.utoc` nella cartella `Paks` del gioco e indicizza ogni percorso di pacchetto, senza distinguere
maiuscole e minuscole. I contenitori che non si aprono vengono saltati. `global.utoc` fornisce gli oggetti di script (le
classi C++). I dati bulk di un pacchetto (`.ubulk`) si trovano come il chunk con lo stesso id e tipo `BULK_DATA`, in
qualunque contenitore lo contenga.

Verificato: ogni contenitore del gioco installato e ogni percorso di pacchetto al suo interno.

## Pacchetti zen {#zen-packages}

Un pacchetto cotto è un'intestazione (nomi, import, export, bundle di export, tabelle delle dipendenze, nomi di pacchetti
importati) seguita dai dati serializzati di ogni export. Gli oggetti si riferiscono l'uno all'altro tramite un
`FPackageObjectIndex` a 64 bit i cui due bit più alti dicono che cos'è: un export di questo pacchetto, un oggetto di script, un
import da un altro pacchetto (quale pacchetto, e l'export tramite un hash del suo percorso), oppure null.

- Il layout del riepilogo è cambiato nella 5.3 (bundle di dipendenze e nomi di pacchetti importati) e di nuovo nella 5.6 (due
  offset in più). Vengono provati entrambi i layout, e si tiene quello la cui tabella dei nomi si analizza, quindi la versione
  non deve essere nota.
- I pacchetti **versionati** (in stile non cotto) vengono rifiutati.
- I nomi di pacchetti importati portano un numero. Un pacchetto `_Terrain` numerato 1 è il file `_Terrain_0`.
- I nomi `/Game/...` vengono mappati sulla cartella `Content` del progetto nello store.
- I riferimenti vengono seguiti tra pacchetti confrontando l'hash pubblico dell'export.

Verificato: ogni cella di ogni tappa si apre.

## Proprietà non versionate {#unversioned-properties}

Gli export Unreal 5 cotti non nominano le loro proprietà. Un export inizia con un'intestazione di sequenze, "salta tanti slot,
poi tante presenti", e una maschera che dice quali presenti sono zero e non portano byte. I valori seguono nell'ordine delle
proprietà della classe. Leggere questo richiede lo **schema** di ogni classe: il suo elenco di proprietà, nell'ordine esatto in
cui il motore lo costruisce (prima le proprie, poi quelle del genitore, uno slot per elemento di array statico, escluse le
proprietà solo per l'editor).

Gli schemi sono incorporati per le classi che un percorso richiede:

| Classe | Catena |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | le catene ISM (presenti, ma non usate dall'esportazione del percorso, perché questa build le ha riorganizzate) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Coprono anche le struct che questi contengono (`FBodyInstance`, le risposte di collisione e altre). I tipi di valore vengono
letti per codifica: numeri e vettori a dimensione fissa (`FVector`, `FRotator` come double, `FTransform`...), `FName`, enum (un
byte), riferimenti a oggetti (indice di pacchetto `i32`), percorsi di oggetti soft, array, struct annidate, e delegati multicast
(saltati).

Gli schemi sono **solo nomi e tipi di proprietà**, ricavati dagli header di Unreal Engine 5.6.1 (che Epic rende disponibili a
chiunque abbia un account collegato). Non è incluso alcun codice del motore. Questa build ha **due slot in più in
`UPrimitiveComponent`** rispetto agli header, e **uno in più nel volume della texture virtuale**, trovati dai dati e segnati
`(unknown)`. Un valore presente in uno di questi slot è un errore, non un'ipotesi. Uno slot oltre la fine di uno schema, o un tipo
sconosciuto, solleva `PropertyError`.

Verificato: ogni componente mesh statica e di scena di ogni tappa si decodifica, terminando ciascuno esattamente alla coda nativa
fissa della sua classe. Una patch del gioco può spostare gli slot. Il lettore allora solleva un errore, e il percorso riporta quanti
componenti sono falliti.

## Mesh statiche {#static-meshes}

Un export `UStaticMesh` è le sue proprietà seguite dai dati nativi. Le proprietà non servono alla geometria e non vengono lette. La
parte nativa si trova dal suo inizio fisso: un flag GUID a zero, due byte di flag di striscia, `bCooked = 1`, e l'indice dell'export
`BodySetup` proprio della mesh. Viene poi letta nell'ordine in cui `UStaticMesh::Serialize` e `FStaticMeshRenderData::Serialize`
la scrivono per una mesh **cotta, non Nanite**:

- fino a 16 livelli di dettaglio, ciascuno con le sue sezioni (materiale, primo indice, numero di triangoli), i limiti e, quando
  **inline**: il buffer delle posizioni (float32 x 3), le tangenti, le UV (tutti i canali, precisione a metà o piena), i colori, e
  il buffer degli indici (16 o 32 bit);
- ciò che segue (buffer degli indici invertiti e solo per la profondità, dati di ray tracing, campionatori ponderati per area) viene
  saltato per arrivare al livello successivo.

Un livello non memorizzato in linea termina la lista. Una mesh senza nessuno viene rifiutata. Le posizioni sono quelle di Unreal:
centimetri, X in avanti, Y a destra, Z in alto.

Verificato: quasi ogni mesh campionata si decodifica (le altre sono scheletriche), e l'estensione decodificata di una tessera stradale
corrisponde ai limiti che memorizza.

## Texture {#textures}

Un export `Texture2D` sono le sue proprietà e poi i suoi dati di piattaforma cotti: il nome del formato dei pixel, la dimensione, e
una tabella di livelli mip, ciascuno che punta alla **mappa dei dati bulk** del pacchetto (offset, dimensione, flag; inline nell'export
quando il flag `0x40` è impostato, altrimenti nel `.ubulk`). I dati di piattaforma si trovano dalla loro forma propria, non saltando le
proprietà, quindi il layout delle proprietà della classe texture non conta. Viene decodificato il primo mip non più grande della dimensione
richiesta.

| Formato Unreal | Decodificato come |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA a 8 bit |
| `PF_G8` | grigio a 8 bit |

Verificato: un'immagine satellitare DXT5 da 4096 px i cui tredici livelli sono esattamente le dimensioni delle voci bulk.

## Texture virtuali in streaming {#streaming-virtual-textures}

Una `VirtualTexture2D` cotta è composta da tessere quadrate con un bordo, per livello di dettaglio, indirizzate da un **codice Morton**
(x nei bit pari), memorizzate in blocchi dei dati bulk del pacchetto. Il layout viene letto come lo scrive `FVirtualTextureBuiltData::Serialize`
in Unreal 5.6: layer, dimensione della tessera, bordo, tabelle di indirizzi delle tessere per mip, formati dei layer, e il blocco *n* come
voce bulk *n*. Una regione della texture viene assemblata tessera per tessera, con i bordi rimossi, dal livello la cui risoluzione è più
vicina alla dimensione richiesta. Viene letto solo il primo layer, e solo nei formati sopra.

Verificato: le tessere di un blocco di texture virtuale sono tutte contate, fino all'ultimo byte.
