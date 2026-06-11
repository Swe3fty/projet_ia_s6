# -*- coding: utf-8 -*-
"""
Clustering des bornes de recharge
"""

import os
import pandas as pd
import numpy as np
import joblib

#Toutes les ressources sont chargees/enregistrees ici
DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_CSV = os.path.join(DOSSIER, 'exportIA.csv')
CHEMIN_MODELE = os.path.join(DOSSIER, 'kmeans_bornes.pkl')


# Donnees : positions des bornes
lat_col = 'lat'
lon_col = 'long'

df = pd.read_csv(CHEMIN_CSV, sep=None, engine='python')

# On garde latitude + longitude, en numerique
coords = df[[lat_col, lon_col]].apply(pd.to_numeric, errors='coerce').dropna()

# Filtre France metropolitaine
coords = coords[(coords[lat_col].between(41.0, 51.5)) & (coords[lon_col].between(-5.5, 9.8))]

# Une position par borne
coords = coords.drop_duplicates().reset_index(drop=True)

# Attention : on prend bien les DEUX colonnes (latitude, longitude)
X = coords[[lat_col, lon_col]].values


# === Choix du modele ===
# Modele retenu : K-Means.
# Sur la France metropolitaine, k = 5 donne a la fois la meilleure silhouette (~0.50)
# et le meilleur Davies-Bouldin (~0.68), et correspond au coude de la courbe d'inertie.
# Deux metriques sur trois (silhouette + Davies-Bouldin) designent donc k = 5 comme
# nombre optimal. Calinski-Harabasz continue de croitre avec k, mais sans palier net :
# il ne contredit pas ce choix.


# === Chargement du modele deja entraine ===
model = joblib.load(CHEMIN_MODELE)
best_k = model.n_clusters

# On applique le modele pour obtenir le cluster de chaque borne (predict, pas fit)
coords['cluster'] = model.predict(X)


# === Graphique des clusters (enregistre dans le dossier du script) ===
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 8))
plt.scatter(coords[lon_col], coords[lat_col], c=coords['cluster'], cmap='tab10', s=3)
plt.xlabel("longitude")
plt.ylabel("latitude")
plt.title(f"Clusters des bornes (k={best_k})")
plt.tight_layout()
plt.savefig(os.path.join(DOSSIER, 'clusters.png'), dpi=150)
plt.show()
print("Graphique enregistre : clusters.png")


# === Carte interactive (enregistree dans le dossier du script) ===
import folium
import matplotlib

m = folium.Map(location=[coords[lat_col].mean(), coords[lon_col].mean()], zoom_start=6)
palette = matplotlib.colormaps['tab10'].resampled(best_k)

for _, r in coords.iterrows():
    couleur = matplotlib.colors.to_hex(palette(int(r['cluster'])))
    folium.CircleMarker(
        location=[r[lat_col], r[lon_col]],
        radius=3,
        color=couleur,
        fill=True,
        fill_color=couleur,
        fill_opacity=0.7,
        popup=f"Cluster {int(r['cluster'])}"
    ).add_to(m)

m.save(os.path.join(DOSSIER, 'carte_clusters.html'))
print("Carte enregistree : carte_clusters.html")


# === Script de prediction ===
# Le modele a ete entraine dans l'ordre (latitude, longitude) : on respecte le meme ordre ici.
def predire_cluster(latitude, longitude):
    return int(model.predict(np.array([[latitude, longitude]]))[0])

	
# Exemple : une borne a Brest
print("Cluster :", predire_cluster(48.3904, -4.4861))
