from django.contrib import admin
from .models import MainCategory, SubCategory, Ad

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category', 'slug', 'created_at')
    list_filter = ('main_category',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'main_category', 'sub_category', 'status', 'created_at')
    list_filter = ('status', 'main_category', 'sub_category', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
