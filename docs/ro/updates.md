---
title: "Actualizări"
nav_order: 13
lang: "ro"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Actualizări {#updates}

3DHeat GameFiles verifică la pornire lansările de pe GitHub ale acestui depozit, spune când a apărut o versiune nouă și oferă să se actualizeze. Fișierele tale (ture, exporturi) nu sunt atinse niciodată.

Sursa: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Versiunea instalată este fișierul [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) al depozitului.

## Verificarea la pornire {#the-check-at-start-up}

Fiecare rulare `python -m heat3d_gamefiles ...` apelează verificarea înainte de a-și analiza argumentele:

- Întreabă `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, cu un timeout de **5 secunde**.
- Răspunsul este salvat în cache timp de **6 ore** în `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (sau `~/.cache/3DHeat/...` fără `LOCALAPPDATA`). În acest interval nu se face nicio cerere. Și „nicio lansare încă” (HTTP 404) este salvat în cache.
- Offline, cu limită de cereri sau în spatele unui proxy, verificarea doar revine, iar instrumentul rulează pe versiunea pe care o are.
- Dacă eticheta ultimei lansări (`v1.2.3` sau `1.2.3`; orice după `-` sau `+` este ignorat) este mai nouă decât `VERSION`, scrie pe stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **La un terminal** (stdin și stderr sunt ambele TTY) întreabă `Update now? [Y/n]`. Enter, `y`, `yes`, `j` sau `ja` actualizează. După o actualizare reușită, **aceeași comandă este pornită din nou** pe codul nou, iar codul ei de ieșire este transmis mai departe.
- **Fără terminal** (o rulare programată, un pipe) afișează doar ``Run `python -m heat3d_update` in <folder> to update.`` și continuă.

## Actualizarea la cerere {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Aceasta întreabă mereu GitHub (fără cache). Afișează `Up to date: 1.0.1.`, `No release found (...)`, sau ce a făcut. Codul de ieșire este 1 dacă actualizarea nu a putut fi aplicată.

## Cum se aplică o actualizare {#how-an-update-is-applied}

| Instalat ca | Actualizare |
|---|---|
| un **clon git** (un folder `.git` și `git` în PATH) | `git pull --ff-only`. **Refuzată** cât timp fișierele urmărite au modificări locale: „this checkout has local changes; commit or stash them, then run `git pull`”. Fișierele neurmărite nu o blochează |
| o **copie descărcată** | arhiva sursă a lansării (`zipball_url`) este descărcată și dezarhivată într-un folder temporar, ignorând orice cale care ar ieși din el; `VERSION` ei trebuie să fie egal cu versiunea lansării, altfel nu se copiază nimic; apoi fișierele ei sunt copiate peste acest folder |

Când copiază dintr-o arhivă, fișierele care nu fac parte din lansare (ture, exporturi, medii virtuale, orice ai făcut tu) sunt lăsate în pace. Actualizatorul încearcă și să șteargă modulele `.py` pe care o lansare le-a scos din pachetele sale, ca un modul vechi să nu umbrească înlocuitorul. Caută pachete `heat3d_*` la rădăcina arhivei și cu un folder mai jos, și șterge fișierele `.py` pe care lansarea nu le mai are.

## Dezactivarea {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Orice valoare în afară de goală, `0`, `false` sau `no` oprește atât verificarea de la pornire, cât și oferta. `python -m heat3d_update` funcționează în continuare când este rulat manual.
