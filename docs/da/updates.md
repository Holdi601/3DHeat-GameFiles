---
title: "Opdateringer"
nav_order: 13
lang: "da"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Opdateringer {#updates}

3DHeat GameFiles tjekker dette repositorys GitHub-udgivelser, når det starter, siger til,
når en nyere version er ude, og tilbyder at opdatere. Dine egne filer (omgange,
eksporter) bliver aldrig rørt.

Kilde: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Den installerede version er repositoryets
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION)-fil.

## Tjekket ved opstart {#the-check-at-start-up}

Hver `python -m heat3d_gamefiles ...`-kørsel kalder tjekket, før den læser sine argumenter:

- Den spørger `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  med en **5 sekunders** timeout.
- Svaret gemmes i **6 timer** i
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (eller
  `~/.cache/3DHeat/...` uden `LOCALAPPDATA`). Inden for den tid sendes ingen forespørgsel.
  "Ingen udgivelse endnu" (HTTP 404) gemmes også.
- Uden internetforbindelse, ved hastighedsbegrænsning eller bag en proxy vender tjekket blot tilbage, og værktøjet
  kører på den version, det har.
- Hvis den seneste udgivelses tag (`v1.2.3` eller `1.2.3`; alt efter `-` eller `+` ignoreres) er
  nyere end `VERSION`, skrives følgende til stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **I en terminal** (stdin og stderr er begge en TTY) spørger den `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` eller `ja` opdaterer. Efter en vellykket opdatering **startes
  den samme kommando igen** på den nye kode, og dens afslutningskode videregives.
- **Uden terminal** (en planlagt kørsel, en pipe) skriver den kun
  ``Run `python -m heat3d_update` in <folder> to update.`` og fortsætter.

## Opdater efter behov {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Dette spørger altid GitHub (ingen cache). Den skriver `Up to date: 1.0.1.`,
`No release found (...)`, eller hvad den gjorde. Afslutningskoden er 1, hvis opdateringen
ikke kunne gennemføres.

## Sådan gennemføres en opdatering {#how-an-update-is-applied}

| Installeret som | Opdatering |
|---|---|
| en **git-klon** (en `.git`-mappe og `git` på PATH) | `git pull --ff-only`. **Afvist**, mens sporede filer har lokale ændringer: "this checkout has local changes; commit or stash them, then run `git pull`". Usporede filer blokerer ikke |
| en **downloadet kopi** | udgivelsens kildearkiv (`zipball_url`) hentes og pakkes ud i en midlertidig mappe, og stier, der ville slippe ud af den, ignoreres; dens `VERSION` skal være lig med udgivelsens version, ellers kopieres intet; derefter kopieres dens filer over denne mappe |

Når der kopieres fra et arkiv, lades filer, der ikke er en del af udgivelsen (omgange, eksporter, virtuelle
miljøer, alt du selv har lavet), være i fred. Opdateringen forsøger
også at slette `.py`-moduler, som en udgivelse har fjernet fra sine pakker, så et forældet
modul ikke kan skygge for sin afløser. Den leder efter `heat3d_*`-pakker i arkivets rod og én mappe
under, og fjerner `.py`-filer, udgivelsen ikke længere har.

## Slå det fra {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Enhver værdi undtagen tom, `0`, `false` eller `no` slår både tjekket ved opstart og tilbuddet fra. `python -m heat3d_update` virker stadig, når den køres i hånden.
