---
title: Zasady i licencje
nav_order: 12
lang: "pl"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Zasady i licencje {#rules-and-licences}

Trzy zasady kształtują całe narzędzie. Pełny tekst: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Bez kluczy: żadnych w zestawie, żadnych odzyskiwanych {#no-keys-none-shipped-none-recovered}

**Narzędzie czyta kontenery.** Parsowanie formatu archiwum to zwykła obsługa plików, a FModel, UModel i AssetRipper robią to od lat na otwartą rękę.

**Linia, która ma znaczenie, to szyfrowanie, i jest wyznaczona wewnątrz narzędzia.**

- **Żadnych wbudowanych kluczy.** Nie ma klucza w kodzie ani w danych.
- **Żadnego odzyskiwania kluczy.** Nic nie przeszukuje pliku wykonywalnego w poszukiwaniu klucza i nic nie czyta pamięci innego procesu.
- **Klucz, który masz, albo nic.** Zaszyfrowany pak Unreal otwiera się tylko przez `--key <hex>` (w Pythonie `PakArchive(path, aes_key=...)`). `pak.py` nie ma ścieżki kodu, która zdobywa klucz. Zaszyfrowany kontener IoStore jest odrzucany bez wyjątku.
- **Obfuskacja też nie jest zaimplementowana.** Zaciemnione XOR tabele Frostbite trzymają swój klucz w samym pliku, więc są obfuskacją, a nie mechanizmem kontroli dostępu. Mimo to są wykrywane i odrzucane, bo żaden posiadany plik nie używa tej formy i nie byłoby z czym porównać implementacji. Zaszyfrowany pakiet Assetto Corsa EVO jest odrzucany z tego samego powodu, dla którego obowiązuje zasada kluczy.
- **Zaszyfrowane pliki pozostają zamknięte.** Initial file system Battlefield 6, który trzyma bibliotekę typów gry, jest zaszyfrowany i nie jest czytany. Eksport poziomu działa z plików niezaszyfrowanych i odtwarza z danych dwa typy, których potrzebuje.
- **Nic nie wstrzykuje się do procesu gry.** Telemetria pochodzi z kanałów, które same gry publikują, a przechwytywanie używa publicznych API nagrywania ekranu (w innych narzędziach 3DHeat). Wstrzyknięcie do tytułu z systemem anty-cheat grozi kontu tego, kto je uruchamia.

Każde dotąd testowane archiwum było niezaszyfrowane.

## 2. Twoje pliki {#your-own-files}

Narzędzie czyta pliki gry **zainstalowane na twoim komputerze**. Nigdy nie pobiera zawartości gry.

Nic z gry nie jest dołączane: żadne zasoby gry, żaden kod gry, żadne biblioteki DLL. To, co narzędzie eksportuje, trafia na twój dysk i nigdzie indziej.

3DHeat GameFiles nie jest powiązany z żadnym wydawcą gier ani przez niego popierany. Gry oraz związane z nimi nazwy i znaki towarowe należą do ich właścicieli. Właściciele praw: otwórzcie zgłoszenie na [github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) - odpowiadamy szybko i usuwamy wszystko na żądanie.

## 3. Wynik nie jest do rozpowszechniania {#output-is-not-for-redistribution}

To, co wychodzi, to geometria do **kontekstu przestrzennego**: podłoże, droga i to, co stoi obok, zredukowane do budżetu, żeby okrążenia dało się analizować na miejscu. To najmniej z tego, co zawiera archiwum, a mimo to jest to treść wydawcy gry.

- Zachowuj wyeksportowane pliki `.glb` i zawarte w nich tekstury do własnej analizy.
- Nie publikuj, nie udostępniaj ani nie sprzedawaj wyeksportowanych tras, poziomów, modeli ani tekstur.
- `.gitignore` repozytorium trzyma pliki gier, eksporty, okrążenia i nagrania poza kontrolą wersji, po folderze i po typie pliku (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` i inne).

## Oodle jest znajdowane, nie dołączane {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, obecnie Epic) jest zastrzeżone i nie ma wersji do redystrybucji. `oo2core_*.dll` jest licencjonowane produktowi, który je dostarcza. `oodle.py` więc ładuje bibliotekę już obecną na komputerze, zamiast ją dołączać. To rozwiązanie, które przewiduje licencja, i to samo, którego używają FModel i UModel. Zobacz [Oodle](reader-oodle.md).

## Same formaty {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` Unity, `.toc` Frostbite i formaty ForzaTech są nieudokumentowane. Żaden z tutejszych czytników nie pochodzi z cudzego kodu źródłowego. W przypadku Frostbite publiczne opisy starszych wersji (narzędzia modderskie Frosty, notatka o formacie Need for Speed Heat, prelekcja GDC) dostarczyły nazwy pól i mapę tego, czego szukać. Nie wzięto żadnego kodu, a każdy offset zmierzono na plikach (zob. [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Wyciągnięte poziomy są do twojego własnego użytku. Narzędzie zapisuje je na twoim dysku i nigdzie indziej; nie publikuj ich.
- BeamNG publikuje układ `.cdae`, a czytnik się go trzyma.
- Valve dokumentuje VPK.
- Zapisane dane właściwości Unreal 5 wymagają listy właściwości każdej klasy. Listy w `unversioned.py` to **tylko nazwy i typy**, czyli fakty o formacie, takie jak zawiera plik mapowań interoperacyjnych. Wyprowadzono je z nagłówków Unreal Engine, które Epic udostępnia każdemu z połączonym kontem, i sprawdzono względem dostarczanych danych. Nie ma ani nie jest wymagany kod silnika.

## Licencja tego narzędzia {#this-tools-licence}

Wszystko, co napisano dla tego repozytorium, jest na **licencji MIT** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): można go używać, zmieniać, dostarczać, komercyjnie albo nie.

Pakiety zewnętrzne, wszystkie permisywne, więc eksporter sam nie ma żadnego ograniczenia:

| Pakiet | Licencja | Do czego |
|---|---|---|
| numpy | BSD-3-Clause | dekodowanie siatek |
| cryptography | Apache-2.0 / BSD-3-Clause | tylko archiwa, do których masz klucz |
| lz4 | BSD-3-Clause | archiwa Forzy, niektóre pakiety Unity, bloki LZ4 IoStore |
| Pillow | MIT-CMU (HPND) | tekstury block-compressed, wyjście JPEG |
| msgpack | Apache-2.0 | `.cdae` BeamNG |
| zstandard | BSD-3-Clause | nieliczne `.cdae` kompresowane zstd, bloki zstd Frostbite |
| pytest | MIT | tylko na potrzeby rozwoju |

Licencje odczytano z metadanych pakietów we wrześniu 2026. Jeśli warunki któregoś składnika zmieniły się później, liczy się źródło.
