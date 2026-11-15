---
title: "Mașinile Forza"
nav_order: 6
lang: "ro"
source: forza-cars.md
source_hash: "30d017479887"
nav_exclude: true
search_exclude: true
---
# Mașinile Forza: `cars` {#forza-cars-cars}

Scrie fiecare mașină a unui Forza instalat, la nivelul de detaliu propriu al jocului, într-un singur fișier pentru fila Analiză de cursă din vizualizator (desenează câte o mașină pentru fiecare tur pe care l-ai parcurs). Astfel, fiecare mașină înregistrată este desenată în propria formă, la dimensiunea ei reală.

![ajutorul comenzii cars](../assets/img/cars-help.svg)

## Pas cu pas {#step-by-step}

1. **Rulează-l** cu jocul instalat (este găsit în bibliotecile Steam și în `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Sau numește folderul jocului:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Încarcă-l în vizualizator**: **Încarcă fișierul cu mașini…** din secțiunea Vizualizare, sau trage fișierul pe fila Analiză de cursă; rămâne în acel browser. Tururile al căror număr de mașină se află în fișier sunt desenate apoi ca mașina aceea (vezi [documentația despre redarea cursei](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars) a vizualizatorului).

3. **Rulează-l din nou** atunci când jocul primește mașini noi. Durează câteva secunde și scrie aproximativ 5 MB.

## Opțiuni {#options}

| Opțiune | Implicit | Înseamnă |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars` | fișierul de scris |
| `--game FOLDER` | jocul instalat găsit | folderul jocului |

## Ce este în fișier {#what-is-in-the-file}

Pentru fiecare arhivă de mașină din `media/Cars`: modelul `ProxyLOD` pe care îl conține (aproximativ 900 de triunghiuri), numărul mașinii așa cum îl spune telemetria, marca, eticheta modelului și anul din numele arhivei, precum și roțile și luminile din spate. Formele sunt în metri, 1:1 cu mașina. O arhivă fără un astfel de model (un obiect decorativ de trafic) este numită și lăsată afară.

Fișierul este făcut pentru vizualizatorul 3DHeat. Structura lui, pentru cine îl citește în altă parte ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Parte | Structură |
|---|---|
| întregul fișier | comprimat gzip |
| magic | cei 8 octeți `H3DCARS1` |
| lungimea antetului | u32 little-endian |
| antet | JSON UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| umplutură | spații până la un multiplu de 4 octeți |
| date | pentru fiecare mașină: vârfurile ca trei i16 fiecare (milimetri; x dreapta, y sus, z înainte), apoi triunghiurile ca trei u16 fiecare |

Fiecare intrare `cars`: `key`, `ordinals` (numerele mașinii așa cum le spune telemetria), `make`, `model`, `year`, `height` și `length` (m), `wheels` (pentru fiecare roată `[x, y, z, radius]`, m), `lights` (punctele luminilor din spate `[x, y, z]`, m) și `vertexAt`, `vertices`, `faceAt`, `faces` (deplasări în octeți de la începutul datelor, și numărători).

Fișierul conține conținutul jocului: este pentru mașina pe care a fost făcut, nu pentru a fi trimis mai departe ([Reguli și licențe](rules-and-licences.md)).
