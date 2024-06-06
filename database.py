import os
import psycopg2
from argon2 import PasswordHasher
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Establishes a connection to the database."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def create_tables():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Create users table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
            """)
            conn.commit()

            # Create user_searches table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS user_searches (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                search_query TEXT NOT NULL,
                image_url TEXT,
                web_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """)
            conn.commit()

            # Create user_history table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS user_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                poem TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """)
            conn.commit()

            print("Tables created or updated successfully.")
    except Exception as e:
        print(f"Failed to create tables: {e}")
    finally:
        conn.close()

# 调用 create_tables 函数重新创建表
create_tables()

def register_user(email, password):
    """Registers a new user with a hashed password using Argon2."""
    ph = PasswordHasher()
    hashed_password = ph.hash(password)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the email already exists
            cur.execute("SELECT email FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return "Email already exists. Please login."

            # Proceed with inserting the new user since the email does not exist
            cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
            conn.commit()
            return "Registration successful. Redirecting..."
    except psycopg2.Error as e:
        # Returning the exception message or a custom message based on the exception
        print(f"Registration failed: {e}")
        return f"Registration failed: {str(e)}"
    finally:
        conn.close()

def validate_login(email, password):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Fetch the user's ID and hashed password from the database
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                return None

            user_id, hashed_password = user
            try:
                # Verify the password using Argon2
                ph = PasswordHasher()
                ph.verify(hashed_password, password)
                return user_id
            except:
                # Verification failed
                return None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def add_user_search(user_id, search_query, image_urls, web_links):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            INSERT INTO user_searches (
                user_id, search_query, 
                image_url, web_link, created_at
            ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            for image_url, web_link in zip(image_urls, web_links):
                print(f"Inserting: {user_id}, {search_query}, {image_url}, {web_link}")  # Debugging output
                cur.execute(query, (
                    user_id, search_query, image_url, web_link
                ))
            conn.commit()
    except Exception as e:
        print(f"Failed to add user search: {e}")  # Debugging output
    finally:
        conn.close()

def insert_user_history(user_id, poem):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            INSERT INTO user_history (user_id, poem, created_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            """
            cur.execute(query, (user_id, poem))
            conn.commit()
    except Exception as e:
        print(f"Failed to insert user history: {e}")
    finally:
        conn.close()

def get_user_history(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM user_searches WHERE user_id = %s ORDER BY created_at DESC",
                (user_id,)
            )
            history = cur.fetchall()
            if not history:
                print(f"No history found for user_id: {user_id}")
            else:
                print(f"Found history for user_id: {user_id}")
                for record in history:
                    print(record)
    except Exception as e:
        print(f"Failed to retrieve user history: {e}")
        return []
    finally:
        conn.close()
    return history

def delete_user_search(user_id, search_id):
    """Deletes a specific search record from the database."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM user_searches WHERE user_id = %s AND id = %s", (user_id, search_id))
            conn.commit()
            print(f"Deleted search record {search_id} for user {user_id}")
    except Exception as e:
        print(f"Failed to delete search record: {e}")
    finally:
        conn.close()

# New function for resetting password
def reset_password(email, old_password, new_password):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Fetch the user's ID and hashed password from the database
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            if not user:
                return "Email not found."

            user_id, hashed_password = user
            ph = PasswordHasher()
            try:
                # Verify the old password using Argon2
                ph.verify(hashed_password, old_password)
                # Hash the new password
                new_hashed_password = ph.hash(new_password)
                # Update the user's password in the database
                cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashed_password, user_id))
                conn.commit()
                return "Password reset successful."
            except:
                # Verification failed
                return "Old password is incorrect."
    except Exception as e:
        print(f"Failed to reset password: {e}")
        return "An error occurred."
    finally:
        conn.close()
