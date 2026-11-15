---
title: Før du går i gang
nav_order: 2
lang: da
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Før du går i gang {#before-you-start}

Ny til kommandolinjen? Denne side fører dig fra ingenting til et fungerende værktøj på
cirka ti minutter. Du skriver kommandoer i et vindue, der kaldes en **terminal**, og
værktøjet svarer med tekst.

## 1. Installer Python {#install-python}

1. Gå til [python.org/downloads](https://www.python.org/downloads/) og hent
   **Python 3.10 eller nyere**.
2. Kør installationsprogrammet. På dets første skærm sætter du flueben i **"Add python.exe to PATH"**,
   og klikker derefter på **Install Now**.

## 2. Hent værktøjet {#get-the-tool}

- **Med git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Uden git:** på [GitHub-siden](https://github.com/Holdi601/3DHeat-GameFiles)
  klikker du på den grønne knap **Code**, derefter **Download ZIP**, og pakker den ud.

## 3. Åbn en terminal i værktøjets mappe {#open-a-terminal-in-the-tools-folder}

- I Stifinder åbner du mappen, der indeholder `README.md`. Klik i adresselinjen,
  skriv `cmd` og tryk Enter. Et sort vindue åbner, allerede i den mappe.
- Eller åbn **Windows Terminal** og gå dertil med `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installer det, værktøjet har brug for {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Du bør se linjer, der slutter med `Successfully installed ...`.

## 5. Tjek, at det virker {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Du bør se `usage: heat3d_gamefiles [-h]` og en liste over verber (`identify`,
`list`, `extract`, `course`, ...). Det betyder, at det lykkedes: værktøjet er klar.

## Sådan læser du eksemplerne {#reading-the-examples}

- `<something>` er en **pladsholder**: skriv din egen værdi i stedet, uden de spidse
  parenteser. `<lap file>` bliver for eksempel til `laps\my_lap.json`.
- `[--option]` i firkantede parenteser er **valgfri**: udelad den, hvis du ikke har brug for den.
- En sti med mellemrum skal have **dobbelte anførselstegn**: `"C:\My Games\lap.json"`.
- Kør hver kommando i værktøjets mappe (trin 3).

## Når noget går galt {#when-something-goes-wrong}

| Du ser | Hvad du gør |
|---|---|
| `'python' is not recognized` | Python er ikke installeret, eller "Add to PATH" blev ikke sat flueben i. Kør installationsprogrammet igen, sæt flueben, og åbn derefter en ny terminal. |
| `No module named heat3d_gamefiles` | Terminalen står i den forkerte mappe. `cd` til mappen, der indeholder `README.md`. |
| `No module named numpy` (eller et andet navn) | Trin 4 blev sprunget over. Kør `pip install -r requirements.txt`. |
| `can't open file` / `not found` med en sti | Stien har mellemrum uden anførselstegn, eller en tastefejl. Sæt den i dobbelte anførselstegn. |

Flere meddelelser og deres rettelser: [Fejlfinding](../troubleshooting.md).
