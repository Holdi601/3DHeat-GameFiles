---
title: "Forza automobili"
nav_order: 6
lang: "bs"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Forza automobili: `cars` {#forza-cars-cars}

Upisuje svaki automobil instalirane Forze, u njenom vlastitom niskom nivou detalja, u jednu
datoteku za karticu Analiza utrke u pregledniku (ona crta automobil za svaki krug koji ste vozili), tako da je svaki snimljeni automobil nacrtan svojim vlastitim oblikom
u svojoj stvarnoj veličini.

![cars --help](../assets/img/cars-help.svg)

## Korak po korak {#step-by-step}

1. **Pokrenite je** s instaliranom igrom (pronalazi se u Steam bibliotekama i u
   `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ili navedite folder igre:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Učitajte je u preglednik**: **Učitajte datoteku s automobilima…** u postavkama prikaza, ili spustite
   datoteku na karticu utrke; ostaje u tom pregledniku. Krugovi čiji je broj automobila
   u datoteci tada se crtaju baš kao taj automobil (pogledajte
   [dokumentaciju preglednika o ponovnom prikazu utrke](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Pokrenite je ponovo** kad igra dobije nove automobile. Traje nekoliko sekundi i upisuje
   oko 5 MB.

## Opcije {#options}

| Opcija | Zadano | Značenje |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | datoteka koja se upisuje |
| `--game FOLDER` | pronađena instalirana igra | folder igre |

## Šta je u datoteci {#what-is-in-the-file}

Za svaku arhivu automobila u `media/Cars`: model `ProxyLOD` koji sadrži
(oko 900 trouglova), broj automobila onako kako ga navodi telemetrija, njegova marka,
oznaka modela i godina iz imena arhive, te njegovi točkovi i zadnja svjetla. Oblici
su u metrima, 1:1 s automobilom. Arhiva bez takvog modela (rekvizit prometa) se
navede i izostavi.

Datoteka je napravljena za 3DHeat preglednik; njen raspored, za sve koji je čitaju
negdje drugdje ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Dio | Raspored |
|---|---|
| cijela datoteka | gzip-kompresirana |
| magic | 8 bajtova `H3DCARS1` |
| dužina zaglavlja | little-endian u32 |
| zaglavlje | UTF-8 JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| dopuna | razmaci do višekratnika od 4 bajta |
| podaci | po automobilu: vrhovi kao po tri i16 (milimetri; x desno, y gore, z naprijed), zatim trouglovi kao po tri u16 |

Svaki unos u `cars`: `key`, `ordinals` (brojevi automobila onako kako ih navodi
telemetrija), `make`, `model`, `year`, `height` i `length` (m), `wheels`
(po točku `[x, y, z, radius]`, m), `lights` (tačke zadnjih svjetala `[x, y, z]`, m),
te `vertexAt`, `vertices`, `faceAt`, `faces` (pomaci u bajtima od početka
podataka, i brojevi).

Datoteka sadrži sadržaj igre: namijenjena je računaru na kojem je napravljena, a ne
za prosljeđivanje ([Pravila i licence](rules-and-licences.md)).
