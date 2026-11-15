---
title: Aktualizácie
nav_order: 13
lang: "sk"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Aktualizácie {#updates}

3DHeat GameFiles pri spustení skontroluje GitHub vydania tohto repozitára, povie, keď je vonku novšia verzia, a ponúkne aktualizáciu. Vaše vlastné súbory (kolá, exporty) sa nikdy nedotknú.

Zdroj: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Nainštalovaná verzia je súbor [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) v repozitári.

## Kontrola pri spustení {#the-check-at-start-up}

Každý beh `python -m heat3d_gamefiles ...` zavolá kontrolu skôr, než spracuje svoje argumenty:

- Pýta sa `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` s časovým limitom **5 sekúnd**.
- Odpoveď sa ukladá do vyrovnávacej pamäte na **6 hodín** v `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (alebo `~/.cache/3DHeat/...` bez `LOCALAPPDATA`). Počas tejto doby sa žiadna požiadavka neposiela. Odpoveď „No release yet“ (HTTP 404) sa ukladá tiež.
- Keď je offline, obmedzený počtom požiadaviek alebo za proxy, kontrola len skončí a nástroj beží na svojej verzii.
- Ak je značka najnovšieho vydania (`v1.2.3` alebo `1.2.3`; všetko za `-` alebo `+` sa ignoruje) novšia než `VERSION`, vypíše na stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **V termináli** (stdin aj stderr sú TTY) sa pýta `Update now? [Y/n]`. Enter, `y`, `yes`, `j` alebo `ja` aktualizuje. Po úspešnej aktualizácii sa **rovnaký príkaz spustí znova** na novom kóde a jeho návratový kód sa odovzdá ďalej.
- **Bez terminálu** (naplánovaný beh, rúra) iba vypíše ``Run `python -m heat3d_update` in <folder> to update.`` a pokračuje ďalej.

## Aktualizácia na požiadanie {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Toto sa vždy pýta GitHubu (bez vyrovnávacej pamäte). Vypíše `Up to date: 1.0.1.`, `No release found (...)` alebo to, čo urobila. Návratový kód je 1, ak sa aktualizácia nedala použiť.

## Ako sa aktualizácia použije {#how-an-update-is-applied}

| Nainštalované ako | Aktualizácia |
|---|---|
| **git clone** (priečinok `.git` a `git` v PATH) | `git pull --ff-only`. **Odmietnutá**, kým sledované súbory majú lokálne zmeny: „this checkout has local changes; commit or stash them, then run `git pull`“. Nesledované súbory ju nebránia |
| **stiahnutá kópia** | zdrojový archív vydania (`zipball_url`) sa stiahne a rozbalí do dočasného priečinka, pričom sa ignoruje každá cesta, ktorá by unikla von; jeho `VERSION` sa musí rovnať verzii vydania, inak sa nič nekopíruje; potom sa jeho súbory prekopírujú do tohto priečinka |

Pri kopírovaní z archívu sa súbory, ktoré nie sú súčasťou vydania (kolá, exporty, virtuálne prostredia, čokoľvek, čo ste vytvorili), nechajú tak. Aktualizátor sa tiež pokúsi zmazať moduly `.py`, ktoré vydanie odstránilo z balíkov, aby zastaraný modul nezatienil svoju náhradu. Hľadá balíky `heat3d_*` v koreni archívu a o jeden priečinok nižšie a odstráni súbory `.py`, ktoré vydanie už nemá.

## Vypnutie {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Ľubovoľná hodnota iná než prázdna, `0`, `false` alebo `no` vypne aj kontrolu pri spustení, aj ponuku. `python -m heat3d_update` funguje aj pri ručnom spustení.
