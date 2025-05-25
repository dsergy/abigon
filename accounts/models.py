from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from datetime import date

class User(AbstractUser):
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('', _('Prefer not to answer'))
    ]

    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('personal', 'Personal'),
        ('personal_pro', 'Personal Pro'),
        ('business', 'Business'),
        ('business_pro', 'Business Pro'),
    )

    USER_STATUS_CHOICES = (
        ('active', 'Active'),
        ('blocked', 'Blocked'),
        ('suspended', 'Suspended'),
    )

    name = models.CharField(_('Name'), max_length=255, blank=True)
    avatar = models.ImageField(_('Avatar'), upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(_('Date of Birth'), null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=10, choices=GENDER_CHOICES, default='', blank=True)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^\+1 \(\d{3}\) \d{3}-\d{4}$',
        message="Phone number must be entered in the format: '+1 (XXX) XXX-XXXX'"
    )
    phone = models.CharField(_('Phone'), validators=[phone_regex], max_length=17, blank=True)
    phone_verified = models.BooleanField(_('Phone Verified'), default=False)
    zip_code = models.CharField(_('ZIP Code'), max_length=10, blank=True,
                              validators=[RegexValidator(
                                  regex=r'^\d{5}(?:-\d{4})?$',
                                  message="ZIP code must be entered in the format: '12345' or '12345-6789'"
                              )])

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='personal',
        verbose_name='User Type'
    )
    
    user_status = models.CharField(
        max_length=20,
        choices=USER_STATUS_CHOICES,
        default='active',
        verbose_name='User Status'
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
