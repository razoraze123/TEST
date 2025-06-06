from __future__ import annotations

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(String, primary_key=True)
    name = Column(String)
    sku = Column(String)
    price = Column(String)
    dossier = Column(String)

    variants = relationship('Variant', back_populates='product', cascade='all, delete-orphan')
    competitors = relationship('Competitor', back_populates='product', cascade='all, delete-orphan')
    images = relationship('Image', back_populates='product', cascade='all, delete-orphan')

class Variant(Base):
    __tablename__ = 'variants'
    product_id = Column(String, ForeignKey('products.product_id'), primary_key=True)
    sku = Column(String, primary_key=True)
    name = Column(String)
    price = Column(String)

    product = relationship('Product', back_populates='variants')

class Competitor(Base):
    __tablename__ = 'competitors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey('products.product_id'))
    title = Column(String)
    url = Column(String)
    file_path = Column(String)
    status = Column(String)

    product = relationship('Product', back_populates='competitors')

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey('products.product_id'))
    variant = Column(String)
    url_competitor = Column(String)
    filename = Column(String)
    wordpress_link = Column(String)

    product = relationship('Product', back_populates='images')

class ScheduledTask(Base):
    __tablename__ = 'scheduled_tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    scheduled_for = Column(DateTime)
    status = Column(String)

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created = Column(DateTime)
    level = Column(String)
    message = Column(Text)


class Preference(Base):
    """Simple key/value store for user preferences."""

    __tablename__ = 'preferences'

    name = Column(String, primary_key=True)
    value = Column(String)


class Selector(Base):
    """Saved CSS selectors keyed by domain."""

    __tablename__ = 'selectors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String, unique=True)
    selector = Column(String)

class Workflow(Base):
    __tablename__ = 'workflows'
    id = Column(Integer, primary_key=True, autoincrement=True)
    params = Column(Text)
    output_dir = Column(String)
