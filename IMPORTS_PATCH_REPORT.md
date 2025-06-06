# Rapport de corrections d'import

Ce correctif ajoute l'import manquant suivant :

- **ui/main_window.py** : ajout de `QPropertyAnimation` depuis `PySide6.QtCore` pour permettre l'animation de la barre latérale.

Aucun autre fichier ne présentait d'utilisation de module sans import correspondant.
La vérification a été effectuée à l'aide de **pyflakes** sur l'ensemble du projet.
