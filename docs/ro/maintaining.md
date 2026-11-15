---
title: "Întreținere"
nav_order: 99
lang: "ro"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Întreținere: lista de verificare pentru lansare {#maintaining-the-release-checklist}

Înainte de a eticheta o lansare (`v` + numărul din `VERSION`), parcurge această listă în ordine. Ea ține paginile, imaginile și traducerile în acord cu codul.

1. **Regenerează paginile generate.**
   - `python tools/gen_docs_reference.py` rescrie [Referința comenzilor](../cli-reference.md) din `--help`-ul propriu al programului. `python tools/gen_docs_reference.py --check` iese cu codul 1 cât timp pagina salvată este învechită.
   - `python tools/docs_diagrams.py --strings` redesenează diagramele din `docs/assets/img/` și rescrie `docs/assets/i18n/en.json`, lista fiecărei etichete de diagramă de tradus.
2. **Listează ce s-a schimbat de la ultima lansare:** `git log --oneline v<last VERSION>..HEAD`. Fiecare comandă, opțiune, câmp de ieșire sau comportament nou are nevoie de o linie în `CHANGELOG.md` și de un rând în tabelul ei **Docs**, care numește pagina ce o explică. Actualizează acea pagină.
3. **Obține o revizuire independentă** a paginilor și imaginilor schimbate, de către cineva (sau un agent) care nu le-a scris, citind ca trei oameni: un începător care nu a folosit niciodată un terminal, un copil de 8 ani și un profesionist. Diagramele sunt verificate și ele: lizibile la lățimea paginii, etichete corecte, culori explicate.
4. **Repară ce găsește revizuirea**, apoi verifică faptul că nu a intrat date reale din joc: nicio hartă, nume de nivel sau de jucător, nicio cifră din înregistrări sau instalări reale (folosește substituenți precum `<map>` sau „nivelul de test”).
5. **Retraduce paginile schimbate.** Fiecare pagină tradusă notează hash-ul paginii engleze din care a fost făcută; paginile a căror sursă engleză s-a schimbat sunt traduse din nou, odată cu etichetele diagramelor. Apoi revizuiește fiecare limbă: clară pentru aceiași trei cititori, etichete corecte, cuvinte care se potrivesc cu interfața proprie a vizualizatorului în acea limbă.
6. **Trimite doar după acordul proprietarului.** Nimic nu este trimis sau etichetat înainte ca proprietarul să fi spus da.

## Traduceri: comenzile {#translations-the-commands}

Site-ul este tradus în cele 40 de limbi ale vizualizatorului 3DHeat: engleza în `docs/`, fiecare altă limbă în `docs/<lang>/`, cu aceleași nume de fișiere. `tools/docs_i18n.py` ține evidența:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Traduce doar ce listează `todo`: păstrează Markdown, linkurile, codul, numele fișierelor și ale coloanelor ca atare, traduce titlurile și descrierile imaginilor, și folosește cuvintele proprii ale vizualizatorului 3DHeat pentru butoanele și panourile lui (`src/i18n/locales/<lang>/`). Paginile de referință generate și imaginile din terminal rămân în engleză. Pe site, o traducere învechită spune asta și trimite la pagina engleză; una lipsă revine la engleză. Meniul de limbă din antet și redirecționarea după limba browserului de pe pagina principală vin din `docs/_includes/`.
