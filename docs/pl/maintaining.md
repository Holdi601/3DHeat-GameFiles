---
title: Utrzymanie
nav_order: 99
lang: "pl"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Utrzymanie: lista kontrolna wydania {#maintaining-the-release-checklist}

Przed oznaczeniem wydania (`v` + numer z `VERSION`) przejdź przez tę listę po kolei.
Dzięki niej strony, obrazki i tłumaczenia zgadzają się z kodem.

1. **Wygeneruj ponownie strony generowane.**
   - `python tools/gen_docs_reference.py` przepisuje [Dokumentację poleceń](../cli-reference.md)
     na podstawie `--help` samego programu.
     `python tools/gen_docs_reference.py --check` kończy się kodem 1, gdy zapisana strona jest
     nieaktualna.
   - `python tools/docs_diagrams.py --strings` rysuje diagramy na nowo w `docs/assets/img/`
     i przepisuje `docs/assets/i18n/en.json`, czyli listę każdej etykiety diagramu do przetłumaczenia.
2. **Wypisz, co się zmieniło od ostatniego wydania:**
   `git log --oneline v<last VERSION>..HEAD`. Każde nowe polecenie, opcja, pole wyniku
   lub zachowanie potrzebuje wiersza w `CHANGELOG.md` oraz wiersza w tabeli **Dokumentacja**
   z nazwą strony, która je opisuje. Zaktualizuj tę stronę.
3. **Zdobądź niezależną recenzję** zmienionych stron i obrazków od kogoś (albo od agenta),
   kto ich nie pisał, czytającą je jako trzy osoby: początkującego, który nigdy nie używał
   terminala, ośmiolatka i profesjonalistę. Diagramy też są sprawdzane: czytelne przy szerokości
   strony, etykiety poprawne, kolory wyjaśnione.
4. **Popraw to, co wykaże recenzja**, a potem sprawdź, czy nie wkradły się prawdziwe dane gry:
   żadnych nazw map, poziomów ani graczy, żadnych liczb z prawdziwych nagrań lub instalacji
   (używaj zastępników, np. `<map>` albo „the test level”).
5. **Przetłumacz zmienione strony na nowo.** Każda przetłumaczona strona zapisuje skrót
   angielskiej strony, z której powstała; strony, których angielskie źródło się zmieniło,
   tłumaczy się ponownie, a wraz z nimi etykiety diagramów. Potem przejrzyj każdy język: ma być
   jasny dla tych samych trzech czytelników, etykiety poprawne, słowa zgodne z interfejsem
   przeglądarki w tym języku.
6. **Wypychaj dopiero po zgodzie właściciela.** Nic nie jest wypychane ani oznaczane tagiem,
   dopóki właściciel tego nie potwierdzi.

## Tłumaczenia: polecenia {#translations-the-commands}

Strona jest przetłumaczona na 40 języków przeglądarki 3DHeat: angielski jest w `docs/`,
każdy inny język w `docs/<lang>/` z tymi samymi nazwami plików. `tools/docs_i18n.py` prowadzi
ewidencję:

```bash
python tools/docs_i18n.py hashes             # po każdej zmianie angielskiej: zapisz skrót każdej strony
python tools/docs_i18n.py svg-strings        # po każdej zmianie obrazka: etykiety do przetłumaczenia
python tools/docs_i18n.py status             # dla każdego języka: aktualne, nieaktualne, brakujące strony
python tools/docs_i18n.py todo --lang de     # niemieckie strony do (ponownego) przetłumaczenia
python tools/docs_i18n.py svg-build --lang de    # niemieckie obrazki z docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # oznacz niemieckie strony skrótem angielskiej strony
python tools/docs_i18n.py check              # kod 1, gdy skróty lub etykiety są nieaktualne
```

Tłumacz tylko to, co wypisze `todo`: zachowaj Markdown, linki, kod, nazwy plików i kolumn,
przetłumacz tytuły i opisy obrazków, a przyciski i panele przeglądarki 3DHeat nazywaj jej własnymi
słowami (z `src/i18n/locales/<lang>/`). Strony generowanej dokumentacji i obrazki terminala
pozostają po angielsku. Na stronie nieaktualne tłumaczenie to mówi i linkuje angielską stronę;
brakujące tłumaczenie wraca do angielskiego. Menu języka w nagłówku i przekierowanie strony
głównej według języka przeglądarki pochodzą z `docs/_includes/`.
