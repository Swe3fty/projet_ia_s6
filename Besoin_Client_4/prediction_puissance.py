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
plt.close()
print("Graphique enregistre : importances.png")


# === Graphique 2 : importance par PERMUTATION ===
# L'importance par impurete ci-dessus favorise les variables continues (lat/long) et
# dilue les categorielles eclatees par le one-hot. La permutation mesure la vraie utilite :
# on melange les valeurs d'une variable et on regarde de combien le score (F1-macro) chute.
from sklearn.inspection import permutation_importance

CHEMIN_CSV = os.path.join(DOSSIER, 'ExportIA.csv')
df = pd.read_csv(CHEMIN_CSV, sep=None, engine='python')
df = df[(df['puissance_nominale'] > 0) & (df['puissance_nominale'] <= 400)].copy()

def classe_puissance(p):
    if p <= 7.4:
        return '1_lente'
    elif p <= 22:
        return '2_acceleree'
    elif p <= 50:
        return '3_rapide'
    else:
        return '4_ultra_rapide'

df['classe_puissance'] = df['puissance_nominale'].apply(classe_puissance)
for col in bool_features:
    df[col] = df[col].astype(str).str.lower().isin(['true', 'vrai']).astype(int)

num_features = ['nbre_pdc', 'consolidated_longitude', 'consolidated_latitude']
cat_features = ['implantation_station', 'condition_acces']
features = num_features + bool_features + cat_features
X = df[features]
y = df['classe_puissance']

# On evalue sur un echantillon (la permutation est couteuse)
X_ech = X.sample(min(8000, len(X)), random_state=0)
y_ech = y.loc[X_ech.index]
r = permutation_importance(modele, X_ech, y_ech, n_repeats=5, random_state=42,
                           scoring='f1_macro', n_jobs=-1)
imp_perm = pd.Series(r.importances_mean, index=features).sort_values()
print("\nImportance par permutation :")
print(imp_perm.sort_values(ascending=False).round(4))

imp_perm.plot.barh(figsize=(8, 6), title="Importance par permutation (chute de F1-macro)")
plt.tight_layout()
plt.savefig(os.path.join(DOSSIER, 'importances_permutation.png'), dpi=150)
plt.close()
print("Graphique enregistre : importances_permutation.png")


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
