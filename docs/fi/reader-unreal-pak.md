---
title: Unreal `.pak`
nav_order: 1
lang: "fi"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Listaa ja purkaa** Unreal 4.22–5.x `.pak`-arkistot: versiot 8, 9, 10, 11 ja 12, Zlib-, Gzip- ja
Oodle-pakkaus sekä salatut arkistot, kun annat AES-avaimen. Se ei tulkitse purettua sisältöä
(`.uasset`, `.umap`).

Lähde: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Komennot: `identify`, `list`, `extract` (katso [Komennot](commands.md)).

## Asettelu {#layout}

Alatunniste on tiedoston lopussa, ja se löytyy etsimällä viimeisistä 1 024 tavusta taika
`0x5A6F12E1`. Kenttien järjestys on tärkeä:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Salauslippu on **ennen** taikaa. Jos se luetaan taian jälkeen, lukija osuu Zlib-sanan "Z"-kirjaimeen.
Silloin jokainen arkisto näyttäytyy salattuna, ja jokaisesta pakkausmenetelmän nimestä katoaa ensimmäinen
kirjain ("lib", "odle"). Se on hiljainen ja uskottava virhe. Versio on alin tavu, koska "frozen index" -
koosteet asettavat korkean bitin.

Indeksi kantaa mount-pisteen, polkutiivistehakemiston, täyden hakemistoindeksin ja **koodatut merkinnät**:
bittipakattu muoto, jossa liput-sana kertoo, mitkä luvut ovat 32-bittisiä, pakkausmenetelmän (6 bittiä),
onko merkintä salattu, lohkomäärän (16 bittiä) ja lohkokoon yksiköissä 2 048 (6 bittiä). Kaikki ykköset
lohkokoossa on eskape: todellinen koko seuraa u32:na **ennen** siirtymää. Suuressa arkistossa tämän
lukeminen koon jälkeen siirsi 7 % merkinnöistä neljällä tavulla ja antoi niille siirtymät eksatavuissa.

Jokaisen merkinnän täysi tietue toistetaan juuri ennen sen dataa, joten data alkaa
`8+8+8+20+4+1+4` tavun jälkeen, plus `4 + 16 x blocks`, kun se on pakattu. Salatut lohkot täytetään
16 tavuun.

## Mitä se lukee ja mitä hylkää {#what-it-reads-and-what-it-refuses}

| Tapaus | Tulos |
|---|---|
| versiot 8–12 | luetaan |
| mikä tahansa muu versio | `pak version N; this reader handles 8-12` (vanhemmat versiot tallentavat tasaisen tietuelistan, eikä testitiedostoa ollut) |
| ei alatunnisteen taikaa | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| indeksi tiedoston ulkopuolella | hylätään: alatunniste ei jäsentynyt väitetyllä tavalla |
| vain polkutiivisteindeksi | hylätään: tiedostonimet hashattiin pois rakennusvaiheessa, eikä niitä voi palauttaa |
| merkinnät indeksin ylivuotolistalla (hakemiston siirtymä -1) | ohitetaan, ei väärennetä |
| salattu indeksi, ei avainta | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Komentoriviltä yksi rivi ja poistumiskoodi 1 |
| salattu merkintä, ei avainta | `EncryptedPak` luettaessa |
| menetelmät Zlib, Gzip, Oodle | puretaan (Oodle tarvitsee kirjaston, katso [Oodle](reader-oodle.md)) |
| mikä tahansa muu menetelmä | `compression method '...' is not supported` |

## Avaimet {#keys}

`--key` komennoissa `list` ja `extract` ottaa AES-256-avaimen, jonka jo omistat, 64 heksadesimaalinumeroa,
`0x`:n kanssa tai ilman. Muu hylätään ennen kuin arkisto avataan, poistumiskoodilla 2. Salauksen purku on
AES-256-ECB:llä `cryptography`-paketin kautta. Mikään koodipolku ei hanki avainta: ei toimitettuja avaimia,
ei suoritettavien tiedostojen hakua, ei muistin lukua. Katso [Säännöt ja lisenssit](rules-and-licences.md).

## Todennettu {#verified}

Julkaistuja arkistoja vastaan useammasta pelistä: jokainen merkintä, myös yksi erittäin suuri arkisto,
täsmäsi SHA-1:een, jonka Unreal kirjoittaa jokaisen datan eteen. Se tiiviste kattaa tavut sellaisina kuin
ne on tallennettu, joten täsmäys tarkoittaa, että indeksin dekoodaus, datan siirtymä ja jokainen pakatun
lohkon raja olivat oikein. Asennetun pelin testit (`test_pak.py`) toistavat tämän enintään neljälle
salaamattomalle pakille, jotka löytyvät `steamapps\common\*\...\Content\Paks`-kansiosta. Ne tarkistavat,
että jokaisen merkinnän siirtymä on tiedoston sisällä, ja että SHA-1 täsmää 150 satunnaisesti valitun
merkinnän otannalla jokaisessa arkistossa.
