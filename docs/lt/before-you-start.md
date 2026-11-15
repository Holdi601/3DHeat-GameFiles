---
title: "Prieš pradedant"
nav_order: 2
lang: "lt"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Prieš pradedant {#before-you-start}

Nesate įpratę prie komandinės eilutės? Šis puslapis padės nuo nieko iki veikiančio įrankio maždaug per dešimt minučių, vieną kartą.
Komandas rašote į langą, vadinamą **terminalu**, o įrankis atsako tekstu.

## 1. Įdiekite Python {#install-python}

1. Eikite į [python.org/downloads](https://www.python.org/downloads/) ir atsisiųskite
   **Python 3.10 ar naujesnę versiją**.
2. Paleiskite diegimo programą. Pirmame ekrane pažymėkite **„Add python.exe to PATH“**,
   tada spustelėkite **Install Now**.

## 2. Gaukite įrankį {#get-the-tool}

- **Su git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Be git:** [GitHub puslapyje](https://github.com/Holdi601/3DHeat-GameFiles)
  spustelėkite žalią mygtuką **Code**, tada **Download ZIP**, ir išskleiskite.

## 3. Atidarykite terminalą įrankio aplanke {#open-a-terminal-in-the-tools-folder}

- Failų naršyklėje atidarykite aplanką, kuriame yra `README.md`. Spustelėkite adresų juostą,
  įrašykite `cmd` ir paspauskite Enter. Atsidaro juodas langas, jau tame aplanke.
- Arba atidarykite **Windows Terminal** ir nueikite ten su `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Įdiekite tai, ko įrankiui reikia {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Turėtumėte matyti eilutes, baigiančias `Successfully installed ...`.

## 5. Patikrinkite, ar veikia {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Turėtumėte matyti `usage: heat3d_gamefiles [-h]` ir veiksmažodžių sąrašą (`identify`,
`list`, `extract`, `course`, ...). Tai sėkmė: įrankis paruoštas.

## Pavyzdžių skaitymas {#reading-the-examples}

- `<something>` yra **vietos žymeklis**: vietoj jo įrašykite savo reikšmę, be kampinių skliaustų.
  `<lap file>` taps, pavyzdžiui, `laps\my_lap.json`.
- `[--option]` laužtiniuose skliaustuose yra **neprivaloma**: nerašykite, jei jos nereikia.
- Kelias su tarpais reikalauja **dvigubų kabučių**: `"C:\My Games\lap.json"`.
- Visas komandas vykdykite įrankio aplanke (3 žingsnis).

## Kai kas nors neveikia {#when-something-goes-wrong}

| Matote | Ką daryti |
|---|---|
| `'python' is not recognized` | Python neįdiegtas arba nepažymėtas „Add to PATH“. Paleiskite diegimo programą iš naujo, pažymėkite ir atidarykite naują terminalą. |
| `No module named heat3d_gamefiles` | terminalas yra ne tame aplanke. `cd` į aplanką, kuriame yra `README.md`. |
| `No module named numpy` (ar kitas vardas) | praleistas 4 žingsnis. Vykdykite `pip install -r requirements.txt`. |
| `can't open file` / `not found` su keliu | kelias turi tarpų be kabučių arba klaidą. Įdėkite jį į dvigubas kabutes. |

Daugiau pranešimų ir jų taisymų: [Trikčių šalinimas](../troubleshooting.md).
