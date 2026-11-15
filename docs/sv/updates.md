---
title: Uppdateringar
nav_order: 13
lang: "sv"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Uppdateringar {#updates}

3DHeat GameFiles kontrollerar det här förrådets GitHub-releaser när det startar, säger till när en nyare version finns och erbjuder en uppdatering. Dina egna filer (varv, exporter) rörs aldrig.

Källa: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Den installerade versionen är förrådets fil [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION).

## Kontrollen vid start {#the-check-at-start-up}

Varje körning av `python -m heat3d_gamefiles ...` anropar kontrollen innan den tolkar sina argument:

- Den frågar `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, med en timeout på **5 sekunder**.
- Svaret cachas i **6 timmar** i `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (eller `~/.cache/3DHeat/...` om `LOCALAPPDATA` saknas). Under den tiden görs ingen förfrågan. "No release yet" (HTTP 404) cachas också.
- Offline, begränsad av en gräns för anrop eller bakom en proxy, returnerar kontrollen helt enkelt och verktyget körs på den version det har.
- Om den senaste releasens tagg (`v1.2.3` eller `1.2.3`; allt efter `-` eller `+` ignoreras) är nyare än `VERSION` skrivs följande ut till stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **I en terminal** (stdin och stderr är båda en TTY) frågar den `Update now? [Y/n]`. Enter, `y`, `yes`, `j` eller `ja` uppdaterar. Efter en lyckad uppdatering startas **samma kommando om** med den nya koden, och dess slutkod skickas vidare.
- **Utan terminal** (en schemalagd körning, en pipe) skriver den bara ut ``Run `python -m heat3d_update` in <folder> to update.`` och fortsätter.

## Uppdatera på begäran {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Den frågar alltid GitHub (ingen cache). Den skriver ut `Up to date: 1.0.1.`, `No release found (...)` eller vad den gjorde. Slutkoden är 1 om uppdateringen inte kunde genomföras.

## Så tillämpas en uppdatering {#how-an-update-is-applied}

| Installerad som | Uppdatering |
|---|---|
| en **git-klon** (en `.git`-mapp och `git` i PATH) | `git pull --ff-only`. **Avvisas** så länge spårade filer har lokala ändringar: "this checkout has local changes; commit or stash them, then run `git pull`". Ospårade filer hindrar den inte |
| en **nedladdad kopia** | releasens källarkiv (`zipball_url`) laddas ner och packas upp i en tillfällig mapp, och sökvägar som skulle ta sig utanför den ignoreras; dess `VERSION` måste vara lika med releasens version, annars kopieras ingenting; sedan kopieras dess filer över den här mappen |

När något kopieras från ett arkiv lämnas filer som inte ingår i releasen (varv, exporter, virtuella miljöer, allt du har skapat) orörda. Uppdateraren försöker också ta bort `.py`-moduler som en release har tagit bort ur sina paket, så att en gammal modul inte kan skymma sin ersättning. Den letar efter `heat3d_*`-paket i arkivets rot och en mapp nedanför, och tar bort `.py`-filer som releasen inte längre har.

## Stäng av den {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Varje värde utom tomt, `0`, `false` eller `no` stänger av både kontrollen vid start och erbjudandet. `python -m heat3d_update` fungerar fortfarande när den körs för hand.
