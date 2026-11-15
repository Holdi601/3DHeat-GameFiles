---
title: "Oodle"
nav_order: 3
lang: "hr"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: pronađen, ne isporučuje se {#oodle-found-not-bundled}

Većina isporučenog Unreal sadržaja i neki Frostbite tereti komprimirani su **Oodleom** (RAD Game Tools, sada Epic). Oodle je vlasnički. Nema preraspodjeljive verzije ni Python implementacije, a `oo2core_*.dll` licenciran je proizvodu koji ga isporučuje. Zato ovaj alat **pronalazi primjerak koji je već na vašem računalu i učitava ga**. Nikad ga ne nosi sa sobom. FModel i UModel rade na isti način.

Izvor: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Gdje traži {#where-it-looks}

Prva datoteka koja postoji pobjeđuje, tim redom:

1. Izričita putanja koju preda pozivatelj (Python API).
2. `HEAT3D_OODLE`: putanja do DLL-a ili mape koja ga sadrži.
3. Plitko pretraživanje, jedna razina duboko, u:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` svake Steam biblioteke

   Za svaku podmapu `<game>` provjerava `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` i `<game>\Engine\Binaries\Win64`.

Imena datoteka koja se pokušavaju, od najnovijeg: `oo2core_9_win64.dll` do `oo2core_3_win64.dll`. Format je unatrag kompatibilan, pa starija biblioteka obično i dalje radi.

Pretraga namjerno **nije** rekurzivno skeniranje svakog diska, jer bi trajalo minutama. Ako ništa ne nađe, postavite `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Mapa radi jednako dobro kao i sama datoteka: unutra se pokušavaju imena DLL-ova navedena iznad.

Instalacija Unreal Enginea ima Oodle pod `Engine\Binaries\ThirdParty\Oodle`, što je za programera najuredniji izvor. Mnoge igre isporučuju ga pored svoje izvršne datoteke. Unreal 5 igre često povezuju Oodle statički i ne isporučuju DLL, pa pronađeni primjerak može pripadati drugoj igri od one čija se arhiva čita. Format je u oba slučaja isti.

## Kako se poziva {#how-it-is-called}

`OodleLZ_Decompress` poziva se preko `ctypes` s očekivanom duljinom izlaza (indeks arhive uvijek je zna, a Oodle je ne može zaključiti), s uključenim dekodiranjem otpornim na fuzzing (ulaz nije pouzdan), bez CRC provjere (vlastiti SHA-1 paka već pokriva bajtove) i bez niti. Rezultat pogrešne duljine je greška. Biblioteka se učitava jednom po pokretanju.

## Kad nema nijedne {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Unos koji se ne može dekomprimirati je greška, nikad uvjerljivo smeće.

Čitač radi samo na Windowsu (traži `*_win64.dll`). Linux i macOS biblioteke se ne traže.
