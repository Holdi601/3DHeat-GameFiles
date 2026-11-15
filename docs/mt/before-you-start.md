---
title: Qabel ma tibda
nav_order: 2
lang: mt
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Qabel ma tibda {#before-you-start}

Ġdid mal-linja tal-kmandi? Din il-paġna tieħdok minn xejn sa għodda li taħdem f'
madwar għaxar minuti. Tittajpja kmandi f'tieqa msejħa **terminal**, u
l-għodda twieġeb b'test.

## 1. Installa Python {#install-python}

1. Mur fuq [python.org/downloads](https://www.python.org/downloads/) u niżżel
   **Python 3.10 jew aktar ġdid**.
2. Ħaddem l-installer. Fl-ewwel skrin, immarka **"Add python.exe to PATH"**,
   imbagħad ikklikkja **Install Now**.

## 2. Ġib l-għodda {#get-the-tool}

- **B'git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Mingħajr git:** fuq il-[paġna ta' GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  ikklikkja l-buttuna ħadra **Code**, imbagħad **Download ZIP**, u ħollha.

## 3. Iftaħ terminal fil-folder tal-għodda {#open-a-terminal-in-the-tools-folder}

- Fil-File Explorer, iftaħ il-folder li fih `README.md`. Ikklikkja l-bar tal-indirizz,
  ittajpja `cmd` u agħfas Enter. Tiftaħ tieqa sewda, diġà f'dak il-folder.
- Jew iftaħ **Windows Terminal** u mur hemm b'`cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installa dak li teħtieġ l-għodda {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Għandek tara linji li jispiċċaw b'`Successfully installed ...`.

## 5. Iċċekkja li taħdem {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Għandek tara `usage: heat3d_gamefiles [-h]` u lista ta' verbs (`identify`,
`list`, `extract`, `course`, ...). Dak huwa s-suċċess: l-għodda lesta.

## Kif taqra l-eżempji {#reading-the-examples}

- `<something>` huwa **placeholder**: ittajpja l-valur tiegħek minfloku, mingħajr
  il-parentesi angolari. `<lap file>` isir, pereżempju, `laps\my_lap.json`.
- `[--option]` bejn parentesi kwadri huwa **fakultattiv**: ħallih barra jekk ma għandekx bżonnu.
- Triq b'spazji teħtieġ **virgoletti doppji**: `"C:\My Games\lap.json"`.
- Ħaddem kull kmand fil-folder tal-għodda (pass 3).

## Meta xi ħaġa tmur ħażin {#when-something-goes-wrong}

| Tara | X'għandek tagħmel |
|---|---|
| `'python' is not recognized` | Python mhuwiex installat, jew "Add to PATH" ma ġiex immarkat. Ħaddem l-installer mill-ġdid u immarkah, imbagħad iftaħ terminal ġdid. |
| `No module named heat3d_gamefiles` | It-terminal qiegħed fil-folder ħażin. Mur b'`cd` fil-folder li fih `README.md`. |
| `No module named numpy` (jew isem ieħor) | Il-pass 4 tqabbeż. Ħaddem `pip install -r requirements.txt`. |
| `can't open file` / `not found` b'triq | It-triq fiha spazji u ebda virgoletti, jew żball tat-tajpjar. Poġġiha bejn virgoletti doppji. |

Aktar messaġġi u l-fixes tagħhom: [Soluzzjoni ta' problemi](../troubleshooting.md).
