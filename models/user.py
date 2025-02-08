from utils.database import Database
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    @staticmethod
    def create_user(username, password, first_name, last_name, date_of_birth, address, email, gender):
        hashed_password = generate_password_hash(password)
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password, first_name, last_name, date_of_birth, address, email, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (username, hashed_password, first_name, last_name, date_of_birth, address, email, gender))
            user_id = cursor.fetchone()[0]
            connection.commit()
            return user_id
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            Database.return_connection(connection)

    @staticmethod
    def get_user_by_email(email):
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            return cursor.fetchone()
        except Exception as e:
            raise e
        finally:
            Database.return_connection(connection)

    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)