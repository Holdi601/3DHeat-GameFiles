---
title: "Përditësimet"
nav_order: 13
lang: "sq"
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Përditësimet {#updates}

3DHeat GameFiles kontrollon botimet GitHub të këtij depoje kur nis, të thotë
kur ka dalë një version më i ri dhe ofron ta përditësojë. Skedarët e tu (xhirot,
eksportet) nuk preken kurrë.

Burimi: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Versioni i instaluar është skedari
[`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) i depos.

## Kontrolli në nisje {#the-check-at-start-up}

Çdo ekzekutim `python -m heat3d_gamefiles ...` e thërret kontrollin para se të analizojë
argumentet:

- Pyet `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest`,
  me kufi kohe **5 sekonda**.
- Përgjigjja ruhet në cache për **6 orë** te
  `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` (ose
  `~/.cache/3DHeat/...` pa `LOCALAPPDATA`). Brenda kësaj kohe nuk bëhet asnjë kërkesë.
  "Ende pa botim" (HTTP 404) ruhet gjithashtu.
- Pa internet, me kufizim kërkesash ose pas një proxy, kontrolli thjesht kthehet dhe mjeti
  vazhdon me versionin që ka.
- Nëse etiketa e botimit të fundit (`v1.2.3` ose `1.2.3`; çdo gjë pas `-` ose `+`
  injorohet) është më e re se `VERSION`, printon në stderr:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **Në një terminal** (stdin dhe stderr janë të dy TTY) pyet `Update now? [Y/n]`.
  Enter, `y`, `yes`, `j` ose `ja` përditëson. Pas një përditësimi të suksesshëm, **e njëjta
  komandë niset përsëri** me kodin e ri, dhe kodi i daljes i kalohet më tej.
- **Pa terminal** (një ekzekutim i planifikuar, një pipe) vetëm printon
  ``Run `python -m heat3d_update` in <folder> to update.`` dhe vazhdon.

## Përditësimi me kërkesë {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Kjo pyet gjithmonë GitHub (pa cache). Printon `Up to date: 1.0.1.`,
`No release found (...)`, ose çfarë bëri. Kodi i daljes është 1 nëse përditësimi
nuk u zbatua.

## Si zbatohet një përditësim {#how-an-update-is-applied}

| Instaluar si | Përditësimi |
|---|---|
| një **klon git** (një dosje `.git` dhe `git` në PATH) | `git pull --ff-only`. **Refuzohet** sa kohë skedarët e ndjekur kanë ndryshime lokale: "this checkout has local changes; commit or stash them, then run `git pull`". Skedarët e pandjekur nuk e bllokojnë |
| një **kopje e shkarkuar** | arkivi burimor i botimit (`zipball_url`) shkarkohet dhe shpaketohet në një dosje të përkohshme, duke injoruar çdo rrugë që do të dilte jashtë saj; `VERSION` i tij duhet të jetë i barabartë me versionin e botimit, ose nuk kopjohet asgjë; pastaj skedarët e tij kopjohen mbi këtë dosje |

Kur kopjon nga një arkiv, skedarët që nuk janë pjesë e botimit (xhirot, eksportet,
mjediset virtuale, çdo gjë që ke bërë ti) lihen të paprekur. Përditësuesi
provon gjithashtu të fshijë modulet `.py` që një botim i ka hequr nga paketat e veta, që një
modul i vjetruar të mos e hijezojë zëvendësuesin e tij. Kërkon paketat `heat3d_*` te
rrënja e arkivit dhe një dosje më poshtë, dhe heq skedarët `.py` që botimi
nuk i ka më.

## Çaktivizimi {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Çdo vlerë tjetër nga bosh, `0`, `false` ose `no` çaktivizon si kontrollin në nisje
ashtu edhe ofertën. `python -m heat3d_update` funksionon prapë kur niset me dorë.
