---
title: "Frissítések"
nav_order: 13
lang: "hu"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Frissítések {#updates}

A 3DHeat GameFiles indításkor ellenőrzi ennek a tárolónak a GitHub-kiadásait, megmondja, ha
újabb verzió jelent meg, és felajánlja a frissítést. A saját fájljaidhoz (körök, exportok) soha nem
nyúl.

Forrás: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
A telepített verzió a tároló
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) fájlja.

## Az ellenőrzés indításkor {#the-check-at-start-up}

Minden `python -m heat3d_gamefiles ...` futtatás meghívja az ellenőrzést, mielőtt feldolgozná az
argumentumait:

- Lekérdezi a `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` címet, **5
  másodperces** időkorláttal.
- A választ **6 órán** át gyorsítótárazza a
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` fájlban (vagy `~/.cache/3DHeat/...`,
  ha nincs `LOCALAPPDATA`). Ez idő alatt nem történik kérés. A "még nincs kiadás" (HTTP 404) válasz is
  gyorsítótárazódik.
- Offline, kérésszám-korlátozás esetén vagy proxy mögött az ellenőrzés egyszerűen visszatér, és az
  eszköz a saját verzióján fut tovább.
- Ha a legújabb kiadás címkéje (`v1.2.3` vagy `1.2.3`; a `-` vagy `+` utáni rész figyelmen kívül
  marad) újabb a `VERSION`-nél, az stderr-re ír:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Terminálban** (a stdin és a stderr is TTY) rákérdez: `Update now? [Y/n]`. Enter, `y`, `yes`, `j`
  vagy `ja` frissít. Sikeres frissítés után **ugyanaz a parancs indul újra** az új kódon, és a
  kilépési kódja tovább adódik.
- **Terminál nélkül** (ütemezett futtatás, csővezeték) csak kiírja a
  ``Run `python -m heat3d_update` in <folder> to update.`` üzenetet, és folytatja.

## Frissítés kérésre {#updating-on-request}

```
python -m heat3d_update          # frissítés a legújabb kiadásra, ha van
python -m heat3d_update --check  # csak azt mondja meg, van-e újabb kiadás
```

Ez mindig megkérdezi a GitHubot (gyorsítótár nélkül). Kiírja a `Up to date: 1.0.1.` üzenetet, a
`No release found (...)` üzenetet, vagy azt, amit tett. A kilépési kód 1, ha a frissítést nem lehetett
alkalmazni.

## Hogyan alkalmazódik a frissítés {#how-an-update-is-applied}

| Telepítve mint | Frissítés |
|---|---|
| **git-klón** (van `.git` mappa és `git` a PATH-ban) | `git pull --ff-only`. **Elutasítja**, amíg a követett fájloknak helyi változtatásai vannak: "this checkout has local changes; commit or stash them, then run `git pull`". A nem követett fájlok nem akadályozzák |
| **letöltött másolat** | a kiadás forrásarchívuma (`zipball_url`) letöltődik és egy ideiglenes mappába kicsomagolódik, figyelmen kívül hagyva minden olyan útvonalat, amely kilépne belőle; a `VERSION`-jének egyeznie kell a kiadás verziójával, különben semmi nem másolódik; majd a fájlok átmásolódnak ebbe a mappába |

Archívumból másoláskor a kiadás részét nem képező fájlok (körök, exportok, virtuális környezetek,
bármi, amit te készítettél) érintetlenek maradnak. A frissítő megpróbálja törölni azokat a `.py`
modulokat is, amelyeket egy kiadás eltávolított a csomagjaiból, hogy egy elavult modul ne takarja el a
helyettesítőjét. A `heat3d_*` csomagokat az archívum gyökerében és eggyel lejjebb keresi, és törli azokat
a `.py` fájlokat, amelyek a kiadásban már nincsenek meg.

## Kikapcsolás {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Az üres, `0`, `false` vagy `no` értéktől eltérő bármilyen érték kikapcsolja az indulási ellenőrzést
és a felajánlást is. A `python -m heat3d_update` kézzel futtatva továbbra is működik.
