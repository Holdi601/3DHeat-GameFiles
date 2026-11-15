---
title: "Pregled arhiva"
nav_order: 3
lang: "bs"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Pregled arhiva: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Igra pakuje svoje datoteke u velike kutije zvane **arhive**. Ove komande pogledaju
etiketu kutije, ispišu šta je u njoj i izvade jednu stvar.

Prije izvoza bilo čega iz nepoznate igre, pogledajte šta isporučuje.
Ova četiri glagola čitaju datoteku i kažu vam šta je i šta sadrži; ne
upisuju ništa osim jednog unosa koji tražite pomoću `extract`.

![identify, list i extract pokrenuti na malom zip-u](../assets/img/inspect-archives.svg)

*Pokretanje na sintetičkom zip-u raspoređenom kao nivo BeamNG.drive.*

## Korak po korak {#step-by-step}

1. **Pitajte šta je datoteka.** `identify` čita bajtove, a ne ekstenziju:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Imenuje format (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle ili
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ili
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), njegovu verziju, koliko unosa
   sadrži i je li šifriran.

2. **Ispišite šta je unutra.** `list` ispisuje jedan red po unosu: veličinu, kompresiju,
   putanju. Suzite ga pomoću `--filter`, ograničite pomoću `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Izvadite jedan unos.** `extract` upisuje jedan unos (u folder u kojem se nalazite,
   osim ako `--out` ne kaže drugačije), prema putanji koju je `list`
   ispisao (ili `#12`, po broju, u `.minizip` bez imena):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` ispisuje i provjerava mreže u `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Opcije {#options}

| Glagol | Opcija | Značenje |
|---|---|---|
| `identify` | `<file>` | bilo koja datoteka |
| `list` | `<archive>` | `.pak`, `.utoc` (ili `.ucas` pored njega), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | samo putanje koje sadrže TEXT |
| | `--limit N` | najviše N redova |
| | `--key HEX` | AES-256 ključ (64 heksadecimalne cifre) koji već imate; treba samo šifriranom `.pak` |
| `extract` | `<archive> <path>` | arhiva i putanja unosa onako kako je `list` ispisuje |
| | `--out FILE` | gdje ga upisati (zadano: ime datoteke unosa) |
| | `--key HEX` | kao za `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; najviše N mreža |

Alat ne isporučuje ključeve i nijedan ne otkriva: šifrirana arhiva se otvara samo s
ključem koji navedete. Datoteka koju ne može pročitati odbija se u jednom redu s izlaznim kodom 1.
Svaki glagol i izlazni kod nalazi se na stranici [Komande](commands.md); kako se svaki format
čita, opisano je u [Čitačima arhiva](archive-readers.md).
