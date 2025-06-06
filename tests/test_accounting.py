"""Tests intégrés pour le module de comptabilité.

Cas couverts :
- import de fichiers CSV avec catégorisation automatique
- détection d'erreurs de format (colonnes manquantes, valeurs invalides)
- rapprochement de transactions avec des écritures
- export des transactions, des écritures et des rapports CSV
"""

from datetime import date
import pandas as pd
import pytest

from accounting import (
    InMemoryStorage,
    import_releve,
    export_transactions,
    export_entries,
    export_report_csv,
    grand_livre,
    balance,
    rapport_categorie,
    Transaction,
    JournalEntry,
    suggere_rapprochements,
    rapprocher,
    ComptaValidationError,
)


def _sample_csv(path):
    df = pd.DataFrame({
        "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Libellé": [
            "Paiement client facture 1",
            "Frais restaurant",
            "Achat fournisseur",
        ],
        "Montant": [100.0, 50.0, 200.0],
        "Type": ["crédit", "débit", "débit"],
    })
    df.to_csv(path, index=False)


def test_workflow_import_rapprochement_export(tmp_path):
    csv_path = tmp_path / "releve.csv"
    _sample_csv(csv_path)

    storage = InMemoryStorage()
    txs = import_releve(str(csv_path), storage)
    assert [t.categorie for t in txs] == ["Client", "Frais", "Fournisseur"]

    entries = [
        JournalEntry(txs[0].id, "411", credit=100.0, date=date(2023, 1, 1)),
        JournalEntry(txs[1].id, "606", debit=50.0, date=date(2023, 1, 2)),
        JournalEntry(txs[2].id, "401", debit=200.0, date=date(2023, 1, 3)),
    ]

    sugg = suggere_rapprochements(txs[0], entries, txs)
    assert entries[0] in sugg
    rapprocher(txs[0], entries[0])
    assert txs[0].journal_entry_id == entries[0].id

    ledger = grand_livre(entries)
    bal = balance(entries)
    cat = rapport_categorie(txs)

    export_transactions(txs, tmp_path / "tx.csv")
    export_entries(entries, tmp_path / "entries.csv")
    export_report_csv(ledger, bal, cat, tmp_path / "reports")

    assert (tmp_path / "tx.csv").exists()
    assert (tmp_path / "entries.csv").exists()
    assert (tmp_path / "reports" / "ledger.csv").exists()
    assert set(cat["categorie"]) == {"Client", "Frais", "Fournisseur"}


def test_import_fichier_incomplet(tmp_path):
    df = pd.DataFrame({"Date": ["2023-01-01"], "Libellé": ["Test"], "Montant": [5.0]})
    path = tmp_path / "bad.csv"
    df.to_csv(path, index=False)
    with pytest.raises(ComptaValidationError):
        import_releve(str(path))


def test_import_valeur_invalide(tmp_path):
    df = pd.DataFrame({
        "Date": ["2023-01-01"],
        "Libellé": ["Test"],
        "Montant": [5.0],
        "Type": ["inconnu"],
    })
    path = tmp_path / "bad.csv"
    df.to_csv(path, index=False)
    with pytest.raises(ComptaValidationError):
        import_releve(str(path))
