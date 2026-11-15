---
title: Aktualizacje
nav_order: 13
lang: "pl"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Aktualizacje {#updates}

3DHeat GameFiles sprawdza wydania tego repozytorium na GitHubie przy starcie, mówi, kiedy jest
nowsza wersja, i proponuje aktualizację. Twoje własne pliki (okrążenia, eksporty) nigdy nie są
ruszane.

Źródło: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Zainstalowana wersja to plik [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION)
repozytorium.

## Sprawdzenie przy starcie {#the-check-at-start-up}

Każde uruchomienie `python -m heat3d_gamefiles ...` wywołuje sprawdzenie, zanim przeanalizuje
argumenty:

- Pyta `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`
  z limitem czasu **5 sekund**.
- Odpowiedź jest zapamiętana na **6 godzin** w
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (albo `~/.cache/3DHeat/...`,
  gdy nie ma `LOCALAPPDATA`). W tym czasie nie wysyła się żadne zapytanie. Również „brak wydania”
  (HTTP 404) jest zapamiętywany.
- Gdy jesteś offline, trafisz na limit zapytań albo działasz za proxy, sprawdzenie po prostu
  się kończy i narzędzie działa w wersji, którą ma.
- Jeśli tag najnowszego wydania (`v1.2.3` albo `1.2.3`; wszystko po `-` lub `+` jest ignorowane)
  jest nowszy niż `VERSION`, na stderr pojawia się komunikat:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **W terminalu** (stdin i stderr są TTY) program pyta `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` albo `ja` aktualizuje. Po udanej aktualizacji **to samo polecenie
  startuje ponownie** na nowym kodzie, a jego kod wyjścia jest przekazywany dalej.
- **Bez terminala** (zaplanowane uruchomienie, potok) program tylko wypisuje
  ``Run `python -m heat3d_update` in <folder> to update.`` i działa dalej.

## Aktualizacja na żądanie {#updating-on-request}

```
python -m heat3d_update          # aktualizuj do najnowszego wydania, jeśli jest
python -m heat3d_update --check  # tylko powiedz, czy jest nowsze wydanie
```

To zawsze pyta GitHub (bez pamięci podręcznej). Wypisuje `Up to date: 1.0.1.`,
`No release found (...)` albo to, co zrobiło. Kod wyjścia to 1, gdy nie udało się zastosować
aktualizacji.

## Jak stosowana jest aktualizacja {#how-an-update-is-applied}

| Zainstalowane jako | Aktualizacja |
|---|---|
| **klon git** (folder `.git` i `git` w PATH) | `git pull --ff-only`. **Odmowa**, gdy śledzone pliki mają lokalne zmiany: „this checkout has local changes; commit or stash them, then run `git pull`”. Nieśledzone pliki nie blokują |
| **pobrana kopia** | archiwum źródeł wydania (`zipball_url`) jest pobierane i rozpakowywane do folderu tymczasowego, z pominięciem każdej ścieżki, która wychodziłaby poza nie; jego `VERSION` musi być równy wersji wydania, inaczej nic nie jest kopiowane; potem jego pliki są kopiowane do tego folderu |

Przy kopiowaniu z archiwum pliki, które nie należą do wydania (okrążenia, eksporty, wirtualne
środowiska, cokolwiek sam zrobiłeś), zostają nietknięte. Aktualizator próbuje też usunąć moduły
`.py`, które wydanie usunęło z pakietów, żeby stary moduł nie przesłaniał swojego następcy.
Szuka pakietów `heat3d_*` w korzeniu archiwum i jeden poziom niżej i usuwa pliki `.py`, których
wydanie już nie ma.

## Wyłączanie {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Każda wartość inna niż pusta, `0`, `false` lub `no` wyłącza zarówno sprawdzenie przy starcie,
jak i propozycję. `python -m heat3d_update` nadal działa, gdy uruchomisz je ręcznie.
