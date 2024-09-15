#
#  Mis en modèle pour pouvoir modifier Renseignement principalement
#  mais trop de dépendances empêchent de le faire simplement
#  il est possible d'ajouter d'autres modèles/form/admin par contre
#

from django.contrib import admin
from .models import *

class MenuAdmin(admin.ModelAdmin):
    list_display=('nom','id','parent','ordre','fonction')

class FichierAdmin(admin.ModelAdmin):
    pass

class ProgColleAdmin(admin.ModelAdmin):
    pass

class SemainesAdmin(admin.ModelAdmin):
    list_display=('numero','date')

class CreneauxColleursAdmin(admin.ModelAdmin):
    list_display=('numero','colleur','jour','horaire','matière','salle')

class InfoColleursAdmin(admin.ModelAdmin):
    list_display=('colleur','prof','matière')

class GroupeCollesAdmin(admin.ModelAdmin):
    list_display=('numero','get_eleves')

    def get_eleves(self,obj):
        return ", ".join([x.username for x in obj.eleves.all()])

class ColloscopeAdmin(admin.ModelAdmin):
    list_display=('semaine','groupe','creneau')

class RenseignementsAdmin(admin.ModelAdmin):
    list_display=('login','année')

class DiversAdmin(admin.ModelAdmin):
    pass

class NotesCollesAdmin(admin.ModelAdmin):
    pass

class Colloscope_individuelAdmin(admin.ModelAdmin):
    list_display=('semaine','eleve','creneau','optionnel')

class Gestion_colles_individuellesAdmin(admin.ModelAdmin):
    pass

class CommentaireColleAdmin(admin.ModelAdmin):
    pass

class SondagesAdmin(admin.ModelAdmin):
    pass

class SondagesItemAdmin(admin.ModelAdmin):
    pass

class SondagesReponseAdmin(admin.ModelAdmin):
    pass

class GroupesTDAdmin(admin.ModelAdmin):
    pass
    
class Gestion_colloscope_individuelAdmin(admin.ModelAdmin):
    pass

class Gestion_plage_colloscope_individuelAdmin(admin.ModelAdmin):
    pass

admin.site.register(Sondages,SondagesAdmin)
admin.site.register(SondagesItem,SondagesItemAdmin)
admin.site.register(SondagesReponse,SondagesReponseAdmin)
admin.site.register(NotesColles,NotesCollesAdmin)
admin.site.register(Divers,DiversAdmin)
admin.site.register(Menu,MenuAdmin)
admin.site.register(Fichier,FichierAdmin)
admin.site.register(ProgColle,ProgColleAdmin)
admin.site.register(Semaines,SemainesAdmin)
admin.site.register(CreneauxColleurs,CreneauxColleursAdmin)
admin.site.register(InfoColleurs,InfoColleursAdmin)
admin.site.register(GroupeColles,GroupeCollesAdmin)
admin.site.register(Colloscope,ColloscopeAdmin)
admin.site.register(Renseignements,RenseignementsAdmin)
admin.site.register(Colloscope_individuel,Colloscope_individuelAdmin)
admin.site.register(Gestion_colles_individuelles,Gestion_colles_individuellesAdmin)
admin.site.register(CommentaireColle,CommentaireColleAdmin)
admin.site.register(GroupesTD,GroupesTDAdmin)
admin.site.register(Gestion_colloscope_individuel,Gestion_colloscope_individuelAdmin)
admin.site.register(Gestion_plage_colloscope_individuel,Gestion_plage_colloscope_individuelAdmin)

