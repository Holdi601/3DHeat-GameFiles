---
title: Assetto Corsa Rally
lang: "fi"
source: course-assetto-corsa-rally.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Radan vienti: Assetto Corsa Rally

Assetto Corsa Rally on rakennettu Unreal Engine 5:llä (5.6.1, muokattu versio),
ja se toimittaa sisältönsä IoStore-konteissa. Mikään niistä ei ole salattu.
Vienti löytää vaiheen ja akselien suunnan kierroksesta. Se kirjoittaa vaiheen
omat maaruudut, jaettuna tieksi ja maastoksi. Tekstuuri tulee vaiheen
paistetusta maanväristä. Muut mallit saavat tasaisia värejä luokittain.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Lähteet: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (asennus, vaiheet, sijoittelu),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (vienti).
Niiden alla olevat Unreal-lukijat ovat sivulla [Unreal 5 IoStore](reader-unreal-iostore.md),
ja purkaminen sivulla [Oodle](reader-oodle.md).

**Tila:** tarkistettu asennetulla pelillä, kierroksilla jotka luotiin
satunnaiseen kehykseen jokaisella vaiheella. Se löysi oikean vaiheen ja kehyksen
joka kerta. Peli itse tallentamaa kierrosta ei ole vielä viety tämän läpi.

## Asennuksen löytäminen

- `--install <folder>`: pelikansio, sen `Content\Paks` tai mikä tahansa kansio,
  jossa on `.utoc`-tiedostoja. Työkalu tarkistaa `<folder>`, sitten
  `<folder>\acr\Content\Paks`, sitten `<folder>\Content\Paks`.
- Muuten jokaisen Steam-kirjaston `steamapps\common\Assetto Corsa Rally` tarkistetaan
  samalla tavalla.
- Jokainen `.utoc` tässä kansiossa avataan yhtenä kontistona. Kontit, jotka eivät
  aukea, ohitetaan. Jos mikään ei aukea: "no readable IoStore containers in ...".

Useimmat lohkot on pakattu Oodlella, ja kirjastoa etsitään koneelta (jokainen
Steam-kirjasto haetaan). Katso [Oodle](reader-oodle.md).

Peli tunnistetaan Assetto Corsa Rallyksi, kun kierrostiedostossa lukee
`"game": "assetto-corsa-rally"` (tai `acrally`), tai kun annat `--game acrally`.

## Mikä vaihe on

Vaihe on **World Partition** -kartta:

- `Content\Levels\<Stage>.umap` sijoittaa kaukaisen maaston.
- Käännetyt solut kansiossa `Content\Levels\<Stage>\_Generated_\*.umap` sijoittavat
  kaiken muun.

Taso on vaihe, jos sen ympäristökansiossa, `Content\Environments\<Stage>\`, on
kansio `MeshesTrack`. Työkalu ei katso laattojen nimiä, koska vaihe voi nimetä
ne kaupungin mukaan eikä kartan. `--level` vertaa kartan nimiä kirjainkoosta
piittaamatta. Väärä nimi listaa vaiheet, joita on.

**Maastotasoa ei ole.** Maa koostuu staattisista malleista:

| Laatat | Polku | Muuttuvat |
|---|---|---|
| radan laatat, noin 175 m, jaettu kahtia | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` ja `..._Terrain_k` | `ground:road` ja `ground:terrain` (jakamaton radan laatta, kuten jäätynyt järvi, on kokonaan tietä) |
| kaukainen maasto, 2 km:n laatat | `.../MeshesTerrain/...` | `ground:terrain` |

## Sijoitusten lukeminen

Mallin sijoittaa `StaticMeshComponent`: sen `StaticMesh`, sekä sen
`RelativeLocation`, `RelativeRotation` ja `RelativeScale3D`. Jokainen on
suhteessa komponenttiin, johon se on kiinnitetty (`AttachParent`), aina
toimijan juureen asti, joka on maailmassa.

- Ominaisuudet ovat **versiottomia**: ne on tallennettu paikan mukaan luokan
  ominaisuuslistassa, eivät nimen mukaan. Ne luetaan skeemoilla tiedostosta
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (katso [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Arvo, joka on sama kuin komponentin malli (sen arkkityyppi Blueprintissä), ei ole
  tallennettu. Mallin arvot luetaan ensin rekursiivisesti, ja komponentin omat
  arvot korvaavat ne.
- Komponentit, joissa on `bVisible = 0` tai `bHiddenInGame = 1`, ohitetaan. Samoin
  mallit, joiden polku täsmää sanoihin `respawnwall`, `collision`, `blocker`,
  `invisible`, `/hlod/` tai `_hlod`.
- Kierrokset käyttävät Unrealin `FRotationMatrix`-muotoa (pitch, yaw, roll asteina).
- Kaksoiskappaleet (sama malli samassa muunnoksessa 0,1 cm:n tarkkuudella) pudotetaan.
- Komponentit, joita ei voi lukea, lasketaan syyn mukaan ja ilmoitetaan, esimerkiksi
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instanssoidut komponentit** (metsät, lähes kaikki) luetaan vain valinnalla
`--trees`. Tämä versio on järjestänyt nuo luokat uudelleen moottorin
otsikkotiedostojen ulkopuolelle, joten niiden ominaisuuksia ei lueta. Sen sijaan:

- malli tulee paketin riippuvuustaulukosta, jossa jokaisella tällaisella
  komponentilla on täsmälleen yksi staattinen malli,
- instanssit tulevat ominaisuuksien jälkeisestä natiivilohkosta
  (`[1][1][128][count]`, sitten `count` kappaletta 4x4 double-matriiseja),
- komponentin katsotaan olevan toimijansa juuressa, mikä on tapa, jolla
  metsätoimijat sijoittavat kasvit.

Koordinaatit ovat Unrealin: senttimetrejä, Z ylös, X eteenpäin, Y oikealle,
vasenkätinen koordinaatisto.

## Mikä vaihe ja mihin suuntaan

Telemetrian kehystä ei ole dokumentoitu, joten sitä ei oleteta. Se sovitetaan:

- **Kahdeksan ehdokaskehystä.** Unreal Z (cm) kerrottuna 0,01:llä tulee kierroksen
  korkeudeksi (y). Unreal X ja Y tulevat kierroksen x:ksi ja z:ksi, vaihdettuina tai
  vaihtamatta, kumpikin kummalla tahansa etumerkillä, kaikki skaalattuna 0,01:llä
  metreiksi.
- **Tien korkeusruudukko.** Jokaiselle vaiheelle jokainen tielaatta sijoitetaan
  (karkeimmalla yksityiskohtatasolla), ja korkein tien kärki säilytetään jokaisessa
  2 m:n solussa.
- **Pisteytys.** Enintään 400 kierrosnäytettä, tasavälein, viedään Unreal-avaruuteen
  jokaisen kehyksen läpi. Näyte on tiellä, kun 3 x 3 solun ympäröimässä ruudukossa
  lähin tien korkeus on 1 m näytettä alempana ja 3 m ylempänä (`ON_ROAD`). Pisteet
  ovat tiellä olevien näytteiden osuus.
- **Voittaja.** Paras kehys parhaalla vaiheella, jos se saa vähintään 50 %.
  Muuten vienti pysähtyy: "the lap does not lie on any stage's road in any
  frame (best: ...). Name the stage with --level."
- **Kierros, joka nimeää radan.** Jos kierrostiedostossa on `track`-kenttä,
  vaihe, jonka nimi vastaa sitä löyhästi (vain kirjaimet ja numerot, toinen
  sisältää toisen), kokeillaan ensin, yksin, ja hyväksytään vain jos se saa
  vähintään 80 %. Muuten kokeillaan kaikkia vaiheita.
- `--level`-valinnalla kokeillaan vain sitä vaihetta, kaikissa kahdeksassa kehyksessä.

Konsoli kertoo esimerkiksi
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Kaikki kirjoitetaan sitten **kierroksen kehykseen**: metreinä, Y ylös. Kolmion
kiertosuunta käännetään aina, kun muunnos peilaa, joten pinnat osoittavat
oikeaan suuntaan.

## Maa

- Käytävä on `--margin` metriä kierroksen ympärillä sen omassa x/z-tasossa.
- Jokainen maalaatta sijoitetaan hienoimmalla yksityiskohtatasollaan, ja vain
  käytävään ulottuvat kolmiot säilytetään.
- Kolmiot ryhmitellään lajin (tie tai maasto) ja 512 m:n neliön mukaan Unreal-
  avaruudessa (51 200 cm), ja jokaisella neliöllä on oma kuvansa. Osat nimetään
  esimerkiksi `ground:road 1_-4`. UV:t ovat `(unreal_xy - square_origin) / 51200`.
- Normaalit lasketaan kolmioista koko tiedostolle.

### Maan tekstuuri

Ellei `--no-textures` ole annettu, jokainen neliö maalataan kahdesta lähteestä,
`--texture-size`-pikselikokoon:

1. **Paistettu maanväri.** Vaiheen kartan `RuntimeVirtualTextureComponent`
   (sen laatikko on `RelativeLocation` kulmana ja `RelativeScale3D` kokona, ilman
   kiertoa) osoittaa suoratoistettavaan **virtuaalitekstuuriin**, eli maanväriin,
   jonka peli paistoi. Neliön alue luetaan siitä tasolta, jonka pikselit ovat
   lähimpänä haluttua kokoa. Se on 13–59 cm pikseliltä vaiheesta riippuen.
2. **Satelliittikuva** täyttää kaiken, minkä virtuaalitekstuuri jättää mustaksi.
   Se on vaiheen `sat*_(b|bc|c|basecolor)`-tekstuuri sen ympäristökansiossa, luettuna
   enintään 4096 px:nä. Sen paikka löydetään pienimmän neliösumman sovituksella
   kaukaisen maaston ensimmäisestä UV-kanavasta maailman x:ää ja y:tä vastaan.
   Sovituksen täytyy olla lineaarinen 0,01:n tarkkuudella 95. prosenttipisteessä,
   muuten kuvaa ei käytetä. Jos kaukaisen maaston UV:t menevät yli 1:n (materiaali,
   joka toistaa niitä), kartoitus puolitetaan kerran, kunnes ne sopivat.

Konsoli kertoo, mitä käytettiin, esimerkiksi
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Vaihe, jolla ei ole kumpaakaan, piirretään tasaisin värein.

## Sijoitetut mallit

Jokainen sijoitus, joka ei ole maalaatta, luokitellaan mallipolkunsa mukaan
(ensimmäinen osuma voittaa):

| Luokka | Mallin nimi (tai polku puille) sisältää |
|---|---|
| puut (vain `--trees`-valinnalla) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| kivet | `rock`, `cliff`, `boulder`, `stone` |
| reunakivet | `kerb`, `curb` |
| esteet | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| kyltit | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| rakennukset | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktuuri | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekvisiitta | kaikki muu |

- Kopio otetaan huomioon, jos sen origo on ulottuvuuskäytävässä (`margin + 60 m`),
  ja piirretään, jos sen rajat koskevat käytävää.
- Yksityiskohtatasot seuraavat sivua [Yksityiskohtatasot ja budjetti](detail-budget.md):
  etäisyysvyöhykkeet, sitten kalleimmat mallit laskevat tasoa budjetin mahtuessa.
  Jos edes karkeimmat tasot ylittävät budjetin, kaukaisimmat kopiot jätetään pois,
  kuten BeamNG:ssä, kunnes budjetti täyttyy. Reunakivet säilyttävät täyden
  yksityiskohtansa eikä niitä koskaan jätetä pois. Yhteenvedossa lukee
  `placed on it (N triangles of a B budget)` ja, jos kopioita jätettiin pois,
  `N copies left out to fit the budget, the furthest from the driving first`.
- Jokainen luokka on yksi osa tasaisella värillä: `ground:kerbs` reunakiville, jotka
  ovat ajopintaa, kuten Forzassa ja BeamNG:ssä, ja `structure:<category>` muille:

| Luokka | Väri (lineaarinen RGB) |
|---|---|
| esteet | 0.55, 0.52, 0.48 |
| kyltit | 0.75, 0.72, 0.65 |
| rakennukset | 0.62, 0.58, 0.52 |
| infrastruktuuri | 0.48, 0.48, 0.50 |
| kivet | 0.45, 0.43, 0.40 |
| rekvisiitta | 0.55, 0.45, 0.35 |
| puut | 0.20, 0.32, 0.14 |
| reunakivet | 0.70, 0.25, 0.22 |

Staattiset mallit, joita ei voi lukea (luuranko-mallit, vain Nanite-mallit,
tasot, joita ei ole tallennettu sisäisesti), lasketaan: `N meshes could not be read`.

## Todentamiset

Lähdekoodin mukaan asennetulla pelillä:

- Jokainen sisällysluettelo luetaan (versio 8).
- Jokainen vaiheen solu aukeaa, ja jokainen staattisen mallin ja näkymän komponentti
  dekoodautuu niin, että se päättyy täsmälleen luokkansa natiivihännän kohdalle.
- Lähes jokainen otannan staattinen malli dekoodautuu (loput ovat luurankomalleja).
  Tielaatan dekoodattu laajuus vastaa sen tallennettuja rajoja.
- Satelliittikuvan mip-tasot ovat täsmälleen sen massadatamerkintöjen kokoisia.
- Virtuaalitekstuurin palan laatat on tili tavulleen, ja tieltä löytyvät laatat
  osuvat tielle, jonka se näyttää.

## Tunnetut puutteet

- Instanssoitujen komponenttien omia ominaisuuksia ei lueta (katso yllä). Niiden
  sijoittelu olettaa toimijan juuren.
- PCG:n ajonaikaisesti luomia metsiä ei ole tallennettu tiedostoihin, joten niitä ei
  voi viedä.
- Spline-mallit (näkymättömät respawn-seinät), tarramaiset komponentit ja sijoitettujen
  mallien omat tekstuurit eivät piirry. Mallit ovat tasavärisiä.
- `--season` ei vaikuta mihinkään.
- Pelipäivitys voi siirtää ominaisuuspaikkoja. Lukija pysähtyy sen sijaan, että lukisi
  väärin, ja rata ilmoittaa, kuinka monta komponenttia epäonnistui.
