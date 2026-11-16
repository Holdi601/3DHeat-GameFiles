---
title: "Maintenance"
nav_order: 99
lang: "fr"
source: maintaining.md
source_hash: "0ee713010eb1"
nav_exclude: true
search_exclude: true
---
# Maintenance : la liste de contrôle des publications {#maintaining-the-release-checklist}

Avant d'étiqueter une version (`v` + le numéro de `VERSION`), parcourez cette liste
dans l'ordre. Elle garde les pages, les images et les traductions fidèles au code.

1. **Régénérer les pages générées.**
   - `python tools/gen_docs_reference.py` réécrit
     [Référence des commandes](../cli-reference.md) à partir du `--help` du programme lui-même.
     `python tools/gen_docs_reference.py --check` renvoie 1 tant que la page
     enregistrée n'est pas à jour.
   - `python tools/docs_diagrams.py --strings` redessine les schémas dans
     `docs/assets/img/` et réécrit `docs/assets/i18n/en.json`, la liste de
     toutes les étiquettes de schéma à traduire.
2. **Lister ce qui a changé depuis la dernière version :**
   `git log --oneline v<last VERSION>..HEAD`. Chaque nouveau verbe, option, champ
   de sortie ou comportement demande une ligne dans `CHANGELOG.md` et une ligne dans son tableau
   **Docs** qui nomme la page qui l'explique. Mettez cette page à jour.
3. **Faire relire de façon indépendante** les pages et images modifiées, par quelqu'un
   (ou un agent) qui ne les a pas écrites, en lisant comme trois personnes : un débutant qui
   n'a jamais utilisé de terminal, un enfant de 8 ans et un professionnel. Les schémas sont
   vérifiés aussi : lisibles à la largeur de la page, étiquettes justes, couleurs expliquées.
4. **Corriger ce que la relecture trouve**, puis vérifier qu'aucune donnée réelle de jeu ne s'est glissée :
   aucun nom de carte, de niveau ou de joueur, aucun chiffre tiré d'enregistrements ou d'installations réels
   (utilisez des substituts comme `<map>` ou « le niveau de test »).
5. **Retraduire les pages modifiées.** Chaque page traduite garde le hash de
   la page anglaise dont elle vient ; les pages dont la source anglaise a changé sont
   retraduites, et les étiquettes de schéma avec elles. Relisez ensuite chaque
   langue : claire pour les mêmes trois lecteurs, étiquettes justes, mots conformes à
   l'interface du viewer dans cette langue.
6. **Ne publier qu'après l'accord de l'utilisateur.** Rien n'est poussé ni étiqueté avant que
   le propriétaire l'ait dit.

## Traductions : les commandes {#translations-the-commands}

Le site est traduit dans les 40 langues du viewer 3DHeat : l'anglais dans `docs/`, chaque autre
langue dans `docs/<lang>/` avec les mêmes noms de fichiers. `tools/docs_i18n.py` tient la comptabilité :

```bash
python tools/docs_i18n.py hashes             # after any English change: record each page's hash
python tools/docs_i18n.py svg-strings        # after any picture change: the labels to translate
python tools/docs_i18n.py status             # per language: current, outdated, missing pages
python tools/docs_i18n.py todo --lang de     # the German pages to (re)translate
python tools/docs_i18n.py svg-build --lang de    # German pictures from docs/assets/i18n/svg/de.json
python tools/docs_i18n.py finish --lang de   # stamp the German pages with their English hash
python tools/docs_i18n.py check              # exit 1 when hashes or labels are stale
```

Ne traduisez que ce que `todo` liste : gardez le Markdown, les liens, le code, les noms de fichiers et de colonnes tels quels,
traduisez les titres et les descriptions d'images, et utilisez les mots propres au viewer 3DHeat pour ses boutons
et ses panneaux (son dossier `src/i18n/locales/<lang>/`). Les pages de référence générées et les images de terminal restent
en anglais. Sur le site, une traduction périmée le dit et renvoie vers la page anglaise ; une page manquante
retombe sur l'anglais. Le menu de langue de l'en-tête et la redirection de la page d'accueil selon la langue du navigateur
viennent de `docs/_includes/`.
