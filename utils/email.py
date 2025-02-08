from flask_mail import Message
from flask import current_app
from extensions import mail

def send_email(subject, recipients, body):
    """
    Send an email using Flask-Mail.
    """
    msg = Message(subject, recipients=recipients, body=body)
    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {e}")
        return False