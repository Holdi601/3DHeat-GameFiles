---
title: "Oodle: najdeno, ne priloženo"
nav_order: 3
lang: "sl"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: najdeno, ne priloženo {#oodle-found-not-bundled}

Večina objavljene vsebine Unreal in nekateri tovori Frostbite so stisnjeni z **Oodle** (RAD Game Tools, zdaj Epic). Oodle je lastniški. Ni distribucijske različice in ni implementacije v Pythonu, `oo2core_*.dll` pa je licenciran izdelku, ki ga objavlja. Zato to orodje **najde kopijo, ki je že na vašem računalniku, in jo naloži**. Nikoli je ne prinaša s seboj. FModel in UModel delata enako.

Vir: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Kje išče {#where-it-looks}

Uporabi se prva datoteka, ki obstaja, v tem vrstnem redu:

1. Izrecna pot, ki jo poda klicatelj (Python API).
2. `HEAT3D_OODLE`: pot do DLL ali do mape, ki jo vsebuje.
3. Plitvo iskanje, eno raven globoko, v:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` vsake knjižnice Steam

   Za vsako podmapo `<game>` preveri `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` in `<game>\Engine\Binaries\Win64`.

Imena datotek, ki se preizkusijo, od najnovejšega: `oo2core_9_win64.dll` do `oo2core_3_win64.dll`. Oblika je povratno združljiva, zato starejša knjižnica običajno še vedno deluje.

Iskanje namenoma **ni** rekurzivno preiskovanje vseh diskov, ki bi trajalo minute. Če ne najde ničesar, nastavite `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Mapa deluje prav tako kot sama datoteka: imena DLL zgoraj se preizkusijo znotraj nje.

Namestitev Unreal Engine ima knjižnico v `Engine\Binaries\ThirdParty\Oodle`, kar je za razvijalca najbolj urejen vir. Mnoge igre imajo eno poleg svoje izvršljive datoteke. Igre Unreal 5 pogosto povežejo Oodle statično in ne priložijo nobenega DLL, zato lahko najdena kopija pripada drugi igri kot arhiv, ki se bere. Oblika je v obeh primerih enaka.

## Kako se kliče {#how-it-is-called}

`OodleLZ_Decompress` se kliče prek `ctypes` s pričakovano dolžino izhoda (indeks arhiva jo vedno pozna, Oodle je ne more uganiti), z vklopljenim dekodiranjem, odpornim na nepravilne vhode (vhod ni zaupanja vreden), brez preverjanja CRC (SHA-1 same datoteke pak že pokriva bajte) in brez niti. Rezultat napačne dolžine je napaka. Knjižnica se naloži enkrat na zagon.

## Kadar je ni {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Vnos, ki ga ni mogoče razpakirati, je napaka, nikoli verjetna smet.

Nalagalnik deluje samo v Windows (išče `*_win64.dll`). Knjižnic za Linux in macOS ne išče.
