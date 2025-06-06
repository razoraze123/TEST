"""Classes et fonctions concernant les opérations comptables."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Transaction:
    """Représente une opération comptable de base."""

    date: date
    description: str
    montant: float
    debit: str
    credit: str

    def __post_init__(self) -> None:
        if self.montant < 0:
            raise ValueError("Le montant doit être positif")

