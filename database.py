import os
import psycopg2
from argon2 import PasswordHasher
from dotenv import load_dotenv
import boto3
import requests
from io import BytesIO
from datetime import datetime, timedelta

load_dotenv()

# Obtain the database URL from the environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

# S3 Configurations
S3_BUCKET_NAME = os.getenv('BUCKETEER_BUCKET_NAME')
S3_ACCESS_KEY = os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY')


def get_db_connection():
    """Establishes a connection to the database."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')


def create_tables():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
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
            result = cur.fetchone()
            if result is None:
                # No user found with the provided email
                return None

            user_id, stored_password = result
            # Initialize the password hasher
            ph = PasswordHasher()
            try:
                # Verify the provided password against the stored hash
                ph.verify(stored_password, password)
                # If verification passed, return the user's ID
                return user_id
            except:
                # Verification failed
                return None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()


s3 = boto3.client('s3',
                  aws_access_key_id=S3_ACCESS_KEY,
                  aws_secret_access_key=S3_SECRET_KEY)


def upload_image_to_s3(image_url, file_name):
    """Downloads an image from a URL and uploads it to S3, returning the URL."""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            file_content = BytesIO(response.content)
            s3.upload_fileobj(
                file_content,
                S3_BUCKET_NAME,
                file_name,
                ExtraArgs={'ContentType': response.headers['Content-Type']}
            )
            return file_name
        else:
            print(f"Failed to download image from URL: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to upload image to S3: {e}")
        return None


def save_link(search_id, link_url):
    """保存链接到数据库"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            INSERT INTO weblinks (user_searches_id, link)
            VALUES (%s, %s)
            """
            cur.execute(query, (search_id, link_url))
            conn.commit()
    except Exception as e:
        print(f"Failed to save link: {e}")
    finally:
        conn.close()


def save_image(search_id, image_url):
    """保存图像到数据库和S3"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            image_url = upload_image_to_s3(image_url, os.path.basename(image_url))
            query = """
            INSERT INTO images (
                user_searches_id, image_name
            ) VALUES (%s, %s)
            """
            cur.execute(query, (search_id, image_url))
            conn.commit()
    except Exception as e:
        print(f"Failed to save image: {e}")
    finally:
        conn.close()



def add_user_search(user_id, search_query):
    """Adds a user search to the database and returns the search ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Check if the search query already exists for the user
            check_query = """
            SELECT id FROM user_searches
            WHERE user_id = %s AND search_query = %s
            """
            cur.execute(check_query, (user_id, search_query))
            existing_search = cur.fetchone()

            if (existing_search):
                # If the search query exists, return the existing search ID
                return existing_search[0]
            else:
                # If the search query does not exist, insert it and return the new search ID
                insert_query = """
                INSERT INTO user_searches (
                    user_id, search_query
                ) VALUES (%s, %s)
                RETURNING id
                """
                cur.execute(insert_query, (user_id, search_query))
                search_id = cur.fetchone()[0]
                conn.commit()
                return search_id
    except Exception as e:
        print(f"Failed to add user search: {e}")
        return None
    finally:
        conn.close()


def get_user_searches(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT us.id, us.search_query
            FROM user_searches us
            LEFT JOIN images i ON us.id = i.user_searches_id
            LEFT JOIN weblinks w ON us.id = w.user_searches_id
            WHERE us.user_id = %s
            GROUP BY us.id
            HAVING COUNT(i.id) > 0 OR COUNT(w.id) > 0
            ORDER BY us.timestamp DESC
            """
            cur.execute(query, (user_id,))
            searches = cur.fetchall()
            return searches
    except Exception as e:
        print(f"Failed to retrieve user searches: {e}")
        return None
    finally:
        conn.close()


def generate_presigned_url(bucket_name, file_name, expiration=3600):
    """Generate a pre-signed URL for an S3 object."""
    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name,
                                                     'Key': file_name},
                                             ExpiresIn=expiration)
    except Exception as e:
        print(f"Failed to generate pre-signed URL: {e}")
        return None
    return response


def get_search_history_images(search_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT id, image_name
            FROM images
            WHERE user_searches_id = %s
            """
            cur.execute(query, (search_id,))
            images = cur.fetchall()

            # Generate presigned URLs for the images
            result = []
            for image in images:
                image_id, image_name = image
                result.append((image_id, generate_presigned_url(S3_BUCKET_NAME, image_name)))

            return result
    except Exception as e:
        print(f"Failed to retrieve search history images: {e}")
        return None
    finally:
        conn.close()


def get_search_history_weblinks(search_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            query = """
            SELECT id, link
            FROM weblinks
            WHERE user_searches_id = %s
            """
            cur.execute(query, (search_id,))
            weblinks = cur.fetchall()

            result = [(link[0], link[1]) for link in weblinks]

            return result
    except Exception as e:
        print(f"Failed to retrieve search history links: {e}")
        return None
    finally:
        conn.close()


def clear_user_search(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Retrieve all image keys associated with the user's searches
            cur.execute("""
                SELECT image_name
                FROM images
                WHERE user_searches_id IN (
                    SELECT id FROM user_searches WHERE user_id = %s
                )
            """, (user_id,))
            images = cur.fetchall()

            # Delete images from S3
            for image in images:
                image_key = image[0]
                if (image_key):
                    try:
                        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=image_key)
                    except Exception as e:
                        print(f"Failed to delete image {image_key} from S3: {e}")

            # Clear the user's search history from the user_searches table
            cur.execute("DELETE FROM user_searches WHERE user_id = %s", (user_id,))
            conn.commit()
    except Exception as e:
        print(f"Failed to clear search history: {e}")
    finally:
        conn.close()


# 删除特定的用户搜索记录
def delete_user_search(search_id):
    """删除特定的用户搜索记录，包括其关联的图片和链接"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 删除与指定搜索记录关联的图片
            cur.execute("""
                DELETE FROM images 
                WHERE user_searches_id = %s
            """, (search_id,))

            # 删除与指定搜索记录关联的链接
            cur.execute("""
                DELETE FROM weblinks 
                WHERE user_searches_id = %s
            """, (search_id,))

            # 删除用户的搜索记录
            cur.execute("""
                DELETE FROM user_searches 
                WHERE id = %s
            """, (search_id,))

            conn.commit()
    except Exception as e:
        print(f"Failed to delete user search: {e}")
    finally:
        conn.close()


def store_verification_code(email, code):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            expires_at = datetime.now() + timedelta(minutes=10)  # Code expires in 10 minutes
            cur.execute("""
                INSERT INTO verification_codes (email, verification_code, expires_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                verification_code = EXCLUDED.verification_code,
                expires_at = EXCLUDED.expires_at
            """, (email, code, expires_at))
            conn.commit()
    except Exception as e:
        print(f"Failed to store verification code: {e}")
    finally:
        conn.close()


def verify_code(email, code):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT verification_code, expires_at
                FROM verification_codes
                WHERE email = %s
            """, (email,))
            result = cur.fetchone()
            if (result):
                stored_code, expires_at = result
                if stored_code == code and expires_at > datetime.now():
                    return True
            return False
    except Exception as e:
        print(f"Failed to verify code: {e}")
        return False
    finally:
        conn.close()


def reset_user_password(email, new_password):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            hashed_password = PasswordHasher().hash(new_password)
            cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
            conn.commit()
    except Exception as e:
        print(f"Failed to reset password: {e}")
    finally:
        conn.close()


def send_verification_email(recipient_email, verification_code):
    url = f"{os.getenv('TRUSTIFI_URL')}/api/i/v1/email"
    payload = {
        "recipients": [{"email": recipient_email}],
        "title": "Your Verification Code",
        "html": f"<p>Your verification code is: <strong>{verification_code}</strong></p>"
    }
    headers = {
        'x-trustifi-key': os.getenv('TRUSTIFI_KEY'),
        'x-trustifi-secret': os.getenv('TRUSTIFI_SECRET'),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)
    if (response.status_code == 200):
        print("Verification email sent successfully.")
    else:
        print(f"Failed to send verification email: {response.text}")


# 新增文件夹管理功能

def add_folder(user_id, folder_name):
    """为用户添加一个文件夹"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO folders (user_id, folder_name)
                VALUES (%s, %s)
                RETURNING id;
            """, (user_id, folder_name))
            folder_id = cur.fetchone()[0]
            conn.commit()
            return folder_id
    except Exception as e:
        print(f"Failed to add folder: {e}")
        return None
    finally:
        conn.close()


def delete_folder(user_id, folder_name):
    """删除用户的文件夹及其内容"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 删除文件夹内的图片和链接
            cur.execute("""
                DELETE FROM images 
                WHERE folder_id = (
                    SELECT id FROM folders WHERE user_id = %s AND folder_name = %s
                );
            """, (user_id, folder_name))

            cur.execute("""
                DELETE FROM weblinks 
                WHERE folder_id = (
                    SELECT id FROM folders WHERE user_id = %s AND folder_name = %s
                );
            """, (user_id, folder_name))

            # 删除文件夹
            cur.execute("""
                DELETE FROM folders 
                WHERE user_id = %s AND folder_name = %s
                RETURNING id;
            """, (user_id, folder_name))
            folder_id = cur.fetchone()[0]
            conn.commit()
            return folder_id
    except Exception as e:
        print(f"Failed to delete folder: {e}")
        return None
    finally:
        conn.close()


def get_folder_images(folder_id):
    """获取文件夹内的所有图片的URL"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, image_name 
                FROM images 
                WHERE folder_id = %s
            """, (folder_id,))
            images = cur.fetchall()

            # 生成预签名URL
            result = []
            for image in images:
                image_id, image_name = image
                result.append((image_id, generate_presigned_url(S3_BUCKET_NAME, image_name)))

            return result
    except Exception as e:
        print(f"Failed to get folder images: {e}")
        return None
    finally:
        conn.close()


def get_folder_weblinks(folder_id):
    """获取文件夹内的所有链接"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, link 
                FROM weblinks 
                WHERE folder_id = %s
            """, (folder_id,))
            links = cur.fetchall()

            result = [(link[0], link[1]) for link in links]
            return result
    except Exception as e:
        print(f"Failed to get folder links: {e}")
        return None
    finally:
        conn.close()


def delete_folder_image(image_id):
    """删除文件夹内的指定图像"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 从数据库中删除指定图像
            cur.execute("DELETE FROM images WHERE id = %s", (image_id,))
            conn.commit()
    except Exception as e:
        print(f"Failed to delete folder image: {e}")
    finally:
        conn.close()

def delete_folder_link(link_id):
    """删除文件夹内的指定链接"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 从数据库中删除指定链接
            cur.execute("DELETE FROM weblinks WHERE id = %s", (link_id,))
            conn.commit()
    except Exception as e:
        print(f"Failed to delete folder link: {e}")
    finally:
        conn.close()



# 删除历史记录内指定的图像
def delete_image(image_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM images WHERE id = %s", (image_id,))
            conn.commit()
    except Exception as e:
        print(f"Failed to delete image: {e}")
    finally:
        conn.close()


# 删除历史记录内指定的链接
def delete_link(link_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM weblinks WHERE id = %s", (link_id,))
            conn.commit()
    except Exception as e:
        print(f"Failed to delete link: {e}")
    finally:
        conn.close()
