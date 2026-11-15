---
title: "Frostbite"
lang: "fi"
source: reader-frostbite.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, paketit, meshit ja kentät

**Lukee Battlefield 6 -kentän maastoonsa, sen sijoitettuihin meshiin ja niiden värikarttoihin asti, ja kirjoittaa sen `.glb`-tiedostona.** Frostbite-pelit (Battlefield, Need for Speed, Dead Space) säilyttävät sisältönsä `.cas`-lohkoissa, joita kuvaavat `.toc`-sisällysluettelot. Kentän taulukko kertoo, mitkä paketit kenttä lataa, paketit nimeävät jokaisen assetin, ja assetit kertovat, mikä mesh seisoo missäkin.

Lähteet:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(taulukot, paketit, hyötykuormat),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(paketit ja niiden manifestit),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(EBX-osiot),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(korkeuskenttä),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(tekstuurit ja materiaalit),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(sijoittelu ja vienti).
Komennot: `identify`, `levels`, `level` (katso [Komennot](commands.md#levels-and-level-frostbite)).

Pelin kehittäjä ei ole dokumentoinut mitään tästä. Jokainen alla oleva asettelu on luettu tiedostoista ja tarkistettu
kaikkia niitä vastaan, ja jokainen osio kertoo, mikä tarkistus tehtiin. Missä Frostbite-modding-työkalujen kuvaamat vanhemmat versiot
rakenteista, kenttien nimet seuraavat niiden nimiä; koodia ei otettu niistä (katso
[Säännöt ja lisenssit](rules-and-licences.md)).

## Otsikko, joka näyttää salatulta mutta ei ole

| Tunnus (u32, little-endian) | Merkitys | Käsittely |
|---|---|---|
| `0x00CED100` | tavallinen: puu alkaa heti | luetaan |
| `0x01CED100` | allekirjoitettu: 556 tavun allekirjoitus, sitten puu **selkotekstinä** | luetaan |
| `0x03CED100` | XOR-hämärretty, avain tiedoston omassa otsikossa | tunnistetaan ja hylätään |

Allekirjoitettu muoto on se, minkä nykyinen Battlefield toimittaa. Tunnuksen jälkeiset korkean entropian tavut ovat allekirjoitus, eivät salattua tekstiä.

## DbObject-puu

Yksi rekursiivinen rakenne. Jokainen kenttä on tyyppitavu (alemmat viisi bittiä tyyppi, bitti 7 "anonyymi"), valinnainen nimi ja arvo. Säiliöt kantavat pituutensa muuttuvapituisena kokonaislukuna ja päättyvät nollatavuun. `parse_toc` tarkistaa jokaisen säiliön pituuden, joten tiedosto, joka jäsentyy, on ymmärretty. `layout.toc` on tässä muodossa.

## Asennuspaketit

Jokainen sijainti nimeää **asennuspaketin**, johon sen lohko kuuluu. Jokainen paketti numeroi lohkonsa alkaen `cas_01`:stä, joten pelkkä lohkonumero on moniselitteinen heti, kun on asennettu useampi paketti, ja niin on aina.

- `layout.toc` luettelee paketit kohdassa `installManifest.installChunks`, kukin `persistentIndex`- ja `installBundle`-kentällä, kuten `Win32/installation/<package>`.
- Paketin lohkot ovat siinä kansiossa, kohdassa `Data` peruspelille tai kohdassa `Update/<pack>/Data` myöhemmille lisäyksille.
- Sijaintitietue kantaa täyden 32-bittisen `persistentIndex`:n: ensimmäisen sanan alempi puolisko sisältää toisen sanan ylemmän puoliskon, ja toisen sanan ylempi puolisko sen alemman puoliskon; toisen sanan alempi puolisko on lohkonumero.

Tarkistus: jokainen sijainti jokaisessa binäärisessä taulukossa asennuksessa ratkeaa ilmoitetuksi paketiksi ja osuu lohkon sisään, jonka se nimeää. Aiempi versio otti ensimmäisen oikean numeron omaavan `cas_NN.cas`-tiedoston. Kolmannes sen lukemista hyötykuormista näytti silloin korkean entropian tiedoilta, ja ne otettiin salaukseksi. Ne olivat oikeat siirtymät väärässä tiedostossa. Mitään löydettyä ei ole salattu.

## Kenttätaulukko

Kentän taulukko (`levels/<level>/<level>.toc`) on osiotaulukko: viisitoista big-endian-otsikkosanaa, sitten osiot peräkkäin, joiden siirtymät sekä mainitaan että johdetaan kahdesta lukumäärästä.

| Osio | Sisältö |
|---|---|
| paketit | tiivistetaulukko (yksi sana per paketti), sitten 16 tavun tietue per paketti: avain, `0x40000000` \| koko, 0, siirtymä |
| palojen tiivistetaulukko | yksi sana per pala |
| palat | 16 tavun tunnus (palan GUID **tavut käännettyinä**), sitten sana: `0x80000000` \| 4 x sen sijainnin indeksi |
| sijainnit | neljä big-endian-sanaa: paketti (jaettuna), lohko, siirtymä, koko |

Palojen tunnukset ja sijainnit ovat **eri järjestyksessä**. Niiden lukeminen tiedoston järjestyksessä parittaa jokaisen palan toisen palan tavuihin, jotka dekoodautuvat täysin hyvin (enimmäkseen äänenä), eikä niistä näe, että jotain on pielessä, ennen kuin mesh tulee kohinana.
Tarkistus: kentässä indeksisanat ovat permutaatio nollasta palojen määrään miinus yksi.

Lohkot on tallennettu taulukon jälkeen. Jokainen on yhdeksän big-endian-otsikkosanaa, sitten sen merkinnät: kahdeksan tavua siirtymää ja kokoa, joita edeltää kahdeksan tavua paketin ja lohkon nimeä, jos merkinnän liput-tavun ylin bitti on asetettu.
Tarkistus: jokaisella lohkolla viimeinen merkintä päättyy täsmälleen sinne, missä liput-tavut alkavat.

### Mikä taulukko on kenttä

Kentällä voi olla useita taulukoita samalla nimellä: yksi peruspelin `Data`-kansiossa, yksi jokaisessa päivityksessä (`Update/<pack>/Data`), joka toimittaa tai muuttaa sitä, ja yksi jokaisessa korkean resoluution paketissa
(`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Vain osa niistä sisältää lohkoja. Kentälle, jonka päivitys toimittaa, peruspelin taulukko sisältää vain paloja eikä lohkoja, ja päivityksen taulukko on kenttä; ensimmäisen löydetyn taulukon ottaminen ei vienyt siitä mitään.

Joten kenttä on taulukko, jossa on eniten lohkoja, ja tasatilanteessa myöhempi kerros voittaa (ensin peruspeli, sitten päivitykset nimijärjestyksessä). Saman nimiset taulukot ilman lohkoja ovat sen **täydennyksiä**: niiden palat lisätään kentän paloihin, koska ne sisältävät sen tekstuurien suurimmat mipit. Tekstuuriotsikko nimeää tuon palan kohdasta +164 (katso [Tekstuurit ja materiaalit](#textures-and-materials)). `levels` tulostaa, mistä kukin kenttä tulee ja kuinka monta täydennystä sillä on.

## Paketin manifesti

Paketin ensimmäinen merkintä on sen manifesti, tallennettuna pakkaamattomana. Se on aiempien Frostbite-pelien binäärinen pakettimuoto uudella tunnuksella `0xD68E799D`: lukumäärät, SHA-1-tiivisteet, ebx- ja res-tietueet (nimen siirtymä ja koko), res-tyypit, metatiedot ja tunnukset, palojen GUID:t, merkkijonot. Paketin muut merkinnät ovat ebx, res ja palat tässä järjestyksessä.
Tarkistus: lukumäärät täsmäävät merkintöihin jokaisessa paketissa, ja merkkijonot alkavat siitä, mihin tietueet päättyvät.

Res-tyypit ovat tiivisteitä. `0x49B156D4` on MeshSet (jokainen tämän tyypin res on nimetty `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` lukee kaiken tämän yhdelle kentälle muutamassa sekunnissa: kentällä on kymmeniä paketteja ja kymmeniä tuhansia ebx-, res- ja palamerkintöjä.

## Hyötykuormalohkot

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Nollapakkauskoko tarkoittaa tallennettua, kunhan se purkautuu siihen.

| Menetelmäsana | Koodekki |
|---|---|
| `0x0070`, `0x0071` | ei mitään |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), pelin oman `oo2core`-DLL:n kautta) |
| muu, samalla koolla | kopioidaan sellaisenaan |
| muu | hylätään |

Kun luetaan oikeasta paketista, jokainen otettu hyötykuorma dekoodautuu.

## EBX-osiot

EBX pitää sisällään kaiken, mikä ei ole raakadataa. Jokainen osio on RIFF-tiedosto:
`EBXD` (data, kohdistettu 16:een), `EFIX` (osion GUID, tyyppi-GUID:t ja allekirjoitukset, instanssi, osoitin, tuonti- ja tyyppitietojen siirtymät, tuonnit, sekä taulukon, laatikoidun arvon ja merkkijonojen siirtymät), `EBXX` (taulukkotaulukko: siirtymä, määrä, tiiviste, liput, elementtityyppi). Osoitinkenttä on kahdeksan tavua: nolla on tyhjä, pariton arvo on tuonti numero `value >> 1`, muu on suhteellinen kenttään nähden.

**Tyyppikirjastoa ei voi lukea.** Peli toimittaa sen alkutiedostojärjestelmässään, joka on salattu, eikä tämä paketti koske siihen. Tyypit tunnetaan GUID:n ja allekirjoituksen perusteella, jotka jokaisella osiolla on, ja muutamat tyypit, joita kentän vienti tarvitsee, ovat asettuneet datasta.

## MeshSet

Mesh on MeshSet-res (kuvaus) ja yksi pala jokaista yksityiskohtaisuustasoa kohden (puskurit).

| Osa | Asettelu |
|---|---|
| etuliite | neljä sanaa: otsikon koko (176 tai 192), tason tietueen koko (176 - 188), osiotietueen koko (368), 0 |
| otsikko | rajauslaatikko; kuusi i64-tason siirtymää; meshin tyyppi kohdassa `0x6C` (jäykkä, skinnattu, yhdistetty); tasojen ja osioiden lukumäärät kohdassa `0x9C` |
| taso | osiot kohdassa `+0x08`; viisi piirtolistaa kohdassa `+0x14` (läpinäkymätön, läpinäkyvä, decal, vain syvyys, varjo); indeksimuoto `+0x54` (`0x21` u16, `0x2E` u32), indeksi- ja kärkitavut; palan GUID kohdassa `+0x74` |
| osio | materiaalin nimi; kärkiaskel; kolmiot, ensimmäinen indeksi, kärjen siirtymä (tavuina), kärkien määrä kohdassa `+0x20`; kärkimäärittely kohdassa `+0x64`: 16 x (käyttö, muoto, siirtymä, virta), 16 virran askelta, lukumäärät |
| pala | kärkipuskuri, sitten indeksipuskuri. Osion virrat seuraavat toisiaan, ja indeksit lasketaan osion ensimmäisestä kärjestä |

Positiot ovat käyttö 1, virta 0, siirtymä 0, neljänä puolisanana tai kolmena floattina.
Vain läpinäkymättömät ja läpinäkyvät osiot piirretään. Jokainen nimeltään `..._shadow` oleva osio on varjolistalla eikä missään muualla, joten listat päättävät.

Tarkistus: jokainen mesh kentässä, jonka tasot ovat paloissa, dekoodautuu, ja lähes kaikilla on 99 % tai enemmän kärjistä julistetun laatikon sisällä; loput missaavat puolisanan pyöristyksen takia. Dekoodattu laatikko on noin metri, Y ylös, normaalit osoittavat ulospäin.

## Sijoittelu

Sisältöputki kerää kunkin alimaailman staattiset objektit **staattiseksi mallirypääksi**: taulukko jäseniä, yksi per mesh, kullakin instanssimuunnokset.

| Tyyppi (GUID, allekirjoitus) | Asettelu |
|---|---|
| jäsen `ad13064e…`, `0xF861A878` | 224 tavua: `+88` muunnostaulukko, `+112` objektin piirustus (tuonti), `+160` meshiassetti (tuonti) |
| muunnos `101dce06…`, `0x5E6D8C37` | 64 tavua: oikea, ylös, eteen, siirto, kukin vec3 täytettynä 16:een |

Meshiassetin osio on nimetty kuten sen MeshSet-res, joten tuonnin osion GUID antaa meshin. Piste asettuu kohtaan `x·right + y·up + z·forward + translation`. Ryhmän oma muunnos oli identiteetti jokaisessa tarkistetun kentän ryhmässä, eikä sitä sovelleta.

Tarkistus: kentässä jokainen ryhmän jäsen ratkeaa meshiksi; useimmat kopiot ovat kiertoja, joiden determinantti on 1 tuhannesosan tarkkuudella, loput ovat skaalattuja tai peilattuja. Tyyppien GUID:t ja allekirjoitukset ovat samat muissa kentissä. Pelipäivitys, joka muuttaa asettelua, muuttaa allekirjoituksen, ja lukija ei silloin löydä mitään, eikä lue väärin.

### Yksitellen sijoitetut esineet

Mitä putki ei voi ryhmitellä — tuhoutuvat esineet, säiliöt, romu — sijoitetaan **objektiviittauksilla** ja **prefab-viittauksilla**, jotka ovat kentän osioissa:

| Tyyppi (GUID, allekirjoitus) | Asettelu |
|---|---|
| objektiviittaus `a9a6a6ad…`, `0xC4856BEC` | `+32` muunnos (kuten yllä), `+112` objektin piirustus (tuonti) |
| prefab-viittaus `117c746e…`, `0xDE3FE9B4` | sama; piirustus on prefab, osio, jossa on lisää viittauksia |

Prefabit sisäkkäin; kopio asettuu omaan muunnokseensa kerrottuna vanhemman muunnoksella (riviveketorit), jopa kahdeksan tason syvyyteen. Objektin piirustus piirretään meshien mukaan, joita se tuo, jättäen pois tuhoutuneet tilat (`dc_...`). Ryhmitelty prefab viitataan sen `..._nongroupable_autogen`-jäännöksellä, joten mitään ei piirretä kahdesti.

Kävely alkaa vain kentän maailmoista ja kerroksista. Osio, jonka ensimmäinen ilmentymä on prefab-piirustus (`134919fc…`, `0x0247807D`), on prefabin määritelmä, ja kenttä pitää niitä monia omassa kansiossaan, sijoitettuna maailmoillaan muilla tavoilla kuin nämä viittaukset; jos sitä käsiteltäisiin maailmana, prefab asettaisi sisältönsä paikallisiin koordinaatteihin. Se kasaisi satoja kopioita maailman origon ympärille, kaukana maan alle. Maailmoilla ja kerroksilla on `a10ebe0f…`, `0xD3D16C3C` ensimmäisenä.

Pelivaiheen ulkopuolelle asetettuja piirustuksia ei seurata: kehitys- ja testiassetit (`game/dev/`, `test/`), kierroksen lopun elokuvan sarja (`..._gameend_...`: asetettu maan alle)
ja kuolemakameran ohjain (`.../deathflow/...`, jonka laitteet seisovat maailman origossa). Ne tunnistetaan asetuspolusta, ei kerroksesta: sama kerros, joka pitää elokuvasarjan, voi sijoittaa kentän todelliset seinät ja katot. Näiden kahden säännön jälkeen mikään tarkistetun kentän kopio ei ole yli 10 m maanpinnan alla, ja kopiot seisovat maastossa, missä peli ne näyttää.

**Yksityiskohtaisuustasot, jotka korvaavat.** Meshin viimeinen yksityiskohtaisuustaso voi vaihtaa kaukonäkymän korvikkeeseen omalla materiaalillaan: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Hilatorni, jossa on kymmeniä tuhansia kolmioita, voi päättyä muutamaan sataan kolmioon olevaan siluettiin, jonka budjetti valitsisi, ja joka lähellä on kiinteä piikki. Yksityiskohtaisuustaso, joka tuo tällaisen materiaalin, jota sen hienoin taso ei ole, ei koskaan valita: meshin karkein on viimeinen todellinen.

## Maasto

Lähde: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Maasto on TerrainStreamingTree-res (tyyppi `0x22FE8AC8`) ja palat, joihin se viittaa.

| Osa | Asettelu |
|---|---|
| otsikko | 34 tavua; solmujen määrä kohdassa 25 |
| rasteripuut | tyyppitavu ja u32-pituus kumpikin, kunnes tyyppitavu `0xFF`. Tyyppi 0 on korkeuskenttä: näytteitä sivulla +5 (265), korkeusalue kohdassa +21 (1 280 m), maaston neliö sen ensimmäisen solmutietueen kohdassa +77 (8 192 m tarkistetussa kentässä). Se pitää solmujen rajauslaatikot ja 16 x 16 min/max-pyramidin solmua kohden, ei korkeuksia |
| virtaussolmut | neliöpuu, syvyys ensin: palan koko ja GUID; valinnainen toinen pala; liput-tavu (bitti 0: pala alkaa korkeussivulla); onko lapsia. Lapset järjestyksessä (0,0), (1,0), (1,1), (0,1) |
| korkeussivu | ensimmäiset 265 x 265 u16 liputetun solmun palasta, rivi kerrallaan; korkeus = arvo x 1 280 / 65 535 m; sarakkeet x-suuntaan, rivit z-suuntaan, solmun matalasta kulmasta; 4 näytteen reuna, joten 256 solua solmua kohden |

Jokainen askel tarkistettiin erikseen:

- Solmun neliöpuun jäsennys kuluttaa resin viimeiseen tavuun asti, julistettuine 529 solmuineen.
- Naapurisolmut jakavat yhdeksän reunasaraketta tarkalleen, joten askel on 256.
- Lapsen näytteet joka toisessa positiossa ovat tarkalleen yhtä suuret kuin sen vanhemman, reunalla 4, ja ne ovat 90 - 700 yksikköä pois millä tahansa muulla reunalla.
- Kentän alin sana dekoodautuu rajauslaatikon alimmaksi korkeudeksi senttimetriin asti.
- Kahdeksasta tavasta, joilla neliö voi olla maailmassa, vain x x-suuntaan ja z z-suuntaan asettaa sijoitetut esineet paikalleen: puolet näytteistetyistä kopioista noin 2 m:n sisällä, verrattuna moninkertaiseen muilla tavoilla.

Sijoitetut esineet mittaavat tuloksen sitten itse. Jokaisen kopion alin piste verrattuna sen alla olevaan maastoon (bilineaarinen, hienoimmasta solmusta):

| Sijoitettu | Mediaanietäisyys | Etumerkillinen mediaani |
|---|---|---|
| puut ja pensaat | alle metrin | juuri pinnan alla |
| rekvisiitta | metri tai kaksi | pinnalla |
| kivet | noin metri | upotettu noin metri |
| rakennukset | useita metrejä (ne seisovat perustusten päällä) | hieman upotettu |

Kasvillisuus sijoitetaan vain maahan, ei muualle, joten se on terävin tarkistus: sen origot ovat mediaanissa 0,07 m pinnasta. Rakennukset leviävät laajasti, koska luokka sisältää monikerroksisten ja maanalaisten rakennusten seiniä, lattioita ja rakennussarjojen osia. Maaston siirtäminen 64 m sivuun pudottaa 0,5 m:n sisällä olevien kopioiden osuuden 29 %:sta 10 %:iin.

`level` piirtää korkeuskentän `ground:terrain`-osana, jokaisen osan hienoimmasta solmusta, jossa on korkeuksia, ei hienompana kuin `--ground-spacing` (oletus 4 m: 3,7 miljoonaa kolmiota tarkistetulle kentälle, jonka hienoimmat solmut ovat 0,5 m). Eri resoluution palat kohtaavat pienillä askelmilla; mikään ei yhdistä niitä.

Solmun pala kantaa myös sen tasomaskien sivut korkeussivun jälkeen, ja sen toinen pala päättyy solmun värikarttaan (katso [Maastokerrokset](#terrain-layers)).

## Maastokerrokset

Peli varjostaa pelaajan lähellä olevan maaston splatoimalla laatoitettuja pintamateriaaleja maalattujen maskien mukaan, värikartta niiden päällä, ja piirtämällä decaleja (tiet, asfalttipaikat, kiitoratamerkinnät) päälle. Frostbiten oma kuvaus järjestelmästä (Widmark, "Terrain in Battlefield 3", GDC 2012) luettelee maaston rasterit: korkeuskentän, varjostimen splatointimaskit, värikartan, "käytettynä päällekkäiskuvana splatoinnin päällä", fysiikkamateriaalit, tuhoutumissyvyysmaskin, albedokartan kimpoavalolle ja lisämaskikanavat; rasterin laatoissa on reuna renderöintialgoritmeille. Tarkistettujen kenttien virtaussolmupuussa on seitsemän rasteripuuta, tyypit 0, 1, 2, 4, 5, 7 ja 8, joiden otsikot alkavat laattakoollaan: 265 korkeuskentälle (tyyppi 0) ja tyypille 2, 72 tai 66 maskeille (tyyppi 1), 132 reunalla 2 värikartalle (tyyppi 4), 260 reunalla 2 tyypille 5.

**Kerrosluettelo.** Maaston `....layergraphs`-res luettelee yhden 32 tavun merkinnän kerrosta kohden, siinä järjestyksessä, jossa maskitietueet numeroivat ne (34 merkintää, 34 depot-osiota ja kerrosindeksit 0 - 33 yhdessä kentässä). Jokaisen merkinnän tunnus päättyy sen osion avaimeen kerrosgraafin varjostinlohkon depotissa (`....layergraphs_shaderblockdepot`), jonka lohko nimeää kerroksen kartat: yhden `_cv`-värikartan, `_nhs`- ja `_ao`-kartat per pinta, sekä jaetut yksityiskohta- ja kohinakartat. Monet kerrokset eivät nimeä kartoja lainkaan: ne ovat lähteitä, jotka kerrosgraafi lukee. Kerroksen väri on sen `_cv`-kartan keskiarvo; laatoitusmittakaavaa ei löydy. Maaston asetus päättyy yhteen viiden tavun merkintään per kerros (tavu, sitten u32 kerrosindeksi tai -1).

**Maskit.** Rasteripuu 1 on maskien neliöpuu. Sen runko alkaa 59 tavulla, sivun koko kohdassa 0: 72, kun sivut ovat BC4:ää (72 x 72, 2 592 tavua), 66, kun ne ovat pakkaamatonta kahdeksan bitin muotoa (4 356 tavua). Sitten tulee yksi ryhmä per solmu, syvyys ensin:

| Osa | Asettelu |
|---|---|
| ryhmä | u16; u16 tietueiden määrä; u32 sivujen määrä; tietueet; nollatavu. Ryhmä ilman tietueita on 7 tavua |
| tietue | 33 tavua: u16 kerros, u16 tiiviste, neljänneksen laatikko (neljä floattia), kaksi liput-tavua, 85-bittinen läsnäolopyramidi |

Ryhmän tietueet ovat sen solmun neljä neljännestä, kerros kerrallaan, kunkin kerroksen neljännekset järjestyksessä (0,0), (1,0), (1,1), (0,1). Tietue, jolla on toinen lippu, peittää neljänneksensä kokonaan eikä sillä ole sivua; sellainen ilman sitä on seuraava sivu; neljännes ilman tietuetta kerroksessa, jonka ryhmä nimeää, on tyhjä kyseisestä kerroksesta; ensimmäinen lippu on selvä täsmälleen silloin, kun kerros jatkuu neljänneksen omassa ryhmässä, yksi taso alempana, ja korvaa sen siellä. Sivujen määrä on niiden tietueiden määrä, joilla on sivu.

Sivut: solmun oman ryhmän sivut seuraavat sen palassa, korkeussivun jälkeen, 4 358 tavun 16-bittisen osion ja 67 x 67 kahdeksan bitin rasterin kanssa (palan alusta, kun sillä ei ole korkeussivua); sen toinen pala pitää neljän neljänneksensä ryhmien sivut yhden tason alempana, neljännekset värikartan järjestyksessä, ja sitten värikartan. Sivu on neljänneksen 64 x 64 texeliä, rivit z-suuntaan ja sarakkeet x-suuntaan, reunalla kopioituna naapureilta: 4 texeliä BC4-sivulla, 1 pakkaamattomalla.

Reunat todistavat sijoittelun ilman arviointia: saman kerroksen kaksi vierekkäistä sivua kantavat toistensa reunatexelit. `read_masks` tarkistaa sen jokaiselle sijoitetulle parille ja hylkää kentän, jossa alle 99 % on samaa mieltä. Noin kolmasosa tarkistetuista kentistä luetaan, reunojen ollessa samaa mieltä; muutamassa ei ole maalattuja maskeja; loput hylätään, lähes kaikki tarkistuksen takia (niiden solmujen palat sisältävät enemmän kuin tämä asettelu tuntee). Hylätyn kentän maa saa pintamateriaaliensa keskivärin, ja vienti kertoo syyn. Neljänneksen ympärillä olevat reunat, jotka ovat täyden neljänneksen kohdalla, ovat 255 ja tyhjää vasten 0.

Osiota 4 358 tavua ja 67 x 67 rasteria ennen sivuja ei lueta: niiden arvot ovat kapealla korkealla kaistalla, ilman pieniä arvoja eikä vartijaa.

**Maan väri.** Kerrosgraafi sekoittaa kerrokset käännetyssä varjostinkaaviossa maskeista, kaltevuudesta, korkeudesta ja kohinasta; sitä ei lueta. `--ground-texture` värittää maan omalla säännöllään, joka sanotaan tässä sellaisena:

- kerrokset, joiden värikartta on nimetty etäisyyden mukaan, ovat kaukonäkymän korvikkeita ja jätetään pois;
- tekstuuroidut kerrokset, jotka peittävät yhdeksän kymmenesosaa maastosta tai enemmän, ovat pohja. Niiden maskit ovat täynnä lähes kaikkialla, joten missä kukin on, on varjostimen valinta, ei niiden: ne, joiden nimi viittaa kallioon tai rinteeseen, värittävät yli 40 asteen rinteet, ne, joiden nimi viittaa soraan, tasaisen maan (muut pohjakerrokset, jos mitään muuta ei ole), sekoitettuina 20 ja 40 asteen välillä korkeuskentän rinteen mukaan (otettuna 4 m:n välein ja levitettynä bilineaarisesti leivotuille texeleille: toistettuna 4 m:n lohkoina se piirsi kallion värin kovareunaisina laikkuina);
- jokainen muu tekstuuroitu kerros peitetään pohjalla omalla maskillaan, kerrosjärjestyksessä;
- värikartta peitetään tuloksen päälle niin kuin moottori sen tekee, kaksi kertaa maan väri kerrottuna kartan kanssa, joten keskiharmaa jättää sen ennalleen; jos värikartalla ei ole texeleitä, maa saa kartan mediaanikirkkauden harmaana.

Tarkistettu pelin maan mediaaniväriin pelikuvien (punainen ja sininen suhteessa vihreään) mukaan: leivotun pelialueen arvo on 1,00 / 0,69 pelikuvien 1,19 / 0,78 vastaan yhdessä, jonka ruohokerrokset ovat vihreitä siinä, missä kuvat näyttävät kuivaa ruohoa; 1,19 / 0,82 vastaan 1,01 / 1,04 toisessa, jonka värikartta itsessään on lämmin (1,13 / 0,88); ja 1,05 / 0,91 vastaan 0,93 / 0,92 kolmannessa ilman värikarttaa. Kuvat ovat valaistuja ja gradattuja, joten tämä mittaa sävyn, ei kirkkautta.

**Värikartta.** Solmun toinen pala sisältää, maskisivujen jälkeen niiden neljänneksen ryhmistä, neljä BC7-sivua 132 x 132 (17 424 tavua kukin), yksi solmun neljännestä kohden, järjestyksessä (matala x, korkea z), (korkea x, korkea z), (korkea x, matala z), (matala x, matala z). Maskipuu kertoo, kuinka monta tavua maskisivut vievät, joten värikartta löydetään laskemalla, ei palan lopusta: yhdessä kentässä karkeammilla solmuilla on neljä lisää tällaista sivua sen jälkeen, toinen rasteri yhdellä tasaisella värillä, ja viimeisten neljän sivun lukeminen menetti värikartan yli yhdeksän kymmenesosasta maastoa. Ilman tätä laskentaa värikartta jäi huomaamatta myös kentissä, joissa on pakkaamattomia maskisivuja, joiden sivut eivät ole kokonaisia BC4-sivuja; yhden kentän värikartta meni 0,4:stä 0,94:ään sen maastosta. Järjestys sovitettiin: neljänneksen korkeuskentän reunoja vasten jokainen solmun sivu, jossa on piirteitä, täsmää yhteen neljännekseen, sovittamattomana, arvoilla 0,3 - 0,54, kun seuraava paras sijoitus on alle 0,2. Sen liittämänä kentän sivut yhdistyvät saumattomasti teihin, veteen ja rakennettuihin alueisiin testikentässä, 0,5 m:n texelillä pelialueella. Kohdissa, joissa kerrokset tekevät työn, värikartta on lähes neutraali (mediaani 110, 107, 104); muualla se voi kantaa täyttä väriä. Kenttä, jonka toiset palat sisältävät vain pakkaamattomia maskisivuja, ei lue värikarttaa. Tämän lukijan aiempi kierros kutsui näitä sivuja maantieteellisiksi; se vertasi niitä taustakarttaan, joka voi olla aivan toinen maisema, ja sijoitti jokaisen sivun koko solmuun neljänneksen sijaan.

**Kimpoavan valon albedo** haettiin, eikä sitä löytynyt: juuren ja ensimmäisen tason solmujen palat ovat kokonaisia maskisivuja, ja tyypin 5 hyötykuormaa ei löydetty.

**Aukot.** Kentän maastoasset (res-tyyppi `0x1CA38E06`) nimeää kolme varjostinta: oletuspinnan varjostimen, aukkojen pinnan varjostimen ja oletuslähdevarjostimen. Mitä kerrosta aukkojen varjostin lukee, ei ole löydetty, joten korkeuskenttää ei leikata. Kentässä navigointiverkko voi kulkea kallio-meshien päällä kymmeniä metrejä korkeuskentän alapuolella, missä pelin on täytynyt leikata ne pois. Etsittiin ja ei löydetty: kerroksen maskia, 67 x 67 rasteria, varattua korkeutta (yhdessäkään kentän korkeussivussa ei ole 0 tai 65 535) ja solmun lippua (jokaisella juuren alapuolisella solmulla on lippu 1). Rasteripuut 7 ja 8 ovat jäljellä. Molemmat ovat pituuskoodattuja: tavu, joka on sama kuin sitä edeltävä, seuraa lisäkopioiden määrä (`ff ff 84` on 134 tavua 255:tä). Puu 7 (laatta 256, täysi neliöpuu viidellä tasolla, neljä bittiä näytettä kohden) dekoodautuu tavuparien arvoiksi 0 - 3; puu 8 (laatta 265) tavuiksi, jotka ovat enimmäkseen 255, ja muut arvot säännöllisinä juoksuina. Kumman laattoja ei vielä sijoiteta, joten kumpikaan ei tiedetä pitävän aukkoja.

**Decalit** luetaan ja paistetaan; katso [Maastodecalit](#terrain-decals).

## Maastodecalit

Lähde: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Tiet, kiitoradat, betonipaikat, maalatut viivat ja kirjaimet, renkaanjäljet: `TerrainDecals`-res (tyyppi `0x15E1F32E`) pitää niitä litteänä geometriana, jonka peli asettaa maaston päälle.

| Osa | Asettelu |
|---|---|
| otsikko | kohdassa +16 paikkamäärä n, sitten n 16 tavun paikkaa, sitten tietueiden määrä |
| tietueet | yksi per piirtoerä, peräkkäin, vaihtelevan pituisina: 156 tavua kiinteitä kenttiä — ensimmäinen kärki kohdassa +32, kolmioiden määrä kohdassa +36, tekstuurin laatoitus metreinä kohdassa +44 — sitten erän kärkitavut (siirtymä, koko), sitten häntä, joka nimeää sen tekstuurit niiden omaisuuksien osien GUID:illa |
| kärjet | 32 tavua: x, z (f32), 8 pakattua tavua, u, v (f32), r, g, b, a (f16); jokainen erä on tavallinen kolmiolista |
| indeksit | u32, lasketaan nollasta jokaisessa erässä; ei tarvita |

Tarkistukset:

- tietueiden kärkialueet seuraavat toisiaan ilman aukkoa ja kattavat kaikki kärjet täsmälleen, ja jokaisen tietueen ensimmäinen kärki kertaa 32 on sen siirtymä;
- näin luettuna kolmiot ovat kompakteja decaleja (kirjaimia, viivanauhoja, laikkuja); yhdellä kärjellä vähemmän ne ovat viiruja läpi kartan;
- lähes jokainen erä nimeää tekstuurit hännässään: värikartta (`_cv`) ja läpinäkyvyyskartta (`_op`, punainen kanava), tai merkinnöille kanavamaski (`_rgb`).

Tekstuurien GUID:ien jälkeen häntä kantaa erän materiaaliparametrit, koodattuina kuten varjostinlohkon (katso alla Sävyt). Merkinnän, renkaanjäljen tai viivan maalivärinen on float3, jonka tiiviste on `607e`: hiekkaisen 0,64, 0,56, 0,48 renkaanjäljille hiekassa, lähes musta asfaltille. Läpinäkyvyyskartat ovat enimmäkseen muotoa 62, yksi kanava 8 tavua lohkoa kohden, luettuna BC4:nä.

Erä kartoittaa tekstuurinsa joko maailmasijainnin mukaan (u = x, v = z, tekstuuri toistuu tiilemetrin välein: asfaltti, betoni, sora) tai 0 - 1 koko decalin yli (viiva, kirjain, renkaanjälki). Tietueet piirretään tiedoston järjestyksessä.

**Paistaminen.** `level --ground-texture M` maalaa decaleiden alueen alle, laatoissa enintään 4 096 pikseliä, taustan värikartan (bilineaarisesti) ja sitten jokaisen erän sen päälle, sen läpinäkyvyys × kärjen alfa. Kärkien väriä ei käytetä: joidenkin erien kärjet ovat puhdasta vihreää tai sinistä, mikä väritti yhden kentän merkintöjä noilla väreillä. Korkeuskentän kolmiot siellä muuttuvat `ground:terrain x<x> z<z>`-osiksi, jotka kantavat laatan. Jokainen erä piirtyy seuraavasti:

| Erän nimet | Piirretään |
|---|---|
| värikartta (`_cv`) | kartta sen läpinäkyvyyskartan mukaan |
| kertolaskukartta (`_mult`) ja läpinäkyvyyskartta | maali (valkoinen, jos materiaali ei nimeä sitä) kerrottuna kertolaskukartalla, läpinäkyvyyskartan mukaan: kiitoradan kulunut keskiviiva, reunaviivat ja kynnyspalkit |
| kanavamaski (`_rgb`) | maali, muuten valkoinen viivoille ja kirjaimille, tumma ääriviivoille, lievä tummennus kulumalle, renkaanjäljille, tahroille, lätäköille ja kosteudelle, maskin mukaan |
| pelkkä läpinäkyvyyskartta maalilla | maali läpinäkyvyyskartan mukaan: renkaanjäljet |

Tien vaihtelumaski ei ole maalia, vaan muuttaa sen alla olevaa pintaa, satojen metrien päässä, eikä sitä piirretä, mikä sen maali sitten on: valkoisena se piirsi kahdella kentän rinteellä kaksi vaaleaa suorakulmiota, 150 - 250 m pitkiä. `_mult`-karttaa pidetään maalin omana kulumisena, ei sen alla olevan maan tummennuksena: se on lähes valkoinen, ja viivan muoto on läpinäkyvyyskartassa.

Lähes jokainen erä piirtyy muutamaan laattaan 0,5 m pikseliä kohden; vienti kasvaa muutamalla MB:llä ja kestää muutaman sekunnin enemmän. Ylhäältä katsottuna aprokit, rullateet ja tieverkko ovat yhdistelmien aitojen ja rakennusten alla ja johtavat niiden porteille.

Jos ne piirrettäisiin sen sijaan omana geometrianaan, decalit tarvitsisivat alfasekoitusta, jota kirjoittaja ei kanna, ja siirtymä maaston yläpuolella tappelisi z-fightissa; paistaminen pitää ne maan omassa värissä.

## Tekstuurit ja materiaalit

Lähde: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Texture-res (tyyppi `0x6BDE20BA`) on 180 tavun otsikko: tyyppi ja pikselimuoto kohdassa +8, leveys ja korkeus kohdassa +22, mip-määrä kohdassa +30, palan GUID kohdassa +40, viisitoista mip-kokoa kohdassa +56. Pala on mip-ketju, suurin ensin. Joistakin paloista puuttuvat suurimmat mipit, jotka toimitetaan korkean resoluution paketissa, ja palan pituus kertoo, mistä mipistä se alkaa. Tuon paketin pala on nimetty kohdassa +164; se luetaan kentän [täydennyksistä](#which-table-is-the-level), kun pääpalasta puuttuvaa mipiä tarvitaan, ja sen pituus plus pääpalan pituus on koko ketju.

| Muoto | Dekoodataan | Todiste |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineaarinen) | muovisen säiliön värikartta dekoodautuu sellaisena; BC3:na samat tavut ovat kohinaa |
| 61, 60 | BC3 | laatikon värikartta dekoodautuu siististi BC3:na, ei BC1:nä eikä BC7:nä |
| 57, 56, 55 | BC1 | puoli tavua pikseliä kohden |

Meshiasset ei nimeä tekstuuria. Linkki on kentän **varjostinlohkodepoissa** (res-tyyppi `0x73312045`, yksi per alimaailma), avaimena meshiosion tietueen kohdan +0x130 kahdeksan tavua:

| Osa | Asettelu |
|---|---|
| taulukko, kohdasta 16 | (osioavain u64, kuvaajan siirtymä u64), kunnes siirtymä osuu resin ulkopuolelle |
| kuvaaja | (lohkon siirtymä u64, tiiviste u64, lohkon koko u64) |
| lohko | osion varjostinparametrit; jokainen tekstuuri on 49 tavun tietue: tavu, 16 tavua, tekstuuriasetuksen osion GUID, sen instanssin GUID |

Laatikon osioavain esiintyy kerran jokaisessa kymmenestä depoista alimaailmoissa, jotka sijoittavat sen, ja sen lohko nimeää `t_mil_crate_03_cs`:n ja `_nmt`:n jaettujen yksityiskohtakarttojen joukossa. Lohko nimeää jokaisen tekstuurin, jota varjostin näytteistää, eikä sitä sanota, mikä on värikartta, joten se valitaan: sRGB-2D-tekstuuri, jonka nimi sisältää suurimman osan materiaalin nimen sanoista (`M_ConcreteWall_01`: concrete, wall), sitten meshin sanoista, sitten sellainen, joka ei ole yksityiskohta, decal (`t_de_...`) tai vauriokartta, sitten se, jota vähiten lohkot käyttävät. Tieopaston lohkon paneeli on `t_com_highwaysignage_01_cs` ja decal-levy `t_de_com_highwaysignage_01_ca`, jossa on sivulleen käännetty kilpi; molemmat täsmäävät sanoihin, ja ilman decal-sääntöä levy voitti käytöllä, ja kyltti näytti kilven käännettynä neljänneksen, kaikkien tekstuurikoordinaattijoukkojen läpi, jotka osiolla on. Etäisyyskenttien (`..._sdf`), paletoiden ja kanavamaskien (`_rgb`) tekstuureita ei koskaan valita, mitä sanoja ne jakavatkin (`_rgba`-kartat valitaan: useimmat ovat väriä alfalla, ja niiden jättäminen pois vaihtoi sähköjohdon ja portaiden omat kartat vieraisiin); taustan kasvillisuusatlas `..._atlas_a_sdf`, joka piirrettiin värinä, näytti puille mustia ja valkoisia tähtiä, taustan rakennuspaletti antoi seinille konfettina värinäytteitä, ja lasijätteet piirrettynä kanavamaskinsa kautta tulivat syaanina. Osio, jonka ainoat ehdokkaat ovat jaettuja yksityiskohtakarttoja, pysyy tasaisena värinä.

**Paletit.** Taustan rakennukset ottavat värinsä paletista, 256 x 256 texeliä 16 x 16 värinäytteenä: jokaisella kärjellä on neljä tavua (käyttö `0x1E`), joiden kaksi ensimmäistä kertovat, missä paletin kohdassa sen väri on, x ja y 255:stä. `level` piirtää tällaisen osion paletin kanssa tekstuurinaan, jokainen kärki värinäytteen keskellä. Näin piirrettynä kentän taustan lohkot tulevat pastellinvärisiksi seiniksi, tiilenpunaisiksi ja tummiksi ikkunoiksi siellä, missä ne olivat valkoisia.

**Peitteet.** Suuret esineet laatoittavat trimmiarkin ensimmäisten tekstuurikoordinaattiensa kautta ja asettavat peitteen sen päälle toisten koordinaattien kautta, jotka ovat välillä 0 - 1: esineen kokonaisuuden auki kääntäminen. Peite (`..._overlay_cs`, maskinsa `..._overlay_a`) kantaa sen, miltä esine näyttää kaukaa: öljysäiliön punaiset raidat ja ruoste; piirrettynä pelkällä trimmiarkilla yhden kentän säiliöt näyttivät harmaina paneeleina. Osio, jonka lohko nimeää peitteen maskeineen, ja jonka toiset koordinaatit ovat sellainen auki käännetty, piirretään peitteellä niiden läpi (36 osiota kyseisessä kentässä).

**Sävyt.** Monet värikartat ovat harmaita (niiden kanavien keskiarvot 6 %:n sisällä toisistaan): varjostin maalaa ne lohkon parametreistä löytyvillä väreillä. Tekstuurimerkintöjensä (49 tavua kukin) jälkeen lohko luettelee parametrinsa, kukin tyyppitunnisteella (`f11af825` float3, `a5e1f2de` float4, `c1b1a014` float, `4a4fc3a1` kokonaisluku), liput-tavut `01 80` yhdelle arvolle, parametrin nimen kaksitavuisen tiivisteen, u32-määrän, arvon ja kahdeksan tavun tunnuksen. Nimiä ei tallenneta. Seitsemän float3-nimitiivistettä toimii sävyinä: yhdessä kentässä kolme niistä pitää väriä noin yhdessä lohkossa kuudesta, jonka kartta on harmaa ja lähes koskaan siellä, missä kartalla on oma väri, ja muut pitävät värejä, joilla harmaa kartta maalataan, kun materiaalin nimi sanoo niin (sillan `..._blue`-reuna: 0,047, 0,098, 0,171 neutraalia 0,5:tä vastaan). Yksi perhe voi pitää useita arvoja, yhden kutakin maskin kanavaa kohden, useimmat neutraaleja, ja arvo, jolla kanavassa on lähes ei mitään (puhdas vihreä tiilifasadeilla), valitsee maskin kanavan eikä maalaa. `level` kertoo harmaan värikartan, lineaarisessa valossa, jokaisen perheen ensimmäisellä arvolla, joka ei ole neutraali eikä tällainen valitsija, neutraaliin arvoonsa nähden, ja pitää tuloksen omana tekstuurinaan; värikartta, jossa on väriä, jätetään ennalleen. Sääntö on vientiäijän oma: sitä, mikä maskin kanava saa mitäkin sävyä, ei luettu. Yhdessä kentässä se laski rakennusosien kolmioiden osuuden, jotka piirtyvät lähes valkoisina, 19,4 %:sta 3,9 %:iin.

**Esinevaihtelut.** Yksi mesh sijoitetaan useaan ulkonäköön: varastoseinä punaisella tai sinisellä raidalla ja eri numerolla maalattuna, kontti vihreänä tai harmaana. Jokainen sijoitettu kopio nimeää ulkonäkönsä:

| Missä | Kenttä |
|---|---|
| staattisen mallirypään jäsen | kohdassa +32: taulukko yhdestä osoittimesta kopiota kohden, esinevaihteluun tai nollaan |
| objektiviittaus | kohdassa +120: osoitin esinevaihteluun tai nollaan |
| esinevaihtelu (`ov_...`-osio, tyyppi `235f2a9c...`) | sen ensimmäisen instanssin kohdassa +32: vaihtelun u32-nimitiiviste |

Osion ulkonäkö vaihtelussa on sen varjostinlohko, joka avataan osion omalla avaimella, johon vaihtelun tiiviste on lisätty sen neljään ensimmäiseen tavuun little-endian u32:na (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); osio ilman lohkoa tuolla avaimella näyttää samalta jokaisessa vaihtelussa.
Kentän meshien vaihteludatakannat (`meshvariationdb_win32`) luettelevat meshiä ja vaihtelun tiivistettä kohden materiaalit, joihin kukin vaihtelu koskee, mutta ei avaimia: sääntö löydettiin itse avaimista, ja se pätee jokaiseen osioon, jolla on variantteja, joita tarkistettiin (yhden seinän neljä vaihtelua, kolme sen osiota kutakin kohden). Vaihtelun lohko tuo mukanaan omat tekstuurinsa ja sävynsä: seinällä maalattu numero on kirjainlevy, jonka vaihtelun lohko nimeää. Suuri osa ryhmitellyistä kopioista on sijoitettu vaihteluun.

Lohko paistetaan kerran per sisältöjoukko, ja depon merkinnän avaimella on niiden tiiviste (merkinnän toinen u64). Jos osiolla ei ole lohkoa sen vaihtelun avaimella, vaihtelu tavoittaa sen silti *kaksosen* kautta: toisen osion, jonka oletuslohkolla on sama sisältö ja jolla on sellainen. Ilman kaksosia seinä, jonka pituudet jakavat yhden oletuslohkon, voi tulla kahdessa värissä. Osio ilman omaa varianttia ottaa variantin, jonka useimmilla sen kaksosilla on.

**Tuhoutuvat meshit.** Mesh, jonka ottelu voi kaataa, on tuhoamisasetus omalla nimellään sen vieressä (`.../br_x.destruction` meshille `.../br_x_mesh`): rikottavat rakennukset ja seinät (`br_`) ja monet rekvisiitat. `level` pitää niiden pinnat osissa omanaan, nimettyinä ` (destructible)`, joiden glTF-solmut kantavat `{"destructible": true}`. Niiden tuhoutuneet tilat ovat niiden vierellä olevat `dc_..._part<N>_mesh`-meshit, kukin omassa origossaan; missä osa istuu, on tuhoamisasetuksessa, jota ei lueta, joten tuhoutuneita tiloja ei viedä.

**Jätetään pois.** Osiot, joilla on paikkamerkkilohkon materiaaleja (`M_Whitebox`: muutama suuri teksturoimaton kolmio, joita jotkut rakennukset pitävät pintojensa vieressä, ja jotka nousivat kentästä valkoisina evinä), elokuville tehdyt meshit (helikopteri, joka on sijoitettu sinne, missä sen kohtaus alkaa) ja valaistusapuvälineet (tasoja, jotka estävät valon, eivät koskaan piirry). Kentän generoituja taustarakennuksia (`..._generated_blueprints_..._mesh`) piirretään, mutta niiden seinien materiaalien nimet nimeävät vain kohinakarttoja, ja niiden kärjissä ei ole väriä, joten ne jäävät tavallisiksi. Lähes jokaiselle piirretylle osiolle tulee värikartta.

**Kirjainlevyt.** Seinän maalattu numero tai nosturin mainostaulun tuloste on oma osionsa, jonka värikartta on levy (`_ca`): kirjaimen alfa tasamaalin päällä, tai tuloste. Sen ensimmäiset tekstuurikoordinaatit laatoittavat seinän rappauksen paneelin yli (u -0,2 - 1,7 yhdellä seinällä), mikä piirtää levyn lähes kahdesti. Neljäs joukko (`0x24`, muuten kolmas, `0x23`) asettaa sen tarkalleen kerran (u -1 - 0, v 1 - 2, muutama tuhannesosa yli karkeammilla yksityiskohtaisuustasoilla). Kun ensimmäinen joukko jättää yhden kuvan kopion ja neljäs tai kolmas on sen yhden sisällä, levy piirretään niiden läpi, siirrettynä välille 0 - 1. Alfalla varustettu levy piirretään 1 cm pinnan edessä, jolle se on maalattu, ja tämä pinta piirretään sen alle lohkon toisella värikartalla ensimmäisen joukon läpi: ilman sitä levyn tyhjät texelit näyttivät seinän sisäpuolen. Toinen joukko on esineen auki käännö peitettä varten, eikä sitä käytetä tässä.

**Leikatut kartat.** Värikartan neljännellä kanavalla on eri merkitys kartan nimen mukaan. `_cs`-kartassa, ylivoimaisesti yleisin (893 valitusta kartasta yhdessä kentässä), se on kiiltoa: 1 % mediaanikartan alfasta on 0,1 etäisyydellä nollasta tai yhdestä. `_cu`-kartoissa (lehdet, ruoho) ja `_ca`-kartoissa (väri ja alfa) se on läpinäkyvyyttä: 90 % ja 87 %. Värikartta, jonka nimi on `..._cu` tai `..._ca` ja jonka alfa on vähintään 75 % lähellä nollaa tai yhtä, vähintään 1 % alle 0,5 ja vähintään 5 % yli 0,5, kirjoitetaan alfansa kanssa PNG:nä, ja sen materiaali glTF:nä `alphaMode` MASK, `alphaCutoff` 0,5, kaksipuolisena; lehtikortit näyttävät silloin lehtiä, eivät niiden mustia kulmia. Yhden puun lehtikartassa ei ole alfaa lainkaan (enintään 4 255:stä): sen lehvät leikataan geometrialla, ja pelkillä kahdella ensimmäisellä ehdolla koko latva leikattiin pois.

Tekstuurikoordinaatit ovat kärkikäyttö `0x21`, kaksi puolisanaa (muoto 6) tai kaksi floattia (muoto 2). Osiot kantavat jopa kolme lisäjoukkoa (`0x22` - `0x24`) decal- ja yksityiskohtakerroksille. Koordinaatit toistuvat: säiliön kylkiluullinen puoli kulkee -1,6:sta 1,8:aan, taustamaaston laatat ovat kokonaan 0..1:n ulkopuolella, ja yhdessä kentässä 23 % tekstuuroiduista kolmioista ylittää 0..1. Ne kirjoitetaan sellaisinaan toistuvalla näytteenottimella; 3DHeat-viewer kääräisee jokaisen toistuvan tekstuurin atlaksensa sisään. Renderöijä, joka sen sijaan rajaa ne, venyttää kylkiluut kaksinkertaisiksi, muuttaa betonilattian raidoiksi yhteen akseliin ja antaa tornin teräspalkeille niiden tekstuurin reunavärin; sitä varten `--clamped-uvs` leikkaa jokaisen kolmion linjoja pitkin, joilla tekstuuri toistuu, ja siirtää jokaisen palan välille 0..1 (katso [Tulostemuoto](output-format.md)). Sen jälkeen 0,03 % tekstuuroiduista kolmioista, joiden yli tekstuuri toistuu yli 16 kertaa, ylittää, ja kolmio, jonka leikkaaminen tekisi enemmäksi kuin 4 palaksi, piirretään sen tekstuurin keskivärissä: kuori toistuu jokaisen oksan alas, ja leikattuna kentän puiden kolmiot menivät 6,4 miljoonasta 24 miljoonaan.

Maaston korkeuskentällä ei ole omaa värikarttaa, jota voitaisiin lukea. Missä yksi taustamaaston kartoista peittää sen, se väritetään siitä: taustan tekstuurikoordinaatit ovat lineaarinen funktio maailman x:stä ja z:sta (99 % sen kärjistä 0,001:n sisällä siitä; kartta peittää 65 536 m:n neliön, käännettynä neljänneksen verran), ja sama funktio antaa korkeuskentän. Kenttä lataa tuon kartan mipit 2 048 px:stä alaspäin, joten korkeuskenttä saa 32 m pikseliä. Sen tumma kallio on jyrkillä rinteillä: tumman ja rinteen korrelaatio on 0,48, ja enintään 0,34 seitsemälle muulle suuntaukselle.

Toisen kentän tausta on kahdeksan lähi- ja kahdeksan kaukolaattaa pelialueen ympärillä, kukin toistaen oman tekstuurinsa laatan yli, eikä yksikään ulotu korkeuskenttään. Jokainen taustan tekstuuri sovitetaan itsenäisesti, ja kun mikään ei peitä korkeuskenttää, se ottaa keskiarvon, jonka tausta näyttää maaston neliöstä kilometrin säteellä; sen päälle `--ground-texture` paistaa decalit. Taustamateriaali on sellainen, jonka nimessä on `TerrainBackdrop`, tai `BD_` ja `Terrain` (`M_BD_<site>_Terrain..._Near`); tai taustamesh (`bd_..._terrain<site>_04_far_mesh`) kantaa tavallisen maastomateriaalin (`M_<region>_Terrain<site>_04_Far`), jonka ensimmäiset kaksi sääntöä missasivat yhdessä kentässä, ja värittivät sen maan pinnoistaan.

Missä mikään taustakartta ei peitä korkeuskenttää, se ottaa kuitenkin ensin maaston omien pintojen keskivärin ennen taustan keskiarvoa: `_cv`-värikartat, joihin kerrosgraafin varjostinlohkot viittaavat (27 yhdessä kentässä: hiekkoja, soraa, maita, nurmea, halkeilleita betoneja), kukin keskiarvoistettuna, sitten kunkin kanavan mediaani, jättäen pois moottorin oletuspinnan. Tausta voi olla aivan toinen maisema: yhdessä kentässä sen keskiarvo (95, 99, 80 sRGB:nä) käänsi pelialueen maan harmaaksi, jota peli ei näytä. `--ground-texture`-valinnalla tuo väri kerrotaan kahdella kertaa värikartan kanssa, joka jättää keskiharmaan ennalleen, ja se paistetaan decalien kanssa molempien, decalien ja värikartan alueen päälle.

Kokonaisuudessaan kunkin kentän leivotun pelialueen ja pelikuvien mediaanivärit verrattuna peliin (rivit 55 - 72 % kuvasta HUD:n vierestä, 24 kuvaa kumpaakin; sRGB; kuvat ovat valaistuja ja gradattuja, joten suhteet r/g ja b/g ovat oikea vertailu):

| Kenttä | Kuvat | Taustan keskiarvo | Nyt |
|---|---|---|---|
| ensimmäinen | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| toinen | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| kolmas | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Ensimmäinen on korjattu; muut kaksi olivat ennen hieman lähempänä sävyltään. Yksi väri koko kentälle ei voi olla oikein kaikkialla; maskit olisivat.

## Navigointiverkko

Lähde: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Kenttä toimittaa yhden osion per agentti, `<level>/dbt/<level>_navmesh_layer_<n>`: yhdessä kentässä kerros 0 on sotilas (1,8 m pitkä, 0,18 m askel, 0,4 m säde), ja kaksi muuta ovat ajoneuvoja (3,5 ja 10 m korkeita). Jokainen osio pitää kahta taulukkoa:

| Taulukko | Alkio |
|---|---|
| laatat | 28 tavua: u32 0, u32 tiiviste, u32 0, u32 palan indeksi, u16 laatan x, u16 laatan z, u32 siirtymä, u32 koko |
| palat | 20 tavua: palan GUID, u32 koko |

Laatta on `size` tavua kohdassa `offset` palassa `chunk index`, little-endian, ja se on asetettu Detourin (Recast Navigationin) tavoin pidemmän otsikon takana:

| Siirtymä | Sisältö |
|---|---|
| 0 | `VAND`, versio 7 |
| 24 | lukumäärät: polygonit, kärjet, linkit, yksityiskohtaiset meshit, yksityiskohtaiset kärjet, yksityiskohtaiset kolmiot, rajausvolyymisolmut, pois-meshin linkit, ensimmäinen pois-meshin polygoni |
| 188 | agentin korkeus, askel, säde |
| 200 | laatan rajauslaatikko, kuusi floattia |
| 232 | kärjet: x, y, z floattia, maailmakoordinaatit |
| seuraava 8 tavun raja | polygonit, 32 tavua: u32, kuusi u16 kärkiindeksiä, kuusi u16 naapuria, u16 liput, kärkimäärä kohdassa +30, kohdassa +31 ala (kuusi alinta bittiä) ja tyyppi (kaksi ylintä) |
| sitten pakattuna | linkit (16 tavua), yksityiskohtaiset meshit (12: ensimmäinen yksityiskohtainen kärki u32, ensimmäinen yksityiskohtainen kolmio u32, kärki- ja kolmiomäärä u8), yksityiskohtaiset kärjet (kolme floattia), yksityiskohtaiset kolmiot (kolme indeksiä ja liput), rajausvolyymisolmut (16), pois-meshin linkit (80) |

Jokaisessa kentän laatassa nämä summautuvat laatan kokoon tavulleen, ja yksityiskohtaiset meshit numeroivat polygonit ennen ensimmäistä pois-meshin polygonia.

Polygoni on tasainen kulmiensa välillä; sen **yksityiskohtainen mesh** pitää pinnan todellisen korkeuden kyhmyjen, kivien ja askelmien yli, ja se on se, mitä piirretään. Yksityiskohtaisen kolmion indeksi, joka on polygonin kulmamäärää pienempi, on tuo kulma, muuten yksityiskohtainen kärki `first + index - corners`. Polygonien viuhkoittaminen sen sijaan tuo paljon enemmän kolmioita maan alle ja tekee pitkiä siivuja; yksityiskohtaisilla meshillä mikään ei ole pidempi kuin 16 m:n laatan lävistäjä plus askel ylös rinteessä.

Tyyppi 0 on maa, tyyppi 2 pieniä jyrkkiä laikkuja (noin 45 astetta, neliömetri kukin), tyyppi 1 linkki pintojen välillä: sen kulmat kattavat 125 m tai enemmän korkeutta ja ovat laatan ulkopuolella, osa origossa. Linkit jätetään pois; muut piirretään niiden yksityiskohtaisilla meshillä, tai viuhkoitetaan laatassa, jossa ei ole yhtään.

Tarkistukset: palojen koot summautuvat laattojen kokoihin tarkalleen; jokainen pintakärki on laatan laatikon sisällä, plus tai miinus noin metri; lähes kaikki kolmiot osoittavat ylös. Laatta, joka epäonnistuu, hylätään ja lasketaan, ja siinä kentässä ei hylätä yhtään.

Mitä sotilaan mesh peittää, ylhäältä nähtynä testikentässä: maan, lattiat, portaat ja osan katoista, ja ei rahtikonttien kattoja. Se on AI:n kartta siitä, missä sotilas voi seisoa, ja lähinnä mitä tiedostot tietävät pelaajan seisomispaikoista.

## Ei toteutettu

- Maaston kerrosgraafi, joka sekoittaa sen pintakerroksia (katso [Maastokerrokset](#terrain-layers)): maan väri seuraa tämän lukijan omaa sääntöä kerrosten maskeista ja korkeuskentän rinteestä, ja kentät, joiden maskisivut eivät sovi yhteen, saavat yhden värin.
- Decal-materiaalien väriparametrit: merkinnät kanavamaskien kautta maalataan neutraalilla värillä.
- Objektilohkot, jotka eivät ole meshejä (pelilogiikka, efektit, äänet).
- Tuhoutuvien meshien tuhoutuneet tilat: niiden osien paikat ovat tuhoamisasetuksessa, jota ei lueta.
- Navigointiverkon linkit (hypyt, tikkaat, ylitykset) ja sen ajoneuvokerrokset.
- Meshit, joiden tasot on tallennettu resin sisään (10 meshiä kentässä, rekvisiitta), skinnattujen ja yhdistettyjen meshien luut ja osat, sekä normaalit (kirjoittaja laskee ne).
- Normaali-, karkeus- ja muut kartat; muu läpinäkyvyys kuin leikattu (läpinäkyvä lasi ja decalit piirretään läpinäkymättöminä).
- Maaston aukot: aukkojen pinnan varjostin on nimetty, mutta mitä se lukee, ei ole löydetty (katso [Maastokerrokset](#terrain-layers)), joten korkeuskenttää ei leikata siellä, missä kävelykelpoinen maa kulkee sen alla.
- Tekstuurien värikartat ja sävyjen sovitus: sävyt valitaan ensimmäisellä ei-neutraalilla arvolla (katso [Tekstuurit ja materiaalit](#textures-and-materials)).
- Tehosteet (`fx/`-polut) ja kaapelimeshit, joiden rajauslaatikot ovat kymmeniä kilometrejä pitkiä; ne jätetään pois ja lasketaan yhteenvedossa.
- XOR-hämärretty taulukkomuoto.
