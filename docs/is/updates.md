---
title: "Uppfærslur"
nav_order: 13
lang: "is"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Uppfærslur {#updates}

3DHeat GameFiles athugar GitHub-útgáfur þessarar geymslu þegar það ræsist, segir frá
þegar nýrri útgáfa er komin og býðst til að uppfæra. Þínar eigin skrár (hringir,
útflutningur) eru aldrei snertar.

Frumkóði: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Uppsetta útgáfan er skráin
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) í geymslunni.

## Athugunin við ræsingu {#the-check-at-start-up}

Sérhver keyrsla á `python -m heat3d_gamefiles ...` kallar á athugunina áður en hún les
færibreytur sínar:

- Hún spyr `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  með **5 sekúndna** tímamörkum.
- Svarið er vistað í **6 klukkustundir** í
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (eða
  `~/.cache/3DHeat/...` án `LOCALAPPDATA`). Innan þess tíma er engin beiðni
  send. „Engin útgáfa enn“ (HTTP 404) er líka vistuð.
- Án nettengingar, með takmarkaðan hraða eða á bak við milliþjón snýr athugunin einfaldlega til baka og verkfærið
  heldur áfram á útgáfunni sem það hefur.
- Ef merki nýjustu útgáfu (`v1.2.3` eða `1.2.3`; allt á eftir `-` eða `+` er
  hunsað) er nýrra en `VERSION` prentar það á stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Í skipanalínu** (stdin og stderr eru bæði TTY) spyr það `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` eða `ja` uppfærir. Eftir vel heppnaða uppfærslu er **sama
  skipun ræst aftur** á nýja kóðanum og útgöngukóði hennar sendur áfram.
- **Án skipanalínu** (tímasett keyrsla, pípa) prentar það aðeins
  ``Run `python -m heat3d_update` in <folder> to update.`` og heldur áfram.

## Uppfærsla að beiðni {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Þetta spyr alltaf GitHub (engin skyndiminni). Það prentar `Up to date: 1.0.1.`,
`No release found (...)`, eða hvað það gerði. Útgöngukóðinn er 1 ef ekki tókst að
framkvæma uppfærsluna.

## Hvernig uppfærsla er framkvæmd {#how-an-update-is-applied}

| Sett upp sem | Uppfærsla |
|---|---|
| **git-afrit** (`.git` mappa og `git` á PATH) | `git pull --ff-only`. **Hafnað** á meðan raktar skrár hafa staðbundnar breytingar: „this checkout has local changes; commit or stash them, then run `git pull`“. Óraktar skrár hindra það ekki |
| **niðurhalað afrit** | frumkóðasafn útgáfunnar (`zipball_url`) er sótt og pakkað upp í tímabundna möppu, með því að hunsa hverja slóð sem myndi sleppa út úr henni; `VERSION` þess verður að jafngilda útgáfu útgáfunnar, annars er engu afritað; síðan eru skrár þess afritaðar yfir þessa möppu |

Þegar afritað er úr safni eru skrár sem eru ekki hluti af útgáfunni (hringir, útflutningur,
sýndarumhverfi, allt sem þú bjóst til) látnar í friði. Uppfærslan
reynir líka að eyða `.py` einingum sem útgáfa fjarlægði úr pökkum sínum, svo
úrelt eining geti ekki skyggt á arftaka sinn. Hún leitar að `heat3d_*` pökkum
í rót safnsins og einni möppu neðar, og fjarlægir `.py` skrár sem útgáfan
hefur ekki lengur.

## Að slökkva á því {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Hvaða gildi sem er annað en tómt, `0`, `false` eða `no` slekkur bæði á athuguninni við ræsingu
og tilboðinu. `python -m heat3d_update` virkar enn þegar það er keyrt með hendi.
