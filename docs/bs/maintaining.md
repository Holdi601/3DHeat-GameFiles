---
title: "Održavanje"
nav_order: 99
lang: "bs"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Održavanje: kontrolna lista izdanja {#maintaining-the-release-checklist}

Prije označavanja izdanja (`v` + broj iz `VERSION`), prođite kroz ovu listu
redom. Ona održava stranice, slike i prijevode tačnim u odnosu na kod.

1. **Ponovo generirajte generirane stranice.**
   - `python tools/gen_docs_reference.py` ponovo piše
     [Referencu komandi](../cli-reference.md) iz vlastitog `--help` programa.
     `python tools/gen_docs_reference.py --check` izlazi s 1 dok je pohranjena
     stranica zastarjela.
   - `python tools/docs_diagrams.py --strings` ponovo crta dijagrame u
     `docs/assets/img/` i ponovo piše `docs/assets/i18n/en.json`, listu
     svih oznaka dijagrama za prevođenje.
2. **Ispišite šta se promijenilo od posljednjeg izdanja:**
   `git log --oneline v<last VERSION>..HEAD`. Svaki novi glagol, opcija, izlazno
   polje ili ponašanje treba red u `CHANGELOG.md` i red u njegovoj tabeli **Docs**
   koji imenuje stranicu koja ga objašnjava. Ažurirajte tu stranicu.
3. **Nabavite nezavisan pregled** promijenjenih stranica i slika, od nekoga
   (ili agenta) ko ih nije napisao, koji čita kao tri osobe: početnik koji
   nikad nije koristio terminal, osmogodišnjak i profesionalac. Dijagrami se
   također provjeravaju: čitljivi u širini stranice, oznake tačne, boje objašnjene.
4. **Popravite šta pregled nađe**, zatim provjerite da nijedan stvarni podatak igre nije promakao:
   nikakva imena mapa, nivoa ili igrača, nikakve brojke iz stvarnih snimaka ili instalacija
   (koristite rezervirane oznake poput `<map>` ili „testni nivo“).
5. **Ponovo prevedite promijenjene stranice.** Svaka prevedena stranica bilježi heš
   engleske stranice iz koje je napravljena; stranice čiji se engleski izvor promijenio
   prevode se ponovo, a s njima i oznake dijagrama. Zatim pregledajte svaki
   jezik: jasno za ista tri čitaoca, oznake tačne, riječi usklađene s
   vlastitim sučeljem preglednika na tom jeziku.
6. **Šaljite tek nakon odobrenja korisnika.** Ništa se ne šalje niti označava prije nego
   što vlasnik to kaže.

## Prijevodi: komande {#translations-the-commands}

Sajt je preveden na 40 jezika 3DHeat preglednika: engleski u `docs/`, svaki drugi
jezik u `docs/<lang>/` s istim imenima datoteka. `tools/docs_i18n.py` vodi evidenciju:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Prevodite samo ono što `todo` ispisuje: Markdown, linkove, kod, imena datoteka i kolona ostavite kakvi jesu,
prevedite naslove i opise slika, i koristite vlastite riječi 3DHeat preglednika za njegova dugmad
i panele (njegov `src/i18n/locales/<lang>/`). Generirane referentne stranice i slike terminala ostaju
na engleskom. Na sajtu zastarjeli prijevod to kaže i povezuje englesku stranicu; nedostajući
se vraća na engleski. Jezički meni u zaglavlju i preusmjeravanje početne stranice prema jeziku preglednika
dolaze iz `docs/_includes/`.
