# Generated by Django 5.1.3 on 2024-12-06 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_adstatistics_revenue_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='countryrevenue',
            name='is_universal',
            field=models.BooleanField(default=False),
        ),
    ]
