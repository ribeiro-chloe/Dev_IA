"""Interface de jeu au clavier pour le Puissance 4 avec règles maison."""

import moteur
import regles


def afficher_grille(etat, sortie=print):
    colonnes = etat["colonnes"]
    sortie("      " + "   ".join(f"{colonne:^3}" for colonne in range(colonnes)))
    sortie("    +" + "+".join("---" for _ in range(colonnes)) + "+")
    for index, ligne in enumerate(etat["grille"]):
        cases = ("." if case is None else str(case) for case in ligne)
        sortie(f"{index:>3} | " + " | ".join(f"{case:^3}" for case in cases) + " |")
        sortie("    +" + "+".join("---" for _ in range(colonnes)) + "+")


def _lire_entier(prompt, lecture, sortie):
    while True:
        texte = lecture(prompt).strip()
        try:
            return int(texte)
        except ValueError:
            sortie("Saisie invalide : entrez un entier.")


def demander_coup(etat, regles_actives, lecture=None, sortie=print):
    if lecture is None:
        lecture = input

    while True:
        possibles = moteur.coups_possibles(etat)
        texte = lecture(
            "Choisissez une colonne, F (jeton fixe) ou K (Kamikaze) "
            f"({', '.join(map(str, possibles))}) : "
        ).strip()

        commande = texte.upper()
        if commande == "F" and regles_actives is not None:
            ligne = _lire_entier("Ligne du jeton fixe (0 = bas) : ", lecture, sortie)
            colonne = _lire_entier("Colonne du jeton fixe : ", lecture, sortie)
            coup = ("F", ligne, colonne)
        elif commande == "K" and regles_actives is not None:
            colonne = _lire_entier("Colonne du Kamikaze : ", lecture, sortie)
            coup = ("K", colonne)
        else:
            try:
                colonne = int(texte)
            except ValueError:
                sortie("Saisie invalide : entrez un entier, F ou K.")
                continue
            coup = colonne

        if isinstance(coup, int) or (
            isinstance(coup, tuple) and coup[0] == "K"
        ):
            if colonne not in possibles:
                sortie(
                    f"Coup illégal. Colonnes possibles : "
                    f"{', '.join(map(str, possibles))}."
                )
                continue

        return coup


def _reserves(etat, joueur):
    reserves = etat.get("reserves", {}).get(joueur, {})
    return reserves.get("fixes", 3), reserves.get("kamikaze", 1)


def _afficher_compteurs(etat, sortie=print):
    fixes, kamikazes = _reserves(etat, etat["joueur"])
    sortie(
        f"Réserves de {etat['joueur']} : {fixes} jeton(s) fixe(s), "
        f"{kamikazes} Kamikaze(s)."
    )
    detruits = etat.get("detruits", {})
    sortie(
        "Jetons détruits : "
        f"X {detruits.get('X', 0)} — O {detruits.get('O', 0)}"
    )


def _regle_active(regles_actives, nom):
    return regles_actives is not None and any(
        regle.get("nom") == nom for regle in regles_actives
    )


def _nombre_jetons(etat):
    return sum(
        case is not None
        for ligne in etat["grille"]
        for case in ligne
    )


def afficher_regles_declenchees(
    etat_avant, etat_apres, coup, regles_actives, sortie=print
):
    if (
        _regle_active(regles_actives, "tete_qui_tourne")
        and (
            etat_avant["colonnes"] != etat_apres["colonnes"]
            or etat_avant["lignes"] != etat_apres["lignes"]
        )
    ):
        sortie(
            "Règle 1 : le plateau a tourné de 90° dans le sens anti-horaire "
            "et la gravité a été appliquée."
        )

    destructions = (
        _nombre_jetons(etat_avant) + 1 - _nombre_jetons(etat_apres)
    )
    if (
        _regle_active(regles_actives, "tetris")
        and destructions > 0
        and not (isinstance(coup, tuple) and coup[0] == "K")
    ):
        sortie(
            "Règle 2 : les lignes complètes ont été supprimées "
            f"({destructions} jeton(s) détruit(s))."
        )

    if _regle_active(regles_actives, "kamikaze") and (
        isinstance(coup, tuple) and coup[0] == "K"
    ):
        sortie(
            f"Règle 3 : le Kamikaze a explosé dans la colonne {coup[1]} "
            f"({max(destructions, 0)} jeton(s) détruit(s))."
        )

    if _regle_active(regles_actives, "inebranlable") and (
        isinstance(coup, tuple) and coup[0] == "F"
    ):
        sortie(
            f"Règle 5 : un jeton fixe a été posé en ligne {coup[1]}, "
            f"colonne {coup[2]}."
        )

    detruits_avant = etat_avant.get("detruits", {})
    detruits_apres = etat_apres.get("detruits", {})
    joueur = etat_avant["joueur"]
    points = detruits_apres.get(joueur, 0) - detruits_avant.get(joueur, 0)
    if _regle_active(regles_actives, "collectionneur") and points > 0:
        sortie(
            f"Règle 4 : {joueur} gagne {points} point(s) "
            f"({detruits_apres[joueur]} destructions au total)."
        )


def _appliquer_coup(etat, coup, regles_actives):
    if regles_actives is None:
        return moteur.jouer(etat, coup)
    return regles.jouer_avec_regles(etat, coup, regles_actives)


def jouer_partie(regles_actives=regles.REGLES, lecture=None, sortie=print):
    etat = moteur.nouvelle_partie()

    while not etat["fini"]:
        sortie(f"\nTour {etat['tour']} — joueur {etat['joueur']}")
        afficher_grille(etat, sortie)
        _afficher_compteurs(etat, sortie)
        possibles = moteur.coups_possibles(etat)
        if not possibles:
            raise RuntimeError("La partie n'est pas marquée finie malgré l'absence de coups.")

        coup = demander_coup(etat, regles_actives, lecture, sortie)
        etat_avant = etat
        try:
            etat = _appliquer_coup(etat, coup, regles_actives)
        except ValueError:
            sortie("Coup illégal ou jeton spécial indisponible. Réessayez.")
            continue

        afficher_regles_declenchees(
            etat_avant, etat, coup, regles_actives, sortie
        )
        _afficher_compteurs(etat, sortie)

    afficher_grille(etat, sortie)
    _afficher_compteurs(etat, sortie)
    resultat = (
        moteur.gagnant(etat)
        if regles_actives is None
        else regles._resultat_victoire(etat, regles_actives)
    )
    if resultat not in ("X", "O", "nul"):
        raise RuntimeError(f"La partie est finie avec un résultat inattendu : {resultat!r}.")
    sortie(f"Fin de partie : {resultat}")
    return etat


def main():
    jouer_partie()


if __name__ == "__main__":
    main()
