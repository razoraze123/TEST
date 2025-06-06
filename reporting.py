from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy import func

import db
from db.models import Product, Competitor


@dataclass
class ErrorStat:
    status: str
    count: int


def total_articles() -> int:
    """Return total number of products stored in the database."""
    with db.SessionLocal() as session:
        return session.query(func.count(Product.product_id)).scalar() or 0


def error_counts() -> List[ErrorStat]:
    """Return counts of competitor records grouped by status (excluding 'OK')."""
    with db.SessionLocal() as session:
        rows = (
            session.query(Competitor.status, func.count(Competitor.id))
            .filter(Competitor.status != "OK")
            .group_by(Competitor.status)
            .all()
        )
    return [ErrorStat(status, count) for status, count in rows]


def progress_by_batch(batch_size: int = 50) -> List[Tuple[int, int]]:
    """Return number of competitor entries processed per batch."""
    with db.SessionLocal() as session:
        ids = [r[0] for r in session.query(Competitor.id).order_by(Competitor.id).all()]

    batches: Counter[int] = Counter()
    for idx, _id in enumerate(ids, start=1):
        batch = (idx - 1) // batch_size + 1
        batches[batch] += 1

    return sorted(batches.items())

