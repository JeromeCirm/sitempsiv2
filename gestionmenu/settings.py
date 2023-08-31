try:
    from .settings_perso import *
except ImportError:
    print("pas de fichier settings_perso")
    from .settings_modele import *
import locale
from .forms import RenseignementsForm
from django.contrib.auth.models import Group

locale.setlocale(locale.LC_ALL,'fr_FR.UTF-8')

autoriser_changement_nom = my_autoriser_changement_nom
autoriser_changement_renseignement = my_autoriser_changement_renseignement
annee_courante = my_annee_courante
gestionnaires_pdf = my_gestionnaires_pdf

if not autoriser_changement_nom:
    RenseignementsForm.Meta.exclude=(*RenseignementsForm.Meta.exclude,'nomusage','prenomusage')

try:
    groupe_eleves=Group.objects.get(name='eleves')
    groupe_profs=Group.objects.get(name='profs')
    groupe_generic=Group.objects.get(name='generic')
except:
    print("attention, groupes eleves/profs/generic non créés")
