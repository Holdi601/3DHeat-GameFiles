---
title: Regole e licenze
nav_order: 12
lang: "it"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Regole e licenze {#rules-and-licences}

Tre regole danno forma a tutto lo strumento. Sono decisioni di progetto, non semplici avvertenze. Testo completo:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Questa pagina registra ciò che dicono le licenze, non è un parere legale.

## 1. Nessuna chiave: nessuna distribuita, nessuna recuperata {#no-keys-none-shipped-none-recovered}

**Lo strumento legge i contenitori.** Analizzare un formato di archivio è normale gestione di file, e FModel, UModel e
AssetRipper lo fanno apertamente da anni. Analizzare un contenitore non è di per sé un'elusione.

**La linea che conta è la cifratura, e viene tracciata dentro lo strumento.** Uno strumento il cui scopo è aggirare un controllo
d'accesso è di per sé nell'ambito delle leggi anti-elusione (DMCA §1201(a)(2) riguarda le tecnologie, non solo gli atti), anche
se nessuno distribuisce un singolo file estratto. Quindi:

- **Nessuna chiave inclusa.** Non c'è nessuna chiave nel codice o nei dati.
- **Nessun recupero di chiavi.** Niente cerca una chiave in un eseguibile, e niente legge la memoria di un altro processo.
- **Una chiave che possiedi, oppure niente.** Un `.pak` di Unreal cifrato si apre solo con `--key <hex>` (in Python,
  `PakArchive(path, aes_key=...)`). `pak.py` non ha alcun percorso di codice che ottenga una chiave. Un contenitore IoStore cifrato
  viene rifiutato senza eccezioni.
- **Anche l'offuscamento non è implementato.** Le tabelle Frostbite offuscate con XOR tengono la chiave nel file stesso, quindi sono
  offuscamento più che un controllo d'accesso. Vengono comunque riconosciute e rifiutate, perché nessun file a disposizione usa quella
  forma e non ci sarebbe nulla su cui verificare un'implementazione. Il pacchetto con chiave di Assetto Corsa EVO viene rifiutato per lo
  stesso motivo per cui esiste la regola sulle chiavi.
- **I file cifrati restano chiusi.** Il file system iniziale di Battlefield 6, che contiene la libreria dei tipi del gioco, è cifrato e
  non viene letto. L'esportazione del livello lavora sui file non cifrati, e ricostruisce dai dati i due tipi di cui ha bisogno.
- **Nulla si inserisce in un processo di gioco.** La telemetria viene da flussi che i giochi pubblicano da sé, e la cattura usa API
  pubbliche di registrazione dello schermo (negli altri strumenti di 3DHeat). L'iniezione in un titolo con anti-cheat mette a rischio
  l'account di chi la esegue.

Ogni archivio provato finora non è cifrato.

## 2. I tuoi file, la tua responsabilità {#your-own-files-your-responsibility}

Lo strumento legge i file di gioco **installati sul tuo computer**. Non scarica mai contenuti di gioco.

Ciò a cui lo punti resta sotto la tua responsabilità. I giochi hanno i propri termini di licenza, e i contratti di licenza con l'utente
vietano comunemente l'ingegneria inversa. Sono contratti applicabili, e l'obbligo ricade su chi esegue lo strumento, su qualsiasi gioco.
Nessuna scelta di progetto qui lo esonera. Il caso legittimo più chiaro è quello di uno sviluppatore che legge la build del proprio studio:
il progetto di un altro team, un ramo vecchio, una build di un partner.

## 3. Il risultato non è per la ridistribuzione {#output-is-not-for-redistribution}

Quello che esce è geometria per **contesto spaziale**: il suolo, la strada e ciò che le sta accanto, semplificato per stare in un budget,
così i giri si possono analizzare sul posto. È la parte meno importante di ciò che contiene un archivio, ed è comunque contenuto
dell'editore del gioco.

- Conserva i `.glb` esportati, e le texture al loro interno, per la tua analisi personale.
- Non pubblicare, condividere o vendere percorsi, livelli, modelli o texture esportati.
- Il `.gitignore` del repository tiene i file di gioco, gli esportati, i giri e le registrazioni fuori dal controllo di versione, per
  cartella e per tipo di file (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` e altri).

## Oodle si trova, non si include {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, ora Epic) è proprietario e non ha una build ridistribuibile. `oo2core_*.dll` è concesso in licenza al prodotto
che lo distribuisce. Quindi `oodle.py` carica una libreria già presente sul computer invece di includerne una. È la disposizione che la
licenza prevede, e la stessa che usano FModel e UModel. Vedi [Oodle](reader-oodle.md).

## I formati in sé {#the-formats-themselves}

- `.pak`, IoStore, il `SerializedFile` di Unity, i `.toc` di Frostbite e i formati di ForzaTech non sono documentati. Leggerli è
  ingegneria inversa di un contenitore. Nessuno dei lettori qui deriva dal codice sorgente di un altro progetto. Per Frostbite, descrizioni
  pubbliche di versioni più vecchie (gli strumenti di modding Frosty, una nota sul formato di Need for Speed Heat, un talk GDC) hanno fornito
  nomi di campi e una mappa di cosa cercare. Non è stato copiato alcun codice; ogni offset è stato misurato sui file (vedi
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- I livelli estratti sono per uso personale. Lo strumento le scrive sul tuo disco e da nessun'altra parte; non pubblicarle.
- BeamNG pubblica il layout del suo `.cdae`, e il lettore lo segue.
- Valve documenta il VPK.
- Le proprietà cotte di Unreal 5 hanno bisogno dell'elenco delle proprietà di ogni classe. Gli elenchi in `unversioned.py` sono **solo
  nomi e tipi**, fatti sul formato come quelli che contiene un file di mappatura per l'interoperabilità. Sono stati ricavati dagli header
  di Unreal Engine che Epic rende disponibili a chiunque abbia un account collegato, e verificati contro i dati distribuiti. Non è incluso né
  richiesto alcun sorgente del motore.

## La licenza di questo strumento {#this-tools-licence}

Tutto ciò che è scritto per questo repository è sotto la **licenza MIT** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
usalo, modificalo, distribuiscilo, commercialmente o no.

I pacchetti di terze parti, tutti permissivi, quindi l'esportatore non ha restrizioni proprie:

| Pacchetto | Licenza | Usato per |
|---|---|---|
| numpy | BSD-3-Clause | decodifica delle mesh |
| cryptography | Apache-2.0 / BSD-3-Clause | solo per gli archivi di cui hai una chiave |
| lz4 | BSD-3-Clause | archivi Forza, alcuni bundle Unity, blocchi LZ4 di IoStore |
| Pillow | MIT-CMU (HPND) | texture a blocchi compressi, output JPEG |
| msgpack | Apache-2.0 | `.cdae` di BeamNG |
| zstandard | BSD-3-Clause | i pochi `.cdae` compressi con zstd, blocchi zstd di Frostbite |
| pytest | MIT | solo per lo sviluppo |

Le licenze sono state lette dai metadati dei pacchetti a settembre 2026. Se i termini di un componente cambiano dopo, conta il sorgente.
