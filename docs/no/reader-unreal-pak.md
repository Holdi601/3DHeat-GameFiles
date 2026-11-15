---
title: Unreal .pak
nav_order: 1
lang: "no"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Lister og henter ut** Unreal 4.22-5.x `.pak`-arkiver: versjon 8, 9, 10, 11 og 12, Zlib-, Gzip- og Oodle-komprimering, og krypterte
arkiver når du oppgir AES-nøkkelen. Den tolker ikke det den henter ut (`.uasset`, `.umap`).

Kilde: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Kommandoer: `identify`, `list`, `extract` (se [Kommandoer](commands.md)).

## Oppsett {#layout}

Fotet ligger på slutten av filen og finnes ved å søke i de siste 1 024 bytene etter magien `0x5A6F12E1`. Feltrekkefølgen betyr noe:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Krypteringsflagget står **før** magien. Tas det fra etter magien, havner man på «Z» i «Zlib». Da rapporterer hvert arkiv seg selv som kryptert, og
hvert metodenavn mister første bokstav («lib», «odle»), en stille og plausibel feil. Versjonen er den lave byten, fordi «frozen index»-bygg setter en høy bit.

Indeksen holder monteringspunktet, hash-indeksen for stier, den fulle katalogindeksen, og en blokk med **kodede oppføringer**: en bitpakket form der et flaggord sier
hvilke tall som er 32-bit, komprimeringsmetoden (6 bit), om oppføringen er kryptert, blokktallet (16 bit) og blokkstørrelsen i enheter av 2 048 (6 bit). Den
helt ettall-blokkstørrelsen er en escape: den virkelige størrelsen følger som en u32 **før** forskyvningen. I et stort arkiv, lest etter størrelsene, forskjøv det 7 %
av oppføringene med fire byte, og gav dem forskyvninger i exabyte-området.

Hver oppførings fulle post gjentas rett før nyttelasten, så nyttelasten starter etter `8+8+8+20+4+1+4` byte, pluss `4 + 16 x blocks` når den er komprimert.
Krypterte blokker fylles til 16 byte.

## Hva den leser, og hva den avviser {#what-it-reads-and-what-it-refuses}

| Tilfelle | Resultat |
|---|---|
| versjon 8-12 | leses |
| annen versjon | `pak version N; this reader handles 8-12` (eldre versjoner lagrer en flat postliste, og det fantes ingen fil å teste mot) |
| ingen fotmagi | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks utenfor filen | avvist: fotet parset ikke slik det påsto |
| bare hash-indeks for stier | avvist: filnavnene ble hashet bort ved bygging og kan ikke gjenskapes |
| oppføringer i indeksens overløpsliste (katalogforskyvning -1) | hoppes over, ikke forfalsket |
| kryptert indeks, ingen nøkkel | `EncryptedPak`: «Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys.» På kommandolinjen: én linje og avslutningskode 1 |
| kryptert oppføring, ingen nøkkel | `EncryptedPak` ved lesing |
| metodene Zlib, Gzip, Oodle | pakkes ut (Oodle trenger et bibliotek, se [Oodle](reader-oodle.md)) |
| enhver annen metode | `compression method '...' is not supported` |

## Nøkler {#keys}

`--key` på `list` og `extract` tar en AES-256-nøkkel du allerede har, som 64 heksadesimale siffer, med eller uten `0x`. Alt annet avvises før arkivet
åpnes, med avslutningskode 2. Dekryptering er AES-256-ECB gjennom pakken `cryptography`. Det finnes ingen kodevei som skaffer en nøkkel: ingen medfølgende
nøkler, ingen søk i kjørbare filer, ingen lesing av minne. Se [Regler og lisenser](rules-and-licences.md).

## Verifisert {#verified}

Mot utgitte arkiver fra mer enn ett spill ble hver oppføring, inkludert ett svært stort arkiv, matchet med SHA-1-en Unreal skriver foran hver
nyttelast. Den hashen dekker bytene slik de er lagret, så et treff betyr at indekskodingen, nyttelastforskyvningen og hver komprimert blokkgrense var
riktige. De installerte testene (`test_pak.py`) gjentar dette på opptil fire ukrypterte pakker funnet under `steamapps\common\*\...\Content\Paks`. De kontrollerer
at hver oppførings forskyvning ligger innenfor filen, og at SHA-1 stemmer for en tilfeldig stikkprøve på 150 oppføringer per arkiv.
