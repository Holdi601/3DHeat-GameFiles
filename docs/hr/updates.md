---
title: "Ažuriranja"
nav_order: 13
lang: "hr"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Ažuriranja {#updates}

3DHeat GameFiles pri pokretanju provjerava GitHub izdanja ovog repozitorija, kaže kad je izašla novija verzija i nudi ažuriranje. Vaše vlastite datoteke (krugovi, izvozi) se nikad ne diraju.

Izvor: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Instalirana verzija je datoteka [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) ovog repozitorija.

## Provjera pri pokretanju {#the-check-at-start-up}

Svako pokretanje `python -m heat3d_gamefiles ...` poziva provjeru prije nego obradi argumente:

- Pita `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, s vremenskim ograničenjem od **5 sekundi**.
- Odgovor se sprema u predmemoriju **6 sati**, u `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (ili `~/.cache/3DHeat/...` bez `LOCALAPPDATA`). Unutar tog vremena ne šalje se zahtjev. I odgovor „još nema izdanja” (HTTP 404) sprema se u predmemoriju.
- Bez mreže, s ograničenjem broja zahtjeva ili iza proxyja, provjera jednostavno vraća i alatka radi na verziji koju ima.
- Ako je oznaka najnovijeg izdanja (`v1.2.3` ili `1.2.3`; sve iza `-` ili `+` se ignorira) novija od `VERSION`, ispisuje na stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **U terminalu** (stdin i stderr su oba TTY) pita `Update now? [Y/n]`. Enter, `y`, `yes`, `j` ili `ja` ažurira. Nakon uspješnog ažuriranja **ista naredba se ponovo pokreće** na novom kodu, a njezin izlazni kod se prosljeđuje.
- **Bez terminala** (zakazano pokretanje, cijev) samo ispisuje poruku ``Run `python -m heat3d_update` in <folder> to update.`` i nastavlja.

## Ažuriranje na zahtjev {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Ovo uvijek pita GitHub (bez predmemorije). Ispisuje `Up to date: 1.0.1.`, `No release found (...)` ili što je učinilo. Izlazni kod je 1 ako se ažuriranje nije moglo primijeniti.

## Kako se ažuriranje primjenjuje {#how-an-update-is-applied}

| Instalirano kao | Ažuriranje |
|---|---|
| **git klon** (mapa `.git` i `git` na PATH-u) | `git pull --ff-only`. **Odbija se** dok praćene datoteke imaju lokalne promjene: „this checkout has local changes; commit or stash them, then run `git pull`”. Nepraćene datoteke ga ne blokiraju |
| **preuzeta kopija** | izvorni arhiv izdanja (`zipball_url`) preuzima se i raspakira u privremenu mapu, uz ignoriranje svake putanje koja bi izašla van nje. Njegov `VERSION` mora biti jednak verziji izdanja, inače se ništa ne kopira. Zatim se njegove datoteke kopiraju preko ove mape |

Kad se kopira iz arhive, datoteke koje nisu dio izdanja (krugovi, izvozi, virtualna okruženja, sve što ste sami napravili) ostaju netaknute. Ažuriranje također pokušava obrisati `.py` module koje je izdanje uklonilo iz svojih paketa, tako da zastarjeli modul ne može zasjeniti svoju zamjenu. Traži `heat3d_*` pakete u korijenu arhive i jednu mapu niže te briše `.py` datoteke koje izdanje više nema.

## Isključivanje {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Bilo koja vrijednost osim prazne, `0`, `false` ili `no` isključuje i provjeru pri pokretanju i ponudu. `python -m heat3d_update` i dalje radi kad se pokrene ručno.
