from datetime import date

from accounting import Transaction, JournalEntry
from accounting.reconciliation import suggere_rapprochements, rapprocher


def test_suggere_rapprochements():
    tx = Transaction(date(2023, 1, 10), "Paiement", 100.0, "BANQUE", "")
    entry1 = JournalEntry("1", "701", debit=100.0, date=date(2023, 1, 11))
    entry2 = JournalEntry("2", "701", debit=50.0, date=date(2023, 1, 11))
    entry3 = JournalEntry("3", "701", debit=100.0, date=date(2023, 1, 20))
    entries = [entry1, entry2, entry3]
    res = suggere_rapprochements(tx, entries, [tx], delta_jours=3)
    assert res == [entry1]


def test_rapprocher():
    tx = Transaction(date(2023, 1, 10), "Paiement", 100.0, "BANQUE", "")
    entry = JournalEntry("1", "701", debit=100.0, date=date(2023, 1, 10))
    rapprocher(tx, entry)
    assert tx.journal_entry_id == entry.id
