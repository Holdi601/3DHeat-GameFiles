---
title: "Unreal .pak"
nav_order: 1
lang: "bs"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Navodi i izvlači** Unreal 4.22-5.x `.pak` arhive: verzije 8, 9, 10, 11 i 12,
Zlib, Gzip i Oodle kompresiju, te šifrirane arhive kad date AES ključ. Ne
interpretira ono što izvuče (`.uasset`, `.umap`).

Izvor: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Komande: `identify`, `list`, `extract` (pogledajte [Komande](commands.md)).

## Raspored {#layout}

Podnožje je na kraju datoteke i pronalazi se traženjem magica `0x5A6F12E1` u
posljednjih 1.024 bajta. Redoslijed njegovih polja je bitan:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Zastavica šifriranja stoji **prije** magica. Ako se uzme iza magica, sleti na "Z"
iz "Zlib". Tada svaka arhiva prijavljuje da je šifrirana, a svako ime metode
gubi prvo slovo ("lib", "odle"), tihi i uvjerljiv kvar. Verzija je donji bajt,
jer verzije "frozen index" postavljaju visoki bit.

Indeks sadrži tačku montiranja, indeks hasheva putanja, puni indeks direktorija i
blok **kodiranih unosa**: bitno pakiran oblik gdje riječ zastavica kaže koji su
brojevi 32-bitni, metodu kompresije (6 bita), da li je unos šifriran, broj
blokova (16 bita) i veličinu bloka u jedinicama od 2.048 (6 bita). Veličina
bloka sa svim jedinicama je escape: prava veličina slijedi kao u32 **prije**
pomaka. U velikoj arhivi, čitanje nakon veličina pomjeralo je 7% unosa za
četiri bajta i davalo im pomake u eksabajtima.

Puni zapis svakog unosa ponavlja se neposredno prije njegovog payloada, pa
payload počinje nakon `8+8+8+20+4+1+4` bajta, plus `4 + 16 x blocks` kad je
komprimiran. Šifrirani blokovi dopunjuju se na 16 bajta.

## Šta čita, a šta odbija {#what-it-reads-and-what-it-refuses}

| Slučaj | Rezultat |
|---|---|
| verzije 8-12 | čita se |
| bilo koja druga verzija | `pak version N; this reader handles 8-12` (starije verzije pohranjuju ravnu listu zapisa, a nije bilo datoteke za testiranje) |
| nema magica podnožja | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks izvan datoteke | odbija se: podnožje se nije parsiralo kako tvrdi |
| samo indeks hasheva putanja | odbija se: imena datoteka su pri izgradnji pretvorena u hasheve i ne mogu se povratiti |
| unosi u listi preljeva indeksa (pomak direktorija -1) | preskaču se, ne lažiraju |
| šifriran indeks, nema ključa | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Na komandnoj liniji, jedan red i izlazni kod 1 |
| šifriran unos, nema ključa | `EncryptedPak` pri čitanju |
| metode Zlib, Gzip, Oodle | dekomprimira se (Oodle treba biblioteku, pogledajte [Oodle](reader-oodle.md)) |
| bilo koja druga metoda | `compression method '...' is not supported` |

## Ključevi {#keys}

`--key` na `list` i `extract` uzima AES-256 ključ koji već posjedujete, kao 64
heksadecimalne cifre, sa ili bez `0x`. Sve drugo se odbija prije otvaranja
arhive, s izlaznim kodom 2. Dešifriranje je AES-256-ECB kroz paket
`cryptography`. Ne postoji putanja koda koja dobija ključ: nema priloženih
ključeva, pretraživanja izvršnih datoteka, čitanja memorije. Pogledajte
[Pravila i licence](rules-and-licences.md).

## Provjereno {#verified}

Naspram isporučenih arhiva više od jedne igre, svaki unos, uključujući jednu vrlo
veliku arhivu, podudarao se sa SHA-1 koji Unreal piše ispred svakog payloada. Taj
hash pokriva bajte kako su pohranjeni, pa podudaranje znači da su dekodiranje
indeksa, pomak payloada i svaka granica komprimiranog bloka bili ispravni. Testovi
na instaliranim igrama (`test_pak.py`) ponavljaju to na do četiri nešifrirana paka
pronađena pod `steamapps\common\*\...\Content\Paks`. Provjeravaju da svaki pomak
unosa leži unutar datoteke i da se SHA-1 podudara za nasumični uzorak od 150
unosa po arhivi.
