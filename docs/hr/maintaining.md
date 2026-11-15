---
title: "Održavanje"
nav_order: 99
lang: "hr"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Održavanje: popis za izdanje {#maintaining-the-release-checklist}

Prije označavanja izdanja (`v` + broj u `VERSION`) prođite ovaj popis redom. Tako stranice, slike i prijevodi ostaju vjerni kodu.

1. **Ponovo generirajte generirane stranice.**
   - `python tools/gen_docs_reference.py` prepisuje [Referencu naredbi](../cli-reference.md) iz vlastitog `--help` programa. `python tools/gen_docs_reference.py --check` završava s izlaznim kodom 1 dok je zapisana stranica zastarjela.
   - `python tools/docs_diagrams.py --strings` ponovo crta dijagrame u `docs/assets/img/` i prepisuje `docs/assets/i18n/en.json`, popis svake oznake dijagrama za prijevod.
2. **Popišite što se promijenilo od posljednjeg izdanja:** `git log --oneline v<last VERSION>..HEAD`. Svaki novi glagol, opcija, polje izlaza ili ponašanje treba redak u `CHANGELOG.md` i redak u tablici **Docs** koji imenuje stranicu koja ga objašnjava. Ažurirajte tu stranicu.
3. **Zatražite neovisnu recenziju** izmijenjenih stranica i slika, od nekoga (ili agenta) tko ih nije napisao. Čitajte ih kao tri osobe: početnik koji nikad nije koristio terminal, osmogodišnjak i stručnjak. Provjeravaju se i dijagrami: čitljivi su na širini stranice, oznake su točne, a boje objašnjene.
4. **Popravite ono što recenzija nađe**, zatim provjerite da nijedni pravi podaci igre nisu procurjeli: nema imena karata, razina ni igrača, nema brojki iz pravih snimaka ni instalacija. Koristite zamjenske oznake, poput `<map>` ili „testna razina”.
5. **Ponovo prevedite izmijenjene stranice.** Svaka prevedena stranica bilježi hash engleske stranice iz koje je nastala. Stranice čiji se engleski izvor promijenio prevode se iznova, a s njima i oznake dijagrama. Zatim pregledajte svaki jezik: mora biti jasan istim trima čitateljima, oznake moraju biti točne, a riječi se moraju podudarati sa sučeljem preglednika 3DHeat na tom jeziku.
6. **Gurnite tek nakon dopuštenja korisnika.** Ništa se ne gura niti označava prije nego vlasnik to kaže.

## Prijevodi: naredbe {#translations-the-commands}

Stranice su prevedene na 40 jezika preglednika 3DHeat: engleski je u `docs/`, a svaki drugi jezik u `docs/<lang>/`, s istim imenima datoteka. `tools/docs_i18n.py` vodi evidenciju:

```bash
python tools/docs_i18n.py hashes             # nakon svake promjene engleskog: zabilježi hash svake stranice
python tools/docs_i18n.py svg-strings        # nakon svake promjene slike: oznake za prijevod
python tools/docs_i18n.py status             # po jeziku: ažurne, zastarjele i nedostajuće stranice
python tools/docs_i18n.py todo --lang de     # njemačke stranice za (ponovni) prijevod
python tools/docs_i18n.py svg-build --lang de    # njemačke slike iz docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # označi njemačke stranice hashom engleske
python tools/docs_i18n.py check              # izlaz 1 kad su hashovi ili oznake zastarjeli
```

Prevodite samo ono što `todo` navodi. Zadržite Markdown, poveznice, kod, imena datoteka i stupaca, a prevedite naslove i opise slika. Za gumbe i ploče preglednika koristite vlastite riječi 3DHeat preglednika (`src/i18n/locales/<lang>/`). Generirane stranice referenci i terminalne slike ostaju engleske. Na stranici zastarjeli prijevod to kaže i povezuje englesku stranicu, a nedostajući se vraća na engleski. Izbornik jezika u zaglavlju i preusmjeravanje početne stranice prema jeziku preglednika dolaze iz `docs/_includes/`.
