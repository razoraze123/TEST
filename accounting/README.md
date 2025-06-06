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

## Export des données

Plusieurs fonctions permettent d'enregistrer les informations du journal au
format **CSV** ou **XLSX** : `export_transactions` pour les transactions brutes
et `export_entries` pour les écritures générées. Les rapports globaux peuvent
être exportés en **PDF** avec `export_report_pdf` ou en **CSV** via
`export_report_csv`.

L'arborescence recommandée pour stocker ces fichiers est :

```text
BASE_DIR/
  exports/
    journal/
    rapports/
```

Les rapports comportent trois tableaux :

- **grand livre** : toutes les écritures classées par compte puis par date ;
- **balance** : total des débits et crédits par compte avec le solde associé ;
- **synthèse** (totaux par catégorie).

Dans l'interface graphique, la page **Journal** possède un bouton
**Exporter** permettant d'enregistrer soit la liste des transactions, soit les
écritures courantes selon le format choisi.

## Exemple d'import et d'export

Voici un exemple minimal pour importer un relevé bancaire puis enregistrer les écritures correspondantes :

```python
from accounting import import_releve, export_transactions, export_entries
from accounting import InMemoryStorage

storage = InMemoryStorage()
transactions = import_releve("releve.csv", storage)
# ... générer ou charger des écritures dans `entries` ...
export_transactions(transactions, "exports/journal/transactions.xlsx")
export_entries(entries, "exports/journal/entries.csv")
```

La page **Journal** comporte un bouton **Importer relevé...** permettant de charger un fichier au même format. Un lien **Aide** ouvre le fichier `accounting/HELP.md` pour détailler les colonnes attendues.

## Exceptions et journaux d'erreurs

Le module définit plusieurs exceptions spécialisées :

- `ComptaError` : classe de base pour toutes les erreurs comptables.
- `ComptaImportError` : problème lors de la lecture d'un fichier (format non reconnu, fichier absent...).
- `ComptaValidationError` : données manquantes ou valeur invalide.
- `ComptaExportError` : erreur lors de l'écriture d'un fichier d'export.

Toutes les erreurs issues du package sont enregistrées dans le fichier `logs/compta_errors.log`, en plus de l'affichage classique dans la console.
