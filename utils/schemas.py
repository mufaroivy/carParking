from marshmallow import Schema, fields, validate
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserSchema(Schema):
    """
    Schema for validating user data during signup or other user-related operations.

    Fields:
        - username (str): The user's username. Must be at least 3 characters long.
        - password (str): The user's password. Must be at least 6 characters long.
    """
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, error="Username must be at least 3 characters long.")
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters long.")
    )

class ParkingSpotSchema(Schema):
    """
    Schema for validating parking spot data.

    Fields:
        - id (int): The parking spot's ID. Must be a positive integer.
        - location (list[float]): The parking spot's location as [x, y] coordinates.
        - is_reserved (bool): The reservation status of the parking spot.
    """
    id = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Parking spot ID must be a positive integer.")
    )
    location = fields.List(
        fields.Float(),
        required=True,
        validate=validate.Length(equal=2, error="Location must be a list of two coordinates [x, y].")
    )
    is_reserved = fields.Boolean(
        required=True,
        error_messages={"required": "Reservation status is required."}
    )

class ReservationSchema(Schema):
    """
    Schema for validating reservation data.

    Fields:
        - spot_id (int): The ID of the parking spot. Must be a positive integer.
        - user_id (str): The ID of the user making the reservation. Must not be empty.
        - time (str): The reservation time in ISO 8601 format (e.g., '2023-01-23T15:30:00').
    """
    spot_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Spot ID must be a positive integer.")
    )
    user_id = fields.String(
        required=True,
        validate=validate.Length(min=1, error="User ID is required.")
    )
    time = fields.String(
        required=True,
        validate=validate.Regexp(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            error="Time must be in ISO 8601 format (e.g., '2023-01-23T15:30:00')."
        )
    )