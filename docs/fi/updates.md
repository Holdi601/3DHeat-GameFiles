---
title: "Päivitykset"
nav_order: 13
lang: "fi"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Päivitykset {#updates}

3DHeat GameFiles tarkistaa tämän repositorion GitHub-julkaisut käynnistyessään, kertoo, kun uudempi versio on ilmestynyt, ja tarjoaa päivitystä. Omia tiedostojasi (kierroksia, vientejä) ei koskaan kosketa.

Lähde: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Asennettu versio on repositorion
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION)-tiedosto.

## Tarkistus käynnistyksessä {#the-check-at-start-up}

Jokainen `python -m heat3d_gamefiles ...` -ajo kutsuu tarkistuksen ennen kuin se jäsentää argumenttinsa:

- Se kysyy osoitteesta `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` **5 sekunnin** aikarajalla.
- Vastaus tallennetaan välimuistiin **6 tunniksi** tiedostoon `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (tai `~/.cache/3DHeat/...`, jos `LOCALAPPDATA` puuttuu). Sen aikana pyyntöjä ei tehdä. Myös "ei vielä julkaisua" (HTTP 404) tallennetaan välimuistiin.
- Offline-tilassa, pyyntörajan kohdalla tai välityspalvelimen takana tarkistus yksinkertaisesti palaa, ja työkalu toimii sillä versiolla, joka sillä on.
- Jos uusimman julkaisun tagi (`v1.2.3` tai `1.2.3`; kaikki `-`- tai `+`-merkin jälkeinen jätetään huomiotta) on uudempi kuin `VERSION`, se tulostaa stderr-virtaan:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Terminaalissa** (stdin ja stderr ovat molemmat TTY) se kysyy `Update now? [Y/n]`. Enter, `y`, `yes`, `j` tai `ja` päivittää. Onnistuneen päivityksen jälkeen **sama komento käynnistetään uudelleen** uudella koodilla, ja sen poistumiskoodi välitetään eteenpäin.
- **Ilman terminaalia** (ajastettu ajo, putki) se tulostaa vain ``Run `python -m heat3d_update` in <folder> to update.`` ja jatkaa.

## Päivitys pyynnöstä {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Tämä kysyy aina GitHubilta (ei välimuistia). Se tulostaa `Up to date: 1.0.1.`, `No release found (...)` tai kuvauksen siitä, mitä se teki. Poistumiskoodi on 1, jos päivitystä ei voitu toteuttaa.

## Miten päivitys tehdään {#how-an-update-is-applied}

| Asennettu tapana | Päivitys |
|---|---|
| **git-kloonina** (`.git`-kansio ja `git` PATH:ssa) | `git pull --ff-only`. **Estetään**, kun seurattuihin tiedostoihin on paikallisia muutoksia, ja tulostetaan viesti: "this checkout has local changes; commit or stash them, then run `git pull`" (viesti on englanniksi, kuten työkalu sen tulostaa). Seuraamattomat tiedostot eivät estä sitä |
| **ladattu kopio** | julkaisun lähdearkisto (`zipball_url`) ladataan ja puretaan väliaikaiseen kansioon, ohittaen kaikki polut, jotka pääsisivät sen ulkopuolelle. Sen `VERSION` on oltava sama kuin julkaisun version, muuten mitään ei kopioida. Sitten sen tiedostot kopioidaan tämän kansion päälle |

Kun kopioidaan arkistosta, tiedostot, jotka eivät kuulu julkaisuun (kierrokset, viennit, virtuaaliympäristöt, kaikki mitä olet itse tehnyt), jätetään rauhaan. Päivitys yrittää myös poistaa `.py`-moduulit, jotka julkaisu on poistanut paketeistaan, jotta vanha moduuli ei peitä sen korvaajaa. Se etsii `heat3d_*`-paketteja arkiston juuresta ja yhden kansion alta ja poistaa `.py`-tiedostot, joita julkaisulla ei enää ole.

## Pois kytkeminen {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Mikä tahansa muu arvo kuin tyhjä, `0`, `false` tai `no` kytkee pois sekä käynnistystarkistuksen että tarjouksen. `python -m heat3d_update` toimii yhä, kun sen ajaa käsin.
