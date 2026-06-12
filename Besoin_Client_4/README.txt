================================================================================
README — Besoin Client 4 : Prédiction de la classe de puissance d'une borne
================================================================================

DESCRIPTION
-----------
Ce dossier contient tout le nécessaire pour prédire la classe de puissance
d'une borne de recharge pour véhicules électriques (VE) à partir de ses
caractéristiques techniques et géographiques.

La puissance nominale étant continue (192 valeurs distinctes dans la base),
elle est regroupée en 4 classes correspondant aux types de recharge réels
du marché :

    Classe           | Puissance     | Type de recharge
    -----------------|---------------|----------------------------------------
    1_lente          | <= 7.4 kW     | recharge lente (prise domestique)
    2_acceleree      | 7.4 - 22 kW   | recharge accélérée (bornes urbaines)
    3_rapide         | 22 - 50 kW    | recharge rapide
    4_ultra_rapide   | > 50 kW       | recharge ultra-rapide DC (autoroutes)

Modèle retenu : Random Forest.
Comparaison (F1-macro, validation croisée) :
    Random Forest (0.839) > KNN (0.771) > Régression logistique (0.622)
Après optimisation par GridSearchCV : accuracy de 0.944 sur le jeu de test.


CONTENU DU DOSSIER
------------------
  prediction_puissance.ipynb   Notebook expérimental (exploration, comparaison
                               des modèles, GridSearchCV, évaluation)
  prediction_puissance.py      Script final de prédiction (ne relance PAS
                               l'entraînement)
  modele_puissance.zip         Modèle Random Forest + prétraitement, compressé
                               (à décompresser pour obtenir
                               modele_puissance.pkl)
  importances.png              Importance des variables (par impureté)
  importances_permutation.png  Importance des variables (par permutation)
  ExportIA.csv                 Base de données utilisée
  README.txt                   Ce fichier


PRÉREQUIS
---------
Python 3.8 ou supérieur.

Installation des dépendances :
    pip install pandas scikit-learn joblib matplotlib

⚠️  Le fichier modele_puissance.pkl doit être présent dans le même dossier
    que le script.
    Si le .pkl est absent, exécuter le notebook
    prediction_puissance.ipynb depuis le début pour le régénérer.

⚠️  Le fichier ExportIA.csv doit aussi être présent : il sert au calcul de
    l'importance par permutation.


COMMENT UTILISER LE SCRIPT FINAL
--------------------------------
Étape 1 : Décompressez modele_puissance.zip dans ce dossier
          (-> modele_puissance.pkl).

Étape 2 : Placez le fichier de données "ExportIA.csv" dans ce dossier.

Étape 3 : Ouvrez un terminal dans ce dossier et lancez :
          > python prediction_puissance.py

Le script charge le modèle déjà entraîné (prétraitement inclus dans le
pipeline), génère les deux graphiques d'importance des variables, puis
affiche un exemple de prédiction sur une borne prédéfinie (Brest).


PRÉDICTION SUR UNE NOUVELLE BORNE
---------------------------------
Le script expose une fonction de prédiction :

    predire_puissance(borne)

où `borne` est un dictionnaire avec les caractéristiques de la borne.

Exemple :
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
    predire_puissance(exemple)   ->   '4_ultra_rapide'


VARIABLES ACCEPTÉES
-------------------
Champ                   | Type          | Description
------------------------|---------------|-------------------------------------
nbre_pdc                | entier        | Nombre de points de charge
consolidated_longitude  | flottant      | Longitude GPS
consolidated_latitude   | flottant      | Latitude GPS
prise_type_ef           | booléen       | Prise EF (prise domestique)
prise_type_2            | booléen       | Prise Type 2 (standard européen)
prise_type_combo_ccs    | booléen       | Prise Combo CCS (charge rapide DC)
prise_type_chademo      | booléen       | Prise CHAdeMO (charge rapide DC)
prise_type_autre        | booléen       | Autre type de prise
gratuit                 | booléen       | Recharge gratuite
station_deux_roues      | booléen       | Adaptée aux 2-roues électriques
implantation_station    | texte         | Ex : "Parking public", "Voirie"...
condition_acces         | texte         | Ex : "Acces libre", "Accès réservé"...

Les booléens acceptent : 'true'/'false' (ou 'vrai'), la conversion en 0/1
est faite par le script, à l'identique de l'entraînement.


REMARQUES
---------
- Le script ne relance JAMAIS l'entraînement. Il charge uniquement le
  pipeline sauvegardé (prétraitement + modèle) et applique predict().
- Pour ré-entraîner ou modifier le modèle, utiliser le notebook
  prediction_puissance.ipynb.
- Le modèle est sauvegardé via joblib. Assurez-vous d'utiliser une version
  de scikit-learn compatible (>= 1.0).
- La classe la plus difficile à prédire est 3_rapide (tranche étroite
  22-50 kW) : les confusions se font surtout entre classes voisines, ce qui
  est attendu pour des bornes proches d'une frontière entre deux catégories.

================================================================================
