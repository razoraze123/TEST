# Rapport de corrections d'import / Import Fix Report

## FRANÇAIS

Les scripts Python du projet ont été vérifiés afin de s'assurer que tous les modules utilisés sont bien importés.
Une seule anomalie a été trouvée et corrigée :

- **ui/visual_selector.py** : ajout de `import os` pour permettre l'utilisation de `os.path.join` et `os.path.isfile`.

Aucun autre fichier n'utilisait de module non importé.

## ENGLISH

All Python files were checked to guarantee that every used module is properly imported.
Only one issue was found and fixed:

- **ui/visual_selector.py**: added `import os` to enable the calls to `os.path.join` and `os.path.isfile`.

No other file referenced modules without importing them.

### Rapport de vérification supplémentaire

Un second passage sur l'ensemble des 53 fichiers Python n'a révélé aucun nouvel
oubli d'import. Aucun changement additionnel n'a été nécessaire.
