---
title: "Prije nego počnete"
nav_order: 2
lang: "bs"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Prije nego počnete {#before-you-start}

Je li vam komandna linija nova? Ova stranica vas za desetak minuta vodi od ničega
do alata koji radi. Komande upisujete u prozor zvan **terminal**, a alat
odgovara tekstom.

## 1. Instalirajte Python {#install-python}

1. Idite na [python.org/downloads](https://www.python.org/downloads/) i preuzmite
   **Python 3.10 ili noviji**.
2. Pokrenite instalacijski program. Na njegovom prvom ekranu označi **"Add python.exe to PATH"**,
   pa kliknite **Install Now**.

## 2. Nabavite alat {#get-the-tool}

- **S gitom:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez gita:** na [GitHub stranici](https://github.com/Holdi601/3DHeat-GameFiles)
  kliknite zeleno dugme **Code**, zatim **Download ZIP** i raspakujte ga.

## 3. Otvorite terminal u folderu alata {#open-a-terminal-in-the-tools-folder}

- U File Exploreru otvorite folder koji drži `README.md`. Kliknite u adresnu traku,
  upišite `cmd` i pritisnite Enter. Otvara se crni prozor, već u tom folderu.
- Ili otvorite **Windows Terminal** i dođi tamo pomoću `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instalirajte ono što alat treba {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Trebali biste vidjeti redove koji završavaju s `Successfully installed ...`.

## 5. Provjerite radi li {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Trebali biste vidjeti `usage: heat3d_gamefiles [-h]` i popis komandi (`identify`,
`list`, `extract`, `course`, ...). To je uspjeh: alat je spreman.

## Čitanje primjera {#reading-the-examples}

- `<something>` je **rezervirano mjesto**: upišite vlastitu vrijednost umjesto toga, bez
  špicastih zagrada. `<lap file>` postaje, na primjer, `laps\my_lap.json`.
- `[--option]` u uglastim zagradama je **neobavezno**: izostavite ga ako vam ne treba.
- Putanja s razmacima treba **dvostruke navodnike**: `"C:\My Games\lap.json"`.
- Svaku komandu pokrenite u folderu alata (korak 3).

## Kad nešto pođe po zlu {#when-something-goes-wrong}

| Vidite | Šta učiniti |
|---|---|
| `'python' is not recognized` | Python nije instaliran ili "Add to PATH" nije označeno. Ponovo pokrenite instalacijski program i označite ga, pa otvorite novi terminal. |
| `No module named heat3d_gamefiles` | Terminal je u pogrešnom folderu. Uradite `cd` u folder koji drži `README.md`. |
| `No module named numpy` (ili neko drugo ime) | Korak 4 je preskočen. Pokrenite `pip install -r requirements.txt`. |
| `can't open file` / `not found` s putanjom | Putanja ima razmake a nema navodnika, ili je greška u kucanju. Stavite je u dvostruke navodnike. |

Više poruka i njihovih rješenja: [Rješavanje problema](troubleshooting.md).
