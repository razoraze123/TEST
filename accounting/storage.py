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
        self._accounts: List[Account] = []
        self._transactions: List[Transaction] = []
        self._entries: List[JournalEntry] = []

    def add_account(self, account: Account) -> None:
        self._accounts.append(account)

    def add_transaction(self, tx: Transaction) -> None:
        self._transactions.append(tx)

    def add_entry(self, entry: JournalEntry) -> None:
        self._entries.append(entry)

    def list_accounts(self) -> List[Account]:
        return list(self._accounts)

    def list_transactions(self) -> List[Transaction]:
        return list(self._transactions)

    def list_entries(self) -> List[JournalEntry]:
        return list(self._entries)

