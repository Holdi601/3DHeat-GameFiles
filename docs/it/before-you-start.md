---
title: Prima di iniziare
nav_order: 2
lang: "it"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Prima di iniziare {#before-you-start}

Non hai mai usato la riga di comando? Questa pagina ti porta dal nulla a uno strumento funzionante in
circa dieci minuti. Scrivi i comandi in una finestra chiamata **terminale**, e lo strumento risponde
con del testo.

## 1. Installa Python {#install-python}

1. Vai su [python.org/downloads](https://www.python.org/downloads/) e scarica **Python 3.10 o
   successivo**.
2. Esegui il programma di installazione. Nella prima schermata spunta **"Add python.exe to PATH"**,
   poi clicca su **Install Now**.

## 2. Procurati lo strumento {#get-the-tool}

- **Con git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Senza git:** sulla [pagina GitHub](https://github.com/Holdi601/3DHeat-GameFiles) clicca sul
  pulsante verde **Code**, poi su **Download ZIP**, e decomprimilo.

## 3. Apri un terminale nella cartella dello strumento {#open-a-terminal-in-the-tools-folder}

- In Esplora file, apri la cartella che contiene `README.md`. Clicca nella barra degli indirizzi,
  digita `cmd` e premi Invio. Si apre una finestra nera, già in quella cartella.
- Oppure apri **Windows Terminal** e vai lì con `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installa ciò che lo strumento richiede {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Dovresti vedere righe che terminano con `Successfully installed ...`.

## 5. Verifica che funzioni {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Dovresti vedere `usage: heat3d_gamefiles [-h]` e un elenco di verbi (`identify`,
`list`, `extract`, `course`, ...). È il segno che è andata bene: lo strumento è pronto.

## Leggere gli esempi {#reading-the-examples}

- `<qualcosa>` è un **segnaposto**: scrivi al suo posto il tuo valore, senza le parentesi angolari.
  `<lap file>` diventa, per esempio, `laps\my_lap.json`.
- `[--option]` tra parentesi quadre è **facoltativo**: omettilo se non ti serve.
- Un percorso con spazi richiede le **virgolette doppie**: `"C:\My Games\lap.json"`.
- Esegui ogni comando nella cartella dello strumento (passo 3).

## Quando qualcosa non va {#when-something-goes-wrong}

| Vedi | Cosa fare |
|---|---|
| `'python' is not recognized` | Python non è installato, oppure non era spuntato "Add to PATH". Esegui di nuovo il programma di installazione spuntando la casella, poi apri un nuovo terminale. |
| `No module named heat3d_gamefiles` | Il terminale è nella cartella sbagliata. Usa `cd` per andare nella cartella che contiene `README.md`. |
| `No module named numpy` (o un altro nome) | Il passo 4 è stato saltato. Esegui `pip install -r requirements.txt`. |
| `can't open file` / `not found` con un percorso | Il percorso ha spazi senza virgolette, oppure c'è un errore di battitura. Mettilo tra virgolette doppie. |

Altri messaggi e le loro soluzioni: [Risoluzione dei problemi](troubleshooting.md).
