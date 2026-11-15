---
title: Pflege
nav_order: 99
lang: de
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Pflege: die Checkliste für Veröffentlichungen {#maintaining-the-release-checklist}

Bevor du ein Release markierst (`v` + die Nummer in `VERSION`), geh diese Liste der Reihe nach durch. Sie hält die Seiten, die Bilder und die Übersetzungen mit dem Code im Einklang.

1. **Erzeuge die generierten Seiten neu.**
   - `python tools/gen_docs_reference.py` schreibt die [Befehlsreferenz](../cli-reference.md) aus der eigenen `--help` des Programms neu. `python tools/gen_docs_reference.py --check` endet mit Exit-Code 1, solange die gespeicherte Seite veraltet ist.
   - `python tools/docs_diagrams.py --strings` zeichnet die Diagramme in `docs/assets/img/` neu und schreibt `docs/assets/i18n/en.json` neu, die Liste aller Beschriftungen der Diagramme, die übersetzt werden müssen.
2. **Liste auf, was seit dem letzten Release geändert wurde:** `git log --oneline v<last VERSION>..HEAD`. Jeder neue Befehl, jede neue Option, jedes neue Ausgabefeld und jedes neue Verhalten braucht eine Zeile in `CHANGELOG.md` und eine Zeile in deiner Tabelle **Docs**, die auf die Seite verweist, die es erklärt. Aktualisiere diese Seite.
3. **Hol dir eine unabhängige Prüfung** der geänderten Seiten und Bilder, von jemandem (oder einem Agenten), der sie nicht geschrieben hat. Er liest sie aus der Sicht von drei Leuten: einem Anfänger, der noch nie ein Terminal benutzt hat, einem Achtjährigen und einem Profi. Auch die Diagramme werden geprüft: lesbar in Seitenbreite, Beschriftungen richtig, Farben erklärt.
4. **Behebe, was die Prüfung findet**, und prüfe dann, dass keine echten Spieldaten hineingerutscht sind: keine Namen von Karten, Leveln oder Spielern, keine Zahlen aus echten Aufnahmen oder Installationen (nimm Platzhalter wie `<map>` oder „das Testlevel“).
5. **Übersetze die geänderten Seiten neu.** Jede übersetzte Seite speichert den Hash der englischen Seite, aus der sie entstanden ist. Seiten, deren englische Vorlage sich geändert hat, werden neu übersetzt, und mit ihnen die Beschriftungen der Diagramme. Prüfe dann jede Sprache: klar für die drei gleichen Leser, Beschriftungen richtig, Wörter passend zur eigenen Oberfläche des Viewers in dieser Sprache.
6. **Veröffentliche erst nach der Freigabe durch den Besitzer.** Nichts wird gepusht oder markiert, bevor der Besitzer es gesagt hat.

## Übersetzungen: die Befehle {#translations-the-commands}

Die Seite ist in die 40 Sprachen des 3DHeat-Viewers übersetzt: Englisch in `docs/`, jede andere Sprache in `docs/<lang>/` mit denselben Dateinamen. `tools/docs_i18n.py` erledigt die Buchführung:

```bash
python tools/docs_i18n.py hashes             # nach jeder Änderung am Englischen: den Hash jeder Seite festhalten
python tools/docs_i18n.py svg-strings        # nach jeder Bildänderung: die Beschriftungen, die übersetzt werden müssen
python tools/docs_i18n.py status             # je Sprache: aktuell, veraltet, fehlende Seiten
python tools/docs_i18n.py todo --lang de     # die deutschen Seiten, die (neu) übersetzt werden müssen
python tools/docs_i18n.py svg-build --lang de    # deutsche Bilder aus docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # die deutschen Seiten mit dem englischen Hash versehen
python tools/docs_i18n.py check              # Exit-Code 1, wenn Hashes oder Beschriftungen veraltet sind
```

Übersetze nur, was `todo` auflistet. Behalte Markdown, Links, Code, Datei- und Spaltennamen bei, übersetze Titel und Bildbeschreibungen, und nimm für Knöpfe und Bereiche des 3DHeat-Viewers dessen eigene Wörter (aus `src/i18n/locales/<lang>/`). Generierte Referenzseiten und Terminalbilder bleiben Englisch. Auf der Website sagt eine veraltete Übersetzung das und verlinkt die englische Seite; fehlt eine Übersetzung, wird Englisch gezeigt. Das Sprachmenü im Kopf und die Weiterleitung der Startseite nach Browsersprache kommen aus `docs/_includes/`.
