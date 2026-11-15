---
title: Pravila i licence
nav_order: 12
lang: "hr"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Pravila i licence {#rules-and-licences}

Tri pravila oblikuju cijeli alat. To su dizajnerske odluke, a ne samo izjave o odricanju.
Puni tekst: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Ova stranica je zapis onoga što licence kažu, a ne pravni savjet.

## 1. Nema ključeva: nijedan se ne isporučuje, nijedan se ne izvlači {#no-keys-none-shipped-none-recovered}

**Alat čita spremnike.** Parsiranje formata arhive je običan rad s datotekama, a FModel, UModel i
AssetRipper to godinama rade javno. Samo parsiranje spremnika nije zaobilaženje zaštite.

**Crta koja je važna je šifriranje, i povučena je unutar alata.** Alat čija je svrha zaobići
kontrolu pristupa sam je u dosegu zakona protiv zaobilaženja zaštite (DMCA §1201(a)(2) obuhvaća
tehnologije, a ne samo radnje), čak i kad nitko ne distribuira ni jednu izvučenu datoteku. Zato:

- **Nema ugrađenih ključeva.** Nijedan ključ nije u kodu ni u podacima.
- **Nema izvlačenja ključeva.** Ništa ne traži ključ u izvršnoj datoteci i ništa ne čita memoriju
  tuđeg procesa.
- **Ključ koji imate, ili ništa.** Šifrirani Unreal `.pak` se otvara samo uz `--key <hex>` (u
  Pythonu, `PakArchive(path, aes_key=...)`). `pak.py` nema puta u kodu koji dobiva ključ. Šifrirani
  IoStore spremnik se odbija bez iznimke.
- **Ni zamaskiranje nije implementirano.** Frostbiteove tablice zaštićene XOR-om čuvaju ključ u
  samoj datoteci, pa su zamaskiranje, a ne kontrola pristupa. Ipak se prepoznaju i odbijaju, jer
  nijedna datoteka pri ruci ne koristi taj oblik i nema se s čim provjeriti implementacija.
  Zaštićeni paket Assetto Corsa EVO odbija se iz istog razloga zbog kojeg postoji pravilo o ključevima.
- **Šifrirane datoteke ostaju zatvorene.** Početni datotečni sustav Battlefield 6, koji sadrži
  biblioteku tipova igre, je šifriran i ne čita se. Izvoz razine radi iz datoteka koje nisu šifrirane
  i iz podataka slaže dva tipa koja su mu potrebna.
- **Ništa se ne ubacuje u proces igre.** Telemetrija dolazi iz izvora koje same igre objavljuju, a
  snimanje koristi javne API-je za snimanje zaslona (u drugim 3DHeat alatima). Ubacivanje u naslov s
  anti-cheat zaštitom ugrožava račun onoga tko ga pokreće.

Svaki arhiv testiran do sada je nešifriran.

## 2. Vaše datoteke, vaša odgovornost {#your-own-files-your-responsibility}

Alat čita datoteke igara **instalirane na vašem računalu**. Nikad ne preuzima sadržaj igara.

Što predate ostaje vaša odgovornost. Igre nose vlastite uvjete licence, a EULA-e uobičajeno
zabranjuju obrnuto inženjerstvo. To su provedivi ugovori, a obveza pada na onoga tko pokreće
alat, za koju god igru. Nijedna dizajnerska odluka ovdje to ne ukida. Najjasniji legitimni slučaj
je razvojni programer koji čita build vlastitog studija: naslov drugog tima, stara grana, build od
partnera.

## 3. Izlaz nije za distribuciju {#output-is-not-for-redistribution}

Ono što izlazi je geometrija za **prostorni kontekst**: tlo, cesta i ono što stoji uz nju,
smanjeno na proračun, da se krugovi mogu analizirati na mjestu. To je najmanje od onoga što arhiv
sadrži, a i dalje je sadržaj izdavača igre.

- Zadržite izvezene `.glb` datoteke, i teksture u njima, za vlastitu analizu.
- Ne objavljujte, ne dijelite i ne prodajte izvezene staze, razine, modele ni teksture.
- `.gitignore` repozitorija drži datoteke igara, izvoze, krugove i snimke izvan verzioniranja po mapi
  i po vrsti (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` i još).

## Oodle se nalazi, ne isporučuje {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, sada Epic) je vlasnički i nema biblioteke za redistribuciju. `oo2core_*.dll`
je licenciran proizvodu koji ga isporučuje. Zato `oodle.py` učitava biblioteku koja je već na
računalu, umjesto da je nosi sa sobom. To je uređenje koje licenca predviđa i isto kakvo koriste
FModel i UModel. Vidi [Oodle](reader-oodle.md).

## Sami formati {#the-formats-themselves}

- `.pak`, IoStore, Unityjev `SerializedFile`, Frostbiteov `.toc` i ForzaTechovi formati su
  nedokumentirani. Čitanje njih je obrnuto inženjerstvo spremnika. Nijedan čitač ovdje nije izveden iz
  tuđeg izvornog koda. Za Frostbite su javni opisi starijih verzija (alati za modding Frosty, bilješka
  o formatu Need for Speed Heat, GDC predavanje) dali nazive polja i popis onoga što treba tražiti.
  Kod nije preuzet; svaki pomak je izmjeren na datotekama (vidi
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Izvučene razine su za vašu vlastitu upotrebu. Alat ih zapisuje na vaš disk i nigdje drugdje; ne
  objavljujte ih.
- BeamNG objavljuje svoj raspored `.cdae`, a čitač ga slijedi.
- Valve dokumentira VPK.
- Pečeni podaci svojstava Unreal 5 trebaju popis svojstava svake klase. Popisi u `unversioned.py` su
  **samo imena i tipovi**, činjenice o formatu kakve drži datoteka za međusobno mapiranje. Izvedeni su
  iz zaglavlja Unreal Enginea koja Epic stavlja na raspolaganje svakome s povezanim računom, i
  provjereni prema isporučenim podacima. Nema izvornog koda motora niti je potreban.

## Licenca ovog alata {#this-tools-licence}

Sve što je napisano za ovaj repozitorij je pod **MIT licencom**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): koristite ga,
mijenjate, isporučujete, komercijalno ili ne.

Paketi trećih strana, svi permisivni, pa izvoznik nema vlastito ograničenje:

| Paket | Licenca | Za što |
|---|---|---|
| numpy | BSD-3-Clause | dekodiranje mreža |
| cryptography | Apache-2.0 / BSD-3-Clause | samo arhive za koje imate ključ |
| lz4 | BSD-3-Clause | Forza arhive, neki Unity paketi, LZ4 blokovi IoStorea |
| Pillow | MIT-CMU (HPND) | teksture s blok kompresijom, JPEG izlaz |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | nekoliko zstd komprimiranih `.cdae`, zstd blokovi Frostbitea |
| pytest | MIT | samo za razvoj |

Licence su očitane s metapodataka paketa u rujnu 2026. Gdje su se uvjeti komponente kasnije
promijenili, mjerodavan je izvor.
