from utils.database import Database

class Reservation:
    @staticmethod
    def create_reservation(spot_id, user_id, time):
        """
        Create a new reservation in the database.
        """
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO reservations (spot_id, user_id, time) VALUES (%s, %s, %s) RETURNING id",
                (spot_id, user_id, time)
            )
            reservation_id = cursor.fetchone()[0]
            connection.commit()
            return reservation_id
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            Database.return_connection(connection)

    @staticmethod
    def get_reservations_by_user(user_id):
        """
        Fetch all reservations for a specific user.
        """
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
            return cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            Database.return_connection(connection)