---
title: Assetto Corsa Rally
lang: "no"
source: course-assetto-corsa-rally.md
source_hash: ""
nav_exclude: true
search_exclude: true
---
# Løypeeksport: Assetto Corsa Rally

Assetto Corsa Rally er bygget på Unreal Engine 5 (5.6.1, en modifisert versjon) og
leverer innholdet sitt som IoStore-beholdere. Ingen av dem er kryptert. Eksporten
finner etappen og aksenes retning fra runden. Den skriver etappens egne bakkeflis, delt
i vei og terreng og med tekstur fra etappens innbakte bakkefarge, og plasserer de andre
modellene i flate farger etter kategori.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Kilder: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (installasjon, etapper, plassering),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (eksporten).
Unreal-leserne under den finnes på [Unreal 5 IoStore](reader-unreal-iostore.md),
og dekomprimering på [Oodle](reader-oodle.md).

**Status:** kontrollert på det installerte spillet med runder laget i en tilfeldig ramme
på hver etappe, og den fant riktig etappe og ramme hver gang. Ingen runde spilt inn i
selve spillet har blitt kjørt gjennom den ennå.

## Finne installasjonen

- `--install <folder>`: spillmappen, eller `Content\Paks`, eller en hvilken som helst
  mappe med `.utoc`-filer. Verktøyet sjekker `<folder>`, deretter
  `<folder>\acr\Content\Paks`, og så `<folder>\Content\Paks`.
- Ellers sjekkes hvert Steam-bibliotek sin `steamapps\common\Assetto Corsa Rally` på
  samme måte.
- Hver `.utoc` i den mappen åpnes som én beholder. Beholdere som ikke kan åpnes, hoppes
  over. Hvis ingen åpnes: «no readable IoStore containers in ...».

De fleste blokkene er Oodle-komprimerte, og et bibliotek letes etter på maskinen (alle
Steam-biblioteker søkes). Se [Oodle](reader-oodle.md).

Spillet regnes som AC Rally når rundefilen sier `"game": "assetto-corsa-rally"`
(eller `acrally`), eller når du gir `--game acrally`.

## Hva en etappe er

En etappe er et **World Partition**-kart:

- `Content\Levels\<Stage>.umap` plasserer det fjerne terrenget.
- Kompilerte celler under `Content\Levels\<Stage>\_Generated_\*.umap` plasserer alt annet.

Et nivå regnes som en etappe hvis miljømappen, `Content\Environments\<Stage>\`, har en
mappe `MeshesTrack`. Verktøyet går ikke etter flisenes navn, fordi en etappe kan gi dem
navn etter en by i stedet for kartet. `--level` sammenlignes uten hensyn til store og
små bokstaver mot disse kartnavnene. Et feil navn lister opp etappene som finnes.

Det finnes **ingen landskapsflate**. Bakken er statiske modeller:

| Fliser | Sti | Blir |
|---|---|---|
| banefliser, ca. 175 m, delt i to | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` og `..._Terrain_k` | `ground:road` og `ground:terrain` (en udelt banefli, som en frossen innsjø, er helt vei) |
| fjernt terreng, 2 km-fliser | `.../MeshesTerrain/...` | `ground:terrain` |

## Lese plasseringene

Det som plasserer en modell, er en `StaticMeshComponent`: dens `StaticMesh`, og dens
`RelativeLocation`, `RelativeRotation` og `RelativeScale3D`, hver i forhold til
komponenten den er festet til (`AttachParent`), helt opp til aktørens rot, som ligger i
verden.

- Egenskapene er **uversjonerte**: lagret etter posisjon i klassens egenskapsliste, ikke
  etter navn. De leses med skjemaene i
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (se [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- En verdi som er lik komponentens mal (dens archetype i en Blueprint), lagres ikke. Mal-
  verdiene leses derfor først, rekursivt, og komponentens egne verdier overstyrer dem.
- Komponenter med `bVisible = 0` eller `bHiddenInGame = 1` hoppes over. Det samme gjelder
  modeller der stien inneholder `respawnwall`, `collision`, `blocker`, `invisible`, `/hlod/`
  eller `_hlod`.
- Rotasjoner bruker Unreals `FRotationMatrix` (pitch, yaw, roll i grader).
- Duplikater (samme modell med samme transform, til 0,1 cm) fjernes.
- Komponenter som ikke kan leses, telles etter årsak og rapporteres, for eksempel
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instansierte komponenter** (skog, nesten alt av det) leses bare med `--trees`. Denne
versjonen har flyttet om på disse klassene utover motorens headere, så egenskapene deres
leses ikke. I stedet:

- kommer modellen fra pakkens avhengighetstabell, der hver slik komponent lister nøyaktig
  én statisk modell,
- kommer instansene fra den innfødte blokken etter egenskapene
  (`[1][1][128][count]` og deretter `count` 4x4 double-matriser),
- antas komponenten å stå i aktørens rot, slik skogaktørene plasserer dem.

Koordinatene er Unreals: centimeter, Z opp, X forover, Y til høyre, et venstrehendt
system.

## Hvilken etappe, og hvilken vei rundt

Telemetriens ramme er ikke dokumentert, så den antas ikke. Den tilpasses:

- **Åtte kandidatrammer.** Unreal Z (cm) ganger 0,01 blir rundens høyde (y). Unreal X og Y
  blir rundens x og z, byttet om eller ikke, hver med fortegn i begge retninger, alt skalert
  med 0,01 til meter.
- **Et rutenett for veihøyde.** For hver etappe plasseres hver veiflis (på sitt groveste
  detaljnivå), og det høyeste veihjørnet beholdes per 2 m celle.
- **Poengsetting.** Opptil 400 rundeprøver, jevnt fordelt, føres inn i Unreal-rommet
  gjennom hver ramme. En prøve er på veien når veihøyden nærmest den, blant de 3 x 3
  cellene rundt den, ligger mellom 1 m under og 3 m over prøven (`ON_ROAD`). Poengsummen er
  andelen prøver på veien.
- **Vinneren.** Den beste rammen på den beste etappen, hvis den får minst 50 %. Ellers
  stopper eksporten: «the lap does not lie on any stage's road in any frame (best: ...).
  Name the stage with --level.»
- **En runde som oppgir sin bane.** Hvis rundefilen har et `track`-felt, prøves først en
  etappe der navnet passer omtrent (bare bokstaver og tall, og det ene inneholder det
  andre), alene, og den godtas bare hvis den får minst 80 %. Ellers prøves hver etappe.
- Med `--level` prøves bare den etappen, i alle åtte rammene.

Konsollen sier for eksempel
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Alt skrives deretter **i rundens ramme**: meter, Y opp. En trekants vikling snus der en
transform speiler, slik at flatene fortsatt peker riktig vei.

## Bakken

- Korridoren er `--margin` meter rundt runden i sitt eget x/z-plan.
- Hver bakkeflis plasseres på sitt fineste detaljnivå, og bare trekanter som går inn i
  korridoren beholdes.
- Trekanter grupperes etter slag (vei eller terreng) og etter 512 m kvadrat i Unreal-rommet
  (51 200 cm), og hvert kvadrat får sitt eget bilde. Delene får navn som `ground:road 1_-4`.
  UV-er er `(unreal_xy - square_origin) / 51200`.
- Normaler beregnes fra trekantene for hele filen.

### Bakketeksturen

Med mindre `--no-textures` er gitt, males hvert kvadrat fra to kilder, med `--texture-size`
piksler:

1. **Den innbakte bakkefargen.** Kartets `RuntimeVirtualTextureComponent` (boksen er
   `RelativeLocation` som hjørne og `RelativeScale3D` som størrelse, uten rotasjon) peker på
   en strømmet **virtuell tekstur**, bakkefargen spillet har innbakt. Området for kvadratet
   leses fra den, på nivået hvis piksler ligger nærmest ønsket størrelse. Det er 13 til 59 cm
   per piksel, avhengig av etappen.
2. **Satellittbildet** fyller det den virtuelle teksturen lar stå svart. Det er etappens
   `sat*_(b|bc|c|basecolor)`-tekstur i miljømappen, lest med opptil 4096 px. Plasseringen
   finnes med en minste-kvadrat-tilpasning av det fjerne terrengets første UV-kanal mot
   verdens x og y. Tilpasningen må være lineær til innenfor 0,01 ved 95-persentilen, ellers
   brukes ikke bildet. Går det fjerne terrengets UV-er over 1 (et materiale som gjentar
   dem), halveres kartleggingen til den passer én gang.

Konsollen sier hvilken den brukte, for eksempel
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
En etappe med ingen av dem tegnes i flate farger.

## Plasserte modeller

Hver plassering som ikke er en bakkeflis, klassifiseres etter modellens sti (første treff
vinner):

| Kategori | Modellnavnet (eller stien, for trær) inneholder |
|---|---|
| trær (bare med `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| steiner | `rock`, `cliff`, `boulder`, `stone` |
| kantstein | `kerb`, `curb` |
| barrierer | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| skilt | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| bygninger | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktur | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekvisitter | alt annet |

- En kopi vurderes hvis origo ligger i rekkeviddekorridoren (`margin + 60 m`), og tegnes hvis
  avgrensningen rører korridoren.
- Detaljnivåer følger [Detaljnivåer og budsjett](detail-budget.md): avstandsbånd, og deretter
  trapper de dyreste modellene ned for å passe budsjettet. Der selv de groveste nivåene
  overskrider det, utelates de fjerneste kopiene, som i BeamNG, til det passer. Kantstein
  beholder full detalj og utelates aldri. Oppsummeringen skriver
  `placed on it (N triangles of a B budget)` og, når kopier ble borte, `N copies left out to fit the budget, the furthest from the driving first`.
- Hver kategori er én del i en flat farge: `ground:kerbs` for kantstein, som er kjørbar
  flate, som i Forza og BeamNG, og `structure:<category>` for resten:

| Kategori | Farge (lineær RGB) |
|---|---|
| barrierer | 0,55, 0,52, 0,48 |
| skilt | 0,75, 0,72, 0,65 |
| bygninger | 0,62, 0,58, 0,52 |
| infrastruktur | 0,48, 0,48, 0,50 |
| steiner | 0,45, 0,43, 0,40 |
| rekvisitter | 0,55, 0,45, 0,35 |
| trær | 0,20, 0,32, 0,14 |
| kantstein | 0,70, 0,25, 0,22 |

Statiske modeller som ikke kan leses (skjelettmodeller, modeller som bare finnes som
Nanite, nivåer som ikke er lagret innebygd) telles: `N meshes could not be read`.

## Kontroller bak dette

Slik det står i kildekoden, på det installerte spillet:

- Hver innholdsfortegnelse leses (versjon 8).
- Hver celle i hver etappe åpnes, og hver statisk modell og scenekomponent dekodes og ender
  nøyaktig ved klassens innfødte hale.
- Nesten hver statiske modell i utvalget dekodes (resten er skjelettmodeller). En veiflis'
  dekodede utstrekning stemmer med dens lagrede avgrensning.
- Et satellittbildes mip-nivåer er nøyaktig størrelsene til sine bulk-oppføringer.
- Et virtuelt tekstur-chunks fliser er regnskapsført til byte, og veiflisene havner på veien
  det viser.

## Kjente mangler

- Instansierte komponenters egne egenskaper leses ikke (se over). Plasseringen deres antar
  aktørens rot.
- Skog generert av PCG under kjøring lagres ikke i filene og kan ikke eksporteres.
- Spline-modeller (usynlige respawn-vegger), dekalkomponenter og plasserte modellers egne
  teksturer tegnes ikke. Modellene har flate farger.
- `--season` har ingen effekt.
- En spilloppdatering kan flytte egenskapsplasser. Leseren avviser heller enn å lese feil,
  og løypen rapporterer hvor mange komponenter som feilet.
