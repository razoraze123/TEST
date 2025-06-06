# Accounting Module

This folder contains a minimal implementation to manage basic accounting transactions. The structure can be extended with import, reporting and reconciliation features.

## Files
- `transaction.py`: `Transaction` class representing a basic operation with automatic category assignment based on keywords.
- `account.py`: `Account` class to manage accounts and compute balances.
- `journal_entry.py`: `JournalEntry` class linked to transactions.
- `storage.py`: storage abstractions with an in-memory implementation (`InMemoryStorage`).
- `categorization.py`: automatic categorization rules and category report function.
- `__init__.py`: exposes the main classes and functions.

Data is currently kept in memory but the `BaseStorage` layer allows plugging other backends like SQLite or CSV.
