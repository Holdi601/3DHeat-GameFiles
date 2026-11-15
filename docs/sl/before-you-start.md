---
title: "Preden začnete"
nav_order: 2
lang: "sl"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Preden začnete {#before-you-start}

Še niste vajeni ukazne vrstice? Ta stran vas v približno desetih minutah vodi od nič do delujočega
orodja. Ukaze vtipkate v okno, imenovano **terminal**, orodje pa odgovori z besedilom.

## 1. Namesti Python {#install-python}

1. Pojdite na [python.org/downloads](https://www.python.org/downloads/) in prenesite
   **Python 3.10 ali novejši**.
2. Zaženite namestitev. Na prvem zaslonu obkljukajte **»Add python.exe to PATH«**,
   nato kliknite **Install Now**.

## 2. Pridobite orodje {#get-the-tool}

- **Z gitom:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Brez gita:** na [strani GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  kliknite zeleni gumb **Code**, nato **Download ZIP**, in ga razpakirajte.

## 3. Odprite terminal v mapi orodja {#open-a-terminal-in-the-tools-folder}

- V Raziskovalcu odprite mapo, ki vsebuje `README.md`. Kliknite v vrstico z naslovom,
  vtipkajte `cmd` in pritisnite Enter. Odpre se črno okno, ki je že v tej mapi.
- Ali odprite **Windows Terminal** in se tja premaknite z `cd`:

  ```
  cd "C:\Users\ti\Downloads\3DHeat-GameFiles"
  ```

## 4. Namestite, kar orodje potrebuje {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Videti bi morali vrstice, ki se končajo z `Successfully installed ...`.

## 5. Preverite, da deluje {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Videti bi morali `usage: heat3d_gamefiles [-h]` in seznam ukazov (`identify`,
`list`, `extract`, `course`, ...). To pomeni uspeh: orodje je pripravljeno.

## Kako brati primere {#reading-the-examples}

- `<nekaj>` je **nadomestilo**: namesto tega vtipkajte svojo vrednost, brez kotnih oklepajev.
  `<datoteka kroga>` postane na primer `laps\moj_krog.json`.
- `[--možnost]` v oglatih oklepajih je **izbirno**: če je ne potrebujete, jo izpusti.
- Pot s presledki potrebuje **dvojne narekovaje**: `"C:\Moje igre\krog.json"`.
- Vsak ukaz zaženite v mapi orodja (korak 3).

## Ko nekaj ne gre prav {#when-something-goes-wrong}

| Kar vidite | Kaj storiti |
|---|---|
| `'python' is not recognized` | Python ni nameščen ali ni bilo obkljukano »Add python.exe to PATH«. Zaženite namestitev znova, obkljukajte in odprite nov terminal. |
| `No module named heat3d_gamefiles` | Terminal je v napačni mapi. Z `cd` pojdite v mapo, ki vsebuje `README.md`. |
| `No module named numpy` (ali drugo ime) | Korak 4 je bil izpuščen. Zaženite `pip install -r requirements.txt`. |
| `can't open file` / `not found` s potjo | Pot ima presledke brez narekovajev ali napako v črkovanju. Dajte jo v dvojne narekovaje. |

Več sporočil in njihovih rešitev: [Odpravljanje težav](troubleshooting.md).
