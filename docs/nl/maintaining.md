---
title: Onderhouden
nav_order: 99
lang: "nl"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Onderhouden: de checklist voor een release {#maintaining-the-release-checklist}

Voordat je een release taggt (`v` + het getal in `VERSION`), loop je deze lijst in volgorde door. Zo blijven de pagina's, de afbeeldingen en de vertalingen in overeenstemming met de code.

1. **Genereer de gegenereerde pagina's opnieuw.**
   - `python tools/gen_docs_reference.py` schrijft de [Commandoreferentie](../cli-reference.md) opnieuw uit de eigen `--help` van het programma. `python tools/gen_docs_reference.py --check` eindigt met exitcode 1 zolang de vastgelegde pagina verouderd is.
   - `python tools/docs_diagrams.py --strings` tekent de diagrammen in `docs/assets/img/` opnieuw en schrijft `docs/assets/i18n/en.json` opnieuw: de lijst van elk diagramlabel om te vertalen.
2. **Lijst wat er sinds de vorige release veranderd is:**
   `git log --oneline v<last VERSION>..HEAD`. Elk nieuw commando, elke nieuwe optie, elk uitvoerveld of gedrag heeft een regel nodig in `CHANGELOG.md` en een rij in de tabel **Docs** die de pagina noemt die het uitlegt. Werk die pagina bij.
3. **Vraag een onafhankelijke beoordeling** van de gewijzigde pagina's en afbeeldingen, door iemand (of een agent) die ze niet zelf schreef. Die leest als drie personen: een beginner die nog nooit een terminal gebruikte, een achtjarige, en een professional. Ook diagrammen worden nagekeken: leesbaar op paginabreedte, labels juist, kleuren uitgelegd.
4. **Los op wat de beoordeling vindt**, en controleer dan dat er geen echte spelgegevens zijn ingeslopen: geen namen van kaarten, levels of spelers, en geen cijfers uit echte opnames of installaties (gebruik plaatshouders zoals `<map>` of "het testlevel").
5. **Vertaal de gewijzigde pagina's opnieuw.** Elke vertaalde pagina onthoudt de hash van de Engelse pagina waarop ze gebaseerd is. Pagina's waarvan de Engelse bron veranderd is, worden opnieuw vertaald, en de diagramlabels met hen. Beoordeel daarna elke taal: helder voor dezelfde drie lezers, labels juist, en woorden die passen bij de eigen interface van de viewer in die taal.
6. **Push pas na het akkoord van de eigenaar.** Niets wordt gepusht of getagd voordat de eigenaar dat heeft gezegd.

## Vertalingen: de commando's {#translations-the-commands}

De site is vertaald in de 40 talen van de 3DHeat-viewer: Engels in `docs/`, elke andere taal in `docs/<lang>/` met dezelfde bestandsnamen. `tools/docs_i18n.py` houdt de administratie bij:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Vertaal alleen wat `todo` aangeeft. Laat Markdown, links, code, en bestands- en kolomnamen zoals ze zijn. Vertaal titels en beschrijvingen van afbeeldingen, en gebruik de eigen woorden van de 3DHeat-viewer voor zijn knoppen en panelen (zijn `src/i18n/locales/<lang>/`). Gegenereerde referentiepagina's en terminalafbeeldingen blijven Engels. Op de site zegt een verouderde vertaling dat en linkt naar de Engelse pagina; een ontbrekende valt terug op Engels. Het taalmenu in de kop en de doorverwijzing op basis van de browsertaal van de startpagina komen uit `docs/_includes/`.
