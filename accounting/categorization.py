"""Outils pour catégoriser automatiquement les transactions."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

from .transaction import Transaction

# Mots-clés par catégorie
CATEGORIES_KEYWORDS: Dict[str, List[str]] = {
    "Client": ["facture", "vente", "paiement client"],
    "Fournisseur": ["achat", "fournisseur"],
    "Frais": ["frais", "carburant", "restaurant", "hotel"],
    "TVA": ["tva", "taxe"],
}


def categoriser_automatiquement(tx: Transaction) -> str:
    """Attribue une catégorie en fonction du libellé."""
    texte = tx.description.lower()
    for categorie, mots in CATEGORIES_KEYWORDS.items():
        if any(m in texte for m in mots):
            tx.categorie = categorie
            return categorie
    tx.categorie = "Autre"
    return "Autre"


def rapport_par_categorie(
    transactions: List[Transaction],
    start: date | None = None,
    end: date | None = None,
) -> Dict[str, float]:
    """Retourne le total des montants par catégorie."""
    totaux: Dict[str, float] = {}
    for tx in transactions:
        if start and tx.date < start:
            continue
        if end and tx.date > end:
            continue
        cat = tx.categorie
        totaux[cat] = totaux.get(cat, 0.0) + tx.montant
    return totaux
