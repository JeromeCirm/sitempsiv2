from django.db import models
from django.contrib.auth.models import User

class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_demande=models.DateField(null=True,blank=True,default=None)
    csrf_token=models.TextField(null=True,blank=True,default=None)
    en_attente_confirmation=models.BooleanField(default=True,blank=True) # lien envoyé et non validé par mail
    reinitialisation_password=models.BooleanField(default=False,blank=True)
    autorise_modif=models.BooleanField(default=True,blank=True)
    doit_changer_mdp=models.BooleanField(default=True,blank=True)
