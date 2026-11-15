---
title: Unreal .pak
nav_order: 1
lang: "hr"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Popisuje i izdvaja** Unreal 4.22-5.x `.pak` arhive: verzije 8, 9, 10, 11 i 12, kompresije Zlib,
Gzip i Oodle, te šifrirane arhive kad vi predate AES ključ. Ne tumači ono što izdvaja
(`.uasset`, `.umap`).

Izvor: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Naredbe: `identify`, `list`, `extract` (vidi [Naredbe](commands.md)).

## Raspored {#layout}

Podnožje je na kraju datoteke i pronalazi se pretragom zadnjih 1024 bajta za magičnim brojem
`0x5A6F12E1`. Redoslijed polja je važan:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Zastavica šifriranja stoji **prije** magičnog broja. Uzeti je iza magičnog broja znači pasti na
"Z" u "Zlib". Tada se svaka arhiva prijavljuje kao šifrirana, a svakom nazivu metode nedostaje
prvo slovo ("lib", "odle"), tiha i uvjerljiva pogreška. Verzija je donji bajt, jer "frozen index"
verzije postavljaju visoki bit.

Indeks sadrži točku montiranja, indeks putanja hasheva, puni indeks direktorija i blok
**kodiranih unosa**: oblik u bitovima gdje riječ zastavica kaže koji su brojevi 32-bitni, metodu
kompresije (6 bitova), je li unos šifriran, broj blokova (16 bitova) i veličinu bloka u jedinicama
od 2048 (6 bitova). Sve-jedinice veličina bloka je izlaz: stvarna veličina slijedi kao u32
**prije** pomaka. U velikoj arhivi, čitanje nakon što su veličine pomaknute, pomaknulo je 7%
unosa za četiri bajta i dalo im pomake u eksabajtima.

Potpuni zapis svakog unosa ponavlja se tik prije njegova podatka, pa podatak počinje nakon
`8+8+8+20+4+1+4` bajta, plus `4 + 16 x blocks` kad je komprimiran. Šifrirani blokovi se popunjavaju
do 16 bajtova.

## Što čita, a što odbija {#what-it-reads-and-what-it-refuses}

| Slučaj | Rezultat |
|---|---|
| verzije 8-12 | čita se |
| bilo koja druga verzija | `pak version N; this reader handles 8-12` (starije verzije spremaju ravan popis zapisa, a nije bilo datoteke za provjeru) |
| nema magičnog broja podnožja | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks izvan datoteke | odbijeno: podnožje se nije parsiralo kako tvrdi |
| samo indeks putanja hasheva | odbijeno: imena datoteka su hashirana pri izradi i ne mogu se povratiti |
| unosi na popisu prekoračenja indeksa (pomak direktorija -1) | preskočeni, ne izmišljaju se |
| šifrirani indeks, bez ključa | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Iz naredbenog retka: jedan redak i izlazni kod 1 |
| šifrirani unos, bez ključa | `EncryptedPak` pri čitanju |
| metode Zlib, Gzip, Oodle | raspakiraju se (Oodle treba biblioteku, vidi [Oodle](reader-oodle.md)) |
| bilo koja druga metoda | `compression method '...' is not supported` |

## Ključevi {#keys}

`--key` uz `list` i `extract` uzima AES-256 ključ koji već imate, kao 64 heksadecimalne
znamenke, s `0x` ili bez njega. Sve drugo se odbija prije otvaranja arhive, s izlaznim kodom 2.
Dešifriranje je AES-256-ECB preko paketa `cryptography`. Nema puta u kodu koji dobiva ključ: nema
ugrađenih ključeva, nema pretrage izvršnih datoteka, nema čitanja memorije. Vidi
[Pravila i licence](rules-and-licences.md).

## Provjereno {#verified}

Na isporučenim arhivama više igara, svaki unos, uključujući jednu vrlo veliku arhivu, odgovara
SHA-1 hashu koji Unreal piše ispred svakog podatka. Taj hash pokriva bajtove kako su spremljeni,
pa podudaranje znači da su dekodiranje indeksa, pomak podatka i svaka granica kompresiranog bloka
ispravni. Testovi na instaliranim igrama (`test_pak.py`) ponavljaju to na do četiri nešifrirana paka
pronađena pod `steamapps\common\*\...\Content\Paks`. Provjeravaju da pomak svakog unosa leži unutar
datoteke i da se SHA-1 podudara za slučajan uzorak od 150 unosa po arhivi.
