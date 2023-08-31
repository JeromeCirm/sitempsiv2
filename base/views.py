from django.shortcuts import render,redirect
from django.contrib.auth import logout,authenticate
from .fonctions import *

def connexion(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None: 
            # on vérifie si le compte a bien été activé
            try:
                utilisateur=Utilisateur.objects.get(user=user)
                if not utilisateur.en_attente_confirmation:
                    if utilisateur.doit_changer_mdp:
                        return redirect('/change_mdp')
                    else:
                        login(request,user)
                        return redirect('/home')
                #compte en attente si on arrive ici
            except:
                pass
    context={ "creation" : AUTORISE_CREATION, "recuperation" : AUTORISE_RECUPERATION}
    context["titresite"]=TITRE_SITE
    return render(request,'base/connexion.html',context)

def deconnexion(request):
    logout(request)
    return redirect('/')

def creation_compte(request):
    if not AUTORISE_CREATION: return redirect('/home')
    context={}
    if request.method=="POST":
        reussi,err=demande_creation_compte(request)
        if reussi:
            context["reussi"]=True
        else:
            context["echec"]=True
            context["err"]=err
            context["ancien"]=request.POST
    context["titresite"]=TITRE_SITE
    return render(request,'base/creation_compte.html',context)

def validation_compte(request,login=None,lehash=None):
    if not AUTORISE_CREATION: return redirect('/home')
    if login==None:
        context={ "msg" : "Le lien n'est pas valide"}
    else:
        context={ "msg" : verifie_lien_validation(login,lehash)}
    context["titresite"]=TITRE_SITE
    return render(request,'base/validation_compte.html',context)

def recuperation_password(request):
    if not AUTORISE_RECUPERATION: return redirect('/home')
    context={"titresite" : TITRE_SITE}
    if request.method=="POST":   
        context["msg"]=envoie_mail_recuperation_mot_de_passe(request)
    return render(request,'base/recuperation_password.html',context)

def demande_reinitialisation(request,login=None,lehash=None):
    if not AUTORISE_RECUPERATION: return redirect('/home')
    if request.method=='POST':
        context={**reinitialise_mot_de_passe(request)}
    elif login==None:
        context={ "msg" : "Le lien n'est pas valide"}
    else:
        context={ **verifie_lien_reinitialisation(login,lehash)}
    context["titresite"]=TITRE_SITE
    return render(request,'base/demande_reinitialisation.html',context)

def change_mdp(request):
    context={ "titresite" : TITRE_SITE}
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        passwordnew=request.POST.get('passwordnew')
        passwordconfirm=request.POST.get('passwordconfirm')
        user=authenticate(request,username=username,password=password)
        if user is not None: 
            # on vérifie si le compte a bien été activé
            try:
                utilisateur=Utilisateur.objects.get(user=user)
                if not utilisateur.en_attente_confirmation:
                    if utilisateur.doit_changer_mdp:
                        if passwordnew==passwordconfirm and passwordnew!=password:
                            user.set_password(passwordnew)
                            user.save()
                            utilisateur.doit_changer_mdp=False
                            utilisateur.save()
                            login(request,user)
                            context["reussi"]=True
                        else:
                            context["msg"]="données incorrectes"
                            return render(request,'base/change_mdp.html',context)
            except:
                pass
    return render(request,'base/change_mdp.html',context)

import gestionmenu.views as my_view

@auth(None)
def home(request):
    return   my_view.home(request) 