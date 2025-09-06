# /var/www/abstractendeavors/secure-files/big_man/flask_app/login_app/functions/query_utils.py
from abstract_database import connectionManager
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize connectionManager once (using your .env path if needed)
connectionManager(env_path="/home/solcatcher/.env",
                  dbType='database',
                  dbName='abstract')

def get_cur_conn(use_dict_cursor=True):
    """
    Get a database connection and a RealDictCursor.
    Returns:
        tuple: (cursor, connection)
    """
    conn = connectionManager().get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor) if use_dict_cursor else conn.cursor()
    return cur, conn

def insert_query(query: str, *args):
    """
    Execute an INSERT query with optional parameters.
    Args:
        query (str): The SQL query with %s placeholders.
        *args: Parameters to substitute into the query.
    """
    cur, conn = get_cur_conn()
    try:
        cur.execute(query, args)
        conn.commit()
    finally:
        cur.close()
        conn.close()

def select_rows(query: str, *args):
    """
    Execute a SELECT query that returns a single row or None.
    Args:
        query (str): The SQL query with %s placeholders.
        *args: Parameters to substitute into the query.
    Returns:
        A dictionary if a row is found, else None.
    """
    print("DEBUG select_rows—type(query):", type(query), " value:", query)
    cur, conn = get_cur_conn()
    try:
        if args:
            cur.execute(query, args)
        else:
            cur.execute(query)
        row = cur.fetchone()
        return row or []
    finally:
        cur.close()
        conn.close()


