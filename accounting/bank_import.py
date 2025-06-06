"""Importation de relevés bancaires au format CSV ou Excel."""

from __future__ import annotations

import logging
import os
import unicodedata
from typing import List

import pandas as pd

from .transaction import Transaction
from .storage import BaseStorage


def _norm(text: str) -> str:
    """Normalise un texte (minuscules, sans accents)."""
    tmp = unicodedata.normalize("NFKD", text)
    tmp = "".join(c for c in tmp if not unicodedata.combining(c))
    return tmp.lower().strip()


def import_releve(path: str, storage: BaseStorage | None = None) -> List[Transaction]:
    """Lit un relevé bancaire et retourne une liste de :class:`Transaction`.

    Le fichier peut être au format CSV ou Excel. En option, un objet
    :class:`BaseStorage` peut être passé pour enregistrer automatiquement
    les transactions importées.
    """
    try:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(path)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(path)
        else:
            raise ValueError("Format de fichier non supporté")
    except FileNotFoundError:
        logging.error("Fichier introuvable: %s", path)
        raise ValueError(f"Fichier introuvable: {path}") from None
    except Exception as e:  # lecture/parse errors
        logging.error("Erreur lors de la lecture de %s : %s", path, e)
        raise ValueError(f"Erreur lors de la lecture du fichier {path} : {e}") from None

    # normaliser les noms de colonnes
    col_map = { _norm(c): c for c in df.columns }
    required = ["date", "libelle", "montant", "type"]
    missing = [c for c in required if c not in col_map]
    if missing:
        logging.error("Colonnes manquantes: %s", ", ".join(missing))
        raise ValueError("Colonnes manquantes : " + ", ".join(missing))

    df = df.rename(columns={ col_map[k]: k for k in required })

    txs: List[Transaction] = []
    for _, row in df.iterrows():
        try:
            dt = pd.to_datetime(row["date"]).date()
        except Exception as e:
            logging.error("Date invalide %s: %s", row.get("date"), e)
            raise ValueError(f"Date invalide : {row.get('date')}") from None
        desc = str(row["libelle"]) if not pd.isna(row["libelle"]) else ""
        montant = float(row["montant"])
        type_val = _norm(str(row["type"]))
        if type_val.startswith("debit"):
            tx = Transaction(dt, desc, montant, debit="BANQUE", credit="")
        elif type_val.startswith("credit"):
            tx = Transaction(dt, desc, montant, debit="", credit="BANQUE")
        else:
            logging.error("Type invalide: %s", row["type"])
            raise ValueError(f"Type invalide : {row['type']}")
        txs.append(tx)
        if storage:
            try:
                storage.add_transaction(tx)
            except Exception as e:
                logging.error("Erreur lors de l'enregistrement: %s", e)
                raise
    return txs
