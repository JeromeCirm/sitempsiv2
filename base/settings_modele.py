# 
#  exemple de fichier configuration utilisable en local
# 

# gestion des mails
# pas besoin de rensigner les information ici car l'envoi n'a pas lieu
MY_EMAIL_USE_TLS=True
MY_EMAIL_HOST_USER = '' 
MY_EMAIL_HOST_PASSWORD = '' 
MY_EMAIL_HOST = ''
MY_EMAIL_PORT = 587

# envoie un mail (True)  ou bien affiche le texte dans la console (False)
MY_ENVOIE_MAIL = False
# l'url est indispensable pour créer un lien d'activation/récupération de compte par mail
MY_URL_COMPLETE = 'http://127.0.0.1:8000/'

# autorisation creation compte/récupération de mot de passe par mail
MY_AUTORISE_CREATION = False          # 
MY_AUTORISE_RECUPERATION = True

# le titre du site
MY_TITRE_SITE='titre version modele'
