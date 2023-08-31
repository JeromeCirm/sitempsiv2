try:
    from .models_perso import *
except ImportError:
    print("pas de fichier models_perso")
    from .models_modele import *