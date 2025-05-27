from django.db import migrations

def create_post_statuses(apps, schema_editor):
    PostStatus = apps.get_model('ads', 'PostStatus')
    # Проверяем существующие статусы
    existing_statuses = set(PostStatus.objects.values_list('name', flat=True))
    # Добавляем только недостающие статусы
    required_statuses = {'draft', 'review', 'rejected', 'expired'}
    missing_statuses = required_statuses - existing_statuses
    
    for status in missing_statuses:
        PostStatus.objects.create(name=status)

def remove_post_statuses(apps, schema_editor):
    PostStatus = apps.get_model('ads', 'PostStatus')
    # Удаляем только добавленные статусы, оставляя 'published'
    PostStatus.objects.filter(name__in=['draft', 'review', 'rejected', 'expired']).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_post_statuses, remove_post_statuses),
    ] 