try:
    from .forms_perso import *
except ImportError:
    print("pas de fichier form_perso")
    from .forms_modele import *