"""Interface de jeu au clavier pour le Puissance 4 avec règles maison."""

import moteur
import regles


_NOMS_REGLES = {
    "tete_qui_tourne": "Règle 1",
    "tetris": "Règle 2",
    "kamikaze": "Règle 3",
    "collectionneur": "Règle 4",
    "inebranlable": "Règle 5",
}


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


def demander_coup(etat, regles_actives=regles.REGLES, lecture=None, sortie=print):
    if lecture is None:
        lecture = input

    while True:
        possibles = moteur.coups_possibles(etat)
        choix = lecture(
            "Colonne (entier), F (jeton fixe) ou K (Kamikaze) : "
        ).strip()

        if choix.upper() == "F":
            if regles_actives is None:
                sortie("Les coups fixes ne sont pas disponibles en mode standard.")
                continue
            ligne = _lire_entier(
                "Ligne du jeton fixe (0 = bas) : ", lecture, sortie
            )
            colonne = _lire_entier(
                "Colonne du jeton fixe (0 = gauche) : ", lecture, sortie
            )
            return ("F", ligne, colonne)

        if choix.upper() == "K":
            if regles_actives is None:
                sortie("Les coups Kamikaze ne sont pas disponibles en mode standard.")
                continue
            colonne = _lire_entier(
                "Colonne du jeton Kamikaze : ", lecture, sortie
            )
            if colonne not in possibles:
                sortie(
                    f"Coup illégal. Colonnes possibles : "
                    f"{', '.join(map(str, possibles))}."
                )
                continue
            return ("K", colonne)

        try:
            colonne = int(choix)
        except ValueError:
            sortie("Saisie invalide : entrez un entier, F ou K.")
            continue

        if colonne not in possibles:
            sortie(
                f"Coup illégal. Colonnes possibles : "
                f"{', '.join(map(str, possibles))}."
            )
            continue
        return colonne


def _nombre_jetons(etat):
    return sum(
        case is not None
        for ligne in etat["grille"]
        for case in ligne
    )


def _instrumenter_regles(regles_actives, evenements):
    regles_instrumentees = []
    for regle in regles_actives:
        regle_instrumentee = regle.copy()
        nom = regle.get("nom", "")
        etiquette = _NOMS_REGLES.get(nom, f"Règle {nom}")

        for crochet_nom in ("debut_tour", "placement", "apres_coup", "victoire"):
            crochet = regle.get(crochet_nom)
            if crochet is None:
                continue

            def observer(*arguments, crochet=crochet, crochet_nom=crochet_nom,
                         etiquette=etiquette):
                etat_avant = arguments[0]
                resultat = crochet(*arguments)
                if crochet_nom == "debut_tour" and (
                    etat_avant["colonnes"] != resultat["colonnes"]
                    or etat_avant["lignes"] != resultat["lignes"]
                ):
                    evenements.append(
                        f"{etiquette} : le plateau a tourné de 90° "
                        "dans le sens anti-horaire."
                    )
                elif crochet_nom == "placement" and resultat is not None:
                    coup = arguments[1]
                    if coup[0] == "K":
                        joueur = etat_avant["joueur"]
                        detruits_avant = etat_avant.get("detruits", {}).get(joueur, 0)
                        detruits_apres = resultat.get("detruits", {}).get(joueur, 0)
                        nombre = detruits_apres - detruits_avant
                        evenements.append(
                            f"{etiquette} : le Kamikaze a été posé en colonne "
                            f"{coup[1]} et a détruit {nombre} jeton(s)."
                        )
                    else:
                        evenements.append(
                            f"{etiquette} : un jeton fixe a été posé en "
                            f"ligne {coup[1]}, colonne {coup[2]}."
                        )
                elif crochet_nom == "apres_coup":
                    detruits_avant = _nombre_jetons(etat_avant)
                    detruits_apres = _nombre_jetons(resultat)
                    evenements.append(
                        f"{etiquette} : une ou plusieurs lignes complètes "
                        f"ont été supprimées ({detruits_avant - detruits_apres} "
                        "jeton(s) détruit(s))."
                    )
                elif crochet_nom == "victoire" and resultat is not None:
                    evenement = (
                        f"{etiquette} : la condition de victoire est atteinte "
                        f"par {resultat}."
                    )
                    if evenement not in evenements:
                        evenements.append(evenement)
                return resultat

            regle_instrumentee[crochet_nom] = observer
        regles_instrumentees.append(regle_instrumentee)
    return regles_instrumentees


def _afficher_points(etat_avant, etat_apres, sortie):
    detruits_avant = etat_avant.get("detruits", {})
    detruits_apres = etat_apres.get("detruits", {})
    for joueur in ("X", "O"):
        points = detruits_apres.get(joueur, 0) - detruits_avant.get(joueur, 0)
        if points > 0:
            sortie(
                f"Règle 4 : {joueur} gagne {points} point(s) "
                f"({detruits_apres[joueur]} destructions au total)."
            )


def _afficher_reserves(etat, joueur, regles_actives, sortie):
    reserves = etat.get("reserves", {})
    reserve_joueur = reserves.get(joueur, {})
    regles_noms = {regle.get("nom") for regle in (regles_actives or [])}

    elements = []
    if "inebranlable" in regles_noms:
        elements.append(f"fixes : {reserve_joueur.get('fixes', 3)}")
    if "kamikaze" in regles_noms:
        elements.append(f"Kamikaze : {reserve_joueur.get('kamikaze', 1)}")
    if elements:
        sortie("Réserves — " + ", ".join(elements))


def jouer_partie(regles_actives=regles.REGLES, lecture=None, sortie=print):
    etat = moteur.nouvelle_partie()

    while not etat["fini"]:
        sortie(f"\nTour {etat['tour']} — joueur {etat['joueur']}")
        _afficher_reserves(etat, etat["joueur"], regles_actives, sortie)
        afficher_grille(etat, sortie)
        if not moteur.coups_possibles(etat):
            raise RuntimeError(
                "La partie n'est pas marquée finie malgré l'absence de coups."
            )

        while True:
            coup = demander_coup(etat, regles_actives, lecture, sortie)
            try:
                if regles_actives is None:
                    etat_suivant = moteur.jouer(etat, coup)
                else:
                    evenements = []
                    regles_instrumentees = _instrumenter_regles(
                        regles_actives, evenements
                    )
                    etat_suivant = regles.jouer_avec_regles(
                        etat, coup, regles_instrumentees
                    )
            except ValueError as erreur:
                sortie(f"Coup refusé : {erreur}. Réessayez.")
                continue
            break

        if regles_actives is not None:
            for evenement in evenements:
                sortie(evenement)
            _afficher_points(etat, etat_suivant, sortie)
        etat = etat_suivant

    afficher_grille(etat, sortie)
    resultat = (
        moteur.gagnant(etat)
        if regles_actives is None
        else regles._resultat_victoire(etat, regles_actives)
    )
    if resultat not in ("X", "O", "nul"):
        raise RuntimeError(
            f"La partie est finie avec un résultat inattendu : {resultat!r}."
        )
    sortie(f"Fin de partie : {resultat}")
    return etat


def main():
    jouer_partie()


if __name__ == "__main__":
    main()
