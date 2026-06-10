import argparse
import json
import sys
import os
import pandas as pd
import joblib

# ─────────────────────────────────────────────
# Chemins vers les modèles sauvegardés
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, 'best_model_rf.pkl')
PREPROC_PATH = os.path.join(BASE_DIR, 'preprocessor.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'label_encoder_target.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'feature_names.pkl')


def load_models():
    """Charge les modèles et artefacts de prétraitement depuis le disque."""
    for path, name in [
        (MODEL_PATH, 'best_model_rf.pkl'),
        (PREPROC_PATH, 'preprocessor.pkl'),
        (ENCODER_PATH, 'label_encoder_target.pkl'),
        (FEATURES_PATH, 'feature_names.pkl'),
    ]:
        if not os.path.exists(path):
            sys.exit(f"[ERREUR] Fichier manquant : {name}\n"
                     f"         Chemin attendu : {path}\n"
                     f"         Veuillez d'abord exécuter le notebook.")

    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROC_PATH)
    le_target = joblib.load(ENCODER_PATH)
    feature_names = joblib.load(FEATURES_PATH)

    return model, preprocessor, le_target, feature_names


def predict(borne_data: dict) -> dict:
    """
    Prédit le type d'implantation d'une borne.

    Paramètres
    ----------
    borne_data : dict
        Dictionnaire contenant les caractéristiques de la borne.
        Les clés manquantes seront complétées par des valeurs par défaut.

    Retourne
    --------
    dict avec :
        - 'implantation_predite' : str  — classe prédite
        - 'probabilites'         : dict — probabilité de chaque classe
    """
    model, preprocessor, le_target, feature_names = load_models()

    # Valeurs par défaut pour les champs non renseignés
    defaults = {
        'nbre_pdc': 1,
        'puissance_nominale': 22.0,
        'long': 2.3522,
        'lat': 48.8566,
        'prise_type_ef': 0,
        'prise_type_2': 1,
        'prise_type_combo_ccs': 0,
        'prise_type_chademo': 0,
        'prise_type_autre': 0,
        'paiement_acte': 0,
        'paiement_cb': 0,
        'reservation': 0,
        'station_deux_roues': 0,
        'condition_acces': 'inconnu',
        'accessibilite_pmr': 'inconnu',
    }

    # Fusion des données fournies sur les valeurs par défaut
    input_data = {**defaults, **borne_data}

    # Normalisation des booléens (accepte True/False/1/0/'True'/'False')
    bool_cols = [
        'prise_type_ef', 'prise_type_2', 'prise_type_combo_ccs',
        'prise_type_chademo', 'prise_type_autre', 'paiement_acte',
        'paiement_cb', 'reservation', 'station_deux_roues'
    ]
    bool_map = {True: 1, False: 0, 'True': 1, 'False': 0,
                'true': 1, 'false': 0, 1: 1, 0: 0}
    for col in bool_cols:
        input_data[col] = bool_map.get(input_data[col], 0)

    # Normalisation des catégorielles
    for col in ['condition_acces', 'accessibilite_pmr']:
        input_data[col] = str(input_data[col]).strip().lower()

    # Construction du DataFrame dans le bon ordre de colonnes
    df_input = pd.DataFrame([input_data])[feature_names]

    # Prétraitement (même pipeline que l'entraînement)
    X_proc = preprocessor.transform(df_input)

    # Prédiction
    y_pred_encoded = model.predict(X_proc)[0]
    implantation = le_target.inverse_transform([y_pred_encoded])[0]

    # Probabilités par classe
    probas = model.predict_proba(X_proc)[0]
    proba_dict = {
        cls: round(float(p), 4)
        for cls, p in zip(le_target.classes_, probas)
    }
    proba_sorted = dict(sorted(proba_dict.items(), key=lambda x: -x[1]))

    return {
        'implantation_predite': implantation,
        'probabilites': proba_sorted
    }


# ─────────────────────────────────────────────
# Interface en ligne de commande
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='Prédit le type d\'implantation d\'une borne de recharge VE.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--json', type=str, metavar='JSON_STRING',
        help='Caractéristiques de la borne sous forme de chaîne JSON'
    )
    group.add_argument(
        '--file', type=str, metavar='FILE',
        help='Chemin vers un fichier JSON contenant les caractéristiques'
    )
    args = parser.parse_args()

    # ── Lecture des données d'entrée ──
    if args.json:
        try:
            borne_data = json.loads(args.json)
        except json.JSONDecodeError as e:
            sys.exit(f"[ERREUR] JSON invalide : {e}")

    elif args.file:
        if not os.path.exists(args.file):
            sys.exit(f"[ERREUR] Fichier introuvable : {args.file}")
        with open(args.file, 'r', encoding='utf-8') as f:
            try:
                borne_data = json.load(f)
            except json.JSONDecodeError as e:
                sys.exit(f"[ERREUR] JSON invalide dans le fichier : {e}")

    else:
        # Mode interactif : exemple de borne par défaut
        print("Aucun argument fourni — exécution avec une borne d'exemple.\n")
        borne_data = {
            "nbre_pdc": 2,
            "puissance_nominale": 50.0,
            "long": 2.3522,
            "lat": 48.8566,
            "prise_type_ef": False,
            "prise_type_2": True,
            "prise_type_combo_ccs": True,
            "prise_type_chademo": False,
            "prise_type_autre": False,
            "paiement_acte": True,
            "paiement_cb": True,
            "reservation": False,
            "station_deux_roues": False,
            "condition_acces": "Accès libre",
            "accessibilite_pmr": "Accessible"
        }
        print("Données de la borne :")
        print(json.dumps(borne_data, ensure_ascii=False, indent=2))
        print()

    # ── Prédiction ──
    result = predict(borne_data)

    # ── Affichage des résultats ──
    print("=" * 50)
    print(f"  Implantation prédite : {result['implantation_predite']}")
    print("=" * 50)
    print("\nProbabilités par classe :")
    for cls, proba in result['probabilites'].items():
        bar = '█' * int(proba * 30)
        print(f"  {cls:<45} {proba:.2%}  {bar}")
    print()


if __name__ == '__main__':
    main()
