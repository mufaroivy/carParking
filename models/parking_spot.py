from utils.database import Database

class ParkingSpot:
    @staticmethod
    def get_all_spots():
        """
        Fetch all parking spots from the database.
        """
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id, location, is_reserved FROM parking_spots")
            spots = cursor.fetchall()
            return [{"id": spot[0], "location": spot[1], "is_reserved": spot[2]} for spot in spots]
        except Exception as e:
            raise e
        finally:
            Database.return_connection(connection)

    @staticmethod
    def add_spot(location, is_reserved=False):
        """
        Add a new parking spot to the database.
        """
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO parking_spots (location, is_reserved) VALUES (%s, %s) RETURNING id",
                (location, is_reserved)
            )
            spot_id = cursor.fetchone()[0]
            connection.commit()
            return spot_id
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            Database.return_connection(connection)

    @staticmethod
    def delete_spot(spot_id):
        """
        Delete a parking spot by ID.
        """
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM parking_spots WHERE id = %s", (spot_id,))
            connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            connection.rollback()
            raise e
        finally:
            Database.return_connection(connection)