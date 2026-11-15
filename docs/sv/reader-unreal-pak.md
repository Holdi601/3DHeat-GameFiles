---
title: Unreal .pak
nav_order: 1
lang: "sv"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Listar och extraherar** Unreal 4.22-5.x `.pak`-arkiv: version 8, 9, 10, 11 och 12,
Zlib-, Gzip- och Oodle-komprimering, och krypterade arkiv när du anger AES-nyckeln. Den
tolkar inte det den extraherar (`.uasset`, `.umap`).

Källkod: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Kommandon: `identify`, `list`, `extract` (se [Kommandon](commands.md)).

## Layout {#layout}

Footern finns i slutet av filen och hittas genom att söka de sista 1 024 byten efter
magin `0x5A6F12E1`. Dess fältordning spelar roll:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Krypteringsflaggan ligger **före** magin. Tar man den från efter magin landar man på
"Z" i "Zlib". Då anses varje arkiv krypterat, och varje metodnamn tappar sin första
bokstav ("lib", "odle"), ett tyst och trovärdigt fel. Versionen är den lägsta byten,
eftersom "frozen index"-byggen sätter en hög bit.

Indexet innehåller monteringspunkten, sökvägshash-indexet, det fullständiga katalogindexet
och ett block med **kodade poster**: en bitpackad form där ett flaggord anger vilka tal som
är 32-bitars, komprimeringsmetoden (6 bitar), om posten är krypterad, blockantalet
(16 bitar) och blockstorleken i enheter om 2 048 (6 bitar). Den helt ettställda
blockstorleken är en escape: den verkliga storleken följer som en u32 **före** offseten.
I ett stort arkiv flyttade läsning den efter storlekarna 7 % av posterna fyra byte, och
gav dem offset i exabyte-storlek.

Varje posts fullständiga post upprepas precis före dess nyttolast, så nyttolasten
börjar efter `8+8+8+20+4+1+4` byte, plus `4 + 16 x blocks` när den är komprimerad.
Krypterade block utfylls till 16 byte.

## Vad den läser, och vad den vägrar {#what-it-reads-and-what-it-refuses}

| Fall | Resultat |
|---|---|
| version 8-12 | läses |
| någon annan version | `pak version N; this reader handles 8-12` (äldre versioner lagrar en platt postlista, och det fanns ingen fil att testa mot) |
| ingen footer-magi | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index utanför filen | vägras: footern tolkades inte som den påstod |
| bara sökvägshash-index | vägras: filnamnen hashades bort vid bygget och kan inte återskapas |
| poster i indexets överflödeslista (katalogoffset -1) | hoppas över, inte förfalskas |
| krypterat index, ingen nyckel | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." På kommandoraden: en rad och avslutningskod 1 |
| krypterad post, ingen nyckel | `EncryptedPak` vid läsning |
| metoderna Zlib, Gzip, Oodle | packas upp (Oodle behöver ett bibliotek, se [Oodle](reader-oodle.md)) |
| annan metod | `compression method '...' is not supported` |

## Nycklar {#keys}

`--key` för `list` och `extract` tar en AES-256-nyckel som du redan har, som 64 hexadecimala
siffror, med eller utan `0x`. Allt annat vägras innan arkivet öppnas, med avslutningskod 2.
Dekrypteringen är AES-256-ECB via paketet `cryptography`. Det finns ingen kodväg som
skaffar en nyckel: inga medlevererade nycklar, ingen sökning i körbara filer, ingen
läsning av minne. Se [Regler och licenser](rules-and-licences.md).

## Verifierat {#verified}

Mot levererade arkiv från fler än ett spel matchade varje post, även i ett mycket stort
arkiv, mot den SHA-1 som Unreal skriver före varje nyttolast. Den hashen täcker byten
så som de är lagrade, så en träff betyder att indexavkodningen, nyttolastoffseten och
varje komprimerad blockgräns var rätt. Testerna mot installerade spel (`test_pak.py`)
upprepar detta på upp till fyra okrypterade pak-filer under `steamapps\common\*\...\Content\Paks`.
De kontrollerar att varje posts offset ligger inom filen, och att SHA-1 stämmer för ett
slumpmässigt urval på 150 poster per arkiv.
