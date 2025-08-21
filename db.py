import config
import mysql.connector
from contextlib import contextmanager

# Define your DB configuration
db_config = {
    'host': config.MYSQL_HOST,
    'user': config.MYSQL_USER,
    'password': config.MYSQL_PASS,
    'database': config.MYSQL_DB
}

@contextmanager
def get_db():
    """Context manager to get a MySQL cursor and connection."""
    global conn, cursor
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor() # Do NOT use dictionary=True, to avoid column alphabetical order
        yield cursor, conn
    finally:
        cursor.close()
        conn.close()
