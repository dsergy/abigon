from django.core.exceptions import ValidationError
from .forms import ImageUploadForm

class ImageUploadMixin:
    """Mixin for handling image uploads in views."""
    
    def handle_image_upload(self, request):
        """Handle image upload and return processed images."""
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            return form.cleaned_data['images']
        return []

    def get_image_form(self):
        """Return image upload form for template."""
        return ImageUploadForm() 