"""Classes et fonctions concernant les opérations comptables."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import uuid4

from .errors import ComptaValidationError



@dataclass
class Transaction:
    """Représente une opération comptable de base."""

    date: date
    description: str
    montant: float
    debit: str
    credit: str
    categorie: str = "Autre"
    id: str = field(default_factory=lambda: uuid4().hex)
    journal_entry_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Vérifie que ``montant`` est positif et lève une erreur sinon."""
        if self.montant < 0:
            raise ComptaValidationError("Le montant doit être positif")

