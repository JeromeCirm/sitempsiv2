#
# fonctions pouvant être utilisées dans les menus du site
# une fonction définie ici remplace la même fonction définie dans menus_defaut
# 
# seules les fonctions mises dans liste_menus_perso seront utilisables dans les menus

from django.shortcuts import render
from .menus_defaut import inscription_colles_individuelles,gestion_colles_individuelles

liste_menus_perso=['menu_perso','inscription_colles_philo','gestion_colles_philo']

def menu_perso(request,id_menu,context):
    context["message"]="Bonjour "+str(request.user.username)
    return render(request,'gestionmenu/menu_perso.html',context)

def inscription_colles_philo(request,id_menu,context):
    context["matiere"]="philo"
    return inscription_colles_individuelles(request,id_menu,context)

def gestion_colles_philo(request,id_menu,context):
    context["matiere"]="philo"
    return gestion_colles_individuelles(request,id_menu,context)
