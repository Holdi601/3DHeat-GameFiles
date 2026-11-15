---
title: Oodle
nav_order: 3
lang: "it"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: trovato, non incluso {#oodle-found-not-bundled}

La maggior parte dei contenuti Unreal distribuiti, e alcuni payload Frostbite, sono compressi con
**Oodle** (RAD Game Tools, ora Epic). Oodle è proprietario. Non esiste una build ridistribuibile
né un'implementazione in Python, e `oo2core_*.dll` è concesso in licenza al prodotto che lo
distribuisce. Quindi questo strumento **trova una copia già presente sulla tua macchina e la carica**.
Non ne porta mai una con sé. FModel e UModel funzionano nello stesso modo.

Fonte: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Dove cerca {#where-it-looks}

Vince il primo file che esiste, in quest'ordine:

1. Un percorso esplicito passato dal chiamante (API Python).
2. `HEAT3D_OODLE`: un percorso alla DLL, o a una cartella che ne contiene una.
3. Una ricerca superficiale, a un solo livello di profondità, in
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - la cartella `steamapps\common` di ogni libreria Steam

   Per ogni cartella figlia `<gioco>`, controlla `<gioco>`,
   `<gioco>\Engine\Binaries\ThirdParty\Oodle\Win64` e
   `<gioco>\Engine\Binaries\Win64`.

Nomi di file provati, dal più recente: da `oo2core_9_win64.dll` fino a
`oo2core_3_win64.dll`. Il formato è retrocompatibile, quindi una libreria più vecchia
di solito funziona ancora.

La ricerca è volutamente **non** una scansione ricorsiva di ogni disco, che richiederebbe
minuti. Se non trova nulla, imposta `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Anche una cartella funziona come il file stesso: i nomi delle DLL sopra vengono provati al suo interno.

Un'installazione di Unreal Engine ne contiene una sotto `Engine\Binaries\ThirdParty\Oodle`,
che è la fonte più pulita per uno sviluppatore. Molti giochi ne distribuiscono una accanto
al loro eseguibile. I giochi Unreal 5 spesso collegano Oodle in modo statico e non distribuiscono
alcuna DLL, quindi la copia trovata può appartenere a un gioco diverso da quello dell'archivio
letto. Il formato è lo stesso in entrambi i casi.

## Come viene chiamata {#how-it-is-called}

`OodleLZ_Decompress` viene chiamata tramite `ctypes` con la lunghezza di output attesa (l'indice
dell'archivio la conosce sempre, e Oodle non può dedurla), decodifica sicura contro i dati malformati
attiva (l'input non è fidato), nessun controllo CRC (lo SHA-1 del pak già copre i byte), e
senza thread. Un risultato di lunghezza sbagliata è un errore. La libreria viene caricata una
volta per esecuzione.

## Quando non ce n'è nessuna {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Una voce che non può essere decompressa è un errore, mai una spazzatura plausibile.

Il caricatore funziona solo su Windows (cerca `*_win64.dll`). Le librerie per Linux e macOS
non vengono cercate.
