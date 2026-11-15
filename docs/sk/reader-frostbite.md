---
title: "Frostbite: `.toc`, `.cas`, zväzky, siete a levely"
nav_order: 5
lang: "sk"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, zväzky, siete a levely {#frostbite-toc-cas-bundles-meshes-and-levels}

**Číta level Battlefield 6 až po jeho terén, umiestnené siete a ich farebné mapy
a zapíše ho ako `.glb`.** Hry Frostbite (Battlefield, Need for Speed, Dead Space)
držia obsah v blobách `.cas`, opísaných tabuľkami obsahu `.toc`. Tabuľka levelu
hovorí, ktoré zväzky level načíta, zväzky pomenúvajú každé aktívum a aktíva hovoria,
ktorá sieť kde stojí.

Zdroje:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabuľky, balíky, užitočné zaťaženie),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(zväzky a ich manifesty),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(oddiely EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(výškové pole),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(textúry a materiály),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(umiestnenie a export).
Príkazy: `identify`, `levels`, `level` (pozri [Príkazy](commands.md#levels-and-level-frostbite)).

Hra o ničom z tohto nedokumentuje. Každé rozloženie nižšie bolo prečítané zo
súborov a potom overené voči všetkým z nich, a každá časť hovorí, aká bola
kontrola. Kde Frosty modding nástroje opisujú staršie verzie štruktúry, názvy polí
nasledujú ich; žiaden kód sa z nich nepreberal (pozri [Pravidlá a licencie](rules-and-licences.md)).

## Hlavička, ktorá vyzerá zašifrovane a nie je {#the-header-that-looks-encrypted-and-is-not}

| Magická hodnota (u32, little-endian) | Význam | Spracovanie |
|---|---|---|
| `0x00CED100` | obyčajný: strom začína hneď | číta sa |
| `0x01CED100` | podpísaný: podpis 556 bajtov, potom strom **v čistom texte** | číta sa |
| `0x03CED100` | XOR-zaslepený, s kľúčom v hlavičke samotného súboru | rozpoznaný a odmietnutý |

Podpísaná forma je to, čo dodáva súčasný Battlefield. Bajty s vysokou entropiou
za magickou hodnotou sú podpis, nie šifrový text.

## Strom DbObject {#the-dbobject-tree}

Jedna rekurzívna štruktúra. Každé pole je bajt typu (nižších päť bitov je typ,
bit 7 znamená "anonymný"), voliteľný názov a hodnota. Kontajnery nesú svoju dĺžku
ako premenlivo dlhé celé číslo a končia nulovým bajtom. `parse_toc` kontroluje
dĺžku každého kontajnera, takže súbor, ktorý sa dá prečítať, bol pochopený.
`layout.toc` je v tejto forme.

## Inštalačné balíky {#installation-packages}

Každé umiestnenie pomenúva **inštalačný balík**, ku ktorému jeho blob patrí. Každý
balík čísluje svoje bloby od `cas_01`, takže číslo blobu samo osebe je nejednoznačné,
len čo je nainštalovaných viac balíkov, a to je vždy.

- `layout.toc` vymenúva balíky pod `installManifest.installChunks`, každý s `persistentIndex` a `installBundle`, napríklad `Win32/installation/<package>`.
- Blobs balíka sú v tom priečinku, pod `Data` pre základnú hru alebo pod `Update/<pack>/Data` pre to, čo prišlo neskôr.
- Záznam umiestnenia nesie plný 32-bitový `persistentIndex`: nízka polovica jeho prvého slova drží vysokú polovicu, vysoká polovica jeho druhého slova nízku polovicu; nízka polovica druhého slova je číslo blobu.

Kontrola: každé umiestnenie v každej binárnej tabuľke každej inštalácie sa
rozlíši na deklarovaný balík a leží vnútri blobu, ktorý pomenúva. Skoršia verzia
zobrala prvý `cas_NN.cas` správneho čísla. Tretina užitočných zaťažení, ktoré
čítala, vyzerala potom ako vysoká entropia a bola považovaná za šifrovanie. Boli
to správne offsety v zlom súbore. Nič nájdené nie je zašifrované.

## Tabuľka levelu {#the-level-table}

Tabuľka levelu (`levels/<level>/<level>.toc`) je tabuľka sekcií: pätnásť
hlavičkových slov big-endian, potom sekcie uložené jedna za druhou, ktorých
offsety sú uvedené aj odvoditeľné z dvoch počtov.

| Sekcia | Obsah |
|---|---|
| zväzky | tabuľka hashov (jedno slovo každý), potom 16-bajtový záznam na zväzok: kľúč, `0x40000000` \| veľkosť, 0, offset |
| hašovacia tabuľka blokov | jedno slovo na blok |
| bloky | 16-bajtové id (GUID bloku **v opačnom bajtovom poradí**), potom slovo: `0x80000000` \| 4 x index jeho umiestnenia |
| umiestnenia | štyri big-endian slová: balík (rozdelený), blob, offset, veľkosť |

Id blokov a umiestnenia sú **v rozdielnom poradí**. Čítanie v poradí súboru
spáruje každý blok s bajtami iného bloku, ktoré sa dekódujú úplne dobre (väčšinou
ako zvuk), a preto to nevyzerá zle, kým sa sieť nezmení na šum. Kontrola: v leveli
sú indexové slová permutáciou od 0 po počet blokov mínus jeden.

Zväzky sú uložené vnútri za tabuľkou sekcií. Každý má deväť big-endian hlavičkových
slov, potom svoje položky: osem bajtov offsetu a veľkosti, pred ktorými je ďalších
osem bajtov balíka a blobu, keď má bajt príznaku horný bit nastavený. Kontrola: na
každom zväzku sa posledná položka končí presne tam, kde začínajú bajty príznakov.

### Ktorá tabuľka je level {#which-table-is-the-level}

Level môže mať viacero tabuliek s rovnakým názvom: jednu v `Data` základnej hry, jednu
v každej aktualizácii (`Update/<pack>/Data`), ktorá ho dodá alebo zmení, a jednu v
každom balíku vysokého rozlíšenia (`Update/<pack>/Data/Win32/installation/detail/<package>/...`).
Len niektoré obsahujú zväzky. Pre level, ktorý dodá aktualizácia, tabuľka v základnej
hre drží len bloky a žiadne zväzky a tabuľka v aktualizácii je level; zobrať prvú
nájdenú tabuľku nevyexportovalo z neho nič.

Level je teda tabuľka s najviac zväzkami, pričom v remíze vyhráva neskoršia vrstva
(najprv základná hra, potom aktualizácie podľa názvu). Tabuľky s rovnakým názvom bez
zväzkov sú jeho **doplnky**: ich bloky sa pridajú k blokom levelu, lebo držia
najväčšie mipy jeho textúr. Hlavička textúry pomenúva tento blok na +164 (pozri
[Textúry a materiály](#textures-and-materials)). `levels` vypíše, odkiaľ každý level
pochádza a koľko má doplnkov.

## Manifesty zväzkov {#bundle-manifests}

Prvá položka zväzku je jeho manifest, uložený nekomprimovaný. Je to binárny formát
zväzku predošlých hier Frostbite s novou magickou hodnotou `0xD68E799D`: počty,
SHA-1, záznamy ebx a res (offset a veľkosť názvu), typy res, metadáta a id, GUID
blokov, reťazce. Ostatné položky zväzku sú ebx, res a bloky v tomto poradí. Kontrola:
počty sa zhodujú s položkami na každom zväzku a reťazce začínajú tam, kde končia záznamy.

Typy zdrojov sú hashe. `0x49B156D4` je MeshSet (každý res tohto typu sa volá
`..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` prečíta toto všetko pre jeden level za pár sekúnd: level má
desiatky zväzkov a desaťtisíce záznamov ebx, res a blokov.

## Bloky užitočného zaťaženia {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

Nulová komprimovaná veľkosť znamená uložené, pokiaľ sa to dekomprimuje na seba.

| Slovo metódy | Kodek |
|---|---|
| `0x0070`, `0x0071` | žiadny |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), z vlastnej DLL `oo2core` hry) |
| iné, s rovnakými veľkosťami | skopírované tak, ako sú uložené |
| iné | odmietnuté |

Čítané z správneho balíka sa dekódovalo každé vzorkované užitočné zaťaženie.

## Oddiely EBX {#ebx-partitions}

EBX drží všetko, čo nie sú surové dáta. Každý oddiel je súbor RIFF:
`EBXD` (dáta, zarovnané na 16), `EFIX` (GUID oddielu, GUID typov a podpisy,
inštancia, offsety ukazovateľov, importov a informácií o type, importy, a offsety
poľa, zabalenej hodnoty a reťazca), `EBXX` (tabuľka polí: offset, počet, hash,
príznaky, typ prvku). Pole ukazovateľa má osem bajtov: nula je null, nepárna hodnota
je číslo importu `value >> 1`, inak je relatívna k poľu.

**Knižnica typov sa nedá prečítať.** Hra ju dodáva v svojom počiatočnom súborovom
systéme, ktorý je zašifrovaný, a tento balík sa ho nedotýka. Typy sa poznajú podľa
GUID a podpisu, ktoré každý oddiel nesie, a pár typov, ktoré export levelu
potrebuje, sa rozložilo z dát.

## MeshSet {#meshset}

Sieť je res MeshSet (popis) a jeden blok na každú úroveň detailu (buffre).

| Časť | Rozloženie |
|---|---|
| prefix | štyri slová: veľkosť hlavičky (176 alebo 192), veľkosť záznamu úrovne (176 až 188), veľkosť záznamu sekcie (368), 0 |
| hlavička | ohraničujúci kváder; šesť i64 offsetov úrovní; typ siete na `0x6C` (pevná, kostrová, zložená); počty úrovní a sekcií na `0x9C` |
| úroveň | sekcie na `+0x08`; päť zoznamov kreslenia na `+0x14` (nepriehľadné, priehľadné, nálepky, len hĺbka, tieň); formát indexov na `+0x54` (`0x21` u16, `0x2E` u32), bajty indexov a vrcholov; GUID bloku na `+0x74` |
| sekcia | názov materiálu; krok vrcholu; trojuholníky, prvý index, offset vrcholu (v bajtoch), počet vrcholov na `+0x20`; deklarácia vrcholov na `+0x64`: 16 x (použitie, formát, offset, prúd), 16 krokov prúdov, počty |
| blok | buffer vrcholov, potom buffer indexov. Prúdy sekcie idú jeden za druhým a indexy sa počítajú od prvého vrcholu sekcie |

Pozície sú použitie 1, prúd 0, offset 0, ako štyri polovičné alebo tri float čísla.
Kreslia sa len nepriehľadné a priehľadné sekcie. Každá sekcia pomenovaná
`..._shadow` je v zozname tieňov a len tam, takže rozhodujú zoznamy.

Kontrola: každá sieť levelu, ktorého úrovne sú uložené v blokoch, sa dekóduje, a
takmer všetky majú 99 % alebo viac vrcholov v deklarovanom kvádri; zvyšok mimo
o zaokrúhlenie polovičnej presnosti. Dekódovaná debna meria asi meter, Y hore, s
normálami smerujúcimi von.

## Umiestnenie {#placement}

Obsahový postup zbiera statické objekty každého podsveta do **skupiny statických
modelov**: pole členov, jeden na sieť, každý so svojimi transformáciami inštancií.

| Typ (GUID, podpis) | Rozloženie |
|---|---|
| člen `ad13064e…`, `0xF861A878` | 224 bajtov: `+88` pole transformácií, `+112` plán objektu (import), `+160` aktívum siete (import) |
| transformácia `101dce06…`, `0x5E6D8C37` | 64 bajtov: pravá, horná, predná, posunutie, každé vec3 vyplnené na 16 |

Import GUID oddielu aktíva siete dáva sieť, lebo oddiel sa volá ako jeho res
MeshSet. Bod pristane na `x·right + y·up + z·forward + translation`. Transformácia
samotnej skupiny bola v každej skupine skontrolovaných levelov identita a neaplikuje
sa.

Kontrola: v leveli sa každý člen každej skupiny rozlíši na sieť; väčšina kópií má
rotáciu s determinantom 1 na tisícinu, zvyšok je škálovaný alebo zrkadlený. GUID
typov a podpisy sú rovnaké v iných leveloch. Aktualizácia hry, ktorá zmení
rozloženie, zmení podpis a čítač potom nenájde nič namiesto toho, aby čítal nesprávne.

### Objekty umiestnené jednotlivo {#objects-placed-one-by-one}

Čo postup nedokáže zoskupiť - ničiteľné objekty, kontajnery, trosky - sa umiestni
cez **odkazy na objekty** a **odkazy na prefaby** v oddieloch levelu:

| Typ (GUID, podpis) | Rozloženie |
|---|---|
| odkaz na objekt `a9a6a6ad…`, `0xC4856BEC` | `+32` transformácia (ako vyššie), `+112` plán objektu (import) |
| odkaz na prefab `117c746e…`, `0xDE3FE9B4` | to isté; plán je prefab, oddiel ďalších odkazov |

Prefaby sa vnárajú; kópia pristane na svojej transformácii vynásobenej transformáciou
svojho rodiča (vektory riadkov), až do ôsmich úrovní. Plán objektu sa kreslí ako
siete, ktoré importuje, s vynechaním zničených stavov (`dc_...`). Zoskupený prefab
sa odkazuje ako svoj zvyšok `..._nongroupable_autogen`, takže sa nič nekreslí dvakrát.

Prechod začína len od svetov a vrstiev levelu. Oddiel, ktorého prvá inštancia je
plán prefabu (`134919fc…`, `0x0247807D`), je definícia prefabu, a level ich drží
veľa pod svojím priečinkom, umiestnených svojimi svetmi inými spôsobmi než týmito
odkazmi; prejdený ako svet, prefab uloží svoj obsah na jeho lokálne súradnice. To
nahromadí stovky kópií okolo počiatku sveta, hlboko pod zemou. Svety a vrstvy majú
ako prvé `a10ebe0f…`, `0xD3D16C3C`.

Plány vyradené z hry sa nesledujú: vývojové a testovacie aktíva (`game/dev/`, `test/`),
sada koncovej scény kola (`..._gameend_...`: postavená pod zemou) a kontrolér kamery
smrti (`.../deathflow/...`, ktorého prvky stoja na počiatku sveta). Rozpoznávajú sa
podľa cesty aktíva, nie podľa vrstvy: tá istá vrstva, ktorá drží sadu koncovej scény,
môže umiestniť skutočné steny a strechy levelu. Po oboch pravidlách žiadna kópia
v skontrolovaných leveloch neleží hlbšie než 10 m pod terénom a kópie stoja na
terénu, kde ich hra ukazuje.

**Úrovne detailu, ktoré zastupujú.** Posledná úroveň detailu siete sa môže prepnúť
na vzdialený záložný obraz s vlastným materiálom: `M_LastLod`, `M_Billboard`,
`M_Vista`, `M_ProjectionLod`. Mriežková veža s desiatkami tisíc trojuholníkov môže
skončiť siluetou niekoľkých stoviek, ktorú rozpočet vyberie a ktorá zblízka je
plný hrot. Úroveň detailu, ktorá zavedie takýto materiál, ktorý jej najjemnejšia
úroveň nemá, sa nikdy nevyberie; najhrubšia úroveň siete je posledná skutočná.

## Terén {#terrain}

Zdroj: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terén je res TerrainStreamingTree (typ `0x22FE8AC8`) a bloky, ktoré pomenúva.

| Časť | Rozloženie |
|---|---|
| hlavička | 34 bajtov; počet uzlov na 25 |
| stromy rastrov | bajt typu a u32 dĺžka každý, až kým bajt typu nie je `0xFF`. Typ 0 je výškové pole: vzorky na strane na +5 (265), rozsah výšok na +21 (1 280 m), štvorec terénu v prvom zázname uzla na +77 (8 192 m v skontrolovanom leveli). Drží kvádre uzlov a pyramídu min/max 16 x 16 na uzol, nie výšky |
| uzly streamingu | kvadrantový strom, do hĺbky: veľkosť bloku a GUID; voliteľný druhý blok; bajt príznakov (bit 0: blok začína stránkou výšok); má potomkov. Potomkovia v poradí (0,0), (1,0), (1,1), (0,1) |
| stránka výšok | prvých 265 x 265 u16 bloku označeného uzla, riadok po riadku; výška = hodnota x 1 280 / 65 535 m; stĺpce pozdĺž x, riadky pozdĺž z, od nízkeho rohu uzla; okraj 4 vzorky, takže 256 buniek na uzol |

Každý krok sa kontroloval samostatne:

- Parsovanie kvadrantového stromu uzlov spotrebuje res až do posledného bajtu, s deklarovanými 529 uzlami.
- Susedné uzly zdieľajú presne svojich deväť okrajových stĺpcov, takže krok je 256.
- Vzorky dieťaťa na každej druhej pozícii sa presne rovnajú vzorkám rodiča s okrajom 4 a s akýmkoľvek iným okrajom sa líšia o 90 až 700 jednotiek.
- Najnižšie slovo v leveli dekóduje na najnižšiu výšku ohraničujúceho kvádra na centimeter.
- Z ôsmich spôsobov, ako môže štvorec ležať na svete, len x pozdĺž x a z pozdĺž z dáva umiestneným objektom zhodu: polovica vzorkovaných kópií do asi 2 m, oproti niekoľkonásobku pre každý iný spôsob.

Umiestnené objekty potom výsledok merajú. Najnižší bod každej kópie oproti
terénu pod ňou (bilineárne, z najjemnejšieho uzla):

| Umiestnené | Mediánová vzdialenosť | Mediánová so znamienkom |
|---|---|---|
| stromy a kry | pod meter | tesne pod povrchom |
| rekvizity | meter alebo dva | na povrchu |
| skaly | asi meter | zapustené asi o meter |
| budovy | niekoľko metrov (stoja na základoch) | mierne zapustené |

Vegetácia sa umiestňuje len na zem a nikde inde, čo je najostrejšia kontrola:
jej počiatky sú v mediáne 0,07 m od povrchu. Budovy sa rozptyľujú široko, lebo
kategória drží steny, podlahy a stavebné prvky viacpodlažných a podzemných
stavieb. Posunutie terénu o 64 m do strany zníži podiel kópií do 0,5 m z 29 % na 10 %.

`level` kreslí výškové pole ako `ground:terrain`, každú jeho časť z najjemnejšieho
uzla s výškami tam a nie jemnejšiu než `--ground-spacing` (predvolene 4 m: 3,7
milióna trojuholníkov pre skontrolovaný level, ktorého najjemnejšie uzly sú 0,5 m).
Kúsky rozdielneho rozlíšenia sa stretávajú s malými schodmi; nič ich nespája.

Blok uzla tiež drží stránky masiek vrstiev za svojou stránkou výšok, a jeho druhý
blok končí farebnou mapou uzla (pozri [Vrstvy terénu](#terrain-layers)).

## Vrstvy terénu {#terrain-layers}

Hra tieni terén pri hráčovi tak, že splatuje povrchové materiály dlaždicovaním
podľa namaľovaných masiek, s farebnou mapou nad nimi, a kreslí nálepky (cesty,
asfaltové záplaty, značenia ranvejí) navrchu. Výklad systému od Frostbite
(Widmark, "Terrain in Battlefield 3", GDC 2012) vymenúva rastre terénu:
výškové pole, masky splatovania shaderom, farebnú mapu "použitú ako prekrytie nad
splatovaním shaderom", fyzikálne materiály, masku hĺbky ničenia, albedo mapu pre
odrazené svetlo a dodatočné kanály masiek; bloky rastra nesú okraj pre renderovacie
algoritmy. Stromy streamingu skontrolovaných levelov majú sedem stromov rastrov,
typovaných 0, 1, 2, 4, 5, 7 a 8, ktorých hlavičky začínajú svojou veľkosťou dlaždice:
265 pre výškové pole (typ 0) a typ 2, 72 alebo 66 pre masky (typ 1), 132 s okrajom 2
pre farebnú mapu (typ 4), 260 s okrajom 2 pre typ 5.

**Zoznam vrstiev.** Res `....layergraphs` terénu vymenúva jednu položku po 32 bajtoch
na vrstvu, v poradí, v akom ju číslujú záznamy masiek (34 položiek, 34 sekcií depa
a indexy vrstiev 0 až 33 v jednom leveli); id každej položky končí jej kľúčom
sekcie v depe shader blokov layer grafu (`....layergraphs_shaderblockdepot`), ktorého
blok pomenúva mapy vrstvy: jednu mapu `_cv` farby, mapy `_nhs` a `_ao` na povrch,
plus spoločné mapy detailu a šumu. Mnohé vrstvy nepomenúvajú žiadne mapy: sú to
zdroje, ktoré layer graf číta. Farba vrstvy je priemer jej mapy `_cv`; mierka
dlaždicovania sa nenachádza. Aktívum terénu končí jednou päťbajtovou položkou na
vrstvu (bajt, potom u32 index vrstvy alebo -1).

**Masky.** Strom rastra 1 je kvadrantový strom masiek. Jeho telo začína 59 bajtami,
veľkosťou stránky na 0: 72, keď sú stránky BC4 (72 x 72, 2 592 bajtov), 66, keď sú
nekomprimované osembitové (4 356 bajtov). Potom nasleduje jedna skupina na uzol,
do hĺbky:

| Časť | Rozloženie |
|---|---|
| skupina | u16; u16 počet záznamov; u32 počet stránok; záznamy; nulový bajt. Skupina bez záznamov má 7 bajtov |
| záznam | 33 bajtov: u16 vrstva, u16 hash, ohraničujúci kváder kvadrantu (štyri floaty), dva bajty príznakov, 85-bitová pyramída prítomnosti |

Záznamy skupiny sú štyri kvadranty jej uzla, vrstva po vrstve, kvadranty každej
vrstvy v poradí (0,0), (1,0), (1,1), (0,1). Záznam s nastaveným druhým príznakom
pokrýva svoj kvadrant celý a nemá stránku; bez neho má ďalšiu stránku; kvadrant bez
záznamu vrstvy, ktorú jeho skupina pomenúva, je prázdny pre túto vrstvu; prvý príznak
je vynulovaný presne vtedy, keď vrstva pokračuje v skupine samotného kvadrantu o
úroveň nižšie, čo ju tam nahrádza. Počet stránok je počet záznamov so stránkou.

Stránky: po stránkach skupiny vlastného uzla v jeho bloku nasleduje stránka výšok,
16-bitová sekcia 4 358 bajtov a raster 67 x 67 s osembitovými hodnotami (od začiatku
bloku, ak nemá stránku výšok); jeho druhý blok drží stránky štyroch skupín
kvadrantov o úroveň nižšie, kvadranty v poradí farebnej mapy, potom farebnú mapu.
Stránka je 64 x 64 texelov kvadrantu, riadky pozdĺž z a stĺpce pozdĺž x, s okrajom
skopírovaným zo susedov: 4 texely na stránke BC4, 1 na nekomprimovanej.

Okraje dokazujú umiestnenie bez úsudku: dve stránky jednej vrstvy vedľa seba musia
niesť navzájom svoje okrajové texely. `read_masks` to kontroluje pre každý pár, ktorý
umiestni, a odmietne level, kde sa zhoduje menej než 99 %. Asi tretina
skontrolovaných levelov sa číta, s okrajmi, ktoré sa zhodujú; niekoľko nemá
namaľované masky; zvyšok sa odmietne, takmer všetko kontrolou (ich bloky uzlov
držia viac, než tento rozklad pozná). Zem odmietnutého levelu dostane stredovú
farbu svojich materiálov povrchu a export povie prečo. Okraje obrátené k plnému
kvadrantu sú 255 a k prázdnemu 0.

Surová sekcia 4 358 bajtov a raster 67 x 67 pred stránkami sa nečítajú: ich
hodnoty sedia v úzkom vysokom pásme, bez malých hodnôt a bez strážcu.

**Farba zeme.** Layer graf mieša vrstvy v skompilovanom grafe shaderu z masiek,
sklonu, výšky a šumu, a ten sa nečíta. `--ground-texture` farbí zem podľa vlastného
pravidla čítača, tu uvedeného ako také:

- vrstvy, ktorých farebná mapa je pomenovaná pre vzdialenosť, sú zástupné obrazy ďalekého pohľadu a vynechávajú sa;
- texturované vrstvy pokrývajúce deväť desatín terénu alebo viac sú základ. Ich masky sú takmer všade plné, takže kde každá leží, je voľba shaderu, nie ich: tie pomenované pre skalu alebo útes farbia svahy strmšie než 40 stupňov, tie pomenované pre štrk farbia rovnú zem (ostatné základné vrstvy, ak žiadne nie sú), a medzi 20 a 40 stupňami sa miešajú podľa sklonu výškového poľa (berie sa každé 4 m a rozprestrie bilineárne cez pečené texely: opakované v blokoch po 4 m kreslilo skalnú farbu ako ostré škvrny s hranami);
- každá iná texturovaná vrstva sa položí na základ podľa vlastnej masky, v poradí vrstiev;
- farebná mapa sa položí na výsledok tak, ako to robí engine: dvojnásobok farby zeme vynásobený mapou, takže pološedá ju necháva tak, ako je; kde farebná mapa nemá texely, zem dostane medián jasu mapy, v šedej.

Porovnané s mediánovou farbou zeme z hernych snímok troch levelov (chróma ako
červená a modrá voči zelenej): pečená herná oblasť vychádza 1,00 / 0,69 oproti
snímkam 1,19 / 0,78 v jednom, kde sú trávne vrstvy zelené tam, kde snímky ukazujú
suchú trávu; 1,19 / 0,82 oproti 1,01 / 1,04 v druhom, kde je sama farebná mapa teplá
(1,13 / 0,88); a 1,05 / 0,91 oproti 0,93 / 0,92 v treťom bez farebnej mapy. Snímky sú
osvetlené a gradované, takže toto meria odtieň, nie jas.

**Farebná mapa.** Druhý blok uzla drží po stránkach masiek svojich skupín kvadrantov
štyri stránky BC7 po 132 x 132 (každá 17 424 bajtov), jednu na kvadrant uzla, v
poradí (nízke x, vysoké z), (vysoké x, vysoké z), (vysoké x, nízke z), (nízke x,
nízke z). Strom masiek hovorí, koľko bajtov zaberajú stránky masiek, takže farebná
mapa sa nájde počtom, nie koncom bloku: v jednom leveli hrubšie uzly nesú za ňou
ešte štyri takéto stránky, ďalší raster v jednej plochej farbe, a čítanie posledných
štyroch stránok bloku stratilo farebnú mapu na deviatich desatinách terénu. Bez tohto
počtu sa farebná mapa minula aj v leveloch s nekomprimovanými stránkami masiek,
ktorých stránky nie sú celým počtom stránok BC4; farebná mapa jedného levelu sa
zlepšila z 0,4 na 0,94 svojho terénu. Poradie sa určilo fitovaním: oproti okrajom
výškového poľa každého kvadrantu každá stránka uzlov s prvkami sa zhoduje s jedným
kvadrantom, nepreklopená, na 0,3 až 0,54, kde ďalšie najlepšie umiestnenie je pod
0,2. Podľa neho sa stránky levelu spájajú bez švu do ciest, vôd a zastavaných oblastí
testovacieho levelu, na 0,5 m na texel v hernej oblasti. Tam, kde vrstvy robia prácu,
je farebná mapa takmer neutrálna (medián 110, 107, 104); inde môže niesť plnú farbu.
Level, ktorého druhé bloky držia len nekomprimované stránky masiek, nemá prečítanú
farebnú mapu. Skorší pokus tohto čítača nazýval tieto stránky nezemepisné: porovnával
ich s mapou pozadia, ktorá môže byť úplne inou krajinou, a každú stránku umiestňoval
na celý uzol namiesto kvadrantu.

**Albedo pre odrazené svetlo** sa hľadalo a nenašlo: bloky koreňových a prvých
uzlov sú celé stránky masiek a dáta typu 5 nie sú nájdené.

**Diery.** Aktívum terénu levelu (res typu `0x1CA38E06`) pomenúva tri shadery:
predvolený povrchový shader, shader dier a predvolený zdrojový shader. Ktorú vrstvu
číta shader dier, sa nenašlo, takže výškové pole sa nevyrezáva. V leveli môže navigačná
sieť bežať na skalných sieťach desiatky metrov pod výškovým poľom, kde ich hra musela
odrezať. Hľadalo sa tam a nenašlo: maska vrstvy, raster 67 x 67, rezervovaná výška
(žiadna stránka výšok levelu nedrží 0 ani 65 535) a príznak uzla (každý uzol pod
koreňom má príznaky 1). Zostávajú stromy rastrov 7 a 8. Obe sú kódované behovou dĺžkou:
bajt rovnaký ako ten pred ním nasleduje počet ďalších kópií (`ff ff 84` sú 134 bajtov
z 255). Strom 7 (dlaždica 256, úplný kvadrantový strom piatich úrovní, štyri bity na
vzorku) sa dekóduje na páry bajtov s hodnotami 0 až 3; strom 8 (dlaždica 265) na bajty
prevažne 255, s ostatnými hodnotami v pravidelných behoch. Ani jedna dlaždica sa zatiaľ
neumiestňuje, takže ani jedna sa nedá označiť, že drží diery.

**Nálepky** sa čítajú a pečú; pozri [Nálepky terénu](#terrain-decals).

## Nálepky terénu {#terrain-decals}

Zdroj: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Cesty, ranvoje, betónové plochy, namaľované čiary a písmená, stopy pneumatík: res
`TerrainDecals` (typ `0x15E1F32E`) ich drží ako plochú geometriu, ktorú hra prekladá
cez terén.

| Časť | Rozloženie |
|---|---|
| hlavička | na +16 počet slotov n, potom n 16-bajtových slotov, potom počet záznamov |
| záznamy | jeden na dávku kreslenia, za sebou, rôznej dĺžky: 156 bajtov pevných polí - prvý vrchol na +32, počet trojuholníkov na +36, dlaždicovanie textúry v metroch na +44 - potom bajty vrcholov dávky (offset, veľkosť), potom chvost, ktorý pomenúva jej textúry podľa GUID oddielov ich aktív |
| vrcholy | 32 bajtov: x, z (f32), 8 zabalených bajtov, u, v (f32), r, g, b, a (f16); každá dávka je obyčajný zoznam trojuholníkov |
| indexy | u32, počítané od 0 v každej dávke; nepotrebné |

Kontroly:

- rozsahy vrcholov záznamov nasledujú jeden za druhým bez medzery a pokrývajú všetky vrcholy presne, a prvý vrchol každého záznamu krát 32 je jeho offset;
- takto prečítané, trojuholníky sú kompaktné nálepky (písmená, pásy čiar, záplaty), kým jeden vrchol mimo nich ich urobí pruhmi cez mapu;
- takmer každá dávka pomenúva textúry vo svojom chvoste: farebnú mapu (`_cv`) s mapou nepriehľadnosti (`_op`, červený kanál), alebo pri značeniach masku kanálov (`_rgb`).

Za GUID textúr nesie chvost materiálové parametre dávky, zakódované tak, ako ich
kóduje blok shadera (pozri Odtiene nižšie). Farba namaľovaného značenia, stopy
pneumatiky alebo čiary je float3 hashovaný `607e`: piesočnatá 0,64, 0,56, 0,48 pre
stopy pneumatík v piesku, takmer čierna pre decht. Mapy nepriehľadnosti sú väčšinou
formátu 62, jeden kanál s 8 bajtmi na blok, čítaný ako BC4.

Dávka mapuje svoju textúru buď podľa pozície vo svete (u = x, v = z, textúra sa
opakuje každých dlaždicovacích metrov: asfalt, betón, štrk), alebo 0 až 1 cez nálepku
(čiara, písmeno, stopa pneumatiky). Záznamy sa kreslia v poradí súboru.

**Pečenie.** `level --ground-texture M` maľuje pod rozsahom nálepiek a dlaždicami
najviac 4 096 pixelov farebnú mapu pozadia (bilineárne) a potom každú dávku nad ňu
podľa jej nepriehľadnosti × alfa vrcholu. Farba vrcholov sa nepoužíva: niektoré vrcholy
dávok sú čisto zelené alebo modré, čo zafarbilo značenia levelu do týchto farieb.
Trojuholníky výškového poľa tam sa stanú časťami `ground:terrain x<x> z<z>` nesúcimi
dlaždicu. Každá dávka kreslí takto:

| Dávka pomenúva | Kreslí sa ako |
|---|---|
| farebnú mapu (`_cv`) | mapa, podľa jej mapy nepriehľadnosti |
| mapu násobenia (`_mult`) a mapu nepriehľadnosti | farba (biela, ak materiál nič nepomenúva) vynásobená mapou násobenia, podľa mapy nepriehľadnosti: opotrebovaná stredová čiara ranvoja, okrajové čiary a prahové pruhy |
| masku kanálov (`_rgb`) | farba, inak biela pre čiary a písmená, tmavá pre obrysy, mierne stmavenie pre opotrebovanie, stopy pneumatík, škvrny, mláky a vlhkosť, podľa masky |
| samotnú mapu nepriehľadnosti s farbou | farba podľa mapy nepriehľadnosti: stopy pneumatík |

Mapa variácie cesty nie je farba, ale mení povrch pod ňou, na stovky metrov, a
nekreslí sa, nech je jej farba akákoľvek: namaľovaná na biela položila dva bledé
obdĺžniky dlhé 150 až 250 m na svahoch levelu. Mapa `_mult` sa berie ako vlastné
opotrebovanie farby, nie ako stmavenie zeme pod ňou: je takmer biela a tvar čiary je
v mape nepriehľadnosti.

Takmer každá dávka sa kreslí do niekoľkých dlaždíc na 0,5 m na pixel; export
narastie o niekoľko MB a trvá o pár sekúnd dlhšie. Pohľadom zhora ležia plochy,
dráhy a sieť ciest pod plotmi a budovami areálov a vedú k ich bránam.

Nakreslené ako vlastná geometria by nálepky potrebovali alfa prelínanie, ktoré
zapisovač nenesie, a posun nad terénom by s ním bojoval o hĺbku; pečenie ich drží
vo farbe samotnej zeme.

## Textúry a materiály {#textures-and-materials}

Zdroj: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

Res Texture (typ `0x6BDE20BA`) je 180-bajtová hlavička: typ a formát pixelov na +8,
šírka a výška na +22, počet mipov na +30, GUID bloku na +40, pätnásť veľkostí mipov
na +56. Blok je reťazec mipov, najväčší prvý. Niektoré bloky nemajú svoje najväčšie
mipy, ktoré sa dodávajú v balíku vysokého rozlíšenia, a dĺžka bloku hovorí, od
ktorého mipu začína. Blok toho balíka je pomenovaný na +164; číta sa z
[doplnkov](#which-table-is-the-level) levelu, keď sa chce mip, ktorý hlavný blok
nemá, a jeho dĺžka plus dĺžka hlavného bloku je celý reťazec.

| Formát | Dekódovaný ako | Dôkaz |
|---|---|---|
| 67, 66 | BC7 (sRGB, lineárne) | farebný plech plastovej nádrže sa dekóduje ako BC7; ako BC3 sú tie isté bajty šum |
| 61, 60 | BC3 | plech debny sa čisto dekóduje ako BC3, nie ako BC1 ani BC7 |
| 57, 56, 55 | BC1 | pol bajtu na pixel |

Aktívum siete nepomenúva žiadnu textúru. Prepojenie je v **depách blokov shadera
levelu** (typ res `0x73312045`, jedno na podsvet), kľúčované osmimi bajtami na +0x130
záznamu sekcie siete:

| Časť | Rozloženie |
|---|---|
| tabuľka, na 16 | (kľúč sekcie u64, offset deskriptora u64), až kým offset nevypadne z res |
| deskriptor | (offset bloku u64, hash u64, veľkosť bloku u64) |
| blok | parametre shadera sekcie; každá textúra je 49-bajtový záznam: bajt, 16 bajtov, GUID oddielu aktíva textúry, GUID inštancie |

Kľúč sekcie debny sa objaví raz v každom z desiatich depí podsvetov, ktoré ju
umiestňujú, a jej blok medzi zdieľanými mapami detailu pomenúva `t_mil_crate_03_cs`
a `_nmt`. Blok pomenúva každú textúru, ktorú shader vzorkuje, a ktorá je farebná
mapa, sa nehovorí, takže sa vyberá: sRGB 2D textúra, ktorej názov obsahuje väčšinu
slov názvu materiálu (`M_ConcreteWall_01`: concrete, wall), potom názvu siete, potom
taká, ktorá nie je detail, nálepka (`t_de_...`) ani mapa poškodenia, potom tá, ktorú
používa najmenej blokov. Blok dopravnej značky pomenúva jej panel
`t_com_highwaysignage_01_cs` a plech nálepky `t_de_com_highwaysignage_01_ca` so
štítom položeným na bok; obe sedia na slová, a bez pravidla o nálepke vyhral plech
podľa použitia a značka ukázala štít otočený o štvrtinu, cez každú sadu UV, ktorú
sekcia má. Mapy signálnych vzdialeností (`..._sdf`), palety a masky kanálov (`_rgb`)
sa nikdy nevyberajú, nech zdieľajú čokoľvek; mapy `_rgba` sa vyberajú (väčšina je
farba s alfou, a ich vynechanie vymenilo vlastné mapy vedenia a schodiska za cudzie);
atlas vegetácie pozadia `..._atlas_a_sdf` kreslený ako farba ukázal čierne a biele
hviezdy na stromoch, paleta budov pozadia konfety vzoriek na stenách a sklený úlomok
kreslený cez svoju masku kanálov vyšiel tyrkysovo. Sekcia, ktorej jediní kandidáti
sú zdieľané mapy detailu, zostane plochofarebná.

**Palety.** Budovy pozadia berú svoje farby z palety, 256 x 256 texelov v
swatchoch 16 x 16: každý vrchol nesie štyri bajty (použitie `0x1E`), z ktorých prvé
dva hovoria, kde v palete je jeho farba, x a y z 255. `level` kreslí takúto sekciu
s paletou ako jej textúrou, každý vrchol v strede svojho swatchu. Tak nakreslené
bloky pozadia levelu vyjdú ako pastelové steny, terakota a tmavé okná tam, kde boli
čisto biele.

**Prekrytia.** Veľké objekty dlaždicujú tradičný list cez svoje prvé súradnice
textúry a položia prekrytie navrch cez druhé, ktoré ležia v 0 až 1: rozbalenie celého
objektu. Prekrytie (`..._overlay_cs`, s maskou `..._overlay_a`) nesie to, ako objekt
vyzerá zďaleka, pruhy a hrdzu na olejovej nádrži; nakreslené len s listom, nádrže
jedného levelu vyšli ako šedé panely. Sekcia, ktorej blok pomenúva prekrytie s jeho
maskou a ktorej druhé súradnice sú takým rozbalením, sa kreslí s prekrytím cez ne
(36 sekcií v tom leveli).

**Odtiene.** Mnohé farebné mapy sú šedé (priemery ich kanálov sú do 6 % od seba):
shader ich maľuje farbami z parametrov bloku. Za svojimi textúrnymi záznamami (po 49
bajtoch) blok vymenúva svoje parametre, každý typovou značkou (`f11af825` float3,
`a5e1f2de` float4, `c1b1a014` float, `4a4fc3a1` celé číslo), bajtmi príznakov `01 80`
pre jednu hodnotu, dvojbajtovým hashom názvu parametra, u32 počtom, hodnotou a
osmibajtovým id. Názvy sa neukladajú. Sedem float3 názvových hashov pôsobí ako odtiene:
v jednom leveli tri z nich držia farbu asi v 1 bloku zo šiestich, ktorého mapa je
šedá a takmer nikdy tam, kde mapa má vlastnú farbu, a ostatné držia farby, ktorými sa
šedá mapa maľuje, keď to hovorí názov materiálu (modrá lišta mosta
`..._blue`: 0,047, 0,098, 0,171 oproti neutrálnemu 0,5). Rodina môže obsahovať
viacero hodnôt, jednu na kanál masky, väčšinu neutrálnych, a hodnota s kanálom blízko
ničoho (čistá zelená na tehlových fasádach) vyberá kanál masky, nemaľuje. `level`
násobí šedú farebnú mapu v lineárnom svetle prvou hodnotou každej rodiny, ktorá nie
je neutrálna ani takýto výber, oproti jej neutrálnej, a výsledok drží ako vlastnú
textúru; mapa s farbou sa nechá tak, ako je. Pravidlo je exportérovo vlastné: ktorý
kanál masky dostane ktorý odtieň, sa nečíta. V jednom leveli sa tým podiel
trojuholníkov konštrukcie kreslených takmer bielych znížil z 19,4 % na 3,9 %.

**Variácie objektov.** Jedna sieť sa umiestňuje vo viacerých vzhľadoch: stena
skladu s červeným alebo modrým pruhom a iným číslom namaľovaným na nej, kontajner v
zelenej alebo sivej. Každá umiestnená kópia pomenúva svoj vzhľad:

| Kde | Pole |
|---|---|
| člen skupiny statického modelu | +32: pole jedného ukazovateľa na kópiu, na variáciu objektu alebo null |
| odkaz na objekt | +120: ukazovateľ na variáciu objektu alebo null |
| variácia objektu (oddiel `ov_...`, typ `235f2a9c...`) | jeho prvá inštancia +32: u32 hash názvu variácie |

Vzhľad sekcie vo variácii je blok shadera kľúčovaný kľúčom samotnej sekcie s
hashom variácie pripočítaným k jej prvým štyrom bajtom, ako little-endian u32
(`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); sekcia bez bloku pod
týmto kľúčom vyzerá vo všetkých variáciách rovnako. Tabuľky variácií siete levelu
(`meshvariationdb_win32`) vymenúvajú na sieť a hash variácie materiály, ktorých sa
variácia dotýka, ale nie kľúče; pravidlo sa našlo z samotných kľúčov a platí pre
každú sekciu s variantmi, ktorú sa podarilo skontrolovať (štyri variácie jednej steny,
tri jej sekcie). Blok variácie prináša vlastné textúry aj svoje odtiene: namaľované
číslo na stene je sada písmen, ktorú pomenúva blok variácie. Veľký podiel zoskupených
kópií je umiestnených vo variácii.

Blok sa pečie raz pre každý súbor obsahu a záznam depa pre kľúč nesie hash z nich
(druhý u64 záznamu). Kde sekcia nemá blok pod kľúčom svojej variácie, variácia sa
k nej stále dostane cez *dvojča*: inú sekciu, ktorej predvolený blok má rovnaký
obsah a takýto blok má. Bez dvojčiat sa stena, ktorej dĺžky zdieľajú jeden predvolený
blok, môže vyjsť v dvoch farbách. Sekcia bez vlastnej variácie berie variant, ktorý
väčšina jej dvojčiat.

**Ničiteľné siete.** Sieť, ktorú môže zápas zborit, má vedľa seba aktívum ničenia
rovnakého názvu (`.../br_x.destruction` pre `.../br_x_mesh`): zničiteľné budovy a steny
(`br_`) a mnohé rekvizity. `level` drží ich povrchy v časťach vlastných, pomenovaných
s ` (destructible)`, ktorých uzly glTF nesú `{"destructible": true}`. Ich zničené stavy
sú uzly `dc_..._part<N>_mesh` vedľa nich, každý vycentrovaný na vlastný počiatok;
kde ktorá časť sedí, je v aktíve ničenia, ktoré sa nečíta, takže zničené stavy sa
neexportujú.

**Vynechané.** Sekcie plánovaných placeholder materiálov (`M_Whitebox`: pár veľkých
netexturovaných trojuholníkov, ktoré niektoré budovy držia pri svojich povrchoch a
ktoré z levelu trčali ako biele plutvy), siete vyrobené pre filmové scény (vrtuľník
umiestnený, kde začína jeho scéna) a pomocné osvetľovacie objekty (roviny, ktoré blokujú
svetlo, nikdy sa nekreslia). Generované budovy pozadia levelu
(`..._generated_blueprints_..._mesh`) sa kreslia, ale ich steny majú materiálové
názvy s len šumovými mapami a ich vrcholy nenesú farbu, takže zostávajú obyčajné.
Takmer každá nakreslená sekcia dostane farebnú mapu.

**Tabuľky písmen.** Namaľované číslo na stene alebo tlač na billboarde žeriava je
samostatná sekcia, ktorej farebná mapa je tabuľka (`_ca`): alfa písmena nad plnou
farbou, alebo tlač. Jej prvé súradnice textúry dlaždicujú omietku steny cez panel
(u -0,2 až 1,7 na jednej stene), čo tabuľku nakreslí takmer dvakrát; štvrtá sada
(`0x24`, inak tretia, `0x23`) ju položí presne raz (u -1 až 0, v 1 až 2, pár tisícin
navyše v hrubších úrovniach detailu). Kde prvá sada nechá jednu kópiu obrazu a štvrtá
alebo tretia leží do jednej, tabuľka sa kreslí cez ňu, presunutá do 0 až 1. Tabuľka s
alfou sa kreslí 1 cm pred povrchom, na ktorý je namaľovaná, ktorý sa kreslí pod ňou v
inej farebnej mape bloku cez prvú sadu: bez toho prázdne texely tabuľky ukázali vnútro
steny. Druhá sada je rozbalenie objektu pre jeho prekrytie a tu sa nepoužíva.

**Výrezové mapy.** Štvrtý kanál farebnej mapy znamená iné veci podľa názvu mapy. V
`_cs` je to, zďaleka najčastejšie (893 z vybraných máp jedného levelu), hladkosť: 1 %
alfy mediánovej mapy leží v rozsahu 0,1 od 0 alebo 1. V `_cu` (lístie, tráva) a `_ca`
(farba a alfa) je to nepriehľadnosť: 90 % a 87 %. Farebná mapa pomenovaná `..._cu` alebo
`..._ca`, ktorej alfa je aspoň z 75 % blízko 0 alebo 1, aspoň 1 % pod 0,5 a aspoň 5 %
nad ním, sa zapíše s alfou ako PNG a jej materiál ako glTF `alphaMode` MASK,
`alphaCutoff` 0.5, obojstranný; karty listov potom ukazujú lístie, nie ich čierne rohy.
Jedna listová mapa stromu nemá žiadnu alfu (najviac 4 z 255): jej vetvy sú vystrihnuté
geometriou, a pri len prvých dvoch podmienkach zmizla celá koruna.

Súradnice textúry sú vrcholový použitie `0x21`, dve polovičné (formát 6) alebo dve
float (formát 2). Sekcie nesú až tri ďalšie sady (`0x22` až `0x24`) pre nálepkové a
detailné vrstvy. Súradnice sa dlaždicujú: vnútorná strana kontajnera ide od -1,6 do 1,8,
dlaždice pozadia terénu ležia celé mimo 0..1 a v jednom leveli 23 % texturovaných
trojuholníkov siaha mimo 0..1. Zapisujú sa tak, ako sú, s opakujúcim sa vzorkovačom;
prehliadač 3DHeat obalí každú opakujúcu sa textúru v svojom atlase. Renderer, ktorý ich
namiesto toho orezáva, roztiahne rebrá na dvojnásobnú šírku, zmení betónovú podlahu
na pruhy pozdĺž jednej osi a dá oceľovým nosníkom veže farbu okraja ich textúry; pre
neho `--clamped-uvs` rozreže každý trojuholník pozdĺž čiar, kde sa jeho textúra
opakuje, a presunie každý kus do 0..1 (pozri [Výstupný formát](output-format.md)).
Potom 0,03 % texturovaných trojuholníkov, cez ktoré sa textúra opakuje viac než
16-krát, siaha von, a trojuholník, ktorý by rezanie rozdelilo na viac než 4 kusy, sa
kreslí v priemernej farbe svojej textúry: kôra sa opakuje dole každou vetvou a
rozrezaná, stromy jedného levelu vyrástli z 6,4 na 24 miliónov trojuholníkov.

Výškové pole nemá vlastnú farebnú mapu, ktorú by sa dalo prečítať. Kde ju pokrýva
jedna z máp pozadia terénu, farbí sa podľa nej: súradnice textúry pozadia sú lineárna
funkcia svetového x a z (99 % jeho vrcholov je do 0,001 od nej; mapa pokrýva štvorec
65 536 m, otočený o štvrtinu) a tá istá funkcia dáva súradnice výškového poľa. Level
dodáva mipy tejto mapy od 2 048 px nadol, takže výškové pole dostane 32 m na pixel.
Jeho tmavá skala leží na strmej zemi: korelácia tmavosti so sklonom je 0,48 a najviac
0,34 pre ostatných sedem orientácií.

Pozadie iného levelu je osem blízkych a osem vzdialených dlaždíc okolo herného
priestoru, každá opakuje svoju vlastnú textúru cez dlaždicu, a žiadna nedosiahne na
výškové pole. Každá textúra pozadia sa fituje samostatne, a keď žiadna nepokrýva
výškové pole, dostane priemernú farbu, ktorú pozadie ukazuje do jedného kilometra od
štvorca terénu; tou sa pečú nálepky terénu, ktoré `--ground-texture` pečie nad ňou.
Materiál pozadia je ten, ktorého názov obsahuje `TerrainBackdrop`, alebo `BD_` a
`Terrain` (`M_BD_<site>_Terrain..._Near`); alebo sieť pozadia
(`bd_..._terrain<site>_04_far_mesh`) nesie obyčajný materiál terénu
(`M_<region>_Terrain<site>_04_Far`), ktorý prvé dve pravidlá v jednom leveli minuli, a
tak zafarbil svoju zem podľa svojich povrchov.

Kde žiadna mapa pozadia nepokrýva výškové pole, dostane namiesto toho stredovú
farbu vlastných povrchov terénu pred priemerom pozadia: farebné mapy `_cv`, ktoré
pomenúvajú bloky shadera layer grafu (27 v jednom leveli: piesky, štrky, pôdy, tráva,
popraskaný betón), každá spriemerovaná, potom medián každého kanála, bez predvoleného
povrchu motora. Pozadie môže byť úplne iná krajina: v jednom leveli jeho priemer (95,
99, 80 v sRGB) zafarbil zem herného priestoru na šedú, akú hra nezobrazuje. S
`--ground-texture` sa táto farba vynásobí dvojnásobkom farebnej mapy, čo pološedá
necháva tak, ako je, a zapečie sa s nálepkami cez rozsah nálepiek aj farebnej mapy.

Voči hre: medianová farba zeme pečenej herné oblasti každého levelu a herných snímok
(riadky 55 až 72 % obrazu vedľa HUD, po 24 snímkach; sRGB; snímky sú osvetlené a
gradované, takže pomer r/g a b/g je férové porovnanie):

| Level | Snímky | Priemer pozadia | Teraz |
|---|---|---|---|
| prvý | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| druhý | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| tretí | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Prvý je opravený; ostatné dva boli predtým v odtieni o niečo bližšie. Jedna farba pre
celý level nemôže byť správna všade; správne by boli masky.

## Navigačná sieť {#navigation-mesh}

Zdroj: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Level dodáva jeden oddiel na agenta, `<level>/dbt/<level>_navmesh_layer_<n>`: v jednom
leveli je vrstva 0 vojak (1,8 m vysoký, krok 0,18 m, polomer 0,4 m) a dve ďalšie sú
vozidlá (3,5 a 10 m vysoké). Každý oddiel drží dve polia:

| Pole | Prvok |
|---|---|
| dlaždice | 28 bajtov: u32 0, u32 hash, u32 0, u32 index bloku, u16 x dlaždice, u16 z dlaždice, u32 offset, u32 veľkosť |
| bloky | 20 bajtov: GUID bloku, u32 veľkosť |

Dlaždica je `size` bajtov na `offset` v bloku `chunk index`, little-endian, a rozložená
ako Detour (Recast Navigation) za dlhšou hlavičkou:

| Offset | Obsah |
|---|---|
| 0 | `VAND`, verzia 7 |
| 24 | počty: polygóny, vrcholy, spoje, detailné siete, detailné vrcholy, detailné trojuholníky, uzly objemu ohraničenia, spoje mimo siete, prvý polygón mimo siete |
| 188 | výška agenta, krok, polomer |
| 200 | ohraničujúci kváder dlaždice, šesť floatov |
| 232 | vrcholy: x, y, z floaty, svetové súradnice |
| ďalší 8-bajtový hranica | polygóny, 32 bajtov: u32, šesť u16 indexov vrcholov, šesť u16 susedov, u16 príznaky, počet vrcholov na +30, na +31 plocha (nižších šesť bitov) a druh (horné dva) |
| potom, zbalené | spoje (16 bajtov), detailné siete (12: prvý detailný vrchol u32, prvý detailný trojuholník u32, počet vrcholov a trojuholníkov u8), detailné vrcholy (tri floaty), detailné trojuholníky (tri indexy a príznaky), uzly objemu ohraničenia (16), spoje mimo siete (80) |

V každej dlaždici skontrolovaných levelov sa tieto súčty rovnajú veľkosti dlaždice
na bajt a detailné siete číslujú polygóny pred prvým polygónom mimo siete.

Polygón je medzi svojimi rohmi plochý; jeho **detailná sieť** drží skutočnú výšku
povrchu cez hrboly, skaly a schody, a to je to, čo sa kreslí. Index detailného
trojuholníka nižší než počet rohov polygónu je ten roh, inak detailný vrchol
`first + index - corners`. Vejárovité rozloženie polygónov namiesto toho dá oveľa
viac trojuholníkov pod terénom a dlhé tenké pásy; s detailnými sieťami žiadny nie je
dlhší než uhlopriečka 16 m dlaždice plus schod nahor po svahu.

Druh 0 je zem, druh 2 malé strmé záplaty (asi 45 stupňov, každá meter štvorcový), druh
1 spoj medzi povrchmi: jeho rohy sa rozprestierajú na 125 m výšky alebo viac a ležia
mimo dlaždice, niektoré na počiatku. Spoje sa vynechávajú; zvyšok sa kreslí podľa
svojich detailných sietí, alebo sa vejárovito rozloží v dlaždici bez nich.

Kontroly: veľkosti blokov sa presne sčítavajú s dlaždicami; každý vrchol povrchu leží
v kvádri svojej dlaždice s toleranciou asi meter; takmer všetky trojuholníky smerujú
nahor. Dlaždica, ktorá zlyhá, sa odmietne a počíta, a v tom leveli žiadna.

Čo pokrýva sieť vojaka, zhora pozorované v testovacom leveli: zem, podlahy, schody a
niektoré strechy, a nie vrchy nákladných kontajnerov. Je to mapa AI, kde môže vojak stáť,
najbližšie, čo súbory dávajú k miestam, kde stoja hráči.

## Ešte neimplementované {#not-implemented}

- Layer graf terénu, ktorý mieša jeho povrchové vrstvy (pozri [Vrstvy terénu](#terrain-layers)): farba zeme sa riadi pravidlom tohto čítača z masiek vrstiev a sklonu výškového poľa, a levely, ktorých stránky masiek do seba nezapadajú, dostanú jednu farbu.
- Farebné parametre materiálov nálepiek: značenia cez masky kanálov sa maľujú neutrálnou farbou.
- Plány objektov, ktoré nie sú sieťami (herná logika, efekty, zvuky).
- Zničené stavy ničiteľných sietí: miesta ich častí sú v aktíve ničenia, ktoré sa nečíta.
- Spoje navigačnej siete (skoky, rebríky, prekážky) a jej vozidlové vrstvy.
- Úrovne siete uložené vnútri res (10 sietí v leveli, pomôcky), kostrové a zložené siete, ich kosti a časti, a normály (dopočítava ich zapisovač).
- Normálové, drsnostné a iné mapy; alfa iná než výrez (priehľadné sklá a nálepky sa kreslia nepriehľadne).
- Diery terénu: pomenovaný je shader dier, ale čo číta, sa nenašlo (pozri [Vrstvy terénu](#terrain-layers)), takže výškové pole sa nevyrezáva tam, kde pod ním beží chodiaca zem.
- Ktorý odtieň patrí ku ktorému kanálu masky materiálu: šedá farebná mapa dostane prvý odtieň, ktorý nie je neutrálny (pozri [Textúry a materiály](#textures-and-materials)).
- Efekty (cesty `fx/`) a káblové siete, ktorých kvádre majú desiatky kilometrov; vynechávajú sa a počítajú v súhrne.
- Formu tabuľky s XOR zaslepením.
