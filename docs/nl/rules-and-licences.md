---
title: Regels en licenties
nav_order: 12
lang: "nl"
source: rules-and-licences.md
source_hash: "d99319d82d24"
nav_exclude: true
search_exclude: true
---
# Regels en licenties {#rules-and-licences}

Drie regels bepalen de hele tool. Volledige tekst: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).

## 1. Geen sleutels: er worden er geen meegeleverd, en er worden er geen gevonden {#no-keys-none-shipped-none-recovered}

**Het leest containers.** Een archiefformaat parseren is gewone bestandsverwerking, en FModel, UModel en AssetRipper doen dat al jaren in het openbaar.

**De grens die telt, is versleuteling, en die is binnen de tool getrokken.**

- **Geen meegeleverde sleutels.** Er staat geen sleutel in de code of de data.
- **Geen sleutelherstel.** Niets zoekt in een programma naar een sleutel, en niets leest het geheugen van een ander proces.
- **Een sleutel die je hebt, of niets.** Een versleuteld Unreal `.pak` opent alleen met `--key <hex>` (in Python `PakArchive(path, aes_key=...)`). `pak.py` heeft geen codepad dat een sleutel verkrijgt. Een versleutelde IoStore-container wordt helemaal geweigerd.
- **Verhulling wordt ook niet geïmplementeerd.** De XOR-verhulde tabellen van Frostbite bewaren hun sleutel in het bestand zelf, dus het is verhulling en geen toegangsbeveiliging. Ze worden toch herkend en geweigerd, omdat geen bestand ter beschikking staat dat deze vorm gebruikt, en er dus niets is om een implementatie tegen te controleren. Het met een sleutel verhulde pakket van Assetto Corsa EVO wordt om dezelfde reden geweigerd als de sleutelregel.
- **Versleutelde bestanden blijven gesloten.** Het initiële bestandssysteem van Battlefield 6, dat de typebibliotheek van het spel bevat, is versleuteld en wordt niet gelezen. De levelexport werkt met de bestanden die niet versleuteld zijn, en legt de twee typen die hij nodig heeft vast op basis van de data.
- **Niets injecteert in een spelproces.** Telemetrie komt van feeds die spellen zelf publiceren, en opname gebruikt openbare schermopname-API's (in de andere 3DHeat-tools). Injectie in een titel met anti-cheat brengt het account van wie het draait in gevaar.

Elk archief dat tot nu toe is getest, is niet versleuteld.

## 2. Je eigen bestanden {#your-own-files}

De tool leest de spelbestanden **die op jouw computer zijn geïnstalleerd**. Hij downloadt nooit spelinhoud.

Er wordt niets van een spel meegeleverd: geen spelinhoud, geen spelcode, geen DLL's. Wat het exporteert, wordt naar je eigen schijf geschreven en nergens anders heen.

3DHeat GameFiles is niet verbonden aan of goedgekeurd door een uitgever van spellen. De spellen en bijbehorende namen en merken zijn van hun eigenaars. Rechthebbenden: open een issue op [github.com/Holdi601/3DHeat-GameFiles/issues](https://github.com/Holdi601/3DHeat-GameFiles/issues) - we reageren snel en verwijderen alles op verzoek.

## 3. De uitvoer is niet voor verspreiding {#output-is-not-for-redistribution}

Wat eruit komt, is geometrie voor **ruimtelijke context**: de grond, de weg en wat ernaast staat, teruggebracht tot een budget, zodat ronden op hun plaats geanalyseerd kunnen worden. Het is het minste van wat een archief bevat, en het blijft de inhoud van de uitgever van het spel.

- Bewaar geëxporteerde `.glb`-bestanden, en de texturen erin, voor je eigen analyse.
- Publiceer, deel of verkoop geëxporteerde banen, levels, modellen of texturen niet.
- Het `.gitignore` van de repository houdt spelbestanden, exports, ronden en opnames uit de versiebeheer per map en per bestandstype (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` en meer).

## Oodle wordt gevonden, niet meegeleverd {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, nu Epic) is eigendom en heeft geen herdistribueerbare build. `oo2core_*.dll` is in licentie gegeven aan het product dat het meelevert. `oodle.py` laadt daarom een bibliotheek die al op de computer staat, in plaats van er een mee te leveren. Dit is de regeling die de licentie voorziet, en dezelfde die FModel en UModel gebruiken. Zie [Oodle](reader-oodle.md).

## De formaten zelf {#the-formats-themselves}

- `.pak`, IoStore, Unity's `SerializedFile`, Frostbite's `.toc` en de formaten van ForzaTech zijn niet gedocumenteerd. Geen van de lezers hier is afgeleid van de broncode van een ander project. Voor Frostbite leverden openbare beschrijvingen van oudere versies (de Frosty-modding-tools, een formaatnotitie van Need for Speed Heat, een GDC-praatje) veldnamen en een overzicht van wat je moet zoeken. Er is geen code overgenomen; elke offset is op de bestanden zelf gemeten (zie [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Geëxtraheerde levels zijn voor eigen gebruik. De tool schrijft ze naar je schijf en nergens anders; publiceer ze niet.
- BeamNG publiceert zijn `.cdae`-indeling, en de lezer volgt die.
- Valve documenteert VPK.
- Het cookede eigenschapsdata van Unreal 5 heeft per klasse een lijst van eigenschappen nodig. De lijsten in `unversioned.py` bevatten **alleen namen en typen**, feiten over het formaat zoals een interoperabiliteits-mappingbestand die bevat. Ze zijn afgeleid van de Unreal Engine-headers die Epic beschikbaar stelt aan iedereen met een gekoppeld account, en gecontroleerd tegen de meegeleverde data. Er is geen engine-broncode bijgevoegd of nodig.

## De licentie van deze tool {#this-tools-licence}

Alles wat voor deze repository is geschreven, valt onder de **MIT-licentie** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): gebruiken, aanpassen, meeleveren, commercieel of niet.

Pakketten van derden, allemaal permissief, dus de exporter heeft geen eigen beperking:

| Pakket | Licentie | Gebruikt voor |
|---|---|---|
| numpy | BSD-3-Clause | meshdecodering |
| cryptography | Apache-2.0 / BSD-3-Clause | alleen archieven waarvoor je een sleutel hebt |
| lz4 | BSD-3-Clause | Forza-archieven, sommige Unity-bundels, IoStore LZ4-blokken |
| Pillow | MIT-CMU (HPND) | blokgecomprimeerde texturen, JPEG-uitvoer |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | de paar zstd-gecomprimeerde `.cdae`, Frostbite zstd-blokken |
| pytest | MIT | alleen voor ontwikkeling |

De licenties zijn in september 2026 van de pakketmetadata afgelezen. Waar de voorwaarden van een onderdeel daarna zijn veranderd, telt de bron.
