---
title: "BeamNG.drive"
lang: "fi"
source: course-beamng.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Kurssin vienti: BeamNG.drive

BeamNG-vienti lukee kentän samalla tavalla kuin peli sen liittää, ja kirjoittaa sitten saman tyyppisen
tiedoston kuin Forzan vienti: maan 512 m:n neliöittäin leivotulla tekstuurilla, tie ja löyhä maa omina osinaan,
sijoitetut mallit luokittain, ja vesi.

```
python -m heat3d_gamefiles course beamng_lap.json
python -m heat3d_gamefiles course beamng_lap.json --level <level folder>
python -m heat3d_gamefiles course beamng_lap.json --install "D:\Games\BeamNG.drive"
python -m heat3d_gamefiles course lap.csv --game beamng
```

Lähteet: [`beamng.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamng.py) (asennus, tiedostojärjestelmä, kohtaus, maasto, materiaalit),
[`beamngcourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcourse.py) (vienti),
[`beamngshape.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngshape.py) ja
[`beamngcollada.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/beamngcollada.py) (muodot).
Tiedostomuodot tarkemmin: [BeamNG-tiedostot](reader-beamng.md).

## Ajon kehys

`course`-vienti odottaa BeamNG-sijainteja **viewerin kehyksessä**:
`(x, z, -y)` BeamNG:n Z-ylös-maailmasta, metreinä. Tämä on kierto, jonka 3DHeat-telemetriatallennin tekee.
Vienti kääntää ajon takaisin BeamNG:n kehykseen (`(x, -z, y)`), työskentelee siellä ja kirjoittaa kaiken
ulos jälleen viewerin kehyksessä. Tämä on kierto, ei peilaus, joten mitään ei tule ulos peilattuna. Ajo, joka
on tallennettu BeamNG:n raakakehyksessä, ei sijoittuisi oikein. Tätä ei ole testattu muilla tallentajilla.

Peli otetaan BeamNG:ksi, kun `heat3d-lap`-tiedosto sanoo `"game": "beamng"`, tai kun annat
`--game beamng`.

## Asennuksen löytäminen

- `--install <folder>`: kansio, jossa on `gameengine.zip` ja `content`.
- Muuten tarkistetaan jokaisen Steam-kirjaston `steamapps\common\BeamNG.drive` niiden kahden varalta.
- Jos kumpikaan ei toimi: "no BeamNG.drive install found in the Steam libraries. Name
  its folder with --install (the one holding gameengine.zip)."

## Tiedostojärjestelmä

BeamNG toimittaa tavallisia zip-arkistoja ja liittää ne yhteen tiedostojärjestelmään, johon kentät viittaavat
(`/art/shapes/...`, `/assets/materials/...`). Vienti rakentaa saman: yhden kirjainkoosta riippumattoman
hakemiston seuraavista

1. `gameengine.zip`,
2. jokainen `*.zip` kansiossa `content`, paitsi `content\vehicles\*` ja arkistot, joiden nimi alkaa
   `art_sound`- tai `audio`-sanalla,
3. käyttäjän sisältö, uusin asettelu ensin: kansioissa `%LOCALAPPDATA%\BeamNG\BeamNG.drive` ja
   `%LOCALAPPDATA%\BeamNG.drive` kansio `current` ja korkeimman numeroinen versiokansio. Jokaisesta:
   `mods\*.zip`, jokainen kansio kohdassa `mods\unpacked`, ja käyttäjäkansio itse, jos siinä on kansio `levels`.

Myöhemmät lisäykset voittavat, kuten pelissä, joten modi korvaa sen, minkä se ohittaa. Modit ovat aina
mukana kurssiviennissä.

Polut, joita kenttä nimeää, ratkaistaan samalla tavalla kuin peli ne ratkaisee: sellaisenaan, sitten
suhteessa tiedostoon, joka ne nimesi, ja kullekin myös sen `.dds`-tiedostona, johon tekstuuri leivottiin,
sen `.cdae`-tiedostona, johon `.dae` käännettiin, tai `.link`-tiedoston kautta, joka osoittaa kohtaan `/assets`.

## Mikä kenttä

Ilman `--level`-valintaa jokainen kenttä pisteytetään sen mukaan, kuinka suuri osa ajosta on sillä:

- Enintään 500 ajonäytettä, tasavälein, käytetään.
- Jokaisen kentän `TerrainBlock`-osalle maaston laajuus luetaan `.ter`-tiedoston viidestä ensimmäisestä
  tavusta, joten kenttä, jonka lähellä ajo ei ole, ei maksa mitään. Jos vähintään 30 % näytteistä on laajuuden
  sisällä, korkeudet luetaan. Näyte lasketaan **maalla** olevaksi, kun se on 1 m maanpinnan alapuolella ja
  3 m sen yläpuolella (`ON_GROUND`), koska auton vertauspiste on sen runko, ei renkaat.
- Jos mikään kenttä ei saa 50 % tai enemmän, kentät pisteytetään myös niiden **teiden** perusteella. Osa
  kentistä jatkuu korkeuskarttansa ohi (niiden reunat jatkuvat kallioina). Näyte on tiellä, kun se on
  tien puolileveyden plus 4 m (vähintään 6 m) sisällä `DecalRoad`-segmentistä, ja 2 m maanpinnan alapuolella ja
  4 m sen yläpuolella.
- Paras kenttä voittaa, jos se saa vähintään 30 %. Muuten vienti pysähtyy ja luettelee parhaat kolme:
  "the lap does not lie on any installed level's terrain (best: ...). Name the level with --level."

Konsoli sanoo `on <level>: 87% of the lap lies on its terrain` (tai `roads`). `--level` täsmää kirjainkoosta
riippumatta kentän kansioiden nimiin.

## Kentän lukeminen

Mistä kenttä koostuu, kukin osa tarkistettuna toimitettuja kenttiä vasten (tarkemmin
[BeamNG-tiedostoissa](reader-beamng.md)):

- **Kohtaus**: `levels\<name>\main\**\*.level.json` (yksi JSON-objekti rivillä, tai JSON-taulukko), tai `.mis`-tiedosto
  vanhemmille kentille. Työkalu lukee `TSStatic`-objektit (sijoitetut mallit, piilotettuja ohittaen), `Prefab`-objektit
  (sisäkkäin enintään 8 tason syvyyteen, TorqueScript `.prefab` tai `.prefab.json`), `DecalRoad`-objektit
  (maalatut tiet), `TerrainBlock`, `WaterPlane`, `WaterBlock` ja `River`.
- **Metsäesineet**: `levels\<name>\forest\*.forest4.json`, tyypitettynä `managedItemData.json`-tietueiden kautta.
  Kaiteet, aidat ja kivet ovat metsäesineitä yhtä usein kuin puut.
- **Maasto**: `.ter`-korkeuskenttä ja sen kerroskartta.
- **Materiaalit**: jokainen `*.materials.json` kansion `levels\` ulkopuolella, sekä tämän kentän omat.

## Käytävä ja tiejäljet

Käytävä on `--margin`-metriä ajon ympärillä BeamNG:n x/y-tasossa (katso
[Kurssin vienti](course-export.md#the-corridor)). Ehdokkaiden valintaan käytetään
`margin + 60 m`:n käytävää.

**Tiejäljet** (`DecalRoad`) ovat siellä, missä suurin osa BeamNG:n teistä on: maalattuna maastoon, ei mallinnettuina.
Jäljet, joiden ulottuvuus koskettaa ulottuvuuskäytävää, otetaan pelin piirtojärjestyksessä (laskeva `renderPriority`,
sitten tiedostojärjestys), ja asetellaan nauhoiksi:

- Solmut (x, y, z, leveys) interpoloidaan **sentripetaalisella Catmull-Rom -splinellä** noin 1 m:n välein.
  Tasainen tyyppi kiertyy itsensä ympäri siinä, missä solmut kasaantuvat hiusneulamutkaan. Silmukoidut tiet sulkeutuvat.
- Kukin reuna ottaa maaston korkeuden siinä, missä maasto on 1,5 m:n sisällä tien omasta korkeudesta, ja säilyttää
  tien oman korkeuden muualla (sillalla).
- Materiaalin nimi määrää, mitä jälki maalaa. Ensimmäinen osuma voittaa:

| Laji | Materiaalin nimi täsmää (ensimmäinen osuma voittaa) |
|---|---|
| renkaanjäljet | `rubber`, `skid`, `tire_track`, `tyre_track`, `tread_mark` |
| peitte (koristeellinen) | `crack`, `patch`, `repair`, `damage`, `variation`, `edge`, `erosion`, `leaf`, `litter`, `gutter`, `grass`, `puddle`, `stain`, `oil`, `trace`, `bank`, `flow`, `leak` |
| merkinnät | `line`, `marking`, `crossing`, `zebra`, `parking`, `arrow`, `stripe`, `checker`, `chevron` |
| löyhä | `dirt`, `gravel`, `mud`, `sand`, `snow`, `loose`, `dust`, `soil`, `clay`, `rally` |
| tie | `asphalt`, `road`, `concrete`, `cobble`, `tarmac`, `pavement`, `street`, `paved`, `brick` |
| peite | mikä tahansa muu |

## Maa

Maaston korkeuskenttä käytävän sisällä muuttuu kolmioiksi:

- Yksi nelikulmio maaston ruutua kohden, jonka keskipiste on käytävässä. Ruudut, joiden kerros on 255 (aukot),
  ohitetaan. Jokainen nelikulmio on kaksi kolmiota, ja lävistäjä vaihtuu samalla tavalla kuin Torquen maasto tekee.
- Korkeudet ovat `position.z + h * maxHeight / 65535`. Normaalit tulevat korkeuseroista.
- Jokainen ruutu luokitellaan **kerroksensa** mukaan: kerroksen nimi sen maastomateriaalin maamallin ja
  huomautuksen kanssa. Päällystesanat tekevät siitä `road`-kerroksen, `grass/forest/rock/moss/leaves/cliff/stone`
  tekevät `terrain`-kerroksen, ja löyhät sanat tekevät `loose`-kerroksen (sora ja multa). Muu on `terrain`.
- Sitten **tie- ja löyhät jäljet** korvaavat ruudut, jotka ne peittävät, piirtojärjestyksessä, joten viimeinen
  maalattu jälki päättää.
- Kärjet jaetaan 512 m:n neliöittäin (`floor(x / 512)`, `floor(y / 512)`), joten jokainen osa kartoittuu
  täsmälleen yhteen kuvaan: `u = (x - x0) / 512`, `v = 1 - (y - y0) / 512`.

Konsoli tulostaa `what the ground is made of` kolmiomäärineen lajeittain.

### Mallinnettu ajopinta

BeamNG:n radat ovat yhtä usein malleja kuin maastoa. Raceway-rata voi olla yksi mesh viivoineen, ja kumijälki ja
tärinänauhat meshinä sen päällä. Siksi sijoitetuista malleista kategorioissa tie, reunakivet, reuna, rekvisiitta ja
sillat etsitään ajopintaa. Materiaalikohtaisesti:

| Pinta | Päätetään (ensimmäinen osuma) |
|---|---|
| renkaanjäljet | `skid`, `rubber`, `tire_mark`, `tyre_mark`, `tread` nimessä, maalajissa tai huomautuksessa |
| merkinnät | `line`, `marking`, `zebra`, `arrow`, `stripe`, `crossing` materiaalin nimessä |
| reunakivet | `rumble`, `kerb`, `curb` |
| tie | maalaji `asphalt*`, `concrete*`, `cobblestone`, `tarmac`, `street`, `paved*`, `brick*`, tai nimi sisältää `asphalt`, `tarmac`, `track_edge`, `road_surface` |
| löyhä | maalaji `dirt*`, `gravel*`, `sand*`, `mud*`, `snow*`, `soil*`, `clay*` |
| reuna | `sidewalk` |
| (mallin oma kategoria) | malleille, jotka on jo luokiteltu tieksi, reunakiveksi tai reunaksi |

Näistä materiaaleista käytävän sisällä olevat **ylöspäin osoittavat** kolmiot (normaali z yli 0,5) otetaan pois
mallista ja tulevat maaksi. Ne maalataan laatan leivottuun tekstuuriin ja kirjoitetaan osiin kuten
`ground:road 3_-2 asphalt_light`. Merkinnät ja renkaanjäljet vain maalataan. Mallin loput kolmiot jäävät mallille.
Näitä malleja ei koskaan yksinkertaisteta eikä jätetä budjetin takia pois, koska karkea rata on väärä rata.

## Leivottu maatekstuuri

Jokaisella 512 m:n neliöllä, jossa on maata, on yksi kuva, jossa on `--texture-size`-pikseliä (2048 = 25 cm pikseli),
piirrettynä samalla tavalla kuin peli piirtää maansa:

1. **Maastokerrokset.** Pikselikohtaisesti ympäröivien neljän maastoruudun kerrokset sekoitetaan bilineaarisesti.
   Jokainen kerros värjätään kuten peli sen värjää: materiaalin **pohjakartta** venytettynä `diffuseSize`-metriin
   (tai koko maastoon), sitten **detail**- ja **macro**-kartat harmaina peitteinä
   (`colour * (1 + strength * (2 * overlay - 1))`, 0,5 neutraali). Niiden oletukset toistuvat 2 m:n ja 60 m:n välein,
   voimakkuudet 0,5 ja 0,3, ellei materiaali sano toisin. Kerros ilman materiaalia saa pinnan tasaisen värin.
   Pohjakartan rivi 0 on pohjoinen.
2. **Tiejäljet**, jotka on maalattu vain maastoon, piirtojärjestyksessä, kukin omalla tekstuurillaan, peittokartallaan,
   sävyllään ja peittävyydellään, pitkin nauhaa. Kentät, joita on julkaistu, käyttävät prioriteetteja noin 12-16
   asfalttipohjille, 10 merkinnöille ja 4 kumijäljille.
3. **Mallinnettu ajopinta** ylhäältä nähtynä: pohjat ensin, sitten peitteet, kukin mallin oman toistuvan tekstuurin
   mukaan yhdellä texelillä leivontapikseliä kohden.
4. **Jäljet, jotka projisoituvat myös esineiden päälle** (`overObjects`), viimeisenä.

Ilman `--no-textures`-valintaa mitään ei leiviä: maaosat saavat tasaiset värit, ja mallinnetut merkinnät ja
renkaanjäljet tulevat omiksi osikseen, nostettuina **3 cm**.

## Sijoitetut mallit

Ehdokkaat ovat jokainen `TSStatic`, prefab-lapsi ja metsäesine, jonka origo on ajon käytävässä. Malli piirretään,
jos sen muodon maailman rajauslaatikko koskettaa käytävää.

**Kategoria** tulee kentän omasta merkinnästä ja muodon polusta. Ensimmäinen sääntö, joka täsmää, voittaa:

| Kategoria | Merkintä | Polku tai nimi sisältää |
|---|---|---|
| tausta (ei piirretä koskaan) | | `backdrop`, `skybox`, `sky_dome`, `horizon`, `distant`, `matte` |
| reunakivet | | `kerb`, `curb`, `rumble` |
| tie | `ASPHALT`, `STREET`, `SPEED_BUMP` | |
| reuna | `SIDEWALK`, `COBBLESTONE` | |
| puut (vain `--trees`-valinnalla) | `NATURE` | tree, foliage, bush, grass, plant ja vastaavat sanat |
| kivet | `ROCK` | `rock`, `cliff`, `boulder`, `quarry` |
| kaiteet | `GUARD_RAIL`, `ROADBLOCK` | `guard_rail`, `barrier`, `armco`, `fence`, `wall`, `tire_stack`, `tyre`, `cone`, `bollard`, `jersey`, `railing`, `catch`, `blocker` |
| kyltit | `TRAFFIC_SIGNS` | `sign`, `billboard`, `banner`, `flag`, `arrow`, `marker` |
| sillat | | `bridge`, `overpass`, `tunnel`, `viaduct` |
| infrastruktuuri | `POLE` | `pole`, `light`, `lamp`, `electric`, `power`, `cable`, `pylon`, `antenna`, `mast`, `transformer` |
| rakennukset | `BUILDINGS` | `/build`, `bld_`, `house`, `garage`, `shed`, `hall`, `tower`, `stand`, `pit`, `tent`, `gazebo`, `roof`, `warehouse`, `factory` |
| rekvisiitta | | mikä tahansa muu |

**Muodot** luetaan käännetystä `.cdae`-tiedostosta, tai `.dae`-tiedostosta (Collada), jos välimuistia ei ole (modit).
Muoto, jota ei voi lukea, lasketaan: `N copies of M models could not be read`. Materiaalit, joiden nimi tai tekstuuri on
`invisible`, `collision` tai `nodraw`, eivät piirry koskaan.

**Tekstuurit.** Mallit ryhmitellään kategorian ja materiaalin mukaan osiin, joiden nimi on
`structure:<category> <material>` (tai `ground:kerbs <material>`). Ryhmä saa materiaalinsa värityksen tekstuurin enintään
**256 px**:nä vain, jos sen UV:t pysyvät välillä 0-1 (98 % kärjistä välillä -0,02 - 1,02). Viewer pakkaa tekstuurit atlakseen
eikä voi toistaa yhtä. Ryhmä, jonka tekstuuri toistuu, piirretään tekstuurin keskivärinä (alfapainotettuna, sRGB:nä,
kerrottuna materiaalin sävyllä), tai kategorian värinä, jos sillä ei ole tekstuuria.

**Yksityiskohtaisuus** noudattaa yhteistä järjestelmää, kuvattu sivulla
[Yksityiskohtaisuustasot ja budjetti](detail-budget.md). BeamNG:n yksityiskohtaisuustasot ovat muodon `details`
(suurin pikselikoko ensin). Budjetin ylittyessä kaukaisimmat kopiot menevät ensin. Reunakivet ja mallit, joilla on
ajopinta, eivät koskaan yksinkertaistu tai jää pois.

`--no-placed` pudottaa rakenteet mutta säilyttää mallinnetun ajopinnan. `--trees` lisää puukategorian.

## Vesi

| Lähde | Piirretään |
|---|---|
| `WaterPlane` (meri) | 4 m:n nelikulmio veden korkeudessa jokaiselle käytävän ruudulle, jossa mikään maasto ei yllä siihen korkeuteen |
| `WaterBlock` | yksi nelikulmio, yksikköneliö paikallisessa z = 0 lohkon muunnoksessa (joten sen skaala asettaa koon), jos se koskettaa käytävää; onko z = 0 lohkon pinta, on vahvistamatta |
| `River` | nauha sen solmujen kautta, jos se koskettaa käytävää |

Kaikki vesi on yksi tasainen osa, `water:water`.

## Ei piirretä

- Maanpeite (proseduraalinen ruoho).
- Maisema, joka on sijoitettu maailman reunan ympärille (`backdrop` ja vastaavat).
- Toistuvat mallitekstuurit, jotka tulevat keskivärinä (katso yllä).
- Skinnatut meshit (ajoneuvot, hahmot) ja muodon sisällä olevat tarramallit.

## Tarkistukset tämän takana

Kuten lähdekoodissa sanotaan, mitattuna toimitetuissa kentissä:

- Tien solmut ovat maastossa 1-2 cm:n tarkkuudella (mediaani) tarkistetuilla kentillä, kun käytetään `h * maxHeight / 65535` ja rivejä +y-suuntaan. `h / 32` tai muu akselijärjestys menee ohi kymmeniä tai satoja metrejä.
- Tietä pitkin ketjutetut kiskojaksot kulkevat `rotationMatrix`-rivin 0 suuntaan (suuri enemmistö).
- `.cdae`-solmun kierto on transponoitava. Sen jälkeen maailman rajat täsmäävät lähde-`.dae`:n kanssa millimetrin tarkkuudella. Oppikirjan mukaan ne ovat 38 cm pois (mediaani).
- Vietiin useilla toimitetuilla kentillä kaikkia lajeja, sekunneista minuutteihin kukin.
