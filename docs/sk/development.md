---
title: Vývoj
nav_order: 14
lang: "sk"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Vývoj {#development}

## Rozloženie {#layout}

```
heat3d_gamefiles/     balík: čítačky, exporty tratí, príkazový riadok
heat3d_update/        kontrola vydaní a aktualizátor (pozri Aktualizácie)
tests/                syntetické testy, fixtúry a testy voči nainštalovaným hrám
docs/                 táto dokumentácia (docs/wiki sa generuje z nej)
VERSION               nainštalovaná verzia, porovnávaná s vydaniami na GitHube
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Mapa modulov {#module-map}

| Modul | Čo robí |
|---|---|
| `__main__.py` | spustí kontrolu aktualizácie a potom `cli.main()` |
| `cli.py` | príkazy, `identify`, rozdeľovanie archívov, zapisovač trate Forza |
| `lapinput.py` | každý tvar kola na pozície; vyhľadávanie v knižnici FH Companion |
| `corridor.py` | pás na oboch stranách jazdy ako raster 4 m |
| `surfaces.py` | druhy povrchu, názvy ich častí a farby |
| `glb.py` | zapisovač `.glb` (časti, normály, farby, textúry, kvantizácia) |
| `courseexport.py` | Forza: planárne UV dlaždíc, rozdelenie cesta/krajnica, pečenie povrchu, zdvihnutie dekálov |
| `forzainstall.py` | knižnice Steam a Xbox; ku ktorej trati patrí box |
| `minizip.py` | archívy ForzaTech `.minizip` a ich zoznamy názvov |
| `forzatech.py` | `.modelbin`: chunky, buffery, layouty, podsiete, materiály |
| `forzaterrain.py` | dlaždice terénu podľa miesta; triedy povrchu |
| `forzatexture.py` | vzorníky `.pb`; mapy dlaždíc; pečenie povrchu |
| `forzamaterial.py` | `AssetManifest.xml`; ktoré farby textúr má model; ročné obdobia |
| `forzaplacement.py` | umiestnenia `.pgeo`, úrovne modelov, textúry, výrezy, náhrady, rozpočet |
| `beamng.py` | inštalácia BeamNG, pripojený súborový systém, scéna, terén, materiály |
| `beamngcourse.py` | export trate BeamNG |
| `beamngshape.py` | skompilované tvary `.cdae` |
| `beamngcollada.py` | záložné čítanie `.dae` |
| `acrally.py` | inštalácia AC Rally, etapy, umiestnenie komponentov, objem virtuálnych textúr |
| `acrallycourse.py` | export trate AC Rally: fit rámca, povrch, umiestnenie |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | cooked balíky Unreal 5 |
| `unversioned.py` | schémy neverzovaných vlastností a ich čítačka |
| `unrealmesh.py` | cooked statické siete |
| `unrealtexture.py` | textúry a streamované virtuálne textúry |
| `oodle.py` | hľadanie a volanie nainštalovanej knižnice Oodle |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | kontajnery Unity, zväzky, siete |
| `frostbite.py` | Frostbite `.toc`, tabuľky sekcií, inštalačné balíky, umiestnenia chunkov, dáta |
| `frostbitebundle.py` | vložené zväzky Frostbite, manifesty zväzkov, katalóg úrovne, zoznam úrovní |
| `frostbiteebx.py` | oddiely RIFF EBX Frostbite bez knižnice typov |
| `frostbitemesh.py` | MeshSet Frostbite a jeho chunky úrovní detailu |
| `frostbiteterrain.py` | stromový streaming terénu Frostbite, stránky výšok, sieť povrchu |
| `frostbitematerial.py` | textúry Frostbite (mipy BC1/BC3/BC7), depa blokov shaderov, výber farebnej mapy |
| `frostbitedecals.py` | dekály terénu Frostbite a pečenie povrchu |
| `frostbitenav.py` | dlaždice navigačnej siete Frostbite: pochôdzne plochy vojakov |
| `frostbitelevel.py` | skupiny statických modelov Frostbite, umiestnenie, export `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | komponenty krajiny Unreal 5: výškové mapy do siete povrchu (`ue-map`) |
| `unreallevel.py` | mapy Unreal 5 World Partition: výpis, štruktúry HLOD, voda, export `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, dlaždice terénu, `resourceDatabase.rdb` |
| `enfusionworld.py` | svety Arma Reforger: súbory `.ent`, boxy, export `enfusion-world` |
| `forzacars.py` | každé auto Forza v nízkom detaile do `.h3dcars` (`cars`) |

Všetky moduly sú na GitHube v
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Spúšťanie testov {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` nastavuje `testpaths = tests` a `-q`. Dva druhy testov sú dôležité, z
rôznych dôvodov:

- **Syntetické testy** stavajú archívy bajt po bajte a bežia kdekoľvek. Pevne
  určujú rozloženie polí, ktoré boli niekedy zlé: 64-bitová základňa segmentu
  `.minizip` a jej zarovnávacie výplne, escape veľkosti bloku pak, u32 medzi dvoma
  int64 v hlavičke Unity, index VPK `0x7FFF`, rozdelená x zložka normály Forza.
- **Testy na nainštalovaných hrách** bežia nad skutočnými súbormi, keď je hra
  v počítači, a **preskočia sa** (nezlyhajú), keď nie je. Sú jediná vec, ktorá
  zachytí rozloženie, správne pre malý súbor a zlé pre veľký.

### Fixtúry {#fixtures}

| Fixtúra | Vytvára |
|---|---|
| `tests/forza_fixtures.py` | archívy `.minizip` (s 64-bitovou základňou, výplňou, zmiešanými kodekmi), manifesty, modely `.modelbin` a terén, vzorníky `.pb` |
| `tests/beamng_fixtures.py` | malú inštaláciu BeamNG: `gameengine.zip`, `content`, jeden zip úrovne s terénom 64 m, pás asfaltu, dekál cesty, zábradlie, prefab, položku lesa, more, materiály a tvary `.cdae` v dokumentovanom rozložení |
| `tests/unreal_fixtures.py` | úložný priestor IoStore s adresárom, balík zen, blok neverzovaných vlastností |
| `tests/frostbite_fixtures.py` | tabuľky, zväzky, oddiely EBX, siete a stránky terénu Frostbite, bajt po bajte |

### Testovacie súbory {#test-files}

| Súbor | Pokrýva |
|---|---|
| `test_minizip.py` | čítanie späť, 64-bitová základňa, párne a nepárne tabuľky zväzkov, odmietnutia, súbor názvov |
| `test_forzatech.py` | tabuľka a reťaz chunkov, odmietnutia; na nainštalovanej hre: reťazce a značky skutočných modelov |
| `test_forza_geometry.py` | umiestnenie vo svete, rozloženie vrcholov, odmietnuté formáty, podsiete, normály a UV |
| `test_forzaterrain.py` | mriežka dlaždíc (1023 vs 512 m), orezanie, extrakcia |
| `test_forzatexture.py` | hlavička vzorníka, dekódovanie, polica textúr, pečenie povrchu |
| `test_forzamaterial.py` | manifest, názvy, hashe materiálov, výber farby, ročné obdobia |
| `test_forzaplacement.py` | záznam `.pgeo`, umiestňovanie kópií, úrovne, varianty, priehľadné plochy, celý box, rozpočet, zástupná farba, automatický rozpočet; na nainštalovanej hre: obrubníky na povrchu |
| `test_forzainstall.py` | hľadanie hry, výber trate |
| `test_courseexport.py` | UV dlaždíc, plán častí, zdvihnutie dekálov |
| `test_course_cli.py` | celé príkazy `course` a `courses` na syntetickej trati; `terrain --route` s bajtovou značkou poradia a bez `bounds` |
| `test_archive_cli.py` | `identify`, `list` a `extract` na každom archíve s čítačkou (`.pak`, IoStore, `.vpk`, `.minizip` so názvami aj bez názvov, zip, `.cdae`, `.ter`); chyby ako jeden riadok a návratový kód: šifrovaný pak, šifrovaný kontajner, súbor, ktorý nie je archív, zlý `--key` |
| `test_corridor.py` | pás, rezanie terénu týmto pásom |
| `test_lapinput.py` | každý tvar kola, box, chyby, vyhľadanie názvu kurzu, ktorá hra je v priečinku |
| `test_surfaces.py` | ktoré názvy rozhodujú o povrchu, ktoré nie, názvy častí |
| `test_glb.py` | súbor je platný, uzly nesú triedu, odmietnutia, kvantizácia |
| `test_beamng.py` | tvary, úroveň, kategórie, nájdenie úrovne z kola, trať, záložné čítanie Collada; na nainštalovanej hre: `.cdae` vs `.dae`, každá úroveň sa otvorí |
| `test_acrally.py` | kontajnery, balíky, vlastnosti, transformácie, fit rámca, časti umiestnených modelov a rozpočet, virtuálne textúry; na nainštalovanej hre: etapy a pečená farba povrchu |
| `test_pak.py` | pätka, záznamy, escape veľkosti bloku, odmietnutia; na nainštalovanej hre: offsety a SHA-1 |
| `test_unity.py` | odmietnutia; na nainštalovanej hre: tabuľka objektov pokrýva súbor, reťazce verzií, hranice sietí |
| `test_frostbite.py` | podpísané vs. zakryté hlavičky, odmietnutia, inštalačné balíky (dva balíky s rovnakým číslom bloby); na nainštalovanej hre: každá tabuľka, superzväzky, reťazce sekcií, rozdielne id, vzorkované dáta zo správneho balíka |
| `test_frostbitelevel.py` | id chunkov spárované s ich vlastnými umiestneniami, vložené zväzky, manifesty, MeshSet s tieňovou sekciou a UV, člen skupiny, konvencia transformácie, terén z dvoch úrovní, výber farebnej mapy, textúrový chunk bez svojich najväčších mipov, opakujúci sa sampler, záznamy dekálov, dekál zložený podľa svojej alfy, dekálový hárok prehrávajúci mape povrchu, vlastná mapa, výber katalógu levelu medzi základnou hrou a jej aktualizáciami, navigačné dlaždice (plochy zachované, prepojenia vynechané, odmietnutia, detailné siete), opakujúce sa textúry zapísané s vlastnými súradnicami, trojuholníky rezané tam, kde sa ich textúra opakuje, pre orezaný výstup, farba terénu z jeho povrchových materiálov, stránky masiek (BC4 a nekomprimované) umiestnené na svojich kvadrantoch a odmietnuté, keď sa ich okraje nezhodujú, stránky farebných máp umiestnené na svojich kvadrantoch a nájdené až po stránkach masiek, ktoré strom masiek počíta, distančné polia, palety a masky kanálov nikdy nevzaté ako farba, odtieň bloku a šedá mapa namaľovaná ním, vrchol palety v strede svojho vzorníka, mriežka sklonu rozložená späť bilineárne, prekrytie objektu nakreslené cez jeho rozbalenie, blok variácie kľúčovaný svojim hashom a dosiahnutý cez dvojča bloku, písmenový hárok položený podľa svojich štvrtých súradníc textúry nad povrch, na ktorý je namaľovaný, náter dekálu čítaný z jeho materiálu a nakreslené dráhové čiary a stopy pneumatík, jednokanálové mapy dekódované, ničiteľné siete označené v svojich častiach a extras, blockout, kinematografické a osvetľovacie siete vynechané a rozloženie colormap, ktoré sa nečíta, mapy orezania a ich masked, dvojstranné PNG materiály, pozadia dlaždíc pomenované podľa svojej siete; na nainštalovanej hre: terénne dekály levelu, katalóg najväčšieho levelu, siete vnútri svojich hraníc, členovia skupiny, vegetácia stojaca na dekódovanom teréne |
| `test_vpk.py` | adresár, odmietnutia, rozdelené archívy; na nainštalovanej hre: mapy sa otvoria, CRC sedia, navigačná sieť |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, dlaždice terénu a svetové súbory; export `enfusion-world` |
| `test_forzacars.py` | súbor `.h3dcars`, ktorý zapisuje príkaz `cars` |
| `test_unreallevel.py` | krajiny Unreal 5, štruktúry HLOD, voda; export `ue-map` |

## Testy na nainštalovaných hrách {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
hľadá hry pre testy. `steam_common()` vypíše `steamapps\common` každej knižnice Steam
(vrátane priečinkov samotného Steamu) a `installed(*globs)` vráti cesty zodpovedajúce
ľubovoľnému vzoru pod nimi, rekurzívne tam, kde vzor obsahuje `**`. Každý test
rozhodne, čo potrebuje:

| Test | Hľadá | Preskočí sa s hláškou |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` s **nešifrovaným** indexom, najviac 4 | „no shipped pak on this machine“ |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` v `*/*_Data` alebo `*/*/*_Data`, ktoré čítačka prijme, najviac 6 | „no Unity game on this machine“ |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | „no Frostbite game on this machine“ |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | „no Frostbite level on this machine“ |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, najviac 6 | „Counter-Strike 2 is not installed“ |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | „no Forza install on this machine“ |
| `test_forzaplacement.py` | okruhy knižnice kôl FH Companion (štart a cieľ do 50 m), s najviac kolami, ktoré `find_track` umiestni; alebo `HEAT3D_COURSE` | „no Forza install with a recorded lap library here“ |
| `test_beamng.py` | `find_install()` | „BeamNG.drive is not installed“ |
| `test_acrally.py` | `find_paks()` | „Assetto Corsa Rally is not installed“ |

Spustite testy len jednej hry alebo nasmerujte test obrubníkov Forza na trať:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testy na nainštalovaných hrách čítajú len z hier. Nič nezapisujú do priečinkov hier.
Výstupy testov idú do dočasných priečinkov pytestu.

## Konvencie {#conventions}

- **Odmietnuť namiesto hádania.** Každá čítačka vyhodí svoju výnimku
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) so
  správou, ktorá hovorí, čo sa našlo a prečo sa to neprečítalo.
- **Kontrola voči samotnému formátu.** Hash, CRC, reťaz offsetov, uložený
  ohraničujúci box, jazda ležiaca na povrchu. Nie „nespadlo to“.
- **Žiadne kľúče, žiadny patentovaný kód v balíku.** Pozri [Pravidlá a licencie](rules-and-licences.md).
- **Dôverné dáta zostávajú vonku.** Herné súbory, exporty, kolá, nahrávky a
  snímky obrazovky nikdy nejdú do repozitára. `.gitignore` ich vylučuje podľa
  priečinka aj podľa typu. Testy používajú syntetické dáta a nainštalované hry,
  nikdy obsah hry uložený v repozitári.
