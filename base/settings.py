try:
    from .settings_perso import *
except:
    from .settings_modele import *

EMAIL_USE_TLS = MY_EMAIL_USE_TLS
EMAIL_HOST_USER = MY_EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = MY_EMAIL_HOST_PASSWORD
EMAIL_HOST = MY_EMAIL_HOST
EMAIL_PORT = MY_EMAIL_PORT
URL_COMPLETE = MY_URL_COMPLETE

# Autorisation des pages de création de compte/récupération du mot de passe
AUTORISE_CREATION = MY_AUTORISE_CREATION
AUTORISE_RECUPERATION = MY_AUTORISE_RECUPERATION

# possibilité de ne pas envoyer le mail et d'afficher le texte en console
ENVOIE_MAIL = MY_ENVOIE_MAIL

# données générales du site
TITRE_SITE=MY_TITRE_SITE
