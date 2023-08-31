from django.contrib import admin
from .models import *

class UtilisateurAdmin(admin.ModelAdmin):
    list_display=('user','date_demande','en_attente_confirmation','reinitialisation_password')

admin.site.register(Utilisateur,UtilisateurAdmin)
