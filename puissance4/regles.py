"""Moteur générique pour les crochets de règles maison de Puissance 4."""

from moteur import nouvelle_partie


def _copier_valeur(valeur):
    if isinstance(valeur, dict):
        return {cle: _copier_valeur(element) for cle, element in valeur.items()}
    if isinstance(valeur, list):
        return [_copier_valeur(element) for element in valeur]
    if isinstance(valeur, tuple):
        return tuple(_copier_valeur(element) for element in valeur)
    return valeur


def copier_etat(etat):
    """Renvoie une copie indépendante de l'état et de ses données imbriquées."""
    return _copier_valeur(etat)


def gravite(etat):
    """Fait tomber X et O dans chaque segment séparé par un jeton fixe."""
    nouvel_etat = copier_etat(etat)
    grille = nouvel_etat["grille"]

    for colonne in range(etat["colonnes"]):
        debut_segment = 0
        for ligne in range(etat["lignes"] + 1):
            fixe = (
                ligne < etat["lignes"]
                and isinstance(grille[ligne][colonne], str)
                and grille[ligne][colonne].startswith("F")
            )
            fin_segment = ligne == etat["lignes"] or fixe
            if not fin_segment:
                continue

            jetons = [
                grille[index][colonne]
                for index in range(debut_segment, ligne)
                if grille[index][colonne] in ("X", "O")
            ]
            for index in range(debut_segment, ligne):
                grille[index][colonne] = None
            destination = ligne - len(jetons)
            for jeton in jetons:
                grille[destination][colonne] = jeton
                destination += 1

            if fixe:
                debut_segment = ligne + 1

    return nouvel_etat


def victoire(etat):
    """Renvoie le résultat standard des alignements, ou None si la partie continue."""
    grille = etat["grille"]
    lignes = etat["lignes"]
    colonnes = etat["colonnes"]
    gagnants = set()

    for ligne in range(lignes):
        for colonne in range(colonnes):
            joueur = grille[ligne][colonne]
            if joueur not in ("X", "O"):
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
                    gagnants.add(joueur)

    if len(gagnants) > 1:
        return "nul"
    if gagnants:
        return next(iter(gagnants))
    if all(
        grille[ligne][colonne] is not None
        for ligne in range(lignes)
        for colonne in range(colonnes)
    ):
        return "nul"
    return None


def _obtenir_crochet(regle, nom):
    crochet = regle.get(nom)
    if crochet is not None and not callable(crochet):
        raise TypeError(f"le crochet {nom!r} doit être appelable")
    return crochet


def _appliquer_crochet(etat, crochet, *arguments):
    resultat = crochet(copier_etat(etat), *arguments)
    if not isinstance(resultat, dict):
        raise TypeError("un crochet d'état doit renvoyer un dictionnaire")
    return copier_etat(resultat)


def _resultat_victoire(etat, regles):
    for regle in regles:
        crochet = _obtenir_crochet(regle, "victoire")
        if crochet is None:
            continue
        resultat = crochet(copier_etat(etat))
        if resultat not in (None, "X", "O", "nul"):
            raise ValueError("un crochet victoire doit renvoyer X, O, nul ou None")
        if resultat is not None:
            return resultat
    return victoire(etat)


def _marquer_fin_si_necessaire(etat, regles):
    if _resultat_victoire(etat, regles) is None:
        return etat, False
    nouvel_etat = copier_etat(etat)
    nouvel_etat["fini"] = True
    return nouvel_etat, True


def _regles_applicables(etat, regles):
    applicables = []
    for regle in regles:
        crochet_applicable = _obtenir_crochet(regle, "applicable")
        crochet_apres = _obtenir_crochet(regle, "apres_coup")
        if crochet_applicable is None or crochet_apres is None:
            continue
        resultat = crochet_applicable(copier_etat(etat))
        if not isinstance(resultat, bool):
            raise TypeError("un crochet applicable doit renvoyer un booléen")
        if resultat:
            applicables.append(crochet_apres)
    return applicables


def _boucle_applicables(etat, coup, regles, limite, arreter_a_victoire):
    for _ in range(limite):
        passage_effectue = False
        for regle in regles:
            crochet_applicable = _obtenir_crochet(regle, "applicable")
            crochet_apres = _obtenir_crochet(regle, "apres_coup")
            if crochet_applicable is None or crochet_apres is None:
                continue
            resultat = crochet_applicable(copier_etat(etat))
            if not isinstance(resultat, bool):
                raise TypeError("un crochet applicable doit renvoyer un booléen")
            if resultat:
                passage_effectue = True
                etat = _appliquer_crochet(etat, crochet_apres, coup)

        if not passage_effectue:
            return etat, False
        etat = gravite(etat)
        etat, termine = _marquer_fin_si_necessaire(etat, regles)
        if termine and arreter_a_victoire:
            return etat, True

    if _regles_applicables(etat, regles):
        raise RuntimeError("la boucle applicable dépasse lignes * colonnes passages")
    return etat, False


def _poser_jeton(etat, colonne):
    if (
        not isinstance(colonne, int)
        or isinstance(colonne, bool)
        or not 0 <= colonne < etat["colonnes"]
    ):
        raise ValueError("coup illegal")

    nouvel_etat = copier_etat(etat)
    grille = nouvel_etat["grille"]
    premiere_case_occupee = next(
        (
            ligne
            for ligne in range(etat["lignes"])
            if grille[ligne][colonne] is not None
        ),
        etat["lignes"],
    )
    ligne_pose = premiere_case_occupee - 1
    if ligne_pose < 0:
        raise ValueError("coup illegal")
    grille[ligne_pose][colonne] = etat["joueur"]
    return nouvel_etat


def jouer_avec_regles(etat, coup, regles):
    """Joue un coup avec des règles décrites par des dictionnaires de crochets.

    Crochets facultatifs : ``debut_tour(etat) -> nouvel_etat``,
    ``avant_coup(etat, coup) -> bool``, ``placement(etat, coup) ->
    nouvel_etat | None``, ``apres_coup(etat, coup) -> nouvel_etat``,
    ``applicable(etat) -> bool`` et ``victoire(etat) -> "X" | "O" |
    "nul" | None``. Les règles sont parcourues dans l'ordre de la liste.
    ``avant_coup`` est vérifié avant le placement ; un résultat faux l'interdit.
    Un crochet ``placement`` peut prendre en charge un coup non entier en
    renvoyant un état ; le premier état renvoyé gagne. Les retours non nuls des
    crochets ``victoire`` sont prioritaires sur la victoire standard.

    Au début du tour, les ``debut_tour`` précèdent gravité, victoire, puis les
    passages applicables. Après placement, les ``apres_coup`` sans crochet
    ``applicable`` sont exécutés une fois, puis viennent les passages
    applicables et le contrôle final par gravité et victoire. Un état déjà fini
    à l'entrée lève ``ValueError("partie finie")``. Si le début de tour produit
    une victoire, l'état fini est renvoyé sans placement ni ajout du coup, et
    sans modifier ``tour`` ou ``joueur``.
    """
    if etat["fini"]:
        raise ValueError("partie finie")

    etat_courant = copier_etat(etat)
    for regle in regles:
        crochet = _obtenir_crochet(regle, "debut_tour")
        if crochet is not None:
            etat_courant = _appliquer_crochet(etat_courant, crochet)

    etat_courant = gravite(etat_courant)
    etat_courant, termine = _marquer_fin_si_necessaire(etat_courant, regles)
    if termine:
        return etat_courant

    limite = etat_courant["lignes"] * etat_courant["colonnes"]
    etat_courant, _ = _boucle_applicables(
        etat_courant, coup, regles, limite, arreter_a_victoire=True
    )
    if etat_courant["fini"]:
        return etat_courant

    for regle in regles:
        crochet = _obtenir_crochet(regle, "avant_coup")
        if crochet is not None:
            autorise = crochet(copier_etat(etat_courant), coup)
            if not isinstance(autorise, bool):
                raise TypeError("un crochet avant_coup doit renvoyer un booléen")
            if not autorise:
                raise ValueError("coup interdit")

    if isinstance(coup, bool):
        raise ValueError("coup illegal")
    if isinstance(coup, int):
        etat_courant = _poser_jeton(etat_courant, coup)
    else:
        placement_gere = False
        for regle in regles:
            crochet = _obtenir_crochet(regle, "placement")
            if crochet is None:
                continue
            resultat = crochet(copier_etat(etat_courant), coup)
            if resultat is not None:
                if not isinstance(resultat, dict):
                    raise TypeError("un crochet placement doit renvoyer un état ou None")
                etat_courant = copier_etat(resultat)
                placement_gere = True
                break
        if not placement_gere:
            raise ValueError("coup illegal")

    for regle in regles:
        if _obtenir_crochet(regle, "applicable") is None:
            crochet = _obtenir_crochet(regle, "apres_coup")
            if crochet is not None:
                etat_courant = _appliquer_crochet(
                    etat_courant, crochet, coup
                )

    etat_courant, _ = _boucle_applicables(
        etat_courant, coup, regles, limite, arreter_a_victoire=True
    )
    etat_courant = gravite(etat_courant)
    joueur = etat["joueur"]
    etat_courant["coups"] = copier_etat(etat["coups"]) + [coup]
    etat_courant["tour"] += 1
    etat_courant["joueur"] = "O" if joueur == "X" else "X"
    etat_courant["fini"] = _resultat_victoire(etat_courant, regles) is not None
    return etat_courant


def rejouer_avec_regles(coups, regles):
    """Rejoue une partie depuis la position initiale avec les crochets fournis."""
    etat = nouvelle_partie()
    for coup in coups:
        etat = jouer_avec_regles(etat, coup, regles)
    return etat


REGLES = []
