---
title: Arkistolukijat
nav_order: 9
lang: "fi"
source: archive-readers.md
source_hash: "0f1064f05cfd"
nav_exclude: true
search_exclude: true
---
# Arkistolukijat {#archive-readers}

**Kontti** (tai arkisto) on yksi iso tiedosto, johon peli on pakannut monta
tiedostoa. **CRC** tai hash on lyhyt sormenjälki joistakin tavuista: jos se
täsmää, tavut luettiin oikein. **Rajauslaatikko** on pienin laatikko mallin
ympärillä.

Komentojen alla on lukijat niille konteille, joita pelit toimittavat. Niiden
muodot eivät ole dokumentoituja, paitsi Valven VPK ja BeamNG:n `.cdae`. Siksi
"tuettu" tarkoittaa **todennettu oikeita tiedostoja vastaan**, ei "ei kaatunut".
Jokainen lukija tarkistaa itsensä jollakin, minkä muoto takaa: tiivisteellä, CRC:llä,
siirrosketjulla joka täytyy sulkeutua tai tallennetulla rajauslaatikolla. Kun
tarkistus epäonnistuu, lukija kieltäytyy antamasta viestiä eikä arvaa. Väärä
malli näyttää oikealta, kunnes joku asettaa sen radan viereen.

| Lukija | Moduuli | Lukee | Ei lue | Tulee käytettyä kohdasta |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | versiot 8-12: hakemisto, merkinnät, Zlib-, Gzip- ja Oodle-lohkot, AES jolla on avain jonka annat | versiot ennen 8:aa, pelkän polkutiivisteen hakemistot, ylivuotomerkinnät, resurssien sisällöt | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, todennettu v8:lla), zen-paketit, versiottomat ominaisuudet muutamalle komponenttiluokalle, leikatut staattiset mallit, tekstuurit, suoratoistettavat virtuaalitekstuurit | salatut kontit, versiolliset paketit, pelkästään Nanite-mallit, muiden luokkien ominaisuudet | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | Oodle-lohkot koneella jo olevan kirjaston kautta | kaikki ilman sellaista kirjastoa; sitä ei koskaan toimiteta mukana | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile`-muoto 22 ja uudempi (Unity 2020–6000), `UnityFS`-paketit, pakkaamattomat mallit, `.resS` mukaan lukien | ennen 2020:tä olevat muodot, upotetut tyyppipuut, pakatut mallit, muu luokka kuin `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | `.toc`-DbObject-puut ja binääriset osiotaulukot, asennuspaketit, palojen sijainnit, sisäiset paketit ja niiden luettelot, RIFF EBX -osiot, MeshSet-mallit, maaston korkeuskenttä, BC1/BC3/BC7-tekstuurit ja niiden varjostinlohkot, staattisten mallien ryhmien sijoittelu | XOR-hämärretyt taulukot, maaston lähimaan väri ja aukot, normaalikartat, muu alfa kuin leikkausreiät | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | versiot 1 ja 2, jaetut arkistot, esilatausdata, CRC-tarkistus | käännetyt assetit (`.vmdl_c`, `.vtex_c`), CS2:n navigointiverkon muoto | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, tallentamaton), `.modelbin`-geometria, `.pb`-näytteet (BC1, BC7, RGBA), `.pgeo`-sijoittelut, materiaalien tekstuurihashit | muut kärki- ja indeksimuodot, muut tekstuurimuodot, maaston varjostimen kerrokset | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` ja `extract` (`.minizip`) |
| [BeamNG-tiedostot](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | liitetty zip-tiedostojärjestelmä, kohtauksen JSON ja TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiaalit | taipuvat ja tarrat-mallit, animoidut sekvenssit, proseduraalinen maanpeite | `course` (BeamNG), `identify` (zipit, `.cdae`, `.ter`), `list` ja `extract` (zipit) |

## Säännöt, joita jokainen lukija noudattaa {#rules-every-reader-follows}

- **Ei toimitettuja avaimia, ei löydettyjä avaimia.** Salattu arkisto aukeaa
  vain avaimella, jonka annat (Unreal `.pak`, `--key`). Salattu IoStore-kontti
  hylätään. Mitään ei etsitä suoritettavasta tiedostosta avainta, eikä toisen
  prosessin muistia lueta. Katso [Säännöt ja lisenssit](rules-and-licences.md).
- **Ei suljettua koodia mukana.** Oodle ladataan pelistä tai moottorista, joka
  on jo asennettu koneelle.
- **Kieltäydy sen sijaan, että arvaat.** Tuntematon versio, pakkausmenetelmä,
  kärkimuoto tai tekstuurimuoto aiheuttaa oman virheen, esimerkiksi
  `texture format 42 has not been identified; refusing to guess`.
- **Vain luku.** Yksikään lukija ei kirjoita pelikansioon. Viennit menevät sinne,
  minne sanot.

## Mitä "todennettu" tarkoitti {#what-verified-meant}

Näiden sivujen todennusluvut tulevat moduulien docstringeistä. Ne mitattiin
asennettuja pelejä vastaan, kun kukin lukija kirjoitettiin. Synteettiset testit
(katso [Kehitys](development.md)) lukitsevat kenttien asettelut. Asennettujen
pelien testit toistavat osan tarkistuksista, kun peli on koneella, ja ohittavat
ne muuten. Testaamattomia lukuja ei ole tarkistettu uudelleen sen jälkeen.
