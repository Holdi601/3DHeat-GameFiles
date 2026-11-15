---
title: "Frostbite"
nav_order: 5
lang: "cs"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, bundly, meshe a úrovně {#frostbite-toc-cas-bundles-meshes-and-levels}

**Čte úroveň Battlefield 6 až do jejího terénu, jejích umístěných meshů a jejich barevných map a zapisuje ji jako `.glb`.** Hry Frostbite (Battlefield, Need for Speed, Dead Space) drží svůj obsah v blobech `.cas`, popsaných tabulkami obsahu `.toc`. Tabulka úrovně říká, které bundly úroveň načítá, bundly pojmenovávají každý asset a assety říkají, který mesh kde stojí.

Zdroje:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabulky, balíčky, datové bloky),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(bundly a jejich manifesty),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(oddíly EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(výšková mapa),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(textury a materiály),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(umístění a export).
Příkazy: `identify`, `levels`, `level` (viz [Příkazy](commands.md#levels-and-level-frostbite)).

Nic z toho hra nedokumentuje. Každé rozložení níže bylo přečteno ze souborů a pak ověřeno proti všem z nich, a každá sekce říká, jaká kontrola to byla. Tam, kde starší nástroje Frosty popisují starší verze struktury, názvy polí následují jejich, ale žádný kód z nich převzat nebyl (viz [Pravidla a licence](rules-and-licences.md)).

## Hlavička, která vypadá zašifrovaně a není {#the-header-that-looks-encrypted-and-is-not}

| Magické číslo (u32, little-endian) | Význam | Zpracováno |
|---|---|---|
| `0x00CED100` | prostý: strom začíná hned | čte se |
| `0x01CED100` | podepsaný: podpis o 556 bajtech, pak strom **v čistém textu** | čte se |
| `0x03CED100` | XOR obfuskovaný, s klíčem v hlavičce souboru | rozpoznán a odmítnut |

Podepsaná forma je ta, kterou dnešní Battlefield dodává. Bajty s vysokou entropií za magickým číslem jsou podpis, ne šifrový text.

## Strom DbObject {#the-dbobject-tree}

Jedna rekurzivní struktura. Každé pole je bajt typu (spodních pět bitů typ, bit 7 „anonymní“), volitelný název a hodnota. Kontejnery nesou svou délku jako celé číslo s proměnnou délkou a končí nulovým bajtem. `parse_toc` ověří délku každého kontejneru, takže soubor, který se přečte, byl pochopen. `layout.toc` je v této podobě.

## Instalační balíčky {#installation-packages}

Každé umístění pojmenovává **instalační balíček**, do kterého jeho blob patří. Každý balíček číslují své bloby od `cas_01`, takže samotné číslo blobu je dvojznačné, jakmile je nainstalováno víc než jeden balíček, což se vždy stane.

- `layout.toc` vypisuje balíčky pod `installManifest.installChunks`, každý s `persistentIndex` a `installBundle` jako `Win32/installation/<package>`.
- Blobs balíčku jsou v té složce, pod `Data` pro základní hru, nebo pod `Update/<pack>/Data` pro to, co přišlo později.
- Záznam umístění nese úplný 32bitový `persistentIndex`: spodní polovina prvního slova drží horní polovinu, horní polovina druhého slova spodní polovinu; spodní polovina druhého slova je číslo blobu.

Kontrola: každé umístění v každé binární tabulce instalace se přeloží na deklarovaný balíček a leží uvnitř blobu, který pojmenovává. Dřívější verze vzala první `cas_NN.cas` správného čísla. Třetina datových bloků, které tehdy četla, pak vypadala na vysokou entropii a byla brána za šifrování. Byly to správné posuny v nesprávném souboru. Nic nalezeného není šifrované.

## Tabulka úrovně {#the-level-table}

Tabulka úrovně (`levels/<level>/<level>.toc`) je tabulka sekcí: patnáct big-endian slov hlavičky, pak sekce kladené za sebou, jejichž posuny jsou jak uvedené, tak odvoditelné ze dvou počtů.

| Sekce | Obsah |
|---|---|
| bundly | hašovací tabulka (jedno slovo na každý), pak záznam 16 bajtů na bundle: klíč, `0x40000000` \| velikost, 0, posun |
| hašovací tabulka chunků | jedno slovo na chunk |
| chunky | 16bajtové id (GUID chunku **s obrácenými bajty**), pak slovo: `0x80000000` \| 4 x index jeho umístění |
| umístění | čtyři big-endian slova: balíček (rozdělený), blob, posun, velikost |

Id chunků a umístění jsou **v různém pořadí**. Čtení v pořadí souboru spáruje každý chunk s bajty jiného chunku, které se dekódují dobře (většinou jako zvuk), a tak to nevypadá špatně, dokud mesh nevyjde jako šum. Kontrola: v úrovni jsou indexová slova permutací 0 až počet chunků minus jedna.

Bundly jsou uloženy přímo za tabulkou sekcí. Každý má devět big-endian slov hlavičky, pak své záznamy: osm bajtů posunu a velikosti, před kterými jsou dalších osm s balíčkem a blobem, když má bajt příznaků nastavený nejvyšší bit. Kontrola: u každého bundlu končí poslední záznam přesně tam, kde začínají bajty příznaků.

### Která tabulka je úroveň {#which-table-is-the-level}

Úroveň může mít několik tabulek stejného názvu: jednu v `Data` základní hry, jednu v každé aktualizaci (`Update/<pack>/Data`), která ji přidává nebo mění, a jednu v každém balíčku ve vysokém rozlišení (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Jen některé obsahují bundly. U úrovně, kterou přidává aktualizace, obsahuje tabulka v základní hře jen chunky a žádné bundly, a úrovní je ta v aktualizaci. Vzít první nalezenou tabulku nevyexportovalo z ní nic.

Úrovní je tedy tabulka s nejvíce bundly, a při shodě vyhrává pozdější vrstva (nejdřív základní hra, pak aktualizace v pořadí názvů). Tabulky stejného názvu bez bundlů jsou její **doplňky**: jejich chunky se přidají k chunkům úrovně, protože drží největší mipy jejích textur. Hlavička textury pojmenovává tento chunk na +164 (viz [Textury a materiály](#textures-and-materials)). `levels` vypíše, odkud každá úroveň pochází a kolik má doplňků.

## Manifesty bundlů {#bundle-manifests}

První záznam bundlu je jeho manifest, uložený nekomprimovaně. Je to binární formát bundlu předchozích her Frostbite s novým magickým číslem `0xD68E799D`: počty, SHA-1, záznamy ebx a res (posun názvu a velikost), typy res, metadata a id, GUID chunků, řetězce. Zbylé záznamy bundlu jsou ebx, res a chunky v tomto pořadí. Kontrola: počty se shodují se záznamy na každém bundlu a řetězce začínají tam, kde končí záznamy.

Typy zdrojů jsou hashe. `0x49B156D4` je MeshSet (každý res tohoto typu se jmenuje `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` čte to vše pro jednu úroveň za několik sekund: úroveň má desítky bundlů a desítky tisíc ebx, res a chunků.

## Datové bloky {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Nulová komprimovaná velikost znamená uloženo, pokud se to dekomprimuje na stejnou velikost.

| Slovo metody | Kodek |
|---|---|
| `0x0070`, `0x0071` | žádný |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), z vlastní DLL `oo2core` hry) |
| jiné, se stejnými velikostmi | zkopírováno tak, jak je uloženo |
| jiné | odmítnuto |

Čteno ze správného balíčku se dekódoval každý vzorkovaný blok.

## Oddíly EBX {#ebx-partitions}

EBX drží všechno, co není surová data. Každý oddíl je soubor RIFF: `EBXD` (data, zarovnaná na 16), `EFIX` (GUID oddílu, GUID typů a podpisy, instance, posuny ukazatele, importů a informací o typech, importy, a posuny polí, řetězců a textů), `EBXX` (tabulka polí: posun, počet, hash, příznaky, typ prvku). Pole ukazatele má osm bajtů: nula je null, lichá hodnota je číslo importu `value >> 1`, cokoli jiného je relativní k poli.

**Knihovna typů se přečíst nedá.** Hra ji dodává v svém počátečním souborovém systému, který je šifrovaný, a tento balíček se ho nedotýká. Typy se poznávají podle GUID a podpisu, které každý oddíl nese, a těch pár typů, které export úrovně potřebuje, bylo rozloženo z dat.

## MeshSet {#meshset}

Mesh je res MeshSet (popis) a jeden chunk na každou úroveň detailu (buffery).

| Část | Rozložení |
|---|---|
| prefix | čtyři slova: velikost hlavičky (176 nebo 192), velikost záznamu úrovně (176 až 188), velikost záznamu sekce (368), 0 |
| hlavička | ohraničující kvádr; šest 64bitových posunů úrovní; typ meshe na `0x6C` (tuhý, skinovaný, složený); počty úrovní a sekcí na `0x9C` |
| úroveň | sekce na `+0x08`; pět seznamů kreslení na `+0x14` (neprůhledné, průhledné, dekál, jen hloubka, stín); formát indexů na `+0x54` (`0x21` u16, `0x2E` u32), bajty indexů a vrcholů; GUID chunku na `+0x74` |
| sekce | název materiálu; krok vrcholů; trojúhelníky, první index, posun vrcholů (v bajtech), počet vrcholů na `+0x20`; deklarace vrcholů na `+0x64`: 16 x (užití, formát, posun, proud), 16 kroků proudů, počty |
| chunk | buffer vrcholů, pak buffer indexů. Proudy jedné sekce jdou za sebou a indexy se počítají od prvního vrcholu sekce |

Pozice jsou užití 1, proud 0, posun 0, jako čtyři poloviční čísla nebo tři floaty. Kreslí se jen neprůhledné a průhledné sekce. Každá sekce pojmenovaná `..._shadow` je v seznamu stínů a jen v něm, takže rozhodují seznamy.

Kontrola: každý mesh úrovně, jejíž úrovně jsou uloženy v chunkech, se dekóduje, a téměř všechny mají 99 % nebo víc svých vrcholů uvnitř deklarovaného kvádru; zbytek mine kvůli zaokrouhlení poloviční přesnosti. Dekódovaná bedna měří asi metr, Y nahoru, s normálami směřujícími ven.

## Umístění {#placement}

Obsahový postup shromáždí statické objekty každé podoblasti do **skupiny statických modelů**: pole členů, jeden na mesh, každý se svými transformacemi instancí.

| Typ (GUID, podpis) | Rozložení |
|---|---|
| člen `ad13064e…`, `0xF861A878` | 224 bajtů: `+88` pole transformací, `+112` blueprint objektu (import), `+160` asset meshe (import) |
| transformace `101dce06…`, `0x5E6D8C37` | 64 bajtů: right, up, forward, translation, každý vec3 vycpaný na 16 |

Oddíl assetu meshe je pojmenován jako jeho res MeshSet, takže GUID oddílu importu dá mesh. Bod přistane na `x·right + y·up + z·forward + translation`. Transformace samotné skupiny byla v každé skupině zkontrolovaných úrovní identita a nepoužívá se.

Kontrola: v úrovni se každý člen každé skupiny přeloží na mesh; většina kopií má rotaci s determinantem 1 na tisícinu, zbytek je zmenšený nebo zrcadlený. GUID typů a podpisy jsou stejné v jiných úrovních. Herní aktualizace, která změní rozložení, změní podpis, a čtečka pak nic nenajde místo toho, aby to špatně přečetla.

### Objekty umístěné jeden po druhém {#objects-placed-one-by-one}

To, co postup nemůže seskupit (rozbitné objekty, kontejnery, trosky), se umísťuje přes **odkazy na objekty** a **odkazy na prefaby** v oddílech úrovně:

| Typ (GUID, podpis) | Rozložení |
|---|---|
| odkaz na objekt `a9a6a6ad…`, `0xC4856BEC` | `+32` transformace (jako výše), `+112` blueprint objektu (import) |
| odkaz na prefab `117c746e…`, `0xDE3FE9B4` | totéž; blueprint je prefab, oddíl dalších odkazů |

Prefaby se vnořují; kopie přistane na své vlastní transformaci krát transformace svého rodiče (řádkové vektory), až do osmi úrovní. Blueprint objektu se kreslí jako meshe, které importuje, s vynechanými zničenými stavy (`dc_...`). Seskupený prefab se odkazuje jako zbytek `..._nongroupable_autogen`, takže se nic nekreslí dvakrát.

Procházení začíná jen od světů a vrstev úrovně. Oddíl, jehož první instancí je blueprint prefabu (`134919fc…`, `0x0247807D`), je definice prefabu, a úroveň jich drží mnoho ve vlastní složce, umístěných svými světy jinými způsoby než těmito odkazy. Když by se procházel jako svět, prefab by své obsahy umístil v jeho lokálních souřadnicích. To nahromadí stovky kopií kolem počátku světa, hluboko pod zemí. Světy a vrstvy mají jako první `a10ebe0f…`, `0xD3D16C3C`.

Blueprinty odložené mimo hru se nesledují: vývojové a testovací assety (`game/dev/`, `test/`), sada závěrečné cutscény kola (`..._gameend_...`: odložená pod zemí) a řídicí jednotka mrtvého kamery (`.../deathflow/...`, jejíž prvky stojí v počátku světa). Rozpoznávají se podle cesty assetu, ne podle vrstvy: stejná vrstva, která drží sadu cutscény, může umisťovat skutečné zdi a střechy úrovně. Po obou pravidlech žádná kopie v kontrolovaných úrovních neleží víc než 10 m pod terénem a kopie stojí na terénu tam, kde je hra ukazuje.

**Úrovně detailu, které zastupují.** Poslední úroveň detailu meshe může přejít na vzdálenou náhradu s vlastním materiálem: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Mřížová věž o desítkách tisíc trojúhelníků může skončit siluetou o několika stovkách, kterou by rozpočet vybral a která zblízka vypadá jako pevný hrot. Úroveň detailu, která přináší takový materiál, který její nejjemnější úroveň nemá, se nikdy nevybere; nejhrubší úroveň meshe je poslední skutečná.

## Terén {#terrain}

Zdroj: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terén je res TerrainStreamingTree (typ `0x22FE8AC8`) a chunky, které pojmenovává.

| Část | Rozložení |
|---|---|
| hlavička | 34 bajtů; počet uzlů na 25 |
| rastrové stromy | bajt typu a u32 délka každý, dokud bajt typu není `0xFF`. Typ 0 je výšková mapa: vzorků na stranu na +5 (265), rozsah výšek na +21 (1,280 m), čtverec terénu v prvním záznamu uzlu na +77 (8,192 m v kontrolované úrovni). Drží ohraničující kvádry uzlů a mřížku min/max 16 x 16 na uzel, ne výšky |
| uzly streamování | kvadrotrí, do hloubky: velikost chunku a GUID; volitelný druhý chunk; bajt příznaků (bit 0: chunk začíná stránkou výšek); má potomky. Potomci v pořadí (0,0), (1,0), (1,1), (0,1) |
| stránka výšek | prvních 265 x 265 u16 chunku označeného uzlu, řádek po řádku; výška = hodnota x 1,280 / 65,535 m; sloupce podél x, řádky podél z, od nízkého rohu uzlu; okraj 4 vzorků, takže 256 buněk na uzel |

Každý krok byl kontrolován zvlášť:

- Parsování kvadrotrí uzlů spotřebuje res až do posledního bajtu, s deklarovanými 529 uzly.
- Sousední uzly sdílejí svých devět okrajových sloupců přesně, takže krok je 256.
- Vzorky potomka na každé druhé pozici se rovnají vzorkům jeho rodiče přesně při okraji 4 a liší se o 90 až 700 jednotek při jakémkoli jiném okraji.
- Nejnižší slovo v úrovni se dekóduje na nejnižší výšku ohraničujícího kvádru na centimetr.
- Z osmi způsobů, jak by čtverec mohl ležet na světě, jen x podél x a z podél z dává umístěným objektům smysl: polovina vzorkovaných kopií leží do asi 2 m, proti několikanásobku u všech ostatních.

Umístěné objekty pak výsledek měří. Nejnižší bod každé kopie oproti terénu pod ní (bilineárně, z nejjemnějšího uzlu):

| Umístěné | Mediánová vzdálenost | Znaménkový medián |
|---|---|---|
| stromy a keře | pod metr | těsně pod povrchem |
| rekvizity | metr nebo dva | na povrchu |
| skály | asi metr | zapuštěné asi o metr |
| budovy | několik metrů (stojí na základech) | mírně zapuštěné |

Vegetace se umisťuje na zem a nikam jinam, což z ní dělá nejostřejší kontrolu: její počátky leží mediánově 0.07 m od povrchu. Budovy se rozptylují široce, protože tato kategorie drží stěny, podlahy a montážní díly vícepatrových a podzemních staveb. Posun terénu o 64 m do strany sníží podíl kopií do 0.5 m z 29 % na 10 %.

`level` kreslí výškovou mapu jako `ground:terrain`, každou její část z nejjemnějšího uzlu s výškami tam a ne jemnější než `--ground-spacing` (ve výchozím nastavení 4 m: 3.7 milionu trojúhelníků pro kontrolovanou úroveň, jejíž nejjemnější uzly jsou 0.5 m). Kusy různého rozlišení se stýkají s malými schody; nic je nespojuje.

Chunk uzlu také drží stránky masek vrstev za svou stránkou výšek a jeho druhý chunk končí barevnou mapou uzlu (viz [Vrstvy terénu](#terrain-layers)).

## Vrstvy terénu {#terrain-layers}

Hra vykresluje terén tak, že mísí dlaždicované povrchové materiály podle namalovaných masek, s barevnou mapou nad nimi, a kreslí dekály (silnice, asfaltové záplaty, značení dráhy) navrch. Vlastní výklad systému od Frostbite (Widmark, „Terrain in Battlefield 3“, GDC 2012) uvádí rastry terénu jako výškovou mapu, masky míšení shaderu, barevnou mapu „použitou jako překryv nad míšením shaderem“, fyzikální materiály, masku hloubky ničení, albedo mapu pro odražené světlo a další kanály masek; dlaždice rastru nesou okraj pro vykreslovací algoritmy. Stromy rastrů sledovaných úrovní jsou sedm, s typy 0, 1, 2, 4, 5, 7 a 8, jejichž hlavičky začínají velikostí dlaždice: 265 pro výškovou mapu (typ 0) a typ 2, 72 nebo 66 pro masky (typ 1), 132 s okrajem 2 pro barevnou mapu (typ 4), 260 s okrajem 2 pro typ 5.

**Seznam vrstev.** Res `....layergraphs` terénu vypisuje jeden záznam po 32 bajtech na vrstvu, v pořadí, jak je čísluje záznamy masek (34 záznamů, 34 oddílů depa a indexů vrstev 0 až 33 v jedné úrovni). Id každého záznamu končí svým klíčem oddílu v depu shaderových bloků grafu vrstev (`....layergraphs_shaderblockdepot`), jehož blok pojmenovává mapy vrstvy: jednu mapu barvy `_cv`, mapy `_nhs` a `_ao` na povrch, plus sdílené detailní a šumové mapy. Mnoho vrstev nepojmenovává žádné mapy: jsou to zdroje, které čte graf vrstev. Barva vrstvy je průměr její mapy `_cv`; měřítko dlaždicování se nenajde. Asset terénu končí jedním pětibajtovým záznamem na vrstvu (bajt, pak u32 index vrstvy nebo -1).

**Masky.** Strom rastru 1 je kvadrotrí masek. Jeho tělo začíná 59 bajty, velikostí stránky na 0: 72 tam, kde jsou stránky BC4 (72 x 72, 2,592 bajtů), 66 tam, kde jsou nekomprimované osmibitové (4,356 bajtů). Potom následuje jedna skupina na uzel, do hloubky:

| Část | Rozložení |
|---|---|
| skupina | u16; u16 počet záznamů; u32 počet stránek; záznamy; nulový bajt. Skupina bez záznamů má celkem 7 bajtů |
| záznam | 33 bajtů: u16 vrstva, u16 hash, kvádr kvadrantu (čtyři floaty), dva bajty příznaků, 85bitová pyramida přítomnosti |

Záznamy skupiny jsou čtyři kvadranty jejího uzlu, vrstvu po vrstvě, kvadranty každé vrstvy v pořadí (0, 0), (1, 0), (1, 1), (0, 1). Záznam s druhým nastaveným příznakem pokrývá svůj kvadrant celý a nemá stránku; záznam bez něj má další stránku; kvadrant bez záznamu vrstvy, kterou jeho skupina jmenuje, je vůči té vrstvě prázdný; první příznak je vynulován přesně tehdy, když vrstva pokračuje ve skupině samotného kvadrantu, o úroveň níž, a ta ji tam nahrazuje. Počet stránek je počet záznamů se stránkou.

Stránky: za chunkem streamovaného uzlu následují stránky jeho vlastní skupiny, výšková stránka, 4,358bajtová 16bitová sekce a raster 67 x 67 po osmi bitech (od začátku chunku, pokud nemá výškovou stránku); jeho druhý chunk drží stránky čtyř kvadrantových skupin o úroveň níž, kvadranty v pořadí barevné mapy, a pak barevnou mapu. Stránka je 64 x 64 texelů kvadrantu, řádky podél z a sloupce podél x, s okrajem kopírovaným od sousedů: 4 texely u stránky BC4, 1 u nekomprimované. Kontrola: dvě stránky téže vrstvy vedle sebe musí nést texely hran toho druhého. `read_masks` to ověřuje pro každou dvojici, kterou umístí, a odmítne úroveň, kde se shoduje méně než 99 %. Asi třetina kontrolovaných úrovní se čte s okraji, které souhlasí; několik nemá malované masky; zbytek je odmítnut, skoro všechny kontrolou (chunky jejich uzlů drží víc, než tato struktura zná). Odmítnutá úroveň dostane barvu země jako střední barvu svých povrchových materiálů a export to řekne. Okraje, obrácené k plnému kvadrantu, jsou 255 a ty k prázdnému 0.

Nepřečtený zůstává 4,358bajtový úsek a raster 67 x 67 před stránkami: jeho hodnoty leží v úzkém vysokém pásmu, bez malých hodnot a bez strážního znaku.

**Barva země.** Graf vrstev mísí vrstvy v kompilovaném shaderovém grafu masek, sklonu, výšky a šumu, který se nečte. `--ground-texture` barví zemi pravidlem vlastním, a zde je řečeno, že je vlastní:

- vrstvy, jejichž barevná mapa je pojmenovaná pro vzdálenost, jsou zástupci pohledu zdaleka a vynechají se;
- texturované vrstvy pokrývající devět desetin terénu nebo víc tvoří základ. Jejich masky jsou skoro všude plné, takže to, kde která leží, volí shader, ne ony: ty pojmenované pro skálu nebo útes barví svahy strmější než 40 stupňů, ty pojmenované pro štěrk barví rovný terén (když žádné nejsou, pak ostatní základní vrstvy), a mezi 20 a 40 stupni se mísí podle sklonu výškové mapy (vzorkovaného po 4 m a bilineárně rozloženého přes texely zapečení: opakovaný v 4m blocích kreslil skalní barvu jako ostře ohraničené skvrny);
- každá jiná texturovaná vrstva se položí přes základ podle své masky, v pořadí vrstev;
- barevná mapa se položí přes výsledek tak, jak to dělá engine: dvojnásobek barvy země krát mapa, takže střední šedá ho nechá beze změny; kde barevná mapa nemá texely, země dostane střední jas mapy, v šedi.

Porovnáno s mediánovou barvou země na herních snímcích tří úrovní (chroma jako červená a modrá proti zelené): zapečená hrací plocha vychází 1.00 / 0.69 proti snímkům 1.19 / 0.78 u jedné, jejíž travnaté vrstvy jsou zelené tam, kde snímky ukazují suchou trávu; 1.19 / 0.82 proti 1.01 / 1.04 u jiné, jejíž barevná mapa sama je teplá (1.13 / 0.88); a 1.05 / 0.91 proti 0.93 / 0.92 u třetí bez barevné mapy. Snímky jsou osvětlené a barevně upravené, takže se tím měří odstín, ne jas.

**Barevná mapa.** Druhý chunk uzlu drží, za stránkami masek jeho kvadrantových skupin, čtyři stránky BC7 o 132 x 132 (každá 17,424 bajtů), jednu na kvadrant uzlu, v pořadí (nízké x, vysoké z), (vysoké x, vysoké z), (vysoké x, nízké z), (nízké x, nízké z). Strom masek říká, kolik bajtů berou stránky masek, takže barevná mapa se najde počtem, ne koncem chunku: v jedné úrovni nesou hrubší uzly za ní ještě čtyři takové stránky, další raster v jedné plné barvě, a čtení posledních čtyř stránek chunku ztratilo barevnou mapu přes devět desetin terénu. Bez tohoto počítání se barevná mapa také ztrácela v úrovních s nekomprimovanými stránkami masek, jejichž stránky nejsou celým počtem BC4; jedna úroveň přešla z 0.4 na 0.94 svého terénu. Pořadí bylo přizpůsobeno: proti hranám výškové mapy každého kvadrantu se každá stránka uzlů s rysy shoduje s jedním kvadrantem, nepřevrácená, na 0.3 až 0.54, kdežto nejlepší další umístění je pod 0.2. Podle něj poskládané se stránky úrovně spojí bez švu do silnic, vody a zastavěných ploch testovací úrovně, na 0.5 m na texel v hrací ploše. Tam, kde vrstvy dělají práci, je barevná mapa téměř neutrální (medián 110, 107, 104); jinde může nést plnou barvu. Úroveň, jejíž druhé chunky drží jen nekomprimované stránky masek, nemá přečtenou barevnou mapu. Dřívější kolo této čtečky tyto stránky nazvalo negeografickými: porovnávalo je s mapou pozadí, která může být úplně jiná krajina, a každou stránku kladlo na celý její uzel místo kvadrantu.

**Albedo pro odražené světlo** se hledalo a nenašlo: chunky kořenového a prvního uzlu jsou celé stránky masek, a data typu 5 nejsou nalezena.

**Díry.** Asset terénu úrovně (typ res `0x1CA38E06`) pojmenovává tři shadery: výchozí povrchový shader, shader děr a výchozí zdrojový shader. Která vrstva shader děr čte, se nenašlo, takže výšková mapa se nevyřezává. V jedné úrovni může navigační mesh běžet na skalních meshích desítky metrů pod výškovou mapou, kde je hra musela vyříznout. Hledalo se a nenašlo: maska vrstvy, raster 67 x 67, rezervovaná výška (žádná výšková stránka úrovně nedrží 0 ani 65,535) a příznak uzlu (každý uzel pod kořenem má příznaky 1). Zbývají stromy rastrů 7 a 8. Oba jsou kódované délkou běhu: bajt rovný tomu před ním následuje počtem dalších kopií (`ff ff 84` je 134 bajtů z 255). Strom 7 (dlaždice 256, úplný kvadrotrí o pěti úrovních, čtyři bity na vzorek) se dekóduje na dvojice bajtů s hodnotami 0 až 3; strom 8 (dlaždice 265) na bajty většinou 255, s ostatními hodnotami v pravidelných bězích. Dlaždice žádného z nich zatím nejsou umístěny, takže se o žádném nezná, že by držel díry.

**Dekály** se čtou a zapékají; viz [Dekály terénu](#terrain-decals).

## Dekály terénu {#terrain-decals}

Zdroj: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Silnice, dráhy, betonové plochy, malované čáry a písmena, stopy pneumatik: res `TerrainDecals` (typ `0x15E1F32E`) je drží jako plochou geometrii, kterou hra položí přes terén.

| Část | Rozložení |
|---|---|
| hlavička | na +16 počet slotů n, pak n 16bajtových slotů, pak počet záznamů |
| záznamy | jeden na dávku kreslení, za sebou, různé délky: 156 bajtů pevných polí — první vrchol na +32, počet trojúhelníků na +36, dlaždicování textury v metrech na +44 — pak bajty vrcholů dávky (posun, velikost), pak ocas, který pojmenovává její textury podle GUID oddílů jejich assetů |
| vrcholy | 32 bajtů: x, z (f32), 8 zabalených bajtů, u, v (f32), r, g, b, a (f16); každá dávka prostý seznam trojúhelníků |
| indexy | u32, počítané od 0 v každé dávce; nejsou potřeba |

Kontroly:

- rozsahy vrcholů záznamů na sebe navazují bez mezery a pokrývají všechny vrcholy přesně, a první vrchol každého záznamu krát 32 je jeho posun;
- tak přečtené jsou trojúhelníky kompaktní dekály (písmena, pásy čar, záplaty); přečtené o jeden vrchol mimo jsou to pruhy přes celou mapu;
- téměř každá dávka pojmenovává textury ve svém ocasu: mapu barvy (`_cv`) s mapou průhlednosti (`_op`, červený kanál), nebo u značení masku kanálů (`_rgb`).

Za texturovými GUID nese ocas materiálové parametry dávky, zakódované tak, jak je kódují bloky shaderu (viz Odstíny níže). Barva barvy značení, stopy pneumatiky nebo čáry je float3 s hashem `607e`: pískově 0.64, 0.56, 0.48 pro stopy pneumatik v písku, téměř černá pro dehet. Mapy průhlednosti jsou většinou formát 62, jeden kanál po 8 bajtech na blok, čtený jako BC4.

Dávka mapuje svou texturu buď podle světové pozice (u = x, v = z, textura se opakuje každých tiling-metrů: asfalt, beton, štěrk), nebo 0 až 1 přes dekál (čára, písmeno, stopa pneumatiky). Záznamy se kreslí v pořadí v souboru.

**Zapečení.** `level --ground-texture M` maluje pod rozsahem dekálů a dlaždicemi nejvýš 4,096 pixelů mapu barvy pozadí (bilineárně) a pak každou dávku přes ni podle své průhlednosti krát alfa vrcholu. Barva vrcholů se nepoužívá: některé vrcholy dávek jsou čistě zelené nebo modré, což by obarvilo značení úrovně těmito barvami. Trojúhelníky výškové mapy tam se stanou částmi `ground:terrain x<x> z<z>` nesoucími dlaždici. Každá dávka se kreslí takto:

| Dávka pojmenovává | Kreslí se jako |
|---|---|
| mapu barvy (`_cv`) | mapa, podle své mapy průhlednosti |
| mapu násobení (`_mult`) a mapu průhlednosti | barva (bílá, pokud ji materiál nejmenuje) krát mapa násobení, podle mapy průhlednosti: opotřebovaná středová čára dráhy, okrajové čáry a prahové pruhy |
| masku kanálů (`_rgb`) | barva, jinak bílá pro čáry a písmena, tmavá pro obrysy, mírné ztmavení pro opotřebení, stopy pneumatik, skvrny, kaluže a vlhkost, podle masky |
| samotnou mapu průhlednosti s barvou | barva podle mapy průhlednosti: stopy pneumatik |

Maska variací silnice není barva, ale mění povrch pod sebou, na stovky metrů, a nekreslí se, ať je jakkoli natřená: natřená bíle položila na svahy jedné úrovně dva bledé obdélníky dlouhé 150 až 250 m. Mapa `_mult` se bere jako vlastní opotřebení barvy, ne jako ztmavení země pod ní: je téměř bílá a tvar čáry je v mapě průhlednosti.

Téměř každá dávka se nakreslí do několika dlaždic na 0.5 m na pixel; export naroste o několik MB a zabere několik sekund navíc. Shora pohledem leží plochy, rulovací dráhy a síť silnic pod ploty a budovami kompaundů a vedou k jejich bránám.

Kdyby se dekály kreslily jako vlastní geometrie, potřebovaly by alfa prolínání, které zapisovač nenese, a odsazení nad terénem by s ním z-bojovalo; zapékání je udrží v barvě samotné země.

## Textury a materiály {#textures-and-materials}

Zdroj: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Res Texture (typ `0x6BDE20BA`) je 180bajtová hlavička: typ a formát pixelů na +8, šířka a výška na +22, počet mipů na +30, GUID chunku na +40, patnáct velikostí mipů na +56. Chunk je řetěz mipů, největší první. Některé chunky postrádají své největší mipy, které jsou v balíčku ve vysokém rozlišení, a délka chunku říká, od kterého mipu začíná. Chunk toho balíčku je pojmenován na +164; čte se z [doplňků](#which-table-is-the-level) úrovně, když je potřeba mip, který hlavní chunk nemá, a jeho délka plus délka hlavního chunku je celý řetěz.

| Formát | Dekóduje se jako | Důkaz |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineární) | barevný list plastové nádrže se dekóduje jako BC7; jako BC3 jsou stejné bajty šum |
| 61, 60 | BC3 | list bedny se čistě dekóduje jako BC3, ne jako BC1 nebo BC7 |
| 57, 56, 55 | BC1 | půl bajtu na pixel |

Asset meshe nepojmenovává žádnou texturu. Spojení je v **depech bloků shaderu** úrovně (typ res `0x73312045`, jedno na podoblast), klíčovaných osmi bajty na +0x130 záznamu sekce meshe:

| Část | Rozložení |
|---|---|
| tabulka, od 16 | (u64 klíč sekce, u64 posun popisovače), dokud posun nevypadne z res |
| popisovač | (u64 posun bloku, u64 hash, u64 velikost bloku) |
| blok | parametry shaderu sekce; každá textura je 49bajtový záznam: bajt, 16 bajtů, GUID oddílu assetu textury, její GUID instance |

Klíč sekce bedny se objeví jednou v každém z deseti depů podoblastí, které ji umisťují, a její blok pojmenovává `t_mil_crate_03_cs` a `_nmt` mezi sdílenými detailními mapami. Blok pojmenovává každou texturu, kterou shader vzorkuje, a která z nich je barevná mapa se neuvádí, takže se vybírá: 2D textura sRGB, jejíž název obsahuje většinu slov názvu materiálu (`M_ConcreteWall_01`: concrete, wall), pak názvu meshe, pak ta, která není detailní, dekál (`t_de_...`) nebo mapa poškození, a pak ta, kterou nejméně bloků používá. Blok dopravní značky pojmenovává její panel `t_com_highwaysignage_01_cs` a dekálový list `t_de_com_highwaysignage_01_ca` se štítem položeným na bok; oba odpovídají slovům, a bez pravidla o dekálu vyhrál list kvůli použití a značka ukazovala štít pootočený o čtvrtinu, přes všechny sady souřadnic textur, které sekce má. Podpisové vzdálenostní pole (`..._sdf`), palety a masky kanálů (`_rgb`) se nikdy nevybírají, ať sdílejí jakákoli slova (`_rgba` mapy ano: většina je barevná s alfou, a jejich vynechání vyměnilo vlastní mapy vedení elektrického vedení a schodiště za cizí); vegetační atlas pozadí `..._atlas_a_sdf`, kreslený jako barva, ukázal černé a bílé hvězdičky místo stromů, paleta budov pozadí konfety vzorků pro zdi, a skleněné trosky kreslené přes masku kanálů vyšly tyrkysově. Sekce, jejíž jediní kandidáti jsou sdílené detailní mapy, zůstane plošně obarvená.

**Palety.** Budovy pozadí berou své barvy z palety, 256 x 256 texelů po čtvercích 16 x 16: každý vrchol nese čtyři bajty (užití `0x1E`), jejichž první dva říkají, kde v paletě je jeho barva, x a y z 255. `level` kreslí takovou sekci s paletou jako texturou, každý vrchol ve středu jejího čtverce. Tak nakreslené bloky pozadí úrovně vyjdou jako pastelové zdi, terakota a tmavá okna tam, kde byly prostě bílé.

**Překryvy.** Velké objekty dlaždí střižný list přes své první souřadnice textury a položí přes něj překryv přes druhé, které leží v 0 až 1: rozbalení celého objektu. Překryv (`..._overlay_cs`, s maskou `..._overlay_a`) nese, jak objekt vypadá zdaleka, například červené pruhy a rez nádrže na olej; nakreslené jen se střižným listem vyšly nádrže jedné úrovně jako šedé panely. Sekce, jejíž blok pojmenovává překryv s maskou a jejíž druhé souřadnice jsou takovým rozbalením, se kreslí s překryvem přes ně (36 sekcí v té úrovni).

**Odstíny.** Mnoho barevných map je šedých (průměry jejich kanálů jsou do 6 % od sebe navzájem): shader je maluje barvami z parametrů bloku. Za svými texturovými položkami (každá 49 bajtů) blok vypisuje své parametry, každý s typovou značkou (`f11af825` float3, `a5e1f2de` float4, `c1b1a014` float, `4a4fc3a1` celé číslo), bajty příznaků `01 80` pro jednu hodnotu, dvoubajtový hash názvu parametru, u32 počet, hodnotu a osmibajtové id. Názvy se neukládají. Sedm hashů názvů float3 funguje jako odstíny: v jedné úrovni drží tři z nich barvu asi v 1 bloku ze 6, jehož mapa je šedá a skoro nikdy tam, kde mapa má vlastní barvu, a ostatní drží barvy, kterými se šedá mapa maluje, když to říká název materiálu (modrý lem mostu `..._blue`: 0.047, 0.098, 0.171 proti neutrálním 0.5). Rodina může držet několik hodnot, jednu na kanál masky, většina neutrální, a hodnota s kanálem blízkým nule (čistě zelená na cihlových fasádách) vybírá kanál masky, nemaluje. `level` násobí šedou barevnou mapu v lineárním světle první hodnotou každé rodiny, která není neutrální ani takovým výběrovým kanálem, proti její neutrální hodnotě, a výsledek drží jako vlastní texturu; mapa s barvou se nechá beze změny. Pravidlo je vlastní exportéru: který kanál masky dostane který odstín, se nečte. V jedné úrovni snížilo podíl trojúhelníků konstrukce kreslených poblíž bílé z 19.4 % na 3.9 %.

**Varianty objektů.** Jeden mesh se umisťuje v několika vzhledech: zeď skladu s červeným nebo modrým pruhem a jiným číslem namalovaným na ní, kontejner v zelené nebo šedé. Každá umístěná kopie pojmenovává svůj vzhled:

| Kde | Pole |
|---|---|
| člen skupiny statických modelů | +32: pole jednoho ukazatele na kopii, na variantu objektu nebo null |
| odkaz na objekt | +120: ukazatel na variantu objektu nebo null |
| varianta objektu (oddíl `ov_...`, typ `235f2a9c...`) | u její první instance +32: u32 hash názvu varianty |

Vzhled sekce ve variantě je blok shaderu klíčovaný klíčem sekce s přičteným hashem varianty do prvních čtyř bajtů jako little-endian u32 (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); sekce bez bloku pod tímto klíčem vypadá ve všech variantách stejně. Databáze variant meshů úrovně (`meshvariationdb_win32`) vypisuje pro každý mesh a hash varianty materiály, kterých se varianta dotýká, ale ne klíče: pravidlo bylo nalezeno z klíčů samotných a platí pro každou sekci s variantami, která byla zkontrolována (čtyři varianty jedné zdi, tři její sekce každá). Blok varianty přináší své vlastní textury i odstíny: malované číslo na zdi je písmenový list, který blok varianty pojmenovává. Velký podíl seskupených kopií je umístěn v nějaké variantě.

Blok se zapéká jednou pro každou sadu obsahu a položka depa pro klíč nese hash jejich obsahu (druhé u64 položky). Kde sekce nemá blok pod klíčem své varianty, varianta k ní dojde přes *dvojče*: jinou sekci, jejíž výchozí blok má stejný obsah a který jeden mít. Bez dvojčat by stěna, jejíž délky sdílejí jeden výchozí blok, mohla vyjít ve dvou barvách. Sekce bez vlastní varianty vezme variantu, kterou má většina jejích dvojčat.

**Ničitelné meshe.** Mesh, který může zápas srazit, má vedle sebe destrukční asset vlastního jména (`.../br_x.destruction` pro `.../br_x_mesh`): rozbitné budovy a zdi (`br_`) a mnoho rekvizit. `level` drží jejich povrchy v částech vlastních, pojmenovaných ` (destructible)`, jejichž uzly glTF nesou `{"destructible": true}`. Jejich zničené stavy jsou meshe `dc_..._part<N>_mesh` vedle nich, každý vycentrovaný na svůj vlastní počátek; kde která část sedí, je v destrukčním assetu, který se nečte, takže zničené stavy se neexportují.

**Vynechané.** Sekce zástupných blokovacích materiálů (`M_Whitebox`: několik velkých netexturovaných trojúhelníků, které si některé budovy nechávají vedle svých povrchů, vyčnívaly z úrovně jako bílé ploutve), meshe vyrobené pro cutscény (vrtulník umístěný tam, kde začíná jeho scéna) a pomocné světelné prvky (roviny, které blokují světlo, nikdy se nekreslí). Vygenerované budovy pozadí úrovně (`..._generated_blueprints_..._mesh`) se kreslí, ale jejich stěnové materiály pojmenovávají jen šumové mapy a jejich vrcholy nenesou barvu, takže zůstávají prosté. Téměř každá nakreslená sekce dostane barevnou mapu.

**Listy s nápisy.** Namalované číslo na zdi nebo potisk billboardu na jeřábu je sekce vlastní, jejíž barevná mapa je list (`_ca`): alfa písmene přes plnou barvu, nebo potisk. Její první souřadnice textury dlaždicují omítku zdi přes panel (u -0.2 až 1.7 na jedné zdi), což list nakreslí skoro dvakrát; čtvrtá sada (`0x24`, jinak třetí, `0x23`) ho položí přesně jednou (u -1 až 0, v 1 až 2, několik tisícin přes v hrubších úrovních detailu). Kde první sada nechává jednu kopii obrázku a čtvrtá nebo třetí leží v rozmezí jedné, list se kreslí přes tu sadu, přesunutý do 0 až 1. List s alfou se kreslí 1 cm před povrch, na který je namalován, který se kreslí pod ním v druhé barvě bloku přes první sadu: bez toho prázdné texely listu ukazovaly vnitřek zdi. Druhá sada je rozbalení objektu pro jeho překryv a tady se nepoužívá.

**Výřezové mapy.** Čtvrtý kanál barevné mapy znamená různé věci podle názvu mapy. V `_cs`, zdaleka nejčastější (893 z vybraných map jedné úrovně), je to hladkost: 1 % alfy mediánové mapy leží do 0.1 od 0 nebo 1. V `_cu` (listí, tráva) a `_ca` (barva a alfa) je to průhlednost: 90 % a 87 %. Barevná mapa pojmenovaná `..._cu` nebo `..._ca`, jejíž alfa je alespoň z 75 % blízko 0 nebo 1, alespoň z 1 % pod 0.5 a alespoň z 5 % nad ním, se zapisuje s alfou jako PNG a její materiál jako glTF `alphaMode` MASK, `alphaCutoff` 0.5, oboustranně; listové karty pak ukazují listí, ne jeho černé rohy. List stromu, který nemá žádnou alfu (nejvýš 4 z 255), je vyříznut geometrií: jeho listy se řežou geometrií, a s jen prvními dvěma podmínkami byla celá koruna vyříznuta pryč.

Souřadnice textur jsou vrcholový užitek `0x21`, dvě poloviční čísla (formát 6), nebo dva floaty (formát 2). Sekce nesou až tři další sady (`0x22` až `0x24`) pro dekálové a detailní vrstvy. Souřadnice se dlaždicují: vnější strana žebrování kontejneru běží od -1.6 do 1.8, dlaždice pozadí terénu leží celé mimo 0..1, a v jedné úrovni leží 23 % texturovaných trojúhelníků částečně mimo 0..1. Zapisují se tak, jak jsou, s opakujícím se vzorkovačem; prohlížeč 3DHeat každou opakující se texturu zabalí do atlasu. Renderer, který je místo toho ořezává, rozmáže žebra na dvojnásobnou šířku, promění betonovou podlahu v pruhy podél jedné osy a dá ocelovým nosníkům věže barvu okraje jejich textury; pro něj `--clamped-uvs` rozřeže každý trojúhelník podél čar, kde se jeho textura opakuje, a přesune každý kus do 0..1 (viz [Výstupní formát](output-format.md)). Potom 0.03 % texturovaných trojúhelníků, přes které se textura opakuje víc než 16krát, leží mimo, a trojúhelník, který by řezání rozdělilo na víc než 4 kusy, se kreslí v průměrné barvě své textury: kůra se opakuje podél každé větve, a rozřezané, stromy úrovně vzrostly z 6.4 na 24 milionů trojúhelníků.

Výškové mapě chybí vlastní barevná mapa, kterou by bylo možné přečíst. Kde ji pokrývá některá z barevných map pozadí terénu, je obarvena z ní: souřadnice textur pozadí jsou lineární funkcí světového x a z (99 % vrcholů v rozmezí 0.001 od ní; mapa pokrývá čtverec 65,536 m, otočený o čtvrt otáčky), a táž funkce dává souřadnice výškové mapy. Úroveň dodává mipy té mapy od 2,048 px dolů, takže výšková mapa dostane 32 m na pixel. Její tmavá skála leží na strmé zemi: korelace tmavosti se sklonem je 0.48 a nejvýš 0.34 pro sedm dalších orientací.

Jiné pozadí úrovně je osm blízkých a osm vzdálených dlaždic kolem hrací plochy, každá opakuje svou vlastní texturu přes dlaždici a žádná nedosáhne na výškovou mapu. Každá textura pozadí se přizpůsobí sama, a když žádná nepokrývá výškovou mapu, vezme průměrnou barvu, kterou pozadí ukazuje do jednoho kilometru od čtverce terénu, a `--ground-texture` na ni zapéká dekály. Materiál pozadí je ten, jehož název obsahuje `TerrainBackdrop`, nebo `BD_` a `Terrain` (`M_BD_<site>_Terrain..._Near`); nebo mesh pozadí (`bd_..._terrain<site>_04_far_mesh`) nese prostý materiál terénu (`M_<region>_Terrain<site>_04_Far`), který první dvě pravidla v jedné úrovni minula, a tak barvilo svou zem z jejích povrchů.

Tam, kde žádná mapa pozadí výškovou mapu nepokrývá, však vezme střední barvu vlastních povrchů terénu, než průměr pozadí: barevné mapy `_cv`, které pojmenovávají shaderové bloky jeho grafu vrstev (27 v jedné úrovni: písky, štěrky, půdy, tráva, popraskaný beton), každá zprůměrovaná, pak medián každého kanálu, bez výchozího povrchu motoru. Pozadí může být úplně jiná krajina: v jedné úrovni jeho průměr (95, 99, 80 v sRGB) obarvil zemi hrací plochy šedě, jak ji hra neukazuje. S `--ground-texture` se ta barva násobí dvojnásobkem barevné mapy, což střední šedá nechá beze změny, a zapéká se s dekály přes obojí, rozsah dekálů i barevné mapy.

Proti hře: mediánová barva země zapečené hrací plochy každé úrovně a herních snímků (řádky 55 až 72 % obrazu vedle HUD, 24 snímků každý; sRGB; snímky jsou osvětlené a barevně upravené, takže poměry r/g a b/g jsou férové srovnání):

| Úroveň | Snímky | Průměr pozadí | Nyní |
|---|---|---|---|
| první | 167, 140, 109 (1.19, 0.78) | 95, 99, 80 (0.96, 0.81) | 117, 108, 86 (1.08, 0.80) |
| druhá | 72, 71, 74 (1.01, 1.04) | 117, 110, 104 (1.06, 0.95) | 146, 135, 117 (1.08, 0.87) |
| třetí | 83, 89, 82 (0.93, 0.92) | 160, 148, 136 (1.08, 0.92) | 148, 137, 117 (1.08, 0.85) |

První je opravena; zbylé dvě byly před tím v odstínu o trochu blíž. Jedna barva pro celou úroveň nemůže být všude správná; správné by byly masky.

## Navigační mesh {#navigation-mesh}

Zdroj: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Úroveň dodává jeden oddíl na agenta, `<level>/dbt/<level>_navmesh_layer_<n>`: u jedné úrovně je vrstva 0 voják (1.8 m vysoký, krok 0.18 m, poloměr 0.4 m) a dvě další jsou vozidla (3.5 a 10 m vysoká). Každý oddíl drží dvě pole:

| Pole | Prvek |
|---|---|
| dlaždice | 28 bajtů: u32 0, u32 hash, u32 0, u32 index chunku, u16 x dlaždice, u16 z dlaždice, u32 posun, u32 velikost |
| chunky | 20 bajtů: GUID chunku, u32 velikost |

Dlaždice je `size` bajtů na `offset` v chunku `chunk index`, little-endian, a rozložená jako u Detouru (Recast Navigation) za delší hlavičkou:

| Posun | Obsah |
|---|---|
| 0 | `VAND`, verze 7 |
| 24 | počty: polygony, vrcholy, spoje, detailní meshe, detailní vrcholy, detailní trojúhelníky, uzly objemů ohraničení, spoje mimo mesh, první polygon mimo mesh |
| 188 | výška agenta, krok, poloměr |
| 200 | ohraničující kvádr dlaždice, šest floatů |
| 232 | vrcholy: x, y, z floaty, světové souřadnice |
| další 8bajtová hranice | polygony, 32 bajtů: u32, šest u16 indexů vrcholů, šest u16 sousedů, u16 příznaky, počet vrcholů na +30, na +31 plocha (spodních šest bitů) a druh (horní dva) |
| pak nabitě | spoje (16 bajtů), detailní meshe (12: první detailní vrchol u32, první detailní trojúhelník u32, počet vrcholů a trojúhelníků u8), detailní vrcholy (tři floaty), detailní trojúhelníky (tři indexy a příznaky), uzly objemů ohraničení (16), spoje mimo mesh (80) |

V každé dlaždici kontrolovaných úrovní tyto součty dávají velikost dlaždice přesně na bajt, a detailní meshe číslují polygony před prvním polygonem mimo mesh.

Polygon je mezi svými rohy plochý; jeho **detailní mesh** drží skutečnou výšku povrchu přes boule, skály a schody, a ten se kreslí. Index detailního trojúhelníku pod počtem rohů polygonu je ten roh, jinak detailní vrchol `first + index - corners`. Vějířování polygonů místo toho dá pod terén mnohem víc trojúhelníků a dlouhé třísky; s detailními meshi není žádná delší než úhlopříčka dlaždice 16 m plus schod do svahu.

Druh 0 je země, druh 2 malé strmé záplaty (asi 45 stupňů, každá čtvereční metr), druh 1 spoj mezi povrchy: jeho rohy zaberou 125 m výšky nebo víc a leží mimo dlaždici, některé v počátku. Spoje se vynechají; zbytek se kreslí svými detailními meshi, nebo se vějířuje v dlaždici bez nich.

Kontroly: součty velikostí chunků přesně odpovídají dlaždicím; každý vrchol povrchu leží v kvádru své dlaždice s tolerancí asi jednoho metru; téměř všechny trojúhelníky směřují nahoru. Dlaždice, která neprojde, se odmítne a spočítá, a v té úrovni žádná neprošla.

Co pokrývá mesh vojáka, shora pohledem v testovací úrovni: zem, podlahy, schody a některé střechy, a ne vrchy nákladních kontejnerů. Je to mapa AI o tom, kde může voják stát, nejblíž tomu, kde hráči stojí, co soubory ukazují.

## Neimplementováno {#not-implemented}

- Graf vrstev terénu, který mísí jeho povrchové vrstvy (viz [Vrstvy terénu](#terrain-layers)): barva země se řídí pravidlem této čtečky z masek vrstev a sklonu výškové mapy, a úrovně, jejichž stránky masek nesedí k sobě, dostanou jednu barvu.
- Barevné parametry materiálů dekálů: značení přes masky kanálů se maluje neutrální barvou.
- Blueprinty objektů, které nejsou meshe (herní logika, efekty, zvuky).
- Zničené stavy ničitelných meshů: jejich místa jsou v destrukčním assetu, který se nečte.
- Spoje navigačního meshe (skoky, žebříky, přelezy) a jeho vrstvy vozidel.
- Úrovně meshe uložené přímo v res (10 meshů v úrovni, gadgety), kosti a části skinovaných a složených meshů, a normály (počítá je zapisovač).
- Normálové, drsnostní a jiné mapy; průhlednost jiná než výřez (sklo a průhledné dekály se kreslí neprůhledně).
- Díry terénu: shader děr je pojmenován, ale co čte, se nenašlo (viz [Vrstvy terénu](#terrain-layers)), takže výšková mapa se nevyřezává tam, kde pod ní běží pochozí země.
- Který odstín patří ke kterému kanálu masky materiálu: šedá barevná mapa vezme první odstín, který není neutrální (viz [Textury a materiály](#textures-and-materials)).
- Efekty (cesty `fx/`) a kabelové meshe, jejichž ohraničující kvádry mají desítky kilometrů; vynechají se a počítají se v souhrnu.
- Poškozený tvar XOR obfuskované tabulky.
