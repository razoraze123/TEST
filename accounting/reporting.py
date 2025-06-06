"""Fonctions d'export des données comptables."""

from __future__ import annotations

import logging
import logger_setup  # noqa: F401  # configure logging
import os
from dataclasses import asdict
from datetime import date
from typing import Iterable

import pandas as pd

from fpdf import FPDF

logger = logging.getLogger(__name__)

from .transaction import Transaction
from .journal_entry import JournalEntry
from .categorization import rapport_par_categorie
from .errors import ComptaExportError


def _save_dataframe(df: pd.DataFrame, path: str) -> None:
    """Sauvegarde un DataFrame en CSV ou XLSX selon l'extension."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        func = df.to_csv
    elif ext in {".xls", ".xlsx"}:
        func = df.to_excel
    else:
        raise ComptaExportError("Extension non supportée: " + ext)
    try:
        func(path, index=False)
    except Exception as e:
        logger.exception("Erreur lors de l'export du fichier %s", path)
        raise ComptaExportError(f"Erreur lors de l'export du fichier {path}: {e}") from None


def export_transactions(transactions: Iterable[Transaction], path: str) -> None:
    """Exporte une liste de :class:`Transaction` vers un fichier."""
    df = pd.DataFrame([asdict(tx) for tx in transactions])
    _save_dataframe(df, path)


def export_entries(entries: Iterable[JournalEntry], path: str) -> None:
    """Exporte une liste de :class:`JournalEntry` vers un fichier."""
    df = pd.DataFrame([asdict(e) for e in entries])
    _save_dataframe(df, path)


def grand_livre(entries: Iterable[JournalEntry]) -> pd.DataFrame:
    """Retourne le grand livre trié par compte puis par date."""
    df = pd.DataFrame([asdict(e) for e in entries])
    if not df.empty:
        df = df.sort_values(["account_code", "date"]).reset_index(drop=True)
    return df


def balance(entries: Iterable[JournalEntry]) -> pd.DataFrame:
    """Calcule la balance des comptes."""
    df = pd.DataFrame([asdict(e) for e in entries])
    if df.empty:
        return pd.DataFrame(columns=["account_code", "debit", "credit", "solde"])
    grouped = df.groupby("account_code").agg({"debit": "sum", "credit": "sum"})
    grouped["solde"] = grouped["debit"] - grouped["credit"]
    return grouped.reset_index().sort_values("account_code").reset_index(drop=True)


def rapport_categorie(
    transactions: Iterable[Transaction], start: date | None = None, end: date | None = None
) -> pd.DataFrame:
    """Rapport des montants par catégorie."""
    totals = rapport_par_categorie(list(transactions), start, end)
    df = pd.DataFrame(
        [{"categorie": cat, "total": total} for cat, total in totals.items()]
    )
    if not df.empty:
        df = df.sort_values("categorie").reset_index(drop=True)
    return df


def _add_table(pdf: FPDF, df: pd.DataFrame) -> None:
    """Ajoute un tableau simple dans le PDF."""
    col_width = pdf.epw / max(len(df.columns), 1)
    pdf.set_font("Helvetica", size=10)
    for col in df.columns:
        pdf.cell(col_width, 8, str(col), border=1)
    pdf.ln(8)
    for _, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_width, 8, str(row[col]), border=1)
        pdf.ln(8)


def export_report_pdf(
    ledger_df: pd.DataFrame, balance_df: pd.DataFrame, cat_df: pd.DataFrame, path: str
) -> None:
    """Exporte un rapport complet (grand livre, balance, catégories) en PDF."""
    try:
        pdf = FPDF(orientation="L")
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Grand livre", ln=True)
        _add_table(pdf, ledger_df)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Balance", ln=True)
        _add_table(pdf, balance_df)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Totaux par catégorie", ln=True)
        _add_table(pdf, cat_df)

        pdf.output(path)
    except Exception as e:
        logger.exception("Erreur lors de l'export PDF %s", path)
        raise ComptaExportError(f"Erreur lors de l'export PDF {path}: {e}") from None


def export_report_csv(
    ledger_df: pd.DataFrame, balance_df: pd.DataFrame, cat_df: pd.DataFrame, folder: str
) -> None:
    """Exporte les trois rapports au format CSV dans le dossier donné."""
    os.makedirs(folder, exist_ok=True)
    try:
        ledger_df.to_csv(os.path.join(folder, "ledger.csv"), index=False)
        balance_df.to_csv(os.path.join(folder, "balance.csv"), index=False)
        cat_df.to_csv(os.path.join(folder, "categories.csv"), index=False)
    except Exception as e:
        logger.exception("Erreur lors de l'export CSV dans %s", folder)
        raise ComptaExportError(f"Erreur lors de l'export CSV dans {folder}: {e}") from None

