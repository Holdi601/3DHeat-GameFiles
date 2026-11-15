---
title: "Forza Horizon"
lang: "fi"
source: course-forza-horizon.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Kurssin vienti: Forza Horizon

Forzan vienti lukee radan suoraan pelin ForzaTech-arkistoista: maaston, jossa tie, reuna ja nurmi on erotettu toisistaan,
maatekstuurin, leivotun pelin omista maakartoista, ja jokaisen sijoitetun mallin omalla tekstuurillaan (reunakivet,
kaiteet, renkaiset esteet, kyltit, rekvisiitta, rakennukset). Se löytää myös, minkä pelin kisoista ajo tehtiin,
ja lisää sen, minkä peli tuottaa juuri sille kisalle (sen tapahtumakerroksen: esteet, teltat, portaalit, katsomot, liput),
sekä minkä tahansa paikan maan, jonka läpi ajo kulkee, kuten stadionin lattian.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Lähteet: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Itse säilömuodot ovat sivulla [ForzaTech](reader-forzatech.md).

## Asennetun pelin löytäminen

Kenenkään ei pitäisi joutua kirjoittamaan polkua kuten
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, joten polku selvitetään itse:

1. **Steam-kirjastot.** Steamin `config\libraryfolders.vdf` luetaan kohdasta
   `C:\Program Files (x86)\Steam` tai `C:\Program Files\Steam`, ja jokainen sen `"path"`-merkintä on kirjasto. Jokaisen kirjaston
   `steamapps\common` etsitään.
2. **Microsoft Store.** `C:\XboxGames` etsitään, jos se on olemassa. Siellä peli on yhden tason syvemmällä,
   kansiossa `<game>\Content`.
3. **Pelikansio** on mikä tahansa näiden kansioiden lapsi, jolla on kansio `media\Tracks`, nimestä riippumatta.
4. **Radan kansio** on mikä tahansa kansio kohdassa `media\Tracks`, jossa on `GeoChunk0.minizip`. Se tunnistetaan sisällön,
   ei nimen perusteella, joten rata nimellä, jota kukaan ei ole nähnyt, löytyy silti.

Jos peli on muualla, anna radan kansio valinnalla `--track`; katso
[Vianetsintä](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` ohittaa kaiken tämän.

Radan kansiossa on se, minkä vienti lukee:

| Tiedosto | Mikä se on |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | arkistot: jokainen malli-, tekstuuri- ja sijoitustiedosto, ilman nimiä sisällä |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | yksi rivi arkiston merkintää kohden, merkintöjärjestyksessä: ainoa nimilähde |
| `AssetManifest.xml` | jokainen radan toimittama tekstuuri, sen tiiviste, jolla materiaalit viittaavat siihen |

## Mikä rata

Peli toimittaa useamman radan kansion (avoin maailma, yksi tai kaksi autotallia). Oikea valitaan
**koordinaattien, ei nimen perusteella**:

- Kysymys on ajon rajauslaatikko, leventänä `--margin`-valinnalla.
- Jokaisesta radan kansiosta luetaan neljä `ChunkContentsMiniZip*.txt`-luetteloa tekstinä, avaamatta arkistoa. Jokainen maaston
  laattanimi (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) kantaa ruudukkosijaintinsa. Työkalu laskee,
  kuinka monta eri laattaa osuu laatikkoon.
- Rata, jolla on eniten laattoja siellä, voittaa. Jos millään radalla ei ole yhtään, vienti pysähtyy viestillä
  "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Koko radan vastaus tulee alle sekunnissa. Pelkkä nimivertailu voisi valita väärän kartan, ja väärä kartta näyttää
yhtä uskottavalta kuin oikea.

Konsoli sanoo `on <track>, in <game folder>`.

## Mikä kisa

Peli toimittaa jokaisen kisansa reittinä, jolla on numero, sen **reitin tunnuksena**. Kaksi tiedostoa kuuluu
jokaiseen reittiin:

| Tiedosto | Mitä se sisältää |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | kisan tekoälyn ajolinja: 56 tavun solmu tavusta `0x60` alkaen, solmujen määrä kohdassa `0x24`, jokainen solmu alkaa sijainnilla (x, y, z) pelin metreinä |
| `media\Stripped\gs\<map>\routedefinitions.zip` | yksi `route<id>_<map>.rtd` kisaa kohden: tavallista XML:ää, joka listaa, mitä kisa lisää maailmaan ja mitä se poistaa (katso [Kisan oma kerros](#the-races-own-layer)) |

Ajo sovitetaan reittiin vertaamalla sitä jokaiseen tekoälylinjaan, jonka laatikko menee päällekkäin ajon laatikon kanssa:

- Jokaisesta ajonäytteestä: etäisyys linjan lähimpään pisteeseen; ja jokaisesta linjan pisteestä: etäisyys lähimpään ajonäytteeseen.
- Kaksi mediaania lasketaan yhteen. Pienin summa voittaa, jos se on alle **30 m** (`MATCH`).
- Molempia suuntia tarvitaan: lyhyt sprintti kulkee pitkän reitin varrella, joka käyttää samaa tietä, ja pitkä ajo kattaa lyhyen reitin.

Konsoli sanoo `the game's route <id> (driven line within <n> m of it)`, tai että reittiä ei löydy. Ilman osumaa
sijoitetaan vain vapaan ajon maailma.

## Maasto

Miten maasto löydetään (tiedostossa `forzaterrain.py`):

- Luettelot nimeävät maaston tilaindeksinä:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Kaksi lukua ovat ruudukkokoordinaatteja, jotka **etenevät 1023:n välein**, ja jokainen ruudukkoaskel on **512 m:n** laatta.
  Laatta `x-2046` on `-2046 / 1023 = -2`, ja se alkaa kohdasta `-2 * 512 = -1024` m. Jos luet nimet metreinä, jokainen haku
  menee pieleen kertoimella kaksi ja palauttaa silti maastoa, kartan väärästä osasta.
- Laatta voi esiintyä kolmesti: tavallisena, `_cb`- ja `_ul`-muotoisena. Kaikki kolme kattavat saman maan. Yksi otetaan
  laattaa kohden, tässä etusijajärjestyksessä, koska niiden yhdistäminen kolminkertaistaisi geometrian päällekkäisiksi pinnoiksi.
- Laatta luetaan vain, jos se koskettaa ajon laatikkoa **ja** käytävää. Laattaa, jota käytävä ei kosketa, ei koskaan puretta.
- Jokainen valitun laatan `.modelbin` dekoodataan vain **yksityiskohtaisuustasolla 0**. Laatassa on neljä tasoa samasta maasta,
  ja kaikkien vieminen panisi saman neliömetrin tiedostoon neljästi.
- Jokaisella meshillä on oma maailman skaalansa ja bias-arvonsa, joten laatta asettuu sinne, minne peli sen asettaa,
  ilman instanssimuunnosta. Kolmiot, joiden jalanjälki menee laatikon päälle, säilytetään, ja sitten vain ne, jotka ulottuvat käytävään.
- Mesh muodossa, jonka lukija hylkää, ohitetaan ja lasketaan (`N meshes could not be read`), joten ohut tulos kertoo syynsä.

Maastoyhteenveto tulostaa kärkien määrän, kolmioiden määrän, meshien määrän, laattojen määrän ja x/y/z-ulottuvuuden.

### Tie, reuna, maasto, merkinnät, vesi

Materiaalien nimet eivät kerro, missä tie on. Kiertoradan ympärillä 94 % maasta käyttää tiemateriaalin varjostinta, koska
tien lähellä oleva maasto piirretään sillä, ja varjostin päättää asfaltin tai nurmen pikselikohtaisesti. Joten:

| Laji | Päätetään |
|---|---|
| tiekaista | **kärkien asettelu**: tiekaistat ovat ainoa maa, jolla on toinen UV-joukko (kanava 1); kolmio, jonka kaikilla kolmella kärjellä se on, on tietä |
| asfaltti vs. reuna | tiekaistan sisällä laatan **asfalttimaski** kolmion keskipisteessä: 0,5 tai enemmän on `road`, vähemmän on `verge` |
| merkinnät | materiaalin nimi täsmää `whiteline`, `yellowline` tai `decal` |
| renkaanjäljet | materiaalin nimi täsmää `tyremark` tai `skid` (tarkistetaan ennen merkintöjä, koska renkaanjäljet toimitetaan nimellä `tyremark_decal_*`) |
| vesi | materiaalin nimi täsmää `water`, `lake`, `river`, `paddy`, `ocean` tai `sea` |
| maasto | kaikki muu |

Mitattuna kisa-ajoista testiradalla lähes kaikki näytteet osuvat tiekaistan kolmioihin, ja suuri enemmistö asfaltin
osaan, kun maski on erottanut reunan.

Asfalttimaski on olemassa vain, kun maatekstuurit leivotaan. Valinnalla `--no-textures`, tai laatalle, jonka kartat puuttuvat,
tiekaistat pysyvät kokonaisina `road`-osina, eikä reunaa erotella. Puuttuvat kartat maksavat yksityiskohtia, eivät geometriaa.

### Maalatut kerrokset nostetaan

Merkinnät ja renkaanjäljet toimitetaan omina kolmioinaan, jotka makaavat täsmälleen tiellä. Peli piirtää ne syvyyssiirtymällä.
Jos ne piirrettäisiin sellaisinaan, tie ja maali taistelisivat jokaisesta pikselistä. Vienti antaa jokaiselle merkintä- ja
renkaanjälkiosalle oman kopion kärjistään, nostettuna **5 cm** (`DECAL_LIFT`) pinnan normaalia pitkin, joten tie sen alla
ei nouse mukana.

### Normaalit

Maaston normaalit tulevat arkistosta. Normaalin x tallennetaan sijainnin neljäntenä lyhytnä, ja y ja z
`NORMAL`-attribuutissa (katso [ForzaTech](reader-forzatech.md)). Jos jollakin kärjellä purussa ei ole normaalia,
koko maan normaalit lasketaan kolmioista.

## Maatekstuuri

Jokainen maaston laatta toimittaa kolme karttaa, jotka kattavat sen 512 m:n neliön, viidessä resoluutiossa
(`_quality1` - `_quality5`, suurin 2048 px, mikä on 25 cm pikseli):

| Kartta | Tiedostonimen malli | Mitä se sisältää (mitattuna) |
|---|---|---|
| pääkartta | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: yksityiskohtainen normaali (x, z). A: matala asfaltilla ja karkealla maalla |
| ala | `submap_x<X>_z<Z>_x<season>x_diff` | kerrospainot. B: korkea asfaltilla (239 ajolinjalla, 165 sen vieressä) |
| kiilto | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: matala asfaltilla (147 vs. 215). B: nousee metsässä |

Mikään näistä ei ole värivalokuva. Ne ovat syötteitä, joilla pelin maastovarjostin sekoittaa materiaalikerroksensa,
eikä niitä kerroksia dekoodata. Joten leivottu tekstuuri on **tulkinta, ei kopio pelin ulkonäöstä**. Se säilyttää
*missä* kukin maalaji on, 25 cm:n tarkkuudella, ja maalaa sen kiinteillä väreillä:

| Maa | Lineaarinen RGB | Paino |
|---|---|---|
| nurmi (lyhyt, lähellä rataa) | 0,30, 0,44, 0,18 | pohja |
| karkea (kauempana) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| metsä | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfaltti | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Molempien karttojen täytyy olla samaa mieltä asfaltista. Kumpikin yksin jättää harmaata pilkkua nurmeen siellä, missä
lohkopakkaus kehää. Tulos varjostetaan pääkartan yksityiskohtaisella normaalilla kiinteää valoa vasten (`0.55 + 0.6 * lambert`),
joten reunakivien kieleke, penkereet ja urat lukeutuvat muotoina, ja tallennetaan 8-bittisenä sRGB:nä.

Suunta: kuvan rivi 0 on laatan **pohjoinen** reuna (suurin z), sarake 0 sen **läntinen** reuna (pienin x). Tämä löydettiin
projisoimalla tallennetut ajot asfalttimaskille kaikilla kahdeksalla tavalla, joilla neliö voidaan kääntää tai peilata.
Täsmälleen yksi tapa asettaa ne asfaltille. UV:t seuraavat siitä: `u = (x - x0) / 512`, `v = 1 - (z - z0) / 512`.

Kartat luetaan parhaalla saatavilla olevalla resoluutiolla asti laatuun 5, ja ne skaalataan pääkartan kokoon.
Jos värikuva on suurempi kuin `--texture-size`, se pienennetään siihen Lanczos-suodatuksella. Asfalttimaski säilytetään aina
täydellä resoluutiolla, koska se päättää geometriasta. `--season` valitsee `x<season>x`-kartat. Laatta, jolla ei ole karttoja
sille vuodenajalle, piirretään tasaisin värein, ja konsoli ilmoittaa `N without maps`.

## Sijoitetut mallit

Maasto kantaa oman maailmasijaintinsa. Mikään muu ei kanna. Missä kukin mallin kopio seisoo, on tallennettu
`.pgeo`-sijoitustiedostoihin, yksi kutakin kategoriaa ja tilaruutua kohden:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Tietuerakenne on sivulla
[ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Mitä luetaan

- Sijoitustiedostot suodatetaan **nimen mukaan**: solukoko ja solun sijainti polussa antavat solun neliön (`x * size` - `(x + 1) * size`),
  ja vain ajon laatikkoa koskettavat solut, halutussa kategoriassa, avataan.
- Kategoriat oletuksena: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` lisää
  `trees`, `bushes` ja `smashables`. Näitä ei koskaan lueta: `grasstemplate`, `crowdtemplate` ja `cwdspline` (ruoho ja katsojat:
  peli piirtää ne animoituina spriteinä, niillä ei ole geometriaa).
- Jokainen tiedosto kuuluu **kerrokseen**, joka luetaan sen nimestä kohdasta `c<size>_<category>_` eteenpäin. Tason sanat
  (`do`, `so`, `ulc`, `ulp`, `cwd`) ja valinnainen osanumero ovat vapaan ajon maailma. Mikä tahansa muu on kerros, jonka peli
  kytkee päälle: ajonaikainen kerros (`rt_0`), toiminto (`_tag_<name>_`), keräilyesine, tai mikä tahansa `evolving`-alla oleva.
  Kerros, joka nimeää reitit (`rt_x<id>`, esimerkiksi `rt_x1023_x2201`), kuuluu vain niille kisoille, ja se luetaan vain, jos
  ajo osui yhteen niistä. Katso [Päälle kytketyt kerrokset](#switched-on-layers).
- Kopio säilytetään, jos sen sijainti on laatikon sisällä ja käytävän sisällä. Täsmälleen samat toistot (sama sijainti ja suunta
  millimetriin asti, kahden naapuriruudun listaamina) yhdistetään.
- **Reunakivet** ovat rekvisiittaa, jonka mallin nimi alkaa `road_gen_rum` (tärinänauhat). Ne kirjoitetaan `ground:kerbs`-osaksi, eivät
  koskaan yksinkertaisteta eivätkä jää pois, koska ajo mitataan niitä vasten.

| Kategoria | Osa | Varaväri (ei tekstuuria) |
|---|---|---|
| reunakivet | `ground:kerbs` | 0,60, 0,12, 0,10 |
| kaiteet | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekvisiitta | `structure:props` | 0,45, 0,35, 0,25 |
| kyltit | `structure:signs` | 0,70, 0,70, 0,70 |
| rakennukset | `structure:buildings` | 0,55, 0,52, 0,48 |
| infrastruktuuri | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| sillat | `structure:bridges` | 0,45, 0,45, 0,45 |
| kivet | `structure:rocks` | 0,30, 0,28, 0,25 |
| murskattavat | `structure:smashables` | 0,12, 0,22, 0,06 |
| puut, pensaat | `structure:trees` | 0,10, 0,20, 0,05 |

### Mallin geometria

Sijoitettu nimi `<model>_3D` viittaa mallitiedostoihin `<model>_cluster###.i.modelbin` (enintään tusina).
Jokainen kolmio kantaa peitteen niistä yksityiskohtaisuustasoista, joihin se kuuluu:

- Mallin tasot ovat sen kolmiot, jotka on nimenomaisesti merkitty kyseiselle tasolle. Tasot ovat peräkkäisiä nollasta alkaen, hienoin ensin.
- Kolmiot, jotka on merkitty `0xFFFF` (kaikki tasot), ovat hajoavia paloja, kuten kaiteen pylväät tai renkaiden pinon yksittäiset renkaat. Ne
  peittävät koko mallin, ja peli piirtää ne sen sijaan, kun se on hajotettu. Niitä käytetään vain mallissa, jolla ei ole nimenomaisesti
  merkittyä tasoa.
- Alimeshit, joiden materiaalivarjostin on projisoitu **decal**, jätetään pois.

Jokainen kopio sijoitetaan omalla sijainnillaan, x- ja y-akseleillaan tietueesta (z = x cross y), ja skaalallaan. Normaalit
muunnetaan käänteisellä skaalalla.

### Mikä tekstuuri

Materiaali ei nimeä tekstuureitaan. Se luettelee ne tiivisteinä, ja radan `AssetManifest.xml` kuvaa jokaisen tiivisteen (`SourceHash`)
tekstuurin nimeksi. Luetaan vain `<Textures>`-osio, ja lukeminen pysähtyy kohtaan `</Textures>` tiedostossa, joka voi olla kymmeniä megatavuja. Sitten:

1. Paikka `0x88B483AA` on peruspohjaväri standardissa ympäristövarjostimessa (jokainen otettu materiaali). Jos materiaali sitoo siihen tekstuurin, sitä käytetään.
2. Muuten tekstuurin oma laji päättää, joka on sanan ennen sen GUID:ia: `_bclr_`, sitten `_diff_`, sitten `_colour_`.
3. Maastokartat (`mainmap`, `submap`, `autogloss`) ja väripaletit (`tint`, `worldtint`) eivät koskaan värjää mallia.

Malli värjätään siis sen mukaan, mitä sen materiaali sitoo, ei sen mukaan, millä on mallin nimi. Esimerkiksi
`bar_rur_armco_crct_02_c` käyttää `..._02_a`:n tekstuuria.

Tekstuuri luetaan arkistoista pienimmällä resoluutiolla, joka on vähintään **256 px** leveydeltä (`MODEL_TEXTURE`), pienennettynä 256:een, jos se on suurempi,
ja tallennetaan `.glb`:hen RGB JPEG:nä. Kaiteen väri 256 px:llä neljälle metrille on 1,6 cm pikseli, ja noin 80 tällaista tekstuuria mahtuu viewerin atlakseen
maalaattojen viereen.

**Vuodenajat.** `--season` vaihtaa tekstuurin sen vuodenaikaiseen vastineeseen nimellä, GUID jätettynä huomiotta
(`..._xsummerx_bclr` -> `..._xwinterx_bclr`, tai `..._bclr` -> `..._winter_bclr`), jos radalla on sellainen. Valinnalla `--season winter` alimeshin
talvimateriaalia käytetään myös siellä, missä sen varianttitaulukko sellaisen nimeää.

**Variantit.** Alimeshitietue alkaa `(summer, winter)`-materiaalien taulukolla, yksi kutakin ulkonäköä kohden, jonka kopio voi kantaa: viisi tulostetta mainostaululle,
kuusi maalivärisävyä renkaiden pinolle. Jokainen sijoitustietue kertoo, mitä varianttia kopio kantaa. Alimeshi, jolla on vähemmän variantteja kuin mallilla,
toistaa omansa.

**Paikkamerkkilohko.** Yhteiset rakennusatlakset varaavat kiinteän RGB (255, 64, 0) -lohkon pinnoille, joita rakennusvarjostin värjää muista tekstuureista.
Jos yli kaksikymmenesosa tekstuurista on 12 tason sisällä tästä väristä, lohko maalataan uudelleen tekstuurin oman keskivärin mukaan. Muuten kaupunki tulisi oranssina.

### Läpinäkyvät pinnat

Ketjuaidat ja verkot ovat yksittäisiä nelikulmioita, joissa on reikiä tekstuurin alfassa. Jos ne piirretään kiinteinä, aita on seinä näkymän yli radalle. Pinnat, joiden materiaalivarjostin
täsmää `alphatest`, `alphablend`, `transmissive`, `anim_flag`, `impostor`, `branch`, `bush` tai `tree`, testataan:

- Tekstuurin peittävyys keskiarvoistetaan 32 x 32 -ruudukolla.
- Pinnoittain (jokainen leikattu kolmio, joka jakaa saman tekstuurin) jokaisesta kolmiosta otetaan neljä pistettä UV-avaruudessa, painotettuna kolmion UV-alalla.
- Jos keskimääräinen peittävyys on vähintään 0,05 ja alle **0,5**, koko pinta jätetään pois. Alle 0,05 alfa tarkoittaa selvästi jotain muuta sen varjostimelle (varoitusmerkki, joka näytteistää 0,01), ja pinta säilytetään kiinteänä.
- Malli, jonka jokainen pinta jätettiin pois, ilmoitetaan: `N models left out as see-through (mostly holes in their texture)`.

Työkalu arvioi koko pinnan eikä yhtä kolmiota kerrallaan. Kolmio kerrallaan arvioituna puolet jokaisesta nelikulmiosta säilyi, ja aidat tulivat ulos hampaiden riveinä.

### Rakennukset piirretään kokonaisina

Kaupunki rakentaa rakennuksensa modulaarisista paloista: satoja tuhansia niitä yhden katuradan ympärillä, kymmeniä miljoonia kolmioita
jopa karkeimmillaan. Palojen jättäminen pois yksi kerrallaan jätti yksittäisiä seinälevyjä seisomaan. Peli toimittaa myös kokonaisten rakennusten
korvikkeita kohdassa `scene\hlod_tier_1\`, yksi mesh rakennusta kohden (kanta `hlod_tier_1_*`), jo maailmakoordinaateissa kuten maasto:

- Jokaisen korvikkeen maailmalaatikko luetaan sen meshin sijaintilaatikosta (otsikkolukema, ei dekoodaus). Tämä kestää sekunteja koko kartalle.
- Korvikkeet, jotka koskettavat ajon laatikkoa ja käytävää, otetaan käyttöön.
- Jokainen `buildings`-pala, jonka sijainti on korvikkeen pohjan sisällä (plus 0,5 m), pudotetaan, ja korvike piirretään sen tilalle. Sen etäisyys ajoon mitataan rakennuksen lähimpään reunaan.
- Yhteenveto kertoo: `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Päälle kytketyt kerrokset

Se, mitä päälle kytketty kerros sijoittaa, viedään, mutta vapaan ajon maailman ulkopuolella, jotta viewer voi näyttää tai piilottaa sen:

| Kerros | Osa |
|---|---|
| vapaan ajon maailma | `structure:<category>` (kuten ennen) |
| kerros, joka nimeää kisan reitin | `structure:event_<category>` |
| mikä tahansa muu päälle kytketty kerros | `structure:layer_<category>` |

Yhteenveto laskee ne: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Mallit, jotka ovat jo maailmakoordinaateissa

Muutamaa mallityyppiä ei ole millään sijoitustiedostossa. Niiden meshit kantavat oman maailmasijaintinsa, kuten maasto tekee, joten mitään ei tarvitse sijoittaa:

| Kansio `scene\models\` alla | Mikä se on | Osa |
|---|---|---|
| `plots` | paikan oma maa: stadionin lattia ja kenttä, festivaalialue, aukio | `ground:venue` |
| `plinths` (ja mikä tahansa malli nimeltä `floor`, `ground` tai `road`) | maa, jolla katu on koristeltu: istutuslaatikot, portaat, puiston päällystys | `ground:plinths` |
| `hda_infrastructure` (sillat) | proseduraalisesti rakennetut sillat | `structure:bridges` |

- Malli lasketaan olevan maailmakoordinaateissa, kun sen laatikon keskipiste on yli **300 m** (`WORLD_REACH`) sen oman origon päässä. Sijoitustiedostojen mallit ovat muutaman sadan metrin sisällä omasta origostaan.
- Ei piirretä: näkyvyyden estäjät, ajojen varrelle venytetyt kaapelit, maailman reunan taustan, modulaaristen rakennusten katot ja estäjät (korvikkeet piirtävät ne rakennukset), törmäys- ja vesitilavuudet.
- Jokainen luetaan sen meshien laatikosta (otsikkolukema), muutama sekunti koko kartalle, kerran per ajo.
- Maaosia ei koskaan piirretä karkeammin, eikä jätetä pois budjetin mahduttamiseksi, kuten reunakivet.

**Paikka leikataan kokonaisena.** Kun ajo koskettaa paikan omaa maata (`ground:venue`), käytävä levennetään koko tuon maan alueeseen plus
`--margin`, joten stadionin ympärillä olevat katsomot, seinät ja esteet tulevat mukaan, eivät vain se kaista, jonka kierrokset käyttivät. Konsoli sanoo
`through a venue (<model names>): cutting all of its ground, <n> km2`. Plinthit eivät levennä leikkausta.

### Yksityiskohtaisuus ja budjetti

Etäisyyskaistat, budjetti ja se, mitkä kopiot lähtevät, kun budjetti on liian pieni, ovat sivulla
[Yksityiskohtaisuustasot ja budjetti](detail-budget.md).

### Sijoitusyhteenveto

```
  placed on it (1,500,000 triangles of a 1,500,000 budget, 91 textures):
        102 placed     3 models        8,568 triangles  ground:kerbs
      2,278 placed    14 models      ...                structure:barriers
    12 of 107 models drawn at a coarser level to fit the budget
    174 buildings drawn whole from the game's own stand-ins (which replace 5,120 modular pieces)
    120,000 of 125,000 copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)
    2 models left out as see-through (mostly holes in their texture): fence_a, net_b
    3 placed names have no model in the archives: ...
    venue: the driving passes through 2 pieces of a site's own ground (plt_example_floor_a, plt_example_lawn_a)
    1 models drawn where the game builds them in place (plinths, bridges)
    event layer (route 1234): 1,200 copies in barriers, decals, infrastructure, props
    40 free-roam objects left out: the race takes them away
    switched-on layers: 12 copies in 2 (rt_0, tag_example)
```

## Kisan oma kerros

Monet kisat tuottavat asioita, joita ei ole vapaassa ajossa: betoniseiniä ja aitoja, jotka sulkevat sivuteitä, renkaiden pinoja, telttoja, lähtöportaalin,
katsomoja, lippuja, banderolleja. Jokainen kisa listaa ne reittimäärittelyssään (`route<id>_<map>.rtd` tiedostossa `routedefinitions.zip`, tavallista XML:ää tavallisessa zip-tiedostossa):

```
<Route>
  <HiddenAssets>
    <Transform guid="..." value="16 numbers" />        free-roam objects the race removes
  </HiddenAssets>
  <RouteAssets>
    <Instance>
      <Model value="tracks\<map>\scene\models\<kind>\...\<model>.model" />
      <Transform value="16 numbers" />                  what the race adds
      <Material value="n" />
    </Instance>
  </RouteAssets>
</Route>
```

- **Mitä lisätään.** Jokainen instanssi sijoitetaan kuten sijoitustiedoston kopio. Muunnoksen 16 lukua ovat neljä riviä: mallin x-, y- ja z-akselit (kukin skaalattuna)
  ja sen sijainti pelin metreinä. Kolmas rivi on kahden ensimmäisen ristitulo. `Material` on variantti, jonka kopio kantaa. Osa on
  `structure:event_<kind>`, `<kind>` on kansio `scene\models\` alla (barriers, props, infrastructure, signs; mikä tahansa muu lasketaan rekvisiitaksi),
  ja solmu kantaa glTF-lisätiedot `{"layer": "event", "route": <id>}`.
- **Mitä poistetaan.** Vapaan ajon kopio, joka seisoo **0,1 m:n** sisällä piilotetun omaisuuden sijainnista, jätetään pois. Piilotettu omaisuus, joka seisoo origossa, on
  maailmakoordinaateissa oleva malli; sen instanssi-GUID haetaan radan `AssetManifest.xml`:stä (`<Models>`-luettelo: mallin lähde, sitten sen kopioiden GUID:t) sen nimeämiseksi.
- **Kisan piilottama maa säilytetään.** Kisa, joka piilottaa paikan maan, asettaa sinne oman pintansa. Kun se pinta ei kuulu radan toimittamiin malleihin, piilotettu maa jää paikalleen
  lähimpänä sitä, mitä ajetaan, ja yhteenveto kertoo sen (`kept <model>: the race hides it for a surface of its own that the track does not ship`).
- **Ei piirretä, mutta lasketaan.** Katsojamerkit (`crowd_proxies`: peli piirtää väkijoukon spriteinä niistä) ja törmäyssplinet (`.splinecol`). Konsoli luettelee ne:
  `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Kisan mallit, joita radan toimittama malli ei ole (valogloriat, osa kylteistä, peli, joka suoratoistaa sisältöä), nimetään kohdassa
  `placed names have no model in the archives`.

Vain käytävän sisällä olevat kopiot sijoitetaan, kuten kaikki muu.

## Tiedoston kirjoittaminen

Osat kirjoitetaan tässä järjestyksessä: laatta kerrallaan `terrain`, `verge`, `road` (kukin laatan kuvalla), sitten `water`, `tyre marks`, `markings` (tasaisina, kaksi viimeistä nostettuina), ja sitten jokainen sijoitettu osa nimen mukaan lajiteltuna. Koordinaatit ovat pelin omia (metrejä, Y ylös). Katso [Tulostemuoto](output-format.md).

Tiedosto kertoo, mitä se sisältää, glTF:n `asset.extras`-kentässä:

| Kenttä | Merkitys |
|---|---|
| `course_format` | `2`: kisan oma kerros, paikat ja maailmakoordinaateissa olevat mallit ovat siinä. [`courses`](commands.md#courses) vie pienemmän numeron (tai ei numeroa) omaavan tiedoston uudelleen |
| `route` | täsmätty reitin tunnus tai `null` |
| `event_copies`, `event_kinds` | kuinka monta kopiota kisan omasta kerroksesta sijoitettiin, ja niiden lajit |
| `hidden` | vapaan ajon kopiot, jotka jätettiin pois, koska kisa poistaa ne |
| `venue` | paikan maa-mallit, joiden kautta ajo kulkee |
| `layers` | sijoitetut päälle kytketyt kerrokset |

## Mitä se maksaa

Karkeita suuruusluokkia:

| Kurssi | Tulos |
|---|---|
| lyhyt maantiekisa | muutama sadan tuhannen maan kolmio, yli miljoona sijoitettua; sekunteja, alle 100 MB |
| pitkä pisteestä pisteeseen -sprintti | käytävä on pieni osa ympäröivästä laatikosta; noin minuutti, muutama sata MB |
| kaupunkikatuynnys | tuhansia kaiteita, rekvisiittaa ja kylttejä sekä kokonaisia rakennuksia; automaattisella budjetilla jopa useita satoja MB |

Neliökilometri avointa maailmaa on noin miljoona kolmiota.

## Tarkistukset tämän takana

Nämä ovat mittauksia, jotka tehtiin lukijaa kirjoitettaessa, kuten lähdekoodissa sanotaan. Testit eivät aja niitä uudelleen, ellei peli ole asennettu.

- Testiradalla auto istuu noin ajokorkeutensa päällä purettua maata (mediaani alle 0,2 m).
- Jokainen näytteistetty laatta osuu 512 m:n neliöön, jonka sen nimi ennustaa.
- Peräkkäiset kaidesijoitukset ovat täsmälleen 4 m:n päässä toisistaan, ja useimmat kaiteen päät osuvat 5 cm:n tarkkuudella seuraavan alkuun.
- Reunakivet istuvat muutaman senttimetrin verran purettua maata korkeammalla, kasvot ylöspäin, 5 m:n sisällä ajosta (myös asennetun pelin testi, katso [Kehitys](development.md)).

## Ei piirretä

- Puut ja pensaat, ellei `--trees`. Ruoho ja väkijoukot eivät koskaan (peli piirtää ne spriteinä).
- Kisan omat mallit, joita rata ei toimita (katso [Kisan oma kerros](#the-races-own-layer)).
- Projisoidut tarramateriaalit malleilla.
- Merkkitarrat, jotka on alfasekoitettu taulunsa päälle, tulevat läpinäkymättöminä.
- Maan väri on rekonstruktio siitä, missä asfaltti, nurmi ja metsä ovat, ei pelin oma maamateriaali.
