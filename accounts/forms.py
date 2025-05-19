from django.conf import settings
 
def get_recaptcha_context():
    """Get reCAPTCHA context for templates."""
    return {
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY
    } 