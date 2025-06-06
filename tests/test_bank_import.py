import pandas as pd
import pytest

from accounting import import_releve, InMemoryStorage


def test_import_releve_csv(tmp_path):
    # create sample csv
    data = pd.DataFrame({
        'Date': ['2023-01-01', '2023-01-02'],
        'Libellé': ['Achat', 'Virement'],
        'Montant': [10.5, 20.0],
        'Type': ['débit', 'crédit'],
    })
    csv_path = tmp_path / 'releve.csv'
    data.to_csv(csv_path, index=False)

    storage = InMemoryStorage()
    txs = import_releve(str(csv_path), storage)

    assert len(txs) == 2
    assert txs[0].debit == 'BANQUE'
    assert txs[1].credit == 'BANQUE'
    # storage should contain same transactions
    assert len(storage.list_transactions()) == 2


def test_import_releve_missing_col(tmp_path):
    df = pd.DataFrame({'Date': ['2023-01-01']})
    path = tmp_path / 'bad.csv'
    df.to_csv(path, index=False)
    with pytest.raises(ValueError):
        import_releve(str(path))
