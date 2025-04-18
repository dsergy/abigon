from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Name', max_length=100)
    slug = models.SlugField('URL', unique=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ads:category_detail', kwargs={'slug': self.slug})

class Ad(models.Model):
    STATUS_CHOICES = (
        ('draft', 'On moderation'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    )

    title = models.CharField('Title', max_length=200)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Description')
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Category'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ads',
        verbose_name='Author'
    )
    status = models.CharField(
        'Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft'
    )
    views = models.PositiveIntegerField('Views', default=0)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        verbose_name = 'Advertisement'
        verbose_name_plural = 'Advertisements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ads:ad_detail', kwargs={'slug': self.slug})