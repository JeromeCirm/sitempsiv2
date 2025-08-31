#
#  fonctions utiles pour l'initialisation du site
# l'initialisation se fait réellement à partir de initialisation_perso ou initialisation_modele
#

import os
import json
from django.contrib.auth.models import User
from django.core.files import File
from .models import *
from .settings import *
from .fonctions import creation_compte
import datetime

# on efface tous les profs et on les créé à nouveau
# sauf si garde_ancien est vrai
# mot de passe par défaut : mdp
# dico["login"] : dico des éléments à renseigner
#       (au choix : nom,prenom,mail )
def maj_comptes_profs(context,mdp,dico,garde_ancien=False,oblige_changement_mdp=True):
    a_effacer=User.objects.filter(groups=groupe_profs)
    if garde_ancien: 
        a_effacer=a_effacer.exclude(username__in=dico.keys())
    a_effacer.delete()
    for unprof in dico:
        try:
            user=User.objects.get(username=unprof)
            if groupe_profs in user.groups.all():
                context["msg"].append(unprof+" existe déjà en prof,")
            else:
                context["msg"].append(unprof+" existe déjà et n'est pas prof : on arrête.")
                return
        except:
            if creation_compte(unprof,mdp,[groupe_profs],oblige_changement_mdp,dico[unprof])==None:
                context["msg"].append("!!! erreur lors de la création du compte de "+unprof)
                return              
            context["msg"].append(unprof+" est créé,")

def maj_comptes_eleves(context,mdp,dico,garde_ancien=False,oblige_changement_mdp=True):
    anciens=User.objects.filter(groups=groupe_eleves)
    if garde_ancien: 
        anciens=anciens.exclude(username__in=dico.keys())
    doublons=User.objects.filter(username__in=dico.keys()).exclude(groups=groupe_eleves)
    if len(doublons)!=0:
        msg_s="!!! attention : au moins un login élève est déjà utilisé dans un autre rôle :"    # liste à vérifier, il y a déjà un utilisateur avec ce nom
        for x in doublons:
            msg_s+=" "+x.username+","
        context["msg"].append(msg_s)
        return
    Renseignements.objects.filter(login__in=[x.username for x in anciens],année=annee_courante).delete()
    anciens.delete()          # on efface tous les anciens élèves.   
    eleves_actuels=User.objects.filter(groups=groupe_eleves)
    logins={}
    for x in eleves_actuels:
        logins[x.username]=True
    for uneleve in dico:
        if uneleve not in logins:
            user=creation_compte(uneleve,mdp,[groupe_eleves],oblige_changement_mdp,dico[uneleve])
            if user==None:
                context["msg"].append("!!! erreur lors de la création du compte de "+uneleve)
                return
            try:
                prenomofficiel=dico[uneleve]["prenomofficiel"]
            except:
                prenomofficiel=""
            try:
                nomofficiel=dico[uneleve]["nomofficiel"]
            except:
                nomofficiel=uneleve
            renseignements=Renseignements.objects.create(login=uneleve,année=annee_courante,nomofficiel=nomofficiel,prenomofficiel=prenomofficiel)
            renseignements.save()

# on ne touche pas à un compte prof
# on garde un compte colleur si garde_ancien=True et qu'il est dans dico
# on supprime un colleur s'il n'est pas dans dico quoiqu'il arrive
def maj_comptes_colleurs(context,mdp,dico,garde_ancien=False,oblige_changement_mdp=True):
    try:
        liste_colleurs=InfoColleurs.objects.values_list("colleur__username",flat=True)
        a_effacer=User.objects.filter(username__in=liste_colleurs).exclude(groups=groupe_profs)
        if garde_ancien: 
            a_effacer=a_effacer.exclude(username__in=dico.keys())
        a_effacer.delete()
        for uncolleur in dico:
            d=dico[uncolleur]
            try:
                user=User.objects.get(username=uncolleur)
                if len(InfoColleurs.objects.filter(colleur=user))>0:
                    if user.groups.filter(name='eleves').exists():
                        context["msg"].append('!!! attention : '+uncolleur+" existe déjà en élève, impossible de le transformer en colleur ")
                        return
                    context["msg"].append(uncolleur+" existe déjà en colleur, ")
                else:
                    try:
                        referent=User.objects.get(username=d["referent"])
                    except:
                        context["msg"].append("erreur lors de la récupération du prof référent "+d["referent"])
                        return
                    InfoColleurs(colleur=user,prof=referent,matière=d["matiere"]).save()
                    user.groups.add(Group.objects.get(name=d["matiere"]))
                    context["msg"].append(uncolleur+" existe déjà : transformé en colleur ("+d["referent"]+")")
            except:
                user=creation_compte(uncolleur,mdp,[Group.objects.get(name=d["matiere"])],oblige_changement_mdp,d)
                if user==None:
                    context["msg"].append("!!! erreur lors de la création du compte de "+uncolleur)
                    return              
                try:
                    referent=User.objects.get(username=d["referent"])
                except:
                    context["msg"].append("!!! erreur lors de la récupération du prof référent "+d["referent"])
                    return
                InfoColleurs(colleur=user,prof=referent,matière=d["matiere"]).save()
                context["msg"].append(uncolleur+" est créé ("+d["referent"]+")")
    except:
        context["msg"].append("!!! erreur dans la fonction maj_comptes_colleurs")

def creation_menu_site(context,liste):
    try:
        Menu.objects.all().delete()
        ordre=0
        for item in liste:
            x=Menu(nom=item[0],fonction=item[1])
            x.ordre=ordre
            x.parent=0
            x.save()
            ordre+=1
            id=x.pk
            for y in item[2]:
                try:
                    x.gestionnaires.add(User.objects.get(username=y))
                except:
                    context["msg"].append("!!! erreur lors de l'ajout de "+y+" comme gestionnaire du menu "+item[0])
            for y in item[3]:
                try:
                    x.groupes.add(Group.objects.get(name=y))
                except:
                    context["msg"].append("!!! erreur lors de l'ajout de "+y+" comme groupe au menu "+item[0])                    
            ordre_s=0
            for subitem in item[4]:
                x=Menu(nom=subitem[0],fonction=subitem[1])
                x.ordre=ordre_s
                x.parent=id
                x.save()
                for y in subitem[2]:
                    try:
                        x.gestionnaires.add(User.objects.get(username=y))
                    except:
                        context["msg"].append("!!! erreur lors de l'ajout de "+y+" comme gestionnaire du sous-menu "+subitem[0])
                for y in subitem[3]:
                    try:
                        x.groupes.add(Group.objects.get(name=y))
                    except:
                        context["msg"].append("!!! erreur lors de l'ajout de "+y+" comme groupe au sous-menu "+subitem[0])     
                ordre_s+=1
    except:
        context["msg"].append("!!! erreur lors de la création des menus")

def trouve_premier_lundi_septembre(annee):
    jour=datetime.date(year=annee,month=9,day=1)
    unjour=datetime.timedelta(days=1)
    while jour.strftime("%A")!="lundi":
        jour=jour+unjour
    return jour

def maj_semaines(context,liste,annee):
    Semaines.objects.all().delete()
    semaine=trouve_premier_lundi_septembre(annee)
    unesemaine=datetime.timedelta(days=7)
    flag=False
    nb_semaine=1
    for x in liste:
        for _ in range(x):
            if flag:
                Semaines(numero=nb_semaine,date=semaine).save()
                nb_semaine+=1
            semaine=semaine+unesemaine
        flag=not flag

def supprime_creneaux(context,matiere="",depart=1):
    try:
        CreneauxColleurs.objects.filter(matière=matiere,numero__gte=depart).delete()
    except:
        context["msg"].append("!!! impossible de supprimer les créneaux de "+matiere)

def maj_creneaux_colleurs(context,liste,garde_ancien=False,depart=1):
    if not garde_ancien:
        CreneauxColleurs.objects.all().delete()
    numero=depart
    for item in liste:
        user=User.objects.get(username=item[0])
        matiere=InfoColleurs.objects.get(colleur=user).matière
        CreneauxColleurs(colleur=user,jour=item[1],horaire=item[2],salle=item[3],matière=matiere,numero=numero).save()
        numero+=1

def maj_groupes_colles(context,liste,depart=1):
    GroupeColles.objects.filter(numero__gte=depart).delete()
    numero=depart
    for item in liste:
        gr=GroupeColles(numero=numero)
        gr.save()
        for x in item:
            user=User.objects.get(username=x)
            gr.eleves.add(user)
        gr.save()
        numero+=1

# on efface les semaines à partir de "a_partir", ou rien si cela vaut -1
def maj_colloscope(context,liste,a_partir=-1):
    if a_partir>=0:
        Colloscope.objects.filter(semaine__numero__gte=a_partir).delete()
    for item in liste:
        Colloscope(semaine=item[0],groupe=item[1],creneau=item[2]).save()

def importation_fiches_eleves(context,efface=False,remplace_officiel=True,impose_usuel=True,force_remplacement=False):
    #
    # à gérer : année courante uniquement ici ou autoriser tout ?
    #
    # importe à partir du répertoire private_files/transfert_fiche
    # login_annee_json pour le fichier contenant le json du dictionnaire à mettre dans Renseignements
    # login_annee.pdf pour un fichier pdf à mettre en plus de la fiche élève
    # si le fichier pdf est déjà présent : on efface ou non l'ancien selon l'argument "efface"
    # remplace_officiel décide si on remplace les champs prénom/nom officiel par ceux de l'import, s'ils existent
    # utile pour mettre à False si ces champs ont déjà été remplis
    # impose_usuel décide si on utilise le prénom/nom officiel comme prénom/nom d'usage (first_name/last_name de user)
    # (pris en compte uniquement si l'annee est bien l'année courante)
    try:
        listefichier=[ f for f in os.listdir('private_files/transfert_fiche') if os.path.isfile(os.path.join('private_files/transfert_fiche',f)) ]
    except:
        context["msg"].append("Impossible d'obtenir le liste des fichiers à importer.")
        return 
    listefichier.sort()
    print(listefichier)
    for name in listefichier:
        if len(name)>=10:
            login=name[:-9].lower()
            annee=name[-8:-4]
            ext=name[-4:]
        else:
            context["msg"].append('!!! fichier '+name+' non traité.')
            continue
        if annee!=str(annee_courante):
            continue
        try:
            lafiche=Renseignements.objects.get(login=login,année=annee)
        except:
            context["msg"].append('!!! pas de fiche pour '+login+' en '+annee)
            continue
        if lafiche.rne_lycee!=None and not force_remplacement:
            context["msg"].append('fiche ignorée pour  '+login+' en '+annee)
            continue
        if ext=='json':
            try:
                f=open('private_files/transfert_fiche/'+name,"r")
                dico=json.load(f)
                f.close()
                for key,val in dico.items():
                    try:
                        if key not in ['nomofficiel','prenomofficiel'] or remplace_officiel:
                            if key=="date_naissance_officiel":
                                val=datetime.datetime.strptime(val,"%d/%m/%Y").strftime("%Y-%m-%d")
                            lafiche.__setattr__(key,val)
                    except:
                        pass
                lafiche.save()
                if impose_usuel and annee==str(annee_courante):
                    try:
                        user=User.objects.get(username=login)
                        user.first_name=lafiche.prenomofficiel
                        user.last_name=lafiche.nomofficiel
                        user.save()
                    except:
                        context["msg"].append('!!! erreur lors de l\'affectation prénom/nom usuel de '+name)
            except:
                context["msg"].append('!!! erreur lors de la lecture de '+name)
        elif ext=='.pdf':
            if efface:
                FichierFiches.objects.filter(fiche=lafiche,nomfichier=name).delete()
            f=open('private_files/transfert_fiche/'+name,'rb')
            lepdf=FichierFiches(fiche=lafiche,nomfichier=name)
            lepdf.save()
            lepdf.fichier.save('private_files/transfert_fiche/'+name,File(f))
            lepdf.save() # utile?
        else:
            context["msg"].append('!!! fichier '+name+' non traité.')
            continue
        context["msg"].append('   fichier '+name+' traité')

def importation_fiches_renseignements(context,efface=True):
    # !!!
    # !!! ne gère pas une fiche présente si efface=False
    # importe à partir du répertoire private_files/fiches_renseignements.json
    # qui doit être le dump json d'une liste d'enregistrement de fiches Renseignement
    # on récupère les champs qui sont cohérents
    # efface décide si on efface les fiches déjà présentes ou non
    f=open("private_files/fiches_renseignements.json","r")
    liste=json.load(f)
    for d in liste:
        if efface:
            try:
                Renseignements.objects.filter(login=d["login"],année=d["année"]).delete()
            except:
                pass
        r=Renseignements(login=d["login"],année=d["année"])
        for key,val in d.items():
            if key in Renseignements.__dict__:
                r.__setattr__(key,val)
        r.save()
    f.close()

