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

Vai nekad neesat strādājis ar komandrindu? Šī lapa palīdzēs jums no nulles nonākt līdz strādājošam rīkam
apmēram desmit minūtēs. Komandas rakstāt logā, ko sauc par **termināli**, un rīks atbild ar tekstu.

## 1. Uzstādiet Python {#install-python}

1. Dodieties uz [python.org/downloads](https://www.python.org/downloads/) un lejupielādējiet
   **Python 3.10 vai jaunāku versiju**.
2. Palaidiet instalētāju. Pirmajā ekrānā atzīmējiet **"Add python.exe to PATH"**,
   tad noklikšķiniet **Install Now**.

## 2. Iegūstiet rīku {#get-the-tool}

- **Ar git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez git:** [GitHub lapā](https://github.com/Holdi601/3DHeat-GameFiles)
  noklikšķiniet zaļo pogu **Code**, tad **Download ZIP**, un izpakojiet to.

## 3. Atveriet termināli rīka mapē {#open-a-terminal-in-the-tools-folder}

- Failu pārlūkā atveriet mapi, kurā ir `README.md`. Noklikšķiniet adreses joslā,
  ierakstiet `cmd` un nospiediet Enter. Atveras melns logs, kas jau ir šajā mapē.
- Vai atveriet **Windows Terminal** un ieejiet mapē ar `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Uzstādiet, ko rīks vajag {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Jums vajadzētu redzēt rindas, kas beidzas ar `Successfully installed ...`.

## 5. Pārbaudiet, ka rīks darbojas {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Jums vajadzētu redzēt `usage: heat3d_gamefiles [-h]` un komandu sarakstu (`identify`,
`list`, `extract`, `course`, ...). Tas nozīmē, ka viss ir kārtībā: rīks ir gatavs.

## Piemēru lasīšana {#reading-the-examples}

- `<kaut kas>` ir **vietturis**: ierakstiet savu vērtību bez leņķiekavām. `<lap file>` kļūst, piemēram, par `laps\my_lap.json`.
- `[--option]` kvadrātiekavās ir **izvēles**: izlaidiet, ja tā nav vajadzīgs.
- Ceļš ar atstarpēm vajag **dubultās pēdiņas**: `"C:\My Games\lap.json"`.
- Katru komandu izpildiet rīka mapē (3. solis).

## Ja kaut kas noiet greizi {#when-something-goes-wrong}

| Jūs redzat | Ko darīt |
|---|---|
| `'python' is not recognized` | Python nav uzstādīts vai "Add to PATH" nebija atzīmēts. Palaidiet instalētāju vēlreiz, atzīmējiet to un atveriet jaunu termināli. |
| `No module named heat3d_gamefiles` | Termināls ir nepareizā mapē. Ar `cd` ieejiet mapē, kurā ir `README.md`. |
| `No module named numpy` (vai cits nosaukums) | 4. solis netika izpildīts. Palaidiet `pip install -r requirements.txt`. |
| `can't open file` / `not found` ar ceļu | Ceļā ir atstarpes bez pēdiņām vai ir drukas kļūda. Ieliekiet to dubultās pēdiņās. |

Citi ziņojumi un to labojumi: [Problēmu risināšana](../troubleshooting.md).
