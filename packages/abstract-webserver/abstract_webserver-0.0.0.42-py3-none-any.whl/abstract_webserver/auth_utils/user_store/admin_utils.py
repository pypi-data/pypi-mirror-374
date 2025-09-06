from ..query_utils import insert_query, select_rows
from abstract_flask import initialize_call_log
from ..pass_utils import * 
def upsert_admin():
    initialize_call_log()
    query = """
      INSERT INTO users (username, password_hash, is_admin)
      VALUES (%s, %s, TRUE)
      ON CONFLICT (username)
      DO UPDATE
        SET password_hash = EXCLUDED.password_hash,
            is_admin      = TRUE,
            updated_at    = NOW();
    """
    try:
        plaintext = input_plain_text()
        bcrypt_hash = bcrypt_plain_text(plaintext)
        insert_query(query, "admin", bcrypt_hash)
        print("✅ 'admin' user created or updated successfully.")
        print("   You should now be able to log in as 'admin' with your new password.")
    except Exception as e:
        print("❌ Error while upserting admin user:", e)
        exit(1)
