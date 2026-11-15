---
title: "Oodle: βρίσκεται, δεν παρέχεται"
nav_order: 3
lang: "el"
source: reader-oodle.md
source_hash: "ee6d42fcfdc5"
nav_exclude: true
search_exclude: true
---
# Oodle: βρίσκεται, δεν παρέχεται {#oodle-found-not-bundled}

Το μεγαλύτερο μέρος του περιεχομένου Unreal που διανέμεται, και μερικά φορτία Frostbite, είναι συμπιεσμένο με **Oodle** (RAD Game Tools, τώρα Epic). Το Oodle είναι ιδιόκτητο. Δεν υπάρχει έκδοση για αναδιανομή ούτε υλοποίηση σε Python, και το `oo2core_*.dll` ανήκει με άδεια στο προϊόν που το στέλνει. Γι' αυτό αυτό το εργαλείο **βρίσκει ένα αντίγραφο που ήδη υπάρχει στον υπολογιστή σας και το φορτώνει**. Ποτέ δεν μεταφέρει δικό του. Το FModel και το UModel δουλεύουν με τον ίδιο τρόπο.

Πηγή: [`oodle.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/oodle.py).

## Πού ψάχνει {#where-it-looks}

Ισχύει το πρώτο αρχείο που υπάρχει, με αυτή τη σειρά:

1. Μια ρητή διαδρομή που δίνει ο καλών (Python API).
2. `HEAT3D_OODLE`: μια διαδρομή προς το DLL, ή προς έναν φάκελο που το περιέχει.
3. Μια επιφανειακή αναζήτηση, ενός επιπέδου βάθος, στους:
   - `C:\Program Files\Epic Games`
   - `C:\Program Files (x86)\Steam\steamapps\common`
   - `C:\Program Files\Unreal Engine`
   - το `steamapps\common` κάθε βιβλιοθήκης του Steam

   Για κάθε υποφάκελο `<game>`, ελέγχει το `<game>`, το `<game>\Engine\Binaries\ThirdParty\Oodle\Win64` και το `<game>\Engine\Binaries\Win64`.

Τα ονόματα αρχείων που δοκιμάζονται, το νεότερο πρώτο: από `oo2core_9_win64.dll` έως `oo2core_3_win64.dll`. Η μορφή είναι συμβατή προς τα πίσω, οπότε μια παλαιότερη βιβλιοθήκη συνήθως δουλεύει ακόμα.

Η αναζήτηση σκόπιμα **δεν** είναι αναδρομική σάρωση όλων των δίσκων, που θα κρατούσε λεπτά. Αν δεν βρει τίποτα, ορίστε το `HEAT3D_OODLE`:

```
rem cmd.exe
set HEAT3D_OODLE=C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64\oo2core_9_win64.dll

# PowerShell
$env:HEAT3D_OODLE = "C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\ThirdParty\Oodle\Win64"
```

Ένας φάκελος δουλεύει εξίσου καλά με το ίδιο το αρχείο: τα ονόματα DLL παραπάνω δοκιμάζονται μέσα του.

Μια εγκατάσταση του Unreal Engine περιέχει ένα κάτω από το `Engine\Binaries\ThirdParty\Oodle`, που είναι η πιο τακτική πηγή για προγραμματιστή. Πολλά παιχνίδια έχουν ένα δίπλα στο εκτελέσιμό τους. Τα Unreal 5 παιχνίδια συχνά συνδέουν το Oodle στατικά και δεν έχουν DLL, οπότε το αντίγραφο που βρέθηκε μπορεί να ανήκει σε άλλο παιχνίδι από εκείνο της αρχειοθήκης που διαβάζεται. Η μορφή είναι η ίδια σε κάθε περίπτωση.

## Πώς καλείται {#how-it-is-called}

Το `OodleLZ_Decompress` καλείται μέσω `ctypes` με το αναμενόμενο μήκος εξόδου (ο κατάλογος της αρχειοθήκης το ξέρει πάντα, και το Oodle δεν μπορεί να το μαντέψει), με την ασφαλή αποκωδικοποίηση ενεργή (η είσοδος δεν είναι έμπιστη), χωρίς έλεγχο CRC (το SHA-1 του pak καλύπτει ήδη τα bytes), και χωρίς νήματα. Ένα αποτέλεσμα με λάθος μήκος είναι σφάλμα. Η βιβλιοθήκη φορτώνεται μία φορά ανά εκτέλεση.

## Όταν δεν υπάρχει καμία {#when-there-is-none}

```
no Oodle library found. Most shipped Unreal content is Oodle-compressed and it cannot be decompressed without one.
  Point at a copy with HEAT3D_OODLE=<path to oo2core_9_win64.dll>.
  Any installed game or engine that ships the DLL has one; it is proprietary, so this tool does not include it.
```

Ένα στοιχείο που δεν μπορεί να αποσυμπιεστεί είναι σφάλμα, ποτέ εύλογα σκουπίδια.

Ο φορτωτής λειτουργεί μόνο στα Windows (ψάχνει για `*_win64.dll`). Βιβλιοθήκες για Linux και macOS δεν αναζητούνται.
