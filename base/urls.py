
from django.urls import path,include,re_path
from . import views

urlpatterns = [
    path('change_mdp',views.change_mdp,name='change_mdp'),
    path('connexion',views.connexion,name='connexion'),
    path('deconnexion',views.deconnexion,name='deconnexion'),
    path('recuperation_password',views.recuperation_password,name='recuperation_password'),
    path('creation_compte',views.creation_compte,name='creation_compte'),
    path('validation_compte/<str:login>/<str:lehash>',views.validation_compte,name='validation_compte'),
    re_path(r'validation_comptea*',views.validation_compte,name='validation_compte_erreur'),
    path('demande_reinitialisation/<str:login>/<str:lehash>',views.demande_reinitialisation,name='demande_reinitialisation'),
    re_path(r'demande_reinitialisationa*',views.demande_reinitialisation,name='demande_reinitialisation_erreur'),
    re_path(r'a*', views.home,name='home'),    
    ]