| Ce que l'on a demandé | Ce qui a été livré | Comment vous l'avez remarqué | Ce que vous avez changé dans la demande |
| – | – | – | – |
| Lis AGENTS.md, moteur.py et regles.py avant de proposer quoi que ce soit.

Implémente uniquement la règle 3, dont voici l'énoncé exact :
Chaque joueur à un jeton spécial, qui lorsqu’il est placé détruit la ligne et la colonne où il se trouve et s’autodétruit
Déclenchement : À n’importe quel tour du joueur. Ce tour, le joueur ne pose pas d’autre jeton 
Cas limite : 
   - Si un joueur aligne 4 jetons de sa couleur avec la gravité il remporte le partie
   - Si 2 joueurs gagnent en même temps il y a match nul


Elle s'accroche via un dictionnaire{"nom": "kamikaze", "placement":  kamikaze_placement}, ajouté à la liste REGLES de regles.py (REGLES = [REGLE_1, REGLE_2, REGLE_3]). Ne modifie pas moteur.py ni jouer_avec_regles ni les regles 1 et 2. L'état  reçu ne doit pas être modifié.

Le coup d'un jeton kamikaze s'ecrit ("K", colonne). Les coordonnées sont celles de l'orientation courante du plateau: 6 lignes sur 7 colonnes, ou 7 lignes sur 6 colonnes après chaque rotation de la règle 1. Ce tour-là, le joueur ne pose rien d'autre: le tour, le joueur et les coups sont mis à jour par le pipeline, comme pour un coup normal.

Ne crée pas de fichier de test : vérifie avec des scripts jetables dans le shell.

Ce doit être vrai :
- rejouer_avec_regles([1,1,2,("K",2)], [REGLE_1, REGLE_2, REGLE_3]) : Le joueur O detruit les jetons de la ligne 1 et de la colonne 2 en jouant un jeton kamikaze. Après le coup 4 le plateau a tourné (7 lignes, 6 colonnes) et la ligne du bas est . . . . . X (6 cases). joueur = "X", fini = False, coups = [1,1,2,("K",2)], detruits = {"X": 0, "O": 3}, reserves = {"X": {"fixes": 3, "kamikaze": 1}, "O": {"fixes": 3, "kamikaze": 0}} (le jeton kamikaze détruit mais n'est pas redonner à "O").
-python test_socle.py moteur donne toujours 15/15, et avec REGLES=[] le comportement reste celui du jeu standard.

Montre-moi le code, puis explique en une phrase quand la règle se déclenche.",
 | Une enveloppe 'jouer_avec_regles' qui passait par 'rejouer' (option proposée : modifier 'rejouer'). Une règle modifiait l'état reçu au lieu d'en rendre un nouveau. | En relisant le code et par notification de l'IA | Dans le prompt et dans AGENTS.md : " moteur.py n'est jamais modifié, 'rejouer' compris", 'jouer_avec_regles' joue un seul coup et n'appelle jamais 'rejouer', ni 'gagnant' |
| "Lis AGENTS.md, moteur.py et regles.py avant de proposer quoi que ce soit.

Implémente uniquement la règle 2, dont voici l'énoncé exact :
Si une ligne est remplie, la ligne se vide, les jetons ainsi détruits sont renvoyé chez le joueur correspondant
Déclenchement : Quand un ligne de jetons se forme après vérification de victoire par 4 à la suite
Cas limite : 
- Double victoire -> match nul
- Si une ligne est remplie après la règle n°1 , les points de destruction ne sont reçus par aucun des joueurs

Elle s'accroche via un dictionnaire{"nom": "tetris", "applicable":   f, "apres_coup": g}, ajouté à la liste REGLES de regles.py (REGLES = [REGLE_1, REGLE_2]). Ne modifie pas moteur.py ni rejouer_avec_regles. L'état  reçu ne doit pas être modifié.

Tu es autorisé à modifié le pipeline de jouer_avec_regles pour respecter cet ordre:
Si tour modulo 4 == 0 et tour!=0:
Règle 1 : Rotation du plateau
Application de la gravité
Vérification de victoire par 4 à la suite
Tant que Règle 2 est applicable:
Règle 2 : destruction
Application de la gravité
Vérification de victoire par 4 à la suite


Ne crée pas de fichier de test : vérifie avec des scripts jetables dans le shell.

Ce doit être vrai :
- rejouer_avec_regles([0,0,0,0,0,1], [REGLE_1, REGLE_2]) : après le coup 4, la colonne 0 est devenue la ligne du bas (. . O X O X). Le coup 5 (X en colonne 0) puis le coup 6 (O en colonne 1) la remplissent : X O O X O X, sans alignement de 4. La règle 2 la détruit : grille entièrement vide, lignes = 7, colonnes = 6, tour = 7, joueur = "X", fini = False, coups = [0,0,0,0,0,1]. Avec [REGLE_2] seule, la même suite ne détruit rien : grille 6x7 avec 5 "X"/"O" empilés en colonne 0 et "O" en (5,1).
-python test_socle.py moteur donne toujours 15/15, et avec REGLES=[] le comportement reste celui du jeu standard.


Montre-moi le code, puis explique en une phrase quand la règle se déclenche.",
 | Première version avec des erreurs d'indentation, qui attribuait chaque jeton détruit à la ‘couleur des jetons’ et non au joueur qui jouait | En exécutant un cas dans RECETTE.md le mauvais joueur gagnait | Ajout d'énoncé exact et d'un cas dans le prompt les jetons détruits pendant un tour comptent tous pour le joueur qui vient de jouer, quel que soit leur propriétaire |

| Lis AGENTS.md, moteur.py et regles.py avant de proposer quoi que ce soit.

Implémente uniquement l'interface graphique du jeu pour le terminal, dont voici l'énoncé exact : 
Elle doit: 
-Afficher la grille lisible d'un coup d'œil. 
-Afficher les numéros de colonnes visibles, avec ligne 0 en haut. 
-Permettre la saisie d'une colonne avec un entier ; tout le reste est rejeté sans planter. 
-Proposer une nouvelle saisie si un coup illégal ou autre chose qu'un entier est entré. 
-Refuser un coup illégal en s'appuyant sur coups_possibles(), jamais sur sa propre idée de ce qui est légal. 
-Afficher le joueur dont c'est le tour de jouer. 
-Afficher le numéro du tour. 
-Afficher une règle quand elle se déclenche et ce qu'elle vient de déclencher.
-Annoncer la fin selon gagnant() : 'X', 'O', 'nul'. 

Ne modifie aucune fonction de moteur.py ni de regles.py. 

Ne recopie aucune règle du jeu dans l’interface et ne recrée pas de logique permettant de déterminer si un coup est légal. L’interface doit utiliser uniquement les fonctions prévues par le contrat.

 Ce doit être vrai: 
-Lancer l’interface permet de jouer une partie complète uniquement au clavier.
-Une saisie comme abc, 1.5, une chaîne vide ou des caractères quelconques ne fait pas planter le programme et redemande une colonne. -Une colonne qui n’est pas dans coups_possibles() est refusée et une nouvelle saisie est demandée. 
-Lorsque la partie est terminée, le résultat affiché correspond exactement à gagnant(). 


Montre-moi le code, puis explique en quelques phrases comment elle respecte le contrat du moteur et comment elle détecte qu’une règle vient de se déclencher. | Une interface propre mais avec les règles 3 et 5 non jouable | En testant une partie dans le terminal | Permettre la saisie d’une colonne avec un entier, “F” ou “K” tout le reste est rejeté. Permettre de choisir une ligne et une colonne avec “F” et une colonne pour “K”. |
