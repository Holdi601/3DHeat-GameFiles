---
title: "Forza Horizon"
nav_order: 1
lang: "sk"
source: course-forza-horizon.md
source_hash: "a8355122c4be"
nav_exclude: true
search_exclude: true
---
# Export trate: Forza Horizon {#course-export-forza-horizon}

Export Forzy číta trať priamo z archívov ForzaTech hry: terén, pričom cesta,
lem a tráva sú od seba rozlíšené, zem pečená z vlastných mapových podkladov hry,
a každý umiestnený model vo vlastnej textúre (obruby, zvodidlá, bariéry z pneumatík,
značky, rekvizity, budovy). Tiež nájde, na ktorých z pretekov hry bolo kolo
odjazdené, a pridá to, čo hra vydáva len pre tieto preteky (ich vrstvu udalostí:
bariéry, stany, portály, tribúny, vlajky), a zem každého miesta konania, cez ktoré
jazda prechádza, napríklad podlahu štadióna.

```
python -m heat3d_gamefiles course "Example Circuit"
python -m heat3d_gamefiles course lap.json -o course.glb --season winter
python -m heat3d_gamefiles courses -o courses
python -m heat3d_gamefiles terrain "<game>\media\Tracks\<map>" --route lap.json -o map.glb
```

Zdroje: [`cli.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/cli.py) (`export_course`, `_write_course`),
[`forzainstall.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzainstall.py),
[`forzaterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaterrain.py),
[`forzatexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzatexture.py),
[`courseexport.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/courseexport.py),
[`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py),
[`forzamaterial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzamaterial.py),
[`forzaroute.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaroute.py).
Samotné formáty kontajnerov sú na [ForzaTech](reader-forzatech.md).

## Hľadanie nainštalovanej hry {#finding-the-installed-game}

Nikto by nemal písať cestu ako
`D:\Games\steamapps\common\<Forza>\media\Tracks\<map>`, takže sa cesta zistí sama:

1. **Knižnice Steamu.** Súbor `config\libraryfolders.vdf` Steamu sa načíta z
   `C:\Program Files (x86)\Steam` alebo `C:\Program Files\Steam`, a každá položka
   `"path"` v ňom je knižnica. Hľadá sa `steamapps\common` každej knižnice.
2. **Microsoft Store.** Ak existuje, prehľadá sa `C:\XboxGames`. Tam je hra o jednu
   úroveň hlbšie, v `<game>\Content`.
3. **Priečinok hry** je ktorýkoľvek potomok týchto priečinkov, ktorý má priečinok
   `media\Tracks`, bez ohľadu na jeho názov.
4. **Priečinok trate** je ktorýkoľvek priečinok pod `media\Tracks`, ktorý obsahuje
   `GeoChunk0.minizip`. Počíta sa podľa obsahu, nie podľa názvu, takže trať pod
   názvom, ktorý nikto nevidel, sa tiež nájde.

Ak je hra inde, zadajte priečinok trate cez `--track`; pozri
[Riešenie problémov](troubleshooting.md#finding-the-game) ("no installed Forza track found").

`--track <folder>` preskočí všetko toto.

Priečinok trate obsahuje to, čo export číta:

| Súbor | Čo to je |
|---|---|
| `GeoChunk0.minizip` ... `GeoChunk3.minizip` | archívy: každý model, textúra a súbor umiestnení, bez názvov vnútri |
| `ChunkContentsMiniZip0.txt` ... `3.txt` | jeden riadok na položku archívu, v poradí položiek: jediný zdroj názvov |
| `AssetManifest.xml` | každá textúra, ktorú trať obsahuje, s hashom, pomocou ktorého na ňu odkazujú materiály |

## Ktorá trať {#which-track}

Hra obsahuje viac priečinkov tratí (otvorený svet mapy, garáž alebo dve). Správna
sa vyberie podľa **súradníc, nie podľa názvu**:

- Ohraničujúci kváder kola, rozšírený o `--margin`, je otázka.
- Pre každý priečinok trate sa štyri manifesty `ChunkContentsMiniZip*.txt` prečítajú ako text, bez otvárania archívu. Každý názov dlaždice terénu (`autoterrain_x<X>_z<Z>..._cluster<N>.i.modelbin`) nesie svoju pozíciu v mriežke. Nástroj spočíta, koľko rozdielnych dlaždíc leží v kvádri.
- Vyhrá trať s najviac dlaždicami tam. Ak žiadna nemá nijaké, export sa zastaví s hlásením "none of the installed tracks (...) has terrain at x ..., z .... Those are the game's own metres, as its telemetry reports them."

Celá trať sa vyhodnotí za menej ako sekundu. Zhoda názvu by mohla vybrať zlú mapu
a zlá mapa vyzerá rovnako uveriteľne ako správna.

Konzola vypíše `on <track>, in <game folder>`.

## Ktoré preteky {#which-race}

Hra distribuuje každé preteky ako trasu s číslom, ich **id trasy**. Každej trase
patria dva súbory:

| Súbor | Čo obsahuje |
|---|---|
| `media\OpenWorld\<map>\AITracks\Route<id>.owt` | AI jazdná línia pretekov: uzol s 56 bajtmi od bajtu `0x60`, počet uzlov na `0x24`, každý uzol začína svojou pozíciou (x, y, z) v metroch hry |
| `media\Stripped\gs\<map>\routedefinitions.zip` | jeden `route<id>_<map>.rtd` na preteky: obyčajný XML, ktorý vypisuje, čo pretek pridáva do sveta a čo z neho odoberá (pozri [Vrstva samotných pretekov](#the-races-own-layer)) |

Kolo sa priradí k trase porovnaním s každou AI líniou, ktorej kváder sa prekrýva
s kvádrom kola:

- Od každej vzorky kola vzdialenosť k najbližšiemu bodu línie; a od každého bodu línie vzdialenosť k najbližšej vzorke kola.
- Dva mediány sa sčítajú. Trasa s najmenším súčtom vyhrá, ak je súčet menší ako **30 m** (`MATCH`).
- Potrebné sú oba smery: krátky sprint leží pozdĺž dlhej trasy, ktorá používa tú istú cestu, a dlhé kolo pokrýva krátku trasu.

Konzola vypíše `the game's route <id> (driven line within <n> m of it)`, alebo že
žiadna trasa nesedí. Bez zhody sa umiestni len voľný svet.

## Terén {#terrain}

Ako sa terén nájde (v `forzaterrain.py`):

- Manifesty pomenúvajú terén ako priestorový index:
  `scene\tbheightfield\autoterrain_x-2046_z1023_cluster012.i.modelbin`.
- Obe čísla sú súradnice mriežky, ktoré **postupujú po 1023**, a každý krok mriežky je **dlaždica 512 m**. Dlaždica `x-2046` je `-2046 / 1023 = -2`, ktorá začína na `-2 * 512 = -1024` m. Ak čítate názvy ako metre, každé vyhľadanie sa minie dvojnásobne a stále vráti terén, z nesprávnej časti mapy.
- Dlaždica sa môže vyskytnúť trikrát: obyčajná, `_cb` a `_ul`. Všetky tri pokrývajú rovnakú zem. Jedna sa vezme na dlaždicu, v tomto poradí preferencie, pretože ich zlúčenie by strojnásobilo geometriu do splývajúcich plôch.
- Dlaždica sa načíta len vtedy, ak sa dotýka kvádra kola **a** koridora. Dlaždica, ktorej sa koridor nedotýka, sa nikdy nedekomprimuje.
- Každý `.modelbin` vybranej dlaždice sa dekóduje len na **úrovni detailu 0**. Dlaždica nesie štyri úrovne nad tou istou zemou, a ak by sa exportovali všetky, ten istý meter štvorcový by bol v súbore štyrikrát.
- Každá sieť nesie vlastnú mierku a posun vo svetových súradniciach, takže dlaždica pristane tam, kde ju hra položí, bez transformácie inštancie. Trojuholníky, ktorých stopa sa prekrýva s kvádrom, sa zachovajú, potom len tie, ktoré zasahujú do koridora.
- Sieť vo formáte, ktorý čitateľ odmietne, sa preskočí a počíta (`N meshes could not be read`), aby tenký výsledok vysvetlil, prečo.

Súhrn terénu vypíše počet vrcholov, trojuholníkov, sietí a dlaždíc a rozsah x/y/z.

### Cesta, lem, terén, vyznačenia, voda {#road-verge-terrain-markings-water}

Názvy materiálov nevedia povedať, kde je cesta. Okolo okruhu 94 % zeme používa
materiál s cestným shaderom, lebo terén pri ceste sa kreslí s ním a shader
rozhodne asfalt alebo trávu na každý pixel. Preto:

| Druh | Určený podľa |
|---|---|
| pás cesty | **rozloženie vrcholov**: pásy cesty sú jediná zem s druhou sadou UV (kanál 1); trojuholník, ktorého všetky tri vrcholy ju majú, je cesta |
| asfalt alebo lem | v rámci pásu cesty, **maska asfaltu** dlaždice v ťažisku trojuholníka: 0,5 alebo viac je `road`, menej je `verge` |
| vyznačenia | názov materiálu obsahuje `whiteline`, `yellowline` alebo `decal` |
| stopy pneumatík | názov materiálu obsahuje `tyremark` alebo `skid` (kontroluje sa pred vyznačeniami, lebo stopy pneumatík sa dodávajú ako `tyremark_decal_*`) |
| voda | názov materiálu obsahuje `water`, `lake`, `river`, `paddy`, `ocean` alebo `sea` |
| terén | všetko ostatné |

Podľa meraní na nahraných kolách na testovacom okruhu skoro všetky vzorky
pristanú na trojuholníkoch pásu cesty a drvivá väčšina na asfaltovej časti, keď
maska oddelí lem.

Maska asfaltu existuje len vtedy, keď sa pečú textúry zeme. S `--no-textures`,
alebo pri dlaždici, ktorej chýbajú mapy, pásy cesty zostanú celé ako `road` a lem
sa neoddelí. Chýbajúce mapy stoja detail, nikdy geometriu.

### Namaľované vrstvy sa zdvihnú {#painted-layers-are-lifted}

Čiary pruhov a stopy pneumatík sa dodávajú ako vlastné trojuholníky ležiace presne
na ceste. Hra ich kreslí s hĺbkovým posunom. Ak by sa kreslili tak, ako sú, cesta
a farba by bojovali o každý pixel. Export dá každej časti vyznačenia a stôp
pneumatík vlastnú kópiu jej vrcholov, zdvihnutú o **5 cm** (`DECAL_LIFT`) pozdĺž
normály povrchu, takže cesta pod nimi sa nezdvihne tiež.

### Normály {#normals}

Normály terénu pochádzajú z archívu. X normály je uložené ako štvrtý short
pozície, a Y a Z v atribúte `NORMAL` (pozri [ForzaTech](reader-forzatech.md)). Ak
nejaký vrchol v extrakcii nemá normálu, normály pre celú zem sa namiesto toho
vypočítajú z trojuholníkov.

## Textúra zeme {#the-ground-texture}

Každá dlaždica terénu dodáva tri mapy pokrývajúce jej štvorec 512 m, v piatich
rozlíšeniach (`_quality1` až `_quality5`, najväčšia 2048 px, čo je 25 cm na pixel):

| Mapa | Vzor názvu súboru | Čo obsahuje (ako sa meralo) |
|---|---|---|
| hlavná | `mainmap_x<X>_z<Z>_x<season>x_diff` | R, G: detailná normála (x, z). A: nižšia na asfalte a na drsnej zemi |
| podradená | `submap_x<X>_z<Z>_x<season>x_diff` | váhy vrstiev. B: vysoká na asfalte (239 na jazdnej línii, 165 vedľa nej) |
| lesk | `autoglossf0_x<X>_z<Z>_x<season>x_glos` | G: nízka na asfalte (147 oproti 215). B: stúpa v lesoch |

Žiadna z nich nie je farebná fotografia. Sú to vstupy, s ktorými shader terénu
hry mieša svoje materiálové vrstvy, a tie vrstvy sa nedekódujú. Pečená textúra je
preto **interpretácia, nie kópia vzhľadu hry**. Zachováva *kde* je aký druh zeme,
na 25 cm, a maľuje ju pevnými farbami:

| Zem | Lineárne RGB | Váha |
|---|---|---|
| tráva (krátka, pri trati) | 0,30, 0,44, 0,18 | základ |
| drsná (ďalej von) | 0,40, 0,42, 0,22 | `smoothstep(88 -> 72, main.A) * (1 - asphalt)` |
| les | 0,13, 0,23, 0,10 | `smoothstep(4 -> 24, gloss.B)` |
| asfalt | 0,20, 0,20, 0,21 | `smoothstep(188 -> 228, sub.B) * smoothstep(200 -> 168, gloss.G)` |

Pre asfalt musia súhlasiť obe mapy. Jedna sama nechá šedé škvrny v tráve všade,
kde kompresia blokov zvoní. Výsledok sa tieňuje detailnou normálou hlavnej mapy
voči pevnému svetlu (`0.55 + 0.6 * lambert`), takže okraje obrubníkov, svahy a
koľaje vyzerajú ako reliéf, a zapíše sa ako 8-bitové sRGB.

Orientácia: riadok 0 pixelov je **severný** okraj dlaždice (najväčšie z), stĺpec 0
jej **západný** okraj (najmenšie x). Zistilo sa to premietnutím nahraných kôl na
masku asfaltu všetkými ôsmimi spôsobmi, akými sa štvorec dá prevrátiť alebo otočiť.
Presne jeden spôsob ich položí na asfalt. Z neho vyplývajú UV: `u = (x - x0) / 512`,
`v = 1 - (z - z0) / 512`.

Mapy sa čítajú v najlepšom dostupnom rozlíšení až do kvality 5 a prevzorkujú sa na
veľkosť hlavnej mapy. Ak je farebný obraz väčší ako `--texture-size`, potom sa
zmenší na túto veľkosť Lanczosovým filtrom. Maska asfaltu sa vždy zachová v plnom
rozlíšení, pretože rozhoduje o geometrii. `--season` vyberie mapy `x<season>x`.
Dlaždica bez máp pre toto obdobie sa kreslí v plochých farbách a konzola hlási
`N without maps`.

## Umiestnené modely {#placed-models}

Terén nesie vlastnú svetovú pozíciu. Nič iné ju nemá. Kde stojí každá kópia
modelu, je zapísané v súboroch umiestnení `.pgeo`, jeden na kategóriu na
priestorovú bunku:
`scene\proc\cellsize\<size>\<x>_<z>\c<size>_<category>_....pgeo`. Rozloženie
záznamu je na [ForzaTech](reader-forzatech.md#placement-files-pgeo).

### Čo sa číta {#what-is-read}

- Súbory umiestnení sa filtrujú **podľa názvu**: veľkosť bunky a pozícia bunky v ceste dávajú štvorec bunky (`x * size` až `(x + 1) * size`), a otvoria sa len bunky prekrývajúce kváder kola v žiadanej kategórii.
- Predvolené kategórie: `barriers`, `props`, `signs`, `buildings`, `infrastructure`, `bridges`, `rocks`, `evolving`. `--trees` pridá `trees`, `bushes` a `smashables`. Tieto sa nikdy nečítajú: `grasstemplate`, `crowdtemplate` a `cwdspline` (tráva a diváci: hra ich kreslí ako animované sprity, nemajú geometriu).
- Každý súbor patrí k **vrstve**, prečítanej z jeho názvu za `c<size>_<category>_`. Slovo úrovne detailu (`do`, `so`, `ulc`, `ulp`, `cwd`) a voliteľné číslo sekcie je voľný svet. Čokoľvek iné je vrstva, ktorú hra zapína: runtime vrstva (`rt_0`), aktivita (`_tag_<name>_`), zberateľský predmet, čokoľvek zaradené pod `evolving`. Vrstva, ktorá pomenúva trasy (`rt_x<id>`, napríklad `rt_x1023_x2201`), patrí len týmto pretekom a číta sa len vtedy, ak sa kolo prideľuje k nim. Pozri [Zapínané vrstvy](#switched-on-layers).
- Kópia sa zachová, ak je jej pozícia vnútri kvádra a vnútri koridora. Presné opakovania (rovnaká pozícia a orientácia na milimeter, uvedené dvoma susednými bunkami) sa zlúčia.
- **Obrubníky** sú rekvizity, ktorých názov modelu začína `road_gen_rum` (vibračné pásy). Zapisujú sa ako `ground:kerbs`, nikdy sa nezjednodušujú ani nevynechávajú, lebo kolo sa meria podľa nich.

| Kategória | Časť | Záložná farba (bez textúry) |
|---|---|---|
| obrubníky | `ground:kerbs` | 0,60, 0,12, 0,10 |
| bariéry | `structure:barriers` | 0,50, 0,50, 0,50 |
| rekvizity | `structure:props` | 0,45, 0,35, 0,25 |
| značky | `structure:signs` | 0,70, 0,70, 0,70 |
| budovy | `structure:buildings` | 0,55, 0,52, 0,48 |
| infraštruktúra | `structure:infrastructure` | 0,45, 0,45, 0,47 |
| mosty | `structure:bridges` | 0,45, 0,45, 0,45 |
| skaly | `structure:rocks` | 0,30, 0,28, 0,25 |
| rozbitné | `structure:smashables` | 0,12, 0,22, 0,06 |
| stromy, kry | `structure:trees` | 0,10, 0,20, 0,05 |

### Geometria modelu {#the-model-s-geometry}

Umiestnený názov `<model>_3D` odkazuje na súbory modelu `<model>_cluster###.i.modelbin`
(až tucet). Každý trojuholník nesie masku úrovní detailu, do ktorých patrí:

- Úrovne modelu sú jeho trojuholníky výslovne označené pre danú úroveň. Úrovne idú súvisle od 0, najjemnejšia prvá.
- Trojuholníky označené `0xFFFF` (všetky úrovne) sú rozbitné kúsky, napríklad stĺpiky zvodidla alebo jednotlivé pneumatiky z hromady. Prekrývajú celý model a hra ich kreslí namiesto neho, keď je rozbitý. Používajú sa len pri modeli bez výslovne označenej úrovne.
- Podsiete, ktorých materiálový shader je projektovaná **nálepka**, sa vynechajú.

Každá kópia sa umiestni svojou pozíciou, svojimi osami x a y z záznamu (z = x krížom y)
a svojou mierkou. Normály sa transformujú inverznou mierkou.

### Ktorá textúra {#which-texture}

Materiál nepomenúva svoje textúry. Vymenúva ich ako hashe a `AssetManifest.xml`
trate mapuje každý hash (`SourceHash`) na názov textúry. Číta sa len sekcia
`<Textures>`, ktorá sa zastaví na `</Textures>` v súbore, ktorý môže mať desiatky
megabajtov. Potom:

1. Slot `0x88B483AA` je základná farba v štandardnom shaderi prostredia (každý vzorkovaný materiál). Ak sa tam materiál viaže na textúru, použije sa tá.
2. Inak rozhoduje druh samotnej textúry, čo je slovo pred jej GUID: `_bclr_`, potom `_diff_`, potom `_colour_`.
3. Mapy terénu (`mainmap`, `submap`, `autogloss`) a palety odtieňov (`tint`, `worldtint`) nikdy nefarbia model.

Model je teda zafarbený tým, čo jeho materiál viaže, nie textúrou pomenovanou ako
model. Napríklad `bar_rur_armco_crct_02_c` používa textúru `..._02_a`.

Textúra sa číta zo archívov v najmenšom rozlíšení, ktoré má aspoň **256 px** na
šírku (`MODEL_TEXTURE`), zmenší sa na 256, ak je väčšia, a uloží sa ako RGB JPEG
v `.glb`. Farba zvodidla pri 256 px na štyri metre je 1,6 cm na pixel a okolo 80
takých textúr sa zmestí do atlasu prehliadača spolu s dlaždicami zeme.

**Ročné obdobia.** `--season` vymení textúru za jej sezónny ekvivalent podľa názvu,
GUID sa ignoruje (`..._xsummerx_bclr` na `..._xwinterx_bclr`, alebo `..._bclr` na
`..._winter_bclr`), ak to trať má. S `--season winter` sa zimný materiál podsiete
použije tam, kde ho uvádza jej tabuľka variantov.

**Varianty.** Záznam podsiete sa začína tabuľkou dvojíc `(summer, winter)` materiálov,
jeden pre každý vzhľad, aký kópia môže mať: päť potlačí pre bilboard, šesť farieb
pre hromadu pneumatík. Každý záznam umiestnenia hovorí, aký variant má táto kópia.
Podsieť s menším počtom variantov, než má model, opakuje svoje vlastné.

**Blok zástupnej farby.** Spoločné atlasy budov vyhradzujú plný RGB blok (255, 64, 0)
pre plochy, ktoré shader budovy farbí z iných textúr. Ak je viac než dvadsatina
textúry v rozsahu 12 úrovní od tejto farby, blok sa prefarbí na priemernú farbu
textúry. Inak by mesto vyšlo oranžové.

### Priehľadné plochy {#see-through-surfaces}

Pletivá a siete sú jednoduché štvoruholníky s dierami v alfa kanáli textúry.
Nakreslené plné, je z plota stena naprieč výhľadom na trať. Plochy, ktorých
materiálový shader zodpovedá `alphatest`, `alphablend`, `transmissive`,
`anim_flag`, `impostor`, `branch`, `bush` alebo `tree`, sa testujú:

- Nepriehľadnosť textúry sa spriemeruje na mriežke 32 x 32.
- Pre každú plochu (každý vystrihnutý trojuholník zdieľajúci jednu textúru) sa vzorkujú štyri body na trojuholník v priestore UV a váhujú sa plochou UV trojuholníka.
- Ak je priemerná nepriehľadnosť aspoň 0,05 a menej ako **0,5**, celá plocha sa vynechá. Pod 0,05 alfa jasne znamená niečo iné pre svoj shader (výstražná značka vzorkujúca 0,01), a plocha sa ponechá plná.
- Model, ktorého každá plocha bola vynechaná, sa nahlási: `N models left out as see-through (mostly holes in their texture)`.

Nástroj posudzuje celú plochu, nie jeden trojuholník naraz. Keby sa posudzovalo
po trojuholníkoch, z každého štvoruholníka by prežila polovica a pletivá by vyšli
ako rad zubov.

### Budovy nakreslené celé {#buildings-drawn-whole}

Mesto stavia budovy z modulárnych dielov: stovky tisíc okolo jedného pouličného
okruhu, desiatky miliónov trojuholníkov aj na najhrubšej úrovni. Vynechávanie
kúskov po jednom nechávalo osamelé steny stáť. Hra tiež dodáva celé náhrady
budov v `scene\hlod_tier_1\`, jedna sieť na budovu (kmeň `hlod_tier_1_*`), už vo
svetových súradniciach ako terén:

- Svetový kváder každej náhrady sa prečíta z pozičného kvádra jej siete (čítanie hlavičky, nie dekódovanie). Pre celú mapu to trvá sekundy.
- Použijú sa náhrady, ktoré sa dotýkajú kvádra kola a koridora.
- Každý kus `buildings`, ktorého pozícia leží vnútri stopy náhrady (plus 0,5 m), sa zahodí a nakreslí sa náhrada. Jej vzdialenosť od jazdy sa meria k najbližšej hrane budovy.
- Súhrn hovorí `N buildings drawn whole from the game's own stand-ins (which replace M modular pieces)`.

### Zapínané vrstvy {#switched-on-layers}

To, čo zapnutá vrstva umiestňuje, sa exportuje, ale oddelene od voľného sveta,
aby ju prehliadač mohol zobraziť alebo skryť:

| Vrstva | Časť |
|---|---|
| voľný svet | `structure:<category>` (ako doteraz) |
| vrstva pomenúvajúca trasu zhodných pretekov | `structure:event_<category>` |
| každá iná zapnutá vrstva | `structure:layer_<category>` |

Súhrn ich počíta: `switched-on layers: <n> copies in <m> (<layer names>)`.

### Modely už vo svetových súradniciach {#models-already-in-world-coordinates}

Niektoré druhy modelov nie sú v žiadnom súbore umiestnení. Ich siete nesú vlastnú
svetovú pozíciu, ako terén, takže ich nič nemusí umiestňovať:

| Priečinok pod `scene\models\` | Čo je to | Časť |
|---|---|---|
| `plots` | vlastná zem miesta: podlaha a vnútro štadióna, areál festivalu, námestie | `ground:venue` |
| `plinths` (a každý model pomenovaný `floor`, `ground` alebo `road`) | zem, ktorou je ulica ozdobená: kvetináče, schody, dlažba parku | `ground:plinths` |
| `hda_infrastructure` (mosty) | procedurálne postavené mosty | `structure:bridges` |

- Model sa považuje za ležiaci vo svetových súradniciach, keď stred jeho kvádra leží
  viac než **300 m** (`WORLD_REACH`) od jeho vlastného počiatku. Modely umiestnené
  súbormi umiestnení sú do pár stoviek metrov od svojich.
- Nekreslia sa: uzávery, káble natiahnuté pozdĺž ciest, pozadie mora, strechy a uzávery
  modulárnych budov (náhrady tie budovy kreslia), kolízne a vodné objemy.
- Každý sa číta z kvádra svojich sietí (čítanie hlavičky), niekoľko sekúnd pre celú
  mapu, raz za beh.
- Časti zeme sa nikdy nekreslia hrubšie a nikdy sa nevynechávajú kvôli rozpočtu,
  rovnako ako obrubníky.

**Miesto sa vyreže celé.** Keď jazda prechádza cez vlastnú zem miesta
(`ground:venue`), koridor sa rozšíri na celú stopu tej zeme plus `--margin`, takže
tribúny, steny a bariéry okolo štadióna prídu tiež, nielen pás, po ktorom išli
kolá. Konzola vypíše `through a venue (<model names>): cutting all of its ground, <n> km2`.
Podstavce koridor nerozširujú.

### Detail a rozpočet {#detail-and-the-budget}

Pásma vzdialenosti, rozpočet a ktoré kópie idú prvé, keď je rozpočet príliš malý,
sú na [Úrovne detailu a rozpočet](detail-budget.md).

### Súhrn umiestnenia {#placement-summary}

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

## Vrstva samotných pretekov {#the-races-own-layer}

Mnohé preteky vydávajú veci, ktoré vo voľnej jazde nie sú: betónové steny a ploty,
ktoré uzatvárajú bočné cesty, hromady pneumatík, stany, štartovný portál,
tribúny, vlajky, transparenty. Každé preteky ich vymenúvajú vo svojej definícii trasy
(`route<id>_<map>.rtd` v `routedefinitions.zip`, obyčajný XML v obyčajnom zip):

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

- **Čo sa pridáva.** Každá inštancia sa umiestni ako kópia zo súboru umiestnení. Šestnásť čísel transformácie sú štyri riadky: osi x, y a z modelu (každá škálovaná) a jeho pozícia v metroch hry. Tretí riadok je vektorový súčin prvých dvoch. `Material` je variant, ktorý kópia nosí. Časť je `structure:event_<kind>`, kde `<kind>` je priečinok pod `scene\models\` (barriers, props, infrastructure, signs; čokoľvek iné sa počíta ako props), a uzol nesie glTF extras `{"layer": "event", "route": <id>}`.
- **Čo sa odoberá.** Kópia voľnej jazdy, ktorá stojí do **0,1 m** od pozície skrytého objektu, sa vynechá. Skrytý objekt stojiaci v počiatku je model vo svetových súradniciach; jeho GUID inštancie sa vyhľadá v `AssetManifest.xml` trate (zoznam `<Models>`: zdroj modelu, potom GUID jeho kópií), aby sa pomenoval.
- **Zem, ktorú pretek skrýva, sa zachová.** Pretek, ktorý skrýva zem miesta konania, na nej položí vlastný povrch. Keď tento povrch nie je medzi modelmi, ktoré trať dodáva, skrytá zem zostane ako najbližšia vec tomu, po čom sa jazdí, a súhrn to hovorí (`kept <model>: the race hides it for a surface of its own
  that the track does not ship`).
- **Nekreslí sa, ale počíta sa.** Značky divákov (`crowd_proxies`: hra z nich kreslí dav ako sprity) a kolízne splajny (`.splinecol`). Konzola ich vypíše: `its own layer: <n> copies of <m> models, <k> free-roam objects hidden; not drawn: ...`.
- Modely pretekov, ktoré trať nedodáva, sa pomenujú v `placed names have no model in the archives` (svetelné žiary, niektoré značky, obsah, ktorý hra streamuje).

Umiestnia sa len kópie vnútri koridora, ako pri všetkom ostatnom.

## Zapisovanie súboru {#writing-the-file}

Časti sa zapisujú v tomto poradí: pre každú dlaždicu `terrain`, `verge`, `road`
(každá s obrázkom dlaždice), potom `water`, `tyre marks`, `markings` (ploché, posledné
dve zdvihnuté), a potom každá umiestnená časť zoradená podľa názvu. Súradnice sú
hry vlastné (metre, Y hore). Pozri [Výstupný formát](output-format.md).

Súbor hovorí, čo obsahuje, vo svojom glTF `asset.extras`:

| Pole | Význam |
|---|---|
| `course_format` | `2`: vrstva samotných pretekov, miesta konania a modely vo svetových súradniciach sú v ňom. [`courses`](commands.md#courses) exportuje súbor s nižším číslom (alebo bez neho) znova |
| `route` | priradené id trasy, alebo `null` |
| `event_copies`, `event_kinds` | koľko kópií vrstvy samotných pretekov sa umiestnilo a ich druhy |
| `hidden` | kópie voľnej jazdy vynechané, lebo ich preteky odstraňujú |
| `venue` | modely zeme miest konania, cez ktoré jazda prechádza |
| `layers` | umiestnené zapnuté vrstvy |

## Čo to stojí {#what-it-costs}

Hrubé rády veľkostí:

| Trať | Výsledok |
|---|---|
| krátky vidiecky okruh | niekoľko stoviek tisíc trojuholníkov terénu, cez milión umiestnených; sekundy, pod 100 MB |
| dlhý bodový sprint | koridor je malá časť kvádra okolo neho; asi minúta, niekoľko stoviek MB |
| pouličný okruh v meste | tisíce bariér, rekvizít a značiek a celé budovy; s automatickým rozpočtom až niekoľko stoviek MB |

Štvorcový kilometer terénu otvoreného sveta je asi milión trojuholníkov.

## Kontroly v pozadí {#checks-behind-it}

Toto sú merania urobené pri písaní čítača, ako je uvedené v zdrojovom kóde. Testy
ich znova nespúšťajú, pokiaľ nie je hra nainštalovaná.

- Na testovacom okruhu auto sedí asi na svojej výške jazdy nad extrahovanou zemou (medián pod 0,2 m).
- Každá vzorkovaná dlaždica pristane vnútri štvorca 512 m, ktorý predpovedá jej názov.
- Po sebe idúce umiestnenia zvodidiel sú presne 4 m od seba a väčšina koncov zvodidiel pristane do 5 cm od začiatku ďalšieho.
- Obrubníky sú pár centimetrov nad extrahovanou zemou, čelom nahor, do 5 m od jazdy (tiež test s nainštalovanou hrou, pozri [Vývoj](development.md)).

## Nevykresľuje sa {#not-drawn}

- Stromy a kry, pokiaľ nie je `--trees`. Tráva a davy nikdy (hra ich kreslí ako sprity).
- Modely pretekov, ktoré trať nedodáva (pozri [Vrstva samotných pretekov](#the-races-own-layer)).
- Materiály projektovaných nálepiek na modeloch.
- Nápisy na značkách, ktoré sú alfou prelínané cez tabuľu, vyjdú nepriehľadné.
- Farba zeme je rekonštrukcia toho, kde sú asfalt, tráva a lesy, nie vlastné materiály terénu hry.
