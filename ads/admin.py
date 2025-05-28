from django.contrib import admin
from .models import MainCategory, SubCategory, Ad, RealEstate, RealEstateImage, SubSubCategory

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

@admin.register(SubSubCategory)
class SubSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category', 'sub_category', 'slug', 'cost', 'created_at')
    list_filter = ('main_category', 'sub_category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('main_category', 'sub_category')
    date_hierarchy = 'created_at'

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'main_category', 'sub_category', 'status', 'created_at')
    list_filter = ('status', 'main_category', 'sub_category', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'

@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'property_type', 'listing_purpose', 'price', 'city', 'status', 'created_at')
    list_filter = ('status', 'property_type', 'listing_purpose', 'city', 'created_at')
    search_fields = ('title', 'description', 'address', 'city')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author', 'main_category', 'sub_category')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'listing_purpose', 'property_type', 'price', 'cost')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_feet', 'year_built')
        }),
        ('Amenities', {
            'fields': ('parking', 'heating', 'cooling')
        }),
        ('Location', {
            'fields': ('zip_code', 'city', 'state', 'address', 'hide_address')
        }),
        ('Rent Details', {
            'fields': ('availability_date', 'lease_term'),
            'classes': ('collapse',)
        }),
        ('Categories & Status', {
            'fields': ('main_category', 'sub_category', 'status')
        }),
        ('SEO & Stats', {
            'fields': ('slug', 'views'),
            'classes': ('collapse',)
        })
    )

@admin.register(RealEstateImage)
class RealEstateImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'uploaded_at')
    list_filter = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'
