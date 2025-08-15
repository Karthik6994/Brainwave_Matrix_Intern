from hashlib import sha256
import secrets
from db import get_conn
from typing import Optional, Tuple

def _hash_password(password: str, salt: str) -> str:
    return sha256((salt + password).encode('utf-8')).hexdigest()

def get_user_by_username(username: str) -> Optional[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash, salt, role FROM users WHERE username = ?", (username,))
        return cur.fetchone()

def create_user(username: str, password: str, role: str = "user") -> int:
    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(password, salt)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username, password_hash, salt, role) VALUES(?,?,?,?)",
                    (username, pwd_hash, salt, role))
        conn.commit()
        return cur.lastrowid

def validate_login(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    if not user:
        return False
    _id, _u, pwd_hash, salt, role = user
    return _hash_password(password, salt) == pwd_hash

def list_users():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users ORDER BY username;")
        return cur.fetchall()

def delete_user(user_id: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

def change_password(user_id: int, new_password: str) -> None:
    salt = secrets.token_hex(16)
    pwd_hash = _hash_password(new_password, salt)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE users SET password_hash=?, salt=? WHERE id=?",
                    (pwd_hash, salt, user_id))
        conn.commit()
