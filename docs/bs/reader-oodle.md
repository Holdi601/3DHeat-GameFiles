---
title: "Oodle"
nav_order: 3
lang: "bs"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: pronađen, ne uključen {#oodle-found-not-bundled}

Najveći dio isporučenog Unreal sadržaja, i neki Frostbite podaci, kompresirani su pomoću
**Oodle** (RAD Game Tools, sada Epic). Oodle je vlasnički. Nema
build koji se smije redistribuirati niti implementacije u Pythonu, a `oo2core_*.dll` je
licenciran proizvodu koji ga isporučuje. Zato ovaj alat **pronalazi kopiju koja je već na vašem
računaru i učitava je**. Nikad ne nosi vlastitu. FModel i UModel rade na isti
način.

Izvor: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Gdje traži {#where-it-looks}

Prva datoteka koja postoji pobjeđuje, ovim redoslijedom:

1. Izričita putanja koju proslijedi pozivalac (Python API).
2. `HEAT3D_OODLE`: putanja do DLL-a, ili folder koji ga sadrži.
3. Plitka pretraga, dubine jedan nivo, u
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` svake Steam biblioteke

   Za svaki podfolder `<game>` provjerava `<game>`,
   `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` i
   `<game>\Engine\Binaries\Win64`.

Imena datoteka koja se probaju, najnovije prvo: `oo2core_9_win64.dll` pa sve do
`oo2core_3_win64.dll`. Format je unazad kompatibilan, pa starija biblioteka
obično i dalje radi.

Pretraga namjerno **nije** rekurzivno skeniranje svakog diska, što bi
trajalo minutama. Ako ništa ne nađe, postavite `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Folder radi jednako dobro kao i sama datoteka: imena DLL-ova gore probaju se unutar njega.

Instalacija Unreal Enginea nosi jednu u `Engine\Binaries\ThirdParty\Oodle`,
što je najuredniji izvor za programera. Mnoge igre isporučuju jednu pored svoje
izvršne datoteke. Igre na Unrealu 5 često povezuju Oodle statički i ne isporučuju DLL, pa
pronađena kopija može pripadati drugoj igri nego arhiva koja se čita. Format
je u oba slučaja isti.

## Kako se poziva {#how-it-is-called}

`OodleLZ_Decompress` poziva se preko `ctypes` s očekivanom dužinom izlaza
(indeks arhive je uvijek zna, a Oodle je ne može zaključiti), uz dekodiranje
sigurno od fuzzinga (ulaz nije pouzdan), bez provjere CRC-a (vlastiti SHA-1 paka
već pokriva bajtove) i bez niti. Rezultat pogrešne dužine je greška.
Biblioteka se učitava jednom po pokretanju.

## Kad je nema {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Unos koji se ne može dekompresirati je greška, nikad uvjerljivo smeće.

Učitavač radi samo na Windowsu (traži `*_win64.dll`). Biblioteke za Linux i macOS
se ne traže.
