"""Module de comptabilité.

Ce module fournit des classes de base pour gérer des opérations
comptables simples. Les données sont stockées en mémoire mais une
abstraction prépare l'utilisation d'autres backends comme SQLite ou CSV.
"""

from .transaction import Transaction
from .account import Account
from .journal_entry import JournalEntry
from .storage import BaseStorage, InMemoryStorage
from .bank_import import import_releve

__all__ = [
    "Transaction",
    "Account",
    "JournalEntry",
    "BaseStorage",
    "InMemoryStorage",
    "import_releve",
]

