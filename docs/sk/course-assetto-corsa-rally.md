---
title: Assetto Corsa Rally
nav_order: 3
lang: "sk"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Export trate: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally je postavená na Unreal Engine 5 (5.6.1, upravená verzia)
a obsah posiela v kontajneroch IoStore. Žiadny z nich nie je šifrovaný. Export
nájde etapu a orientáciu osí z kola. Zapíše vlastné dlaždice terénu etapy, rozdelené
na cestu a terén a potiahnuté texturou z pečenej farby povrchu etapy, a ostatné
modely umiestni v plošných farbách podľa kategórie.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Zdroje: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (inštalácia, etapy, umiestnenie),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (export).
Čítačky Unreal pod ním sú opísané na stránke [Unreal 5 IoStore](reader-unreal-iostore.md),
dekompresia na stránke [Oodle](reader-oodle.md).

**Stav:** overené na nainštalovanej hre s kolami vygenerovanými v náhodnom
snímku na každej etape; vždy našiel správnu etapu a snímok. Zatiaľ žiadne kolo
zaznamenané priamo v hre neprešlo týmto exportom.

## Hľadanie inštalácie {#finding-the-install}

- `--install <folder>`: priečinok hry, alebo jej `Content\Paks`, alebo ľubovoľný
  priečinok s súbormi `.utoc`. Nástroj skontroluje `<folder>`, potom
  `<folder>\acr\Content\Paks`, potom `<folder>\Content\Paks`.
- Inak sa prehľadá `steamapps\common\Assetto Corsa Rally` v každej knižnici Steam
  rovnakým spôsobom.
- Každý `.utoc` v tom priečinku sa otvorí ako jeden úložný priestor. Kontajnery,
  ktoré sa nedajú otvoriť, sa preskočia. Ak sa neotvorí žiadny, výpis je:
  „no readable IoStore containers in ...“.

Väčšina blokov je komprimovaná cez Oodle a knižnica sa hľadá v počítači (prehľadajú
sa všetky knižnice Steam). Pozri [Oodle](reader-oodle.md).

Hra sa berie ako AC Rally, keď kolo hovorí `"game": "assetto-corsa-rally"` (alebo
`acrally`), alebo keď zadáte `--game acrally`.

## Čo je etapa {#what-a-stage-is}

Etapa je mapa **World Partition**:

- `Content\Levels\<Stage>.umap` umiestňuje vzdialený terén.
- Zapečené bunky v `Content\Levels\<Stage>\_Generated_\*.umap` umiestňujú všetko
  ostatné.

Úroveň sa počíta ako etapa, ak jej priečinok prostredia,
`Content\Environments\<Stage>\`, obsahuje priečinok `MeshesTrack`. Nástroj sa neriadi
názvami dlaždíc, lebo etapa ich môže pomenovať podľa mesta, nie podľa svojej mapy.
`--level` sa porovnáva s týmito názvami máp bez ohľadu na veľkosť písmen. Zlý názov
vypíše, aké etapy existujú.

Nie je tu **žiadna krajina** (landscape). Povrch tvoria statické modely:

| Dlaždice | Cesta | Stanú sa |
|---|---|---|
| dlaždice trate, asi 175 m, rozdelené na dve | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` a `..._Terrain_k` | `ground:road` a `ground:terrain` (dlaždica trate bez rozdelenia, napríklad zamrznuté jazero, je celá cesta) |
| vzdialený terén, dlaždice 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Čítanie umiestnení {#reading-the-placements}

To, čo umiestni model, je `StaticMeshComponent`: jeho `StaticMesh` a jeho
`RelativeLocation`, `RelativeRotation` a `RelativeScale3D`, každé vzhľadom na
komponent, ku ktorému je pripojený (`AttachParent`), až ku koreňu aktéra, ktorý je
vo svete.

- Vlastnosti sú **neverzované**: uložené podľa pozície v zozname vlastností triedy,
  nie podľa mena. Čítajú sa so schémami v súbore
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (pozri [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Hodnota rovnaká ako šablóna komponentu (jeho archetyp v Blueprinte) sa neukladá,
  preto sa najprv rekurzívne čítajú hodnoty šablóny a vlastné hodnoty komponentu ich
  prepíšu.
- Komponenty s `bVisible = 0` alebo `bHiddenInGame = 1` sa preskočia. Preskočia sa
  aj siete, ktorých cesta obsahuje `respawnwall`, `collision`, `blocker`, `invisible`,
  `/hlod/` alebo `_hlod`.
- Rotácie používajú `FRotationMatrix` od Unreal (pitch, yaw, roll v stupňoch).
- Duplicity (rovnaká sieť v rovnakej transformácii na 0,1 cm) sa zahodia.
- Komponenty, ktoré sa nedajú prečítať, sa počítajú podľa dôvodu a hlásia sa,
  napríklad `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Inštancované komponenty** (lesy, takmer všetky) sa čítajú len s `--trees`. Tento
build preusporiadal tieto triedy nad rámec hlavičiek enginu, takže ich vlastnosti sa
nečítajú. Namiesto toho:

- sieť sa vezme z tabuľky závislostí balíka, kde každý taký komponent uvádza presne
  jednu statickú sieť,
- inštancie sa vezmú z natívneho bloku za vlastnosťami
  (`[1][1][128][count]`, potom `count` matíc 4x4 typu double),
- komponent sa považuje za umiestnený v koreni svojho aktéra, lebo tak umiestňujú
  aktéri vegetácie.

Súradnice sú Unreal: centimetre, Z hore, X dopredu, Y doprava, ľavotočivý systém.

## Ktorá etapa a akým smerom {#which-stage-and-which-way-round}

Rámec telemetrie nie je zdokumentovaný, preto sa nepredpokladá. Odhaduje sa:

- **Osem kandidátskych rámcov.** Unreal Z (cm) krát 0,01 sa stane výškou kola
  (y). Unreal X a Y sa stanú x a z kola, zameniť alebo nie, každé s ľubovoľným
  znamienkom, všetko škálované 0,01 na metre.
- **Mriežka výšky cesty.** Pre každú etapu sa umiestni každá dlaždica cesty (na
  najhrubšej úrovni detailu) a na každej bunke 2 m sa ponechá najvyšší vrchol cesty.
- **Bodovanie.** Až 400 vzoriek kola, rovnomerne rozložených, sa prevedie do
  priestoru Unreal cez každý rámec. Vzorka je na ceste, ak je medzi 3 x 3 bunkami
  okolo nej výška cesty najbližšia k nej medzi 1 m pod a 3 m nad vzorkou
  (`ON_ROAD`). Skóre je podiel vzoriek na ceste.
- **Víťaz.** Najlepší rámec na najlepšej etape, ak dosiahne aspoň 50 %. Inak sa
  export zastaví: „the lap does not lie on any stage's road in any frame (best: ...).
  Name the stage with --level.“
- **Kolo, ktoré pomenúva svoju trať.** Ak súbor kola má pole `track`, etapa, ktorej
  názov sa voľne zhoduje (iba písmená a číslice, jeden obsahuje druhý), sa vyskúša
  ako prvá, sama, a prijme sa, len ak dosiahne aspoň 80 %. Inak sa vyskúšajú všetky
  etapy.
- S `--level` sa vyskúša len táto etapa, vo všetkých ôsmich rámcoch.

Konzola napríklad vypíše
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Všetko sa potom zapíše **v rámci kola**: metre, Y hore. Stranu trojuholníka
otočí, kdekoľvek transformácia zrkadlí, aby plochy stále smerovali správne.

## Povrch {#the-ground}

- Koridor je `--margin` metrov okolo kola v jeho vlastnej rovine x/z.
- Každá dlaždica povrchu sa umiestni na najjemnejšej úrovni detailu a ponechajú sa
  len trojuholníky, ktoré zasahujú do koridora.
- Trojuholníky sa zoskupia podľa druhu (cesta alebo terén) a podľa štvorca 512 m
  v priestore Unreal (51 200 cm), každý štvorec s vlastným obrázkom. Časti sa
  pomenujú napríklad `ground:road 1_-4`. UV súradnice sú
  `(unreal_xy - square_origin) / 51200`.
- Normály sa počítajú z trojuholníkov pre celý súbor.

### Textúra povrchu {#the-ground-texture}

Ak nie je `--no-textures`, každý štvorec sa vymaľuje z dvoch zdrojov, pri
`--texture-size` pixeloch:

1. **Pečená farba povrchu.** `RuntimeVirtualTextureComponent` mapy etapy (jej box
   je `RelativeLocation` ako roh a `RelativeScale3D` ako veľkosť, bez rotácie)
   ukazuje na streamovanú **virtuálnu textúru**, farbu povrchu, ktorú hra zapiekla.
   Oblasť štvorca sa z nej prečíta na úrovni, ktorej pixely sú najbližšie
   požadovanej veľkosti. To je 13 až 59 cm na pixel podľa etapy.
2. **Satelitný obrázok** vyplní to, čo virtuálna textúra nechá čierne. Je to textúra
   `sat*_(b|bc|c|basecolor)` etapy v jej priečinku prostredia, čítaná až do 4096 px.
   Jej umiestnenie sa zistí fitovaním najmenších štvorcov prvého kanála UV vzdialeného
   terénu voči svetovým x a y. Fit musí byť lineárny s odchýlkou najviac 0,01 v 95. percentile,
   inak sa obrázok nepoužije. Ak UV vzdialeného terénu presiahnu 1 (materiál, ktorý
   ich opakuje), mapovanie sa raz zmenší na polovicu, kým sa nezmestí.

Konzola hlási, ktorý zdroj použila, napríklad
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Etapa bez oboch sa kreslí v plošných farbách.

## Umiestnené modely {#placed-models}

Každé umiestnenie, ktoré nie je dlaždicou povrchu, sa zaradí podľa cesty k sieti
(prvá zhoda vyhráva):

| Kategória | Názov siete (alebo cesta, pri stromoch) obsahuje |
|---|---|
| stromy (len s `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| skaly | `rock`, `cliff`, `boulder`, `stone` |
| obrubníky | `kerb`, `curb` |
| bariéry | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| tabule | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| budovy | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infraštruktúra | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekvizity | čokoľvek iné |

- Kópia sa zvažuje, ak jej začiatok leží v koridore dosahu (`margin + 60 m`),
  a kreslí sa, ak jej hranice zasahujú do koridora.
- Úrovne detailu nasledujú [Úrovne detailu a rozpočet](detail-budget.md):
  pásma vzdialenosti, potom sa najdrahšie modely znížia, aby sa zmestili do rozpočtu.
  Ak ani najhrubšie úrovne rozpočet neprekročia, najvzdialenejšie kópie sa vynechajú
  ako v BeamNG, kým to nevyjde. Obrubníky si zachovávajú plný detail a nikdy sa
  nevynechajú. Súhrn vypíše `placed on it (N triangles of a B budget)` a, ak kópie
  boli vynechané, `N copies left out to fit the budget, the furthest from the driving first`.
- Každá kategória je jedna časť v plošnej farbe: `ground:kerbs` pre obrubníky, ktoré
  sú jazdným povrchom, ako vo Forze a BeamNG, a `structure:<category>` pre ostatné:

| Kategória | Farba (lineárne RGB) |
|---|---|
| bariéry | 0,55, 0,52, 0,48 |
| tabule | 0,75, 0,72, 0,65 |
| budovy | 0,62, 0,58, 0,52 |
| infraštruktúra | 0,48, 0,48, 0,50 |
| skaly | 0,45, 0,43, 0,40 |
| rekvizity | 0,55, 0,45, 0,35 |
| stromy | 0,20, 0,32, 0,14 |
| obrubníky | 0,70, 0,25, 0,22 |

Statické modely, ktoré sa nedajú prečítať (kostrové siete, siete len pre Nanite,
úrovne, ktoré nie sú uložené vnútri), sa počítajú: `N meshes could not be read`.

## Kontroly, na ktorých to stojí {#checks-behind-it}

Podľa zdrojového kódu, na nainštalovanej hre:

- Každá tabuľka obsahu sa prečíta (verzia 8).
- Každá bunka každej etapy sa otvorí a každý komponent statickej siete a scény sa
  dekóduje tak, že skončí presne na natívnom konci svojej triedy.
- Takmer každá vzorkovaná statická sieť sa dekóduje (zvyšok sú kostrové). Dekódovaný
  rozmer dlaždice cesty sa zhoduje s jej uloženými hranicami.
- Úrovne mip satelitného obrázka sú presne také veľké ako ich bulk položky.
- Dlaždice kusu virtuálnej textúry sa účtujú až na bajt a dlaždice cesty pristanú na
  ceste, ktorú ukazuje.

## Známe medzery {#known-gaps}

- Vlastnosti inštancovaných komponentov sa nečítajú (pozri vyššie). Ich umiestnenie
  predpokladá koreň aktéra.
- Lesy generované PCG za behu hry nie sú uložené v súboroch a nedajú sa exportovať.
- Splinové siete (neviditeľné steny respawnu), dekálové komponenty a vlastné textúry
  umiestnených modelov sa nekreslia. Modely sú v plošných farbách.
- `--season` nemá žiadny efekt.
- Záplata hry môže posunúť sloty vlastností. Čítačka vyhodí chybu namiesto zlého
  čítania a kurz nahlási, koľko komponentov zlyhalo.
