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


def _boucle_applicables(
    etat, coup, regles, limite, arreter_a_victoire, points_destruction=True
):
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
                avait_detruits = "detruits" in etat
                detruits_precedents = copier_etat(etat.get("detruits"))
                etat = _appliquer_crochet(etat, crochet_apres, coup)
                if not points_destruction:
                    if avait_detruits:
                        etat["detruits"] = detruits_precedents
                    else:
                        etat.pop("detruits", None)

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

    Après le placement, la gravité et la victoire sont vérifiées avant les
    règles applicables. Si la partie continue, le coup, le tour et le joueur
    sont mis à jour, puis les ``debut_tour`` du tour suivant sont appliqués
    avant gravité, victoire et les règles applicables. Une ligne détruite après
    une rotation ne rapporte pas de points de destruction. Un état déjà fini à
    l'entrée lève ``ValueError("partie finie")``.
    """
    if etat["fini"]:
        raise ValueError("partie finie")

    etat_courant = copier_etat(etat)
    limite = etat_courant["lignes"] * etat_courant["colonnes"]

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

    etat_courant = gravite(etat_courant)
    etat_courant, victoire_apres_coup = _marquer_fin_si_necessaire(
        etat_courant, regles
    )
    if not victoire_apres_coup:
        etat_courant, _ = _boucle_applicables(
            etat_courant, coup, regles, limite, arreter_a_victoire=True
        )
    etat_courant = gravite(etat_courant)
    joueur = etat["joueur"]
    etat_courant["coups"] = copier_etat(etat["coups"]) + [coup]
    etat_courant["tour"] += 1
    etat_courant["joueur"] = "O" if joueur == "X" else "X"
    etat_courant["fini"] = _resultat_victoire(etat_courant, regles) is not None

    if etat_courant["fini"]:
        return etat_courant

    rotation_effectuee = False
    for regle in regles:
        crochet = _obtenir_crochet(regle, "debut_tour")
        if crochet is not None:
            etat_precedent = etat_courant
            etat_courant = _appliquer_crochet(etat_courant, crochet)
            if (
                regle.get("nom") == "tete_qui_tourne"
                and etat_courant != etat_precedent
            ):
                rotation_effectuee = True

    etat_courant = gravite(etat_courant)
    etat_courant, termine = _marquer_fin_si_necessaire(etat_courant, regles)
    if termine:
        return etat_courant

    etat_courant, _ = _boucle_applicables(
        etat_courant,
        coup,
        regles,
        limite,
        arreter_a_victoire=True,
        points_destruction=not rotation_effectuee,
    )
    return etat_courant


def rejouer_avec_regles(coups, regles):
    """Rejoue une partie depuis la position initiale avec les crochets fournis."""
    etat = nouvelle_partie()
    for coup in coups:
        etat = jouer_avec_regles(etat, coup, regles)
    return etat


def _tete_qui_tourne(etat):
    if etat["tour"] == 1 or etat["tour"] % 4 != 1:
        return copier_etat(etat)

    nouvel_etat = copier_etat(etat)
    ancienne_grille = nouvel_etat["grille"]
    nouvel_etat["grille"] = [list(ligne) for ligne in zip(*ancienne_grille)][::-1]
    nouvel_etat["colonnes"], nouvel_etat["lignes"] = (
        nouvel_etat["lignes"],
        nouvel_etat["colonnes"],
    )
    return nouvel_etat


def _lignes_pleines(etat):
    return [
        index
        for index, ligne in enumerate(etat["grille"])
        if all(case is not None for case in ligne)
    ]


def _tetris_applicable(etat):
    return bool(_lignes_pleines(etat))


def _tetris_apres_coup(etat, coup):
    nouvel_etat = copier_etat(etat)
    lignes_pleines = _lignes_pleines(nouvel_etat)
    detruits = nouvel_etat.setdefault("detruits", {"X": 0, "O": 0})
    joueur = nouvel_etat["joueur"]

    for index in lignes_pleines:
        for jeton in nouvel_etat["grille"][index]:
            detruits[joueur] += 1
            if jeton in ("FX", "FO"):
                proprietaire = jeton[1]
                if "reserves" in nouvel_etat:
                    nouvel_etat["reserves"][proprietaire]["fixes"] += 1
        nouvel_etat["grille"][index] = [None] * nouvel_etat["colonnes"]

    return nouvel_etat


REGLE_1 = {"nom": "tete_qui_tourne", "debut_tour": _tete_qui_tourne}
REGLE_2 = {
    "nom": "tetris",
    "applicable": _tetris_applicable,
    "apres_coup": _tetris_apres_coup,
}
REGLES = [REGLE_1, REGLE_2]
