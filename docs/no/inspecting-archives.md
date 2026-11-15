---
title: Undersøke arkiver
nav_order: 3
lang: "no"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Undersøke arkiver: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Et spill pakker filene sine i store esker som kalles **arkiver**. Disse
kommandoene ser på merkelappen på en eske, lister hva som er i den, og tar ut
én ting.

Før du eksporterer noe fra et ukjent spill, se på hva det leverer. Disse fire
verbene leser en fil og forteller deg hva den er og hva den inneholder; de skriver
ingenting unntatt den ene oppføringen du ber `extract` om.

![identify, list og extract kjørt på en liten zip](../assets/img/inspect-archives.svg)

*En kjøring på et syntetisk zip lagt opp som en BeamNG.drive-nivå.*

## Steg for steg {#step-by-step}

1. **Spør hva filen er.** `identify` leser bytene, ikke filendelsen:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Den navngir formatet (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity-pakke eller
   `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` eller
   `.modelbin`, BeamNG `.cdae`/`.ter`, zip), versjonen, hvor mange oppføringer den
   har, og om den er kryptert.

2. **List hva som er inni.** `list` skriver én linje per oppføring: størrelse,
   komprimering, sti. Innsnevre med `--filter`, begrens med `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Ta ut én oppføring.** `extract` skriver én oppføring (inn i mappen du står i,
   med mindre `--out` sier hvor), etter stien `list` skrev ut (eller `#12`, etter
   nummer, i en `.minizip` uten navn):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** `meshes` lister og sjekker modellene i en `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Alternativer {#options}

| Verb | Alternativ | Betydning |
|---|---|---|
| `identify` | `<file>` | en hvilken som helst fil |
| `list` | `<archive>` | `.pak`, `.utoc` (eller `.ucas` ved siden av), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | bare stier som inneholder TEXT |
| | `--limit N` | høyst N linjer |
| | `--key HEX` | en AES-256-nøkkel (64 heksadesimale siffer) du allerede har; bare en kryptert `.pak` trenger den |
| `extract` | `<archive> <path>` | arkivet og oppføringens sti slik `list` skriver den |
| | `--out FILE` | hvor den skal skrives (standard: oppføringens filnavn) |
| | `--key HEX` | som for `list` |
| `meshes` | `<file>`, `--limit N` | en Unity `SerializedFile`; høyst N modeller |

Verktøyet leverer ingen nøkler og henter ingen ut: et kryptert arkiv åpnes bare
med en nøkkel du selv oppgir. En fil den ikke kan lese, avvises på én linje med
avslutningskode 1. Alle verb og avslutningskoder står under
[Kommandoer](commands.md); hvordan hvert format leses, står under
[Arkivlesere](archive-readers.md).
