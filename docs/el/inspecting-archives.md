---
title: Επιθεώρηση αρχείων
nav_order: 3
lang: "el"
source: inspecting-archives.md
source_hash: "a47b1685d2d0"
nav_exclude: true
search_exclude: true
---
# Επιθεώρηση αρχείων: `identify`, `list`, `extract`, `meshes` {#inspecting-archives-identify-list-extract-meshes}

Ένα παιχνίδι βάζει τα αρχεία του σε μεγάλα κουτιά που λέγονται **αρχειοθήκες** (archives). Αυτές οι εντολές κοιτάζουν την ετικέτα ενός κουτιού, καταγράφουν τι υπάρχει μέσα και βγάζουν ένα πράγμα έξω.

Πριν εξάγετε οτιδήποτε από ένα άγνωστο παιχνίδι, κοιτάξτε τι περιέχει. Αυτές οι τέσσερις εντολές διαβάζουν ένα αρχείο και σας λένε τι είναι και τι κρατά· δεν γράφουν τίποτα, εκτός από το ένα στοιχείο που ζητάτε με το `extract`.

![identify, list and extract run on a small zip](../assets/img/inspect-archives.svg)

*Εκτέλεση σε ένα τεχνητό zip με διάταξη σαν χάρτη του BeamNG.drive.*

## Βήμα προς βήμα {#step-by-step}

1. **Ρωτήστε τι είναι το αρχείο.** Το `identify` διαβάζει τα bytes, όχι την κατάληξη:

   ```
   python -m heat3d_gamefiles identify "C:\Games\<game>\Content\Paks\<archive>.pak"
   ```

   Ονομάζει τη μορφή (Unreal `.pak`, IoStore `.utoc`/`.ucas`, Unity bundle ή `SerializedFile`, Frostbite `.toc`, Source 2 `.vpk`, ForzaTech `.minizip` ή `.modelbin`, BeamNG `.cdae`/`.ter`, zip), την έκδοσή της, πόσα στοιχεία περιέχει, και αν είναι κρυπτογραφημένη.

2. **Δείτε τι υπάρχει μέσα.** Το `list` τυπώνει μία γραμμή ανά στοιχείο: μέγεθος, συμπίεση, διαδρομή. Περιόρισέ το με `--filter` και κόψτε το με `--limit`:

   ```
   python -m heat3d_gamefiles list <archive> --filter Maps/ --limit 50
   ```

3. **Βγάλτε ένα στοιχείο.** Το `extract` γράφει ένα στοιχείο (στον φάκελο όπου βρίσκεστε, εκτός αν το `--out` δείχνει αλλού), με τη διαδρομή που τύπωσε το `list` (ή `#12`, με αριθμό, σε ένα `.minizip` χωρίς ονόματα):

   ```
   python -m heat3d_gamefiles extract <archive> <path inside> --out out\entry.bin
   ```

4. **Unity:** το `meshes` καταγράφει και ελέγχει τα mesh ενός `SerializedFile`:

   ```
   python -m heat3d_gamefiles meshes <unity .assets> --limit 20
   ```

## Επιλογές {#options}

| Εντολή | Επιλογή | Σημασία |
|---|---|---|
| `identify` | `<file>` | οποιοδήποτε αρχείο |
| `list` | `<archive>` | `.pak`, `.utoc` (ή το `.ucas` δίπλα του), `.vpk`, `.minizip`, zip |
| | `--filter TEXT` | μόνο διαδρομές που περιέχουν το TEXT |
| | `--limit N` | το πολύ N γραμμές |
| | `--key HEX` | ένα κλειδί AES-256 (64 δεκαεξαδικά ψηφία) που ήδη έχετε· το χρειάζεται μόνο ένα κρυπτογραφημένο `.pak` |
| `extract` | `<archive> <path>` | η αρχειοθήκη και η διαδρομή του στοιχείου όπως την τυπώνει το `list` |
| | `--out FILE` | πού να γραφτεί (προεπιλογή: το όνομα αρχείου του στοιχείου) |
| | `--key HEX` | όπως στο `list` |
| `meshes` | `<file>`, `--limit N` | ένα `SerializedFile` της Unity· το πολύ N mesh |

Το εργαλείο δεν συνοδεύεται από κλειδιά και δεν ανακτά κανένα: μια κρυπτογραφημένη αρχειοθήκη ανοίγει μόνο με κλειδί που εσείς δίνετε. Ένα αρχείο που δεν μπορεί να διαβάσει απορρίπτεται με μία γραμμή και κωδικό εξόδου 1. Κάθε εντολή και κωδικός εξόδου βρίσκονται στις [Εντολές](commands.md)· ο τρόπος ανάγνωσης κάθε μορφής περιγράφεται στους [Αναγνώστες αρχείων](archive-readers.md).
