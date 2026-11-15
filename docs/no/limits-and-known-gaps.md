---
title: Begrensninger og kjente mangler
nav_order: 10
lang: "no"
source: limits-and-known-gaps.md
source_hash: "02df0dd20fc9"
nav_exclude: true
search_exclude: true
---
# Begrensninger og kjente mangler {#limits-and-known-gaps}

Det verktøyet ikke gjør, det det bare gjør delvis, og der oppførselen er ujevn.
De fleste mangler er bevisste avvisninger. Å dekode uten en fil å sjekke mot gir
resultater som ser riktige ut, men ikke er det.

## Spill {#games}

| Spill | Baneeksport | Hvorfor ikke, eller hvor langt |
|---|---|---|
| Forza Horizon | ja | bakkefarge er en tolkning (se under) |
| BeamNG.drive | ja | ingen bakkedekke, gjentatte modelltekstur flatet ut |
| Assetto Corsa Rally | ja | modeller med flat farge; ennå ikke kjørt på en runde tatt opp i spillet |
| Assetto Corsa EVO | **nei** | alt innhold ligger i én pakke forhårdet med en nøkkel, og verktøyet henter ingen nøkler |
| Battlefield 6 (nivåeksport, `level`) | ja, et helt nivå | terreng, gruppert og enkeltplasserte modeller og deres fargekart, soldatenes navigasjonsnett, utskåret vegetasjon; bakkefargen i spillområdet er grov (32 m per piksel, eller én gjennomsnittsfarge); ingen gjennomsiktighet eller normalkart; ødeleggbare modeller er merket, men tilstandene etter ødeleggelse eksporteres ikke |
| Unreal 5 World Partition-spill (karteksport, `ue-map`) | ja, et helt kart | terrenget nøyaktig; bygninger som kartets forenklede HLOD-modeller, ikke de fulldetaljerte modellene; vannmasser; ingen vegetasjon, dekaler eller bakkefarge |
| Arma Reforger (verdenseksport, `enfusion-world`) | ja, en hel verden | terreng i sine egne farger og havet; bygninger, rekvisitter og steiner som sine modellers bokser, ikke deres trekanter; trær på forespørsel (`--trees`), som bokser; ingen innsjøer, elver eller underentiteter |
| iRacing | **nei** | banene leveres i et beskyttet format som ikke er et mål for filuttrekk |
| alt annet | **nei** | det finnes ingen banelesing; rekonstruer fra spilling med 3DHeat GameCapture, eller analyser rundene i visningens fane for løpsanalyse uten bane |

## Motorer og formater {#engines-and-formats}

| Format | Ikke implementert |
|---|---|
| Unreal `.pak` | versjoner før 8; indekser med bare stihash (navn kan ikke gjenopprettes); oppføringer i indeksens overløpsliste (hoppes over); dekoding av `.uasset`/`.umap`-innhold fra en pak |
| Unreal IoStore | krypterte beholdere (avvises, ingen nøkkelvalg); liste over en beholder uten katalogindeks (den nevner ingen filer); versjonerte pakker; modeller som bare finnes som Nanite, og ikke-innebygde modeller; skjelettmodeller; egenskaper for klasser uten skjema; egenskaper for instanserte komponenter (oppsettet endret i spillets bygg); spline-modeller og dekalkomponenter |
| Unity | formater før 22 (Unity 2019 og eldre); filer med innebygde typetrær; komprimerte modeller; alle klasser unntatt `Mesh`, så ingen transformasjoner, materialer eller scener; `meshes` på en pakke; `list`/`extract` (bruk `meshes`) |
| Frostbite | XOR-forhårdede tabeller; terrengets lagsgraf (maskene er lest i omtrent en tredjedel av nivåene som ble sjekket); objektblåkopier annet enn modeller (spillogikk, effekter, lyder); modelnivåer lagret innebygd; normal- og andre kart, alfa annet enn utskjæringer; hull i terrenget; typebiblioteket (kryptert i den første filsystemet, ikke berørt); en kommando for å liste eller pakke ut enkeltressurser |
| Source 2 | kompilerte ressurser (`.vmdl_c`, `.vtex_c`); CS2-navigasjonsnettet (versjon 36) |
| ForzaTech | posisjonsformater annet enn fire skalerte shorts; indeksformater annet enn u16; teksturkoder annet enn 0, 9, 13; terrengets shaders materiallag; tangenter |
| BeamNG | skinnede modeller og dekalmodeller; animasjon; prosedyremessig bakkedekke; scenerier rundt kanten av verden |
| Unreal-terreng og World Partition-kart | terreng der høydekartene ligger i de innbakte cellene; redigeringslag og hull; Nanite-terrengmodeller; fulldetaljerte modeller plassert i cellene; vegetasjon; terrengmaterialer |
| Enfusion | modelltrekanter (`.xob`-geometri er komprimert i et oppsett som ikke leses); `.edds` med pre-DX10-topptekster; verdier av nestede objekter i verdensfiler (hoppes over, telles); underentiteter; genererte innsjøer og elver; `list`/`extract` på en `.pak` |

## Oppførsel verdt å kjenne til {#behaviour-worth-knowing}

- **Forza-bakkefargen er ikke spillets.** Det innbakte teksturbildet tegnes fra
  flisekartene som sier *hvor* asfalt, kort gress, røft underlag og skog er. Det
  bruker faste farger og skygging, fordi terrengshaderens egne materiallag ikke
  dekodes.
- **`--no-textures` fjerner også Forzas kantsone.** Deling av asfalt og kantsone
  bruker asfaltmasken som følger med de innbakte kartene. Uten teksturer forblir
  veistripene hele som vei.
- **Et budsjett du gir, kan bare overskrides av kantstein.** Kantstein (og
  BeamNGs modeller av kjøreflaten) forenkles eller utelates aldri, i noe spill, så et
  `--detail-budget` som er mindre enn de koster, overskrides av dem alene; alt annet
  utelates først. Se [Detaljnivåer og budsjettet](detail-budget.md).
- **Alternativer som ikke gjelder, ignoreres stille**: `--season` for BeamNG og
  AC Rally, `--track` for BeamNG og AC Rally, `--level`/`--install` for Forza.
- **Et Battlefield 6-nivås bakkefarge er grov bort fra dets dekaler.** Høydefeltet
  farges fra terrengbakgrunnens fargekart, 32 m per piksel på det største mipnivået
  nivået leverer - eller, der intet bakgrunnskart dekker, i midtfargen til terrengets
  overflatematerialer; `--ground-texture` multipliserer det med terrengets colormap
  (på 0,5 m per piksel der nivået har en) og baker veiene, plattformene, rullebanelinjene,
  dekkspor og merkinger over det, i sitt materiales malingsfarge der en er satt og en
  nøytral der ikke; veienes variasjonsmasker utelates. Spillet blander sine
  overflatelag i en shadergraf som ikke leses; eksporten legger lagenes farger etter
  maskene og høydefeltets helning, etter en regel av sin egen, og et nivå der
  maskesidene ikke passer sammen, får én farge. Hvert lag er fargekartets
  gjennomsnitt, ikke teksturen. Se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#terrain-layers). Biter av
  høydefeltet i ulik oppløsning møtes med små trinn.
- **Et Battlefield 6-fargekart velges, leses ikke.** En shaderblokk nevner hver
  tekstur den sampler uten å si hvilken som er fargen; valget gjøres etter navn (se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#textures-and-materials)),
  og kan velge et trim- eller detaljark for en overflate. Dekalark (`t_de_...`)
  taper mot overflatens egne kart; en skilts dekal tegnet som sitt panel viste sitt
  skjold vridd en kvart omdreining. Avstandsfelt, paletter og kanalmasker tas aldri.
  Bakgrunnsbygninger tegnes i sin palettes farger; grå kart tar materialets tone etter
  en regel eksporten selv har, siden parameternavnene er hashet, og et materiale som
  maler et grått kart gjennom en maske med flere toner, får én av dem.
- **Battlefield 6-terrenghull blir ikke kuttet.** Der nivåets begehbare bakke går
  under høydefeltet, må spillet ha kuttet terrenget, og eksporten gjør det ikke. Utelukket
  som stedet for hullene: terrengets lagmasker (ingen er konsentrert der), dets
  67 x 67 noderaster, en reservert høydeverdi (ingen høydeside holder 0 eller 65 535),
  nodenes flagg (alle like), og modeller eller ressurser som kutter bakken: det som er
  plassert under bakken der, er stein- og klippemodeller, og ingen ressurs i nivået
  er navngitt for hull, tunneler eller huler. To rastertrær er run-length-dekodet, men
  ikke plassert, og er det som er igjen (se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#terrain-layers)).
- **En Battlefield 6-objektvariasjon når en seksjon gjennom sine tvillinger.** En
  plassert kopis variasjon velger sine seksjoners shaderblokker etter nøkkel; der en
  modell ikke har en blokk for en variasjon, tas varianten av en annen modells seksjon
  med en identisk standardblokk (se
  [Frostbite](https://holdi601.github.io/3DHeat-Ext-Battlefield/reader-frostbite.html#textures-and-materials)).
  Det er eksportørens regel; en seksjon uten tvilling som varierer, beholder sitt
  standarduttrykk.
- **Battlefield 6-lagdelte materialer tegnes som sitt grunnlag og ett ark.** En
  veggplate med skrift tegnes som sin puss med bokstavarket over; materialets andre
  lag (grime som legger seg over gjennom sin maske, og detalj- og mosskart) blandes
  ikke inn.
- **Navigasjonsnettet er AI-ens, ikke spillernes.** Det dekker det en soldat kan gå
  til: bakken, gulv og trapper, og noen tak, men ikke hvert høyt sted. Forbindelsene
  mellom flater (hopp, stiger, vaulting) er utelatt.
- **Et Battlefield 6-nivå inkluderer hvert spillmodus' lag.** Objekter som bare én
  modus plasserer, kan overlappe en annens. `--skip` utelater lag etter navn.
- **`courses` gjelder bare Forza**, og plukker bare opp bibliotekmapper med navn
  `... (course_...)`.
- **BeamNG-rundens koordinatsystem antas** å være visningens `(x, z, -y)` som
  3DHeat-opptakeren skriver. Runder fra en annen opptaker i BeamNGs rå ramme ville
  ikke bli plassert.
- **`list` og `extract` tar arkivene, ikke alle formater.** De åpner en `.pak`, en
  IoStore `.utoc`, en `.vpk`, en `.minizip` og et zip. En Unity-beholder leses med
  `meshes`, et Frostbite-nivå med `level`, og en `.cdae` eller `.ter` er en fil og ikke
  et arkiv (`identify` navngir den). En `.minizip` uten sin `ChunkContentsMiniZip<n>.txt`
  ved siden av listes etter oppføringsnummer.
- **Plasserte modeller i BeamNG bruker gjentatte teksturer som gjennomsnittsfarger**,
  fordi `.glb`-samplingen klemmer og visningen pakker teksturene i en atlas.
- **Bare Windows, i praksis.** Steam-stier under `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames`, og en `*_win64.dll` for Oodle. Andre plattformer er
  ikke testet.

## Ikke verifisert {#unverified}

- Eldre Python-versjoner (verktøyet er kjørt med 3.13).
- Assetto Corsa Rally med en runde tatt opp i spillet. Det er bare testet med
  syntetiske runder i tilfeldige rammer.
- glTF-visninger andre enn 3DHeat-visningen.
- Om hvert spills ramme er venstre- eller høyrehåndet. Eksporten beholder hvert spills
  telemetriramme, så runder og baner stemmer uansett.
- Betydningen av `WaterBlock`s lokale z = 0 som dens overflate (BeamNG).
- Frostbite-plassering på andre spill enn Battlefield 6, og på Battlefield 6 etter en
  oppdatering som endrer gruppemedlemmenes oppsett. Leseren finner da ingen grupper og
  sier det.
- Om en Battlefield 6-eksport stemmer med posisjoner spillet rapporterer. Koordinatene
  er spillets egne, som for de andre spillene, men ingen innspilling er ennå lagt over
  en.
