from marshmallow import Schema, fields, validate

# Schema for validating user data
class UserSchema(Schema):
    """
    Schema for user data validation during signup or other user-related operations.
    """
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, error="Username must be at least 3 characters long.")
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, error="Password must be at least 6 characters long.")
    )

# Schema for parking spot data
class ParkingSpotSchema(Schema):
    """
    Schema for parking spot data validation.
    """
    id = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Parking spot ID must be a positive integer.")
    )
    location = fields.List(
        fields.Float(),
        required=True,
        validate=validate.Length(equal=2, error="Location must be a list of two coordinates [x, y].")
    )  # Assuming location is [x, y] coordinates
    is_reserved = fields.Boolean(
        required=True,
        error_messages={"required": "Reservation status is required."}
    )

# Schema for reservation data
class ReservationSchema(Schema):
    """
    Schema for reservation data validation.
    """
    spot_id = fields.Integer(
        required=True,
        validate=validate.Range(min=1, error="Spot ID must be a positive integer.")
    )
    user_id = fields.String(
        required=True,
        validate=validate.Length(min=1, error="User ID is required.")
    )  # Assuming user_id is a string (e.g., username or a unique user ID)
    time = fields.String(
        required=True,
        validate=validate.Regexp(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            error="Time must be in ISO 8601 format (e.g., '2023-01-23T15:30:00')."
        )
    )
