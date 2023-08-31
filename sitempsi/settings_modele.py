# 
#  exemple de fichier configuration utilisable en local
# 

MY_SECRET_KEY = 'django-insecure-$sp&6x*kkoimrhn$dy*a=&_p^5k7hd$$0&74z0hby1ibzmg2ql'
# Passer Debug à False pour l'utilisation réelle
MY_DEBUG = True
# l'url du site, sans https ni www
MY_ALLOWED_HOSTS = ['127.0.0.1']
# l'adresse sur le serveur ou sont rangés les fichiers "static"
# qui seront livrés par apache et non django
# sans doute quelquechose comme   "/home/nomcompte/nomdusite/static"
MY_STATIC_ROOT = 'C:/Users/jerome/Documents/GitHub/sitempsi_v2/static'

# mettre les trois à "True" pour l'utilisation réelle
MY_SECURE_SSL_REDIRECT = False
MY_SESSION_COOKIE_SECURE = False
MY_CSRF_COOKIE_SECURE = False

# adresse pour accéder à la partie admin : la cacher un peu en utilisation réelle
MY_ADMIN_URL="admin/"