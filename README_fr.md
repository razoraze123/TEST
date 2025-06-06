# Installation et utilisation

## Prérequis
- Python 3.10 ou supérieur
- Google Chrome (le pilote est téléchargé automatiquement si `CHROME_DRIVER_PATH` est vide)

Installez le projet avec :
```bash
pip install .
```

Pour utiliser le scraping asynchrone, installez également les navigateurs `playwright` :
```bash
playwright install
```

### Démarrage rapide
```bash
pip install .
python Application.py
```

### Autres modes d'installation
- **Docker**
  ```bash
  docker build -t woocommerce-scraper .
  docker run --rm woocommerce-scraper
  ```
- **Exécutable autonome**
  ```bash
  ./build.sh
  dist/woocommerce-scraper --help
  ```

### Lancer les tests
```bash
pip install .[test]
pytest
```

### Paramétrage
Les chemins sont stockés dans `config.toml` à la racine du dépôt. S'il est absent, un fichier par défaut est créé.

### Utilisation de l'application
Lancez l'interface PySide6 avec :
```bash
python Application.py
```
Elle permet d'effectuer le scraping, l'optimisation des images et de consulter les rapports.
