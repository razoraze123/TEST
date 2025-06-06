# Journal Import Help

This document explains how to format your bank file and import it in the **Journal** page of the application.

## File Format
The file must contain at least the following columns:
- **date**: operation date (any format recognised by pandas, e.g. `YYYY-MM-DD`)
- **libelle**: description of the entry
- **montant**: numeric amount
- **type**: "debit" or "credit"

Column names are case- and accent-insensitive. Other columns are ignored.

## Importing a Statement
1. Open the **Journal** page.
2. Click **Importer relevé...**.
3. Choose your CSV or Excel file.
4. Valid rows are added to the table.

## Available Filters
Below the import button you can filter the journal by date range, text, amount range, transaction type and category. Results update immediately when you change a field.
