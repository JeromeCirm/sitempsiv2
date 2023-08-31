from django.core.mail import send_mail
from django.contrib.auth import login
from django.shortcuts import redirect
from .models import *
from .settings import *
import datetime
from string import digits,ascii_letters
from re import match
from random import choice

# préfixe pour une "view"
# n'autorise la view que si l'utilisateur est dans un des groupes de la liste
# redirige vers la page de connexion sinon
# renseigner None à la place de la liste des groupes pour imposer une authentification
#    sans imposer de groupe
def auth(group_list=[]):
    def teste(func):
        def nouvelle_func(request,*args,**kwargs):
            if request.user.is_authenticated:
                if group_list==None:
                    return func(request,*args,**kwargs)
                lesgroupes=request.user.groups.all()
                for x in group_list:
                    if x in lesgroupes:
                        return func(request,*args,**kwargs)
            return redirect('connexion')
        return nouvelle_func
    return teste

def envoie_mail(liste_destinataire,sujet,corps_mail): 
    if ENVOIE_MAIL:
        send_mail(subject=sujet,message=corps_mail,from_email=EMAIL_HOST_USER,recipient_list=liste_destinataire)
    else: 
        print(sujet+"\n"+corps_mail)

def hash(n=40):
    #renvoie 40 lettres/chiffres aléatoires
    val=digits+ascii_letters
    return ''.join(choice(val) for i in range(n))

def demande_creation_compte(request):
    def login_autorise(txt):
        # on n'autorise que les lettres et les chiffres
        return  match("^[a-zA-Z0-9]+$", txt) is not None
    try:
        login=request.POST['login']
        prenom=request.POST['prenom']
        nom=request.POST['nom']
        mail=request.POST['mail']
        password=request.POST['password']
        password_verif=request.POST['password_verif']
        if password!=password_verif:
            return False,"les mots de passe ne sont pas identiques"
        # teste si l'utilisateur existe déjà
        utilisateurs=User.objects.filter(username=login)
        if len(utilisateurs)>0:
            return False,"ce login n'est pas disponible"
        # inutile normalement sauf base corrompue
        utilisateurs=Utilisateur.objects.filter(user__username=login)
        if len(utilisateurs)>0:
            return False,"ce login n'est pas disponible"
        if not login_autorise(login):
            return False, "ce login contient des caractères interdits. Seuls les chiffres et les lettres (minuscules ou majuscules mais sans accent) sont autorisés"
    except:        
        return False,"Le formulaire est incomplet."
    try:
        new_user=User.objects.create_user(username=login,first_name=prenom,last_name=nom,email=mail,password=password)
        new_user.save()
        le_hash=hash()
        new_utilisateur=Utilisateur(user=new_user,csrf_token=le_hash,date_demande=datetime.datetime.now(),en_attente_confirmation=True)
        new_utilisateur.save()
    except:
        return False,"erreur lors de la création de compte"
    try:
        msg="Bonjour "+prenom+",\n\nVoici le lien pour activer le compte sur le site (valable 7 jours): \n" 
        msg+=URL_COMPLETE+"validation_compte/"+login+"/"+le_hash
        msg+="\n\nL'équipe de gestion"   
        envoie_mail([mail],'inscription site',msg)
        return True,"reussi"
    except:
        new_user.delete()
        new_utilisateur.delete()
        return False,"impossible d'envoyer le mail d'inscription"


# vérifie si on peut activer le compte login.
# renvoi "reussi" si c'est bon et un message d'erreur sinon
def verifie_lien_validation(login,lehash):
    try:
        user=User.objects.get(username=login)
        utilisateur=Utilisateur.objects.get(user=user,csrf_token=lehash)
        if not utilisateur.en_attente_confirmation:
            return "le compte associé est déjà validé"
        if utilisateur.date_demande+datetime.timedelta(days=7)<datetime.date.today():
            return "le lien a expiré"
        utilisateur.en_attente_confirmation=False
        utilisateur.save()
        return "le compte a bien été validé!"
    except:
        return "le lien est invalide"

def envoie_mail_recuperation_mot_de_passe(request):
    msg="Si le login et le mail correspondent à un compte existant, un mail a été envoyé pour réinitialiser le mot de passe."
    try:
        login=request.POST['login']
        mail=request.POST['mail']
        if login=="admin":
            return msg
        user=User.objects.get(username=login,email=mail)
        lehash=hash()
        utilisateur=Utilisateur.objects.get(user=user)
        if not utilisateur.autorise_modif:
            # modification de compte non autorisée : on sort
            return msg
        utilisateur.csrf_token=lehash
        utilisateur.date_demande=datetime.datetime.now()
        utilisateur.reinitialisation_password=True
        utilisateur.save()
        msg_mail="Bonjour "+user.first_name+",\n\n"
        msg_mail+="Une demande de réinitialisation de mail vient d'être envoyé pour ton compte.\n"
        msg_mail+="clique sur ce lien pour changer de mot de passe : "
        msg_mail+=URL_COMPLETE+"demande_reinitialisation/"+login+"/"+lehash
        msg_mail+="\n\nNe pas répondre, mail automatique."
        envoie_mail([mail],'Demande de récupération de compte, site MPSI',msg_mail)
        return msg
    except:
        return msg

# vérifie si la demande de récupération de mail est légitime
# renvoie un dictionnaire de contexte pour le template
# le champs autorise est mis à vrai si c'est bien autorisé
# le message d'erreu est alors dans msg
def verifie_lien_reinitialisation(login,lehash):
    try:
        user=User.objects.get(username=login)
        utilisateur=Utilisateur.objects.get(user=user,csrf_token=lehash)
        if not (utilisateur.reinitialisation_password and utilisateur.autorise_modif):
            return {"autorise" : False, "msg":"le lien est invalide"}
        if utilisateur.date_demande+datetime.timedelta(days=7)<datetime.date.today():
            return {"autorise" : False, "msg":"le lien a expiré"}
        return {"autorise" : True, "login" : login,"hash" : lehash}
    except:
        return {"autorise" : False, "msg":"le lien est invalide"}
  
def reinitialise_mot_de_passe(request):
    try:
        username=request.POST['login']
        lehash=request.POST['hash']
        newpassword=request.POST['password']
        user=User.objects.get(username=username)
        utilisateur=Utilisateur.objects.get(user=user,csrf_token=lehash)
        if not utilisateur.autorise_modif:
            # compte pour lequel toute modif est impossible
            return {"autorise" : False, "msg" : "action impossible"}
        if not utilisateur.reinitialisation_password:
            return {"autorise" : False, "msg":"le lien est invalide"}
        if utilisateur.date_demande+datetime.timedelta(days=7)<datetime.date.today():
            return {"autorise" : False, "msg":"le lien a expiré"}
        user.set_password(newpassword)
        user.save()
        login(request,user)                
        utilisateur.reinitialisation_password=False
        utilisateur.save()
        return {"autorise" : False, "msg" : "le mot de passe a été correctement modifié"}
    except:
        return {"autorise" : False, "msg":"le lien est invalide"}

