import os
import psycopg2
from argon2 import PasswordHasher
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# Obtain the database URL from the environment variable
# DATABASE_URL = os.environ['DATABASE_URL']

DATABASE_URL = os.environ.get('DATABASE_URL')


def get_db_connection():
    """Establishes a connection to the database."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def create_tables():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the user_history table already exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_history'
                );
            """)
            if not cur.fetchone()[0]:
                cur.execute(open("schema.sql", "r").read())
                conn.commit()
    except Exception as e:
        print(f"Failed to create tables: {e}")
    finally:
        conn.close()


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
    # Assuming image_urls is a list containing the binary data of six images
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Prepare the INSERT query
            query = """
            INSERT INTO user_searches (
                user_id, search_query, 
                image_1, image_2, image_3, 
                image_4, image_5, image_6,
                web_link_1, web_link_2, web_link_3, 
                web_link_4, web_link_5, web_link_6
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Execute the query with parameters
            cur.execute(query, (
                user_id, search_query,
                image_urls[0], image_urls[1], image_urls[2],
                image_urls[3], image_urls[4], image_urls[5],
                web_links[0], web_links[1], web_links[2],
                web_links[3], web_links[4], web_links[5]
            ))
            conn.commit()
    except Exception as e:
        print(f"Failed to add user search: {e}")
    finally:
        conn.close()


def insert_user_history(user_id, poem):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO user_history (user_id, poem) VALUES (%s, %s)",
            (user_id, poem)
        )
        conn.commit()
    conn.close()


def get_user_history(user_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM user_history WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        history = cur.fetchall()
    conn.close()
    return history
