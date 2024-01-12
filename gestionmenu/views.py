#
# liste des fonctions appelées lorsque l'on lit une url
# le fonction principale est menu qui appelle les fonctions correspondantes de menus_defaut et menus_perso
# en gérant les droits définis par les groupes/gestionnaires dans le modele Menu
# les autres fonctions correspondent à la partie API de l'application
# pour ces dernières, les droits sont gérés en accord avec une utilisation "classique"
# (seuls les profs peuvent lire les fiches, etc...)

from django.shortcuts import render,redirect
from base.fonctions import auth
from .models import *
from .forms import *
from django.db.models import Max
from wsgiref.util import FileWrapper
from django.http.response import HttpResponse
from django.http import FileResponse
import json
from collections import defaultdict
from .fonctions import *
from .menus_defaut import *
try:
    import gestionmenu.menus_perso as mp
except ImportError:
    print("pas de fichier menus_perso")
    import gestionmenu.menus_modele as mp
liste_menus_perso=mp.liste_menus_perso

# suite dans settings? ou dans fonction ?
import sys
sys.path.append("..")
from base.settings import TITRE_SITE

@auth(None)
def menu(request,numero):
    context={"menu":menu_navigation(request)}
    context["titresite"]=TITRE_SITE
    if True: #try:
        lemenu=Menu.objects.get(pk=numero) 
        if autorise_menu(request.user,lemenu):
            nom_fonction=str(lemenu.fonction)
            if nom_fonction in liste_menus_perso:
                return mp.__dict__[str(nom_fonction)](request,numero,context)
            elif nom_fonction in liste_menus_defaut:
                return globals()[str(nom_fonction)](request,numero,context)
        return redirect('/home')
    #except:
        debug('erreur dans la fonction : enlever try except de la fonction menu de views.py')
        return redirect('/home')

@auth(None)
def home(request):
    try:
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        lessemaines=Semaines.objects.all().order_by("numero")
        context["lessemaines"]=[{"numero":x.numero,"date":date_fr(x.date,True)} for x in lessemaines]
        try:
            context["lasemaine"]=semaine_en_cours().numero
        except:
            context["lasemaine"]=0
        lesgroupes=request.user.groups.all()
        if groupe_eleves in lesgroupes:
            context["eleve"]=True
            try:
                context["annonce"]=Divers.objects.get(label="annonce").contenu
            except:
                context["annonce"]=""
        if groupe_profs in lesgroupes:
            if request.method=='POST':
                try:
                    annonce=Divers.objects.get(label='annonce')
                    annonce.contenu=request.POST.get('annonce')
                    annonce.save()  
                except:
                    try:
                        annonce=Divers.objects.create(label='annonce',contenu=request.POST.get('annonce'))
                        annonce.save() 
                    except:
                        debug("erreur : pas de création possible pour divers mais récupération de l'annonce impossible, dans 'home'")
            context["prof"]=True
            try:
                context["annonce"]=Divers.objects.get(label="annonce").contenu
            except:
                debug("erreur : pas d'annonce disponible pour l'instant")
                context["annonce"]=""
        return render(request,'gestionmenu/home.html',context)
    except:
        debug("erreur dans home")
        context={"menu":menu_navigation(request)}
        return render(request,'gestionmenu/home.html',context)

@auth(None)
def recuperation_informations_home(request):
    response_data = {}
    try:
        lesgroupes=request.user.groups.all()
        if groupe_eleves in lesgroupes:
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])  
            msg=informations_colle_semaine_eleve(request.user,lasemaine)
            response_data["informations"]=msg
        elif est_colleur(request.user):
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])  
            msg=informations_colle_semaine_colleur(request.user,lasemaine)
            response_data["informations"]=msg
    except:
        debug("erreur dans recuperation_informations_home")
    return HttpResponse(json.dumps(response_data), content_type="application/json")    

@auth(None)
def ajout_fichier(request,pk):
    try:
        menu=Menu.objects.get(id=pk)
        if menu.fonction!="liste_fichiers" or not est_gestionnaire_menu(request.user,menu):
            debug("tentative piratage ajout_fichier")
            return redirect('/home')
        form=FichierForm()
        if request.method=="POST":
            obj=Fichier.objects.create(description="bidon",ordre=0,menu=menu)
            form=FichierForm(request.POST,request.FILES,instance=obj)
            if form.is_valid():
                new_fichier=form.save(commit=False)
                try:
                    res=Fichier.objects.all().aggregate(Max('ordre'))
                    new_fichier.ordre=res['ordre__max']+1
                except :
                    new_fichier.ordre=1
                if 'fichier' in request.FILES:
                    new_fichier.nomfichier=request.FILES['fichier']
                new_fichier.date_parution=request.POST["date_parution"]
                try:
                    new_fichier.save()
                except:
                    new_fichier.date_parution=datetime.datetime.now()
                    new_fichier.save()
                return redirect('/menu/'+str(pk))
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['form']=form
        context['idmenu']=pk
        return render(request,'gestionmenu/ajout_fichier.html',context)
    except:
        debug("erreur dans ajout_fichier")
        return redirect('/home')

@auth(None)
def supprime_fichier(request,pk):
    try:
        obj=Fichier.objects.get(id=pk)
        menu=obj.menu
        if not est_gestionnaire_menu(request.user,menu):
            debug("tentative de piratage supprime_fichier")
            return redirect('/home')
        if request.method=="POST" and "validation" in request.POST:
                obj.delete()
                return redirect('/menu/'+str(menu.id))
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['obj']="le fichier "+str(obj.nomfichier)
        return render(request,'gestionmenu/delete.html',context)
    except:
        debug("erreur supprime_fichier")
        return redirect('/home')

@auth(None)
def supprime_fiche(request,pk):
    try:
        obj=FichierFiches.objects.get(id=pk)
        if not request.user.username in gestionnaires_pdf:
            debug("tentative de piratage supprime_fichier")
            return redirect('/home')
        if request.method=="POST" and "validation" in request.POST:
                obj.delete()
                return redirect('/home')
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['obj']="le fichier "+str(obj.nomfichier)
        return render(request,'gestionmenu/delete.html',context)
    except:
        debug("erreur supprime_fichier")
        return redirect('/home')

@auth(None)
def modifie_fichier(request,pk):
    try:
        obj=Fichier.objects.get(id=pk)
        menu=obj.menu
        if menu.fonction!="liste_fichiers" or not est_gestionnaire_menu(request.user,menu):
            debug("tentative de piratage modifie_fichier")
            return redirect('/home')
        if request.method=="POST":
                if 'description' in request.POST:
                    form=FichierForm(request.POST,instance=obj)
                    if form.is_valid():
                        form.save()
                        obj.date_parution=request.POST["date_parution"]
                        try:
                            obj.save()
                        except:
                            obj.date_parution=datetime.datetime.now()
                            obj.save()
                if 'fichier-clear' in request.POST:
                    obj.fichier.delete()
                elif 'fichier' in request.FILES:
                    form=FichierForm({'description':obj.description},request.FILES,instance=obj)
                    if obj.fichier!=None:
                        obj.fichier.delete()
                    if form.is_valid():
                        new_record=form.save(commit=False)
                        new_record.nomfichier=request.FILES['fichier']
                        new_record.save()  
                return redirect('/menu/'+str(menu.id))
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['nom_fichier']=obj.nomfichier
        formdescription=FichierFormDescription(instance=obj)
        formfichier=FichierFormFichier(instance=obj)
        context['formdescription']=formdescription
        context['formfichier']=formfichier
        context["date_parution"]=str(obj.date_parution)
        return render(request,'gestionmenu/modifie_fichier.html',context)
    except:
        debug("erreur modifie_fichier")
        return redirect('/home')

# le fichier apparaissant en premier est celui d'ordre le plus élevé
# afin d'afficher en premier les derniers fichiers ajoutés.
@auth(None)
def modifie_ordre_fichier(request,pk,up="True"):
    try:
        obj=Fichier.objects.get(id=pk)
        menu=obj.menu
        if menu.fonction!="liste_fichiers" or not est_gestionnaire_menu(request.user,menu):
            debug("tentative de piratage ordre_fichier")
            return redirect('/home')
        liste=Fichier.objects.filter(menu=menu).order_by('-ordre')
        i=0
        while i<len(liste) and liste[i].id!=int(pk):
           i+=1  
        if i>0 and up=="True":
            echange(liste,liste[i].ordre,liste[i-1].ordre) 
        if i<len(liste)-1 and up=="False": 
            echange(liste,liste[i].ordre,liste[i+1].ordre) 
        return redirect('/menu/'+str(menu.id))
    except:
        debug("erreur ordre_fichier")
        return redirect('/home')

@auth(None)
def ajout_menu(request,pk):
    try:
        menu=Menu.objects.get(id=pk)
        if not est_gestionnaire_menu(request.user,menu):
            debug("tentative de piratage ajout_menu")
            return redirect('/home')
        form=MenuForm()
        if request.method=="POST":
            form=MenuForm(request.POST)
            if form.is_valid:
                new_menu=form.save(commit=False)
                new_menu.parent=pk
                request.POST['type_de_menu']
                if request.POST['type_de_menu']=="l":
                    new_menu.fonction="liste_fichiers"
                else:
                    new_menu.fonction="fichier_unique"
                try:
                    res=Menu.objects.filter(parent=pk).aggregate(Max('ordre'))
                    new_menu.ordre=res['ordre__max']+1
                except :
                    new_menu.ordre=1
                new_menu.save()
                for ungroupe in menu.groupes.all():
                    new_menu.groupes.add(ungroupe)
                for user in menu.gestionnaires.all():
                    new_menu.gestionnaires.add(user)
                context={"menu":menu_navigation(request)}
                return gestion_menu(request,0,context)
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['form']=form
        context['idmenu']=menu.nom
        return render(request,'gestionmenu/ajout_menu.html',context)
    except:
        debug("erreur ajout_menu")
        return redirect('/home')

@auth(None)
def supprime_menu(request,pk):
    try:
        menu=Menu.objects.get(id=pk)
        parent=Menu.objects.get(id=menu.parent)
        if not est_gestionnaire_menu(request.user,parent):
            debug("tentative de piratage supprime_menu")
            return redirect('/home')
        if request.method=="POST" and "validation" in request.POST:
            if menu.fonction=="liste_fichiers" or menu.fonction=="fichier_unique":
                menu.delete()
                context={"menu":menu_navigation(request)}
            else:
                context={"menu":menu_navigation(request)}
                context["msg"]="impossible de supprimer ce menu"
            return gestion_menu(request,0,context)
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['obj']="le sous-menu '"+str(menu.nom)+"' de "+str(parent.nom)
        return render(request,'gestionmenu/delete.html',context)
    except:
        debug("erreur supprime_menu")
        return redirect('/home')
    
@auth(None)
def modifie_menu(request,pk):
    try:
        menu=Menu.objects.get(id=pk)
        parent=Menu.objects.get(id=menu.parent)
        if not est_gestionnaire_menu(request.user,parent):
            debug("tentative de piratage modifie_menu")
            return redirect('/home')
        if request.method=="POST":
            form=MenuFormSimple(request.POST,instance=menu)
            if form.is_valid():
                form.save()
                context={"menu":menu_navigation(request)}
                return gestion_menu(request,0,context)               
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        context['idmenu']=parent.nom
        form=MenuFormSimple(instance=menu)
        context['form']=form
        return render(request,'gestionmenu/ajout_menu.html',context)
    except:
        debug("erreur modifie_menu")
        return redirect('/home')

@auth(None)
def modifie_ordre_menu(request,pk,up="True"):
    try:
        menu=Menu.objects.get(id=pk)
        parent=Menu.objects.get(id=menu.parent)
        if not est_gestionnaire_menu(request.user,parent):
            debug("tentative de piratage modifie_ordre_menu")
            return redirect('/home')
        listemenus=Menu.objects.filter(parent=menu.parent).order_by('ordre')
        i=0
        while i<len(listemenus) and listemenus[i].id!=int(pk):
           i+=1  
        if i>0 and up=="True":
            echange(listemenus,listemenus[i].ordre,listemenus[i-1].ordre) 
        if i<len(listemenus)-1 and up=="False": 
            echange(listemenus,listemenus[i].ordre,listemenus[i+1].ordre) 
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        return gestion_menu(request,0,context)
    except:
        debug("erreur modifie_ordre_menu")
        return redirect('/home')

@auth(None)
def modifie_fichier_unique(request,pk):
    try:
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        menu=Menu.objects.get(id=pk)
        if not (est_gestionnaire_menu(request.user,menu) and menu.fonction=="fichier_unique"):
            debug("tentative de piratage modifie_fichier_unique")
            return redirect('/home')
        if request.method=="POST":
            if 'fichier-clear' in request.POST:
                Fichier.objects.filter(menu=menu).delete()                
                return gestion_menu(request,0,context)
            elif 'fichier' in request.FILES:
                Fichier.objects.filter(menu=menu).delete()
                obj=Fichier.objects.create(description="",ordre=0,menu=menu)
                form=FichierForm({'description':""},request.FILES,instance=obj)
                if form.is_valid():
                    new_record=form.save(commit=False)
                    new_record.nomfichier=request.FILES['fichier']
                    new_record.save()
            return gestion_menu(request,0,context)            
        else:
            try:
                obj=Fichier.objects.get(menu=menu)              
                form=FichierUniqueForm(instance=obj)
            except:
                form=FichierUniqueForm()
            context['form']=form
            context['nommenu']=menu.nom
            return render(request,'gestionmenu/modifie_fichier_unique.html',context)
    except:
        debug("erreur modifie_fichier_unique")
        return redirect('/home')

@auth(None)
def download(request,letype,pk,id_menu=0):
    # lien vers la version dans fonction afin de pouvoir l'utiliser dans d'autres menus
    return download_file(request,letype,pk,id_menu)

@auth(None)
def download_pronote(request):
    if est_gestionnaire_colle(request.user):
            document = open('private_files/colles_'+request.user.username+'.csv','rb')
            response = HttpResponse(FileWrapper(document),content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="colles_'+request.user.username+'.csv"'
            return response
    debug("tentative de piratage download_pronote")
    return redirect('/home')

@auth(None)
def recupere_eleves(request):
    # liste des élèves d'une année
    # pour la lecture des fiches renseignements
    if not est_prof(request.user):
        debug("tentative de piratage recupere_eleves")
        return redirect('/home')
    try:
        r=Renseignements.objects.filter(année=request.POST["annee"])
        response_data = {"eleves":[str(x.login) for x in r]}
    except:
        debug("erreur recupere_eleves")
        response_data = {"eleves":[]}
    return HttpResponse(json.dumps(response_data), content_type="application/json")

@auth(None)
def ajout_prog_colle(request,id_menu):
    if est_gestionnaire_menu(request.user,Menu.objects.get(id=id_menu)):
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        form=ProgColleForm()
        context['form']=form
        if request.method=="POST":
            obj=ProgColle.objects.create(description="bidon",numero=0,menu=Menu.objects.get(id=id_menu))
            form=ProgColleForm(request.POST,request.FILES,instance=obj)
            if form.is_valid():
                new_prog=form.save(commit=False)
                if 'programme' in request.FILES:
                    new_prog.nomprogramme=request.FILES['programme']
                if 'exercices' in request.FILES:
                    new_prog.nomexercices=request.FILES['exercices']
                new_prog.save()
                return redirect('/menu/'+str(id_menu))
        return render(request,'gestionmenu/ajout_prog_colle.html',context)
    debug("tentative de piratage")
    return redirect('/home')

@auth(None)
def supprime_prog_colle(request,id_menu,pk):
    if est_gestionnaire_menu(request.user,Menu.objects.get(id=id_menu)):
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        if request.method=="POST":
            obj=ProgColle.objects.get(id=pk)
            obj.delete()
            return redirect('/menu/'+str(id_menu))
        context['obj']="programme de colle n° "+str(pk)
        return render(request,'gestionmenu/delete.html',context)
    debug("tentative de piratage")
    return redirect('/home')

@auth(None)
def modifie_prog_colle(request,id_menu,pk):
    if est_gestionnaire_menu(request.user,Menu.objects.get(id=id_menu)):
        context={"menu":menu_navigation(request)}
        context["titresite"]=TITRE_SITE
        obj=ProgColle.objects.get(id=pk)
        if request.method=="POST":
            if 'description' in request.POST:
                form=ProgColleForm(request.POST,instance=obj)
                if form.is_valid():
                    form.save()
            elif 'programme-clear' in request.POST and obj.programme!=None:
                obj.programme.delete()
            elif 'programme' in request.FILES:
                if obj.programme!=None:
                    obj.programme.delete()
                form=ProgColleForm({'description':obj.description,'numero':obj.numero},request.FILES,instance=obj)
                if form.is_valid():
                    new_record=form.save(commit=False)
                    new_record.nomprogramme=request.FILES['programme']
                    new_record.save()
            elif 'exercices-clear' in request.POST and obj.exercices!=None:
                obj.exercices.delete()                    
            elif 'exercices' in request.FILES:
                if obj.exercices!=None:
                    obj.exercices.delete()
                form=ProgColleForm({'description':obj.description,'numero':obj.numero},request.FILES,instance=obj)
                if form.is_valid():
                    new_record=form.save(commit=False)
                    new_record.nomexercices=request.FILES['exercices']
                    new_record.save()
            return redirect('/menu/'+str(id_menu))
        context['id']=obj.id
        formdescription=ProgColleFormDescription(instance=obj)
        formprogramme=ProgColleFormProgramme(instance=obj)
        formexercices=ProgColleFormExercices(instance=obj)
        context['formprogdescription']=formdescription
        context['formprogprogramme']=formprogramme
        context['formprogexercices']=formexercices
        return render(request,'gestionmenu/modifie_prog.html',context)
    debug("tentative de piratage")
    return redirect('/home')

@auth(None)
def recuperation_notes_colles(request):
    response_data = {}
    try:
        if request.method=="POST" and "semaine" in request.POST and "colleur" in request.POST:
            semaine=Semaines.objects.get(numero=int(request.POST["semaine"]))
            if request.POST["colleur"]=="__all__":
                # un gestionnaire récupère toutes les colles
                # de la semaine
                if est_gestionnaire_colle(request.user):
                    lescolleurs=[x.colleur for x in InfoColleurs.objects.filter(prof=request.user)]
                    tousleseleves=User.objects.filter(groups=groupe_eleves).order_by('username')
                    lesnotes={ joli_nom(item) : '' for item in tousleseleves}
                    notes=NotesColles.objects.filter(semaine=semaine,colleur__in=lescolleurs)
                    doublons={}
                    for x in notes:
                        try:
                            lecom=CommentaireColle.objects.get(notecolle=x)
                            lecom_id=lecom.id
                        except:
                            lecom_id=None
                        if lesnotes[joli_nom(x.eleve)]=='':
                            lesnotes[joli_nom(x.eleve)]={"colleur":joli_nom(x.colleur),"note":x.note,"lecom_id":lecom_id}
                        else:
                            if joli_nom(x.eleve) not in doublons: doublons[joli_nom(x.eleve)]=[]
                            doublons[joli_nom(x.eleve)].append({"colleur":joli_nom(x.colleur),"note":x.note,"lecom_id":lecom_id})
                    response_data["lesnotes"]=lesnotes
                    response_data["doublons"]=doublons
                else:
                    debug("tentative de piratage recuperation_notes_colles")
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                # on récupère les notes d'un colleur
                colleur_name=request.POST["colleur"] 
                if colleur_name=="" and est_colleur(request.user):
                    # un colleur demande ses notes
                    colleur=request.user
                else:
                    # on vérifie que c'est un bien un gestionnaire qui demande les notes
                    # d'un de ses colleurs
                    colleur=User.objects.get(username=colleur_name)
                    if not est_gestionnaire_colle(request.user,colleur):
                        debug("tentative de piratage recuperation_notes_colles")
                        return HttpResponse(json.dumps(response_data), content_type="application/json") 
                notes=NotesColles.objects.filter(semaine=semaine,colleur=colleur)
                idnotes=[]
                creneaux=CreneauxColleurs.objects.filter(colleur=colleur)
                notessemaine=[]
                lecolloscope=Colloscope.objects.filter(semaine=semaine,creneau__in=creneaux)
                for item in lecolloscope:
                        liste=[]
                        for eleve in item.groupe.eleves.all().order_by("username"):
                            try:
                                lanote=notes.get(eleve=User.objects.get(username=eleve.username),creneau=item.creneau)
                                try:
                                    lecom=CommentaireColle.objects.get(notecolle=lanote)
                                    lecom_present=True
                                    lecom_id=lecom.id
                                except:
                                    lecom_present=False
                                    lecom_id=None
                                liste.append({"lecom_present":lecom_present,"lecom_id":lecom_id,"idnote" : lanote.id,"user":eleve.username,"eleve": joli_nom(eleve),"note":lanote.note,"creneau":item.creneau.id})
                                idnotes.append(lanote.id)
                            except:
                                liste.append({"user":eleve.username,"eleve":joli_nom(eleve),"note":'',"creneau":item.creneau.id})
                        notessemaine.append((item.groupe.numero,liste))
                indiv=Colloscope_individuel.objects.filter(semaine=semaine,creneau__in=creneaux)
                notesindiv=[]
                for item in indiv:
                    if item.eleve!=None:
                        try:
                            lanote=notes.get(eleve=User.objects.get(username=item.eleve.username),creneau=item.creneau)
                            try:
                                    lecom=CommentaireColle.objects.get(notecolle=lanote)
                                    lecom_present=True
                                    lecom_id=lecom.id
                            except:
                                    lecom_present=False
                                    lecom_id=None
                            notesindiv.append({"lecom_present":lecom_present,"lecom_id":lecom_id,"idnote" : lanote.id,"user":item.eleve.username,"eleve": joli_nom(item.eleve),"note":lanote.note,"creneau":item.creneau.id})
                            idnotes.append(lanote.id)
                        except:
                            notesindiv.append({"user":item.eleve.username,"eleve": joli_nom(item.eleve),"note":'',"creneau":item.creneau.id})
                autresnotes=[]
                lesnotes=notes.exclude(id__in=idnotes)
                for item in lesnotes:
                    try:
                        lecom=CommentaireColle.objects.get(notecolle=item)
                        lecom_present=True
                        lecom_id=lecom.id
                    except:
                        lecom_present=False
                        lecom_id=None                   
                    autresnotes.append({"lecom_present":lecom_present,"lecom_id":lecom_id,"user":item.eleve.username,"eleve":joli_nom(item.eleve),"note":item.note,"idnote" : item.id})
                leseleves=User.objects.filter(groups=groupe_eleves).order_by("username")
                response_data["notessemaine"]=notessemaine
                response_data["notesindiv"]=notesindiv
                response_data["autresnotes"]=autresnotes
                response_data["leseleves"]=[{"user" : item.username, "eleve":joli_nom(item)} for item in leseleves]
    except:
        debug("erreur recuperation_notes_colles")
    return HttpResponse(json.dumps(response_data), content_type="application/json")    

@auth(None)
def maj_notes_colles(request):
    response_data = {"resultat" : "erreur"}
    try:
        colleur_name=request.POST["colleur"]
        if colleur_name=="" and est_colleur(request.user):
            # un colleur modifie une de ses notes
            colleur=request.user
        else:
            # un gestionnaire modifie une note
            colleur=User.objects.get(username=colleur_name)
            if not est_gestionnaire_colle(request.user,colleur):
                debug("tentative de piratage maj_notes_colles")
                return HttpResponse(json.dumps(response_data), content_type="application/json")  
        eleve=User.objects.get(username=request.POST["eleve"])
        semaine=Semaines.objects.get(numero=request.POST["semaine"])
        note=request.POST["note"]
        letype=request.POST["type"]
        info=request.POST["info"]
        if letype=='colloscope':
            try:
            # la note existe déjà
                notecolle=NotesColles.objects.get(colleur=colleur,eleve=eleve,semaine=semaine,creneau__id=info)
                if note=="":
                    notecolle.delete()
                else:
                    notecolle.note=note
                    notecolle.save()
            except:
            # la note n'existe pas
                if note!="": 
                    notecolle=NotesColles(colleur=colleur,eleve=eleve,semaine=semaine,note=note,creneau=CreneauxColleurs.objects.get(id=info))
                    notecolle.save()
                else:
                # else impossible normalement
                    debug("impossible normalement ?: note de colloscope vide et absente, on ne fait rien")
        elif letype=='horscolloscope':
            try:
                notecolle=NotesColles.objects.get(id=info)
                if note=="":
                    notecolle.delete()
                else:
                    notecolle.note=note
                    notecolle.save()
            except:
                debug("note hors colloscope absente : effacé sur un autre navigateur?")
        elif letype=="ajout":
            notecolle=NotesColles(colleur=colleur,eleve=eleve,semaine=semaine,note=note)
            notecolle.save()
        else:
            debug("erreur dans maj_notes_colles")
    except:
        debug("erreur dans maj_notes_colles")
    return HttpResponse(json.dumps(response_data), content_type="application/json")    

@auth(None)
def recuperation_colloscope_semaine(request):
    response_data = {}
    try:
        if est_prof(request.user) or est_colleur(request.user) or est_eleve(request.user) or est_generic(request.user):
            dico_semaine={"lundi" : [], "mardi" : [], "mercredi" : [], "jeudi" : [], "vendredi" : [], "samedi" : []}
            autre_jour=[]
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])  
            lescolles=Colloscope.objects.filter(semaine=lasemaine)
            for unecolle in lescolles:
                cr=unecolle.creneau
                autorise_modif=est_gestionnaire_colle(request.user,cr.colleur) or (est_colleur(request.user) and request.user==cr.colleur)
                if cr.jour in dico_semaine:
                    dico_semaine[cr.jour].append(["Groupe "+str(unecolle.groupe.numero),cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,unecolle.id,autorise_modif])
                else:
                    autre_jour.append(["Groupe "+str(unecolle.groupe.numero),cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,cr.jour,unecolle.id,autorise_modif])
            dico_semaine["autre_jour"]=autre_jour
            lesindividuelles=Colloscope_individuel.objects.filter(semaine=lasemaine)
            for unecolle in lesindividuelles:
                cr=unecolle.creneau
                autorise_modif=est_gestionnaire_colle(request.user,cr.colleur) or (est_colleur(request.user) and request.user==cr.colleur)
                if cr.jour in dico_semaine:
                    if unecolle.eleve!=None:
                        dico_semaine[cr.jour].append([unecolle.eleve.first_name+" "+unecolle.eleve.last_name,cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,unecolle.id,autorise_modif])
                    else:
                        dico_semaine[cr.jour].append(["non attribué",cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,unecolle.id,autorise_modif])
                else:
                    if unecolle.eleve!=None:
                        dico_semaine["autre_jour"].append([unecolle.eleve.first_name+" "+unecolle.eleve.last_name,cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,cr.jour,unecolle.id,autorise_modif])
                    else:
                        dico_semaine["autre_jour"].append(["non attribué",cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,cr.jour,unecolle.id,autorise_modif])
            for key in dico_semaine:
                dico_semaine[key].sort(key=lambda x:x[1]) 
            response_data["informations"]=dico_semaine
        else:
            debug("tentative de piratage recuperation_colloscope_semaine")
    except:
        debug("erreur dans recuperation_colloscope_semaine")
    return HttpResponse(json.dumps(response_data), content_type="application/json")   

def maj_response_data_creneaux_colles(response_data,user):
    tmp=InfoColleurs.objects.filter(prof=user).values_list("colleur")
    lescreneaux=CreneauxColleurs.objects.filter(colleur__in=tmp)
    liste=[]
    for item in lescreneaux:
        liste.append({"id" : item.id , "text" : item.colleur.first_name+" "+item.colleur.last_name+", "+item.jour+" à "+item.horaire+" en "+item.salle})
    response_data["creneaux"]=liste
    lessemaines=Semaines.objects.all()
    dico_semaine={ item.numero : {"lundi" : [], "mardi" : [], "mercredi" : [], "jeudi" : [], "vendredi" : [], "samedi" : [],"autre_jour" : []} for item in lessemaines}
    lescolles=Colloscope.objects.all()
    for unecolle in lescolles:
        cr=unecolle.creneau
        if cr.jour in dico_semaine[unecolle.semaine.numero]:
            dico_semaine[unecolle.semaine.numero][cr.jour].append(["Groupe "+str(unecolle.groupe.numero),cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,unecolle.id,'groupe'])
        else:
            dico_semaine[unecolle.semaine.numero]["autre_jour"].append(["Groupe "+str(unecolle.groupe.numero),cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,cr.jour,unecolle.id,'groupe'])
    lesindividuelles=Colloscope_individuel.objects.all()
    for unecolle in lesindividuelles:
        cr=unecolle.creneau
        if cr.jour in dico_semaine[unecolle.semaine.numero]:
            if unecolle.eleve!=None:
                dico_semaine[unecolle.semaine.numero][cr.jour].append([unecolle.eleve.first_name+" "+unecolle.eleve.last_name,cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,unecolle.id,'eleve'])
            else:
                dico_semaine[unecolle.semaine.numero][cr.jour].append(["non attribué",cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,unecolle.id,'eleve'])
        else:
            if unecolle.eleve!=None:
                dico_semaine[unecolle.semaine.numero]["autre_jour"].append([unecolle.eleve.first_name+" "+unecolle.eleve.last_name,cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,cr.jour,unecolle.id,'eleve'])
            else:
                dico_semaine[unecolle.semaine.numero]["autre_jour"].append(["non attribué",cr.colleur.first_name+" "+cr.colleur.last_name,cr.horaire,cr.salle,cr.matière,cr.jour,unecolle.id,'eleve'])
    for key in dico_semaine:
        for subkey in dico_semaine[key]:
            dico_semaine[key][subkey].sort(key=lambda x:x[1])
    response_data["semaines"]=dico_semaine

@auth(None)
def recuperation_creneaux(request):
    response_data = {}
    try:
        if est_gestionnaire_colle(request.user):
            maj_response_data_creneaux_colles(response_data,request.user)
        else:
            debug("tentative de piratage recuperation_creneaux")
    except:
        debug("erreur dans recuperation_creneaux")
    return HttpResponse(json.dumps(response_data), content_type="application/json")   

@auth(None)
def creation_creneaux_groupe(request):
    response_data = {}
    try:
        if est_gestionnaire_colle(request.user):
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])
            lecreneau=CreneauxColleurs(id=request.POST["creneau"])
            legroupe=GroupeColles.objects.get(numero=request.POST["groupe"])
            try:
                Colloscope.objects.get(semaine=lasemaine,creneau=lecreneau)
                response_data["msg"]="créneau déjà occupé par un groupe"
            except:
                Colloscope(semaine=lasemaine,groupe=legroupe,creneau=lecreneau).save()
                response_data["msg"]="créneau créé pour le groupe "+str(legroupe.numero)
            maj_response_data_creneaux_colles(response_data,request.user)
        else:
            debug("tentative de piratage creation_creneaux_groupe")
    except:
        debug("erreur dans creation_creneaux_groupe")
    return HttpResponse(json.dumps(response_data), content_type="application/json")   

@auth(None)
def suppression_creneaux_groupe(request):
    response_data = {}
    try:
        if est_gestionnaire_colle(request.user):
            try:
                if request.POST['type']=='groupe':
                    Colloscope.objects.get(id=request.POST["colle"]).delete()
                    response_data["msg"]="créneau groupe supprimé correctement"
                elif request.POST['type']=='eleve':
                    Colloscope_individuel.objects.get(id=request.POST["colle"]).delete()
                    response_data["msg"]="créneau élève supprimé correctement"
                else:
                    print(1/0)  # pas normal d'arriver là
            except:
                response_data["msg"]="créneau sélectionné inexistant "
            maj_response_data_creneaux_colles(response_data,request.user)
        else:
            debug("tentative de piratage suppression_creneaux_groupe")
    except:
        debug("erreur dans suppression_creneaux_groupe")
    return HttpResponse(json.dumps(response_data), content_type="application/json")   

@auth(None)
def creation_creneaux_eleve(request):
    response_data = {}
    try:
        if est_gestionnaire_colle(request.user):
            lasemaine=Semaines.objects.get(numero=request.POST["semaine"])
            lecreneau=CreneauxColleurs(id=request.POST["creneau"])
            leleve=User.objects.get(id=request.POST["eleve"])
            try:
                Colloscope_individuel.objects.get(semaine=lasemaine,creneau=lecreneau)
                response_data["msg"]="créneau déjà occupé par un élève"
            except:
                Colloscope_individuel(semaine=lasemaine,eleve=leleve,creneau=lecreneau).save()
                response_data["msg"]="créneau créé pour l'élève "+leleve.first_name+" "+leleve.last_name
            maj_response_data_creneaux_colles(response_data,request.user)
        else:
            debug("tentative de piratage creation_creneaux_eleve")
    except:
        debug("erreur dans creation_creneaux_eleve")
    return HttpResponse(json.dumps(response_data), content_type="application/json")  

@auth(None)
def recuperation_creneaux_individuels(request):
    response_data = {}
    try:
        if est_eleve(request.user):
            lamatiere=Gestion_colles_individuelles.objects.get(matiere=request.POST["matiere"])
            lessemaines=Semaines.objects.all()
            lescreneaux=CreneauxColleurs.objects.filter(matière=lamatiere.matiere)
            lescolles=Colloscope_individuel.objects.filter(creneau__in=lescreneaux)
            dico_semaine={ item.numero : {"date" : date_fr(item.date,True),"lundi" : [], "mardi" : [], "mercredi" : [], "jeudi" : [], "vendredi" : [], "samedi" : [],"autre_jour" : []} for item in lessemaines}
            for unecolle in lescolles:
                lejour=unecolle.creneau.jour
                if lejour not in ["lundi","mardi","mercredi","jeudi","vendredi","samedi"]:
                    lejour="autre_jour"
                if unecolle.eleve!=None:
                    leleve=unecolle.eleve.first_name+" "+unecolle.eleve.last_name
                    if unecolle.eleve==request.user:
                        etat="se désinscrire"
                    else:
                        if unecolle.optionnel:
                            etat="remplacer"
                        else:
                            etat="occupé"
                else:
                    etat="s'inscrire"
                    leleve="non attribué"
                dico_semaine[unecolle.semaine.numero][lejour].append((lejour+" à "+unecolle.creneau.horaire+" en "+unecolle.creneau.salle+" avec "+unecolle.creneau.colleur.first_name
                                                                      +" "+unecolle.creneau.colleur.last_name+" : "+leleve,etat,unecolle.id))
            response_data["creneaux"]=dico_semaine
            response_data["creneaux_occupes"]=len(Colloscope_individuel.objects.filter(creneau__in=lescreneaux,eleve=request.user))
        else:
            debug("tentative de piratage recuperation_creneaux_individuels")
    except:
        debug("erreur dans recuperation_creneaux_individuels")
    return HttpResponse(json.dumps(response_data), content_type="application/json")  

@auth(None)
def action_creneaux_individuels(request):
    response_data = {}
    try:
        if est_eleve(request.user):
            lamatiere=Gestion_colles_individuelles.objects.get(matiere=request.POST["matiere"])
            id=request.POST['id']
            etat=request.POST["etat"]
            lecreneau=Colloscope_individuel.objects.get(id=id)
            if etat=="s'inscrire":
                if lecreneau.eleve==None:
                    lescreneaux=CreneauxColleurs.objects.filter(matière=lamatiere.matiere)
                    lescolles=Colloscope_individuel.objects.filter(creneau__in=lescreneaux,eleve=request.user)
                    if len(lescolles)<lamatiere.max_par_eleve:
                        if len(lescolles)<lamatiere.max_garanti:
                            lecreneau.optionnel=False
                        else:
                            lecreneau.optionnel=True
                        lecreneau.eleve=request.user
                        lecreneau.save()
                    else:
                        msg="il faut d'abord se désinscrire d'un créneau"
                else:
                    msg="le créneau n'est plus libre"
            elif etat=="se désinscrire":
                if lecreneau.eleve==request.user:
                    lecreneau.eleve=None
                    lecreneau.save() 
                    lescreneaux=CreneauxColleurs.objects.filter(matière=lamatiere.matiere)
                    lescolles=Colloscope_individuel.objects.filter(creneau__in=lescreneaux,eleve=request.user)
                    garanti=len(lescolles.filter(optionnel=False))
                    nongaranti=lescolles.filter(optionnel=True)
                    if garanti<lamatiere.max_garanti:
                        a_changer=min(len(nongaranti),lamatiere.max_par_eleve-lamatiere.max_garanti)
                        for item in nongaranti:
                            if a_changer>0:
                                a_changer-=1
                                item.optionnel=False
                                item.save()
            elif etat=="remplacer":
                lescreneaux=CreneauxColleurs.objects.filter(matière=lamatiere.matiere)
                lescolles=Colloscope_individuel.objects.filter(creneau__in=lescreneaux,eleve=request.user)
                if len(lescolles)<lamatiere.max_garanti:
                    lecreneau.eleve=request.user
                    lecreneau.optionnel=False
                    lecreneau.save()
            else:
                msg="etat impossible"          
        else:
            debug("tentative de piratage action_creneaux_individuels")
    except:
        debug("erreur dans action_creneaux_individuels")
    return HttpResponse(json.dumps(response_data), content_type="application/json")      


@auth(None)
def recuperation_creneaux_individuels_gestionnaire(request):
    response_data = {}
    try: 
        lamatiere=Gestion_colles_individuelles.objects.get(matiere=request.POST["matiere"])
        if request.user in lamatiere.responsables.all():
            lessemaines=Semaines.objects.all()
            lescreneaux=CreneauxColleurs.objects.filter(matière=lamatiere.matiere)
            lescolles=Colloscope_individuel.objects.filter(creneau__in=lescreneaux)
            dico_semaine={ item.numero : {"date" : date_fr(item.date,True),"lundi" : [], "mardi" : [], "mercredi" : [], "jeudi" : [], "vendredi" : [], "samedi" : [],"autre_jour" : []} for item in lessemaines}
            for unecolle in lescolles:
                lejour=unecolle.creneau.jour
                if lejour not in ["lundi","mardi","mercredi","jeudi","vendredi","samedi"]:
                    lejour="autre_jour"
                if unecolle.eleve!=None:
                    leleve=unecolle.eleve.first_name+" "+unecolle.eleve.last_name
                    username=unecolle.eleve.username
                else:
                    leleve="non attribué"
                    username=""
                dico_semaine[unecolle.semaine.numero][lejour].append((lejour+" à "+unecolle.creneau.horaire+" en "+unecolle.creneau.salle+" avec "+unecolle.creneau.colleur.first_name
                                                                      +" "+unecolle.creneau.colleur.last_name+" : "+leleve,unecolle.id,username))
            response_data["creneaux"]=dico_semaine
        else:
            debug("tentative de piratage recuperation_creneaux_individuels_gestionnaire")
    except:
        debug("erreur dans recuperation_creneaux_individuels_gestionnaire")
    return HttpResponse(json.dumps(response_data), content_type="application/json")  

@auth(None)
def action_creneaux_individuels_gestionnaire(request):
    response_data = {}
    try:
        lamatiere=Gestion_colles_individuelles.objects.get(matiere=request.POST["matiere"])
        if request.user in lamatiere.responsables.all():
            id=request.POST['id']
            eleve=request.POST["eleve"]
            lecreneau=Colloscope_individuel.objects.get(id=id)
            if eleve=="":
                lecreneau.eleve=None
            else:
                lecreneau.eleve=User.objects.get(username=eleve)
            lecreneau.save()
        else:
            debug("tentative de piratage action_creneaux_individuels")
    except:
        debug("erreur dans action_creneaux_individuels")
    return HttpResponse(json.dumps(response_data), content_type="application/json")      

@auth(None)
def maj_commentaire_notes_colles(request):
    response_data = {}
    try:
        lanote=NotesColles.objects.get(id=request.POST["id_colle"])
        if lanote.colleur==request.user: # à modifier avec les gestionnaires? sans doute non
            texte=request.POST['texte']
            try:
                lecom=CommentaireColle.objects.get(notecolle=lanote)
                if texte!="":
                    lecom.text=texte
                    lecom.save()
                else:
                    lecom.delete()
            except:
                if texte!="":
                    lecom=CommentaireColle(notecolle=lanote,text=texte)
                    lecom.save()
        else:
            debug("tentative de piratage maj_commentaire_notes_colles")
    except:
        debug("erreur dans maj_commentaire_notes_colles")
    return HttpResponse(json.dumps(response_data), content_type="application/json")      

@auth(None)
def recupere_commentaire_notes_colles(request):
    response_data = {}
    try:
        lecom=CommentaireColle.objects.get(id=request.POST["id_com"])
        if lecom.notecolle.colleur==request.user or est_gestionnaire_colle(request.user,lecom.notecolle.colleur): 
            response_data["texte"]=lecom.text
        else:
            debug("tentative de piratage recupere_commentaire_notes_colles")
    except:
        response_data["texte"]=""
        debug("erreur dans recupere_commentaire_notes_colles ou bien commentaire vide")
    return HttpResponse(json.dumps(response_data), content_type="application/json") 

@auth(None)
def modifie_creneau(request):
    response_data = {}
    try:
        lacolle=Colloscope.objects.get(id=request.POST["id"])
        oldcreneau=lacolle.creneau
        autorise_modif=est_gestionnaire_colle(request.user,oldcreneau.colleur) or (est_colleur(request.user) and request.user==oldcreneau.colleur)
        if autorise_modif:
            try:
                newcreneau=CreneauxColleurs.objects.get(colleur=oldcreneau.colleur,jour=request.POST["jour"],horaire=request.POST["horaire"],
                                            salle=request.POST["salle"],matière=oldcreneau.matière)
            except:
                newcreneau=CreneauxColleurs.objects.create(colleur=oldcreneau.colleur,jour=request.POST["jour"],horaire=request.POST["horaire"],
                                            salle=request.POST["salle"],matière=oldcreneau.matière,numero=0)
                newcreneau.save()
            lacolle.creneau=newcreneau
            lacolle.save()
        else:
            debug("tentative de piratage modifie_creneau")
    except:
        debug("erreur dans modifie_creneau")
    return HttpResponse(json.dumps(response_data), content_type="application/json") 

@auth(None)
def recuperation_notes_colles_semaine(request):
    response_data = {}
    try:
        lesnotes=NotesColles.objects.filter(eleve=request.user).order_by("-semaine")
        contenu=[]
        for item in lesnotes:
            d={"id":item.id,"semaine":item.semaine.numero,"note":item.note,"colleur":joli_nom(item.colleur)}
            if item.colleur.username in ["rouillier","lenoir"]:
                try:
                    com=CommentaireColle.objects.get(notecolle=item)
                    d["commentaire"]=com.text
                except:
                    pass
            contenu.append(d)
        response_data["notes_semaine"]=contenu
    except:
        debug("erreur dans recuperation_notes_colles_semaine")
    return HttpResponse(json.dumps(response_data), content_type="application/json") 

@auth(None)
def creation_sondage(request):
    response_data = {}
    try:
        if not est_prof(request.user):
            debug("tentative de piratage creation_sondage")
            return
        action=request.POST['action']
        if action=="demande":
            lessondages=Sondages.objects.filter(createur=request.user).order_by("-date")
            liste=[]
            for unsondage in lessondages:
                liste.append({"titre": unsondage.titre, "date" : date_fr(unsondage.date,True), "type_sondage" : unsondage.type_sondage,
                "actif" : unsondage.actif,"visible":unsondage.visible,"id":unsondage.id})
                pass
            response_data["les_sondages"]=liste
        elif action=="creation":
            titre=request.POST['titre']
            texte=request.POST['texte']
            type_sondage=request.POST['type_sondage']
            if type_sondage not in ["question","choix","priorise"]:
                debug("tentative de piratage creation_sondage")
                return
            newsondage=Sondages(titre=titre,description=texte,type_sondage=type_sondage,actif=True,visible=True,createur=request.user,date=datetime.datetime.now())
            newsondage.save()
            if type_sondage!="question":
                complement=int(request.POST['complement'])
                complement_tab=[request.POST['complement'+str(i)] for i in range(complement)]        
                for i,x in enumerate(complement_tab):
                    newitem=SondagesItem(sondage=newsondage,texte=x,numero=i)
                    newitem.save()
        elif action=="change":
            id=request.POST['id']
            lesondage=Sondages.objects.get(createur=request.user,id=id)
            if request.POST["etat"]=="supprime":
                lesondage.delete()
            elif request.POST["etat"]=="visible":
                if request.POST["valeur"]=="true":
                    lesondage.visible=False
                else:
                    lesondage.visible=True
                lesondage.save()
            elif request.POST["etat"]=="actif":
                if request.POST["valeur"]=="true":
                    lesondage.actif=False
                else:
                    lesondage.actif=True
                lesondage.save()
            else:
                debug("tentative de piratage creation_sondage")
                return
        else:
            debug("tentative de piratage creation_sondage")
            return
    except:
        debug("erreur dans creation_sondage")
    return HttpResponse(json.dumps(response_data), content_type="application/json")     

@auth(None)
def sondage(request):
    response_data = {}
    if True: #try:
        if not est_eleve(request.user):
            debug("tentative de piratage sondage")
            return
        action=request.POST['action']
        if action=="demande":
            lessondages=Sondages.objects.filter(visible=True)
            for lesondage in lessondages:
                d={}
                try:
                    reponse=SondagesReponse.objects.get(utilisateur=request.user,sondage=lesondage)
                    d["reponse"]=reponse.reponse
                except:
                    newreponse=SondagesReponse(utilisateur=request.user,sondage=lesondage,reponse="")
                    newreponse.save()
                    d["reponse"]=""
                d["titre"]=lesondage.titre
                d["description"]=lesondage.description
                d["type_sondage"]=lesondage.type_sondage
                d["actif"]=lesondage.actif
                d["id"]=lesondage.id
                if lesondage.type_sondage!="question":
                    l=[]
                    lesitems=SondagesItem.objects.filter(sondage=lesondage)
                    for x in lesitems:
                        l.append((x.numero,x.texte))
                    d["lesitems"]=l
                response_data[str(lesondage.id)]=d
        elif action=="changement":
            try:
                sondage=Sondages.objects.get(id=request.POST["id_sondage"])
                if sondage.actif and sondage.visible:
                    reponse=SondagesReponse.objects.get(utilisateur=request.user,sondage=sondage)
                    reponse.reponse=request.POST["reponse"]
                    reponse.save()
            except:
                debug("tentative de piratage sondage")
                return
        elif action=="demande_reponse":
            id=request.POST["id"]
            lesondage=Sondages.objects.get(id=id)
            response_data["titre"]=lesondage.titre
            try:
                lareponse=SondagesReponse.objects.get(utilisateur=request.user,sondage=lesondage)
                response_data["reponse"]=lareponse.reponse
            except:
                response_data["reponse"]=""
        else:
            debug("tentative de piratage sondage")
            return
    #except:
        debug("erreur dans sondage")
    return HttpResponse(json.dumps(response_data), content_type="application/json")   

@auth(None)
def resultat_sondage(request):
    response_data = {}
    try:
        if not est_prof(request.user):
            debug("tentative de piratage resultat_sondage")
            return
        if request.POST["action"]=="demande":
            lessondages=Sondages.objects.filter(actif=True)
            for lesondage in lessondages:
                d={"type_sondage" : lesondage.type_sondage,"titre" : lesondage.titre}
                if lesondage.type_sondage!="question":
                    l={}
                    lesitems=SondagesItem.objects.filter(sondage=lesondage)
                    for x in lesitems:
                        l[str(x.numero)]=[x.texte]
                    d["lesitems"]=l
                if lesondage.type_sondage=="choix":
                    lesreponses=SondagesReponse.objects.filter(sondage=lesondage)
                    choix_eleves=defaultdict(list)
                    nombre_eleves=defaultdict(int)
                    eleves_vu=set()
                    for unereponse in lesreponses:
                        choix_eleves[unereponse.reponse].append(unereponse.utilisateur.username)
                        eleves_vu.add(unereponse.utilisateur.username)
                    tousleseleves=User.objects.filter(groups=groupe_eleves).order_by('username')
                    for uneleve in tousleseleves:
                        if uneleve.username not in eleves_vu:
                            choix_eleves[""].append(uneleve.username)
                    for key in d["lesitems"]:
                        if key not in choix_eleves:
                            choix_eleves[key]=[]
                    for key in choix_eleves:
                        choix_eleves[key].sort()
                        nombre_eleves[key]=len(choix_eleves[key])
                    d['choix']=choix_eleves
                    d['nombre']=nombre_eleves
                elif lesondage.type_sondage=="question":
                    lesreponses=SondagesReponse.objects.filter(sondage=lesondage)
                    avecreponse={}
                    for unereponse in lesreponses:
                        if unereponse.reponse!="":
                            avecreponse[unereponse.utilisateur.username]=True
                    sansreponse=[]
                    tousleseleves=User.objects.filter(groups=groupe_eleves).order_by('username')
                    for uneleve in tousleseleves:
                        if uneleve.username not in avecreponse:
                            sansreponse.append(uneleve.username)
                    sansreponse.sort()
                    avecreponse=sorted(avecreponse.keys())
                    d["avecreponse"]=avecreponse
                    d["nb_avecreponse"]=len(avecreponse)
                    d["sansreponse"]=sansreponse
                    d["nb_sansreponse"]=len(sansreponse)
                response_data[lesondage.id]=d
        elif request.POST["action"]=="demande":
            pass
        else:
            debug("tentative de piratage resultat_sondage")
            return
    except:
        debug("erreur dans resultat_sondage")
    return HttpResponse(json.dumps(response_data), content_type="application/json")   