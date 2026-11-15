---
title: "Frostbite: `.toc`, `.cas`, pachete, mesh-uri și niveluri"
nav_order: 5
lang: "ro"
source: reader-frostbite.md
source_hash: "5aa518f14f3a"
nav_exclude: true
search_exclude: true
---
# Frostbite: `.toc`, `.cas`, pachete, mesh-uri și niveluri {#frostbite-toc-cas-bundles-meshes-and-levels}

**Citește un nivel Battlefield 6 până la terenul lui, mesh-urile plasate și hărțile lor de culoare, și îl scrie ca `.glb`.** Jocurile Frostbite (Battlefield, Need for Speed, Dead Space) își țin conținutul în blob-uri `.cas`, descrise de tabele de conținut `.toc`. Tabelul unui nivel spune ce pachete încarcă nivelul, pachetele numesc fiecare activ, iar activele spun ce mesh stă unde.

Surse:
[`frostbite.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbite.py)
(tabele, pachete, payload-uri),
[`frostbitebundle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitebundle.py)
(pachete și manifestele lor),
[`frostbiteebx.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteebx.py)
(partiții EBX),
[`frostbitemesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitemesh.py)
(MeshSet),
[`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py)
(heightfield),
[`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py)
(texturi și materiale),
[`frostbitelevel.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitelevel.py)
(plasare și export).
Comenzi: `identify`, `levels`, `level` (vedeți [Comenzi](commands.md#levels-and-level-frostbite)).

Nimic de aici nu este documentat de joc. Fiecare layout de mai jos a fost citit din fișiere și apoi confruntat cu toate, iar fiecare secțiune spune ce verificare s-a făcut. Acolo unde uneltele de modding Frosty descriu versiuni mai vechi ale unei structuri, numele câmpurilor urmează ale lor; nu s-a luat niciun cod de la ele (vedeți [Reguli și licențe](rules-and-licences.md)).

## Antetul care pare criptat și nu este {#the-header-that-looks-encrypted-and-is-not}

| Magie (u32, little-endian) | Înseamnă | Tratat |
|---|---|---|
| `0x00CED100` | simplu: arborele începe imediat | citit |
| `0x01CED100` | semnat: o semnătură de 556 de octeți, apoi arborele **în clar** | citit |
| `0x03CED100` | obfuscat cu XOR, cu cheia în antetul propriu al fișierului | detectat și refuzat |

Forma semnată este cea pe care o livrează Battlefield actual. Octeții cu entropie mare de după magie sunt o semnătură, nu text cifrat.

## Arborele DbObject {#the-dbobject-tree}

O structură recursivă. Fiecare câmp are un octet de tip (cei cinci biți mici sunt tipul, bitul 7 înseamnă "anonim"), un nume opțional și o valoare. Containerele își poartă lungimea ca un întreg de lungime variabilă și se termină cu un octet zero. `parse_toc` verifică lungimea fiecărui container, deci un fișier care se parsează a fost înțeles. `layout.toc` este în această formă.

## Pachete de instalare {#installation-packages}

Fiecare locație numește **pachetul de instalare** din care face parte blob-ul ei. Fiecare pachet își numerotează blob-urile de la `cas_01`, deci numărul blob-ului singur este ambiguu de îndată ce este instalat mai mult de un pachet, ceea ce se întâmplă mereu.

- `layout.toc` listează pachetele sub `installManifest.installChunks`, fiecare cu un `persistentIndex` și un `installBundle` ca `Win32/installation/<package>`.
- Blob-urile pachetului sunt în acel folder, sub `Data` pentru jocul de bază sau sub `Update/<pack>/Data` pentru ce a venit mai târziu.
- O înregistrare de locație poartă `persistentIndex` complet, de 32 de biți: jumătatea mică a primului ei cuvânt ține jumătatea mare, jumătatea mare a celui de-al doilea cuvânt ține jumătatea mică; jumătatea mică a celui de-al doilea cuvânt este numărul blob-ului.

Verificare: fiecare locație din fiecare tabel binar al unei instalări se rezolvă la un pachet declarat și se încadrează în blob-ul pe care îl numește. O versiune anterioară lua primul `cas_NN.cas` cu numărul potrivit. O treime dintre payload-urile citite arătau atunci cu entropie mare și erau luate drept criptate. Erau offset-urile corecte în fișierul greșit. Nimic găsit nu este criptat.

## Tabelul nivelului {#the-level-table}

Tabelul unui nivel (`levels/<level>/<level>.toc`) este un tabel de secțiuni: cincisprezece cuvinte mari-endian de antet, apoi secțiuni puse cap la cap, ale căror offset-uri sunt și declarate, și derivabile din două numere.

| Secțiune | Conținut |
|---|---|
| pachete | un tabel de hash (un cuvânt fiecare), apoi o înregistrare de 16 octeți per pachet: cheie, `0x40000000` \| mărime, 0, offset |
| tabel de hash al fragmentelor | un cuvânt per fragment |
| fragmente | un id de 16 octeți (GUID-ul fragmentului, **cu octeții inversați**), apoi un cuvânt: `0x80000000` \| 4 x indexul locației lui |
| locații | patru cuvinte mari-endian: pachet (despărțit), blob, offset, mărime |

Id-urile fragmentelor și locațiile sunt **în ordini diferite**. Citite în ordinea din fișier, fiecare fragment se asociază cu octeții altui fragment, care se decodează perfect (mai ales ca sunet) și deci nu par greșite până când un mesh iese zgomot. Verificare: într-un nivel, cuvintele de index sunt o permutare de la 0 la numărul de fragmente minus unu.

Pachetele sunt stocate în linie după tabelul de secțiuni. Fiecare are nouă cuvinte mari-endian de antet, apoi intrările lor: opt octeți de offset și mărime, precedați de încă opt care numesc pachetul și blob-ul când octetul de flag al intrării are bitul de sus setat. Verificare: pe fiecare pachet, ultima intrare se termină exact unde încep octeții de flag.

### Care tabel este nivelul {#which-table-is-the-level}

Un nivel poate avea mai multe tabele cu același nume: unul în `Data` al jocului de bază, unul în fiecare actualizare (`Update/<pack>/Data`) care îl livrează sau îl schimbă, și unul în fiecare pachet de rezoluție mare (`Update/<pack>/Data/Win32/installation/detail/<package>/...`). Doar unele au pachete. Pentru un nivel pe care o actualizare îl livrează, tabelul din jocul de bază are doar fragmente și niciun pachet, iar cel din actualizare este nivelul; luarea primului tabel găsit nu exporta nimic din el.

Deci nivelul este tabelul cu cele mai multe pachete, straturile mai târzii câștigând la egalitate (jocul de bază întâi, apoi actualizările în ordinea numelor), iar tabelele cu același nume fără pachete sunt **suplimentele** lui: fragmentele lor se adaugă la cele ale nivelului, căci conțin cele mai mari mip-uri ale texturilor lui. Un antet de textură numește fragmentul acela la +164 (vedeți [Texturi și materiale](#textures-and-materials)). `levels` afișează de unde vine fiecare nivel și câte suplimente are.

## Manifestele pachetelor {#bundle-manifests}

Prima intrare a unui pachet este manifestul lui, stocat necomprimat. Este formatul binar de pachete al jocurilor Frostbite mai vechi, cu o magie nouă, `0xD68E799D`: numărători, SHA-1, înregistrări ebx și res (offset și mărime de nume), tipuri res, metadate și id-uri, GUID-uri de fragmente, șiruri. Restul intrărilor pachetului sunt ebx, res și fragmentele, în această ordine. Verificare: numărătorile se potrivesc cu intrările pe fiecare pachet, iar șirurile încep unde se termină înregistrările.

Tipurile de resurse sunt hash-uri. `0x49B156D4` este MeshSet (fiecare res de acest tip se numește `..._mesh`), `0x6BDE20BA` Texture, `0x22FE8AC8` TerrainStreamingTree.

`LevelCatalogue` citește toate acestea pentru un nivel, în câteva secunde: un nivel are zeci de pachete și zeci de mii de ebx, res și fragmente.

## Blocurile payload {#payload-blocks}

```
[decompressed size : 4] [method : 2] [compressed size : 2]    big-endian
```

O mărime comprimată zero înseamnă stocat, atâta timp cât se decomprimă la mărimea declarată.

| Cuvânt de metodă | Codec |
|---|---|
| `0x0070`, `0x0071` | niciunul |
| `0x0270` | zlib |
| `0x0970` | LZ4 |
| `0x0F70` | Zstandard |
| `0x1170`, `0x1570` | Oodle ([Oodle](reader-oodle.md), din DLL-ul `oo2core` al jocului) |
| altul, cu mărimi egale | copiat ca stocat |
| altul | refuzat |

Citit din pachetul corect, fiecare payload eșantionat se decodează.

## Partițiile EBX {#ebx-partitions}

EBX ține tot ce nu este date brute. Fiecare partiție este un fișier RIFF: `EBXD` (datele, aliniate la 16), `EFIX` (GUID-ul partiției, GUID-urile și semnăturile de tip, instanța, offset-urile de pointer, import și informații de tip, importurile, și offset-urile tabloului, valorii împachetate și șirurilor), `EBXX` (tabelul de tablouri: offset, numărătoare, hash, flag-uri, tipul elementului). Un câmp pointer are opt octeți: zero este null, o valoare impară este importul numărul `value >> 1`, orice altceva este relativ la câmp.

**Biblioteca de tipuri nu se poate citi**. Jocul o livrează în sistemul lui de fișiere inițial, care este criptat, iar acest pachet nu îl atinge. Tipurile se cunosc după GUID și semnătură, pe care le poartă fiecare partiție, iar puținele tipuri de care are nevoie exportul de nivel au fost descrise după date.

## MeshSet {#meshset}

Un mesh este o res MeshSet (descrierea) și câte un fragment pentru fiecare nivel de detaliu (bufferele).

| Parte | Layout |
|---|---|
| prefix | patru cuvinte: mărimea antetului (176 sau 192), mărimea înregistrării de nivel (176 până la 188), mărimea înregistrării de secțiune (368), 0 |
| antet | cutia de delimitare; șase offset-uri i64 de nivel; tipul mesh-ului la `0x6C` (rigid, skinned, composite); numărul de niveluri și de secțiuni la `0x9C` |
| nivel | secțiunile la `+0x08`; cinci liste de desenare la `+0x14` (opace, transparente, decal, doar adâncime, umbră); formatul indecșilor la `+0x54` (`0x21` u16, `0x2E` u32), octeții indecșilor și ai vârfurilor; GUID-ul fragmentului la `+0x74` |
| secțiune | numele materialului; pasul vârfului; triunghiurile, primul index, offset-ul vârfului (octeți), numărul de vârfuri la `+0x20`; declarația vârfului la `+0x64`: 16 x (utilizare, format, offset, stream), 16 pași de stream, numărători |
| fragment | bufferul de vârfuri, apoi bufferul de indecși. Fluxurile unei secțiuni vin unul după altul, iar indecșii se numără de la primul vârf al secțiunii |

Pozițiile sunt utilizarea 1, stream 0, offset 0, ca patru semi-float-uri sau trei float-uri. Doar secțiunile opace și transparente se desenează. Fiecare secțiune numită `..._shadow` este în lista de umbră și doar acolo, deci listele decid.

Verificare: fiecare mesh al unui nivel ale cărui niveluri sunt stocate în fragmente se decodează, iar aproape toate au 99% sau mai mult din vârfurile lor în cutia declarată; restul ratează prin rotunjirea semi-float-urilor. Un ladă decodată măsoară aproximativ un metru, Y în sus, cu normalele îndreptate spre exterior.

## Plasarea {#placement}

Procesul de conținut strânge obiectele statice ale fiecărui sub-world într-un **grup de modele statice**: un tablou de membri, câte unul per mesh, fiecare cu transformările lui de instanță.

| Tip (GUID, semnătură) | Layout |
|---|---|
| membru `ad13064e…`, `0xF861A878` | 224 de octeți: `+88` tablou de transformări, `+112` planul obiectului (import), `+160` activul mesh (import) |
| transformare `101dce06…`, `0x5E6D8C37` | 64 de octeți: right, up, forward, translation, fiecare un vec3 completat la 16 |

Partiția activului mesh este numită ca res-ul ei MeshSet, deci GUID-ul partiției importului dă mesh-ul. Un punct ajunge la `x·right + y·up + z·forward + translation`. Transformarea grupului însuși a fost identitatea în fiecare grup al nivelurilor verificate și nu se aplică.

Verificare: într-un nivel, fiecare membru al fiecărui grup se rezolvă la un mesh; majoritatea copiilor au o rotație cu determinantul 1 la o miime, restul sunt scalate sau oglindite. GUID-urile și semnăturile de tip sunt aceleași în alte niveluri. O actualizare a jocului care schimbă layout-ul schimbă semnătura, iar cititorul atunci nu găsește nimic în loc să citească greșit.

### Obiecte plasate unul câte unul {#objects-placed-one-by-one}

Ce nu poate grupa procesul - obiecte distructibile, containere, resturi - este plasat prin **referințe de obiect** și **referințe de prefab** din partițiile nivelului:

| Tip (GUID, semnătură) | Layout |
|---|---|
| referință de obiect `a9a6a6ad…`, `0xC4856BEC` | `+32` transformarea (ca mai sus), `+112` planul obiectului (import) |
| referință de prefab `117c746e…`, `0xDE3FE9B4` | la fel; planul este un prefab, o partiție de referințe suplimentare |

Prefab-urile se cuibăresc; o copie ajunge la propria transformare înmulțită cu cea a părintelui (vectori rând), până la opt niveluri adâncime. Un plan de obiect se desenează ca mesh-urile pe care le importă, lăsând afară stările distruse (`dc_...`). Un prefab grupat este referit ca rămășița lui `..._nongroupable_autogen`, deci nimic nu se desenează de două ori.

Parcurgerea pornește doar de la lumile și straturile nivelului. O partiție a cărei prima instanță este un plan de prefab (`134919fc…`, `0x0247807D`) este definiția unui prefab, iar un nivel ține multe dintre acestea în folderul lui propriu, plasate de lumile lui în alte feluri decât aceste referințe; parcurse ca și cum ar fi o lume, un prefab își pune conținutul la coordonatele lui locale. Asta ar face sute de copii în jurul originii lumii, mult sub teren. Lumile și straturile au `a10ebe0f…`, `0xD3D16C3C` ca prim element.

Planurile scoase din joc nu sunt urmate: activele de dezvoltare și de test (`game/dev/`, `test/`), setul cinematicii de sfârșit de rundă (`..._gameend_...`: pus sub teren) și controlerul camerei de moarte (`.../deathflow/...`, ale cărui obiecte stau în originea lumii). Sunt recunoscute după calea activului, nu după strat: același strat care ține setul cinematicii poate plasa pereții și acoperișurile reale ale nivelului. După ambele reguli, nicio copie din nivelurile verificate nu stă mai mult de 10 m sub teren, iar copiile stau pe teren acolo unde le arată jocul.

**Niveluri de detaliu care țin locul.** Ultimul nivel de detaliu al unui mesh poate trece la un substitut de vedere îndepărtată cu un material propriu: `M_LastLod`, `M_Billboard`, `M_Vista`, `M_ProjectionLod`. Un turn de zăbrele cu zeci de mii de triunghiuri se poate termina într-o siluetă de câteva sute, pe care bugetul ar alege-o și care de aproape este un vârf solid. Un nivel de detaliu care aduce un astfel de material, pe care nivelul cel mai fin nu îl are, nu se alege niciodată; cel mai grosier al mesh-ului este ultimul real.

## Terenul {#terrain}

Sursă: [`frostbiteterrain.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbiteterrain.py).

Terenul este o res TerrainStreamingTree (tipul `0x22FE8AC8`) și fragmentele pe care le numește.

| Parte | Layout |
|---|---|
| antet | 34 de octeți; numărul de noduri la 25 |
| arbori raster | un octet de tip și o lungime u32 fiecare, până la un octet de tip `0xFF`. Tipul 0 este harta de înălțimi: eșantioane pe latură la +5 (265), intervalul de înălțimi la +21 (1.280 m), pătratul terenului în prima înregistrare de nod la +77 (8.192 m în nivelul verificat). Conține cutiile de delimitare ale nodurilor și o piramidă min/max de 16 x 16 per nod, nu înălțimile |
| noduri de streaming | quadtree-ul, în adâncime: mărimea fragmentului și GUID-ul; un fragment opțional al doilea; un octet de flag (bitul 0: fragmentul începe cu o pagină de înălțime); are-copii. Copiii în ordinea (0,0), (1,0), (1,1), (0,1) |
| pagină de înălțime | primele 265 x 265 u16 ale fragmentului unui nod cu flag, rând cu rând; înălțimea = valoare x 1.280 / 65.535 m; coloanele de-a lungul lui x, rândurile de-a lungul lui z, de la colțul de jos al nodului; o margine de 4 eșantioane, deci 256 de celule pe nod |

Fiecare pas a fost verificat separat:

- Parsarea quadtree-ului de noduri consumă res-ul până la ultimul octet, cu cele 529 de noduri declarate.
- Nodurile vecine își împart exact cele nouă coloane de margine, deci pasul este 256.
- Eșantioanele unui copil din fiecare poziție alternativă sunt exact egale cu ale părintelui său cu o margine de 4, și sunt cu 90 până la 700 de unități diferite cu orice altă margine.
- Cel mai mic cuvânt din nivel se decodează la cea mai mică înălțime a cutiei de delimitare, până la centimetru.
- Din cele opt moduri în care pătratul ar putea sta pe lume, doar x de-a lungul lui x și z de-a lungul lui z pune obiectele plasate pe el: jumătate din copiile eșantionate în aproximativ 2 m, față de de câteva ori mai mult pentru fiecare alt mod.

Obiectele plasate măsoară apoi rezultatul. Punctul cel mai de jos al fiecărei copii, față de terenul de sub ea (biliniar, din cel mai fin nod):

| Plasat | Distanța mediană | Mediană cu semn |
|---|---|---|
| copaci și tufișuri | sub un metru | ușor sub suprafață |
| recuzită | un metru sau două | pe suprafață |
| stânci | aproximativ un metru | scufundate cu aproximativ un metru |
| clădiri | câțiva metri (stau pe fundații) | ușor scufundate |

Vegetația se plasează pe sol și nicăieri altundeva, ceea ce o face cea mai ascuțită verificare: originile ei stau la o mediană de 0,07 m de suprafață. Clădirile se împrăștie mult pentru că categoria ține pereți, podele și piese de kit ale structurilor cu mai multe etaje și subterane. Deplasarea terenului cu 64 m lateral scade proporția copiilor la cel mult 0,5 m de la 29% la 10%.

`level` desenează harta de înălțimi ca `ground:terrain`, fiecare parte a ei din cel mai fin nod cu înălțimi acolo și nu mai fin decât `--ground-spacing` (4 m implicit: 3,7 milioane de triunghiuri pentru nivelul verificat, ale cărui noduri cele mai fine au 0,5 m). Piesele de rezoluții diferite se întâlnesc cu pași mici; nimic nu le îmbină.

Fragmentul unui nod conține și paginile de măști ale straturilor de după pagina lui de înălțime, iar al doilea fragment se termină cu harta de culoare a nodului (vedeți [Straturile terenului](#terrain-layers)).

## Straturile terenului {#terrain-layers}

Jocul umbrește terenul din apropierea unui jucător prin împrăștierea materialelor de suprafață cu mască pictată, cu o hartă de culoare peste ele, și desenează decalcuri (drumuri, petice de asfalt, marcaje de pistă) deasupra. Descrierea Frostbite a sistemului (Widmark, "Terrain in Battlefield 3", GDC 2012) listează rasterele terenului ca harta de înălțimi, măștile de împrăștiere ale shader-ului, o hartă de culoare "folosită ca suprapunere peste împrăștierea shader-ului", materialele de fizică, o mască de adâncime a distrugerii, o hartă de albedo pentru lumina reflectată și canale de mască suplimentare; plăcile unui raster poartă o margine pentru algoritmii de randare. Arborii raster ai nivelurilor verificate sunt șapte, de tipurile 0, 1, 2, 4, 5, 7 și 8, ale căror antete încep cu mărimea plăcii: 265 pentru harta de înălțimi (tipul 0) și tipul 2, 72 sau 66 pentru măști (tipul 1), 132 cu o margine de 2 pentru harta de culoare (tipul 4), 260 cu o margine de 2 pentru tipul 5.

**Lista straturilor.** Res-ul `....layergraphs` al terenului listează câte o intrare de 32 de octeți per strat, în ordinea în care le numerotează înregistrările măștilor (34 de intrări, 34 de secțiuni de depozit și indicii de strat de la 0 la 33 într-un nivel); id-ul fiecărei intrări se termină cu cheia ei de secțiune în depozitul de blocuri de shader al graficului de straturi (`....layergraphs_shaderblockdepot`), al cărui bloc numește hărțile stratului: câte o hartă de culoare `_cv`, hărți `_nhs` și `_ao` per suprafață, plus hărți comune de detaliu și zgomot. Multe straturi nu numesc nicio hartă: sunt surse pe care le citește graficul de straturi. Culoarea unui strat este media hărții lui `_cv`; scara de întindere nu se găsește. Asetul terenului se termină cu câte o intrare de cinci octeți per strat (un octet, apoi un u32 cu indexul stratului sau -1).

**Măștile.** Raster-ul 1 este quadtree-ul măștilor. Corpul lui începe cu 59 de octeți, latura paginii la 0: 72 unde paginile sunt BC4 (72 x 72, 2.592 de octeți), 66 unde sunt opt biți necomprimați (4.356 de octeți). Apoi vine câte un grup per nod, în adâncime:

| Parte | Layout |
|---|---|
| grup | u16; u16 numărul de înregistrări; u32 numărul de pagini; înregistrările; un octet zero. Un grup fără înregistrări are 7 octeți în total |
| înregistrare | 33 de octeți: u16 strat, u16 hash, cutia cvadrantului (patru float-uri), doi octeți de flag, o piramidă de prezență de 85 de biți |

Înregistrările unui grup sunt cei patru cvadranți ai nodului său, strat cu strat, cu cvadranții fiecărui strat în ordinea (0, 0), (1, 0), (1, 1), (0, 1). O înregistrare cu al doilea flag setat acoperă cvadrantul întreg și nu are pagină; una fără el are pagina următoare; un cvadrant fără înregistrare a unui strat pe care grupul lui îl numește este gol de acel strat; primul flag este șters exact când stratul continuă în grupul cvadrantului însuși, cu un nivel mai jos, care îl înlocuiește acolo. Numărul de pagini este numărul înregistrărilor cu pagină.

Paginile: paginile grupului propriu al unui nod urmează, în fragmentul lui, pagina de înălțime, o secțiune de 4.358 de octeți pe 16 biți și un raster de 67 x 67 pe opt biți (de la începutul fragmentului când nu are pagină de înălțime); al doilea fragment al lui ține paginile grupurilor celor patru cvadranți ai lui cu un nivel mai jos, cvadranții în ordinea hărții de culoare, apoi harta de culoare. O pagină este cele 64 x 64 de texeli ai cvadrantului, rândurile de-a lungul lui z și coloanele de-a lungul lui x, cu o margine copiată de la vecini: 4 texeli pe o pagină BC4, 1 pe una necomprimată.

Marginile dovedesc plasarea fără judecată: două pagini ale aceluiași strat una lângă alta trebuie să poarte reciproc texelii de margine. `read_masks` verifică asta pentru fiecare pereche pe care o plasează și refuză un nivel unde mai puțin de 99% se potrivesc. Aproximativ o treime din nivelurile verificate se citesc, cu marginile lor de acord; câteva nu au măști pictate; restul sunt refuzate, aproape toate de verificare (fragmentele nodurilor lor conțin mai mult decât știe acest layout). Terenul unui nivel refuzat ia culoarea medie a materialelor sale de suprafață, iar exportul spune de ce. Marginile care dau spre un cvadrant plin sunt 255, iar cele care dau spre unul gol 0.

Pagina de secțiune de 4.358 de octeți și rasterul de 67 x 67 dinaintea paginilor nu se citesc: valorile lor stau într-o bandă înaltă și îngustă, fără valori mici și fără marcaj.

**Culoarea terenului.** Graficul de straturi amestecă straturile într-un graf de shader compilat, din măști, pantă, înălțime și zgomot, care nu se citește. `--ground-texture` colorează solul printr-o regulă proprie, spusă aici ca atare:

- straturile a căror hartă de culoare este numită după distanță sunt substitutele vederii îndepărtate și se lasă afară;
- straturile cu textură care acoperă nouă zecimi sau mai mult din teren sunt baza. Măștile lor sunt pline aproape peste tot, deci unde stă fiecare este alegerea shader-ului, nu a lor: cele numite pentru stâncă sau fund colorează pantele mai abrupte de 40 de grade, cele numite pentru pietriș colorează terenul plat (celelalte straturi de bază când niciunul nu este), amestecate între 20 și 40 de grade după panta hărții de înălțimi (luată din 4 în 4 m și împrăștiată biliniar peste texelii copți: repetată în blocuri de 4 m desena culoarea stâncoasă ca pete cu margini tăioase);
- fiecare alt strat cu textură se așază peste bază după propria lui mască, în ordinea straturilor;
- harta de culoare se așază peste rezultat cum o face motorul: de două ori culoarea solului înmulțită cu harta, astfel încât gri-mijlociu o lasă neschimbată; unde harta de culoare nu are texeli, solul ia luminozitatea mediană a hărții, în gri.

Verificat față de culoarea mediană a solului din cadrele de joc ale a trei niveluri (cromatica ca roșu și albastru peste verde): zona de joc copta iese 1,00 / 0,69 față de 1,19 / 0,78 ale cadrelor într-unul, al cărui strat de iarbă este verde unde cadrele arată iarbă uscată; 1,19 / 0,82 față de 1,01 / 1,04 într-altul, a cărui hartă de culoare este ea însăși caldă (1,13 / 0,88); și 1,05 / 0,91 față de 0,93 / 0,92 într-un al treilea, fără hartă de culoare. Cadrele sunt luminate și gradate, deci asta măsoară nuanța, nu luminozitatea.

**Harta de culoare.** Al doilea fragment al unui nod ține, după paginile de mască ale grupurilor cvadranților lui, patru pagini BC7 de 132 x 132 (17.424 de octeți fiecare), câte una per cvadrant al nodului, în ordinea (x mic, z mare), (x mare, z mare), (x mare, z mic), (x mic, z mic). Arborele de măști spune câți octeți iau paginile de mască, deci harta de culoare se găsește prin numărare, nu prin sfârșitul fragmentului: într-un nivel, nodurile mai grosiere poartă patru astfel de pagini în plus după ea, un alt raster într-o culoare plată, iar citirea ultimelor patru pagini ale fragmentului pierdea harta de culoare pe nouă zecimi din teren. Fără numărare, harta de culoare era pierdută și în nivelurile cu pagini de mască necomprimate, al căror număr de octeți nu este un număr întreg de pagini BC4; harta de culoare a unui nivel a trecut de la 0,4 la 0,94 din terenul lui. Ordinea a fost determinată prin potrivire: față de marginile fiecărei hărți de înălțimi a unui cvadrant, fiecare pagină a nodurilor cu trăsături se potrivește cu un cvadrant, nerăsucită, la 0,3 până la 0,54, unde următoarea cea mai bună plasare este sub 0,2. Cusută astfel, paginile unui nivel se îmbină fără cusătură în drumurile, apele și zonele construite ale nivelului de test, la 0,5 m un texel în zona de joc. Acolo unde straturile fac treaba, harta de culoare este aproape neutră (mediană 110, 107, 104); în altă parte poate avea culoare întreagă. Un nivel ale cărui al doilea fragmente au doar pagini de mască necomprimate nu are harta de culoare citită. O rundă anterioară a acestui cititor numea aceste pagini ne-geografice: le compara cu harta de fundal, care poate fi cu totul alt peisaj, și punea fiecare pagină pe întregul nod, nu pe un cvadrant.

**Albedo-ul luminii reflectate** a fost căutat și nu a fost găsit: fragmentele nodurilor rădăcină și de primul nivel sunt pagini de mască întregi, iar payload-ul tipului 5 nu este localizat.

**Găuri.** Asetul terenului unui nivel (res de tipul `0x1CA38E06`) numește trei shadere: un shader de suprafață implicit, un shader de suprafață pentru găuri și un shader de sursă implicit. Nu s-a găsit ce strat citește shader-ul de găuri, deci harta de înălțimi nu se taie. Într-un nivel, plasa de navigare poate merge pe mesh-uri de stâncă cu zeci de metri sub harta de înălțimi, unde jocul trebuie să le fi tăiat. Căutate și negăsite acolo: masca unui strat, rasterul de 67 x 67, o înălțime rezervată (nicio pagină de înălțime a nivelului nu conține 0 sau 65.535) și un flag al nodului (fiecare nod sub rădăcină are flag-urile 1). Rasterele 7 și 8 sunt ce a rămas. Ambele sunt codificate prin lungimi de serie: un octet egal cu cel dinaintea lui este urmat de un număr de copii în plus (`ff ff 84` înseamnă 134 de octeți de 255). Arborele 7 (plăci de 256, un quadtree complet cu cinci niveluri, patru biți per eșantion) se decodifică în perechi de octeți cu valori de la 0 la 3; arborele 8 (plăci de 265) în octeți în mare parte 255, cu celelalte valori în serii regulate. Plăcile niciunuia nu sunt plasate încă, deci nu se știe că vreuna conține găurile.

**Decalcurile** se citesc și se coc; vedeți [Decalcurile terenului](#terrain-decals).

## Decalcurile terenului {#terrain-decals}

Sursă: [`frostbitedecals.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitedecals.py).

Drumuri, piste, platforme de beton, marcaje și litere pictate, urme de cauciucuri: res-ul `TerrainDecals` (tipul `0x15E1F32E`) le ține ca geometrie plată pe care jocul o așază peste teren.

| Parte | Layout |
|---|---|
| antet | la +16 un număr de sloturi n, apoi n sloturi de 16 octeți, apoi numărul de înregistrări |
| înregistrări | una per lot de desenare, unele după altele, de lungime variabilă: 156 de octeți de câmpuri fixe - primul vârf la +32, numărul de triunghiuri la +36, repetarea texturii în metri la +44 - apoi octeții vârfurilor lotului (offset, mărime), apoi o coadă care numește texturile prin GUID-urile partițiilor activelor lor |
| vârfuri | 32 de octeți: x, z (f32), 8 octeți împachetați, u, v (f32), r, g, b, a (f16); fiecare lot este o listă simplă de triunghiuri |
| indecși | u32, numărați de la 0 în fiecare lot; nu sunt necesari |

Verificări:

- intervalele de vârfuri ale înregistrărilor se urmează fără gol și acoperă exact toate vârfurile, iar primul vârf al fiecărei înregistrări × 32 este offset-ul ei;
- citite așa, triunghiurile sunt decalcuri compacte (litere, fâșii de linie, petice); citite cu un vârf în minus, sunt așchii peste hartă;
- aproape toate loturile numesc în coadă texturi: o hartă de culoare (`_cv`) cu o hartă de opacitate (`_op`, canalul roșu), sau pentru marcaje o mască de canale (`_rgb`).

După GUID-urile texturilor, coada poartă parametrii de material ai lotului, codificați cum sunt cei ai unui bloc de shader (vedeți Nuanțele mai jos). Culoarea de vopsea a unui marcaj, a unei urme de cauciucuri sau a unei linii este vectorul de trei float hashuit `607e`: un 0,64, 0,56, 0,48 nisipiu pentru urmele pe nisip, aproape negru pentru gudron. Hărțile de opacitate sunt în mare parte de formatul 62, un canal pe 8 octeți per bloc, citite ca BC4.

Un lot își mapează textura fie după poziția în lume (u = x, v = z, textura repetându-se la fiecare metri de repetare: asfalt, beton, pietriș), fie 0 până la 1 peste decal (o linie, o literă, o urmă de cauciuc). Înregistrările se desenează în ordinea fișierului.

**Coacerea.** `level --ground-texture M` pictează, sub extinderea decalurilor și în plăci de cel mult 4.096 de pixeli, harta de culoare a fundalului (biliniar), apoi fiecare lot peste ea, după opacitatea lui × alfa vârfului. Culoarea vârfurilor nu se folosește: unele vârfuri de lot sunt pur verzi sau albastre, ceea ce colora marcajele unui nivel în acele culori. Triunghiurile hărții de înălțimi de acolo devin părți `ground:terrain x<x> z<z>` care poartă placa. Fiecare lot se desenează astfel:

| Numele loturilor | Desenat ca |
|---|---|
| o hartă de culoare (`_cv`) | harta, după harta ei de opacitate |
| o hartă de înmulțire (`_mult`) și o hartă de opacitate | vopseaua (alb dacă materialul nu numește una) înmulțită cu harta de înmulțire, după harta de opacitate: linia centrală uzată a unei piste, liniile de margine și barele de prag |
| o mască de canale (`_rgb`) | vopseaua, altfel alb pentru linii și litere, întunecat pentru contururi, o ușoară întunecare pentru uzură, urme de cauciucuri, pete, bălți și umezeală, după mască |
| o hartă de opacitate singură, cu o vopsea | vopseaua după harta de opacitate: urmele de anvelope |

O mască de variație a drumului nu este vopsea, ci variază suprafața de sub ea, pe sute de metri, și nu se desenează, oricare ar fi vopseaua: pictată alb, a așezat două dreptunghiuri palide de 150 până la 250 m pe pantele unui nivel. Harta `_mult` se ia drept uzura proprie a vopselei, nu drept o întunecare a solului de sub ea: este aproape albă, iar forma liniei este în harta de opacitate.

Aproape fiecare lot se desenează, în câteva plăci de 0,5 m un pixel; exportul crește cu câțiva MB și durează câteva secunde în plus. Privite de sus, platformele, căile de rulare și rețeaua de drumuri stau sub gardurile și clădirile compușilor și duc la porțile lor.

Desenate ca geometrie proprie, decalcurile ar avea nevoie de amestec alfa, pe care scriitorul nu îl duce, iar un decalaj deasupra unui teren s-ar lupta cu el la nivel de z; coacerea le ține în culoarea solului.

## Texturi și materiale {#textures-and-materials}

Sursă: [`frostbitematerial.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitematerial.py).

O res Texture (tipul `0x6BDE20BA`) este un antet de 180 de octeți: tipul și formatul pixelului la +8, lățimea și înălțimea la +22, numărul de mip-uri la +30, GUID-ul fragmentului la +40, cincisprezece mărimi de mip la +56. Fragmentul este lanțul de mip-uri, cel mai mare primul. Unele fragmente nu au cele mai mari mip-uri, care sunt într-un pachet de rezoluție mare; lungimea fragmentului spune de la ce mip începe. Fragmentul acelui pachet este numit la +164; se citește din [suplimentele](#which-table-is-the-level) nivelului atunci când lipsește un mip pe care îl cere fragmentul principal, iar lungimea lui plus cea a fragmentului principal dă lanțul întreg.

| Format | Decodat ca | Dovadă |
|---|---|---|
| 67, 66 | BC7 (sRGB, liniar) | o foaie de culoare a unui rezervor de plastic se decodează ca BC7; ca BC3, aceiași octeți sunt zgomot |
| 61, 60 | BC3 | o foaie de ladă se decodează curat ca BC3, nu ca BC1 sau BC7 |
| 57, 56, 55 | BC1 | o jumătate de octet per pixel |

Mesh-ul activului nu numește nicio textură. Legătura este în **depozitele de blocuri de shader** ale nivelului (tipul de res `0x73312045`, unul per sub-world), cheiate de cei opt octeți de la +0x130 din înregistrarea unei secțiuni de mesh:

| Parte | Layout |
|---|---|
| tabel, la 16 | (cheie de secțiune u64, offset de descriptor u64), până când un offset cade în afara res-ului |
| descriptor | (offset de bloc u64, hash u64, mărime de bloc u64) |
| bloc | parametrii de shader ai secțiunii; fiecare textură este o înregistrare de 49 de octeți: un octet, 16 octeți, GUID-ul partiției activului texturii, GUID-ul instanței lui |

Cheia de secțiune a ladei apare o dată în fiecare dintre cele zece depozite ale sub-world-urilor care o plasează, iar blocul ei numește `t_mil_crate_03_cs` și `_nmt` printre hărțile comune de detaliu. Un bloc numește fiecare textură pe care o eșantionează shader-ul, iar care dintre ele este harta de culoare nu este spus, deci se alege: o textură 2D sRGB al cărei nume conține majoritatea cuvintelor din numele materialului (`M_ConcreteWall_01`: concrete, wall), apoi din cel al mesh-ului, apoi una care nu este un detaliu, un decal (`t_de_...`) sau o hartă de deteriorare, apoi cea pe care o folosesc cele mai puține blocuri. Blocul unui panou rutier numește panoul lui `t_com_highwaysignage_01_cs` și o foaie de decal `t_de_com_highwaysignage_01_ca` cu un scut pus pe o parte; ambele se potrivesc cu cuvintele, iar fără regula decalului foaia câștiga după folosire, iar indicatorul arăta scutul rotit cu un sfert, prin toate seturile de coordonate de textură ale secțiunii. Shader-ele de distanță cu semn (`..._sdf`), paletele și măștile de canale (`_rgb`) nu se aleg niciodată, oricare cuvinte ar avea în comun (`_rgba` se aleg: majoritatea sunt culoare cu alfa, iar a le lăsa afară a schimbat hărțile proprii ale unui stâlp de înaltă tensiune și ale unei scări cu altele fără legătură): un atlas de vegetație al fundalului `..._atlas_a_sdf`, desenat ca culoare, arăta stele negre și albe pentru copaci, o paletă de clădiri a fundalului un confetti de mostre pentru pereți, iar sticla spartă desenată prin masca ei de canale ieșea cyan. O secțiune ale cărei singure candidate sunt hărți comune de detaliu rămâne colorată plat.

**Palete.** Clădirile unui fundal își iau culorile dintr-o paletă de 256 x 256 de texeli, din mostre de 16 x 16: fiecare vârf poartă patru octeți (utilizarea `0x1E`) al căror primi doi spun unde în paletă stă culoarea lui, x și y din 255. `level` desenează o asemenea secțiune cu paleta drept textură, fiecare vârf în centrul mostrei lui. Așa desenate, blocurile fundalului unui nivel ies ca pereți pastelați, cărămidă arsă și ferestre închise, unde erau albe simple.

**Suprapuneri.** Obiectele mari așază o foaie de tăiere pe primele lor coordonate de textură, iar peste ea o suprapunere prin a doua set de coordonate, care stau între 0 și 1: un desfășurat al întregului obiect. Suprapunerea (`..._overlay_cs`, cu masca ei `..._overlay_a`) poartă ce arată obiectul de departe, benzile roșii și rugina unui rezervor de ulei; desenat doar cu foaia de tăiere, rezervoarele unui nivel ieșeau ca panouri gri. O secțiune al cărei bloc numește o suprapunere cu masca ei, și ale cărei a doua coordonate sunt un astfel de desfășurat, se desenează cu suprapunerea prin ele (36 de secțiuni în acel nivel).

**Nuanțe.** Multe hărți de culoare sunt gri (mediile canalelor lor se află la 6% una de alta): shader-ul le pictează cu culori din parametrii blocului. După intrările lui de textură (49 de octeți fiecare), un bloc își listează parametrii, fiecare cu o etichetă de tip (`f11af825` un float3, `a5e1f2de` un float4, `c1b1a014` un float, `4a4fc3a1` un întreg), octeții de flag `01 80` pentru o singură valoare, un hash de doi octeți al numelui parametrului, un număr u32, valoarea și un id de opt octeți. Numele nu sunt stocate. Șapte nume de hash float3 se comportă ca nuanțe: într-un nivel, trei dintre ele țin o culoare în aproximativ 1 bloc din 6 a cărui hartă este gri și aproape niciodată acolo unde harta are culoare proprie, iar celelalte țin culorile în care este vopsită o hartă gri când numele materialului spune asta (banda `..._blue` a unui pod: 0,047, 0,098, 0,171 față de un 0,5 neutru). O familie poate avea mai multe valori, câte una per canal al unei măști, cele mai multe neutre, iar o valoare cu un canal aproape gol (verde pur pe fațadele de cărămidă) selectează un canal al unei măști, nu vopsește. `level` înmulțește o hartă de culoare gri, în lumină liniară, cu prima valoare a fiecărei familii care nu este nici neutră, nici un astfel de selector, peste cea neutră, și păstrează rezultatul ca textură proprie; o hartă cu culoare rămâne cum este. Regula este a exportatorului însuși: care canal al unei măști primește care nuanță nu se citește. Într-un nivel, asta a scos proporția triunghiurilor de structură desenate aproape de alb de la 19,4% la 3,9%.

**Variații de obiect.** Un mesh este plasat în mai multe înfățișări: un perete de depozit cu o dungă roșie sau albastră și un număr diferit pictat pe el, un container verde sau gri. Fiecare copie plasată își numește înfățișarea:

| Unde | Câmp |
|---|---|
| membru de grup de model static | +32: un tablou de un pointer al unei copii, către o variație de obiect sau null |
| referință de obiect | +120: un pointer către o variație de obiect sau null |
| variație de obiect (partiția `ov_...`, tipul `235f2a9c...`) | prima ei instanță +32: hash-ul u32 al numelui variației |

Înfățișarea unei secțiuni dintr-o variație este blocul de shader cheiat de cheia proprie a secțiunii cu hash-ul variației adăugat la primii patru octeți ai ei, ca u32 little-endian (`05177857 76ddd22e` + `0x88af2290` = `953927e0 76ddd22e`); o secțiune fără bloc sub acea cheie arată la fel în fiecare variație. Tabelele de variații ale meshurilor nivelului (`meshvariationdb_win32`) listează, pe mesh și hash de variație, materialele pe care le atinge fiecare variație, dar nu cheile; regula a fost găsită din chiar cheile și ține pentru fiecare secțiune cu variante verificată (cele patru variații ale unui perete, trei dintre secțiunile lui). Blocul unei variații aduce și texturile lui proprii, nu doar nuanțele: numărul pictat pe perete este o foaie de litere pe care o numește blocul variației. O mare parte din copiile grupate sunt plasate într-o variație.

Un bloc se coace o singură dată pentru fiecare set de conținut, iar intrarea depozitului pentru o cheie poartă un hash al lor (al doilea u64 al intrării). Unde o secțiune nu are bloc sub cheia variației ei, variația o ajunge totuși printr-un *geamăn*: altă secțiune al cărei bloc implicit are același conținut și care are unul. Fără gemeni, un perete ale cărui lungimi împart un bloc implicit poate ieși în două culori. O secțiune fără variantă proprie ia varianta pe care o au cei mai mulți dintre gemenii ei.

**Mesh-uri distructibile.** Un mesh pe care îl poate doborî un meci are alături un fișier de distrugere de același nume (`.../br_x.destruction` pentru `.../br_x_mesh`): clădirile și zidurile sparte (`br_`) și multe recuzite. `level` le păstrează suprafețele în părți proprii, numite cu ` (destructible)`, ale căror noduri glTF poartă `{"destructible": true}`. Stările lor distruse sunt mesh-urile `dc_..._part<N>_mesh` de lângă ele, fiecare centrat pe propria origine; unde stă fiecare parte este în fișierul de distrugere, care nu se citește, deci stările distruse nu se exportă.

**Lăsate afară.** Secțiunile de materiale provizorii de blocaj (`M_Whitebox`: câteva triunghiuri mari, nedecorate, pe care unele clădiri le țin lângă suprafețele lor, care ieșeau dintr-un nivel ca aripioare albe), mesh-urile făcute pentru cinematice (un elicopter așezat unde începe scena lui) și ajutoarele de iluminare (plane care blochează lumina și nu se desenează niciodată). Clădirile generate ale fundalului unui nivel (`..._generated_blueprints_..._mesh`) se desenează, dar materialele pereților lor numesc doar hărți de zgomot, iar vârfurile lor nu poartă culoare, deci rămân simple. Aproape fiecare secțiune desenată primește o hartă de culoare.

**Foi de litere.** Un număr pictat pe perete sau un panou publicitar al unei macarale este o secțiune proprie a cărei hartă de culoare este o foaie (`_ca`): alfa unei litere peste vopseaua plină sau un tipar. Primele ei coordonate de textură așează plasterul peretelui pe panou (u de la -0,2 la 1,7 pe un perete), ceea ce desenează foaia aproape de două ori; al patrulea set (`0x24`, altfel al treilea, `0x23`) o așază exact o dată (u de la -1 la 0, v de la 1 la 2, cu câteva miimi peste în nivelurile mai grosiere de detaliu). Când primul set lasă o copie a imaginii și al patrulea sau al treilea se află într-una, foaia se desenează prin acela, mutată în 0 până la 1. O foaie cu alfa se desenează cu 1 cm în fața suprafeței pe care este pictată, care se desenează sub ea în cealaltă hartă de culoare a blocului prin primul set: fără asta, texelii goi ai foii arătau interiorul peretelui. Al doilea set este desfășurarea unui obiect pentru suprapunerea lui și nu se folosește aici.

**Hărți decupate.** Al patrulea canal al hărții de culoare înseamnă lucruri diferite după numele hărții. În `_cs`, de departe cel mai comun (893 din hărțile alese ale unui nivel), este netezimea: 1% din alfa unei hărți medii se află la 0,1 de 0 sau 1. În `_cu` (frunze, iarbă) și `_ca` (culoare și alfa) este opacitate: 90% și 87%. O hartă de culoare numită `..._cu` sau `..._ca` a cărei alfa este cel puțin 75% aproape de 0 sau 1, cel puțin 1% sub 0,5 și cel puțin 5% peste se scrie cu alfa ei, ca PNG, iar materialul ei ca `alphaMode` MASK glTF, `alphaCutoff` 0,5, cu două fețe; cărțile de frunze arată atunci frunze, nu colțurile lor negre. O hartă de frunze a unui copac nu are deloc alfa (4 din 255 cel mult): frondele lui sunt tăiate de geometrie, iar cu doar primele două condiții întreaga coroană ieșea tăiată.

Coordonatele de textură sunt utilizarea de vârf `0x21`, doi semi-float-uri (format 6) sau două float-uri (format 2). Secțiunile au până la trei seturi în plus (`0x22` până la `0x24`) pentru straturile de decal și de detaliu. Coordonatele se repetă: partea nervurată a unui container merge de la -1,6 la 1,8, plăcile fundalului de teren stau în întregime în afara intervalului 0..1, iar într-un nivel 23% din triunghiurile texturate ajung în afara lui 0..1. Ele se scriu cum sunt, cu un eșantionator care se repetă; vizualizatorul 3DHeat împachetează fiecare textură repetitivă în atlasul lui. Un renderer care le fixează în loc le întinde nervurile la dublul lățimii lor, transformă o podea de beton în dungi pe o axă și dă grinzilor de oțel ale unui turn culoarea de margine a texturii lor; pentru el, `--clamped-uvs` taie fiecare triunghi de-a lungul liniilor unde textura lui se repetă și mută fiecare bucată în 0..1 (vedeți [Formatul de ieșire](output-format.md)). Apoi 0,03% din triunghiurile texturate, peste care o textură se repetă de mai mult de 16 ori, ajung în afară, iar un triunghi pe care tăierea l-ar face în mai mult de 4 bucăți se desenează în culoarea medie a texturii în loc: scoarța se repetă pe fiecare ramură, iar tăiată, copacii unui nivel au trecut de la 6,4 la 24 de milioane de triunghiuri.

Harta de înălțimi nu are o hartă de culoare proprie care să se poată citi. Unde o hartă a fundalului de teren o acoperă, se colorează din ea: coordonatele de textură ale fundalului sunt o funcție liniară de x și z ai lumii (99% din vârfuri în 0,001 de ea; harta acoperă un pătrat de 65.536 m, răsucit cu un sfert), iar aceeași funcție dă și pe cele ale hărții de înălțimi. Nivelul livrează mip-urile acelei hărți de la 2.048 px în jos, deci harta de înălțimi primește 32 m un pixel. Stânca lui întunecată stă pe terenul abrupt: corelația dintre întuneric și pantă este 0,48, și cel mult 0,34 pentru celelalte șapte orientări.

Fundalul unui alt nivel este opt plăci apropiate și opt îndepărtate în jurul zonei de joc, fiecare repetându-și propria textură pe tot cuprinsul plăcii, iar niciuna nu ajunge la harta de înălțimi. Fiecare textură de fundal se potrivește separat, iar când niciuna nu acoperă harta de înălțimi, ia culoarea medie pe care o arată fundalul la mai puțin de un kilometru de pătratul terenului, pe care o coace `--ground-texture` cu decalurile peste ea. Un material de fundal este unul al cărui nume conține `TerrainBackdrop`, sau `BD_` și `Terrain` (`M_BD_<site>_Terrain..._Near`); sau un mesh de fundal (`bd_..._terrain<site>_04_far_mesh`) poartă un material simplu de teren (`M_<region>_Terrain<site>_04_Far`), pe care primele două reguli le-au ratat într-un nivel și deci i-au colorat solul din suprafețele lui.

Acolo unde nicio hartă de fundal nu acoperă harta de înălțimi, însă, aceasta ia culoarea medie a suprafețelor proprii ale terenului înaintea mediei fundalului: hărțile `_cv` pe care le numesc blocurile de shader ale grafului lui de straturi (27 într-un nivel: nisipuri, pietrișuri, soluri, iarbă, beton crăpat), fiecare mediată, apoi mediana fiecărui canal, lăsând afară suprafața implicită a motorului. Un fundal poate fi cu totul alt peisaj: media lui (95, 99, 80 în sRGB) a transformat solul zonei de joc într-un gri pe care jocul nu îl arată. Cu `--ground-texture`, culoarea aceea se înmulțește cu de două ori harta de culoare, ceea ce lasă neschimbat gri-mijlociu, și se coace cu decalurile peste ambele extinderi, a decalurilor și a hărții de culoare.

Față de joc, culoarea mediană a solului fiecărei zone de joc coapte și a cadrelor de joc (rândurile de la 55 până la 72% din imagine, lângă HUD; 24 de cadre per nivel; sRGB; cadrele sunt luminate și gradate, deci rapoartele r/g și b/g sunt comparația corectă):

| Nivel | Cadre | Media fundalului | Acum |
|---|---|---|---|
| primul | 167, 140, 109 (1,19, 0,78) | 95, 99, 80 (0,96, 0,81) | 117, 108, 86 (1,08, 0,80) |
| al doilea | 72, 71, 74 (1,01, 1,04) | 117, 110, 104 (1,06, 0,95) | 146, 135, 117 (1,08, 0,87) |
| al treilea | 83, 89, 82 (0,93, 0,92) | 160, 148, 136 (1,08, 0,92) | 148, 137, 117 (1,08, 0,85) |

Primul este corectat; celelalte două erau puțin mai aproape de nuanță înainte. O singură culoare pentru un nivel întreg nu poate fi corectă peste tot; măștile ar fi.

## Plasa de navigare {#navigation-mesh}

Sursă: [`frostbitenav.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/frostbitenav.py).

Un nivel livrează câte o partiție per agent, `<level>/dbt/<level>_navmesh_layer_<n>`: într-un nivel, stratul 0 este soldatul (1,8 m înălțime, 0,18 m pas, rază de 0,4 m), iar alte două sunt vehicule (3,5 și 10 m înălțime). Fiecare partiție ține două tablouri:

| Tablou | Element |
|---|---|
| plăci | 28 de octeți: u32 0, u32 hash, u32 0, u32 indexul fragmentului, u16 x al plăcii, u16 z al plăcii, u32 offset, u32 mărime |
| fragmente | 20 de octeți: GUID-ul fragmentului, u32 mărime |

O placă este `size` octeți la `offset` în fragmentul `chunk index`, little-endian, și este aranjată ca Detour (Recast Navigation), după un antet mai lung:

| Offset | Conținut |
|---|---|
| 0 | `VAND`, versiunea 7 |
| 24 | numărători: poligoane, vârfuri, legături, mesh-uri de detaliu, vârfuri de detaliu, triunghiuri de detaliu, noduri de volum de delimitare, legături în afara mesh-ului, primul poligon din afara mesh-ului |
| 188 | înălțimea agentului, pasul, raza |
| 200 | cutia de delimitare a plăcii, șase float-uri |
| 232 | vârfuri: float-uri x, y, z, coordonate lume |
| următorul limită de 8 octeți | poligoane, 32 de octeți: u32, șase indici de vârf u16, șase vecini u16, flag u16, numărul de vârfuri la +30, la +31 aria (cei șase biți mici) și tipul (cei doi de sus) |
| apoi, împachetat | legături (16 octeți), mesh-uri de detaliu (12: primul vârf de detaliu u32, primul triunghi de detaliu u32, numărul de vârfuri și triunghiuri u8), vârfuri de detaliu (trei float-uri), triunghiuri de detaliu (trei indici și flag-uri), noduri de volum de delimitare (16), legături în afara mesh-ului (80) |

În fiecare placă a nivelurilor verificate, acestea adună exact mărimea plăcii, octet cu octet, iar mesh-urile de detaliu numerotează poligoanele dinaintea primului poligon din afara mesh-ului.

Un poligon este plat între colțurile lui; **mesh-ul lui de detaliu** ține înălțimea reală a suprafeței peste denivelări, stânci și trepte, și este ce se desenează. Un indice de triunghi de detaliu sub numărul de colțuri ale poligonului este acel colț, altfel vârful de detaliu `first + index - corners`. Triangularea poligoanelor în evantai în loc pune mult mai multe triunghiuri sub teren și face fâșii lungi; cu mesh-urile de detaliu niciunul nu este mai lung decât diagonala unei plăci de 16 m plus pasul în sus al unei pante.

Tipul 0 este sol, tipul 2 petice mici și abrupte (aproximativ 45 de grade, un metru pătrat fiecare), tipul 1 o legătură între suprafețe: colțurile ei acoperă 125 m sau mai mult pe înălțime și stau în afara plăcii, unele în origine. Legăturile se lasă afară; restul se desenează prin mesh-urile lor de detaliu, sau se triunghiulează în evantai într-o placă fără niciunul.

Verificări: mărimile fragmentelor se adună exact cu ale plăcilor; fiecare vârf de suprafață se află în cutia plăcii lui cu o abatere de aproximativ un metru; aproape toate triunghiurile sunt cu fața în sus. O placă care eșuează este refuzată și numărată, iar într-un nivel nu eșuează niciuna.

Ce acoperă plasa soldatului, privită de sus, în nivelul de test: solul, podelele, scările și unele acoperișuri, și nu vârfurile containerelor de marfă. Este harta AI a locurilor unde poate sta un soldat, cel mai apropiat lucru pe care îl arată fișierele de locul unde stau jucătorii.

## Neimplementate {#not-implemented}

- Graficul de straturi al terenului, care amestecă straturile lui de suprafață (vedeți [Straturile terenului](#terrain-layers)): culoarea solului urmează o regulă proprie a acestui cititor, din măștile straturilor și panta hărții de înălțimi, iar nivelurile ale căror pagini de mască nu se potrivesc între ele primesc o singură culoare.
- Parametrii de culoare ai materialelor de decal: marcajele prin mască de canale se pictează într-o culoare neutră.
- Planuri de obiecte care nu sunt mesh-uri (logică de joc, efecte, sunete).
- Stările distruse ale mesh-urilor distructibile: locurile părților lor sunt în fișierul de distrugere, care nu se citește.
- Legăturile plasei de navigare (sărituri, scări, escaladări) și straturile ei pentru vehicule.
- Mesh-uri de nivel stocate în linie în res (10 mesh-uri într-un nivel, accesorii), oasele și părțile mesh-urilor skinned și composite, și normalele (calculate de scriitor).
- Hărți de normală, de rugozitate și alte hărți; alfa în afară de o hartă decupată (sticla translucidă și decalurile se desenează opace).
- Găuri în teren: un shader de suprafață pentru găuri este numit, dar ce citește nu se găsește (vedeți [Straturile terenului](#terrain-layers)), deci harta de înălțimi nu se taie acolo unde terenul pe care se merge trece pe sub ea.
- Ce nuanță merge cu ce canal al măștii unui material: o hartă de culoare gri ia prima nuanță care nu este neutră (vedeți [Texturi și materiale](#textures-and-materials)).
- Efecte (căi `fx/`) și mesh-urile de cablu, ale căror cutii de delimitare au zeci de kilometri; sunt lăsate afară și numărate în rezumat.
- Forma de tabel XOR obfuscată.
