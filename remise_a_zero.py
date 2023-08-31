# ne lancer que la toute première fois : 
# efface complètement la base de données, tous les fichiers, etc...
# et crée uniquement un compte admin
# et un menu permettant d'accéder à l'initialisation 

import os
import shutil

admin_login=input("login admin (vide pour admin) : ")
if admin_login=="":
    admin_login="admin"
admin_mdp=input("mot de passe admin (vide pour admin) : ")
if admin_mdp=="":
    admin_mdp="admin"
else:
    confirm_mdp=input("entrer de nouveau le mot de passe : ")
    if confirm_mdp!=admin_mdp:
        print("les deux mots de passe ne coïncident pas")
        exit()

shutil.rmtree('private_files', ignore_errors=True)
shutil.rmtree('base/migrations', ignore_errors=True)
shutil.rmtree('gestionmenu/migrations', ignore_errors=True)
os.mkdir('private_files')
os.mkdir('private_files/fichiers')
os.mkdir('base/migrations')
os.mkdir('gestionmenu/migrations')
f=open('base/migrations/__init__.py',"w")
f.close()
f=open('gestionmenu/migrations/__init__.py',"w")
f.close()

try:
    pass
    os.remove('db.sqlite3')
except:
    pass

os.system("python manage.py makemigrations")
os.system("python manage.py migrate")
os.system("python manage.py remise_a_zero_command "+admin_login+" "+admin_mdp)

print("Réinitialisation terminée.")

