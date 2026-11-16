---
title: "Pravila i licence"
nav_order: 12
lang: "bs"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Pravila i licence {#rules-and-licences}

Tri pravila oblikuju cijeli alat. Puni tekst:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Bez ključeva: nijedan se ne isporučuje, nijedan se ne otkriva {#no-keys-none-shipped-none-recovered}

**Čita kontejnere.** Parsiranje formata arhive je obična obrada datoteka, a
FModel, UModel i AssetRipper rade to javno godinama.

**Linija koja je bitna je šifriranje, i povučena je unutar alata.**

- **Nema priloženih ključeva.** Nijedan ključ nije u kodu ni u podacima.
- **Nema otkrivanja ključeva.** Ništa ne traži ključ u izvršnoj datoteci i ništa
  ne čita memoriju drugog procesa.
- **Ključ koji posjedujete, ili ništa.** Šifrirani Unreal `.pak` otvara se samo
  s `--key <hex>` (u Pythonu, `PakArchive(path, aes_key=...)`). `pak.py` nema
  putanju koda koja dobija ključ. Šifrirani IoStore kontejner se odbija odmah.
- **Obfuskacija također nije implementirana.** Frostbiteove XOR-obfuscirane
  tablice drže svoj ključ u samoj datoteci, pa su obfuskacija, a ne kontrola
  pristupa. Ipak se otkrivaju i odbijaju, jer nijedna dostupna datoteka ne koristi
  taj oblik i ne bi bilo ničega naspram čega bi se implementacija provjerila.
  Keyed paket Assetto Corsa EVO odbija se iz istog razloga zbog kojeg pravilo o
  ključevima postoji.
- **Šifrirane datoteke ostaju zatvorene.** Početni datotečni sistem Battlefield 6,
  koji drži biblioteku tipova igre, je šifriran i ne čita se. Izvoz nivoa radi iz
  datoteka koje nisu šifrirane i iz podataka slaže dva tipa koja su mu potrebna.
- **Ništa se ne ubacuje u proces igre.** Telemetrija dolazi iz feedova koje igre
  same objavljuju, a snimanje koristi javne API-je za snimanje ekrana (u drugim
  3DHeat alatima). Ubacivanje u naslov s anti-cheatom riskira račun onoga ko ga
  pokrene.

Svaka dosad testirana arhiva je nešifrirana.

## 2. Vaše vlastite datoteke {#your-own-files}

Alat čita datoteke igre **instalirane na vašem računaru**. Nikad ne preuzima
sadržaj igre.

Ništa iz igre ne isporučuje se s njim: nikakav sadržaj igre, nikakav kod igre,
nikakvi DLL-ovi. Ono što izveze upisuje se na vaš disk i nigdje drugo.

3DHeat GameFiles nije povezan ni sa jednim izdavačem igara niti ga on podržava.
Igre i povezani nazivi i žigovi pripadaju svojim vlasnicima. Nosioci prava:
otvorite issue na
[github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) -
brzo odgovaramo i na zahtjev uklanjamo bilo šta.

## 3. Izlaz nije za redistribuciju {#output-is-not-for-redistribution}

Ono što izlazi je geometrija za **prostorni kontekst**: tlo, cesta i ono što
stoji pored nje, decimirano na budžet, da se krugovi mogu analizirati na mjestu.
To je najmanje od onoga što arhiva drži, a ipak je to sadržaj izdavača igre.

- Čuvajte izvezene `.glb` datoteke, i teksture u njima, za vlastitu analizu.
- Ne objavljujte, ne dijelite i ne prodajte izvezene staze, nivoe, modele ili
  teksture.
- `.gitignore` repozitorija drži datoteke igara, izvoze, krugove i snimke van
  kontrole verzija po folderu i po tipu datoteke (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` i više).

## Oodle se pronalazi, ne prilaže {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, sada Epic) je vlasnički i nema build koji se smije
redistribuirati. `oo2core_*.dll` je licenciran proizvodu koji ga isporučuje.
`oodle.py` zato učitava biblioteku koja je već na računaru umjesto da nosi svoju.
To je dogovor koji licenca predviđa, isti koji koriste FModel i UModel.
Pogledajte [Oodle](reader-oodle.md).

## Sami formati {#the-formats-themselves}

- `.pak`, IoStore, Unityjev `SerializedFile`, Frostbiteov `.toc` i ForzaTech
  formati nisu dokumentirani. Nijedan čitač ovdje nije izveden iz izvornog koda drugog projekta.
  Za Frostbite, javni opisi starijih verzija (Frosty modding alati, bilješka o
  formatu Need for Speed Heat, GDC predavanje) dali su imena polja i mapu onoga
  što treba tražiti. Nikakav kod nije preuzet; svaki pomak je izmjeren na
  datotekama (pogledajte [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Izvučeni nivoi su za vašu vlastitu upotrebu. Alat ih piše na vaš disk i
  nigdje drugdje; ne objavljujte ih.
- BeamNG objavljuje raspored svog `.cdae`, i čitač ga slijedi.
- Valve dokumentira VPK.
- Pečeni podaci svojstava Unreala 5 trebaju listu svojstava svake klase. Liste u
  `unversioned.py` su **samo imena i tipovi**, činjenice o formatu kakve drži
  datoteka mapiranja za interoperabilnost. Izvedene su iz zaglavlja Unreal Enginea
  koja Epic daje na raspolaganje svakome s povezanim računom, i provjerene naspram
  isporučenih podataka. Nikakav izvorni kod enginea nije uključen niti potreban.

## Licenca ovog alata {#this-tools-licence}

Sve napisano za ovaj repozitorij je pod **MIT licencom**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
koristite ga, mijenjajte, isporučujte, komercijalno ili ne.

Paketi trećih strana, svi permisivni, pa izvoznik ne nosi nikakvo vlastito
ograničenje:

| Paket | Licenca | Koristi se za |
|---|---|---|
| numpy | BSD-3-Clause | dekodiranje mreža |
| cryptography | Apache-2.0 / BSD-3-Clause | samo arhive za koje posjedujete ključ |
| lz4 | BSD-3-Clause | Forza arhive, neki Unity bundlovi, IoStore LZ4 blokovi |
| Pillow | MIT-CMU (HPND) | blokovski komprimirane teksture, JPEG izlaz |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | rijetki zstd-komprimirani `.cdae`, Frostbite zstd blokovi |
| pytest | MIT | samo razvoj |

Licence su očitane iz metapodataka paketa u septembru 2026. Gdje su se uslovi
komponente promijenili poslije toga, mjerodavan je izvor.
