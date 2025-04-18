from django.contrib import admin
from .models import Category, Ad

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'price', 'status', 'views', 'created_at']
    list_filter = ['status', 'created_at', 'category']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
