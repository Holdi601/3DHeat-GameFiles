---
title: Vývoj
nav_order: 14
lang: "cs"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Vývoj {#development}

## Rozložení {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mapa modulů {#module-map}

| Modul | Co dělá |
|---|---|
| `__main__.py` | spustí kontrolu aktualizací, potom `cli.main()` |
| `cli.py` | příkazy, `identify`, rozesílání archivů, zapisovač tratí Forza |
| `lapinput.py` | každý tvar kola na pozice; vyhledání knihovny FH Companion |
| `corridor.py` | pás na obě strany jízdy, jako rastr 4 m |
| `surfaces.py` | druhy terénu, jejich názvy částí a barvy |
| `glb.py` | zápis `.glb` (části, normály, barvy, textury, kvantizace) |
| `courseexport.py` | Forza: planární UV dlaždic, rozdělení silnice a krajnice, zapečení terénu, zvednutí dekorací |
| `forzainstall.py` | knihovny Steam a Xbox; trať Forzy, do které patří box |
| `minizip.py` | archivy ForzaTech `.minizip` a jejich seznamy názvů |
| `forzatech.py` | `.modelbin`: chunky, buffery, rozvržení, podsítě, materiály |
| `forzaterrain.py` | dlaždice terénu podle místa; třídy povrchu |
| `forzatexture.py` | vzorníky `.pb`; mapy dlaždic; zapečení terénu |
| `forzamaterial.py` | `AssetManifest.xml`; které barvy textur model používá; roční období |
| `forzaplacement.py` | umístění `.pgeo`, úrovně modelů, textury, výřezy, náhrady budov, rozpočet |
| `beamng.py` | instalace BeamNG, připojený souborový systém, scéna, terén, materiály |
| `beamngcourse.py` | export trati BeamNG |
| `beamngshape.py` | zkompilované tvary `.cdae` |
| `beamngcollada.py` | záložní čtení `.dae` |
| `acrally.py` | instalace AC Rally, etapy, umístění komponent, objem virtuální textury |
| `acrallycourse.py` | export trati AC Rally: přizpůsobení soustavy, terén, umístění |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | zapečené balíčky Unreal 5 |
| `unversioned.py` | schémata neverzovaných vlastností a jejich čtečka |
| `unrealmesh.py` | zapečené statické sítě |
| `unrealtexture.py` | textury a streamované virtuální textury |
| `oodle.py` | nalezení a volání nainstalované knihovny Oodle |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | kontejnery, bundly a sítě Unity |
| `frostbite.py` | Frostbite `.toc`, tabulky sekcí, instalační balíčky, umístění chunků, datové části |
| `frostbitebundle.py` | vnořené bundly Frostbite, manifesty bundlů, katalog úrovně, seznam úrovní |
| `frostbiteebx.py` | oddíly RIFF EBX Frostbite bez knihovny typů |
| `frostbitemesh.py` | MeshSet Frostbite a jeho chunky úrovní detailu |
| `frostbiteterrain.py` | strom streamování terénu Frostbite, stránky výšek, síť země |
| `frostbitematerial.py` | textury Frostbite (mipy BC1/BC3/BC7), sklady bloků shaderů, výběr barevné mapy |
| `frostbitedecals.py` | dekorace terénu Frostbite a zapečení země |
| `frostbitenav.py` | dlaždice navigační sítě Frostbite: povrchy, po kterých chodí vojáci |
| `frostbitelevel.py` | skupiny statických modelů Frostbite, umístění, export `level` |
| `vpk.py` | VPK Source 2 |
| `unreallandscape.py` | komponenty krajiny Unreal 5: výškové mapy do sítě země (`ue-map`) |
| `unreallevel.py` | mapy World Partition Unreal 5: výpis, struktury HLOD, voda, export `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, dlaždice terénu, `resourceDatabase.rdb` |
| `enfusionworld.py` | světy Arma Reforger: soubory `.ent`, kvádry, export `enfusion-world` |
| `forzacars.py` | každé auto Forzy v nízkém detailu do `.h3dcars` (`cars`) |

Všechny moduly jsou na GitHubu v
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Spuštění testů {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` nastavuje `testpaths = tests` a `-q`. Záleží na dvou druzích testů,
z různých důvodů:

- **Syntetické testy** vytvářejí archivy bajt po bajtu a běží kdekoli. Zamykají
  rozložení polí, která byla někdy špatně: 64bitová báze segmentu `.minizip` a její
  zarovnávací výplň, velikost bloku v pak, u hlavičky Unity u32 mezi dvěma int64,
  index VPK `0x7FFF`, rozdělení normály Forzy na x.
- **Testy na nainstalovaných hrách** běží na skutečných souborech, když je hra na
  počítači, a **přeskočí se** (nespadnou), když není. Jsou jediná věc, která chytí
  rozložení, které je správné pro malý soubor a špatné pro velký.

### Fixtures {#fixtures}

| Fixture | Vytváří |
|---|---|
| `tests/forza_fixtures.py` | archivy `.minizip` (s 64bitovou bází, výplní, smíšenými kodeky), manifesty, modely `.modelbin` a terén, vzorníky `.pb` |
| `tests/beamng_fixtures.py` | malou instalaci BeamNG: `gameengine.zip`, `content`, jeden zip úrovně s terénem 64 m, pás asfaltu, dekoraci silnice, zábradlí, prefab, položku lesa, moře, materiály a tvary `.cdae` v dokumentovaném rozložení |
| `tests/unreal_fixtures.py` | kontejner IoStore s adresářem, balíček zen, blok neverzovaných vlastností |
| `tests/frostbite_fixtures.py` | tabulky Frostbite, bundly, oddíly EBX, sítě a stránky terénu, bajt po bajtu |

### Soubory testů {#test-files}

| Soubor | Pokrývá |
|---|---|
| `test_minizip.py` | čtení zpět, 64bitová báze, liché a sudé tabulky bundlů, odmítnutí, soubor názvů |
| `test_forzatech.py` | tabulku chunků a řetěz, odmítnutí; na instalované hře: řetězy a značky skutečných modelů |
| `test_forza_geometry.py` | umístění ve světě, rozložení vrcholů, odmítnuté formáty, podsítě, normály a UV |
| `test_forzaterrain.py` | mřížka dlaždic (1023 vs 512 m), ořezání, extrakce |
| `test_forzatexture.py` | hlavička vzorníku, dekódování, police textur, zapečení terénu |
| `test_forzamaterial.py` | manifest, názvy, hashe materiálů, výběr barvy, roční období |
| `test_forzaplacement.py` | záznam `.pgeo`, umísťování kopií, úrovně, varianty, průhledné povrchy, celý box, rozpočet, barva zástupce, automatický rozpočet; na instalované hře: obruby na zemi |
| `test_forzainstall.py` | hledání hry, výběr tratě |
| `test_courseexport.py` | UV dlaždic, plán částí, zvednutí dekorací |
| `test_course_cli.py` | celé příkazy `course` a `courses` na syntetické trati; `terrain --route` s značkou pořadí bajtů a bez `bounds` |
| `test_archive_cli.py` | `identify`, `list` a `extract` na každém archivu s čtečkou (`.pak`, IoStore, `.vpk`, `.minizip` s názvy i bez nich, zip, `.cdae`, `.ter`); chyby jako jeden řádek a návratový kód: šifrovaný pak, šifrovaný kontejner, soubor, který není archiv, špatný `--key` |
| `test_corridor.py` | pás, řezání terénu jím |
| `test_lapinput.py` | každý tvar kola, box, chyby, vyhledání názvu tratě, která je to hra podle složky |
| `test_surfaces.py` | které názvy rozhodují o povrchu a které ne, názvy částí |
| `test_glb.py` | soubor je platný, uzly nesou třídu, odmítnutí, kvantizace |
| `test_beamng.py` | tvary, úroveň, kategorie, nalezení úrovně z kola, trať, záložní Collada; na instalované hře: `.cdae` vs `.dae`, každá úroveň se otevře |
| `test_acrally.py` | kontejnery, balíčky, vlastnosti, transformace, přizpůsobení soustavy, části umístěných modelů a rozpočet, virtuální textury; na instalované hře: etapy a zapečená barva povrchu |
| `test_pak.py` | patka, položky, únik velikosti bloku, odmítnutí; na instalované hře: posuny a SHA-1 |
| `test_unity.py` | odmítnutí; na instalované hře: tabulka objektů pokrývá soubor, řetězce verzí, hranice sítí |
| `test_frostbite.py` | podepsané vs obfuskované hlavičky, odmítnutí, instalační balíčky (dva balíčky se stejným číslem bloku); na instalované hře: každá tabulka, superbundly, řetězy sekcí, různá id, vzorkovaná data ze správného balíčku |
| `test_frostbitelevel.py` | id chunků spárovaná s jejich vlastním umístěním, vnořené bundly, manifesty, MeshSet se stínovou sekcí a UV, člen skupiny, konvence transformace, dvouúrovňový terén, výběr barevné mapy, chunk textury bez svých největších mipů, opakující se vzorkovač, záznamy dekorací, dekorace složená podle své alfy, list dekorace prohrává s vlastní mapou povrchu, tabulka úrovně vybraná napříč základní hrou a jejími aktualizacemi, navigační dlaždice (povrchy ponechány, spojení vynechána, odmítnutí, detailní sítě), opakující se textury zapsané s vlastními souřadnicemi, trojúhelníky řezané tam, kde se jejich textura opakuje, pro sevřený výstup, barva země z jejích povrchových materiálů, masková stránka (BC4 i nekomprimovaná) umístěná na svých čtvrtinách a odmítnutá, když se jejich okraje neshodují, stránky barevné mapy umístěné na čtvrtinách a nalezené až po maskových stránkách, které strom masek počítá, pole vzdálenosti, palety a kanálové masky nikdy nebrány jako barva, odstín bloku a šedá mapa jím obarvená, vrchol palety ve středu svého vzorníku, mřížka sklonu rozprostřená zpět bilineárně, překryv objektu nakreslený přes jeho rozbalení, blok variace klíčovaný svým hashem a dosažený přes dvojče bloku, list písma položený podle svých čtvrtých souřadnic textury přes povrch, na který se maluje, nátěr dekorace čtený z jejího materiálu a vykreslené dráhové čáry a stopy pneumatik, jednokanálové mapy dekódované, ničitelné sítě označené v svých částech a extras, blockout, kinematografické a světelné sítě vynechány a rozložení barevné mapy, které se nečte, mapy s výřezy a jejich maskované, oboustranné PNG materiály, dlaždice kulisy pojmenované podle své sítě; na instalované hře: dekorace terénu úrovně, katalog největší úrovně, sítě uvnitř svých hranic, členové skupin, vegetace stojící na dekódovaném terénu |
| `test_vpk.py` | adresář, odmítnutí, rozdělené archivy; na instalované hře: mapy se otevřou, kontroly CRC odpovídají, navigační síť |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, dlaždice terénu a soubory světa; export `enfusion-world` |
| `test_forzacars.py` | soubor `.h3dcars`, který zapisuje příkaz `cars` |
| `test_unreallevel.py` | krajiny Unreal 5, struktury HLOD, voda; export `ue-map` |

## Testy na nainstalovaných hrách {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
hledá hry pro testy. `steam_common()` vypíše `steamapps\common` každé knihovny
Steamu (včetně složek samotného Steamu) a `installed(*globs)` vrátí cesty, které
odpovídají některému vzoru pod nimi, rekurzivně tam, kde vzor obsahuje `**`. Každý
test si určí, co potřebuje:

| Test | Hledá | Přeskočí se s |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` s **nešifrovaným** indexem, až 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` v `*/*_Data` nebo `*/*/*_Data`, které čtečka přijme, až 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, až 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | okruhy knihovny kol FH Companion (start a cíl do 50 m), s nejvíce koly, které `find_track` umístí; nebo `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Spustit testy jedné hry nebo nasměrovat test obrub Forzy na konkrétní trať:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testy na nainstalovaných hrách čtou jen ze her. Do složek her nic nezapisují.
Výstupy testů jdou do dočasných složek pytestu.

## Konvence {#conventions}

- **Raději odmítnout než hádat.** Každá čtečka vyhodí vlastní výjimku
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`…) se
  zprávou, co našla a proč to nepřečetla.
- **Ověřovat vůči samotnému formátu.** Hash, CRC, řetěz posunů, uložený ohraničující
  kvádr, jízda ležící na zemi. Ne "nespadlo to".
- **Žádné klíče, žádný přibalený proprietární kód.** Viz [Pravidla a licence](rules-and-licences.md).
- **Citlivá data zůstávají venku.** Herní soubory, exporty, kola, nahrávky a
  snímky obrazovky se nikdy nedostanou do repozitáře. `.gitignore` je vylučuje
  podle složky i typu. Testy používají syntetická data a nainstalované hry, nikdy
  herní obsah uložený v repozitáři.
