import uuid
import os
import logging
from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from django.conf import settings

logger = logging.getLogger(__name__)

class ImageProcessor:
    MAX_IMAGES = 10
    MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB
    MAX_DIMENSION = 1600
    MIN_DIMENSION = 300
    THUMBNAIL_SIZE = 300
    ALLOWED_FORMATS = ['JPEG', 'PNG']
    JPEG_QUALITY = 80

    @classmethod
    def validate_image(cls, image: UploadedFile) -> None:
        """Validate image file."""
        if not image:
            raise ValidationError('No image provided')

        # Check file size
        if image.size > cls.MAX_FILE_SIZE:
            raise ValidationError(f'File size exceeds {cls.MAX_FILE_SIZE/1024/1024}MB limit')

        # Check file type
        try:
            img = Image.open(image)
            if img.format not in cls.ALLOWED_FORMATS:
                raise ValidationError(f'Only {", ".join(cls.ALLOWED_FORMATS)} formats are allowed')
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            raise ValidationError('Invalid image file')

        # Check dimensions
        width, height = img.size
        if width < cls.MIN_DIMENSION or height < cls.MIN_DIMENSION:
            raise ValidationError(f'Image dimensions must be at least {cls.MIN_DIMENSION}x{cls.MIN_DIMENSION} pixels')
        if width > cls.MAX_DIMENSION or height > cls.MAX_DIMENSION:
            raise ValidationError(f'Image dimensions must not exceed {cls.MAX_DIMENSION}x{cls.MAX_DIMENSION} pixels')

    @classmethod
    def process_image(cls, image: UploadedFile, instance=None) -> dict:
        """Process image and create thumbnail."""
        try:
            # Validate image
            cls.validate_image(image)

            # Generate unique filename
            ext = os.path.splitext(image.name)[1].lower()
            filename = f"{uuid.uuid4()}{ext}"
            
            # Create paths
            upload_path = os.path.join(settings.MEDIA_ROOT, 'ads', 'images')
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'ads', 'thumbnails')
            
            # Ensure directories exist
            os.makedirs(upload_path, exist_ok=True)
            os.makedirs(thumbnail_path, exist_ok=True)

            # Process main image
            img = Image.open(image)
            
            # Resize if needed
            if img.width > cls.MAX_DIMENSION or img.height > cls.MAX_DIMENSION:
                img.thumbnail((cls.MAX_DIMENSION, cls.MAX_DIMENSION), Image.Resampling.LANCZOS)

            # Convert to JPEG
            if img.format != 'JPEG':
                img = img.convert('RGB')

            # Save main image
            main_path = os.path.join(upload_path, filename)
            img.save(main_path, 'JPEG', quality=cls.JPEG_QUALITY)

            # Create thumbnail
            thumb = img.copy()
            thumb.thumbnail((cls.THUMBNAIL_SIZE, cls.THUMBNAIL_SIZE), Image.Resampling.LANCZOS)
            thumb_path = os.path.join(thumbnail_path, filename)
            thumb.save(thumb_path, 'JPEG', quality=cls.JPEG_QUALITY)

            return {
                'filename': filename,
                'path': os.path.join('ads', 'images', filename),
                'thumbnail_path': os.path.join('ads', 'thumbnails', filename)
            }
        except Exception as e:
            logger.error(f"Error processing image {image.name}: {str(e)}")
            raise ValidationError(f'Error processing image: {str(e)}')

    @classmethod
    def process_multiple_images(cls, images: list, instance=None) -> list:
        """Process multiple images."""
        try:
            if len(images) > cls.MAX_IMAGES:
                raise ValidationError(f'Maximum {cls.MAX_IMAGES} images allowed')

            processed_images = []
            for image in images:
                try:
                    result = cls.process_image(image, instance)
                    processed_images.append(result)
                except ValidationError as e:
                    logger.error(f"Error processing {image.name}: {str(e)}")
                    raise ValidationError(f'Error processing {image.name}: {str(e)}')

            return processed_images
        except Exception as e:
            logger.error(f"Error in process_multiple_images: {str(e)}")
            raise ValidationError(str(e)) 