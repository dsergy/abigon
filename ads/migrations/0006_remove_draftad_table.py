from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('ads', '0005_add_real_estate_categories'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS ads_draftad;",
            reverse_sql=""
        ),
    ] 