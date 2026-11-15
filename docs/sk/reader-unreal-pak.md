---
title: Unreal .pak
nav_order: 1
lang: "sk"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Vypisuje a extrahuje** archívy Unreal `.pak` verzií 4.22 až 5.x: verzie 8, 9, 10, 11
a 12, kompresiu Zlib, Gzip a Oodle a šifrované archívy, keď dodáte kľúč AES. Neinterpretuje
to, čo extrahuje (`.uasset`, `.umap`).

Zdroj: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Príkazy: `identify`, `list`, `extract` (pozri [Príkazy](commands.md)).

## Rozloženie {#layout}

Pätka je na konci súboru a nájde sa hľadaním magického čísla `0x5A6F12E1` v posledných
1 024 bajtoch. Záleží na poradí polí:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Príznak šifrovania je **pred** magickým číslom. Ak sa vezme zo miesta za ním, trafí sa
na „Z“ v „Zlib“. Potom sa každý archív hlási ako šifrovaný a každý názov metódy stratí
prvé písmeno („lib“, „odle“), tichá a vierohodná chyba. Verzia je nižší bajt, lebo
buildy „frozen index“ nastavujú vysoký bit.

Index obsahuje bod pripojenia, index ciest hashov, úplný index adresárov a blok
**zakódovaných položiek**: formát v bitoch, kde slovo príznakov hovorí, ktoré čísla sú
32-bitové, metódu kompresie (6 bitov), či je položka šifrovaná, počet blokov (16 bitov)
a veľkosť bloku v jednotkách 2 048 (6 bitov). Veľkosť bloku, ktorá má všetky jednotky,
je únikový kód: skutočná veľkosť nasleduje ako u32 **pred** offsetom. V veľkom archíve
sa čítanie po veľkostiach posunulo pri 7 % položiek o štyri bajty a dalo im offsety
v exabajtoch.

Úplný záznam každej položky sa zopakuje tesne pred jej užitočnými dátami, takže dáta
začínajú po `8+8+8+20+4+1+4` bajtoch, plus `4 + 16 x blocks` pri komprimovaných.
Šifrované bloky sú dorovnané na 16 bajtov.

## Čo sa číta a čo sa odmieta {#what-it-reads-and-what-it-refuses}

| Prípad | Výsledok |
|---|---|
| verzie 8-12 | prečíta sa |
| akákoľvek iná verzia | `pak version N; this reader handles 8-12` (staršie verzie ukladajú plochý zoznam záznamov a nebol k dispozícii žiadny súbor na testovanie) |
| chýba magické číslo pätky | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index mimo súboru | odmietnuté: pätka sa nezparsovala tak, ako tvrdí |
| len index hashov ciest | odmietnuté: názvy súborov boli zahashované pri zostavovaní a nedajú sa získať |
| položky v preplnenom zozname indexu (offset adresára -1) | preskočené, nie vymyslené |
| šifrovaný index, bez kľúča | `EncryptedPak`: „Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys.“ Na príkazovom riadku jeden riadok a návratový kód 1 |
| šifrovaná položka, bez kľúča | `EncryptedPak` pri čítaní |
| metódy Zlib, Gzip, Oodle | rozbalia sa (Oodle potrebuje knižnicu, pozri [Oodle](reader-oodle.md)) |
| akákoľvek iná metóda | `compression method '...' is not supported` |

## Kľúče {#keys}

`--key` pri `list` a `extract` berie kľúč AES-256, ktorý už máte, ako 64 hexadecimálnych
číslic, s `0x` alebo bez neho. Čokoľvek iné sa odmietne skôr, než sa archív otvorí,
s návratovým kódom 2. Dešifrovanie ide cez AES-256-ECB balíkom `cryptography`. Neexistuje
žiadna cesta v kóde, ktorá kľúč získa: žiadne dodávané kľúče, žiadne hľadanie
v spustiteľných súboroch, žiadne čítanie pamäte. Pozri [Pravidlá a licencie](rules-and-licences.md).

## Overené {#verified}

Na dodávaných archívoch viacerých hier sa každá položka vrátane jedného veľmi veľkého
archívu zhodovala so SHA-1, ktoré Unreal zapisuje pred každý užitočný náklad. Tento hash
pokrýva bajty tak, ako sú uložené, takže zhoda znamená, že dekódovanie indexu, offset
užitočných dát a každá hranica komprimovaného bloku boli správne. Testy na nainštalovaných
hrách (`test_pak.py`) to zopakujú na až štyroch nešifrovaných pakoch nájdených pod
`steamapps\common\*\...\Content\Paks`. Kontrolujú, že offset každej položky leží vnútri
súboru, a že SHA-1 sedí pre náhodnú vzorku 150 položiek na archív.
