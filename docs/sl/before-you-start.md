---
title: "Preden začneš"
nav_order: 2
lang: sl
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Preden začneš {#before-you-start}

Še nisi vajen ukazne vrstice? Ta stran te v približno desetih minutah vodi od nič do delujočega
orodja. Ukaze vtipkaš v okno, imenovano **terminal**, orodje pa odgovori z besedilom.

## 1. Namesti Python {#install-python}

1. Pojdi na [python.org/downloads](https://www.python.org/downloads/) in prenesi
   **Python 3.10 ali novejši**.
2. Zaženi namestitev. Na prvem zaslonu obkljukaj **»Add python.exe to PATH«**,
   nato klikni **Install Now**.

## 2. Pridobi orodje {#get-the-tool}

- **Z gitom:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Brez gita:** na [strani GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  klikni zeleni gumb **Code**, nato **Download ZIP**, in ga razpakiraj.

## 3. Odpri terminal v mapi orodja {#open-a-terminal-in-the-tools-folder}

- V Raziskovalcu odpri mapo, ki vsebuje `README.md`. Klikni v vrstico z naslovom,
  vtipkaj `cmd` in pritisni Enter. Odpre se črno okno, ki je že v tej mapi.
- Ali odpri **Windows Terminal** in se tja premakni z `cd`:

  ```
  cd "C:\Users\ti\Downloads\3DHeat-GameFiles"
  ```

## 4. Namesti, kar orodje potrebuje {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Videti bi moral vrstice, ki se končajo z `Successfully installed ...`.

## 5. Preveri, da deluje {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Videti bi moral `usage: heat3d_gamefiles [-h]` in seznam ukazov (`identify`,
`list`, `extract`, `course`, ...). To pomeni uspeh: orodje je pripravljeno.

## Kako brati primere {#reading-the-examples}

- `<nekaj>` je **nadomestilo**: namesto tega vtipkaj svojo vrednost, brez kotnih oklepajev.
  `<datoteka kroga>` postane na primer `laps\moj_krog.json`.
- `[--možnost]` v oglatih oklepajih je **izbirno**: če je ne potrebuješ, jo izpusti.
- Pot s presledki potrebuje **dvojne narekovaje**: `"C:\Moje igre\krog.json"`.
- Vsak ukaz zaženi v mapi orodja (korak 3).

## Ko nekaj ne gre prav {#when-something-goes-wrong}

| Kar vidiš | Kaj storiti |
|---|---|
| `'python' is not recognized` | Python ni nameščen ali ni bilo obkljukano »Add python.exe to PATH«. Zaženi namestitev znova, obkljukaj in odpri nov terminal. |
| `No module named heat3d_gamefiles` | Terminal je v napačni mapi. Z `cd` pojdi v mapo, ki vsebuje `README.md`. |
| `No module named numpy` (ali drugo ime) | Korak 4 je bil izpuščen. Zaženi `pip install -r requirements.txt`. |
| `can't open file` / `not found` s potjo | Pot ima presledke brez narekovajev ali napako v črkovanju. Daj jo v dvojne narekovaje. |

Več sporočil in njihovih rešitev: [Odpravljanje težav](../troubleshooting.md).
