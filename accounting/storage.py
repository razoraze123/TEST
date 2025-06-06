"""Abstractions de stockage pour les données comptables."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from sqlalchemy import Column, String, Float, Date, ForeignKey

from db import SessionLocal, engine
from db.models import Base


class AccountModel(Base):
    __tablename__ = "accounts"
    code = Column(String, primary_key=True)
    nom = Column(String)


class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    date = Column(Date)
    description = Column(String)
    montant = Column(Float)
    debit = Column(String)
    credit = Column(String)
    categorie = Column(String)
    journal_entry_id = Column(String, ForeignKey("journal_entries.id"), nullable=True)


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"
    id = Column(String, primary_key=True)
    transaction_id = Column(String, ForeignKey("transactions.id"))
    account_code = Column(String, ForeignKey("accounts.code"))
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=True)

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


class SQLStorage(BaseStorage):
    """Implémentation basée sur SQLAlchemy."""

    def __init__(self) -> None:
        Base.metadata.create_all(bind=engine)

    def _session(self):
        return SessionLocal()

    def add_account(self, account: Account) -> None:
        with self._session() as session:
            obj = AccountModel(code=account.code, nom=account.nom)
            session.merge(obj)
            session.commit()

    def add_transaction(self, tx: Transaction) -> None:
        with self._session() as session:
            obj = TransactionModel(
                id=tx.id,
                date=tx.date,
                description=tx.description,
                montant=tx.montant,
                debit=tx.debit,
                credit=tx.credit,
                categorie=tx.categorie,
                journal_entry_id=tx.journal_entry_id,
            )
            session.merge(obj)
            session.commit()

    def add_entry(self, entry: JournalEntry) -> None:
        with self._session() as session:
            obj = JournalEntryModel(
                id=entry.id,
                transaction_id=entry.transaction_id,
                account_code=entry.account_code,
                debit=entry.debit,
                credit=entry.credit,
                description=entry.description,
                date=entry.date,
            )
            session.merge(obj)
            session.commit()

    def list_accounts(self) -> List[Account]:
        with self._session() as session:
            rows = session.query(AccountModel).all()
            return [Account(code=r.code, nom=r.nom) for r in rows]

    def list_transactions(self) -> List[Transaction]:
        with self._session() as session:
            rows = session.query(TransactionModel).all()
            return [
                Transaction(
                    r.date,
                    r.description,
                    r.montant,
                    r.debit,
                    r.credit,
                    categorie=r.categorie,
                    id=r.id,
                    journal_entry_id=r.journal_entry_id,
                )
                for r in rows
            ]

    def list_entries(self) -> List[JournalEntry]:
        with self._session() as session:
            rows = session.query(JournalEntryModel).all()
            return [
                JournalEntry(
                    r.transaction_id,
                    r.account_code,
                    debit=r.debit,
                    credit=r.credit,
                    description=r.description,
                    date=r.date,
                    id=r.id,
                )
                for r in rows
            ]
