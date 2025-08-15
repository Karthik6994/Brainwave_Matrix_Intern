from db import get_conn
from typing import Optional, List, Tuple

def add_product(name: str, sku: str, price: float, quantity: int, reorder_level: int = 5) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""INSERT INTO products(name, sku, price, quantity, reorder_level)
                    VALUES(?,?,?,?,?)""", (name, sku, price, quantity, reorder_level))
        conn.commit()
        return cur.lastrowid

def update_product(product_id: int, name: str, sku: str, price: float, quantity: int, reorder_level: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""UPDATE products SET name=?, sku=?, price=?, quantity=?, reorder_level=?
                    WHERE id=?""", (name, sku, price, quantity, reorder_level, product_id))
        conn.commit()

def delete_product(product_id: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()

def get_product(product_id: int) -> Optional[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, sku, price, quantity, reorder_level FROM products WHERE id=?", (product_id,))
        return cur.fetchone()

def list_products(search: str = "") -> List[Tuple]:
    q = "%" + search + "%"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT id, name, sku, price, quantity, reorder_level
                    FROM products
                    WHERE name LIKE ? OR sku LIKE ?
                    ORDER BY name""", (q, q))
        return cur.fetchall()

def adjust_stock(product_id: int, delta: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        # Ensure not below zero
        cur.execute("SELECT quantity FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Product not found")
        new_q = row[0] + delta
        if new_q < 0:
            raise ValueError("Insufficient stock")
        cur.execute("UPDATE products SET quantity=? WHERE id=?", (new_q, product_id))
        conn.commit()
