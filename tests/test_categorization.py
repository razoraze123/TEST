from datetime import date

from accounting import Transaction
from accounting.categorization import categoriser_automatiquement, rapport_par_categorie


def test_categoriser_automatiquement():
    tx = Transaction(date.today(), "Paiement client facture 123", 100.0, "BANQUE", "")
    categoriser_automatiquement(tx)
    assert tx.categorie == "Client"


def test_rapport_par_categorie():
    tx1 = Transaction(date(2023, 1, 1), "Achat fournisseur", 50.0, "", "BANQUE")
    tx2 = Transaction(date(2023, 1, 2), "Paiement client", 120.0, "BANQUE", "")
    categoriser_automatiquement(tx1)
    categoriser_automatiquement(tx2)
    totals = rapport_par_categorie([tx1, tx2], date(2023, 1, 1), date(2023, 1, 31))
    assert totals["Fournisseur"] == 50.0
    assert totals["Client"] == 120.0
