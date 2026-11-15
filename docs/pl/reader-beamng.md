---
title: "Pliki BeamNG: poziomy archiwów, `.ter`, `.cdae`, `.dae`"
nav_order: 8
lang: "pl"
source: reader-beamng.md
source_hash: "6f7a0239e385"
nav_exclude: true
search_exclude: true
---
# Pliki BeamNG: poziomy archiwów, `.ter`, `.cdae`, `.dae` {#beamng-files-level-archives-ter-cdae-dae}

BeamNG.drive dostarcza zwykłe archiwa zip, więc nie ma kontenera do inżynierii wstecznej. Praca polega na czytaniu poziomu **tak, jak robi to gra**: zamontowaniu archiwów w jeden system plików, podążaniu za plikami scen i dekodowaniu terenu oraz skompilowanych kształtów. Do tych czytników dochodzi się przez eksport trasy [BeamNG.drive](course-beamng.md). `identify` rozpoznaje także zip poziomu, `.cdae` i `.ter`, a `list` i `extract` biorą dowolny z zipów.

Źródła: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Zamontowany system plików {#the-mounted-file-system}

`Files.of_install(game)` buduje jeden indeks niezależny od wielkości liter nad `gameengine.zip`, archiwami `content` (poza pojazdami i dźwiękami) oraz modami użytkownika (`mods\*.zip`, `mods\unpacked\*` i folder `levels` użytkownika). Późniejsze dodatki nadpisują wcześniejsze, jak w grze. Wyszukiwania ignorują wielkość liter, bo odwołania w poziomach nie zgadzają się z nazwami w archiwach (`.DAE` dla `.dae`). Szczegóły są na [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` znajduje ścieżkę tak, jak robi to gra: jako podaną, względem pliku, który ją wymienił, `x.png` jako `x.dds`, `x.dae` jako `x.cdae` (ten pierwszy ma pierwszeństwo) oraz przez plik JSON `x.png.link`, którego `path` wskazuje na `/assets`.

## Pliki scen {#scene-files}

| Źródło | Format | Co czytane |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | jeden obiekt JSON na linię, albo jedna tablica JSON lub mapa | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | te same klasy, dla starszych poziomów bez `main\` |
| `*.prefab` / `*.prefab.json` | TorqueScript albo JSON | dzieci umieszczone względem prefabu, do 8 poziomów w głąb |
| `levels\<name>\forest\*.forest4.json` | jedna instancja na linię | typowane przez rekordy `TSForestItemData` w `managedItemData.json` (`shapeFile`) |
| `info.json` | JSON | tytuł poziomu (klucze tłumaczeń są pomijane) |

**Transformacje.** `rotationMatrix` to dziewięć liczb, których **wiersze** są osiami obiektu w świecie. Odcinki bariery łańcuchowane wzdłuż drogi biegną wzdłuż wiersza 0 (92%), a wiersz „w górę” przechyla się razem z nachyleniem drogi. Starsze prefaby podają `rotation = "x y z degrees"`, czyli obrót prawoskrętny o ten kąt (92% łańcuchów barier zgadza się z tym, 19% z przeciwnym kierunkiem). Skala mnoży wiersze, a `position` (albo `pos`) to ostatni wiersz. Transformacja dziecka prefabu składa się z transformacji prefabu. `groupPosition` prefabu to pivot edytora i **nie** jest odejmowany: wózek z prefabu stoi na ziemi tylko bez tego odejmowania.

Liczby w TorqueScript czyta się tolerancyjnym wzorcem, bo niektóre dostarczane prefaby zapisują wartości takie jak `-0.99563-0.0` bez spacji.

## Teren: `.ter` {#terrain-ter}

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Wysokość w metrach: `position.z + h * maxHeight / 65535`, z `position`, `squareSize` i `maxHeight` z `TerrainBlock` (domyślnie 0, 1 i 2048).
- Wiersze biegną wzdłuż +y. Punkt siatki (i, j) leży w `(position.x + i * squareSize, position.y + j * squareSize)`.
- Warstwa 255 to dziura.

Sprawdzono: węzły drogi leżą na terenie z dokładnością 1-2 cm (mediana) na trzech poziomach. `h / 32` albo inna kolejność osi chybia o dziesiątki do setek metrów.

## Materiały {#materials}

Każdy `*.materials.json` poza `levels\`, plus ten z bieżącego poziomu, indeksowany po `mapTo`, `name` i kluczu:

| Klasa | Używane pola |
|---|---|
| `Material`, `CustomMaterial` | mapa koloru (`baseColorMap`, `colorMap` albo `diffuseMap`, pierwszy stopień), współczynnik koloru, mapa i współczynnik krycia, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | mapa bazowa i `diffuseSize`, mapa detali, rozmiar i siła, mapa makro, rozmiar i siła, `groundmodelName`, `annotation` |

Obrazy dekoduje się przez Pillow (DDS, PNG i inne), używając zmniejszonego draftu tam, gdzie to możliwe, i cache'uje się je według rozmiaru. Tekstura, której nie da się odczytać, wraca do jednolitego koloru.

## Skompilowane kształty: `.cdae` {#compiled-shapes-cdae}

`.cdae` to własna pamięć podręczna gry dla każdego pliku Collada, zapisana jako MessagePack. Jej układ **opisuje BeamNG** (documentation.beamng.com/modding/file_formats/cdae/), a czytnik się go trzyma:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Czyta się: granice, węzły, obiekty, `details` (poziomy szczegółowości), domyślne obroty węzłów (`Quat16`) i translacje, każdą siatkę (wierzchołki, UV, normalne, kolory, prymitywy i indeksy) oraz nazwy materiałów. Nazwy materiałów są na końcu strumienia, bo sekwencje animowanego rekwizytu idą przed nimi w postaci, która nie jest udokumentowana.

Dwie rzeczy, których dokumentacja nie opisuje wprost, ustalono na podstawie plików `.dae`, z których zbudowano kształty:

- **Obroty węzłów są Torque'owe.** `Quat16` czytany podręcznikowo obraca się w złą stronę. Jego macierz trzeba **transponować**. Z tym każde granice świata węzła zgadzają się z Collada co do milimetra. Bez tego są w medianie 38 cm poza.
- **Jednostki i osie są już zastosowane.** Plik Collada zapisany w centymetrach albo z osią Y w górę trafia z pamięci podręcznej w metrach, z osią Z w górę.

Poziomy szczegółowości to `details` o nieujemnym rozmiarze, od największego. Ujemne rozmiary to siatki kolizji i linii widzenia, nigdy nierysowane. Obiekty o nazwach `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` albo `imposter` nigdy nie są rysowane. Rysuje się tylko siatki standardowe i sortowane. Siatki szkieletowe (postacie, pojazdy) i siatki nakładek nie są rysowane. Paski i wachlarze trójkątów są rozwijane, a ściany są nawijane ponownie tak, by zgadzały się z zapisanymi normalnymi, bo własne nawijanie Torque tego nie gwarantuje.

Sprawdzono: prawie każdy dostarczany kształt się czyta. Pozostałe dwa to starsza wersja.

## Awaryjny odczyt Collada: `.dae` {#collada-fallback-dae}

Dla kształtów bez `.cdae` (mody i nieliczne kształty ze starszą pamięcią podręczną) plik Collada czyta się tak, jak importer Torque, do tej samej struktury:

- Poziomy szczegółowości wg nazewnictwa Torque: końcowa liczba w nazwie węzła siatki to rozmiar w pikselach, z którego jest rysowana (`barrier75`, `barrier40`). Ujemna liczba albo nazwa `collision`/`Colmesh`/`LOS`/`nulldetail` nigdy nie jest rysowana. Kształt bez tej konwencji ma jeden poziom.
- Jednostki z `<unit meter>`, a oś Y w górę zamieniana na Z w górę.
- UV odwrócone do konwencji pamięci podręcznej (v biegnie w dół obrazu).

Sprawdzono z `.cdae` gry dla tych samych plików: prawie wszystkie próbkowane granice w granicach 1 cm, 583 z tą samą liczbą trójkątów, 94% UV materiałów identycznych. Test na zainstalowanej grze wymaga, by 90% z do 60 par kształtów z wspólnego archiwum sztuki zgadzało się w granicach 1 cm.

## Nieczytane {#not-read}

- Podłoże roślinne (proceduralna trawa) i wszystko generowane w czasie działania gry.
- Animowane sekwencje i skinning.
- Pojazdy i dźwięki (nigdy nie są montowane).
