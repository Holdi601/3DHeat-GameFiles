---
title: "Posodobitve"
nav_order: 13
lang: "sl"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Posodobitve {#updates}

3DHeat GameFiles ob zagonu preveri izdaje na GitHubu za ta repozitorij, pove, ali je na voljo novejša različica, in ponudi posodobitev. Vaše lastne datoteke (krogi, izvozi) se nikoli ne spremenijo.

Vir: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Nameščena različica je datoteka [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) v repozitoriju.

## Preverjanje ob zagonu {#the-check-at-start-up}

Vsak zagon `python -m heat3d_gamefiles ...` pokliče preverjanje, preden obdela svoje argumente:

- Vpraša `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, s časovno omejitvijo **5 sekund**.
- Odgovor se shrani v predpomnilnik za **6 ur** v `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (oziroma `~/.cache/3DHeat/...`, če ni `LOCALAPPDATA`). V tem času se ne pošlje nobena zahteva. Tudi odgovor »še ni izdaje« (HTTP 404) je shranjen v predpomnilnik.
- Brez povezave, pri omejitvi števila zahtev ali za proxyjem preverjanje preprosto vrne rezultat, orodje pa teče na svoji različici.
- Če je oznaka (tag) najnovejše izdaje (`v1.2.3` ali `1.2.3`; vse za `-` ali `+` se ignorira) novejša od `VERSION`, izpiše na stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **V terminalu** (stdin in stderr sta oba TTY) vpraša `Update now? [Y/n]`. Enter, `y`, `yes`, `j` ali `ja` posodobi. Po uspešni posodobitvi se **isti ukaz znova zažene** na novi kodi, njegova izhodna koda pa se posreduje naprej.
- **Brez terminala** (načrtovan zagon, cev) samo izpiše ``Run `python -m heat3d_update` in <folder> to update.`` in nadaljuje.

## Posodobitev na zahtevo {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

To vedno vpraša GitHub (brez predpomnilnika). Izpiše `Up to date: 1.0.1.`, `No release found (...)` ali kaj je naredilo. Izhodna koda je 1, če posodobitve ni bilo mogoče uveljaviti.

## Kako se posodobitev uveljavi {#how-an-update-is-applied}

| Nameščeno kot | Posodobitev |
|---|---|
| **klon git** (mapa `.git` in `git` v PATH) | `git pull --ff-only`. **Zavrnjeno**, dokler sledene datoteke kažejo lokalne spremembe: "this checkout has local changes; commit or stash them, then run `git pull`". Nesledene datoteke posodobitve ne ovirajo |
| **prenesena kopija** | izvorni arhiv izdaje (`zipball_url`) se prenese in razpakira v začasno mapo, pri tem se prezre vsaka pot, ki bi ušla iz nje; njegov `VERSION` mora biti enak različici izdaje, sicer se ne kopira ničesar; nato se njegove datoteke prekopirajo v to mapo |

Pri kopiranju iz arhiva se datoteke, ki niso del izdaje (krogi, izvozi, virtualna okolja, vse, kar ste sami naredili), pustijo pri miru. Posodabljalnik poskusi tudi izbrisati module `.py`, ki jih je izdaja odstranila iz svojih paketov, da zastarel modul ne bi zasenčil svojega nadomestka. Išče pakete `heat3d_*` v korenu arhiva in eno mapo globlje ter odstrani datoteke `.py`, ki jih izdaja več nima.

## Izklop {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Vsaka vrednost, razen prazne, `0`, `false` ali `no`, izklopi tako preverjanje ob zagonu kot ponudbo. `python -m heat3d_update` še vedno deluje, kadar ga zaženete ročno.
