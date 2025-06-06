# Aide sur l'import du journal

Ce document explique comment mettre en forme votre fichier bancaire et comment l'importer dans la page **Journal** de l'application.

## Format du fichier

Le fichier doit comporter au minimum les colonnes suivantes :

- **date** : date de l'opération (formats reconnus par pandas, par exemple `AAAA-MM-JJ`).
- **libellé** : description de l'écriture.
- **montant** : montant numérique de l'opération.
- **type** : indique s'il s'agit d'un "débit" ou d'un "crédit".

La détection des noms de colonnes est insensible à la casse et aux accents. Les autres colonnes sont ignorées.

## Importer un relevé

1. Ouvrez la page **Journal** depuis la barre latérale.
2. Cliquez sur le bouton **Importer relevé…** situé en haut de la page.
3. Sélectionnez un fichier CSV ou Excel contenant les colonnes ci-dessus.
4. Les lignes valides sont ajoutées au tableau.

## Filtres disponibles

Sous le bouton d'import se trouvent plusieurs champs permettant de filtrer le journal :

- **Du / au** : limites de dates.
- **Libellé contient…** : texte à rechercher dans la colonne libellé.
- **Min / Max** : plage de montants.
- **Type** : tous, seulement les débits ou seulement les crédits.
- **Catégorie** : limite l'affichage aux opérations d'une catégorie
  précise (Client, Fournisseur, Frais, TVA ou Autre).

Les filtres s'appliquent immédiatement lors de la modification des champs.
