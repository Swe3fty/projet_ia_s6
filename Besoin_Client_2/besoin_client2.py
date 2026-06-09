# -*- coding: utf-8 -*-
"""
Apprentissage non-supervise - Clustering des bornes de recharge

Objectif : regrouper les bornes de recharge selon leur position geographique
(latitude / longitude).

Etapes : chargement -> choix des variables -> recherche du nombre optimal de
clusters -> mesure de la qualite (3 metriques) -> modele final -> carte ->
script de prediction.
"""

# =====================================================================
# 1. Chargement des donnees
# =====================================================================
from google.colab import drive
drive.mount("/content/drive/")

import pandas as pd
import numpy as np

df = pd.read_csv('/content/drive/MyDrive/Projet_IA/ExportIA.csv', sep=None, engine='python')
print(df.head())


# =====================================================================
# 2. Choix des variables
# ---------------------------------------------------------------------
# On veut regrouper les bornes par position, donc on garde uniquement la
# latitude et la longitude.
# Deux nettoyages importants :
#  - On filtre la France metropolitaine (Corse incluse). Sans ca, les bornes
#    des DOM-TOM (Guadeloupe, Reunion...), tres eloignees, forment des groupes
#    triviaux qui faussent le clustering.
#  - On deduplique : le fichier a une ligne par point de charge, donc une meme
#    station revient plusieurs fois aux memes coordonnees.
# =====================================================================
lat_col = 'consolidated_latitude'
lon_col = 'consolidated_longitude'

# On garde latitude + longitude, en numerique
coords = df[[lat_col, lon_col]].apply(pd.to_numeric, errors='coerce').dropna()

# Filtre France metropolitaine (Corse incluse)
coords = coords[(coords[lat_col].between(41.0, 51.5)) & (coords[lon_col].between(-5.5, 9.8))]

# Une position par borne
coords = coords.drop_duplicates().reset_index(drop=True)

# Attention : on prend bien les DEUX colonnes (latitude, longitude)
X = coords[[lat_col, lon_col]].values

print(f"Nombre de positions de bornes : {len(X)}")
print(coords.head())


# =====================================================================
# 3. Recherche du nombre optimal de clusters
# ---------------------------------------------------------------------
# K-Means a besoin qu'on lui donne le nombre de groupes k. On teste plusieurs
# valeurs et on mesure la qualite avec 3 metriques :
#  - Silhouette         : plus c'est proche de 1, mieux c'est.
#  - Calinski-Harabasz  : plus c'est grand, mieux c'est.
#  - Davies-Bouldin     : plus c'est proche de 0, mieux c'est.
# On ajoute aussi l'inertie pour la methode du coude.
# =====================================================================
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import matplotlib.pyplot as plt

# La silhouette est lente sur beaucoup de points : on la calcule sur un echantillon
rng = np.random.default_rng(42)
sample = rng.choice(len(X), size=min(5000, len(X)), replace=False)

results = []
for k in range(2, 16):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    results.append({
        'k': k,
        'inertie': km.inertia_,
        'silhouette': silhouette_score(X[sample], labels[sample]),
        'calinski_harabasz': calinski_harabasz_score(X, labels),
        'davies_bouldin': davies_bouldin_score(X, labels),
    })

metrics = pd.DataFrame(results).set_index('k')
print(metrics.round(3))


# --- Graphes des metriques en fonction de k ---
fig, ax = plt.subplots(2, 2, figsize=(13, 9))
ax[0, 0].plot(metrics.index, metrics['inertie'], 'o-')
ax[0, 0].set_title("Methode du coude (inertie)")
ax[0, 1].plot(metrics.index, metrics['silhouette'], 'o-', c='green')
ax[0, 1].set_title("Silhouette (plus haut = mieux)")
ax[1, 0].plot(metrics.index, metrics['calinski_harabasz'], 'o-', c='orange')
ax[1, 0].set_title("Calinski-Harabasz (plus haut = mieux)")
ax[1, 1].plot(metrics.index, metrics['davies_bouldin'], 'o-', c='red')
ax[1, 1].set_title("Davies-Bouldin (plus bas = mieux)")
for a in ax.flat:
    a.set_xlabel("k")
    a.grid(alpha=0.3)
plt.tight_layout()
plt.show()


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

joblib.dump(final_model, '/content/drive/MyDrive/Projet_IA/kmeans_bornes.pkl')
print("Modele sauvegarde.")


# =====================================================================
# 5. Visualisation sur une carte
# ---------------------------------------------------------------------
# Chaque borne est affichee sur une carte avec une couleur differente selon
# son cluster.
# =====================================================================
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

# En script .py (hors notebook), on sauvegarde la carte en HTML pour l'ouvrir
m.save('/content/drive/MyDrive/Projet_IA/carte_clusters.html')
print("Carte sauvegardee : carte_clusters.html")


# =====================================================================
# 6. Script de prediction
# ---------------------------------------------------------------------
# Le script charge le modele deja enregistre (il ne relance pas le clustering)
# et renvoie le cluster d'une borne a partir de sa position.
# Le modele a ete entraine dans l'ordre (latitude, longitude) : on respecte le
# meme ordre ici.
# =====================================================================
import joblib
import numpy as np

# Chargement du modele sauvegarde (une seule fois)
model = joblib.load('/content/drive/MyDrive/Projet_IA/kmeans_bornes.pkl')

def predire_cluster(latitude, longitude):
    return int(model.predict(np.array([[latitude, longitude]]))[0])

# Exemple : une borne a Paris
print("Cluster :", predire_cluster(48.8566, 2.3522))
