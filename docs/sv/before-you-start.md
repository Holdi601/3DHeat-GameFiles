---
title: Innan du börjar
nav_order: 2
lang: "sv"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Innan du börjar {#before-you-start}

Har du aldrig använt kommandoraden förut? Den här sidan tar dig från noll till ett fungerande
verktyg på ungefär tio minuter. Du skriver kommandon i ett fönster som kallas **terminal**,
och verktyget svarar med text.

## 1. Installera Python {#install-python}

1. Gå till [python.org/downloads](https://www.python.org/downloads/) och ladda ner
   **Python 3.10 eller senare**.
2. Kör installationsprogrammet. På första skärmen kryssar du i **"Add python.exe to PATH"**,
   och klickar sedan på **Install Now**.

## 2. Hämta verktyget {#get-the-tool}

- **Med git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Utan git:** på [GitHub-sidan](https://github.com/Holdi601/3DHeat-GameFiles),
  klicka på den gröna knappen **Code**, sedan **Download ZIP**, och packa upp den.

## 3. Öppna en terminal i verktygets mapp {#open-a-terminal-in-the-tools-folder}

- I Utforskaren öppnar du mappen som innehåller `README.md`. Klicka i adressfältet,
  skriv `cmd` och tryck på Enter. Ett svart fönster öppnas, redan i den mappen.
- Eller öppna **Windows Terminal** och gå dit med `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installera det verktyget behöver {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Du bör se rader som slutar med `Successfully installed ...`.

## 5. Kontrollera att det fungerar {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Du bör se `usage: heat3d_gamefiles [-h]` och en lista med verb (`identify`,
`list`, `extract`, `course`, ...). Det är lyckat: verktyget är klart.

## Läsa exemplen {#reading-the-examples}

- `<något>` är en **platshållare**: skriv ditt eget värde i stället, utan
  vinkelparenteserna. `<lap file>` blir till exempel `laps\my_lap.json`.
- `[--option]` inom hakparenteser är **valfritt**: utelämna det om du inte behöver det.
- En sökväg med mellanslag behöver **dubbla citattecken**: `"C:\My Games\lap.json"`.
- Kör varje kommando i verktygets mapp (steg 3).

## När något går fel {#when-something-goes-wrong}

| Du ser | Gör så här |
|---|---|
| `'python' is not recognized` | Python är inte installerat, eller "Add to PATH" var inte ikryssad. Kör installationsprogrammet igen och kryssa i den, öppna sedan en ny terminal. |
| `No module named heat3d_gamefiles` | terminalen står i fel mapp. Gå med `cd` till mappen som innehåller `README.md`. |
| `No module named numpy` (eller ett annat namn) | steg 4 hoppades över. Kör `pip install -r requirements.txt`. |
| `can't open file` / `not found` med en sökväg | sökvägen har mellanslag utan citattecken, eller ett stavfel. Sätt den inom dubbla citattecken. |

Fler meddelanden och hur de åtgärdas: [Felsökning](troubleshooting.md).
