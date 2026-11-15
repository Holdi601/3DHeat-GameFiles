---
title: Pravidlá a licencie
nav_order: 12
lang: "sk"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Pravidlá a licencie {#rules-and-licences}

Tri pravidlá tvoria celý nástroj. Sú to rozhodnutia o návrhu, nie len vyhlásenia.
Úplný text: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Táto stránka je záznam toho, čo licencie hovoria, nie právne poradenstvo.

## 1. Žiadne kľúče: žiadne dodávané, žiadne získavané {#no-keys-none-shipped-none-recovered}

**Nástroj číta kontajnery.** Parsovanie formátu archívu je obyčajná práca so súbormi;
FModel, UModel a AssetRipper to robia verejne už roky. Samo osebe parsovanie kontajnera
nie je obchádzanie ochrany.

**Čiara, na ktorej záleží, je šifrovanie, a je nakreslená vnútri nástroja.** Nástroj,
ktorého účelom je obísť kontrolu prístupu, je sám v dosahu zákonov proti obchádzaniu
ochrán (DMCA §1201(a)(2) sa vzťahuje na technológie, nie len na činy), aj keď nikto
nerozdistribuuje ani jeden extrahovaný súbor. Preto:

- **Žiadne dodávané kľúče.** Kľúč nie je v kóde ani v dátach.
- **Žiadne získavanie kľúčov.** Nič nehľadá kľúč v spustiteľnom súbore a nič nečíta
  pamäť iného procesu.
- **Kľúč, ktorý máte, alebo nič.** Šifrovaný Unreal `.pak` sa otvorí len s
  `--key <hex>` (v Pythone `PakArchive(path, aes_key=...)`). `pak.py` nemá žiadnu cestu
  v kóde, ktorá kľúč získa. Šifrovaný kontajner IoStore sa odmietne bez výnimky.
- **Obfuskácia sa tiež neimplementuje.** XOR-obfuskované tabuľky Frostbite držia kľúč
  v samotnom súbore, takže ide o obfuskáciu, nie o kontrolu prístupu. Aj tak sa rozpoznajú
  a odmietnu, lebo žiadny súbor po ruke nepoužíva túto formu a nebolo by voči čomu
  overiť implementáciu. Šifrovaný balík Assetto Corsa EVO sa odmieta z rovnakého dôvodu,
  aký stojí za pravidlom o kľúčoch.
- **Šifrované súbory zostávajú zatvorené.** Počiatočný súborový systém Battlefield 6,
  ktorý drží knižnicu typov hry, je šifrovaný a nečíta sa. Export levelu pracuje
  z nešifrovaných súborov a dva typy, ktoré potrebuje, zostaví z dát.
- **Nič sa nevkladá do procesu hry.** Telemetria pochádza z kanálov, ktoré hry
  zverejňujú samy, a zachytávanie používa verejné API nahrávania obrazovky (v ostatných
  nástrojoch 3DHeat). Vkladanie do titulu s anti-cheatom ohrozuje účet toho, kto ho
  spúšťa.

Každý doteraz testovaný archív bol nešifrovaný.

## 2. Vaše súbory, vaša zodpovednosť {#your-own-files-your-responsibility}

Nástroj číta herné súbory **nainštalované na vašom počítači**. Herný obsah nikdy
nesťahuje.

Čo mu ukážete, zostáva vaša zodpovednosť. Hry majú vlastné licenčné podmienky a koncové
licencie často zakazujú spätné inžinierstvo. Sú to vymáhateľné zmluvy a povinnosť nesie
ten, kto nástroj spúšťa, pri akejkoľvek hre. Žiadne rozhodnutie o návrhu tu túto
povinnosť nezbavuje. Najjasnejší legitímny prípad je vývojár, ktorý číta build vlastného
štúdia: titul iného tímu, starú vetvu, build od partnera.

## 3. Výstup nie je na ďalšie šírenie {#output-is-not-for-redistribution}

Výstup je geometria pre **priestorový kontext**: povrch, cesta a to, čo stojí vedľa nej,
zredukované na rozpočet, aby sa kolá dali analyzovať na mieste. Je to najmenej z toho,
čo archív obsahuje, a stále ide o obsah vydavateľa hry.

- Exportované `.glb` súbory aj textúry v nich si ponechajte na vlastnú analýzu.
- Exportované trate, levely, modely ani textúry nezverejňujte, nezdieľajte ani nepredávajte.
- `.gitignore` repozitára drží herné súbory, exporty, kolá a nahrávky mimo verziovania
  podľa priečinka aj podľa typu súboru (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`,
  `*.lap.json` a ďalšie).

## Oodle sa nájde, nedodáva sa {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, teraz Epic) je patentovaný a nemá redistribuovateľný build.
`oo2core_*.dll` je licencovaná produktu, ktorý ju dodáva. `oodle.py` preto načíta
knižnicu, ktorá je už v počítači, namiesto toho, aby ju niesla. Toto je usporiadanie,
ktoré licencia predpokladá, a rovnaké, aké používajú FModel a UModel. Pozri [Oodle](reader-oodle.md).

## Samotné formáty {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` Unity, `.toc` Frostbite a formáty ForzaTech sú
  nezdokumentované. Čítať ich znamená spätné inžinierstvo kontajnera. Žiadna z tu
  uvedených čítačiek nie je odvodená zo zdrojového kódu iného projektu. Pri Frostbite
  verejné popisy starších verzií (nástroje na modovanie Frosty, poznámka k formátu
  Need for Speed Heat, prednáška z GDC) dodali názvy polí a prehľad toho, čo hľadať.
  Žiadny kód sa nepreberal; každý offset bol nameraný na súboroch (pozri
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Extrahované levely sú na váš vlastný účel. Nástroj ich zapisuje na váš disk a nikam
  inam; nezverejňujte ich.
- BeamNG zverejňuje rozloženie `.cdae` a čítačka ho nasleduje.
- Valve dokumentuje VPK.
- Vlastné dáta Unreal 5 potrebujú zoznam vlastností každej triedy. Zoznamy v
  `unversioned.py` sú **len názvy a typy**, fakty o formáte, aké obsahuje
  interoperabilný súbor mapovaní. Odvodené boli z hlavičiek Unreal Engine, ktoré Epic
  sprístupňuje každému s prepojeným účtom, a overené voči dodávaným dátam. Nie je
  zahrnutý ani nevyžaduje sa žiadny zdrojový kód enginu.

## Licencia tohto nástroja {#this-tools-licence}

Všetko napísané pre tento repozitár je pod **licenciou MIT**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
používajte, menite a distribuujte, komerčne alebo nie.

Balíky tretích strán, všetky permisívne, takže exportér nemá vlastné obmedzenie:

| Balík | Licencia | Použitie |
|---|---|---|
| numpy | BSD-3-Clause | dekódovanie sietí |
| cryptography | Apache-2.0 / BSD-3-Clause | len archívy, ku ktorým máte kľúč |
| lz4 | BSD-3-Clause | archívy Forza, niektoré zväzky Unity, bloky LZ4 IoStore |
| Pillow | MIT-CMU (HPND) | textúry s blokovou kompresiou, výstup JPEG |
| msgpack | Apache-2.0 | `.cdae` BeamNG |
| zstandard | BSD-3-Clause | niekoľko `.cdae` so zstd, bloky zstd Frostbite |
| pytest | MIT | len na vývoj |

Licencie sa prečítali z metadát balíkov v septembri 2026. Ak sa podmienky komponentu
zmenili neskôr, rozhoduje zdroj.
