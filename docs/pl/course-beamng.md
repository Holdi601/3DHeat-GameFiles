---
title: BeamNG.drive
nav_order: 2
lang: "pl"
source: course-beamng.md
source_hash: "20b6c04360dc"
nav_exclude: true
search_exclude: true
---
# Eksport toru: BeamNG.drive {#course-export-beamngdrive}

Eksport BeamNG czyta poziom tak, jak gra go montuje, a potem zapisuje ten sam
rodzaj pliku, co eksport Forzy: grunt w kwadratach 512 m z zapieczoną teksturą,
drogę i luźny grunt jako osobne części, umieszczone modele według kategorii oraz
wodę.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Źródła: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (instalacja, system plików, scena, teren, materiały),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (eksport),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) i
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (kształty).
Szczegółowy opis formatów plików: [Pliki BeamNG](reader-beamng.md).

## Układ okrążenia {#the-laps-frame}

Eksport `course` oczekuje pozycji BeamNG we **układzie przeglądarki 3DHeat**:
`(x, z, -y)` świata BeamNG z osią Z w górę, w metrach. To jest obrót, który
stosuje rejestrator telemetrii 3DHeat. Eksport przelicza okrążenie z powrotem na
układ BeamNG (`(x, -z, y)`), pracuje w nim, a na końcu zapisuje wszystko znowu
w układzie przeglądarki. To jest obrót, a nie odbicie lustrzane, więc nic nie
wychodzi odwrócone. Okrążenie nagrane w surowym układzie BeamNG nie zostałoby
umieszczone poprawnie. Nie testowano tego z innymi rejestratorami.

Grę uznaje się za BeamNG, gdy plik `heat3d-lap` ma `"game": "beamng"`, albo gdy
podasz `--game beamng`.

## Znajdowanie instalacji {#finding-the-install}

- `--install <folder>`: folder zawierający `gameengine.zip` i `content`.
- Inaczej sprawdzany jest `steamapps\common\BeamNG.drive` w każdej bibliotece Steam, czy ma te dwie rzeczy.
- Jeśli żadna z tych metod nie działa: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## System plików {#the-file-system}

BeamNG dostarcza zwykłe archiwa zip i montuje je w jeden system plików, do którego
odwołują się poziomy (`/art/shapes/...`, `/assets/materials/...`). Eksport buduje
to samo: jeden indeks bez rozróżniania wielkości liter, zbudowany z

1. `gameengine.zip`,
2. każdego `*.zip` w `content`, z wyjątkiem `content\vehicles\*` i archiwów, których nazwy zaczynają się od `art_sound` albo `audio`,
3. zawartości użytkownika, w kolejności od najnowszej warstwy: w `%LOCALAPPDATA%\BeamNG\BeamNG.drive` i `%LOCALAPPDATA%\BeamNG.drive`, folder `current` i folder wersji o najwyższym numerze. Z każdego z nich: `mods\*.zip`, każdy folder w `mods\unpacked` oraz sam folder użytkownika, jeśli ma folder `levels`.

Późniejsze dodatki wygrywają, jak w grze, więc mod zastępuje to, co nadpisuje.
Mody są zawsze uwzględniane w eksporcie toru.

Ścieżki, które poziom podaje, są rozwiązywane tak, jak robi to gra: najpierw tak,
jak są podane, potem względem pliku, który je podał, a dla każdej także jako
plik `.dds`, do którego zapieczono teksturę, `.cdae`, do którego skompilowano
`.dae`, albo przez plik `.link` wskazujący na `/assets`.

## Który poziom {#which-level}

Bez `--level` każdy poziom dostaje ocenę według tego, ile okrążenia na nim leży:

- Używanych jest do 500 próbek okrążenia, rozłożonych równomiernie.
- Dla każdego `TerrainBlock` poziomu zasięg terenu odczytuje się z pierwszych pięciu bajtów jego pliku `.ter`, więc poziom, w pobliżu którego okrążenia nie ma, nic nie kosztuje. Jeśli co najmniej 30% próbek leży w zasięgu, czyta się wysokości. Próbka liczy się jako **na** terenie, gdy jest między 1 m poniżej a 3 m powyżej niego (`ON_GROUND`), bo punkt odniesienia samochodu to jego nadwozie, a nie opony.
- Jeśli żaden poziom nie dostaje 50% lub więcej, poziomy ocenia się też po ich **drogach**. Niektóre poziomy biegną dalej niż ich mapa wysokości (ich krawędzie ciągną się jako skalne płaty). Próbka leży na drodze, gdy jest w odległości półszerokości drogi plus 4 m (co najmniej 6 m) od segmentu `DecalRoad`, i między 2 m poniżej a 4 m powyżej niej.
- Najlepszy poziom wygrywa, jeśli dostaje co najmniej 30%. Inaczej eksport się zatrzymuje i wypisuje trzy najlepsze: "the lap does not lie on any installed level's terrain
  (best: ...). Name the level with --level."

Konsola pisze `on <level>: 87% of the lap lies on its terrain` (albo `roads`).
`--level` jest dopasowywane bez rozróżniania wielkości liter do nazw folderów poziomów.

## Odczyt poziomu {#reading-the-level}

Z czego składa się poziom, każda część sprawdzona na poziomach dostarczonych z grą
(szczegóły w [Pliki BeamNG](reader-beamng.md)):

- **Scena**: `levels\<name>\main\**\*.level.json` (jeden obiekt JSON w wierszu albo tablica JSON) albo plik `.mis` dla starszych poziomów. Narzędzie czyta obiekty `TSStatic` (umieszczone modele, pomijając ukryte), obiekty `Prefab` (zagnieżdżone do 8 poziomów, pliki TorqueScript `.prefab` albo `.prefab.json`), obiekty `DecalRoad` (malowane drogi), `TerrainBlock`, `WaterPlane`, `WaterBlock` i `River`.
- **Elementy lasu**: `levels\<name>\forest\*.forest4.json`, z typami z rekordów `managedItemData.json`. Bariery, ogrodzenia i skały są elementami lasu tak samo często jak drzewa.
- **Teren**: mapa wysokości `.ter` i jej mapa warstw.
- **Materiały**: każdy `*.materials.json` poza `levels\`, plus te tego poziomu.

## Korytarz i dekale drogowe {#the-corridor-and-the-road-decals}

Korytarz to `--margin` metrów wokół okrążenia w płaszczyźnie x/y BeamNG (zobacz
[Eksport toru](course-export.md#the-corridor)). Korytarz zasięgu o szerokości
`margin + 60 m` wybiera kandydatów.

**Dekale drogowe** (`DecalRoad`) to większość dróg BeamNG: malowane na terenie, a
nie modelowane. Dekale, których zasięg dotyka korytarza zasięgu, są brane w
kolejności rysowania gry (malejąco `renderPriority`, potem kolejność w pliku) i
układane jako wstęgi:

- Węzły (x, y, z, szerokość) są interpolowane splajnem **centripetal Catmull-Rom** co około 1 m. Wersja jednostajna zapętla się na sobie tam, gdzie węzły zbijają się w ostrym zakręcie. Zamknięte drogi się zamykają.
- Każda krawędź bierze wysokość terenu tam, gdzie teren jest w odległości 1,5 m od własnej wysokości drogi, a w pozostałych miejscach zachowuje wysokość drogi (na moście).
- Nazwa materiału decyduje, co dekal maluje (pierwsze dopasowanie wygrywa):

| Rodzaj | Nazwa materiału zawiera (pierwsze dopasowanie wygrywa) |
|---|---|
| ślady opon | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| nakładka (kosmetyczna) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| oznaczenia | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| luźne | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| droga | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| nakładka | wszystko inne |

## Grunt {#the-ground}

Mapa wysokości terenu wewnątrz korytarza zamienia się w trójkąty:

- Jeden czworokąt na kwadrat terenu, którego środek leży w korytarzu. Kwadraty z warstwą 255 (dziury) są pomijane. Każdy czworokąt to dwa trójkąty, z przekątną zmieniającą kierunek tak, jak robi to teren Torque.
- Wysokości to `position.z + h * maxHeight / 65535`. Normalne wynikają z różnic wysokości.
- Każdy kwadrat jest klasyfikowany według swojej **warstwy**: nazwy warstwy z modelem gruntu i adnotacją materiału terenu. Słowa o utwardzeniu dają `road`, słowa `grass/forest/rock/moss/leaves/cliff/stone` dają `terrain`, a luźne słowa dają `loose` (żwir i ziemia). Cała reszta to `terrain`.
- Potem **dekale drogowe i luźne nadpisują** kwadraty, które pokrywają, w kolejności rysowania, więc decyduje ostatni namalowany dekal.
- Wierzchołki są dzielone na kwadraty 512 m (`floor(x / 512)`, `floor(y / 512)`), więc każda część mapuje się dokładnie na jeden obraz: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konsola wypisuje `what the ground is made of` z liczbami trójkątów na rodzaj.

### Modelowana powierzchnia jezdna {#modelled-driving-surface}

Tory wyścigowe BeamNG są równie często modelami, co terenem. Tor wyścigowy może być
jedną siatką z liniami, gumą i pasami wibracyjnymi jako osobnymi siatkami na wierzchu.
Dlatego umieszczone modele w kategoriach drogi, krawężniki, pobocza, rekwizyty i mosty
są przeszukiwane pod kątem powierzchni jezdnej. Dla każdego materiału:

| Powierzchnia | Ustalana przez (pierwsze dopasowanie) |
|---|---|
| ślady opon | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` w nazwie, typie gruntu albo adnotacji |
| oznaczenia | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` w nazwie materiału |
| krawężniki | `rumble`, `kerb`, `curb` |
| droga | typ gruntu `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, albo nazwa zawiera `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| luźne | typ gruntu `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| pobocze | `sidewalk` |
| (własna kategoria modelu) | dla modeli już zaliczonych do drogi, krawężników albo pobocza |

Z tych materiałów **skierowane w górę** trójkąty (normalna z większa niż 0,5)
wewnątrz korytarza są wyjmowane z modelu i stają się gruntem. Są malowane w
zapieczonej teksturze kafla i zapisywane jako części w rodzaju
`ground:road 3_-2 asphalt_light`. Oznaczenia i ślady opon są tylko malowane. Reszta
trójkątów modelu zostaje przy modelu. Te modele nigdy nie są upraszczane ani pomijane
przez budżet, bo źle narysowany tor to zły tor.

## Zapieczona tekstura gruntu {#the-baked-ground-texture}

Każdy kwadrat 512 m, który ma grunt, dostaje jeden obraz o `--texture-size` pikselach
(2048 = 25 cm na piksel), narysowany tak, jak gra rysuje swój grunt:

1. **Warstwy terenu.** Dla każdego piksela warstwy czterech sąsiednich kwadratów terenu są mieszane dwuliniowo. Każda warstwa jest pokolorowana tak, jak gra ją koloruje: **mapa bazowa** materiału rozciągnięta na `diffuseSize` metrów (albo na cały teren), potem mapy **detail** i **macro** jako szare nakładki (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutralne). Ich domyślne powtórzenia to co 2 m i co 60 m, z siłami 0,5 i 0,3, chyba że materiał mówi inaczej. Warstwa bez materiału dostaje płaski kolor swojej powierzchni. Wiersz 0 mapy bazowej to północ.
2. **Dekale drogowe** malowane tylko na terenie, w kolejności rysowania, każdy ze swoją teksturą, mapą krycia, odcieniem i kryciem, wzdłuż wstęgi. Poziomy dostarczane z grą używają priorytetów około 12-16 dla bazy asfaltowej, 10 dla oznaczeń i 4 dla gumy.
3. **Modelowana powierzchnia jezdna** widziana z góry: najpierw bazy, potem nakładki, każda we własnej powtarzającej się teksturze modelu, w jednym texelu na piksel pieczenia.
4. **Dekale, które rzutują też na obiekty** (`overObjects`), na końcu.

Przy `--no-textures` nic nie jest zapiekane: części gruntu dostają płaskie kolory,
a modelowane oznaczenia i ślady opon stają się własnymi częściami, podniesionymi o
**3 cm**.

## Umieszczone modele {#placed-models}

Kandydatami są wszystkie `TSStatic`, dzieci prefabów i elementy lasu, których punkt
początkowy leży w korytarzu zasięgu. Model jest rysowany, jeśli jego świat-pudełko
ograniczające dotyka korytarza.

**Kategoria** pochodzi z adnotacji poziomu i ścieżki kształtu. Pierwsza reguła, która
pasuje, wygrywa:

| Kategoria | Adnotacja | Ścieżka lub nazwa zawiera |
|---|---|---|
| tło (nigdy nie rysowane) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| krawężniki | | `kerb`, `curb`, `rumble` |
| droga | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| pobocze | `SIDEWALK`, `COBBLESTONE` | |
| drzewa (tylko z `--trees`) | `NATURE` | tree, foliage, bush, grass, plant i podobne słowa |
| skały | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| bariery | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| znaki | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| mosty | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktura | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| budynki | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekwizyty | | wszystko inne |

**Kształty** czyta się z gotowego pliku `.cdae`, albo z pliku Collada `.dae` tam, gdzie
nie ma pamięci podręcznej (mody). Kształt, którego nie da się odczytać, jest liczony:
`N copies of M models could not be read`. Materiały nazwane albo z teksturą
`invisible`, `collision` albo `nodraw` nigdy nie są rysowane.

**Tekstury.** Modele są grupowane według kategorii i materiału w części o nazwach
`structure:<category> <material>` (albo `ground:kerbs <material>`). Grupa dostaje
teksturę koloru swojego materiału w rozdzielczości do **256 px** tylko wtedy, gdy jej
UV zostają w zakresie 0-1 (98% wierzchołków w zakresie od -0,02 do 1,02). Narzędzie
pakuje tekstury w atlas i nie potrafi ich powtarzać. Grupa, której tekstura się
powtarza, jest rysowana w średnim kolorze tekstury (ważonym alfą, w sRGB, pomnożonym
przez odcień materiału), a jeśli nie ma tekstury, w kolorze kategorii.

**Szczegółowość** idzie według wspólnego schematu z [Poziomy szczegółowości i budżet](detail-budget.md).
Poziomy szczegółowości BeamNG to `details` kształtu (od największego rozmiaru w pikselach).
Przy przekroczeniu budżetu najpierw idą najdalsze kopie. Krawężniki i modele niosące
powierzchnię jezdną nigdy nie są upraszczane ani pomijane.

`--no-placed` usuwa konstrukcje, ale zachowuje modelowaną powierzchnię jezdną.
`--trees` dodaje kategorię drzew.

## Woda {#water}

| Źródło | Rysowane jako |
|---|---|
| `WaterPlane` (morze) | czworokąt 4 m na wysokości wody dla każdej komórki korytarza, do której nie dociera teren na tej wysokości |
| `WaterBlock` | jeden czworokąt, kwadrat jednostkowy przy lokalnym z = 0 w przekształceniu bloku (więc jego skala ustala rozmiar), jeśli dotyka korytarza; czy z = 0 to powierzchnia bloku, nie zostało sprawdzone |
| `River` | wstęga przez jego węzły, jeśli dotyka korytarza |

Cała woda to jedna płaska część, `water:water`.

## Nie jest rysowane {#not-drawn}

- Pokrycie gruntu (proceduralna trawa).
- Dekoracje na obrzeżach świata (`backdrop` i podobne).
- Powtarzające się tekstury modeli, które wychodzą jako średni kolor (zobacz wyżej).
- Skinned meshes (pojazdy, postacie) i siatki dekali wewnątrz kształtów.

## Sprawdzenia, na których to opiera się {#checks-behind-it}

Jak podano w źródle, zmierzone na poziomach dostarczonych z grą:

- Węzły drogi leżą na terenie z dokładnością 1-2 cm (mediana) na sprawdzonych poziomach, przy `h * maxHeight / 65535` i rzędach wzdłuż +y. `h / 32` albo inna kolejność osi mylą się o dziesiątki do setek metrów.
- Odcinki szyn połączone wzdłuż drogi biegną wzdłuż wiersza 0 `rotationMatrix` (w zdecydowanej większości).
- Rotację węzła `.cdae` trzeba transponować. Wtedy pudełka świata zgadzają się z źródłowym `.dae` co do milimetra. Podejście podręcznikowe myli się o 38 cm (mediana).
- Eksportowane na kilku dostarczanych z grą poziomach każdego rodzaju, w sekundach do minut każdy.
