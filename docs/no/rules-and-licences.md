---
title: Regler og lisenser
nav_order: 12
lang: "no"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Regler og lisenser {#rules-and-licences}

Tre regler former hele verktøyet. De er designbeslutninger, ikke bare ansvarsfraskrivelser. Fullstendig tekst:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Denne siden er en oversikt over hva lisensene sier, ikke juridisk rådgivning.

## 1. Ingen nøkler: ingen medfølger, ingen hentes ut {#no-keys-none-shipped-none-recovered}

**Det leser beholdere.** Å parse et arkivformat er vanlig filhåndtering, og FModel, UModel og AssetRipper har gjort det åpent i
flere år. Å parse en beholder er i seg selv ingen omgåelse.

**Skillelinjen som betyr noe, er kryptering, og den trekkes inne i verktøyet.** Et verktøy hvis formål er å slå en tilgangskontroll,
er selv innenfor rekkevidden av lovgivning mot omgåelse (DMCA §1201(a)(2) rammer teknologier, ikke bare handlinger), selv om ingen
distribuerer én eneste utpakket fil. Derfor:

- **Ingen medfølgende nøkler.** Det finnes ingen nøkkel i koden eller dataene.
- **Ingen nøkkelutvinning.** Ingenting leter etter nøkler i en kjørbar fil, og ingenting leser en annen prosess sitt minne.
- **En nøkkel du har, eller ingenting.** En kryptert Unreal `.pak` åpnes bare med `--key <hex>` (i Python, `PakArchive(path, aes_key=...)`).
  `pak.py` har ingen kodevei som skaffer en nøkkel. En kryptert IoStore-beholder avvises rett ut.
- **Forvrengning er heller ikke implementert.** Frostbites XOR-forvrengede tabeller har nøkkelen sin i selve filen, så det er forvrengning
  snarere enn en tilgangskontroll. De oppdages likevel og avvises, fordi ingen fil ved hånden bruker den formen, og det ville ikke vært noe å
  sjekke en implementasjon mot. Assetto Corsa EVOs nøkkelpakke avvises av samme grunn som nøkkelregelen finnes.
- **Krypterte filer holdes lukket.** Battlefield 6s innledende filsystem, som holder spillets typebibliotek, er kryptert og leses ikke.
  Nivåeksporten jobber fra filene som ikke er kryptert, og legger ut de to typene den trenger fra dataene.
- **Ingenting injiseres i en spillprosess.** Telemetri kommer fra datastrømmer spillene publiserer selv, og opptak bruker offentlige
  skjermopptaks-API-er (i de andre 3DHeat-verktøyene). Injeksjon i en tittel med juksebeskyttelse setter kontoen til den som kjører den i fare.

Hvert arkiv som er testet så langt, er ukryptert.

## 2. Dine egne filer, ditt eget ansvar {#your-own-files-your-responsibility}

Verktøyet leser spillfilene **installert på maskinen din**. Det laster aldri ned spillinnhold.

Det du peker det på, er fortsatt ditt ansvar. Spill har sine egne lisensvilkår, og sluttbrukeravtaler forbyr ofte revers utvikling.
Disse er håndhevbare kontrakter, og plikten ligger hos den som kjører verktøyet, uansett spill. Ingen designvalg her fritar for den.
Det klareste legitime tilfellet er en utvikler som leser sitt eget studios bygg: en annen teams tittel, en gammel gren, et bygg fra en partner.

## 3. Resultatet er ikke til videredistribusjon {#output-is-not-for-redistribution}

Det som kommer ut, er geometri for **romlig kontekst**: bakken, veien og det som står ved siden av den, redusert til et budsjett, slik at
runder kan analyseres på stedet. Det er det minste av det et arkiv inneholder, og det er fortsatt utgiverens innhold.

- Behold eksporterte `.glb`-filer, og teksturene i dem, til din egen analyse.
- Ikke publiser, del eller selg eksporterte løyper, nivåer, modeller eller teksturer.
- `.gitignore` i depotet holder spillfiler, eksporter, runder og opptak ute av versjonskontroll, etter mappe og filtype (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` med flere).

## Oodle blir funnet, ikke medfulgt {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nå Epic) er proprietær og finnes ikke i en videredistribuerbar utgave. `oo2core_*.dll` er lisensiert til produktet som leveres
med den. `oodle.py` laster derfor et bibliotek som allerede finnes på maskinen, i stedet for å bære med seg et. Dette er ordningen lisensen forutsetter,
og den samme FModel og UModel bruker. Se [Oodle](reader-oodle.md).

## Formatene selv {#the-formats-themselves}

- `.pak`, IoStore, Unitys `SerializedFile`, Frostbites `.toc` og ForzaTechs formater er udokumenterte. Å lese dem er reverse engineering av en beholder.
  Ingen av leserne her er avledet fra et annet prosjekts kildekode. For Frostbite leverte offentlige beskrivelser av eldre versjoner (Frosty-modding-verktøyene,
  et formatnotat for Need for Speed Heat, et GDC-foredrag) feltnavn og et kart over hva som skal ses etter. Ingen kode ble tatt; hver forskyvning ble målt på
  filene (se [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Utpakkede nivåer er til din egen bruk. Verktøyet skriver dem til din disk og ingen andre steder; ikke publiser dem.
- BeamNG publiserer oppsettet for sin `.cdae`, og leseren følger det.
- Valve dokumenterer VPK.
- Unreal 5s innbakte egenskapsdata trenger hver klasses egenskapsliste. Listene i `unversioned.py` er **bare navn og typer**, fakta om formatet slik en
  interoperabilitetsoversikt inneholder dem. De ble avledet fra Unreal Engine-headerne som Epic gjør tilgjengelige for alle med en koblet konto, og kontrollert
  mot de utgitte dataene. Ingen motorkilde er med, og ingen trengs.

## Dette verktøyets lisens {#this-tools-licence}

Alt som er skrevet for dette depotet, er under **MIT-lisensen** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
bruk det, endre det, send det, kommersielt eller ikke.

Tredjepartspakker, alle tillatende, så eksporten har ingen egen begrensning:

| Pakke | Lisens | Brukes til |
|---|---|---|
| numpy | BSD-3-Clause | dekoding av meshes |
| cryptography | Apache-2.0 / BSD-3-Clause | bare arkiver du har en nøkkel til |
| lz4 | BSD-3-Clause | Forza-arkiver, noen Unity-pakker, IoStore LZ4-blokker |
| Pillow | MIT-CMU (HPND) | blokkomprimerte teksturer, JPEG-utdata |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | de få zstd-komprimerte `.cdae`, Frostbite zstd-blokker |
| pytest | MIT | bare utvikling |

Lisensene ble lest av pakkemetadataene i september 2026. Der en komponents vilkår endret seg etter det, er kilden det som gjelder.
