---
title: "Limites et lacunes connues"
nav_order: 10
lang: fr
source: limits-and-known-gaps.md
source_hash: "d4e0f1a4714e"
nav_exclude: true
search_exclude: true
---
# Limites et lacunes connues {#limits-and-known-gaps}

Ce que l'outil ne fait pas, ce qu'il ne fait qu'en partie, et là où son comportement est inégal.
La plupart des lacunes sont des refus délibérés. Décoder sans fichier pour vérifier produit une
sortie qui a l'air juste et ne l'est pas.

## Jeux {#games}

| Jeu | Export de parcours | Pourquoi pas, ou jusqu'où |
|---|---|---|
| Forza Horizon | oui | la couleur du sol est une interprétation (voir plus bas) |
| BeamNG.drive | oui | pas de végétation au sol, textures de modèles répétitives aplaties |
| Assetto Corsa Rally | oui | modèles en couleurs unies ; pas encore testé sur un tour enregistré dans le jeu |
| Assetto Corsa EVO | **non** | tout le contenu est dans un seul paquet brouillé par une clé, et cet outil ne récupère aucune clé |
| Battlefield 6 (export de niveau, `level`) | oui, un niveau entier | terrain, maillages groupés et placés un par un, leurs cartes de couleur, le maillage de navigation des soldats, feuillage découpé ; la couleur du sol de la zone de jeu est grossière (32 m par pixel, ou une seule couleur moyenne) ; pas de translucidité ni de cartes de normales ; maillages destructibles marqués, leurs états détruits non exportés |
| Cartes Unreal 5 World Partition (export de carte, `ue-map`) | oui, une carte entière | le paysage exact ; bâtiments sous forme des maillages HLOD simplifiés de la carte, non les modèles en pleine définition ; plans d'eau ; pas de feuillage, de décalques ni de couleur de sol |
| Arma Reforger (export de monde, `enfusion-world`) | oui, un monde entier | terrain dans ses propres couleurs et la mer ; bâtiments, accessoires et rochers sous forme de boîtes de leurs modèles, non de leurs triangles ; arbres sur demande (`--trees`), en boîtes ; pas de lacs, rivières ni entités enfants |
| iRacing | **non** | les circuits sont livrés dans un format protégé qui n'est pas une cible d'extraction de fichiers |
| autre | **non** | il n'existe pas de lecteur de parcours ; reconstruisez à partir du jeu avec 3DHeat GameCapture, ou analysez les tours dans l'onglet Analyse de course de la visionneuse sans parcours |

## Moteurs et formats {#engines-and-formats}

| Format | Non implémenté |
|---|---|
| Unreal `.pak` | versions antérieures à 8 ; index avec seulement des hash de chemins (les noms ne peuvent pas être retrouvés) ; entrées dans la liste de débordement de l'index (sautées) ; décodage du contenu `.uasset`/`.umap` depuis un pak |
| Unreal IoStore | conteneurs chiffrés (refusés, pas d'option de clé) ; liste d'un conteneur sans index de répertoires (il ne nomme aucun fichier) ; paquets versionnés ; maillages Nanite seuls et non en ligne ; maillages squelettiques ; propriétés des classes sans schéma ; propriétés des composants instanciés (disposition changée dans la version du jeu) ; maillages en spline et composants de décalques |
| Unity | formats antérieurs à 22 (Unity 2019 et plus ancien) ; fichiers avec arbres de types intégrés ; maillages compressés ; toutes les classes sauf `Mesh`, donc ni transformations, ni matériaux, ni scènes ; `meshes` sur un bundle ; `list`/`extract` (utilisez `meshes`) |
| Frostbite | tables brouillées par XOR ; le graphe de couches du terrain (les masques lus dans environ un tiers des niveaux examinés) ; gabarits d'objets autres que les maillages (logique de jeu, effets, sons) ; maillages de niveau stockés en ligne ; cartes de normales et autres, alpha autre que les découpes ; trous du terrain ; la bibliothèque de types (chiffrée dans le système de fichiers initial, non touchée) ; une commande pour lister ou extraire des assets isolés |
| Source 2 | assets compilés (`.vmdl_c`, `.vtex_c`) ; le maillage de navigation de CS2 (version 36) |
| ForzaTech | formats de position autres que quatre shorts mis à l'échelle ; formats d'index autres que u16 ; codes de texture autres que 0, 9, 13 ; les couches de matériaux du shader du terrain ; tangentes |
| BeamNG | maillages skinnés et de décalques ; animation ; végétation au sol générée par procédé ; décor en bordure du monde |
| Paysages et cartes World Partition Unreal | paysages dont les cartes de hauteurs vivent dans les cellules cuites ; calques d'édition et trous ; maillages de paysage Nanite ; modèles en pleine définition placés dans les cellules ; feuillage ; matériaux de paysage |
| Enfusion | géométrie des modèles (la géométrie `.xob` est compressée dans une disposition non lue) ; `.edds` aux en-têtes d'avant DX10 ; valeurs d'objets imbriqués dans les fichiers de monde (sautées, comptées) ; entités enfants ; lacs et rivières générés ; `list`/`extract` sur un `.pak` |

## Comportements à connaître {#behaviour-worth-knowing}

- **La couleur du sol de Forza n'est pas celle du jeu.** La texture cuite est tirée des cartes de
  tuiles qui disent *où* se trouvent l'asphalte, l'herbe courte, le sol rugueux et les bois. Elle
  utilise des couleurs et un ombrage fixes, parce que les couches de matériaux propres au shader du
  terrain ne sont pas décodées.
- **`--no-textures` retire aussi l'accotement de Forza.** La séparation asphalte/accotement utilise le
  masque d'asphalte livré avec les cartes cuites. Sans textures, les bandes de route restent entières
  en route.
- **Un budget que vous donnez ne peut être dépassé que par les bordures.** Les bordures (et les modèles
  de surface de conduite de BeamNG) ne sont jamais simplifiées ni laissées de côté, dans aucun jeu : un
  `--detail-budget` plus petit que leur coût est donc dépassé par elles seules ; tout le reste est
  laissé de côté en premier. Voir [Niveaux de détail et budget](detail-budget.md).
- **Les options qui ne s'appliquent pas sont ignorées sans rien dire** : `--season` pour BeamNG et AC
  Rally, `--track` pour BeamNG et AC Rally, `--level`/`--install` pour Forza.
- **La couleur du sol d'un niveau Battlefield 6 est grossière loin de ses décalques.** Le champ de
  hauteurs est coloré à partir de la carte de couleur du fond de terrain, à 32 m par pixel au plus grand
  mip que livre le niveau — ou, là où aucune carte de fond ne couvre la zone, dans la couleur moyenne des
  matériaux de surface du terrain ; `--ground-texture` multiplie cela par la colormap du terrain (à
  0,5 m par pixel là où le niveau en a une) et cuit par-dessus les routes, aires, lignes de piste, traces
  de pneus et marquages, dans la couleur de peinture de leur matériau quand elle est définie, et une
  couleur neutre sinon ; les masques de variation des routes sont laissés de côté. Le jeu mélange ses
  couches de surface dans un graphe de shaders qui n'est pas lu ; l'export pose les couleurs des couches
  selon leurs masques et la pente du champ de hauteurs, par une règle qui lui est propre, et un niveau
  dont les pages de masques ne s'accordent pas reçoit une seule couleur. Chaque couche prend la moyenne de
  sa carte de couleur, et non sa texture. Voir [Frostbite](reader-frostbite.md#terrain-layers). Des morceaux
  du champ de hauteurs à des résolutions différentes se rejoignent par de petits paliers.
- **Une carte de couleur Battlefield 6 est choisie, non lue.** Un bloc de shader nomme chaque texture
  qu'il échantillonne sans dire laquelle est la couleur ; le choix se fait par le nom (voir
  [Frostbite](reader-frostbite.md#textures-and-materials)) et peut prendre une feuille de finition ou de
  détail pour une surface. Les feuilles de décalque (`t_de_...`) cèdent à la carte propre de la surface ;
  le décalque d'un panneau, dessiné comme son panneau, a montré son écusson tourné d'un quart. Les champs de
  distance, palettes et masques de canaux ne sont jamais pris. Les bâtiments de fond sont dessinés dans les
  couleurs de leur palette ; les cartes en gris prennent la teinte du matériau selon une règle propre à
  l'exporteur, car les noms des paramètres sont hachés, et un matériau qui peint une carte en gris à travers
  un masque à plusieurs teintes en reçoit une seule.
- **Les trous du terrain Battlefield 6 ne sont pas découpés.** Là où le sol praticable d'un niveau passe
  sous le champ de hauteurs, le jeu doit avoir découpé le terrain, et l'export ne le fait pas. Écartés comme
  emplacement des trous : les masques de couches du terrain (aucun n'est concentré là), sa trame de nœuds
  67 x 67, une valeur de hauteur réservée (aucune page de hauteurs ne contient 0 ni 65 535), les drapeaux des
  nœuds (tous identiques), et les maillages ou assets qui coupent le sol : ce qui est placé sous le sol à cet
  endroit ce sont des maillages de roche et de falaise, et aucun asset du niveau n'est nommé pour des trous,
  tunnels ou grottes. Deux arbres de trame sont décodés par longueurs de séquence mais non placés, et sont ce
  qui reste (voir [Frostbite](reader-frostbite.md#terrain-layers)).
- **Une variation d'objet Battlefield 6 atteint une section par ses jumeaux.** La variation d'une copie
  placée choisit les blocs de shader de ses sections par clé ; quand un maillage n'a pas de bloc pour une
  variation, la variante d'une section d'un autre maillage avec un bloc par défaut identique est prise (voir
  [Frostbite](reader-frostbite.md#textures-and-materials)). C'est la règle de l'exporteur ; une section sans
  jumeau qui varie garde son aspect par défaut.
- **Les matériaux superposés de Battlefield 6 sont dessinés comme leur base et une seule feuille.** Un
  panneau de mur avec des lettres est dessiné comme son plâtre, avec la feuille de lettres par-dessus ; les
  autres couches du matériau (salissure en surimpression par son masque, cartes de détail et de mousse) ne
  sont pas mélangées.
- **Le maillage de navigation est celui de l'IA, non celui des joueurs.** Il couvre ce qu'un soldat peut
  atteindre à pied : le sol, les planchers et escaliers, et certains toits, mais pas chaque point haut. Les
  liens entre surfaces (sauts, échelles, franchissements) sont laissés de côté.
- **Un niveau Battlefield 6 inclut la couche de chaque mode de jeu.** Des objets que seul un mode place
  peuvent chevaucher ceux d'un autre. `--skip` laisse des couches de côté, par leur nom.
- **`courses` concerne seulement Forza**, et ne prend que les dossiers de bibliothèque nommés `... (course_...)`.
- **Le repère du tour BeamNG est supposé** être le repère de la visionneuse `(x, z, -y)` qu'écrit l'enregistreur
  3DHeat. Les tours d'un autre enregistreur, dans le repère brut de BeamNG, ne seraient pas placés.
- **`list` et `extract` prennent les archives, non tous les formats.** Ils ouvrent un `.pak`, un `.utoc`
  IoStore, un `.vpk`, un `.minizip` et un zip. Un conteneur Unity se lit avec `meshes`, un niveau Frostbite
  avec `level`, et un `.cdae` ou `.ter` est un fichier et non une archive (`identify` le nomme). Un `.minizip`
  sans son `ChunkContentsMiniZip<n>.txt` à côté se liste par numéro d'entrée.
- **Les modèles placés dans BeamNG utilisent les textures répétitives comme couleurs moyennes**, parce que le
  sampler du `.glb` ramène les coordonnées dans l'intervalle et que la visionneuse range les textures dans un
  atlas.
- **Windows seulement, en pratique.** Chemins Steam sous `C:\Program Files`, `%LOCALAPPDATA%`, `C:\XboxGames`,
  et un `*_win64.dll` pour Oodle. Les autres plateformes n'ont pas été testées.

## Non vérifié {#unverified}

- Les anciennes versions de Python (l'outil a été lancé avec 3.13).
- Assetto Corsa Rally avec un tour enregistré dans le jeu. Il n'a été testé qu'avec des tours synthétiques
  dans des repères aléatoires.
- Les visionneuses glTF autres que la visionneuse 3DHeat.
- Si le repère de chaque jeu est gauche ou droit. L'export garde le repère de télémétrie de chaque jeu, donc
  tours et parcours s'alignent dans tous les cas.
- Le sens de `WaterBlock` à z local = 0 comme surface (BeamNG).
- Le placement Frostbite sur d'autres jeux que Battlefield 6, et sur Battlefield 6 après une mise à jour qui
  change la disposition des membres de groupe. Le lecteur ne trouve alors aucun groupe et le dit.
- Si un export Battlefield 6 s'aligne avec les positions que rapporte le jeu. Les coordonnées sont celles du
  jeu, comme pour les autres jeux, mais aucun enregistrement n'a encore été superposé à l'un d'eux.
