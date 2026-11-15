---
title: "Ylläpito"
nav_order: 99
lang: "fi"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Ylläpito: julkaisun tarkistuslista {#maintaining-the-release-checklist}

Ennen julkaisun merkitsemistä tagilla (`v` + `VERSION`-tiedoston numero) käy tämä lista läpi järjestyksessä. Se pitää sivut, kuvat ja käännökset ajan tasalla koodin kanssa.

1. **Luo generoidut sivut uudelleen.**
   - `python tools/gen_docs_reference.py` kirjoittaa [Komentoviitteen](../cli-reference.md) uudelleen ohjelman omasta `--help`-tulosteesta. `python tools/gen_docs_reference.py --check` päättyy koodiin 1, kun tallennettu sivu on vanhentunut.
   - `python tools/docs_diagrams.py --strings` piirtää kaaviot uudelleen kansioon `docs/assets/img/` ja kirjoittaa uudelleen tiedoston `docs/assets/i18n/en.json`, eli luettelon kaikista kaavioiden tekstimerkinnöistä, jotka pitää kääntää.
2. **Listaa, mikä on muuttunut edellisen julkaisun jälkeen:**
   `git log --oneline v<last VERSION>..HEAD`. Jokainen uusi komento, valinta, tulostekenttä tai toiminta tarvitsee rivin tiedostoon `CHANGELOG.md` ja rivin **Docs**-taulukkoon, joka nimeää sivun, jolla se selitetään. Päivitä se sivu.
3. **Pyydä riippumaton arvio** muuttuneista sivuista ja kuvista. Arvion tekee joku (tai agentti), joka ei kirjoittanut niitä. Hän lukee ne kolmen lukijan näkökulmasta: aloittelija, joka ei ole koskaan käyttänyt päätettä, 8-vuotias ja ammattilainen. Myös kaaviot tarkistetaan: ne ovat luettavia sivun leveydellä, tekstit ovat oikein ja värit selitetty.
4. **Korjaa arvion löydökset** ja tarkista sitten, ettei oikeaa pelidataa ole päässyt mukaan: ei kartta-, kenttä- tai pelaajanimiä, ei lukuja oikeista tallenteista tai asennuksista (käytä paikkamerkkejä, kuten `<map>` tai "testikenttä").
5. **Käännä muuttuneet sivut uudelleen.** Jokainen käännetty sivu tallentaa englanninkielisen sivun tiivisteen, josta se tehtiin. Sivut, joiden englanninkielinen lähde on muuttunut, käännetään uudelleen, ja kaavioiden tekstit kanssa. Tarkista sitten jokainen kieli: sama selkeys kolmelle lukijalle, tekstit oikein ja sanat vastaavat katsojan omaa käyttöliittymää kyseisellä kielellä.
6. **Työnnä vasta, kun omistaja on antanut luvan.** Mitään ei työnnetä eikä tagata ennen kuin omistaja on sanonut niin.

## Käännökset: komennot {#translations-the-commands}

Sivusto on käännetty 3DHeat-katsojan 40 kielelle: englanti on kansiossa `docs/`, muut kielet kansiossa `docs/<lang>/` samoilla tiedostonimillä. `tools/docs_i18n.py` hoitaa kirjanpidon:

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Käännä vain se, mitä `todo` listaa. Säilytä Markdown, linkit, koodi sekä tiedosto- ja sarakenimet sellaisinaan, käännä otsikot ja kuvien kuvaukset, ja käytä 3DHeat-katsojan omia sanoja sen painikkeille ja paneeleille (sen `src/i18n/locales/<lang>/`). Generoidut viitesivut ja terminaalikuvat pysyvät englanninkielisinä. Sivustolla vanhentunut käännös kertoo sen ja linkittää englanninkieliselle sivulle. Puuttuva käännös näyttää englanninkielisen sivun. Kielivalikko ja etusivun selaimen kielen mukainen uudelleenohjaus tulevat kansiosta `docs/_includes/`.
