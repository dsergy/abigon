from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class MainCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Main Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sub Categories"
        ordering = ['main_category', 'name']

    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class PostStatus(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('review', _('Under Review')),
        ('published', _('Published')),
        ('blocked', _('Blocked')),
        ('canceled', _('Canceled')),
        ('suspended', _('Suspended')),
    )

    name = models.CharField(_('Status Name'), max_length=20, choices=STATUS_CHOICES, unique=True)
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Post Status')
        verbose_name_plural = _('Post Statuses')
        ordering = ['name']

    def __str__(self):
        return self.get_name_display()

class Ad(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Listing Title")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.ForeignKey(PostStatus, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='ads')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='ads')
    slug = models.SlugField(_('Slug'), unique=True)

    class Meta:
        verbose_name = _('Ad')
        verbose_name_plural = _('Ads')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ads:ad_detail', kwargs={'slug': self.slug})

class RealEstate(models.Model):
    LISTING_PURPOSE_CHOICES = (
        ('sale', _('Sale')),
        ('rent', _('Rent')),
    )

    PROPERTY_TYPE_CHOICES = (
        ('houses', _('Houses')),
        ('apartments', _('Apartments')),
        ('rooms', _('Rooms')),
        ('commercial', _('Commercial')),
        ('other', _('Other')),
    )

    PARKING_CHOICES = (
        ('none', _('None')),
        ('street', _('Street')),
        ('garage', _('Garage')),
        ('lot', _('Lot')),
    )

    HEATING_CHOICES = (
        ('none', _('None')),
        ('central', _('Central')),
        ('electric', _('Electric')),
        ('gas', _('Gas')),
        ('other', _('Other')),
    )

    COOLING_CHOICES = (
        ('none', _('None')),
        ('central', _('Central')),
        ('window', _('Window')),
        ('other', _('Other')),
    )

    # Basic Information
    listing_purpose = models.CharField(_('Listing Purpose'), max_length=10, choices=LISTING_PURPOSE_CHOICES)
    property_type = models.CharField(_('Property Type'), max_length=20, choices=PROPERTY_TYPE_CHOICES)
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2)
    cost = models.DecimalField(_('Cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Property Details
    bedrooms = models.PositiveIntegerField(_('Bedrooms'), null=True, blank=True)
    bathrooms = models.DecimalField(_('Bathrooms'), max_digits=3, decimal_places=1, null=True, blank=True)
    square_feet = models.DecimalField(_('Square Feet'), max_digits=10, decimal_places=2, null=True, blank=True)
    year_built = models.PositiveIntegerField(_('Year Built'), null=True, blank=True)
    
    # Amenities
    parking = models.CharField(_('Parking'), max_length=10, choices=PARKING_CHOICES, default='none')
    heating = models.CharField(_('Heating'), max_length=10, choices=HEATING_CHOICES, default='none')
    cooling = models.CharField(_('Cooling'), max_length=10, choices=COOLING_CHOICES, default='none')
    
    # Location
    zip_code = models.CharField(_('Zip Code'), max_length=5)
    city = models.CharField(_('City'), max_length=100)
    state = models.CharField(_('State'), max_length=100)
    address = models.CharField(_('Address'), max_length=200)
    hide_address = models.BooleanField(_('Hide Address'), default=False)
    
    # Rent specific
    availability_date = models.DateField(_('Availability Date'), null=True, blank=True)
    
    # Media
    images = models.ManyToManyField('RealEstateImage', verbose_name=_('Images'), blank=True)
    
    # Relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='real_estates')
    status = models.ForeignKey(PostStatus, on_delete=models.PROTECT, verbose_name=_('Status'), default=1)
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Real Estate')
        verbose_name_plural = _('Real Estates')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_property_type_display()} - {self.address}"

class RealEstateImage(models.Model):
    image = models.ImageField(_('Image'), upload_to='real_estate/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Real Estate Image')
        verbose_name_plural = _('Real Estate Images')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Image {self.id} - {self.uploaded_at}"

class SubSubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subsubcategories')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='subsubcategories')
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    icon = models.CharField(_('Icon'), max_length=50, help_text="Font Awesome icon class", blank=True)
    description = models.TextField(_('Description'), blank=True)
    cost = models.DecimalField(_('Cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Sub Sub Category')
        verbose_name_plural = _('Sub Sub Categories')
        ordering = ['main_category', 'sub_category', 'name']
        unique_together = ['main_category', 'sub_category', 'name']

    def __str__(self):
        return f"{self.main_category.name} - {self.sub_category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)