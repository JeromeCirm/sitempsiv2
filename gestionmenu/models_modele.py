#
#  Mis en modèle pour pouvoir modifier Renseignement principaelemtn
#  mais trop de dépendances empêchent de le faire simplement
#  il est possible d'ajouter d'autres modèles par contre
#

from django.db import models
from django.contrib.auth.models import Group, User
from django.db.models.signals import pre_delete,post_delete
from django.dispatch import receiver
from os import remove,rmdir

class Menu(models.Model):
    nom=models.CharField(max_length=40)
    parent=models.IntegerField(blank=True)  # 0 pour un menu principal
    fonction=models.CharField(max_length=50,blank=True,default="")  #  fonction à appeler : vide s'il y des sous-menus
    groupes=models.ManyToManyField(Group,blank=True)
    gestionnaires=models.ManyToManyField(User,blank=True)
    ordre=models.IntegerField(default=0) # ordre dans le sous-menu

    def __str__(self):
        return self.nom+",id "+str(self.pk)+", parent "+str(self.parent)+",ordre "+str(self.ordre)+" "+str(self.fonction)

    class Meta : 
        ordering=['parent','ordre']

@receiver(pre_delete,sender=Menu)
def gestion_delete_menu_dir(sender, instance, using, **kwargs):
    if instance.fonction=="programme_colle":
        try:
            rmdir('private_files/prog_colle_'+str(instance.id))
        except:
            pass

def extension(nomfichier):
    l=str(nomfichier).split(".")
    if len(l)==1:
        return ""
    return "."+l[-1]

class Fichier(models.Model):
    description=models.CharField(max_length=5000,default="",blank=True)
    def uploadpath(self,filename):
        return 'private_files/fichiers/'+str(self.id)+extension(self.nomfichier)
    fichier=models.FileField(null=True,blank=True,upload_to=uploadpath)
    nomfichier=models.CharField(max_length=100,null=True,blank=True)
    ordre=models.IntegerField(null=True,blank=True)
    menu=models.ForeignKey(Menu,on_delete=models.CASCADE,blank=True,null=True)
    date_parution=models.DateField(blank=True,null=True)
    type_fichier=models.CharField(max_length=100,default="",blank=True,null=True)

    def __str__(self):
        return str(self.nomfichier)+" : "+str(self.description)

    class Meta : 
        ordering=['-ordre']

@receiver(post_delete,sender=Fichier)
def gestion_delete_file(sender, instance, using, **kwargs):
    try:
        remove(instance.uploadpath(None))
    except:
        pass

class Semaines(models.Model):
    numero=models.IntegerField()
    date=models.DateField()

    def __str__(self):
        return str(self.numero)

class CreneauxColleurs(models.Model):
    colleur=models.ForeignKey(User,on_delete=models.CASCADE)
    jour=models.CharField(max_length=20,blank=True,default="")
    horaire=models.CharField(max_length=20,blank=True,default="")
    salle=models.CharField(max_length=20,blank=True,default="")
    matière=models.CharField(max_length=20,blank=True,default="")   # copie de infocolleurs pour faciliter 
    numero=models.IntegerField(blank=True,null=True)           # utilisation libre pour créer le colloscope par ex

    def __str__(self):
        return self.colleur.username+": "+str(self.jour)+" "+str(self.horaire)
    
class InfoColleurs(models.Model):
    colleur=models.ForeignKey(User,on_delete=models.CASCADE)
    prof=models.ForeignKey(User,related_name='%(class)s_requests_created',on_delete=models.CASCADE) #pour eviter le clash des deux ForeignKey
    matière=models.CharField(max_length=20,blank=True,default="") # important pour repérer un colleur sans créneaux pour l'instant

class GroupeColles(models.Model):
    numero=models.IntegerField()
    eleves=models.ManyToManyField(User)

    def __str__(self):
        return str(self.numero)

class Colloscope(models.Model):
    semaine=models.ForeignKey(Semaines,on_delete=models.CASCADE)
    groupe=models.ForeignKey(GroupeColles,on_delete=models.CASCADE)
    creneau=models.ForeignKey(CreneauxColleurs,on_delete=models.CASCADE)

class Colloscope_individuel(models.Model):
    semaine=models.ForeignKey(Semaines,on_delete=models.CASCADE)
    eleve=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,default=None,blank=True)
    creneau=models.ForeignKey(CreneauxColleurs,on_delete=models.CASCADE)
    optionnel=models.BooleanField(null=True,blank=True,default=False)

class Gestion_colles_individuelles(models.Model):
    matiere=models.CharField(max_length=100,null=True,blank=True) 
    titre=models.CharField(max_length=100,null=True,blank=True)
    responsables=models.ManyToManyField(User)
    max_par_eleve=models.IntegerField()
    max_garanti=models.IntegerField()
    modif_par_eleves=models.BooleanField()

class Divers(models.Model):
    label=models.CharField(max_length=30)
    contenu=models.TextField()

class ProgColle(models.Model):
    numero=models.IntegerField()
    description=models.CharField(max_length=5000,default="")
    def uploadpathprog(self,filename):
        return 'private_files/prog_colle_'+str(self.menu.id)+'/prog'+str(self.id)+extension(self.nomprogramme)
    def uploadpathexos(self,filename):
        return 'private_files/prog_colle_'+str(self.menu.id)+'/exos'+str(self.id)+extension(self.nomexercices)
    programme=models.FileField(null=True,blank=True,upload_to=uploadpathprog) 
    nomprogramme=models.CharField(max_length=100,null=True,blank=True)
    exercices=models.FileField(null=True,blank=True,upload_to=uploadpathexos) 
    nomexercices=models.CharField(max_length=100,null=True,blank=True)
    menu=models.ForeignKey(Menu,on_delete=models.CASCADE)

    class Meta : 
        ordering=['-numero']

@receiver(pre_delete,sender=ProgColle)
def gestion_delete_prog_file(sender, instance, using, **kwargs):
    try:
        remove(instance.uploadpathprog(None))
    except:
        pass
    try:
        remove(instance.uploadpathexos(None))
    except:
        pass

class NotesColles(models.Model):
    colleur=models.ForeignKey(User,on_delete=models.CASCADE)
    creneau=models.ForeignKey(CreneauxColleurs,on_delete=models.SET_NULL,null=True,default=None,blank=True)
    eleve=models.ForeignKey(User,related_name='%(class)s_requests_created',on_delete=models.CASCADE) #pour eviter le clash des deux ForeignKey
    note=models.IntegerField()
    semaine=models.ForeignKey(Semaines,on_delete=models.CASCADE)

class Renseignements(models.Model):
    # les 4 premiers sont indispensables pour le site : ne pas effacer
    login=models.CharField(max_length=50)
    année=models.IntegerField(null=True,blank=True)
    # les champs que l'élève peut modifier, dans l'ordre d'apparition dans le formulaire
    seullogement=models.BooleanField(null=True,blank=True)
    motivationprepa=models.TextField(null=True,blank=True)
    lyceeorigine=models.CharField(max_length=50,null=True,blank=True)
    villelyceeorigine=models.CharField(max_length=50,null=True,blank=True)
    professionparents=models.TextField(null=True,blank=True)
    freressoeurs=models.TextField(null=True,blank=True)
    calculatrice=models.CharField(max_length=50,null=True,blank=True)
    tempstrajet=models.IntegerField(null=True,blank=True)
    accessordinateur=models.BooleanField(null=True,blank=True)
    connexioninternet=models.BooleanField(null=True,blank=True)
    evalcours=[['1','1 :quasi inexistant'],['2','2'],['3','3'],['4','4'],['5','5 : sans changement notable']]
    coursconfinementmath=models.CharField(max_length=1,choices=evalcours,null=True,blank=True)
    coursconfinementphysique=models.CharField(max_length=1,choices=evalcours,null=True,blank=True)
    confinementcommentaire=models.TextField(null=True,blank=True)
    notesbac=models.TextField(null=True,blank=True)
    # les champs que le site remplit lui-même à un moment 
    # !!!!!!!!
    #  Penser à les exclure dans la classe RenseignementsForm
    # les deux premiers sont indispensables pour l'exportation pronote : 
    # modifier la fonction si on les enlève
    prenomofficiel=models.CharField(max_length=50,null=True,blank=True)
    nomofficiel=models.CharField(max_length=50,null=True,blank=True)
    date_naissance_officiel=models.DateField(blank=True,null=True)
    rne_lycee=models.CharField(max_length=50,null=True,blank=True)
    lycee_officiel=models.CharField(max_length=50,null=True,blank=True)
    ville_officiel=models.CharField(max_length=50,null=True,blank=True)
    departement_officiel=models.CharField(max_length=50,null=True,blank=True)

# les fichiers ajoutés par les gestionnaires aux fiches élèves
class FichierFiches(models.Model):
    fiche=models.ForeignKey(Renseignements,on_delete=models.CASCADE)
    def uploadpath(self,filename):
        return 'private_files/fiches/'+str(self.fiche.année)+'/'+str(self.id)+extension(self.nomfichier)
    fichier=models.FileField(null=True,blank=True,upload_to=uploadpath)
    nomfichier=models.CharField(max_length=100,null=True,blank=True)

@receiver(pre_delete,sender=FichierFiches)
def gestion_delete_prog_file(sender, instance, using, **kwargs):
    try:
        remove(instance.uploadpath(None))
    except:
        pass

class CommentaireColle(models.Model):
   notecolle=models.ForeignKey(NotesColles,on_delete=models.CASCADE,null=True,blank=True,default=None)
   # notecolle en cas de commentaire pour la note d'un élève, inutile sinon
   colle=models.ForeignKey(Colloscope,on_delete=models.CASCADE,null=True,blank=True,default=None) 
   # colle en cas de commentaire pour un groupe entier, inutile sinon
   text=models.CharField(max_length=1000,null=True,blank=True)
   def uploadpath(self,filename):
       return 'private_files/commentairescolles/'+str(self.id)+extension(self.nomfichier)
   fichier=models.FileField(null=True,blank=True,upload_to=uploadpath)
   nomfichier=models.CharField(max_length=100,null=True,blank=True)

class Sondages(models.Model):
    createur=models.ForeignKey(User,on_delete=models.CASCADE)
    titre=models.TextField(null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    type_sondage=models.TextField(null=True,blank=True)
    actif=models.BooleanField(null=True,blank=True)
    visible=models.BooleanField(null=True,blank=True)
    date=models.DateField(blank=True,null=True)

class SondagesItem(models.Model):
    sondage=models.ForeignKey(Sondages,on_delete=models.CASCADE)
    texte=models.TextField(null=True,blank=True)
    numero=models.IntegerField(null=True,blank=True)

class SondagesReponse(models.Model):
    utilisateur=models.ForeignKey(User,on_delete=models.CASCADE)
    reponse=models.TextField(null=True,blank=True)
    sondage=models.ForeignKey(Sondages,on_delete=models.CASCADE)

class PrecisionColle(models.Model):
    colleindiv=models.ForeignKey(Colloscope_individuel,on_delete=models.CASCADE,null=True,blank=True,default=None)
    # colleindiv en cas de commentaire pour la colle d'un élève, inutile sinon
    collegroupe=models.ForeignKey(Colloscope,on_delete=models.CASCADE,null=True,blank=True,default=None) 
    # collegroupe en cas de commentaire pour un groupe entier, inutile sinon
    text=models.CharField(max_length=1000,null=True,blank=True)
    def uploadpath(self,filename):
       return 'private_files/precisioncolle/'+str(self.id)+extension(self.nomfichier)
    fichier=models.FileField(null=True,blank=True,upload_to=uploadpath)
    nomfichier=models.CharField(max_length=100,null=True,blank=True)