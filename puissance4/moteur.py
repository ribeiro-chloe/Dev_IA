"""Puissance 4 — socle impose. Lot 1.

Ces quatre signatures sont un CONTRAT : ne changez ni les noms, ni les parametres,
ni la forme de l'etat. Elles sont verifiees telles quelles a la correction.

L'etat est un dictionnaire, et rien d'autre (pas de classe, pas d'objet) :

    {
        "colonnes": 7,
        "lignes":   6,
        "grille":   [[None, ...], ...],   # grille[ligne][colonne]
                                          # ligne 0 = HAUT, ligne lignes-1 = BAS
        "joueur":   "X",                  # a qui de jouer
        "tour":     1,                    # commence a 1
        "coups":    [],                   # colonnes jouees, dans l'ordre
        "fini":     False,
    }

Regle du jeu de base : chacun depose a son tour un jeton dans une colonne, le jeton
tombe sur la case libre la plus basse, et le premier qui aligne 4 jetons gagne
(horizontalement, verticalement ou en diagonale).

Vos cinq regles maison ne vont PAS ici : voir la section en fin de fichier.
"""

JOUEURS = ("X", "O")


def nouvelle_partie(colonnes=7, lignes=6):
    """Etat d'une partie qui commence. Deja ecrit : c'est la forme de l'etat."""
    return {
        "colonnes": colonnes,
        "lignes": lignes,
        "grille": [[None] * colonnes for _ in range(lignes)],
        "joueur": "X",
        "tour": 1,
        "coups": [],
        "fini": False,
    }


def coups_possibles(etat):
    """Indices des colonnes ou l'on peut encore jouer, dans l'ordre croissant.

    Renvoie une liste vide si la partie est finie.
    """
    if etat["fini"]:
        return []
    return [
        colonne
        for colonne in range(etat["colonnes"])
        if etat["grille"][0][colonne] is None
    ]


def jouer(etat, colonne):
    """Joue un jeton dans `colonne` et renvoie un NOUVEL etat.

    L'etat recu ne doit pas etre modifie — c'est ce qui permet de rejouer une partie
    et de revenir en arriere. Leve ValueError si le coup est illegal.
    """
    if (
        not isinstance(colonne, int)
        or isinstance(colonne, bool)
        or colonne not in coups_possibles(etat)
    ):
        raise ValueError("coup illegal")

    nouvel_etat = etat.copy()
    nouvel_etat["grille"] = [ligne.copy() for ligne in etat["grille"]]
    nouvel_etat["coups"] = etat["coups"].copy()

    ligne = next(
        index
        for index in range(etat["lignes"] - 1, -1, -1)
        if nouvel_etat["grille"][index][colonne] is None
    )
    joueur = etat["joueur"]
    nouvel_etat["grille"][ligne][colonne] = joueur
    nouvel_etat["coups"].append(colonne)
    nouvel_etat["tour"] += 1
    nouvel_etat["joueur"] = "O" if joueur == "X" else "X"

    grille = nouvel_etat["grille"]
    aligne = False
    for delta_ligne, delta_colonne in ((0, 1), (1, 0), (1, 1), (1, -1)):
        total = 1
        for sens in (-1, 1):
            l, c = ligne + sens * delta_ligne, colonne + sens * delta_colonne
            while (
                0 <= l < etat["lignes"]
                and 0 <= c < etat["colonnes"]
                and grille[l][c] == joueur
            ):
                total += 1
                l += sens * delta_ligne
                c += sens * delta_colonne
        if total >= 4:
            aligne = True
            break

    nouvel_etat["fini"] = aligne or all(
        grille[0][c] is not None for c in range(etat["colonnes"])
    )
    return nouvel_etat


def gagnant(etat):
    """'X', 'O', 'nul' si la grille est pleine sans alignement, sinon None."""
    grille = etat["grille"]
    lignes = etat["lignes"]
    colonnes = etat["colonnes"]

    for ligne in range(lignes):
        for colonne in range(colonnes):
            joueur = grille[ligne][colonne]
            if joueur is None:
                continue
            for delta_ligne, delta_colonne in (
                (0, 1),
                (1, 0),
                (1, 1),
                (1, -1),
            ):
                fin_ligne = ligne + 3 * delta_ligne
                fin_colonne = colonne + 3 * delta_colonne
                if not (
                    0 <= fin_ligne < lignes
                    and 0 <= fin_colonne < colonnes
                ):
                    continue
                if all(
                    grille[ligne + pas * delta_ligne][colonne + pas * delta_colonne]
                    == joueur
                    for pas in range(1, 4)
                ):
                    return joueur

    if all(grille[0][colonne] is not None for colonne in range(colonnes)):
        return "nul"
    return None


def rejouer(coups, regles=None):
    """Rejoue une partie entiere depuis une liste de colonnes. Deja ecrit.

    C'est par cette fonction que votre jeu sera verifie : elle doit rester capable
    de rejouer n'importe quelle suite de coups, regles maison comprises.
    """
    etat = nouvelle_partie()
    for colonne in coups:
        etat = jouer(etat, colonne)
    return etat


# ---------------------------------------------------------------------------
# LE POINT D'ACCROCHE DES REGLES MAISON
# ---------------------------------------------------------------------------
# Vos cinq regles ne s'ecrivent pas dans les fonctions ci-dessus : elles arrivent
# ici, et le lot 2 les branchera. C'est a VOUS de decider comment — et cette
# decision se prend au TP2, avant d'ecrire la moindre regle.
#
# Les questions a trancher, et a consigner dans CLAUDE.md :
#
#   - A quel moment une regle intervient-elle ? Avant le coup (elle l'autorise ou
#     l'interdit) ? Apres (elle deplace des jetons) ? Sur la victoire ?
#   - Une regle recoit quoi, et rend quoi ? Un etat ? Un etat modifie ?
#   - Dans quel ordre s'appliquent deux regles declenchees au meme tour ?
#   - Comment une regle a usage limite retient-elle qu'elle a servi ?
#
# Aucune de ces reponses n'est dans ce fichier, et c'est voulu : c'est le travail
# du lot 1 de la concevoir, et celui du lot 2 de s'en servir sans rien reecrire.