---
title: Čtečky archivů
nav_order: 9
lang: "cs"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Čtečky archivů {#archive-readers}

**Kontejner** (neboli archiv) je jeden velký soubor, do kterého hra zabalí mnoho
souborů. **CRC** nebo hash je krátký otisk nějakých bajtů: pokud sedí, bajty se
načetly správně. **Ohraničující kvádr** je nejmenší kvádr kolem modelu.

Pod příkazy jsou čtečky kontejnerů, které hry dodávají. Jejich formáty nejsou
zdokumentované, kromě VPK od Valve a `.cdae` od BeamNG. Proto "podporováno" musí
znamenat **ověřeno na skutečných souborech**, ne "nespadlo to". Každá čtečka se
kontroluje sama vůči něčemu, co formát zaručuje: hashi, CRC, řetězci posunů,
které se musí uzavřít, nebo uloženým ohraničujícím kvádrem. Když kontrola selže,
čtečka skončí se zprávou a neodhaduje. Špatná síť vypadá jako správná, dokud ji
nedáte vedle trati.

| Čtečka | Modul | Čte | Nečte | Volá se z |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | verze 8-12: index, položky, bloky Zlib/Gzip/Oodle, AES s klíčem, který dodáte | verze před 8, indexy jen s hashi cest, položky přetečení, obsah assetů | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5+, ověřeno na v8), zen balíčky, neverzované vlastnosti pro několik tříd komponent, zkompilované statické sítě, textury, streamované virtuální textury | šifrované kontejnery, verzované balíčky, sítě jen pro Nanite, vlastnosti ostatních tříd | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | bloky Oodle přes knihovnu, která už je v počítači | cokoli bez takové knihovny; nikdy se nebalí | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` formát 22+ (Unity 2020 až 6000), `UnityFS` bundly, nekomprimované sítě včetně `.resS` | formáty před rokem 2020, vložené stromy typů, komprimované sítě, jakákoli třída kromě `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | stromy objektů `.toc` DbObject a binární tabulky sekcí, instalační balíčky, umístění chunků, vnořené bundly a jejich manifesty, RIFF EBX oddíly, sítě MeshSet, výškové pole terénu, textury BC1/BC3/BC7 a jejich bloky shaderů, umístění statických skupin modelů | tabulky s XOR obfuskací, barvu terénu blízko země a díry, normálové mapy, alfu jinou než výřezy | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | verze 1 a 2, rozdělené archivy, přednačtená data, kontrola CRC | zkompilované assety (`.vmdl_c`, `.vtex_c`), formát navigační sítě CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, uložené), geometrie `.modelbin`, vzorníky `.pb` (BC1, BC7, RGBA), umístění `.pgeo`, hashe textur materiálů | jiné formáty vrcholů a indexů, jiné formáty textur, vrstvy shaderu terénu | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` a `extract` (`.minizip`) |
| [Soubory BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | připojený souborový systém zip, scénové soubory JSON a TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, materiály | kožované a dekorační sítě, animované sekvence, procedurální porost | `course` (BeamNG), `identify` (zipy, `.cdae`, `.ter`), `list` a `extract` (zipy) |

## Pravidla, kterými se řídí každá čtečka {#rules-every-reader-follows}

- **Žádné klíče se nedodávají, žádné se neobnovují.** Šifrovaný archiv se otevře
  jen s klíčem, který jim předáte (Unreal `.pak`, `--key`). Šifrovaný kontejner
  IoStore se odmítne. Nic nehledá klíč v programu a nečte paměť jiného procesu.
  Viz [Pravidla a licence](rules-and-licences.md).
- **Žádný proprietární kód se nebalí.** Oodle se načítá z hry nebo enginu, který
  už je na počítači nainstalovaný.
- **Raději odmítnout než hádat.** Neznámá verze, kodek, formát vrcholů nebo
  formát textury vyvolá konkrétní chybu, například
  `texture format 42 has not been identified; refusing to guess`.
- **Jen čtení.** Žádná čtečka nezapisuje do složky hry. Exporty jdou tam, kam
  řeknete.

## Co znamená "ověřeno" {#what-verified-meant}

Čísla ověření uvedená na těchto stránkách pocházejí z dokumentačních řetězců
modulů. Byla změřena na nainstalovaných hrách během psaní každé čtečky. Syntetické
testy (viz [Vývoj](development.md)) zamykají rozložení polí. Testy na
nainstalovaných hrách opakují některé kontroly, když je hra na počítači, a jinak
se přeskočí. Čísla, která test nepokrývá, se od posledního ověření nepřepočítávala.
