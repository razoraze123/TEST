import os
import sqlite3
import config


def db_path(base_dir=None):
    base = base_dir or config.BASE_DIR
    return os.path.join(base, "scraper.db")


def init_db(base_dir=None):
    path = db_path(base_dir)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT,
            sku TEXT,
            price TEXT,
            dossier TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS variants (
            product_id TEXT,
            sku TEXT,
            name TEXT,
            price TEXT,
            PRIMARY KEY (product_id, sku),
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            title TEXT,
            url TEXT,
            file_path TEXT,
            status TEXT,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        )
        """
    )
    conn.commit()
    conn.close()


def upsert_product(product_id, name, sku, price, dossier, base_dir=None):
    path = db_path(base_dir)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO products(product_id, name, sku, price, dossier)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(product_id) DO UPDATE SET
            name=excluded.name,
            sku=excluded.sku,
            price=excluded.price,
            dossier=excluded.dossier
        """,
        (product_id, name, sku, price, dossier),
    )
    conn.commit()
    conn.close()


def upsert_variant(product_id, sku, name, price, base_dir=None):
    path = db_path(base_dir)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO variants(product_id, sku, name, price)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(product_id, sku) DO UPDATE SET
            name=excluded.name,
            price=excluded.price
        """,
        (product_id, sku, name, price),
    )
    conn.commit()
    conn.close()


def record_competitor(product_id, title, url, file_path, status, base_dir=None):
    path = db_path(base_dir)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO competitors(product_id, title, url, file_path, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (product_id, title, url, file_path, status),
    )
    conn.commit()
    conn.close()


def search_products(name, base_dir=None):
    path = db_path(base_dir)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT product_id, name, sku, price FROM products WHERE name LIKE ?", (f"%{name}%",))
    rows = cur.fetchall()
    conn.close()
    return rows
