Tetris
------

Execution du programme:
------------------
-Definitions des constantes
-Définition des Tetrominos et leurs couleurs
-Initialisation de la fenetre
-Si le mode deux joueur est acivé deux dictionnaire (player1,player2) sont stocké dans le dictionnaire jeu
-Initialisation de l'etat du jeu de base (grille,piece,game over...) dans un dictionaire
-Creation d'une nouvelle piece au hasard dans piece_current.
-prise en compte des entrées utillisateur
-quitte si q est presse
-bouge rotation de la piece si haut est presse verifie le si il n'y a pas de collision
-accelere la piece vers le bas si bas est presse jusqu'a colision.
-bouge la piece vers gauche ou droite si la touche haut gauche est presse
-mise a jour par le deplacement vers le bas de la piece actuelle
-dessiner toute la piece actuelle et les espaces deja occupe par les piece precedente
-a quasiment tous les deplacement des pieces les colisions sont checker pour voir si la piece peut etre bouge
si la piece ne peut plus bouger vers le bas alors le game over est activés
-Si le joueur appuie sur le mode Decay les pieces

fonction principale:
-------------------
-appliquer_deplacement:Fonction qui deplace toute les cellules de la piece courrante de peux import combien ont dit

-nouvelle_forme_rotatee:verifie et realise une rotation a 90 de la matrice courrante


-verifier_lignes:verifie les lignes une par une puis les enleves si elle sont complete fera appelle au code de mise a jour
de niveau pour rajouter le score

-piece_en_collision:verifie si les Element de la matrice courrante ne sont pas en colision avec des piéces du plateau
ou en dehors du plateau il appelle a la fusion est don a l'arret des piéces si le deplacement vers le bas n'est plus
possible.

-dessiner_jeu: Dessine le plateau le score le niveau ,etc..

-main:Programme principale du jeu

-initialiser_jeu:initialise l'etat du jeu initiale qui sera sous forme de dictionnaire puis cree une nouvelle piece qui
qui sera la piece courrante

-traiter_touche:traite les entress utillisateurs

-Toute les fonctions deux joueur sont les meme fonctions que les fonctions de 1 joeur mais concu pour traivailler avec un etat de jeux ou il y a deux grille definies


Variantes ajoutes:
-----------------
#ancienne version
-La variantes ajoutes et tres simplement implementé dans la fonctions mise_a_jour_score_et_niveau
et  finalement ne prend q'une seule ligne  "jeu['score'] += points * jeu['level']#Variantes Points liés au niveau"
nous multiplions donc le score par le niveau .le niveau est calcule par le nombre de ligne complete.

#nouvelle version
-Toute les version ont été ajouté le mode multijoueur,decay,sauvegarde,pause

-Polyminos arbitraire:lis simplement les données d'un fichier texte
Difficulte:
----------
#ancienne version
-Les plus grandes difficultés rencontrées ont été, sans aucun doute, liées au travail sur les matrices, en particulier
pour la rotation de matrices imbriquées. J'ai trouvé cela difficile au début, car j'avais une approche assez naïve.
Une grande source d'inspiration a été ce gist de Timur Bakibayev(https://gist.github.com/timurbakibayev/1f683d34487362b0f36280989c80960c)
,dans lequel il utilise des objets pour résoudre le problème. Cependant, comme je ne pouvais pas utiliser d'objets,
j'ai choisi de sauvegarder l'état du plateau et celui de la pièce dans deux dictionnaires distincts. Cette méthode m'a
permis de conserver simplement les coordonnées de la pièce en cours, puis de parcourir la matrice de cette pièce et de la comparer à la grille.

-Le second défi concernait principalement les calculs mathématiques pour le placement correct des pièces et la détection
 des collisions. Pour cela, un exemple qui m'a beaucoup aidé est celui-ci :
https://api.arcade.academy/en/latest/examples/tetris.html

#nouvelle version

-2 joueur les fonctionnalitées deux joueur n'ont pas été extrement difficile a implémenter mais les fonctions on du etre récrite
pour fonctioner avec un deuxieme joueur sinon l'ecriture de  ce code c'est fait de maniére assez fluide

-Sauvegarde et Chargement:C'est deux fonctionnalitées on étes les plus dure a implémenter nous avons opter pour le json
pour sa flexibillite et sa gestion hiérarchique des données.

