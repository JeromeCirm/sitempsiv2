#
# Exemple d'utilisation des fonctions d'initialisation
# en fournissant les données directement dans le code sous forme de liste
# il est possible de créer une version perso où ces données sont 
# importées depuis un fichier extérieur bien sûr
#

from gestionmenu.initialisation import *

# liste des fonctions disponibles dans le menu d'initialisation
# key : la fonction
# value : le texte affiché dans le menu d'initialisation
liste_initialisation={
    "init_complete_perso" : 'reinitialisation complète du site (avec les données persos)',
    "creation_comptes_prof" : 'création des comptes profs ',
    "creation_comptes_eleves" : 'reinitialisation des comptes élèves',
    "creation_comptes_colleurs" : 'reinitialisation des comptes colleurs (hors profs)',
    "creation_groupes_creneaux_colloscope" : 'création groupes de colles, créneaux de colles et colloscope',
    "creation_colloscope_philo" : 'création des créneaux de colles de philo et gestion du dico colles-persos',
    "init_menu" : 'reinitialisation des menus du site',
    "creation_semaines" : 'création des semaines',
    "importation_des_fiches_eleves" : 'Importation des fiches élèves',
    "importation_des_fiches_renseignements" : 'Importation des fiches renseignements élèves'}

# menu du site :
# liste de menu, sous le format ["nom_menu","fonction_menu",liste_login_gestionnaire,liste_nom_groupe,[liste_sous_menu] ]
# un sous_menu a le même format sans la liste des sous_menu
# nom de groupes et non "groupes" pour éviter les problèmes à l'initialisation
# ces noms de groupes sont dans liste_groupes
liste_groupes=["profs","eleves","generic","gestion_colles","math","physique","anglais","philo"]
liste_menu=[
    ["Infos de la classe","",["prof_math"],["eleves","profs","generic","math","physique","anglais","philo"],[
        ["Colloscope personnel","colloscope",["prof_math"],["eleves","profs","math","physique","anglais","philo"]],
        ["Colloscope par semaine","colloscope_semaine",["prof_math"],["eleves","profs","generic"]],
        ["Gestion des colles","gestion_colles",["prof_math"],["gestion_colles"]],
        ["Trombinoscope","fichier_unique",["prof_math"],["eleves","profs","generic","math","physique","anglais","philo"]],
        ["Liste des mails","contacts",["prof_math"],["eleves","profs","math","physique","anglais","philo"]],
        ["Emploi du temps","fichier_unique",["prof_math"],["eleves","profs","generic","math","physique","anglais","philo"]],
        ["Partage de fichiers","liste_fichiers",["prof_math","prof_anglais","prof_philo","prof_physique","prof_info","prof_si"],["profs"]],
        ]],
    ["Anglais","",["prof_anglais"],["eleves","profs","generic"],[
    ]],     
    ["Informatique",["prof_info"],["eleves","profs","generic"],[
        ["Python-navigateur","lienhttps://console.basthon.fr/",["prof_info"],["eleves","profs","generic"]],         
    ]],     
    ["Math","",["prof_math"],["eleves","profs","generic","math"],[
        ["Cours de math","liste_fichiers",["prof_math"],["eleves","profs","generic","math"]],
        ["Documents de math","liste_fichiers",["prof_math"],["eleves","profs","generic"]],
        ["Programme de colle de math","programme_colle",["prof_math"],["eleves","profs","generic","math"]],
    ]],
    ["Philosophie","",["prof_philo"],["eleves","profs","generic"],[
        ["Documents de philo","liste_fichiers",["prof_philo"],["eleves","profs","generic"]],
        ["S'inscrire en colle de philo","inscription_colles_philo",["prof_philo"],["eleves"]],
        ["Gestion des colles de philo","gestion_colles_philo",["prof_philo"],[]],
    ]],  
    ["Physique","",["prof_physique"],["eleves","profs","generic","physique"],[
        ["Documents de physique","liste_fichiers",["prof_physique"],["eleves","profs","generic"]],
        ["Programme de colle de physique","liste_fichiers",["prof_physique"],["eleves","profs","generic","physique"]],
    ]],  
    ["Données personnelles","",["prof_math"],["eleves","profs","math","physique","anglais","philo"],[
        ["Rentrer les notes de colles","rentrer_notes_colles",["prof_math"],["gestion_colles","math","physique","anglais","philo"]],
        ["Lire ses notes de colles","lire_notes_colles",["prof_math"],["eleves"]], 
        ["Lire les notes de colles par semaine","lire_notes_colleurs",["prof_math"],["gestion_colles"]],
        ["Fiche de renseignement","fiche_renseignements",["prof_math"],["eleves"]],
        ["Lire les fiches élèves","lire_fiches_eleves",["prof_math"],["profs"]],
        ["Création du fichier Pronote","creation_fichier_pronote",["prof_math"],["gestion_colles"]],
        ["Paramètres du compte","parametres_compte",["prof_math"],["eleves","profs","math","physique","anglais","philo"]],
        ["Gestion des menus","gestion_menu",["prof_math"],[]],
        ["Initialisation","initialisation",["prof_math"],[]] 
    ]]
    ]

# les semaines : 
# à partir du  1er lundi de septembre, on alterne :  nombre de semaines non actives (vacances et début),  nombre de semaines actives
les_semaines=[
    2,5,    # toussaint
    2,7,    # noel
    2,5,    # fevrier
    2,6,    # paques
    2,10
    ]

# dico des profs
# key : login
# liste : Nom,prénom,mail    dans l'ordre et facultatif (laissé vide si absent)
mdp_profs="prof"
oblige_changement_mdp_profs=False # oblig le changement de mdp au premier login
dico_prof={"prof_math": ["Nom_math","prenom_math","mail_prof_math@none.com"],"prof_physique": ["Nom_phy","prenom_phy"],"prof_anglais": [],'prof_info' : ["Nom_info"],'prof_si' : [],'prof_philo' : []}

# dictionnaire des élèves : 
# key : login de l'élève
# value : Nom,Prénom  officiel
mdp_eleves="fenelon"
oblige_changement_mdp_eleves=False # oblig le changement de mdp au premier login
dico_eleves={"eleve1": ["eleve1","Adrien","mail_eleve1"],"eleve2" :["eleve2","Alexis"],
"eleve3":["eleve3","Nina"],"eleve4":["eleve4","Sophie"],"eleve5":["eleve5","Quentin"],"eleve6":["eleve6","Dimitri"],
"eleve7":["eleve7","Lucie"],"eleve8":["eleve8","Guillaume"],"eleve9":["eleve9","Jean"],"eleve10":["eleve10","Gaspard"],
"eleve11":["eleve11","Adrien"],"eleve12":["eleve12","Panila"],"eleve13":["eleve13","Charles","mail_eleve13"],"eleve14":["eleve14","Camille"],
"eleve15":["eleve15","Guillaume"],"eleve16":["eleve16","Elodie"],"eleve17":["eleve17","Charles"],"eleve18":["eleve18","Max"],
"eleve19":["eleve19","Joseph"],"eleve20":["eleve20","Elias"],"eleve21":["eleve21","Laura"],"eleve22":["eleve22","Victor"],
"eleve23":["eleve23","Maxime"],"eleve24":["eleve24","Guillaume"],"eleve25":["eleve25","Laura"],
"eleve26":["eleve26","Maxence"],"eleve27":["eleve27","Victor"],"eleve28":["eleve28","Samuel"],"eleve29":["eleve29","Juliette"],
"eleve30":["eleve30","Victor"],"eleve31":["eleve31","Timothée"],"eleve32":["eleve32","Maxence"],
"eleve33":["eleve33","Nina"],"eleve34":["eleve34","Adrien"],"eleve35":["eleve35","Leon"],"eleve36":["eleve36","Lea"],
"eleve37":["eleve37","Adrien"],"eleve38":["eleve38","Eleonore"],"eleve39":["eleve39","Joseph"],"eleve40":["eleve40","Benjamin"],
"eleve41":["eleve41","Antoine"],"eleve42":["eleve42","Orphee"],"eleve43":["eleve43","Guillaume"],
"eleve44":["eleve44","Gaspard"],"eleve45":["eleve45","Guillaume"],"eleve46":["eleve46","Charlotte"],"eleve47":["eleve47","Sophie"]}

# dictionnaire des colleurs:
# key : login
# value : Référent,Matière,Nom,prénom,mail dans l'ordre et facultatif sauf pour "référent" et "matiere", le login du prof référent
# matière n'a pas forcément besoin d'être écrit comme le nom du groupe associé mais est en lien avec ce qui est indiqué 
# dans dico_inscriptions_colles_individuelles en cas de colloscope individuel
mdp_colleurs="colleur"
oblige_changement_mdp_colleurs=False # oblig le changement de mdp au premier login
dico_colleurs={"prof_math": ["prof_math","math"],"colleur_math7": ["prof_math","math"],"colleur_math1": ["prof_math","math","nom colleur1","prenom colleur1","mail colleur1"],"colleur_math2": ["prof_math","math"],"colleur_math3": ["prof_math","math"],
"colleur_math4": ["prof_math","math"],"colleur_math5": ["prof_math","math"],"prof_info": ["prof_math","math"],"colleur_math6": ["prof_math","math"],
'prof_physique':["prof_physique","physique"],'colleur_phys1':["prof_physique","physique"],'colleur_phys2':["prof_physique","physique"],'colleur_phys3':["prof_physique","physique"],
'colleur_phys4':["prof_physique","physique"],
"colleur_ang1": ["prof_anglais","anglais"],"colleur_ang2": ["prof_anglais","anglais"],"colleur_ang3": ["prof_anglais","anglais"],"colleur_ang4": ["prof_anglais","anglais"],"colleur_ang5": ["prof_anglais","anglais"],
"prof_philo": ["prof_philo","philo"],"colleur_philo1" : ["prof_philo","philo"],"colleur_philo2" : ["prof_philo","philo"]}

# liste des créneaux de colle
creneaux_math=[
        ["prof_info","lundi","17h","403"],
        ["colleur_math4","lundi","14h","404"],
        ["colleur_math2","lundi","16h","401"],
        ["colleur_math5","lundi","14h","203"],
        ["colleur_math3","lundi","16h","116"],
        ["colleur_math1","jeudi","17h","301"],
        ["prof_math","mercredi","11h","203"],
        ["colleur_math7","mardi","17h","405"],
        ["prof_info","lundi","18h","403"],
        ["colleur_math4","lundi","15h","404"],
        ["colleur_math3","lundi","17h","116"],
        ["colleur_math2","lundi","15h","401"],
        ["colleur_math1","jeudi","18h","301"],
        ["colleur_math6","mardi","15h","213"],
        ["prof_math","mercredi","12h","203"],
        ["colleur_math7","mardi","18h","405"],
        ]
creneaux_physique=[
        ["colleur_phys4","jeudi","16h","303"],
        ["colleur_phys2","jeudi","16h","306"],
        ["colleur_phys3","mardi","16h","301"],
        ["prof_physique","lundi","14h","217"],
        ["colleur_phys1","mardi","17h","201"],
        ["colleur_phys2","jeudi","17h","306"],
        ["colleur_phys3","mardi","17h","301"],
        ["prof_physique","lundi","15h","217"],
        ]
creneaux_anglais=[
        ["colleur_ang2","jeudi","16h","115"],
        ["colleur_ang3","jeudi","17h","47"],
        ["colleur_ang4","mercredi","17h","01"],
        ["colleur_ang1","jeudi","17h","305"],
        ["colleur_ang2","jeudi","17h","115"],
        ["colleur_ang3","jeudi","18h","47"],
        ["colleur_ang5","mercredi","17h","116"],
        ["colleur_ang1","jeudi","18h","305"],
        ]
creneaux_philo=[
        ["prof_philo","mardi","16h","115"],
        ["prof_philo","mardi","17h","115"],
        ["colleur_philo1","jeudi","16h","115"],
        ["colleur_philo1","jeudi","17h","115"],
        ["colleur_philo2","jeudi","14h","115"],
]

# liste des groupes de colles:
groupes_colles=[["eleve6","eleve23","eleve46"],
        ["eleve1","eleve9","eleve38"],
        ["eleve30","eleve32","eleve35"],
        ["eleve11","eleve29","eleve37"],
        ["eleve4","eleve33","eleve42"],
        ["eleve8","eleve10","eleve18"],
        ["eleve19","eleve22","eleve24"],
        ["eleve5","eleve16"],
        ["eleve26","eleve44","eleve47"],
        ["eleve13","eleve15","eleve27"],
        ["eleve28","eleve31","eleve39"],
        ["eleve14","eleve20","eleve36"],
        ["eleve34","eleve40","eleve41"],
        ["eleve17","eleve25","eleve45"],
        ["eleve2","eleve12","eleve43"],
        ["eleve3","eleve7","eleve21"],
    ]

# gestion des colloscopes avec possibilité d'inscription pour les élèves

# on définit le nombre de colle par an : 3 max avec une non garantie
# un élève peut supprimer la 3ème colle d'un autre élève si c'est pour 
# y mettre une de ses deux premières colles.
dico_inscriptions_colles_individuelles=[
    { "responsables" : ["prof_philo"], "matiere" : "philo","titre" : "philosophie","max_par_eleve" : 3 , "max_garanti" : 2}
]

def init_complete_perso(context):
    creation_comptes_prof(context)
    init_menu(context)
    creation_comptes_eleves(context)
    creation_comptes_colleurs(context)
    creation_semaines(context)
    creation_groupes_creneaux_colloscope(context)
    creation_colloscope_philo(context)
    context["msg"].append(" ** fin de l'initialisation compète")

def creation_groupe(context,laliste=liste_groupes):
    for nom in laliste:
        try:
            Group(name=nom).save()
        except:
            pass

def creation_comptes_prof(context):
    creation_groupe(context,["profs","gestion_colles"])
    dico={}
    for x in dico_prof:
        l=dico_prof[x]
        d={}
        try:
            d["nom"]=l[0]
            d["prenom"]=l[1]
            d["email"]=l[2]
        except:
            pass
        dico[x]=d
    maj_comptes_profs(context,mdp_profs,dico,garde_ancien=False,oblige_changement_mdp=oblige_changement_mdp_profs)
    gr=Group.objects.get(name="gestion_colles")
    liste_gestion=[]
    for key in dico_colleurs:
        prof=dico_colleurs[key][0]
        if prof not in liste_gestion:
            liste_gestion.append(prof)
    for x in liste_gestion:
        try:
            leprof=User.objects.get(username=x)
            leprof.groups.add(gr)
        except:
            context["msg"].append(" impossible de donner les droits gestion_colles à "+x)
    context["msg"].append(" ** fin de la création des comptes profs")

def init_menu(context):
    creation_groupe(context)
    lesgroupes={}
    for item in liste_menu:
        gr=[]
        for x in item[3]:
            if x not in lesgroupes:
                lesgroupes[x]=Group.objects.get(name=x)
            gr.append(lesgroupes[x])
        item[3]=gr
        for subitem in item[4]:
            gr=[]
            for x in subitem[3]:
                if x not in lesgroupes:
                    lesgroupes[x]=Group.objects.get(name=x)
                gr.append(lesgroupes[x])
            subitem[3]=gr
    creation_menu_site(context,liste_menu)
    context["msg"].append(" ** fin de la création des menus")

def creation_compte_generic(context):
    creation_groupe(context,["generic"])
    user=creation_compte("eleve",mdp_eleves,[groupe_generic],oblige_change_mdp=False,donnees={},efface_existant=True)
    user.utilisateur.autorise_modif=False
    user.utilisateur.save()
    context["msg"].append(" ** fin de la création du compte générique")

def creation_comptes_eleves(context):
    creation_groupe(context,["eleves"])
    creation_compte_generic(context)
    dico={}
    for x in dico_eleves:
        l=dico_eleves[x]
        d={}
        try:
            d["nom"]=l[0]
            d["nomofficiel"]=l[0]
            d["prenom"]=l[1]
            d["prenomofficiel"]=l[1]
            d["email"]=l[2]
        except:
            pass
        dico[x]=d
    maj_comptes_eleves(context,mdp_eleves,dico,garde_ancien=False,oblige_changement_mdp=oblige_changement_mdp_eleves)
    context["msg"].append(" ** fin de la création des comptes élèves")

def creation_comptes_colleurs(context):
    creation_groupe(context)
    dico={}
    for x in dico_colleurs:
        l=dico_colleurs[x]
        d={}
        try:
            d["referent"]=l[0]
            d["matiere"]=l[1]
            d["nom"]=l[2]
            d["prenom"]=l[3]
            d["email"]=l[4]
        except:
            pass
        dico[x]=d
    maj_comptes_colleurs(context,mdp_colleurs,dico,garde_ancien=False,oblige_changement_mdp=oblige_changement_mdp_colleurs)
    context["msg"].append(" ** fin de la création des comptes colleurs")

def creation_semaines(context):
    maj_semaines(context,les_semaines,annee_courante)
    context["msg"].append(" ** fin de la création des semaines.")

def creation_groupes_creneaux_colloscope(context):
    maj_creneaux_colleurs(context,creneaux_math)
    maj_creneaux_colleurs(context,creneaux_physique,True)
    maj_creneaux_colleurs(context,creneaux_anglais,True)
    maj_groupes_colles(context,groupes_colles)
    liste=[]
    for semaine in range(1,31):
        for groupe in range(1,17):
            liste.append([Semaines.objects.get(numero=semaine),GroupeColles.objects.get(numero=groupe),
                        CreneauxColleurs.objects.get(numero=1+(semaine+groupe)%16,matière="math")])
            if (semaine+groupe)%2==0:
                autre="physique"
            else:
                autre="anglais"
            liste.append([Semaines.objects.get(numero=semaine),GroupeColles.objects.get(numero=groupe),
                        CreneauxColleurs.objects.get(numero=1+((semaine+groupe)//2)%8,matière=autre)]) 
    maj_colloscope(context,liste)
    context["msg"].append(" ** fin de la création Groupes, créneaux et colloscope.")

def importation_des_fiches_eleves(context):
    # on choisit ici d'effacer le pdf s'il est déjà présent
    # et de prendre en compte les prénoms/noms officiels
    importation_fiches_eleves(context,efface=True,remplace_officiel=True,impose_usuel=True)
    context["msg"].append(" ** fin de l'importation des fiches élèves.")

def importation_des_fiches_renseignements(context):
    # on importe des anciennes fiches renseignements
    # en effaçant les éventuelles fiches déjà présentes pour le même couple (login,année)
    importation_fiches_renseignements(context,efface=True)
    context["msg"].append(" ** fin de l'importation des fiches renseignements élèves.")

def creation_colloscope_philo(context):
    gestion_dico_colles_perso(context)
    maj_creneaux_colleurs(context,creneaux_philo,True)
    lessemaines=Semaines.objects.all()
    lescreneaux=CreneauxColleurs.objects.filter(matière="philo")
    Colloscope_individuel.objects.filter(creneau__in=lescreneaux).delete()
    for uncreneau in lescreneaux:
        for unesemaine in lessemaines:
            unecolle=Colloscope_individuel(semaine=unesemaine,creneau=uncreneau)
            unecolle.save()
    context["msg"].append(" ** fin de la création des créneaux de philo ")

def gestion_dico_colles_perso(context):
    Gestion_colles_individuelles.objects.all().delete()
    for val in dico_inscriptions_colles_individuelles:
        unegestion=Gestion_colles_individuelles(matiere=val["matiere"],titre=val["titre"],max_par_eleve=val["max_par_eleve"],max_garanti=val["max_garanti"],modif_par_eleves=False) 
        unegestion.save()
        for name in val["responsables"] :
            user=User.objects.get(username=name)
            unegestion.responsables.add(user)
        unegestion.save()  
    context["msg"].append(" ** fin de la gestion du dico des colles persos ")
