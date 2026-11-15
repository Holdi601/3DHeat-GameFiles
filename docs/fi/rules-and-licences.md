---
title: Säännöt ja lisenssit
nav_order: 12
lang: "fi"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Säännöt ja lisenssit {#rules-and-licences}

Kolme sääntöä muovaa koko työkalua. Ne ovat suunnittelupäätöksiä, eivät pelkkiä vastuuvapauslausekkeita.
Täysi teksti: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Tämä sivu on kirjaus siitä, mitä lisenssit sanovat, ei oikeudellinen neuvo.

## 1. Ei avaimia: ei toimitettuja, ei löydettyjä {#no-keys-none-shipped-none-recovered}

**Työkalu lukee kontteja.** Arkistomuodon jäsentäminen on tavallista tiedostonkäsittelyä, ja FModel,
UModel ja AssetRipper ovat tehneet sen avoimesti vuosia. Kontin jäsentäminen ei sinänsä ole kiertämistä.

**Ratkaiseva raja on salaus, ja se on piirretty työkalun sisään.** Työkalu, jonka tarkoitus on
kumota käyttöoikeuden hallinta, on itsessään anti-kiertolainsäädännön piirissä (DMCA §1201(a)(2)
koskee tekniikoita, ei pelkästään tekoja), vaikka kukaan ei jakaisi yhtäkään purettua tiedostoa.
Siksi:

- **Ei toimitettuja avaimia.** Koodissa tai datassa ei ole avainta.
- **Ei avainten palautusta.** Mitään ei etsitä suoritettavasta tiedostosta avainta, eikä toisen prosessin
  muistia lueta.
- **Avain, jonka sinulla on, tai ei mitään.** Salattu Unreal `.pak` aukeaa vain `--key <hex>`-valinnalla
  (Pythonissa `PakArchive(path, aes_key=...)`). `pak.py`:ssä ei ole koodipolkua, joka hankkisi avaimen.
  Salattu IoStore-kontti hylätään suoraan.
- **Hämärrystä ei myöskään toteuteta.** Frostbiten XOR-hämärretyt taulukot pitävät avaimensa itse
  tiedostossa, joten ne ovat hämärrystä eivätkä käyttöoikeuden hallintaa. Ne tunnistetaan silti ja
  jätetään käsittelemättä, koska mikään käytettävissä oleva tiedosto ei käytä sitä muotoa, eikä
  toteutusta olisi mihin verrata. Assetto Corsa EVO:n avainpaketti hylätään samasta syystä kuin
  avainsääntö.
- **Salatut tiedostot pysyvät suljettuina.** Battlefield 6:n alkuperäinen tiedostojärjestelmä, joka
  pitää pelin tyyppikirjaston, on salattu, eikä sitä lueta. Kentän vienti toimii salaamattomista
  tiedostoista ja muodostaa tarvittavat kaksi tyyppiä datasta.
- **Mitään ei injektoida pelin prosessiin.** Telemetria tulee syötteistä, jotka pelit itse julkaisevat, ja
  tallennus käyttää julkisia näytön tallennusrajapintoja (muissa 3DHeat-työkaluissa). Injektointi peliin,
  jossa on huijauksenesto, vaarantaa sen käyttäjän tilin, joka sitä ajaa.

Jokainen tähän mennessä testattu arkisto on salaamaton.

## 2. Omat tiedostot, oma vastuu {#your-own-files-your-responsibility}

Työkalu lukee **koneellesi asennettuja** pelitiedostoja. Se ei koskaan lataa pelisisältöä.

Mihin osoitat, on edelleen sinun vastuullasi. Peleillä on omat lisenssiehdot, ja EULA:t kieltävät
usein käänteisen suunnittelun. Ne ovat täytäntöönpanokelpoisia sopimuksia, ja velvollisuus on sillä,
joka työkalua ajaa, millä tahansa pelillä. Mikään tämän työn suunnitteluratkaisu ei vapauta siitä.
Selvin lailliselle tapaus on kehittäjä, joka lukee oman studionsa buildia: eri tiimin tuotetta, vanhaa
haaraa tai kumppanin buildia.

## 3. Tulos ei ole jaettavaksi {#output-is-not-for-redistribution}

Ulos tulee geometriaa **spatiaalista kontekstia** varten: maa, tie ja sen vieressä oleva, pienennettynä
budjettiin, jotta kierroksia voi analysoida paikallaan. Se on pienin osa arkiston sisällöstä, ja se on
silti pelijulkaisijan sisältöä.

- Säilytä viedyt `.glb`-tiedostot ja niiden sisällä olevat tekstuurit omaan analyysiisi.
- Älä julkaise, jaa tai myy vietyjä ratoja, kenttiä, malleja tai tekstuureja.
- Repositorion `.gitignore` pitää pelitiedostot, viennit, kierrokset ja tallenteet versionhallinnan
  ulkopuolella kansioittain ja tiedostotyypeittäin (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`,
  `*.lap.json` ja muut).

## Oodle löydetään, sitä ei toimiteta mukana {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nyt Epic) on omistusoikeudellinen, eikä sillä ole jaettavaa buildia.
`oo2core_*.dll` on lisensoitu tuotteelle, joka sen toimittaa. Siksi `oodle.py` lataa koneella jo olevan
kirjaston sen sijaan, että mukana olisi yksi. Tämä on järjestely, jota lisenssi tarkoittaa, ja sama, jota
FModel ja UModel käyttävät. Katso [Oodle](reader-oodle.md).

## Muodot itsessään {#the-formats-themselves}

- `.pak`, IoStore, Unityn `SerializedFile`, Frostbiten `.toc` ja ForzaTechin muodot eivät ole
  dokumentoituja. Niiden lukeminen on kontin käänteistä suunnittelua. Yksikään tässä olevista lukijoista
  ei perustu toisen projektin lähdekoodiin. Frostbitelle julkiset kuvaukset vanhemmista versioista
  (Frosty-mallinnustyökalut, Need for Speed Heat -formaattihuomautus, GDC-esitys) antoivat kenttänimiä ja
  kartan siitä, mitä etsiä. Koodia ei otettu; jokainen siirtymä mitattiin tiedostoista (katso
  [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Puretut tasot ovat omaa käyttöäsi varten. Työkalu kirjoittaa ne omalle levylle eikä mihinkään muualle; älä
  julkaise niitä.
- BeamNG julkaisee `.cdae`-asettelunsa, ja lukija seuraa sitä.
- Valve dokumentoi VPK:n.
- Unreal 5:n käännetty ominaisuusdata tarvitsee kunkin luokan ominaisuuslistan. Listat `unversioned.py`:ssä
  ovat **vain nimiä ja tyyppejä**, tosiseikkoja muodosta, kuten yhteentoimivuus-kartoitustiedosto sisältää.
  Ne johdettiin Unreal Engine -otsikoista, jotka Epic tarjoaa jokaiselle linkitetyn tilin omistajalle, ja
  tarkistettiin toimitettua dataa vastaan. Moottorin lähdekoodia ei ole mukana eikä sitä tarvita.

## Tämän työkalun lisenssi {#this-tools-licence}

Kaikki tälle repositoriolle kirjoitettu on **MIT-lisenssin** alla
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): käytä, muuta, toimita,
kaupallisesti tai ei.

Kolmannen osapuolen paketit, kaikki sallivia, joten viejällä ei ole omia rajoituksia:

| Paketti | Lisenssi | Käyttö |
|---|---|---|
| numpy | BSD-3-Clause | mallien dekoodaus |
| cryptography | Apache-2.0 / BSD-3-Clause | vain arkistoille, joihin sinulla on avain |
| lz4 | BSD-3-Clause | Forza-arkistot, osa Unity-paketeista, IoStore-LZ4-lohkot |
| Pillow | MIT-CMU (HPND) | lohkopakatut tekstuurit, JPEG-tulos |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | muutama zstd-pakattu `.cdae`, Frostbiten zstd-lohkot |
| pytest | MIT | vain kehitykseen |

Lisenssit luettiin paketin metatiedoista syyskuussa 2026. Jos komponentin ehdot muuttuivat sen jälkeen,
lähde on ratkaiseva.
