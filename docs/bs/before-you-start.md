---
title: "Prije nego počneš"
nav_order: 2
lang: "bs"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Prije nego počneš {#before-you-start}

Komandna linija ti je nova? Ova stranica te za desetak minuta vodi od ničega
do alata koji radi. Naredbe upisuješ u prozor zvan **terminal**, a alat
odgovara tekstom.

## 1. Instaliraj Python {#install-python}

1. Idi na [python.org/downloads](https://www.python.org/downloads/) i preuzmi
   **Python 3.10 ili noviji**.
2. Pokreni instalacijski program. Na njegovom prvom ekranu označi **"Add python.exe to PATH"**,
   pa klikni **Install Now**.

## 2. Nabavi alat {#get-the-tool}

- **S gitom:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez gita:** na [GitHub stranici](https://github.com/Holdi601/3DHeat-GameFiles)
  klikni zeleno dugme **Code**, zatim **Download ZIP** i raspakuj ga.

## 3. Otvori terminal u folderu alata {#open-a-terminal-in-the-tools-folder}

- U File Exploreru otvori folder koji drži `README.md`. Klikni u adresnu traku,
  upiši `cmd` i pritisni Enter. Otvara se crni prozor, već u tom folderu.
- Ili otvori **Windows Terminal** i dođi tamo pomoću `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instaliraj ono što alat treba {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Trebao bi vidjeti redove koji završavaju s `Successfully installed ...`.

## 5. Provjeri radi li {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Trebao bi vidjeti `usage: heat3d_gamefiles [-h]` i popis naredbi (`identify`,
`list`, `extract`, `course`, ...). To je uspjeh: alat je spreman.

## Čitanje primjera {#reading-the-examples}

- `<something>` je **rezervirano mjesto**: upiši vlastitu vrijednost umjesto toga, bez
  špicastih zagrada. `<lap file>` postaje, na primjer, `laps\my_lap.json`.
- `[--option]` u uglastim zagradama je **neobavezno**: izostavi ga ako ti ne treba.
- Putanja s razmacima treba **dvostruke navodnike**: `"C:\My Games\lap.json"`.
- Svaku naredbu pokreni u folderu alata (korak 3).

## Kad nešto pođe po zlu {#when-something-goes-wrong}

| Vidiš | Šta učiniti |
|---|---|
| `'python' is not recognized` | Python nije instaliran ili "Add to PATH" nije označeno. Ponovo pokreni instalacijski program i označi ga, pa otvori novi terminal. |
| `No module named heat3d_gamefiles` | Terminal je u pogrešnom folderu. Uradi `cd` u folder koji drži `README.md`. |
| `No module named numpy` (ili neko drugo ime) | Korak 4 je preskočen. Pokreni `pip install -r requirements.txt`. |
| `can't open file` / `not found` s putanjom | Putanja ima razmake a nema navodnika, ili je greška u kucanju. Stavi je u dvostruke navodnike. |

Više poruka i njihovih rješenja: [Rješavanje problema](../troubleshooting.md).
