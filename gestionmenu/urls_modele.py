# 
#  exemple de fichier url_perso
#  sert à ajouter des appels au serveur django autrement que grâce à une fonction de menu
#  ou à remplacer une vue existante
#
# c'est par exemple ce qui est fait ici en remplaçant la vue "recuperation_informations_home"
# pour lui ajouter un petit message en plus (cf views_modele)

from django.urls import path
# à remplacer par  "from . import views_perso as v"  à priori pour être cohérent
# si c'est un fichier urls_perso.py
from . import views_modele as v

# on liste ici les urls et les fonctions associées
# avec ou sans paramètre

urlpatterns_perso = [
    path('recuperation_informations_home',v.recuperation_informations_home_perso,name='recuperation_informations_home'),
]