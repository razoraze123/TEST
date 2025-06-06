# Module de comptabilité

Ce dossier contient une implémentation minimale permettant de gérer des 
transactions comptables simples. La structure est conçue pour être 
étendue ultérieurement avec des fonctions d'import, de reporting et de 
rapprochement.

## Fichiers

- `transaction.py` : classe `Transaction` représentant une opération
  comptable basique. Chaque transaction possède un champ `categorie`
  (Client, Fournisseur, Frais, TVA ou Autre) attribué automatiquement
  selon des mots-clés présents dans le libellé.
- `account.py` : classe `Account` pour manipuler des comptes et calculer
  leur solde.
- `journal_entry.py` : classe `JournalEntry` correspondant aux lignes
  d'écriture liées aux transactions.
- `storage.py` : abstractions de stockage avec une implémentation en
  mémoire (`InMemoryStorage`). Ce système pourra être adapté pour
  utiliser SQLite ou des fichiers CSV.
- `categorization.py` : règles de catégorisation automatique et fonction de
  rapport des totaux par catégorie.
- `__init__.py` : expose les classes et fonctions principales du module.

Les données sont pour l'instant conservées en mémoire via des listes
mais la couche `BaseStorage` prévoit l'intégration future d'autres
backends de persistance.

Un outil permet également d'obtenir un **rapport rapide** des montants
totaux par catégorie sur une période donnée via la fonction
`rapport_par_categorie`.

## Règles de catégorisation

La fonction `categoriser_automatiquement` recherche certains mots-clés
dans le libellé pour déterminer la catégorie :

- **Client** : « facture », « vente », « paiement client »
- **Fournisseur** : « achat », « fournisseur »
- **Frais** : « frais », « carburant », « restaurant », « hotel »
- **TVA** : « tva », « taxe »
- **Autre** si aucun mot-clé n'est trouvé.


Pour plus de détails sur l'import des relevés et l'utilisation des filtres du journal, consultez le fichier [HELP.md](HELP.md).

## Rapprochement bancaire

Le module propose un mécanisme simple pour l'appariement entre
les transactions importées et les écritures internes du journal.

La fonction `suggere_rapprochements` recherche, pour une transaction
donnée, les écritures dont le montant est identique et dont la date est
proche (±3 jours par défaut). Les écritures déjà associées à une autre
transaction sont ignorées. Une fois le bon élément trouvé, la fonction
`rapprocher` assigne l'identifiant de l'écriture à la transaction. Une
transaction possédant un champ `journal_entry_id` est considérée comme
« rapprochée » et peut être filtrée dans l'interface graphique.
