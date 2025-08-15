from db import get_conn
from typing import List, Tuple
import csv
from pathlib import Path

EXPORT_DIR = Path(__file__).with_name("exports")
EXPORT_DIR.mkdir(exist_ok=True)

def low_stock(threshold: int = 5) -> List[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT id, name, sku, quantity, reorder_level
                    FROM products
                    WHERE quantity <= COALESCE(?, reorder_level) OR quantity <= reorder_level
                    ORDER BY quantity ASC""", (threshold,))
        return cur.fetchall()

def sales_summary(date_from: str = None, date_to: str = None):
    # Returns (total_orders, total_qty, total_revenue)
    query = "SELECT COUNT(*), COALESCE(SUM(quantity),0), COALESCE(SUM(total),0) FROM sales"
    params = []
    clauses = []
    if date_from:
        clauses.append("date(ts) >= date(?)")
        params.append(date_from)
    if date_to:
        clauses.append("date(ts) <= date(?)")
        params.append(date_to)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

def export_inventory_csv(filename: str = "inventory_export.csv") -> str:
    path = EXPORT_DIR / filename
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, sku, price, quantity, reorder_level FROM products ORDER BY name;")
        rows = cur.fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "SKU", "Price", "Quantity", "Reorder Level"])
        writer.writerows(rows)
    return str(path)

def export_sales_csv(filename: str = "sales_export.csv") -> str:
    path = EXPORT_DIR / filename
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT s.id, p.name, s.quantity, s.unit_price, s.total, s.ts
                    FROM sales s JOIN products p ON s.product_id=p.id
                    ORDER BY s.ts DESC;""")
        rows = cur.fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Sale ID", "Product", "Qty", "Unit Price", "Total", "Timestamp"])
        writer.writerows(rows)
    return str(path)
