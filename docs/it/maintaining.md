---
title: Manutenzione
nav_order: 99
lang: "it"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Manutenzione: la lista di controllo per il rilascio {#maintaining-the-release-checklist}

Prima di applicare il tag a una versione (`v` + il numero in `VERSION`), segui questa lista
in ordine. Mantiene le pagine, le immagini e le traduzioni coerenti con il codice.

1. **Rigenera le pagine generate.**
   - `python tools/gen_docs_reference.py` riscrive
     [Riferimento dei comandi](../cli-reference.md) a partire dal `--help` del programma.
     `python tools/gen_docs_reference.py --check` termina con codice 1 finché la pagina
     committata è vecchia.
   - `python tools/docs_diagrams.py --strings` ridisegna i diagrammi in
     `docs/assets/img/` e riscrive `docs/assets/i18n/en.json`, l'elenco di ogni
     etichetta dei diagrammi da tradurre.
2. **Elenca cosa è cambiato dall'ultimo rilascio:**
   `git log --oneline v<ultimo VERSION>..HEAD`. Ogni nuovo comando, opzione, campo di output o
   comportamento richiede una riga in `CHANGELOG.md` e una riga nella tabella **Docs**
   che indichi la pagina che lo spiega. Aggiorna quella pagina.
3. **Chiedi una revisione indipendente** delle pagine e delle immagini cambiate, da qualcuno
   (o da un agente) che non le ha scritte, leggendole come tre persone: un principiante che non ha
   mai usato un terminale, un bambino di 8 anni e un professionista. Anche i diagrammi
   vengono controllati: leggibili alla larghezza della pagina, etichette corrette, colori spiegati.
4. **Correggi ciò che la revisione trova**, poi controlla che nessun dato reale del gioco sia finito
   dentro: nessun nome di mappa, livello o giocatore, nessun numero di registrazioni reali o
   installazioni (usa segnaposto come `<map>` o "il livello di prova").
5. **Ritraduci le pagine cambiate.** Ogni pagina tradotta registra l'hash della pagina inglese
   da cui è stata fatta; le pagine la cui fonte inglese è cambiata vengono tradotte di nuovo, e con
   loro le etichette dei diagrammi. Poi rivedi ogni lingua: chiara per le stesse tre
   persone, etichette corrette, parole che corrispondono all'interfaccia del visualizzatore 3DHeat in quella lingua.
6. **Pubblica solo con il via libera dell'utente.** Non si pubblica né si applica il tag prima
   che il proprietario l'abbia detto.

## Traduzioni: i comandi {#translations-the-commands}

Il sito è tradotto nelle 40 lingue del visualizzatore 3DHeat: l'inglese in `docs/`, ogni altra
lingua in `docs/<lang>/` con gli stessi nomi di file. `tools/docs_i18n.py` si occupa della
contabilità:

```bash
python tools/docs_i18n.py hashes             # dopo ogni modifica all'inglese: registra l'hash di ogni pagina
python tools/docs_i18n.py svg-strings        # dopo ogni modifica alle immagini: le etichette da tradurre
python tools/docs_i18n.py status             # per lingua: aggiornate, obsolete, pagine mancanti
python tools/docs_i18n.py todo --lang de     # le pagine tedesche da (ri)tradurre
python tools/docs_i18n.py svg-build --lang de    # immagini tedesche da docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # marca le pagine tedesche con l'hash inglese
python tools/docs_i18n.py check              # termina con 1 quando hash o etichette sono obsoleti
```

Traduci solo ciò che elenca `todo`: lascia invariati Markdown, link, codice, nomi di file e colonne,
traduci i titoli e le descrizioni delle immagini, e usa le parole del visualizzatore 3DHeat per i suoi pulsanti
e pannelli (il suo `src/i18n/locales/<lang>/`). Le pagine di riferimento generate e le immagini del
terminale restano in inglese. Sul sito, una traduzione obsoleta lo dichiara e rimanda alla pagina
inglese; una traduzione mancante ricade sull'inglese. Il menu delle lingue nell'intestazione e il
reindirizzamento della home page secondo la lingua del browser vengono da `docs/_includes/`.
