---
title: Assetto Corsa Rally
lang: "sv"
source: course-assetto-corsa-rally.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Banexport: Assetto Corsa Rally

Assetto Corsa Rally är byggt på Unreal Engine 5 (5.6.1, en modifierad version)
och levererar sitt innehåll som IoStore-behållare. Ingen av dem är krypterad.
Exporten hittar etappen och axlarnas riktning utifrån varvet. Den skriver etappens
egna markrutor, delade i väg och terräng och med en textur från etappens inbakade
markfärg, och placerar de övriga modellerna i platta färger efter kategori.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <etappens kartnamn>
python -m heat3d_gamefiles course rally_lap.json --level x      # ett fel namn listar etapperna
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Källkod: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (installation, etapper, placering),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (exporten).
Unreal-läsarna under detta finns på [Unreal 5 IoStore](reader-unreal-iostore.md),
och dekomprimeringen på [Oodle](reader-oodle.md).

**Status:** kontrollerad på det installerade spelet med varv som skapats i en slumpvald
bildruta på varje etapp. Den hittade rätt etapp och bildruta varje gång. Inget
varv som spelats in i spelet själv har körts igenom den ännu.

## Hitta installationen

- `--install <mapp>`: spelmappen, eller dess `Content\Paks`, eller valfri mapp
  med `.utoc`-filer. Verktyget kollar `<mapp>`, sedan
  `<mapp>\acr\Content\Paks`, sedan `<mapp>\Content\Paks`.
- Annars kontrolleras varje Steam-biblioteks `steamapps\common\Assetto Corsa Rally`
  på samma sätt.
- Varje `.utoc` i mappen öppnas som en behållare. Behållare som inte går att
  öppna hoppas över. Om ingen öppnas: "no readable IoStore containers in ...".

De flesta block är Oodle-komprimerade, och ett bibliotek letas efter på datorn
(alla Steam-bibliotek söks). Se [Oodle](reader-oodle.md).

Spelet räknas som AC Rally när varvfilen säger `"game": "assetto-corsa-rally"`
(eller `acrally`), eller när du anger `--game acrally`.

## Vad en etapp är

En etapp är en **World Partition**-karta:

- `Content\Levels\<Etapp>.umap` placerar den avlägsna terrängen.
- Cachade celler under `Content\Levels\<Etapp>\_Generated_\*.umap` placerar allt annat.

En nivå räknas som etapp om dess miljömapp, `Content\Environments\<Etapp>\`, har en
mapp `MeshesTrack`. Verktyget går inte på rutornas namn, eftersom en etapp kan
ha döpt dem efter en stad i stället för efter sin karta. `--level` jämförs utan
hänsyn till stora och små bokstäver mot kartnamnen. Ett fel namn listar de etapper som finns.

Det finns **ingen landskapsyta**. Marken är statiska meshar:

| Rutor | Sökväg | Blir |
|---|---|---|
| banrutor, cirka 175 m, delade i två | `.../MeshesTrack/SM_<Etapp>TrackNNNN_Road_k` och `..._Terrain_k` | `ground:road` och `ground:terrain` (en odelad banruta, till exempel en frusen sjö, är helt väg) |
| fjärrterräng, 2 km-rutor | `.../MeshesTerrain/...` | `ground:terrain` |

## Läsa placeringarna

Det som placerar en mesh är en `StaticMeshComponent`: dess `StaticMesh`, och dess
`RelativeLocation`, `RelativeRotation` och `RelativeScale3D`. Var och en är relativ
till komponenten den är fäst vid (`AttachParent`), upp till aktörens rot, som ligger i världen.

- Egenskaperna är **oversionerade**: lagrade efter position i klassens egenskapslista,
  inte efter namn. De läses med schemana i
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (se [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Ett värde som är lika med komponentens mall (dess arketyp i en Blueprint) lagras
  inte. Mallens värden läses därför först, rekursivt, och komponentens egna värden
  skriver över dem.
- Komponenter med `bVisible = 0` eller `bHiddenInGame = 1` hoppas över. Det gör även
  meshar vars sökväg matchar `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/`
  eller `_hlod`.
- Rotationer använder Unreals `FRotationMatrix` (pitch, yaw, roll i grader).
- Dubletter (samma mesh med samma transform, till 0,1 cm) tas bort.
- Komponenter som inte kan läsas räknas per orsak och redovisas, till exempel
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instansierade komponenter** (skogar, nästan alla) läses bara med `--trees`. Den här
versionen har flyttat om de klasserna så att de inte längre motsvarar motorns headers,
så deras egenskaper läses inte. I stället:

- kommer meshen från paketets beroendetabell, där varje sådan komponent anger
  exakt en statisk mesh,
- kommer instanserna från det inbyggda blocket efter egenskaperna
  (`[1][1][128][count]` följt av `count` st 4x4 dubbla matriser),
- antas komponenten sitta i sin aktörs rot, så som vegetationsaktörerna placerar dem.

Koordinaterna är Unreals: centimeter, Z uppåt, X framåt, Y åt höger, ett
vänsterhänt koordinatsystem.

## Vilken etapp, och vilket håll

Telemetrins koordinatsystem är inte dokumenterat, så det antas inte. Det anpassas i stället:

- **Åtta kandidatriktningar.** Unreals Z (cm) gånger 0,01 blir varvets höjd (y).
  Unreals X och Y blir varvets x och z, bytta eller inte, var och en med valfritt
  tecken, allt skalat med 0,01 till meter.
- **Ett rutnät för vägens höjd.** För varje etapp placeras varje vägruta (i sin grövsta
  detaljnivå), och den högsta vägpunkten behålls per 2 m-cell.
- **Poängsättning.** Upp till 400 varvpunkter, jämnt fördelade, förs in i Unreal-rymden
  via varje riktning. En punkt är på vägen när den, bland de 3 x 3 cellerna runt
  den, har en vägyta närmast sig som ligger mellan 1 m under och 3 m över punkten
  (`ON_ROAD`). Poängen är andelen punkter på vägen.
- **Vinnare.** Den bästa riktningen på den bästa etappen, om den får minst 50 %.
  Annars stannar exporten: "the lap does not lie on any stage's road in any frame
  (best: ...). Name the stage with --level."
- **Ett varv som anger sin bana.** Om varvfilen har fältet `track` prövas först en
  etapp vars namn ungefär stämmer (bara bokstäver och siffror, och det ena innehåller
  det andra). Den testas ensam och godtas bara om den får minst 80 %. Annars prövas
  alla etapper.
- Med `--level` prövas bara den etappen, i alla åtta riktningar.

Konsolen skriver till exempel
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Allt skrivs sedan **i varvets koordinatsystem**: meter, Y uppåt. En triangels
vindning vänds där en transform speglar, så att ytorna fortfarande pekar rätt.

## Marken

- Korridoren är `--margin` meter runt varvet i dess egna x/z-plan.
- Varje markruta placeras i sin finaste detaljnivå, och bara de triangar som når in
  i korridoren behålls.
- Triangarna grupperas efter sort (väg eller terräng) och efter 512 m-kvadrat i
  Unreal-rymden (51 200 cm), där varje kvadrat får en egen bild. Delarna heter till
  exempel `ground:road 1_-4`. UV är `(unreal_xy - square_origin) / 51200`.
- Normaler beräknas från triangarna för hela filen.

### Markens textur

Om `--no-textures` inte anges målas varje kvadrat från två källor, med
`--texture-size` pixlar:

1. **Den inbakade markfärgen.** Kartans `RuntimeVirtualTextureComponent` (dess låda
   är `RelativeLocation` som hörn och `RelativeScale3D` som storlek, utan rotation)
   pekar på en strömmad **virtuell textur**, den markfärg spelet bakat in. Kvadratens
   område läses från den, på den nivå vars pixlar ligger närmast önskad storlek. Det
   är 13 till 59 cm per pixel, beroende på etappen.
2. **Satellitbilden** fyller det som den virtuella texturen lämnar svart. Den är
   etappens textur `sat*_(b|bc|c|basecolor)` i dess miljömapp, läst upp till 4096 px.
   Placeringen hittas med en minsta-kvadrat-anpassning av fjärrterrängens första
   UV-kanal mot världens x och y. Anpassningen måste vara linjär till inom 0,01 vid
   95-percentilen, annars används inte bilden. Om fjärrterrängens UV går över 1
   (ett material som upprepar dem) halveras avbildningen tills de passar en gång.

Konsolen säger vilken källa som användes, till exempel
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
En etapp utan någondera ritas i platta färger.

## Placerade modeller

Varje placering som inte är en markruta klassas efter sin meshsökväg (först träffen gäller):

| Kategori | Meshnamnet (eller sökvägen, för träd) innehåller |
|---|---|
| träd (bara med `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| stenar | `rock`, `cliff`, `boulder`, `stone` |
| kantstenar | `kerb`, `curb` |
| barriärer | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| skyltar | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| byggnader | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktur | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekvisita | allt annat |

- En kopia tas med om dess origo ligger i reach-korridoren (`margin + 60 m`) och ritas
  om dess yta når in i korridoren.
- Detaljnivåer följer [Detaljnivåer och budgeten](detail-budget.md): avstånds-band,
  sedan får de dyraste modellerna sänkas för att få plats i budgeten. Där även de
  grövsta nivåerna överskrider budgeten utelämnas de mest avlägsna kopiorna, precis
  som i BeamNG, tills det passar. Kantstenar behåller full detalj och utelämnas aldrig.
  Sammanfattningen skriver `placed on it (N triangles of a B budget)` och, om kopior
  togs bort, `N copies left out to fit the budget, the furthest from the driving first`.
- Varje kategori är en del i en platt färg: `ground:kerbs` för kantstenar, som är
  körbar yta, som i Forza och BeamNG, och `structure:<kategori>` för resten:

| Kategori | Färg (linjär RGB) |
|---|---|
| barriärer | 0,55, 0,52, 0,48 |
| skyltar | 0,75, 0,72, 0,65 |
| byggnader | 0,62, 0,58, 0,52 |
| infrastruktur | 0,48, 0,48, 0,50 |
| stenar | 0,45, 0,43, 0,40 |
| rekvisita | 0,55, 0,45, 0,35 |
| träd | 0,20, 0,32, 0,14 |
| kantstenar | 0,70, 0,25, 0,22 |

Statiska meshar som inte kan läsas (skelettmeshar, meshar som bara finns i Nanite,
nivåer som inte lagrats inline) räknas: `N meshes could not be read`.

## Kontroller bakom det

Enligt källkoden, på det installerade spelet:

- Varje innehållsförteckning läses (version 8).
- Varje cell i varje etapp öppnas, och varje statisk mesh- och scenkomponent avkodas
  och slutar exakt vid sin klass inbyggda svans.
- Nästan varje samplad statisk mesh avkodas (resten är skelett). En vägruta utsträckning
  stämmer med dess lagrade omslutningsruta.
- En satellitbilds mip-nivåer har exakt samma storlekar som deras bulkposter.
- En virtuell texturs chunk har alla sina rutor redovisade till byten, och vägrutorna
  landar på vägen den visar.

## Kända brister

- Instansierade komponenters egna egenskaper läses inte (se ovan). Deras placering
  antar aktörens rot.
- Skogar som PCG genererar vid körning lagras inte i filerna och kan inte exporteras.
- Spline-meshar (osynliga respawn-väggar), dekalkomponenter och placerade modellers
  egna texturer ritas inte. Modeller har platta färger.
- `--season` har ingen effekt.
- En spelpatch kan flytta egenskapsplatser. Läsaren avbryter hellre än läser fel, och
  banan redovisar hur många komponenter som misslyckades.
