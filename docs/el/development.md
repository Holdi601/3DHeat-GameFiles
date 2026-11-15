---
title: "Ανάπτυξη"
nav_order: 14
lang: "el"
source: development.md
source_hash: "7ac0e851b837"
nav_exclude: true
search_exclude: true
---
# Ανάπτυξη {#development}

## Διάταξη {#layout}

```
heat3d_gamefiles/     the package: readers, course exports, the command line
heat3d_update/        the release check and updater (see Updates)
tests/                synthetic tests, fixtures, and tests against installed games
docs/                 this documentation (docs/wiki is generated from it)
VERSION               the installed version, compared with GitHub releases
requirements.txt      numpy, cryptography, lz4, Pillow, msgpack, zstandard, pytest
```

## Χάρτης ενοτήτων {#module-map}

| Ενότητα | Τι κάνει |
|---|---|
| `__main__.py` | τρέχει τον έλεγχο ενημέρωσης, μετά το `cli.main()` |
| `cli.py` | τα ρήματα, `identify`, η δρομολόγηση των αρχείων, ο εγγραφέας διαδρομών του Forza |
| `lapinput.py` | κάθε σχήμα γύρου σε θέσεις· αναζήτηση βιβλιοθήκης του FH Companion |
| `corridor.py` | η ζώνη εκατέρωθεν της οδήγησης, ως raster 4 m |
| `surfaces.py` | τα είδη εδάφους, τα ονόματα των μερών τους και τα χρώματά τους |
| `glb.py` | ο εγγραφέας `.glb` (μέρη, κάθετοι, χρώματα, υφές, κβαντοποίηση) |
| `courseexport.py` | Forza: επίπεδες UV πλακιδίων, διαχωρισμός δρόμου/άκρης, ψήσιμο εδάφους, ανύψωση decal |
| `forzainstall.py` | βιβλιοθήκες Steam και Xbox· η πίστα Forza στην οποία ανήκει ένα κουτί |
| `minizip.py` | αρχεία `.minizip` του ForzaTech και οι λίστες ονομάτων τους |
| `forzatech.py` | `.modelbin`: chunks, buffers, layouts, submeshes, υλικά |
| `forzaterrain.py` | πλακίδια εδάφους κατά θέση· κλάσεις επιφάνειας |
| `forzatexture.py` | δείγματα `.pb`· χάρτες πλακιδίων· το ψήσιμο εδάφους |
| `forzamaterial.py` | `AssetManifest.xml`· ποια χρώματα υφής έχει ένα μοντέλο· εποχές |
| `forzaplacement.py` | τοποθετήσεις `.pgeo`, επίπεδα μοντέλων, υφές, cut-outs, υποκατάστατα κτιρίων, ο προϋπολογισμός |
| `beamng.py` | εγκατάσταση BeamNG, συνδεδεμένο σύστημα αρχείων, σκηνή, έδαφος, υλικά |
| `beamngcourse.py` | η εξαγωγή διαδρομής του BeamNG |
| `beamngshape.py` | συμπιεσμένα σχήματα `.cdae` |
| `beamngcollada.py` | εναλλακτική ανάγνωση `.dae` |
| `acrally.py` | εγκατάσταση AC Rally, στάδια, τοποθέτηση εξαρτημάτων, όγκος virtual texture |
| `acrallycourse.py` | η εξαγωγή διαδρομής του AC Rally: προσαρμογή πλαισίου, έδαφος, τοποθέτηση |
| `iostore.py` | Unreal 5 `.utoc`/`.ucas` |
| `zen.py` | πακέτα Unreal 5 που έχουν μεταγλωττιστεί |
| `unversioned.py` | σχήματα unversioned ιδιοτήτων και αναγνώστης |
| `unrealmesh.py` | μεταγλωττισμένα στατικά μοντέλα |
| `unrealtexture.py` | υφές και streaming virtual textures |
| `oodle.py` | εύρεση και κλήση μιας εγκατεστημένης βιβλιοθήκης Oodle |
| `pak.py` | Unreal `.pak` |
| `unity.py`, `unity_mesh.py` | containers, bundles και μοντέλα Unity |
| `frostbite.py` | Frostbite `.toc`, πίνακες τμημάτων, πακέτα εγκατάστασης, θέσεις chunk, φορτία |
| `frostbitebundle.py` | Frostbite inline bundles, manifests bundles, ο κατάλογος ενός επιπέδου, η λίστα επιπέδων |
| `frostbiteebx.py` | Frostbite RIFF EBX partitions χωρίς βιβλιοθήκη τύπων |
| `frostbitemesh.py` | Frostbite MeshSet και τα chunks επιπέδων λεπτομέρειας του |
| `frostbiteterrain.py` | δέντρο ροής εδάφους Frostbite, σελίδες ύψους, το πλέγμα του εδάφους |
| `frostbitematerial.py` | Frostbite υφές (mips BC1/BC3/BC7), αποθήκες shader blocks, επιλογή χρωματικού χάρτη |
| `frostbitedecals.py` | Frostbite decals εδάφους και το ψήσιμο του εδάφους |
| `frostbitenav.py` | Frostbite πλακίδια navigation mesh: οι βατές επιφάνειες των στρατιωτών |
| `frostbitelevel.py` | Frostbite ομάδες στατικών μοντέλων, τοποθέτηση, η εξαγωγή `level` |
| `vpk.py` | Source 2 VPK |
| `unreallandscape.py` | Unreal 5 components τοπίου: heightmaps στο πλέγμα εδάφους (`ue-map`) |
| `unreallevel.py` | Unreal 5 χάρτες World Partition: λίστα, δομές HLOD, νερό, η εξαγωγή `ue-map` |
| `enfusion.py` | Enfusion `.pak`, `.edds`, πλακίδια εδάφους, `resourceDatabase.rdb` |
| `enfusionworld.py` | κόσμοι Arma Reforger: αρχεία `.ent`, κουτιά, η εξαγωγή `enfusion-world` |
| `forzacars.py` | κάθε αυτοκίνητο Forza σε χαμηλή λεπτομέρεια σε `.h3dcars` (`cars`) |

Όλες οι ενότητες είναι στο GitHub, στο [`heat3d_gamefiles/`](https://github.com/Holdi601/3DHeat-GameFiles/tree/main/heat3d_gamefiles).

## Εκτέλεση των τεστ {#running-the-tests}

```
pip install -r requirements.txt
python -m pytest
```

Το `pytest.ini` ορίζει `testpaths = tests` και `-q`. Δύο είδη τεστ έχουν σημασία, για διαφορετικούς λόγους:

- **Συνθετικά τεστ** φτιάχνουν αρχεία byte προς byte και τρέχουν παντού. Κλειδώνουν τις διατάξεις των πεδίων που ήταν λάθος κάποτε: το βάσης 64-bit του segment του `.minizip` και το padding ευθυγράμμισής του, η διαφυγή του μεγέθους μπλοκ του pak, ο u32 του header του Unity ανάμεσα σε δύο int64, ο δείκτης `0x7FFF` του VPK, ο διαχωρισμός του x στην κανονική του Forza.
- **Τεστ εγκατεστημένων παιχνιδιών** τρέχουν πάνω στα πραγματικά αρχεία όταν το παιχνίδι υπάρχει στον υπολογιστή, και **παραλείπονται** (δεν αποτυγχάνουν) όταν δεν υπάρχει. Είναι το μόνο που πιάνει μια διάταξη που είναι σωστή για μικρό αρχείο και λάθος για μεγάλο.

### Fixtures {#fixtures}

| Fixture | Φτιάχνει |
|---|---|
| `tests/forza_fixtures.py` | αρχεία `.minizip` (με το βάσης 64-bit, το padding, μικτούς κωδικοποιητές), manifests, μοντέλα `.modelbin` και έδαφος, δείγματα `.pb` |
| `tests/beamng_fixtures.py` | μια μικρή εγκατάσταση BeamNG: `gameengine.zip`, `content`, ένα zip επιπέδου με έδαφος 64 m, μια λωρίδα άσφαλτου, ένα decal δρόμου, ένα κιγκλίδωμα, ένα prefab, ένα στοιχείο δάσους, τη θάλασσα, υλικά και σχήματα `.cdae` στη τεκμηριωμένη διάταξη |
| `tests/unreal_fixtures.py` | ένα IoStore container με κατάλογο, ένα πακέτο zen, ένα μπλοκ unversioned ιδιοτήτων |
| `tests/frostbite_fixtures.py` | πίνακες Frostbite, bundles, EBX partitions, μοντέλα και σελίδες εδάφους, byte προς byte |

### Αρχεία τεστ {#test-files}

| Αρχείο | Καλύπτει |
|---|---|
| `test_minizip.py` | ανάγνωση, το βάσης 64-bit, ζυγοί και μονοί πίνακες bundles, αρνήσεις, το αρχείο ονομάτων |
| `test_forzatech.py` | ο πίνακας και η αλυσίδα των chunks, αρνήσεις· εγκατεστημένο: οι αλυσίδες και οι ετικέτες των πραγματικών μοντέλων |
| `test_forza_geometry.py` | τοποθέτηση στον κόσμο, διάταξη κορυφών, αρνημένες μορφές, submeshes, κάθετοι και UV |
| `test_forzaterrain.py` | το πλέγμα πλακιδίων (1023 έναντι 512 m), περικοπή, εξαγωγή |
| `test_forzatexture.py` | κεφαλίδα δείγματος, αποκωδικοποίηση, η ράφι υφών, το ψήσιμο του εδάφους |
| `test_forzamaterial.py` | το manifest, τα ονόματα, τα hashes υλικών, η επιλογή χρώματος, οι εποχές |
| `test_forzaplacement.py` | η εγγραφή `.pgeo`, τοποθέτηση αντιγράφων, επίπεδα, παραλλαγές, επιφάνειες που φαίνονται μέσα από, ένα ολόκληρο κουτί, ο προϋπολογισμός, το χρώμα placeholder, ο αυτόματος προϋπολογισμός· εγκατεστημένο: τα κράσπεδα στο έδαφος |
| `test_forzainstall.py` | εύρεση του παιχνιδιού, επιλογή πίστας |
| `test_courseexport.py` | UV πλακιδίων, το σχέδιο μερών, ανύψωση decal |
| `test_course_cli.py` | ολόκληρα τα ρήματα `course` και `courses` σε συνθετική πίστα· `terrain --route` με byte-order mark, και χωρίς `bounds` |
| `test_archive_cli.py` | `identify`, `list` και `extract` σε κάθε αρχείο με αναγνώστη (`.pak`, IoStore, `.vpk`, `.minizip` με και χωρίς ονόματα, zip, `.cdae`, `.ter`)· αποτυχίες ως μία γραμμή και κωδικός εξόδου: ένα κρυπτογραφημένο pak, ένα κρυπτογραφημένο container, ένα αρχείο που δεν είναι αρχείο αρχειοθήκης, ένα λάθος `--key` |
| `test_corridor.py` | η ζώνη, η κοπή εδάφους με αυτήν |
| `test_lapinput.py` | κάθε σχήμα γύρου, το κουτί, οι αποτυχίες, η αναζήτηση ονόματος πίστας, ποιο παιχνίδι είναι ένας φάκελος |
| `test_surfaces.py` | ποια ονόματα αποφασίζουν την επιφάνεια και ποια όχι, τα ονόματα των μερών |
| `test_glb.py` | το αρχείο είναι έγκυρο, οι κόμβοι φέρουν την κλάση τους, αρνήσεις, κβαντοποίηση |
| `test_beamng.py` | σχήματα, επίπεδο, κατηγορίες, εύρεση του επιπέδου από γύρο, η διαδρομή, η εναλλακτική Collada· εγκατεστημένο: `.cdae` έναντι `.dae`, ανοίγει κάθε επίπεδο |
| `test_acrally.py` | containers, πακέτα, ιδιότητες, μετασχηματισμοί, η προσαρμογή πλαισίου, τα μέρη και ο προϋπολογισμός των τοποθετημένων μοντέλων, virtual textures· εγκατεστημένο: στάδια και το ψημένο χρώμα εδάφους |
| `test_pak.py` | footer, καταχωρίσεις, η διαφυγή μεγέθους μπλοκ, αρνήσεις· εγκατεστημένο: offsets και SHA-1 |
| `test_unity.py` | αρνήσεις· εγκατεστημένο: ο πίνακας αντικειμένων καλύπτει το αρχείο, οι συμβολοσειρές έκδοσης, τα όρια meshes |
| `test_frostbite.py` | υπογεγραμμένες έναντι αποκρυμμένων κεφαλίδων, αρνήσεις, πακέτα εγκατάστασης (δύο πακέτα με τον ίδιο αριθμό blob)· εγκατεστημένο: κάθε πίνακας, superbundles, αλυσίδες τμημάτων, διακριτά ids, δείγματα φορτίων από το σωστό πακέτο |
| `test_frostbitelevel.py` | ids chunks με τις δικές τους θέσεις, inline bundles, manifests, MeshSet με τμήμα σκιάς και UV, μέλος ομάδας, η σύμβαση μετασχηματισμού, έδαφος δύο επιπέδων, επιλογή χρωματικού χάρτη, chunk υφής που χάνει τα μεγαλύτερα mips, ο επαναλαμβανόμενος sampler, εγγραφές decal, decal συνθεμένο με το άλφα του, φύλλο decal που χάνει από τον δικό του χάρτη επιφάνειας, τα πλακίδια πλοήγησης (επιφάνειες κρατιούνται, συνδέσεις αφήνονται έξω, αρνήσεις, μοντέλα λεπτομέρειας), υφές που επαναλαμβάνονται γραμμένες με τις δικές τους συντεταγμένες, τρίγωνα κομμένα εκεί που η υφή επαναλαμβάνεται για σφιγμένη έξοδο, το χρώμα του εδάφους από τα υλικά επιφανειών του, χάρτες μάσκας (BC4 και μη συμπιεσμένοι) τοποθετημένοι στα τεταρτημόρια τους και απορρίπτονται όταν τα σύνορά τους διαφωνούν, σελίδες colormap τοποθετημένες στα τεταρτημόρια τους, διάκριτες ανά δέντρο μάσκας, πεδία απόστασης, παλέτες και μάσκες καναλιών που ποτέ δεν λαμβάνονται ως χρώμα, το χρώμα ενός μπλοκ και ένας γκρι χάρτης βαμμένος με αυτό, μια κορυφή παλέτας στο κέντρο του δείγματός της, το πλέγμα κλίσης που απλώνεται πίσω γραμμικά, η επικάλυψη ενός αντικειμένου ζωγραφισμένη μέσω του unwrap του, ένα μπλοκ παραλλαγής κλειδωμένο από το hash του και φτασμένο μέσω ενός δίδυμου μπλοκ, ένα φύλλο γραμμάτων τοποθετημένο από τις τέταρτες συντεταγμένες υφής πάνω στην επιφάνεια που βάφει, η μπογιά ενός decal διαβασμένη από το υλικό του, γραμμές διαδρόμου και ίχνη ελαστικών ζωγραφισμένα, χάρτες ενός καναλιού αποκωδικοποιημένοι, σπαστά μοντέλα σημειωμένα στα μέρη και τα extras τους, μπλοκ σχεδίου, cinematic και φωτισμού εκτός, και ένα colormap layout που δεν διαβάζεται, χάρτες cut-out και τα masked τους, υλικά PNG δύο όψεων· εγκατεστημένο: τα decal εδάφους του επιπέδου, ο μεγαλύτερος κατάλογος επιπέδου, μοντέλα εντός των ορίων τους, μέλη ομάδων, βλάστηση πάνω στο αποκωδικοποιημένο έδαφος |
| `test_vpk.py` | ο κατάλογος, αρνήσεις, χωρισμένα αρχεία· εγκατεστημένο: οι χάρτες ανοίγουν, τα CRC ταιριάζουν, το nav mesh |
| `test_enfusion.py` | Enfusion `.pak`, `.edds`, πλακίδια εδάφους και αρχεία κόσμου· η εξαγωγή `enfusion-world` |
| `test_forzacars.py` | το αρχείο `.h3dcars` που γράφει το ρήμα `cars` |
| `test_unreallevel.py` | Unreal 5 τοπία, δομές HLOD, νερό· η εξαγωγή `ue-map` |

## Τεστ εγκατεστημένων παιχνιδιών {#installed-game-tests}

Το [`tests/installed.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/tests/installed.py)
βρίσκει παιχνίδια για τα τεστ. Το `steam_common()` απαριθμεί το `steamapps\common` κάθε βιβλιοθήκης Steam (και τους φακέλους του ίδιου του Steam), και το `installed(*globs)` επιστρέφει τις διαδρομές που ταιριάζουν με οποιοδήποτε glob από κάτω τους, αναδρομικά όπου ένα glob έχει `**`. Κάθε τεστ αποφασίζει τι χρειάζεται:

| Τεστ | Ψάχνει | Παραλείπεται με |
|---|---|---|
| `test_pak.py` | `*/(*/){0..3}Content/Paks/*.pak` με **μη κρυπτογραφημένο** ευρετήριο, έως 4 | "no shipped pak on this machine" |
| `test_unity.py` | `resources.assets` / `sharedassets0.assets` σε `*/*_Data` ή `*/*/*_Data` που δέχεται ο αναγνώστης, έως 6 | "no Unity game on this machine" |
| `test_frostbite.py` | `Battlefield*/**/*.toc` | "no Frostbite game on this machine" |
| `test_frostbitelevel.py` | `Battlefield*/**/levels/**/*.toc` | "no Frostbite level on this machine" |
| `test_vpk.py` | `Counter-Strike Global Offensive/game/csgo/maps/*.vpk`, έως 6 | "Counter-Strike 2 is not installed" |
| `test_forzatech.py` | `ForzaHorizon*/media/*.zip` | "no Forza install on this machine" |
| `test_forzaplacement.py` | τις πίστες της βιβλιοθήκης γύρων του FH Companion (αφετηρία και τερματισμός μέσα σε 50 m), με τους περισσότερους γύρους, που τοποθετεί το `find_track`· ή `HEAT3D_COURSE` | "no Forza install with a recorded lap library here" |
| `test_beamng.py` | `find_install()` | "BeamNG.drive is not installed" |
| `test_acrally.py` | `find_paks()` | "Assetto Corsa Rally is not installed" |

Τρέξτε μόνο τα τεστ ενός παιχνιδιού, ή δείξτε το τεστ κράσπεδου του Forza σε μια διαδρομή:

```
python -m pytest tests/test_vpk.py
set HEAT3D_COURSE=%LOCALAPPDATA%\FHCompanion\laps\Example Circuit (course_0_0_to_0_0)
python -m pytest tests/test_forzaplacement.py -k kerbs
```

Τα τεστ εγκατεστημένων παιχνιδιών διαβάζουν μόνο από τα παιχνίδια. Δεν γράφουν τίποτα μέσα σε φακέλους παιχνιδιών. Οι έξοδοι των τεστ πηγαίνουν στους προσωρινούς φακέλους του pytest.

## Συμβάσεις {#conventions}

- **Αρνείται αντί να μαντεύει.** Κάθε αναγνώστης πετάει τη δική του εξαίρεση (`UnsupportedPak`, `IoStoreError`, `UnsupportedForza`, `UnsupportedUnity`, `UnsupportedFrostbite`, `UnsupportedVpk`, `BeamNGError`, `PropertyError`...) με μήνυμα που λέει τι βρέθηκε και γιατί δεν διαβάστηκε.
- **Έλεγχος με βάση την ίδια τη μορφή.** Ένα hash, ένα CRC, μια αλυσίδα offsets, ένα αποθηκευμένο bounding box, η διαδρομή να βρίσκεται πάνω στο έδαφος. Όχι «δεν έσκασε».
- **Κανένα κλειδί και κανένας ιδιόκτητος κώδικας δεν συμπεριλαμβάνεται.** Βλ. [Κανόνες και άδειες](rules-and-licences.md).
- **Τα ευαίσθητα δεδομένα μένουν έξω.** Αρχεία παιχνιδιών, εξαγωγές, γύροι, καταγραφές και στιγμιότυπα δεν μπαίνουν ποτέ στο αποθετήριο. Το `.gitignore` τα εξαιρεί ανά φάκελο και ανά τύπο. Τα τεστ χρησιμοποιούν συνθετικά δεδομένα και εγκατεστημένα παιχνίδια, ποτέ περιεχόμενο παιχνιδιού που να έχει καταχωρηθεί στο αποθετήριο.
