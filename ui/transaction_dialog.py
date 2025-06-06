from __future__ import annotations

from datetime import date
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QLineEdit,
    QDateEdit,
    QDoubleSpinBox,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import QDate

from accounting import Transaction, CATEGORIES_KEYWORDS


class TransactionDialog(QDialog):
    """Bo\u00eete de dialogue pour saisir ou modifier une transaction."""

    def __init__(self, parent=None, transaction: Optional[Transaction] = None):
        super().__init__(parent)
        self.setWindowTitle("Op\u00e9ration")

        self._tx = transaction

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.edit_date = QDateEdit()
        self.edit_date.setCalendarPopup(True)
        self.edit_description = QLineEdit()
        self.spin_amount = QDoubleSpinBox()
        self.spin_amount.setDecimals(2)
        self.spin_amount.setRange(0.0, 1e9)
        self.edit_debit = QLineEdit()
        self.edit_credit = QLineEdit()
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(list(CATEGORIES_KEYWORDS.keys()) + ["Autre"])

        form.addRow("Date", self.edit_date)
        form.addRow("Libell\u00e9", self.edit_description)
        form.addRow("Montant", self.spin_amount)
        form.addRow("Compte d\u00e9bit", self.edit_debit)
        form.addRow("Compte cr\u00e9dit", self.edit_credit)
        form.addRow("Cat\u00e9gorie", self.combo_cat)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if transaction:
            self.edit_date.setDate(QDate(transaction.date.year, transaction.date.month, transaction.date.day))
            self.edit_description.setText(transaction.description)
            self.spin_amount.setValue(transaction.montant)
            self.edit_debit.setText(transaction.debit)
            self.edit_credit.setText(transaction.credit)
            index = self.combo_cat.findText(transaction.categorie)
            if index >= 0:
                self.combo_cat.setCurrentIndex(index)

    # ------------------------------------------------------------------
    def _validate(self):
        if not self.edit_date.date().isValid():
            QMessageBox.warning(self, "Date invalide", "Veuillez saisir une date valide")
            return
        montant = self.spin_amount.value()
        if montant <= 0:
            QMessageBox.warning(self, "Montant invalide", "Le montant doit \u00eatre positif")
            return
        debit = self.edit_debit.text().strip()
        credit = self.edit_credit.text().strip()
        if not debit and not credit:
            QMessageBox.warning(self, "Comptes manquants", "Sp\u00e9cifiez un compte d\u00e9bit ou cr\u00e9dit")
            return

        self.accept()

    # ------------------------------------------------------------------
    def get_transaction(self) -> Transaction:
        qdate = self.edit_date.date()
        tx_date = date(qdate.year(), qdate.month(), qdate.day())
        tx = Transaction(
            tx_date,
            self.edit_description.text(),
            float(self.spin_amount.value()),
            self.edit_debit.text().strip(),
            self.edit_credit.text().strip(),
            self.combo_cat.currentText(),
        )
        return tx

