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
- `regles=None` : Puissance 4 STANDARD, comportement strictement identique au socle.
  C'est ce que vérifie `test_socle.py`.
- `regles=<liste des cinq règles de regles.py>` : jeu avec les règles maison.
- Une règle à usage limité retient qu'elle a servi dans l'état, jamais ailleurs.


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
- "reserves": {"X": {"fixes": 3, "kamikaze": 1}, "O": {...}} — usages restants(règles 3 et 5)
-"detruits": {"X": 0, "O": 0} — jetons détruits par joueur (règles 2,3,4)
Représentation d'un jeton fixe (règle 5) dans la grille : `"FX"` ou `"FO"`
(le second caractère est le propriétaire, à qui le jeton est redonné s'il est détruit).
Ce n'est ni `"X"` ni `"O"` : il n'appartient à aucun joueur pour les alignements.
Le jeton fixe voyage ainsi avec la case lors des rotations, sans clé supplémentaire.
3. Forme d’un coup
Le contrat dit que ‘coups’ contient des colonnes. Avec les règles actives, un coup est :
‘int’ : jeton normal dans la colonne(colonne de l’orientation courante)
‘(“K”, colonne)’ : jeton Kamikaze(règle 3), posé dans la colonne
‘(“F”, ligne, colonne)’ : jeton fixe (règle 5), Avec ‘regles=None’, seuls les ‘int’ sont acceptés.
4. Ordre : <
Si tour % 4 == 1 et tour!=1:
	Règle 1 : Renversement du plateau
	Application de la gravité
	Vérification de victoire par 4 à la suite
	Tant que Règle 2 est applicable:
		Règle 2 : destruction(ces destructions ne rapportent aucun point)
		Application de la gravité
		Vérification de victoire par 4 à la suite
Choix du jeton
Si Règle 5 est utilisée : 
	Règle 5 : placement libre du jeton sur un emplacement vide
Sinon si Règle 3 est utilisée : 
	Placement normal de jeton
	Règle 3 : destruction
	Règle 4 : ajout des points
	Règle 4 : vérification des points
	Application de la gravité
Vérification de victoire par 4 à la suite
Sinon : 
	Placement normal de jeton
	Vérification de victoire par 4 à la suite
Tant que Règle 2 applicable : 
	Règle 2 : destruction
	Règle 4 : ajout des points
	Règle 4 : vérification des points
	Application de la gravité
	Vérification de victoire par 4 à la suite
Vérification de victoire par 4 à la suite
>.
Règles de victoire :
- Double victoire de 4 alignés (les deux joueurs en même temps) : match nul.
- **Règle 4 prioritaire** : un joueur qui atteint 30 jetons détruits ou plus gagne, même si l'adversaire aligne 4 au même moment.
5. Interactions :
| Règles | Situation | Ce qui se passe |
| 1 et 2 | déclenchées au même tour | Règle 1 puis règle 2|
| 1 et 5 | lors de la règle 1 | Le plateau tourne à 90°, les jetons fixes  suivent le plateau et restent inaffectés par la gravité. |
| 2 et 4 | déclenchées au même tour | Règle 2 puis 4 |
| 2 et 5 | déclenchement de la règle 2 | Quand un jeton fixe se trouve sur une ligne supprimée par la règle 2, le jeton est détruit et redonné au joueur. |
| 3 et 4 | déclenchées au même tour | Règle 3 puis 4 |
| 3 et 5 | déclenchement règle 3 | Quand un jeton fixe se trouve sur une ligne ou colonne supprimée par la règle 3, le jeton est détruit et redonné au joueur. |


6. Usage limité : Règle 3: 1 jeton Kamikaze par joueur. Règle 5: 3 jetons fixes par joueur. Le compteur est dans `etat["reserves"]`, donc rejouer la même suite de coups redonne exactement le même résultat.

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

