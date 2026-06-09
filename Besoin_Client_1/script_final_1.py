import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium
from folium.plugins import MarkerCluster, HeatMap
from folium import Element
import os

def main():
    print("=====================================================")
    print(" Lancement du traitement - Besoin Client 1")
    print("=====================================================")

    # 1. Vérification du fichier de données
    chemin_csv = "export_ia.csv"
    if not os.path.exists(chemin_csv):
        print(f"\n[ERREUR] Le fichier '{chemin_csv}' est introuvable dans le dossier actuel.")
        print("Veuillez placer le fichier CSV dans le même dossier que ce script avant de le relancer.")
        return

    # 2. Chargement et préparation des données
    print("\n-> 1/4 Chargement et nettoyage des données...")
    colonnes_utiles = [
        'nom_station', 'implantation_station', 'puissance_nominale',
        'nbre_pdc', 'lat', 'long', 'prise_type_ef', 'prise_type_2',
        'prise_type_combo_ccs', 'prise_type_chademo', 'prise_type_autre'
    ]
    
    # Chargement uniquement des colonnes utiles pour optimiser la mémoire
    data = pd.read_csv(chemin_csv, usecols=lambda c: c in colonnes_utiles, low_memory=False)

    # Nettoyage des types et valeurs aberrantes
    data['nom_station'] = data['nom_station'].astype(str)
    data['implantation_station'] = data['implantation_station'].astype(str)
    
    colonnes_prises = ['prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs', 'prise_type_chademo', 'prise_type_autre']
    for col in colonnes_prises:
        data[col] = data[col].astype(bool)

    data_propre = data.dropna(subset=['lat', 'long', 'implantation_station', 'puissance_nominale'])

    # 3. Visualisation des données (Sauvegarde en PNG au lieu d'afficher pour automatiser le script)
    print("-> 2/4 Génération des graphiques statistiques...")
    
    plt.figure(figsize=(10, 6))
    data_propre['puissance_nominale'].plot(kind='hist', bins=20, color='skyblue', edgecolor='black')
    plt.title("Répartition des Puissances Nominales")
    plt.xlabel("Puissance Nominale (kW)")
    plt.ylabel("Fréquence")
    plt.grid(axis='y', alpha=0.7)
    plt.savefig("repartition_puissances.png", bbox_inches='tight')
    plt.close()

    total_par_prise = data_propre[colonnes_prises].sum()
    plt.figure(figsize=(10, 6))
    total_par_prise.plot(kind='bar', color='coral', edgecolor='black')
    plt.title("Équipement des stations par type de prise")
    plt.ylabel("Nombre de prises disponibles")
    plt.xticks(rotation=45)
    plt.savefig("repartition_prises.png", bbox_inches='tight')
    plt.close()

    # 4. Agrégation spatiale pour les cartes
    print("-> 3/4 Agrégation spatiale des coordonnées GPS...")
    # On groupe par localisation pour éviter d'avoir plusieurs points au même endroit
    stations = data_propre.groupby(['lat', 'long']).agg(
        implantation=('implantation_station', 'first'),
        nom=('nom_station', 'first'),
        puissance_max=('puissance_nominale', 'max'),
        nb_pdc=('puissance_nominale', 'count')
    ).reset_index()

    # Nettoyage drastique des caractères spéciaux pour éviter les crashs JavaScript dans Folium
    stations['nom'] = stations['nom'].astype(str).replace(r'[\'\"`\n\r]+', ' ', regex=True)
    stations['implantation'] = stations['implantation'].astype(str).replace(r'[\'\"`\n\r]+', ' ', regex=True)
    stations = stations.fillna("Inconnu")

    centre_lat = stations['lat'].mean()
    centre_long = stations['long'].mean()

    # 5. Création des cartes
    print("-> 4/4 Génération des cartes interactives (HTML)...")
    
    # ---------------------------------------------------------
    # CARTE 1 : TYPES D'IMPLANTATION
    # ---------------------------------------------------------
    map_implantation = folium.Map(location=[centre_lat, centre_long], zoom_start=6)
    types_uniques = stations['implantation'].unique()
    couleurs_impl = ['green', 'blue', 'purple', 'orange', 'red', 'darkblue', 'cadetblue']
    clusters_impl = {}

    for index, type_impl in enumerate(types_uniques):
        calque = folium.FeatureGroup(name=str(type_impl))
        cluster = MarkerCluster().add_to(calque)
        calque.add_to(map_implantation)
        couleur = couleurs_impl[index % len(couleurs_impl)]
        clusters_impl[type_impl] = {'cluster': cluster, 'couleur': couleur}

    for lat, lon, station, puissance, nb_pdc, implantation in zip(stations['lat'], stations['long'], stations['nom'], stations['puissance_max'], stations['nb_pdc'], stations['implantation']):
        texte_bulle = f"📍 {station} | {implantation} | ⚡ Max: {puissance} kW | 🔋 {nb_pdc} prise(s)"
        folium.Marker(
            location=[lat, lon],
            tooltip=texte_bulle,
            icon=folium.Icon(color=clusters_impl[implantation]['couleur'])
        ).add_to(clusters_impl[implantation]['cluster'])

    # Légende Implantation
    lignes_html_impl = ""
    for type_impl, infos in clusters_impl.items():
        lignes_html_impl += f'<div style="display: flex; align-items: center; margin-bottom: 8px;"><span style="background-color: {infos["couleur"]}; width: 15px; height: 15px; border-radius: 50%; display: inline-block; margin-right: 10px; border: 1px solid #555;"></span><span>{type_impl}</span></div>'

    legende_impl = f'<div style="position: fixed; bottom: 30px; left: 30px; width: 250px; z-index: 9999; background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 8px; border: 2px solid #ccc; box-shadow: 3px 3px 10px rgba(0,0,0,0.2); font-family: Arial, sans-serif; font-size: 14px; color: #333;"><h4 style="margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Types d\'implantation</h4>{lignes_html_impl}</div>'
    map_implantation.get_root().html.add_child(Element(legende_impl))
    folium.LayerControl().add_to(map_implantation)
    map_implantation.save("map_implantation.html")

    # ---------------------------------------------------------
    # CARTE 2 : PUISSANCE NOMINALE
    # ---------------------------------------------------------
    limites_puissance = [0, 24, 150, np.inf]
    nom_labels = ["Normale (0-24kW)", "Rapide (25-150kW)", "Extrêmement Rapide (>150kW)"]
    stations["puissance_cat"] = pd.cut(stations["puissance_max"], bins=limites_puissance, labels=nom_labels)
    stations_pui = stations.dropna(subset=['puissance_cat'])

    map_puissance = folium.Map(location=[centre_lat, centre_long], zoom_start=6)
    couleurs_pui = ['lightgreen', 'orange', 'red']
    clusters_pui = {}

    for index, cat_label in enumerate(nom_labels):
        calque = folium.FeatureGroup(name=str(cat_label))
        cluster = MarkerCluster().add_to(calque)
        calque.add_to(map_puissance)
        clusters_pui[cat_label] = {'cluster': cluster, 'couleur': couleurs_pui[index]}

    for lat, lon, station, pui_chiffre, pui_texte, nb_pdc, implantation in zip(stations_pui['lat'], stations_pui['long'], stations_pui['nom'], stations_pui['puissance_max'], stations_pui['puissance_cat'], stations_pui['nb_pdc'], stations_pui['implantation']):
        texte_bulle = f"📍 {station} | {implantation} | ⚡ Max : {pui_chiffre} kW | 🔋 {nb_pdc} prise(s)"
        folium.Marker(
            location=[lat, lon],
            tooltip=texte_bulle,
            icon=folium.Icon(color=clusters_pui[pui_texte]['couleur'])
        ).add_to(clusters_pui[pui_texte]['cluster'])

    # Légende Puissance
    lignes_html_pui = ""
    for pui_label, infos in clusters_pui.items():
        lignes_html_pui += f'<div style="display: flex; align-items: center; margin-bottom: 8px;"><span style="background-color: {infos["couleur"]}; width: 15px; height: 15px; border-radius: 50%; display: inline-block; margin-right: 10px; border: 1px solid #555;"></span><span>{pui_label}</span></div>'

    legende_pui = f'<div style="position: fixed; bottom: 30px; left: 30px; width: 250px; z-index: 9999; background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 8px; border: 2px solid #ccc; box-shadow: 3px 3px 10px rgba(0,0,0,0.2); font-family: Arial, sans-serif; font-size: 14px; color: #333;"><h4 style="margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Puissance des stations</h4>{lignes_html_pui}</div>'
    map_puissance.get_root().html.add_child(Element(legende_pui))
    folium.LayerControl().add_to(map_puissance)
    map_puissance.save("map_puissance.html")

    # ---------------------------------------------------------
    # CARTE 3 : HEATMAP (CARTE DE CHALEUR)
    # ---------------------------------------------------------
    map_chaleur = folium.Map(location=[centre_lat, centre_long], zoom_start=6)
    donnees_chaleur = stations[['lat', 'long']].values.tolist()
    HeatMap(donnees_chaleur, radius=10, blur=10).add_to(map_chaleur)
    map_chaleur.save("map_chaleur.html")

    print("\n=====================================================")
    print(" SUCCÈS : Tous les fichiers ont été générés !")
    print("=====================================================")
    print("- repartition_puissances.png")
    print("- repartition_prises.png")
    print("- map_implantation.html")
    print("- map_puissance.html")
    print("- map_chaleur.html")

if __name__ == "__main__":
    main()
