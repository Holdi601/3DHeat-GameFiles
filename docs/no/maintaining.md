---
title: "Vedlikehold: utgivelsessjekklisten"
nav_order: 99
lang: "no"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Vedlikehold: utgivelsessjekklisten {#maintaining-the-release-checklist}

Før du merker en utgivelse (`v` + tallet i `VERSION`), gå gjennom denne listen i
rekkefølge. Den holder sidene, bildene og oversettelsene i samsvar med koden.

1. **Lag de genererte sidene på nytt.**
   - `python tools/gen_docs_reference.py` skriver om
     [Kommandoreferansen](../cli-reference.md) fra programmets egen `--help`.
     `python tools/gen_docs_reference.py --check` avslutter med kode 1 så lenge den
     committede siden er utdatert.
   - `python tools/docs_diagrams.py --strings` tegner diagrammene i `docs/assets/img/`
     på nytt og skriver `docs/assets/i18n/en.json` på nytt, listen over hver
     diagramtekst som skal oversettes.
2. **List hva som har endret seg siden forrige utgivelse:**
   `git log --oneline v<last VERSION>..HEAD`. Hvert nytt verb, alternativ,
   utdatafelt eller oppførsel trenger en linje i `CHANGELOG.md` og en rad i sin
   **Docs**-tabell som nevner siden som forklarer den. Oppdater den siden.
3. **Få en uavhengig gjennomgang** av de endrede sidene og bildene, av noen (eller en
   agent) som ikke skrev dem, som leser som tre personer: en nybegynner som aldri har
   brukt en terminal, en åtteåring, og en profesjonell. Diagrammer kontrolleres også:
   lesbare i sidebredde, riktige tekster, farger forklart.
4. **Rett det gjennomgangen finner**, og sjekk deretter at ingen ekte spilldata har
   sneket seg inn: ingen kart-, nivå- eller spillernavn, ingen tall fra ekte
   innspillinger eller installasjoner (bruk plassholdere som `<map>` eller "the test
   level").
5. **Oversett de endrede sidene på nytt.** Hver oversatt side registrerer hashen av den
   engelske siden den ble laget fra; sider der den engelske kilden har endret seg, oversettes
   på nytt, og diagramtekstene med dem. Gå så gjennom hvert språk: klart for de samme tre
   leserne, tekster riktige, og ord som stemmer med visningens egne i det språket.
6. **Publiser først etter eierens klarsignal.** Ingenting blir publisert eller merket
   før eieren har sagt det.

## Oversettelser: kommandoene {#translations-the-commands}

Nettstedet er oversatt til de 40 språkene i 3DHeat-visningen: engelsk i `docs/`, hvert
annet språk i `docs/<lang>/` med de samme filnavnene. `tools/docs_i18n.py` gjør
bokføringen:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Oversett bare det `todo` lister: behold Markdown, lenker, kode og fil- og kolonnenavn som
de er, oversett titler og bildebeskrivelser, og bruk 3DHeat-visningens egne ord for knapper
og paneler (dens `src/i18n/locales/<lang>/`). Genererte referansesider og terminalbilder
forblir engelske. På nettstedet sier en utdatert oversettelse fra, og lenker til den
engelske siden; en manglende faller tilbake til engelsk. Språkmenyen i toppteksten og
nettsidens omdirigering etter nettleserspråk kommer fra `docs/_includes/`.
