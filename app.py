from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from database import Database
from dotenv import load_dotenv
import os
from schemas import ParkingSpotSchema

# Load environment variables
load_dotenv()

# Debugging: Print the value of the DATABASE_URL to ensure it's loaded correctly
dsn = os.getenv("DATABASE_URL")
print(f"Database DSN: {dsn}")


# Initialize the Flask app
app = Flask(__name__)

# Load secret key from environment variable
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")

# Initialize JWT Manager
jwt = JWTManager(app)

# Retrieve DSN from environment variable
dsn = os.getenv("DATABASE_URL")
if not dsn:
    raise ValueError("Error: 'DATABASE_URL' is not set in the environment.")

# Initialize the database
Database.initialize(dsn)

@app.route('/parking_spots', methods=['GET'])
@jwt_required()
def get_parking_spots():
    """
    Endpoint to fetch all parking spots.
    """
    connection = Database.get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, location, is_reserved FROM parking_spots")
        spots = cursor.fetchall()
        # Convert query result into a dictionary
        result = [
            {"id": spot[0], "location": spot[1], "is_reserved": spot[2]} for spot in spots
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"msg": "Error fetching parking spots", "error": str(e)}), 500
    finally:
        Database.return_connection(connection)

@app.route('/parking_spots', methods=['POST'])
@jwt_required()
def add_parking_spot():
    """
    Endpoint to add a new parking spot.
    """
    data = request.get_json()
    parking_spot_schema = ParkingSpotSchema()
    errors = parking_spot_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    location = data.get('location')
    is_reserved = data.get('is_reserved', False)

    connection = Database.get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO parking_spots (location, is_reserved) VALUES (%s, %s) RETURNING id",
            (f"({location[0]},{location[1]})", is_reserved)
        )
        spot_id = cursor.fetchone()[0]
        connection.commit()
        return jsonify({"msg": "Parking spot added successfully", "id": spot_id}), 201
    except Exception as e:
        return jsonify({"msg": "Error adding parking spot", "error": str(e)}), 500
    finally:
        Database.return_connection(connection)

@app.route('/parking_spots/<int:spot_id>', methods=['DELETE'])
@jwt_required()
def delete_parking_spot(spot_id):
    """
    Endpoint to remove a parking spot by ID.
    """
    connection = Database.get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM parking_spots WHERE id = %s", (spot_id,))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({"msg": f"Parking spot {spot_id} removed successfully."}), 200
        else:
            return jsonify({"msg": "Parking spot not found."}), 404
    except Exception as e:
        return jsonify({"msg": "Error removing parking spot", "error": str(e)}), 500
    finally:
        Database.return_connection(connection)

if __name__ == '__main__':
    app.run(debug=True)
