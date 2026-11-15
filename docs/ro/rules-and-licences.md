---
title: "Reguli și licențe"
nav_order: 12
lang: "ro"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Reguli și licențe {#rules-and-licences}

Trei reguli modelează întregul instrument. Sunt decizii de proiectare, nu doar declinări de responsabilitate. Textul complet: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md). Această pagină este o consemnare a ceea ce spun licențele, nu un sfat juridic.

## 1. Nicio cheie: niciuna livrată, niciuna recuperată {#no-keys-none-shipped-none-recovered}

**Instrumentul citește containere.** Analizarea unui format de arhivă este gestionare obișnuită de fișiere, iar FModel, UModel și AssetRipper au făcut-o în deschis de ani de zile. Analizarea unui container nu este în sine o ocolire.

**Linia care contează este criptarea, și este trasată în interiorul instrumentului.** Un instrument al cărui scop este să învingă un control de acces este el însuși în sfera legii anticircumvenție (DMCA §1201(a)(2) vizează tehnologiile, nu doar actele), chiar dacă nimeni nu distribuie vreun fișier extras. Deci:

- **Nicio cheie livrată.** Nu există nicio cheie în cod sau în date.
- **Nicio recuperare de chei.** Nimic nu caută o cheie într-un executabil, iar nimic nu citește memoria altui proces.
- **O cheie pe care o aveți, sau nimic.** Un `.pak` Unreal criptat se deschide doar cu `--key <hex>` (în Python, `PakArchive(path, aes_key=...)`). `pak.py` nu are nicio cale de cod care să obțină o cheie. Un container IoStore criptat este refuzat din capul locului.
- **Nici obfuscarea nu este implementată.** Tabelele Frostbite obfuscate XOR își păstrează cheia în chiar fișier, deci sunt o obfuscare, nu un control de acces. Totuși sunt detectate și refuzate, pentru că niciun fișier la îndemână nu folosește acea formă și nu ar exista cu ce să verificăm o implementare. Pachetul cu cheie al Assetto Corsa EVO este refuzat din același motiv pentru care există regula cheilor.
- **Fișierele criptate rămân închise.** Sistemul de fișiere inițial al Battlefield 6, care conține biblioteca de tipuri a jocului, este criptat și nu este citit. Exportul de nivel lucrează din fișierele care nu sunt criptate și așază cele două tipuri de care are nevoie din date.
- **Nimic nu se injectează într-un proces de joc.** Telemetria vine din fluxuri pe care jocurile le publică singure, iar captura folosește API-uri publice de înregistrare a ecranului (în celelalte instrumente 3DHeat). Injectarea într-un titlu cu anti-cheat riscă contul celui care o rulează.

Fiecare arhivă testată până acum este necriptată.

## 2. Fișierele dumneavoastră, responsabilitatea dumneavoastră {#your-own-files-your-responsibility}

Instrumentul citește fișierele jocurilor **instalate pe calculatorul dumneavoastră**. Nu descarcă niciodată conținut de joc.

Ce îi indicați rămâne responsabilitatea dumneavoastră. Jocurile au propriile termeni de licență, iar EULA-urile interzic de obicei ingineria inversă. Acestea sunt contracte executorii, iar obligația revine celui care rulează instrumentul, la orice joc. Nicio decizie de proiectare de aici nu o anulează. Cel mai clar caz legitim este un dezvoltator care citește build-ul propriului studio: o echipă diferită, un titlu, o ramură veche sau un build de la un partener.

## 3. Rezultatul nu este pentru redistribuire {#output-is-not-for-redistribution}

Ce iese este geometrie pentru **context spațial**: solul, drumul și ce stă lângă el, micșorat la un buget, ca tururile să poată fi analizate pe loc. Este cea mai mică parte din ce conține o arhivă și este totuși conținutul editorului jocului.

- Păstrați fișierele `.glb` exportate, și texturile din ele, pentru analiza dumneavoastră.
- Nu publicați, nu împărtășiți și nu vindeți circuitele, nivelurile, modelele sau texturile exportate.
- `.gitignore` din depozit ține fișierele de joc, exporturile, tururile și înregistrările afară din controlul versiunilor, după folder și după tipul fișierului (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` și altele).

## Oodle este găsit, nu inclus {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, acum Epic) este proprietar și nu are un build redistribuibil. `oo2core_*.dll` este licențiat produsului care îl livrează. Așadar `oodle.py` încarcă o bibliotecă deja existentă pe calculator, în loc să o transporte. Aceasta este aranjamentul pe care îl prevede licența și cel pe care îl folosesc FModel și UModel. Vezi [Oodle](reader-oodle.md).

## Formatele în sine {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` al Unity, `.toc` Frostbite și formatele ForzaTech nu sunt documentate. Citirea lor înseamnă inginerie inversă a unui container. Niciun cititor de aici nu derivă din codul-sursă al altui proiect. Pentru Frostbite, descrierile publice ale versiunilor mai vechi (uneltele de modding Frosty, o notă de format din Need for Speed Heat, o prezentare GDC) au furnizat nume de câmpuri și o hartă a ce să căutăm. Nu s-a luat niciun cod; fiecare decalaj a fost măsurat pe fișiere (vezi [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Nivelurile extrase sunt pentru utilizarea dumneavoastră. Instrumentul le scrie pe discul dumneavoastră și nicăieri altundeva; nu le publicați.
- BeamNG își publică layout-ul `.cdae`, iar cititorul îl urmează.
- Valve documentează VPK.
- Datele de proprietăți compilate ale Unreal 5 au nevoie de lista de proprietăți a fiecărei clase. Listele din `unversioned.py` sunt **doar nume și tipuri**, fapte despre format, de felul celor pe care le conține un fișier de maparea interoperabilității. Au fost derivate din anteturile Unreal Engine pe care Epic le pune la dispoziția oricui are un cont legat și au fost verificate față de datele livrate. Nu este inclus și nu este necesar niciun cod-sursă al motorului.

## Licența acestui instrument {#this-tools-licence}

Tot ce a fost scris pentru acest depozit este sub **licența MIT** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): folosiți-l, schimbați-l, distribuiți-l, comercial sau nu.

Pachetele terțe, toate permisive, așa că exportorul nu are vreo restricție proprie:

| Pachet | Licență | Folosit pentru |
|---|---|---|
| numpy | BSD-3-Clause | decodarea mesh-urilor |
| cryptography | Apache-2.0 / BSD-3-Clause | doar pentru arhivele pentru care aveți o cheie |
| lz4 | BSD-3-Clause | arhivele Forza, unele pachete Unity, blocuri LZ4 IoStore |
| Pillow | MIT-CMU (HPND) | texturi comprimate pe blocuri, ieșire JPEG |
| msgpack | Apache-2.0 | `.cdae` BeamNG |
| zstandard | BSD-3-Clause | puținele `.cdae` comprimate cu zstd, blocurile zstd Frostbite |
| pytest | MIT | doar pentru dezvoltare |

Licențele au fost citite din metadatele pachetelor în septembrie 2026. Acolo unde termenii unei componente s-au schimbat după aceea, sursa este cea care contează.
