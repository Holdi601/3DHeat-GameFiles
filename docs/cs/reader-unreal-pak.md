---
title: Unreal .pak
nav_order: 1
lang: "cs"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Vypisuje a extrahuje** archivy `.pak` Unreal 4.22 až 5.x: verze 8, 9, 10, 11 a 12,
komprimace Zlib, Gzip a Oodle, a šifrované archivy, když dodáte klíč AES. Co
extrahuje, neinterpretuje (`.uasset`, `.umap`).

Zdroj: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Příkazy: `identify`, `list`, `extract` (viz [Příkazy](commands.md)).

## Rozložení {#layout}

Patka je na konci souboru a hledá se v posledních 1 024 bajtech podle magie
`0x5A6F12E1`. Pořadí polí je důležité:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Příznak šifrování je **před** magií. Když se vezme z místa za magií, trefí se do
"Z" v "Zlib". Pak každý archiv hlásí, že je šifrovaný, a každý název metody přijde o
první písmeno ("lib", "odle"), tiché a věrohodné selhání. Verze je nejnižší bajt,
protože buildy "frozen index" nastavují vysoký bit.

Index obsahuje bod připojení, index hashů cest, úplný index adresáře a blok
**zakódovaných položek**: bitově balenou formu, kde slovo příznaků říká, která čísla
jsou 32bitová, metodu komprimace (6 bitů), zda je položka šifrovaná, počet bloků (16
bitů) a velikost bloku v jednotkách 2 048 (6 bitů). Velikost bloku samé jedničky je
únik: skutečná velikost následuje jako u32 **před** posunem. V rozsáhlém archivu
čtení jí až po velikostech posunulo 7 % položek o čtyři bajty a dalo jim posuny v
exabajtech.

Úplný záznam každé položky se opakuje těsně před jejím datem, takže data začínají po
`8+8+8+20+4+1+4` bajtech, plus `4 + 16 x blocks`, když je komprimovaná. Šifrované
bloky se doplňují na 16 bajtů.

## Co čte a co odmítá {#what-it-reads-and-what-it-refuses}

| Případ | Výsledek |
|---|---|
| verze 8-12 | čte se |
| jakákoli jiná verze | `pak version N; this reader handles 8-12` (starší verze ukládají plochý seznam záznamů a nebyl po ruce soubor na test) |
| chybí magie patky | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index mimo soubor | odmítnuto: patka se nenaparsovala tak, jak tvrdí |
| jen index hashů cest | odmítnuto: názvy souborů byly při sestavení zahashované a nejdou obnovit |
| položky v přetokovém seznamu indexu (offset adresáře -1) | přeskočí se, neudělají se falešně |
| šifrovaný index, bez klíče | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Na příkazové řádce jeden řádek a návratový kód 1 |
| šifrovaná položka, bez klíče | `EncryptedPak` při čtení |
| metody Zlib, Gzip, Oodle | rozbalí se (Oodle potřebuje knihovnu, viz [Oodle](reader-oodle.md)) |
| jakákoli jiná metoda | `compression method '...' is not supported` |

## Klíče {#keys}

`--key` u `list` a `extract` bere klíč AES-256, který už máte, jako 64 šestnáctkových
číslic, s `0x` nebo bez něj. Cokoli jiného se odmítne ještě před otevřením archivu,
s návratovým kódem 2. Dešifrování je AES-256-ECB přes balíček `cryptography`. Neexistuje
žádná cesta kódu, která by klíč získala: žádné přibalené klíče, žádné hledání v
programech, žádné čtení paměti. Viz [Pravidla a licence](rules-and-licences.md).

## Ověřeno {#verified}

Proti dodaným archivům více her byla každá položka, včetně jednoho velmi velkého
archivu, ověřena podle SHA-1, které Unreal zapisuje před každým datem. Tento hash
pokrývá bajty tak, jak jsou uložené, takže shoda znamená, že dekódování indexu,
posun dat i každá hranice komprimovaného bloku byly správně. Testy na nainstalované
hře (`test_pak.py`) to opakují až u čtyř nešifrovaných paků nalezených pod
`steamapps\common\*\...\Content\Paks`. Kontrolují, že posun každé položky leží uvnitř
souboru a že SHA-1 sedí u náhodného vzorku 150 položek na archiv.
