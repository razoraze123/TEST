"""Outils de rapprochement bancaire."""

from __future__ import annotations

from typing import List

from .transaction import Transaction
from .journal_entry import JournalEntry


def _entry_amount(entry: JournalEntry) -> float:
    """Retourne le montant positif de l'écriture."""
    return entry.debit if entry.debit else entry.credit


def suggere_rapprochements(
    tx: Transaction,
    entries: List[JournalEntry],
    transactions: List[Transaction],
    delta_jours: int = 3,
) -> List[JournalEntry]:
    """Propose les écritures correspondant à une transaction.

    Une écriture est suggérée si son montant est égal à celui de la
    transaction et si sa date est comprise dans l'intervalle ``±delta_jours``.
    Les écritures déjà rapprochées sont ignorées.
    """

    matched_ids = {
        t.journal_entry_id for t in transactions if t.journal_entry_id
    }
    suggestions = []
    for entry in entries:
        if entry.id in matched_ids:
            continue
        if entry.date is None:
            continue
        if abs(_entry_amount(entry) - tx.montant) > 0.01:
            continue
        if abs((entry.date - tx.date).days) > delta_jours:
            continue
        suggestions.append(entry)
    return suggestions


def rapprocher(tx: Transaction, entry: JournalEntry) -> None:
    """Marque la transaction comme rapprochée avec l'écriture donnée."""
    tx.journal_entry_id = entry.id
