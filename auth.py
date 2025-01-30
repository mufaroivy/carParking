from flask import Flask, request, jsonify
from config import Config
from schemas import UserSchema
from database import get_db
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import fields, validate

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

# Enhanced password validation to ensure security
password = fields.String(
    required=True,
    validate=validate.And(
        validate.Length(min=6),
        validate.Regexp(
            r'(?=.*\d)(?=.*[A-Z])',
            error="Password must contain at least one digit and one uppercase letter."
        )
    )
)

@app.route('/signup', methods=['POST'])
def signup():
    """Endpoint for user registration."""
    data = request.get_json()
    errors = UserSchema().validate(data)  # Validate input data using schema
    if errors:
        return jsonify(errors), 400

    username = data.get('username')
    password = data.get('password')

    try:
        db = get_db()
        cursor = db.cursor()
        # Check if the username already exists
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"msg": "Username already exists"}), 400

        # Hash the password and insert new user into the database
        hashed_password = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        db.commit()
    except Exception as e:
        return jsonify({"msg": "Database error", "error": str(e)}), 500
    finally:
        cursor.close()  # Ensure the cursor is closed
        db.close()      # Ensure the DB connection is closed

    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    """Endpoint for user login."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        db = get_db()
        cursor = db.cursor()
        # Fetch user details from the database
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):  # Assuming password is in the 3rd column
            # Generate JWT token for the authenticated user
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Invalid username or password"}), 401
    except Exception as e:
        return jsonify({"msg": "Database error", "error": str(e)}), 500
    finally:
        cursor.close()  # Ensure the cursor is closed
        db.close()      # Ensure the DB connection is closed

if __name__ == '__main__':
    app.run(debug=True)
