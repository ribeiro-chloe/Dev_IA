—-------------------------------------------------------------------------
##AGENTS.md - Puissance 4 à règles maisons

Projet : puissance 4 en Python(grille 7*6) avec 5 règles maisons : Tête qui tourne(1),Tetris(2), Kamikaze(3), Collectionneur(4), Inébranlable(5). ‘moteur.py’ contient le socle imposé. ‘socle_test.py’ vérifie le jeu standards(sans règles maisons)et doit rester à 15/15 après chaque règle.. Les cinq règles s'ajoutent au moteur sans modifier ses fonctions. test_socle 

## Contrat(ne jamais le changer)
def nouvelle_partie(colonnes=7, lignes=6) -> dict
def coups_possibles(etat) -> list[int]
def jouer(etat, colonne) -> dict          # renvoie un NOUVEL état
def gagnant(etat) -> str | None            # 'X', 'O', 'nul' ou None
def rejouer(coups, regles=None) -> dict     # rejoue une partie entière
Forme de l’état(un dictionnaire, rien d’autre):
{
    "colonnes": 7,
    "lignes":   6,
    "grille":   [[None, ...], ...],   # grille[ligne][colonne]
                                  # ligne 0 = HAUT, ligne lignes-1 = BAS
    "joueur":   "X",                # à qui de jouer
    "tour":     1,                  # commence à 1
    "coups":    [],                 # colonnes jouées, dans l'ordre
    "fini":     False,
} 

## Mode de jeu
- Jeu standard : `moteur.jouer` et `moteur.rejouer(coups)`. `rejouer` ignore `regles`.
- Jeu avec règles : `regles.rejouer_avec_regles(coups, REGLES)` ou, un coup à la fois, `regles.jouer_avec_regles(etat, coup, REGLES)`. Cette dernière joue UN coup à partir de l'état reçu et n'appelle jamais `rejouer`, `jouer` ni `gagnant`.
- Avec `regles=[]`, `jouer_avec_regles` se comporte comme le jeu standard (les coups spéciaux `("K", …)` et `("F", …)` sont alors refusés par `ValueError`).
- Résultat d'une partie avec règles : `regles._resultat_victoire(etat, regles)` renvoie `"X"`, `"O"`, `"nul"` ou `None`. `moteur.gagnant(etat)` ignore les règles (voir « Questions ouvertes »).
  
## Forme d'un coup (avec règles)
Le contrat dit que `coups` contient des colonnes. Avec les règles, un coup est :
- `int` : jeton normal dans la colonne (colonne de l'orientation courante) ;
- `("K", colonne)` : jeton Kamikaze (règle 3), il tombe dans la colonne comme un jeton normal ;
- `("F", ligne, colonne)` : jeton fixe (règle 5), posé sur n'importe quelle case VIDE, même en l'air. ATTENTION : pour ce coup, `ligne` 0 = BAS et `colonne` 0 = gauche, dans l'orientation
  courante du plateau (6 lignes × 7 colonnes, ou 7 × 6 après chaque rotation). L'indice dans `etat["grille"]` (ligne 0 = haut, imposé par le contrat) est `etat["lignes"] - 1 - ligne`. Exemple : `("F", 0, 1)` = bas de la colonne 1.


## Décisions de conception
1. Moments où une règle intervient: 
{"nom": "...",
 "debut_tour":      f(etat) -> etat,            # avant le choix du jeton
 "avant_coup":      f(etat, coup) -> bool,      # autorise / interdit
 "placement":       f(etat, coup) -> etat,      # change la façon de poser (règles 3, 5)
 "apres_coup":      f(etat, coup) -> etat,      # destructions, points
 "victoire":        f(etat) -> "X"|"O"|"nul"|None}
Une règle reçoit un état et renvoie un NOUVEL état. Elle ne modifie jamais l'état reçu. Les règles `avant_coup` et `victoire` ne modifient rien : elles répondent seulement.

2. Ajout clés d'état dans regles.py:
- `"reserves"` : `{"X": {"fixes": 3, "kamikaze": 1}, "O": {...}}` — usages restants (règles 3 et 5). Créée au premier coup spécial ; la règle 2 s'en sert pour redonner un jeton fixe détruit.
- `"detruits"` : `{"X": 0, "O": 0}` — nombre de jetons détruits PENDANT LES TOURS de chaque joueur, quel que soit leur propriétaire (règles 2, 3 ; lue par la règle 4). Créée à la première destruction.
- Jeton fixe (règle 5) dans la grille : `"FX"` ou `"FO"` (second caractère = propriétaire, à qui le jeton est redonné s'il est détruit). Ce n'est ni `"X"` ni `"O"` : il ne compte dans aucun alignement. Il voyage avec la case lors des rotations, sans clé supplémentaire. Toute nouvelle clé qui contient une liste ou un dictionnaire doit être copiée par `copier_etat`.

3. Forme d’un coup
Le contrat dit que ‘coups’ contient des colonnes. Avec les règles actives, un coup est :
‘int’ : jeton normal dans la colonne(colonne de l’orientation courante)
‘(“K”, colonne)’ : jeton Kamikaze(règle 3), posé dans la colonne
‘(“F”, ligne, colonne)’ : jeton fixe (règle 5), Avec ‘regles=None’, seuls les ‘int’ sont acceptés.

4. Interactions :
| Règles | Situation | Ce qui se passe |
| 1 et 2 | déclenchées au même tour | Règle 1 puis règle 2|
| 1 et 5 | lors de la règle 1 | Le plateau tourne à 90°, les jetons fixes  suivent le plateau et restent inaffectés par la gravité. |
| 2 et 4 | déclenchées au même tour | Règle 2 puis 4 |
| 2 et 5 | déclenchement de la règle 2 | Quand un jeton fixe se trouve sur une ligne supprimée par la règle 2, le jeton est détruit et redonné au joueur. |
| 3 et 4 | déclenchées au même tour | Règle 3 puis 4 |
| 3 et 5 | déclenchement règle 3 | Quand un jeton fixe se trouve sur une ligne ou colonne supprimée par la règle 3, le jeton est détruit et redonné au joueur. |


5. Usage limité : Règle 3: 1 jeton Kamikaze par joueur. Règle 5: 3 jetons fixes par joueur. Le compteur est dans `etat["reserves"]`, donc rejouer la même suite de coups redonne exactement le même résultat.

## Ordre d'application implémenté (le règlement fait foi ; en cas de divergence, le code change)
`jouer_avec_regles(etat, coup, regles)` :
0. Si `etat["fini"]` : `ValueError("partie finie")`.
1. `avant_coup` de chaque règle ; un seul `False` lève `ValueError("coup interdit")`.
2. Placement : `int` → jeton normal ; sinon crochets `placement` (règle 3 : Kamikaze, qui pose le jeton PUIS détruit sa ligne et sa colonne ; règle 5 : jeton fixe).
3. `apres_coup` des règles sans `applicable` (aucune pour l'instant).
4. Gravité, puis vérification de victoire. Si la partie est finie, la boucle suivante n'a pas lieu : la victoire est prioritaire, une ligne pleine n'est donc pas détruite.
5. Boucle « règle 2 » : tant qu'une règle `applicable` l'est (garde-fou : lignes × colonnes passages, sinon `RuntimeError`) : son `apres_coup` (destruction de TOUTES les lignes pleines d'un coup, points comptés), gravité, vérification de victoire (arrêt si la partie est finie).
6. Mise à jour de `coups`, `tour` (+1), `joueur` ; `fini` = résultat de victoire non `None`.
7. Si la partie continue : début du tour du joueur suivant. Crochets `debut_tour` (règle 1 : rotation si le nouveau `tour % 4 == 1` et `tour != 1`), gravité, victoire, puis la même boucle qu'en 5., SANS POINT si une rotation vient d'avoir lieu. Conséquence : l'état renvoyé après le coup 4, 8, 12… est déjà tourné ; `coups_possibles` porte sur la grille tournée.

## Règles de victoire
- Le résultat est donné par `_resultat_victoire(etat, regles)` : les crochets `victoire` d'abord (le premier résultat non `None` l'emporte), sinon la détection standard `victoire(etat)`.
- Détection standard : 4 alignés de `"X"` ou `"O"` (les jetons fixes ne comptent pas) ;les deux joueurs alignés en même temps : `"nul"` ; grille pleine sans alignement : `"nul"`.
- Règle 4 prioritaire : le joueur qui atteint 30 jetons détruits gagne, même si l'adversaire aligne 4 au même moment.
- Tous les jetons détruits pendant un tour comptent pour le joueur qui vient de jouer. Un seul joueur marque donc par tour.

## Interdits
- Aucune bibliothèque externe.
-Pas d'import exterieur au projet.
- Ne jamais modifier l'état reçu : toujours renvoyer un nouvel état.
- Ne jamais changer une signature du contrat, ni la forme de l'état de base. La structure de l'état reste la même, mais les valeurs `colonnes` et `lignes` peuvent s'inverser.
- Pas de classe ni d'objet pour représenter l'état ou une règle : dictionnaires et fonctions.
- Pas d'état global (compteurs, usages) en dehors de l'état.
- Ne pas inventer de comportement absent du règlement : en cas de doute, poser la question.

## Architecture
- Les règles sont écrites uniquement dans `regles.py`.
- `moteur.py` n'en dépend que dans `rejouer`, qui importe `regles.py` si `regles` n'est pas `None`.
- Une fonction d'enveloppe (ex. `jouer_avec_regles(etat, coup, regles)`) applique la séquence ci-dessus ; `jouer(etat, colonne)` reste le coup standard.
- `rejouer(coups, regles=None)` transmet `regles` à cette enveloppe.
- UNE SEULE fonction de détection dans regles.py, utilisée par le pipeline. Ne pas dupliquer la logique.
- La gravité est une fonction unique, réutilisée après chaque rotation ou destruction.

## Précisions règles
- **Rotation (règle 1)** : on tourne la grille de 90° dans le sens anti-horaire (7×6 devient 6×7 : `colonnes` et `lignes` s'inversent). Pour l’ancienne grille de R lignes et C colonnes : `ancienne[i][j] = nouvelle[R+1-j][i]`. Puis la gravité s'applique vers le bas de la nouvelle orientation.
- **Gravité** : les jetons normaux tombent ; les jetons fixes ne bougent pas et servent d'obstacle (un jeton normal s'empile dessus).
- **« Ligne remplie » (règle 2)** : ligne horizontale selon l'orientation courante du plateau.
- **Kamikaze (règle 3)** : tous les jetons détruits comptent pour le joueur qui a posé le Kamikaze. Le Kamikaze compte lui-même dans `detruits` à son activation.
- **Jeton fixe (règle 5)** : n'empêche pas une ligne d'être remplie, ne compte pas pour l'alignement de 4, n'appartient à aucun joueur. S'il est détruit, il compte dans `detruits`.

