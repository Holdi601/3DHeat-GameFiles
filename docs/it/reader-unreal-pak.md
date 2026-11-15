---
title: Unreal .pak
nav_order: 1
lang: "it"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Elenca ed estrae** gli archivi `.pak` di Unreal 4.22-5.x: versioni 8, 9, 10, 11 e 12, compressione Zlib, Gzip e Oodle, e
archivi cifrati quando fornisci la chiave AES. Non interpreta ciò che estrae (`.uasset`, `.umap`).

Sorgente: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Comandi: `identify`, `list`, `extract` (vedi [Comandi](commands.md)).

## Struttura {#layout}

Il footer si trova alla fine del file e viene cercato nei 1.024 byte finali alla ricerca del magic `0x5A6F12E1`. Il suo ordine dei
campi conta:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Il flag di cifratura sta **prima** del magic. Prenderlo da dopo il magic cade sulla "Z" di "Zlib". Allora ogni archivio risulta
cifrato e ogni nome di metodo perde la prima lettera ("lib", "odle"), un errore silenzioso e plausibile. La versione è il bit basso,
perché le build "frozen index" impostano un bit alto.

L'indice contiene il punto di montaggio, l'indice dei percorsi con hash, l'indice completo delle directory, e un blocco di **voci
codificate**: una forma impacchettata a bit in cui una parola di flag dice quali numeri sono a 32 bit, il metodo di compressione (6 bit),
se la voce è cifrata, il numero di blocchi (16 bit) e la dimensione del blocco in unità di 2.048 (6 bit). La dimensione di blocco tutta a
uno è una via di fuga: la dimensione reale segue come u32 **prima** dell'offset. In un archivio grande, leggerla dopo le dimensioni ha
spostato del 7% le voci di quattro byte e ha dato loro offset nell'ordine degli exabyte.

Il record completo di ogni voce viene ripetuto appena prima del suo payload, quindi il payload inizia dopo `8+8+8+20+4+1+4` byte, più
`4 + 16 x blocks` quando è compresso. I blocchi cifrati sono imbottiti fino a 16 byte.

## Cosa legge e cosa rifiuta {#what-it-reads-and-what-it-refuses}

| Caso | Risultato |
|---|---|
| versioni 8-12 | lette |
| qualsiasi altra versione | `pak version N; this reader handles 8-12` (le versioni precedenti memorizzano un elenco piatto di record, e non c'era un file su cui provarle) |
| nessun magic nel footer | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indice fuori dal file | rifiutato: il footer non si è analizzato come dichiarato |
| solo indice dei percorsi con hash | rifiutato: i nomi dei file sono stati sottoposti a hash in fase di build e non si possono recuperare |
| voci nell'elenco di overflow dell'indice (offset di directory -1) | saltate, non falsificate |
| indice cifrato, senza chiave | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Dalla riga di comando, una riga e codice di uscita 1 |
| voce cifrata, senza chiave | `EncryptedPak` alla lettura |
| metodi Zlib, Gzip, Oodle | decompressi (Oodle richiede una libreria, vedi [Oodle](reader-oodle.md)) |
| qualsiasi altro metodo | `compression method '...' is not supported` |

## Chiavi {#keys}

`--key` con `list` ed `extract` accetta una chiave AES-256 che già possiedi, come 64 cifre esadecimali, con o senza `0x`.
Qualsiasi altra cosa viene rifiutata prima di aprire l'archivio, con codice di uscita 2. La decifratura è AES-256-ECB tramite il
pacchetto `cryptography`. Non esiste alcun percorso di codice che ottenga una chiave: niente chiavi incluse, nessuna ricerca negli
eseguibili, nessuna lettura della memoria. Vedi [Regole e licenze](rules-and-licences.md).

## Verificato {#verified}

Su archivi distribuiti di più giochi, ogni voce, incluso un archivio molto grande, corrisponde per SHA-1 che Unreal scrive prima di
ogni payload. Quell'hash copre i byte così come sono memorizzati, quindi una corrispondenza significa che la decodifica dell'indice,
l'offset del payload e ogni confine di blocco compresso erano giusti. I test sui giochi installati (`test_pak.py`) ripetono questo su
fino a quattro pak non cifrati trovati sotto `steamapps\common\*\...\Content\Paks`. Verificano che l'offset di ogni voce stia dentro il
file, e che lo SHA-1 corrisponda per un campione casuale di 150 voci per archivio.
