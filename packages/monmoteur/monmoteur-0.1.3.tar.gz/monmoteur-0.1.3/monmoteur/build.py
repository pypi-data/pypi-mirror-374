import ctypes
from ctypes import c_int, c_float, c_bool, c_void_p, POINTER, c_double
import importlib.resources as pkg_resources
import monmoteur  # ton package contenant la DLL

TAILLE_LIEN_GT = 256

# --------------------
# Structures C
# --------------------
class TextureEntry(ctypes.Structure):
    _fields_ = [("id", ctypes.c_char * TAILLE_LIEN_GT),
                ("texture", c_void_p)]

class GestionnaireTextures(ctypes.Structure):
    _fields_ = [("entrees", POINTER(TextureEntry)),
                ("taille", c_int),
                ("capacite", c_int),
                ("rendu", c_void_p)]

class SonEntry(ctypes.Structure):
    _fields_ = [("id", ctypes.c_char * TAILLE_LIEN_GT),
                ("son", c_void_p)]

class GestionnaireSon(ctypes.Structure):
    _fields_ = [("entrees", POINTER(SonEntry)),
                ("taille", c_int),
                ("capacite", c_int)]

class GestionnaireEntrees(ctypes.Structure):
    _fields_ = [("mouse_x", c_int),
                ("mouse_y", c_int),
                ("mouse_pressed", c_bool),
                ("mouse_just_pressed", c_bool),
                ("keys", c_bool * 512),
                ("keys_pressed", c_bool * 512),
                ("quit", c_bool)]

class Image(ctypes.Structure):
    _fields_ = [("id", c_int),
                ("posx", c_float),
                ("posy", c_float),
                ("taillex", c_float),
                ("tailley", c_float),
                ("sens", c_int),
                ("rotation", c_int),
                ("texture", c_void_p)]

class TableauImage(ctypes.Structure):
    _fields_ = [("tab", POINTER(Image)),
                ("nb_images", c_int),
                ("capacite_images", c_int)]

class FondActualiser(ctypes.Structure):
    _fields_ = [("r", c_int),
                ("g", c_int),
                ("b", c_int),
                ("dessiner", c_bool),
                ("bande_noir", c_bool)]

class Gestionnaire(ctypes.Structure):
    _fields_ = [
        ("run", c_bool),
        ("dt", c_float),
        ("fps", c_float),
        ("largeur", c_int),
        ("hauteur", c_int),
        ("coeff_minimise", c_int),
        ("largeur_actuel", c_int),
        ("hauteur_actuel", c_int),
        ("decalage_x", c_float),
        ("decalage_y", c_float),
        ("plein_ecran", c_bool),
        ("temps_frame", c_int),
        ("fenetre", c_void_p),
        ("rendu", c_void_p),
        ("fond", POINTER(FondActualiser)),
        ("image", POINTER(TableauImage)),
        ("entrees", POINTER(GestionnaireEntrees)),
        ("textures", POINTER(GestionnaireTextures)),
        ("sons", POINTER(GestionnaireSon)),
    ]

# --------------------
# Charger la DLL
# --------------------
def charger_dll():
    dll_path = pkg_resources.files(monmoteur) / "dll" / "jeu.dll"
    return ctypes.CDLL(str(dll_path))

jeu = charger_dll()

# --------------------
# Signatures C
# --------------------
jeu.initialisation.argtypes = (
    c_int, c_int, c_float, c_int,
    ctypes.c_char_p, ctypes.c_char_p,
    c_bool, c_bool,
    c_int, c_int, c_int
)
jeu.initialisation.restype = POINTER(Gestionnaire)

jeu.boucle_principale.argtypes = (POINTER(Gestionnaire),)
jeu.boucle_principale.restype = None

jeu.liberer_jeu.argtypes = (POINTER(Gestionnaire),)
jeu.liberer_jeu.restype = None

# sons
jeu.jouer_son.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p, c_int, c_int)
jeu.jouer_son.restype = None
jeu.arreter_canal.argtypes = (c_int,)
jeu.arreter_canal.restype = None
jeu.arreter_son.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p)
jeu.arreter_son.restype = None

# images
jeu.ajouter_image_au_tableau.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p, c_float, c_float, c_float, c_float, c_int, c_int, c_int)
jeu.ajouter_image_au_tableau.restype = c_int

jeu.supprimer_images_par_id.argtypes = (POINTER(Gestionnaire), c_int)
jeu.supprimer_images_par_id.restype = None

jeu.modifier_images.argtypes = (POINTER(Gestionnaire), c_float, c_float, c_float, c_float, c_int, c_int, c_int)
jeu.modifier_images.restype = None

jeu.modifier_texture_image.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p, c_int)
jeu.modifier_texture_image.restype = None

jeu.touche_juste_presse.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p)
jeu.touche_juste_presse.restype = c_bool

jeu.touche_enfoncee.argtypes = (POINTER(Gestionnaire), ctypes.c_char_p)
jeu.touche_enfoncee.restype = c_bool

jeu.redimensionner_fenetre.argtypes = (POINTER(Gestionnaire),)
jeu.redimensionner_fenetre.restype = None

# --------------------
# Math alias
# --------------------
import math
_math_aliases = {
    "abs_val": "abs",
    "clamp": "clamp",
    "pow_custom": "pow",
    "sqrt_custom": "sqrt",
    "cbrt_custom": "cbrt",
    "exp_custom": "exp",
    "log_custom": "log",
    "log10_custom": "log10",
    "log2_custom": "log2",
    "sin_custom": "sin",
    "cos_custom": "cos",
    "tan_custom": "tan",
    "asin_custom": "asin",
    "acos_custom": "acos",
    "atan_custom": "atan",
    "atan2_custom": "atan2",
    "sinh_custom": "sinh",
    "cosh_custom": "cosh",
    "tanh_custom": "tanh",
    "asinh_custom": "asinh",
    "acosh_custom": "acosh",
    "atanh_custom": "atanh",
    "floor_custom": "floor",
    "ceil_custom": "ceil",
    "round_custom": "round",
    "trunc_custom": "trunc",
    "fmod_custom": "fmod",
    "hypot_custom": "hypot",
}
for cname, alias in _math_aliases.items():
    if hasattr(jeu, cname):
        f = getattr(jeu, cname)
        # special cases pour fonctions à 2 arguments
        if cname == "atan2_custom" or cname == "hypot_custom":
            f.argtypes = [c_double, c_double]
        else:
            f.argtypes = [c_double]
        f.restype = c_double
        globals()[alias] = f

# --------------------
# API Python
# --------------------
_gestionnaire_global = None

def initialisation(largeur=320, hauteur=180, dt=1/60, coeff_ecran_minimise=3,
                   chemin_image="", chemin_son="", dessiner_fond=True,
                   bande_noir=False, r=0, g=0, b=0):
    global _gestionnaire_global
    if isinstance(chemin_image, str):
        chemin_image = chemin_image.encode("utf-8")
    if isinstance(chemin_son, str):
        chemin_son = chemin_son.encode("utf-8")
    _gestionnaire_global = jeu.initialisation(
        hauteur, largeur, dt, coeff_ecran_minimise,
        chemin_image, chemin_son,
        dessiner_fond, bande_noir,
        r, g, b
    )
    if not _gestionnaire_global:
        raise RuntimeError("Erreur d'initialisation du moteur")
    return _gestionnaire_global

def lancer():
    if not _gestionnaire_global:
        raise RuntimeError("Le moteur n’a pas été initialisé !")
    jeu.boucle_principale(_gestionnaire_global)

def liberer():
    global _gestionnaire_global
    if _gestionnaire_global:
        jeu.liberer_jeu(_gestionnaire_global)
        _gestionnaire_global = None

def jouer_son(lien: str, boucle: int = 0, canal: int = -1):
    if not _gestionnaire_global:
        raise RuntimeError("Pas de gestionnaire initialisé")
    if isinstance(lien, str):
        lien = lien.encode("utf-8")
    jeu.jouer_son(_gestionnaire_global, lien, boucle, canal)

def arreter_canal(canal: int):
    jeu.arreter_canal(canal)

def arreter_son(lien: str):
    if not _gestionnaire_global:
        raise RuntimeError("Pas de gestionnaire initialisé")
    if isinstance(lien, str):
        lien = lien.encode("utf-8")
    jeu.arreter_son(_gestionnaire_global, lien)

def ajouter_image(chemin, x, y, w, h, id_num, sens=0, rotation=0):
    if isinstance(chemin, str):
        chemin = chemin.encode("utf-8")
    return jeu.ajouter_image_au_tableau(_gestionnaire_global, chemin, x, y, w, h, sens, id_num, rotation)

def supprimer_images(id_num):
    jeu.supprimer_images_par_id(_gestionnaire_global, id_num)

def modifier_image(x, y, w, h, sens, id_num, rotation=0):
    jeu.modifier_images(_gestionnaire_global, x, y, w, h, sens, id_num, rotation)

def changer_texture(chemin, id_num):
    if isinstance(chemin, str):
        chemin = chemin.encode("utf-8")
    jeu.modifier_texture_image(_gestionnaire_global, chemin, id_num)

def touche_juste_presse(touche: str) -> bool:
    return jeu.touche_juste_presse(_gestionnaire_global, touche.encode("utf-8"))

def touche_enfoncee(touche: str) -> bool:
    return jeu.touche_enfoncee(_gestionnaire_global, touche.encode("utf-8"))

def redimensionner():
    jeu.redimensionner_fenetre(_gestionnaire_global)
