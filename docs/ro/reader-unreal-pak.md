---
title: "Unreal `.pak`"
nav_order: 1
lang: "ro"
source: reader-unreal-pak.md
source_hash: "36a27e2133a0"
nav_exclude: true
search_exclude: true
---
# Unreal `.pak` {#unreal-pak}

**Listează și extrage** arhive Unreal `.pak` din Unreal 4.22-5.x: versiunile 8, 9, 10, 11 și 12, compresie Zlib, Gzip și Oodle, și arhive criptate, când furnizați cheia AES. Nu interpretează ce extrage (`.uasset`, `.umap`).

Sursa: [`pak.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/pak.py).
Comenzi: `identify`, `list`, `extract` (vezi [Comenzi](commands.md)).

## Structura {#layout}

Footer-ul se află la sfârșitul fișierului și este găsit căutând în ultimii 1.024 de octeți magicul `0x5A6F12E1`. Ordinea câmpurilor contează:

```
[encryption key GUID : 16] [encrypted index : 1]
[magic : 4] [version : 4] [index offset : 8] [index size : 8]
[index SHA-1 : 20] [compression method names : 32 bytes each, up to 5]
```

Steagul de criptare stă **înaintea** magicului. Dacă este luat de după magic, ajunge pe „Z” din „Zlib”. Atunci fiecare arhivă se raportează criptată, iar fiecare nume de metodă pierde prima literă („lib”, „odle”), o eroare discretă și plauzibilă. Versiunea este octetul mic, pentru că build-urile cu „frozen index” setează un bit înalt.

Indexul conține punctul de montare, indexul cu hash de cale, indexul complet de directoare și un bloc de **intrări codate**: o formă împachetată pe biți, în care un cuvânt de steaguri spune care numere sunt de 32 de biți, metoda de compresie (6 biți), dacă intrarea este criptată, numărul de blocuri (16 biți) și dimensiunea blocului în unități de 2.048 (6 biți). Dimensiunea blocului formată doar din unu este un escape: dimensiunea reală urmează ca un u32 **înainte** de decalaj. Într-o arhivă mare, citirea ei după dimensiuni a deplasat 7% dintre intrări cu patru octeți și le-a dat decalaje în exaocteți.

Antetul complet al fiecărei intrări se repetă chiar înainte de încărcătură, deci încărcătura începe după `8+8+8+20+4+1+4` octeți, plus `4 + 16 x blocks` când este comprimată. Blocurile criptate sunt completate până la 16 octeți.

## Ce citește și ce refuză {#what-it-reads-and-what-it-refuses}

| Caz | Rezultat |
|---|---|
| versiunile 8-12 | citit |
| orice altă versiune | `pak version N; this reader handles 8-12` (versiunile mai vechi stochează o listă plată de înregistrări, iar nu exista un fișier pe care să le testăm) |
| niciun magic de footer | `has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` |
| index în afara fișierului | refuzat: footer-ul nu s-a parsat cum pretinde |
| doar index cu hash de cale | refuzat: numele fișierelor au fost ascunse prin hash la compilare și nu pot fi recuperate |
| intrări din lista de depășire a indexului (directory offset -1) | sărite, nu falsificate |
| index criptat, fără cheie | `EncryptedPak`: "Pass the AES key (`--key`, or `aes_key=` from Python) if you hold one; this tool does not recover keys." În linia de comandă, o linie și codul de ieșire 1 |
| intrare criptată, fără cheie | `EncryptedPak` la citire |
| metodele Zlib, Gzip, Oodle | decomprimate (Oodle are nevoie de o bibliotecă, vezi [Oodle](reader-oodle.md)) |
| orice altă metodă | `compression method '...' is not supported` |

## Chei {#keys}

`--key` pentru `list` și `extract` primește o cheie AES-256 pe care o aveți deja, ca 64 de cifre hexazecimale, cu sau fără `0x`. Orice altceva este refuzat înainte ca arhiva să fie deschisă, cu codul de ieșire 2. Decriptarea este AES-256-ECB prin pachetul `cryptography`. Nu există nicio cale de cod care să obțină o cheie: nicio cheie livrată, nicio căutare în executabile, nicio citire de memorie. Vezi [Reguli și licențe](rules-and-licences.md).

## Verificat {#verified}

Pe arhive livrate din mai multe jocuri, fiecare intrare, inclusiv o arhivă foarte mare, s-a potrivit cu SHA-1 pe care îl scrie Unreal înaintea fiecărei încărcături. Acel hash acoperă octeții așa cum sunt stocați, deci o potrivire înseamnă că decodarea indexului, decalajul încărcăturii și fiecare limită de bloc comprimat au fost corecte. Testele pe jocurile instalate (`test_pak.py`) repetă asta pe până la patru pachete necriptate găsite sub `steamapps\common\*\...\Content\Paks`. Verifică faptul că decalajul fiecărei intrări este în interiorul fișierului și că SHA-1 se potrivește pentru un eșantion aleator de 150 de intrări din fiecare arhivă.
