---
title: "Unreal 5 IoStore"
nav_order: 2
lang: "el"
source: reader-unreal-iostore.md
source_hash: "a09552249e75"
nav_exclude: true
search_exclude: true
---
# Unreal 5 IoStore {#unreal-5-iostore}

Το Unreal 5 κυκλοφορεί τα περισσότερα περιεχόμενα σε containers **IoStore**: έναν πίνακα περιεχομένων `.utoc` και τα δεδομένα `.ucas` που ευρετηριάζει. Ένα `.pak` υπάρχει ακόμα, αλλά κρατά λίγα περισσότερα από ένα footer. Οι αναγνώστες εδώ φτάνουν από το container μέχρι τη γεωμετρία και τα pixels, όσο χρειάζεται μια διαδρομή. Χτίστηκαν και ελέγχθηκαν στο Assetto Corsa Rally (Unreal 5.6.1, τροποποιημένο), και φτάνει κανείς σε αυτούς μέσω της εξαγωγής διαδρομής του [Assetto Corsa Rally](course-assetto-corsa-rally.md). Τα `identify`, `list` και `extract` δέχονται ένα `.utoc` (ή το `.ucas` δίπλα του): τα αρχεία που ονομάζει ο κατάλογός του, με τη διαδρομή τους κάτω από το σημείο προσάρτησης. Ένα container χωρίς ευρετήριο καταλόγου δεν ονομάζει αρχεία και δεν εμφανίζεται στη λίστα.

| Στρώμα | Ενότητα |
|---|---|
| containers και το store | [`iostore.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/iostore.py) |
| μεταγλωττισμένα πακέτα «zen» | [`zen.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/zen.py) |
| δεδομένα unversioned ιδιοτήτων | [`unversioned.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unversioned.py) |
| στατικά μοντέλα | [`unrealmesh.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealmesh.py) |
| υφές και virtual textures | [`unrealtexture.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/unrealtexture.py) |

## Containers (`.utoc`, `.ucas`) {#containers-utoc-ucas}

Ο πίνακας περιεχομένων, έκδοση 8 (Unreal 5.6), little-endian:

```
header (144 bytes)  magic "-==--==--==--==-", version, header size, entry count,
                    block count, block entry size, compression method count and
                    name length, block size, directory index size, partition
                    count, container id, key GUID, flags, perfect-hash seed count,
                    partition size, chunks without a perfect hash
chunk ids           entries x 12: id u64, index u16 (big-endian), pad, type
offsets, lengths    entries x 10: two 40-bit big-endian numbers
hash seeds          seeds x 4, then chunks-without-hash x 4
blocks              blocks x 12: offset 40 bits, compressed 24, uncompressed 24, method u8 (0 = stored)
method names        count x name length, NUL-padded
signatures          when signed (skipped)
directory index     when indexed: mount point, directories, files, strings
```

- Οι εκδόσεις πριν από την 5 αρνούνται. Μόνο η έκδοση 8 έχει ελεγχθεί σε πραγματικά αρχεία.
- **Τα κρυπτογραφημένα containers αρνούνται**: `<file> is encrypted. This tool holds no keys and recovers none.` Δεν υπάρχει επιλογή κλειδιού για το IoStore.
- Μέθοδοι μπλοκ: αποθηκευμένο, `oodle` (μέσω του [Oodle](reader-oodle.md)), `zlib`, `lz4`. Οτιδήποτε άλλο αρνείται.
- Τα τμήματα μετά το πρώτο ζουν σε `<name>_s<n>.ucas`.

Το **store** ανοίγει κάθε `.utoc` στον φάκελο `Paks` του παιχνιδιού και ευρετηριάζει κάθε διαδρομή πακέτου χωρίς διάκριση πεζών και κεφαλαίων. Τα containers που δεν ανοίγουν παρακάμπτονται. Το `global.utoc` παρέχει τα αντικείμενα script (τις κλάσεις C++). Τα bulk data (`.ubulk`) ενός πακέτου βρίσκονται ως το chunk με το ίδιο id και τύπο `BULK_DATA`, σε όποιο container το κρατά.

Ελέγχθηκε: κάθε container του εγκατεστημένου παιχνιδιού και κάθε διαδρομή πακέτου μέσα του.

## Πακέτα zen {#zen-packages}

Ένα μεταγλωττισμένο πακέτο είναι μια κεφαλίδα (ονόματα, εισαγωγές, εξαγωγές, δέσμες εξαγωγών, πίνακες εξαρτήσεων, ονόματα εισαγόμενων πακέτων) ακολουθούμενη από τα σειριοποιημένα δεδομένα κάθε εξαγωγής. Τα αντικείμενα αναφέρονται το ένα στο άλλο με έναν `FPackageObjectIndex` 64-bit, του οποίου τα δύο πρώτα bits λένε τι είναι: μια εξαγωγή αυτού του πακέτου, ένα αντικείμενο script, μια εισαγωγή από άλλο πακέτο (ποιο πακέτο, και η εξαγωγή μέσω hash της διαδρομής της), ή null.

- Η διάταξη της σύνοψης άλλαξε στην 5.3 (δέσμες εξαρτήσεων και ονόματα εισαγόμενων πακέτων) και ξανά στην 5.6 (δύο ακόμα offsets). Δοκιμάζονται και οι δύο διατάξεις, και κρατιέται αυτή της οποίας ο πίνακας ονομάτων αναλύεται, οπότε η έκδοση δεν χρειάζεται να είναι γνωστή.
- **Πακέτα έκδοσης** (τύπου μη μεταγλωττισμένου) αρνούνται.
- Τα εισαγόμενα ονόματα πακέτων έχουν έναν αριθμό. Ένα πακέτο `_Terrain` με αριθμό 1 είναι το αρχείο `_Terrain_0`.
- Τα ονόματα `/Game/...` αντιστοιχίζονται στον φάκελο `Content` του έργου μέσα στο store.
- Οι αναφορές διασχίζουν πακέτα με αντιστοίχιση του δημόσιου hash της εξαγωγής.

Ελέγχθηκε: κάθε κελί κάθε σταδίου ανοίγει.

## Unversioned ιδιότητες {#unversioned-properties}

Οι μεταγλωττισμένες εξαγωγές Unreal 5 δεν ονομάζουν τις ιδιότητές τους. Μια εξαγωγή αρχίζει με κεφαλίδα από σειρές, «παράλειψε τόσα, και μετά τόσα παρόντα», και μια μάσκα που λέει ποιες παρούσες είναι μηδέν και δεν φέρουν bytes. Οι τιμές ακολουθούν με τη σειρά ιδιοτήτων της κλάσης. Για να διαβαστεί αυτό χρειάζεται το **σχήμα** κάθε κλάσης: η λίστα ιδιοτήτων της, με ακριβώς τη σειρά που τη χτίζει η μηχανή (πρώτα οι δικές της ιδιότητες, μετά του γονέα, μία θέση ανά στοιχείο στατικού πίνακα, χωρίς τις ιδιότητες μόνο του επεξεργαστή).

Τα σχήματα είναι ενσωματωμένα για τις κλάσεις που χρειάζεται μια διαδρομή:

| Κλάση | Αλυσίδα |
|---|---|
| `/Script/Engine.SceneComponent` | `USceneComponent`, `UActorComponent` |
| `/Script/Engine.StaticMeshComponent` | `UStaticMeshComponent`, `UMeshComponent`, `UPrimitiveComponent`, `USceneComponent`, `UActorComponent` |
| `/Script/Engine.InstancedStaticMeshComponent`, `HierarchicalInstancedStaticMeshComponent`, `/Script/Foliage.FoliageInstancedStaticMeshComponent` | οι αλυσίδες ISM (υπάρχουν, αλλά η εξαγωγή διαδρομής δεν τις χρησιμοποιεί, επειδή αυτή η έκδοση τις αναδιάταξε) |
| `/Script/Engine.RuntimeVirtualTextureComponent` | `URuntimeVirtualTextureComponent`, `USceneComponent`, `UActorComponent` |

Καλύπτουν επίσης τις δομές που κρατούν αυτά (`FBodyInstance`, αποκρίσεις σύγκρουσης και άλλες). Οι τύποι τιμών διαβάζονται ανά κωδικοποίηση: αριθμοί και διανύσματα σταθερού μεγέθους (`FVector`, `FRotator` ως διπλής ακρίβειας, `FTransform`...), `FName`, enums (ένα byte), αναφορές αντικειμένων (δείκτης πακέτου `i32`), soft object paths, πίνακες, εμφωλευμένες δομές, και multicast delegates (παρακάμπτονται).

Τα σχήματα είναι **μόνο ονόματα ιδιοτήτων και τύποι**, παραγόμενα από τα headers της Unreal Engine 5.6.1 (που η Epic τα κάνει διαθέσιμα σε όποιον έχει συνδεδεμένο λογαριασμό). Δεν περιλαμβάνεται κώδικας της μηχανής. Αυτή η έκδοση έχει **δύο επιπλέον θέσεις στο `UPrimitiveComponent`** από ό,τι τα headers, και **μία επιπλέον στον όγκο virtual texture**, που βρέθηκαν από τα δεδομένα και σημειώνονται ως `(unknown)`. Μια τιμή παρούσα σε μία από αυτές τις θέσεις είναι σφάλμα, όχι εικασία. Μια θέση πέρα από το τέλος ενός σχήματος, ή ένας άγνωστος τύπος, δίνει `PropertyError`.

Ελέγχθηκε: κάθε στατικό μοντέλο και κάθε component σκηνής κάθε σταδίου αποκωδικοποιείται, τελειώνοντας ακριβώς στο σταθερό native tail της κλάσης του. Μια ενημέρωση του παιχνιδιού μπορεί να μετακινήσει θέσεις. Τότε ο αναγνώστης σηκώνει σφάλμα, και η διαδρομή αναφέρει πόσα components απέτυχαν.

## Στατικά μοντέλα {#static-meshes}

Μια εξαγωγή `UStaticMesh` είναι οι ιδιότητές της ακολουθούμενες από native δεδομένα. Οι ιδιότητες δεν χρειάζονται για τη γεωμετρία και δεν διαβάζονται. Το native μέρος βρίσκεται από την σταθερή αρχή του: ένα μηδενικό GUID flag, δύο bytes σημαιών strip, `bCooked = 1`, και ο δείκτης της δικής του εξαγωγής `BodySetup` του mesh. Διαβάζεται έπειτα με τη σειρά που γράφουν τα `UStaticMesh::Serialize` και `FStaticMeshRenderData::Serialize` για ένα **μεταγλωττισμένο, μη Nanite** mesh:

- έως 16 επίπεδα λεπτομέρειας, καθένα με τα τμήματά του (υλικό, πρώτος δείκτης, πλήθος τριγώνων), τα όριά του, και όταν είναι **ενσωματωμένο**: το buffer θέσεων (float32 x 3), εφαπτόμενες, UV (όλα τα κανάλια, ημι ή πλήρους ακρίβειας), χρώματα, και το buffer δεικτών (16 ή 32 bit)·
- ό,τι ακολουθεί (ανάποδα και buffers δεικτών βάθους, δεδομένα ray tracing, δειγματολήπτες σταθμισμένοι κατά επιφάνεια) παρακάμπτεται για να φτάσει στο επόμενο επίπεδο.

Ένα επίπεδο που δεν είναι αποθηκευμένο ενσωματωμένο τερματίζει τη λίστα. Ένα mesh χωρίς κανένα αρνείται. Οι θέσεις είναι της Unreal: εκατοστόμετρα, X προς τα εμπρός, Y δεξιά, Z προς τα πάνω.

Ελέγχθηκε: σχεδόν κάθε δειγματοληπτικό mesh αποκωδικοποιείται (τα υπόλοιπα είναι σκελετικά), και η έκταση ενός πλακιδίου δρόμου ταιριάζει με τα όρια που αποθηκεύει.

## Υφές {#textures}

Μια εξαγωγή `Texture2D` είναι οι ιδιότητές της και μετά τα μεταγλωττισμένα δεδομένα πλατφόρμας της: το όνομα της μορφής pixel, το μέγεθος, και ένας πίνακας επιπέδων mip, καθένα με δείκτη στον **χάρτη bulk δεδομένων** του πακέτου (offset, μέγεθος, σημαίες· μέσα στην εξαγωγή όταν είναι ορισμένη η σημαία `0x40`, αλλιώς στο `.ubulk`). Τα δεδομένα πλατφόρμας βρίσκονται από το δικό τους σχήμα, όχι παρακάμπτοντας τις ιδιότητες, οπότε η διάταξη ιδιοτήτων της κλάσης υφής δεν έχει σημασία. Αποκωδικοποιείται το πρώτο mip που δεν είναι μεγαλύτερο από το ζητούμενο μέγεθος.

| Μορφή Unreal | Αποκωδικοποιείται ως |
|---|---|
| `PF_DXT1`, `PF_DXT3`, `PF_DXT5` | BC1, BC2, BC3 |
| `PF_BC4`, `PF_BC5`, `PF_BC7` | BC4, BC5, BC7 |
| `PF_B8G8R8A8`, `PF_R8G8B8A8` | RGBA 8-bit |
| `PF_G8` | γκρι 8-bit |

Ελέγχθηκε: μια δορυφορική εικόνα DXT5 των 4096 px, της οποίας τα δεκατρία επίπεδα είναι ακριβώς τα μεγέθη των bulk καταχωρίσεων.

## Streaming virtual textures {#streaming-virtual-textures}

Μια ψημένη `VirtualTexture2D` είναι τετράγωνα πλακίδια με περίγραμμα, ανά επίπεδο λεπτομέρειας, με διεύθυνση από **κώδικα Morton** (το x στα άρτια bits), αποθηκευμένα σε chunks του bulk δεδομένων του πακέτου. Η διάταξη διαβάζεται όπως τη γράφει το `FVirtualTextureBuiltData::Serialize` στην Unreal 5.6: επίπεδα, μέγεθος πλακιδίου, περίγραμμα, πίνακες διευθύνσεων πλακιδίων ανά mip, μορφές επιπέδων, και το chunk *n* ως η καταχώριση bulk *n*. Μια περιοχή της υφής συναρμολογείται πλακίδιο προς πλακίδιο, χωρίς τα περιγράμματα, από το επίπεδο του οποίου η ανάλυση είναι η πλησιέστερη στο ζητούμενο μέγεθος. Διαβάζεται μόνο το πρώτο στρώμα, και μόνο στις μορφές που αναφέρθηκαν παραπάνω.

Ελέγχθηκε: τα πλακίδια ενός chunk virtual texture λογαριάζονται ως προς το ακριβές byte.
