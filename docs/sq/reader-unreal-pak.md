---
title: "Unreal .pak"
nav_order: 1
lang: "sq"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Liston dhe nxjerr** arkivat Unreal 4.22-5.x `.pak`: versionet 8, 9, 10, 11
dhe 12, kompresimin Zlib, Gzip dhe Oodle, dhe arkivat e enkriptuara kur jep
çelësin AES. Nuk interpreton çfarë nxjerr (`.uasset`, `.umap`).

Burimi: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Komandat: `identify`, `list`, `extract` (shih [Komandat](commands.md)).

## Struktura {#layout}

Fundi është në fund të skedarit dhe gjendet duke kërkuar në 1,024 bajtet e fundit
për magjinë `0x5A6F12E1`. Rendi i fushave të tij ka rëndësi:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Flamuri i enkriptimit qëndron **para** magjisë. Nëse merret nga pas magjisë,
bie mbi "Z" të "Zlib". Atëherë çdo arkiv raporton veten të enkriptuar dhe çdo
emër metode e humb shkronjën e parë ("lib", "odle"), një dështim i heshtur
dhe i besueshëm. Versioni është bajti i ulët, sepse ndërtimet "frozen index" vënë një
bit të lartë.

Indeksi mban pikën e montimit, indeksin e hash-eve të shtigjeve, indeksin e plotë të direktorive,
dhe një bllok **hyrjesh të koduara**: një formë e paketuar në bite ku një fjalë flamujsh thotë
cilët numra janë 32-bit, metodën e kompresimit (6 bite), nëse hyrja është
e enkriptuar, numrin e blloqeve (16 bite) dhe madhësinë e bllokut në njësi prej 2,048
(6 bite). Madhësia e bllokut me të gjitha njëshet është një ikje: madhësia e vërtetë pason si u32
**para** ofsetit. Në një arkiv të madh, leximi pas madhësive i zhvendosi 7%
të hyrjeve me katër bajte dhe u dha ofsete në eksabajte.

Regjistri i plotë i çdo hyrjeje përsëritet para ngarkesës së saj, prandaj ngarkesa
fillon pas `8+8+8+20+4+1+4` bajtesh, plus `4 + 16 x blocks` kur është e kompresuar.
Blloqet e enkriptuara mbushen në 16 bajte.

## Çfarë lexon, dhe çfarë refuzon {#what-it-reads-and-what-it-refuses}

| Rasti | Rezultati |
|---|---|
| versionet 8-12 | lexohen |
| çdo version tjetër | `pak version N; this reader handles 8-12` (versionet më të vjetra ruajnë një listë regjistrash të sheshtë, dhe nuk kishte skedar për ta testuar) |
| pa magji fundi | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeks jashtë skedarit | refuzohet: fundi nuk u parsua siç pretendonte |
| vetëm indeks hash-esh shtigjesh | refuzohet: emrat e skedarëve u hashuan gjatë ndërtimit dhe nuk rikuperohen |
| hyrje në listën e tejmbushjes të indeksit (ofseti i direktorisë -1) | anashkalohen, nuk shpiken |
| indeks i enkriptuar, pa çelës | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Në rreshtin e komandave, një rresht dhe kodi i daljes 1 |
| hyrje e enkriptuar, pa çelës | `EncryptedPak` gjatë leximit |
| metodat Zlib, Gzip, Oodle | dekompresohen (Oodle ka nevojë për një bibliotekë, shih [Oodle](reader-oodle.md)) |
| çdo metodë tjetër | `compression method '...' is not supported` |

## Çelësat {#keys}

`--key` në `list` dhe `extract` merr një çelës AES-256 që e ke tashmë, si 64 shifra
heksadecimale, me ose pa `0x`. Çdo gjë tjetër refuzohet para se të hapet arkivi,
me kodin e daljes 2. Dekriptimi është AES-256-ECB përmes paketës
`cryptography`. Nuk ka asnjë shteg kodi që merr një çelës: pa çelësa të përfshirë,
pa kërkim në ekzekutues, pa lexim memorieje. Shih
[Rregullat dhe licencat](rules-and-licences.md).

## Verifikuar {#verified}

Kundrejt arkivave të dërguar të më shumë se një loje, çdo hyrje, përfshirë një arkiv
shumë të madh, përputhej me SHA-1 që Unreal e shkruan
para çdo ngarkese. Ai hash mbulon bajtet siç janë ruajtur, prandaj një përputhje do të thotë
që dekodimi i indeksit, ofseti i ngarkesës dhe çdo kufi bllokut të kompresuar ishin
të saktë. Testet me lojë të instaluar (`test_pak.py`) e përsërisin këtë në deri në katër
pak të paenkriptuar të gjetur nën `steamapps\common\*\...\Content\Paks`. Kontrollojnë
që ofseti i çdo hyrjeje qëndron brenda skedarit, dhe që SHA-1 përputhet për një
mostër të rastësishme prej 150 hyrjesh për arkiv.
