from __future__ import annotations

import os
from typing import List, Tuple

import config
import db
from db import SessionLocal
from db.models import Base, Product, Variant, Competitor


def db_path(base_dir=None) -> str:
    base = base_dir or config.BASE_DIR
    return os.path.join(base, "scraper.db")


def init_db() -> None:
    """Create all tables bound to the current engine."""
    Base.metadata.create_all(bind=db.engine)


def _get_session():
    return SessionLocal()


def upsert_product(product_id: str, name: str, sku: str, price: str, dossier: str) -> None:
    with _get_session() as session:
        obj = session.get(Product, product_id)
        if obj is None:
            obj = Product(product_id=product_id)
            session.add(obj)
        obj.name = name
        obj.sku = sku
        obj.price = price
        obj.dossier = dossier
        session.commit()


def upsert_variant(product_id: str, sku: str, name: str, price: str) -> None:
    with _get_session() as session:
        obj = session.query(Variant).get((product_id, sku))
        if obj is None:
            obj = Variant(product_id=product_id, sku=sku)
            session.add(obj)
        obj.name = name
        obj.price = price
        session.commit()


def record_competitor(product_id: str, title: str, url: str, file_path: str, status: str) -> None:
    with _get_session() as session:
        comp = Competitor(product_id=product_id, title=title, url=url, file_path=file_path, status=status)
        session.add(comp)
        session.commit()


def search_products(name: str) -> List[Tuple[str, str, str, str]]:
    with _get_session() as session:
        results = (
            session.query(Product)
            .filter(Product.name.like(f"%{name}%"))
            .all()
        )
        return [(p.product_id, p.name, p.sku, p.price) for p in results]

