import random
import string
import jwt
from datetime import datetime, timedelta
from django.conf import settings
import requests

def get_recaptcha_context():
    """Get reCAPTCHA context for templates."""
    return {
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY
    }

def verify_recaptcha(token):
    """Verify reCAPTCHA token"""
    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': token
    }
    r = requests.post(url, data=data)
    result = r.json()
    return result.get('success', False) and result.get('score', 0) >= settings.RECAPTCHA_SCORE_THRESHOLD

def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))

def generate_token(email, code):
    """Generate a JWT token for verification."""
    payload = {
        'email': email,
        'code': code,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except Exception:
        return None

def send_verification_email(email, code):
    """Send verification code to user's email."""
    subject = 'Password Reset Verification Code'
    message = f'Your verification code is: {code}\n\nIf you did not request this password reset, please contact support immediately.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    from django.core.mail import send_mail
    send_mail(subject, message, from_email, recipient_list) 