from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.reservation import Reservation
from utils.schemas import ReservationSchema

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/reserve', methods=['POST'])
@jwt_required()
def reserve():
    data = request.get_json()
    errors = ReservationSchema().validate(data)
    if errors:
        return jsonify(errors), 400
    try:
        user_id = get_jwt_identity()
        reservation_id = Reservation.create_reservation(data['spot_id'], user_id, data['time'])
        return jsonify({"msg": "Reservation created successfully", "reservation_id": reservation_id}), 201
    except Exception as e:
        return jsonify({"msg": "Error creating reservation", "error": str(e)}), 500

@reservation_bp.route('/my-reservations', methods=['GET'])
@jwt_required()
def my_reservations():
    try:
        user_id = get_jwt_identity()
        reservations = Reservation.get_reservations_by_user(user_id)
        return jsonify(reservations), 200
    except Exception as e:
        return jsonify({"msg": "Error fetching reservations", "error": str(e)}), 500