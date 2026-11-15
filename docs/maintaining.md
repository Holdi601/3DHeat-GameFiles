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
