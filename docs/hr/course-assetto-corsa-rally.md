---
title: Assetto Corsa Rally
nav_order: 3
lang: "hr"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Izvoz staze: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally izrađena je na Unreal Engineu 5 (5.6.1, izmijenjena verzija)
i sadržaj isporučuje kao IoStore spremnike. Nijedan nije šifriran. Izvoz iz kruga
pronalazi etapu i orijentaciju osi. Zapisuje vlastite pločice tla etape, podijeljene
na cestu i teren, s teksturom iz pečene boje tla etape, a ostale modele postavlja
u jednolikim bojama po kategoriji.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <ime karte etape>
python -m heat3d_gamefiles course rally_lap.json --level x      # krivo ime ispisuje etape
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Izvori: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalacija, etape, postavljanje),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (izvoz).
Unreal čitači ispod toga opisani su na [Unreal 5 IoStore](reader-unreal-iostore.md),
a dekompresija na [Oodle](reader-oodle.md).

**Stanje:** provjereno na instaliranoj igri s krugovima generiranima u nasumičnom
okviru na svakoj etapi, i izvoz je svaki put našao pravu etapu i okvir. Nijedan
krug zabilježen u samoj igri još nije prošao kroz izvoz.

## Pronalaženje instalacije {#finding-the-install}

- `--install <mapa>`: mapa igre, ili njezin `Content\Paks`, ili bilo koja mapa s
  datotekama `.utoc`. Alat provjerava `<mapa>`, zatim `<mapa>\acr\Content\Paks`,
  zatim `<mapa>\Content\Paks`.
- Inače se u svakoj Steam biblioteci provjerava `steamapps\common\Assetto Corsa Rally`
  na isti način.
- Svaka `.utoc` datoteka u toj mapi otvara se kao jedan spremnik. Spremnici koji se
  ne mogu otvoriti preskaču se. Ako se nijedan ne otvori, ispisuje se:
  `no readable IoStore containers in ...`.

Većina blokova komprimirana je Oodleom, a biblioteka se traži na računalu (pretražuje
se svaka Steam biblioteka). Vidi [Oodle](reader-oodle.md).

Igra se prepoznaje kao AC Rally kad datoteka kruga kaže `"game": "assetto-corsa-rally"`
(ili `acrally`), ili kad predate `--game acrally`.

## Što je etapa {#what-a-stage-is}

Etapa je **World Partition** karta:

- `Content\Levels\<Etapa>.umap` postavlja daleki teren.
- Pečene ćelije pod `Content\Levels\<Etapa>\_Generated_\*.umap` postavljaju sve ostalo.

Razina se smatra etapom ako njezina mapa okoline, `Content\Environments\<Etapa>\`,
ima mapu `MeshesTrack`. Alat se ne oslanja na imena pločica, jer etapa može pločice
nazvati prema gradu, a ne prema svojoj karti. `--level` se uspoređuje bez obzira na
velika i mala slova s tim imenima karata. Krivo ime ispisuje etape koje postoje.

Nema **landscapea** (Unreal terena kao jednog objekta). Tlo čine statičke mreže:

| Pločice | Putanja | Postaju |
|---|---|---|
| pločice staze, oko 175 m, podijeljene na dva dijela | `.../MeshesTrack/SM_<Etapa>TrackNNNN_Road_k` i `..._Terrain_k` | `ground:road` i `ground:terrain` (pločica staze koja nije podijeljena, na primjer smrznuto jezero, sva je cesta) |
| daleki teren, pločice od 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Čitanje postavljanja {#reading-the-placements}

Što postavlja mrežu jest `StaticMeshComponent`: njegov `StaticMesh` te njegovi
`RelativeLocation`, `RelativeRotation` i `RelativeScale3D`, svaki relativan prema
komponenti za koju je vezan (`AttachParent`), sve do korijena aktera, koji je u svijetu.

- Svojstva su **neverzionirana**: spremljena prema položaju na popisu svojstava
  klase, a ne prema imenu. Čitaju se pomoću shema u
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (vidi [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Vrijednost jednaka predlošku komponente (njezinom archetypeu u Blueprintu) nije
  spremljena, pa se prvo rekurzivno čitaju vrijednosti predloška, a vlastite
  vrijednosti komponente ih nadjačavaju.
- Komponente s `bVisible = 0` ili `bHiddenInGame = 1` preskaču se. Preskaču se i
  mreže čija putanja odgovara `respawnwall`, `collision`, `blocker`, `invisible`,
  `/hlod/` ili `_hlod`.
- Rotacije koriste Unrealov `FRotationMatrix` (pitch, yaw, roll u stupnjevima).
- Duplikati (ista mreža na istoj transformaciji, do 0,1 cm) se odbacuju.
- Komponente koje se ne mogu pročitati broje se po razlogu i prijavljuju, na primjer
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instancirane komponente** (šume, gotovo sve) čitaju se samo uz `--trees`. Ova
verzija igre preuredila je te klase izvan engineovih zaglavlja, pa se njihova
svojstva ne čitaju. Umjesto toga:

- mreža dolazi iz tablice ovisnosti paketa, gdje svaka takva komponenta navodi
  točno jednu statičku mrežu,
- instance dolaze iz nativnog bloka iza svojstava (`[1][1][128][count]`, pa `count`
  4x4 double matrica),
- komponenta se smatra smještenom u korijenu svog aktera, kako to rade akteri
  vegetacije.

Koordinate su Unrealove: centimetri, Z gore, X naprijed, Y desno, lijevo orijentirani
koordinatni sustav.

## Koja etapa i koji smjer {#which-stage-and-which-way-round}

Okvir telemetrije nije dokumentiran, pa se ne pretpostavlja. Procjenjuje se:

- **Osam kandidatskih okvira.** Unreal Z (cm) puta 0,01 postaje visina kruga (y).
  Unreal X i Y postaju x i z kruga, zamijenjeni ili ne, svaki s jednim od predznaka,
  sve skalirano s 0,01 u metre.
- **Mreža visina ceste.** Za svaku etapu postavlja se svaka pločica ceste (na
  najgrubljoj razini detalja) i zadržava se najviši vrh ceste po ćeliji od 2 m.
- **Bodovanje.** Do 400 uzoraka kruga, ravnomjerno raspoređenih, prevodi se u
  Unreal prostor kroz svaki okvir. Uzorak je na cesti kad, među 3 x 3 ćelije oko
  njega, visina ceste najbliža njemu leži između 1 m ispod i 3 m iznad uzorka
  (`ON_ROAD`). Rezultat je udio uzoraka na cesti.
- **Pobjednik.** Najbolji okvir na najboljoj etapi, ako postiže najmanje 50%. Inače
  izvoz staje: "the lap does not lie on any stage's road in any frame (best: ...).
  Name the stage with --level." (Krug ne leži ni na jednoj cesti ni u jednom okviru
  (najbolje: ...). Imenujte etapu s `--level`.)
- **Krug koji imenuje svoju stazu.** Ako datoteka kruga ima polje `track`, etapa
  čije ime labavo odgovara (samo slova i brojevi, jedno sadrži drugo) isprobava se
  prva, sama, i prihvaća se samo ako postiže najmanje 80%. Inače se isprobava svaka
  etapa.
- S `--level` isprobava se samo ta etapa, u svih osam okvira.

Konzola ispisuje, na primjer,
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Sve se zatim zapisuje **u okviru kruga**: metri, Y gore. Trokutu se obrće redoslijed
vrhova gdje god transformacija zrcali, pa lica i dalje gledaju pravo.

## Tlo {#the-ground}

- Koridor je `--margin` metara oko kruga u njegovoj vlastitoj ravnini x/z.
- Svaka pločica tla postavlja se na svoju najfiniju razinu detalja, i zadržavaju se
  samo trokuti koji sežu u koridor.
- Trokuti se grupiraju po vrsti (cesta ili teren) i po kvadratu od 512 m u Unreal
  prostoru (51 200 cm), a svaki kvadrat ima vlastitu sliku. Dijelovi se zovu, na
  primjer, `ground:road 1_-4`. UV-koordinate su `(unreal_xy - square_origin) / 51200`.
- Normale se računaju iz trokuta za cijelu datoteku.

### Tekstura tla {#the-ground-texture}

Osim ako nije `--no-textures`, svaki kvadrat boji se iz dva izvora, na
`--texture-size` piksela:

1. **Pečena boja tla.** `RuntimeVirtualTextureComponent` karte etape (njegov okvir je
   `RelativeLocation` kao kut i `RelativeScale3D` kao veličina, bez rotacije) pokazuje
   na streaming **virtualnu teksturu**, boju tla koju je igra zapekla. Područje kvadrata
   čita se iz nje, na razini čiji su pikseli najbliži traženoj veličini. To je od 13 do
   59 cm po pikselu, ovisno o etapi.
2. **Satelitska slika** popunjava ono što virtualna tekstura ostavi crnim. To je
   tekstura `sat*_(b|bc|c|basecolor)` u mapi okoline etape, čitana do 4096 px.
   Njezin položaj nalazi se metodom najmanjih kvadrata, prema prvom UV kanalu dalekog
   terena i x i y koordinatama svijeta. Prilagodba mora biti linearna do 0,01 na 95.
   percentilu, inače se slika ne koristi. Ako UV-koordinate dalekog terena prelaze 1
   (materijal ih ponavlja), preslikavanje se prepolovi dok ne stane jednom.

Konzola kaže koju je koristila, na primjer
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Etapa bez nijedne od njih crta se u jednolikim bojama.

## Postavljeni modeli {#placed-models}

Svako postavljanje koje nije pločica tla razvrstava se po putanji mreže (prvo
podudaranje vrijedi):

| Kategorija | Ime mreže (ili putanja, za drveće) sadrži |
|---|---|
| drveće (samo uz `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| stijene | `rock`, `cliff`, `boulder`, `stone` |
| rubnici | `kerb`, `curb` |
| ograde | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| znakovi | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| zgrade | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekviziti | sve ostalo |

- Primjerak se razmatra ako mu je ishodište u koridoru dosega (`margin + 60 m`), a
  crta se ako mu se granice dotiču koridora.
- Razine detalja slijede [Razine detalja i proračun](detail-budget.md): pojasevi
  udaljenosti, pa se najskuplji modeli spuštaju da stanu u proračun. Gdje ni najgrublje
  razine ne prelaze proračun, najudaljeniji primjerci se izostavljaju, kao kod BeamNG-a,
  dok ne stane. Rubnici zadržavaju punu razinu detalja i nikad se ne izostavljaju.
  Sažetak ispisuje `placed on it (N triangles of a B budget)` i, kad su neki primjerci
  izostavljeni, `N copies left out to fit the budget, the furthest from the driving first`.
- Svaka kategorija je jedan dio u jednolikoj boji: `ground:kerbs` za rubnike, koji su
  vozna površina, kao kod Forze i BeamNG-a, a `structure:<kategorija>` za ostalo:

| Kategorija | Boja (linearni RGB) |
|---|---|
| ograde | 0,55, 0,52, 0,48 |
| znakovi | 0,75, 0,72, 0,65 |
| zgrade | 0,62, 0,58, 0,52 |
| infrastruktura | 0,48, 0,48, 0,50 |
| stijene | 0,45, 0,43, 0,40 |
| rekviziti | 0,55, 0,45, 0,35 |
| drveće | 0,20, 0,32, 0,14 |
| rubnici | 0,70, 0,25, 0,22 |

Statičke mreže koje se ne mogu pročitati (skeletne mreže, mreže samo za Nanite,
razine koje nisu spremljene unutra) broje se: `N meshes could not be read`.

## Što je provjereno {#checks-behind-it}

Prema izvornom kodu, na instaliranoj igri:

- Svaka tablica sadržaja čita se (verzija 8).
- Svaka ćelija svake etape se otvara, i svaka statička mreža i komponenta scene
  dekodira se tako da završi točno na nativnom repu svoje klase.
- Gotovo svaka uzorkovana statička mreža se dekodira (ostale su skeletne). Dekodirani
  obuhvat pločice ceste odgovara njezinim spremljenim granicama.
- Mip razine satelitske slike točno su veličine svojih bulk unosa.
- Pločice jednog dijela virtualne teksture obračunate su do bajta, a pločice ceste
  padaju na cestu koju ona prikazuje.

## Poznati nedostaci {#known-gaps}

- Svojstva instanciranih komponenti sama se ne čitaju (vidi gore). Njihovo postavljanje
  pretpostavlja korijen aktera.
- Šume koje PCG generira u vrijeme rada nisu spremljene u datotekama i ne mogu se
  izvesti.
- Spline mreže (nevidljivi zidovi za respawn), decal komponente i vlastite teksture
  postavljenih modela se ne crtaju. Modeli su u jednolikim bojama.
- `--season` nema učinka.
- Zakrpa igre može pomaknuti mjesta svojstava. Čitač prijavljuje grešku umjesto da
  pogrešno čita, a izvoz kaže koliko je komponenti otkazalo.
