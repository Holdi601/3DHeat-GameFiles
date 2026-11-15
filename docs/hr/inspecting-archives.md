---
title: "Pregled arhiva: `identify`, `list`, `extract`, `meshes`"
nav_order: 3
lang: "hr"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Pregled arhiva: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Igra svoje datoteke pakira u velike kutije koje se zovu **arhive**. Ove naredbe pogledaju oznaku kutije, popišu što je u njoj i izvade jednu stvar.

Prije izvoza bilo čega iz nepoznate igre pogledajte što ona isporučuje. Ova četiri glagola čitaju datoteku i kažu vam što je i što sadrži. Ne zapisuju ništa, osim jednog unosa koji zatražite naredbom `extract`.

![identify, list i extract pokrenuti na maloj zip datoteci](../assets/img/inspect-archives.svg)

*Pokretanje na sintetičkoj zip datoteci posloženoj kao razina igre BeamNG.drive.*

## Korak po korak {#step-by-step}

1. **Pitajte što je datoteka.** `identify` čita bajtove, a ne ekstenziju:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Imenuje format (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity paket ili `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ili `.modelbin`, BeamNG `.cdae`/`.ter`, zip), njegovu verziju, koliko unosa sadrži i je li šifrirana.

2. **Popišite što je unutra.** `list` ispisuje jedan redak po unosu: veličina, kompresija, putanja. Suzite ispis s `--filter`, a ograničite broj redaka s `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Izvadite jedan unos.** `extract` zapisuje jedan unos (u mapu u kojoj se nalazite, osim ako `--out` ne kaže drugačije), prema putanji koju je ispisao `list` (ili `#12`, prema broju, u `.minizip` datoteci bez imena):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` popisuje i provjerava mreže u `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Opcije {#options}

| Glagol | Opcija | Značenje |
|---|---|---|
| `identify` | `<file>` | bilo koja datoteka |
| `list` | `<archive>` | `.pak`, `.utoc` (ili `.ucas` pored njega), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | samo putanje koje sadrže TEXT |
| | `--limit N` | najviše N redaka |
| | `--key HEX` | AES-256 ključ (64 heksadecimalne znamenke) koji već imate; treba ga samo šifrirana `.pak` datoteka |
| `extract` | `<archive> <path>` | arhiva i putanja unosa kako je ispisuje `list` |
| | `--out FILE` | gdje ga zapisati (zadano: ime datoteke unosa) |
| | `--key HEX` | kao za `list` |
| `meshes` | `<file>`, `--limit N` | Unity `SerializedFile`; najviše N mreža |

Alatka ne isporučuje ključeve i ne vraća ih: šifrirana arhiva otvara se samo s ključem koji predate. Datoteka koju ne može pročitati odbija se jednim retkom, s izlaznim kodom 1. Svaki glagol i izlazni kod nalaze se na stranici [Naredbe](commands.md). Kako se čita svaki format opisano je pod [Čitači arhiva](archive-readers.md).
