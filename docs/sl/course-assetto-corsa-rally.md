---
title: "Assetto Corsa Rally"
nav_order: 3
lang: "sl"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Izvoz proge: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally je zgrajen na Unreal Engine 5 (5.6.1, prirejena različica) in svojo vsebino shranjuje v kontejnerjih IoStore. Noben ni šifriran. Izvoz iz kroga najde etapo in usmerjenost osi. Zapiše lastne talne ploščice etape, razdeljene na cesto in teren, teksturirane z zapečeno talno barvo etape, druge modele pa v enobarvnih ploskvah po kategorijah.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Viri: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (namestitev, etape, postavitev),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (izvoz).
Bralniki Unreal, na katerih to stoji, so opisani na [Unreal 5 IoStore](reader-unreal-iostore.md),
dekompresija pa na [Oodle](reader-oodle.md).

**Stanje:** preverjeno na nameščeni igri s krogi, ustvarjenimi v naključnem koordinatnem sistemu na vsaki etapi. Vsakič je našlo pravo etapo in koordinatni sistem. Krog, posnet v sami igri, še ni bil obdelan.

## Iskanje namestitve {#finding-the-install}

- `--install <mapa>`: mapa igre, ali njena `Content\Paks`, ali katerakoli mapa z datotekami `.utoc`. Orodje preveri `<mapa>`, nato `<mapa>\acr\Content\Paks`, nato `<mapa>\Content\Paks`.
- Sicer se v vsaki knjižnici Steam preveri `steamapps\common\Assetto Corsa Rally`.
- Vsaka `.utoc` datoteka v tisti mapi se odpre kot en shranjevalnik. Kontejnerji, ki se ne odprejo, se preskočijo. Če se nobeden ne odpre, je sporočilo "no readable IoStore containers in ...".

Večina blokov je stisnjena z Oodle, knjižnica pa se išče na računalniku (preišče se vsaka knjižnica Steam). Glejte [Oodle](reader-oodle.md).

Igra se šteje za AC Rally, če datoteka kroga navaja `"game": "assetto-corsa-rally"` (ali `acrally`), ali če podate `--game acrally`.

## Kaj je etapa {#what-a-stage-is}

Etapa je zemljevid **World Partition**:

- `Content\Levels\<Stage>.umap` postavi daljni teren.
- Zapečene celice pod `Content\Levels\<Stage>\_Generated_\*.umap` postavijo vse drugo.

Nivo šteje za etapo, če njena okoljska mapa, `Content\Environments\<Stage>\`, vsebuje mapo `MeshesTrack`. Orodje ne gre po imenih ploščic, ker etapa lahko ploščice poimenuje po kraju, ne po svojem zemljevidu. `--level` se ujema z imeni zemljevidov brez razlike med velikimi in malimi črkami. Napačno ime izpiše etape, ki obstajajo.

Nobene **višinske mreže** (landscape) ni. Tla so statični meshi:

| Ploščice | Pot | Postanejo |
|---|---|---|
| ploščice proge, okoli 175 m, razdeljene na dva dela | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` in `..._Terrain_k` | `ground:road` in `ground:terrain` (neločena ploščica proge, na primer zamrznjeno jezero, je v celoti cesta) |
| daljni teren, ploščice po 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Branje postavitev {#reading-the-placements}

Mesh postavi `StaticMeshComponent`: njegov `StaticMesh` ter njegovi `RelativeLocation`, `RelativeRotation` in `RelativeScale3D`, vsi relativni glede na komponento, na katero je pripet (`AttachParent`), do korena aktorja, ki je v svetu.

- Lastnosti so **unversioned**: shranjene so po položaju v seznamu lastnosti razreda, ne po imenu. Berejo se s shemami v [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) (glejte [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Vrednost, ki je enaka predlogi komponente (njenemu archetype-u v Blueprintu), ni shranjena. Zato se najprej rekurzivno preberejo vrednosti predloge, lastne vrednosti komponente pa jih nadomestijo.
- Komponente z `bVisible = 0` ali `bHiddenInGame = 1` se preskočijo. Enako meshi, katerih pot ustreza `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/` ali `_hlod`.
- Rotacije uporabljajo Unrealov `FRotationMatrix` (pitch, yaw, roll v stopinjah).
- Podvojeni (isti mesh na isti transformaciji, do 0,1 cm) se izpustijo.
- Komponente, ki jih ni mogoče prebrati, se preštejejo po razlogu in prijavijo, na primer `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instancirane komponente** (gozdovi, skoraj vse) se preberejo samo z `--trees`. Ta različica je te razrede preuredila onkraj glav motorja, zato njihove lastnosti niso prebrane. Namesto tega:

- mesh pride iz tabele odvisnosti paketa, kjer vsaka taka komponenta našteje natanko en statični mesh,
- primerki pridejo iz nativnega bloka za lastnostmi (`[1][1][128][count]`, nato `count` matrik 4x4 double),
- komponenta se šteje, da stoji v korenu aktorja, kot ga postavljajo aktorji rastlinja.

Koordinate so Unrealove: centimetri, Z navzgor, X naprej, Y desno, levosučni koordinatni sistem.

## Katera etapa in v katero smer {#which-stage-and-which-way-round}

Koordinatni sistem telemetrije ni dokumentiran, zato se ne predpostavlja. Ugotovi se:

- **Osem možnih koordinatnih sistemov.** Unrealov Z (cm), pomnožen z 0,01, postane višina kroga (y). Unrealov X in Y postaneta x in z kroga, zamenjana ali ne, vsak z enim od predznakov, vse pomnoženo z 0,01 v metre.
- **Mreža višine ceste.** Za vsako etapo se vsaka cestna ploščica postavi na svoji najgrobljši stopnji podrobnosti, za vsako celico 2 m pa se shrani najvišja cestna točka.
- **Ocenjevanje.** Do 400 enakomerno razporejenih točk kroga se prek vsakega koordinatnega sistema pretvori v Unrealov prostor. Točka je na cesti, če je med 3 x 3 celicami okoli nje cestna višina, ki je najbližja točki, med 1 m pod in 3 m nad njo (`ON_ROAD`). Rezultat je delež točk na cesti.
- **Zmagovalec.** Najboljši koordinatni sistem na najboljši etapi, če doseže vsaj 50 %. Sicer se izvoz ustavi: "the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level."
- **Krog, ki navaja svojo progo.** Če ima datoteka kroga polje `track`, se najprej preizkusi, sama, etapa, katere ime se ohlapno ujema z njim (samo črke in številke, ena vsebuje drugo). Sprejme se samo, če doseže vsaj 80 %. Sicer se preizkusijo vse etape.
- Z `--level` se preizkusi samo ta etapa, v vseh osmih smereh.

Konzola na primer izpiše `on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Vse se nato zapiše **v koordinatnem sistemu kroga**: metri, Y navzgor. Vrstni red oglišč trikotnika se obrne tam, kjer transformacija zrcali, da ploskve še vedno kažejo pravo stran.

## Tla {#the-ground}

- Pas je `--margin` metrov na vsako stran kroga v njegovi lastni ravnini x/z.
- Vsaka talna ploščica se postavi na svojo najfinejšo stopnjo podrobnosti, obdržijo pa se samo trikotniki, ki segajo v pas.
- Trikotniki so razvrščeni po vrsti (cesta ali teren) in po kvadratu 512 m v Unrealovem prostoru (51.200 cm), vsak kvadrat s svojo sliko. Deli se imenujejo na primer `ground:road 1_-4`. UV koordinate so `(unreal_xy - square_origin) / 51200`.
- Normale se za celotno datoteko izračunajo iz trikotnikov.

### Talna tekstura {#the-ground-texture}

Razen če je `--no-textures`, se vsak kvadrat pobarva iz dveh virov, pri `--texture-size` pikslih:

1. **Zapečena talna barva.** `RuntimeVirtualTextureComponent` zemljevida etape (njegova škatla je `RelativeLocation` kot vogal in `RelativeScale3D` kot velikost, brez rotacije) kaže na tokovno **virtualno teksturo**, talno barvo, ki jo je igra zapekla. Območje kvadrata se prebere iz nje, s stopnje, katere piksli so najbližji želeni velikosti. To je 13 do 59 cm na piksel, odvisno od etape.
2. **Satelitska slika** zapolni, kar virtualna tekstura pusti črno. Je tekstura `sat*_(b|bc|c|basecolor)` etape v njeni okoljski mapi, prebrana do 4096 px. Njen položaj se najde z metodo najmanjših kvadratov, s katero se prvi kanal UV daljnega terena prilagodi svetovnima x in y. Prilagoditev mora biti linearna do 0,01 pri 95. percentilu, sicer se slika ne uporabi. Če UV koordinate daljnega terena presegajo 1 (material, ki jih ponavlja), se preslikava prepolovi, dokler se enkrat ne prilegajo.

Konzola pove, katero je uporabila, na primer `ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`. Etapa brez obeh se nariše v enobarvnih ploskvah.

## Postavljeni modeli {#placed-models}

Vsaka postavitev, ki ni talna ploščica, se razvrsti po poti do mesha (prvo ujemanje zmaga):

| Kategorija | Ime mesha (ali pot, pri drevesih), ki vsebuje |
|---|---|
| drevesa (samo z `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| skale | `rock`, `cliff`, `boulder`, `stone` |
| robniki | `kerb`, `curb` |
| ovire | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| znaki | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| stavbe | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekviziti | vse drugo |

- Kopija se upošteva, če je njen izvor v pasu dosega (`margin + 60 m`), in se nariše, če se njeni robovi dotikajo pasu.
- Stopnje podrobnosti sledijo [Stopnjam podrobnosti in proračunu](detail-budget.md): pasovi razdalje, nato se najdražji modeli znižajo, da se prilegajo proračunu trikotnikov. Kjer tudi najgrobljše stopnje presegajo proračun, se najbolj oddaljene kopije izpustijo, kot pri BeamNG, dokler se ne prilegajo. Robniki ohranijo polno podrobnost in se nikoli ne izpustijo. Povzetek izpiše `placed on it (N triangles of a B budget)` in, če so kopije odšle, `N copies left out to fit the budget, the furthest from the driving first`.
- Vsaka kategorija je en del v enobarvni ploskvi: `ground:kerbs` za robnike, ki so vozna površina, kot pri Forzi in BeamNG, in `structure:<kategorija>` za ostale:

| Kategorija | Barva (linearni RGB) |
|---|---|
| ovire | 0.55, 0.52, 0.48 |
| znaki | 0.75, 0.72, 0.65 |
| stavbe | 0.62, 0.58, 0.52 |
| infrastruktura | 0.48, 0.48, 0.50 |
| skale | 0.45, 0.43, 0.40 |
| rekviziti | 0.55, 0.45, 0.35 |
| drevesa | 0.20, 0.32, 0.14 |
| robniki | 0.70, 0.25, 0.22 |

Statični meshi, ki jih ni mogoče prebrati (skeletni meshi, meshi samo za Nanite, nivoji, ki niso shranjeni v vrstici), se preštejejo: `N meshes could not be read`.

## Preverjanja, na katerih to stoji {#checks-behind-it}

Kakor je navedeno v izvorni kodi, na nameščeni igri:

- Vsaka tabela vsebine se prebere (različica 8).
- Vsaka celica vsake etape se odpre, vsak statični mesh in vsaka komponenta scene pa se dekodira tako, da se konča natanko na nativnem repu svojega razreda.
- Skoraj vsak vzorčen statični mesh se dekodira (ostali so skeletni). Dekodirana razsežnost cestne ploščice se ujema z njenimi shranjenimi mejami.
- Stopnje satelitske slike so natanko velikosti njenih zbirnih vnosov.
- Vse ploščice vsakega kosa virtualne teksture so obračunane do bajta, cestne ploščice pa pristanejo na cesti, ki jo kaže.

## Znane vrzeli {#known-gaps}

- Lastnosti instanciranih komponent same niso prebrane (glejte zgoraj). Njihova postavitev predpostavlja koren aktorja.
- Gozdovi, ki jih PCG ustvari med izvajanjem, niso shranjeni v datotekah in jih ni mogoče izvoziti.
- Spline meshi (nevidni zidovi za ponovni zagon), dekorativne komponente in lastne teksture postavljenih modelov se ne rišejo. Modeli so enobarvni.
- `--season` nima učinka.
- Popravek igre lahko premakne reže lastnosti. Bralnik sproži napako, namesto da bi napačno bral, izvoz pa pove, koliko komponent je odpovedalo.
