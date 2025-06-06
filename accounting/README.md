# Module de comptabilité

Ce dossier contient une implémentation minimale permettant de gérer des 
transactions comptables simples. La structure est conçue pour être 
étendue ultérieurement avec des fonctions d'import, de reporting et de 
rapprochement.

## Fichiers

- `transaction.py` : classe `Transaction` représentant une opération
  comptable basique.
- `account.py` : classe `Account` pour manipuler des comptes et calculer
  leur solde.
- `journal_entry.py` : classe `JournalEntry` correspondant aux lignes
  d'écriture liées aux transactions.
- `storage.py` : abstractions de stockage avec une implémentation en
  mémoire (`InMemoryStorage`). Ce système pourra être adapté pour
  utiliser SQLite ou des fichiers CSV.
- `__init__.py` : expose les classes principales du module.

Les données sont pour l'instant conservées en mémoire via des listes
mais la couche `BaseStorage` prévoit l'intégration future d'autres
backends de persistance.


Pour plus de détails sur l'import des relevés et l'utilisation des filtres du journal, consultez le fichier [HELP.md](HELP.md).
