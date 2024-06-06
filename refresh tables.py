import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Establishes a connection to the database."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def drop_tables():
    """Drops existing tables if they exist."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS user_searches;")
            cur.execute("DROP TABLE IF EXISTS user_history;")
            cur.execute("DROP TABLE IF EXISTS users;")
            conn.commit()
    except Exception as e:
        print(f"Failed to drop tables: {e}")
    finally:
        conn.close()

def create_tables():
    """Creates tables using schema.sql."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(open("schema.sql", "r").read())
            conn.commit()
    except Exception as e:
        print(f"Failed to create tables: {e}")
    finally:
        conn.close()

# Drop existing tables
drop_tables()

# Create new tables
create_tables()

print("Tables created successfully.")
