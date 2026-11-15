---
title: Unreal `.pak`
nav_order: 1
lang: "da"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Lister og udtrækker** Unreal 4.22-5.x `.pak`-arkiver: versionerne 8, 9, 10, 11 og 12, Zlib-, Gzip- og Oodle-komprimering, og krypterede arkiver, når du angiver AES-nøglen. Den fortolker ikke det, den udtrækker (`.uasset`, `.umap`).

Kilde: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Kommandoer: `identify`, `list`, `extract` (se [Kommandoer](commands.md)).

## Layout {#layout}

Footeren ligger til sidst i filen og findes ved at søge i de sidste 1.024 bytes efter magic-værdien `0x5A6F12E1`. Feltrækkefølgen har betydning:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Krypteringsflaget står **før** magic-værdien. Hvis man henter det efter magic-værdien, lander man på "Z" i "Zlib". Så melder hvert arkiv sig selv som krypteret, og hvert metodenavn mister sit første bogstav ("lib", "odle"), en stille og troværdig fejl. Versionen er den laveste byte, fordi "frozen index"-builds sætter en høj bit.

Indekset indeholder monteringspunktet, stihash-indekset, det fulde mappeindeks og en blok af **kodede poster**: en bit-pakket form, hvor et flag-ord siger, hvilke tal der er 32-bit, komprimeringsmetoden (6 bit), om posten er krypteret, blokantallet (16 bit) og blokstørrelsen i enheder af 2.048 (6 bit). Blokstørrelsen med alle ettal er et escape: den rigtige størrelse følger som en u32 **før** offsettet. I et stort arkiv flyttede læsning efter størrelserne 7 % af posterne fire bytes og gav dem offsets i exabytes.

Hver posts fulde post gentages lige før dens nyttelast, så nyttelasten starter efter `8+8+8+20+4+1+4` bytes, plus `4 + 16 x blocks`, når den er komprimeret. Krypterede blokke polstres til 16 bytes.

## Hvad den læser, og hvad den afviser {#what-it-reads-and-what-it-refuses}

| Tilfælde | Resultat |
|---|---|
| versionerne 8-12 | læst |
| enhver anden version | `pak version N; this reader handles 8-12` (ældre versioner gemmer en flad postliste, og der var ingen fil at teste mod) |
| ingen footer-magic | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks uden for filen | afvist: footeren blev ikke parset som angivet |
| indeks med kun stihash | afvist: filnavnene blev hashet væk under build og kan ikke gendannes |
| poster i indeksets overløbsliste (mappe-offset -1) | springes over, ikke forfalsket |
| krypteret indeks, ingen nøgle | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." På kommandolinjen: én linje og exit-kode 1 |
| krypteret post, ingen nøgle | `EncryptedPak` ved læsning |
| metoderne Zlib, Gzip, Oodle | pakket ud (Oodle kræver et bibliotek, se [Oodle](reader-oodle.md)) |
| enhver anden metode | `compression method '...' is not supported` |

## Nøgler {#keys}

`--key` på `list` og `extract` tager en AES-256-nøgle, du allerede har, som 64 hex-cifre, med eller uden `0x`. Alt andet afvises, før arkivet åbnes, med exit-kode 2. Dekryptering er AES-256-ECB via pakken `cryptography`. Der er ingen kodesti, der henter en nøgle: ingen medleverede nøgler, ingen søgning i eksekverbare filer, ingen læsning af hukommelse. Se [Regler og licenser](rules-and-licences.md).

## Verificeret {#verified}

Mod leverede arkiver fra mere end ét spil matchede hver post, inklusive ét meget stort arkiv, med den SHA-1, Unreal skriver før hver nyttelast. Hashet dækker bytes, som de er gemt, så et match betyder, at indeksafkodningen, nyttelastoffsettet og hver komprimerede blokgrænse var rigtige. Testene mod det installerede spil (`test_pak.py`) gentager dette på op til fire ukrypterede paks fundet under `steamapps\common\*\...\Content\Paks`. De tjekker, at hver posts offset ligger inden for filen, og at SHA-1 passer for en tilfældig stikprøve på 150 poster pr. arkiv.
