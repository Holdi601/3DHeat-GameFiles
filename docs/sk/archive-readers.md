---
title: Čítačky archívov
nav_order: 9
lang: "sk"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Čítačky archívov {#archive-readers}

**Kontajner** (alebo archív) je jeden veľký súbor, do ktorého hra zabalí mnoho
súborov. **CRC** alebo hash je krátky odtlačok niekoľkých bajtov: ak sedí, bajty
sa prečítali správne. **Ohraničujúci box** je najmenší kváder okolo modelu.

Pod príkazmi sú čítačky kontajnerov, ktoré hry používajú. Ich formáty nie sú
zdokumentované, okrem VPK od Valve a `.cdae` od BeamNG, preto „podporované“ musí
znamenať **overené na skutočných súboroch**, nie „nespadlo to“. Každá čítačka sa
overuje voči niečomu, čo formát zaručuje: hashu, CRC, reťazu offsetov, ktorý musí
vyjsť, alebo uloženému ohraničujúcemu boxu. Ak kontrola zlyhá, čítačka odmietne
s hlásením a nehádže. Zlá sieť vyzerá ako dobrá, kým ju nepoložíte vedľa trate.

| Čítačka | Modul | Číta | Nečíta | Volá sa z |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | verzie 8-12: index, položky, bloky Zlib/Gzip/Oodle, AES s kľúčom, ktorý zadáte | verzie pred 8, indexy len s hashmi ciest, preplnené položky, obsah assetov | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5 a novšie, overené na v8), zen balíky, neverzované vlastnosti pre niekoľko tried komponentov, uložené statické siete, textúry, streamované virtuálne textúry | šifrované kontajnery, verzované balíky, siete len pre Nanite, vlastnosti iných tried | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | bloky Oodle cez knižnicu, ktorá je už v počítači | nič bez takej knižnice; nikdy sa nedodáva | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` formát 22 a novší (Unity 2020 až 6000), zväzky `UnityFS`, nekomprimované siete vrátane `.resS` | formáty pred rokom 2020, vložené stromy typov, komprimované siete, akákoľvek trieda okrem `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | stromy `.toc` DbObject a binárne tabuľky sekcií, inštalačné balíky, umiestnenia chunkov, vložené zväzky a ich manifesty, oddiely RIFF EBX, siete MeshSet, výškové pole terénu, textúry BC1/BC3/BC7 a ich bloky shaderov, umiestnenie skupín statických modelov | tabuľky zakryté XOR, farbu pri zemi a diery v teréne, normálové mapy, alfa iná ako výrezy | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | verzie 1 a 2, rozdelené archívy, predbežne načítané dáta, kontrola CRC | skompilované assety (`.vmdl_c`, `.vtex_c`), formát navigačnej siete CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, uložené), geometria `.modelbin`, vzorníky `.pb` (BC1, BC7, RGBA), umiestnenia `.pgeo`, hashe textúr materiálov | iné formáty vrcholov a indexov, iné formáty textúr, vrstvy materiálu shaderu terénu | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` a `extract` (`.minizip`) |
| [Súbory BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | pripojený súborový systém zip, scénový JSON a TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiály | skinované a dekálové siete, animované sekvencie, procedurálny porast terénu | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` a `extract` (zip) |

## Pravidlá, ktorými sa riadi každá čítačka {#rules-every-reader-follows}

- **Žiadne kľúče v balíku, žiadne sa nezískavajú.** Šifrovaný archív Unreal `.pak`
  sa otvorí len s kľúčom, ktorý zadáte (`--key`). Šifrovaný kontajner IoStore sa
  odmietne. Nič nehľadá kľúč v spustiteľnom súbore a nič nečíta pamäť iného procesu.
  Pozri [Pravidlá a licencie](rules-and-licences.md).
- **Žiadny patentovaný kód v balíku.** Oodle sa načíta z hry alebo enginu, ktoré sú
  už nainštalované v počítači.
- **Odmietnuť namiesto hádania.** Neznáma verzia, kodek, formát vrcholov alebo
  formát textúry vyvolá konkrétnu chybu, napríklad
  `texture format 42 has not been identified; refusing to guess`.
- **Len na čítanie.** Žiadna čítačka nezapisuje do priečinka hry. Exporty idú
  tam, kam určíte.

## Čo znamená „overené“ {#what-verified-meant}

Čísla overenia uvedené na týchto stránkach pochádzajú z dokumentačných reťazcov
modulov. Namerali sa na nainštalovaných hrách počas písania každej čítačky.
Syntetické testy (pozri [Vývoj](development.md)) pevne určujú rozloženie polí.
Testy na nainštalovaných hrách zopakujú niektoré kontroly, keď je hra v počítači,
inak sa preskočia. Čísla, ktoré test nepokrýva, sa odvtedy znovu neoverovali.
