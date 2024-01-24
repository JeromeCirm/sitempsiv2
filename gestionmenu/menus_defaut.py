#
#  liste des fonctions par défaut qui peuvent être utilisées pour un menu
#

# les fichiers associés à liste_fichiers et fichier_unique sont sauvegardés dans
# le répertoire private_files/fichiers/ (changeable dans models.py)

from django.contrib.auth import authenticate,login
from django.shortcuts import render,redirect
from .models import *
from .forms import *
from base.models import Utilisateur
from django.contrib.auth.models import User,Group
from django.db.models import Case,When
from .settings import *
from .fonctions import *
try:
    from gestionmenu.initialisation_perso import *
except ImportError:
    print("pas de fichier initialisation_perso")
    from gestionmenu.initialisation_modele import *
import datetime

liste_menus_defaut = ['liste_fichiers','parametres_compte','gestion_menu','fichier_unique','initialisation','contacts',
                      'programme_colle','rentrer_notes_colles',
                      'lire_notes_colles','lire_notes_colleurs','lire_fiches_eleves','fiche_renseignements',
                      'creation_fichier_pronote','colloscope','colloscope_semaine','gestion_colles','gestion_sondages',
                      'sondages','resultat_sondages','bilan_colleurs']

def liste_fichiers(request,id_menu,context):
    le_menu=Menu.objects.get(id=id_menu)
    if le_menu.parent!=0:
        parent=Menu.objects.get(id=le_menu.parent)
        le_menu.nom=parent.nom+' : '+le_menu.nom
    context['lemenu']=le_menu
    # on récupère la liste des fichiers de la page
    gestionnaire=est_gestionnaire_menu(request.user,le_menu)
    if gestionnaire:
        context['fichier']=Fichier.objects.filter(menu=le_menu)
    else:
        context['fichier']=Fichier.objects.filter(menu=le_menu).exclude(date_parution__gt=datetime.datetime.now())
    for k in context['fichier']:
        k.description=k.description.split("\r\n")
    # on détermine si l'utilisateur est un gestionnaire de cette page
    context['gestionnaire']=gestionnaire
    return render(request,'gestionmenu/listefichiers.html',context)

def parametres_compte(request,id_menu,context):
    try:
        user=request.user
        if not user.utilisateur.autorise_modif:
            context["interdit"]=True
            return render(request,'gestionmenu/parametres_compte.html',context)
        context['changepassword']=False
        context['changepasswordreussi']=False
        if  request.method=="POST" and "password" in request.POST:
                context['changepassword']=True
                old=request.POST.get('password')
                new=request.POST.get('newpassword')
                newconfirm=request.POST.get('newpasswordconfirm')
                user=authenticate(request,username=user.username,password=old)
                if (new==newconfirm) and (user is not None):
                    context['changepasswordreussi']=True
                    user=User.objects.get(username=user.username)
                    user.set_password(new)
                    user.save()
                    login(request,user)
        if  request.method=="POST" and "mail" in request.POST:
            user.email=request.POST["mail"]
            if autoriser_changement_nom:
                user.first_name=request.POST["prenomusage"]
                user.last_name=request.POST["nomusage"]
            user.save()
            context["msg"]="paramètres mis à jour"
        context["mail"]=request.user.email
        context["prenomusage"]=request.user.first_name
        context["nomusage"]=request.user.last_name
        context["autoriser_changement_nom"]=autoriser_changement_nom
        return render(request,'gestionmenu/parametres_compte.html',context)
    except:
        debug("erreur paramètre compte")
        return redirect('/home')

def gestion_menu(request,id_menu,context):
    # menu spécifique
    # est autorisé dès que l'utilisateur gère au moins un menu
    lesmenus=Menu.objects.filter(gestionnaires=request.user,parent=0)
    menus=[]
    for unmenu in lesmenus:
        lessousmenu=Menu.objects.filter(parent=unmenu.id)
        menus.append({"lemenu":unmenu,"lessousmenus":lessousmenu})
    context['menus']=menus
    lesmenus_unique=Menu.objects.filter(gestionnaires=request.user,fonction='fichier_unique')
    for unmenu in lesmenus_unique:
        if unmenu.parent!=0:
            parent=Menu.objects.get(pk=unmenu.parent)
            unmenu.nom=parent.nom+": "+unmenu.nom
            try:
                fichier=Fichier.objects.get(menu=unmenu)
                unmenu.nomfichier="fichier : "+fichier.nomfichier
            except:
                unmenu.nomfichier="pas de fichier "
    context['menus_unique']=lesmenus_unique
    return render(request,'gestionmenu/gestion_menu.html',context)

def fichier_unique(request,id_menu,context):
    le_menu=Menu.objects.get(id=id_menu)
    if le_menu.parent!=0:
        parent=Menu.objects.get(id=le_menu.parent)
        le_menu.nom=parent.nom+' : '+le_menu.nom
    context['lemenu']=le_menu
    # on récupère le fichier de la page
    try:
        lefichier=Fichier.objects.get(menu=le_menu)
        return download_file(request,"file",lefichier.pk)
    except:
        return render(request,'gestionmenu/fichier_unique.html',context)
    
def initialisation(request,id_menu,context):
    try: 
        if request.method=='POST':
            action=request.POST['action']
            if action in liste_initialisation:
                context["msg"]=[]
                globals()[str(action)](context)
            else:
                debug("erreur nom fonction initialisation")
        context["lesactions"]=liste_initialisation
        return render(request,'gestionmenu/initialisation.html',context)
    except:
        debug("erreur dans la fonction initialisation")
        return redirect('/home')

def contacts(request,id_menu,context):
    usergroupes=request.user.groups.all()
    if groupe_eleves in usergroupes:
        context["profs"]=User.objects.filter(groups=groupe_profs).distinct().order_by("last_name")
        context["nb_profs"]=len(context["profs"])
        liste_colleurs=[]
        for x in InfoColleurs.objects.all().order_by("colleur__last_name"):
            if x.colleur not in liste_colleurs and x.colleur not in context["profs"]:
                liste_colleurs.append(x.colleur)
        context["colleurs"]=liste_colleurs 
    elif groupe_profs in usergroupes or est_colleur(request.user):
        context["eleves"]=GroupeColles.objects.all().order_by('numero')
    return render(request,'gestionmenu/contacts.html',context)

def programme_colle(request,id_menu,context):
    progs=ProgColle.objects.filter(menu__id=id_menu).values()
    context["id_menu"]=id_menu
    context["contenu"]=progs
    context["titre"]=Menu.objects.get(id=id_menu).nom
    context['gestionnaire']=est_gestionnaire_menu(request.user,Menu.objects.get(id=id_menu))
    return render(request,'gestionmenu/prog_colle.html',context)

def rentrer_notes_colles(request,id_menu,context):
    context["semaine"]=semaine_en_cours() 
    lessemaines=Semaines.objects.all().order_by("numero")
    context["lessemaines"]=[{"numero":x.numero,"date":date_fr(x.date,True)} for x in lessemaines]
    if est_gestionnaire_colle(request.user):
        listecolleurs=[]
        for x in InfoColleurs.objects.filter(prof=request.user).order_by("colleur__username"):
            listecolleurs.append(x.colleur)
        context["listecolleurs"]=listecolleurs
    return render(request,'gestionmenu/rentrer_notes_colles.html',context)

def lire_notes_colles(request,id_menu,context):
    return render(request,'gestionmenu/lire_notes_colles.html',context)

def lire_notes_colleurs(request,id_menu,context):
    if not est_gestionnaire_colle(request.user):
        debug("tentative de piratage lire_notes_colleurs")
        return redirect('/home')
    context["semaine"]=semaine_en_cours() 
    lessemaines=Semaines.objects.all().order_by("numero")
    context["lessemaines"]=[{"numero":x.numero,"date":date_fr(x.date,True)} for x in lessemaines]
    return render(request,'gestionmenu/notes_colles_semaine.html',context)

def lire_fiches_eleves(request,id_menu,context):
    annee=annee_courante
    context["annee"]=annee_courante
    context["selection"]="false"
    if request.method=="POST":
        try:
            context["selection"]="true"
            menu=Menu.objects.get(pk=id_menu)
            login=request.POST['eleve']
            context['login']=login
            annee=int(request.POST['annee'])
            context["annee"]=annee
            eleve=Renseignements.objects.get(login=login,année=annee)
            if request.POST["action"]=='ajout' and (request.user.username in gestionnaires_pdf):
                if 'fichier' in request.FILES:
                    obj=FichierFiches.objects.create(fiche=eleve)
                    form=FichierFormFichier(request.POST,request.FILES,instance=obj)
                    if form.is_valid():
                        new_fichier=form.save(commit=False)
                        new_fichier.nomfichier=request.FILES['fichier']
                        new_fichier.save()
                        return redirect('/menu/'+str(menu.id))
                context["eleve"]=request.POST['eleve']
                form=FichierFormFichier()
                context["form"]=form
                return render(request,'gestionmenu/ajout_fichier_fiche_eleve.html',context)
            donnees=RenseignementsFormProf(instance=eleve)
            context["donnees"]=donnees
            context["gestionnaire"]=request.user.username in gestionnaires_pdf
            if annee==annee_courante:
                try:
                    user=User.objects.get(username=login)
                    context["prenom"]=user.first_name
                    context["nom"]=user.last_name
                    context["mail"]=user.email
                except:
                    debug("utilisateur absent pour l'année courante")
            if context["gestionnaire"]:
                context["lesfichiers"]=FichierFiches.objects.filter(fiche=eleve)
        except:
            debug("erreur lire_fiche_eleves")
    return render(request,'gestionmenu/lire_renseignements.html',context)

def fiche_renseignements(request,id_menu,context):
    try:
        context["autoriser_changement_renseignement"]=autoriser_changement_renseignement
        obj=Renseignements.objects.get(login=request.user.username,année=annee_courante)
        if autoriser_changement_renseignement: 
            context["msg"]="Ne pas oublier de valider les modifications si besoin : "
            if not autoriser_changement_nom:
                context["msg"]+="( prénom et nom non modifiables )"
        else:
            context["msg"]="la fiche n'est pas modifiable actuellement"
        if request.method=="POST" and autoriser_changement_renseignement:
            form=RenseignementsForm(request.POST,instance=obj)
            if form.is_valid():
                form.save()
                request.user.email=request.POST["mail"]
                if autoriser_changement_nom: # test inutile avec les lignes au dessus à priori
                    request.user.first_name=request.POST["prenom"]
                    request.user.last_name=request.POST["nom"]
                request.user.save()
                context["msg"]="modifications enregistrées ! "
                context['form']=form
                context["mail"]=request.user.email
                context["prenom"]=request.user.first_name
                context["nom"]=request.user.last_name                
                return render(request,'gestionmenu/fiche_renseignements.html',context)
            context["msg"]="erreur dans le formulaire"
        else:
            form=RenseignementsForm(instance=obj)
        context['form']=form
        context["mail"]=request.user.email
        context["prenom"]=request.user.first_name
        context["nom"]=request.user.last_name         
    except:
        debug("erreur fiche_renseignements")
        return redirect('/home')
    return render(request,'gestionmenu/fiche_renseignements.html',context)

def creation_fichier_pronote(request,id_menu,context):
    if est_gestionnaire_colle(request.user):
        liste_colleurs=[x.colleur for x in InfoColleurs.objects.filter(prof=request.user)]
    else:
        debug("tentative d'utilisation de creation_fichier_pronote par un autre prof ")
        return redirect('/home/')
    semaines=Semaines.objects.all().order_by("numero")
    if request.method=="POST":
        semainedep=int(request.POST["semainedep"])
        try:
            semainedep=Semaines.objects.get(numero=semainedep)
        except:
            semainedep=semaines.first()
        semainefin=int(request.POST["semainefin"])
        try:
            semainefin=Semaines.objects.get(numero=semainefin)
        except:
            semainefin=semaines.last()
        if request.POST["quinzaine"]=="oui":
            quinzaine=True
        else : 
            quinzaine=False
        leseleves=User.objects.filter(groups=groupe_eleves).order_by("username")
        if quinzaine : 
            ecart=2
        else : 
            ecart=1
        txt="Nom;prenom"
        for _ in range(semainedep.numero,semainefin.numero+1,ecart):
            txt+=";20"
        txt+="\n"
        enplus=[]
        for user in leseleves:
            lafiche=Renseignements.objects.get(login=user.username,année=annee_courante)
            txt+=lafiche.nomofficiel+";"+lafiche.prenomofficiel
            for lasemaine in range(semainedep.numero,semainefin.numero+1,ecart):
                txt+=";"
                lesnotes=NotesColles.objects.filter(colleur__in=liste_colleurs,semaine__numero__gte=lasemaine,
                semaine__numero__lte=min(semainefin.numero,lasemaine+ecart-1),eleve=user)
                if len(lesnotes)>0:
                    if lesnotes[0].note==-1:
                        txt+='A'
                    elif lesnotes[0].note==-2:
                        txt+='N'
                    else:
                        txt+=str(lesnotes[0].note)
                if len(lesnotes)>1:
                    enplus+=lesnotes[1:]
            txt+="\n"
        txt.encode('latin1')
        sortie=open('private_files/colles_'+request.user.username+'.csv',"w",encoding="latin1")
        sortie.write(txt)
        sortie.close()
        context["enplus"]=enplus
        context["fichier"]=request.user.username+'.csv'
    else :
        semainedep=semaines.first()
        semainefin=semaines.last()
        quinzaine=False
    context["semaines"]=semaines
    context["semainedep"]=semainedep
    context["semainefin"]=semainefin
    context["quinzaine"]=quinzaine
    return render(request,'gestionmenu/creation_pronote.html',context)
    
def colloscope(request,id_menu,context):
    def maj_colloscope():
        # patch pour gérer l'ordre du colloscope
        context["colloscope"]=[(num,colloscope[num]) for num in sorted(colloscope.keys())]
    usergroupes=request.user.groups.all()
    context["user"]=request.user
    if groupe_eleves in usergroupes:
        # cas d'un élève
        groupes=GroupeColles.objects.filter(eleves=request.user)
        colles=Colloscope.objects.filter(groupe__in=groupes)
        colloscope={}
        for item in colles:
            s=item.semaine.numero
            if s not in colloscope:
                colloscope[s]=[]
            colloscope[s].append(('groupe',item.creneau))
        collesperso=Colloscope_individuel.objects.filter(eleve=request.user)
        for item in collesperso:
            s=item.semaine.numero
            if s not in colloscope:
                colloscope[s]=[]
            colloscope[s].append(('eleve',item.creneau))
        maj_colloscope()
        context["type"]="eleve"
        context["actuel"]=request.user
    elif est_gestionnaire_colle(request.user):
        # cas d'un prof responsable des colles
        context["prof"]="oui"
        l=[]
        for x in InfoColleurs.objects.values_list("colleur"): #.distinct()
            l.append(User.objects.get(id=x[0]))
        l.sort(key=lambda x: x.username)
        context["listecolleurs"]=l
        context["listeeleves"]=User.objects.filter(groups=groupe_eleves)
        if request.method=='POST':
            if "eleve" in request.POST:
                context["type"]="eleve"
                context["actuel"]=User.objects.get(username=request.POST["eleve"])
                groupes=GroupeColles.objects.filter(eleves=context["actuel"])
                colles=Colloscope.objects.filter(groupe__in=groupes)
                colloscope={}
                for item in colles:
                    s=item.semaine.numero
                    if s not in colloscope:
                        colloscope[s]=[]
                    colloscope[s].append(('groupe',item.creneau))
                leleve=User.objects.get(username=context["actuel"])
                collesperso=Colloscope_individuel.objects.filter(eleve=leleve)
                for item in collesperso:
                    s=item.semaine.numero
                    if s not in colloscope:
                        colloscope[s]=[]
                    colloscope[s].append(('eleve',item.creneau))      
                maj_colloscope()
                return render(request,'gestionmenu/colloscope.html',context)
            elif "colleur" in request.POST:
                context["actuel"]=User.objects.get(username=request.POST["colleur"])
        else:
            context["actuel"]=request.user
        creneaux=CreneauxColleurs.objects.filter(colleur=context["actuel"])
        colles=Colloscope.objects.filter(creneau__in=creneaux)
        colloscope={}
        for item in colles:
            s=item.semaine.numero
            if s not in colloscope:
                colloscope[s]=[]
            colloscope[s].append(('groupe',item.groupe,item.creneau))
        collesperso=Colloscope_individuel.objects.filter(creneau__in=creneaux)
        for item in collesperso:
            s=item.semaine.numero
            if s not in colloscope:
                colloscope[s]=[]
            colloscope[s].append(('eleve',item.eleve,item.creneau)) 
        maj_colloscope()
        context["type"]="colleur"
    elif est_colleur(request.user):
        # cas d'un colleur classique
        creneaux=CreneauxColleurs.objects.filter(colleur=request.user)
        colles=Colloscope.objects.filter(creneau__in=creneaux)
        colloscope={}
        for item in colles:
            s=item.semaine.numero
            if s not in colloscope:
                colloscope[s]=[]
            colloscope[s].append(('groupe',item.groupe,item.creneau))
        collesperso=Colloscope_individuel.objects.filter(creneau__in=creneaux)
        for item in collesperso:
            s=item.semaine.numero
            if s not in colloscope:
                colloscope[s]=[]
            colloscope[s].append(('eleve',item.eleve,item.creneau))              
        maj_colloscope()
        context["type"]="colleur"
        context["actuel"]=request.user
    else:
        context["type"]="rien"
    return render(request,'gestionmenu/colloscope.html',context)


def colloscope_semaine(request,id_menu,context):
    try:
        if est_prof(request.user) or est_colleur(request.user) or est_eleve(request.user) or est_generic(request.user):
            lessemaines=Semaines.objects.all().order_by("numero")
            context["lessemaines"]=[{"numero":x.numero,"date":date_fr(x.date,True)} for x in lessemaines]
            try:
                context["lasemaine"]=semaine_en_cours().numero
            except:
                context["lasemaine"]=0            
            if not est_generic(request.user):
                context["les_groupes"]=GroupeColles.objects.all()
            return render(request,'gestionmenu/colloscope_semaine.html',context)
        else:
            debug("tentative de piratage colosscope_semaine")
            return redirect('/home')
    except:
        debug("erreur dans colloscope_semaine")
        return redirect('/home')

def gestion_colles(request,id_menu,context):
    context["semaine"]=semaine_en_cours() 
    lessemaines=Semaines.objects.all().order_by("numero")
    context["lessemaines"]=[{"numero":x.numero,"date":date_fr(x.date,True)} for x in lessemaines]    
    context["lesgroupes"]=GroupeColles.objects.all()
    context["leseleves"]=User.objects.filter(groups=groupe_eleves)
    return render(request,'gestionmenu/gestion_colles.html',context)

def inscription_colles_individuelles(request,id_menu,context):
    lamatiere=Gestion_colles_individuelles.objects.get(matiere=context["matiere"])
    context["max_par_eleve"]=lamatiere.max_par_eleve
    context["max_garanti"]=lamatiere.max_garanti
    context["modif_par_eleves"]=lamatiere.modif_par_eleves
    context["titre"]=lamatiere.titre
    return render(request,'gestionmenu/inscription_colles_individuelles.html',context)

def gestion_colles_individuelles(request,id_menu,context):     
    lamatiere=Gestion_colles_individuelles.objects.get(matiere=context["matiere"])
    context["max_par_eleve"]=lamatiere.max_par_eleve
    context["max_garanti"]=lamatiere.max_garanti
    context["titre"]=lamatiere.titre
    context["leseleves"]=User.objects.filter(groups=groupe_eleves)
    if request.method=="POST" and request.user in lamatiere.responsables.all():
        if 'check' in request.POST:
            lamatiere.modif_par_eleves=True
        else:
            lamatiere.modif_par_eleves=False
        lamatiere.save()
    context["modif_par_eleves"]=lamatiere.modif_par_eleves
    return render(request,'gestionmenu/gestion_colles_individuelles.html',context)

def gestion_sondages(request,id_menu,context): 
    return render(request,'gestionmenu/gestion_sondages.html',context)

def sondages(request,id_menu,context): 
    return render(request,'gestionmenu/sondages.html',context)

def resultat_sondages(request,id_menu,context): 
    return render(request,'gestionmenu/resultat_sondages.html',context)

def bilan_colleurs(request,id_menu,context):
    if True: #try:
        if est_prof(request.user) or est_colleur(request.user) or est_gestionnaire_colle(request.user):

            if est_prof(request.user):
                context["prof"]="oui"
                info = InfoColleurs.objects.filter(colleur=request.user)[0]
                debug(info)
                matiere = info.matière
                l=[]
                for x in InfoColleurs.objects.all(): #.distinct()
                    #if matiere == x.matière:   # fonctionnement normal
                    if matiere == x.matière or \
                        (matiere == 'math' and x.matière=='philo'): # voir aussi la philo
                        # matiere == 'math' : rajout pour que le prof de maths puisse tout voir
                        l.append(x.colleur)
                l.sort(key=lambda x: x.username)
                context["listecolleurs"]=l
            else:
                context["prof"]="colleur"
            if request.method=='POST':
                if "colleur" in request.POST:
                    context["actuel"]=User.objects.get(username=request.POST["colleur"])
                    # on réactualise actuel avec la sélection (si prof)
            else:
                context["actuel"]=request.user
                # par défaut
            info = InfoColleurs.objects.filter(colleur=context["actuel"])
            context['matiere'] = info[0].matière
            L = faitbilan(context["actuel"], bilan, context['matiere'])
            context["Laafficher"] = L
            return render(request,'gestionmenu/menu_bilan.html',context)
        else:
            debug("tentative de piratage bilan_colleurs")
            return redirect('/home')
    #except:
        debug("erreur dans bilan_colleurs")
        return redirect('/home')



