##
# @file simulation_trafic_v1.py
# @brief Simulation 2D de trafic routier avec voitures, feux, obstacles, piétons et zones non routières, utilisant Pygame.
# @details Ce script met en place une grille représentant un réseau routier avec des zones définies
#          comme non praticables (bâtiments, ...). Les routes sont des cellules spécifiques.
#          Les voitures se déplacent sur les routes vers des destinations, en suivant les sens de circulation,
#          en respectant feux, piétons sur passages dédiés, et obstacles.
#          Les utilisateurs peuvent ajouter/retirer des obstacles sur les routes via clic souris.
#          La programmation des voitures inclut désormais des mécanismes renforcés pour éviter les blocages permanents.
# @author Sokhna Oumou DIOUF
# @author Rym BENOUMECHIARA
# @date 2025-04-07

import pygame
import sys
import time
import random
import heapq
from typing import List, Dict, Tuple, Any, Set, Union

# Initialisation de Pygame
pygame.init()

# --- CONSTANTES DE CONFIGURATION ---

## @brief Largeur de la fenêtre de simulation en pixels.
LARGEUR = 1200
## @brief Hauteur de la fenêtre de simulation en pixels.
HAUTEUR = 600
## @brief Taille de chaque cellule carrée de la grille en pixels.
TAILLE_CELLULE = 40

# Dérivation de la taille de la grille en cellules
## @brief Nombre de colonnes (largeur) de la grille en cellules.
TAILLE_X_GRILLE = LARGEUR // TAILLE_CELLULE
## @brief Nombre de lignes (hauteur) de la grille en cellules.
TAILLE_Y_GRILLE = HAUTEUR // TAILLE_CELLULE

# --- COULEURS ---

## @brief Couleur blanche (RVB).
BLANC = (255, 255, 255)
## @brief Couleur noire (RVB).
NOIR = (0, 0, 0)

# Couleurs des feux
## @brief Couleur verte (RVB), utilisée pour les feux verts.
VERT = (0, 255, 0)
## @brief Couleur orange (RVB), utilisée pour les feux oranges.
ORANGE = (255, 165, 0)
## @brief Couleur rouge (RVB), utilisée pour les feux rouges.
ROUGE = (255, 0, 0)
## @brief Couleur gris foncé (RVB), utilisée pour les cercles inactifs des feux.
GRIS_FONCE = (80, 80, 80)

# Couleurs de la grille et éléments
## @brief Couleur gris clair (RVB), utilisée pour les zones non routières.
GRIS_CLAIR = (200, 200, 200)
## @brief Couleur gris moyen (RVB), utilisée pour le fond des routes.
GRIS_ROUTE = (55, 55, 55)

## @brief Couleur jaune/dorée (RVB), utilisée pour dessiner les places de parking (destinations).
JAUNE_PARKING = (255, 190, 0)
## @brief Couleur gris clair (RVB) utilisée pour dessiner les zébrures des passages piétons.
COULEUR_PASSAGE = (220, 220, 220)
## @brief Couleur noire (RVB) utilisée pour dessiner les piétons (bonshommes allumettes).
COULEUR_PIETON = (0, 0, 0)

# Couleurs pour les éléments décoratifs
## @brief Couleur marron pour le tronc des arbres (RVB).
MARRON_TRONC = (139, 69, 19)
## @brief Couleur verte foncée pour le feuillage des arbres (RVB).
VERT_FEUILLAGE = (34, 139, 34)
## @brief Couleur marron clair pour les murs des maisons (RVB).
BRUN_MUR = (205, 133, 63) # Saddle Brown clair
## @brief Couleur rouge foncé pour les toits des maisons (RVB).
ROUGE_TOIT = (139, 0, 0) # Dark Red
## @brief Couleurs pour dessiner l'école (Murs: Cornsilk, Toit: Dark Red, Porte: Sienne, Fenêtre: Bleu ciel).
COULEUR_ECOLE_MUR = (255, 250, 205)
COULEUR_ECOLE_TOIT = (139, 0, 0)
COULEUR_ECOLE_PORTE = (160, 82, 45)
COULEUR_ECOLE_FENETRE = (135, 206, 235)
## @brief Couleurs pour dessiner les massifs montagneux (Eau: Bleu vif, Roc: Brun/Gris rocheux, Neige: Blanc/Bleuâtre).
COULEUR_EAU = (0, 150, 255)
COULEUR_MONTAGNE_ROCHE = (120, 100, 90)
COULEUR_MONTAGNE_NEIGE = (230, 240, 250)
## @brief NOUVEAU: Couleurs pour dessiner des fleurs roses (Pétales: Rose vif, Tige/Feuilles: Vert foncé).
COULEUR_FLEUR_ROSE = (255, 105, 180)
COULEUR_FLEUR_VERT = (0, 100, 0)

# --- SYMBOLES DE LA GRILLE ---

## @brief Symbole représentant une zone non routière (bâtiment, parc, etc.) dans la grille.
NON_ROUTIER = "N"
## @brief Symbole représentant une route praticable dans la grille.
ROUTE = " "
## @brief Symbole représentant un obstacle MANUEL ('X') sur une route.
OBSTACLE_MANUEL = "X"
## @brief NOUVEAU : Symbole représentant un obstacle AUTOMATIQUE ('A') sur une route.
OBSTACLE_AUTO_SYM = "A"

## @brief Ensemble de tous les symboles représentant des cellules non praticables (pour le pathfinding, etc.).
SYMBOLES_NON_PRATICABLES = {NON_ROUTIER, OBSTACLE_MANUEL, OBSTACLE_AUTO_SYM}

# --- POSITIONS D'ÉLÉMENTS FIXES (DÉCORATIONS) ---
# Assurez-vous que ces positions correspondent à des cases NON_ROUTIER dans le réseau routier défini.
## @brief Positions (x, y) où dessiner les arbres.
POSITIONS_ARBRES = [(1, 1), (10, 2), (20, 4), (5, 2), (7, 10), (13, 7)]
## @brief Positions (x, y) où dessiner les écoles.
POSITIONS_ECOLES = [(23, 13), (10, 4), (19, 13), (5, 13), (28, 2)]
## @brief Positions (x, y) où dessiner les maisons.
POSITIONS_MAISONS = [(29, 1), (25, 4), (20, 10), (17, 2), (22, 7), (28, 8)]
## @brief Positions (x, y) où dessiner la base d'eau/montagne. Ces positions définissent la limite basse du massif.
POSITIONS_MASSIF_BASE_EAU = [(4, 11), (1, 8), (7, 2), (16, 8), (22, 2), (25, 14)]
## @brief Positions (x, y) où dessiner des fleurs.
POSITIONS_FLEURS = [(7, 7), (1, 4), (2, 1), (4, 5), (5, 11), (8, 1), (10, 5), (13, 8), (16, 13), (20, 2), (25, 5), (28, 1)]

# --- PARAMÈTRES DE SIMULATION ---

## @brief Vitesse de base des voitures (pas par seconde).
VITESSE_VOITURE = 1.5
## @brief Délai minimum en secondes entre deux déplacements d'une voiture (1 / VITESSE_VOITURE).
DELAI_MIN_MOUVEMENT = 1.0 / VITESSE_VOITURE

## @brief Délai en secondes après lequel une voiture est considérée comme potentiellement bloquée pour un simple recalcul de chemin.
SEUIL_BLOCAGE = 1.0 # 1 seconde
## @brief Nombre maximum d'échecs de recalcul simple (vers la même destination) avant qu'une voiture n'essaie de trouver une nouvelle destination.
MAX_RECALCUL_ECHECS = 6
## @brief Temps en secondes après lequel une voiture est considérée comme durablement bloquée et recherche une *nouvelle* destination. Utilisé pour l'ancien mécanisme principal, maintenant complété par recalcul_echecs.
SEUIL_BLOCAGE_PERMANENT = 10.0 # Un seuil plus élevé si nécessaire comme backup

## @brief Délai en secondes après qu'une voiture atteint sa destination avant de disparaître.
DELAI_DISPARITION_APRES_ARRIVEE = 1.0
## @brief Nombre cible de voitures actives à maintenir dans la simulation (en route ou en phase de disparition post-arrivée).
NOMBRE_VOITURES_CIBLE = 50

## @brief Nombre de passages piétons à générer initialement sur la grille.
NB_PASSAGES_PIETONS = 10 # Sur des routes uniquement.
## @brief Vitesse de traversée des piétons (fraction de la cellule par tick). Une valeur basse signifie une traversée lente.
VITESSE_PIETON = 0.02
## @brief Probabilité (par tick et par passage piéton libre) qu'un nouveau piéton apparaisse.
PROBA_APPARITION_PIETON = 0.005

## @brief Intervalle de temps en secondes pour tenter d'ajouter ou de retirer un obstacle automatique.
OBSTACLE_AUTOMATIQUE_INTERVAL = 0.5 # 0.5 secondes

# --- VARIABLES GLOBALES DE SIMULATION (ÉTAT) ---

## @brief Surface principale de dessin (la fenêtre Pygame).
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Simulation de Trafic Urbain v1")
## @brief Horloge Pygame pour contrôler la vitesse de la simulation (framerate).
clock = pygame.time.Clock()

##
# @var grille
# @brief La grille 2D représentant le réseau routier et les zones non routières.
# Chaque cellule contient un symbole : 'N', ' ', 'X', ou 'A'.
grille: List[List[str]] = []

##
# @var lignes_directions
# @brief Dictionnaire associant un indice de ligne à son sens de circulation ('droite' ou 'gauche').
lignes_directions: Dict[int, str] = {}
##
# @var colonnes_directions
# @brief Dictionnaire associant un indice de colonne à son sens de circulation ('haut' ou 'bas').
colonnes_directions: Dict[int, str] = {}

##
# @var feux
# @brief Liste des feux de circulation. Chaque feu est un dict.
feux: List[Dict[str, Any]] = []
##
# @var passages_pietons
# @brief Liste des passages piétons sur la grille. Chaque passage est un dict.
passages_pietons: List[Dict[str, Any]] = []
##
# @var pietons_actifs
# @brief Liste des piétons actuellement en cours de traversée. Chaque piéton est un dict.
pietons_actifs: List[Dict[str, Any]] = []
## @brief Compteur pour attribuer un ID unique croissant à chaque nouveau piéton.
prochain_id_pieton = 0

##
# @var voitures
# @brief Liste des voitures actives dans la simulation. Chaque voiture est un dict.
voitures: List[Dict[str, Any]] = []
## @brief Compteur pour attribuer un ID unique croissant à chaque nouvelle voiture (initiale ou régénérée).
prochain_id_voiture = 1

##
# @var image_voiture_echelle
# @brief Image de base de la voiture, redimensionnée et prête à être colorée. `None` si échec de chargement.
image_voiture_echelle: Union[pygame.Surface, None] = None

## @brief Minuteur pour déclencher l'ajout/retrait d'obstacles automatiques.
obstacle_automatique_timer: float = 0.0

# --- CHARGEMENT IMAGE VOITURE ---
try:
    image_voiture_originale = pygame.image.load('car.png').convert_alpha()
    largeur_voiture_px = int(TAILLE_CELLULE * 0.85)
    # Conserve le ratio hauteur/largeur
    hauteur_voiture_px = int(image_voiture_originale.get_height() * (largeur_voiture_px / image_voiture_originale.get_width()))
    image_voiture_echelle = pygame.transform.scale(image_voiture_originale, (largeur_voiture_px, hauteur_voiture_px))
    print(f"Image de base 'car.png' chargée et redimensionnée ({largeur_voiture_px}x{hauteur_voiture_px}).")
except Exception as e:
    print(f"AVERTISSEMENT: Impossible de charger/redimensionner 'car.png'. Les voitures seront des cercles. Erreur: {e}")

# --- FONCTIONS UTILITAIRES GRILLE & ENVIRONNEMENT ---

##
# @brief Crée une grille 2D remplie de zones non routières ('N').
# @param taille_x Nombre de colonnes.
# @param taille_y Nombre de lignes.
# @return Une liste de listes représentant la grille initialisée.
def creer_grille(taille_x: int, taille_y: int) -> List[List[str]]:
    return [[NON_ROUTIER for _ in range(taille_x)] for _ in range(taille_y)]

##
# @brief Définit le tracé des routes (remplace 'N' par ROUTE=' ') sur la grille.
# @param grille La grille (sera modifiée).
# @param taille_x Largeur de la grille.
# @param taille_y Hauteur de la grille.
# @details Exemple: crée une grille régulière avec routes toutes les 3 lignes/colonnes.
def definir_reseau_routier(grille: List[List[str]], taille_x: int, taille_y: int) -> None:
    print("Définition du réseau routier...")
    for y in range(taille_y):
        for x in range(taille_x):
            if x % 3 == 0 or y % 3 == 0:
                 grille[y][x] = ROUTE
    print("Réseau routier défini.")

##
# @brief Crée des dictionnaires définissant les sens de circulation autorisés pour chaque ligne et colonne.
# @param taille_x Largeur de la grille.
# @param taille_y Hauteur de la grille.
# @return Tuple contenant les dictionnaires de sens pour les lignes et les colonnes.
def creer_directions_routes(taille_x: int, taille_y: int) -> Tuple[Dict[int, str], Dict[int, str]]:
    directions_lignes = {y: "droite" if y % 2 == 0 else "gauche" for y in range(taille_y)}
    directions_colonnes = {x: "bas" if x % 2 == 0 else "haut" for x in range(taille_x)}
    return directions_lignes, directions_colonnes

##
# @brief Vérifie si une case donnée permet de sortir (est ROUTE et a au moins une voisine ROUTE).
# @param pos Position (x, y) à vérifier.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param grille La grille.
# @return True si la case est une ROUTE et permet un mouvement valide vers une case ROUTE adjacente. False sinon.
def est_case_escapable(pos: Tuple[int, int], taille_x: int, taille_y: int, grille: List[List[str]]) -> bool:
    x, y = pos
    # Doit être sur une route
    if not (0 <= y < taille_y and 0 <= x < taille_x and grille[y][x] == ROUTE):
        return False
    # Vérifie s'il y a au moins un voisin qui est aussi une route
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < taille_x and 0 <= ny < taille_y and grille[ny][nx] == ROUTE:
                 return True
    return False


# --- FONCTIONS DE GESTION OBSTACLES ---

##
# @brief Ajoute un obstacle MANUEL ('X') sur une case ROUTE de la grille.
# @param grille La grille.
# @param x Coordonnée X (colonne).
# @param y Coordonnée Y (ligne).
# @param feux Liste des feux (pour ne pas placer sur un feu).
# @return True si l'obstacle a été ajouté, False sinon.
def ajouter_obstacle_manuel(grille: List[List[str]], x: int, y: int, feux: List[Dict[str, Any]]) -> bool:
    positions_feux = {feu["position"] for feu in feux}
    if grille[y][x] == ROUTE and (x, y) not in positions_feux and grille[y][x] not in SYMBOLES_NON_PRATICABLES:
        grille[y][x] = OBSTACLE_MANUEL
        print(f"Obstacle MANUEL ajouté en ({x},{y}).")
        return True
    return False

##
# @brief Ajoute un obstacle AUTOMATIQUE ('A') sur une case ROUTE de la grille.
# @param grille La grille.
# @param x Coordonnée X (colonne).
# @param y Coordonnée Y (ligne).
# @param feux Liste des feux (pour ne pas placer sur un feu).
# @return True si l'obstacle automatique a été ajouté, False sinon.
def ajouter_obstacle_auto(grille: List[List[str]], x: int, y: int, feux: List[Dict[str, Any]]) -> bool:
    positions_feux = {feu["position"] for feu in feux}
    if grille[y][x] == ROUTE and (x, y) not in positions_feux and grille[y][x] not in SYMBOLES_NON_PRATICABLES:
        grille[y][x] = OBSTACLE_AUTO_SYM
        return True
    return False

##
# @brief Force un recalcul de chemin pour les voitures dont la destination ou le chemin est affecté par un nouvel obstacle.
# @param obstacle_x Coordonnée X de l'obstacle.
# @param obstacle_y Coordonnée Y de l'obstacle.
# @param voitures Liste des voitures actives (sera modifiée).
def forcer_recalcul_si_affecte(obstacle_x: int, obstacle_y: int, voitures: List[Dict[str, Any]]) -> None:
    obstacle_pos = (obstacle_x, obstacle_y)
    for v in voitures:
        if v.get('temps_arrivee') is None and tuple(v["position"]) != obstacle_pos:
            chemin_tuples = [tuple(p) for p in v["chemin"]] if v["chemin"] else []
            if (obstacle_pos in chemin_tuples) or (tuple(v["destination"]) == obstacle_pos):
                v["chemin"] = [] # Chemin vide pour forcer un recalcul
                v["recalcul_echecs"] = 0
                # Ne marque pas comme bloquée ici, la fonction détectera le blocage si le recalcul échoue ou si elle ne bouge pas.

# --- FONCTIONS DE GESTION PIÉTONS ET PASSAGES PIÉTONS ---

##
# @brief Initialise et place aléatoirement les passages piétons sur des cases ROUTE valides (évite feux et obstacles existants).
# @param n_passages Le nombre souhaité de passages piétons.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param feux Liste des feux (positions interdites).
# @param grille La grille (pour vérifier si la case est ROUTE et non obstacle).
# @return Une liste de dictionnaires représentant les passages piétons placés.
def initialiser_passages_pietons_sur_routes(n_passages: int, taille_x: int, taille_y: int, feux: List[Dict[str, Any]], grille: List[List[str]]) -> List[Dict[str, Any]]:
    nouveaux_passages = []
    positions_interdites = {f['position'] for f in feux}.union({
        (x,y) for y in range(taille_y) for x in range(taille_x)
        if grille[y][x] in (OBSTACLE_MANUEL, OBSTACLE_AUTO_SYM)
    })

    tentatives = 0
    max_tentatives = n_passages * 200

    while len(nouveaux_passages) < n_passages and tentatives < max_tentatives:
        px = random.randrange(1, taille_x - 1) # Evite les bords stricts
        py = random.randrange(1, taille_y - 1)
        pos = (px, py)

        if grille[py][px] == ROUTE and pos not in positions_interdites and pos not in {p['position'] for p in nouveaux_passages}:
            is_good_spot = False
            # Check passage horizontal
            if px > 0 and px < taille_x - 1 and grille[py][px-1] == ROUTE and grille[py][px+1] == ROUTE:
                 orientation = 'horizontal'
                 is_good_spot = True
            # Check passage vertical
            elif py > 0 and py < taille_y - 1 and grille[py-1][px] == ROUTE and grille[py+1][px] == ROUTE:
                 orientation = 'vertical'
                 is_good_spot = True

            if is_good_spot:
                 nouveaux_passages.append({'position': pos, 'orientation': orientation})
                 positions_interdites.add(pos)

        tentatives += 1

    if len(nouveaux_passages) < n_passages:
         print(f"Avertissement: N'a pu placer que {len(nouveaux_passages)} passages piétons utiles sur {n_passages} demandés.")

    print(f"Initialisé {len(nouveaux_passages)} passages piétons.")
    return nouveaux_passages

##
# @brief Met à jour l'état (progression) des piétons et gère l'apparition de nouveaux sur les passages libres.
# @param passages_pietons Liste des passages piétons.
# @param pietons_actifs Liste des piétons actifs (sera modifiée).
# @param voitures Liste des voitures actives (pour vérifier si un passage est bloqué par une voiture arrêtée).
def mettre_a_jour_pietons(passages_pietons: List[Dict[str, Any]], pietons_actifs: List[Dict[str, Any]], voitures: List[Dict[str, Any]]) -> None:
    global prochain_id_pieton

    # 1. Mise à jour de la progression des piétons existants et suppression si arrivée
    pietons_termines: List[Dict[str, Any]] = [] # Liste temporaire pour ceux à garder
    for pieton in pietons_actifs:
        pos_passage = pieton['passage_pos']
        # Un piéton est bloqué si une voiture *bloquée* ou non-arrivé est sur sa case passage
        # Vérifier uniquement si la voiture n'est pas en cours de disparition.
        voiture_bloquante_sur_passage = any(
            tuple(v['position']) == pos_passage and v.get('temps_arrivee') is None # Une voiture active occupe la case
            for v in voitures
        )
        # Alternativement, pour être précis comme dans la mise à jour voitures:
        # Une voiture BLOQUÉE (statut bloqué_depuis != None) ou en phase terminale (temps_arrivee!=None, pas encore supprimée)
        # bloquant_logic = any(
        #     tuple(v['position']) == pos_passage and (v.get('bloquee_depuis') is not None or (v.get('temps_arrivee') is not None and (time.time() - v['temps_arrivee']) < DELAI_DISPARITION_APRES_ARRIVEE ))
        #     for v in voitures
        # )
        # Conservons la version plus simple "une voiture active sur la case", car est_deplacement_valide checke voitures + pietons
        # Et les voitures ne *tentent* pas de rouler sur un piéton actif.
        # Le piéton lui-même s'arrête si une voiture active (même non bloquée) est sur sa case.
        voiture_presente_sur_passage = any(
            tuple(v['position']) == pos_passage
            for v in voitures if v.get('temps_arrivee') is None
        )


        # Le piéton ne bouge que s'il n'y a PAS de voiture active sur son passage
        if not voiture_presente_sur_passage:
             pieton['progres'] += VITESSE_PIETON

        # Si le piéton a fini sa traversée (progression >= 1.0), il est supprimé
        if pieton['progres'] < 1.0:
            pietons_termines.append(pieton)

    # Remplace la liste des piétons actifs par ceux qui n'ont pas fini de traverser
    pietons_actifs[:] = pietons_termines

    # 2. Tentative d'apparition de nouveaux piétons
    # Vérifie s'il y a des passages piétons disponibles et si la probabilité aléatoire permet l'apparition ce tick.
    if passages_pietons and random.random() < PROBA_APPARITION_PIETON * len(passages_pietons):
        # Choisit un passage piéton au hasard parmi ceux initialisés sur des routes valides
        passage_choisi = random.choice(passages_pietons)
        pos_passage_cible = passage_choisi['position']

        # Un nouveau piéton peut apparaître seulement si la case du passage piéton n'est occupée par AUCUN piéton
        # ET par AUCUNE voiture (ni arrivée ni en route) qui serait dessus au moment de l'apparition.
        passage_deja_occupe_par_pieton = any(p['passage_pos'] == pos_passage_cible for p in pietons_actifs)
        passage_deja_occupe_par_voiture = any(
            tuple(v['position']) == pos_passage_cible
            for v in voitures # Regarde TOUTES les voitures, même celles marquées pour suppression imminente, tant qu'elles sont encore dans la liste.
        )

        # Apparait seulement si le passage est totalement libre (ROUTE, pas de piéton, pas de voiture)
        # Note: la vérification que le passage est sur ROUTE est faite lors de l'initialisation des passages.
        if not passage_deja_occupe_par_pieton and not passage_deja_occupe_par_voiture:
            nouvel_id = prochain_id_pieton
            nouveau_pieton = {
                'id': nouvel_id,
                'passage_pos': pos_passage_cible, # Position de la cellule du passage
                'orientation': passage_choisi['orientation'], # Orientation de la traversée (horizontal ou vertical)
                'progres': 0.0 # Commence la traversée (0.0 = début, 1.0 = fin)
            }
            pietons_actifs.append(nouveau_pieton)
            prochain_id_pieton += 1
            #print(f"Nouveau piéton P{nouvel_id} apparaît en {pos_passage_cible}.")


# --- FONCTIONS DE GESTION FEUX ---

##
# @brief Initialise et place les feux sur des cases ROUTE candidates (préfère intersections) de manière répartie.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param grille La grille (pour identifier les routes et intersections).
# @return Une liste de dictionnaires représentant les feux initialisés.
def initialiser_feux_repartis_sur_routes(taille_x: int, taille_y: int, grille: List[List[str]]) -> List[Dict[str, Any]]:
    feux = []
    positions_occupees = set() # Pour éviter de placer deux feux sur la même case
    # Limites pour répartir les feux
    MAX_FEUX_PAR_LIGNE = max(1, taille_x // 15) # Par exemple, 1 feu tous les ~15 cellules de largeur
    MAX_FEUX_PAR_COLONNE = max(1, taille_y // 8) # Par exemple, 1 feu tous les ~8 cellules de hauteur

    feux_par_ligne: Dict[int, int] = {}
    feux_par_colonne: Dict[int, int] = {}

    duree_vert, duree_orange, duree_rouge = 10.0, 3.0, 7.0

    # Trouver les intersections (cases ROUTE avec >=3 voisins ROUTE y compris elles-mêmes)
    intersections_candidates: List[Tuple[int, int]] = []
    for y in range(taille_y):
        for x in range(taille_x):
             if grille[y][x] == ROUTE:
                 route_voisins = sum(
                     1 for dx, dy in [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
                     if 0 <= x + dx < taille_x and 0 <= y + dy < taille_y and grille[y + dy][x + dx] == ROUTE
                 )
                 if route_voisins >= 3: intersections_candidates.append((x, y))

    # Fallback si peu/pas d'intersections détectées
    if not intersections_candidates:
         intersections_candidates = [(x,y) for y in range(taille_y) for x in range(taille_x) if grille[y][x] == ROUTE]
         if not intersections_candidates:
              print("FATAL: Aucune case ROUTE pour placer les feux!")
              return []

    random.shuffle(intersections_candidates)

    for pos in intersections_candidates:
        x, y = pos
        peut_placer = (
            feux_par_ligne.get(y, 0) < MAX_FEUX_PAR_LIGNE and
            feux_par_colonne.get(x, 0) < MAX_FEUX_PAR_COLONNE and
            pos not in positions_occupees and
            grille[y][x] not in (OBSTACLE_AUTO_SYM, OBSTACLE_MANUEL)
        )

        if peut_placer:
            temps_total_cycle = duree_vert + duree_orange + duree_rouge
            offset = random.uniform(0, temps_total_cycle)
            temps_depuis_debut_cycle = (time.time() - offset) % temps_total_cycle

            etat_initial = "vert"
            duree_actuelle_initiale: float
            dernier_changement_initial: float = time.time() - temps_depuis_debut_cycle

            if temps_depuis_debut_cycle <= duree_vert:
                 etat_initial = "vert"
                 temps_ecoule_dans_etat = temps_depuis_debut_cycle
                 duree_actuelle_initiale = duree_vert - temps_ecoule_dans_etat
            elif temps_depuis_debut_cycle <= duree_vert + duree_orange:
                 etat_initial = "orange"
                 temps_ecoule_dans_etat = temps_depuis_debut_cycle - duree_vert
                 duree_actuelle_initiale = duree_orange - temps_ecoule_dans_etat
            else: # Reste du cycle = rouge
                 etat_initial = "rouge"
                 temps_ecoule_dans_etat = temps_depuis_debut_cycle - (duree_vert + duree_orange)
                 duree_actuelle_initiale = duree_rouge - temps_ecoule_dans_etat

            feux.append({
                "position": pos, "etat": etat_initial,
                "duree_vert": duree_vert, "duree_orange": duree_orange, "duree_rouge": duree_rouge,
                "duree_actuelle": duree_actuelle_initiale,
                "dernier_changement": dernier_changement_initial
            })
            positions_occupees.add(pos)
            feux_par_ligne[y] = feux_par_ligne.get(y, 0) + 1
            feux_par_colonne[x] = feux_par_colonne.get(x, 0) + 1

    print(f"Initialisé {len(feux)} feux (max {MAX_FEUX_PAR_LIGNE}/ligne, max {MAX_FEUX_PAR_COLONNE}/colonne).")
    return feux

##
# @brief Met à jour l'état (couleur) de chaque feu en fonction du temps écoulé.
# @param feux La liste des feux de circulation (sera modifiée).
def mettre_a_jour_feux(feux: List[Dict[str, Any]]) -> None:
    temps_actuel = time.time()
    for feu in feux:
        if temps_actuel - feu["dernier_changement"] > feu["duree_actuelle"]:
            if feu["etat"] == "vert":
                feu["etat"] = "orange"
                feu["duree_actuelle"] = feu["duree_orange"]
            elif feu["etat"] == "orange":
                feu["etat"] = "rouge"
                feu["duree_actuelle"] = feu["duree_rouge"]
            elif feu["etat"] == "rouge":
                feu["etat"] = "vert"
                feu["duree_actuelle"] = feu["duree_vert"]
            feu["dernier_changement"] = temps_actuel

# --- FONCTION PATHFINDING (A*) ---

##
# @brief Calcule le chemin le plus court entre deux points sur la grille en évitant les obstacles et respectant les sens de circulation.
# @param grille La grille.
# @param depart Coordonnées de départ [x, y].
# @param arrivee Coordonnées d'arrivée [x, y].
# @param directions_lignes Dictionnaire des sens par ligne.
# @param directions_colonnes Dictionnaire des sens par colonne.
# @return Liste de coordonnées [x, y] représentant le chemin, ou None si aucun chemin n'est trouvé.
def trouver_chemin(grille: List[List[str]], depart: List[int], arrivee: List[int], directions_lignes: Dict[int, str], directions_colonnes: Dict[int, str]) -> Union[List[List[int]], None]:
    def heuristique(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        # Distance de Manhattan comme heuristique
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    depart_t, arrivee_t = tuple(depart), tuple(arrivee)
    taille_x, taille_y = len(grille[0]), len(grille)

    # Vérification basique de la validité des points de départ/arrivée
    if not (0 <= depart_t[0] < taille_x and 0 <= depart_t[1] < taille_y and 0 <= arrivee_t[0] < taille_x and 0 <= arrivee_t[1] < taille_y):
        return None # Hors limites
    if grille[depart_t[1]][depart_t[0]] != ROUTE or grille[arrivee_t[1]][arrivee_t[0]] != ROUTE:
        return None # Pas sur une route praticable

    if depart_t == arrivee_t:
        return [list(depart_t)] # Déjà arrivé

    # Initialisation de l'algorithme A*
    # ouverte est un min-heap: [(f_cost, position)]
    ouverte: List[Tuple[int, Tuple[int, int]]] = [(heuristique(depart_t, arrivee_t), depart_t)]
    # precedent enregistre le chemin : position courante -> position précédente
    precedent: Dict[Tuple[int, int], Union[Tuple[int, int], None]] = {depart_t: None}
    # cout_g enregistre le coût du départ à la position courante
    cout_g: Dict[Tuple[int, int], float] = {depart_t: 0}

    # Directions de déplacement possibles (orthogonal seulement)
    cardinal_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # Bas, Haut, Droite, Gauche

    while ouverte:
        # Sélectionne la case dans 'ouverte' avec le plus petit f_cost
        _, courant = heapq.heappop(ouverte)
        cx, cy = courant

        if courant == arrivee_t:
            # Chemin trouvé, reconstruction à l'envers
            chemin: List[List[int]] = []
            temp = courant
            while temp is not None:
                chemin.append(list(temp))
                temp = precedent.get(temp)
            return chemin[::-1] # Retourne le chemin dans le bon ordre (du départ à l'arrivée)

        # Explore les voisins
        for dx, dy in cardinal_directions:
            voisin_t = (cx + dx, cy + dy)
            nx, ny = voisin_t

            # Vérifications du voisin
            if not (0 <= nx < taille_x and 0 <= ny < taille_y): continue # Hors limites
            if grille[ny][nx] != ROUTE: continue # Le voisin n'est pas une route (inclut Obstacles et Non-Routier)

            # Vérifie si le déplacement est autorisé selon les sens uniques globaux
            move_is_allowed = False
            if dy == 0 and dx != 0: # Mouvement horizontal
                # Vérifie le sens de la ligne actuelle (cy)
                if (directions_lignes.get(cy) == "droite" and dx == 1) or (directions_lignes.get(cy) == "gauche" and dx == -1):
                    move_is_allowed = True
            elif dx == 0 and dy != 0: # Mouvement vertical
                 # Vérifie le sens de la colonne actuelle (cx)
                if (directions_colonnes.get(cx) == "bas" and dy == 1) or (directions_colonnes.get(cx) == "haut" and dy == -1):
                    move_is_allowed = True
            # Les mouvements diagonaux sont implicitement non autorisés ici.

            if not move_is_allowed:
                 continue # Le déplacement ne suit pas le sens unique

            # Calcule le coût (distance + 1 car mouvements unitaires)
            n_cout_g = cout_g[courant] + 1 # Chaque étape coûte 1

            # Si ce chemin vers le voisin est meilleur (coût G plus petit), ou si le voisin n'a pas encore été visité
            if voisin_t not in cout_g or n_cout_g < cout_g[voisin_t]:
                cout_g[voisin_t] = n_cout_g # Met à jour le coût G
                precedent[voisin_t] = courant # Enregistre le parent pour reconstruction du chemin
                priorite = n_cout_g + heuristique(voisin_t, arrivee_t) # Calcule f_cost (G + H)
                heapq.heappush(ouverte, (priorite, voisin_t)) # Ajoute ou met à jour dans la queue de priorité

    return None # Aucun chemin trouvé de départ à arrivée

##
# @brief Trouve une nouvelle destination aléatoire valide (sur ROUTE praticable et "escapable")
# pour une voiture, en évitant la position actuelle et les positions permanemment bloquées.
# @param voiture_actuelle Le dict voiture.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param feux Liste feux (pour exclure ces positions).
# @param grille La grille.
# @param directions_lignes Dictionnaire des sens par ligne (utilisé par `est_case_escapable`).
# @param colonnes_directions Dictionnaire des sens par colonne (utilisé par `est_case_escapable`).
# @param voitures Liste autres voitures (non utilisé dans l'impl. actuelle pour choisir dest, mais pourrait l'être).
# @return Nouvelle destination sous forme de liste [x, y] ou None si aucune destination atteignable trouvée.
def trouver_nouvelle_destination_valide(voiture_actuelle: Dict[str, Any], taille_x: int, taille_y: int, feux: List[Dict[str, Any]], grille: List[List[str]], directions_lignes: Dict[int, str], colonnes_directions: Dict[int, str], voitures: List[Dict[str, Any]]) -> Union[List[int], None]:
    # Calculer les positions permanentes interdites une seule fois
    positions_interdites_perm = {feu["position"] for feu in feux}.union({
         (x,y) for y in range(taille_y) for x in range(taille_x)
         if grille[y][x] in SYMBOLES_NON_PRATICABLES
    })

    pos_actuelle = tuple(voiture_actuelle["position"])
    tentatives = 0
    max_tentatives = 300 # Limiter le nombre de tentatives pour éviter de bloquer la simulation

    while tentatives < max_tentatives:
        # Choisit une destination aléatoire potentielle
        x_dest, y_dest = random.randrange(taille_x), random.randrange(taille_y)
        dest = (x_dest, y_dest)

        # Vérifie si la destination candidate est valide :
        # 1. Dans les limites
        # 2. Sur une case ROUTE
        # 3. Pas la position actuelle de la voiture
        # 4. Non dans la liste des positions permanentes interdites (feux, obstacles, non-routier)
        # 5. Est une case "escapable" (a une route voisine accessible depuis elle)
        if (0 <= y_dest < taille_y and 0 <= x_dest < taille_x) and \
           grille[y_dest][x_dest] == ROUTE and \
           dest != pos_actuelle and \
           dest not in positions_interdites_perm and \
           est_case_escapable(dest, taille_x, taille_y, grille):

            # De plus, il doit exister un chemin possible de la position actuelle vers cette destination
            # avec l'état actuel de la grille (obstacles, directions).
            temp_path = trouver_chemin(grille, list(pos_actuelle), list(dest), directions_lignes, colonnes_directions)
            # Un chemin valide doit exister ET contenir plus d'une étape (plus que juste la position de départ)
            if temp_path and len(temp_path) > 1:
                return list(dest) # Destination valide et atteignable trouvée

        tentatives += 1

    return None # Aucune destination valide et atteignable trouvée après max_tentatives


# --- FONCTION GESTION MOUVEMENT (Détection Blocage, Recalcul, Déplacement) ---

##
# @brief Vérifie si un déplacement vers une position donnée est valide, en tenant compte des feux et des piétons.
# Cette fonction NE VÉRIFIE PAS la présence d'autres voitures (collision car-to-car).
# @param pos Position cible [x, y] du déplacement.
# @param feux Liste des feux (pour vérifier les états).
# @param pietons Liste des piétons actifs (pour vérifier les passages piétons occupés).
# @param grille La grille (pour vérifier que la position est une ROUTE).
# @return True si la position est ROUTE et non bloquée par un feu rouge/orange ou un piéton, False sinon.
def est_deplacement_valide(pos: Tuple[int, int], feux: List[Dict[str, Any]], pietons: List[Dict[str, Any]], grille: List[List[str]]) -> bool:
    x, y = pos
    # Vérifier les limites de la grille et le type de cellule (doit être une ROUTE)
    taille_y, taille_x = len(grille), len(grille[0])
    if not (0 <= x < taille_x and 0 <= y < taille_y) or grille[y][x] != ROUTE:
        # Cette vérification est déjà implicitement faite par le pathfinding et la gestion des obstacles
        # dans les fonctions d'ajout, mais une double vérification ne fait pas de mal ici,
        # ou peut signaler un problème logique ailleurs si elle est déclenchée.
        return False

    # Vérifier les feux de circulation
    # Si la position cible correspond à un feu qui n'est PAS vert, le déplacement est interdit.
    for feu in feux:
        if feu["position"] == pos and feu["etat"] != "vert":
             #print(f" -> Mouvement vers {pos} bloqué par un feu {feu['etat']}.")
             return False

    # Vérifier les passages piétons
    # Si la position cible est un passage piéton et qu'un piéton est en cours de traversée (progrès < 1.0) dessus,
    # le déplacement de la voiture est interdit.
    for pieton in pietons:
         if pieton['passage_pos'] == pos and pieton['progres'] < 1.0:
              #print(f" -> Mouvement vers {pos} bloqué par un piéton.")
              return False

    # Si toutes les vérifications passent, le déplacement est valide selon ces règles (feux, piétons, type de cellule).
    return True

##
# @brief Gère le comportement de toutes les voitures : pathfinding, détection de blocage, recalcul de chemin/destination, et déplacement.
# @param voitures Liste des voitures (sera modifiée).
# @param grille La grille.
# @param feux Liste des feux.
# @param directions_lignes Dict sens lignes.
# @param colonnes_directions Dict sens colonnes.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param pietons Liste des piétons actifs.
def mettre_a_jour_voitures(voitures: List[Dict[str, Any]], grille: List[List[str]], feux: List[Dict[str, Any]], directions_lignes: Dict[int, str], colonnes_directions: Dict[int, str], taille_x: int, taille_y: int, pietons: List[Dict[str, Any]]) -> None:
    temps_actuel = time.time()

    # PHASE 0: Gérer les arrivées et identifier les voitures à supprimer ou garder actives
    voitures_restantes: List[Dict[str, Any]] = []
    for v in voitures:
        # Marque la voiture comme arrivée si elle atteint sa destination pour la première fois
        if v.get("temps_arrivee") is None and tuple(v["position"]) == tuple(v["destination"]):
            v["temps_arrivee"] = temps_actuel
            v["chemin"] = [] # Vide le chemin une fois arrivé
            v["bloquee_depuis"] = None # N'est plus considérée comme bloquée une fois arrivée
            v["recalcul_echecs"] = 0 # Reset le compteur d'échecs car objectif atteint

        # Conserver la voiture si elle n'est pas encore arrivée OU si elle est arrivée récemment et n'a pas dépassé le délai de disparition
        if v.get("temps_arrivee") is None or (temps_actuel - v["temps_arrivee"] < DELAI_DISPARITION_APRES_ARRIVEE):
             voitures_restantes.append(v)
    # Mettre à jour la liste des voitures dans l'espace mémoire référencé par 'voitures'
    voitures[:] = voitures_restantes

    # Identifier les voitures *effectivement en route* pour les phases suivantes (celles qui n'ont PAS atteint leur destination finale)
    voitures_en_route = [v for v in voitures if v.get("temps_arrivee") is None]

    # PHASE 1: Tenter recalcul de chemin pour les voitures pathless ou récemment bloquées (test court)
    # Identifie les voitures ayant besoin d'un calcul ou recalcul de chemin initial
    # (celles qui n'ont pas de chemin actuellement OU qui sont marquées bloquées et ont dépassé le seuil pour un recalcul simple)
    cars_needing_pathfind = [
         v for v in voitures_en_route
         if not v["chemin"] or (v.get("bloquee_depuis") is not None and (temps_actuel - v["bloquee_depuis"]) > SEUIL_BLOCAGE)
    ]

    for v in cars_needing_pathfind:
         current_pos_list = list(v["position"])
         destination_list = list(v["destination"])

         # Tente de trouver un chemin VERS la destination actuelle
         path_trouve = trouver_chemin(grille, current_pos_list, destination_list, directions_lignes, colonnes_directions)

         if path_trouve and len(path_trouve) > 1:
             # Chemin trouvé, le définir et réinitialiser l'état bloqué
             v["chemin"] = path_trouve[1:] # Chemin commence *après* la position actuelle
             v["bloquee_depuis"] = None # N'est plus considérée comme bloquée, elle a maintenant un chemin
             v["recalcul_echecs"] = 0 # Reset car un chemin viable a été trouvé
             #print(f"V{v['id']}: Succès simple recalcul.")
         else:
             # Aucun chemin trouvé vers la destination actuelle
             v["chemin"] = [] # Assurer que le chemin est vide pour indiquer pas de direction connue
             # Si elle n'était pas déjà marquée bloquée, la marquer maintenant
             if v.get("bloquee_depuis") is None:
                  v["bloquee_depuis"] = temps_actuel
             # Le compteur d'échecs sera incrémenté dans la phase suivante si nécessaire.



    # PHASE 2: Résolution des mouvements (Prévention des collisions car-to-car) et Application
    # Construit l'ensemble des positions occupées *projetées* à la fin de ce tick.
    # Commence par toutes les positions actuelles des voitures qui ne sont PAS en cours de disparition (elles pourraient potentiellement rester là si elles ne peuvent pas bouger).
    projected_occupied_cells: Set[Tuple[int, int]] = {
        tuple(v['position']) for v in voitures if v.get("temps_arrivee") is None # Only active cars participate in projected collision
    }

    # Stocke les mouvements approuvés : car_id -> (new_x, new_y) tuple
    approved_moves: Dict[int, Tuple[int, int]] = {}

    # Identifier les voitures éligibles pour un mouvement *potentielles* ce tick: non arrivées, avec chemin, délai respecté.
    voitures_eligibles_pour_mouvement = [
        v for v in voitures_en_route # Seules les voitures en route peuvent bouger
        if v["chemin"] and (temps_actuel - v["dernier_deplacement"] >= DELAI_MIN_MOUVEMENT)
    ]

    # Prioriser les voitures récemment bloquées pour la résolution du mouvement (pour aider à "défiler" les queues)
    # Une voiture est "priorisée" si elle était marquée `bloquee_depuis`.
    prioritized_cars = [v for v in voitures_eligibles_pour_mouvement if v.get("bloquee_depuis") is not None]
    remaining_cars = [v for v in voitures_eligibles_pour_mouvement if v.get("bloquee_depuis") is None]

    # Tri ascendant par 'bloquee_depuis': les plus anciens timestamps (les plus bloqués) en premier
    prioritized_cars.sort(key=lambda car: car["bloquee_depuis"])
    # Mélange le reste aléatoirement pour casser les égalités
    random.shuffle(remaining_cars)

    # Ordre de traitement: voitures prioritaires, puis le reste mélangé
    voitures_a_resoudre_mouvement = prioritized_cars + remaining_cars


    # Itère sur les voitures dans l'ordre de priorité pour tenter d'appliquer leur mouvement
    for v in voitures_a_resoudre_mouvement:
        car_id = v["id"]
        current_pos_t = tuple(v["position"])
        # Le prochain pas désiré est la première case du chemin calculé
        next_pos_t = tuple(v["chemin"][0]) # On sait qu'il y a un chemin, car elles sont "eligibles"

        # Tente de se déplacer vers next_pos_t seulement si cette case projetée est libre
        # ET que le déplacement respecte les règles externes (feux, piétons).
        # On NE VERIFIE PAS ICI le type de cellule (ROUTE, obstacle, etc.) car cela a été fait par le pathfinding.
        if next_pos_t not in projected_occupied_cells and \
           est_deplacement_valide(next_pos_t, feux, pietons, grille): # La case cible est libre (proj.), non bloquée par feu/piéton...

            # --- MOUVEMENT APPROUVÉ pour V vers next_pos_t! ---
            # La voiture V quitte sa position actuelle current_pos_t et va vers next_pos_t.
            # Cette future position next_pos_t est maintenant réservée dans notre projection pour ce tick.

            # Met à jour l'occupation projetée: V libère sa position actuelle et réserve sa future position.
            # La suppression de current_pos_t est parfois inutile si elle n'y était pas,
            # mais l'ajouter et retirer après garantit que SA nouvelle position bloque les autres.
            # Meilleure approche : l'ajouter *après* qu'on sache qu'elle BOUGE vers elle.
            # projected_occupied_cells.discard(current_pos_t) # Retiré car l'initialisation inclut déjà les positions courantes. On n'a besoin d'ajouter QUE les nouvelles.
            # Add the *new* target position to the projected occupied cells.
            projected_occupied_cells.add(next_pos_t) # C'est ICI qu'on marque la cellule ciblée comme occupée *pour le reste des voitures de ce tick*.

            # Enregistre le mouvement approuvé pour application différée
            approved_moves[car_id] = next_pos_t

            # Remettre à zéro le marqueur de blocage si la voiture a pu bouger.
            # Ce marqueur était activé si la voiture n'avait pas bougé depuis SEUIL_BLOCAGE.
            # Maintenant qu'elle bouge, elle n'est plus "bloquée" par le système de détection de blocage passif.
            v["bloquee_depuis"] = None # Une voiture qui bouge n'est plus considérée bloquée


    # PHASE 3: Application réelle des mouvements approuvés
    # Itère sur la liste principale des voitures et applique les mouvements qui ont été décidés dans la phase 3.
    for v in voitures:
        car_id = v["id"]
        # Vérifie si un mouvement a été approuvé pour cette voiture
        if car_id in approved_moves:
            old_pos = list(v["position"]) # Ancienne position (liste)
            new_pos_t = approved_moves[car_id] # Nouvelle position (tuple)
            new_pos_list = list(new_pos_t) # Convertir en liste

            # Mettre à jour l'orientation basée sur la direction du mouvement
            dx, dy = new_pos_t[0] - old_pos[0], new_pos_t[1] - old_pos[1]
            if dx == 1 and dy == 0: v["orientation"] = 0 # Droite
            elif dx == -1 and dy == 0: v["orientation"] = 180 # Gauche
            elif dx == 0 and dy == 1: v["orientation"] = 270 # Bas
            elif dx == 0 and dy == -1: v["orientation"] = 90  # Haut
            # Gérer les diagonales si le pathfinding les autorisait

            # Appliquer la nouvelle position
            v["position"] = new_pos_list

            # Supprimer le premier pas du chemin car il a été exécuté
            # Cette vérification assure qu'on pop le bon élément, bien qu'avec la logique actuelle ça devrait toujours être v["chemin"][0].
            if v["chemin"] and tuple(v["chemin"][0]) == new_pos_t:
                 v["chemin"].pop(0)
            #else: # Potential desync? Or the move was just one step and chemin is now empty.

            # Mettre à jour le timestamp du dernier déplacement réussi
            v["dernier_deplacement"] = temps_actuel

            # 'bloquee_depuis' a déjà été reset en Phase 3 si le mouvement a été approuvé.

        # Les voitures qui n'ont pas pu bouger restent sur place. Leur 'bloquee_depuis' sera potentiellement mis à jour en Phase 1/2
        # du prochain tick si elles restent immobiles pendant suffisamment longtemps.

# --- FONCTIONS DE GENERATION VOITURES ---

##
# @brief Tente de générer une nouvelle voiture avec destination aléatoire valide et chemin atteignable.
# Cette fonction est utilisée pour remplacer les voitures supprimées afin de maintenir un nombre cible.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param feux Liste des feux.
# @param grille La grille.
# @param directions_lignes Dict sens lignes.
# @param colonnes_directions Dict sens colonnes.
# @param img_base_voiture Image Pygame de base pour coloration (ou None).
# @param voitures Liste des voitures actuelles (pour vérifier positions déjà occupées).
# @return Un dictionnaire représentant la nouvelle voiture si succès, None sinon.
def generer_une_nouvelle_voiture(taille_x: int, taille_y: int, feux: List[Dict[str, Any]], grille: List[List[str]], directions_lignes: Dict[int, str], colonnes_directions: Dict[int, str], img_base_voiture: Union[pygame.Surface, None], voitures: List[Dict[str, Any]]) -> Union[Dict[str, Any], None]:
    global prochain_id_voiture
    # Positions non routières, feux, ou obstacles permanents/initiaux sont interdits comme START ou END.
    # Les positions temporairement bloquées par des voitures actuelles doivent aussi être évitées comme START.
    positions_interdites_perm = {feu["position"] for feu in feux}.union({
         (x,y) for y in range(taille_y) for x in range(taille_x)
         if grille[y][x] in SYMBOLES_NON_PRATICABLES
    })
    # Les positions *actuellement* occupées par des voitures actives
    occupied_positions_by_cars: Set[Tuple[int, int]] = {tuple(v['position']) for v in voitures if v.get('temps_arrivee') is None}

    tentatives_start = 50 # Limite les tentatives pour trouver un point de départ viable
    tentatives_dest = 50 # Limite les tentatives pour trouver une destination viable DEPUIS ce point de départ
    total_attempts_pair = 1000 # Nombre max de paires start/dest candidates à tester en tout

    for _ in range(total_attempts_pair):
        # Trouver un point de départ valide (ROUTE, libre, pas feu/obstacle, escapable)
        pos_initiale: Union[Tuple[int, int], None] = None
        for _ in range(tentatives_start):
            x_pos, y_pos = random.randrange(taille_x), random.randrange(taille_y)
            pos_candidate = (x_pos, y_pos)
            if (0 <= y_pos < taille_y and 0 <= x_pos < taille_x) and \
               grille[y_pos][x_pos] == ROUTE and \
               pos_candidate not in positions_interdites_perm and \
               pos_candidate not in occupied_positions_by_cars and \
               est_case_escapable(pos_candidate, taille_x, taille_y, grille): # Escapable basé uniquement sur grille non bloquée permanemment
               pos_initiale = pos_candidate
               break # Trouvé un point de départ

        if pos_initiale is None:
            # print("  > Génération: Échec de trouver une position initiale viable.")
            continue # Tente une nouvelle paire

        # Trouve une destination valide depuis ce point de départ
        dest: Union[Tuple[int, int], None] = None
        for _ in range(tentatives_dest):
            x_dest, y_dest = random.randrange(taille_x), random.randrange(taille_y)
            dest_candidate = (x_dest, y_dest)
            if (0 <= y_dest < taille_y and 0 <= x_dest < taille_x) and \
               grille[y_dest][x_dest] == ROUTE and \
               dest_candidate != pos_initiale and \
               dest_candidate not in positions_interdites_perm and \
               est_case_escapable(dest_candidate, taille_x, taille_y, grille): # Escapable basé uniquement sur grille non bloquée permanemment
                # Et surtout, doit être atteignable PAR PATHFINDING depuis pos_initiale
                temp_path = trouver_chemin(grille, list(pos_initiale), list(dest_candidate), directions_lignes, colonnes_directions)
                if temp_path and len(temp_path) > 1:
                    dest = dest_candidate
                    chemin_initial = temp_path # Garde le chemin trouvé
                    break # Trouvé une destination atteignable

        if dest is not None:
            # PAIRE (start, dest) trouvée AVEC un chemin
            nouvel_id = prochain_id_voiture
            prochain_id_voiture += 1

            voiture_couleur = (random.randint(0, 150), random.randint(0, 150), random.randint(100, 255)) # Une couleur distinctive
            voiture_image_specifique = None
            if img_base_voiture:
                try:
                    voiture_image_specifique = img_base_voiture.copy()
                    sombresseur_facteur = 0.8
                    mask = pygame.Surface(voiture_image_specifique.get_size(), pygame.SRCALPHA)
                    dark_color = (int(voiture_couleur[0]*sombresseur_facteur), int(voiture_couleur[1]*sombresseur_facteur), int(voiture_couleur[2]*sombresseur_facteur), 255)
                    mask.fill(dark_color)
                    voiture_image_specifique.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                except Exception as img_err:
                    print(f"Erreur coloration img nouvelle voiture {nouvel_id}: {img_err}. Utilisera un cercle.")
                    voiture_image_specifique = None

            # Créer la nouvelle voiture
            nouvelle_voiture = {
                "id": nouvel_id,
                "position": list(pos_initiale),
                "destination": list(dest),
                "chemin": chemin_initial[1:], # Le chemin commence par le prochain pas, pas la position actuelle
                "temps_arrivee": None,
                "dernier_deplacement": time.time(), # Initialisé maintenant, elle bougera après DELAI_MIN_MOUVEMENT
                "couleur": voiture_couleur if voiture_image_specifique is None else None,
                "image": voiture_image_specifique,
                "orientation": 0, # Orientation initiale (peut être ajustée au 1er mouvement)
                "bloquee_depuis": None,
                "recalcul_echecs": 0
            }
            #print(f"Généré nouvelle voiture V{nouvel_id} de {pos_initiale} à {dest}. Chemin trouvé de {len(nouvelle_voiture['chemin']) + 1} pas.")
            return nouvelle_voiture
        # else: Failed to find a reachable destination from this start pos. Loop continues to try a new start pos.

    #print(f"Avertissement: Échec génération nouvelle voiture après {total_attempts_pair} tentatives de paires start/dest.")
    return None # Aucune voiture générée après toutes les tentatives

##
# @brief Génère la population initiale de voitures. Utilise `generer_une_nouvelle_voiture` en boucle.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param feux Liste des feux.
# @param grille La grille.
# @param directions_lignes Dict sens lignes.
# @param colonnes_directions Dict sens colonnes.
# @param img_base_voiture Image Pygame de base (ou None).
# @param n_voitures Nombre de voitures souhaité.
# @return Liste des dictionnaires voiture générés.
def generer_voitures_initiales(taille_x: int, taille_y: int, feux: List[Dict[str, Any]], grille: List[List[str]], directions_lignes: Dict[int, str], colonnes_directions: Dict[int, str], img_base_voiture: Union[pygame.Surface, None], n_voitures: int) -> List[Dict[str, Any]]:
    initial_voitures: List[Dict[str, Any]] = []
    max_total_generation_attempts = n_voitures * 2 # Tenter jusqu'à X fois le nombre cible

    attempt = 0
    while len(initial_voitures) < n_voitures and attempt < max_total_generation_attempts:
        nouvelle_voiture = generer_une_nouvelle_voiture(
            taille_x, taille_y, feux, grille, directions_lignes, colonnes_directions,
            img_base_voiture,
            initial_voitures # Passe la liste actuelle des voitures initiales pour éviter les doublons de position *au début*
        )
        if nouvelle_voiture:
            initial_voitures.append(nouvelle_voiture)
        attempt += 1

    print(f"Initialisé {len(initial_voitures)} voitures (demandées {n_voitures}, {attempt} tentatives). Prochain ID: {prochain_id_voiture}.")
    return initial_voitures

# --- FONCTIONS DE DESSIN ---

##
# @brief Dessine les fonds des cellules de la grille (Non-Routier ou Route).
# @param fenetre Surface Pygame.
# @param grille La grille.
# @param taille_cellule Taille d'une cellule en pixels.
def dessiner_fonds_cellules(fenetre: pygame.Surface, grille: List[List[str]], taille_cellule: int) -> None:
    for y in range(len(grille)):
        for x in range(len(grille[0])):
            cell_rect = pygame.Rect(x * taille_cellule, y * taille_cellule, taille_cellule, taille_cellule)
            couleur = GRIS_CLAIR if grille[y][x] == NON_ROUTIER else GRIS_ROUTE
            pygame.draw.rect(fenetre, couleur, cell_rect)

##
# @brief Dessine les lignes de la grille (par-dessus les fonds).
# @param fenetre Surface Pygame.
# @param largeur Largeur de la fenêtre.
# @param hauteur Hauteur de la fenêtre.
# @param taille_cellule Taille d'une cellule.
def dessiner_grille_lignes(fenetre: pygame.Surface, largeur: int, hauteur: int, taille_cellule: int) -> None:
    epaisseur_ligne = 1
    for x in range(0, largeur + 1, taille_cellule):
        pygame.draw.line(fenetre, NOIR, (x, 0), (x, hauteur), epaisseur_ligne)
    for y in range(0, hauteur + 1, taille_cellule):
        pygame.draw.line(fenetre, NOIR, (0, y), (largeur, y), epaisseur_ligne)

##
# @brief Dessine les obstacles MANUELS ('X').
# @param fenetre Surface Pygame.
# @param grille La grille.
# @param taille_cellule Taille d'une cellule.
def dessiner_obstacles_manuels(fenetre: pygame.Surface, grille: List[List[str]], taille_cellule: int) -> None:
    for y in range(len(grille)):
        for x in range(len(grille[0])):
            if grille[y][x] == OBSTACLE_MANUEL:
                pygame.draw.rect(fenetre, NOIR, (x * taille_cellule, y * taille_cellule, taille_cellule, taille_cellule))

##
# @brief Dessine les obstacles AUTOMATIQUES ('A').
# @param fenetre Surface Pygame.
# @param grille La grille.
# @param taille_cellule Taille d'une cellule.
def dessiner_obstacles_automatiques(fenetre: pygame.Surface, grille: List[List[str]], taille_cellule: int) -> None:
    # Optionnel : Dessiner les obstacles automatiques différemment ou pas du tout
    # S'ils sont destinés à être des blocages "naturels" non visibles, ne les dessine pas.
    # S'ils représentent un événement (accident, travaux), on peut les dessiner.
    # Exemple : on ne les dessine pas, le fond GRIS_ROUTE reste visible, le blocage est purement logique.
    # Pour les rendre visibles, on peut faire :
     for y in range(len(grille)):
         for x in range(len(grille[0])):
             if grille[y][x] == OBSTACLE_AUTO_SYM:
                 # Exemple : un carré rouge/orange pour indiquer travaux ou accident
                 pygame.draw.rect(fenetre, (255, 80, 0), (x * taille_cellule, y * taille_cellule, taille_cellule, taille_cellule), 2) # Bordure orange
                 # Peut aussi ajouter une icône ou hachures
                 pass # Ne dessine rien de visible par défaut, comme des ralentissements invisibles.
     pass # Pas de dessin visible pour OBSTACLE_AUTO_SYM par défaut. Ils sont des blocages logiques.


##
# @brief Dessine les feux de circulation.
# @param fenetre Surface Pygame.
# @param feux Liste des feux.
# @param taille_cellule Taille d'une cellule.
def dessiner_feux(fenetre: pygame.Surface, feux: List[Dict[str, Any]], taille_cellule: int) -> None:
    for feu in feux:
        x, y = feu["position"]
        dc = taille_cellule // 2
        cx = x * taille_cellule + dc
        cy = y * taille_cellule + dc
        rayon = max(3, taille_cellule // 8)
        espacement_vertical = int(rayon * 2.2)
        epaisseur_contour = 1
        etat_actuel = feu["etat"]
        couleur_inactive = GRIS_FONCE
        couleur_r = ROUGE if etat_actuel == "rouge" else couleur_inactive
        couleur_o = ORANGE if etat_actuel == "orange" else couleur_inactive
        couleur_v = VERT if etat_actuel == "vert" else couleur_inactive
        centre_r, centre_o, centre_v = (cx, cy - espacement_vertical), (cx, cy), (cx, cy + espacement_vertical)

        pygame.draw.circle(fenetre, couleur_r, centre_r, rayon)
        pygame.draw.circle(fenetre, couleur_o, centre_o, rayon)
        pygame.draw.circle(fenetre, couleur_v, centre_v, rayon)

        if epaisseur_contour > 0:
            pygame.draw.circle(fenetre, NOIR, centre_r, rayon, epaisseur_contour)
            pygame.draw.circle(fenetre, NOIR, centre_o, rayon, epaisseur_contour)
            pygame.draw.circle(fenetre, NOIR, centre_v, rayon, epaisseur_contour)

##
# @brief Dessine les indicateurs de sens de circulation sur les bords de la grille.
# @param fenetre Surface Pygame.
# @param directions_lignes Dict directions lignes.
# @param directions_colonnes Dict directions colonnes.
# @param taille_x Largeur grille.
# @param taille_y Hauteur grille.
# @param taille_cellule Taille cellule.
def dessiner_directions(fenetre: pygame.Surface, directions_lignes: Dict[int, str], directions_colonnes: Dict[int, str], taille_x: int, taille_y: int, taille_cellule: int) -> None:
    taille_fleche = taille_cellule * 0.3
    decalage_centre = taille_cellule // 2
    couleur_fleche = NOIR
    epaisseur = 2
    taille_pointe, largeur_pointe = 6, 4

    # Lignes
    for y, direction in directions_lignes.items():
        if any(grille[y][x] != NON_ROUTIER for x in range(taille_x)): # Dessine si la ligne contient une route
            cy = y * taille_cellule + decalage_centre
            if direction == "droite":
                cx_depart = 0 # Bord gauche de la grille
                sp, ep = (cx_depart + decalage_centre - taille_fleche / 2, cy), (cx_depart + decalage_centre + taille_fleche / 2, cy)
                pygame.draw.line(fenetre, couleur_fleche, sp, ep, epaisseur)
                pygame.draw.polygon(fenetre, couleur_fleche, [(ep), (ep[0] - taille_pointe, ep[1] - largeur_pointe), (ep[0] - taille_pointe, ep[1] + largeur_pointe)])
            elif direction == "gauche":
                cx_depart = (taille_x - 1) * taille_cellule # Bord droit de la grille
                sp, ep = (cx_depart + decalage_centre + taille_fleche / 2, cy), (cx_depart + decalage_centre - taille_fleche / 2, cy)
                pygame.draw.line(fenetre, couleur_fleche, sp, ep, epaisseur)
                pygame.draw.polygon(fenetre, couleur_fleche, [(ep), (ep[0] + taille_pointe, ep[1] - largeur_pointe), (ep[0] + taille_pointe, ep[1] + largeur_pointe)])
    # Colonnes
    for x, direction in directions_colonnes.items():
         if any(grille[y][x] != NON_ROUTIER for y in range(taille_y)): # Dessine si la colonne contient une route
            cx = x * taille_cellule + decalage_centre
            if direction == "bas":
                cy_depart = 0 # Bord haut de la grille
                sp, ep = (cx, cy_depart + decalage_centre - taille_fleche / 2), (cx, cy_depart + decalage_centre + taille_fleche / 2)
                pygame.draw.line(fenetre, couleur_fleche, sp, ep, epaisseur)
                pygame.draw.polygon(fenetre, couleur_fleche, [(ep), (ep[0] - largeur_pointe, ep[1] - taille_pointe), (ep[0] + largeur_pointe, ep[1] - taille_pointe)])
            elif direction == "haut":
                cy_depart = (taille_y - 1) * taille_cellule # Bord bas de la grille
                sp, ep = (cx, cy_depart + decalage_centre + taille_fleche / 2), (cx, cy_depart + decalage_centre - taille_fleche / 2)
                pygame.draw.line(fenetre, couleur_fleche, sp, ep, epaisseur)
                pygame.draw.polygon(fenetre, couleur_fleche, [(ep), (ep[0] - largeur_pointe, ep[1] + taille_pointe), (ep[0] + largeur_pointe, ep[1] + taille_pointe)])

##
# @brief Dessine les passages piétons.
# @param fenetre Surface Pygame.
# @param passages Liste des passages piétons.
# @param taille_cellule Taille cellule.
# @param couleur Couleur des zébrures.
# @param largeur_zebre Epaisseur des zébrures.
def dessiner_passages_pietons(fenetre: pygame.Surface, passages: List[Dict[str, Any]], taille_cellule: int, couleur: Tuple[int, int, int], largeur_zebre: int=5) -> None:
    marge = taille_cellule // 6
    for passage in passages:
        x_cell, y_cell = passage['position']
        orientation = passage['orientation']
        cell_rect = pygame.Rect(x_cell * taille_cellule, y_cell * taille_cellule, taille_cellule, taille_cellule)

        if orientation == 'horizontal':
            y_debut, y_fin = cell_rect.top + marge, cell_rect.bottom - marge
            x_courant = cell_rect.left + marge
            while x_courant < cell_rect.right - marge:
                 pygame.draw.line(fenetre, couleur, (x_courant, y_debut), (x_courant, y_fin), largeur_zebre)
                 x_courant += largeur_zebre * 2
        else: # Vertical
             x_debut, x_fin = cell_rect.left + marge, cell_rect.right - marge
             y_courant = cell_rect.top + marge
             while y_courant < cell_rect.bottom - marge:
                 pygame.draw.line(fenetre, couleur, (x_debut, y_courant), (x_fin, y_courant), largeur_zebre)
                 y_courant += largeur_zebre * 2

##
# @brief Dessine les piétons actifs.
# @param fenetre Surface Pygame.
# @param pietons Liste des piétons actifs.
# @param taille_cellule Taille cellule.
# @param couleur Couleur du bonhomme.
# @param epaisseur_ligne Epaisseur des traits.
def dessiner_pietons(fenetre: pygame.Surface, pietons: List[Dict[str, Any]], taille_cellule: int, couleur: Tuple[int, int, int], epaisseur_ligne: int=2) -> None:
    demi_cellule_px = taille_cellule // 2
    # Ratios pour dessiner un bonhomme allumette simple
    head_radius_ratio, torso_height_ratio, limb_length_ratio = 0.10, 0.25, 0.20
    head_radius = max(2, int(taille_cellule * head_radius_ratio))
    torso_dy = max(3, int(taille_cellule * torso_height_ratio))
    limb_len = max(3, int(taille_cellule * limb_length_ratio))

    for pieton in pietons:
        x_cell, y_cell = pieton['passage_pos']
        orientation, progres = pieton['orientation'], pieton['progres']
        # Centre de la cellule
        cx_cell_px, cy_cell_px = x_cell * taille_cellule + demi_cellule_px, y_cell * taille_cellule + demi_cellule_px

        # Position actuelle interpolée du piéton (entre les bords du passage)
        px, py = cx_cell_px, cy_cell_px # Default to center if no movement occurs (progres = 0)

        if orientation == 'horizontal':
            # Le piéton se déplace horizontalement le long du passage
            # Décalage horizontal basé sur la marge du dessin du passage piéton pour s'aligner avec les zébrures
            marge_passage_px = taille_cellule // 6 + head_radius # Ajoute le rayon de la tête pour ne pas sortir
            start_x, end_x = x_cell * taille_cellule + marge_passage_px, (x_cell + 1) * taille_cellule - marge_passage_px
            px = start_x + (end_x - start_x) * progres
            py = y_cell * taille_cellule + demi_cellule_px # Reste centré verticalement dans la cellule

        else: # Vertical
             # Le piéton se déplace verticalement
             # Décalage vertical basé sur la marge des zébrures + rayon tête
             marge_passage_px = taille_cellule // 6 + head_radius # Ajoute le rayon de la tête pour ne pas sortir
             start_y, end_y = y_cell * taille_cellule + marge_passage_px, (y_cell + 1) * taille_cellule - marge_passage_px
             py = start_y + (end_y - start_y) * progres
             px = x_cell * taille_cellule + demi_cellule_px # Reste centré horizontalement

        # Position de dessin (au centre de la silhouette du bonhomme)
        center_x, center_y = int(px), int(py)

        # Calcul des points pour dessiner le bonhomme allumette relatif à center_x, center_y
        head_center_y = center_y - (torso_dy // 2) - head_radius
        head_pos = (center_x, head_center_y)
        torso_top_y = center_y - (torso_dy // 2)
        torso_bottom_y = center_y + (torso_dy // 2)
        torso_start, torso_end = (center_x, torso_top_y), (center_x, torso_bottom_y)
        shoulder_y = torso_top_y + int(torso_dy * 0.1)
        shoulder_point = (center_x, shoulder_y)
        hip_point = torso_end
        arm_angle_offset_x = int(limb_len * 0.7)
        arm_end_y = shoulder_y + int(limb_len * 0.7)
        left_arm_end, right_arm_end = (center_x - arm_angle_offset_x, arm_end_y), (center_x + arm_angle_offset_x, arm_end_y)
        leg_angle_offset_x = int(limb_len * 0.5)
        leg_end_y = torso_bottom_y + limb_len
        left_leg_end, right_leg_end = (center_x - leg_angle_offset_x, leg_end_y), (center_x + leg_angle_offset_x, leg_end_y)

        # Dessin du bonhomme
        pygame.draw.circle(fenetre, couleur, head_pos, head_radius)
        pygame.draw.line(fenetre, couleur, torso_start, torso_end, epaisseur_ligne)
        pygame.draw.line(fenetre, couleur, shoulder_point, left_arm_end, epaisseur_ligne)
        pygame.draw.line(fenetre, couleur, shoulder_point, right_arm_end, epaisseur_ligne)
        pygame.draw.line(fenetre, couleur, hip_point, left_leg_end, epaisseur_ligne)
        pygame.draw.line(fenetre, couleur, hip_point, right_leg_end, epaisseur_ligne)


##
# @brief Dessine les voitures (image ou cercle).
# Gère l'affichage avec l'orientation et l'ID de la voiture. Gère la phase de disparition.
# @param fenetre Surface Pygame.
# @param voitures Liste des voitures (inclut actives et en disparition).
# @param taille_cellule Taille cellule.
def dessiner_voitures(fenetre: pygame.Surface, voitures: List[Dict[str, Any]], taille_cellule: int) -> None:
    temps_actuel = time.time() # Temps actuel pour gérer le délai de disparition
    font_pour_id = pygame.font.Font(None, 16) # Police pour afficher l'ID

    # Couleurs pour l'ID de la voiture, contrastées selon le fond probable (image colorée ou cercle)
    couleur_texte_sur_image = BLANC # Utile si l'image colorée est foncée
    couleur_texte_sur_cercle = NOIR # Utile si le cercle est de couleur claire

    # Décalage pour centrer l'objet voiture/cercle dans sa cellule
    centre_cellule_decalage = taille_cellule // 2

    # Angle par défaut quand une voiture est considérée comme "garée" (atteint sa destination finale et commence sa phase de disparition)
    ANGLE_GAREE = 90 # Orienter la voiture vers le "haut" (Nord, ou face à la zone non routière derrière la place de parking)

    # Itère sur TOUTES les voitures dans la liste, y compris celles en phase de disparition.
    for voiture in voitures:
        # Condition pour dessiner la voiture : soit elle est encore en route, soit elle est arrivée
        # et le temps écoulé depuis son arrivée est inférieur au délai de disparition.
        est_active = voiture.get("temps_arrivee") is None # Est active si temps_arrivee est None
        est_en_disparition = voiture.get("temps_arrivee") is not None and (temps_actuel - voiture["temps_arrivee"] < DELAI_DISPARITION_APRES_ARRIVEE)

        if est_active or est_en_disparition:
            # Récupère la position [x, y] de la voiture dans la grille
            x_grid, y_grid = voiture["position"]

            # Calcule les coordonnées centrales en pixels pour le dessin dans la cellule
            centre_x_px = x_grid * taille_cellule + centre_cellule_decalage
            centre_y_px = y_grid * taille_cellule + centre_cellule_decalage

            # Essaie d'utiliser l'image de voiture spécifique à cette voiture (déjà colorée et redimensionnée)
            image_specifique_voiture = voiture.get("image")

            if image_specifique_voiture:
                # --- Dessine l'image de la voiture ---
                # Détermine l'angle d'orientation. Utilise l'angle de mouvement habituel,
                # mais passe à l'angle "garée" si elle est arrivée et à sa destination finale.
                angle_final_rotation = ANGLE_GAREE if voiture.get("temps_arrivee") is not None and tuple(voiture["position"]) == tuple(voiture["destination"]) else voiture.get("orientation", 0)

                # Fait tourner l'image à l'angle souhaité
                image_rotatee = pygame.transform.rotate(image_specifique_voiture, angle_final_rotation)
                # Obtient le rectangle de l'image après rotation pour la positionner correctement par son centre
                rect_image_rotatee = image_rotatee.get_rect(center=(centre_x_px, centre_y_px))

                # Dessine l'image rotatée sur la fenêtre
                fenetre.blit(image_rotatee, rect_image_rotatee)

                # Dessine l'ID de la voiture (centré sur l'image)
                texte_id_surface = font_pour_id.render(str(voiture["id"]), True, couleur_texte_sur_image)
                rect_texte_id = texte_id_surface.get_rect(center=rect_image_rotatee.center) # Centre le texte sur l'image
                fenetre.blit(texte_id_surface, rect_texte_id)

            else:
                # --- Si l'image n'est pas disponible, dessine un cercle de fallback ---
                rayon_cercle = centre_cellule_decalage - 5 # Un peu plus petit que la demi-cellule pour la marge
                couleur_du_cercle = voiture.get("couleur", NOIR) # Utilise la couleur définie pour la voiture ou noir par défaut

                # Dessine le cercle
                pygame.draw.circle(fenetre, couleur_du_cercle, (centre_x_px, centre_y_px), rayon_cercle)

                # Dessine l'ID de la voiture (centré sur le cercle)
                texte_id_surface = font_pour_id.render(str(voiture["id"]), True, couleur_texte_sur_cercle)
                rect_texte_id = texte_id_surface.get_rect(center=(centre_x_px, centre_y_px)) # Centre le texte sur le cercle
                fenetre.blit(texte_id_surface, rect_texte_id)

##
# @brief Dessine des indicateurs visuels pour les destinations des voitures.
# Affiche les destinations uniquement pour les voitures qui ne sont PAS arrivées.
# @param fenetre Surface Pygame.
# @param voitures Liste des voitures.
# @param taille_cellule Taille cellule.
# @param couleur_lignes Couleur des lignes "parking".
# @param epaisseur_lignes Epaisseur des lignes.
def dessiner_destinations(fenetre: pygame.Surface, voitures: List[Dict[str, Any]], taille_cellule: int, couleur_lignes: Tuple[int, int, int], epaisseur_lignes: int=2) -> None:
    font = pygame.font.Font(None, 16)
    font_color_id = NOIR # Couleur de l'ID de la voiture
    # Ratios pour la taille de l'indicateur par rapport à la cellule
    marge_laterale_ratio, marge_haut_ratio, marge_bas_ratio = 0.15, 0.15, 0.40
    # Paramètres du pointillé pour la ligne arrière
    longueur_pointille = max(4, taille_cellule // 10)
    espace_pointille = max(3, taille_cellule // 15)

    # Stocke les destinations uniques actuellement visibles avec l'ID d'une des voitures y allant.
    destinations_visibles: Dict[Tuple[int, int], int] = {}

    # Collecte les destinations des voitures *actives* (qui ne sont pas encore arrivées)
    for v in voitures:
        # N'affiche la destination que si la voiture est toujours en route
        if v.get("temps_arrivee") is None:
            dest_tuple = tuple(v["destination"])
            # S'assure de ne stocker qu'une seule entrée par position de destination unique
            if dest_tuple not in destinations_visibles:
                destinations_visibles[dest_tuple] = v["id"]

    # Dessine les indicateurs pour chaque destination unique visible
    for dest_pos, voiture_id in destinations_visibles.items():
        dx, dy = dest_pos
        # Calcule les coordonnées en pixels du coin supérieur gauche de la cellule
        cell_x_px, cell_y_px = dx * taille_cellule, dy * taille_cellule

        # Vérifie si la destination est toujours sur une ROUTE praticable (un obstacle manuel/auto pourrait y avoir été placé)
        # Si non, ne dessine pas l'indicateur.
        if 0 <= dy < len(grille) and 0 <= dx < len(grille[0]) and grille[dy][dx] == ROUTE:
            # Calcul des positions en pixels pour les lignes de "parking"
            marge_laterale_px = int(taille_cellule * marge_laterale_ratio)
            marge_haut_px = int(taille_cellule * marge_haut_ratio)
            marge_bas_px = int(taille_cellule * marge_bas_ratio)

            # Coordonnées pixel des lignes (relativement à la cellule)
            ligne_gauche_x = cell_x_px + marge_laterale_px
            ligne_droite_x = cell_x_px + taille_cellule - marge_laterale_px
            ligne_haut_y = cell_y_px + marge_haut_px
            ligne_bas_y = cell_y_px + taille_cellule - marge_bas_px # Ligne "basse" (côté où la voiture se garerait face au "mur")

            # Dessin des lignes latérales et de la ligne arrière (souvent pointillée)
            pygame.draw.line(fenetre, couleur_lignes, (ligne_gauche_x, ligne_haut_y), (ligne_gauche_x, ligne_bas_y), epaisseur_lignes) # Ligne gauche
            pygame.draw.line(fenetre, couleur_lignes, (ligne_droite_x, ligne_haut_y), (ligne_droite_x, ligne_bas_y), epaisseur_lignes) # Ligne droite

            # Ligne arrière (pointillée)
            ligne_arriere_y = ligne_bas_y # C'est le côté "mur", la voiture se garerait contre ce bord visuellement
            ligne_arriere_debut_x = ligne_gauche_x
            ligne_arriere_fin_x = ligne_droite_x
            # Boucle pour dessiner les tirets de la ligne pointillée
            x_courant = ligne_arriere_debut_x
            while x_courant < ligne_arriere_fin_x:
                x_fin_tiret = min(x_courant + longueur_pointille, ligne_arriere_fin_x) # Assure que le dernier tiret ne dépasse pas
                pygame.draw.line(fenetre, couleur_lignes, (x_courant, ligne_arriere_y), (x_fin_tiret, ligne_arriere_y), epaisseur_lignes)
                x_courant += longueur_pointille + espace_pointille # Espace entre les tirets


            # Dessin de l'ID de la voiture associée (centré dans l'espace de la "place")
            centre_id_x = (ligne_gauche_x + ligne_droite_x) // 2
            centre_id_y = (ligne_haut_y + ligne_bas_y) // 2
            txt_surface = font.render(str(voiture_id), True, font_color_id)
            text_rect = txt_surface.get_rect(center=(centre_id_x, centre_id_y))
            fenetre.blit(txt_surface, text_rect)



# --- FONCTIONS DESSIN DÉCORATIONS (sur NON_ROUTIER) ---

##
# @brief Dessine des arbres simples (tronc + feuillage) sur des positions spécifiques si elles sont NON_ROUTIER.
# @param fenetre Surface Pygame.
# @param positions_arbres Liste de tuples (x, y).
# @param grille La grille (pour vérifier NON_ROUTIER).
# @param taille_cellule Taille cellule.
def dessiner_arbres(fenetre: pygame.Surface, positions_arbres: List[Tuple[int, int]], grille: List[List[str]], taille_cellule: int) -> None:
    for pos in positions_arbres:
        x, y = pos
        if 0 <= y < len(grille) and 0 <= x < len(grille[0]) and grille[y][x] == NON_ROUTIER:
            cell_x_px, cell_y_px = x * taille_cellule, y * taille_cellule
            # Dimensions
            tronc_largeur = int(taille_cellule * 0.15)
            tronc_hauteur = int(taille_cellule * 0.4)
            feuillage_rayon = int(taille_cellule * 0.3)
            # Positionnement (ancre bas-milieu du tronc sur bas-milieu cellule, puis positionne feuillage)
            tronc_x = cell_x_px + taille_cellule // 2 - tronc_largeur // 2
            tronc_y = cell_y_px + taille_cellule - tronc_hauteur # Tronc en bas de la cellule
            tronc_rect = pygame.Rect(tronc_x, tronc_y, tronc_largeur, tronc_hauteur)
            feuillage_cx = cell_x_px + taille_cellule // 2
            feuillage_cy = tronc_y - int(feuillage_rayon * 0.5) # Feuillage un peu au dessus du tronc

            pygame.draw.rect(fenetre, MARRON_TRONC, tronc_rect)
            pygame.draw.circle(fenetre, VERT_FEUILLAGE, (feuillage_cx, feuillage_cy), feuillage_rayon)


##
# @brief Dessine des maisons simples sur des positions spécifiques si elles sont NON_ROUTIER.
# @param fenetre Surface Pygame.
# @param positions_maisons Liste de tuples (x, y).
# @param grille La grille (pour vérifier NON_ROUTIER).
# @param taille_cellule Taille cellule.
def dessiner_maisons(fenetre: pygame.Surface, positions_maisons: List[Tuple[int, int]], grille: List[List[str]], taille_cellule: int) -> None:
    for pos in positions_maisons:
        x, y = pos
        if 0 <= y < len(grille) and 0 <= x < len(grille[0]) and grille[y][x] == NON_ROUTIER:
            cell_x_px, cell_y_px = x * taille_cellule, y * taille_cellule
            # Ratios dimensionnels
            marge_horizontale = int(taille_cellule * 0.15)
            marge_bas = int(taille_cellule * 0.1)
            hauteur_mur_ratio = 0.65
            # Hauteur totale maison ~ 100% - marge_bas
            hauteur_mur = int(taille_cellule * hauteur_mur_ratio)
            hauteur_toit = taille_cellule - hauteur_mur - marge_bas

            # Mur (rectangle)
            mur_largeur = taille_cellule - 2 * marge_horizontale
            mur_x = cell_x_px + marge_horizontale
            mur_y = cell_y_px + taille_cellule - hauteur_mur - marge_bas
            mur_rect = pygame.Rect(mur_x, mur_y, mur_largeur, hauteur_mur)
            pygame.draw.rect(fenetre, BRUN_MUR, mur_rect)

            # Toit (triangle au-dessus du mur)
            sommet_toit_x = mur_x + mur_largeur // 2
            sommet_toit_y = mur_y - hauteur_toit
            base_gauche_x, base_gauche_y = mur_x, mur_y
            base_droite_x, base_droite_y = mur_x + mur_largeur, mur_y
            toit_points = [(sommet_toit_x, sommet_toit_y), (base_gauche_x, base_gauche_y), (base_droite_x, base_droite_y)]
            pygame.draw.polygon(fenetre, ROUGE_TOIT, toit_points)


##
# @brief Dessine une représentation simple d'école sur les positions spécifiées si elles sont NON_ROUTIER.
# @param fenetre Surface Pygame.
# @param positions_ecoles Liste de tuples (x, y).
# @param grille La grille (pour vérifier NON_ROUTIER).
# @param taille_cellule Taille cellule.
def dessiner_ecoles(fenetre: pygame.Surface, positions_ecoles: List[Tuple[int, int]], grille: List[List[str]], taille_cellule: int) -> None:
    for pos in positions_ecoles:
        x, y = pos
        if 0 <= y < len(grille) and 0 <= x < len(grille[0]) and grille[y][x] == NON_ROUTIER:
            cell_x_px, cell_y_px = x * taille_cellule, y * taille_cellule

            # Bâtiment principal (Rectangle)
            marge_bas_mur = int(taille_cellule * 0.1)
            hauteur_mur = int(taille_cellule * 0.6)
            largeur_mur = int(taille_cellule * 0.8)
            marge_laterale_mur = (taille_cellule - largeur_mur) // 2

            mur_x = cell_x_px + marge_laterale_mur
            mur_y = cell_y_px + taille_cellule - hauteur_mur - marge_bas_mur
            mur_rect = pygame.Rect(mur_x, mur_y, largeur_mur, hauteur_mur)
            pygame.draw.rect(fenetre, COULEUR_ECOLE_MUR, mur_rect)

            # Toit (Triangle Gable)
            hauteur_toit = int(taille_cellule * 0.3)
            sommet_toit_x = mur_x + largeur_mur // 2
            sommet_toit_y = mur_y - hauteur_toit
            base_gauche_x, base_gauche_y = mur_x, mur_y
            base_droite_x, base_droite_y = mur_x + largeur_mur, mur_y
            toit_points = [(sommet_toit_x, sommet_toit_y), (base_gauche_x, base_gauche_y), (base_droite_x, base_droite_y)]
            pygame.draw.polygon(fenetre, COULEUR_ECOLE_TOIT, toit_points)

            # Fenêtres (Rectangles) - Positionnées sur le mur
            fenetre_largeur = int(largeur_mur * 0.2)
            fenetre_hauteur = int(hauteur_mur * 0.3)
            marge_entre_fenetres = int(largeur_mur * 0.15)
            fenetre1_x = mur_x + (largeur_mur - 2 * fenetre_largeur - marge_entre_fenetres) // 2
            fenetre_y = mur_y + int(hauteur_mur * 0.2) # Partie supérieure du mur
            fenetre2_x = fenetre1_x + fenetre_largeur + marge_entre_fenetres
            pygame.draw.rect(fenetre, COULEUR_ECOLE_FENETRE, (fenetre1_x, fenetre_y, fenetre_largeur, fenetre_hauteur))
            pygame.draw.rect(fenetre, COULEUR_ECOLE_FENETRE, (fenetre2_x, fenetre_y, fenetre_largeur, fenetre_hauteur))

            # Porte (Rectangle) - Positionnée au centre en bas du mur
            porte_largeur = int(largeur_mur * 0.25)
            porte_hauteur = int(hauteur_mur * 0.4)
            porte_x = mur_x + (largeur_mur - porte_largeur) // 2
            porte_y = mur_y + hauteur_mur - porte_hauteur - 2 # Légèrement relevée du bas
            pygame.draw.rect(fenetre, COULEUR_ECOLE_PORTE, (porte_x, porte_y, porte_largeur, porte_hauteur))

##
# @brief Dessine des massifs montagneux avec eau à leur base sur les positions spécifiées si elles sont NON_ROUTIER.
# Le dessin s'étend dans les cellules NON_ROUTIER situées directement au-dessus de la cellule de base d'eau donnée.
# @param fenetre Surface Pygame.
# @param positions_base_eau Liste de tuples (x, y) des cellules base d'eau/montagne.
# @param grille La grille (pour vérifier NON_ROUTIER au-dessus).
# @param taille_cellule Taille cellule.
def dessiner_montagne_avec_eau(fenetre: pygame.Surface, positions_base_eau: List[Tuple[int, int]], grille: List[List[str]], taille_cellule: int) -> None:
    taille_x_grille = len(grille[0])
    taille_y_grille = len(grille)

    for pos_base in positions_base_eau:
        x_base, y_base = pos_base
        # S'assure que la position de base est valide et sur une zone non-routière ('N')
        if not (0 <= y_base < taille_y_grille and 0 <= x_base < taille_x_grille and grille[y_base][x_base] == NON_ROUTIER):
             continue # Ignore cette position si non valide

        # Coordonnées pixel du coin supérieur gauche de la cellule de base
        cell_x_base_px, cell_y_base_px = x_base * taille_cellule, y_base * taille_cellule
        # Centre horizontal de la cellule de base
        centre_x_cell_base_px = cell_x_base_px + taille_cellule // 2
        # La limite supérieure de la cellule de base représente le "niveau de l'eau" visuel.
        niveau_eau_y_px = cell_y_base_px

        # --- Dessin de l'Eau ---
        # Le rectangle de l'eau remplit la cellule de base.
        pygame.draw.rect(fenetre, COULEUR_EAU, (cell_x_base_px, cell_y_base_px, taille_cellule, taille_cellule -25))

        # --- Détermination de la hauteur du massif montagneux ---
        # On compte les cellules NON_ROUTIER empilées verticalement au-dessus de la cellule de base (x_base, y_base).
        ligne_y_pic_potentiel = y_base # Commence au niveau de la cellule de base
        cellules_non_routières_au_dessus = 0 # Compteur

        y_courant_check = y_base - 1 # Commence à vérifier la cellule juste au-dessus
        while y_courant_check >= 0 and grille[y_courant_check][x_base] == NON_ROUTIER:
            cellules_non_routières_au_dessus += 1
            ligne_y_pic_potentiel = y_courant_check # La ligne la plus haute atteinte par les cellules NON_ROUTIER empilées
            y_courant_check -= 1 # Continue de monter

        # --- Dessin de la Montagne (Roc et Neige) si des cellules NON_ROUTIER sont trouvées au-dessus ---
        if cellules_non_routières_au_dessus > 0:
            # La position Y pixel correspondant au sommet *potentiel* maximum du massif.
            # C'est la ligne supérieure de la cellule la plus haute non-routière empilée.
            limite_y_pic_px = ligne_y_pic_potentiel * taille_cellule

            # Rocher : dessiné comme un triangle ancré à la base d'eau, montant jusqu'à un pic rocheux.
            largeur_base_roc_px = int(taille_cellule * (1 + cellules_non_routières_au_dessus * 0.09)) # La base peut s'élargir avec la hauteur
            # Position Y pixel du pic rocheux : Ancré un peu en dessous de la limite maximale. Sa hauteur est liée au nombre de cellules.
            pos_y_pic_roc_px = limite_y_pic_px + int(taille_cellule * (cellules_non_routières_au_dessus * 0.4 + 0.1))

            # Points du triangle de roc (pic centré, base aux niveaux de l'eau)
            points_roc = [
                (centre_x_cell_base_px - largeur_base_roc_px // 2, niveau_eau_y_px),
                (centre_x_cell_base_px + largeur_base_roc_px // 2, niveau_eau_y_px),
                (centre_x_cell_base_px, pos_y_pic_roc_px)
            ]
            # S'assure que le pic du roc ne descend pas en dessous du niveau de l'eau
            points_roc[2] = (points_roc[2][0], min(points_roc[2][1], niveau_eau_y_px)) # Le pic roc est toujours au-dessus de l'eau.

            pygame.draw.polygon(fenetre, COULEUR_MONTAGNE_ROCHE, points_roc)

            # Neige : dessiné comme un triangle plus étroit sur le pic rocheux, montant plus haut vers le pic max.
            largeur_base_neige_px = int(largeur_base_roc_px * 0.5) # La base de la neige est sur le roc
            # Position Y pixel du pic neigeux : Proche ou au niveau de la limite max.
            pos_y_pic_neige_px = limite_y_pic_px + int(taille_cellule * (cellules_non_routières_au_dessus * 0.2)) # Un peu au dessus du roc peak

            # Points du triangle de neige (pic centré, base au niveau du pic rocheux)
            points_neige = [
                (centre_x_cell_base_px - largeur_base_neige_px // 2, pos_y_pic_roc_px), # Ancré sur le pic roc
                (centre_x_cell_base_px + largeur_base_neige_px // 2, pos_y_pic_roc_px),
                (centre_x_cell_base_px, pos_y_pic_neige_px)
            ]
            # S'assure que le pic neigeux ne monte pas au-dessus de la limite pixel calculée pour le pic max
            points_neige[2] = (points_neige[2][0], max(limite_y_pic_px, points_neige[2][1]))

            pygame.draw.polygon(fenetre, COULEUR_MONTAGNE_NEIGE, points_neige)

        # else: S'il n'y a PAS de cellules NON_ROUTIER directement au-dessus
        else:
             # Dessine un petit monticule rocheux bas qui reste DANS la cellule de base d'eau.
             largeur_monticule_px = int(taille_cellule * 0.7)
             hauteur_monticule_px = int(taille_cellule * 0.4)
             # Position Y pixel du pic du monticule : En dessous du niveau de l'eau pour donner l'impression d'être partiellement submergé.
             pos_y_pic_monticule_px = niveau_eau_y_px + hauteur_monticule_px # Pic en bas de la base eau Y.

             points_monticule_roc = [
                 (centre_x_cell_base_px - largeur_monticule_px // 2, niveau_eau_y_px), # Ancré à la base de l'eau
                 (centre_x_cell_base_px + largeur_monticule_px // 2, niveau_eau_y_px), # Ancré à la base de l'eau
                 (centre_x_cell_base_px, pos_y_pic_monticule_px)
             ]
             # Dessine le petit monticule rocheux dans la cellule d'eau.
             pygame.draw.polygon(fenetre, COULEUR_MONTAGNE_ROCHE, points_monticule_roc)

##
# @brief Dessine des représentations simples de fleurs sur les positions spécifiées si elles sont NON_ROUTIER.
# Dessine une tige verte et quelques "pétales" circulaires avec un centre.
# @param fenetre Surface Pygame.
# @param positions_fleurs Liste de tuples (x, y) des cellules où dessiner les fleurs.
# @param grille La grille (pour vérifier NON_ROUTIER).
# @param taille_cellule Taille cellule.
def dessiner_fleurs(fenetre: pygame.Surface, positions_fleurs: List[Tuple[int, int]], grille: List[List[str]], taille_cellule: int) -> None:
    # Dimensions et propriétés des éléments de la fleur, basées sur la taille de la cellule
    rayon_petale = max(1, int(taille_cellule * 0.08)) # Rayon des petits cercles pour les pétales
    rayon_centre_fleur = max(1, int(taille_cellule * 0.04)) # Rayon du cercle central
    hauteur_tige_ratio = 0.5 # La tige s'étend sur environ la moitié de la cellule vers le bas.
    epaisseur_tige = max(1, int(taille_cellule * 0.03)) # Epaisseur du trait de la tige
    decalage_petales_du_centre = max(2, int(taille_cellule * 0.1)) # Distance entre le centre et chaque pétale
    # Décalage léger aléatoire par fleur pour varier un peu le positionnement dans la cellule
    # décalage_aleatoire_x = random.randint(-int(taille_cellule * 0.05), int(taille_cellule * 0.05))
    # décalage_aleatoire_y = random.randint(-int(taille_cellule * 0.05), int(taille_cellule * 0.05))

    taille_x_grille = len(grille[0])
    taille_y_grille = len(grille)

    for pos in positions_fleurs:
        x, y = pos
        # S'assure que la position est valide et bien sur une zone non-routière ('N')
        if not (0 <= y < taille_y_grille and 0 <= x < taille_x_grille and grille[y][x] == NON_ROUTIER):
            continue # Ignore si pas valide ou pas sur une zone NON_ROUTIER.

        # Coordonnées pixel du coin supérieur gauche de la cellule
        cell_x_px, cell_y_px = x * taille_cellule, y * taille_cellule
        # Calcule le centre exact de la cellule
        centre_cellule_x_px = cell_x_px + taille_cellule // 2
        centre_cellule_y_px = cell_y_px + taille_cellule // 2

        # Position centrale pour le dessin de la fleur (peut appliquer les décalages aléatoires ici)
        centre_dessin_x = centre_cellule_x_px # + décalage_aleatoire_x # Avec décalage aléatoire
        centre_dessin_y = centre_cellule_y_px # + décalage_aleatoire_y # Avec décalage aléatoire


        # --- Dessin de la Tige ---
        # La tige descend du centre visuel de la fleur vers le bas de la cellule (avec une petite marge).
        pos_y_debut_tige_px = centre_dessin_y # Démarre au centre Y de la fleur
        pos_y_fin_tige_px = (y + 1) * taille_cellule - int(taille_cellule * 0.15) # Finit près du bord bas de la cellule
        # La tige est une ligne verticale à la position horizontale du centre de dessin de la fleur.
        pygame.draw.line(fenetre, COULEUR_FLEUR_VERT, (centre_dessin_x, pos_y_debut_tige_px), (centre_dessin_x, pos_y_fin_tige_px), epaisseur_tige)

        # Optionnel : ajouter des feuilles simples sur la tige
        # petit_feuille_largeur = int(epaisseur_tige * 4)
        # petit_feuille_hauteur = int(epaisseur_tige * 2)
        # decalage_feuille_y_depuis_centre = int(hauteur_tige_ratio * taille_cellule * 0.4)
        # pygame.draw.ellipse(fenetre, COULEUR_FLEUR_VERT, pygame.Rect(centre_dessin_x - epaisseur_tige - petit_feuille_largeur, centre_dessin_y + decalage_feuille_y_depuis_centre, petit_feuille_largeur, petit_feuille_hauteur)) # Feuille gauche
        # pygame.draw.ellipse(fenetre, COULEUR_FLEUR_VERT, pygame.Rect(centre_dessin_x + epaisseur_tige, centre_dessin_y + decalage_feuille_y_depuis_centre, petit_feuille_largeur, petit_feuille_hauteur)) # Feuille droite


        # --- Dessin des Pétales ---
        # Dessine des pétales (des cercles) autour du centre de dessin de la fleur.
        # On utilise 4 pétales dans les directions cardinales simples (haut, bas, gauche, droite).
        pygame.draw.circle(fenetre, COULEUR_FLEUR_ROSE, (centre_dessin_x, centre_dessin_y - decalage_petales_du_centre), rayon_petale) # Pétale Nord
        pygame.draw.circle(fenetre, COULEUR_FLEUR_ROSE, (centre_dessin_x, centre_dessin_y + decalage_petales_du_centre), rayon_petale) # Pétale Sud
        pygame.draw.circle(fenetre, COULEUR_FLEUR_ROSE, (centre_dessin_x - decalage_petales_du_centre, centre_dessin_y), rayon_petale) # Pétale Ouest
        pygame.draw.circle(fenetre, COULEUR_FLEUR_ROSE, (centre_dessin_x + decalage_petales_du_centre, centre_dessin_y), rayon_petale) # Pétale Est

        # --- Dessin du Centre de la fleur ---
        # Dessiné après les pétales pour qu'il soit par-dessus eux.
        pygame.draw.circle(fenetre, (255, 200, 0), (centre_dessin_x, centre_dessin_y), rayon_centre_fleur) # Centre (Jaune/Orange)


# --- INITIALISATION ET BOUCLE PRINCIPALE ---

# Configuration de la grille et des éléments permanents
grille = creer_grille(TAILLE_X_GRILLE, TAILLE_Y_GRILLE)
definir_reseau_routier(grille, TAILLE_X_GRILLE, TAILLE_Y_GRILLE)
lignes_directions, colonnes_directions = creer_directions_routes(TAILLE_X_GRILLE, TAILLE_Y_GRILLE)

# Initialisation des feux, passages piétons et voitures
feux = initialiser_feux_repartis_sur_routes(TAILLE_X_GRILLE, TAILLE_Y_GRILLE, grille)
passages_pietons = initialiser_passages_pietons_sur_routes(NB_PASSAGES_PIETONS, TAILLE_X_GRILLE, TAILLE_Y_GRILLE, feux, grille)
# Remarque : pietons_actifs commence vide
voitures = generer_voitures_initiales(
    TAILLE_X_GRILLE, TAILLE_Y_GRILLE, feux, grille,
    lignes_directions, colonnes_directions,
    image_voiture_echelle,
    NOMBRE_VOITURES_CIBLE
)
# Remarque : obstacle_automatique_timer commence à 0.0

# Boucle Principale
running = True
while running:
    # Calcule le temps écoulé depuis la dernière frame en secondes
    dt: float = clock.tick(30) / 1000.0 # Vise 30 images par seconde

    # --- Gestion des Événements Utilisateur ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Convertit les coordonnées souris en coordonnées de grille
            cx, cy = event.pos[0] // TAILLE_CELLULE, event.pos[1] // TAILLE_CELLULE
            # Vérifie que les coordonnées sont dans les limites de la grille
            if 0 <= cx < TAILLE_X_GRILLE and 0 <= cy < TAILLE_Y_GRILLE:
                 if event.button == 1: # Clic Gauche -> Ajouter Obstacle Manuel
                     if ajouter_obstacle_manuel(grille, cx, cy, feux):
                          # Forcer le recalcul des voitures dont le chemin ou la destination est touché
                          forcer_recalcul_si_affecte(cx, cy, voitures)
                 elif event.button == 3: # Clic Droit -> Retirer Obstacle Manuel
                     if grille[cy][cx] == OBSTACLE_MANUEL:
                         grille[cy][cx] = ROUTE
                         print(f"Obstacle MANUEL retiré en ({cx},{cy}). Case redevenue ROUTE.")

    # --- Logique d'Obstacle Automatique ---
    obstacle_automatique_timer += dt
    if obstacle_automatique_timer >= OBSTACLE_AUTOMATIQUE_INTERVAL:
        obstacle_automatique_timer -= OBSTACLE_AUTOMATIQUE_INTERVAL

        action = random.choice(['add', 'remove', 'none']) # Peut choisir de ne rien faire
        if action == 'add':
            # Trouve les positions ROUTE où on PEUT ajouter un obstacle automatique (pas déjà occupé par feu/obstacle manuel/auto)
            possible_add_positions = []
            positions_interdites = {feu["position"] for feu in feux}.union({
                (x,y) for y in range(TAILLE_Y_GRILLE) for x in range(TAILLE_X_GRILLE)
                if grille[y][x] in SYMBOLES_NON_PRATICABLES # N, X, A
            })

            for y in range(TAILLE_Y_GRILLE):
                 for x in range(TAILLE_X_GRILLE):
                      if grille[y][x] == ROUTE and (x,y) not in positions_interdites:
                           possible_add_positions.append((x, y))

            if possible_add_positions:
                ox, oy = random.choice(possible_add_positions)
                if ajouter_obstacle_auto(grille, ox, oy, feux): # Appelle ajouter_obstacle_auto
                    # Si ajouté avec succès, force recalcul des voitures impactées.
                    forcer_recalcul_si_affecte(ox, oy, voitures)

        elif action == 'remove':
            # Trouve toutes les positions actuellement occupées par un obstacle AUTOMATIQUE
            current_obstacle_auto_positions = [(x, y) for y in range(TAILLE_Y_GRILLE) for x in range(TAILLE_X_GRILLE) if grille[y][x] == OBSTACLE_AUTO_SYM]
            if current_obstacle_auto_positions:
                # Choisit un obstacle AUTOMATIQUE au hasard et le retire (le rend ROUTE)
                ox, oy = random.choice(current_obstacle_auto_positions)
                grille[oy][ox] = ROUTE
                # Les voitures affectées recalculeront ou se débloqueront automatiquement au prochain tick si besoin.

    # --- Mises à jour Logiques (État de la Simulation) ---
    mettre_a_jour_feux(feux)
    mettre_a_jour_pietons(passages_pietons, pietons_actifs, voitures) # Les piétons sont bloqués si une voiture est bloquée sur le passage
    # La mise à jour des voitures est le coeur de la logique dynamique : déplacement, blocages, recalculs, nouvelle destination
    mettre_a_jour_voitures(voitures, grille, feux, lignes_directions, colonnes_directions, TAILLE_X_GRILLE, TAILLE_Y_GRILLE, pietons_actifs) # Piétons sont passés pour la vérification de validité de déplacement

    # --- Regénération de Voitures ---
    # Maintient le nombre de voitures autour de la cible en ajoutant de nouvelles si la population diminue.
    # Ajout dans une boucle pour essayer d'ajouter plusieurs voitures par tick si nécessaire et possible.
    while len(voitures) < NOMBRE_VOITURES_CIBLE:
        nouvelle_voiture = generer_une_nouvelle_voiture(
             TAILLE_X_GRILLE, TAILLE_Y_GRILLE, feux, grille, lignes_directions, colonnes_directions,
             image_voiture_echelle,
             voitures # Passe la liste actuelle pour que la génération évite les positions occupées
        )
        if not nouvelle_voiture:
             break # Sort de la boucle while (de génération) si aucune voiture n'a pu être ajoutée

        voitures.append(nouvelle_voiture)


    # --- Section Dessin ---
    fenetre.fill(BLANC) # Nettoie l'écran avec un fond blanc

    # Dessine les fonds des cellules (route/non-route) en premier
    dessiner_fonds_cellules(fenetre, grille, TAILLE_CELLULE)
    # Dessine les éléments fixes du décor sur les zones non routières
    dessiner_maisons(fenetre, POSITIONS_MAISONS, grille, TAILLE_CELLULE)
    dessiner_arbres(fenetre, POSITIONS_ARBRES, grille, TAILLE_CELLULE)
    dessiner_ecoles(fenetre, POSITIONS_ECOLES, grille, TAILLE_CELLULE)
    dessiner_montagne_avec_eau(fenetre, POSITIONS_MASSIF_BASE_EAU, grille, TAILLE_CELLULE)
    dessiner_fleurs(fenetre, POSITIONS_FLEURS, grille, TAILLE_CELLULE)

    # Dessine les lignes de la grille
    dessiner_grille_lignes(fenetre, LARGEUR, HAUTEUR, TAILLE_CELLULE)

    # Dessine les éléments interactifs ou importants du réseau routier (sauf voitures/piétons/dest qui sont dynamiques)
    dessiner_obstacles_manuels(fenetre, grille, TAILLE_CELLULE)
    # dessiner_obstacles_automatiques(fenetre, grille, TAILLE_CELLULE) # Désactivé par défaut si 'auto' n'est pas visuel
    dessiner_passages_pietons(fenetre, passages_pietons, TAILLE_CELLULE, COULEUR_PASSAGE)
    dessiner_feux(fenetre, feux, TAILLE_CELLULE)
    dessiner_directions(fenetre, lignes_directions, colonnes_directions, TAILLE_X_GRILLE, TAILLE_Y_GRILLE, TAILLE_CELLULE)
    dessiner_destinations(fenetre, voitures, TAILLE_CELLULE, JAUNE_PARKING)

    # Dessine les entités dynamiques (piétons avant voitures pour ne pas être cachés si très petits)
    dessiner_pietons(fenetre, pietons_actifs, TAILLE_CELLULE, COULEUR_PIETON)
    dessiner_voitures(fenetre, voitures, TAILLE_CELLULE)

    # Afficher l'état du rendu (mettre à jour l'écran)
    pygame.display.flip()


# --- Fin de la Simulation ---
print("Arrêt de la simulation.")
pygame.quit()
sys.exit()