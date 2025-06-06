import pandas as pd
import pytest
from datetime import date

from accounting import (
    Transaction,
    JournalEntry,
    export_transactions,
    export_entries,
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


def test_export_invalid_extension(tmp_path):
    with pytest.raises(ValueError):
        export_transactions([], tmp_path / "report.txt")
