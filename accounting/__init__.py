"""Module de comptabilité.

Ce module fournit des classes de base pour gérer des opérations
comptables simples. Les données sont stockées en mémoire mais une
abstraction prépare l'utilisation d'autres backends comme SQLite ou CSV.

---

Accounting module.

This package offers basic classes to manage simple accounting
transactions. Data is kept in memory but the abstraction layer allows
using other backends such as SQLite or CSV.
"""

from .transaction import Transaction
from .account import Account
from .journal_entry import JournalEntry
from .storage import BaseStorage, InMemoryStorage, SQLStorage
from .bank_import import import_releve
from .categorization import (
    categoriser_automatiquement,
    rapport_par_categorie,
    CATEGORIES_KEYWORDS,
)
from .reconciliation import suggere_rapprochements, rapprocher
from .reporting import (
    export_transactions,
    export_entries,
    grand_livre,
    balance,
    rapport_categorie,
    export_report_pdf,
    export_report_csv,
)
from .errors import (
    ComptaError,
    ComptaImportError,
    ComptaValidationError,
    ComptaExportError,
)

__all__ = [
    "Transaction",
    "Account",
    "JournalEntry",
    "BaseStorage",
    "InMemoryStorage",
    "SQLStorage",
    "import_releve",
    "categoriser_automatiquement",
    "rapport_par_categorie",
    "CATEGORIES_KEYWORDS",
    "suggere_rapprochements",
    "rapprocher",
    "export_transactions",
    "export_entries",
    "grand_livre",
    "balance",
    "rapport_categorie",
    "export_report_pdf",
    "export_report_csv",
    "ComptaError",
    "ComptaImportError",
    "ComptaValidationError",
    "ComptaExportError",
]
