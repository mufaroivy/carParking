from flask import Flask, request, jsonify
from config import Config
from database import Database
from flask_socketio import SocketIO, emit
from flask_jwt_extended import jwt_required, get_jwt_identity

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app)

@app.route('/check_availability', methods=['GET'])
@jwt_required()
def check_availability():
    """
    Endpoint to check the availability of parking spots.
    Requires a valid JWT for authentication.
    """
    connection = Database.get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute('SELECT id, location, is_reserved FROM parking_spots')
        spots = cursor.fetchall()

        # Format the response
        response = [
            {"id": spot[0], "location": spot[1], "is_reserved": spot[2]}
            for spot in spots
        ]
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"msg": "Error fetching availability", "error": str(e)}), 500
    finally:
        Database.return_connection(connection)

@app.route('/reserve', methods=['POST'])
@jwt_required()
def reserve():
    """
    Endpoint to reserve a parking spot.
    Requires:
        - spot_id: ID of the parking spot to reserve.
        - time: Reservation time.
    """
    data = request.get_json()
    spot_id = data.get('spot_id')
    time = data.get('time')

    if not spot_id or not time:
        return jsonify({"msg": "Invalid data. 'spot_id' and 'time' are required."}), 400

    connection = Database.get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO reservations (spot_id, user_id, time) VALUES (%s, %s, %s)',
            (spot_id, get_jwt_identity(), time)
        )
        connection.commit()
        return jsonify({"msg": "Spot reserved successfully"}), 201
    except Exception as e:
        return jsonify({"msg": "Error reserving spot", "error": str(e)}), 500
    finally:
        Database.return_connection(connection)

@socketio.on('connect')
def test_connect():
    """
    Handle client socket connection.
    Broadcast a welcome message to the connected client.
    """
    emit('my response', {'data': 'Connected'})

@socketio.on('update_spaces')
def update_spaces(data):
    """
    Handle updates for parking space availability and broadcast to all connected clients.
    """
    emit('spaces_update', data, broadcast=True)

@app.route('/')
def index():
    """
    Root endpoint of the API.
    Returns a welcome message.
    """
    return jsonify({"msg": "Welcome to the Parking Manager API"})

if __name__ == '__main__':
    # Initialize the database pool before starting the app
    Database.initialize(Config.DATABASE_URL, minconn=2, maxconn=10)

    # Run the Flask app with SocketIO
    socketio.run(app, debug=True)
