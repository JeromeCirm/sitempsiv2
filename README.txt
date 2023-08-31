Général : 
 * l'accès à un menu/une fonction se fait avec les groupes : 
 * chaque menu a un/des gestionnaires (qui ont tous les droits)  et un/des groupes qui peuvent utiliser le menu
   (sauf pour gestion_menu, s'il est présent, accessible si et seulement si la personne gère un menu)
 * groupes créés : eleves, profs, generic, gestion_colle (facultatif : colleurs_math, colleurs_physique, colleurs_anglais, colleurs_philo )
 * un colleur est une personne qui a une entrée dans Infocolleur, indépendamment du groupe
 * dans info_colleur : indiquer une ligne permet de renseigner un colleur qui n'a pas encore de créneaux
 * les groupes "colleurs_math", etc... permettent de donner accès à une partie des documents du site
 * dans gestionmenu/fonctions : debug() est définie pour afficher dans la console en mode débug et ne rien faire sinon


!!!!!
!! Attention quand on modifie un fichier perso
!! Bien vérifier qu'il est pris en compte au démarrage
!! (pas de message "pas de fichier __perso")
!! en cas d'erreur dans le fichier perso, il est oublié
!! et le fichier modele prend la place 
!! (enlever les "try except" si cela pose probleme)
!!!!

Avant de lancer en local : 
 * dans sitempsi : modifier  "settings_perso" 
 * dans base : modifier "settings_perso"
 * dans gestionmenu : modifier "settings_perso"
( pour un modele de fichiers: cf "settings_modele" à chaque fois)
 * lancer le script remise_a_zero.py du répertoire principale pour une première initialisation

Avant de lancer le vrai site : 
 * penser à modifier à nouveau les fichiers "perso", attention dans sitempsi a gérer correctement la sécurité
 * passer DEBUG à False !

Modifs pour changer le comportement du site: (dans gestionmenu)
* dans menus_perso,views_perso,urls_perso : il y a des modeles pour cela
* tout fichier *_perso*  est hors-git par définition et peut être ajouté
  (indispensable pour ajouter des templates persos)
* une fonction dans menus_perso remplace la même dans menu_defaut
* une url lue dans urls_perso remplace la meme url dans urls.py
* dans views, "home" est appelée en cas de problème, on peut la modifier si besoin


#########################################
###############   Partie travail
#########################################

A faire : 
* trouver comment créer une "clef django secure" -> dans remise_a_zero??
* enlever la copie de db.sqlite3
# la fonction debug affiche un message en console en mode debug
# elle ne fait rien sinon : possible de la modifier pour qu'elle
# log le message dans un fichier éventuellement (tentative de piratage par ex)
  
******* Dans menus_defaut : 
colloscope à finir : 
  -envoyer un mail au groupe
contact : 
  - ouvrir un navigateur mail? pas indispensable sans doute
  - possibilité pour les profs d'envoyer vraiment le mail depuis le serveur?
gestion des menus : 
   - autoriser à dire quels groupes peuvent lire
   - mettre par défaut les groupes autorisés à lire la racine du menu que l'on gère
   - autoriser à mettre toutes les fonctions? risqué - à réfléchir -> juste admin sans doute
sondages : 
  - à faire !!
colles :
   - à faire : formulaire pour faire le bilan/remplir la déclaration des heures de colle ( en cours : cf marc en perso)

****** base
   - imposer un mail correct la première fois?
   - option dans settings pour eleves/prof/colleur pour ce point ? ou juste dans initialisation ?
   - possibilité d'activer les comptes eleves par mail si on rentre un mail?? peu utile

**** template home:
    - erreur si pas eleve car information n'est pas définie : pas clean, à rendre plus propre

Dans l'ordre d'importance déroissante : 
   - gestion des colles : trop lent pour le python
   - gérer l'obligation de valider le compte par mail ?
   - sondage

Bonus rapide :
 - lire ses notes pour les colleurs?
