---
title: Maintaining
nav_order: 99
---

# Maintaining: the release checklist

Before tagging a release (`v` + the number in `VERSION`), go through this list
in order. It keeps the pages, the pictures and the translations true to the code.

1. **Regenerate the generated pages.**
   - `python tools/gen_docs_reference.py` rewrites
     [Command reference](cli-reference.md) from the program's own `--help`.
     `python tools/gen_docs_reference.py --check` exits 1 while the committed
     page is out of date.
   - `python tools/docs_diagrams.py --strings` redraws the diagrams in
     `docs/assets/img/` and rewrites `docs/assets/i18n/en.json`, the list of
     every diagram label to translate.
2. **List what changed since the last release:**
   `git log --oneline v<last VERSION>..HEAD`. Every new verb, option, output
   field or behaviour needs a line in `CHANGELOG.md` and a row in its **Docs**
   table naming the page that explains it. Update that page.
3. **Get an independent review** of the changed pages and pictures, by someone
   (or an agent) who did not write them, reading as three people: a beginner who
   has never used a terminal, an 8-year-old, and a professional. Diagrams are
   checked too: readable at page width, labels correct, colours explained.
4. **Fix what the review finds**, then check no real game data slipped in:
   no map, level or player names, no figures from real recordings or installs
   (use placeholders such as `<map>` or "the test level").
5. **Re-translate the changed pages.** Each translated page records the hash of
   the English page it was made from; pages whose English source changed are
   translated again, and the diagram labels with them. Then review each
   language: clear for the same three readers, labels right, words matching the
   viewer's own interface in that language.
6. **Push only after the user's go-ahead.** Nothing is pushed or tagged before
   the owner has said so.

## Translations: the commands

The site is translated into the 3DHeat viewer's 40 languages: English in `docs/`, each other
language in `docs/<lang>/` with the same file names. `tools/docs_i18n.py` does the bookkeeping:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Translate only what `todo` lists: keep Markdown, links, code, file and column names as they are,
translate titles and picture descriptions, and use the 3DHeat viewer's own words for its buttons
and panels (its `src/i18n/locales/<lang>/`). Generated reference pages and terminal pictures stay
English. On the site, an outdated translation says so and links the English page; a missing one
falls back to English. The header's language menu and the home page's browser-language redirect
come from `docs/_includes/`.
