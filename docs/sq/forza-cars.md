---
title: "Makinat e Forza-s"
nav_order: 6
lang: "sq"
source: forza-cars.md
source_hash: "e1b48f2525db"
nav_exclude: true
search_exclude: true
---
# Makinat e Forza-s: `cars` {#forza-cars-cars}

Shkruan çdo makinë të një Forza-je të instaluar, me detajin e ulët të vetë lojës, në një
skedar për skedën Analiza e garës të shikuesit (ajo vizaton një makinë për çdo xhiro që ke vozitur), kështu që çdo makinë e regjistruar vizatohet me formën e vet
dhe në madhësinë e vërtetë.

![cars --help](../assets/img/cars-help.svg)

## Hap pas hapi {#step-by-step}

1. **Nise** me lojën të instaluar (gjendet në bibliotekat e Steam dhe në
   `C:\XboxGames`):

   ```
   python -m heat3d_gamefiles cars -o forza.h3dcars
   ```

   Ose jepi emrin e dosjes së lojës:

   ```
   python -m heat3d_gamefiles cars --game "D:\Games\<Forza folder>" -o forza.h3dcars
   ```

2. **Ngarkoje në shikues**: **Ngarko skedarin e makinave…** te cilësimet e pamjes, ose hidhe
   skedarin mbi skedën e garës; mbetet në atë shfletues. Xhirot, numri i makinës i të cilave
   është në skedar, vizatohen pastaj si pikërisht ajo makinë (shih
   [dokumentet e shikuesit për riprodhimin e garës](https://holdi601.github.io/3DHeat/race-replay-and-scene.html#the-cars)).

3. **Nise përsëri** kur loja merr makina të reja. Zgjat sekonda dhe shkruan
   rreth 5 MB.

## Opsionet {#options}

| Opsioni | Parazgjedhja | Kuptimi |
|---|---|---|
| `-o`, `--out FILE` | `./forza.h3dcars`, ose `$HEAT3D_LEVELS/forza/forza.h3dcars` kur ai është vendosur | skedari që shkruhet |
| `--game FOLDER` | loja e instaluar që u gjet | dosja e lojës |

## Çfarë ka në skedar {#what-is-in-the-file}

Për çdo arkiv makine nën `media/Cars`: modeli `ProxyLOD` që mban
(rreth 900 trekëndësha), numri i makinës ashtu siç e thotë telemetria, marka,
etiketa e modelit dhe viti nga emri i arkivit, si dhe rrotat dhe dritat e pasme. Format
janë në metra, 1:1 me makinën. Një arkiv pa një model të tillë (një objekt trafiku)
emërtohet dhe lihet jashtë.

Skedari është bërë për shikuesin 3DHeat; ja struktura e tij, për kë e lexon
diku tjetër ([`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py)):

| Pjesa | Struktura |
|---|---|
| gjithë skedari | i ngjeshur me gzip |
| magic | 8 bajtet `H3DCARS1` |
| gjatësia e kokës | u32 little-endian |
| koka | JSON në UTF-8: `format` (`heat3d-cars`), `version`, `game`, `source`, `cars` |
| mbushja | hapësira deri në shumëfishin e 4 bajteve |
| të dhënat | për çdo makinë: kulmet si tri i16 secila (milimetra; x djathtas, y lart, z përpara), pastaj trekëndëshat si tri u16 secili |

Çdo hyrje e `cars`: `key`, `ordinals` (numrat e makinës ashtu siç i thotë
telemetria), `make`, `model`, `year`, `height` dhe `length` (m), `wheels`
(për çdo rrotë `[x, y, z, radius]`, m), `lights` (pikat e dritave të pasme `[x, y, z]`, m),
dhe `vertexAt`, `vertices`, `faceAt`, `faces` (zhvendosjet në bajte nga fillimi i
të dhënave, dhe numrat).

Skedari përmban përmbajtjen e lojës: është për makinën ku u bë, jo
për t'u shpërndarë ([Rregullat dhe licencat](rules-and-licences.md)).
