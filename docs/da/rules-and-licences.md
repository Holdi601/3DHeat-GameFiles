---
title: Regler og licenser
nav_order: 12
lang: "da"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Regler og licenser {#rules-and-licences}

Tre regler former hele værktøjet. De er designbeslutninger, ikke blot ansvarsfraskrivelser. Fuld tekst: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md). Denne side er en optegnelse af, hvad licenserne siger, ikke juridisk rådgivning.

## 1. Ingen nøgler: ingen leveret, ingen fundet {#no-keys-none-shipped-none-recovered}

**Det læser containere.** At parse et arkivformat er almindelig filhåndtering, og FModel, UModel og AssetRipper har gjort det åbent i årevis. Intet ved at parse en container er i sig selv en omgåelse.

**Grænsen, der betyder noget, er kryptering, og den trækkes inde i værktøjet.** Et værktøj, hvis formål er at slå en adgangskontrol, er selv omfattet af lovgivning mod omgåelse (DMCA §1201(a)(2) rammer teknologier, ikke kun handlinger), selv om ingen distribuerer en eneste udtrukket fil. Derfor:

- **Ingen medleverede nøgler.** Der er ingen nøgle i koden eller dataene.
- **Ingen nøglegenfindelse.** Intet søger i en eksekverbar fil efter en nøgle, og intet læser en anden proces' hukommelse.
- **En nøgle du har, eller intet.** En krypteret Unreal `.pak` åbnes kun med `--key <hex>` (i Python, `PakArchive(path, aes_key=...)`). `pak.py` har ingen kodesti, der henter en nøgle. En krypteret IoStore-container afvises fuldstændigt.
- **Sløring er heller ikke implementeret.** Frostbites XOR-slørede tabeller har deres nøgle i selve filen, så de er sløring snarere end en adgangskontrol. De genkendes stadig og afvises, fordi ingen fil ved hånden bruger den form, og der ville ikke være noget at tjekke en implementering mod. Assetto Corsa EVO's nøglede pakke afvises af samme grund, som nøgleregelen findes.
- **Krypterede filer forbliver lukkede.** Battlefield 6's oprindelige filsystem, som indeholder spillets typebibliotek, er krypteret og læses ikke. Niveau-eksporten arbejder ud fra de filer, der ikke er krypteret, og lægger de to typer, den har brug for, ud fra dataene.
- **Intet indsprøjtes i en spilproces.** Telemetri kommer fra feeds, spil selv udgiver, og optagelse bruger offentlige skærmoptagelses-API'er (i de andre 3DHeat-værktøjer). Indsprøjtning i en titel med anti-snyd risikerer kontoen for den, der kører den.

Alle arkiver, der er testet indtil nu, er ukrypterede.

## 2. Dine egne filer, dit ansvar {#your-own-files-your-responsibility}

Værktøjet læser spilfilerne, der er **installeret på din maskine**. Det downloader aldrig spilindhold.

Det, du peger det på, er fortsat dit ansvar. Spil har deres egne licensvilkår, og slutbrugeraftaler (EULA'er) forbyder typisk reverse engineering. Det er bindende kontrakter, og forpligtelsen ligger hos den, der kører værktøjet, på hvilket som helst spil. Intet designvalg her fritager for den. Det klareste legitime tilfælde er en udvikler, der læser sit eget studies build: en anden teams titel, en gammel gren, et build fra en partner.

## 3. Resultatet er ikke til videredistribution {#output-is-not-for-redistribution}

Det, der kommer ud, er geometri til **rumlig kontekst**: jorden, vejen og det, der står ved siden af, nedskaleret til et budget, så runder kan analyseres på stedet. Det er det mindste af, hvad et arkiv indeholder, og det er stadig spiludgiverens indhold.

- Behold eksporterede `.glb`-filer og teksturerne i dem til din egen analyse.
- Offentliggør, del eller sælg ikke eksporterede baner, niveauer, modeller eller teksturer.
- Repositoriets `.gitignore` holder spilfiler, eksporter, runder og optagelser ude af versionskontrol efter mappe og filtype (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` med flere).

## Oodle findes, medleveres ikke {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nu Epic) er proprietær og har ingen redistribuerbar build. `oo2core_*.dll` er licenseret til det produkt, der leverer den. `oodle.py` indlæser derfor et bibliotek, der allerede er på maskinen, i stedet for at medbringe ét. Det er den ordning, licensen forudser, og den samme, FModel og UModel bruger. Se [Oodle](reader-oodle.md).

## Selve formaterne {#the-formats-themselves}

- `.pak`, IoStore, Unitys `SerializedFile`, Frostbites `.toc` og ForzaTechs formater er udokumenterede. At læse dem er reverse engineering af en container. Ingen af læserne her er afledt af et andet projekts kildekode. For Frostbite leverede offentlige beskrivelser af ældre versioner (Frosty-modderingsværktøjerne, en formatnote til Need for Speed Heat, et GDC-foredrag) feltnavne og et kort over, hvad der skal kigges efter. Der er ikke taget nogen kode; hver offset er målt på filerne (se [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Udtrukne niveauer er til din egen brug. Værktøjet skriver dem til din disk og ingen andre steder; offentliggør dem ikke.
- BeamNG offentliggør sit `.cdae`-layout, og læseren følger det.
- Valve dokumenterer VPK.
- Unreal 5's bagte egenskabsdata kræver hver klasses egenskabsliste. Listerne i `unversioned.py` er **kun navne og typer**, fakta om formatet, sådan som en interoperabilitets-mappingfil indeholder dem. De blev udledt af Unreal Engine-headerne, som Epic gør tilgængelige for alle med en tilknyttet konto, og tjekket mod de leverede data. Ingen motorkilde er medtaget eller nødvendig.

## Dette værktøjs licens {#this-tools-licence}

Alt, der er skrevet til dette repositorie, er under **MIT-licensen** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): brug det, ændr det, lever det, kommercielt eller ikke.

Tredjepartspakker, alle tilladende, så eksporteren har ingen begrænsning af sin egen:

| Pakke | Licens | Bruges til |
|---|---|---|
| numpy | BSD-3-Clause | afkodning af meshes |
| cryptography | Apache-2.0 / BSD-3-Clause | kun arkiver, du har en nøgle til |
| lz4 | BSD-3-Clause | Forza-arkiver, nogle Unity-bundles, IoStore LZ4-blokke |
| Pillow | MIT-CMU (HPND) | blokkomprimerede teksturer, JPEG-output |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | de få zstd-komprimerede `.cdae`, Frostbite zstd-blokke |
| pytest | MIT | kun udvikling |

Licenserne blev læst af pakkernes metadata i september 2026. Hvor en komponents vilkår er ændret siden da, er kilden det, der gælder.
