---
title: Pravidla a licence
nav_order: 12
lang: "cs"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Pravidla a licence {#rules-and-licences}

Tři pravidla určují celý nástroj. Jsou to rozhodnutí o návrhu, ne jen prohlášení o
odpovědnosti. Úplné znění: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Tato stránka je záznam toho, co licence říkají, ne právní rada.

## 1. Žádné klíče: žádné nepřibalené, žádné neobnovené {#no-keys-none-shipped-none-recovered}

**Čte kontejnery.** Parsování formátu archivu je běžná práce se soubory a FModel,
UModel a AssetRipper to dělají veřejně už léta. Samotné parsování kontejneru není
obcházení ochrany.

**Rozhodující hranice je šifrování a je nakreslená uvnitř nástroje.** Nástroj, jehož
účelem je obejít řízení přístupu, sám spadá pod zákony proti obcházení ochrany
(DMCA §1201(a)(2) se vztahuje na technologie, ne jen na činy), i když nikdo nerozšíří
ani jediný extrahovaný soubor. Proto:

- **Žádné přibalené klíče.** V kódu ani v datech není žádný klíč.
- **Žádné obnovování klíčů.** Nic nehledá klíč v programu a nic nečte paměť jiného
  procesu.
- **Klíč, který máte, nebo nic.** Šifrovaný Unreal `.pak` se otevře jen s
  `--key <hex>` (v Pythonu `PakArchive(path, aes_key=...)`). `pak.py` nemá žádnou
  cestu kódu, která by klíč získala. Šifrovaný kontejner IoStore se odmítne úplně.
- **Obfuskace se také neimplementuje.** Tabulky Frostbite obfuskované XOR nesou klíč
  v samotném souboru, takže jde o obfuskaci, ne o řízení přístupu. Přesto se
  rozpoznají a odmítnou, protože žádný soubor po ruce tuto formu nepoužívá a nebylo
  by proti čemu ověřit implementaci. Šifrovaný balíček Assetto Corsa EVO se odmítá ze
  stejného důvodu, jako platí pravidlo o klíčích.
- **Šifrované soubory zůstávají zavřené.** Počáteční souborový systém Battlefieldu 6,
  který drží typovou knihovnu hry, je šifrovaný a nečte se. Export úrovně pracuje ze
  souborů, které nejsou šifrované, a dva typy, které potřebuje, rozloží z dat.
- **Nic se nevkládá do procesu hry.** Telemetrie přichází z kanálů, které hry
  zveřejňují samy, a záznam používá veřejná API pro nahrávání obrazovky (v dalších
  nástrojích 3DHeat). Vkládání do titulu s anti-cheatem riskuje účet toho, kdo ho
  spouští.

Každý dosud testovaný archiv byl nešifrovaný.

## 2. Vlastní soubory, vlastní odpovědnost {#your-own-files-your-responsibility}

Nástroj čte herní soubory **nainstalované ve vašem počítači**. Nikdy nestahuje herní
obsah.

Co mu ukážete, zůstává vaší odpovědností. Hry mají vlastní licenční podmínky a
koncové licenční smlouvy běžně zakazují reverzní inženýrství. Jsou to vymahatelné
smlouvy a povinnost leží na tom, kdo nástroj spouští, u jakékoli hry. Žádné
rozhodnutí v návrhu ji nezbaví. Nejjasnějším oprávněným případem je vývojář, který
čte vlastní buildy svého studia: titul jiného týmu, starou větev, build od partnera.

## 3. Výstup se nerozšiřuje {#output-is-not-for-redistribution}

Co vychází, je geometrie pro **prostorový kontext**: země, silnice a to, co stojí
vedle ní, zjednodušené na rozpočet, aby se kola dala analyzovat na místě. Je to
nejmenší část toho, co archiv obsahuje, a stále je to obsah herního vydavatele.

- Exportované soubory `.glb` a textury v nich ponechte pro vlastní analýzu.
- Nezveřejňujte, nesdílejte ani neprodávejte exportované tratě, úrovně, modely ani
  textury.
- `.gitignore` repozitáře drží herní soubory, exporty, kola a nahrávky mimo správu
  verzí podle složky a typu souboru (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`,
  `*.lap.json` a další).

## Oodle se nalezne, nepřibaluje se {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nyní Epic) je proprietární a nemá žádný redistribuovatelný
build. `oo2core_*.dll` je licencovaný s produktem, který ho dodává. `oodle.py` proto
načte knihovnu, která už je v počítači, místo aby nějakou nesl. Tohle uspořádání
licence předpokládá a je stejné, jaké používají FModel a UModel. Viz [Oodle](reader-oodle.md).

## Samotné formáty {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` Unity, `.toc` Frostbite a formáty ForzaTech jsou
  nezdokumentované. Číst je znamená reverzně inženýrovat kontejner. Žádná z těchto
  čteček nevychází ze zdrojového kódu jiného projektu. U Frostbite veřejné popisy
  starších verzí (nástroje pro modding Frosty, poznámka k formátu Need for Speed Heat,
  přednáška z GDC) dodaly názvy polí a přehled, co hledat. Kód se nepřevzal; každý
  posun se změřil na souborech (viz [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Extrahované úrovně jsou pro vaše vlastní použití. Nástroj je zapisuje na váš disk
  a nikam jinam; nezveřejňujte je.
- BeamNG zveřejňuje rozložení svých `.cdae` a čtečka se jím řídí.
- Valve dokumentuje VPK.
- Zkompilovaná data vlastností Unreal 5 potřebují seznam vlastností každé třídy.
  Seznamy v `unversioned.py` jsou **jen názvy a typy**, fakta o formátu, jaká drží
  mapovací soubor pro interoperabilitu. Byly odvozeny z hlaviček Unreal Engine, které
  Epic zpřístupňuje každému s propojeným účtem, a ověřeny proti dodaným datům. Není
  zahrnut ani vyžadován žádný zdrojový kód enginu.

## Licence tohoto nástroje {#this-tools-licence}

Vše napsané pro tento repozitář je pod **licencí MIT**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
používejte, měňte, dodávejte, komerčně nebo ne.

Balíčky třetích stran, všechny povolné, takže exportér sám žádné omezení nenese:

| Balíček | Licence | Použití |
|---|---|---|
| numpy | BSD-3-Clause | dekódování sítí |
| cryptography | Apache-2.0 / BSD-3-Clause | jen archivy, ke kterým máte klíč |
| lz4 | BSD-3-Clause | archivy Forzy, některé bundly Unity, bloky LZ4 IoStore |
| Pillow | MIT-CMU (HPND) | blokově komprimované textury, výstup JPEG |
| msgpack | Apache-2.0 | `.cdae` BeamNG |
| zstandard | BSD-3-Clause | několik `.cdae` komprimovaných zstd, bloky zstd Frostbite |
| pytest | MIT | jen pro vývoj |

Licence byly přečteny z metadat balíčků v září 2026. Pokud se podmínky komponenty
později změnily, rozhoduje zdroj.
