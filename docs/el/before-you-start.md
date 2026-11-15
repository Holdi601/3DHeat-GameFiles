---
title: Πριν ξεκινήσετε
nav_order: 2
lang: "el"
source: before-you-start.md
source_hash: "e32b8f35ade9"
nav_exclude: true
search_exclude: true
---
# Πριν ξεκινήσετε {#before-you-start}

Δεν έχετε ξαναδουλέψει με τη γραμμή εντολών; Αυτή η σελίδα σας πηγαίνει από το μηδέν σε ένα λειτουργικό εργαλείο
σε περίπου δέκα λεπτά. Πληκτρολογείτε εντολές σε ένα παράθυρο που λέγεται **τερματικό**, και το εργαλείο
απαντά με κείμενο.

## 1. Εγκαταστήστε την Python {#install-python}

1. Πηγαίνετε στο [python.org/downloads](https://www.python.org/downloads/) και κατεβάστε
   **Python 3.10 ή νεότερη**.
2. Τρέξτε το πρόγραμμα εγκατάστασης. Στην πρώτη οθόνη επιλέξτε **«Add python.exe to PATH»**,
   και μετά κάντε κλικ στο **Install Now**.

## 2. Αποκτήστε το εργαλείο {#get-the-tool}

- **Με git:** `git clone https://github.com/Holdi601/3DHeat-GameFiles.git`
- **Χωρίς git:** στη [σελίδα του GitHub](https://github.com/Holdi601/3DHeat-GameFiles),
  κάντε κλικ στο πράσινο κουμπί **Code**, μετά στο **Download ZIP**, και αποσυμπιέστε το.

## 3. Ανοίξτε τερματικό στον φάκελο του εργαλείου {#open-a-terminal-in-the-tools-folder}

- Στην Εξερεύνηση αρχείων, ανοίξτε τον φάκελο που περιέχει το `README.md`. Κάντε κλικ στη γραμμή
  διεύθυνσης, πληκτρολογήστε `cmd` και πατήστε Enter. Ανοίγει ένα μαύρο παράθυρο, ήδη σε αυτόν τον φάκελο.
- Ή ανοίξτε το **Windows Terminal** και πηγαίνετε εκεί με `cd`:

  ```
  cd "C:\Users\you\Downloads\3DHeat-GameFiles"
  ```

## 4. Εγκαταστήστε όσα χρειάζεται το εργαλείο {#install-what-the-tool-needs}

```
pip install -r requirements.txt
```

Θα δείτε γραμμές που τελειώνουν σε `Successfully installed ...`.

## 5. Ελέγξτε ότι δουλεύει {#check-that-it-works}

```
python -m heat3d_gamefiles --help
```

Θα δείτε `usage: heat3d_gamefiles [-h]` και μια λίστα εντολών (`identify`,
`list`, `extract`, `course`, ...). Αυτό είναι επιτυχία: το εργαλείο είναι έτοιμο.

## Ανάγνωση των παραδειγμάτων {#reading-the-examples}

- Το `<something>` είναι **σημείο κράτησης θέσης**: πληκτρολογήστε αντί γι' αυτό τη δική σας τιμή, χωρίς τις γωνιώδεις
  αγκύλες. Το `<lap file>` γίνεται, για παράδειγμα, `laps\my_lap.json`.
- Το `[--option]` μέσα σε τετράγωνες αγκύλες είναι **προαιρετικό**: αφήστε το έξω αν δεν το χρειάζεστε.
- Μια διαδρομή με κενά θέλει **διπλά εισαγωγικά**: `"C:\My Games\lap.json"`.
- Εκτελείτε κάθε εντολή μέσα στον φάκελο του εργαλείου (βήμα 3).

## Όταν κάτι πάει στραβά {#when-something-goes-wrong}

| Βλέπετε | Τι να κάνετε |
|---|---|
| `'python' is not recognized` | Η Python δεν είναι εγκατεστημένη, ή δεν επιλέχθηκε το «Add to PATH». Τρέξτε ξανά το πρόγραμμα εγκατάστασης, επιλέξτε το, και μετά ανοίξτε νέο τερματικό. |
| `No module named heat3d_gamefiles` | Το τερματικό είναι σε λάθος φάκελο. Κάντε `cd` στον φάκελο που περιέχει το `README.md`. |
| `No module named numpy` (ή άλλο όνομα) | Παραλείφθηκε το βήμα 4. Τρέξτε `pip install -r requirements.txt`. |
| `can't open file` / `not found` με διαδρομή | Η διαδρομή έχει κενά χωρίς εισαγωγικά, ή ένα τυπογραφικό λάθος. Βάλτε την σε διπλά εισαγωγικά. |

Περισσότερα μηνύματα και οι λύσεις τους: [Αντιμετώπιση προβλημάτων](../troubleshooting.md).
