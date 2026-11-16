---
title: Säännöt ja lisenssit
nav_order: 12
lang: "fi"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Säännöt ja lisenssit {#rules-and-licences}

Kolme sääntöä muovaa koko työkalua. Täysi teksti:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Ei avaimia: ei toimitettuja, ei löydettyjä {#no-keys-none-shipped-none-recovered}

**Työkalu lukee kontteja.** Arkistomuodon jäsentäminen on tavallista tiedostonkäsittelyä, ja FModel,
UModel ja AssetRipper ovat tehneet sen avoimesti vuosia.

**Ratkaiseva raja on salaus, ja se on piirretty työkalun sisään.**

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

## 2. Omat tiedostot {#your-own-files}

Työkalu lukee **koneellesi asennettuja** pelitiedostoja. Se ei koskaan lataa pelisisältöä.

Mitään pelistä ei toimiteta sen mukana: ei pelin sisältöä, ei pelin koodia, ei DLL-tiedostoja. Sen
vienti kirjoitetaan omalle levyllesi eikä minnekään muualle.

3DHeat GameFiles ei ole sidoksissa mihinkään pelijulkaisijaan eikä minkään pelijulkaisijan hyväksymä.
Pelit sekä niihin liittyvät nimet ja tavaramerkit kuuluvat omistajilleen. Oikeudenhaltijat: avatkaa
issue osoitteessa
[github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) -
vastaamme nopeasti ja poistamme pyynnöstä mitä tahansa.

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
  dokumentoituja. Yksikään tässä olevista lukijoista
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
