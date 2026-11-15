---
title: "Komennot"
nav_order: 2
lang: "fi"
source: commands.md
source_hash: "97a154edc5e0"
nav_exclude: true
search_exclude: true
---
# Komennot

Jokainen komento toimii muodossa `python -m heat3d_gamefiles <verb> ...` tiedostokansiosta.
Verbit on järjestetty siihen järjestykseen, jossa niitä yleensä tarvitaan: mikä tämä tiedosto on,
mitä siinä on, anna minulle tuo, ja muuta ajo kurssiksi.

| Verbi | Ottaa | Tekee |
|---|---|---|
| [`identify`](#identify) | minkä tahansa tiedoston | tunnistaa säilön muodon tiedoston tavuista |
| [`list`](#list) | Unreal `.pak`- tai IoStore `.utoc`-tiedoston, Source 2 `.vpk`-tiedoston, ForzaTech `.minizip`-tiedoston tai zip-tiedoston | listaa sen tiedot |
| [`extract`](#extract) | saman kuin yllä | kirjoittaa yhden tiedon levylle |
| [`meshes`](#meshes) | Unity `SerializedFile`-tiedoston | listaa ja tarkistaa sen meshit |
| [`course`](#course) | ajon | vie ajon ympärillä olevan kurssin (Forza, BeamNG.drive, Assetto Corsa Rally) |
| [`courses`](#courses) | tallennetun ajokirjaston | ajaa `course`-komennon jokaiselle siinä olevalle kurssille (Forza) |
| [`races`](#races) | asennetun Forzan | listaa kaikki pelin määrittelemät kisat: mitä ne lisäävät, mitä ne piilottavat, paikat ja vientin tilan |
| [`terrain`](#terrain) | Forzan radan kansion | leikkaa alueen maailmakoordinaateilla |
| [`levels`](#levels-and-level-frostbite) | asennetun Frostbite-pelin (Battlefield 6) | listaa sen kentät |
| [`level`](#levels-and-level-frostbite) | kentän nimen | vie kentän: maaston, sijoitetut meshit ja tarvittaessa niiden värikartat (Battlefield 6) |
| [`cars`](#cars) | asennetun Forzan | jokaisen auton matalalla yksityiskohtaisuudella, yhteen tiedostoon viewerin kisavälilehteä varten |
| [`ue-maps`](#ue-maps-and-ue-map-unreal-5-world-partition) | Unreal 5 -pelin | listaa sen World Partition -kartat |
| [`ue-map`](#ue-maps-and-ue-map-unreal-5-world-partition) | kartan nimen | vie kartan: maaston, HLOD-rakenteet, veden |
| [`enfusion-worlds`](#enfusion-worlds-and-enfusion-world-arma-reforger) | asennetun Arma Reforgerin | listaa sen maailmat |
| [`enfusion-world`](#enfusion-worlds-and-enfusion-world-arma-reforger) | maailman nimen | vie maailman: maaston väreissään, meren, rakennukset laatikkoina |

**Esimerkkien lukeminen:** `<x>` tarkoittaa, että korvaat sen omalla arvollasi ilman kulmasulkeita;
`[...]` on valinnainen; polku, jossa on välilyöntejä, kirjoitetaan "kaksoislainausmerkkien" sisään,
esimerkiksi `"C:\Games\My Game"`. Oletko uusi tässä? Katso [Ennen aloittamista](before-you-start.md).
Jokaisen verbin täydellinen `--help` on [Komentoviitteessä](../cli-reference.md).

Ohjelma voi jokaisen käynnistyksen yhteydessä tarkistaa ensin, onko uudempi julkaisu saatavilla. Katso
[Päivitykset](updates.md). `HEAT3D_NO_UPDATE=1` kytkee tarkistuksen pois.

Lähdekoodi: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py).
Vaiheittaiset sivut: [Arkistojen tarkastelu](inspecting-archives.md), [Kurssin vienti](course-export.md),
[Koko kentät](whole-levels.md), [Forzan autot](forza-cars.md).

![python -m heat3d_gamefiles --help](../assets/img/help.svg)

## Poistumiskoodit

| Koodi | Merkitys |
|---|---|
| 0 | onnistui |
| 1 | työ epäonnistui (luettamaton ajo, peliä ei löytynyt, ei mitään vietävää, `courses`-komennon kurssi epäonnistui; `list`- ja `extract`-komennoissa tiedosto, joka ei ole yksikään niistä arkistoista, joita ne lukevat, tiedosto, jota ei voi avata tai lukea - salattu pak ilman `--key`-avainta, salattu IoStore-säilö - tai tiedon puuttuminen arkistosta) |
| 2 | virheelliset argumentit (argparse), polku, jota ei ole olemassa, `--key`, joka ei ole 64 heksadesimaalinumeroa, tai `terrain` annettuna sekä `--box` että `--route`, tai ilman kumpaakaan |

`list`- ja `extract`-komentojen virheet ovat kukin yksi rivi vakiovirheessä, eivät Python-jäljitys.

---

## identify

```
python -m heat3d_gamefiles identify <path>
```

Tämä lukee tiedoston ja kertoo, mikä säilö se on. Se ei katso tiedostopäätettä (poikkeus on `.ucas`, alla).
Se kokeilee muotoja tässä järjestyksessä ja pysähtyy ensimmäiseen, joka jäsentyy:

1. **Unreal `.pak`**: alatunniste, jossa on pak-tunnus viimeisissä 1 024 tavussa. Tulostaa version,
   hakemiston sijainnin ja koon, sen, onko hakemisto salattu, sekä pakkausmenetelmät.
2. **Unreal IoStore `.utoc`**: IoStore-tunnus sen alussa. Tulostaa version, palojen määrän ja sen,
   onko säilö salattu; jos ei ole, niin tiedostojen määrän hakemistossa (ja minkä mount pointin alla),
   pakkausmenetelmät ja sen, onko sen `.ucas` vieressä.
   `.ucas` ei sisällä omaa otsikkoa, joten se tunnistetaan samannimisen vieressä olevan `.utoc`-tiedoston
   perusteella, ja `identify` nimeää sen tiedoston.
3. **ForzaTech `.minizip`**: `PGZP`-tunnus. Tulostaa version, merkintöjen ja segmenttien määrät ja sen,
   onko `ChunkContentsMiniZip<n>.txt` (joka nimeää merkinnät) vieressä (ja jos on, niin nimeääkö se yhtä monta
   kuin merkintöjä on).
4. **zip**: zip-paikallisen tiedoston otsikko alussa. Tulostaa merkintöjen määrän, kuusi yleisintä
   tiedostopäätettä ja kentän nimet, kun merkinnät ovat kansion `levels/<name>/` alla, kuten BeamNG.driven
   kenttäarkistossa.
5. **Unity**: `UnityFS`-paketti (tulostaa moottoriversion ja merkintöjen määrän) tai pelkkä `SerializedFile`
   (tulostaa muodon, moottoriversion, objektien määrän ja kuusi yleisintä luokkaa).
6. **Frostbite `.toc`**: tulostaa tyypin (`plain` tai `signed`), kohdan, josta puu alkaa, ja joko
   assettien määrän (binäärinen osiotaulukko) tai superbundlejen määrän (DbObject-puu).
7. **Source 2 `.vpk`**: tulostaa version, merkintöjen määrän ja ensimmäisen `.nav`-navigointiverkon,
   jos arkistossa on sellainen.
8. **BeamNG `.cdae`**: muotoversio 31, joka jäsentyy. Tulostaa meshien määrän, piirrettyjen
   yksityiskohtaisuustasojen määrän ja ensimmäiset materiaalit.
9. **BeamNG `.ter`**: sillä ei ole tunnusta, joten kaiken pitää täsmätä - sivun pituus 2 - 16 384,
   sen verran korkeuksia ja kerrosbaitteja neliössä, sitten 1 - 255 tulostettavaa kerroksen nimeä.
   Tulostaa version, koon ja kerrosten nimet.
10. **ForzaTech `.modelbin`**: tulostaa version, palojen määrän ja kuusi yleisintä palan tunnisteita.
    Palojen sisältöä ei puretä tässä.

Muodot, joilla on oma tunnus (2 - 4), tulevat ennen Unityä ja Frostbitea, joiden tarkistukset lukevat
koko tiedoston: Forzan arkisto on kymmeniä gigatavuja.

Jos mikään niistä ei täsmää, komento tulostaa `not a format this tool reads` ja viimeisen syyn.
Tuo syy tulee ForzaTech-tarkistuksesta.

Esimerkki (keksittyjä lukuja):

```
> python -m heat3d_gamefiles identify pakchunk0-Windows.pak
pakchunk0-Windows.pak  (1,234,567,890 bytes)
  Unreal pak, version 11
    index      2,345,678 bytes at 1,232,000,000
    encrypted  no
    methods    Oodle
```

```
> python -m heat3d_gamefiles identify GeoChunk0.minizip
GeoChunk0.minizip  (12,345,678,901 bytes)
  ForzaTech .minizip archive, version 101
    entries    98,304 in 192 segments
    names      ChunkContentsMiniZip0.txt
```

## list

```
python -m heat3d_gamefiles list <archive> [--filter TEXT] [--limit N] [--key HEX]
```

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<archive>` | pakollinen | Unreal `.pak`; IoStore `.utoc` (tai sen vieressä oleva `.ucas`); Source 2 `.vpk` (jaettujen VPK:iden kohdalla `_dir.vpk`); ForzaTech `.minizip`; zip, kuten BeamNGin kenttä- ja sisältöarkistot |
| `--filter TEXT` | ei mitään | vain polut, joissa on TEXT, kirjainkoosta riippumatta |
| `--limit N` | 50 | tulosta enintään N merkintää (kokonaismäärä tulostetaan aina) |
| `--key HEX` | ei mitään | AES-256-avain, jonka sinulla jo on, 64 heksadesimaalinumeroa, joko `0x`:n kanssa tai ilman. Vain salattu `.pak` käyttää sitä. Kaikki, mikä ei ole 64 heksadesimaalinumeroa, hylätään ennen kuin arkisto avataan (poistumiskoodi 2) |

Muoto päätellään tavuista: IoStore-sisällysluettelo, `.minizip` ja VPK tunnistetaan niiden
alkutunnuksella, zip paikallisesta tiedoston otsikosta ja `.pak` lopussa olevasta alatunnisteesta.
`.ucas`-tiedostolla ei ole otsikkoa, ja se avataan samannimisen `.utoc`-tiedoston kautta. Tiedosto, joka
ei ole mikään näistä, hylätään viestillä `<file> is not an archive list and extract read (...)`.
Tiedosto, joka on arkisto mutta jota ei voi avata, hylätään lukijan syyllä: salattu pak ilman
`--key`-avainta, salattu IoStore-säilö, pak-versio, jota se ei lue. Kummassakin tapauksessa tulos on yksi
rivi ja poistumiskoodi 1.

Jokainen rivi näyttää pakkaamattoman koon, pakkausmenetelmän ja polun:

| Arkisto | Menetelmä | Polut |
|---|---|---|
| `.pak` | `none` tai alatunnisteen nimi (`Zlib`, `Oodle`, `Gzip`...) | arkiston mount pointin kanssa, esimerkiksi `../../../Game/Content/...` |
| IoStore `.utoc` | `none` tai säilön menetelmä (`Oodle`, `Zlib`...), kuten sen ensimmäinen lohko on tallennettu | mount pointin kanssa, esimerkiksi `../../../<Project>/Content/...`. Säilö ilman hakemistoindeksiä ei nimeä tiedostoja, ja se hylätään |
| `.vpk` | aina `stored` | kuten hakemistossa |
| `.minizip` | `lz4`, `deflate` tai `stored` | kuten `ChunkContentsMiniZip<n>.txt` niitä kuvaa, joka on `GeoChunk<n>.minizip`-tiedoston vieressä, rakennuskoneen etuliite poistettuna (kenoviivat, kuten peli ne kirjoittaa). Arkisto ei tallenna nimiä, joten ilman tuota tiedostoa merkinnät ovat `#0`, `#1`... Lista, jonka rivimäärä ei täsmää merkintöihin, hylätään: ne eivät kuulu yhteen |
| zip | `stored`, `deflate`, ... | tallennetun mukaan; kansioita ei listata |

```
> python -m heat3d_gamefiles list pakchunk0-Windows.pak --filter /Maps/ --limit 3
1,204 entries matching '/Maps/'
       524,288  Oodle  ../../../Game/Content/Maps/TestLevel.umap
        12,040  none   ../../../Game/Content/Maps/TestLevel_BuiltData.uasset
     3,145,728  Oodle  ../../../Game/Content/Maps/TestLevel_BuiltData.ubulk
  ... 1,201 more
```

## extract

```
python -m heat3d_gamefiles extract <archive> <entry> [--out FILE] [--key HEX]
```

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<archive>` | pakollinen | kuten `list`-komennossa |
| `<entry>` | pakollinen | polku täsmälleen sellaisena kuin `list` sen tulostaa (kirjainkoolla on väliä); `.minizip`-tiedostossa myös `#<numero>` käy | 
| `--out FILE` | merkinnän tiedostonimi (viimeisen `/` tai `\` jälkeen), nykyisessä kansiossa | mihin kirjoitetaan; puuttuvat kansiot luodaan |
| `--key HEX` | ei mitään | kuten `list`-komennossa |

Merkintä puretaan (pak avaimella), dekoodataan ja kirjoitetaan levylle. Komento tulostaa
`<bytes> bytes -> <file>`. Jos polkua ei ole arkistossa, komento päättyy poistumiskoodilla 1.
Sama koskee merkintää, jota ei voi lukea (salattu merkintä ilman avainta, Oodle-pakattu ilman
Oodle-kirjastoa), ja syy tulostuu yhdelle riville. VPK-merkintää ei tarkisteta tässä CRC:llä. Lukijalla on
siihen `verify()`-metodi (katso [Source 2 VPK](reader-source2-vpk.md)).

```
python -m heat3d_gamefiles extract pak01_dir.vpk maps/example_map.nav --out example.nav
python -m heat3d_gamefiles extract GeoChunk0.minizip "scene\example\example.modelbin"
```

## meshes

```
python -m heat3d_gamefiles meshes <unity .assets> [--limit N]
```

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<path>` | pakollinen | pelkkä Unity `SerializedFile` (`sharedassets0.assets`, `level0`...), ei paketti |
| `--limit N` | 25 | pura ja tulosta enintään N meshiä |

Komento tulostaa `Mesh`-objektien määrän ja sitten rivin jokaista meshiä kohden: nimen (ensimmäiset
40 merkkiä), kärkien ja kolmioiden määrät, sekä `ok` tai `BOUNDS DISAGREE`.
`BOUNDS DISAGREE` tarkoittaa, että puretut kärjet eivät toista Unityn tallentamaa rajauslaatikkoa
2 %:n tarkkuudella laatikon koosta. Tämä on jäsentimen oma tarkistus (katso [Unity](reader-unity.md)).
Mesh, jota ei voi lukea, ilmoitetaan syyn kanssa, ja se lasketaan rajaan. `.resS`-tiedoston kärkidata
luetaan säilön kansiosta.

```
> python -m heat3d_gamefiles meshes sharedassets0.assets --limit 2
312 meshes in sharedassets0.assets
  Rock_Large_01                               1,204 verts    2,096 tris  ok
  [123456] could not be read: mesh 'Terrain_Chunk' is stored compressed; that encoding is not implemented
```

---

## course

```
python -m heat3d_gamefiles course <lap> [-o FILE] [options]
```

Tämä vie kurssin ajon ympäriltä: maan kaistan molemmin puolin ajon ja sen päällä olevat asiat yhtenä
`.glb`-tiedostona. Loput se selvittää itse: mikä peli, mikä asennettu kopio, mikä rata, kenttä tai
osuus, ja (Assetto Corsa Rallylle) mihin suuntaan akselit ovat. Katso [Kurssin vienti](course-export.md).

`<lap>` voi olla jokin seuraavista (tiedot kohdassa [Ajon syötteet](lap-inputs.md)):

- ajotiedosto: reitti-JSON, FH Companionin ajo-JSON, `heat3d-lap`-JSON, `.npz` tai `.csv`, jossa on x-, y- ja z-sarakkeet
- ajotiedostojen kansio, haetaan rekursiivisesti (koko tallennettu kurssi)
- kurssin **nimi**, haetaan FH Companionin kirjastosta kohdasta `%LOCALAPPDATA%\FHCompanion\laps`

### Valinnat

| Valinta | Oletus | Pelit | Merkitys |
|---|---|---|---|
| `-o`, `--out FILE` | `<course name>.glb` nykyisessä kansiossa, tai `$HEAT3D_LEVELS/<game>/courses/`, kun se on asetettu | kaikki | minne kirjoitetaan; nimi kirjoitetaan pienillä kirjaimilla, ja muiden merkkien jonot korvataan `_`:llä |
| `--game {forza,beamng,acrally}` | mitä ajotiedosto kertoo, muuten `forza` | kaikki | mistä pelistä ajo on |
| `--margin M` | 80 | kaikki | metriä maata ajon molemmin puolin |
| `--texture-size {2048,1024,512}` | 2048 | kaikki | maatekstuurin pikseleitä 512 m:n laattaa kohden (2048 = 25 cm pikseli) |
| `--no-textures` | pois | kaikki | pelkät tasaiset värit: paljon pienempi tiedosto. Forzalle tämä ohittaa myös tien ja reunan jaon (katso alla) |
| `--season {summer,autumn,winter,spring}` | summer | Forza | minkä vuodenajan maakartat ja mallitekstuurit |
| `--no-placed` | pois | kaikki | pelkkä maasto: ei reunakiviä, kaiteita, kylttejä, rakennuksia. BeamNG:ssa mallinnetut ajopinnat säilyvät |
| `--trees` | pois | kaikki | sijoittaa myös kasvillisuuden (Forza: puut, pensaat ja murskattavat; BeamNG: puut; AC Rally: puut ja instanssoitu lehvästö) |
| `--detail-budget N` | automaattinen | kaikki | kolmioiden katto kaikelle sijoitetulle; katso [Yksityiskohtaisuustasot ja budjetti](detail-budget.md) |
| `--track DIR` | haetaan | Forza | radan kansio (kansio `media\Tracks` alla, jossa on `GeoChunk0.minizip`), jos asennettua peliä ei pitäisi etsiä |
| `--level NAME` | löydetään ajosta | BeamNG, AC Rally | kenttä (BeamNG:n kansion nimi) tai osuus (AC Rallyn karttanimi), kirjainkoosta riippumatta |
| `--install DIR` | haetaan Steam-kirjastoista | BeamNG, AC Rally | BeamNG: kansio, jossa on `gameengine.zip`. AC Rally: pelin kansio tai sen `acr\Content\Paks` / `Content\Paks` |

Valinnat, jotka eivät koske peliä, ohitetaan ilman varoitusta. Esimerkiksi
`--season` ei tee mitään BeamNG:lle ja AC Rallylle, ja `--track` ei tee mitään niillekään.

### Mikä peli

Peli otetaan `--game`-valinnasta, sitten `heat3d-lap`-tiedoston `game`-kentästä (tai CSV:n
`# {...}`-kuvauskommentista), ja oletuksena on Forza. Kansio saa pelin, jonka sen tiedostot nimeävät,
kun ne nimeävät vain yhden; tiedosto, joka ei nimeä mitään (FH Companionin ajo, `course.json`, CSV ilman
kuvauskommenttiriviä), ei lasketa mukaan (katso [Ajon syötteet](lap-inputs.md)).

| Arvo | Vienti |
|---|---|
| alkaa `forza`-sanalla | Forza Horizon |
| `beamng` | BeamNG.drive |
| `assetto-corsa-rally` tai `acrally` | Assetto Corsa Rally |
| `assetto-corsa-evo` | hylätty: "keeps all its content in one package obfuscated with a key, and this tool recovers none" |
| `iracing` | hylätty: "tracks ship in a protected format that is not a file-extraction target" |
| mikä tahansa muu | hylätty: "there is no course reader for <game> yet" |

Hylkäys ehdottaa myös vaihtoehtoja: rakenna kurssi pelistä (3DHeat GameCapture), tai analysoi ajot ilman
kurssia, koska viewerin Kisa-analyysi-välilehti piirtää tien niistä.

### Esimerkit

```
# Kurssi FH Companionin kirjastosta nimellä
python -m heat3d_gamefiles course "Example Circuit"

# Yksi ajotiedosto, kapeampi kaista, pienempi tiedosto
python -m heat3d_gamefiles course lap.json -o example.glb --margin 40 --texture-size 1024

# Talvitekstuurit, puut mukana
python -m heat3d_gamefiles course "Example Circuit" --season winter --trees

# 500 000 sijoitetun kolmion ehdoton katto
python -m heat3d_gamefiles course lap.json --detail-budget 500000

# Radan kansio annettuna suoraan (peli asennettu Steamin ulkopuolelle)
python -m heat3d_gamefiles course lap.json --track "D:\Games\<Forza>\media\Tracks\<map>"

# BeamNG: nimeä kenttä, osoita asennukseen
python -m heat3d_gamefiles course beamng_lap.json --level <level folder> --install "D:\Games\BeamNG.drive"

# AC Rally, tavallinen CSV-ajo, joka ei kerro pelistään
python -m heat3d_gamefiles course rally_lap.csv --game acrally
```

Esimerkkituloste (Forza, keksittyjä lukuja):

```
Example Circuit: 12 laps, 18,400 samples, 41,200 m driven
  on <map>, in <game folder>
  cutting 80 m either side of the driving: 1.10 km2 of a 1,350 by 1,020 m box
262,144 vertices, 225,000 triangles from 410 meshes across 2 tiles
  x       0.0 ..    1150.0
  y      88.4 ..     131.9
  z       0.0 ..     820.0

  baked 2 ground textures at 2048 px (25 cm a pixel)

  what the ground is made of:
       76,500 triangles  34.0%  verge
       60,750 triangles  27.0%  terrain
       56,250 triangles  25.0%  road
       31,500 triangles  14.0%  markings

  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
      102 placed    3 models      8,568 triangles  ground:kerbs
    2,278 placed   14 models    ...   structure:barriers
    ...
wrote example_circuit.glb (79,000,000 bytes)
```

## cars

```
python -m heat3d_gamefiles cars -o forza.h3dcars
python -m heat3d_gamefiles cars --game "<game folder>" -o forza.h3dcars
```

Jokainen asennetun Forzan auto pelin omalla matalalla yksityiskohtaisuudella, yhteen tiedostoon
viewerin kisavälilehteä varten: `ProxyLOD`-malli, jonka jokainen autoarkisto kansiossa `media/Cars` kantaa,
noin 900 kolmiota, auton numero sellaisena kuin telemetria sen ilmoittaa, sen merkki, mallitunniste ja
vuosi arkiston nimestä, sekä sen pyörät ja takavalot. Kestää sekunteja ja kirjoittaa noin 5 MB.
Aja uudelleen, kun peliin tulee uusia autoja. Arkisto, jossa ei ole tuollaista mallia (liikenteen rekvisiitta),
nimetään ja jätetään pois. Muoto on kuvattu tiedostossa
[`forzacars.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzacars.py).

Muodot ovat metreinä, pelin omina: 1:1 auton kanssa. Tiedosto sisältää pelin sisältöä, joten se on
sille koneelle, jolla se tehtiin, ei jaettavaksi.

## courses

```
python -m heat3d_gamefiles courses [-o FOLDER] [options]
```

Tämä ajaa Forzan `course`-viennin jokaiselle kurssikansiolle tallennetussa ajokirjastossa ja kirjoittaa
jokaisesta yhden `<name>.glb`-tiedoston. Se on vain Forzaa varten. Se kutsuu Forzan vientiä suoraan, eikä
lue `--game`-, `--level`- tai `--install`-valintoja.

| Valinta | Oletus | Merkitys |
|---|---|---|
| `-o`, `--out FOLDER` | `courses`, tai `$HEAT3D_LEVELS/forza/courses`, kun se on asetettu | kansio, johon kirjoitetaan (luodaan, jos puuttuu) |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | ajokirjasto |
| `--only TEXT [TEXT ...]` | kaikki | vain ne kurssit, joiden kansion nimessä on jokin näistä (kirjainkoosta riippumatta) |
| `--force` | pois | vie uudelleen se, jolla on jo `.glb` |
| `--track DIR` | haetaan | kuten `course`-komennossa |
| `--margin M` | 80 | kuten `course`-komennossa |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kuten `course`-komennossa |

Mikä on kurssikansio: ajokirjaston suora alikansio, jonka nimessä on ` (course_`. FH Companion nimeää
kurssit näin, esimerkiksi `Example Circuit (course_1200_3400_to_1175_3400)`. Osa nimestä alkaen
` (course_` pudotetaan pois.

Näin ajo toimii:

- Kurssi, jonka `.glb` on jo olemassa, ohitetaan (`kept`), ellei `--force` ole annettu, joten keskeytynyt ajo jatkuu siitä, mihin se jäi.
- Vanhemman version kirjoittama `.glb`, josta puuttuu kisan oma kerros ja paikat (sen `asset.extras.course_format` puuttuu tai on nykyistä pienempi), viedään uudelleen, aivan kuin `--force` olisi annettu vain sille.
- Kaksi kurssikansiota, joilla on sama nimi ennen ` (course_`-osaa (tallentaja, joka nimesi uuden kurssin vanhan mukaan), eivät ylikirjoita toisiaan: ensin luotu kansio säilyttää nimen `<name>.glb`, toinen kirjoitetaan nimellä `<name>_<start>.glb`, `<start>` on lähtökohta miinusmerkit muutettuna kirjaimeksi `m` (esimerkiksi `example_circuit_m120_m340.glb`).
- Kurssi, joka epäonnistuu (luettamattomat ajot, muistin loppuminen, ei maastoa...), ilmoitetaan `FAILED`-merkinnällä, ja ajo jatkuu.
- Lopuksi tulostetaan taulukko tilasta, koosta megatavuina, kuluneista sekunneista ja nimestä, sekä `<n> of <total> courses in <folder>`.
- Poistumiskoodi on 1, jos jokin kurssi epäonnistui.

```
python -m heat3d_gamefiles courses -o courses --only circuit sprint --texture-size 1024
```

## races

```
python -m heat3d_gamefiles races [-o FOLDER] [--markdown FILE] [options]
```

Listaa jokaisen kisan, jonka asennettu Forza määrittelee, sen reittimäärittelyistä (katso
[Forza Horizon -kurssit](course-forza-horizon.md#which-race)), ja tarkistaa `courses`-kansion viennit niitä
vasten. Se lukee pelin ja ajokirjaston; se ei kirjoita mitään paitsi valinnaisen taulukon.

| Valinta | Oletus | Merkitys |
|---|---|---|
| `-o`, `--out FOLDER` | kuten `courses`-komennossa | kansio, johon `courses` kirjoittaa ja jonka tiedostot tarkistetaan |
| `--library DIR` | `%LOCALAPPDATA%\FHCompanion\laps` | ajokirjasto |
| `--track DIR` | haetaan | radan kansio, jos se ei ole asennetun pelin |
| `--markdown FILE` | ei mitään | kirjoita taulukko myös tähän Markdownina |

Yksi rivi kisaa kohden ja yksi jokaista kisalla ajettua tallennettua kurssia kohden:

| Sarake | Merkitys |
|---|---|
| route | reitin tunnus |
| course | kisaan sovitettu tallennettu kurssi, jos sellainen on |
| own assets | kisan lisäämät kopiot vapaan ajon maailmaan |
| drawn | niistä ne kopiot, joiden mallin rata toimittaa |
| kinds | lisätyt kopiot tyypeittäin (kaiteet, rekvisiitta, tarrat, infrastruktuuri, ...) |
| not geometry | katsojamerkit ja törmäyssplinet, laskettuina |
| hidden | vapaan ajon esineet, jotka kisa poistaa |
| venue | paikan maa-mallit, joiden kautta kisan tekoälyn linja kulkee 10 m:n päässä |
| export | `current`, `older format` (viedään uudelleen `courses`-komennolla), `not exported`, tai tyhjä kisalle, jolla ei ole tallennettua kurssia |

Lopussa on laskuri: `<n> races: <a> with assets of their own, <v> through a
venue, <d> driven in the lap library, <s> recorded courses to export again`.

```
python -m heat3d_gamefiles races -o courses --markdown races.md
```

## terrain

```
python -m heat3d_gamefiles terrain <track folder> -o FILE (--box X0 Z0 X1 Z1 | --route FILE) [options]
```

Tämä on Forzan leikkaus, jossa kaikki määritellään käsin: annat radan kansion ja alueen, et ajoa. Se on
hyödyllinen, kun haluttu alue on laatikko eikä ajo.

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<path>` | pakollinen | Forzan radan kansio kohdassa `media\Tracks` (jossa on `GeoChunk*.minizip`) |
| `-o`, `--out FILE` | pakollinen | kirjoitettava `.glb` |
| `--box X0 Z0 X1 Z1` | | alue pelin metreinä (x ja z, sellaisina kuin telemetria ne ilmoittaa); kulmat missä järjestyksessä tahansa |
| `--route FILE` | | reitti-JSON, jossa on `"bounds": {"min": [x, y, z], "max": [x, y, z]}`, kuten `heat3d_capture route` ja `heat3d_capture laps` ne kirjoittavat; luetaan UTF-8:na, byte-order-merkillä tai ilman |
| `--margin M` | **100** | metriä reitin rajojen ympärille, ja käytävän leveys, kun reitillä on viiva |
| `--texture-size`, `--no-textures`, `--season`, `--no-placed`, `--trees`, `--detail-budget` | | kuten `course`-komennossa |

Anna täsmälleen yksi `--box` tai `--route`, muuten poistumiskoodi on 2. `--route`-valinnalla leikkaus on
reitin `bounds` (`min`/`max`, x ja z), leventää marginaalilla. Jos tiedostossa on myös vähintään
10 sijaintia, leikkaus kapenee `--margin`-metrin käytäväksi niiden ympärille, ja sijoitetut mallit saavat
yksityiskohtaisuutensa etäisyyden mukaan siitä viivasta. `--box`-valinnalla koko laatikko säilyy, ja
yksityiskohdat menevät sen lähimmälle keskikohtaa seisoville asioille.

Korkeus ei koskaan ole osa leikkausta. Laatikko kartan ulkopuolella tai meressä antaa viestin
"no terrain there" (poistumiskoodi 1), ei koordinaattivirhettä.

```
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --box 0 0 512 512 -o piece.glb
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route route.json -o map.glb
```

## levels and level (Frostbite)

```
python -m heat3d_gamefiles levels [--install FOLDER]
python -m heat3d_gamefiles level <level> [-o FILE] [--install FOLDER] [--textures [PIXELS]]
                                 [--ground-texture [METRES]] [--ground-spacing METRES]
                                 [--navmesh] [--detail-budget N] [--skip TEXT ...] [--by-mesh]
                                 [--clamped-uvs]
```

`levels` listaa kentät, joita asennettu Frostbite-peli sisältää, taulukkonsa nimen mukaan
(`levels/<level>/<level>.toc`), sen koon ja sen lähteen: `Data` peruspelille, `Update/<pack>` päivitykselle,
ja kuinka monta korkean resoluution taulukkoa sitä täydentää. Kenttä, jonka päivitys tuo mukanaan, on
pienellä palojen taulukolla myös peruspelissä; taulukko, jossa on kentän palat, on kenttä (katso
[Frostbite](reader-frostbite.md#which-table-is-the-level)).
`level` vie yhden: maaston korkeuskentän, jokaisen mallin, jonka kentän staattiset mallilohkot sijoittavat,
yksittäin sijoitetut esineet ja missä ne seisovat, sekä kentän maiseman taustan kartan ympärillä. Valinnalla
`--textures` jokaisella pinnalla on sen värikartta; valinnalla `--navmesh` mukaan tulevat pinnat, joilla
sotilaat kävelevät. Lukutapa on kuvattu [Frostbitessä](reader-frostbite.md).

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<level>` | pakollinen | nimi sellaisena kuin `levels` sen tulostaa, sen yksikäsitteinen osa, tai kentän `.toc`-tiedoston polku |
| `-o`, `--out FILE` | `<level>.glb` (kohdassa `$HEAT3D_LEVELS/<game>/`, kun se on asetettu) | kirjoitettava `.glb` |
| `--install FOLDER` | ensimmäinen Steam-peli, jonka `Data` sisältää `layout.toc`-tiedoston | pelin kansio |
| `--textures [PIXELS]` | pois; 512, kun annetaan ilman kokoa | kirjoita kunkin pinnan värikartta, suurin mip, joka ei ole suurempi kuin PIXELS sivulta, ja sen tekstuurikoordinaatit sellaisina kuin peli ne pitää, toistuvalla näytteenottimella (katso [Tulostemuoto](output-format.md)). Korkeuskenttä saa maiseman taustan värikartan siinä, missä se kattaa sen; muuten maaston pintamateriaalien keskiväri; muuten taustan keskiväri ympärillä. Pois päältä jokainen osa on tasainen väri |
| `--ground-texture [METRES]` | pois; 0.5, kun annetaan ilman kokoa | paista maaston päällysteet (tiet, kiitoradat, apronit, maalatut merkinnät) maaväriin, kerrottuna maaston värikartalla siellä, missä kentällä sellainen on, korkeuskentän väriksi, METRES pikseli, laattoina enintään 4 096 pikseliä (`ground:terrain x<x> z<z>`). Toimii sekä `--textures`:n kanssa että ilman |
| `--navmesh` | pois | lisää kentän navigointiverkko sen pienimmälle agentille, sotilaalle (1,8 m pitkä, 0,4 m leveä), osana `nav:walkable`: maa, lattiat, portaat ja katot, joihin sotilas pääsee, ilman hyppyjä, tikkaita ja hyppimisiä niiden välillä |
| `--ground-spacing METRES` | 4 | korkeuskentän hienoin väli; hienommat solmut otetaan harvemmin. 0 jättää korkeuskentän pois |
| `--detail-budget N` | jokainen kopio karkeimmalla tasollaan plus neljännes, vähintään 1 500 000 | kolmioiden katto. Eniten kustantavat meshit putoavat yhden yksityiskohtaisuustason kerrallaan, kunnes se mahtuu; jos karkeimmatkin tasot eivät riitä, pienimmät kopiot jätetään pois ensin. Maaston tausta ei koskaan karkene eikä jää pois |
| `--skip TEXT` | | jätä pois staattiset mallilohkot, joiden osion nimessä on TEXT; toista useammalle. Esimerkiksi pelimuodon kerros |
| `--by-mesh` | pois | sen selvittämiseen, mikä osa on: yksi osa lähdemeshiä ja materiaalia kohden, nimetty `<part> \| <mesh> \| <material>`; paljon suurempi tiedosto |
| `--clamped-uvs` | pois | renderöijälle, joka ei osaa toistaa tekstuuria: leikkaa jokainen tekstuuroitu kolmio paloiksi, joiden koordinaatit ovat välillä 0..1, ja piirtää kolmion, joka tarvitsisi yli 4 palaa, sen tekstuurin keskiväriin, osassa `<part> (average colour)` |

Se tulostaa ryhmät ja kuinka monta kopiota kukin sijoitti, mallit, jotka jätettiin pois ja miksi, kolmiot
osaa kohden (ja `--textures`-valinnalla kuinka monta tekstuuria ja kuinka monessa osassa löytyi
värikartta), mikä maa on, ja `--navmesh`-valinnalla kuinka monta navigointilaattaa luettiin. Kentästä ei
kirjoiteta mitään geometrian lisäksi: ei nimiä, ei metatietoja (katso [Tulostemuoto](output-format.md)).

Maaston budjetti on erillinen: korkeuskenttää ja taustaa ei koskaan karkenneta `--detail-budget`-valinnalla;
`--ground-spacing` mitoittaa korkeuskentän.

Koko kenttä on suuri: tyypillisesti yli kymmenen miljoonaa kolmiota ja useita satoja megatavuja.
`--textures` lisää tiedostoon vähän; kenttä, jossa on paljon puita, voi ylittää noin 1 GB. `--textures 256 --detail-budget 3000000 --ground-spacing 8`
tuo kentän noin kolmannekseen tästä.

```
python -m heat3d_gamefiles levels
python -m heat3d_gamefiles level <level> -o level.glb --textures --ground-texture
python -m heat3d_gamefiles level <level> --textures 512 --ground-texture 0.5 --navmesh
python -m heat3d_gamefiles level <level> --textures 256 --detail-budget 3000000 --ground-spacing 8
```

## ue-maps and ue-map (Unreal 5 World Partition)

```
python -m heat3d_gamefiles ue-maps <game>
python -m heat3d_gamefiles ue-map  <game> <map> [-o FILE] [--ground-spacing METRES] [--no-structures] [--no-water]
```

`<game>` on pelin kansio, sen `Content/Paks`, tai sen kansion nimi Steam-kirjastossa
(`"<Steam game folder name>"`). `ue-maps` listaa jokaisen kartan, jolla on valmiita World Partition -soluja
vieressään. `ue-map` vie yhden muodossa `ground:<map>` (maisema), `structure:<map>` (kartan yhdistetyt HLOD-meshit)
ja `water:<map>` (sen vesistöt siellä, missä ne ovat maan yläpuolella), Unrealin **senttimetreinä** Y- ja Z-akselit
vaihdettuina - ainoa vienti, joka ei ole metreinä. Miten kukin luetaan ja tarkistetaan:
[Unreal 5 -kartat](level-unreal-world-partition.md).

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<map>` | pakollinen | nimi sellaisena kuin `ue-maps` sen tulostaa, tai sen yksikäsitteinen osa |
| `-o`, `--out FILE` | `<map>.glb` (kohdassa `$HEAT3D_LEVELS/<game>/`, kun se on asetettu) | kirjoitettava `.glb` |
| `--ground-spacing METRES` | 2 | maisemaverkon kärkiväli tiedostossa, pyöristettynä sen omien ruutujen kokonaiseen määrään |
| `--no-structures`, `--no-water` | | jätä se osa pois |

Se tulostaa kolmiot osaa kohden, kuinka monta maiseman komponenttia luettiin, ja kuinka moni niiden
kahdesti tallentama kärki on eri mieltä. 3 km:n kartta 2 metrin välillä on noin 4,6 miljoonaa maan kolmiota.

## enfusion-worlds and enfusion-world (Arma Reforger)

```
python -m heat3d_gamefiles enfusion-worlds [--install FOLDER]
python -m heat3d_gamefiles enfusion-world <world> [-o FILE] [--install FOLDER] [--ground-spacing METRES]
                                          [--texture-size PIXELS] [--no-structures] [--trees]
```

`enfusion-worlds` listaa jokaisen maailman, jossa on maasto, sen kansion mukaan kohdassa `worlds/`.
`enfusion-world` vie yhden: `ground:<world>` (maasto, sen laattojen väreissä), `water:<world>` (meri, korkeudessa nolla)
ja `structure:<world>` (jokaisen sijoitetun mallin laatikko), pelin omina metreinä - x itään, y ylös, z pohjoiseen.
Miten kukin luetaan ja tarkistetaan: [Arma Reforgerin maailmat](level-arma-reforger.md).

| Valinta | Oletus | Merkitys |
|---|---|---|
| `<world>` | pakollinen | maailma sellaisena kuin `enfusion-worlds` sen tulostaa |
| `-o`, `--out FILE` | `<world>.glb` (kohdassa `$HEAT3D_LEVELS/<game>/`, kun se on asetettu) | kirjoitettava `.glb` |
| `--install FOLDER` | Steam-kirjasto, joka sisältää pelin | pelin kansio |
| `--ground-spacing METRES` | 2 (maaston oma) | maaston kärkiväli tiedostossa |
| `--texture-size PIXELS` | 4096 | maan värikuvan pidempi sivu; 0 tasaiselle värille |
| `--no-structures` | | jätä sijoitetut mallit pois |
| `--trees` | pois | sijoita myös puut ja muu kasvillisuus laatikkoina |

Se tulostaa kolmiot osaa kohden, kuinka monta laattareunan kärkeä ei täsmää, kuinka monta oliota maailmatiedosto
sisältää ja kuinka monta laatikkoa sijoitettiin, sekä mitä jätettiin pois ja miksi.

## Ympäristömuuttujat

| Muuttuja | Vaikutus |
|---|---|
| `HEAT3D_OODLE` | polku `oo2core_*_win64.dll`-tiedostoon, tai kansioon, jossa se on; katso [Oodle](reader-oodle.md) |
| `HEAT3D_LEVELS` | yksi kansio jokaiselle viennille, joka tehdään ilman `-o`:ta: jokaisen pelin tulokset menevät kansioon `<HEAT3D_LEVELS>/<game>/` (kurssit kansioon `<game>/courses/`, autopaketti kansioon `forza/`). Kun sitä ei ole asetettu, ne menevät nykyiseen kansioon |
| `HEAT3D_NO_UPDATE` | mikä tahansa arvo muu kuin tyhjä, `0`, `false` tai `no` kytkee päivityksen tarkistuksen pois; katso [Päivitykset](updates.md) |
| `LOCALAPPDATA` | mistä FH Companionin kirjastoa, BeamNG:n käyttäjäkansiota ja päivitysvälimuistia etsitään |
| `HEAT3D_COURSE` | vain testejä varten: kurssi, jota asennetun pelin reunakivitesti käyttää; katso [Kehitys](development.md) |
