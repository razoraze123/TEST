# Documentation

For English instructions see [README_en.md](README_en.md).

Pour la documentation en français, consultez [README_fr.md](README_fr.md).

Launch the application with:
```bash
python Application.py
```

---

## Détection CSS avec IA légère

✨ RÉCAPITULATIF COMPLET – Mise en place de ton système intelligent pour détection CSS avec IA légère

---

🎯 Objectif général :
Créer un outil intelligent capable de :
- Recevoir du HTML
- Comprendre une question (ex : "Je veux le lien" / "Donne-moi le titre")
- Générer le meilleur sélecteur CSS
- Fonctionner hors-ligne, léger, sans dépendre d’un navigateur (pas Selenium)
- Utiliser une IA embarquée légère (DistilBERT) pour simuler un mini cerveau

---

🧱 Architecture à 2 composants :

1. **cerveau.py** – Le cerveau IA
   - Chargera DistilBERT ou un modèle NLP léger (ex : zero-shot classifier)
   - Comprend la question et déduit la cible à extraire dans le HTML
   - Retourne un mot-clé cible (ex : "lien" → chercher `<a>`, "titre" → chercher `h1`/`h2`/`h3`…)

2. **detecteur.py** – Le moteur d’analyse
   - Reçoit un extrait HTML et une demande (ex : "je veux le lien")
   - Envoie la question au cerveau
   - Extrait les balises ou classes en fonction de la réponse du cerveau
   - Retourne un sélecteur CSS stable et optimisé

---

📁 Structure du projet :

```
projet-scrap/
├── cerveau.py            # IA NLP avec DistilBERT
├── detecteur.py          # Détection + extraction + interaction
├── requirements.txt      # Liste des libs nécessaires
└── samples/              # (Optionnel) dossiers de tests HTML
```

---

🛠️ Préparation et installation :

1. Créer un environnement virtuel (recommandé) :
   ```bash
   python -m venv venv
   source venv/bin/activate  # (ou venv\Scripts\activate sous Windows)
   ```
2. Installer les bibliothèques :
   ```bash
   pip install torch transformers beautifulsoup4
   ```
3. Créer ton fichier `requirements.txt` :
   ```
   torch
   transformers
   beautifulsoup4
   ```

---

🧠 Exemple de pipeline de communication :

```python
# detecteur.py
from cerveau import analyser_requete

type_cible = analyser_requete("je veux le lien")
# Retourne 'lien' ou 'titre'
# Puis détecte automatiquement <a> ou <h2> dans le HTML fourni
```

---

💡 Avantages de ce système :

| 🧠 IA Compréhensive | ⚙️ Léger et modulaire | 🔌 Fonctionne hors-ligne | 📚 Évolutif facilement |
|---------------------|-----------------------|---------------------------|-------------------------|
| Tu poses une question librement | Chaque module peut évoluer indépendamment | Pas besoin de navigateur | Tu peux lui apprendre de nouveaux labels ou comportements |

---

❓ Et ensuite ?
- 💾 Générer les deux scripts (`cerveau.py` + `detecteur.py`) prêts à l’emploi ?
- 📂 Fournir un dossier complet zippé avec l’environnement prêt ?
- 🧠 Montrer comment ajouter de nouveaux types de questions intelligentes ?
