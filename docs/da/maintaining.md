---
title: "Vedligeholdelse"
nav_order: 99
lang: "da"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Vedligeholdelse: udgivelsestjeklisten {#maintaining-the-release-checklist}

Før du markerer en udgivelse (`v` + tallet i `VERSION`), så gennemgå denne liste
i rækkefølge. Den holder siderne, billederne og oversættelserne sande i forhold til koden.

1. **Generer de genererede sider igen.**
   - `python tools/gen_docs_reference.py` skriver
     [Kommandoreference](../cli-reference.md) om ud fra programmets egen `--help`.
     `python tools/gen_docs_reference.py --check` afslutter med 1, mens den committede
     side er forældet.
   - `python tools/docs_diagrams.py --strings` tegner diagrammerne i `docs/assets/img/` om og skriver
     `docs/assets/i18n/en.json` om, listen over alle diagramtekster, der skal oversættes.
2. **List, hvad der er ændret siden den sidste udgivelse:**
   `git log --oneline v<last VERSION>..HEAD`. Hvert nye verbum, hver valgmulighed, hvert outputfelt eller hver adfærd
   skal have en linje i `CHANGELOG.md` og en række i tabellen **Docs**, der
   nævner den side, som forklarer den. Opdater den side.
3. **Få en uafhængig gennemgang** af de ændrede sider og billeder, af en person
   (eller en agent), der ikke skrev dem, og som læser dem som tre personer: en begynder, der aldrig
   har brugt en terminal, et otte-årigt barn og en professionel. Diagrammer bliver også
   kontrolleret: læselige i sidens bredde, labels rigtige, farver forklaret.
4. **Ret det, gennemgangen finder**, og kontrollér derefter, at ingen rigtige spildata er sluppet med:
   ingen kort-, bane- eller spillernavne, ingen tal fra rigtige optagelser eller installationer
   (brug pladsholdere som `<map>` eller "the test level").
5. **Oversæt de ændrede sider igen.** Hver oversat side gemmer hashen af den
   engelske side, den blev lavet ud fra; sider, hvis engelske kilde er ændret, oversættes igen, og
   diagramtekster med dem. Gennemgå derefter hvert sprog: tydeligt for de samme tre
   læsere, labels rigtige, ord, der passer til vieweren's egen grænseflade på det sprog.
6. **Push først, når ejeren har givet grønt lys.** Intet bliver pushet eller markeret med tag, før
   ejeren har sagt det.

## Oversættelser: kommandoerne {#translations-the-commands}

Siden er oversat til vieweren's 40 sprog for 3DHeat: engelsk i `docs/`, hvert andet
sprog i `docs/<lang>/` med de samme filnavne. `tools/docs_i18n.py` står for bogholderiet:

```bash
python tools/docs_i18n.py hashes             # efter enhver engelsk ændring: gem hver sides hash
python tools/docs_i18n.py svg-strings        # efter enhver billedændring: teksterne der skal oversættes
python tools/docs_i18n.py status             # pr. sprog: aktuelle, forældede og manglende sider
python tools/docs_i18n.py todo --lang de     # de tyske sider, der skal (gen)oversættes
python tools/docs_i18n.py svg-build --lang de    # tyske billeder ud fra docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stempl de tyske sider med deres engelske hash
python tools/docs_i18n.py check              # afslutter med 1, når hashes eller labels er forældede
```

Oversæt kun det, `todo` lister: behold Markdown, links, kode, fil- og kolonnenavne, som de er, oversæt
titler og billedbeskrivelser, og brug 3DHeat-vieweren's egne ord til dens knapper
og paneler (dens `src/i18n/locales/<lang>/`). Genererede referencesider og terminalbilleder
forbliver engelske. På siden viser en forældet oversættelse det og linker til den engelske side; en manglende
falder tilbage til engelsk. Sprogmenuen i sidehovedet og browsersprog-omdirigeringen
på forsiden kommer fra `docs/_includes/`.
