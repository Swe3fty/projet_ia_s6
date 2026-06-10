================================================================================
README — Besoin Client 3 : Prédiction du Type d'Implantation d'une Borne VE
================================================================================

DESCRIPTION
-----------
Ce dossier contient tout le nécessaire pour prédire le type d'implantation
d'une borne de recharge pour véhicules électriques (VE) à partir de ses
caractéristiques techniques et géographiques.

La variable cible est : implantation_station
Classes possibles :
    - voirie
    - parking privé à usage public
    - parking public
    - station dédiée recharge rapide
    - parking privé réservé clientèle


CONTENU DU DOSSIER
------------------
  Besoin_Client_3.ipynb             Notebook expérimental (exploration, entraînement, évaluation)
  Besoin_Client_3.py		    Script final de prédiction (ne relance PAS l'entraînement)
  best_model_rf.pkl                 Modèle Random Forest optimisé (généré par le notebook)
  preprocessor.pkl                  Pipeline de prétraitement (généré par le notebook)
  label_encoder_target.pkl          Encodeur de la variable cible (généré par le notebook)
  feature_names.pkl                 Ordre des features (généré par le notebook)
  exportIA.csv                      Base de données utilisée
  README.txt                        Ce fichier


PRÉREQUIS
---------
Python 3.8 ou supérieur.

Installation des dépendances :
    pip install pandas scikit-learn joblib

⚠️  Les fichiers .pkl doivent être présents dans le même dossier que le
    script. Ils sont générés lors de l'exécution complète du notebook.
    Si les fichiers .pkl sont absents, exécuter d'abord le notebook
    Besoin_Client_3.ipynb depuis le début.


UTILISATION DU SCRIPT
---------------------

1) SANS ARGUMENT (mode démonstration avec une borne d'exemple)
   -----------------------------------------------------------------
   python predict_implantation.py

   Affiche une prédiction sur une borne prédéfinie.


2) AVEC UNE CHAÎNE JSON EN ARGUMENT
   -----------------------------------------------------------------
   python predict_implantation.py --json '{"nbre_pdc": 4, "puissance_nominale": 150, "prise_type_combo_ccs": true, "condition_acces": "Accès libre"}'

   Les champs non fournis prennent des valeurs par défaut raisonnables.


3) AVEC UN FICHIER JSON
   -----------------------------------------------------------------
   python predict_implantation.py --file ma_borne.json

   Le fichier doit contenir un objet JSON avec les champs souhaités.


EXEMPLE DE FICHIER JSON (ma_borne.json)
---------------------------------------
{
    "nbre_pdc":             2,
    "puissance_nominale":   50.0,
    "long":                 2.3522,
    "lat":                  48.8566,
    "prise_type_ef":        false,
    "prise_type_2":         true,
    "prise_type_combo_ccs": true,
    "prise_type_chademo":   false,
    "prise_type_autre":     false,
    "paiement_acte":        true,
    "paiement_cb":          true,
    "reservation":          false,
    "station_deux_roues":   false,
    "condition_acces":      "Accès libre",
    "accessibilite_pmr":    "Accessible"
}

Commande :
    python predict_implantation.py --file ma_borne.json


VARIABLES ACCEPTÉES
-------------------
Champ                   | Type          | Description
------------------------|---------------|-------------------------------------------
nbre_pdc                | entier        | Nombre de points de charge
puissance_nominale      | flottant (kW) | Puissance maximale disponible
long                    | flottant      | Longitude GPS
lat                     | flottant      | Latitude GPS
prise_type_ef           | booléen       | Prise EF (prise domestique)
prise_type_2            | booléen       | Prise Type 2 (standard européen)
prise_type_combo_ccs    | booléen       | Prise CCS (charge rapide)
prise_type_chademo      | booléen       | Prise CHAdeMO (charge rapide japonaise)
prise_type_autre        | booléen       | Autre type de prise
paiement_acte           | booléen       | Paiement sans abonnement possible
paiement_cb             | booléen       | Paiement par carte bancaire accepté
reservation             | booléen       | Réservation possible
station_deux_roues      | booléen       | Adaptée aux 2-roues électriques
condition_acces         | texte         | Ex : "Accès libre", "Accès réservé"...
accessibilite_pmr       | texte         | Ex : "Accessible", "Non accessible"...

Les booléens acceptent : true/false, True/False, 1/0.
Les champs omis sont remplacés par des valeurs par défaut.


EXEMPLE DE SORTIE
-----------------
Données de la borne :
{
  "nbre_pdc": 2,
  "puissance_nominale": 50.0,
  ...
}


REMARQUES
---------
- Le script ne relance JAMAIS l'entraînement. Il charge uniquement les modèles
  sauvegardés (.pkl) et applique la même pipeline de prétraitement.
- Pour réentraîner ou modifier le modèle, utiliser le notebook .ipynb.
- Les modèles sont sauvegardés au format .pkl via joblib. Assurez-vous
  d'utiliser une version scikit-learn compatible (>= 1.0).

================================================================================
