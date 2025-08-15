import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).with_name("inventory.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        # users
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin'
            );'''
        )
        # products
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                reorder_level INTEGER NOT NULL DEFAULT 5
            );'''
        )
        # sales
        cur.execute(
            '''CREATE TABLE IF NOT EXISTS sales(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price REAL NOT NULL CHECK(unit_price >= 0),
                total REAL NOT NULL CHECK(total >= 0),
                ts TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            );'''
        )
        conn.commit()

def seed_admin_if_missing(username="admin", password="admin123"):
    from auth import create_user, get_user_by_username
    if get_user_by_username(username) is None:
        create_user(username, password, role="admin")
