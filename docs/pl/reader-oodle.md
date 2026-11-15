---
title: Oodle
nav_order: 3
lang: "pl"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: znaleziony, nie dołączony {#oodle-found-not-bundled}

Większość dostarczanej zawartości Unreal i część ładunków Frostbite są kompresowane algorytmem
**Oodle** (RAD Game Tools, obecnie Epic). Oodle jest własnościowy. Nie ma wersji do dalszego
rozprowadzania ani implementacji w Pythonie, a `oo2core_*.dll` jest licencjonowany produktowi,
który go dostarcza. Dlatego to narzędzie **znajduje kopię, która już jest na twoim komputerze,
i ją wczytuje**. Nigdy jej nie dołącza. FModel i UModel działają tak samo.

Źródło: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Gdzie szuka {#where-it-looks}

Wygrywa pierwszy plik, który istnieje, w tej kolejności:

1. Jawna ścieżka podana przez wywołującego (API w Pythonie).
2. `HEAT3D_OODLE`: ścieżka do DLL albo folderu, który go zawiera.
3. Płytkie wyszukiwanie, na jeden poziom w głąb, w
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` każdej biblioteki Steam

   Dla każdego podfolderu `<game>` sprawdza `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` i `<game>\Engine\Binaries\Win64`.

Próbowane nazwy plików, od najnowszej: `oo2core_9_win64.dll` aż do `oo2core_3_win64.dll`.
Format jest wstecznie zgodny, więc starsza biblioteka zwykle też działa.

Wyszukiwanie celowo **nie** jest rekurencyjnym przeglądem wszystkich dysków, bo trwałoby to
minuty. Jeśli nic nie znajdzie, ustaw `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Folder działa równie dobrze jak sam plik: nazwy DLL podane wyżej są w nim szukane.

Instalacja Unreal Engine ma go w `Engine\Binaries\ThirdParty\Oodle`, co jest najwygodniejszym
źródłem dla dewelopera. Wiele gier ma go obok pliku wykonywalnego. Gry Unreal 5 często linkują
Oodle statycznie i nie mają żadnego DLL, więc znaleziona kopia może należeć do innej gry niż
czytane archiwum. Format jest w obu przypadkach ten sam.

## Jak jest wywoływany {#how-it-is-called}

`OodleLZ_Decompress` jest wywoływany przez `ctypes` z oczekiwaną długością wyjścia (indeks
archiwum zawsze ją zna, a Oodle nie potrafi jej odgadnąć), z włączonym dekodowaniem odpornym
na fuzzing (wejście jest niezaufane), bez sprawdzania CRC (SHA-1 samego pliku pak już obejmuje
bajty) i bez wątków. Zły rozmiar wyniku to błąd. Biblioteka jest ładowana raz na uruchomienie.

## Gdy nic nie ma {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Wpis, którego nie da się rozpakować, jest błędem, nigdy wiarygodnie wyglądającymi śmieciami.

Czytnik działa tylko w Windows (szuka plików `*_win64.dll`). Biblioteki dla Linuksa i macOS
nie są szukane.
