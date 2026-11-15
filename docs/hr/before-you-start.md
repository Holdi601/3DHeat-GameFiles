---
title: Prije nego što počnete
nav_order: 2
lang: hr
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Prije nego što počnete {#before-you-start}

Ne znate ništa o naredbenom retku? Ova stranica vas vodi od nule do radnog alata u
oko deset minuta. Naredbe upisujete u prozor koji se zove **terminal**, a alat odgovara tekstom.

## 1. Instalirajte Python {#install-python}

1. Idite na [python.org/downloads](https://www.python.org/downloads/) i preuzmite
   **Python 3.10 ili noviji**.
2. Pokrenite instalaciju. Na prvom zaslonu označite **"Add python.exe to PATH"**,
   zatim kliknite **Install Now**.

## 2. Nabavite alat {#get-the-tool}

- **S gitom:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez gita:** na [stranici na GitHubu](https://github.com/Holdi601/3DHeat-GameFiles)
  kliknite zeleni gumb **Code**, zatim **Download ZIP**, i raspakirajte ga.

## 3. Otvorite terminal u mapi alata {#open-a-terminal-in-the-tools-folder}

- U File Exploreru otvorite mapu koja sadrži `README.md`. Kliknite adresnu traku,
  upišite `cmd` i pritisnite Enter. Otvara se crni prozor, već u toj mapi.
- Ili otvorite **Windows Terminal** i idite tamo naredbom `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instalirajte što alat treba {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Trebali biste vidjeti retke koji završavaju s `Successfully installed ...`.

## 5. Provjerite radi li {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Trebali biste vidjeti `usage: heat3d_gamefiles [-h]` i popis naredbi (`identify`,
`list`, `extract`, `course`, ...). To znači uspjeh: alat je spreman.

## Čitanje primjera {#reading-the-examples}

- `<something>` je **mjesto za upis**: upišite svoju vrijednost, bez kutnih zagrada.
  `<lap file>` postaje, na primjer, `laps\my_lap.json`.
- `[--option]` u uglatim zagradama je **izborno**: izostavite ga ako vam ne treba.
- Put koji ima razmake treba **dvostruke navodnike**: `"C:\My Games\lap.json"`.
- Svaku naredbu pokrenite u mapi alata (korak 3).

## Kad nešto pođe po zlu {#when-something-goes-wrong}

| Vidite | Što učiniti |
|---|---|
| `'python' is not recognized` | Python nije instaliran ili nije bio označen "Add to PATH". Pokrenite instalaciju ponovno, označite ga i otvorite novi terminal. |
| `No module named heat3d_gamefiles` | Terminal je u krivoj mapi. `cd` u mapu koja sadrži `README.md`. |
| `No module named numpy` (ili drugo ime) | Korak 4 je preskočen. Pokrenite `pip install -r requirements.txt`. |
| `can't open file` / `not found` uz put | Put ima razmake, a nema navodnike, ili je pogrešno upisan. Stavite ga u dvostruke navodnike. |

Više poruka i njihovih rješenja: [Rješavanje problema](../troubleshooting.md).
