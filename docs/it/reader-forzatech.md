---
title: ForzaTech
nav_order: 7
lang: "it"
source: reader-forzatech.md
source_hash: "5b298baf30a0"
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, campioni, posizionamenti {#forzatech-minizip-modelbin-swatches-placements}

Forza Horizon gira su ForzaTech, il motore di Turn 10. Questi lettori portano una pista dai suoi archivi fino a
triangoli posizionati e texturizzati. Vengono raggiunti tramite `course`, `courses` e `terrain` (vedi
[Forza Horizon](course-forza-horizon.md)). `identify` riconosce un `.minizip` e un `.modelbin` isolato, e `list` ed
`extract` prendono un `.minizip`, con i nomi nel file `ChunkContentsMiniZip<n>.txt` accanto ad esso oppure per numero di
voce (`#12`).

| Formato | Modulo |
|---|---|
| archivi `.minizip` e i loro elenchi di nomi | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| modelli `.modelbin` e terreno | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| campioni di texture `.pb` | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| file di posizionamento `.pgeo` | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` e hash delle texture dei materiali | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| tessere di terreno per posizione | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza tiene anche gran parte dei suoi contenuti in normali archivi ZIP sotto `media\`. Il `zipfile` di Python li apre, e
`forzatech.models_in_archive()` elenca le loro voci `.modelbin`. La geometria delle piste è negli archivi `.minizip`.

## `.minizip`: un archivio senza nomi {#minizip-an-archive-with-no-names}

Una pista distribuisce quattro archivi `GeoChunk<n>.minizip`, decine di gigabyte ciascuno per una mappa open-world, con
centinaia di migliaia di voci. **Gli archivi non memorizzano nessun nome**: né una tabella dei nomi né un'intestazione per
voce, solo un ordinale. I nomi si trovano nel file `ChunkContentsMiniZip<n>.txt` accanto a ogni archivio, una riga per voce
nell'ordine delle voci (`<build path>zipcache\pc\<path>|<bundle>`). Questo abbinamento è l'unico modo per chiedere un file.
Tutto ciò che sta fino a `zipcache\pc\` viene scartato, e le ricerche ignorano le maiuscole.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Tre dettagli nell'indice producono ancora un output quando vengono letti male. Il lettore li gestisce tutti e tre:

| Dettaglio | Cosa fa un lettore sbadato | Che aspetto ha |
|---|---|---|
| la base del segmento è a **64 bit** | la legge come u32 più padding | corretta per i primi 4 GB, poi rumore della lunghezza giusta |
| la base è **allineata a 8 byte** | ignora la parola di padding dopo la tabella dei bundle | negli archivi con un numero pari di bundle, ogni voce dichiara un codec che non esiste |
| la lunghezza memorizzata di una voce è lo spazio fino alla voce successiva (o alla base del segmento successivo) **meno il suo padding** (bit di flag 12-13) | usa l'intero spazio | LZ4 rifiuta il blocco del tutto |

I codec sono i cinque bit bassi dei flag: `0x00` memorizzato, `0x08` deflate grezzo, `0x1F` blocco LZ4. Qualsiasi altro
viene rifiutato. Ogni voce deve espandersi esattamente alla dimensione che dichiara, altrimenti viene rifiutata. L'indice
(circa 5 MB) viene letto una volta, e i payload vengono letti con uno spostamento.

L'intestazione viene controllata: magic, un'intestazione di 32 byte, e un numero di segmenti che corrisponde a
`ceil(entries / per segment)`.

**Verificato:** voci campionate in ogni archivio di una mappa, ciascuna espansa esattamente alla sua lunghezza dichiarata
con tutti e tre i codec.

## `.modelbin`: il contenitore di chunk {#modelbin-the-chunk-container}

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- La dimensione dichiarata del file deve essere uguale alla dimensione reale.
- La **catena**: ogni chunk inizia dove finisce il precedente, arrotondato in su a 4 byte. Nulla nel file lo dichiara,
  quindi è una prova: un record letto con il passo sbagliato non produce questo. Ha retto per tutti i 252 modelli campionati.
- Un file `PGZP` dato al lettore dei modelli viene nominato "a ForzaTech .minizip archive, not a model" e indirizzato a
  `minizip.py`, invece di essere rifiutato in modo generico.

La geometria viene da questi chunk:

| Chunk | Contiene |
|---|---|
| `VLay` | un layout di vertici: nomi di attributi, poi elementi (indice del nome u16, canale u16, buffer, formato DXGI, offset); il numero di elementi è un u16 |
| `VerB` | un buffer di vertici dietro un'intestazione di 16 byte (conteggio, dimensione, passo u16, attributi u16, formato) |
| `IndB` | il buffer di indici, stessa intestazione |
| `Mesh` | una sottomesh: materiale, maschera del livello di dettaglio, intervallo di indici, layout, buffer, passo, tabella delle varianti e un riquadro di posizione alla fine |
| `MatI` | un'istanza di materiale: il suo percorso `.materialbin` e gli hash delle texture |

### Posizioni e riquadro {#positions-and-the-box}

Le posizioni sono `R16G16B16A16_SNORM` (formato 13): quattro short con segno per vertice.
`position = short / 32767 * scale + bias`, dove scale e bias sono gli ultimi 32 byte del chunk `Mesh` (due float4).
Il bias è nelle **coordinate del mondo del gioco**, quindi un tassello di terreno cade dove il gioco lo mette senza alcuna
trasformazione dell'istanza. Per questo basta un giro di telemetria per chiedere un pezzo di mappa.
Ogni sottomesh di un modello porta lo stesso riquadro (verificato su 860 di esse).

### Il layout dei vertici {#the-vertex-layout}

Un unico buffer di posizioni copre ogni vertice. Gli altri attributi sono divisi in gruppi di vertici consecutivi, ciascuno
con il proprio buffer e il proprio layout: una strada vicino a un incrocio porta tre set di UV e due tangenti, la scarpata
accanto solo una normale. Ogni attributo che non è una posizione occupa quattro byte. Quale layout descrive quale buffer
si ricava dalle sottomesh che disegnano da esso, perché layout e buffer non sono nello stesso ordine (uguale, ruotato di
uno, o permutato, a seconda del modello).

| Formato DXGI | Codice | Usato per |
|---|---|---|
| R16G16B16A16_SNORM | 13 | posizione (il quarto short è la x della normale) |
| R16G16_SNORM | 37 | y, z della normale |
| R16G16_UNORM | 35 | una coppia UV (canale = quale set) |
| R8G8B8A8_UNORM | 28 | colore o pesi di miscelazione |
| R10G10B10A2_UNORM | 24 | tangente (non decodificata) |
| R16_UINT | 57 | indici |

**La normale è divisa.** `NORMAL` contiene y e z. La x è il quarto short della posizione, che sembrava padding. Su centinaia
di migliaia di vertici di terreno correla +0,92 con la x della normale del triangolo e con nient'altro. Con essa, il 96% dei
vertici di terreno in pendenza sta entro 18° dalla normale calcolata. Ogni codifica a due componenti provata senza di essa
(ottaedrica in tutte le 48 disposizioni incluse) ha dato bene y e z e male x.

Gli altri formati di posizione o di indice vengono **rifiutati** ("only 13 (four shorts, scaled) is implemented"; "only
unsigned shorts are implemented").

### Sottomesh {#submeshes}

Un record `Mesh` è di 238 byte nella forma standard. Quelli più lunghi portano all'inizio una tabella delle **varianti** di
materiale più lunga, 238 + 8 x count - 4 byte, e ogni campo dopo di essa si sposta indietro esattamente di tanto. Quelli
più corti (218 byte, alcuni terreni) mantengono gli offset. Ogni voce di variante è
`u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`. La maschera del livello di dettaglio è un u16, un bit per
livello a partire dal bit 1.

Niente viene preso per buono da solo. Gli intervalli di indici devono coprire esattamente il buffer degli indici, ogni
`index count` deve essere uguale a 3 x `triangles`, e il passo che una sottomesh nomina deve essere quello del suo buffer.
Una tabella che fallisce viene rifiutata per intero, perché etichettare triangoli da campi letti male è peggio che non
etichettarli. Su migliaia di sottomesh campionate, passano tutte quelle il cui indice di buffer è nell'intervallo.

### Materiali e hash delle texture {#materials-and-texture-hashes}

Un `MatI` nomina il suo materiale con un percorso `Game:...\x.materialbin`, trovato cercando nel chunk. Le sue texture sono
record `u32 slot, u32, u32 hash`, distanziati di 33 byte e non allineati, quindi il chunk viene cercato a ogni offset di byte
in cerca di parole che sono hash di texture noti. Questi vengono dal `AssetManifest.xml` della pista
(`<Texture Source="...\name.swatch" SourceHash="...">`, letto fino a `</Textures>`). Lo slot `0x88B483AA` è il colore base dello
shader standard. Come viene poi scelta la texture del colore è descritto in [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: campioni di texture {#pb-texture-swatches}

Un campione è lo stesso contenitore `burG` di un modello: un'intestazione `HCXT` di 96 byte a partire dal byte 44, poi un
chunk di pixel. L'intestazione contiene il GUID della texture (quello nel nome del file), larghezza e altezza, il numero di
mip, e il **codice di formato al byte 72** (numerazione propria di ForzaTech). Il byte 84 contiene il numero di byte dei pixel.

| Codice | Formato | Identificato come |
|---|---|---|
| 0 | BC1, mezzo byte per pixel | si decodifica come un bordo rosso e bianco (rumore sotto BC4) |
| 9 | BC7, un byte per pixel | si decodifica come una tessera di terreno con visibile il circuito |
| 13 | RGBA8, quattro byte per pixel | semplice |
| altro | rifiutato | "texture format N has not been identified; refusing to guess" |

I formati sono stati identificati decodificando file reali in ogni modo che la dimensione del payload consente. Il byte 47,
che una versione precedente prendeva come formato, vale 4 in ognuna delle texture campionate. Viene decodificato solo il mip
più alto di un file. Ogni risoluzione è una voce propria, `<name>_<guid>_quality<n>.pb`, dalla qualità 1 (più piccola) alla 5
(più grande). Per le mappe di terreno, le due più grandi si trovano in un archivio diverso dalle altre. La decodifica passa
dal decodificatore BCn di Pillow, tramite un'intestazione DDS generata.

## File di posizionamento (.pgeo) {#placement-files-pgeo}

Un file per categoria per cella spaziale: `scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Il percorso da solo
dà il quadrato della cella e la categoria, così i file si possono filtrare senza aprirli.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Come è stato deciso ogni campo:

| Campo | Deciso da |
|---|---|
| la posizione è in virgola fissa 16.16, non una frazione del riquadro | guardrail consecutivi sono esattamente 4,000 m di distanza (la lunghezza del modello) |
| modulo e segno, non complemento a due | il complemento a due metteva le coordinate negative decine di chilometri fuori mappa; con il bit 31 come segno, ogni record di ogni categoria campionata cade dentro il riquadro del suo file |
| i vettori sono gli assi propri del modello | la fine di ogni guardrail cade sull'inizio del successivo: 93,5% entro 5 cm, mediana 0,000 m |
| il byte 60 è la variante | le cinque copie di un cartellone leggono 0, 2, 2, 3, 4 mentre ogni guardrail legge 0 |

Solo i nomi che terminano con `_3D` sono record di modello. La tabella delle varianti prima di essi elenca nomi senza il
suffisso, e letti come record finirebbero all'infinito. Un record candidato viene accettato solo se il suo conteggio sta nel
file, e le istanze con numeri non finiti vengono scartate.

## Non implementato {#not-implemented}

- Formati di vertici e indici diversi da quelli sopra (rifiutati).
- Formati di texture diversi da 0, 9, 13 (rifiutati).
- Tangenti (lette e scartate, non usate).
- I livelli di materiale dello shader del terreno. La texture del suolo è un'interpretazione delle mappe delle tessere (vedi
  [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
