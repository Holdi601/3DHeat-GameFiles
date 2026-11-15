---
title: VPK di Source 2
nav_order: 6
lang: "it"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# VPK di Source 2 `.vpk` {#source-2-vpk}

**Elenca ed estrae** gli archivi VPK di Valve, versioni 1 e 2, inclusi gli archivi divisi e i dati
memorizzati dentro il file della directory. Ogni voce può essere controllata con il proprio
CRC. È l'unico formato contenitore qui il cui produttore lo documenta. Giochi: Counter-Strike 2, Dota 2, Half-Life: Alyx e altri su Source 2.

Fonte: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Comandi: `identify`, `list`, `extract`.

## Struttura {#layout}

```
u32 magic 0x55AA1234, u32 version (1 o 2), u32 dimensione dell'albero
  (versione 2: 16 byte di intestazione in più; intestazione di 12 o 28 byte)
albero della directory:
  estensione       "vmdl_c", poi "vtex_c", ..., poi ""
    percorso       "maps/example_map", poi ""
      nome file    "world_layer0", poi ""
        u32 crc, u16 dimensione di precaricamento, u16 indice d'archivio, u32 offset, u32 lunghezza, u16 0xFFFF
        [byte di precaricamento]
```

- Tre cicli annidati, ognuno che finisce con una stringa vuota, quindi un lettore che si aspetta un
  conteggio non ne trova nessuno. I percorsi sono memorizzati una volta per gruppo e ricomposti dalle tre
  parti. Uno spazio singolo significa "nessuna cartella" o "nessuna estensione".
- Ogni record termina con `0xFFFF`. Questo viene controllato, quindi un lettore che ha perso
  la posizione si ferma subito ("the directory is not being read at the right offset", cioè
  "la directory non viene letta all'offset giusto").
- **Archivi divisi:** `pak01_dir.vpk` contiene la directory, e i dati si trovano in
  `pak01_000.vpk`, `pak01_001.vpk`... scelti in base all'indice d'archivio della voce.
- **Indice d'archivio `0x7FFF`** significa che i byte si trovano nel file della directory stesso,
  dopo l'albero. Leggerlo come un vero indice porta un lettore a cercare
  `pak01_32767.vpk`.
- **Precaricamento:** i file piccoli sono memorizzati interi nella directory. Una lunghezza di 0 non è
  allora un errore.

## Comandi {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` stampa la versione, il numero di voci e il primo file `.nav`. `list`
mostra ogni voce come `stored`, perché VPK non comprime. `extract` scrive i byte
senza controllare il CRC. In Python, `VpkArchive(path).verify(name)`
confronta i byte di una voce con il CRC registrato nella directory.

## La mesh di navigazione {#the-navigation-mesh}

Una mappa distribuisce la sua **mesh di navigazione** (`maps/<mappa>.nav`) accanto alla
geometria compilata. Per una mappa di calore delle posizioni dei giocatori è la più utile delle due, di gran lunga,
perché la mesh di navigazione *è* il pavimento percorribile, già calcolato e un millesimo
della dimensione. Il test sul gioco installato verifica che il `.nav` di una mappa distribuita inizi
con il magic della navigazione Source `CE FA ED FE`.

## Verificato {#verified}

Ogni voce campionata in tutti gli archivi di mappe distribuiti di un gioco è risultata identica byte per byte
al suo CRC, e ogni archivio di mappe si analizza correttamente.
I test sul gioco installato ripetono il controllo CRC su 25 voci casuali da ciascuno di
fino a quattro archivi di mappe.

## Non implementato {#not-implemented}

- La decodifica delle risorse compilate di Source 2 (`.vmdl_c`, `.vtex_c`). Sono file binari a blocchi
  a sé, lo stesso tipo di lavoro dei formati mesh di Unreal e Frostbite. Lo strumento CS2
  separato di 3DHeat gestisce la geometria delle mappe CS2.
- La decodifica della mesh di navigazione di CS2. Il suo formato è la versione 36 e differisce da quello
  Source 1, ampiamente documentato. I suoi byte sono strutturati anziché compressi
  (entropia 6.2, 31% di zeri), ma solo il 3% delle sue parole si legge come coordinate, quindi la
  struttura non è quella ovvia e non è ancora stata ricostruita.
