---
title: "Karbantartás"
nav_order: 99
lang: "hu"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Karbantartás: a kiadási ellenőrzőlista {#maintaining-the-release-checklist}

Mielőtt címkéznél egy kiadást (`v` + a `VERSION`-ben lévő szám), menj végig ezen a listán sorrendben.
Így az oldalak, az ábrák és a fordítások megfelelnek a kódnak.

1. **A generált oldalak újragenerálása.**
   - `python tools/gen_docs_reference.py` a program saját `--help` kimenetéből újraírja a
     [Parancsreferenciát](../cli-reference.md). A `python tools/gen_docs_reference.py --check` 1-es
     kóddal lép ki, amíg a commitolt oldal elavult.
   - `python tools/docs_diagrams.py --strings` újrarajzolja a `docs/assets/img/` ábráit, és
     újraírja a `docs/assets/i18n/en.json` fájlt, vagyis az összes ábrafelirat listáját, amelyet
     le kell fordítani.
2. **Sorold fel, mi változott az utolsó kiadás óta:**
   `git log --oneline v<utolsó VERSION>..HEAD`. Minden új parancsnak, kapcsolónak, kimeneti
   mezőnek vagy viselkedésnek kell egy sor a `CHANGELOG.md`-ben, és egy sor a **Dokumentáció**
   táblázatban, amely megnevezi az oldalt, ami elmagyarázza. Frissítsd azt az oldalt.
3. **Kérj független átnézést** a megváltozott oldalakról és ábrákról valakitől (vagy egy ügynöktől),
   aki nem ő írta őket, háromféle olvasóként: egy kezdőtől, aki még sosem használt terminált, egy
   nyolcévestől és egy szakembertől. Az ábrákat is ellenőrzik: oldalszélességen olvashatók, a
   feliratok helyesek, a színek magyarázata megvan.
4. **Javítsd, amit az átnézés talál**, majd ellenőrizd, hogy nem került-e be valódi játékadat: nincs
   pálya-, szint- vagy játékosnév, nincs valódi felvételekből vagy telepítésekből származó szám
   (használj helyőrzőket, például `<map>` vagy "a teszt pálya").
5. **Fordítsd újra a megváltozott oldalakat.** Minden lefordított oldal rögzíti annak az angol oldalnak
   a hash-ét, amelyből készült; ha az angol forrás megváltozott, az oldalt újra lefordítjuk, az
   ábrafeliratokkal együtt. Ezután nyelvenként nézd át: ugyanannak a három olvasónak legyen érthető,
   a feliratok legyenek helyesek, és a szavak egyezzenek a megtekintő saját felületének szavaival azon
   a nyelven.
6. **Csak a felhasználó jóváhagyása után pusholj.** Semmi nem kerül feltöltésre vagy címkézésre,
   amíg a tulajdonos nem adja rá az engedélyt.

## Fordítások: a parancsok {#translations-the-commands}

Az oldal a 3DHeat megtekintő 40 nyelvére van lefordítva: az angol az `docs/` mappában van, minden más
nyelv a `docs/<lang>/` mappában, ugyanazokkal a fájlnevekkel. A `tools/docs_i18n.py` végzi a
nyilvántartást:

```bash
python tools/docs_i18n.py hashes             # angol módosítás után: minden oldal hash-ének rögzítése
python tools/docs_i18n.py svg-strings        # ábramódosítás után: a lefordítandó feliratok
python tools/docs_i18n.py status             # nyelvenként: naprakész, elavult és hiányzó oldalak
python tools/docs_i18n.py todo --lang de     # a német oldalak, amelyeket (újra)le kell fordítani
python tools/docs_i18n.py svg-build --lang de    # német ábrák a docs/assets/i18n/svg/de.json alapján
python tools/docs_i18n.py finish --lang de   # a német oldalak megjelölése az angol hash-ükkel
python tools/docs_i18n.py check              # 1-es kilépés, ha a hash-ek vagy a feliratok elavultak
```

Csak azt fordítsd le, amit a `todo` listáz: tartsd meg a Markdownt, a linkeket, a kódot, a fájl- és
oszlopneveket; fordítsd a címeket és az ábraleírásokat; a gombokhoz és panelekhez pedig a 3DHeat
megtekintő saját szavait használd (a `src/i18n/locales/<lang>/` alatt). A generált referenciaoldalak
és a terminálábrák angolok maradnak. A webhelyen az elavult fordítás ezt jelzi, és az angol oldalra
mutat; a hiányzó oldal angolra esik vissza. A fejléc nyelvmenüjét és a főoldal böngészőnyelv szerinti
átirányítását a `docs/_includes/` adja.
