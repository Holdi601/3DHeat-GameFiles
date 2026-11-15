---
title: Assetto Corsa Rally
nav_order: 3
lang: "cs"
source: course-assetto-corsa-rally.md
source_hash: "2e2369b24de9"
nav_exclude: true
search_exclude: true
---
# Export trati: Assetto Corsa Rally {#course-export-assetto-corsa-rally}

Assetto Corsa Rally je postaveno na Unreal Engine 5 (5.6.1, upravená verze)
a obsah dodává jako kontejnery IoStore. Žádný z nich není šifrovaný. Export
najde etapu a osovou orientaci z kola. Zapíše vlastní dlaždice terénu etapy,
rozdělené na silnici a terén a texturované zapečenou barvou povrchu etapy, a
ostatní modely umístí v plochých barvách podle kategorie.

```
python -m heat3d_gamefiles course rally_lap.json
python -m heat3d_gamefiles course rally_lap.json --level <stage map name>
python -m heat3d_gamefiles course rally_lap.json --level x      # a wrong name lists the stages
python -m heat3d_gamefiles course rally_lap.csv --game acrally --install "D:\Games\Assetto Corsa Rally"
```

Zdroje: [`acrally.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrally.py) (instalace, etapy, umístění),
[`acrallycourse.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/acrallycourse.py) (export).
Unreal čtečky pod tím jsou popsány na [Unreal 5 IoStore](reader-unreal-iostore.md)
a dekomprese na [Oodle](reader-oodle.md).

**Stav:** ověřeno na nainstalované hře s koly vygenerovanými v náhodném snímku na
každé etapě. Vždy našlo správnou etapu a snímek. Zatím jím neprošlo žádné kolo
nahrané přímo ve hře.

## Nalezení instalace {#finding-the-install}

- `--install <složka>`: složka hry, nebo její `Content\Paks`, nebo jakákoli složka
  s soubory `.utoc`. Nástroj zkontroluje `<složka>`, pak
  `<složka>\acr\Content\Paks`, pak `<složka>\Content\Paks`.
- Jinak se projde `steamapps\common\Assetto Corsa Rally` v každé knihovně Steamu
  stejným způsobem.
- Každý `.utoc` v té složce se otevře jako jeden úložiště. Kontejnery, které se
  nepodaří otevřít, se přeskočí. Pokud se neotevře žádný: "no readable IoStore
  containers in ...".

Většina bloků je komprimovaná Oodle a knihovna se hledá v počítači (prohledají se
všechny knihovny Steamu). Viz [Oodle](reader-oodle.md).

Hra se bere jako AC Rally, když soubor s kolem říká `"game": "assetto-corsa-rally"`
(nebo `acrally`), nebo když zadáte `--game acrally`.

## Co je etapa {#what-a-stage-is}

Etapa je mapa **World Partition**:

- `Content\Levels\<Stage>.umap` umisťuje vzdálený terén.
- Zapečené buňky v `Content\Levels\<Stage>\_Generated_\*.umap` umisťují všechno
  ostatní.

Úroveň se počítá jako etapa, když její složka prostředí,
`Content\Environments\<Stage>\`, obsahuje složku `MeshesTrack`. Nástroj se neřídí
názvy dlaždic, protože etapa může dlaždice pojmenovat podle města a ne podle
mapy. `--level` se porovnává bez ohledu na velikost písmen s těmito názvy map.
Špatný název vypíše etapy, které existují.

Žádná **krajina** tu není. Terén tvoří statické sítě:

| Dlaždice | Cesta | Stane se z nich |
|---|---|---|
| dlaždice trati, zhruba 175 m, rozdělené na dvě části | `.../MeshesTrack/SM_<Stage>TrackNNNN_Road_k` a `..._Terrain_k` | `ground:road` a `ground:terrain` (nerozdělená dlaždice trati, například zamrzlé jezero, je celá silnice) |
| vzdálený terén, dlaždice 2 km | `.../MeshesTerrain/...` | `ground:terrain` |

## Čtení umístění {#reading-the-placements}

Co mesh umisťuje, je `StaticMeshComponent`: jeho `StaticMesh` a jeho
`RelativeLocation`, `RelativeRotation` a `RelativeScale3D`, každé vztažené ke
komponentě, na kterou je připojená (`AttachParent`), až ke kořeni aktéra, který je
ve světě.

- Vlastnosti jsou **neverzované**: uložené podle pozice v seznamu vlastností třídy,
  ne podle jména. Čtou se pomocí schémat v
  [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py)
  (viz [Unreal 5 IoStore](reader-unreal-iostore.md#unversioned-properties)).
- Hodnota, která se rovná šabloně komponenty (jejímu archetypu v Blueprintu), se
  neukládá. Proto se nejdřív rekurzivně načtou hodnoty šablony a vlastní hodnoty
  komponenty je přepíšou.
- Komponenty s `bVisible = 0` nebo `bHiddenInGame = 1` se přeskočí. Stejně tak
  sítě, jejichž cesta obsahuje `respawnwall`, `collision`, `blocker`, `invisible`,
  `/hlod/` nebo `_hlod`.
- Rotace používají `FRotationMatrix` z Unreal (pitch, yaw, roll ve stupních).
- Duplicity (stejná síť se stejnou transformací na 0,1 cm) se zahodí.
- Komponenty, které nejde přečíst, se počítají podle důvodu a hlásí se, například
  `12 of 4,321 components could not be read: {'properties unreadable': 12}`.

**Instancované komponenty** (lesy, skoro všechny) se čtou jen s `--trees`. Tento
build upravil ty třídy nad rámec hlaviček enginu, takže jejich vlastnosti se
nečtou. Místo toho:

- síť se vezme z tabulky závislostí balíčku, kde každá taková komponenta uvádí
  přesně jednu statickou síť,
- instance se vezmou z nativního bloku za vlastnostmi
  (`[1][1][128][count]`, pak `count` matic 4x4 double),
- komponenta se bere jako umístěná v kořeni svého aktéra, což je způsob, jakým
  aktéři vegetace je umisťují.

Souřadnice jsou Unreal: centimetry, Z nahoru, X dopředu, Y doprava, levotočivá
soustava.

## Která etapa a jak otočená {#which-stage-and-which-way-round}

Rámec telemetrie není zdokumentovaný, proto se nepředpokládá. Nastavuje se
přizpůsobením:

- **Osm kandidátních rámců.** Unreal Z (cm) krát 0,01 se stane výškou kola (y).
  Unreal X a Y se stanou x a z kola, prohozené nebo ne, každé s některým
  znaménkem, vše násobeno 0,01 na metry.
- **Mřížka výšky silnice.** Pro každou etapu se umístí každá dlaždice silnice (na
  nejhrubší úrovni detailu) a pro každou buňku 2 m se ponechá nejvyšší vrchol
  silnice.
- **Bodování.** Až 400 vzorků kola, rovnoměrně rozmístěných, se převede do
  prostoru Unreal přes každý rámec. Vzorek je na silnici, když mezi 3 x 3 buňkami
  kolem něj je výška silnice nejblíž vzorku mezi 1 m pod ním a 3 m nad ním
  (`ON_ROAD`). Skóre je podíl vzorků na silnici.
- **Vítěz.** Nejlepší rámec na nejlepší etapě, pokud dosáhne aspoň 50 %. Jinak se
  export zastaví: "the lap does not lie on any stage's road in any frame (best:
  ...). Name the stage with --level."
- **Kolo, které pojmenuje svou trať.** Pokud soubor kola má pole `track`, jako
  první se zkusí jediná etapa, jejíž název se s ním volně shoduje (jen písmena
  a číslice, jeden obsahuje druhý), a přijme se, jen když dosáhne aspoň 80 %.
  Jinak se zkusí všechny etapy.
- S `--level` se zkusí jen tato etapa, ve všech osmi rámcích.

Konzole napíše například
`on <Stage>: 96% of the lap lies on its road, read as x = +X, z = -Y (Unreal, metres)`.

Všechno se pak zapíše **v rámci kola**: metry, Y nahoru. Obrácení trojúhelníku se
otočí všude, kde transformace zrcadlí, takže plochy stále ukazují správným směrem.

## Terén {#the-ground}

- Koridor je `--margin` metrů kolem kola v jeho vlastní rovině x/z.
- Každá dlaždice terénu se umístí na své nejjemnější úrovni detailu a ponechají
  se jen trojúhelníky, které zasahují do koridoru.
- Trojúhelníky se seskupí podle druhu (silnice nebo terén) a podle čtverce 512 m
  v prostoru Unreal (51 200 cm), každý čtverec s vlastním obrázkem. Části se
  pojmenují například `ground:road 1_-4`. UV souřadnice jsou
  `(unreal_xy - square_origin) / 51200`.
- Normály se počítají z trojúhelníků pro celý soubor.

### Textura terénu {#the-ground-texture}

Pokud nezadáte `--no-textures`, každý čtverec se maluje ze dvou zdrojů, v
rozlišení `--texture-size` pixelů:

1. **Zapečená barva povrchu.** `RuntimeVirtualTextureComponent` mapy etapy (jeho
   box je `RelativeLocation` jako roh a `RelativeScale3D` jako velikost, bez
   rotace) ukazuje na streamovanou **virtuální texturu**, barvu povrchu, kterou
   hra zapekla. Oblast čtverce se z ní přečte na úrovni, jejíž pixely jsou nejblíž
   požadované velikosti. To je 13 až 59 cm na pixel podle etapy.
2. **Satelitní snímek** vyplní to, co virtuální textura nechá černé. Je to textura
   `sat*_(b|bc|c|basecolor)` etapy ve složce jejího prostředí, čtená až do 4096 px.
   Její umístění se najde nejmenšími čtverci, které přizpůsobí první kanál UV
   vzdáleného terénu souřadnicím světa x a y. Přizpůsobení musí být lineární
   s chybou nejvýš 0,01 v 95. percentilu, jinak se snímek nepoužije. Pokud UV
   vzdáleného terénu přesahují 1 (materiál je opakuje), mapování se jednou
   zmenší na polovinu, dokud sedí.

Konzole napíše, který zdroj použila, například
`ground textured from the stage's baked ground colour (20 cm a pixel) and its satellite image (1.5 m a pixel)`.
Etapa bez obojího se vykreslí v plochých barvách.

## Umístěné modely {#placed-models}

Každé umístění, které není dlaždicí terénu, se zařadí podle cesty ke svému meshi
(vyhrává první shoda):

| Kategorie | Název meshe (nebo cesta, u stromů) obsahuje |
|---|---|
| stromy (jen s `--trees`) | `/foliage/`, `tree`, `bush`, `grass`, `plant`, `flower`, `leaves`, `spruce`, `pine`, `larch`, `birch`, `maple`, `oak`, `fern`, `shrub`, `hedge` |
| skály | `rock`, `cliff`, `boulder`, `stone` |
| obruby | `kerb`, `curb` |
| svodidla | `barrier`, `fence`, `wall`, `rail`, `tape`, `bale`, `tyre`, `tire`, `cone`, `bollard`, `net`, `guard` |
| značky | `sign`, `banner`, `board`, `flag`, `arch`, `gantry`, `advert`, `logo` |
| budovy | `house`, `building`, `bld`, `barn`, `shed`, `church`, `hut`, `garage`, `roof`, `tent`, `stand`, `cabin`, `chalet`, `farm` |
| infrastruktura | `pole`, `light`, `lamp`, `power`, `pylon`, `cable`, `post`, `mast`, `bridge` |
| rekvizity | cokoli dalšího |

- Kopie se zvažuje, když její počátek leží v koridoru dosahu (`margin + 60 m`),
  a vykreslí se, když její hranice zasahují do koridoru.
- Úrovně detailu se řídí podle [Úrovně detailu a rozpočet](detail-budget.md):
  pásma vzdálenosti, potom se nejdražší modely zjednoduší, aby se vešly do
  rozpočtu. Tam, kde nevejdou ani nejhrubší úrovně, se nejvzdálenější kopie
  vynechají, jako u BeamNG, dokud se to nevejde. Obruby si drží plný detail a
  nikdy se nevynechávají. Shrnutí vypíše `placed on it (N triangles of a B budget)`
  a, pokud se některé kopie vynechaly, `N copies left out to fit the budget, the
  furthest from the driving first`.
- Každá kategorie je jedna část v ploché barvě: `ground:kerbs` pro obruby, které
  jsou jízdní plochou, jako u Forzy a BeamNG, a `structure:<category>` pro ostatní:

| Kategorie | Barva (lineární RGB) |
|---|---|
| svodidla | 0,55, 0,52, 0,48 |
| značky | 0,75, 0,72, 0,65 |
| budovy | 0,62, 0,58, 0,52 |
| infrastruktura | 0,48, 0,48, 0,50 |
| skály | 0,45, 0,43, 0,40 |
| rekvizity | 0,55, 0,45, 0,35 |
| stromy | 0,20, 0,32, 0,14 |
| obruby | 0,70, 0,25, 0,22 |

Statické sítě, které nejde přečíst (skeletální sítě, sítě jen pro Nanite, úrovně
neuložené uvnitř), se počítají: `N meshes could not be read`.

## Kontroly v základu {#checks-behind-it}

Podle zdrojového kódu na nainstalované hře:

- Každá tabulka obsahu se načte (verze 8).
- Každá buňka každé etapy se otevře a každá komponenta statické sítě a scény se
  dekóduje tak, že končí přesně na nativním konci své třídy.
- Téměř každá vzorkovaná statická síť se dekóduje (zbytek jsou skeletální). Zjištěný
  rozměr dlaždice silnice odpovídá jejím uloženým hranicím.
- Mipy satelitního snímku mají přesně velikosti svých hromadných položek.
- Dlaždice části virtuální textury jsou spočítané až po bajt a dlaždice silnice
  dopadají na silnici, kterou ukazují.

## Známé mezery {#known-gaps}

- Vlastnosti samotných instancovaných komponent se nečtou (viz výše). Jejich
  umístění předpokládá kořen aktéra.
- Lesy generované PCG za běhu nejsou v souborech uložené a nedají se exportovat.
- Spline meshe (neviditelné zdi respawnu), dekorační komponenty a vlastní textury
  umístěných modelů se nekreslí. Modely mají ploché barvy.
- `--season` nemá žádný účinek.
- Oprava hry může posunout pozice vlastností. Čtečka vyhodí chybu místo špatného
  čtení a kurz nahlásí, kolik komponent selhalo.
