---
title: "Unreal .pak"
nav_order: 1
lang: "is"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Listar og dregur út** Unreal 4.22-5.x `.pak` skjalasöfn: útgáfur 8, 9, 10, 11
og 12, Zlib, Gzip og Oodle þjöppun, og dulkóðuð skjalasöfn þegar þú gefur upp
AES lykilinn. Það túlkar ekki það sem það dregur út (`.uasset`, `.umap`).

Heimild: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Skipanir: `identify`, `list`, `extract` (sjá [Skipanir](commands.md)).

## Uppröðun {#layout}

Fóturinn er aftast í skránni og finnst með því að leita í síðustu 1.024
bætum að töfratölunni `0x5A6F12E1`. Röð reita hans skiptir máli:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Dulkóðunarfáninn situr **á undan** töfratölunni. Ef hann er tekinn frá eftir töfratöluna
lendir það á „Z“ í „Zlib“. Þá segir hvert skjalasafn sig dulkóðað og sérhvert
aðferðarheiti missir fyrsta stafinn („lib“, „odle“), hljóðlaus og trúverðug
bilun. Útgáfan er lægsta bætið, því „frozen index“ útgáfur setja háan
bita.

Vísirinn geymir tengipunktinn, slóðatætivísinn, fulla möppuvísinn,
og blokk af **kóðuðum færslum**: bitapakkað form þar sem flaggaorð segir
hvaða tölur eru 32 bita, þjöppunaraðferðina (6 bitar), hvort færslan er
dulkóðuð, blokkafjöldann (16 bitar) og blokkastærðina í einingum af 2.048
(6 bitar). Blokkastærðin með alla bita sem einn er undankomuleið: raunveruleg stærð fylgir sem u32
**á undan** hliðruninni. Í stóru skjalasafni færði lestur hennar á eftir stærðunum 7%
færslna um fjögur bæti og gaf þeim hliðranir í exabætum.

Full færsla hverrar skráar er endurtekin rétt á undan farmi hennar, svo farmurinn
byrjar eftir `8+8+8+20+4+1+4` bæti, auk `4 + 16 x blocks` þegar hann er þjappaður.
Dulkóðaðar blokkir eru fylltar í 16 bæti.

## Hvað það les, og hverju það hafnar {#what-it-reads-and-what-it-refuses}

| Tilvik | Niðurstaða |
|---|---|
| útgáfur 8-12 | lesið |
| hver önnur útgáfa | `pak version N; this reader handles 8-12` (eldri útgáfur geyma flatan færslulista, og engin skrá var til að prófa á móti) |
| engin töfratala í fæti | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| vísir utan skrárinnar | hafnað: fóturinn þáttaðist ekki eins og hann fullyrti |
| aðeins slóðatætivísir | hafnað: skráarnöfn voru tætt í burtu við smíði og er ekki hægt að endurheimta |
| færslur í yfirflæðislista vísisins (möppuhliðrun -1) | sleppt, ekki skálduð |
| dulkóðaður vísir, enginn lykill | `EncryptedPak`: „Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys.“ Á skipanalínu, ein lína og útgangskóði 1 |
| dulkóðuð færsla, enginn lykill | `EncryptedPak` við lestur |
| aðferðir Zlib, Gzip, Oodle | afþjappað (Oodle þarf safn, sjá [Oodle](reader-oodle.md)) |
| hver önnur aðferð | `compression method '...' is not supported` |

## Lyklar {#keys}

`--key` á `list` og `extract` tekur AES-256 lykil sem þú átt þegar, sem 64 sextándakerfis
tölustafi, með eða án `0x`. Allt annað er hafnað áður en skjalasafnið er
opnað, með útgangskóða 2. Afkóðun er AES-256-ECB í gegnum
`cryptography` pakkann. Engin kóðaleið er til sem útvegar lykil: enginn sendur
lykill, engin leit í keyrsluskrám, enginn minnislestur. Sjá
[Reglur og leyfi](rules-and-licences.md).

## Sannreynt {#verified}

Á móti sendum skjalasöfnum úr fleiri en einum leik passaði hver færsla, þar á meðal eitt
mjög stórt skjalasafn, við SHA-1 sem Unreal skrifar
á undan hverjum farmi. Það tætigildi nær yfir bætin eins og þau eru geymd, svo samsvörun þýðir að
afkóðun vísisins, hliðrun farmsins og hver mörk þjappaðra blokka voru
rétt. Prófin á uppsettum leikjum (`test_pak.py`) endurtaka þetta á allt að fjórum
ódulkóðuðum pak skrám sem finnast undir `steamapps\common\*\...\Content\Paks`. Þau athuga
að hliðrun hverrar færslu liggi innan skrárinnar, og að SHA-1 passi fyrir
handahófskennt úrtak 150 færslna í hverju skjalasafni.
