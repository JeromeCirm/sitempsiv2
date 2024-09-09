# 
#  exemple de fichier views_perso
#  sert à ajouter des appels au serveur django autrement que grâce à une fonction de menu
#  ne pas oublier de gérer les droits avec auth
# 
# peut aussi servir à remplacer les "vues" du fichier views.py :
# il suffit pour cela de créer une nouvelle vue perso
# puis d'utiliser urls_perso pour courtcircuiter l'appel à la vue initiale
#
# c'est ce qui est fait dans le modèle pour modifier la vue "recuperation_informations_home"
# et afficher un message "Voici les informations de la semaine : " en plus au début

from base.fonctions import auth
from .fonctions import *
from .models import Semaines,GroupesTD
import json

@auth(None)
def recuperation_informations_home_perso(request):
    response_data = {}
    if True: #try:
        lesgroupes=request.user.groups.all()
        if groupe_eleves in lesgroupes:
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])  
            msg=informations_colle_semaine_eleve(request.user,lasemaine)
            msg=['Voici les informations de la semaine : ']+msg
            lesgroupes=GroupeColles.objects.filter(eleves=request.user)
            lesTD=GroupesTD.objects.filter(semaine=lasemaine,groupe__in=lesgroupes)
            for x in lesTD:
                msg.append(x.texte)
            response_data["informations"]=msg
        elif est_colleur(request.user):
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])  
            msg=informations_colle_semaine_colleur(request.user,lasemaine)
            response_data["informations"]=msg              
    #except:
        debug("erreur dans recuperation_informations_home_perso")
    return HttpResponse(json.dumps(response_data), content_type="application/json")    
