from fltk import *
import random
import time
import json 
import os

vitesse_de_base=1.0

# Configurations des mode de jeu
GAME_MODES = {
    'standard': False,
    'decay': False,
    'two_player': False,
    'Polymynos_arbitraire': False,
    'Couleur_adjacente':False,
    'rotation_grille':False,
    'Polynomes_de_taille_N':False
}


DEFAULT_CONFIG = {
    "display": {
        "bloc_size": 40,
        "grid_width": 10,
        "grid_height": 20,
        "sidebar_width": 200
    },
    "gameplay": {
        "level_speed_multiplier": 1.0,
        "points_multiplier": 1,
        "decay_interval": 30
    },
    "colors": [
        "cyan", "yellow", "purple", 
        "orange", "blue", "red", "green"
    ]
}



POINTS_WITH_LEVEL_ENABLED = False
DECAY_INTERVAL = 30 
POLYMINO_HISTORY = []  
temp_depuis_bonus=time.time()
Tetromino_history={'cyan':[], 'yellow':[], 'purple':[], 'orange':[], 'blue':[], 'red':[], 'green':[]}

BLOC_BONUS=[]
Multiplicateur=1

temp_depuis_rotation=time.time()

# Tetrominos
Tetrominos = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[1, 1, 1], [0, 1, 0]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]


def creer_piece_n(n=4):
    """Crée une pièce aléatoire de taille n x n et l'ajoute à Tetrominos."""
    # Crée une pièce n x n vide
    piece = [[0] * n for _ in range(n)]
    
    # Choisir un nombre de blocs à placer aléatoirement dans la pièce
    nb_blocs = random.randint(1, n * n)

    # Liste des blocs
    blocs = []

    start_x, start_y = random.randint(0, n - 1), random.randint(0, n - 1)
    piece[start_y][start_x] = 1
    blocs.append((start_x, start_y))

    # Ajouter des blocs connectés
    while len(blocs) < nb_blocs:
        x, y = random.choice(blocs)

        # Trouver les voisins valides (haut, bas, gauche, droite)
        voisins = [
            (x - 1, y),  # Gauche
            (x + 1, y),  # Droite
            (x, y - 1),  
            (x, y + 1)   
        ]

        # Filtrer les voisins valides (dans les limites de la grille et non déjà occupés)
        voisins_valides = [(nx, ny) for nx, ny in voisins if 0 <= nx < n and 0 <= ny < n and piece[ny][nx] == 0]

        if voisins_valides:
            nx, ny = random.choice(voisins_valides)
            piece[ny][nx] = 1
            blocs.append((nx, ny))
    Tetrominos.append(piece)



def faire_rotation(jeu):
    a=random.randint(0,1)
    if a==0:
        rotation_droite(jeu)
    else:
        rotation_gauche(jeu)
    Bonus_gravite_avec_animation(jeu)



def rotation_droite(jeu):
    """Effectue une rotation de la grille d'un quart de tour vers la droite."""
    hauteur = len(jeu['grid'])
    largeur = len(jeu['grid'][0])

    # Nouvelle grille vide avec None
    nouvelle_grille = [[None for _ in range(hauteur)] for _ in range(largeur)]

    for y in range(hauteur):
        for x in range(largeur):
            if jeu['grid'][y][x] is not None:
                # Calcul des nouvelles coordonnées pour une rotation à droite
                new_x = y
                new_y = largeur - 1 - x
                nouvelle_grille[new_y][new_x] = jeu['grid'][y][x]

    # Mise à jour de la grille
    jeu['grid'] = nouvelle_grille

def rotation_gauche(jeu):
    """Effectue une rotation de la grille d'un quart de tour vers la gauche."""
    hauteur = len(jeu['grid'])
    largeur = len(jeu['grid'][0])

    # Nouvelle grille vide avec None
    nouvelle_grille = [[None for _ in range(hauteur)] for _ in range(largeur)]

    for y in range(hauteur):
        for x in range(largeur):
            if jeu['grid'][y][x] is not None:
                # Calcul des nouvelles coordonnées pour une rotation à gauche
                new_x = hauteur - 1 - y
                new_y = x
                nouvelle_grille[new_y][new_x] = jeu['grid'][y][x]

    # Mise à jour de la grille
    jeu['grid'] = nouvelle_grille



def load_config(filename='tetris_config.json'):
    try:
        if not os.path.exists(filename):
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
            
        with open(filename, 'r') as f:
            user_config = json.load(f)
            config = DEFAULT_CONFIG.copy()
            for category in user_config:
                if category in config:
                    if isinstance(config[category], dict):
                        config[category].update(user_config[category])
                    else:
                        config[category] = user_config[category]
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG
    

def charger_config():
    global BLOC_SIZE,LARGEUR_PLATEAU,GRID_HEIGHT,WINDOW_WIDTH,WINDOW_HEIGHT,COLORS,DECAY_INTERVAL,vitesse_de_base
    config = load_config()
    BLOC_SIZE = config['display']['bloc_size']
    LARGEUR_PLATEAU = config['display']['grid_width']
    GRID_HEIGHT = config['display']['grid_height']
    WINDOW_WIDTH, WINDOW_HEIGHT = get_window_dimensions(config)
    COLORS = config['colors']
    DECAY_INTERVAL = config['gameplay']['decay_interval']
    vitesse_de_base=config['gameplay']['level_speed_multiplier']


def save_config(config, filename='tetris_config.json'):
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4, default=str)
        print(f"Config saved to {filename}")
    except Exception as e:
        print(f"Error saving config: {e}")

def get_window_dimensions(config):
    display = config['display']
    width = display['bloc_size'] * display['grid_width'] + display['sidebar_width']
    height = display['bloc_size'] * display['grid_height']
    return width, height


def effacage_du_plateau_entier(jeu):
    for ligne in range(len(jeu['grid'])):
        for elem in range(len(jeu['grid'][0])):
            if jeu['grid'][ligne][elem] is not None:
                jeu['grid'][ligne][elem]=None


def Desactiver_bonus(jeu):
    global temp_depuis_bonus,Multiplicateur
    if time.time()-temp_depuis_bonus>10:
      Multiplicateur=1

def Bonus_gravite_avec_animation(jeu, delai=0.1):
    """Applique la gravité avec une animation progressive visible."""
    M = jeu['grid']
    hauteur = len(M)
    largeur = len(M[0])
    changement = True

    while changement:  # Continue tant qu'il y a des blocs qui peuvent tomber
        changement = False
        for j in range(largeur):
            for i in range(hauteur - 1, 0, -1):  # Parcours de bas en haut
                if M[i][j] is None and M[i - 1][j] is not None:
                    # Échange le bloc du dessus avec l'espace vide
                    M[i][j], M[i - 1][j] = M[i - 1][j], None
                    changement = True

        # Affiche la grille après une étape et attend un moment
        dessiner_jeu(jeu,False)
        time.sleep(delai)

def Bonus_gravite(jeu):
    M=jeu['grid']
    for j in range(len(M[0])):
        colonne = [M[i][j] for i in range(len(M)) if M[i][j] is not None]
        colonne = [None] * (len(M) - len(colonne)) + colonne
        for i in range(len(M)):
            M[i][j] = colonne[i]


def point_bonus(jeu):
    global Multiplicateur
    Multiplicateur+=1

def eliminer_lignes_lambda(jeu):
    pass

def appliquer_bonus(jeu):
    chance=random.randint(0,2)
    if chance==0:
        effacage_du_plateau_entier(jeu)
    elif chance==1:
        Bonus_gravite(jeu)
    else:
        point_bonus(jeu)


def piece_aleatoire_bonus(jeu):
    global BLOC_BONUS
    occupied_cells = [
            (y, x) for y in range(GRID_HEIGHT) 
            for x in range(LARGEUR_PLATEAU) 
            if jeu['grid'][y][x] is not None
        ]

    if occupied_cells:
        # Choose and remove a random block
        y, x = random.choice(occupied_cells)
        BLOC_BONUS.append(y)
        jeu['grid'][y][x] = '#fdd700'

    


def lire_polyominos_et_remplacer(nom_fichier):
    """
    Lit un fichier contenant des polyominos et remplace la liste Tetrominos si le fichier n'est pas vide.
    """
    try:
        with open(nom_fichier, "r") as fichier:
            contenu = fichier.read().strip()
        
        if not contenu:
            print("Fichier vide, Tetrominos par défaut utilisés.")
            return None  # Indique qu'on doit conserver les Tetrominos par défaut

        # Découper les polyominos par double saut de ligne
        blocs = contenu.split("\n\n")
        nouveaux_tetrominos = []

        for bloc in blocs:
            lignes = bloc.split("\n")
            max_largeur = max(len(ligne) for ligne in lignes)
            
            # Construire la matrice pour ce polyomino
            matrice = []
            for ligne in lignes:
                row = [1 if char == '+' else 0 for char in ligne]
                # Compléter les lignes pour avoir une largeur uniforme
                row += [0] * (max_largeur - len(row))
                matrice.append(row)
            
            nouveaux_tetrominos.append(matrice)
        
        return nouveaux_tetrominos
    
    except FileNotFoundError:
        print(f"Erreur : le fichier {nom_fichier} est introuvable.")
        return None






def mode_decay(jeu):
    """Implement block decay mechanism"""
    temps_actuel = time.time()
    if temps_actuel - jeu.get('last_decay_time', 0) > DECAY_INTERVAL:
        occupied_cells = [
            (y, x) for y in range(len(jeu['grid'])) 
            for x in range(len(jeu['grid'][0])) 
            if jeu['grid'][y][x] is not None
        ]
        
        if occupied_cells:
            # Choose and remove a random block
            y, x = random.choice(occupied_cells)
            jeu['grid'][y][x] = None
        
        jeu['last_decay_time'] = temps_actuel




def load_game(filename='tetris_save.json'):
    """Load game state from a file with advanced mode support"""
    try:
        with open(filename, 'r') as f:
            save_data = json.load(f)
        
        # Recreate game state
        jeu = creer_etat_jeu()
        jeu['grid'] = save_data['grid']
        jeu['current_piece'] = save_data['current_piece']
        jeu['next_piece'] = save_data['next_piece']
        jeu['score'] = save_data['score']
        jeu['level'] = save_data['level']
        jeu['lines_cleared'] = save_data['lines_cleared']
        
        # Update global configurations from saved game
        global GAME_MODES, POINTS_WITH_LEVEL_ENABLED
        GAME_MODES['standard'] = save_data.get('game_modes', {}).get('standard', True)
        GAME_MODES['decay'] = save_data.get('game_modes', {}).get('decay', False)
        GAME_MODES['two_player'] = save_data.get('game_modes', {}).get('two_player', False)
        GAME_MODES['Polymynos_arbitraire']=save_data.get('game_mode', {}).get('Polymynos_arbitraire', False)
        POINTS_WITH_LEVEL_ENABLED = save_data.get('points_with_level', False)
        
        # Add missing attributes for game update
        jeu['dernier_tombe'] = time.time()
        jeu['vitesse_tombe'] = 1.0
        
        print(f"Game loaded from {filename}")
        return jeu
    except FileNotFoundError:
        print("No saved game found.")
        return None
    except Exception as e:
        print(f"Error loading game: {e}")
        return None



def save_game(jeu, filename='tetris_save.json'):
    """Save game state to a file with advanced mode support"""
    try:
        save_data = {
            'grid': jeu['grid'],
            'current_piece': jeu['current_piece'],
            'next_piece': jeu['next_piece'],
            'score': jeu['score'],
            'level': jeu['level'],
            'lines_cleared': jeu['lines_cleared'],
            'game_modes': GAME_MODES,
            'points_with_level': POINTS_WITH_LEVEL_ENABLED,
            'dernier_tombe': jeu.get('dernier_tombe', time.time()),
            'vitesse_tombe': jeu.get('vitesse_tombe', 1.0)
        }
        with open(filename, 'w') as f:
            json.dump(save_data, f, default=lambda o: str(o))
        print(f"Game saved to {filename}")
    except Exception as e:
        print(f"Error saving game: {e}")







def mode_selection_menu():
    """Menu amélioré pour la sélection du mode de jeu et des points"""
    cree_fenetre(WINDOW_WIDTH, WINDOW_HEIGHT+100)
    
    # Liste étendue des modes pour plusieurs sélections
    modes = ['Standard', 'Détérioration', 'Deux joueurs', 'Points avec niveaux', 'Polymynos arbitraire','Couleur adjacente','Bonus','Rotation grille','Polynomes de taille N']
    selected_modes = [False] * len(modes)
    current_selection = 0
    
    while True:
        efface_tout()
        
        # Titre
        texte(WINDOW_WIDTH // 2 - 250, 50, "CONFIGURATION DU JEU TETRIS", "red")
        
        # Sélection du mode
        for i, mode in enumerate(modes):
            # Mettre en surbrillance la sélection actuelle
            if i == current_selection:
                rectangle(WINDOW_WIDTH // 2 - 180, 150 + i * 70, 
                          WINDOW_WIDTH // 2 + 180, 200 + i * 70, "white")
            
            # Couleur selon l'état de sélection
            if i < 3:  # Modes de jeu
                couleur = "green" if selected_modes[i] else "gray"
            else:  # Points avec niveaux
                couleur = "green" if selected_modes[i] else "gray"
            
            rectangle(WINDOW_WIDTH // 2 - 150, 150 + i * 70, 
                      WINDOW_WIDTH // 2 + 150, 200 + i * 70, couleur)
            texte(WINDOW_WIDTH // 2 - 100, 165 + i * 70, mode, couleur)
        
        # Instructions
        texte(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT-20, 
              "ESPACE pour sélectionner/décocher", "blue")
        texte(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT +10, 
              "ENTRÉE pour confirmer", "blue")
        texte(WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT +40, 
              "Appuyez sur L pour charger une partie", "blue")
        
        mise_a_jour()
        
        # Gestion des événements
        ev = attend_ev()
        type_evt = type_ev(ev)
        
        if type_evt == 'Touche':
            touche_pressee = touche(ev)
            
            if touche_pressee == 'Up':
                current_selection = (current_selection - 1) % len(modes)
            elif touche_pressee == 'Down':
                current_selection = (current_selection + 1) % len(modes)
            elif touche_pressee == 'space':
                # Basculer le mode actuellement sélectionné
                selected_modes[current_selection] = not selected_modes[current_selection]
            elif touche_pressee == 'Return':
                # Mettre à jour les modes de jeu globaux
                global GAME_MODES, POINTS_WITH_LEVEL_ENABLED
                GAME_MODES['standard'] = selected_modes[0]
                GAME_MODES['decay'] = selected_modes[1]
                GAME_MODES['two_player'] = selected_modes[2]
                GAME_MODES['Polymynos_arbitraire'] = selected_modes[4]
                GAME_MODES['Couleur_adjacente'] = selected_modes[5]
                GAME_MODES['Bonus'] = selected_modes[6]
                GAME_MODES['rotation_grille']=selected_modes[7]
                GAME_MODES['Polynomes_de_taille_N']=selected_modes[8]
                POINTS_WITH_LEVEL_ENABLED = selected_modes[3]
                
                ferme_fenetre()
                return None

            elif touche_pressee=="e":
                charger_config()
            elif touche_pressee == 'l':
                # Option pour charger une partie
                loaded_game = load_game()
                if loaded_game:
                    ferme_fenetre()
                    return loaded_game
    
    return None


#Devra etre modifie pour les Bonus
def creer_grille():
    """Crée une grille vide pour le jeu."""
    grille = []
    for _ in range(GRID_HEIGHT):
        ligne = []
        for _ in range(LARGEUR_PLATEAU):
            ligne.append(None)
        grille.append(ligne)
    
    return grille

def piece_en_collision(jeu, piece):
    """Vérifie si la pièce donnée entre en collision avec la grille."""
    forme = piece['forme']
    hauteur = len(forme)
    largeur = len(forme[0])

    for rel_y in range(hauteur):
        for rel_x in range(largeur):
            if forme[rel_y][rel_x]:  # Si cette cellule fait partie de la pièce
                # Calcul de la position dans la grille
                grille_x = piece['x'] + rel_x
                grille_y = piece['y'] + rel_y
                
                if grille_x < 0 or grille_x >= len(jeu['grid'][0]) or grille_y >= len(jeu['grid']):
                    return True
                if grille_y >= 0 and jeu['grid'][grille_y][grille_x] is not None:
                    return True
    return False

def nouvelle_forme_rotatee(piece):
    """Renvoie une nouvelle forme de la pièce, tournée de 90 degrés dans le sens horaire."""

    # Initialisation de la matrice de la nouvelle forme avec les dimensions transposées
    ancienne_forme = piece['forme']
    nb_lignes = len(ancienne_forme)
    nb_colonnes = len(ancienne_forme[0]) if nb_lignes > 0 else 0
    nouvelle_forme = []

    # Création d'une matrice vide pour la nouvelle forme (transposée et inversée)
    for j in range(nb_colonnes):
        nouvelle_ligne = []
        for i in range(nb_lignes - 1, -1, -1):
            nouvelle_ligne.append(ancienne_forme[i][j])
        nouvelle_forme.append(nouvelle_ligne)

    return nouvelle_forme


def appliquer_rotation_si_possible(jeu):
    """Déplace la pièce courante de dx et dy, fusionne si une collision empêche le déplacement."""
    piece = jeu['current_piece']
    ancienne_forme = piece['forme']
    piece['forme'] = nouvelle_forme_rotatee(piece)
    if piece_en_collision(jeu, piece):
        piece['forme'] = ancienne_forme  # Annule la rotation si elle entraîne une collision


def appliquer_deplacement(jeu, dx, dy):
    """Déplace la pièce courante de dx et dy, fusionne si une collision empêche le déplacement."""
    piece = jeu['current_piece']
    piece['x'] += dx
    piece['y'] += dy
    if piece_en_collision(jeu, piece):
        piece['x'] -= dx
        piece['y'] -= dy
        if dy > 0:  # S'il y a une collision en descendant, on fusionne et crée une nouvelle pièce
            fusionner_piece(jeu)
            verifier_lignes(jeu)
            nouvelle_piece(jeu)
        return False
    return True

def sont_voisins(b1, b2):
    """Vérifie si deux blocs b1 et b2 sont voisins (touchent horizontalement ou verticalement)."""
    return abs(b1[0] - b2[0]) == 1 and b1[1] == b2[1] or abs(b1[1] - b2[1]) == 1 and b1[0] == b2[0]


def remplacer_blocs_par_none(grille, pieces, tetromino_history, couleur,jeu):
    """Remplace les blocs des pièces par None dans la grille et les supprime de Tetromino_history."""
    for piece in pieces:
        for bloc in piece:
            y, x = bloc
            grille[y][x] = None

        # Une fois tous les blocs de la pièce remplacés, on supprime la pièce de Tetromino_history
        if couleur in tetromino_history:
            if piece in tetromino_history[couleur]:
                tetromino_history[couleur].remove(piece)
                jeu["score"]+=10
    
    # Si après la suppression il n'y a plus de pièces pour une couleur, on enlève cette couleur de Tetromino_history
    if couleur in tetromino_history and not tetromino_history[couleur]:
        tetromino_history[couleur]=[]


def verifier_et_remplacer(grille, tetromino_history, couleur,jeu):
    """
    Vérifie si deux pièces de la même couleur se touchent par au moins deux blocs et
    remplace leurs blocs par None dans la grille.
    """
    # Récupère toutes les positions des blocs pour la couleur donnée
    pieces = tetromino_history.get(couleur, [])

    # Si moins de 2 pièces, aucune possibilité de se toucher
    if len(pieces) < 2:
        return False

    # Compare chaque bloc de la première pièce avec chaque bloc de la deuxième pièce
    for i in range(len(pieces)):
        for j in range(i + 1, len(pieces)):  # Comparer chaque paire de pièces
            piece1 = pieces[i]
            piece2 = pieces[j]
            
            # Vérifier si au moins deux blocs de piece1 se touchent avec au moins deux blocs de piece2
            count = 0
            for b1 in piece1:
                for b2 in piece2:
                    if sont_voisins(b1, b2):
                        count += 1
                    if count >= 2:  # Si on a trouvé deux blocs voisins, on remplace les blocs par None
                        # Remplacer les blocs des deux pièces par None dans la grille
                        remplacer_blocs_par_none(grille, [piece1, piece2],tetromino_history,couleur,jeu)
                        return True

    return False



def verifier_lignes(jeu):
    """Vérifie les lignes complètes, les supprime, met à jour Tetromino_history et décale les blocs."""
    global Tetromino_history,BLOC_BONUS,temp_depuis_bonus,temp_depuis_rotation
    lignes_vides = 0
    lignes_supprimees = []  # Liste pour stocker les numéros des lignes supprimées

    # Parcourt chaque ligne de la grille (de bas en haut pour éviter les décalages)
    for y in range(len(jeu['grid']) - 1, -1, -1):  # Commence par la dernière ligne
        ligne_complete = True
        for x in range(len(jeu['grid'][0])):
            if jeu['grid'][y][x] is None:
                ligne_complete = False
                break

        if ligne_complete:
            # Supprime la ligne complète
            jeu['grid'].pop(y)
            ligne_vide = [None] * LARGEUR_PLATEAU
            jeu['grid'].insert(0, ligne_vide)
            lignes_vides += 1
            lignes_supprimees.append(y)  # Garde le numéro de la ligne supprimée

    
    # Met à jour le score et le niveau en fonction des lignes effacées
    mise_a_jour_score_et_niveau(jeu, lignes_vides)
    if GAME_MODES['Couleur_adjacente']:
    # **Itérer sur une copie des clés pour éviter les modifications en cours d'itération**
        for couleur in list(Tetromino_history.keys()):  # Crée une copie des clés du dictionnaire
            verifier_et_remplacer(jeu['grid'], Tetromino_history, couleur,jeu)

    if GAME_MODES['decay']:
        mode_decay(jeu)

    if GAME_MODES['Couleur_adjacente']:
        for couleur, blocs in Tetromino_history.items():
            nouvelles_pieces = []  # Pour stocker les pièces mises à jour
            for piece in blocs:
                nouvelle_piece = []
                for bloc in piece:
                    y, x = bloc  # Coordonnées du bloc
                    if y in lignes_supprimees:
                    # Le bloc appartient à une ligne supprimée, on l'ignore (il est supprimé)
                        continue
                    # Décale les blocs situés au-dessus des lignes supprimées
                    decalage = sum(1 for ligne in lignes_supprimees if y < ligne)  # Compte les lignes en dessous
                    nouvelle_piece.append([y + decalage, x])
            # Ajoute la pièce mise à jour si elle contient encore des blocs
                if nouvelle_piece:
                    nouvelles_pieces.append(nouvelle_piece)
            Tetromino_history[couleur] = nouvelles_pieces
    
    if GAME_MODES['rotation_grille']:
        if time.time()-temp_depuis_rotation>20:
            temp_depuis_rotation=time.time()
            faire_rotation(jeu)
    
    if GAME_MODES['Bonus']:
        a=random.randint(0,5)
        b=random.randint(0,5)
        if a==b:
            piece_aleatoire_bonus(jeu)
        for y in lignes_supprimees:
            if y in BLOC_BONUS:
                BLOC_BONUS.remove(y)
                appliquer_bonus(jeu)
                temp_depuis_bonus=time.time()
        Desactiver_bonus(jeu)

def fusionner_piece(jeu):
    """Ajoute la pièce courante à la grille, en fonction de sa position et de sa couleur."""
    piece = jeu['current_piece']
    forme = piece['forme']
    couleur = piece['couleur']
    hauteur = len(forme)
    largeur = len(forme[0])
    # Liste pour stocker les coordonnées de cette pièce
    piece_coords = []

    for rel_y in range(hauteur):
        for rel_x in range(largeur):
            if forme[rel_y][rel_x]:
                grille_y, grille_x = piece['y'] + rel_y, piece['x'] + rel_x
                POLYMINO.append([grille_y, grille_x])  # Pour la compatibilité existante
                if grille_y >= 0:  # Ne pas dessiner en dehors de la grille
                    jeu['grid'][grille_y][grille_x] = couleur
                    piece_coords.append([grille_y, grille_x])
    if GAME_MODES['Couleur_adjacente']:
        global Tetromino_history
        Tetromino_history[couleur].append(piece_coords)




def mise_a_jour_score_et_niveau(jeu, lignes_vides):
    """Met à jour le score et le niveau en fonction des lignes complètes."""
    jeu['lines_cleared'] += lignes_vides
    point = 0
    if lignes_vides == 1:
        point += 40
    elif lignes_vides == 2:
        point += 100
    elif lignes_vides == 3:
        point += 300
    elif lignes_vides == 4:
        point += 500
    else:
        point += 0
    
    # Apply level multiplier only if POINTS_WITH_LEVEL_ENABLED is True
    if POINTS_WITH_LEVEL_ENABLED:
        point *= jeu['level']
    point*=Multiplicateur
    jeu['score'] += point
    jeu['level'] = jeu['lines_cleared'] // 5 + 1

def nouvelle_piece(jeu):
    """Génère une nouvelle pièce et la positionne en haut de la grille, termine le jeu si collision."""
    if jeu['next_piece'] is None:
        jeu['next_piece'] = creer_piece()  # Crée la première pièce suivante
    
    jeu['current_piece'] = jeu['next_piece']  # Utilise la pièce suivante comme pièce courante
    jeu['next_piece'] = creer_piece()  # Crée une nouvelle pièce suivante
    
    if piece_en_collision(jeu, jeu['current_piece']):
        jeu['game_over'] = True


def dessiner_prochaine_piece(jeu):
    """Dessine la prochaine pièce dans une zone à droite du plateau."""
    if jeu['next_piece']:
        # Position de la zone d'aperçu
        preview_x = len(jeu['grid'][0]) * BLOC_SIZE +25
        preview_y = 200       
        
        texte(preview_x - 20, preview_y - 30, "Prochaine", "black")
        
        piece = jeu['next_piece']
        forme = piece['forme']
        couleur = piece['couleur']
        
        # Centre la pièce dans la zone d'aperçu
        centre_x = preview_x + 30
        centre_y = preview_y + 30


        for y in range(len(forme)):
            for x in range(len(forme[0])):
                if forme[y][x]:
                    rectangle(centre_x + x * BLOC_SIZE,
                            centre_y + y * BLOC_SIZE,
                            centre_x + (x + 1) * BLOC_SIZE,
                            centre_y + (y + 1) * BLOC_SIZE,
                            couleur, couleur)





def creer_piece():
    """Crée une nouvelle pièce au hasard avec une forme et couleur aléatoires."""
    # Sélectionne un index aléatoire pour déterminer la forme et la couleur de la pièce
    index = random.randint(0, len(Tetrominos) - 1)
    
    # Initialise une nouvelle liste pour la forme et copie chaque élément sans slicing ni compréhension de liste
    forme = []
    for row in Tetrominos[index]:
        # Crée une copie de la ligne en ajoutant chaque élément un par un
        copie_row = []
        for element in row:
            copie_row.append(element)
        forme.append(copie_row)
    
    # Crée le dictionnaire de la pièce avec la forme, couleur, et position de départ
    return {
        'forme': forme,
        'couleur': COLORS[index],
        'x': LARGEUR_PLATEAU // 2 - len(Tetrominos[index][0]) // 2,
        'y': 0
    }

def creer_etat_jeu():
    """Initialise l'état de jeu avec une grille vide et les valeurs de départ."""

    return {
        'grid': creer_grille(),
        'current_piece': None,
        'next_piece': None,  
        'game_over': False,
        'score': 0,
        'level': 1,
        'lines_cleared': 0
    }

def dessiner_grille(jeu):
    """Dessine la grille de jeu avec les lignes verticales et horizontales."""
    # Dessiner les lignes verticales
    for x in range(len(jeu['grid'][0]) + 1):
        ligne(x * BLOC_SIZE, 0, x * BLOC_SIZE, len(jeu['grid']) * BLOC_SIZE, "white")

    # Dessiner les lignes horizontales
    for y in range(len(jeu['grid']) + 1):
        ligne(0, y * BLOC_SIZE, len(jeu['grid'][0]) * BLOC_SIZE, y * BLOC_SIZE, "white")

def dessiner_contenu_grille(jeu):
    """Dessine le contenu actuel de la grille."""
    for y in range(len(jeu['grid'])):
        for x in range(len(jeu['grid'][0])):
            color = jeu['grid'][y][x]
            if color:
                rectangle(x * BLOC_SIZE, y * BLOC_SIZE,
                          (x + 1) * BLOC_SIZE, (y + 1) * BLOC_SIZE,
                          color, color)



def dessiner_piece_courante(jeu):
    """Dessine la pièce courante sur la grille."""
    if jeu['current_piece']:
        piece = jeu['current_piece']
        forme = piece['forme']
        couleur = piece['couleur']
        hauteur = len(forme)
        largeur = len(forme[0])

        for y in range(hauteur):
            for x in range(largeur):
                if forme[y][x]:
                    abs_x = piece['x'] + x
                    abs_y = piece['y'] + y
                    if abs_y >= 0:  # Si la pièce est dans le plateau, on la dessine
                        rectangle(abs_x * BLOC_SIZE, abs_y * BLOC_SIZE,
                                  (abs_x + 1) * BLOC_SIZE, (abs_y + 1) * BLOC_SIZE,
                                  couleur, couleur)

def dessiner_scores(jeu):
    """Dessine le score, le niveau et le nombre de lignes effacées."""
    texte(len(jeu['grid'][0]) * BLOC_SIZE + 20, 50, "Score: " + str(jeu['score']), "black")
    texte(len(jeu['grid'][0]) * BLOC_SIZE + 20, 80, "Niveau: " + str(jeu['level']), "black")
    texte(len(jeu['grid'][0]) * BLOC_SIZE + 20, 110, "Lignes: " + str(jeu['lines_cleared']), "black")
    if jeu['game_over']:
        texte(len(jeu['grid'][0]) * BLOC_SIZE // 2 - 40, len(jeu['grid']) * BLOC_SIZE // 2, "GAME OVER", "red")

def dessiner_jeu(jeu,c=True):
    """Dessine l'état actuel du jeu."""
    efface_tout()
    rectangle(0, 0, len(jeu['grid'][0]) * BLOC_SIZE, len(jeu['grid']) * BLOC_SIZE, "black", "black")
    dessiner_grille(jeu)  # Dessine la grille
    dessiner_contenu_grille(jeu)  # Dessine le contenu de la grille
    if c:
        dessiner_piece_courante(jeu)  # Dessine la pièce courante
    dessiner_scores(jeu)  # Dessine le score et le niveau
    dessiner_prochaine_piece(jeu)  # Dessine la prochaine pièce
    if GAME_MODES['decay']==True:
        mode_decay(jeu)
    mise_a_jour()  # Met à jour l'affichage





def pause(jeu):
    """Met le jeu en pause jusqu'à ce que le joueur appuie à nouveau sur 'p'"""
    while True:  # Boucle d'attente
        efface_tout()
        dessiner_jeu(jeu)  # Garde l'affichage du jeu
        texte(LARGEUR_PLATEAU * BLOC_SIZE // 2 - 40, GRID_HEIGHT * BLOC_SIZE // 2, "PAUSE", "white")
        mise_a_jour()  # Met à jour l'affichage
        
        ev = donne_ev()
        if ev:
            type_evt = type_ev(ev)
            if type_evt == 'Touche':
                touche_pressee = touche(ev)
                if touche_pressee == 'p':  # Si 'p' est pressé, sort de la pause
                    return
    


def initialiser_fenetre():
    """Initialise la fenêtre du jeu."""
    if GAME_MODES['rotation_grille']:
        cree_fenetre(WINDOW_HEIGHT*2 ,WINDOW_HEIGHT)
    else:
        cree_fenetre(WINDOW_WIDTH, WINDOW_HEIGHT)


def initialiser_jeu():
    """Initialise l'état du jeu avec les options choisies."""
    global vitesse_de_base
    jeu = creer_etat_jeu()
    jeu['points_with_level'] = POINTS_WITH_LEVEL_ENABLED
    jeu['next_piece'] = creer_piece()
    nouvelle_piece(jeu)
    jeu['dernier_tombe'] = time.time()
    jeu['vitesse_tombe'] = vitesse_de_base
    return jeu

def gerer_entrees_utilisateur(jeu):
    """Gère les entrées utilisateur."""
    ev = donne_ev()
    if ev:
        type_evt = type_ev(ev)
        if type_evt == 'Touche':
            traiter_touche(touche(ev), jeu)

def traiter_touche(touche_pressee, jeu):
    """Ajout de nouvelles touches pour les fonctionnalités avancées"""
    # Touches existantes
    if touche_pressee == 'q':  # Quitter le jeu
        jeu['game_over'] = True
    elif touche_pressee == 'Left':
        appliquer_deplacement(jeu, -1, 0)
    elif touche_pressee == 'Right':
        appliquer_deplacement(jeu, 1, 0)
    elif touche_pressee == 'Down':
        appliquer_deplacement(jeu, 0, 1)
    elif touche_pressee == 'Up':
        appliquer_rotation_si_possible(jeu)
    elif touche_pressee == 'space':
        faire_tomber_piece(jeu)
    
    # Nouvelles touches
    elif touche_pressee == 's':  # Sauvegarder
        save_game(jeu)
    elif touche_pressee == 'p':  # Pause
        pause(jeu)
    elif touche_pressee == 'm':  # Retour au menu
        jeu['game_over'] = True
        main()



def faire_tomber_piece(jeu):
    """Fait tomber la pièce directement."""
    while appliquer_deplacement(jeu, 0, 1):
        pass

def mettre_a_jour_jeu(jeu):
    """Met à jour l'état du jeu pour faire descendre les pièces."""
    temps_actuel = time.time()
    if temps_actuel - jeu['dernier_tombe'] > jeu['vitesse_tombe'] / jeu['level']:#regarde le niveau
        appliquer_deplacement(jeu, 0, 1)
        jeu['dernier_tombe'] = temps_actuel

def attendre_fin():
    """Attendre que le joueur clique pour quitter."""
    attend_clic_gauche()
    ferme_fenetre()

def charger_Poly():
    # Remplacement si le fichier contient des polyominos
    global Tetrominos
    nom_fichier_polyominos = "polyominos.txt"
    nouveaux_polyominos = lire_polyominos_et_remplacer(nom_fichier_polyominos)

    if nouveaux_polyominos:
        Tetrominos = nouveaux_polyominos

    # Affiche les Tetrominos utilisés
    print("Tetrominos utilisés :")
    for t in Tetrominos:
        for a in t:
            print("".join(str(x) for x in a))
        print()


#====================================================================================
#code pour le mode deux joueur


def creer_etat_jeu_deux_joueurs():
    """Initialise l'état de jeu pour deux joueurs."""
    return {
        'player1': {
            'grid': creer_grille(),
            'current_piece': None,
            'next_piece': None,  
            'game_over': False,
            'score': 0,
            'level': 1,
            'lines_cleared': 0,
            'dernier_tombe': time.time(),
            'vitesse_tombe': 1.0
        },
        'player2': {
            'grid': creer_grille(),
            'current_piece': None,
            'next_piece': None,  
            'game_over': False,
            'score': 0,
            'level': 1,
            'lines_cleared': 0,
            'dernier_tombe': time.time(),
            'vitesse_tombe': 1.0
        },
        'game_over': False
    }


def dessiner_jeu_deux_joueurs(jeu):
    """Dessine l'état du jeu pour deux joueurs."""
    efface_tout()
    
    # Dessiner la grille du joueur 1
    rectangle(0, 0, LARGEUR_PLATEAU * BLOC_SIZE, GRID_HEIGHT * BLOC_SIZE, "black", "black")
    dessiner_grille_specifique(0)
    dessiner_contenu_grille_specifique(jeu, 'player1', 0)
    dessiner_piece_courante_specifique(jeu, 'player1', 0)
    dessiner_scores_specifique(jeu, 'player1', (LARGEUR_PLATEAU * BLOC_SIZE))
    dessiner_prochaine_piece_specifique(jeu, 'player1', LARGEUR_PLATEAU * BLOC_SIZE)
    
    # Dessiner la grille du joueur 2
    rectangle(LARGEUR_PLATEAU * BLOC_SIZE, 0, 
              2 * LARGEUR_PLATEAU * BLOC_SIZE, GRID_HEIGHT * BLOC_SIZE, "black", "black")
    dessiner_grille_specifique(LARGEUR_PLATEAU * BLOC_SIZE)
    dessiner_contenu_grille_specifique(jeu, 'player2', LARGEUR_PLATEAU * BLOC_SIZE)
    dessiner_piece_courante_specifique(jeu, 'player2', LARGEUR_PLATEAU * BLOC_SIZE)
    dessiner_scores_specifique(jeu, 'player2', LARGEUR_PLATEAU * BLOC_SIZE)
    dessiner_prochaine_piece_specifique(jeu, 'player2', LARGEUR_PLATEAU * BLOC_SIZE)
    
    mise_a_jour()

def dessiner_grille_specifique(offset_x):
    """Dessine les lignes de la grille pour un joueur spécifique."""
    for x in range(LARGEUR_PLATEAU + 1):
        ligne(offset_x + x * BLOC_SIZE, 0, 
              offset_x + x * BLOC_SIZE, GRID_HEIGHT * BLOC_SIZE, "white")
        if x==(LARGEUR_PLATEAU):
            ligne(x * BLOC_SIZE, 0, x * BLOC_SIZE, GRID_HEIGHT * BLOC_SIZE, "red")
    for y in range(GRID_HEIGHT + 1):
        ligne(offset_x, y * BLOC_SIZE, 
              offset_x + LARGEUR_PLATEAU * BLOC_SIZE, y * BLOC_SIZE, "white")


def dessiner_contenu_grille_specifique(jeu, joueur, offset_x):
    """Dessine le contenu de la grille pour un joueur spécifique."""
    for y in range(GRID_HEIGHT):
        for x in range(LARGEUR_PLATEAU):
            color = jeu[joueur]['grid'][y][x]
            if color:
                rectangle(offset_x + x * BLOC_SIZE, y * BLOC_SIZE,
                          offset_x + (x + 1) * BLOC_SIZE, (y + 1) * BLOC_SIZE,
                          color, color)


def dessiner_piece_courante_specifique(jeu, joueur, offset_x):
    """Dessine la pièce courante pour un joueur spécifique."""
    if jeu[joueur]['current_piece']:
        piece = jeu[joueur]['current_piece']
        forme = piece['forme']
        couleur = piece['couleur']
        hauteur = len(forme)
        largeur = len(forme[0])

        for y in range(hauteur):
            for x in range(largeur):
                if forme[y][x]:
                    abs_x = piece['x'] + x
                    abs_y = piece['y'] + y
                    if abs_y >= 0:
                        rectangle(offset_x + abs_x * BLOC_SIZE, abs_y * BLOC_SIZE,
                                  offset_x + (abs_x + 1) * BLOC_SIZE, (abs_y + 1) * BLOC_SIZE,
                                  couleur, couleur)

def dessiner_scores_specifique(jeu, joueur, offset_x):
    """Dessine les scores pour un joueur spécifique."""
    base_y=50
    if joueur=="player1":
        base_y=400
    texte(offset_x + LARGEUR_PLATEAU * BLOC_SIZE + 20, base_y, 
          f"{joueur.capitalize()} Score: " + str(jeu[joueur]['score']), "black")
    texte(offset_x + LARGEUR_PLATEAU * BLOC_SIZE + 20, base_y+30, 
          f"{joueur.capitalize()} Niveau: " + str(jeu[joueur]['level']), "black")
    texte(offset_x + LARGEUR_PLATEAU * BLOC_SIZE + 20, base_y+60, 
          f"{joueur.capitalize()} Lignes: " + str(jeu[joueur]['lines_cleared']), "black")
    
    if jeu[joueur]['game_over']:
        if joueur=='player1':
            texte(100,GRID_HEIGHT * BLOC_SIZE // 2,"GAME OVER","red")
        else:
            texte(offset_x + LARGEUR_PLATEAU * BLOC_SIZE // 2 - 40, 
                  GRID_HEIGHT * BLOC_SIZE // 2, "GAME OVER", "red")


def dessiner_prochaine_piece_specifique(jeu, joueur, offset_x):
    """Dessine la prochaine pièce pour un joueur spécifique."""
    if jeu[joueur]['next_piece']:
        preview_x = offset_x + LARGEUR_PLATEAU * BLOC_SIZE + 25
        preview_y=200
        if joueur=="player1":
            preview_y=550
        
        texte(preview_x - 20, preview_y - 30, f"Prochaine {joueur.capitalize()}", "black")
        
        piece = jeu[joueur]['next_piece']
        forme = piece['forme']
        couleur = piece['couleur']
        
        centre_x = preview_x + 30
        centre_y = preview_y + 30

        for y in range(len(forme)):
            for x in range(len(forme[0])):
                if forme[y][x]:
                    rectangle(centre_x + x * BLOC_SIZE,
                              centre_y + y * BLOC_SIZE,
                              centre_x + (x + 1) * BLOC_SIZE,
                              centre_y + (y + 1) * BLOC_SIZE,
                              couleur, couleur)



def appliquer_deplacement_deux(jeu, dx, dy,joueur):
    """Déplace la pièce courante de dx et dy, fusionne si une collision empêche le déplacement."""
    piece = jeu[joueur]['current_piece']
    piece['x'] += dx
    piece['y'] += dy
    if piece_en_collision(jeu[joueur], piece):
        piece['x'] -= dx
        piece['y'] -= dy
        if dy > 0:  # S'il y a une collision en descendant, on fusionne et crée une nouvelle pièce
            fusionner_piece_deux(jeu,joueur)
            verifier_lignes_deux(jeu,joueur)
            if not jeu[joueur]['game_over']:
                nouvelle_piece(jeu[joueur])
        return False
    return True


def faire_tomber_piece_deux(jeu,joueur):
    """Fait tomber la pièce directement."""
    while appliquer_deplacement_deux(jeu, 0, 1,joueur):
        pass


def traiter_touche_deux_joueurs(touche_pressee, jeu):
    """Gère les touches pour deux joueurs."""
    
    # Touches pour le joueur 1
    if touche_pressee == 'Left':
        appliquer_deplacement_deux(jeu, -1, 0,'player1')
    elif touche_pressee == 'Right':
        appliquer_deplacement_deux(jeu, 1, 0,'player1')
    elif touche_pressee == 'Down':
        appliquer_deplacement_deux(jeu, 0, 1,'player1')
    elif touche_pressee == 'Up':
        appliquer_rotation_si_possible(jeu['player1'])
    elif touche_pressee == 'space':
        faire_tomber_piece_deux(jeu,'player1')
    

    # Touches pour le joueur 2
    if touche_pressee == 'a':  # Gauche
        appliquer_deplacement_deux(jeu, -1, 0,'player2')
    elif touche_pressee == 'd':  # Droite
        appliquer_deplacement_deux(jeu, 1, 0,'player2')
    elif touche_pressee == 's':  # Descendre
        appliquer_deplacement_deux(jeu, 0, 1,'player2')
    elif touche_pressee == 'z':  # Rotation
        appliquer_rotation_si_possible(jeu['player2'])
    elif touche_pressee == 'x':  # Faire tomber
        faire_tomber_piece_deux(jeu,'player2')
    
    # Touches communes
    if touche_pressee == 'p':  # Pause
        pause(jeu)
    elif touche_pressee == 'm':  # Retour au menu
        jeu['game_over'] = True
        main()

def mettre_a_jour_jeu_deux_joueurs(jeu):
    """Met à jour l'état du jeu pour deux joueurs."""
    temps_actuel = time.time()
    
    # Joueur 1
    if temps_actuel - jeu['player1']['dernier_tombe'] > jeu['player1']['vitesse_tombe'] / jeu['player1']['level']:
        appliquer_deplacement_deux(jeu, 0, 1,'player1')
        jeu['player1']['dernier_tombe'] = temps_actuel
    
    # Joueur 2
    if temps_actuel - jeu['player2']['dernier_tombe'] > jeu['player2']['vitesse_tombe'] / jeu['player2']['level']:
        appliquer_deplacement_deux(jeu, 0, 1,'player2')
        jeu['player2']['dernier_tombe'] = temps_actuel



def nouvelle_piece_deux_joueurs(jeu, joueur):
    """Génère une nouvelle pièce pour un joueur spécifique."""
    if jeu[joueur]['next_piece'] is None:
        jeu[joueur]['next_piece'] = creer_piece()
    
    jeu[joueur]['current_piece'] = jeu[joueur]['next_piece']
    jeu[joueur]['next_piece'] = creer_piece()
    
    if piece_en_collision(jeu[joueur], jeu[joueur]['current_piece']):
        jeu[joueur]['game_over'] = True
        jeu['game_over'] = True



def initialiser_fenetre2():
    """Initialise la fenêtre du jeu."""
    cree_fenetre(WINDOW_WIDTH, WINDOW_HEIGHT)


def generer_ligne_avec_trou(largeur):
    """Génère une ligne de blocs avec un trou à un emplacement aléatoire."""
    ligne = [random.choice(COLORS) if x != random.randint(0, largeur-1) else None 
             for x in range(largeur)]
    return ligne


def ajouter_lignes_attaque(jeu, joueur_attaquant, joueur_defenseur, nb_lignes):
    """
    Ajoute des lignes d'attaque au plateau du joueur défenseur.
    """
    # Supprimer les lignes du bas du plateau
    for _ in range(nb_lignes):
        jeu[joueur_defenseur]['grid'].pop(0)
        
        # Ajouter de nouvelles lignes avec un trou
        nouvelle_ligne = generer_ligne_avec_trou(LARGEUR_PLATEAU)
        jeu[joueur_defenseur]['grid'].append(nouvelle_ligne)


def verifier_lignes_deux(jeu, joueur):
    """
    Version modifiée de la fonction verifier_lignes pour le mode deux joueurs.
    
    Calcule les lignes complètes et gère l'attaque entre joueurs.
    """
    lignes_vides = 0

    # Parcourt chaque ligne de la grille
    for y in range(GRID_HEIGHT):
        ligne_complete = True
        for x in range(LARGEUR_PLATEAU):
            if jeu[joueur]['grid'][y][x] is None:
                ligne_complete = False
                break

        if ligne_complete:
            jeu[joueur]['grid'].pop(y)

            ligne_vide = [None] * LARGEUR_PLATEAU
            jeu[joueur]['grid'].insert(0, ligne_vide)

            lignes_vides += 1

    # Met à jour le score et le niveau en fonction des lignes effacées
    # Logique d'attaque entre joueurs
    if lignes_vides >= 1:
        # Détermine le joueur à attaquer
        joueur_cible = 'player2' if joueur == 'player1' else 'player1'
        
        # Nombre de lignes à envoyer = lignes_vides - 1
        ajouter_lignes_attaque(jeu, joueur, joueur_cible, lignes_vides)
    
    mise_a_jour_score_et_niveau(jeu[joueur], lignes_vides)

def fusionner_piece_deux(jeu, joueur):
    """
    Version modifiée de fusionner_piece pour le mode deux joueurs.
    
    Ajoute la pièce courante à la grille du joueur spécifié.
    """
    piece = jeu[joueur]['current_piece']
    forme = piece['forme']
    couleur = piece['couleur']
    hauteur = len(forme)
    largeur = len(forme[0])

    for rel_y in range(hauteur):
        for rel_x in range(largeur):
            if forme[rel_y][rel_x]:
                grille_y, grille_x = piece['y'] + rel_y, piece['x'] + rel_x
                if grille_y >= 0:  # Ne pas dessiner en dehors de la grille
                    jeu[joueur]['grid'][grille_y][grille_x] = couleur








def main():
    """Fonction principale du jeu avec modes avancés"""
    # Sélection du mode de jeu
    jeu = mode_selection_menu()

    if jeu is None and GAME_MODES['two_player']:
        global WINDOW_WIDTH

        WINDOW_WIDTH*=2
        jeu = creer_etat_jeu_deux_joueurs()
        jeu['player1']['next_piece'] = creer_piece()
        jeu['player2']['next_piece'] = creer_piece()
        nouvelle_piece_deux_joueurs(jeu, 'player1')
        nouvelle_piece_deux_joueurs(jeu, 'player2')
        initialiser_fenetre2()
        
        while not jeu['player1']['game_over'] or not jeu['player2']['game_over']:
            ev = donne_ev()
            if ev:
                type_evt = type_ev(ev)
                if type_evt == 'Touche':
                    traiter_touche_deux_joueurs(touche(ev), jeu)
        
            mettre_a_jour_jeu_deux_joueurs(jeu)
            dessiner_jeu_deux_joueurs(jeu)
            time.sleep(0.001)
    
        attendre_fin()
    print('a')
    if GAME_MODES['Polynomes_de_taille_N']:
        a=int(input("Entrez la hauteur de la piece"))
        for i in range(6):
            creer_piece_n(a)
            
    # Si aucun jeu n'est chargé, créer un nouveau
    if jeu is None:
        jeu = initialiser_jeu()
    
    if GAME_MODES['Polymynos_arbitraire']==True:
        charger_Poly()
    
    initialiser_fenetre()

    while not jeu['game_over']:
        gerer_entrees_utilisateur(jeu)
        mettre_a_jour_jeu(jeu)
        dessiner_jeu(jeu)
        time.sleep(0.001)
    
    attendre_fin()



BLOC_SIZE = 40
LARGEUR_PLATEAU = 10
GRID_HEIGHT = 20
WINDOW_WIDTH = LARGEUR_PLATEAU * BLOC_SIZE + 200
WINDOW_HEIGHT = GRID_HEIGHT * BLOC_SIZE
POLYMINO=[]

COLORS = ['cyan', 'yellow', 'purple', 'orange', 'blue', 'red', 'green']


if __name__ == '__main__':
    main()
