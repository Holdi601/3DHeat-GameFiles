---
title: Kehitys
nav_order: 14
lang: "fi"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Kehitys {#development}

## Rakenne {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Moduulikartta {#module-map}

| Moduuli | Mitä se tekee |
|---|---|
| `__main__.py` | suorittaa päivitystarkistuksen ja sitten `cli.main()` |
| `cli.py` | komennot, `identify`, arkiston reititys, Forzan radan kirjoittaja |
| `lapinput.py` | jokainen kierrosmuoto pisteiksi; FH Companionin kirjastohaku |
| `corridor.py` | kaista ajon kummallakin puolella 4 m:n rasterina |
| `surfaces.py` | maalajit, niiden osien nimet ja värit |
| `glb.py` | `.glb`-kirjoittaja (osat, normaalit, värit, tekstuurit, kvantisointi) |
| `courseexport.py` | Forza: tasomaiset laatta-UV:t, tie/reuna-jako, maan paistaminen, merkintöjen nosto |
| `forzainstall.py` | Steam- ja Xbox-kirjastot; Forzan rata, jonka alueeseen laatikko kuuluu |
| `minizip.py` | ForzaTech `.minizip`-arkistot ja niiden nimilistat |
| `forzatech.py` | `.modelbin`: palat, puskurit, asettelut, alimallit, materiaalit |
| `forzaterrain.py` | maalaatat paikan mukaan; pintaluokat |
| `forzatexture.py` | `.pb`-näytteet; laattakartat; maan paistaminen |
| `forzamaterial.py` | `AssetManifest.xml`; mitkä tekstuurivärit mallilla on; vuodenajat |
| `forzaplacement.py` | `.pgeo`-sijoitukset, mallin tasot, tekstuurit, leikkaukset, korvikkeet, budjetti |
| `beamng.py` | BeamNG-asennus, liitetty tiedostojärjestelmä, kohtaus, maasto, materiaalit |
| `beamngcourse.py` | BeamNG-radan vienti |
| `beamngshape.py` | `.cdae`-käännetyt muodot |
| `beamngcollada.py` | `.dae`-varamenetelmä |
| `acrally.py` | AC Rallyn asennus, vaiheet, komponenttien sijoittelu, virtuaalitekstuurin tilavuus |
| `acrallycourse.py` | AC Rallyn radan vienti: kehyksen sovitus, maa, sijoittelu |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | Unreal 5 käännetyt paketit |
| `unversioned.py` | versiottomien ominaisuuksien skeemat ja lukija |
| `unrealmesh.py` | käännetyt staattiset mallit |
| `unrealtexture.py` | tekstuurit ja suoratoistettavat virtuaalitekstuurit |
| `oodle.py` | asennetun Oodle-kirjaston etsiminen ja kutsuminen |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | Unity-kontit, paketit, mallit |
| `frostbite.py` | Frostbite `.toc`, osiotaulukot, asennuspaketit, palojen sijainnit, datat |
| `frostbitebundle.py` | Frostbiten sisäiset paketit, pakettien luettelot, tason luettelo, tasolista |
| `frostbiteebx.py` | Frostbite RIFF EBX -osiot ilman tyyppikirjastoa |
| `frostbitemesh.py` | Frostbite MeshSet ja sen yksityiskohtatasojen palat |
| `frostbiteterrain.py` | Frostbiten maaston suoratoistopuu, korkeussivut, maamalli |
| `frostbitematerial.py` | Frostbite-tekstuurit (BC1/BC3/BC7-mip-tasot), varjostinlohkojen varastot, värikartan valinta |
| `frostbitedecals.py` | Frostbiten maaston tarrat ja maan paistaminen |
| `frostbitenav.py` | Frostbiten navigointiverkkolaatat: sotilaiden kävelypinnat |
| `frostbitelevel.py` | Frostbiten staattiset mallien ryhmät, sijoittelu, `level`-vienti |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 -maisemakomponentit: korkeuskentät maamalliksi (`ue-map`) |
| `unreallevel.py` | Unreal 5 World Partition -kartat: listaus, HLOD-rakenteet, vesi, `ue-map`-vienti |
| `enfusion.py` | Enfusion `.pak`, `.edds`, maaston laatat, `resourceDatabase.rdb` |
| `enfusionworld.py` | Arma Reforger -maailmat: `.ent`-tiedostot, laatikot, `enfusion-world`-vienti |
| `forzacars.py` | jokainen Forza-auto pienellä yksityiskohdalla `.h3dcars`-tiedostoksi (`cars`) |

Kaikki moduulit ovat GitHubissa
[`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles)-kansiossa.

## Testien ajaminen {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

`pytest.ini` asettaa `testpaths = tests` ja `-q`. Kahdella tyypillä testeillä on
merkitystä, eri syistä:

- **Synteettiset testit** rakentavat arkistoja tavu tavulta ja toimivat missä tahansa.
  Ne lukitsevat kenttäasettelut, jotka olivat joskus väärin: 64-bittisen `.minizip`-
  segmentin perustan ja sen tasauksen, pakin lohkokoon eskapen, Unity-otsikon
  u32:n kahden int64:n välissä, VPK:n `0x7FFF`-indeksin ja Forzan normaalin jaetun x:n.
- **Asennettujen pelien testit** ajetaan oikeilla tiedostoilla, kun peli on koneella,
  ja ne **ohitetaan** (eivät epäonnistu), kun se ei ole. Ne ovat ainoa asia, joka
  saa kiinni asettelun, joka on oikein pienelle tiedostolle mutta väärin suurelle.

### Testikiinnitteet {#fixtures}

| Kiinnite | Rakentaa |
|---|---|
| `tests/forza_fixtures.py` | `.minizip`-arkistot (64-bittisellä perustalla, tasauksella, sekoitetuilla pakkausmenetelmillä), manifestit, `.modelbin`-mallit ja maasto, `.pb`-näytteet |
| `tests/beamng_fixtures.py` | pieni BeamNG-asennus: `gameengine.zip`, `content`, yksi tasozip 64 m:n maastolla, asfalttikaista, tieliite, kiskot, esivalmiste, meri, materiaalit ja `.cdae`-muodot dokumentoidussa asettelussa |
| `tests/unreal_fixtures.py` | IoStore-kontti hakemistolla, zen-paketti, versioton ominaisuuslohko |
| `tests/frostbite_fixtures.py` | Frostbite-taulukot, paketit, EBX-osiot, mallit ja maaston sivut, tavu tavulta |

### Testitiedostot {#test-files}

| Tiedosto | Kattaa |
|---|---|
| `test_minizip.py` | lukeminen takaisin, 64-bittinen perusta, parilliset ja parittomat pakettitaulukot, kieltäytymiset, nimitiedosto |
| `test_forzatech.py` | palataulukko ja ketju, kieltäytymiset; asennettuna: oikeiden mallien ketjut ja tunnisteet |
| `test_forza_geometry.py` | maailmasijoitus, kärkiasettelu, kielletyt muodot, alimallit, normaalit ja UV:t |
| `test_forzaterrain.py` | laattaruudukko (1023 vs 512 m), leikkaus, purku |
| `test_forzatexture.py` | näytteen otsikko, dekoodaus, tekstuurihylly, maan paistaminen |
| `test_forzamaterial.py` | manifesti, nimet, materiaalihashit, värinvalinta, vuodenajat |
| `test_forzaplacement.py` | `.pgeo`-tietue, kopioiden sijoittelu, tasot, muunnelmat, läpinäkyvät pinnat, koko laatikko, budjetti, paikkamerkin väri, automaattinen budjetti; asennettuna: reunakivet maalla |
| `test_forzainstall.py` | pelin etsiminen, radan valinta |
| `test_courseexport.py` | laatta-UV:t, osasuunnitelma, merkintöjen nosto |
| `test_course_cli.py` | koko `course`- ja `courses`-komento synteettisellä radalla; `terrain --route` tavujärjestysmerkillä ja ilman `bounds`-kenttää |
| `test_archive_cli.py` | `identify`, `list` ja `extract` jokaisella lukijan tukemalla arkistolla (`.pak`, IoStore, `.vpk`, `.minizip` nimien kanssa ja ilman, zip, `.cdae`, `.ter`); virheet yhtenä rivinä ja poistumiskoodilla: salattu pak, salattu kontti, tiedosto, joka ei ole arkisto, väärä `--key` |
| `test_corridor.py` | kaista, maaston leikkaaminen sillä |
| `test_lapinput.py` | jokainen kierrosmuoto, laatikko, virheet, radan nimen haku, mikä peli kansio on |
| `test_surfaces.py` | mitkä nimet ratkaisevat pinnan, mitkä eivät, osien nimet |
| `test_glb.py` | tiedosto on kelvollinen, solmut kantavat luokan, kieltäytymiset, kvantisointi |
| `test_beamng.py` | muodot, taso, luokat, tason löytäminen kierroksesta, rata, Collada-varamenetelmä; asennettuna: `.cdae` vs `.dae`, jokainen taso aukeaa |
| `test_acrally.py` | kontit, paketit, ominaisuudet, muunnokset, kehyksen sovitus, sijoitettujen mallien osat ja budjetti, virtuaalitekstuurit; asennettuna: vaiheet ja paistettu maaväri |
| `test_pak.py` | alatunniste, merkinnät, lohkokoon eskape, kieltäytymiset; asennettuna: siirrot ja SHA-1 |
| `test_unity.py` | kieltäytymiset; asennettuna: objektitaulukko tiilittää tiedoston, versiomerkkijonot, mallin rajat |
| `test_frostbite.py` | allekirjoitetut vs hämärretyt otsikot, kieltäytymiset, asennuspaketit (kaksi pakettia samalla blobnumerolla); asennettuna: jokainen taulukko, superpaketit, osaketjut, erilliset tunnisteet, otannan datat oikeasta paketista |
| `test_frostbitelevel.py` | tunnisteet yhdistettyinä omiin sijainteihinsa, sisäiset paketit, luettelot, MeshSet varjo-osalla ja UV:illa, ryhmän jäsen, muunnoksen sopimus, kaksitasoinen maasto, värikartan valinta, tekstuuripala, jolta puuttuvat suurimmat mip-tasot, toistuva näytteenotin, tarrojen tietueet, alfallaan koostettu tarra, pinnan oman kartan voittama tarrakartta, tason taulukon valinta pelin perus- ja päivitystiedostojen välillä, navigointilaatat (pinnat säilyvät, linkit jätetään pois, kieltäytymiset, yksityiskohtamallit), toistuvat tekstuurit kirjoitettuina omilla koordinaateillaan, kolmiot leikattuna siellä, missä niiden tekstuuri toistuu rajatulle tulosteelle, maan väri pinnan materiaaleista, maskisivut (BC4 ja pakkaamaton) sijoitettuina neljänneksilleen ja hylättyinä, kun reunat eivät täsmää, värikarttasivut sijoitettuina neljänneksilleen ja löydettyinä maskipuiden jälkeen, etäisyyskentät, paletit ja kanavamaskit eivät koskaan väriksi, lohkon sävytys ja harmaa kartta maalattuna sillä, paletin kärki näytteen keskellä, kaltevuusruudukko levitettynä takaisin bilineaarisesti, kohteen peittokuva piirrettynä sen avauksen kautta, muunnelman lohko avaimen hashin mukaan ja saavutettu kaksoislohkon kautta, kirjainarkki asetettuna neljännellä tekstuurikoordinaatillaan sen pinnan päälle, jolle se maalataan, tarran maali luettuna materiaalista, kiitotien viivat ja renkaanjäljet piirrettyinä, yksikanavaiset kartat dekoodattuina, tuhoutuvat mallit merkittyinä osissaan ja lisätiedoissaan, blockout-, elokuva- ja valaistusmallit jätetty pois sekä väriasettelu, jota ei lueta, leikkauskartat ja niiden maskatut, kaksipuoliset PNG-materiaalit, taustatason laatat nimettyinä mallinsa mukaan; asennettuna: tason maastotarrat, suurimman tason luettelo, mallit rajojensa sisällä, ryhmän jäsenet, kasvillisuus dekoodatulla maastolla |
| `test_vpk.py` | hakemisto, kieltäytymiset, jaetut arkistot; asennettuna: kartat aukeavat, CRC:t täsmäävät, navigointiverkko |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, maaston laatat ja maailmatiedostot; `enfusion-world`-vienti |
| `test_forzacars.py` | `.h3dcars`-tiedosto, jonka `cars`-komento kirjoittaa |
| `test_unreallevel.py` | Unreal 5 -maisemat, HLOD-rakenteet, vesi; `ue-map`-vienti |

## Asennettujen pelien testit {#installed-game-tests}

[`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
etsii pelejä testeille. `steam_common()` listaa jokaisen Steam-kirjaston
`steamapps\common`-kansion (myös Steamin omat kansiot), ja `installed(*globs)`
palauttaa polut, jotka täsmäävät mihin tahansa globiin sen alla, rekursiivisesti
siellä, missä globissa on `**`. Jokainen testi päättää, mitä se tarvitsee:

| Testi | Etsii | Ohittuu kun |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` joissa on **salaamaton** indeksi, enintään 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` kansioissa `*/*_Data` tai `*/*/*_Data`, joita lukija hyväksyy, enintään 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, enintään 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | FH Companionin kirjaston radat (lähtö ja maali 50 m:n sisällä), joissa on eniten kierroksia, jotka `find_track` sijoittaa; tai `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Vain yhden pelin testit, tai Forzan reunakivitesti osoittamaan radalle:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Asennettujen pelien testit lukevat vain pelistä. Ne eivät kirjoita mitään pelikansioihin.
Testien tulokset menevät pytestin väliaikaiskansioihin.

## Käytännöt {#conventions}

- **Kieltäydy sen sijaan, että arvaat.** Jokainen lukija nostaa oman poikkeuksensa
  (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`,
  `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError` ...), jossa
  kerrotaan, mitä löytyi ja miksi sitä ei luettu.
- **Tarkista muodon omaa vastaan.** Tiiviste, CRC, siirrosketju, tallennettu
  rajauslaatikko, maan päällä oleva ajo. Ei "se ei kaatunut".
- **Ei avaimia, ei suljettua koodia mukana.** Katso [Säännöt ja lisenssit](rules-and-licences.md).
- **Luottamukselliset tiedot pysyvät poissa.** Pelitiedostot, viennit, kierrokset,
  tallenteet ja kuvakaappaukset eivät koskaan mene repositorioon. `.gitignore` sulkee
  ne pois kansioittain ja tyypeittäin. Testit käyttävät synteettistä dataa ja
  asennettuja pelejä, eivät tarkistettuja pelisisältöjä.
