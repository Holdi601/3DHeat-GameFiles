---
title: Rajoitukset ja tunnetut puutteet
nav_order: 10
lang: "fi"
source: limits-and-known-gaps.md
source_hash: "02df0dd20fc9"
nav_exclude: true
search_exclude: true
---
# Rajoitukset ja tunnetut puutteet {#limits-and-known-gaps}

Mitä työkalu ei tee, mitä se tekee vain osittain ja missä sen käytös on epätasaista.
Useimmat puutteet ovat tarkoituksellisia kieltäytymisiä. Dekoodaus ilman tiedostoa,
jota vasten tarkistaa, tuottaa tulosta, joka näyttää oikealta ja ei ole.

## Pelit {#games}

| Peli | Radan vienti | Miksi ei tai kuinka pitkälle |
|---|---|---|
| Forza Horizon | kyllä | ruudun väri on tulkinta (katso alla) |
| BeamNG.drive | kyllä | ei maanpeitettä, toistuvat mallitekstuurit litistettyinä |
| Assetto Corsa Rally | kyllä | mallit tasavärisiä; ei vielä ajettu kierroksella, joka on tallennettu pelissä |
| Assetto Corsa EVO | **ei** | koko sisältö on yhdessä paketissa, joka on hämärretty avaimella, eikä tämä työkalu palauta avaimia |
| Battlefield 6 (kentän vienti, `level`) | kyllä, koko kenttä | maasto, ryhmiteltyinä ja yksittäin sijoitetut mallit ja niiden värikartat, sotilaiden navigointiverkko, leikatut kasvit; pelialueen maanväri on karkea (32 m pikseliltä tai yksi keskiväri); ei läpinäkyvyyttä eikä normaalikarttoja; tuhoutuvat mallit merkitty, niiden tuhoutuneita tiloja ei viedä |
| Unreal 5 World Partition -pelit (karttojen vienti, `ue-map`) | kyllä, koko kartta | maisema tarkasti; rakennukset kartan yksinkertaistettuina HLOD-malleina, eivät täysin yksityiskohtaisina; vesialueet; ei kasvillisuutta, tarroja tai maanväriä |
| Arma Reforger (maailman vienti, `enfusion-world`) | kyllä, koko maailma | maasto omilla väreillään ja meri; rakennukset, rekvisiitta ja kivet mallinsa laatikkoina, eivät kolmioina; puut pyynnöstä (`--trees`), laatikkoina; ei järviä, jokia tai lapsientiteettejä |
| iRacing | **ei** | radat toimitetaan suojatussa muodossa, joka ei ole tiedostojen purkamisen kohde |
| mikä tahansa muu | **ei** | ei radan lukijaa; rakenna uudelleen pelistä 3DHeat GameCapturella tai analysoi kierrokset katseluohjelman Kisa-analyysi-välilehdellä ilman rataa |

## Moottorit ja muodot {#engines-and-formats}

| Muoto | Ei toteutettu |
|---|---|
| Unreal `.pak` | versiot ennen 8:aa; pelkän polkutiivisteen hakemistot (nimiä ei voi palauttaa); merkinnät hakemiston ylivuotolistalla (ohitetaan); `.uasset`/`.umap`-sisältöjen dekoodaus paketista |
| Unreal IoStore | salatut kontit (hylätään, ei avainvalintaa); kontin listaaminen ilman hakemistoindeksiä (se ei nimeä tiedostoja); versiolliset paketit; pelkästään Nanite-mallit ja ei-sisäiset mallit; luurankomallit; ilman skeemaa olevien luokkien ominaisuudet; instanssoitujen komponenttien ominaisuudet (asettelu muuttui pelin versiossa); spline-mallit ja tarrakomponentit |
| Unity | muodot ennen 22:ta (Unity 2019 ja vanhemmat); tiedostot, joissa on upotettuja tyyppipuita; pakatut mallit; kaikki luokat paitsi `Mesh`, joten ei muunnoksia, materiaaleja tai kohtauksia; `meshes` paketilla; `list`/`extract` (käytä `meshes`) |
| Frostbite | XOR-hämärretyt taulukot; maaston kerrosgraafi (maskit luetaan noin kolmesta tarkistetusta kentästä); muut objektikuvaukset kuin mallit (pelilogiikka, efektit, äänet); mallien ryhmät, joiden tasot ovat sisäisiä; normaali- ja muut kartat, alfa muu kuin leikkaus; maaston reiät; tyyppikirjasto (salattu alkutiedostojärjestelmässä, ei kosketa); komento yksittäisten assettien listaamiseen tai purkamiseen |
| Source 2 | käännetyt assetit (`.vmdl_c`, `.vtex_c`); CS2:n navigointiverkko (versio 36) |
| ForzaTech | muut sijaintimuodot kuin neljä skaalattua lyhyttä; muut indeksimuodot kuin u16; muut tekstuurikoodit kuin 0, 9, 13; maaston varjostimen materiaalikerrokset; tangentit |
| BeamNG | taipuvat ja tarrat-mallit; animaatio; proseduraalinen maanpeite; maailman reunan ulkopuolinen maisema |
| Unreal-maisemat ja World Partition -kartat | maisemat, joiden korkeuskentät ovat käännetyissä soluissa; muokkauskerrokset ja reiät; Nanite-maisemamallit; solussa olevat täysin yksityiskohtaiset mallit; kasvillisuus; maisemamateriaalit |
| Enfusion | mallin kolmiot (`.xob`-geometria on pakattu asettelussa, jota ei lueta); `.edds` ennen DX10-otsikoita; sisäkkäisten objektien arvot maailmatiedostoissa (ohitetaan, lasketaan); lapsientiteetit; generoidut järvet ja joet; `list`/`extract` `.pak`-tiedostolle |

## Käytöstä, joka kannattaa tietää {#behaviour-worth-knowing}

- **Forzan maanväri ei ole pelin.** Paistettu tekstuuri piirretään laattakartoista,
  jotka kertovat *missä* asfaltti, lyhyt nurmi, karkea maa ja metsämaa ovat. Se
  käyttää kiinteitä värejä ja varjostusta, koska terrain-varjostimen omia materiaalikerroksia
  ei dekoodata.
- **`--no-textures` poistaa myös Forzan reunan.** Asfaltin ja reunan jako käyttää
  paistettujen karttojen mukana tulevaa asfalttimaskia. Ilman tekstuureja tiekaistat
  pysyvät kokonaisina teinä.
- **Annettu budjetti ylittyy vain reunakivistä.** Reunakiviä (ja BeamNG:n ajopintaa
  kantavia malleja) ei koskaan yksinkertaisteta tai jätetä pois millään pelillä, joten
  `--detail-budget`, joka on pienempi kuin ne maksavat, ylittyy pelkästään niiden takia;
  kaikki muu jätetään pois ensin. Katso [Yksityiskohtatasot ja budjetti](detail-budget.md).
- **Valinnat, jotka eivät koske peliä, jätetään huomiotta hiljaa**: `--season` BeamNG:lle ja
  AC Rallylle, `--track` BeamNG:lle ja AC Rallylle, `--level`/`--install` Forzalle.
- **Battlefield 6 -kentän maanväri on karkea irti sen tarroista.** Korkeuskenttä
  värjätään taustamaaston värikartasta, 32 m pikseliltä suurimmalla mip-tasolla, jonka
  kenttä toimittaa; tai, missä mikään taustakartta ei peitä aluetta, pinnan materiaalien
  keskiväristä. `--ground-texture` kertoo tämän maaston värikartalla (0,5 m pikseliltä, missä
  kentässä sellainen on) ja paistaa tiet, aukiot, kiitotien viivat, renkaanjäljet ja
  merkinnät sen päälle materiaalien maaliväreillä, missä sellainen on asetettu, ja neutraalilla
  värillä, missä ei ole; tien vaihtelumaskit jätetään pois. Peli sekoittaa pintakerroksensa
  varjostinverkossa, jota ei lueta; vienti asettaa kerrosten värit niiden maskien ja
  korkeuskentän rinteen mukaan, oman sääntönsä mukaan, ja kenttä, jonka maskisivut eivät
  sovi yhteen, saa yhden värin. Jokainen kerros on värikarttansa keskiarvo, ei sen
  tekstuuri. Katso [Frostbite](reader-frostbite.md#terrain-layers). Korkeuskentän osat eri
  resoluutioilla kohtaavat pienin askelmin.
- **Battlefield 6 -värikarttaa valitaan, ei lueta.** Varjostinlohko nimeää jokaisen
  tekstuurin, jota se näytteistää, sanomatta, mikä on väri; valinta tehdään nimen
  perusteella (katso [Frostbite](reader-frostbite.md#textures-and-materials)), ja se voi
  valita pinnan koristeen tai yksityiskohtakartan. Tarrakarttoja (`t_de_...`) häviävät
  pinnan oman kartan; kilven tarra piirrettynä paneelinaan näytti kilven neljänneksen
  kierrettynä. Etäisyyskenttiä, paletteja ja kanavamaskeja ei koskaan valita. Taustan
  rakennukset piirretään paletin väreillä; harmaat kartat saavat materiaalin sävytyksen
  viejän oman säännön mukaan, koska parametrien nimet ovat hashattuja, ja materiaali, joka
  maalaa harmaan kartan maskin läpi useilla sävyillä, saa yhden niistä.
- **Battlefield 6 -kentän maanalaisia reikiä ei leikata.** Missä kentän kävelykelpoinen maa
  kulkee korkeuskentän alla, pelin on täytynyt leikata maasto, eikä vienti tee sitä. Pois
  suljettu reikien sijainti: maaston kerrosmaskit (mikään ei ole keskittynyt sinne), sen
  67 x 67 solmun rasteri, varattu korkeusarvo (yksikään korkeussivu ei pidä 0:aa tai 65 535:tä),
  solmujen liput (kaikki samat), ja mallit tai assetit, jotka leikkaavat maan: sen alla
  sijaitsee kallio- ja jyrkänteiden malleja, eikä kentän yhdellekään assetille ole nimetty
  reikiä, tunneleita tai luolia. Kaksi rasteripuuta dekoodataan pituussarjoina mutta niitä
  ei sijoiteta, ja ne ovat se, mikä jää jäljelle (katso [Frostbite](reader-frostbite.md#terrain-layers)).
- **Battlefield 6 -objektin muunnelma saavuttaa osion kaksosten kautta.** Sijoitetun kopion
  muunnelma valitsee sen osien varjostinlohkot avaimella; missä mallilla ei ole lohkoa
  muunnelmalle, toisen mallin osan muunnelma, jonka oletuslohko on identtinen, otetaan
  (katso [Frostbite](reader-frostbite.md#textures-and-materials)). Se on viejän sääntö; osio
  ilman vaihtelevaa kaksosta säilyttää oletusilmeensä.
- **Battlefield 6 -kerrostetut materiaalit piirretään pohjansa ja yhden arkin mukaan.** Kirjaimilla
  varustettu seinäpaneeli piirretään rappauksenaan, ja kirjainarkki sen päällä; materiaalin muita
  kerroksia (ruskan peittokuva maskinsa kautta, yksityiskohta- ja sammalkartat) ei sekoiteta.
- **Navigointiverkko on tekoälyn, ei pelaajien.** Se kattaa sen, minne sotilas voi kävellä:
  maan, lattiat ja portaat sekä osan katoista, mutta ei jokaista korkeaa paikkaa. Pintojen
  väliset linkit (hypyt, tikkaat, ylitykset) jätetään pois.
- **Battlefield 6 -kenttä sisältää jokaisen pelimuodon kerroksen.** Kohteet, joita vain yksi
  muoto sijoittaa, voivat mennä päällekkäin toisen kanssa. `--skip` jättää kerroksia pois
  nimen mukaan.
- **`courses` on vain Forzalle**, ja se poimii vain kirjastokansioita nimeltä `... (course_...)`.
- **BeamNG-kierroksen koordinaatisto oletetaan** katseluohjelman `(x, z, -y)`-koordinaatistoksi,
  jonka 3DHeat-tallennin kirjoittaa. Muun tallentimen kierrokset BeamNG:n raakakoordinaatistossa
  eivät asettuisi oikein.
- **`list` ja `extract` ottavat arkistot, ei jokaista muotoa.** Ne avaavat `.pak`-tiedoston,
  IoStore-`.utoc`-tiedoston, `.vpk`-tiedoston, `.minizip`-tiedoston ja zipin. Unity-kontti
  luetaan `meshes`-komennolla, Frostbite-kenttä `level`-komennolla, ja `.cdae` tai `.ter`
  on tiedosto eikä arkisto (`identify` nimeää sen). `.minizip`, jolla ei ole vierellään
  `ChunkContentsMiniZip<n>.txt`-tiedostoa, listautuu merkintänumeroilla.
- **BeamNG-sijoitetut mallit käyttävät toistuvia tekstuureja keskiväreinä**, koska `.glb`:n
  näytteenotin rajaa ja katseluohjelma pakkaa tekstuurit atlakseen.
- **Käytännössä vain Windows.** Steam-polut `C:\Program Files` -kansion alla,
  `%LOCALAPPDATA%`, `C:\XboxGames`, ja `*_win64.dll` Oodlelle. Muita alustoja ei ole testattu.

## Todentamatta {#unverified}

- Vanhemmat Python-versiot (työkalua on ajettu versiolla 3.13).
- Assetto Corsa Rally pelissä tallennetulla kierroksella. Sitä on testattu vain synteettisillä
  kierroksilla satunnaisissa kehyksissä.
- Muut glTF-katseluohjelmat kuin 3DHeat-katseluohjelma.
- Onko kunkin pelin koordinaatisto vasen- vai oikeakätinen. Vienti säilyttää kunkin pelin
  telemetriakoordinaatiston, joten kierrokset ja radat asettuvat kohdalleen joka tapauksessa.
- `WaterBlock`-lohkon paikallisen z = 0:n merkitys pintana (BeamNG).
- Frostbite-sijoittelu muissa peleissä kuin Battlefield 6:ssa, ja Battlefield 6:ssa päivityksen
  jälkeen, joka muuttaa ryhmän jäsenen asettelua. Lukija ei silloin löydä ryhmiä ja kertoo sen.
- Vastaako Battlefield 6 -vienti pelin ilmoittamia sijainteja. Koordinaatit ovat pelin omat,
  kuten muissakin peleissä, mutta yhtään tallennetta ei ole vielä asetettu sen päälle.
