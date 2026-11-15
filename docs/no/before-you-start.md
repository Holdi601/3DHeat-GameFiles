---
title: Før du starter
nav_order: 2
lang: no
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Før du starter {#before-you-start}

Ny til kommandolinjen? Denne siden tar deg fra null til et fungerende verktøy på
omtrent ti minutter. Du skriver kommandoer inn i et vindu som kalles en **terminal**, og
verktøyet svarer med tekst.

## 1. Installer Python {#install-python}

1. Gå til [python.org/downloads](https://www.python.org/downloads/) og last ned
   **Python 3.10 eller nyere**.
2. Kjør installasjonen. På første skjerm, kryss av **«Add python.exe to PATH»**,
   og klikk deretter på **Install Now**.

## 2. Skaff verktøyet {#get-the-tool}

- **Med git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Uten git:** på [GitHub-siden](https://github.com/Holdi601/3DHeat-GameFiles),
  klikk på den grønne knappen **Code**, deretter **Download ZIP**, og pakk den ut.

## 3. Åpne en terminal i verktøyets mappe {#open-a-terminal-in-the-tools-folder}

- I Filutforsker, åpne mappen som holder `README.md`. Klikk i adressefeltet, skriv
  `cmd` og trykk Enter. Et svart vindu åpnes, allerede i den mappen.
- Eller åpne **Windows Terminal** og gå dit med `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installer det verktøyet trenger {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Du bør se linjer som slutter med `Successfully installed ...`.

## 5. Sjekk at det virker {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Du bør se `usage: heat3d_gamefiles [-h]` og en liste over verb (`identify`,
`list`, `extract`, `course`, ...). Det betyr at det virker: verktøyet er klart.

## Slik leser du eksemplene {#reading-the-examples}

- `<noe>` er en **plassholder**: skriv inn din egen verdi i stedet, uten
  vinkelparentesene. `<lap file>` blir for eksempel `laps\my_lap.json`.
- `[--option]` i hakeparenteser er **valgfritt**: utelat det hvis du ikke trenger det.
- En sti med mellomrom trenger **doble anførselstegn**: `"C:\My Games\lap.json"`.
- Kjør hver kommando i verktøyets mappe (steg 3).

## Når noe går galt {#when-something-goes-wrong}

| Du ser | Hva du gjør |
|---|---|
| `'python' is not recognized` | Python er ikke installert, eller «Add to PATH» var ikke avkrysset. Kjør installasjonen på nytt og kryss av der, og åpne deretter en ny terminal. |
| `No module named heat3d_gamefiles` | Terminalen står i feil mappe. `cd` til mappen som holder `README.md`. |
| `No module named numpy` (eller et annet navn) | Steg 4 ble hoppet over. Kjør `pip install -r requirements.txt`. |
| `can't open file` / `not found` med en sti | Stien har mellomrom uten anførselstegn, eller en skrivefeil. Sett den i doble anførselstegn. |

Flere meldinger og hvordan du fikser dem: [Feilsøking](../troubleshooting.md).
