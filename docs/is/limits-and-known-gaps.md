---
title: "Takmarkanir og þekktar eyður"
nav_order: 10
lang: "is"
source: limits-and-known-gaps.md
source_hash: "02df0dd20fc9"
nav_exclude: true
search_exclude: true
---
# Takmarkanir og þekktar eyður {#limits-and-known-gaps}

Hvað verkfærið gerir ekki, hvað það gerir aðeins að hluta, og hvar hegðun þess er
ójöfn. Flestar eyður eru ásetningur um að neita. Afkóðun án skrár til að prófa á móti
gefur úttak sem lítur rétt út en er það ekki.

## Leikir {#games}

| Leikur | Brautarútflutningur | Hvers vegna ekki, eða hversu langt |
|---|---|---|
| Forza Horizon | já | jarðlitur er túlkun (sjá hér að neðan) |
| BeamNG.drive | já | enginn jarðargróður, endurteknar áferðir líkana fletjast út |
| Assetto Corsa Rally | já | líkön í sléttum litum; ekki enn keyrt á hring sem tekinn var upp í leiknum |
| Assetto Corsa EVO | **nei** | allt efni er í einum pakka sem er hulinn með lykli, og þetta verkfæri endurheimtir enga lykla |
| Battlefield 6 (borðsútflutningur, `level`) | já, heilt borð | land, hópuð og stök staðsett net og litakort þeirra, leiðarnet hermannanna, útklippt laufblöð; jarðlitur leiksvæðisins er grófur (32 m á dikil, eða einn meðallitur); engin gegnsæi eða normal-kort; eyðanleg net merkt, eyðilögð ástönd þeirra ekki flutt út |
| Unreal 5 World Partition leikir (kortaútflutningur, `ue-map`) | já, heilt kort | landslagið nákvæmt; byggingar sem einfölduð HLOD net kortsins, ekki líkönin með fullum smáatriðum; vatnshlot; enginn gróður, límmiðar eða jarðlitur |
| Arma Reforger (heimsútflutningur, `enfusion-world`) | já, heill heimur | land í eigin litum og sjórinn; byggingar, munir og klettar sem kassar líkana sinna, ekki þríhyrningar þeirra; tré sé þess óskað (`--trees`), sem kassar; engin vötn, ár eða undireiningar |
| iRacing | **nei** | brautir eru sendar í vernduðu sniði sem er ekki skotmark skráaútdráttar |
| allt annað | **nei** | enginn brautarlesari er til; endurbyggðu úr spilun með 3DHeat GameCapture, eða greindu hringina í Kappakstursgreiningar-flipa skoðarans án brautar |

## Vélar og snið {#engines-and-formats}

| Snið | Ekki útfært |
|---|---|
| Unreal `.pak` | útgáfur fyrir 8; vísar með aðeins slóðatætigildi (ekki hægt að endurheimta nöfn); færslur í yfirflæðislista vísisins (sleppt); afkóðun á innihaldi `.uasset`/`.umap` úr pak |
| Unreal IoStore | dulkóðuð ílát (hafnað, enginn lykilvalkostur); að listann yfir ílát án möppuvísis (það nefnir engar skrár); útgáfumerktir pakkar; net eingöngu Nanite og ekki innbyggð; net með beinagrind; eigindir flokka án skemu; eigindir íhluta með eintökum (uppröðun breyttist í útgáfu leiksins); splínunet og límmiðaíhlutir |
| Unity | snið fyrir 22 (Unity 2019 og eldra); skrár með innbyggðum gerðatrjám; þjöppuð net; allir flokkar nema `Mesh`, svo engar hnitabreytingar, efni eða senur; `meshes` á búnti; `list`/`extract` (notaðu `meshes`) |
| Frostbite | XOR-hulin töflur; lagagraf landsins (grímur lesnar í um þriðjungi borða sem voru athuguð); hlutateikningar aðrar en net (spilunarrökfræði, áhrif, hljóð); netastig geymd innbyggð; normal- og önnur kort, alfa annað en útklippur; göt í landi; gerðasafnið (dulkóðað í upphafsskráakerfinu, ekki snert); skipun til að listann eða draga út stakar eignir |
| Source 2 | þýddar eignir (`.vmdl_c`, `.vtex_c`); CS2 leiðarnetið (útgáfa 36) |
| ForzaTech | staðsetningarsnið önnur en fjórir skalaðir shorts; vísasnið önnur en u16; áferðarkóðar aðrir en 0, 9, 13; efnislög skuggara landsins; snertlar (tangents) |
| BeamNG | net með beinagrind og límmiðanet; hreyfimynd; kerfisbundinn gróður á jörðu; umhverfi við jaðar heimsins |
| Unreal landslag og World Partition kort | landslag þar sem hæðarkort búa í bökuðu reitunum; breytingalög og göt; Nanite landslagsnet; líkön með fullum smáatriðum staðsett í reitunum; gróður; landslagsefni |
| Enfusion | þríhyrningar líkana (`.xob` rúmfræði er þjöppuð í uppröðun sem er ekki lesin); `.edds` með hausa eldri en DX10; gildi hreiðraðra hluta í heimsskrám (sleppt, talið); undireiningar; búin til vötn og ár; `list`/`extract` á `.pak` |

## Hegðun sem vert er að vita {#behaviour-worth-knowing}

- **Jarðlitur Forza er ekki sá sem leikurinn hefur.** Baka áferðin er teiknuð úr
  flísakortunum sem segja *hvar* malbik, stutt gras, gróft land og skóglendi eru.
  Hún notar fasta liti og skyggingu, því eigin efnislög skuggara landsins
  eru ekki afkóðuð.
- **`--no-textures` fjarlægir líka vegöxl Forza.** Skipting malbiks/vegaxlar notar
  malbiksgrímuna sem fylgir bökuðu kortunum. Án áferða haldast vegarræmur
  heilar sem vegur.
- **Aðeins kantsteinar geta farið yfir hámark sem þú gefur.** Kantsteinar (og akstursflatalíkön
  BeamNG) eru aldrei einfaldaðir eða skildir eftir, í neinum leik, svo
  `--detail-budget` sem er minna en þeir kosta er farið yfir af þeim einum; allt annað
  er skilið eftir fyrst. Sjá [Smáatriðastig og kostnaðarhámarkið](detail-budget.md).
- **Valkostir sem eiga ekki við eru hunsaðir hljóðlega**: `--season` fyrir BeamNG og
  AC Rally, `--track` fyrir BeamNG og AC Rally, `--level`/`--install` fyrir Forza.
- **Jarðlitur Battlefield 6 borðs er grófur fjarri límmiðum þess.**
  Landhæðarsviðið er litað úr litakorti landbakgrunnsins, 32 m á dikil á
  stærsta mip sem borðið sendir með - eða, þar sem ekkert bakgrunnskort nær yfir það, í
  miðlit yfirborðsefna landsins; `--ground-texture`
  margfaldar það með litakorti landsins (0,5 m á dikil þar sem borðið
  hefur það) og bakar vegi, svuntur, flugbrautarlínur, hjólför og
  merkingar yfir það, í málningarlit efna þeirra þar sem hann er stilltur og
  hlutlausum lit þar sem ekki; afbrigðisgrímur vega eru sleppt. Leikurinn blandar yfirborðslögum sínum í
  skuggaraferli sem er ekki lesið; útflutningurinn leggur liti laganna eftir
  grímum þeirra og halla landhæðarsviðsins, eftir eigin reglu, og borð þar sem
  grímusíður passa ekki saman fær einn lit. Hvert lag er
  meðaltal litakorts síns, ekki áferð þess. Sjá
  [Frostbite](reader-frostbite.md#terrain-layers). Bútar landhæðarsviðsins
  með mismunandi upplausn mætast með litlum þrepum.
- **Litakort í Battlefield 6 er valið, ekki lesið.** Skuggablokk nefnir
  hverja áferð sem hún sýnatekur án þess að segja hver er liturinn; valið fer
  eftir nafni (sjá [Frostbite](reader-frostbite.md#textures-and-materials)) og getur
  valið skreytingar- eða smáatriðablað fyrir yfirborð. Límmiðablöð (`t_de_...`)
  tapa fyrir eigin korti yfirborðsins; límmiði skiltis teiknaður sem spjald þess sýndi skjöld þess
  snúinn um fjórðung. Fjarlægðarsvið, litaspjöld og rásagrímur eru aldrei
  tekin. Bakgrunnsbyggingar eru teiknaðar í litum litaspjalds síns; grá kort
  taka lit efnisins eftir eigin reglu útflytjandans, þar sem
  nöfn færibreytnanna eru tætt, og efni sem málar grátt kort
  í gegnum grímu með nokkrum litum fær einn þeirra.
- **Göt í landi Battlefield 6 eru ekki skorin.** Þar sem gönguhæft land borðs
  liggur undir landhæðarsviðinu hlýtur leikurinn að hafa skorið landið, og útflutningurinn gerir
  það ekki. Útilokað sem staðir gatanna: lagagrímur landsins (engin
  er þétt þar), 67 x 67 hnútaraster þess, frátekið hæðargildi (engin
  hæðarsíða geymir 0 eða 65.535), flögg hnútanna (öll eins), og net
  eða eignir sem skera landið: það sem er staðsett undir jörðinni þar
  eru klettanet, og engin eign borðsins er nefnd eftir götum,
  göngum eða hellum. Tvö rastatré eru lengdarkóðuð afkóðuð en ekki staðsett,
  og eru það sem eftir er (sjá [Frostbite](reader-frostbite.md#terrain-layers)).
- **Afbrigði hlutar í Battlefield 6 nær til kafla í gegnum tvíbura hans.**
  Afbrigði staðsetts eintaks velur skuggablokkir kafla sinna eftir lykli; þar sem
  net hefur enga blokk fyrir afbrigði er tekið afbrigði kafla annars nets
  með eins sjálfgefna blokk (sjá
  [Frostbite](reader-frostbite.md#textures-and-materials)). Það er
  regla útflytjandans; kafli án tvíbura sem breytist heldur sjálfgefnu útliti.
- **Lagskipt efni í Battlefield 6 eru teiknuð sem grunnur þeirra og eitt blað.**
  Veggspjald með letri er teiknað sem pússning þess með stafablaðinu yfir
  sér; önnur lög efnisins (yfirlagsóhreinindi í gegnum grímu sína, smáatriða-
  og mosakort) eru ekki blönduð inn.
- **Leiðarnetið er gervigreindarinnar, ekki leikmannanna.** Það nær yfir það sem
  hermaður getur gengið til: jörðina, gólf og tröppur, og
  suma þakfleti, en ekki alla háa staði. Tengingarnar milli flata (stökk, stigar, klifur) eru sleppt.
- **Battlefield 6 borð inniheldur lag hverrar leikjastillingar.** Hlutir sem aðeins
  ein stilling setur geta skarast við annarrar. `--skip` sleppir lögum eftir nafni.
- **`courses` er aðeins fyrir Forza**, og tekur aðeins upp safnmöppur sem heita
  `... (course_...)`.
- **Gert er ráð fyrir BeamNG hringásakerfinu** sem ásakerfi skoðarans `(x, z, -y)` sem
  3DHeat upptökuforritið skrifar. Hringir frá öðru upptökuforriti í hráu ásakerfi BeamNG
  yrðu ekki staðsettir.
- **`list` og `extract` taka skjalasöfn, ekki hvert snið.** Þau opna
  `.pak`, IoStore `.utoc`, `.vpk`, `.minizip` og zip. Unity ílát
  er lesið með `meshes`, Frostbite borð með `level`, og `.cdae` eða
  `.ter` er skrá frekar en skjalasafn (`identify` nefnir það). `.minizip`
  án `ChunkContentsMiniZip<n>.txt` við hliðina listast eftir færslunúmeri.
- **Staðsett líkön í BeamNG nota endurteknar áferðir sem meðallitir**, því
  `.glb` sýnatakinn klemmir og skoðarinn pakkar áferðum í atlas.
- **Aðeins Windows, í reynd.** Steam slóðir undir `C:\Program Files`,
  `%LOCALAPPDATA%`, `C:\XboxGames`, og `*_win64.dll` fyrir Oodle. Aðrir vettvangar
  eru óprófaðir.

## Óstaðfest {#unverified}

- Eldri Python útgáfur (verkfærið hefur verið keyrt með 3.13).
- Assetto Corsa Rally með hring sem tekinn var upp í leiknum. Það hefur aðeins verið prófað
  með gervihringjum í handahófskenndum ásakerfum.
- glTF skoðarar aðrir en 3DHeat skoðarinn.
- Hvort ásakerfi hvers leiks er vinstri- eða hægrihandar. Útflutningurinn heldur ásakerfi
  mælinga hvers leiks, svo hringir og brautir raðast saman hvort sem er.
- Merking staðbundins z = 0 hjá `WaterBlock` sem yfirborðs þess (BeamNG).
- Frostbite staðsetning í öðrum leikjum en Battlefield 6, og í Battlefield 6
  eftir uppfærslu sem breytir uppröðun hópmeðlims. Lesarinn finnur þá
  enga hópa og segir frá því.
- Hvort Battlefield 6 útflutningur raðast við staðsetningar sem leikurinn greinir frá. Hnitin
  eru eigin hnit leiksins, eins og í hinum leikjunum, en engin upptaka hefur
  enn verið lögð yfir einn.
