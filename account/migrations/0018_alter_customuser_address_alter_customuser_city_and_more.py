# Generated by Django 5.1.3 on 2025-01-27 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_delete_customgroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='city',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='country',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='post_code',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
    ]
