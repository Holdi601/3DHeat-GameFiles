---
title: "Oodle"
nav_order: 3
lang: "sq"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: gjendet, nuk përfshihet {#oodle-found-not-bundled}

Pjesa më e madhe e përmbajtjes së dërguar të Unreal, dhe disa ngarkesa të Frostbite, janë të ngjeshura me
**Oodle** (RAD Game Tools, tani Epic). Oodle është pronësor. Nuk ka version
që mund të shpërndahet dhe nuk ka zbatim në Python, dhe `oo2core_*.dll` është
e licencuar për produktin që e dërgon. Prandaj ky mjet **gjen një kopje që e ke tashmë në
kompjuter dhe e ngarkon**. Nuk e mban kurrë vetë. FModel dhe UModel punojnë
njësoj.

Burimi: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Ku kërkon {#where-it-looks}

Fiton skedari i parë që ekziston, sipas kësaj radhe:

1. Një rrugë e dhënë qartë nga thirrësi (API i Python).
2. `HEAT3D_OODLE`: një rrugë për DLL-në, ose një dosje që e mban.
3. Një kërkim i cekët, një nivel në thellësi, te
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` i çdo biblioteke Steam

   Për çdo dosje fëmijë `<game>`, kontrollon `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` dhe
   `<game>\Engine\Binaries\Win64`.

Emrat e skedarëve që provon, nga më i riu: `oo2core_9_win64.dll` e deri te
`oo2core_3_win64.dll`. Formati është i pajtueshëm prapa, kështu që një bibliotekë më e vjetër
zakonisht funksionon prapë.

Kërkimi me qëllim **nuk** është një skanim rekursiv i çdo disku, që do të
zgjaste minuta. Nëse nuk gjen asgjë, vendos `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Një dosje funksionon po aq mirë sa vetë skedari: emrat e DLL-ve më sipër provohen brenda saj.

Një instalim i Unreal Engine mban një nën `Engine\Binaries\ThirdParty\Oodle`,
që është burimi më i rregullt për një zhvillues. Shumë lojëra e dërgojnë një pranë
skedarit të tyre ekzekutues. Lojërat Unreal 5 shpesh e lidhin Oodle statikisht dhe nuk dërgojnë DLL,
kështu që kopja e gjetur mund t'i përkasë një loje tjetër nga arkivi që po lexohet. Formati
është i njëjtë në të dyja rastet.

## Si thirret {#how-it-is-called}

`OodleLZ_Decompress` thirret përmes `ctypes` me gjatësinë e pritur të daljes
(indeksi i arkivit e di gjithmonë, dhe Oodle nuk mund ta nxjerrë vetë), dekodim
i sigurt ndaj fuzz i ndezur (hyrja nuk është e besueshme), pa kontroll CRC (SHA-1 i vetë pak-ut
i mbulon tashmë bajtet), dhe pa fije. Një rezultat me gjatësi të gabuar është gabim. Biblioteka
ngarkohet një herë për çdo ekzekutim.

## Kur nuk ka asnjë {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Një hyrje që nuk mund të dekompresohet është gabim, kurrë mbeturinë që duket e besueshme.

Ngarkuesi punon vetëm në Windows (kërkon `*_win64.dll`). Bibliotekat për Linux dhe macOS
nuk kërkohen.
