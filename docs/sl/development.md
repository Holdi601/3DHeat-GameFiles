---
title: "Razvoj"
nav_order: 14
lang: "sl"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

## Postavitev {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Zemljevid modulov {#module-map}

| Modul | Kaj počne |
|---|---|
| `__main__.py` | zažene preverjanje posodobitev, nato `cli.main()` |
| `cli.py` | ukazi, `identify`, usmerjanje arhivov, zapisovalnik izvoza Forze |
| `lapinput.py` | vsaka oblika kroga v položaje; iskanje v knjižnici FH Companion |
| `corridor.py` | pas na vsako stran vožnje, kot raster 4 m |
| `surfaces.py` | vrste tal, njihova imena delov in barve |
| `glb.py` | zapisovalnik `.glb` (deli, normale, barve, teksture, kvantizacija) |
| `courseexport.py` | Forza: ravninske UV ploščic, delitev ceste in bankine, zapek tal, dvig nalepk |
| `forzainstall.py` | knjižnice Steam in Xbox; progo Forze, ki ji pripada škatla |
| `minizip.py` | arhivi ForzaTech `.minizip` in njihovi seznami imen |
| `forzatech.py` | `.modelbin`: chunki, medpomnilniki, postavitve, podmeshi, materiali |
| `forzaterrain.py` | ploščice terena po mestu; razredi površin |
| `forzatexture.py` | vzorci `.pb`; zemljevidi ploščic; zapek tal |
| `forzamaterial.py` | `AssetManifest.xml`; katere barve teksture ima model; letni časi |
| `forzaplacement.py` | postavitve `.pgeo`, stopnje modelov, teksture, izrezi, nadomestki stavb, proračun |
| `beamng.py` | namestitev BeamNG, nameščen sistem datotek, scena, teren, materiali |
| `beamngcourse.py` | izvoz proge BeamNG |
| `beamngshape.py` | sestavljene oblike `.cdae` |
| `beamngcollada.py` | rezerva `.dae` |
| `acrally.py` | namestitev AC Rally, etape, postavitev komponent, volumen virtualne teksture |
| `acrallycourse.py` | izvoz proge AC Rally: prilagajanje koordinatnega sistema, tla, postavitev |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 prevedeni paketi |
| `unversioned.py` | sheme lastnosti brez različic in njihov bralnik |
| `unrealmesh.py` | prevedeni statični meshi |
| `unrealtexture.py` | teksture in tokovne virtualne teksture |
| `oodle.py` | iskanje in klicanje Oodle knjižnice, nameščene na računalniku |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | kontejnerji Unity, paketi, meshi |
| `frostbite.py` | Frostbite `.toc`, tabele odsekov, namestitveni paketi, lokacije chunkov, tovor |
| `frostbitebundle.py` | vgrajeni paketi Frostbite, manifesti paketov, katalog nivojev, seznam nivojev |
| `frostbiteebx.py` | particije RIFF EBX Frostbite brez knjižnice tipov |
| `frostbitemesh.py` | MeshSet Frostbite in njegovi chunki stopenj podrobnosti |
| `frostbiteterrain.py` | drevo pretakanja terena Frostbite, strani višin, mreža tal |
| `frostbitematerial.py` | teksture Frostbite (mipi BC1/BC3/BC7), bloki senčilnikov, izbira barvne mape |
| `frostbitedecals.py` | nalepke terena Frostbite in zapek tal |
| `frostbitenav.py` | ploščice navigacijske mreže Frostbite: hodljive površine vojakov |
| `frostbitelevel.py` | skupine statičnih modelov Frostbite, postavitev, izvoz `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | komponente višinske mreže Unreal 5: višinske mape v mrežo tal (`ue-map`) |
| `unreallevel.py` | zemljevidi Unreal 5 World Partition: seznam, strukture HLOD, voda, izvoz `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, ploščice terena, `resourceDatabase.rdb` |
| `enfusionworld.py` | svetovi Arma Reforger: datoteke `.ent`, škatle, izvoz `enfusion-world` |
| `forzacars.py` | vsak avto Forze na nizki stopnji v `.h3dcars` (`cars`) |

Vsi moduli so na GitHubu v [`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Zagon testov {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` nastavi `testpaths = tests` in `-q`. Pomembni sta dve vrsti testov, iz različnih razlogov:

- **Sintetični testi** zgradijo arhive bajt za bajtom in tečejo povsod. Zaklenejo postavitve polj, ki so bile v nekem trenutku napačne: 64-bitno osnovo segmenta `.minizip` in njeno poravnalno polnilo, izbiro velikosti bloka v pak, u32 med dvema int64 v glavi Unity, indeks `0x7FFF` pri VPK, razcepljeni x normale pri Forzi.
- **Testi na nameščenih igrah** tečejo nad pravimi datotekami, kadar je igra na računalniku, in se **preskočijo** (ne spodletijo), kadar je ni. Edini so, ki ujamejo postavitev, ki je pravilna za majhno datoteko in napačna za veliko.

### Fiksture {#fixtures}

| Fiksture | Zgradijo |
|---|---|
| `tests/forza_fixtures.py` | arhive `.minizip` (s 64-bitno osnovo, polnilom, mešanimi kodeki), manifeste, modele `.modelbin` in teren, vzorce `.pb` |
| `tests/beamng_fixtures.py` | majhno namestitev BeamNG: `gameengine.zip`, `content`, en zip nivo s 64 m terena, pas asfalta, nalepko ceste, ograjo, predlogo, predmet gozda, morje, materiale in oblike `.cdae` v dokumentirani postavitvi |
| `tests/unreal_fixtures.py` | kontejner IoStore z imenikom, paket zen, blok lastnosti brez različic |
| `tests/frostbite_fixtures.py` | tabele Frostbite, paketi, particije EBX, meshi in strani terena, bajt za bajtom |

### Testne datoteke {#test-files}

| Datoteka | Pokriva |
|---|---|
| `test_minizip.py` | branje nazaj, 64-bitna osnova, sode in lihe tabele paketov, zavrnitve, datoteka imen |
| `test_forzatech.py` | tabela chunkov in veriga, zavrnitve; nameščeno: verige in oznake pravih modelov |
| `test_forza_geometry.py` | postavitev v svet, postavitev oglišč, zavrnjeni formati, podmeshi, normale in UV |
| `test_forzaterrain.py` | mreža ploščic (1023 proti 512 m), rezanje, izvlečenje |
| `test_forzatexture.py` | glava vzorca, dekodiranje, polica tekstur, zapek tal |
| `test_forzamaterial.py` | manifest, imena, zgoščene vrednosti materialov, izbira barv, letni časi |
| `test_forzaplacement.py` | zapis `.pgeo`, postavljanje kopij, stopnje, variante, prosojne površine, cela škatla, proračun, barva nadomestka, samodejni proračun; nameščeno: robniki na tleh |
| `test_forzainstall.py` | iskanje igre, izbira proge |
| `test_courseexport.py` | UV ploščic, načrt delov, dvig nalepk |
| `test_course_cli.py` | celotna ukaza `course` in `courses` na sintetični progi; `terrain --route` z oznako byte-order in brez `bounds` |
| `test_archive_cli.py` | `identify`, `list` in `extract` na vsakem arhivu z bralnikom (`.pak`, IoStore, `.vpk`, `.minizip` z in brez imen, zip, `.cdae`, `.ter`); napake kot ena vrstica in izhodna koda: šifriran pak, šifriran kontejner, datoteka, ki ni arhiv, napačen `--key` |
| `test_corridor.py` | pas, rezanje terena z njim |
| `test_lapinput.py` | vsaka oblika kroga, škatla, napake, iskanje imena proge, katera igra je mapa |
| `test_surfaces.py` | katera imena odločajo o površini, katera ne, imena delov |
| `test_glb.py` | datoteka je veljavna, vozlišča nosijo razred, zavrnitve, kvantizacija |
| `test_beamng.py` | oblike, nivo, kategorije, iskanje nivoja iz kroga, izvoz proge, rezerva Collada; nameščeno: `.cdae` proti `.dae`, vsak nivo se odpre |
| `test_acrally.py` | kontejnerji, paketi, lastnosti, transformacije, prilagajanje koordinatnega sistema, deli in proračun postavljenih modelov, virtualne teksture; nameščeno: etape in zapečena talna barva |
| `test_pak.py` | noga, vnosi, izbira velikosti bloka, zavrnitve; nameščeno: odmiki in SHA-1 |
| `test_unity.py` | zavrnitve; nameščeno: tabela predmetov prekrije datoteko, nizi različice, meje meshev |
| `test_frostbite.py` | glave z podpisom proti zakriti, zavrnitve, namestitveni paketi (dva paketa z isto številko bloba); nameščeno: vsaka tabela, nadpaketi, verige odsekov, različni ID-ji, vzorčni tovori iz pravega paketa |
| `test_frostbitelevel.py` | ID-ji chunkov v parih z lastnimi lokacijami, vgrajeni paketi, manifesti, MeshSet s senčnim odsekom in UV, član skupine, konvencija transformacije, dvonivojski teren, izbira barvne mape, teksturni chunk brez največjih mipov, ponavljajoči vzorčevalnik, zapisi nalepk, nalepka, sestavljena po alfi, list nalepk, ki izgubi proti lastni mapi površine, izbira tabele nivoja med osnovno igro in njenimi posodobitvami, navigacijske ploščice (površine ohranjene, povezave izpuščene, zavrnitve, mreže podrobnosti), ponavljajoče se teksture, zapisane s svojimi koordinatami, trikotniki, odrezani tam, kjer se tekstura ponavlja za omejen izhod, barva tal iz njihovih površinskih materialov, strani mask (BC4 in nekomprimirane), postavljene na svoje kvadrante in zavrnjene, ko se njihovi robovi ne ujemajo, strani barvnih map, postavljene na kvadrante in najdene po straneh mask, ki jih drevo mask šteje, polja razdalje, palete in kanalne maske, nikoli vzete kot barva, odtenek bloka in siva mapa, pobarvana z njim, oglišče palete v središču svojega vzorca, mreža naklona, razširjena nazaj bilinearno, prekrivni sloj predmeta, narisan skozi njegovo razvitje, blok variacije, ključen z zgoščeno vrednostjo in dosežen prek dvojnega bloka, sloj črk, položen s svojimi četrtimi teksturnimi koordinatami nad površino, na katero je naslikan, barva nalepke, prebrana iz njenega materiala, in narisani črti steze ter sledi gum, enokanalne mape dekodirane, uničljivi meshi označeni v svojih delih in dodatkih, meshi blockout, cinematic in osvetlitve izpuščeni, postavitev barvne mape, ki ni prebrana, izrezane mape in njihove maske, dvostranski materiali PNG, ploščice ozadja, poimenovane po svojem meshu; nameščeno: nalepke terena nivoja, največji katalog nivojev, mreže v mejah, člani skupin, rastlinje na dekodiranem terenu |
| `test_vpk.py` | imenik, zavrnitve, razdeljeni arhivi; nameščeno: zemljevidi se odprejo, CRC-ji se ujemajo, navigacijska mreža |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, ploščice terena in svetovne datoteke; izvoz `enfusion-world` |
| `test_forzacars.py` | datoteka `.h3dcars`, ki jo zapiše ukaz `cars` |
| `test_unreallevel.py` | krajine Unreal 5, strukture HLOD, voda; izvoz `ue-map` |

## Testi na nameščenih igrah {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
poišče igre za teste. `steam_common()` našteje mapo `steamapps\common` vsake knjižnice Steam (vključno z Steamovimi lastnimi mapami), `installed(*globs)` pa vrne poti, ki ustrezajo katerikoli vzorci pod njimi, rekurzivno tam, kjer vzorec vsebuje `**`. Vsak test sam odloči, kaj potrebuje:

| Test | Išče | Preskoči z |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` z **nešifriranim** kazalom, do 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` v `*/*_Data` ali `*/*/*_Data`, ki ju bralnik sprejme, do 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, do 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | krogi knjižnice FH Companion (začetek in konec v 50 m), tiste z največ krogi, ki jih `find_track` postavi; ali `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Zaženite samo teste ene igre ali usmerite test robnikov Forze v progo:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Testi na nameščenih igrah berejo samo iz iger. V mape iger nič ne pišejo. Izhodi testov gredo v začasne mape pytesta.

## Dogovori {#conventions}

- **Raje zavrni kot ugibaj.** Vsak bralnik sproži svojo izjemo (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError` ...) s sporočilom, ki pove, kaj je bilo najdeno in zakaj ni bilo prebrano.
- **Preverite proti samemu formatu.** Zgoščena vrednost, CRC, veriga odmikov, shranjena omejujoča škatla, tla, na katerih leži vožnja. Ne "ni se sesulo".
- **Brez ključev, brez priložene lastniške kode.** Glejte [Pravila in licence](rules-and-licences.md).
- **Zaupni podatki ostanejo zunaj.** Datoteke igre, izvozi, krogi, posnetki in posnetki zaslona nikoli ne gredo v repozitorij. `.gitignore` jih izključi po mapi in vrsti. Testi uporabljajo sintetične podatke in nameščene igre, nikoli pa ne vsebine iger, shranjene v repozitoriju.
