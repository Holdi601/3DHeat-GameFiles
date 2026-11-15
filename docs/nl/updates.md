---
title: Bijwerken
nav_order: 13
lang: "nl"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Bijwerken {#updates}

3DHeat GameFiles controleert bij het opstarten de GitHub-releases van deze repository, zegt wanneer er een nieuwere versie is, en biedt aan bij te werken. Je eigen bestanden (ronden, exports) worden nooit aangeraakt.

Bron: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
De geïnstalleerde versie is het bestand
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) van de repository.

## De controle bij het opstarten {#the-check-at-start-up}

Elke run van `python -m heat3d_gamefiles ...` roept de controle aan voordat hij zijn argumenten leest:

- Hij vraagt `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`, met een time-out van **5 seconden**.
- Het antwoord wordt **6 uur** bewaard in `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (of `~/.cache/3DHeat/...` zonder `LOCALAPPDATA`). Binnen die tijd wordt geen verzoek gedaan. "Nog geen release" (HTTP 404) wordt ook bewaard.
- Offline, bij een limiet op het aantal verzoeken, of achter een proxy, keert de controle gewoon terug en draait het hulpmiddel op de versie die het heeft.
- Als de tag van de laatste release (`v1.2.3` of `1.2.3`; alles na `-` of `+` wordt genegeerd) nieuwer is dan `VERSION`, drukt het op stderr af:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **In een terminal** (stdin en stderr zijn allebei een TTY) vraagt het `Update now? [Y/n]`. Enter, `y`, `yes`, `j` of `ja` werkt bij. Na een geslaagde update wordt **hetzelfde commando opnieuw gestart** op de nieuwe code, en zijn exitcode wordt doorgegeven.
- **Zonder terminal** (een geplande run, een pipe) drukt het alleen af: ``Run `python -m heat3d_update` in <folder> to update.``, en gaat het verder.

## Op verzoek bijwerken {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Dit vraagt altijd GitHub (zonder bewaarde gegevens). Het drukt `Up to date: 1.0.1.`, `No release found (...)`, of wat het heeft gedaan, af. De exitcode is 1 als de update niet kon worden toegepast.

## Hoe een update wordt toegepast {#how-an-update-is-applied}

| Geïnstalleerd als | Update |
|---|---|
| een **git-kloon** (een `.git`-map en `git` op het PATH) | `git pull --ff-only`. **Geweigerd** zolang gevolgde bestanden lokale wijzigingen hebben: "this checkout has local changes; commit or stash them, then run `git pull`". Niet-gevolgde bestanden blokkeren het niet |
| een **gedownloade kopie** | het bronarchief van de release (`zipball_url`) wordt gedownload en in een tijdelijke map uitgepakt, waarbij elk pad dat buiten de map zou vallen wordt genegeerd. Zijn `VERSION` moet gelijk zijn aan de versie van de release, anders wordt er niets gekopieerd. Daarna worden de bestanden over deze map gekopieerd |

Bij het kopiëren uit een archief blijven bestanden die geen deel van de release zijn (ronden, exports, virtuele omgevingen, alles wat je zelf maakte) met rust. De updater probeert ook `.py`-modules te verwijderen die een release uit zijn pakketten heeft gehaald, zodat een verouderde module de vervanging niet kan verbergen. Hij zoekt naar `heat3d_*`-pakketten in de hoofdmap van het archief en één map dieper, en verwijdert de `.py`-bestanden die de release niet meer heeft.

## Uitzetten {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Elke waarde behalve leeg, `0`, `false` of `no` zet zowel de controle bij het opstarten als het aanbod uit. `python -m heat3d_update` werkt nog steeds wanneer je het met de hand uitvoert.
