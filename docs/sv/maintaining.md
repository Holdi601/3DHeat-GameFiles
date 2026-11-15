---
title: Underhåll
nav_order: 99
lang: "sv"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Underhåll: checklistan för release {#maintaining-the-release-checklist}

Innan du taggar en release (`v` + numret i `VERSION`) går du igenom den här listan i ordning. Den håller sidorna, bilderna och översättningarna sanna mot koden.

1. **Generera om de genererade sidorna.**
   - `python tools/gen_docs_reference.py` skriver om [Kommandoreferens](../cli-reference.md) från programmets egen `--help`.
     `python tools/gen_docs_reference.py --check` avslutas med 1 så länge den incheckade sidan är föråldrad.
   - `python tools/docs_diagrams.py --strings` ritar om diagrammen i `docs/assets/img/` och skriver om `docs/assets/i18n/en.json`, listan över varje diagramtext som ska översättas.
2. **Lista vad som ändrats sedan förra releasen:**
   `git log --oneline v<last VERSION>..HEAD`. Varje nytt verb, alternativ, utdatafält eller beteende behöver en rad i `CHANGELOG.md` och en rad i sin tabell **Docs** som anger sidan som förklarar det. Uppdatera den sidan.
3. **Låt någon oberoende granska** de ändrade sidorna och bilderna, av någon (eller en agent) som inte skrev dem, och läsa som tre personer: en nybörjare som aldrig använt en terminal, en åttaåring och en proffs. Diagram kontrolleras också: de ska gå att läsa i sidbredd, med rätt texter och med färgerna förklarade.
4. **Rätta det granskningen hittar**, och kontrollera sedan att inga riktiga speldata har smugit sig in: inga karta-, nivå- eller spelarnamn, inga siffror från riktiga inspelningar eller installationer (använd platshållare som `<map>` eller ”testnivån”).
5. **Översätt om de ändrade sidorna.** Varje översatt sida registrerar hashvärdet för den engelska sida den gjordes från; sidor vars engelska källa ändrats översätts på nytt, och diagramtexterna med dem. Granska sedan varje språk: tydligt för samma tre läsare, rätt texter, och orden stämmer med visarens eget gränssnitt på det språket.
6. **Pusha först när användaren har gett klartecken.** Inget pushas eller taggas innan ägaren har sagt till.

## Översättningar: kommandona {#translations-the-commands}

Webbplatsen är översatt till de 40 språk som 3DHeat-visaren har: engelska i `docs/`, varje annat språk i `docs/<lang>/` med samma filnamn. `tools/docs_i18n.py` sköter bokföringen:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Översätt bara det `todo` listar: behåll Markdown, länkar, kod, fil- och kolumnnamn som de är, översätt titlar och bildbeskrivningar, och använd 3DHeat-visarens egna ord för knappar och paneler (dess `src/i18n/locales/<lang>/`). Genererade referenssidor och terminalbilder förblir på engelska. På webbplatsen säger en föråldrad översättning det och länkar till den engelska sidan; en saknad faller tillbaka till engelska. Språkmenyn i sidhuvudet och startsidans omdirigering efter webbläsarens språk kommer från `docs/_includes/`.
