---
title: "Mielőtt elkezded"
nav_order: 2
lang: "hu"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Mielőtt elkezded {#before-you-start}

Még nem használt parancssort? Ez az oldal a semmitől egy működő eszközig vezet, körülbelül tíz perc alatt,
egyszer. Parancsokat egy **terminál** nevű ablakba gépelsz be, és az eszköz szöveggel válaszol.

## 1. Telepítsd a Pythont {#install-python}

1. Menj a [python.org/downloads](https://www.python.org/downloads/) oldalra, és töltsd le a
   **Python 3.10 vagy újabb** verzióját.
2. Futtasd a telepítőt. Az első képernyőn pipáld be a **„Add python.exe to PATH”** lehetőséget,
   majd kattints az **Install Now** gombra.

## 2. Szerezd meg az eszközt {#get-the-tool}

- **Git-tel:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Git nélkül:** a [GitHub oldalon](https://github.com/Holdi601/3DHeat-GameFiles) kattints a zöld
  **Code** gombra, majd a **Download ZIP** lehetőségre, és csomagold ki.

## 3. Nyiss terminált az eszköz mappájában {#open-a-terminal-in-the-tools-folder}

- A Fájlkezelőben nyisd meg azt a mappát, amelyben a `README.md` van. Kattints a címsorba, gépeld be
  a `cmd`-t, és nyomj Entert. Egy fekete ablak nyílik meg, már abban a mappában.
- Vagy nyisd meg a **Windows Terminal** alkalmazást, és lépj oda a `cd` paranccsal:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Telepítsd, amire az eszköznek szüksége van {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

A végén `Successfully installed ...` kezdetű sorokat kell látnod.

## 5. Ellenőrizd, hogy működik {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

A `usage: heat3d_gamefiles [-h]` sort és az igék listáját kell látnod (`identify`,
`list`, `extract`, `course`, ...). Ez a siker: az eszköz kész.

## A példák olvasása {#reading-the-examples}

- Az `<valami>` egy **helyőrző**: írd be a saját értékét, a szögletes zárójelek nélkül. A `<lap file>`
  helyére például `laps\my_lap.json` kerül.
- A szögletes zárójelben álló `[--option]` **nem kötelező**: hagyd ki, ha nincs rá szükséged.
- A szóközöket tartalmazó útvonalat **dupla idézőjelbe** kell tenni: `"C:\My Games\lap.json"`.
- Minden parancsot az eszköz mappájában futtass (3. lépés).

## Ha valami nem jól működik {#when-something-goes-wrong}

| Amit lát | Mit tegyél |
|---|---|
| `'python' is not recognized` | A Python nincs telepítve, vagy nem volt bepipálva az „Add to PATH”. Futtasd újra a telepítőt, pipáld be, majd nyiss új terminált. |
| `No module named heat3d_gamefiles` | A terminál rossz mappában van. Lépj oda a `cd` paranccsal ahhoz a mappához, amelyben a `README.md` van. |
| `No module named numpy` (vagy más név) | A 4. lépést kihagytad. Futtasd a `pip install -r requirements.txt` parancsot. |
| `can't open file` / `not found` egy útvonallal | Az útvonalban szóköz van idézőjel nélkül, vagy elgépelés történt. Tedd dupla idézőjelbe. |

További üzenetek és megoldásaik: [Hibaelhárítás](troubleshooting.md).
