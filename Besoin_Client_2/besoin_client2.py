# -*- coding: utf-8 -*-
"""
Clustering des bornes de recharge
"""

<<<<<<< HEAD
import os
import pandas as pd
import numpy as np
import joblib

#Toutes les ressources sont chargees/enregistrees ici
DOSSIER = os.path.dirname(os.path.abspath(__file__))
CHEMIN_CSV = os.path.join(DOSSIER, 'exportIA.csv')
CHEMIN_MODELE = os.path.join(DOSSIER, 'kmeans_bornes.pkl')
=======
# =====================================================================
# 1. Chargement des donnees
# =====================================================================
import pandas as pd
import numpy as np
import os


# 1. Vérification du fichier de données
chemin_csv = "ExportIA.csv"
if not os.path.exists(chemin_csv):
        print(f"\n[ERREUR] Le fichier '{chemin_csv}' est introuvable dans le dossier actuel.")
        print("Veuillez placer le fichier CSV dans le même dossier que ce script avant de le relancer.")
        

df = pd.read_csv(chemin_csv, sep=None, engine='python')
print(df.head())
>>>>>>> 60150a02ee34db0e4aae8e909c9da7795ff60589


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
<<<<<<< HEAD
plt.savefig(os.path.join(DOSSIER, 'clusters.png'), dpi=150)
plt.show()
print("Graphique enregistre : clusters.png")


# === Carte interactive (enregistree dans le dossier du script) ===
=======
plt.savefig("graphes_metriques_k.png")
plt.close()


# ---------------------------------------------------------------------
# Conclusion sur le nombre de clusters
# ---------------------------------------------------------------------
# Sur la France metropolitaine, k = 5 donne a la fois la meilleure silhouette
# (~0.50) et le meilleur Davies-Bouldin (~0.68), et correspond au coude de la
# courbe d'inertie.
# Deux metriques sur trois (silhouette + Davies-Bouldin) designent donc k = 5
# comme nombre optimal. Calinski-Harabasz continue de croitre avec k, mais sans
# palier net : il ne contredit pas ce choix.
# ---------------------------------------------------------------------

# On arrondit la silhouette pour que les quasi-egalites deviennent de vraies egalites
sil = metrics['silhouette'].round(3)

# Candidats = tous les k qui atteignent la silhouette max (arrondie)
candidats = sil.index[sil == sil.max()].tolist()
print("k candidats (silhouette maximale) :", candidats)

# On departage avec Davies-Bouldin (le plus bas = meilleur)
best_k = int(metrics.loc[candidats, 'davies_bouldin'].idxmin())
print(f"\nk optimal = {best_k}")


# =====================================================================
# 4. Modele final et sauvegarde
# ---------------------------------------------------------------------
# On entraine K-Means avec le k optimal, puis on enregistre le modele pour
# pouvoir le reutiliser sans le re-entrainer.
# =====================================================================
import joblib

final_model = KMeans(n_clusters=best_k, random_state=42, n_init=10)
coords['cluster'] = final_model.fit_predict(X)

joblib.dump(final_model, 'kmeans_bornes.pkl')
print("Modele sauvegarde.")


# =====================================================================
# 5. Visualisation sur une carte
# ---------------------------------------------------------------------
# Chaque borne est affichee sur une carte avec une couleur differente selon
# son cluster.
# =====================================================================
>>>>>>> 60150a02ee34db0e4aae8e909c9da7795ff60589
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

<<<<<<< HEAD
m.save(os.path.join(DOSSIER, 'carte_clusters.html'))
print("Carte enregistree : carte_clusters.html")


# === Script de prediction ===
# Le modele a ete entraine dans l'ordre (latitude, longitude) : on respecte le meme ordre ici.
=======
# En script .py (hors notebook), on sauvegarde la carte en HTML pour l'ouvrir
m.save('carte_clusters.html')
print("Carte sauvegardee : carte_clusters.html")


# =====================================================================
# 6. Script de prediction
# ---------------------------------------------------------------------
# Le script charge le modele deja enregistre (il ne relance pas le clustering)
# et renvoie le cluster d'une borne a partir de sa position.
# Le modele a ete entraine dans l'ordre (latitude, longitude) : on respecte le
# meme ordre ici.
# =====================================================================


# Chargement du modele sauvegarde (une seule fois)
model = joblib.load('kmeans_bornes.pkl')

>>>>>>> 60150a02ee34db0e4aae8e909c9da7795ff60589
def predire_cluster(latitude, longitude):
    return int(model.predict(np.array([[latitude, longitude]]))[0])

	
# Exemple : une borne a Brest
print("Cluster :", predire_cluster(48.3904, -4.4861))
