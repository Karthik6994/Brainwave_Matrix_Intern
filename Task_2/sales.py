from db import get_conn
from typing import List, Tuple
import datetime

def record_sale(product_id: int, quantity: int, unit_price: float) -> int:
    if quantity <= 0:
        raise ValueError("Quantity must be > 0")
    total = unit_price * quantity
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    with get_conn() as conn:
        cur = conn.cursor()
        # ensure enough stock
        cur.execute("SELECT quantity FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Product not found")
        if row[0] < quantity:
            raise ValueError("Insufficient stock")
        # insert sale
        cur.execute("""INSERT INTO sales(product_id, quantity, unit_price, total, ts)
                    VALUES(?,?,?,?,?)""", (product_id, quantity, unit_price, total, ts))
        # decrement stock
        cur.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
        conn.commit()
        return cur.lastrowid

def list_sales(date_from: str = None, date_to: str = None) -> List[Tuple]:
    query = "SELECT s.id, p.name, s.quantity, s.unit_price, s.total, s.ts FROM sales s JOIN products p ON s.product_id=p.id"
    params = []
    clauses = []
    if date_from:
        clauses.append("date(s.ts) >= date(?)")
        params.append(date_from)
    if date_to:
        clauses.append("date(s.ts) <= date(?)")
        params.append(date_to)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY s.ts DESC"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
