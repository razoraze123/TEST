"""Gestion des comptes comptables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .journal_entry import JournalEntry


@dataclass
class Account:
    """Un compte comptable."""

    code: str
    nom: str
    entries: List[JournalEntry] = field(default_factory=list)

    def ajouter_ecriture(self, entry: JournalEntry) -> None:
        """Ajoute une écriture au compte."""
        self.entries.append(entry)

    @property
    def solde(self) -> float:
        """Calcule le solde du compte."""
        debit = sum(e.debit for e in self.entries)
        credit = sum(e.credit for e in self.entries)
        return debit - credit
