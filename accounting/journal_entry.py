"""Ecritures comptables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from datetime import date
from uuid import uuid4


@dataclass
class JournalEntry:
    """Ligne d'écriture liée à une transaction."""

    transaction_id: str
    account_code: str
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    date: date | None = None
    id: str = field(default_factory=lambda: uuid4().hex)

