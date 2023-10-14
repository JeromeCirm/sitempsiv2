
from django.urls import path
from . import views

try:
    from .urls_perso import urlpatterns_perso
except ImportError:
    print("pas de urlpatterns_perso dans urls_perso")
    from .urls_modele import urlpatterns_perso

urlpatterns = urlpatterns_perso+[
    path('menu/<int:numero>',views.menu,name='menu'),
    path('ajout_fichier/<int:pk>',views.ajout_fichier,name='ajout_fichier'),
    path('supprime_fichier/<int:pk>',views.supprime_fichier,name='supprime_fichier'),
    path('modifie_fichier/<int:pk>',views.modifie_fichier,name='modifie_fichier'),
    path('modifie_ordre_fichier/<int:pk>/<str:up>',views.modifie_ordre_fichier,name='modifie_ordre_fichier'),
    path('ajout_menu/<int:pk>',views.ajout_menu,name='ajout_menu'),
    path('supprime_menu/<int:pk>',views.supprime_menu,name='supprime_menu'),
    path('modifie_menu/<int:pk>',views.modifie_menu,name='modifie_menu'),
    path('modifie_ordre_menu/<int:pk>/<str:up>',views.modifie_ordre_menu,name='modifie_ordre_menu'),
    path('modifie_fichier_unique/<int:pk>',views.modifie_fichier_unique,name='modifie_fichier_unique'),
    path('supprime_fiche/<int:pk>',views.supprime_fiche,name='supprime_fiche'),
    path('download/<int:pk>',views.download,{'letype':'file'},name='download'),
    path('download/fiche/<int:pk>',views.download,{'letype':'fiche'},name='download_fiche'),
    path('download/prog/<int:id_menu>/<int:pk>',views.download,{'letype':'prog'},name='download_prog'),
    path('download/exos/<int:id_menu>/<int:pk>',views.download,{'letype':'exos'},name='download_exos'), 
    path('downloadpronote',views.download_pronote,name='download_pronote'),
    path('recupere_eleves',views.recupere_eleves,name='recupere_eleves'),
    path('ajout_prog_colle/<int:id_menu>',views.ajout_prog_colle,name='ajout_prog_colle'),
    path('supprime_prog_colle/<int:id_menu>/<int:pk>',views.supprime_prog_colle,name='supprime_prog_colle'),
    path('modifie_prog_colle/<int:id_menu>/<int:pk>',views.modifie_prog_colle,name='modifie_prog_colle'),
    path('recuperation_notes_colles',views.recuperation_notes_colles,name='recuperation_notes_colles'),
    path('maj_notes_colles',views.maj_notes_colles,name='maj_notes_colles'),
    path('recuperation_informations_home',views.recuperation_informations_home,name='recuperation_informations_home'),
    path('recuperation_colloscope_semaine',views.recuperation_colloscope_semaine,name='recuperation_colloscope_semaine'),
    path('recuperation_creneaux',views.recuperation_creneaux,name='recuperation_creneaux'),
    path('creation_creneaux_groupe',views.creation_creneaux_groupe,name='creation_creneaux_groupe'),
    path('suppression_creneaux_groupe',views.suppression_creneaux_groupe,name='suppression_creneaux_groupe'),
    path('creation_creneaux_eleve',views.creation_creneaux_eleve,name='creation_creneaux_eleve'),
    path('recuperation_creneaux_individuels',views.recuperation_creneaux_individuels,name='recuperation_creneaux_individuels'),
    path('action_creneaux_individuels',views.action_creneaux_individuels,name='action_creneaux_individuels'),
    path('recuperation_creneaux_individuels_gestionnaire',views.recuperation_creneaux_individuels_gestionnaire,name='recuperation_creneaux_individuels_gestionnaire'),
    path('action_creneaux_individuels_gestionnaire',views.action_creneaux_individuels_gestionnaire,name='action_creneaux_individuels_gestionnaire'),
    path('maj_commentaire_notes_colles',views.maj_commentaire_notes_colles,name='maj_commentaire_notes_colles'),
    path('recupere_commentaire_notes_colles',views.recupere_commentaire_notes_colles,name='recupere_commentaire_notes_colles'),
    path('modifie_creneau',views.modifie_creneau,name='modifie_creneau'),
    path('recuperation_notes_colles_semaine',views.recuperation_notes_colles_semaine,name='recuperation_notes_colles_semaine'),
    ]
