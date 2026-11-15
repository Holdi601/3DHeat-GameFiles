---
title: Dane okrążenia
nav_order: 7
lang: "pl"
source: lap-inputs.md
source_hash: "76716785ff83"
nav_exclude: true
search_exclude: true
---
# Dane okrążenia {#lap-inputs}

**Plik okrążenia** to lista punktów x, y, z: dokąd pojechał samochód. Najprostszy ręcznie zrobiony to CSV, opisany w punkcie [5. Tabela `.csv`](#5-a-csv-table) poniżej.

Okrążenie mówi eksportowi trasy **dokąd jechał samochód**. Nic innego z niego nie jest używane: prędkość, sterowanie i przeciążenia należą do części telemetrycznej 3DHeat. Narzędzie czyta pozycje w metrach świata gry, a tam, gdzie plik to mówi, także grę i tor.

Źródło: [`lapinput.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/lapinput.py).

## Co przyjmuje `course` {#what-course-accepts}

Format rozpoznaje się po zawartości pliku, nie po nazwie, z jednym wyjątkiem: `.npz` i `.csv` rozpoznaje się po rozszerzeniu, a wszystko inne próbuje się jako JSON.

### 1. Dokument `heat3d-lap` (dowolna gra) {#a-heat3d-lap-document-any-game}

Zapisywany przez rejestratory telemetrii 3DHeat (`heat3d_capture telemetry`, [3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture)):

```json
{
  "format": "heat3d-lap",
  "game": "beamng",
  "track": "Example Stage",
  "channels": {
    "x": [12.0, 12.4, 12.9],
    "y": [3.1, 3.1, 3.2],
    "z": [-40.0, -38.7, -37.3],
    "speed": [21.0, 21.3, 21.8]
  }
}
```

- `channels.x`, `channels.y` i `channels.z` są wymagane. Wiersze, w których którakolwiek z tych trzech wartości nie jest skończoną liczbą, są odrzucane. Pozostałe kanały są ignorowane.
- `game` decyduje o eksporcie (zob. [Polecenia](commands.md#which-game)).
- `track` używa Assetto Corsa Rally, żeby najpierw sprawdzić nazwany etap.
- Osie: y to wysokość. Okrążenia Forzy i AC Rally używają poziomych osi gry tak, jak zapisuje je rejestrator. Okrążenia BeamNG oczekuje się w ramce przeglądarki, `(x, z, -y)` świata BeamNG z osią Z w górę (zob. [BeamNG.drive](course-beamng.md#the-laps-frame)).

### 2. Plik trasy {#a-route-file}

Zapisywany przez `heat3d_capture route` i `heat3d_capture laps`:

```json
{
  "bounds": {"min": [0.0, 80.0, 0.0], "max": [500.0, 140.0, 500.0]},
  "positions": [[12.0, 101.2, 40.5], [12.9, 101.2, 42.0]]
}
```

`positions` to lista `[x, y, z]`. Plik trasy z `bounds`, ale bez pozycji, nadal działa: jego dwa narożniki dają zdegenerowaną linię, ale użyteczne pudełko.

### 3. Plik okrążenia FH Companion {#an-fh-companion-lap-file}

Pliki poszczególnych okrążeń z nagranej biblioteki FH Companion:

```json
{"Lap": {"samples": [{"X": 12.0, "Y": 101.2, "Z": 40.5}, {"X": 12.9, "Y": 101.2, "Z": 42.0}]}}
```

Brakujące `X`, `Y` lub `Z` odczytuje się jako 0. Pliki są zapisywane ze znacznikiem kolejności bajtów, więc cały JSON czyta się jako `utf-8-sig`.

### 4. Nagranie `.npz` {#a-npz-recording}

Archiwum NumPy zawierające tablicę `positions` o kształcie (n, 3).

### 5. Tabela `.csv` {#a-csv-table}

```
# {"game": "assetto-corsa-rally", "track": "Example Stage"}
time,x,y,z,speed
0.00,12.0,3.1,-40.0,21.0
0.05,12.4,3.1,-38.7,21.3
```

- Kolumny o nazwach `x`, `y`, `z` (bez względu na wielkość liter i otaczające spacje) są wymagane. Inne kolumny są ignorowane.
- Wiersze zaczynające się od `#` są pomijane. Jeśli **pierwszy** wiersz to `# {json}`, czytane są z niego `game` i `track`.
- Wiersze, których nie da się odczytać jako liczb, są pomijane.

### 6. Folder {#a-folder}

Folder przeszukuje się **rekurencyjnie** w poszukiwaniu plików `.json`, `.npz` i `.csv`, a wszystkie łączy się w jedną przejechaną linię. Tak przechowuje się cały nagrany tor: FH Companion zagnieżdża foldery klas, samochodów, ustawień i znaczników.

- `course.json` jest pomijany po nazwie (to metadane, nie okrążenie).
- Plik, którego nie da się odczytać, jest po cichu pomijany. Jeden zły plik wśród setek nie kosztuje reszty.
- Konsola podaje, ile plików okrążeń weszło (`12 laps, 18,400 samples`).
- Folder dostaje grę, którą nazywają jego pliki, jeśli nazywają **tylko jedną**. Plik, który nie nazywa żadnej gry (okrążenie FH Companion, `course.json`, CSV bez wiersza opisu), się nie liczy, więc jeden z nich wśród nagrań gry nie odbiera folderowi jego gry. Pliki nazywające dwie różne gry to mieszanka i folder nie dostaje żadnej. Folder bez gry eksportuje się jako Forza, chyba że `--game` mówi inaczej.
- Jeśli nic się nie odczyta: "no readable laps under <folder>".

### 7. Nazwa trasy {#a-course-name}

Jeśli argument nie jest istniejącym plikiem ani folderem, szuka się go jako nazwy trasy w bibliotece FH Companion, `%LOCALAPPDATA%\FHCompanion\laps`:

1. folder, którego nazwa, bez końcówki ` (course_...)`, jest równa tej nazwie (bez względu na wielkość liter);
2. w przeciwnym razie jedyny folder, którego nazwa tę nazwę zawiera.

Więc `"Example Circuit"` znajdzie `Example Circuit (course_1200_3400_to_1175_3400)` bez znajomości współrzędnych. Kilka dopasowań to błąd, który je wymienia. Trasa znaleziona po nazwie nie niesie gry, więc eksportuje się jako Forza, chyba że `--game` mówi inaczej.

## Co przyjmuje `terrain --route` {#what-terrain---route-accepts}

`terrain` potrzebuje `bounds` z pliku trasy (kształt 2 powyżej), w postaci `{"min": [x, y, z], "max": [x, y, z]}`. Bez `bounds` zatrzymuje się z komunikatem "<file> has no bounds; --route takes a route file with "bounds": {...}". Plik czyta się jako UTF-8 z znacznikiem kolejności bajtów albo bez, jak każdy JSON okrążenia. Jeśli ten sam plik ma także co najmniej 10 pozycji odczytanych wg reguł wyżej, zawężają one wycinkę do korytarza i kierują szczegółowością.

## Jak używa się okrążenia {#how-the-lap-is-used}

| Zastosowanie | Szczegóły |
|---|---|
| nazwa | nazwa pliku bez rozszerzenia albo nazwa folderu, bez końcówki ` (course_...)`; staje się domyślną nazwą pliku wyjściowego |
| przejechana odległość | suma odstępów między kolejnymi próbkami (wypisywana jako `m driven`; dla folderu wlicza się też skoki między plikami) |
| pudełko | zakres x i z rozszerzony o `--margin`; wysokość nigdy nie jest ograniczana |
| korytarz | x i z każdej próbki, zob. [Eksport trasy](course-export.md#the-corridor) |
| szczegółowość | odległość każdej umieszczonej kopii do najbliższej próbki, zob. [Poziomy szczegółowości i budżet](detail-budget.md) |

Okrążenie z mniej niż dwiema próbkami jest odrzucane ("holds no driving").

## Błędy {#errors}

| Komunikat | Znaczenie |
|---|---|
| `<file> is not a lap this can read. Give it a route or lap file (.json), a recording (.npz), a table with x, y and z columns (.csv), a folder of any of those, or just a course's name.` | plik nie jest JSON (ani `.npz`, ani `.csv`) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | JSON innego kształtu |
| `<file> has no x, y and z columns` | CSV bez tych nagłówków |
| `<file> has no positions array` | `.npz` bez `positions` |
| `'<name>' is not a file, and there is no lap library at <path> to look it up in` | nazwa, ale brak biblioteki FH Companion |
| `'<name>' matches 3 courses: A, B, C` | podaj dokładniej |
| `LOCALAPPDATA is not set, so the lap library cannot be found` | tylko dla wyszukiwania po nazwie i dla `courses` |
