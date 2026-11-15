---
title: "Áður en þú byrjar"
nav_order: 2
lang: is
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Áður en þú byrjar {#before-you-start}

Hefurðu aldrei notað skipanalínu? Þessi síða kemur þér frá engu að virku verkfæri á
um tíu mínútum. Þú skrifar skipanir í glugga sem kallast **skipanalína** (terminal), og
verkfærið svarar með texta.

## 1. Settu upp Python {#install-python}

1. Farðu á [python.org/downloads](https://www.python.org/downloads/) og sæktu
   **Python 3.10 eða nýrra**.
2. Keyrðu uppsetningarforritið. Á fyrsta skjánum skaltu haka við **"Add python.exe to PATH"**
   og smella síðan á **Install Now**.

## 2. Náðu í verkfærið {#get-the-tool}

- **Með git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Án git:** á [GitHub-síðunni](https://github.com/Holdi601/3DHeat-GameFiles)
  smelltu á græna hnappinn **Code**, síðan **Download ZIP**, og pakkaðu skránni upp.

## 3. Opnaðu skipanalínu í möppu verkfærisins {#open-a-terminal-in-the-tools-folder}

- Í File Explorer, opnaðu möppuna sem geymir `README.md`. Smelltu í vistfangastikuna,
  skrifaðu `cmd` og ýttu á Enter. Svartur gluggi opnast, þegar í þeirri möppu.
- Eða opnaðu **Windows Terminal** og farðu þangað með `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Settu upp það sem verkfærið þarf {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Þú ættir að sjá línur sem enda á `Successfully installed ...`.

## 5. Athugaðu að það virki {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Þú ættir að sjá `usage: heat3d_gamefiles [-h]` og lista yfir skipanir (`identify`,
`list`, `extract`, `course`, ...). Það er árangur: verkfærið er tilbúið.

## Að lesa dæmin {#reading-the-examples}

- `<something>` er **staðgengill**: skrifaðu þitt eigið gildi í staðinn, án
  oddklofanna. `<lap file>` verður til dæmis `laps\my_lap.json`.
- `[--option]` í hornklofum er **valkvætt**: slepptu því ef þú þarft það ekki.
- Slóð með bilum þarf **tvöfaldar gæsalappir**: `"C:\My Games\lap.json"`.
- Keyrðu hverja skipun í möppu verkfærisins (skref 3).

## Þegar eitthvað fer úrskeiðis {#when-something-goes-wrong}

| Þú sérð | Hvað á að gera |
|---|---|
| `'python' is not recognized` | Python er ekki uppsett, eða "Add to PATH" var ekki merkt. Keyrðu uppsetningarforritið aftur og hakaðu við það, opnaðu síðan nýja skipanalínu. |
| `No module named heat3d_gamefiles` | Skipanalínan er í rangri möppu. Farðu með `cd` í möppuna sem geymir `README.md`. |
| `No module named numpy` (eða annað nafn) | Skrefi 4 var sleppt. Keyrðu `pip install -r requirements.txt`. |
| `can't open file` / `not found` með slóð | Slóðin hefur bil og engar gæsalappir, eða innsláttarvillu. Settu hana innan tvöfaldra gæsalappa. |

Fleiri skilaboð og lagfæringar þeirra: [Bilanaleit](../troubleshooting.md).
