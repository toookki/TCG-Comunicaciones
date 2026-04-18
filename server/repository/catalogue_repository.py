import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOGUE_PATH = os.path.join(BASE_DIR, "data", "catalogue.json")

def load_catalogue():
    with open(CATALOGUE_PATH, "r") as f:
        return json.load(f)

def save_catalogue(catalogue):
    with open(CATALOGUE_PATH, "w") as f:
        json.dump(catalogue, f, indent=4)