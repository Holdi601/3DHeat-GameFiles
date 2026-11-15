---
title: "Unreal .pak"
nav_order: 1
lang: "sl"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Izpisuje in izvlači** arhive `.pak` Unreal 4.22-5.x: različice 8, 9, 10, 11 in 12, stiskanje Zlib, Gzip in Oodle ter šifrirane arhive, kadar podate ključ AES. Ne razlaga tega, kar izvleče (`.uasset`, `.umap`).

Vir: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Ukazi: `identify`, `list`, `extract` (glejte [Ukazi](commands.md)).

## Postavitev {#layout}

Noga je na koncu datoteke in se najde tako, da se zadnjih 1.024 bajtov preišče za magično številko `0x5A6F12E1`. Vrstni red polj je pomemben:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Zastavica šifriranja je **pred** magično številko. Če se vzame iz mesta za njo, pristane na "Z" v "Zlib". Potem vsak arhiv sporoči, da je šifriran, in vsakemu imenu metode zmanjka prva črka ("lib", "odle"), kar je tiha in verjetna napaka. Različica je nižji bajt, ker gradnje "frozen index" nastavijo visoki bit.

Kazalo vsebuje točko montaže, kazalo zgoščenih poti, celoten imenik in blok **kodiranih vnosov**: obliko, zapakirano v bite, kjer beseda zastavic pove, katera števila so 32-bitna, metodo stiskanja (6 bitov), ali je vnos šifriran, število blokov (16 bitov) in velikost bloka v enotah po 2.048 (6 bitov). Vsa enice v velikosti bloka so pobeg: prava velikost sledi kot u32 **pred** odmikom. V veliki arhivu je branje po velikostih premaknilo 7 % vnosov za štiri bajte in jim dalo odmike v eksabajtih.

Celoten zapis vsakega vnosa se ponovi tik pred njegovim podatkom, zato se podatek začne po `8+8+8+20+4+1+4` bajtih, plus `4 + 16 x blocks`, če je stisnjen. Šifrirani bloki so podložni na 16 bajtov.

## Kaj bere in kaj zavrne {#what-it-reads-and-what-it-refuses}

| Primer | Rezultat |
|---|---|
| različice 8-12 | prebrane |
| katera koli druga različica | `pak version N; this reader handles 8-12` (starejše različice shranjujejo ravni seznam zapisov, testne datoteke pa ni bilo na voljo) |
| ni magične številke noge | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| kazalo zunaj datoteke | zavrnjeno: noga se ni razčlenila, kot je trdila |
| samo kazalo zgoščenih poti | zavrnjeno: imena datotek so bila ob gradnji zgoščena in se ne dajo obnoviti |
| vnosi v prelivnem seznamu kazala (odmik imenika -1) | preskočeni, ne ponarejeni |
| šifrirano kazalo, brez ključa | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." V ukazni vrstici ena vrstica in izhodna koda 1 |
| šifrirani vnos, brez ključa | `EncryptedPak` pri branju |
| metode Zlib, Gzip, Oodle | razširjene (Oodle potrebuje knjižnico, glejte [Oodle](reader-oodle.md)) |
| katera koli druga metoda | `compression method '...' is not supported` |

## Ključi {#keys}

`--key` pri `list` in `extract` vzame ključ AES-256, ki ga že imate, kot 64 šestnajstiških številk, z ali brez `0x`. Vse drugo je zavrnjeno, preden se arhiv odpre, z izhodno kodo 2. Dešifriranje je AES-256-ECB prek paketa `cryptography`. Ni nobene kodirne poti, ki bi ključ pridobila: ni vgrajenih ključev, ni iskanja po izvršljivih datotekah, ni branja pomnilnika. Glejte [Pravila in licence](rules-and-licences.md).

## Preverjeno {#verified}

Proti objavljenim arhivom več iger se je vsak vnos, tudi eden zelo velikega arhiva, ujel z SHA-1, ki ga Unreal zapiše pred vsak podatek. Ta zgoščena vrednost pokriva bajte, kakor so shranjeni, zato ujemanje pomeni, da so bili pravilni dekodiranje kazala, odmik podatka in vsaka meja stisnjenega bloka. Testi na nameščeni igri (`test_pak.py`) to ponovijo na do štirih nešifriranih pakih, najdenih pod `steamapps\common\*\...\Content\Paks`. Preverijo, da je odmik vsakega vnosa znotraj datoteke, in da se SHA-1 ujema za naključni vzorec 150 vnosov na arhiv.
