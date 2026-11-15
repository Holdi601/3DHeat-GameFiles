---
title: "Viðhald"
nav_order: 99
lang: "is"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Viðhald: útgáfugátlistinn {#maintaining-the-release-checklist}

Áður en þú merkir útgáfu (`v` + talan í `VERSION`) skaltu fara í gegnum þennan lista
í röð. Hann heldur síðunum, myndunum og þýðingunum sönnum gagnvart kóðanum.

1. **Endurbúðu til síðurnar sem eru búnar til.**
   - `python tools/gen_docs_reference.py` skrifar
     [Skipanayfirlit](../cli-reference.md) upp á nýtt úr `--help` forritsins sjálfs.
     `python tools/gen_docs_reference.py --check` hættir með 1 á meðan vistaða
     síðan er úrelt.
   - `python tools/docs_diagrams.py --strings` teiknar skýringarmyndirnar upp á nýtt í
     `docs/assets/img/` og skrifar `docs/assets/i18n/en.json`, listann yfir
     hvert myndamerki sem þarf að þýða.
2. **Teldu upp hvað breyttist frá síðustu útgáfu:**
   `git log --oneline v<last VERSION>..HEAD`. Sérhver ný skipun, valkostur, úttakssvið
   eða hegðun þarf línu í `CHANGELOG.md` og röð í **Docs** töflunni þar sem
   nefnd er síðan sem útskýrir það. Uppfærðu þá síðu.
3. **Fáðu óháða yfirferð** á breyttu síðunum og myndunum, hjá einhverjum
   (eða aðstoðarmanni) sem skrifaði þær ekki, og les sem þrír einstaklingar: byrjandi sem
   hefur aldrei notað skipanalínu, 8 ára barn og fagmaður. Skýringarmyndir eru
   líka skoðaðar: læsilegar í breidd síðunnar, merki rétt, litir útskýrðir.
4. **Lagaðu það sem yfirferðin finnur**, athugaðu svo að engin raunveruleg leikjagögn hafi slæðst með:
   engin kort, borð eða nöfn leikmanna, engar tölur úr raunverulegum upptökum eða uppsetningum
   (notaðu staðgengla eins og `<map>` eða „prófunarborðið“).
5. **Þýddu breyttu síðurnar upp á nýtt.** Hver þýdd síða geymir hakk (hash) af
   ensku síðunni sem hún var gerð úr; síður þar sem enska uppsprettan breyttist eru
   þýddar aftur, og myndamerkin með. Farðu síðan yfir hvert
   tungumál: skýrt fyrir sömu þrjá lesendur, merki rétt, orð í samræmi við
   eigið viðmót skoðarans á því tungumáli.
6. **Ýttu aðeins eftir grænt ljós frá notandanum.** Ekkert er ýtt eða merkt áður en
   eigandinn hefur sagt já.

## Þýðingar: skipanirnar {#translations-the-commands}

Vefurinn er þýddur á 40 tungumál 3DHeat-skoðarans: enska í `docs/`, hvert annað
tungumál í `docs/<lang>/` með sömu skráarnöfnum. `tools/docs_i18n.py` sér um bókhaldið:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Þýddu aðeins það sem `todo` telur upp: haltu Markdown, tenglum, kóða, skráar- og dálkanöfnum óbreyttum,
þýddu titla og myndlýsingar, og notaðu orð 3DHeat-skoðarans sjálfs fyrir hnappa hans
og spjöld (`src/i18n/locales/<lang>/`). Síður sem eru búnar til og skjámyndir af skipanalínu haldast
á ensku. Á vefnum segir úrelt þýðing frá því og tengir á ensku síðuna; vantandi þýðing
fellur aftur á ensku. Tungumálavalmynd haussins og vafratungumálsvísunin á forsíðunni
koma úr `docs/_includes/`.
