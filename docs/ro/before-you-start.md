---
title: "Înainte de a începe"
nav_order: 2
lang: ro
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Înainte de a începe {#before-you-start}

Nu ați mai lucrat în linia de comandă? Această pagină vă duce de la zero la un instrument care
funcționează, în vreo zece minute. Scrieți comenzi într-o fereastră numită **terminal**, iar
instrumentul răspunde cu text.

## 1. Instalați Python {#install-python}

1. Mergeți la [python.org/downloads](https://www.python.org/downloads/) și descărcați
   **Python 3.10 sau mai nou**.
2. Rulați programul de instalare. Pe primul ecran bifați **„Add python.exe to PATH”**,
   apoi apăsați **Install Now**.

## 2. Obțineți instrumentul {#get-the-tool}

- **Cu git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Fără git:** pe [pagina GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  apăsați butonul verde **Code**, apoi **Download ZIP**, și dezarhivați-l.

## 3. Deschideți un terminal în dosarul instrumentului {#open-a-terminal-in-the-tools-folder}

- În File Explorer, deschideți dosarul care conține `README.md`. Faceți clic în bara de adrese,
  scrieți `cmd` și apăsați Enter. Se deschide o fereastră neagră, deja în acel dosar.
- Sau deschideți **Windows Terminal** și mergeți acolo cu `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instalați ce are nevoie instrumentul {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Ar trebui să vedeți linii care se termină cu `Successfully installed ...`.

## 5. Verificați că funcționează {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Ar trebui să vedeți `usage: heat3d_gamefiles [-h]` și o listă de verbe (`identify`,
`list`, `extract`, `course`, ...). Asta înseamnă succes: instrumentul este gata.

## Citirea exemplelor {#reading-the-examples}

- `<something>` este un **loc rezervat**: scrieți propria valoare în locul lui, fără
  paranteze unghiulare. `<lap file>` devine, de exemplu, `laps\my_lap.json`.
- `[--option]` între paranteze pătrate este **opțional**: lăsați-l pe dinafară dacă nu aveți nevoie de el.
- Un drum cu spații are nevoie de **ghilimele duble**: `"C:\My Games\lap.json"`.
- Rulați fiecare comandă în dosarul instrumentului (pasul 3).

## Când apare o problemă {#when-something-goes-wrong}

| Ce vedeți | Ce să faceți |
|---|---|
| `'python' is not recognized` | Python nu este instalat, sau „Add to PATH” nu a fost bifat. Rulați din nou programul de instalare, bifați opțiunea, apoi deschideți un terminal nou. |
| `No module named heat3d_gamefiles` | Terminalul este în alt dosar. Folosiți `cd` până în dosarul care conține `README.md`. |
| `No module named numpy` (sau alt nume) | Pasul 4 a fost sărit. Rulați `pip install -r requirements.txt`. |
| `can't open file` / `not found` cu o cale | Calea are spații fără ghilimele, sau o greșeală de scriere. Puneți-o între ghilimele duble. |

Mai multe mesaje și remedierile lor: [Depanare](../troubleshooting.md).
