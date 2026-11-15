---
title: "Bevor du anfängst"
nav_order: 2
lang: de
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Bevor du anfängst {#before-you-start}

Neu in der Kommandozeile? Diese Seite bringt dich von null zu einem funktionierenden Werkzeug, in etwa
zehn Minuten. Du tippst Befehle in ein Fenster namens **Terminal**, und das Werkzeug antwortet mit Text.

## 1. Python installieren {#install-python}

1. Geh zu [python.org/downloads](https://www.python.org/downloads/) und lade
   **Python 3.10 oder neuer** herunter.
2. Starte das Installationsprogramm. Setze auf dem ersten Bildschirm den Haken bei **"Add python.exe to PATH"**,
   dann klicke auf **Install Now**.

## 2. Das Werkzeug holen {#get-the-tool}

- **Mit git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Ohne git:** Auf der [GitHub-Seite](https://github.com/Holdi601/3DHeat-GameFiles)
  klicke auf den grünen Button **Code** und dann auf **Download ZIP**, und entpacke es.

## 3. Ein Terminal im Ordner des Werkzeugs öffnen {#open-a-terminal-in-the-tools-folder}

- Öffne im Explorer den Ordner, der `README.md` enthält. Klicke in die Adressleiste, tippe
  `cmd` und drücke Enter. Ein schwarzes Fenster öffnet sich, schon in diesem Ordner.
- Oder öffne das **Windows Terminal** und wechsle mit `cd` dorthin:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Installieren, was das Werkzeug braucht {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Du solltest Zeilen sehen, die mit `Successfully installed ...` enden.

## 5. Prüfen, ob es funktioniert {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Du solltest `usage: heat3d_gamefiles [-h]` und eine Liste von Befehlen sehen (`identify`,
`list`, `extract`, `course`, ...). Das heißt Erfolg: Das Werkzeug ist bereit.

## Die Beispiele lesen {#reading-the-examples}

- `<etwas>` ist ein **Platzhalter**: tippe deinen eigenen Wert, ohne die spitzen Klammern.
  `<lap file>` wird zum Beispiel `laps\my_lap.json`.
- `[--option]` in eckigen Klammern ist **optional**: lass es weg, wenn du es nicht brauchst.
- Ein Pfad mit Leerzeichen braucht **doppelte Anführungszeichen**: `"C:\My Games\lap.json"`.
- Führe jeden Befehl im Ordner des Werkzeugs aus (Schritt 3).

## Wenn etwas schiefgeht {#when-something-goes-wrong}

| Du siehst | Was zu tun ist |
|---|---|
| `'python' is not recognized` | Python ist nicht installiert, oder "Add to PATH" war nicht angehakt. Führe das Installationsprogramm noch einmal aus, hake es an und öffne dann ein neues Terminal. |
| `No module named heat3d_gamefiles` | Das Terminal ist im falschen Ordner. Wechsle mit `cd` in den Ordner, der `README.md` enthält. |
| `No module named numpy` (oder ein anderer Name) | Schritt 4 wurde übersprungen. Führe `pip install -r requirements.txt` aus. |
| `can't open file` / `not found` mit einem Pfad | Der Pfad hat Leerzeichen und keine Anführungszeichen, oder einen Tippfehler. Setze ihn in doppelte Anführungszeichen. |

Weitere Meldungen und ihre Lösungen: [Fehlersuche](troubleshooting.md).
