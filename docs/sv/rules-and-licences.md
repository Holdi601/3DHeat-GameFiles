---
title: Regler och licenser
nav_order: 12
lang: "sv"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Regler och licenser {#rules-and-licences}

Tre regler styr hela verktyget. De är konstruktionsbeslut, inte bara ansvarsfriskrivningar.
Full text: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Den här sidan är en redogörelse för vad licenserna säger, inte juridisk rådgivning.

## 1. Inga nycklar: inga levereras, inga återskapas {#no-keys-none-shipped-none-recovered}

**Den läser behållare.** Att tolka ett arkivformat är vanlig filhantering, och FModel,
UModel och AssetRipper har gjort det öppet i flera år. Att tolka en behållare är i sig
ingen kringgång.

**Gränsen som spelar roll är kryptering, och den dras inne i verktyget.** Ett verktyg
vars syfte är att kringgå en åtkomstkontroll omfattas i sig av lagar mot kringgående
(DMCA §1201(a)(2) gäller tekniker, inte bara handlingar), även om ingen sprider en enda
extraherad fil. Därför:

- **Inga medlevererade nycklar.** Det finns ingen nyckel i koden eller datan.
- **Ingen nyckelåterskapning.** Ingenting söker efter en nyckel i en körbar fil, och ingenting
  läser en annan processes minne.
- **En nyckel du har, eller ingen.** Ett krypterat Unreal-`.pak` öppnas bara med
  `--key <hex>` (i Python, `PakArchive(path, aes_key=...)`). `pak.py` har ingen kodväg som
  skaffar en nyckel. En krypterad IoStore-behållare vägras helt.
- **Obfuskering är inte heller implementerad.** Frostbites XOR-maskerade tabeller har
  sin nyckel i filen själv, så de är obfuskering snarare än en åtkomstkontroll. De
  känns ändå igen och avböjs, eftersom ingen fil på hand använder den formen och det
  inte skulle finnas något att kontrollera en implementation mot. Assetto Corsa EVO:s
  nyckelpaket vägras av samma skäl som nyckelregeln.
- **Krypterade filer hålls stängda.** Battlefield 6:s initiala filsystem, som innehåller
  spelets typbibliotek, är krypterat och läses inte. Nivåexporten arbetar med de filer
  som inte är krypterade, och lägger ut de två typer den behöver från datan.
- **Inget injiceras i en spelprocess.** Telemetrin kommer från flöden som spelen publicerar
  själva, och inspelningen använder publika skärminspelnings-API:er (i de andra 3DHeat-
  verktygen). Injektion i en titel med fusksskydd riskerar kontot för den som kör den.

Varje arkiv som testats hittills har varit okrypterat.

## 2. Dina egna filer, ditt eget ansvar {#your-own-files-your-responsibility}

Verktyget läser spelfilerna **som är installerade på din dator**. Det hämtar aldrig
spelinnehåll.

Vad du pekar det mot är fortfarande ditt ansvar. Spel har egna licensvillkor, och
slutanvändarlicensavtal förbjuder ofta omvänd konstruktion. Det är bindande avtal, och
skyldigheten ligger hos den som kör verktyget, på vilket spel som helst. Ingen
konstruktionsdetalj här befriar från den. Det tydligaste legitima fallet är att en
utvecklare läser sin egen studios build: ett annat teams titel, en gammal gren, en build
från en partner.

## 3. Resultatet är inte för vidarespridning {#output-is-not-for-redistribution}

Det som kommer ut är geometri för **rumslig kontext**: marken, vägen och det som står
bredvid den, minskad till en budget, så att varv kan analyseras på plats. Det är det minst
värdefulla i ett arkiv, och det är fortfarande spelutgivarens innehåll.

- Behåll exporterade `.glb`-filer, och texturerna i dem, för din egen analys.
- Publicera, dela eller sälj inte exporterade banor, nivåer, modeller eller texturer.
- `.gitignore` i förrådet håller spelfiler, exporter, varv och inspelningar utanför
  versionshanteringen, efter mapp och filtyp (`*.glb`, `*.pak`, `*.minizip`,
  `*.utoc`, `*.png`, `*.lap.json` med flera).

## Oodle hittas, levereras inte {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nu Epic) är proprietärt och har ingen version som får spridas.
`oo2core_*.dll` är licensierad till produkten som levererar den. `oodle.py` laddar därför
ett bibliotek som redan finns på datorn i stället för att bära med ett. Det här är upplägget
licensen förutsätter, och samma som FModel och UModel använder. Se [Oodle](reader-oodle.md).

## Formaten själva {#the-formats-themselves}

- `.pak`, IoStore, Unitys `SerializedFile`, Frostbites `.toc` och ForzaTechs format är
  odokumenterade. Att läsa dem är reverse engineering av en behållare. Ingen av läsarna
  här härleds från någon annan projekts källkod. För Frostbite gav offentliga beskrivningar
  av äldre versioner (Frosty-modderingsverktygen, en formatanteckning från Need for Speed
  Heat, ett GDC-föredrag) fältnamn och en karta över vad som ska letas efter. Ingen kod
  togs; varje offset mättes på filerna (se [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Extraherade nivåer är för din egen användning. Verktyget skriver dem till din disk och
  ingenstans annars; publicera dem inte.
- BeamNG publicerar sin `.cdae`-layout, och läsaren följer den.
- Valve dokumenterar VPK.
- Unreal 5:s cachade egenskapsdata behöver varje klass egenskapslista. Listorna i
  `unversioned.py` är **bara namn och typer**, fakta om formatet, på samma sätt som en
  interoperabilitets-mappningsfil innehåller. De härleddes från Unreal Engine-headers
  som Epic gör tillgängliga för alla med ett länkat konto, och kontrollerades mot den
  levererade datan. Ingen motorkälla ingår eller krävs.

## Verktygets egen licens {#this-tools-licence}

Allt som skrivits för förrådet står under **MIT-licensen**
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)):
använd det, ändra det, distribuera det, kommersiellt eller inte.

Tredjepartspaket, alla tillåtande, så exportören bär inga egna begränsningar:

| Paket | Licens | Används till |
|---|---|---|
| numpy | BSD-3-Clause | avkodning av meshar |
| cryptography | Apache-2.0 / BSD-3-Clause | bara för arkiv du har en nyckel till |
| lz4 | BSD-3-Clause | Forza-arkiv, en del Unity-paket, IoStore LZ4-block |
| Pillow | MIT-CMU (HPND) | blockkomprimerade texturer, JPEG-utdata |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | de få zstd-komprimerade `.cdae`-filerna, Frostbites zstd-block |
| pytest | MIT | bara utveckling |

Licenserna lästes av från paketens metadata i september 2026. Där ett komponents villkor
ändrats efter det, är källan avgörande.
