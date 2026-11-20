"""Interface de jeu au clavier pour le Puissance 4 avec règles maison."""

import ast
import random

import moteur
import regles


def lire_coups(texte):
    try:
        coups = ast.literal_eval(texte)
    except (SyntaxError, ValueError, TypeError) as erreur:
        raise ValueError("Saisie illisible : entrez une liste Python de coups.") from erreur

    if not isinstance(coups, list):
        raise ValueError("Les coups doivent être présentés sous forme de liste.")

    for numero, coup in enumerate(coups, start=1):
        if isinstance(coup, int) and not isinstance(coup, bool):
            continue
        if (
            isinstance(coup, tuple)
            and len(coup) == 2
            and coup[0] == "K"
            and isinstance(coup[1], int)
            and not isinstance(coup[1], bool)
        ):
            continue
        if (
            isinstance(coup, tuple)
            and len(coup) == 3
            and coup[0] == "F"
            and all(
                isinstance(valeur, int) and not isinstance(valeur, bool)
                for valeur in coup[1:]
            )
        ):
            continue
        raise ValueError(f"Coup {numero} invalide : {coup!r}.")

    return coups


def formater_coups(coups):
    return repr(list(coups))


def afficher_historique(etat, sortie=print):
    coups = etat["coups"]
    sortie(f"Coups joués ({len(coups)}) :")
    sortie(formater_coups(coups))
    for index, coup in enumerate(coups):
        joueur = "X" if index % 2 == 0 else "O"
        sortie(f"{index + 1}. {joueur} : {coup!r}")


def coup_hasard(etat, rng, speciaux=False, proba_special=0.2):
    possibles = moteur.coups_possibles(etat)
    if not speciaux or rng.random() < 1 - proba_special:
        return rng.choice(possibles)

    reserves = etat.get("reserves", {}).get(
        etat["joueur"], {"fixes": 3, "kamikaze": 1}
    )
    types_disponibles = []
    if reserves.get("kamikaze", 0) > 0:
        types_disponibles.append("K")
    if reserves.get("fixes", 0) > 0:
        types_disponibles.append("F")
    if not types_disponibles:
        return rng.choice(possibles)

    type_special = (
        rng.choice(types_disponibles)
        if len(types_disponibles) > 1
        else types_disponibles[0]
    )
    if type_special == "K":
        return ("K", rng.choice(possibles))

    cases_vides = [
        (ligne, colonne)
        for ligne in range(etat["lignes"])
        for colonne in range(etat["colonnes"])
        if etat["grille"][etat["lignes"] - 1 - ligne][colonne] is None
    ]
    return ("F", *rng.choice(cases_vides))


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
        if commande == "H":
            afficher_historique(etat, sortie)
            continue

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


def _afficher_resume_rejeu(etat, regles_actives, sortie):
    _afficher_compteurs(etat, sortie)
    resultat = (
        moteur.gagnant(etat)
        if regles_actives is None
        else regles._resultat_victoire(etat, regles_actives)
    )
    sortie(f"Tour : {etat['tour']}")
    sortie(f"Joueur : {etat['joueur']}")
    sortie(f"Résultat : {resultat if resultat is not None else 'en cours'}")


def _afficher_coup_refuse(numero, coup, etat, erreur, regles_actives, sortie):
    sortie(f"Le coup {numero} ({coup!r}) refusé : {erreur}")
    sortie("État avant le coup refusé :")
    afficher_grille(etat, sortie)
    _afficher_resume_rejeu(etat, regles_actives, sortie)


def _trouver_coup_refuse(coups, regles_actives, sortie):
    etat = moteur.nouvelle_partie()
    for numero, coup in enumerate(coups, start=1):
        etat_avant = etat
        try:
            etat = _appliquer_coup(etat, coup, regles_actives)
        except ValueError as erreur:
            _afficher_coup_refuse(
                numero, coup, etat_avant, erreur, regles_actives, sortie
            )
            return etat_avant
    raise RuntimeError("Le rejeu a échoué, mais aucun coup refusé n'a été trouvé.")


def rejouer_depuis_texte(
    texte, regles_actives=regles.REGLES, pas_a_pas=False, sortie=print
):
    coups = lire_coups(texte)
    try:
        etat_final = (
            moteur.rejouer(coups)
            if regles_actives is None
            else regles.rejouer_avec_regles(coups, regles_actives)
        )
    except ValueError:
        return _trouver_coup_refuse(coups, regles_actives, sortie)

    if pas_a_pas:
        etat = moteur.nouvelle_partie()
        for numero, coup in enumerate(coups, start=1):
            etat_avant = etat
            try:
                etat = _appliquer_coup(etat, coup, regles_actives)
            except ValueError as erreur:
                _afficher_coup_refuse(
                    numero, coup, etat_avant, erreur, regles_actives, sortie
                )
                return etat_avant
            sortie(f"Après le coup {numero} ({coup!r}) :")
            afficher_grille(etat, sortie)
            afficher_regles_declenchees(
                etat_avant, etat, coup, regles_actives, sortie
            )

        identique = repr(etat) == repr(etat_final)
        sortie("Identique ✓" if identique else "DIFFÉRENT ✗")

    afficher_grille(etat_final, sortie)
    _afficher_resume_rejeu(etat_final, regles_actives, sortie)
    return etat_final


def jouer_partie(
    regles_actives=regles.REGLES,
    lecture=None,
    sortie=print,
    automatiques=(),
    graine=None,
):
    rng = random.Random(graine)
    if automatiques:
        if graine is None:
            graine = rng.getrandbits(64)
            rng = random.Random(graine)
        sortie(f"Graine : {graine}")

    etat = moteur.nouvelle_partie()

    while not etat["fini"]:
        sortie(f"\nTour {etat['tour']} — joueur {etat['joueur']}")
        afficher_grille(etat, sortie)
        _afficher_compteurs(etat, sortie)
        possibles = moteur.coups_possibles(etat)
        if not possibles:
            raise RuntimeError("La partie n'est pas marquée finie malgré l'absence de coups.")

        automatique = etat["joueur"] in automatiques
        if automatique:
            coup = coup_hasard(
                etat, rng, speciaux=regles_actives is not None
            )
            joueur = etat["joueur"]
            if isinstance(coup, tuple) and coup[0] == "K":
                sortie(
                    f"L'ordinateur ({joueur}) joue le Kamikaze "
                    f"en colonne {coup[1]}"
                )
            elif isinstance(coup, tuple) and coup[0] == "F":
                sortie(
                    f"L'ordinateur ({joueur}) pose un jeton fixe "
                    f"ligne {coup[1]} (0 = bas), colonne {coup[2]}"
                )
            else:
                sortie(f"L'ordinateur ({joueur}) joue la colonne {coup}")
        else:
            coup = demander_coup(etat, regles_actives, lecture, sortie)

        etat_avant = etat
        try:
            etat = _appliquer_coup(etat, coup, regles_actives)
        except ValueError as erreur:
            if automatique:
                raise RuntimeError(
                    f"Le coup automatique {coup!r} a été refusé."
                ) from erreur
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
    afficher_historique(etat, sortie)
    return etat


def _demander_graine(lecture, sortie):
    while True:
        texte = lecture("Graine (vide pour aléatoire) : ").strip()
        if not texte:
            return None
        try:
            return int(texte)
        except ValueError:
            sortie("Saisie invalide : entrez un entier ou laissez vide.")


def main(lecture=None, sortie=print):
    if lecture is None:
        lecture = input

    while True:
        sortie("\n1) Deux joueurs")
        sortie("2) Contre l'ordinateur (O automatique)")
        sortie("3) Ordinateur contre ordinateur")
        sortie("4) Rejouer une partie")
        sortie("5) Quitter")
        choix = lecture("Choix : ").strip()

        if choix == "1":
            jouer_partie(lecture=lecture, sortie=sortie)
        elif choix == "2":
            graine = _demander_graine(lecture, sortie)
            jouer_partie(
                lecture=lecture,
                sortie=sortie,
                automatiques=("O",),
                graine=graine,
            )
        elif choix == "3":
            graine = _demander_graine(lecture, sortie)
            jouer_partie(
                lecture=lecture,
                sortie=sortie,
                automatiques=("X", "O"),
                graine=graine,
            )
        elif choix == "4":
            while True:
                texte = lecture("Liste des coups : ")
                try:
                    lire_coups(texte)
                except ValueError as erreur:
                    sortie(str(erreur))
                    continue
                break

            while True:
                choix_regles = lecture(
                    "Règles (1 toutes, 2 standard) : "
                ).strip()
                if choix_regles in ("1", "2"):
                    regles_actives = regles.REGLES if choix_regles == "1" else None
                    break
                sortie("Saisie invalide : choisissez 1 ou 2.")

            while True:
                choix_pas_a_pas = lecture("Pas à pas (o/n) : ").strip().lower()
                if choix_pas_a_pas in ("o", "n"):
                    break
                sortie("Saisie invalide : répondez o ou n.")

            rejouer_depuis_texte(
                texte,
                regles_actives=regles_actives,
                pas_a_pas=choix_pas_a_pas == "o",
                sortie=sortie,
            )
        elif choix == "5":
            return
        else:
            sortie("Saisie invalide : choisissez 1, 2, 3, 4 ou 5.")


if __name__ == "__main__":
    main()
