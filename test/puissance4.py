"""Puissance 4 classique avec interface graphique pygame.

Lancer avec : python puissance4.py
La bibliothèque pygame doit être installée pour afficher la fenêtre.
"""

from __future__ import annotations

from typing import Optional


NB_LIGNES = 6
NB_COLONNES = 7
JOUEURS = ("X", "O")

LARGEUR_CASE = 90
MARGE = 35
HAUTEUR_ENTETE = 120
LARGEUR_FENETRE = NB_COLONNES * LARGEUR_CASE + 2 * MARGE
HAUTEUR_FENETRE = HAUTEUR_ENTETE + NB_LIGNES * LARGEUR_CASE + 70

COULEUR_FOND = (246, 244, 237)
COULEUR_GRILLE = (30, 101, 156)
COULEUR_CASE_VIDE = (230, 233, 232)
COULEUR_X = (224, 76, 62)
COULEUR_O = (245, 196, 66)
COULEUR_TEXTE = (34, 43, 48)
COULEUR_MESSAGE = (82, 91, 94)


def creer_grille() -> list[list[Optional[str]]]:
    """Crée une grille vide de six lignes et sept colonnes."""
    return [[None for _ in range(NB_COLONNES)] for _ in range(NB_LIGNES)]


def afficher_grille(grille: list[list[Optional[str]]]) -> None:
    """Affiche la grille dans le terminal, avec les colonnes numérotées."""
    print("\n" + "\n".join(
        "| " + " | ".join(case or " " for case in ligne) + " |"
        for ligne in grille
    ))
    print("  " + "   ".join(str(numero) for numero in range(1, NB_COLONNES + 1)))


def coup_valide(grille: list[list[Optional[str]]], colonne: int) -> bool:
    """Indique si la colonne (indexée de 0 à 6) existe et n'est pas pleine."""
    return 0 <= colonne < NB_COLONNES and grille[0][colonne] is None


def jouer_coup(
    grille: list[list[Optional[str]]], colonne: int, joueur: str
) -> Optional[int]:
    """Dépose un pion dans la colonne et renvoie sa ligne, ou None si invalide."""
    if not coup_valide(grille, colonne):
        return None

    for ligne in range(NB_LIGNES - 1, -1, -1):
        if grille[ligne][colonne] is None:
            grille[ligne][colonne] = joueur
            return ligne
    return None


def verifier_victoire(
    grille: list[list[Optional[str]]],
    ligne: int,
    colonne: int,
    joueur: str,
) -> bool:
    """Vérifie si le dernier pion posé forme un alignement de quatre."""
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))

    for delta_ligne, delta_colonne in directions:
        alignement = 1
        for sens in (-1, 1):
            ligne_courante = ligne + sens * delta_ligne
            colonne_courante = colonne + sens * delta_colonne
            while (
                0 <= ligne_courante < NB_LIGNES
                and 0 <= colonne_courante < NB_COLONNES
                and grille[ligne_courante][colonne_courante] == joueur
            ):
                alignement += 1
                ligne_courante += sens * delta_ligne
                colonne_courante += sens * delta_colonne
        if alignement >= 4:
            return True
    return False


def grille_pleine(grille: list[list[Optional[str]]]) -> bool:
    """Indique si aucune colonne ne peut recevoir de pion."""
    return all(grille[0][colonne] is not None for colonne in range(NB_COLONNES))


def afficher_grille_pygame(pygame: object, ecran: object, grille: list[list[Optional[str]]]) -> None:
    """Dessine la grille et ses pions dans la fenêtre pygame."""
    ecran.fill(COULEUR_FOND)
    pygame.draw.rect(
        ecran,
        COULEUR_GRILLE,
        (MARGE, HAUTEUR_ENTETE, NB_COLONNES * LARGEUR_CASE, NB_LIGNES * LARGEUR_CASE),
    )

    for ligne in range(NB_LIGNES):
        for colonne in range(NB_COLONNES):
            centre = (
                MARGE + colonne * LARGEUR_CASE + LARGEUR_CASE // 2,
                HAUTEUR_ENTETE + ligne * LARGEUR_CASE + LARGEUR_CASE // 2,
            )
            pion = grille[ligne][colonne]
            couleur = COULEUR_X if pion == "X" else COULEUR_O if pion == "O" else COULEUR_CASE_VIDE
            pygame.draw.circle(ecran, couleur, centre, LARGEUR_CASE // 2 - 9)


def traiter_coup(
    grille: list[list[Optional[str]]],
    colonne: int,
    joueur: str,
) -> tuple[bool, str]:
    """Joue un coup valide et renvoie son résultat ainsi que le message associé."""
    if not 0 <= colonne < NB_COLONNES:
        return False, "Colonne hors limites : choisissez un numéro de 1 à 7."
    if not coup_valide(grille, colonne):
        return False, f"La colonne {colonne + 1} est pleine. Choisissez-en une autre."

    ligne = jouer_coup(grille, colonne, joueur)
    afficher_grille(grille)

    if ligne is not None and verifier_victoire(grille, ligne, colonne, joueur):
        return True, f"Le joueur {joueur} a gagné !  R : rejouer    Q : quitter"
    if grille_pleine(grille):
        return True, "Match nul !  R : rejouer    Q : quitter"
    return False, f"Au tour du joueur {JOUEURS[(JOUEURS.index(joueur) + 1) % 2]}"


def main() -> None:
    """Lance les parties pygame et gère les entrées des joueurs."""
    try:
        import pygame
    except ModuleNotFoundError as erreur:
        raise SystemExit(
            "pygame n'est pas installé. Installez-le avec : python -m pip install pygame"
        ) from erreur

    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    pygame.display.set_caption("Puissance 4")
    horloge = pygame.time.Clock()
    police = pygame.font.Font(None, 34)
    petite_police = pygame.font.Font(None, 27)

    grille = creer_grille()
    joueur = JOUEURS[0]
    partie_terminee = False
    message = f"Au tour du joueur {joueur}"
    afficher_grille(grille)
    en_cours = True

    while en_cours:
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_q:
                    en_cours = False
                elif partie_terminee and evenement.key == pygame.K_r:
                    grille = creer_grille()
                    joueur = JOUEURS[0]
                    partie_terminee = False
                    message = f"Au tour du joueur {joueur}"
                    afficher_grille(grille)
                elif not partie_terminee:
                    if evenement.unicode in "1234567890":
                        colonne = int(evenement.unicode) - 1
                        partie_terminee, message = traiter_coup(
                            grille, colonne, joueur
                        )
                        if not partie_terminee and message.startswith("Au tour"):
                            joueur = JOUEURS[(JOUEURS.index(joueur) + 1) % 2]
                    else:
                        message = "Entrée invalide : utilisez les touches 1 à 7."
            elif evenement.type == pygame.MOUSEBUTTONDOWN and not partie_terminee:
                x, y = evenement.pos
                if (
                    MARGE <= x < MARGE + NB_COLONNES * LARGEUR_CASE
                    and HAUTEUR_ENTETE <= y < HAUTEUR_ENTETE + NB_LIGNES * LARGEUR_CASE
                ):
                    colonne = (x - MARGE) // LARGEUR_CASE
                    partie_terminee, message = traiter_coup(
                        grille, colonne, joueur
                    )
                    if not partie_terminee and message.startswith("Au tour"):
                        joueur = JOUEURS[(JOUEURS.index(joueur) + 1) % 2]

        afficher_grille_pygame(pygame, ecran, grille)
        texte = police.render(message, True, COULEUR_TEXTE)
        ecran.blit(texte, (MARGE, 35))
        aide = petite_police.render(
            "Cliquez sur une colonne ou utilisez les touches 1 à 7",
            True,
            COULEUR_MESSAGE,
        )
        ecran.blit(aide, (MARGE, 78))
        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()