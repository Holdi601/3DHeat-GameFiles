---
title: "Vzdrževanje"
nav_order: 99
lang: "sl"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Vzdrževanje: kontrolni seznam za izdajo {#maintaining-the-release-checklist}

Preden označite izdajo (`v` + številka v `VERSION`), pojdite po tem seznamu po vrsti. Tako strani, slike in prevodi ostanejo skladni s kodo.

1. **Ponovno ustvarite ustvarjene strani.**
   - `python tools/gen_docs_reference.py` iz `--help` programa na novo zapiše [Referenco ukazov](../cli-reference.md). `python tools/gen_docs_reference.py --check` izstopi s kodo 1, dokler je zapisana stran zastarela.
   - `python tools/docs_diagrams.py --strings` na novo nariše diagrame v `docs/assets/img/` in na novo zapiše `docs/assets/i18n/en.json`, seznam vseh oznak diagramov za prevod.
2. **Izpišite, kaj se je spremenilo od zadnje izdaje:**
   `git log --oneline v<last VERSION>..HEAD`. Vsak nov ukaz, možnost, polje izpisa ali vedenje potrebuje vrstico v `CHANGELOG.md` in vrstico v njegovi tabeli **Docs**, ki navaja stran, ki ga razlaga. Posodobite to stran.
3. **Pridobite neodvisen pregled** spremenjenih strani in slik od nekoga (ali agenta), ki jih ni napisal. Pregledovalec naj bere kot tri osebe: začetnik, ki še nikoli ni uporabljal terminala, osemletnik in strokovnjak. Pregledajo se tudi diagrami: berljivi na širini strani, oznake pravilne, barve razložene.
4. **Popravite, kar pregled najde**, nato preverite, da se ni vrinil pravi podatek iz igre: nobenega imena zemljevida, nivoja ali igralca, nobenih številk iz pravih posnetkov ali namestitev (uporabite nadomestke, kot `<map>` ali "the test level").
5. **Ponovno prevedite spremenjene strani.** Vsaka prevedena stran si zabeleži zgoščeno vrednost angleške strani, iz katere je nastala. Strani, katerih angleški vir se je spremenil, se ponovno prevedejo, z njimi pa tudi oznake diagramov. Nato pregledajte vsak jezik: jasen za iste tri bralce, oznake pravilne, besede se ujemajo z lastnim vmesnikom pregledovalnika 3DHeat v tistem jeziku.
6. **Potisnite šele po vaši odobritvi.** Nič se ne potisne ali označi, dokler lastnik tega ne reče.

## Prevodi: ukazi {#translations-the-commands}

Stran je prevedena v 40 jezikov pregledovalnika 3DHeat: angleščina je v `docs/`, vsak drug jezik je v `docs/<lang>/` z enakimi imeni datotek. `tools/docs_i18n.py` vodi evidenco:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prevedite samo tisto, kar izpiše `todo`. Ohranite Markdown, povezave, kodo ter imena datotek in stolpcev. Prevedite naslove in opise slik. Za gumbe in plošče pregledovalnika uporabite njegove lastne besede (iz `src/i18n/locales/<lang>/`). Ustvarjene referenčne strani in slike terminala ostanejo v angleščini. Na spletnem mestu zastarel prevod to pove in povezuje na angleško stran, manjkajoča stran pa se prikaže v angleščini. Meni za jezike v glavi in preusmeritev domače strani glede na jezik brskalnika prihajata iz `docs/_includes/`.
