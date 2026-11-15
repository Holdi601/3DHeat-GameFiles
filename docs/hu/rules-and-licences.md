---
title: Szabályok és licencek
nav_order: 12
lang: "hu"
source: rules-and-licences.md
source_hash: "b68f4b6e3fe0"
nav_exclude: true
search_exclude: true
---
# Szabályok és licencek {#rules-and-licences}

Három szabály alakítja az egész eszközt. Ezek tervezési döntések, nem puszta jogi felmentések. Teljes szöveg:
[`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md). Ez az oldal azt rögzíti, mit
mondanak a licencek, nem jogi tanács.

## 1. Nincs kulcs: nincs beágyazva, nincs kinyerve {#no-keys-none-shipped-none-recovered}

**Konténereket olvas.** Egy archívumformátum elemzése hétköznapi fájlkezelés, a FModel, az UModel és az AssetRipper
évek óta nyíltan csinálja. Egy konténer elemzése önmagában nem kijátszás.

**A lényeges határvonal a titkosítás, és az eszközön belül húzzuk meg.** Egy eszköz, amelynek célja egy
hozzáférés-védelem kijátszása, maga is a körülkerülés-ellenes jog hatálya alá esik (DMCA §1201(a)(2) a
technológiákat éri, nem csak a cselekményeket), még ha senki nem is terjeszt kibontott fájlt. Ezért:

- **Nincs beágyazott kulcs.** Nincs kulcs sem a kódban, sem az adatokban.
- **Nincs kulcs-kinyerés.** Semmi nem keres kulcsot végrehajtható fájlban, és semmi nem olvas más folyamat
  memóriájából.
- **Egy kulcs, amely nálad van, vagy semmi.** Egy titkosított Unreal `.pak` csak `--key <hex>`-szel nyílik meg
  (Pythonban `PakArchive(path, aes_key=...)`). A `pak.py`-ban nincs kódútvonal, amely kulcsot szerezne. Egy titkosított
  IoStore-konténer egyenesen megtagadva.
- **Az elrejtés sincs megvalósítva.** A Frostbite XOR-elrejtett tábláinak kulcsa maga a fájlban van, így inkább
  elrejtés, mint hozzáférés-védelem. Mégis felismerjük és visszautasítjuk őket, mert egyetlen fájl sem használja
  ezt a formát, és nem lenne mivel ellenőrizni egy megvalósítást. Az Assetto Corsa EVO kulcsolt csomagját ugyanazon
  okból utasítjuk el, mint a kulcsszabályt.
- **A titkosított fájlok zárva maradnak.** A Battlefield 6 kezdeti fájlrendszere, amely a játék típuskönyvtárát
  tartalmazza, titkosított, és nincs beolvasva. A pályaexport a nem titkosított fájlokból dolgozik, és a két szükséges
  típust az adatokból rakja össze.
- **Semmi nem injektál játékfolyamatba.** A telemetria a játékok által maguk közzétett adatfolyamokból jön, a rögzítés
  pedig nyilvános képernyőfelvételi API-kat használ (a többi 3DHeat-eszközben). Egy csalásvédelemmel rendelkező cím
  folyamatába injektálni kockáztatja annak a fióknak a biztonságát, aki futtatja.

Eddig tesztelt minden archívum titkosítatlan volt.

## 2. A saját fájlod, a saját felelősséged {#your-own-files-your-responsibility}

Az eszköz a **gépeden telepített** játékfájlokat olvassa. Soha nem tölt le játéktartalmat.

Az, amire rámutatsz, a te felelősséged marad. A játékoknak saját licenszfeltételeik vannak, és a végfelhasználói
licencszerződések gyakran tiltják a visszafejtést. Ezek kikényszeríthető szerződések, a kötelezettség pedig azé, aki
az eszközt futtatja, bármely játékon. Semmilyen tervezési döntés nem mentesít alól. A legegyértelműbb jogszerű eset
egy fejlesztő saját stúdiójának buildjét olvassa: egy másik csapat címét, egy régi ágat, egy partnertől kapott buildet.

## 3. A kimenet nem terjeszthető {#output-is-not-for-redistribution}

Ami kijön, a **térbeli kontextushoz** való geometria: a talaj, az út és ami mellette áll, egy költségvetésre
csökkentve, hogy a köröket a helyükön lehessen elemezni. Egy archívum legkevesebb része ez, és még mindig a
játékkiadó tartalma.

- A kiexportált `.glb` fájlokat és a bennük lévő textúrákat a saját elemzésedhez tartsd meg.
- Ne publikáld, ne oszd meg és ne add el a kiexportált pályákat, szinteket, modelleket vagy textúrákat.
- A tároló `.gitignore`-ja a játékfájlokat, exportokat, köröket és felvételeket mappa és fájltípus szerint
  a verziókezelésen kívül tartja (`*.glb`, `*.pak`, `*.minizip`, `*.utoc`, `*.png`, `*.lap.json` és más).

## Az Oodle-t megtaláljuk, nem csomagoljuk {#oodle-is-found-not-bundled}

Az Oodle (RAD Game Tools, ma Epic) zárt forrású, és nincs újraterjeszthető build. Az `oo2core_*.dll` annak a
terméknek van licencelve, amely szállítja. Az `oodle.py` ezért a gépen már meglévő könyvtárat tölt be, nem hord
magával egyet. Ez az a megoldás, amelyet a licenc szabályoz, és amelyet a FModel és az UModel is használ. Lásd:
[Oodle](reader-oodle.md).

## Maguk a formátumok {#the-formats-themselves}

- A `.pak`, az IoStore, a Unity `SerializedFile`, a Frostbite `.toc` és a ForzaTech formátumai nincsenek
  dokumentálva. Ezek olvasása konténer visszafejtése. Az itteni olvasók egyike sem más projekt forráskódjából származik.
  A Frostbite-nál a régebbi verziók nyilvános leírásai (a Frosty modding eszközei, egy Need for Speed Heat formátumjegyzet,
  egy GDC-előadás) adták a mezőneveket és azt a térképet, hogy mit keressünk. Kódot nem vettünk át; minden eltolást a
  fájlokon mértünk (lásd: [`LICENSES.md`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSES.md)).
- A kibontott pályák a te saját használatodra vannak. Az eszköz a lemezedre írja őket, máshová nem; ne publikáld őket.
- A BeamNG közzéteszi a `.cdae` elrendezését, és az olvasó ezt követi.
- A Valve dokumentálja a VPK-t.
- Az Unreal 5 cookolt tulajdonságadataihoz kell minden osztály tulajdonságlistája. Az `unversioned.py` listái
  **csak neveket és típusokat** tartalmaznak, olyan tényeket a formátumról, amilyeneket egy interoperabilitási
  leképezési fájl is tartalmaz. Az Unreal Engine fejlécei alapján készültek, amelyeket az Epic minden összekapcsolt
  fiókkal rendelkezőnek elérhetővé tesz, és a szállított adatokon ellenőrizve. Motorforrás nincs bennük, és nem is
  szükséges hozzájuk.

## Az eszköz licence {#this-tools-licence}

Mindent, amit ehhez a tárolóhoz írtak, az **MIT licenc** fed
([`LICENSE`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/LICENSE)): használhatod, megváltoztathatod,
szállíthatod, kereskedelmi célra is.

A harmadik féltől származó csomagok mind engedékenyek, így az exportőr nem hordoz saját korlátozást:

| Csomag | Licenc | Mire való |
|---|---|---|
| numpy | BSD-3-Clause | hálódekódolás |
| cryptography | Apache-2.0 / BSD-3-Clause | csak olyan archívumokhoz, amelyekhez kulcsod van |
| lz4 | BSD-3-Clause | Forza-archívumok, néhány Unity-csomag, IoStore LZ4-blokkok |
| Pillow | MIT-CMU (HPND) | blokk-tömörített textúrák, JPEG-kimenet |
| msgpack | Apache-2.0 | BeamNG `.cdae` |
| zstandard | BSD-3-Clause | a néhány zstd-tömörített `.cdae`, Frostbite zstd-blokkok |
| pytest | MIT | csak fejlesztéshez |

A licenceket a csomagmetaadatokról olvastuk le 2026 szeptemberében. Ha egy összetevő feltételei azóta változtak,
a forrás a mérvadó.
