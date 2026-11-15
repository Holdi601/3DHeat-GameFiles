---
title: ForzaTech
lang: "fi"
source: reader-forzatech.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# ForzaTech: `.minizip`, `.modelbin`, näytteet, sijoittelut

Forza Horizon toimii ForzaTechillä, Turn 10:n omalla moottorilla. Nämä lukijat vievät radan
arkistoistaan asti sijoitettuihin, teksturoituihin kolmioihin. Niihin päästään
`course`-, `courses`- ja `terrain`-komennoilla (katso [Forza Horizon](course-forza-horizon.md)).
`identify` tunnistaa `.minizip`-tiedoston ja paljaan `.modelbin`-tiedoston, ja `list` ja
`extract` ottavat `.minizip`-tiedoston, joko nimien mukaan `ChunkContentsMiniZip<n>.txt`-
tiedostosta vierestä tai merkintänumeron mukaan (`#12`).

| Muoto | Moduuli |
|---|---|
| `.minizip`-arkistot ja niiden nimilistat | [`minizip.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/minizip.py) |
| `.modelbin`-mallit ja maasto | [`forzatech.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatech.py) |
| `.pb`-tekstuurinäytteet | [`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py) |
| `.pgeo`-sijoitustiedostot | [`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py) |
| `AssetManifest.xml` ja materiaalien tekstuurihashit | [`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py) |
| maalaatat paikan mukaan | [`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py) |

Forza pitää osan sisällöstään myös tavallisissa ZIP-arkistoissa `media\`-kansion alla.
Pythonin `zipfile` avaa ne, ja `forzatech.models_in_archive()` listaa niiden `.modelbin`-
merkinnät. Radan geometria on `.minizip`-arkistoissa.

## `.minizip`: arkisto ilman nimiä

Rata toimitetaan neljänä `GeoChunk<n>.minizip`-arkistona, avoimen maailman kartalle kukin
kymmeniä gigatavuja, satojentuhansien merkintöjen kanssa. **Arkistot eivät tallenna nimiä
lainkaan**: ei nimitaulukkoa eikä merkintäkohtaista otsikkoa, vain järjestysnumeron. Nimet
ovat `ChunkContentsMiniZip<n>.txt`-tiedostossa jokaisen arkiston vieressä, yksi rivi
merkintää kohden merkintäjärjestyksessä (`<build path>zipcache\pc\<path>|<bundle>`). Tuo
pari on ainoa tapa pyytää tiedostoa. Kaikki `zipcache\pc\`-kohtaan asti pudotetaan, ja
haut eivät välitä kirjainkoosta.

```
u32 'PGZP', u32 version (101), u32 header bytes (32), u32 entries,
u32 bundles, u32 entries per segment (512), u32 segments, u32 0
u32 bundle_start[bundles + 1]
padding to an 8-byte boundary
segments x:  u64 segment base (absolute), then (u32 offset, u32 size, u32 flags) x up to 512
```

Indeksin kolme yksityiskohtaa tuottavat yhä tulosta, vaikka ne luettaisiin väärin. Lukija
hoitaa kaikki kolme oikein:

| Yksityiskohta | Mitä huolimaton lukija tekee | Miltä se näyttää |
|---|---|---|
| segmentin perusta on **64-bittinen** | lukee sen u32:na ja täytteenä | oikein ensimmäiset 4 Gt, sitten oikean pituinen kohina |
| perusta on **8-tavuun tasattu** | ohittaa täytesanan pakettitaulukon jälkeen | arkistoissa, joissa on parillinen pakettimäärä, jokainen merkintä väittää koodekkia, jota ei ole |
| merkinnän tallennettu pituus on väli seuraavaan merkintään (tai seuraavan segmentin perustaan) **miinus sen täyte** (lippubitit 12–13) | käyttää koko väliä | LZ4 hylkää lohkon kokonaan |

Koodekit ovat lippujen alemmat viisi bittiä: `0x00` tallentamaton, `0x08` raaka deflate,
`0x1F` LZ4-lohko. Muu hylätään. Jokaisen merkinnän on purkauduttava täsmälleen ilmoittamaansa
kokoon, muuten se hylätään. Indeksi (noin 5 Mt) luetaan kerran, ja datat luetaan hakemalla.

Otsikko tarkistetaan: taika, 32 tavun otsikko ja segmenttimäärä, joka täsmää
`ceil(entries / per segment)`-lausekkeen kanssa.

**Todennettu:** merkinnät otannalla jokaisesta kartan arkistosta, ja jokainen purkautuu
täsmälleen ilmoitettuun pituuteensa kaikilla kolmella koodekilla.

## `.modelbin`: palakontti

```
"burG" (the FourCC "Grub", little-endian), u32 version, u32 name-table offset, u32 file size, u32 chunk count
chunk count x 24 bytes: tag (reversed FourCC), flags, name offset, data offset, size, stored size
```

- Ilmoitetun tiedostokoon on oltava sama kuin todellinen koko.
- **Ketju:** jokainen pala alkaa siitä, mihin edellinen päättyi, pyöristettynä ylöspäin 4 tavuun.
  Mikään tiedosto ei sano tätä, joten se on todiste: väärällä askeleella luettu tietue ei tuota
  tätä. Se piti kaikilla 252 otannan mallilla.
- `PGZP`-tiedosto, joka annetaan mallilukijalle, nimetään "ForzaTech .minizip -arkistoksi, ei
  malliksi" ja osoitetaan `minizip.py`:lle sen sijaan, että se hylättäisiin tyhjästi.

Geometria tulee näistä paloista:

| Pala | Sisältää |
|---|---|
| `VLay` | kärkiasettelun: attribuuttinimet, sitten elementit (u16 nimen indeksi, u16 kanava, puskuri, DXGI-muoto, siirtymä); elementtimäärä on u16 |
| `VerB` | kärkipuskurin 16 tavun otsikon takana (määrä, koko, u16 askel, u16 attribuutit, muoto) |
| `IndB` | indeksipuskuri, sama otsikko |
| `Mesh` | yksi alimalli: materiaali, tason maski, indeksialue, asettelu, puskuri, askel, muunnelmataulukko ja sijaintilaatikko lopussa |
| `MatI` | materiaali-instanssi: sen `.materialbin`-polku ja tekstuurihashit |

### Sijainnit ja laatikko

Sijainnit ovat `R16G16B16A16_SNORM`-muodossa (muoto 13): neljä etumerkillistä lyhyttä
kärkeä kohden. `position = short / 32767 * scale + bias`, missä skaala ja bias ovat
`Mesh`-palan kahdeksan viimeistä tavua (kaksi float4:ää). Bias on **pelin maailmakoordinaateissa**,
joten maalaatta osuu oikeaan kohtaan pelin sijoittamana ilman instanssimuunnosta. Siksi
telemetrian kierros riittää kartan palan pyytämiseen. Jokaisella mallin alimallilla on sama
laatikko (tarkistettu 860:lla).

### Kärkiasettelu

Yksi sijaintipuskuri kattaa kaikki kärjet. Muut attribuutit on jaettu peräkkäisiin kärkiryhmiin,
joilla kullakin on oma puskuri ja oma asettelu: lähellä liittymää oleva tie kantaa kolmea UV-
joukkoa ja kahta tangenttia, sen vieressä oleva penkka vain normaalin. Jokainen muu attribuutti
on neljä tavua. Mikä asettelu kuvaa mikäkin puskuri, otetaan alimalleista, jotka piirtävät
puskurista, koska asettelut ja puskurit eivät ole samassa järjestyksessä (sama, yhden verran
kierrettynä tai permutoituna, mallista riippuen).

| DXGI-muoto | Koodi | Käyttö |
|---|---|---|
| R16G16B16A16_SNORM | 13 | sijainti (neljäs lyhyt on normaalin x) |
| R16G16_SNORM | 37 | normaalin y, z |
| R16G16_UNORM | 35 | UV-pari (kanava = mikä joukko) |
| R8G8B8A8_UNORM | 28 | väri tai sekoituspainot |
| R10G10B10A2_UNORM | 24 | tangentti (ei dekoodattu) |
| R16_UINT | 57 | indeksit |

**Normaali on jaettu.** `NORMAL` sisältää y:n ja z:n. x on sijainnin neljäs lyhyt, jota pidettiin
täytteenä. Satojentuhansien maaston kärkien yli se korreloi +0,92 kolmion normaalin x:n kanssa ja
kenenkään muun kanssa. Sen avulla 96 % rinteiden kärjistä on 18 asteen sisällä lasketusta
normaalista. Jokainen kaksikomponenttinen koodaus, joka kokeiltiin ilman sitä (oktaedrinen kaikissa
48 järjestelyssä mukaan lukien), sai y:n ja z:n oikein ja x:n väärin.

Muut sijainti- tai indeksimuodot **hylätään** ("only 13 (four shorts, scaled) is implemented";
"only unsigned shorts are implemented").

### Alimallit

`Mesh`-tietue on 238 tavua tavallisessa muodossa. Pidemmät kantavat pidemmän materiaali-
**muunnelmataulukon** alussa, 238 + 8 x count - 4 tavua, ja jokainen kenttä sen jälkeen siirtyy
taaksepäin täsmälleen saman verran. Lyhyemmät (218 tavua, osa maastosta) pitävät siirtymänsä.
Jokainen muunnelmamerkintä on `u16 0xFFFF, u16 summer material, u16 0xFFFF, u16 winter material`.
Yksityiskohtatason maski on u16, yksi bitti tasoa kohden bitistä 1 alkaen.

Mitään ei luoteta yksin. Indeksialueiden on peitettävä indeksipuskuri täsmälleen, jokaisen
`index count` on oltava 3 x `triangles`, ja alimallin nimeämän askelen on oltava sen puskurin.
Taulukko, joka ei täsmää, hylätään kokonaan, koska kolmioiden nimeäminen väärin luetuista
kentistä on huonompaa kuin ilman nimeä. Tuhansien otannan alimallien joukossa jokainen, jonka
puskuri-indeksi on alueella, läpäisee.

### Materiaalit ja tekstuurihashit

`MatI` nimeää materiaalinsa `Game:...\x.materialbin`-polulla, joka löytyy etsimällä palasta.
Sen tekstuurit ovat `u32 slot, u32, u32 hash` -tietueita, 33 tavun välein ja tasaamattomina,
joten pala etsitään jokaisesta tavuoffsetista sanoille, jotka ovat tunnettuja tekstuurihashejä.
Ne tulevat radan `AssetManifest.xml`-tiedostosta
(`<Texture Source="...\name.swatch" SourceHash="...">`, luettuna `</Textures>`-merkkiin asti).
Paikka `0x88B483AA` on standardivarjostimen peruskerroin. Miten väritekstuuri sitten valitaan, on
sivulla [Forza Horizon](course-forza-horizon.md#which-texture).

## `.pb`: tekstuurinäytteet

Näyte on sama `burG`-kontti kuin malli: 96 tavun `HCXT`-otsikko tavusta 44 alkaen, sitten yksi
pikselipala. Otsikko kantaa tekstuurin GUID:n (se, joka on sen tiedostonimessä), leveyden ja
korkeuden, mip-määrän ja **muototunnuksen tavussa 72** (ForzaTechin oma numerointi). Tavu 84
kantaa pikselitavujen määrän.

| Koodi | Muoto | Tunnistettu |
|---|---|---|
| 0 | BC1, puoli tavua pikseliä kohden | dekoodautuu punaiseksi ja valkoiseksi reunakiveksi (BC4:llä kohinaa) |
| 9 | BC7, yksi tavu pikseliä kohden | dekoodautuu maalaataksi, jossa rata näkyy |
| 13 | RGBA8, neljä tavua pikseliä kohden | tavallinen |
| muu | hylätään | "texture format N has not been identified; refusing to guess" |

Muodot tunnistettiin dekoodaamalla oikeita tiedostoja kaikilla tavoilla, joilla
datakoko sallii. Tavu 47, jota aiempi versio piti muotona, on 4 jokaisessa otannan
tekstuurissa. Vain tiedoston ylin mip dekoodataan. Jokainen resoluutio on oma merkintänsä,
`<name>_<guid>_quality<n>.pb`, laatu 1 pienimmästä 5 suurimpaan. Maastokartoissa kaksi suurinta
ovat eri arkistossa kuin muut. Dekoodaus kulkee Pillow'n BCn-dekooderin kautta, generoidun
DDS-otsikon kautta.

## Sijoitustiedostot (.pgeo)

Yksi tiedosto kategoriaa ja spatiaalista solua kohden:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Pelkkä polku kertoo solun
neliön ja kategorian, joten tiedostoja voi suodattaa avaamatta niitä.

```
u32 length, name                 cell and section, for humans
u32 0, u32 13, u32 15
f32 x 8                          box: min xyz, pad, max xyz, pad
u32 length, CATEGORY
... a table of variant names (bare names) ...
per model:
  u32 length, <model name>_3D
  u32 count (1..200,000)
  count x 80 bytes:
    0-11   position: 3 x sign-magnitude 16.16 fixed point
    12-23  the model's x axis in the world (3 x f32)
    24-35  its y axis (3 x f32); z = x cross y
    36-47  scale (3 x f32)
    48-59  unknown
    60-63  material variant (u32)
    64-79  not needed to place it
```

Miten jokainen kenttä päätettiin:

| Kenttä | Ratkaistu |
|---|---|
| sijainti on 16.16 kiinteä piste, ei osuus laatikosta | peräkkäiset suojakaiteet ovat tasan 4,000 m:n päässä toisistaan (mallin pituus) |
| etumerkki-suuruus, ei kahden komplementti | kahden komplementti vei negatiiviset koordinaatit kymmenien kilometrien päähän kartalta; kun bitti 31 on etumerkki, jokainen tiedoston laatikon kategorian tietue osuu laatikkoonsa |
| vektorit ovat mallin omia akseleita | jokaisen suojakaiteen pää osuu seuraavan alkuun: 93,5 % 5 cm:n sisällä, mediaani 0,000 m |
| tavu 60 on muunnelma | silta, jolla on viisi kopiota, lukee 0, 2, 2, 3, 4, kun jokainen suojakaide lukee 0 |

Vain nimet, jotka päättyvät `_3D`:hen, ovat mallitietueita. Muunnelmataulukko ennen niitä listaa
nimet ilman päätettä, ja jos ne luettaisiin tietueina, ne osuisivat äärettömyyteen. Ehdokas-
tietue hyväksytään vain, jos sen määrä mahtuu tiedostoon, ja ei-äärellisiä lukuja sisältävät
ilmentymät pudotetaan.

## Ei toteutettu

- Muut kärki- ja indeksimuodot kuin yllä olevat (hylätään).
- Muut tekstuurimuodot kuin 0, 9, 13 (hylätään).
- Tangentit (ohitetaan, ei käytetä).
- Maaston varjostimen materiaalikerrokset. Maatekstuuri on tulkinta laattakartoista (katso [Forza Horizon](course-forza-horizon.md#the-ground-texture)).
