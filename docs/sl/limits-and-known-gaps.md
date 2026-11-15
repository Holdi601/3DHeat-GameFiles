---
title: "Meje in znane vrzeli"
nav_order: 10
lang: "sl"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Meje in znane vrzeli {#limits-and-known-gaps}

Kaj orodje ne počne, kaj počne samo delno in kje je njegovo obnašanje neenakomerno. Večina vrzeli je namernih zavrnitev. Dekodiranje brez datoteke, s katero bi preverili, da je pravilno, da izhod, ki izgleda prav, pa ni.

## Igre {#games}

| Igra | Izvoz proge | Zakaj ne ali kako daleč |
|---|---|---|
| Forza Horizon | da | barva tal je interpretacija (glejte spodaj) |
| BeamNG.drive | da | brez rastlinja na tleh, ponavljajoče teksture modelov so poravnane |
| Assetto Corsa Rally | da | modeli v enobarvnih ploskvah; še ni bilo preizkušeno na krogu, posnetem v igri |
| Assetto Corsa EVO | **ne** | vsa vsebina je v enem paketu, zakrit s ključem, orodje pa nobenega ključa ne izlušči |
| Battlefield 6 (izvoz nivoja, `level`) | da, cel nivo | teren, združeni in posamično postavljeni meshi ter njihove barvne mape, navigacijska mreža vojakov, izrezano listje; barva tal območja igre je groba (32 m na piksel, ali ena povprečna barva); brez prosojnosti in normalnih map; uničljivi meshi so označeni, njihova uničena stanja niso izvožena |
| igre Unreal 5 s World Partition (izvoz zemljevida, `ue-map`) | da, cel zemljevid | krajina natančna; stavbe kot poenostavljeni HLOD meshi zemljevida, ne polni modeli; vodna telesa; brez rastlinja, nalepk ali barve tal |
| Arma Reforger (izvoz sveta, `enfusion-world`) | da, cel svet | teren v svojih barvah in morje; stavbe, rekviziti in skale kot škatle njihovih modelov, ne njihovi trikotniki; drevesa na zahtevo (`--trees`), kot škatle; brez jezer, rek ali otročjih entitet |
| iRacing | **ne** | proge so v zaščitenem formatu, ki ni cilj izvlečenja datotek |
| vse drugo | **ne** | ni bralnika prog; rekonstruirajte iz igranja s 3DHeat GameCapture ali analizirajte kroge v zavihku Analiza dirke pregledovalnika brez proge |

## Motorji in formati {#engines-and-formats}

| Format | Ni implementirano |
|---|---|
| Unreal `.pak` | različice pred 8; kazala samo z zgoščenimi potmi (imen ni mogoče dobiti nazaj); vnosi v prelivnem seznamu kazala (preskočeni); dekodiranje vsebine `.uasset`/`.umap` iz paka |
| Unreal IoStore | šifrirani kontejnerji (zavrnjeni, ni možnosti ključa); izpis kontejnerja brez imenika (ne imenuje datotek); različični paketi; meshi samo za Nanite in meshi, ki niso vgrajeni; skeletni meshi; lastnosti razredov brez sheme; lastnosti instanciranih komponent (postavitev se je spremenila v igrini gradnji); komponente spline mesh in komponente nalepk |
| Unity | formati pred 22 (Unity 2019 in starejši); datoteke z vgrajenimi drevesi tipov; stisnjeni meshi; vsak razred razen `Mesh`, zato ni transformacij, materialov ali scen; `meshes` na paketu; `list`/`extract` (uporabi `meshes`) |
| Frostbite | tabele, zakrite z XOR; graf plasti terena (maske prebrane v okoli tretjini pregledanih nivojev); predloge predmetov razen mrež (logika igre, učinki, zvoki); mrežne ravni, shranjene vrstično; normalne in druge mape, alfa razen izrezov; luknje v terenu; sistem tipov (šifriran v začetnem datotečnem sistemu, se ga ne dotika); ukaz za izpis ali izvlečenje posameznih sredstev |
| Source 2 | prevedena sredstva (`.vmdl_c`, `.vtex_c`); navigacijska mreža CS2 (različica 36) |
| ForzaTech | formati položajev razen štirih skaliranih shortov; formati indeksov razen u16; kode tekstur razen 0, 9, 13; plasti materialov senčilnika terena; tangente |
| BeamNG | meshi s skeleti in nalepkami; animacija; proceduralno rastlinje na tleh; scenografija ob robu sveta |
| Unreal krajine in zemljevidi World Partition | krajine, katerih višinske mape živijo v prevedenih celicah; plasti urejanja in luknje; mreže krajine za Nanite; polni modeli, postavljeni v celice; rastlinje; materiali krajine |
| Enfusion | trikotniki modelov (geometrija `.xob` je stisnjena v postavitvi, ki se ne bere); `.edds` s pred-DX10 glavami; vrednosti gnezdenih objektov v svetovnih datotekah (preskočene, prešteta); otročje entitete; ustvarjena jezera in reke; `list`/`extract` na `.pak` |

## Obnašanje, ki ga je vredno vedeti {#behaviour-worth-knowing}

- **Barva tal Forze ni igrina.** Pečena tekstura se riše iz zemljevidov ploščic, ki povedo, *kje* so asfalt, kratka trava, grob teren in gozd. Uporablja fiksne barve in senčenje, ker plasti materialov lastnega senčilnika terena niso dekodirane.
- **`--no-textures` odstrani tudi bankino Forze.** Delitev asfalt/bankina uporablja masko asfalta, ki pride s pečenimi zemljevidi. Brez tekstur ostanejo pasovi ceste celi kot cesta.
- **Proračun, ki ga podate, lahko preseže samo robnik.** Robniki (in modeli vozne površine BeamNG) se nikoli ne poenostavijo ali izpustijo, v nobeni igri, zato jih `--detail-budget`, manjši od njihove cene, preseže sam po sebi; vse drugo se izpusti najprej. Glejte [Stopnje podrobnosti in proračun](detail-budget.md).
- **Možnosti, ki se ne uporabljajo, se tiho prezrejo:** `--season` za BeamNG in AC Rally, `--track` za BeamNG in AC Rally, `--level`/`--install` za Forzo.
- **Barva tal nivoja Battlefield 6 je groba stran od njenih nalepk.** Višinska mreža je obarvana iz barvne mape pasu ozadja terena, na 32 m na piksel pri največjem mipu, ki ga nivo ponuja – ali, kjer nobena mapa ozadja ne pokrije, v srednji barvi površinskih materialov terena; `--ground-texture` to pomnoži z barvno mapo terena (pri 0,5 m na piksel, kjer jo nivo ima) in vžge ceste, ploščadi, označbe vzletišča, sledi gum in označbe v barvo tal, v barvi barve njihovih materialov, kjer je nastavljena, in nevtralni barvi, kjer ni; maske variacije cest niso vključene. Igra meša svoje površinske plasti v grafu senčilnika, ki ni prebran; izvoz razporedi barve plasti po njihovih maskah in naklonu višinske mreže, po pravilu, ki je njegovo lastno, in nivo, katerega strani mask se ne ujemajo, dobi eno barvo. Vsaka plast je povprečje njene barvne mape, ne njena tekstura. Glejte [Frostbite](reader-frostbite.md#terrain-layers). Kosi višinske mreže pri različnih ločljivostih se srečajo z majhnimi stopničkami.
- **Barvna mapa Battlefield 6 je izbrana, ne prebrana.** Blok senčilnika poimenuje vsako teksturo, ki jo vzorči, ne da bi povedal, katera je barva; izbira gre po imenu (glejte [Frostbite](reader-frostbite.md#textures-and-materials)) in lahko za površino izbere list za obrobo ali podrobnosti. Liste nalepk (`t_de_...`) izgubijo proti lastni mapi površine; nalepka znaka, narisana kot njegova plošča, je pokazala njegov ščit, zasukan za četrt. Mape razdalje, palete in kanalne maske se nikoli ne vzamejo. Stavbe ozadja so narisane v barvah svoje palete; sive mape vzamejo barvni ton materiala po pravilu izvoznika, ker so imena parametrov zgoščena, in material, ki slika sivo mapo skozi masko z več toni, dobi enega od njih.
- **Luknje v terenu Battlefield 6 niso izrezane.** Kjer hodljivo tlo nivoja teče pod višinsko mrežo, mora igra teren izrezati, izvoz pa tega ne naredi. Izključeno kot kraj lukenj: maske plasti terena (nobena se ne zbira tam), njegova rastrska mreža 67 x 67 vozlišč, rezervirana višinska vrednost (nobena stran višin ne vsebuje 0 ali 65.535), zastavice vozlišč (vse enake) ali meshi in sredstva, ki tla režejo: tam postavljeno je kamenje in skalnata stena, nobeno sredstvo nivoja pa ni poimenovano za luknje, predore ali jame. Dva rastrska drevesa sta dekodirana z dolžino tekov, vendar nista postavljena, in to sta, kar ostane (glejte [Frostbite](reader-frostbite.md#terrain-layers)).
- **Različica predmeta Battlefield 6 doseže odsek prek svojih dvojčkov.** Postavljena kopija variacije izbere bloke senčilnikov svojih odsekov po ključu; kjer mesh nima bloka za variacijo, se vzame varianta odseka drugega mesha z enakim privzetim blokom (glejte [Frostbite](reader-frostbite.md#textures-and-materials)). To je pravilo izvoznika; odsek brez dvojnika, ki se spreminja, ohrani svoj privzeti videz.
- **Večplastni materiali Battlefield 6 so narisani kot njihova osnova in ena plast.** Stenska plošča z napisi je narisana kot njen omet s črkovno plastjo čez njega; druge plasti materiala (prekrivni umazanija skozi svojo masko, podrobnostne in mahovne mape) se ne mešajo.
- **Navigacijska mreža je AI-jeva, ne igralčeva.** Pokriva, kam lahko vojak hodi: tla, tla in stopnice ter nekatere strehe, ne pa vsakega visokega mesta. Povezave med površinami (skoki, lestve, preskoki) so izpuščene.
- **Nivo Battlefield 6 vključuje sloj vsakega igralnega načina.** Predmeti, ki jih postavi samo en način, se lahko prekrivajo z drugim. `--skip` izpusti sloje po imenu.
- **`courses` je samo za Forzo** in poišče samo mape knjižnice z imenom `... (course_...)`.
- **Predpostavljen je koordinatni sistem kroga BeamNG**, pregledovalnikov okvir `(x, z, -y)`, ki ga piše snemalnik 3DHeat. Krogi iz drugega snemalnika v surovem koordinatnem sistemu BeamNG se ne bi postavili.
- **`list` in `extract` vzameta arhive, ne vsakega formata.** Odpreta `.pak`, IoStore `.utoc`, `.vpk`, `.minizip` in zip. Kontejner Unity se prebere z `meshes`, nivo Frostbite z `level`, `.cdae` ali `.ter` pa je datoteka, ne arhiv (`identify` ju poimenuje). `.minizip` brez `ChunkContentsMiniZip<n>.txt` ob sebi se izpiše po številki vnosa.
- **Postavljeni modeli v BeamNG uporabljajo ponavljajoče teksture kot povprečne barve**, ker vzorčevalnik `.glb` tekstur zapira in pregledovalnik jih pakira v atlas.
- **V praksi samo Windows.** Poti Steam pod `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames` in `*_win64.dll` za Oodle. Druge platforme niso preizkušene.

## Neoverjeno {#unverified}

- Starejše različice Pythona (orodje je bilo zagnano s 3.13).
- Assetto Corsa Rally s krogom, posnetim v igri. Preizkušeno je bilo samo s sintetičnimi krogi v naključnih koordinatnih sistemih.
- Pregledovalniki glTF razen pregledovalnika 3DHeat.
- Ali je koordinatni sistem vsake igre levosučen ali desnosučen. Izvoz ohrani telemetrični koordinatni sistem vsake igre, zato se krogi in proge poravnajo ne glede na to.
- Pomen `WaterBlock` z lokalnim z = 0 kot njegove površine (BeamNG).
- Postavitev Frostbite v igrah razen Battlefield 6 in v Battlefield 6 po posodobitvi, ki spremeni postavitev člana skupine. Bralnik potem ne najde skupin in to pove.
- Ali se izvoz Battlefield 6 poravna s položaji, ki jih igra poroča. Koordinate so igrine lastne, kot pri drugih igrah, vendar še nobeden posnetek ni bil položen čez enega.
