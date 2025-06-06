"""Importation de relevés bancaires au format CSV ou Excel."""

from __future__ import annotations

import logging
import logger_setup  # noqa: F401  # configure logging
import os
import unicodedata
from typing import List

logger = logging.getLogger(__name__)

import pandas as pd

from .transaction import Transaction
from .storage import BaseStorage
from .categorization import categoriser_automatiquement
from .errors import ComptaImportError, ComptaValidationError


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
    logger.info("D\u00e9but import du fichier %s", path)
    try:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(path)
        elif ext in [".xls", ".xlsx"]:
            df = pd.read_excel(path)
        else:
            raise ComptaImportError("Format de fichier non support\u00e9")
    except FileNotFoundError:
        logger.exception("Fichier introuvable: %s", path)
        raise ComptaImportError(f"Fichier introuvable: {path}") from None
    except Exception as e:  # lecture/parse errors
        logger.exception("Erreur lors de la lecture du fichier %s", path)
        raise ComptaImportError(f"Erreur lors de la lecture du fichier {path} : {e}") from None

    logger.info("%d lignes lues depuis %s", len(df), path)

    # normaliser les noms de colonnes
    col_map = {_norm(c): c for c in df.columns}
    required = ["date", "libelle", "montant", "type"]
    missing = [c for c in required if c not in col_map]
    if missing:
        logger.error("Colonnes manquantes: %s", ", ".join(missing))
        raise ComptaValidationError("Colonnes manquantes : " + ", ".join(missing))

    df = df.rename(columns={ col_map[k]: k for k in required })

    txs: List[Transaction] = []
    for _, row in df.iterrows():
        try:
            dt = pd.to_datetime(row["date"]).date()
        except Exception as e:
            logger.exception("Date invalide %s: %s", row.get("date"), e)
            raise ComptaValidationError(f"Date invalide : {row.get('date')}") from None
        desc = str(row["libelle"]) if not pd.isna(row["libelle"]) else ""
        montant = float(row["montant"])
        type_val = _norm(str(row["type"]))
        if type_val.startswith("debit"):
            tx = Transaction(dt, desc, montant, debit="BANQUE", credit="")
        elif type_val.startswith("credit"):
            tx = Transaction(dt, desc, montant, debit="", credit="BANQUE")
        else:
            logger.error("Type invalide: %s", row["type"])
            raise ComptaValidationError(f"Type invalide : {row['type']}")
        categoriser_automatiquement(tx)
        txs.append(tx)
        if storage:
            try:
                storage.add_transaction(tx)
            except Exception as e:
                logger.exception("Erreur lors de l'enregistrement: %s", e)
                raise ComptaImportError(f"Erreur lors de l'enregistrement : {e}") from None
    logger.info("Import du fichier %s termin\u00e9 : %d lignes trait\u00e9es", path, len(txs))
    return txs
