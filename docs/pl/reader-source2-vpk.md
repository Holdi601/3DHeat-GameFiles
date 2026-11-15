---
title: Source 2 `.vpk`
nav_order: 6
lang: "pl"
source: reader-source2-vpk.md
source_hash: "7c2e83952ba6"
nav_exclude: true
search_exclude: true
---
# Source 2 `.vpk` {#source-2-vpk}

**Wypisuje i wyciąga** archiwa VPK firmy Valve, wersje 1 i 2, w tym archiwa podzielone
i dane zapisane wewnątrz pliku katalogu. Każdy wpis można sprawdzić jego własnym CRC. To jedyny
format kontenera tutaj, którego opis publikuje jego producent. Gry: Counter-Strike 2, Dota 2,
Half-Life: Alyx i inne na Source 2.

Źródło: [`vpk.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/vpk.py).
Polecenia: `identify`, `list`, `extract`.

## Układ {#layout}

```
u32 magic 0x55AA1234, u32 version (1 lub 2), u32 tree size
  (wersja 2: 16 dodatkowych bajtów nagłówka; nagłówek 12 lub 28 bajtów)
directory tree:
  extension        "vmdl_c", potem "vtex_c", ..., potem ""
    path           "maps/example_map", potem ""
      file name    "world_layer0", potem ""
        u32 crc, u16 preload size, u16 archive index, u32 offset, u32 length, u16 0xFFFF
        [preload bytes]
```

- Trzy zagnieżdżone pętle, każda kończy się pustym ciągiem, więc czytnik oczekujący liczby
  nie znajdzie jej wcale. Ścieżki są zapisane raz na grupę i składane z wszystkich trzech części.
  Pojedyncza spacja oznacza „brak folderu” albo „brak rozszerzenia”.
- Każdy rekord kończy się `0xFFFF`. To jest sprawdzane, więc czytnik, który zgubił miejsce,
  zatrzymuje się od razu („the directory is not being read at the right offset”).
- **Archiwa podzielone:** `pak01_dir.vpk` zawiera katalog, a dane leżą w
  `pak01_000.vpk`, `pak01_001.vpk`... wybieranych przez indeks archiwum wpisu.
- **Indeks archiwum `0x7FFF`** oznacza, że bajty są w samym pliku katalogu, za drzewem.
  Czytanie go jak prawdziwego indeksu wysyła czytnik po `pak01_32767.vpk`.
- **Preload:** małe pliki są zapisane w całości w katalogu. Długość 0 nie jest wtedy błędem.

## Polecenia {#commands}

```
python -m heat3d_gamefiles identify maps\example_map.vpk
python -m heat3d_gamefiles list maps\example_map.vpk --filter .nav
python -m heat3d_gamefiles extract maps\example_map.vpk maps/example_map.nav
```

`identify` wypisuje wersję, liczbę wpisów i pierwszy plik `.nav`. `list` pokazuje każdy wpis
jako `stored`, bo VPK nie kompresuje. `extract` zapisuje bajty bez sprawdzania CRC. W Pythonie
`VpkArchive(path).verify(name)` porównuje bajty wpisu z CRC zapisanym w katalogu.

## Siatka nawigacyjna {#the-navigation-mesh}

Mapa dostarcza swoją **siatkę nawigacyjną** (`maps/<map>.nav`) obok skompilowanej geometrii.
Dla mapy cieplnej pozycji graczy jest ona zdecydowanie bardziej użyteczna z tych dwóch, bo siatka
nawigacyjna *jest* podłogą, po której można chodzić, już obliczoną i tysiąc razy mniejszą.
Test zainstalowanej gry sprawdza, czy `.nav` dostarczonej mapy zaczyna się od magii nawigacji
Source `CE FA ED FE`.

## Zweryfikowane {#verified}

Każdy wpis próbkowany w dostarczonych archiwach map gry został odtworzony bajt w bajt zgodnie
z CRC, a każde archiwum mapy się parsuje.
Testy zainstalowanej gry powtarzają sprawdzenie CRC na 25 losowych wpisach z każdego z co najwyżej
czterech archiwów map.

## Niezaimplementowane {#not-implemented}

- Dekodowanie skompilowanych zasobów Source 2 (`.vmdl_c`, `.vtex_c`). To porcjowane pliki binarne
  o własnym układzie, to samo zadanie co formaty siatek Unreal i Frostbite. Osobne narzędzie
  3DHeat dla CS2 obsługuje geometrię map CS2.
- Dekodowanie siatki nawigacyjnej CS2. Jej format to wersja 36 i różni się od szeroko opisanego
  formatu Source 1. Jej bajty są ustrukturyzowane, a nie skompresowane (entropia 6,2, 31% zer),
  ale tylko 3% jej słów czyta się jako współrzędne, więc układ nie jest oczywisty i nie został
  jeszcze rozpracowany.
