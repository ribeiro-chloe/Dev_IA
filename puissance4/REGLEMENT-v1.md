# Puissance 4 augmenté — règlement v1
Groupe : <Groupe 1>          Date : <05/10>

## Jeu de base
Puissance 4 standard, grille 7 × 6. Les règles ci-dessous s'y ajoutent.

## Règle 1 — <Tête qui tourne>
**Catégorie :** gravité | temporelle
**Énoncé :**   Tous les 4 coups, le plateau se retourne de 90°
**Déclenchement :** Tous les 4 coups. Au début du tour du joueur.
**Cas limite :**  
-Si un joueur aligne 4 jetons de sa couleur avec la gravité il remporte le partie
      - Si 2 joueurs gagnent en même temps il y a match nul
**Interagit avec :** règle n°2, règle n°5

## Règle 2 — <Tetris>
**Catégorie :**    placement | gravité | géométrie
**Énoncé :**       Si une ligne est remplie, la ligne se vide, les jetons ainsi détruits sont renvoyé chez le joueur correspondant
**Déclenchement :** Quand un ligne de jetons se forme après vérification de victoire par 4 à la suite
**Cas limite :**   
  - Double victoire -> match nul
  - Si une ligne est remplie après la règle n°1 , les points de destruction ne sont reçus par aucun des joueurs
**Interagit avec :** règle n°1, règle n°4, règle n°5


## Règle 3 — <Kamikaze>
**Catégorie :** Jeton spécial 
**Énoncé :** Chaque joueur à un jeton spécial, qui lorsqu’il est placé détruit la ligne et la colonne où il se trouve et s’autodétruit
**Déclenchement :** À n’importe quel tour du joueur. Ce tour, le joueur ne pose pas d’autre jeton 
**Cas limite :**  
   - Si un joueur aligne 4 jetons de sa couleur avec la gravité il remporte le partie
   - Si 2 joueurs gagnent en même temps il y a match nul
**Interagit avec :**  règle n°4, règle n°5


## Règle 4 — <Collectionneur>
**Catégorie :**   Condition de victoire
**Énoncé :**  Si un joueur atteint un nombre de jetons détruits supérieur ou égal à 100 il gagne la partie
**Déclenchement :** Quand un joueur atteint 100 jetons détruits ou plus 
**Interagit avec :** règle n°2, règle n°3


## Règle 5 — <Inébranlable>
**Catégorie :**    placement | gravité | jeton spécial | géométrie
**Énoncé :**  Chaque joueur dispose de trois jetons non affectés par la gravité. Ces jetons sont sans couleur.
**Déclenchement :** À n’importe quel tour du joueur. Ce tour, le joueur ne pose pas d’autre jeton 
**Cas limite :**   Aucun
**Interagit avec :** règle n° 1, règle n°2, règle n°3

## Interactions déclarées
| Règles | Situation | Ce qui se passe |
| 1 et 2 | déclenchées au même tour | Règle 1 puis règle 2|
| 1 et 5 | lors de la règle 1 | Le plateau tourne à 90°, les jetons fixes  suivent le plateau et restent inaffectés par la gravité. |
| 2 et 4 | déclenchées au même tour | Règle 2 puis 4 |
| 2 et 5 | déclenchement de la règle 2 | Quand un jeton fixe se trouve sur une ligne supprimée par la règle 2, le jeton est détruit et redonné au joueur. |
| 3 et 4 | déclenchées au même tour | Règle 3 puis 4 |
| 3 et 5 | déclenchement règle 3 | Quand un jeton fixe se trouve sur une ligne ou colonne supprimée par la règle 3, le jeton est détruit et redonné au joueur. |

## Ordre d'application général
<
Si tour modulo 4 == 0 :
	Règle 1 : Renversement du plateau
	Application de la gravité
	Vérification de victoire par 4 à la suite
	Tant que Règle 2 est applicable:
		Règle 2 : destruction
		Application de la gravité
		Vérification de victoire par 4 à la suite
Choix du jeton
Si Règle 5 utilisée : 
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
Tant que Règle 2 applicable : 
	Règle 2 : destruction
	Règle 4 : ajout des points
	Règle 4 : vérification des points
	Application de la gravité
	Vérification de victoire par 4 à la suite
Vérification de victoire par 4 à la suite

