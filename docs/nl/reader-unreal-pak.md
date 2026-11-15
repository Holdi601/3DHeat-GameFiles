---
title: Unreal `.pak`
nav_order: 1
lang: "nl"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Toont en pakt uit** Unreal 4.22-5.x `.pak`-archieven: versies 8, 9, 10, 11 en 12, Zlib-, Gzip- en Oodle-compressie, en versleutelde archieven wanneer je de AES-sleutel meegeeft. Het interpreteert niet wat het uitpakt (`.uasset`, `.umap`).

Bron: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Commando's: `identify`, `list`, `extract` (zie [Commando's](commands.md)).

## Indeling {#layout}

De footer staat aan het eind van het bestand en wordt gevonden door de laatste 1.024 bytes te doorzoeken naar de magic `0x5A6F12E1`. De volgorde van de velden doet ertoe:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

De versleutelingsvlag staat **vóór** de magic. Neem je hem van ná de magic, dan land je op de "Z" van "Zlib". Dan meldt elk archief zichzelf als versleuteld, en verliest elke methodenaam zijn eerste letter ("lib", "odle"), een stille en plausibele fout. De versie is de laagste byte, omdat "frozen index"-builds een hoge bit zetten.

De index bevat het mountpunt, de path-hashindex, de volledige mapindex, en een blok met **gecodeerde items**: een bitgepakte vorm waarin een vlaggenwoord zegt welke getallen 32-bit zijn, de compressiemethode (6 bits), of het item versleuteld is, het aantal blokken (16 bits) en de blokgrootte in eenheden van 2.048 (6 bits). De alles-enen blokgrootte is een escape: de echte grootte volgt als een u32 **vóór** de offset. In een groot archief leverde het lezen ervan na de groottes een verschuiving van 7% van de items met vier bytes op, en kregen ze offsets in de exabytes.

Het volledige record van elk item wordt herhaald vlak vóór de payload, dus de payload begint na `8+8+8+20+4+1+4` bytes, plus `4 + 16 x blokken` wanneer gecomprimeerd. Versleutelde blokken worden opgevuld tot 16 bytes.

## Wat het leest en wat het weigert {#what-it-reads-and-what-it-refuses}

| Geval | Resultaat |
|---|---|
| versies 8-12 | gelezen |
| elke andere versie | `pak version N; this reader handles 8-12` (oudere versies slaan een platte lijst van records op, en er was geen bestand om het mee te testen) |
| geen footer-magic | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index buiten het bestand | geweigerd: de footer parseerde niet zoals opgegeven |
| alleen path-hashindex | geweigerd: bestandsnamen zijn bij het bouwen weggehasht en kunnen niet worden hersteld |
| items in de overloopslijst van de index (mapoffset -1) | overgeslagen, niet nagemaakt |
| versleutelde index, geen sleutel | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." Op de opdrachtregel één regel en exitcode 1 |
| versleuteld item, geen sleutel | `EncryptedPak` bij het lezen |
| methoden Zlib, Gzip, Oodle | gedecomprimeerd (Oodle heeft een bibliotheek nodig, zie [Oodle](reader-oodle.md)) |
| elke andere methode | `compression method '...' is not supported` |

## Sleutels {#keys}

`--key` bij `list` en `extract` neemt een AES-256-sleutel die je al hebt, als 64 hexadecimale cijfers, met of zonder `0x`. Al het andere wordt geweigerd voordat het archief wordt geopend, met exitcode 2. Ontsleuteling is AES-256-ECB via het pakket `cryptography`. Er is geen codepad dat een sleutel verkrijgt: geen meegeleverde sleutels, geen zoektocht in programma's, geen geheugenlezen. Zie [Regels en licenties](rules-and-licences.md).

## Gecontroleerd {#verified}

Tegen meegeleverde archieven van meer dan één spel, matchte elk item, inclusief een zeer groot archief, met de SHA-1 die Unreal schrijft vóór elke payload. Die hash dekt de bytes zoals ze zijn opgeslagen, dus een match betekent dat de decodering van de index, de payloadoffset en elke grens van een gecomprimeerd blok klopte. De tests op geïnstalleerde spellen (`test_pak.py`) herhalen dit op maximaal vier niet-versleutelde pakken onder `steamapps\common\*\...\Content\Paks`. Ze controleren dat de offset van elk item binnen het bestand ligt, en dat de SHA-1 klopt voor een willekeurige steekproef van 150 items per archief.
