---
title: "Oodle"
nav_order: 3
lang: "ro"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: găsit, nu livrat {#oodle-found-not-bundled}

Majoritatea conținutului Unreal livrat, și unele încărcături Frostbite, sunt comprimate cu **Oodle** (RAD Game Tools, acum Epic). Oodle este proprietar. Nu există o versiune redistribuibilă și nicio implementare în Python, iar `oo2core_*.dll` este licențiat produsului care îl livrează. Așadar acest instrument **găsește o copie deja aflată pe calculatorul tău și o încarcă**. Nu o transportă niciodată. FModel și UModel funcționează în același mod.

Sursa: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Unde caută {#where-it-looks}

Primul fișier care există câștigă, în această ordine:

1. O cale explicită transmisă de apelant (API Python).
2. `HEAT3D_OODLE`: o cale către DLL, sau un folder care conține unul.
3. O căutare superficială, pe un singur nivel, în
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - `steamapps\common` din fiecare bibliotecă Steam

   Pentru fiecare folder copil `<game>`, verifică `<game>`, `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` și `<game>\Engine\Binaries\Win64`.

Nume de fișiere încercate, cele mai noi primele: de la `oo2core_9_win64.dll` până la `oo2core_3_win64.dll`. Formatul este compatibil cu versiunile anterioare, deci o bibliotecă mai veche de obicei tot funcționează.

Căutarea nu este, intenționat, o scanare recursivă a fiecărui disc, care ar dura minute. Dacă nu găsește nimic, setează `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Un folder funcționează la fel de bine ca fișierul în sine: numele de DLL de mai sus sunt încercate în interiorul lui.

O instalare Unreal Engine conține una sub `Engine\Binaries\ThirdParty\Oodle`, ceea ce este cea mai curată sursă pentru un dezvoltator. Multe jocuri livrează una lângă executabilul lor. Jocurile Unreal 5 leagă adesea Oodle static și nu livrează niciun DLL, așa că, copia găsită poate aparține unui alt joc decât arhiva citită. Formatul este același în ambele cazuri.

## Cum este apelat {#how-it-is-called}

`OodleLZ_Decompress` este apelat prin `ctypes` cu lungimea de ieșire așteptată (indexul arhivei o știe mereu, iar Oodle nu o poate deduce), cu decodare sigură la fuzz pornită (intrarea nu este de încredere), fără verificare CRC (SHA-1 al pak-ului acoperă deja octeții) și neîmpărțit pe fire. Un rezultat de lungime greșită este o eroare. Biblioteca este încărcată o dată per rulare.

## Când nu există niciuna {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

O intrare care nu poate fi decomprimată este o eroare, niciodată gunoi plauzibil.

Loader-ul funcționează doar pe Windows (caută `*_win64.dll`). Bibliotecile pentru Linux și macOS nu sunt căutate.
