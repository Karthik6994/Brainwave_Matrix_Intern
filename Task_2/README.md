# Inventory Management System (Python + Tkinter + SQLite)

A complete, internship-ready Python mini-project with:

- SQLite storage (no setup needed)
- User authentication (hashed passwords)
- Product CRUD (add/edit/delete)
- Inventory tracking (quantity, reorder level)
- Sales recording
- Reports (low-stock alert, sales summary by date range)
- CSV export (inventory & sales)
- Clean Tkinter GUI (Treeview lists, dialogs, validation)

## Requirements
- Python 3.9+ (works on Windows/Mac/Linux)
- Standard library only (no external packages required)

## How to run
```bash
python main.py
```
The app will create `inventory.db` on first run and seed a default admin:

- **username**: `admin`
- **password**: `admin123`

> Change this in the Users tab after login.

## Project Structure
```
inventory_system_full/
├── main.py             # Entrypoint
├── db.py               # SQLite connection & schema
├── auth.py             # Authentication helpers (hashing, login, add user)
├── inventory.py        # Product CRUD
├── sales.py            # Sales handling
├── reports.py          # Reporting & CSV export
├── utils.py            # Validation helpers
├── gui.py              # Tkinter UI
├── inventory.db        # Created on first run
└── exports/            # CSV exports saved here
```

## Notes
- Passwords are hashed with SHA-256 + per-user salt.
- Prices must be >= 0; quantities must be >= 0.
- Sales automatically decrease inventory if enough stock exists.
- You can export CSVs from the Reports tab.
