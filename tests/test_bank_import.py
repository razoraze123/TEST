import pandas as pd
import pytest

from accounting import (
    import_releve,
    InMemoryStorage,
    ComptaValidationError,
    ComptaImportError,
)


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
    with pytest.raises(ComptaValidationError):
        import_releve(str(path))


def test_import_releve_bad_extension(tmp_path):
    txt = tmp_path / "releve.txt"
    txt.write_text("dummy")
    with pytest.raises(ComptaImportError):
        import_releve(str(txt))
