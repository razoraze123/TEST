from __future__ import annotations

import os
from typing import List, Tuple
from urllib.parse import urlparse

import config
import db
from db import SessionLocal
from db.models import (
    Base,
    Product,
    Variant,
    Competitor,
    Preference,
    Selector,
)


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


# ---------------------------------------------------------------------------
# Preference helpers

def set_preference(name: str, value: str) -> None:
    """Store a string preference value keyed by *name*."""
    with _get_session() as session:
        obj = session.get(Preference, name)
        if obj is None:
            obj = Preference(name=name)
            session.add(obj)
        obj.value = value
        session.commit()


def get_preference(name: str, default: str | None = None) -> str | None:
    """Return the preference value for *name* or *default*."""
    with _get_session() as session:
        obj = session.get(Preference, name)
        return obj.value if obj else default


# ---------------------------------------------------------------------------
# Selector helpers

def load_selectors() -> dict:
    """Return saved selectors as {domain: selector} mapping."""
    with _get_session() as session:
        return {sel.domain: sel.selector for sel in session.query(Selector).all()}


def save_selector(url: str, selector: str) -> None:
    """Persist selector for given *url* (domain key)."""
    domain = urlparse(url).netloc or url
    with _get_session() as session:
        obj = session.query(Selector).filter_by(domain=domain).first()
        if obj is None:
            obj = Selector(domain=domain)
            session.add(obj)
        obj.selector = selector
        session.commit()

