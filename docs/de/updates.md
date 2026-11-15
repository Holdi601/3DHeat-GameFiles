---
title: Updates
nav_order: 13
lang: de
source: updates.md
source_hash: "9a8e1e51df4b"
nav_exclude: true
search_exclude: true
---
# Updates {#updates}

3DHeat GameFiles prüft beim Start die GitHub-Releases dieses Repositorys, sagt dir, wenn eine neuere Version da ist, und bietet an zu aktualisieren. Deine eigenen Dateien (Runden, Exporte) werden nie angerührt.

Quelle: [`heat3d_update/__init__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__init__.py),
[`heat3d_update/__main__.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_update/__main__.py).
Die installierte Version ist die Datei [`VERSION`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/VERSION) des Repositorys.

## Die Prüfung beim Start {#the-check-at-start-up}

Jeder Lauf von `python -m heat3d_gamefiles ...` ruft die Prüfung auf, bevor er seine Argumente auswertet:

- Sie fragt `https://api.github.com/repos/Holdi601/3DHeat-GameFiles/releases/latest` ab, mit einem Timeout von **5 Sekunden**.
- Die Antwort wird **6 Stunden** lang in `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-GameFiles.json` zwischengespeichert (oder `~/.cache/3DHeat/...`, wenn `LOCALAPPDATA` fehlt). In dieser Zeit wird keine Anfrage gestellt. „Noch kein Release“ (HTTP 404) wird ebenfalls zwischengespeichert.
- Offline, bei einem Ratenlimit oder hinter einem Proxy kehrt die Prüfung einfach zurück, und das Werkzeug läuft mit der Version, die es hat.
- Wenn der Tag des neuesten Releases (`v1.2.3` oder `1.2.3`; alles nach `-` oder `+` wird ignoriert) neuer ist als `VERSION`, gibt es auf stderr aus:

  ```
  [heat3d_gamefiles] 3DHeat GameFiles 1.1.0 is out (this is 1.0.1). https://github.com/...
  ```

- **In einem Terminal** (stdin und stderr sind beide ein TTY) fragt es `Update now? [Y/n]`. Enter, `y`, `yes`, `j` oder `ja` aktualisieren. Nach einem erfolgreichen Update wird **derselbe Befehl erneut** mit dem neuen Code gestartet, und sein Exit-Code wird weitergegeben.
- **Ohne Terminal** (ein geplanter Lauf, eine Pipe) gibt es nur aus ``Run `python -m heat3d_update` in <folder> to update.`` und macht weiter.

## Auf Wunsch aktualisieren {#updating-on-request}

```
python -m heat3d_update          # update to the newest release, if there is one
python -m heat3d_update --check  # only say whether a newer release is out
```

Das fragt immer bei GitHub nach (ohne Zwischenspeicher). Es gibt `Up to date: 1.0.1.`, `No release found (...)` oder aus, was es getan hat. Der Exit-Code ist 1, wenn das Update nicht angewendet werden konnte.

## Wie ein Update angewendet wird {#how-an-update-is-applied}

| Installiert als | Update |
|---|---|
| ein **Git-Klon** (ein `.git`-Ordner und `git` im PATH) | `git pull --ff-only`. **Abgelehnt**, solange versionierte Dateien lokale Änderungen haben: „this checkout has local changes; commit or stash them, then run `git pull`“. Nicht versionierte Dateien blockieren es nicht |
| eine **heruntergeladene Kopie** | das Quellarchiv des Releases (`zipball_url`) wird heruntergeladen und in einen temporären Ordner entpackt, wobei jeder Pfad ignoriert wird, der herausführen würde; seine `VERSION` muss der Version des Releases entsprechen, sonst wird nichts kopiert; dann werden seine Dateien über diesen Ordner kopiert |

Beim Kopieren aus einem Archiv bleiben Dateien, die nicht Teil des Releases sind (Runden, Exporte, virtuelle Umgebungen, alles, was du selbst erstellt hast), unberührt. Das Update versucht außerdem, `.py`-Module zu löschen, die ein Release aus seinen Paketen entfernt hat, damit ein veraltetes Modul seinen Nachfolger nicht verdeckt. Es sucht nach `heat3d_*`-Paketen an der Wurzel des Archivs und eine Ebene darunter und entfernt `.py`-Dateien, die das Release nicht mehr hat.

## Abschalten {#switching-it-off}

```
set HEAT3D_NO_UPDATE=1
```

Jeder andere Wert als leer, `0`, `false` oder `no` schaltet sowohl die Prüfung beim Start als auch das Angebot ab. `python -m heat3d_update` funktioniert weiterhin, wenn man es von Hand startet.
