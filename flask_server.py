from flask import Flask, request, jsonify
import os
import json
import re
# from flask_cors import CORS  # Décommente si besoin

app = Flask(__name__)
# CORS(app)

# ====== CONFIGURATION ======
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHEMIN_JSON = os.path.join(BASE_DIR, "produits.json")
DOSSIER_FICHES = os.path.join(BASE_DIR, "fiches")
PRODUITS_PAR_BATCH = 15

# ====== OUTILS ======
def clean_filename(nom):
    return re.sub(r'[^a-zA-Z0-9\-]', '-', nom.replace(" ", "-").lower())

def charger_produits():
    if not os.path.exists(CHEMIN_JSON):
        raise FileNotFoundError(f"❌ Le fichier JSON est introuvable : {CHEMIN_JSON}")
    with open(CHEMIN_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def get_flexible(data, *cles):
    for cle in cles:
        for k in data:
            if k.lower() == cle.lower():
                return data[k]
    return None

# ====== ROUTES ======
@app.route("/get-produits", methods=["GET"])
def get_produits():
    batch = int(request.args.get("batch", 1))
    all_products = charger_produits()
    start = (batch - 1) * PRODUITS_PAR_BATCH
    end = batch * PRODUITS_PAR_BATCH
    produits = all_products[start:end]
    has_next = end < len(all_products)

    print(f"🔄 Batch {batch} envoyé avec {len(produits)} produit(s) | has_next: {has_next}")
    return jsonify({
        "produits": produits,
        "has_next": has_next
    })

@app.route("/upload-fiche", methods=["POST"])
def upload_fiche():
    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("❌ JSON invalide :", e)
        return jsonify({"error": "Requête JSON invalide."}), 400

    id_produit = get_flexible(data, "id")
    nom = get_flexible(data, "nom")
    html = get_flexible(data, "html")

    missing = []
    if not id_produit: missing.append("id")
    if not nom: missing.append("nom")
    if not html: missing.append("html")
    if missing:
        return jsonify({"error": f"Champs manquants : {', '.join(missing)}"}), 400

    if not os.path.exists(DOSSIER_FICHES):
        os.makedirs(DOSSIER_FICHES)

    nom_fichier = f"{id_produit}-{clean_filename(nom)[:80]}.txt"
    chemin = os.path.join(DOSSIER_FICHES, nom_fichier)

    try:
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        print("❌ Erreur écriture fichier :", e)
        return jsonify({"error": "Impossible d'enregistrer la fiche."}), 500

    print(f"✅ Fiche '{nom}' (ID {id_produit}) enregistrée.")
    return jsonify({"message": f"Fiche '{nom}' (ID {id_produit}) enregistrée avec succès."})

@app.route("/list-fiches", methods=["GET"])
def list_fiches():
    return jsonify(os.listdir(DOSSIER_FICHES)) if os.path.exists(DOSSIER_FICHES) else jsonify([])

# ====== LANCEMENT ======
if __name__ == "__main__":
    app.run(port=5000, debug=True)
