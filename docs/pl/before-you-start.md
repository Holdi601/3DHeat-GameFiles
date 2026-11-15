---
title: "Zanim zaczniesz"
nav_order: 2
lang: pl
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Zanim zaczniesz {#before-you-start}

Nigdy nie używałeś wiersza poleceń? Ta strona przeprowadzi cię od zera do działającego narzędzia w około
dziesięć minut. Wpisujesz polecenia w oknie zwanym **terminalem**, a narzędzie odpowiada tekstem.

## 1. Zainstaluj Pythona {#install-python}

1. Wejdź na [python.org/downloads](https://www.python.org/downloads/) i pobierz
   **Pythona 3.10 lub nowszego**.
2. Uruchom instalator. Na jego pierwszym ekranie zaznacz **„Add python.exe to PATH”**,
   a potem kliknij **Install Now**.

## 2. Pobierz narzędzie {#get-the-tool}

- **Z gitem:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Bez gita:** na [stronie GitHub](https://github.com/Holdi601/3DHeat-GameFiles)
  kliknij zielony przycisk **Code**, potem **Download ZIP**, i rozpakuj plik.

## 3. Otwórz terminal w folderze narzędzia {#open-a-terminal-in-the-tools-folder}

- W Eksploratorze plików otwórz folder, w którym leży `README.md`. Kliknij pasek adresu,
  wpisz `cmd` i naciśnij Enter. Otworzy się czarne okno, już w tym folderze.
- Albo otwórz **Terminal Windows** i przejdź tam poleceniem `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Zainstaluj to, czego potrzebuje narzędzie {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Powinieneś zobaczyć linie kończące się na `Successfully installed ...`.

## 5. Sprawdź, czy działa {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Powinieneś zobaczyć `usage: heat3d_gamefiles [-h]` oraz listę czasowników (`identify`,
`list`, `extract`, `course`, ...). To znaczy sukces: narzędzie jest gotowe.

## Jak czytać przykłady {#reading-the-examples}

- `<coś>` to **symbol zastępczy**: wpisz zamiast niego własną wartość, bez nawiasów ostrokątnych.
  `<lap file>` staje się na przykład `laps\my_lap.json`.
- `[--option]` w nawiasach kwadratowych jest **opcjonalne**: pomiń je, jeśli nie są ci potrzebne.
- Ścieżka ze spacjami wymaga **cudzysłowów**: `"C:\My Games\lap.json"`.
- Każde polecenie uruchamiaj w folderze narzędzia (krok 3).

## Gdy coś pójdzie nie tak {#when-something-goes-wrong}

| Widzisz | Co zrobić |
|---|---|
| `'python' is not recognized` | Python nie jest zainstalowany albo nie zaznaczono „Add to PATH”. Uruchom instalator ponownie, zaznacz tę opcję, a potem otwórz nowy terminal. |
| `No module named heat3d_gamefiles` | Terminal jest w złym folderze. Wejdź poleceniem `cd` do folderu, w którym leży `README.md`. |
| `No module named numpy` (albo inna nazwa) | Pominięto krok 4. Uruchom `pip install -r requirements.txt`. |
| `can't open file` / `not found` przy ścieżce | Ścieżka ma spacje i nie ma cudzysłowów, albo jest literówka. Ujmij ją w cudzysłowy. |

Więcej komunikatów i ich poprawek: [Rozwiązywanie problemów](../troubleshooting.md).
