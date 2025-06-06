"""Fonctions d'export des données comptables."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Iterable

import pandas as pd

from .transaction import Transaction
from .journal_entry import JournalEntry


def _save_dataframe(df: pd.DataFrame, path: str) -> None:
    """Sauvegarde un DataFrame en CSV ou XLSX selon l'extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in {".xls", ".xlsx"}:
        df.to_excel(path, index=False)
    else:
        raise ValueError("Extension non supportée: " + ext)


def export_transactions(transactions: Iterable[Transaction], path: str) -> None:
    """Exporte une liste de :class:`Transaction` vers un fichier."""
    df = pd.DataFrame([asdict(tx) for tx in transactions])
    _save_dataframe(df, path)


def export_entries(entries: Iterable[JournalEntry], path: str) -> None:
    """Exporte une liste de :class:`JournalEntry` vers un fichier."""
    df = pd.DataFrame([asdict(e) for e in entries])
    _save_dataframe(df, path)

