from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.user import User
from utils.schemas import UserSchema

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    errors = UserSchema().validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        user_id = User.create_user(**data)
        return jsonify({"msg": "User created successfully", "user_id": user_id}), 201
    except Exception as e:
        return jsonify({"msg": "Error creating user", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.get_user_by_email(data.get('email'))
    if user and User.verify_password(user[2], data.get('password')):
        access_token = create_access_token(identity=user[0])
        return jsonify({"access_token": access_token}), 200
    return jsonify({"msg": "Invalid credentials"}), 401