---
title: Omezení a známé mezery
nav_order: 10
lang: "cs"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Omezení a známé mezery {#limits-and-known-gaps}

Co nástroj nedělá, co dělá jen částečně a kde je jeho chování nerovnoměrné. Většina
mezer jsou záměrná odmítnutí. Dekódování bez souboru, na kterém by se ověřilo,
vyprodukuje výstup, který vypadá správně a správný není.

## Hry {#games}

| Hra | Export trati | Proč ne, nebo jak daleko |
|---|---|---|
| Forza Horizon | ano | barva země je interpretace (viz níže) |
| BeamNG.drive | ano | bez porostu země, opakující se textury modelů zploštělé |
| Assetto Corsa Rally | ano | modely s plochými barvami; zatím neproběhlo kolo nahrané ve hře |
| Assetto Corsa EVO | **ne** | všechen obsah je v jednom balíčku obfuskovaném klíčem a tento nástroj žádné klíče neobnovuje |
| Battlefield 6 (export úrovně, `level`) | ano, celá úroveň | terén, seskupené a jednotlivě umístěné sítě a jejich barevné mapy, navigační síť vojáků, vyříznutá vegetace; barva herní plochy je hrubá (32 m na pixel, nebo jedna průměrná barva); bez průhlednosti a normálových map; ničitelné sítě označené, jejich zničené stavy se neexportují |
| Unreal 5 World Partition (export mapy, `ue-map`) | ano, celá mapa | krajina přesně; budovy jako zjednodušené sítě HLOD mapy, ne plné modely; vodní plochy; bez vegetace, dekorací a barvy země |
| Arma Reforger (export světa, `enfusion-world`) | ano, celý svět | terén v jeho vlastních barvách a moře; budovy, rekvizity a skály jako kvádry z modelů, ne jejich trojúhelníky; stromy na přání (`--trees`), jako kvádry; bez jezer, řek a podřízených entit |
| iRacing | **ne** | tratě jsou dodávané v chráněném formátu, který není cílem extrakce souborů |
| cokoli jiného | **ne** | není čtečka tratí; rekonstruujte z hraní pomocí 3DHeat GameCapture, nebo analyzujte kola v kartě Analýza závodu v prohlížeči bez trati |

## Enginy a formáty {#engines-and-formats}

| Formát | Neimplementováno |
|---|---|
| Unreal `.pak` | verze před 8; indexy jen s hashi cest (jména nejdou obnovit); položky v přetokovém seznamu indexu (přeskočí se); dekódování obsahu `.uasset`/`.umap` z paku |
| Unreal IoStore | šifrované kontejnery (odmítnuty, žádná volba klíče); výpis kontejneru bez indexu adresáře (nejmenuje soubory); verzované balíčky; sítě jen pro Nanite a ne uložené uvnitř; kostrové sítě; vlastnosti tříd bez schématu; vlastnosti instancovaných komponent (rozložení se v buildu hry změnilo); spline sítě a dekorační komponenty |
| Unity | formáty před 22 (Unity 2019 a starší); soubory s vloženými stromy typů; komprimované sítě; každá třída kromě `Mesh`, takže žádné transformace, materiály ani scény; `meshes` na bundlu; `list`/`extract` (použijte `meshes`) |
| Frostbite | tabulky obfuskované XOR; graf vrstev terénu (masky čteny asi u třetiny kontrolovaných úrovní); blueprinty objektů jiné než sítě (herní logika, efekty, zvuky); sítě úrovní uložené uvnitř; normálové a jiné mapy, alfa jiná než výřezy; díry v terénu; knihovna typů (šifrovaná v počátečním souborovém systému, nedotčena); příkaz pro výpis nebo extrakci jednotlivých assetů |
| Source 2 | zkompilované assety (`.vmdl_c`, `.vtex_c`); navigační síť CS2 (verze 36) |
| ForzaTech | formáty pozic jiné než čtyři škálované shorty; formáty indexů jiné než u16; kódy textur jiné než 0, 9, 13; vrstvy materiálů shaderu terénu; tangenty |
| BeamNG | kožované a dekorační sítě; animace; procedurální porost; scenérie na okraji světa |
| Unreal krajiny a mapy World Partition | krajiny, jejichž výškové mapy jsou v zapečených buňkách; vrstvy úprav a díry; sítě krajiny Nanite; plné modely umístěné v buňkách; vegetace; materiály krajiny |
| Enfusion | trojúhelníky modelů (geometrie `.xob` je komprimovaná v rozložení, které se nečte); `.edds` s hlavičkami před DX10; hodnoty vnořených objektů v souborech světa (přeskočí se, počítají se); podřízené entity; generovaná jezera a řeky; `list`/`extract` na `.pak` |

## Chování, které stojí za to znát {#behaviour-worth-knowing}

- **Barva země ve Forze není barva hry.** Zapečená textura se kreslí z mapových
  dlaždic, které říkají, *kde* je asfalt, krátká tráva, drsný terén a lesík. Používá
  pevné barvy a stínování, protože vrstvy materiálů shaderu terénu se nedekódují.
- **`--no-textures` odstraní i krajnici Forzy.** Rozdělení asfalt/krajnice používá
  masku asfaltu, která přichází se zapečenými mapami. Bez textur zůstanou pásy
  silnice celé jako silnice.
- **Rozpočet, který zadáte, může překročit jen obruby.** Obruby (a modely jízdní
  plochy BeamNG) se nikdy nezjednodušují ani nevynechávají, v žádné hře, takže
  rozpočet `--detail-budget` menší než jejich cena překročí jen ony; všechno ostatní
  se vynechá jako první. Viz [Úrovně detailu a rozpočet](detail-budget.md).
- **Možnosti, které se netýkají dané hry, se tiše ignorují:** `--season` pro BeamNG
  a AC Rally, `--track` pro BeamNG a AC Rally, `--level`/`--install` pro Forzu.
- **Barva země úrovně Battlefield 6 je hrubá mimo dekály.** Výškové pole se
  obarví podle barevné mapy kulisy terénu, 32 m na pixel na největším mipu, který
  úroveň obsahuje — nebo, kde žádná mapa kulisy nepokrývá, středovou barvou
  povrchových materiálů terénu; `--ground-texture` to vynásobí barevnou mapou terénu
  (v 0,5 m na pixel, kde ji úroveň má) a zapéká silnice, plochy, značení dráhy,
  stopy pneumatik a značky přes ni, v barvě nátěru jejich materiálu, kde je nastavena,
  a neutrální barvě, kde není; masky variací silnice se vynechávají. Hra mísí své
  povrchové vrstvy v grafu shaderů, který se nečte; export rozloží barvy vrstev
  podle jejich masek a sklonu výškového pole, podle vlastního pravidla, a úroveň,
  jejíž stránky masek do sebe nezapadají, dostane jednu barvu. Každá vrstva je
  střední hodnota své barevné mapy, ne její textura. Viz
  [Frostbite](reader-frostbite.md#terrain-layers). Kusy výškového pole v různém
  rozlišení se stýkají s malými schody.
- **Barevná mapa Battlefieldu 6 se vybírá, nečte.** Blok shaderu jmenuje každou
  texturu, kterou vzorkuje, ale neříká, která je barva; výběr se řídí názvem (viz
  [Frostbite](reader-frostbite.md#textures-and-materials)) a může vzít doplňkový nebo
  detailní list pro povrch. Listy dekorací (`t_de_...`) prohrávají s vlastní mapou
  povrchu; dekorace znaku, nakreslená jako jeho panel, ukazující jeho štít, se
  otočila o čtvrtinu. Pole vzdálenosti, palety a kanálové masky se nikdy nevezmou.
  Budovy kulisy se kreslí v barvách své palety; šedé mapy přejímají barvu materiálu
  podle pravidla samotného exportéru, protože parametry jsou hashované, a materiál,
  který maluje šedou mapu přes masku s několika barvami, dostane jednu z nich.
- **Terénní díry Battlefieldu 6 se nevyřezávají.** Kde pod výškovým polem běží
  choditelná země úrovně, hra musela terén vyříznout, a export to nedělá. Vyloučeno
  jako místo děr: masky vrstev terénu (žádná se tam nekoncentruje), jeho rastr uzlů
  67 x 67, rezervovaná hodnota výšky (žádná stránka výšek neobsahuje 0 nebo 65 535),
  příznaky uzlů (všechny stejné), a sítě nebo assety, které zem řežou: pod zemí tam
  jsou skalní a útesové sítě a žádný asset úrovně není pojmenovaný pro díry, tunely
  nebo jeskyně. Dva stromy rastru jsou dekódovány délkovým kódováním, ale neumístěny,
  a jsou to to, co zbývá (viz [Frostbite](reader-frostbite.md#terrain-layers)).
- **Varianta objektu Battlefieldu 6 dosáhne sekce přes své dvojčata.** Varianta
  umístěné kopie vybere bloky shaderů svých sekcí podle klíče; kde síť nemá blok pro
  variantu, vezme se varianta sekce jiné sítě se stejným výchozím blokem (viz
  [Frostbite](reader-frostbite.md#textures-and-materials)). To je pravidlo exportéru;
  sekce bez dvojčete, které se mění, si zachová výchozí vzhled.
- **Vrstvené materiály Battlefieldu 6 se kreslí jako jejich základ a jeden list.**
  Stěnový panel s nápisy se kreslí jako jeho omítka s listem písma přes ni; ostatní
  vrstvy materiálu (přemaz přes svou masku, detailní a mechové mapy) se nemíchají.
- **Navigační síť je síť AI, ne hráčů.** Pokrývá to, kam voják může dojít: zem,
  podlahy a schody a některé střechy, ale ne každé vysoké místo. Spojení mezi
  povrchy (skoky, žebříky, přeskoky) se vynechávají.
- **Úroveň Battlefieldu 6 obsahuje vrstvu každého herního režimu.** Objekty, které
  jen jeden režim umisťuje, se mohou překrývat s jiným. `--skip` vynechá vrstvy podle
  názvu.
- **`courses` je jen pro Forzu** a bere jen složky knihovny pojmenované `... (course_...)`.
- **Soustava kola BeamNG se předpokládá** jako soustava prohlížeče `(x, z, -y)`, kterou
  zapisuje záznamník 3DHeat. Kola z jiného záznamníku v surové soustavě BeamNG by se
  neumístila.
- **`list` a `extract` berou archivy, ne každý formát.** Otevřou `.pak`, IoStore
  `.utoc`, `.vpk`, `.minizip` a zip. Kontejner Unity se čte přes `meshes`, úroveň
  Frostbite přes `level`, a `.cdae` nebo `.ter` je soubor, ne archiv (`identify` ho
  pojmenuje). `.minizip` bez `ChunkContentsMiniZip<n>.txt` vedle sebe se vypíše podle
  čísla položky.
- **Umístěné modely v BeamNG používají opakující se textury jako průměrné barvy**,
  protože vzorkovač `.glb` ořezává a prohlížeč balí textury do atlasu.
- **V praxi jen Windows.** Cesty Steamu pod `C:\Program Files`, `%LOCALAPPDATA%`,
  `C:\XboxGames`, a `*_win64.dll` pro Oodle. Jiné platformy nejsou otestované.

## Neověřeno {#unverified}

- Starší verze Pythonu (nástroj se spouštěl s 3.13).
- Assetto Corsa Rally s kolem nahraným ve hře. Testováno jen se syntetickými koly v
  náhodných soustavách.
- Prohlížeče glTF jiné než prohlížeč 3DHeat.
- Zda je soustava každé hry levotočivá nebo pravotočivá. Export zachovává telemetrickou
  soustavu každé hry, takže kola a tratě sedí tak či onak.
- Význam lokální hodnoty z = 0 u `WaterBlock` jako hladiny (BeamNG).
- Umísťování Frostbite ve hrách jiných než Battlefield 6 a v Battlefieldu 6 po
  aktualizaci, která změní rozložení členů skupiny. Čtečka pak žádné skupiny nenajde
  a řekne to.
- Zda export Battlefieldu 6 sedí na pozicích, které hra hlásí. Souřadnice jsou
  vlastní hry jako u ostatních her, ale zatím nebyl přes žádnou položen žádný záznam.
