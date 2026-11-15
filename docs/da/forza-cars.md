---
title: "Forza-biler"
nav_order: 6
lang: "da"
source: forza-cars.md
source_hash: "e1b48f2525db"
nav_exclude: true
search_exclude: true
---
# Forza-biler: `cars` {#forza-cars-cars}

Skriver hver bil i et installeret Forza med spillets egen lave detaljegrad til én
fil til vieweren's fane Løbsanalyse (den tegner en bil for hver omgang, du har kørt), så hver
optaget bil bliver tegnet i sin egen form i sin rigtige størrelse.

![cars --help](../assets/img/cars-help.svg)

## Trin for trin {#step-by-step}

1. **Kør den**, mens spillet er installeret (det findes i Steam-bibliotekerne og
   i `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Eller angiv spillets mappe:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Indlæs den i vieweren**: **Indlæs bilfil...** i visningsindstillingerne, eller slip
   filen på løbsfanen; den bliver i browseren. Omgange, hvis bilnummer står i
   filen, bliver så tegnet som netop den bil (se vieweren's
   [dokumentation om løbsgengivelse](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Kør den igen**, når spillet får nye biler. Det tager få sekunder og skriver
   cirka 5 MB.

## Valgmuligheder {#options}

| Valgmulighed | Standard | Betydning |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars`, eller `$HEAT3D_LEVELS/forza/forza.h3dcars`, når den er sat | filen, der skrives |
| `--game FOLDER` | det installerede spil, der findes | spillets mappe |

## Hvad der er i filen {#what-is-in-the-file}

For hvert bilarkiv under `media/Cars`: den `ProxyLOD`-model, det indeholder (cirka 900
trekanter), bilens nummer, som telemetrien angiver det, dens mærke, modelmærke og år
fra arkivets navn, samt dens hjul og baglygter. Formerne er i meter, 1:1 med bilen.
Et arkiv uden en sådan model (en trafikrekvisit) bliver navngivet og udeladt.

Filen er lavet til 3DHeat-vieweren. Dens opbygning, for dem der læser den andre steder
([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Del | Opbygning |
|---|---|
| hele filen | gzip-komprimeret |
| magi | de 8 bytes `H3DCARS1` |
| headerlængde | little-endian u32 |
| header | UTF-8-JSON: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| opfyldning | mellemrum op til en flerfoldig af 4 bytes |
| data | pr. bil: hjørnepunkter som tre i16 hver (millimeter; x til højre, y op, z fremad), derefter trekanter som tre u16 hver |

Hver `cars`-post: `key`, `ordinals` (bilens numre, som telemetrien angiver dem), `make`, `model`, `year`, `height` og `length` (m), `wheels`
(pr. hjul `[x, y, z, radius]`, m), `lights` (baglygtepunkter `[x, y, z]`, m) og
`vertexAt`, `vertices`, `faceAt`, `faces` (byteforskydninger fra starten af
data, og antal).

Filen indeholder spillets indhold: den er til den maskine, den blev lavet på, ikke
til at give videre ([Regler og licenser](rules-and-licences.md)).
