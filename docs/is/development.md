---
title: "Þróun"
nav_order: 14
lang: "is"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Þróun {#development}

## Uppbygging {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Einingakort {#module-map}

| Eining | Hvað hún gerir |
|---|---|
| `__main__.py` | keyrir uppfærsluathugun, síðan `cli.main()` |
| `cli.py` | skipanirnar, `identify`, val á skjalasafni, Forza brautarritarinn |
| `lapinput.py` | hvert hringform í staðsetningar; uppfletting í FH Companion safni |
| `corridor.py` | bandið beggja vegna við aksturinn, sem 4 m raster |
| `surfaces.py` | gerðir jarðarinnar, heiti hluta þeirra og litir |
| `glb.py` | `.glb` ritarinn (hlutar, normalar, litir, áferðir, magngreining) |
| `courseexport.py` | Forza: flatar UV flísanna, skipting vegar/vegaxlar, jarðarbakstur, lyfting límmiða |
| `forzainstall.py` | Steam og Xbox söfn; Forza brautin sem kassi tilheyrir |
| `minizip.py` | ForzaTech `.minizip` skjalasöfn og nafnalistar þeirra |
| `forzatech.py` | `.modelbin`: bitar, biðminni, uppsetningar, undirnet, efni |
| `forzaterrain.py` | landflísar eftir stað; yfirborðsflokkar |
| `forzatexture.py` | `.pb` sýnishorn; flísakort; jarðarbakstur |
| `forzamaterial.py` | `AssetManifest.xml`; hvaða áferðarlitir lita líkan; árstíðir |
| `forzaplacement.py` | `.pgeo` staðsetningar, stig líkana, áferðir, útklippur, staðgenglar, kostnaðarhámarkið |
| `beamng.py` | BeamNG uppsetning, tengt skráakerfi, sena, land, efni |
| `beamngcourse.py` | BeamNG brautarútflutningurinn |
| `beamngshape.py` | `.cdae` þýdd form |
| `beamngcollada.py` | `.dae` varaleið |
| `acrally.py` | AC Rally uppsetning, sérleiðir, staðsetning íhluta, rúmmál sýndaráferðar |
| `acrallycourse.py` | AC Rally brautarútflutningurinn: ásamátun, jörð, staðsetning |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 bakaðir pakkar |
| `unversioned.py` | skemu óútgefinna eiginda og lesari |
| `unrealmesh.py` | bökuð kyrrstæð net |
| `unrealtexture.py` | áferðir og streymandi sýndaráferðir |
| `oodle.py` | að finna og kalla í uppsett Oodle safn |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity ílát, búnt, net |
| `frostbite.py` | Frostbite `.toc`, kaflatöflur, uppsetningarpakkar, staðsetningar bita, farmur |
| `frostbitebundle.py` | Frostbite innbyggð búnt, skrár búnta, skrá borðs, borðalistinn |
| `frostbiteebx.py` | Frostbite RIFF EBX skipt svæði án gerðasafns |
| `frostbitemesh.py` | Frostbite MeshSet og smáatriðastigsbitar þess |
| `frostbiteterrain.py` | Frostbite streymitré lands, hæðarsíður, jarðarnetið |
| `frostbitematerial.py` | Frostbite áferðir (BC1/BC3/BC7 mip), skuggablokkasöfn, val á litakorti |
| `frostbitedecals.py` | Frostbite límmiðar á landi og jarðarbakstur |
| `frostbitenav.py` | Frostbite leiðarnetsflísar: göngufletir hermannanna |
| `frostbitelevel.py` | Frostbite hópar kyrrstæðra líkana, staðsetning, `level` útflutningurinn |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 landslagsíhlutir: hæðarkort í jarðarnetið (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition borð: listun, HLOD uppbyggingar, vatn, `ue-map` útflutningurinn |
| `enfusion.py` | Enfusion `.pak`, `.edds`, landflísar, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger heimar: `.ent` skrár, kassar, `enfusion-world` útflutningurinn |
| `forzacars.py` | allir Forza bílar á lágum smáatriðum í `.h3dcars` (`cars`) |

Allar einingar eru á GitHub undir
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Prófin keyrð {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` setur `testpaths = tests` og `-q`. Tvær gerðir prófa skipta máli, af
ólíkum ástæðum:

- **Gerviprófin** (synthetic) smíða skjalasöfn bæti fyrir bæti og keyra hvar sem er. Þau festa í sessi
  uppröðun reita sem voru einhvern tíma röng: 64 bita `.minizip` bútagrunninn
  og fyllingu hans, undankomuleið blokkastærðar í pak, u32 í Unity hausnum milli tveggja int64,
  VPK `0x7FFF` vísinn, skiptan x í normal Forza.
- **Prófin á uppsettum leikjum** keyra á raunverulegu skránum þegar leikurinn er á
  tölvunni, og **sleppa** (þau mistakast ekki) þegar hann er það ekki. Þau eru það eina sem
  nær uppröðun sem er rétt fyrir litla skrá og röng fyrir stóra.

### Prófunargögn (fixtures) {#fixtures}

| Prófunargögn | Smíða |
|---|---|
| `tests/forza_fixtures.py` | `.minizip` skjalasöfn (með 64 bita grunni, fyllingu, blönduðum þjöppunum), skrár, `.modelbin` líkön og land, `.pb` sýnishorn |
| `tests/beamng_fixtures.py` | litla BeamNG uppsetningu: `gameengine.zip`, `content`, eitt borðs-zip með 64 m landi, malbiksræmu, vegamerkingu, rimlahandriði, prefab, skógarhlut, sjónum, efnum og `.cdae` form í skjalfestu uppröðuninni |
| `tests/unreal_fixtures.py` | IoStore ílát með möppu, zen pakka, óútgefna eigindablokk |
| `tests/frostbite_fixtures.py` | Frostbite töflur, búnt, EBX svæði, net og landsíður, bæti fyrir bæti |

### Prófskrár {#test-files}

| Skrá | Nær yfir |
|---|---|
| `test_minizip.py` | lestur til baka, 64 bita grunninn, oddatölu- og sléttatölutöflur búnta, höfnun, nafnaskrána |
| `test_forzatech.py` | bitatöfluna og keðjuna, höfnun; uppsett: keðjur og merki raunverulegra líkana |
| `test_forza_geometry.py` | heimsstaðsetningu, hnútauppröðun, hafnað snið, undirnet, normala og UV |
| `test_forzaterrain.py` | flísanetið (1023 á móti 512 m), klippingu, útdrátt |
| `test_forzatexture.py` | haus sýnishorns, afkóðun, áferðarhilluna, jarðarbakstur |
| `test_forzamaterial.py` | skrána, nöfn, tætigildi efnis, litavalið, árstíðir |
| `test_forzaplacement.py` | `.pgeo` færsluna, staðsetningu eintaka, stig, afbrigði, gegnsæja fleti, heilan kassa, kostnaðarhámarkið, staðgengilslitinn, sjálfvirka hámarkið; uppsett: kantsteina á jörðinni |
| `test_forzainstall.py` | að finna leikinn, val á braut |
| `test_courseexport.py` | UV flísa, hlutaáætlunina, lyftingu límmiða |
| `test_course_cli.py` | allar skipanirnar `course` og `courses` á gerviraut; `terrain --route` með bætaröðunarmerki, og án `bounds` |
| `test_archive_cli.py` | `identify`, `list` og `extract` á hverju skjalasafni sem hefur lesara (`.pak`, IoStore, `.vpk`, `.minizip` með og án nafna, zip, `.cdae`, `.ter`); bilanir sem ein lína og útgangskóði: dulkóðað pak, dulkóðað ílát, skrá sem er ekki skjalasafn, rangur `--key` |
| `test_corridor.py` | bandið, að skera land með því |
| `test_lapinput.py` | hvert hringform, kassann, bilanir, uppflettingu heita brauta, hvaða leikur mappa er |
| `test_surfaces.py` | hvaða nöfn ráða yfirborði, hver ekki, heiti hluta |
| `test_glb.py` | skráin er gild, hnútar bera flokkinn, höfnun, magngreining |
| `test_beamng.py` | form, borðið, flokka, að finna borðið út frá hring, brautina, Collada varaleiðina; uppsett: `.cdae` á móti `.dae`, hvert borð opnast |
| `test_acrally.py` | ílát, pakka, eigindir, hnitabreytingar, ásamátunina, hluta staðsettra líkana og hámarkið, sýndaráferðir; uppsett: sérleiðir og bakaðan jarðlit |
| `test_pak.py` | fót, færslur, undankomuleið blokkastærðar, höfnun; uppsett: hliðranir og SHA-1 |
| `test_unity.py` | höfnun; uppsett: hlutataflan flísar skrána, útgáfustrengi, mörk neta |
| `test_frostbite.py` | undirrituð á móti hulin hausa, höfnun, uppsetningarpakka (tveir pakkar með sama blobbanúmer); uppsett: hver tafla, ofurbúnt, kaflakeðjur, aðgreind auðkenni, sýnatökufarmur úr réttum pakka |
| `test_frostbitelevel.py` | bitaauðkenni pöruð við eigin staðsetningar, innbyggð búnt, skrár, MeshSet með skuggakafla og UV, hópmeðlim, hnitabreytingasamkomulagið, tveggja stiga land, val á litakorti, áferðarbita sem vantar stærstu mip, endurtekna sýnatakann, límmiðafærslur, límmiða sem er settur saman með alfa sínu, límmiðablað sem tapar fyrir eigin korti yfirborðs, töflu borðsins valda yfir grunnleikinn og uppfærslur hans, leiðarnetsflísar (fletir geymdir, tengingar sleppt, höfnun, smáatriðanet), endurteknar áferðir skrifaðar með eigin hnitum, þríhyrninga skorna þar sem áferð þeirra endurtekur sig fyrir klemmt úttak, lit jarðarinnar úr yfirborðsefnum hennar, grímusíður (BC4 og óþjappaðar) settar á fjórðunga sína og hafnað þegar jaðrar þeirra ósammála, litakortasíður settar á fjórðunga sína og fundnar á eftir grímusíðunum sem grímutréð telur, fjarlægðarsvið, litaspjöld og rásagrímur aldrei tekin sem litur, lit blokkar og grátt kort málað með honum, litaspjaldshnút við miðju litasýnis síns, hallanetið breitt aftur út tvílínulega, yfirlag hlutar teiknað í gegnum útflettingu hans, blokk afbrigðis lykluð með tætigildi sínu og náð í gegnum tvíburablokk, stafablað lagt á með fjórðu áferðarhnitum yfir yfirborðið sem það er málað á, málningu límmiða lesna úr efni hans og flugbrautarlínur og hjólför teiknuð, einrása kort afkóðuð, eyðanleg net merkt í hlutum þeirra og aukagögnum, blockout, kvikmynda- og lýsinganet sleppt og litakortauppsetningu sem er ekki lesin, útklippukort og grímuð, tvíhliða PNG efni þeirra, bakgrunnsflísar nefndar eftir neti sínu; uppsett: límmiða lands á borðinu, skrá stærsta borðsins, net innan marka sinna, hópmeðlimi, gróður sem stendur á afkóðaða landinu |
| `test_vpk.py` | möppuna, höfnun, skipt skjalasöfn; uppsett: kort opnast, CRC passa, leiðarnetið |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, landflísar og heimsskrár; `enfusion-world` útflutninginn |
| `test_forzacars.py` | `.h3dcars` skrána sem `cars` skipunin skrifar |
| `test_unreallevel.py` | Unreal 5 landslag, HLOD uppbyggingar, vatn; `ue-map` útflutninginn |

## Próf á uppsettum leikjum {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
finnur leiki fyrir prófin. `steam_common()` listar `steamapps\common` í hverju Steam-safni
(eigin möppur Steam meðtaldar), og `installed(*globs)`
skilar slóðunum sem passa við eitthvert glob undir þeim, endurkvæmt þar sem glob hefur
`**`. Hvert próf ákveður hvað það þarf:

| Próf | Leitar að | Sleppir með |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` með **ódulkóðuðum** vísi, allt að 4 | „no shipped pak on this machine“ |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` í `*/*_Data` eða `*/*/*_Data` sem lesarinn tekur við, allt að 6 | „no Unity game on this machine“ |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | „no Frostbite game on this machine“ |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | „no Frostbite level on this machine“ |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, allt að 6 | „Counter-Strike 2 is not installed“ |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | „no Forza install on this machine“ |
| `test_forzaplacement.py` | hringbrautir í FH Companion safninu (byrjun og endir innan 50 m), með flesta hringi, sem `find_track` staðsetur; eða `HEAT3D_COURSE` | „no Forza install with a recorded lap library here“ |
| `test_beamng.py` | `find_install()` | „BeamNG.drive is not installed“ |
| `test_acrally.py` | `find_paks()` | „Assetto Corsa Rally is not installed“ |

Keyrðu aðeins próf eins leiks, eða beindu Forza kantsteinaprófinu að braut:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Prófin á uppsettum leikjum lesa aðeins úr leikjunum. Þau skrifa ekkert í leikjamöppur.
Úttak prófa fer í tímabundnar möppur pytest.

## Venjur {#conventions}

- **Neita frekar en að giska.** Hver lesari kastar eigin undantekningu
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) með
  skilaboðum sem segja hvað fannst og hvers vegna það var ekki lesið.
- **Prófaðu á sniðinu sjálfu.** Tætigildi, CRC, keðja hliðrana, geymdur
  umlykjandi kassi, aksturinn liggjandi á jörðinni. Ekki „það hrundi ekki“.
- **Engir lyklar, enginn séreignarkóði sendur með.** Sjá [Reglur og leyfi](rules-and-licences.md).
- **Trúnaðargögn haldast úti.** Leikjaskrár, útflutningur, hringir, upptökur og
  skjámyndir fara aldrei í geymsluna. `.gitignore` útilokar þau eftir möppu
  og gerð. Prófin nota gervigögn og uppsetta leiki, aldrei innritað efni úr leikjum.
