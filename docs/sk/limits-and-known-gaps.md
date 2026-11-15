---
title: Obmedzenia a známe medzery
nav_order: 10
lang: "sk"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Obmedzenia a známe medzery {#limits-and-known-gaps}

Čo nástroj nerobí, čo robí len čiastočne a kde je jeho správanie nerovnomerné. Väčšina
medzier sú zámerné odmietnutia. Dekódovanie bez súboru, voči ktorému by sa dalo
overiť, vyrába výstup, ktorý vyzerá správne a nie je.

## Hry {#games}

| Hra | Export trate | Prečo nie, alebo do akej miery |
|---|---|---|
| Forza Horizon | áno | farba povrchu je interpretácia (pozri nižšie) |
| BeamNG.drive | áno | žiadny porast povrchu, opakujúce sa textúry modelov sú zploštené |
| Assetto Corsa Rally | áno | modely v plošných farbách; zatiaľ nebežalo na kole nahranom v hre |
| Assetto Corsa EVO | **nie** | všetok obsah je v jednom balíku zakrytom kľúčom a tento nástroj žiadne kľúče nezískava |
| Battlefield 6 (export levelu, `level`) | áno, celý level | terén, zoskupené aj jednotlivo umiestnené siete a ich farebné mapy, navigačná sieť vojakov, vystrihnutá vegetácia; farba terénu hracej oblasti je hrubá (32 m na pixel, alebo jedna priemerná farba); žiadna priehľadnosť ani normálové mapy; ničiteľné siete označené, ich zničené stavy sa neexportujú |
| Unreal 5 hry World Partition (export mapy, `ue-map`) | áno, celá mapa | krajina presne; budovy ako zjednodušené siete HLOD mapy, nie plnodetailné modely; vodné plochy; žiadna vegetácia, dekály ani farba povrchu |
| Arma Reforger (export sveta, `enfusion-world`) | áno, celý svet | terén vo vlastných farbách a more; budovy, rekvizity a skaly ako boxy ich modelov, nie ich trojuholníky; stromy na požiadanie (`--trees`), ako boxy; žiadne jazerá, rieky ani podradené entity |
| iRacing | **nie** | trate sa dodávajú v chránenom formáte, ktorý nie je cieľom extrakcie súborov |
| čokoľvek iné | **nie** | neexistuje čítačka tratí; zrekonštruujte z hrania pomocou 3DHeat GameCapture, alebo analyzujte kolá na karte Analýza pretekov v prehliadači bez trate |

## Enginy a formáty {#engines-and-formats}

| Formát | Nie je implementované |
|---|---|
| Unreal `.pak` | verzie pred 8; indexy len s hashmi ciest (názvy sa nedajú získať); položky v preplnenom zozname indexu (preskočené); dekódovanie obsahu `.uasset`/`.umap` z pak |
| Unreal IoStore | šifrované kontajnery (odmietnuté, žiadna možnosť kľúča); výpis kontajnera bez adresárového indexu (nepomenúva súbory); verzované balíky; siete len pre Nanite a siete neuložené vnútri; kostrové siete; vlastnosti tried bez schémy; vlastnosti inštancovaných komponentov (rozloženie sa zmenilo v builde hry); splinové siete a dekálové komponenty |
| Unity | formáty pred 22 (Unity 2019 a staršie); súbory s vloženými stromami typov; komprimované siete; každá trieda okrem `Mesh`, takže žiadne transformácie, materiály ani scény; `meshes` nad zväzkom; `list`/`extract` (použite `meshes`) |
| Frostbite | tabuľky zakryté XOR; graf vrstiev terénu (masky sa čítajú asi v tretine skontrolovaných levelov); objektové šablóny iné ako siete (herná logika, efekty, zvuky); úrovne sietí uložené vnútri; normálové a iné mapy, alfa iná ako výrezy; diery v teréne; knižnica typov (zašifrovaná v počiatočnom súborovom systéme, nedotknutá); príkaz na výpis alebo extrakciu jednotlivých assetov |
| Source 2 | skompilované assety (`.vmdl_c`, `.vtex_c`); navigačná sieť CS2 (verzia 36) |
| ForzaTech | formáty pozícií iné ako štyri škálované shorty; formáty indexov iné ako u16; kódy textúr iné ako 0, 9, 13; vrstvy materiálu shaderu terénu; tangenty |
| BeamNG | skinované a dekálové siete; animácia; procedurálny porast povrchu; scenéria pri okraji sveta |
| Unreal krajiny a mapy World Partition | krajiny, ktorých výškové mapy sú v zapečených bunkách; vrstvy úprav a diery; mriežky krajiny Nanite; plnodetailné modely umiestnené v bunkách; vegetácia; materiály krajiny |
| Enfusion | trojuholníky modelov (geometria `.xob` je komprimovaná v rozložení, ktoré sa nečíta); `.edds` s hlavičkami pred DX10; hodnoty vnorených objektov v súboroch sveta (preskočené, započítané); podradené entity; generované jazerá a rieky; `list`/`extract` nad `.pak` |

## Správanie, ktoré stojí za pozornosť {#behaviour-worth-knowing}

- **Farba povrchu Forzy nie je farba hry.** Upečená textúra sa kreslí z máp dlaždíc,
  ktoré hovoria *kde* sú asfalt, krátka tráva, drsný terén a lesík. Používa pevné
  farby a tieňovanie, pretože vrstvy materiálov shaderu terénu sa nedekódujú.
- **`--no-textures` odstráni aj krajnicu Forzy.** Rozdelenie asfalt/krajnica používa
  masku asfaltu, ktorá prichádza s upečenými mapami. Bez textúr zostanú pásy cesty
  celé ako cesta.
- **Rozpočet, ktorý zadáte, môžu prekročiť len obrubníky.** Obrubníky (a modely
  jazdného povrchu v BeamNG) sa nikdy nezjednodušia ani nevynechajú vo všetkých hrách,
  takže rozpočet `--detail-budget` menší, než čo stoja, prekročia samy; všetko ostatné
  sa najprv vynechá. Pozri [Úrovne detailu a rozpočet](detail-budget.md).
- **Možnosti, ktoré sa netýkajú danej hry, sa ticho ignorujú**: `--season` pre BeamNG
  a AC Rally, `--track` pre BeamNG a AC Rally, `--level`/`--install` pre Forzu.
- **Farba povrchu levelu Battlefield 6 je mimo dekálov hrubá.** Výškové pole sa
  farbí z farebnej mapy pozadia terénu, 32 m na pixel na najväčšom mipe, ktorý level
  obsahuje – alebo, kde žiadna mapa pozadia nepokrýva, v strednej farbe povrchových
  materiálov terénu; `--ground-texture` to násobí farebnou mapou terénu (pri 0,5 m
  na pixel, kde ju level má) a zapečie cesty, plochy, čiary dráhy, stopy pneumatík
  a značenie nad to, v farbe náteru ich materiálu, kde je nastavená, a neutrálnej
  farbe, kde nie; masky variácií ciest sa vynechajú. Hra mieša vrstvy povrchu v grafe
  shaderov, ktorý sa nečíta; export rozloží farby vrstiev podľa ich masiek a sklonu
  výškového poľa, podľa vlastného pravidla, a level, ktorého stránky masiek do seba
  nezapadajú, dostane jednu farbu. Každá vrstva je priemer svojej farebnej mapy, nie
  jej textúra. Pozri [Frostbite](reader-frostbite.md#terrain-layers). Kúsky výškového
  poľa s rôznym rozlíšením sa stretávajú s malými schodmi.
- **Farebná mapa Battlefield 6 sa vyberá, nečíta sa.** Blok shaderu pomenuje každú
  textúru, ktorú vzorkuje, bez toho, aby povedal, ktorá je farebná; výber sa robí
  podľa názvu (pozri [Frostbite](reader-frostbite.md#textures-and-materials)) a môže
  vybrať pomocnú alebo detailnú plochu pre povrch. Plochy dekálov (`t_de_...`) prehrávajú
  s vlastnou mapou povrchu; dekál značky nakreslený ako jej panel ukazoval jej štít
  otočený o štvrť. Distančné polia, palety a masky kanálov sa nikdy nevyberú. Budovy
  pozadia sa kreslia vo farbách svojej palety; šedé mapy preberú farbu materiálu podľa
  pravidla exportéra, pretože názvy parametrov sú hašované, a materiál, ktorý maľuje
  šedú mapu cez masku s viacerými farbami, dostane jednu z nich.
- **Diery v teréne Battlefield 6 sa nevyrezávajú.** Tam, kde pochôdzny terén levelu
  beží pod výškovým poľom, hra musela terén vyrezať, a export to nerobí. Vylúčené ako
  miesto dier: masky vrstiev terénu (žiadna sa nesústreďuje tam), jeho mriežka uzlov
  67 x 67, rezervovaná výšková hodnota (žiadna výšková stránka nemá 0 ani 65 535),
  príznaky uzlov (všetky rovnaké) a siete alebo assety, ktoré terén rušia: pod
  povrchom tam sú skalné a útesové siete a žiadny asset levelu nie je pomenovaný pre
  diery, tunely ani jaskyne. Dva stromy rastra sú dekódované po dĺžke, ale neumiestnené,
  a sú to to, čo zostáva (pozri [Frostbite](reader-frostbite.md#terrain-layers)).
- **Variácia objektu Battlefield 6 dosiahne sekciu cez svoje dvojčatá.** Variácia
  umiestnenej kópie vyberie bloky shaderov jej sekcií podľa kľúča; kde sieť nemá blok
  pre variáciu, vezme sa varianta sekcie inej siete s rovnakým predvoleným blokom
  (pozri [Frostbite](reader-frostbite.md#textures-and-materials)). To je pravidlo
  exportéra; sekcia bez dvojčaťa, ktorá sa mení, si ponechá predvolený vzhľad.
- **Vrstvené materiály Battlefield 6 sa kreslia ako ich základ a jeden list.** Stena
  s nápismi sa kreslí ako jej omietka s listom písma nad ňou; ďalšie vrstvy materiálu
  (zaprášenie cez jeho masku, detailné a machové mapy) sa nemiešajú.
- **Navigačná sieť je pre AI, nie pre hráčov.** Pokrýva, kam sa vojak môže dostať pešo:
  zem, podlahy a schody a niektoré strechy, ale nie každé vysoké miesto. Prepojenia
  medzi plochami (skoky, rebríky, preskoky) sa vynechajú.
- **Level Battlefield 6 obsahuje vrstvu každého herného režimu.** Objekty, ktoré
  umiestňuje len jeden režim, sa môžu prekrývať s iným. `--skip` vynechá vrstvy podľa
  názvu.
- **`courses` je len pre Forzu** a berie len priečinky knižnice pomenované
  `... (course_...)`.
- **Predpokladá sa rámec kola BeamNG** ako rámec prehliadača `(x, z, -y)`, ktorý
  zapisuje nahrávač 3DHeat. Kolá z iného nahrávača v surovom rámci BeamNG by sa
  neumiestnili.
- **`list` a `extract` berú archívy, nie každý formát.** Otvoria `.pak`, IoStore `.utoc`,
  `.vpk`, `.minizip` a zip. Kontajner Unity sa číta cez `meshes`, level Frostbite cez
  `level`, a `.cdae` alebo `.ter` je súbor, nie archív (`identify` ho pomenuje). Súbor
  `.minizip` bez `ChunkContentsMiniZip<n>.txt` vedľa seba sa vypíše podľa čísla položky.
- **Umiestnené modely v BeamNG používajú opakujúce sa textúry ako priemerné farby**,
  lebo vzorkovač `.glb` orezáva a prehliadač balí textúry do atlasu.
- **Prakticky len Windows.** Cesty Steamu pod `C:\Program Files`, `%LOCALAPPDATA%`,
  `C:\XboxGames` a `*_win64.dll` pre Oodle. Iné platformy nie sú testované.

## Neoverené {#unverified}

- Staršie verzie Pythonu (nástroj sa spúšťal s 3.13).
- Assetto Corsa Rally s kolom nahratým v hre. Testované iba so syntetickými kolami
  v náhodných rámcoch.
- Prehliadače glTF iné ako prehliadač 3DHeat.
- Či je rámec každej hry ľavo- alebo pravotočivý. Export zachováva telemetrický rámec
  každej hry, takže kolá a trate sa zarovnajú bez ohľadu na to.
- Význam lokálnej z = 0 bloku `WaterBlock` ako jeho hladiny (BeamNG).
- Umiestnenie Frostbite v hrách iných ako Battlefield 6 a v Battlefield 6 po aktualizácii,
  ktorá zmení rozloženie člena skupiny. Čítačka potom nenájde žiadne skupiny a povie to.
- Či export Battlefield 6 sedí s pozíciami, ktoré hra hlási. Súradnice sú vlastné hry,
  ako pri iných hrách, ale zatiaľ sa nepoložil na žiadny zaznamenaný záznam.
