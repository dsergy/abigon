from django.db import migrations, models
import django.db.models.deletion
import django.utils.text

def create_initial_categories(apps, schema_editor):
    MainCategory = apps.get_model('ads', 'MainCategory')
    SubCategory = apps.get_model('ads', 'SubCategory')

    # Create main categories
    buy_rent = MainCategory.objects.create(
        name='Buy/Rent',
        slug='buy-rent',
        icon='fas fa-home',
        description='Buy or rent items and properties'
    )

    services = MainCategory.objects.create(
        name='Services',
        slug='services',
        icon='fas fa-tools',
        description='Professional services and maintenance'
    )

    events = MainCategory.objects.create(
        name='Events',
        slug='events',
        icon='fas fa-calendar-alt',
        description='Concerts, sports, and other events'
    )

    # Create subcategories for Buy/Rent
    SubCategory.objects.create(
        main_category=buy_rent,
        name='Real Estate',
        slug='real-estate',
        icon='fas fa-building',
        description='Apartments, houses, and commercial properties'
    )
    SubCategory.objects.create(
        main_category=buy_rent,
        name='Vehicles',
        slug='vehicles',
        icon='fas fa-car',
        description='Cars, motorcycles, and other vehicles'
    )
    SubCategory.objects.create(
        main_category=buy_rent,
        name='Electronics',
        slug='electronics',
        icon='fas fa-laptop',
        description='Computers, phones, and other electronics'
    )

    # Create subcategories for Services
    SubCategory.objects.create(
        main_category=services,
        name='Legal & Financial Services',
        slug='legal-financial',
        icon='fas fa-balance-scale',
        description='Legal advice and financial services'
    )
    SubCategory.objects.create(
        main_category=services,
        name='Home & Maintenance Services',
        slug='home-maintenance',
        icon='fas fa-home',
        description='Home repairs and maintenance services'
    )
    SubCategory.objects.create(
        main_category=services,
        name='Transportation & Moving',
        slug='transportation-moving',
        icon='fas fa-truck',
        description='Moving and transportation services'
    )

    # Create subcategories for Events
    SubCategory.objects.create(
        main_category=events,
        name='Concerts & Performances',
        slug='concerts-performances',
        icon='fas fa-music',
        description='Music concerts and live performances'
    )
    SubCategory.objects.create(
        main_category=events,
        name='Sports & Recreation',
        slug='sports-recreation',
        icon='fas fa-futbol',
        description='Sports events and recreational activities'
    )
    SubCategory.objects.create(
        main_category=events,
        name='Other Events',
        slug='other-events',
        icon='fas fa-calendar',
        description='Other types of events and gatherings'
    )

def remove_initial_categories(apps, schema_editor):
    MainCategory = apps.get_model('ads', 'MainCategory')
    MainCategory.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('icon', models.CharField(help_text='Font Awesome icon class', max_length=50)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Main Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('icon', models.CharField(help_text='Font Awesome icon class', max_length=50)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('main_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='ads.maincategory')),
            ],
            options={
                'verbose_name_plural': 'Sub Categories',
                'ordering': ['main_category', 'name'],
            },
        ),
        migrations.AddField(
            model_name='ad',
            name='main_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='ads.maincategory'),
        ),
        migrations.AddField(
            model_name='ad',
            name='sub_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='ads.subcategory'),
        ),
        migrations.RunPython(create_initial_categories, remove_initial_categories),
    ] 