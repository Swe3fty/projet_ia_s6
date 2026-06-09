========================================================================
                          DOSSIER : BESOIN CLIENT 1
========================================================================

Ce dossier correspond au livrable de la phase "Besoin Client 1".
Objectif : L'identification et la localisation des points de charges 
avec leur type et la détection d'éventuelles anomalies.

------------------------------------------------------------------------
1. CONTENU DU DOSSIER
------------------------------------------------------------------------
• export_ia.csv          : La base de données brute (à placer ici manuellement).
• Besoin_Client_1.ipynb  : Le Notebook Jupyter interactif contenant les 
                           recherches, les commentaires et les tests.
• script_final.py        : Le script Python automatisant le nettoyage,
                           l'analyse et la création des cartes.
• Readme.txt             : Ce fichier d'instructions.

------------------------------------------------------------------------
2. PRÉREQUIS ET INSTALLATION
------------------------------------------------------------------------
Assurez-vous d'avoir Python 3 installé sur votre machine. 
Vous aurez besoin des librairies suivantes pour exécuter le script :
    -> pandas
    -> matplotlib
    -> numpy
    -> folium

Pour les installer, ouvrez un terminal et exécutez la commande :
> pip install pandas matplotlib numpy folium

------------------------------------------------------------------------
3. COMMENT UTILISER LE SCRIPT FINAL
------------------------------------------------------------------------
Étape 1 : Placez impérativement votre fichier de données nommé "export_ia.csv" 
          dans le même dossier que "script_final.py".

Étape 2 : Ouvrez un terminal (ou invite de commande) dans ce dossier.

Étape 3 : Lancez l'exécution du script en tapant :
> python script_final.py

------------------------------------------------------------------------
4. RÉSULTATS GÉNÉRÉS
------------------------------------------------------------------------
Le script va traiter les données automatiquement (filtrage des colonnes, 
nettoyage des caractères spéciaux, agrégation spatiale par station) pour 
réduire le temps d'exécution. 

Une fois terminé, il créera 5 nouveaux fichiers dans votre dossier :

Images (Analyses statistiques) :
 - repartition_puissances.png : Histogramme des puissances nominales.
 - repartition_prises.png     : Graphique en barres des types de prises.

Cartes Interactives :
 - map_implantation.html      : Carte des bornes classées par implantation.
 - map_puissance.html         : Carte des bornes classées par puissance.
 - map_chaleur.html           : HeatMap représentant la densité spatiale.

Pour visualiser une carte, double-cliquez simplement sur le fichier .html 
généré afin de l'ouvrir dans votre navigateur web classique.
========================================================================
