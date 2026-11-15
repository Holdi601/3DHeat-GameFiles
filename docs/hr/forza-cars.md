---
title: "Forza automobili: `cars`"
nav_order: 6
lang: "hr"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Forza automobili: `cars` {#forza-cars-cars}

Zapisuje svaki automobil instalirane igre Forza u najnižoj razini detalja koju igra sama koristi, u jednu datoteku za karticu Analiza utrke u pregledniku (ona nacrta automobil za svaki krug koji ste vozili). Tako je svaki zabilježeni automobil nacrtan vlastitim oblikom u svojoj stvarnoj veličini.

![cars --help](../assets/img/cars-help.svg)

## Korak po korak {#step-by-step}

1. **Pokrenite** uz instaliranu igru (pronalazi se u Steam bibliotekama i u `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ili navedite mapu igre:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Učitajte datoteku u preglednik:** gumb **Učitaj datoteku s automobilima…** u postavkama preglednika ili ispustite datoteku na karticu Analiza utrke. Datoteka ostaje u tom pregledniku. Krugovi čiji je broj automobila u datoteci tada se crtaju kao upravo taj automobil (vidi [dokumentaciju o reprodukciji utrke](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Pokrenite ponovo** kad igra dobije nove automobile. Traje nekoliko sekundi i zapisuje oko 5 MB.

## Opcije {#options}

| Opcija | Zadano | Značenje |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | datoteka koju treba zapisati |
| `--game FOLDER` | pronađena instalirana igra | mapa igre |

## Što je u datoteci {#what-is-in-the-file}

Za svaku arhivu automobila pod `media/Cars`: model `ProxyLOD` koji nosi (oko 900 trokuta), broj automobila kako ga navodi telemetrija, njegov proizvođač, oznaka modela i godina iz imena arhive te njegovi kotači i stražnja svjetla. Oblici su u metrima, 1:1 s automobilom. Arhiva bez takvog modela (prometni rekvizit) imenuje se i izostavlja.

Datoteka je napravljena za preglednik 3DHeat. Njezin raspored, za sve koji je čitaju drugdje ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Dio | Raspored |
|---|---|
| cijela datoteka | komprimirana gzipom |
| magija | 8 bajtova `H3DCARS1` |
| duljina zaglavlja | little-endian u32 |
| zaglavlje | UTF-8 JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| punjenje | razmaci do višekratnika od 4 bajta |
| podaci | po automobilu: vrhovi kao tri i16 svaki (milimetri; x desno, y gore, z naprijed), zatim trokuti kao tri u16 svaki |

Svaki unos u `cars` ima: `key`, `ordinals` (brojevi automobila kako ih navodi telemetrija), `make`, `model`, `year`, `height` i `length` (m), `wheels` (za svaki kotač `[x, y, z, radius]`, m), `lights` (točke stražnjih svjetala `[x, y, z]`, m) te `vertexAt`, `vertices`, `faceAt`, `faces` (pomaci u bajtovima od početka podataka, i brojevi).

Datoteka sadrži sadržaj igre: namijenjena je stroju na kojem je napravljena, a ne za slanje drugima ([Pravila i licence](rules-and-licences.md)).
