---
title: "Údržba: kontrolní seznam vydání"
nav_order: 99
lang: "cs"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Údržba: kontrolní seznam vydání {#maintaining-the-release-checklist}

Před označením vydání (`v` + číslo ve `VERSION`) projděte tento seznam postupně. Udržuje stránky, obrázky a překlady v souladu s kódem.

1. **Znovu vygenerujte generované stránky.**
   - `python tools/gen_docs_reference.py` přepíše [Přehled příkazů](../cli-reference.md) podle vlastní nápovědy `--help` programu. `python tools/gen_docs_reference.py --check` skončí s kódem 1, dokud je uložená stránka zastaralá.
   - `python tools/docs_diagrams.py --strings` překreslí diagramy v `docs/assets/img/` a přepíše `docs/assets/i18n/en.json`, což je seznam všech popisků diagramů k překladu.
2. **Vypište, co se změnilo od posledního vydání:** `git log --oneline v<last VERSION>..HEAD`. Každý nový příkaz, volba, výstupní pole nebo chování potřebuje řádek v `CHANGELOG.md` a řádek v tabulce **Docs**, který uvádí stránku, jež to vysvětluje. Tu stránku aktualizujte.
3. **Získejte nezávislou kontrolu** změněných stránek a obrázků od někoho (nebo od agenta), kdo je nepsal. Ať čte jako tři lidé: začátečník, který nikdy nepoužil terminál, osmiletý žák a profesionál. Kontrolují se i diagramy: musí být čitelné na šířku stránky, popisky správné a barvy vysvětlené.
4. **Opravte, co kontrola najde,** a pak zkontrolujte, že se nedostala žádná skutečná herní data: žádné názvy map, úrovní ani hráčů a žádná čísla ze skutečných záznamů nebo instalací. Použijte zástupné údaje, jako `<map>` nebo „testovací úroveň“.
5. **Přeložte znovu změněné stránky.** Každá přeložená stránka si zaznamenává hash anglické stránky, ze které vznikla. Stránky, jejichž anglický zdroj se změnil, se přeloží znovu, a s nimi i popisky diagramů. Pak zkontrolujte každý jazyk: musí být srozumitelný pro stejné tři čtenáře, popisky správné a slova odpovídat vlastnímu rozhraní prohlížeče 3DHeat v daném jazyce.
6. **Odešlete až po souhlasu majitele.** Nic se neodesílá ani neoznačuje, dokud to vlastník nepotvrdí.

## Překlady: příkazy {#translations-the-commands}

Stránky jsou přeloženy do 40 jazyků, které prohlížeč 3DHeat zná: angličtina je v `docs/`, každý další jazyk v `docs/<lang>/` se stejnými názvy souborů. `tools/docs_i18n.py` vede evidenci:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Překládejte jen to, co vypíše `todo`. Markdown, odkazy, kód, názvy souborů a sloupců ponechte beze změny. Přeložte titulky a popisy obrázků a pro tlačítka a panely používejte vlastní slova prohlížeče 3DHeat (jeho `src/i18n/locales/<lang>/`). Generované referenční stránky a obrázky terminálu zůstávají v angličtině. Na webu zastaralý překlad na to upozorní a odkáže na anglickou stránku. Chybějící stránka se vrátí k angličtině. Nabídku jazyků v záhlaví a přesměrování na domovské stránce podle jazyka prohlížeče řídí `docs/_includes/`.
