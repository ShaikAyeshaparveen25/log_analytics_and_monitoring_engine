from backend.config.sql_config import get_connection

try:
    conn = get_connection()
    if conn.is_connected():
        print("Database connected successfully")
    conn.close()
except Exception as e:
    print("MySQL Error:", e)
