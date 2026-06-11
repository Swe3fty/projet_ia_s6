# -*- coding: utf-8 -*-
"""
Prediction de la classe de puissance d'une borne.
"""

import os
import pandas as pd
import joblib

# Dossier du script : toutes les ressources sont chargees/enregistrees ici
DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_MODELE = os.path.join(DOSSIER, 'modele_puissance.pkl')


# === Choix du modele ===
# Modele retenu : Random Forest (foret aleatoire).
# Comparaison (F1-macro, validation croisee) : Random Forest (0.835) > KNN (0.768)
# > Regression logistique (0.636). Le lien entre les caracteristiques et la puissance
# n'est pas lineaire, et la foret capture bien les interactions entre variables.
# Principe : un grand nombre d'arbres de decision, chacun entraine sur un tirage
# aleatoire des lignes et des variables ; la prediction finale est le vote majoritaire.


# === Variables utilisees ===
bool_features = ['prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs',
                 'prise_type_chademo', 'prise_type_autre', 'gratuit', 'station_deux_roues']


# === Chargement du modele deja entraine (pretraitement inclus) ===
modele = joblib.load(CHEMIN_MODELE)


# === Graphique : importance des variables ===
import matplotlib.pyplot as plt

noms = modele.named_steps['preprocess'].get_feature_names_out()
importances = modele.named_steps['model'].feature_importances_
imp = pd.Series(importances, index=noms).sort_values()
imp.tail(15).plot.barh(figsize=(8, 6), title="Variables les plus importantes")
plt.tight_layout()
plt.savefig(os.path.join(DOSSIER, 'importances.png'), dpi=150)
plt.show()
plt.close()
print("Graphique enregistre : importances.png")


# === Script de prediction (charge le modele, ne reapprend pas) ===
def predire_puissance(borne):
    """Prend les caracteristiques d'une borne (dictionnaire) et renvoie sa classe de puissance."""
    X_new = pd.DataFrame([borne])
    for col in bool_features:
        X_new[col] = X_new[col].astype(str).str.lower().isin(['true', 'vrai']).astype(int)
    return modele.predict(X_new)[0]


# Exemple : une borne a Brest
exemple = {
    'nbre_pdc': 4,
    'consolidated_longitude': -4.4861,
    'consolidated_latitude': 48.3904,
    'prise_type_ef': 'false',
    'prise_type_2': 'true',
    'prise_type_combo_ccs': 'true',
    'prise_type_chademo': 'true',
    'prise_type_autre': 'false',
    'gratuit': 'false',
    'station_deux_roues': 'false',
    'implantation_station': 'Parking public',
    'condition_acces': 'Acces libre',
}
print("Classe de puissance predite :", predire_puissance(exemple))
