---
title: Przeglądanie archiwów
nav_order: 3
lang: "pl"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Przeglądanie archiwów: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Gra pakuje swoje pliki do dużych pudeł zwanych **archiwami**. Te polecenia patrzą na etykietę
pudła, wypisują, co w nim jest, i wyciągają jedną rzecz.

Zanim wyeksportujesz cokolwiek z nieznanej gry, sprawdź, co ona zawiera. Te cztery polecenia
czytają plik i mówią, czym jest i co zawiera; nie zapisują nic poza jednym wpisem, o który
poprosisz `extract`.

![identify, list i extract uruchomione na małym zip](../assets/img/inspect-archives.svg)

*Przebieg na syntetycznym zipie ułożonym jak poziom BeamNG.drive.*

## Krok po kroku {#step-by-step}

1. **Zapytaj, czym jest plik.** `identify` czyta bajty, a nie rozszerzenie:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Podaje format (Unreal `.pak`, IoStore `.utoc`/`.ucas`, pakiet Unity lub `SerializedFile`,
   Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` lub `.modelbin`, BeamNG `.cdae`/`.ter`,
   zip), jego wersję, liczbę wpisów i to, czy jest zaszyfrowany.

2. **Wypisz zawartość.** `list` drukuje jedną linię na wpis: rozmiar, kompresję, ścieżkę.
   Zawęź wynik przez `--filter`, ogranicz liczbę przez `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Wyciągnij jeden wpis.** `extract` zapisuje jeden wpis (do folderu, w którym jesteś, chyba
   że `--out` wskazuje inaczej), po ścieżce wypisanej przez `list` (albo `#12`, po numerze,
   w `.minizip` bez nazw):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` wypisuje i sprawdza siatki w `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Opcje {#options}

| Polecenie | Opcja | Znaczenie |
|---|---|---|
| `identify` | `<file>` | dowolny plik |
| `list` | `<archive>` | `.pak`, `.utoc` (albo `.ucas` obok niego), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | tylko ścieżki zawierające TEXT |
| | `--limit N` | co najwyżej N linii |
| | `--key HEX` | klucz AES-256 (64 cyfry szesnastkowe), który już masz; potrzebny tylko zaszyfrowany `.pak` |
| `extract` | `<archive> <path>` | archiwum i ścieżka wpisu, tak jak wypisuje ją `list` |
| | `--out FILE` | gdzie zapisać (domyślnie: nazwa pliku wpisu) |
| | `--key HEX` | jak w `list` |
| `meshes` | `<file>`, `--limit N` | `SerializedFile` Unity; co najwyżej N siatek |

Narzędzie nie zawiera kluczy i żadnego nie odzyskuje: zaszyfrowane archiwum otworzy się tylko
z kluczem, który podasz. Plik, którego nie da się odczytać, zostaje odrzucony jedną linią
z kodem wyjścia 1. Każde polecenie i kod wyjścia są opisane na stronie [Polecenia](commands.md);
sposób czytania każdego formatu jest w [Czytnikach archiwów](archive-readers.md).
