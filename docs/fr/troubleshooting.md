---
title: "Dépannage"
nav_order: 11
lang: fr
source: troubleshooting.md
source_hash: "3d2cd69d42e4"
nav_exclude: true
search_exclude: true
---
# Dépannage {#troubleshooting}

Les messages que l'outil affiche quand quelque chose l'arrête, ce que chacun signifie, et quoi faire. Les messages
sont cités tels qu'ils sont dans le code, avec les espaces réservés entre chevrons.

## Avant même le démarrage de l'outil {#before-the-tool-even-starts}

| Vous voyez | Faites |
|---|---|
| `'python' is not recognized` | installez Python 3.10 ou plus récent et cochez « Add python.exe to PATH » ; ouvrez un nouveau terminal ([Avant de commencer](before-you-start.md)) |
| `No module named heat3d_gamefiles` | le terminal est dans le mauvais dossier : `cd` vers le dossier qui contient `README.md` |
| `No module named numpy` (ou un autre paquet) | lancez `pip install -r requirements.txt` |
| un chemin contenant des espaces est coupé, ou `unrecognized arguments` | mettez le chemin entre guillemets doubles : `"C:\My Games\lap.json"` |

## Trouver le jeu {#finding-the-game}

| Message | Signification | Faites |
|---|---|---|
| `no installed Forza track found. Pass the folder directly - it is the one under media/Tracks that holds GeoChunk0.minizip.` | aucune bibliothèque Steam ni `C:\XboxGames` ne contient un jeu avec `media\Tracks` | `--track "<game>\media\Tracks\<map>"` |
| `none of the installed tracks (<names>) has terrain at x <a>..<b>, z <c>..<d>. Those are the game's own metres, as its telemetry reports them.` | les coordonnées du tour ne sont sur aucune piste installée | vérifiez que le tour vient de ce jeu ; passez `--track` si la piste est ailleurs |
| `no terrain there. <track> has tiles nearby but none that cover the driving, which usually means the lap and the track are from different games.` | des tuiles existent près de la boîte, mais aucune ne couvre la conduite dans le couloir | comme ci-dessus |
| `no BeamNG.drive install found in the Steam libraries. Name its folder with --install (the one holding gameengine.zip).` | | `--install "<folder with gameengine.zip>"` |
| `no Assetto Corsa Rally install found in the Steam libraries. Name its folder with --install.` | | `--install "<game folder>"` |
| `no readable IoStore containers in <folder>` | le dossier n'a aucun `.utoc` qui s'ouvre | faites pointer `--install` vers le dossier qui contient les fichiers `.utoc` |

## Trouver l'endroit {#finding-the-place}

| Message | Signification | Faites |
|---|---|---|
| `the lap does not lie on any installed level's terrain (best: A 12%, B 3%). Name the level with --level.` | BeamNG : aucun niveau n'a atteint 30 % | `--level <name>` ; vérifiez que le tour est dans le repère de la visionneuse |
| `no level called '<name>'; installed: ...` | BeamNG : `--level` n'a rien trouvé | utilisez l'un des noms de dossier listés |
| `<level> has no scene (no main/*.level.json and no .mis)` | le dossier du niveau n'a pas de fichier de scène | niveau ou mod cassé ou incomplet |
| `no terrain of <level> lies along the driving.` | BeamNG : le couloir ne contient aucun carré de terrain | mauvais niveau, ou niveau sans terrain à l'endroit du tour |
| `the lap does not lie on any stage's road in any frame (best: ...). Name the stage with --level.` | AC Rally : aucune étape ni aucun repère n'a atteint 50 % | `--level <stage>` ; vérifiez que les positions du tour sont en mètres avec y vers le haut |
| `no stage called '<name>'; there are: ...` | AC Rally : `--level` n'a rien trouvé | utilisez l'un des noms listés |
| `no ground of <stage> lies along the driving.` | AC Rally : aucune tuile de sol dans le couloir | mauvaise étape |

## Le tour {#the-lap}

| Message | Faites |
|---|---|
| `<file> is not a lap this can read. ...` | donnez une forme prise en charge, voir [Entrées de tour](lap-inputs.md) |
| `<file> is JSON, but holds neither positions nor Lap.samples nor bounds` | le JSON n'est pas un tour |
| `<file> has no x, y and z columns` | nommez les colonnes du CSV `x`, `y`, `z` |
| `'<name>' is not a file, and no course in <library> matches it` | vérifiez le nom, ou passez un fichier |
| `'<name>' matches 3 courses: ...` | utilisez une partie plus longue du nom |
| `<name> holds no driving` | le tour a moins de deux points |
| `<file> has no bounds; --route takes a route file with "bounds": {"min": [x, y, z], "max": [x, y, z]}` | `terrain --route` a besoin d'un JSON de parcours avec `bounds`, tel que l'écrivent `heat3d_capture route` et `laps` ; un fichier de tour sert à `course` |
| `give exactly one of --box and --route` | `terrain` a besoin d'une seule zone |
| `no course export for this lap: <reason>.` | le jeu n'est pas pris en charge, voir [Limites et lacunes connues](limits-and-known-gaps.md) |

## Archives {#archives}

| Message | Signification |
|---|---|
| `no Oodle library found. ...` | définissez `HEAT3D_OODLE`, voir [Oodle](reader-oodle.md) |
| `<file> has an encrypted index. Pass the AES key (--key, or aes_key= from Python) if you hold one; this tool does not recover keys.` | un pak chiffré : `--key <hex>` si vous détenez la clé. Il n'y a pas d'autre moyen |
| `--key is not hexadecimal: '<key>'`, `--key takes an AES-256 key, 64 hex digits; this one has <n>` | la clé fait 32 octets écrits en 64 chiffres hexadécimaux, `0x` facultatif (code de sortie 2) |
| `<file> is not an archive list and extract read (an Unreal .pak or IoStore .utoc, a Source 2 .vpk, a ForzaTech .minizip, or a zip)` | ce n'est aucun de ceux-là ; `identify` dit ce que c'est. Un conteneur Unity passe par `meshes` |
| `<file> is encrypted. This tool holds no keys and recovers none.` | un conteneur IoStore chiffré. Il ne peut pas être lu |
| `pak version <n>; this reader handles 8-12` | un format de pak plus ancien ou plus récent |
| `<file> has no pak footer. A UE 4.26+ title may ship its content as IoStore (.utoc/.ucas) instead` | depuis Python : essayez le `.utoc`, que prennent aussi `list` et `extract` |
| `<file> has no directory index, so its chunks carry no names to list` | un conteneur IoStore qui ne nomme aucun fichier ; ses morceaux ne sont atteints que par d'autres paquets |
| `<list>.txt names <n> entries but <archive>.minizip holds <m>; the two do not belong together` | le `ChunkContentsMiniZip<n>.txt` à côté de l'archive vient d'un autre build ou d'une autre archive ; sans lui, les entrées sont listées par numéro |
| `<file> carries only the path-hash index, so file names cannot be recovered from it` | les noms ont été hachés à la compilation |
| `<file> is XOR-obfuscated. That form is not implemented, ...` | une table Frostbite sous la forme brouillée |
| `no Frostbite game found in a Steam library; give --install` | `levels` ou `level` n'a trouvé aucun jeu Steam dont `Data` contient un `layout.toc` ; passez le dossier du jeu |
| `no level called '<name>'; did you mean one of ...?` | le nom ne correspond à la table d'aucun niveau, ou à plusieurs ; `levels` les liste |
| `nothing was placed: no static model group was recognised` | la signature de type des membres de groupe du niveau a changé, après une mise à jour du jeu ou dans un autre jeu Frostbite ; la disposition doit être mesurée à nouveau |
| `mesh '<name>' is stored compressed; that encoding is not implemented` | un maillage Unity compressé |
| `mesh vertices live in <x>.resS, which is not beside the container in <folder>` | gardez le `.resS` à côté du `.assets` |
| `<file>: format <n> predates Unity 2020 ...` | un build Unity plus ancien |
| `<file> is an asset bundle, not a bare SerializedFile` | `meshes` prend un conteneur nu |
| `texture format <n> has not been identified; refusing to guess` | un format de nuancier Forza pas encore vu |
| `<path> lives in <part>.vpk, which is not beside <dir>.vpk` | gardez ensemble les parties d'un VPK découpé |

## Exports qui sortent faux {#exports-that-come-out-wrong}

| Symptôme | Cause probable |
|---|---|
| le parcours est décalé par rapport au tour dans la visionneuse | le tour et l'export n'utilisent pas le même repère : vérifiez `--game` (un tour BeamNG lu comme Forza, par exemple) |
| aucun accotement dans un parcours Forza | `--no-textures`, ou la tuile n'avait pas de cartes pour cette `--season` (la console affiche `N without maps`) |
| une tuile Forza en couleurs unies | ses cartes de sol manquent pour la saison |
| beaucoup moins d'objets placés que prévu | un `--detail-budget` explicite trop petit ; le résumé indique combien de copies ont été laissées de côté |
| le fichier est très gros (des centaines de Mo) | un corridor urbain sous le budget automatique ; utilisez `--detail-budget`, `--texture-size 1024`, ou `--margin 40` |
| des clôtures manquent | les surfaces transparentes sont laissées de côté à dessein (le résumé les nomme) |
| `N meshes could not be read` | certains modèles utilisent un format que le lecteur refuse ; le reste est tout de même exporté |
| `N of M components could not be read` (AC Rally) | un correctif du jeu a peut-être déplacé des emplacements de propriétés ; merci de le signaler |
