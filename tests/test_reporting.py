import pandas as pd
import pytest
from datetime import date

from accounting import (
    Transaction,
    JournalEntry,
    export_transactions,
    export_entries,
    grand_livre,
    balance,
    rapport_categorie,
    export_report_pdf,
    export_report_csv,
)


def test_export_transactions_csv(tmp_path):
    txs = [
        Transaction(date(2023, 1, 1), "Achat", 50.0, debit="401", credit=""),
        Transaction(date(2023, 1, 2), "Vente", 120.0, debit="", credit="701"),
    ]
    path = tmp_path / "tx.csv"
    export_transactions(txs, path)

    assert path.exists()
    df = pd.read_csv(path)
    assert len(df) == 2
    assert set(["date", "description", "montant"]).issubset(df.columns)


def test_export_transactions_xlsx(tmp_path):
    txs = [
        Transaction(date(2023, 1, 1), "Achat", 50.0, debit="401", credit=""),
        Transaction(date(2023, 1, 2), "Vente", 120.0, debit="", credit="701"),
    ]
    path = tmp_path / "tx.xlsx"
    export_transactions(txs, path)

    assert path.exists()
    df = pd.read_excel(path)
    assert len(df) == 2
    assert set(["date", "description", "montant"]).issubset(df.columns)


def test_export_entries_xlsx(tmp_path):
    entries = [
        JournalEntry("1", "701", debit=100.0, date=date(2023, 1, 1)),
        JournalEntry("2", "602", credit=80.0, date=date(2023, 1, 2)),
    ]
    path = tmp_path / "entries.xlsx"
    export_entries(entries, path)

    assert path.exists()
    df = pd.read_excel(path)
    assert len(df) == 2
    assert set(["transaction_id", "account_code"]).issubset(df.columns)


def test_export_entries_csv(tmp_path):
    entries = [
        JournalEntry("1", "701", debit=100.0, date=date(2023, 1, 1)),
        JournalEntry("2", "602", credit=80.0, date=date(2023, 1, 2)),
    ]
    path = tmp_path / "entries.csv"
    export_entries(entries, path)

    assert path.exists()
    df = pd.read_csv(path)
    assert len(df) == 2
    assert set(["transaction_id", "account_code"]).issubset(df.columns)


def test_grand_livre_and_balance_values():
    entries = [
        JournalEntry("1", "601", debit=50.0, date=date(2023, 1, 1)),
        JournalEntry("2", "701", credit=20.0, date=date(2023, 1, 2)),
        JournalEntry("3", "601", debit=30.0, date=date(2023, 1, 3)),
    ]
    ledger_df = grand_livre(entries)
    assert list(ledger_df["account_code"]) == ["601", "601", "701"]

    balance_df = balance(entries)
    balance_df["account_code"] = balance_df["account_code"].astype(str)
    bal_601 = balance_df.loc[balance_df["account_code"] == "601"].iloc[0]
    bal_701 = balance_df.loc[balance_df["account_code"] == "701"].iloc[0]
    assert bal_601["debit"] == 80.0
    assert bal_601["credit"] == 0.0
    assert bal_601["solde"] == 80.0
    assert bal_701["debit"] == 0.0
    assert bal_701["credit"] == 20.0
    assert bal_701["solde"] == -20.0


def test_export_invalid_extension(tmp_path):
    with pytest.raises(ValueError):
        export_transactions([], tmp_path / "report.txt")


def _sample_data():
    entries = [
        JournalEntry("1", "701", debit=100.0, date=date(2023, 1, 1)),
        JournalEntry("2", "602", credit=80.0, date=date(2023, 1, 2)),
    ]
    txs = [
        Transaction(date(2023, 1, 1), "Vente", 100.0, debit="411", credit="701", categorie="Client"),
        Transaction(date(2023, 1, 2), "Achat", 80.0, debit="602", credit="401", categorie="Fournisseur"),
    ]
    ledger_df = grand_livre(entries)
    balance_df = balance(entries)
    cat_df = rapport_categorie(txs)
    return ledger_df, balance_df, cat_df


def test_export_report_csv(tmp_path):
    ledger_df, balance_df, cat_df = _sample_data()
    folder = tmp_path / "csv"
    export_report_csv(ledger_df, balance_df, cat_df, folder)
    ledger_path = folder / "ledger.csv"
    balance_path = folder / "balance.csv"
    cat_path = folder / "categories.csv"

    assert ledger_path.exists()
    assert balance_path.exists()
    assert cat_path.exists()

    df_bal = pd.read_csv(balance_path)
    assert "solde" in df_bal.columns
    df_bal["account_code"] = df_bal["account_code"].astype(str)
    assert df_bal.loc[df_bal["account_code"] == "701", "solde"].iloc[0] == 100.0


def test_export_report_pdf(tmp_path):
    ledger_df, balance_df, cat_df = _sample_data()
    path = tmp_path / "report.pdf"
    export_report_pdf(ledger_df, balance_df, cat_df, path)
    assert path.exists()
    assert path.stat().st_size > 0
    with open(path, "rb") as f:
        header = f.read(4)
    assert header.startswith(b"%PDF")
