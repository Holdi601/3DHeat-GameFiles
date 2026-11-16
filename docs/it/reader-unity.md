---
title: Unity
nav_order: 4
lang: "it"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, bundle, mesh {#unity-serializedfile-bundles-meshes}

**Elenca gli oggetti e decodifica le mesh** dei `SerializedFile` di Unity dal formato 22 in poi (Unity 2020 fino alla 6000),
e apre i bundle `UnityFS`. Non esiste un'esportazione del percorso per Unity.

Fonti: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Comandi: `identify` (contenitori e bundle), `meshes` (solo contenitori semplici).

## Il contenitore {#the-container}

Unity distribuisce un livello come grafi di oggetti serializzati: `globalgamemanagers`, `sharedassets*.assets`,
`resources.assets`, `level*`, e i bundle di asset. Ognuno contiene una tabella di oggetti marcati con un id di classe.

L'intestazione è dove la lettura sbaglia in silenzio. I primi sedici byte sono quattro `uint32` big-endian mantenuti per
compatibilità. Nel formato 22 tre di essi sono zero, e i valori veri seguono perché un file può superare i 4 GB:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Il secondo `metadata size` è un `uint32` tra due `int64`. Presumere che tutti e tre siano a 64 bit sposta la stringa di
versione di quattro byte. Il risultato si decodifica comunque in qualcosa che sembra una stringa, e manda storto tutto ciò
che segue. L'intestazione è big-endian. Tutto il resto segue il byte di endianness (0, little-endian, su ogni build desktop).

Dopo l'intestazione: la stringa di versione del motore, la piattaforma, il flag del type tree, la tabella dei tipi (id di
classe per tipo), la tabella degli oggetti (path id, offset, dimensione, tipo) e gli esterni (altri file a cui un puntatore
può riferirsi).

| Caso | Risultato |
|---|---|
| formato 22-30 | letto |
| formato 9-21 (prima di Unity 2020) | rifiutato: gli offset sono nell'intestazione legacy, e nessun file a disposizione la usava |
| fuori da 9-30 | rifiutato |
| type tree incorporato (build dell'editor) | rifiutato: le build distribuite non ne incorporano uno, e il percorso dell'editor non è implementato |
| un bundle passato dove ci si aspetta un contenitore | rifiutato, con un rinvio al lettore di bundle |

Non esiste un **deserializzatore generale**. Le build distribuite non portano un type tree, perché lo schema è compilato nel
player, quindi ogni classe va analizzata con un layout noto per la sua versione. Viene decodificato solo `Mesh`. Le altre
classi vengono segnalate per nome e numero (`GameObject`, `Transform`, `MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`,
`MeshCollider`, `MonoBehaviour`, `MonoScript`, `AssetBundle`, `RectTransform`, `PrefabInstance`; le altre come `class<id>`).

**Verificato** su molti giochi installati e milioni di oggetti: la tabella degli oggetti deve coprire esattamente la sezione
dei dati, senza sovrapposizioni, con soltanto padding di allineamento tra gli oggetti, e l'ultimo oggetto deve finire
sull'ultimo byte del file. Un'intestazione letta male non può produrre questo. Il test sui giochi installati lo ripete su fino
a sei file `resources.assets` / `sharedassets0.assets` nelle cartelle `*_Data`.

## Bundle (`UnityFS`) {#bundles-unityfs}

Un bundle è un contenitore compresso di `SerializedFile`. Anche la lista dei blocchi e la directory sono compresse. Il metodo sta
nei sei bit bassi di una parola di flag: 0 memorizzato, 1 LZMA (l'intestazione di 5 byte di Unity con la dimensione inserita),
2 e 3 LZ4 / LZ4HC. Il formato 7 e successivi allinea l'intestazione a 16 byte. Il flag `0x80` mette la directory alla fine del
file. `UnityWeb`, `UnityRaw` e `UnityArchive` (precedenti alla 5.3) sono riconosciuti ma non letti.

## Mesh {#meshes}

`read_mesh` decodifica un oggetto `Mesh` in posizioni, normali, il primo set di UV e triangoli, nell'ordine in cui Unity 2019+
le scrive: nome, sottomesh, blend shape (saltate), pose di bind e dati delle ossa (saltati), i flag di compressione e leggibilità,
il buffer degli indici, i canali dei vertici e i dati dei vertici, il blocco della mesh compressa, il riquadro di contenimento
locale e le informazioni di streaming.

- **Vertici esterni.** La maggior parte della geometria distribuita vive in un file `.resS` accanto al contenitore. Lo strumento lo
  legge dalla cartella del contenitore (si usa solo il nome del file del percorso `archive:/...` memorizzato). Un `.resS`
  mancante è un errore, non una mesh vuota.
- **Stream e canali.** I canali dicono quale stream, offset, formato e dimensione ha ogni attributo. Gli stream sono impacchettati
  uno dopo l'altro, ciascuno imbottito fino a 16 byte, quindi l'inizio di uno stream si accumula dai passi che lo precedono.
  Formati: float32, float16, unorm/snorm 8 e 16 (normalizzati), e interi semplici.
- **Topologia.** Solo triangoli (topologia 0). Strisce, quad e linee vengono rifiutati, perché una conversione sbagliata sembra
  geometria vera.
- **Mesh compresse** (delta quantizzati) vengono rifiutate: "mesh '...' is stored compressed; that encoding is not implemented".

### Il controllo interno {#the-self-check}

Leggere una struttura nell'ordine sbagliato non solleva errori. Produce numeri plausibili. Quindi ogni mesh decodificata viene
controllata contro il **riquadro di contenimento che Unity ha memorizzato per essa**, calcolato dall'editor dai vertici reali.
`aabb_matches()` passa quando gli angoli del riquadro decodificato sono entro il 2% della dimensione del riquadro memorizzato.
`meshes` stampa `ok` o `BOUNDS DISAGREE` su ogni riga.

**Verificato:** le mesh campionate su diversi giochi si decodificano con i riquadri che concordano. Il test sui giochi installati
ripete il controllo sui contenitori installati.

## Non implementato {#not-implemented}

- Formati precedenti al 2020.
- Mesh compresse.
- Qualsiasi classe diversa da `Mesh`: niente grafo di scena, trasformazioni o materiali, quindi le mesh sono nel loro spazio locale.
- `meshes` su un bundle. Il lettore di bundle esiste in Python (`UnityBundle.serialized_files()`), ma il comando accetta un contenitore semplice.
