# Generated by Django 5.1.3 on 2024-12-13 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_alter_adstatistics_revenue'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='placementlink',
            options={'verbose_name_plural': 'User Smart Link'},
        ),
        migrations.AlterModelOptions(
            name='publisherplacement',
            options={'verbose_name_plural': 'Publisher Smart Link'},
        ),
    ]
