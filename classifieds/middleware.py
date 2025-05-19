from django.conf import settings
from django.http import HttpResponseBadRequest

class CustomHoneypotMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exclude_urls = getattr(settings, 'HONEYPOT_EXCLUDE_URLS', ['/admin/', '/admin/login/', '/admin/logout/'])

    def __call__(self, request):
        # Skip honeypot check for excluded URLs
        if any(request.path.startswith(url) for url in self.exclude_urls):
            return self.get_response(request)

        # Only check POST requests
        if request.method == 'POST':
            honeypot_field = getattr(settings, 'HONEYPOT_FIELD_NAME', 'website')
            honeypot_value = request.POST.get(honeypot_field, '')

            if honeypot_value:
                return HttpResponseBadRequest('Invalid form submission')

        return self.get_response(request) 