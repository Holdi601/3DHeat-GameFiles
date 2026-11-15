---
title: BeamNG-tiedostot
lang: "fi"
source: reader-beamng.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# BeamNG-tiedostot: tasoarkistot, `.ter`, `.cdae`, `.dae`

BeamNG.drive toimittaa tavallisia zip-arkistoja, joten konttia ei tarvitse purkaa
käänteisesti. Työ on kentän lukemisessa **niin kuin peli sen lukee**: arkistojen
liittäminen yhdeksi tiedostojärjestelmäksi, kohtaustiedostojen seuraaminen sekä maaston
ja käännettyjen muotojen dekoodaus. Näihin lukijoihin päästään
[BeamNG.drive](course-beamng.md)-radan viennin kautta. `identify` nimeää myös tasozipin,
`.cdae`:n ja `.ter`:n, ja `list` ja `extract` ottavat minkä tahansa zipin.

Lähteet: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py),
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py).

## Liitetty tiedostojärjestelmä

`Files.of_install(game)` rakentaa yhden isoilla ja pienillä kirjaimilla välittämättömän
hakemiston tiedostoista `gameengine.zip`, `content`-zipit (paitsi ajoneuvot ja äänet) sekä
käyttäjän modit (`mods\*.zip`, `mods\unpacked\*` ja käyttäjän `levels`-kansio). Myöhemmät
lisäykset ohittavat aiemmat, kuten pelissä. Haut eivät välitä kirjainkoosta, koska tasojen
omat viittaukset eivät täsmää arkistojen kanssa (`.DAE` `.dae`:n sijaan). Yksityiskohdat
ovat sivulla [BeamNG.drive](course-beamng.md#the-file-system).

`resolve()` löytää polun niin kuin peli: sellaisenaan, suhteessa tiedostoon, joka sen
nimesi, `x.png` kuin `x.dds`, `x.dae` kuin `x.cdae` (suositeltu), ja `x.png.link`-JSON-
tiedoston kautta, jonka `path` osoittaa kohtaan `/assets`.

## Kohtaustiedostot

| Lähde | Muoto | Luettu |
|---|---|---|
| `levels\<name>\main\**\items.level.json` | yksi JSON-olio riviä kohden, tai yksi JSON-taulukko tai -kartta | `TSStatic`, `Prefab`, `DecalRoad`, `TerrainBlock`, `WaterPlane`, `WaterBlock`, `River` |
| `levels\<name>\*.mis` | TorqueScript `new Class(name) { field = "value"; ... };` | samat luokat, vanhemmille tasoille ilman `main\`-kansiota |
| `*.prefab` / `*.prefab.json` | TorqueScript tai JSON | lapset sijoitettu esivalmisteen suhteen, enintään 8 tasoa syvälle |
| `levels\<name>\forest\*.forest4.json` | yksi instanssi riviä kohden | tyypitetty `managedItemData.json`-tiedoston `TSForestItemData`-tietueilla (`shapeFile`) |
| `info.json` | JSON | tason otsikko (käännösavaimet ohitetaan) |

**Muunnokset.** `rotationMatrix` on yhdeksän lukua, joiden **rivit** ovat kohteen omat
akselit maailmassa. Tien varrella ketjutetut suojakaidesegmentit kulkevat rivin 0 suuntaan
(92 %), ja ylärivi kallistuu tien kaltevuuden mukaan. Vanhemmat esivalmisteet antavat
`rotation = "x y z degrees"`, oikeakätisen käännön kyseisen kulman verran (92 % kiskoketjuista
asettuu sen mukaan, 19 % vastakkaiseen suuntaan). Skaala kertoo rivit, ja `position` (tai
`pos`) on viimeinen rivi. Esivalmisteen lapsen muunnos yhdistetään esivalmisteen muunnokseen.
Esivalmisteen `groupPosition` on editorin kiertopiste eikä sitä **vähennetä**: rekkaesivalmiste
on maassa vain ilman sitä.

TorqueScript-luvut luetaan toleranssia sallivalla mallilla, koska jotkin toimitetut
esivalmisteet kirjoittavat arvoja kuten `-0.99563-0.0` ilman välilyöntiä.

## Maasto: `.ter`

```
u8 version, u32 size, u16 heights[size x size], u8 layers[size x size],
u32 count, count x (u8 length, name)
```

- Korkeus metreinä: `position.z + h * maxHeight / 65535`, kun `position`, `squareSize` ja
  `maxHeight` tulevat `TerrainBlock`-lohkosta (oletukset 0, 1 ja 2048).
- Rivit kulkevat +y-suuntaan. Ruudukkopiste (i, j) on kohdassa
  `(position.x + i * squareSize, position.y + j * squareSize)`.
- Kerros 255 on reikä.

Tarkistettu: tien solmut ovat maastolla 1–2 cm:n tarkkuudella (mediaani) kolmella tasolla.
`h / 32`, tai muu akselijärjestys, osuu metrien tai satojen metrien päähän.

## Materiaalit

Jokainen `*.materials.json` `levels\`-kansion ulkopuolella, sekä nykyisen tason, indeksoituna
`mapTo`:n, `name`:n ja avaimen mukaan:

| Luokka | Käytetyt kentät |
|---|---|
| `Material`, `CustomMaterial` | värikartta (`baseColorMap`, `colorMap` tai `diffuseMap`, ensimmäinen vaihe), värikerroin, läpinäkyvyyskartta ja kerroin, `alphaTest`/`translucent`, `annotation`, `groundType` |
| `TerrainMaterial` | pohjakartta ja `diffuseSize`, yksityiskohtakartta, koko ja voimakkuus, makrokartta, koko ja voimakkuus, `groundmodelName`, `annotation` |

Kuvat dekoodataan Pillow'lla (DDS, PNG ja muut), käyttäen pienennettyä versiota missä
mahdollista, ja välimuistitetaan kokokohtaisesti. Luettamaton tekstuuri palautuu tasaväriin.

## Käännetyt muodot: `.cdae`

`.cdae` on pelin oma välimuisti jokaisesta Collada-tiedostosta, kirjoitettuna MessagePack-
muodossa. BeamNG **dokumentoi** sen asettelun
(documentation.beamng.com/modding/file_formats/cdae/), ja lukija seuraa sitä:

```
u32 version (low byte must be 31), u32 header size, MessagePack header,
then a MessagePack stream (zstd-compressed if the header says "compression"):
  Torque's TSShape field by field, each array as [count, element size, bytes]
```

Luetaan: rajat, solmut, objektit, `details` (yksityiskohtatasot), solmujen oletuskierrot
(`Quat16`) ja siirrot, jokaisen verkon kärkipisteet, UV:t, normaalit, värit, primitiivit ja
indeksit sekä materiaalinimet. Materiaalinimet löytyvät streamin lopusta, koska animoidun
rekvisiitan sekvenssit tulevat niiden eteen muodossa, jota ei ole dokumentoitu.

Kaksi asiaa, joita dokumentaatio ei täsmennä, todettu `.dae`-tiedostoja vasten, joista
muodot tehtiin:

- **Solmujen kierrot ovat Torquen.** `Quat16` luettuna kirjan mukaan pyörii väärin päin.
  Sen matriisi on **transponoitava**. Sen jälkeen jokaisen solmun maailmarajat täsmäävät
  Colladaan millimetrin tarkkuudella. Ilman sitä ne ovat 38 cm pois mediaanina.
- **Yksiköt ja akselit on jo sovellettu.** Collada-tiedosto, joka on tehty senttimetreissä tai
  Y-ylös, tulee välimuistista metreinä, Z-ylös.

Yksityiskohtatasot ovat `details`, joiden koko on ei-negatiivinen, suurimmasta alkaen.
Negatiiviset koot ovat törmäys- ja näkölinjamalleja, joita ei koskaan piirretä. Nimettyjä
objekteja `colmesh`, `collision`, `los`, `bb_`, `billboard`, `autobillboard` tai `imposter`
ei koskaan piirretä. Piirretään vain standardi- ja lajitellut verkot. Luurankomalleja
(hahmot, ajoneuvot) ja tarramalleja ei piirretä. Kolmioiden nauhat ja viuhkat puretaan, ja
kolmiot käännetään uudelleen vastaamaan tallennettuja normaaleja, mitä Torquen oma kiertosuunta
ei takaa.

Tarkistettu: lähes jokainen toimitettu muoto luetaan. Kaksi muuta ovat vanhempaa versiota.

## Collada-varamenetelmä: `.dae`

Muodoille, joilla ei ole `.cdae`-tiedostoa (modit ja muutama muoto, jonka välimuisti on
vanhempi), Collada-tiedosto luetaan samalla tavalla kuin Torquen tuoja sen lukee, samaan
rakenteeseen:

- Yksityiskohtatasot Torquen nimeämiskäytännöstä: verkkosolmun lopussa oleva numero on
  pikselikoko, jolla se piirretään (`barrier75`, `barrier40`). Negatiivinen numero tai
  nimi `collision`/`Colmesh`/`LOS`/`nulldetail` ei piirry koskaan. Muoto ilman käytäntöä on
  yksi taso.
- Yksiköt `<unit meter>`-tagista, ja Y-ylös käännetään Z-ylösiksi.
- UV:t käännetään välimuistin tavalle (v kulkee alas kuvassa).

Tarkistettu pelin omaa samojen tiedostojen `.cdae`-tiedostoa vastaan: lähes kaikki otannan rajat
1 cm:n sisällä, 583 samalla kolmiomäärällä, 94 % materiaalien UV:istä identtisiä. Asennetun
pelin testi vaatii 90 % enintään 60 muotoparista yhteisestä taiteiden arkistosta täsmäävän
1 cm:n tarkkuudella.

## Ei luettu

- Maanpeite (proseduraalinen ruoho) ja ajonaikaisesti luotu sisältö.
- Animoidut sekvenssit ja skinnaus.
- Ajoneuvot ja äänet (ei koskaan liitetty).
