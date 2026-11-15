---
title: Samochody Forza
nav_order: 6
lang: "pl"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Samochody Forza: `cars` {#forza-cars-cars}

Zapisuje każdy samochód zainstalowanej gry Forza w jej własnym, niskim poziomie szczegółowości
do jednego pliku dla karty Analiza wyścigowa w przeglądarce (rysuje samochód dla każdego
okrążenia, które przejechałeś), więc każdy nagrany samochód jest rysowany w swoim własnym kształcie
i w prawdziwym rozmiarze.

![cars --help](../assets/img/cars-help.svg)

## Krok po kroku {#step-by-step}

1. **Uruchom polecenie**, mając grę zainstalowaną (program znajdzie ją w bibliotekach Steam
   i w `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Albo podaj folder gry:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Wczytaj plik w przeglądarce 3DHeat**: **Wczytaj plik z samochodami...** w ustawieniach widoku
   albo upuść plik na karcie wyścigu; zostaje w tej przeglądarce. Okrążenia, których numer
   samochodu jest w pliku, są wtedy rysowane jako ten właśnie samochód (zobacz
   [dokumentację odtwarzania wyścigu](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)
   przeglądarki).

3. **Uruchom ponownie**, gdy gra dostanie nowe samochody. Zajmuje to kilka sekund i zapisuje
   około 5 MB.

## Opcje {#options}

| Opcja | Domyślnie | Znaczenie |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | plik do zapisania |
| `--game FOLDER` | znaleziona zainstalowana gra | folder gry |

## Co jest w pliku {#what-is-in-the-file}

Dla każdego archiwum samochodu w `media/Cars`: model `ProxyLOD`, który zawiera (około 900 trójkątów),
numer samochodu, tak jak podaje telemetria, markę, znacznik modelu i rok z nazwy archiwum oraz
koła i światła tylne. Kształty są w metrach, w skali 1:1 z samochodem. Archiwum bez takiego
modelu (rekwizyt ruchu drogowego) jest nazwane i pominięte.

Plik jest przygotowany dla przeglądarki 3DHeat; jego układ, dla każdego, kto czyta go gdzie indziej
([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Część | Układ |
|---|---|
| cały plik | skompresowany gzipem |
| magia | 8 bajtów `H3DCARS1` |
| długość nagłówka | u32 little-endian |
| nagłówek | JSON w UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| dopełnienie | spacje do wielokrotności 4 bajtów |
| dane | dla każdego samochodu: wierzchołki jako trzy i16 (milimetry; x w prawo, y w górę, z do przodu), potem trójkąty jako trzy u16 |

Każdy wpis `cars` zawiera: `key`, `ordinals` (numery samochodu, tak jak podaje je telemetria),
`make`, `model`, `year`, `height` i `length` (m), `wheels` (dla każdego koła `[x, y, z, radius]`, m),
`lights` (punkty świateł tylnych `[x, y, z]`, m) oraz `vertexAt`, `vertices`, `faceAt`, `faces`
(przesunięcia bajtowe od początku danych i liczby).

Plik zawiera treści gry: jest przeznaczony dla komputera, na którym powstał, a nie do rozsyłania
([Zasady i licencje](rules-and-licences.md)).
