---
title: "Kufijtë dhe boshllëqet e njohura"
nav_order: 10
lang: "sq"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Kufijtë dhe boshllëqet e njohura {#limits-and-known-gaps}

Çfarë nuk bën mjeti, çfarë bën vetëm pjesërisht, dhe ku sjellja e tij është
e pabarabartë. Shumica e boshllëqeve janë refuzime të qëllimshme. Dekodimi pa një skedar për t'u kontrolluar
prodhon dalje që duket e saktë dhe nuk është.

## Lojërat {#games}

| Loja | Eksporti i kursit | Pse jo, ose deri ku |
|---|---|---|
| Forza Horizon | po | ngjyra e tokës është një interpretim (shih më poshtë) |
| BeamNG.drive | po | pa mbulesë toke, teksturat që përsëriten të modeleve të sheshuara |
| Assetto Corsa Rally | po | modele me ngjyra të sheshta; ende i paekzekutuar mbi një xhiro të regjistruar në lojë |
| Assetto Corsa EVO | **jo** | e gjithë përmbajtja është në një paketë të vetme të turbulluar me një çelës, dhe ky mjet nuk rikuperon çelësa |
| Battlefield 6 (eksporti i nivelit, `level`) | po, një nivel i plotë | terreni, rrjetat e grupuara dhe të vendosura individualisht dhe hartat e tyre të ngjyrave, rrjeta e navigimit e ushtarëve, gjethet cut-out; ngjyra e tokës së zonës së lojës është e trashë (32 m për piksel, ose një ngjyrë mesatare); pa tejdukshmëri ose harta normalesh; rrjetat e shkatërrueshme janë të etiketuara, gjendjet e tyre të shkatërruara nuk eksportohen |
| Lojërat Unreal 5 World Partition (eksporti i hartës, `ue-map`) | po, një hartë e plotë | peizazhi i saktë; ndërtesat si rrjetat HLOD të thjeshtuara të hartës, jo modelet me detaj të plotë; trupat ujorë; pa gjethe, decal-e ose ngjyrë toke |
| Arma Reforger (eksporti i botës, `enfusion-world`) | po, një botë e plotë | terreni me ngjyrat e veta dhe deti; ndërtesat, objektet dhe shkëmbinjtë si kutitë e modeleve të tyre, jo trekëndëshat e tyre; pemët sipas kërkesës (`--trees`), si kuti; pa liqene, lumenj ose entitete fëmijë |
| iRacing | **jo** | pistat dërgohen në një format të mbrojtur që nuk është objektiv nxjerrjeje skedarësh |
| gjithçka tjetër | **jo** | nuk ka lexues kursi; rindërtoje nga loja me 3DHeat GameCapture, ose analizo xhirot në skedën Analiza e garës të shikuesit pa kurs |

## Motorët dhe formatet {#engines-and-formats}

| Formati | Nuk është zbatuar |
|---|---|
| Unreal `.pak` | versionet para 8; indeksat vetëm me hash të shtegut (emrat nuk rikuperohen); hyrjet në listën e tejmbushjes të indeksit (anashkalohen); dekodimi i përmbajtjes `.uasset`/`.umap` nga një pak |
| Unreal IoStore | kontejnerët e enkriptuar (refuzohen, pa opsion çelësi); listimi i një kontejneri pa indeks direktorie (nuk emërton skedarë); paketat me version; rrjetat vetëm Nanite dhe jo të brendshme; rrjetat me skelet; vetitë e klasave pa skemë; vetitë e komponentëve me instanca (struktura ndryshoi në ndërtimin e lojës); rrjetat spline dhe komponentët decal |
| Unity | formatet para 22 (Unity 2019 e më të vjetra); skedarët me pemë llojesh të ngulitura; rrjetat e kompresuara; çdo klasë përveç `Mesh`, pra pa transformime, materiale ose skena; `meshes` në një paketë; `list`/`extract` (përdor `meshes`) |
| Frostbite | tabelat e turbulluara me XOR; grafi i shtresave të terrenit (maskat lexohen në rreth një të tretën e niveleve të kontrolluara); planet e objekteve përveç rrjetave (logjika e lojës, efektet, tingujt); nivelet e rrjetave të ruajtura brenda; hartat e normaleve dhe të tjera, alfa përveç cut-out; vrimat e terrenit; biblioteka e llojeve (e enkriptuar në sistemin fillestar të skedarëve, e paprekur); një komandë për të listuar ose nxjerrë asete të vetme |
| Source 2 | asetet e përpiluara (`.vmdl_c`, `.vtex_c`); rrjeta e navigimit e CS2 (versioni 36) |
| ForzaTech | formatet e pozicionit përveç katër shorts të shkallëzuar; formatet e indeksit përveç u16; kodet e teksturave përveç 0, 9, 13; shtresat e materialeve të shaderit të terrenit; tangjentet |
| BeamNG | rrjetat me skelet dhe decal; animacioni; mbulesa procedurale e tokës; peizazhi rreth skajit të botës |
| Peizazhet e Unreal dhe hartat World Partition | peizazhet hartat e lartësive të të cilave jetojnë në qelizat e gatuara; shtresat e redaktimit dhe vrimat; rrjetat e peizazhit Nanite; modelet me detaj të plotë të vendosura në qeliza; gjethet; materialet e peizazhit |
| Enfusion | trekëndëshat e modelit (gjeometria `.xob` është e kompresuar në një strukturë që nuk lexohet); `.edds` me koka para-DX10; vlerat e objekteve të futura në skedarët e botës (anashkalohen, numërohen); entitetet fëmijë; liqenet dhe lumenjtë e gjeneruar; `list`/`extract` në një `.pak` |

## Sjellje që vlen ta dish {#behaviour-worth-knowing}

- **Ngjyra e tokës së Forza nuk është ajo e lojës.** Teksturë e pjekur vizatohet nga
  hartat e pllakave që thonë *ku* janë asfalti, bari i shkurtër, toka e ashpër dhe pylli.
  Përdor ngjyra dhe hijezim fiks, sepse shtresat e vetë materialeve të shaderit të terrenit
  nuk dekodohen.
- **`--no-textures` heq edhe buzën e Forza.** Ndarja asfalt/buzë përdor
  maskën e asfaltit që vjen me hartat e pjekura. Pa tekstura, shiritat e rrugës mbeten
  të plotë si rrugë.
- **Një buxhet që e jep ti mund të tejkalohet vetëm nga bordurat.** Bordurat (dhe modelet e
  sipërfaqes së vozitjes të BeamNG) nuk thjeshtohen e nuk lihen kurrë jashtë, në asnjë lojë, prandaj një
  `--detail-budget` më i vogël se sa kushtojnë ato tejkalohet vetëm prej tyre; gjithçka
  tjetër lihet jashtë së pari. Shih [Nivelet e detajit dhe buxheti](detail-budget.md).
- **Opsionet që nuk zbatohen injorohen në heshtje**: `--season` për BeamNG dhe
  AC Rally, `--track` për BeamNG dhe AC Rally, `--level`/`--install` për Forza.
- **Ngjyra e tokës së një niveli Battlefield 6 është e trashë larg decal-eve të saj.** Fusha e
  lartësive ngjyroset nga harta e ngjyrave të sfondit të terrenit, 32 m për piksel në
  mip-in më të madh që dërgon niveli — ose, ku asnjë hartë sfondi nuk e mbulon, me
  ngjyrën e mesit të materialeve të sipërfaqes së terrenit; `--ground-texture`
  e shumëzon këtë me colormap të terrenit (me 0.5 m për piksel ku niveli
  ka një të tillë) dhe piq rrugët, platformat, vijat e pistës, gjurmët e gomave dhe
  shenjat mbi të, me ngjyrën e bojës së materialeve të tyre ku është caktuar një dhe me një
  ngjyrë neutrale ku jo; maskat e variacionit të rrugës lihen jashtë. Loja i përzien shtresat e sipërfaqes në një
  graf shaderi që nuk lexohet; eksporti i shtron ngjyrat e shtresave sipas
  maskave të tyre dhe pjerrësisë së fushës së lartësive, me një rregull të vetin, dhe një nivel hartat e faqeve të maskave
  të të cilit nuk përshtaten bashkë merr një ngjyrë. Çdo shtresë është
  mesatarja e hartës së saj të ngjyrave, jo teksturë e saj. Shih
  [Frostbite](reader-frostbite.md#terrain-layers). Pjesët e fushës së lartësive
  me rezolucione të ndryshme takohen me hapa të vegjël.
- **Një hartë ngjyrash e Battlefield 6 zgjidhet, nuk lexohet.** Një bllok shaderi emërton
  çdo teksturë që mostron pa thënë cila është ngjyra; zgjedhja shkon
  sipas emrit (shih [Frostbite](reader-frostbite.md#textures-and-materials)) dhe mund
  të zgjedhë një fletë zbukurimi ose detaji për një sipërfaqe. Fletët e decal-eve (`t_de_...`) humbasin
  përballë hartës së vetë sipërfaqes; decal-i i një tabele të vizatuar si paneli i saj tregoi
  mburojën e saj të kthyer një të katërtën. Fushat e largësisë, paletat dhe maskat e kanaleve nuk
  merren kurrë. Ndërtesat e sfondit vizatohen me ngjyrat e paletës së tyre; hartat gri
  marrin ngjyrimin e materialit me një rregull të vetë eksportuesit, pasi emrat e
  parametrave janë të hash-uar, dhe një material që lyen një hartë gri
  përmes një maske me disa ngjyrime merr njërin prej tyre.
- **Vrimat e terrenit të Battlefield 6 nuk priten.** Ku toka e ecshme e një niveli
  kalon nën fushën e lartësive, loja duhet ta ketë prerë terrenin, dhe eksporti nuk e
  bën. Të përjashtuara si vendi ku janë vrimat: maskat e shtresave të terrenit (asnjë nuk është
  e përqendruar atje), rrjeta e tij raster nyjesh 67 x 67, një vlerë e rezervuar lartësie (asnjë
  faqe lartësish nuk mban 0 ose 65,535), flamujt e nyjeve (të gjithë të njëjtë), dhe rrjetat
  ose asetet që presin tokën: ajo që vendoset nën tokë atje është
  rrjeta shkëmbinjsh dhe shkëmbijsh të pjerrët, dhe asnjë aset i nivelit nuk emërtohet për vrima,
  tunele ose shpella. Dy pemë raster dekodohen me run-length por nuk vendosen,
  dhe janë ajo që mbetet (shih [Frostbite](reader-frostbite.md#terrain-layers)).
- **Një variacion objekti i Battlefield 6 arrin një seksion përmes binjakëve të tij.**
  Variacioni i një kopjeje të vendosur zgjedh blloqet e shaderit të seksioneve të saj sipas çelësit; ku një
  rrjetë nuk ka bllok për një variacion, merret varianti i seksionit të një rrjete tjetër
  me bllok parazgjedhës identik (shih
  [Frostbite](reader-frostbite.md#textures-and-materials)). Ky është
  rregulli i eksportuesit; një seksion pa binjak që ndryshon e mban pamjen e tij parazgjedhëse.
- **Materialet me shtresa të Battlefield 6 vizatohen si baza e tyre dhe një fletë.**
  Një panel muri me shkronja vizatohet si suvaja e tij me fletën e shkronjave sipër;
  shtresat e tjera të materialit (papastërtia sipër përmes maskës së saj, hartat e detajit
  dhe myshkut) nuk përzihen.
- **Rrjeta e navigimit është e AI-së, jo e lojtarëve.** Mbulon ku mund të ecë një
  ushtar: tokën, dyshemetë dhe shkallët, dhe
  disa çatia, por jo çdo pikë të lartë. Lidhjet mes sipërfaqeve (kërcimet, shkallët, kapërcimet) lihen jashtë.
- **Një nivel Battlefield 6 përfshin shtresën e çdo mënyre loje.** Objektet që vetëm
  një mënyrë i vendos mund të mbivendosen me të një tjetre. `--skip` lë shtresat jashtë sipas emrit.
- **`courses` është vetëm për Forza**, dhe merr vetëm dosjet e bibliotekës me emra
  `... (course_...)`.
- **Korniza e xhiros BeamNG supozohet** të jetë korniza e shikuesit `(x, z, -y)` që e shkruan
  regjistruesi 3DHeat. Xhirot nga një regjistrues tjetër në kornizën e papërpunuar të BeamNG
  nuk do të vendoseshin.
- **`list` dhe `extract` marrin arkivat, jo çdo format.** Ato hapin një
  `.pak`, një IoStore `.utoc`, një `.vpk`, një `.minizip` dhe një zip. Një kontejner Unity
  lexohet me `meshes`, një nivel Frostbite me `level`, dhe një `.cdae` ose
  `.ter` është skedar dhe jo arkiv (`identify` e emërton). Një `.minizip`
  pa `ChunkContentsMiniZip<n>.txt` pranë tij listohet sipas numrit të hyrjes.
- **Modelet e vendosura në BeamNG i përdorin teksturat që përsëriten si ngjyra mesatare**, sepse
  mostruesi i `.glb` kap (clamp) dhe shikuesi i paketon teksturat në një atlas.
- **Praktikisht vetëm Windows.** Shtigje Steam nën `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames`, dhe një `*_win64.dll` për Oodle. Platformat e tjera
  nuk janë testuar.

## Të paverifikuara {#unverified}

- Versionet më të vjetra të Python (mjeti është ekzekutuar me 3.13).
- Assetto Corsa Rally me një xhiro të regjistruar në lojë. Është testuar vetëm
  me xhiro sintetike në korniza të rastësishme.
- Shikuesit glTF të ndryshëm nga shikuesi 3DHeat.
- Nëse korniza e çdo loje është e dorës së majtë apo së djathtë. Eksporti e mban kornizën e telemetrisë
  të çdo loje, prandaj xhirot dhe kurset përputhen sido që të jetë.
- Kuptimi i z = 0 lokal të `WaterBlock` si sipërfaqe e tij (BeamNG).
- Vendosja e Frostbite në lojëra të ndryshme nga Battlefield 6, dhe në Battlefield 6
  pas një përditësimi që ndryshon strukturën e anëtarit të grupit. Lexuesi atëherë nuk gjen
  grupe dhe e thotë.
- Nëse një eksport Battlefield 6 përputhet me pozicionet që raporton loja. Koordinatat
  janë ato të vetë lojës, si për lojërat e tjera, por asnjë regjistrim nuk është shtruar ende mbi një të tillë.
