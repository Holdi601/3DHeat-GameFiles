---
title: "Para se të fillosh"
nav_order: 2
lang: "sq"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Para se të fillosh {#before-you-start}

Je i ri me rreshtin e komandave? Kjo faqe të çon nga zero te një mjet që funksionon në
rreth dhjetë minuta. Shkruaj komanda në një dritare të quajtur **terminal**, dhe
mjeti përgjigjet me tekst.

## 1. Instalo Python {#install-python}

1. Shko te [python.org/downloads](https://www.python.org/downloads/) dhe shkarko
   **Python 3.10 ose më të ri**.
2. Nis instaluesin. Në ekranin e parë, zgjidh **"Add python.exe to PATH"**,
   pastaj kliko **Install Now**.

## 2. Merr mjetin {#get-the-tool}

- **Me git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Pa git:** te [faqja e GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  kliko butonin jeshil **Code**, pastaj **Download ZIP**, dhe shpaketoje.

## 3. Hap një terminal në dosjen e mjetit {#open-a-terminal-in-the-tools-folder}

- Në File Explorer, hap dosjen që mban `README.md`. Kliko te shiriti i
  adresës, shkruaj `cmd` dhe shtyp Enter. Hapet një dritare e zezë, tashmë brenda asaj dosjeje.
- Ose hap **Windows Terminal** dhe shko aty me `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Instalo çfarë i duhet mjetit {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Duhet të shohësh rreshta që mbarojnë me `Successfully installed ...`.

## 5. Kontrollo që funksionon {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Duhet të shohësh `usage: heat3d_gamefiles [-h]` dhe një listë foljesh (`identify`,
`list`, `extract`, `course`, ...). Kjo është sukses: mjeti është gati.

## Leximi i shembujve {#reading-the-examples}

- `<something>` është një **vendmbajtës**: shkruaj vlerën tënde në vend të tij, pa
  kllapat këndore. `<lap file>` bëhet, për shembull, `laps\my_lap.json`.
- `[--option]` në kllapa katrore është **opsional**: lëre jashtë nëse nuk të duhet.
- Një shteg me hapësira ka nevojë për **thonjëza të dyfishta**: `"C:\My Games\lap.json"`.
- Ekzekuto çdo komandë në dosjen e mjetit (hapi 3).

## Kur diçka shkon keq {#when-something-goes-wrong}

| Çfarë sheh | Çfarë të bësh |
|---|---|
| `'python' is not recognized` | Python nuk është instaluar, ose "Add to PATH" nuk u zgjodh. Nis përsëri instaluesin dhe zgjidhe, pastaj hap një terminal të ri. |
| `No module named heat3d_gamefiles` | Terminali është në dosjen e gabuar. Bëj `cd` te dosja që mban `README.md`. |
| `No module named numpy` (ose emër tjetër) | Hapi 4 u anashkalua. Ekzekuto `pip install -r requirements.txt`. |
| `can't open file` / `not found` me një shteg | Shtegu ka hapësira pa thonjëza, ose një gabim shkrimi. Vendose në thonjëza të dyfishta. |

Më shumë mesazhe dhe zgjidhjet e tyre: [Zgjidhja e problemeve](troubleshooting.md).
