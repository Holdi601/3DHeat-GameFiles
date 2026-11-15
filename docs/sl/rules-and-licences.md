---
title: "Pravila in licence"
nav_order: 12
lang: "sl"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Pravila in licence {#rules-and-licences}

Tri pravila oblikujejo celotno orodje. So odločitve pri zasnovi, ne le izjave o odgovornosti. Celotno besedilo: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md).
Ta stran je zapis, kaj licence pravijo, ne pravni nasvet.

## 1. Brez ključev: nobenega shranjenega, nobenega izluščenega {#no-keys-none-shipped-none-recovered}

**Bere kontejnerje.** Razčlenjevanje formata arhiva je običajno delo z datotekami, FModel, UModel in AssetRipper pa to odprto delajo že leta. Razčlenjevanje kontejnerja samo po sebi ni izogibanje zaščiti.

**Črta, ki šteje, je šifriranje, in je potegnjena znotraj orodja.** Orodje, katerega namen je premagati nadzor dostopa, je samo po sebi v okviru zakonov proti izogibanju (DMCA §1201(a)(2) zajema tehnologije, ne samo dejanja), tudi če nihče ne razdeli niti ene izvlečene datoteke. Zato:

- **Brez vgrajenih ključev.** Ključa ni v kodi ali podatkih.
- **Brez izluščenja ključa.** Nič ne išče ključa v izvršljivi datoteki, nič ne bere pomnilnika drugega procesa.
- **Ključ, ki ga imate, ali nič.** Šifriran Unreal `.pak` se odpre samo z `--key <hex>` (v Pythonu `PakArchive(path, aes_key=...)`). `pak.py` nima kodne poti, ki bi ključ pridobila. Šifriran kontejner IoStore je brez pogojev zavrnjen.
- **Tudi zakrivanje ni implementirano.** Tabele Frostbite, zakrite z XOR, hranijo svoj ključ v sami datoteki, zato so zakrivanje in ne nadzor dostopa. Vseeno so prepoznane in zavrnjene, ker nobena datoteka, ki jo imamo, ne uporablja te oblike, zato ni ničesar, s čimer bi preverili implementacijo. Šifrirani paket Assetto Corsa EVO je zavrnjen iz istega razloga, zaradi katerega obstaja pravilo o ključih.
- **Šifrirane datoteke ostanejo zaprte.** Začetni datotečni sistem Battlefield 6, ki hrani tip knjižnice igre, je šifriran in ni prebran. Izvoz nivoja dela iz datotek, ki niso šifrirane, in iz podatkov postavi dva tipa, ki ju potrebuje.
- **Nič se ne vbrizga v proces igre.** Telemetrija prihaja iz virov, ki jih igre same objavljajo, zajem pa uporablja javne API-je za snemanje zaslona (v drugih orodjih 3DHeat). Vbrizgavanje v naslov z zaščito proti goljufijam ogroža račun tistega, ki ga zažene.

Vsi doslej preizkušeni arhivi so nešifrirani.

## 2. Vaše datoteke, vaša odgovornost {#your-own-files-your-responsibility}

Orodje bere igrine datoteke, **nameščene na vašem računalniku**. Nikoli ne prenese vsebine igre.

Kar usmerite vanj, ostaja vaša odgovornost. Igre imajo svoje licenčne pogoje, EULA pogosto prepovedujejo povratni inženiring. To so izvršljive pogodbe, obveznost pa leži pri tistem, ki orodje zažene, pri katerikoli igri. Nobena zasnova tukaj vas te obveznosti ne odveže. Najbolj jasen zakonit primer je razvijalec, ki bere gradnjo svojega lastnega studia: drugačno ekipo naslova, staro vejo, gradnjo partnerja.

## 3. Izhod ni za deljenje {#output-is-not-for-redistribution}

Kar pride ven, je geometrija za **prostorski kontekst**: tla, cesta in to, kar stoji ob njej, poenostavljeno na proračun, da se krogi lahko analizirajo na mestu. Je najmanj od tistega, kar arhiv vsebuje, in še vedno je vsebina založnika igre.

- Hranite izvožene datoteke `.glb` in teksture v njih za lastno analizo.
- Ne objavljajte, ne delite in ne prodajajte izvoženih prog, nivojev, modelov ali tekstur.
- `.gitignore` repozitorija izključi datoteke igre, izvoze, krogi in posnetki iz nadzora različic po mapi in vrsti datoteke (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` in drugi).

## Oodle je najden, ne priložen {#oodle-is-found-not-bundled}

Oodle (RAD Game Tools, zdaj Epic) je lastniški in nima redistribucijske gradnje. `oo2core_*.dll` je licenciran izdelku, ki ga pošilja. `oodle.py` zato naloži knjižnico, ki je že na računalniku, namesto da bi jo nosil s seboj. To je ureditev, ki jo predvideva licenca, in ista, ki jo uporabljata FModel in UModel. Glejte [Oodle](reader-oodle.md).

## Sami formati {#the-formats-themselves}

- `.pak`, IoStore, `SerializedFile` Unity, `.toc` Frostbite in ForzaTech formati niso dokumentirani. Njihovo branje je povratni inženiring kontejnerja. Nobeden od tukajšnjih bralnikov ni izpeljan iz izvorne kode drugega projekta. Za Frostbite so javni opisi starejših različic (orodja za modding Frosty, zapis o formatu za Need for Speed Heat, predavanje z GDC) dali imena polj in zemljevid, kaj iskati. Nobena koda ni bila vzeta; vsak odmik je bil izmerjen na datotekah (glejte [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- Izvlečeni nivoji so za lastno uporabo. Orodje jih zapiše na vaš disk in nikamor drugam; ne objavljajte jih.
- BeamNG objavlja postavitev svojih datotek `.cdae`, bralnik pa jo sledi.
- Valve dokumentira VPK.
- Prevedeni podatki lastnosti Unreal 5 potrebujejo seznam lastnosti vsakega razreda. Seznami v `unversioned.py` so **samo imena in tipi**, dejstva o formatu, kakršna ima npr. datoteka za interoperabilnost preslikav. Izpeljani so bili iz glav Unreal Engine, ki jih Epic da na voljo vsakomur z registriranim računom, in preverjeni proti objavljenim podatkom. Nobena izvorna koda motorja ni vključena ali potrebna.

## Licenca tega orodja {#this-tools-licence}

Vse, kar je napisano za ta repozitorij, je pod **licenco MIT** ([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): uporabi, spremeni, razdeli, komercialno ali ne.

Paketi drugih avtorjev, vsi dovoljujoči, zato izvoznik sam nima nobene omejitve:

| Paket | Licenca | Za kaj |
|---|---|---|
| numpy | BSD-3-Clause | dekodiranje meshev |
| cryptography | Apache-2.0 / BSD-3-Clause | samo arhivi, za katere imate ključ |
| lz4 | BSD-3-Clause | arhivi Forze, nekateri paketi Unity, bloki LZ4 IoStore |
| Pillow | MIT-CMU (HPND) | teksture s stiskanjem blokov, izhod JPEG |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | nekateri `.cdae` s stiskanjem zstd, bloki zstd Frostbite |
| pytest | MIT | samo razvoj |

Licence so prebrane iz metapodatkov paketov septembra 2026. Kjer so se pogoji komponente pozneje spremenili, je merodajen vir.
