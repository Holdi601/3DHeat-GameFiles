---
title: "Inspectarea arhivelor"
nav_order: 3
lang: "ro"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Inspectarea arhivelor: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Un joc își împachetează fișierele în cutii mari numite **arhive**. Aceste comenzi se uită la eticheta unei cutii, arată ce este în ea și scot un lucru din ea.

Înainte de a exporta ceva dintr-un joc necunoscut, uită-te ce livrează. Aceste patru comenzi citesc un fișier și îți spun ce este și ce conține; nu scriu nimic, în afară de intrarea pe care o ceri de la `extract`.

![identify, list și extract rulate pe un zip mic](../assets/img/inspect-archives.svg)

*O rulare pe un zip sintetic, aranjat ca un nivel din BeamNG.drive.*

## Pas cu pas {#step-by-step}

1. **Întreabă ce fișier este.** `identify` citește octeții, nu extensia:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Spune formatul (Unreal `.pak`, IoStore `.utoc`/`.ucas`, pachet Unity sau `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` sau `.modelbin`, BeamNG `.cdae`/`.ter`, zip), versiunea lui, câte intrări are și dacă este criptat.

2. **Listează ce este înăuntru.** `list` afișează o linie pentru fiecare intrare: dimensiune, compresie, cale. Restrânge-o cu `--filter`, limitează-o cu `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Scoate o intrare.** `extract` scrie o intrare (în folderul în care te afli, dacă `--out` nu spune altceva), după calea afișată de `list` (sau `#12`, după număr, într-un `.minizip` fără nume):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` listează și verifică mesh-urile dintr-un `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Opțiuni {#options}

| Comandă | Opțiune | Înseamnă |
|---|---|---|
| `identify` | `<file>` | orice fișier |
| `list` | `<archive>` | `.pak`, `.utoc` (sau `.ucas` de lângă el), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | doar căile care conțin TEXT |
| | `--limit N` | cel mult N linii |
| | `--key HEX` | o cheie AES-256 (64 de cifre hexa) pe care o deții deja; doar un `.pak` criptat are nevoie de ea |
| `extract` | `<archive> <path>` | arhiva și calea intrării, așa cum o afișează `list` |
| | `--out FILE` | unde să fie scrisă (implicit: numele fișierului intrării) |
| | `--key HEX` | ca la `list` |
| `meshes` | `<file>`, `--limit N` | un `SerializedFile` Unity; cel mult N mesh-uri |

Instrumentul nu livrează chei și nu recuperează niciuna: o arhivă criptată se deschide doar cu o cheie pe care o dați dumneavoastră. Un fișier pe care nu îl poate citi este refuzat, pe o linie, cu codul de ieșire 1.

Fiecare comandă și cod de ieșire se află în [Comenzi](commands.md). Modul în care este citit fiecare format este la [Cititoare de arhive](archive-readers.md).
