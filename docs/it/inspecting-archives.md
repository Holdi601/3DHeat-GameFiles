---
title: Esaminare gli archivi
nav_order: 3
lang: "it"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Esaminare gli archivi: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Un gioco impacchetta i suoi file in grandi scatole chiamate **archivi**. Questi comandi
guardano l'etichetta di una scatola, elencano cosa c'è dentro e ne estraggono una cosa.

Prima di esportare qualcosa da un gioco che non conosci, guarda cosa contiene.
Questi quattro comandi leggono un file e ti dicono cos'è e cosa contiene; non scrivono
nulla, tranne la sola voce che chiedi con `extract`.

![identify, list e extract eseguiti su un piccolo zip](../assets/img/inspect-archives.svg)

*Un'esecuzione su uno zip sintetico organizzato come un livello di BeamNG.drive.*

## Passo dopo passo {#step-by-step}

1. **Chiedi che file è.** `identify` legge i byte, non l'estensione:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<gioco>\Content\Paks\<archivio>.pak"
   ```

   Indica il formato (Unreal `.pak`, IoStore `.utoc`/`.ucas`, bundle Unity o
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` o
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), la sua versione, quante voci contiene e
   se è cifrato.

2. **Elenca cosa c'è dentro.** `list` stampa una riga per voce: dimensione, compressione,
   percorso. Restringila con `--filter`, limitala con `--limit`:

   ```
   python -m heat3d_gamefiles list <archivio> --filter Maps/ --limit 50
   ```

3. **Estrai una voce.** `extract` scrive una voce (nella cartella in cui ti trovi, a meno che
   `--out` non indichi dove), usando il percorso che `list` ha stampato
   (oppure `#12`, con il numero, in un `.minizip` senza nomi):

   ```
   python -m heat3d_gamefiles extract <archivio> <percorso interno> --out out\voce.bin
   ```

4. **Unity:** `meshes` elenca e controlla le mesh di un `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <file .assets di unity> --limit 20
   ```

## Opzioni {#options}

| Comando | Opzione | Significato |
|---|---|---|
| `identify` | `<file>` | qualsiasi file |
| `list` | `<archivio>` | `.pak`, `.utoc` (o il `.ucas` accanto), `.vpk`, `.minizip`, zip |
| | `--filter TESTO` | solo i percorsi che contengono TESTO |
| | `--limit N` | al massimo N righe |
| | `--key HEX` | una chiave AES-256 (64 cifre esadecimali) che già possiedi; serve solo a un `.pak` cifrato |
| `extract` | `<archivio> <percorso>` | l'archivio e il percorso della voce come lo stampa `list` |
| | `--out FILE` | dove scriverlo (predefinito: il nome del file della voce) |
| | `--key HEX` | come per `list` |
| `meshes` | `<file>`, `--limit N` | un `SerializedFile` di Unity; al massimo N mesh |

Lo strumento non include chiavi e non ne recupera nessuna: un archivio cifrato si apre solo con
una chiave che passi tu. Un file che non riesce a leggere viene rifiutato con una riga e codice di
uscita 1. Ogni comando e codice di uscita è nella pagina [Comandi](commands.md); come viene
letto ogni formato è spiegato in [Lettori di archivi](archive-readers.md).
