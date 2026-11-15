---
title: "Unreal `.pak`"
nav_order: 1
lang: "pl"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Wypisuje i wyciąga** archiwa Unreal `.pak` w wersjach 4.22-5.x: wersje 8, 9, 10, 11 i 12, kompresję Zlib, Gzip i Oodle oraz zaszyfrowane archiwa, gdy podasz klucz AES. Nie interpretuje tego, co wyciąga (`.uasset`, `.umap`).

Źródło: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Polecenia: `identify`, `list`, `extract` (zob. [Polecenia](commands.md)).

## Układ {#layout}

Stopka jest na końcu pliku i znajduje się przez przeszukanie ostatnich 1024 bajtów w poszukiwaniu magicznej liczby `0x5A6F12E1`. Kolejność pól ma znaczenie:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Flaga szyfrowania stoi **przed** magiczną liczbą. Gdyby brać ją z miejsca za magiczną liczbą, trafiłoby się na literę „Z” z „Zlib”. Wtedy każde archiwum zgłaszałoby się jako zaszyfrowane, a każda nazwa metody traciłaby pierwszą literę („lib", „odle"): ciche i wiarygodne błędy. Wersja to najniższy bajt, bo buildy z „zamrożonym indeksem" ustawiają wysoki bit.

Indeks zawiera punkt montowania, indeks haszy ścieżek, pełny indeks katalogów oraz blok **zakodowanych wpisów**: forma spakowana bitowo, w której słowo flag mówi, które liczby są 32-bitowe, metodę kompresji (6 bitów), czy wpis jest zaszyfrowany, liczbę bloków (16 bitów) i rozmiar bloku w jednostkach po 2048 (6 bitów). Samo jedynki w rozmiarze bloku to ucieczka: prawdziwy rozmiar idzie za nią jako u32 **przed** przesunięciem. W dużym archiwum czytanie go po rozmiarach przesunęło 7% wpisów o cztery bajty i dało im przesunięcia w eksabajtach.

Pełny rekord każdego wpisu jest powtórzony tuż przed jego ładunkiem, więc ładunek zaczyna się po `8+8+8+20+4+1+4` bajtach, plus `4 + 16 x blocks`, gdy jest skompresowany. Zaszyfrowane bloki dopełnia się do 16 bajtów.

## Co czyta, a co odrzuca {#what-it-reads-and-what-it-refuses}

| Przypadek | Wynik |
|---|---|
| wersje 8-12 | czytane |
| każda inna wersja | `pak version N; this reader handles 8-12` (starsze wersje przechowują płaską listę rekordów, a nie było pliku do testów) |
| brak magicznej liczby stopki | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks poza plikiem | odrzucany: stopka nie parsuje się tak, jak twierdzi |
| tylko indeks haszy ścieżek | odrzucany: nazwy plików zostały zahaszowane podczas budowania i nie da się ich odzyskać |
| wpisy na liście przepełnienia indeksu (przesunięcie katalogu -1) | pomijane, a nie udawane |
| zaszyfrowany indeks bez klucza | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." W linii poleceń: jedna linia i kod wyjścia 1 |
| zaszyfrowany wpis bez klucza | `EncryptedPak` przy odczycie |
| metody Zlib, Gzip, Oodle | rozpakowywane (Oodle potrzebuje biblioteki, zob. [Oodle](reader-oodle.md)) |
| każda inna metoda | `compression method '...' is not supported` |

## Klucze {#keys}

`--key` przy `list` i `extract` przyjmuje klucz AES-256, który już masz, jako 64 cyfry szesnastkowe, z `0x` albo bez. Cokolwiek innego jest odrzucane przed otwarciem archiwum, z kodem wyjścia 2. Deszyfrowanie to AES-256-ECB przez pakiet `cryptography`. Nie ma ścieżki kodu, która zdobywa klucz: nie ma wbudowanych kluczy, przeszukiwania plików wykonywalnych ani czytania pamięci. Zobacz [Zasady i licencje](rules-and-licences.md).

## Sprawdzone {#verified}

Na dostarczanych archiwach więcej niż jednej gry każdy wpis, łącznie z jednym bardzo dużym archiwum, pasował do SHA-1, które Unreal zapisuje przed każdym ładunkiem. Ten hasz obejmuje bajty tak, jak są przechowywane, więc zgodność oznacza, że dekodowanie indeksu, przesunięcie ładunku i każda granica bloku skompresowanego były poprawne. Testy na zainstalowanych grach (`test_pak.py`) powtarzają to na do czterech niezaszyfrowanych paków znalezionych w `steamapps\common\*\...\Content\Paks`. Sprawdzają, że przesunięcie każdego wpisu leży w pliku i że SHA-1 się zgadza dla losowej próbki 150 wpisów z każdego archiwum.
