---
title: "Oodle: nalezeno, nikoli přibaleno"
nav_order: 3
lang: "cs"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: nalezeno, nikoli přibaleno {#oodle-found-not-bundled}

Většina dodaného obsahu Unreal a některá data Frostbite jsou komprimována pomocí **Oodle** (RAD Game Tools, nyní Epic). Oodle je proprietární. Neexistuje žádná volně šiřitelná verze ani implementace v Pythonu, a `oo2core_*.dll` je licencovaná s produktem, který ji dodává. Tento nástroj proto **najde kopii, která už je na vašem počítači, a načte ji**. Nikdy žádnou nepřibaluje. FModel a UModel fungují stejně.

Zdroj: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Kde hledá {#where-it-looks}

Vyhrává první soubor, který existuje, v tomto pořadí:

1. Výslovná cesta předaná volajícím (Python API).
2. `HEAT3D_OODLE`: cesta k DLL nebo ke složce, která ji obsahuje.
3. Mělké hledání, jen o jednu úroveň hluboko, v
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` každé knihovny Steamu

   Pro každou podsložku `<game>` zkontroluje `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` a `<game>\Engine\Binaries\Win64`.

Názvy souborů, které zkouší, od nejnovějšího: `oo2core_9_win64.dll` až `oo2core_3_win64.dll`. Formát je zpětně kompatibilní, takže starší knihovna obvykle také funguje.

Hledání záměrně **není** rekurzivní prohledání všech disků, které by trvalo minuty. Pokud nic nenajde, nastavte `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Složka funguje stejně jako samotný soubor: názvy DLL výše se v ní zkoušejí.

Instalace Unreal Engine ji obsahuje v `Engine\Binaries\ThirdParty\Oodle`, což je pro vývojáře nejčistší zdroj. Mnoho her ji má vedle spustitelného souboru. Hry Unreal 5 často propojují Oodle staticky a DLL nedodávají, takže nalezená kopie může patřit jiné hře, než je čtený archiv. Formát je v každém případě stejný.

## Jak se volá {#how-it-is-called}

`OodleLZ_Decompress` se volá přes `ctypes` s očekávanou délkou výstupu (index archivu ji vždy zná a Oodle ji nedokáže odvodit). Dekódování běží v režimu odolném proti chybám (vstup je nedůvěryhodný), bez kontroly CRC (SHA-1 samotného pak už bajty kryje) a bez vláken. Výsledek se špatnou délkou je chyba. Knihovna se načte jednou za běh.

## Když žádná není {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Položka, kterou nelze dekomprimovat, je chyba, nikdy ne věrohodný nesmysl.

Načítač funguje jen na Windows (hledá `*_win64.dll`). Knihovny pro Linux a macOS se nehledají.
