---
title: "Αντιμετώπιση προβλημάτων"
nav_order: 11
lang: "el"
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Αντιμετώπιση προβλημάτων {#troubleshooting}

Τα μηνύματα που τυπώνει το εργαλείο όταν σταματά κάτι, τι σημαίνει το καθένα, και τι να κάνετε. Τα μηνύματα είναι αυτούσια από τον κώδικα, με τα placeholders σε γωνιώδεις αγκύλες.

## Πριν ξεκινήσει καν το εργαλείο {#before-the-tool-even-starts}

| Βλέπετε | Κάντε |
|---|---|
| `'python' is not recognized` | εγκαταστήστε Python 3.10 ή νεότερη και επιλέξτε «Add python.exe to PATH»· ανοίξτε νέο τερματικό ([Πριν ξεκινήσετε](before-you-start.md)) |
| `No module named heat3d_gamefiles` | το τερματικό είναι στον λάθος φάκελο: κάντε `cd` στον φάκελο με το `README.md` |
| `No module named numpy` (ή άλλο πακέτο) | τρέξτε `pip install -r requirements.txt` |
| μια διαδρομή με κενά κόβεται, ή `unrecognized arguments` | βάλτε τη διαδρομή σε διπλά εισαγωγικά: `"C:\My Games\lap.json"` |

## Εύρεση του παιχνιδιού {#finding-the-game}

| Μήνυμα | Σημασία | Κάντε |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | καμία βιβλιοθήκη Steam ή `C:\XboxGames` δεν έχει παιχνίδι με `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | οι συντεταγμένες του γύρου δεν βρίσκονται σε καμία εγκατεστημένη πίστα | ελέγξτε ότι ο γύρος είναι από αυτό το παιχνίδι· δώστε `--track` αν η πίστα είναι αλλού |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | υπάρχουν πλακίδια κοντά στο κουτί, αλλά κανένα στον διάδρομο | όπως παραπάνω |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | ο φάκελος δεν έχει `.utoc` που να ανοίγει | δώστε στο `--install` τον φάκελο με τα αρχεία `.utoc` |

## Εύρεση της θέσης {#finding-the-place}

| Μήνυμα | Σημασία | Κάντε |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG: κανένα επίπεδο δεν βαθμολογήθηκε πάνω από 30% | `--level <name>`· ελέγξτε ότι ο γύρος είναι στο πλαίσιο του viewer |
| `no level called '<name>'; installed: ...` | BeamNG: το `--level` δεν ταίριαξε | χρησιμοποιήστε ένα από τα ονόματα φακέλων που εμφανίζονται |
| `<level> has no scene (no main/*.level.json and no .mis)` | ο φάκελος του επιπέδου δεν έχει αρχεία σκηνής | κατεστραμμένο ή ελλιπές επίπεδο ή mod |
| `no terrain of <level> lies along the driving.` | BeamNG: ο διάδρομος δεν έχει τετράγωνα εδάφους | λάθος επίπεδο, ή επίπεδο χωρίς έδαφος εκεί που είναι ο γύρος |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally: κανένα στάδιο και πλαίσιο δεν βαθμολογήθηκε 50% | `--level <stage>`· ελέγξτε ότι οι θέσεις του γύρου είναι σε μέτρα με Y προς τα πάνω |
| `no stage called '<name>'; there are: ...` | AC Rally: το `--level` δεν ταίριαξε | χρησιμοποιήστε ένα από τα ονόματα που εμφανίζονται |
| `no ground of <stage> lies along the driving.` | AC Rally: κανένα πλακίδιο εδάφους στον διάδρομο | λάθος στάδιο |

## Ο γύρος {#the-lap}

| Μήνυμα | Κάντε |
|---|---|
| `<file> is not a lap this can read. ...` | δώστε υποστηριζόμενη μορφή, βλ. [Είσοδοι γύρων](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | το JSON δεν είναι γύρος |
| `<file> has no x, y and z columns` | ονομάστε τις στήλες του CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | ελέγξτε το όνομα, ή δώστε αρχείο |
| `'<name>' matches 3 courses: ...` | χρησιμοποιήστε μεγαλύτερο μέρος του ονόματος |
| `<name> holds no driving` | ο γύρος έχει λιγότερα από δύο δείγματα |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | το `terrain --route` χρειάζεται αρχείο διαδρομής JSON με `bounds`, όπως γράφουν τα `heat3d_capture route` και `laps`· ένα αρχείο γύρου είναι για το `course` |
| `give exactly one of --box and --route` | το `terrain` χρειάζεται μία περιοχή |
| `no course export for this lap: <reason>.` | το παιχνίδι δεν υποστηρίζεται, βλ. [Όρια και γνωστά κενά](limits-and-known-gaps.md) |

## Αρχειοθήκες {#archives}

| Μήνυμα | Σημασία |
|---|---|
| `no Oodle library found. ...` | ορίστε `HEAT3D_OODLE`, βλ. [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | ένα κρυπτογραφημένο pak: `--key <hex>` αν έχετε το κλειδί. Δεν υπάρχει άλλος τρόπος |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | το κλειδί είναι 32 bytes γραμμένα ως 64 δεκαεξαδικά ψηφία, το `0x` προαιρετικό (κωδικός εξόδου 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | δεν είναι κανένα από αυτά· το `identify` λέει τι είναι. Ένα container Unity παίρνει `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | ένα κρυπτογραφημένο container IoStore. Δεν μπορεί να διαβαστεί |
| `pak version <n>; this reader handles 8-12` | μορφή pak παλαιότερη ή νεότερη |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | από Python: δοκιμάστε το `.utoc`, που δέχονται και τα `list` και `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | ένα container IoStore που δεν ονομάζει αρχεία· τα chunks του φτάνουν μόνο μέσω άλλων πακέτων |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | το `ChunkContentsMiniZip<n>.txt` δίπλα στο αρχείο είναι από άλλο build ή άλλο αρχείο· χωρίς αυτό οι καταχωρίσεις απαριθμούνται με αριθμό |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | τα ονόματα κρύφτηκαν κατά το build |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | ένας πίνακας Frostbite στη μορφή με απόκρυψη |
| `no Frostbite game found in a Steam library; give --install` | το `levels` ή το `level` δεν βρήκε παιχνίδι Steam του οποίου ο `Data` έχει `layout.toc`· δώστε τον φάκελο του παιχνιδιού |
| `no level called '<name>'; did you mean one of ...?` | το όνομα δεν ταίριαξε με κανέναν πίνακα επιπέδου, ή ταίριαξε με πολλούς· το `levels` τους απαριθμεί |
| `nothing was placed: no static model group was recognised` | τα μέλη των ομάδων του επιπέδου έχουν άλλη υπογραφή τύπου, μετά από ενημέρωση του παιχνιδιού ή σε άλλο παιχνίδι Frostbite· η διάταξη πρέπει να μετρηθεί ξανά |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | ένα συμπιεσμένο mesh Unity |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | κρατήστε το `.resS` δίπλα στο `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | παλαιότερο build Unity |
| `<file> is an asset bundle, not a bare SerializedFile` | το `meshes` δέχεται γυμνό container |
| `texture format <n> has not been identified; refusing to guess` | μορφή δείγματος Forza που δεν έχει ακόμα εμφανιστεί |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | κρατήστε μαζί τα μέρη ενός χωρισμένου VPK |

## Εξαγωγές που βγαίνουν λάθος {#exports-that-come-out-wrong}

| Σύμπτωμα | Πιθανή αιτία |
|---|---|
| η διαδρομή είναι μετατοπισμένη σε σχέση με τον γύρο στον viewer | ο γύρος και η εξαγωγή χρησιμοποιούν διαφορετικά πλαίσια: ελέγξτε το `--game` (ένας γύρος BeamNG διαβασμένος ως Forza, για παράδειγμα) |
| καμία άκρη σε διαδρομή Forza | `--no-textures`, ή το πλακίδιο δεν είχε χάρτες για το `--season` (η κονσόλα γράφει `N without maps`) |
| ένα πλακίδιο Forza σε επίπεδα χρώματα | λείπουν οι χάρτες εδάφους του για την εποχή |
| πολύ λιγότερα τοποθετημένα αντικείμενα από ό,τι περιμένετε | ένα ρητό `--detail-budget` πολύ μικρό· η σύνοψη λέει πόσα αντίγραφα αφαιρέθηκαν |
| το αρχείο είναι πολύ μεγάλο (εκατοντάδες MB) | αστικός διάδρομος με τον αυτόματο προϋπολογισμό· χρησιμοποιήστε `--detail-budget`, `--texture-size 1024` ή `--margin 40` |
| λείπουν φράχτες | οι επιφάνειες που φαίνονται μέσα από αυτές αφαιρούνται σκόπιμα (η σύνοψη τις ονομάζει) |
| `N meshes could not be read` | ορισμένα μοντέλα χρησιμοποιούν μορφή που αρνείται ο αναγνώστης· το υπόλοιπο εξάγεται κανονικά |
| `N of M components could not be read` (AC Rally) | μια ενημέρωση του παιχνιδιού μπορεί να μετακίνησε θέσεις ιδιοτήτων· παρακαλώ αναφέρετέ το |
