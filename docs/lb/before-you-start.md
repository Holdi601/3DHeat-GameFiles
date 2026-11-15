---
title: "Ier Dir ufänkt"
nav_order: 2
lang: "lb"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Ier Dir ufänkt {#before-you-start}

Nei op der Kommandozeil? Dës Säit bréngt Iech vun Null bis bei en funktionéierend Tool a
ongeféier zéng Minutten. Dir tippt Kommandoe a e Fënster, dat **Terminal** heescht, an
d'Tool äntwert mat Text.

## 1. Python installéieren {#install-python}

1. Gitt op [python.org/downloads](https://www.python.org/downloads/) a luet
   **Python 3.10 oder méi nei** erof.
2. Startt den Installer. Um éischten Ecran **"Add python.exe to PATH"** ukräizen,
   dann op **Install Now** klicken.

## 2. D'Tool kréien {#get-the-tool}

- **Mat git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Ouni git:** Op der [GitHub-Säit](https://github.com/Holdi601/3DHeat-GameFiles)
  klickt op de gréngen **Code**-Knäppchen, dann op **Download ZIP**, an entpackt et.

## 3. E Terminal am Dossier vum Tool opmaachen {#open-a-terminal-in-the-tools-folder}

- Mécht am File Explorer den Dossier op, deen `README.md` hält. Klickt an d'Adressleist,
  tippt `cmd` an dréckt Enter. E schwaarzt Fënster geet op, schonn an deem Dossier.
- Oder mécht den **Windows Terminal** op a gitt mat `cd` dohinner:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installéieren, wat d'Tool brauch {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Dir sollt Zeilen gesinn, déi mat `Successfully installed ...` ophalen.

## 5. Préift, ob et funktionéiert {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Dir sollt `usage: heat3d_gamefiles [-h]` an eng Lëscht vu Verben gesinn (`identify`,
`list`, `extract`, `course`, ...). Dat ass Erfolleg: d'Tool ass prett.

## D'Beispiller liesen {#reading-the-examples}

- `<something>` ass e **Platzhalter**: tippt Äre Wäert amplaz, ouni d'
  spëtze Klammeren. `<lap file>` gëtt zum Beispill `laps\my_lap.json`.
- `[--option]` an eckege Klammeren ass **optional**: looss et fort, wann Dir et net braucht.
- E Wee mat Espacen brauch **duebel Ureechnungszeechen**: `"C:\My Games\lap.json"`.
- Féiert all Kommando am Dossier vum Tool aus (Schrëtt 3).

## Wann eppes falsch geet {#when-something-goes-wrong}

| Dir gesitt | Wat maachen |
|---|---|
| `'python' is not recognized` | Python ass net installéiert, oder "Add to PATH" war net ugekräizt. Startt den Installer nach eemol an kräizt et un, dann mécht en neit Terminal op. |
| `No module named heat3d_gamefiles` | D'Terminal ass am falschen Dossier. Gitt mat `cd` an den Dossier, deen `README.md` hält. |
| `No module named numpy` (oder en anere Numm) | Schrëtt 4 gouf iwwersprong. Féiert `pip install -r requirements.txt` aus. |
| `can't open file` / `not found` mat engem Wee | De Wee huet Espacen an keng Ureechnungszeechen, oder en Tippfeeler. Setzt en an duebel Ureechnungszeechen. |

Méi Meldungen an hir Léisungen: [Fehlerbehebung](../troubleshooting.md).
