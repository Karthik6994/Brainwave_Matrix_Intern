import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db import init_db, seed_admin_if_missing
import auth, inventory, sales, reports
from utils import is_non_negative_int, is_positive_float, is_positive_int

class LoginFrame(ttk.Frame):
    def __init__(self, master, on_success):
        super().__init__(master, padding=24)
        self.on_success = on_success
        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Inventory Management System", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,18))
        ttk.Label(self, text="Username").grid(row=1, column=0, sticky="e", padx=(0,8))
        self.username = ttk.Entry(self)
        self.username.grid(row=1, column=1, sticky="ew")

        ttk.Label(self, text="Password").grid(row=2, column=0, sticky="e", padx=(0,8))
        self.password = ttk.Entry(self, show="*")
        self.password.grid(row=2, column=1, sticky="ew")

        self.login_btn = ttk.Button(self, text="Login", command=self.attempt_login)
        self.login_btn.grid(row=3, column=0, columnspan=2, pady=12, sticky="ew")

        self.username.focus_set()

    def attempt_login(self):
        u, p = self.username.get().strip(), self.password.get()
        if auth.validate_login(u, p):
            self.on_success(u)
        else:
            messagebox.showerror("Login failed", "Invalid username or password.")

class ProductsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        # Search bar
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Search").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side="left", padx=8, fill="x", expand=True)
        ttk.Button(top, text="Go", command=self.refresh).pack(side="left")
        ttk.Button(top, text="Add Product", command=self.add_dialog).pack(side="right")

        # Treeview
        cols = ("id", "name", "sku", "price", "quantity", "reorder")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        for c, w in zip(cols, (50, 220, 120, 90, 90, 110)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=8)

        btns = ttk.Frame(self)
        btns.pack(fill="x")
        ttk.Button(btns, text="Edit", command=self.edit_dialog).pack(side="left")
        ttk.Button(btns, text="Delete", command=self.delete_selected).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side="right")

        self.refresh()

    def selected_id(self):
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.item(sel[0])
        return int(item["values"][0])

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        rows = inventory.list_products(self.search_var.get().strip())
        for r in rows:
            self.tree.insert("", "end", values=r)

    def add_dialog(self):
        ProductDialog(self, title="Add Product", on_submit=self._add_submit)

    def _add_submit(self, data):
        name, sku, price, qty, reorder = data
        if not name or not sku or not is_positive_float(price) or not is_non_negative_int(qty) or not is_non_negative_int(reorder):
            messagebox.showerror("Invalid", "Please enter valid product details.")
            return
        try:
            inventory.add_product(name, sku, float(price), int(qty), int(reorder))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_dialog(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Select", "Please select a product to edit.")
            return
        p = inventory.get_product(pid)
        if not p:
            messagebox.showerror("Error", "Product not found.")
            return
        ProductDialog(self, title="Edit Product", init_values=p, on_submit=lambda d: self._edit_submit(pid, d))

    def _edit_submit(self, pid, data):
        name, sku, price, qty, reorder = data
        if not name or not sku or not is_positive_float(price) or not is_non_negative_int(qty) or not is_non_negative_int(reorder):
            messagebox.showerror("Invalid", "Please enter valid product details.")
            return
        try:
            inventory.update_product(pid, name, sku, float(price), int(qty), int(reorder))
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        pid = self.selected_id()
        if not pid:
            messagebox.showinfo("Select", "Please select a product to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete selected product? This cannot be undone."):
            try:
                inventory.delete_product(pid)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

class ProductDialog(tk.Toplevel):
    def __init__(self, master, title="Product", init_values=None, on_submit=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.on_submit = on_submit

        ttk.Label(self, text="Name").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        self.name = ttk.Entry(self, width=32)
        self.name.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(self, text="SKU").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        self.sku = ttk.Entry(self, width=32)
        self.sku.grid(row=1, column=1, padx=8, pady=6)

        ttk.Label(self, text="Price").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        self.price = ttk.Entry(self, width=32)
        self.price.grid(row=2, column=1, padx=8, pady=6)

        ttk.Label(self, text="Quantity").grid(row=3, column=0, sticky="e", padx=8, pady=6)
        self.quantity = ttk.Entry(self, width=32)
        self.quantity.grid(row=3, column=1, padx=8, pady=6)

        ttk.Label(self, text="Reorder Level").grid(row=4, column=0, sticky="e", padx=8, pady=6)
        self.reorder = ttk.Entry(self, width=32)
        self.reorder.grid(row=4, column=1, padx=8, pady=6)

        btns = ttk.Frame(self)
        btns.grid(row=5, column=0, columnspan=2, pady=8)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text="Save", command=self.submit).pack(side="right", padx=4)

        if init_values:
            # p = (id, name, sku, price, quantity, reorder_level)
            _, name, sku, price, qty, reorder = init_values
            self.name.insert(0, name)
            self.sku.insert(0, sku)
            self.price.insert(0, str(price))
            self.quantity.insert(0, str(qty))
            self.reorder.insert(0, str(reorder))

        self.name.focus_set()

    def submit(self):
        data = (
            self.name.get().strip(),
            self.sku.get().strip(),
            self.price.get().strip(),
            self.quantity.get().strip(),
            self.reorder.get().strip() or "5"
        )
        if self.on_submit:
            self.on_submit(data)
        self.destroy()

class SalesTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        # Product selection
        top = ttk.Frame(self)
        top.pack(fill="x")
        ttk.Label(top, text="Product").pack(side="left")
        self.products = inventory.list_products()
        self.product_map = {f"{p[1]} ({p[2]})": p for p in self.products}
        self.prod_var = tk.StringVar()
        self.prod_cb = ttk.Combobox(top, textvariable=self.prod_var, values=list(self.product_map.keys()), state="readonly", width=40)
        self.prod_cb.pack(side="left", padx=8)

        ttk.Label(top, text="Qty").pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        ttk.Entry(top, textvariable=self.qty_var, width=8).pack(side="left", padx=4)

        ttk.Label(top, text="Unit Price").pack(side="left")
        self.price_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=self.price_var, width=10).pack(side="left", padx=4)

        ttk.Button(top, text="Record Sale", command=self.record_sale).pack(side="left", padx=8)

        # Sales list
        cols = ("id", "product", "qty", "unit_price", "total", "ts")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c, w in zip(cols, (60, 240, 80, 100, 100, 150)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=8)

        self.refresh_sales()

    def refresh_products(self):
        self.products = inventory.list_products()
        self.product_map = {f"{p[1]} ({p[2]})": p for p in self.products}
        self.prod_cb["values"] = list(self.product_map.keys())

    def record_sale(self):
        key = self.prod_var.get()
        if key not in self.product_map:
            messagebox.showerror("Select", "Select a valid product.")
            return
        qty = self.qty_var.get().strip()
        price = self.price_var.get().strip()
        if not is_positive_int(qty) or not is_positive_float(price):
            messagebox.showerror("Invalid", "Enter valid quantity (>0) and unit price (>=0).")
            return
        pid = self.product_map[key][0]
        try:
            sale_id = sales.record_sale(pid, int(qty), float(price))
            messagebox.showinfo("Success", f"Sale recorded (ID: {sale_id}).")
            self.refresh_sales()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_sales(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for s in sales.list_sales():
            self.tree.insert("", "end", values=s)

class ReportsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)

        # Low stock
        lf = ttk.LabelFrame(self, text="Low Stock")
        lf.pack(fill="x")
        self.threshold_var = tk.StringVar(value="5")
        ttk.Label(lf, text="Threshold").pack(side="left", padx=4)
        ttk.Entry(lf, textvariable=self.threshold_var, width=6).pack(side="left")
        ttk.Button(lf, text="Check", command=self.refresh_low_stock).pack(side="left", padx=6)
        self.low_tree = ttk.Treeview(self, columns=("id","name","sku","qty","reorder"), show="headings", height=6)
        for c, w in zip(("id","name","sku","qty","reorder"), (50, 220, 120, 80, 100)):
            self.low_tree.heading(c, text=c.upper())
            self.low_tree.column(c, width=w, anchor="center")
        self.low_tree.pack(fill="x", pady=6)

        # Sales summary
        sf = ttk.LabelFrame(self, text="Sales Summary")
        sf.pack(fill="x", pady=8)
        ttk.Label(sf, text="From (YYYY-MM-DD)").pack(side="left", padx=4)
        self.from_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.from_var, width=12).pack(side="left")
        ttk.Label(sf, text="To (YYYY-MM-DD)").pack(side="left", padx=4)
        self.to_var = tk.StringVar()
        ttk.Entry(sf, textvariable=self.to_var, width=12).pack(side="left")
        ttk.Button(sf, text="Run", command=self.refresh_summary).pack(side="left", padx=6)

        self.summary_lbl = ttk.Label(self, text="Total Orders: 0 | Total Qty: 0 | Revenue: 0.00", font=("Segoe UI", 10, "bold"))
        self.summary_lbl.pack(anchor="w", pady=4)

        # Exports
        ef = ttk.LabelFrame(self, text="Exports")
        ef.pack(fill="x", pady=8)
        ttk.Button(ef, text="Export Inventory CSV", command=self.export_inventory).pack(side="left", padx=6)
        ttk.Button(ef, text="Export Sales CSV", command=self.export_sales).pack(side="left", padx=6)

        self.refresh_low_stock()

    def refresh_low_stock(self):
        thr = self.threshold_var.get().strip()
        try:
            thr = int(thr)
        except:
            messagebox.showerror("Invalid", "Threshold must be an integer.")
            return
        for r in self.low_tree.get_children():
            self.low_tree.delete(r)
        for row in reports.low_stock(thr):
            # row: (id, name, sku, quantity, reorder_level)
            self.low_tree.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

    def refresh_summary(self):
        f, t = self.from_var.get().strip() or None, self.to_var.get().strip() or None
        try:
            total_orders, total_qty, total_revenue = reports.sales_summary(f, t)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.summary_lbl.config(text=f"Total Orders: {total_orders} | Total Qty: {total_qty} | Revenue: {round(total_revenue,2)}")

    def export_inventory(self):
        path = reports.export_inventory_csv()
        messagebox.showinfo("Exported", f"Inventory CSV exported to:\n{path}")

    def export_sales(self):
        path = reports.export_sales_csv()
        messagebox.showinfo("Exported", f"Sales CSV exported to:\n{path}")

class UsersTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        cols = ("id","username","role")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c, w in zip(cols, (60, 220, 120)):
            self.tree.heading(c, text=c.upper())
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=8)

        btns = ttk.Frame(self)
        btns.pack(fill="x")
        ttk.Button(btns, text="Add User", command=self.add_user).pack(side="left")
        ttk.Button(btns, text="Change Password", command=self.change_password).pack(side="left")
        ttk.Button(btns, text="Delete User", command=self.delete_user).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self.refresh).pack(side="right")

        self.refresh()

    def selected_id(self):
        sel = self.tree.selection()
        if not sel: return None
        item = self.tree.item(sel[0])
        return int(item["values"][0])

    def refresh(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for uid, username, role in auth.list_users():
            self.tree.insert("", "end", values=(uid, username, role))

    def add_user(self):
        u = simpledialog.askstring("Add User", "Enter username:")
        if not u: return
        p = simpledialog.askstring("Add User", "Enter password:", show="*")
        if not p: return
        try:
            auth.create_user(u, p, role="admin")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_password(self):
        uid = self.selected_id()
        if not uid:
            messagebox.showinfo("Select", "Select a user.")
            return
        p = simpledialog.askstring("Change Password", "Enter new password:", show="*")
        if not p: return
        try:
            auth.change_password(uid, p)
            messagebox.showinfo("Success", "Password updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        uid = self.selected_id()
        if not uid:
            messagebox.showinfo("Select", "Select a user to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete selected user?"):
            try:
                auth.delete_user(uid)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

class MainApp(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.title(f"Inventory Management - Logged in as {username}")
        self.geometry("860x600")
        nb = ttk.Notebook(self)
        self.products_tab = ProductsTab(nb)
        nb.add(self.products_tab, text="Products")
        self.sales_tab = SalesTab(nb)
        nb.add(self.sales_tab, text="Sales")
        self.reports_tab = ReportsTab(nb)
        nb.add(self.reports_tab, text="Reports")
        self.users_tab = UsersTab(nb)
        nb.add(self.users_tab, text="Users")
        nb.pack(fill="both", expand=True)

class RootApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        init_db()
        seed_admin_if_missing()
        self.show_login()

    def show_login(self):
        for w in self.winfo_children():
            w.destroy()
        lf = LoginFrame(self, on_success=self.launch_main)
        lf.pack(fill="both", expand=True)

    def launch_main(self, username):
        for w in self.winfo_children():
            w.destroy()
        # Reuse this same window for main UI
        self.destroy()  # close login window
        app = MainApp(username)
        app.mainloop()

if __name__ == "__main__":
    RootApp().mainloop()
