"""Ecritures comptables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class JournalEntry:
    """Ligne d'écriture liée à une transaction."""

    transaction_id: str
    account_code: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None

