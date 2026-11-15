---
title: "Αναγνώστες αρχείων"
nav_order: 9
lang: "el"
source: archive-readers.md
source_hash: "14a63a51eff5"
nav_exclude: true
search_exclude: true
---
# Αναγνώστες αρχείων {#archive-readers}

Ένα **container** (ή αρχείο-αρχειοθήκη) είναι ένα μεγάλο αρχείο στο οποίο ένα παιχνίδι στοιβάζει πολλά αρχεία. Ένα **CRC** ή hash είναι ένα σύντομο αποτύπωμα κάποιων bytes: αν ταιριάζει, τα bytes διαβάστηκαν σωστά. Ένα **bounding box** είναι το μικρότερο κουτί γύρω από ένα μοντέλο.

Κάτω από τις εντολές υπάρχουν αναγνώστες για τα containers που χρησιμοποιούν τα παιχνίδια. Οι μορφές τους δεν είναι τεκμηριωμένες, εκτός από το VPK της Valve και το `.cdae` του BeamNG, οπότε το «υποστηρίζεται» πρέπει να σημαίνει **επαληθευμένο σε πραγματικά αρχεία**, και όχι «δεν έσκασε». Κάθε αναγνώστης ελέγχει τον εαυτό του με κάτι που εγγυάται η μορφή: ένα hash, ένα CRC, μια αλυσίδα offsets που πρέπει να κλείνει, ένα αποθηκευμένο bounding box. Όπου ένας έλεγχος αποτυγχάνει, ο αναγνώστης αρνείται με ένα μήνυμα και δεν μαντεύει. Ένα λάθος μοντέλο μοιάζει με σωστό, μέχρι να το βάλετε δίπλα στην πίστα.

| Αναγνώστης | Ενότητα | Διαβάζει | Δεν διαβάζει | Φτάνει από |
|---|---|---|---|---|
| [Unreal .pak](reader-unreal-pak.md) | `pak.py` | εκδόσεις 8-12: ευρετήριο, καταχωρίσεις, μπλοκ Zlib/Gzip/Oodle, AES με κλειδί που δίνετε εσείς | εκδόσεις πριν από την 8, ευρετήρια μόνο με path-hash, καταχωρίσεις υπερχείλισης, περιεχόμενο assets | `identify`, `list`, `extract` |
| [Unreal 5 IoStore](reader-unreal-iostore.md) | `iostore.py`, `zen.py`, `unversioned.py`, `unrealmesh.py`, `unrealtexture.py` | `.utoc`/`.ucas` (v5 και άνω, ελεγμένο στην v8), πακέτα zen, unversioned ιδιότητες για μερικές κλάσεις component, cooked static meshes, υφές και streaming virtual textures | κρυπτογραφημένα containers, versioned πακέτα, meshes μόνο Nanite, ιδιότητες άλλων κλάσεων | `identify`, `list`, `extract`, `course` (AC Rally) |
| [Oodle](reader-oodle.md) | `oodle.py` | μπλοκ Oodle μέσω βιβλιοθήκης που υπάρχει ήδη στον υπολογιστή | οτιδήποτε χωρίς τέτοια βιβλιοθήκη· δεν συμπεριλαμβάνεται ποτέ | pak, IoStore, Frostbite |
| [Unity](reader-unity.md) | `unity.py`, `unity_mesh.py` | `SerializedFile` format 22 και άνω (Unity 2020 έως 6000), bundles `UnityFS`, μη συμπιεσμένα meshes, συμπεριλαμβανομένου του `.resS` | μορφές πριν από το 2020, ενσωματωμένα type trees, συμπιεσμένα meshes, καμία κλάση εκτός από το `Mesh` | `identify`, `meshes` |
| [Frostbite](reader-frostbite.md) | `frostbite.py`, `frostbitebundle.py`, `frostbiteebx.py`, `frostbitemesh.py`, `frostbiteterrain.py`, `frostbitematerial.py`, `frostbitelevel.py` | πίνακες `.toc` DbObject και πίνακες τμημάτων σε δυαδική μορφή, πακέτα εγκατάστασης, θέσεις chunk, inline bundles και τα manifests τους, RIFF EBX partitions, MeshSet meshes, το ύψος του εδάφους, υφές BC1/BC3/BC7 και τα shader blocks τους, θέση των ομάδων στατικών μοντέλων | πίνακες με απόκρυψη XOR, το κοντινό στο έδαφος χρώμα και οι τρύπες του, normal maps, άλφα εκτός από cut-outs | `identify`, `levels`, `level` |
| [Source 2 VPK](reader-source2-vpk.md) | `vpk.py` | εκδόσεις 1 και 2, χωρισμένα αρχεία, δεδομένα preload, έλεγχος CRC | μεταγλωττισμένα assets (`.vmdl_c`, `.vtex_c`), τη μορφή του nav mesh του CS2 | `identify`, `list`, `extract` |
| [ForzaTech](reader-forzatech.md) | `minizip.py`, `forzatech.py`, `forzatexture.py`, `forzaplacement.py`, `forzamaterial.py` | `.minizip` (LZ4, deflate, αποθηκευμένα), γεωμετρία `.modelbin`, δείγματα `.pb` (BC1, BC7, RGBA), τοποθετήσεις `.pgeo`, hashes υφών υλικών | άλλες μορφές κορυφών και δεικτών, άλλες μορφές υφών, στρώματα shader εδάφους | `course`, `courses`, `terrain`, `identify` (`.minizip`, `.modelbin`), `list` και `extract` (`.minizip`) |
| [Αρχεία BeamNG](reader-beamng.md) | `beamng.py`, `beamngshape.py`, `beamngcollada.py` | το συνδεδεμένο σύστημα αρχείων των zip, σκηνές JSON και TorqueScript, `.ter`, `.cdae` v31, Collada `.dae`, υλικά | skinned και decal meshes, κινούμενες ακολουθίες, διαδικαστική κάλυψη εδάφους | `course` (BeamNG), `identify` (zip, `.cdae`, `.ter`), `list` και `extract` (zip) |

## Κανόνες που ακολουθεί κάθε αναγνώστης {#rules-every-reader-follows}

- **Κανένα κλειδί δεν συμπεριλαμβάνεται, κανένα δεν ανακτάται.** Ένα κρυπτογραφημένο αρχείο ανοίγει μόνο με κλειδί που περνάτε εσείς (Unreal `.pak`, `--key`). Ένα κρυπτογραφημένο IoStore container αρνείται. Τίποτα δεν ψάχνει σε εκτελέσιμο αρχείο για κλειδί και τίποτα δεν διαβάζει τη μνήμη άλλης διεργασίας. Βλ. [Κανόνες και άδειες](rules-and-licences.md).
- **Δεν συμπεριλαμβάνεται ιδιόκτητος κώδικας.** Το Oodle φορτώνεται από παιχνίδι ή engine που είναι ήδη εγκατεστημένο στον υπολογιστή.
- **Αρνείται αντί να μαντεύει.** Μια άγνωστη έκδοση, κωδικοποίηση, μορφή κορυφών ή μορφή υφής δίνει ένα συγκεκριμένο σφάλμα, όπως `texture format 42 has not been identified; refusing to guess`.
- **Μόνο ανάγνωση.** Κανένας αναγνώστης δεν γράφει μέσα σε φάκελο παιχνιδιού. Οι εξαγωγές πηγαίνουν εκεί που ορίζετε εσείς.

## Τι σήμαινε «επαληθευμένο» {#what-verified-meant}

Τα νούμερα επαλήθευσης που αναφέρονται σε αυτές τις σελίδες προέρχονται από τα docstrings των ενοτήτων. Μετρήθηκαν σε εγκατεστημένα παιχνίδια όσο γραφόταν κάθε αναγνώστης. Τα συνθετικά τεστ (βλ. [Ανάπτυξη](development.md)) κλειδώνουν τις διατάξεις των πεδίων. Τα τεστ εγκατεστημένων παιχνιδιών επαναλαμβάνουν μερικούς από τους ελέγχους όταν το παιχνίδι υπάρχει στον υπολογιστή, και αλλιώς παραλείπονται. Τα νούμερα που δεν καλύπτει κάποιο τεστ δεν έχουν ξανα-ελεγχθεί από τότε.
