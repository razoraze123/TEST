# Rapport d'audit / Audit Report

## Résumé / Summary
- Structure du dépôt vérifiée : modules CLI, interface graphique, scraping, optimisation et API Flask avec jeux de tests.
- Les tests échouent si les dépendances comme `pandas` ou `SQLAlchemy` ne sont pas installées.
- La configuration `pyproject.toml` ne définit pas explicitement les paquets, ce qui empêche `pip install .`.

## Correctifs appliqués / Fixes Applied
- Ajout d'une section `[tool.setuptools.packages.find]` dans `pyproject.toml` pour lister `accounting`, `db`, `plugins` et `ui`.
- Ajout d'une documentation bilingue (fichiers `README_fr.md` et `README_en.md`).

## Recommandations / Recommendations
- Installer les dépendances avec `pip install .[test]` puis exécuter les tests avec `PYTHONPATH=$PWD pytest`.
- Envisager un script de configuration pour préparer l'environnement (bases de données, outils externes).
