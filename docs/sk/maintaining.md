---
title: "Údržba: kontrolný zoznam pred vydaním"
nav_order: 99
lang: "sk"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Údržba: kontrolný zoznam pred vydaním {#maintaining-the-release-checklist}

Pred označením vydania (`v` + číslo v `VERSION`) prejdite tento zoznam po poriadku. Udržuje stránky, obrázky a preklady v súlade s kódom.

1. **Znovu vygenerujte generované stránky.**
   - `python tools/gen_docs_reference.py` prepíše [Referenciu príkazov](../cli-reference.md) z vlastnej pomoci programu (`--help`). `python tools/gen_docs_reference.py --check` skončí s kódom 1, kým je uložená stránka zastaraná.
   - `python tools/docs_diagrams.py --strings` prekreslí diagramy v `docs/assets/img/` a prepíše `docs/assets/i18n/en.json`, zoznam všetkých popisov diagramov na preklad.
2. **Vypíšte, čo sa zmenilo od posledného vydania:** `git log --oneline v<last VERSION>..HEAD`. Každý nový príkaz, voľba, pole výstupu alebo správanie potrebuje riadok v `CHANGELOG.md` a riadok v tabuľke **Dokumentácia**, ktorý pomenuje stránku, na ktorej je vysvetlené. Aktualizujte túto stránku.
3. **Získajte nezávislú kontrolu** zmenených stránok a obrázkov od niekoho (alebo agenta), kto ich nenapísal. Čítajte ich ako traja ľudia: začiatočník, ktorý nikdy nepoužil terminál, osemročné dieťa a profesionál. Kontrolujú sa aj diagramy: čitateľné na šírku stránky, popisy správne, farby vysvetlené.
4. **Opravte, čo kontrola nájde**, potom overte, že sa nedostali žiadne skutočné herné dáta: žiadne mená máp, úrovní ani hráčov, žiadne čísla zo skutočných záznamov alebo inštalácií. Použite zástupné znaky ako `<map>` alebo „testovacia úroveň“.
5. **Znovu preložte zmenené stránky.** Každá preložená stránka si zapamätá hash anglickej stránky, z ktorej vznikla. Stránky, ktorých anglický zdroj sa zmenil, sa prekladajú znova, a s nimi aj popisy diagramov. Potom skontrolujte každý jazyk: jasné pre tých istých troch čitateľov, popisy správne a slová zodpovedajú vlastnému rozhraniu prehliadača v danom jazyku.
6. **Zverejnite až po súhlase majiteľa.** Nič sa nezverejní ani neoznačí skôr, než to vlastník povie.

## Preklady: príkazy {#translations-the-commands}

Stránky sú preložené do 40 jazykov prehliadača 3DHeat: angličtina je v `docs/`, každý ďalší jazyk v `docs/<lang>/` s rovnakými menami súborov. `tools/docs_i18n.py` vedie evidenciu:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prekladajte len to, čo vypíše `todo`: zachovajte Markdown, odkazy, kód a mená súborov a stĺpcov. Preložte nadpisy a popisy obrázkov a používajte vlastné slová prehliadača 3DHeat pre jeho tlačidlá a panely (jeho `src/i18n/locales/<lang>/`). Generované referenčné stránky a terminálové obrázky zostávajú v angličtine. Na webe zastaraný preklad to povie a odkazuje na anglickú stránku; chýbajúca stránka sa vráti k angličtine. Ponuka jazykov v hlavičke a presmerovanie domovskej stránky podľa jazyka prehliadača sú v `docs/_includes/`.
