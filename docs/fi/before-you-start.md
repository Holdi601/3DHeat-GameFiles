---
title: "Ennen aloittamista"
nav_order: 2
lang: fi
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Ennen aloittamista {#before-you-start}

Uusi komentorivin kanssa? Tämä sivu vie sinut nollasta toimivaan työkaluun noin
kymmenessä minuutissa. Kirjoitat komentoja **päätteeseen**, ikkunaan, ja työkalu vastaa tekstillä.

## 1. Asenna Python {#install-python}

1. Mene osoitteeseen [python.org/downloads](https://www.python.org/downloads/) ja lataa
   **Python 3.10 tai uudempi**.
2. Suorita asennusohjelma. Ensimmäisellä näytöllä rastita **"Add python.exe to PATH"**,
   ja napsauta sitten **Install Now**.

## 2. Hae työkalu {#get-the-tool}

- **Gitillä:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Ilman gitiä:** [GitHub-sivulla](https://github.com/Holdi601/3DHeat-GameFiles)
  napsauta vihreää **Code**-painiketta ja sitten **Download ZIP**, ja pura zip.

## 3. Avaa pääte työkalun kansiossa {#open-a-terminal-in-the-tools-folder}

- Avaa File Explorerissa kansio, jossa on `README.md`. Napsauta osoitepalkkiin, kirjoita
  `cmd` ja paina Enter. Musta ikkuna aukeaa, jo oikeassa kansiossa.
- Tai avaa **Windows Terminal** ja siirry sinne komennolla `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Asenna työkalun tarvitsemat {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Lopussa pitäisi näkyä rivejä, jotka päättyvät `Successfully installed ...`.

## 5. Tarkista, että se toimii {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Pitäisi näkyä `usage: heat3d_gamefiles [-h]` ja luettelo komennoista (`identify`,
`list`, `extract`, `course` ...). Se tarkoittaa onnistumista: työkalu on valmis.

## Esimerkkien lukeminen {#reading-the-examples}

- `<jotain>` on **paikanpitäjä**: kirjoita oma arvosi sen tilalle ilman kulmasulkuja.
  `<lap file>` muuttuu esimerkiksi muotoon `laps\my_lap.json`.
- Hakasulkeissa oleva `[--option]` on **valinnainen**: jätä pois, jos et tarvitse sitä.
- Välilyöntejä sisältävä polku tarvitsee **lainausmerkit**: `"C:\My Games\lap.json"`.
- Suorita jokainen komento työkalun kansiossa (vaihe 3).

## Kun jokin menee pieleen {#when-something-goes-wrong}

| Näet | Mitä tehdä |
|---|---|
| `'python' is not recognized` | Pythonia ei ole asennettu, tai "Add to PATH" ei ollut rastitettu. Suorita asennusohjelma uudelleen ja rastita ruutu, avaa sitten uusi pääte. |
| `No module named heat3d_gamefiles` | Pääte on väärässä kansiossa. `cd` kansioon, jossa `README.md` on. |
| `No module named numpy` (tai muu nimi) | Vaihe 4 jäi väliin. Suorita `pip install -r requirements.txt`. |
| `can't open file` / `not found` polun kanssa | Polussa on välilyöntejä ilman lainausmerkkejä, tai siinä on kirjoitusvirhe. Laita se kaksinkertaisiin lainausmerkkeihin. |

Lisää viestejä ja niiden korjauksia: [Vianmääritys](../troubleshooting.md).
