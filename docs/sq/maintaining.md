---
title: "Mirëmbajtja"
nav_order: 99
lang: "sq"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Mirëmbajtja: lista e kontrollit për botimin {#maintaining-the-release-checklist}

Para se të etiketosh një botim (`v` + numri te `VERSION`), kalo këtë listë
me radhë. Ajo i mban faqet, fotot dhe përkthimet në përputhje me kodin.

1. **Rigjenero faqet e gjeneruara.**
   - `python tools/gen_docs_reference.py` rishkruan
     [Referencën e komandave](../cli-reference.md) nga `--help` i vetë programit.
     `python tools/gen_docs_reference.py --check` del me 1 për sa kohë faqja e
     commit-uar është e vjetruar.
   - `python tools/docs_diagrams.py --strings` rivizaton diagramet te
     `docs/assets/img/` dhe rishkruan `docs/assets/i18n/en.json`, listën e
     çdo etikete diagrami që duhet përkthyer.
2. **Listo çfarë ndryshoi që nga botimi i fundit:**
   `git log --oneline v<last VERSION>..HEAD`. Çdo komandë, opsion, fushë
   dalje ose sjellje e re ka nevojë për një rresht te `CHANGELOG.md` dhe një rresht te tabela e tij
   **Docs** që emërton faqen që e shpjegon. Përditëso atë faqe.
3. **Merr një shqyrtim të pavarur** të faqeve dhe fotove të ndryshuara, nga dikush
   (ose një agjent) që nuk i ka shkruar, duke lexuar si tre persona: një fillestar që
   nuk ka përdorur kurrë terminal, një 8-vjeç dhe një profesionist. Diagramet
   kontrollohen gjithashtu: të lexueshme në gjerësinë e faqes, etiketa të sakta, ngjyra të shpjeguara.
4. **Rregullo çfarë gjen shqyrtimi**, pastaj kontrollo që nuk ka rrëshqitur të dhëna reale loje:
   asnjë emër harte, niveli apo lojtari, asnjë shifër nga regjistrime ose instalime të vërteta
   (përdor shenja zëvendësuese si `<map>` ose "niveli i testit").
5. **Ripërkthe faqet e ndryshuara.** Çdo faqe e përkthyer ruan hash-in e
   faqes angleze nga e cila u bë; faqet burimi anglez i të cilave ndryshoi
   përkthehen sërish, bashkë me etiketat e diagrameve. Pastaj shqyrto çdo
   gjuhë: e qartë për të tre lexuesit e njëjtë, etiketa të sakta, fjalë që përputhen me ndërfaqen
   e vetë shikuesit në atë gjuhë.
6. **Shtyje vetëm pas lejes së përdoruesit.** Asgjë nuk shtyhet apo etiketohet para se
   pronari ta ketë thënë.

## Përkthimet: komandat {#translations-the-commands}

Faqja është e përkthyer në 40 gjuhët e shikuesit 3DHeat: anglishtja te `docs/`, çdo gjuhë tjetër
te `docs/<lang>/` me të njëjtat emra skedarësh. `tools/docs_i18n.py` mban llogaritë:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Përkthe vetëm çfarë liston `todo`: mbaji Markdown-in, lidhjet, kodin, emrat e skedarëve dhe kolonave siç janë,
përkthe titujt dhe përshkrimet e fotove, dhe përdor fjalët e vetë shikuesit 3DHeat për butonat
dhe panelet e tij (`src/i18n/locales/<lang>/`). Faqet e referencës së gjeneruara dhe fotot e terminalit mbeten
në anglisht. Në faqe, një përkthim i vjetruar e thotë këtë dhe lidh faqen angleze; një i munguar
kthehet te anglishtja. Menyja e gjuhëve në krye dhe ridrejtimi i faqes kryesore sipas gjuhës së shfletuesit
vijnë nga `docs/_includes/`.
