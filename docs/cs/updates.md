---
title: "Aktualizace"
nav_order: 13
lang: "cs"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Aktualizace {#updates}

3DHeat GameFiles při startu zkontroluje vydání (releases) tohoto repozitáře na GitHubu, řekne, když je venku novější verze, a nabídne aktualizaci. Vaše vlastní soubory (kola, exporty) se nikdy nedotknou.

Zdroj: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Nainstalovaná verze je soubor [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) v repozitáři.

## Kontrola při startu {#the-check-at-start-up}

Každé spuštění `python -m heat3d_gamefiles ...` zavolá kontrolu, než zpracuje své argumenty:

- Ptá se na `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` s časovým limitem **5 sekund**.
- Odpověď se ukládá do mezipaměti na **6 hodin** v `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (nebo `~/.cache/3DHeat/...` bez `LOCALAPPDATA`). V té době se žádný požadavek neposílá. Odpověď „zatím žádné vydání“ (HTTP 404) se také ukládá do mezipaměti.
- Offline, při omezení počtu požadavků nebo za proxy kontrola jen skončí a nástroj běží ve verzi, kterou má.
- Pokud je značka nejnovějšího vydání (`v1.2.3` nebo `1.2.3`; cokoli za `-` nebo `+` se ignoruje) novější než `VERSION`, vypíše na stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **V terminálu** (stdin i stderr jsou TTY) se zeptá, zda aktualizovat (`Update now? [Y/n]`). Enter, `y`, `yes`, `j` nebo `ja` aktualizuje. Po úspěšné aktualizaci se **stejný příkaz spustí znovu** na novém kódu a jeho návratový kód se předá dál.
- **Bez terminálu** (naplánované spuštění, roura) jen vypíše zprávu ``Run `python -m heat3d_update` in <folder> to update.`` a pokračuje dál.

## Aktualizace na vyžádání {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Tohle se vždy ptá GitHubu (bez mezipaměti). Vypíše `Up to date: 1.0.1.`, `No release found (...)`, nebo co udělala. Návratový kód je 1, pokud aktualizaci nebylo možné použít.

## Jak se aktualizace provede {#how-an-update-is-applied}

| Nainstalováno jako | Aktualizace |
|---|---|
| **klon gitu** (složka `.git` a `git` v PATH) | `git pull --ff-only`. **Odmítnuto**, dokud mají sledované soubory lokální změny. Vypíše se: "this checkout has local changes; commit or stash them, then run `git pull`". Nesledované soubory aktualizaci neblokují |
| **stažená kopie** | zdrojový archiv vydání (`zipball_url`) se stáhne a rozbalí do dočasné složky, s ignorováním každé cesty, která by z ní unikla. Jeho `VERSION` se musí rovnat verzi vydání, jinak se nic nezkopíruje. Pak se jeho soubory zkopírují přes tuto složku |

Při kopírování z archivu zůstanou soubory, které nejsou součástí vydání (kola, exporty, virtuální prostředí, cokoli, co jste vytvořili). Aktualizátor se také pokusí smazat moduly `.py`, které vydání odstranilo ze svých balíčků, aby zastaralý modul nemohl zastínit svého nástupce. Hledá balíčky `heat3d_*` v kořeni archivu a o úroveň níž a odstraní soubory `.py`, které vydání už nemá.

## Vypnutí {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Jakákoli hodnota jiná než prázdná, `0`, `false` nebo `no` vypne jak kontrolu při startu, tak nabídku. `python -m heat3d_update` funguje dál, když ho spustíte ručně.
