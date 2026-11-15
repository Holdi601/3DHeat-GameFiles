---
title: Unreal .pak
nav_order: 1
lang: "hu"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Listáz és kibont** Unreal 4.22–5.x `.pak` archívumokat: 8, 9, 10, 11 és 12-es verzió, Zlib, Gzip és Oodle
tömörítéssel, és titkosított archívumokat, ha megadod az AES-kulcsot. Nem értelmezi azt, amit kibont (`.uasset`,
`.umap`).

Forrás: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Parancsok: `identify`, `list`, `extract` (lásd: [Parancsok](commands.md)).

## Elrendezés {#layout}

A lábléc a fájl végén van, és a utolsó 1024 bájtban keresve találjuk meg a `0x5A6F12E1` mágikus számot.
A mezőinek sorrendje számít:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

A titkosítási jelző a mágikus szó **előtt** van. Ha a mágikus szó utánról olvassuk, a „Z" a „Zlib"-ből lesz
az olvasott bájt. Ekkor minden archívum titkosítottnak látszik, és minden módszernév elveszíti az első betűjét
(„lib", „odle"), csendes és hihető hiba. A verzió az alsó bájt, mert a „fagyasztott index" buildek egy magas bitet
állítanak.

Az index tartalmazza a csatolási pontot, a path-hash indexet, a teljes könyvtárindexet, és egy blokkot
**kódolt bejegyzésekből**: egy bit-csomagolt formából, ahol egy jelzőszó megmondja, mely számok 32 bitesek, a
tömörítési módszert (6 bit), azt, hogy a bejegyzés titkosított-e, a blokkok számát (16 bit) és a blokkméretet
2048-as egységekben (6 bit). A csupa egyes blokkméret egy escape: a valódi méret egy u32, **az eltolás előtt**.
Egy nagy archívumban az olvasás a méretek után 7%-nyi bejegyzést négy bájttal eltolt, és nekik az exabájtokban
lévő eltolásokat adta.

Minden bejegyzés teljes rekordja megismétlődik közvetlenül a tartalma előtt, így a tartalom a
`8+8+8+20+4+1+4` bájt után kezdődik, plusz `4 + 16 x blocks` tömörített esetben. A titkosított blokkok 16
bájtra vannak kitöltve.

## Mit olvas, és mit utasít el {#what-it-reads-and-what-it-refuses}

| Eset | Eredmény |
|---|---|
| 8–12-es verziók | olvasva |
| bármely más verzió | `pak version N; this reader handles 8-12` (a régebbi verziók lapos rekordlistát tárolnak, és nem volt fájl a teszteléshez) |
| nincs lábléc-mágikus szó | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| az index a fájlon kívül esik | megtagadva: a lábléc nem úgy dekódolódott, ahogy állítja |
| csak path-hash index | megtagadva: a fájlneveket az építéskor hash-elték, nem állíthatók vissza |
| bejegyzések az index túlcsordulási listájában (könyvtári eltolás -1) | kihagyva, nem hamisítva |
| titkosított index, nincs kulcs | `EncryptedPak`: „Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." A parancssoron egy sor és 1-es kilépési kód |
| titkosított bejegyzés, nincs kulcs | `EncryptedPak` olvasáskor |
| Zlib, Gzip, Oodle módszerek | kicsomagolva (az Oodle-hez könyvtár kell, lásd: [Oodle](reader-oodle.md)) |
| bármely más módszer | `compression method '...' is not supported` |

## Kulcsok {#keys}

A `--key` a `list` és `extract` parancsokon egy AES-256 kulcsot vesz, amely már nálad van, 64 hexadecimális
számjegyként, `0x`-szel vagy anélkül. Minden más megtagadva, mielőtt az archívumot megnyitnánk, 2-es kilépési kóddal.
A visszafejtés AES-256-ECB a `cryptography` csomagon át. Nincs olyan kódútvonal, amely kulcsot szerezne: nincs
beágyazott kulcs, nincs végrehajtható fájl átkutatása, nincs memória-olvasás. Lásd: [Szabályok és licencek](rules-and-licences.md).

## Ellenőrizve {#verified}

Több játék szállított archívumain minden bejegyzés, egy nagyon nagy archívumot is beleértve, egyezett a
SHA-1-gyel, amelyet az Unreal minden tartalom elé ír. Ez a hash a tárolt bájtokat fedi le, így az egyezés azt
jelenti, hogy az index dekódolása, a tartalom eltolása és minden tömörített blokkhatár helyes volt. A telepített
játékon futó tesztek (`test_pak.py`) ezt megismétlik legfeljebb négy, `steamapps\common\*\...\Content\Paks`
alatt talált titkosítatlan pakon. Ellenőrzik, hogy minden bejegyzés eltolása a fájlon belül van, és hogy a SHA-1
egyezik egy véletlen, archívumonként 150 bejegyzésből álló mintán.
