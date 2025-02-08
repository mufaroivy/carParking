import re
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from database import Database
from dotenv import load_dotenv
import os
from schemas import ParkingSpotSchema
from user import User
import bcrypt
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from config import Config
from routes.auth import auth_bp
from routes.parking import parking_bp
from routes.reservation import reservation_bp
from utils.database import Database
import sys

# Add the root folder to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import Database

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize JWT
jwt = JWTManager(app)

# Initialize SocketIO
socketio = SocketIO(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(parking_bp)
app.register_blueprint(reservation_bp)

# Initialize database connection pool
Database.initialize(Config.DATABASE_URL)

@app.route('/')
def index():
    return "Welcome to the Parking System API!"

if __name__ == '__main__':
    socketio.run(app, debug=Config.DEBUG)

load_dotenv(override=True)  # Force reload the .env file

print("Database URL:", os.getenv("DATABASE_URL"))  # Debugging output

# Load configuration from environment variables
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")  # Add your email
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")  # Add your email password
mail = Mail(app)

# Retrieve DSN from environment variable
dsn = os.getenv("DATABASE_URL")
if not dsn:
    raise ValueError("Error: 'DATABASE_URL' is not set in the environment.")

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Validate fields
    required_fields = ["username", "password", "first_name", "last_name", "date_of_birth", "address", "email", "gender"]
    if not all(key in data for key in required_fields):
        return jsonify({"msg": "Missing required fields"}), 400

    # Additional validations (you can adjust as needed)
    if not re.match(r"[^@]+@[^@]+\\.[^@]+", data['email']):
        return jsonify({"msg": "Invalid email address"}), 400

    if len(data['password']) < 6 or not re.search(r"\\d", data['password']) or not re.search(r"[A-Za-z]", data['password']):
        return jsonify({"msg": "Password must be at least 6 characters and contain both letters and numbers"}), 400

    # Create user
    try:
        user_id = User.create_user(
            data['username'], data['password'], data['first_name'],
            data['last_name'], data['date_of_birth'], data['address'], data['email'], data['gender']
        )
        # Send verification email (example implementation)
        msg = Message("Verify Your Email", sender=app.config["MAIL_USERNAME"], recipients=[data['email']])
        msg.body = f"Please verify your email by clicking this link: {os.getenv('APP_URL')}/verify/{user_id}"
        mail.send(msg)
        return jsonify({"msg": "User created successfully, please check your email for verification."}), 201
    except Exception as e:
        app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"msg": "Error creating user", "error": str(e)}), 500

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(hashed_password, input_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate login fields
    if not all(key in data for key in ("email", "password")):
        return jsonify({"msg": "Missing email or password"}), 400

    # Fetch user from the database
    try:
        user = User.get_user_by_email(data['email'])
        if not user or not User.verify_password(user[2], data['password']):
            return jsonify({"msg": "Invalid credentials"}), 401

        # Generate JWT token
        access_token = create_access_token(identity=user[0])  # user[0] is the user ID
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        app.logger.error(f"Error during login: {str(e)}")
        return jsonify({"msg": "Error during login process", "error": str(e)}), 500

@app.route('/parking_spots', methods=['GET'])
@jwt_required()
def get_parking_spots():
    """
    Endpoint to fetch all parking spots.
    """
    connection = Database.get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, location, is_reserved FROM parking_spots")
            spots = cursor.fetchall()
            # Convert query result into a dictionary
            result = [
                {"id": spot[0], "location": spot[1], "is_reserved": spot[2]} for spot in spots
            ]
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"Error fetching parking spots: {str(e)}")
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
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO parking_spots (location, is_reserved) VALUES (%s, %s) RETURNING id",
                (f"({location[0]},{location[1]})", is_reserved)
            )
            spot_id = cursor.fetchone()[0]
        connection.commit()
        return jsonify({"msg": "Parking spot added successfully", "id": spot_id}), 201
    except Exception as e:
        connection.rollback()
        app.logger.error(f"Error adding parking spot: {str(e)}")
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
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM parking_spots WHERE id = %s", (spot_id,))
            connection.commit()

        if cursor.rowcount > 0:
            return jsonify({"msg": f"Parking spot {spot_id} removed successfully."}), 200
        else:
            return jsonify({"msg": "Parking spot not found."}), 404
    except Exception as e:
        connection.rollback()
        app.logger.error(f"Error removing parking spot: {str(e)}")
        return jsonify({"msg": "Error removing parking spot", "error": str(e)}), 500
    finally:
        Database.return_connection(connection)

if __name__ == '__main__':
    socketio.run(app, debug=Config.DEBUG)