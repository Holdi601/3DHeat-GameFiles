---
title: Unity
nav_order: 4
lang: "fi"
source: reader-unity.md
source_hash: "21d52b5357fb"
nav_exclude: true
search_exclude: true
---
# Unity: `SerializedFile`, paketit, mallit {#unity-serializedfile-bundles-meshes}

**Listaa objektit ja dekoodaa mallit** Unity `SerializedFile`-muodosta 22 ja uudemmasta
(Unity 2020–6000), ja avaa `UnityFS`-paketit. Unitylle ei ole radan vientiä.

Lähteet: [`unity.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity.py),
[`unity_mesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unity_mesh.py).
Komennot: `identify` (kontit ja paketit), `meshes` (vain paljaat kontit).

## Kontti {#the-container}

Unity toimittaa tason sarjallistettuina objektigraafeina: `globalgamemanagers`,
`sharedassets*.assets`, `resources.assets`, `level*` ja assettipaketit. Jokaisessa on
objektitaulukko, jossa jokainen objekti on merkitty luokkatunnuksella.

Otsikko on se kohta, jossa luku menee hiljaa pieleen. Ensimmäiset kuusitoista tavua ovat neljä
big-endian `uint32`:a, jotka säilytetään yhteensopivuuden vuoksi. Muodossa 22 kolme niistä on
nollia, ja todelliset arvot seuraavat, koska tiedosto voi ylittää 4 Gt:n:

```
[legacy metadata size : 4] [legacy file size : 4] [format version : 4] [legacy data offset : 4]
[endianness : 1] [reserved : 3]
[metadata size : 4] [file size : 8] [data offset : 8] [unknown : 8]
```

Toinen `metadata size` on `uint32` kahden `int64`:n välissä. Jos kaikki kolme oletetaan 64-bittisiksi,
versiomerkkijono tulee neljä tavua myöhässä. Se dekoodautuu silti merkkijonon näköiseksi ja lähettää
kaiken sen jälkeisen harhaan. Otsikko on big-endian. Kaikki sen jälkeen seuraa endianness-tavua
(0, little-endian, jokaisessa pöytäkoneen versiossa).

Otsikon jälkeen: moottorin versiomerkkijono, alusta, tyyppipuun lippu, tyyppitaulukko (luokkatunnus
tyypeittäin), objektitaulukko (polku-ID, siirtymä, koko, tyyppi) ja ulkoiset viittaukset (muut
tiedostot, joihin osoitin voi viitata).

| Tapaus | Tulos |
|---|---|
| muoto 22–30 | luetaan |
| muoto 9–21 (ennen Unity 2020:tä) | hylätään: siirtymät ovat vanhassa otsikossa, eikä yksikään käytettävissä oleva tiedosto käyttänyt sitä |
| muu kuin 9–30 | hylätään |
| upotettu tyyppipuu (editoriversiot) | hylätään: toimitetut versiot eivät upota sitä, eikä editorireittiä ole toteutettu |
| paketti annetaan paikassa, jossa odotetaan konttia | hylätään, ja osoitetaan paketinlukijaan |

Yleistä deserialisoijaa **ei ole**. Toimitetut versiot eivät kanna tyyppipuuta, koska skeema on
käännetty pelaajaan, joten jokainen luokka täytyy jäsentää versionsa tunnetussa asettelussa. Vain
`Mesh` dekoodataan. Muut luokat raportoidaan nimellä ja määrällä (`GameObject`, `Transform`,
`MeshRenderer`, `MeshFilter`, `Mesh`, `BoxCollider`, `MeshCollider`, `MonoBehaviour`, `MonoScript`,
`AssetBundle`, `RectTransform`, `PrefabInstance`; muut `class<id>`).

**Todennettu** monissa asennetuissa peleissä ja miljoonissa objekteissa: objektitaulukon on peitettävä
datapala täsmälleen, ilman päällekkäisyyksiä, ja objektien välissä on vain tasaustäytettä, ja viimeinen
objekti päättyy tiedoston viimeiseen tavuun. Väärin luettu otsikko ei voi tuottaa tätä. Asennetun pelin
testi toistaa sen enintään kuudelle `resources.assets`- / `sharedassets0.assets`-tiedostolle, jotka
löytyvät `*_Data`-kansioista.

## Paketit (`UnityFS`) {#bundles-unityfs}

Paketti on pakattu säiliö SerializedFile-tiedostoista. Lohkolista ja hakemisto ovat myös pakattuja.
Menetelmä on liput-sanan alimmissa kuudessa bitissä: 0 tallentamaton, 1 LZMA (Unityn 5 tavun otsikko,
johon koko on liitetty), 2 ja 3 LZ4 / LZ4HC. Muoto 7 ja uudemmat tasaavat otsikon 16 tavuun. Lippu
`0x80` asettaa hakemiston tiedoston loppuun. `UnityWeb`, `UnityRaw` ja `UnityArchive` (ennen 5.3:a)
tunnistetaan, mutta niitä ei lueta.

## Mallit {#meshes}

`read_mesh` dekoodaa `Mesh`-objektin sijainneiksi, normaaleiksi, ensimmäiseksi UV-joukoksi ja
kolmioiksi siinä järjestyksessä, jossa Unity 2019+ ne kirjoittaa: nimi, alimallit, sekoitusmuodot
(ohitetaan), bind-asennot ja luudata (ohitetaan), pakkaus- ja luettavuusliput, indeksipuskuri,
kärkikanavat ja kärkidata, pakatun verkon lohko, paikallinen rajauslaatikko ja suoratoistotiedot.

- **Ulkoiset kärjet.** Suurin osa toimitetusta geometriasta on `.resS`-tiedostossa säiliön vieressä.
  Työkalu lukee sen säiliön kansiosta (tallennetun `archive:/...`-polun tiedostonimi käytetään
  vain). Puuttuva `.resS` on virhe, ei tyhjä malli.
- **Virrat ja kanavat.** Kanavat kertovat, mistä virrasta, siirtymästä, muodosta ja ulottuvuudesta
  kukin attribuutti tulee. Virrat on pakattu peräkkäin, jokainen 16 tavun täytettynä, joten virran
  alku kertyy sitä edeltävistä askelista. Muodot: float32, float16, unorm/snorm 8 ja 16 (normalisoitu)
  ja tavalliset kokonaisluvut.
- **Topologia.** Vain kolmiot (topologia 0). Nauhat, nelikulmiot ja viivat hylätään, koska väärin
  tehty muunnos näyttää oikealta geometrialta.
- **Pakatut mallit** (kvantisoidut deltat) hylätään: "mesh '...' is stored compressed; that encoding is
  not implemented".

### Itsetarkistus {#the-self-check}

Struktuurin lukeminen väärässä järjestyksessä ei nosta virhettä. Se tuottaa uskottavia lukuja. Siksi
jokainen dekoodattu malli tarkistetaan **Unityn tallentamaa rajauslaatikkoa** vastaan, jonka editori
laski oikeista kärjistä. `aabb_matches()` läpäisee, kun dekoodatun laatikon kulmat ovat 2 %:n sisällä
tallennetun laatikon koosta. `meshes` tulostaa `ok` tai `BOUNDS DISAGREE` jokaiselle riville.

**Todennettu:** mallit otannalla useista peleistä dekoodautuvat ja niiden rajat täsmäävät. Asennetun
pelin testi toistaa tarkistuksen asennetuille konteille.

## Ei toteutettu {#not-implemented}

- Ennen 2020:tä olevat muodot.
- Pakatut mallit.
- Muu luokka kuin `Mesh`: ei kohtausgraafia, muunnoksia eikä materiaaleja, joten mallit ovat omassa
  paikallisessa avaruudessaan.
- `meshes` paketille. Paketinlukija on olemassa Pythonissa (`UnityBundle.serialized_files()`), mutta
  komento ottaa paljaan kontin.
