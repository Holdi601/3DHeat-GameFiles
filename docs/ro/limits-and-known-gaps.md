---
title: "Limite și lacune cunoscute"
nav_order: 10
lang: "ro"
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Limite și lacune cunoscute {#limits-and-known-gaps}

Ce nu face instrumentul, ce face doar parțial și unde comportamentul său este inegal. Majoritatea lacunelor sunt refuzuri deliberate. Decodarea fără un fișier de verificare produce un rezultat care arată corect și nu este.

## Jocuri {#games}

| Joc | Export de circuit | De ce nu, sau cât de departe merge |
|---|---|---|
| Forza Horizon | da | culoarea solului este o interpretare (vezi mai jos) |
| BeamNG.drive | da | fără vegetație de sol, texturile repetate ale modelelor sunt aplatizate |
| Assetto Corsa Rally | da | modelele sunt în culori uniforme; nu a fost încă rulat pe un tur înregistrat în joc |
| Assetto Corsa EVO | **nu** | tot conținutul este într-un singur pachet obfuscat cu o cheie, iar acest instrument nu recuperează chei |
| Battlefield 6 (exportul de nivel, `level`) | da, un nivel întreg | terenul, mesh-urile grupate și plasate individual și hărțile lor de culoare, plasa de navigare a soldaților, vegetația decupată; culoarea solului din zona de joc este grosieră (32 m pe pixel, sau o singură culoare medie); fără translucență sau hărți de normale; mesh-urile distructibile sunt etichetate, stările lor distruse nu sunt exportate |
| jocuri Unreal 5 World Partition (exportul de hartă, `ue-map`) | da, o hartă întreagă | peisajul exact; clădirile ca mesh-urile HLOD simplificate ale hărții, nu modelele complete; corpuri de apă; fără vegetație, decalcomanii sau culoarea solului |
| Arma Reforger (exportul de lume, `enfusion-world`) | da, o lume întreagă | terenul în propriile lui culori și marea; clădirile, recuzita și stâncile ca casetele modelelor lor, nu triunghiurile lor; copaci la cerere (`--trees`), ca casete; fără lacuri, râuri sau entități copil |
| iRacing | **nu** | circuitele sunt livrate într-un format protejat, care nu este o țintă de extragere de fișiere |
| orice altceva | **nu** | nu există un cititor de circuite; reconstruiți din joc cu 3DHeat GameCapture sau analizați tururile în fila Race analysis a vizualizatorului, fără un circuit |

## Motoare și formate {#engines-and-formats}

| Format | Neimplementat |
|---|---|
| Unreal `.pak` | versiunile dinainte de 8; indexurile doar cu hash de cale (numele nu pot fi recuperate); intrări din lista de depășire a indexului (sărite); decodarea conținutului `.uasset`/`.umap` dintr-un pak |
| Unreal IoStore | containere criptate (refuzate, fără opțiune de cheie); listarea unui container fără index de directoare (nu numește fișiere); pachete versionate; mesh-uri doar Nanite și mesh-uri nestocate inline; mesh-uri cu schelet; proprietățile claselor fără schemă; proprietățile componentelor instanțiate (structura s-a schimbat în versiunea jocului); mesh-uri spline și componente de decalcomanii |
| Unity | formate dinainte de 22 (Unity 2019 și mai vechi); fișiere cu arbori de tipuri încorporați; mesh-uri comprimate; orice clasă în afară de `Mesh`, deci fără transformări, materiale sau scene; `meshes` pe un pachet; `list`/`extract` (folosiți `meshes`) |
| Frostbite | tabele obfuscate XOR; graful de straturi al terenului (măștile sunt citite în circa o treime din nivelurile verificate); plane de obiecte în afara mesh-urilor (logica de joc, efecte, sunete); nivelurile de mesh stocate inline; hărți de normale și alte hărți, alfa în afara decupărilor; găurile din teren; biblioteca de tipuri (criptată în sistemul de fișiere inițial, nu este atinsă); o comandă de listare sau extragere a unor active individuale |
| Source 2 | active compilate (`.vmdl_c`, `.vtex_c`); plasa de navigare CS2 (versiunea 36) |
| ForzaTech | formate de poziție altele decât patru scurte scalate; formate de index altele decât u16; coduri de textură altele decât 0, 9, 13; straturile de material ale shaderului de teren; tangente |
| BeamNG | mesh-uri cu schelet și de decalcomanii; animație; vegetație procedurală de sol; scenografie pe marginea lumii |
| Landscape-uri Unreal și hărți World Partition | landscape-uri ale căror câmpuri de înălțime stau în celulele compilate; straturi de editare și găuri; mesh-uri de landscape Nanite; modele cu detaliu complet plasate în celule; vegetație; materiale de landscape |
| Enfusion | triunghiurile modelelor (geometria `.xob` este comprimată într-un layout care nu este citit); `.edds` cu antete dinainte de DX10; valori de obiecte imbricate în fișierele de lume (sărite, numărate); entități copil; lacuri și râuri generate; `list`/`extract` pe un `.pak` |

## Comportamente care merită știute {#behaviour-worth-knowing}

- **Culoarea solului în Forza nu este cea a jocului.** Textura coaptă este desenată din hărțile de dale care spun *unde* sunt asfalt, iarbă scurtă, teren accidentat și pădure. Folosește culori și umbrire fixe, pentru că straturile de material ale shaderului terenului nu sunt decodate.
- **`--no-textures` îl elimină și pe acostamentul Forza.** Separarea asfalt/acostament folosește masca de asfalt care vine cu hărțile coapte. Fără texturi, fâșiile de drum rămân întregi, ca drum.
- **Un buget pe care îl dați poate fi depășit doar de borduri.** Bordurile (și modelele de suprafață de rulare ale BeamNG) nu sunt niciodată simplificate sau lăsate afară, în niciun joc, deci un `--detail-budget` mai mic decât costă ele este depășit de ele singure; orice altceva este lăsat afară primul. Vezi [Niveluri de detaliu și buget](detail-budget.md).
- **Opțiunile care nu se aplică sunt ignorate în tăcere**: `--season` pentru BeamNG și AC Rally, `--track` pentru BeamNG și AC Rally, `--level`/`--install` pentru Forza.
- **Culoarea solului unui nivel Battlefield 6 este grosieră departe de decalcomaniile sale.** Câmpul de înălțimi este colorat din harta de culoare a fundalului de teren, la 32 m pe pixel la cel mai mare mip livrat pentru nivel, sau, unde nicio hartă de fundal nu acoperă zona, în culoarea medie a materialelor de suprafață ale terenului; `--ground-texture` înmulțește asta cu harta de culoare a terenului (la 0,5 m pe pixel acolo unde nivelul are una) și coace peste ea drumurile, platformele, pistele, urmele de anvelope și marcajele, în culoarea de vopsea a materialelor lor, unde este setată, și într-o culoare neutră unde nu; măștile de variație ale drumurilor sunt lăsate afară. Jocul amestecă straturile de suprafață într-un graf de shadere care nu este citit; exportul așază culorile straturilor după măștile lor și după panta câmpului de înălțimi, printr-o regulă proprie, iar un nivel ale cărui pagini de mască nu se potrivesc primește o singură culoare. Fiecare strat este media hărții lui de culoare, nu textura lui. Vezi [Frostbite](reader-frostbite.md#terrain-layers). Bucățile câmpului de înălțimi la rezoluții diferite se întâlnesc cu mici trepte.
- **Culoarea de hartă a unui model Battlefield 6 este aleasă, nu citită.** Un bloc de shader numește fiecare textură pe care o eșantionează, fără să spună care este culoarea; alegerea se face după nume (vezi [Frostbite](reader-frostbite.md#textures-and-materials)) și poate alege o foaie de ornamente sau de detaliu pentru o suprafață. Foile de decalcomanii (`t_de_...`) cedează în fața hărții proprii a suprafeței; decalcomania unui semn desenată ca panoul lui arăta scutul rotit cu un sfert. Câmpurile de distanță, paletele și măștile de canal nu sunt niciodată luate. Clădirile de fundal sunt desenate în culorile paletei lor; hărțile gri iau nuanța materialului printr-o regulă a exportului, pentru că numele parametrilor sunt hash-uite, iar un material care vopsește o hartă gri printr-o mască cu mai multe nuanțe primește una dintre ele.
- **Găurile din terenul Battlefield 6 nu sunt tăiate.** Unde solul practicabil al unui nivel trece sub câmpul de înălțimi, jocul trebuie să fi tăiat terenul, iar exportul nu o face. Excluse ca locuri ale găurilor: măștile de strat ale terenului (niciuna nu este concentrată acolo), raster-ul lui de noduri 67 x 67, o valoare rezervată a înălțimii (nicio pagină de înălțime nu conține 0 sau 65.535), steagurile nodurilor (toate la fel), și mesh-urile sau activele care taie solul: ce este plasat sub sol acolo sunt mesh-uri de stâncă și de faleză, iar niciun activ al nivelului nu este numit pentru găuri, tuneluri sau peșteri. Două arbori raster sunt decodați pe lungimi, dar nu sunt plasați, și sunt ceea ce rămâne (vezi [Frostbite](reader-frostbite.md#terrain-layers)).
- **O variație a unui obiect Battlefield 6 ajunge la o secțiune prin gemenii săi.** Variația unei copii plasate alege blocurile de shader ale secțiunilor sale după cheie; unde un mesh nu are un bloc pentru o variație, este luată varianta secțiunii altui mesh cu un bloc implicit identic (vezi [Frostbite](reader-frostbite.md#textures-and-materials)). Aceasta este regula exportului; o secțiune fără geamăn care variază își păstrează aspectul implicit.
- **Materialele stratificate Battlefield 6 sunt desenate ca baza lor plus o foaie.** Un panou de perete cu litere este desenat ca tencuiala lui, cu foaia de litere peste ea; celelalte straturi ale materialului (murdăria de suprapunere prin masca ei, hărțile de detaliu și de mușchi) nu sunt amestecate.
- **Plasa de navigare este a AI-ului, nu a jucătorilor.** Acoperă ce poate ajunge un soldat pe jos: solul, podelele și scările, și unele acoperișuri, dar nu fiecare loc înalt. Legăturile dintre suprafețe (sărituri, scări, escaladări) sunt lăsate afară.
- **Un nivel Battlefield 6 include stratul fiecărui mod de joc.** Obiectele pe care le plasează doar un mod se pot suprapune cu ale altuia. `--skip` lasă straturile afară după nume.
- **`courses` este doar pentru Forza** și doar preia dosarele din bibliotecă numite `... (course_...)`.
- **Cadrul turului BeamNG este presupus** a fi cadrul vizualizatorului `(x, z, -y)` pe care îl scrie înregistratorul 3DHeat. Tururile de la un alt înregistrator, în cadrul brut al BeamNG, nu ar fi plasate.
- **`list` și `extract` iau arhivele, nu fiecare format.** Deschid un `.pak`, un `.utoc` IoStore, un `.vpk`, un `.minizip` și un zip. Un container Unity se citește cu `meshes`, un nivel Frostbite cu `level`, iar un `.cdae` sau un `.ter` este un fișier, nu o arhivă (`identify` îl numește). Un `.minizip` fără `ChunkContentsMiniZip<n>.txt` lângă el se listează după numărul intrării.
- **Modelele plasate în BeamNG folosesc texturile repetate ca culori medii**, pentru că eșantionatorul `.glb` le fixează la margini, iar vizualizatorul împachetează texturile într-un atlas.
- **În practică, doar Windows.** Căile Steam sub `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames`, și un `*_win64.dll` pentru Oodle. Alte platforme nu au fost testate.

## Neverificat {#unverified}

- Versiuni mai vechi de Python (instrumentul a fost rulat cu 3.13).
- Assetto Corsa Rally cu un tur înregistrat în joc. A fost testat doar cu tururi sintetice, în cadre aleatorii.
- Vizualizatoare glTF în afara vizualizatorului 3DHeat.
- Dacă fiecare cadru de joc este stângaci sau drept. Exportul păstrează cadrul de telemetrie al fiecărui joc, deci tururile și circuitele se aliniază oricum.
- Sensul lui z = 0 al `WaterBlock` ca suprafață (BeamNG).
- Plasarea Frostbite pe jocuri altele decât Battlefield 6, și pe Battlefield 6 după o actualizare care schimbă structura membrului de grup. Cititorul nu găsește atunci grupuri și o spune.
- Dacă un export Battlefield 6 se aliniază cu pozițiile raportate de joc. Coordonatele sunt ale jocului, ca la celelalte jocuri, dar nicio înregistrare nu a fost încă suprapusă peste una.
