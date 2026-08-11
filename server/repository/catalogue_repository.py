"""
Repositorio del Catálogo.
Abstrae el acceso a los datos persistentes del catálogo público (catalogue.json).
Es el único componente autorizado para leer, modificar y proteger mediante cerrojos
(locks) la concurrencia sobre dicho archivo.
"""

import json
import threading
import os

catalogue_lock = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOGUE_PATH = os.path.join(BASE_DIR, "data", "catalogue.json")

def load_catalogue():
    with open(CATALOGUE_PATH, "r") as f:
        return json.load(f)

def save_catalogue(catalogue):
    with open(CATALOGUE_PATH, "w") as f:
        json.dump(catalogue, f, indent=4)

def get_catalogue_lock():
    return catalogue_lock