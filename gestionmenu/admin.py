try:
    from .admin_perso import *
except ImportError:
    print("pas de fichier admin_perso")
    from .admin_modele import *