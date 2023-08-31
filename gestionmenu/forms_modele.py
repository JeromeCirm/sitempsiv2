#
#  Mis en modèle pour pouvoir modifier Renseignement principalement (à la fin)
#  mais trop de dépendances empêchent de le faire simplement
#  il est possible d'ajouter d'autres modèles/formes par contre
#

from django.forms import ModelForm
from .models import Fichier,Renseignements,Menu,ProgColle
from django import forms
from django.contrib.auth.models import Group, User

class FichierForm(ModelForm):
    class Meta:
        model=Fichier
        fields=['description','fichier']

class FichierUniqueForm(ModelForm):
    class Meta:
        model=Fichier
        fields=['fichier']

class FichierFormDescription(ModelForm):
    class Meta:
        model=Fichier
        fields=['description']

class FichierFormFichier(ModelForm):
    class Meta:
        model=Fichier
        fields=['fichier']

class MenuForm(ModelForm):
    type_de_menu=forms.ChoiceField(choices=[('l','liste de fichiers'),('f','fichier unique')])
    class Meta:
        model=Menu
        fields=['nom']

class MenuFormSimple(ModelForm):
    class Meta:
        model=Menu
        fields=['nom']

class ProgColleForm(ModelForm):
    class Meta:
        model=ProgColle
        fields=['numero','description','programme','exercices'] 

class ProgColleFormDescription(ModelForm):
    class Meta:
        model=ProgColle
        fields=['numero','description'] 

class ProgColleFormProgramme(ModelForm):
    class Meta:
        model=ProgColle
        fields=['programme'] 

class ProgColleFormExercices(ModelForm):
    class Meta:
        model=ProgColle
        fields=['exercices'] 

class RenseignementsFormProf(ModelForm):
    class Meta:
        model=Renseignements
        fields = '__all__'
        labels= {
            "nomusage" : "Nom d'usage",
            "prenomusage" : "Prénom d'usage",
            "naissance" : "Date de naissance",
            "tempstrajet" : "Temps de trajet Lycée-domicile (aller)",
            "seullogement" : "Es-tu seul(e) dans ton logement ?",
            "motivationprepa" : "Pourquoi avoir choisi MPSI?",
            "villelyceeorigine" : "Ville du lycée d'origine",
            "professionparents" : "Professions des parents",
            "freressoeurs" : "Renseignements sur les frères/soeurs",
            "calculatrice" : "Type de calculatrice utilisée",
            "accessordinateur" : "as-tu accès à un ordinateur personnel ?",
            "lyceeorigine" : "Nom du lycée d'origine",
            "connexioninternet" : "as-tu possibilité de te connecter régulièrement à internet ?"
        }
        exclude=('login','année')

# Ici, même chose mais en excluant les champs que l'élève ne doit pas modifié
# on ne met pas nomusage/prénomusage : c'est géré avec settings

class RenseignementsForm(RenseignementsFormProf):
    class Meta(RenseignementsFormProf.Meta):
         exclude=('login','année','prenomofficiel','nomofficiel','rne_lycee','lycee_officiel','ville_officiel','departement_officiel')
