#
# fonctions internes
#

from django.contrib.auth import authenticate,login
from django.shortcuts import render,redirect
from wsgiref.util import FileWrapper
from django.http.response import HttpResponse
from django.http import FileResponse
from .models import *
from base.models import Utilisateur
from django.contrib.auth.models import User,Group
from django.db.models import Case,When
from .settings import *
import datetime
from sitempsi.settings import DEBUG

if DEBUG:
    def debug(*args):
        print(*args)
else:
    def debug(*args):
        pass

def joli_nom(user):  # renvoie le login ou   prénom+nom si cela a été renseigné
    try:
        if user.last_name!="":
            return user.first_name+" "+user.last_name
        return user.username
    except:
        return "vide"

def date_fr(date,annee=False):
    # transforme la date en francais, avec ou sans l'année
    try:
        if annee: 
            return date.strftime("%d/%m/%y")
        else:
            return date.strftime("%d/%m")
    except:
        return "None"

# échange deux éléments d'un requete liste selon le champ ordre
def echange(liste,ordre1,ordre2): 
    liste.filter(ordre__in=[ordre1,ordre2]).update(ordre=Case(When(ordre=ordre1,then=ordre2),When(ordre=ordre2,then=ordre1)) )

def est_gestionnaire_menu(user,menu):
    # teste si l'utilisateur est gestionnaire du menu
    for x in menu.gestionnaires.all():
        if x==user:
            return True
    return False

def autorise_menu(user,menu):
    # teste si on autorise ce menu pour l'utilisateur 
    if menu.fonction=="gestion_menu":
        menus_en_gestion=Menu.objects.filter(gestionnaires=user)
        return len(menus_en_gestion)>0
    lesgroupes=user.groups.all()
    if user.is_superuser:
        return True
    for x in menu.groupes.all():
        if x in lesgroupes:
            return True
    return est_gestionnaire_menu(user,menu)

def menu_navigation(request):
    # liste des menus accessibles à l'utilisateur connecté
    # gestion_menu est à part : autorisé pour tous les gestionnaires de menu
    liste=Menu.objects.all().order_by('ordre')
    tableau=[]
    for item in liste : 
        if item.parent==0 and autorise_menu(request.user,item):
            subtableau=[]
            for subitem in liste : 
                if subitem.parent==item.id and autorise_menu(request.user,subitem):
                    if subitem.fonction[0:4]=="lien":
                        subtableau.append((subitem.nom,subitem.id,subitem.fonction[4:],True))
                    else:
                        subtableau.append((subitem.nom,subitem.id,subitem.fonction,False))
            tableau.append((item.nom,item.id,item.fonction,subtableau))
    return tableau

def creation_compte(login,password,liste_groupe=[],oblige_change_mdp=True,donnees={},efface_existant=False):
    try:
        if efface_existant:
            try:
                User.objects.get(username=login).delete()
            except:
                pass
        user=User.objects.create_user(username=login,password=password)
        if "prenom" in donnees:
            user.first_name=donnees["prenom"]
        if "nom" in donnees:
            user.last_name=donnees["nom"]
        else:
            user.last_name=login
        if "email" in donnees:
            user.email=donnees["email"]
        user.save()
        utilisateur=Utilisateur.objects.create(user=user,en_attente_confirmation=False,doit_changer_mdp=oblige_change_mdp)        
        utilisateur.save()
        for group in liste_groupe:
            user.groups.add(group)
        return user
    except:
        return None

def est_eleve(user):
    usergroupes=user.groups.all()
    return groupe_eleves in usergroupes
    
def est_generic(user):
    usergroupes=user.groups.all()
    return groupe_generic in usergroupes

def est_prof(user):
    usergroupes=user.groups.all()
    return groupe_profs in usergroupes

def est_colleur(user):
    # user est-il un colleur?
    res=InfoColleurs.objects.filter(colleur=user)
    return len(res)>0

def est_gestionnaire_colle(user,colleur_name=None):
    # colleur_name est-il un colleur pour user? ou user est-il un gestionnaire tout court si None ?
    if colleur_name==None:
        res=InfoColleurs.objects.filter(prof=user)
    else:
        res=InfoColleurs.objects.filter(colleur=colleur_name,prof=user)
    return len(res)>0

def semaine_en_cours():
    # cherche la semaine en cours. Renvoi la première sinon
    try:
        semaine=Semaines.objects.filter(date__lte=datetime.date.today()).order_by('-date')
        if len(semaine)>0:
            # on renvoie la dernière semaine commençant avant aujourd'hui
            return semaine[0]
        else:
            # on renvoie la première semaine
            semaine=Semaines.objects.all().order_by('date')
            return semaine[0]
    except:
        # pas de semaines créées pour l'instant
        return None

def informations_colle_semaine_eleve(user,semaine=None):
    # renvoie une list de messages à afficher concernant les colles de la semaine, les TD, etc.. de l'éleve
    if semaine==None:
        semaine=semaine_en_cours() # on récupère la semaine en cours
    lesgroupes=GroupeColles.objects.filter(eleves=user)
    lescolles=Colloscope.objects.filter(semaine=semaine,groupe__in=lesgroupes)
    msg=[]
    for item in lescolles : 
        colle=item.creneau
        msg.append("colle de "+colle.matière+" avec "+joli_nom(colle.colleur)+" "+colle.jour+" à "+colle.horaire+" en "+colle.salle)
    lescolles=Colloscope_individuel.objects.filter(semaine=semaine,eleve=user)
    for item in lescolles : 
        colle=item.creneau
        msg.append("colle de "+colle.matière+" avec "+joli_nom(colle.colleur)+" "+colle.jour+" à "+colle.horaire+" en "+colle.salle)
    return msg 

def informations_colle_semaine_colleur(user,semaine=None):
    # renvoie une list de messages à afficher concernant les colles de la semaine du colleur
    if semaine==None:
        semaine=semaine_en_cours() # on récupère la semaine en cours
    lescreneaux=CreneauxColleurs.objects.filter(colleur=user)
    lescolles=Colloscope.objects.filter(semaine=semaine,creneau__in=lescreneaux)
    msg=[]
    for item in lescolles : 
        colle=item.creneau
        msg.append("Groupe "+str(item.groupe.numero)+" "+colle.jour+" à "+colle.horaire+" en "+colle.salle)
    lescolles=Colloscope_individuel.objects.filter(semaine=semaine,creneau__in=lescreneaux)
    for item in lescolles : 
        colle=item.creneau
        msg.append(joli_nom(item.eleve)+" "+colle.jour+" à "+colle.horaire+" en "+colle.salle)
    return msg 

def auth_prog_colle_math(request):
    try:
        menu=Menu.objects.get(fonction="programme_colle_math")
        return est_gestionnaire_menu(request.user,menu)
    except:
        return False
    
def download_file(request,letype,pk,id_menu=0):
    def extension(nomfichier):
        l=nomfichier.split(".")
        if len(l)==1:
            return ""
        return "."+l[-1]
    def aux(nomfichier):  # pour enlever les caractères bizarres !
        res=""
        for x in nomfichier:
            if ord(x)<256:
                res+=x
        return res
    if letype=="file":
        try : 
            obj=Fichier.objects.get(id=pk)
            if autorise_menu(request.user,obj.menu):
                document = open('private_files/fichiers/'+str(pk)+extension(obj.nomfichier),'rb')
                response = HttpResponse(FileWrapper(document),content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename="'+aux(obj.nomfichier)+'"'
                return response
        except: 
            debug("fichier absent avec icone téléchargement")
            return redirect('/home')
    if letype=="fiche":
        try : 
            obj=FichierFiches.objects.get(id=pk)
            if request.user.username in gestionnaires_pdf:
                document = open('private_files/fiches/'+str(obj.fiche.année)+'/'+str(obj.id)+extension(obj.nomfichier),'rb')
                response = HttpResponse(FileWrapper(document),content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename="'+aux(obj.nomfichier)+'"'
                return response
        except: 
            debug("fiche absente avec icone téléchargement")
            return redirect('/home')
    if letype=='prog':
        try:
            if autorise_menu(request.user,Menu.objects.get(id=id_menu)):
                obj=ProgColle.objects.get(id=pk)
                document = open('private_files/prog_colle_'+str(id_menu)+'/prog'+str(pk)+extension(obj.nomprogramme),'rb')
                response = HttpResponse(FileWrapper(document),content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename="prog'+str(obj.nomprogramme)+'"'
                return response
        except: 
            debug("fichier absent avec icone téléchargement")
            return redirect('/home')
    if letype=='exos':
        try:
            if autorise_menu(request.user,Menu.objects.get(id=id_menu)):
                obj=ProgColle.objects.get(id=pk)
                document = open('private_files/prog_colle_'+str(id_menu)+'/exos'+str(pk)+extension(obj.nomexercices),'rb')
                response = HttpResponse(FileWrapper(document),content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename="exos'+str(obj.nomexercices)+'"'
                return response
        except: #fichier absent avec icone téléchargement?
            debug("fichier absent avec icone téléchargement")
            return redirect('/home')
    debug("tentative de piratage download")
    return redirect('/home')
 
def trouvegroupe(eleve, grps):
    '''
    il exixste sûrement mieux !
    '''
    for g in grps:
        if grps.filter(pk=g.pk, eleves__pk=eleve.pk).exists():
            return g
    return None

def nbang(nb):
    h, minu = nb // 3, nb % 3
    minu *= 20
    if minu:
        return '{}h{}min'.format(h, minu)
    else:
        return '{}h'.format(h)

def nbphilo(nb):
    h, minu = nb // 2, nb % 2
    minu *= 30
    if minu:
        return '{}h{}min'.format(h, minu)
    else:
        return '{}h'.format(h)

def faitbilan(colleur, bilan, matiere):
    '''
    on l'appelle avec
    bilan = variable globale définie dans initialisation_perso
    [('Sept-Oct', 1, 5),
    ('Novembre', 6, 9), etc. ]
    '''

    # créneaux du colleur
    creneaux=CreneauxColleurs.objects.filter(colleur=colleur)
    # colles [groupe] dans ces créneaux (du colleur)
    colles=Colloscope.objects.filter(creneau__in=creneaux)
    # # colles individuelles dans ces créneaux (du colleur)
    # collesind=Colloscope.objects.filter(creneau__in=creneaux)
    # notes du colleur
    Notes = NotesColles.objects.filter(colleur=colleur)
    # groupes de colles
    grps = GroupeColles.objects.all()

    def calcul(mois, s1, s2):
        '''
        calcul à partir des groupes prévus par le colloscope, pas les colles individuelles
        '''
        cptgrptheo = 0 # nombre de groupe avec au moins un élève interrogé
        cpteleve = 0 # nobre d'élèves interrogés
        scolles = colles.filter(semaine__numero__range=[s1,s2])

        # méthode 1 seulement les colles officielles
        for item in scolles:
            els = item.groupe.eleves.all()
            cptgrp = False
            # on détermine pour un groupe s'il y a au moins une note
            # (et on décompte les élèves)
            for el in els:
                note = Notes.filter(eleve=el, semaine=item.semaine)
                if note: # il y a bien une note (rappel: pour ce colleur)
                    cpteleve += 1
                    cptgrp = True # donc on compte tout le groupe
                    # debug(note[0].note, el.username)
            if cptgrp:
                cptgrptheo += 1
        # comptage par colloscope

        # méthode 2, plus fine
        # comptage des notes hors colloscope (inclure les colle individuelles de Jérôme ?? à comprendre et faire)
        cptsupp = 0
        # comptage sur toutes les notes
        cptvraiel = 0
        verbose = ''
        # complexité pourrie
        for note in Notes:
            if note.note and s1 <= note.semaine.numero <= s2:
                cptvraiel += 1      # note à décompter
                grcolle = trouvegroupe(note.eleve, grps)
                if len(scolles.filter(semaine=note.semaine, groupe=grcolle)) == 0:
                    # note en plus de celle du colloscope à décompter
                    verbose += '{} en s.{}, '.format(note.eleve.username, note.semaine)
                    cptsupp += 1

        return {'mois': mois, 's1': s1, 's2': s2, 'cpteleve': cpteleve,
                'cptgrptheo': cptgrptheo,
                'nbheures': cptgrptheo,
                'cptsupp': cptsupp,
                'cptvraiel': cptvraiel,
                'nbangheures': nbang(cptvraiel),
                'verbose': verbose}

    def calculphilo(mois, s1, s2):
        '''
        calcul à partir des groupes prévus par le colloscope, pas les colles individuelles
        '''
        #cptgrptheo = 0 # nombre de groupe avec au moins un élève interrogé
        cpteleve = 0 # nobre d'élèves interrogés
        #scolles = colles.filter(semaine__numero__range=[s1,s2])

        # # méthode 2, plus fine
        # # comptage des notes hors colloscope (inclure les colle individuelles de Jérôme ?? à comprendre et faire)
        # cptsupp = 0
        # comptage sur toutes les notes
        cptvraiel = 0 # nombre d'élèves interrogés (note ou n.n. mais pas abs.)
        cptabs = 0  # nombre d'absents
        verbose = ''
        # complexité pourrie
        for note in Notes: # != 0 peut-être à modifier...
            if note.note != 0 and s1 <= note.semaine.numero <= s2 and note.creneau in creneaux:
                # si note.creneau existe c'est bien une colle individuelle
                if note.note == -1:  # absent
                    cptabs += 1
                    verbose += '{} absent en s.{}, '.format(note.eleve.username, note.semaine)
                else:
                    #verbose += '{} noté en s.{}, '.format(note.eleve.username, note.semaine)
                    cptvraiel += 1      # note à décompter
                    # note en plus de celle du colloscope à décompter


        return {'mois': mois, 's1': s1, 's2': s2, 'cpteleve': 0,
                'cptgrptheo': 0,
                'nbheures': 0,
                'cptsupp': cptabs,
                'cptvraiel': cptvraiel,
                'nbangheures': nbphilo(cptvraiel),
                'verbose': verbose}


    L = []
    if matiere != 'philo':
        for mois, s1, s2 in bilan:
            L.append(calcul(mois, s1, s2))
    else:
        for mois, s1, s2 in bilan:
            L.append(calculphilo(mois, s1, s2))
        # pass # à faire
        # L = [{'mois': 'cc', 's1': 1, 's2': 2, 'cpteleve': 20,
                # 'cptgrptheo': 21,
                # 'nbheures': 22,
                # 'cptsupp': 23,
                # 'cptvraiel': 24,
                # 'nbangheures': 25,
                # 'verbose': 'verbbbb'}]

    return L