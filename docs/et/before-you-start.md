---
title: "Enne alustamist"
nav_order: 2
lang: "et"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Enne alustamist {#before-you-start}

Pole sul käsurealt kogemust? See leht viib sind nullist töötava tööriistani umbes kümne minutiga.
Kirjutad käske aknasse, mida nimetatakse **terminaliks**, ja tööriist vastab tekstiga.

## 1. Paigalda Python {#install-python}

1. Mine lehele [python.org/downloads](https://www.python.org/downloads/) ja laadi alla **Python 3.10 või uuem**.
2. Käivita installer. Selle esimesel ekraanil märgi **"Add python.exe to PATH"**,
   seejärel klõpsa **Install Now**.

## 2. Hangi tööriist {#get-the-tool}

- **Gitiga:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Ilma gitita:** lehel [GitHubi leht](https://github.com/Holdi601/3DHeat-GameFiles)
  klõpsa roheline nupp **Code**, seejärel **Download ZIP** ja paki lahti.

## 3. Ava terminal tööriista kaustas {#open-a-terminal-in-the-tools-folder}

- Ava Windowsi Exploreris kaust, kus on `README.md`. Klõpsa aadressiribale, kirjuta
  `cmd` ja vajuta Enter. Avaneb must aken, mis on juba selles kaustas.
- Või ava **Windows Terminal** ja liigu sinna `cd`-ga:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Paigalda, mida tööriist vajab {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Lõpus peaks näha ridu, mis lõppevad sõnadega `Successfully installed ...`.

## 5. Kontrolli, et see töötab {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Peaksid nägema `usage: heat3d_gamefiles [-h]` ja käskude loendit (`identify`,
`list`, `extract`, `course`, ...). See tähendab edu: tööriist on valmis.

## Näidete lugemine {#reading-the-examples}

- `<something>` on **kohatäide**: kirjuta oma väärtus selle asemel, ilma nurksulgudeta. `<lap file>` saab näiteks väärtuseks `laps\my_lap.json`.
- `[--option]` nurksulgudes on **valikuline**: jäta välja, kui seda ei vaja.
- Tee tühikutega vajab **topeltjutumärke**: `"C:\My Games\lap.json"`.
- Käivita iga käsk tööriista kaustas (samm 3).

## Kui midagi läheb valesti {#when-something-goes-wrong}

| Näed | Mida teha |
|---|---|
| `'python' is not recognized` | Python pole paigaldatud või "Add to PATH" jäi märkimata. Käivita installer uuesti, märgi see ja ava uus terminal. |
| `No module named heat3d_gamefiles` | Terminal on valesti kaustas. `cd` kausta, kus on `README.md`. |
| `No module named numpy` (või mõni muu nimi) | Samm 4 jäi vahele. Käivita `pip install -r requirements.txt`. |
| `can't open file` / `not found` koos teega | Teel on tühikud ja jutumärgid puuduvad, või on kirjavea. Pane see topeltjutumärkidesse. |

Rohkem teateid ja nende parandusi: [Tõrkeotsing](../troubleshooting.md).
