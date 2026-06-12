================================================================================
README — Besoin Client 2 : Clustering géographique des bornes de recharge
================================================================================

DESCRIPTION
-----------
Ce dossier correspond au volet APPRENTISSAGE NON SUPERVISÉ du projet.
Objectif : regrouper automatiquement les bornes de recharge selon leur
position géographique (latitude / longitude), sans étiquette préexistante,
à l'aide de l'algorithme K-Means.

Le nombre de clusters retenu est k = 5. Ce choix est justifié par la
convergence de plusieurs métriques :
    - Silhouette        : meilleure valeur (~0.50) atteinte pour k = 5
    - Davies-Bouldin    : meilleure valeur (~0.68) atteinte pour k = 5
    - Méthode du coude  : le coude de la courbe d'inertie se situe à k = 5
    - Calinski-Harabasz : croît avec k sans palier net, ne contredit pas k = 5


CONTENU DU DOSSIER
------------------
  besoin_client2.ipynb     Notebook expérimental (exploration, recherche du k
                           optimal, métriques, entraînement, visualisation)
  besoin_client2.py        Script final : charge le modèle déjà entraîné
                           (ne relance PAS le clustering)
  kmeans_bornes.pkl        Modèle K-Means entraîné (généré par le notebook)
  exportIA.csv             Base de données brute (à placer ici manuellement)
  README.txt               Ce fichier


PRÉREQUIS
---------
Python 3.8 ou supérieur.

Installation des dépendances :
    pip install pandas numpy scikit-learn joblib matplotlib folium

⚠️  Le fichier kmeans_bornes.pkl doit être présent dans le même dossier que
    le script. Il est généré lors de l'exécution complète du notebook.
    S'il est absent, exécuter d'abord le notebook besoin_client2.ipynb
    depuis le début.


PRÉPARATION DES DONNÉES (effectuée par le script)
-------------------------------------------------
- Seules la latitude et la longitude sont conservées, en numérique.
- Filtrage de la France métropolitaine (Corse incluse) : sans ce filtre,
  les bornes des DOM-TOM, très éloignées, formeraient des clusters
  triviaux qui fausseraient le résultat.
- Déduplication : le fichier contient une ligne par point de charge, donc
  une même station revient plusieurs fois aux mêmes coordonnées.


COMMENT UTILISER LE SCRIPT FINAL
--------------------------------
Étape 1 : Placez le fichier de données "exportIA.csv" dans le même dossier
          que "besoin_client2.py".

Étape 2 : Ouvrez un terminal dans ce dossier.

Étape 3 : Lancez l'exécution du script :
          > python besoin_client2.py


RÉSULTATS GÉNÉRÉS
-----------------
  clusters.png           Nuage de points (longitude / latitude) coloré par
                         cluster.
  carte_clusters.html    Carte interactive Folium : chaque borne est affichée
                         avec une couleur selon son cluster. Double-cliquez
                         sur le fichier pour l'ouvrir dans un navigateur.


PRÉDICTION DU CLUSTER D'UNE NOUVELLE BORNE
------------------------------------------
Le script expose une fonction de prédiction qui charge le modèle sauvegardé
et renvoie le cluster d'une borne à partir de sa position :

    predire_cluster(latitude, longitude)

Exemple (borne à Brest) :
    predire_cluster(48.3904, -4.4861)

⚠️  Le modèle a été entraîné dans l'ordre (latitude, longitude) : il faut
    impérativement respecter le même ordre lors de la prédiction.


REMARQUES
---------
- Le script ne relance JAMAIS le clustering. Il charge uniquement le modèle
  sauvegardé (kmeans_bornes.pkl) et applique predict() sur les données.
- Pour ré-entraîner ou modifier le modèle (changer k, les métriques...),
  utiliser le notebook besoin_client2.ipynb.
- Le modèle est sauvegardé via joblib. Assurez-vous d'utiliser une version
  de scikit-learn compatible (>= 1.0).

================================================================================
