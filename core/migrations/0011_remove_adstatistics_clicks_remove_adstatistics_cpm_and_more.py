# Generated by Django 5.1.3 on 2024-12-02 10:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_visitorlog_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adstatistics',
            name='clicks',
        ),
        migrations.RemoveField(
            model_name='adstatistics',
            name='cpm',
        ),
        migrations.RemoveField(
            model_name='adstatistics',
            name='ctr',
        ),
    ]
