from ..query_utils import insert_query, select_rows
from ..pass_utils import bcrypt_plain_text
from abstract_flask import initialize_call_log
def get_user(username: str) -> dict | None:
    """
    Returns a mapping (dict) with keys: 'username', 'password_hash', 'is_admin',
    or None if no such user exists.
    """

 
    # Use RealDictCursor → fetchone() gives a dict
    query ="SELECT username, password_hash, is_admin FROM users WHERE username = %s"
    rows = select_rows(query, username)  # e.g. {'username': 'joe', 'password_hash': '…', 'is_admin': False}
    return rows


def get_user_by_username(username: str) -> dict | None:
    """
    Returns a dict with keys: id, username, password_hash, is_admin,
    or None if no such user exists.
    """
    query = """
      SELECT id,
             username,
             password_hash,
             is_admin
        FROM users
       WHERE username = %s
    """
    rows = select_rows(query, (username,))

    if not rows:
        return None

    # If select_rows returned a dict, use it; if it returned a list, grab the first item
    if isinstance(rows, dict):
        return rows
    else:
        return rows[0]
def add_or_update_user(username: str, plaintext_pwd: str, is_admin: bool = None) -> None:
    """
    Inserts a new user or updates an existing user’s password_hash and is_admin flag.
    """
    is_admin = is_admin or False
    initialize_call_log()
    # 1) Hash the plaintext password with bcrypt
    hashed = bcrypt_plain_text(plaintext_pwd,rounds=12)
    query = """
      INSERT INTO users (username, password_hash, is_admin)
      VALUES (%s, %s, %s)
      ON CONFLICT (username) DO UPDATE
        SET password_hash = EXCLUDED.password_hash,
            is_admin      = EXCLUDED.is_admin;
    """

    insert_query(query, username, hashed, is_admin)


def get_existing_users() -> list[str]:
    initialize_call_log()
    query = "SELECT username FROM users ORDER BY username ASC;"
    rows = select_rows(query)
    if not rows:
        return []
    return [r[0] for r in rows]
