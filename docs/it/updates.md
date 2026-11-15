---
title: Aggiornamenti
nav_order: 13
lang: "it"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Aggiornamenti {#updates}

3DHeat GameFiles controlla le release GitHub di questo repository all'avvio, dice
quando è uscita una versione più recente e offre di aggiornare. I tuoi file (giri,
esportazioni) non vengono mai toccati.

Fonte: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
La versione installata è il file
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) del repository.

## Il controllo all'avvio {#the-check-at-start-up}

Ogni esecuzione di `python -m heat3d_gamefiles ...` richiama il controllo prima di
analizzare i suoi argomenti:

- Chiede a `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  con un timeout di **5 secondi**.
- La risposta viene memorizzata nella cache per **6 ore** in
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (o
  `~/.cache/3DHeat/...` senza `LOCALAPPDATA`). In quel tempo non viene fatta alcuna richiesta.
  Anche "nessuna release ancora" (HTTP 404) viene messa in cache.
- Offline, con limite di richieste superato o dietro un proxy, il controllo si limita a tornare
  indietro e lo strumento funziona con la versione che ha.
- Se il tag della release più recente (`v1.2.3` o `1.2.3`; tutto ciò che segue `-` o `+` viene
  ignorato) è più nuovo di `VERSION`, stampa su stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **In un terminale** (stdin e stderr sono entrambi un TTY) chiede `Update now? [Y/n]`.
  Invio, `y`, `yes`, `j` o `ja` aggiornano. Dopo un aggiornamento riuscito, lo **stesso
  comando viene riavviato** sul nuovo codice, e il suo codice di uscita viene passato oltre.
- **Senza un terminale** (un'esecuzione pianificata, una pipe) stampa soltanto
  ``Run `python -m heat3d_update` in <folder> to update.`` e prosegue.

## Aggiornare su richiesta {#updating-on-request}

```
python -m heat3d_update          # aggiorna alla release più recente, se c'è
python -m heat3d_update --check  # dice soltanto se è uscita una release più recente
```

Questo chiede sempre a GitHub (senza cache). Stampa `Up to date: 1.0.1.`,
`No release found (...)`, oppure cosa ha fatto. Il codice di uscita è 1 se l'aggiornamento non
ha potuto essere applicato.

## Come viene applicato un aggiornamento {#how-an-update-is-applied}

| Installato come | Aggiornamento |
|---|---|
| un **clone git** (una cartella `.git` e `git` nel PATH) | `git pull --ff-only`. **Rifiutato** finché i file tracciati hanno modifiche locali: "this checkout has local changes; commit or stash them, then run `git pull`" (questa copia ha modifiche locali; fai commit o stash, poi esegui `git pull`). I file non tracciati non lo bloccano |
| una **copia scaricata** | l'archivio dei sorgenti della release (`zipball_url`) viene scaricato e decompresso in una cartella temporanea, ignorando ogni percorso che uscirebbe da essa; il suo `VERSION` deve essere uguale alla versione della release, altrimenti non viene copiato nulla; poi i suoi file vengono copiati in questa cartella |

Quando copia da un archivio, i file che non fanno parte della release (giri, esportazioni, ambienti
virtuali, tutto ciò che hai creato) vengono lasciati in pace. L'aggiornamento prova
anche a cancellare i moduli `.py` che una release ha rimosso dai suoi pacchetti, così un
modulo vecchio non può oscurare il suo sostituto. Cerca i pacchetti `heat3d_*` nella radice
dell'archivio e in una cartella sotto di essa, e rimuove i file `.py` che la release non
possiede più.

## Disattivarlo {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Qualsiasi valore diverso da vuoto, `0`, `false` o `no` disattiva sia il controllo all'avvio
sia l'offerta. `python -m heat3d_update` funziona comunque quando viene eseguito a mano.
