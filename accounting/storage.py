"""Abstractions de stockage pour les données comptables."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .transaction import Transaction
from .account import Account
from .journal_entry import JournalEntry


class BaseStorage(ABC):
    """Interface de stockage des données comptables."""

    @abstractmethod
    def add_account(self, account: Account) -> None:
        """Sauvegarde un compte."""

    @abstractmethod
    def add_transaction(self, tx: Transaction) -> None:
        """Sauvegarde une transaction."""

    @abstractmethod
    def add_entry(self, entry: JournalEntry) -> None:
        """Sauvegarde une écriture."""

    @abstractmethod
    def list_accounts(self) -> List[Account]:
        """Retourne tous les comptes."""

    @abstractmethod
    def list_transactions(self) -> List[Transaction]:
        """Retourne toutes les transactions."""

    @abstractmethod
    def list_entries(self) -> List[JournalEntry]:
        """Retourne toutes les écritures."""


class InMemoryStorage(BaseStorage):
    """Implémentation en mémoire simple."""

    def __init__(self) -> None:
        """Crée des listes pour stocker comptes, transactions et écritures."""
        self._accounts: List[Account] = []
        self._transactions: List[Transaction] = []
        self._entries: List[JournalEntry] = []

    def add_account(self, account: Account) -> None:
        """Ajoute un compte dans la mémoire."""
        self._accounts.append(account)

    def add_transaction(self, tx: Transaction) -> None:
        """Enregistre une transaction en mémoire."""
        self._transactions.append(tx)

    def add_entry(self, entry: JournalEntry) -> None:
        """Enregistre une écriture en mémoire."""
        self._entries.append(entry)

    def list_accounts(self) -> List[Account]:
        """Retourne la liste des comptes enregistrés."""
        return list(self._accounts)

    def list_transactions(self) -> List[Transaction]:
        """Retourne la liste des transactions enregistrées."""
        return list(self._transactions)

    def list_entries(self) -> List[JournalEntry]:
        """Retourne la liste des écritures enregistrées."""
        return list(self._entries)

