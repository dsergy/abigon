from django.db import migrations

def create_real_estate_categories(apps, schema_editor):
    MainCategory = apps.get_model('ads', 'MainCategory')
    SubCategory = apps.get_model('ads', 'SubCategory')
    
    # Создаем основную категорию Real Estate
    real_estate, created = MainCategory.objects.get_or_create(
        name='Real Estate',
        slug='real-estate',
        icon='fa-home',
        description='Real estate listings including houses, apartments, and commercial properties'
    )
    
    # Создаем подкатегории
    subcategories = [
        {
            'name': 'Residential',
            'slug': 'residential',
            'icon': 'fa-house',
            'description': 'Residential properties including houses and apartments'
        },
        {
            'name': 'Commercial',
            'slug': 'commercial',
            'icon': 'fa-building',
            'description': 'Commercial properties including offices and retail spaces'
        },
        {
            'name': 'Land',
            'slug': 'land',
            'icon': 'fa-mountain',
            'description': 'Land plots and undeveloped properties'
        }
    ]
    
    for subcat_data in subcategories:
        SubCategory.objects.get_or_create(
            main_category=real_estate,
            **subcat_data
        )

def remove_real_estate_categories(apps, schema_editor):
    MainCategory = apps.get_model('ads', 'MainCategory')
    MainCategory.objects.filter(slug='real-estate').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('ads', '0004_merge_20250526_0049'),
    ]

    operations = [
        migrations.RunPython(create_real_estate_categories, remove_real_estate_categories),
    ] 