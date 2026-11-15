---
title: Rozwój
nav_order: 14
lang: "pl"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Rozwój {#development}

## Układ {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mapa modułów {#module-map}

| Moduł | Co robi |
|---|---|
| `__main__.py` | uruchamia sprawdzenie aktualizacji, potem `cli.main()` |
| `cli.py` | polecenia, `identify`, obsługa archiwów, zapis trasy Forzy |
| `lapinput.py` | każdy kształt okrążenia zamienia na pozycje; wyszukiwanie w bibliotece FH Companion |
| `corridor.py` | pas po obu stronach jazdy, jako raster 4 m |
| `surfaces.py` | rodzaje podłoża, nazwy ich części i kolory |
| `glb.py` | zapis `.glb` (części, normalne, kolory, tekstury, kwantyzacja) |
| `courseexport.py` | Forza: płaskie UV kafelków, podział droga/pobocze, zapiekanie podłoża, podnoszenie nakładek |
| `forzainstall.py` | biblioteki Steam i Xbox; tor Forzy, do którego należy pudełko |
| `minizip.py` | archiwa ForzaTech `.minizip` i ich listy nazw |
| `forzatech.py` | `.modelbin`: chunki, bufory, układy, podsiatki, materiały |
| `forzaterrain.py` | kafelki terenu według miejsca; klasy nawierzchni |
| `forzatexture.py` | próbki `.pb`; mapy kafelków; zapiekanie podłoża |
| `forzamaterial.py` | `AssetManifest.xml`; jakie kolory tekstur ma model; pory roku |
| `forzaplacement.py` | rozmieszczenia `.pgeo`, poziomy modeli, tekstury, wycinanki, zastępniki, budżet |
| `beamng.py` | instalacja BeamNG, zamontowany system plików, scena, teren, materiały |
| `beamngcourse.py` | eksport trasy BeamNG |
| `beamngshape.py` | skompilowane kształty `.cdae` |
| `beamngcollada.py` | awaryjny odczyt `.dae` |
| `acrally.py` | instalacja AC Rally, etapy, umieszczenie komponentów, objętość tekstur wirtualnych |
| `acrallycourse.py` | eksport trasy AC Rally: dopasowanie ramki, podłoże, umieszczenie |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | zapieczone pakiety Unreal 5 |
| `unversioned.py` | schematy i odczyt właściwości unversioned |
| `unrealmesh.py` | zapieczone siatki statyczne |
| `unrealtexture.py` | tekstury i strumieniowane tekstury wirtualne |
| `oodle.py` | znajdowanie i wywoływanie zainstalowanej biblioteki Oodle |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | kontenery, pakiety i siatki Unity |
| `frostbite.py` | Frostbite `.toc`, tabele sekcji, pakiety instalacyjne, położenia fragmentów, ładunki |
| `frostbitebundle.py` | pakiety wbudowane Frostbite, manifesty pakietów, katalog poziomu, lista poziomów |
| `frostbiteebx.py` | partycje RIFF EBX Frostbite bez biblioteki typów |
| `frostbitemesh.py` | MeshSet Frostbite i jego fragmenty poziomów szczegółowości |
| `frostbiteterrain.py` | drzewo strumieniowania terenu Frostbite, strony wysokości, siatka podłoża |
| `frostbitematerial.py` | tekstury Frostbite (mipy BC1/BC3/BC7), magazyny bloków shaderów, wybór mapy kolorów |
| `frostbitedecals.py` | nakładki terenu Frostbite i zapiekanie podłoża |
| `frostbitenav.py` | kafelki siatki nawigacyjnej Frostbite: powierzchnie, po których chodzą żołnierze |
| `frostbitelevel.py` | grupy statycznych modeli Frostbite, umieszczenie, eksport `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | komponenty landscape Unreal 5: mapy wysokości w siatce podłoża (`ue-map`) |
| `unreallevel.py` | mapy Unreal 5 World Partition: lista, struktury HLOD, woda, eksport `ue-map` |
| `enfusion.py` | `.pak` Enfusion, `.edds`, kafelki terenu, `resourceDatabase.rdb` |
| `enfusionworld.py` | światy Arma Reforger: pliki `.ent`, pudełka, eksport `enfusion-world` |
| `forzacars.py` | każdy samochód Forzy w niskim szczegółowości do `.h3dcars` (`cars`) |

Wszystkie moduły są na GitHubie w katalogu [`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Uruchamianie testów {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` ustawia `testpaths = tests` i `-q`. Ważne są dwa rodzaje testów, z różnych powodów:

- **Testy syntetyczne** budują archiwa bajt po bajcie i działają wszędzie. Przypinają układy pól, które kiedyś były błędne: 64-bitową bazę segmentu `.minizip` i jej wypełnienie do wyrównania, ucieczkę rozmiaru bloku w pak, u32 między dwoma int64 w nagłówku Unity, indeks `0x7FFF` w VPK, podzieloną składową x normalnej w Forzie.
- **Testy na zainstalowanych grach** działają na prawdziwych plikach, gdy gra jest na komputerze, i **pomijają się** (nie zawodzą), gdy jej nie ma. Tylko one łapią układ, który jest poprawny dla małego pliku, a błędny dla dużego.

### Fixtures {#fixtures}

| Fixture | Buduje |
|---|---|
| `tests/forza_fixtures.py` | archiwa `.minizip` (z 64-bitową bazą, wypełnieniem, mieszanymi kodekami), manifesty, modele `.modelbin` i teren, próbki `.pb` |
| `tests/beamng_fixtures.py` | mała instalacja BeamNG: `gameengine.zip`, `content`, jedno archiwum poziomu z terenem 64 m, pas asfaltu, nakładkę drogową, barierę, prefab, element lasu, morze, materiały i kształty `.cdae` w udokumentowanym układzie |
| `tests/unreal_fixtures.py` | kontener IoStore z katalogiem, pakiet zen, blok właściwości unversioned |
| `tests/frostbite_fixtures.py` | tabele, pakiety, partycje EBX, siatki i strony terenu Frostbite, bajt po bajcie |

### Pliki testów {#test-files}

| Plik | Pokrywa |
|---|---|
| `test_minizip.py` | odczyt, 64-bitowa baza, parzyste i nieparzyste tabele pakietów, odmowy, plik nazw |
| `test_forzatech.py` | tabela chunków i łańcuch, odmowy; na zainstalowanej grze: łańcuchy i tagi prawdziwych modeli |
| `test_forza_geometry.py` | umieszczenie w świecie, układ wierzchołków, odrzucane formaty, podsiatki, normalne i UV |
| `test_forzaterrain.py` | siatka kafelków (1023 vs 512 m), przycinanie, wyciąganie |
| `test_forzatexture.py` | nagłówek próbki, dekodowanie, półka tekstur, zapiekanie podłoża |
| `test_forzamaterial.py` | manifest, nazwy, skróty materiałów, wybór koloru, pory roku |
| `test_forzaplacement.py` | rekord `.pgeo`, umieszczanie kopii, poziomy, warianty, powierzchnie przeźroczyste, całe pudełko, budżet, kolor zastępczy, automatyczny budżet; na zainstalowanej grze: krawężniki na podłożu |
| `test_forzainstall.py` | znajdowanie gry, wybór toru |
| `test_courseexport.py` | UV kafelków, plan części, podnoszenie nakładek |
| `test_course_cli.py` | całe polecenia `course` i `courses` na syntetycznym torze; `terrain --route` z znacznikiem kolejności bajtów i bez `bounds` |
| `test_archive_cli.py` | `identify`, `list` i `extract` na każdym archiwum, które ma czytnik (`.pak`, IoStore, `.vpk`, `.minizip` z nazwami i bez, zip, `.cdae`, `.ter`); błędy jako jedna linia i kod wyjścia: zaszyfrowany pak, zaszyfrowany kontener, plik, który nie jest archiwum, zły `--key` |
| `test_corridor.py` | pas, wycinanie terenu przez niego |
| `test_lapinput.py` | każdy kształt okrążenia, pudełko, błędy, wyszukiwanie nazwy trasy, rozpoznawanie gry w folderze |
| `test_surfaces.py` | które nazwy decydują o nawierzchni, a które nie, nazwy części |
| `test_glb.py` | plik jest poprawny, węzły mają klasę, odmowy, kwantyzacja |
| `test_beamng.py` | kształty, poziom, kategorie, znajdowanie poziomu na podstawie okrążenia, trasa, awaryjny odczyt Collada; na zainstalowanej grze: `.cdae` vs `.dae`, każdy poziom się otwiera |
| `test_acrally.py` | kontenery, pakiety, właściwości, transformacje, dopasowanie ramki, części i budżet umieszczonych modeli, tekstury wirtualne; na zainstalowanej grze: etapy i zapieczony kolor podłoża |
| `test_pak.py` | stopka, wpisy, ucieczka rozmiaru bloku, odmowy; na zainstalowanej grze: przesunięcia i SHA-1 |
| `test_unity.py` | odmowy; na zainstalowanej grze: tabela obiektów wypełnia plik, wersje, granice siatek |
| `test_frostbite.py` | nagłówki z podpisem vs zaciemnione, odmowy, pakiety instalacyjne (dwa pakiety z tym samym numerem bloba); na zainstalowanej grze: każda tabela, superbundle, łańcuchy sekcji, różne identyfikatory, próbkowane ładunki z właściwego pakietu |
| `test_frostbitelevel.py` | identyfikatory chunków sparowane z własnymi położeniami, pakiety wbudowane, manifesty, MeshSet z sekcją cienia i UV, członek grupy, konwencja transformacji, teren z dwoma poziomami, wybór mapy kolorów, chunk tekstury bez największych mipów, powtarzający się próbnik, rekordy nakładek, nakładka złożona przez swoją alfę, arkusz nakładki przegrywający z własną mapą powierzchni, farba nakładki czytana z materiału, linie pasa startowego i ślady opon, pojedynczokanałowe mapy, niszczalne siatki oznaczone w częściach i extrasach, siatki blockout, cinematic i oświetlenia pominięte, a układ mapy kolorów, którego nie czyta się, mapy wycinanek i ich maskowane, dwustronne materiały PNG, kafelki tła nazwane przez siatkę; na zainstalowanej grze: nakładki terenu poziomu, katalog największego poziomu, siatki w granicach pudełek, członkowie grup, roślinność stojąca na odkodowanym terenie |
| `test_vpk.py` | katalog, odmowy, archiwa podzielone; na zainstalowanej grze: mapy się otwierają, CRC się zgadzają, siatka nawigacyjna |
| `test_enfusion.py` | `.pak` Enfusion, `.edds`, kafelki terenu i pliki świata; eksport `enfusion-world` |
| `test_forzacars.py` | plik `.h3dcars`, który zapisuje polecenie `cars` |
| `test_unreallevel.py` | landscape Unreal 5, struktury HLOD, woda; eksport `ue-map` |

## Testy na zainstalowanych grach {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py) znajduje gry dla testów. `steam_common()` wypisuje `steamapps\common` każdej biblioteki Steam (także foldery samego Steama), a `installed(*globs)` zwraca ścieżki pasujące do dowolnego wzorca w tych folderach, rekurencyjnie tam, gdzie wzorzec ma `**`. Każdy test sam decyduje, czego potrzebuje:

| Test | Szuka | Pomija się z komunikatem |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` z **niezaszyfrowanym** indeksem, do 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` w `*/*_Data` albo `*/*/*_Data`, które czytnik przyjmuje, do 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, do 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | okręgi z biblioteki nagranych okrążeń FH Companion (start i meta w odległości 50 m), z największą liczbą okrążeń, które `find_track` umieszcza; albo `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Uruchom testy tylko jednej gry albo wskaż test kształtu krawężnika Forzy na konkretnym torze:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testy na zainstalowanych grach tylko czytają z gier. Nic nie zapisują w folderach gier. Wyniki testów trafiają do tymczasowych folderów pytesta.

## Konwencje {#conventions}

- **Odmawiaj zamiast zgadywać.** Każdy czytnik zgłasza własny wyjątek (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) z komunikatem, co znaleziono i dlaczego nie odczytano.
- **Sprawdzaj o sam format.** Skrót, CRC, łańcuch przesunięć, zapisana ramka ograniczająca, leżenie jazdy na podłożu. Nie „nie wywaliło się”.
- **Bez kluczy i bez zastrzeżonego kodu w zestawie.** Zobacz [Zasady i licencje](rules-and-licences.md).
- **Poufne dane zostają poza repozytorium.** Pliki gier, eksporty, okrążenia, nagrania i zrzuty ekranu nigdy nie trafiają do repozytorium. `.gitignore` wyklucza je po folderze i po typie. Testy używają danych syntetycznych i zainstalowanych gier, nigdy nie wgranych treści gier.
