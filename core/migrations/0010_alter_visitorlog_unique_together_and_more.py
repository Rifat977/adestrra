# Generated by Django 5.1.3 on 2024-11-30 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_visitorlog'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='visitorlog',
            unique_together={('placement_link', 'ip_address', 'visited_at')},
        ),
        migrations.RemoveField(
            model_name='visitorlog',
            name='proxy',
        ),
    ]