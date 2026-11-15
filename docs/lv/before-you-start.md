---
title: Pirms sākat
nav_order: 2
lang: lv
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Pirms sākat {#before-you-start}

Vai nekad neesi strādājis ar komandrindu? Šī lapa palīdzēs tev no nulles nonākt līdz strādājošam rīkam
apmēram desmit minūtēs. Komandas raksti logā, ko sauc par **termināli**, un rīks atbild ar tekstu.

## 1. Instalē Python {#install-python}

1. Ej uz [python.org/downloads](https://www.python.org/downloads/) un lejupielādē
   **Python 3.10 vai jaunāku versiju**.
2. Palaid instalētāju. Pirmajā ekrānā atzīmē **"Add python.exe to PATH"**,
   tad noklikšķini **Install Now**.

## 2. Iegūsti rīku {#get-the-tool}

- **Ar git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez git:** [GitHub lapā](https://github.com/Holdi601/3DHeat-GameFiles)
  noklikšķini zaļo pogu **Code**, tad **Download ZIP**, un izpako to.

## 3. Atver terminali rīka mapē {#open-a-terminal-in-the-tools-folder}

- Failu pārlūkā atver mapi, kurā ir `README.md`. Noklikšķini adreses joslā,
  ieraksti `cmd` un nospied Enter. Atveras melns logs, jau šajā mapē.
- Vai atver **Windows Terminal** un ieej mapē ar `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Uzstādi, ko rīks vajag {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Tev vajadzētu redzēt rindas, kas beidzas ar `Successfully installed ...`.

## 5. Pārbaudi, ka rīks darbojas {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Tev vajadzētu redzēt `usage: heat3d_gamefiles [-h]` un komandu sarakstu (`identify`,
`list`, `extract`, `course`, ...). Tas nozīmē, ka viss ir kārtībā: rīks ir gatavs.

## Piemēru lasīšana {#reading-the-examples}

- `<kaut kas>` ir **vietturis**: ieraksti savu vērtību bez leņķiekavām. `<lap file>` kļūst, piemēram, par `laps\my_lap.json`.
- `[--option]` kvadrātiekavās ir **izvēles**: izlaid, ja tā nav vajadzīgs.
- Ceļš ar atstarpēm vajag **dubultās pēdiņas**: `"C:\My Games\lap.json"`.
- Katru komandu izpildi rīka mapē (3. solis).

## Ja kaut kas noiet greizi {#when-something-goes-wrong}

| Tu redzi | Ko darīt |
|---|---|
| `'python' is not recognized` | Python nav uzstādīts vai "Add to PATH" nebija atzīmēts. Palaid instalētāju vēlreiz, atzīmē to un atver jaunu termināli. |
| `No module named heat3d_gamefiles` | Terminālis ir nepareizā mapē. Ar `cd` ieej mapē, kurā ir `README.md`. |
| `No module named numpy` (vai cits nosaukums) | 4. solis netika izpildīts. Palaid `pip install -r requirements.txt`. |
| `can't open file` / `not found` ar ceļu | Ceļā ir atstarpes bez pēdiņām vai ir drukas kļūda. Ieliec to dubultās pēdiņās. |

Citi ziņojumi un to labojumi: [Problēmu risināšana](../troubleshooting.md).
