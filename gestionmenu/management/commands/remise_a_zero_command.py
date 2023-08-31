from django.core.management.base import BaseCommand
from gestionmenu.initialisation import *
from gestionmenu.fonctions import creation_compte
from django.contrib.auth.models import Group
from gestionmenu.models import Divers


class Command(BaseCommand):
    help = 'Adds a user to django'

    def add_arguments(self, parser):
        parser.add_argument('admin_login')
        parser.add_argument('admin_password')

    def handle(self, *args, **options):
        user=creation_compte(options["admin_login"],options["admin_password"],[],True,{})
        user.is_admin=True
        user.is_staff=True
        user.is_superuser=True
        user.save()
        user.utilisateur.autorise_modif=False
        user.utilisateur.doit_changer_mdp=False
        user.utilisateur.save()
        creation_menu_site({},[["Initialisation","initialisation",[],[],[]]])

        Group(name="profs").save()
        Group(name="eleves").save()
        Group(name="generic").save()
        Group(name="gestion_colles").save()
        Divers(label="annonce",contenu="").save()
