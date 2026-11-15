---
title: Oppdateringer
nav_order: 13
lang: "no"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Oppdateringer {#updates}

3DHeat GameFiles sjekker dette repoets GitHub-utgivelser når det starter, sier fra når en nyere
versjon er ute, og tilbyr å oppdatere. Dine egne filer (runder, eksporter) røres aldri.

Kilde: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Den installerte versjonen er repoets
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION)-fil.

## Sjekken ved oppstart {#the-check-at-start-up}

Hver `python -m heat3d_gamefiles ...`-kjøring kaller sjekken før den tolker argumentene:

- Den spør `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  med en tidsgrense på **5 sekunder**.
- Svaret bufres i **6 timer** i `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (eller
  `~/.cache/3DHeat/...` uten `LOCALAPPDATA`). I den tiden sendes ingen forespørsel. "Ingen utgivelse
  ennå" (HTTP 404) bufres også.
- Frakoblet, rate-begrenset eller bak en proxy returnerer sjekken bare, og verktøyet kjører på
  versjonen det har.
- Hvis taggen til den siste utgivelsen (`v1.2.3` eller `1.2.3`; alt etter `-` eller `+` ignoreres) er
  nyere enn `VERSION`, skrives dette til standardfeil:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **I en terminal** (stdin og stderr er begge en TTY) spør den `Update now? [Y/n]`. Enter, `y`,
  `yes`, `j` eller `ja` oppdaterer. Etter en vellykket oppdatering **startes den samme kommandoen
  på nytt** med den nye koden, og avslutningskoden sendes videre.
- **Uten terminal** (en planlagt kjøring, en pipe) skriver den bare
  ``Run `python -m heat3d_update` in <folder> to update.`` og fortsetter.

## Oppdatering på forespørsel {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Dette spør alltid GitHub (ingen buffer). Den skriver `Up to date: 1.0.1.`,
`No release found (...)`, eller hva den gjorde. Avslutningskoden er 1 hvis oppdateringen ikke
kunne brukes.

## Hvordan en oppdatering brukes {#how-an-update-is-applied}

| Installert som | Oppdatering |
|---|---|
| en **git-klon** (en `.git`-mappe og `git` på PATH) | `git pull --ff-only`. **Avvist** så lenge sporede filer har lokale endringer: "this checkout has local changes; commit or stash them, then run `git pull`". Usporede filer blokkerer ikke |
| en **nedlastet kopi** | kildearkivet til utgivelsen (`zipball_url`) lastes ned og pakkes ut i en midlertidig mappe, og ignorerer enhver sti som ville rømme ut av den; dens `VERSION` må være lik utgivelsens versjon, ellers kopieres ingenting; deretter kopieres filene over denne mappen |

Når det kopieres fra et arkiv, lar man filer som ikke er del av utgivelsen (runder, eksporter,
virtuelle miljøer, alt du lagde) være i fred. Oppdateringen prøver også å slette `.py`-moduler en
utgivelse har fjernet fra pakkene sine, så en utdatert modul ikke kan skygge for erstatningen. Den
ser etter `heat3d_*`-pakker i arkivroten og ett nivå ned, og fjerner `.py`-filer utgivelsen ikke
lenger har.

## Slå det av {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Enhver verdi annen enn tom, `0`, `false` eller `no` slår av både oppstartssjekken og tilbudet.
`python -m heat3d_update` fungerer fortsatt når du kjører den selv.
