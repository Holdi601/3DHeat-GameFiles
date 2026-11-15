---
title: "Assetto Corsa Rally"
nav_order: 3
lang: "bs"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Izvoz staze: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally je izgrađen na Unreal Engineu 5 (5.6.1, izmijenjena verzija)
i svoj sadržaj isporučuje kao IoStore kontejnere. Nijedan nije šifriran. Izvoz iz
vožnje pronalazi etapu i orijentaciju osa. Piše vlastite pločice tla te etape,
podijeljene na cestu i teren i teksturirane iz pečene boje tla te etape, a ostale
modele postavlja u ravnim bojama po kategorijama.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Izvori: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalacija, etape, postavljanje),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (izvoz).
Unreal čitači ispod toga opisani su na stranici [Unreal 5 IoStore](reader-unreal-iostore.md),
a dekompresija na stranici [Oodle](reader-oodle.md).

**Status:** provjereno na instaliranoj igri s krugovima generiranim u nasumičnom
okviru na svakoj etapi, i svaki put je pronašlo ispravnu etapu i okvir. Nijedan
krug snimljen u samoj igri još nije prošao kroz njega.

## Pronalaženje instalacije {#finding-the-install}

- `--install <folder>`: folder igre, ili njegov `Content\Paks`, ili bilo koji
  folder sa `.utoc` datotekama. Alat provjerava `<folder>`, zatim
  `<folder>\acr\Content\Paks`, zatim `<folder>\Content\Paks`.
- Inače se na isti način provjerava `steamapps\common\Assetto Corsa Rally` u
  svakoj Steam biblioteci.
- Svaki `.utoc` u tom folderu otvara se kao jedna pohrana. Kontejneri koji se ne
  otvore preskaču se. Ako se nijedan ne otvori: "no readable IoStore containers in ...".

Većina blokova je komprimirana Oodleom, a biblioteka se traži na računaru
(pretražuje se svaka Steam biblioteka). Pogledajte [Oodle](reader-oodle.md).

Igra se smatra AC Rally kad datoteka kruga kaže `"game": "assetto-corsa-rally"`
(ili `acrally`), ili kad predate `--game acrally`.

## Šta je etapa {#what-a-stage-is}

Etapa je mapa tipa **World Partition**:

- `Content\Levels\<Stage>.umap` postavlja daleki teren.
- Pečene ćelije pod `Content\Levels\<Stage>\_Generated_\*.umap` postavljaju sve ostalo.

Nivo se računa kao etapa ako njegov folder okoline,
`Content\Environments\<Stage>\`, ima folder `MeshesTrack`. Alat ne ide po
imenima pločica, jer etapa može pločice nazvati po gradu, a ne po svojoj mapi.
`--level` se poredi bez obzira na velika i mala slova s ovim imenima mapa. Pogrešno
ime ispisuje etape koje postoje.

**Nema terena kao landscapea.** Tlo su statičke mreže:

| Pločice | Putanja | Postaju |
|---|---|---|
| pločice staze, oko 175 m, podijeljene na dva dijela | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` i `..._Terrain_k` | `ground:road` i `ground:terrain` (nepodijeljena pločica staze, kao zaleđeno jezero, sva je cesta) |
| daleki teren, pločice od 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Čitanje postavljanja {#reading-the-placements}

Mrežu postavlja `StaticMeshComponent`: njegov `StaticMesh` te `RelativeLocation`,
`RelativeRotation` i `RelativeScale3D`, svaki relativan prema komponenti na koju
je zakačen (`AttachParent`), sve do korijena aktora, koji je u svijetu.

- Svojstva su **neverzionirana**: pohranjena po poziciji u listi svojstava klase,
  a ne po imenu. Čitaju se pomoću shema u
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (pogledajte [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Vrijednost jednaka predlošku komponente (njenom arhetipu u Blueprintu) nije
  pohranjena, pa se vrijednosti predloška čitaju prve, rekurzivno, a vlastite
  vrijednosti komponente ih nadjačavaju.
- Komponente s `bVisible = 0` ili `bHiddenInGame = 1` preskaču se. Preskaču se i
  mreže čija putanja sadrži `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/`
  ili `_hlod`.
- Rotacije koriste Unrealov `FRotationMatrix` (pitch, yaw, roll u stepenima).
- Duplikati (ista mreža s istom transformacijom, na 0,1 cm) odbacuju se.
- Komponente koje se ne mogu pročitati broje se po razlogu i prijavljuju, na
  primjer `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instancirane komponente** (šume, gotovo sve) čitaju se samo s `--trees`. Ova
verzija je preuredila te klase izvan zaglavlja engina, pa se njihova svojstva ne
čitaju. Umjesto toga:

- mreža dolazi iz tablice zavisnosti paketa, gdje svaka takva komponenta navodi
  tačno jednu statičku mrežu,
- instance dolaze iz nativnog bloka nakon svojstava
  (`[1][1][128][count]`, zatim `count` matrica 4x4 tipa double),
- smatra se da komponenta sjedi u korijenu svog aktora, što je način na koji ih
  aktori raslinja postavljaju.

Koordinate su Unrealove: centimetri, Z gore, X naprijed, Y desno, lijevi
(left-handed) okvir.

## Koja etapa i na koju stranu {#which-stage-and-which-way-round}

Okvir telemetrije nije dokumentiran, pa se ne pretpostavlja. On se pronalazi
fitovanjem:

- **Osam kandidatskih okvira.** Unreal Z (cm) puta 0,01 postaje visina kruga (y).
  Unreal X i Y postaju x i z kruga, zamijenjeni ili ne, svaki s bilo kojim
  predznakom, sve skalirano s 0,01 na metre.
- **Mreža visine ceste.** Za svaku etapu postavlja se svaka pločica ceste (na
  njenom najgrubljem nivou detalja) i čuva se najviši vrh ceste po ćeliji od 2 m.
- **Bodovanje.** Do 400 uzoraka kruga, ravnomjerno raspoređenih, prevodi se u
  Unreal prostor kroz svaki okvir. Uzorak je na cesti kad je, među 3 x 3 ćelije
  oko njega, visina ceste najbliža njemu između 1 m ispod i 3 m iznad uzorka
  (`ON_ROAD`). Rezultat je udio uzoraka na cesti.
- **Pobjednik.** Najbolji okvir na najboljoj etapi, ako postigne barem 50%. Inače
  se izvoz zaustavlja: "the lap does not lie on any stage's road in any
  frame (best: ...). Name the stage with --level."
- **Krug koji imenuje svoju stazu.** Ako datoteka kruga ima polje `track`, etapa
  čije se ime okvirno podudara s njim (samo slova i cifre, jedno sadrži drugo)
  isprobava se prva, sama, i prihvata se samo ako postigne barem 80%. Inače se
  isprobava svaka etapa.
- S `--level` isprobava se samo ta etapa, u svih osam okvira.

Konzola kaže, na primjer,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Sve se zatim piše **u okviru kruga**: metri, Y gore. Namotavanje trougla
(winding) se obrće gdje god transformacija zrcali, pa lica i dalje gledaju na
pravu stranu.

## Tlo {#the-ground}

- Koridor je `--margin` metara oko kruga u njegovoj vlastitoj x/z ravni.
- Svaka pločica tla postavlja se na svom najfinijem nivou detalja, a zadržavaju
  se samo trouglovi koji sežu u koridor.
- Trouglovi se grupišu po vrsti (cesta ili teren) i po kvadratu od 512 m u
  Unreal prostoru (51.200 cm), svaki kvadrat sa svojom slikom. Dijelovi se zovu
  poput `ground:road 1_-4`. UV-ovi su `(unreal_xy - square_origin) / 51200`.
- Normale se računaju iz trouglova za cijelu datoteku.

### Tekstura tla {#the-ground-texture}

Osim s `--no-textures`, svaki kvadrat se boji iz dva izvora, na
`--texture-size` piksela:

1. **Pečena boja tla.** `RuntimeVirtualTextureComponent` mape etape (njegova
   kutija ima `RelativeLocation` kao ugao i `RelativeScale3D` kao veličinu, bez
   rotacije) pokazuje na streaming **virtualnu teksturu**, boju tla koju je igra
   ispekla. Područje kvadrata čita se iz nje, na nivou čiji su pikseli najbliži
   željenoj veličini. To je 13 do 59 cm po pikselu, ovisno o etapi.
2. **Satelitska slika** popunjava ono što virtualna tekstura ostavi crnim. To je
   tekstura etape `sat*_(b|bc|c|basecolor)` u njenom folderu okoline, čitana do
   4096 px. Njeno postavljanje pronalazi se fitom najmanjih kvadrata prvog UV
   kanala dalekog terena naspram svjetskih x i y. Fit mora biti linearan unutar
   0,01 na 95. percentilu, inače se slika ne koristi. Ako UV-ovi dalekog terena
   prelaze 1 (materijal koji ih ponavlja), mapiranje se prepolovljuje dok se ne
   uklopi jednom.

Konzola kaže šta je korišteno, na primjer
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Etapa bez ijednog od njih crta se u ravnim bojama.

## Postavljeni modeli {#placed-models}

Svako postavljanje koje nije pločica tla razvrstava se po putanji njegove mreže
(vrijedi prvo podudaranje):

| Kategorija | Ime mreže (ili putanja, za drveće) sadrži |
|---|---|
| drveće (samo s `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| stijene | `rock`, `cliff`, `boulder`, `stone` |
| ivičnjaci (kerbs) | `kerb`, `curb` |
| ograde | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| znakovi | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| zgrade | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekviziti (props) | sve ostalo |

- Kopija se razmatra ako je njeno ishodište u koridoru dosega (`margin + 60 m`),
  a crta se ako njene granice dodiruju koridor.
- Nivoi detalja slijede [Nivoi detalja i budžet](detail-budget.md): pojasevi
  udaljenosti, zatim najskuplji modeli silaze nivo niže da stanu u budžet. Gdje i
  najgrubljim nivoima budžet bude prekoračen, najudaljenije kopije se izostavljaju,
  kao u BeamNG-u, dok ne stane. Ivičnjaci zadržavaju puni detalj i nikad se ne
  izostavljaju. Sažetak ispisuje `placed on it (N triangles of a B budget)` i, kad
  su kopije otpale, `N copies left out to fit the budget, the furthest from the driving first`.
- Svaka kategorija je jedan dio u ravnoj boji: `ground:kerbs` za ivičnjake, koji
  su površina za vožnju, kao u Forzi i BeamNG-u, i `structure:<category>` za
  ostale:

| Kategorija | Boja (linearni RGB) |
|---|---|
| ograde | 0.55, 0.52, 0.48 |
| znakovi | 0.75, 0.72, 0.65 |
| zgrade | 0.62, 0.58, 0.52 |
| infrastruktura | 0.48, 0.48, 0.50 |
| stijene | 0.45, 0.43, 0.40 |
| rekviziti | 0.55, 0.45, 0.35 |
| drveće | 0.20, 0.32, 0.14 |
| ivičnjaci | 0.70, 0.25, 0.22 |

Statičke mreže koje se ne mogu pročitati (skeletalne mreže, mreže samo za Nanite,
nivoi koji nisu pohranjeni ugrađeno) se broje: `N meshes could not be read`.

## Provjere iza toga {#checks-behind-it}

Kako navodi izvor, na instaliranoj igri:

- Svaka tablica sadržaja se čita (verzija 8).
- Svaka ćelija svake etape se otvara, a svaka komponenta statičke mreže i scene
  dekodira se završavajući tačno na nativnom repu svoje klase.
- Gotovo svaka uzorkovana statička mreža se dekodira (ostale su skeletalne).
  Dekodirani opseg pločice ceste podudara se s njenim pohranjenim granicama.
- Mip nivoi satelitske slike tačno su veličine svojih bulk unosa.
- Pločice chunka virtualne teksture obračunate su do bajta, a pločice ceste
  slijeću na cestu koju ona prikazuje.

## Poznate praznine {#known-gaps}

- Vlastita svojstva instanciranih komponenti se ne čitaju (pogledajte gore).
  Njihovo postavljanje pretpostavlja korijen aktora.
- Šume koje PCG generira u toku izvođenja nisu pohranjene u datotekama i ne mogu
  se izvesti.
- Spline mreže (nevidljivi zidovi za respawn), komponente decala i vlastite
  teksture postavljenih modela se ne crtaju. Modeli su u ravnim bojama.
- `--season` nema učinka.
- Zakrpa igre može pomjeriti slotove svojstava. Čitač izaziva grešku umjesto da
  pogrešno čita, a `course` prijavljuje koliko komponenti nije uspjelo.
