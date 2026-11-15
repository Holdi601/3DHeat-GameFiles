---
title: Voordat je begint
nav_order: 2
lang: "nl"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Voordat je begint {#before-you-start}

Nog nooit met de opdrachtregel gewerkt? Deze pagina brengt je in ongeveer tien minuten van niets
naar een werkend hulpmiddel. Je typt opdrachten in een venster dat een **terminal** heet, en het
hulpmiddel antwoordt met tekst.

## 1. Installeer Python {#install-python}

1. Ga naar [python.org/downloads](https://www.python.org/downloads/) en download
   **Python 3.10 of later**.
2. Start het installatieprogramma. Vink op het eerste scherm **"Add python.exe to PATH"** aan,
   en klik dan op **Install Now**.

## 2. Haal het hulpmiddel op {#get-the-tool}

- **Met git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Zonder git:** op de [GitHub-pagina](https://github.com/Holdi601/3DHeat-GameFiles),
  klik op de groene knop **Code**, dan op **Download ZIP**, en pak het uit.

## 3. Open een terminal in de map van het hulpmiddel {#open-a-terminal-in-the-tools-folder}

- Open in Verkenner de map die `README.md` bevat. Klik in de adresbalk, typ
  `cmd` en druk op Enter. Er opent een zwart venster, al in die map.
- Of open **Windows Terminal** en ga er met `cd` naartoe:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installeer wat het hulpmiddel nodig heeft {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Je ziet regels die eindigen op `Successfully installed ...`.

## 5. Controleer of het werkt {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Je ziet `usage: heat3d_gamefiles [-h]` en een lijst met werkwoorden (`identify`,
`list`, `extract`, `course`, ...). Dat is geslaagd: het hulpmiddel is klaar.

## De voorbeelden lezen {#reading-the-examples}

- `<iets>` is een **plaatsaanduiding**: typ in plaats daarvan je eigen waarde, zonder de
  punthaken. `<lap file>` wordt bijvoorbeeld `laps\my_lap.json`.
- `[--option]` tussen vierkante haken is **optioneel**: laat het weg als je het niet nodig hebt.
- Een pad met spaties heeft **dubbele aanhalingstekens** nodig: `"C:\My Games\lap.json"`.
- Voer elke opdracht uit in de map van het hulpmiddel (stap 3).

## Als er iets misgaat {#when-something-goes-wrong}

| Je ziet | Wat je doet |
|---|---|
| `'python' is not recognized` | Python is niet geïnstalleerd, of "Add to PATH" was niet aangevinkt. Voer het installatieprogramma opnieuw uit, vink het aan, en open daarna een nieuwe terminal. |
| `No module named heat3d_gamefiles` | De terminal staat in de verkeerde map. Ga met `cd` naar de map die `README.md` bevat. |
| `No module named numpy` (of een andere naam) | Stap 4 is overgeslagen. Voer `pip install -r requirements.txt` uit. |
| `can't open file` / `not found` met een pad | Het pad heeft spaties zonder aanhalingstekens, of er zit een typefout in. Zet het tussen dubbele aanhalingstekens. |

Meer meldingen en hun oplossingen: [Problemen oplossen](troubleshooting.md).
