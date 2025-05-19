from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def recaptcha(request):
    """Add reCAPTCHA settings to template context."""
    logger.debug(f"reCAPTCHA public key: {settings.RECAPTCHA_PUBLIC_KEY}")
    return {
        'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY
    } 